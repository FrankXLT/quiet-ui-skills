/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI Pillar 2 — Progressive-Enhancement Evidence Runtime (<= 250L, zero deps).
 * Features:
 *   1. Synchronized multi-channel waveform cursor readout ([data-qe-scope="true"])
 *   2. Pedagogical Flow equation-to-visual term highlighting ([data-term])
 *   3. Spec drawer metadata & copy-JSON feedback
 */
(function (window, document) {
  'use strict';

  var termsBound = false;

  function findNearestSample(samples, targetT, maxGap) {
    if (!Array.isArray(samples) || samples.length === 0) return null;
    for (let i = 0; i < samples.length - 1; i++) {
      const a = samples[i];
      const b = samples[i + 1];
      if (!Array.isArray(a) || !Array.isArray(b) || a.length < 2 || b.length < 2) continue;
      const t0 = Number(a[0]);
      const t1 = Number(b[0]);
      if (targetT >= t0 && targetT <= t1) {
        if (Math.abs(targetT - t0) < 1e-6 && a[1] !== null && a[1] !== undefined) return a;
        if (Math.abs(targetT - t1) < 1e-6 && b[1] !== null && b[1] !== undefined) return b;
        if (a[1] === null || a[1] === undefined || b[1] === null || b[1] === undefined) {
          return null;
        }
        if (Number.isFinite(maxGap) && maxGap > 0 && (t1 - t0) > maxGap) {
          return null;
        }
      }
    }
    let best = null;
    let bestDt = Infinity;
    for (let i = 0; i < samples.length; i++) {
      const s = samples[i];
      if (!Array.isArray(s) || s.length < 2) continue;
      const dt = Math.abs(Number(s[0]) - targetT);
      if (dt < bestDt) {
        bestDt = dt;
        best = s;
      }
    }
    return best;
  }

  function renderScopeAtTime(svg, meta, targetT) {
    if (!Number.isFinite(meta.x0) || !Number.isFinite(meta.pw) || meta.pw <= 0) return;
    if (!Number.isFinite(meta.t_min) || !Number.isFinite(meta.t_span) || meta.t_span <= 0) return;
    const t = Math.max(meta.t_min, Math.min(meta.t_min + meta.t_span, targetT));
    const clampedX = meta.x0 + ((t - meta.t_min) / meta.t_span) * meta.pw;
    svg.dataset.qeCursorT = String(t);

    const cursorLine = svg.querySelector('.qe-live-cursor');
    if (cursorLine) {
      cursorLine.setAttribute('x1', clampedX.toFixed(1));
      cursorLine.setAttribute('x2', clampedX.toFixed(1));
      cursorLine.setAttribute('visibility', 'visible');
    }

    const wrap = svg.closest('.qe-waveform-wrap') || svg.closest('.qe-plot-wrap');
    const readout = wrap ? wrap.querySelector('.qe-scope-readout') : null;
    if (!readout) return;

    const gapLim = Number(meta.max_gap);
    const vals = (meta.channels || []).map(function (ch) {
      const cid = String((ch && ch.id) || 'CH').toUpperCase();
      const s = findNearestSample(ch && ch.samples, t, gapLim);
      if (!s || s[1] === null || s[1] === undefined) {
        return cid + ': DROPOUT';
      }
      const vStr = typeof s[1] === 'number' ? Number(s[1]).toFixed(2) : String(s[1]);
      return cid + ': ' + vStr + (ch.unit ? '\u00a0' + ch.unit : '');
    });
    readout.textContent = 't = ' + t.toFixed(2) + '\u00a0' + (meta.t_unit || '') + '  |  ' + vals.join('  |  ');
  }

  function updateScopeCursor(svg, meta, clientX) {
    const rect = svg.getBoundingClientRect();
    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!rect.width || !vb || !vb.width || !meta.pw || meta.pw <= 0) return;
    const svgX = ((clientX - rect.left) / rect.width) * vb.width;
    const clampedX = Math.max(meta.x0, Math.min(meta.x0 + meta.pw, svgX));
    const t = meta.t_min + ((clampedX - meta.x0) / meta.pw) * meta.t_span;
    renderScopeAtTime(svg, meta, t);
  }

  function clearScopeCursor(svg) {
    const cursorLine = svg.querySelector('.qe-live-cursor');
    if (cursorLine) cursorLine.setAttribute('visibility', 'hidden');
    const wrap = svg.closest('.qe-waveform-wrap') || svg.closest('.qe-plot-wrap');
    const readout = wrap ? wrap.querySelector('.qe-scope-readout') : null;
    if (readout) {
      if (readout._qeDefaultNodes && readout._qeDefaultNodes.length) {
        readout.replaceChildren.apply(readout, readout._qeDefaultNodes.map(function (n) { return n.cloneNode(true); }));
      } else if (readout.dataset.default) {
        readout.textContent = readout.dataset.default;
      }
    }
  }

  function initWaveforms() {
    document.querySelectorAll('svg[data-qe-scope="true"]').forEach(function (svg) {
      if (svg.dataset.qeScopeBound === '1') return;
      const wrap = svg.closest('.qe-waveform-wrap') || svg.closest('.qe-plot-wrap');
      const dataEl = wrap ? wrap.querySelector('.qe-scope-data') : null;
      const roEl = wrap ? wrap.querySelector('.qe-scope-readout') : null;
      if (roEl && !roEl._qeDefaultNodes) roEl._qeDefaultNodes = Array.from(roEl.childNodes, function (n) { return n.cloneNode(true); });
      if (!dataEl) return;
      let meta = null;
      try {
        meta = JSON.parse(dataEl.textContent || '{}');
      } catch (_err) {
        return;
      }
      svg.dataset.qeScopeBound = '1';
      svg.addEventListener('pointermove', function (ev) { updateScopeCursor(svg, meta, ev.clientX); });
      svg.addEventListener('pointerdown', function (ev) { updateScopeCursor(svg, meta, ev.clientX); });
      svg.addEventListener('pointerleave', function () { clearScopeCursor(svg); });
      svg.addEventListener('keydown', function (ev) {
        const curT = Number(svg.dataset.qeCursorT || meta.t_min);
        const dt = Number(meta.dt);
        const step = (Number.isFinite(dt) && dt > 0 && ((meta.t_span || 1) / dt) <= 200) ? dt : ((meta.t_span || 1) / 40);
        if (ev.key === 'ArrowRight') { ev.preventDefault(); renderScopeAtTime(svg, meta, curT + step); }
        else if (ev.key === 'ArrowLeft') { ev.preventDefault(); renderScopeAtTime(svg, meta, curT - step); }
        else if (ev.key === 'Home') { ev.preventDefault(); renderScopeAtTime(svg, meta, meta.t_min); }
        else if (ev.key === 'End') { ev.preventDefault(); renderScopeAtTime(svg, meta, meta.t_min + meta.t_span); }
        else if (ev.key === 'Escape') { clearScopeCursor(svg); }
      });
    });
  }

  function setActiveTerm(scopeRoot, termKey) {
    if (!scopeRoot) return;
    scopeRoot.querySelectorAll('[data-term]').forEach(function (el) {
      if (!termKey) {
        el.classList.remove('is-term-active', 'is-term-dimmed');
      } else if (el.getAttribute('data-term') === termKey) {
        el.classList.add('is-term-active');
        el.classList.remove('is-term-dimmed');
      } else {
        el.classList.remove('is-term-active');
        el.classList.add('is-term-dimmed');
      }
    });
  }

  function initPedagogicalTerms() {
    if (termsBound) return;
    termsBound = true;
    const resolveScope = function (ev) {
      const target = ev.target && ev.target.closest ? ev.target.closest('[data-term]') : null;
      if (!target) return null;
      return { target: target, scope: target.closest('.qe-pedagogy-scope') || target.closest('.qe-figure') || document };
    };
    document.addEventListener('pointerover', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, r.target.getAttribute('data-term')); });
    document.addEventListener('pointerout', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, r.scope.dataset.pinnedTerm || null); });
    document.addEventListener('click', function (ev) {
      const btn = ev.target && ev.target.closest ? ev.target.closest('button[data-term], .qe-eq-term[data-term]') : null;
      if (!btn) return;
      const scope = btn.closest('.qe-pedagogy-scope') || btn.closest('.qe-figure') || document;
      const term = btn.getAttribute('data-term');
      const next = (scope.dataset.pinnedTerm === term) ? '' : (term || '');
      if (next) scope.dataset.pinnedTerm = next;
      else delete scope.dataset.pinnedTerm;
      setActiveTerm(scope, next || null);
      scope.querySelectorAll('button[data-term], .qe-eq-term[data-term]').forEach(function (b) {
        b.setAttribute('aria-pressed', (next && b.getAttribute('data-term') === next) ? 'true' : 'false');
      });
    });
    document.addEventListener('focusin', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, r.target.getAttribute('data-term')); });
    document.addEventListener('focusout', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, r.scope.dataset.pinnedTerm || null); });
  }

  function copyWithFallback(txt, btn, defaultLabel, statusEl) {
    const label = defaultLabel || 'Copy JSON Spec';
    const markCopied = function (msg) {
      if (statusEl) {
        statusEl.textContent = msg;
        statusEl.classList.add('is-visible');
        window.setTimeout(function () { statusEl.classList.remove('is-visible'); statusEl.textContent = ''; }, 1800);
      } else {
        btn.textContent = msg;
        window.setTimeout(function () { btn.textContent = label; }, 1400);
      }
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(function () { markCopied('Copied'); }).catch(function () {});
      return;
    }
    const ta = document.createElement('textarea');
    ta.value = txt;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;left:-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { if (document.execCommand('copy')) markCopied('Copied'); } catch (_err) {}
    document.body.removeChild(ta);
  }

  function initSpecDrawers() {
    document.querySelectorAll('.qe-spec-drawer').forEach(function (dlg) {
      if (dlg.querySelector('.qe-copy-spec-btn')) return;
      const pre = dlg.querySelector('pre');
      if (!pre) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'va-pill-btn qe-copy-spec-btn';
      btn.textContent = 'Copy JSON Spec';
      btn.addEventListener('click', function () { copyWithFallback(pre.textContent || '', btn, 'Copy JSON Spec'); });
      pre.parentNode.insertBefore(btn, pre);
    });
  }

  function activateEcoTabFallback(tabBtn) {
    const wrap = tabBtn && tabBtn.closest('.qe-eco-drawer');
    if (!wrap) return;
    const targetId = tabBtn.getAttribute('aria-controls');
    wrap.querySelectorAll('.qe-eco-tab[role="tab"]').forEach(function (t) {
      const on = t === tabBtn;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
    });
    wrap.querySelectorAll('.qe-eco-panel[role="tabpanel"]').forEach(function (p) {
      if (p.id === targetId) p.removeAttribute('hidden');
      else p.setAttribute('hidden', 'until-found');
    });
  }

  function initEcoAndModeFallback() {
    const hideUnusedModebars = function () {
      const hasEcharts = typeof window.echarts !== 'undefined' || (window.parent && window.parent !== window && typeof window.parent.echarts !== 'undefined');
      if (typeof window.QuietEChartsAdapter === 'undefined' && !hasEcharts) {
        document.querySelectorAll('.qe-plot-modebar').forEach(function (bar) { bar.hidden = true; });
      }
    };
    if (typeof queueMicrotask === 'function') queueMicrotask(hideUnusedModebars);
    else window.setTimeout(hideUnusedModebars, 0);
    if (typeof window.QuietEChartsAdapter !== 'undefined' || document.documentElement.dataset.qeEcoFallback === '1') return;
    document.documentElement.dataset.qeEcoFallback = '1';
    document.addEventListener('click', function (ev) {
      if (typeof window.QuietEChartsAdapter !== 'undefined') return;
      const tab = ev.target && ev.target.closest ? ev.target.closest('.qe-eco-tab[role="tab"]') : null;
      if (tab) { activateEcoTabFallback(tab); return; }
      const copyBtn = ev.target && ev.target.closest ? ev.target.closest('.qe-copy-btn') : null;
      if (copyBtn) {
        const drw = copyBtn.closest('.qe-eco-drawer');
        const pre = drw && drw.querySelector('.qe-eco-panel:not([hidden]) pre');
        if (pre) copyWithFallback(pre.textContent || '', copyBtn, copyBtn.textContent, drw.querySelector('.qe-copy-status'));
      }
    });
    document.addEventListener('keydown', function (ev) {
      if (typeof window.QuietEChartsAdapter !== 'undefined') return;
      const tab = ev.target && ev.target.closest ? ev.target.closest('.qe-eco-tab[role="tab"]') : null;
      if (!tab) return;
      const list = tab.closest('[role="tablist"]');
      const tabs = list ? Array.prototype.slice.call(list.querySelectorAll('.qe-eco-tab[role="tab"]')) : [];
      const idx = tabs.indexOf(tab);
      if (idx < 0) return;
      const nxt = ev.key === 'ArrowRight' ? (idx + 1) % tabs.length : (ev.key === 'ArrowLeft' ? (idx - 1 + tabs.length) % tabs.length : (ev.key === 'Home' ? 0 : (ev.key === 'End' ? tabs.length - 1 : -1)));
      if (nxt >= 0) { ev.preventDefault(); activateEcoTabFallback(tabs[nxt]); tabs[nxt].focus(); }
    });
    document.addEventListener('beforematch', function (ev) {
      if (typeof window.QuietEChartsAdapter !== 'undefined') return;
      const panel = ev.target && ev.target.closest ? ev.target.closest('.qe-eco-panel[role="tabpanel"]') : null;
      const tid = panel && panel.getAttribute('aria-labelledby');
      if (tid) activateEcoTabFallback(document.getElementById(tid));
    }, true);
  }

  function boot() {
    initWaveforms();
    initPedagogicalTerms();
    initSpecDrawers();
    initEcoAndModeFallback();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.QuietEvidenceRuntime = { boot: boot, setActiveTerm: setActiveTerm };
})(window, document);


// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  var _measureCtx = null;

  function getMeasureCtx() {
    if (_measureCtx) return _measureCtx;
    if (typeof document !== 'undefined' && document.createElement) {
      var canvas = document.createElement('canvas');
      if (canvas && canvas.getContext) _measureCtx = canvas.getContext('2d');
    }
    return _measureCtx;
  }

  function measureTextPx(text, fontSpec) {
    var s = String(text == null ? '' : text);
    var ctx = getMeasureCtx();
    if (ctx) {
      ctx.font = fontSpec || '11px Inter, system-ui, sans-serif';
      return ctx.measureText(s).width;
    }
    return s.length * 6.8;
  }

  function roundClean(v) {
    return Math.abs(v) < 1e-12 ? 0 : Number(v.toFixed(10));
  }

  function niceStep125(rawStep) {
    if (!Number.isFinite(rawStep) || rawStep <= 0) return 1;
    var exp = Math.floor(Math.log10(rawStep));
    var pow = Math.pow(10, exp);
    var frac = rawStep / pow;
    var mant = 1;
    if (frac > 5) mant = 10;
    else if (frac > 2) mant = 5;
    else if (frac > 1) mant = 2;
    return mant * pow;
  }

  function niceScale125(minVal, maxVal, opts) {
    var cfg = opts || {};
    var targetTicks = Math.max(2, Number(cfg.targetTicks || 5));
    var lo = Number(minVal);
    var hi = Number(maxVal);
    if (!Number.isFinite(lo)) lo = 0;
    if (!Number.isFinite(hi)) hi = lo + 1;
    if (cfg.includeZero) {
      lo = Math.min(lo, 0);
      hi = Math.max(hi, 0);
    }
    if (lo > hi) { var tmp = lo; lo = hi; hi = tmp; }
    if (Math.abs(hi - lo) < 1e-9) {
      var pad = Math.abs(lo) > 1e-6 ? Math.abs(lo) * 0.2 : 1;
      lo = cfg.includeZero && lo >= 0 ? 0 : lo - pad;
      hi = hi + pad;
    }
    var step = niceStep125((hi - lo) / (targetTicks - 1));
    var sMin = roundClean(Math.floor(lo / step + 1e-9) * step);
    if (cfg.clampMin !== undefined && cfg.clampMin !== null && Number.isFinite(Number(cfg.clampMin))) {
      sMin = Math.max(Number(cfg.clampMin), sMin);
    }
    var sMax = roundClean(Math.ceil(hi / step - 1e-9) * step);
    if (sMax <= sMin) sMax = roundClean(sMin + step);
    var ticks = [];
    var guard = 0;
    for (var cur = sMin; cur <= sMax + step * 1e-4 && guard < 24; cur += step, guard += 1) {
      ticks.push(roundClean(cur));
    }
    return { min: sMin, max: sMax, step: roundClean(step), ticks: ticks };
  }

  function formatTick(v, step) {
    if (!Number.isFinite(v)) return '';
    if (Math.abs(v) < 1e-12) return '0';
    var st = Math.abs(Number(step || 1));
    var dec = st >= 1 ? 0 : Math.min(4, Math.max(1, Math.ceil(-Math.log10(st)) + 1));
    return roundClean(v).toLocaleString(undefined, { maximumFractionDigits: dec });
  }

  function firstUnclosedIdx(str) {
    var p = [], b = [];
    for (var i = 0; i < str.length; i += 1) {
      var c = str[i];
      if (c === '(') p.push(i);
      else if (c === ')' && p.length) p.pop();
      else if (c === '[') b.push(i);
      else if (c === ']' && b.length) b.pop();
    }
    var ip = p.length ? p[0] : Infinity;
    var ib = b.length ? b[0] : Infinity;
    var m = Math.min(ip, ib);
    return Number.isFinite(m) ? m : -1;
  }

  function balanceDelimiters(str) {
    var out = String(str || '').replace(/[\s,(\[:/-]+$/, '');
    var guard = 0;
    while (guard < 8) {
      var idx = firstUnclosedIdx(out);
      if (idx === -1) break;
      if (idx > 0) {
        out = out.slice(0, idx).replace(/[\s,(\[:/-]+$/, '');
      } else {
        out = out.slice(1).replace(/^[\s(\[]+/, '');
      }
      guard += 1;
    }
    return out;
  }

  function truncateTokenSafe(str, limit) {
    var cut = Math.max(2, limit - 1);
    var head = balanceDelimiters(str.slice(0, cut).replace(/\s+\S*$/, '') || str.slice(0, cut));
    return (head || str.replace(/[(\[]/g, '').slice(0, cut)) + '\u2026';
  }

  function wrapLabelLines(text, maxChars, maxLines) {
    var raw = String(text == null ? '' : text).trim().replace(/\s+/g, ' ');
    var limit = Math.max(6, Number(maxChars || 18));
    var capLines = Math.max(1, Number(maxLines || 2));
    if (!raw || raw.length <= limit) return raw ? [balanceDelimiters(raw) || raw] : [''];
    var words = raw.split(' ');
    var lines = [];
    var cur = '';
    for (var i = 0; i < words.length; i += 1) {
      var w = words[i];
      if (!cur) {
        cur = w;
      } else if ((cur.length + 1 + w.length) <= limit) {
        cur += ' ' + w;
      } else {
        lines.push(cur);
        if (lines.length >= capLines) {
          cur = '';
          break;
        }
        cur = w;
      }
    }
    if (cur && lines.length < capLines) lines.push(cur);
    if (lines.length === 1 && lines[0].length > limit) {
      return [truncateTokenSafe(lines[0], limit)];
    }
    var consumedWords = lines.join(' ').split(' ').length;
    if (consumedWords < words.length || (lines.length === capLines && lines.join(' ').length < raw.length)) {
      lines[lines.length - 1] = truncateTokenSafe(lines[lines.length - 1], limit);
    }
    for (var li = 0; li < lines.length - 1; li += 1) {
      if (firstUnclosedIdx(lines[li]) !== -1 && firstUnclosedIdx(lines.join(' ')) !== -1) {
        lines[li] = balanceDelimiters(lines[li]) || lines[li].replace(/[(\[]/g, '');
      }
    }
    return lines;
  }

  function measureCategoryGutter(labels, opts) {
    var cfg = opts || {};
    var list = Array.isArray(labels) ? labels : [];
    var minPx = Number(cfg.minPx != null ? cfg.minPx : 64);
    var maxPx = Number(cfg.maxPx != null ? cfg.maxPx : 176);
    var padPx = Number(cfg.padPx != null ? cfg.padPx : 18);
    var maxChars = Number(cfg.maxChars != null ? cfg.maxChars : 22);
    var fontSpec = cfg.font || '11px Inter, system-ui, sans-serif';
    var maxW = 0;
    var wrappedLabels = list.map(function (lbl) {
      var lines = wrapLabelLines(lbl, maxChars, cfg.maxLines || 2);
      lines.forEach(function (ln) {
        maxW = Math.max(maxW, measureTextPx(ln, fontSpec));
      });
      return lines.join('\n');
    });
    var gutterPx = Math.max(minPx, Math.min(maxPx, Math.ceil(maxW + padPx)));
    return { gutterPx: gutterPx, maxLinePx: Math.ceil(maxW), wrappedLabels: wrappedLabels };
  }

  function filterNonOverlappingTicks(ticks, opts) {
    var list = Array.isArray(ticks) ? ticks.slice() : [];
    var cfg = opts || {};
    var axis = cfg.axis === 'y' ? 'y' : 'x';
    var gap = Math.max(2, Number(cfg.minGapPx != null ? cfg.minGapPx : 10));
    var fontSpec = cfg.font || '11px JetBrains Mono, monospace';
    var lineH = Number(cfg.lineHeightPx || 14);
    var keepEnds = !!cfg.keepEnds;
    list.sort(function (a, b) { return Number(a.pos || 0) - Number(b.pos || 0); });
    var kept = [];
    var lastEnd = -Infinity;
    list.forEach(function (tk, idx) {
      var pos = Number(tk.pos || 0);
      var lbl = String(tk.label != null ? tk.label : tk.value);
      var span = axis === 'x' ? Math.max(18, measureTextPx(lbl, fontSpec)) : lineH;
      var lo = pos - span * 0.5;
      var hi = pos + span * 0.5;
      var isLast = idx === list.length - 1;
      if (lo >= lastEnd + gap) {
        kept.push(tk);
        lastEnd = hi;
      } else if (keepEnds && isLast && kept.length > 0) {
        var prev = kept[kept.length - 1];
        var prevSpan = axis === 'x' ? Math.max(18, measureTextPx(String(prev.label != null ? prev.label : prev.value), fontSpec)) : lineH;
        if (kept.length > 1) {
          var beforePrev = kept[kept.length - 2];
          var bSpan = axis === 'x' ? Math.max(18, measureTextPx(String(beforePrev.label != null ? beforePrev.label : beforePrev.value), fontSpec)) : lineH;
          if ((lo - (Number(beforePrev.pos || 0) + bSpan * 0.5)) >= gap && (lo - (Number(prev.pos || 0) + prevSpan * 0.5)) < gap) {
            kept[kept.length - 1] = tk;
            lastEnd = hi;
          }
        }
      }
    });
    return kept;
  }

  function placeReferenceLabel(docOrSvg, opts) {
    var cfg = opts || {};
    var doc = (docOrSvg && docOrSvg.ownerDocument) ? docOrSvg.ownerDocument : (typeof document !== 'undefined' ? document : null);
    var svgNS = 'http://www.w3.org/2000/svg';
    var text = String(cfg.text || '');
    var plotX0 = Number(cfg.plotX0 != null ? cfg.plotX0 : 0);
    var plotX1 = Number(cfg.plotX1 != null ? cfg.plotX1 : 600);
    var plotY0 = Number(cfg.plotY0 != null ? cfg.plotY0 : 0);
    var plotY1 = Number(cfg.plotY1 != null ? cfg.plotY1 : 260);
    var fontSpec = cfg.font || '600 11px JetBrains Mono, monospace';
    var estW = Math.ceil(measureTextPx(text, fontSpec));
    var x = Number(cfg.x != null ? cfg.x : (plotX1 - 8));
    var y = Number(cfg.y != null ? cfg.y : (plotY0 + 14));
    var anchor = cfg.anchor || (x > (plotX0 + plotX1) * 0.6 ? 'end' : (x < (plotX0 + plotX1) * 0.4 ? 'start' : 'middle'));
    var padX = 6;
    if (anchor === 'start') {
      var minS = plotX0 + padX, maxS = Math.max(minS, plotX1 - estW - padX);
      x = Math.max(minS, Math.min(maxS, x));
    } else if (anchor === 'end') {
      var minE = Math.min(plotX1 - padX, plotX0 + estW + padX), maxE = Math.max(minE, plotX1 - padX);
      x = Math.max(minE, Math.min(maxE, x));
    } else {
      var midLo = Math.min(plotX1 - padX, plotX0 + estW * 0.5 + padX), midHi = Math.max(midLo, plotX1 - estW * 0.5 - padX);
      x = Math.max(midLo, Math.min(midHi, x));
    }
    var yLo = plotY0 + 13, yHi = Math.max(yLo, plotY1 - 6);
    y = Math.max(yLo, Math.min(yHi, y));
    var haloColor = cfg.haloColor || 'var(--bg-surface, #FFFFFF)';
    var fillColor = cfg.fill || 'var(--text-secondary, #334155)';
    if (!doc || typeof doc.createElementNS !== 'function') {
      return { x: x, y: y, anchor: anchor, text: text, estWidth: estW };
    }
    var g = doc.createElementNS(svgNS, 'g');
    g.setAttribute('data-role', 'ref-label');
    var rx = anchor === 'start' ? x - 4 : (anchor === 'end' ? x - estW - 4 : x - estW * 0.5 - 4);
    var bg = doc.createElementNS(svgNS, 'rect');
    bg.setAttribute('x', rx.toFixed(1));
    bg.setAttribute('y', (y - 11.5).toFixed(1));
    bg.setAttribute('width', (estW + 8).toFixed(1));
    bg.setAttribute('height', '15');
    bg.setAttribute('rx', '2');
    bg.setAttribute('fill', haloColor);
    bg.setAttribute('fill-opacity', '0.94');
    bg.setAttribute('stroke', 'none');
    g.appendChild(bg);
    var txt = doc.createElementNS(svgNS, 'text');
    txt.setAttribute('x', x.toFixed(1));
    txt.setAttribute('y', y.toFixed(1));
    txt.setAttribute('text-anchor', anchor);
    txt.setAttribute('font-family', cfg.fontFamily || 'var(--font-mono, ui-monospace)');
    txt.setAttribute('font-size', String(cfg.fontSize || 11));
    txt.setAttribute('font-weight', String(cfg.fontWeight || 600));
    txt.setAttribute('fill', fillColor);
    txt.setAttribute('stroke', haloColor);
    txt.setAttribute('stroke-width', '3.2');
    txt.setAttribute('stroke-linejoin', 'round');
    txt.setAttribute('paint-order', 'stroke fill');
    txt.textContent = text;
    g.appendChild(txt);
    if (docOrSvg && docOrSvg.nodeType === 1) docOrSvg.appendChild(g);
    return g;
  }

  var api = {
    niceScale125: niceScale125,
    formatTick: formatTick,
    wrapLabelLines: wrapLabelLines,
    measureCategoryGutter: measureCategoryGutter,
    filterNonOverlappingTicks: filterNonOverlappingTicks,
    placeReferenceLabel: placeReferenceLabel,
  };
  root.QuietSvgLayout = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
