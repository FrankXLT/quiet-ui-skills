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

    set_viewport(driver, 390, 844, 1)
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v17-picture-frame-home-kiosk&theme=white")
    time.sleep(0.45)
    v17_mob = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal').contentDocument;
        if (!doc) return 'no doc';
        if (doc.documentElement.scrollWidth > doc.documentElement.clientWidth + 1) return 'v17 mobile x-overflow';
        const fr = doc.getElementById('v17-kiosk'), im = doc.getElementById('v17-photo-art');
        if (!fr || !im) return 'missing v17 elements';
        const ratio = im.getBoundingClientRect().height / Math.max(1, fr.getBoundingClientRect().height);
        return ratio >= 0.82 ? 'ok' : 'imgRect/frameRect=' + ratio.toFixed(3) + ' < 0.82';
    """)
    if v17_mob != "ok":
        errs.append(f"[V17_MOBILE_FILL] {v17_mob}")

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


def _check_phase62_directional_views(driver: Any, base_url: str, errs: list[str]) -> None:
    set_viewport(driver, 1440, 900, 1)
    # v19: ECharts Gantt active + filter/click triage rows
    driver.get(f"{base_url}?world=02-cloud-cyber-and-ai-ops&view=v19-product-roadmap-and-triage&theme=white")
    time.sleep(0.55)
    v19_res = driver.execute_script("""
        const d = document.getElementById('va-stage-portal')?.contentDocument;
        if (!d) return 'no doc';
        const wrap = d.querySelector('#v19-gantt .qe-plot-wrap');
        if (!wrap || wrap.dataset.echartsActive !== 'true' || !wrap.querySelector('.qe-echarts-host svg')) return 'v19 gantt echarts inactive';
        const rows = d.querySelectorAll('#v19-triage .v9-triage-row');
        if (rows.length !== 4) return 'expected 4 triage rows, got ' + rows.length;
        rows[2].click();
        if (!(d.getElementById('v19-triage-detail')?.textContent || '').includes('+3.0 d')) return 'v19 triage click failed';
        d.querySelector('#v19-filter-chips [data-v19-filter="blocked"]')?.click();
        const vis = [...rows].filter(r => !r.hidden).length;
        return vis === 2 ? 'ok' : 'expected 2 filtered rows, got ' + vis;
    """)
    if v19_res != "ok":
        errs.append(f"[V19_PLANNER] {v19_res}")

    # v20: Student upward rubric chips & M1 print compatibility + ECharts dumbbell/scope
    driver.get(f"{base_url}?world=04-civic-finance-and-stem-learning&view=v20-student-capstone-lab-report&theme=paper")
    time.sleep(0.55)
    v20_res = driver.execute_script("""
        const d = document.getElementById('va-stage-portal')?.contentDocument;
        if (!d) return 'no doc';
        const wraps = [...d.querySelectorAll('#v20-evidence .qe-plot-wrap')];
        if (wraps.length !== 2 || !wraps.every(w => w.dataset.echartsActive === 'true')) return 'v20 echarts not active on both plots';
        d.querySelector('#v20-rubric-chips [data-v20-focus="error"]')?.click();
        return (d.getElementById('v20-focus-note')?.textContent || '').includes('Error Bounds') ? 'ok' : 'v20 rubric toggle failed';
    """)
    if v20_res != "ok":
        errs.append(f"[V20_STUDENT] {v20_res}")

    # v21: Field Tech isolation tabs, 8.0h recovery Gantt & systems escalation confirm
    driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v21-field-anomaly-escalation-tsn&theme=dark")
    time.sleep(0.55)
    v21_res = driver.execute_script("""
        const d = document.getElementById('va-stage-portal')?.contentDocument;
        if (!d) return 'no doc';
        const wrap = d.querySelector('#v21-recovery .qe-plot-wrap');
        if (!wrap || wrap.dataset.echartsActive !== 'true') return 'v21 recovery gantt echarts inactive';
        d.querySelector('#v21-step-chips [data-v21-step="thermal"]')?.click();
        const tp = d.querySelector('[data-v21-panel="thermal"]');
        if (!tp || tp.hidden) return 'v21 thermal step panel stayed hidden';
        d.getElementById('v21-handoff-arm')?.click();
        d.getElementById('v21-handoff-send')?.click();
        return (d.getElementById('v21-handoff-status')?.textContent || '').includes('HANDOFF SENT') ? 'ok' : 'v21 escalation handoff failed';
    """)
    if v21_res != "ok":
        errs.append(f"[V21_TSN] {v21_res}")


def run_domain06_and_echarts_checks(driver: Any, base_url: str, root_url: str) -> list[str]:
    """Execute Gate 5.5/6.2 CDP checks for Domain 06, 8 photos, single-legend ECharts, v19-v21 & 5-tab Bench."""
    errs: list[str] = []
    _check_v17_and_v18(driver, base_url, errs)
    _check_all_8_photos_and_echarts(driver, base_url, errs)
    _check_phase62_directional_views(driver, base_url, errs)
    set_viewport(driver, 1440, 900, 1)
    return errs


def capture_gate41_gallery(driver: Any, base_url: str, shots_dir: Path) -> None:
    """Capture Gate 4.1 World 01 Retina proof screenshots."""
    shots_dir.mkdir(parents=True, exist_ok=True)
    for fname, w, h, qs in (
        ("01_v01_icu_desktop_white.png", 1440, 900, "view=v01-icu-bedside-terminal&theme=white"),
        ("02_v01_icu_desktop_oled.png", 1440, 900, "view=v01-icu-bedside-terminal&theme=dark"),
        ("03_v01_icu_mobile_390x844.png", 390, 844, "view=v01-icu-bedside-terminal&theme=white"),
        ("04_v02_trial_desktop_paper.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=paper"),
    ):
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?world=01-clinical-icu-and-trials&{qs}")
        time.sleep(0.35)
        driver.save_screenshot(str(shots_dir / fname))
    set_viewport(driver, 1440, 900, 1)


def capture_phase6_gallery(driver: Any, base_url: str, out_dir: Path) -> None:
    """Capture 8 Phase 6.1 & 6.2 Retina (deviceScaleFactor=2) proof PNGs into screenshots_phase62."""
    out_dir.mkdir(parents=True, exist_ok=True)
    comp_shots = [
        ("01_components_gantt_and_heatmap_echarts.png", "bench-25-m4-schedule-gantt", "M4", True),
        ("02_components_dumbbell_and_forest_plots.png", "bench-23-m4-dumbbell-12", "M4", False),
        ("03_components_ui_controls_and_pills.png", "ui-pill-and-status-grammar", "UI", False),
        ("04_components_triage_and_tree_explorer.png", "ui-compact-triage-queue", "UI", False),
    ]
    for fname, focus_id, mod_val, enable_ec in comp_shots:
        set_viewport(driver, 1440, 900, 2)
        driver.get(f"{base_url}?mode=components&theme=white")
        time.sleep(0.85)
        driver.execute_script(
            "const bd=document.getElementById('va-stage-portal').contentDocument;"
            "const sel=bd.getElementById('bench-modality-filter');"
            "if(sel){sel.value=arguments[1];sel.dispatchEvent(new Event('change'));}"
            "if(arguments[2]){bd.querySelectorAll('.qe-mode-btn[data-qe-mode=\"echarts\"]').forEach(b=>b.click());}"
            "const el=bd.getElementById(arguments[0]);if(el)el.scrollIntoView({block:'start'});",
            focus_id, mod_val, enable_ec,
        )
        time.sleep(0.4)
        driver.save_screenshot(str(out_dir / fname))

    stage_shots = [
        ("05_v19_saas_release_gantt_and_triage.png", "02-cloud-cyber-and-ai-ops", "v19-product-roadmap-and-triage", "white", 1440, 900),
        ("06_v20_student_capstone_lab_report.png", "04-civic-finance-and-stem-learning", "v20-student-capstone-lab-report", "paper", 1440, 900),
        ("07_v21_field_tech_escalation_tsn.png", "05-physical-systems-auto-and-aero", "v21-field-anomaly-escalation-tsn", "dark", 1440, 900),
        ("08_v19_mobile_390x844_responsive.png", "02-cloud-cyber-and-ai-ops", "v19-product-roadmap-and-triage", "white", 390, 844),
    ]
    for fname, wid, vw, theme, w, h in stage_shots:
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?world={wid}&view={vw}&theme={theme}")
        time.sleep(0.6)
        driver.save_screenshot(str(out_dir / fname))
    set_viewport(driver, 1440, 900, 1)

