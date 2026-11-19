/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.0 Phase 5.4 — World 06 (v17 & v18) Client Interactions */
(function (global) {
  'use strict';

  function bootV17(doc) {
    var vp = doc.getElementById('v17-kiosk');
    if (!vp) return;
    var readout = doc.getElementById('v17-scene-readout');

    function syncReadout() {
      if (!readout) return;
      var bd = vp.dataset.v17Backdrop === 'landscape' ? 'Landscape' : 'Fine Art';
      var sc = vp.dataset.v17Scene === 'cinema-dim'
        ? 'Cinema Dim'
        : (vp.dataset.v17Scene === 'night-quiet' ? 'Night Quiet' : 'Evening Warm');
      readout.textContent = bd + ' · ' + sc;
    }

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
        syncReadout();
      });
    });

    vp.querySelectorAll('button[data-v17-scene]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var scene = btn.dataset.v17Scene || 'evening-warm';
        vp.dataset.v17Scene = scene;
        vp.querySelectorAll('button[data-v17-scene]').forEach(function (b) {
          var active = b.dataset.v17Scene === scene;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        syncReadout();
      });
    });
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
        log.textContent = cfg.name + ' ARMED — confirm Step 2 to actuate';
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
        log.textContent = cfg.name + ' transitioned to ' + pill.textContent;
      }
    });
  }

  function bootV18(doc) {
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

    wireTwoStep(doc, {
      name: 'LOCK-FRONT-01',
      armId: 'v18-lock-arm',
      execId: 'v18-lock-exec',
      pillId: 'v18-lock-pill',
      closedLabel: 'LOCKED',
      openLabel: 'UNLOCKED',
      openBtnText: '2. Unlock Entry',
      recloseBtnText: '2. Relock Entry',
    });
    wireTwoStep(doc, {
      name: 'GARAGE-BAY-01',
      armId: 'v18-garage-arm',
      execId: 'v18-garage-exec',
      pillId: 'v18-garage-pill',
      closedLabel: 'CLOSED',
      openLabel: 'OPEN',
      openBtnText: '2. Open Bay Door',
      recloseBtnText: '2. Close Bay Door',
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
