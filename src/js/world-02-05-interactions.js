/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.0 Phase 5 — Interactive Workbench & Optical HUD Handlers (Worlds 02-05) */

(function (global) {
  'use strict';
  var V15_CLEANUPS = typeof WeakMap === 'function' ? new WeakMap() : null;

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
          || (f === 'inflow' && (txt.includes('Opening') || txt.includes('Grant') || txt.includes('Bond') || txt.includes('Escrow')))
          || (f === 'outlay' && (txt.includes('Outlay') || txt.includes('Closing')))
          || (f === 'review' && (txt.includes('REVIEW') || txt.includes('HOLD')));
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

    function syncV15Viewport() {
      var stg = doc.getElementById('v15-hud-stage');
      var svg = stg ? stg.querySelector('.v15-reticle-layer') : null;
      if (!stg || !svg) return;
      var w = stg.clientWidth || doc.documentElement.clientWidth || 1200;
      var portrait = w < 600;
      svg.setAttribute('viewBox', portrait ? '260 0 680 720' : '0 0 1200 720');
      svg.classList.toggle('is-portrait', portrait);
      var spdG = doc.getElementById('v15-hud-spd-grp');
      var altG = doc.getElementById('v15-hud-alt-grp');
      if (spdG) spdG.setAttribute('transform', portrait ? 'translate(224,0)' : '');
      if (altG) altG.setAttribute('transform', portrait ? 'translate(-224,0)' : '');
    }
    var prevV15Cleanup = V15_CLEANUPS ? V15_CLEANUPS.get(doc) : null;
    if (prevV15Cleanup) { prevV15Cleanup(); V15_CLEANUPS.delete(doc); }
    var v15Stage = doc.getElementById('v15-hud-stage');
    if (v15Stage) {
      syncV15Viewport();
      var v15Ro = typeof ResizeObserver === 'function' ? new ResizeObserver(syncV15Viewport) : null;
      if (v15Ro) v15Ro.observe(v15Stage);
      if (global.addEventListener) global.addEventListener('resize', syncV15Viewport);
      if (V15_CLEANUPS) {
        V15_CLEANUPS.set(doc, function () {
          if (v15Ro) v15Ro.disconnect();
          if (global.removeEventListener) global.removeEventListener('resize', syncV15Viewport);
        });
      }
    }

    wireChipGroup(doc, 'v16-luminance-chips', null, function (btn, d) {
      const vp = d.getElementById('v16-glass-viewport');
      if (vp && btn.dataset.luminance) vp.setAttribute('data-luminance', btn.dataset.luminance);
      if (vp && btn.dataset.contrast) vp.setAttribute('data-contrast', btn.dataset.contrast);
    });
    const derateBtn = doc.getElementById('v16-derate-btn');
    if (derateBtn && derateBtn.dataset.v16Bound !== '1') {
      derateBtn.dataset.v16Bound = '1';
      derateBtn.addEventListener('click', function () {
        const vp = doc.getElementById('v16-glass-viewport');
        if (!vp) return;
        const on = vp.getAttribute('data-derate') !== 'true';
        vp.setAttribute('data-derate', on ? 'true' : 'false');
        derateBtn.classList.toggle('is-active', on);
        derateBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
        const spd = doc.getElementById('v16-speed-val');
        const cap = doc.getElementById('v16-speed-cap');
        const eta = doc.getElementById('v16-eta-val');
        const pill = doc.getElementById('v16-warn-pill');
        const title = doc.getElementById('v16-warn-title');
        const act = doc.getElementById('v16-warn-action');
        if (spd) spd.textContent = on ? '17.6' : '18.4';
        if (cap) cap.textContent = on ? 'GOVERNED <= 18 kt' : 'HOLD <= 18 kt';
        if (eta) eta.textContent = on ? '04m 05s' : '03m 54s';
        if (pill) {
          pill.setAttribute('data-state', on ? 'nominal' : 'warn');
          pill.textContent = on ? 'GOVERNOR ACTIVE · 17.6 kt' : 'STBD DRIVE DERATE';
        }
        if (title) title.textContent = on ? 'MCU Stabilized (79 °C)' : 'MCU Thermal Limit (85 °C)';
        if (act) act.textContent = on ? 'Governor Holding <= 18 kt · Thermal Margin +6 °C' : 'Hold <= 18 kt · Inspect Aft J1939 Drop at Berth';
      });
    }
    const aisBtn = doc.getElementById('v16-ais-btn');
    if (aisBtn && aisBtn.dataset.v16Bound !== '1') {
      aisBtn.dataset.v16Bound = '1';
      aisBtn.addEventListener('click', function () {
        const vp = doc.getElementById('v16-glass-viewport');
        if (!vp) return;
        const on = vp.getAttribute('data-ais') !== 'true';
        vp.setAttribute('data-ais', on ? 'true' : 'false');
        aisBtn.classList.toggle('is-active', on);
        aisBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    }

    function selectV19Row(target, shouldFocus) {
      doc.querySelectorAll('#v19-triage .v9-triage-row').forEach(function (r) {
        var on = r === target;
        r.setAttribute('aria-selected', on ? 'true' : 'false');
        r.tabIndex = on ? 0 : -1;
      });
      var box = doc.getElementById('v19-triage-detail');
      if (box) box.textContent = target ? (target.dataset.v19Meta || '') : 'No matching items in filter.';
      if (shouldFocus && target && target.focus) target.focus();
    }

    wireChipGroup(doc, 'v19-filter-chips', null, function (btn, d) {
      var want = btn.dataset.v19Filter || 'all';
      var visible = [];
      d.querySelectorAll('#v19-triage .v9-triage-row').forEach(function (r) {
        r.hidden = want !== 'all' && r.dataset.v19State !== want;
        if (!r.hidden) visible.push(r);
      });
      var cur = d.querySelector('#v19-triage .v9-triage-row[aria-selected="true"]');
      if (!cur || cur.hidden) selectV19Row(visible[0] || null, false);
    });
    doc.querySelectorAll('#v19-triage .v9-triage-row').forEach(function (row) {
      row.addEventListener('click', function () { selectV19Row(row, false); });
      row.addEventListener('keydown', function (ev) {
        var vis = Array.prototype.slice.call(doc.querySelectorAll('#v19-triage .v9-triage-row')).filter(function (r) { return !r.hidden; });
        var idx = vis.indexOf(row);
        if (idx < 0 || !vis.length) return;
        var nxt = -1;
        if (ev.key === 'ArrowDown') nxt = Math.min(vis.length - 1, idx + 1);
        else if (ev.key === 'ArrowUp') nxt = Math.max(0, idx - 1);
        else if (ev.key === 'Home') nxt = 0;
        else if (ev.key === 'End') nxt = vis.length - 1;
        if (nxt >= 0) { ev.preventDefault(); selectV19Row(vis[nxt], true); }
      });
    });

    wireChipGroup(doc, 'v20-rubric-chips', null, function (btn, d) {
      var focus = btn.dataset.v20Focus || 'claim';
      d.querySelectorAll('[data-v20-card]').forEach(function (c) {
        c.style.outline = c.dataset.v20Card === focus ? '2px solid var(--accent-focal)' : 'none';
      });
      var note = d.getElementById('v20-focus-note');
      if (note) note.textContent = 'Focus: ' + btn.textContent.trim() + ' inspected against 1.84 V theory';
    });

    wireChipGroup(doc, 'v21-step-chips', null, function (btn, d) {
      var step = btn.dataset.v21Step || 'wire';
      d.querySelectorAll('.v21-step-panel').forEach(function (p) {
        p.hidden = p.dataset.v21Panel !== step;
      });
    });
    var v21Arm = doc.getElementById('v21-handoff-arm');
    var v21Send = doc.getElementById('v21-handoff-send');
    var v21Can = doc.getElementById('v21-handoff-cancel');
    var v21St = doc.getElementById('v21-handoff-status');
    if (v21Arm && v21Send && v21St) {
      var resetV21 = function (sent) {
        v21Arm.classList.remove('is-armed');
        v21Arm.setAttribute('aria-expanded', 'false');
        v21Send.hidden = true;
        if (v21Can) v21Can.hidden = true;
        v21St.dataset.state = sent ? 'nominal' : 'warn';
        v21St.textContent = sent ? 'HANDOFF SENT · 8.0 H' : 'BAY HOLD · PREPARE';
        if (v21Arm.focus) v21Arm.focus();
      };
      v21Arm.addEventListener('click', function () {
        if (v21Arm.getAttribute('aria-expanded') === 'true') { resetV21(false); return; }
        v21Arm.classList.add('is-armed');
        v21Arm.setAttribute('aria-expanded', 'true');
        v21Send.hidden = false;
        if (v21Can) v21Can.hidden = false;
        v21St.dataset.state = 'warn';
        v21St.textContent = 'ARMED · CONFIRM';
      });
      v21Send.addEventListener('click', function () { resetV21(true); });
      if (v21Can) v21Can.addEventListener('click', function () { resetV21(false); });
    }

    var v08View = doc.querySelector('.v9-stage-inner.v9-view-v08');
    var v08Ro = doc.getElementById('v08-ch-readout');
    if (v08View && v08Ro && v08View.dataset.v08Bound !== '1') {
      v08View.dataset.v08Bound = '1';
      var V08_CH = {
        dispatch: { lbl: 'CH1 · Active Dispatch', '15m': 'Min 23.3 MW · Avg 23.6 MW · Max 23.9 MW · Ripple ±0.3 MW (15m)', '1h': 'Min 23.1 MW · Avg 23.6 MW · Max 24.1 MW · Ripple ±0.4 MW (1h)', shift: 'Min 22.4 MW · Avg 23.6 MW · Max 24.4 MW · Ripple ±0.6 MW (Shift)' },
        freq: { lbl: 'CH2 · Grid Frequency', '15m': 'Min 59.981 Hz · Avg 59.985 Hz · Max 59.992 Hz · Ripple ±0.004 Hz (15m)', '1h': 'Min 59.978 Hz · Avg 59.985 Hz · Max 60.004 Hz · Ripple ±0.005 Hz (1h)', shift: 'Min 59.972 Hz · Avg 59.985 Hz · Max 60.012 Hz · Ripple ±0.008 Hz (Shift)' },
        bess: { lbl: 'CH3 · Battery SoC', '15m': 'Min 78.1% · Avg 78.4% · Max 78.9% · Ripple ±0.2% (15m)', '1h': 'Min 77.2% · Avg 78.4% · Max 79.8% · Ripple ±0.5% (1h)', shift: 'Min 74.6% · Avg 78.4% · Max 82.0% · Ripple ±0.9% (Shift)' },
        oee: { lbl: 'CH4 · Cell-03 OEE', '15m': 'Min 93.8% · Avg 94.2% · Max 94.6% · Ripple ±0.3% (15m)', '1h': 'Min 93.4% · Avg 94.2% · Max 95.1% · Ripple ±0.4% (1h)', shift: 'Min 92.6% · Avg 94.2% · Max 95.4% · Ripple ±0.6% (Shift)' },
      };
      var v08Cards = Array.from(v08View.querySelectorAll('.v08-kpi-card[data-v08-ch]'));
      var v08Wins = Array.from(v08View.querySelectorAll('button[data-v08-win]'));
      var v08Hold = doc.getElementById('v08-hold-btn');
      var curCh = 'dispatch', curWin = '1h', held = false;
      var syncV08 = function () {
        var cfg = V08_CH[curCh] || V08_CH.dispatch;
        v08Ro.textContent = (held ? 'HOLD · ' : '') + cfg.lbl + ' — ' + (cfg[curWin] || cfg['1h']);
      };
      v08Cards.forEach(function (card) {
        var pickCard = function () {
          curCh = card.getAttribute('data-v08-ch') || 'dispatch';
          v08Cards.forEach(function (c) { var on = c === card; c.classList.toggle('is-v08-selected', on); c.setAttribute('aria-pressed', on ? 'true' : 'false'); });
          syncV08();
        };
        card.addEventListener('click', pickCard);
        card.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pickCard(); } });
      });
      v08Wins.forEach(function (btn) {
        btn.addEventListener('click', function () {
          curWin = btn.getAttribute('data-v08-win') || '1h';
          v08Wins.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
          syncV08();
        });
      });
      if (v08Hold) {
        v08Hold.addEventListener('click', function () {
          held = !held;
          v08View.setAttribute('data-v08-hold', held ? 'true' : 'false');
          v08Hold.setAttribute('aria-pressed', held ? 'true' : 'false');
          v08Hold.textContent = held ? 'HOLDING' : 'Hold Display';
          syncV08();
        });
      }
    }
  }

  global.QuietWorlds02To05Runtime = { boot: wireWorlds02To05 };
})(typeof window !== 'undefined' ? window : globalThis);
