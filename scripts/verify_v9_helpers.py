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
if (view === 'v15-collimated-flight-hud') {
  const photos = [...document.querySelectorAll('#v15-hud-stage img.v9-opt-photo')];
  if (photos.length !== 3) errs.push(`[M6_PHOTOS] Expected 3 photographic backplates, found ${photos.length}`);
  for (const img of photos) {
    if (!img.complete || img.naturalWidth < 1200) errs.push(`[M6_PHOTO_LOAD] Backplate ${img.dataset.asset} unloaded (w=${img.naturalWidth})`);
  }
  if (document.querySelectorAll('.v15-scene-svg, .v16-scene-svg, .v16-corridor-svg').length) {
    errs.push('[M6_SYNTHETIC] Synthetic scenery SVG found in v15');
  }
  const ret = document.querySelector('.v15-reticle-layer');
  const retTxt = ret ? (ret.textContent || '') : '';
  for (const sym of ['138', '1,180', '084', '+5', '-5', 'VS -650 FPM', '42.8%']) {
    if (!retTxt.includes(sym)) errs.push(`[M6_RETICLE] Missing MIL-STD-1787B symbology '${sym}'`);
  }
  if (ret && ret.querySelectorAll('line[y1="360"][y2="360"]').length < 2) {
    errs.push('[HUD_HORIZON_50] Expected 0 deg horizon wing lines at y=360 (50% of 720)');
  }
  for (const bad of ['BORESIGHT', 'NAV/PROPULSION HUD', 'dual stroke halo']) {
    if (visBody.includes(bad)) errs.push(`[M6_META_LEAK] v15 leaked '${bad}'`);
  }
  const pRgba = (s) => (s.match(/[\\d.]+/g) || [0, 0, 0, 1]).map(Number);
  const cLum = ([r, g, b]) => { const f = (v) => { const x = v / 255; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  for (const ch of document.querySelectorAll('.v15-hud-chip, .v16-lum-chip')) {
    const cs = getComputedStyle(ch), bg = pRgba(cs.backgroundColor), fg = pRgba(cs.color), a = bg.length >= 4 ? bg[3] : 1;
    const comp = [bg[0] * a + 2 * (1 - a), bg[1] * a + 6 * (1 - a), bg[2] * a + 23 * (1 - a)];
    const l1 = cLum(comp), l2 = cLum(fg), cr = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    if (cr < 4.5) errs.push(`[M6_CHIP_CONTRAST] '${ch.textContent.trim()}' contrast=${cr.toFixed(2)} < 4.5`);
  }
  if (w >= 1400) {
    const h = window.innerHeight, kx0 = w * 0.175, kx1 = w * 0.825, ky0 = h * 0.15, ky1 = h * 0.85;
    let occ = 0;
    for (const el of document.querySelectorAll('.v15-hud-stage *')) {
      if (el.closest('svg') || el.tagName === 'IMG') continue;
      const bg = getComputedStyle(el).backgroundColor;
      if (!bg || bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') continue;
      const r = el.getBoundingClientRect();
      occ += Math.max(0, Math.min(r.right, kx1) - Math.max(r.left, kx0)) * Math.max(0, Math.min(r.bottom, ky1) - Math.max(r.top, ky0));
    }
    const clearPct = 100 * (1 - occ / ((kx1 - kx0) * (ky1 - ky0)));
    if (clearPct < 65.0) errs.push(`[M6_KEEPOUT] Central boresight clear=${clearPct.toFixed(1)}% < 65%`);
  }
}
if (view === 'v16-transparent-window-overlay') {
  const photos = [...document.querySelectorAll('#v16-glass-viewport img.v9-opt-photo')];
  if (photos.length !== 3) errs.push(`[M7_PHOTOS] Expected 3 photographic backplates, found ${photos.length}`);
  for (const img of photos) {
    if (!img.complete || img.naturalWidth < 1200) errs.push(`[M7_PHOTO_LOAD] Backplate ${img.dataset.asset} unloaded (w=${img.naturalWidth})`);
  }
  if (document.querySelectorAll('.v15-scene-svg, .v16-scene-svg, .v16-corridor-svg').length) {
    errs.push('[M7_SYNTHETIC] Synthetic scenery SVG found in v16');
  }
  const vp = document.getElementById('v16-glass-viewport');
  const lumMode = vp ? (vp.dataset.luminance || 'daylight') : 'daylight';
  const sceneBackdrop = lumMode === 'night' ? [15, 23, 42] : (lumMode === 'dusk' ? [180, 83, 9] : [224, 242, 254]);
  const parseRgba = (s) => (s.match(/[\\d.]+/g) || [0, 0, 0, 1]).map(Number);
  const over = (fg, bg) => {
    const a = fg.length >= 4 ? fg[3] : 1;
    return [fg[0] * a + bg[0] * (1 - a), fg[1] * a + bg[1] * (1 - a), fg[2] * a + bg[2] * (1 - a)];
  };
  const lum = ([r, g, b]) => {
    const f = (v) => { const x = v / 255; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const h = window.innerHeight, kx0 = w * 0.24, kx1 = w * 0.76, ky0 = h * 0.24, ky1 = h * 0.68;
  const pods = [...document.querySelectorAll('.v16-glass-pod')];
  if (w < 640 && pods.length) {
    const visorH = Math.max(...pods.map(p => p.getBoundingClientRect().bottom)) - Math.min(...pods.map(p => p.getBoundingClientRect().top));
    const maxBot = Math.max(...pods.map(p => p.getBoundingClientRect().bottom));
    if (visorH > 145 || maxBot > 155) errs.push(`[M7_MOBILE_VISOR] Visor height=${visorH.toFixed(1)}px bottom=${maxBot.toFixed(1)}px > 145/155px`);
  }
  for (const pod of pods) {
    const cs = getComputedStyle(pod), pr = pod.getBoundingClientRect();
    const bf = cs.backdropFilter || cs.webkitBackdropFilter || '';
    if (!bf.includes('blur(')) errs.push(`[M7_BLUR] Glass pod missing backdrop-filter blur (got '${bf}')`);
    if (pr.width > 420.5) errs.push(`[M7_POD_WIDTH] Pod width ${pr.width.toFixed(1)}px > 420px`);
    if (w >= 1400 && Math.min(pr.right, kx1) > Math.max(pr.left, kx0) + 1 && Math.min(pr.bottom, ky1) > Math.max(pr.top, ky0) + 1) {
      errs.push(`[M7_CORRIDOR] Pod overlaps central windshield corridor at ${w}`);
    }
    const podBg = over(parseRgba(cs.backgroundColor), sceneBackdrop);
    for (const el of pod.querySelectorAll('.v16-speed-val, .v16-speed-unit, .v16-speed-cap, .v16-route-line, .v16-eff-line, .v16-warn-title, .v16-warn-action, .va-pill')) {
      const ecs = getComputedStyle(el);
      if (ecs.display === 'none' || ecs.visibility === 'hidden') continue;
      const elBg = over(parseRgba(ecs.backgroundColor), podBg), fg = parseRgba(ecs.color);
      const lBg = lum(elBg), lFg = lum(fg);
      const cr = (Math.max(lBg, lFg) + 0.05) / (Math.min(lBg, lFg) + 0.05);
      if (cr < 7.0) errs.push(`[M7_SCRIM_AAA] (${lumMode}) '${el.textContent.trim()}' contrast=${cr.toFixed(2)} < 7.0`);
    }
  }
  for (const bad of ['0x18FEF100', 'Offset: 0x', 'SCRIM:', 'NO FLASH', '>= 7.0:1', 'preserves', '120 Ω']) {
    if (visBody.includes(bad)) errs.push(`[M7_META_LEAK] v16 leaked '${bad}'`);
  }
}
for (const p of document.querySelectorAll('.va-pill')) {
  const cs = getComputedStyle(p), rad = parseFloat(cs.borderTopLeftRadius || '0');
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
for (const badTxt of ['QUIET-BRIDGE', 'Murder-Board', 'Murder-board', 'Qualification Bench', 'Booktabs', 'Home Nominal', 'Unlock Arm', 'Arm Door']) {
  if (visBody.includes(badTxt)) errs.push(`[PLAIN_ENGLISH] ${view} leaked '${badTxt}'`);
}
const taxHit = visBody.match(/\\b(?:L[123]|M[1-7])\\b|\\[data-term\\]/);
if (taxHit) errs.push(`[TAXONOMY_LEAK] ${view} exposed '${taxHit[0]}'`);
if (/\\bV\\d{2}:/.test(visBody)) errs.push(`[PREFIX_LEAK] ${view} leaked VXX: prefix in visible content`);
if (w >= 700 && w < 1100 && medium !== 'm1') {
  const mh = document.querySelector('.v9-masthead');
  if (mh && getComputedStyle(mh).display !== 'none') {
    const eb = mh.querySelector('.v9-masthead-eyebrow'), h1 = mh.querySelector('.v9-masthead-title');
    if (eb && h1) {
      const er = eb.getBoundingClientRect(), hr = h1.getBoundingClientRect();
      if (hr.left - er.left > 8.0 || hr.top < er.bottom - 2.0) errs.push(`[FOLD_MASTHEAD_SPLIT] ${view} title left-offset=${(hr.left - er.left).toFixed(1)}px top=${hr.top.toFixed(1)} vs eyebrow.bottom=${er.bottom.toFixed(1)}`);
    }
  }
}
if (view === 'v06-ai-drift-and-lineage-ide') {
  for (const rawTok of ['p_hat', 'f_obs', '+/- u_y']) {
    if (visBody.includes(rawTok)) errs.push(`[V06_POLISH] Raw token '${rawTok}' leaked`);
  }
}
if (view === 'v07-grid-scada-poi-console' && w >= 1400) {
  const cards4 = [...document.querySelectorAll('.qe-scalar-grid[data-count="4"] > .qe-scalar-card')];
  if (cards4.length === 4) {
    const tops = cards4.map(c => c.getBoundingClientRect().top);
    if (Math.max(...tops) - Math.min(...tops) > 2.0) errs.push(`[V07_4UP] Expected 1 row of 4 scalars, got y=${tops.map(v => v.toFixed(0)).join(',')}`);
  }
  const topo = document.getElementById('v07-topology');
  if (!topo || topo.getBoundingClientRect().top >= 900) errs.push(`[V07_FOLD] Topology top=${topo ? topo.getBoundingClientRect().top.toFixed(0) : 'missing'} >= 900`);
}
if (view === 'v08-plant-floor-wall-kiosk' && w >= 1900) {
  if (visBody.includes('10-FT WALL DISPLAY')) errs.push('[V08_KICKER] Unwanted 10-FT WALL DISPLAY tag');
  for (const kc of document.querySelectorAll('.v08-kpi-card')) {
    if (parseFloat(getComputedStyle(kc).borderTopWidth || '0') > 1.5) errs.push('[V08_BORDER] Heavy colored top border on v08 card');
  }
}
if (view === 'v12-stem-interactive-lab') {
  for (const rawTok of ['tau =', 'tau_s', 'u_y', '+/-']) {
    if (visBody.includes(rawTok)) errs.push(`[V12_MATH] Raw ASCII token '${rawTok}' leaked`);
  }
  if (!visBody.includes('τ') || !visBody.includes('V0')) errs.push('[V12_MATH] Expected formatted Unicode τ and V₀');
}
if (view === 'v16-transparent-window-overlay' && w >= 1400) {
  const tb = document.getElementById('va-shell-topbar');
  if (tb && getComputedStyle(tb).display !== 'none') errs.push('[V16_FULLBLEED] Top shell bar not hidden on M7');
}
for (const pw of document.querySelectorAll('.qe-plot-wrap[data-echarts-active="true"]')) {
  const ls = pw.querySelector('.qe-legend-series');
  if (ls && getComputedStyle(ls).display !== 'none') errs.push('[SINGLE_LEGEND] Duplicate HTML legend visible over ECharts');
  if (/\\b[A-Za-z]\\((?:pv|load|grid|rx|obs|bte)\\)/i.test(pw.innerText || '')) errs.push('[ECHARTS_ASCII] ASCII pseudo-subscript in plot');
  try {
    const pld = JSON.parse(pw.dataset.quietEcharts || '{}');
    const hostTxt = pw.querySelector('.qe-echarts-host svg')?.textContent || '';
    if (['v06-ai-drift-and-lineage-ide', 'v11-treasury-stress-test-solver', 'v12-stem-interactive-lab', 'v13-propulsion-archival-monograph'].includes(view)) {
      if (!pld.residuals || !pld.residuals.points || pld.residuals.points.length < 5) errs.push(`[ECHARTS_RESIDUAL] ${view} missing residual points payload`);
      if (!hostTxt.includes('+2σ') || !hostTxt.includes('−2σ')) errs.push(`[ECHARTS_RESIDUAL_SVG] ${view} residual strip ticks missing in ECharts SVG`);
      for (const s of (pld.series || [])) {
        if (s.epistemic === 'discrete_measurement' && s.connectPiecewise) errs.push(`[ECHARTS_DISCRETE_LINE] ${view} discrete series unexpectedly connected`);
        if (s.epistemic === 'analytical_model' && (!Array.isArray(s.corridor) || s.corridor.length < 2)) errs.push(`[ECHARTS_CORRIDOR] ${view} missing shaded corridor`);
      }
      if (view === 'v06-ai-drift-and-lineage-ide' && !(pld.envelopes || []).some(e => Array.isArray(e.points) && e.points.length >= 2)) {
        errs.push('[ECHARTS_SLOPED_ENV] v06 missing sloped calibration gate envelope');
      }
    }
    if (view === 'v10-civic-capital-budget-deck') {
      if (!Array.isArray(pld.totals) || !(pld.envelopes || []).length || !hostTxt.includes('Policy Reserve Floor')) {
        errs.push('[ECHARTS_WATERFALL] v10 missing total bars or Policy Reserve Floor markLine');
      }
    }
  } catch (_e) { errs.push('[ECHARTS_PAYLOAD] Invalid JSON descriptor'); }
}
return errs;
"""

def set_viewport(driver: Any, width: int, height: int, scale: int = 1) -> None:
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": scale, "mobile": width < 600})
