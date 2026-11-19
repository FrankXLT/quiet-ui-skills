/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.0 Gate 5.5 — World 06 (v17 & v18) Client Interactions */
(function (global) {
  'use strict';

  function applyTempUnit(root, unit) {
    if (!root) return;
    var u = unit === 'f' ? 'f' : 'c';
    root.setAttribute('data-temp-unit', u);
    root.querySelectorAll('[data-temp-c][data-temp-f]').forEach(function (el) {
      el.textContent = u === 'f' ? el.getAttribute('data-temp-f') : el.getAttribute('data-temp-c');
    });
  }

  function bootV17(doc) {
    var vp = doc.getElementById('v17-kiosk');
    if (!vp) return;

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
      });
    });

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
        log.textContent = cfg.name + ' armed — tap Step 2 to confirm';
      }
    });

    execBtn.addEventListener('click', function () {
      if (execBtn.disabled) return;
      active = !active;
      pill.textContent = active ? cfg.openLabel : cfg.closedLabel;
      pill.dataset.state = active ? 'warn' : 'nominal';
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
      openBtnText: '2. Unlock Door',
      recloseBtnText: '2. Lock Door',
    });
    wireTwoStep(doc, {
      name: 'Garage door',
      armId: 'v18-garage-arm',
      execId: 'v18-garage-exec',
      pillId: 'v18-garage-pill',
      closedLabel: 'CLOSED',
      openLabel: 'OPEN',
      openBtnText: '2. Open Garage',
      recloseBtnText: '2. Close Garage',
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
