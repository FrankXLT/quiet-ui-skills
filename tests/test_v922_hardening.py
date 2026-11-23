#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.2.2 hardening tests: bundle parity, UTC binning, mono gutters, and 6 new CDP/static gates."""

from __future__ import annotations

import json
import os
import re
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
UX_DRIFT_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_ux_and_drift.py"
TOKENS_CSS = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
BUNDLE_CSS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.css"
BUNDLE_JS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.js"
STAGE_CSS = REPO_ROOT / "src" / "css" / "01-stage-and-containers.css"
NAV_CSS = REPO_ROOT / "src" / "css" / "02-nav-shells-and-drawers.css"
SVG_LAYOUT_JS = REPO_ROOT / "src" / "js" / "quiet-svg-chart-layout.js"
ECHARTS_DEFAULTS_JS = REPO_ROOT / "src" / "js" / "echarts-layout-defaults.js"


class TestV922Hardening(unittest.TestCase):
    """Verify v9.2.2 bundle parity, adaptive binning, monospace gutters, and static/CDP auditor gates."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.auditor = self.tmp_dir / "audit_quiet_html.py"
        for src in (AUDITOR_SRC, CHECKS_SRC, PROBES_SRC, STATIC_RULES_SRC, UX_DRIFT_SRC):
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

    def test_bundle_exports_and_layer_order(self) -> None:
        tok = TOKENS_CSS.read_text("utf-8")
        css = BUNDLE_CSS.read_text("utf-8")
        js = BUNDLE_JS.read_text("utf-8")
        self.assertEqual(len(re.findall(r"--bg-subtle:", tok)), 4)
        self.assertIn("@layer reset, tokens, shell, archetypes, evidence, views, utilities;", css)
        for cls in (
            ".va-workbench-panes", ".va-pane", ".va-pane-hdr", ".va-pane-body",
            ".va-pane-count", ".va-side-rail", ".va-drawer-backdrop",
            ".va-kpi-grid", ".va-kpi-card", "max-inline-size: 1480px",
        ):
            self.assertIn(cls, css, f"Missing shipped CSS selector/rule: {cls}")
        tb_active = STAGE_CSS.read_text("utf-8").split(".va-tb-btn[aria-pressed=\"true\"]")[1].split("}")[0]
        self.assertNotIn("inset 0 -2px 0", tb_active)
        self.assertIn("inset 0 0 0 1px var(--border-strong)", tb_active)
        self.assertIn("flex: 0 0 auto;", STAGE_CSS.read_text("utf-8"))
        for sym in ("QuietSvgLayout", "QuietEChartsDefaults", "binTimeSeries", "alignPlotGridFrames"):
            self.assertIn(sym, js, f"Missing JS export in bundle: {sym}")

    def test_documented_va_qe_classes_exist_in_bundle(self) -> None:
        bundle_txt = BUNDLE_CSS.read_text("utf-8") + "\n" + TOKENS_CSS.read_text("utf-8")
        defined_classes = set(re.findall(r"\.((?:va|qe)-[a-z0-9-]+)\b", bundle_txt))
        missing: list[str] = []
        for md in sorted((REPO_ROOT / "skills").rglob("*.md")):
            raw = md.read_text("utf-8")
            css_blocks = re.findall(r"```css\b(.*?)```", raw, flags=re.S | re.I)
            local_defs = set(re.findall(r"\.((?:va|qe)-[a-z0-9-]+)\b", "\n".join(css_blocks)))
            without_css = re.sub(r"```css\b.*?```", "", raw, flags=re.S | re.I)
            refs = set(re.findall(r"(?<![A-Za-z0-9_/-])\.((?:va|qe)-[a-z0-9-]+)\b", without_css))
            for cls in sorted(refs - defined_classes - local_defs):
                missing.append(f"{md.relative_to(REPO_ROOT).as_posix()}: .{cls}")
        self.assertEqual(missing, [], "Documented .va-*/.qe-* classes missing from bundle:\n" + "\n".join(missing))

    def test_node_measure_category_gutter_and_bin_time_series(self) -> None:
        node_bin = shutil.which("node")
        self.assertIsNotNone(node_bin, "Node.js required to verify QuietSvgLayout & binTimeSeries")
        script = (
            f"const L = require({json.dumps(str(SVG_LAYOUT_JS))});\n"
            f"const D = require({json.dumps(str(ECHARTS_DEFAULTS_JS))});\n"
            "const sans = L.measureCategoryGutter(['Home', 'Logs']);\n"
            "const mono = L.measureCategoryGutter(['claude-sonnet-4-5-thinking', 'gemini-2.5-pro'], { axisLabelMargin: 8 });\n"
            "if (!mono.mono || mono.gutterPx <= sans.gutterPx || mono.gutterPx < 170) {\n"
            "  throw new Error('Unexpected mono gutter sizing: ' + JSON.stringify({ sans, mono }));\n"
            "}\n"
            "const hDates = [], hVals = [];\n"
            "for (let d = 0; d < 2; d += 1) for (let h = 0; h < 24; h += 1) {\n"
            "  hDates.push(`2026-11-0${d + 1} ${String(h).padStart(2, '0')}:00`); hVals.push(2);\n"
            "}\n"
            "const r1h = D.binTimeSeries(hDates, { s: hVals });\n"
            "if (r1h.bin !== '1h' || r1h.dates.length !== 48 || r1h.layers.s.reduce((a, b) => a + b, 0) !== 96) {\n"
            "  throw new Error('1h binning mismatch: ' + JSON.stringify(r1h));\n"
            "}\n"
            "const d14 = [], v14 = [];\n"
            "for (let d = 1; d <= 14; d += 1) for (let h = 0; h < 24; h += 1) {\n"
            "  d14.push(`2026-11-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:00`); v14.push(1);\n"
            "}\n"
            "const r1d = D.binTimeSeries(d14, { s: v14 });\n"
            "if (r1d.bin !== '1d' || r1d.dates.length !== 14 || r1d.layers.s.reduce((a, b) => a + b, 0) !== 336) {\n"
            "  throw new Error('1d binning mismatch: ' + JSON.stringify(r1d));\n"
            "}\n"
            "const d120 = [], v120 = [];\n"
            "for (let i = 0; i < 120; i += 1) {\n"
            "  const dt = new Date(Date.UTC(2026, 0, 1 + i));\n"
            "  d120.push(dt.toISOString().slice(0, 10)); v120.push(5);\n"
            "}\n"
            "const r1w = D.binTimeSeries(d120, { total: v120 });\n"
            "if (r1w.bin !== '1w' || r1w.dates.length >= 25 || !/^\\d{4}-W\\d{2}$/.test(r1w.dates[0]) || r1w.layers.total.reduce((a, b) => a + b, 0) !== 600) {\n"
            "  throw new Error('1w ISO week binning mismatch: ' + JSON.stringify(r1w));\n"
            "}\n"
            "const optA = { xAxis: { type: 'category', data: ['2026-11-01', '2026-11-02'] }, yAxis: { type: 'value' }, series: [{ type: 'bar', data: [10, 20] }] };\n"
            "const optB = { xAxis: { type: 'category', data: ['00h', '01h', '02h'] }, yAxis: { type: 'category', data: ['opus-4-5-thinking', 'sonnet-4-5'] }, series: [{ type: 'bar', data: [4, 7] }] };\n"
            "D.alignSharedAxes([optA, optB]);\n"
            "if (!optA.independentXSpan || !optB.independentXSpan || optA.xAxis.data.length !== 2 || optB.xAxis.data.length !== 3) {\n"
            "  throw new Error('Disparate X formats were merged unexpectedly');\n"
            "}\n"
            "if (optB.grid.left < 130 || optA.grid.left !== optB.grid.left) {\n"
            "  throw new Error('Horizontal mono Y-category gutter mismatch: ' + JSON.stringify([optA.grid, optB.grid]));\n"
            "}\n"
            "const safeOpt = L.measureCategoryGutter(['svc_a'], { axisLabelMargin: '8px', fontSize: -4, mono: false });\n"
            "if (!Number.isFinite(safeOpt.gutterPx) || safeOpt.mono) {\n"
            "  throw new Error('Invalid option guard failed: ' + JSON.stringify(safeOpt));\n"
            "}\n"
            "const invDates = D.binTimeSeries(['2026-02-31', '2026-W99', '2026-11-01'], { s: [1, 2, 3] });\n"
            "if (invDates.dates.length !== 1 || invDates.layers.s[0] !== 3) {\n"
            "  throw new Error('Invalid calendar/week rejection failed: ' + JSON.stringify(invDates));\n"
            "}\n"
            "const valNullA = { xAxis: { type: 'value', min: null }, yAxis: { type: 'value' }, series: [{ type: 'line', data: [[10, 5], [20, 8]] }] };\n"
            "const valNullB = { xAxis: { type: 'value', min: '' }, yAxis: { type: 'value' }, series: [{ type: 'line', data: [[15, 3], [30, 9]] }] };\n"
            "D.alignSharedAxes([valNullA, valNullB]);\n"
            "if (valNullA.xAxis.min !== 10 || valNullB.xAxis.max !== 30) {\n"
            "  throw new Error('Null value axis min coerced to 0: ' + JSON.stringify([valNullA.xAxis, valNullB.xAxis]));\n"
            "}\n"
        )
        script_path = self.tmp_dir / "verify_v922_js.js"
        script_path.write_text(script, encoding="utf-8")
        subprocess.run([node_bin, str(script_path)], check=True)

    def test_static_json_mock_and_chrome_emoji_rejection(self) -> None:
        clean_app = self.tmp_dir / "clean_app"
        clean_app.mkdir()
        (clean_app / "package.json").write_text('{"name":"ops-ui","workspaces":[{"path":"a"},{"path":"b"}]}', encoding="utf-8")
        (clean_app / "config.json").write_text('{"endpoints":[{"name":"alpha"},{"name":"beta"}]}', encoding="utf-8")
        (clean_app / "demographics.json").write_text('[{"cohort":"A","n":12},{"cohort":"B","n":18}]', encoding="utf-8")
        (clean_app / "telemetry_samples.json").write_text('{"samples":[{"x":1,"records":"ok"},{"x":2,"records":"ok"}]}', encoding="utf-8")
        (clean_app / "demo_snapshot.json").write_text('[{"id":1,"name":"sensor-a"},{"id":2,"name":"sensor-b"}]', encoding="utf-8")
        (clean_app / "index.html").write_text(
            "<!DOCTYPE html><html lang='en'><body><header><nav><button type='button'>"
            "<svg viewBox='0 0 16 16' width='14' height='14' aria-hidden='true'><path d='M2 8h12'/></svg> Refresh"
            "</button></nav></header><main><code>⚡</code></main></body></html>",
            encoding="utf-8",
        )
        self.assertEqual(self._run_auditor(clean_app).returncode, 0)

        dirty_app = self.tmp_dir / "dirty_app"
        dirty_app.mkdir()
        (dirty_app / "mock_transcripts.json").write_text(
            '[{"session":"demo_1","transcript":"hello"},{"session":"demo_2","transcript":"world"}]',
            encoding="utf-8",
        )
        (dirty_app / "index.html").write_text(
            "<!DOCTYPE html><html lang='en'><body><header><button type='button'><span>\U0001f512</span> Unlock</button></header></body></html>",
            encoding="utf-8",
        )
        res = self._run_auditor(dirty_app)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("[JSON_MOCK_FIXTURE]", res.stdout + res.stderr)
        self.assertIn("[EMOJI_IN_CHROME]", res.stdout + res.stderr)

    def test_cdp_v922_gates_negative_and_positive(self) -> None:
        self._require_cdp()
        head = (
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<style>body{margin:0;padding:12px;font-size:14px;background:#fff;color:#0f172a}"
            ".va-kpi-gauge-card,.va-kpi-card{border:1px solid #e2e8f0;padding:10px}"
            ".va-kpi-gauge-track{height:6px;background:#f8fafc}"
            ".va-pane-hdr{height:40px;display:flex;justify-content:space-between;align-items:center}</style></head><body>"
        )
        bad_clip = self.tmp_dir / "bad_clip.html"
        bad_clip.write_text(
            head + "<main><svg width='300' height='120' viewBox='0 0 300 120' role='img' aria-label='Clip'>"
            "<text x='-24' y='40'>clipped-mono-id</text><rect x='40' y='20' width='200' height='40' fill='#1d4ed8'/>"
            "</svg></main></body></html>",
            encoding="utf-8",
        )
        r_clip = self._run_auditor(bad_clip, "--cdp")
        self.assertNotEqual(r_clip.returncode, 0)
        self.assertIn("[AXIS_LABEL_CLIPPED]", r_clip.stdout + r_clip.stderr)

        needles = "".join(f"<rect x='{50 + i * 4}' y='40' width='2' height='60' fill='#1d4ed8'/>" for i in range(60))
        bad_bars = self.tmp_dir / "bad_bars.html"
        bad_bars.write_text(
            head + "<main><svg width='320' height='160' viewBox='0 0 320 160' role='img' aria-label='Dense Bars'>"
            "<rect x='44' y='15' width='260' height='120' fill='none' stroke='#cbd5e1'/>"
            f"<text x='46' y='28'>Tokens</text><text x='46' y='150'>Time</text>{needles}</svg></main></body></html>",
            encoding="utf-8",
        )
        r_bars = self._run_auditor(bad_bars, "--cdp")
        self.assertNotEqual(r_bars.returncode, 0)
        self.assertIn("[BAR_HAIRLINE_DENSITY]", r_bars.stdout + r_bars.stderr)

        bad_gauge = self.tmp_dir / "bad_gauge.html"
        bad_gauge.write_text(
            head + "<main><div class='va-kpi-gauge-card'><div class='va-kpi-gauge-label'>Cumulative Steps</div>"
            "<div class='va-kpi-gauge-val'>14,820 steps</div>"
            "<div class='va-kpi-gauge-track' role='progressbar'><div class='va-kpi-gauge-fill' style='width:100%'></div></div>"
            "<div class='va-kpi-gauge-stats'><span>7d total</span></div></div></main></body></html>",
            encoding="utf-8",
        )
        r_gauge = self._run_auditor(bad_gauge, "--cdp")
        self.assertNotEqual(r_gauge.returncode, 0)
        self.assertIn("[FAKE_UNBOUNDED_GAUGE]", r_gauge.stdout + r_gauge.stderr)

        bad_nav = self.tmp_dir / "bad_nav_pane.html"
        bad_nav.write_text(
            head + "<header style='display:flex;gap:8px;align-items:center'>"
            "<button id='cond-btn' type='button' style='display:none;width:48px'>Rail</button>"
            "<span class='va-studio-brand'>Console</span>"
            "<div role='tablist'><button role='tab' aria-selected='true' onclick=\"document.getElementById('cond-btn').style.display='none'\">A</button>"
            "<button role='tab' aria-selected='false' onclick=\"document.getElementById('cond-btn').style.display='inline-flex'\">B</button></div>"
            "<button type='button'>\u2728 Magic</button></header>"
            "<main><div class='va-pane-hdr' style='width:120px;overflow:hidden;white-space:nowrap'>"
            "<span>Long Pane Header Title</span><span class='va-pane-count' style='min-width:90px'>9999</span>"
            "</div></main></body></html>",
            encoding="utf-8",
        )
        r_nav = self._run_auditor(bad_nav, "--cdp")
        self.assertNotEqual(r_nav.returncode, 0)
        out_nav = r_nav.stdout + r_nav.stderr
        self.assertIn("[NAVBAR_SHIFT]", out_nav)
        self.assertIn("[PANE_CONTROL_CLIPPED]", out_nav)
        self.assertIn("[EMOJI_IN_CHROME]", out_nav)

        good_page = self.tmp_dir / "good_v922.html"
        good_page.write_text(
            "<!DOCTYPE html><html lang='en' data-theme='white'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<style>" + BUNDLE_CSS.read_text("utf-8") + "</style></head><body>"
            "<header style='display:flex;gap:8px;align-items:center;padding:6px 12px'>"
            "<span class='va-studio-brand'>Ops</span>"
            "<div role='tablist'><button role='tab' aria-selected='true'>Overview</button>"
            "<button role='tab' aria-selected='false'>Runs</button></div></header>"
            "<main class='va-stage'><aside class='va-side-rail' data-open='true'><span>Projects</span></aside>"
            "<div class='va-kpi-grid'><div class='va-kpi-card'><div class='va-kpi-head'><span class='va-kpi-label'>Total Steps</span></div>"
            "<div class='va-kpi-val'>14,820 steps</div></div>"
            "<div class='va-kpi-gauge-card'><div class='va-kpi-gauge-head'><span class='va-kpi-gauge-label'>Cryo Stage</span></div>"
            "<div class='va-kpi-gauge-val'>294.2 K</div><div class='va-kpi-gauge-track' role='progressbar'><div class='va-kpi-gauge-fill' style='width:42%'></div></div>"
            "<div class='va-kpi-gauge-stats'><span>Range 290-300 K</span></div></div></div>"
            "<div class='va-pane-hdr'><div class='va-tab-strip' role='tablist' style='max-width:140px'>"
            "<button type='button' class='va-tab' role='tab' aria-selected='true'>Overview</button>"
            "<button type='button' class='va-tab' role='tab' aria-selected='false'>Extended Telemetry Log</button>"
            "<button type='button' class='va-tab' role='tab' aria-selected='false'>Diffs</button>"
            "</div><span class='va-pane-count'>4</span></div>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_good = self._run_auditor(good_page, "--cdp")
        self.assertEqual(r_good.returncode, 0, f"Unexpected failure on clean fixture:\n{r_good.stdout}\n{r_good.stderr}")

        tests_dir = str(Path(__file__).resolve().parent)
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        from cdp_gates import create_headless_driver, set_viewport, start_http_server

        srv, port = start_http_server(self.tmp_dir)
        driver = create_headless_driver()
        try:
            set_viewport(driver, 390, 844)
            driver.get(f"http://127.0.0.1:{port}/{good_page.name}")
            rail_bg = driver.execute_script(
                "const r = document.querySelector('.va-side-rail[data-open=\"true\"]');"
                "return r ? getComputedStyle(r).backgroundColor : '';"
            )
            self.assertTrue(
                rail_bg and not rail_bg.endswith(", 0)") and rail_bg != "transparent",
                f"Expected opaque .va-side-rail background at 390px, got {rail_bg!r}",
            )
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
