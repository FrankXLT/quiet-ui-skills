#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.2 Portable Auditor: Static CSS/HTML/JS & Live Chrome CDP SVG/Overflow Checker."""

from __future__ import annotations

import argparse
import functools
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from audit_quiet_checks import (  # noqa: E402
    BRAIN_TEXT_RE,
    CDP_AUDIT_JS,
    COMMENT_RE,
    OVERFLOW_RULE_RE,
    SELF_BADGE_RE,
    SKIP_DIRS,
    VIEWPORTS,
    WRAPPER_CLASS_HINTS,
    audit_css_text,
    audit_js_text,
    has_responsive_table_stacking,
    parse_mount_prefixes,
    resolve_asset_path,
)


def _valid_viewbox(val: str) -> bool:
    nums = [n for n in re.split(r"[\s,]+", (val or "").strip()) if n]
    if len(nums) != 4:
        return False
    try:
        _, _, w, h = (float(x) for x in nums)
        return w > 0 and h > 0
    except ValueError:
        return False


_HTML_VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
)


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
        self._chrome_depth = 0
        self._chrome_buf: list[str] = []

    def _ancestor_hidden(self) -> bool:
        return any(a.get("aria-hidden", "").lower() == "true" for _, a in self.tag_stack)

    def _is_chrome_tag(self, tag: str, ad: dict[str, str]) -> bool:
        if tag in {"header", "nav"}:
            return True
        cls = ad.get("class", "").lower()
        return any(k in cls for k in ("brand", "topbar", "kicker", "badge", "pill"))

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
            cur = self.table_stack[-1]
            cur["row_cols"] += span
            cur["max_cols"] = max(cur["max_cols"], cur["row_cols"])
        if t not in _HTML_VOID_TAGS:
            if self._chrome_depth > 0 or self._is_chrome_tag(t, ad):
                self._chrome_depth += 1
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
        if self._chrome_depth > 0:
            self._chrome_depth -= 1
            if self._chrome_depth == 0:
                chrome_txt = " ".join(" ".join(self._chrome_buf).split())
                self._chrome_buf = []
                if not self.allow_showcase_chrome:
                    m = SELF_BADGE_RE.search(chrome_txt)
                    if m:
                        self.errs.append(f"[SELF_BADGE] {self.source}: application chrome contains framework self-badge '{m.group(0)}'")
        for i in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[i][0] == t:
                del self.tag_stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_buf.append(data)
            return
        if self._in_style:
            self._style_buf.append(data)
            return
        if self._in_svg_title and self.svg_stack:
            self.svg_stack[-1]["title"].append(data)
        if self._chrome_depth > 0:
            self._chrome_buf.append(data)
        if data.strip() and not any(t in {"pre", "code"} for t, _ in self.tag_stack):
            m = BRAIN_TEXT_RE.search(data)
            if m:
                self.errs.append(f"[INTERNAL_ID] {self.source}:{self.getpos()[0]}: raw internal identifier '{m.group(0)}'")


def audit_html_text(
    html_text: str,
    source: str,
    base_dir: Path | None = None,
    *,
    web_root: Path | None = None,
    mount_prefixes: dict[str, Path] | None = None,
    allow_showcase_chrome: bool = False,
) -> list[str]:
    """Run zero-dependency static Quiet UI checks on an HTML document and mounted assets."""
    auditor = QuietHTMLAuditor(source, allow_showcase_chrome=allow_showcase_chrome)
    auditor.feed(html_text)
    auditor.close()
    for line_no, js_body in auditor.inline_js:
        audit_js_text(js_body, f"{source}:{line_no} <script>", auditor.errs)

    css_parts = list(auditor.css_blocks)
    seen_css: set[Path] = set()
    for href in auditor.linked_css:
        css_p = resolve_asset_path(href, base_dir=base_dir, web_root=web_root, mount_prefixes=mount_prefixes)
        if css_p is not None and css_p not in seen_css:
            seen_css.add(css_p)
            css_txt = css_p.read_text(encoding="utf-8", errors="ignore")
            css_parts.append(css_txt)
            audit_css_text(css_txt, str(css_p), auditor.errs)

    seen_js: set[Path] = set()
    for src in auditor.linked_js:
        js_p = resolve_asset_path(src, base_dir=base_dir, web_root=web_root, mount_prefixes=mount_prefixes)
        if js_p is not None and js_p not in seen_js:
            seen_js.add(js_p)
            js_txt = js_p.read_text(encoding="utf-8", errors="ignore")
            audit_js_text(js_txt, str(js_p), auditor.errs)

    all_css = COMMENT_RE.sub(" ", "\n".join(css_parts))
    has_stacking = has_responsive_table_stacking(all_css)
    scroll_classes = set(WRAPPER_CLASS_HINTS)
    for m in OVERFLOW_RULE_RE.finditer(all_css):
        for sel in m.group(1).split(","):
            term = re.split(r"[\s>+~]+", sel.strip())[-1]
            scroll_classes.update(re.findall(r"\.([A-Za-z0-9_-]+)", term))
    for tbl in auditor.recorded_tables:
        if tbl["role"] in ("presentation", "none") or tbl["max_cols"] < 4:
            continue
        if not (tbl["inline_wrap"] or has_stacking or (tbl["anc_cls"] & scroll_classes)):
            auditor.errs.append(
                f"[TABLE_WRAP] {source}:{tbl['line']}: {tbl['max_cols']}-col <table> needs scroll wrapper or responsive stacking"
            )
    return auditor.errs


