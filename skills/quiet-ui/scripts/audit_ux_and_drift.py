# SPDX-License-Identifier: Apache-2.0
"""Persistent .quiet-ui.md context contract, UX micro-state gates, and strict drift lints."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from audit_static_rules import find_closing_delim

DEFAULT_CONTEXT_TEMPLATE = (
    "# .quiet-ui.md — Persistent Quiet UI Project Contract\n"
    "- **Project Mode**: Greenfield\n- **Primary Medium**: M3\n"
    "- **Chromatic Budget**: Quiet Cockpit\n- **Navigation Shell**: N1\n"
    "- **Strict Drift**: false\n- **Mount Prefixes**:\n"
    "- **Excludes**: `*.min.js`, `vendor/**`\n\n"
    "## Capability Parity Ledger\n| Existing Capability | Disposition | Target Pattern |\n| :--- | :--- | :--- |\n\n"
    "## Deprecation Blocklist\n- selector: `#legacy-deprecated-selector`\n- copy: `diurnal`\n"
)

_VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})
_EXEMPT_CSS_HDR_RE = re.compile(r"(?:@layer\s+(?:tokens|legacy)\b|:root\b|\[data-theme\b|@media\s+print\b|@media[^{]*forced-colors)", re.I)
_RAW_COLOR_RE = re.compile(r"(?:#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b|\b(?:rgba?|hsla?)\s*\()", re.I)
_INLINE_DRIFT_PROPS = frozenset(
    "color background background-color font-size padding padding-top padding-right padding-bottom "
    "padding-left padding-inline padding-block margin margin-top margin-right margin-bottom margin-left margin-inline margin-block".split()
)
_JS_STR_CMT_RE = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`|//[^\n]*|/\*[\s\S]*?\*/")
_SKIP_INPUT_TYPES = frozenset({"hidden", "submit", "reset", "button", "image"})


def _strip_q(val: str) -> str:
    return val.strip().strip("`'\"").strip()


def _whole_word_re(term: str) -> re.Pattern[str]:
    pre = r"(?<![A-Za-z0-9_])" if term and term[0].isalnum() else ""
    post = r"(?![A-Za-z0-9_])" if term and term[-1].isalnum() else ""
    return re.compile(f"{pre}{re.escape(term)}{post}", re.IGNORECASE)


def init_context_file(raw_path: str) -> tuple[Path, bool]:
    """Create starter .quiet-ui.md if absent; return (resolved_path, created)."""
    p = Path(raw_path).expanduser()
    target = (p / ".quiet-ui.md") if (p.is_dir() or p.suffix.lower() != ".md") else p
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return target.resolve(), False
    target.write_text(DEFAULT_CONTEXT_TEMPLATE, encoding="utf-8")
    return target.resolve(), True


def find_context_file(target: str | None, explicit: str | None = None) -> tuple[Path | None, list[str]]:
    """Resolve explicit --context PATH or auto-discover .quiet-ui.md up to 3 ancestor dirs."""
    if explicit:
        p = Path(explicit).expanduser()
        p = (p / ".quiet-ui.md") if p.is_dir() else p
        return (p.resolve(), []) if p.is_file() else (None, [f"[MISSING_CONTEXT] Context file not found: {explicit}"])
    if not target or target.startswith(("http://", "https://")):
        return None, []
    cur = Path(target).expanduser().resolve()
    cur = cur if cur.is_dir() else cur.parent
    for _ in range(4):
        if (cur / ".quiet-ui.md").is_file():
            return cur / ".quiet-ui.md", []
        if cur.parent == cur:
            break
        cur = cur.parent
    return None, []


def parse_context_file(ctx_path: Path) -> dict[str, Any]:
    """Parse .quiet-ui.md into mounts, excludes, strict_drift, and deprecation blocklists."""
    ctx: dict[str, Any] = {"path": str(ctx_path), "mount_prefixes": {}, "excludes": [], "strict_drift": False, "blocklist_selectors": [], "blocklist_copy": []}
    in_blocklist = False
    for raw_ln in ctx_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = raw_ln.strip()
        if ln.startswith("## "):
            in_blocklist = ln[3:].strip().lower().startswith("deprecation blocklist")
            continue
        if not ln or ln.startswith(("#", "|", ">", "```", "~~~")):
            continue
        if in_blocklist:
            item = ln.lstrip("-* ").strip()
            for rgx, key in ((r"^selector\s*:\s*(.+)$", "blocklist_selectors"), (r"^copy\s*:\s*(.+)$", "blocklist_copy")):
                m = re.match(rgx, item, re.I)
                if m and _strip_q(m.group(1)):
                    ctx[key].append(_strip_q(m.group(1)))
                    break
            continue
        m_kv = re.match(r"^(?:[-*]\s+)?\*{0,2}([A-Za-z0-9 _-]+?)\*{0,2}\s*:\s*(.*)$", ln)
        if not m_kv:
            continue
        k, v = m_kv.group(1).strip().lower(), m_kv.group(2).strip()
        if k == "strict drift":
            ctx["strict_drift"] = _strip_q(v).lower() in {"true", "yes", "1", "on"}
        elif k == "mount prefixes" and v:
            for item in (_strip_q(p) for p in v.split(",")):
                if "=" in item:
                    rpfx, rrdir = (_strip_q(x) for x in item.split("=", 1))
                    if rpfx and rrdir:
                        norm = "/" + rpfx.strip("/") if rpfx != "/" else "/"
                        dp = Path(rrdir).expanduser()
                        ctx["mount_prefixes"][norm] = (dp if dp.is_absolute() else (ctx_path.parent / dp)).resolve()
        elif k == "excludes" and v:
            ctx["excludes"].extend(x for x in (_strip_q(p) for p in v.split(",")) if x)
    return ctx


def merge_context_options(ctx: dict[str, Any] | None, cli_mounts: dict[str, Path], cli_excludes: list[str], cli_strict: bool) -> tuple[dict[str, Path], list[str], bool]:
    """Merge .quiet-ui.md settings with explicit CLI flags (CLI wins on prefix conflict)."""
    mounts = {**((ctx or {}).get("mount_prefixes") or {}), **cli_mounts}
    excludes = list(dict.fromkeys([*((ctx or {}).get("excludes") or ()), *cli_excludes]))
    return mounts, excludes, bool(cli_strict or (ctx or {}).get("strict_drift"))


def _strip_var_fallbacks(expr: str) -> str:
    out, i, n = [], 0, len(expr)
    while i < n:
        low = expr[i : i + 4].lower()
        if low in {"var(", "url("}:
            end = find_closing_delim(expr, i + 3, "(", ")", line_comments=False, backtick_quotes=False)
            if end > i:
                out.append(f"var({expr[i + 4 : end - 1].split(',', 1)[0].strip()})" if low == "var(" else "url()")
                i = end
                continue
        out.append(expr[i])
        i += 1
    return "".join(out)


def _flush_css_decl(decl_parts: list[tuple[int, str]], source: str, errs: list[str]) -> None:
    if not decl_parts:
        return
    txt, start_ln = "".join(c for _, c in decl_parts).strip(), decl_parts[0][0]
    decl_parts.clear()
    if txt and not txt.startswith(("--", "@")) and ":" in txt:
        m = _RAW_COLOR_RE.search(_strip_var_fallbacks(txt.split(":", 1)[1]))
        if m:
            errs.append(f"[TOKEN_BYPASS_HEX] {source}:{start_ln}: raw color '{m.group(0)}' outside tokens/themes; use CSS var(--*)")


def audit_css_drift(css_text: str, source: str, errs: list[str]) -> None:
    """Flag raw #hex, rgb(), and hsl() color literals outside token/theme/exempt CSS scopes."""
    skip_stack, hdr_buf, decl_parts, in_cmt, quote = [], [], [], False, ""
    for line_no, raw_ln in enumerate(css_text.splitlines(), 1):
        exempt, i, n = bool(re.search(r"/\*\s*token-exempt\s*\*/", raw_ln, re.I)), 0, len(raw_ln)
        while i < n:
            if in_cmt:
                end = raw_ln.find("*/", i)
                in_cmt, i = (False, end + 2) if end >= 0 else (True, n)
                continue
            ch, active = raw_ln[i], bool(skip_stack and not any(skip_stack))
            if quote:
                step = 2 if (ch == "\\" and i + 1 < n) else 1
                if active and not exempt:
                    decl_parts.append((line_no, raw_ln[i : i + step]))
                if step == 1 and ch == quote:
                    quote = ""
                i += step
                continue
            if raw_ln[i : i + 2] == "/*":
                in_cmt, i = True, i + 2
                continue
            if ch in ("'", '"'):
                quote = ch
                if active and not exempt:
                    decl_parts.append((line_no, ch))
            elif ch == "{":
                decl_parts.clear()
                skip_stack.append(any(skip_stack) or bool(_EXEMPT_CSS_HDR_RE.search("".join(hdr_buf).strip())))
                hdr_buf.clear()
            elif ch in "};":
                _flush_css_decl(decl_parts, source, errs)
                hdr_buf.clear()
                if ch == "}" and skip_stack:
                    skip_stack.pop()
            else:
                if not any(skip_stack):
                    hdr_buf.append(ch)
                if active and not exempt:
                    decl_parts.append((line_no, ch))
            i += 1
        if decl_parts and not exempt:
            decl_parts.append((line_no, "\n"))
    _flush_css_decl(decl_parts, source, errs)


