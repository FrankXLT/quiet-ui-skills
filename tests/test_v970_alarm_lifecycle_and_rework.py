# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.7.0 Wave 1 tests: 4-phase alarm lifecycle, Single Control Home N2, and console rework."""

from __future__ import annotations

import json
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


class TestWave1Contracts(unittest.TestCase):
    """Static verification of Specimen 50, WF-09 docs, CSS fallbacks, and expanded tables."""

    def test_specimen_50_wf09_and_table_densities(self) -> None:
        bench_html = (REPO_ROOT / "docs" / "bench" / "evidence-bench.html").read_text("utf-8")
        self.assertIn('id="ui-alarm-lifecycle"', bench_html)
        self.assertIn("ISA-18.2 / IEC 60601-1-8", bench_html)

        wf_text = (REPO_ROOT / "docs" / "WORKFLOWS.md").read_text("utf-8")
        self.assertLessEqual(len(wf_text.splitlines()), 450)
        self.assertIn("Workflow WF-09", wf_text)
        self.assertIn("Calm Baseline", wf_text)
        self.assertIn("Acknowledge Alarm", wf_text)

        css_text = (REPO_ROOT / "src" / "css" / "19-alarm-lifecycle.css").read_text("utf-8")
        self.assertIn("prefers-reduced-motion: reduce", css_text)
        self.assertIn("@media print", css_text)
        self.assertNotIn("!important", css_text)

        table_checks = (
            ("01-clinical-icu-and-trials/evidence/v02_trial_adverse_events_table.json", 10),
            ("02-cloud-cyber-and-ai-ops/evidence/v06_ood_drift_samples_table.json", 10),
            ("04-civic-finance-and-stem-learning/evidence/v10_civic_budget_table.json", 10),
            ("06-smart-home-and-energy/evidence/v18_zone_device_and_sensor_table.json", 11),
        )
        for rel, exp_n in table_checks:
            spec = json.loads((REPO_ROOT / "content" / "corpora" / rel).read_text("utf-8"))
            self.assertEqual(len(spec["rows"]), exp_n, f"{rel} row count mismatch")
        v18_spec = json.loads(
            (REPO_ROOT / "content/corpora/06-smart-home-and-energy/evidence/v18_zone_device_and_sensor_table.json").read_text("utf-8")
        )
        self.assertIn("Water Leak", v18_spec["rows"][4]["device_id"])


