# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.7.0 Wave 1.5 tests: trace width, card binding, header/topbar sync & visual polish."""

from __future__ import annotations

import ast
import os
import shutil
import sys
import time
import unittest
from pathlib import Path
from typing import Any

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from cdp_gates import REPO_ROOT, create_headless_driver, set_viewport, start_http_server  # noqa: E402


def _has_chrome() -> bool:
    return bool(shutil.which("chromium") or shutil.which("google-chrome") or os.environ.get("CHROME_BIN"))


class TestWave15Contracts(unittest.TestCase):
    """Static checks for WF-01..WF-09, v9.7 badges, AST compatibility, and line budgets."""

    def test_workflows_version_badge_and_line_budgets(self) -> None:
        wf_text = (REPO_ROOT / "docs" / "WORKFLOWS.md").read_text("utf-8")
        self.assertLessEqual(len(wf_text.splitlines()), 450)
        for tag in (f"WF-0{i}" for i in range(1, 10)):
            self.assertIn(tag, wf_text, f"WORKFLOWS.md missing workflow tag {tag}")

        py_targets = [
            "src/views/world_common.py", "src/views/world_01_clinical.py",
            "src/views/world_02_cloud_cyber_ai.py", "src/views/world_03_industrial_grid.py",
            "src/views/world_06_smart_home.py", "src/views/world_directional_views.py",
            "scripts/build_all.py", "scripts/build_showcase.py",
            "scripts/build_evidence_bench.py", "scripts/bench_alarm_specimen.py",
            "skills/quiet-evidence/scripts/compile_evidence.py",
            "skills/quiet-evidence/scripts/compilers/echarts_adapter.py",
            "skills/quiet-evidence/scripts/compilers/plot_compiler.py",
            "skills/quiet-evidence/scripts/compilers/schematic_variants.py",
            "tests/test_v970_wave15_visual_sync.py",
        ]
        for rel in py_targets:
            src = (REPO_ROOT / rel).read_text("utf-8")
            self.assertLessEqual(len(src.splitlines()), 450, f"{rel} exceeded 450 lines")
            tree = ast.parse(src, filename=rel)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.end_lineno:
                    fn_len = node.end_lineno - node.lineno + 1
                    self.assertLessEqual(fn_len, 100, f"{rel}:{node.name} is {fn_len}L (>100L)")

        for rel in ("src/js/quiet-alarm-trace.js", "src/js/quiet-alarm-lifecycle.js"):
            self.assertLessEqual(len((REPO_ROOT / rel).read_text("utf-8").splitlines()), 450, rel)

        for html_rel in (
            "quiet-ui-showcase.html", "docs/index.html",
            "customizations/personal-starter/showcase.html",
            "customizations/brand-starter/showcase.html",
        ):
            txt = (REPO_ROOT / html_rel).read_text("utf-8")
            self.assertIn('<span class="va-studio-badge">v9.7</span>', txt, f"{html_rel} missing v9.7 badge")
            self.assertNotIn('<span class="va-studio-badge">v9.6</span>', txt, f"{html_rel} kept stale v9.6 badge")


