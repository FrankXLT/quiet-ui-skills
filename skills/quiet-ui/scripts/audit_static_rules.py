# SPDX-License-Identifier: Apache-2.0
"""Static CSS/HTML/JS, mount-prefix, exclusion, and data-honesty rules for Quiet UI."""

from __future__ import annotations

import fnmatch
import re
import urllib.parse
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
VIEWPORTS: tuple[tuple[int, int], ...] = ((390, 844), (820, 1080), (1440, 900))
WRAPPER_CLASS_HINTS = {"va-table-wrap", "qe-table-wrap", "table-wrap", "table-scroll", "overflow-x-auto"}
EARLY_LAYER_NAMES = frozenset(
    {"reset", "base", "tokens", "shell", "archetypes", "views", "components", "cards", "chrome", "workspace"}
)

_IMPORTANT_RE = re.compile(r"!\s*important\b", re.IGNORECASE)
_FONT_PX_RE = re.compile(r"(?<![A-Za-z0-9_-])font-size\s*:\s*([0-9]*\.?[0-9]+)\s*px\b", re.IGNORECASE)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_NARROW_AT_RE = re.compile(r"@media[^{]*?(?:max-width\s*:\s*\d+px|pointer\s*:\s*coarse)[^{]*\{", re.IGNORECASE)
OVERFLOW_RULE_RE = re.compile(r"([^{};]+)\{[^{}]*overflow(?:-x)?\s*:\s*(?:auto|scroll)\b[^{}]*\}", re.IGNORECASE | re.DOTALL)
_LAYER_ORDER_RE = re.compile(r"@layer\s+([A-Za-z0-9_.,\s-]+)\s*;", re.IGNORECASE)
_LAYER_BLOCK_RE = re.compile(r"@layer\s+([A-Za-z0-9_.-]+)\s*\{", re.IGNORECASE)
_HIDDEN_SEL_RE = re.compile(
    r"(?<![A-Za-z0-9_-])\.hidden(?![A-Za-z0-9_-])|(?:^|[\s,>+~])\[hidden\](?::not\([^)]*\))?(?=$|[\s,:{>+~])",
    re.IGNORECASE,
)
_DISPLAY_NONE_RE = re.compile(r"(?:^|;)\s*display\s*:\s*none\b", re.IGNORECASE)

SELF_BADGE_RE = re.compile(
    r"(?<![A-Za-z0-9_/-])\b(?:(?:v\d+(?:\.\d+)*|\d+\.\d+(?:\.\d+)*)\s*[·•|-]?\s*Quiet(?:[\s-]+UI)?|Quiet(?:[\s-]+UI)(?:\s+v\d|\s+Pillar|\s+Skills)?|Quiet-Evidence\s+L[1-3]|Pillar\s+[123]\s+M[1-7])\b(?![-_][A-Za-z0-9]|/)",
    re.IGNORECASE,
)
BRAIN_TEXT_RE = re.compile(r"(?:\bbrain:[0-9a-z_-]{6,}\b|\.gemini/antigravity/brain/)", re.IGNORECASE)
_BRAIN_JS_RE = re.compile(
    r"(?:`[^`]*brain:\$\{[^`]+`|['\"]brain:['\"]\s*\+|\bbrain:[0-9a-z_-]{6,}\b|\.gemini/antigravity/brain/)",
    re.IGNORECASE,
)
_NAMED_MOCK_ARR_RE = re.compile(
    r"(?:const|let|var)?\s*\b(?:(?:MOCK|FAKE|DUMMY|STUB)_[A-Z0-9_]+|(?:mock|fake|dummy|demo|stub)(?:Rows|Runs|Series|Data|Items|Metrics|Logs|Events|Cards))\s*=\s*\[\s*\{",
    re.IGNORECASE,
)
_DEMO_GUARD_RE = re.compile(r"\b(?:isDemo|demoMode|useDemo)\b|\bdemo\s*[!=]==?|(?:get|has)\(\s*['\"]demo['\"]", re.IGNORECASE)
_DEMO_TERNARY_RE = re.compile(r"\b(?:isDemo|demoMode|useDemo)\b\s*\?\s*\[\s*\{[\s\S]{1,400}?\}\s*,\s*\{", re.IGNORECASE)
_MULTI_OBJ_ARR_RE = re.compile(r"(?:=|\breturn)\s*\[\s*\{[\s\S]{1,400}?\}\s*,\s*\{", re.IGNORECASE)
DIURNAL_RE = re.compile(r"\bdiurnal\b", re.IGNORECASE)
_DENSITY_WORDS = frozenset({"compact", "cozy", "comfortable", "relaxed", "dense", "spacious"})
_FOOTER_BANNED_RE = re.compile(r"^(?:lock|unlock|<?\s*classic)$", re.IGNORECASE)
_CSS_FOOTER_COL_RE = re.compile(r"\.va-rail-footer\s*\{[^}]*flex-direction\s*:\s*column\b", re.IGNORECASE | re.DOTALL)


