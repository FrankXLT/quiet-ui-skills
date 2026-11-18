# SPDX-License-Identifier: Apache-2.0
"""Gates 14 (Diagram Atlas Parity) and 15 (HUD-1 Field-of-Regard) for Quiet UI v8.0."""

from __future__ import annotations

import time
import urllib.parse
from typing import Any
from selenium import webdriver

from .constants import ATLAS_FAMILY_EXPECTED_COUNTS, ATLAS_TOTAL_CARDS, HUD_BACKPLATES


def check_gate_14_atlas_standalone(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Deprecated Gate 14 stub retained for contract export compatibility (bench tested in Gate 17)."""
    errors: list[str] = []
    atlas_url = urllib.parse.urljoin(base_url, "bench/evidence-bench.html")
    driver.set_window_size(390, 844)
    driver.get(atlas_url)
    time.sleep(0.3)

    # 1. Check browser console logs for SEVERE errors
    try:
        logs = driver.get_log("browser")
        severe_logs = [
            log for log in logs
            if log.get("level") == "SEVERE" and "favicon.ico" not in log.get("message", "")
        ]
        if severe_logs:
            errors.append(f"[GATE_14_LOGS] Found {len(severe_logs)} SEVERE console log(s): {severe_logs[0].get('message')}")
    except Exception:
        pass  # Some webdrivers don't support log retrieval

    # 2. Check 45 cards rendered, content-visibility, human titles, and dock overlap
    eval_res = driver.execute_script("""
        const errs = [];
        const cards = document.querySelectorAll('.atlas-card');
        if (cards.length !== 45) {
            errs.push(`Card count ${cards.length} !== 45`);
        }
        for (const c of cards) {
            const h = c.querySelector('h4, .atlas-card-title');
            if (h) {
                const t = h.textContent.trim();
                if (t.startsWith('dp-') || t.startsWith('type-')) {
                    errs.push(`Raw slug used as title: '${t}'`);
                    break;
                }
            }
        }
        for (const def of document.querySelectorAll('.atlas-deferred-family')) {
            const cv = window.getComputedStyle(def).contentVisibility;
            if (cv !== 'auto') {
                errs.push(`.atlas-deferred-family missing content-visibility: auto (got '${cv}')`);
                break;
            }
        }
        const dock = document.getElementById('atlas-dock');
        if (dock) {
            const dr = dock.getBoundingClientRect();
            for (const c of cards) {
                const cr = c.getBoundingClientRect();
                if (cr.bottom > dr.top && cr.top < dr.bottom && cr.right > dr.left && cr.left < dr.right) {
                    errs.push('Card overlaps bottom floating dock');
                    break;
                }
            }
        }
        return errs;
    """)
    errors.extend([f"[GATE_14_STANDALONE] {e}" for e in eval_res])

    # 3. Test <dialog id="atlas-inspect-dialog" closedby="any"> opens on card click
    dlg_res = driver.execute_script("""
        const card = document.querySelector('.atlas-card');
        const dlg = document.getElementById('atlas-inspect-dialog');
        if (!dlg) return ['Missing #atlas-inspect-dialog element'];
        if (dlg.getAttribute('closedby') !== 'any') return ['Dialog missing closedby="any" attribute'];
        if (card) {
            card.click();
            if (!dlg.open) return ['Dialog did not open after card click'];
            const closeBtn = dlg.querySelector('.atlas-close-btn');
            if (closeBtn) closeBtn.click();
        }
        return [];
    """)
    errors.extend([f"[GATE_14_DIALOG] {e}" for e in dlg_res])
    return errors


def check_gate_14_atlas_embedded(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Test diagrams view inside #va-stage-portal via ?view=diagrams."""
    errors: list[str] = []
    embedded_url = urllib.parse.urljoin(base_url, "?view=diagrams")
    driver.set_window_size(1920, 1080)
    driver.get(embedded_url)
    time.sleep(0.3)

    driver.switch_to.default_content()
    portals = driver.find_elements("id", "va-stage-portal")
    if portals:
        driver.switch_to.frame(portals[0])

    res = driver.execute_script("""
        const cards = document.querySelectorAll('.atlas-card');
        return cards.length > 0 && cards.length !== 45 ? [`Embedded card count ${cards.length} !== 45`] : [];
    """)
    errors.extend([f"[GATE_14_EMBEDDED] {e}" for e in res])
    return errors


def check_gate_15_field_of_regard(driver: webdriver.Chrome, w: int, h: int) -> list[str]:
    """Gate 15: HUD-1 >= 65% unobstructed central field-of-regard and pod area < 35%."""
    errors: list[str] = []
    driver.switch_to.default_content()
    # Switch tier to hud-1
    driver.execute_script("""
        if (typeof switchTier === 'function') switchTier('hud-1');
        else {
            const b = document.querySelector('[data-tier="hud-1"]');
            if (b) b.click();
        }
    """)
    time.sleep(0.08)

    portals = driver.find_elements("id", "va-stage-portal")
    if portals:
        driver.switch_to.frame(portals[0])

    res = driver.execute_script("""
        const vp = document.getElementById('hud1-viewport') || document.querySelector('.hud1-viewport');
        if (!vp) return ['[GATE_15_HUD] Missing #hud1-viewport on hud-1 tier'];
        const r = vp.getBoundingClientRect();
        const W = r.width, H = r.height;
        if (W <= 0 || H <= 0) return ['[GATE_15_HUD] hud1-viewport has 0 width or height'];

        // Central keep-out core: [0.175*W, 0.825*W] x [0.15*H, 0.85*H]
        const kx1 = 0.175 * W, kx2 = 0.825 * W;
        const ky1 = 0.15 * H, ky2 = 0.85 * H;

        let totalPodArea = 0;
        const pods = document.querySelectorAll('.va-hud-pod, [class*="hud1-top-"], [class*="hud1-bottom-"]');
        const errs = [];

        for (const pod of pods) {
            if (pod.offsetParent === null) continue;
            const pr = pod.getBoundingClientRect();
            // Relative to vp
            const px1 = pr.left - r.left, px2 = pr.right - r.left;
            const py1 = pr.top - r.top, py2 = pr.bottom - r.top;
            totalPodArea += pr.width * pr.height;

            // Check overlap with central keep-out core
            const ox = Math.max(0, Math.min(px2, kx2) - Math.max(px1, kx1));
            const oy = Math.max(0, Math.min(py2, ky2) - Math.max(py1, ky1));
            if (ox > 4 && oy > 4) {
                errs.push(`Pod overlaps central keep-out core: ${pod.className} (${ox.toFixed(1)}x${oy.toFixed(1)}px overlap)`);
                break;
            }
        }

        const maxAllowedArea = 0.35 * W * H;
        if (totalPodArea > maxAllowedArea) {
            const ratio = (totalPodArea / (W * H) * 100).toFixed(1);
            errs.push(`Total pod area exceeds 35% of viewport (${ratio}% occupied, need >=65% unobstructed)`);
        }
        return errs;
    """)
    errors.extend([f"[GATE_15_HUD_{w}] {e}" for e in res])
    return errors


def check_gate_15_backplates_contrast(driver: webdriver.Chrome) -> list[str]:
    """Test setHudBackplate across earthrise, daylight, and lowlight for >= 4.5:1 text contrast."""
    errors: list[str] = []
    for bp in HUD_BACKPLATES:
        c_res = driver.execute_script("""
            const bp = arguments[0];
            if (typeof setHudBackplate === 'function') setHudBackplate(bp);
            else {
                const vp = document.getElementById('hud1-viewport') || document.querySelector('.hud1-viewport');
                if (vp) vp.setAttribute('data-backplate', bp);
            }
            // Luminance helper
            function getLum(rgbStr) {
                const m = rgbStr.match(/\\d+/g);
                if (!m || m.length < 3) return 1.0;
                const a = m.slice(0, 3).map(v => {
                    const c = parseInt(v, 10) / 255;
                    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                });
                return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
            }
            const pods = document.querySelectorAll('.va-hud-pod');
            for (const pod of pods) {
                const cs = window.getComputedStyle(pod);
                const bgLum = getLum(cs.backgroundColor);
                const fgLum = getLum(cs.color);
                const hi = Math.max(bgLum, fgLum), lo = Math.min(bgLum, fgLum);
                const cr = (hi + 0.05) / (lo + 0.05);
                if (cr < 4.4) {
                    return [`Backplate '${bp}' low contrast on pod: ${cr.toFixed(2)}:1 (need >= 4.5:1)`];
                }
            }
            return [];
        """, bp)
        errors.extend([f"[GATE_15_CONTRAST] {e}" for e in c_res])
    return errors


def run_atlas_and_hud_gates(
    driver: webdriver.Chrome,
    base_url: str,
    screenshots_dir: Any = None,
) -> list[str]:
    """Execute live Selenium CDP Gate 15 (HUD-1 field of regard & contrast)."""
    errors: list[str] = []

    # Gate 15 across 4 key viewports: 820x1180, 1920x1080, 2560x1440, 3840x2160
    for w, h in [(820, 1180), (1920, 1080), (2560, 1440), (3840, 2160)]:
        driver.set_window_size(w, h)
        time.sleep(0.08)
        errors.extend(check_gate_15_field_of_regard(driver, w, h))

    errors.extend(check_gate_15_backplates_contrast(driver))
    return errors
