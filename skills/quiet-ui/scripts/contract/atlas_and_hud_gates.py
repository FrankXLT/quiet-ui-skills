# SPDX-License-Identifier: Apache-2.0
"""Gates 14 (39-Specimen Component Library + ECharts) and 15 (v15 HUD & v16 Optics) for Quiet UI v9.0."""

from __future__ import annotations

import time
import urllib.parse
from selenium import webdriver

from .selenium_gates import select_tier, set_cdp_viewport, switch_to_outer, switch_to_portal


def check_gate_14_atlas_standalone(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 14A: Standalone 39-specimen Components Library (evidence-bench.html) parity & mobile overflow."""
    errors: list[str] = []
    bench_url = urllib.parse.urljoin(base_url, "docs/bench/evidence-bench.html")
    set_cdp_viewport(driver, 390, 844)
    driver.get(bench_url)
    time.sleep(0.35)
    res = driver.execute_script("""
        const errs = [];
        const cards = document.querySelectorAll('.qe-specimen');
        if (cards.length !== 39) errs.push(`Expected 39 specimens, got ${cards.length}`);
        if (document.documentElement.scrollWidth > window.innerWidth + 2) {
            errs.push(`Mobile 390px overflow: ${document.documentElement.scrollWidth} > ${window.innerWidth}`);
        }
        for (const c of cards) {
            const h = c.querySelector('.qe-fig-title');
            if (h && /^M[1-6]-L[1-3]:/.test(h.textContent.trim())) {
                errs.push(`Leaked specimen prefix in title: '${h.textContent.trim()}'`); break;
            }
        }
        return errs;
    """)
    errors.extend(f"[GATE_14_BENCH_STANDALONE] {e}" for e in res)
    set_cdp_viewport(driver, 1440, 900)
    return errors


def check_gate_14_atlas_embedded(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 14B: Components tab inside Studio Shell loads 39 specimens, Live ECharts & 5-tab Eco Drawer."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    driver.get(base_url)
    time.sleep(0.25)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    for _ in range(25):
        time.sleep(0.08)
        if driver.execute_script("const p=document.getElementById('va-stage-portal');return p?.contentDocument?.querySelectorAll('.qe-specimen').length===39;"):
            break
    bench_ok = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal')?.contentDocument;
        if (!doc) return 'missing portal document';
        if (doc.querySelectorAll('.qe-specimen').length !== 39) return 'specimen count !== 39';
        const wraps = [...doc.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]')];
        if (wraps.length < 3) return 'expected >=3 ECharts specimens, found ' + wraps.length;
        for (const wrap of wraps) {
            wrap.querySelector('.qe-mode-btn[data-qe-mode="echarts"]')?.click();
            if (wrap.dataset.echartsActive !== 'true' || !wrap.querySelector('.qe-echarts-host svg')) return 'Live ECharts failed to mount on specimen';
            const ls = wrap.querySelector('.qe-legend-series');
            if (ls && getComputedStyle(ls).display !== 'none') return 'Duplicate HTML legend visible under ECharts';
        }
        const fig = wraps[0].closest('.qe-figure');
        const drw = fig?.querySelector('.qe-eco-drawer');
        if (!drw) return 'missing 5-tab Eco Drawer';
        drw.open = true;
        const tabs = [...drw.querySelectorAll('.qe-eco-tab[role="tab"]')];
        if (tabs.length !== 5) return 'expected 5 Eco tabs, got ' + tabs.length;
        tabs[1].click();
        const pre = drw.querySelector('.qe-eco-panel:not([hidden]) pre');
        if (!pre || pre.scrollWidth > pre.clientWidth + 2) return 'Eco code viewer missing or horizontally overflowing';
        drw.querySelector('.qe-copy-btn')?.click();
        return 'ok';
    """)
    if bench_ok != "ok":
        errors.append(f"[GATE_14_COMPONENTS_TAB] {bench_ok}")
    driver.execute_script("document.getElementById('va-tab-examples').click();")
    time.sleep(0.25)
    return errors


