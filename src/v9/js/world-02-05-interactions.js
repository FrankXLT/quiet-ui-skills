/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.0 Phase 5 — Interactive Workbench & Optical HUD Handlers (Worlds 02-05) */

(function (global) {
  'use strict';

  function updateExecButton(btnA, btnB, execBtn) {
    if (!execBtn) return;
    execBtn.disabled = !(btnA && btnA.getAttribute('aria-pressed') === 'true' && btnB && btnB.getAttribute('aria-pressed') === 'true');
  }

  function wireTwoStepInterlock(doc, opts) {
    const btnA = doc.getElementById(opts.btnAId);
    const btnB = doc.getElementById(opts.btnBId);
    const execBtn = doc.getElementById(opts.execId);
    const pill = doc.getElementById(opts.pillId);
    const log = doc.getElementById(opts.logId);
    if (!btnA || !btnB || !execBtn || execBtn.dataset.v9Bound === '1') return;
    execBtn.dataset.v9Bound = '1';

    function toggle(btn) {
      btn.setAttribute('aria-pressed', btn.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      updateExecButton(btnA, btnB, execBtn);
    }
    btnA.addEventListener('click', function () { toggle(btnA); });
    btnB.addEventListener('click', function () { toggle(btnB); });
    execBtn.addEventListener('click', function () {
      if (execBtn.disabled) return;
      if (pill) {
        pill.textContent = opts.doneLabel;
        pill.setAttribute('data-variant', 'status');
        pill.setAttribute('data-state', opts.doneState || 'nominal');
      }
      btnA.setAttribute('aria-pressed', 'false');
      btnB.setAttribute('aria-pressed', 'false');
      if (log) {
        const entry = doc.createElement('div');
        entry.className = 'v9-audit-item';
        entry.textContent = opts.auditText;
        log.insertBefore(entry, log.firstChild);
        while (log.children.length > 5) log.removeChild(log.lastElementChild);
      }
      execBtn.disabled = true;
    });
  }

  function wireChipGroup(doc, containerId, readoutId, onSelect) {
    const bar = doc.getElementById(containerId);
    const readout = readoutId ? doc.getElementById(readoutId) : null;
    if (!bar || bar.dataset.v9Bound === '1') return;
    bar.dataset.v9Bound = '1';
    bar.addEventListener('click', function (ev) {
      const btn = ev.target && ev.target.closest ? ev.target.closest('[data-variant="chip"]') : null;
      if (!btn || !bar.contains(btn)) return;
      bar.querySelectorAll('[data-variant="chip"]').forEach(function (b) {
        const active = b === btn;
        b.classList.toggle('is-active', active);
        b.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
      if (readout && btn.dataset.summary) readout.textContent = btn.dataset.summary;
      if (typeof onSelect === 'function') onSelect(btn, doc);
    });
  }

  function wireWorlds02To05(doc) {
    wireTwoStepInterlock(doc, {
      btnAId: 'v04-otel-btn', btnBId: 'v04-arm-btn', execId: 'v04-exec-btn',
      pillId: 'v04-gate-pill', logId: 'v04-audit-list',
      doneLabel: 'CANARY ISOLATED', doneState: 'nominal',
      auditText: '[04:15:08Z] OTel scrape verified and canary drained to 0% weight; production p99 stabilized.',
    });
    wireTwoStepInterlock(doc, {
      btnAId: 'v07-loto-btn', btnBId: 'v07-arm-btn', execId: 'v07-exec-btn',
      pillId: 'v07-gate-pill', logId: 'v07-audit-list',
      doneLabel: 'ISLAND ARMED', doneState: 'nominal',
      auditText: '[21:30:06Z] LOTO [10]=0 & Sync 59.985 Hz confirmed; POI 52-M islanding dispatch armed.',
    });
    wireTwoStepInterlock(doc, {
      btnAId: 'v14-term-btn', btnBId: 'v14-arm-btn', execId: 'v14-exec-btn',
      pillId: 'v14-gate-pill', logId: 'v14-audit-list',
      doneLabel: 'SOF_ARB_ERR W1C OK', doneState: 'nominal',
      auditText: '[05:30:04Z] 120 Ohm termination & stub <= 0.3 m verified; SOF_ARB_ERR [31] W1C latch cleared.',
    });

    wireChipGroup(doc, 'v05-enclave-chips', 'v05-enclave-readout', function (btn, d) {
      const target = btn.dataset.enclave || 'all';
      d.querySelectorAll('#v05-enclave-cards [data-enclave]').forEach(function (card) {
        const hit = target === 'all' || card.dataset.enclave === target;
        card.classList.toggle('is-enclave-match', target !== 'all' && hit);
        card.classList.toggle('is-enclave-dimmed', target !== 'all' && !hit);
      });
    });

    wireChipGroup(doc, 'v10-fund-chips', 'v10-fund-readout', function (btn, d) {
      const f = btn.dataset.fund || 'all';
      d.querySelectorAll('#v10-budget-table tbody tr').forEach(function (row) {
        const txt = (row.textContent || '');
        const show = f === 'all'
          || (f === 'inflow' && (txt.includes('Opening') || txt.includes('Grant') || txt.includes('Bond')))
          || (f === 'outlay' && (txt.includes('HVAC') || txt.includes('Water Main') || txt.includes('Closing')))
          || (f === 'review' && txt.includes('REVIEW'));
        row.classList.toggle('v10-row-hidden', !show);
      });
    });

    wireChipGroup(doc, 'v11-shock-chips', 'v11-shock-readout', function (btn, d) {
      const q1El = d.getElementById('v11-q1-val');
      const q8El = d.getElementById('v11-q8-val');
      const headEl = d.getElementById('v11-headroom-val');
      const gatePill = d.getElementById('v11-gate-pill');
      if (q1El && btn.dataset.q1) q1El.textContent = btn.dataset.q1;
      if (q8El && btn.dataset.q8) q8El.textContent = btn.dataset.q8;
      if (headEl && btn.dataset.headroom) {
        headEl.textContent = btn.dataset.headroom;
        const st = btn.dataset.state || '';
        headEl.setAttribute('data-tone', st === 'err' ? 'danger' : (st === 'warn' ? 'warn' : (st === 'nominal' ? 'ok' : 'accent')));
      }
      if (gatePill && btn.dataset.state) {
        gatePill.setAttribute('data-state', btn.dataset.state);
        gatePill.textContent = btn.dataset.pill || 'NOMINAL';
      }
    });

    wireChipGroup(doc, 'v12-role-chips', null, function (btn, d) {
      const role = btn.dataset.role || 'student';
      const stu = d.getElementById('v12-student-note');
      const ins = d.getElementById('v12-instructor-note');
      if (stu) stu.classList.toggle('v12-panel-hidden', role !== 'student');
      if (ins) ins.classList.toggle('v12-panel-hidden', role !== 'instructor');
    });

    var SVG_NS = 'http://www.w3.org/2000/svg';
    function _setTxt(d, id, txt) {
      var el = d.getElementById(id);
      if (el) el.textContent = txt;
    }
    function _renderTicks(d, id, cfg) {
      var g = d.getElementById(id);
      if (!g) return;
      g.textContent = '';
      var decimals = cfg.decimals || 0;
      for (var v = cfg.min; v <= cfg.max + 1e-6; v += cfg.step) {
        var val = decimals ? Number(v.toFixed(decimals)) : Math.round(v);
        var y = Math.round(360 - (val - cfg.center) * cfg.pxPerUnit);
        if (y < 162 || y > 558) continue;
        var isMaj = decimals ? (Math.round(val * 10) % Math.round(cfg.majorEvery * 10) === 0) : (val % cfg.majorEvery === 0);
        var ln = d.createElementNS(SVG_NS, 'line');
        ln.setAttribute('x1', String(cfg.side === 'left' ? (isMaj ? 122 : 128) : 1064));
        ln.setAttribute('x2', String(cfg.side === 'left' ? 136 : (isMaj ? 1078 : 1072)));
        ln.setAttribute('y1', String(y));
        ln.setAttribute('y2', String(y));
        ln.setAttribute('stroke-width', '1.6');
        g.appendChild(ln);
        if (isMaj && Math.abs(y - 360) >= 28) {
          var tx = d.createElementNS(SVG_NS, 'text');
          tx.setAttribute('x', String(cfg.side === 'left' ? 115 : 1084));
          tx.setAttribute('y', String(y + 5));
          tx.setAttribute('text-anchor', cfg.side === 'left' ? 'end' : 'start');
          tx.setAttribute('font-size', '13');
          tx.textContent = decimals ? val.toFixed(decimals) : val.toLocaleString('en-US');
          g.appendChild(tx);
        }
      }
    }
    var V15_REGIMES = {
      daylight: {
        hdgRef: 'TRUE HDG', spdUnit: 'KT IAS', spdVal: '138', spdSub: 'GS 144 KT',
        propFn: function (b) { return 'PROP BTE ' + b + '% · IMEP 14.0 BAR'; },
        altUnit: 'FT MSL', altVal: '1,180', rad: '640 FT AGL · 3.0° GS', vs: 'VS -650 FPM', baro: '29.92 IN',
        fpm: 'translate(0,0)', ils: '0',
        spdCfg: { side: 'left', center: 138, min: 110, max: 165, step: 5, majorEvery: 10, pxPerUnit: 6 },
        altCfg: { side: 'right', center: 1180, min: 1000, max: 1400, step: 50, majorEvery: 100, pxPerUnit: 0.85 },
      },
      lowlight: {
        hdgRef: 'LOC HDG', spdUnit: 'KT IAS', spdVal: '134', spdSub: 'GS 139 KT',
        propFn: function (b) { return 'PROP BTE ' + b + '% · IMEP 14.0 BAR'; },
        altUnit: 'FT MSL', altVal: '860', rad: '480 FT RAD · ILS', vs: 'VS -710 FPM', baro: '29.92 IN',
        fpm: 'translate(0,0)', ils: '0.88',
        spdCfg: { side: 'left', center: 134, min: 105, max: 160, step: 5, majorEvery: 10, pxPerUnit: 6 },
        altCfg: { side: 'right', center: 860, min: 650, max: 1050, step: 50, majorEvery: 100, pxPerUnit: 0.85 },
      },
      earthrise: {
        hdgRef: 'INERTIAL', spdUnit: 'M/S', spdVal: '1,632', spdSub: 'ORB VEL 1,632 M/S',
        propFn: function (b) { return 'PROP η ' + b + '% REF · RCS NOMINAL'; },
        altUnit: 'KM', altVal: '112.4', rad: 'APO 114.2 · PER 110.8 KM', vs: 'HDOT 0 M/S', baro: '',
        fpm: 'translate(0,-45)', ils: '0',
        spdCfg: { side: 'left', center: 1632, min: 1605, max: 1660, step: 5, majorEvery: 10, pxPerUnit: 6 },
        altCfg: { side: 'right', center: 112.4, min: 100, max: 124, step: 2, majorEvery: 4, pxPerUnit: 15, decimals: 1 },
      },
    };
    wireChipGroup(doc, 'v15-backplate-chips', null, function (btn, d) {
      var mode = btn.dataset.backplate;
      var stage = d.getElementById('v15-hud-stage');
      if (stage && mode) stage.setAttribute('data-backplate', mode);
      var reg = mode && V15_REGIMES[mode];
      if (!reg) return;
      var propEl = d.getElementById('v15-hud-prop-line');
      var bte = (propEl && propEl.dataset.bte) || '42.8';
      _setTxt(d, 'v15-hud-hdg-ref', reg.hdgRef);
      _setTxt(d, 'v15-hud-spd-unit', reg.spdUnit);
      _setTxt(d, 'v15-hud-spd-val', reg.spdVal);
      _setTxt(d, 'v15-hud-spd-sub', reg.spdSub);
      _setTxt(d, 'v15-hud-prop-line', reg.propFn(bte));
      _setTxt(d, 'v15-hud-alt-unit', reg.altUnit);
      _setTxt(d, 'v15-hud-alt-val', reg.altVal);
      _setTxt(d, 'v15-hud-rad-line', reg.rad);
      _setTxt(d, 'v15-hud-vs-line', reg.vs);
      _setTxt(d, 'v15-hud-baro-line', reg.baro);
      var fpm = d.getElementById('v15-hud-fpm');
      if (fpm) fpm.setAttribute('transform', reg.fpm);
      var ils = d.getElementById('v15-hud-ils-scale');
      if (ils) ils.setAttribute('opacity', reg.ils);
      _renderTicks(d, 'v15-spd-ticks', reg.spdCfg);
      _renderTicks(d, 'v15-alt-ticks', reg.altCfg);
    });

    wireChipGroup(doc, 'v16-luminance-chips', null, function (btn, d) {
      const vp = d.getElementById('v16-glass-viewport');
      if (vp && btn.dataset.luminance) vp.setAttribute('data-luminance', btn.dataset.luminance);
      if (vp && btn.dataset.contrast) vp.setAttribute('data-contrast', btn.dataset.contrast);
    });
  }

  global.QuietWorlds02To05Runtime = { boot: wireWorlds02To05 };
})(typeof window !== 'undefined' ? window : globalThis);
