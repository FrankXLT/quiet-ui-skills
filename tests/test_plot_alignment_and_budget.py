#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unit and CDP regression tests for Wave 2/3 plot axis spine registration, coarse-pointer rules, and 820px chrome budgets."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_html.py"
CHECKS_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_checks.py"
PROBES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_cdp_probes.py"
STATIC_RULES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_static_rules.py"
TOKENS_CSS = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
STAGE_CSS = REPO_ROOT / "src" / "css" / "01-stage-and-containers.css"
PILLS_CSS = REPO_ROOT / "src" / "css" / "03-pills-and-annunciators.css"
LAYERS_CSS = REPO_ROOT / "src" / "css" / "00-layers-and-reset.css"
ECHARTS_MIN = REPO_ROOT / "docs" / "assets" / "vendor" / "echarts.min.js"
SVG_LAYOUT_JS = REPO_ROOT / "src" / "js" / "quiet-svg-chart-layout.js"
ECHARTS_DEFAULTS_JS = REPO_ROOT / "src" / "js" / "echarts-layout-defaults.js"


class TestPlotAlignmentAndBudget(unittest.TestCase):
    """Verify 820px foldable viewports, [STICKY_CHROME_BLOAT], [PLOT_AXIS_MISALIGN], subgrid & coarse-pointer CSS."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.auditor = self.tmp_dir / "audit_quiet_html.py"
        for src in (AUDITOR_SRC, CHECKS_SRC, PROBES_SRC, STATIC_RULES_SRC):
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

    def _require_cdp(self) -> bool:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise
            self.skipTest("selenium not installed")
        return True

    def test_viewports_and_css_primitives(self) -> None:
        sys.path.insert(0, str(self.tmp_dir))
        from audit_static_rules import VIEWPORTS  # noqa: E402

        self.assertEqual(VIEWPORTS, ((390, 844), (820, 1080), (1440, 900)))
        stage_txt = STAGE_CSS.read_text("utf-8")
        tokens_txt = TOKENS_CSS.read_text("utf-8")
        for needle in (".va-inline-bar", ".va-inline-bar-fill", ".va-inline-bar-pin", ".va-plot-row", ".va-plot-grid", "subgrid", "min-width: 780px", ".va-overlay-control::after", "pointer: coarse) and (min-width: 768px)"):
            self.assertIn(needle, stage_txt)
        self.assertIn("@media (pointer: coarse) and (min-width: 768px)", tokens_txt)
        self.assertNotIn("!important", stage_txt.lower() + tokens_txt.lower())

    def test_cdp_sticky_chrome_bloat_and_nested_exemption(self) -> None:
        self._require_cdp()
        bloat_p = self.tmp_dir / "sticky_bloat.html"
        bloat_p.write_text(
            "<!DOCTYPE html><html lang='en'><head><style>"
            "body{margin:0;font-size:14px;background:#fff;height:1800px}"
            ".bar1{position:sticky;top:0;height:52px;width:100%;background:#f8fafc}"
            ".bar2{position:sticky;top:52px;height:44px;width:100%;background:#e2e8f0}"
            "</style></head><body>"
            "<header class='bar1'>Brand</header><div class='bar2'>Filters</div><main>Content</main>"
            "</body></html>",
            encoding="utf-8",
        )
        r_fail = self._run_auditor(bloat_p, "--cdp")
        self.assertEqual(r_fail.returncode, 1, r_fail.stdout)
        self.assertIn("[STICKY_CHROME_BLOAT]", r_fail.stdout)
        self.assertIn("@820px", r_fail.stdout)
        self.assertEqual(self._run_auditor(bloat_p, "--cdp", "--allow-showcase-chrome").returncode, 0)

        clean_p = self.tmp_dir / "sticky_ok.html"
        clean_p.write_text(
            "<!DOCTYPE html><html lang='en'><head><style>"
            "body{margin:0;font-size:14px;background:#fff;height:1800px}"
            ".rail{position:fixed;top:0;left:0;width:220px;height:100vh;background:#f8fafc}"
            ".hdr{position:sticky;top:0;height:52px;width:100%;background:#fff}"
            ".hdr-in{position:sticky;top:0;height:40px;width:100%}"
            "@media(max-width:1099px){.rail{display:none}}"
            "</style></head><body>"
            "<aside class='rail'>Nav</aside><header class='hdr'><div class='hdr-in'>Single Row</div></header>"
            "<main><details><summary>0 issues</summary><table><tr><th>k</th><td>0</td></tr></table></details></main>"
            "</body></html>",
            encoding="utf-8",
        )
        self.assertEqual(self._run_auditor(clean_p, "--cdp").returncode, 0)

    def test_cdp_plot_axis_misalign_and_subgrid_echarts_grid(self) -> None:
        self._require_cdp()
        mis_p = self.tmp_dir / "plot_misalign.html"
        mis_p.write_text(
            "<!DOCTYPE html><html lang='en'><head><style>"
            "body{margin:0;font-size:14px;background:#fff}"
            "main{max-width:760px;margin:0 auto;padding:12px}"
            "svg{display:block;width:100%;height:auto}"
            "</style></head><body><main>"
            "<svg viewBox='0 0 600 180' role='img' aria-label='Top Plot'>"
            "<rect data-role='frame' x='52' y='20' width='520' height='130' fill='none' stroke='#111'/>"
            "<text x='12' y='24'>6,000,000</text><text x='60' y='170'>10:00</text></svg>"
            "<svg viewBox='0 0 600 180' role='img' aria-label='Bottom Plot'>"
            "<rect data-role='frame' x='74' y='20' width='498' height='130' fill='none' stroke='#111'/>"
            "<text x='12' y='24'>3.5M</text><text x='80' y='170'>10:00</text></svg>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_mis = self._run_auditor(mis_p, "--cdp")
        self.assertEqual(r_mis.returncode, 1, r_mis.stdout)
        self.assertIn("[PLOT_AXIS_MISALIGN]", r_mis.stdout)

        # Build a real 2x2 ECharts + subgrid page and verify 0 misalignment and compact coarse/foldable CSS
        shutil.copy2(ECHARTS_MIN, self.tmp_dir / "echarts.min.js")
        shutil.copy2(SVG_LAYOUT_JS, self.tmp_dir / "quiet-svg-chart-layout.js")
        shutil.copy2(ECHARTS_DEFAULTS_JS, self.tmp_dir / "echarts-layout-defaults.js")
        css_all = "\n".join(p.read_text("utf-8") for p in (LAYERS_CSS, TOKENS_CSS, STAGE_CSS, PILLS_CSS))
        (self.tmp_dir / "bundle.css").write_text(css_all, encoding="utf-8")
        aligned_p = self.tmp_dir / "aligned_grid.html"
        aligned_p.write_text(
            "<!DOCTYPE html><html lang='en' data-theme='white' data-form-factor='touch'><head>"
            "<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<link rel='stylesheet' href='bundle.css'>"
            "<style>body{margin:0;padding:12px}.ehost{width:100%;height:200px}</style>"
            "<script src='echarts.min.js'></script>"
            "<script src='quiet-svg-chart-layout.js'></script>"
            "<script src='echarts-layout-defaults.js'></script></head><body><main>"
            "<div class='va-toolbar-joined' role='toolbar'><div class='va-tb-group'>"
            "<button class='va-tb-btn' id='tb1'>24h</button><button class='va-tb-btn'>7d</button></div>"
            "<span class='va-pill' id='stpill' data-variant='status' data-state='nominal'>Nominal</span>"
            "<button class='va-overlay-control' id='ovbtn' aria-label='Select'></button>"
            "<button class='va-overlay-control' id='ovhid' hidden aria-label='Hidden'></button>"
            "<button class='va-pill-btn' id='pbhid' hidden>HiddenBtn</button></div>"
            "<div class='va-compare-grid hidden' id='cmphid'><div>Hidden Compare</div></div>"
            "<div class='va-kpi-gauge-grid' id='kpihid' hidden><div>Hidden KPI</div></div>"
            "<section class='va-plot-grid' id='grid2d'>"
            "<article class='va-card'><h3 style='margin:0'>Throughput Cohort</h3><div class='ehost' id='c00'></div><footer>n=30</footer></article>"
            "<article class='va-card'><h3 style='margin:0'>Dual Axis Utilization &amp; Wrapped Subgrid Card Title</h3><div class='ehost' id='c01'></div><footer>n=30</footer></article>"
            "<article class='va-card'><h3 style='margin:0'>Thermal Envelope</h3><div class='ehost' id='c10'></div><footer>degC</footer></article>"
            "<article class='va-card'><h3 style='margin:0'>Duty Ratio</h3><div class='ehost' id='c11'></div><footer>%</footer></article>"
            "</section><script>"
            "const m = [\n"
            "  [\n"
            "    { animation: false, xUnit: 't', yUnit: 'req', xAxis: { type: 'category', data: ['10:00','10:15','10:30'] }, yAxis: { type: 'value', axisLabel: { formatter: v => (v>=1e6?(v/1e6)+'M':v) } }, series: [{ type: 'bar', data: [1e6, 6e6, 3e6] }] },\n"
            "    { animation: false, xUnit: 't', yUnit: 'ms', xAxis: { type: 'category', data: ['10:00','10:15','10:30'] }, yAxis: [{ type: 'value' }, { type: 'value', max: 100 }], legend: { data: ['Lat', 'SLA'] }, series: [{ name: 'Lat', type: 'line', data: [20, 45, 30] }, { name: 'SLA', type: 'line', yAxisIndex: 1, data: [80, 95, 90] }] }\n"
            "  ],\n"
            "  [\n"
            "    { animation: false, xUnit: 't', yUnit: 'degC', xAxis: { type: 'category', data: ['10:15'] }, yAxis: { type: 'value' }, series: [{ type: 'line', data: [38] }] },\n"
            "    { animation: false, xUnit: 't', yUnit: 'pct', xAxis: { type: 'category', data: ['10:00','10:15','10:30'] }, yAxis: { type: 'value' }, series: [{ type: 'bar', data: [40, 70, 55] }] }\n"
            "  ]\n"
            "];\n"
            "const ids = [['c00','c01'],['c10','c11']];\n"
            "const hosts = ids.map(row => row.map(id => echarts.init(document.getElementById(id), null, { renderer: 'svg' })));\n"
            "function syncGrid() {\n"
            "  QuietEChartsDefaults.alignPlotGridFrames(m, { containerWidth: window.innerWidth });\n"
            "  m.forEach((row, r) => row.forEach((opt, c) => { hosts[r][c].setOption(opt, true); hosts[r][c].resize(); }));\n"
            "}\n"
            "syncGrid(); window.addEventListener('resize', syncGrid);\n"
            "</script></main></body></html>",
            encoding="utf-8",
        )
        r_ok = self._run_auditor(aligned_p, "--cdp", "--exclude", "echarts.min.js")
        self.assertEqual(r_ok.returncode, 0, r_ok.stdout + r_ok.stderr)

        # Verify @layer utilities .hidden/[hidden] display:none, 22px overlay control, compact pill, and 820px subgrid
        tests_dir = str(REPO_ROOT / "tests")
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        from cdp_gates import create_headless_driver  # noqa: E402

        drv = create_headless_driver()
        try:
            drv.get(aligned_p.as_uri())
            drv.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 820, "height": 1080, "deviceScaleFactor": 1, "mobile": False})
            geom = drv.execute_script("""
                return {
                  hiddenDisplays: ['cmphid', 'ovhid', 'pbhid', 'kpihid'].map(id => getComputedStyle(document.getElementById(id)).display),
                  ovH: Math.round(document.getElementById('ovbtn').getBoundingClientRect().height),
                  pillH: Math.round(document.getElementById('stpill').getBoundingClientRect().height),
                  c00Top: Math.round(document.getElementById('c00').getBoundingClientRect().top),
                  c01Top: Math.round(document.getElementById('c01').getBoundingClientRect().top),
                };
            """)
            self.assertEqual(geom["hiddenDisplays"], ["none", "none", "none", "none"])
            self.assertLessEqual(geom["ovH"], 24)
            self.assertLessEqual(geom["pillH"], 22)
            self.assertLessEqual(abs(geom["c00Top"] - geom["c01Top"]), 2)
        finally:
            drv.quit()

        # Unaligned containLabel:true real ECharts stack ('6,000,000' vs '3.5M') MUST trigger [PLOT_AXIS_MISALIGN]
        ec_bad = self.tmp_dir / "echarts_misalign.html"
        ec_bad.write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<style>body{margin:0;padding:12px;font-size:14px;background:#fff}.eh{width:100%;height:190px}</style>"
            "<script src='echarts.min.js'></script></head><body><main>"
            "<div class='eh' id='eb1'></div><div class='eh' id='eb2'></div><script>"
            "echarts.init(document.getElementById('eb1'),null,{renderer:'svg'}).setOption({animation:false,grid:{containLabel:true,left:12,right:12},xAxis:{type:'category',data:['A','B']},yAxis:{type:'value'},series:[{type:'bar',data:[1e6,6e6]}]});"
            "echarts.init(document.getElementById('eb2'),null,{renderer:'svg'}).setOption({animation:false,grid:{containLabel:true,left:12,right:12},xAxis:{type:'category',data:['A','B']},yAxis:{type:'value'},series:[{type:'bar',data:[1,5]}]});"
            "</script></main></body></html>",
            encoding="utf-8",
        )
        r_ec_bad = self._run_auditor(ec_bad, "--cdp", "--exclude", "echarts.min.js")
        self.assertEqual(r_ec_bad.returncode, 1, r_ec_bad.stdout)
        self.assertIn("[PLOT_AXIS_MISALIGN]", r_ec_bad.stdout)


if __name__ == "__main__":
    unittest.main()