def check_gate_15_backplates_contrast(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 15A: Verify v15 HUD & v16 Maritime photographic backplates load (>= 1200px) with zero synthetic scenes."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    driver.get(base_url)
    for vid, min_photos in (("v15-collimated-flight-hud", 3), ("v16-transparent-window-overlay", 3)):
        select_tier(driver, vid)
        if not switch_to_portal(driver):
            continue
        res = driver.execute_script("""
            const [vid, n] = arguments, errs = [];
            const imgs = [...document.querySelectorAll('img.v9-opt-photo')];
            if (imgs.length !== n) errs.push(`${vid}: expected ${n} photos, got ${imgs.length}`);
            for (const i of imgs) if (!i.complete || i.naturalWidth < 1200) errs.push(`${vid}: unloaded photo ${i.dataset.asset}`);
            if (document.querySelectorAll('.v15-scene-svg, .v16-scene-svg, .v16-corridor-svg').length) errs.push(`${vid}: legacy synthetic scenery SVG present`);
            if (vid.startsWith('v15') && document.querySelectorAll('.v15-reticle-layer line[y1="360"][y2="360"]').length < 2) {
                errs.push('v15 horizon lines missing at y=360 (50% center)');
            }
            return errs;
        """, vid, min_photos)
        errors.extend(f"[GATE_15_OPTICS] {e}" for e in res)
    switch_to_outer(driver)
    return errors


def check_gate_15_field_of_regard(driver: webdriver.Chrome, base_url: str, screenshots_dir: str | None = None) -> list[str]:
    """Gate 15B: Verify v15 >= 65% clear boresight & v16 AAA >= 7.0:1 smart-glass scrim contrast."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    select_tier(driver, "v15-collimated-flight-hud")
    if switch_to_portal(driver):
        hud_err = driver.execute_script("""
            const st = document.getElementById('v15-hud-stage');
            if (!st) return 'missing #v15-hud-stage';
            const sr = st.getBoundingClientRect(), tot = sr.width * sr.height;
            let occ = 0;
            for (const el of st.querySelectorAll('.v15-hud-mode-strip, button')) {
                const r = el.getBoundingClientRect();
                occ += Math.max(0, r.width) * Math.max(0, r.height);
            }
            const clearFrac = tot > 0 ? 1 - (occ / tot) : 0;
            return clearFrac >= 0.65 ? '' : `v15 clear boresight ${(clearFrac * 100).toFixed(1)}% < 65%`;
        """)
        if hud_err:
            errors.append(f"[GATE_15_BORESIGHT] {hud_err}")

    select_tier(driver, "v16-transparent-window-overlay")
    if switch_to_portal(driver):
        glass_err = driver.execute_script("""
            const w = window.innerWidth, h = window.innerHeight, kx0 = w * 0.24, kx1 = w * 0.76, ky0 = h * 0.24, ky1 = h * 0.68;
            const parseRgb = (s) => { const m = s.match(/[0-9.]+/g) || [0,0,0,1]; return m.slice(0, 4).map(Number); };
            const relLum = (r, g, b) => [r, g, b].map(c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }).reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
            for (const pod of document.querySelectorAll('.v16-glass-pod')) {
                const cs = getComputedStyle(pod);
                const bf = cs.backdropFilter || cs.webkitBackdropFilter || '';
                if (!bf.includes('blur(')) return 'Pod missing backdrop blur';
                const pr = pod.getBoundingClientRect();
                if (Math.min(pr.right, kx1) > Math.max(pr.left, kx0) + 1 && Math.min(pr.bottom, ky1) > Math.max(pr.top, ky0) + 1) {
                    return 'Pod invades central windshield sightline corridor';
                }
                const bg = parseRgb(cs.backgroundColor), fg = parseRgb(cs.color);
                const a = bg.length >= 4 ? bg[3] : 1;
                const l1 = relLum(fg[0], fg[1], fg[2]);
                const l2 = relLum(bg[0] * a + 255 * (1 - a), bg[1] * a + 255 * (1 - a), bg[2] * a + 255 * (1 - a));
                const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                if (ratio < 7.0) return `v16 worst-case scrim contrast ${ratio.toFixed(1)}:1 < 7.0:1`;
            }
            return '';
        """)
        if glass_err:
            errors.append(f"[GATE_15_GLASS] {glass_err}")
    switch_to_outer(driver)
    return errors


def run_atlas_and_hud_gates(driver: webdriver.Chrome, base_url: str, screenshots_dir: str | None = None) -> list[str]:
    errors: list[str] = []
    errors.extend(check_gate_14_atlas_standalone(driver, base_url))
    errors.extend(check_gate_14_atlas_embedded(driver, base_url))
    errors.extend(check_gate_15_backplates_contrast(driver, base_url))
    errors.extend(check_gate_15_field_of_regard(driver, base_url, screenshots_dir))
    return errors
