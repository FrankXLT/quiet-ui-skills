/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.0 Gate 5.5 — World 06 (v17 & v18) Client Interactions */
(function (global) {
  'use strict';

  var V17_SCENES = {
    morning: { time: '7:15 AM', meta: 'Morning Routine · Clear ', c: '12 °C', f: '54 °F', energy: 'Solar 5.8 kW · Battery 91%', sub: 'Shades Open 85% · All 6 Leak Sensors Dry' },
    evening: { time: '7:42 PM', meta: 'Wed, Nov 18 · Clear ', c: '14 °C', f: '57 °F', energy: 'Solar 4.8 kW · Battery 84%', sub: 'Evening Scene · All 6 Leak Sensors Dry' },
    movie: { time: '8:30 PM', meta: 'Cinema Lights 15% · Clear ', c: '13 °C', f: '55 °F', energy: 'Media Load 0.4 kW · Battery 82%', sub: 'Theater Dimmed · All 6 Leak Sensors Dry' },
    goodnight: { time: '10:45 PM', meta: 'Doors Armed · Clear ', c: '11 °C', f: '52 °F', energy: 'Grid Standby · Battery 80%', sub: 'Night Setback · All 6 Leak Sensors Dry' }
  };

  function applyTempUnit(root, unit) {
    if (!root) return;
    var u = unit === 'f' ? 'f' : 'c';
    root.setAttribute('data-temp-unit', u);
    root.querySelectorAll('[data-temp-c][data-temp-f]').forEach(function (el) {
      el.textContent = u === 'f' ? el.getAttribute('data-temp-f') : el.getAttribute('data-temp-c');
    });
    var spEl = root.querySelector('#v17-sp-val');
    if (spEl) {
      var c = parseFloat(spEl.getAttribute('data-setpoint-c') || '21.0');
      var fAttr = spEl.getAttribute('data-setpoint-f');
      var fVal = fAttr ? parseInt(fAttr, 10) : Math.round(c * 9 / 5 + 32);
      spEl.textContent = u === 'f' ? (fVal + ' °F') : (c.toFixed(1) + ' °C');
    }
  }

  function bootV17(doc) {
    var vp = doc.getElementById('v17-kiosk');
    if (!vp || vp.dataset.v06Bound === '1') return;
    vp.dataset.v06Bound = '1';

    vp.querySelectorAll('button[data-v17-backdrop]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var mode = btn.dataset.v17Backdrop || 'art';
        vp.dataset.v17Backdrop = mode;
        vp.querySelectorAll('button[data-v17-backdrop]').forEach(function (b) {
          var active = b.dataset.v17Backdrop === mode;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        vp.querySelectorAll('.v17-art-photo').forEach(function (img) {
          img.classList.toggle('is-active', img.dataset.backdrop === mode);
        });
      });
    });

    vp.querySelectorAll('button[data-v17-scene]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var scene = btn.dataset.v17Scene || 'evening';
        vp.dataset.v17Scene = scene;
        vp.querySelectorAll('button[data-v17-scene]').forEach(function (b) {
          var active = b.dataset.v17Scene === scene;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        var sc = V17_SCENES[scene];
        if (sc) {
          var clk = vp.querySelector('#v17-clock-time');
          var meta = vp.querySelector('#v17-clock-meta');
          var eng = vp.querySelector('#v17-energy-main');
          var sub = vp.querySelector('#v17-energy-sub');
          if (clk) clk.textContent = sc.time;
          if (eng) eng.textContent = sc.energy;
          if (sub) sub.textContent = sc.sub;
          if (meta) {
            meta.innerHTML = '';
            meta.appendChild(doc.createTextNode(sc.meta));
            var tSpan = doc.createElement('span');
            tSpan.className = 'v17-temp-num';
            tSpan.setAttribute('data-temp-c', sc.c);
            tSpan.setAttribute('data-temp-f', sc.f);
            tSpan.textContent = sc.c;
            meta.appendChild(tSpan);
          }
          applyTempUnit(vp, vp.getAttribute('data-temp-unit') || 'c');
        }
      });
    });

    function nudgeSetpoint(step) {
      var spEl = vp.querySelector('#v17-sp-val');
      if (!spEl) return;
      var unit = vp.getAttribute('data-temp-unit') || 'c';
      if (unit === 'f') {
        var curF = parseInt(spEl.getAttribute('data-setpoint-f') || '70', 10);
        var nextF = Math.max(63, Math.min(77, curF + (step > 0 ? 1 : -1)));
        var nextC = Math.round(((nextF - 32) * 5 / 9) * 2) / 2;
        spEl.setAttribute('data-setpoint-f', String(nextF));
        spEl.setAttribute('data-setpoint-c', nextC.toFixed(1));
      } else {
        var curC = parseFloat(spEl.getAttribute('data-setpoint-c') || '21.0');
        var adjC = Math.max(17.0, Math.min(25.0, Math.round((curC + (step > 0 ? 0.5 : -0.5)) * 2) / 2));
        spEl.setAttribute('data-setpoint-c', adjC.toFixed(1));
        spEl.setAttribute('data-setpoint-f', String(Math.round(adjC * 9 / 5 + 32)));
      }
      applyTempUnit(vp, unit);
    }
    var spDown = doc.getElementById('v17-sp-down');
    var spUp = doc.getElementById('v17-sp-up');
    if (spDown) spDown.addEventListener('click', function () { nudgeSetpoint(-0.5); });
    if (spUp) spUp.addEventListener('click', function () { nudgeSetpoint(0.5); });

    var matBtn = doc.getElementById('v17-mat-btn');
    if (matBtn) {
      matBtn.addEventListener('click', function () {
        var next = (vp.getAttribute('data-v17-mat') || 'linen') === 'linen' ? 'obsidian' : 'linen';
        vp.setAttribute('data-v17-mat', next);
        var dark = next === 'obsidian';
        matBtn.classList.toggle('is-active', dark);
        matBtn.setAttribute('aria-pressed', dark ? 'true' : 'false');
        matBtn.textContent = dark ? 'Linen Mat' : 'Dark Mat';
      });
    }

    var unitBtn = doc.getElementById('v17-unit-btn');
    if (unitBtn) {
      unitBtn.addEventListener('click', function () {
        var next = (vp.getAttribute('data-temp-unit') || 'c') === 'c' ? 'f' : 'c';
        applyTempUnit(vp, next);
        unitBtn.setAttribute('data-v17-unit', next);
        unitBtn.classList.toggle('is-active', next === 'f');
        unitBtn.setAttribute('aria-pressed', next === 'f' ? 'true' : 'false');
      });
    }
  }

  function wireTwoStep(doc, cfg) {
    var armBtn = doc.getElementById(cfg.armId);
    var execBtn = doc.getElementById(cfg.execId);
    var pill = doc.getElementById(cfg.pillId);
    var log = doc.getElementById('v18-sec-log');
    if (!armBtn || !execBtn || !pill) return;
    var active = false;

    armBtn.addEventListener('click', function () {
      var armed = armBtn.getAttribute('aria-pressed') !== 'true';
      armBtn.setAttribute('aria-pressed', armed ? 'true' : 'false');
      execBtn.disabled = !armed;
      if (log && armed) {
        log.textContent = cfg.name + ' ready \u2014 tap Step 2 to confirm';
      }
    });

    execBtn.addEventListener('click', function () {
      if (execBtn.disabled) return;
      active = !active;
      pill.textContent = active ? cfg.openLabel : cfg.closedLabel;
      pill.dataset.state = active ? 'warn' : 'nominal';
      armBtn.textContent = active ? cfg.recloseArmText : cfg.openArmText;
      execBtn.textContent = active ? cfg.recloseBtnText : cfg.openBtnText;
      armBtn.setAttribute('aria-pressed', 'false');
      execBtn.disabled = true;
      if (log) {
        log.textContent = cfg.name + ' is now ' + pill.textContent.toLowerCase();
      }
    });
  }

  function bootV18(doc) {
    var v18Root = doc.querySelector('.v9-view-v18');
    if (!v18Root || v18Root.dataset.v06Bound === '1') return;
    v18Root.dataset.v06Bound = '1';
    var filterBtns = doc.querySelectorAll('button[data-v18-filter]');
    var tiles = doc.querySelectorAll('.v18-zone-tile[data-v18-cat]');
    if (filterBtns.length && tiles.length) {
      filterBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var cat = btn.dataset.v18Filter || 'all';
          filterBtns.forEach(function (b) {
            var active = b.dataset.v18Filter === cat;
            b.classList.toggle('is-active', active);
            b.setAttribute('aria-pressed', active ? 'true' : 'false');
          });
          tiles.forEach(function (tile) {
            var show = cat === 'all' || tile.dataset.v18Cat === cat;
            if (show) tile.removeAttribute('hidden');
            else tile.setAttribute('hidden', '');
          });
        });
      });
    }

    doc.querySelectorAll('button[data-v18-unit]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var unit = btn.dataset.v18Unit || 'c';
        applyTempUnit(v18Root, unit);
        doc.querySelectorAll('button[data-v18-unit]').forEach(function (b) {
          var active = b.dataset.v18Unit === unit;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
      });
    });

    wireTwoStep(doc, {
      name: 'Front door',
      armId: 'v18-lock-arm',
      execId: 'v18-lock-exec',
      pillId: 'v18-lock-pill',
      closedLabel: 'LOCKED',
      openLabel: 'UNLOCKED',
      openArmText: '1. Tap to Unlock',
      recloseArmText: '1. Tap to Lock',
      openBtnText: '2. Confirm Unlock',
      recloseBtnText: '2. Confirm Lock',
    });
    wireTwoStep(doc, {
      name: 'Garage door',
      armId: 'v18-garage-arm',
      execId: 'v18-garage-exec',
      pillId: 'v18-garage-pill',
      closedLabel: 'CLOSED',
      openLabel: 'OPEN',
      openArmText: '1. Tap to Open',
      recloseArmText: '1. Tap to Close',
      openBtnText: '2. Confirm Open',
      recloseBtnText: '2. Confirm Close',
    });
  }

  global.QuietWorld06Runtime = {
    boot: function (doc) {
      if (!doc) return;
      bootV17(doc);
      bootV18(doc);
    },
  };
}(window));
