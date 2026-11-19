/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 — Two-Axis Universal Stage Portal Controller (World × Distilled View)
 */
(function (window, document) {
  'use strict';

  const state = {
    studioView: 'examples', world: '', view: '', medium: 'auto', theme: 'white',
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
      medium: ['auto', 'm1'],
      theme: ['white', 'paper', 'dark-paper', 'dark'],
      nav: ['auto', 'n0', 'n1', 'n2', 'n3', 'n4'],
      zoom: ['fit', '1:1'],
      density: ['d1', 'd2', 'd3', 'd4'],
      corners: ['auto', 'sharp', 'subtle', 'rounded', 'soft'],
    };
    const rawMode = (p.get('mode') || '').toLowerCase();
    if (rawMode === 'examples' || rawMode === 'worlds') state.studioView = 'examples';
    else if (rawMode === 'components' || rawMode === 'bench' || rawMode === 'atlas') state.studioView = 'components';
    ['medium', 'theme', 'nav', 'zoom', 'density', 'corners'].forEach(function (k) {
      if (rules[k].indexOf(p.get(k)) !== -1) state[k] = p.get(k);
    });
    const vp = p.get('vp') || '';
    if (vp === 'fill' || /^\d{3,4}x\d{3,4}$/.test(vp)) state.vp = vp;
    const sc = parseInt(p.get('scale') || '', 10);
    if (!isNaN(sc)) state.scale = String(Math.max(75, Math.min(150, sc)));
    if (p.has('domain')) state.world = p.get('domain') || '';
    else if (p.has('world')) state.world = p.get('world') || '';
    if (p.has('view')) state.view = p.get('view') || '';
    if (!state.world && state.view) {
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
    if (state.studioView !== 'examples') p.set('mode', state.studioView);
    p.set('domain', state.world);
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
    if (path.indexOf('/pilot/') !== -1 || path.indexOf('/v9/') !== -1) return '../' + relPath;
    if (path.indexOf('/quiet-ui-showcase') !== -1) return './docs/' + relPath;
    return './' + relPath;
  }

  function resolveAbsDocsAsset(relPath) {
    try { return new URL(resolveDocsAsset(relPath), window.location.href).href; } catch (_e) { return resolveDocsAsset(relPath); }
  }

  function computeEffectiveNav(nav, viewMeta, width) {
    const allowed = (viewMeta && viewMeta.allowed_navs) ? viewMeta.allowed_navs : ['n0', 'n1', 'n2', 'n3', 'n4'];
    const defNav = (viewMeta && viewMeta.default_nav) ? viewMeta.default_nav : (allowed[0] || 'n0');
    if (nav && nav !== 'auto') {
      if (nav === 'n4' && width >= 700) return defNav;
      return allowed.indexOf(nav) !== -1 ? nav : defNav;
    }
    return (width < 700 && allowed.indexOf('n4') !== -1) ? 'n4' : defNav;
  }

  function getActiveDimensions() { return window.QuietPortalResize.parseDimensions(state.vp); }

  function updatePortalDimensions() {
    const mat = document.getElementById('va-portal-mat'), scaler = document.getElementById('va-portal-scaler'), iframe = document.getElementById('va-stage-portal');
    if (mat && scaler && iframe) window.QuietPortalResize.applyPortalDimensions(scaler, iframe, mat, getActiveDimensions(), state.zoom);
  }

  function effectiveMedium(viewMeta) {
    if (state.medium === 'm1') return 'm1';
    return (viewMeta && viewMeta.default_medium) ? viewMeta.default_medium : 'm2';
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
    'glasses': '<circle cx="5" cy="9" r="2.5"/><circle cx="11" cy="9" r="2.5"/><path d="M7.5 9h1M2.5 9 4 4.5M13.5 9 12 4.5" fill="none"/>', 'home': '<path d="M2.5 7.5 8 2.5l5.5 5v6H10V9.5H6v4H2.5z" fill="none"/>', 'frame': '<rect x="2" y="3" width="12" height="10" rx="1"/><path d="M4.5 10.5 7 7.5l2 2 1.5-1.5 2 2.5" fill="none"/>',
  };
  function svgIcon(name) {
    const body = NAV_ICONS[name] || NAV_ICONS.compass;
    return '<svg class="va-icon" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style="flex:none" aria-hidden="true">' + body + '</svg>';
  }

  function buildIframeSrcDoc(viewMeta) {
    const cssEl = document.getElementById('va-bundled-portal-css');
    const jsEl = document.getElementById('va-bundled-stage-js');
    const med = effectiveMedium(viewMeta);
    const chrom = (viewMeta && viewMeta.chromatic_code) ? viewMeta.chromatic_code : 'c4';
    const baseHref = window.location.href.split('?')[0].split('#')[0];
    const tokStyle = document.getElementById('custom-tokens');
    const ovrStyle = document.getElementById('custom-overrides');
    const hasCustom = document.documentElement.dataset.customStyles === 'true';
    const customTok = tokStyle ? '<style>' + tokStyle.textContent + '</style>\n' : (hasCustom ? '<link rel="stylesheet" href="./styles/quiet-ui-tokens.css">\n' : '');
    const customOvr = ovrStyle ? '<style>' + ovrStyle.textContent + '</style>\n' : (hasCustom ? '<link rel="stylesheet" href="./styles/overrides.css">\n' : '');
    return '<!DOCTYPE html>\n<html lang="en" data-theme="' + escHtml(state.theme) +
      '" data-medium="' + escHtml(med) + '" data-chromatic="' + escHtml(chrom) +
      '" data-density="' + escHtml(state.density) + '" data-corners="' + escHtml(state.corners) +
      '" data-world="' + escHtml(state.world) + '" data-view="' + escHtml(state.view) +
      '" data-nav-shell="' + escHtml(state.nav) + '" data-effective-nav="n0" data-form-factor="desktop">\n<head>\n' +
      '<meta charset="utf-8">\n<base href="' + escHtml(baseHref) + '">\n' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">\n' +
      customTok +
      '<style id="va-portal-styles">\n' + (cssEl ? cssEl.textContent : '') + '\n</style>\n' + customOvr + '</head>\n<body>\n' +
      '<div class="va-app-shell">\n' +
      '  <header id="va-shell-topbar" class="va-shell-topbar"><a class="va-shell-brand" href="#stage"></a>' +
      '<nav class="va-shell-topbar-links" aria-label="Section Navigation"></nav>' +
      '<div class="va-shell-topbar-status" aria-label="Unit Telemetry Status"></div>' +
      '<button type="button" id="va-drawer-open-btn" class="va-btn-ghost" aria-label="Open Navigation Drawer" onclick="openShellDrawer()">' +
      svgIcon('bars') + '</button></header>\n' +
      '  <aside id="va-shell-rail" class="va-shell-rail" aria-label="Section Spine"></aside>\n' +
      '  <main id="va-stage-main" class="va-stage" tabindex="-1"></main>\n' +
      '  <nav id="va-shell-bottomdock" class="va-shell-bottomdock" aria-label="Mobile Dock"></nav>\n' +
      '  <dialog id="va-shell-drawer" closedby="any" aria-label="Navigation Drawer">' +
      '<div class="va-drawer-header"><strong>View Navigation</strong>' +
      '<button type="button" class="va-btn-ghost" aria-label="Close Drawer" onclick="closeShellDrawer()" autofocus>' + svgIcon('close') + '</button></div>' +
      '<nav class="va-drawer-nav"></nav></dialog>\n' +
      '</div>\n<script>\n' +
      'window.openShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.showModal)d.showModal();};\n' +
      'window.closeShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.close)d.close();};\n' +
      (jsEl ? jsEl.textContent : '') + '\n<\/script>\n</body>\n</html>';
  }

  function syncShellNav(doc, viewMeta) {
    const icon = (viewMeta && viewMeta.nav_icon) ? viewMeta.nav_icon : 'compass';
    const brandLbl = (viewMeta && viewMeta.nav_brand) ? viewMeta.nav_brand : 'Quiet UI';
    const topBrandLbl = (viewMeta && viewMeta.topbar_brand) ? viewMeta.topbar_brand : brandLbl;
    const railBrandLbl = (viewMeta && viewMeta.rail_brand) ? viewMeta.rail_brand : brandLbl;
    const items = (viewMeta && viewMeta.nav_items) ? viewMeta.nav_items : ['Overview'];
    const anchors = (viewMeta && viewMeta.nav_anchors) ? viewMeta.nav_anchors : [];
    const icons = ['activity', 'layers', 'sliders', 'bell'];
    const hrefFor = function (i) { return anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage'; };
    const mapLinks = function (list, render) { return list.map(function (lbl, i) { return render(lbl, i, hrefFor(i)); }).join(''); };

    const brand = doc.querySelector('#va-shell-topbar .va-shell-brand');
    if (brand) brand.innerHTML = svgIcon(icon) + ' <span>' + escHtml(topBrandLbl) + '</span>';

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
      rail.innerHTML = '<div class="va-rail-brand">' + svgIcon(icon) + ' <span>' + escHtml(railBrandLbl) + '</span></div>' +
        mapLinks(items, function (lbl, i, href) { return '<a class="va-rail-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '">' + svgIcon(icons[i % 4]) + ' <span>' + escHtml(lbl) + '</span></a>'; });
    }
    const dock = doc.getElementById('va-shell-bottomdock');
    if (dock) {
      dock.innerHTML = mapLinks(items.slice(0, 3), function (lbl, i, href) {
        return '<a href="' + href + '"' + (i === 0 ? ' class="is-active"' : '') + '>' + svgIcon(icons[i % 4]) + '<span>' + escHtml(lbl.split(' ')[0]) + '</span></a>';
      }) + '<button type="button" onclick="openShellDrawer()">' + svgIcon('bars') + '<span>Menu</span></button>';
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
    if (!state.isMounted || !iframe || !iframe.contentDocument || !iframe.contentDocument.documentElement || !viewMeta) return;
    syncIframeAttributes();
    const doc = iframe.contentDocument;
    const win = iframe.contentWindow;
    const main = doc.getElementById('va-stage-main');
    if (main && state.renderedView !== state.view) {
      if (win && win.QuietEChartsAdapter && win.QuietEChartsAdapter.disposeAll) win.QuietEChartsAdapter.disposeAll(doc);
      const tpl = document.getElementById('tpl-view-' + state.view);
      main.innerHTML = tpl ? tpl.innerHTML : '<div class="v9-stage-inner">View template not found</div>';
      doc.querySelectorAll('img[data-asset]').forEach(function (img) {
        img.onerror = function () { img.style.display = 'none'; }; img.src = resolveAbsDocsAsset(img.dataset.asset);
      });
      syncShellNav(doc, viewMeta);
      state.renderedView = state.view;
      state.renderedNav = doc.documentElement.dataset.effectiveNav;
      if (win) {
        if (win.QuietEvidenceRuntime) win.QuietEvidenceRuntime.boot();
        if (win.QuietWorld01Runtime) win.QuietWorld01Runtime.boot(doc); if (win.QuietWorlds02To05Runtime) win.QuietWorlds02To05Runtime.boot(doc);
        if (win.QuietWorld06Runtime) win.QuietWorld06Runtime.boot(doc); if (win.QuietEChartsAdapter) win.QuietEChartsAdapter.boot(doc);
        win.scrollTo(0, 0);
      }
      main.scrollTop = 0;
    } else {
      if (doc.documentElement.dataset.effectiveNav !== state.renderedNav) { syncShellNav(doc, viewMeta); state.renderedNav = doc.documentElement.dataset.effectiveNav; }
      if (win && win.QuietEChartsAdapter) win.QuietEChartsAdapter.refresh(doc);
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

    const dSel = document.getElementById('va-domain-select');
    if (dSel && dSel.value !== state.world) dSel.value = state.world;

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

    const allowed = viewMeta ? viewMeta.allowed_navs : ['n0', 'n1', 'n2', 'n3', 'n4'];
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.syncSheetControls(state, allowed);
  }

  function syncExternalMode(iframe) {
    const base = resolveDocsAsset('bench/evidence-bench.html');
    const med = state.medium === 'm1' ? 'm1' : 'm2';
    const q = '?embed=1&theme=' + encodeURIComponent(state.theme) + '&density=' + encodeURIComponent(state.density) +
      '&corners=' + encodeURIComponent(state.corners) + '&medium=' + med;
    const doSync = function () {
      const d = getActiveDimensions();
      if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.postExternalSync(iframe, state, d ? d.width : (iframe.clientWidth || window.innerWidth));
    };
    if (iframe.dataset.externalMode !== state.studioView) {
      try { if (iframe.contentWindow && iframe.contentWindow.QuietEChartsAdapter && iframe.contentWindow.QuietEChartsAdapter.disposeAll) iframe.contentWindow.QuietEChartsAdapter.disposeAll(iframe.contentDocument); } catch (_e) {}
      state.isMounted = false; state.renderedView = '';
      iframe.removeAttribute('srcdoc'); iframe.dataset.externalMode = state.studioView;
      iframe.onload = function () { state.isMounted = true; doSync(); };
      iframe.src = base + q;
      return;
    }
    doSync();
  }

  function applyState(worldChanged) {
    const worldObj = findWorld(state.world);
    if (worldObj && (worldChanged || !findView(worldObj, state.view))) state.view = worldObj.views[0].view_id;
    const viewKey = state.studioView + ':' + state.view + ':' + state.medium;
    if (state.lastViewKey !== viewKey && window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
    state.lastViewKey = viewKey;
    const viewMeta = findView(worldObj, state.view);
    const iframe = document.getElementById('va-stage-portal');
    if (!iframe) return;
    updatePortalDimensions();
    if (state.studioView !== 'examples') {
      syncExternalMode(iframe); syncBarControls(); syncUrlParams();
      return;
    }
    if (!viewMeta) return;
    if (iframe.dataset.externalMode) {
      try { if (iframe.contentWindow && iframe.contentWindow.QuietEChartsAdapter && iframe.contentWindow.QuietEChartsAdapter.disposeAll) iframe.contentWindow.QuietEChartsAdapter.disposeAll(iframe.contentDocument); } catch (_e) {}
      delete iframe.dataset.externalMode; iframe.removeAttribute('src'); state.isMounted = false;
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
    if (iframe && iframe.contentWindow) { iframe.contentWindow.focus(); iframe.contentWindow.print(); }
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
        if (btn && ['examples', 'components'].indexOf(btn.dataset.studioTab) !== -1) {
          state.studioView = btn.dataset.studioTab;
          applyState(false);
        }
      });
    }
    const dSel = document.getElementById('va-domain-select');
    if (dSel) dSel.addEventListener('change', function (e) { state.world = e.target.value; applyState(true); });
    const vSel = document.getElementById('va-view-select');
    if (vSel) vSel.addEventListener('change', function (e) { state.view = e.target.value; applyState(false); });
    ['density', 'corners'].forEach(function (k) {
      const el = document.getElementById('va-' + k + '-select');
      if (el) el.addEventListener('change', function (e) { state[k] = e.target.value; applyState(false); });
    });
    const onRotate = function () { const d = getActiveDimensions(); if (d) { state.vp = d.height + 'x' + d.width; applyState(false); } };
    const onZoomToggle = function () { state.zoom = (state.zoom === 'fit') ? '1:1' : 'fit'; updatePortalDimensions(); syncBarControls(); syncUrlParams(); };
    [
      ['va-step-prev', function () { stepView(-1); }], ['va-step-next', function () { stepView(1); }],
      ['va-bridge-btn', openBridgeDialog],
      ['va-customize-btn', function () { const s = document.getElementById('va-customize-sheet'); if (s && s.showModal) s.showModal(); }],
    ].forEach(function (pair) { bind(pair[0], pair[1]); });
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.initSheetEvents(state, applyState, onRotate, onZoomToggle, printActiveStage);
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 700 && window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
      updatePortalDimensions();
      if (state.studioView === 'examples') syncIframeDOM();
    });
    window.QuietPortalResize.initResizeHandles(
      document.getElementById('va-portal-scaler'), document.getElementById('va-stage-portal'), document.getElementById('va-portal-mat'),
      function (w, h) { state.vp = w + 'x' + h; if (state.studioView === 'examples') syncIframeDOM(); syncUrlParams(); syncBarControls(); }
    );
  }

  window.addEventListener('DOMContentLoaded', function () {
    loadManifest(); readUrlParams(); initControls(); applyState(false);
    if (!window.echarts) { const s = document.createElement('script'); s.id = 'va-echarts-vendor'; s.src = resolveAbsDocsAsset('assets/vendor/echarts.min.js'); s.onload = function () { if (state.studioView === 'examples') syncIframeDOM(); }; document.head.appendChild(s); }
  });
  window.QuietStudioPortalV9 = { state: state, applyState: applyState, openBridgeDialog: openBridgeDialog };
})(window, document);
