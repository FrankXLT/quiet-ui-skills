#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""v9.5.0 Regression Suite: OAW Overview Landing, Light Topbar, 1080p Presets, Stepping & Interactive Rail."""

from __future__ import annotations

import os
import re
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


class TestV950LandingPortalAndRail(unittest.TestCase):
    """Static and live CDP checks for Quiet UI v9.5.0 landing, framing presets, stepping, and interactive rail."""

    def test_static_v950_shell_overview_and_svg_fill_safety(self) -> None:
        html_path = REPO_ROOT / "quiet-ui-showcase.html"
        self.assertTrue(html_path.exists(), "quiet-ui-showcase.html missing")
        html = html_path.read_text(encoding="utf-8")
        for token in (
            'data-studio-view="overview"',
            'id="va-tab-overview"',
            'id="va-tab-examples"',
            'id="va-tab-components"',
            'id="va-step-pos"',
            'id="va-format-pills"',
            'id="va-preset-auto-btn"',
            'id="va-studio-landing"',
            'id="va-sheet-auto-preset-btn"',
        ):
            self.assertIn(token, html, f"missing {token} in quiet-ui-showcase.html")
        # Ensure every static <path ...> inside showcase HTML declares an explicit fill attribute.
        bare_paths = [m.group(0) for m in re.finditer(r"<path\b[^>]*>", html) if "fill=" not in m.group(0)]
        self.assertEqual(bare_paths, [], f"paths missing fill= attribute: {bare_paths[:3]}")

    def test_v950_overview_light_portal_stepping_and_rail_cdp(self) -> None:
        require_cdp = os.environ.get("QUIET_REQUIRE_CDP") == "1"
        ok, reason = _can_launch_cdp()
        if not ok:
            if require_cdp:
                self.fail(f"QUIET_REQUIRE_CDP=1 set but Headless Chrome/Selenium unavailable: {reason}")
            self.skipTest(f"CDP v9.5.0 check skipped ({reason})")

        srv, port = start_http_server(REPO_ROOT)
        root_url = f"http://127.0.0.1:{port}"
        base_url = f"{root_url}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        try:
            self._check_overview_and_starters(driver, root_url, base_url)
            self._check_light_topbar_viewports(driver, base_url)
            self._check_1080p_portal_stepping_and_presets(driver, base_url)
            self._check_interactive_rail_and_footer(driver, base_url)
            severe = [
                entry for entry in driver.get_log("browser")
                if entry.get("level") == "SEVERE" and "favicon.ico" not in entry.get("message", "")
            ]
            self.assertEqual(severe, [], f"SEVERE console errors: {severe}")
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()

    def _check_overview_and_starters(self, driver: Any, root_url: str, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.get(base_url)
        time.sleep(0.2)
        state_info = driver.execute_script(
            """
            const root = document.documentElement;
            const land = document.getElementById('va-studio-landing');
            const mat = document.getElementById('va-portal-mat');
            const bar = document.getElementById('va-studio-bar');
            const pills = [...document.querySelectorAll('#va-studio-landing .va-domain-view-btn')];
            const cards = document.querySelectorAll('#va-studio-landing .va-domain-card');
            return {
              mode: root.dataset.studioView,
              landingHeight: land ? land.getBoundingClientRect().height : 0,
              matDisplay: mat ? getComputedStyle(mat).display : '',
              barBg: bar ? getComputedStyle(bar).backgroundColor : '',
              domainCount: cards.length,
              stdCount: document.querySelectorAll('#va-landing-standards .va-standard-card').length,
              viewBtnCount: pills.length,
              overflowX: root.scrollWidth > root.clientWidth + 1,
            };
            """
        )
        self.assertEqual(state_info["mode"], "overview")
        self.assertGreater(state_info["landingHeight"], 400)
        self.assertEqual(state_info["matDisplay"], "none")
        self.assertEqual(state_info["barBg"], "rgb(255, 255, 255)")
        self.assertEqual(state_info["domainCount"], 6)
        self.assertEqual(state_info["stdCount"], 4)
        self.assertEqual(state_info["viewBtnCount"], 21)
        self.assertFalse(state_info["overflowX"], "landing page horizontal overflow at 1440px")

        for morph_mode in ("paper", "mobile", "dark", "brief", "screen"):
            res = driver.execute_script(
                """
                const m = arguments[0];
                const btn = document.querySelector('[data-morph-btn="' + m + '"]');
                if (btn) btn.click();
                const c = document.getElementById('va-morph-canvas');
                return {
                  mode: c ? c.dataset.morphMode : '',
                  pressed: btn ? btn.getAttribute('aria-pressed') : '',
                };
                """,
                morph_mode,
            )
            self.assertEqual(res["mode"], morph_mode)
            self.assertEqual(res["pressed"], "true")

        slider_res = driver.execute_script(
            """
            const sl = document.getElementById('va-morph-threshold');
            const fire = (v) => { sl.value = String(v); sl.dispatchEvent(new Event('input', { bubbles: true })); };
            fire(60);
            const nomState = document.getElementById('va-morph-status-pill').dataset.state;
            const nomMargin = document.getElementById('va-morph-margin-val').textContent;
            const nomLbl = document.getElementById('va-morph-thresh-label').textContent;
            fire(90);
            const warnState = document.getElementById('va-morph-status-pill').dataset.state;
            const warnMargin = document.getElementById('va-morph-margin-val').textContent;
            return { nomState, nomMargin, nomLbl, warnState, warnMargin };
            """
        )
        self.assertEqual(slider_res["nomState"], "nominal")
        self.assertIn("+3.5 mmHg", slider_res["nomMargin"])
        self.assertIn("60 mmHg", slider_res["nomLbl"])
        self.assertEqual(slider_res["warnState"], "warn")
        self.assertIn("-26.5 mmHg", slider_res["warnMargin"])

        for rel, expected_cnt in (("customizations/personal-starter/showcase.html", 21), ("customizations/brand-starter/showcase.html", 17)):
            driver.get(f"{root_url}/{rel}")
            time.sleep(0.2)
            cnt = driver.execute_script(
                "return document.documentElement.dataset.studioView === 'overview' ? document.querySelectorAll('#va-studio-landing .va-domain-view-btn').length : -1;"
            )
            self.assertEqual(int(cnt), expected_cnt, f"starter {rel} landing view button mismatch")

    def _check_light_topbar_viewports(self, driver: Any, base_url: str) -> None:
        for vp_w, vp_h in ((390, 844), (840, 1050), (1440, 900), (1920, 1080), (3840, 2160)):
            set_viewport(driver, vp_w, vp_h, 1)
            for suffix in ("", "?mode=examples"):
                driver.get(f"{base_url}{suffix}")
                time.sleep(0.18)
                res = driver.execute_script(
                    """
                    const b = document.getElementById('va-studio-bar');
                    return {
                      bg: getComputedStyle(b).backgroundColor,
                      h: b.getBoundingClientRect().height,
                      barOverflow: b.scrollWidth > b.clientWidth + 1,
                      rootOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
                    };
                    """
                )
                self.assertEqual(res["bg"], "rgb(255, 255, 255)", f"non-white topbar at {vp_w}{suffix}")
                self.assertLessEqual(res["h"], 48.5, f"topbar height > 48.5 at {vp_w}{suffix}")
                self.assertFalse(res["barOverflow"] or res["rootOverflow"], f"horizontal overflow at {vp_w}{suffix}")

    def _wait_iframe_view(self, driver: Any, expected_view: str) -> None:
        for _ in range(40):
            cur = driver.execute_script(
                "const d=document.getElementById('va-stage-portal')?.contentDocument;"
                "return d?.getElementById('va-stage-main')?.children.length ? (d.documentElement?.dataset?.view || '') : '';"
            )
            if cur == expected_view:
                return
            time.sleep(0.05)
        self.fail(f"timed out waiting for iframe view {expected_view}")

    def _check_1080p_portal_stepping_and_presets(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        driver.get(base_url)
        time.sleep(0.18)
        driver.execute_script("document.getElementById('va-tab-examples').click();")
        self._wait_iframe_view(driver, "v01-icu-bedside-terminal")
        init = driver.execute_script(
            """
            const s = window.QuietStudioPortalV9.state;
            const mat = document.getElementById('va-portal-mat');
            const scaler = document.getElementById('va-portal-scaler');
            return {
              studioView: document.documentElement.dataset.studioView,
              vp: s.vp,
              pos: document.getElementById('va-step-pos').textContent.trim(),
              matBg: getComputedStyle(mat).backgroundColor,
              frame: scaler.dataset.portalFrame,
            };
            """
        )
        self.assertEqual(init["studioView"], "examples")
        self.assertEqual(init["vp"], "1920x1080")
        self.assertEqual(init["pos"], "1 / 21")
        self.assertEqual(init["matBg"], "rgb(226, 232, 240)")
        self.assertEqual(init["frame"], "screen")

        visited: list[dict[str, str]] = []
        for step_idx in range(21):
            snap = driver.execute_script(
                """
                const api = window.QuietStudioPortalV9;
                return {
                  pos: document.getElementById('va-step-pos').textContent.trim(),
                  domain: api.state.world,
                  hasDomainSel: !!document.getElementById('va-domain-select'),
                  optgroups: document.querySelectorAll('#va-view-select optgroup').length,
                  view: api.state.view,
                  vp: api.state.vp,
                  medium: api.state.medium,
                  theme: api.state.theme,
                  frame: document.getElementById('va-portal-scaler').dataset.portalFrame || '',
                };
                """
            )
            self.assertEqual(snap["pos"], f"{step_idx + 1} / 21")
            self.assertFalse(snap["hasDomainSel"])
            self.assertEqual(snap["optgroups"], 6)
            visited.append(snap)
            driver.execute_script("document.getElementById('va-step-next').click();")
            time.sleep(0.08)

        wrapped_view = driver.execute_script("return window.QuietStudioPortalV9.state.view;")
        self.assertEqual(wrapped_view, "v01-icu-bedside-terminal", "wraparound failed to return to v01")
        self.assertEqual(len({v["view"] for v in visited}), 21)
        self.assertEqual(len({v["domain"] for v in visited}), 6)
        frames = {v["frame"] for v in visited}
        themes = {v["theme"] for v in visited}
        self.assertTrue({"screen", "paper", "mobile"}.issubset(frames), f"missing curated frames: {frames}")
        self.assertTrue({"white", "paper", "dark-paper", "dark"}.issubset(themes), f"missing curated themes: {themes}")
        paper_v02 = next(v for v in visited if v["view"] == "v02-trial-regulatory-brief")
        self.assertEqual((paper_v02["vp"], paper_v02["medium"], paper_v02["theme"]), ("1056x1368", "m1", "paper"))

        # Test manual override lock + Auto Preset reset & stepView preset-carryover reset
        driver.execute_script("document.querySelector('[data-format-preset=\"fill\"]').click();")
        time.sleep(0.08)
        locked = driver.execute_script(
            "return {locked: window.QuietStudioPortalV9.state.presetLocked, btnHidden: document.getElementById('va-preset-auto-btn').hidden, vp: window.QuietStudioPortalV9.state.vp};"
        )
        self.assertTrue(locked["locked"])
        self.assertFalse(locked["btnHidden"])
        self.assertEqual(locked["vp"], "fill")

        driver.execute_script("document.getElementById('va-preset-auto-btn').click();")
        time.sleep(0.08)
        unlocked = driver.execute_script(
            "return {locked: window.QuietStudioPortalV9.state.presetLocked, btnHidden: document.getElementById('va-preset-auto-btn').hidden, vp: window.QuietStudioPortalV9.state.vp};"
        )
        self.assertFalse(unlocked["locked"])
        self.assertTrue(unlocked["btnHidden"])
        self.assertEqual(unlocked["vp"], "1920x1080")

        driver.execute_script("document.querySelector('[data-format-preset=\"paper\"]').click();")
        time.sleep(0.08)
        driver.execute_script("document.getElementById('va-step-next').click();")
        time.sleep(0.08)
        driver.execute_script("document.getElementById('va-step-next').click();")
        time.sleep(0.08)
        after_step = driver.execute_script(
            "const s=window.QuietStudioPortalV9.state;return {locked: s.presetLocked, view: s.view, vp: s.vp, theme: s.theme};"
        )
        self.assertFalse(after_step["locked"])
        self.assertEqual((after_step["view"], after_step["vp"], after_step["theme"]), ("v03-patient-recovery-companion", "390x844", "white"))

        # Verify legacy deep links keep vp='fill' unless specified
        driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
        self._wait_iframe_view(driver, "v01-icu-bedside-terminal")
        self.assertEqual(driver.execute_script("return window.QuietStudioPortalV9.state.vp;"), "fill")

    def _check_interactive_rail_and_footer(self, driver: Any, base_url: str) -> None:
        set_viewport(driver, 1440, 900, 1)
        # 1. N3 view (v01) -> topbar rail collapse, section focus + Show Full View, footer sync
        driver.get(base_url)
        time.sleep(0.15)
        driver.execute_script("window.QuietStudioPortalV9.openExamples('01-clinical-icu-and-trials', 'v01-icu-bedside-terminal');")
        self._wait_iframe_view(driver, "v01-icu-bedside-terminal")
        time.sleep(0.25)

        driver.switch_to.frame("va-stage-portal")
        try:
            driver.execute_script("document.getElementById('va-topbar-rail-toggle').click();")
            self.assertEqual(driver.execute_script("return document.documentElement.dataset.railCollapsed;"), "true")
            driver.execute_script("document.getElementById('va-topbar-rail-toggle').click();")
            self.assertEqual(driver.execute_script("return document.documentElement.dataset.railCollapsed;"), "false")

            rail_diag = driver.execute_script(
                "const r=document.getElementById('va-shell-rail'),links=[...document.querySelectorAll('#va-shell-rail .va-rail-link')];"
                "if(links[1])links[1].click();const dBtn=document.querySelector('.qe-scope-preset-bar [data-scope-preset=\"dropout\"]');if(dBtn)dBtn.click();"
                "const visCol=[document.getElementById('va-topbar-rail-toggle'),...document.querySelectorAll('.va-rail-brand .va-rail-collapse-btn')].filter(el=>el&&el.getBoundingClientRect().width>0);"
                "return {sw: r.scrollWidth, cw: r.clientWidth, brandBtn: document.querySelectorAll('.va-rail-brand .va-rail-collapse-btn').length, visCol: visCol.length, hidden: document.querySelectorAll('[data-rail-hidden]').length, spot: document.querySelectorAll('.is-rail-spotlight').length, ro: (document.querySelector('.qe-scope-readout')||{}).textContent||''};"
            )
            self.assertLessEqual(rail_diag["sw"], rail_diag["cw"] + 1)
            self.assertEqual(rail_diag["brandBtn"], 0)
            self.assertEqual(rail_diag["visCol"], 1)
            self.assertEqual(rail_diag["hidden"], 0)
            self.assertGreaterEqual(rail_diag["spot"], 1)
            self.assertIn("6.50", rail_diag["ro"])
            footer_h = float(driver.execute_script("return document.querySelector('#va-shell-rail .va-rail-footer').getBoundingClientRect().height;"))
            self.assertLessEqual(footer_h, 48.0)
            driver.execute_script("document.querySelector('#va-shell-rail .va-swatch-btn[data-swatch=\"dark-paper\"]').click();")
            driver.execute_script("document.querySelector('#va-shell-rail [data-density=\"compact\"]').click();")
            time.sleep(0.1)
        finally:
            driver.switch_to.default_content()

        synced = driver.execute_script(
            "const s=window.QuietStudioPortalV9.state,sc=document.getElementById('va-portal-scaler');"
            "return {theme: s.theme, density: s.density, locked: s.presetLocked, sl: sc.scrollLeft, st: sc.scrollTop};"
        )
        self.assertEqual(synced, {"theme": "dark-paper", "density": "d3", "locked": True, "sl": 0, "st": 0})

        # 2. N1 view (v19 Roadmap & Triage) -> rail collapse + reopen button + Quick Switch tree
        driver.execute_script("window.QuietStudioPortalV9.openExamples('02-cloud-cyber-and-ai-ops', 'v19-product-roadmap-and-triage');")
        self._wait_iframe_view(driver, "v19-product-roadmap-and-triage")
        time.sleep(0.25)
        driver.switch_to.frame("va-stage-portal")
        try:
            driver.execute_script("document.querySelector('#va-shell-rail .va-rail-collapse-btn').click();")
            time.sleep(0.1)
            reopen_vis = driver.execute_script(
                "const b=document.getElementById('va-rail-reopen-btn');return {c: document.documentElement.dataset.railCollapsed, w: b.getBoundingClientRect().width};"
            )
            self.assertEqual(reopen_vis["c"], "true")
            self.assertGreater(reopen_vis["w"], 20)
            driver.execute_script("document.getElementById('va-rail-reopen-btn').click();")
            self.assertEqual(driver.execute_script("return document.documentElement.dataset.railCollapsed;"), "false")

            driver.execute_script("document.querySelector('#va-shell-rail .va-tree-caret').click();")
            self.assertTrue(driver.execute_script("return document.querySelector('#va-shell-rail .va-tree-children').hidden;"))
            driver.execute_script("document.querySelector('#va-shell-rail .va-tree-caret').click();")
            driver.execute_script("document.querySelector('#va-shell-rail [data-quick-idx=\"1\"]').click();")
            time.sleep(0.1)
            quick_on = driver.execute_script("return document.querySelector('#va-shell-rail [data-quick-idx=\"1\"]').classList.contains('is-active');")
            self.assertTrue(quick_on)
        finally:
            driver.switch_to.default_content()

        # 3. Verify mobile bezel content-box (no 8px clipping) & v01 collapsed -> v06 aria-expanded reset + @layer utilities single-col focus
        driver.execute_script("document.querySelector('[data-format-preset=\"mobile\"]').click();")
        time.sleep(0.15)
        bezel = driver.execute_script(
            "const sc=document.getElementById('va-portal-scaler'), fr=document.getElementById('va-stage-portal').getBoundingClientRect();"
            "return {cw: sc.clientWidth, ch: sc.clientHeight, fw: fr.width, fh: fr.height};"
        )
        self.assertLessEqual(abs(bezel["cw"] - bezel["fw"]), 1.5, f"mobile bezel clipped horizontally: {bezel}")
        self.assertLessEqual(abs(bezel["ch"] - bezel["fh"]), 1.5, f"mobile bezel clipped vertically: {bezel}")

        driver.execute_script("window.QuietStudioPortalV9.openExamples('01-clinical-icu-and-trials', 'v01-icu-bedside-terminal');")
        self._wait_iframe_view(driver, "v01-icu-bedside-terminal")
        driver.switch_to.frame("va-stage-portal")
        try:
            driver.execute_script("document.getElementById('va-topbar-rail-toggle').click();")
            self.assertEqual(driver.execute_script("return document.getElementById('va-topbar-rail-toggle').getAttribute('aria-expanded');"), "false")
        finally:
            driver.switch_to.default_content()

        driver.execute_script("window.QuietStudioPortalV9.openExamples('02-cloud-cyber-and-ai-ops', 'v06-ai-drift-and-lineage-ide');")
        self._wait_iframe_view(driver, "v06-ai-drift-and-lineage-ide")
        time.sleep(0.25)
        driver.switch_to.frame("va-stage-portal")
        try:
            t_exp = driver.execute_script("return document.getElementById('va-topbar-rail-toggle').getAttribute('aria-expanded');")
            self.assertEqual(t_exp, "true", "stale aria-expanded across view switch")
            driver.execute_script(
                "const lnk=document.querySelector('#va-shell-rail .va-rail-link[data-rail-anchor=\"v06-cal\"]');if(lnk)lnk.click();"
            )
            time.sleep(0.12)
            v06_diag = driver.execute_script(
                "const cal=document.getElementById('v06-cal'),lin=document.getElementById('v06-lineage');"
                "return {spot: !!cal && cal.classList.contains('is-rail-spotlight'), linVis: !!lin && lin.getBoundingClientRect().height > 10, hidden: document.querySelectorAll('[data-rail-hidden]').length};"
            )
            self.assertTrue(v06_diag["spot"])
            self.assertTrue(v06_diag["linVis"])
            self.assertEqual(v06_diag["hidden"], 0)
        finally:
            driver.switch_to.default_content()

        driver.execute_script("window.QuietStudioPortalV9.openExamples('01-clinical-icu-and-trials', 'v02-trial-regulatory-brief');")
        self._wait_iframe_view(driver, "v02-trial-regulatory-brief")
        driver.switch_to.frame("va-stage-portal")
        try:
            r_res = driver.execute_script(
                "const row=document.querySelector('.qe-table tbody tr');if(row)row.click();"
                "const ins=document.querySelector('.qe-row-inspector');"
                "return {sel: !!row && row.classList.contains('is-selected-row'), vis: !!ins && !ins.hasAttribute('hidden'), txt: ins ? ins.textContent : ''};"
            )
            self.assertTrue(r_res["sel"])
            self.assertTrue(r_res["vis"])
            self.assertIn("Selected Record", r_res["txt"])
        finally:
            driver.switch_to.default_content()

        driver.execute_script("window.QuietStudioPortalV9.openExamples('03-industrial-grid-and-manufacturing', 'v07-grid-scada-poi-console');")
        self._wait_iframe_view(driver, "v07-grid-scada-poi-console")
        driver.switch_to.frame("va-stage-portal")
        try:
            n_res = driver.execute_script(
                "const btn=document.querySelector('#v07-node-chips [data-v07-node=\"bess\"]');if(btn)btn.click();"
                "return {hi: document.querySelectorAll('.qe-scalar-card.is-node-highlight').length, diag: (document.getElementById('v07-node-diag')||{}).textContent||''};"
            )
            self.assertGreaterEqual(n_res["hi"], 1)
            self.assertIn("78.4%", n_res["diag"])
        finally:
            driver.switch_to.default_content()



if __name__ == "__main__":
    unittest.main()
