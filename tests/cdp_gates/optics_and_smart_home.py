# SPDX-License-Identifier: Apache-2.0
"""CDP visual gates for optical HUD (v15), smart-glass overlay (v16), and smart home (v17, v18)."""

from __future__ import annotations

import time
from typing import Any

from . import set_viewport


def _check_v15_and_v16_optics(driver: Any, base_url: str, errs: list[str]) -> None:
    set_viewport(driver, 1440, 900, 1)
    for wid, vw, btn_sel, mode_val in (
        ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "button[data-backplate='earthrise']", "earthrise"),
        ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "button[data-backplate='lowlight']", "lowlight"),
        ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "button[data-luminance='daylight']", "daylight"),
        ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "button[data-luminance='night']", "night"),
    ):
        driver.get(f"{base_url}?world={wid}&view={vw}&theme=white")
        time.sleep(0.35)
        driver.execute_script(
            "const b=document.getElementById('va-stage-portal').contentDocument.querySelector(arguments[0]);if(b)b.click();",
            btn_sel,
        )
        time.sleep(0.35)
        nw = driver.execute_script(
            "const i=document.getElementById('va-stage-portal').contentDocument.querySelector('img[data-photo-mode=\"'+arguments[0]+'\"]');"
            "return i&&i.complete?i.naturalWidth:0;",
            mode_val,
        )
        if int(nw or 0) < 1200:
            errs.append(f"[PHOTO_LOAD] {vw}/{mode_val} naturalWidth={nw} < 1200")

    driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v15-collimated-flight-hud&theme=dark")
    time.sleep(0.3)
    driver.switch_to.frame("va-stage-portal")
    hud_res = driver.execute_script("""
        const st = document.getElementById('v15-hud-stage');
        if (!st) return 'missing #v15-hud-stage';
        if (document.querySelectorAll('.v15-scene-svg').length) return 'synthetic scene svg present';
        const sr = st.getBoundingClientRect(), tot = sr.width * sr.height;
        let occ = 0;
        for (const el of st.querySelectorAll('.v15-hud-mode-strip, button')) {
            const r = el.getBoundingClientRect();
            occ += Math.max(0, r.width) * Math.max(0, r.height);
        }
        return (tot > 0 && (1 - occ / tot) >= 0.65) ? 'ok' : 'boresight keepout < 65%';
    """)
    driver.switch_to.default_content()
    if hud_res != "ok":
        errs.append(f"[V15_OPTICS] {hud_res}")

    driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v16-transparent-window-overlay&theme=white")
    time.sleep(0.3)
    for lum in ("daylight", "dusk", "night"):
        driver.switch_to.frame("va-stage-portal")
        driver.execute_script(f"document.querySelector('#v16-luminance-chips [data-luminance=\"{lum}\"]').click();")
        time.sleep(0.1)
        g_err = driver.execute_script("""
            const w = window.innerWidth, h = window.innerHeight, kx0 = w * 0.24, kx1 = w * 0.76, ky0 = h * 0.24, ky1 = h * 0.68;
            const lumMode = document.getElementById('v16-glass-viewport')?.dataset?.luminance || 'daylight';
            const scene = lumMode === 'night' ? [15, 23, 42] : (lumMode === 'dusk' ? [180, 83, 9] : [224, 242, 254]);
            const parseRgba = (s) => (s.match(/[\\d.]+/g) || [0, 0, 0, 1]).map(Number);
            const over = (fg, bg) => { const a = fg.length >= 4 ? fg[3] : 1; return [fg[0]*a + bg[0]*(1-a), fg[1]*a + bg[1]*(1-a), fg[2]*a + bg[2]*(1-a)]; };
            const rLum = ([r, g, b]) => { const f = (v) => { const x = v/255; return x <= 0.04045 ? x/12.92 : Math.pow((x+0.055)/1.055, 2.4); }; return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b); };
            for (const pod of document.querySelectorAll('.v16-glass-pod')) {
                const cs = getComputedStyle(pod), pr = pod.getBoundingClientRect();
                if (!(cs.backdropFilter || cs.webkitBackdropFilter || '').includes('blur(')) return 'pod missing blur';
                if (pr.width > 420.5) return 'pod width > 420px';
                if (Math.min(pr.right, kx1) > Math.max(pr.left, kx0) + 1 && Math.min(pr.bottom, ky1) > Math.max(pr.top, ky0) + 1) return 'pod invades windshield corridor';
                const podBg = over(parseRgba(cs.backgroundColor), scene);
                for (const el of pod.querySelectorAll('.v16-speed-val,.v16-route-line,.v16-eff-line,.v16-warn-title,.v16-warn-action')) {
                    const ecs = getComputedStyle(el);
                    if (ecs.display === 'none') continue;
                    const l1 = rLum(over(parseRgba(ecs.backgroundColor), podBg)), l2 = rLum(parseRgba(ecs.color));
                    const cr = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                    if (cr < 7.0) return `scrim contrast ${cr.toFixed(2)} < 7.0 (${lumMode})`;
                }
            }
            if (lumMode === 'night') {
                const db = document.getElementById('v16-derate-btn'), ab = document.getElementById('v16-ais-btn');
                const vp = document.getElementById('v16-glass-viewport');
                if (!db || !ab || !vp) return 'missing derate/ais btns';
                if (ab.getAttribute('aria-pressed') !== 'true' || vp.getAttribute('data-ais') !== 'true') return 'ais default-on missing';
                db.click(); ab.click();
                if (document.querySelectorAll('#v16-luminance-chips .is-active').length !== 1) return 'luminance chip desync';
                if (db.getAttribute('aria-pressed') !== 'true' || ab.getAttribute('aria-pressed') !== 'false') return 'bridge aria desync';
                if (document.getElementById('v16-speed-val').textContent.trim() !== '17.6') return 'derate speed update failed';
                if (document.getElementById('v16-warn-pill').getAttribute('data-state') !== 'nominal') return 'derate state failed';
                if (vp.getAttribute('data-ais') !== 'false') return 'ais toggle-off failed';
                db.click(); ab.click();
                if (db.getAttribute('aria-pressed') !== 'false' || ab.getAttribute('aria-pressed') !== 'true' || vp.getAttribute('data-ais') !== 'true') return 'untoggle aria desync';
                if (document.querySelectorAll('#v16-luminance-chips .is-active').length !== 1) return 'luminance chip desync after untoggle';
            }
            return '';
        """)
        driver.switch_to.default_content()
        if g_err:
            errs.append(f"[V16_OPTICS_{lum.upper()}] {g_err}")


