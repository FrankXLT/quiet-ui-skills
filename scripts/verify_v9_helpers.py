#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 4.1 — Stage CDP Audit Script & Gallery Helpers (<= 250L)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

STAGE_AUDIT_JS = """
const errs = [];
const view = document.documentElement.dataset.view || '';
const medium = document.documentElement.dataset.medium || '';
const w = window.innerWidth;
if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) {
  errs.push(`[OVERFLOW] ${view} @${w}: scrollWidth=${document.documentElement.scrollWidth} > clientWidth=${document.documentElement.clientWidth}`);
}
if (w >= 700) {
  const dock = document.getElementById('va-shell-bottomdock');
  if (dock && getComputedStyle(dock).display !== 'none') errs.push(`[N4_BAN] Bottom dock visible at width=${w}`);
  if (document.documentElement.dataset.effectiveNav === 'n4') errs.push(`[N4_BAN] effectiveNav=n4 at width=${w}`);
}
if (w >= 1280) {
  for (const wrap of document.querySelectorAll('.va-table-wrap')) {
    const tbl = wrap.querySelector('table');
    if (tbl && tbl.scrollWidth > wrap.clientWidth + 2) errs.push(`[TABLE_CLIP] ${view}: table ${tbl.scrollWidth} > wrap ${wrap.clientWidth}`);
  }
}
if (w >= 3800) {
  const rfs = parseFloat(getComputedStyle(document.documentElement).fontSize);
  if (rfs < 21.0) errs.push(`[4K_SCALE] root fontSize=${rfs}px < 21.0px at ${w}px`);
}
if (w === 390 || w === 840 || w === 1440) {
  for (const el of document.querySelectorAll('.va-figure-scroll, .qe-scalar-card')) {
    if (getComputedStyle(el).display === 'none' || el.clientWidth === 0) continue;
    if (el.scrollWidth > el.clientWidth + 1) errs.push(`[INNER_SCROLL] ${view} @${w}: ${el.className} scroll=${el.scrollWidth} > client=${el.clientWidth}`);
  }
  for (const svg of document.querySelectorAll('svg')) {
    const sr = svg.getBoundingClientRect();
    if (sr.width < 20 || sr.height < 10) continue;
    for (const t of svg.querySelectorAll('text')) {
      if (!t.textContent || !t.textContent.trim() || getComputedStyle(t).display === 'none') continue;
      const tr = t.getBoundingClientRect();
      if (tr.width <= 0 || tr.height <= 0) continue;
      if (tr.left < sr.left - 1.5 || tr.right > sr.right + 1.5 || tr.top < sr.top - 1.5 || tr.bottom > sr.bottom + 1.5) {
        errs.push(`[SVG_CLIP] ${view} @${w}: '${t.textContent.trim().slice(0, 20)}' (${tr.left.toFixed(1)}..${tr.right.toFixed(1)}) outside SVG (${sr.left.toFixed(1)}..${sr.right.toFixed(1)})`);
      }
    }
  }
}
const visBody = document.body.innerText || '';
for (const leak of ['Quiet Cockpit', 'Pedagogical Flow', 'Decision Contrast', 'Walk-Up Bedside', 'PlainLanguage.gov', 'FDA IEC 62366']) {
  if (visBody.includes(leak)) errs.push(`[FRAMEWORK_LEAK] ${view} leaked '${leak}'`);
}
for (const badBadge of document.querySelectorAll('.qe-card-head .va-pill')) {
  errs.push(`[EMBEDDED_BADGE] ${view} has internal card badge '${badBadge.textContent}'`);
}
if (view === 'v01-icu-bedside-terminal') {
  const scopeSvg = document.querySelector('svg.qe-waveform-svg');
  if (scopeSvg) {
    const negTicks = [...scopeSvg.querySelectorAll('text[text-anchor="end"]')].map(t => t.textContent.trim()).filter(s => /^-(120|100|50)$/.test(s));
    if (negTicks.length) errs.push(`[UNIPOLAR_SCOPE] Negative physiological Y-ticks found: ${negTicks.join(',')}`);
    const paths = [...scopeSvg.querySelectorAll('path')];
    if (paths.length >= 2 && paths[1].getBoundingClientRect().height < 8.0) {
      errs.push(`[PLETH_FLATLINE] CH2 path height=${paths[1].getBoundingClientRect().height.toFixed(1)}px < 8px`);
    }
  }
  if (w >= 1400) {
    if (w <= 1950) {
      const sr = scopeSvg ? scopeSvg.getBoundingClientRect() : null;
      if (!sr || sr.top > 390 || sr.bottom > 860) {
        errs.push(`[V01_DESKTOP_FOLD] Scope rect top=${sr ? sr.top.toFixed(1) : 'none'} bottom=${sr ? sr.bottom.toFixed(1) : 'none'} outside [<=390, <=860]`);
      }
    }
    const visText = (el) => {
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') return '';
      const r = el.getBoundingClientRect();
      return (r.width > 0 && r.height > 0) ? el.textContent.trim() : '';
    };
    const topTexts = new Set([...document.querySelectorAll('.va-shell-topbar a')].map(visText).filter(Boolean));
    for (const ra of document.querySelectorAll('.va-shell-rail a')) {
      const rt = visText(ra);
      if (rt && topTexts.has(rt)) errs.push(`[N3_DUP_NAV] Topbar and rail duplicate link '${rt}'`);
    }
  }
  if (w <= 420) {
    const grid = document.querySelector('.qe-scalar-grid');
    if (grid && grid.getBoundingClientRect().height > 118) errs.push(`[MOBILE_GRID] 2x2 vitals height=${grid.getBoundingClientRect().height.toFixed(1)}px > 118px`);
    if (!scopeSvg || scopeSvg.getBoundingClientRect().top > 340) errs.push(`[MOBILE_TOP_FOLD] Scope SVG top=${scopeSvg ? scopeSvg.getBoundingClientRect().top.toFixed(1) : 'missing'} > 340px`);
    const ch1 = scopeSvg ? scopeSvg.querySelector('rect[data-role="channel"]') : null;
    if (!ch1 || ch1.getBoundingClientRect().top > 320) errs.push(`[MOBILE_CH1] CH1 top=${ch1 ? ch1.getBoundingClientRect().top.toFixed(1) : 'missing'} > 320px`);
    for (const btn of document.querySelectorAll('.v01-tactile-btn')) {
      if (btn.getBoundingClientRect().height < 44) errs.push(`[TOUCH_44] ${btn.id} height < 44px`);
    }
  }
}
if (view === 'v02-trial-regulatory-brief' && w >= 700 && w < 1100 && medium !== 'm1') {
  const gate = document.getElementById('v02-disposition');
  if (!gate || gate.getBoundingClientRect().top > 200) errs.push(`[FOLD_TOP] v02 gate top=${gate ? gate.getBoundingClientRect().top.toFixed(1) : 'missing'} > 200px`);
  if (w >= 780 && w <= 1080) {
    const prose = document.querySelector('.v02-prose-col');
    const forest = document.getElementById('v02-forest');
    if (!prose || !forest) errs.push('[FOLD_SPREAD] Missing .v02-prose-col or #v02-forest');
    else {
      const pr = prose.getBoundingClientRect(), fr = forest.getBoundingClientRect();
      if (pr.right > 414 || fr.left < 426) errs.push(`[FOLD_HINGE] 420px hinge crossed: prose.right=${pr.right.toFixed(1)}, forest.left=${fr.left.toFixed(1)}`);
    }
  }
}
if (view === 'v03-patient-recovery-companion') {
  if (w >= 700 && w < 1100) {
    const links = document.querySelector('#va-shell-topbar .va-shell-topbar-links');
    if (!links || getComputedStyle(links).display === 'none') errs.push(`[FOLD_N2_NAV] Topbar links hidden at width=${w}`);
  }
  for (const bad of ['raw_adc', 'ADC', 'k=2', 'PEEP', 'CAL-', 'T05:30:00Z', 'Mean MAP', 'Oxygen / %', 'Blood Pressure / mmHg', 'HOME-OXYGEN', 'HOME-BP-CHECK', 'Nominal', 'CAUTION', 'Discrete Sample']) {
    if (visBody.includes(bad)) errs.push(`[L1_JARGON] v03 exposed forbidden term '${bad}'`);
  }
  const plotSvgs = [...document.querySelectorAll('.v03-pedagogy-panel .qe-plot-wrap svg')];
  if (plotSvgs.length !== 2) errs.push(`[DIM_HOMOGENEITY] Expected 2 separate v03 trend SVGs, found ${plotSvgs.length}`);
  else {
    const t0 = plotSvgs[0].textContent || '', t1 = plotSvgs[1].textContent || '';
    if (!(t0.includes('%') && !t0.includes('mmHg') && t1.includes('mmHg') && !t1.includes('%'))) {
      errs.push('[DIM_HOMOGENEITY] v03 plots share mixed units instead of pure % and mmHg axes');
    }
  }
}
for (const u of document.querySelectorAll('.qe-unit')) {
  if (getComputedStyle(u).textTransform !== 'none') errs.push(`[SI_CASE] .qe-unit textTransform=${getComputedStyle(u).textTransform}`);
  if (/\\b(MMOL|MMHG|CMH2O|KHZ|PS|DBM)\\b/.test(u.innerText || '')) errs.push(`[SI_CASE] Uppercase unit leak '${u.innerText}'`);
}
for (const el of document.querySelectorAll('.v9-stage-inner *')) {
  if (el.closest('svg')) continue;
  if (getComputedStyle(el).textTransform === 'uppercase') {
    const txt = el.innerText || '';
    if (/\\b(MMOL|MMHG|CMH2O|KHZ|DBM|PS)\\b/.test(txt)) errs.push(`[UPPERCASE_SI_LEAK] Corrupted SI unit in '${txt.slice(0, 48)}'`);
  }
}
for (const grid of document.querySelectorAll('.qe-scalar-grid')) {
  const rows = new Map();
  for (const card of grid.querySelectorAll(':scope > .qe-scalar-card')) {
    if (getComputedStyle(card).display === 'none') continue;
    const key = Math.round(card.getBoundingClientRect().top / 8);
    if (!rows.has(key)) rows.set(key, []);
    rows.get(key).push(card);
  }
  for (const cards of rows.values()) {
    if (cards.length < 2) continue;
    for (const sel of ['.qe-scalar-title', '.qe-scalar-val-row', 'svg.qe-gauge-svg']) {
      const tops = cards.map(c => c.querySelector(sel)).filter(el => el && getComputedStyle(el).display !== 'none').map(el => el.getBoundingClientRect().top);
      if (tops.length >= 2 && Math.max(...tops) - Math.min(...tops) > 1.0) errs.push(`[BASELINE_LOCK] ${view} ${sel} drift ${(Math.max(...tops) - Math.min(...tops)).toFixed(2)}px > 1.0px`);
    }
  }
}
if (document.querySelectorAll('.qe-label-pill').length > 0) errs.push('[SVG_KNOCKOUT] Legacy .qe-label-pill detected');
for (const r of document.querySelectorAll('svg .qe-svg-knockout rect')) {
  const cs = getComputedStyle(r);
  if (cs.stroke && cs.stroke !== 'none' && parseFloat(cs.strokeWidth || '0') > 0) errs.push('[SVG_KNOCKOUT] Stroked knockout rect found');
}
for (const p of document.querySelectorAll('.va-pill')) {
  const cs = getComputedStyle(p);
  const rad = parseFloat(cs.borderTopLeftRadius || '0');
  const v = p.dataset.variant, st = p.dataset.state, txt = p.textContent || '';
  if (/[\\x5b\\x5d]|\\bMargin\\b/.test(txt)) errs.push(`[ATOMIC_PILL] Non-atomic pill '${txt}'`);
  if ((v === 'status' || v === 'tag') && rad >= 12) errs.push(`[ROUND_CLICK] Non-interactive pill '${txt}' has radius ${rad}px`);
  if (v === 'chip' && (!p.matches('button, a[href], input, [role="button"]') || rad < 99)) errs.push(`[ROUND_CLICK] Chip '${txt}' invalid`);
  if (v === 'status' && st === 'nominal' && (parseFloat(cs.borderTopWidth) > 0 || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent')))
    errs.push(`[QUIET_NOMINAL] Nominal pill '${txt}' has bg/border`);
}
for (const el of document.querySelectorAll('.v9-stage-inner :is(span, div, p)')) {
  if (el.closest('svg') || el.classList.contains('va-pill')) continue;
  const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
  if (r.width > 14 && r.height > 14 && parseFloat(cs.borderTopLeftRadius || '0') >= 99 && !el.matches('[role="button"], button, a[href]'))
    errs.push(`[ROUND_CLICK] Unmarked rounded capsule '${(el.textContent || '').trim().slice(0, 20)}'`);
}
for (const wsvg of document.querySelectorAll('svg.qe-waveform-svg')) {
  const spans = [...wsvg.querySelectorAll('rect[data-role="dropout-zone"]')].map(r => {
    const x = parseFloat(r.getAttribute('x') || '0');
    return [x, x + parseFloat(r.getAttribute('width') || '0')];
  }).sort((a, b) => a[0] - b[0]);
  const merged = [];
  for (const [a, b] of spans) {
    if (!merged.length || a > merged[merged.length - 1][1] + 1.0) merged.push([a, b]);
    else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b);
  }
  const labels = [...wsvg.querySelectorAll('text')].filter(t => (t.textContent || '').includes('DROPOUT')).length;
  if (merged.length > 0 && labels !== merged.length) errs.push(`[SINGLE_DROPOUT] Expected ${merged.length} DROPOUT label(s), got ${labels}`);
}
return errs;
"""


