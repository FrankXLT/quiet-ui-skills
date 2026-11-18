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

    wireChipGroup(doc, 'v15-backplate-chips', null, function (btn, d) {
      const stage = d.getElementById('v15-hud-stage');
      if (stage && btn.dataset.backplate) stage.setAttribute('data-backplate', btn.dataset.backplate);
    });

    wireChipGroup(doc, 'v16-luminance-chips', null, function (btn, d) {
      const vp = d.getElementById('v16-glass-viewport');
      if (vp && btn.dataset.luminance) vp.setAttribute('data-luminance', btn.dataset.luminance);
      if (vp && btn.dataset.contrast) vp.setAttribute('data-contrast', btn.dataset.contrast);
    });
  }

  global.QuietWorlds02To05Runtime = { boot: wireWorlds02To05 };
})(typeof window !== 'undefined' ? window : globalThis);
