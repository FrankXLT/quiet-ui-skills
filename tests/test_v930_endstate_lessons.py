#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.3.0 verification: End-state layout lessons, Cyclical Whiskers (S43), and CDP gates."""

from __future__ import annotations

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
BUNDLE_CSS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.css"
BUNDLE_JS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.js"
BENCH_HTML = REPO_ROOT / "docs" / "bench" / "evidence-bench.html"


class TestV930EndstateLessons(unittest.TestCase):
    """Verify v9.3.0 upstream lessons across bundle exports, Node contracts, static lints, and CDP."""

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

    def _require_cdp(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise
            self.skipTest("selenium not installed")

    def test_v930_bundle_exports_and_specimen_43(self) -> None:
        css = BUNDLE_CSS.read_text("utf-8")
        js = BUNDLE_JS.read_text("utf-8")
        bench = BENCH_HTML.read_text("utf-8")
        for sel in (
            ".va-rail-footer",
            ".va-swatch-row",
            ".va-swatch-btn",
            ".va-tree-children",
            ".va-tree-more",
            ".va-tree-action",
            ".va-split-reader-gallery",
            ".va-split-reader-primary",
            ".va-split-reader-companion",
            ".va-split-mode-toggle",
            ".va-split-sheet-trigger",
            "dialog.va-modal-sheet[open]",
            "dialog.va-modal-sheet::backdrop",
            "overscroll-behavior: contain",
        ):
            self.assertIn(sel, css, f"Missing v9.3.0 CSS selector/rule in bundle: {sel}")
        for sym in ("buildCyclicalWhiskerOption", "QuietCyclicalWhiskers", "applyTreeChildCaps", "data-dialog-open"):
            self.assertIn(sym, js, f"Missing v9.3.0 JS symbol in bundle: {sym}")
        self.assertIn('id="qe-cyclical-whiskers"', bench)
        self.assertIn("Activity by Hour of Day", bench)
        self.assertNotIn("diurnal", bench.lower())

    def test_node_cyclical_whiskers_contract(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        probe = (
            "const fs=require('fs'), vm=require('vm');\n"
            "const ctx={window:{},globalThis:{},document:null,performance:{now:()=>0}};\n"
            "ctx.window=ctx; ctx.globalThis=ctx;\n"
            "vm.createContext(ctx);\n"
            f"vm.runInContext(fs.readFileSync({str(BUNDLE_JS)!r}, 'utf8'), ctx);\n"
            "const rows=Array.from({length:24},(_,h)=>h===1?{label:'01h',min:0,avg:0,max:0,recent:null,nActive:0}:{label:String(h).padStart(2,'0')+'h',min:h%3,avg:(h%5)+1.5,max:(h%5)+6,recent:(h%4)+2,nActive:5});\n"
            "const opt=ctx.QuietEChartsDefaults.buildCyclicalWhiskerOption(rows,{title:'Activity by Hour of Day',unit:'calls/h',recentLabel:'Today'});\n"
            "if(!opt||!Array.isArray(opt.series)||opt.series.length<3) throw new Error('Expected 3 series');\n"
            "if(opt.tooltip.renderMode!=='richText') throw new Error('Expected renderMode: richText');\n"
            "const t0=opt.tooltip.formatter([{dataIndex:0}]), t1=opt.tooltip.formatter([{dataIndex:1}]);\n"
            "if(!t0.includes('n=5 active days')||t0.includes('<br')) throw new Error('Bad activeDays/tooltip format: '+t0);\n"
            "if(!t1.includes('0 active days')||opt.series[0].data[1][1]!==null) throw new Error('Expected nActive=0 slot skipped');\n"
            "const frac=ctx.QuietEChartsDefaults.buildCyclicalWhiskerOption([{label:'00h',values:[0.02,0.04,0.06],recent:0.05}],{unit:'kW'});\n"
            "if(frac.yAxis.max>=0.25||!frac.tooltip.formatter([{dataIndex:0}]).includes('0.04 kW')) throw new Error('Bad fractional scaling/precision');\n"
            "console.log(JSON.stringify({series:opt.series.map(s=>s.name),t0}));\n"
        )
        res = subprocess.run([node, "-e", probe], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stderr or res.stdout)
        self.assertIn("Active Avg", res.stdout)
        self.assertIn("n=5 active days", res.stdout)

    def _build_clean_html(self) -> str:
        tree_kids = "".join(
            f"<div class='va-tree-row'><button type='button' class='va-tree-dest' data-target='doc-{i}'><span class='va-tree-label'>Runbook Note {i:02d} — Detailed Trace</span></button>"
            f"<button type='button' class='va-tree-action' aria-label='Pin {i}'>+</button></div>"
            + ("<div class='va-tree-group' hidden><div class='va-tree-row'><button type='button' class='va-tree-dest'>Nested Hidden Sub</button></div></div>" if i == 1 else "")
            for i in range(1, 9)
        )
        return (
            "<!DOCTYPE html><html lang='en' data-theme='white' data-medium='m3'><head>"
            "<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<link rel='icon' href='data:,'><style>{BUNDLE_CSS.read_text('utf-8')}</style></head><body>"
            "<header class='va-shell-topbar'>"
            "<button id='rail-btn' type='button' class='va-tb-btn' data-rail-trigger='main-rail' aria-controls='main-rail' aria-expanded='false'>Menu</button>"
            "<span class='va-studio-brand'>Ops Console</span>"
            "<span class='va-scope-chip'><span class='va-scope-dot'></span><span class='va-scope-label'>Node A</span>"
            "<button type='button' class='va-scope-clear' aria-label='Clear scope'>x</button></span>"
            "</header>"
            "<aside id='main-rail' class='va-side-rail' data-mode='overlay' data-open='false'>"
            "<div class='va-tree-row'><button type='button' class='va-tree-caret' aria-expanded='true' aria-label='Toggle Group'>&gt;</button>"
            "<button type='button' class='va-tree-dest is-active' aria-current='page' data-target='overview'><span class='va-tree-label'>Workspace Overview</span></button></div>"
            f"<div class='va-tree-children'>{tree_kids}</div>"
            "<div class='va-rail-footer'>"
            "<div class='va-swatch-row' role='group' aria-label='Theme'>"
            "<button type='button' class='va-swatch-btn is-active' data-swatch='white' aria-pressed='true' aria-label='White theme'></button>"
            "<button type='button' class='va-swatch-btn' data-swatch='paper' aria-pressed='false' aria-label='Paper theme'></button>"
            "<button type='button' class='va-swatch-btn' data-swatch='dark-paper' aria-pressed='false' aria-label='Dark paper theme'></button>"
            "<button type='button' class='va-swatch-btn' data-swatch='dark' aria-pressed='false' aria-label='Dark theme'></button>"
            "</div>"
            "<div class='va-tb-group va-density-toggle' role='group' aria-label='Density'>"
            "<button type='button' class='va-tb-btn' data-density='compact' aria-pressed='false'>Compact</button>"
            "<button type='button' class='va-tb-btn' data-density='comfortable' aria-pressed='true'>Comfortable</button>"
            "</div></div></aside>"
            "<div class='va-drawer-backdrop' data-open='false'></div>"
            "<main class='va-stage'>"
            "<div role='toolbar' aria-label='Mode' style='margin-bottom:8px'><div class='va-tb-group'>"
            "<button type='button' class='va-tb-btn' aria-pressed='true'>Standard</button>"
            "<button type='button' class='va-tb-btn' aria-pressed='false'>Detailed</button></div></div>"
            "<div class='va-split-reader-gallery'>"
            "<article class='va-split-reader-primary va-card'>"
            "<div class='va-pane-hdr'><span>Primary Runbook</span>"
            "<div class='va-tb-group va-split-mode-toggle' role='group' aria-label='View Mode'>"
            "<button type='button' class='va-tb-btn' aria-pressed='true'>Split</button>"
            "<button type='button' class='va-tb-btn' aria-pressed='false'>Docs</button>"
            "<button type='button' class='va-tb-btn' aria-pressed='false'>Captures</button>"
            "</div>"
            "<button type='button' id='sheet-trig' class='va-tb-btn va-split-sheet-trigger' data-dialog-open='cap-sheet'>Captures (2)</button>"
            "</div>"
            "<div class='va-prose'><p>Activity by Hour of Day stays steady across normal runs with zero artificial sums.</p></div>"
            "</article>"
            "<aside class='va-split-reader-companion' data-mobile-promoted='true'>"
            "<div class='va-card va-prose'><div class='va-kicker'>Capture 01</div><p>Desktop layout check clean.</p></div>"
            "<div class='va-card'><div class='va-kicker'>Capture 02</div><p>Foldable 820px split clean.</p></div>"
            "</aside></div>"
            "<div class='va-workbench-panes' style='margin-top:12px'>"
            "<aside class='va-pane'><div class='va-pane-hdr'><span>Nav</span></div><div class='va-pane-body'>Left</div></aside>"
            "<section class='va-pane'><div class='va-pane-hdr'><span>Doc</span></div><div class='va-pane-body va-prose'><p>Center workbench pane.</p></div></section>"
            "<aside class='va-pane'><div class='va-pane-hdr'><span>Meta</span></div><div class='va-pane-body'>Right</div></aside>"
            "</div>"
            "<dialog id='cap-sheet' class='va-modal-sheet' closedby='any'>"
            "<div class='va-modal-sheet-hdr'><span>Captures</span>"
            "<button type='button' id='sheet-close' class='va-tb-btn' data-dialog-close>Close</button></div>"
            "<div class='va-modal-sheet-body'><p>Mobile sheet capture viewer.</p></div>"
            "</dialog></main>"
            f"<script>{BUNDLE_JS.read_text('utf-8')}</script>"
            "<script>// don't flag comments mentioning diurnal;\nwindow.__bgShortcutHits=0;document.addEventListener('keydown',function(e){if(e.key==='k'){if(document.querySelector('dialog[open]'))return;window.__bgShortcutHits+=1;}});</script>"
            "</body></html>"
        )

    def test_static_auditor_v930_gates(self) -> None:
        clean_p = self.tmp_dir / "clean_v930.html"
        clean_p.write_text(self._build_clean_html(), encoding="utf-8")
        r_clean = self._run_auditor(clean_p)
        self.assertEqual(r_clean.returncode, 0, r_clean.stdout + r_clean.stderr)

        bad_p = self.tmp_dir / "bad_v930.html"
        bad_p.write_text(
            "<!DOCTYPE html><html lang='en'><head><style>.va-rail-footer{flex-direction:column;}</style></head><body><main>"
            "<h2>Diurnal Activity</h2>"
            "<aside class='va-side-rail'><div class='va-card va-tree-group'><div class='va-tree-row'><button class='va-tree-dest'>N1</button></div></div>"
            "<div class='va-rail-footer'><div>A</div><div>B</div><div>C</div>"
            "<div class='va-density-toggle'><button>D1</button><button>D2</button><button>D3</button><button>Lock</button></div>"
            "</div></aside><script>const h='Diurnal Peak';</script></main></body></html>",
            encoding="utf-8",
        )
        r_bad = self._run_auditor(bad_p)
        self.assertNotEqual(r_bad.returncode, 0)
        out = r_bad.stdout + r_bad.stderr
        for code in ("[DENSITY_STOP_SPRAWL]", "[RAIL_FOOTER_CLUTTER]", "[TREE_NESTED_CARD_BORDERS]", "[JARGON_TERMINOLOGY]"):
            self.assertIn(code, out, f"Missing expected static code {code}:\n{out}")

    def test_cdp_v930_endstate_geometry_and_dialog(self) -> None:
        self._require_cdp()
        clean_p = self.tmp_dir / "clean_v930.html"
        clean_p.write_text(self._build_clean_html(), encoding="utf-8")
        r_clean = self._run_auditor(clean_p, "--cdp")
        self.assertEqual(r_clean.returncode, 0, f"Unexpected CDP failure on clean v930 page:\n{r_clean.stdout}\n{r_clean.stderr}")

        cramped_p = self.tmp_dir / "cramped_prose.html"
        cramped_p.write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><style>"
            f"{BUNDLE_CSS.read_text('utf-8')}"
            ".cramped-split{display:grid;grid-template-columns:40% 60%;}"
            "</style></head><body><main>"
            "<div class='cramped-split'>"
            "<article class='va-split-reader-primary'><p>Narrow prose column under 55%</p></article>"
            "<aside><p>Oversized right sidebar</p></aside></div>"
            "<label><input type='radio' name='d' data-density='1'>D1</label>"
            "<label><input type='radio' name='d' data-density='2'>D2</label>"
            "<label><input type='radio' name='d' data-density='3'>D3</label>"
            "<h2>Diurnal Activity</h2></main></body></html>",
            encoding="utf-8",
        )
        r_cramp = self._run_auditor(cramped_p, "--cdp")
        self.assertNotEqual(r_cramp.returncode, 0)
        out_c = r_cramp.stdout + r_cramp.stderr
        for code in ("[PROSE_PANE_CRAMPED]", "[JARGON_TERMINOLOGY]", "[DENSITY_STOP_SPRAWL]"):
            self.assertIn(code, out_c)

        tests_dir = str(Path(__file__).resolve().parent)
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
        from cdp_gates import create_headless_driver, set_viewport, start_http_server
        from selenium.webdriver.common.by import By

        srv, port = start_http_server(self.tmp_dir)
        driver = create_headless_driver()
        try:
            url = f"http://127.0.0.1:{port}/{clean_p.name}"
            set_viewport(driver, 390, 844)
            driver.get(url)
            time.sleep(0.15)
            m390 = driver.execute_script(
                "const mt=getComputedStyle(document.querySelector('.va-split-mode-toggle')).display;"
                "const cp=getComputedStyle(document.querySelector('.va-split-reader-companion')).display;"
                "const tbH=Math.round(document.querySelector('.va-shell-topbar').getBoundingClientRect().height);"
                "const st=document.getElementById('sheet-trig').getBoundingClientRect();"
                "const rows=[...document.querySelectorAll('.va-tree-children > .va-tree-row')];"
                "const visRows=rows.filter(r=>!r.hidden).length;"
                "const more=document.querySelector('.va-tree-more');"
                "const leafW=Math.round(rows[0].querySelector('.va-tree-dest').getBoundingClientRect().width);"
                "const rf=document.querySelector('.va-rail-footer'), rfr=rf.getBoundingClientRect();"
                "const sw=document.querySelector('.va-swatch-btn').getBoundingClientRect();"
                "const dn=document.querySelector('[data-density=\"compact\"]').getBoundingClientRect();"
                "return {mt, cp, tbH, stW:st.width, rowCount:rows.length, visRows, leafW, moreTxt:more?more.textContent:'', rfDir:getComputedStyle(rf).flexDirection, rfH:Math.round(rfr.height), swW:Math.round(sw.width), sameRow:Math.abs(sw.top-dn.top)<12};"
            )
            self.assertEqual(m390["mt"], "none")
            self.assertEqual(m390["cp"], "none")
            self.assertLessEqual(m390["tbH"], 88)
            self.assertGreater(m390["stW"], 40)
            self.assertEqual(m390["rowCount"], 8)
            self.assertEqual(m390["visRows"], 5)
            self.assertGreater(m390["leafW"], 120, "Caret-less leaf .va-tree-dest squeezed into 24px track")
            self.assertIn("Show 3", m390["moreTxt"])
            self.assertEqual(m390["rfDir"], "row")
            self.assertLessEqual(m390["rfH"], 52)
            self.assertLessEqual(m390["swW"], 24)
            self.assertTrue(m390["sameRow"])

            driver.find_element(By.ID, "rail-btn").click()
            time.sleep(0.25)
            driver.find_element(By.CSS_SELECTOR, ".va-tree-more").click()
            self.assertEqual(driver.execute_script("return [...document.querySelectorAll('.va-tree-children > .va-tree-row')].filter(r=>!r.hidden).length;"), 8)
            self.assertTrue(driver.execute_script("return document.querySelector('.va-tree-children > .va-tree-group').hidden;"))
            driver.find_element(By.CSS_SELECTOR, ".va-tree-children .va-tree-dest").click()
            time.sleep(0.25)
            self.assertEqual(driver.find_element(By.ID, "main-rail").get_attribute("data-open"), "false")

            driver.find_element(By.ID, "sheet-trig").click()
            time.sleep(0.1)
            self.assertTrue(driver.execute_script("return document.getElementById('cap-sheet').hasAttribute('open') && getComputedStyle(document.documentElement).overflow==='hidden';"))
            driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown',{key:'k',bubbles:true}));")
            self.assertEqual(driver.execute_script("return window.__bgShortcutHits;"), 0)
            driver.find_element(By.ID, "sheet-close").click()
            self.assertFalse(driver.execute_script("return document.getElementById('cap-sheet').hasAttribute('open');"))

            for vw, vh, min_ratio, exp_cols in ((820, 1080, 0.58, 1), (1440, 900, 0.56, 2)):
                set_viewport(driver, vw, vh)
                time.sleep(0.12)
                g = driver.execute_script(
                    "const box=document.querySelector('.va-split-reader-gallery').getBoundingClientRect();"
                    "const p=document.querySelector('.va-split-reader-primary').getBoundingClientRect();"
                    "const cols=getComputedStyle(document.querySelector('.va-split-reader-companion')).gridTemplateColumns.trim().split(/\\s+/).length;"
                    "return {pw:p.width, cw:box.width, cols, overflow:document.documentElement.scrollWidth>window.innerWidth+1};"
                )
                self.assertFalse(g["overflow"], f"Overflow at {vw}px")
                self.assertGreaterEqual(g["pw"] / g["cw"], min_ratio, f"Narrow prose at {vw}px: {g}")
                self.assertGreaterEqual(g["cols"], exp_cols, f"Expected {exp_cols} companion cols at {vw}px: {g}")
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
