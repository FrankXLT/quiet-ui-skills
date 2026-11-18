/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 — Studio Settings Sheet, Dialog Light-Dismiss Fallback & Scroll Auto-Tuck
 */
(function (window) {
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
      state.medium !== 'auto' ||
      state.density !== 'd2' ||
      state.scale !== '100' ||
      state.corners !== 'auto' ||
      state.vp !== 'fill'
    );
  }

  function buildContractPrompt(state) {
    return (
      'World: ' + state.world + ' · View: ' + state.view +
      ' · Medium: ' + state.medium + ' · Nav: ' + state.nav +
      ' · Theme: ' + state.theme + ' · Density: ' + state.density +
      ' · Scale: ' + state.scale + '%'
    );
  }

  function bindDialogLightDismissFallback(dialog) {
    if (!dialog || ('closedBy' in HTMLDialogElement.prototype)) return;
    let pressedOutside = false;
    const isOutside = function (ev) {
      const r = dialog.getBoundingClientRect();
      return ev.clientX < r.left || ev.clientX > r.right || ev.clientY < r.top || ev.clientY > r.bottom;
    };
    dialog.addEventListener('pointerdown', function (ev) { pressedOutside = isOutside(ev); });
    dialog.addEventListener('pointerup', function (ev) {
      if (pressedOutside && isOutside(ev)) dialog.close();
      pressedOutside = false;
    });
  }

  function syncSheetControls(state, allowedNavs) {
    const dot = document.getElementById('va-settings-dot');
    if (dot) dot.hidden = !hasNonDefaultSettings(state);

    document.querySelectorAll('[data-theme-dot], [data-sheet-theme]').forEach(function (btn) {
      const val = btn.dataset.themeDot || btn.dataset.sheetTheme;
      const active = val === state.theme;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-checked', active ? 'true' : 'false');
    });

    document.querySelectorAll('[data-sheet-scale]').forEach(function (btn) {
      const active = btn.dataset.sheetScale === state.scale;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    const syncPairs = {
      'va-sheet-world-select': state.world,
      'va-sheet-medium-select': state.medium,
      'va-density-select': state.density,
      'va-corners-select': state.corners,
      'va-sheet-nav-select': state.nav,
      'va-sheet-vp-select': state.vp,
    };
    Object.keys(syncPairs).forEach(function (id) {
      const el = document.getElementById(id);
      if (el) el.value = syncPairs[id];
    });

    const sheetNav = document.getElementById('va-sheet-nav-select');
    if (sheetNav && allowedNavs) {
      Array.from(sheetNav.options).forEach(function (opt) {
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

    win.addEventListener('scroll', function (ev) {
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
    }, { passive: true, capture: true });
  }

  function initSheetEvents(state, applyState, onRotate, onZoomToggle, onPrint) {
    bindDialogLightDismissFallback(document.getElementById('va-customize-sheet'));
    bindDialogLightDismissFallback(document.getElementById('va-bridge-dialog'));

    const cycleBtn = document.getElementById('va-theme-cycle-btn');
    if (cycleBtn) cycleBtn.addEventListener('click', function () { state.theme = cycleTheme(state.theme); applyState(); });

    document.querySelectorAll('[data-theme-dot], [data-sheet-theme]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        state.theme = btn.dataset.themeDot || btn.dataset.sheetTheme;
        applyState();
      });
    });

    document.querySelectorAll('[data-sheet-scale]').forEach(function (btn) {
      btn.addEventListener('click', function () { state.scale = btn.dataset.sheetScale || '100'; applyState(); });
    });

    const sw = document.getElementById('va-sheet-world-select');
    if (sw) sw.addEventListener('change', function (e) { state.world = e.target.value; applyState(true); });

    const sm = document.getElementById('va-sheet-medium-select');
    if (sm) sm.addEventListener('change', function (e) { state.medium = e.target.value; applyState(); });

    const sn = document.getElementById('va-sheet-nav-select');
    if (sn) sn.addEventListener('change', function (e) { state.nav = e.target.value; applyState(); });

    const sv = document.getElementById('va-sheet-vp-select');
    if (sv) sv.addEventListener('change', function (e) { state.vp = e.target.value; applyState(); });

    const sr = document.getElementById('va-sheet-rotate-btn');
    if (sr) sr.addEventListener('click', onRotate);

    const sz = document.getElementById('va-sheet-zoom-btn');
    if (sz) sz.addEventListener('click', onZoomToggle);

    const sp = document.getElementById('va-sheet-print-btn');
    if (sp && typeof onPrint === 'function') sp.addEventListener('click', onPrint);

    const copyBtn = document.getElementById('va-copy-prompt-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        const txt = buildContractPrompt(state);
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(txt).then(function () {
            const orig = copyBtn.textContent;
            copyBtn.textContent = 'Copied';
            window.setTimeout(function () { copyBtn.textContent = orig; }, 1400);
          });
        }
      });
    }
  }

  function escHtml(val) {
    return String(val == null ? '' : val)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function openBridgeDialog(worldObj, viewMeta) {
    const dlg = document.getElementById('va-bridge-dialog');
    const body = document.getElementById('va-bridge-body');
    const title = document.getElementById('va-bridge-title');
    if (!dlg || !body || !worldObj || !viewMeta) return;
    if (title) title.textContent = 'Why This View? — ' + viewMeta.title;
    const ledgerRows = (worldObj.conservation_ledger || []).map(function (row) {
      return '<tr><td><code>' + escHtml(row.metric_id) + '</code></td><td>' + escHtml(row.canonical_value) +
        '</td><td>' + escHtml(row.unit) + '</td><td>' + escHtml(row.views) + '</td></tr>';
    }).join('');
    const mbRows = (viewMeta.murder_board || []).map(function (m) {
      return '<div class="va-bridge-item"><strong>' + escHtml(m.rubric) + ' · <span class="va-bridge-pass">' +
        escHtml(m.verdict) + '</span></strong>' + escHtml(m.finding) + '</div>';
    }).join('');
    const inv = viewMeta.invariants || {};
    body.innerHTML =
      '<section class="va-bridge-card"><h3>1. Active Presenter -> Audience Vector</h3>' +
      '<div class="va-bridge-vector">' + escHtml(viewMeta.vector_summary) + '</div>' +
      '<div class="va-bridge-item"><strong>Actionable Disposition</strong>' + escHtml(viewMeta.actionable_disposition) + '</div></section>' +
      '<section class="va-bridge-card"><h3>2. Scrubbed Sender Bias</h3><div class="va-bridge-grid">' +
      '<div class="va-bridge-item"><strong>Raw Bias Removed</strong>' + escHtml(viewMeta.bias_removed) + '</div>' +
      '<div class="va-bridge-item"><strong>Audience Risk Prevented</strong>' + escHtml(viewMeta.bias_risk) + '</div>' +
      '<div class="va-bridge-item"><strong>Distilled Replacement</strong>' + escHtml(viewMeta.bias_replacement) + '</div></div></section>' +
      '<section class="va-bridge-card"><h3>3. Four Universal Audience Invariants</h3><div class="va-bridge-grid">' +
      '<div class="va-bridge-item"><strong>1. Baseline &amp; Corridor</strong>' + escHtml(inv.baseline || '') + '</div>' +
      '<div class="va-bridge-item"><strong>2. Epistemic Provenance</strong>' + escHtml(inv.provenance || '') + '</div>' +
      '<div class="va-bridge-item"><strong>3. Margin &amp; Consequence</strong>' + escHtml(inv.margin || '') + '</div>' +
      '<div class="va-bridge-item"><strong>4. Actionable Disposition</strong>' + escHtml(inv.disposition || '') + '</div></div></section>' +
      '<section class="va-bridge-card"><h3>4. Murder-Board Red-Team Verdict</h3><div class="va-bridge-grid">' + mbRows + '</div></section>' +
      '<section class="va-bridge-card"><h3>5. Canonical Numerical Conservation Ledger</h3>' +
      '<div class="va-bridge-table-wrap"><table class="va-bridge-table"><thead><tr><th>Metric ID</th><th>Canonical Value</th><th>Unit</th><th>Consuming Views</th></tr></thead>' +
      '<tbody>' + ledgerRows + '</tbody></table></div></section>';
    if (typeof dlg.showModal === 'function') dlg.showModal();
  }

  function postExternalSync(iframe, state, stageW) {
    const payload = {
      type: 'quiet-ui-sync', theme: state.theme, medium: state.medium,
      density: state.density, corners: state.corners, formFactor: stageW <= 480 ? 'touch' : 'desktop',
    };
    try {
      if (iframe.contentWindow) iframe.contentWindow.postMessage(payload, '*');
      const doc = iframe.contentDocument && iframe.contentDocument.documentElement;
      if (doc) {
        doc.dataset.theme = state.theme;
        doc.dataset.density = state.density;
        doc.dataset.corners = state.corners;
        if (state.studioView === 'bench') doc.dataset.medium = state.medium === 'm1' ? 'm1' : 'm2';
      }
    } catch (_e) {}
  }

  window.QuietStudioSheetV9 = {
    escHtml: escHtml,
    postExternalSync: postExternalSync,
    syncSheetControls: syncSheetControls,
    untuckStudioBar: untuckStudioBar,
    bindPortalScrollTuck: bindPortalScrollTuck,
    initSheetEvents: initSheetEvents,
    openBridgeDialog: openBridgeDialog,
  };
})(typeof window !== 'undefined' ? window : this);