def parse_mount_prefixes(raw_items: list[str] | None) -> dict[str, Path]:
    """Parse repeatable PREFIX=DIR CLI flags into normalized mount prefix mappings."""
    out: dict[str, Path] = {}
    for item in raw_items or ():
        if "=" not in item:
            continue
        pfx, raw_dir = item.split("=", 1)
        norm = "/" + pfx.strip().strip("/") if pfx.strip() != "/" else "/"
        out[norm] = Path(raw_dir).expanduser().resolve()
    return out


def compute_mount_scopes(target: str, mount_prefixes: dict[str, Path] | None) -> dict[str, Path]:
    """Compute subdirectory/subpath lint boundaries when target sits strictly inside a mount."""
    scopes: dict[str, Path] = {}
    if not mount_prefixes:
        return scopes
    if target.startswith(("http://", "https://")):
        url_path = urllib.parse.unquote(urllib.parse.urlsplit(target).path or "/")
        for pfx, mdir in mount_prefixes.items():
            mdir_res = mdir.resolve()
            pfx_base = "" if pfx == "/" else pfx.rstrip("/")
            if not url_path.startswith(pfx_base + "/"):
                continue
            rel = url_path[len(pfx_base):].strip("/")
            if not rel:
                continue
            cand = (mdir_res / rel).resolve()
            if not cand.is_relative_to(mdir_res):
                continue
            scope_dir = cand if cand.is_dir() else cand.parent
            while not scope_dir.is_dir() and scope_dir != mdir_res and scope_dir.is_relative_to(mdir_res):
                scope_dir = scope_dir.parent
            if scope_dir.is_dir() and scope_dir != mdir_res and scope_dir.is_relative_to(mdir_res):
                scopes[pfx] = scope_dir
        return scopes
    tpath = Path(target).resolve()
    tdir = tpath if tpath.is_dir() else tpath.parent
    for pfx, mdir in mount_prefixes.items():
        mdir_res = mdir.resolve()
        if tdir != mdir_res and tdir.is_relative_to(mdir_res):
            scopes[pfx] = tdir
    return scopes


def matches_exclude(candidate: str | Path, patterns: list[str] | tuple[str, ...] | None, *, root: Path | None = None) -> bool:
    """Return True if a file path or asset URL matches any --exclude filename, suffix, or glob."""
    if not patterns:
        return False
    raw = str(candidate).split("?", 1)[0].split("#", 1)[0].replace("\\", "/").strip()
    cands: list[str] = [raw]
    if isinstance(candidate, Path):
        cands.extend([candidate.name, candidate.as_posix()])
        if root is not None:
            try:
                cands.append(candidate.resolve().relative_to(root.resolve()).as_posix())
            except ValueError:
                pass
    else:
        cands.extend([raw.lstrip("/"), Path(raw).name])
    for pat in patterns:
        np = pat.strip().replace("\\", "/")
        if not np:
            continue
        np_trim = np.lstrip("/")
        for s in cands:
            if fnmatch.fnmatch(s, np) or ("/" not in np and fnmatch.fnmatch(Path(s).name, np)):
                return True
            if s == np_trim or s.endswith("/" + np_trim):
                return True
            if "/" in np and not np.startswith(("/", "*")) and fnmatch.fnmatch(s, "*/" + np_trim):
                return True
            if np.endswith("/") and (s.startswith(np) or s.startswith(np_trim) or ("/" + np_trim) in s):
                return True
    return False


