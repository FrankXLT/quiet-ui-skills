# SPDX-License-Identifier: Apache-2.0
"""Live Chrome DOM/SVG/Chart/Navbar JS probes for Quiet UI CDP auditor."""

from __future__ import annotations

import time
from typing import Any

CDP_SVG_PROBES_JS = r"""
function isRectPathD(d) {
  const s = String(d || '').trim();
  return /^M/i.test(s) && /[Zz]\s*$/.test(s) && (s.match(/[CcSsQqTtAa]/g) || []).length <= 4;
}

function isNonBarSvg(svg) {
  if (svg.closest('.qe-schematic-wrap, .qe-bitfield-wrap, .qe-heatmap-wrap, .qe-gantt-wrap, .qe-sankey-wrap, .qe-waveform-wrap')) return true;
  if (svg.matches('.qe-schematic-svg, .qe-bitfield-svg, .qe-gauge-svg, .qe-spark-svg, .qe-sparkline-svg, .va-schematic-svg, .qe-sankey-svg, .qe-heatmap-svg, .qe-waveform-svg')) return true;
  const al = (svg.getAttribute('aria-label') || '').toLowerCase();
  if (/\b(heatmap|heat map|sankey|schematic|topology|register|bitfield|fsm|state machine|schedule|gantt|sequence|lineage|waveform|oscilloscope|pipeline dag|interlock)\b/.test(al)) return true;
  const wrap = svg.closest('.qe-plot-wrap[data-quiet-echarts]');
  if (wrap && wrap.dataset.quietEcharts) {
    try {
      const m = JSON.parse(wrap.dataset.quietEcharts);
      if (m && /^(heatmap|gantt|sankey|gauge|radar|pie|treemap|scatter|line|area|waterfall|dumbbell|forest)$/i.test(String(m.kind || ''))) return true;
    } catch (_e) {}
  }
  return false;
}

function parseAlphaVal(raw) {
  if (!raw) return 1;
  const t = String(raw).trim();
  if (t.endsWith('%')) return Math.max(0, Math.min(1, parseFloat(t) / 100));
  const v = parseFloat(t);
  return Number.isFinite(v) ? Math.max(0, Math.min(1, v)) : 0;
}

function parseAlphaColor(str) {
  const s = String(str || '').trim().toLowerCase();
  if (!s || s === 'transparent' || s === 'none') return 0;
  const rgba = s.match(/^rgba\(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([^)]+)\)/);
  if (rgba) return parseAlphaVal(rgba[1]);
  if (/^(?:rgb|hsl|hwb|lab|lch|oklab|oklch|color)\(/.test(s)) {
    const slash = s.match(/\/\s*([^)\s]+)\s*\)$/);
    return slash ? parseAlphaVal(slash[1]) : 1;
  }
  const hxA = s.match(/^#([0-9a-f]{4}|[0-9a-f]{8})$/);
  if (hxA) {
    const h = hxA[1];
    return h.length === 4 ? parseInt(h[3] + h[3], 16) / 255 : parseInt(h.slice(6, 8), 16) / 255;
  }
  if (/^#[0-9a-f]{3}([0-9a-f]{3})?$/.test(s)) return 1;
  return 0;
}

function chromaticSeriesKey(str) {
  const s = String(str || '').trim().toLowerCase();
  if (!s || isTransparentPaint(s)) return '';
  const m = s.match(/^rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/);
  if (m) {
    const r = Number(m[1]), g = Number(m[2]), b = Number(m[3]);
    if (Math.max(r, g, b) - Math.min(r, g, b) <= 22) return '';
    return `${Math.round(r / 12)}-${Math.round(g / 12)}-${Math.round(b / 12)}`;
  }
  const hx = s.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/);
  if (!hx) return '';
  let h = hx[1];
  if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
  const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
  if (Math.max(r, g, b) - Math.min(r, g, b) <= 22) return '';
  return `${Math.round(r / 12)}-${Math.round(g / 12)}-${Math.round(b / 12)}`;
}

function hasCardLegendOrTable(svg, doc, win, box) {
  const card = svg.closest('.va-card, .qe-card, .qe-bench-card, .qe-figure, .v9-figure, .qe-plot-wrap, figure, section, article') || svg.parentElement;
  if (card) {
    for (const lg of card.querySelectorAll('.qe-legend-series, [class*="legend"], table')) {
      if (isVis(lg, win.getComputedStyle(lg)) && (lg.textContent || '').trim().length > 0) return true;
    }
  }
  const outsideSwatches = [];
  for (const el of svg.querySelectorAll('rect, path, circle, line')) {
    const cs = win.getComputedStyle(el);
    if (!isVis(el, cs)) continue;
    const ck = chromaticSeriesKey(el.getAttribute('fill') || cs.fill) || chromaticSeriesKey(el.getAttribute('stroke') || cs.stroke);
    if (!ck) continue;
    const er = el.getBoundingClientRect();
    const outBox = !box || er.bottom <= box.yt + 4 || er.top >= box.yb + 14 || er.left >= box.xr - 2;
    if (outBox && er.width > 0 && er.width <= 32 && er.height > 0 && er.height <= 24) outsideSwatches.push(er);
  }
  if (outsideSwatches.length >= 2) return true;
  const outTexts = [...svg.querySelectorAll('text')].filter((t) => {
    const cs = win.getComputedStyle(t);
    if (!isVis(t, cs) || !(t.textContent || '').trim()) return false;
    const tr = t.getBoundingClientRect();
    return box && (tr.bottom <= box.yt + 2 || tr.left >= box.xr + 2);
  });
  return outTexts.length >= 2 && outsideSwatches.length >= 1;
}

function auditSvgV922(svg, doc, win, ctxTag, sr, box) {
  for (const t of svg.querySelectorAll('text')) {
    const cs = win.getComputedStyle(t);
    if (!isVis(t, cs)) continue;
    const raw = (t.textContent || '').trim();
    if (!raw) continue;
    const r = t.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    if (r.left < sr.left - 2 || r.right > sr.right + 2 || r.top < sr.top + 0.5 || r.bottom > sr.bottom + 2) {
      pushErr(`[AXIS_LABEL_CLIPPED${ctxTag}] @${vw}px: SVG text '${raw.slice(0, 28)}' clips SVG bounds`);
    }
  }
  if (!box || isNonBarSvg(svg)) return;
  const bw = box.xr - box.xl, bh = box.yb - box.yt;
  if (bw < 40 || bh < 20) return;
  const bars = [], yRows = new Set(), seriesColors = new Set();
  for (const sh of svg.querySelectorAll('rect, path, circle, line')) {
    const tag = (sh.tagName || '').toLowerCase();
    const cs = win.getComputedStyle(sh);
    if (!isVis(sh, cs)) continue;
    const r = sh.getBoundingClientRect();
    if (r.left < box.xl - 4 || r.right > box.xr + 4 || r.top < box.yt - 4 || r.bottom > box.yb + 4) continue;
    const fill = String(sh.getAttribute('fill') || cs.fill || 'none').toLowerCase();
    const stroke = String(sh.getAttribute('stroke') || cs.stroke || 'none').toLowerCase();
    const fo = parseFloat(sh.getAttribute('fill-opacity') || cs.fillOpacity || '1');
    const dash = String(sh.getAttribute('stroke-dasharray') || cs.strokeDasharray || '');
    const isDashedRef = dash && dash !== 'none';
    const isFrame = r.width >= bw * 0.88 && r.height >= bh * 0.88;
    if (!isFrame && !isDashedRef) {
      if (fo >= 0.35) { const ck = chromaticSeriesKey(fill); if (ck) seriesColors.add(ck); }
      const sw = parseFloat(sh.getAttribute('stroke-width') || cs.strokeWidth || '0');
      if (sw >= 1.5 && r.height < bh * 0.85 && r.width < bw * 0.85) {
        const sk = chromaticSeriesKey(stroke);
        if (sk) seriesColors.add(sk);
      }
    }
    if (tag !== 'rect' && tag !== 'path') continue;
    if (tag === 'path' && !isRectPathD(sh.getAttribute('d'))) continue;
    if (isTransparentPaint(fill) || fo < 0.25) continue;
    if (r.height < 2 || r.height >= bh * 0.99 || r.width <= 0.1 || r.width >= bw * 0.4) continue;
    if (r.width >= r.height * 2 && bh > r.height * 4) continue;
    bars.push(r);
    yRows.add(Math.round(r.top));
  }
  if (seriesColors.size >= 2 && sr.width >= 140 && sr.height >= 80 && !hasCardLegendOrTable(svg, doc, win, box)) {
    pushErr(`[ORPHAN_SERIES_LEGEND${ctxTag}] @${vw}px: multi-series chart (${seriesColors.size} colors) has no visible on-card legend or table`);
  }
  if (bars.length <= 45) return;
  const grounded = bars.filter((r) => Math.abs(r.bottom - box.yb) <= 8).length;
  if (yRows.size >= 4 && grounded * 2 < bars.length && bars.every((r) => r.height <= 16)) return;
  const widths = bars.map((r) => r.width).sort((a, b) => a - b);
  const medW = widths[Math.floor(widths.length / 2)];
  const xCols = new Set(bars.map((r) => Math.round(r.left * 2) / 2));
  if (xCols.size > 45 && ((bw >= 420 && medW < 5.0) || medW < 3.2)) {
    pushErr(`[BAR_HAIRLINE_DENSITY${ctxTag}] @${vw}px: dense bar chart renders ${xCols.size} columns with median width ${medW.toFixed(1)}px (< 5px)`);
  }
}
"""

