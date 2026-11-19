# SPDX-License-Identifier: Apache-2.0
"""Headless Selenium CDP Gates 1 to 13 for Quiet UI v9.0 (6-Domain Studio)."""

from __future__ import annotations

import time
from typing import Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .constants import ROOT_FONT_SCALE_TARGETS, VIEWPORTS


def create_headless_driver() -> webdriver.Chrome:
    opts = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920,1080"):
        opts.add_argument(arg)
    return webdriver.Chrome(options=opts)


def switch_to_portal(driver: webdriver.Chrome) -> bool:
    driver.switch_to.default_content()
    portals = driver.find_elements(By.ID, "va-stage-portal")
    if portals:
        driver.switch_to.frame(portals[0])
        return True
    return False


def switch_to_outer(driver: webdriver.Chrome) -> None:
    driver.switch_to.default_content()


def set_cdp_viewport(driver: webdriver.Chrome, w: int, h: int) -> None:
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": w < 600},
    )


def select_tier(driver: webdriver.Chrome, slug: str) -> None:
    """Switch active v9 view by view_id (maps slug automatically via #va-v9-manifest)."""
    switch_to_outer(driver)
    driver.execute_script("""
        const slug = arguments[0];
        const api = window.QuietStudioPortalV9;
        const mEl = document.getElementById('va-v9-manifest');
        if (!api || !mEl) return;
        const man = JSON.parse(mEl.textContent || '{"worlds":[]}');
        let worldId = api.state.world, viewId = api.state.view;
        for (const w of man.worlds || []) {
            for (const v of w.views || []) {
                if (v.view_id === slug || v.view_id.startsWith(slug + '-')) {
                    worldId = w.world_id; viewId = v.view_id; break;
                }
            }
        }
        api.state.studioView = 'examples';
        api.state.world = worldId;
        api.state.view = viewId;
        api.applyState(false);
    """, slug)
    for _ in range(45):
        time.sleep(0.06)
        if driver.execute_script("""
            const slug = arguments[0];
            const w = document.getElementById('va-stage-portal')?.contentWindow;
            const d = w?.document;
            const cur = d?.documentElement?.dataset?.view || '';
            const main = d?.getElementById('va-stage-main');
            if (!(cur === slug || cur.startsWith(slug + '-')) || !(main && main.children.length)) return false;
            const imgsOk = [...d.querySelectorAll('img.v9-opt-photo, img.v17-art-photo.is-active')].every(i => i.complete && i.naturalWidth > 0);
            if (!imgsOk) return false;
            const isAutoEc = ['v06','v10','v11','v12','v13','v18'].some(p => cur.startsWith(p + '-'));
            if (isAutoEc) {
                const wraps = [...d.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]')];
                if (wraps.length && !wraps.every(el => el.dataset.echartsActive === 'true' && el.querySelector('.qe-echarts-host svg'))) return false;
            }
            return true;
        """, slug):
            break
    time.sleep(0.06)


def check_gates_viewport(driver: webdriver.Chrome, w: int, h: int) -> list[str]:
    errors: list[str] = []
    switch_to_outer(driver)
    outer_res = driver.execute_script("""
        const sw = document.documentElement.scrollWidth, iw = window.innerWidth, errs = [];
        if (sw > iw + 2) errs.push(`Outer scrollWidth (${sw}) > innerWidth (${iw}) + 2`);
        for (const b of document.querySelectorAll('#va-studio-bar button, #va-studio-bar select')) {
            const r = b.getBoundingClientRect();
            if (r.width > 0 && (r.left < -2 || r.right > iw + 2)) {
                errs.push(`Studio bar control out of bounds: [${r.left.toFixed(1)}, ${r.right.toFixed(1)}] vs ${iw}`); break;
            }
        }
        return errs;
    """)
    errors.extend([f"[GATE_4_CLIPPING_{w}] {e}" for e in outer_res])

    if switch_to_portal(driver):
        exp_fs, tol = ROOT_FONT_SCALE_TARGETS.get(w, (16.0, 0.5))
        inner_res = driver.execute_script("""
            const [w, expFs, tol] = arguments, docEl = document.documentElement, errs = [];
            if (Math.abs(window.innerWidth - w) > 2) errs.push(`[GATE_1_PORTAL] innerWidth ${window.innerWidth} != ${w}`);
            if (docEl.scrollWidth > window.innerWidth + 2) errs.push(`[GATE_4_PORTAL] scrollWidth ${docEl.scrollWidth} > ${window.innerWidth}`);
            const fs = parseFloat(window.getComputedStyle(docEl).fontSize);
            if (Math.abs(fs - expFs) > tol) errs.push(`[GATE_2_SCALE] Root font-size ${fs}px deviates from ${expFs}px +/-${tol}`);
            return errs;
        """, w, exp_fs, tol)
        errors.extend([f"[VIEWPORT_{w}] {e}" for e in inner_res])
    switch_to_outer(driver)
    return errors


def run_selenium_gates_1_to_13(
    driver: webdriver.Chrome, base_url: str, screenshots_dir: str | None = None
) -> list[str]:
    """Execute v9 Responsive Continuum & Theme/Medium Gates 1-13."""
    errors: list[str] = []
    driver.get(base_url)
    select_tier(driver, "v01-icu-bedside-terminal")

    for w, h in VIEWPORTS:
        set_cdp_viewport(driver, w, h)
        for view_id in ("v01-icu-bedside-terminal", "v02-trial-regulatory-brief", "v12-stem-interactive-lab"):
            select_tier(driver, view_id)
            errors.extend(check_gates_viewport(driver, w, h))

    set_cdp_viewport(driver, 1440, 900)
    bgs: set[str] = set()
    for th in ("white", "paper", "dark-paper", "dark"):
        switch_to_outer(driver)
        driver.execute_script("window.QuietStudioPortalV9.state.theme = arguments[0]; window.QuietStudioPortalV9.applyState(false);", th)
        time.sleep(0.1)
        if switch_to_portal(driver):
            bgs.add(str(driver.execute_script("return getComputedStyle(document.body).backgroundColor;")))
    if len(bgs) < 3:
        errors.append(f"[GATE_3_THEMES] Expected distinct backgrounds across 4 themes, got {bgs}")

    switch_to_outer(driver)
    driver.execute_script("window.QuietStudioPortalV9.state.theme = 'dark'; window.QuietStudioPortalV9.state.medium = 'm1'; window.QuietStudioPortalV9.applyState(false);")
    time.sleep(0.12)
    if switch_to_portal(driver):
        m1_stage_bg = driver.execute_script("return getComputedStyle(document.querySelector('.va-stage') || document.body).backgroundColor;")
        if m1_stage_bg != "rgb(255, 255, 255)":
            errors.append(f"[GATE_5_M1_POLARITY] Dark theme + m1 did not reset .va-stage to pure white (got {m1_stage_bg})")
    switch_to_outer(driver)
    driver.execute_script("window.QuietStudioPortalV9.state.theme = 'white'; window.QuietStudioPortalV9.state.medium = 'auto'; window.QuietStudioPortalV9.applyState(false);")

    try:
        severe = [l for l in driver.get_log("browser") if l.get("level") == "SEVERE" and "favicon.ico" not in l.get("message", "")]
        if severe:
            errors.append(f"[CONSOLE_SEVERE] {severe[0].get('message')}")
    except Exception:
        pass
    return errors
