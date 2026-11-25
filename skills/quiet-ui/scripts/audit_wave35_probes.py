# SPDX-License-Identifier: Apache-2.0
"""Wave 3.5 CDP DOM/SVG probes: label clearance, disabled contrast, tablet key wrap, print margins."""

from __future__ import annotations

import time
from typing import Any

CDP_WAVE35_PROBES_JS = r"""
function _w35Color(str) {
  const s = String(str || '').trim().toLowerCase();
  if (!s || s === 'transparent' || s === 'none') return null;
  const pa = (v) => (v == null || v === '') ? 1 : (String(v).endsWith('%') ? parseFloat(v) / 100 : parseFloat(v));
  const mRgb = s.match(/^rgba?\(\s*([0-9.]+)[,\s]+([0-9.]+)[,\s]+([0-9.]+)(?:\s*[,/]\s*([^)\s]+))?/);
  if (mRgb) return { r: +mRgb[1] / 255, g: +mRgb[2] / 255, b: +mRgb[3] / 255, a: pa(mRgb[4]) };
  const mSrgb = s.match(/^color\(\s*srgb\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)(?:\s*\/\s*([^)\s]+))?/);
  if (mSrgb) return { r: +mSrgb[1], g: +mSrgb[2], b: +mSrgb[3], a: pa(mSrgb[4]) };
  const mOk = s.match(/^okl(ab|ch)\(\s*([0-9.]+)(%?)\s+([-0-9.]+)\s+([-0-9.]+)(?:\s*\/\s*([^)\s]+))?/);
  if (mOk) {
    const L = mOk[3] === '%' ? parseFloat(mOk[2]) / 100 : parseFloat(mOk[2]);
    let a = parseFloat(mOk[4]), b = parseFloat(mOk[5]);
    if (mOk[1] === 'ch') { const rad = (b * Math.PI) / 180; const c = a; a = c * Math.cos(rad); b = c * Math.sin(rad); }
    const l_ = Math.pow(L + 0.3963377774 * a + 0.2158037573 * b, 3);
    const m_ = Math.pow(L - 0.1055613458 * a - 0.0638541728 * b, 3);
    const s_ = Math.pow(L - 0.0894841775 * a - 1.2914855480 * b, 3);
    const toS = (v) => (v <= 0.0031308 ? 12.92 * Math.max(0, v) : 1.055 * Math.pow(Math.min(1, v), 1 / 2.4) - 0.055);
    return {
      r: toS(4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_),
      g: toS(-1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_),
      b: toS(-0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_),
      a: pa(mOk[6]),
    };
  }
  return null;
}
function _w35Lum(c) {
  const ch = (v) => { const x = Math.max(0, Math.min(1, v)); return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
  return 0.2126 * ch(c.r) + 0.7152 * ch(c.g) + 0.0722 * ch(c.b);
}
function _w35Blend(top, bot, mul) {
  const a = Math.max(0, Math.min(1, (top.a == null ? 1 : top.a) * mul));
  return { r: top.r * a + bot.r * (1 - a), g: top.g * a + bot.g * (1 - a), b: top.b * a + bot.b * (1 - a), a: 1 };
}
function _w35EffectiveContrast(el, doc, win) {
  const chain = [];
  for (let cur = el; cur && cur.nodeType === 1; cur = cur.parentElement) chain.push(cur);
  let backdrop = { r: 1, g: 1, b: 1, a: 1 };
  const bodyCs = win.getComputedStyle(doc.documentElement);
  const bodyC = _w35Color(bodyCs.backgroundColor);
  if (bodyC && bodyC.a > 0.9) backdrop = bodyC;
  let parentSurf = Object.assign({}, backdrop);
  for (let i = chain.length - 1; i >= 1; i -= 1) {
    const cs = win.getComputedStyle(chain[i]);
    const bg = _w35Color(cs.backgroundColor);
    if (bg && bg.a > 0.01) parentSurf = _w35Blend(bg, parentSurf, parseFloat(cs.opacity || '1'));
  }
  const ecs = win.getComputedStyle(el);
  const eOp = parseFloat(ecs.opacity || '1');
  const eBg = _w35Color(ecs.backgroundColor);
  const surf = (eBg && eBg.a > 0.01) ? _w35Blend(eBg, parentSurf, eOp) : parentSurf;
  const fgRaw = _w35Color(ecs.color) || { r: 0, g: 0, b: 0, a: 1 };
  const fgEff = _w35Blend(fgRaw, parentSurf, eOp);
  const l1 = _w35Lum(fgEff), l2 = _w35Lum(surf);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
function auditDisabledContrastW35(doc, win, ctxTag, vwCur) {
  const theme = (doc.documentElement.getAttribute('data-theme') || 'default').toLowerCase();
  const sel = 'button:disabled, input:disabled, select:disabled, button[aria-disabled="true"], [role="button"][aria-disabled="true"], a[aria-disabled="true"]';
  for (const el of doc.querySelectorAll(sel)) {
    if (el.closest('[hidden], .hidden, dialog:not([open]), details:not([open]), pre, code')) continue;
    const cs = win.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 4 || r.height <= 4) continue;
    const rawTxt = el.tagName === 'SELECT' && el.selectedIndex >= 0 ? (el.options[el.selectedIndex]?.text || el.value || '') : (el.textContent || el.value || '');
    const txt = rawTxt.replace(/\s+/g, ' ').trim();
    if (!txt) continue;
    const ratio = _w35EffectiveContrast(el, doc, win);
    if (ratio < 2.8) {
      pushErr(`[DISABLED_CONTROL_LOW_CONTRAST${ctxTag}] @${vwCur}px theme=${theme}: disabled '${txt.slice(0, 26)}' contrast=${ratio.toFixed(2)}:1 (< 2.8:1)`);
    }
  }
}
function auditParamKeysTabletW35(doc, win, ctxTag, vwCur) {
  if (vwCur < 601 || vwCur > 980) return;
  for (const el of doc.querySelectorAll('table td code, table td[data-param-key]')) {
    if (el.closest('[hidden], .hidden, .va-wrap-prose, thead, dialog:not([open]), details:not([open])')) continue;
    const cs = win.getComputedStyle(el);
    if (!isVis(el, cs)) continue;
    const txt = (el.textContent || '').trim();
    if (!txt || txt.length < 6 || /\s/.test(txt)) continue;
    const rng = doc.createRange();
    rng.selectNodeContents(el);
    const rows = new Set();
    for (const rr of rng.getClientRects()) {
      if (rr.width > 0.5 && rr.height > 2) rows.add(Math.round(rr.top / 4));
    }
    if (rows.size >= 2) {
      pushErr(`[PARAM_KEY_MIDWORD_WRAP${ctxTag}] @${vwCur}px: parameter key '${txt.slice(0, 34)}' wraps mid-word across ${rows.size} lines`);
    }
  }
}
function _w35DistSegRect(x1, y1, x2, y2, r) {
  const inBox = (px, py) => px >= r.left && px <= r.right && py >= r.top && py <= r.bottom;
  if (inBox(x1, y1) || inBox(x2, y2)) return 0;
  const cross = (ax, ay, bx, by, cx, cy, dx, dy) => {
    const den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
    if (Math.abs(den) < 1e-6) return false;
    const t = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den;
    const u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
    return t >= 0 && t <= 1 && u >= 0 && u <= 1;
  };
  if (cross(x1, y1, x2, y2, r.left, r.top, r.right, r.top) || cross(x1, y1, x2, y2, r.right, r.top, r.right, r.bottom) ||
      cross(x1, y1, x2, y2, r.left, r.bottom, r.right, r.bottom) || cross(x1, y1, x2, y2, r.left, r.top, r.left, r.bottom)) return 0;
  const ptSeg = (px, py) => {
    const dx = x2 - x1, dy = y2 - y1, l2 = dx * dx + dy * dy;
    const t = l2 > 0 ? Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / l2)) : 0;
    return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
  };
  const ptRect = (px, py) => Math.hypot(Math.max(r.left - px, 0, px - r.right), Math.max(r.top - py, 0, py - r.bottom));
  let best = Math.min(ptRect(x1, y1), ptRect(x2, y2));
  best = Math.min(best, ptSeg(r.left, r.top), ptSeg(r.right, r.top), ptSeg(r.left, r.bottom), ptSeg(r.right, r.bottom));
  return best;
}
function _w35IsAxisOrGrid(x1, y1, x2, y2, sw, cs, sr) {
  const len = Math.hypot(x2 - x1, y2 - y1);
  if (len < 16) return true;
  const horiz = Math.abs(y2 - y1) <= 1.2, vert = Math.abs(x2 - x1) <= 1.2;
  if (!horiz && !vert) return false;
  const dash = cs.strokeDasharray && cs.strokeDasharray !== 'none';
  if (sw <= 1.35 && !dash) return true;
  if (dash && sw <= 1.35 && ((horiz && len >= sr.width * 0.35) || (vert && len >= sr.height * 0.35))) return true;
  return false;
}
function _w35ExtractSegments(svg, win, sr) {
  const segs = [];
  const pushPoly = (pts, sw, isGrid, node) => { for (let i = 1; i < pts.length; i += 1) segs.push({ a: pts[i - 1], b: pts[i], sw, isGrid, isStraight: false, node }); };
  for (const el of svg.querySelectorAll('line, polyline, path')) {
    if (el.closest('defs, [hidden], .qe-legend-series')) continue;
    const cs = win.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') <= 0.2) continue;
    const stroke = cs.stroke || el.getAttribute('stroke') || '';
    if (!stroke || stroke === 'none' || stroke === 'transparent' || /,\s*0(?:\.0+)?\)$/.test(stroke)) continue;
    const sw = parseFloat(cs.strokeWidth || el.getAttribute('stroke-width') || '1') || 1;
    if (sw < 1.1) continue;
    const fill = cs.fill || el.getAttribute('fill') || 'none';
    const fOp = parseFloat(cs.fillOpacity || el.getAttribute('fill-opacity') || '1');
    const hasFill = fill && fill !== 'none' && fill !== 'transparent' && fOp >= 0.22 && !/,\s*0(?:\.0+)?\)$/.test(fill);
    const ctm = el.getScreenCTM();
    if (!ctm) continue;
    const xform = (x, y) => new DOMPoint(x, y).matrixTransform(ctm);
    const tag = el.tagName.toLowerCase();
    if (tag === 'line') {
      const p1 = xform(parseFloat(el.getAttribute('x1') || '0'), parseFloat(el.getAttribute('y1') || '0'));
      const p2 = xform(parseFloat(el.getAttribute('x2') || '0'), parseFloat(el.getAttribute('y2') || '0'));
      const isG = _w35IsAxisOrGrid(p1.x, p1.y, p2.x, p2.y, sw, cs, sr);
      if (Math.hypot(p2.x - p1.x, p2.y - p1.y) >= 16) segs.push({ a: p1, b: p2, sw, isGrid: isG, isStraight: true, node: el });
    } else if (tag === 'polyline') {
      const nums = (el.getAttribute('points') || '').trim().split(/[\s,]+/).map(Number).filter(Number.isFinite);
      const pts = [];
      for (let i = 0; i + 1 < nums.length; i += 2) pts.push(xform(nums[i], nums[i + 1]));
      if (pts.length >= 2) {
        const isG = pts.length === 2 && _w35IsAxisOrGrid(pts[0].x, pts[0].y, pts[1].x, pts[1].y, sw, cs, sr);
        pushPoly(pts, sw, isG, el);
      }
    } else if (!hasFill && typeof el.getTotalLength === 'function') {
      const len = el.getTotalLength();
      if (!(len > 16)) continue;
      const steps = Math.min(160, Math.max(6, Math.ceil(len / 5)));
      const pts = [];
      for (let k = 0; k <= steps; k += 1) {
        const pt = el.getPointAtLength((len * k) / steps);
        pts.push(xform(pt.x, pt.y));
      }
      const isG = pts.length === 7 && _w35IsAxisOrGrid(pts[0].x, pts[0].y, pts[6].x, pts[6].y, sw, cs, sr);
      pushPoly(pts, sw, isG, el);
    }
  }
  return segs;
}
function _w35InsideOpaqueBox(t, tr, plates) {
  const cx = tr.left + tr.width / 2, cy = tr.top + tr.height / 2;
  return plates.some((pr) => pr.el !== t && cx >= pr.left - 2 && cx <= pr.right + 2 && cy >= pr.top - 2 && cy <= pr.bottom + 2 && pr.width >= tr.width * 0.65 && pr.height >= tr.height * 0.65);
}
function _w35LabelClearancePx(t, tr, s) {
  const hasRot = !!((t.getAttribute('transform') || '').includes('rotate'));
  if (!hasRot || typeof t.getBBox !== 'function') {
    const padTr = { left: tr.left, right: tr.right, top: tr.top + 1.5, bottom: tr.bottom - 1.5 };
    return padTr.bottom > padTr.top ? _w35DistSegRect(s.a.x, s.a.y, s.b.x, s.b.y, padTr) - s.sw * 0.5 : Infinity;
  }
  const tCtm = t.getScreenCTM();
  if (!tCtm) return Infinity;
  const inv = tCtm.inverse();
  const scale = Math.hypot(tCtm.a, tCtm.b) || 1;
  const bb = t.getBBox();
  const box = { left: bb.x, right: bb.x + bb.width, top: bb.y + 1.5 / scale, bottom: bb.y + bb.height - 1.5 / scale };
  if (box.bottom <= box.top) return Infinity;
  const p1 = new DOMPoint(s.a.x, s.a.y).matrixTransform(inv), p2 = new DOMPoint(s.b.x, s.b.y).matrixTransform(inv);
  return _w35DistSegRect(p1.x, p1.y, p2.x, p2.y, box) * scale - s.sw * 0.5;
}
function auditSvgLabelClearanceW35(doc, win, ctxTag, vwCur) {
  if (!(vwCur <= 420 || (vwCur >= 800 && vwCur <= 960) || vwCur >= 1280)) return;
  for (const svg of doc.querySelectorAll('svg')) {
    const scs = win.getComputedStyle(svg);
    if (!isVis(svg, scs) || svg.closest('[hidden], .hidden')) continue;
    const sr = svg.getBoundingClientRect();
    if (sr.width < 120 || sr.height < 60) continue;
    if (svg.matches('.qe-schematic-svg, .va-schematic-svg') || svg.closest('.qe-schematic-wrap')) continue;
    const segs = _w35ExtractSegments(svg, win, sr);
    if (!segs.length) continue;
    const plates = [];
    for (const sh of svg.querySelectorAll('rect, polygon, path')) {
      if (sh.closest('defs, [hidden]')) continue;
      const cs = win.getComputedStyle(sh);
      const fill = cs.fill || sh.getAttribute('fill') || '';
      const fOp = parseFloat(cs.opacity || '1') * parseFloat(cs.fillOpacity || '1');
      if (!fill || fill === 'none' || fill === 'transparent' || fOp < 0.72) continue;
      const pr = sh.getBoundingClientRect();
      if (pr.width >= 18 && pr.height >= 12 && pr.width < sr.width * 0.85) plates.push({ el: sh, left: pr.left, right: pr.right, top: pr.top, bottom: pr.bottom, width: pr.width, height: pr.height });
    }
    for (const t of svg.querySelectorAll('text')) {
      const tcs = win.getComputedStyle(t);
      if (!isVis(t, tcs) || t.closest('[hidden], .qe-legend-series, [data-axis], .tick')) continue;
      const raw = (t.textContent || '').replace(/\s+/g, ' ').trim();
      if (!raw) continue;
      const tr = t.getBoundingClientRect();
      if (tr.width <= 2 || tr.height <= 2 || _w35InsideOpaqueBox(t, tr, plates)) continue;
      const po = (tcs.paintOrder || t.getAttribute('paint-order') || '').toLowerCase();
      const swT = parseFloat(tcs.strokeWidth || t.getAttribute('stroke-width') || '0');
      const hasHalo = (typeof hasTextHalo === 'function') ? hasTextHalo(doc, t, win) : (po.includes('stroke') && swT >= 2.5);
      let minD = Infinity, isCut = false;
      for (const s of segs) {
        if (s.isStraight && hasHalo && s.node && (s.node.compareDocumentPosition(t) & 4)) continue;
        const d = _w35LabelClearancePx(t, tr, s);
        if (s.isGrid) {
          if (d <= 0) { isCut = true; minD = 0; break; }
          continue;
        }
        if (d < minD) minD = d;
        if (minD < 5.2) break;
      }
      if (isCut || minD < 5.2) {
        pushErr(`[SVG_LABEL_STROKE_COLLISION${ctxTag}] @${vwCur}px: SVG label '${raw.slice(0, 26)}' clears plotted stroke by only ${Math.max(0, minD).toFixed(1)}px (< 6px)`);
      }
    }
  }
}
function auditDocWave35(doc, win, ctxTag, opts) {
  const vwCur = (win === window ? vw : win.innerWidth) || win.innerWidth || 1280;
  auditDisabledContrastW35(doc, win, ctxTag, vwCur);
  auditParamKeysTabletW35(doc, win, ctxTag, vwCur);
  auditSvgLabelClearanceW35(doc, win, ctxTag, vwCur);
}
"""

