#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.7.0 Wave 3.5 tests: three-layer rule, token, negative-CDP & live Studio gates."""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR_SCRIPTS = REPO_ROOT / "skills" / "quiet-ui" / "scripts"
TESTS_DIR = Path(__file__).resolve().parent
for _p in (str(AUDITOR_SCRIPTS), str(TESTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from audit_editorial_print import probe_print_flow_collision  # noqa: E402
from audit_quiet_checks import CDP_AUDIT_JS, audit_cdp_urls  # noqa: E402
from audit_wave35_probes import CDP_WAVE35_PROBES_JS, probe_print_safe_margins  # noqa: E402
from cdp_gates import create_headless_driver, select_view, set_viewport, start_http_server  # noqa: E402

WAVE35_CODES = (
    "[SVG_LABEL_STROKE_COLLISION]",
    "[DISABLED_CONTROL_LOW_CONTRAST]",
    "[PARAM_KEY_MIDWORD_WRAP]",
    "[PRINT_EDGE_CLIP]",
)


def _cdp_ready() -> tuple[bool, str]:
    if os.environ.get("QUIET_SKIP_CDP") == "1":
        return False, "QUIET_SKIP_CDP=1"
    try:
        drv = create_headless_driver()
        drv.quit()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _set_all_themes(driver: Any, theme: str) -> None:
    driver.execute_script(
        "document.documentElement.setAttribute('data-theme', arguments[0]);"
        "const fr = document.getElementById('va-stage-portal');"
        "if (fr && fr.contentDocument) fr.contentDocument.documentElement.setAttribute('data-theme', arguments[0]);",
        theme,
    )
    time.sleep(0.24)


def _run_iframe_wave35_js(driver: Any, mode: str) -> list[Any]:
    script = (
        CDP_WAVE35_PROBES_JS
        + "\nconst errs=[];function pushErr(m){errs.push(m);}\n"
        + "const isVis=(el,cs)=>cs.display!=='none'&&cs.visibility!=='hidden'&&parseFloat(cs.opacity||'1')>0.01;\n"
        + "const fr=document.getElementById('va-stage-portal'), d=fr.contentDocument, w=fr.contentWindow;\n"
        + "const vw=w.innerWidth||window.innerWidth, fn=arguments[0];\n"
        + "if(fn==='disabled') auditDisabledContrastW35(d,w,'',vw);\n"
        + "else if(fn==='param') auditParamKeysTabletW35(d,w,'',vw);\n"
        + "else if(fn==='svg') auditSvgLabelClearanceW35(d,w,'',vw);\n"
        + "return errs;"
    )
    return list(driver.execute_script(script, mode) or ())


class TestWave35ThreeLayerParity(unittest.TestCase):
    """Verify Wave 3.5 governing docs, installer parity, and 4-theme disabled tokens."""

    def test_layer1_docs_and_installer_include_wave35(self) -> None:
        doc_paths = (
            REPO_ROOT / "skills" / "quiet-ui" / "SKILL.md",
            REPO_ROOT / "docs" / "WORKFLOWS.md",
            REPO_ROOT / "llms.txt",
        )
        for p in doc_paths:
            txt = p.read_text(encoding="utf-8")
            for code in WAVE35_CODES:
                self.assertIn(code, txt, f"{p.name} missing Wave 3.5 code {code}")

        install_txt = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("audit_wave35_probes.py", install_txt)
        self.assertIn("audit_editorial_print.py", install_txt)

        skill_ev = (REPO_ROOT / "skills" / "quiet-evidence" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("6px", skill_ev)

    def test_layer2_disabled_tokens_exist_across_all_themes(self) -> None:
        targets = (
            (REPO_ROOT / "tokens" / "quiet-ui-tokens.css", 5),
            (REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.css", 5),
            (REPO_ROOT / "skills" / "quiet-evidence" / "scripts" / "compile_evidence.py", 4),
        )
        for p, min_cnt in targets:
            txt = p.read_text(encoding="utf-8")
            for tok in ("--disabled-bg", "--disabled-fg", "--disabled-border"):
                self.assertGreaterEqual(txt.count(tok), min_cnt, f"{p.name} missing all-theme {tok}")


class TestWave35CDPGates(unittest.TestCase):
    """Run negative CDP violation fixtures plus live Showcase Wave 3.5 verification."""

    def _require_or_skip_cdp(self) -> None:
        ok, reason = _cdp_ready()
        if not ok:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                self.fail(f"QUIET_REQUIRE_CDP=1 set but Chrome unavailable: {reason}")
            self.skipTest(f"Wave 3.5 CDP gates skipped ({reason})")

    def test_negative_fixtures_trigger_all_four_wave35_probes(self) -> None:
        self._require_or_skip_cdp()
        fixtures = {
            "bad_svg.html": (
                '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>body{font-size:14px;background:#fff}</style></head>'
                '<body><main><svg viewBox="0 0 420 180" width="420" height="180" role="img" aria-label="Bad">'
                '<line x1="20" y1="90" x2="400" y2="90" stroke="#dc2626" stroke-width="2.2"/>'
                '<text x="210" y="93" text-anchor="middle" font-size="12" fill="#0f172a">Direct Strike</text></svg></main></body></html>'
            ),
            "bad_disabled.html": (
                '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>'
                'body{font-size:14px;background:#1e293b;color:#f8fafc}'
                'button:disabled{background:#1e293b;color:#273347;border:1px dashed #334155;opacity:1;font-size:14px;padding:8px 14px}'
                '</style></head><body><main><button type="button" disabled>Confirm Execute</button></main></body></html>'
            ),
            "bad_param_wrap.html": (
                '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>'
                'body{font-size:14px;background:#fff;margin:0}table{width:100%;table-layout:fixed}'
                'td code{word-break:break-all;overflow-wrap:anywhere}'
                '</style></head><body><main><table><thead><tr><th style="width:92px">Key</th><th>Description</th></tr></thead>'
                '<tbody><tr><td><code>tls.minimum_protocol_version_enforce</code></td><td>Enforced across edges.</td></tr></tbody>'
                '</table></main></body></html>'
            ),
            "bad_print_edge.html": (
                '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>'
                '@media print{@page{margin:0}html,body,main{margin:0;padding:0;background:#fff;color:#000}}'
                'body{font-size:14px;background:#fff;color:#0f172a}'
                '</style></head><body><main><p>Full-bleed paragraph invading the 12px print margin edge without horizontal safe padding.</p>'
                '</main></body></html>'
            ),
        }
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            for name, html in fixtures.items():
                (tdir / name).write_text(html, encoding="utf-8")
            srv, port = start_http_server(tdir)
            try:
                urls = [f"http://127.0.0.1:{port}/{name}" for name in fixtures]
                errs = audit_cdp_urls(urls, allow_showcase_chrome=False)
            finally:
                srv.shutdown()
                srv.server_close()

        joined = "\n".join(errs)
        for code in WAVE35_CODES:
            self.assertIn(code, joined, f"Expected negative probe to fire {code}; got:\n{joined}")

    def test_live_studio_views_pass_all_wave35_invariants(self) -> None:
        self._require_or_skip_cdp()
        srv, port = start_http_server(REPO_ROOT)
        url = f"http://127.0.0.1:{port}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        try:
            driver.get(url)
            time.sleep(0.35)

            for slug, btn_sel in (
                ("v18-home-assistant-companion-console", "#v18-lock-exec"),
                ("v23-semantic-config-diff-review", "[data-v23-confirm]"),
            ):
                select_view(driver, slug)
                set_viewport(driver, 1440, 900)
                time.sleep(0.18)
                has_dis = driver.execute_script(
                    "const d=document.getElementById('va-stage-portal').contentDocument;return !!d.querySelector(arguments[0]+':disabled');",
                    btn_sel,
                )
                self.assertTrue(has_dis, f"{slug} missing initial locked disabled button {btn_sel}")
                for th in ("white", "paper", "dark-paper", "dark"):
                    _set_all_themes(driver, th)
                    errs = _run_iframe_wave35_js(driver, "disabled")
                    self.assertEqual(errs, [], f"{slug} theme={th} disabled contrast failed: {errs}")
                _set_all_themes(driver, "white")

            def _set_stage_size(w: int, h: int) -> None:
                set_viewport(driver, max(w, 920), h)
                driver.execute_script(
                    "const a=window.QuietStudioPortalV9;if(a){a.state.vp=arguments[0]+'x'+arguments[1];a.state.presetLocked=true;a.applyState(false);}",
                    w, h,
                )
                time.sleep(0.28)

            select_view(driver, "v23-semantic-config-diff-review")
            for w, h in ((820, 1080), (900, 1050)):
                _set_stage_size(w, h)
                self.assertEqual(_run_iframe_wave35_js(driver, "param"), [], f"v23 @{w}px param key wrapped")

            for slug in ("v25-subsea-corridor-and-link-margin", "v26-constrained-trade-space-calculator"):
                select_view(driver, slug)
                for w, h in ((390, 844), (900, 1050), (1440, 900)):
                    _set_stage_size(w, h)
                    errs = _run_iframe_wave35_js(driver, "svg")
                    self.assertEqual(errs, [], f"{slug} @{w}px SVG collision: {errs}")

            for slug in ("v22-reading-and-mobility-brief", "v01-icu-bedside-terminal"):
                select_view(driver, slug)
                time.sleep(0.18)
                errs = probe_print_flow_collision(driver, f"{url}#{slug}", "white")
                self.assertEqual(errs, [], f"{slug} print flow/edge clip failed: {errs}")

            set_viewport(driver, 1440, 900)
            payload = {"allowShowcase": False, "blocklistSelectors": [], "blocklistCopy": []}
            doc_errs = list(driver.execute_script(CDP_AUDIT_JS, payload) or ())
            self.assertEqual([e for e in doc_errs if "[SVG_LABEL_STROKE_COLLISION]" in e], [])
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()

    def test_standalone_compiled_editorial_clears_print_safe_margins(self) -> None:
        self._require_or_skip_cdp()
        ev_scripts = str(REPO_ROOT / "skills" / "quiet-evidence" / "scripts")
        if ev_scripts not in sys.path:
            sys.path.insert(0, ev_scripts)
        from compile_evidence import compile_spec  # noqa: E402
        import json

        specs = json.loads((REPO_ROOT / "docs/bench/specimens/m4_civic_research.json").read_text("utf-8"))
        doc_html = compile_spec(specs[0], rigor="L1", medium="m2", theme="white", chrome="editorial", standalone=True)
        with tempfile.TemporaryDirectory() as tmp:
            ed_p = Path(tmp) / "standalone_ed.html"
            ed_p.write_text(doc_html, encoding="utf-8")
            srv, port = start_http_server(Path(tmp))
            try:
                errs = audit_cdp_urls([f"http://127.0.0.1:{port}/standalone_ed.html"], allow_showcase_chrome=False)
            finally:
                srv.shutdown()
                srv.server_close()
        self.assertEqual([e for e in errs if "[PRINT_EDGE_CLIP]" in e or "[DISABLED_CONTROL_LOW_CONTRAST]" in e], [], errs)

    def test_project_site_overview_print_safe_margins(self) -> None:
        self._require_or_skip_cdp()
        driver = create_headless_driver()
        try:
            for label, site_dir in (
                ("docs", REPO_ROOT / "docs"),
                ("starter", REPO_ROOT / "customizations" / "project-site-starter" / "site"),
            ):
                srv, port = start_http_server(site_dir)
                url = f"http://127.0.0.1:{port}/"
                try:
                    driver.get(url)
                    time.sleep(0.25)
                    driver.execute_cdp_cmd(
                        "Emulation.setDeviceMetricsOverride",
                        {"width": 820, "height": 1100, "deviceScaleFactor": 1, "mobile": False},
                    )
                    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
                    time.sleep(0.14)
                    self.assertEqual(probe_print_safe_margins(driver, url, "white"), [], f"{label} closed drawer print clip")
                    driver.execute_script("document.querySelectorAll('details.qe-spec-drawer').forEach(d => { d.open = true; });")
                    time.sleep(0.08)
                    self.assertEqual(probe_print_safe_margins(driver, url, "white"), [], f"{label} open drawer print clip")
                finally:
                    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
                    driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
                    srv.shutdown()
                    srv.server_close()
        finally:
            driver.quit()


if __name__ == "__main__":
    unittest.main()
