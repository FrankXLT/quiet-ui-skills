/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.8.0 — Route 3 Docs Search, Active Chapter Sync, Quick Jumps & Mobile TOC Sheet
 */
(function (window, document) {
  'use strict';

  const TOC_NAV_SEL = '.oaw-docs-rail a[href^="#"], .oaw-docs-rail a[data-doc-jump], .oaw-docs-toc-list a[href^="#"], .oaw-docs-toc-list a[data-doc-jump]';
  const EMPTY_CLEAR_SEL = '#oaw-empty-clear-btn, [data-empty-clear], [data-doc-clear]';
  const TOC_CLOSE_SEL = '[data-close-dialog], [data-toc-close], .va-modal-sheet-hdr button, button[aria-label*="close" i]';
  const isDialogOpen = function (d) { return Boolean(d && (d.open || d.hasAttribute('open'))); };
  const prefersReducedMotion = function () { return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches; };
  const formatCountText = function (v, t) { return v === 0 ? '0 matching sections' : String(v) + ' of ' + String(t) + (t === 1 ? ' guide' : ' guides'); };

  function parseSearchIndex() {
    const el = document.getElementById('oaw-docs-search-index');
    if (!el) return [];
    try { const p = JSON.parse(el.textContent || '[]'); return Array.isArray(p) ? p : []; } catch (_e) { return []; }
  }

  function resolveInPageTargetId(el) {
    if (!el || typeof el.getAttribute !== 'function') return null;
    const raw = (el.getAttribute('data-doc-target') || el.getAttribute('data-doc-jump') || el.getAttribute('href') || '').trim();
    if (!raw) return null;
    return raw.startsWith('#') ? (raw.slice(1) || null) : (/^[a-zA-Z0-9_-]+$/.test(raw) ? raw : null);
  }

  function resolveChapterTitle(secEl, tocLinks) {
    if (secEl.id) {
      const m = tocLinks.find(function (l) { return !l.classList.contains('oaw-docs-sub') && resolveInPageTargetId(l) === secEl.id; });
      if (m && m.textContent && m.textContent.trim()) return m.textContent.trim();
    }
    const attr = (secEl.getAttribute('data-chapter-title') || secEl.getAttribute('data-title') || '').trim();
    if (attr) return attr;
    const h = secEl.querySelector('h1, h2');
    return h && h.textContent ? h.textContent.trim() : (secEl.id || '');
  }

  function buildSectionModel() {
    const tocLinks = Array.from(document.querySelectorAll(TOC_NAV_SEL));
    const sections = Array.from(document.querySelectorAll('.oaw-docs-section, .oaw-doc-section'));
    const byId = new Map(), byDocKey = new Map();
    const entries = sections.map(function (el) {
      const entry = { el: el, title: resolveChapterTitle(el, tocLinks), texts: [] };
      if (el.id) { byId.set(el.id, entry); byDocKey.set(el.id.startsWith('doc-') ? el.id.slice(4) : el.id, entry); }
      if (el.dataset && el.dataset.docId) byDocKey.set(el.dataset.docId, entry);
      return entry;
    });
    parseSearchIndex().forEach(function (rec) {
      if (!rec || typeof rec !== 'object') return;
      const haystack = [rec.title, rec.category, rec.heading, rec.text].filter(Boolean).join(' ').toLowerCase();
      if (!haystack) return;
      let target = rec.doc_id && byDocKey.has(String(rec.doc_id)) ? byDocKey.get(String(rec.doc_id))
        : (rec.id && byId.has(String(rec.id)) ? byId.get(String(rec.id)) : null);
      if (!target && rec.id) { const n = document.getElementById(String(rec.id)); if (n) target = entries.find(function (e) { return e.el.contains(n); }) || null; }
      if (target) target.texts.push(haystack);
    });
    entries.forEach(function (e) { if (e.texts.length === 0) e.texts.push((e.el.textContent || '').toLowerCase()); });
    return entries;
  }

  function isEditableElement(el) {
    if (!el) return false;
    const tag = (el.tagName || '').toUpperCase();
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || Boolean(el.isContentEditable);
  }

  function hasOpenPopover() {
    try { if (document.querySelector('[popover]:popover-open')) return true; } catch (_e) {}
    return Boolean(document.querySelector('.oaw-popover[data-open="true"], .oaw-popover.is-open, #oaw-route-menu.is-open, #oaw-route-menu[data-open="true"]'));
  }

  function bindDialogLightDismiss(dialog, closeFn, isModalFn) {
    if (!dialog) return;
    const supportsClosedBy = typeof HTMLDialogElement !== 'undefined' && 'closedBy' in HTMLDialogElement.prototype;
    let pressedOutside = false, sawPointer = false;
    const isOutside = function (ev) { const r = dialog.getBoundingClientRect(); return ev.clientX < r.left || ev.clientX > r.right || ev.clientY < r.top || ev.clientY > r.bottom; };
    dialog.addEventListener('pointerdown', function (ev) { sawPointer = true; pressedOutside = isDialogOpen(dialog) && isOutside(ev); });
    dialog.addEventListener('pointerup', function (ev) {
      if (pressedOutside && isDialogOpen(dialog) && isOutside(ev) && (!supportsClosedBy || !isModalFn() || !ev.isTrusted)) closeFn(true);
      pressedOutside = false;
      window.requestAnimationFrame(function () { sawPointer = false; });
    });
    dialog.addEventListener('pointercancel', function () { pressedOutside = false; sawPointer = false; });
    dialog.addEventListener('click', function (ev) { if (!sawPointer && ev.target === dialog && (ev.clientX !== 0 || ev.clientY !== 0) && isOutside(ev)) closeFn(true); });
  }

  function bindTocDialog(tocTrigger, tocDialog, resetSearch) {
    const state = { openedAsModal: false };
    const cleanupClosed = function () {
      tocDialog.classList.remove('is-open');
      if ('returnValue' in tocDialog) tocDialog.returnValue = '';
      state.openedAsModal = false;
      if (tocTrigger) tocTrigger.setAttribute('aria-expanded', 'false');
    };
    const closeTocDialog = function (restoreFocus) {
      if (!tocDialog) return;
      const wasOpen = isDialogOpen(tocDialog) || tocDialog.classList.contains('is-open');
      if (tocDialog.open && typeof tocDialog.close === 'function') { try { tocDialog.close(); } catch (_e) { tocDialog.removeAttribute('open'); } }
      if (tocDialog.hasAttribute('open')) tocDialog.removeAttribute('open');
      cleanupClosed();
      if (restoreFocus && wasOpen && tocTrigger && typeof tocTrigger.focus === 'function') tocTrigger.focus();
    };
    if (!tocDialog) return { closeTocDialog: closeTocDialog, isOpenedAsModal: function () { return false; } };
    if (tocTrigger) {
      tocTrigger.setAttribute('aria-expanded', isDialogOpen(tocDialog) ? 'true' : 'false');
      tocTrigger.addEventListener('click', function () {
        if (isDialogOpen(tocDialog)) return;
        if ('returnValue' in tocDialog) tocDialog.returnValue = '';
        state.openedAsModal = false;
        if (typeof tocDialog.showModal === 'function') { try { tocDialog.showModal(); state.openedAsModal = true; } catch (_e) { tocDialog.setAttribute('open', ''); } }
        else tocDialog.setAttribute('open', '');
        tocDialog.classList.add('is-open');
        tocTrigger.setAttribute('aria-expanded', 'true');
      });
    }
    tocDialog.addEventListener('close', cleanupClosed);
    tocDialog.addEventListener('click', function (ev) {
      const el = ev.target && typeof ev.target.closest === 'function' ? ev.target : null;
      if (!el) return;
      if (el.closest(TOC_CLOSE_SEL)) return closeTocDialog(true);
      const tocLink = el.closest('a[href]');
      if (!tocLink) return;
      const tid = resolveInPageTargetId(tocLink), tel = tid ? document.getElementById(tid) : null;
      if (tel && tel.closest('[hidden]')) resetSearch(false);
      closeTocDialog(false);
    });
    bindDialogLightDismiss(tocDialog, closeTocDialog, function () { return state.openedAsModal; });
    const desktopMq = typeof window.matchMedia === 'function' ? window.matchMedia('(min-width: 960px)') : null;
    const onDesktopGrow = function () { if (desktopMq ? desktopMq.matches : window.innerWidth >= 960) closeTocDialog(false); };
    if (desktopMq) { if (typeof desktopMq.addEventListener === 'function') desktopMq.addEventListener('change', onDesktopGrow); else if (typeof desktopMq.addListener === 'function') desktopMq.addListener(onDesktopGrow); }
    window.addEventListener('resize', onDesktopGrow);
    return { closeTocDialog: closeTocDialog, isOpenedAsModal: function () { return state.openedAsModal; } };
  }

  function createChapterTracker(entries, chapterEl) {
    const defaultTitle = chapterEl && chapterEl.textContent ? chapterEl.textContent.trim() : '';
    let activeSectionId = '', lockTarget = null, lockDist = 0, lockUntil = 0, rafPending = false;
    const getTocLinks = function () { return Array.from(document.querySelectorAll(TOC_NAV_SEL)); };
    const getThreshold = function () {
      const tb = document.querySelector('.oaw-topbar'), sb = document.getElementById('oaw-docs-subbar');
      return (tb ? tb.getBoundingClientRect().height : 46) + (sb && sb.getBoundingClientRect().height > 0 ? sb.getBoundingClientRect().height : 0) + 32;
    };
    const resolveSection = function (tid) {
      const tel = tid ? document.getElementById(tid) : null, sec = tel ? tel.closest('.oaw-docs-section, .oaw-doc-section') : null;
      return sec ? (entries.find(function (e) { return e.el === sec; }) || null) : null;
    };
    const setActiveChapter = function (secEntry, targetId) {
      const links = getTocLinks();
      if (!secEntry) {
        activeSectionId = '';
        if (chapterEl) chapterEl.textContent = entries.length ? 'No matching sections' : defaultTitle;
        return links.forEach(function (l) { l.removeAttribute('aria-current'); });
      }
      activeSectionId = secEntry.el.id || '';
      if (chapterEl && secEntry.title) chapterEl.textContent = secEntry.title;
      const hasExact = Boolean(targetId && links.some(function (l) { return resolveInPageTargetId(l) === targetId; }));
      const matchId = hasExact ? targetId : activeSectionId;
      links.forEach(function (l) { if (matchId && resolveInPageTargetId(l) === matchId) l.setAttribute('aria-current', 'location'); else l.removeAttribute('aria-current'); });
    };
    const syncFromScroll = function (force) {
      const threshold = getThreshold();
      if (!force && lockTarget && Date.now() < lockUntil) {
        const curDist = Math.abs(lockTarget.getBoundingClientRect().top - threshold);
        if (curDist <= lockDist + 4 && curDist > 48) { lockDist = curDist; return; }
      }
      lockTarget = null;
      const visible = entries.filter(function (e) { return !e.el.hidden; });
      if (visible.length === 0) return setActiveChapter(null, null);
      let active = visible[0];
      for (let i = 0; i < visible.length; i += 1) { if (visible[i].el.getBoundingClientRect().top <= threshold) active = visible[i]; else break; }
      const last = visible[visible.length - 1];
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 8 && last.el.getBoundingClientRect().top < window.innerHeight * 0.75) active = last;
      const links = getTocLinks(), subHeads = active.el.querySelectorAll('h2[id]');
      let subTarget = active.el.id;
      for (let j = 0; j < subHeads.length; j += 1) {
        const hid = subHeads[j].id;
        if (subHeads[j].getBoundingClientRect().top <= threshold && links.some(function (l) { return resolveInPageTargetId(l) === hid; })) subTarget = hid;
      }
      setActiveChapter(active, subTarget);
    };
    const scheduleSync = function () { if (!rafPending) { rafPending = true; window.requestAnimationFrame(function () { rafPending = false; syncFromScroll(false); }); } };
    if (typeof window.IntersectionObserver === 'function' && entries.length > 0) {
      const io = new IntersectionObserver(scheduleSync, { rootMargin: '-96px 0px -65% 0px', threshold: [0, 0.1] });
      entries.forEach(function (e) { io.observe(e.el); });
    }
    window.addEventListener('scroll', scheduleSync, { passive: true });
    window.addEventListener('scrollend', function () { if (lockTarget) { lockTarget = null; syncFromScroll(true); } }, { passive: true });
    ['wheel', 'touchstart'].forEach(function (n) { window.addEventListener(n, function () { lockTarget = null; }, { passive: true }); });
    return {
      getActiveSectionId: function () { return activeSectionId; },
      lockScrollSync: function (el, ms) { lockTarget = el || null; lockUntil = Date.now() + ms; lockDist = el ? Math.abs(el.getBoundingClientRect().top - getThreshold()) : 0; },
      resolveSection: resolveSection, setActiveChapter: setActiveChapter, syncFromScroll: syncFromScroll
    };
  }

  function init() {
    const entries = buildSectionModel(), searchInput = document.getElementById('oaw-docs-search');
    const clearBtn = document.getElementById('oaw-docs-search-clear'), emptyClearBtn = document.getElementById('oaw-empty-clear-btn');
    const countEl = document.getElementById('oaw-docs-search-count') || document.getElementById('oaw-docs-count');
    const emptyEl = document.getElementById('oaw-docs-empty') || document.querySelector('.va-empty-state[data-kind="filtered"]');
    const tocTrigger = document.getElementById('oaw-docs-toc-trigger'), tocDialog = document.getElementById('oaw-docs-toc-dialog');
    const tracker = createChapterTracker(entries, document.getElementById('oaw-docs-current-chapter'));
    const applyFilter = function (rawQuery) {
      const tokens = String(rawQuery || '').trim().toLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0, firstVis = null;
      entries.forEach(function (entry) {
        const match = tokens.length === 0 || entry.texts.some(function (c) { return tokens.every(function (t) { return c.indexOf(t) !== -1; }); });
        entry.el.hidden = !match;
        if (match) { visible += 1; if (!firstVis) firstVis = entry; }
      });
      if (countEl) countEl.textContent = formatCountText(visible, entries.length);
      if (emptyEl) emptyEl.hidden = !(visible === 0 && entries.length > 0);
      const curId = tracker.getActiveSectionId(), curOk = curId && entries.some(function (e) { return e.el.id === curId && !e.el.hidden; });
      if (!firstVis) tracker.setActiveChapter(null, null); else if (!curOk) tracker.setActiveChapter(firstVis, firstVis.el.id);
    };
    const resetSearch = function (focus) {
      if (searchInput) { searchInput.value = ''; if (focus && typeof searchInput.focus === 'function') searchInput.focus(); }
      applyFilter('');
    };
    const tocApi = bindTocDialog(tocTrigger, tocDialog, resetSearch);
    const jumpToTargetId = function (tid) {
      resetSearch(false);
      tocApi.closeTocDialog(false);
      const tel = document.getElementById(tid), sec = tracker.resolveSection(tid);
      if (sec) { tracker.lockScrollSync(tel || sec.el, prefersReducedMotion() ? 0 : 750); tracker.setActiveChapter(sec, tid); }
      if (tel) {
        try { window.history.replaceState(null, '', '#' + encodeURIComponent(tid)); } catch (_e) {}
        if (typeof tel.scrollIntoView === 'function') tel.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
        if (!tel.hasAttribute('tabindex')) tel.setAttribute('tabindex', '-1');
        if (typeof tel.focus === 'function') { try { tel.focus({ preventScroll: true }); } catch (_e) { tel.focus(); } }
      }
    };
    const syncFromHash = function () {
      let id = (window.location.hash || '').slice(1);
      if (!id) return false;
      try { id = decodeURIComponent(id); } catch (_e) {}
      const sec = tracker.resolveSection(id);
      if (!sec) return false;
      if (sec.el.hidden) resetSearch(false);
      tracker.lockScrollSync(document.getElementById(id) || sec.el, 350);
      tracker.setActiveChapter(sec, id);
      return true;
    };
    if (searchInput) { searchInput.addEventListener('input', function () { applyFilter(searchInput.value); }); applyFilter(searchInput.value); }
    else if (entries.length > 0) applyFilter('');
    if (!syncFromHash()) tracker.syncFromScroll(true);
    if (clearBtn) clearBtn.addEventListener('click', function () { resetSearch(true); });
    if (emptyEl) emptyEl.addEventListener('click', function (ev) {
      const btn = ev.target && typeof ev.target.closest === 'function' ? ev.target.closest(EMPTY_CLEAR_SEL) : null;
      if (btn) { const tid = resolveInPageTargetId(btn); if (tid) jumpToTargetId(tid); else resetSearch(true); }
    });
    if (emptyClearBtn && (!emptyEl || !emptyEl.contains(emptyClearBtn))) emptyClearBtn.addEventListener('click', function () { resetSearch(true); });
    document.addEventListener('click', function (ev) {
      const el = ev.target && typeof ev.target.closest === 'function'
        ? ev.target.closest('[data-doc-jump], [data-doc-target], .oaw-docs-main a[href^="#"], .oaw-docs-prose a[href^="#"], .oaw-docs-rail a[href^="#"], .oaw-docs-toc-list a[href^="#"]') : null;
      if (!el || el.matches(EMPTY_CLEAR_SEL)) return;
      const tid = resolveInPageTargetId(el);
      if (!tid) return tocApi.closeTocDialog(false);
      ev.preventDefault();
      jumpToTargetId(tid);
    });
    window.addEventListener('hashchange', syncFromHash);
    document.addEventListener('oaw:docs-navigate', function (ev) {
      const id = ev && ev.detail && typeof ev.detail.id === 'string' ? ev.detail.id : '';
      if (!id || !tracker.resolveSection(id)) return;
      ev.preventDefault();
      jumpToTargetId(id);
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.isComposing || ev.keyCode === 229) return;
      if (ev.key === 'Escape' && !ev.defaultPrevented) {
        if (isDialogOpen(tocDialog)) { if (!tocApi.isOpenedAsModal()) { ev.preventDefault(); tocApi.closeTocDialog(true); } return; }
        if (document.querySelector('dialog[open]') || hasOpenPopover() || !searchInput) return;
        if (searchInput.value) { ev.preventDefault(); resetSearch(document.activeElement === searchInput); }
        else if (document.activeElement === searchInput) searchInput.blur();
      } else if (ev.key === '/' && !ev.ctrlKey && !ev.metaKey && !ev.altKey && !ev.defaultPrevented && searchInput) {
        if (document.querySelector('dialog[open]') || isEditableElement(document.activeElement) || isEditableElement(ev.target)) return;
        ev.preventDefault();
        searchInput.focus();
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true }); else init();
}(window, document));
