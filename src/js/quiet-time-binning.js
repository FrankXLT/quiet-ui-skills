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
        var initVals = Object.create(null);
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
    var outDates = ordered.map(function (b) { return b.key; }), outLayers = Object.create(null);
    names.forEach(function (nm) { outLayers[nm] = ordered.map(function (b) { return Math.round(b.vals[nm] * 1e9) / 1e9; }); });
    return { dates: outDates, layers: outLayers, bin: bin, spanDays: Math.round(spanDays * 100) / 100 };
  }

  function resolveCssColor(raw, doc) {
    var s = String(raw || '').trim();
    var targetDoc = doc || root.document || null;
    for (var depth = 0; depth < 4 && /^var\(/i.test(s); depth += 1) {
      var inner = s.slice(4, -1), comma = inner.indexOf(',');
      var tok = (comma >= 0 ? inner.slice(0, comma) : inner).trim();
      var fb = comma >= 0 ? inner.slice(comma + 1).trim() : '';
      var val = '';
      var csHost = (targetDoc && targetDoc.defaultView && typeof targetDoc.defaultView.getComputedStyle === 'function')
        ? targetDoc.defaultView
        : (typeof root.getComputedStyle === 'function' ? root : null);
      if (targetDoc && targetDoc.documentElement && csHost) {
        try { val = csHost.getComputedStyle(targetDoc.documentElement).getPropertyValue(tok).trim(); } catch (_err) {}
      }
      s = val || fb;
      if (!s) break;
    }
    return s;
  }

  function parseCssRgb(str, doc) {
    var s = resolveCssColor(str, doc);
    var m3 = s.match(/^#([0-9a-f]{3})$/i);
    if (m3) {
      var h3 = m3[1];
      return [parseInt(h3[0] + h3[0], 16), parseInt(h3[1] + h3[1], 16), parseInt(h3[2] + h3[2], 16)];
    }
    var m = s.match(/^#([0-9a-f]{6})$/i);
    if (m) return [parseInt(m[1].slice(0, 2), 16), parseInt(m[1].slice(2, 4), 16), parseInt(m[1].slice(4, 6), 16)];
    var r = s.match(/^rgba?\(\s*(\d+)\s*[,\s]+(\d+)\s*[,\s]+(\d+)/i);
    if (r) return [Number(r[1]), Number(r[2]), Number(r[3])];
    var ok = s.match(/^okl(?:ch|ab)\(\s*([0-9.]+)(%?)/i);
    if (ok) {
      var lRaw = parseFloat(ok[1]), lNorm = ok[2] === '%' ? (lRaw / 100) : lRaw;
      var g = Math.max(0, Math.min(255, Math.round(Math.pow(Math.max(0, Math.min(1, lNorm)), 1.5) * 255)));
      return [g, g, g];
    }
    return null;
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

  function heatmapZeroCellStyle(cardBg, borderHairline, docOrOpts) {
    var doc = docOrOpts && docOrOpts.documentElement ? docOrOpts : (docOrOpts && docOrOpts.document ? docOrOpts.document : root.document);
    var bgResolved = resolveCssColor(cardBg, doc);
    var lum = relLum(parseCssRgb(bgResolved, doc) || [255, 255, 255]);
    var isDark = lum < 0.2;
    var fill = isDark ? '#435266' : '#E2E8F0';
    var bdRaw = resolveCssColor(borderHairline, doc);
    var bd = bdRaw && bdRaw.toLowerCase() !== fill.toLowerCase() ? bdRaw : (isDark ? '#64748B' : '#CBD5E1');
    if (isDark && bd.toLowerCase() === '#1e293b') bd = '#64748B';
    return {
      fill: fill,
      borderColor: bd,
      borderWidth: 1,
      labelColor: isDark ? '#F1F5F9' : '#0F172A',
      minDeltaLuminance: 0.06,
    };
  }

  var DAY_MS = 86400000;
  var ROLLING_SPECS = Object.assign(Object.create(null), { '7d': ['7 days', 7], r7: ['7 days', 7], r7d: ['7 days', 7], '14d': ['14 days', 14], r14: ['14 days', 14], r14d: ['14 days', 14], '30d': ['30 days', 30], r30: ['30 days', 30], r30d: ['30 days', 30], '90d': ['90 days', 90], r90: ['90 days', 90], r90d: ['90 days', 90], '52w': ['52 weeks', 364], r52w: ['52 weeks', 364] });
  var CAL_LABELS = Object.assign(Object.create(null), { wtd: 'WTD', '2w-cal': '2W-Cal', '2w_cal': '2W-Cal', mtd: 'MTD', qtd: 'QTD', ytd: 'YTD', all: 'All Scanned', all_scanned: 'All Scanned' });
  var ROLL_TO_CAL = Object.assign(Object.create(null), { '7d': 'wtd', r7: 'wtd', r7d: 'wtd', '14d': '2w-cal', r14: '2w-cal', r14d: '2w-cal', '30d': 'mtd', r30: 'mtd', r30d: 'mtd', '90d': 'qtd', r90: 'qtd', r90d: 'qtd', '52w': 'ytd', r52w: 'ytd' });
  var CAL_TO_ROLL = Object.assign(Object.create(null), { wtd: '7d', '2w-cal': '14d', '2w_cal': '14d', mtd: '30d', qtd: '90d', ytd: '52w', all: '52w', all_scanned: '52w' });

  function toUtcDayMs(raw) {
    var ms = parseUtcMs(raw);
    if (!Number.isFinite(ms)) return NaN;
    var d = new Date(ms);
    return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate());
  }

  function fmtUtcDay(ms) {
    var d = new Date(ms);
    return d.getUTCFullYear() + '-' + pad2(d.getUTCMonth() + 1) + '-' + pad2(d.getUTCDate());
  }

  function normMode(mode, preset) {
    var m = String(mode || '').toLowerCase();
    if (m === 'cal' || m === 'calendar' || m === 'cal-to-date') return 'cal';
    if (m === 'rolling') return 'rolling';
    return CAL_LABELS[String(preset || '').toLowerCase()] ? 'cal' : 'rolling';
  }

  function mapPresetForMode(preset, mode) {
    var p = String(preset || '30d').toLowerCase(), md = normMode(mode, p);
    if (md === 'cal') return CAL_LABELS[p] ? p : (ROLL_TO_CAL[p] || 'mtd');
    return ROLLING_SPECS[p] ? p : (CAL_TO_ROLL[p] || '30d');
  }

  function formatPresetLabel(preset, mode) {
    var p = mapPresetForMode(preset, mode), md = normMode(mode, p);
    return md === 'cal' ? (CAL_LABELS[p] || 'MTD') : (ROLLING_SPECS[p] ? ROLLING_SPECS[p][0] : '30 days');
  }

  function calStartMs(endMs, preset) {
    var d = new Date(endMs), y = d.getUTCFullYear(), mo = d.getUTCMonth();
    if (preset === 'wtd' || preset === '2w-cal' || preset === '2w_cal') {
      var monMs = endMs - ((d.getUTCDay() || 7) - 1) * DAY_MS;
      return preset === 'wtd' ? monMs : (monMs - 7 * DAY_MS);
    }
    if (preset === 'mtd') return Date.UTC(y, mo, 1);
    if (preset === 'qtd') return Date.UTC(y, Math.floor(mo / 3) * 3, 1);
    return Date.UTC(y, 0, 1);
  }

  /** Clamp lookback start & anchor end to {minDate, maxDate} and switch Rolling/Cal-to-Date labels cleanly. */
  function resolvePeriodBounds(opts) {
    var cfg = opts || {}, mode = normMode(cfg.mode, cfg.preset), preset = mapPresetForMode(cfg.preset || (mode === 'cal' ? 'mtd' : '30d'), mode);
    var todayMs = toUtcDayMs(cfg.today);
    if (!Number.isFinite(todayMs)) todayMs = toUtcDayMs(Date.now());
    var minMs = toUtcDayMs(cfg.minDate), maxMs = toUtcDayMs(cfg.maxDate);
    if (Number.isFinite(minMs) && Number.isFinite(maxMs) && minMs > maxMs) { var sw = minMs; minMs = maxMs; maxMs = sw; }
    var rawAnchor = toUtcDayMs(cfg.anchorDate);
    var endMs = Number.isFinite(rawAnchor) ? rawAnchor : (Number.isFinite(maxMs) ? maxMs : todayMs);
    var step = Number(cfg.stepDelta || 0);
    var stepSpan = mode === 'rolling' ? (ROLLING_SPECS[preset] ? ROLLING_SPECS[preset][1] : 30) : (preset === 'wtd' ? 7 : 14);
    if (step && preset !== 'all' && preset !== 'all_scanned') {
      var curStart = mode === 'rolling' ? (endMs - (stepSpan - 1) * DAY_MS) : calStartMs(endMs, preset);
      if (!(step < 0 && Number.isFinite(minMs) && curStart <= minMs)) {
        if (mode === 'cal' && preset === 'mtd') {
          var edm = new Date(endMs);
          endMs = Date.UTC(edm.getUTCFullYear(), edm.getUTCMonth() + step + 1, 0);
        } else if (mode === 'cal' && preset === 'qtd') {
          var edq = new Date(endMs);
          endMs = Date.UTC(edq.getUTCFullYear(), (Math.floor(edq.getUTCMonth() / 3) + step + 1) * 3, 0);
        } else if (mode === 'cal' && preset === 'ytd') {
          var edy = new Date(endMs);
          endMs = Date.UTC(edy.getUTCFullYear() + step, 11, 31);
        } else if (mode === 'cal' && step < 0) {
          endMs = curStart + (step + 1) * stepSpan * DAY_MS - DAY_MS;
        } else {
          endMs += step * stepSpan * DAY_MS;
        }
      }
    }
    if (Number.isFinite(maxMs) && endMs > maxMs) endMs = maxMs;
    if (Number.isFinite(minMs) && endMs < minMs) endMs = minMs;
    var rawStart = (preset === 'all' || preset === 'all_scanned') ? (Number.isFinite(minMs) ? minMs : endMs)
      : (mode === 'rolling' ? (endMs - (ROLLING_SPECS[preset][1] - 1) * DAY_MS) : calStartMs(endMs, preset));
    var startMs = (Number.isFinite(minMs) && rawStart < minMs) ? minMs : rawStart;
    if (startMs > endMs) startMs = endMs;
    var isCapped = Number.isFinite(maxMs) && Number.isFinite(todayMs) && maxMs < todayMs;
    var effMax = Number.isFinite(maxMs) ? maxMs : todayMs;
    return {
      mode: mode, preset: preset, label: formatPresetLabel(preset, mode),
      startDate: fmtUtcDay(startMs), endDate: fmtUtcDay(endMs),
      spanDays: Math.max(1, Math.round((endMs - startMs) / DAY_MS) + 1),
      anchorLabel: isCapped ? 'Latest Scanned' : 'Today', isCorpusCapped: isCapped,
      atLatest: endMs >= effMax, canStepPrev: !Number.isFinite(minMs) || startMs > minMs, canStepNext: endMs < effMax,
    };
  }

  var api = {
    parseUtcMs: parseUtcMs,
    binTimeSeries: binTimeSeries,
    trimTrailingFutureWeeks: trimTrailingFutureWeeks,
    resolveCssColor: resolveCssColor,
    heatmapZeroCellStyle: heatmapZeroCellStyle,
    mapPresetForMode: mapPresetForMode,
    formatPresetLabel: formatPresetLabel,
    resolvePeriodBounds: resolvePeriodBounds,
  };
  root.QuietTimeBinning = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
