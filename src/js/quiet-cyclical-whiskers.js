// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  function readThemeTokens(doc) {
    var d = doc || (typeof document !== 'undefined' ? document : null);
    var cs = (d && d.documentElement && typeof getComputedStyle === 'function')
      ? getComputedStyle(d.documentElement) : null;
    var pick = function (tok, fb) {
      try {
        var v = cs ? cs.getPropertyValue(tok).trim() : '';
        return v || fb;
      } catch (_e) {
        return fb;
      }
    };
    return {
      textPrimary: pick('--text-primary', '#0F172A'),
      textSecondary: pick('--text-secondary', '#475569'),
      borderHairline: pick('--border-hairline', '#E2E8F0'),
      borderStrong: pick('--border-strong', '#94A3B8'),
      bgSurface: pick('--bg-surface', '#FFFFFF'),
      bgElevated: pick('--bg-elevated', '#F8FAFC'),
      accentFocal: pick('--accent-focal', '#1D4ED8'),
    };
  }

  function nice125(lo, hi, targetTicks) {
    if (root.QuietSvgLayout && typeof root.QuietSvgLayout.niceScale125 === 'function') {
      return root.QuietSvgLayout.niceScale125(lo, hi, { targetTicks: targetTicks || 5, includeZero: lo >= 0 });
    }
    var a = lo >= 0 ? 0 : lo;
    var span = Math.max(1e-9, hi - a);
    var raw = span / Math.max(2, (targetTicks || 5) - 1);
    var p = Math.pow(10, Math.floor(Math.log10(raw)));
    var f = raw / p;
    var m = f <= 1 ? 1 : (f <= 2 ? 2 : (f <= 5 ? 5 : 10));
    var step = m * p;
    var sMin = Math.floor(a / step) * step;
    var sMax = Math.ceil(hi / step) * step;
    return { min: sMin, max: sMax === sMin ? sMin + step : sMax, step: step };
  }

  function finiteNum(v) {
    if (v === null || v === undefined || v === '' || typeof v === 'boolean') return null;
    var n = Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function normalizeCyclicalBuckets(buckets) {
    return (Array.isArray(buckets) ? buckets : []).map(function (b, idx) {
      var item = b && typeof b === 'object' ? b : {};
      var label = String(item.label != null ? item.label : (item.slot != null ? item.slot : (item.hour != null ? item.hour : (item.day != null ? item.day : idx))));
      var vals = Array.isArray(item.values) ? item.values.map(finiteNum).filter(function (v) { return v !== null; }) : [];
      var rawN = [item.activeDays, item.active_days, item.nActive, item.n_active, item.n, item.samples].find(function (v) { return v != null; });
      var activeDays = finiteNum(rawN);
      var min = finiteNum(item.min);
      var max = finiteNum(item.max);
      var avg = finiteNum(item.avg != null ? item.avg : item.mean);
      var recent = finiteNum(item.recent != null ? item.recent : (item.last24h != null ? item.last24h : (item.current != null ? item.current : item.today)));
      if (vals.length) {
        if (min === null) min = Math.min.apply(null, vals);
        if (max === null) max = Math.max.apply(null, vals);
        if (avg === null) avg = vals.reduce(function (s, x) { return s + x; }, 0) / vals.length;
        if (activeDays === null) activeDays = vals.length;
      }
      if (min !== null && max !== null && min > max) {
        var t = min; min = max; max = t;
      }
      if (avg === null && min !== null && max !== null) avg = (min + max) * 0.5;
      if (min !== null && max === null) max = avg !== null ? Math.max(min, avg) : min;
      if (max !== null && min === null) min = avg !== null ? Math.min(max, avg) : max;
      var hasObs = (activeDays === null || activeDays > 0) && min !== null && max !== null;
      return {
        idx: idx,
        label: label,
        min: hasObs ? min : null,
        avg: hasObs ? avg : null,
        max: hasObs ? max : null,
        recent: recent,
        activeDays: activeDays !== null ? activeDays : (hasObs ? 1 : 0),
      };
    });
  }

  function buildCyclicalWhiskerOption(buckets, opts) {
    var cfg = opts || {};
    var tok = cfg.tokens || readThemeTokens(cfg.document);
    var rows = normalizeCyclicalBuckets(buckets);
    var labels = rows.map(function (r) { return r.label; });
    var yVals = [];
    rows.forEach(function (r) {
      [r.min, r.avg, r.max, r.recent].forEach(function (v) { if (v !== null) yVals.push(v); });
    });
    var rawLo = yVals.length ? Math.min.apply(null, yVals) : 0;
    var rawHi = yVals.length ? Math.max.apply(null, yVals) : 10;
    var span = rawHi - rawLo;
    var padHi = rawHi + (span > 0 ? span * 0.08 : (Math.abs(rawHi) * 0.08 || 1));
    var ySc = nice125(rawLo >= 0 ? 0 : rawLo, padHi, 5);
    var unit = String(cfg.unit || '').trim();
    var rangeLabel = String(cfg.rangeLabel || 'Min–Max');
    var avgLabel = String(cfg.avgLabel || 'Active Avg');
    var recentLabel = String(cfg.recentLabel || 'Last 24h');
    var showLegend = cfg.showLegend !== false;
    var cw = Number(cfg.containerWidth || 640);
    var xInterval = cfg.xInterval !== undefined ? cfg.xInterval : (labels.length > 16 ? (cw < 480 ? 3 : 2) : 0);
    var yName = String(cfg.yName || (unit ? 'Activity / (' + unit + ')' : 'Per-Day Activity'));

    var stemData = rows.map(function (r) {
      return r.min === null ? [r.idx, null, null, null, r.recent, r.activeDays] : [r.idx, r.min, r.max, r.avg, r.recent, r.activeDays];
    });
    var avgData = rows.map(function (r) { return r.avg === null ? [r.idx, null] : [r.idx, r.avg]; });
    var recentData = rows.map(function (r) { return r.recent === null ? [r.idx, null] : [r.idx, r.recent]; });
    var fmtVal = function (v) {
      if (v === null || v === undefined || !Number.isFinite(Number(v))) return '—';
      var n = Number(v), absN = Math.abs(n);
      var s = absN > 0 && absN < 1 ? n.toFixed(2).replace(/0+$/, '').replace(/\.$/, '') : (Math.abs(n - Math.round(n)) < 0.05 ? String(Math.round(n)) : n.toFixed(1));
      return s + (unit ? ' ' + unit : '');
    };

    var opt = {
      animation: false,
      backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Inter, system-ui, sans-serif', color: tok.textPrimary },
      tooltip: {
        trigger: 'axis',
        renderMode: 'richText',
        confine: true,
        backgroundColor: tok.bgElevated,
        borderColor: tok.borderStrong,
        borderWidth: 1,
        textStyle: { color: tok.textPrimary, fontSize: 12 },
        formatter: function (params) {
          var first = Array.isArray(params) ? params[0] : params;
          var idx = first && first.dataIndex != null ? Number(first.dataIndex) : 0;
          var r = rows[idx];
          if (!r) return '';
          var hdr = r.label + (r.activeDays ? ' (n=' + r.activeDays + ' active days)' : ' (0 active days)');
          if (r.min === null) return hdr + '\nNo observations recorded';
          return [
            hdr,
            rangeLabel + ': ' + fmtVal(r.min) + ' – ' + fmtVal(r.max),
            avgLabel + ': ' + fmtVal(r.avg),
            recentLabel + ': ' + fmtVal(r.recent),
          ].join('\n');
        },
      },
      legend: {
        show: showLegend,
        bottom: 0,
        left: 'center',
        itemWidth: 14,
        itemHeight: 8,
        itemGap: 14,
        textStyle: { color: tok.textSecondary, fontSize: 11 },
        data: [rangeLabel, avgLabel, recentLabel],
      },
      grid: { left: 48, right: 16, top: 32, bottom: showLegend ? 56 : 36, containLabel: true },
      xAxis: {
        type: 'category',
        name: String(cfg.xName || ''),
        nameLocation: 'middle',
        nameGap: 24,
        data: labels,
        axisLine: { lineStyle: { color: tok.textSecondary } },
        axisTick: { alignWithLabel: true },
        axisLabel: { color: tok.textSecondary, fontSize: 11, interval: xInterval, hideOverlap: true },
      },
      yAxis: {
        type: 'value',
        name: yName,
        nameLocation: 'end',
        nameGap: 12,
        nameTextStyle: { color: tok.textSecondary, fontSize: 11, fontWeight: 600, align: 'left' },
        min: ySc.min,
        max: ySc.max,
        interval: ySc.step,
        axisLine: { lineStyle: { color: tok.textSecondary } },
        axisLabel: { color: tok.textSecondary, fontSize: 11 },
        splitLine: { lineStyle: { color: tok.borderHairline, type: 'dashed' } },
      },
      series: [
        {
          id: 'cyclical-range',
          name: rangeLabel,
          type: 'custom',
          z: 2,
          itemStyle: { color: tok.textSecondary },
          renderItem: function (params, api) {
            var xv = api.value(0), lo = api.value(1), hi = api.value(2);
            if (lo === null || hi === null || !Number.isFinite(lo) || !Number.isFinite(hi)) return null;
            var pLo = api.coord([xv, lo]), pHi = api.coord([xv, hi]);
            if (!pLo || !pHi || !Number.isFinite(pLo[0]) || !Number.isFinite(pLo[1]) || !Number.isFinite(pHi[1])) return null;
            var cs = params && params.coordSys;
            var catW = (cs && labels.length) ? (cs.width / labels.length) : 16;
            var cap = Math.min(4.5, Math.max(2.5, catW * 0.22));
            return {
              type: 'group',
              children: [
                { type: 'line', shape: { x1: pLo[0], y1: pLo[1], x2: pHi[0], y2: pHi[1] }, style: { stroke: tok.textSecondary, lineWidth: 1.5, opacity: 0.72 } },
                { type: 'line', shape: { x1: pHi[0] - cap, y1: pHi[1], x2: pHi[0] + cap, y2: pHi[1] }, style: { stroke: tok.textSecondary, lineWidth: 1.5, opacity: 0.72 } },
                { type: 'line', shape: { x1: pLo[0] - cap, y1: pLo[1], x2: pLo[0] + cap, y2: pLo[1] }, style: { stroke: tok.textSecondary, lineWidth: 1.5, opacity: 0.72 } },
              ],
            };
          },
          data: stemData,
        },
        {
          id: 'cyclical-avg',
          name: avgLabel,
          type: 'custom',
          z: 3,
          itemStyle: { color: tok.textPrimary },
          renderItem: function (params, api) {
            var xv = api.value(0), av = api.value(1);
            if (av === null || !Number.isFinite(av)) return null;
            var pt = api.coord([xv, av]);
            if (!pt || !Number.isFinite(pt[0]) || !Number.isFinite(pt[1])) return null;
            var cs = params && params.coordSys;
            var catW = (cs && labels.length) ? (cs.width / labels.length) : 16;
            var half = Math.min(9, Math.max(4, catW * 0.34));
            return {
              type: 'line',
              shape: { x1: pt[0] - half, y1: pt[1], x2: pt[0] + half, y2: pt[1] },
              style: { stroke: tok.textPrimary, lineWidth: 2.4 },
            };
          },
          data: avgData,
        },
        {
          id: 'cyclical-recent',
          name: recentLabel,
          type: 'scatter',
          z: 4,
          symbol: 'circle',
          symbolSize: 7.5,
          itemStyle: { color: tok.accentFocal, borderColor: tok.bgSurface, borderWidth: 1.5 },
          data: recentData,
        },
      ],
    };
    return opt;
  }

  root.QuietEChartsDefaults = root.QuietEChartsDefaults || {};
  root.QuietEChartsDefaults.buildCyclicalWhiskerOption = buildCyclicalWhiskerOption;
  var api = { buildCyclicalWhiskerOption: buildCyclicalWhiskerOption, normalizeCyclicalBuckets: normalizeCyclicalBuckets };
  root.QuietCyclicalWhiskers = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
