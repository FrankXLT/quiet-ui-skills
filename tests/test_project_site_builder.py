#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unit and CLI integration tests for src/site_shell and build_project_site.py."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from customizations.scripts.verify_customization import check_immutability  # noqa: E402
from src.site_shell import (  # noqa: E402
    build_project_site,
    compile_markdown_docs,
    load_site_config,
    render_demo_return_bar,
    render_social_png,
    render_social_svg,
)
from src.site_shell.markdown_docs import _sanitize_svg_html, compile_diagram_spec  # noqa: E402
from src.site_shell.templates import render_chrome_top, safe_href, to_page_href  # noqa: E402

QUIET_CFG_PATH = REPO_ROOT / "src" / "chrome" / "quiet-ui-site.json"
STARTER_CFG_PATH = REPO_ROOT / "customizations" / "project-site-starter" / "oaw-site.json"
BUILD_CLI = REPO_ROOT / "customizations" / "scripts" / "build_project_site.py"
AUDITOR_CLI = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_html.py"
HAS_PIL = importlib.util.find_spec("PIL") is not None

BANNED_EMOJIS = ("✨", "⚡", "☀", "🛡", "●", "&#10024;", "🚀", "💡", "🔥", "⚠️", "❌", "✅")
PIPELINE_SPEC: dict[str, Any] = {
    "$schema": "urn:quiet-ui:schema:v9:schematic",
    "id": "unit-pipeline",
    "schematic_kind": "pipeline",
    "metadata": {"title": "Unit Pipeline", "rigor_level": "L1"},
    "stages": ["Inputs", "Build"],
    "nodes": [
        {"id": "src", "stage": 0, "label": "Markdown", "metric": "2 files"},
        {"id": "out", "stage": 1, "label": "HTML", "metric": "Static", "focal": True},
    ],
    "edges": [{"from": "src", "to": "out"}],
}


def _minimal_raw_config() -> dict[str, Any]:
    return {
        "$schema": "urn:quiet-ui:schema:v9:project-site",
        "project": {
            "slug": "sample-tool",
            "title": "Sample Tool",
            "tagline": "Clean static documentation portal",
            "version": "1.0.0",
            "repo_url": "https://github.com/example/sample-tool",
            "site_url": "https://example.github.io/sample-tool/",
            "license_summary": "MIT",
        },
        "routes": {
            "overview": {"href": "index.html", "label": "Overview"},
            "demo": {"href": "demo/index.html", "label": "Demo", "enabled": False},
            "docs": {"href": "docs/index.html", "label": "Docs"},
        },
        "docs_reader": {
            "title": "Documentation",
            "sources": [{"id": "guide", "path": "docs/guide.md", "title": "Guide"}],
        },
        "social_preview": {
            "image_path": "assets/social-preview.png",
            "title": "Sample Tool",
            "subtitle": "Static site preview",
            "accent_hex": "#1D4ED8",
        },
    }


def _assert_svg_clean(test: unittest.TestCase, svg_text: str) -> None:
    test.assertIn("<svg", svg_text)
    test.assertNotRegex(svg_text, r'preserveAspectRatio\s*=\s*["\']none["\']')
    missing_fill = re.findall(r"<path\b(?![^>]*\bfill\s*=)[^>]*>", svg_text, flags=re.I)
    test.assertEqual(missing_fill, [], f"<path> missing fill=: {missing_fill}")
    for emoji in BANNED_EMOJIS:
        test.assertNotIn(emoji, svg_text)


