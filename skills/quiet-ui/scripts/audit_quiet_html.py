#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.5.0 Portable Auditor: Static CSS/HTML/JS & Live Chrome CDP SVG/Overflow Checker."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from audit_quiet_checks import CDP_AUDIT_JS, audit_cdp_urls, run_cdp_target  # noqa: E402
from audit_ux_and_drift import (  # noqa: E402
    audit_css_drift, audit_html_ux_drift, audit_js_blocklist, find_context_file,
    init_context_file, merge_context_options, parse_context_file,
)
from audit_workbench_probes import audit_workbench_static  # noqa: E402
from audit_static_rules import (  # noqa: E402
    BRAIN_TEXT_RE, COMMENT_RE, DENSITY_WORDS, DIURNAL_RE, FOOTER_BANNED_RE, OVERFLOW_RULE_RE, SELF_BADGE_RE,
    SKIP_DIRS, WRAPPER_CLASS_HINTS, audit_css_text, audit_js_text, audit_json_text, check_hidden_layer_css,
    compute_mount_scopes, extract_layer_order, has_chrome_emoji, has_responsive_table_stacking,
    is_asset_in_scope, is_json_mock_candidate, matches_exclude, parse_mount_prefixes, resolve_asset_detail,
)

_HTML_VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})
_CHROME_CLASSES = frozenset({"va-shell-topbar", "va-shell-brand", "va-topbar", "v9-topbar", "va-brand", "v9-brand", "topbar"})


def _valid_viewbox(val: str) -> bool:
    nums = [n for n in re.split(r"[\s,]+", (val or "").strip()) if n]
    if len(nums) != 4:
        return False
    try:
        _, _, w, h = (float(x) for x in nums)
        return w > 0 and h > 0
    except ValueError:
        return False