def audit_static_target(
    target: str,
    *,
    web_root: Path | None = None,
    mount_prefixes: dict[str, Path] | None = None,
    allow_showcase_chrome: bool = False,
) -> tuple[list[str], list[Path]]:
    """Audit a file, directory, or HTTP(S) URL statically; return (errors, html_files)."""
    errs: list[str] = []
    if target.startswith(("http://", "https://")):
        with urllib.request.urlopen(target, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        errs.extend(
            audit_html_text(
                html, target, web_root=web_root, mount_prefixes=mount_prefixes, allow_showcase_chrome=allow_showcase_chrome
            )
        )
        return errs, []
    path = Path(target).resolve()
    if not path.exists():
        return [f"[MISSING_TARGET] Not found: {target}"], []
    files = [path] if path.is_file() else sorted(
        p for p in path.rglob("*")
        if p.is_file()
        and p.resolve().is_relative_to(path)
        and not (set(p.parts) & SKIP_DIRS)
        and p.suffix.lower() in {".html", ".htm", ".css", ".js"}
    )
    html_files: list[Path] = []
    eff_root = web_root if web_root is not None else (path if path.is_dir() else None)
    seen_msgs: set[str] = set()

    def _add(msgs: list[str]) -> None:
        for msg in msgs:
            if msg not in seen_msgs:
                seen_msgs.add(msg)
                errs.append(msg)

    for f in files:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        sfx = f.suffix.lower()
        if sfx == ".css":
            tmp: list[str] = []
            audit_css_text(txt, str(f), tmp)
            _add(tmp)
        elif sfx == ".js":
            tmp = []
            audit_js_text(txt, str(f), tmp)
            _add(tmp)
        else:
            html_files.append(f)
            _add(
                audit_html_text(
                    txt,
                    str(f),
                    base_dir=f.parent,
                    web_root=eff_root,
                    mount_prefixes=mount_prefixes,
                    allow_showcase_chrome=allow_showcase_chrome,
                )
            )
    return errs, html_files


class _SafeHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def translate_path(self, path: str) -> str:
        out = Path(super().translate_path(path)).resolve()
        root = Path(self.directory).resolve()
        return str(out) if out.is_relative_to(root) else str(root / "__forbidden__")

    def log_message(self, format: str, *args: Any) -> None:
        return


def audit_cdp_urls(urls: list[str], *, allow_showcase_chrome: bool = False) -> list[str]:
    """Audit URLs in Headless Chrome across 390, 900, and 1440 viewports."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    opts = Options()
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin
    for arg in (
        "--headless=new",
        "--ozone-platform=headless",
        "--disable-gpu",
        "--disable-vulkan",
        "--use-gl=angle",
        "--use-angle=swiftshader-webgl",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ):
        opts.add_argument(arg)
    errs: list[str] = []
    driver_bin = os.environ.get("CHROMEDRIVER_BIN")
    driver = webdriver.Chrome(service=Service(executable_path=driver_bin), options=opts) if driver_bin else webdriver.Chrome(options=opts)
    try:
        for url in urls:
            driver.get(url)
            time.sleep(0.28)
            uses_theme = bool(driver.execute_script("return document.documentElement.hasAttribute('data-theme') || !!document.querySelector('[data-theme]');"))
            themes = ("white", "dark") if uses_theme else ("default",)
            for th in themes:
                if th != "default":
                    driver.execute_script("document.documentElement.setAttribute('data-theme', arguments[0]);", th)
                for w, h in VIEWPORTS:
                    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": w < 600})
                    time.sleep(0.12)
                    res = driver.execute_script(CDP_AUDIT_JS, {"allowShowcase": allow_showcase_chrome})
                    errs.extend(f"[{url} theme={th}] {e}" for e in res)
    finally:
        driver.quit()
    return errs


def run_cdp_target(
    target: str,
    html_files: list[Path],
    *,
    allow_showcase_chrome: bool = False,
) -> list[str]:
    if target.startswith(("http://", "https://")):
        return audit_cdp_urls([target], allow_showcase_chrome=allow_showcase_chrome)
    if not html_files:
        return []
    root = Path(target).resolve()
    serve_dir = root.parent if root.is_file() else root
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_SafeHTTPHandler, directory=str(serve_dir)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        urls = [f"{base}/{urllib.parse.quote(f.relative_to(serve_dir).as_posix(), safe='/')}" for f in html_files]
        return audit_cdp_urls(urls, allow_showcase_chrome=allow_showcase_chrome)
    finally:
        srv.shutdown()
        srv.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Portable Quiet UI v9.2 HTML/CSS/JS & CDP Linter.")
    parser.add_argument("target", help="HTML/CSS/JS file, directory, or http(s):// URL")
    parser.add_argument("--cdp", action="store_true", help="Run Headless Chrome checks across 390, 900, and 1440px")
    parser.add_argument("--web-root", help="Filesystem web root for resolving leading '/' CSS and JS paths")
    parser.add_argument("--mount-prefix", action="append", default=[], help="Mount mapping PREFIX=DIR for resolving rooted assets (repeatable)")
    parser.add_argument("--allow-showcase-chrome", action="store_true", help="Allow Quiet UI framework badges in showcase/bench headers")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    wr = Path(args.web_root).expanduser().resolve() if args.web_root else None
    mounts = parse_mount_prefixes(args.mount_prefix)
    errs, html_files = audit_static_target(
        args.target, web_root=wr, mount_prefixes=mounts, allow_showcase_chrome=args.allow_showcase_chrome
    )
    if args.cdp:
        errs.extend(run_cdp_target(args.target, html_files, allow_showcase_chrome=args.allow_showcase_chrome))

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
