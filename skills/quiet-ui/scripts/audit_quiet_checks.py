# SPDX-License-Identifier: Apache-2.0
"""CDP DOM/SVG audit script and backwards-compatible check exports for Quiet UI."""

from __future__ import annotations

import functools, os, sys, threading, time, urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from audit_cdp_probes import CDP_DOC_PROBES_JS, CDP_SVG_PROBES_JS, CDP_WORKBENCH_PROBES_JS, probe_navbar_shift, probe_workbench_1920  # noqa: E402
try:
    from audit_editorial_print import CDP_EDITORIAL_PRINT_JS, probe_print_flow_collision  # noqa: E402
except ImportError:  # pragma: no cover - partial sandbox copy fallback
    CDP_EDITORIAL_PRINT_JS, probe_print_flow_collision = "", (lambda *_a, **_kw: [])  # type: ignore[assignment]
from audit_ux_and_drift import CDP_UX_DRIFT_JS  # noqa: E402
from audit_static_rules import (  # noqa: E402, F401
    BRAIN_TEXT_RE, COMMENT_RE, EARLY_LAYER_NAMES, OVERFLOW_RULE_RE, SELF_BADGE_RE, SKIP_DIRS,
    VIEWPORTS, WRAPPER_CLASS_HINTS, audit_css_text, audit_js_text, check_hidden_layer_css,
    compute_mount_scopes, extract_layer_order, find_closing_delim, has_demo_branch_mock_array,
    has_responsive_table_stacking, is_asset_in_scope, matches_exclude, parse_mount_prefixes,
    resolve_asset_detail, resolve_asset_path,
)
CDP_AUDIT_JS = "\n".join((CDP_SVG_PROBES_JS, CDP_DOC_PROBES_JS, CDP_UX_DRIFT_JS, CDP_WORKBENCH_PROBES_JS, CDP_EDITORIAL_PRINT_JS)) + "\n" + r"""
const opts = arguments[0] || {};
const allowShowcase = !!opts.allowShowcase;
const errs = [], seen = new Set(), vw = window.innerWidth;
function pushErr(msg) { if (!seen.has(msg)) { seen.add(msg); errs.push(msg); } }
const SELF_BADGE_RE = /(?<![A-Za-z0-9_/-])\b(?:(?:v\d+(?:\.\d+)*|\d+\.\d+(?:\.\d+)*)\s*[·•|-]?\s*Quiet(?:[\s-]+UI)?|Quiet(?:[\s-]+UI)(?:\s+v\d|\s+Pillar|\s+Skills)?|Quiet-Evidence\s+L[1-3]|Pillar\s+[123]\s+M[1-7])\b(?![-_][A-Za-z0-9]|\/)/i;
const BRAIN_RE = /(?:\bbrain:[0-9a-z_-]{6,}\b|\.gemini\/antigravity\/brain\/)/i;
const MATH_INTERVAL_RE = /(?:\[[^\]\[]+,\s*[^()\[]+\)|\([^()\[]+,\s*[^\]\[]+\])/g;

function isVis(el, cs) {
  if (!el || !cs || cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') === 0) return false;
  const r = el.getBoundingClientRect();
  return r.width > 1 && r.height > 1;
}

function unclosedDelim(txt) {
  let p = 0, b = 0;
  for (const ch of String(txt || '').replace(MATH_INTERVAL_RE, '')) {
    if (ch === '(') p += 1; else if (ch === ')' && p > 0) p -= 1;
    else if (ch === '[') b += 1; else if (ch === ']' && b > 0) b -= 1;
  }
  return p > 0 || b > 0;
}
function getRotDeg(el, cs) {
  const tf = (cs && cs.transform && cs.transform !== 'none') ? cs.transform : (el.getAttribute('transform') || '');
  if (!tf) return 0;
  const mRot = tf.match(/rotate\(\s*([-0-9.]+)/i);
  if (mRot) return Math.abs(parseFloat(mRot[1]) || 0);
  const mMat = tf.match(/matrix\(\s*([-0-9.eE]+)\s*,\s*([-0-9.eE]+)/i);
  if (!mMat) return 0;
  const a = parseFloat(mMat[1]), b = parseFloat(mMat[2]);
  return (Number.isFinite(a) && Number.isFinite(b)) ? Math.abs(Math.atan2(b, a) * 180 / Math.PI) : 0;
}
function isTransparentPaint(c) { return !c || c === 'none' || c === 'transparent' || /^rgba\([^)]*,\s*0(?:\.0+)?\s*\)$/.test(c); }
function hasTextHalo(doc, txtEl, win) {
  if (txtEl.classList && txtEl.classList.contains('va-svg-halo-text')) return true;
  if (txtEl.dataset && txtEl.dataset.halo === 'true') return true;
  const cs = win.getComputedStyle(txtEl), po = String(txtEl.getAttribute('paint-order') || cs.paintOrder || '').toLowerCase();
  const st = String(txtEl.getAttribute('stroke') || cs.stroke || 'none').toLowerCase();
  const sw = parseFloat(txtEl.getAttribute('stroke-width') || cs.strokeWidth || '0');
  if (po.includes('stroke') && !isTransparentPaint(st) && sw >= 1.25) return true;
  const prev = txtEl.previousElementSibling;
  if (prev && (prev.tagName || '').toLowerCase() === 'rect' && !isTransparentPaint(String(prev.getAttribute('fill') || win.getComputedStyle(prev).fill || 'none').toLowerCase())) {
    const pr = prev.getBoundingClientRect(), tr = txtEl.getBoundingClientRect();
    if (pr.left <= tr.left + 2 && pr.right >= tr.right - 2 && pr.top <= tr.top + 2 && pr.bottom >= tr.bottom - 2) return true;
  }
  return false;
}

function auditSvg(svg, doc, win, ctxTag) {
  if (svg.getAttribute('aria-hidden') === 'true') return;
  const sr = svg.getBoundingClientRect();
  if (sr.width < 30 || sr.height < 20) return;

  const allNodes = [...svg.querySelectorAll('*')];
  const nodeOrder = new Map();
  allNodes.forEach((el, idx) => nodeOrder.set(el, idx));

  const texts = [];
  for (const t of svg.querySelectorAll('text')) {
    const cs = win.getComputedStyle(t);
    if (!isVis(t, cs)) continue;
    const raw = (t.textContent || '').trim();
    if (!raw) continue;
    const r = t.getBoundingClientRect();
    texts.push({ el: t, txt: raw, r, rot: getRotDeg(t, cs), idx: nodeOrder.get(t) || 0, halo: hasTextHalo(doc, t, win) });
    if (raw.length >= 6 && unclosedDelim(raw)) {
      pushErr(`[LABEL_TRUNCATED${ctxTag}] @${vw}px: SVG text truncated with unclosed delimiter '${raw.slice(0, 36)}'`);
    }
  }

  for (let i = 0; i < texts.length; i += 1) {
    for (let j = i + 1; j < texts.length; j += 1) {
      const a = texts[i], b = texts[j];
      const ovW = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const ovH = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (ovW <= 2.5 || ovH <= 4.5) continue;
      if (a.rot > 8 || b.rot > 8) {
        const dx = (a.r.left + a.r.width / 2) - (b.r.left + b.r.width / 2);
        const dy = (a.r.top + a.r.height / 2) - (b.r.top + b.r.height / 2);
        if (Math.hypot(dx, dy) > Math.min(a.r.width, b.r.width) * 0.65) continue;
      }
      pushErr(`[SVG_TEXT_OVERLAP${ctxTag}] @${vw}px: '${a.txt.slice(0, 24)}' overlaps '${b.txt.slice(0, 24)}' (${ovW.toFixed(1)}x${ovH.toFixed(1)}px)`);
    }
  }

  const plates = [];
  for (const sh of svg.querySelectorAll('rect, path, polygon')) {
    const cs = win.getComputedStyle(sh);
    if (!isVis(sh, cs)) continue;
    const fill = String(sh.getAttribute('fill') || cs.fill || 'none').toLowerCase();
    const fo = parseFloat(sh.getAttribute('fill-opacity') || cs.fillOpacity || '1');
    if (fill === 'none' || fill === 'transparent' || fill === 'rgba(0, 0, 0, 0)' || fo < 0.7) continue;
    plates.push({ r: sh.getBoundingClientRect(), idx: nodeOrder.get(sh) || 0 });
  }

  for (const ln of svg.querySelectorAll('line, path')) {
    const tag = (ln.tagName || '').toLowerCase();
    const cs = win.getComputedStyle(ln);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') < 0.05) continue;
    const stroke = String(ln.getAttribute('stroke') || cs.stroke || 'none').toLowerCase();
    if (!stroke || stroke === 'none' || stroke === 'transparent' || stroke === 'rgba(0, 0, 0, 0)') continue;
    const lr = ln.getBoundingClientRect();
    const isH = lr.width >= 10 && lr.height <= 4;
    const isV = lr.height >= 10 && lr.width <= 4;
    if (tag === 'path' && !isH && !isV) continue;
    if (!isH && !isV) continue;
    const lIdx = nodeOrder.get(ln) || 0;
    const lCy = lr.top + lr.height * 0.5, lCx = lr.left + lr.width * 0.5;
    for (const t of texts) {
      if (t.halo && lIdx < t.idx) continue;
      const tr = t.r;
      const cutH = isH && lr.left < tr.right - 2 && lr.right > tr.left + 2 && lCy > tr.top + 2 && lCy < tr.bottom - 2;
      const cutV = isV && lr.top < tr.bottom - 2 && lr.bottom > tr.top + 2 && lCx > tr.left + 2 && lCx < tr.right - 2;
      if (!cutH && !cutV) continue;
      if (lIdx < t.idx) {
        const covered = plates.some((p) => p.idx > lIdx && p.idx < t.idx && p.r.left <= tr.left + 2 && p.r.right >= tr.right - 2 && p.r.top <= tr.top + 2 && p.r.bottom >= tr.bottom - 2);
        if (covered) continue;
      }
      pushErr(`[SVG_LINE_COLLISION${ctxTag}] @${vw}px: SVG ${isH ? 'horizontal' : 'vertical'} line cuts through '${t.txt.slice(0, 28)}' without halo`);
    }
  }
  auditSvgV922(svg, doc, win, ctxTag, sr, getCartesianPlotBox(svg, win));
}

function getCartesianPlotBox(svg, win) {
  const sr = svg.getBoundingClientRect();
  if (sr.width < 120 || sr.height < 80 || svg.getAttribute('aria-hidden') === 'true') return null;
  if (svg.closest('.qe-schematic-wrap, .qe-bitfield-wrap, .qe-heatmap-wrap, [data-axis-align="independent"]')) return null;
  if (svg.matches('.qe-schematic-svg, .qe-bitfield-svg, .qe-gauge-svg, .qe-spark-svg, .qe-sparkline-svg, .va-schematic-svg, .qe-sankey-svg, .qe-heatmap-svg')) return null;
  const al = (svg.getAttribute('aria-label') || '').toLowerCase();
  if (/\b(heatmap|heat map|sankey|schematic|topology|register|bitfield|fsm|state machine|schedule|gantt|sequence|lineage|pipeline dag|interlock)\b/.test(al)) return null;
  const wrap = svg.closest('.qe-plot-wrap[data-quiet-echarts]');
  if (wrap && wrap.dataset.quietEcharts) {
    try {
      const m = JSON.parse(wrap.dataset.quietEcharts);
      if (m && (m.axisAlign === 'independent' || /^(sankey|heatmap|gantt|gauge|radar|pie|treemap)$/i.test(String(m.kind || '')))) return null;
    } catch (_e) {}
  }
  const fr = svg.querySelector('.qe-plot-frame, [data-role="frame"]');
  if (fr && isVis(fr, win.getComputedStyle(fr))) {
    const r = fr.getBoundingClientRect();
    if (r.width >= 50 && r.height >= 35) return { xl: r.left, xr: r.right, yt: r.top, yb: r.bottom };
  }
  for (const rc of svg.querySelectorAll('rect')) {
    const rcs = win.getComputedStyle(rc);
    if (!isVis(rc, rcs)) continue;
    const fill = String(rc.getAttribute('fill') || rcs.fill || 'none').toLowerCase();
    const st = String(rc.getAttribute('stroke') || rcs.stroke || 'none').toLowerCase();
    if (!isTransparentPaint(fill) || isTransparentPaint(st)) continue;
    const rr = rc.getBoundingClientRect();
    if (rr.width >= sr.width * 0.35 && rr.width < sr.width * 0.985 && rr.height >= sr.height * 0.25 && rr.height < sr.height * 0.985) {
      return { xl: rr.left, xr: rr.right, yt: rr.top, yb: rr.bottom };
    }
  }
  const hMap = new Map(), vLines = [], orthoPaths = [];
  for (const el of svg.querySelectorAll('line, path')) {
    const cs = win.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') < 0.05) continue;
    const st = String(el.getAttribute('stroke') || cs.stroke || 'none').toLowerCase();
    if (isTransparentPaint(st)) continue;
    const fill = String(el.getAttribute('fill') || cs.fill || 'none').toLowerCase();
    const lr = el.getBoundingClientRect();
    if (el.tagName.toLowerCase() === 'path' && !isTransparentPaint(fill) && lr.height > 3.5 && lr.width > 3.5) continue;
    if (lr.height <= 3.5 && lr.width >= sr.width * 0.25 && lr.width < sr.width * 0.985) {
      const key = `${Math.round(lr.left / 2) * 2}:${Math.round(lr.right / 2) * 2}`;
      if (!hMap.has(key)) hMap.set(key, { n: 0, xl: lr.left, xr: lr.right, yt: lr.top, yb: lr.bottom, w: lr.width });
      const b = hMap.get(key); b.n += 1; b.yt = Math.min(b.yt, lr.top); b.yb = Math.max(b.yb, lr.bottom);
    } else if (lr.width <= 3.5 && lr.height >= sr.height * 0.25 && lr.height < sr.height * 0.985) {
      vLines.push(lr);
    } else if (el.tagName.toLowerCase() === 'path' && lr.width >= sr.width * 0.25 && lr.width < sr.width * 0.985 && lr.height >= sr.height * 0.25 && lr.height < sr.height * 0.985) {
      const d = (el.getAttribute('d') || '').trim();
      if (!/[CcSsQqTtAa]/.test(d)) orthoPaths.push(lr);
    }
  }
  let best = null;
  for (const b of hMap.values()) {
    const sc = b.n * 100 + (b.yb - b.yt) + b.w * 0.1;
    if (!best || sc > best.sc) best = { ...b, sc };
  }
  if (!best && orthoPaths.length) best = { xl: orthoPaths[0].left, xr: orthoPaths[0].right, yt: orthoPaths[0].top, yb: orthoPaths[0].bottom };
  if (!best) return null;
  let yt = best.yt, yb = best.yb;
  for (const vl of vLines) {
    if (Math.abs(vl.left - best.xl) <= 10 || Math.abs(vl.right - best.xr) <= 10 || Math.abs(vl.bottom - yb) <= 6) {
      yt = Math.min(yt, vl.top); yb = Math.max(yb, vl.bottom);
    }
  }
  if (svg.querySelectorAll('text').length < 2 && !fr && !wrap) return null;
  return (best.xr - best.xl >= 40 && yb - yt >= 25) ? { xl: best.xl, xr: best.xr, yt, yb } : null;
}

function auditDoc(doc, maxW, ctxTag) {
  if (!doc || !doc.documentElement) return;
  const win = doc.defaultView || window;
  if (doc.documentElement.scrollWidth > maxW + 2) {
    pushErr(`[OVERFLOW${ctxTag}] @${vw}px: scrollWidth=${doc.documentElement.scrollWidth} > width=${maxW}`);
  }
  for (const tbl of doc.querySelectorAll('table')) {
    if (tbl.closest('[hidden]')) continue;
    const tr = tbl.getBoundingClientRect();
    if (tr.width <= 0 || tr.height <= 0) continue;
    if (tr.right > maxW + 2) {
      let scroller = null, p = tbl.parentElement;
      while (p) {
        const ox = win.getComputedStyle(p).overflowX;
        if ((ox === 'auto' || ox === 'scroll') && p.getBoundingClientRect().right <= maxW + 2) { scroller = p; break; }
        p = p.parentElement;
      }
      if (!scroller) pushErr(`[TABLE_CLIP${ctxTag}] @${vw}px: table right=${tr.right.toFixed(1)}px > ${maxW}px without scroll container`);
    }
  }
  for (const el of doc.querySelectorAll('.va-pill, .v9-pill, .va-nav-link, nav a, [class*="nav"] a, [class*="pill"], [class*="badge"], button, .va-tb-btn, .va-tb-group')) {
    const cs = win.getComputedStyle(el);
    if (!isVis(el, cs) || el.closest('pre, code')) continue;
    const raw = (el.textContent || '').trim();
    if (!raw) continue;
    if (el.clientWidth > 12 && (cs.textOverflow === 'ellipsis' || cs.overflowX === 'hidden') && el.scrollWidth > el.clientWidth + 2) {
      pushErr(`[LABEL_TRUNCATED${ctxTag}] @${vw}px: clipped control '${raw.slice(0, 32)}' (scroll=${el.scrollWidth} > client=${el.clientWidth})`);
    } else if (!el.classList.contains('va-tb-group') && raw.length >= 6 && unclosedDelim(raw)) {
      pushErr(`[LABEL_TRUNCATED${ctxTag}] @${vw}px: control has unclosed delimiter '${raw.slice(0, 32)}'`);
    }
  }
  if (!allowShowcase) {
    const explicitChrome = '.va-shell-topbar, .va-shell-brand, .va-topbar, .v9-topbar, .va-brand, .v9-brand, .topbar, [role="banner"], [role="navigation"]';
    for (const hdr of doc.querySelectorAll('header, footer, nav, ' + explicitChrome)) {
      if (hdr.closest('main') && !hdr.matches(explicitChrome)) continue;
      const cs = win.getComputedStyle(hdr);
      if (!isVis(hdr, cs)) continue;
      const t = (hdr.textContent || '').trim();
      const m = t.match(SELF_BADGE_RE);
      if (m) pushErr(`[SELF_BADGE${ctxTag}] @${vw}px: application chrome contains framework self-badge '${m[0]}'`);
    }
    const bands = [];
    for (const el of (doc.body ? doc.body.querySelectorAll('*') : [])) {
      if (/^(SCRIPT|STYLE|NOSCRIPT|SVG)$/.test(el.tagName)) continue;
      if (el.closest('dialog, [role="dialog"], [aria-modal="true"]')) continue;
      const cs = win.getComputedStyle(el);
      if ((cs.position !== 'sticky' && cs.position !== 'fixed') || !isVis(el, cs)) continue;
      const r = el.getBoundingClientRect();
      if (r.height >= win.innerHeight * 0.75 && !el.matches('header, nav, [role="banner"], [role="navigation"]')) continue;
      if (r.width >= maxW * 0.5 && r.height > 4 && r.top >= -4 && r.top < 120 && r.bottom > 0) {
        bands.push([Math.max(0, r.top), Math.min(win.innerHeight, r.bottom)]);
      }
    }
    bands.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const merged = [];
    for (const [s, e] of bands) {
      if (!merged.length || s > merged[merged.length - 1][1]) merged.push([s, e]);
      else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], e);
    }
    const stickyH = merged.reduce((acc, [s, e]) => acc + (e - s), 0);
    const maxSticky = maxW < 680 ? 88 : 64;
    if (stickyH > maxSticky) {
      pushErr(`[STICKY_CHROME_BLOAT${ctxTag}] @${vw}px: top sticky/fixed header chrome height=${stickyH.toFixed(1)}px > ${maxSticky}px`);
    }
    const radPx = (v, h) => { const n = parseFloat(v || '0'); return String(v || '').endsWith('%') ? (n / 100) * h : n; };
    const isPill = (el) => {
      if (!el || /^(IMG|SVG|CANVAS|VIDEO)$/.test(el.tagName) || (el.tagName === 'INPUT' && /^(checkbox|radio)$/i.test(el.type || '')) || el.closest('svg, pre')) return false;
      const cs = win.getComputedStyle(el), r = el.getBoundingClientRect(), pw = el.parentElement ? el.parentElement.getBoundingClientRect().width : vw;
      if (!isVis(el, cs) || r.height < 16 || r.height > 48 || !(pw > 0 && r.width < pw * 0.65)) return false;
      if (radPx(cs.borderTopLeftRadius, r.height) < r.height * 0.42 || radPx(cs.borderBottomRightRadius, r.height) < r.height * 0.42) return false;
      return !isTransparentPaint(cs.backgroundColor) || ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width'] || '0') > 0 && !isTransparentPaint(cs['border' + s + 'Color']));
    };
    const hdrSel = 'header, [role="banner"], .va-shell-topbar, .va-topbar, .v9-topbar, .topbar, [class*="topbar"], .va-pane-hdr, .va-figure-hdr, .qe-card-head, [class*="card-head"], [class*="card-hdr"], [class*="panel-head"], [class*="panel-hdr"], [class*="section-head"], [class*="section-hdr"]';
    const auditedHdrs = new Set();
    for (const hdr of doc.querySelectorAll(hdrSel)) {
      if (!isVis(hdr, win.getComputedStyle(hdr)) || hdr.getBoundingClientRect().height > 220) continue;
      auditedHdrs.add(hdr);
      const pills = [...hdr.querySelectorAll('*')].filter((el) => isPill(el));
      if (pills.filter((el) => !pills.some((p) => p !== el && p.contains(el))).length > 2) pushErr(`[PILL_SPRAWL${ctxTag}] @${vw}px: header/topbar contains >2 visible stadium pills`);
    }
    const cardSel = 'main, section, article, .va-card, .card, .va-panel-tonal, .va-figure-card, .va-pane';
    const rawBody = [];
    for (const el of (doc.body ? doc.body.querySelectorAll('*') : [])) {
      const hAnc = el.closest(hdrSel);
      if (el.matches('button, a, [role="button"], [role="tab"]') || el.closest('button, a, [role="button"], [role="tab"]') || (hAnc && auditedHdrs.has(hAnc)) || !isPill(el)) continue;
      rawBody.push(el);
    }
    const bodyPills = new Map();
    for (const el of rawBody.filter((el) => !rawBody.some((p) => p !== el && p.contains(el)))) {
      const box = el.closest(cardSel) || doc.body;
      bodyPills.set(box, (bodyPills.get(box) || 0) + 1);
    }
    for (const cnt of bodyPills.values()) { if (cnt >= 6) pushErr(`[PILL_SPRAWL${ctxTag}] @${vw}px: card/section body has ${cnt} (>=6) non-interactive stadium pills`); }
    const hasRectTb = [...doc.querySelectorAll('.va-toolbar-joined button, .va-tb-btn, [role="toolbar"] button, [class*="toolbar"] button, .va-btn-primary, .va-btn-ghost, .va-pill-btn, button, [role="button"]')].some((b) => {
      if (b.closest('[role="tablist"]')) return false;
      const cs = win.getComputedStyle(b), r = b.getBoundingClientRect();
      if (!isVis(b, cs) || r.height < 16 || r.height > 48) return false;
      const hasInk = !isTransparentPaint(cs.backgroundColor) || ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width'] || '0') > 0 && !isTransparentPaint(cs['border' + s + 'Color']));
      return hasInk && radPx(cs.borderTopLeftRadius, r.height) <= 8 && radPx(cs.borderBottomRightRadius, r.height) <= 8;
    });
    if (hasRectTb) {
      for (const tl of doc.querySelectorAll('[role="tablist"]')) {
        if (isVis(tl, win.getComputedStyle(tl)) && [...tl.querySelectorAll('[role="tab"], button, a')].some((t) => isPill(t))) {
          pushErr(`[PILL_SPRAWL${ctxTag}] @${vw}px: [role="tablist"] uses stadium pill tabs alongside rectangular toolbar buttons`);
        }
      }
    }
  }
  const plots = [];
  for (const svg of doc.querySelectorAll('svg')) {
    auditSvg(svg, doc, win, ctxTag);
    const cs = win.getComputedStyle(svg);
    if (!isVis(svg, cs) || svg.closest('[hidden]')) continue;
    const box = getCartesianPlotBox(svg, win);
    if (box) plots.push({ svg, sr: svg.getBoundingClientRect(), box, alignRoot: svg.closest('.va-plot-row, .va-plot-grid, [data-plot-align]'), flow: svg.closest('main, section') || doc.body });
  }
  for (let i = 0; i < plots.length; i += 1) {
    for (let j = i + 1; j < plots.length; j += 1) {
      const a = plots[i], b = plots[j];
      if (a.alignRoot || b.alignRoot) { if (a.alignRoot !== b.alignRoot) continue; }
      else if (allowShowcase) continue;
      if (Math.abs(a.sr.left - b.sr.left) <= 24 && Math.abs(a.sr.right - b.sr.right) <= 24) {
        const dxL = Math.abs(a.box.xl - b.box.xl), dxR = Math.abs(a.box.xr - b.box.xr);
        if (dxL > 2.0 || dxR > 2.0) pushErr(`[PLOT_AXIS_MISALIGN${ctxTag}] @${vw}px: column plots differ dxLeft=${dxL.toFixed(1)}px dxRight=${dxR.toFixed(1)}px (> 2px)`);
      }
      const ovY = Math.min(a.sr.bottom, b.sr.bottom) - Math.max(a.sr.top, b.sr.top);
      const ovX = Math.min(a.sr.right, b.sr.right) - Math.max(a.sr.left, b.sr.left);
      if (ovY > Math.min(a.sr.height, b.sr.height) * 0.35 && ovX < 16) {
        const dyT = Math.abs(a.box.yt - b.box.yt), dyB = Math.abs(a.box.yb - b.box.yb);
        if (dyT > 2.0 || dyB > 2.0) pushErr(`[PLOT_AXIS_MISALIGN${ctxTag}] @${vw}px: row plots differ dyTop=${dyT.toFixed(1)}px dyBottom=${dyB.toFixed(1)}px (> 2px)`);
      }
    }
  }
  const walker = doc.createTreeWalker(doc.body || doc.documentElement, NodeFilter.SHOW_TEXT);
  let n, fontChecked = false;
  while ((n = walker.nextNode())) {
    const raw = n.nodeValue ? n.nodeValue.trim() : '';
    if (!raw) continue;
    const el = n.parentElement;
    if (!el || el.closest('script,style,noscript,svg,sub,sup')) continue;
    const cs = win.getComputedStyle(el), r = el.getBoundingClientRect();
    if (cs.display === 'none' || cs.visibility === 'hidden' || r.width <= 2 || r.height <= 2) continue;
    const bm = raw.match(BRAIN_RE);
    if (bm && !el.closest('pre, code')) pushErr(`[INTERNAL_ID${ctxTag}] @${vw}px: raw internal identifier '${bm[0]}' visible in DOM`);
    if (!fontChecked) {
      const fs = parseFloat(cs.fontSize || '16');
      if (fs < 10.8) { pushErr(`[FONT_FLOOR_CDP${ctxTag}] @${vw}px: '${raw.slice(0, 24)}' computed fontSize=${fs.toFixed(1)}px < 11px`); fontChecked = true; }
    }
  }
  auditDocV922(doc, win, ctxTag);
  if (typeof auditDocV940 === 'function') auditDocV940(doc, win, ctxTag, opts); if (typeof auditDocV940Workbench === 'function') auditDocV940Workbench(doc, win, ctxTag, opts); if (typeof auditDocEditorial === 'function') auditDocEditorial(doc, win, ctxTag, opts);
  for (const fr of doc.querySelectorAll('iframe')) {
    try {
      const fdoc = fr.contentDocument;
      if (fdoc && fdoc.documentElement) {
        const fw = Math.round(fr.clientWidth || maxW);
        auditDoc(fdoc, fw > 0 ? fw : maxW, ctxTag + ' iframe#' + (fr.id || 'frame'));
      }
    } catch (_err) {}
  }
}
auditDoc(document, vw, '');
return errs;
"""

