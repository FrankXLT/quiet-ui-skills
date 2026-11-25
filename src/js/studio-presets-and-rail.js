/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.6 — Curated Form-Factor Presets, Global Stepping & Interactive #va-shell-rail
 */
(function (window) {
  'use strict';

  const VIEW_PRESETS = {
    'v01-icu-bedside-terminal': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v02-trial-regulatory-brief': { vp: '1056x1368', medium: 'm1', theme: 'paper', preset_label: 'Paper Sheet' },
    'v03-patient-recovery-companion': { vp: '390x844', medium: 'auto', theme: 'white', preset_label: 'Mobile' },
    'v04-sre-incident-workbench': { vp: '1920x1080', medium: 'auto', theme: 'dark-paper', preset_label: 'Dark Workbench' },
    'v05-zero-trust-ato-spec': { vp: '1056x1368', medium: 'm1', theme: 'paper', preset_label: 'Paper Sheet' },
    'v06-ai-drift-and-lineage-ide': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v07-grid-scada-poi-console': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v08-plant-floor-wall-kiosk': { vp: '1280x800', medium: 'auto', theme: 'dark', preset_label: 'Tablet HMI' },
    'v09-spc-quality-and-modbus-report': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v10-civic-capital-budget-deck': { vp: '1056x1368', medium: 'm1', theme: 'paper', preset_label: 'Paper Sheet' },
    'v11-treasury-stress-test-solver': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v12-stem-interactive-lab': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v13-propulsion-archival-monograph': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v14-fieldbus-and-scope-debugger': { vp: '1920x1080', medium: 'auto', theme: 'dark-paper', preset_label: 'Dark Workbench' },
    'v15-collimated-flight-hud': { vp: '1920x1080', medium: 'auto', theme: 'dark', preset_label: 'Optical HUD' },
    'v16-transparent-window-overlay': { vp: '1920x1080', medium: 'auto', theme: 'dark', preset_label: 'Smart Glass' },
    'v17-picture-frame-home-kiosk': { vp: '1920x1080', medium: 'auto', theme: 'paper', preset_label: 'Art Frame' },
    'v18-home-assistant-companion-console': { vp: '390x844', medium: 'auto', theme: 'white', preset_label: 'Mobile' },
    'v19-product-roadmap-and-triage': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
    'v20-student-capstone-lab-report': { vp: '1056x1368', medium: 'm1', theme: 'paper', preset_label: 'Paper Sheet' },
    'v21-field-anomaly-escalation-tsn': { vp: '390x844', medium: 'auto', theme: 'white', preset_label: 'Mobile' },
    'v22-reading-and-mobility-brief': { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' },
  };

  function esc(val) {
    if (window.QuietStudioSheetV9 && window.QuietStudioSheetV9.escHtml) return window.QuietStudioSheetV9.escHtml(val);
    return String(val == null ? '' : val).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function getViewPreset(viewId) {
    return VIEW_PRESETS[viewId] || { vp: '1920x1080', medium: 'auto', theme: 'white', preset_label: '1080p Screen' };
  }

  function applyViewPreset(viewId, state) {
    const p = getViewPreset(viewId);
    state.vp = p.vp;
    state.medium = p.medium;
    state.theme = p.theme;
    state.zoom = 'fit';
  }

  function flattenViews(manifest) {
    const out = [];
    (manifest.worlds || []).forEach(function (w) {
      (w.views || []).forEach(function (v) {
        out.push({ world_id: w.world_id, view_id: v.view_id, meta: v });
      });
    });
    return out;
  }

  function getGlobalPosition(manifest, state) {
    const flat = flattenViews(manifest);
    const idx = flat.findIndex(function (it) { return it.view_id === state.view; });
    return { index: idx >= 0 ? idx + 1 : 1, total: flat.length || 1 };
  }

  function stepGlobalView(manifest, state, delta) {
    const flat = flattenViews(manifest);
    if (!flat.length) return null;
    let idx = flat.findIndex(function (it) { return it.view_id === state.view; });
    if (idx < 0) idx = 0;
    const next = flat[(idx + delta + flat.length) % flat.length];
    state.world = next.world_id;
    state.view = next.view_id;
    return next;
  }

  const NAV_ICONS = {
    'compass': '<circle cx="8" cy="8" r="6"/><path d="M10.5 5.5 9 9l-3.5 1.5L7 7z" fill="none"/>',
    'bars': '<path d="M2.5 4.5h11M2.5 8h11M2.5 11.5h11" fill="none"/>',
    'close': '<path d="M4 4l8 8M12 4l-8 8" fill="none"/>',
    'activity': '<path d="M1.5 8h3l1.8-4.5 2.4 9 1.8-4.5h4" fill="none"/>',
    'layers': '<path d="M8 2 14 5 8 8 2 5zM2 8l6 3 6-3M2 11l6 3 6-3" fill="none"/>',
    'sliders': '<path d="M3 4h10M3 8h10M3 12h10M6 2.5v3M10 6.5v3M7 10.5v3" fill="none"/>',
    'bell': '<path d="M4.5 10.5V7a3.5 3.5 0 0 1 7 0v3.5l1.5 1.5H3zM6.5 13.5h3" fill="none"/>',
    'heart-pulse': '<path d="M8 13.5S2.5 9.8 2.5 5.8a3 3 0 0 1 5.5-1.6 3 3 0 0 1 5.5 1.6c0 4-5.5 7.7-5.5 7.7zM4.5 8h2l1-2 1.2 3.5L10 8h1.5" fill="none"/>',
    'file-medical': '<path d="M4 2h5.5L13 5.5V14H4zM9.5 2v3.5H13M8 7v4M6 9h4" fill="none"/>',
    'hand-holding-medical': '<path d="M2 10.5h4l2 1.5h4.5M5 4.5h6M8 1.5v6" fill="none"/>',
    'alert-triangle': '<path d="M8 2.2 14 13H2zM8 6.5v3M8 11.2v.4" fill="none"/>',
    'shield-halved': '<path d="M8 2 13.5 4v4c0 3.2-2.2 5.2-5.5 6.2C4.7 13.2 2.5 11.2 2.5 8V4zM8 2v12" fill="none"/>',
    'code-branch': '<path d="M5 3v10M11 4v2.5c0 1.5-2 2.5-6 2.5" fill="none"/><circle cx="5" cy="3.5" r="1.3"/><circle cx="5" cy="12.5" r="1.3"/><circle cx="11" cy="4" r="1.3"/>',
    'bolt': '<path d="M9 1.5 3.5 9H8l-1 5.5L12.5 7H8z" fill="none"/>',
    'tv': '<rect x="2" y="3" width="12" height="8" rx="1"/><path d="M5.5 13.5h5M8 11v2.5" fill="none"/>',
    'chart-line': '<path d="M2.5 2.5v11h11M4.5 10.5 7.5 7l2.2 2 3.5-4" fill="none"/>',
    'landmark': '<path d="M2 6 8 2.5 14 6zM3.5 6v6M6.5 6v6M9.5 6v6M12.5 6v6M2 13.5h12" fill="none"/>',
    'scale-balanced': '<path d="M8 2.5v11M4.5 13.5h7M3 5l5-1 5 1M2 9.5 3.5 5 5 9.5zM11 9.5 12.5 5 14 9.5z" fill="none"/>',
    'flask': '<path d="M6 2.5h4M7 2.5V6l-3.5 7.5h9L9 6V2.5M5 10.5h6" fill="none"/>',
    'gauge-high': '<path d="M3 11.5a5.5 5.5 0 1 1 10 0M8 8.5l2.8-2.8" fill="none"/>',
    'microchip': '<rect x="4.5" y="4.5" width="7" height="7" rx="1"/><path d="M6.5 2v2.5M9.5 2v2.5M6.5 11.5V14M9.5 11.5V14M2 6.5h2.5M2 9.5h2.5M11.5 6.5H14M11.5 9.5H14" fill="none"/>',
    'crosshairs': '<circle cx="8" cy="8" r="5"/><path d="M8 1.5v3M8 11.5v3M1.5 8h3M11.5 8h3" fill="none"/>',
    'glasses': '<circle cx="5" cy="9" r="2.5"/><circle cx="11" cy="9" r="2.5"/><path d="M7.5 9h1M2.5 9 4 4.5M13.5 9 12 4.5" fill="none"/>',
    'home': '<path d="M2.5 7.5 8 2.5l5.5 5v6H10V9.5H6v4H2.5z" fill="none"/>',
    'frame': '<rect x="2" y="3" width="12" height="10" rx="1"/><path d="M4.5 10.5 7 7.5l2 2 1.5-1.5 2 2.5" fill="none"/>',
    'list-check': '<path d="M2.5 4.5h1.5M6 4.5h7.5M2.5 8h1.5M6 8h7.5M2.5 11.5h1.5M6 11.5h5.5M11.5 11l1.2 1.2 2-2.2" fill="none"/>',
    'graduation-cap': '<path d="M1.5 6.5 8 3l6.5 3.5L8 10zM4 8v3.5c0 1 1.8 2 4 2s4-1 4-2V8" fill="none"/>',
    'wrench': '<path d="M10.5 2.5a3.2 3.2 0 0 0-3.8 4.4L2.8 10.8a1.4 1.4 0 0 0 2 2l3.9-3.9a3.2 3.2 0 0 0 4.4-3.8l-1.9 1.9-1.5-1.5z" fill="none"/>',
  };
  function svgIcon(name) {
    const body = NAV_ICONS[name] || NAV_ICONS.compass;
    return '<svg class="va-icon" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style="flex:none" aria-hidden="true">' + body + '</svg>';
  }

  function sidebarSvg(kind) {
    if (kind === 'collapse') {
      return '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="2.5" width="12" height="11" rx="1.5" fill="none"/><path d="M6 2.5v11" fill="none"/></svg>';
    }
    if (kind === 'caret') {
      return '<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5" fill="none"/></svg>';
    }
    return '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="2.5" width="4.5" height="4.5" rx="1" fill="none"/><rect x="9" y="2.5" width="4.5" height="4.5" rx="1" fill="none"/><rect x="2.5" y="9" width="4.5" height="4.5" rx="1" fill="none"/><rect x="9" y="9" width="4.5" height="4.5" rx="1" fill="none"/></svg>';
  }

  function countForAnchor(doc, anchor) {
    const el = anchor ? doc.getElementById(anchor) : null;
    if (!el) return 1;
    return el.querySelectorAll('.qe-figure, .va-figure-card, .qe-scalar-card, .v9-kpi-tile, .v18-kpi-card, .v18-zone-tile, .v18-access-card, .v9-triage-row, .v01-audit-item, .v9-audit-item, table').length || 1;
  }

  function refreshStageCharts(doc) {
    const win = doc && doc.defaultView;
    if (!win || !win.QuietEChartsAdapter) return;
    win.QuietEChartsAdapter.refresh(doc);
    if (typeof win.requestAnimationFrame === 'function') {
      win.requestAnimationFrame(function () { win.QuietEChartsAdapter.refresh(doc); });
    }
  }

  let scrollOpId = 0;

  function setRailActiveLink(doc, anchorId) {
    doc.querySelectorAll('#va-shell-rail .va-rail-link').forEach(function (lnk) {
      const on = lnk.getAttribute('data-rail-anchor') === anchorId;
      lnk.classList.toggle('is-active', on);
      if (on) lnk.setAttribute('aria-current', 'location');
      else lnk.removeAttribute('aria-current');
    });
  }

  function spotlightAnchor(doc, anchorId, shouldScroll) {
    doc.querySelectorAll('.is-rail-spotlight').forEach(function (el) { el.classList.remove('is-rail-spotlight'); });
    setRailActiveLink(doc, anchorId);
    const target = anchorId ? doc.getElementById(anchorId) : null;
    if (!target) {
      refreshStageCharts(doc);
      return;
    }
    target.classList.add('is-rail-spotlight');
    if (shouldScroll) {
      const opId = ++scrollOpId;
      doc.__quietManualNavUntil = Date.now() + 750;
      if (!target.hasAttribute('tabindex') && !target.matches('a,button,input,select,textarea')) {
        target.setAttribute('tabindex', '-1');
      }
      const win = doc.defaultView;
      if (win) {
        const tb = doc.getElementById('va-shell-topbar');
        const tbH = (tb && win.getComputedStyle(tb).display !== 'none') ? tb.getBoundingClientRect().height : 0;
        const destY = Math.max(0, (win.scrollY || 0) + target.getBoundingClientRect().top - tbH - 14);
        win.scrollTo({ top: destY, behavior: 'smooth' });
      }
      const done = function () {
        if (opId !== scrollOpId || !target.isConnected) return;
        target.classList.add('is-rail-spotlight');
        refreshStageCharts(doc);
      };
      if (win && 'onscrollend' in win) {
        win.addEventListener('scrollend', done, { once: true });
      }
      (win || globalThis).setTimeout(done, 460);
    } else {
      refreshStageCharts(doc);
    }
  }

  function initScrollSpy(doc, anchors) {
    if (doc.__quietRailSpy && typeof doc.__quietRailSpy.disconnect === 'function') {
      doc.__quietRailSpy.disconnect();
      doc.__quietRailSpy = null;
    }
    const win = doc.defaultView;
    if (doc.__quietRailScrollFn && win) {
      win.removeEventListener('scroll', doc.__quietRailScrollFn);
      doc.__quietRailScrollFn = null;
    }
    if (!win || typeof win.IntersectionObserver !== 'function') return;
    const targets = [];
    (anchors || []).forEach(function (aid) {
      const el = aid ? doc.getElementById(aid) : null;
      if (el && targets.indexOf(el) === -1) targets.push(el);
    });
    if (targets.length < 2) return;
    const visible = new Set();
    function syncActive() {
      if (Date.now() < (doc.__quietManualNavUntil || 0)) return;
      const sy = win.scrollY || 0;
      if (sy <= 6) { setRailActiveLink(doc, targets[0].id); return; }
      const de = doc.documentElement;
      if (de && (sy + win.innerHeight) >= (de.scrollHeight - 4)) {
        setRailActiveLink(doc, targets[targets.length - 1].id);
        return;
      }
      for (let i = 0; i < targets.length; i += 1) {
        if (visible.has(targets[i].id)) { setRailActiveLink(doc, targets[i].id); return; }
      }
    }
    const spy = new win.IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) visible.add(e.target.id);
        else visible.delete(e.target.id);
      });
      syncActive();
    }, { root: null, rootMargin: '-18% 0px -55% 0px', threshold: 0 });
    targets.forEach(function (el) { spy.observe(el); });
    doc.__quietRailSpy = spy;
    let raf = 0;
    doc.__quietRailScrollFn = function () {
      if (raf) return;
      raf = win.requestAnimationFrame(function () { raf = 0; syncActive(); });
    };
    win.addEventListener('scroll', doc.__quietRailScrollFn, { passive: true });
  }

  function findStageQuickControls(doc) {
    const sels = [
      '.qe-scope-preset-bar button[data-scope-preset]',
      '#v02-subgroup-chips button', '#v05-enclave-chips button', '#v10-fund-chips button',
      '#v11-shock-chips button', '#v12-role-chips button', '#v12-lab button[data-term]',
      '#v03-guide button[data-term]', '.v18-filter-bar button[data-v18-filter]',
      '#v19-filter-chips button', '#v21-step-chips button',
      '.va-tab-strip button',
    ];
    for (let i = 0; i < sels.length; i += 1) {
      const hits = Array.prototype.slice.call(doc.querySelectorAll(sels[i]));
      if (hits.length >= 2) return hits.slice(0, 4);
    }
    return [];
  }

  function syncRailFooter(doc, state) {
    if (!doc || !state) return;
    doc.querySelectorAll('#va-shell-rail .va-swatch-btn').forEach(function (b) {
      const on = b.getAttribute('data-swatch') === state.theme;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    doc.querySelectorAll('#va-shell-rail [data-density]').forEach(function (b) {
      const mode = b.getAttribute('data-density');
      const on = (mode === 'compact' && state.density === 'd3') || (mode === 'comfortable' && state.density === 'd2');
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function syncQuickButtons(doc, quickCtrls) {
    doc.querySelectorAll('#va-shell-rail [data-quick-idx]').forEach(function (mb) {
      const real = quickCtrls[parseInt(mb.getAttribute('data-quick-idx') || '-1', 10)];
      if (!real) return;
      const on = real.classList.contains('is-active') || real.getAttribute('aria-pressed') === 'true';
      mb.classList.toggle('is-active', on);
      mb.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function enhanceShellNav(doc, viewMeta, portalApi) {
    doc.documentElement.dataset.railCollapsed = 'false';
    const effNav = (doc.documentElement && doc.documentElement.dataset.effectiveNav) || 'n1';
    const topbar = doc.getElementById('va-shell-topbar');
    if (topbar && !doc.getElementById('va-topbar-rail-toggle')) {
      const tBtn = doc.createElement('button');
      tBtn.type = 'button';
      tBtn.id = 'va-topbar-rail-toggle';
      tBtn.className = 'va-rail-collapse-btn';
      tBtn.setAttribute('aria-label', 'Toggle Navigation Sidebar');
      tBtn.setAttribute('aria-expanded', 'true');
      tBtn.innerHTML = sidebarSvg('collapse');
      topbar.insertBefore(tBtn, topbar.firstChild);
    }
    const main = doc.getElementById('va-stage-main');
    if (main && !doc.getElementById('va-rail-reopen-btn')) {
      const rBtn = doc.createElement('button');
      rBtn.type = 'button';
      rBtn.id = 'va-rail-reopen-btn';
      rBtn.className = 'va-rail-reopen-btn';
      rBtn.setAttribute('aria-label', 'Show Navigation Sidebar');
      rBtn.setAttribute('aria-expanded', 'false');
      rBtn.innerHTML = sidebarSvg('collapse') + ' <span>Sidebar</span>';
      main.insertBefore(rBtn, main.firstChild);
    }
    doc.querySelectorAll('.va-rail-collapse-btn').forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
    const reopenEl = doc.getElementById('va-rail-reopen-btn');
    if (reopenEl) reopenEl.setAttribute('aria-expanded', 'false');

    const rail = doc.getElementById('va-shell-rail');
    if (!rail) return;
    const icon = (viewMeta && viewMeta.nav_icon) ? viewMeta.nav_icon : 'compass';
    const railBrand = (viewMeta && viewMeta.rail_brand) ? viewMeta.rail_brand : ((viewMeta && viewMeta.nav_brand) || 'Quiet UI');
    const items = (viewMeta && viewMeta.nav_items) ? viewMeta.nav_items : [];
    const anchors = (viewMeta && viewMeta.nav_anchors) ? viewMeta.nav_anchors : [];
    const icons = ['activity', 'layers', 'sliders', 'bell'];

    const linksHtml = items.map(function (lbl, i) {
      const anchor = anchors[i] || '';
      const activeCls = i === 0 ? ' is-active' : '';
      const ariaCur = i === 0 ? ' aria-current="location"' : '';
      return '<a class="va-rail-link' + activeCls + '" href="#' + esc(anchor || 'stage') + '" data-rail-anchor="' + esc(anchor) + '"' + ariaCur + '>' +
        svgIcon(icons[i % 4]) + ' <span>' + esc(lbl) + '</span><span class="va-rail-count va-nums">' + countForAnchor(doc, anchor) + '</span></a>';
    }).join('');

    const quickCtrls = findStageQuickControls(doc);
    doc.__quietQuickCtrls = quickCtrls;
    let quickHtml = '';
    if (quickCtrls.length >= 2) {
      quickHtml = '<div class="va-rail-quick-group"><div class="va-tree-row">' +
        '<button type="button" class="va-tree-caret" aria-expanded="true" aria-label="Toggle Interactive Controls">' + sidebarSvg('caret') + '</button>' +
        '<button type="button" class="va-tree-dest" data-quick-toggle="true"><span class="va-tree-label">Interactive Controls</span></button>' +
        '</div><div class="va-tree-children">' +
        quickCtrls.map(function (b, idx) {
          const on = b.classList.contains('is-active') || b.getAttribute('aria-pressed') === 'true';
          return '<div class="va-tree-row"><button type="button" class="va-tree-dest' + (on ? ' is-active' : '') +
            '" data-quick-idx="' + idx + '" aria-pressed="' + (on ? 'true' : 'false') + '"><span class="va-tree-label">' + esc((b.textContent || '').trim()) + '</span></button></div>';
        }).join('') + '</div></div>';
    }

    const footerHtml = '<div class="va-rail-footer">' +
      '<div class="va-swatch-row" role="group" aria-label="Theme">' +
      '<button type="button" class="va-swatch-btn" data-swatch="white" aria-pressed="false" aria-label="White theme"></button>' +
      '<button type="button" class="va-swatch-btn" data-swatch="paper" aria-pressed="false" aria-label="Paper theme"></button>' +
      '<button type="button" class="va-swatch-btn" data-swatch="dark-paper" aria-pressed="false" aria-label="Slate theme"></button>' +
      '<button type="button" class="va-swatch-btn" data-swatch="dark" aria-pressed="false" aria-label="Dark theme"></button></div>' +
      '<div class="va-tb-group va-density-toggle" role="group" aria-label="Density">' +
      '<button type="button" class="va-tb-btn" data-density="compact" aria-pressed="false">Compact</button>' +
      '<button type="button" class="va-tb-btn" data-density="comfortable" aria-pressed="true">Comfortable</button>' +
      '</div></div>';

    const brandHtml = effNav === 'n3'
      ? '<div class="va-rail-brand is-kicker-only"><span class="va-rail-kicker">' + esc(railBrand) + '</span></div>'
      : '<div class="va-rail-brand"><span class="va-rail-brand-title">' + svgIcon(icon) + ' <span>' + esc(railBrand) + '</span></span>' +
        '<button type="button" class="va-rail-collapse-btn" aria-label="Toggle Navigation Sidebar" aria-expanded="true">' + sidebarSvg('collapse') + '</button></div>';

    rail.innerHTML = brandHtml + '<div class="va-rail-scroll"><nav class="va-rail-links" aria-label="Section Navigation">' + linksHtml + '</nav>' + quickHtml + '</div>' + footerHtml;

    const toggleCollapse = function () {
      const next = doc.documentElement.dataset.railCollapsed !== 'true';
      doc.documentElement.dataset.railCollapsed = next ? 'true' : 'false';
      doc.querySelectorAll('.va-rail-collapse-btn, #va-rail-reopen-btn').forEach(function (b) {
        b.setAttribute('aria-expanded', next ? 'false' : 'true');
      });
      refreshStageCharts(doc);
    };
    doc.querySelectorAll('.va-rail-collapse-btn').forEach(function (b) {
      if (b.dataset.bound !== '1') { b.dataset.bound = '1'; b.addEventListener('click', toggleCollapse); }
    });
    const reopen = doc.getElementById('va-rail-reopen-btn');
    if (reopen && reopen.dataset.bound !== '1') { reopen.dataset.bound = '1'; reopen.addEventListener('click', toggleCollapse); }

    rail.querySelectorAll('.va-rail-link').forEach(function (lnk) {
      lnk.addEventListener('click', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        spotlightAnchor(doc, lnk.getAttribute('data-rail-anchor') || '', true);
      });
    });
    initScrollSpy(doc, anchors);

    const caret = rail.querySelector('.va-tree-caret');
    const qHead = rail.querySelector('[data-quick-toggle]');
    const qKids = rail.querySelector('.va-tree-children');
    if (caret && qKids) {
      const toggleTree = function () {
        const open = caret.getAttribute('aria-expanded') !== 'true';
        caret.setAttribute('aria-expanded', open ? 'true' : 'false');
        qKids.hidden = !open;
      };
      caret.addEventListener('click', toggleTree);
      if (qHead) qHead.addEventListener('click', toggleTree);
    }

    rail.querySelectorAll('[data-quick-idx]').forEach(function (mb) {
      mb.addEventListener('click', function () {
        const real = quickCtrls[parseInt(mb.getAttribute('data-quick-idx') || '-1', 10)];
        if (!real) return;
        real.click();
        syncQuickButtons(doc, quickCtrls);
      });
    });
    if (main && main.dataset.railQuickSync !== '1') {
      main.dataset.railQuickSync = '1';
      main.addEventListener('click', function () {
        if (doc.__quietQuickCtrls) window.setTimeout(function () { syncQuickButtons(doc, doc.__quietQuickCtrls); }, 0);
      });
    }

    rail.querySelectorAll('.va-swatch-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        if (!portalApi) return;
        portalApi.state.theme = b.getAttribute('data-swatch') || 'white';
        portalApi.state.presetLocked = true;
        portalApi.applyState(false);
      });
    });
    rail.querySelectorAll('[data-density]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (!portalApi) return;
        portalApi.state.density = b.getAttribute('data-density') === 'compact' ? 'd3' : 'd2';
        portalApi.state.presetLocked = true;
        portalApi.applyState(false);
      });
    });
    syncRailFooter(doc, portalApi ? portalApi.state : null);
  }

  window.QuietStudioPresetsRailV9 = {
    VIEW_PRESETS: VIEW_PRESETS,
    svgIcon: svgIcon,
    getViewPreset: getViewPreset,
    applyViewPreset: applyViewPreset,
    flattenViews: flattenViews,
    getGlobalPosition: getGlobalPosition,
    stepGlobalView: stepGlobalView,
    enhanceShellNav: enhanceShellNav,
    syncRailFooter: syncRailFooter,
  };
})(typeof window !== 'undefined' ? window : this);
