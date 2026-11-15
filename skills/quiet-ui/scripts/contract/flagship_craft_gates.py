# SPDX-License-Identifier: Apache-2.0
"""Gates 18 to 21 for Quiet UI v8.2 Flagship Craftsmanship & Substance."""

from __future__ import annotations

import time
from pathlib import Path
from selenium import webdriver

from .constants import TIERS, TIER_HTML_FLOOR, TIER_HTML_LINE_RANGE, VIEWPORTS
from .selenium_gates import select_tier, switch_to_outer, switch_to_portal

TIER_LANDMARKS: dict[str, list[str]] = {
    "doc-1": [".va-bleed-wide", ".va-equation, .eq-num, [class*='math'], .doc1-equation, .doc1-eq-num", ".va-margin-citation, .sidenote, .sidenote-box, .doc1-sidenotes"],
    "doc-2": [".bluf-frame, .doc2-bluf", ".kpi-4strip, .kpi-cell", ".va-bleed-wide"],
    "doc-3": [".rfc-masthead, .doc3-masthead", ".req-badge", ".rfc-diff-block, #doc3-fsm-table"],
    "doc-4b": [".va-flow-spine, .spine-step", ".sig-band", ".doctest-box, .doc4b-nav-sidebar"],
    "doc-4a": [".doc4a-interlock-banner", ".doc4a-console-dock", ".doc4a-step-rail, .va-seq-step-band"],
    "bridge-1": [".b1-solver-frame, .b1-slider-group", ".b1-formula-box", ".b1-ledger-sec, .va-bleed-wide"],
    "deck-1": [".deck-step-card", ".deck1-slide-view, .deck1-slide, .deck1-shell"],
    "bridge-2": [".bridge2-matrix", ".bridge2-summary-panel, .bridge2-cell", ".va-table-wrap"],
    "app-2": [".app2-workbench", ".app2-kpi-strip", ".app2-thresh-pill, .app2-wave-wrap"],
    "app-1": [".app1-3pane-grid", ".app1-triage-row", ".app1-inspector, .app1-detail-pane, #app1-insp-id, #app1-insp-title, [aria-label='Selected Anomaly Details']"],
    "app-4": [".app4-dual-pane", ".app4-tasks-card", ".app4-blocks-card"],
    "app-3": [".app3-grid, .app3-bento", ".va-card.app3-span-2", ".va-card.app3-span-full"],
    "app-5": [".app5-circadian-svg, .app5-grid", ".app5-phase-switcher, .app5-top-bar", ".va-table-wrap"],
    "app-tree": [".apptree-panes, .apptree-pane-grid", ".tree-node", ".va-table-wrap"],
    "hud-1": [".hud1-reticle", ".hud1-viewport", ".va-hud-pod"],
    "ctrl-1": [".ctrl-ann-cell", ".ctrl1-zone-rail", ".ctrl-pid-svg", ".guarded-actuator-card"],
}


