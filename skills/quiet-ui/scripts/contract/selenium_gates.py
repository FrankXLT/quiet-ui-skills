# SPDX-License-Identifier: Apache-2.0
"""Headless Selenium CDP Gates 1 to 13 for Quiet UI v8.0."""

from __future__ import annotations

import time
from typing import Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .constants import ROOT_FONT_SCALE_TARGETS, VIEWPORTS


def create_headless_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
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


def select_tier(driver: webdriver.Chrome, slug: str) -> None:
    switch_to_outer(driver)
    driver.execute_script("""
        const s = arguments[0];
        if (typeof switchTier === 'function') switchTier(s);
        else {
            const b = document.querySelector(`[data-tier="${s}"]`);
            if (b) b.click();
            const sel = document.getElementById('va-studio-tier-select');
            if (sel) { sel.value = s; sel.dispatchEvent(new Event('change')); }
        }
    """, slug)
    time.sleep(0.06)


def check_gates_viewport(driver: webdriver.Chrome, w: int, h: int) -> list[str]:
    """Check Gates 1, 2, 4, 6, 8, 9, 10, 11 for the current viewport."""
    errors: list[str] = []
    switch_to_outer(driver)

    outer_res = driver.execute_script("""
        const sw = document.documentElement.scrollWidth, iw = window.innerWidth, errs = [];
        if (sw > iw + 2) errs.push(`Outer scrollWidth (${sw}) > innerWidth (${iw}) + 2`);
        for (const b of document.querySelectorAll('#va-studio-bar button, #va-studio-bar select')) {
            const r = b.getBoundingClientRect();
            if (r.width > 0 && (r.left < -2 || r.right > iw + 2)) {
                errs.push(`Studio bar control out of bounds: [${r.left}, ${r.right}] vs ${iw}`); break;
            }
        }
        return errs;
    """)
    errors.extend([f"[GATE_4_CLIPPING_{w}] {e}" for e in outer_res])

    switch_to_portal(driver)
    exp_fs, tol = ROOT_FONT_SCALE_TARGETS.get(w, (16.0, 0.5))

    inner_res = driver.execute_script("""
        const [w, expFs, tol] = arguments, docEl = document.documentElement, errs = [];
        if (Math.abs(window.innerWidth - w) > 2) errs.push(`[GATE_1_PORTAL] innerWidth ${window.innerWidth} != ${w}`);
        if (docEl.scrollWidth > window.innerWidth + 2) errs.push(`[GATE_4_PORTAL] scrollWidth ${docEl.scrollWidth} > ${window.innerWidth}`);
        const fs = parseFloat(window.getComputedStyle(docEl).fontSize);
        if (Math.abs(fs - expFs) > tol) errs.push(`[GATE_2_SCALE] Root font-size ${fs}px deviates from expected ${expFs}px ±${tol}`);
        if (w < 1100) {
            const r = document.getElementById('va-shell-rail'), d = document.getElementById('va-shell-drawer');
            if (r && r.getBoundingClientRect().width > 0) errs.push(`[GATE_6_DRAWER] Rail width > 0 at ${w}px`);
            if (d && d.getAttribute('closedby') !== 'any') errs.push(`[GATE_6_DRAWER] <dialog> missing closedby="any"`);
        }
        for (const el of document.querySelectorAll('p, span, a, button, th, td, label')) {
            if (el.offsetParent === null) continue;
            const cfs = parseFloat(window.getComputedStyle(el).fontSize);
            if (cfs > 0 && cfs < 10.9) { errs.push(`[GATE_8_FLOOR] Sub-11px font (${cfs}px): ${el.tagName}.${el.className}`); break; }
        }
        if (w === 390) {
            for (const c of document.querySelectorAll('th, td')) {
                if (c.offsetParent === null) continue;
                const cr = c.getBoundingClientRect(), wb = window.getComputedStyle(c).wordBreak;
                if (cr.width < 47) { errs.push(`[GATE_9_TABLE] Cell width ${cr.width.toFixed(1)}px < 48px`); break; }
                if (wb === 'break-all') { errs.push(`[GATE_9_TABLE] Cell word-break: break-all`); break; }
            }
        }
        if (document.querySelector('.va-oa-sidebar-footer')) errs.push('[GATE_10] Forbidden .va-oa-sidebar-footer found');
        if (typeof window.openShellDrawer !== 'function' || typeof window.closeShellDrawer !== 'function') {
            errs.push('[GATE_6_DRAWER] Missing global openShellDrawer/closeShellDrawer handler');
        }
        if (typeof window.setAppTreeMobilePane !== 'function') {
            errs.push('[GATE_6_DRAWER] Missing global setAppTreeMobilePane handler');
        }
        const minH = w <= 390 ? 43 : 24;
        for (const btn of document.querySelectorAll('button, select')) {
            if (btn.offsetParent === null) continue;
            const br = btn.getBoundingClientRect();
            if (br.height > 0 && br.height < minH - 1) {
                errs.push(`[GATE_11_HIT] Control height ${br.height.toFixed(1)}px < ${minH}px (${btn.className})`); break;
            }
        }
        return errs;
    """, w, exp_fs, tol)
    errors.extend(inner_res)

    if w == 390:
        for probe_tier in ("doc-4a", "bridge-1", "app-2", "app-tree", "ctrl-1", "doc-1"):
            select_tier(driver, probe_tier)
            if not switch_to_portal(driver):
                continue
            hit_errs = driver.execute_script("""
                const tier = arguments[0], errs = [];
                for (const btn of document.querySelectorAll('button, select')) {
                    if (btn.offsetParent === null) continue;
                    const br = btn.getBoundingClientRect();
                    if (br.height > 0 && br.height < 42) {
                        errs.push(`[GATE_11_HIT_${tier}] Control height ${br.height.toFixed(1)}px < 43px (${btn.className})`); break;
                    }
                }
                return errs;
            """, probe_tier)
            errors.extend(hit_errs)

    return errors


