# SPDX-License-Identifier: Apache-2.0
"""Studio Chrome, 21-View x 5-Viewport Continuum, Interactions, Starters & Deep-Link CDP Gates."""

from __future__ import annotations

import time
from typing import Any

from . import ALL_WORLDS_VIEWS, ROOT_FONT_SCALE_TARGETS, select_view, set_viewport

STAGE_AUDIT_JS = """
const errs = [], view = document.documentElement.dataset.view || '', med = document.documentElement.dataset.medium || '', w = window.innerWidth;
const bodyTxt = document.body.innerText || '';
if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)
  errs.push(`[OVERFLOW] ${view} @${w}: ${document.documentElement.scrollWidth} > ${document.documentElement.clientWidth}`);
if (w >= 700) {
  const dock = document.getElementById('va-shell-bottomdock');
  if ((dock && getComputedStyle(dock).display !== 'none') || document.documentElement.dataset.effectiveNav === 'n4')
    errs.push(`[N4_BAN] Bottom dock active at ${w}`);
}
if (w >= 1280) {
  for (const wrap of document.querySelectorAll('.va-table-wrap')) {
    const tbl = wrap.querySelector('table');
    if (tbl && wrap.offsetParent !== null && tbl.scrollWidth > wrap.clientWidth + 2) errs.push(`[TABLE_CLIP] ${view}: ${tbl.scrollWidth} > ${wrap.clientWidth}`);
  }
}
if (w >= 3800 && parseFloat(getComputedStyle(document.documentElement).fontSize) < 21.0) errs.push('[4K_SCALE] root font < 21px');
if ([390, 840, 1440, 1920, 3840].includes(w)) {
  for (const el of document.querySelectorAll('.va-figure-scroll, .qe-scalar-card')) {
    if (getComputedStyle(el).display !== 'none' && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1)
      errs.push(`[INNER_SCROLL] ${view} @${w}: ${el.className} ${el.scrollWidth} > ${el.clientWidth}`);
  }
  for (const svg of document.querySelectorAll('svg')) {
    const sr = svg.getBoundingClientRect();
    if (sr.width < 20 || sr.height < 10) continue;
    if (svg.getAttribute('preserveAspectRatio') === 'none') errs.push(`[SVG_ASPECT] ${view}`);
    for (const t of svg.querySelectorAll('text')) {
      if (!t.textContent?.trim() || getComputedStyle(t).display === 'none') continue;
      const tr = t.getBoundingClientRect();
      if (tr.width > 0 && (tr.left < sr.left - 2 || tr.right > sr.right + 2 || tr.top < sr.top - 2 || tr.bottom > sr.bottom + 2))
        errs.push(`[SVG_CLIP] ${view} @${w}: '${t.textContent.trim().slice(0, 18)}'`);
    }
  }
}
for (const leak of ['Quiet Cockpit','Pedagogical Flow','Decision Contrast','Walk-Up Bedside','PlainLanguage.gov','FDA IEC 62366','T1 GATE','STROKE-ONLY PHOSPHOR','WCAG AAA','QUIET-BRIDGE','Murder-Board','Qualification Bench','Booktabs','Home Nominal','Unlock Arm','Arm Door'])
  if (bodyTxt.includes(leak)) errs.push(`[LEAK] ${view}: '${leak}'`);
if (/\\b(?:L[123]|M[1-7])\\b|\\[data-term\\]|\\bV\\d{2}:/.test(bodyTxt)) errs.push(`[TAXONOMY_LEAK] ${view}`);
if (document.querySelectorAll('.qe-card-head .va-pill, .qe-label-pill').length) errs.push(`[LEGACY_PILL] ${view}`);
if (view === 'v01-icu-bedside-terminal') {
  const s = document.querySelector('svg.qe-waveform-svg');
  if (s) {
    if ([...s.querySelectorAll('text[text-anchor="end"]')].some(t => /^-(120|100|50)$/.test(t.textContent.trim()))) errs.push('[UNIPOLAR_SCOPE]');
    const ps = [...s.querySelectorAll('path')];
    if (ps.length >= 2 && ps[1].getBoundingClientRect().height < 8.0) errs.push('[PLETH_FLATLINE]');
    if (w >= 1400 && w <= 1950 && (s.getBoundingClientRect().top > 390 || s.getBoundingClientRect().bottom > 860)) errs.push('[V01_DESKTOP_FOLD]');
  }
  if (w <= 420) {
    const gr = document.querySelector('.qe-scalar-grid');
    if (gr && gr.getBoundingClientRect().height > 148) errs.push('[MOBILE_GRID] >148px');
    for (const c of document.querySelectorAll('.v9-view-v01 .qe-scalar-card')) if (c.scrollHeight > c.clientHeight + 1) errs.push('[MOBILE_CARD_CLIP]');
    if (!s || s.getBoundingClientRect().top > 340) errs.push('[MOBILE_TOP_FOLD]');
    for (const b of document.querySelectorAll('.v01-tactile-btn')) if (b.getBoundingClientRect().height < 44) errs.push('[TOUCH_44]');
  }
}
if (view === 'v02-trial-regulatory-brief' && w >= 780 && w <= 1080 && med !== 'm1') {
  const pr = document.querySelector('.v02-prose-col')?.getBoundingClientRect(), fr = document.getElementById('v02-forest')?.getBoundingClientRect();
  if (!pr || !fr || pr.right > 414 || fr.left < 426) errs.push('[FOLD_HINGE]');
}
if (view === 'v03-patient-recovery-companion') {
  for (const bad of ['raw_adc','ADC','k=2','PEEP','CAL-','T05:30:00Z','Mean MAP','Oxygen / %','HOME-OXYGEN','Nominal','CAUTION'])
    if (bodyTxt.includes(bad)) errs.push(`[V03_JARGON] '${bad}'`);
  const svgs = [...document.querySelectorAll('.v03-pedagogy-panel .qe-plot-wrap svg')];
  if (svgs.length !== 2 || !svgs[0].textContent.includes('%') || svgs[0].textContent.includes('mmHg') || !svgs[1].textContent.includes('mmHg'))
    errs.push('[V03_DIM_HOMOGENEITY]');
}
for (const u of document.querySelectorAll('.qe-unit')) {
  if (getComputedStyle(u).textTransform !== 'none' || /\\b(MMOL|MMHG|CMH2O|KHZ|PS|DBM)\\b/.test(u.innerText || '')) errs.push('[SI_CASE]');
}
for (const grid of document.querySelectorAll('.qe-scalar-grid')) {
  const rows = new Map();
  for (const c of grid.querySelectorAll(':scope > .qe-scalar-card')) {
    if (getComputedStyle(c).display === 'none') continue;
    const k = Math.round(c.getBoundingClientRect().top / 8);
    (rows.get(k) || rows.set(k, []).get(k)).push(c);
  }
  for (const cards of rows.values()) if (cards.length >= 2) {
    for (const sel of ['.qe-scalar-title', '.qe-scalar-val-row', 'svg.qe-gauge-svg']) {
      const tops = cards.map(c => c.querySelector(sel)).filter(e => e && getComputedStyle(e).display !== 'none').map(e => e.getBoundingClientRect().top);
      if (tops.length >= 2 && Math.max(...tops) - Math.min(...tops) > 1.0) errs.push(`[BASELINE_LOCK] ${view} ${sel}`);
    }
  }
}
for (const p of document.querySelectorAll('.va-pill')) {
  const cs = getComputedStyle(p), rad = parseFloat(cs.borderTopLeftRadius || '0'), v = p.dataset.variant, st = p.dataset.state, txt = (p.textContent || '').trim();
  if ((v === 'status' || v === 'tag') && rad >= 12) errs.push(`[ROUND_CLICK] ${txt}`);
  if (v === 'chip' && (!p.matches('button,a[href],input,[role="button"]') || rad < 99)) errs.push(`[ROUND_CLICK] chip ${txt}`);
  if (v === 'status' && st === 'nominal' && (parseFloat(cs.borderTopWidth) > 0 || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent')))
    errs.push(`[QUIET_NOMINAL] ${txt}`);
}
if (med === 'm1' && w >= 1200) {
  for (const pc of document.querySelectorAll('.v9-prose-card, .v02-prose-col')) {
    const pcs = getComputedStyle(pc);
    if (pcs.borderTopWidth !== '0px' || pcs.columnCount !== '2') errs.push(`[M1_UNBOXED] ${view}`);
  }
}
if (view === 'v08-plant-floor-wall-kiosk' && w >= 1900) {
  for (const kv of document.querySelectorAll('.v08-kpi-val')) if (parseFloat(getComputedStyle(kv).fontSize) < 32) errs.push('[M5_KPI]');
  if (document.documentElement.scrollHeight > window.innerHeight + 16) errs.push('[M5_SINGLE_FRAME]');
}
if (view === 'v12-stem-interactive-lab' && (!bodyTxt.includes('τ') || !bodyTxt.includes('V0'))) errs.push('[V12_MATH]');
if (view === 'v16-transparent-window-overlay' && w >= 1400) {
  const tb = document.getElementById('va-shell-topbar');
  if (tb && getComputedStyle(tb).display !== 'none') errs.push('[V16_FULLBLEED]');
}
for (const pw of document.querySelectorAll('.qe-plot-wrap[data-echarts-active="true"]')) {
  const ls = pw.querySelector('.qe-legend-series');
  if (ls && getComputedStyle(ls).display !== 'none') errs.push('[SINGLE_LEGEND]');
}
return errs;
"""