def set_viewport(driver: Any, width: int, height: int, scale: int = 1) -> None:
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": scale, "mobile": width < 600},
    )


def capture_gate41_gallery(driver: Any, base_url: str, shots_dir: Path) -> None:
    shots_dir.mkdir(parents=True, exist_ok=True)
    shots = [
        ("01_v01_icu_desktop_white.png", 1440, 900, "view=v01-icu-bedside-terminal&theme=white"),
        ("02_v01_icu_desktop_oled.png", 1440, 900, "view=v01-icu-bedside-terminal&theme=dark"),
        ("03_v01_icu_mobile_390x844.png", 390, 844, "view=v01-icu-bedside-terminal&theme=white"),
        ("04_v02_trial_desktop_paper.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=paper"),
        ("05_v02_trial_foldable_840x1050.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=white&vp=840x1050"),
        ("06_v02_trial_m1_print_sheet.png", 1440, 900, "view=v02-trial-regulatory-brief&theme=dark&medium=m1"),
        ("07_v03_patient_desktop_white.png", 1440, 900, "view=v03-patient-recovery-companion&theme=white"),
        ("08_v03_patient_mobile_390x844.png", 390, 844, "view=v03-patient-recovery-companion&theme=white"),
    ]
    for fname, w, h, qs in shots:
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
