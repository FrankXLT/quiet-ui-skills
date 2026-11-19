# SPDX-License-Identifier: Apache-2.0
"""Gates 18 to 21 for Quiet UI v9.0 (6-Domain x 18-View Substance, Tables, Halos & Domain 06 HA)."""

from __future__ import annotations

from pathlib import Path
from selenium import webdriver

from .selenium_gates import select_tier, set_cdp_viewport, switch_to_outer, switch_to_portal


def _get_manifest_views(driver: webdriver.Chrome) -> list[str]:
    switch_to_outer(driver)
    return list(
        driver.execute_script(
            "const m=JSON.parse(document.getElementById('va-v9-manifest').textContent||'{\"worlds\":[]}');"
            "return m.worlds.flatMap(w=>(w.views||[]).map(v=>v.view_id));"
        )
        or []
    )


def check_gate_18_desktop_tables(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 18: Unclipped desktop tables (>= 1440px) across all views in #va-v9-manifest."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    driver.get(base_url)
    for vid in _get_manifest_views(driver):
        select_tier(driver, vid)
        if not switch_to_portal(driver):
            continue
        t_errs = driver.execute_script("""
            const vid = arguments[0], errs = [];
            for (const wrap of document.querySelectorAll('.va-table-wrap')) {
                if (wrap.offsetParent !== null && wrap.scrollWidth > wrap.clientWidth + 2) {
                    errs.push(`${vid}: table scrollWidth ${wrap.scrollWidth} > ${wrap.clientWidth}`);
                }
            }
            return errs;
        """, vid)
        errors.extend(f"[GATE_18_TABLES] {e}" for e in t_errs)
    switch_to_outer(driver)
    return errors


def check_gate_19_svg_text_halos(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 19: Zero internal figure badges or unmasked legacy pills across schematic/plot views."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    for vid in ("v02-trial-regulatory-brief", "v05-zero-trust-ato-spec", "v07-grid-scada-poi-console", "v14-fieldbus-and-scope-debugger"):
        select_tier(driver, vid)
        if switch_to_portal(driver):
            bad = driver.execute_script("""
                if (document.querySelectorAll('.qe-card-head .va-pill').length) return 'internal card pill rendered';
                if (document.querySelectorAll('.qe-label-pill').length) return 'legacy label pill rendered';
                return '';
            """)
            if bad:
                errors.append(f"[GATE_19_HALOS_{vid}] {bad}")
    switch_to_outer(driver)
    return errors


def check_gate_20_domain_layout(driver: webdriver.Chrome, base_url: str) -> list[str]:
    """Gate 20: Verify Domain 06 (v17 Framed Gallery & v18 HA Companion Stacked Energy + 2-Step Doors)."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    select_tier(driver, "v17-picture-frame-home-kiosk")
    if switch_to_portal(driver):
        if not driver.execute_script("const i=document.querySelector('.v17-mat-window img.v17-art-photo.is-active'); return !!(i && i.complete && i.naturalWidth > 0);"):
            errors.append("[GATE_20_V17] Missing or unloaded v17 picture-frame gallery photograph")
    select_tier(driver, "v18-home-assistant-companion-console")
    if switch_to_portal(driver):
        v18_err = driver.execute_script("""
            const p = document.querySelector('.qe-plot-wrap[data-quiet-echarts]');
            const pld = p ? JSON.parse(p.dataset.quietEcharts || '{}') : {};
            if (pld.kind !== 'stacked_bar') return 'expected stacked_bar in v18';
            const arm = document.getElementById('v18-lock-arm'), ex = document.getElementById('v18-lock-exec');
            if (!arm || !ex || !ex.disabled || !arm.textContent.includes('Tap to Unlock')) return '2-step lock UI mismatch';
            arm.click(); if (ex.disabled) return 'Step 1 did not enable Step 2';
            ex.click(); return document.getElementById('v18-lock-pill')?.textContent.trim() === 'UNLOCKED' ? '' : 'Step 2 unlock failed';
        """)
        if v18_err:
            errors.append(f"[GATE_20_V18] {v18_err}")
    switch_to_outer(driver)
    return errors


def check_gate_21_substance_landmarks(driver: webdriver.Chrome, base_url: str, repo_root: Path) -> list[str]:
    """Gate 21: All 6 Domains x 18 Views and Why? modal mount cleanly with zero taxonomy or robot-speak leaks."""
    errors: list[str] = []
    set_cdp_viewport(driver, 1440, 900)
    views = _get_manifest_views(driver)
    if len(views) != 18:
        errors.append(f"[GATE_21_MANIFEST] Expected 18 views across 6 domains, found {len(views)}")
    leak_re = r"\b(?:L[123]|M[1-7]|N[0-4])\b|\[data-term\]|\bBooktabs\b|\bHome Nominal\b|\bUnlock Arm\b|\bArm Door\b|PANEL-MAIN-200A|ZONE-LIVING|LOCK-FRONT-01"
    for vid in views:
        select_tier(driver, vid)
        if not switch_to_portal(driver):
            continue
        leak = driver.execute_script(f"""
            const txt = document.body.innerText || '';
            const m = txt.match(/{leak_re}/);
            return m ? m[0] : (txt.trim().length < 25 ? 'EMPTY_VIEW' : '');
        """)
        if leak:
            errors.append(f"[GATE_21_LEAK_{vid}] {leak}")
        switch_to_outer(driver)
        dlg_leak = driver.execute_script(f"""
            const btn = document.getElementById('va-bridge-btn'), dlg = document.getElementById('va-bridge-dialog');
            if (!btn || !dlg) return 'MISSING_BRIDGE_DIALOG';
            btn.click();
            const txt = dlg.innerText || '';
            const m = txt.match(/{leak_re}/);
            dlg.close();
            return m ? m[0] : (txt.trim().length < 30 ? 'EMPTY_BRIDGE_DIALOG' : '');
        """)
        if dlg_leak:
            errors.append(f"[GATE_21_WHY_LEAK_{vid}] {dlg_leak}")
    try:
        severe = [l for l in driver.get_log("browser") if l.get("level") == "SEVERE" and "favicon.ico" not in l.get("message", "")]
        if severe:
            errors.append(f"[CONSOLE_SEVERE_FINAL] {severe[0].get('message')}")
    except Exception:
        pass
    return errors


def run_flagship_craft_gates(driver: webdriver.Chrome, base_url: str, repo_root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(check_gate_18_desktop_tables(driver, base_url))
    errors.extend(check_gate_19_svg_text_halos(driver, base_url))
    errors.extend(check_gate_20_domain_layout(driver, base_url))
    errors.extend(check_gate_21_substance_landmarks(driver, base_url, repo_root))
    return errors