def check_gates_editorial_and_hinge(driver: webdriver.Chrome, w: int) -> list[str]:
    """Gate 2 editorial measure, Gate 6 820px crease alignment, and Gate 7 SVG aspect."""
    errors: list[str] = []
    for tier in ("doc-1", "doc-4a"):
        select_tier(driver, tier)
        switch_to_portal(driver)
        p_res = driver.execute_script("""
            const w = arguments[0], maxW = w >= 3840 ? 1260 : (w >= 1920 ? 960 : 99999);
            for (const p of document.querySelectorAll('main p, article p')) {
                if (p.offsetParent === null) continue;
                const r = p.getBoundingClientRect();
                if (r.width > maxW + 2) return [`Prose <p> width ${r.width.toFixed(1)}px exceeds ${maxW}px at ${w}px`];
            }
            return [];
        """, w)
        errors.extend([f"[GATE_2_MEASURE_{tier}] {e}" for e in p_res])

    if w == 820:
        for split_tier, split_sel in [("doc-4a", ".doc4a-split"), ("bridge-1", ".bridge1-grid"), ("app-4", ".app4-dual-pane")]:
            select_tier(driver, split_tier)
            switch_to_portal(driver)
            h_res = driver.execute_script("""
                const g = document.querySelector(arguments[0]);
                if (!g || g.children.length < 2) return [];
                const c2 = g.children[1].getBoundingClientRect();
                return Math.abs(c2.left - 410) > 16 ? [`Pane 2 left (${c2.left.toFixed(1)}px) not centered at 410px ±16px`] : [];
            """, split_sel)
            errors.extend([f"[GATE_6_HINGE_{split_tier}] {e}" for e in h_res])

    switch_to_portal(driver)
    svg_res = driver.execute_script("""
        for (const s of document.querySelectorAll('svg')) {
            const r = s.getBoundingClientRect();
            if (r.width > 20 && r.height > 20 && s.viewBox && s.viewBox.baseVal && s.viewBox.baseVal.width > 0) {
                const vb = s.viewBox.baseVal, ratio = (r.width / vb.width) / (r.height / vb.height);
                if (ratio < 0.94 || ratio > 1.06) return [`Distorted SVG aspect ratio: ${ratio.toFixed(3)}`];
            }
        }
        return [];
    """)
    errors.extend([f"[GATE_7_SVG] {e}" for e in svg_res])
    return errors


