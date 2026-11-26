/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.8.0 — Shared Site Shell Runtime
 * 4-theme persistence, user-menu theme buttons, sticky route links, viewport-aware popovers, and copy buttons.
 */
(function (window) {
  'use strict';

  const STORAGE_KEY = 'quiet-ui-site-theme';
  const VALID_THEMES = new Set(['white', 'paper', 'dark-paper', 'dark']);
  const DARK_THEMES = new Set(['dark-paper', 'dark']);
  const VIEWPORT_PAD = 8;
  const ROUTE_LINK_SELECTOR =
    '[data-oaw-route-link], .oaw-nav-links a, .oaw-mobile-subnav a, .oaw-cta-row a, .oaw-domain-card a';
  const POPOVER_PAIRS = [
    { btnId: 'oaw-projects-btn', popId: 'oaw-projects-popover', alignRight: false },
    { btnId: 'oaw-pillar-btn', popId: 'oaw-pillar-popover', alignRight: true },
    { btnId: 'oaw-user-btn', popId: 'oaw-user-popover', alignRight: true }
  ];
  const copyTimers = new WeakMap();
  const hasAnchorCss = typeof CSS !== 'undefined' && typeof CSS.supports === 'function' && CSS.supports('position-area', 'block-end');

  function normalizeTheme(raw) {
    const val = String(raw || '').trim();
    return VALID_THEMES.has(val) ? val : null;
  }

  function readStoredTheme() {
    try { return normalizeTheme(window.localStorage.getItem(STORAGE_KEY)); } catch (_e) { return null; }
  }

  function writeStoredTheme(theme) {
    try { window.localStorage.setItem(STORAGE_KEY, theme); } catch (_e) {}
  }

  function readUrlTheme() {
    try { return normalizeTheme(new URLSearchParams(window.location.search).get('theme')); } catch (_e) { return null; }
  }

  function resolveInitialTheme() {
    const demoHost = document.querySelector('.oaw-demo-chrome');
    const attrTheme = demoHost ? demoHost.dataset.theme : document.documentElement.dataset.theme;
    return readUrlTheme() || readStoredTheme() || normalizeTheme(attrTheme) || 'white';
  }

  function withThemeParam(rawHref, theme) {
    const trimmed = String(rawHref || '').trim();
    if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('//') || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(trimmed)) {
      return null;
    }
    const hashIdx = trimmed.indexOf('#');
    const beforeHash = hashIdx >= 0 ? trimmed.slice(0, hashIdx) : trimmed;
    const hashPart = hashIdx >= 0 ? trimmed.slice(hashIdx) : '';
    const qIdx = beforeHash.indexOf('?');
    const pathPart = qIdx >= 0 ? beforeHash.slice(0, qIdx) : beforeHash;
    const params = new URLSearchParams(qIdx >= 0 ? beforeHash.slice(qIdx + 1) : '');
    params.set('theme', theme);
    const qs = params.toString();
    return pathPart + (qs ? '?' + qs : '') + hashPart;
  }

  function syncColorSchemeMeta(theme) {
    const scheme = DARK_THEMES.has(theme) ? 'dark' : 'light';
    let meta = document.querySelector('meta[name="color-scheme"]');
    if (!meta && document.head) {
      meta = document.createElement('meta');
      meta.setAttribute('name', 'color-scheme');
      document.head.appendChild(meta);
    }
    if (meta) meta.setAttribute('content', scheme);
  }

  function updateUrlTheme(theme) {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('theme', theme);
      window.history.replaceState(null, '', url.toString());
    } catch (_e) {}
  }

  function applyTheme(rawTheme) {
    const theme = normalizeTheme(rawTheme) || 'white';
    const demoHost = document.querySelector('.oaw-demo-chrome');
    if (demoHost) {
      demoHost.dataset.theme = theme;
    } else {
      document.documentElement.dataset.theme = theme;
      syncColorSchemeMeta(theme);
    }
    document.querySelectorAll('.oaw-theme-opt[data-theme-opt]').forEach(function (btn) {
      const on = btn.getAttribute('data-theme-opt') === theme;
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.classList.toggle('is-active', on);
    });
    document.querySelectorAll(ROUTE_LINK_SELECTOR).forEach(function (link) {
      const nextHref = withThemeParam(link.getAttribute('href'), theme);
      if (nextHref !== null) link.setAttribute('href', nextHref);
    });
    return theme;
  }

  function initThemeControls() {
    const demoHost = document.querySelector('.oaw-demo-chrome');
    const urlTheme = readUrlTheme();
    const initial = applyTheme(demoHost ? (urlTheme || normalizeTheme(demoHost.dataset.theme) || 'white') : resolveInitialTheme());
    if (urlTheme) writeStoredTheme(initial);

    document.addEventListener('click', function (ev) {
      const target = ev.target;
      if (!target || typeof target.closest !== 'function') return;
      const opt = target.closest('.oaw-theme-opt[data-theme-opt]');
      if (!opt) return;
      const nextTheme = applyTheme(opt.getAttribute('data-theme-opt'));
      writeStoredTheme(nextTheme);
      if (demoHost) {
        window.dispatchEvent(new CustomEvent('oaw:theme-change', { detail: { theme: nextTheme } }));
      } else {
        updateUrlTheme(nextTheme);
      }
    });

    window.addEventListener('oaw:studio-theme-sync', function (ev) {
      const t = ev && ev.detail ? normalizeTheme(ev.detail.theme) : null;
      if (t) applyTheme(t);
    });
    window.addEventListener('storage', function (ev) {
      if (ev.key === STORAGE_KEY) {
        const t = normalizeTheme(ev.newValue);
        if (!t) return;
        const applied = applyTheme(t);
        if (demoHost) window.dispatchEvent(new CustomEvent('oaw:theme-change', { detail: { theme: applied } }));
      }
    });
  }

  function clearInlinePos(popEl) {
    Object.assign(popEl.style, { position: '', margin: '', inset: '', top: '', left: '' });
  }

  function clampPopover(popEl, trigEl, alignRight) {
    if (!popEl || !trigEl) return;
    clearInlinePos(popEl);
    const r = popEl.getBoundingClientRect();
    const tr = trigEl.getBoundingClientRect();
    const overflows = r.right > window.innerWidth - VIEWPORT_PAD || r.left < VIEWPORT_PAD;
    if (hasAnchorCss && !overflows) return;
    const maxL = Math.max(VIEWPORT_PAD, window.innerWidth - r.width - VIEWPORT_PAD);
    const rawL = hasAnchorCss ? r.left : (alignRight ? tr.right - r.width : tr.left);
    const rawT = hasAnchorCss ? Math.max(VIEWPORT_PAD, r.top) : Math.min(tr.bottom + 6, Math.max(VIEWPORT_PAD, window.innerHeight - r.height - VIEWPORT_PAD));
    Object.assign(popEl.style, {
      position: 'fixed', margin: '0', inset: 'auto',
      top: Math.round(rawT) + 'px', left: Math.round(Math.min(Math.max(VIEWPORT_PAD, rawL), maxL)) + 'px'
    });
  }

  function initPopovers() {
    const supportsPopover = typeof HTMLElement !== 'undefined' && 'showPopover' in HTMLElement.prototype;
    const entries = POPOVER_PAIRS.map(function (p) {
      return { btn: document.getElementById(p.btnId), pop: document.getElementById(p.popId), alignRight: p.alignRight };
    }).filter(function (e) { return Boolean(e.btn && e.pop); });

    const setFallback = function (entry, open) {
      entry.pop.hidden = !open;
      if (open) {
        entry.pop.setAttribute('data-open', 'true');
        clampPopover(entry.pop, entry.btn, entry.alignRight);
      } else {
        entry.pop.removeAttribute('data-open');
        clearInlinePos(entry.pop);
      }
      entry.btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };

    entries.forEach(function (entry) {
      const btn = entry.btn, pop = entry.pop;
      if (supportsPopover) {
        const isPopOpen = function () { return typeof pop.matches === 'function' && pop.matches(':popover-open'); };
        btn.setAttribute('aria-expanded', isPopOpen() ? 'true' : 'false');
        pop.addEventListener('toggle', function (ev) {
          const open = ev && typeof ev.newState === 'string' ? ev.newState === 'open' : isPopOpen();
          btn.setAttribute('aria-expanded', open ? 'true' : 'false');
          if (open) clampPopover(pop, btn, entry.alignRight);
          else clearInlinePos(pop);
        });
        pop.addEventListener('click', function (ev) {
          if (ev.target && ev.target.closest('a[href]') && typeof pop.hidePopover === 'function' && isPopOpen()) pop.hidePopover();
        });
        return;
      }
      setFallback(entry, false);
      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        const willOpen = pop.getAttribute('data-open') !== 'true';
        entries.forEach(function (other) { if (other !== entry) setFallback(other, false); });
        setFallback(entry, willOpen);
      });
      pop.addEventListener('click', function (ev) {
        if (ev.target && ev.target.closest('a[href]')) setFallback(entry, false);
      });
    });

    if (!supportsPopover && entries.length > 0) {
      document.addEventListener('click', function (ev) {
        entries.forEach(function (e) {
          if (e.pop.getAttribute('data-open') === 'true' && !e.pop.contains(ev.target) && !e.btn.contains(ev.target)) setFallback(e, false);
        });
      });
      document.addEventListener('keydown', function (ev) {
        if (ev.key !== 'Escape') return;
        entries.forEach(function (e) {
          if (e.pop.getAttribute('data-open') === 'true') {
            const hadFocus = e.pop.contains(document.activeElement);
            setFallback(e, false);
            if (hadFocus) e.btn.focus();
          }
        });
      });
    }
    window.addEventListener('resize', function () {
      entries.forEach(function (e) {
        const open = supportsPopover ? (typeof e.pop.matches === 'function' && e.pop.matches(':popover-open')) : e.pop.getAttribute('data-open') === 'true';
        if (open) clampPopover(e.pop, e.btn, e.alignRight);
      });
    });
  }

  function fallbackCopyText(text) {
    const prevFocus = document.activeElement;
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.cssText = 'position:fixed;inset-block-start:-9999px;opacity:0;';
    document.body.appendChild(area);
    let copied = false;
    try {
      area.select();
      area.setSelectionRange(0, text.length);
      copied = typeof document.execCommand === 'function' && document.execCommand('copy');
    } catch (_e) {
      copied = false;
    } finally {
      area.remove();
      if (prevFocus && typeof prevFocus.focus === 'function') prevFocus.focus({ preventScroll: true });
    }
    return copied;
  }

  function writeClipboard(text) {
    if (!text) return Promise.resolve(false);
    if (window.navigator && window.navigator.clipboard && typeof window.navigator.clipboard.writeText === 'function') {
      return window.navigator.clipboard.writeText(text).then(function () { return true; }).catch(function () {
        return fallbackCopyText(text);
      });
    }
    return Promise.resolve(fallbackCopyText(text));
  }

  function ensureLiveRegion() {
    let region = document.querySelector('#oaw-live-status, [data-oaw-live-status]');
    if (!region && document.body) {
      region = document.createElement('div');
      region.id = 'oaw-live-status';
      region.className = 'oaw-sr-only';
      region.setAttribute('aria-live', 'polite');
      region.setAttribute('aria-atomic', 'true');
      document.body.appendChild(region);
    }
    return region;
  }

  function setCopiedFeedback(btn) {
    if (!btn.dataset.copyLabel) btn.dataset.copyLabel = (btn.textContent || '').trim() || 'Copy';
    const prevTimer = copyTimers.get(btn);
    if (prevTimer) window.clearTimeout(prevTimer);
    btn.setAttribute('data-copied', 'true');
    btn.textContent = 'Copied';
    const live = ensureLiveRegion();
    if (live) live.textContent = 'Copied to clipboard';
    copyTimers.set(btn, window.setTimeout(function () {
      btn.removeAttribute('data-copied');
      btn.textContent = btn.dataset.copyLabel || 'Copy';
      if (live && live.textContent === 'Copied to clipboard') live.textContent = '';
      copyTimers.delete(btn);
    }, 1600));
  }

  function resolveCopyPayload(btn) {
    if (btn.hasAttribute('data-copy-text')) return btn.getAttribute('data-copy-text') || '';
    const block = btn.closest('.oaw-code-block');
    if (block) {
      const codeEl = block.querySelector('pre code, pre');
      return codeEl ? codeEl.textContent || '' : '';
    }
    const cmdWrap = btn.closest('.oaw-install-cmd');
    const cmdCode = cmdWrap ? cmdWrap.querySelector('code') : null;
    return cmdCode ? cmdCode.textContent || '' : '';
  }

  function initCopyButtons() {
    document.addEventListener('click', function (ev) {
      const target = ev.target;
      if (!target || typeof target.closest !== 'function') return;
      const btn = target.closest('.oaw-copy-btn[data-copy-text], .oaw-copy-code-btn');
      if (!btn) return;
      const text = resolveCopyPayload(btn);
      if (text) writeClipboard(text).then(function (ok) { if (ok) setCopiedFeedback(btn); });
    });
  }

  function init() {
    initThemeControls();
    initPopovers();
    initCopyButtons();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
}(window));
