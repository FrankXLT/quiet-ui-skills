/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.2 — Family C Tier Event Controllers (App-1, App-4, App-3, App-5, App-Tree)
 */
(function(window) {
  'use strict';

  function activateSiblingBtn(btn) {
    if (btn && btn.parentElement) {
      btn.parentElement.querySelectorAll('button').forEach(function(b) {
        b.classList.remove('active', 'is-active');
      });
      btn.classList.add('active', 'is-active');
    }
  }

  // --- App-1: Flight Discrepancy Queue & Live Inspector ---
  const DISCREPANCY_DATA = {
    'DISC-0101': {
      title: 'Carrier phase jitter excursion on Palomar Hale receiver',
      subsystem: 'COMM // GROUND-RX',
      severity: 'CRIT',
      reported: '14:22 UTC',
      rootCause: 'Cryogenic compressor pressure oscillation induced microphonic vibration on SNSPD array.',
      disposition: 'Activated spatial diversity mode; transitioned downlink tracking to DSS-13 Goldstone.'
    },
    'DISC-0102': {
      title: 'Fine Steering Mirror point-ahead angle slew lag',
      subsystem: 'GNC // OPT-POINTING',
      severity: 'WARN',
      reported: '13:58 UTC',
      rootCause: 'Thermal gradient across piezo actuator bridge caused 1.8 urad closed-loop hysteresis.',
      disposition: 'Recalibrated bias offset look-up table; hysteresis reduced to 0.12 urad.'
    },
    'DISC-0103': {
      title: 'BCJR soft decoder iteration budget exceeded (>10)',
      subsystem: 'COMM // BASEBAND-FPGA',
      severity: 'WARN',
      reported: '12:45 UTC',
      rootCause: 'Atmospheric scintillation drop lowered channel SNR below 12.0 dB.',
      disposition: 'Dynamically adapted modulation order from M=16 to M=64; zero frame losses.'
    }
  };

  window.filterApp1Queue = function(status, btn) {
    activateSiblingBtn(btn);
    const target = (status || 'ALL').toUpperCase();
    document.querySelectorAll('.app1-triage-row').forEach(function(r) {
      const s = (r.getAttribute('data-status') || '').toUpperCase();
      r.style.display = (target === 'ALL' || s === target) ? '' : 'none';
    });
  };

  window.selectApp1Discrepancy = function(discId, rowEl) {
    document.querySelectorAll('.app1-triage-row').forEach(function(r) { r.classList.remove('is-active'); });
    if (rowEl) rowEl.classList.add('is-active');

    const data = DISCREPANCY_DATA[discId] || DISCREPANCY_DATA['DISC-0101'];
    const idEl = document.getElementById('app1-insp-id');
    const titleEl = document.getElementById('app1-insp-title');
    const causeEl = document.getElementById('app1-insp-cause');
    const dispEl = document.getElementById('app1-insp-disp');

    if (idEl) idEl.textContent = discId;
    if (titleEl) titleEl.textContent = data.title;
    if (causeEl) causeEl.textContent = data.rootCause;
    if (dispEl) dispEl.textContent = data.disposition;
  };

  // --- App-4: Focus Hero Timer & NRHO Task List ---
  let focusSeconds = 45 * 60;
  let focusInterval = null;

  window.adjustFocusTimer = function(minutes) {
    focusSeconds = Math.max(0, focusSeconds + minutes * 60);
    updateFocusDisplay();
  };

  function updateFocusDisplay() {
    const min = Math.floor(focusSeconds / 60);
    const sec = focusSeconds % 60;
    const digits = document.getElementById('focus-timer-digits');
    if (digits) {
      digits.textContent = (min < 10 ? '0' : '') + min + ':' + (sec < 10 ? '0' : '') + sec;
    }
  }

  window.toggleFocusPlay = function(btn) {
    if (focusInterval) {
      clearInterval(focusInterval);
      focusInterval = null;
      if (btn) btn.innerHTML = '<i class="fa-solid fa-play"></i> Resume';
    } else {
      focusInterval = setInterval(function() {
        if (focusSeconds > 0) {
          focusSeconds--;
          updateFocusDisplay();
        } else {
          clearInterval(focusInterval);
          focusInterval = null;
          if (btn) btn.innerHTML = '<i class="fa-solid fa-check"></i> Done';
        }
      }, 1000);
      if (btn) btn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause';
    }
  };

  window.toggleApp4Task = function(cb) {
    const list = cb ? cb.closest('.app4-task-list') : null;
    if (!list) return;
    const total = list.querySelectorAll('input[type="checkbox"]').length;
    const done = list.querySelectorAll('input[type="checkbox"]:checked').length;
    const label = document.getElementById('app4-progress-label');
    if (label) label.textContent = 'Orbit 142 · NRHO Perilune Window · ' + done + ' of ' + total + ' Tasks Complete';
  };

  // --- App-3: Complete 6-Card Bento Time Horizon Switcher ---
  window.setApp3Horizon = function(horizon, btn) {
    activateSiblingBtn(btn);
    const multiplier = { '24H': 1.0, '7D': 6.8, '30D': 28.5, 'ORBIT': 142.0 }[horizon] || 1.0;
    const volEl = document.getElementById('bento-vol-val');
    const paceEl = document.getElementById('bento-pace-delta');
    if (volEl) volEl.textContent = (4.2 * multiplier).toFixed(1) + ' TB';
    if (paceEl) paceEl.textContent = '+' + (0.6 * multiplier).toFixed(1) + ' TB ahead';
  };

  // --- App-5: Circadian Phase Switcher ---
  window.setApp5Phase = function(phase, btn) {
    activateSiblingBtn(btn);
    const el = document.getElementById('app5-phase-status');
    if (!el) return;
    const copy = {
      presleep: 'Phase: Pre-Sleep Shift · 4100K to 2700K Lighting Active · Cabin <= 40 dBA',
      sortie: 'Phase: Pre-Sortie Briefing · Cognitive Readiness 96% · Circadian Anchor Confirmed',
      nominal: 'Phase: Nominal Orbit · 8.0h Sleep Opportunity Protected · Melatonin Alignment Nominal'
    };
    el.textContent = copy[phase] || copy.nominal;
  };

  // --- App-Tree: 3-Pane Explorer Navigation & CCSDS Row Inspector ---
  window.selectTreeNode = function(nodeId, el) {
    document.querySelectorAll('#tier-app-tree .tree-node').forEach(function(l) { l.classList.remove('is-active'); });
    if (el) el.classList.add('is-active');
    const nameEl = document.getElementById('apptree-table-name');
    if (nameEl) nameEl.textContent = 'TABLE // ' + (nodeId || 'ccsds_space_packets');
  };

  window.selectCcsdsRow = function(rowEl, apid, seqCount) {
    document.querySelectorAll('#apptree-packet-table tbody tr').forEach(function(r) { r.classList.remove('is-selected'); });
    if (rowEl) rowEl.classList.add('is-selected');

    const apidEl = document.getElementById('insp-apid');
    const seqEl = document.getElementById('insp-seq');
    if (apidEl) apidEl.textContent = apid || '0x0428';
    if (seqEl) seqEl.textContent = seqCount || '14285';
  };

  window.setAppTreeTab = function(tabName, btn) {
    activateSiblingBtn(btn);
    ['data', 'spec', 'lineage'].forEach(function(t) {
      const panel = document.getElementById('apptree-tab-' + t);
      if (panel) panel.style.display = (t === tabName) ? 'block' : 'none';
    });
  };

  window.setAppTreeMobilePane = function(pane, btn) {
    activateSiblingBtn(btn);
    const explorer = document.querySelector('#tier-app-tree .apptree-explorer') || document.querySelector('.apptree-explorer');
    if (explorer) explorer.setAttribute('data-mobile-pane', pane || 'tree');
  };

})(typeof window !== 'undefined' ? window : this);