def resolve_asset_detail(ref: str, *, base_dir: Path | None = None, web_root: Path | None = None, mount_prefixes: dict[str, Path] | None = None) -> tuple[Path | None, str | None, bool]:
    """Resolve an HTML asset reference; return (path, matched_mount_prefix, missing_in_mount)."""
    if not ref or ref.startswith(("http://", "https://", "//", "data:", "blob:")):
        return None, None, False
    raw = urllib.parse.unquote(ref.split("?", 1)[0].split("#", 1)[0]).strip()
    if not raw:
        return None, None, False
    if raw.startswith("/"):
        for pfx, mdir in sorted((mount_prefixes or {}).items(), key=lambda kv: len(kv[0]), reverse=True):
            if raw == pfx or raw.startswith(pfx.rstrip("/") + "/"):
                mdir_res = mdir.resolve()
                tail = raw[len(pfx):].lstrip("/")
                cand = (mdir_res / tail).resolve() if tail else mdir_res
                if not cand.is_relative_to(mdir_res):
                    return None, None, False
                if cand.is_file():
                    return cand, pfx, False
                return cand, pfx, True
        if web_root is not None:
            wr = web_root.resolve()
            cand = (wr / raw.lstrip("/")).resolve()
            if cand.is_relative_to(wr) and cand.is_file():
                return cand, None, False
    for root in (base_dir, web_root):
        if root is None:
            continue
        rdir = root.resolve()
        cand = (rdir / raw.lstrip("/")).resolve() if raw.startswith("/") else (rdir / raw).resolve()
        if cand.is_relative_to(rdir) and cand.is_file():
            return cand, None, False
    return None, None, False


def resolve_asset_path(ref: str, base_dir: Path | None = None, web_root: Path | None = None, mount_prefixes: dict[str, Path] | None = None) -> Path | None:
    """Resolve an HTML stylesheet or script src reference cleanly inside mounted roots."""
    cand, _pfx, missing = resolve_asset_detail(ref, base_dir=base_dir, web_root=web_root, mount_prefixes=mount_prefixes)
    return None if missing else cand


def is_asset_in_scope(asset_path: Path, matched_pfx: str | None, mount_scopes: dict[str, Path] | None, *, audit_mounted_external: bool = False) -> bool:
    """Return True if a mounted asset resides inside the target's scoped subpath."""
    if audit_mounted_external or not matched_pfx or not mount_scopes:
        return True
    scope_dir = mount_scopes.get(matched_pfx)
    return True if scope_dir is None else asset_path.resolve().is_relative_to(scope_dir.resolve())


