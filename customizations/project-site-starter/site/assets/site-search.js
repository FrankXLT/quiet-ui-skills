/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.8.0 — Lazy Modal Search (This Space + All OAW; zero initial DOM/fetch) */
((window, document) => {
  'use strict';

  const SVG_NS = 'http://www.w3.org/2000/svg', FETCH_TIMEOUT_MS = 3000, MAX_RENDERED = 24;
  const ALLOWED_ORIGINS = new Set(['https://oaworkbench.org', 'https://learn.oaworkbench.org', 'https://projects.oaworkbench.org', 'https://research.oaworkbench.org']);
  const REMOTE_SOURCES = [['', 'Home', 'home'], ['learn.', 'Learn', 'learn'], ['projects.', 'Projects', 'projects'], ['research.', 'Research', 'research']]
    .map(([sub, label, pillar]) => ({ url: `https://${sub}oaworkbench.org/search-index.json`, label, pillar }));
  const manifestCache = new Map(), resolvedResults = new Map();
  const state = {
    dialog: null, input: null, clearBtn: null, closeBtn: null, statusEl: null, resultsEl: null, emptyEl: null,
    emptyMsgEl: null, expandBtn: null, scopeBtns: [], scope: 'space', items: [], rendered: [], activeIdx: 0,
    settledScopes: new Set(), loadingScopes: new Set(), bound: false, openedAsModal: false, closedHandled: false,
    suppressRestoreFocus: false, lastFocus: null,
  };

  const el = (tag, cls, text, attrs) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = String(text);
    if (attrs) for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, String(v));
    return n;
  };
  const svgSearchIcon = () => {
    const svg = document.createElementNS(SVG_NS, 'svg');
    for (const [k, v] of [['width', 16], ['height', 16], ['viewBox', '0 0 16 16'], ['fill', 'none'], ['stroke', 'currentColor'],
      ['stroke-width', '1.6'], ['stroke-linecap', 'round'], ['stroke-linejoin', 'round'], ['aria-hidden', 'true']]) svg.setAttribute(k, String(v));
    const c = document.createElementNS(SVG_NS, 'circle');
    for (const [k, v] of [['cx', '7'], ['cy', '7'], ['r', '4.5'], ['fill', 'none']]) c.setAttribute(k, v);
    const p = document.createElementNS(SVG_NS, 'path'); p.setAttribute('fill', 'none'); p.setAttribute('d', 'M10.5 10.5L14 14');
    svg.append(c, p); return svg;
  };
  const reducedMotion = () => typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isComposingEvent = (ev) => Boolean(ev && (ev.isComposing || ev.keyCode === 229));
  const isDialogOpen = (dlg) => Boolean(dlg && (dlg.open || dlg.hasAttribute('open')));
  const normUrlKey = (u) => u.origin + u.pathname.replace(/\/index\.html$/i, '/') + u.search + u.hash;
  const searchWithoutTheme = (s) => { if (!s) return ''; const p = new URLSearchParams(s); p.delete('theme'); const q = p.toString(); return q ? `?${q}` : ''; };

  function isSafeHref(raw) {
    if (typeof raw !== 'string') return false;
    const s = raw.trim();
    if (!s || /[\u0000-\u001f\u007f]/.test(s) || s.includes('\\') || s.startsWith('//') || s.startsWith('/\\')) return false;
    if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(s)) {
      if (!/^https?:/i.test(s)) return false;
      try { const u = new URL(s); return (u.protocol === 'http:' || u.protocol === 'https:') && !u.username && !u.password; } catch (_e) { return false; }
    }
    return !s.split(/[/?#]/, 1)[0].includes(':');
  }
  const getSearchPrefix = (raw) => { const c = String(raw || './search-index.json').trim().split(/[?#]/)[0], i = c.lastIndexOf('/'); return i >= 0 ? c.slice(0, i + 1) : './'; };
  const normalizeSiteBase = (raw) => {
    if (!isSafeHref(raw) || !/^https?:/i.test(raw.trim())) return null;
    try { const u = new URL(raw.trim()); return { origin: u.origin, pathname: u.pathname.endsWith('/') ? u.pathname : `${u.pathname}/` }; } catch (_e) { return null; }
  };

  function resolveEntryUrl(rawUrl, manifestUrl, meta, siteBase, relPrefix) {
    if (typeof rawUrl !== 'string' || !isSafeHref(rawUrl)) return null;
    const s = rawUrl.trim();
    if (!meta.isLocal || /^https?:/i.test(s)) {
      try {
        const u = new URL(s, manifestUrl);
        if ((u.protocol !== 'http:' && u.protocol !== 'https:') || u.username || u.password) return null;
        if (meta.isLocal && siteBase && u.origin === siteBase.origin &&
            (u.pathname === siteBase.pathname || u.pathname.startsWith(siteBase.pathname) || `${u.pathname}/` === siteBase.pathname)) {
          let sub = `${u.pathname}/` === siteBase.pathname ? '' : u.pathname.slice(siteBase.pathname.length);
          if (!sub || sub.endsWith('/')) sub += 'index.html';
          return { href: `${relPrefix}${sub}${u.search}${u.hash}`, urlKey: normUrlKey(u) };
        }
        return { href: u.href, urlKey: normUrlKey(u) };
      } catch (_e) { return null; }
    }
    if (s.startsWith('#')) return { href: s, urlKey: s };
    let rel = s;
    if (!s.startsWith('/') && !s.startsWith('../')) {
      const parts = (s.startsWith('./') ? s.slice(2) : s).split(/([?#].*)/, 2);
      rel = `${relPrefix}${(!parts[0] || parts[0].endsWith('/')) ? `${parts[0]}index.html` : parts[0]}${parts[1] || ''}`;
    }
    return { href: rel, urlKey: rel.replace(/\/index\.html(?=$|[?#])/i, '/') };
  }

  function getTriggerMeta() {
    const btn = document.getElementById('oaw-search-btn'), rawIdx = btn?.getAttribute('data-search-index') || './search-index.json';
    let localUrl = (isSafeHref(rawIdx) && !/^[a-zA-Z]+:/.test(rawIdx.trim())) ? rawIdx.trim() : './search-index.json';
    if (isSafeHref(rawIdx)) {
      try {
        const p = new URL(rawIdx.trim(), window.location.href);
        if ((p.protocol === 'http:' || p.protocol === 'https:') && (p.origin === window.location.origin || ALLOWED_ORIGINS.has(p.origin))) localUrl = p.href;
      } catch (_e) {}
    }
    const label = document.querySelector('.oaw-projects-label')?.textContent?.trim() || 'This Space';
    return { localSource: { url: localUrl, label, pillar: 'projects', isLocal: true }, relPrefix: getSearchPrefix(rawIdx), siteBase: normalizeSiteBase(btn?.getAttribute('data-site-url') || '') };
  }
  function getScopeSources(scope) {
    const list = [getTriggerMeta().localSource], seen = new Set();
    if (scope === 'all') for (const s of REMOTE_SOURCES) if (ALLOWED_ORIGINS.has(new URL(s.url).origin)) list.push({ ...s, isLocal: false });
    return list.filter((s) => s.url && !seen.has(s.url) && seen.add(s.url));
  }

  function normalizeManifest(payload, manifestUrl, meta, relPrefix, triggerSiteBase) {
    const list = Array.isArray(payload) ? payload : (Array.isArray(payload?.entries) ? payload.entries : (Array.isArray(payload?.items) ? payload.items : []));
    const siteBase = triggerSiteBase || (typeof payload?.site_url === 'string' ? normalizeSiteBase(payload.site_url) : null);
    const rootLabel = (!Array.isArray(payload) && (payload?.project_title || payload?.projectTitle || payload?.project || payload?.title)) || meta.label;
    const out = [];
    for (const e of list) {
      if (!e || typeof e !== 'object') continue;
      const title = String(e.title || e.heading || e.name || e.label || '').trim();
      const resolved = resolveEntryUrl(meta.isLocal ? (e.path || e.href || e.url || '') : (e.url || e.href || e.path || ''), manifestUrl, meta, siteBase, relPrefix);
      if (!title || !resolved) continue;
      const canon = meta.isLocal && typeof e.url === 'string' ? resolveEntryUrl(e.url, manifestUrl, { isLocal: false }, siteBase, relPrefix) : null;
      const summary = String(e.summary || e.description || e.excerpt || e.snippet || '').trim(), cat = String(e.category || e.section || e.group || e.type || '').trim();
      const srcName = meta.isLocal ? rootLabel : (meta.label || String(e.pillar || rootLabel || '').trim());
      const kwList = (Array.isArray(e.keywords) ? e.keywords : (Array.isArray(e.tags) ? e.tags : String(e.keywords || e.tags || '').split(','))).map((k) => String(k || '').trim()).filter(Boolean);
      const badge = meta.isLocal ? (cat || srcName) : (srcName && cat && srcName.toLowerCase() !== cat.toLowerCase() ? `${srcName} · ${cat}` : (srcName || cat));
      out.push({
        title, summary, category: cat, badge, href: resolved.href, sourceKey: meta.url, isLocal: Boolean(meta.isLocal),
        dedupKey: `${(canon || resolved).urlKey}::${title.toLowerCase()}`, titleLow: title.toLowerCase(), catLow: cat.toLowerCase(),
        kwArr: kwList.map((k) => k.toLowerCase()), kwLow: kwList.join(' ').toLowerCase(), summaryLow: summary.toLowerCase(),
        haystack: `${title} ${cat} ${kwList.join(' ')} ${summary} ${srcName}`.toLowerCase(),
      });
    }
    return out;
  }

  function fetchManifest(source, relPrefix, siteBase) {
    if (manifestCache.has(source.url)) return manifestCache.get(source.url);
    if (!source.isLocal) {
      try { if (!ALLOWED_ORIGINS.has(new URL(source.url).origin)) return Promise.resolve({ ok: false, url: source.url, items: [] }); } catch (_e) { return Promise.resolve({ ok: false, url: source.url, items: [] }); }
    }
    let failed = false;
    const task = (async () => {
      let timer = null;
      try {
        let signal;
        if (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function') signal = AbortSignal.timeout(FETCH_TIMEOUT_MS);
        else if (typeof AbortController !== 'undefined') { const c = new AbortController(); signal = c.signal; timer = window.setTimeout(() => c.abort(), FETCH_TIMEOUT_MS); }
        const res = await window.fetch(source.url, { signal, headers: { Accept: 'application/json' } });
        if (!res?.ok) { failed = true; manifestCache.delete(source.url); return { ok: false, url: source.url, items: [] }; }
        return { ok: true, url: source.url, items: normalizeManifest(await res.json(), source.url, source, relPrefix, siteBase) };
      } catch (_err) { failed = true; manifestCache.delete(source.url); return { ok: false, url: source.url, items: [] }; }
      finally { if (timer) window.clearTimeout(timer); }
    })();
    if (!failed) manifestCache.set(source.url, task);
    return task;
  }

  function rebuildScopeItems(scope) {
    const seen = new Set(), merged = [];
    for (const src of getScopeSources(scope)) {
      const res = resolvedResults.get(src.url);
      if (res?.items?.length) for (const it of res.items) if (!seen.has(it.dedupKey) && seen.add(it.dedupKey)) merged.push(it);
    }
    return merged;
  }
  async function loadScope(scope) {
    if (state.settledScopes.has(scope)) { state.items = rebuildScopeItems(scope); renderResults(); return; }
    const meta = getTriggerMeta(), sources = getScopeSources(scope);
    state.loadingScopes.add(scope); renderResults();
    const settled = await Promise.allSettled(sources.map((src) => fetchManifest(src, meta.relPrefix, meta.siteBase).then((result) => {
      resolvedResults.set(src.url, result);
      if (state.scope === scope && (src.isLocal || (result.ok && result.items.length))) { state.items = rebuildScopeItems(scope); renderResults(); }
      return result;
    })));
    state.loadingScopes.delete(scope);
    if (settled.every((r) => r.status === 'fulfilled' && r.value?.ok)) state.settledScopes.add(scope);
    if (state.scope === scope) { state.items = rebuildScopeItems(scope); renderResults(); }
  }

  function curatedDefaultItems(items) {
    if (state.scope !== 'all' || items.length <= MAX_RENDERED) return items.slice(0, MAX_RENDERED);
    const buckets = new Map(), out = [], seen = new Set();
    for (const it of items) { const k = it.isLocal ? '__local__' : it.sourceKey; (buckets.get(k) || buckets.set(k, []).get(k)).push(it); }
    const push = (it) => { if (out.length < MAX_RENDERED && !seen.has(it.dedupKey) && seen.add(it.dedupKey)) out.push(it); };
    (buckets.get('__local__') || []).slice(0, 8).forEach(push);
    buckets.forEach((arr, k) => { if (k !== '__local__') arr.slice(0, 4).forEach(push); });
    items.forEach(push); return out;
  }
  function scoreItems(items, rawQuery) {
    const q = String(rawQuery || '').trim().toLowerCase();
    if (!q) return curatedDefaultItems(items);
    const terms = q.split(/\s+/).filter(Boolean), scored = [];
    for (let i = 0; i < items.length; i += 1) {
      const it = items[i];
      if (!terms.every((t) => it.haystack.includes(t))) continue;
      let score = (it.isLocal ? 10 : 0) + (it.titleLow === q ? 200 : it.titleLow.startsWith(q) ? 120 : it.titleLow.includes(q) ? 80 : 0);
      score += (it.kwArr.includes(q) ? 65 : (it.kwLow.includes(q) ? 35 : 0)) + (it.catLow === q ? 45 : (it.catLow.includes(q) ? 30 : 0)) + (it.summaryLow.includes(q) ? 20 : 0);
      for (const t of terms) score += (it.titleLow.startsWith(t) ? 30 : (it.titleLow.includes(t) ? 20 : 0)) + (it.catLow.includes(t) ? 12 : 0) + (it.kwLow.includes(t) ? 10 : 0) + (it.summaryLow.includes(t) ? 5 : 0);
      scored.push({ item: it, score, idx: i });
    }
    scored.sort((a, b) => (b.score - a.score) || (a.idx - b.idx));
    return scored.map((e) => e.item);
  }

  function syncActiveItem(scrollIntoView) {
    if (!state.resultsEl || !state.input) return;
    const links = state.resultsEl.querySelectorAll('a.oaw-search-item');
    if (!links.length) { state.input.setAttribute('aria-expanded', 'false'); state.input.removeAttribute('aria-activedescendant'); return; }
    state.activeIdx = ((state.activeIdx % links.length) + links.length) % links.length;
    state.input.setAttribute('aria-expanded', 'true');
    links.forEach((l, idx) => { const s = idx === state.activeIdx; l.setAttribute('aria-selected', String(s)); l.classList.toggle('is-selected', s); });
    const active = links[state.activeIdx];
    if (active) { state.input.setAttribute('aria-activedescendant', active.id); if (scrollIntoView && typeof active.scrollIntoView === 'function') active.scrollIntoView({ block: 'nearest' }); }
  }
  function updateStatusText(trimmed, totalMatches, shownCount, loading) {
    const sources = getScopeSources(state.scope), failed = sources.filter((s) => resolvedResults.get(s.url)?.ok === false).length;
    const phrase = state.scope === 'all' ? 'across OAW' : 'in this space';
    if (loading) { state.statusEl.setAttribute('aria-live', 'off'); state.statusEl.textContent = state.scope === 'all' ? 'Loading OAW indexes...' : 'Loading space index...'; return; }
    state.statusEl.setAttribute('aria-live', 'polite');
    const suffix = (state.scope === 'all' && failed > 0) ? ` (${sources.length - failed}/${sources.length} sources, ${failed} offline)` : (state.loadingScopes.has(state.scope) ? ' (syncing...)' : '');
    if (!state.items.length && (state.settledScopes.has(state.scope) || (!state.loadingScopes.has(state.scope) && failed > 0))) { state.statusEl.textContent = `0 matches ${phrase}${suffix || ' (index unavailable)'}`; return; }
    const baseTotal = trimmed ? totalMatches : state.items.length, noun = trimmed ? (baseTotal === 1 ? 'match' : 'matches') : (baseTotal === 1 ? 'entry' : 'entries');
    state.statusEl.textContent = (shownCount < baseTotal ? `Showing ${shownCount} of ${baseTotal} ${noun} ${phrase}` : `${baseTotal} ${noun} ${phrase}`) + suffix;
  }
  function renderResults() {
    if (!state.dialog || !state.resultsEl || !state.statusEl || !state.emptyEl) return;
    const prevKey = state.rendered[state.activeIdx]?.dedupKey || '', trimmed = state.input?.value.trim() || '';
    const matches = scoreItems(state.items, trimmed), visible = matches.slice(0, MAX_RENDERED), loading = state.loadingScopes.has(state.scope) && !state.items.length;
    const keptIdx = prevKey ? visible.findIndex((it) => it.dedupKey === prevKey) : -1;
    state.rendered = visible; state.activeIdx = keptIdx >= 0 ? keptIdx : 0;
    const frag = document.createDocumentFragment();
    visible.forEach((item, idx) => {
      const sel = idx === state.activeIdx, li = el('li', null, null, { role: 'none' });
      const link = el('a', sel ? 'oaw-search-item is-selected' : 'oaw-search-item', null, { id: `oaw-search-opt-${idx}`, role: 'option', href: item.href, 'aria-selected': String(sel) });
      const top = el('div', 'oaw-search-item-top');
      top.appendChild(el('span', 'oaw-search-item-title', item.title));
      if (item.badge) top.appendChild(el('span', 'oaw-search-item-badge', item.badge));
      link.appendChild(top);
      if (item.summary) link.appendChild(el('span', 'oaw-search-item-sub', item.summary));
      li.appendChild(link); frag.appendChild(li);
    });
    state.resultsEl.replaceChildren(frag);
    const hasResults = visible.length > 0;
    state.resultsEl.hidden = !hasResults; state.emptyEl.hidden = hasResults || loading;
    updateStatusText(trimmed, matches.length, visible.length, loading);
    if (!hasResults && !loading && state.emptyMsgEl) {
      const phrase = state.scope === 'all' ? 'across OAW' : 'in this space';
      state.emptyMsgEl.textContent = !state.items.length ? `Search index unavailable ${phrase}.` : (trimmed ? `No results matched "${trimmed}" ${phrase}.` : `No entries available ${phrase}.`);
      if (state.expandBtn) state.expandBtn.hidden = state.scope === 'all';
    }
    syncActiveItem(false);
  }

  function clearQuery(focusInput) {
    if (!state.input) return;
    state.input.value = ''; state.activeIdx = 0; state.clearBtn?.setAttribute('data-empty', 'true');
    renderResults(); if (focusInput) state.input.focus();
  }
  function setScope(nextScope) {
    const scope = nextScope === 'all' ? 'all' : 'space'; state.scope = scope;
    state.scopeBtns.forEach((b) => { const on = b.getAttribute('data-search-scope') === scope; b.setAttribute('aria-pressed', String(on)); b.classList.toggle('is-active', on); });
    state.items = rebuildScopeItems(scope); loadScope(scope);
  }
  function navigateToHref(href) {
    if (!isSafeHref(href)) return;
    let targetUrl; try { targetUrl = new URL(href, window.location.href); } catch (_e) { return; }
    const norm = (p) => String(p || '').replace(/\/index\.html$/i, '/');
    const samePage = targetUrl.origin === window.location.origin && norm(targetUrl.pathname) === norm(window.location.pathname)
      && searchWithoutTheme(targetUrl.search) === searchWithoutTheme(window.location.search) && Boolean(targetUrl.hash);
    if (!samePage) { close(); window.location.assign(targetUrl.href); return; }
    state.suppressRestoreFocus = true; close();
    const hash = targetUrl.hash;
    window.requestAnimationFrame(() => {
      let id = hash.slice(1);
      try { id = decodeURIComponent(id); } catch (_e) {}
      const navEv = new CustomEvent('oaw:docs-navigate', { cancelable: true, detail: { id } });
      const handled = id ? !document.dispatchEvent(navEv) : false;
      if (handled) return;
      const targetEl = id ? document.getElementById(id) : null;
      if (targetEl?.closest?.('[hidden]')) {
        const docsClear = document.getElementById('oaw-docs-search-clear') || document.querySelector('[data-doc-clear], #oaw-empty-clear-btn, [data-empty-clear]');
        if (docsClear && typeof docsClear.click === 'function') docsClear.click();
        for (let h = targetEl.closest('[hidden]'); h; h = targetEl.closest('[hidden]')) { h.hidden = false; h.removeAttribute('hidden'); }
      }
      if (window.location.hash !== hash) { try { window.location.hash = hash; } catch (_e) { window.history.replaceState(null, '', hash); } }
      else window.dispatchEvent(new Event('hashchange'));
      if (targetEl) {
        if (typeof targetEl.scrollIntoView === 'function') targetEl.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'start' });
        if (!targetEl.hasAttribute('tabindex')) targetEl.setAttribute('tabindex', '-1');
        if (typeof targetEl.focus === 'function') targetEl.focus({ preventScroll: true });
      }
    });
  }

  function handleDialogClosed() {
    const dialog = state.dialog;
    if (!dialog || state.closedHandled) return;
    state.closedHandled = true;
    if ('returnValue' in dialog) dialog.returnValue = '';
    const restore = !state.suppressRestoreFocus; state.suppressRestoreFocus = false;
    if (restore) {
      const btn = document.getElementById('oaw-search-btn') || state.lastFocus;
      if (btn && typeof btn.focus === 'function') { try { btn.focus({ preventScroll: true }); } catch (_e) { btn.focus(); } }
    }
    state.lastFocus = null;
  }
  function attachLightDismissFallback(dialog) {
    if (typeof HTMLDialogElement !== 'undefined' && 'closedBy' in HTMLDialogElement.prototype) return;
    const outside = (ev) => { const r = dialog.getBoundingClientRect(); return ev.clientX < r.left || ev.clientX > r.right || ev.clientY < r.top || ev.clientY > r.bottom; };
    let pressedOut = false, sawPointer = false;
    dialog.addEventListener('pointerdown', (ev) => { sawPointer = true; pressedOut = isDialogOpen(dialog) && outside(ev); });
    dialog.addEventListener('pointerup', (ev) => { if (pressedOut && isDialogOpen(dialog) && outside(ev)) close(); pressedOut = false; window.requestAnimationFrame(() => { sawPointer = false; }); });
    dialog.addEventListener('pointercancel', () => { pressedOut = false; sawPointer = false; });
    dialog.addEventListener('click', (ev) => { if (!sawPointer && ev.target === dialog && (ev.clientX !== 0 || ev.clientY !== 0) && outside(ev)) close(); });
  }
  function bindDialogEvents(dialog) {
    dialog.addEventListener('close', handleDialogClosed);
    attachLightDismissFallback(dialog);
    state.clearBtn.addEventListener('click', () => clearQuery(true));
    state.closeBtn.addEventListener('click', close);
    state.scopeBtns.forEach((b) => b.addEventListener('click', () => { setScope(b.getAttribute('data-search-scope')); state.input.focus(); }));
    state.expandBtn.addEventListener('click', () => { setScope('all'); state.input.focus(); });
    state.input.addEventListener('input', () => { state.activeIdx = 0; state.clearBtn.setAttribute('data-empty', state.input.value ? 'false' : 'true'); renderResults(); });
    state.input.addEventListener('keydown', (ev) => {
      if (isComposingEvent(ev)) return;
      if (ev.key === 'Escape') { if (state.input.value) { ev.preventDefault(); ev.stopPropagation(); clearQuery(true); } else if (!state.openedAsModal) { ev.preventDefault(); ev.stopPropagation(); close(); } return; }
      if (!state.rendered.length) return;
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') { ev.preventDefault(); state.activeIdx += ev.key === 'ArrowDown' ? 1 : -1; syncActiveItem(true); }
      else if (ev.key === 'Enter' && state.rendered[state.activeIdx]) { ev.preventDefault(); navigateToHref(state.rendered[state.activeIdx].href); }
    });
    state.resultsEl.addEventListener('focusin', (ev) => {
      const link = ev.target?.closest?.('a.oaw-search-item'), idx = link ? Array.prototype.indexOf.call(state.resultsEl.querySelectorAll('a.oaw-search-item'), link) : -1;
      if (idx >= 0) { state.activeIdx = idx; syncActiveItem(false); }
    });
    state.resultsEl.addEventListener('click', (ev) => {
      const link = (ev.target?.closest ? ev.target : ev.target?.parentElement)?.closest?.('a.oaw-search-item');
      if (!link) return;
      const href = link.getAttribute('href') || '';
      if (!isSafeHref(href)) { ev.preventDefault(); return; }
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button !== 0) { close(); return; }
      ev.preventDefault(); navigateToHref(href);
    });
  }

  function ensureDialog() {
    if (state.dialog) return state.dialog;
    const host = document.querySelector('.oaw-demo-chrome') || document.body;
    if (!host) return null;
    const dialog = el('dialog', 'oaw-search-dialog', null, { id: 'oaw-search-dialog', closedby: 'any', 'aria-labelledby': 'oaw-search-title' });
    const title = el('h2', 'sr-only', 'Search site and documentation', { id: 'oaw-search-title' }), panel = el('div', 'oaw-search-panel');
    const header = el('search', 'oaw-search-header', null, { 'aria-label': 'Site search' }), icon = el('span', 'oaw-search-icon', null, { 'aria-hidden': 'true' });
    icon.appendChild(svgSearchIcon());
    const label = el('label', 'sr-only', 'Search site and documentation', { for: 'oaw-search-input' });
    const input = el('input', 'oaw-search-input', null, {
      id: 'oaw-search-input', type: 'search', autofocus: '', autocomplete: 'off', spellcheck: 'false',
      placeholder: 'Search docs, overview, and OAW...', role: 'combobox', 'aria-autocomplete': 'list', 'aria-expanded': 'false', 'aria-controls': 'oaw-search-results',
    });
    const clearBtn = el('button', 'oaw-search-clear', 'Clear', { type: 'button', id: 'oaw-search-clear', 'aria-label': 'Clear search query', 'data-empty': 'true' });
    const closeBtn = el('button', 'oaw-search-close', 'Esc', { type: 'button', id: 'oaw-search-close', 'aria-label': 'Close search (Esc)' });
    header.append(icon, label, input, clearBtn, closeBtn);
    const toolbar = el('div', 'oaw-search-toolbar'), scopes = el('div', 'oaw-search-scopes', null, { role: 'group', 'aria-label': 'Search scope' });
    const scopeBtns = [['space', 'This Space', true], ['all', 'All OAW', false]].map(([s, txt, on]) => {
      const b = el('button', on ? 'oaw-scope-btn is-active' : 'oaw-scope-btn', txt, { type: 'button', 'data-search-scope': s, 'aria-pressed': String(on) });
      scopes.appendChild(b); return b;
    });
    const statusEl = el('span', 'oaw-search-status', '', { id: 'oaw-search-status', role: 'status', 'aria-live': 'off' }); toolbar.append(scopes, statusEl);
    const body = el('div', 'oaw-search-body'), resultsEl = el('ul', 'oaw-search-results', null, { id: 'oaw-search-results', role: 'listbox', 'aria-label': 'Search results' });
    const emptyEl = el('div', 'oaw-search-empty', null, { id: 'oaw-search-empty', hidden: '' }), emptyMsgEl = el('p', 'oaw-search-empty-msg', '', { id: 'oaw-search-empty-msg' });
    const expandBtn = el('button', 'oaw-search-empty-btn', 'Search All OAW', { type: 'button', id: 'oaw-search-expand-btn', hidden: '' });
    emptyEl.append(emptyMsgEl, expandBtn); body.append(resultsEl, emptyEl);
    const footer = el('div', 'oaw-search-footer');
    for (const [keys, desc] of [[['↑', '↓'], 'navigate'], [['Enter'], 'open'], [['Esc'], 'close']]) {
      const hint = el('span', 'oaw-search-hint'); keys.forEach((k) => hint.appendChild(el('kbd', null, k)));
      hint.appendChild(document.createTextNode(` ${desc}`)); footer.appendChild(hint);
    }
    panel.append(header, toolbar, body, footer); dialog.append(title, panel); host.appendChild(dialog);
    Object.assign(state, { dialog, input, clearBtn, closeBtn, statusEl, resultsEl, emptyEl, emptyMsgEl, expandBtn, scopeBtns });
    bindDialogEvents(dialog); return dialog;
  }

  function closeOpenPopovers() {
    try { document.querySelectorAll('[popover]:popover-open').forEach((p) => { try { p.hidePopover?.(); } catch (_e) {} }); } catch (_e) {}
    const hasPop = typeof HTMLElement !== 'undefined' && 'showPopover' in HTMLElement.prototype;
    document.querySelectorAll('.oaw-popover[data-open="true"], .oaw-popover.is-open, .oaw-route-menu.is-open').forEach((p) => {
      p.removeAttribute('data-open'); p.classList.remove('is-open');
      if (!hasPop || !p.hasAttribute('popover')) p.hidden = true;
      if (p.id) document.querySelector(`[aria-controls="${p.id}"]`)?.setAttribute('aria-expanded', 'false');
    });
  }
  function open(opts) {
    closeOpenPopovers();
    const dialog = ensureDialog();
    if (!dialog) return;
    state.lastFocus = document.activeElement; state.closedHandled = false; state.suppressRestoreFocus = false;
    if (opts && (opts.scope === 'all' || opts.scope === 'space')) state.scope = opts.scope;
    if (!isDialogOpen(dialog)) {
      state.openedAsModal = false;
      if (typeof dialog.showModal === 'function') { try { dialog.showModal(); state.openedAsModal = true; } catch (_e) { dialog.setAttribute('open', ''); } }
      else dialog.setAttribute('open', '');
    }
    if (typeof opts?.query === 'string') { state.input.value = opts.query; state.activeIdx = 0; }
    state.clearBtn.setAttribute('data-empty', state.input.value ? 'false' : 'true'); setScope(state.scope);
    try { state.input.focus(); } catch (_e) {}
    window.requestAnimationFrame(() => { if (isDialogOpen(dialog) && state.input) { state.input.focus(); if (state.input.value) state.input.select(); } });
  }
  function close() {
    const dialog = state.dialog;
    if (!dialog) return;
    if (isDialogOpen(dialog)) {
      if (typeof dialog.close === 'function' && state.openedAsModal) { try { dialog.close(); } catch (_e) { dialog.removeAttribute('open'); } }
      else dialog.removeAttribute('open');
      if (isDialogOpen(dialog)) dialog.removeAttribute('open');
    }
    if ('returnValue' in dialog) dialog.returnValue = '';
    if (!state.openedAsModal || typeof dialog.close !== 'function') handleDialogClosed();
    else window.setTimeout(() => { if (!state.closedHandled && !isDialogOpen(dialog)) handleDialogClosed(); }, 0);
  }
  function isEditableNode(n) {
    if (!n || n.nodeType !== 1) return false;
    if (n.isContentEditable) return true;
    if (typeof n.closest !== 'function') return false;
    const ce = n.closest('[contenteditable]');
    return Boolean(n.closest('input, textarea, select') || (ce && ce.getAttribute('contenteditable') !== 'false'));
  }
  function init() {
    if (state.bound) return; state.bound = true;
    document.addEventListener('click', (ev) => {
      if (ev.defaultPrevented) return;
      const t = ev.target?.closest ? ev.target : ev.target?.parentElement;
      if (t?.closest?.('#oaw-search-btn')) { ev.preventDefault(); open(); }
    });
    document.addEventListener('keydown', (ev) => {
      if (ev.defaultPrevented || isComposingEvent(ev)) return;
      if ((ev.ctrlKey || ev.metaKey) && !ev.altKey && !ev.shiftKey && String(ev.key || '').toLowerCase() === 'k') {
        if (isDialogOpen(state.dialog)) { ev.preventDefault(); close(); } else if (!document.querySelector('dialog[open]')) { ev.preventDefault(); open(); }
      } else if (ev.key === '/' && !ev.ctrlKey && !ev.metaKey && !ev.altKey && !document.getElementById('oaw-docs-search') && !document.querySelector('dialog[open]')) {
        if (!isEditableNode(document.activeElement) && !isEditableNode(ev.target)) { ev.preventDefault(); open(); }
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true }); else init();
  window.OawSiteSearch = { open, close };
})(window, document);
