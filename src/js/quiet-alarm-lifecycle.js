/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.7.0 — Reusable 4-Phase Automated Alarm Lifecycle Controller */
(function (global) {
  'use strict';

  var INSTANCES = [];
  var PHASES = Object.assign(Object.create(null), { nominal: 1, approaching: 2, unack: 3, ack: 4 });

  function getTrace() {
    return global.QuietAlarmTrace || {};
  }

  function hasPhase(k) {
    return typeof k === 'string' && Object.prototype.hasOwnProperty.call(PHASES, k);
  }

  function escHtml(s) {
    return getTrace().escHtml ? getTrace().escHtml(s) : String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtNum(v, dec) {
    if (getTrace().fmtNum) return getTrace().fmtNum(v, dec);
    var num = Number(v);
    if (!isFinite(num)) return '--';
    var d = (typeof dec === 'number' && isFinite(dec)) ? Math.max(0, Math.min(6, Math.round(dec))) : 1;
    return num.toFixed(d);
  }

  function fmtDuration(secTotal) {
    var s = Math.max(0, Math.floor(secTotal));
    var m = Math.floor(s / 60), r = s % 60;
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
    if (getTrace().computeExcursion) return getTrace().computeExcursion(val, cfg);
    var th = Number(cfg.threshold), diff = val - th;
    return { crossed: cfg.direction === 'below' ? val < th : val > th, diff: diff, deltaStr: (diff >= 0 ? '+' : '') + fmtNum(diff, cfg.decimals) + ' ' + cfg.unit };
  }

  function sampleForPhase(cfg, ph, elapsedMs) {
    var nom = Number(cfg.nominalStart), th = Number(cfg.threshold), peak = Number(cfg.breachPeak);
    var val = getTrace().resolveSampleAt ? getTrace().resolveSampleAt(cfg, ph, elapsedMs) : nom;
    var rate = ph === 'nominal' ? (cfg.direction === 'below' ? -0.05 : 0.05) :
      (ph === 'approaching' ? ((th - nom) / 2.0) : (ph === 'unack' ? ((peak - th) / 2.2) : 0));
    return { val: val, rate: rate };
  }

  function measureChartWidth(host, el) {
    var slot = el ? el.querySelector('[data-alarm-svg-slot]') : null;
    var w = (slot && slot.clientWidth > 120) ? (slot.clientWidth - 20) : (host.clientWidth > 120 ? (host.clientWidth - 60) : 960);
    return Math.max(460, Math.min(1120, w));
  }

  function buildFocusSvgForHost(host, el, cfg, phase, series) {
    var T = getTrace();
    var w = measureChartWidth(host, el);
    return T.buildFocusSvg ? T.buildFocusSvg(cfg, phase, series, w) : '';
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
    var hintId = 'va-alarm-ack-hint-' + INSTANCES.indexOf(inst);
    var wChart = measureChartWidth(host, null);
    var svgHtml = getTrace().buildFocusSvg ? getTrace().buildFocusSvg(cfg, 'unack', inst.series, wChart) : '';
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
      '<div class="va-alarm-chart-card" data-alarm-svg-slot>' + svgHtml + '</div>' +
      '<div class="va-alarm-timeline" aria-label="Breach Progression Timeline">' +
        '<div class="va-alarm-tl-step"><span>-00:08</span><span>Safe Window</span></div>' +
        '<div class="va-alarm-tl-step"><span>-00:03</span><span>Pre-Alarm Trend</span></div>' +
        '<div class="va-alarm-tl-step is-active"><span>00:00</span><span>Limit Crossed</span></div>' +
        '<div class="va-alarm-tl-step"><span>Active</span><span>Operator Ack Pending</span></div>' +
      '</div>' +
      (sibHtml ? '<div class="va-alarm-siblings" aria-label="Nominal Sibling Channels">' + sibHtml + '</div>' : '') +
      '<div class="va-alarm-takeover-actions">' +
        '<button type="button" class="va-alarm-ack-btn" data-alarm-ack aria-describedby="' + hintId + '">Acknowledge Alarm</button>' +
        '<div class="va-alarm-action-hints" id="' + hintId + '">' +
          '<span class="va-alarm-shortcut-note"><kbd class="va-kbd">Enter</kbd> / <kbd class="va-kbd">Space</kbd> to silence and restore balanced view</span>' +
          '<span class="va-alarm-limit-note">' + escHtml(cfg.ackActionHint || '') + '</span>' +
        '</div>' +
      '</div>';
    var ackBtn = el.querySelector('[data-alarm-ack]');
    if (ackBtn) ackBtn.addEventListener('click', function () { acknowledge(inst, true); });
  }

  function renderBanner(host, inst) {
    var bn = host.querySelector('[data-alarm-banner]');
    if (!bn) return;
    var cfg = inst.cfg, ph = inst.phase;
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
        setPhase(inst, targetPh, true, targetPh === 'unack' ? '[data-alarm-ack]' : '[data-alarm-jump="' + targetPh + '"]');
      });
    });
  }

  function announce(host, text) {
    var lr = host.querySelector('.va-alarm-live');
    if (lr) lr.textContent = text;
  }

  function setPhase(inst, ph, holdManual, focusSel) {
    if (!hasPhase(ph)) ph = 'nominal';
    if (holdManual) stopTimers(inst);
    var doc = inst.doc, T = getTrace();
    var hadFocus = !!(doc && doc.activeElement && inst.host.contains(doc.activeElement));
    var prev = inst.phase;
    inst.phase = ph;
    inst.manualHold = !!holdManual;
    inst.host.setAttribute('data-alarm-phase', ph);
    if (ph === 'nominal') {
      inst.breachSec = 0;
      if (holdManual) inst.elapsedMs = 0;
    } else if (ph === 'approaching') {
      inst.breachSec = 0;
      if (holdManual) inst.elapsedMs = 3100;
    } else if (ph === 'unack') {
      if (holdManual && inst.elapsedMs < 4000) inst.elapsedMs = 4400;
      inst.breachSec = Math.max(1, Math.floor(Math.max(0, inst.elapsedMs - 4000) / 1000) + 1);
    } else {
      inst.breachSec = Math.max(inst.breachSec, 4);
    }
    var sm = sampleForPhase(inst.cfg, ph, inst.elapsedMs);
    inst.val = sm.val;
    inst.rate = sm.rate;
    inst.series = T.buildPhaseSeries ? T.buildPhaseSeries(inst.cfg, ph, inst.elapsedMs) : [sm.val];
    renderBanner(inst.host, inst);
    if (ph === 'unack') renderTakeover(inst.host, inst);
    if (T.syncBoundUI) T.syncBoundUI(inst.host, inst);
    if (focusSel || hadFocus) {
      var targetSel = focusSel || (ph === 'unack' ? '[data-alarm-ack]' : '[data-alarm-replay]');
      var fEl = inst.host.querySelector(targetSel);
      if (fEl && typeof fEl.focus === 'function') fEl.focus({ preventScroll: true });
    }
    if (prev !== ph) {
      var msg = ph === 'approaching' ? (inst.cfg.paramLabel + ' approaching operating limit.') :
        (ph === 'unack' ? ('Alarm triggered: ' + inst.cfg.paramLabel + ' breached limit. Action required.') :
          (ph === 'ack' ? 'Alarm acknowledged. Balanced diagnostic view restored.' : (inst.cfg.paramLabel + ' returned to calm baseline.')));
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
    setPhase(inst, 'nominal', false, restoreFocus ? '[data-alarm-replay]' : '');
    startLoop(inst);
  }

  function stopTimers(inst) {
    if (inst.timerId) { global.clearInterval(inst.timerId); inst.timerId = 0; }
  }

  function tick(inst) {
    if (!inst.host.isConnected) {
      stopTimers(inst);
      inst.host.__vaAlarmBound = false;
      delete inst.host.__vaAlarmInst;
      var i = INSTANCES.indexOf(inst);
      if (i >= 0) INSTANCES.splice(i, 1);
      return;
    }
    if (inst.doc.hidden || inst.manualHold || inst.phase === 'ack') return;
    inst.elapsedMs += 250;
    var T = getTrace();
    var nextPhase = inst.elapsedMs < 2000 ? 'nominal' : (inst.elapsedMs < 4000 ? 'approaching' : 'unack');
    var sm = sampleForPhase(inst.cfg, nextPhase, inst.elapsedMs);
    inst.val = sm.val;
    inst.rate = sm.rate;
    inst.series = T.buildPhaseSeries ? T.buildPhaseSeries(inst.cfg, nextPhase, inst.elapsedMs) : inst.series.concat([inst.val]).slice(-34);
    if (nextPhase !== inst.phase) {
      setPhase(inst, nextPhase, false, '');
      return;
    }
    if (nextPhase === 'unack') {
      inst.breachSec = Math.max(1, Math.floor((inst.elapsedMs - 4000) / 1000) + 1);
      var tEl = inst.host.querySelector('[data-alarm-timer]'), mEl = inst.host.querySelector('[data-alarm-live-metric]');
      var dEl = inst.host.querySelector('[data-alarm-delta]'), sEl = inst.host.querySelector('[data-alarm-svg-slot]');
      if (tEl) tEl.textContent = fmtDuration(inst.breachSec);
      if (mEl) mEl.textContent = fmtNum(inst.val, inst.cfg.decimals) + ' ' + inst.cfg.unit;
      if (dEl) dEl.textContent = computeExcursion(inst.val, inst.cfg).deltaStr;
      if (sEl) sEl.innerHTML = buildFocusSvgForHost(inst.host, inst.host.querySelector('[data-alarm-takeover]'), inst.cfg, 'unack', inst.series);
    } else {
      var bVal = inst.host.querySelector('[data-alarm-banner-val]');
      if (bVal) bVal.textContent = fmtNum(inst.val, inst.cfg.decimals) + ' ' + inst.cfg.unit;
    }
    if (T.syncBoundUI) T.syncBoundUI(inst.host, inst);
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
    var T = getTrace();
    var inst = {
      host: host, doc: doc, cfg: cfg, phase: 'nominal', elapsedMs: 0, breachSec: 0, timerId: 0, manualHold: false,
      val: Number(cfg.nominalStart), rate: 0, series: T.buildPhaseSeries ? T.buildPhaseSeries(cfg, 'nominal', 0) : [Number(cfg.nominalStart)]
    };
    host.__vaAlarmInst = inst;
    INSTANCES.push(inst);
    var ov = resolveOverride(host, doc);
    if (ov) setPhase(inst, ov, true, '');
    else if (cfg.initialMode === 'ack') setPhase(inst, 'ack', true, '');
    else { setPhase(inst, 'nominal', false, ''); startLoop(inst); }
  }

  function bindHandoffLinks(doc) {
    doc.querySelectorAll('a[data-quiet-handoff-world][data-quiet-handoff-view]').forEach(function (a) {
      if (a.__vaHandoffWired) return;
      a.__vaHandoffWired = true;
      a.addEventListener('click', function (ev) {
        var w = a.getAttribute('data-quiet-handoff-world'), v = a.getAttribute('data-quiet-handoff-view');
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
    if (global.document.readyState === 'loading') global.document.addEventListener('DOMContentLoaded', function () { boot(global.document); });
    else boot(global.document);
  }
})(typeof window !== 'undefined' ? window : this);
