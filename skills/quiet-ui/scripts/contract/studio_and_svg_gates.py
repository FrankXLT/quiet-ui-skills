# SPDX-License-Identifier: Apache-2.0
"""Gates 16 (Outer Host Studio Bar) and 17 (SVG Font Ceiling & Figure Stacking)."""

from __future__ import annotations

import time
import urllib.parse
from selenium import webdriver

from .constants import TIERS, VIEWPORTS
from .selenium_gates import select_tier, switch_to_outer, switch_to_portal


def check_gate_16_studio_bar(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 16: Single-row <=48px Studio Bar, mode-first order, <=1 select @390px, markerless summary."""
    errors: list[str] = []
    driver.get(base_url)
    time.sleep(0.25)

    for w, h in VIEWPORTS:
        switch_to_outer(driver)
        driver.set_window_size(w, h)
        time.sleep(0.08)

        host_errs = driver.execute_script("""
            const w = arguments[0], errs = [];
            const bar = document.querySelector('.va-studio-bar') || document.getElementById('va-studio-bar');
            if (!bar) return ['Missing .va-studio-bar header'];
            bar.classList.remove('is-tucked');
            if (bar.offsetHeight <= 0 || bar.offsetHeight > 48) {
                errs.push(`offsetHeight ${bar.offsetHeight}px exceeds 48px ceiling`);
            }
            if (bar.scrollWidth > bar.clientWidth + 1) {
                errs.push(`scrollWidth (${bar.scrollWidth}) > clientWidth (${bar.clientWidth})`);
            }
            const modePill = document.querySelector('.va-mode-tablist') || document.getElementById('va-view-ui-btn');
            const tierSel = document.getElementById('va-tier-select');
            if (!modePill || !tierSel) {
                errs.push('Missing [UI | Atlas] tablist or #va-tier-select');
            } else {
                const mr = modePill.getBoundingClientRect(), tr = tierSel.getBoundingClientRect();
                if (!(mr.left < tr.left)) {
                    errs.push(`[UI | Atlas] left (${mr.left.toFixed(1)}) not before tierSelect (${tr.left.toFixed(1)})`);
                }
            }
            if (w === 390) {
                const visSelects = Array.from(bar.querySelectorAll('select')).filter(s => {
                    const cs = window.getComputedStyle(s), r = s.getBoundingClientRect();
                    return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0;
                });
                if (visSelects.length > 1) {
                    errs.push(`Expected <= 1 visible <select> in .va-studio-bar at 390px, got ${visSelects.length}`);
                }
            }
            for (const sum of document.querySelectorAll('summary')) {
                const lst = window.getComputedStyle(sum).listStyleType;
                if (lst !== 'none') {
                    errs.push(`Host <summary> has listStyleType='${lst}' (expected 'none')`);
                    break;
                }
            }
            return errs;
        """, w)
        errors.extend([f"[GATE_16_BAR_{w}] {e}" for e in host_errs])

        # Check <summary> listStyleType inside portal across editorial tiers with <details>
        for sum_tier in ("doc-1", "doc-4b"):
            select_tier(driver, sum_tier)
            if switch_to_portal(driver):
                p_sum_errs = driver.execute_script("""
                    const errs = [];
                    for (const sum of document.querySelectorAll('summary')) {
                        const lst = window.getComputedStyle(sum).listStyleType;
                        if (lst !== 'none') {
                            errs.push(`Portal <summary> has listStyleType='${lst}'`);
                            break;
                        }
                    }
                    return errs;
                """)
                errors.extend([f"[GATE_16_SUMMARY_{sum_tier}_{w}] {e}" for e in p_sum_errs])

    # Verify Studio Settings <dialog> micro-labels & Atlas mode center-select swap
    switch_to_outer(driver)
    driver.set_window_size(1280, 900)
    time.sleep(0.06)
    sheet_errs = driver.execute_script("""
        const errs = [];
        const sheet = document.getElementById('va-customize-sheet');
        if (!sheet || sheet.getAttribute('closedby') !== 'any') {
            return ['Missing #va-customize-sheet or closedby="any"'];
        }
        const txt = sheet.textContent.toUpperCase();
        for (const req of ['SURFACE THEME', 'NAVIGATION SHELL', 'DENSITY', 'ROOT SCALE', 'STAGE SIMULATOR', 'COPY PROMPT']) {
            if (!txt.includes(req)) errs.push(`Studio sheet missing label '${req}'`);
        }
        const diagBtn = document.getElementById('va-view-diag-btn');
        const uiBtn = document.getElementById('va-view-ui-btn');
        const tierSel = document.getElementById('va-tier-select');
        if (diagBtn && uiBtn && tierSel) {
            diagBtn.click();
            const opts = Array.from(tierSel.options).map(o => o.textContent.trim());
            if (!opts.includes('All 45') || !opts.includes('DSL Workbench')) {
                errs.push('Atlas mode did not swap #va-tier-select to Atlas section jumps');
            }
            uiBtn.click();
        }
        return errs;
    """)
    errors.extend([f"[GATE_16_SHEET] {e}" for e in sheet_errs])
    return errors


_SVG_FONT_AUDIT_JS = """
const [minPx, maxPx, checkClip, revealDeferred] = arguments;
const defs = revealDeferred ? document.querySelectorAll('.atlas-deferred-family') : [];
defs.forEach(d => { d.style.contentVisibility = 'visible'; });
if (defs.length) document.body.offsetHeight;
const errs = [];
for (const svg of document.querySelectorAll('svg')) {
    const sr = svg.getBoundingClientRect();
    if (sr.width <= 0 || sr.height <= 0) continue;
    const vb = (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width > 0) ? svg.viewBox.baseVal : null;
    for (const t of svg.querySelectorAll('text')) {
        if (!t.textContent || !t.textContent.trim()) continue;
        const cs = window.getComputedStyle(t);
        if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
        const ctm = t.getScreenCTM();
        const scale = ctm ? Math.hypot(ctm.a, ctm.b) : 0;
        if (!ctm || scale <= 0) continue;
        const fs = parseFloat(cs.fontSize);
        const rendered = fs * scale;
        if (rendered < minPx - 0.05 || rendered > maxPx + 0.05) {
            errs.push(`SVG <text> '${t.textContent.trim().slice(0, 28)}' rendered=${rendered.toFixed(2)}px outside [${minPx}, ${maxPx}]`);
            break;
        }
        if (checkClip && vb) {
            const tr = t.getBoundingClientRect();
            const scaleX = sr.width / vb.width;
            if (tr.width > 0 && (tr.left < sr.left - 4 * scaleX || tr.right > sr.right + 6 * scaleX)) {
                errs.push(`SVG <text> '${t.textContent.trim().slice(0, 28)}' clips viewBox [0..${vb.width}]: x=${((tr.left - sr.left) / scaleX).toFixed(1)}..${((tr.right - sr.left) / scaleX).toFixed(1)}`);
                break;
            }
        }
    }
    if (errs.length) break;
}
defs.forEach(d => { d.style.contentVisibility = ''; });
return errs;
"""


def check_gate_17_svg_and_figures(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 17: 10.0 <= fontSize * getScreenCTM().a <= 16.0 across 16 tiers & 45 Atlas cards + 390px stacking."""
    errors: list[str] = []
    driver.get(base_url)
    time.sleep(0.25)

    # 1. Audit all 16 UI tiers across all 5 canonical viewports
    for w, h in VIEWPORTS:
        switch_to_outer(driver)
        driver.set_window_size(w, h)
        time.sleep(0.08)

        for tier in TIERS:
            select_tier(driver, tier)
            if not switch_to_portal(driver):
                errors.append(f"[GATE_17_PORTAL] Missing #va-stage-portal on {tier} @{w}px")
                continue

            t_errs = driver.execute_script(_SVG_FONT_AUDIT_JS, 10.0, 16.0, w == 390, False)
            errors.extend([f"[GATE_17_TIER_{tier}_{w}] {e}" for e in t_errs])

            if w == 390:
                fig_errs = driver.execute_script("""
                    const errs = [];
                    for (const grid of document.querySelectorAll('.va-fig-split-grid')) {
                        if (grid.offsetParent === null) continue;
                        if (grid.scrollWidth > grid.clientWidth + 2) {
                            errs.push(`.va-fig-split-grid overflows horizontally (${grid.scrollWidth} > ${grid.clientWidth})`);
                        }
                        const panels = grid.querySelectorAll('.va-fig-panel');
                        if (panels.length >= 2) {
                            const r0 = panels[0].getBoundingClientRect(), r1 = panels[1].getBoundingClientRect();
                            if (r1.top < r0.bottom - 2) {
                                errs.push(`Multi-panel figure did not stack vertically at 390px`);
                            }
                        }
                    }
                    for (const card of document.querySelectorAll('.va-figure-card')) {
                        if (card.offsetParent === null) continue;
                        const cr = card.getBoundingClientRect();
                        if (cr.right > window.innerWidth + 2 || cr.left < -2) {
                            errs.push(`.va-figure-card clips viewport at 390px`);
                            break;
                        }
                    }
                    return errs;
                """)
                errors.extend([f"[GATE_17_FIG_{tier}_390] {e}" for e in fig_errs])

    # 2. Audit Evidence Component Library across all 5 canonical viewports
    driver.get(urllib.parse.urljoin(base_url, "bench/evidence-bench.html"))
    time.sleep(0.25)

    for w, h in VIEWPORTS:
        driver.set_window_size(w, h)
        time.sleep(0.08)
        a_errs = driver.execute_script(_SVG_FONT_AUDIT_JS, 10.0, 16.0, w == 390, True)
        errors.extend([f"[GATE_17_COMP_{w}] {e}" for e in a_errs])

    return errors


def run_studio_and_svg_gates(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Execute Headless Selenium CDP Gates 16 and 17."""
    errors: list[str] = []
    errors.extend(check_gate_16_studio_bar(driver, base_url))
    errors.extend(check_gate_17_svg_and_figures(driver, base_url))
    return errors
