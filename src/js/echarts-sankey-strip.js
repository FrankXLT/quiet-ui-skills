/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet Evidence — Live Apache ECharts Builders for Flow Sankey & Multi-Track Strip Charts */
(function (global) {
  'use strict';

  function cssVar(doc, token, fallback) {
    try {
      var val = getComputedStyle(doc.documentElement).getPropertyValue(token).trim();
      if (val) return val;
    } catch (_err) {}
    return fallback;
  }

  function resolveTok(doc, rawTok, tokens) {
    var tok = String(rawTok || '--accent-focal');
    if (tok.indexOf('var(') === 0) tok = tok.slice(4, -1).split(',')[0].trim();
    if (tok.indexOf('#') === 0) return tok;
    var fb = tok === '--status-ok' ? tokens.statusOk : (tok === '--status-warn' ? tokens.statusWarn : (tok === '--status-danger' ? tokens.statusDanger : (tok === '--text-secondary' ? tokens.textSecondary : tokens.accentFocal)));
    return cssVar(doc, tok, fb);
  }

  function fmtVal(v) {
    return !Number.isFinite(v) ? '0' : (Math.abs(v) >= 10 ? v.toFixed(1) : Number(v.toFixed(2)).toString());
  }

  function calcHeight(payload, w) {
    if (!payload) return 300;
    if (payload.kind === 'strip_chart') {
      var n = Array.isArray(payload.tracks) ? payload.tracks.length : 3;
      return (w < 500 ? 78 : 88) * Math.max(1, n) + 86;
    }
    return w < 500 ? 276 : Math.round(Math.min(340, Math.max(280, w * 0.44)));
  }

  function buildSankeyOption(doc, payload, tokens, hostW) {
    var narrow = (hostW || 640) < 500;
    var unit = payload.unit ? ' ' + payload.unit : '';
    var total = payload.totalFlow || 1;
    var nodes = payload.nodes || [];
    var maxStage = nodes.reduce(function (m, n) { return Math.max(m, n.stage || 0); }, 0);
    var data = nodes.map(function (n) {
      return { name: n.name, value: n.value, depth: n.stage || 0, itemStyle: { color: resolveTok(doc, n.token, tokens), borderColor: tokens.bgSurface, borderWidth: 1 } };
    });
    var levels = [];
    for (var s = 0; s <= maxStage; s += 1) {
      levels.push({
        depth: s,
        label: {
          position: (s === maxStage && maxStage > 0) ? 'left' : 'right',
          color: tokens.textPrimary, fontSize: 11.5, fontWeight: 600,
          formatter: function (p) {
            var v = Number((p.data && p.data.value) != null ? p.data.value : (p.value || 0));
            var pct = ((v / total) * 100).toFixed(1);
            return narrow ? (p.name + ' (' + pct + '%)') : (p.name + '\n' + fmtVal(v) + unit + ' (' + pct + '%)');
          },
        },
      });
    }
    return {
      animation: false, backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Inter, system-ui, sans-serif', color: tokens.textPrimary },
      tooltip: {
        trigger: 'item', renderMode: 'richText', confine: true,
        backgroundColor: tokens.bgElevated, borderColor: tokens.borderStrong, borderWidth: 1,
        textStyle: { color: tokens.textPrimary, fontSize: 12 },
        formatter: function (p) {
          var d = p.data || {};
          if (p.dataType === 'edge') {
            var pct = ((Number(d.value || 0) / total) * 100).toFixed(1);
            return d.source + ' → ' + d.target + '\n' + fmtVal(Number(d.value || 0)) + unit + ' (' + pct + '%)';
          }
          var nv = Number(d.value != null ? d.value : (p.value || 0));
          return p.name + '\n' + fmtVal(nv) + unit + ' (' + ((nv / total) * 100).toFixed(1) + '%)';
        },
      },
      series: [{
        type: 'sankey', left: 16, right: 20, top: 18, bottom: 18,
        nodeWidth: 14, nodeGap: 18, draggable: false, layoutIterations: 0,
        emphasis: { focus: 'adjacency', lineStyle: { opacity: 0.72 } },
        lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.34 },
        levels: levels, data: data, links: payload.links || [],
      }],
    };
  }

  function appendStripTrack(doc, tr, i, n, layout, xMeta, tokens, out) {
    var gy = Math.round(layout.topPad + i * layout.laneStep + 14);
    var col = resolveTok(doc, tr.token, tokens);
    var isLast = i === n - 1;
    out.grids.push({ left: layout.leftPad, right: layout.rightPad, top: gy, height: layout.laneH, containLabel: false });
    out.xAxes.push({
      type: 'value', gridIndex: i, min: xMeta.min, max: xMeta.max, interval: xMeta.interval,
      axisLine: { lineStyle: { color: tokens.borderStrong } }, axisTick: { show: isLast },
      axisLabel: { show: isLast, color: tokens.textSecondary, fontSize: 11 },
      splitLine: { show: true, lineStyle: { color: tokens.borderHairline, type: 'dashed' } },
      name: isLast ? (xMeta.name || 't / s') : '', nameLocation: 'middle', nameGap: 21,
      nameTextStyle: { color: tokens.textPrimary, fontSize: 11, fontWeight: 700 },
    });
    out.yAxes.push({
      type: 'value', gridIndex: i, min: tr.min, max: tr.max, interval: tr.interval,
      axisLine: { show: true, lineStyle: { color: tokens.borderStrong } },
      axisLabel: { color: tokens.textSecondary, fontSize: 11 },
      splitLine: { lineStyle: { color: tokens.borderHairline, type: 'dotted' } },
    });
    var thr = [];
    if (tr.warnHigh != null) thr.push({ yAxis: tr.warnHigh, lineStyle: { color: tokens.statusWarn, type: 'dashed', width: 1.2 } });
    if (tr.warnLow != null) thr.push({ yAxis: tr.warnLow, lineStyle: { color: tokens.statusWarn, type: 'dashed', width: 1.2 } });
    var nom = Array.isArray(tr.nominalBand) && tr.nominalBand.length === 2 ? tr.nominalBand : null;
    out.series.push({
      id: tr.id, name: tr.name, type: 'line', xAxisIndex: i, yAxisIndex: i, showSymbol: false, smooth: false,
      data: tr.data || [], lineStyle: { color: col, width: 1.7 }, itemStyle: { color: col },
      markArea: nom ? { silent: true, itemStyle: { color: tokens.statusOk, opacity: 0.09 }, data: [[{ yAxis: nom[0] }, { yAxis: nom[1] }]] } : undefined,
      markLine: thr.length ? { silent: true, symbol: ['none', 'none'], label: { show: false }, data: thr } : undefined, z: 3,
    });
    if (tr.breached) {
      var exc = (tr.data || []).map(function (pt) {
        var v = pt[1];
        return ((tr.warnHigh != null && v > tr.warnHigh) || (tr.warnLow != null && v < tr.warnLow)) ? [pt[0], v] : [pt[0], null];
      });
      out.series.push({
        id: tr.id + '-exc', name: tr.name + ' excursion', type: 'line', xAxisIndex: i, yAxisIndex: i,
        connectNulls: false, showSymbol: false, silent: true, tooltip: { show: false },
        data: exc, lineStyle: { color: tokens.statusWarn, width: 2.5 }, z: 4,
      });
    }
    out.graphics.push({
      type: 'text', left: layout.leftPad + 2, top: gy - 14, silent: true,
      style: { text: tr.name + ' (' + tr.calculus + ')', fill: tokens.textPrimary, font: '600 11px Inter, system-ui, sans-serif' },
    });
    var gx = layout.w - layout.rightPad + 8, gw = Math.max(96, layout.rightPad - 12);
    var unitS = tr.unit ? ' ' + tr.unit : '';
    var isLow = tr.warnLow != null && tr.minVal < tr.warnLow;
    var pfx = layout.narrow ? (isLow ? 'Lo ' : 'Hi ') : (isLow ? 'Min ' : 'Peak ');
    var extTxt = pfx + fmtVal(isLow ? tr.minVal : tr.peak) + unitS;
    var stCol = tr.breached ? tokens.statusWarn : tokens.statusOk;
    out.graphics.push({
      type: 'group', left: gx, top: gy,
      children: [
        { type: 'rect', shape: { x: 0, y: 0, width: gw, height: layout.laneH, r: 4 }, style: { fill: tokens.bgElevated, stroke: tr.breached ? tokens.statusWarn : tokens.borderStrong, lineWidth: 1.1 } },
        { type: 'text', style: { x: 8, y: 8, textVerticalAlign: 'top', text: tr.breached ? 'EXCURSION' : 'NOMINAL', fill: stCol, font: '700 11px JetBrains Mono, monospace' } },
        { type: 'text', style: { x: 8, y: Math.round(layout.laneH * 0.50), textVerticalAlign: 'middle', text: fmtVal(tr.current) + unitS, fill: tokens.textPrimary, font: '700 12px JetBrains Mono, monospace' } },
        { type: 'text', style: { x: 8, y: layout.laneH - 8, textVerticalAlign: 'bottom', text: extTxt, fill: tr.breached ? stCol : tokens.textSecondary, font: '600 11px JetBrains Mono, monospace' } },
      ],
    });
  }

  function buildStripChartOption(doc, payload, tokens, hostW) {
    var tracks = payload.tracks || [], n = tracks.length;
    if (!n) return { animation: false, series: [] };
    var w = hostW || 640, narrow = w < 520, h = calcHeight(payload, w);
    var layout = { w: w, narrow: narrow, leftPad: narrow ? 46 : 62, rightPad: narrow ? 112 : 136, topPad: 14, botPad: 68 };
    layout.laneStep = (h - layout.topPad - layout.botPad) / n;
    layout.laneH = Math.max(38, layout.laneStep - 20);
    var xMeta = payload.x || {}, allIdx = [], unitMap = {};
    var out = { grids: [], xAxes: [], yAxes: [], series: [], graphics: [] };
    tracks.forEach(function (tr, i) { allIdx.push(i); unitMap[tr.id] = tr.unit ? (' ' + tr.unit) : ''; appendStripTrack(doc, tr, i, n, layout, xMeta, tokens, out); });
    return {
      animation: false, backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Inter, system-ui, sans-serif', color: tokens.textPrimary },
      tooltip: {
        trigger: 'axis', renderMode: 'richText', confine: true,
        backgroundColor: tokens.bgElevated, borderColor: tokens.borderStrong, borderWidth: 1,
        textStyle: { color: tokens.textPrimary, fontSize: 11.5 },
        formatter: function (params) {
          var list = (params || []).filter(function (p) { return p.seriesId && p.seriesId.slice(-4) !== '-exc'; });
          if (!list.length) return '';
          var tVal = list[0].value ? list[0].value[0] : '';
          var lines = ['t = ' + tVal + ' ' + (xMeta.unit || 's')];
          list.forEach(function (p) { lines.push(p.seriesName + ': ' + fmtVal(Number(p.value[1])) + (unitMap[p.seriesId] || '')); });
          return lines.join('\n');
        },
      },
      axisPointer: { link: [{ xAxisIndex: 'all' }], lineStyle: { color: tokens.accentFocal, width: 1.2, type: 'dashed' } },
      dataZoom: [
        { type: 'inside', xAxisIndex: allIdx },
        { type: 'slider', xAxisIndex: allIdx, left: layout.leftPad, right: layout.rightPad, bottom: 8, height: 20, borderColor: tokens.borderStrong },
      ],
      grid: out.grids, xAxis: out.xAxes, yAxis: out.yAxes, graphic: out.graphics, series: out.series,
    };
  }

  global.QuietEChartsSankeyStrip = {
    calcHeight: calcHeight,
    buildOption: function (doc, payload, tokens, hostW) {
      if (payload.kind === 'sankey') return buildSankeyOption(doc, payload, tokens, hostW);
      if (payload.kind === 'strip_chart') return buildStripChartOption(doc, payload, tokens, hostW);
      return null;
    },
  };
}(typeof window !== 'undefined' ? window : this));