def check_gate_3_and_5_chrome(driver: webdriver.Chrome, w: int) -> list[str]:
    """Gate 3 100dvh isolation & Gate 5 Single-Bar Chrome Law."""
    errors: list[str] = []
    tiers = ["deck-1", "hud-1"] + (["app-tree"] if w >= 1100 else [])
    for t in tiers:
        select_tier(driver, t)
        switch_to_portal(driver)
        errs = driver.execute_script("""
            const h = window.innerHeight, sh = document.documentElement.scrollHeight;
            return sh > h + 2 ? [`Stage isolation broken: scrollHeight (${sh}) > innerHeight (${h}) + 2`] : [];
        """)
        errors.extend([f"[GATE_3_ISOLATION_{t}] {e}" for e in errs])

    switch_to_portal(driver)
    chrome_errs = driver.execute_script("""
        const isV = el => el && el.offsetParent !== null && el.getBoundingClientRect().height > 0, errs = [];
        if (Array.from(document.querySelectorAll('#va-shell-topbar, .va-shell-topbar, .va-shell-header')).filter(isV).length > 1) errs.push('Multiple visible headers');
        if (Array.from(document.querySelectorAll('#va-shell-rail, .va-shell-rail')).filter(isV).length > 1) errs.push('Multiple visible rails');
        if (Array.from(document.querySelectorAll('#va-floating-dock, .va-shell-bottomdock, .va-shell-dock')).filter(isV).length > 1) errs.push('Multiple visible docks');
        return errs;
    """)
    errors.extend([f"[GATE_5_CHROME] {e}" for e in chrome_errs])
    return errors


def check_gate_12_and_13(driver: webdriver.Chrome) -> list[str]:
    """Gates 12 (zero backticks) and 13 (ctrl-1 effector guard)."""
    errors: list[str] = []
    switch_to_portal(driver)
    bt_errs = driver.execute_script("""
        const m = document.getElementById('va-stage-main') || document.body, clone = m.cloneNode(true);
        for (const t of clone.querySelectorAll('pre, code, script, style')) t.remove();
        return (clone.innerText || '').includes('`') ? ['Visible text contains literal backtick (`)'] : [];
    """)
    errors.extend([f"[GATE_12_BACKTICK] {e}" for e in bt_errs])

    select_tier(driver, "ctrl-1")
    switch_to_portal(driver)
    c1_errs = driver.execute_script("""
        const eb = document.querySelector('.ctrl1-exec-btn'), ab = document.querySelector('.ctrl1-arm-btn'), errs = [];
        if (!eb || !ab) return ['Missing .ctrl1-exec-btn or .ctrl1-arm-btn on ctrl-1 tier'];
        if (!eb.disabled) errs.push('Exec button not initially disabled');
        ab.click();
        if (eb.disabled) errs.push('Exec button remained disabled after arm button click');
        eb.click();
        const st = document.querySelector('.ctrl1-telemetry-strip');
        if (st && st.querySelectorAll('button').length > 0) errs.push('ctrl1-telemetry-strip contains buttons');
        const sb = document.querySelector('.va-stale-badge');
        if (!sb || sb.offsetParent === null) errs.push('Missing or hidden .va-stale-badge');
        return errs;
    """)
    errors.extend([f"[GATE_13_CTRL1] {e}" for e in c1_errs])
    return errors


def run_selenium_gates_1_to_13(
    driver: webdriver.Chrome,
    base_url: str,
    screenshots_dir: Any = None,
) -> list[str]:
    """Execute live Selenium CDP Gates 1 through 13 across all canonical viewports."""
    errors: list[str] = []
    driver.get(base_url)
    time.sleep(0.3)

    for w, h in VIEWPORTS:
        driver.set_window_size(w, h)
        time.sleep(0.1)
        errors.extend(check_gates_viewport(driver, w, h))
        errors.extend(check_gates_editorial_and_hinge(driver, w))
        errors.extend(check_gate_3_and_5_chrome(driver, w))

    errors.extend(check_gate_12_and_13(driver))
    return errors
