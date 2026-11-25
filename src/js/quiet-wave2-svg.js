/* Quiet UI v9.7.0 Wave 3 — Plumb-Line Responsive SVG Renderer (1:1 text scale, zero mobile scroll) */
(function (global) {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var V23_COHORTS = [
    ['ewr-edge-01 (Canary 1)', 'Canary r42', 7.4, 'var(--accent-focal)', '0.14'],
    ['fra-edge-02 (Canary 2)', 'Canary r42', 6.9, 'var(--accent-focal)', '0.14'],
    ['NA West/Central (5 clusters)', 'Held r41', 36.1, 'var(--text-muted)', '0.06'],
    ['EU Core (4 clusters)', 'Held r41', 28.8, 'var(--text-muted)', '0.06'],
    ['APAC Edge (3 clusters)', 'Held r41', 20.8, 'var(--text-muted)', '0.06'],
  ];

  var V24_BUCKETS = [
    ['14:00', 0, 0, 0, 1], ['14:02', 0, 1, 0, 1], ['14:05', 0, 0, 1, 0], ['14:07', 0, 1, 0, 1],
    ['14:10', 0, 0, 1, 0], ['14:12', 0, 1, 0, 1], ['14:15', 0, 1, 1, 0], ['14:17', 0, 1, 1, 0],
    ['14:20', 2, 1, 1, 0], ['14:22', 2, 2, 0, 0], ['14:25', 2, 1, 1, 0], ['14:27', 1, 1, 1, 0],
    ['14:30', 1, 1, 0, 0], ['14:32', 1, 1, 1, 0], ['14:35', 0, 1, 1, 0], ['14:37', 0, 0, 1, 1],
    ['14:40', 0, 1, 0, 1], ['14:42', 0, 0, 1, 1], ['14:45', 0, 0, 0, 1], ['14:47', 0, 0, 0, 1],
    ['14:50', 0, 0, 0, 2], ['14:52', 0, 0, 0, 1], ['14:55', 0, 0, 0, 1], ['14:57', 0, 0, 0, 1],
  ];

  var V25_PROFILE = [
    [0, 0], [68, -110], [140, -180], [210, -420], [240, -760], [302, -1180],
    [362, -1420], [440, -2940], [515, -3680], [585, -3850], [618, -1250], [640, 0],
  ];

  var V25_STATIONS = [
    [0, 0, 26.0, 'NOMINAL', 'shelf'], [68, -110, 24.2, 'NOMINAL', 'shelf'],
    [140, -180, 22.9, 'NOMINAL', 'shelf'], [210, -420, 21.8, 'NOMINAL', 'shelf'],
    [240, -760, 20.9, 'NOMINAL', 'branch'], [302, -1180, 20.1, 'NOMINAL', 'branch'],
    [362, -1420, 16.4, 'WARN', 'fault'], [440, -2940, 17.3, 'NOMINAL', 'deep'],
    [515, -3680, 17.8, 'NOMINAL', 'deep'], [640, 0, 18.2, 'NOMINAL', 'deep'],
  ];

  var V25_NODES = [
    [0, 0, 'shelf', 'NOMINAL', 'CLS-Alpha', 'CLS-Alpha', 'Alpha', 'start', 0, 22, 22],
    [68, -110, 'shelf', 'NOMINAL', 'Repeater R1', 'R1', 'R1', 'middle', 0, 58, 58],
    [140, -180, 'shelf', 'NOMINAL', 'Repeater R2', 'R2', 'R2', 'middle', 0, 22, 22],
    [210, -420, 'shelf', 'NOMINAL', 'Repeater R3', 'R3', 'R3', 'end', -9, 68, 72],
    [240, -760, 'branch', 'NOMINAL', 'BU-03', 'BU-03', 'BU-03', 'start', 9, 22, 22],
    [302, -1180, 'branch', 'NOMINAL', 'Repeater R4', 'R4', 'R4', 'end', -9, 96, 96],
    [362, -1420, 'fault', 'WARN', 'R5', 'R5', 'R5', 'end', -9, 108, 108],
    [440, -2940, 'deep', 'NOMINAL', 'Repeater R6', 'R6', 'R6', 'end', -6, 158, 154],
    [515, -3680, 'deep', 'NOMINAL', 'Repeater R7', 'R7', 'R7', 'end', -6, 186, 178],
    [585, -3850, 'deep', 'NOMINAL', 'Repeater R8', 'Repeater R8', 'R8', 'middle', 0, 198, 198],
    [640, 0, 'deep', 'NOMINAL', 'CLS-Bravo', 'CLS-Bravo', 'Bravo', 'end', 0, 22, 22],
  ];

  function el(doc, tag, attrs, text) {
    var node = doc.createElementNS(NS, tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) { node.setAttribute(k, String(attrs[k])); });
    }
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function clearSvg(svg) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
  }

  function clamp(lo, hi, v) {
    return Math.max(lo, Math.min(hi, v));
  }

  function applySpanFilter(node, grp, activeGrp) {
    if (!activeGrp || activeGrp === 'all') return;
    var mine = grp === activeGrp;
    node.setAttribute('data-span-dim', mine ? '0' : '1');
    node.setAttribute('data-span-hot', mine ? '1' : '0');
  }

  function renderV23Blast(svg, vw) {
    var doc = svg.ownerDocument, mob = vw < 560, h = mob ? 276 : 236;
    var ml = mob ? 2 : 196, mr = mob ? 6 : 136, pw = Math.max(120, vw - ml - mr);
    clearSvg(svg);
    svg.setAttribute('viewBox', '0 0 ' + vw + ' ' + h);
    svg.appendChild(el(doc, 'text', { x: 2, y: 16, 'font-size': '12', 'font-weight': '650', fill: 'var(--text-primary)' },
      mob ? 'Traffic Share by Cohort (14 Clusters)' : 'Traffic Share by Cluster Cohort (14 Edge Clusters)'));
    var y0 = mob ? 26 : 24, y1 = mob ? 250 : 210, yTick = mob ? 266 : 226;
    for (var i = 0; i <= 4; i += 1) {
      var gx = (ml + (i * pw) / 4).toFixed(1);
      svg.appendChild(el(doc, 'line', {
        x1: gx, y1: y0, x2: gx, y2: y1, stroke: 'var(--border-subtle)',
        'stroke-dasharray': i === 0 ? 'none' : '2 3',
      }));
      var anc = mob && i === 0 ? 'start' : (mob && i === 4 ? 'end' : 'middle');
      svg.appendChild(el(doc, 'text', { x: gx, y: yTick, 'text-anchor': anc, 'font-size': '11.5', fill: 'var(--text-muted)' }, (i * 10) + '%'));
    }
    V23_COHORTS.forEach(function (row, idx) {
      var bw = ((row[2] / 40) * pw).toFixed(1), valTxt = row[2].toFixed(1) + '% (' + row[1] + ')';
      if (mob) {
        var top = 40 + idx * 42;
        svg.appendChild(el(doc, 'text', { x: 2, y: top, 'font-size': '11.5', fill: 'var(--text-primary)' }, row[0]));
        svg.appendChild(el(doc, 'text', { x: vw - 2, y: top, 'text-anchor': 'end', 'font-size': '11.5', 'font-weight': '600', fill: 'var(--text-primary)' }, valTxt));
        svg.appendChild(el(doc, 'rect', { x: ml, y: top + 5, width: pw.toFixed(1), height: 15, rx: 3, fill: 'var(--text-muted)', opacity: row[4] }));
        svg.appendChild(el(doc, 'rect', { x: ml, y: top + 5, width: bw, height: 15, rx: 3, fill: row[3] }));
      } else {
        var y = 32 + idx * 36;
        svg.appendChild(el(doc, 'text', { x: 2, y: y + 15, 'font-size': '11.5', fill: 'var(--text-primary)' }, row[0]));
        svg.appendChild(el(doc, 'rect', { x: ml, y: y, width: pw.toFixed(1), height: 22, rx: 3, fill: 'var(--text-muted)', opacity: row[4] }));
        svg.appendChild(el(doc, 'rect', { x: ml, y: y, width: bw, height: 22, rx: 3, fill: row[3] }));
        svg.appendChild(el(doc, 'text', { x: vw - 2, y: y + 15, 'text-anchor': 'end', 'font-size': '11.5', 'font-weight': '600', fill: 'var(--text-primary)' }, valTxt));
      }
    });
  }

  function renderV24Hist(svg, vw) {
    var doc = svg.ownerDocument, mob = vw < 560, ml = 26, pw = Math.max(180, vw - ml - 8);
    var step = pw / 24, bw = clamp(7, 36, step * 0.72), scope = svg.closest('[data-v24-scope]');
    var active = scope && scope.dataset.v24ActiveBucket !== undefined ? scope.dataset.v24ActiveBucket : '';
    var hlX = ml + 8 * step, hlW = 6 * step, pillW = mob ? 142 : 148;
    var hlCx = clamp(ml + pillW / 2, vw - 8 - pillW / 2, hlX + hlW / 2);
    clearSvg(svg);
    svg.setAttribute('viewBox', '0 0 ' + vw + ' 178');
    svg.appendChild(el(doc, 'rect', { x: hlX.toFixed(1), y: 24, width: hlW.toFixed(1), height: 124, rx: 3, fill: 'var(--status-danger)', opacity: '0.06' }));
    svg.appendChild(el(doc, 'rect', { x: (hlCx - pillW / 2).toFixed(1), y: 14, width: pillW, height: 18, rx: 2, fill: 'var(--bg-surface)', opacity: '0.94' }));
    svg.appendChild(el(doc, 'text', { x: hlCx.toFixed(1), y: 27, 'text-anchor': 'middle', 'font-size': '11.5', 'font-weight': '650', fill: 'var(--status-danger)' }, 'Burst Peak 14:20Z–14:35Z'));
    for (var yv = 0; yv <= 4; yv += 1) {
      var yy = 148 - yv * 24;
      svg.appendChild(el(doc, 'line', { x1: ml, y1: yy, x2: ml + pw, y2: yy, stroke: 'var(--border-subtle)', 'stroke-dasharray': '2 3' }));
      svg.appendChild(el(doc, 'text', { x: ml - 6, y: yy + 4, 'text-anchor': 'end', 'font-size': '11.5', fill: 'var(--text-muted)' }, String(yv)));
    }
    var segMeta = [['var(--status-danger)', 1], ['var(--status-warn)', 2], ['var(--accent-focal)', 3], ['var(--text-muted)', 4]];
    V24_BUCKETS.forEach(function (b, i) {
      var x = ml + i * step + (step - bw) / 2, tot = b[1] + b[2] + b[3] + b[4], curY = 148;
      var grp = el(doc, 'g', {
        class: 'w2-svg-bar-grp', role: 'button', tabindex: '0', 'data-v24-bucket': String(i),
        'aria-pressed': active === String(i) ? 'true' : 'false',
        'aria-label': 'Bucket ' + b[0] + ' UTC: ' + tot + ' events',
      });
      grp.appendChild(el(doc, 'rect', { class: 'w2-bucket-hit', x: (x - 2).toFixed(1), y: 28, width: (bw + 4).toFixed(1), height: 122, rx: 2, fill: 'transparent' }));
      segMeta.forEach(function (sm) {
        var cnt = b[sm[1]];
        if (cnt <= 0) return;
        var sh = cnt * 24;
        curY -= sh;
        grp.appendChild(el(doc, 'rect', { x: x.toFixed(1), y: curY.toFixed(1), width: bw.toFixed(1), height: (sh - 1).toFixed(1), rx: 1.5, fill: sm[0] }));
      });
      var showTick = mob ? (i === 0 || i === 6 || i === 12 || i === 18 || i === 23) : (i % 4 === 0 || i === 23);
      if (showTick) {
        var anc = i === 0 ? 'start' : (i === 23 ? 'end' : 'middle');
        var tx = i === 0 ? ml : (i === 23 ? ml + pw : x + bw / 2);
        grp.appendChild(el(doc, 'text', { x: tx.toFixed(1), y: 166, 'text-anchor': anc, 'font-size': '11.5', fill: 'var(--text-muted)' }, b[0]));
      }
      svg.appendChild(grp);
    });
  }

  function renderV25Bathy(svg, vw) {
    var doc = svg.ownerDocument, mob = vw < 560, med = vw >= 560 && vw < 940;
    var ml = mob ? 44 : 56, mr = mob ? 10 : 12, pw = Math.max(180, vw - ml - mr), h = mob ? 216 : 210;
    var kx = function (km) { return ml + (km / 640) * pw; };
    var dy = function (d) { return 36 + (Math.abs(d) / 4000) * 144; };
    var scope = svg.closest('[data-v25-scope]'), activeGrp = scope ? (scope.dataset.v25ActiveSpan || 'all') : 'all';
    clearSvg(svg);
    svg.setAttribute('viewBox', '0 0 ' + vw + ' ' + h);
    var cPath = 'M ' + V25_PROFILE.map(function (p) { return kx(p[0]).toFixed(1) + ' ' + dy(p[1]).toFixed(1); }).join(' L ');
    var sPath = cPath + ' L ' + kx(640).toFixed(1) + ' 36.0 L ' + kx(0).toFixed(1) + ' 36.0 Z';
    svg.appendChild(el(doc, 'path', { d: sPath, fill: 'var(--accent-focal)', opacity: '0.08' }));
    [0, 1000, 2000, 3000, 4000].forEach(function (d) {
      var yy = dy(d).toFixed(1), lbl = d === 0 ? '0 m' : (mob ? '-' + (d / 1000) + 'km' : '-' + d + ' m');
      svg.appendChild(el(doc, 'line', { x1: ml, y1: yy, x2: ml + pw, y2: yy, stroke: 'var(--border-subtle)', 'stroke-dasharray': '2 3' }));
      svg.appendChild(el(doc, 'text', { x: ml - 6, y: (Number(yy) + 4).toFixed(1), 'text-anchor': 'end', 'font-size': '11.5', fill: 'var(--text-muted)' }, lbl));
    });
    svg.appendChild(el(doc, 'path', { d: cPath, fill: 'none', stroke: 'var(--text-primary)', 'stroke-width': '2.2' }));
    var xf = kx(362), boxW = mob ? 124 : 222, boxX = clamp(ml + 4, vw - mr - boxW, xf + 8);
    svg.appendChild(el(doc, 'line', { x1: xf.toFixed(1), y1: 28, x2: xf.toFixed(1), y2: 196, stroke: 'var(--status-warn)', 'stroke-dasharray': '4 3', 'stroke-width': '1.5' }));
    svg.appendChild(el(doc, 'rect', { x: boxX.toFixed(1), y: 44, width: boxW, height: 20, rx: 3, fill: 'var(--bg-surface)', stroke: 'var(--status-warn)' }));
    svg.appendChild(el(doc, 'text', { x: (boxX + 6).toFixed(1), y: 58, 'font-size': '11.5', 'font-weight': '650', fill: 'var(--status-warn)' },
      mob ? 'S5 Fault (+4.8 dB)' : 'Span S5 Fault (+4.8 dB · 362 km)'));
    V25_NODES.forEach(function (n) {
      var cx = kx(n[0]), cy = dy(n[1]), isWarn = n[3] === 'WARN', isBu = n[0] === 240;
      var col = isWarn ? 'var(--status-warn)' : (isBu ? 'var(--accent-focal)' : 'var(--text-primary)');
      var grp = el(doc, 'g', { class: 'w2-span-node', 'data-span-group': n[2] });
      applySpanFilter(grp, n[2], activeGrp);
      grp.appendChild(el(doc, 'circle', { cx: cx.toFixed(1), cy: cy.toFixed(1), r: isWarn || isBu ? 6.5 : 4.5, fill: col, stroke: 'var(--bg-surface)', 'stroke-width': '1.8' }));
      var dx = mob && n[7] !== 'middle' ? (n[8] > 0 ? 7 : (n[8] < 0 ? -7 : 0)) : n[8];
      var lblTxt = mob ? n[6] : (med ? n[5] : n[4]);
      grp.appendChild(el(doc, 'text', {
        class: 'va-svg-halo-text', x: (cx + dx).toFixed(1),
        y: mob ? n[10] : n[9], 'text-anchor': n[7], 'font-size': '11.5', 'font-weight': '600', fill: col,
      }, lblTxt));
      svg.appendChild(grp);
    });
  }

  function renderV25Osnr(svg, vw) {
    var doc = svg.ownerDocument, mob = vw < 560, ml = mob ? 44 : 56, mr = mob ? 10 : 12;
    var pw = Math.max(180, vw - ml - mr), scope = svg.closest('[data-v25-scope]');
    var activeGrp = scope ? (scope.dataset.v25ActiveSpan || 'all') : 'all';
    var kx = function (km) { return ml + (km / 640) * pw; };
    var oy = function (db) { return 184 - ((clamp(12, 28, db) - 12) / 16) * 150; };
    clearSvg(svg);
    svg.setAttribute('viewBox', '0 0 ' + vw + ' 214');
    [12, 16, 20, 24, 28].forEach(function (db) {
      var yy = oy(db);
      svg.appendChild(el(doc, 'line', { x1: ml, y1: yy.toFixed(1), x2: ml + pw, y2: yy.toFixed(1), stroke: 'var(--border-subtle)', 'stroke-dasharray': '2 3' }));
      svg.appendChild(el(doc, 'text', { x: ml - 6, y: (yy + 4).toFixed(1), 'text-anchor': 'end', 'font-size': '11.5', fill: 'var(--text-muted)' }, db + ' dB'));
    });
    (mob ? [0, 240, 362, 640] : [0, 160, 240, 362, 480, 640]).forEach(function (km) {
      var anc = km === 0 ? 'start' : (km === 640 ? 'end' : 'middle');
      svg.appendChild(el(doc, 'text', { x: kx(km).toFixed(1), y: 204, 'text-anchor': anc, 'font-size': '11.5', fill: 'var(--text-muted)' }, km + ' km'));
    });
    var yFec = oy(15.0), xf = kx(362);
    svg.appendChild(el(doc, 'line', { x1: kx(240).toFixed(1), y1: 24, x2: kx(240).toFixed(1), y2: 184, stroke: 'var(--border-strong)', 'stroke-dasharray': '2 4' }));
    svg.appendChild(el(doc, 'line', { x1: xf.toFixed(1), y1: 18, x2: xf.toFixed(1), y2: 184, stroke: 'var(--status-warn)', 'stroke-dasharray': '4 3', 'stroke-width': '1.5' }));
    svg.appendChild(el(doc, 'line', { x1: ml, y1: yFec.toFixed(1), x2: ml + pw, y2: yFec.toFixed(1), stroke: 'var(--status-danger)', 'stroke-dasharray': '6 4', 'stroke-width': '1.6' }));
    var fecW = mob ? 124 : 168;
    svg.appendChild(el(doc, 'rect', { x: (ml + pw - fecW - 2).toFixed(1), y: (yFec - 18).toFixed(1), width: fecW, height: 16, rx: 2, fill: 'var(--bg-surface)', opacity: '0.94' }));
    svg.appendChild(el(doc, 'text', { x: (ml + pw - 6).toFixed(1), y: (yFec - 6).toFixed(1), 'text-anchor': 'end', 'font-size': '11.5', 'font-weight': '650', fill: 'var(--status-danger)' },
      mob ? 'SD-FEC (15.0 dB)' : 'SD-FEC Floor (15.0 dB)'));
    var lPath = 'M ' + V25_STATIONS.map(function (s) { return kx(s[0]).toFixed(1) + ' ' + oy(s[2]).toFixed(1); }).join(' L ');
    svg.appendChild(el(doc, 'path', { d: lPath, fill: 'none', stroke: 'var(--accent-focal)', 'stroke-width': '2.3' }));
    V25_STATIONS.forEach(function (s) {
      var w = s[3] === 'WARN', grp = el(doc, 'g', { class: 'w2-span-mark', 'data-span-group': s[4] });
      applySpanFilter(grp, s[4], activeGrp);
      grp.appendChild(el(doc, 'circle', { cx: kx(s[0]).toFixed(1), cy: oy(s[2]).toFixed(1), r: w ? 6.0 : 4.2, fill: w ? 'var(--status-warn)' : 'var(--accent-focal)', stroke: 'var(--bg-surface)', 'stroke-width': '1.6' }));
      svg.appendChild(grp);
    });
    var ow = mob ? 142 : 198, ox = clamp(ml + 4, vw - mr - ow, xf + 8);
    svg.appendChild(el(doc, 'rect', { x: ox.toFixed(1), y: 42, width: ow, height: 20, rx: 3, fill: 'var(--bg-surface)', stroke: 'var(--status-warn)' }));
    svg.appendChild(el(doc, 'text', { x: (ox + 6).toFixed(1), y: 56, 'font-size': '11.5', 'font-weight': '650', fill: 'var(--status-warn)' },
      mob ? 'Min OSNR 16.4 (+1.4 dB)' : 'Min OSNR 16.4 dB (+1.4 dB)'));
  }

  function renderV26Box(svg, vw) {
    var doc = svg.ownerDocument, mob = vw < 560, ml = mob ? 42 : 48, mr = mob ? 10 : 14;
    var pw = Math.max(180, vw - ml - mr), xg = svg.querySelector('[data-v26-xgrid]');
    var geom = { w: vw, h: 264, ml: ml, mr: mr, yTop: 38, lineTop: 24, yBot: 232, mobile: mob };
    svg.setAttribute('viewBox', '0 0 ' + vw + ' 264');
    svg.setAttribute('data-v26-geom', JSON.stringify(geom));
    var ceilBg = svg.querySelector('[data-v26-ceil-bg]'), ceilLbl = svg.querySelector('[data-v26-ceil-lbl]');
    if (ceilBg) ceilBg.setAttribute('x', String(ml + 6));
    if (ceilLbl) ceilLbl.setAttribute('x', String(ml + 12));
    if (xg) {
      clearSvg(xg);
      (mob ? [0, 12, 24, 36] : [0, 6, 12, 18, 24, 30, 36]).forEach(function (m) {
        var anc = m === 0 ? 'start' : (m === 36 ? 'end' : 'middle');
        xg.appendChild(el(doc, 'text', {
          'data-v26-xtick': String(m), x: (ml + (m / 36) * pw).toFixed(1), y: 252,
          'text-anchor': anc, 'font-size': '11.5', fill: 'var(--text-muted)',
        }, 'Mo ' + m));
      });
    }
    var scope = svg.closest('[data-v26-root]');
    if (scope && typeof scope._v26Refresh === 'function') scope._v26Refresh();
  }

  function renderSvgBox(box, forceWidth) {
    if (!box) return;
    var svg = box.querySelector('svg[data-v23-blast-svg], svg[data-v24-hist-svg], svg[data-v25-bathy-svg], svg[data-v25-osnr-svg], svg[data-v26-svg]');
    if (!svg) return;
    var rawW = forceWidth || box.getBoundingClientRect().width;
    if (!rawW || rawW < 120) return;
    var vw = clamp(300, 1400, Math.round(rawW));
    if (svg.dataset.w2RenderedW === String(vw) && !forceWidth) return;
    svg.dataset.w2RenderedW = String(vw);
    if (svg.hasAttribute('data-v23-blast-svg')) renderV23Blast(svg, vw);
    else if (svg.hasAttribute('data-v24-hist-svg')) renderV24Hist(svg, vw);
    else if (svg.hasAttribute('data-v25-bathy-svg')) renderV25Bathy(svg, vw);
    else if (svg.hasAttribute('data-v25-osnr-svg')) renderV25Osnr(svg, vw);
    else if (svg.hasAttribute('data-v26-svg')) renderV26Box(svg, vw);
  }

  var sharedRo = null, globalWired = false;

  function ensureRo() {
    if (!sharedRo && typeof ResizeObserver !== 'undefined') {
      sharedRo = new ResizeObserver(function (entries) { entries.forEach(function (en) { renderSvgBox(en.target); }); });
    }
    return sharedRo;
  }

  function refreshAll(forceWidth, root) {
    var doc = root || document;
    if (doc && doc.querySelectorAll) doc.querySelectorAll('.w2-svg-box').forEach(function (box) { renderSvgBox(box, forceWidth); });
  }

  function observeStageMain(doc) {
    var stageMain = doc && doc.getElementById ? doc.getElementById('va-stage-main') : null;
    if (!stageMain || stageMain.dataset.w2SvgMo === '1' || typeof MutationObserver === 'undefined') return;
    stageMain.dataset.w2SvgMo = '1';
    var mo = new MutationObserver(function () { bootSvgEngine(doc); });
    mo.observe(stageMain, { childList: true });
  }

  function bootSvgEngine(root) {
    var doc = root || document, ro = ensureRo();
    if (doc && doc.querySelectorAll) {
      doc.querySelectorAll('.w2-svg-box').forEach(function (box) {
        if (ro && box.dataset.w2SvgObserved !== '1') { box.dataset.w2SvgObserved = '1'; ro.observe(box); }
        renderSvgBox(box);
      });
    }
    observeStageMain(doc);
    if (!globalWired) {
      globalWired = true;
      global.addEventListener('resize', function () { refreshAll(); });
      global.addEventListener('beforeprint', function () { refreshAll(1120); });
      global.addEventListener('afterprint', function () {
        document.querySelectorAll('.w2-svg-box svg').forEach(function (s) { delete s.dataset.w2RenderedW; });
        refreshAll();
      });
    }
  }

  global.QuietWave2Svg = { boot: bootSvgEngine, refresh: refreshAll, renderOne: renderSvgBox };
  if (typeof document !== 'undefined' && document) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { bootSvgEngine(document); });
    else bootSvgEngine(document);
  }
})(typeof window !== 'undefined' ? window : globalThis);