_PRINT_EDGE_JS = r"""
const errs = [];
function _chkPrintMargins(doc, win, tag) {
  const pageW = doc.documentElement.clientWidth || win.innerWidth || 820;
  const bodyMl = doc.body ? parseFloat(win.getComputedStyle(doc.body).marginLeft || '0') : 0;
  const hasQ = !!doc.querySelector('.v9-stage-inner, .va-editorial-article, .va-question-brief, .qe-bench-main, [data-medium]');
  const reqPad = (bodyMl < 4 || hasQ) ? 11.5 : 4.0;
  const walker = doc.createTreeWalker(doc.body || doc.documentElement, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const raw = (n.nodeValue || '').replace(/\s+/g, ' ').trim();
    if (!raw) continue;
    const el = n.parentElement;
    if (!el || el.closest('script,style,noscript,svg,dialog:not([open]),[hidden],.hidden,.sr-only,.qe-caption-sr')) continue;
    let vis = true;
    for (let p = el; p && p.nodeType === 1; p = p.parentElement) {
      const pcs = win.getComputedStyle(p);
      if (p.hasAttribute('hidden') || pcs.display === 'none' || pcs.visibility === 'hidden' || parseFloat(pcs.opacity || '1') === 0) { vis = false; break; }
    }
    if (!vis) continue;
    const rEl = el.getBoundingClientRect();
    if (rEl.width <= 1 || rEl.height <= 1) continue;
    const rng = doc.createRange();
    rng.selectNodeContents(n);
    const rr = rng.getBoundingClientRect();
    if (rr.width <= 1 || rr.height <= 1) continue;
    if (rr.left < reqPad || rr.right > pageW - reqPad) {
      errs.push(`[PRINT_EDGE_CLIP${tag}] print text '${raw.slice(0, 26)}' invades ${Math.ceil(reqPad)}px horizontal margin (left=${rr.left.toFixed(1)}, right=${rr.right.toFixed(1)}/${pageW})`);
      if (errs.length >= 6) return;
    }
  }
  for (const fr of doc.querySelectorAll('iframe')) {
    try {
      const fcs = win.getComputedStyle(fr), frR = fr.getBoundingClientRect();
      if (!fr.closest('[hidden], .hidden') && fr.contentDocument && fr.contentDocument.documentElement && fcs.display !== 'none' && fcs.visibility !== 'hidden' && parseFloat(fcs.opacity || '1') > 0.01 && frR.width > 1 && frR.height > 1) {
        _chkPrintMargins(fr.contentDocument, fr.contentWindow || win, tag + ' iframe#' + (fr.id || 'frame'));
      }
    } catch (_e) {}
  }
}
_chkPrintMargins(document, window, '');
return errs;
"""


