#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 1 — Portable Static & Headless Chrome HTML/CSS Linter (<= 340L)."""
from __future__ import annotations

import argparse
import functools
import json
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

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "vendor", ".cache"}
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_IMPORTANT_RE = re.compile(r"!\s*important\b", re.I)
_FONT_PX_RE = re.compile(r"(?<![.\d-])font-size\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*px\b", re.I)
_OVERFLOW_RULE_RE = re.compile(
    r"([^{}]+)\{[^{}]*\boverflow(?:-x)?\s*:\s*(?:auto|scroll)\b[^{}]*\}",
    re.I | re.S,
)
_NARROW_AT_RE = re.compile(r"@(?:container|media)[^{]*(?:max-width|max-inline-size|width\s*<=)[^{]*\{", re.I)
_TABLE_BLOCK_RE = re.compile(r"(?:^|[,\s>+~])table\b[^{]*\{[^{}]*\bdisplay\s*:\s*block\b", re.I | re.S)
_WRAPPER_CLASS_HINTS = {"va-table-wrap", "va-figure-scroll", "table-wrapper", "table-wrap", "va-bridge-table-wrap"}

CDP_AUDIT_JS = """
const errs = [], vw = window.innerWidth;
function auditDoc(doc, maxW, ctxTag) {
  if (!doc || !doc.documentElement) return;
  if (doc.documentElement.scrollWidth > maxW + 2) {
    errs.push(`[OVERFLOW${ctxTag}] @${vw}px: scrollWidth=${doc.documentElement.scrollWidth} > width=${maxW}`);
  }
  for (const tbl of doc.querySelectorAll('table')) {
    const tr = tbl.getBoundingClientRect();
    if (tr.width <= 0 || tr.height <= 0) continue;
    if (tr.right > maxW + 2) {
      let scroller = null, p = tbl.parentElement;
      while (p) {
        const ox = getComputedStyle(p).overflowX;
        if ((ox === 'auto' || ox === 'scroll') && p.getBoundingClientRect().right <= maxW + 2) { scroller = p; break; }
        p = p.parentElement;
      }
      if (!scroller) errs.push(`[TABLE_CLIP${ctxTag}] @${vw}px: table right=${tr.right.toFixed(1)}px > ${maxW}px without scroll container`);
    }
  }
  const walker = doc.createTreeWalker(doc.body || doc.documentElement, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    if (!n.nodeValue || !n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest('script,style,noscript,svg,sub,sup')) continue;
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (cs.display === 'none' || cs.visibility === 'hidden' || r.width <= 2 || r.height <= 2) continue;
    const fs = parseFloat(cs.fontSize || '16');
    if (fs < 10.8) {
      errs.push(`[FONT_FLOOR_CDP${ctxTag}] @${vw}px: '${n.nodeValue.trim().slice(0, 24)}' computed fontSize=${fs.toFixed(1)}px < 11px`);
      break;
    }
  }
  for (const fr of doc.querySelectorAll('iframe')) {
    try {
      const fdoc = fr.contentDocument;
      if (fdoc && fdoc.documentElement) {
        const fw = Math.round(fr.clientWidth || maxW);
        auditDoc(fdoc, fw > 0 ? fw : maxW, ctxTag + ' iframe#' + (fr.id || 'frame'));
      }
    } catch (_err) {}
  }
}
auditDoc(document, vw, '');
return errs;
"""


def _audit_css_text(css_text: str, source: str, errs: list[str]) -> None:
    clean = _COMMENT_RE.sub(" ", css_text)
    if _IMPORTANT_RE.search(clean):
        errs.append(f"[IMPORTANT] {source}: contains forbidden '!important' declaration")
    for m in _FONT_PX_RE.finditer(clean):
        if float(m.group(1)) < 11.0:
            errs.append(f"[FONT_FLOOR] {source}: hardcoded font-size {m.group(1)}px < 11px")
            break


