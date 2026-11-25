#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.7.0 Wave 2 — Static Budgets, Single Control Home & CDP Interactive Tests."""
from __future__ import annotations

import ast
import os
import statistics
import sys
import time
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.views.world_wave2_infra_calc import build_v25_html, compute_v26_model  # noqa: E402
from src.views.world_wave2_ops import build_v23_html, build_v24_html, generate_v24_events  # noqa: E402
from tests.cdp_gates import (  # noqa: E402
    create_headless_driver,
    set_viewport,
    start_http_server,
)

WAVE2_VIEWS = (
    ("02-cloud-cyber-and-ai-ops", "v23-semantic-config-diff-review"),
    ("02-cloud-cyber-and-ai-ops", "v24-telemetry-event-triage-desk"),
    ("03-industrial-grid-and-manufacturing", "v25-subsea-corridor-and-link-margin"),
    ("04-civic-finance-and-stem-learning", "v26-constrained-trade-space-calculator"),
)


def _can_launch_cdp() -> tuple[bool, str]:
    try:
        import selenium  # noqa: F401
    except Exception as exc:
        return False, f"selenium missing: {exc}"
    try:
        drv = create_headless_driver()
        drv.quit()
        return True, ""
    except Exception as exc:
        return False, str(exc)


class TestV970Wave2Archetypes(unittest.TestCase):
    """Verify Wave 2 line/function budgets, Single Control Home, math conservation, and live CDP UX."""

    def test_wave2_budgets_and_quantitative_conservation(self) -> None:
        targets = (
            "src/views/world_wave2_ops.py",
            "src/views/world_wave2_infra_calc.py",
            "src/views/world_04_civic_finance_stem.py",
            "src/css/20-wave2-archetypes.css",
            "src/js/quiet-wave2-svg.js",
            "src/js/quiet-wave2-interactions.js",
            "scripts/bench_wave2_specimens.py",
            "tests/test_v970_wave2_archetypes.py",
        )
        for rel in targets:
            txt = (REPO_ROOT / rel).read_text(encoding="utf-8")
            self.assertLessEqual(len(txt.splitlines()), 450, f"{rel} exceeded 450L")
            if rel.endswith(".py"):
                tree = ast.parse(txt, filename=rel)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        span = (node.end_lineno or node.lineno) - node.lineno + 1
                        self.assertLessEqual(span, 100, f"{rel}:{node.name} exceeded 100L")
            if rel.endswith(".js"):
                lines = txt.splitlines()
                starts = [i for i, ln in enumerate(lines) if ln.startswith("  function ")]
                for pos, st in enumerate(starts):
                    end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
                    self.assertLessEqual(end - st, 100, f"{rel}:{lines[st].strip()} exceeded 100L")
            if rel.endswith(".css"):
                self.assertNotIn("!important", txt.lower())

        events = generate_v24_events()
        self.assertEqual(len(events), 48)
        self.assertEqual(sum(1 for e in events if e["cat"] == "critical"), 9)
        self.assertEqual(sum(1 for e in events if e["cat"] == "warning"), 14)
        self.assertEqual(sum(1 for e in events if e["cat"] == "auth_tls"), 11)
        self.assertEqual(sum(1 for e in events if e["cat"] == "nominal"), 14)
        self.assertEqual(len({e["svc"] for e in events}), 4)
        durs = [float(e["dur"].split()[0]) for e in events]
        self.assertEqual(statistics.median(durs), 148.0)

        mod = compute_v26_model(25, 60, 24)
        self.assertEqual(mod["crossover"], 14)
        self.assertEqual(mod["crossover_c"], 31)
        self.assertEqual(mod["winner"], "Option B Hybrid")
        self.assertEqual(mod["y_max"], 6.5)
        self.assertGreater(mod["savings"], 0.9)
        over = compute_v26_model(45, 60, 24)
        self.assertEqual(over["winner"], "Over-Constrained")
        self.assertEqual(over["rec_state"], "warn")
        self.assertEqual(over["constraint_status"], "over_constrained")
        recov = compute_v26_model(45, 80, 24)
        self.assertEqual(recov["winner"], "Option B Hybrid")
        self.assertEqual(recov["rec_state"], "nominal")

        uncrossed = compute_v26_model(10, 20, 24)
        self.assertIsNone(uncrossed["crossover"])
        self.assertEqual(uncrossed["winner"], "Option A PayGo")
        blocked = compute_v26_model(50, 80, 36)
        self.assertEqual(blocked["winner"], "None (Runway Blocked)")
        self.assertEqual(blocked["rec_state"], "fault")
        self.assertEqual(blocked["y_max"], 8.0)

        w2_css = (REPO_ROOT / "src/css/20-wave2-archetypes.css").read_text(encoding="utf-8")
        self.assertNotIn("rgba(", w2_css.lower())
        bench_html = (REPO_ROOT / "docs/bench/evidence-bench.html").read_text(encoding="utf-8")
        self.assertIn("Grid Synchrophasor Frequency", bench_html)
        self.assertIn("59.850 Hz", bench_html)
        self.assertIn("Repeater R8", build_v25_html())
        svg_js = (REPO_ROOT / "src/js/quiet-wave2-svg.js").read_text(encoding="utf-8")
        self.assertLessEqual(len(svg_js.splitlines()), 450)

        for html_chunk in (build_v23_html(), build_v24_html()):
            self.assertNotIn("!important", html_chunk.lower())
            self.assertNotIn(' style="', html_chunk)

        rail_js = (REPO_ROOT / "src/js/studio-presets-and-rail.js").read_text(encoding="utf-8")
        for pat in ("#v23-", "#v24-", "#v25-", "#v26-"):
            self.assertNotIn(pat, rail_js)

    def test_wave2_studio_views_and_specimens_cdp(self) -> None:
        require_cdp = os.environ.get("QUIET_REQUIRE_CDP") == "1"
        ok, reason = _can_launch_cdp()
        if not ok:
            if require_cdp:
                self.fail(f"QUIET_REQUIRE_CDP=1 set but Headless Chrome unavailable: {reason}")
            self.skipTest(f"CDP Wave 2 skipped ({reason})")

        srv, port = start_http_server(REPO_ROOT)
        root_url = f"http://127.0.0.1:{port}"
        base_url = f"{root_url}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        try:
            self._verify_v23_studio(driver, base_url)
            self._verify_v24_studio(driver, base_url)
            self._verify_v25_studio(driver, base_url)
            self._verify_v26_studio(driver, base_url)
            self._verify_viewports_themes_and_print(driver, base_url)
            self._verify_bench_specimens_51_to_53(driver, root_url)
            severe = [e for e in driver.get_log("browser") if e.get("level") == "SEVERE" and "favicon.ico" not in e.get("message", "")]
            self.assertEqual(severe, [], f"SEVERE console errors: {severe}")
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()

    def _open_stage_doc(self, driver: Any, base_url: str, world: str, view: str, theme: str = "white") -> None:
        driver.switch_to.default_content()
        driver.get(f"{base_url}?mode=examples&world={world}&view={view}&theme={theme}&preset=fill")
        for _ in range(45):
            time.sleep(0.06)
            ready = driver.execute_script(
                "const f=document.getElementById('va-stage-portal');const d=f&&f.contentDocument;"
                "return !!(d&&d.documentElement?.dataset?.view===arguments[0]&&d.getElementById('va-stage-main')?.children?.length);",
                view,
            )
            if ready:
                break
        driver.switch_to.frame(driver.find_element("id", "va-stage-portal"))

    def _verify_v23_studio(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        self._open_stage_doc(driver, base_url, *WAVE2_VIEWS[0])
        res = driver.execute_script(
            """
            const vis = () => [...document.querySelectorAll('.v23-row')].filter(r => !r.hidden).length;
            const c0 = vis(), blast0 = document.querySelector('[data-v23-kpi="blast"]').textContent;
            document.querySelector('[data-v23-context]').click();
            const cCtx = vis();
            document.querySelector('[data-v23-filter="security"]').click();
            document.querySelector('[data-v23-context]').click();
            const cSec = vis();
            document.querySelector('[data-v23-filter="all"]').click();
            document.querySelector('[data-v23-stage]').click();
            const stagedPill = document.getElementById('v23-header-status-pill').textContent;
            document.querySelector('[data-v23-confirm]').click();
            const promPill = document.getElementById('v23-header-status-pill').textContent;
            const blastProm = document.querySelector('[data-v23-kpi="blast"]').textContent;
            const blastSub = document.querySelector('[data-v23-kpi="blast_sub"]').textContent;
            const toastOpen = !document.querySelector('[data-v23-toast]').hidden;
            document.querySelector('[data-v23-toast-revert]').click();
            const revPill = document.getElementById('v23-header-status-pill').textContent;
            const blastRev = document.querySelector('[data-v23-kpi="blast"]').textContent;
            return { c0, cCtx, cSec, blast0, stagedPill, promPill, blastProm, blastSub, toastOpen, revPill, blastRev };
            """
        )
        self.assertEqual((res["c0"], res["cCtx"], res["cSec"]), (6, 12, 3))
        self.assertEqual(res["blast0"], "2 of 14 clusters")
        self.assertEqual(res["stagedPill"], "CANARY r42 STAGED")
        self.assertEqual(res["promPill"], "PROMOTED r42")
        self.assertEqual(res["blastProm"], "14 of 14 clusters")
        self.assertIn("Global r42 active", res["blastSub"])
        self.assertTrue(res["toastOpen"])
        self.assertEqual((res["revPill"], res["blastRev"]), ("BASELINE r41", "2 of 14 clusters"))

    def _verify_v24_studio(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        self._open_stage_doc(driver, base_url, *WAVE2_VIEWS[1])
        res = driver.execute_script(
            """
            const wrap = document.querySelector('.v24-table-scroll'), tbl = document.querySelector('[data-v24-table]');
            const tblOverflowX = tbl.scrollWidth > wrap.clientWidth + 2, total = document.querySelectorAll('.v24-row').length;
            const row2 = document.querySelectorAll('.v24-row')[2];
            row2.click();
            const rowClickVis = [...document.querySelectorAll('.v24-row')].filter(r => !r.hidden).length;
            const rowHasPressed = row2.hasAttribute('aria-pressed');
            document.querySelector('.w2-svg-bar-grp[data-v24-bucket="8"]').dispatchEvent(new MouseEvent('click', { bubbles: true }));
            const b8Vis = [...document.querySelectorAll('.v24-row')].filter(r => !r.hidden).length;
            document.querySelector('[data-v24-filter="all"]').click();
            document.querySelector('[data-v24-filter="critical"]').click();
            const critCnt = [...document.querySelectorAll('.v24-row')].filter(r => !r.hidden).length;
            document.querySelector('.v24-row[data-v24-cat="critical"]').click();
            const inspSpan = document.querySelector('[data-insp-span]').textContent;
            const inp = document.querySelector('[data-v24-search]');
            inp.value = 'no-such-xyz-event'; inp.dispatchEvent(new Event('input', { bubbles: true }));
            const emptyOpen = !document.querySelector('[data-v24-empty]').hidden;
            const inspEmpty = !document.querySelector('[data-v24-insp-empty]').hidden && document.querySelector('[data-v24-insp-body]').hidden;
            const sevHid = document.querySelector('[data-insp-sev]').hidden;
            document.querySelector('[data-v24-clear]').click();
            const restored = [...document.querySelectorAll('.v24-row')].filter(r => !r.hidden).length;
            const inspBack = document.querySelector('[data-v24-insp-empty]').hidden && !document.querySelector('[data-v24-insp-body]').hidden;
            return { tblOverflowX, total, rowClickVis, rowHasPressed, b8Vis, critCnt, inspSpan, emptyOpen, inspEmpty, sevHid, restored, inspBack };
            """
        )
        self.assertFalse(res["tblOverflowX"], "v24 desktop table overflowed horizontally")
        self.assertEqual((res["total"], res["rowClickVis"], res["rowHasPressed"], res["b8Vis"], res["critCnt"]), (48, 48, False, 4, 9))
        self.assertTrue(res["inspSpan"].startswith("sp-") and res["emptyOpen"] and res["inspEmpty"] and res["sevHid"])
        self.assertEqual(res["restored"], 48)
        self.assertTrue(res["inspBack"])

    def _verify_v25_studio(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        self._open_stage_doc(driver, base_url, *WAVE2_VIEWS[2])
        res = driver.execute_script(
            """
            const rows = document.querySelectorAll('.w2-span-row').length;
            const texts = [...document.querySelectorAll('[data-v25-bathy-svg] text')];
            const hasR8 = texts.some(t => t.textContent.trim() === 'Repeater R8');
            const r8 = texts.find(t => t.textContent.trim() === 'Repeater R8')?.getBoundingClientRect();
            const r7 = texts.find(t => t.textContent.trim() === 'Repeater R7')?.getBoundingClientRect();
            const br = texts.find(t => t.textContent.trim() === 'CLS-Bravo')?.getBoundingClientRect();
            const overlap = !!(r8 && ((r7 && r8.left < r7.right && r8.top < r7.bottom && r8.bottom > r7.top) || (br && r8.right > br.left && r8.top < br.bottom && r8.bottom > br.top)));
            document.querySelector('[data-v25-span="fault"]').click();
            const hotRows = document.querySelectorAll('.w2-span-row[data-span-hot="1"]').length;
            const dimMarks = document.querySelectorAll('.w2-span-mark[data-span-dim="1"]').length;
            document.querySelector('[data-v25-span="all"]').click();
            const resetDim = document.querySelectorAll('.w2-span-row[data-span-dim="1"]').length;
            return { rows, hasR8, overlap, hotRows, dimMarks, resetDim };
            """
        )
        self.assertEqual((res["rows"], res["hotRows"], res["dimMarks"], res["resetDim"]), (10, 1, 9, 0))
        self.assertTrue(res["hasR8"], "v25 missing Repeater R8 label")
        self.assertFalse(res["overlap"], "v25 Repeater R8 overlapped R7 or CLS-Bravo")

    def _verify_v26_studio(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        self._open_stage_doc(driver, base_url, *WAVE2_VIEWS[3])
        res = driver.execute_script(
            """
            const cInit = document.querySelector('[data-v26-kpi="crossover"]').textContent;
            const p0 = document.querySelector('[data-v26-path="b"]').getAttribute('d');
            const g = document.getElementById('v26-growth'), c = document.getElementById('v26-commit'), r = document.getElementById('v26-runway');
            const set = (el, v) => { el.value = String(v); el.dispatchEvent(new Event('input', { bubbles: true })); };
            set(g, 45); set(c, 60); set(r, 24);
            const overW = document.querySelector('[data-v26-kpi="winner"]').textContent;
            const overSt = document.querySelector('[data-v26-rec-badge]').getAttribute('data-state');
            const overBadge = document.querySelector('[data-v26-rec-badge]').textContent;
            const overDispB = document.querySelector('[data-v26-row="disp"] [data-col="b"]').textContent;
            set(c, 80);
            const recW = document.querySelector('[data-v26-kpi="winner"]').textContent;
            const recSt = document.querySelector('[data-v26-rec-badge]').getAttribute('data-state');
            set(c, 75);
            const cNew = document.querySelector('[data-v26-kpi="crossover"]').textContent;
            const p1 = document.querySelector('[data-v26-path="b"]').getAttribute('d');
            const yHas8 = document.querySelector('[data-v26-ygrid]').textContent.includes('$8.0M');
            set(g, 10); set(c, 20);
            const cUn = document.querySelector('[data-v26-kpi="crossover"]').textContent;
            const crossHidden = document.querySelector('[data-v26-cross-line]').getAttribute('display') === 'none';
            const aDisp = document.querySelector('[data-v26-row="disp"] [data-col="a"]').textContent;
            set(g, 50); set(r, 36);
            const blkBadge = document.querySelector('[data-v26-rec-badge]').textContent;
            const blkState = document.querySelector('[data-v26-rec-badge]').getAttribute('data-state');
            return { cInit, overW, overSt, overBadge, overDispB, recW, recSt, cNew, pathChanged: p0 !== p1, yHas8, cUn, crossHidden, aDisp, blkBadge, blkState };
            """
        )
        self.assertEqual((res["cInit"], res["overW"], res["overSt"], res["overDispB"]), ("Month 14", "Over-Constrained", "warn", "OVER CEILING"))
        self.assertIn("OVER-CONSTRAINED", res["overBadge"])
        self.assertEqual((res["recW"], res["recSt"]), ("Option B Hybrid", "nominal"))
        self.assertTrue(res["pathChanged"] and res["yHas8"] and res["crossHidden"])
        self.assertEqual((res["cUn"], res["aDisp"], res["blkBadge"], res["blkState"]), ("No crossover", "RECOMMENDED", "RUNWAY GATE BLOCKED", "fault"))

    def _verify_viewports_themes_and_print(self, driver: Any, base_url: str) -> None:
        for vp_w, vp_h in ((1440, 900), (900, 1050), (390, 844)):
            set_viewport(driver, vp_w, vp_h, 1)
            for world, view in WAVE2_VIEWS:
                self._open_stage_doc(driver, base_url, world, view)
                diag = driver.execute_script(
                    """
                    const ovX = document.documentElement.scrollWidth > window.innerWidth + 2;
                    const boxScr = [...document.querySelectorAll('.w2-svg-box')].some(b => b.scrollWidth > b.clientWidth + 2);
                    const minRatio = Math.min(...[...document.querySelectorAll('.w2-svg-box')].map(b => {
                        const s = b.querySelector('svg');
                        return s ? (s.getBoundingClientRect().width / Math.max(1, b.getBoundingClientRect().width)) : 1;
                    }));
                    const maxVbW = Math.max(...[...document.querySelectorAll('.w2-svg-box svg')].map(s => Number((s.getAttribute('viewBox') || '').split(/\\s+/)[2] || 0)));
                    let overlapTxt = 0;
                    document.querySelectorAll('.w2-svg-box svg').forEach(svg => {
                        const ts = [...svg.querySelectorAll('text')].map(t => t.getBoundingClientRect()).filter(r => r.width > 0);
                        for (let i = 0; i < ts.length; i++) for (let j = i + 1; j < ts.length; j++) {
                            if (Math.min(ts[i].right, ts[j].right) - Math.max(ts[i].left, ts[j].left) > 2.5 && Math.min(ts[i].bottom, ts[j].bottom) - Math.max(ts[i].top, ts[j].top) > 4.5) overlapTxt++;
                        }
                    });
                    const badSvg = [...document.querySelectorAll('.w2-svg-box svg text')].filter(t => {
                        const sr = t.closest('svg').getBoundingClientRect(), tr = t.getBoundingClientRect();
                        return tr.width > 0 && (tr.right > sr.right + 2 || tr.left < sr.left - 2 || tr.bottom > sr.bottom + 2);
                    }).length;
                    const tdMob = document.querySelector('.w2-table td[data-label]');
                    return { ovX, boxScr, minRatio, maxVbW, overlapTxt, badSvg, tdDisp: tdMob ? getComputedStyle(tdMob).display : '', hasRailCtrl: !!document.querySelector('#va-shell-rail [id^="v2"]') };
                    """
                )
                self.assertFalse(diag["ovX"], f"{view} overflowX at {vp_w}px")
                self.assertFalse(diag["boxScr"], f"{view} SVG box scrolled horizontally at {vp_w}px")
                self.assertGreaterEqual(diag["minRatio"], 0.90, f"{view} SVG not full-width at {vp_w}px")
                self.assertEqual(diag["overlapTxt"], 0, f"{view} SVG labels overlapped at {vp_w}px")
                self.assertEqual(diag["badSvg"], 0, f"{view} clipped SVG label at {vp_w}px")
                self.assertFalse(diag["hasRailCtrl"], f"{view} leaked controls into left rail")
                if vp_w == 390:
                    self.assertLess(diag["maxVbW"], 500, f"{view} Studio SVG viewBox stayed wide at 390px ({diag['maxVbW']})")
                    self.assertIn(diag["tdDisp"], ("flex", "block"), f"{view} missing stacked card row at 390px")

        set_viewport(driver, 1440, 900, 1)
        for theme in ("white", "paper", "dark-paper", "dark"):
            self._open_stage_doc(driver, base_url, *WAVE2_VIEWS[0], theme=theme)
            self.assertEqual(driver.execute_script("return document.documentElement.dataset.theme;"), theme)
        self._open_stage_doc(driver, base_url, *WAVE2_VIEWS[1])
        driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
        print_chk = driver.execute_script(
            "return { tb: getComputedStyle(document.querySelector('.w2-toolbar')).display, sc: getComputedStyle(document.querySelector('.v24-table-scroll')).overflowY };"
        )
        driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
        self.assertEqual((print_chk["tb"], print_chk["sc"]), ("none", "visible"))

    def _verify_bench_specimens_51_to_53(self, driver: Any, root_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.switch_to.default_content()
        driver.get(f"{root_url}/docs/bench/evidence-bench.html")
        time.sleep(0.35)
        res = driver.execute_script(
            """
            const s50Pill = document.querySelector('#ui-alarm-lifecycle .v9-demo-subcard .va-pill')?.textContent || '';
            const s51 = document.getElementById('ui-semantic-diff-gate');
            const s52 = document.getElementById('ui-triage-log-inspector');
            const s53 = document.getElementById('ui-constrained-tradespace');
            const s52InitState = s52.querySelector('[data-insp-sev]').getAttribute('data-state');
            s52.querySelectorAll('.v24-row')[1].click();
            const s52RowVis = [...s52.querySelectorAll('.v24-row')].filter(r => !r.hidden).length;
            s51.querySelector('[data-v23-stage]').click();
            const s51Stage = s51.querySelector('[data-v23-pill]').textContent;
            s51.querySelector('[data-v23-confirm]').click();
            const s51Blast = s51.querySelector('[data-v23-kpi="blast"]').textContent;
            s51.querySelector('[data-v23-revert]').click();
            const s51Rev = s51.querySelector('[data-v23-kpi="blast"]').textContent;
            const q = s52.querySelector('[data-v24-search]');
            q.value = 'none-xyz'; q.dispatchEvent(new Event('input', { bubbles: true }));
            const s52Empty = !s52.querySelector('[data-v24-empty]').hidden && !s52.querySelector('[data-v24-insp-empty]').hidden;
            s52.querySelector('[data-v24-clear]').click();
            const s52Restored = [...s52.querySelectorAll('.v24-row')].filter(r => !r.hidden).length;
            const sl = s53.querySelector('#s53-growth');
            sl.value = '45'; sl.dispatchEvent(new Event('input', { bubbles: true }));
            const s53Over = s53.querySelector('[data-v26-kpi="winner"]').textContent;
            const s53St = s53.querySelector('[data-v26-rec-badge]').getAttribute('data-state');
            return { found: !!(s51 && s52 && s53), s50Pill, s52InitState, s52RowVis, s51Stage, s51Blast, s51Rev, s52Empty, s52Restored, s53Over, s53St, s53Out: s53.querySelector('[data-v26-out="growth"]').textContent };
            """
        )
        self.assertTrue(res["found"] and res["s52Empty"] and ("Hz" in res["s50Pill"]) and ("%" not in res["s50Pill"]))
        self.assertEqual((res["s52InitState"], res["s52RowVis"], res["s51Stage"], res["s51Blast"], res["s51Rev"]), ("nominal", 12, "CANARY r42 STAGED", "14 of 14 clusters", "2 of 14 clusters"))
        self.assertEqual((res["s52Restored"], res["s53Out"], res["s53Over"], res["s53St"]), (12, "45%", "Over-Constrained", "warn"))

