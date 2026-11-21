// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  function ensureGridContainLabel(opt) {
    if (!opt) return opt;
    if (Array.isArray(opt.grid)) {
      opt.grid = opt.grid.map(function (g) {
        return Object.assign({ containLabel: true }, g || {});
      });
    } else if (opt.grid && typeof opt.grid === 'object') {
      opt.grid = Object.assign({ containLabel: true }, opt.grid);
    }
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
        var rawMin = Math.min.apply(null, vals);
        var rawMax = Math.max.apply(null, vals);
        var lo = yAxes[0].min !== undefined ? Number(yAxes[0].min) : rawMin;
        var span = rawMax - rawMin;
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
        if (entry.xAxis !== undefined || (parentLbl.position && !(entry.label && entry.label.position))) {
          return entry;
        }
        var lbl = Object.assign({}, entry.label || {});
        var rawTxt = String(lbl.formatter || entry.name || '').toLowerCase();
        if (!lbl.position) {
          lbl.position = rawTxt.indexOf('floor') >= 0 ? 'insideStartBottom' : 'insideEndTop';
        }
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

  function normalizeOption(opt, payload, tokens) {
    if (!opt) return opt;
    ensureGridContainLabel(opt);
    applySafeMarkLines(opt, tokens);
    if (payload && (payload.kind === 'cartesian' || !payload.kind)) {
      applyNiceLinearAxisBounds(opt, payload);
    }
    return opt;
  }

  root.QuietEChartsDefaults = {
    ensureGridContainLabel: ensureGridContainLabel,
    applyNiceLinearAxisBounds: applyNiceLinearAxisBounds,
    applySafeMarkLines: applySafeMarkLines,
    normalizeOption: normalizeOption,
  };
}(typeof window !== 'undefined' ? window : globalThis));
