/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.0.1 — Universal Responsive Stage Portal Controller
 */
(function(window) {
  'use strict';

  const ATLAS_SECTIONS = [
    { value: 'all', label: 'All 45' },
    { value: 'systems', label: '1. Systems' },
    { value: 'data', label: '2. Data' },
    { value: 'flows', label: '3. Flows' },
    { value: 'strategy', label: '4. Product' },
    { value: 'charts', label: '5. Charts' },
    { value: 'workbench', label: 'DSL Workbench' }
  ];
  const state = {
    view: 'ui', tier: 'doc-1', atlasSec: 'all', vp: 'fill', zoom: 'fit',
    nav: 'auto', theme: 'white', density: 'd2', corners: 'auto', scale: '100',
    isMounted: false, renderedTier: ''
  };
  let uiTierOptions = [];
  let renderedSelectMode = 'ui';

  function readUrlParams() {
    const p = new URLSearchParams(window.location.search);
    ['view', 'tier', 'atlasSec', 'vp', 'zoom', 'nav', 'theme', 'density', 'corners', 'scale'].forEach(function(k) {
      if (p.has(k)) state[k] = p.get(k);
    });
  }

  function syncUrlParams() {
    const p = new URLSearchParams();
    ['view', 'tier', 'vp', 'zoom', 'nav', 'theme', 'density', 'corners'].forEach(function(k) { p.set(k, state[k]); });
    if (state.scale !== '100') p.set('scale', state.scale);
    if (state.view === 'diagrams' && state.atlasSec !== 'all') p.set('atlasSec', state.atlasSec);
    window.history.replaceState(null, '', window.location.pathname + '?' + p.toString());
  }

  function getTierMeta(tier) {
    const tpl = document.getElementById('tpl-tier-' + tier);
    const allowedRaw = (tpl && tpl.dataset.allowedNavs) ? tpl.dataset.allowedNavs : 'n0,n1,n2,n3,n4';
    const allowed = allowedRaw.split(',').map(function(s) { return s.trim(); }).filter(Boolean);
    const defaultNav = (tpl && tpl.dataset.defaultNav) ? tpl.dataset.defaultNav : (allowed[0] || 'n0');
    const stageLock = (tpl && tpl.dataset.stageLock) ? tpl.dataset.stageLock :
      ((tier === 'deck-1' || tier === 'hud-1' || tier === 'app-tree') ? '100dvh' : 'scroll');
    return { tpl: tpl, allowed: allowed, defaultNav: defaultNav, stageLock: stageLock };
  }

  function computeEffectiveNav(nav, tier, width) {
    const meta = getTierMeta(tier);
    if (nav && nav !== 'auto') return meta.allowed.indexOf(nav) !== -1 ? nav : meta.defaultNav;
    if (width < 760 && meta.allowed.indexOf('n4') !== -1) return 'n4';
    return meta.defaultNav;
  }

  function getActiveDimensions() { return window.QuietPortalResize.parseDimensions(state.vp); }

  function updatePortalDimensions() {
    const mat = document.getElementById('va-portal-mat');
    const scaler = document.getElementById('va-portal-scaler');
    const iframe = document.getElementById('va-stage-portal');
    if (mat && scaler && iframe) {
      window.QuietPortalResize.applyPortalDimensions(scaler, iframe, mat, getActiveDimensions(), state.zoom);
    }
  }

  function resolveDocsAsset(relPath) {
    const path = window.location.pathname || '';
    if (path.indexOf('/customizations/') !== -1) return '../../docs/' + relPath;
    if (path.endsWith('/quiet-ui-showcase.html')) return './docs/' + relPath;
    return './' + relPath;
  }

  function buildIframeSrcDoc() {
    const cssEl = document.getElementById('va-bundled-portal-css');
    const jsEl = document.getElementById('va-bundled-tier-js');
    const hasCustom = document.documentElement.dataset.customStyles === 'true';
    const baseHref = window.location.href.split('?')[0].split('#')[0];
    const earthriseUrl = resolveDocsAsset('assets/as08-14-2383.jpg');
    return '<!DOCTYPE html>\n<html lang="en" style="--hud-earthrise-url: url(\'' + earthriseUrl + '\');" data-theme="' + state.theme +
      '" data-density="' + state.density + '" data-corners="' + state.corners +
      '" data-tier="' + state.tier + '" data-nav-shell="' + state.nav +
      '" data-effective-nav="n0" data-form-factor="desktop" data-stage-lock="scroll">\n<head>\n' +
      '<meta charset="utf-8">\n<base href="' + baseHref + '">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' +
      '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous">\n' +
      (hasCustom ? '<link rel="stylesheet" href="./styles/quiet-ui-tokens.css">\n<link rel="stylesheet" href="./styles/overrides.css">\n' : '') +
      '<style id="va-portal-styles">\n' + (cssEl ? cssEl.textContent : '') + '\n</style>\n</head>\n<body>\n<div class="va-app-shell">\n' +
      '  <header id="va-shell-topbar" class="va-shell-topbar"><a class="va-shell-brand" href="#stage"><i class="fa-solid fa-book-open"></i> DSOC Monograph</a>' +
      '<nav class="va-shell-topbar-links" aria-label="Primary Navigation"><a class="va-shell-topbar-link is-active" href="#stage">Abstract</a><a class="va-shell-topbar-link" href="#stage">Optical Stack</a></nav>' +
      '<button type="button" id="va-drawer-open-btn" class="va-btn-ghost" aria-label="Open Navigation Drawer" onclick="openShellDrawer()"><i class="fa-solid fa-bars" aria-hidden="true"></i></button></header>\n' +
      '  <aside id="va-shell-rail" class="va-shell-rail" aria-label="Workspace Rail"><a class="va-rail-link is-active" href="#stage"><i class="fa-solid fa-compass" aria-hidden="true"></i> Abstract</a>' +
      '<a class="va-rail-link" href="#stage"><i class="fa-solid fa-wave-square" aria-hidden="true"></i> Optical Stack</a><a class="va-rail-link" href="#stage"><i class="fa-solid fa-sliders" aria-hidden="true"></i> Link Ledger</a></aside>\n' +
      '  <main id="va-stage-main" class="va-stage"></main>\n' +
      '  <nav id="va-shell-bottomdock" class="va-shell-bottomdock" aria-label="Mobile Dock"><button type="button" class="is-active"><i class="fa-solid fa-compass" aria-hidden="true"></i>Abstract</button>' +
      '<button type="button"><i class="fa-solid fa-wave-square" aria-hidden="true"></i>Optical</button><button type="button"><i class="fa-solid fa-sliders" aria-hidden="true"></i>Ledger</button>' +
      '<button type="button" onclick="openShellDrawer()"><i class="fa-solid fa-bars" aria-hidden="true"></i>Menu</button></nav>\n' +
      '  <dialog id="va-shell-drawer" closedby="any" aria-label="Navigation Drawer"><div class="va-drawer-header"><strong>Mission Navigation</strong><button type="button" class="va-btn-ghost" aria-label="Close Drawer" onclick="closeShellDrawer()"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button></div>' +
      '<nav class="va-drawer-nav"><a class="va-drawer-link" href="#stage">Abstract</a><a class="va-drawer-link" href="#stage">Optical Stack</a><a class="va-drawer-link" href="#stage">Link Ledger</a></nav></dialog>\n' +
      '  <dialog id="va-fig-zoom-dialog" closedby="any" aria-label="Expanded Figure"><div class="va-fig-zoom-content"></div></dialog>\n' +
      '</div>\n<script>\nwindow.openShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.showModal)d.showModal();};\nwindow.closeShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.close)d.close();};\n' + (jsEl ? jsEl.textContent : '') + '\n<\/script>\n</body>\n</html>';
  }

  const TIER_SHELL_NAV = {
    'doc-1':    ['fa-book-open', 'DSOC Monograph', ['Abstract', 'Optical Stack', 'Allan Variance', 'Link Ledger']],
    'doc-2':    ['fa-file-signature', 'NASA KDP-C Board', ['BLUF', 'Impact KPIs', 'Risk Matrix', 'Trade Study']],
    'doc-3':    ['fa-microchip', 'CCSDS 133.0-B-2', ['Bitfield Header', 'Normative Clauses', 'FOP-1 FSM', 'Schema Diff']],
    'doc-4b':   ['fa-code', 'DSOC Ground SDK', ['6-Stage Pipeline', 'Decision Router', 'BAR0 MMIO', 'Python API']],
    'doc-4a':   ['fa-clipboard-check', 'SOP-DSOC-704', ['Laser Interlock', 'Pass Lifelines', 'Procedure Steps', 'CLI Console']],
    'bridge-1': ['fa-calculator', 'Link Margin Solver', ['Equations', 'Parametric Solver', 'Mission Ledger', 'Gradients']],
    'deck-1':   ['fa-display', 'FRR Flight Briefing', ['Exec Summary', 'Link Budget', 'SNSPD Array', 'Readiness Poll']],
    'bridge-2': ['fa-satellite-dish', 'DSN 810-005 Matrix', ['Goldstone', 'Madrid', 'Canberra', 'Phase Skew']],
    'app-2':    ['fa-wave-square', 'SNSPD HIL Bench', ['Quad Waveforms', 'Phase Residual', 'BAR0 Registers', 'Cryo Channels']],
    'app-1':    ['fa-triangle-exclamation', 'Psyche Flight Ops', ['Discrepancy Queue', 'Comm / Optical', 'GNC Pointing', 'Incident Audit']],
    'app-4':    ['fa-calendar-day', 'NRHO Ops Planner', ['Orbit Timeline', 'Flight Tasks', 'Focus Block', 'Staging Inbox']],
    'app-3':    ['fa-chart-pie', 'DSN Executive', ['Trajectory Gain', 'Science Volume', 'Complex Share', 'Pass Schedule']],
    'app-5':    ['fa-moon', 'Crew Readiness', ['Circadian Phase', 'Readiness Ring', 'Cabin Biometrics', 'Biomarker Gate']],
    'app-tree': ['fa-folder-tree', 'Packet Explorer', ['Packet Stream', 'Header Spec', 'ER Lineage', 'JSONB Inspector']],
    'hud-1':    ['fa-crosshairs', 'Cupola AR HUD', ['Boresight', 'Attitude LOS', 'Astrometry', 'Link Margin']],
    'ctrl-1':   ['fa-sliders', 'HALO ECLSS Console', ['ECLSS Loop', 'Power Bus', 'Thermal TCS', 'Optical Cryo']]
  };
  const NAV_ITEM_ICONS = ['fa-compass', 'fa-wave-square', 'fa-sliders', 'fa-shield-halved'];

  function syncShellNav(doc, tier) {
    const cfg = TIER_SHELL_NAV[tier] || TIER_SHELL_NAV['doc-1'];
    const brand = doc.querySelector('#va-shell-topbar .va-shell-brand');
    if (brand) brand.innerHTML = '<i class="fa-solid ' + cfg[0] + '" aria-hidden="true"></i> ' + cfg[1];
    const topLinks = doc.querySelector('#va-shell-topbar .va-shell-topbar-links');
    if (topLinks) {
      topLinks.innerHTML = cfg[2].map(function(lbl, i) {
        return '<a class="va-shell-topbar-link' + (i === 0 ? ' is-active' : '') + '" href="#stage">' + lbl + '</a>';
      }).join('');
    }
    const rail = doc.getElementById('va-shell-rail');
    if (rail) {
      rail.innerHTML = '<div class="va-rail-brand"><i class="fa-solid ' + cfg[0] + '" aria-hidden="true"></i> <span>' + cfg[1] + '</span></div>' +
        cfg[2].map(function(lbl, i) {
          return '<a class="va-rail-link' + (i === 0 ? ' is-active' : '') + '" href="#stage"><i class="fa-solid ' + NAV_ITEM_ICONS[i % 4] + '" aria-hidden="true"></i> ' + lbl + '</a>';
        }).join('');
    }
    const dock = doc.getElementById('va-shell-bottomdock');
    if (dock) {
      dock.innerHTML = cfg[2].slice(0, 3).map(function(lbl, i) {
        const shortLbl = lbl.split(' ')[0];
        return '<button type="button"' + (i === 0 ? ' class="is-active"' : '') + '><i class="fa-solid ' + NAV_ITEM_ICONS[i] + '" aria-hidden="true"></i>' + shortLbl + '</button>';
      }).join('') + '<button type="button" onclick="openShellDrawer()"><i class="fa-solid fa-bars" aria-hidden="true"></i>Menu</button>';
    }
    const drawerNav = doc.querySelector('#va-shell-drawer .va-drawer-nav');
    if (drawerNav) {
      drawerNav.innerHTML = cfg[2].map(function(lbl, i) {
        return '<a class="va-drawer-link' + (i === 0 ? ' is-active' : '') + '" href="#stage" onclick="closeShellDrawer()">' + lbl + '</a>';
      }).join('');
    }
  }

  function syncIframeAttributes() {
    const iframe = document.getElementById('va-stage-portal');
    if (!iframe || !iframe.contentDocument || state.view !== 'ui') return;
    const docEl = iframe.contentDocument.documentElement;
    if (!docEl) return;
    const dims = getActiveDimensions();
    const stageW = dims ? dims.width : (iframe.clientWidth || window.innerWidth);
    const meta = getTierMeta(state.tier);
    docEl.dataset.theme = state.theme;
    docEl.dataset.density = state.density;
    docEl.dataset.corners = state.corners;
    docEl.dataset.tier = state.tier;
    docEl.dataset.navShell = state.nav;
    docEl.dataset.effectiveNav = computeEffectiveNav(state.nav, state.tier, stageW);
    docEl.dataset.formFactor = (stageW <= 480) ? 'touch' : 'desktop';
    docEl.dataset.stageLock = (state.tier === 'app-tree' && stageW < 1100) ? 'scroll' : meta.stageLock;
    if (state.scale && state.scale !== '100') docEl.style.fontSize = state.scale + '%';
    else docEl.style.removeProperty('font-size');
  }

  function syncIframeDOM() {
    const iframe = document.getElementById('va-stage-portal');
    if (!iframe || !iframe.contentDocument) return;
    syncIframeAttributes();
    const main = iframe.contentDocument.getElementById('va-stage-main');
    if (main && state.renderedTier !== state.tier) {
      const meta = getTierMeta(state.tier);
      main.innerHTML = meta.tpl ? meta.tpl.innerHTML : '<div style="padding:2rem;">Stage Content Not Found</div>';
      syncShellNav(iframe.contentDocument, state.tier);
      state.renderedTier = state.tier;
    }
    if (window.QuietStudioSheet) window.QuietStudioSheet.bindPortalScrollTuck(iframe);
  }

  function syncCenterSelect() {
    const sel = document.getElementById('va-tier-select');
    if (!sel) return;
    const targetMode = (state.view === 'diagrams') ? 'diagrams' : 'ui';
    if (renderedSelectMode !== targetMode) {
      const list = (targetMode === 'diagrams') ? ATLAS_SECTIONS : uiTierOptions;
      sel.innerHTML = list.map(function(o) { return '<option value="' + o.value + '">' + o.label + '</option>'; }).join('');
      renderedSelectMode = targetMode;
    }
    sel.value = (targetMode === 'diagrams') ? state.atlasSec : state.tier;
    sel.setAttribute('aria-label', targetMode === 'diagrams' ? 'Select Atlas Section' : 'Select Stage Tier');
  }

  function syncBarControls() {
    document.documentElement.dataset.studioView = state.view;
    syncCenterSelect();
    const meta = getTierMeta(state.tier);
    const vpSel = document.getElementById('va-vp-select');
    if (vpSel) vpSel.value = state.vp;
    const navSel = document.getElementById('va-nav-select');
    if (navSel) {
      navSel.value = state.nav;
      Array.from(navSel.options).forEach(function(opt) {
        if (opt.value === 'auto') return;
        const ok = meta.allowed.indexOf(opt.value) !== -1;
        opt.disabled = !ok;
        opt.title = ok ? '' : ('Disabled for ' + state.tier);
      });
    }
    const stageTools = document.getElementById('va-stage-tools');
    if (stageTools) stageTools.hidden = (state.vp === 'fill');
    const zoomBtn = document.getElementById('va-zoom-btn');
    if (zoomBtn) zoomBtn.textContent = state.zoom.toUpperCase();
    [['va-view-ui-btn', 'ui'], ['va-view-diag-btn', 'diagrams']].forEach(function(pair) {
      const btn = document.getElementById(pair[0]);
      if (btn) {
        btn.classList.toggle('is-active', state.view === pair[1]);
        btn.setAttribute('aria-selected', state.view === pair[1] ? 'true' : 'false');
      }
    });
    if (window.QuietStudioSheet) window.QuietStudioSheet.syncSheetControls(state, meta.allowed);
  }

  function postAtlasSync(iframe) {
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage({
        type: 'quiet-ui-sync', theme: state.theme, density: state.density,
        corners: state.corners, atlasSection: state.atlasSec
      }, '*');
    }
  }

  function applyState() {
    const iframe = document.getElementById('va-stage-portal');
    if (!iframe) return;
    updatePortalDimensions();
    if (state.view === 'diagrams') {
      const targetSrc = resolveDocsAsset('diagrams.html') + '?embed=1&theme=' + encodeURIComponent(state.theme);
      state.isMounted = false;
      state.renderedTier = '';
      iframe.removeAttribute('srcdoc');
      if (!iframe.getAttribute('src') || iframe.getAttribute('src').indexOf('diagrams.html') === -1) {
        iframe.onload = function() {
          if (window.QuietStudioSheet) window.QuietStudioSheet.bindPortalScrollTuck(iframe);
          postAtlasSync(iframe);
        };
        iframe.src = targetSrc;
      } else {
        postAtlasSync(iframe);
      }
      syncBarControls();
      syncUrlParams();
      return;
    }
    if (!state.isMounted || !iframe.contentDocument || !iframe.contentDocument.getElementById('va-stage-main')) {
      state.renderedTier = '';
      iframe.removeAttribute('src');
      iframe.onload = function() { state.isMounted = true; updatePortalDimensions(); syncIframeDOM(); };
      iframe.srcdoc = buildIframeSrcDoc();
    } else {
      syncIframeDOM();
    }
    syncBarControls();
    syncUrlParams();
  }

  function stepCenterOption(delta) {
    const list = (state.view === 'diagrams') ? ATLAS_SECTIONS : uiTierOptions;
    if (!list.length) return;
    const curVal = (state.view === 'diagrams') ? state.atlasSec : state.tier;
    let idx = list.findIndex(function(o) { return o.value === curVal; });
    idx = (idx + delta + list.length) % list.length;
    if (state.view === 'diagrams') state.atlasSec = list[idx].value;
    else state.tier = list[idx].value;
    if (window.QuietStudioSheet) window.QuietStudioSheet.untuckStudioBar();
    applyState();
  }

  function initControls() {
    const tierSel = document.getElementById('va-tier-select');
    if (tierSel) {
      uiTierOptions = Array.from(tierSel.options).map(function(o) { return { value: o.value, label: o.textContent }; });
      if (uiTierOptions.length && !uiTierOptions.some(function(o) { return o.value === state.tier; })) state.tier = uiTierOptions[0].value;
      tierSel.addEventListener('change', function(e) {
        if (state.view === 'diagrams') state.atlasSec = e.target.value;
        else state.tier = e.target.value;
        if (window.QuietStudioSheet) window.QuietStudioSheet.untuckStudioBar();
        applyState();
      });
    }
    ['vp', 'theme', 'density', 'corners', 'nav'].forEach(function(k) {
      const el = document.getElementById('va-' + k + '-select');
      if (el) el.addEventListener('change', function(e) { state[k] = e.target.value; applyState(); });
    });
    const prevBtn = document.getElementById('va-step-prev');
    const nextBtn = document.getElementById('va-step-next');
    if (prevBtn) prevBtn.addEventListener('click', function() { stepCenterOption(-1); });
    if (nextBtn) nextBtn.addEventListener('click', function() { stepCenterOption(1); });

    const onRotate = function() { const d = getActiveDimensions(); if (d) { state.vp = d.height + 'x' + d.width; applyState(); } };
    const onZoomToggle = function() { state.zoom = (state.zoom === 'fit') ? '1:1' : 'fit'; updatePortalDimensions(); syncBarControls(); syncUrlParams(); };
    const rotBtn = document.getElementById('va-rotate-btn');
    const zoomBtn = document.getElementById('va-zoom-btn');
    if (rotBtn) rotBtn.addEventListener('click', onRotate);
    if (zoomBtn) zoomBtn.addEventListener('click', onZoomToggle);

    [['va-view-ui-btn', 'ui'], ['va-view-diag-btn', 'diagrams']].forEach(function(pair) {
      const btn = document.getElementById(pair[0]);
      if (btn) btn.addEventListener('click', function() {
        state.view = pair[1];
        if (window.QuietStudioSheet) window.QuietStudioSheet.untuckStudioBar();
        applyState();
      });
    });
    const custBtn = document.getElementById('va-customize-btn');
    if (custBtn) custBtn.addEventListener('click', function() {
      const sheet = document.getElementById('va-customize-sheet');
      if (sheet && typeof sheet.showModal === 'function') sheet.showModal();
    });
    if (window.QuietStudioSheet) window.QuietStudioSheet.initSheetEvents(state, applyState, onRotate, onZoomToggle);
    window.addEventListener('resize', function() {
      if (window.innerWidth >= 700 && window.QuietStudioSheet) window.QuietStudioSheet.untuckStudioBar();
      updatePortalDimensions();
      syncIframeAttributes();
    });
    window.QuietPortalResize.initResizeHandles(
      document.getElementById('va-portal-scaler'), document.getElementById('va-stage-portal'), document.getElementById('va-portal-mat'),
      function(w, h) { state.vp = w + 'x' + h; syncIframeAttributes(); syncUrlParams(); syncBarControls(); }
    );
  }

  window.switchTier = function(slug) { state.view = 'ui'; state.tier = slug; applyState(); };
  window.addEventListener('DOMContentLoaded', function() { readUrlParams(); initControls(); applyState(); });
  window.QuietStudioPortal = { state: state, applyState: applyState, syncIframeDOM: syncIframeDOM };
})(typeof window !== 'undefined' ? window : this);