def _check_v17_and_v18_smart_home(driver: Any, base_url: str, errs: list[str]) -> None:
    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v17-picture-frame-home-kiosk&theme=white")
    time.sleep(0.4)
    v17_res = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal')?.contentDocument;
        if (!doc) return 'no doc';
        if (doc.querySelector('.v15-reticle-layer')) return 'forbidden HUD crosshair in v17';
        const txt = doc.body.innerText || '';
        for (const bad of ['ZONE-LIVING', 'LEAK-LOOP-06', 'PANEL-MAIN-200A']) {
            if (txt.includes(bad)) return 'leaked SCADA slug: ' + bad;
        }
        const vp = doc.getElementById('v17-kiosk'), imgArt = doc.getElementById('v17-photo-art');
        if (!vp || !imgArt || !imgArt.complete || imgArt.naturalWidth < 1200) return 'art photo unloaded';
        const vr = vp.getBoundingClientRect();
        let occ = 0;
        doc.querySelectorAll('.v17-glass-pod, .v17-scene-bar').forEach(el => { const r = el.getBoundingClientRect(); occ += Math.max(0, r.width)*Math.max(0, r.height); });
        if ((1 - occ / Math.max(1, vr.width * vr.height)) < 0.76) return 'unobstructed canvas < 76%';
        doc.querySelector('button[data-v17-backdrop="landscape"]').click();
        doc.querySelector('button[data-v17-scene="goodnight"]').click();
        if (!doc.getElementById('v17-clock-time').textContent.includes('10:45')) return 'scene telemetry failed';
        doc.getElementById('v17-sp-up').click();
        if (!doc.getElementById('v17-sp-val').textContent.includes('21.5')) return 'setpoint nudge failed';
        doc.getElementById('v17-mat-btn').click();
        if (vp.getAttribute('data-v17-mat') !== 'obsidian') return 'mat toggle failed';
        doc.getElementById('v17-unit-btn').click();
        if (!vp.innerText.includes('71 °F')) return 'unit toggle failed';
        doc.getElementById('v17-sp-up').click();
        return doc.getElementById('v17-sp-val').textContent.trim() === '72 °F' ? 'ok' : 'F setpoint step failed';
    """)
    time.sleep(0.3)
    if v17_res != "ok":
        errs.append(f"[V17_KIOSK] {v17_res}")
    else:
        land_nw = driver.execute_script(
            "const i=document.getElementById('va-stage-portal').contentDocument.getElementById('v17-photo-landscape');"
            "return i&&i.complete?i.naturalWidth:0;"
        )
        if int(land_nw or 0) < 1200:
            errs.append(f"[V17_LANDSCAPE] naturalWidth={land_nw} < 1200")

    set_viewport(driver, 390, 844, 1)
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v17-picture-frame-home-kiosk&theme=white")
    time.sleep(0.4)
    v17_mob = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal').contentDocument;
        const fr = doc.getElementById('v17-kiosk'), im = doc.getElementById('v17-photo-art');
        if (doc.documentElement.scrollWidth > doc.documentElement.clientWidth + 1) return 'mobile x-overflow';
        return (im.getBoundingClientRect().height / Math.max(1, fr.getBoundingClientRect().height)) >= 0.82 ? 'ok' : 'mobile fill < 0.82';
    """)
    if v17_mob != "ok":
        errs.append(f"[V17_MOBILE] {v17_mob}")

    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&theme=white")
    time.sleep(0.4)
    v18_mob = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal').contentDocument;
        if (doc.documentElement.dataset.effectiveNav !== 'n4') return 'expected n4 nav';
        if (doc.documentElement.scrollWidth > doc.documentElement.clientWidth + 1) return 'mobile x-overflow';
        const btn = doc.getElementById('v18-lock-arm');
        return btn && btn.getBoundingClientRect().height >= 43.5 ? 'ok' : 'touch target < 44px';
    """)
    if v18_mob != "ok":
        errs.append(f"[V18_MOBILE] {v18_mob}")

    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?world=06-smart-home-and-energy&view=v18-home-assistant-companion-console&theme=white")
    time.sleep(0.5)
    v18_desk = driver.execute_script("""
        const doc = document.getElementById('va-stage-portal').contentDocument;
        const txt = doc.body.innerText || '';
        for (const bad of ['PANEL-MAIN-200A', 'PV-STRING-SOUTH', 'LOCK-FRONT-01', 'GARAGE-BAY-01', 'HOME-DER-PANEL']) {
            if (txt.includes(bad)) return 'leaked SCADA slug: ' + bad;
        }
        const wrap = doc.querySelector('#v18-energy .qe-plot-wrap');
        if (!wrap || wrap.dataset.echartsActive !== 'true') return 'stacked ECharts inactive';
        doc.querySelector('button[data-v18-unit="f"]').click();
        if (!doc.getElementById('v18-rooms').innerText.includes('71 °F')) return 'F/C switch failed';
        const arm1 = doc.getElementById('v18-lock-arm'), ex1 = doc.getElementById('v18-lock-exec');
        if (!arm1 || !ex1 || !ex1.disabled) return 'lock not guarded';
        arm1.click(); if (ex1.disabled) return 'lock arm failed';
        ex1.click();
        if (doc.getElementById('v18-lock-pill').textContent.trim() !== 'UNLOCKED' || !ex1.disabled) return 'lock re-guard failed';
        doc.getElementById('v18-garage-arm').click(); doc.getElementById('v18-garage-exec').click();
        if (doc.getElementById('v18-garage-pill').textContent.trim() !== 'OPEN') return 'garage unlock failed';
        doc.querySelector('button[data-v18-filter="climate"]').click();
        return [...doc.querySelectorAll('.v18-zone-tile')].filter(el => !el.hasAttribute('hidden')).length === 2 ? 'ok' : 'filter failed';
    """)
    if v18_desk != "ok":
        errs.append(f"[V18_DESKTOP] {v18_desk}")


def run_optics_and_smart_home_gates(driver: Any, base_url: str) -> list[str]:
    """Run Domain 05 optical (v15, v16) and Domain 06 smart-home (v17, v18) CDP checks."""
    errs: list[str] = []
    _check_v15_and_v16_optics(driver, base_url, errs)
    _check_v17_and_v18_smart_home(driver, base_url, errs)
    set_viewport(driver, 1440, 900, 1)
    return errs
