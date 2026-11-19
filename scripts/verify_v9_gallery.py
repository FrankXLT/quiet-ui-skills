#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.5 — Domain 06 HA, Single-Legend ECharts & 8-Shot Retina Proof Helpers."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from verify_v9_helpers import set_viewport


def _check_v17_and_v18(driver: Any, base_url: str, errs: list[str]) -> None:
    set_viewport(driver, 1440, 900, 1)
    # v17: matted picture frame, >= 76% unobstructed canvas, zero SCADA slugs, F/C unit toggle
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v17-picture-frame-home-kiosk&theme=white")
    time.sleep(0.45)
    v17_res = driver.execute_script("""
        const f = document.getElementById('va-stage-portal');
        const doc = f && f.contentDocument;
        if (!doc) return 'no doc';
        if (doc.querySelector('.v15-reticle-layer')) return 'forbidden HUD crosshair in v17';
        const txt = doc.body.innerText || '';
        for (const bad of ['ZONE-LIVING', 'LEAK-LOOP-06', 'PANEL-MAIN-200A']) {
            if (txt.includes(bad)) return 'v17 leaked SCADA slug: ' + bad;
        }
        const vp = doc.getElementById('v17-kiosk');
        const imgArt = doc.getElementById('v17-photo-art');
        if (!vp || !imgArt || !imgArt.complete || imgArt.naturalWidth < 1200) {
            return 'art img incomplete nw=' + (imgArt ? imgArt.naturalWidth : -1);
        }
        const vr = vp.getBoundingClientRect();
        let occ = 0;
        doc.querySelectorAll('.v17-glass-pod, .v17-scene-bar').forEach(el => {
            const r = el.getBoundingClientRect();
            occ += Math.max(0, r.width) * Math.max(0, r.height);
        });
        const freeRatio = 1 - (occ / Math.max(1, vr.width * vr.height));
        if (freeRatio < 0.76) return 'unobstructed art ratio too low: ' + freeRatio.toFixed(3);
        const lBtn = doc.querySelector('button[data-v17-backdrop="landscape"]');
        const sBtn = doc.querySelector('button[data-v17-scene="goodnight"]');
        const uBtn = doc.getElementById('v17-unit-btn');
        if (!lBtn || !sBtn || !uBtn) return 'missing v17 backdrop/scene/unit controls';
        lBtn.click(); sBtn.click(); uBtn.click();
        if (!vp.innerText.includes('71 °F')) return 'v17 unit toggle failed to convert 21.5 °C -> 71 °F';
        return 'ok';
    """)
    time.sleep(0.35)
    if v17_res != "ok":
        errs.append(f"[V17_KIOSK] {v17_res}")
    else:
        land_nw = driver.execute_script(
            "const img=document.getElementById('va-stage-portal').contentDocument.getElementById('v17-photo-landscape');"
            "return img && img.complete ? img.naturalWidth : 0;"
        )
        if int(land_nw or 0) < 1200:
            errs.append(f"[V17_LANDSCAPE] landscape backdrop naturalWidth={land_nw} < 1200")

    # v18 Mobile (390x844 -> N4 dock + >=44px targets + 0 overflow) & Desktop Mushroom + Stacked ECharts
    set_viewport(driver, 390, 844, 1)
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&theme=white")
    time.sleep(0.45)
    mob_res = driver.execute_script("""
        const f = document.getElementById('va-stage-portal');
        const doc = f && f.contentDocument;
        if (!doc) return 'no doc';
        if (doc.documentElement.dataset.effectiveNav !== 'n4') return 'expected N4 mobile nav, got ' + doc.documentElement.dataset.effectiveNav;
        if (doc.documentElement.scrollWidth > doc.documentElement.clientWidth + 1) return 'mobile x-overflow';
        const btn = doc.getElementById('v18-lock-arm');
        if (!btn || btn.getBoundingClientRect().height < 43.5) return 'touch target < 44px';
        return 'ok';
    """)
    if mob_res != "ok":
        errs.append(f"[V18_MOBILE_N4] {mob_res}")

    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&theme=white")
    time.sleep(0.55)
    desk_res = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal').contentDocument;
        if (!doc) return 'no doc';
        const txt = doc.body.innerText || '';
        for (const bad of ['PANEL-MAIN-200A', 'PV-STRING-SOUTH', 'BATT-WALL-13KWH', 'EVSE-GARAGE-48A', 'LOCK-FRONT-01', 'GARAGE-BAY-01', 'MATTER-1.4', 'IEEE-2030.5', 'HOME-DER-PANEL', 'Residential Zones']) {
            if (txt.includes(bad)) return 'v18 leaked SCADA/internal string: ' + bad;
        }
        const wrap = doc.querySelector('#v18-energy .qe-plot-wrap');
        if (!wrap || wrap.dataset.echartsActive !== 'true') return 'v18 stacked energy ECharts did not mount';
        if (wrap.querySelector('.qe-cond-strip')) return 'v18 embedded stacked_bar leaked .qe-cond-strip';
        const leg = wrap.querySelector('.qe-param-legend');
        if (leg && getComputedStyle(leg).display !== 'none') return 'v18 duplicated static legend under active ECharts';
        doc.querySelector('button[data-v18-unit="f"]').click();
        if (!doc.getElementById('v18-rooms').innerText.includes('71 °F')) return 'v18 F/C unit switch failed';
        const ex1 = doc.getElementById('v18-lock-exec');
        const arm1 = doc.getElementById('v18-lock-arm');
        const pill1 = doc.getElementById('v18-lock-pill');
        if (!ex1 || !arm1 || !pill1 || !ex1.disabled) return 'lock exec not initially guarded';
        arm1.click();
        if (ex1.disabled) return 'lock arm failed to unlock step 2';
        ex1.click();
        if (pill1.textContent.trim() !== 'UNLOCKED' || !ex1.disabled) return 'lock did not transition & re-arm-guard';
        const ex2 = doc.getElementById('v18-garage-exec');
        const arm2 = doc.getElementById('v18-garage-arm');
        if (!ex2 || !arm2 || !ex2.disabled) return 'garage not initially guarded';
        arm2.click(); ex2.click();
        if (doc.getElementById('v18-garage-pill').textContent.trim() !== 'OPEN') return 'garage did not open';
        doc.querySelector('button[data-v18-filter="climate"]').click();
        const vis = [...doc.querySelectorAll('.v18-zone-tile')].filter(el => !el.hasAttribute('hidden')).length;
        return vis === 2 ? 'ok' : 'filter climate expected 2 visible, got ' + vis;
    """)
    if desk_res != "ok":
        errs.append(f"[V18_INTERLOCKS] {desk_res}")


def _check_all_8_photos_and_echarts(driver: Any, base_url: str, errs: list[str]) -> None:
    for wid, vw, btn_sel, mode_val in (
        ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "button[data-backplate='earthrise']", "earthrise"),
        ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "button[data-backplate='lowlight']", "lowlight"),
        ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "button[data-luminance='daylight']", "daylight"),
        ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "button[data-luminance='night']", "night"),
    ):
        driver.get(f"{base_url}?world={wid}&view={vw}&theme=white")
        time.sleep(0.4)
        driver.execute_script("const b=document.getElementById('va-stage-portal').contentDocument.querySelector(arguments[0]);if(b)b.click();", btn_sel)
        time.sleep(0.45)
        nw = driver.execute_script("const i=document.getElementById('va-stage-portal').contentDocument.querySelector('img[data-photo-mode=\"'+arguments[0]+'\"]');return i&&i.complete?i.naturalWidth:0;", mode_val)
        if int(nw or 0) < 1200:
            errs.append(f"[PHOTO_LOAD] {vw}/{mode_val} naturalWidth={nw} < 1200")

    for wid, vw in (
        ("04-civic-finance-and-stem-learning", "v10-civic-capital-budget-deck"),
        ("04-civic-finance-and-stem-learning", "v11-treasury-stress-test-solver"),
        ("05-physical-systems-auto-and-aero", "v13-propulsion-archival-monograph"),
        ("06-smart-home-and-energy", "v18-home-assistant-companion-console"),
    ):
        driver.get(f"{base_url}?world={wid}&view={vw}&theme=white")
        time.sleep(0.6)
        ec_ok = driver.execute_script("""
            const doc = document.getElementById('va-stage-portal').contentDocument;
            const wrap = doc && doc.querySelector('.qe-plot-wrap[data-echarts-active="true"]');
            if (!wrap || !wrap.querySelector('.qe-echarts-host svg')) return 'missing svg';
            const ls = wrap.querySelector('.qe-legend-series');
            if (ls && getComputedStyle(ls).display !== 'none') return 'duplicate html legend series visible';
            return 'ok';
        """)
        if ec_ok != "ok":
            errs.append(f"[ECHARTS_MOUNT] {vw}: {ec_ok}")
            continue
        driver.execute_script("window.QuietStudioPortalV9.state.theme='dark'; window.QuietStudioPortalV9.applyState(false);")
        time.sleep(0.35)
        dark_ok = driver.execute_script("""
            const doc = document.getElementById('va-stage-portal').contentDocument;
            return !!(doc && doc.documentElement.dataset.theme === 'dark' && doc.querySelector('.qe-echarts-host svg'));
        """)
        if not dark_ok:
            errs.append(f"[ECHARTS_RETHEME] {vw}: failed dark retheme with live ECharts")

    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&theme=white&medium=m1")
    time.sleep(0.45)
    m1_ok = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal').contentDocument;
        const wrap = doc && doc.querySelector('.qe-plot-wrap');
        const fb = wrap && wrap.querySelector('.qe-svg-fallback');
        return !!(wrap && wrap.dataset.echartsActive !== 'true' && fb && getComputedStyle(fb).display !== 'none');
    """)
    if not m1_ok:
        errs.append("[ECHARTS_M1_FALLBACK] v18 did not fall back to static .qe-svg-fallback under medium=m1")

    # Bench Components toggle, 5-tab Ecosystem Config viewer, zero M4-L1 prefixes & zero horizontal overflow
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.35)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    time.sleep(0.75)
    bench_ok = driver.execute_script("""
        const bdoc = document.getElementById('va-stage-portal').contentDocument;
        if (!bdoc) return 'no bench doc';
        const titles = [...bdoc.querySelectorAll('.qe-fig-title')].map(el => el.textContent.trim());
        const badPre = titles.find(t => /^M[1-6]-L[1-3]:/.test(t));
        if (badPre) return 'specimen title kept prefix: ' + badPre;
        const btn = bdoc.querySelector('.qe-plot-wrap .qe-mode-btn[data-qe-mode="echarts"]');
        const drw = bdoc.querySelector('.qe-eco-drawer');
        if (!btn || !drw) return 'missing toggle or eco drawer';
        btn.click(); drw.open = true;
        const wrap = btn.closest('.qe-plot-wrap');
        if (!wrap || wrap.dataset.echartsActive !== 'true' || !wrap.querySelector('.qe-echarts-host svg')) return 'bench echarts failed';
        const ls = wrap.querySelector('.qe-legend-series');
        if (ls && getComputedStyle(ls).display !== 'none') return 'bench echarts leaked duplicate html legend series';
        const tabs = [...drw.querySelectorAll('.qe-eco-tab[role="tab"]')];
        if (tabs.length !== 5) return 'expected 5 eco tabs, got ' + tabs.length;
        tabs[1].click();
        const openPre = drw.querySelector('.qe-eco-panel:not([hidden]) pre');
        if (!openPre || !openPre.textContent.includes('go.Scatter')) return 'plotly tab did not switch';
        if (openPre.scrollWidth > openPre.clientWidth + 2) return 'eco pre horizontal scrollbar scrollWidth=' + openPre.scrollWidth + ' clientWidth=' + openPre.clientWidth;
        const cbtn = drw.querySelector('.qe-copy-btn');
        const cstat = drw.querySelector('.qe-copy-status');
        if (!cbtn || !cstat) return 'missing eco copy button or status';
        cbtn.click();
        if (/\\b[A-Za-z]\\((?:pv|load|grid|rx|obs|bte)\\)/i.test(bdoc.body.innerText)) return 'bench leaked ASCII pseudo-subscript';
        return 'ok';
    """)
    if bench_ok == "ok":
        time.sleep(0.15)
        cpy_txt = driver.execute_script("return document.getElementById('va-stage-portal').contentDocument.querySelector('.qe-eco-drawer .qe-copy-status')?.textContent || '';")
        if not cpy_txt.strip():
            errs.append("[BENCH_COPY] Copy Snippet click did not announce status")
    if bench_ok != "ok":
        errs.append(f"[BENCH_ECHARTS] {bench_ok}")


