/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.7.0 — Edge-to-Edge Alarm Excursion Trace & Card Synchronization */
(function (global) {
  'use strict';

  var HEADER_META = Object.assign(Object.create(null), {
    nominal: { label: 'ALL SYSTEMS NOMINAL', state: 'nominal' },
    approaching: { label: 'APPROACHING LIMIT', state: 'warn' },
    unack: { label: '1 UNACK ALARM', state: 'fault' },
    ack: { label: '1 LATCHED FAULT', state: 'fault' }
  });

  function escHtml(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtNum(v, dec) {
    var num = Number(v);
    if (!isFinite(num)) return '--';
    var d = (typeof dec === 'number' && isFinite(dec)) ? Math.max(0, Math.min(6, Math.round(dec))) : 1;
    return num.toFixed(d);
  }

  function computeExcursion(val, cfg) {
    var th = Number(cfg.threshold);
    var diff = val - th;
    var crossed = cfg.direction === 'below' ? val < th : val > th;
    var sign = diff >= 0 ? '+' : '';
    return { crossed: crossed, diff: diff, deltaStr: sign + fmtNum(diff, cfg.decimals) + ' ' + cfg.unit };
  }

  function resolveSampleAt(cfg, ph, elapsedMs) {
    var nom = Number(cfg.nominalStart), th = Number(cfg.threshold), peak = Number(cfg.breachPeak);
    var ackVal = (typeof cfg.ackValue === 'number' && isFinite(cfg.ackValue)) ? Number(cfg.ackValue) : (th + (peak - th) * 0.65);
    var span = th - nom;
    if (ph === 'nominal') {
      return nom + Math.sin(elapsedMs / 380) * Math.max(Math.abs(span) * 0.08, 0.002);
    }
    if (ph === 'approaching') {
      var af = Math.min(0.95, Math.max(0.15, (elapsedMs - 2000) / 2000));
      return nom + span * (0.35 + af * 0.62);
    }
    if (ph === 'unack') {
      var bf = Math.min(1, Math.max(0.28, (elapsedMs - 4000) / 3400));
      return th + (peak - th) * bf + Math.sin(elapsedMs / 420) * Math.abs(peak - th) * 0.05;
    }
    return ackVal;
  }

  function buildPhaseSeries(cfg, ph, elapsedMs) {
    var nom = Number(cfg.nominalStart), th = Number(cfg.threshold), peak = Number(cfg.breachPeak);
    var n = 34, arr = [];
    var span = th - nom, exc = peak - th;
    var seed = Number(elapsedMs || 0) / 520;
    var tail = resolveSampleAt(cfg, ph, Number(elapsedMs || 0));
    var ripNom = Math.max(Math.abs(span) * 0.06, Math.abs(th) * 0.0004 || 0.01);
    var ripExc = Math.max(Math.abs(exc) * 0.07, ripNom);
    for (var i = 0; i < n; i++) {
      var wave = Math.sin(i * 0.72 + seed) * 0.55 + Math.cos(i * 1.45 + seed * 0.6) * 0.45;
      var v;
      if (ph === 'nominal') {
        v = nom + wave * ripNom;
      } else if (ph === 'approaching') {
        if (i < 20) {
          v = nom + wave * ripNom;
        } else {
          var tApp = (i - 19) / (n - 20);
          v = nom + (tail - nom) * tApp + wave * ripNom * 0.5;
          if ((cfg.direction === 'below' && v <= th) || (cfg.direction !== 'below' && v >= th)) {
            v = th + (cfg.direction === 'below' ? 1 : -1) * Math.max(Math.abs(span) * 0.02, 0.002);
          }
        }
      } else {
        if (i <= 13) {
          v = nom + wave * ripNom;
        } else if (i <= 21) {
          var tRamp = (i - 13) / 8.5;
          v = nom + span * (0.1 + tRamp * 0.87) + wave * ripNom * 0.4;
          if ((cfg.direction === 'below' && v <= th) || (cfg.direction !== 'below' && v >= th)) {
            v = th + (cfg.direction === 'below' ? 1 : -1) * Math.max(Math.abs(span) * 0.015, 0.001);
          }
        } else if (ph === 'unack') {
          var uFrac = (i - 21) / (n - 22);
          var dip = Math.sin(uFrac * Math.PI * 0.82);
          v = th + exc * (0.32 + 0.68 * Math.min(1, uFrac * 0.85 + dip * 0.25)) + wave * ripExc;
        } else {
          var aFrac = (i - 21) / (n - 22);
          v = aFrac < 0.55 ? (th + exc * (0.35 + aFrac * 1.1) + wave * ripExc * 0.5) : (peak + (tail - peak) * ((aFrac - 0.55) / 0.45));
        }
      }
      arr.push(v);
    }
    arr[n - 1] = tail;
    return arr;
  }

  function computeScaleAndGrid(cfg, series) {
    var th = Number(cfg.threshold);
    var vals = series.concat([th, Number(cfg.nominalStart), Number(cfg.breachPeak)]);
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    var rawSpan = Math.max(hi - lo, Math.abs(th) * 0.004 || 0.5);
    var pad = rawSpan * 0.16;
    if (global.QuietSvgLayout && typeof global.QuietSvgLayout.niceScale125 === 'function') {
      var sc = global.QuietSvgLayout.niceScale125(lo - pad, hi + pad, { targetTicks: 4, includeZero: false });
      return sc;
    }
    var yMin = lo - pad, yMax = hi + pad;
    var step = (yMax - yMin) / 4;
    return { min: yMin, max: yMax, step: step, ticks: [yMin, yMin + step, yMin + step * 2, yMin + step * 3, yMax] };
  }

  function buildBreachPolygon(series, th, dir, mapX, mapY, yTh) {
    var n = series.length;
    if (n < 2) return { areaPath: '', crossX: null };
    var isHit = function (v) { return dir === 'below' ? v < th : v > th; };
    var polyPts = [], segs = [], curRun = null, firstCrossX = null;
    for (var i = 0; i < n; i++) {
      var v1 = series[i], h1 = isHit(v1), x1 = mapX(i, n), y1 = mapY(v1);
      if (i > 0) {
        var v0 = series[i - 1], h0 = isHit(v0), x0 = mapX(i - 1, n);
        if (h0 !== h1) {
          var t = (th - v0) / ((v1 - v0) || 1e-9);
          var xc = x0 + Math.max(0, Math.min(1, t)) * (x1 - x0);
          if (h1) {
            if (firstCrossX === null) firstCrossX = xc;
            curRun = [[xc, yTh]];
          } else if (curRun) {
            curRun.push([xc, yTh]);
            segs.push(curRun);
            curRun = null;
          }
        }
      } else if (h1) {
        if (firstCrossX === null) firstCrossX = x1;
        curRun = [[x1, yTh]];
      }
      if (h1 && curRun) curRun.push([x1, y1]);
      polyPts.push(x1.toFixed(1) + ',' + y1.toFixed(1));
    }
    if (curRun && curRun.length > 0) {
      curRun.push([mapX(n - 1, n), yTh]);
      segs.push(curRun);
    }
    var areaPath = segs.map(function (run) {
      var d = run.map(function (p, idx) { return (idx === 0 ? 'M' : 'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
      return '<path d="' + d + ' Z" fill="var(--status-err)" fill-opacity="0.18" stroke="none"/>';
    }).join('');
    return { areaPath: areaPath, crossX: firstCrossX, polyLine: polyPts.join(' ') };
  }

  function buildXLabels(ML, PW, W, MR, H, crossX) {
    var placed = [{ x: ML, text: '-12s', anchor: 'start', fill: 'var(--text-muted)', weight: '500' }];
    var bx = crossX !== null ? Math.max(ML + 74, Math.min(W - MR - 88, crossX)) : null;
    if (W >= 540) {
      var x8 = ML + PW * 0.24, x4 = ML + PW * 0.46;
      if ((x8 - ML) >= 68 && (bx === null || (bx - x8) >= 90)) {
        placed.push({ x: x8, text: '-8s', anchor: 'middle', fill: 'var(--text-muted)', weight: '500' });
      }
      if ((x4 - placed[placed.length - 1].x) >= 68 && (bx === null || (bx - x4) >= 88)) {
        placed.push({ x: x4, text: '-4s', anchor: 'middle', fill: 'var(--text-muted)', weight: '500' });
      }
    }
    if (bx !== null) {
      placed.push({ x: bx, text: '00:00 BREACH', anchor: 'middle', fill: 'var(--status-err)', weight: '700' });
    }
    placed.push({ x: W - MR, text: 'LIVE', anchor: 'end', fill: 'var(--status-err)', weight: '700' });
    return placed.map(function (it) {
      return '<text x="' + it.x.toFixed(1) + '" y="' + (H - 7) + '" text-anchor="' + it.anchor + '" font-family="var(--font-mono)" font-size="11" font-weight="' + it.weight + '" fill="' + it.fill + '">' + it.text + '</text>';
    }).join('');
  }

  function buildFocusSvg(cfg, phase, series, containerWidth) {
    var W = Math.max(460, Math.min(1120, Math.round(Number(containerWidth) || 960)));
    var H = 192, ML = 64, MR = 24, MT = 22, MB = 28;
    var PW = W - ML - MR, PH = H - MT - MB;
    var pts = (Array.isArray(series) && series.length >= 12) ? series : buildPhaseSeries(cfg, phase || 'unack', 4400);
    var sc = computeScaleAndGrid(cfg, pts);
    var yMin = sc.min, yMax = sc.max, th = Number(cfg.threshold), n = pts.length;
    var mapX = function (idx, total) { return ML + (total <= 1 ? PW : (idx / (total - 1)) * PW); };
    var mapY = function (v) { return MT + PH - ((v - yMin) / (yMax - yMin || 1)) * PH; };
    var yTh = mapY(th);
    var breach = buildBreachPolygon(pts, th, cfg.direction, mapX, mapY, yTh);
    var decGrid = (sc.step && sc.step < 0.05) ? 3 : ((sc.step && sc.step < 0.5) ? 2 : cfg.decimals);
    var gridHtml = (sc.ticks || []).filter(function (tv) {
      var ty = mapY(tv);
      return ty >= MT + 4 && ty <= MT + PH - 4;
    }).map(function (tv) {
      var ty = mapY(tv).toFixed(1);
      return '<line x1="' + ML + '" y1="' + ty + '" x2="' + (W - MR) + '" y2="' + ty + '" stroke="var(--border-hairline)" stroke-width="1"/>' +
        '<text x="' + (ML - 8) + '" y="' + (Number(ty) + 3.5).toFixed(1) + '" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="var(--text-muted)">' + fmtNum(tv, decGrid) + '</text>';
    }).join('');
    var crossPin = '';
    if (breach.crossX !== null) {
      var pinX = breach.crossX;
      var pinLblX = Math.max(ML + 68, Math.min(W - MR - 68, pinX));
      crossPin = '<line x1="' + pinX.toFixed(1) + '" y1="' + (MT + 2) + '" x2="' + pinX.toFixed(1) + '" y2="' + (MT + PH) + '" stroke="var(--status-err)" stroke-width="1.5" stroke-dasharray="4 3"/>' +
        '<circle cx="' + pinX.toFixed(1) + '" cy="' + yTh.toFixed(1) + '" r="4" fill="var(--status-err)" stroke="var(--bg-surface)" stroke-width="1.5"/>' +
        '<text x="' + pinLblX.toFixed(1) + '" y="' + (MT - 5) + '" text-anchor="middle" font-family="var(--font-sans)" font-size="11" font-weight="700" fill="var(--status-err)" paint-order="stroke fill" stroke="var(--bg-surface)" stroke-width="3.5" stroke-linejoin="round">Threshold Crossed</text>';
    }
    var strokeClr = phase === 'nominal' ? 'var(--accent-primary)' : (phase === 'approaching' ? 'var(--status-warn)' : 'var(--status-err)');
    var lastX = mapX(n - 1, n).toFixed(1), lastY = mapY(pts[n - 1]).toFixed(1);
    var limSideLeft = breach.crossX === null || breach.crossX > ML + PW * 0.42;
    var limX = limSideLeft ? (ML + 8) : (W - MR - 8);
    var limAnc = limSideLeft ? 'start' : 'end';
    var limY = (cfg.direction === 'below' || yTh > MT + PH * 0.55) ? Math.max(MT + 13, yTh - 6) : Math.min(MT + PH - 6, yTh + 13);
    return '<svg class="va-alarm-focus-svg" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + escHtml(cfg.paramLabel) + ' full-width excursion trace">' +
      '<rect x="' + ML + '" y="' + MT + '" width="' + PW + '" height="' + PH + '" fill="var(--bg-elevated)" rx="3"/>' +
      gridHtml + breach.areaPath +
      '<line x1="' + ML + '" y1="' + yTh.toFixed(1) + '" x2="' + (W - MR) + '" y2="' + yTh.toFixed(1) + '" stroke="var(--status-warn)" stroke-width="1.5" stroke-dasharray="5 4"/>' +
      crossPin +
      '<text x="' + limX.toFixed(1) + '" y="' + limY.toFixed(1) + '" text-anchor="' + limAnc + '" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-warn)" paint-order="stroke fill" stroke="var(--bg-elevated)" stroke-width="3.5" stroke-linejoin="round">Limit ' + fmtNum(th, cfg.decimals) + ' ' + escHtml(cfg.unit) + '</text>' +
      '<polyline fill="none" stroke="' + strokeClr + '" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round" points="' + (breach.polyLine || '') + '"/>' +
      '<circle cx="' + lastX + '" cy="' + lastY + '" r="4.5" fill="' + strokeClr + '" stroke="var(--bg-surface)" stroke-width="1.5"/>' +
      buildXLabels(ML, PW, W, MR, H, breach.crossX) +
      '</svg>';
  }

  function syncV08Card(card, inst, phMeta) {
    var cfg = inst.cfg, ph = inst.phase, val = inst.val;
    var valEl = card.querySelector('.v08-kpi-val'), pill = card.querySelector('.v08-kpi-head .va-pill'), subEl = card.querySelector('.v08-kpi-target');
    if (valEl) valEl.textContent = fmtNum(val, cfg.decimals) + ' ' + cfg.unit;
    if (pill) {
      pill.setAttribute('data-state', phMeta.state);
      pill.textContent = ph === 'nominal' ? 'LOCK ±0.02 Hz' : (ph === 'approaching' ? 'APPROACHING LIMIT' : (ph === 'unack' ? 'ACTIVE ALARM' : 'LATCHED PEAK ' + fmtNum(cfg.breachPeak, cfg.decimals) + ' ' + cfg.unit));
    }
    if (subEl) {
      var rateTxt = (inst.rate >= 0 ? '+' : '') + fmtNum(inst.rate, cfg.decimals) + ' ' + cfg.unit + '/s';
      var pkExc = computeExcursion(Number(cfg.breachPeak), cfg);
      subEl.textContent = ph === 'nominal'
        ? ('Reference 60.000 Hz · Limit ' + fmtNum(cfg.threshold, cfg.decimals) + ' ' + cfg.unit)
        : (ph === 'approaching'
          ? ('Rate ' + rateTxt + ' · Limit ' + fmtNum(cfg.threshold, cfg.decimals) + ' ' + cfg.unit)
          : ('Peak ' + fmtNum(cfg.breachPeak, cfg.decimals) + ' ' + cfg.unit + ' (' + pkExc.deltaStr + ') · Limit ' + fmtNum(cfg.threshold, cfg.decimals) + ' ' + cfg.unit));
    }
    var vis = card.querySelector('.v08-kpi-visual svg');
    if (vis && inst.series && inst.series.length > 2) {
      var col = ph === 'nominal' ? 'var(--accent-primary)' : (ph === 'approaching' ? 'var(--status-warn)' : 'var(--status-err)');
      var lo = 59.72, hi = 60.06, normPts = inst.series.slice(-12);
      var xs = normPts.map(function (_v, idx) { return 8 + (idx / (normPts.length - 1)) * 464; });
      var ys = normPts.map(function (v) { var t = Math.max(0.05, Math.min(0.95, (v - lo) / (hi - lo))); return 31 - t * 23; });
      var pl = vis.querySelector('polyline'), cr = vis.querySelector('circle'), bar = vis.querySelectorAll('rect')[1];
      if (pl) { pl.setAttribute('points', xs.map(function (x, i) { return x.toFixed(1) + ',' + ys[i].toFixed(1); }).join(' ')); pl.setAttribute('stroke', col); }
      if (cr) { cr.setAttribute('cx', xs[xs.length - 1].toFixed(1)); cr.setAttribute('cy', ys[ys.length - 1].toFixed(1)); cr.setAttribute('fill', col); }
      if (bar) {
        var fw = Math.max(4, Math.min(464, ((val - lo) / (hi - lo)) * 464));
        bar.setAttribute('width', fw.toFixed(1)); bar.setAttribute('fill', col);
      }
    }
  }

  function syncScalarCard(card, inst, phMeta) {
    var cfg = inst.cfg, ph = inst.phase, val = inst.val;
    var valEl = card.querySelector('.qe-scalar-val');
    if (valEl) {
      if (card.dataset.vaUnc === undefined) {
        var m = (valEl.textContent || '').match(/(±\s*[0-9.]+)/);
        card.dataset.vaUnc = m ? m[1] : '';
      }
      var unc = card.dataset.vaUnc;
      valEl.textContent = fmtNum(val, cfg.decimals) + (unc ? ' ' + unc : '') + ' ' + cfg.unit;
    }
    var pill = card.querySelector('.qe-scalar-disp .va-pill');
    if (pill) {
      pill.setAttribute('data-state', phMeta.state);
      pill.textContent = ph === 'nominal' ? 'Nominal' : (ph === 'approaching' ? 'CAUTION' : (ph === 'unack' ? 'TRIPWIRE' : 'LATCHED FAULT'));
    }
    var marg = card.querySelector('.qe-scalar-margin');
    if (marg) {
      var nom = Number(cfg.nominalStart), th = Number(cfg.threshold), den = Math.abs(nom - th) || 1;
      var remPct = ((cfg.direction === 'below' ? (val - th) : (th - val)) / den) * 100;
      marg.textContent = 'Margin ' + (remPct >= 0 ? '+' : '') + remPct.toFixed(1) + '%';
    }
    var svg = card.querySelector('svg.qe-gauge-svg');
    if (svg && typeof cfg.gaugeMin === 'number' && typeof cfg.gaugeMax === 'number') {
      var tPos = Math.max(0, Math.min(1, (val - cfg.gaugeMin) / ((cfg.gaugeMax - cfg.gaugeMin) || 1)));
      var ax = 24 + tPos * 292, fillCol = ph === 'nominal' ? 'var(--status-ok)' : (ph === 'approaching' ? 'var(--status-warn)' : 'var(--status-danger)');
      var polys = svg.querySelectorAll('polygon'), actPin = polys[polys.length - 1];
      if (actPin) {
        actPin.setAttribute('points', ax.toFixed(1) + ',27.0 ' + (ax - 4.5).toFixed(1) + ',39.5 ' + (ax + 4.5).toFixed(1) + ',39.5');
        actPin.setAttribute('fill', fillCol);
      }
      svg.querySelectorAll('text').forEach(function (tx) {
        if ((tx.textContent || '').indexOf('ACT') === 0) {
          tx.textContent = 'ACT\u00a0' + fmtNum(val, cfg.decimals) + ' ' + cfg.unit;
          tx.setAttribute('fill', fillCol);
          var anc = ax < 80 ? 'start' : (ax > 260 ? 'end' : 'middle');
          tx.setAttribute('text-anchor', anc);
          tx.setAttribute('x', Math.max(8, Math.min(332, ax)).toFixed(1));
        }
      });
    }
  }

  function syncTopbar(doc, inst, phMeta) {
    var bar = doc.querySelector('#va-shell-topbar .va-shell-topbar-status');
    if (!bar) return;
    var cfg = inst.cfg, ph = inst.phase;
    var pills = bar.querySelectorAll('.va-pill[data-variant="status"]');
    var metrics = bar.querySelectorAll('.va-topbar-metric');
    if (cfg.viewId === 'v01-icu-bedside-terminal') {
      if (pills[0]) { pills[0].setAttribute('data-state', phMeta.state); pills[0].textContent = phMeta.label; }
      if (metrics[0]) { metrics[0].setAttribute('data-state', phMeta.state); metrics[0].textContent = 'MAP ' + fmtNum(inst.val, cfg.decimals) + ' ' + cfg.unit; }
    } else if (cfg.viewId === 'v07-grid-scada-poi-console') {
      var lastPill = pills[pills.length - 1];
      if (lastPill) { lastPill.setAttribute('data-state', phMeta.state); lastPill.textContent = phMeta.label; }
      var freqMetric = metrics[1] || metrics[0];
      if (freqMetric) { freqMetric.setAttribute('data-state', phMeta.state); freqMetric.textContent = fmtNum(ph === 'unack' || ph === 'ack' ? inst.val : cfg.nominalStart, cfg.decimals) + ' ' + cfg.unit; }
    } else if (pills.length) {
      pills[0].setAttribute('data-state', phMeta.state);
      pills[0].textContent = phMeta.label;
    }
  }

  function syncBoundUI(host, inst) {
    var doc = inst.doc || global.document;
    if (!doc) return;
    var cfg = inst.cfg, ph = inst.phase;
    var phMeta = HEADER_META[ph] || HEADER_META.nominal;
    doc.querySelectorAll('[data-alarm-header-pill]').forEach(function (hp) {
      hp.setAttribute('data-state', phMeta.state);
      hp.textContent = phMeta.label;
    });
    syncTopbar(doc, inst, phMeta);
    var rateTxt = (inst.rate >= 0 ? '+' : '') + fmtNum(inst.rate, cfg.decimals) + ' ' + cfg.unit + '/s';
    host.querySelectorAll('[data-alarm-fault-target="1"]').forEach(function (card) {
      if (card.classList.contains('v08-kpi-card')) {
        syncV08Card(card, inst, phMeta);
      } else if (card.classList.contains('qe-scalar-card')) {
        syncScalarCard(card, inst, phMeta);
      } else if (card.classList.contains('v9-kpi-tile')) {
        var kv = card.querySelector('.v9-kpi-val'), ks = card.querySelector('.v9-kpi-sub');
        var dVal = ph === 'ack' ? Number(cfg.breachPeak) : inst.val;
        if (kv) { kv.textContent = fmtNum(dVal, cfg.decimals) + ' ' + cfg.unit; kv.setAttribute('data-tone', ph === 'nominal' ? '' : (ph === 'approaching' ? 'warn' : 'danger')); }
        if (ks) {
          var th = Number(cfg.threshold);
          ks.textContent = ph === 'nominal' ? ('SLO Ceiling: ' + fmtNum(th, 1) + ' ms (Normal)') :
            (ph === 'approaching' ? ('Approaching ' + fmtNum(th, 1) + ' ms (' + rateTxt + ')') :
              (ph === 'unack' ? ('BREACH ACTIVE (+' + fmtNum(dVal - th, 1) + ' ms over SLO)') : ('Latched Peak: +' + fmtNum(dVal - th, 1) + ' ms above ' + fmtNum(th, 1) + ' ms')));
        }
      } else if (card.classList.contains('v9-demo-subcard')) {
        var sp = card.querySelector('.va-pill');
        var uSuf = cfg.unit && cfg.unit.charAt(0) === '%' ? '%' : (' ' + (cfg.unit || ''));
        if (sp) { sp.setAttribute('data-state', phMeta.state); sp.textContent = ph === 'ack' ? ('LATCHED · ' + fmtNum(cfg.breachPeak, cfg.decimals) + uSuf) : phMeta.label; }
      }
    });
  }

  global.QuietAlarmTrace = {
    escHtml: escHtml,
    fmtNum: fmtNum,
    computeExcursion: computeExcursion,
    resolveSampleAt: resolveSampleAt,
    buildPhaseSeries: buildPhaseSeries,
    buildFocusSvg: buildFocusSvg,
    syncBoundUI: syncBoundUI
  };
})(typeof window !== 'undefined' ? window : this);
