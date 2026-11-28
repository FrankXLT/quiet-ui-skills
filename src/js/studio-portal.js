/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.8 — Universal Stage Portal Controller (Overview | Examples | Components)
 */
(function (window, document) {
  'use strict';

  const VALID_THEMES = ['white', 'paper', 'dark-paper', 'dark'];
  const state = {
    studioView: 'overview', world: '', view: '', medium: 'auto', theme: 'white',
    nav: 'auto', vp: '1920x1080', zoom: 'fit', density: 'd2', corners: 'auto',
    scale: '100', alarm: '', presetLocked: false, isMounted: false, renderedView: '',
  };
  let manifest = { worlds: [] };

  function escHtml(val) {
    if (window.QuietStudioSheetV9 && window.QuietStudioSheetV9.escHtml) return window.QuietStudioSheetV9.escHtml(val);
    return String(val == null ? '' : val).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function normalizeTheme(val) { const s = String(val || '').trim(); return VALID_THEMES.indexOf(s) !== -1 ? s : null; }
  function readStoredTheme() { try { return normalizeTheme(window.localStorage.getItem('oaw_theme_v99')) || normalizeTheme(window.localStorage.getItem('quiet-ui-site-theme')); } catch (_e) { return null; } }
  function applyTheme(theme) {
    const next = normalizeTheme(theme) || 'white'; state.theme = next;
    document.documentElement.dataset.theme = next;
    const chrome = document.querySelector('.oaw-demo-chrome'); if (chrome) chrome.dataset.theme = next;
    return next;
  }
  function getDefaultStudioView() {
    const v = document.documentElement.dataset.defaultStudioView;
    return (v === 'examples' || v === 'components') ? v : 'overview';
  }
  function loadManifest() {
    const el = document.getElementById('va-v9-manifest');
    if (el) try { manifest = JSON.parse(el.textContent || '{"worlds":[]}'); } catch (_e) {}
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
    const rules = { medium: ['auto', 'm1'], theme: VALID_THEMES, nav: ['auto', 'n0', 'n1', 'n2', 'n3', 'n4'], zoom: ['fit', '1:1'], density: ['d1', 'd2', 'd3', 'd4'], corners: ['auto', 'sharp', 'subtle', 'rounded', 'soft'], alarm: ['nominal', 'approaching', 'unack', 'ack'] };
    const rawMode = (p.get('mode') || '').toLowerCase(), hasViewOrWorld = p.has('view') || p.has('world') || p.has('domain');
    if (rawMode === 'overview') state.studioView = 'overview';
    else if (rawMode === 'components' || rawMode === 'bench' || rawMode === 'atlas') state.studioView = 'components';
    else if (hasViewOrWorld || rawMode === 'examples' || rawMode === 'worlds') state.studioView = 'examples';
    else state.studioView = getDefaultStudioView();

    const urlTheme = normalizeTheme(p.get('theme')), storedTheme = readStoredTheme();
    state.theme = urlTheme || storedTheme || 'white';
    ['medium', 'theme', 'nav', 'zoom', 'density', 'corners', 'alarm'].forEach(function (k) { if (rules[k].indexOf(p.get(k)) !== -1) state[k] = p.get(k); });
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
    if (w) { state.world = w.world_id; const v = findView(w, state.view); if (v) state.view = v.view_id; }
    if (p.has('vp') || urlTheme || p.has('medium') || p.has('nav') || p.has('density') || p.has('corners')) state.presetLocked = true;
    if (hasViewOrWorld && !p.has('vp')) { state.vp = 'fill'; state.presetLocked = true; }
    if (state.studioView === 'examples' && !state.presetLocked && state.view && window.QuietStudioPresetsRailV9) {
      window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state); if (!urlTheme && storedTheme) state.theme = storedTheme;
    }
    applyTheme(state.theme);
  }

  function syncDemoStripLinks() {
    window.dispatchEvent(new CustomEvent('oaw:studio-theme-sync', { detail: { theme: state.theme } }));
    document.querySelectorAll('.oaw-demo-chrome a[data-oaw-route-link], .va-demo-site-strip a[data-oaw-route-link]').forEach(function (link) {
      const raw = (link.getAttribute('href') || '').trim();
      if (!raw || raw.charAt(0) === '#' || raw.indexOf('//') === 0 || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(raw)) return;
      const hi = raw.indexOf('#'), pre = hi >= 0 ? raw.slice(0, hi) : raw, hash = hi >= 0 ? raw.slice(hi) : '';
      const qi = pre.indexOf('?'), path = qi >= 0 ? pre.slice(0, qi) : pre;
      const q = new URLSearchParams(qi >= 0 ? pre.slice(qi + 1) : '');
      q.set('theme', state.theme);
      link.setAttribute('href', path + '?' + q.toString() + hash);
    });
  }

  function syncUrlParams() {
    syncDemoStripLinks();
    if (state.studioView === 'overview') {
      const want = getDefaultStudioView() !== 'overview' ? '?mode=overview' : '';
      if (window.location.search !== want) window.history.replaceState(null, '', window.location.pathname + want);
      return;
    }
    const p = new URLSearchParams();
    p.set('mode', state.studioView);
    if (state.studioView === 'examples') {
      p.set('domain', state.world); p.set('view', state.view); p.set('medium', state.medium); p.set('nav', state.nav); p.set('vp', state.vp);
    }
    p.set('theme', state.theme);
    if (state.zoom !== 'fit') p.set('zoom', state.zoom);
    if (state.density !== 'd2') p.set('density', state.density);
    if (state.corners !== 'auto') p.set('corners', state.corners);
    if (state.scale !== '100') p.set('scale', state.scale);
    if (state.alarm) p.set('alarm', state.alarm);
    window.history.replaceState(null, '', window.location.pathname + '?' + p.toString());
  }

  function resolveDocsAsset(relPath) {
    const path = window.location.pathname || '';
    if (path.indexOf('/customizations/') !== -1) return '../../docs/' + relPath;
    if (path.indexOf('/quiet-ui-showcase') !== -1) return './docs/' + relPath;
    const docsBase = (document.documentElement.dataset.docsBase || '').trim();
    if (docsBase && docsBase.indexOf('__') !== 0) return docsBase === '.' ? './' + relPath : docsBase.replace(/\/+$/, '') + '/' + relPath;
    if (/\/demo(?:\/|$)/.test(path)) return '../' + relPath;
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

  function getActiveDimensions() {
    if (state.studioView === 'components') return null;
    if (window.innerWidth < 760 && !state.presetLocked && state.vp === '1920x1080') return null;
    return window.QuietPortalResize.parseDimensions(state.vp);
  }

  function updatePortalDimensions() {
    const mat = document.getElementById('va-portal-mat'), scaler = document.getElementById('va-portal-scaler'), iframe = document.getElementById('va-stage-portal');
    if (mat && scaler && iframe) window.QuietPortalResize.applyPortalDimensions(scaler, iframe, mat, getActiveDimensions(), state.zoom, state.medium);
  }

  function effectiveMedium(viewMeta) {
    if (state.medium === 'm1') return 'm1';
    return (viewMeta && viewMeta.default_medium) ? viewMeta.default_medium : 'm2';
  }

  function svgIcon(name) {
    return (window.QuietStudioPresetsRailV9 && window.QuietStudioPresetsRailV9.svgIcon) ? window.QuietStudioPresetsRailV9.svgIcon(name) : '';
  }

  function buildIframeSrcDoc(viewMeta) {
    const cssEl = document.getElementById('va-bundled-portal-css'), jsEl = document.getElementById('va-bundled-stage-js');
    const med = effectiveMedium(viewMeta), chrom = (viewMeta && viewMeta.chromatic_code) ? viewMeta.chromatic_code : 'c4';
    const baseHref = window.location.href.split('?')[0].split('#')[0];
    const tokStyle = document.getElementById('custom-tokens'), ovrStyle = document.getElementById('custom-overrides');
    const hasCustom = document.documentElement.dataset.customStyles === 'true';
    const customTok = tokStyle ? '<style>' + tokStyle.textContent + '</style>\n' : (hasCustom ? '<link rel="stylesheet" href="./styles/quiet-ui-tokens.css">\n' : '');
    const customOvr = ovrStyle ? '<style>' + ovrStyle.textContent + '</style>\n' : (hasCustom ? '<link rel="stylesheet" href="./styles/overrides.css">\n' : '');
    return '<!DOCTYPE html>\n<html lang="en" data-theme="' + escHtml(state.theme) +
      '" data-medium="' + escHtml(med) + '" data-chromatic="' + escHtml(chrom) +
      '" data-density="' + escHtml(state.density) + '" data-corners="' + escHtml(state.corners) +
      '" data-world="' + escHtml(state.world) + '" data-view="' + escHtml(state.view) +
      '" data-nav-shell="' + escHtml(state.nav) + '" data-effective-nav="n0" data-form-factor="desktop">\n<head>\n' +
      '<meta charset="utf-8">\n<base href="' + escHtml(baseHref) + '">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' +
      customTok + '<style id="va-portal-styles">\n' + (cssEl ? cssEl.textContent : '') + '\n</style>\n' + customOvr + '</head>\n<body>\n' +
      '<div class="va-app-shell">\n  <header id="va-shell-topbar" class="va-shell-topbar"><a class="va-shell-brand" href="#stage"></a>' +
      '<nav class="va-shell-topbar-links" aria-label="Section Navigation"></nav><div class="va-shell-topbar-status" aria-label="Unit Telemetry Status"></div>' +
      '<button type="button" id="va-drawer-open-btn" class="va-btn-ghost" aria-label="Open Navigation Drawer" onclick="openShellDrawer()">' + svgIcon('bars') + '</button></header>\n' +
      '  <aside id="va-shell-rail" class="va-shell-rail" aria-label="Section Spine"></aside>\n  <main id="va-stage-main" class="va-stage" tabindex="-1"></main>\n' +
      '  <nav id="va-shell-bottomdock" class="va-shell-bottomdock" aria-label="Mobile Dock"></nav>\n' +
      '  <dialog id="va-shell-drawer" closedby="any" aria-label="Navigation Drawer"><div class="va-drawer-header"><strong>View Navigation</strong>' +
      '<button type="button" class="va-btn-ghost" aria-label="Close Drawer" onclick="closeShellDrawer()" autofocus>' + svgIcon('close') + '</button></div><nav class="va-drawer-nav"></nav></dialog>\n' +
      '</div>\n<script>\nwindow.openShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.showModal)d.showModal();};\n' +
      'window.closeShellDrawer=function(){var d=document.getElementById("va-shell-drawer");if(d&&d.close)d.close();};\n' +
      (jsEl ? jsEl.textContent : '') + '\n<\/script>\n</body>\n</html>';
  }

  function syncShellNav(doc, viewMeta) {
    const icon = (viewMeta && viewMeta.nav_icon) ? viewMeta.nav_icon : 'compass';
    const brandLbl = (viewMeta && viewMeta.nav_brand) ? viewMeta.nav_brand : 'Quiet UI';
    const topBrandLbl = (viewMeta && viewMeta.topbar_brand) ? viewMeta.topbar_brand : brandLbl;
    const items = (viewMeta && viewMeta.nav_items) ? viewMeta.nav_items : ['Overview'];
    const anchors = (viewMeta && viewMeta.nav_anchors) ? viewMeta.nav_anchors : [];
    const icons = ['activity', 'layers', 'sliders', 'bell'];
    const hrefFor = function (i) { return anchors[i] ? ('#' + escHtml(anchors[i])) : '#stage'; };
    const mapLinks = function (list, render) { return list.map(function (lbl, i) { return render(lbl, i, hrefFor(i)); }).join(''); };

    const brand = doc.querySelector('#va-shell-topbar .va-shell-brand');
    if (brand) brand.innerHTML = svgIcon(icon) + ' <span>' + escHtml(topBrandLbl) + '</span>';

    const statusEl = doc.querySelector('#va-shell-topbar .va-shell-topbar-status');
    const topStatus = (viewMeta && Array.isArray(viewMeta.topbar_status)) ? viewMeta.topbar_status : [];
    if (statusEl) statusEl.innerHTML = topStatus.map(function (st) {
      return (st.variant || '') === 'plain' ? '<span class="va-topbar-metric" data-state="' + escHtml(st.state || 'nominal') + '">' + escHtml(st.text || '') + '</span>' : '<span class="va-pill" data-variant="' + escHtml(st.variant || 'status') + '" data-state="' + escHtml(st.state || 'nominal') + '">' + escHtml(st.text || '') + '</span>';
    }).join('');
    const effNav = (doc.documentElement && doc.documentElement.dataset.effectiveNav) || 'n1', hideTopLinks = effNav === 'n3' && topStatus.length > 0;
    const topLinks = doc.querySelector('#va-shell-topbar .va-shell-topbar-links');
    if (topLinks) topLinks.innerHTML = hideTopLinks ? '' : mapLinks(items, function (lbl, i, href) { return '<a class="va-shell-topbar-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '">' + escHtml(lbl) + '</a>'; });
    const dock = doc.getElementById('va-shell-bottomdock');
    if (dock) dock.innerHTML = mapLinks(items.slice(0, 3), function (lbl, i, href) { return '<a href="' + href + '"' + (i === 0 ? ' class="is-active"' : '') + '>' + svgIcon(icons[i % 4]) + '<span>' + escHtml(lbl.split(' ')[0]) + '</span></a>'; }) + '<button type="button" onclick="openShellDrawer()">' + svgIcon('bars') + '<span>Menu</span></button>';
    const drawerNav = doc.querySelector('#va-shell-drawer .va-drawer-nav');
    if (drawerNav) drawerNav.innerHTML = mapLinks(items, function (lbl, i, href) { return '<a class="va-drawer-link' + (i === 0 ? ' is-active' : '') + '" href="' + href + '" onclick="closeShellDrawer()">' + escHtml(lbl) + '</a>'; });
    if (window.QuietStudioPresetsRailV9) window.QuietStudioPresetsRailV9.enhanceShellNav(doc, viewMeta, window.QuietStudioPortalV9);
  }

  function syncIframeAttributes() {
    const iframe = document.getElementById('va-stage-portal');
    const worldObj = findWorld(state.world), viewMeta = findView(worldObj, state.view);
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
    docEl.dataset.world = state.world; docEl.dataset.view = state.view;
    docEl.dataset.navShell = state.nav; docEl.dataset.effectiveNav = computeEffectiveNav(state.nav, viewMeta, stageW);
    docEl.dataset.formFactor = stageW <= 480 ? 'touch' : 'desktop';
    if (state.alarm) docEl.dataset.alarmOverride = state.alarm; else delete docEl.dataset.alarmOverride;
    if (state.scale && state.scale !== '100') docEl.style.fontSize = state.scale + '%';
    else docEl.style.removeProperty('font-size');
  }

  function syncIframeDOM() {
    const iframe = document.getElementById('va-stage-portal');
    const worldObj = findWorld(state.world), viewMeta = findView(worldObj, state.view);
    if (!state.isMounted || !iframe || !iframe.contentDocument || !iframe.contentDocument.documentElement || !viewMeta) return;
    syncIframeAttributes();
    const doc = iframe.contentDocument, win = iframe.contentWindow, main = doc.getElementById('va-stage-main');
    if (main && state.renderedView !== state.view) {
      if (win && win.QuietAlarmLifecycle && win.QuietAlarmLifecycle.destroyAll) win.QuietAlarmLifecycle.destroyAll(doc);
      if (win && win.QuietEChartsAdapter && win.QuietEChartsAdapter.disposeAll) win.QuietEChartsAdapter.disposeAll(doc);
      const tpl = document.getElementById('tpl-view-' + state.view);
      main.innerHTML = tpl ? tpl.innerHTML : '<div class="v9-stage-inner">View template not found</div>';
      doc.querySelectorAll('img[data-asset]').forEach(function (img) {
        img.onerror = function () { img.style.display = 'none'; }; img.src = resolveAbsDocsAsset(img.dataset.asset);
      });
      if (win) {
        if (win.QuietEvidenceRuntime) win.QuietEvidenceRuntime.boot();
        if (win.QuietWorld01Runtime) win.QuietWorld01Runtime.boot(doc);
        if (win.QuietWorlds02To05Runtime) win.QuietWorlds02To05Runtime.boot(doc);
        if (win.QuietWorld06Runtime) win.QuietWorld06Runtime.boot(doc);
        if (win.QuietStageRichV9) win.QuietStageRichV9.boot(doc);
      }
      syncShellNav(doc, viewMeta);
      if (win && win.QuietAlarmLifecycle) win.QuietAlarmLifecycle.boot(doc);
      state.renderedView = state.view;
      state.renderedNav = doc.documentElement.dataset.effectiveNav;
      if (win) {
        if (win.QuietEChartsAdapter) win.QuietEChartsAdapter.boot(doc);
        win.scrollTo(0, 0);
      }
      main.scrollTop = 0;
    } else {
      if (doc.documentElement.dataset.effectiveNav !== state.renderedNav) {
        syncShellNav(doc, viewMeta); state.renderedNav = doc.documentElement.dataset.effectiveNav;
        var aHost = doc.querySelector('.va-alarm-console');
        if (win && win.QuietAlarmTrace && aHost && aHost.__vaAlarmInst) win.QuietAlarmTrace.syncBoundUI(aHost, aHost.__vaAlarmInst);
      } else if (window.QuietStudioPresetsRailV9) window.QuietStudioPresetsRailV9.syncRailFooter(doc, state);
      if (win && win.QuietEChartsAdapter) win.QuietEChartsAdapter.refresh(doc);
    }
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.bindPortalScrollTuck(iframe);
  }

  function disposePortalCharts(iframe) {
    try {
      const w = iframe.contentWindow;
      if (w && w.QuietAlarmLifecycle && w.QuietAlarmLifecycle.destroyAll) w.QuietAlarmLifecycle.destroyAll(iframe.contentDocument);
      if (w && w.QuietEChartsAdapter && w.QuietEChartsAdapter.disposeAll) w.QuietEChartsAdapter.disposeAll(iframe.contentDocument);
    } catch (_e) {}
  }

  function syncBarControls() {
    const worldObj = findWorld(state.world), viewMeta = findView(worldObj, state.view);
    applyTheme(state.theme); document.documentElement.dataset.medium = state.medium;
    document.documentElement.dataset.studioView = state.studioView;
    document.querySelectorAll('[data-studio-tab]').forEach(function (tab) { const on = tab.dataset.studioTab === state.studioView; tab.classList.toggle('is-active', on); tab.setAttribute('aria-selected', on ? 'true' : 'false'); });
    const vSel = document.getElementById('va-view-select');
    if (vSel && vSel.dataset.allLoaded !== '1') {
      vSel.innerHTML = (manifest.worlds || []).map(function (w) {
        const num = String(w.world_id || '').slice(0, 2);
        return '<optgroup label="' + escHtml(w.world_label || w.world_id) + '">' + (w.views || []).map(function (v) {
          return '<option value="' + escHtml(v.view_id) + '">' + escHtml((num ? num + ' · ' : '') + String(v.option_label || v.title || v.view_id).replace(' · ', ' — ')) + '</option>';
        }).join('') + '</optgroup>';
      }).join('');
      vSel.dataset.allLoaded = '1';
    }
    if (vSel && state.view && vSel.value !== state.view) vSel.value = state.view;
    const posEl = document.getElementById('va-step-pos');
    if (posEl && window.QuietStudioPresetsRailV9) { const pos = window.QuietStudioPresetsRailV9.getGlobalPosition(manifest, state); posEl.textContent = pos.index + ' / ' + pos.total; }
    const activeFmt = (state.medium === 'm1' || state.vp === '1056x1368') ? 'paper' : (state.vp === '1280x800' ? 'tablet' : (state.vp === '390x844' ? 'mobile' : (state.vp === 'fill' ? 'fill' : (state.vp === '1920x1080' ? '1080p' : ''))));
    document.querySelectorAll('[data-format-preset]').forEach(function (b) { const on = b.dataset.formatPreset === activeFmt; b.classList.toggle('is-active', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    const autoBtn = document.getElementById('va-preset-auto-btn');
    if (autoBtn) autoBtn.hidden = !state.presetLocked;
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.syncSheetControls(state, viewMeta ? viewMeta.allowed_navs : ['n0', 'n1', 'n2', 'n3', 'n4']);
  }

  function syncExternalMode(iframe) {
    const base = resolveDocsAsset('bench/evidence-bench.html');
    const q = '?embed=1&theme=' + encodeURIComponent(state.theme) + '&density=' + encodeURIComponent(state.density) +
      '&corners=' + encodeURIComponent(state.corners) + '&medium=' + (state.medium === 'm1' ? 'm1' : 'm2');
    const doSync = function () {
      const d = getActiveDimensions();
      if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.postExternalSync(iframe, state, d ? d.width : (iframe.clientWidth || window.innerWidth));
    };
    if (iframe.dataset.externalMode !== state.studioView) {
      disposePortalCharts(iframe); state.isMounted = false; state.renderedView = '';
      iframe.removeAttribute('srcdoc'); iframe.dataset.externalMode = state.studioView;
      iframe.onload = function () { state.isMounted = true; doSync(); };
      iframe.src = base + q; return;
    }
    doSync();
  }

  function applyState(worldChanged) {
    const worldObj = findWorld(state.world);
    if (worldObj && (worldChanged || !findView(worldObj, state.view))) state.view = worldObj.views[0].view_id;
    if (worldChanged) state.alarm = '';
    if (worldChanged && !state.presetLocked && window.QuietStudioPresetsRailV9) window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state);
    const viewKey = state.studioView + ':' + state.view + ':' + state.medium;
    if (state.lastViewKey !== viewKey && window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
    state.lastViewKey = viewKey;
    const iframe = document.getElementById('va-stage-portal');
    if (state.studioView === 'overview') {
      if (iframe) { disposePortalCharts(iframe); state.renderedView = ''; }
      syncBarControls(); syncUrlParams(); return;
    }
    if (!iframe) return;
    updatePortalDimensions();
    if (state.studioView === 'components') { syncExternalMode(iframe); syncBarControls(); syncUrlParams(); return; }
    const viewMeta = findView(worldObj, state.view);
    if (!viewMeta) return;
    if (iframe.dataset.externalMode) { disposePortalCharts(iframe); delete iframe.dataset.externalMode; iframe.removeAttribute('src'); state.isMounted = false; }
    if (!state.isMounted || !iframe.contentDocument || !iframe.contentDocument.getElementById('va-stage-main')) {
      state.renderedView = ''; iframe.onload = function () { state.isMounted = true; updatePortalDimensions(); syncIframeDOM(); }; iframe.srcdoc = buildIframeSrcDoc(viewMeta);
    } else syncIframeDOM();
    syncBarControls(); syncUrlParams();
  }
  function openExamples(worldId, viewId) {
    state.studioView = 'examples'; state.alarm = ''; if (worldId) state.world = worldId; if (viewId) state.view = viewId;
    const w = findWorld(state.world); if (w) { state.world = w.world_id; const v = findView(w, state.view); if (v) state.view = v.view_id; }
    state.presetLocked = false; if (window.QuietStudioPresetsRailV9) window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state); applyState(false);
  }

  function openComponents() { state.studioView = 'components'; state.alarm = ''; applyState(false); }
  function openBridgeDialog() {
    const worldObj = findWorld(state.world), viewMeta = findView(worldObj, state.view);
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.openBridgeDialog(worldObj, viewMeta);
  }
  function printActiveStage() { const iframe = document.getElementById('va-stage-portal'); if (iframe && iframe.contentWindow) { iframe.contentWindow.focus(); iframe.contentWindow.print(); } }
  function stepView(delta) {
    state.presetLocked = false; state.alarm = '';
    if (window.QuietStudioPresetsRailV9) {
      window.QuietStudioPresetsRailV9.stepGlobalView(manifest, state, delta);
      window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state);
    }
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
    applyState(false);
  }
  function resetAutoPreset() {
    state.presetLocked = false;
    if (window.QuietStudioPresetsRailV9) window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state);
    applyState(false);
  }

  const FORMAT_PRESETS = {
    '1080p': { vp: '1920x1080', medium: 'auto', zoom: 'fit' }, 'tablet': { vp: '1280x800', medium: 'auto', zoom: 'fit' },
    'paper': { vp: '1056x1368', medium: 'm1', theme: 'paper', zoom: 'fit' }, 'mobile': { vp: '390x844', medium: 'auto', zoom: 'fit' },
    'fill': { vp: 'fill', medium: 'auto' },
  };

  function initSiteThemeListener() {
    window.addEventListener('oaw:theme-change', function (ev) {
      const next = normalizeTheme(ev && ev.detail && ev.detail.theme);
      if (next && state.theme !== next) { state.theme = next; state.presetLocked = true; applyState(false); }
      else if (next) applyTheme(next);
    });
  }

  function initControls() {
    const bind = function (id, ev, fn) { const el = document.getElementById(id); if (el) el.addEventListener(ev, fn); };
    const tablist = document.getElementById('va-studio-mode-tablist');
    if (tablist) tablist.addEventListener('click', function (ev) {
      const btn = ev.target && ev.target.closest ? ev.target.closest('[data-studio-tab]') : null;
      if (!btn) return;
      const m = btn.dataset.studioTab;
      if (m === 'components') return openComponents();
      state.studioView = (m === 'examples') ? 'examples' : 'overview';
      if (m === 'examples' && !state.presetLocked && window.QuietStudioPresetsRailV9) {
        const keepTheme = readStoredTheme(); window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state); if (keepTheme) state.theme = keepTheme;
      }
      applyState(false);
    });
    document.querySelectorAll('[data-format-preset]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const cfg = FORMAT_PRESETS[btn.dataset.formatPreset];
        if (cfg) { state.presetLocked = true; Object.assign(state, cfg); applyState(false); }
      });
    });
    bind('va-view-select', 'change', function (e) {
      const vid = e.target.value;
      const hitW = (manifest.worlds || []).find(function (w) { return (w.views || []).some(function (v) { return v.view_id === vid; }); });
      if (hitW) state.world = hitW.world_id;
      state.view = vid; state.alarm = ''; state.presetLocked = false;
      if (window.QuietStudioPresetsRailV9) window.QuietStudioPresetsRailV9.applyViewPreset(state.view, state);
      applyState(false);
    });
    ['density', 'corners'].forEach(function (k) { bind('va-' + k + '-select', 'change', function (e) { state[k] = e.target.value; state.presetLocked = true; applyState(false); }); });
    const onRotate = function () { const d = getActiveDimensions(); if (d) { state.vp = d.height + 'x' + d.width; state.presetLocked = true; applyState(false); } };
    const onZoom = function () { state.zoom = (state.zoom === 'fit') ? '1:1' : 'fit'; updatePortalDimensions(); syncBarControls(); syncUrlParams(); };
    [['va-step-prev', function () { stepView(-1); }], ['va-step-next', function () { stepView(1); }], ['va-preset-auto-btn', resetAutoPreset],
     ['va-bridge-btn', openBridgeDialog], ['va-customize-btn', function () { const s = document.getElementById('va-customize-sheet'); if (s && s.showModal) s.showModal(); }]
    ].forEach(function (p) { bind(p[0], 'click', p[1]); });
    if (window.QuietStudioSheetV9) window.QuietStudioSheetV9.initSheetEvents(state, applyState, onRotate, onZoom, printActiveStage, resetAutoPreset);
    initSiteThemeListener();
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 700 && window.QuietStudioSheetV9) window.QuietStudioSheetV9.untuckStudioBar();
      if (state.studioView !== 'overview') { updatePortalDimensions(); if (state.studioView === 'examples') syncIframeDOM(); }
    });
    window.QuietPortalResize.initResizeHandles(
      document.getElementById('va-portal-scaler'), document.getElementById('va-stage-portal'), document.getElementById('va-portal-mat'),
      function (w, h) { state.vp = w + 'x' + h; state.presetLocked = true; if (state.studioView === 'examples') syncIframeDOM(); syncUrlParams(); syncBarControls(); }
    );
  }

  window.QuietStudioPortalV9 = { state: state, applyState: applyState, applyTheme: applyTheme, openBridgeDialog: openBridgeDialog, openExamples: openExamples, openComponents: openComponents, stepView: stepView, resetAutoPreset: resetAutoPreset };
  window.addEventListener('DOMContentLoaded', function () {
    loadManifest(); readUrlParams();
    if (window.QuietStudioLandingV9) window.QuietStudioLandingV9.renderLanding(manifest, window.QuietStudioPortalV9);
    initControls(); applyState(false);
    if (!window.echarts) { const s = document.createElement('script'); s.id = 'va-echarts-vendor'; s.src = resolveAbsDocsAsset('assets/vendor/echarts.min.js'); s.onload = function () { if (state.studioView === 'examples') syncIframeDOM(); }; document.head.appendChild(s); }
  });
})(window, document);
