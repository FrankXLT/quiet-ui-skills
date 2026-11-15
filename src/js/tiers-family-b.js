/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.2 — Family B Tier Event Controllers (Bridge-1, Deck-1, Bridge-2, App-2)
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

  // --- Bridge-1: Parametric Link Budget Solver & Coupled Multi-Mission Ledger ---
  const MISSION_PROFILES = [
    { id: 'm1', name: 'DSOC Psyche Cruise', baseDist: 2.6, reqMargin: 3.0 },
    { id: 'm2', name: 'Mars 2026 Opposition', baseDist: 0.52, reqMargin: 4.5 },
    { id: 'm3', name: 'Europa Clipper Relay', baseDist: 5.2, reqMargin: 2.5 },
    { id: 'm4', name: 'Titan Dragonfly En Route', baseDist: 9.5, reqMargin: 2.0 },
    { id: 'm5', name: 'Deep Space Lunar Gateway', baseDist: 0.0026, reqMargin: 6.0 },
    { id: 'm6', name: 'JWST L2 Halo Orbit', baseDist: 0.01, reqMargin: 5.5 },
    { id: 'm7', name: 'Lagrange Sun-Earth L1', baseDist: 0.01, reqMargin: 5.5 },
    { id: 'm8', name: 'Asteroid Sample Return', baseDist: 1.8, reqMargin: 3.5 }
  ];

  window.updateBridge1Calc = function() {
    const distEl = document.getElementById('b1-dist-au');
    const apEl = document.getElementById('b1-aperture-cm');
    const pwrEl = document.getElementById('b1-power-w');
    const effEl = document.getElementById('b1-eff-pct');
    if (!distEl || !apEl || !pwrEl) return;

    const r = parseFloat(distEl.value) || 1.0;
    const d = parseFloat(apEl.value) || 22;
    const p = parseFloat(pwrEl.value) || 1250;
    const eff = effEl ? (parseFloat(effEl.value) || 45) : 45;

    const setTxt = function(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; };
    setTxt('b1-dist-val', r.toFixed(2) + ' AU');
    setTxt('b1-aperture-val', d.toFixed(0) + ' cm');
    setTxt('b1-power-val', p.toFixed(0) + ' W');
    if (effEl) setTxt('b1-eff-val', eff.toFixed(0) + '%');

    // Link physics calculation
    const rate = Math.min(267.0, Math.max(0.5, 67.5 * Math.pow(1.0 / r, 2) * Math.pow(d / 22.0, 2) * (p / 1250.0) * (eff / 45.0)));
    const margin = Math.max(-2.0, Math.min(14.0, 4.2 + 3.0 * Math.log10((d / 22.0) * (p / 1250.0) * (eff / 45.0) / r)));

    setTxt('b1-rate-out', rate.toFixed(1) + ' Mbps');
    setTxt('b1-margin-out', (margin >= 0 ? '+' : '') + margin.toFixed(1) + ' dB');
    setTxt('b1-ppm-out', rate >= 120 ? 'M=16 SCPPM' : (rate >= 25 ? 'M=64 SCPPM' : 'M=128 SCPPM'));

    const dot = document.getElementById('b1-op-dot');
    if (dot) {
      dot.setAttribute('cx', (50 + Math.min(1.0, (r - 0.1) / 2.7) * 380).toFixed(1));
      dot.setAttribute('cy', (172 - (Math.log10(rate) / Math.log10(267.0)) * 140).toFixed(1));
    }

    // Coupled Multi-Mission Ledger Update
    MISSION_PROFILES.forEach(function(m) {
      const row = document.getElementById('b1-row-' + m.id);
      if (!row) return;
      const mRatio = m.baseDist / r;
      const mRate = Math.min(267.0, Math.max(0.1, rate * Math.pow(1.0 / mRatio, 2)));
      const mMargin = margin - 3.0 * Math.log10(mRatio);
      const isPass = mMargin >= m.reqMargin;

      const rateCell = row.querySelector('.col-rate');
      const marginCell = row.querySelector('.col-margin');
      const statusCell = row.querySelector('.col-status');

      if (rateCell) rateCell.textContent = mRate >= 1.0 ? mRate.toFixed(1) + ' Mbps' : (mRate * 1000).toFixed(0) + ' kbps';
      if (marginCell) marginCell.textContent = (mMargin >= 0 ? '+' : '') + mMargin.toFixed(1) + ' dB';
      if (statusCell) {
        statusCell.innerHTML = isPass ?
          '<span class="sq-status sq-ok"></span>PASS' :
          '<span class="sq-status sq-warn"></span>MARGINAL';
      }
    });
  };

  // --- Deck-1: 100dvh Briefing Slides & Narrative Step Stepper ---
  let currentDeckSlide = 1;
  let currentDeckStep = 0;

  window.setDeck1Slide = function(n) {
    currentDeckSlide = Math.max(1, Math.min(4, n));
    currentDeckStep = 0;
    document.querySelectorAll('.deck1-slide-pill').forEach(function(b, i) {
      b.classList.toggle('active', i + 1 === currentDeckSlide);
    });
    for (let i = 1; i <= 4; i++) {
      const v = document.getElementById('deck1-viz-' + i);
      if (v) v.style.display = (i === currentDeckSlide) ? 'block' : 'none';
    }
    const badge = document.getElementById('deck1-counter-badge');
    if (badge) badge.textContent = 'SLIDE 0' + currentDeckSlide + ' / 04 · STEP ' + (currentDeckStep + 1) + '/3';
    updateDeckStepCards();
  };

  function updateDeckStepCards() {
    const viz = document.getElementById('deck1-viz-' + currentDeckSlide);
    if (!viz) return;
    viz.querySelectorAll('.deck-step-card').forEach(function(card, idx) {
      card.classList.toggle('is-active', idx === currentDeckStep);
    });
  }

  window.selectDeckStep = function(stepIdx) {
    currentDeckStep = Math.max(0, Math.min(2, stepIdx));
    const badge = document.getElementById('deck1-counter-badge');
    if (badge) badge.textContent = 'SLIDE 0' + currentDeckSlide + ' / 04 · STEP ' + (currentDeckStep + 1) + '/3';
    updateDeckStepCards();
  };

  window.advanceDeckStepOrSlide = function() {
    if (currentDeckStep < 2) {
      selectDeckStep(currentDeckStep + 1);
    } else {
      window.setDeck1Slide(currentDeckSlide < 4 ? currentDeckSlide + 1 : 1);
    }
  };

  window.updateDeck1Beam = function() {
    const nEl = document.getElementById('deck1-slider-n');
    const sllEl = document.getElementById('deck1-slider-sll');
    if (!nEl || !sllEl) return;
    const n = parseInt(nEl.value, 10) || 64;
    const sll = parseInt(sllEl.value, 10) || 44;
    const setTxt = function(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; };
    setTxt('deck1-val-n', n + ' Elements');
    setTxt('deck1-val-sll', '-' + sll + ' dBc');
    setTxt('deck1-kpi-gain', '+' + (28.7 + 3.0 * Math.log2(n / 16)).toFixed(1) + ' dBi');
    setTxt('deck1-kpi-sll', '-' + sll.toFixed(1) + ' dBc');
    const line = document.getElementById('deck1-sll-line');
    if (line) { const y = 80 + (sll - 20) * 1.6; line.setAttribute('y1', y); line.setAttribute('y2', y); }
    const poly = document.getElementById('deck1-beam-poly');
    if (poly) {
      const half = Math.max(24, 96 - n * 0.45);
      poly.setAttribute('points', '260,30 ' + (260 - half).toFixed(0) + ',180 ' + (260 + half).toFixed(0) + ',180');
    }
  };

  // --- Bridge-2: High-Density 12-Aperture Fleet Filtering ---
  window.filterBridge2 = function(complex, btn) {
    activateSiblingBtn(btn);
    const target = (complex || 'ALL').toUpperCase();
    document.querySelectorAll('#bridge2-table tbody tr[data-complex]').forEach(function(tr) {
      const c = (tr.getAttribute('data-complex') || '').toUpperCase();
      tr.style.display = (target === 'ALL' || c === target) ? '' : 'none';
    });
  };

  // --- App-2: Synchronized Waveform Cursor Scrubbing ---
  window.scrubApp2Wave = function(ev) {
    const rect = ev.currentTarget.getBoundingClientRect();
    const x = Math.max(20, Math.min(580, ((ev.clientX - rect.left) / Math.max(1, rect.width)) * 600));
    document.querySelectorAll('.hil-cursor-line').forEach(function(line) {
      line.setAttribute('x1', x.toFixed(1));
      line.setAttribute('x2', x.toFixed(1));
    });
    const readout = document.getElementById('app2-cursor-readout');
    if (readout) {
      const ps = ((x - 300) * 0.08).toFixed(2);
      readout.textContent = 'Cursor: T+' + Math.round(x * 0.85) + 'ms · Phase Skew: ' + (parseFloat(ps) >= 0 ? '+' : '') + ps + ' ps · SNSPD Array Locked';
    }
  };

})(typeof window !== 'undefined' ? window : this);