def _check_studio_bar_and_viewports(driver: Any, base_url: str, errs: list[str]) -> None:
    check_bar_js = """
        const b = document.getElementById('va-studio-bar');
        if (!b) return 'missing #va-studio-bar';
        b.classList.remove('is-tucked');
        if (b.getBoundingClientRect().height > 48.5) return 'height>48.5';
        if (b.scrollWidth > b.clientWidth + 1 || document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) return 'overflow';
        if (document.getElementById('va-domain-select')) return 'obsolete #va-domain-select present';
        const t = document.getElementById('va-studio-mode-tablist'), v = document.getElementById('va-view-select');
        if (!v || v.querySelectorAll('optgroup').length < 6) return 'missing grouped #va-view-select';
        if (v.getBoundingClientRect().width > 0 && t.getBoundingClientRect().left >= v.getBoundingClientRect().left) return 'tablist order';
        return '';
    """
    for vp_w, vp_h in ((390, 844), (840, 1050), (1440, 900), (1920, 1080), (3840, 2160)):
        set_viewport(driver, vp_w, vp_h, 1)
        driver.get(base_url)
        time.sleep(0.2)
        bar_err = driver.execute_script(check_bar_js)
        if bar_err:
            errs.append(f"[STUDIO_BAR_OVERVIEW_{vp_w}] {bar_err}")

        driver.execute_script(
            "const api=window.QuietStudioPortalV9;if(api){api.state.studioView='examples';api.state.vp='fill';api.state.presetLocked=true;api.applyState(false);}"
        )
        time.sleep(0.15)
        bar_err_ex = driver.execute_script(check_bar_js)
        if bar_err_ex:
            errs.append(f"[STUDIO_BAR_{vp_w}] {bar_err_ex}")

        exp_fs, tol = ROOT_FONT_SCALE_TARGETS[vp_w]
        for _wid, views in ALL_WORLDS_VIEWS:
            for vid in views:
                select_view(driver, vid)
                driver.switch_to.frame("va-stage-portal")
                try:
                    fs = float(driver.execute_script("return parseFloat(getComputedStyle(document.documentElement).fontSize);"))
                    if abs(fs - exp_fs) > tol:
                        errs.append(f"[ROOT_SCALE_{vp_w}_{vid}] {fs:.2f} != {exp_fs}+-{tol}")
                    errs.extend(f"[{vid}_{vp_w}] {e}" for e in driver.execute_script(STAGE_AUDIT_JS))
                finally:
                    driver.switch_to.default_content()


