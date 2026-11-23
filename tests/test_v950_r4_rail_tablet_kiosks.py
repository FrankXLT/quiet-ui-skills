#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""v9.5.0 R4 Regression Suite: Pinned Sticky Rail, Tablet (1280x800) Frame & Full-Bleed Kiosks."""

from __future__ import annotations

import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from cdp_gates import REPO_ROOT, create_headless_driver, set_viewport, start_http_server  # noqa: E402


def _can_launch_cdp() -> tuple[bool, str]:
    if os.environ.get("QUIET_SKIP_CDP") == "1":
        return False, "QUIET_SKIP_CDP=1"
    try:
        drv = create_headless_driver()
        drv.quit()
        return True, ""
    except Exception as exc:
        return False, str(exc)


class TestV950R4RailTabletKiosks(unittest.TestCase):
    """CDP checks for pinned sticky rail, Tablet HMI frame, v08 controls, and full-bleed v16/v17."""

    def _wait_view(self, driver: Any, view_id: str) -> None:
        for _ in range(45):
            cur = driver.execute_script(
                "const d=document.getElementById('va-stage-portal')?.contentDocument;"
                "return d?.getElementById('va-stage-main')?.children.length ? (d.documentElement?.dataset?.view || '') : '';"
            )
            if cur == view_id:
                time.sleep(0.1)
                return
            time.sleep(0.05)
        self.fail(f"timed out waiting for view {view_id}")

    def test_static_r4_line_budgets_and_css_wiring(self) -> None:
        css_p = REPO_ROOT / "src" / "css" / "16-kiosks-and-sticky-rail.css"
        self.assertTrue(css_p.is_file(), "16-kiosks-and-sticky-rail.css missing")
        lines = css_p.read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 340, f"16-kiosks-and-sticky-rail.css too long: {len(lines)}L")
        self.assertNotIn("!important", "\n".join(lines).lower())
        showcase_html = (REPO_ROOT / "quiet-ui-showcase.html").read_text(encoding="utf-8")
        self.assertIn('data-format-preset="tablet"', showcase_html)
        self.assertIn('value="1280x800"', showcase_html)
        self.assertIn("v16-ais-svg", showcase_html)

    def test_r4_sticky_rail_tablet_v08_and_fullbleed_kiosks_cdp(self) -> None:
        require_cdp = os.environ.get("QUIET_REQUIRE_CDP") == "1"
        ok, reason = _can_launch_cdp()
        if not ok:
            if require_cdp:
                self.fail(f"QUIET_REQUIRE_CDP=1 set but Headless Chrome/Selenium unavailable: {reason}")
            self.skipTest(f"CDP R4 check skipped ({reason})")

        srv, port = start_http_server(REPO_ROOT)
        base_url = f"http://127.0.0.1:{port}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        try:
            self._check_pinned_sticky_rail(driver, base_url)
            self._check_tablet_frame_v08_and_preset_reset(driver, base_url)
            self._check_fullbleed_v16_and_v17(driver, base_url)
            severe = [
                e for e in driver.get_log("browser")
                if e.get("level") == "SEVERE" and "favicon.ico" not in e.get("message", "")
            ]
            self.assertEqual(severe, [], f"SEVERE console errors: {severe}")
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()

    def _check_pinned_sticky_rail(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1920, 1080, 1)
        for world_id, view_id, expect_top in (
            ("01-clinical-icu-and-trials", "v01-icu-bedside-terminal", True),
            ("04-civic-finance-and-stem-learning", "v10-civic-capital-budget-deck", False),
        ):
            driver.get(f"{base_url}?world={world_id}&view={view_id}&vp=fill&theme=white")
            self._wait_view(driver, view_id)
            driver.switch_to.frame("va-stage-portal")
            try:
                before = driver.execute_script(
                    """
                    const r = document.getElementById('va-shell-rail').getBoundingClientRect();
                    const b = document.querySelector('#va-shell-rail .va-rail-brand').getBoundingClientRect();
                    const f = document.querySelector('#va-shell-rail .va-rail-footer').getBoundingClientRect();
                    const links = document.querySelectorAll('#va-shell-rail .va-rail-link');
                    return {
                      h: window.innerHeight,
                      rTop: r.top, rBot: r.bottom,
                      bTop: b.top, fTop: f.top, fBot: f.bottom,
                      nLinks: links.length,
                    };
                    """
                )
                self.assertGreaterEqual(before["bTop"], 0.0)
                self.assertLessEqual(before["fBot"], before["h"] + 1.0, f"{view_id} footer cut off on load: {before}")
                self.assertLessEqual(before["rBot"], before["h"] + 1.0, f"{view_id} rail stretches past viewport: {before}")
                self.assertGreaterEqual(before["nLinks"], 2)

                if expect_top:
                    mid = driver.execute_script(
                        """
                        const ls = document.querySelectorAll('#va-shell-rail .va-rail-link');
                        const lnk = ls[1] || ls[0];
                        lnk.click();
                        return lnk.getAttribute('data-rail-anchor') || '';
                        """
                    )
                    last_top = None
                    for _ in range(25):
                        time.sleep(0.06)
                        cur_top = driver.execute_script(
                            "const t=document.getElementById(arguments[0]);return t?t.getBoundingClientRect().top:null;",
                            mid,
                        )
                        if last_top is not None and cur_top is not None and abs(cur_top - last_top) < 1.0:
                            break
                        last_top = cur_top
                    mid_box = driver.execute_script(
                        """
                        const t = document.getElementById(arguments[0]);
                        const tb = document.getElementById('va-shell-topbar');
                        const r = document.getElementById('va-shell-rail').getBoundingClientRect();
                        return {
                          tTop: t ? t.getBoundingClientRect().top : -99,
                          tbBot: tb ? tb.getBoundingClientRect().bottom : 0,
                          rTop: r.top,
                        };
                        """,
                        mid,
                    )
                    self.assertGreaterEqual(mid_box["rTop"], -1.0, f"{view_id} rail left viewport on mid click: {mid_box}")
                    self.assertGreaterEqual(mid_box["tTop"], mid_box["tbBot"] + 4.0, f"{view_id} anchor obscured by sticky topbar: {mid_box}")

                driver.execute_script(
                    "const ls=document.querySelectorAll('#va-shell-rail .va-rail-link');ls[ls.length-1].click();"
                )
                for _ in range(25):
                    sy = float(driver.execute_script("return window.scrollY || 0;"))
                    if sy > 100.0:
                        break
                    time.sleep(0.05)

                after = driver.execute_script(
                    """
                    const r = document.getElementById('va-shell-rail').getBoundingClientRect();
                    const b = document.querySelector('#va-shell-rail .va-rail-brand').getBoundingClientRect();
                    const f = document.querySelector('#va-shell-rail .va-rail-footer').getBoundingClientRect();
                    const tb = document.getElementById('va-shell-topbar');
                    const tbr = tb ? tb.getBoundingClientRect() : {top: 0, bottom: 0};
                    return {
                      h: window.innerHeight, sy: window.scrollY || 0,
                      rTop: r.top, rBot: r.bottom,
                      bTop: b.top, fBot: f.bottom,
                      tbTop: tbr.top, tbBot: tbr.bottom,
                    };
                    """
                )
                self.assertGreater(after["sy"], 100.0, f"{view_id} did not scroll stage: {after}")
                self.assertGreaterEqual(after["rTop"], -1.0, f"{view_id} rail scrolled off top: {after}")
                self.assertGreaterEqual(after["bTop"], 0.0, f"{view_id} rail brand clipped off top: {after}")
                self.assertLessEqual(after["fBot"], after["h"] + 1.0, f"{view_id} rail footer cut off after scroll: {after}")
                if expect_top:
                    self.assertGreaterEqual(after["tbTop"], -0.5)
                    self.assertLessEqual(after["tbBot"], 48.0)
            finally:
                driver.switch_to.default_content()

    def _check_tablet_frame_v08_and_preset_reset(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.get(base_url)
        time.sleep(0.15)
        driver.execute_script(
            "window.QuietStudioPortalV9.openExamples('03-industrial-grid-and-manufacturing', 'v07-grid-scada-poi-console');"
        )
        self._wait_view(driver, "v07-grid-scada-poi-console")

        # Click Tablet pill on v07, verify bezel, then lock Paper and step > to v08
        driver.execute_script("document.querySelector('[data-format-preset=\"tablet\"]').click();")
        time.sleep(0.12)
        tab_info = driver.execute_script(
            "const sc=document.getElementById('va-portal-scaler'),fr=document.getElementById('va-stage-portal').getBoundingClientRect();"
            "return {vp: window.QuietStudioPortalV9.state.vp, frame: sc.dataset.portalFrame, cw: sc.clientWidth, fw: fr.width};"
        )
        self.assertEqual(tab_info["vp"], "1280x800")
        self.assertEqual(tab_info["frame"], "tablet")
        self.assertLessEqual(abs(tab_info["cw"] - tab_info["fw"]), 2.0)

        driver.execute_script("document.querySelector('[data-format-preset=\"paper\"]').click();")
        time.sleep(0.1)
        driver.execute_script("document.getElementById('va-step-next').click();")
        self._wait_view(driver, "v08-plant-floor-wall-kiosk")

        v08_state = driver.execute_script(
            "const s=window.QuietStudioPortalV9.state;"
            "return {locked: s.presetLocked, vp: s.vp, theme: s.theme, frame: document.getElementById('va-portal-scaler').dataset.portalFrame};"
        )
        self.assertFalse(v08_state["locked"])
        self.assertEqual(v08_state["vp"], "1280x800")
        self.assertEqual(v08_state["theme"], "dark")
        self.assertEqual(v08_state["frame"], "tablet")

        driver.switch_to.frame("va-stage-portal")
        try:
            res = driver.execute_script(
                """
                const sh = document.documentElement.scrollHeight, ih = window.innerHeight;
                const freqCard = document.querySelector('.v08-kpi-card[data-v08-ch="freq"]');
                freqCard.click();
                const r1 = document.getElementById('v08-ch-readout').textContent;
                document.querySelector('button[data-v08-win="shift"]').click();
                const r2 = document.getElementById('v08-ch-readout').textContent;
                document.getElementById('v08-hold-btn').click();
                const r3 = document.getElementById('v08-ch-readout').textContent;
                const holdAttr = document.querySelector('.v9-view-v08').getAttribute('data-v08-hold');
                return {sh, ih, sel: freqCard.classList.contains('is-v08-selected'), r1, r2, r3, holdAttr};
                """
            )
            self.assertLessEqual(res["sh"], res["ih"] + 16, f"v08 overflows 1280x800 frame: {res}")
            self.assertTrue(res["sel"])
            self.assertIn("CH2 · Grid Frequency", res["r1"])
            self.assertIn("(Shift)", res["r2"])
            self.assertTrue(res["r3"].startswith("HOLD · "))
            self.assertEqual(res["holdAttr"], "true")
        finally:
            driver.switch_to.default_content()

    def _check_fullbleed_v16_and_v17(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1920, 1080, 1)
        driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v16-transparent-window-overlay&vp=fill&theme=dark")
        self._wait_view(driver, "v16-transparent-window-overlay")
        driver.switch_to.frame("va-stage-portal")
        try:
            v16 = driver.execute_script(
                """
                const vp = document.getElementById('v16-glass-viewport');
                const r = vp.getBoundingClientRect();
                const aisBtn = document.getElementById('v16-ais-btn');
                const svg = document.querySelector('.v16-ais-svg');
                return {
                  w: r.width, h: r.height, iw: window.innerWidth, ih: window.innerHeight,
                  dockCount: document.querySelectorAll('.v16-pod-dock').length,
                  aisPressed: aisBtn ? aisBtn.getAttribute('aria-pressed') : '',
                  aisAttr: vp.getAttribute('data-ais'),
                  svgW: svg ? svg.getBoundingClientRect().width : 0,
                };
                """
            )
            self.assertAlmostEqual(v16["w"], v16["iw"], delta=1.5)
            self.assertAlmostEqual(v16["h"], v16["ih"], delta=1.5)
            self.assertEqual(v16["dockCount"], 0)
            self.assertEqual(v16["aisPressed"], "true")
            self.assertEqual(v16["aisAttr"], "true")
            self.assertGreater(v16["svgW"], 1000)
        finally:
            driver.switch_to.default_content()

        driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v17-picture-frame-home-kiosk&vp=fill&theme=paper")
        self._wait_view(driver, "v17-picture-frame-home-kiosk")
        driver.switch_to.frame("va-stage-portal")
        try:
            v17 = driver.execute_script(
                """
                const vp = document.getElementById('v17-kiosk');
                const r = vp.getBoundingClientRect();
                const row = document.querySelector('.v17-comfort-row');
                const txtTop = row.querySelector('span').getBoundingClientRect().top;
                const dnTop = document.getElementById('v17-sp-down').getBoundingClientRect().top;
                const upTop = document.getElementById('v17-sp-up').getBoundingClientRect().top;
                return {
                  w: r.width, h: r.height, iw: window.innerWidth, ih: window.innerHeight,
                  rowH: row.getBoundingClientRect().height,
                  dyDn: Math.abs(dnTop - txtTop), dyUp: Math.abs(upTop - txtTop),
                };
                """
            )
            self.assertAlmostEqual(v17["w"], v17["iw"], delta=1.5)
            self.assertAlmostEqual(v17["h"], v17["ih"], delta=1.5)
            self.assertLessEqual(v17["dyDn"], 8.0, f"v17 setpoint [-] wrapped onto another row: {v17}")
            self.assertLessEqual(v17["dyUp"], 8.0, f"v17 setpoint [+] wrapped onto another row: {v17}")
        finally:
            driver.switch_to.default_content()


if __name__ == "__main__":
    unittest.main()
