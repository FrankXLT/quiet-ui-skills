#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Wave 4 unit and CDP tests for [PILL_SPRAWL], hairline M3 panes, unified corners, and observeChartResize."""

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
TOKENS_CSS = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
LAYERS_CSS = REPO_ROOT / "src" / "css" / "00-layers-and-reset.css"
STAGE_CSS = REPO_ROOT / "src" / "css" / "01-stage-and-containers.css"
NAV_CSS = REPO_ROOT / "src" / "css" / "02-nav-shells-and-drawers.css"
PILLS_CSS = REPO_ROOT / "src" / "css" / "03-pills-and-annunciators.css"
EVIDENCE_CSS = REPO_ROOT / "src" / "css" / "05-evidence-stage.css"
ECHARTS_MIN = REPO_ROOT / "docs" / "assets" / "vendor" / "echarts.min.js"
SVG_LAYOUT_JS = REPO_ROOT / "src" / "js" / "quiet-svg-chart-layout.js"
ECHARTS_DEFAULTS_JS = REPO_ROOT / "src" / "js" / "echarts-layout-defaults.js"
ECHARTS_ADAPTER_JS = REPO_ROOT / "src" / "js" / "echarts-quiet-adapter.js"


class TestCoherenceAndResize(unittest.TestCase):
    """Verify Wave 4 CSS coherence primitives, [PILL_SPRAWL], and ResizeObserver chart sizing."""

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

    def test_wave4_css_tokens_and_panes_contract(self) -> None:
        tok = TOKENS_CSS.read_text("utf-8")
        stage = STAGE_CSS.read_text("utf-8")
        nav = NAV_CSS.read_text("utf-8")
        ev = EVIDENCE_CSS.read_text("utf-8")
        for i in range(1, 6):
            self.assertIn(f"--chart-{i}:", tok)
        self.assertNotIn("border-radius: var(--radius-pill);", tok.split(".va-pill-btn")[1].split("}")[0])
        for needle in (".va-meta-inline", ".va-tab-strip", ".va-tab", "var(--radius-sm, 5px)", "min-width: 0; max-width: 100%;"):
            self.assertIn(needle, stage)
        for needle in (".va-workbench-panes", ".va-pane", ".va-pane-hdr", "height: 40px;", ".va-pane-count"):
            self.assertIn(needle, nav)
        self.assertIn("min-width: 0; max-width: 100%;", ev)

    def test_node_observe_chart_resize_and_adapter_cleanup(self) -> None:
        adapter = ECHARTS_ADAPTER_JS.read_text("utf-8")
        self.assertIn("HOST_RESIZE_CLEANUPS", adapter)
        self.assertIn("defaults.observeChartResize", adapter)
        node_bin = shutil.which("node")
        self.assertIsNotNone(node_bin, "Node.js required to verify observeChartResize")
        script = (
            "let roCb = null, disconnected = 0, rafQueue = [], rafSeq = 1, canceled = [];\n"
            "global.ResizeObserver = class { constructor(cb) { roCb = cb; } observe() {} disconnect() { disconnected += 1; } };\n"
            "global.requestAnimationFrame = (fn) => { const id = rafSeq++; rafQueue.push({ id, fn }); return id; };\n"
            "global.cancelAnimationFrame = (id) => { canceled.push(id); rafQueue = rafQueue.filter(r => r.id !== id); };\n"
            f"const D = require({json.dumps(str(ECHARTS_DEFAULTS_JS))});\n"
            "const host = { clientWidth: 1000 };\n"
            "let resizes = 0, cbCalls = 0, disposed = false;\n"
            "const chart = { resize() { resizes += 1; }, isDisposed() { return disposed; } };\n"
            "const cleanup = D.observeChartResize(host, chart);\n"
            "roCb(); if (rafQueue.length !== 0) throw new Error('fired without width change');\n"
            "host.clientWidth = 720; roCb(); host.clientWidth = 710; roCb();\n"
            "if (rafQueue.length !== 1) throw new Error('expected single RAF debounce');\n"
            "rafQueue.shift().fn();\n"
            "if (resizes !== 1) throw new Error('expected resize on width change, got ' + resizes);\n"
            "disposed = true; host.clientWidth = 500; roCb();\n"
            "if (disconnected !== 1 || rafQueue.length !== 0) throw new Error('disposed chart spun RAF or stayed connected');\n"
            "disposed = false; const cleanup2 = D.observeChartResize(host, chart, { onResize(w) { cbCalls += w; } });\n"
            "host.clientWidth = 640; roCb(); rafQueue.shift().fn();\n"
            "if (cbCalls !== 640) throw new Error('onResize callback failed');\n"
            "host.clientWidth = 960; roCb(); cleanup2();\n"
            "if (disconnected !== 2 || canceled.length !== 1 || rafQueue.length !== 0) throw new Error('cleanup failed to disconnect/cancel');\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=True) as tf:
            tf.write(script)
            tf.flush()
            subprocess.run([node_bin, tf.name], check=True)

    def test_cdp_pill_sprawl_rejection_and_allow_showcase_exemption(self) -> None:
        self._require_cdp()
        base_head = "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{margin:0;padding:12px;font-size:14px;background:#fff;color:#111}.row{display:flex;gap:8px;flex-wrap:wrap}.pill{display:inline-flex;align-items:center;height:24px;padding:0 10px;border-radius:999px;background:#eef2ff;border:1px solid #cbd5e1}.rect{height:28px;padding:0 10px;border-radius:6px;background:#f8fafc;border:1px solid #cbd5e1}</style></head><body>"

        hdr_sprawl = self.tmp_dir / "hdr_sprawl.html"
        hdr_sprawl.write_text(
            base_head + "<header class='row'><span>Svc</span><span class='pill'>v1.2</span><span class='pill'>2026-11-21</span><span class='pill'>main</span></header><main><p>Ok</p></main></body></html>",
            encoding="utf-8",
        )
        r1 = self._run_auditor(hdr_sprawl, "--cdp")
        self.assertEqual(r1.returncode, 1, r1.stdout)
        self.assertIn("[PILL_SPRAWL]", r1.stdout)
        self.assertEqual(self._run_auditor(hdr_sprawl, "--cdp", "--allow-showcase-chrome").returncode, 0)

        tall_hdr = self.tmp_dir / "tall_hdr.html"
        six_pills = "".join(f"<span class='pill'>p-{i}</span>" for i in range(6))
        tall_hdr.write_text(base_head + f"<header class='row' style='min-height:240px'>{six_pills}</header><main><p>Ok</p></main></body></html>", encoding="utf-8")
        r_tall = self._run_auditor(tall_hdr, "--cdp")
        self.assertEqual(r_tall.returncode, 1, r_tall.stdout)
        self.assertIn("[PILL_SPRAWL]", r_tall.stdout)

        nested_ok = self.tmp_dir / "nested_ok.html"
        three_nested = "".join(f"<span class='pill'><span class='pill'>n-{i}</span></span>" for i in range(3))
        nested_ok.write_text(base_head + f"<main><article class='va-card'><div class='row'>{three_nested}</div></article></main></body></html>", encoding="utf-8")
        self.assertEqual(self._run_auditor(nested_ok, "--cdp").returncode, 0)

        cloud_sprawl = self.tmp_dir / "cloud_sprawl.html"
        spans = "".join(f"<span class='pill'>tag-{i}</span>" for i in range(6))
        cloud_sprawl.write_text(base_head + f"<main><article class='va-card'><div class='row'>{spans}</div></article></main></body></html>", encoding="utf-8")
        r2 = self._run_auditor(cloud_sprawl, "--cdp")
        self.assertEqual(r2.returncode, 1, r2.stdout)
        self.assertIn("[PILL_SPRAWL]", r2.stdout)

        tab_clash = self.tmp_dir / "tab_clash.html"
        tab_clash.write_text(
            base_head + "<main><button class='rect'>Filter</button><div role='tablist' class='row'><button role='tab' class='pill'>Overview</button><button role='tab' class='pill'>Logs</button></div></main></body></html>",
            encoding="utf-8",
        )
        r3 = self._run_auditor(tab_clash, "--cdp")
        self.assertEqual(r3.returncode, 1, r3.stdout)
        self.assertIn("[PILL_SPRAWL]", r3.stdout)

    def test_cdp_unified_panes_and_halfscreen_resize_observer(self) -> None:
        self._require_cdp()
        shutil.copy2(ECHARTS_MIN, self.tmp_dir / "echarts.min.js")
        shutil.copy2(SVG_LAYOUT_JS, self.tmp_dir / "quiet-svg-chart-layout.js")
        shutil.copy2(ECHARTS_DEFAULTS_JS, self.tmp_dir / "echarts-layout-defaults.js")
        shutil.copy2(ECHARTS_ADAPTER_JS, self.tmp_dir / "echarts-quiet-adapter.js")
        css_all = "\n".join(p.read_text("utf-8") for p in (LAYERS_CSS, TOKENS_CSS, STAGE_CSS, NAV_CSS, PILLS_CSS, EVIDENCE_CSS))
        (self.tmp_dir / "bundle.css").write_text(css_all, encoding="utf-8")

        payload = json.dumps({
            "kind": "cartesian",
            "x": {"name": "Run Index", "min": 1, "max": 4, "interval": 1},
            "y": {"name": "Latency (ms)", "min": 0, "max": 100, "interval": 25},
            "series": [{"id": "s1", "name": "Median", "epistemic": "analytical_model", "data": [[1, 32], [2, 48], [3, 41], [4, 58]]}],
        })
        page_p = self.tmp_dir / "coherent_workbench.html"
        page_p.write_text(
            "<!DOCTYPE html><html lang='en' data-theme='white' data-medium='m3'><head>"
            "<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<link rel='stylesheet' href='bundle.css'>"
            "<style>body{margin:0;padding:12px;background:var(--bg-shell);color:var(--text-primary)}</style>"
            "<script src='echarts.min.js'></script>"
            "<script src='quiet-svg-chart-layout.js'></script>"
            "<script src='echarts-layout-defaults.js'></script>"
            "<script src='echarts-quiet-adapter.js'></script></head><body><main>"
            "<div class='va-workbench-panes'>"
            "<aside class='va-pane'><div class='va-pane-hdr'><span>Streams</span><span class='va-pane-count'>15</span></div><div class='va-pane-body'><span class='va-meta-inline'>2026-11-21 · main</span></div></aside>"
            "<section class='va-pane'><div class='va-pane-hdr'><span>Telemetry</span><span class='va-badge va-badge-ok'>HEALTHY</span></div><div class='va-pane-body'>"
            "<div class='va-toolbar-joined' role='toolbar' aria-label='Range'><div class='va-tb-group'><button class='va-tb-btn' aria-pressed='true'>24h</button><button class='va-tb-btn' aria-pressed='false'>7d</button></div></div>"
            "<div class='va-tab-strip' role='tablist' aria-label='Views'><button class='va-tab' role='tab' aria-selected='true'>Summary</button><button class='va-tab' role='tab' aria-selected='false'>Trace</button></div>"
            f"<div class='qe-plot-wrap' data-echarts-mode='echarts' data-quiet-echarts='{payload}'><div class='va-figure-scroll'><div class='qe-echarts-host' id='ehost'></div><svg class='qe-svg-fallback' viewBox='0 0 200 80' aria-hidden='true'></svg></div></div>"
            "</div></section>"
            "<aside class='va-pane'><div class='va-pane-hdr'><span>Details</span><span class='va-pane-count'>4</span></div><div class='va-pane-body'><span class='va-meta-inline'>98.4% nominal</span></div></aside>"
            "</div>"
            "<article class='va-card' data-axis-align='independent' style='margin-top:12px'><div class='qe-plot-wrap'><div class='qe-echarts-host' id='directhost' style='height:180px'></div></div></article>"
            "<script>QuietEChartsAdapter.boot(document);"
            "const dh=document.getElementById('directhost'), dc=echarts.init(dh,null,{renderer:'svg'});"
            "dc.setOption({animation:false,grid:{left:44,right:16,top:20,bottom:28},xAxis:{type:'category',data:['A','B','C','D']},yAxis:{type:'value'},series:[{type:'bar',data:[12,34,28,45]}]});"
            "QuietEChartsDefaults.observeChartResize(dh, dc);</script></main></body></html>",
            encoding="utf-8",
        )
        r_clean = self._run_auditor(page_p, "--cdp", "--exclude", "echarts.min.js")
        self.assertEqual(r_clean.returncode, 0, r_clean.stdout + r_clean.stderr)

        tests_dir = str(REPO_ROOT / "tests")
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        from cdp_gates import create_headless_driver  # noqa: E402

        drv = create_headless_driver()
        try:
            drv.get(page_p.as_uri())
            drv.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
            time.sleep(0.25)
            m1440 = drv.execute_script(
                "const h=document.getElementById('ehost'), svg=h.querySelector('svg'), dh=document.getElementById('directhost'), dsvg=dh.querySelector('svg'), hdrs=[...document.querySelectorAll('.va-pane-hdr')].map(e=>Math.round(e.getBoundingClientRect().height)), bd=getComputedStyle(document.querySelector('.va-badge'));"
                "return {sw:document.documentElement.scrollWidth, iw:window.innerWidth, hw:h.getBoundingClientRect().width, svw:svg?svg.getBoundingClientRect().width:0, dhw:dh.getBoundingClientRect().width, dsvw:dsvg?dsvg.getBoundingClientRect().width:0, hdrs, rad:parseFloat(bd.borderTopLeftRadius)};"
            )
            self.assertLessEqual(m1440["sw"], m1440["iw"] + 2)
            self.assertEqual(m1440["hdrs"], [40, 40, 40])
            self.assertLessEqual(m1440["rad"], 8.0)
            self.assertGreater(m1440["svw"], m1440["hw"] * 0.9)
            self.assertGreater(m1440["dsvw"], m1440["dhw"] * 0.9)

            drv.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 720, "height": 900, "deviceScaleFactor": 1, "mobile": False})
            time.sleep(0.25)
            m720 = drv.execute_script(
                "const h=document.getElementById('ehost'), svg=h.querySelector('svg'), dh=document.getElementById('directhost'), dsvg=dh.querySelector('svg');"
                "return {sw:document.documentElement.scrollWidth, iw:window.innerWidth, hw:h.getBoundingClientRect().width, svw:svg?svg.getBoundingClientRect().width:0, dhw:dh.getBoundingClientRect().width, dsvw:dsvg?dsvg.getBoundingClientRect().width:0};"
            )
            self.assertLessEqual(m720["sw"], m720["iw"] + 2)
            self.assertGreater(m720["svw"], m720["hw"] * 0.9)
            self.assertLessEqual(m720["svw"], m720["hw"] + 2)
            self.assertGreater(m720["dsvw"], m720["dhw"] * 0.9)
            self.assertLess(m720["dsvw"], m1440["dsvw"] - 300)

            drv.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
            time.sleep(0.25)
            mBack = drv.execute_script(
                "const h=document.getElementById('ehost'), svg=h.querySelector('svg'), dh=document.getElementById('directhost'), dsvg=dh.querySelector('svg');"
                "return {hw:h.getBoundingClientRect().width, svw:svg?svg.getBoundingClientRect().width:0, dhw:dh.getBoundingClientRect().width, dsvw:dsvg?dsvg.getBoundingClientRect().width:0};"
            )
            self.assertEqual(round(mBack["svw"]), round(m1440["svw"]))
            self.assertGreater(mBack["dsvw"], mBack["dhw"] * 0.9)
            self.assertGreater(mBack["dsvw"], m720["dsvw"] + 300)
        finally:
            drv.quit()


if __name__ == "__main__":
    unittest.main()
