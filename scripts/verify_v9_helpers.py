#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5 — Stage CDP Audit Script & Gallery Helpers (<= 400L)."""

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
if ([390, 840, 1440, 1920, 3840].includes(w)) {
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
for (const leak of ['Quiet Cockpit', 'Pedagogical Flow', 'Decision Contrast', 'Walk-Up Bedside', 'PlainLanguage.gov', 'FDA IEC 62366', 'T1 GATE', 'STROKE-ONLY PHOSPHOR', 'WCAG AAA']) {
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
for (const s of document.querySelectorAll('svg.qe-waveform-svg, svg.qe-plot-svg, svg.qe-gauge-svg')) {
  for (const t of s.querySelectorAll('text')) {
    const raw = (t.textContent || '').trim();
    if (/\\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\\b/.test(raw)) errs.push(`[SVG_SNAKE_CASE] Unformatted identifier '${raw}'`);
  }
}
if (medium === 'm1' && w >= 1200) {
  for (const pc of document.querySelectorAll('.v9-prose-card, .v02-prose-col')) {
    const pcs = getComputedStyle(pc);
    if (pcs.borderTopWidth !== '0px' || pcs.columnCount !== '2') {
      errs.push(`[M1_UNBOXED] ${view} expected unboxed 2-col prose, got border=${pcs.borderTopWidth} cols=${pcs.columnCount}`);
    }
  }
}
if (view === 'v08-plant-floor-wall-kiosk' && w >= 1900) {
  for (const kv of document.querySelectorAll('.v08-kpi-val')) {
    const fs = parseFloat(getComputedStyle(kv).fontSize);
    if (fs < 32.0) errs.push(`[M5_KPI_SIZE] v08 KPI font=${fs.toFixed(1)}px < 32px`);
  }
  for (const kl of document.querySelectorAll('.v08-kpi-label, .v08-wall-kicker')) {
    const fs = parseFloat(getComputedStyle(kl).fontSize);
    if (fs < 18.0) errs.push(`[M5_LABEL_SIZE] v08 label font=${fs.toFixed(1)}px < 18px`);
  }
  for (const p of document.querySelectorAll('.v08-wall-status .va-pill')) {
    const bh = p.getBoundingClientRect().height, pfs = parseFloat(getComputedStyle(p).fontSize);
    if (p.scrollHeight > p.clientHeight + 2 || bh < pfs * 1.15) errs.push(`[M5_PILL_CLIP] box=${bh.toFixed(1)}px font=${pfs}`);
  }
  if (document.documentElement.scrollHeight > window.innerHeight + 16) {
    errs.push(`[M5_SINGLE_FRAME] v08 scrollHeight=${document.documentElement.scrollHeight} > ${window.innerHeight}`);
  }
}
if (view === 'v15-collimated-flight-hud' && w >= 1400) {
  const h = window.innerHeight, kx0 = w * 0.175, kx1 = w * 0.825, ky0 = h * 0.15, ky1 = h * 0.85;
  let occ = 0;
  for (const el of document.querySelectorAll('.v15-hud-stage *')) {
    if (el.closest('svg')) continue;
    const bg = getComputedStyle(el).backgroundColor;
    if (!bg || bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') continue;
    const r = el.getBoundingClientRect();
    const ix = Math.max(0, Math.min(r.right, kx1) - Math.max(r.left, kx0));
    const iy = Math.max(0, Math.min(r.bottom, ky1) - Math.max(r.top, ky0));
    occ += ix * iy;
  }
  const clearPct = 100 * (1 - occ / ((kx1 - kx0) * (ky1 - ky0)));
  if (clearPct < 65.0) errs.push(`[M6_KEEPOUT] Central boresight clear=${clearPct.toFixed(1)}% < 65%`);
}
if (view === 'v16-transparent-window-overlay') {
  const band = document.getElementById('v16-top-scrim');
  if (band) {
    const parseRgba = (s) => (s.match(/[\\d.]+/g) || [0, 0, 0, 1]).map(Number);
    const over = (fg, bg) => {
      const a = fg.length >= 4 ? fg[3] : 1;
      return [fg[0] * a + bg[0] * (1 - a), fg[1] * a + bg[1] * (1 - a), fg[2] * a + bg[2] * (1 - a)];
    };
    const lum = ([r, g, b]) => {
      const f = (v) => { const x = v / 255; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
      return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
    };
    const bandBg = over(parseRgba(getComputedStyle(band).backgroundColor), [255, 255, 255]);
    for (const el of band.querySelectorAll('.v16-metric-val, .v16-metric-lbl, .v16-scrim-pill')) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const elBg = over(parseRgba(cs.backgroundColor), bandBg), fg = parseRgba(cs.color);
      const lBg = lum(elBg), lFg = lum(fg);
      const cr = (Math.max(lBg, lFg) + 0.05) / (Math.min(lBg, lFg) + 0.05);
      if (cr < 7.0) errs.push(`[M7_SCRIM_AAA] '${el.textContent.trim()}' contrast=${cr.toFixed(2)} < 7.0`);
    }
  }
}
for (const p of document.querySelectorAll('.va-pill')) {
  const cs = getComputedStyle(p);
  const rad = parseFloat(cs.borderTopLeftRadius || '0');
  const v = p.dataset.variant, st = p.dataset.state, txt = (p.textContent || '').trim();
  if (/[\\x5b\\x5d]|\\bMargin\\b/.test(txt)) errs.push(`[ATOMIC_PILL] Non-atomic pill '${txt}'`);
  if (v === 'status' && txt.length > 22) errs.push(`[ATOMIC_PILL] Status pill too long (${txt.length} > 22): '${txt}'`);
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


def capture_gate5_gallery(driver: Any, base_url: str, shots_dir: Path) -> None:
    shots_dir.mkdir(parents=True, exist_ok=True)
    shots = [
        ("01_studio_unified_worlds_v04_desktop.png", 1440, 900, "world=02-cloud-cyber-and-ai-ops&view=v04-sre-incident-workbench&theme=white"),
        ("02_studio_mode_bench_embedded.png", 1440, 900, "mode=bench&theme=white"),
        ("03_studio_mode_atlas_embedded.png", 1440, 900, "mode=atlas&theme=white"),
        ("04_v05_zero_trust_ato_m1_sheet.png", 1440, 900, "world=02-cloud-cyber-and-ai-ops&view=v05-zero-trust-ato-spec&medium=m1&theme=white"),
        ("05_v06_ai_drift_lineage_ide_oled.png", 1440, 900, "world=02-cloud-cyber-and-ai-ops&view=v06-ai-drift-and-lineage-ide&theme=dark"),
        ("06_v07_scada_poi_console_desktop.png", 1440, 900, "world=03-industrial-grid-and-manufacturing&view=v07-grid-scada-poi-console&theme=white"),
        ("07_v08_plant_floor_wall_kiosk_m5.png", 1920, 1080, "world=03-industrial-grid-and-manufacturing&view=v08-plant-floor-wall-kiosk&theme=dark"),
        ("08_v10_civic_budget_waterfall_paper.png", 1440, 900, "world=04-civic-finance-and-stem-learning&view=v10-civic-capital-budget-deck&theme=paper"),
        ("09_v12_stem_rc_lab_mobile_390x844.png", 390, 844, "world=04-civic-finance-and-stem-learning&view=v12-stem-interactive-lab&theme=white"),
    ]
    for fname, w, h, qs in shots:
        set_viewport(driver, w, h, 2)
        driver.get(f"{base_url}?{qs}")
        time.sleep(0.55)
        driver.save_screenshot(str(shots_dir / fname))
    set_viewport(driver, 1440, 900, 2)
    driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v15-collimated-flight-hud&theme=dark")
    time.sleep(0.45)
    p1 = shots_dir / "_tmp_v15.png"
    driver.save_screenshot(str(p1))
    driver.get(f"{base_url}?world=05-physical-systems-auto-and-aero&view=v16-transparent-window-overlay&theme=white")
    time.sleep(0.45)
    p2 = shots_dir / "_tmp_v16.png"
    driver.save_screenshot(str(p2))
    composite = shots_dir / "10_v15_m6_flight_hud_and_v16_m7_glass.png"
    try:
        from PIL import Image
        im1, im2 = Image.open(p1), Image.open(p2)
        canvas = Image.new("RGB", (im1.width + im2.width, max(im1.height, im2.height)))
        canvas.paste(im1, (0, 0))
        canvas.paste(im2, (im1.width, 0))
        canvas.save(str(composite))
        p1.unlink(missing_ok=True)
        p2.unlink(missing_ok=True)
    except Exception:
        p1.rename(composite)
