# SPDX-License-Identifier: Apache-2.0
"""Print-flow collision, prose column starvation, nested scroll, code luminance, and plot label probes."""

from __future__ import annotations

import time
from typing import Any

CDP_EDITORIAL_PRINT_JS = r"""
function _parseAlpha(aRaw) {
  if (aRaw == null || aRaw === '') return 1;
  const s = String(aRaw).trim();
  const v = s.endsWith('%') ? parseFloat(s) / 100 : parseFloat(s);
  return Number.isFinite(v) ? v : 1;
}

function parseColorLum(str) {
  const s = String(str || '').trim().toLowerCase();
  if (!s || s === 'transparent' || s === 'none') return null;
  const chan = (c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const rgba = s.match(/^rgba?\(\s*(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)(?:\s*[,/]\s*([^)\s]+))?/);
  if (rgba) {
    if (!(_parseAlpha(rgba[4]) >= 0.72)) return null;
    return 0.2126 * chan(Number(rgba[1]) / 255) + 0.7152 * chan(Number(rgba[2]) / 255) + 0.0722 * chan(Number(rgba[3]) / 255);
  }
  const srgb = s.match(/^color\(\s*srgb\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)(?:\s*\/\s*([^)\s]+))?/);
  if (srgb) {
    if (!(_parseAlpha(srgb[4]) >= 0.72)) return null;
    return 0.2126 * chan(Number(srgb[1])) + 0.7152 * chan(Number(srgb[2])) + 0.0722 * chan(Number(srgb[3]));
  }
  const ok = s.match(/^okl(?:ch|ab)\(\s*([0-9.]+)(%?)(?:\s+[^/)]+){2}(?:\s*\/\s*([^)\s]+))?/);
  if (ok) {
    if (!(_parseAlpha(ok[3]) >= 0.72)) return null;
    const l = ok[2] === '%' ? parseFloat(ok[1]) / 100 : parseFloat(ok[1]);
    return Math.pow(Math.max(0, Math.min(1, l)), 2.2);
  }
  return null;
}

function auditDocEditorial(doc, win, ctxTag, opts) {
  const vwCur = (win === window ? vw : win.innerWidth) || win.innerWidth || 1280;
  const theme = (doc.documentElement.getAttribute('data-theme') || 'white').toLowerCase();
  const medium = (doc.documentElement.getAttribute('data-medium') || 'm2').toLowerCase();

  // Collect direct narrative containers holding paragraph blocks without chart/table chrome (ignoring small inline icons)
  const proseBoxes = new Set();
  for (const pEl of doc.querySelectorAll('p')) {
    if (!pEl.parentElement || !isVis(pEl, win.getComputedStyle(pEl)) || pEl.closest('[hidden], figure, svg, table, dialog, nav, pre, code')) continue;
    const box = pEl.parentElement;
    if (!box || box.matches('body, html, main')) continue;
    if (box.querySelector('figure, table')) continue;
    const hasChartSvg = [...box.querySelectorAll('svg')].some((s) => s.getBoundingClientRect().width > 48 && s.getBoundingClientRect().height > 32);
    if (!hasChartSvg) proseBoxes.add(box);
  }

  // 1. [PROSE_COLUMN_STARVATION] Desktop narrative column squeezed < 260px (~35ch) beside chart/visual
  if (vwCur >= 1024) {
    const visuals = [...doc.querySelectorAll('figure, svg, table, .qe-figure, .va-figure-card')].filter((el) => {
      if (!isVis(el, win.getComputedStyle(el)) || el.closest('[hidden]')) return false;
      const r = el.getBoundingClientRect();
      return r.width > 120 && r.height > 80;
    });
    for (const pBox of proseBoxes) {
      const cs = win.getComputedStyle(pBox);
      if (!isVis(pBox, cs) || pBox.closest('[hidden]')) continue;
      const pText = [...pBox.querySelectorAll(':scope > p')].map((x) => x.textContent || '').join(' ').replace(/\s+/g, ' ').trim();
      if (pText.length < 100) continue;
      const pr = pBox.getBoundingClientRect();
      if (pr.width >= 260 || pr.width <= 20) continue;
      const beside = visuals.some((v) => {
        if (pBox.contains(v) || v.contains(pBox)) return false;
        const vr = v.getBoundingClientRect();
        const ovY = Math.min(pr.bottom, vr.bottom) - Math.max(pr.top, vr.top);
        return ovY > 28 && Math.abs(pr.left - vr.left) > 40;
      });
      if (beside) {
        pushErr(`[PROSE_COLUMN_STARVATION${ctxTag}] @${vwCur}px: narrative prose column width=${pr.width.toFixed(0)}px < 260px (~35ch) beside visual`);
      }
    }
  }

  // 2. [NESTED_PROSE_SCROLL] Narrative prose trapped inside internal scroll-box or fade mask
  for (const el of proseBoxes) {
    if (el.closest('.va-table-wrap, .va-table-region, .va-rail-scroll, .va-tree-root, .qe-spec-drawer, pre, code')) continue;
    const cs = win.getComputedStyle(el);
    if (!isVis(el, cs) || el.closest('[hidden]')) continue;
    if (el.querySelectorAll(':scope > p').length < 2) continue;
    const r = el.getBoundingClientRect();
    const maskImg = String(cs.maskImage || cs.webkitMaskImage || '');
    const clippedScroll = (cs.overflowY === 'auto' || cs.overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 24 && r.height < 480;
    const fadeMask = maskImg && maskImg !== 'none' && /gradient/i.test(maskImg);
    if (clippedScroll || fadeMask) {
      pushErr(`[NESTED_PROSE_SCROLL${ctxTag}] @${vwCur}px: narrative commentary trapped in nested scroll-box or fade mask (${el.scrollHeight}px > ${el.clientHeight}px)`);
    }
  }

  // 3. [CODE_LUMINANCE_SHOCK] Pitch-black #000000 code blocks on light reading surfaces
  const bodyLum = parseColorLum(win.getComputedStyle(doc.body || doc.documentElement).backgroundColor);
  const isLightTheme = theme === 'white' || theme === 'paper' || (theme === 'default' && (bodyLum === null || bodyLum > 0.45));
  if (isLightTheme && !['m4', 'm6', 'm7'].includes(medium)) {
    for (const pre of doc.querySelectorAll('pre, pre > code')) {
      if (pre.closest('details:not([open]), [hidden]')) continue;
      const cs = win.getComputedStyle(pre);
      if (!isVis(pre, cs)) continue;
      const r = pre.getBoundingClientRect();
      if (r.width < 120 || r.height < 26) continue;
      const lum = parseColorLum(cs.backgroundColor);
      if (lum !== null && lum < 0.04) {
        pushErr(`[CODE_LUMINANCE_SHOCK${ctxTag}] @${vwCur}px: pitch-dark <pre>/<code> background (L=${lum.toFixed(3)}) inside light theme '${theme}'`);
      }
    }
  }

  // 4. [DIAGONAL_TICK_OR_ROTATED_Y_TITLE] & [END_LABEL_CLIP]
  for (const svg of doc.querySelectorAll('svg')) {
    const scs = win.getComputedStyle(svg);
    if (!isVis(svg, scs) || svg.closest('[hidden]')) continue;
    const sr = svg.getBoundingClientRect();
    if (sr.width < 60 || sr.height < 40) continue;
    const isSchematic = svg.matches('.qe-schematic-svg, .va-schematic-svg') || !!svg.closest('.qe-schematic-wrap');
    const takeCard = svg.closest('.va-figure-card, .qe-figure');
    const takeSub = takeCard ? (takeCard.querySelector('.qe-takeaway-subtitle')?.textContent || '').toLowerCase() : '';
    const leftVertTexts = [];

    for (const t of svg.querySelectorAll('text')) {
      const tcs = win.getComputedStyle(t);
      if (!isVis(t, tcs)) continue;
      const raw = (t.textContent || '').trim();
      if (!raw) continue;
      const r = t.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;

      if (!isSchematic && (r.right > sr.right + 1.5 || r.left < sr.left - 1.5)) {
        pushErr(`[END_LABEL_CLIP${ctxTag}] @${vwCur}px: SVG label '${raw.slice(0, 24)}' clips past chart horizontal boundary`);
      }
      if (!isSchematic && (/\.\.\.$|…$/.test(raw)) && raw.length >= 4) {
        pushErr(`[END_LABEL_CLIP${ctxTag}] @${vwCur}px: truncated SVG label '${raw.slice(0, 26)}' uses ellipsis instead of wrapping or wider gutter`);
      }

      const deg = getRotDeg(t, tcs) % 180;
      const isBottomTick = !!t.closest('[data-axis="x"], .tick') || (r.top >= sr.top + sr.height * 0.66 && !t.classList.contains('va-svg-halo-text') && r.height < 64);
      if (isBottomTick && deg >= 12 && deg <= 78) {
        pushErr(`[DIAGONAL_TICK_OR_ROTATED_Y_TITLE${ctxTag}] @${vwCur}px: diagonal rotated X-axis tick '${raw.slice(0, 18)}' (${deg.toFixed(0)}deg)`);
      }
      if (deg >= 78 && deg <= 102 && r.left < sr.left + 64) {
        leftVertTexts.push({ raw, t, r });
        const hasLineTspan = [...t.querySelectorAll('tspan')].some((ts) => Math.abs(parseFloat(ts.getAttribute('dy') || '0')) >= 8);
        const yToks = raw.toLowerCase().replace(/[^a-z0-9%]+/g, ' ').trim().split(/\s+/).filter((w) => w.length >= 4);
        const dupSubUnit = !!(takeSub && yToks.length >= 2 && yToks.every((w) => takeSub.includes(w)));
        if (hasLineTspan || dupSubUnit) {
          pushErr(`[DIAGONAL_TICK_OR_ROTATED_Y_TITLE${ctxTag}] @${vwCur}px: multi-line or redundant rotated Y-axis title '${raw.slice(0, 24)}'`);
        }
      }
    }
    if (leftVertTexts.length >= 2) {
      pushErr(`[DIAGONAL_TICK_OR_ROTATED_Y_TITLE${ctxTag}] @${vwCur}px: multi-line rotated vertical Y-axis title block`);
    }
  }
}
"""