def _matches_selector_static(tag: str, attrs: dict[str, str], sel: str) -> bool:
    s = sel.strip()
    if not s:
        return False
    if s[0] in "#.":
        ident = s[1:]
        return bool(ident) and ((attrs.get("id", "") == ident) if s[0] == "#" else (ident in set(attrs.get("class", "").split())))
    m = re.match(r"^\[([A-Za-z0-9_-]+)(?:=[\"']?([^\"'\]]+)[\"']?)?\]$", s)
    return ((m.group(1).lower() in attrs) if m.group(2) is None else (attrs.get(m.group(1).lower()) == m.group(2))) if m else (tag == s.lower())


class _UXDriftParser(HTMLParser):
    def __init__(self, source: str, errs: list[str], strict_drift: bool, ctx: dict[str, Any] | None) -> None:
        super().__init__(convert_charrefs=True)
        self.source, self.errs, self.strict_drift = source, errs, strict_drift
        self.selectors: list[str] = list((ctx or {}).get("blocklist_selectors") or ())
        self.copy_res: list[tuple[str, re.Pattern[str]]] = [(c, _whole_word_re(c)) for c in ((ctx or {}).get("blocklist_copy") or ())]
        self.tag_stack, self.label_fors, self.controls, self.empty_stack, self._in_code = [], set(), [], [], False

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _VOID_TAGS:
            self.handle_endtag(tag)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t, line, ad = tag.lower(), self.getpos()[0], {k.lower(): (v or "") for k, v in attrs}
        if t in {"script", "style"}:
            self._in_code = True
            self.tag_stack.append((t, ad))
            return
        if self._in_code:
            return
        cls = set(ad.get("class", "").lower().split())
        if t == "label" and ad.get("for", "").strip():
            self.label_fors.add(ad["for"].strip())
        if t in {"input", "select", "textarea"} and not (t == "input" and ad.get("type", "text").lower() in _SKIP_INPUT_TYPES):
            ok = bool(ad.get("aria-label", "").strip() or ad.get("aria-labelledby", "").strip() or ad.get("title", "").strip() or any(st == "label" for st, _ in self.tag_stack))
            self.controls.append({"tag": t, "id": ad.get("id", "").strip(), "line": line, "ok": ok})
        if self.empty_stack and (t == "button" or (t == "a" and "href" in ad) or ad.get("role", "").lower() == "button"):
            for box in self.empty_stack:
                box["has_action"] = True
        if t not in _VOID_TAGS and (("va-empty-state" in cls and ad.get("data-kind", "").lower() == "filtered") or ad.get("data-empty-kind", "").lower() == "filtered"):
            self.empty_stack.append({"depth": len(self.tag_stack), "line": line, "has_action": False})
        if self.strict_drift and ad.get("style"):
            for decl in ad["style"].split(";"):
                if ":" in decl:
                    p, v = (x.strip().lower() for x in decl.split(":", 1))
                    if p and not p.startswith("--") and not (p == "display" and v == "none") and (p in _INLINE_DRIFT_PROPS or _RAW_COLOR_RE.search(_strip_var_fallbacks(v))):
                        self.errs.append(f"[INLINE_STYLE_SPRAWL] {self.source}:{line}: inline style sets '{p}' instead of utility/view class")
                        break
        for sel in self.selectors:
            if _matches_selector_static(t, ad, sel):
                self.errs.append(f"[BLOCKLIST_RESURRECTION] {self.source}:{line}: HTML matches blocklisted selector '{sel}'")
        if t not in _VOID_TAGS:
            self.tag_stack.append((t, ad))

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        for i in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[i][0] == t:
                while self.empty_stack and self.empty_stack[-1]["depth"] >= i:
                    box = self.empty_stack.pop()
                    if not box["has_action"]:
                        self.errs.append(f"[DEAD_END_ZERO_STATE] {self.source}:{box['line']}: filtered zero-state missing Clear/Reset <button> or <a href>")
                del self.tag_stack[i:]
                break
        self._in_code = any(st in {"script", "style"} for st, _ in self.tag_stack)

    def handle_data(self, data: str) -> None:
        if not self._in_code and self.copy_res and data.strip() and not any(st in {"pre", "code"} for st, _ in self.tag_stack):
            for raw_copy, pat in self.copy_res:
                if pat.search(data):
                    self.errs.append(f"[BLOCKLIST_RESURRECTION] {self.source}:{self.getpos()[0]}: HTML text matches blocklisted copy '{raw_copy}'")

    def close(self) -> None:
        super().close()
        for c in self.controls:
            if not c["ok"] and not (c["id"] and c["id"] in self.label_fors):
                self.errs.append(f"[UNLABELED_FORM_CONTROL] {self.source}:{c['line']}: <{c['tag']}> missing <label>, aria-label, aria-labelledby, or title")