CDP_DOC_PROBES_JS = r"""
const EMOJI_CHROME_RE = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u;
const UNBOUNDED_UNIT_RE = /\b(?:steps?|tokens?|calls?|events?|runs?|requests?|items?|ops?|msgs?)\b/i;
const UNBOUNDED_MAG_RE = /\d+(?:\.\d+)?\s*(?:k|M|B)\b/;
const BOUND_LABEL_RE = /(?:%|\/|\b(?:ceiling|limit|quota|budget|capacity|threshold|range|target|setpoint|max(?:imum)?)\b)/i;
const WINDOW_BTN_RE = /^(?:\d+\s*[hdwmy]|today|all(?:\s+time)?|mtd|qtd|ytd|last\s+\d+\s*[hdwmy]?|this\s+(?:week|month|quarter|year)|past\s+\d+\s*[hdwmy]?|hourly|daily|weekly|monthly|rolling|cal(?:endar)?)$/i;

function auditDocV922(doc, win, ctxTag) {
  for (const ov of doc.querySelectorAll('.va-side-rail[data-open="true"], .va-side-rail.is-open, dialog[open], [role="dialog"], [aria-modal="true"], .va-preset-popover[data-open="true"], .va-preset-popover:is(:popover-open, .\\:popover-open), .va-popover:is(:popover-open, .\\:popover-open), [role="menu"]')) {
    const cs = win.getComputedStyle(ov);
    if (!isVis(ov, cs) || ov.hasAttribute('hidden')) continue;
    if (ov.getAttribute('role') === 'menu' && !ov.matches('.va-preset-popover, .va-popover') && cs.position !== 'fixed' && cs.position !== 'absolute' && !ov.hasAttribute('popover')) continue;
    const orr = ov.getBoundingClientRect();
    if (orr.width < 24 || orr.height < 24) continue;
    const a = parseAlphaColor(cs.backgroundColor);
    if (a < 0.92) {
      const cls = String(ov.getAttribute('class') || ov.tagName).trim().slice(0, 28);
      pushErr(`[TRANSPARENT_OVERLAY${ctxTag}] @${vw}px: overlay '${cls}' background alpha ${a.toFixed(2)} < 0.92`);
    }
  }

  for (const tb of doc.querySelectorAll('[role="toolbar"], .va-filter-bar')) {
    if (!isVis(tb, win.getComputedStyle(tb))) continue;
    let tCount = 0;
    for (const btn of tb.querySelectorAll('button, [role="button"]')) {
      if (btn.closest('.va-preset-popover, [role="menu"]') || !isVis(btn, win.getComputedStyle(btn))) continue;
      const txt = (btn.textContent || '').replace(/\s+/g, ' ').trim();
      const inWinGrp = !!btn.closest('[data-tb-group="window"], [data-window-group]');
      if (inWinGrp || btn.hasAttribute('data-window') || btn.hasAttribute('data-period') || WINDOW_BTN_RE.test(txt)) tCount += 1;
    }
    if (tCount > 6) {
      pushErr(`[TOOLBAR_CONTROL_SPRAWL${ctxTag}] @${vw}px: toolbar renders ${tCount} (>6) temporal buttons instead of consolidated stepper/popover`);
    }
  }

  for (const card of doc.querySelectorAll('.va-kpi-gauge-card')) {
    if (!isVis(card, win.getComputedStyle(card))) continue;
    const track = card.querySelector('.va-kpi-gauge-track');
    const valEl = card.querySelector('.va-kpi-gauge-val');
    if (!track || !isVis(track, win.getComputedStyle(track)) || !valEl || !isVis(valEl, win.getComputedStyle(valEl))) continue;
    const valTxt = (valEl.textContent || '').trim();
    if (!valTxt || /[%/]/.test(valTxt)) continue;
    const cardTxt = (card.textContent || '').trim();
    if ((UNBOUNDED_UNIT_RE.test(valTxt) || UNBOUNDED_MAG_RE.test(valTxt)) && !BOUND_LABEL_RE.test(cardTxt)) {
      pushErr(`[FAKE_UNBOUNDED_GAUGE${ctxTag}] @${vw}px: .va-kpi-gauge-card '${valTxt.slice(0, 28)}' renders progress track without ceiling/limit/fraction`);
    }
  }

  for (const el of doc.querySelectorAll('header, nav, button, [role="tab"], [role="toolbar"]')) {
    if (el.closest('pre, code')) continue;
    if (!isVis(el, win.getComputedStyle(el))) continue;
    const clone = el.cloneNode(true);
    for (const c of clone.querySelectorAll('pre, code, script, style, svg')) c.remove();
    const txt = (clone.textContent || '').replace(/\s+/g, ' ').trim();
    const em = txt.match(EMOJI_CHROME_RE);
    if (em) {
      pushErr(`[EMOJI_IN_CHROME${ctxTag}] @${vw}px: interactive chrome '${txt.slice(0, 28)}' contains pictographic emoji '${em[0]}'`);
    }
  }

  for (const pane of doc.querySelectorAll('.va-pane-hdr, .va-tab-strip')) {
    const cs = win.getComputedStyle(pane);
    if (!isVis(pane, cs)) continue;
    const ox = cs.overflowX;
    if (ox === 'auto' || ox === 'scroll') continue;
    const paneCls = String(pane.getAttribute('class') || '');
    if ((ox === 'hidden' || ox === 'clip') && pane.scrollWidth > pane.clientWidth + 2) {
      pushErr(`[PANE_CONTROL_CLIPPED${ctxTag}] @${vw}px: pane container '${paneCls}' clips horizontal controls (${pane.scrollWidth} > ${pane.clientWidth})`);
      continue;
    }
    const pr = pane.getBoundingClientRect();
    let clipLeft = pr.left, clipRight = pr.right;
    let anc = pane.parentElement;
    while (anc) {
      const acs = win.getComputedStyle(anc);
      if (acs.overflowX === 'auto' || acs.overflowX === 'scroll') { clipLeft = -Infinity; clipRight = Infinity; break; }
      if (acs.overflowX === 'hidden' || acs.overflowX === 'clip') {
        const ar = anc.getBoundingClientRect();
        clipLeft = Math.max(clipLeft, ar.left);
        clipRight = Math.min(clipRight, ar.right);
      }
      anc = anc.parentElement;
    }
    if (!Number.isFinite(clipRight)) continue;
    for (const child of pane.querySelectorAll('button, a, [role="tab"], input, select, .va-pill, .va-badge, .va-pane-count')) {
      const ccs = win.getComputedStyle(child);
      if (!isVis(child, ccs)) continue;
      let hasScrollAnc = false;
      for (let p = child.parentElement; p && p !== pane; p = p.parentElement) {
        const pox = win.getComputedStyle(p).overflowX;
        if (pox === 'auto' || pox === 'scroll') { hasScrollAnc = true; break; }
      }
      if (hasScrollAnc) continue;
      const cr = child.getBoundingClientRect();
      if (cr.right > clipRight + 1.5 || cr.left < clipLeft - 1.5) {
        const clsStr = String(child.getAttribute('class') || '');
        const label = (child.textContent || child.getAttribute('aria-label') || clsStr).trim().slice(0, 24);
        pushErr(`[PANE_CONTROL_CLIPPED${ctxTag}] @${vw}px: control '${label}' clipped outside non-scrollable container`);
      }
    }
  }
}
"""