_PRINT_AUDIT_JS = r"""
const errs = [];
function auditPrintDoc(doc, win, tag) {
  const pageW = doc.documentElement.clientWidth || win.innerWidth || 800;
  const isVisP = (el, cs) => {
    if (!el || !cs || cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') === 0) return false;
    for (let p = el; p && p.nodeType === 1; p = p.parentElement) {
      if (p.hasAttribute('hidden')) return false;
      if (p !== el && win.getComputedStyle(p).display === 'none') return false;
    }
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  for (const el of doc.querySelectorAll('*')) {
    if (/^(SCRIPT|STYLE|NOSCRIPT|SVG|PATH|CIRCLE|RECT|LINE|POLYGON|TEXT)$/.test(el.tagName)) continue;
    const cs = win.getComputedStyle(el);
    if (cs.position === 'fixed' && isVisP(el, cs)) {
      const r = el.getBoundingClientRect();
      if (r.width > 16 && r.height > 8) errs.push(`[PRINT_FLOW_COLLISION${tag}] fixed-position element remains visible under @media print: ${(el.className || el.tagName).toString().slice(0, 32)}`);
    }
  }
  const figs = [...doc.querySelectorAll('figure, .va-figure-card, .qe-figure, svg')].filter((el) => {
    if (!isVisP(el, win.getComputedStyle(el))) return false;
    if (el.tagName === 'SVG' && el.closest('figure, .va-figure-card, .qe-figure')) return false;
    const r = el.getBoundingClientRect();
    return r.width > 48 && r.height > 40;
  });
  const proseNodes = [...doc.querySelectorAll('h1, h2, h3, h4, p, blockquote, li')].filter((p) => {
    if (p.closest('figure, .va-figure-card, .qe-figure, svg, dialog')) return false;
    if (!isVisP(p, win.getComputedStyle(p))) return false;
    return (p.textContent || '').trim().length >= 12;
  });
  for (const f of figs) {
    const fr = f.getBoundingClientRect();
    for (const p of proseNodes) {
      if (f.contains(p) || p.contains(f)) continue;
      const pr = p.getBoundingClientRect();
      const dx = Math.min(fr.right, pr.right) - Math.max(fr.left, pr.left);
      const dy = Math.min(fr.bottom, pr.bottom) - Math.max(fr.top, pr.top);
      if (dx > 6 && dy > 6) {
        errs.push(`[PRINT_FLOW_COLLISION${tag}] figure overlaps text '${(p.textContent || '').trim().slice(0, 26)}' under @media print`);
        break;
      }
    }
  }
  for (const blk of doc.querySelectorAll('.va-editorial-callouts, .va-callout-stat, .va-kpi-grid, .va-kpi-gauge-grid, table')) {
    const cs = win.getComputedStyle(blk);
    if (!isVisP(blk, cs)) continue;
    const r = blk.getBoundingClientRect();
    if (r.right > pageW + 3) {
      errs.push(`[PRINT_FLOW_COLLISION${tag}] stat strip or table overflows print page width (${r.right.toFixed(0)} > ${pageW})`);
    }
  }
  for (const fr of doc.querySelectorAll('iframe')) {
    try {
      if (fr.contentDocument && fr.contentDocument.documentElement && isVisP(fr, win.getComputedStyle(fr))) {
        auditPrintDoc(fr.contentDocument, fr.contentWindow || win, tag + ' iframe#' + (fr.id || 'frame'));
      }
    } catch (_err) {}
  }
}
auditPrintDoc(document, window, '');
return errs;
"""


def probe_print_flow_collision(driver: Any, url: str, theme: str) -> list[str]:
    """Emulate @media print at portrait Letter width and assert zero print collisions or clips."""
    errs: list[str] = []
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 820, "height": 1100, "deviceScaleFactor": 1, "mobile": False})
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
    try:
        time.sleep(0.14)
        for msg in driver.execute_script(_PRINT_AUDIT_JS) or ():
            errs.append(f"[{url} theme={theme}] {msg}")
    finally:
        driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
        driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
    return errs
