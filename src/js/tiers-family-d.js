/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.2 — Family D Tier Event Controllers (HUD-1, Ctrl-1)
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

  // --- HUD-1: Collimated Optical Viewport Backplate & Mode Controller ---
  window.setHudBackplate = function(mode, btn) {
    const vp = document.getElementById('hud1-viewport') || document.querySelector('.hud1-viewport');
    if (vp) vp.setAttribute('data-backplate', mode);
    activateSiblingBtn(btn);
  };

  // --- Ctrl-1: Tactile Subsystem Mission Control ---
  window.toggleCtrlZone = function(zone, btn) {
    activateSiblingBtn(btn);
    ['eclss', 'pwr', 'tcs', 'opt'].forEach(function(z) {
      const deck = document.getElementById('ctrl-deck-' + z);
      if (deck) deck.style.display = (z === zone) ? 'block' : 'none';
    });
  };

  window.stepCtrlSetpoint = function(btn, delta) {
    const card = btn ? btn.closest('.ctrl1-effector-card') : null;
    const valEl = card ? card.querySelector('.ctrl-cmd-val, .ctrl1-setpoint-val') : null;
    if (valEl) {
      const cur = parseFloat(valEl.textContent) || 0;
      const unit = valEl.textContent.indexOf('kPa') !== -1 ? ' kPa' : (valEl.textContent.indexOf('°C') !== -1 ? ' °C' : ' W');
      valEl.textContent = (cur + delta).toFixed(1) + unit;
    }
  };

  // Two-Step Guarded Actuation (ARM -> EXECUTE) with 5-second safety disarm timeout
  const armTimers = {};

  window.armGuardedActuator = function(actuatorId, armBtn) {
    const card = armBtn ? armBtn.closest('.guarded-actuator-card') : document.querySelector('[data-actuator="' + actuatorId + '"]');
    if (!card) return;
    const execBtn = card.querySelector('.execute-btn');
    const isArmed = card.classList.contains('is-armed');

    if (isArmed) {
      // Disarm manually
      disarmActuator(actuatorId, card, armBtn, execBtn);
    } else {
      // Engage Arm state
      card.classList.add('is-armed');
      armBtn.classList.add('is-active');
      armBtn.setAttribute('aria-pressed', 'true');
      armBtn.innerHTML = '<i class="fa-solid fa-lock-open"></i> DISARM (5s)';
      if (execBtn) execBtn.removeAttribute('disabled');

      // Start 5s countdown
      let remaining = 5;
      if (armTimers[actuatorId]) clearInterval(armTimers[actuatorId]);
      armTimers[actuatorId] = setInterval(function() {
        remaining--;
        if (remaining > 0) {
          armBtn.innerHTML = '<i class="fa-solid fa-lock-open"></i> DISARM (' + remaining + 's)';
        } else {
          disarmActuator(actuatorId, card, armBtn, execBtn);
        }
      }, 1000);
    }
  };

  function disarmActuator(actuatorId, card, armBtn, execBtn) {
    if (armTimers[actuatorId]) {
      clearInterval(armTimers[actuatorId]);
      delete armTimers[actuatorId];
    }
    card.classList.remove('is-armed');
    if (armBtn) {
      armBtn.classList.remove('is-active');
      armBtn.setAttribute('aria-pressed', 'false');
      armBtn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> ARM';
    }
    if (execBtn) execBtn.setAttribute('disabled', 'disabled');
  }

  window.executeGuardedAction = function(actuatorId, execBtn) {
    const card = execBtn ? execBtn.closest('.guarded-actuator-card') : document.querySelector('[data-actuator="' + actuatorId + '"]');
    if (!card || !card.classList.contains('is-armed')) return;

    const armBtn = card.querySelector('.arm-btn');
    const actState = card.querySelector('.act-state .state-val');
    const transit = card.querySelector('.transit-dot');

    if (transit) transit.classList.add('is-transiting');
    if (actState) actState.textContent = 'TRANSIT';

    setTimeout(function() {
      if (transit) transit.classList.remove('is-transiting');
      if (actState) actState.textContent = 'CONFIRMED';
    }, 1200);

    disarmActuator(actuatorId, card, armBtn, execBtn);
  };

  // Interactive P&ID Loop Valve Toggle
  window.togglePidValve = function(valveId) {
    const node = document.querySelector('[data-valve="' + valveId + '"]');
    if (!node) return;
    node.classList.toggle('is-open');
    const statusText = document.getElementById('pid-status-readout');
    if (statusText) {
      const isOpen = node.classList.contains('is-open');
      statusText.textContent = 'Valve ' + valveId + ' // ' + (isOpen ? 'FLOW ENGAGED' : 'ISOLATED');
    }
  };

  // Annunciator Alarm Acknowledgment
  window.acknowledgeAlarm = function(alarmId) {
    const cell = document.querySelector('[data-alarm="' + alarmId + '"]');
    if (cell) {
      cell.classList.remove('is-warning');
      cell.classList.add('is-nominal');
      const btn = cell.querySelector('.ann-ack-btn');
      if (btn) btn.style.display = 'none';
    }
  };

})(typeof window !== 'undefined' ? window : this);