_NAVBAR_SNAP_JS = r"""
const tabs = [...document.querySelectorAll('header [role="tab"], .va-topbar [role="tab"], .va-studio-bar [role="tab"]')].filter((t) => {
  const cs = getComputedStyle(t);
  if (cs.display === 'none' || cs.visibility === 'hidden' || t.disabled || t.getAttribute('aria-disabled') === 'true') return false;
  if (t.tagName === 'A' && t.getAttribute('href') && !t.getAttribute('href').startsWith('#')) return false;
  const r = t.getBoundingClientRect();
  return r.width > 1 && r.height > 1;
});
if (tabs.length < 2) return null;
const hdr = tabs[0].closest('header, .va-topbar, .va-studio-bar') || document.querySelector('header');
const brand = hdr ? hdr.querySelector('.va-studio-brand, .va-shell-brand, .va-brand, [class*="brand"]') : null;
const tablist = tabs[0].closest('[role="tablist"]') || tabs[0].parentElement;
const boxLeft = (el) => el ? el.getBoundingClientRect().left : null;
const origIdx = Math.max(0, tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true' || t.classList.contains('is-active')));
return {
  count: tabs.length,
  origIdx: origIdx,
  brandLeft: boxLeft(brand),
  tablistLeft: boxLeft(tablist),
  tabLefts: tabs.map((t) => t.getBoundingClientRect().left),
};
"""