def _find_broken_relative_links(site_root: Path, html_rel: str) -> list[str]:
    page = site_root / html_rel
    txt = page.read_text(encoding="utf-8")
    broken: list[str] = []
    for ref in re.findall(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", txt):
        if ref.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        clean = ref.split("#", 1)[0].split("?", 1)[0]
        if not clean:
            continue
        target = (page.parent / clean).resolve()
        if not target.is_relative_to(site_root.resolve()) or not target.exists():
            broken.append(f"{html_rel} -> {ref}")
    return broken


class TestProjectSiteBuilder(unittest.TestCase):
    """Comprehensive pure-stdlib tests for Quiet UI v9.8.0 project-site shell."""

    def test_load_site_config_validates_manifests_and_rejects_unsafe_inputs(self) -> None:
        quiet_cfg = load_site_config(QUIET_CFG_PATH)
        starter_cfg = load_site_config(STARTER_CFG_PATH)
        self.assertEqual(quiet_cfg["project"]["slug"], "quiet-ui-skills")
        self.assertTrue(quiet_cfg["routes"]["demo"]["enabled"])
        self.assertEqual(starter_cfg["project"]["slug"], "workbench-starter")
        self.assertFalse(starter_cfg["routes"]["demo"]["enabled"])

        bad_cases: list[tuple[str, list[str], str]] = [
            ("rfc1918_192", ["project", "tagline"], "Host 192." + "168.1.10 endpoint"),
            ("rfc1918_10", ["project", "tagline"], "Host 10.0.0.5 endpoint"),
            ("loopback_127", ["project", "site_url"], "http://127.0.0.1:8080/"),
            ("private_lan", ["project", "site_url"], "https://nas.lan/docs/"),
            ("private_local", ["project", "site_url"], "https://printer.local/"),
            ("home_linux", ["project", "tagline"], "Loaded from /home/alice/repo"),
            ("home_macos", ["project", "tagline"], "Loaded from /Users/bob/repo"),
            ("token_brain", ["project", "tagline"], "Artifact brain:0c9baee0"),
            ("token_deadbolt", ["project", "tagline"], "Internal deadbolt token"),
            ("unsafe_js_url", ["project", "repo_url"], "javascript:alert(1)"),
            ("unsafe_proto_url", ["project", "site_url"], "//evil.example.com/site"),
            ("backslash_proto", ["project", "site_url"], "\\\\evil.example"),
            ("slash_backslash", ["project", "repo_url"], "/\\evil.example"),
            ("ctrl_proto", ["project", "site_url"], "\x01//evil.example"),
            ("traversal_src", ["docs_reader", "sources", "0", "path"], "../secret.md"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "oaw-site.json"
            for name, path_keys, bad_val in bad_cases:
                with self.subTest(case=name):
                    mutated = copy.deepcopy(_minimal_raw_config())
                    cur: Any = mutated
                    for key in path_keys[:-1]:
                        cur = cur[int(key)] if isinstance(cur, list) else cur[key]
                    last = path_keys[-1]
                    cur[int(last) if isinstance(cur, list) else last] = bad_val
                    cfg_path.write_text(json.dumps(mutated), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_site_config(cfg_path)

    def test_compile_markdown_docs_and_compile_diagram_spec(self) -> None:
        direct_svg = compile_diagram_spec(PIPELINE_SPEC)
        _assert_svg_clean(self, direct_svg)

        md_body = (
            "# Alpha Guide ✨\n\n"
            "Summary with [bad](javascript:alert(1)), [proto](//evil.example), "
            "[bs](\\\\evil.example), [sb](/\\evil.example), [ctrl](\x01//evil.example), "
            "see [Beta](beta.md) and [Beta Setup](beta.md#setup), "
            "and raw <script>alert(1)</script> plus &#10024;.\n\n"
            "## Spec Table 🚀\n\n"
            "| Metric | Value |\n"
            "| :--- | ---: |\n"
            "| Latency | 12 ms |\n\n"
            "## Diagram ⚡\n\n"
            f"```quiet-evidence\n{json.dumps(PIPELINE_SPEC)}\n```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "docs").mkdir()
            (base / "docs" / "alpha.md").write_text(md_body, encoding="utf-8")
            (base / "docs" / "beta.md").write_text("# Beta\n\n## Setup\n\nReady.\n", encoding="utf-8")
            out = compile_markdown_docs(
                [
                    {"id": "alpha", "path": "docs/alpha.md", "title": "Alpha Guide", "category": "Ref"},
                    {"id": "beta", "path": "docs/beta.md", "title": "Beta", "category": "Ref"},
                ],
                base,
            )

        html_out = out["sections_html"]
        self.assertEqual(len(out["toc"]), 2)
        self.assertEqual([h["level"] for h in out["toc"][0]["headings"]], [1, 2, 2])
        self.assertGreaterEqual(len(out["search_index"]), 4)
        self.assertIn('<table class="booktabs">', html_out)
        self.assertRegex(html_out, r'<div class="oaw-compiled-diagram">.*?<svg\b')
        self.assertIn('href="#doc-beta" data-doc-jump="doc-beta"', html_out)
        self.assertIn('href="#beta-setup" data-doc-jump="beta-setup"', html_out)
        _assert_svg_clean(self, html_out)
        self.assertNotIn("javascript:", html_out.lower())
        self.assertNotIn("evil.example", html_out)
        self.assertNotRegex(html_out, r"<script\b")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html_out)

    def test_render_social_svg(self) -> None:
        for cfg_path in (QUIET_CFG_PATH, STARTER_CFG_PATH):
            cfg = load_site_config(cfg_path)
            svg = render_social_svg(cfg)
            self.assertTrue(svg.endswith("\n"))
            self.assertIn("WORKBENCH", svg)
            root = ET.fromstring(svg)
            self.assertEqual(root.attrib.get("width"), "1280")
            self.assertEqual(root.attrib.get("height"), "640")
            _assert_svg_clean(self, svg)

        route_cfg = _minimal_raw_config()
        route_cfg["routes"] = {
            "overview": {"href": "index.html", "label": "Portal Home"},
            "demo": {"href": "demo/index.html", "label": "Live Sandbox", "enabled": True},
            "docs": {"href": "docs/index.html", "label": "Reference Manual"},
        }
        route_svg = render_social_svg(route_cfg)
        self.assertTrue(route_svg.endswith("\n"))
        for lbl in ("Portal Home", "Live Sandbox", "Reference Manual"):
            self.assertIn(lbl, route_svg)
        for default_lbl in ("quiet-evidence", "quiet-bridge"):
            self.assertNotIn(default_lbl, route_svg)

        xss_cfg = _minimal_raw_config()
        xss_cfg["social_preview"].update({
            "eyebrow": "PORTAL & <DEV>",
            "title": '<script>alert("xss")</script> & More',
            "subtitle": "Escapes 'single' & \"double\" <tags>",
            "pills": ["A&B", "<Tag>", "Clean", "MIT"],
        })
        xss_svg = render_social_svg(xss_cfg)
        self.assertTrue(xss_svg.endswith("\n"))
        root = ET.fromstring(xss_svg)
        self.assertEqual(root.attrib.get("width"), "1280")
        self.assertEqual(root.attrib.get("height"), "640")
        self.assertNotRegex(xss_svg, r"<script\b")
        self.assertIn("&lt;script&gt;", xss_svg)
        _assert_svg_clean(self, xss_svg)

    @unittest.skipUnless(HAS_PIL, "Pillow not installed")
    def test_render_social_png_when_pillow_available(self) -> None:
        cfg = load_site_config(STARTER_CFG_PATH)
        with tempfile.TemporaryDirectory() as tmp:
            png_path = Path(tmp) / "assets" / "social-preview.png"
            written = render_social_png(cfg, png_path)
            self.assertEqual(written, png_path)
            data = png_path.read_bytes()
            self.assertLessEqual(len(data), 250 * 1024)
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(data[12:16], b"IHDR")
            self.assertEqual(struct.unpack(">II", data[16:24]), (1280, 640))

    def test_cli_build_starter_unbundled_and_bundled(self) -> None:
        for bundle in (False, True):
            with self.subTest(bundle=bundle), tempfile.TemporaryDirectory() as tmp:
                out_dir = Path(tmp)
                cmd = [sys.executable, "-B", str(BUILD_CLI), "--config", str(STARTER_CFG_PATH), "--out", str(out_dir)]
                if bundle:
                    cmd.append("--bundle")
                res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

                for req_rel in ("index.html", "docs/index.html", "search-index.json", "assets/site-search.js"):
                    self.assertTrue((out_dir / req_rel).is_file(), f"Missing {req_rel}")
                self.assertTrue(list((out_dir / "assets").glob("*.svg")), "Expected assets/*.svg output")
                if bundle:
                    self.assertFalse((out_dir / "styles").exists())
                else:
                    self.assertTrue((out_dir / "styles" / "quiet-ui-tokens.css").is_file())
                    self.assertIn("@layer tokens {", (out_dir / "styles" / "tokens.layered.css").read_text(encoding="utf-8"))
                    self.assertTrue((out_dir / "styles" / "overrides.css").is_file())

                self._assert_starter_html_contracts(out_dir, bundle=bundle)

    def _assert_topbar_contract(self, html_txt: str, *, search_idx: str) -> None:
        markup = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", html_txt, flags=re.S | re.I)
        for tok in ('id="oaw-projects-popover"', 'id="oaw-route-btn"', 'id="oaw-route-menu"', 'id="oaw-search-btn"',
                    f'data-search-index="{search_idx}"', 'id="oaw-pillar-btn"', 'id="oaw-user-btn"'):
            self.assertIn(tok, markup)
        self.assertRegex(markup, re.compile(r'id="oaw-projects-popover"[^>]*>.*?<ul class="oaw-pop-list">\s*<li class="oaw-pop-row-sep">.*?All Projects', re.S))
        self.assertRegex(markup, re.compile(r'href="https://research\.oaworkbench\.org/"[^>]*>.*?Research.*?oaw-pop-badge--preview[^>]*>Preview<', re.S))
        for stale in ("oaw-pop-stage1-back", "oaw-mobile-subnav", "is-soon"):
            self.assertNotIn(stale, markup)

    def _assert_starter_html_contracts(self, out_dir: Path, *, bundle: bool) -> None:
        audit = subprocess.run([sys.executable, "-B", str(AUDITOR_CLI), str(out_dir)], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)

        for asset in out_dir.rglob("*"):
            if asset.is_file() and asset.suffix in {".html", ".css"}:
                self.assertNotIn("!important", asset.read_text(encoding="utf-8").lower())

        for rel in ("index.html", "docs/index.html"):
            txt = (out_dir / rel).read_text(encoding="utf-8")
            self.assertNotIn("SPDX-License-Identifier: Apache-2.0", txt)
            for chrome in re.findall(r"<(header|nav|footer)\b[^>]*>.*?</\1>", txt, flags=re.S | re.I):
                self.assertNotIn("quiet ui", chrome.lower())
            self.assertNotIn('data-oaw-route-link="demo"', txt)
            self.assertNotIn("demo/index.html", txt)
            self._assert_topbar_contract(txt, search_idx=("./search-index.json" if rel == "index.html" else "../search-index.json"))
            self.assertTrue("oaw_theme_v99" in txt and "quiet-ui-site-theme" in txt)
            if rel == "index.html":
                self.assertNotIn("oaw-docs-subbar", txt)
            if bundle:
                self.assertIn('<style id="oaw-site-styles">', txt)
                self.assertNotIn('rel="stylesheet"', txt)
            else:
                self.assertLess(txt.index("styles/tokens.layered.css"), txt.index("styles/overrides.css"))
            self.assertEqual(_find_broken_relative_links(out_dir, rel), [])

        docs_txt = (out_dir / "docs" / "index.html").read_text(encoding="utf-8")
        idx_m = re.search(r'<script type="application/json" id="oaw-docs-search-index">(.*?)</script>', docs_txt, flags=re.S)
        self.assertIsNotNone(idx_m)
        parsed_idx = json.loads(idx_m.group(1))
        self.assertIsInstance(parsed_idx, list)
        self.assertGreater(len(parsed_idx), 0)
        self.assertIn('<dialog id="oaw-docs-toc-dialog"', docs_txt)
        self.assertRegex(docs_txt, re.compile(r'id="oaw-docs-subbar"[^>]*>.*?id="oaw-docs-toc-trigger"', re.S))
        searchbar_m = re.search(r'class="oaw-docs-searchbar"[^>]*>.*?</div>', docs_txt, flags=re.S)
        self.assertIsNotNone(searchbar_m)
        self.assertNotIn("oaw-docs-toc-trigger", searchbar_m.group(0))
        self.assertRegex(docs_txt, r'id="oaw-docs-empty"[^>]*class="[^"]*\bva-empty-state\b[^"]*"[^>]*data-kind="filtered"')

    def test_render_overview_false_and_demo_return_bar(self) -> None:
        quiet_cfg = load_site_config(QUIET_CFG_PATH)
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            emitted = build_project_site(quiet_cfg, out_dir, bundle=False, render_overview=False, render_docs=True)
            self.assertFalse((out_dir / "index.html").exists())
            self.assertFalse((out_dir / "search-index.json").exists())
            self.assertTrue((out_dir / "docs" / "index.html").is_file())
            self.assertEqual(list(emitted.keys()), [out_dir / "docs" / "index.html"])

        bar_html = render_demo_return_bar(quiet_cfg)
        self._assert_topbar_contract(bar_html, search_idx="../search-index.json")
        for tok in ("va-demo-site-strip", "Antigravity Nexus", "Quiet User Interface Skills", "@FrankXLT"):
            self.assertIn(tok, bar_html)
        for absent in ("oaw-theme-select", "oaw-docs-subbar"):
            self.assertNotIn(absent, bar_html)
        for route in ("overview", "demo", "docs"):
            self.assertIn(f'data-oaw-route-link="{route}"', bar_html)
        self.assertRegex(bar_html, r'data-oaw-route-link="demo"[^>]*aria-current="page"')

    def test_svg_sanitization_and_traversal_guards(self) -> None:
        dirty_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 40" onload="alert(1)">'
            '<script>alert(1)</script><foreignObject><b>bad</b></foreignObject>'
            '<a href="javascript:alert(1)"><set attributeName="href" to="javascript:alert(1)"/>'
            '<animate attributeName="xlink:href" values="javascript:alert(1)"/><path d="M0 0L10 10"/></a></svg>'
        )
        cleaned = _sanitize_svg_html(dirty_svg)
        for bad in ("<script", "<foreignobject", "<set", "<animate", "onload", "javascript:"):
            self.assertNotIn(bad, cleaned.lower())
        self.assertIn('<path fill="none" d="M0 0L10 10"/>', cleaned)

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "docs").mkdir()
            (base / "docs" / "guide.md").write_text("# Guide\n\nOk.\n", encoding="utf-8")
            (base / "diag.svg").write_text(dirty_svg, encoding="utf-8")
            cfg = _minimal_raw_config()
            cfg["base_dir"] = str(base)
            cfg["overview"] = {"architecture_diagrams": [{"id": "inline", "svg": dirty_svg}, "diag.svg"]}
            out_dir = base / "dist"
            build_project_site(cfg, out_dir, bundle=True)
            ov_html = (out_dir / "index.html").read_text(encoding="utf-8")
            arch_m = re.search(r'<section aria-labelledby="oaw-arch-hdr">.*?</section>', ov_html, flags=re.S)
            self.assertIsNotNone(arch_m)
            arch_html = arch_m.group(0).lower()
            self.assertIn("<svg", arch_html)
            for bad in ("<script", "<foreignobject", "<set", "<animate", "onload", "javascript:", "alert(1)"):
                self.assertNotIn(bad, arch_html)

            for bad_path in ("../secret.md", "../secret.svg", "/etc/passwd"):
                with self.subTest(bad_path=bad_path):
                    with self.assertRaises(ValueError):
                        compile_markdown_docs([{"id": "x", "path": bad_path}], base)
                    bad_cfg = _minimal_raw_config()
                    bad_cfg["base_dir"] = str(base)
                    bad_cfg["docs_reader"]["sources"] = [{"id": "x", "path": bad_path}]
                    with self.assertRaises(ValueError):
                        build_project_site(bad_cfg, base / "bad_docs")
                    diag_cfg = _minimal_raw_config()
                    diag_cfg["base_dir"] = str(base)
                    diag_cfg["overview"] = {"architecture_diagrams": [bad_path]}
                    with self.assertRaises(ValueError):
                        build_project_site(diag_cfg, base / "bad_diag")

    def test_url_guards_demo_wrapper_redirect_and_immutability(self) -> None:
        for bad_url in ("\\\\evil.example", "/\\evil.example", "\x01//evil.example", "javascript:alert(1)", "foo:bar"):
            self.assertEqual(safe_href(bad_url), "")
        self.assertEqual(to_page_href("../index.html", "../"), "../../index.html")
        self.assertEqual(to_page_href("./index.html", "../"), "../index.html")
        rel_cfg = _minimal_raw_config()
        rel_cfg["hub"] = {"hub_url": "projects.html"}
        self.assertIn('href="../projects.html"', render_chrome_top(rel_cfg, current="docs", rel_prefix="../"))

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "docs").mkdir()
            (base / "docs" / "guide.md").write_text("# Guide\n\nBody.\n", encoding="utf-8")
            (base / "ext_demo.html").write_text(
                "<!DOCTYPE html><html><head><title>D</title></head><body><main>App</main></body></html>",
                encoding="utf-8",
            )
            cfg = _minimal_raw_config()
            cfg["base_dir"] = str(base)
            cfg["routes"]["demo"] = {"href": "demo/index.html", "label": "Demo", "enabled": True, "legacy_query_keys": ["mode"]}
            cfg["demo_wrapper"] = {"enabled": True, "entry_path": "ext_demo.html"}
            out_dir = base / "dist"
            emitted = build_project_site(cfg, out_dir, bundle=False, overrides_css="/* custom */")
            self.assertIn(out_dir / "demo" / "index.html", emitted)
            demo_html = (out_dir / "demo" / "index.html").read_text(encoding="utf-8")
            self.assertIn(".va-demo-site-strip", demo_html)
            self.assertRegex(demo_html, r'class="[^"]*\bva-demo-site-strip\b')
            for tok in ("oaw-theme-opt", 'id="oaw-search-btn"', 'id="oaw-route-btn"', "assets/site-search.js", "<main>App</main>"):
                self.assertIn(tok, demo_html)
            self.assertNotIn("oaw-docs-subbar", demo_html)
            ov_html = (out_dir / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("oaw-theme-select", ov_html)
            self.assertNotIn("oaw-docs-subbar", ov_html)
            for tok in ('id="oaw-pillar-btn"', 'id="oaw-user-btn"', 'id="oaw-search-btn"', 'id="oaw-route-btn"', "oaw_theme_v99", "quiet-ui-site-theme", "window.location.replace", "mode"):
                self.assertIn(tok, ov_html)
            self.assertRegex(ov_html, r"q\.get\(['\"]mode['\"]\).*toLowerCase\(\)===['\"]overview['\"]")
            self.assertLess(ov_html.index("styles/tokens.layered.css"), ov_html.index("styles/overrides.css"))
            self.assertNotIn("SPDX-License-Identifier: Apache-2.0", ov_html)
            self.assertNotIn("SPDX-License-Identifier: Apache-2.0", (out_dir / "docs" / "index.html").read_text(encoding="utf-8"))
            self.assertIn("details.qe-spec-drawer:not([open])", ov_html)
            self.assertIn(".qe-spec-pre", ov_html)

            subprocess.run(["git", "init", "-q"], cwd=base, check=True)
            starter_dir = base / "customizations" / "project-site-starter"
            starter_dir.mkdir(parents=True)
            (starter_dir / "oaw-site.json").write_text("{}", encoding="utf-8")
            breaches = check_immutability(base)
            self.assertTrue(any("IMMUTABILITY_BREACH" in b and "customizations/project-site-starter/oaw-site.json" in b for b in breaches))


if __name__ == "__main__":
    unittest.main()