def probe_print_safe_margins(driver: Any, url: str, theme: str) -> list[str]:
    """Assert visible print text stays within >= 12px horizontal safe margins on portrait Letter width."""
    errs: list[str] = []
    for msg in driver.execute_script(_PRINT_EDGE_JS) or ():
        errs.append(f"[{url} theme={theme}] {msg}")
    return errs


def probe_wave35_extras(driver: Any, url: str, th: str, payload: dict[str, Any], audit_js: str) -> list[str]:
    """Verify 900x1050 tablet key integrity/SVG clearance plus 4-theme disabled control contrast."""
    errs: list[str] = []
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 900, "height": 1050, "deviceScaleFactor": 1, "mobile": False})
    time.sleep(0.16)
    errs.extend(f"[{url} theme={th}] {e}" for e in (driver.execute_script(audit_js, payload) or ()))
    if th == "white":
        try:
            for extra_th in ("paper", "dark-paper"):
                driver.execute_script(
                    "document.documentElement.setAttribute('data-theme', arguments[0]);"
                    "document.querySelectorAll('iframe').forEach(f=>{try{f.contentDocument?.documentElement?.setAttribute('data-theme', arguments[0]);}catch(e){}});",
                    extra_th,
                )
                time.sleep(0.24)
                js_only_disabled = CDP_WAVE35_PROBES_JS + "\nconst errs=[];function pushErr(m){errs.push(m);}const vw=window.innerWidth;" + r"""
const _visF=(f,w)=>{const cs=w.getComputedStyle(f),r=f.getBoundingClientRect();return !f.closest('[hidden], .hidden')&&cs.display!=='none'&&cs.visibility!=='hidden'&&parseFloat(cs.opacity||'1')>0.01&&r.width>1&&r.height>1;};
const _run=(d,w,t)=>{auditDisabledContrastW35(d,w,t,vw);d.querySelectorAll('iframe').forEach(f=>{try{if(_visF(f,w)&&f.contentDocument)_run(f.contentDocument,f.contentWindow||w,t+' iframe#'+(f.id||'frame'));}catch(_e){}});};
_run(document,window,'');return errs;"""
                errs.extend(f"[{url} theme={extra_th}] {e}" for e in (driver.execute_script(js_only_disabled) or ()))
        finally:
            driver.execute_script(
                "document.documentElement.setAttribute('data-theme', 'white');"
                "document.querySelectorAll('iframe').forEach(f=>{try{f.contentDocument?.documentElement?.setAttribute('data-theme', 'white');}catch(e){}});"
            )
            time.sleep(0.24)
    return errs