def _valid_viewbox(val: str) -> bool:
    parts = re.split(r"[\s,]+", val.strip())
    if len(parts) != 4:
        return False
    try:
        nums = [float(x) for x in parts]
    except ValueError:
        return False
    return nums[2] > 0 and nums[3] > 0


class _QuietHTMLAuditor(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.errs: list[str] = []
        self.css_blocks: list[str] = []
        self.linked_css: list[str] = []
        self.tag_stack: list[tuple[str, dict[str, str]]] = []
        self.svg_stack: list[dict[str, Any]] = []
        self.table_stack: list[dict[str, Any]] = []
        self.recorded_tables: list[dict[str, Any]] = []
        self._in_style = False
        self._in_script = False
        self._style_buf: list[str] = []
        self._in_svg_title = False

    def _ancestor_hidden(self) -> bool:
        return any(a.get("aria-hidden", "").lower() == "true" for _, a in self.tag_stack)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        ad = {k.lower(): (v or "") for k, v in attrs}
        if t == "script":
            self._in_script = True
        if self._in_script:
            return
        if ad.get("style"):
            _audit_css_text(ad["style"], f"{self.source}:{self.getpos()[0]} style=''", self.errs)
        if t == "style":
            self._in_style = True
            self._style_buf = []
        elif t == "link" and "stylesheet" in ad.get("rel", "").lower() and ad.get("href"):
            self.linked_css.append(ad["href"])
        elif t == "svg":
            self.svg_stack.append({
                "line": self.getpos()[0],
                "aria_hidden": self._ancestor_hidden() or ad.get("aria-hidden", "").lower() == "true",
                "viewbox": ad.get("viewbox", ""),
                "role": ad.get("role", "").lower(),
                "has_label": bool((ad.get("aria-label") or ad.get("aria-labelledby") or "").strip()),
                "title": [],
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
                "line": self.getpos()[0],
                "role": ad.get("role", "").lower(),
                "anc_cls": anc_cls,
                "tbl_cls": set(ad.get("class", "").split()),
                "inline_wrap": inline_wrap,
                "max_cols": 0,
                "row_cols": 0,
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
        self.tag_stack.append((t, ad))

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "script":
            self._in_script = False
            return
        if self._in_script:
            return
        if t == "style" and self._in_style:
            self._in_style = False
            css = "".join(self._style_buf)
            self.css_blocks.append(css)
            _audit_css_text(css, f"{self.source} <style>", self.errs)
        elif t == "title":
            self._in_svg_title = False
        elif t == "svg" and self.svg_stack:
            svg = self.svg_stack.pop()
            if not svg["aria_hidden"]:
                if not _valid_viewbox(svg["viewbox"]):
                    self.errs.append(f"[SVG_VIEWBOX] {self.source}:{svg['line']}: non-decorative <svg> missing valid viewBox")
                has_title = bool("".join(svg["title"]).strip())
                if not (has_title or (svg["role"] == "img" and svg["has_label"])):
                    self.errs.append(f"[SVG_A11Y] {self.source}:{svg['line']}: non-decorative <svg> needs role='img' + aria-label or <title>")
        elif t == "table" and self.table_stack:
            self.recorded_tables.append(self.table_stack.pop())
        for i in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[i][0] == t:
                del self.tag_stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._in_script:
            return
        if self._in_style:
            self._style_buf.append(data)
        elif self._in_svg_title and self.svg_stack:
            self.svg_stack[-1]["title"].append(data)


def _has_responsive_table_stacking(css_text: str) -> bool:
    for m in _NARROW_AT_RE.finditer(css_text):
        start, depth, i = m.end(), 1, m.end()
        while i < len(css_text) and depth > 0:
            if css_text[i] == "{":
                depth += 1
            elif css_text[i] == "}":
                depth -= 1
            i += 1
        if _TABLE_BLOCK_RE.search(css_text[start : max(start, i - 1)]):
            return True
    return False


def audit_html_text(html_text: str, source: str, base_dir: Path | None = None) -> list[str]:
    """Run zero-dependency static Quiet UI checks on an HTML document string."""
    auditor = _QuietHTMLAuditor(source)
    auditor.feed(html_text)
    auditor.close()
    css_parts = list(auditor.css_blocks)
    if base_dir is not None:
        base_resolved = base_dir.resolve()
        for href in auditor.linked_css:
            if not href.startswith(("http://", "https://", "//", "data:")):
                rel_href = urllib.parse.unquote(href.split("?", 1)[0].split("#", 1)[0]).lstrip("/")
                if not rel_href:
                    continue
                css_p = (base_resolved / rel_href).resolve()
                if css_p.is_relative_to(base_resolved) and css_p.is_file():
                    css_parts.append(css_p.read_text(encoding="utf-8", errors="ignore"))
    all_css = _COMMENT_RE.sub(" ", "\n".join(css_parts))
    has_stacking = _has_responsive_table_stacking(all_css)
    scroll_classes = set(_WRAPPER_CLASS_HINTS)
    for m in _OVERFLOW_RULE_RE.finditer(all_css):
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


def audit_static_target(target: str) -> tuple[list[str], list[Path]]:
    """Audit a file, directory, or URL statically; return (errors, html_files)."""
    errs: list[str] = []
    if target.startswith(("http://", "https://")):
        with urllib.request.urlopen(target, timeout=10) as resp:
            errs.extend(audit_html_text(resp.read().decode("utf-8", errors="ignore"), target))
        return errs, []
    path = Path(target).resolve()
    if not path.exists():
        return [f"[MISSING_TARGET] Not found: {target}"], []
    files = [path] if path.is_file() else sorted(
        p for p in path.rglob("*") if p.is_file() and not (set(p.parts) & SKIP_DIRS) and p.suffix.lower() in {".html", ".htm", ".css"}
    )
    html_files: list[Path] = []
    for f in files:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        if f.suffix.lower() == ".css":
            _audit_css_text(txt, str(f), errs)
        else:
            html_files.append(f)
            errs.extend(audit_html_text(txt, str(f), base_dir=f.parent))
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


def audit_cdp_urls(urls: list[str]) -> list[str]:
    """Audit URLs in Headless Chrome across 390, 820, and 1440 viewports."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"):
        opts.add_argument(arg)
    errs: list[str] = []
    driver = webdriver.Chrome(options=opts)
    try:
        for url in urls:
            driver.get(url)
            time.sleep(0.18)
            uses_theme = bool(driver.execute_script("return document.documentElement.hasAttribute('data-theme') || !!document.querySelector('[data-theme]');"))
            themes = ("white", "dark") if uses_theme else ("default",)
            for th in themes:
                if th != "default":
                    driver.execute_script("document.documentElement.setAttribute('data-theme', arguments[0]);", th)
                for w, h in ((390, 844), (820, 1180), (1440, 900)):
                    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": w < 600})
                    time.sleep(0.08)
                    res = driver.execute_script(CDP_AUDIT_JS)
                    errs.extend(f"[{url} theme={th}] {e}" for e in res)
    finally:
        driver.quit()
    return errs


def run_cdp_target(target: str, html_files: list[Path]) -> list[str]:
    if target.startswith(("http://", "https://")):
        return audit_cdp_urls([target])
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
        return audit_cdp_urls(urls)
    finally:
        srv.shutdown()
        srv.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Portable Quiet UI HTML/CSS & CDP Linter.")
    parser.add_argument("target", help="HTML/CSS file, directory, or http(s):// URL")
    parser.add_argument("--cdp", action="store_true", help="Run Headless Chrome layout/overflow/table/font checks")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    errs, html_files = audit_static_target(args.target)
    if args.cdp:
        errs.extend(run_cdp_target(args.target, html_files))

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
