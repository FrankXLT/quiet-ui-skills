#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.2.2 Round 2 verification: Brownfield docs, PeriodStepper/RailTree, heatmap trimming, and CDP gates."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_html.py"
CHECKS_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_checks.py"
PROBES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_cdp_probes.py"
STATIC_RULES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_static_rules.py"
UX_DRIFT_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_ux_and_drift.py"
WORKBENCH_PROBES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_workbench_probes.py"
BUNDLE_CSS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.css"
BUNDLE_JS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.js"
BINNING_JS = REPO_ROOT / "src" / "js" / "quiet-time-binning.js"
ECHARTS_DEFAULTS_JS = REPO_ROOT / "src" / "js" / "echarts-layout-defaults.js"
STEPPER_JS = REPO_ROOT / "src" / "js" / "quiet-period-stepper.js"


class TestV922Round2(unittest.TestCase):
    """Verify Round 2 brownfield contracts, shipped primitives, and live Chrome CDP probes."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.auditor = self.tmp_dir / "audit_quiet_html.py"
        for src in (AUDITOR_SRC, CHECKS_SRC, PROBES_SRC, STATIC_RULES_SRC, UX_DRIFT_SRC, WORKBENCH_PROBES_SRC):
            shutil.copy2(src, self.tmp_dir / src.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run_auditor(self, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(self.auditor), str(target), *extra],
            cwd=self.tmp_dir,
            capture_output=True,
            text=True,
        )

    def _require_cdp(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise
            self.skipTest("selenium not installed")

    def test_round2_docs_and_bundle_exports(self) -> None:
        bf_doc = REPO_ROOT / "skills" / "quiet-ui" / "foundation" / "brownfield-retrofit-and-migration.md"
        self.assertTrue(bf_doc.exists(), "Missing brownfield-retrofit-and-migration.md")
        bf_txt = bf_doc.read_text("utf-8")
        self.assertTrue(120 <= len(bf_txt.splitlines()) <= 450, f"Unexpected line count: {len(bf_txt.splitlines())}")
        for needle in (
            "KEEP | CONSOLIDATE | DEPRECATE",
            "?include_legacy=0",
            "Monolith-to-Zoom",
            "Side-by-Side Strangler",
            "layer(legacy)",
            "Sign-Off Gate",
        ):
            self.assertIn(needle, bf_txt)

        skill_txt = (REPO_ROOT / "skills" / "quiet-ui" / "SKILL.md").read_text("utf-8")
        for needle in ("**Project Mode**", "Greenfield", "Brownfield Retrofit", "Capability Parity Ledger", "brownfield-retrofit-and-migration.md"):
            self.assertIn(needle, skill_txt)

        wf_txt = (REPO_ROOT / "docs" / "WORKFLOWS.md").read_text("utf-8")
        self.assertIn("Workflow G", wf_txt)
        self.assertIn("Brownfield Retrofit", wf_txt)

        mb_txt = (REPO_ROOT / "skills" / "quiet-bridge" / "protocols" / "adversarial-murder-board.md").read_text("utf-8")
        for tok in ("BF-1", "BF-2", "BF-3", "BF-4", "TRG-14"):
            self.assertIn(tok, mb_txt)

        css = BUNDLE_CSS.read_text("utf-8")
        js = BUNDLE_JS.read_text("utf-8")
        for sel in (
            '.va-side-rail[data-mode="overlay"]',
            ".va-rail-footer",
            ".va-period-stepper",
            ".va-preset-popover",
            ".va-scope-chip",
            ".va-tree-row",
        ):
            self.assertIn(sel, css, f"Missing Round 2 CSS in bundle: {sel}")
        for sym in ("QuietPeriodStepper", "QuietRailTree", "trimTrailingFutureWeeks", "heatmapZeroCellStyle"):
            self.assertIn(sym, js, f"Missing Round 2 JS symbol in bundle: {sym}")

    def test_round2_node_helpers(self) -> None:
        node_bin = shutil.which("node")
        self.assertIsNotNone(node_bin, "Node.js required to verify Round 2 JS helpers")
        script = (
            "const fs = require('fs');\n"
            "const vm = require('vm');\n"
            f"const T = require({json.dumps(str(BINNING_JS))});\n"
            f"const D = require({json.dumps(str(ECHARTS_DEFAULTS_JS))});\n"
            f"const P = require({json.dumps(str(STEPPER_JS))});\n"
            "const weeks = ['2026-11-02', '2026-11-09', '2026-11-16', '2026-11-23'];\n"
            "const cells = [[0, 0, 5], [1, 0, 0], null, [null, 0, 1], [2, 0, 0], [3, 0, 0]];\n"
            "const keepPast = T.trimTrailingFutureWeeks(weeks, cells, { today: '2026-11-12' });\n"
            "if (keepPast.weeks.length !== 2 || keepPast.weeks[1] !== '2026-11-09' || keepPast.cells.length !== 2) {\n"
            "  throw new Error('trimTrailingFutureWeeks failed past retention: ' + JSON.stringify(keepPast));\n"
            "}\n"
            "const dropEmpty = T.trimTrailingFutureWeeks(weeks, cells, { today: '2026-11-12', dropEmptyTrailing: true });\n"
            "if (dropEmpty.weeks.length !== 1 || dropEmpty.weeks[0] !== '2026-11-02') {\n"
            "  throw new Error('trimTrailingFutureWeeks failed dropEmptyTrailing: ' + JSON.stringify(dropEmpty));\n"
            "}\n"
            "const darkZ = T.heatmapZeroCellStyle('#0f1624', '#1e293b');\n"
            "const lightZ = T.heatmapZeroCellStyle('#fff', '#cbd5e1');\n"
            "if (darkZ.fill === '#0f1624' || darkZ.borderColor.toLowerCase() === '#1e293b' || darkZ.labelColor !== '#F1F5F9' || lightZ.labelColor !== '#0F172A' || darkZ.minDeltaLuminance < 0.06 || lightZ.borderWidth !== 1) {\n"
            "  throw new Error('heatmapZeroCellStyle invalid: ' + JSON.stringify({ darkZ, lightZ }));\n"
            "}\n"
            "const optTop = { grid: { top: 8 }, xAxis: { type: 'category', data: ['Mon', 'Tue'] }, yAxis: { type: 'value', name: 'kW', nameLocation: 'end', nameGap: 4 }, series: [{ type: 'bar', data: [3, 5] }] };\n"
            "D.alignPlotGridFrames([optTop]);\n"
            "if (optTop.grid.top < 30 || optTop.yAxis.nameGap < 12) {\n"
            "  throw new Error('alignPlotGridFrames missed top Y axis name clearance: ' + JSON.stringify(optTop));\n"
            "}\n"
            "if (typeof P.QuietPeriodStepper.boot !== 'function' || typeof P.QuietRailTree.setRailOpen !== 'function') {\n"
            "  throw new Error('QuietPeriodStepper / QuietRailTree exports missing');\n"
            "}\n"
            "const stubDoc = { readyState: 'complete', addEventListener: () => {}, querySelectorAll: () => [], getElementById: () => null, documentElement: { dataset: {} } };\n"
            "const sb = { globalThis: null, module: { exports: {} }, document: stubDoc, setTimeout: () => 0, clearTimeout: () => {}, addEventListener: () => {} }; sb.globalThis = sb; sb.window = sb;\n"
            f"vm.runInNewContext(fs.readFileSync({json.dumps(str(BUNDLE_JS))}, 'utf8'), sb);\n"
            "if (!sb.QuietPeriodStepper || !sb.QuietRailTree || !sb.QuietEChartsDefaults.trimTrailingFutureWeeks) {\n"
            "  throw new Error('Bundle browser globals incomplete');\n"
            "}\n"
        )
        script_path = self.tmp_dir / "verify_r2_js.js"
        script_path.write_text(script, encoding="utf-8")
        subprocess.run([node_bin, str(script_path)], check=True)

    def test_round2_cdp_negative_and_positive_gates(self) -> None:
        self._require_cdp()
        head = (
            "<!DOCTYPE html><html lang='en' data-theme='white'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        )

        bad_overlay = self.tmp_dir / "bad_overlay.html"
        bad_overlay.write_text(
            head + "</head><body><main>"
            "<aside class='va-side-rail' data-mode='overlay' data-open='true' style='width:220px;height:300px;background:rgba(255,255,255,0.4)'>Nav</aside>"
            "<div class='va-preset-popover' data-open='true' style='width:200px;height:140px;background:transparent'>7d</div>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_ov = self._run_auditor(bad_overlay, "--cdp")
        self.assertNotEqual(r_ov.returncode, 0)
        self.assertIn("[TRANSPARENT_OVERLAY]", r_ov.stdout + r_ov.stderr)

        bad_clip = self.tmp_dir / "bad_top_clip.html"
        bad_clip.write_text(
            head + "</head><body><main>"
            "<svg width='240' height='90' viewBox='0 0 240 90' role='img' aria-label='Top Clip'>"
            "<text x='8' y='7' font-size='12'>Power (W)</text>"
            "<rect x='30' y='24' width='24' height='48' fill='#1d4ed8'/></svg>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_clip = self._run_auditor(bad_clip, "--cdp")
        self.assertNotEqual(r_clip.returncode, 0)
        self.assertIn("[AXIS_LABEL_CLIPPED]", r_clip.stdout + r_clip.stderr)

        bad_orphan = self.tmp_dir / "bad_orphan_legend.html"
        bad_orphan.write_text(
            head + "</head><body><main><div class='va-card'>"
            "<svg width='260' height='140' viewBox='0 0 260 140' role='img' aria-label='Unexplained Bars'>"
            "<rect x='30' y='16' width='210' height='98' fill='none' stroke='#cbd5e1'/>"
            "<rect x='50' y='44' width='22' height='70' fill='#1d4ed8'/>"
            "<rect x='84' y='34' width='22' height='80' fill='#dc2626'/>"
            "</svg></div></main></body></html>",
            encoding="utf-8",
        )
        r_orp = self._run_auditor(bad_orphan, "--cdp")
        self.assertNotEqual(r_orp.returncode, 0)
        self.assertIn("[ORPHAN_SERIES_LEGEND]", r_orp.stdout + r_orp.stderr)

        bad_sprawl = self.tmp_dir / "bad_toolbar_sprawl.html"
        bad_sprawl.write_text(
            head + "</head><body><header style='height:48px'><span>App</span></header><main>"
            "<div role='toolbar' aria-label='Period'>"
            + "".join(f"<button type='button'>{lbl}</button>" for lbl in ("1h", "6h", "24h", "7d", "30d", "90d", "1y"))
            + "</div></main></body></html>",
            encoding="utf-8",
        )
        r_sprawl = self._run_auditor(bad_sprawl, "--cdp")
        self.assertNotEqual(r_sprawl.returncode, 0)
        self.assertIn("[TOOLBAR_CONTROL_SPRAWL]", r_sprawl.stdout + r_sprawl.stderr)

        bad_sticky = self.tmp_dir / "bad_sticky_tier.html"
        bad_sticky.write_text(
            head + "<style>body{margin:0;height:1400px}</style></head><body>"
            "<header style='position:sticky;top:0;height:76px;background:#fff'><span>Hdr</span></header>"
            "<main><p>Content</p></main></body></html>",
            encoding="utf-8",
        )
        r_st = self._run_auditor(bad_sticky, "--cdp")
        self.assertNotEqual(r_st.returncode, 0)
        st_out = r_st.stdout + r_st.stderr
        self.assertIn("[STICKY_CHROME_BLOAT]", st_out)
        self.assertNotIn("@390px:", st_out)

        clean_page = self.tmp_dir / "clean_round2.html"
        clean_page.write_text(
            head + f"<link rel='icon' href='data:,'><style>{BUNDLE_CSS.read_text('utf-8')}</style></head><body>"
            "<header class='va-shell-topbar' style='height:48px;display:flex;align-items:center;gap:8px;padding:0 12px'>"
            "<button id='rail-btn' type='button' class='va-tb-btn' data-rail-trigger='main-rail' aria-controls='main-rail' aria-expanded='false'>Menu</button>"
            "<span class='va-studio-brand'>Ops Console</span></header>"
            "<aside id='main-rail' class='va-side-rail' data-mode='overlay' data-open='false'>"
            "<div class='va-tree-row'><button type='button' class='va-tree-caret' aria-expanded='false' aria-label='Expand Group'>+</button>"
            "<button type='button' class='va-tree-dest' data-target='overview'>Overview</button></div>"
            "<div class='va-tree-group' hidden><button type='button' class='va-tree-dest is-active' aria-current='page' data-target='node-a'>Node A</button></div>"
            "<div class='va-rail-footer'><span>v9.2.2</span></div></aside>"
            "<div class='va-drawer-backdrop' data-open='false'></div>"
            "<main class='va-stage'>"
            "<div role='toolbar' class='va-toolbar-joined' aria-label='Time window and actions'>"
            "<div class='va-period-stepper' data-period-stepper data-value='7d'>"
            "<div class='va-period-nav'>"
            "<button type='button' class='va-period-step' data-period-step='-1' aria-label='Previous'>Prev</button>"
            "<button type='button' class='va-period-trigger' aria-expanded='false'><span data-period-label>7 Days · Nov 15-21</span></button>"
            "<button type='button' class='va-period-step' data-period-step='1' aria-label='Next'>Next</button>"
            "</div>"
            "<div class='va-preset-popover' data-open='false' focusgroup='menu nomemory' hidden>"
            "<button type='button' class='va-preset-item' data-preset='24h' data-label='24 Hours' data-span='Nov 21' aria-checked='false'>24 Hours</button>"
            "<button type='button' class='va-preset-item' data-preset='7d' data-label='7 Days' data-span='Nov 15-21' aria-checked='true'>7 Days</button>"
            "<button type='button' class='va-preset-item' data-preset='30d' data-label='30 Days' data-span='Oct 23-Nov 21' aria-checked='false'>30 Days</button>"
            "</div></div>"
            "<button type='button' class='va-tb-btn'>Filter</button>"
            "<button type='button' class='va-tb-btn'>Export</button></div>"
            "<div class='va-card'>"
            "<div class='qe-legend-series'><span class='qe-legend-item'>Primary</span><span class='qe-legend-item'>Secondary</span></div>"
            "<svg width='260' height='140' viewBox='0 0 260 140' role='img' aria-label='Twin Series'>"
            "<rect x='30' y='24' width='210' height='94' fill='none' stroke='#cbd5e1'/>"
            "<text x='32' y='18' font-size='11'>Rate</text>"
            "<rect x='50' y='48' width='22' height='70' fill='#1d4ed8'/>"
            "<rect x='84' y='38' width='22' height='80' fill='#dc2626'/>"
            "</svg></div>"
            "<section class='qe-plot-wrap' data-axis-align='independent'>"
            "<svg width='260' height='120' viewBox='0 0 260 120' role='img' aria-label='Limit Line Bars'>"
            "<rect x='30' y='20' width='210' height='80' fill='none' stroke='#cbd5e1'/>"
            "<line x1='30' y1='60' x2='240' y2='60' stroke='#dc2626' stroke-width='2'/>"
            "<rect x='50' y='40' width='24' height='60' fill='#1d4ed8'/>"
            "</svg></section>"
            "<dialog open style='position:static;width:120px;height:40px;background:oklch(0.98 0 0)'>Ready</dialog>"
            "</main>"
            f"<script>{BUNDLE_JS.read_text('utf-8')}</script></body></html>",
            encoding="utf-8",
        )
        r_clean = self._run_auditor(clean_page, "--cdp")
        self.assertEqual(r_clean.returncode, 0, f"Unexpected CDP failure on clean Round 2 page:\n{r_clean.stdout}\n{r_clean.stderr}")

        self._verify_interactive_stepper_and_rail(clean_page)

    def _wait_rail_in_view(self, driver: object) -> None:
        for _ in range(30):
            time.sleep(0.03)
            settled = driver.execute_script(
                "const r = document.getElementById('main-rail');"
                "const c = r ? r.querySelector('.va-tree-caret') : null;"
                "const rr = r ? r.getBoundingClientRect() : null;"
                "const cr = c ? c.getBoundingClientRect() : null;"
                "return !!(rr && cr && Math.abs(rr.left) < 0.25 && cr.left >= 0 && cr.right <= window.innerWidth && cr.width >= 16);"
            )
            if settled:
                return

    def _verify_interactive_stepper_and_rail(self, page_path: Path) -> None:
        tests_dir = str(Path(__file__).resolve().parent)
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        from cdp_gates import create_headless_driver, set_viewport, start_http_server
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys

        srv, port = start_http_server(self.tmp_dir)
        driver = create_headless_driver()
        try:
            set_viewport(driver, 390, 844)
            driver.get(f"http://127.0.0.1:{port}/{page_path.name}")
            driver.execute_script(
                "window.__r2Events = [];"
                "document.addEventListener('quiet:tree-navigate', e => window.__r2Events.push(['tree', e.detail]));"
                "document.addEventListener('quiet:period-change', e => window.__r2Events.push(['period', e.detail]));"
            )
            driver.find_element(By.ID, "rail-btn").click()
            self._wait_rail_in_view(driver)
            rail_state = driver.execute_script(
                "const r = document.getElementById('main-rail');"
                "const sub = r.querySelector('.va-tree-group');"
                "return { open: r.dataset.open, bg: getComputedStyle(r).backgroundColor, subHidden: sub.hidden, w: Math.round(r.getBoundingClientRect().width) };"
            )
            self.assertEqual(rail_state["open"], "true")
            self.assertEqual(rail_state["w"], 390, f"Expected 100dvw overlay drawer at 390px, got {rail_state}")
            self.assertFalse(rail_state["subHidden"], "Active parent branch must auto-expand when rail opens")
            self.assertFalse(rail_state["bg"].endswith(", 0)") or rail_state["bg"] == "transparent")

            driver.find_element(By.CSS_SELECTOR, ".va-tree-caret").click()
            self.assertEqual(driver.find_element(By.ID, "main-rail").get_attribute("data-open"), "true")
            driver.find_element(By.CSS_SELECTOR, ".va-tree-dest[data-target='overview']").click()
            self.assertEqual(driver.find_element(By.ID, "main-rail").get_attribute("data-open"), "false")
            time.sleep(0.25)

            driver.execute_script("document.documentElement.dir = 'rtl';")
            driver.find_element(By.ID, "rail-btn").click()
            self._wait_rail_in_view(driver)
            rtl_x = driver.execute_script("return Math.round(document.getElementById('main-rail').getBoundingClientRect().left);")
            self.assertEqual(rtl_x, 0, f"RTL overlay drawer remained offscreen at x={rtl_x}")
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            self.assertEqual(driver.find_element(By.ID, "main-rail").get_attribute("data-open"), "false")
            driver.execute_script("document.documentElement.dir = 'ltr';")
            time.sleep(0.25)

            trig = driver.find_element(By.CSS_SELECTOR, ".va-period-trigger")
            trig.click()
            driver.execute_script("window.dispatchEvent(new Event('resize')); window.dispatchEvent(new Event('scroll'));")
            time.sleep(0.05)
            severe = [m for m in driver.get_log("browser") if str(m.get("level", "")).upper() == "SEVERE"]
            self.assertEqual(severe, [], f"Unexpected browser console errors on resize/scroll: {severe}")
            pop_bg = driver.execute_script(
                "const p = document.querySelector('.va-preset-popover');"
                "return { open: p.dataset.open, bg: getComputedStyle(p).backgroundColor };"
            )
            self.assertEqual(pop_bg["open"], "true")
            self.assertFalse(pop_bg["bg"].endswith(", 0)") or pop_bg["bg"] == "transparent")
            driver.find_element(By.CSS_SELECTOR, ".va-preset-item[data-preset='30d']").click()
            lbl = driver.find_element(By.CSS_SELECTOR, "[data-period-label]").text
            self.assertIn("30 Days", lbl)
            driver.find_element(By.CSS_SELECTOR, "[data-period-step='-1']").click()
            trig.click()
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            self.assertEqual(driver.find_element(By.CSS_SELECTOR, ".va-preset-popover").get_attribute("data-open"), "false")
            ev_names = driver.execute_script("return window.__r2Events.map(x => x[0]);")
            self.assertEqual(ev_names, ["tree", "period", "period"])

            set_viewport(driver, 1280, 900)
            time.sleep(0.08)
            driver.execute_script("document.getElementById('main-rail').removeAttribute('data-mode');")
            driver.find_element(By.ID, "rail-btn").click()
            bd_disp = driver.execute_script("return getComputedStyle(document.querySelector('.va-drawer-backdrop')).display;")
            self.assertEqual(bd_disp, "none", "Desktop >= 1080px inline rail must not display backdrop")
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