def check_gate_18_desktop_tables(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 18: Unclipped widescreen tables (>=1440px desktop) across all 16 tiers."""
    errors: list[str] = []

    for w, h in [(1440, 900), (1920, 1080), (2560, 1440)]:
        switch_to_outer(driver)
        driver.set_window_size(w, h)
        time.sleep(0.08)

        for slug in TIERS:
            select_tier(driver, slug)
            if not switch_to_portal(driver):
                continue
            table_errs = driver.execute_script("""
                const slug = arguments[0], w = arguments[1], errs = [];
                for (const wrap of document.querySelectorAll('.va-table-wrap')) {
                    if (wrap.offsetParent === null) continue;
                    if (wrap.scrollWidth > wrap.clientWidth + 2) {
                        const lbl = wrap.getAttribute('aria-label') || 'table';
                        errs.push(`${slug} @ ${w}px: '${lbl}' scrollWidth (${wrap.scrollWidth}) > clientWidth (${wrap.clientWidth})`);
                    }
                }
                for (const tbl of document.querySelectorAll('table')) {
                    if (tbl.offsetParent === null) continue;
                    const r = tbl.getBoundingClientRect();
                    if (r.right > window.innerWidth + 2) {
                        errs.push(`${slug} @ ${w}px: table right (${Math.round(r.right)}) clips viewport (${window.innerWidth})`);
                    }
                }
                return errs;
            """, slug, w)
            errors.extend([f"[GATE_18_TABLE_OVERFLOW] {e}" for e in table_errs])

    return errors


def check_gate_19_svg_text_halos(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 19: Zero unmasked stroke-through-text, text-on-text overlaps, or rect overflows across all 16 tiers."""
    errors: list[str] = []
    chart_tiers = {"doc-1", "doc-3", "bridge-1", "app-3", "app-5"}

    switch_to_outer(driver)
    driver.set_window_size(1440, 900)
    time.sleep(0.08)

    for slug in TIERS:
        select_tier(driver, slug)
        if not switch_to_portal(driver):
            continue
        check_halo = slug in chart_tiers
        svg_errs = driver.execute_script("""
            const slug = arguments[0], checkHalo = arguments[1], errs = [];
            for (const svg of document.querySelectorAll('svg')) {
                if (svg.getBoundingClientRect().width === 0) continue;
                const texts = Array.from(svg.querySelectorAll('text')).filter(t => {
                    const cs = window.getComputedStyle(t);
                    return cs.display !== 'none' && cs.visibility !== 'hidden';
                });
                const boxes = [];
                for (const t of texts) {
                    try {
                        const b = t.getBBox();
                        if (b.width > 0 && b.height > 0) boxes.push({ el: t, b, txt: t.textContent.trim() });
                    } catch (e) {}
                }
                for (let i = 0; i < boxes.length; i++) {
                    for (let j = i + 1; j < boxes.length; j++) {
                        const a = boxes[i], c = boxes[j];
                        const dx = Math.min(a.b.x + a.b.width, c.b.x + c.b.width) - Math.max(a.b.x, c.b.x);
                        const dy = Math.min(a.b.y + a.b.height, c.b.y + c.b.height) - Math.max(a.b.y, c.b.y);
                        if (dx > 3 && dy > 3) {
                            errs.push(`${slug}: SVG text overlap '${a.txt.slice(0,18)}' vs '${c.txt.slice(0,18)}'`);
                        }
                    }
                }
                const rects = Array.from(svg.querySelectorAll('rect')).map(r => {
                    try { return r.getBBox(); } catch (e) { return null; }
                }).filter(b => b && b.width > 30 && b.height > 18 && b.width < 320);
                for (const item of boxes) {
                    if ((item.el.getAttribute('text-anchor') || '') !== 'middle') continue;
                    const cx = item.b.x + item.b.width / 2, cy = item.b.y + item.b.height / 2;
                    for (const rb of rects) {
                        if (cx >= rb.x + 6 && cx <= rb.x + rb.width - 6 && cy >= rb.y + 4 && cy <= rb.y + rb.height - 4) {
                            if (item.b.width > rb.width + 6) {
                                errs.push(`${slug}: SVG text '${item.txt.slice(0,22)}' (${Math.round(item.b.width)}px) overflows rect (${Math.round(rb.width)}px)`);
                            }
                        }
                    }
                    if (!checkHalo) continue;
                    const cs = window.getComputedStyle(item.el);
                    const hasHalo = (cs.paintOrder || '').toLowerCase().includes('stroke') ||
                                    (parseFloat(cs.strokeWidth) || 0) >= 1.5 ||
                                    item.el.classList.contains('va-svg-halo-text') ||
                                    item.el.getAttribute('paint-order') === 'stroke';
                    if (hasHalo) continue;
                    for (const p of svg.querySelectorAll('path[stroke], line[stroke], polyline[stroke]')) {
                        if (p.getAttribute('stroke') === 'none') continue;
                        try {
                            const pb = p.getBBox();
                            if (!(item.b.x + item.b.width < pb.x || item.b.x > pb.x + pb.width ||
                                  item.b.y + item.b.height < pb.y || item.b.y > pb.y + pb.height)) {
                                errs.push(`${slug}: text '${item.txt.slice(0,20)}' collides with stroke without halo`);
                                break;
                            }
                        } catch (e) {}
                    }
                }
            }
            return errs;
        """, slug, check_halo)
        errors.extend([f"[GATE_19_SVG_CRAFT] {e}" for e in svg_errs])

    return errors


def check_gate_20_domain_layout(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 20: Zero desktop N4, zero dummy shell nav, zero flush-left 0px, Doc-1 serif, <30% void."""
    errors: list[str] = []
    switch_to_outer(driver)
    driver.set_window_size(1920, 1080)
    time.sleep(0.08)

    for slug in TIERS:
        select_tier(driver, slug)
        if not switch_to_portal(driver):
            continue
        dom_errs = driver.execute_script("""
            const slug = arguments[0], errs = [];
            const dock = document.querySelector('.va-thumb-dock, .va-nav-n4, #va-shell-bottomdock');
            if (dock && window.getComputedStyle(dock).display !== 'none' && dock.offsetHeight > 0) {
                errs.push(`${slug} displays mobile thumb dock on desktop 1080p`);
            }
            for (const navEl of document.querySelectorAll('#va-shell-topbar, #va-shell-rail')) {
                if (window.getComputedStyle(navEl).display === 'none' || navEl.offsetHeight === 0) continue;
                const txt = navEl.textContent || '';
                if (txt.includes('Quiet UI') || txt.includes('Diagnostics') || (txt.includes('Home') && txt.includes('Specs'))) {
                    errs.push(`${slug} shell nav contains generic dummy placeholder text`);
                }
            }
            if (slug !== 'hud-1') {
                for (const el of document.querySelectorAll('.va-tier h1, .va-tier h2, .va-tier p')) {
                    const r = el.getBoundingClientRect();
                    if (r.width > 20 && r.height > 8 && r.left < 8) {
                        errs.push(`${slug} has flush-left unpadded element <${el.tagName}> at x=${Math.round(r.left)}px`);
                        break;
                    }
                }
            }
            if (slug === 'doc-1') {
                const p = document.querySelector('.doc1-article p');
                const ff = p ? window.getComputedStyle(p).fontFamily.toLowerCase() : '';
                if (!ff.includes('newsreader') && !ff.includes('georgia') && !ff.includes('serif')) {
                    errs.push(`doc-1 prose fontFamily '${ff}' is missing scholarly serif voice`);
                }
            }
            if (['app-1', 'app-3', 'app-tree', 'ctrl-1'].includes(slug)) {
                const tierEl = document.querySelector('.va-tier');
                if (tierEl && tierEl.scrollHeight < window.innerHeight * 0.65) {
                    errs.push(`${slug} exceeds 30% vertical void ceiling at 1080p`);
                }
            }
            return errs;
        """, slug)
        errors.extend([f"[GATE_20_DOMAIN_LAYOUT] {e}" for e in dom_errs])

    for w, h in VIEWPORTS:
        switch_to_outer(driver)
        driver.set_window_size(w, h)
        time.sleep(0.08)
        select_tier(driver, "app-3")
        if switch_to_portal(driver):
            cnt = driver.execute_script(
                "return document.querySelectorAll('.app3-grid > .va-card, .app3-bento > .va-card').length;"
            )
            if cnt < 6:
                errors.append(f"[GATE_20_BENTO_HOLES] App-3 has {cnt} direct Bento cards at {w}px (expected 6)")

    return errors


def check_gate_21_substance_landmarks(driver: webdriver.Chrome, base_url: str, repo_root: Path) -> list[str]:
    """Gate 21: Per-tier substance landmarks and >= 240L HTML floor across all 16 tier templates."""
    errors: list[str] = []

    # 1. HTML line floor check
    tiers_dir = repo_root / "src" / "tiers"
    if tiers_dir.exists():
        for p in sorted(tiers_dir.glob("*.html")):
            lines = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
            if lines < TIER_HTML_FLOOR:
                errors.append(f"[GATE_21_HTML_FLOOR] {p.name} has {lines} lines (floor is {TIER_HTML_FLOOR})")
            elif lines > TIER_HTML_LINE_RANGE[1]:
                errors.append(f"[GATE_21_HTML_CEILING] {p.name} has {lines} lines (max is {TIER_HTML_LINE_RANGE[1]})")

    # 2. Live DOM landmark verification
    switch_to_outer(driver)
    driver.set_window_size(1920, 1080)
    time.sleep(0.08)

    for slug, selectors in TIER_LANDMARKS.items():
        select_tier(driver, slug)
        time.sleep(0.15)
        if not switch_to_portal(driver):
            errors.append(f"[GATE_21_LANDMARKS] Could not switch to portal for {slug}")
            continue

        for sel in selectors:
            found = driver.execute_script("""
                const sel = arguments[0];
                return document.querySelector(sel) !== null;
            """, sel)
            if not found:
                errors.append(f"[GATE_21_LANDMARKS] Tier '{slug}' missing mandatory landmark: '{sel}'")

    return errors


def run_flagship_craft_gates(driver: webdriver.Chrome, base_url: str, repo_root: Path) -> list[str]:
    """Execute Gates 18 through 21."""
    errors: list[str] = []
    driver.get(base_url)
    time.sleep(0.25)
    print("  Running Gate 18 (Desktop Tables Widescreen Bleed & Zero Clipping)...")
    errors.extend(check_gate_18_desktop_tables(driver, base_url))
    print("  Running Gate 19 (SVG Stroke-Through-Text Intersections & Halos)...")
    errors.extend(check_gate_19_svg_text_halos(driver, base_url))
    print("  Running Gate 20 (Domain-Authentic Layout & Navigation)...")
    errors.extend(check_gate_20_domain_layout(driver, base_url))
    print("  Running Gate 21 (Per-Tier Substance Landmarks & HTML Floor)...")
    errors.extend(check_gate_21_substance_landmarks(driver, base_url, repo_root))
    return errors