def audit_html_ux_drift(html_text: str, source: str, errs: list[str], *, strict_drift: bool = False, context: dict[str, Any] | None = None) -> None:
    """Run static form-label, zero-state recovery, deprecation blocklist, and inline drift checks."""
    parser = _UXDriftParser(source, errs, strict_drift, context)
    parser.feed(html_text)
    parser.close()


def audit_js_blocklist(js_text: str, source: str, context: dict[str, Any] | None, errs: list[str]) -> None:
    """Check non-comment JS strings for blocklisted selectors or copy terms from .quiet-ui.md."""
    if not context or (not context.get("blocklist_selectors") and not context.get("blocklist_copy")):
        return
    str_blob = "\n".join(m.group(0) for m in _JS_STR_CMT_RE.finditer(js_text) if m.group(0)[0] in ("'", '"', "`"))
    for sel in context.get("blocklist_selectors") or ():
        name = sel[1:] if sel.startswith(("#", ".")) else sel
        if name and _whole_word_re(name).search(str_blob):
            errs.append(f"[BLOCKLIST_RESURRECTION] {source}: JS references blocklisted selector '{sel}'")
    for term in context.get("blocklist_copy") or ():
        if _whole_word_re(term).search(str_blob):
            errs.append(f"[BLOCKLIST_RESURRECTION] {source}: JS string matches blocklisted copy '{term}'")


