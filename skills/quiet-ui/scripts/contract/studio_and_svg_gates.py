# SPDX-License-Identifier: Apache-2.0
"""Gates 16 (Studio Bar & Foldable Mastheads) and 17 (SVG Ceiling & ECharts Metrology) for Quiet UI v9.0."""

from __future__ import annotations

import time
from selenium import webdriver

from .constants import VIEWPORTS
from .selenium_gates import select_tier, set_cdp_viewport, switch_to_outer, switch_to_portal


def check_gate_16_studio_bar(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 16: Single-row <=48.5px v9 Studio Bar, [Examples | Components] first, foldable masthead stacking."""
    errors: list[str] = []
    driver.get(base_url)
    time.sleep(0.25)

    for w, h in (*VIEWPORTS, (840, 1050)):
        switch_to_outer(driver)
        set_cdp_viewport(driver, w, h)
        time.sleep(0.06)
        bar_errs = driver.execute_script("""
            const w = arguments[0], errs = [];
            const bar = document.getElementById('va-studio-bar');
            if (!bar) return ['Missing #va-studio-bar'];
            bar.classList.remove('is-tucked');
            if (bar.offsetHeight <= 0 || bar.offsetHeight > 48.5) errs.push(`bar height=${bar.offsetHeight}px > 48.5px`);
            if (bar.scrollWidth > bar.clientWidth + 1) errs.push(`bar overflow ${bar.scrollWidth} > ${bar.clientWidth}`);
            const tabs = document.getElementById('va-studio-mode-tablist'), dSel = document.getElementById('va-domain-select');
            if (!tabs || !dSel) errs.push('Missing tablist or #va-domain-select');
            else if (dSel.getBoundingClientRect().width > 0 && !(tabs.getBoundingClientRect().left < dSel.getBoundingClientRect().left)) {
                errs.push('[Examples | Components] tablist not placed before #va-domain-select');
            }
            return errs;
        """, w)
        errors.extend(f"[GATE_16_BAR_{w}] {e}" for e in bar_errs)

    set_cdp_viewport(driver, 840, 1050)
    for vid in ("v02-trial-regulatory-brief", "v04-sre-incident-workbench", "v06-ai-drift-and-lineage-ide", "v10-civic-capital-budget-deck", "v12-stem-interactive-lab", "v18-home-assistant-companion-console"):
        select_tier(driver, vid)
        if switch_to_portal(driver):
            mh_err = driver.execute_script("""
                const mh = document.querySelector('.v9-masthead');
                if (!mh || getComputedStyle(mh).display === 'none') return '';
                const eb = mh.querySelector('.v9-masthead-eyebrow'), h1 = mh.querySelector('.v9-masthead-title');
                if (!eb || !h1) return '';
                const er = eb.getBoundingClientRect(), hr = h1.getBoundingClientRect();
                return (hr.left - er.left > 8 || hr.top < er.bottom - 2) ? `split masthead dx=${(hr.left - er.left).toFixed(1)} top=${hr.top.toFixed(1)}` : '';
            """)
            if mh_err:
                errors.append(f"[GATE_16_FOLD_{vid}] {mh_err}")
    switch_to_outer(driver)
    return errors


def check_gate_17_svg_font_ceiling(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 17: Inline SVG aspect/clip/font-ceiling invariants + all 6 auto-ECharts parity views."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    driver.get(base_url)

    for vid in (
        "v06-ai-drift-and-lineage-ide",
        "v10-civic-capital-budget-deck",
        "v11-treasury-stress-test-solver",
        "v12-stem-interactive-lab",
        "v13-propulsion-archival-monograph",
        "v18-home-assistant-companion-console",
    ):
        select_tier(driver, vid)
        if not switch_to_portal(driver):
            continue
        svg_errs = driver.execute_script("""
            const vid = arguments[0], errs = [];
            for (const svg of document.querySelectorAll('svg')) {
                if (svg.getAttribute('preserveAspectRatio') === 'none') errs.push(`${vid}: preserveAspectRatio=none`);
                const sr = svg.getBoundingClientRect();
                if (sr.width < 20 || sr.height < 10) continue;
                for (const t of svg.querySelectorAll('text')) {
                    if (!t.textContent?.trim() || getComputedStyle(t).display === 'none') continue;
                    const fs = parseFloat(getComputedStyle(t).fontSize || '0');
                    if (t.closest('.qe-echarts-host, .va-figure-scroll') && fs > 16.5) {
                        errs.push(`${vid}: SVG text fontSize=${fs.toFixed(1)}px > 16.5px`); break;
                    }
                    const tr = t.getBoundingClientRect();
                    if (tr.width > 0 && (tr.left < sr.left - 2 || tr.right > sr.right + 2 || tr.top < sr.top - 2 || tr.bottom > sr.bottom + 2)) {
                        errs.push(`${vid}: SVG text '${t.textContent.trim().slice(0, 18)}' clipped outside viewBox`); break;
                    }
                }
            }
            const active = [...document.querySelectorAll('.qe-plot-wrap[data-echarts-active="true"]')];
            if (!active.length) errs.push(`${vid}: expected ECharts active host, found 0`);
            for (const pw of active) {
                const pld = JSON.parse(pw.dataset.quietEcharts || '{}');
                const txt = pw.querySelector('.qe-echarts-host svg')?.textContent || '';
                if (!txt.trim()) { errs.push(`${vid}: empty ECharts SVG host`); continue; }
                if (vid.startsWith('v10')) {
                    if (!Array.isArray(pld.totals) || !txt.includes('Policy Reserve Floor')) errs.push('v10 waterfall missing totals or Policy Reserve Floor');
                } else if (vid.startsWith('v18')) {
                    if (pld.kind !== 'stacked_bar' || !txt.includes('Solar Production')) errs.push('v18 stacked energy plot incomplete');
                } else if (vid.startsWith('v06') || vid.startsWith('v12') || vid.startsWith('v13')) {
                    if (!pld.residuals || !txt.includes('+2σ')) errs.push(`${vid}: missing synchronized residual strip`);
                }
                for (const s of (pld.series || [])) {
                    if (s.epistemic === 'discrete_measurement' && s.connectPiecewise) errs.push(`${vid}: discrete points connected by line`);
                }
            }
            return errs;
        """, vid)
        errors.extend(f"[GATE_17_SVG_ECHARTS] {e}" for e in svg_errs)
    switch_to_outer(driver)
    return errors


def run_studio_and_svg_gates(driver: webdriver.Chrome, base_url: str) -> list[str]:
    errors: list[str] = []
    errors.extend(check_gate_16_studio_bar(driver, base_url))
    errors.extend(check_gate_17_svg_font_ceiling(driver, base_url))
    return errors
