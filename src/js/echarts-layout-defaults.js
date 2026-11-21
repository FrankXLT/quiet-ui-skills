// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  function ensureGridContainLabel(opt) {
    if (!opt) return opt;
    if (Array.isArray(opt.grid)) opt.grid = opt.grid.map(function (g) { return Object.assign({ containLabel: true }, g || {}); });
    else if (opt.grid && typeof opt.grid === 'object') opt.grid = Object.assign({ containLabel: true }, opt.grid);
    return opt;
  }

  function applyNiceLinearAxisBounds(opt, payload) {
    if (!opt || !payload || !root.QuietSvgLayout) return opt;
    if (payload.y && (payload.y.log || payload.y.logMapped)) return opt;
    var yAxes = Array.isArray(opt.yAxis) ? opt.yAxis : (opt.yAxis ? [opt.yAxis] : []);
    if (yAxes[0] && yAxes[0].type === 'value' && yAxes[0].max === undefined) {
      var vals = [];
      (payload.series || []).forEach(function (sr) {
        (sr.data || []).forEach(function (pt) {
          var raw = Array.isArray(pt) ? pt[1] : (pt && typeof pt === 'object' ? pt.value : pt);
          if (raw === null || raw === undefined || raw === '' || typeof raw === 'boolean') return;
          var v = Number(raw);
          if (Number.isFinite(v)) vals.push(v);
        });
      });
      (payload.envelopes || []).forEach(function (env) {
        if (typeof env.value === 'number' && Number.isFinite(env.value)) vals.push(env.value);
      });
      if (vals.length) {
        var rawMin = Math.min.apply(null, vals), rawMax = Math.max.apply(null, vals);
        var lo = yAxes[0].min !== undefined ? Number(yAxes[0].min) : rawMin, span = rawMax - rawMin;
        var hi = rawMax + (span > 0 ? span * 0.06 : (Math.abs(rawMax) * 0.06 || 1));
        var sc = root.QuietSvgLayout.niceScale125(lo, hi, { targetTicks: 5, includeZero: lo >= 0 });
        if (yAxes[0].min === undefined) yAxes[0].min = sc.min;
        yAxes[0].max = sc.max;
        if (yAxes[0].interval === undefined) yAxes[0].interval = sc.step;
      }
    }
    return opt;
  }

  function applySafeMarkLines(opt, tokens) {
    if (!opt || !Array.isArray(opt.series)) return opt;
    var haloBg = (tokens && tokens.bgSurface) ? tokens.bgSurface : '#FFFFFF';
    opt.series.forEach(function (sr) {
      if (!sr || !sr.markLine || !Array.isArray(sr.markLine.data)) return;
      var parentLbl = sr.markLine.label || {};
      sr.markLine.data = sr.markLine.data.map(function (entry) {
        if (!entry || typeof entry !== 'object') return entry;
        if (entry.xAxis !== undefined || (parentLbl.position && !(entry.label && entry.label.position))) return entry;
        var lbl = Object.assign({}, entry.label || {});
        var rawTxt = String(lbl.formatter || entry.name || '').toLowerCase();
        if (!lbl.position) lbl.position = rawTxt.indexOf('floor') >= 0 ? 'insideStartBottom' : 'insideEndTop';
        if (lbl.distance === undefined) lbl.distance = 4;
        if (!lbl.fontSize || lbl.fontSize < 11) lbl.fontSize = 11;
        if (!lbl.backgroundColor) lbl.backgroundColor = haloBg;
        if (!lbl.padding) lbl.padding = [2, 5];
        if (!lbl.borderRadius) lbl.borderRadius = 2;
        return Object.assign({}, entry, { label: lbl });
      });
    });
    return opt;
  }

  function applySafeLegendLayout(opt, containerWidth) {
    if (!opt || !opt.legend) return opt;
    var yAxes = Array.isArray(opt.yAxis) ? opt.yAxis : (opt.yAxis ? [opt.yAxis] : []);
    var baseGridIdx = (yAxes[0] && yAxes[0].gridIndex) || 0;
    var hasRightYAxis = yAxes.length > 1 && yAxes.some(function (ax, idx) {
      if (!ax) return false;
      if (ax.position === 'right') return true;
      return idx > 0 && (ax.gridIndex === undefined || ax.gridIndex === baseGridIdx);
    });
    var w = Number(containerWidth || 0);
    var isNarrow = w > 0 && w < 640;
    var legends = Array.isArray(opt.legend) ? opt.legend : [opt.legend];
    var needBottomPad = false;
    var maxItems = 0;

    legends.forEach(function (lg) {
      if (!lg || typeof lg !== 'object' || lg.show === false) return;
      var nItems = Array.isArray(lg.data) ? lg.data.length : (Array.isArray(opt.series) ? opt.series.length : 0);
      maxItems = Math.max(maxItems, nItems);
      var isScroll = lg.type === 'scroll';
      var optInScroll = !!(lg.quietAllowScroll || lg.allowScroll);

      if (isScroll && (isNarrow || !optInScroll)) {
        lg.type = 'plain';
        if (lg.orient === 'vertical') lg.orient = 'horizontal';
        delete lg.top;
        lg.bottom = 0;
        lg.left = 'center';
        delete lg.right;
        if (lg.itemGap == null) lg.itemGap = 10;
        needBottomPad = true;
      } else if (hasRightYAxis && lg.bottom == null) {
        if (lg.orient === 'vertical') lg.orient = 'horizontal';
        delete lg.top;
        lg.bottom = 0;
        if (lg.left == null || lg.left === 'right' || typeof lg.left === 'number') {
          lg.left = 'center';
          delete lg.right;
        }
        needBottomPad = true;
      } else if (hasRightYAxis && lg.bottom != null) {
        needBottomPad = true;
      }
    });

    if (needBottomPad) {
      var minBot = (isNarrow && maxItems >= 3) ? 46 : 38;
      if (Array.isArray(opt.grid) && opt.grid.length) {
        var gi = opt.grid.length - 1;
        if (opt.grid[gi] && typeof opt.grid[gi] === 'object') opt.grid[gi] = Object.assign({ containLabel: true }, opt.grid[gi], { bottom: Math.max(Number(opt.grid[gi].bottom) || 0, minBot) });
      } else if (opt.grid && typeof opt.grid === 'object') {
        opt.grid = Object.assign({ containLabel: true }, opt.grid, { bottom: Math.max(Number(opt.grid.bottom) || 0, minBot) });
      } else opt.grid = { containLabel: true, bottom: minBot };
    }
    return opt;
  }

  function normalizeOption(opt, payload, tokens, containerWidth) {
    if (!opt) return opt;
    ensureGridContainLabel(opt);
    applySafeMarkLines(opt, tokens);
    applySafeLegendLayout(opt, containerWidth);
    if (payload && (payload.kind === 'cartesian' || !payload.kind)) applyNiceLinearAxisBounds(opt, payload);
    return opt;
  }

  function getSvgLayout() {
    if (root.QuietSvgLayout) return root.QuietSvgLayout;
    if (typeof require === 'function') { try { return require('./quiet-svg-chart-layout.js'); } catch (_err) {} }
    return null;
  }

  function toMatrix(matrixOrList, opts) {
    if (!Array.isArray(matrixOrList) || !matrixOrList.length) return [];
    if (Array.isArray(matrixOrList[0])) return matrixOrList;
    return (opts && opts.orientation === 'row') ? [matrixOrList] : matrixOrList.map(function (opt) { return [opt]; });
  }

  function inferAxisUnit(opt, ax, optKey, axKey) {
    if (opt && opt[optKey]) return String(opt[optKey]).trim();
    if (ax && ax[axKey]) return String(ax[axKey]).trim();
    if (ax && ax.name) {
      var m = String(ax.name).match(/(?:\(([^)]+)\)|\/\s*([^\s/]+))\s*$/);
      if (m) return (m[1] || m[2]).trim();
    }
    return '__default__';
  }

  function syncColumnXSpans(mat, opts) {
    var cols = mat.reduce(function (m, r) { return Math.max(m, r.length); }, 0);
    var fillVal = opts && opts.fillValue !== undefined ? opts.fillValue : 0;
    var forcedX = (opts && (opts.timeGrid || opts.xBuckets)) || null;
    for (var c = 0; c < cols; c += 1) {
      var groups = {};
      for (var r = 0; r < mat.length; r += 1) {
        var opt = mat[r] && mat[r][c];
        if (!opt) continue;
        var xAx = Array.isArray(opt.xAxis) ? opt.xAxis[0] : opt.xAxis;
        if (!xAx || opt.independentXSpan || xAx.quietIndependentSpan) continue;
        var evKey = opt.eventKey != null ? opt.eventKey : (opts && opts.eventKey != null ? opts.eventKey : '');
        var xKey = inferAxisUnit(opt, xAx, 'xUnit', 'quietUnit') + '|' + String(evKey) + '|' + String(xAx.type || 'category');
        if (!groups[xKey]) groups[xKey] = [];
        groups[xKey].push({ opt: opt, xAx: xAx });
      }
      Object.keys(groups).forEach(function (k) {
        var grp = groups[k];
        if (grp.length < 2 && !forcedX) return;
        var xType = grp[0].xAx.type || 'category';
        if (xType === 'category') {
          var seen = Object.create(null);
          var union = forcedX ? forcedX.slice() : [];
          if (!forcedX) {
            grp.forEach(function (entry) {
              (entry.xAx.data || []).forEach(function (lbl) {
                var sk = String(lbl);
                if (!seen[sk]) { seen[sk] = true; union.push(lbl); }
              });
            });
            if (union.length > 1 && union.every(function (v) { return typeof v === 'number' || /^\d{4}-\d{2}-\d{2}|^\d{1,2}:\d{2}/.test(String(v)); })) {
              union.sort(function (a, b) {
                if (typeof a === 'number' && typeof b === 'number') return a - b;
                var ta = Date.parse(String(a)), tb = Date.parse(String(b));
                return (Number.isFinite(ta) && Number.isFinite(tb)) ? ta - tb : String(a).localeCompare(String(b));
              });
            }
          }
          grp.forEach(function (entry) {
            var oldCats = Array.isArray(entry.xAx.data) ? entry.xAx.data : [];
            (entry.opt.series || []).forEach(function (sr) {
              if (!Array.isArray(sr.data)) return;
              var byCat = Object.create(null);
              sr.data.forEach(function (pt, idx) {
                if (Array.isArray(pt)) byCat[String(pt[0])] = pt[1];
                else if (idx < oldCats.length) byCat[String(oldCats[idx])] = pt;
              });
              if (oldCats.length || sr.data.every(function (pt) { return Array.isArray(pt); })) {
                sr.data = union.map(function (b) {
                  var bk = String(b);
                  return Object.prototype.hasOwnProperty.call(byCat, bk) ? byCat[bk] : fillVal;
                });
              }
            });
            entry.xAx.data = union.slice();
          });
        } else if (xType === 'time' || xType === 'value') {
          var isT = xType === 'time';
          var xs = [];
          var parseX = function (rawV) {
            if (typeof rawV === 'number') return Number.isFinite(rawV) ? rawV : NaN;
            if (rawV instanceof Date) return rawV.getTime();
            if (typeof rawV === 'string' && rawV.trim() !== '') {
              var s = rawV.trim();
              if (/^-?\d+(?:\.\d+)?$/.test(s)) return Number(s);
              if (isT) { var ts = Date.parse(s); return Number.isFinite(ts) ? ts : NaN; }
              return Number(s);
            }
            return NaN;
          };
          grp.forEach(function (entry) {
            var xm0 = parseX(entry.xAx.min), xm1 = parseX(entry.xAx.max);
            if (Number.isFinite(xm0)) xs.push(xm0);
            if (Number.isFinite(xm1)) xs.push(xm1);
            (entry.opt.series || []).forEach(function (sr) {
              (sr.data || []).forEach(function (pt) {
                var rawX = Array.isArray(pt) ? pt[0] : (pt && typeof pt === 'object' && Array.isArray(pt.value) ? pt.value[0] : NaN);
                var xv = parseX(rawX);
                if (Number.isFinite(xv)) xs.push(xv);
              });
            });
          });
          if (forcedX && forcedX.length) {
            var fx0 = parseX(forcedX[0]), fx1 = parseX(forcedX[forcedX.length - 1]);
            if (Number.isFinite(fx0)) xs.push(fx0);
            if (Number.isFinite(fx1)) xs.push(fx1);
          }
          if (xs.length) {
            var loX = Math.min.apply(null, xs), hiX = Math.max.apply(null, xs);
            grp.forEach(function (entry) { entry.xAx.min = loX; entry.xAx.max = hiX; });
          }
        }
      });
    }
  }

  function collectAxisYValues(opt, axisIdx) {
    var vals = [];
    var stackPos = {}, stackNeg = {};
    (opt.series || []).forEach(function (sr) {
      if (!sr || Number(sr.yAxisIndex || 0) !== axisIdx) return;
      var sKey = sr.stack ? String(sr.stack) : null;
      if (sKey && !stackPos[sKey]) { stackPos[sKey] = {}; stackNeg[sKey] = {}; }
      (sr.data || []).forEach(function (pt, idx) {
        var raw = Array.isArray(pt) ? pt[1] : (pt && typeof pt === 'object' ? (Array.isArray(pt.value) ? pt.value[1] : pt.value) : pt);
        if (raw === null || raw === undefined || raw === '' || typeof raw === 'boolean') return;
        var v = Number(raw);
        if (!Number.isFinite(v)) return;
        if (sKey) {
          var bk = Array.isArray(pt) ? String(pt[0]) : (pt && typeof pt === 'object' && Array.isArray(pt.value) ? String(pt.value[0]) : String(idx));
          if (v >= 0) stackPos[sKey][bk] = (stackPos[sKey][bk] || 0) + v;
          else stackNeg[sKey][bk] = (stackNeg[sKey][bk] || 0) + v;
        } else vals.push(v);
      });
      if (sr.markLine && Array.isArray(sr.markLine.data)) {
        sr.markLine.data.forEach(function (ml) {
          var mv = ml && ml.yAxis !== undefined ? Number(ml.yAxis) : NaN;
          if (Number.isFinite(mv)) vals.push(mv);
        });
      }
    });
    [stackPos, stackNeg].forEach(function (map) {
      Object.keys(map).forEach(function (sk) {
        Object.keys(map[sk]).forEach(function (bk) { vals.push(map[sk][bk]); });
      });
    });
    return vals;
  }

  function syncUnitYSpans(mat, opts, svgLayout) {
    if (!svgLayout || (opts && opts.alignY === false)) return;
    var groups = {};
    mat.forEach(function (row) {
      row.forEach(function (opt) {
        if (!opt) return;
        var yAxes = Array.isArray(opt.yAxis) ? opt.yAxis : (opt.yAxis ? [opt.yAxis] : []);
        var y0 = yAxes[0];
        if (!y0 || (y0.type && y0.type !== 'value') || opt.independentYSpan || y0.quietZoomedScale || y0.quietIndependentSpan) return;
        var uk = inferAxisUnit(opt, y0, 'yUnit', 'quietUnit');
        if (!groups[uk]) groups[uk] = [];
        groups[uk].push({ opt: opt, y0: y0 });
      });
    });
    Object.keys(groups).forEach(function (uk) {
      var grp = groups[uk];
      var allVals = [];
      grp.forEach(function (entry) { Array.prototype.push.apply(allVals, collectAxisYValues(entry.opt, 0)); });
      if (!allVals.length) return;
      var sc = svgLayout.sharedNiceScale125(allVals, {
        targetTicks: (opts && opts.targetYTicks) || 5,
        includeZero: opts ? opts.includeZero : undefined,
        headroomRatio: (opts && opts.headroomRatio != null) ? opts.headroomRatio : 0.06,
      });
      grp.forEach(function (entry) {
        var hadMax = entry.y0.max !== undefined;
        if (grp.length > 1 || entry.y0.min === undefined) entry.y0.min = sc.min;
        if (grp.length > 1 || !hadMax) entry.y0.max = sc.max;
        if (grp.length > 1 || (!hadMax && entry.y0.interval === undefined)) entry.y0.interval = sc.step;
      });
    });
  }

  function formatAxisTickList(ax, fallbackVals, svgLayout) {
    var lo = ax && ax.min != null && Number.isFinite(Number(ax.min)) ? Number(ax.min) : (fallbackVals.length ? Math.min.apply(null, fallbackVals) : 0);
    var hi = ax && ax.max != null && Number.isFinite(Number(ax.max)) ? Number(ax.max) : (fallbackVals.length ? Math.max.apply(null, fallbackVals) : 100);
    var sc = svgLayout ? svgLayout.niceScale125(lo, hi, { targetTicks: 5 }) : { ticks: [lo, hi], step: (hi - lo) || 1 };
    var fmt = ax && ax.axisLabel && typeof ax.axisLabel.formatter === 'function' ? ax.axisLabel.formatter : null;
    return sc.ticks.map(function (v) { return fmt ? String(fmt(v)) : (svgLayout ? svgLayout.formatTick(v, sc.step) : String(v)); });
  }

  var _baseGridMap = typeof WeakMap === 'function' ? new WeakMap() : null;

  function alignPlotGridFrames(matrixOrList, opts) {
    var cfg = opts || {};
    var svgLayout = getSvgLayout();
    var mat = toMatrix(matrixOrList, cfg);
    if (!mat.length) return matrixOrList;
    mat.forEach(function (row) {
      row.forEach(function (opt) {
        if (!opt) return;
        var rawG = Array.isArray(opt.grid) ? (opt.grid[0] || {}) : (opt.grid || {});
        if (_baseGridMap && !_baseGridMap.has(opt)) _baseGridMap.set(opt, Object.assign({}, rawG));
        applySafeMarkLines(opt, cfg.tokens);
        applySafeLegendLayout(opt, cfg.containerWidth);
      });
    });
    var collapseCols = !!(cfg.collapseColumns || (Number(cfg.containerWidth || 0) > 0 && Number(cfg.containerWidth) < (cfg.stackBreakpoint || 780)));
    var spanMat = collapseCols ? mat.reduce(function (a, r) { r.forEach(function (o) { if (o) a.push([o]); }); return a; }, []) : mat;
    syncColumnXSpans(spanMat, cfg);
    syncUnitYSpans(mat, cfg, svgLayout);
    if (!svgLayout) return matrixOrList;

    var descMat = mat.map(function (row) {
      return row.map(function (opt) {
        if (!opt) return null;
        var yAxes = Array.isArray(opt.yAxis) ? opt.yAxis : (opt.yAxis ? [opt.yAxis] : []);
        var xAx = Array.isArray(opt.xAxis) ? opt.xAxis[0] : opt.xAxis;
        var g0 = Array.isArray(opt.grid) ? (opt.grid[0] || {}) : (opt.grid || {});
        var baseG = (_baseGridMap && _baseGridMap.get(opt)) || g0;
        var lg = Array.isArray(opt.legend) ? opt.legend[0] : opt.legend;
        var lgOn = !!(lg && lg.show !== false);
        var hasBotLg = !!(lgOn && (lg.bottom != null || lg.top === 'bottom'));
        var hasTopLg = !!(lgOn && !hasBotLg);
        var lgItems = Array.isArray(lg && lg.data) ? lg.data.length : (Array.isArray(opt.series) ? opt.series.length : 0);
        var lgNarrow = Number(cfg.containerWidth || 0) > 0 && Number(cfg.containerWidth) < 640;
        var lgBotFloor = hasBotLg ? ((lgNarrow && lgItems >= 3) ? 46 : 38) : 0;
        var baseBot = typeof baseG.bottom === 'number' ? baseG.bottom : null;
        var y0 = yAxes[0] || {}, y1 = yAxes.length > 1 ? yAxes[1] : null;
        var primVals = collectAxisYValues(opt, 0), secVals = y1 ? collectAxisYValues(opt, 1) : [];
        var xData = xAx && Array.isArray(xAx.data) && xAx.data.length ? xAx.data : ['0', '1'];
        var titleObj = Array.isArray(opt.title) ? opt.title[0] : opt.title;
        return {
          yTicks: formatAxisTickList(y0, primVals, svgLayout),
          rightTicks: y1 ? formatAxisTickList(y1, secVals.length ? secVals : [0, 100], svgLayout) : [],
          hasRightAxis: !!y1, rightTitle: y1 ? y1.name : '',
          yLabel: y0.name && y0.nameLocation === 'middle' ? y0.name : '',
          hasTopYName: !!(y0.name && (!y0.nameLocation || y0.nameLocation === 'end')),
          titleHeight: (titleObj && titleObj.show !== false && titleObj.text) ? 28 : 0,
          xTicks: xData, xLabel: xAx && xAx.name ? xAx.name : '',
          hasTopLegend: hasTopLg, hasBottomLegend: hasBotLg,
          topLegendHeight: hasTopLg ? 28 : 0, bottomLegendHeight: lgBotFloor,
          minLeft: typeof baseG.left === 'number' ? baseG.left : (cfg.minLeft || 44),
          minRight: typeof baseG.right === 'number' ? baseG.right : (cfg.minRight || (y1 ? 48 : 16)),
          minTop: typeof baseG.top === 'number' ? baseG.top : (cfg.minTop || 24),
          minBottom: Math.max(baseBot !== null ? baseBot : (cfg.minBottom || 34), lgBotFloor),
          stageHeight: Number(opt.quietStageHeight || cfg.stageHeight || 0), containerPadX: Number(opt.quietContainerPadX || 0),
        };
      });
    });

    var applyCell = function (opt, cell) {
      if (!opt || !cell) return;
      if (Array.isArray(opt.grid) && opt.grid.length) {
        opt.grid[0] = Object.assign({}, opt.grid[0], { containLabel: false, left: cell.left, right: cell.right, top: cell.top });
        if (opt.grid.length === 1) opt.grid[0].bottom = cell.bottom;
      } else opt.grid = Object.assign({}, opt.grid || {}, { containLabel: false, left: cell.left, right: cell.right, top: cell.top, bottom: cell.bottom });
    };
    var flatIdx = [], gutterInput = collapseCols ? descMat.reduce(function (acc, row, r) {
      row.forEach(function (cell, c) { if (cell) { flatIdx.push([r, c, acc.length]); acc.push([cell]); } });
      return acc;
    }, []) : descMat;
    var gutters = svgLayout.computeGridFrameGutters(gutterInput, cfg);
    if (collapseCols) flatIdx.forEach(function (t) { applyCell(mat[t[0]][t[1]], gutters.cells[t[2]] && gutters.cells[t[2]][0]); });
    else mat.forEach(function (row, r) { row.forEach(function (opt, c) { applyCell(opt, gutters.cells[r] && gutters.cells[r][c]); }); });
    return matrixOrList;
  }

  function observeChartResize(hostEl, chart, opts) {
    if (!hostEl || !chart || typeof chart.resize !== 'function') return function () {};
    var raf = typeof root.requestAnimationFrame === 'function' ? root.requestAnimationFrame.bind(root) : function (fn) { return setTimeout(fn, 16); };
    var cancelRaf = typeof root.cancelAnimationFrame === 'function' ? root.cancelAnimationFrame.bind(root) : clearTimeout;
    var lastW = Math.round(hostEl.clientWidth || 0), rafId = 0, dead = false, ro = null, onWin = null;
    var cleanup = function () {
      dead = true;
      if (rafId) { cancelRaf(rafId); rafId = 0; }
      if (ro) { ro.disconnect(); ro = null; }
      if (onWin && typeof root.removeEventListener === 'function') { root.removeEventListener('resize', onWin); onWin = null; }
    };
    var trigger = function () {
      if (dead) return;
      if (chart.isDisposed && chart.isDisposed()) { cleanup(); return; }
      if (rafId) return;
      rafId = raf(function () {
        rafId = 0;
        if (dead || (chart.isDisposed && chart.isDisposed())) { cleanup(); return; }
        var w = Math.round(hostEl.clientWidth || 0);
        if (w <= 0 || w === lastW) return;
        lastW = w;
        if (opts && typeof opts.onResize === 'function') opts.onResize(w, chart, hostEl);
        else chart.resize();
      });
    };
    if (typeof root.ResizeObserver === 'function') {
      ro = new root.ResizeObserver(function () {
        if (dead || (chart.isDisposed && chart.isDisposed())) { cleanup(); return; }
        var w = Math.round(hostEl.clientWidth || 0);
        if (w > 0 && w !== lastW) trigger();
      });
      ro.observe(hostEl);
      return cleanup;
    }
    if (typeof root.addEventListener === 'function') { onWin = trigger; root.addEventListener('resize', onWin); }
    return cleanup;
  }

  function alignSharedAxes(optionsArray, opts) {
    return alignPlotGridFrames(optionsArray, Object.assign({ orientation: 'column' }, opts || {}));
  }

  var api = {
    ensureGridContainLabel: ensureGridContainLabel, applyNiceLinearAxisBounds: applyNiceLinearAxisBounds,
    applySafeMarkLines: applySafeMarkLines, applySafeLegendLayout: applySafeLegendLayout,
    alignPlotGridFrames: alignPlotGridFrames, alignSharedAxes: alignSharedAxes,
    observeChartResize: observeChartResize, normalizeOption: normalizeOption,
  };
  root.QuietEChartsDefaults = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
