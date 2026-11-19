#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.4 — Domain 06, ECharts & 8-Shot Retina Proof Helpers (<= 260L)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from verify_v9_helpers import set_viewport


def _check_v17_and_v18(driver: Any, base_url: str, errs: list[str]) -> None:
    set_viewport(driver, 1440, 900, 1)
    # v17: picture-frame ambient kiosk, >= 68% unobstructed canvas, zero HUD crosshairs
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v17-picture-frame-home-kiosk&theme=white")
    time.sleep(0.45)
    v17_res = driver.execute_script("""
        const f = document.getElementById('va-stage-portal');
        const doc = f && f.contentDocument;
        if (!doc) return 'no doc';
        if (doc.querySelector('.v15-reticle-layer')) return 'forbidden HUD crosshair in v17';
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
        if (freeRatio < 0.68) return 'unobstructed art ratio too low: ' + freeRatio.toFixed(3);
        const lBtn = doc.querySelector('button[data-v17-backdrop="landscape"]');
        const sBtn = doc.querySelector('button[data-v17-scene="night-quiet"]');
        if (!lBtn || !sBtn) return 'missing v17 backdrop/scene controls';
        lBtn.click(); sBtn.click();
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

    # v18 Mobile (390x844 -> N4 dock + >=44px targets + 0 overflow) & Desktop 2-step interlocks
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
    # Verify remaining swapped modes on v15/v16 load cleanly >= 1200px
    for wid, vw, btn_sel, mode_val in (
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

    # Verify Apache ECharts SVG mounts and re-themes white -> dark + M1 fallback
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
            const host = doc && doc.querySelector('.qe-plot-wrap[data-echarts-active="true"] .qe-echarts-host svg');
            return !!host;
        """)
        if not ec_ok:
            errs.append(f"[ECHARTS_MOUNT] {vw}: live ECharts SVG did not mount")
            continue
        driver.execute_script("window.QuietStudioPortalV9.state.theme='dark'; window.QuietStudioPortalV9.applyState(false);")
        time.sleep(0.35)
        dark_ok = driver.execute_script("""
            const doc = document.getElementById('va-stage-portal').contentDocument;
            return !!(doc && doc.documentElement.dataset.theme === 'dark' && doc.querySelector('.qe-echarts-host svg'));
        """)
        if not dark_ok:
            errs.append(f"[ECHARTS_RETHEME] {vw}: failed dark retheme with live ECharts")

    # M1 print fallback restores .qe-svg-fallback
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

    # Bench Components toggle & Ecosystem Config drawer check via Studio Components tab
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.35)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    time.sleep(0.75)
    bench_ok = driver.execute_script("""
        const bdoc = document.getElementById('va-stage-portal').contentDocument;
        if (!bdoc) return 'no bench doc';
        const btn = bdoc.querySelector('.qe-plot-wrap .qe-mode-btn[data-qe-mode="echarts"]');
        const drw = bdoc.querySelector('.qe-eco-drawer');
        if (!btn || !drw) return 'missing toggle or eco drawer';
        btn.click(); drw.open = true;
        const wrap = btn.closest('.qe-plot-wrap');
        if (!wrap || wrap.dataset.echartsActive !== 'true' || !wrap.querySelector('.qe-echarts-host svg')) return 'bench echarts failed';
        if (!drw.textContent.includes('Plotly') || !drw.textContent.includes('Matplotlib')) return 'missing adapter code';
        return 'ok';
    """)
    if bench_ok != "ok":
        errs.append(f"[BENCH_ECHARTS] {bench_ok}")


def run_domain06_and_echarts_checks(driver: Any, base_url: str, root_url: str) -> list[str]:
    """Execute Gate 5.4 CDP checks for Domain 06, 8 photos, and Apache ECharts."""
    errs: list[str] = []
    _check_v17_and_v18(driver, base_url, errs)
    _check_all_8_photos_and_echarts(driver, base_url, errs)
    set_viewport(driver, 1440, 900, 1)
    return errs


def capture_gate54_gallery(driver: Any, base_url: str, out_dir: Path) -> None:
    """Capture 8 Retina (deviceScaleFactor=2) proof PNGs into session brain screenshots_gate54."""
    out_dir.mkdir(parents=True, exist_ok=True)
    shots = [
        ("01_v15_hud_night_unobstructed_runway.png", "05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "dark", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-backplate='lowlight']\");if(b)b.click();"),
        ("02_v16_glass_daylight_bridge_refraction.png", "05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "white", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-luminance='daylight']\");if(b)b.click();"),
        ("03_v16_glass_night_driver_pov.png", "05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "dark", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-luminance='night']\");if(b)b.click();"),
        ("04_v17_ha_picture_frame_fine_art.png", "06-smart-home-and-energy", "v17-picture-frame-home-kiosk", "white", 1440, 900, ""),
        ("05_v17_ha_picture_frame_landscape.png", "06-smart-home-and-energy", "v17-picture-frame-home-kiosk", "white", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const b=d.querySelector(\"button[data-v17-backdrop='landscape']\");if(b)b.click();"),
        ("06_v18_ha_desktop_console_echarts.png", "06-smart-home-and-energy", "v18-home-assistant-companion-console", "dark", 1440, 900,
         "const d=document.getElementById('va-stage-portal').contentDocument;const e=d.getElementById('v18-rooms');if(e)e.scrollIntoView({block:'start'});"),
        ("07_v18_ha_mobile_390x844_companion.png", "06-smart-home-and-energy", "v18-home-assistant-companion-console", "white", 390, 844, ""),
    ]
    for fname, wid, vw, theme, w, h, js_hook in shots:
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?world={wid}&view={vw}&theme={theme}")
        time.sleep(0.55)
        if js_hook:
            driver.execute_script(js_hook)
            time.sleep(0.45)
        driver.save_screenshot(str(out_dir / fname))

    # Shot 08: Studio Components tab with Live Apache ECharts + open Ecosystem Config drawer
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
    driver.save_screenshot(str(out_dir / "08_components_live_echarts_and_adapters.png"))
    set_viewport(driver, 1440, 900, 1)
