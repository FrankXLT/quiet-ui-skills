/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 — Two-Axis Universal Stage Portal Controller (World × Distilled View)
 */
(function (window, document) {
  'use strict';

  const state = {
    world: '', view: '', medium: 'auto', theme: 'white',
    nav: 'auto', vp: 'fill', zoom: 'fit', density: 'd2',
    corners: 'auto', scale: '100', isMounted: false, renderedView: '',
  };
  let manifest = { worlds: [] };

  function escHtml(val) {
    return String(val == null ? '' : val)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function loadManifest() {
    const el = document.getElementById('va-v9-manifest');
    if (!el) return;
    try { manifest = JSON.parse(el.textContent || '{"worlds":[]}'); } catch (_e) {}
  }

  function findWorld(worldId) {
    const list = manifest.worlds || [];
    return list.find(function (w) { return w.world_id === worldId; }) || list[0] || null;
  }

  function findView(worldObj, viewId) {
    if (!worldObj || !worldObj.views || !worldObj.views.length) return null;
    return worldObj.views.find(function (v) { return v.view_id === viewId; }) || worldObj.views[0];
  }

  function readUrlParams() {
    const p = new URLSearchParams(window.location.search);
    ['world', 'view', 'medium', 'theme', 'nav', 'vp', 'zoom', 'density', 'corners', 'scale'].forEach(function (k) {
      if (p.has(k) && p.get(k)) state[k] = p.get(k);
    });
    const w = findWorld(state.world);
    if (w) {
      state.world = w.world_id;
      const v = findView(w, state.view);
      if (v) state.view = v.view_id;
    }
  }

  function syncUrlParams() {
    const p = new URLSearchParams();
    p.set('world', state.world);
    p.set('view', state.view);
    p.set('medium', state.medium);
    p.set('theme', state.theme);
    p.set('nav', state.nav);
    p.set('vp', state.vp);
    if (state.zoom !== 'fit') p.set('zoom', state.zoom);
    if (state.density !== 'd2') p.set('density', state.density);
    if (state.corners !== 'auto') p.set('corners', state.corners);
    if (state.scale !== '100') p.set('scale', state.scale);
    window.history.replaceState(null, '', window.location.pathname + '?' + p.toString());
  }

  function computeEffectiveNav(nav, viewMeta, width) {
    const allowed = (viewMeta && viewMeta.allowed_navs) ? viewMeta.allowed_navs : ['n0', 'n1', 'n2', 'n3', 'n4'];
    const defNav = (viewMeta && viewMeta.default_nav) ? viewMeta.default_nav : (allowed[0] || 'n0');
    if (nav && nav !== 'auto') {
      if (nav === 'n4' && width >= 700) return defNav;
      return allowed.indexOf(nav) !== -1 ? nav : defNav;
    }
    if (width < 700 && allowed.indexOf('n4') !== -1) return 'n4';
    return defNav;
  }

  function getActiveDimensions() {
    return window.QuietPortalResize.parseDimensions(state.vp);
  }

  function updatePortalDimensions() {
    const mat = document.getElementById('va-portal-mat');
    const scaler = document.getElementById('va-portal-scaler');
    const iframe = document.getElementById('va-stage-portal');
    if (mat && scaler && iframe) {
      window.QuietPortalResize.applyPortalDimensions(scaler, iframe, mat, getActiveDimensions(), state.zoom);
    }
  }

  function effectiveMedium(viewMeta) {
    if (state.medium === 'm1') return 'm1';
    return (viewMeta && viewMeta.default_medium) ? viewMeta.default_medium : 'm2';
  }

  function buildIframeSrcDoc(viewMeta) {
    const cssEl = document.getElementById('va-bundled-portal-css');
    const jsEl = document.getElementById('va-bundled-stage-js');
    const med = effectiveMedium(viewMeta);
    const chrom = (viewMeta && viewMeta.chromatic_code) ? viewMeta.chromatic_code : 'c4';
    return '<!DOCTYPE html>\n<html lang="en" data-theme="' + escHtml(state.theme) +
      '" data-medium="' + escHtml(med) + '" data-chromatic="' + escHtml(chrom) +
      '" data-density="' + escHtml(state.density) + '" data-corners="' + escHtml(state.corners) +
      '" data-world="' + escHtml(state.world) + '" data-view="' + escHtml(state.view) +
      '" data-nav-shell="' + escHtml(state.nav) + '" data-effective-nav="n0" data-form-factor="desktop">\n<head>\n' +
      '<meta charset="utf-8">\n' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">\n' +
      '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous">\n' +
      '<style id="va-portal-styles">\n' + (cssEl ? cssEl.textContent : '') + '\n</style>\n</head>\n<body>\n' +
      '<div class="va-app-shell">\n' +
      '  <header id="va-shell-topbar" class="va-shell-topbar"><a class="va-shell-brand" href="#stage"></a>' +
      '<nav class="va-shell-topbar-links" aria-label="Section Navigation"></nav>' +
      '<div class="va-shell-topbar-status" aria-label="Unit Telemetry Status"></div>' +
      '<button type="button" id="va-drawer-open-btn" class="va-btn-ghost" aria-label="Open Navigation Drawer" onclick="openShellDrawer()">' +
      '<i class="fa-solid fa-bars" aria-hidden="true"></i></button></header>\n' +
      '  <aside id="va-shell-rail" class="va-shell-rail" aria-label="Section Spine"></aside>\n' +
      '  <main id="va-stage-main" class="va-stage" tabindex="-1"></main>\n' +
      '  <nav id="va-shell-bottomdock" class="va-shell-bottomdock" aria-label="Mobile Dock"></nav>\n' +
      '  <dialog id="va-shell-drawer" closedby="any" aria-label="Navigation Drawer">' +
      '<div class="va-drawer-header"><strong>View Navigation</strong>' +
      '<button type="button" class="va-btn-ghost" aria-label="Close Drawer" onclick="closeShellDrawer()" autofocus><i class="fa-solid fa-xmark" aria-hidden="true"></i></button></div>' +
      '<nav class="va-drawer-nav"></nav></dialog>\n' +
      '</div>\n<script>\n' +
      'window.openShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.showModal)d.showModal();};\n' +
      'window.closeShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.close)d.close();};\n' +
      (jsEl ? jsEl.textContent : '') + '\n<\/script>\n</body>\n</html>';
  }

  function syncShellNav(doc, viewMeta) {
    const icon = (viewMeta && viewMeta.nav_icon) ? viewMeta.nav_icon : 'fa-compass';
    const brandLbl = (viewMeta && viewMeta.nav_brand) ? viewMeta.nav_brand : 'Quiet UI';
    const topBrandLbl = (viewMeta && viewMeta.topbar_brand) ? viewMeta.topbar_brand : brandLbl;
    const railBrandLbl = (viewMeta && viewMeta.rail_brand) ? viewMeta.rail_brand : brandLbl;
    const items = (viewMeta && viewMeta.nav_items) ? viewMeta.nav_items : ['Overview'];
    const anchors = (viewMeta && viewMeta.nav_anchors) ? viewMeta.nav_anchors : [];
    const icons = ['fa-heart-pulse', 'fa-lungs', 'fa-syringe', 'fa-bell'];

    const brand = doc.querySelector('#va-shell-topbar .va-shell-brand');
    if (brand) brand.innerHTML = '<i class="fa-solid ' + escHtml(icon) + '" aria-hidden="true"></i> ' + escHtml(topBrandLbl);

    const statusEl = doc.querySelector('#va-shell-topbar .va-shell-topbar-status');
    const topStatus = (viewMeta && Array.isArray(viewMeta.topbar_status)) ? viewMeta.topbar_status : [];
    if (statusEl) {
      statusEl.innerHTML = topStatus.map(function (st) {
        return '<span class="va-pill" data-variant="' + escHtml(st.variant || 'status') + '" data-state="' +
          escHtml(st.state || 'nominal') + '">' + escHtml(st.text || '') + '</span>';
      }).join('');
    }

    const effNav = (doc.documentElement && doc.documentElement.dataset.effectiveNav) || 'n1';
    const hideTopLinks = effNav === 'n3' && topStatus.length > 0;
    const topLinks = doc.querySelector('#va-shell-topbar .va-shell-topbar-links');
    if (topLinks) {
      topLinks.innerHTML = hideTopLinks ? '' : items.map(function (lbl, i) {
        const href = anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage';
        return '<a class="va-shell-topbar-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '">' + escHtml(lbl) + '</a>';
      }).join('');
    }

    const rail = doc.getElementById('va-shell-rail');
    if (rail) {
      rail.innerHTML = '<div class="va-rail-brand"><i class="fa-solid ' + escHtml(icon) + '" aria-hidden="true"></i> <span>' + escHtml(railBrandLbl) + '</span></div>' +
        items.map(function (lbl, i) {
          const href = anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage';
          return '<a class="va-rail-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '"><i class="fa-solid ' + icons[i % 4] + '" aria-hidden="true"></i> ' + escHtml(lbl) + '</a>';
        }).join('');
    }

    const dock = doc.getElementById('va-shell-bottomdock');
    if (dock) {
      dock.innerHTML = items.slice(0, 3).map(function (lbl, i) {
        const shortLbl = lbl.split(' ')[0];
        const href = anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage';
        return '<a href="' + href + '"' + (i === 0 ? ' class="is-active"' : '') + '><i class="fa-solid ' + icons[i % 4] + '" aria-hidden="true"></i>' + escHtml(shortLbl) + '</a>';
      }).join('') + '<button type="button" onclick="openShellDrawer()"><i class="fa-solid fa-bars" aria-hidden="true"></i>Menu</button>';
    }

    const drawerNav = doc.querySelector('#va-shell-drawer .va-drawer-nav');
    if (drawerNav) {
      drawerNav.innerHTML = items.map(function (lbl, i) {
        const href = anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage';
        return '<a class="va-drawer-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '" onclick="closeShellDrawer()">' + escHtml(lbl) + '</a>';
      }).join('');
    }
  }

  function syncIframeAttributes() {
    const iframe = document.getElementById('va-stage-portal');
    const worldObj = findWorld(state.world);
    const viewMeta = findView(worldObj, state.view);
    if (!iframe || !iframe.contentDocument || !viewMeta) return;
    const docEl = iframe.contentDocument.documentElement;
    if (!docEl) return;
    const dims = getActiveDimensions();
    const stageW = dims ? dims.width : (iframe.clientWidth || window.innerWidth);
    docEl.dataset.theme = state.theme;
    docEl.dataset.medium = effectiveMedium(viewMeta);
    docEl.dataset.chromatic = viewMeta.chromatic_code || 'c4';
    docEl.dataset.density = state.density;
    docEl.dataset.corners = state.corners;
    docEl.dataset.world = state.world;
    docEl.dataset.view = state.view;
    docEl.dataset.navShell = state.nav;
    docEl.dataset.effectiveNav = computeEffectiveNav(state.nav, viewMeta, stageW);
    docEl.dataset.formFactor = stageW <= 480 ? 'touch' : 'desktop';
    if (state.scale && state.scale !== '100') docEl.style.fontSize = state.scale + '%';
    else docEl.style.removeProperty('font-size');
  }

  function syncIframeDOM() {
    const iframe = document.getElementById('va-stage-portal');
    const worldObj = findWorld(state.world);
    const viewMeta = findView(worldObj, state.view);
    if (!iframe || !iframe.contentDocument || !viewMeta) return;
    syncIframeAttributes();
    const main = iframe.contentDocument.getElementById('va-stage-main');
    if (main && state.renderedView !== state.view) {
      const tpl = document.getElementById('tpl-view-' + state.view);
      main.innerHTML = tpl ? tpl.innerHTML : '<div class="v9-stage-inner">View template not found</div>';
      syncShellNav(iframe.contentDocument, viewMeta);
      state.renderedView = state.view;
      state.renderedNav = iframe.contentDocument.documentElement.dataset.effectiveNav;
      if (iframe.contentWindow.QuietEvidenceRuntime) iframe.contentWindow.QuietEvidenceRuntime.boot();
      if (iframe.contentWindow.QuietWorld01Runtime) iframe.contentWindow.QuietWorld01Runtime.boot(iframe.contentDocument);
      main.scrollTop = 0;
      if (iframe.contentWindow) iframe.contentWindow.scrollTo(0, 0);
    } else if (iframe.contentDocument.documentElement.dataset.effectiveNav !== state.renderedNav) {
      syncShellNav(iframe.contentDocument, viewMeta);
      state.renderedNav = iframe.contentDocument.documentElement.dataset.effectiveNav;
    }
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.bindPortalScrollTuck(iframe);
  }

  function syncBarControls() {
    const worldObj = findWorld(state.world);
    const viewMeta = findView(worldObj, state.view);
    document.documentElement.dataset.medium = state.medium;

    const wSel = document.getElementById('va-world-select');
    if (wSel && wSel.value !== state.world) wSel.value = state.world;

    const vSel = document.getElementById('va-view-select');
    if (vSel && worldObj) {
      const optsHtml = worldObj.views.map(function (v) {
        return '<option value="' + escHtml(v.view_id) + '">' + escHtml(v.option_label) + '</option>';
      }).join('');
      if (vSel.dataset.worldLoaded !== worldObj.world_id) {
        vSel.innerHTML = optsHtml;
        vSel.dataset.worldLoaded = worldObj.world_id;
      }
      vSel.value = state.view;
    }

    const sheetBtn = document.getElementById('va-sheet-toggle-btn');
    if (sheetBtn) {
      const isSheet = state.medium === 'm1';
      sheetBtn.classList.toggle('is-active', isSheet);
      sheetBtn.setAttribute('aria-pressed', isSheet ? 'true' : 'false');
    }

    const navSel = document.getElementById('va-nav-select');
    const allowed = viewMeta ? viewMeta.allowed_navs : ['n0', 'n1', 'n2', 'n3', 'n4'];
    if (navSel) {
      navSel.value = state.nav;
      Array.from(navSel.options).forEach(function (opt) {
        if (opt.value === 'auto') return;
        const ok = allowed.indexOf(opt.value) !== -1;
        opt.disabled = !ok;
      });
    }

    const vpSel = document.getElementById('va-vp-select');
    if (vpSel) vpSel.value = state.vp;
    const stageTools = document.getElementById('va-stage-tools');
    if (stageTools) stageTools.hidden = state.vp === 'fill';
    const zoomBtn = document.getElementById('va-zoom-btn');
    if (zoomBtn) zoomBtn.textContent = state.zoom.toUpperCase();

    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.syncSheetControls(state, allowed);
  }

  function applyState(worldChanged) {
    const worldObj = findWorld(state.world);
    if (worldObj && (worldChanged || !findView(worldObj, state.view))) {
      state.view = worldObj.views[0].view_id;
    }
    const viewMeta = findView(worldObj, state.view);
    const iframe = document.getElementById('va-stage-portal');
    if (!iframe || !viewMeta) return;
    updatePortalDimensions();
    if (!state.isMounted || !iframe.contentDocument || !iframe.contentDocument.getElementById('va-stage-main')) {
      state.renderedView = '';
      iframe.onload = function () { state.isMounted = true; updatePortalDimensions(); syncIframeDOM(); };
      iframe.srcdoc = buildIframeSrcDoc(viewMeta);
    } else {
      syncIframeDOM();
    }
    syncBarControls();
    syncUrlParams();
  }

  function openBridgeDialog() {
    const worldObj = findWorld(state.world);
    const viewMeta = findView(worldObj, state.view);
    const dlg = document.getElementById('va-bridge-dialog');
    const body = document.getElementById('va-bridge-body');
    const title = document.getElementById('va-bridge-title');
    if (!dlg || !body || !viewMeta) return;
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

  function printActiveStage() {
    const iframe = document.getElementById('va-stage-portal');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    }
  }

  function stepView(delta) {
    const worldObj = findWorld(state.world);
    if (!worldObj || !worldObj.views.length) return;
    const list = worldObj.views;
    let idx = list.findIndex(function (v) { return v.view_id === state.view; });
    idx = (idx + delta + list.length) % list.length;
    state.view = list[idx].view_id;
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
    applyState(false);
  }

  function initControls() {
    const wSel = document.getElementById('va-world-select');
    if (wSel) wSel.addEventListener('change', function (e) { state.world = e.target.value; applyState(true); });
    const vSel = document.getElementById('va-view-select');
    if (vSel) vSel.addEventListener('change', function (e) { state.view = e.target.value; applyState(false); });
    ['vp', 'density', 'corners', 'nav'].forEach(function (k) {
      const el = document.getElementById('va-' + k + '-select');
      if (el) el.addEventListener('change', function (e) { state[k] = e.target.value; applyState(false); });
    });
    const prev = document.getElementById('va-step-prev');
    const next = document.getElementById('va-step-next');
    if (prev) prev.addEventListener('click', function () { stepView(-1); });
    if (next) next.addEventListener('click', function () { stepView(1); });

    const sheetBtn = document.getElementById('va-sheet-toggle-btn');
    if (sheetBtn) sheetBtn.addEventListener('click', function () { state.medium = (state.medium === 'm1') ? 'auto' : 'm1'; applyState(false); });
    const printBtn = document.getElementById('va-print-btn');
    if (printBtn) printBtn.addEventListener('click', printActiveStage);
    const bridgeBtn = document.getElementById('va-bridge-btn');
    if (bridgeBtn) bridgeBtn.addEventListener('click', openBridgeDialog);

    const onRotate = function () { const d = getActiveDimensions(); if (d) { state.vp = d.height + 'x' + d.width; applyState(false); } };
    const onZoomToggle = function () { state.zoom = (state.zoom === 'fit') ? '1:1' : 'fit'; updatePortalDimensions(); syncBarControls(); syncUrlParams(); };
    const rotBtn = document.getElementById('va-rotate-btn');
    const zoomBtn = document.getElementById('va-zoom-btn');
    if (rotBtn) rotBtn.addEventListener('click', onRotate);
    if (zoomBtn) zoomBtn.addEventListener('click', onZoomToggle);

    const custBtn = document.getElementById('va-customize-btn');
    if (custBtn) custBtn.addEventListener('click', function () {
      const sheet = document.getElementById('va-customize-sheet');
      if (sheet && typeof sheet.showModal === 'function') sheet.showModal();
    });
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.initSheetEvents(state, applyState, onRotate, onZoomToggle, printActiveStage);

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 700 && window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
      updatePortalDimensions();
      syncIframeDOM();
    });
    window.QuietPortalResize.initResizeHandles(
      document.getElementById('va-portal-scaler'), document.getElementById('va-stage-portal'), document.getElementById('va-portal-mat'),
      function (w, h) { state.vp = w + 'x' + h; syncIframeDOM(); syncUrlParams(); syncBarControls(); }
    );
  }

  window.addEventListener('DOMContentLoaded', function () {
    loadManifest();
    readUrlParams();
    initControls();
    applyState(false);
  });
  window.QuietStudioPortalV9 = { state: state, applyState: applyState, openBridgeDialog: openBridgeDialog };
})(window, document);
