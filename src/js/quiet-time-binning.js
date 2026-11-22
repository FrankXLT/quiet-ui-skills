// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  function parseUtcMs(raw) {
    if (typeof raw === 'number') return Number.isFinite(raw) ? raw : NaN;
    if (raw instanceof Date) return raw.getTime();
    if (typeof raw !== 'string') return NaN;
    var s = raw.trim();
    if (!s) return NaN;
    if (/^-?\d+(?:\.\d+)?$/.test(s)) {
      var num = Number(s);
      return Number.isFinite(num) ? num : NaN;
    }
    var m = s.match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2})(?::(\d{2})(?::(\d{2}))?)?)?$/);
    if (m) {
      var yr = Number(m[1]), mo = Number(m[2]), dy = Number(m[3]), hh = Number(m[4] || 0), mi = Number(m[5] || 0), ss = Number(m[6] || 0);
      var ms = Date.UTC(yr, mo - 1, dy, hh, mi, ss), dt = new Date(ms);
      return (dt.getUTCFullYear() === yr && dt.getUTCMonth() === mo - 1 && dt.getUTCDate() === dy &&
        dt.getUTCHours() === hh && dt.getUTCMinutes() === mi && dt.getUTCSeconds() === ss) ? ms : NaN;
    }
    var w = s.match(/^(\d{4})-W(\d{2})$/);
    if (w) {
      var wk = Number(w[2]);
      if (wk < 1 || wk > 53) return NaN;
      var j4 = new Date(Date.UTC(Number(w[1]), 0, 4)), d4 = j4.getUTCDay() || 7;
      return j4.getTime() + ((wk - 1) * 7 + (1 - d4)) * 86400000;
    }
    var ts = Date.parse(s);
    return Number.isFinite(ts) ? ts : NaN;
  }

  function pad2(n) { return n < 10 ? '0' + n : String(n); }

  function utcBucketInfo(ms, bin, cfg) {
    var dt = new Date(ms), y = dt.getUTCFullYear(), mo = pad2(dt.getUTCMonth() + 1), d = pad2(dt.getUTCDate());
    if (bin === '1h') return { sortMs: Date.UTC(y, dt.getUTCMonth(), dt.getUTCDate(), dt.getUTCHours()), key: y + '-' + mo + '-' + d + ' ' + pad2(dt.getUTCHours()) + ':00' };
    if (bin === '1d') return { sortMs: Date.UTC(y, dt.getUTCMonth(), dt.getUTCDate()), key: y + '-' + mo + '-' + d };
    var mon = new Date(Date.UTC(y, dt.getUTCMonth(), dt.getUTCDate())), day = mon.getUTCDay() || 7;
    var monMs = mon.getTime() + (1 - day) * 86400000;
    if (cfg && cfg.weekFormat === 'monday') {
      var md = new Date(monMs);
      return { sortMs: monMs, key: md.getUTCFullYear() + '-' + pad2(md.getUTCMonth() + 1) + '-' + pad2(md.getUTCDate()) };
    }
    var thu = new Date(mon.getTime() + (4 - day) * 86400000);
    var wk = Math.ceil(((thu.getTime() - Date.UTC(thu.getUTCFullYear(), 0, 1)) / 86400000 + 1) / 7);
    return { sortMs: monMs, key: thu.getUTCFullYear() + '-W' + pad2(wk) };
  }

  /** Deterministically bin hourly/daily UTC series into 1h (<=3d), 1d (4-92d), or ISO 1w (>92d) sums. */
  function binTimeSeries(dates, layersObj, opts) {
    var cfg = opts || {}, rawDates = Array.isArray(dates) ? dates : [], srcLayers = layersObj && typeof layersObj === 'object' ? layersObj : {};
    var names = Object.keys(srcLayers), parsed = [], minTs = Infinity, maxTs = -Infinity;
    for (var i = 0; i < rawDates.length; i += 1) {
      var ms = parseUtcMs(rawDates[i]);
      if (!Number.isFinite(ms)) continue;
      parsed.push({ idx: i, ms: ms });
      if (ms < minTs) minTs = ms;
      if (ms > maxTs) maxTs = ms;
    }
    if (!parsed.length) {
      var emptyL = {};
      names.forEach(function (nm) { emptyL[nm] = []; });
      return { dates: [], layers: emptyL, bin: cfg.bin || '1h', spanDays: 0 };
    }
    var spanDays = Math.max(0, (maxTs - minTs) / 86400000);
    var hLim = cfg.hourlyMaxDays != null ? Number(cfg.hourlyMaxDays) : 3, dLim = cfg.dailyMaxDays != null ? Number(cfg.dailyMaxDays) : 92;
    var bin = cfg.bin || (spanDays <= hLim ? '1h' : (spanDays <= dLim ? '1d' : '1w')), buckets = Object.create(null);
    parsed.forEach(function (pt) {
      var info = utcBucketInfo(pt.ms, bin, cfg);
      if (!buckets[info.key]) {
        var initVals = {};
        names.forEach(function (nm) { initVals[nm] = 0; });
        buckets[info.key] = { key: info.key, sortMs: info.sortMs, vals: initVals };
      }
      var b = buckets[info.key];
      names.forEach(function (nm) {
        var arr = srcLayers[nm], v = Array.isArray(arr) ? Number(arr[pt.idx]) : 0;
        if (Number.isFinite(v)) b.vals[nm] += v;
      });
    });
    var ordered = Object.keys(buckets).map(function (k) { return buckets[k]; }).sort(function (a, b) { return a.sortMs - b.sortMs; });
    var outDates = ordered.map(function (b) { return b.key; }), outLayers = {};
    names.forEach(function (nm) { outLayers[nm] = ordered.map(function (b) { return Math.round(b.vals[nm] * 1e9) / 1e9; }); });
    return { dates: outDates, layers: outLayers, bin: bin, spanDays: Math.round(spanDays * 100) / 100 };
  }

  function parseCssRgb(str) {
    var s = String(str || '').trim();
    var m3 = s.match(/^#([0-9a-f]{3})$/i);
    if (m3) {
      var h3 = m3[1];
      return [parseInt(h3[0] + h3[0], 16), parseInt(h3[1] + h3[1], 16), parseInt(h3[2] + h3[2], 16)];
    }
    var m = s.match(/^#([0-9a-f]{6})$/i);
    if (m) return [parseInt(m[1].slice(0, 2), 16), parseInt(m[1].slice(2, 4), 16), parseInt(m[1].slice(4, 6), 16)];
    var r = s.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
    return r ? [Number(r[1]), Number(r[2]), Number(r[3])] : null;
  }

  function relLum(rgb) {
    if (!rgb) return 1;
    var f = function (c) { var s = c / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2]);
  }

  function isValidCellForCol(c) {
    return Array.isArray(c) && c[0] != null && c[0] !== '' && Number.isFinite(Number(c[0]));
  }

  /** Trim trailing week columns whose cells lie strictly in the future and provide zero-cell contrast styling. */
  function trimTrailingFutureWeeks(weeks, cells, opts) {
    var wkList = Array.isArray(weeks) ? weeks.slice() : [], cellList = Array.isArray(cells) ? cells.filter(isValidCellForCol) : [];
    var cfg = opts || {};
    var todayMs = cfg.today != null ? parseUtcMs(cfg.today) : Date.now();
    var cutoff = Number.isFinite(todayMs) ? todayMs : Date.now();
    var endCol = wkList.length;
    while (endCol > 0) {
      var wkMs = parseUtcMs(wkList[endCol - 1]);
      var colHasData = cellList.some(function (c) {
        if (Number(c[0]) !== endCol - 1 || c.future || c[2] == null) return false;
        var v = Number(c[2]);
        return Number.isFinite(v) && v !== 0;
      });
      if ((Number.isFinite(wkMs) && wkMs > cutoff) || (!colHasData && cfg.dropEmptyTrailing)) endCol -= 1;
      else break;
    }
    return {
      weeks: wkList.slice(0, endCol),
      cells: cellList.filter(function (c) { var col = Number(c[0]); return col >= 0 && col < endCol; }),
    };
  }

  function heatmapZeroCellStyle(cardBg, borderHairline) {
    var lum = relLum(parseCssRgb(cardBg) || [255, 255, 255]);
    var isDark = lum < 0.2;
    var fill = isDark ? '#435266' : '#E2E8F0';
    var bd = borderHairline && String(borderHairline).trim().toLowerCase() !== fill.toLowerCase() ? borderHairline : (isDark ? '#64748B' : '#CBD5E1');
    if (isDark && bd.toLowerCase() === '#1e293b') bd = '#64748B';
    return {
      fill: fill,
      borderColor: bd,
      borderWidth: 1,
      labelColor: isDark ? '#F1F5F9' : '#0F172A',
      minDeltaLuminance: 0.06,
    };
  }

  var api = {
    parseUtcMs: parseUtcMs,
    binTimeSeries: binTimeSeries,
    trimTrailingFutureWeeks: trimTrailingFutureWeeks,
    heatmapZeroCellStyle: heatmapZeroCellStyle,
  };
  root.QuietTimeBinning = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
