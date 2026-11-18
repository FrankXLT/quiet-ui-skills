/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 — Two-Axis Universal Stage Portal Controller (World × Distilled View)
 */
(function (window, document) {
  'use strict';

  const state = {
    studioView: 'worlds', world: '', view: '', medium: 'auto', theme: 'white',
    nav: 'auto', vp: 'fill', zoom: 'fit', density: 'd2',
    corners: 'auto', scale: '100', isMounted: false, renderedView: '',
  };
  let manifest = { worlds: [] };

  function escHtml(val) {
    if (window.QuietStudioSheetV9 && window.QuietStudioSheetV9.escHtml) return window.QuietStudioSheetV9.escHtml(val);
    return String(val == null ? '' : val).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
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
    const rules = {
      mode: ['worlds', 'bench', 'atlas'], medium: ['auto', 'm1'],
      theme: ['white', 'paper', 'dark-paper', 'dark'], nav: ['auto', 'n0', 'n1', 'n2', 'n3', 'n4'],
      zoom: ['fit', '1:1'], density: ['d1', 'd2', 'd3', 'd4'], corners: ['auto', 'sharp', 'subtle', 'rounded', 'soft'],
    };
    if (rules.mode.indexOf(p.get('mode')) !== -1) state.studioView = p.get('mode');
    ['medium', 'theme', 'nav', 'zoom', 'density', 'corners'].forEach(function (k) {
      if (rules[k].indexOf(p.get(k)) !== -1) state[k] = p.get(k);
    });
    const vp = p.get('vp') || '';
    if (vp === 'fill' || /^\d{3,4}x\d{3,4}$/.test(vp)) state.vp = vp;
    const sc = parseInt(p.get('scale') || '', 10);
    if (!isNaN(sc)) state.scale = String(Math.max(75, Math.min(150, sc)));
    if (p.has('world')) state.world = p.get('world') || '';
    if (p.has('view')) state.view = p.get('view') || '';
    if (!p.get('world') && state.view) {
      const hitW = (manifest.worlds || []).find(function (w) { return (w.views || []).some(function (v) { return v.view_id === state.view; }); });
      if (hitW) state.world = hitW.world_id;
    }
    const w = findWorld(state.world);
    if (w) {
      state.world = w.world_id;
      const v = findView(w, state.view);
      if (v) state.view = v.view_id;
    }
  }

  function syncUrlParams() {
    const p = new URLSearchParams();
    if (state.studioView !== 'worlds') p.set('mode', state.studioView);
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

  function resolveDocsAsset(relPath) {
    const path = window.location.pathname || '';
    if (path.indexOf('/customizations/') !== -1) return '../../docs/' + relPath;
    if (path.indexOf('/docs/pilot/') !== -1 || path.indexOf('/docs/v9/') !== -1) return '../' + relPath;
    if (path.indexOf('/quiet-ui-showcase') !== -1) return './docs/' + relPath;
    return './' + relPath;
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
    const baseHref = window.location.href.split('?')[0].split('#')[0];
    const earthriseUrl = resolveDocsAsset('assets/as08-14-2383.jpg');
    const tokStyle = document.getElementById('custom-tokens');
    const ovrStyle = document.getElementById('custom-overrides');
    const hasCustom = document.documentElement.dataset.customStyles === 'true';
    const customTok = tokStyle ? '<style>' + tokStyle.textContent + '</style>\n' : (hasCustom ? '<link rel="stylesheet" href="./styles/quiet-ui-tokens.css">\n' : '');
    const customOvr = ovrStyle ? '<style>' + ovrStyle.textContent + '</style>\n' : (hasCustom ? '<link rel="stylesheet" href="./styles/overrides.css">\n' : '');
    return '<!DOCTYPE html>\n<html lang="en" style="--hud-earthrise-url: url(\'' + escHtml(earthriseUrl) + '\');" data-theme="' + escHtml(state.theme) +
      '" data-medium="' + escHtml(med) + '" data-chromatic="' + escHtml(chrom) +
      '" data-density="' + escHtml(state.density) + '" data-corners="' + escHtml(state.corners) +
      '" data-world="' + escHtml(state.world) + '" data-view="' + escHtml(state.view) +
      '" data-nav-shell="' + escHtml(state.nav) + '" data-effective-nav="n0" data-form-factor="desktop">\n<head>\n' +
      '<meta charset="utf-8">\n<base href="' + escHtml(baseHref) + '">\n' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">\n' +
      '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous">\n' +
      customTok +
      '<style id="va-portal-styles">\n' + (cssEl ? cssEl.textContent : '') + '\n</style>\n' + customOvr + '</head>\n<body>\n' +
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
    const hrefFor = function (i) { return anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage'; };
    const mapLinks = function (list, render) { return list.map(function (lbl, i) { return render(lbl, i, hrefFor(i)); }).join(''); };

    const brand = doc.querySelector('#va-shell-topbar .va-shell-brand');
    if (brand) brand.innerHTML = '<i class="fa-solid ' + escHtml(icon) + '" aria-hidden="true"></i> ' + escHtml(topBrandLbl);

    const statusEl = doc.querySelector('#va-shell-topbar .va-shell-topbar-status');
    const topStatus = (viewMeta && Array.isArray(viewMeta.topbar_status)) ? viewMeta.topbar_status : [];
    if (statusEl) {
      statusEl.innerHTML = topStatus.map(function (st) {
        if ((st.variant || '') === 'plain') {
          return '<span class="va-topbar-metric" data-state="' + escHtml(st.state || 'nominal') + '">' + escHtml(st.text || '') + '</span>';
        }
        return '<span class="va-pill" data-variant="' + escHtml(st.variant || 'status') + '" data-state="' + escHtml(st.state || 'nominal') + '">' + escHtml(st.text || '') + '</span>';
      }).join('');
    }

    const effNav = (doc.documentElement && doc.documentElement.dataset.effectiveNav) || 'n1';
    const hideTopLinks = effNav === 'n3' && topStatus.length > 0;
    const topLinks = doc.querySelector('#va-shell-topbar .va-shell-topbar-links');
    if (topLinks) {
      topLinks.innerHTML = hideTopLinks ? '' : mapLinks(items, function (lbl, i, href) {
        return '<a class="va-shell-topbar-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '">' + escHtml(lbl) + '</a>';
      });
    }
    const rail = doc.getElementById('va-shell-rail');
    if (rail) {
      rail.innerHTML = '<div class="va-rail-brand"><i class="fa-solid ' + escHtml(icon) + '" aria-hidden="true"></i> <span>' + escHtml(railBrandLbl) + '</span></div>' +
        mapLinks(items, function (lbl, i, href) { return '<a class="va-rail-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '"><i class="fa-solid ' + icons[i % 4] + '" aria-hidden="true"></i> ' + escHtml(lbl) + '</a>'; });
    }
    const dock = doc.getElementById('va-shell-bottomdock');
    if (dock) {
      dock.innerHTML = mapLinks(items.slice(0, 3), function (lbl, i, href) {
        return '<a href="' + href + '"' + (i === 0 ? ' class="is-active"' : '') + '><i class="fa-solid ' + icons[i % 4] + '" aria-hidden="true"></i>' + escHtml(lbl.split(' ')[0]) + '</a>';
      }) + '<button type="button" onclick="openShellDrawer()"><i class="fa-solid fa-bars" aria-hidden="true"></i>Menu</button>';
    }
    const drawerNav = doc.querySelector('#va-shell-drawer .va-drawer-nav');
    if (drawerNav) {
      drawerNav.innerHTML = mapLinks(items, function (lbl, i, href) { return '<a class="va-drawer-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '" onclick="closeShellDrawer()">' + escHtml(lbl) + '</a>'; });
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
      if (iframe.contentWindow.QuietWorlds02To05Runtime) iframe.contentWindow.QuietWorlds02To05Runtime.boot(iframe.contentDocument);
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
    document.documentElement.dataset.studioView = state.studioView;

    document.querySelectorAll('[data-studio-tab]').forEach(function (tab) {
      const active = tab.dataset.studioTab === state.studioView;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
    });

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
        opt.disabled = allowed.indexOf(opt.value) === -1;
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

  function syncExternalMode(iframe) {
    const isBench = state.studioView === 'bench';
    const base = resolveDocsAsset(isBench ? 'bench/evidence-bench.html' : 'diagrams.html');
    const med = state.medium === 'm1' ? 'm1' : 'm2';
    const q = '?embed=1&theme=' + encodeURIComponent(state.theme) + '&density=' + encodeURIComponent(state.density) + '&corners=' + encodeURIComponent(state.corners) + (isBench ? '&medium=' + med : '');
    const doSync = function () {
      const d = getActiveDimensions();
      if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.postExternalSync(iframe, state, d ? d.width : (iframe.clientWidth || window.innerWidth));
    };
    if (iframe.dataset.externalMode !== state.studioView) {
      state.isMounted = false;
      state.renderedView = '';
      iframe.removeAttribute('srcdoc');
      iframe.dataset.externalMode = state.studioView;
      iframe.onload = function () { state.isMounted = true; doSync(); };
      iframe.src = base + q;
      return;
    }
    doSync();
  }

  function applyState(worldChanged) {
    const worldObj = findWorld(state.world);
    if (worldObj && (worldChanged || !findView(worldObj, state.view))) {
      state.view = worldObj.views[0].view_id;
    }
    const viewKey = state.studioView + ':' + state.view + ':' + state.medium;
    if (state.lastViewKey !== viewKey && window.QuietStudioSheetV9) {
      window.QuietStudioSheetV9.untuckStudioBar();
    }
    state.lastViewKey = viewKey;
    const viewMeta = findView(worldObj, state.view);
    const iframe = document.getElementById('va-stage-portal');
    if (!iframe) return;
    updatePortalDimensions();
    if (state.studioView !== 'worlds') {
      syncExternalMode(iframe);
      syncBarControls();
      syncUrlParams();
      return;
    }
    if (!viewMeta) return;
    if (iframe.dataset.externalMode) {
      delete iframe.dataset.externalMode;
      iframe.removeAttribute('src');
      state.isMounted = false;
    }
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
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.openBridgeDialog(worldObj, viewMeta);
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
    const bind = function (id, fn) { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };
    const tablist = document.getElementById('va-studio-mode-tablist');
    if (tablist) {
      tablist.addEventListener('click', function (ev) {
        const btn = ev.target && ev.target.closest ? ev.target.closest('[data-studio-tab]') : null;
        if (btn && ['worlds', 'bench', 'atlas'].indexOf(btn.dataset.studioTab) !== -1) {
          state.studioView = btn.dataset.studioTab;
          applyState(false);
        }
      });
    }
    const wSel = document.getElementById('va-world-select');
    if (wSel) wSel.addEventListener('change', function (e) { state.world = e.target.value; applyState(true); });
    const vSel = document.getElementById('va-view-select');
    if (vSel) vSel.addEventListener('change', function (e) { state.view = e.target.value; applyState(false); });
    ['vp', 'density', 'corners', 'nav'].forEach(function (k) {
      const el = document.getElementById('va-' + k + '-select');
      if (el) el.addEventListener('change', function (e) { state[k] = e.target.value; applyState(false); });
    });
    const onRotate = function () { const d = getActiveDimensions(); if (d) { state.vp = d.height + 'x' + d.width; applyState(false); } };
    const onZoomToggle = function () { state.zoom = (state.zoom === 'fit') ? '1:1' : 'fit'; updatePortalDimensions(); syncBarControls(); syncUrlParams(); };
    [
      ['va-step-prev', function () { stepView(-1); }], ['va-step-next', function () { stepView(1); }],
      ['va-sheet-toggle-btn', function () { state.medium = (state.medium === 'm1') ? 'auto' : 'm1'; applyState(false); }],
      ['va-print-btn', printActiveStage], ['va-bridge-btn', openBridgeDialog],
      ['va-rotate-btn', onRotate], ['va-zoom-btn', onZoomToggle],
      ['va-customize-btn', function () { const s = document.getElementById('va-customize-sheet'); if (s && s.showModal) s.showModal(); }],
    ].forEach(function (pair) { bind(pair[0], pair[1]); });
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.initSheetEvents(state, applyState, onRotate, onZoomToggle, printActiveStage);
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 700 && window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
      updatePortalDimensions();
      if (state.studioView === 'worlds') syncIframeDOM();
    });
    window.QuietPortalResize.initResizeHandles(
      document.getElementById('va-portal-scaler'), document.getElementById('va-stage-portal'), document.getElementById('va-portal-mat'),
      function (w, h) { state.vp = w + 'x' + h; if (state.studioView === 'worlds') syncIframeDOM(); syncUrlParams(); syncBarControls(); }
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