def find_closing_delim(text: str, start: int, open_ch: str, close_ch: str, *, line_comments: bool = True, backtick_quotes: bool = True) -> int:
    """Scan forward past balanced delimiters while ignoring JS/CSS strings and comments."""
    depth, i, n, quote = 1, start + 1, len(text), ""
    while i < n and depth > 0:
        ch = text[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in ("'", '"') or (backtick_quotes and ch == "`"):
            quote = ch
        elif line_comments and ch == "/" and i + 1 < n and text[i + 1] == "/":
            nl = text.find("\n", i + 2)
            i = n if nl < 0 else nl + 1
            continue
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
        i += 1
    return i if depth == 0 else -1


def extract_layer_order(css_text: str) -> list[str]:
    """Return the first multi-name @layer order list declared in CSS."""
    for m in _LAYER_ORDER_RE.finditer(css_text):
        names = [s.strip().lower() for s in m.group(1).split(",") if s.strip()]
        if len(names) >= 2:
            return names
    return []


def check_hidden_layer_css(clean_css: str, source: str, errs: list[str], *, layer_order: list[str] | None = None) -> None:
    """Flag .hidden or bare [hidden] display:none declared inside a non-final @layer."""
    if "@layer" not in clean_css.lower():
        return
    order = extract_layer_order(clean_css) or list(layer_order or ())
    non_final = set(order[:-1]) if len(order) >= 2 else set()
    flagged: set[str] = set()
    for m in _LAYER_BLOCK_RE.finditer(clean_css):
        lname = m.group(1).strip().lower()
        is_early = (lname in EARLY_LAYER_NAMES) or (lname in non_final)
        if not is_early:
            continue
        blk_end = find_closing_delim(clean_css, m.end() - 1, "{", "}", line_comments=False, backtick_quotes=False)
        block = clean_css[m.end() : (blk_end - 1 if blk_end > 0 else len(clean_css))]
        for rm in re.finditer(r"([^{};]+)\{([^{}]*)\}", block):
            sel, body = rm.group(1).strip(), rm.group(2)
            if _DISPLAY_NONE_RE.search(body) and _HIDDEN_SEL_RE.search(sel) and lname not in flagged:
                flagged.add(lname)
                errs.append(
                    f"[HIDDEN_LAYER] {source}: .hidden/[hidden] display:none placed in non-final '@layer {lname}' instead of terminal '@layer utilities'"
                )


def audit_css_text(css_text: str, source: str, errs: list[str], *, layer_order: list[str] | None = None) -> None:
    """Check CSS text for !important, <11px font-size, and non-final @layer .hidden rules."""
    clean_css = COMMENT_RE.sub("", css_text)
    if _IMPORTANT_RE.search(clean_css):
        errs.append(f"[IMPORTANT] {source}: contains forbidden '!important' declaration")
    for m in _FONT_PX_RE.finditer(clean_css):
        if float(m.group(1)) < 11.0:
            errs.append(f"[FONT_FLOOR] {source}: hardcoded font-size {m.group(1)}px < 11px")
    if _CSS_FOOTER_COL_RE.search(clean_css):
        errs.append(f"[RAIL_FOOTER_CLUTTER] {source}: .va-rail-footer declares stacked flex-direction: column")
    check_hidden_layer_css(clean_css, source, errs, layer_order=layer_order)


def has_demo_branch_mock_array(js_text: str) -> bool:
    """Detect inline object-array mock fixtures inside demo branches."""
    if _DEMO_TERNARY_RE.search(js_text):
        return True
    n = len(js_text)
    for m in re.finditer(r"\bif\s*\(", js_text, re.IGNORECASE):
        cond_end = find_closing_delim(js_text, m.end() - 1, "(", ")")
        if cond_end < 0 or not _DEMO_GUARD_RE.search(js_text[m.end() : cond_end - 1]):
            continue
        i = cond_end
        while i < n and js_text[i].isspace():
            i += 1
        if i >= n:
            continue
        if js_text[i] == "{":
            blk_end = find_closing_delim(js_text, i, "{", "}")
            body = js_text[i : blk_end if blk_end > 0 else n]
        else:
            b_depth, k_depth, j, quote = 0, 0, i, ""
            while j < n:
                ch = js_text[j]
                if quote:
                    if ch == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if ch == quote:
                        quote = ""
                    j += 1
                    continue
                if ch in ("'", '"', "`"):
                    quote = ch
                elif ch == "{":
                    b_depth += 1
                elif ch == "}":
                    if b_depth == 0 and k_depth == 0:
                        break
                    b_depth = max(0, b_depth - 1)
                elif ch == "[":
                    k_depth += 1
                elif ch == "]":
                    k_depth = max(0, k_depth - 1)
                elif ch in (";", "\n") and b_depth == 0 and k_depth == 0:
                    j += 1
                    break
                j += 1
            body = js_text[i:j]
        if _MULTI_OBJ_ARR_RE.search(body):
            return True
    return False


_JS_STR_CMT_RE = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`|//[^\n]*|/\*[\s\S]*?\*/")


def audit_js_text(js_text: str, source: str, errs: list[str]) -> None:
    """Check JS text for raw agent brain: storage IDs, mock arrays, and jargon titles."""
    fname = Path(urllib.parse.urlsplit(source).path or source).name.lower()
    if fname.startswith("demo_snapshot") or fname.endswith(".min.js"):
        return
    m_id = _BRAIN_JS_RE.search(js_text)
    if m_id:
        errs.append(f"[INTERNAL_ID] {source}: exposes raw agent storage identifier '{m_id.group(0)[:40]}'")
    if _NAMED_MOCK_ARR_RE.search(js_text) or has_demo_branch_mock_array(js_text):
        errs.append(f"[INLINE_MOCK_DATA] {source}: contains hardcoded inline demo/mock object array")
    if "quiet-cyclical" not in fname and "quiet-evidence-bundle" not in fname:
        for sm in _JS_STR_CMT_RE.finditer(js_text):
            tok = sm.group(0)
            if tok[0] in ("'", '"', "`") and DIURNAL_RE.search(tok):
                errs.append(f"[JARGON_TERMINOLOGY] {source}: UI label uses 'diurnal' — prefer 'Activity by Hour of Day'")
                break


def has_responsive_table_stacking(css_text: str) -> bool:
    """Return True if CSS stacks tables responsively inside narrow media queries."""
    for m in _NARROW_AT_RE.finditer(css_text):
        start, depth, i = m.end(), 1, m.end()
        while i < len(css_text) and depth > 0:
            if css_text[i] == "{":
                depth += 1
            elif css_text[i] == "}":
                depth -= 1
            i += 1
        block = css_text[start:i]
        if re.search(r"\btable\b", block, re.I) and re.search(r"display\s*:\s*(?:block|grid|flex)", block, re.I):
            return True
    return False


CHROME_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
_NON_APP_FIXTURE_DIRS = frozenset({"test", "tests", "__tests__", "spec", "bench", "benches", "corpora", "corpus", "examples", "example", "demo_snapshots"})
_NON_FIXTURE_JSON_RE = re.compile(r"^(?:package(?:-lock)?|tsconfig.*|jsconfig.*|plugin|manifest.*|composer|\.eslintrc.*|\.prettierrc.*|\.visual-lock|settings|config|schema.*)\.json$", re.I)
_MOCK_JSON_NAME_RE = re.compile(r"(?:^|[^a-z0-9])(?:mock|fake|dummy|stub|fixture)(?:[^a-z0-9]|$)|(?:^|[^a-z0-9])demo(?:[_.-]|$)", re.I)
_DOC_ARRAY_KEY_RE = re.compile(r"(?:doc(?:ument)?s?|transcripts?|messages?|turns?|sessions?|entries|items|records|rows)", re.I)
_FAKE_DOC_TEXT_RE = re.compile(r"(?:lorem\s+ipsum|mock\s+doc|fake\s+(?:doc|transcript|session)|sample\s+(?:doc|transcript|session)|demo[_-](?:session|doc|transcript))", re.I)


def has_chrome_emoji(text: str) -> str | None:
    """Return the first pictographic emoji matched in chrome text, or None."""
    m = CHROME_EMOJI_RE.search(text or "")
    return m.group(0) if m else None


def is_json_mock_candidate(path: Path, *, root: Path | None = None) -> bool:
    """Return True if path is a bundled JSON asset outside explicit test/bench/manifest paths."""
    if path.suffix.lower() != ".json" or _NON_FIXTURE_JSON_RE.match(path.name):
        return False
    try:
        rel_parts = path.resolve().relative_to(root.resolve()).parts[:-1] if root else path.parts[:-1]
    except ValueError:
        rel_parts = path.parts[:-1]
    return not any(p.lower() in _NON_APP_FIXTURE_DIRS for p in rel_parts)


def audit_json_text(json_text: str, source: str, errs: list[str]) -> None:
    """Flag static JSON fixtures bundling fabricated document/transcript arrays alongside app code."""
    import json as _json
    try:
        data = _json.loads(json_text)
    except ValueError:
        return
    found_multi = has_doc_key = has_mock_flag = False
    stack: list[tuple[str, object]] = [("", data)]
    while stack:
        key, node = stack.pop()
        if isinstance(node, dict):
            for k, v in node.items():
                kl = str(k).lower()
                if kl in {"is_mock", "is_demo", "mock", "fake", "dummy", "demo"} and v is True:
                    has_mock_flag = True
                if _MOCK_JSON_NAME_RE.search(kl) and isinstance(v, list) and len(v) >= 2:
                    has_mock_flag = True
                stack.append((str(k), v))
        elif isinstance(node, list):
            if len(node) >= 2 and all(isinstance(el, dict) for el in node):
                found_multi = True
                if _DOC_ARRAY_KEY_RE.search(key) or any(_DOC_ARRAY_KEY_RE.search(str(ek)) for el in node[:3] for ek in el):
                    has_doc_key = True
            for el in node[:12]:
                if isinstance(el, (dict, list)):
                    stack.append((key, el))
    if not found_multi:
        return
    fname = Path(urllib.parse.urlsplit(source).path or source).name
    is_demo_snapshot = fname.lower().startswith("demo_snapshot")
    if (_MOCK_JSON_NAME_RE.search(fname) and not is_demo_snapshot) or (has_doc_key and (has_mock_flag or _FAKE_DOC_TEXT_RE.search(json_text))):
        errs.append(f"[JSON_MOCK_FIXTURE] {source}: static JSON fixture bundles fabricated document/transcript array")


DENSITY_WORDS = _DENSITY_WORDS
FOOTER_BANNED_RE = _FOOTER_BANNED_RE



