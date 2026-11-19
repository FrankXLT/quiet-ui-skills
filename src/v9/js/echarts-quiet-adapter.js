/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet Evidence — Runtime Apache ECharts (SVG) + 5-Tab Ecosystem Viewer */
(function (global) {
  'use strict';

  var AUTO_VIEWS = {
    'v06-ai-drift-and-lineage-ide': true,
    'v10-civic-capital-budget-deck': true,
    'v11-treasury-stress-test-solver': true,
    'v12-stem-interactive-lab': true,
    'v13-propulsion-archival-monograph': true,
    'v18-home-assistant-companion-console': true,
  };
  var PALETTE_TOKENS = ['--accent-focal', '--status-warn', '--text-secondary', '--status-danger'];
  var ROOT_LISTENERS = new WeakSet();
  var RESIZE_OBSERVERS = new WeakMap();
  var COPY_TIMERS = new WeakMap();

  function getLib() {
    if (global.echarts) return global.echarts;
    try {
      if (global.parent && global.parent !== global && global.parent.echarts) {
        return global.parent.echarts;
      }
    } catch (_err) {}
    return null;
  }

  function cssVar(doc, token, fallback) {
    try {
      var val = getComputedStyle(doc.documentElement).getPropertyValue(token).trim();
      if (val) return val;
    } catch (_err) {}
    return fallback;
  }

  function readTokens(doc) {
    return {
      textPrimary: cssVar(doc, '--text-primary', '#0F172A'),
      textSecondary: cssVar(doc, '--text-secondary', '#475569'),
      borderHairline: cssVar(doc, '--border-hairline', '#E2E8F0'),
      borderStrong: cssVar(doc, '--border-strong', '#94A3B8'),
      bgSurface: cssVar(doc, '--bg-surface', '#FFFFFF'),
      bgElevated: cssVar(doc, '--bg-elevated', '#F8FAFC'),
      accentFocal: cssVar(doc, '--accent-focal', '#0369A1'),
      statusWarn: cssVar(doc, '--status-warn', '#B45309'),
      statusDanger: cssVar(doc, '--status-danger', '#B91C1C'),
    };
  }

  function fmtLinearTick(v) {
    if (!Number.isFinite(v)) return '';
    if (Math.abs(v) < 1e-12) return '0';
    return String(Number(v.toPrecision(6)));
  }

  function resolveSeriesColor(doc, seriesSpec, idx, tokens) {
    var rawTok = seriesSpec && (seriesSpec.color || seriesSpec.token) ? (seriesSpec.color || seriesSpec.token) : PALETTE_TOKENS[idx % PALETTE_TOKENS.length];
    if (rawTok.indexOf('var(') === 0) rawTok = rawTok.slice(4, -1).split(',')[0].trim();
    if (rawTok.indexOf('#') === 0) return rawTok;
    if (rawTok === '--accent-focal' && idx > 0) rawTok = PALETTE_TOKENS[idx % PALETTE_TOKENS.length];
    var fallback = tokens.accentFocal;
    if (rawTok === '--status-warn') fallback = tokens.statusWarn;
    else if (rawTok === '--status-danger') fallback = tokens.statusDanger;
    else if (rawTok === '--text-secondary') fallback = tokens.textSecondary;
    else if (rawTok === '--text-primary') fallback = tokens.textPrimary;
    return cssVar(doc, rawTok, fallback);
  }

  function mapSymbol(glyph) {
    if (glyph === 'square') return 'rect';
    if (glyph === 'diamond') return 'diamond';
    if (glyph === 'triangle') return 'triangle';
    return 'circle';
  }

  function makeWhiskerSeries(name, color, pts, opacity, logY) {
    var coords = [];
    for (var i = 0; i < pts.length; i += 1) {
      var p = pts[i];
      if (p[1] !== null && p[1] !== undefined && p[2] > 0) {
        if (logY && p[1] <= 0) continue;
        coords.push([p[0], logY ? Math.max(p[1] * 1e-6, p[1] - p[2]) : (p[1] - p[2]), p[1] + p[2]]);
      }
    }
    if (!coords.length) return null;
    return {
      name: name + ' u',
      type: 'custom',
      silent: true,
      tooltip: { show: false },
      legendHoverLink: false,
      z: 3,
      renderItem: function (_params, api) {
        var xv = api.value(0);
        var low = api.coord([xv, api.value(1)]);
        var high = api.coord([xv, api.value(2)]);
        if (!low || !high || !Number.isFinite(low[0]) || !Number.isFinite(low[1]) || !Number.isFinite(high[0]) || !Number.isFinite(high[1])) return null;
        return {
          type: 'group',
          children: [
            { type: 'line', shape: { x1: low[0], y1: low[1], x2: high[0], y2: high[1] }, style: { stroke: color, lineWidth: 1.35, opacity: opacity } },
            { type: 'line', shape: { x1: high[0] - 4, y1: high[1], x2: high[0] + 4, y2: high[1] }, style: { stroke: color, lineWidth: 1.35, opacity: opacity } },
            { type: 'line', shape: { x1: low[0] - 4, y1: low[1], x2: low[0] + 4, y2: low[1] }, style: { stroke: color, lineWidth: 1.35, opacity: opacity } },
          ],
        };
      },
      data: coords,
    };
  }

  function buildEnvelopes(doc, payload, t) {
    return (payload.envelopes || []).map(function (env) {
      var col = cssVar(doc, env.token || '--status-warn', env.type === 'abort' ? t.statusDanger : t.statusWarn);
      return {
        name: env.label || String(env.value),
        yAxis: env.value,
        lineStyle: { color: col, type: env.type === 'abort' ? 'dashdot' : 'dashed', width: 1.4 },
        label: { formatter: env.label || String(env.value), position: 'insideEndTop', color: col, fontSize: 10.5, fontWeight: 600 },
      };
    });
  }

  function buildCartesianOption(doc, payload, activeTerm) {
    var t = readTokens(doc);
    var xMeta = payload.x || {};
    var yMeta = payload.y || {};
    var series = [];
    var envData = buildEnvelopes(doc, payload, t);

    (payload.series || []).forEach(function (sr, idx) {
      var col = resolveSeriesColor(doc, sr, idx, t);
      var dimmed = activeTerm && sr.term && sr.term !== activeTerm;
      var opacity = dimmed ? 0.22 : 1.0;
      if (sr.epistemic === 'analytical_model') {
        series.push({
          id: sr.id || 'model-' + idx,
          name: sr.name || 'Model',
          type: 'line',
          showSymbol: false,
          smooth: false,
          data: sr.data || [],
          lineStyle: { color: col, width: dimmed ? 1.5 : 2.1, type: sr.dashed ? 'dashed' : 'solid', opacity: opacity },
          itemStyle: { color: col, opacity: opacity },
          z: 2,
        });
      } else {
        series.push({
          id: sr.id || 'meas-' + idx,
          name: sr.name || 'Measurement',
          type: 'line',
          connectNulls: false,
          showSymbol: true,
          symbol: mapSymbol(sr.symbol),
          symbolSize: 6.5,
          smooth: false,
          data: (sr.data || []).map(function (p) { return [p[0], p[1]]; }),
          lineStyle: { color: col, width: sr.connect === false ? 0 : (dimmed ? 1.5 : 2.1), opacity: opacity },
          itemStyle: { color: col, opacity: opacity },
          z: 4,
        });
        var whisker = makeWhiskerSeries(sr.name || 'meas', col, sr.data || [], opacity, !!yMeta.log);
        if (whisker) series.push(whisker);
      }
    });

    if (series.length && envData.length) series[0].markLine = { silent: true, symbol: ['none', 'none'], data: envData };
    return {
      animation: false,
      backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Inter, system-ui, sans-serif', color: t.textPrimary },
      tooltip: { trigger: 'axis', renderMode: 'richText', confine: true, backgroundColor: t.bgElevated, borderColor: t.borderStrong, borderWidth: 1, textStyle: { color: t.textPrimary, fontSize: 12 } },
      legend: { top: 2, left: 64, right: 16, itemWidth: 16, itemHeight: 8, textStyle: { color: t.textSecondary, fontSize: 11 }, data: (payload.series || []).map(function (s) { return s.name; }) },
      grid: { left: 66, right: 24, top: 44, bottom: 52, containLabel: true },
      xAxis: {
        type: xMeta.log ? 'log' : 'value',
        min: (xMeta.log && xMeta.min <= 0) || !Number.isFinite(xMeta.min) ? undefined : xMeta.min,
        max: (xMeta.log && xMeta.max <= 0) || !Number.isFinite(xMeta.max) ? undefined : xMeta.max,
        interval: !xMeta.log && Number.isFinite(xMeta.interval) ? xMeta.interval : undefined,
        name: xMeta.name || 'x',
        nameLocation: 'middle',
        nameGap: 28,
        nameTextStyle: { color: t.textSecondary, fontSize: 11.5, fontWeight: 600 },
        axisLine: { onZero: false, lineStyle: { color: t.textSecondary } },
        axisLabel: { color: t.textSecondary, fontSize: 11, hideOverlap: true, formatter: xMeta.log ? undefined : fmtLinearTick },
        splitLine: { lineStyle: { color: t.borderHairline, type: 'dashed' } },
      },
      yAxis: {
        type: yMeta.log ? 'log' : 'value',
        min: (yMeta.log && yMeta.min <= 0) || !Number.isFinite(yMeta.min) ? undefined : yMeta.min,
        max: (yMeta.log && yMeta.max <= 0) || !Number.isFinite(yMeta.max) ? undefined : yMeta.max,
        interval: !yMeta.log && Number.isFinite(yMeta.interval) ? yMeta.interval : undefined,
        name: yMeta.name || 'y',
        nameLocation: 'middle',
        nameGap: 44,
        nameTextStyle: { color: t.textSecondary, fontSize: 11.5, fontWeight: 600 },
        axisLine: { lineStyle: { color: t.textSecondary } },
        axisLabel: { color: t.textSecondary, fontSize: 11, hideOverlap: true, formatter: yMeta.log ? undefined : fmtLinearTick },
        splitLine: { lineStyle: { color: t.borderHairline, type: 'dashed' } },
      },
      series: series,
    };
  }

  function buildWaterfallOption(doc, payload) {
    var t = readTokens(doc);
    var yMeta = payload.y || {};
    return {
      animation: false,
      backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Inter, system-ui, sans-serif', color: t.textPrimary },
      tooltip: { trigger: 'axis', renderMode: 'richText', confine: true, backgroundColor: t.bgElevated, borderColor: t.borderStrong, textStyle: { color: t.textPrimary, fontSize: 12 } },
      legend: { top: 2, left: 64, textStyle: { color: t.textSecondary, fontSize: 11 }, data: ['Increase', 'Reduction / Cost'] },
      grid: { left: 66, right: 22, top: 42, bottom: 54, containLabel: true },
      xAxis: { type: 'category', data: payload.categories || [], axisLine: { onZero: false, lineStyle: { color: t.textSecondary } }, axisLabel: { color: t.textSecondary, fontSize: 11, interval: 0, hideOverlap: true } },
      yAxis: {
        type: 'value',
        min: Number.isFinite(yMeta.min) ? yMeta.min : undefined,
        max: Number.isFinite(yMeta.max) ? yMeta.max : undefined,
        interval: Number.isFinite(yMeta.interval) ? yMeta.interval : undefined,
        name: yMeta.name || payload.yName || 'Value',
        nameLocation: 'middle',
        nameGap: 44,
        nameTextStyle: { color: t.textSecondary, fontSize: 11.5, fontWeight: 600 },
        axisLine: { lineStyle: { color: t.textSecondary } },
        axisLabel: { color: t.textSecondary, fontSize: 11, hideOverlap: true, formatter: fmtLinearTick },
        splitLine: { lineStyle: { color: t.borderHairline, type: 'dashed' } },
      },
      series: [
        { name: 'Base', type: 'bar', stack: 'wf', silent: true, itemStyle: { color: 'transparent' }, data: payload.bases || [] },
        { name: 'Increase', type: 'bar', stack: 'wf', itemStyle: { color: t.accentFocal }, data: payload.positive || [] },
        { name: 'Reduction / Cost', type: 'bar', stack: 'wf', itemStyle: { color: t.statusWarn }, data: payload.negative || [] },
      ],
    };
  }

  function buildStackedBarOption(doc, payload) {
    var t = readTokens(doc);
    var yMeta = payload.y || {};
    var envData = buildEnvelopes(doc, payload, t);
    var series = (payload.series || []).map(function (sr, idx) {
      var col = resolveSeriesColor(doc, sr, idx, t);
      if (sr.seriesType === 'line') {
        return { id: sr.id, name: sr.name, type: 'line', showSymbol: false, symbol: 'circle', symbolSize: 5, smooth: false, data: sr.data || [], lineStyle: { color: col, width: 2.2 }, itemStyle: { color: col }, z: 5 };
      }
      return { id: sr.id, name: sr.name, type: 'bar', stack: sr.stack || 'energy', barMaxWidth: 20, itemStyle: { color: col, borderRadius: [1.5, 1.5, 1.5, 1.5] }, data: sr.data || [], z: 3 };
    });
    if (series.length && envData.length) series[0].markLine = { silent: true, symbol: ['none', 'none'], data: envData };
    return {
      animation: false,
      backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Inter, system-ui, sans-serif', color: t.textPrimary },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, renderMode: 'richText', confine: true, backgroundColor: t.bgElevated, borderColor: t.borderStrong, borderWidth: 1, textStyle: { color: t.textPrimary, fontSize: 12 } },
      legend: { top: 2, left: 48, right: 12, itemWidth: 14, itemHeight: 8, textStyle: { color: t.textSecondary, fontSize: 11 }, data: (payload.series || []).map(function (s) { return s.name; }) },
      grid: { left: 56, right: 20, top: 48, bottom: 48, containLabel: true },
      xAxis: {
        type: 'category',
        data: payload.categories || [],
        name: (payload.x || {}).name || 'Hour of Day',
        nameLocation: 'middle',
        nameGap: 26,
        nameTextStyle: { color: t.textSecondary, fontSize: 11, fontWeight: 600 },
        axisLine: { onZero: true, lineStyle: { color: t.textSecondary } },
        axisLabel: { color: t.textSecondary, fontSize: 11, interval: function (i) { return i % 4 === 0; } },
      },
      yAxis: {
        type: 'value',
        min: Number.isFinite(yMeta.min) ? yMeta.min : undefined,
        max: Number.isFinite(yMeta.max) ? yMeta.max : undefined,
        interval: Number.isFinite(yMeta.interval) ? yMeta.interval : undefined,
        name: yMeta.name || 'Power (kW)',
        nameLocation: 'middle',
        nameGap: 40,
        nameTextStyle: { color: t.textSecondary, fontSize: 11, fontWeight: 600 },
        axisLine: { lineStyle: { color: t.textSecondary } },
        axisLabel: { color: t.textSecondary, fontSize: 11, hideOverlap: true, formatter: fmtLinearTick },
        splitLine: { lineStyle: { color: t.borderHairline, type: 'dashed' } },
      },
      series: series,
    };
  }

  function shouldEnableECharts(doc, wrap) {
    var rootMed = (doc.documentElement.dataset.medium || '').toLowerCase();
    var wrapMed = (wrap.dataset.medium || '').toLowerCase();
    if (rootMed === 'm1' || wrapMed === 'm1') return false;
    if (doc.defaultView && doc.defaultView.matchMedia && doc.defaultView.matchMedia('print').matches) return false;
    if (wrap.dataset.echartsMode === 'svg') return false;
    if (wrap.dataset.echartsMode === 'echarts') return true;
    return !!AUTO_VIEWS[doc.documentElement.dataset.view || ''];
  }

  function disposeWrap(wrap, lib) {
    var host = wrap.querySelector('.qe-echarts-host');
    if (host) {
      if (lib && typeof lib.getInstanceByDom === 'function') {
        var existing = lib.getInstanceByDom(host);
        if (existing) existing.dispose();
      }
      host.hidden = true;
    }
    wrap.dataset.echartsActive = 'false';
  }

  function mountWrap(doc, wrap, lib) {
    var host = wrap.querySelector('.qe-echarts-host');
    var scroll = wrap.querySelector('.va-figure-scroll');
    if (!host || !scroll || !lib || !shouldEnableECharts(doc, wrap)) { disposeWrap(wrap, lib); return; }
    var payload;
    try { payload = JSON.parse(wrap.dataset.quietEcharts || ''); } catch (_err) { disposeWrap(wrap, lib); return; }
    host.hidden = false;
    var w = Math.max(300, Math.round((scroll.clientWidth || wrap.clientWidth || 640) - 8));
    var h = Math.round(w < 500 ? 255 : Math.min(340, Math.max(255, w * 0.44)));
    host.style.width = w + 'px';
    host.style.height = h + 'px';
    var inst = lib.getInstanceByDom(host) || lib.init(host, null, { renderer: 'svg', width: w, height: h });
    var opt = payload.kind === 'waterfall' ? buildWaterfallOption(doc, payload) : (payload.kind === 'stacked_bar' ? buildStackedBarOption(doc, payload) : buildCartesianOption(doc, payload, wrap.dataset.activeTerm || ''));
    inst.setOption(opt, true);
    inst.resize({ width: w, height: h });
    wrap.dataset.echartsActive = 'true';
  }

  function activateEcoTab(tabBtn) {
    var wrap = tabBtn && tabBtn.closest('.qe-eco-drawer');
    if (!wrap) return;
    var targetId = tabBtn.getAttribute('aria-controls');
    wrap.querySelectorAll('.qe-eco-tab[role="tab"]').forEach(function (t) {
      var on = t === tabBtn;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
    });
    wrap.querySelectorAll('.qe-eco-panel[role="tabpanel"]').forEach(function (p) {
      if (p.id === targetId) p.removeAttribute('hidden');
      else p.setAttribute('hidden', 'until-found');
    });
  }

  function copyEcoSnippet(btn) {
    var drawer = btn && btn.closest('.qe-eco-drawer');
    if (!drawer) return;
    var panel = drawer.querySelector('.qe-eco-panel:not([hidden]) pre');
    var status = drawer.querySelector('.qe-copy-status');
    var txt = panel ? panel.textContent : '';
    var done = function (msg) {
      if (!status) return;
      clearTimeout(COPY_TIMERS.get(status));
      status.textContent = msg;
      status.classList.add('is-visible');
      COPY_TIMERS.set(status, setTimeout(function () { status.classList.remove('is-visible'); status.textContent = ''; }, 2000));
    };
    var fallbackCopy = function () {
      var d = drawer.ownerDocument || global.document;
      if (!d || !d.body || typeof d.execCommand !== 'function') { done('Copy failed'); return; }
      var ta = d.createElement('textarea');
      ta.value = txt; ta.readOnly = true;
      ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;left:-9999px';
      d.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = !!d.execCommand('copy'); } catch (_err) {}
      d.body.removeChild(ta);
      if (btn && btn.focus) btn.focus();
      done(ok ? 'Copied' : 'Copy failed');
    };
    if (global.navigator && global.navigator.clipboard && global.navigator.clipboard.writeText) {
      global.navigator.clipboard.writeText(txt).then(function () { done('Copied'); }, fallbackCopy);
    } else { fallbackCopy(); }
  }

  function bindEvents(doc) {
    if (!ROOT_LISTENERS.has(doc)) {
      ROOT_LISTENERS.add(doc);
      doc.addEventListener('click', function (ev) {
        var btn = ev.target && ev.target.closest ? ev.target.closest('.qe-mode-btn[data-qe-mode]') : null;
        if (btn) {
          var mode = btn.dataset.qeMode || 'svg';
          var wrap = btn.closest('.qe-plot-wrap');
          if (wrap) {
            wrap.dataset.echartsMode = mode;
            wrap.querySelectorAll('.qe-mode-btn[data-qe-mode]').forEach(function (b) {
              var on = b.dataset.qeMode === mode;
              b.classList.toggle('is-active', on);
              b.setAttribute('aria-pressed', on ? 'true' : 'false');
            });
            boot(doc);
          }
          return;
        }
        var ecoTab = ev.target && ev.target.closest ? ev.target.closest('.qe-eco-tab[role="tab"]') : null;
        if (ecoTab) { activateEcoTab(ecoTab); return; }
        var copyBtn = ev.target && ev.target.closest ? ev.target.closest('.qe-copy-btn') : null;
        if (copyBtn) { copyEcoSnippet(copyBtn); return; }
        var termBtn = ev.target && ev.target.closest ? ev.target.closest('[data-term]') : null;
        if (termBtn) {
          var term = termBtn.dataset.term || '';
          doc.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]').forEach(function (w) { w.dataset.activeTerm = w.dataset.activeTerm === term ? '' : term; });
          boot(doc);
        }
      });
      doc.addEventListener('keydown', function (ev) {
        var tab = ev.target && ev.target.closest ? ev.target.closest('.qe-eco-tab[role="tab"]') : null;
        if (!tab) return;
        var list = tab.closest('[role="tablist"]');
        var tabs = list ? Array.prototype.slice.call(list.querySelectorAll('.qe-eco-tab[role="tab"]')) : [];
        var idx = tabs.indexOf(tab);
        if (idx < 0) return;
        var nxt = ev.key === 'ArrowRight' ? (idx + 1) % tabs.length : (ev.key === 'ArrowLeft' ? (idx - 1 + tabs.length) % tabs.length : (ev.key === 'Home' ? 0 : (ev.key === 'End' ? tabs.length - 1 : -1)));
        if (nxt >= 0) { ev.preventDefault(); activateEcoTab(tabs[nxt]); tabs[nxt].focus(); }
      });
      doc.addEventListener('beforematch', function (ev) {
        var panel = ev.target && ev.target.closest ? ev.target.closest('.qe-eco-panel[role="tabpanel"]') : null;
        var tid = panel && panel.getAttribute('aria-labelledby');
        if (tid) activateEcoTab(doc.getElementById(tid));
      }, true);
    }
    if (!RESIZE_OBSERVERS.has(doc) && typeof global.ResizeObserver === 'function') {
      var ro = new global.ResizeObserver(function () { refresh(doc); });
      if (doc.body) ro.observe(doc.body);
      RESIZE_OBSERVERS.set(doc, ro);
    }
  }

  function boot(docRef) {
    var doc = docRef || global.document;
    if (!doc) return;
    bindEvents(doc);
    var lib = getLib();
    doc.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]').forEach(function (w) { mountWrap(doc, w, lib); });
  }

  function refresh(docRef) {
    var doc = docRef || global.document;
    if (!doc) return;
    var lib = getLib();
    doc.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]').forEach(function (w) { mountWrap(doc, w, lib); });
  }

  function disposeAll(docRef) {
    var doc = docRef || global.document;
    if (!doc) return;
    var ro = RESIZE_OBSERVERS.get(doc);
    if (ro) { ro.disconnect(); RESIZE_OBSERVERS.delete(doc); }
    var lib = getLib();
    doc.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]').forEach(function (w) { disposeWrap(w, lib); });
  }

  global.QuietEChartsAdapter = { boot: boot, refresh: refresh, disposeAll: disposeAll };
}(window));
