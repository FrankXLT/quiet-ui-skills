/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.0.1 — Studio Settings Sheet, Prompt Export & Mobile Scroll Auto-Tuck
 */
(function(window) {
  'use strict';

  const THEME_ORDER = ['white', 'paper', 'dark-paper', 'dark'];
  let lastPortalScrollY = 0;

  function cycleTheme(current) {
    const idx = THEME_ORDER.indexOf(current);
    return THEME_ORDER[(idx + 1) % THEME_ORDER.length];
  }

  function hasNonDefaultSettings(state) {
    return (
      state.nav !== 'auto' ||
      state.density !== 'd2' ||
      state.scale !== '100' ||
      state.corners !== 'auto' ||
      state.vp !== 'fill'
    );
  }

  function buildContractPrompt(state) {
    if (state.view === 'diagrams') {
      return 'Quiet UI Diagrams · Section: ' + (state.atlasSec || 'all') +
        ' · Surface: ' + state.theme + ' · Density: ' + state.density;
    }
    return 'Target Tier: ' + state.tier + ' (' + state.nav + ') · Surface: ' +
      state.theme + ' · Density: ' + state.density + ' · Corners: ' +
      state.corners + ' · Scale: ' + state.scale + '%';
  }

  function syncSheetControls(state, allowedNavs) {
    const dot = document.getElementById('va-settings-dot');
    if (dot) dot.hidden = !hasNonDefaultSettings(state);

    document.querySelectorAll('[data-theme-dot], [data-sheet-theme]').forEach(function(btn) {
      const val = btn.dataset.themeDot || btn.dataset.sheetTheme;
      const active = val === state.theme;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-checked', active ? 'true' : 'false');
    });

    document.querySelectorAll('[data-sheet-scale]').forEach(function(btn) {
      const active = btn.dataset.sheetScale === state.scale;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    const syncPairs = {
      'va-theme-select': state.theme,
      'va-density-select': state.density,
      'va-corners-select': state.corners,
      'va-sheet-nav-select': state.nav,
      'va-sheet-vp-select': state.vp
    };
    Object.keys(syncPairs).forEach(function(id) {
      const el = document.getElementById(id);
      if (el) el.value = syncPairs[id];
    });

    const sheetNav = document.getElementById('va-sheet-nav-select');
    if (sheetNav && allowedNavs) {
      Array.from(sheetNav.options).forEach(function(opt) {
        if (opt.value === 'auto') return;
        opt.disabled = allowedNavs.indexOf(opt.value) === -1;
      });
    }

    const szBtn = document.getElementById('va-sheet-zoom-btn');
    if (szBtn) szBtn.textContent = state.zoom.toUpperCase();

    const prev = document.getElementById('va-prompt-preview');
    if (prev) prev.textContent = buildContractPrompt(state);
  }

  function untuckStudioBar() {
    lastPortalScrollY = 0;
    const bar = document.getElementById('va-studio-bar');
    if (bar) bar.classList.remove('is-tucked');
  }

  function bindPortalScrollTuck(iframe) {
    if (!iframe || !iframe.contentWindow) return;
    const win = iframe.contentWindow;
    if (win.__quietScrollBound) return;
    win.__quietScrollBound = true;
    lastPortalScrollY = 0;

    const onScroll = function(ev) {
      const bar = document.getElementById('va-studio-bar');
      if (!bar) return;
      if (window.innerWidth >= 700) {
        bar.classList.remove('is-tucked');
        return;
      }
      const doc = iframe.contentDocument;
      const target = (ev && ev.target && ev.target.scrollTop !== undefined) ? ev.target : null;
      const curY = Math.max(
        win.scrollY || 0,
        (doc && doc.documentElement ? doc.documentElement.scrollTop : 0),
        (target ? target.scrollTop : 0)
      );
      if (curY <= 12) {
        bar.classList.remove('is-tucked');
        lastPortalScrollY = curY;
        return;
      }
      const delta = curY - lastPortalScrollY;
      if (delta > 32) {
        bar.classList.add('is-tucked');
        lastPortalScrollY = curY;
      } else if (delta < -12) {
        bar.classList.remove('is-tucked');
        lastPortalScrollY = curY;
      }
    };
    win.addEventListener('scroll', onScroll, { passive: true, capture: true });
  }

  function initSheetEvents(state, applyState, onRotate, onZoomToggle) {
    const sheet = document.getElementById('va-customize-sheet');
    if (sheet && !('closedBy' in HTMLDialogElement.prototype)) {
      sheet.addEventListener('click', function(ev) {
        if (ev.target !== sheet) return;
        const r = sheet.getBoundingClientRect();
        const inside = r.top <= ev.clientY && ev.clientY <= r.bottom && r.left <= ev.clientX && ev.clientX <= r.right;
        if (!inside) sheet.close();
      });
    }

    const cycleBtn = document.getElementById('va-theme-cycle-btn');
    if (cycleBtn) cycleBtn.addEventListener('click', function() {
      state.theme = cycleTheme(state.theme);
      applyState();
    });

    document.querySelectorAll('[data-theme-dot], [data-sheet-theme]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        state.theme = btn.dataset.themeDot || btn.dataset.sheetTheme;
        applyState();
      });
    });

    document.querySelectorAll('[data-sheet-scale]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        state.scale = btn.dataset.sheetScale || '100';
        applyState();
      });
    });

    const sheetNav = document.getElementById('va-sheet-nav-select');
    if (sheetNav) sheetNav.addEventListener('change', function(e) { state.nav = e.target.value; applyState(); });

    const sheetVp = document.getElementById('va-sheet-vp-select');
    if (sheetVp) sheetVp.addEventListener('change', function(e) { state.vp = e.target.value; applyState(); });

    const sRot = document.getElementById('va-sheet-rotate-btn');
    if (sRot) sRot.addEventListener('click', onRotate);

    const sZoom = document.getElementById('va-sheet-zoom-btn');
    if (sZoom) sZoom.addEventListener('click', onZoomToggle);

    const copyBtn = document.getElementById('va-copy-prompt-btn');
    if (copyBtn) copyBtn.addEventListener('click', function() {
      const txt = buildContractPrompt(state);
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(txt).then(function() {
          const orig = copyBtn.textContent;
          copyBtn.textContent = 'Copied';
          setTimeout(function() { copyBtn.textContent = orig; }, 1400);
        });
      }
    });
  }

  window.QuietStudioSheet = {
    syncSheetControls: syncSheetControls,
    untuckStudioBar: untuckStudioBar,
    bindPortalScrollTuck: bindPortalScrollTuck,
    initSheetEvents: initSheetEvents
  };
})(typeof window !== 'undefined' ? window : this);
