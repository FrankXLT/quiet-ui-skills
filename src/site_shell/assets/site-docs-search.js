/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.8.0 — Route 3 Docs Search, Quick Jumps & Mobile TOC Sheet
 */
(function (window) {
  'use strict';

  function parseSearchIndex() {
    const el = document.getElementById('oaw-docs-search-index');
    if (!el) return [];
    try {
      const parsed = JSON.parse(el.textContent || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch (_e) {
      return [];
    }
  }

  function buildSectionModel() {
    const sections = Array.from(document.querySelectorAll('.oaw-docs-section, .oaw-doc-section'));
    const records = parseSearchIndex();
    const byId = new Map();
    const byDocKey = new Map();
    const entries = sections.map(function (el) {
      const entry = { el: el, texts: [] };
      if (el.id) {
        byId.set(el.id, entry);
        byDocKey.set(el.id.startsWith('doc-') ? el.id.slice(4) : el.id, entry);
      }
      if (el.dataset && el.dataset.docId) byDocKey.set(el.dataset.docId, entry);
      return entry;
    });

    records.forEach(function (rec) {
      if (!rec || typeof rec !== 'object') return;
      const haystack = [rec.title, rec.category, rec.heading, rec.text].filter(Boolean).join(' ').toLowerCase();
      if (!haystack) return;
      let target = null;
      if (rec.doc_id && byDocKey.has(String(rec.doc_id))) {
        target = byDocKey.get(String(rec.doc_id));
      } else if (rec.id && byId.has(String(rec.id))) {
        target = byId.get(String(rec.id));
      } else if (rec.id) {
        const node = document.getElementById(String(rec.id));
        if (node) target = entries.find(function (e) { return e.el.contains(node); }) || null;
      }
      if (target) target.texts.push(haystack);
    });

    entries.forEach(function (entry) {
      if (entry.texts.length === 0) entry.texts.push((entry.el.textContent || '').toLowerCase());
    });
    return entries;
  }

  function entryMatchesTokens(entry, tokens) {
    if (tokens.length === 0) return true;
    return entry.texts.some(function (chunk) {
      return tokens.every(function (tok) { return chunk.indexOf(tok) !== -1; });
    });
  }

  function formatCountText(visible, total) {
    if (visible === 0) return '0 matching sections';
    return String(visible) + ' of ' + String(total) + (total === 1 ? ' guide' : ' guides');
  }

  function bindDialogLightDismissFallback(dialog) {
    if (!dialog || (typeof HTMLDialogElement !== 'undefined' && 'closedBy' in HTMLDialogElement.prototype)) return;
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
    dialog.addEventListener('click', function (ev) {
      if (ev.target === dialog && (ev.clientX !== 0 || ev.clientY !== 0) && isOutside(ev)) dialog.close();
    });
  }

  function isEditableElement(el) {
    if (!el) return false;
    const tag = (el.tagName || '').toUpperCase();
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || Boolean(el.isContentEditable);
  }

  function resolveInPageTargetId(el) {
    const raw = (el.getAttribute('data-doc-target') || el.getAttribute('data-doc-jump') || el.getAttribute('href') || '').trim();
    if (!raw) return null;
    if (raw.startsWith('#')) return raw.slice(1) || null;
    return /^[a-zA-Z0-9_-]+$/.test(raw) ? raw : null;
  }

  function bindTocDialog(tocTrigger, tocDialog, closeTocDialog, resetSearch) {
    if (!tocTrigger || !tocDialog) return;
    tocTrigger.setAttribute('aria-expanded', tocDialog.open ? 'true' : 'false');
    tocTrigger.addEventListener('click', function () {
      if (tocDialog.open) return;
      if (typeof tocDialog.showModal === 'function') tocDialog.showModal();
      else tocDialog.setAttribute('open', '');
      tocTrigger.setAttribute('aria-expanded', 'true');
    });
    tocDialog.addEventListener('close', function () { tocTrigger.setAttribute('aria-expanded', 'false'); });
    tocDialog.addEventListener('click', function (ev) {
      const el = ev.target;
      if (!el || typeof el.closest !== 'function') return;
      if (el.closest('[data-close-dialog], [data-toc-close], .va-modal-sheet-hdr button, button[aria-label*="close" i]')) {
        closeTocDialog();
        return;
      }
      const tocLink = el.closest('a[href]');
      if (!tocLink) return;
      const href = (tocLink.getAttribute('href') || '').trim();
      if (href.startsWith('#')) {
        const targetSection = href.slice(1) ? document.getElementById(href.slice(1)) : null;
        if (targetSection && targetSection.closest('[hidden]')) resetSearch(false);
      }
      closeTocDialog();
    });
    bindDialogLightDismissFallback(tocDialog);
  }

  function init() {
    const entries = buildSectionModel();
    const searchInput = document.getElementById('oaw-docs-search');
    const clearBtn = document.getElementById('oaw-docs-search-clear');
    const emptyClearBtn = document.getElementById('oaw-empty-clear-btn');
    const countEl = document.getElementById('oaw-docs-search-count');
    const emptyEl = document.getElementById('oaw-docs-empty') || document.querySelector('.va-empty-state[data-kind="filtered"]');
    const tocTrigger = document.getElementById('oaw-docs-toc-trigger');
    const tocDialog = document.getElementById('oaw-docs-toc-dialog');

    function closeTocDialog() {
      if (!tocDialog) return;
      if (tocDialog.open && typeof tocDialog.close === 'function') tocDialog.close();
      else if (tocDialog.hasAttribute('open')) tocDialog.removeAttribute('open');
      if (tocTrigger) tocTrigger.setAttribute('aria-expanded', 'false');
    }

    function applyFilter(rawQuery) {
      const tokens = String(rawQuery || '').trim().toLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      entries.forEach(function (entry) {
        const match = entryMatchesTokens(entry, tokens);
        entry.el.hidden = !match;
        if (match) visible += 1;
      });
      if (countEl) countEl.textContent = formatCountText(visible, entries.length);
      if (emptyEl) emptyEl.hidden = !(visible === 0 && entries.length > 0);
    }

    function resetSearch(focusInput) {
      if (searchInput) {
        searchInput.value = '';
        if (focusInput && typeof searchInput.focus === 'function') searchInput.focus();
      }
      applyFilter('');
    }

    function jumpToTargetId(targetId) {
      resetSearch(false);
      closeTocDialog();
      const targetEl = document.getElementById(targetId);
      if (targetEl && typeof targetEl.scrollIntoView === 'function') {
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    if (searchInput) {
      searchInput.addEventListener('input', function () { applyFilter(searchInput.value); });
      applyFilter(searchInput.value);
    } else if (entries.length > 0) {
      applyFilter('');
    }

    if (clearBtn) clearBtn.addEventListener('click', function () { resetSearch(true); });

    if (emptyClearBtn) {
      emptyClearBtn.addEventListener('click', function () {
        const targetId = resolveInPageTargetId(emptyClearBtn);
        if (targetId) jumpToTargetId(targetId);
        else resetSearch(true);
      });
    }

    document.addEventListener('click', function (ev) {
      const target = ev.target;
      if (!target || typeof target.closest !== 'function') return;
      const jumpEl = target.closest('[data-doc-jump], [data-doc-target], .oaw-docs-main a[href^="#"], .oaw-docs-prose a[href^="#"]');
      if (!jumpEl || jumpEl === emptyClearBtn) return;
      const targetId = resolveInPageTargetId(jumpEl);
      if (!targetId) { closeTocDialog(); return; }
      ev.preventDefault();
      jumpToTargetId(targetId);
    });

    bindTocDialog(tocTrigger, tocDialog, closeTocDialog, resetSearch);

    document.addEventListener('keydown', function (ev) {
      if (ev.key !== '/' || ev.ctrlKey || ev.metaKey || ev.altKey || !searchInput) return;
      if (document.querySelector('dialog[open]') || isEditableElement(document.activeElement)) return;
      ev.preventDefault();
      searchInput.focus();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
}(window));