class TestWave15CDP(unittest.TestCase):
    """Live headless Chrome suite verifying Wave 1.5 card binding, full-width trace, and 6 view fixes."""

    def _require_or_skip(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        if not _has_chrome():
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise AssertionError("QUIET_REQUIRE_CDP=1 requires Chromium/Chrome")
            self.skipTest("Chrome/Chromium absent")

    def _wait_view(self, driver: Any, view_id: str, timeout: float = 5.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            cur = driver.execute_script(
                "const d=document.getElementById('va-stage-portal')?.contentDocument;"
                "return d?.getElementById('va-stage-main')?.children.length ? (d.documentElement?.dataset?.view || '') : '';"
            )
            if cur == view_id:
                time.sleep(0.14)
                return
            time.sleep(0.06)
        self.fail(f"Timed out waiting for view '{view_id}'")

    def _check_v08_trace_and_q2_binding(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.get(f"{base_url}?world=03-industrial-grid-and-manufacturing&view=v08-plant-floor-wall-kiosk&alarm=unack&theme=white")
        self._wait_view(driver, "v08-plant-floor-wall-kiosk")
        driver.switch_to.frame("va-stage-portal")
        try:
            u = driver.execute_script(
                """
                const host = document.querySelector('.va-alarm-console');
                const hdr = document.querySelector('.v08-wall-header').getBoundingClientRect();
                const tk = host.querySelector('[data-alarm-takeover]').getBoundingClientRect();
                const cc = host.querySelector('.va-alarm-chart-card').getBoundingClientRect();
                const svg = host.querySelector('svg.va-alarm-focus-svg');
                const sr = svg.getBoundingClientRect();
                const hp = document.querySelector('[data-alarm-header-pill]');
                const polyPts = (svg.querySelector('polyline')?.getAttribute('points') || '').trim().split(/\\s+/).length;
                const breachFill = !!svg.querySelector('path[fill="var(--status-err)"]');
                const ackH = host.querySelector('[data-alarm-ack]').getBoundingClientRect().height;
                const kbds = host.querySelectorAll('.va-alarm-takeover-actions kbd').length;
                return {
                  ratio: sr.width / cc.width, topGap: tk.top - hdr.bottom, polyPts, breachFill, ackH, kbds,
                  svgTxt: svg.textContent, hdrTxt: hp?.textContent.trim(), hdrState: hp?.getAttribute('data-state')
                };
                """
            )
            self.assertGreaterEqual(u["ratio"], 0.85, f"Takeover SVG has side wings: {u['ratio']}")
            self.assertLessEqual(u["topGap"], 32.0, f"v08 Phase 3 top void returned: {u['topGap']}px")
            self.assertGreaterEqual(u["polyPts"], 28, f"Expected >=28 trace samples, got {u['polyPts']}")
            self.assertTrue(u["breachFill"], "Expected translucent breach region path")
            self.assertGreaterEqual(u["ackH"], 44.0)
            self.assertGreaterEqual(u["kbds"], 2)
            for needle in ("Threshold Crossed", "-12s", "00:00 BREACH", "LIVE"):
                self.assertIn(needle, u["svgTxt"])
            self.assertEqual((u["hdrTxt"], u["hdrState"]), ("1 UNACK ALARM", "fault"))

            phases = driver.execute_script(
                """
                const h = document.querySelector('.va-alarm-console');
                const q2 = h.querySelector('.v08-kpi-card[data-v08-ch="freq"]');
                const targets = h.querySelectorAll('[data-alarm-fault-target="1"]');
                const snap = ph => {
                  window.QuietAlarmLifecycle.setPhase(h, ph);
                  const hp = document.querySelector('[data-alarm-header-pill]');
                  return {
                    hdr: hp.textContent.trim(), hdrSt: hp.getAttribute('data-state'),
                    val: q2.querySelector('.v08-kpi-val').textContent.trim(),
                    pill: q2.querySelector('.va-pill').textContent.trim()
                  };
                };
                return { count: targets.length, isFreq: targets[0] === q2, p1: snap('nominal'), p2: snap('approaching'), p4: snap('ack') };
                """
            )
            self.assertEqual(phases["count"], 1)
            self.assertTrue(phases["isFreq"], "v08 fault target must be strictly Q2 Frequency card")
            self.assertEqual((phases["p1"]["hdr"], phases["p1"]["val"]), ("ALL SYSTEMS NOMINAL", "59.985 Hz"))
            self.assertEqual((phases["p2"]["hdr"], phases["p2"]["hdrSt"]), ("APPROACHING LIMIT", "warn"))
            self.assertEqual((phases["p4"]["hdr"], phases["p4"]["val"]), ("1 LATCHED FAULT", "59.790 Hz"))
        finally:
            driver.switch_to.default_content()

    def _check_v01_v04_v07_sync(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        # v01 Card 1 + Topbar sync
        driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
        self._wait_view(driver, "v01-icu-bedside-terminal")
        driver.switch_to.frame("va-stage-portal")
        try:
            v01 = driver.execute_script(
                """
                const h = document.querySelector('.va-alarm-console');
                const tgts = h.querySelectorAll('[data-alarm-fault-target="1"]');
                const first = document.querySelector('#v01-vent .qe-scalar-card');
                const rd = () => ({
                  hdr: document.querySelector('[data-alarm-header-pill]')?.textContent.trim(),
                  topPill: document.querySelector('#va-shell-topbar .va-shell-topbar-status .va-pill')?.textContent.trim(),
                  topM: document.querySelector('#va-shell-topbar .va-shell-topbar-status .va-topbar-metric')?.textContent.trim(),
                  cardVal: first.querySelector('.qe-scalar-val').textContent.trim()
                });
                const p1 = rd();
                window.QuietAlarmLifecycle.setPhase(h, 'nominal');
                const p1Hold = rd();
                window.QuietAlarmLifecycle.setPhase(h, 'ack');
                const p4 = rd();
                return { cnt: tgts.length, isFirst: tgts[0] === first, p1, p1Hold, p4 };
                """
            )
            self.assertEqual(v01["cnt"], 1)
            self.assertTrue(v01["isFirst"])
            self.assertEqual(v01["p1"]["hdr"], "ALL SYSTEMS NOMINAL")
            live_map = float(v01["p1"]["cardVal"].split()[0])
            self.assertGreaterEqual(live_map, 72.5)
            self.assertLessEqual(live_map, 75.5)
            self.assertIn("74.0", v01["p1Hold"]["cardVal"])
            self.assertEqual((v01["p4"]["hdr"], v01["p4"]["topPill"]), ("1 LATCHED FAULT", "1 LATCHED FAULT"))
            self.assertIn("63.5", v01["p4"]["cardVal"])
        finally:
            driver.switch_to.default_content()

        # v04 Tile 1 + independent gate pill
        driver.get(f"{base_url}?world=02-cloud-cyber-and-ai-ops&view=v04-sre-incident-workbench&alarm=unack&theme=white")
        self._wait_view(driver, "v04-sre-incident-workbench")
        driver.switch_to.frame("va-stage-portal")
        try:
            v04 = driver.execute_script(
                "return {cnt: document.querySelectorAll('[data-alarm-fault-target=\"1\"]').length, "
                "hdr: document.querySelector('[data-alarm-header-pill]')?.textContent.trim(), "
                "gate: document.getElementById('v04-gate-pill')?.textContent.trim()};"
            )
            self.assertEqual((v04["cnt"], v04["hdr"], v04["gate"]), (1, "1 UNACK ALARM", "CANARY TRIPPED"))
        finally:
            driver.switch_to.default_content()

        # v07 Card 2 + Phase 4 Topbar sync (never NOMINAL in fault!) + no left-rail quick chips
        driver.get(f"{base_url}?world=03-industrial-grid-and-manufacturing&view=v07-grid-scada-poi-console&theme=white")
        self._wait_view(driver, "v07-grid-scada-poi-console")
        driver.switch_to.frame("va-stage-portal")
        try:
            v07 = driver.execute_script(
                """
                const tgts = document.querySelectorAll('[data-alarm-fault-target="1"]');
                const cards = document.querySelectorAll('#v07-scalars .qe-scalar-card');
                return {
                  cnt: tgts.length, isCard2: tgts[0] === cards[1],
                  hdr: document.querySelector('[data-alarm-header-pill]')?.textContent.trim(),
                  topTxt: document.querySelector('#va-shell-topbar .va-shell-topbar-status')?.innerText || '',
                  railQuick: document.querySelectorAll('#va-shell-rail button[data-quick-idx]').length,
                  gate: document.getElementById('v07-gate-pill')?.textContent.trim()
                };
                """
            )
            self.assertEqual(v07["cnt"], 1)
            self.assertTrue(v07["isCard2"], "v07 fault target must bind strictly to Card 2")
            self.assertEqual(v07["hdr"], "1 LATCHED FAULT")
            self.assertIn("1 LATCHED FAULT", v07["topTxt"])
            self.assertIn("59.864 Hz", v07["topTxt"])
            self.assertNotIn("NOMINAL", v07["topTxt"].upper())
            self.assertEqual(v07["railQuick"], 0, "v07 must keep controls inline only (Single Control Home)")
            self.assertEqual(v07["gate"], "BREAKER 52-M CLOSED")
        finally:
            driver.switch_to.default_content()

    def _check_reworked_boards_polish(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        # v20: markLine label positions separated, crisp subscripts, dumbbell caption, no rail quick chips
        driver.get(f"{base_url}?world=04-civic-finance-and-stem-learning&view=v20-student-capstone-lab-report&theme=white")
        self._wait_view(driver, "v20-student-capstone-lab-report")
        driver.switch_to.frame("va-stage-portal")
        try:
            v20 = driver.execute_script(
                """
                const txts = [...document.querySelectorAll('#v20-trace svg text')]
                  .map(el => { const r = el.getBoundingClientRect(); return { t: el.textContent.trim(), top: r.top, h: r.height, y: parseFloat(el.getAttribute('y') || '0') }; })
                  .filter(x => x.h > 0);
                return {
                  railQuick: document.querySelectorAll('#va-shell-rail button[data-quick-idx]').length,
                  bodyTxt: document.body.innerText,
                  subCount: document.querySelectorAll('#v20-trace sub, #v20-claim sub').length,
                  hi: txts.find(x => x.t.includes('5.10 V')),
                  lo: txts.find(x => x.t.includes('4.90 V')),
                  dumbTitle: document.querySelector('#v20-repeatability .qe-fig-title')?.textContent.trim() || ''
                };
                """
            )
            self.assertEqual(v20["railQuick"], 0, "v20 must keep Rubric Focus inline only")
            self.assertNotIn("t_s =", v20["bodyTxt"])
            self.assertNotIn("ω_n", v20["bodyTxt"])
            self.assertGreaterEqual(v20["subCount"], 2)
            self.assertIn("Five-Bench Probe Zero Repeatability", v20["dumbTitle"])
            self.assertIsNotNone(v20["hi"])
            self.assertIsNotNone(v20["lo"])
            self.assertGreaterEqual(abs(v20["lo"]["top"] - v20["hi"]["top"]), 13.0)
        finally:
            driver.switch_to.default_content()

        # Switch format preset to 1080p (screen m2) to verify Live ECharts markLine separation
        driver.execute_script("document.querySelector('[data-format-preset=\"1080p\"]')?.click();")
        time.sleep(0.35)
        driver.switch_to.frame("va-stage-portal")
        try:
            ml = driver.execute_script(
                "const ec=window.echarts||window.parent?.echarts;"
                "const c=document.querySelector('#v20-trace .qe-echarts-host');"
                "const o=ec?.getInstanceByDom(c)?.getOption();"
                "const tx=[...(c?.querySelectorAll('svg text')||[])].map(e=>({t:e.textContent.trim(),top:e.getBoundingClientRect().top,h:e.getBoundingClientRect().height})).filter(x=>x.h>0);"
                "const hi=tx.find(x=>x.t.includes('5.10 V')), lo=tx.find(x=>x.t.includes('4.90 V'));"
                "return {pos:(o?.series||[]).find(s=>s.markLine&&s.markLine.data)?.markLine?.data.map(m=>({n:m.name,p:m.label?.position}))||[], gap: (hi&&lo)?Math.abs(lo.top-hi.top):0};"
            )
            pos_map = {m["n"]: m["p"] for m in ml["pos"]}
            self.assertEqual(pos_map.get("+2% · 5.10 V"), "insideEndTop")
            self.assertEqual(pos_map.get("-2% · 4.90 V"), "insideEndBottom")
            self.assertGreaterEqual(ml["gap"], 12.0, f"ECharts +/-2% labels too close: {ml}")
        finally:
            driver.switch_to.default_content()

        # v06: >= 4 OOD rows visible above 900px fold with single-line headers
        driver.get(f"{base_url}?world=02-cloud-cyber-and-ai-ops&view=v06-ai-drift-and-lineage-ide&theme=white")
        self._wait_view(driver, "v06-ai-drift-and-lineage-ide")
        driver.switch_to.frame("va-stage-portal")
        try:
            v06 = driver.execute_script(
                """
                const visRows = [...document.querySelectorAll('#v06-ood-samples tbody tr')].filter(r => r.getBoundingClientRect().bottom <= 900).length;
                const hdrHeights = [...document.querySelectorAll('#v06-ood-samples thead th')].map(th => th.getBoundingClientRect().height);
                return { visRows, maxHdrH: Math.max(...hdrHeights) };
                """
            )
            self.assertGreaterEqual(v06["visRows"], 4, f"Expected >=4 OOD rows above 900px fold, got {v06}")
            self.assertLessEqual(v06["maxHdrH"], 34.0, f"v06 table headers wrapped vertically: {v06}")
        finally:
            driver.switch_to.default_content()

        # v18: natural subtitle + Primary Bedroom replacing duplicate Home Battery tile
        driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&vp=fill&theme=white")
        self._wait_view(driver, "v18-home-assistant-companion-console")
        driver.switch_to.frame("va-stage-portal")
        try:
            v18 = driver.execute_script(
                "const sub = document.querySelector('.v9-view-v18 .v9-masthead-sub')?.textContent || '';"
                "const rooms = [...document.querySelectorAll('#v18-rooms .v18-mush-card')].map(c => c.innerText);"
                "return { sub, rooms };"
            )
            self.assertIn("-1.68 kW", v18["sub"])
            self.assertNotIn("exporting 1.68 kW (-1.68 kW)", v18["sub"])
            joined = "\n".join(v18["rooms"])
            self.assertNotIn("Home Battery", joined)
            self.assertIn("Primary Bedroom", joined)
            self.assertIn("20.2 °C", joined)
            self.assertIn("Night setback armed", joined)
        finally:
            driver.switch_to.default_content()

    def test_wave15_cdp_sync_and_polish(self) -> None:
        self._require_or_skip()
        srv, port = start_http_server(REPO_ROOT)
        base_url = f"http://127.0.0.1:{port}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        try:
            self._check_v08_trace_and_q2_binding(driver, base_url)
            self._check_v01_v04_v07_sync(driver, base_url)
            self._check_reworked_boards_polish(driver, base_url)
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
