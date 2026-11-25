/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.7.0 — Reusable 4-Phase Automated Alarm Lifecycle Controller */
(function (global) {
  'use strict';

  var INSTANCES = [];
  var PHASES = Object.assign(Object.create(null), { nominal: 1, approaching: 2, unack: 3, ack: 4 });

  function hasPhase(k) {
    return typeof k === 'string' && Object.prototype.hasOwnProperty.call(PHASES, k);
  }

  function escHtml(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtNum(v, dec) {
    var num = Number(v);
    if (!isFinite(num)) return '--';
    var d = (typeof dec === 'number' && isFinite(dec)) ? Math.max(0, Math.min(6, Math.round(dec))) : 1;
    return num.toFixed(d);
  }

  function fmtDuration(secTotal) {
    var s = Math.max(0, Math.floor(secTotal));
    var m = Math.floor(s / 60);
    var r = s % 60;
    return (m < 10 ? '0' : '') + m + 'm ' + (r < 10 ? '0' : '') + r + 's';
  }

  function resolveOverride(host, doc) {
    var attr = host.getAttribute('data-alarm-override') || (doc && doc.documentElement && doc.documentElement.getAttribute('data-alarm-override'));
    if (hasPhase(attr)) return attr;
    try {
      var q1 = new URLSearchParams(global.location.search || '').get('alarm');
      if (hasPhase(q1)) return q1;
    } catch (_e) {}
    try {
      if (global.parent && global.parent !== global) {
        var q2 = new URLSearchParams(global.parent.location.search || '').get('alarm');
        if (hasPhase(q2)) return q2;
      }
    } catch (_e2) {}
    return '';
  }

  function computeExcursion(val, cfg) {
    var th = Number(cfg.threshold);
    var diff = val - th;
    var crossed = cfg.direction === 'below' ? val < th : val > th;
    var sign = diff >= 0 ? '+' : '';
    var deltaStr = sign + fmtNum(diff, cfg.decimals) + ' ' + cfg.unit;
    return { crossed: crossed, diff: diff, deltaStr: deltaStr };
  }

  function buildFocusSvg(cfg, phase, series) {
    var W = 680, H = 160, ML = 56, MR = 24, MT = 18, MB = 26;
    var PW = W - ML - MR, PH = H - MT - MB;
    var th = Number(cfg.threshold);
    var vals = series.concat([th, Number(cfg.nominalStart), Number(cfg.breachPeak)]);
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    var pad = Math.max((hi - lo) * 0.22, Math.abs(th) * 0.015 || 0.5);
    var yMin = lo - pad, yMax = hi + pad;
    function mapX(idx, n) { return ML + (n <= 1 ? PW : (idx / (n - 1)) * PW); }
    function mapY(v) { return MT + PH - ((v - yMin) / (yMax - yMin || 1)) * PH; }

    var yTh = mapY(th);
    var n = series.length;
    var pts = [];
    for (var i = 0; i < n; i++) pts.push(mapX(i, n).toFixed(1) + ',' + mapY(series[i]).toFixed(1));
    var polyPts = pts.join(' ');

    var areaPath = '';
    if (n > 1) {
      var excPts = [];
      for (var j = 0; j < n; j++) {
        var v = series[j];
        var hit = cfg.direction === 'below' ? v < th : v > th;
        if (hit) {
          excPts.push([mapX(j, n), mapY(v), mapX(j, n), yTh]);
        }
      }
      if (excPts.length > 0) {
        var topSeg = excPts.map(function (p, k) { return (k === 0 ? 'M' : 'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
        var baseSeg = excPts.slice().reverse().map(function (p) { return 'L' + p[2].toFixed(1) + ',' + p[3].toFixed(1); }).join(' ');
        areaPath = '<path d="' + topSeg + ' ' + baseSeg + ' Z" fill="var(--status-err)" fill-opacity="0.18" stroke="none"/>';
      }
    }

    var strokeClr = phase === 'nominal' ? 'var(--accent-primary)' : (phase === 'approaching' ? 'var(--status-warn)' : 'var(--status-err)');
    var lastX = mapX(Math.max(0, n - 1), n).toFixed(1);
    var lastY = mapY(series[n - 1] != null ? series[n - 1] : th).toFixed(1);
    var ticks = [yMin + (yMax - yMin) * 0.15, th, yMin + (yMax - yMin) * 0.85];
    var gridHtml = ticks.map(function (tv) {
      var ty = mapY(tv).toFixed(1);
      return '<line x1="' + ML + '" y1="' + ty + '" x2="' + (W - MR) + '" y2="' + ty + '" stroke="var(--border-hairline)" stroke-width="1"/>' +
        '<text x="' + (ML - 6) + '" y="' + (Number(ty) + 3.5).toFixed(1) + '" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="var(--text-muted)">' + fmtNum(tv, cfg.decimals) + '</text>';
    }).join('');

    var limY = cfg.direction === 'above' ? (yTh + 12.5).toFixed(1) : (yTh - 5).toFixed(1);
    return '<svg class="va-alarm-focus-svg" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + escHtml(cfg.paramLabel) + ' excursion trace">' +
      '<rect x="' + ML + '" y="' + MT + '" width="' + PW + '" height="' + PH + '" fill="var(--bg-elevated)" rx="3"/>' +
      gridHtml + areaPath +
      '<line x1="' + ML + '" y1="' + yTh.toFixed(1) + '" x2="' + (W - MR) + '" y2="' + yTh.toFixed(1) + '" stroke="var(--status-warn)" stroke-width="1.5" stroke-dasharray="5 4"/>' +
      '<text x="' + (W - MR - 4) + '" y="' + limY + '" text-anchor="end" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-warn)">Limit ' + fmtNum(th, cfg.decimals) + ' ' + escHtml(cfg.unit) + '</text>' +
      '<polyline fill="none" stroke="' + strokeClr + '" stroke-width="2.4" stroke-linejoin="round" points="' + polyPts + '"/>' +
      '<circle cx="' + lastX + '" cy="' + lastY + '" r="4.5" fill="' + strokeClr + '" stroke="var(--bg-surface)" stroke-width="1.5"/>' +
      '<text x="' + ML + '" y="' + (H - 6) + '" font-family="var(--font-sans)" font-size="11" fill="var(--text-muted)">Calm Baseline</text>' +
      '<text x="' + (ML + PW * 0.45).toFixed(1) + '" y="' + (H - 6) + '" text-anchor="middle" font-family="var(--font-sans)" font-size="11" fill="var(--text-muted)">Pre-Breach Approach</text>' +
      '<text x="' + (W - MR) + '" y="' + (H - 6) + '" text-anchor="end" font-family="var(--font-sans)" font-size="11" fill="var(--text-muted)">Live Window</text>' +
      '</svg>';
  }

  function renderTakeover(host, inst) {
    var el = host.querySelector('[data-alarm-takeover]');
    if (!el) return;
    var cfg = inst.cfg;
    var exc = computeExcursion(inst.val, cfg);
    var rateTxt = (inst.rate >= 0 ? '+' : '') + fmtNum(inst.rate, cfg.decimals) + ' ' + cfg.unit + '/s';
    var boundTxt = (cfg.direction === 'below' ? '>= ' : '<= ') + fmtNum(cfg.threshold, cfg.decimals) + ' ' + cfg.unit;
    var sibHtml = (cfg.siblings || []).map(function (s) {
      return '<span class="va-alarm-sibling-chip"><span class="va-alarm-sibling-dot" aria-hidden="true"></span><strong>' + escHtml(s.label) + '</strong> <span>' + escHtml(s.val) + '</span></span>';
    }).join('');
    el.innerHTML =
      '<div class="va-alarm-takeover-head">' +
        '<div class="va-alarm-takeover-title-group">' +
          '<div><span class="va-pill" data-variant="status" data-state="fault">ACTIVE UNACKNOWLEDGED ALARM</span> <span class="va-pill" data-variant="tag">' + escHtml(cfg.channelTag || 'CHANNEL BREACH') + '</span></div>' +
          '<h2 class="va-alarm-takeover-title">' + escHtml(cfg.paramLabel) + ' Out of Operating Bounds</h2>' +
        '</div>' +
        '<div class="va-alarm-timer-wrap"><span class="va-alarm-timer-label">BREACH ELAPSED</span><span class="va-alarm-timer va-nums" aria-live="off" data-alarm-timer>' + fmtDuration(inst.breachSec) + '</span></div>' +
      '</div>' +
      '<div class="va-alarm-metrics-grid">' +
        '<div class="va-alarm-metric-cell is-excursion"><span class="va-alarm-metric-k">Live Reading</span><span class="va-alarm-metric-v va-nums" data-alarm-live-metric>' + fmtNum(inst.val, cfg.decimals) + ' ' + escHtml(cfg.unit) + '</span></div>' +
        '<div class="va-alarm-metric-cell"><span class="va-alarm-metric-k">Operating Boundary</span><span class="va-alarm-metric-v va-nums">' + escHtml(boundTxt) + '</span></div>' +
        '<div class="va-alarm-metric-cell is-excursion"><span class="va-alarm-metric-k">Excursion Delta</span><span class="va-alarm-metric-v va-nums" data-alarm-delta>' + escHtml(exc.deltaStr) + '</span></div>' +
        '<div class="va-alarm-metric-cell"><span class="va-alarm-metric-k">Rate of Change</span><span class="va-alarm-metric-v va-nums" data-alarm-rate>' + escHtml(rateTxt) + '</span></div>' +
      '</div>' +
      '<div class="va-alarm-chart-card" data-alarm-svg-slot>' + buildFocusSvg(cfg, 'unack', inst.series) + '</div>' +
      '<div class="va-alarm-timeline" aria-label="Breach Progression Timeline">' +
        '<div class="va-alarm-tl-step"><span>1 · Calm Baseline</span><span>0s – 2s</span></div>' +
        '<div class="va-alarm-tl-step"><span>2 · Pre-Breach Approach</span><span>2s – 4s</span></div>' +
        '<div class="va-alarm-tl-step is-active"><span>3 · Threshold Crossed</span><span>' + escHtml(cfg.breachReason || 'Takeover Active') + '</span></div>' +
        '<div class="va-alarm-tl-step"><span>4 · Operator Ack</span><span>Awaiting Response</span></div>' +
      '</div>' +
      (sibHtml ? '<div class="va-alarm-siblings" aria-label="Nominal Sibling Channels">' + sibHtml + '</div>' : '') +
      '<div class="va-alarm-takeover-actions">' +
        '<button type="button" class="va-alarm-ack-btn" data-alarm-ack>Acknowledge Alarm</button>' +
        '<span class="va-alarm-limit-note">' + escHtml(cfg.ackActionHint || 'Acknowledge to silence alert frame and inspect full diagnostic workspace.') + '</span>' +
      '</div>';
    var ackBtn = el.querySelector('[data-alarm-ack]');
    if (ackBtn) ackBtn.addEventListener('click', function () { acknowledge(inst, true); });
  }

  function renderBanner(host, inst) {
    var bn = host.querySelector('[data-alarm-banner]');
    if (!bn) return;
    var cfg = inst.cfg;
    var ph = inst.phase;
    var peakExc = computeExcursion(Number(cfg.breachPeak), cfg);
    var stState = ph === 'nominal' ? 'nominal' : (ph === 'approaching' ? 'warn' : 'fault');
    var stText = ph === 'nominal' ? 'CALM BASELINE' : (ph === 'approaching' ? 'APPROACHING LIMIT' : (ph === 'ack' ? 'ACKNOWLEDGED · LATCHED FAULT' : 'ACTIVE ALARM'));
    var extra = ph === 'approaching'
      ? '<span class="va-alarm-rate-note">Rate ' + (inst.rate >= 0 ? '+' : '') + fmtNum(inst.rate, cfg.decimals) + ' ' + escHtml(cfg.unit) + '/s</span>'
      : (ph === 'ack'
        ? '<span class="va-alarm-rate-note">Latched Peak ' + fmtNum(cfg.breachPeak, cfg.decimals) + ' ' + escHtml(cfg.unit) + ' (' + escHtml(peakExc.deltaStr) + ')</span>'
        : '<span class="va-alarm-limit-note">Limit ' + fmtNum(cfg.threshold, cfg.decimals) + ' ' + escHtml(cfg.unit) + '</span>');
    var btns = ph === 'ack'
      ? '<button type="button" class="va-alarm-btn va-alarm-btn-replay" data-alarm-replay>Replay Breach</button>' +
        '<button type="button" class="va-alarm-btn" data-alarm-reset>Return to Calm</button>'
      : '<button type="button" class="va-alarm-btn va-alarm-btn-replay" data-alarm-replay>Replay Breach</button>';
    var benchCtrl = cfg.benchControls
      ? '<button type="button" class="va-alarm-btn" data-alarm-jump="nominal" aria-pressed="' + (ph === 'nominal' ? 'true' : 'false') + '">1 · Calm</button>' +
        '<button type="button" class="va-alarm-btn" data-alarm-jump="approaching" aria-pressed="' + (ph === 'approaching' ? 'true' : 'false') + '">2 · Approach</button>' +
        '<button type="button" class="va-alarm-btn" data-alarm-jump="unack" aria-pressed="' + (ph === 'unack' ? 'true' : 'false') + '">3 · Takeover</button>' +
        '<button type="button" class="va-alarm-btn" data-alarm-jump="ack" aria-pressed="' + (ph === 'ack' ? 'true' : 'false') + '">4 · Ack</button>'
      : '';
    bn.innerHTML =
      '<div class="va-alarm-banner-left">' +
        '<span class="va-pill" data-variant="status" data-state="' + stState + '">' + stText + '</span>' +
        '<span class="va-alarm-param-name">' + escHtml(cfg.paramLabel) + '</span>' +
        '<span class="va-alarm-live-val va-nums" data-alarm-banner-val>' + fmtNum(inst.val, cfg.decimals) + ' ' + escHtml(cfg.unit) + '</span>' +
        extra +
      '</div>' +
      '<div class="va-alarm-banner-right">' + benchCtrl + btns + '</div>';
    var rep = bn.querySelector('[data-alarm-replay]');
    if (rep) rep.addEventListener('click', function () { replay(inst, true); });
    var rst = bn.querySelector('[data-alarm-reset]');
    if (rst) rst.addEventListener('click', function () { setPhase(inst, 'nominal', true, '[data-alarm-replay]'); });
    bn.querySelectorAll('[data-alarm-jump]').forEach(function (jb) {
      jb.addEventListener('click', function () {
        var targetPh = jb.getAttribute('data-alarm-jump');
        var nextFocus = targetPh === 'unack' ? '[data-alarm-ack]' : '[data-alarm-jump="' + targetPh + '"]';
        setPhase(inst, targetPh, true, nextFocus);
      });
    });
  }

  function announce(host, text) {
    var lr = host.querySelector('.va-alarm-live');
    if (lr) lr.textContent = text;
  }

  function sampleForPhase(cfg, ph, elapsedMs) {
    var nom = Number(cfg.nominalStart), th = Number(cfg.threshold), peak = Number(cfg.breachPeak);
    var dir = cfg.direction === 'below' ? -1 : 1;
    var spanApp = th - nom;
    if (ph === 'nominal') {
      var jitter = Math.sin(elapsedMs / 380) * Math.max(Math.abs(spanApp) * 0.08, 0.05);
      return { val: nom + jitter, rate: dir * 0.05 };
    }
    if (ph === 'approaching') {
      var frac = Math.min(0.95, Math.max(0.15, (elapsedMs - 2000) / 2000));
      var v = nom + spanApp * (0.35 + frac * 0.62);
      return { val: v, rate: (th - nom) / 2.0 };
    }
    if (ph === 'unack') {
      var bFrac = Math.min(1, Math.max(0.25, (elapsedMs - 4000) / 3500));
      var v2 = th + (peak - th) * bFrac + Math.sin(elapsedMs / 420) * Math.abs(peak - th) * 0.06;
      return { val: v2, rate: (peak - th) / 2.2 };
    }
    return { val: th + (peak - th) * 0.65, rate: 0 };
  }

  function setPhase(inst, ph, holdManual, focusSel) {
    if (!hasPhase(ph)) ph = 'nominal';
    if (holdManual) stopTimers(inst);
    var doc = inst.doc;
    var hadFocus = !!(doc && doc.activeElement && inst.host.contains(doc.activeElement));
    var prev = inst.phase;
    inst.phase = ph;
    inst.manualHold = !!holdManual;
    inst.host.setAttribute('data-alarm-phase', ph);
    if (ph === 'nominal') {
      inst.breachSec = 0;
      if (holdManual) {
        inst.elapsedMs = 400;
        var s1 = sampleForPhase(inst.cfg, 'nominal', 400);
        inst.val = s1.val; inst.rate = s1.rate;
        inst.series = [Number(inst.cfg.nominalStart), inst.val];
      } else {
        var s1l = sampleForPhase(inst.cfg, 'nominal', inst.elapsedMs);
        inst.val = s1l.val; inst.rate = s1l.rate;
      }
    } else if (ph === 'approaching') {
      inst.breachSec = 0;
      if (holdManual) {
        inst.elapsedMs = 3100;
        var s2 = sampleForPhase(inst.cfg, 'approaching', 3100);
        inst.val = s2.val; inst.rate = s2.rate;
        inst.series = [Number(inst.cfg.nominalStart), Number(inst.cfg.nominalStart), inst.val];
      }
    } else if (ph === 'unack') {
      if (holdManual && inst.elapsedMs < 4000) inst.elapsedMs = 4200;
      inst.breachSec = Math.max(1, Math.floor(Math.max(0, inst.elapsedMs - 4000) / 1000) + 1);
      if (holdManual) {
        var s3 = sampleForPhase(inst.cfg, 'unack', inst.elapsedMs);
        inst.val = s3.val; inst.rate = s3.rate;
        inst.series = [Number(inst.cfg.nominalStart), (Number(inst.cfg.nominalStart) + Number(inst.cfg.threshold)) / 2, Number(inst.cfg.threshold), inst.val];
      }
    } else {
      inst.breachSec = Math.max(inst.breachSec, 4);
      var s4 = sampleForPhase(inst.cfg, 'ack', inst.elapsedMs);
      inst.val = s4.val; inst.rate = 0;
      if (holdManual || inst.series.length < 2) {
        inst.series = [Number(inst.cfg.nominalStart), Number(inst.cfg.threshold), Number(inst.cfg.breachPeak), inst.val];
      }
    }
    renderBanner(inst.host, inst);
    if (ph === 'unack') renderTakeover(inst.host, inst);
    if (focusSel || hadFocus) {
      var targetSel = focusSel || (ph === 'unack' ? '[data-alarm-ack]' : '[data-alarm-replay]');
      var fEl = inst.host.querySelector(targetSel);
      if (fEl && typeof fEl.focus === 'function') fEl.focus({ preventScroll: true });
    }
    if (prev !== ph) {
      var msg = ph === 'approaching'
        ? inst.cfg.paramLabel + ' approaching operating limit.'
        : (ph === 'unack'
          ? 'Alarm triggered: ' + inst.cfg.paramLabel + ' breached limit. Action required.'
          : (ph === 'ack' ? 'Alarm acknowledged. Balanced diagnostic view restored.' : inst.cfg.paramLabel + ' returned to calm baseline.'));
      announce(inst.host, msg);
    }
  }

  function acknowledge(inst, restoreFocus) {
    stopTimers(inst);
    setPhase(inst, 'ack', true, restoreFocus ? '[data-alarm-replay]' : '');
  }

  function replay(inst, restoreFocus) {
    stopTimers(inst);
    inst.manualHold = false;
    inst.elapsedMs = 0;
    inst.breachSec = 0;
    inst.series = [Number(inst.cfg.nominalStart)];
    setPhase(inst, 'nominal', false, restoreFocus ? '[data-alarm-replay]' : '');
    startLoop(inst);
  }

  function stopTimers(inst) {
    if (inst.timerId) { global.clearInterval(inst.timerId); inst.timerId = 0; }
  }

  function tick(inst) {
    if (!inst.host.isConnected || inst.doc.hidden || inst.manualHold || inst.phase === 'ack') return;
    inst.elapsedMs += 250;
    var nextPhase = inst.elapsedMs < 2000 ? 'nominal' : (inst.elapsedMs < 4000 ? 'approaching' : 'unack');
    var sm = sampleForPhase(inst.cfg, nextPhase, inst.elapsedMs);
    inst.val = sm.val;
    inst.rate = sm.rate;
    inst.series.push(inst.val);
    if (inst.series.length > 28) inst.series.shift();
    if (nextPhase !== inst.phase) {
      setPhase(inst, nextPhase, false, '');
      return;
    }
    if (nextPhase === 'unack') {
      inst.breachSec = Math.max(1, Math.floor((inst.elapsedMs - 4000) / 1000) + 1);
      var tEl = inst.host.querySelector('[data-alarm-timer]');
      var mEl = inst.host.querySelector('[data-alarm-live-metric]');
      var dEl = inst.host.querySelector('[data-alarm-delta]');
      var sEl = inst.host.querySelector('[data-alarm-svg-slot]');
      if (tEl) tEl.textContent = fmtDuration(inst.breachSec);
      if (mEl) mEl.textContent = fmtNum(inst.val, inst.cfg.decimals) + ' ' + inst.cfg.unit;
      if (dEl) dEl.textContent = computeExcursion(inst.val, inst.cfg).deltaStr;
      if (sEl) sEl.innerHTML = buildFocusSvg(inst.cfg, 'unack', inst.series);
    } else {
      var bVal = inst.host.querySelector('[data-alarm-banner-val]');
      if (bVal) bVal.textContent = fmtNum(inst.val, inst.cfg.decimals) + ' ' + inst.cfg.unit;
    }
  }

  function startLoop(inst) {
    stopTimers(inst);
    inst.timerId = global.setInterval(function () { tick(inst); }, 250);
  }

  function normalizeCfg(rawCfg) {
    if (!rawCfg || typeof rawCfg !== 'object' || Array.isArray(rawCfg)) return null;
    if (![rawCfg.nominalStart, rawCfg.threshold, rawCfg.breachPeak].every(function (n) { return typeof n === 'number' && isFinite(n); })) return null;
    rawCfg.paramLabel = String(rawCfg.paramLabel || 'Monitored Channel');
    rawCfg.unit = rawCfg.unit != null ? String(rawCfg.unit) : '';
    rawCfg.siblings = Array.isArray(rawCfg.siblings)
      ? rawCfg.siblings.filter(function (s) { return s && typeof s === 'object'; }).map(function (s) {
          return { label: String(s.label || ''), val: String(s.val != null ? s.val : '') };
        })
      : [];
    return rawCfg;
  }

  function mountHost(host, doc) {
    if (host.__vaAlarmBound) return;
    var raw = host.getAttribute('data-alarm-config');
    if (!raw) return;
    var cfg;
    try { cfg = normalizeCfg(JSON.parse(raw)); } catch (_e) { return; }
    if (!cfg) return;
    host.__vaAlarmBound = true;
    var inst = {
      host: host, doc: doc, cfg: cfg, phase: 'nominal',
      elapsedMs: 0, breachSec: 0, timerId: 0, manualHold: false,
      val: Number(cfg.nominalStart), rate: 0, series: [Number(cfg.nominalStart)]
    };
    host.__vaAlarmInst = inst;
    INSTANCES.push(inst);
    var ov = resolveOverride(host, doc);
    if (ov) {
      setPhase(inst, ov, true, '');
    } else if (cfg.initialMode === 'ack') {
      setPhase(inst, 'ack', true, '');
    } else {
      setPhase(inst, 'nominal', false, '');
      startLoop(inst);
    }
  }

  function bindHandoffLinks(doc) {
    doc.querySelectorAll('a[data-quiet-handoff-world][data-quiet-handoff-view]').forEach(function (a) {
      if (a.__vaHandoffWired) return;
      a.__vaHandoffWired = true;
      a.addEventListener('click', function (ev) {
        var w = a.getAttribute('data-quiet-handoff-world');
        var v = a.getAttribute('data-quiet-handoff-view');
        try {
          if (global.parent && global.parent !== global && global.parent.QuietStudioPortalV9 &&
              typeof global.parent.QuietStudioPortalV9.openExamples === 'function' && w && v) {
            ev.preventDefault();
            global.parent.QuietStudioPortalV9.openExamples(w, v);
          }
        } catch (_e) {}
      });
    });
  }

  function boot(docRef) {
    var doc = docRef || global.document;
    if (!doc) return;
    destroyAll(doc);
    doc.querySelectorAll('.va-alarm-console[data-alarm-config]').forEach(function (h) { mountHost(h, doc); });
    bindHandoffLinks(doc);
    if (!doc.__vaVisWired) {
      doc.__vaVisWired = true;
      doc.addEventListener('visibilitychange', function () {
        INSTANCES.forEach(function (inst) {
          if (inst.doc === doc && inst.host.isConnected && !doc.hidden && inst.phase === 'unack') renderTakeover(inst.host, inst);
        });
      });
      var win = doc.defaultView || global;
      if (win && win.addEventListener) {
        win.addEventListener('beforeprint', function () {
          INSTANCES.forEach(function (inst) { if (inst.doc === doc && inst.phase === 'unack') acknowledge(inst, false); });
        });
      }
    }
  }

  function destroyAll(docRef) {
    for (var i = INSTANCES.length - 1; i >= 0; i--) {
      if (!docRef || INSTANCES[i].doc === docRef) {
        stopTimers(INSTANCES[i]);
        INSTANCES[i].host.__vaAlarmBound = false;
        delete INSTANCES[i].host.__vaAlarmInst;
        INSTANCES.splice(i, 1);
      }
    }
  }

  global.QuietAlarmLifecycle = {
    boot: boot,
    destroyAll: destroyAll,
    setPhase: function (host, phase) { if (host && host.__vaAlarmInst) { stopTimers(host.__vaAlarmInst); setPhase(host.__vaAlarmInst, phase, true, ''); } },
    replay: function (host) { if (host && host.__vaAlarmInst) replay(host.__vaAlarmInst, false); },
    acknowledge: function (host) { if (host && host.__vaAlarmInst) acknowledge(host.__vaAlarmInst, false); }
  };

  if (global.document) {
    if (global.document.readyState === 'loading') {
      global.document.addEventListener('DOMContentLoaded', function () { boot(global.document); });
    } else {
      boot(global.document);
    }
  }
})(typeof window !== 'undefined' ? window : this);
