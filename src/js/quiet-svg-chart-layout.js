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