class TestWave1CDP(unittest.TestCase):
    """Live Chrome CDP suite for automated 4-phase alarm sequences and reworked studio views."""

    def _require_or_skip(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise AssertionError("QUIET_REQUIRE_CDP=1 requires selenium")
            self.skipTest("selenium not installed")
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
                time.sleep(0.12)
                return
            time.sleep(0.06)
        self.fail(f"Timed out waiting for view '{view_id}'")

    def _check_specimen_50(self, driver: Any, root_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.get(f"{root_url}/docs/bench/evidence-bench.html?theme=white#ui-alarm-lifecycle")
        time.sleep(0.35)
        res = driver.execute_script(
            """
            const card = document.querySelector('#ui-alarm-lifecycle .va-alarm-console');
            if (!card) return 'missing card';
            const jump3 = card.querySelector('[data-alarm-jump="unack"]');
            jump3.click();
            const phase3 = card.getAttribute('data-alarm-phase');
            const ackBtn = card.querySelector('[data-alarm-ack]');
            const ackRect = ackBtn ? ackBtn.getBoundingClientRect() : {height: 0};
            const hasDelta = !!card.querySelector('[data-alarm-delta]');
            const hasSvg = !!card.querySelector('svg.va-alarm-focus-svg');
            const sibs = card.querySelectorAll('.va-alarm-sibling-chip').length;
            ackBtn.click();
            const phase4 = card.getAttribute('data-alarm-phase');
            return {phase3, phase4, ackH: ackRect.height, hasDelta, hasSvg, sibs};
            """
        )
        self.assertIsInstance(res, dict, f"Specimen 50 script error: {res}")
        self.assertEqual(res["phase3"], "unack")
        self.assertEqual(res["phase4"], "ack")
        self.assertGreaterEqual(res["ackH"], 44.0)
        self.assertTrue(res["hasDelta"] and res["hasSvg"])
        self.assertEqual(res["sibs"], 3)

    def _check_alarm_views_and_auto(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        # 1. Auto sequence on v08: opens Calm, crosses threshold ~4s into Autonomous Alarm Takeover, Ack restores
        driver.get(f"{base_url}?world=03-industrial-grid-and-manufacturing&view=v08-plant-floor-wall-kiosk&theme=white")
        self._wait_view(driver, "v08-plant-floor-wall-kiosk")
        driver.switch_to.frame("va-stage-portal")
        try:
            init_ph = driver.execute_script("return document.querySelector('.va-alarm-console').getAttribute('data-alarm-phase');")
            self.assertEqual(init_ph, "nominal", "v08 should start in Calm Baseline")
            deadline = time.time() + 6.5
            reached = []
            while time.time() < deadline:
                ph = driver.execute_script("return document.querySelector('.va-alarm-console').getAttribute('data-alarm-phase');")
                if not reached or reached[-1] != ph:
                    reached.append(ph)
                if ph == "unack":
                    break
                time.sleep(0.25)
            self.assertIn("approaching", reached, f"v08 skipped Pre-Breach Approach: {reached}")
            self.assertEqual(reached[-1], "unack", f"v08 did not reach Takeover: {reached}")
            driver.execute_script("document.querySelector('[data-alarm-ack]').click();")
            time.sleep(0.15)
            self.assertEqual(
                driver.execute_script("return document.querySelector('.va-alarm-console').getAttribute('data-alarm-phase');"),
                "ack",
            )
            driver.execute_script("document.querySelector('[data-alarm-replay]').click();")
            time.sleep(0.15)
            self.assertEqual(
                driver.execute_script("return document.querySelector('.va-alarm-console').getAttribute('data-alarm-phase');"),
                "nominal",
            )
        finally:
            driver.switch_to.default_content()

        # 2. v07 opens directly in Phase 4 Acknowledged Diagnostic with Replay Breach and accurate peak delta
        driver.get(f"{base_url}?world=03-industrial-grid-and-manufacturing&view=v07-grid-scada-poi-console&theme=white")
        self._wait_view(driver, "v07-grid-scada-poi-console")
        driver.switch_to.frame("va-stage-portal")
        try:
            v07_info = driver.execute_script(
                "const c=document.querySelector('.va-alarm-console');"
                "return {ph: c.getAttribute('data-alarm-phase'), rep: !!c.querySelector('[data-alarm-replay]'), txt: c.querySelector('.va-alarm-banner').innerText};"
            )
            self.assertEqual(v07_info["ph"], "ack")
            self.assertTrue(v07_info["rep"])
            self.assertIn("-0.055 Hz", v07_info["txt"])
        finally:
            driver.switch_to.default_content()

        # 3. Deterministic ?alarm=unack hook, keyboard focus restoration on Ack, prototype immunity & Overview cleanup
        driver.get(f"{base_url}?world=03-industrial-grid-and-manufacturing&view=v08-plant-floor-wall-kiosk&alarm=constructor&theme=white")
        self._wait_view(driver, "v08-plant-floor-wall-kiosk")
        driver.switch_to.frame("va-stage-portal")
        try:
            self.assertEqual(driver.execute_script("return document.querySelector('.va-alarm-console').getAttribute('data-alarm-phase');"), "nominal")
        finally:
            driver.switch_to.default_content()
        driver.execute_script("document.getElementById('va-tab-overview').click();")
        time.sleep(0.15)
        ov_cleaned = driver.execute_script("return !document.getElementById('va-stage-portal')?.contentDocument?.querySelector('.va-alarm-console')?.__vaAlarmInst;")
        self.assertTrue(ov_cleaned, "Overview tab should dispose mounted alarm intervals")

        for wid, vid in (
            ("01-clinical-icu-and-trials", "v01-icu-bedside-terminal"),
            ("02-cloud-cyber-and-ai-ops", "v04-sre-incident-workbench"),
        ):
            driver.get(f"{base_url}?world={wid}&view={vid}&alarm=unack&theme=white")
            self._wait_view(driver, vid)
            driver.switch_to.frame("va-stage-portal")
            try:
                info = driver.execute_script(
                    """
                    const c = document.querySelector('.va-alarm-console');
                    const tk = c.querySelector('[data-alarm-takeover]');
                    const ph = c.getAttribute('data-alarm-phase');
                    const visBefore = getComputedStyle(tk).display !== 'none';
                    c.querySelector('[data-alarm-ack]').click();
                    const afterPh = c.getAttribute('data-alarm-phase');
                    const visAfter = getComputedStyle(tk).display !== 'none';
                    const focusOnReplay = !!(document.activeElement && document.activeElement.hasAttribute('data-alarm-replay'));
                    const scalars = [...document.querySelectorAll('.qe-scalar-card')].filter(e => getComputedStyle(e).display !== 'none').length;
                    return {ph, afterPh, visBefore, visAfter, focusOnReplay, scalars};
                    """
                )
                self.assertEqual(info["ph"], "unack")
                self.assertTrue(info["visBefore"])
                self.assertFalse(info["visAfter"])
                self.assertEqual(info["afterPh"], "ack")
                self.assertTrue(info["focusOnReplay"], f"{vid} Ack should restore focus onto Replay Breach")
                if vid == "v01-icu-bedside-terminal":
                    self.assertEqual(info["scalars"], 4, "v01 desktop should show all 4 vital KPI cards")
            finally:
                driver.switch_to.default_content()

    def _check_n2_and_tables(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        for wid, vid in (
            ("01-clinical-icu-and-trials", "v02-trial-regulatory-brief"),
            ("02-cloud-cyber-and-ai-ops", "v05-zero-trust-ato-spec"),
            ("03-industrial-grid-and-manufacturing", "v09-spc-quality-and-modbus-report"),
            ("04-civic-finance-and-stem-learning", "v10-civic-capital-budget-deck"),
            ("02-cloud-cyber-and-ai-ops", "v19-product-roadmap-and-triage"),
        ):
            driver.get(f"{base_url}?world={wid}&view={vid}&theme=white")
            self._wait_view(driver, vid)
            driver.switch_to.frame("va-stage-portal")
            try:
                nav = driver.execute_script(
                    "const r=document.getElementById('va-shell-rail');"
                    "return {eff: document.documentElement.dataset.effectiveNav, disp: r ? getComputedStyle(r).display : 'missing'};"
                )
                self.assertEqual(nav["eff"], "n2", f"{vid} should default to N2")
                self.assertEqual(nav["disp"], "none", f"{vid} should hide sidebar rail under N2")
            finally:
                driver.switch_to.default_content()

        driver.get(f"{base_url}?world=02-cloud-cyber-and-ai-ops&view=v06-ai-drift-and-lineage-ide&theme=white")
        self._wait_view(driver, "v06-ai-drift-and-lineage-ide")
        driver.switch_to.frame("va-stage-portal")
        try:
            v06_t = driver.execute_script(
                "const t=document.querySelector('#v06-lineage table tbody');"
                "const b=t?t.getBoundingClientRect():{width:0,height:0};"
                "return {rows: t?t.querySelectorAll('tr').length:0, w: b.width, h: b.height};"
            )
            self.assertEqual(v06_t["rows"], 10)
            self.assertGreaterEqual(v06_t["w"], 280.0)
            self.assertGreaterEqual(v06_t["h"], 140.0)
        finally:
            driver.switch_to.default_content()

        driver.get(f"{base_url}?world=04-civic-finance-and-stem-learning&view=v10-civic-capital-budget-deck&theme=white")
        self._wait_view(driver, "v10-civic-capital-budget-deck")
        driver.switch_to.frame("va-stage-portal")
        try:
            flt = driver.execute_script(
                """
                const rows = () => [...document.querySelectorAll('#v10-budget-table tbody tr')].filter(r => !r.classList.contains('v10-row-hidden')).length;
                const all1 = rows();
                document.querySelector('#v10-fund-chips [data-fund="inflow"]').click();
                const inf = rows();
                document.querySelector('#v10-fund-chips [data-fund="all"]').click();
                return {all1, inf, all2: rows()};
                """
            )
            self.assertEqual((flt["all1"], flt["all2"]), (10, 10))
            self.assertGreaterEqual(flt["inf"], 3)
            self.assertLess(flt["inf"], 10)
        finally:
            driver.switch_to.default_content()

    def _check_v18_v20_and_handoffs(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&vp=fill&theme=white")
        self._wait_view(driver, "v18-home-assistant-companion-console")
        driver.switch_to.frame("va-stage-portal")
        try:
            v18 = driver.execute_script(
                """
                const e = document.getElementById('v18-energy').getBoundingClientRect();
                const rm = document.getElementById('v18-rooms').getBoundingClientRect();
                const dr = document.getElementById('v18-security').getBoundingClientRect();
                const rows = document.querySelectorAll('#v18-ledger table tbody tr').length;
                return {eTop: e.top, rmTop: rm.top, drTop: dr.top, rows};
                """
            )
            self.assertEqual(v18["rows"], 11)
            self.assertLess(abs(v18["rmTop"] - v18["drTop"]), 8.0, f"v18 rooms/doors should sit side-by-side: {v18}")
            self.assertLess(v18["eTop"], 860.0, f"v18 primary energy plot pushed below 900px fold: {v18}")
        finally:
            driver.switch_to.default_content()

        driver.get(f"{base_url}?world=04-civic-finance-and-stem-learning&view=v20-student-capstone-lab-report&theme=white")
        self._wait_view(driver, "v20-student-capstone-lab-report")
        driver.switch_to.frame("va-stage-portal")
        try:
            v20_data = driver.execute_script(
                "return {body: document.body.innerText, svgTxt: document.querySelector('#v20-trace svg')?.textContent || ''};"
            )
            self.assertIn("0.22", v20_data["body"])
            self.assertIn("7.46", v20_data["body"])
            self.assertIn("5.10 V", v20_data["svgTxt"])
            self.assertIn("4.90 V", v20_data["svgTxt"])
        finally:
            driver.switch_to.default_content()

        driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
        self._wait_view(driver, "v01-icu-bedside-terminal")
        driver.switch_to.frame("va-stage-portal")
        driver.execute_script("document.querySelector('.va-handoff-link').click();")
        driver.switch_to.default_content()
        self._wait_view(driver, "v03-patient-recovery-companion")

        driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v14-fieldbus-and-scope-debugger&theme=white")
        self._wait_view(driver, "v14-fieldbus-and-scope-debugger")
        driver.switch_to.frame("va-stage-portal")
        driver.execute_script("document.querySelector('.va-handoff-link').click();")
        driver.switch_to.default_content()
        self._wait_view(driver, "v21-field-anomaly-escalation-tsn")

    def test_wave1_cdp_lifecycle_and_rework(self) -> None:
        self._require_or_skip()
        srv, port = start_http_server(REPO_ROOT)
        root_url = f"http://127.0.0.1:{port}"
        base_url = f"{root_url}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        try:
            self._check_specimen_50(driver, root_url)
            self._check_alarm_views_and_auto(driver, base_url)
            self._check_n2_and_tables(driver, base_url)
            self._check_v18_v20_and_handoffs(driver, base_url)
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