class QuietHTMLAuditor(HTMLParser):
    """Zero-dependency HTML AST/style/script extractor for static Quiet UI checks."""

    def __init__(self, source: str, *, allow_showcase_chrome: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.allow_showcase_chrome = allow_showcase_chrome
        self.errs: list[str] = []
        self.css_blocks: list[str] = []
        self.linked_css: list[str] = []
        self.linked_js: list[str] = []
        self.inline_js: list[tuple[int, str]] = []
        self.tag_stack: list[tuple[str, dict[str, str]]] = []
        self.svg_stack: list[dict[str, Any]] = []
        self.table_stack: list[dict[str, Any]] = []
        self.recorded_tables: list[dict[str, Any]] = []
        self._in_style = False
        self._in_script = False
        self._script_line = 0
        self._style_buf: list[str] = []
        self._script_buf: list[str] = []
        self._in_svg_title = False
        self._chrome_entry_len: int | None = None
        self._chrome_buf: list[str] = []
        self._ftr_depth = self._ftr_kids = 0
        self._density_grps: dict[int, int] = {}
        self._ftr_bad = self._tree_card_bad = self._jargon_bad = False
        self._ctrl_cap: list[str] | None = None
        self._ctrl_meta: tuple[Any, ...] | None = None

    def _ancestor_hidden(self) -> bool:
        return any(a.get("aria-hidden", "").lower() == "true" for _, a in self.tag_stack)

    def _is_chrome_tag(self, tag: str, ad: dict[str, str]) -> bool:
        role = ad.get("role", "").lower()
        cls_tokens = set(ad.get("class", "").lower().split())
        if role in {"banner", "navigation"} or (cls_tokens & _CHROME_CLASSES):
            return True
        in_main = any(t == "main" for t, _ in self.tag_stack)
        return (tag in {"header", "footer", "nav"}) and not in_main

    def _flush_chrome_badge(self) -> None:
        chrome_txt = " ".join(" ".join(self._chrome_buf).split())
        self._chrome_buf = []
        self._chrome_entry_len = None
        if chrome_txt and not self.allow_showcase_chrome:
            m = SELF_BADGE_RE.search(chrome_txt)
            if m:
                self.errs.append(f"[SELF_BADGE] {self.source}: application chrome contains framework self-badge '{m.group(0)}'")

    def close(self) -> None:
        super().close()
        if self._chrome_entry_len is not None:
            self._flush_chrome_badge()
        max_d = max(self._density_grps.values(), default=0)
        if max_d > 2:
            self.errs.append(f"[DENSITY_STOP_SPRAWL] {self.source}: {max_d} (>2) density buttons in app chrome; cap M3 density stops at 2")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _HTML_VOID_TAGS:
            self.handle_endtag(tag)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        ad = {k.lower(): (v or "") for k, v in attrs}
        if t == "script":
            self._in_script = True
            self._script_line = self.getpos()[0]
            self._script_buf = []
            if ad.get("src"):
                self.linked_js.append(ad["src"])
            return
        if self._in_script:
            return
        if ad.get("style"):
            audit_css_text(ad["style"], f"{self.source}:{self.getpos()[0]} style=''", self.errs)
        cls = set(ad.get("class", "").lower().split())
        stack_cls = [set(sa.get("class", "").lower().split()) for _, sa in self.tag_stack]
        in_skip = t == "template" or "hidden" in ad or any(st == "template" or "hidden" in sa for st, sa in self.tag_stack)
        in_rail = "va-side-rail" in cls or any("va-side-rail" in sc for sc in stack_cls)
        if not in_skip and not self._tree_card_bad and in_rail:
            is_c, is_tr = bool(cls & {"va-card", "qe-card"}), bool(cls & {"va-tree-row", "va-tree-group", "va-tree-children", "va-tree-dest"})
            if (is_c and is_tr) or (is_c and any(sc & {"va-tree-group", "va-tree-children"} for sc in stack_cls)) or (is_tr and any(sc & {"va-card", "qe-card"} for sc in stack_cls)):
                self._tree_card_bad = True
                self.errs.append(f"[TREE_NESTED_CARD_BORDERS] {self.source}:{self.getpos()[0]}: tree inside .va-side-rail nested inside .va-card")
        if self._ftr_depth > 0 and len(self.tag_stack) == self._ftr_depth and t not in {"script", "style", "template"} and "hidden" not in ad:
            self._ftr_kids += 1
        if not in_skip and "va-rail-footer" in cls:
            self._ftr_depth, self._ftr_kids = len(self.tag_stack) + 1, 0
            if not self._ftr_bad and re.search(r"flex-direction\s*:\s*column", ad.get("style", ""), re.I):
                self._ftr_bad = True
                self.errs.append(f"[RAIL_FOOTER_CLUTTER] {self.source}:{self.getpos()[0]}: .va-rail-footer uses stacked flex-direction: column")
        is_btn = t == "button" or ad.get("role", "").lower() in {"button", "radio", "tab"} or (t == "input" and ad.get("type", "").lower() == "radio")
        has_da = any(k in ad for k in ("data-density", "data-density-stop", "data-density-mode"))
        if not in_skip and (is_btn or (self._ftr_depth > 0 and (t == "a" or bool(cls & {"va-badge", "va-pill"})))):
            is_dc = lambda sc, sa: any(c.startswith("va-density") for c in sc) or "density" in sa.get("aria-label", "").lower() or "data-density-group" in sa or "data-density-toggle" in sa
            in_d = has_da or is_dc(cls, ad) or any(is_dc(sc, sa) for (_, sa), sc in zip(self.tag_stack, stack_cls))
            tb_idxs = [idx for idx, ((_, sa), sc) in enumerate(zip(self.tag_stack, stack_cls)) if is_dc(sc, sa) or sa.get("role", "").lower() == "toolbar" or bool(sc & {"va-rail-footer", "va-tb-group", "va-density-toggle"})]
            grp_key = tb_idxs[-1] if tb_idxs else -1
            in_tb = self._ftr_depth > 0 or bool(tb_idxs)
            if t in _HTML_VOID_TAGS:
                if in_d:
                    self._density_grps[grp_key] = self._density_grps.get(grp_key, 0) + 1
            elif self._ctrl_cap is None:
                self._ctrl_cap, self._ctrl_meta = [], (len(self.tag_stack), in_d, in_tb, self._ftr_depth > 0, cls, grp_key)
        if t == "style":
            self._in_style = True
            self._style_buf = []
        elif t == "link" and "stylesheet" in ad.get("rel", "").lower() and ad.get("href"):
            self.linked_css.append(ad["href"])
        elif t == "svg":
            self.svg_stack.append({
                "line": self.getpos()[0], "aria_hidden": self._ancestor_hidden() or ad.get("aria-hidden", "").lower() == "true",
                "viewbox": ad.get("viewbox", ""), "role": ad.get("role", "").lower(),
                "has_label": bool((ad.get("aria-label") or ad.get("aria-labelledby") or "").strip()), "title": [],
            })
        elif t == "title" and self.svg_stack:
            self._in_svg_title = True
        elif t == "table":
            anc_cls: set[str] = set()
            inline_wrap = False
            for _, aa in self.tag_stack:
                anc_cls.update(aa.get("class", "").split())
                if re.search(r"overflow(?:-x)?\s*:\s*(?:auto|scroll)", aa.get("style", ""), re.I):
                    inline_wrap = True
            self.table_stack.append({
                "line": self.getpos()[0], "role": ad.get("role", "").lower(), "anc_cls": anc_cls,
                "tbl_cls": set(ad.get("class", "").split()), "inline_wrap": inline_wrap, "max_cols": 0, "row_cols": 0,
            })
        elif t == "tr" and self.table_stack:
            self.table_stack[-1]["row_cols"] = 0
        elif t in ("th", "td") and self.table_stack:
            try:
                span = max(1, int(ad.get("colspan") or 1))
            except ValueError:
                span = 1
            self.table_stack[-1]["row_cols"] += span
            self.table_stack[-1]["max_cols"] = max(self.table_stack[-1]["max_cols"], self.table_stack[-1]["row_cols"])
        if t not in _HTML_VOID_TAGS:
            if self._chrome_entry_len is None and self._is_chrome_tag(t, ad):
                self._chrome_entry_len = len(self.tag_stack)
            self.tag_stack.append((t, ad))

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "script":
            if self._in_script and self._script_buf:
                self.inline_js.append((self._script_line, "".join(self._script_buf)))
            self._in_script = False
            self._script_buf = []
            return
        if self._in_script:
            return
        if t == "style" and self._in_style:
            self._in_style = False
            css = "".join(self._style_buf)
            self.css_blocks.append(css)
            audit_css_text(css, f"{self.source} <style>", self.errs)
        elif t == "title":
            self._in_svg_title = False
        elif t == "svg" and self.svg_stack:
            svg = self.svg_stack.pop()
            if not svg["aria_hidden"]:
                if not _valid_viewbox(svg["viewbox"]):
                    self.errs.append(f"[SVG_VIEWBOX] {self.source}:{svg['line']}: non-decorative <svg> missing valid viewBox")
                if not (bool("".join(svg["title"]).strip()) or (svg["role"] == "img" and svg["has_label"])):
                    self.errs.append(f"[SVG_A11Y] {self.source}:{svg['line']}: non-decorative <svg> needs role='img' + aria-label or <title>")
        elif t == "table" and self.table_stack:
            self.recorded_tables.append(self.table_stack.pop())
        for i in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[i][0] == t:
                if self._ctrl_meta is not None and i == self._ctrl_meta[0]:
                    txt = " ".join("".join(self._ctrl_cap or ()).split()).strip()
                    _, in_d, in_tb, in_ftr, bcls, grp_key = self._ctrl_meta
                    if in_d or (in_tb and txt.lower() in DENSITY_WORDS):
                        self._density_grps[grp_key] = self._density_grps.get(grp_key, 0) + 1
                    if in_ftr and not self._ftr_bad and (FOOTER_BANNED_RE.match(txt) or ((bcls & {"va-badge", "va-pill"}) and re.search(r"lock|classic", txt, re.I))):
                        self._ftr_bad = True
                        self.errs.append(f"[RAIL_FOOTER_CLUTTER] {self.source}: .va-rail-footer contains forbidden Lock/Classic control '{txt[:24]}'")
                    self._ctrl_cap = self._ctrl_meta = None
                if i + 1 == self._ftr_depth:
                    if self._ftr_kids > 2 and not self._ftr_bad:
                        self._ftr_bad = True
                        self.errs.append(f"[RAIL_FOOTER_CLUTTER] {self.source}: .va-rail-footer has {self._ftr_kids} (>2) child control groups")
                    self._ftr_depth = 0
                del self.tag_stack[i:]
                break
        if self._chrome_entry_len is not None and len(self.tag_stack) <= self._chrome_entry_len:
            self._flush_chrome_badge()

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_buf.append(data)
            return
        if self._in_style:
            self._style_buf.append(data)
            return
        if self._in_svg_title and self.svg_stack:
            self.svg_stack[-1]["title"].append(data)
        if self._chrome_entry_len is not None:
            self._chrome_buf.append(data)
        if self._ctrl_cap is not None:
            self._ctrl_cap.append(data)
        if data.strip() and not any(t in {"pre", "code"} for t, _ in self.tag_stack):
            m = BRAIN_TEXT_RE.search(data)
            if m:
                self.errs.append(f"[INTERNAL_ID] {self.source}:{self.getpos()[0]}: raw internal identifier '{m.group(0)}'")
            if not self._jargon_bad and DIURNAL_RE.search(data):
                self._jargon_bad = True
                self.errs.append(f"[JARGON_TERMINOLOGY] {self.source}:{self.getpos()[0]}: copy uses 'diurnal' — prefer 'Activity by Hour of Day'")
            in_chrome = any(
                t in {"header", "nav", "button"} or ad.get("role", "").lower() in {"tab", "toolbar"}
                for t, ad in self.tag_stack
            )
            if in_chrome and not any(t == "svg" for t, _ in self.tag_stack):
                em = has_chrome_emoji(data)
                if em:
                    self.errs.append(f"[EMOJI_IN_CHROME] {self.source}:{self.getpos()[0]}: chrome contains emoji '{em}'")


def audit_html_text(
    html_text: str, source: str, base_dir: Path | None = None, *, web_root: Path | None = None,
    mount_prefixes: dict[str, Path] | None = None, mount_scopes: dict[str, Path] | None = None,
    exclude: tuple[str, ...] | list[str] | None = None, audit_mounted_external: bool = False,
    allow_showcase_chrome: bool = False, strict_drift: bool = False, context: dict[str, Any] | None = None,
) -> list[str]:
    """Run zero-dependency static Quiet UI checks on an HTML document and mounted assets."""
    auditor = QuietHTMLAuditor(source, allow_showcase_chrome=allow_showcase_chrome)
    auditor.feed(html_text)
    auditor.close()
    audit_html_ux_drift(html_text, source, auditor.errs, strict_drift=strict_drift, context=context)
    audit_workbench_static(html_text, source, auditor.errs)
    for line_no, js_body in auditor.inline_js:
        audit_js_text(js_body, f"{source}:{line_no} <script>", auditor.errs)
        audit_js_blocklist(js_body, f"{source}:{line_no} <script>", context, auditor.errs)

    css_parts, in_scope_css, seen_css = list(auditor.css_blocks), [], set()
    for href in auditor.linked_css:
        if matches_exclude(href, exclude):
            continue
        css_p, pfx, missing = resolve_asset_detail(href, base_dir=base_dir, web_root=web_root, mount_prefixes=mount_prefixes)
        if missing:
            auditor.errs.append(f"[MISSING_ASSET] {source}: mounted stylesheet not found '{href}' -> {css_p}")
            continue
        if css_p is None or matches_exclude(css_p, exclude, root=base_dir or web_root) or css_p in seen_css:
            continue
        seen_css.add(css_p)
        css_txt = css_p.read_text(encoding="utf-8", errors="ignore")
        css_parts.append(css_txt)
        if is_asset_in_scope(css_p, pfx, mount_scopes, audit_mounted_external=audit_mounted_external):
            in_scope_css.append((str(css_p), css_txt))

    all_css = COMMENT_RE.sub(" ", "\n".join(css_parts))
    combined_order = extract_layer_order(all_css)
    for css_src, css_txt in in_scope_css:
        audit_css_text(css_txt, css_src, auditor.errs, layer_order=combined_order)
        if strict_drift:
            audit_css_drift(css_txt, css_src, auditor.errs)
    for css_txt in auditor.css_blocks:
        if strict_drift:
            audit_css_drift(css_txt, f"{source} <style>", auditor.errs)
        clean_blk = COMMENT_RE.sub("", css_txt)
        if combined_order and not extract_layer_order(clean_blk):
            check_hidden_layer_css(clean_blk, f"{source} <style>", auditor.errs, layer_order=combined_order)

    seen_js: set[Path] = set()
    for src in auditor.linked_js:
        if matches_exclude(src, exclude):
            continue
        js_p, pfx, missing = resolve_asset_detail(src, base_dir=base_dir, web_root=web_root, mount_prefixes=mount_prefixes)
        if missing:
            auditor.errs.append(f"[MISSING_ASSET] {source}: mounted script not found '{src}' -> {js_p}")
            continue
        if js_p is None or matches_exclude(js_p, exclude, root=base_dir or web_root) or js_p in seen_js:
            continue
        seen_js.add(js_p)
        if is_asset_in_scope(js_p, pfx, mount_scopes, audit_mounted_external=audit_mounted_external):
            js_txt = js_p.read_text(encoding="utf-8", errors="ignore")
            audit_js_text(js_txt, str(js_p), auditor.errs)
            audit_js_blocklist(js_txt, str(js_p), context, auditor.errs)

    has_stacking, scroll_classes = has_responsive_table_stacking(all_css), set(WRAPPER_CLASS_HINTS)
    for m in OVERFLOW_RULE_RE.finditer(all_css):
        for sel in m.group(1).split(","):
            scroll_classes.update(re.findall(r"\.([A-Za-z0-9_-]+)", re.split(r"[\s>+~]+", sel.strip())[-1]))
    for tbl in auditor.recorded_tables:
        if tbl["role"] not in ("presentation", "none") and tbl["max_cols"] >= 4 and not (tbl["inline_wrap"] or has_stacking or (tbl["anc_cls"] & scroll_classes)):
            auditor.errs.append(f"[TABLE_WRAP] {source}:{tbl['line']}: {tbl['max_cols']}-col <table> needs scroll wrapper or responsive stacking")
    return list(dict.fromkeys(auditor.errs))


def audit_static_target(
    target: str, *, web_root: Path | None = None, mount_prefixes: dict[str, Path] | None = None,
    exclude: tuple[str, ...] | list[str] | None = None, audit_mounted_external: bool = False,
    allow_showcase_chrome: bool = False, strict_drift: bool = False, context: dict[str, Any] | None = None,
) -> tuple[list[str], list[Path]]:
    """Audit a file, directory, or HTTP(S) URL statically; return (errors, html_files)."""
    errs, mount_scopes = [], compute_mount_scopes(target, mount_prefixes)
    if target.startswith(("http://", "https://")):
        with urllib.request.urlopen(target, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        errs.extend(audit_html_text(
            html, target, web_root=web_root, mount_prefixes=mount_prefixes, mount_scopes=mount_scopes,
            exclude=exclude, audit_mounted_external=audit_mounted_external,
            allow_showcase_chrome=allow_showcase_chrome, strict_drift=strict_drift, context=context,
        ))
        return errs, []
    path = Path(target).resolve()
    if not path.exists():
        return [f"[MISSING_TARGET] Not found: {target}"], []
    files = [path] if path.is_file() else sorted(
        p for p in path.rglob("*")
        if p.is_file() and p.resolve().is_relative_to(path) and not (set(p.parts) & SKIP_DIRS)
        and not matches_exclude(p, exclude, root=path) and p.suffix.lower() in {".html", ".htm", ".css", ".js", ".json"}
    )
    html_files, eff_root, seen_msgs = [], web_root if web_root is not None else (path if path.is_dir() else None), set()

    def _add(msgs: list[str]) -> None:
        for msg in msgs:
            if msg not in seen_msgs:
                seen_msgs.add(msg)
                errs.append(msg)

    for f in files:
        txt, sfx, tmp = f.read_text(encoding="utf-8", errors="ignore"), f.suffix.lower(), []
        if sfx == ".css":
            audit_css_text(txt, str(f), tmp)
            if strict_drift:
                audit_css_drift(txt, str(f), tmp)
        elif sfx == ".js":
            audit_js_text(txt, str(f), tmp)
            audit_js_blocklist(txt, str(f), context, tmp)
        elif sfx == ".json":
            if path.is_file() or is_json_mock_candidate(f, root=path):
                audit_json_text(txt, str(f), tmp)
        else:
            html_files.append(f)
            tmp = audit_html_text(
                txt, str(f), base_dir=f.parent, web_root=eff_root, mount_prefixes=mount_prefixes,
                mount_scopes=mount_scopes, exclude=exclude, audit_mounted_external=audit_mounted_external,
                allow_showcase_chrome=allow_showcase_chrome, strict_drift=strict_drift, context=context,
            )
        _add(tmp)
    return errs, html_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Portable Quiet UI v9.7.0 HTML/CSS/JS & CDP Linter.")
    parser.add_argument("target", nargs="?", help="HTML/CSS/JS file, directory, or http(s):// URL")
    parser.add_argument("--cdp", action="store_true", help="Run Headless Chrome checks across 390, 820, and 1440px")
    parser.add_argument("--web-root", help="Filesystem web root for resolving leading '/' CSS and JS paths")
    parser.add_argument("--mount-prefix", action="append", default=[], help="Mount mapping PREFIX=DIR for resolving rooted assets (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude filename, path suffix, or glob pattern (repeatable)")
    parser.add_argument("--audit-mounted-external", action="store_true", help="Lint resolved --mount-prefix assets outside the target subpath")
    parser.add_argument("--allow-showcase-chrome", action="store_true", help="Allow Quiet UI framework badges in showcase/bench headers")
    parser.add_argument("--context", help="Explicit path to persistent .quiet-ui.md project contract")
    parser.add_argument("--init-context", help="Create starter .quiet-ui.md contract at PATH if missing")
    parser.add_argument("--strict-drift", action="store_true", help="Fail raw hex/rgb/hsl colors in app CSS and inline presentation styles")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    if args.init_context:
        ctx_p, created = init_context_file(args.init_context)
        if not args.target:
            print(json.dumps({"ok": True, "context": str(ctx_p), "created": created}) if args.json else f"[{'INIT' if created else 'EXISTS'}] {ctx_p}")
            return 0
    if not args.target:
        parser.error("target is required unless --init-context is provided")

    wr = Path(args.web_root).expanduser().resolve() if args.web_root else None
    ctx_path, ctx_errs = find_context_file(args.target, args.context)
    ctx = parse_context_file(ctx_path) if ctx_path else None
    mounts, excludes, strict_drift = merge_context_options(ctx, parse_mount_prefixes(args.mount_prefix), args.exclude, args.strict_drift)
    errs: list[str] = list(ctx_errs)
    if not ctx_errs:
        st_errs, html_files = audit_static_target(
            args.target, web_root=wr, mount_prefixes=mounts, exclude=excludes,
            audit_mounted_external=args.audit_mounted_external, allow_showcase_chrome=args.allow_showcase_chrome,
            strict_drift=strict_drift, context=ctx,
        )
        errs.extend(st_errs)
        if args.cdp:
            errs.extend(run_cdp_target(args.target, html_files, allow_showcase_chrome=args.allow_showcase_chrome, context=ctx))

    if args.json:
        print(json.dumps({"ok": not errs, "errors": errs}, indent=2))
    elif errs:
        for e in errs:
            print(f"[FAIL] {e}")
        print(f"[ERROR] {len(errs)} Quiet UI lint violation(s) found.")
    else:
        print(f"[PASS] Quiet UI audit clean -> {args.target}")
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
