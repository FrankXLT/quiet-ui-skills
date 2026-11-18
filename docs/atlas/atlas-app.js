/* SPDX-License-Identifier: MIT */
/* Quiet UI Diagrams Atlas — Main Application Controller */

(function() {
  let activeTheme = 'white', activeTab = 'mermaid', activeFilter = 'all', currentCardId = null;

  function initTheme() {
    const params = new URLSearchParams(window.location.search);
    const themeParam = params.get('theme');
    if (['white', 'paper', 'dark-paper', 'dark'].includes(themeParam)) activeTheme = themeParam;
    if (params.get('embed') === '1') document.documentElement.dataset.embed = '1';
    applyTheme(activeTheme, false);
  }

  function applyTheme(theme, updateUrl) {
    activeTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.atlas-swatch-dot').forEach(el => el.classList.toggle('active', el.getAttribute('data-theme') === theme));
    if (updateUrl) {
      const url = new URL(window.location);
      url.searchParams.set('theme', theme);
      window.history.replaceState({}, '', url);
    }
  }

  function goToUiShowcase() {
    window.location.href = './index.html?theme=' + encodeURIComponent(activeTheme);
  }

  function renderWorkbench() {
    const data = window.ATLAS_WORKBENCH_DATA && window.ATLAS_WORKBENCH_DATA[activeTab];
    if (!data) return;
    const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    setT('wb-raw-source', data.source);
    setT('wb-cli-cmd', '$ ' + data.cli);
    setT('wb-ast-extract', data.ast);
    const svgWrap = document.getElementById('wb-svg-render');
    if (svgWrap) svgWrap.innerHTML = data.svg;
    document.querySelectorAll('.wb-tab-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-tab') === activeTab));
  }

  function switchWbTab(tabKey) {
    activeTab = tabKey;
    renderWorkbench();
  }

  function downloadWbSvg() {
    const data = window.ATLAS_WORKBENCH_DATA && window.ATLAS_WORKBENCH_DATA[activeTab];
    if (data) downloadSvgString(data.svg, `${data.typeSlug}-${activeTheme}.svg`);
  }

  function renderCatalog() {
    const catalog = window.ATLAS_CATALOG || [];
    ['systems', 'data', 'flows', 'strategy', 'charts'].forEach(fId => {
      const grid = document.getElementById(`fam-grid-${fId}`);
      if (!grid) return;
      grid.innerHTML = '';
      catalog.filter(it => it.family === fId).forEach(it => {
        const card = document.createElement('article');
        card.className = 'atlas-card';
        card.setAttribute('data-id', it.id);
        card.setAttribute('data-family', it.family);
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Inspect ${it.title} diagram`);
        card.innerHTML = `<div class="atlas-card-thumb">${it.svg}</div><div class="atlas-card-body"><div class="atlas-card-header"><h4 class="atlas-card-title">${it.title}</h4><span class="atlas-card-pattern">${it.pattern}</span></div><p class="atlas-card-desc">${it.desc}</p><div class="atlas-card-footer"><span>${it.familyName}</span><span class="atlas-card-action">Inspect &rarr;</span></div></div>`;
        card.addEventListener('click', () => openAtlasDialog(it.id));
        card.addEventListener('keydown', (e) => { if (e.key === 'Enter') openAtlasDialog(it.id); });
        grid.appendChild(card);
      });
    });
    updateFilter();
  }

  function updateFilter() {
    const searchVal = (document.getElementById('atlas-search')?.value || '').toLowerCase().trim();
    const catalog = window.ATLAS_CATALOG || [];
    let visibleTotal = 0;

    document.querySelectorAll('.atlas-card').forEach(card => {
      const item = catalog.find(i => i.id === card.getAttribute('data-id'));
      if (!item) return;
      const matchesFam = activeFilter === 'all' || item.family === activeFilter;
      const haystack = `${item.id} ${item.title} ${item.familyName} ${item.pattern} ${item.desc} ${item.prompt}`.toLowerCase();
      const isVisible = matchesFam && (!searchVal || haystack.includes(searchVal));
      card.style.display = isVisible ? 'flex' : 'none';
      if (isVisible) visibleTotal++;
    });

    ['systems', 'data', 'flows', 'strategy', 'charts'].forEach(fId => {
      const sec = document.getElementById(`fam-sec-${fId}`);
      if (sec) sec.style.display = sec.querySelectorAll(`.atlas-card[style*="display: flex"]`).length > 0 ? 'block' : 'none';
    });

    const counter = document.getElementById('atlas-counter');
    if (counter) counter.textContent = `Showing ${visibleTotal} of ${catalog.length} visual types`;
  }

  function setFilter(famId) {
    activeFilter = famId;
    document.querySelectorAll('.atlas-pill-btn').forEach(btn => btn.classList.toggle('active', btn.getAttribute('data-family') === famId));
    updateFilter();
  }

  function openAtlasDialog(id) {
    currentCardId = id;
    const item = (window.ATLAS_CATALOG || []).find(i => i.id === id);
    if (!item) return;

    const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    setT('atlas-dialog-title', `${item.title} (${item.id})`);
    setT('atlas-dialog-family', `${item.familyName} · Pattern: ${item.pattern}`);
    setT('atlas-dialog-doc', item.doc);
    setT('atlas-dialog-prompt', item.prompt);
    const svgWrap = document.getElementById('atlas-dialog-svg');
    if (svgWrap) svgWrap.innerHTML = item.svg;

    const dlg = document.getElementById('atlas-inspect-dialog');
    if (dlg) {
      if (typeof dlg.showModal === 'function') dlg.showModal();
      else dlg.setAttribute('open', 'true');
    }
  }

  function closeAtlasDialog() {
    const dlg = document.getElementById('atlas-inspect-dialog');
    if (dlg) {
      if (typeof dlg.close === 'function') dlg.close();
      else dlg.removeAttribute('open');
    }
  }

  function copyDialogPrompt() {
    const promptEl = document.getElementById('atlas-dialog-prompt');
    const btn = document.getElementById('atlas-copy-prompt-btn');
    if (promptEl) {
      navigator.clipboard.writeText(promptEl.textContent).then(() => {
        if (btn) {
          const orig = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(() => { btn.textContent = orig; }, 1800);
        }
      });
    }
  }

  function downloadDialogSvg() {
    const item = (window.ATLAS_CATALOG || []).find(i => i.id === currentCardId);
    if (item) downloadSvgString(item.svg, `${item.id}-${activeTheme}.svg`);
  }

  function downloadSvgString(svgHtml, filename) {
    const style = getComputedStyle(document.documentElement);
    const resolved = svgHtml.replace(/var\((--[a-zA-Z0-9_-]+)(?:,\s*([^)]+))?\)/g, (match, varName, fallback) => {
      const val = style.getPropertyValue(varName).trim();
      return val || (fallback ? fallback.trim() : match);
    });
    const blob = new Blob([resolved], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'diagram.svg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function setupDialogDismiss() {
    const dialog = document.getElementById('atlas-inspect-dialog');
    if (!dialog || ('closedBy' in HTMLDialogElement.prototype)) return;
    dialog.addEventListener('click', (event) => {
      if (event.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (!(r.top <= event.clientY && event.clientY <= r.top + r.height && r.left <= event.clientX && event.clientX <= r.left + r.width)) {
        dialog.close();
      }
    });
  }

  function setupEvents() {
    const searchInput = document.getElementById('atlas-search');
    if (searchInput) searchInput.addEventListener('input', updateFilter);

    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
        e.preventDefault();
        searchInput?.focus();
      }
    });

    const handleFamJump = (val) => {
      setFilter('all');
      if (val === 'all') window.scrollTo({ top: 0, behavior: 'smooth' });
      else if (val === 'workbench') document.getElementById('dsl-workbench')?.scrollIntoView({ behavior: 'smooth' });
      else if (val) document.getElementById(`fam-sec-${val}`)?.scrollIntoView({ behavior: 'smooth' });
    };

    ['atlas-top-family-select', 'atlas-dock-family-select'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', (e) => handleFamJump(e.target.value));
    });

    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'quiet-ui-sync') {
        const d = event.data;
        if (['white', 'paper', 'dark-paper', 'dark'].includes(d.theme)) applyTheme(d.theme, false);
        if (['d1', 'd2', 'd3', 'd4'].includes(d.density)) document.documentElement.setAttribute('data-density', d.density);
        if (['auto', 'sharp', 'subtle', 'rounded', 'soft'].includes(d.corners)) document.documentElement.setAttribute('data-corners', d.corners);
        if (['desktop', 'touch', 'tablet'].includes(d.formFactor)) document.documentElement.setAttribute('data-form-factor', d.formFactor);
        if (d.atlasSection) handleFamJump(d.atlasSection);
      }
    });
  }

  window.applyTheme = applyTheme;
  window.goToUiShowcase = goToUiShowcase;
  window.switchWbTab = switchWbTab;
  window.downloadWbSvg = downloadWbSvg;
  window.setFilter = setFilter;
  window.openAtlasDialog = openAtlasDialog;
  window.closeAtlasDialog = closeAtlasDialog;
  window.copyDialogPrompt = copyDialogPrompt;
  window.downloadDialogSvg = downloadDialogSvg;

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    renderWorkbench();
    renderCatalog();
    setupDialogDismiss();
    setupEvents();
  });
})();