def _check_themes_print_why_and_interactions(driver: Any, base_url: str, root_url: str, errs: list[str]) -> None:
    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?mode=examples&theme=white")
    time.sleep(0.2)

    bgs: set[str] = set()
    for th in ("white", "paper", "dark-paper", "dark"):
        driver.execute_script("window.QuietStudioPortalV9.state.theme=arguments[0];window.QuietStudioPortalV9.applyState(false);", th)
        time.sleep(0.1)
        driver.switch_to.frame("va-stage-portal")
        bgs.add(str(driver.execute_script("return getComputedStyle(document.body).backgroundColor;")))
        driver.switch_to.default_content()
    if len(bgs) < 3:
        errs.append(f"[THEMES] Expected >=3 distinct theme backgrounds, got {bgs}")

    # Why? Design Rationale clean across all 21 views
    leak_re = r"\b(?:L[123]|M[1-7]|N[0-4]|T[123])\b|\[data-term\]|\bBooktabs\b|QUIET-BRIDGE|Murder-Board|\.json|_row_status"
    for _wid, views in ALL_WORLDS_VIEWS:
        for vid in views:
            select_view(driver, vid)
            bad_why = driver.execute_script(
                f"document.getElementById('va-bridge-btn').click();const t=document.getElementById('va-bridge-dialog').innerText||'';"
                f"const m=t.match(/{leak_re}/);document.getElementById('va-bridge-dialog').close();return m?m[0]:(t.trim().length<30?'EMPTY':'');"
            )
            if bad_why:
                errs.append(f"[WHY_LEAK_{vid}] {bad_why}")

    # M1 print sheet & dark->print tokens
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v02-trial-regulatory-brief&theme=dark")
    time.sleep(0.25)
    driver.switch_to.frame("va-stage-portal")
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
    time.sleep(0.1)
    dark_print = driver.execute_script("return getComputedStyle(document.documentElement).getPropertyValue('--tint-emerald-fg').trim().toUpperCase();")
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
    driver.switch_to.default_content()
    if dark_print != "#065F46":
        errs.append(f"[DARK_PRINT_TOKENS] got {dark_print}")

    for wid, vid in (("02-cloud-cyber-and-ai-ops", "v05-zero-trust-ato-spec"), ("05-physical-systems-auto-and-aero", "v13-propulsion-archival-monograph")):
        driver.get(f"{base_url}?world={wid}&view={vid}&medium=m1&theme=white")
        time.sleep(0.2)
        driver.switch_to.frame("va-stage-portal")
        errs.extend(f"[M1_{vid}] {e}" for e in driver.execute_script(STAGE_AUDIT_JS))
        driver.switch_to.default_content()

    # Interactive domain workflows
    checks = [
        ("01-clinical-icu-and-trials", "v01-icu-bedside-terminal", "document.getElementById('v01-zero-btn').click();document.getElementById('v01-arm-btn').click();document.getElementById('v01-exec-btn').click();return document.getElementById('v01-audit-list').textContent;", "EXECUTED"),
        ("01-clinical-icu-and-trials", "v02-trial-regulatory-brief", "document.querySelector('button[data-subgroup=\"sofa\"]').click();return document.getElementById('v02-filter-readout').textContent;", "0.68"),
        ("02-cloud-cyber-and-ai-ops", "v04-sre-incident-workbench", "document.getElementById('v04-otel-btn').click();document.getElementById('v04-arm-btn').click();document.getElementById('v04-exec-btn').click();return document.getElementById('v04-gate-pill').textContent;", "CANARY ISOLATED"),
        ("03-industrial-grid-and-manufacturing", "v07-grid-scada-poi-console", "document.getElementById('v07-loto-btn').click();document.getElementById('v07-arm-btn').click();document.getElementById('v07-exec-btn').click();return document.getElementById('v07-gate-pill').textContent;", "ISLAND ARMED"),
        ("04-civic-finance-and-stem-learning", "v11-treasury-stress-test-solver", "document.querySelector('#v11-shock-chips button:last-child').click();return document.getElementById('v11-q8-val').textContent;", "21.4%"),
        ("04-civic-finance-and-stem-learning", "v12-stem-interactive-lab", "const b=document.querySelector('#v12-lab button[data-term=\"tx\"]');b.click();return document.querySelector('#v12-lab article[data-term=\"tx\"]').className;", "is-term-active"),
        ("05-physical-systems-auto-and-aero", "v14-fieldbus-and-scope-debugger", "document.getElementById('v14-term-btn').click();document.getElementById('v14-arm-btn').click();document.getElementById('v14-exec-btn').click();return document.getElementById('v14-gate-pill').textContent;", "SOF_ARB_ERR W1C OK"),
        ("02-cloud-cyber-and-ai-ops", "v19-product-roadmap-and-triage", "document.querySelectorAll('#v19-triage .v9-triage-row')[2].click();return document.getElementById('v19-triage-detail').textContent;", "+3.0 d"),
        ("04-civic-finance-and-stem-learning", "v20-student-capstone-lab-report", "document.querySelector('#v20-rubric-chips [data-v20-focus=\"error\"]').click();return document.getElementById('v20-focus-note').textContent;", "Error Bounds"),
        ("05-physical-systems-auto-and-aero", "v21-field-anomaly-escalation-tsn", "document.getElementById('v21-handoff-arm').click();document.getElementById('v21-handoff-send').click();return document.getElementById('v21-handoff-status').textContent;", "HANDOFF SENT"),
        ("04-civic-finance-and-stem-learning", "v22-reading-and-mobility-brief", "const s=document.querySelector('[data-v22-scope-select]');s.value='md';s.dispatchEvent(new Event('change',{bubbles:true}));return document.querySelector('[data-v22-lead]').textContent;", "35% of Maryland"),
    ]
    for wid, vid, js, expect in checks:
        driver.get(f"{base_url}?world={wid}&view={vid}&theme=white")
        time.sleep(0.24)
        driver.switch_to.frame("va-stage-portal")
        res = str(driver.execute_script(js))
        driver.switch_to.default_content()
        if expect not in res:
            errs.append(f"[INTERACT_{vid}] expected {expect!r}, got {res!r}")

    # Deep links, Settings theme swatches & Starters
    driver.get(f"{base_url}?view=v10-civic-capital-budget-deck")
    time.sleep(0.25)
    if not driver.execute_script("const s=window.QuietStudioPortalV9.state;return s.world==='04-civic-finance-and-stem-learning'&&s.view==='v10-civic-capital-budget-deck';"):
        errs.append("[DEEPLINK_V10] failed domain resolution")

    for rel, cnt in (("customizations/personal-starter/showcase.html", 26), ("customizations/brand-starter/showcase.html", 22)):
        driver.get(f"{root_url}/{rel}?theme=dark")
        time.sleep(0.25)
        n = int(driver.execute_script("return JSON.parse(document.getElementById('va-v9-manifest').textContent).worlds.reduce((a,w)=>a+w.views.length,0);"))
        if n != cnt:
            errs.append(f"[STARTER_{rel}] expected {cnt} views, got {n}")

    severe = [l for l in driver.get_log("browser") if l.get("level") == "SEVERE" and "favicon.ico" not in l.get("message", "")]
    if severe:
        errs.append(f"[CONSOLE_SEVERE] {severe[0].get('message')}")


