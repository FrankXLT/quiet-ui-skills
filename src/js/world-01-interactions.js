/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 — World 01 Interactive Controllers (v01 Titration Guard, v02 Subgroup Filter, v03 Pedagogical Chips)
 */
(function (window, document) {
  'use strict';

  const armTimers = {};

  function prependAuditEntry(doc, message) {
    const list = doc.getElementById('v01-audit-list');
    if (!list) return;
    const item = doc.createElement('div');
    item.className = 'v01-audit-item';
    const stamp = new Date().toISOString().slice(11, 19) + 'Z';
    item.textContent = '[' + stamp + '] ' + message;
    list.insertBefore(item, list.firstChild);
    while (list.children.length > 5) {
      list.removeChild(list.lastChild);
    }
  }

  function clearNorepiTimer() {
    if (armTimers.norepi) {
      window.clearInterval(armTimers.norepi);
      delete armTimers.norepi;
    }
  }

  function disarmTitration(doc, card, armBtn, execBtn) {
    clearNorepiTimer();
    if (card) card.classList.remove('is-armed');
    if (armBtn) {
      armBtn.classList.remove('is-armed');
      armBtn.setAttribute('aria-pressed', 'false');
      armBtn.textContent = '2. ARM Norepinephrine +0.02';
    }
    if (execBtn) execBtn.disabled = true;
  }

  function bindV01Titration(doc) {
    const card = doc.getElementById('v01-titration-card');
    if (!card || card.dataset.bound === '1') return;
    card.dataset.bound = '1';

    const zeroBtn = doc.getElementById('v01-zero-btn');
    const armBtn = doc.getElementById('v01-arm-btn');
    const execBtn = doc.getElementById('v01-exec-btn');
    const stateEl = doc.getElementById('v01-titration-state');

    if (zeroBtn) {
      zeroBtn.addEventListener('click', function () {
        const verified = zeroBtn.classList.toggle('is-verified');
        zeroBtn.setAttribute('aria-pressed', verified ? 'true' : 'false');
        zeroBtn.textContent = verified ? '1. Transducer Zero Verified' : '1. Zero Transducer Check';
        if (stateEl) stateEl.textContent = verified ? 'TRANSDUCER ZEROED' : 'HOLD FOR ZERO CHECK';
        prependAuditEntry(doc, verified
          ? 'Transducer zero-line check verified after 2.4 s artifact (MAP 63.5 mmHg confirmed).'
          : 'Transducer zero verification cleared; hold vasopressor titration.');
      });
    }

    if (armBtn) {
      armBtn.addEventListener('click', function () {
        if (card.classList.contains('is-armed')) {
          disarmTitration(doc, card, armBtn, execBtn);
          if (stateEl) stateEl.textContent = 'DISARMED';
          prependAuditEntry(doc, 'Manual disarm: Norepinephrine +0.02 ug/(kg*min) increment held.');
          return;
        }
        const zeroDone = zeroBtn && zeroBtn.classList.contains('is-verified');
        if (!zeroDone) {
          prependAuditEntry(doc, 'Advisory: verify radial transducer zero after 2.4 s dropout before executing.');
        }
        clearNorepiTimer();
        card.classList.add('is-armed');
        armBtn.classList.add('is-armed');
        armBtn.setAttribute('aria-pressed', 'true');
        if (execBtn) execBtn.disabled = false;
        let remaining = 5;
        armBtn.textContent = 'DISARM (' + remaining + 's)';
        if (stateEl) stateEl.textContent = 'ARMED (5s GUARD)';
        const timerId = window.setInterval(function () {
          if (armTimers.norepi !== timerId || !card.isConnected) {
            window.clearInterval(timerId);
            return;
          }
          remaining -= 1;
          if (remaining > 0) {
            armBtn.textContent = 'DISARM (' + remaining + 's)';
          } else {
            disarmTitration(doc, card, armBtn, execBtn);
            if (stateEl) stateEl.textContent = 'AUTO-DISARMED (5s)';
            prependAuditEntry(doc, '5 s IEC 62366 auto-disarm timeout elapsed; pump rate unchanged.');
          }
        }, 1000);
        armTimers.norepi = timerId;
      });
    }

    if (execBtn) {
      execBtn.addEventListener('click', function () {
        if (!card.classList.contains('is-armed')) return;
        const rateEl = doc.getElementById('v01-norepi-rate');
        if (rateEl) {
          const cur = parseFloat(rateEl.textContent) || 0.08;
          rateEl.textContent = (cur + 0.02).toFixed(2) + ' µg/(kg·min)';
        }
        if (stateEl) stateEl.textContent = 'EXECUTED +0.02';
        prependAuditEntry(doc, 'EXECUTED guarded Norepinephrine titration +0.02 ug/(kg*min) with audit stamp.');
        disarmTitration(doc, card, armBtn, execBtn);
      });
    }
  }

  function bindV02SubgroupChips(doc) {
    const bar = doc.getElementById('v02-subgroup-chips');
    if (!bar || bar.dataset.bound === '1') return;
    bar.dataset.bound = '1';
    const readout = doc.getElementById('v02-filter-readout');

    bar.querySelectorAll('button[data-subgroup]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        bar.querySelectorAll('button[data-subgroup]').forEach(function (b) {
          b.classList.remove('is-active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('is-active');
        btn.setAttribute('aria-pressed', 'true');
        const msg = btn.getAttribute('data-summary') || '';
        if (readout && msg) readout.textContent = msg;

        const key = btn.getAttribute('data-subgroup') || 'all';
        const rows = doc.querySelectorAll('#v02-trial-adverse-events-table tbody tr');
        rows.forEach(function (tr, idx) {
          const match = key === 'all' || (key === 'sofa' && idx <= 2) || (key === 'lactate' && idx <= 2) || (key === 'age' && idx >= 1) || (key === 'overall');
          tr.style.opacity = match ? '1' : '0.45';
        });
      });
    });
  }

  function bindShellSupport(doc) {
    if (doc.__quietShellSupportBound) return;
    doc.__quietShellSupportBound = true;
    doc.addEventListener('click', function (ev) {
      const link = ev.target && ev.target.closest ? ev.target.closest('a[href^="#"]') : null;
      if (!link) return;
      ev.preventDefault();
      const id = (link.getAttribute('href') || '').slice(1);
      const target = id ? doc.getElementById(id) : null;
      if (target && typeof target.scrollIntoView === 'function') {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        const main = doc.getElementById('va-stage-main');
        if (main) main.scrollTop = 0;
      }
    });
    const drawer = doc.getElementById('va-shell-drawer');
    if (drawer && !('closedBy' in HTMLDialogElement.prototype)) {
      let outsideDown = false;
      const outside = function (e) {
        const r = drawer.getBoundingClientRect();
        return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      };
      drawer.addEventListener('pointerdown', function (e) { outsideDown = outside(e); });
      drawer.addEventListener('pointerup', function (e) {
        if (outsideDown && outside(e)) drawer.close();
        outsideDown = false;
      });
    }
  }

  function boot(docRef) {
    const d = docRef || document;
    clearNorepiTimer();
    bindShellSupport(d);
    bindV01Titration(d);
    bindV02SubgroupChips(d);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { boot(document); });
  } else {
    boot(document);
  }

  window.QuietWorld01Runtime = { boot: boot };
})(window, document);