def run_domain06_and_echarts_checks(driver: Any, base_url: str, root_url: str) -> list[str]:
    """Execute Gate 5.5 CDP checks for Domain 06, 8 photos, single-legend ECharts & 5-tab Bench."""
    errs: list[str] = []
    _check_v17_and_v18(driver, base_url, errs)
    _check_all_8_photos_and_echarts(driver, base_url, errs)
    set_viewport(driver, 1440, 900, 1)
    return errs


def capture_gate54_gallery(driver: Any, base_url: str, out_dir: Path) -> None:
    """Capture 8 Gate 5.5 Retina (deviceScaleFactor=2) proof PNGs into screenshots_gate55."""
    out_dir.mkdir(parents=True, exist_ok=True)
    shots = [
        ("01_v15_hud_daylight_runway.png", "05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "white", 1440, 900, ""),
        ("02_v15_hud_orbital_limb_inertial.png", "05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "dark", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-backplate='earthrise']\");if(b)b.click();"),
        ("03_v16_maritime_wheelhouse_daylight.png", "05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "white", 1440, 900, ""),
        ("04_v16_maritime_wheelhouse_night.png", "05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "dark", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-luminance='night']\");if(b)b.click();"),
        ("05_v17_ha_framed_gallery_art.png", "06-smart-home-and-energy", "v17-picture-frame-home-kiosk", "white", 1440, 900, ""),
        ("06_v18_ha_desktop_mushroom_cards.png", "06-smart-home-and-energy", "v18-home-assistant-companion-console", "dark", 1440, 900, ""),
        ("07_v18_ha_24h_stacked_energy_echarts.png", "06-smart-home-and-energy", "v18-home-assistant-companion-console", "white", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const e=d.getElementById('v18-energy');if(e)e.scrollIntoView({block:'center'});"),
    ]
    for fname, wid, vw, theme, w, h, js_hook in shots:
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?world={wid}&view={vw}&theme={theme}")
        time.sleep(0.55)
        if js_hook:
            driver.execute_script(js_hook)
            time.sleep(0.45)
        driver.save_screenshot(str(out_dir / fname))

    set_viewport(driver, 1440, 900, 2)
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.4)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    time.sleep(0.85)
    driver.execute_script("""
        const bdoc = document.getElementById('va-stage-portal').contentDocument;
        const wrap = bdoc && bdoc.querySelector('.qe-plot-wrap[data-quiet-echarts]');
        if (!wrap) return;
        const btn = wrap.querySelector('.qe-mode-btn[data-qe-mode="echarts"]');
        if (btn) btn.click();
        const fig = wrap.closest('.qe-figure');
        const drw = fig && fig.querySelector('.qe-eco-drawer');
        if (drw) drw.open = true;
        if (fig) fig.scrollIntoView({block: 'start'});
    """)
    time.sleep(0.45)
    driver.save_screenshot(str(out_dir / "08_components_5tab_ecosystem_drawer.png"))
    set_viewport(driver, 1440, 900, 1)


def capture_gate41_gallery(driver: Any, base_url: str, shots_dir: Path) -> None:
    shots_dir.mkdir(parents=True, exist_ok=True)
    for fname, w, h, qs in (
        ("01_v01_icu_desktop_white.png", 1440, 900, "view=v01-icu-bedside-terminal&theme=white"),
        ("02_v01_icu_desktop_oled.png", 1440, 900, "view=v01-icu-bedside-terminal&theme=dark"),
        ("03_v01_icu_mobile_390x844.png", 390, 844, "view=v01-icu-bedside-terminal&theme=white"),
        ("04_v02_trial_desktop_paper.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=paper"),
        ("05_v02_trial_foldable_840x1050.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=white&vp=840x1050"),
        ("06_v02_trial_m1_print_sheet.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=dark&medium=m1"),
        ("07_v03_patient_desktop_white.png", 1440, 900, "view=v03-patient-recovery-companion&theme=white"),
        ("08_v03_patient_mobile_390x844.png", 390, 844, "view=v03-patient-recovery-companion&theme=white"),
    ):
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?world=01-clinical-icu-and-trials&{qs}")
        time.sleep(0.35)
        driver.save_screenshot(str(shots_dir / fname))
    set_viewport(driver, 1440, 900, 2)
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v02-trial-regulatory-brief&theme=dark-paper")
    time.sleep(0.3)
    driver.execute_script("document.getElementById('va-bridge-btn').click();")
    time.sleep(0.2)
    driver.save_screenshot(str(shots_dir / "09_studio_why_this_view_bridge.png"))


def capture_phase6_gallery(driver: Any, base_url: str, out_dir: Path) -> None:
    """Capture 8 Phase 6 Retina (deviceScaleFactor=2) proof PNGs from live :8788 showcase."""
    out_dir.mkdir(parents=True, exist_ok=True)
    shots = [
        ("01_v02_foldable_840x1050_masthead.png", "01-clinical-icu-and-trials", "v02-trial-regulatory-brief", "white", 840, 1050, ""),
        ("02_v10_civic_waterfall_echarts.png", "04-civic-finance-and-stem-learning", "v10-civic-capital-budget-deck", "white", 1440, 900, ""),
        ("03_v12_stem_rc_lab_residuals.png", "04-civic-finance-and-stem-learning", "v12-stem-interactive-lab", "white", 1440, 900, ""),
        ("04_v13_propulsion_bte_residuals.png", "05-physical-systems-auto-and-aero", "v13-propulsion-archival-monograph", "paper", 1440, 900, ""),
        ("05_v15_hud_daylight_horizon50.png", "05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "white", 1440, 900, ""),
        ("06_v15_hud_nightfall_ils_horizon50.png", "05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "dark", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-backplate='lowlight']\");if(b)b.click();"),
        ("07_v18_ha_companion_stacked_energy.png", "06-smart-home-and-energy", "v18-home-assistant-companion-console", "white", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const e=d.getElementById('v18-energy');if(e)e.scrollIntoView({block:'center'});"),
    ]
    for fname, wid, vw, theme, w, h, hook in shots:
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?world={wid}&view={vw}&theme={theme}")
        time.sleep(0.55)
        if hook:
            driver.execute_script(hook)
            time.sleep(0.45)
        driver.save_screenshot(str(out_dir / fname))
    set_viewport(driver, 1440, 900, 2)
    driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v16-transparent-window-overlay&theme=white")
    time.sleep(0.55)
    driver.save_screenshot(str(out_dir / "08_v16_maritime_glass_daylight.png"))
    set_viewport(driver, 1440, 900, 1)