def _check_docs_demo_route(driver: Any, root_url: str, errs: list[str]) -> None:
    """Verify /docs/demo/index.html at 390/900/1440px for unified topbar, 900px route pill, 960px search, no subbar, and theme persistence."""
    demo_js = (
        "const vw = arguments[0], b = document.getElementById('va-studio-bar');"
        "if (!b) return 'missing #va-studio-bar';"
        "b.classList.remove('is-tucked');"
        "if (b.getBoundingClientRect().height > 48.5) return 'bar height>48.5';"
        "if (document.getElementById('oaw-docs-subbar')) return 'unexpected #oaw-docs-subbar on demo';"
        "const s = document.querySelector('.va-demo-site-strip');"
        "if (!s) return 'missing .va-demo-site-strip';"
        "if (getComputedStyle(s).position !== 'static') return 'strip position not static';"
        "const sr = s.getBoundingClientRect();"
        "if (sr.height < 44 || sr.height > 48) return 'strip height=' + sr.height;"
        "const rb = document.getElementById('oaw-route-btn'), rm = document.getElementById('oaw-route-menu'), nv = s.querySelector('.oaw-topbar-left .oaw-nav-links');"
        "if (!rb || !rm || !nv) return 'missing route switcher DOM';"
        "if (vw < 900) {"
        "  if (getComputedStyle(rb).display === 'none') return '#oaw-route-btn hidden <900px';"
        "  rb.click();"
        "  const ro = (typeof rm.matches === 'function' && rm.matches(':popover-open')) || rm.getAttribute('data-open') === 'true';"
        "  const ls = [...rm.querySelectorAll('.oaw-nav-link')].filter(a => a.getBoundingClientRect().width > 0).map(a => a.textContent.trim());"
        "  if (!ro || rb.getAttribute('aria-expanded') !== 'true' || !['Overview', 'Demo', 'Docs'].every(k => ls.some(t => t.includes(k)))) return 'route menu missing Overview/Demo/Docs';"
        "  if (typeof rm.hidePopover === 'function' && rm.matches(':popover-open')) rm.hidePopover(); else rb.click();"
        "  if (rb.getAttribute('aria-expanded') !== 'false') return 'route menu failed to close';"
        "} else {"
        "  if (getComputedStyle(rb).display !== 'none') return '#oaw-route-btn visible >=900px';"
        "  if (getComputedStyle(nv).display === 'none' || [...nv.querySelectorAll('.oaw-nav-link')].filter(a => a.getBoundingClientRect().width > 0).length < 3) return 'inline .oaw-nav-links not visible';"
        "}"
        "const sb = document.getElementById('oaw-search-btn'), st = sb?.querySelector('.oaw-search-text');"
        "if (!sb || !st) return 'missing #oaw-search-btn';"
        "if (vw < 960 && getComputedStyle(st).display !== 'none') return 'search text visible <960px';"
        "if (vw >= 960 && getComputedStyle(st).display === 'none') return 'search text hidden >=960px';"
        "const ov = document.getElementById('va-tab-overview');"
        "if (ov && getComputedStyle(ov).display !== 'none' && !ov.hidden) return '#va-tab-overview not hidden';"
        "if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1 || b.scrollWidth > b.clientWidth + 1) return 'overflow';"
        "return '';"
    )
    for vp_w, vp_h in ((390, 844), (900, 900), (1440, 900)):
        set_viewport(driver, vp_w, vp_h, 1)
        driver.get(f"{root_url}/docs/demo/index.html")
        time.sleep(0.25)
        demo_err = driver.execute_script(demo_js, vp_w)
        if demo_err:
            errs.append(f"[DOCS_DEMO_ROUTE_{vp_w}] {demo_err}")

    th_err = driver.execute_script(
        "const opt = document.querySelector('.oaw-theme-opt[data-theme-opt=\"paper\"]');"
        "if (!opt) return 'missing paper theme option';"
        "opt.click();"
        "const c = document.querySelector('.oaw-demo-chrome'), d = document.getElementById('va-stage-portal')?.contentDocument;"
        "const ok = document.documentElement.dataset.theme === 'paper' && c?.dataset.theme === 'paper'"
        " && d?.documentElement?.dataset?.theme === 'paper'"
        " && localStorage.getItem('oaw_theme_v99') === 'paper' && localStorage.getItem('quiet-ui-site-theme') === 'paper';"
        "localStorage.removeItem('oaw_theme_v99'); localStorage.removeItem('quiet-ui-site-theme');"
        "return ok ? '' : 'demo dual-key theme sync failed';"
    )
    if th_err:
        errs.append(f"[DOCS_DEMO_THEME] {th_err}")


def run_studio_and_viewport_gates(driver: Any, base_url: str, root_url: str) -> list[str]:
    """Run all Studio bar, 26-view x 5-viewport continuum, theme, print, interaction, starter & /docs/demo CDP checks."""
    errs: list[str] = []
    _check_studio_bar_and_viewports(driver, base_url, errs)
    _check_themes_print_why_and_interactions(driver, base_url, root_url, errs)
    _check_docs_demo_route(driver, root_url, errs)
    set_viewport(driver, 1440, 900, 1)
    return errs