class _SafeHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)
    def translate_path(self, path: str) -> str:
        out, root = Path(super().translate_path(path)).resolve(), Path(self.directory).resolve()
        return str(out) if out.is_relative_to(root) else str(root / "__forbidden__")
    def log_message(self, format: str, *args: Any) -> None:
        return

def audit_cdp_urls(urls: list[str], *, allow_showcase_chrome: bool = False, context: dict[str, Any] | None = None) -> list[str]:
    """Audit URLs in Headless Chrome across 390, 820, and 1440 viewports plus @media print."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    opts = Options()
    if os.environ.get("CHROME_BIN"):
        opts.binary_location = os.environ["CHROME_BIN"]
    for arg in ("--headless=new", "--ozone-platform=headless", "--disable-gpu", "--disable-vulkan", "--use-gl=angle", "--use-angle=swiftshader-webgl", "--no-sandbox", "--disable-dev-shm-usage"):
        opts.add_argument(arg)
    payload = {"allowShowcase": allow_showcase_chrome, "blocklistSelectors": list((context or {}).get("blocklist_selectors") or ()), "blocklistCopy": list((context or {}).get("blocklist_copy") or ())}
    errs: list[str] = []
    driver_bin = os.environ.get("CHROMEDRIVER_BIN")
    driver = webdriver.Chrome(service=Service(executable_path=driver_bin), options=opts) if driver_bin else webdriver.Chrome(options=opts)
    try:
        for url in urls:
            driver.get(url)
            time.sleep(0.28)
            uses_theme = bool(driver.execute_script("return document.documentElement.hasAttribute('data-theme') || !!document.querySelector('[data-theme]');"))
            for th in (("white", "dark") if uses_theme else ("default",)):
                if th != "default":
                    driver.execute_script("document.documentElement.setAttribute('data-theme', arguments[0]);", th)
                for w, h in VIEWPORTS:
                    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": w < 600})
                    time.sleep(0.12)
                    errs.extend(f"[{url} theme={th}] {e}" for e in driver.execute_script(CDP_AUDIT_JS, payload))
                    errs.extend(probe_navbar_shift(driver, url, th, w))
                errs.extend(probe_workbench_1920(driver, url, th, payload, CDP_AUDIT_JS))
                if th in ("white", "default"):
                    errs.extend(probe_print_flow_collision(driver, url, th))
    finally:
        driver.quit()
    return errs


def run_cdp_target(target: str, html_files: list[Path], *, allow_showcase_chrome: bool = False, context: dict[str, Any] | None = None) -> list[str]:
    """Serve local HTML target directory if needed and execute audit_cdp_urls."""
    if target.startswith(("http://", "https://")):
        return audit_cdp_urls([target], allow_showcase_chrome=allow_showcase_chrome, context=context)
    if not html_files:
        return []
    root = Path(target).resolve()
    serve_dir = root.parent if root.is_file() else root
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_SafeHTTPHandler, directory=str(serve_dir)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        urls = [f"{base}/{urllib.parse.quote(f.relative_to(serve_dir).as_posix(), safe='/')}" for f in html_files]
        return audit_cdp_urls(urls, allow_showcase_chrome=allow_showcase_chrome, context=context)
    finally:
        srv.shutdown()
        srv.server_close()