_NAVBAR_CLICK_JS = r"""
const idx = arguments[0];
const tabs = [...document.querySelectorAll('header [role="tab"], .va-topbar [role="tab"], .va-studio-bar [role="tab"]')].filter((t) => {
  const cs = getComputedStyle(t);
  if (cs.display === 'none' || cs.visibility === 'hidden' || t.disabled || t.getAttribute('aria-disabled') === 'true') return false;
  if (t.tagName === 'A' && t.getAttribute('href') && !t.getAttribute('href').startsWith('#')) return false;
  const r = t.getBoundingClientRect();
  return r.width > 1 && r.height > 1;
});
if (!tabs[idx]) return null;
tabs[idx].click();
return true;
"""


def probe_navbar_shift(driver: Any, url: str, theme: str, vw: int) -> list[str]:
    """Click safe header [role=tab] controls and assert brand/tablist anchor left shifts <= 1px."""
    snap = driver.execute_script(_NAVBAR_SNAP_JS)
    if not snap or snap.get("count", 0) < 2:
        return []
    errs: list[str] = []
    orig_idx = int(snap["origIdx"])
    try:
        for i in range(int(snap["count"])):
            if not driver.execute_script(_NAVBAR_CLICK_JS, i):
                continue
            time.sleep(0.06)
            cur = driver.execute_script(_NAVBAR_SNAP_JS)
            if not cur:
                continue
            checks: list[tuple[str, float | None, float | None]] = [
                ("brand", snap.get("brandLeft"), cur.get("brandLeft")),
                ("tablist", snap.get("tablistLeft"), cur.get("tablistLeft")),
            ]
            for ti, (b0, b1) in enumerate(zip(snap.get("tabLefts", ()), cur.get("tabLefts", ()))):
                checks.append((f"tab#{ti}", b0, b1))
            for name, v0, v1 in checks:
                if v0 is not None and v1 is not None and abs(float(v1) - float(v0)) > 1.0:
                    dx = abs(float(v1) - float(v0))
                    errs.append(f"[{url} theme={theme}] [NAVBAR_SHIFT] @{vw}px: header {name} shifted {dx:.1f}px (> 1px) clicking tab#{i}")
                    break
            if errs:
                break
    finally:
        driver.execute_script(_NAVBAR_CLICK_JS, orig_idx)
        time.sleep(0.04)
    return errs