CDP_UX_DRIFT_JS = r"""
function auditDocV940(doc, win, ctxTag, opts) {
  const isShown = (el) => { for (let p = el; p && p.nodeType === 1; p = p.parentElement) if (p.hasAttribute('hidden') || win.getComputedStyle(p).display === 'none') return false; return true; };
  for (const el of doc.querySelectorAll('input, select, textarea')) {
    if (el.tagName === 'INPUT' && /^(hidden|submit|reset|button|image)$/i.test(el.type || 'text')) continue;
    const hasLab = (el.labels && el.labels.length > 0) || !!(el.getAttribute('aria-label') || '').trim() || !!(el.getAttribute('aria-labelledby') || '').trim() || !!(el.getAttribute('title') || '').trim();
    if (!hasLab) pushErr(`[UNLABELED_FORM_CONTROL${ctxTag}] @${vw}px: <${el.tagName.toLowerCase()}> missing accessible label`);
  }
  for (const box of doc.querySelectorAll('.va-empty-state[data-kind="filtered"], [data-empty-kind="filtered"]')) {
    if (!box.querySelector('button, a[href], [role="button"]')) pushErr(`[DEAD_END_ZERO_STATE${ctxTag}] @${vw}px: filtered zero-state missing Clear/Reset recovery action`);
  }
  for (const sel of (Array.isArray(opts && opts.blocklistSelectors) ? opts.blocklistSelectors : [])) {
    try { if (sel && doc.querySelectorAll(sel).length > 0) pushErr(`[BLOCKLIST_RESURRECTION${ctxTag}] @${vw}px: DOM matches blocklisted selector '${sel}'`); } catch (_e) {}
  }
  const blkCopy = Array.isArray(opts && opts.blocklistCopy) ? opts.blocklistCopy : [];
  if (blkCopy.length && doc.body) {
    const res = blkCopy.map((t) => { const s = String(t), e = s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); return [t, new RegExp(`${/^[A-Za-z0-9_]/.test(s) ? '(?:^|[^A-Za-z0-9_])' : ''}${e}${/[A-Za-z0-9_]$/.test(s) ? '(?=$|[^A-Za-z0-9_])' : ''}`, 'i')]; });
    const tw = doc.createTreeWalker(doc.body, 4);
    for (let tn; (tn = tw.nextNode()); ) {
      const pe = tn.parentElement;
      if (!pe || pe.closest('pre, code, script, style') || !isShown(pe)) continue;
      for (const [term, reObj] of res) { if (reObj.test(tn.nodeValue || '')) pushErr(`[BLOCKLIST_RESURRECTION${ctxTag}] @${vw}px: DOM text matches blocklisted copy '${term}'`); }
    }
  }
}
"""
