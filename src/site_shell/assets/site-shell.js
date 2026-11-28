/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.8.0 — Shared Site Shell Runtime
 * Dual-key theme sync, meta/studio bridge, responsive 900px route switcher, popovers, and copy controls.
 */
(function (window, document) {
  'use strict';

  const THEME_KEY_PRIMARY = 'oaw_theme_v99';
  const THEME_KEY_COMPAT = 'quiet-ui-site-theme';
  const VALID_THEMES = new Set(['white', 'paper', 'dark-paper', 'dark']);
  const DARK_THEMES = new Set(['dark-paper', 'dark']);
  const THEME_COLORS = { white: '#F8FAFC', paper: '#EFECE5', 'dark-paper': '#252421', dark: '#172135' };
  const VIEWPORT_PAD = 8;
  const POPOVER_GAP = 6;
  const ROUTE_LINK_SEL =
    '[data-oaw-route-link], .oaw-nav-links a, .oaw-mobile-subnav a, .oaw-cta-row a, .oaw-domain-card a';
  const POPOVER_SPECS = [
    { btnId: 'oaw-projects-btn', popId: 'oaw-projects-popover', alignRight: false, closeOnLinkClick: true },
    { btnId: 'oaw-route-btn', popId: 'oaw-route-menu', alignRight: false, closeOnLinkClick: true, responsiveMax900: true },
    { btnId: 'oaw-pillar-btn', popId: 'oaw-pillar-popover', alignRight: true, closeOnLinkClick: true },
    { btnId: 'oaw-user-btn', popId: 'oaw-user-popover', alignRight: true, closeOnLinkClick: false }
  ];
  const copyTimers = new WeakMap();
  const supportsPopover = typeof HTMLElement !== 'undefined' && 'showPopover' in HTMLElement.prototype;
  const hasAnchorCss = typeof CSS !== 'undefined' && typeof CSS.supports === 'function' && CSS.supports('position-area', 'block-end');
  const desktopMq = typeof window.matchMedia === 'function' ? window.matchMedia('(min-width: 900px)') : null;
  const isDesktopViewport = function () { return desktopMq ? desktopMq.matches : window.innerWidth >= 900; };
  const normalizeTheme = function (raw) { const v = String(raw || '').trim(); return VALID_THEMES.has(v) ? v : null; };
  const readStoredTheme = function (k) { try { return normalizeTheme(window.localStorage.getItem(k)); } catch (_e) { return null; } };
  const readUrlTheme = function () { try { return normalizeTheme(new URLSearchParams(window.location.search).get('theme')); } catch (_e) { return null; } };
  const dispatchThemeChange = function (t) { window.dispatchEvent(new CustomEvent('oaw:theme-change', { detail: { theme: t } })); };

  function writeStoredTheme(theme) {
    try { window.localStorage.setItem(THEME_KEY_PRIMARY, theme); window.localStorage.setItem(THEME_KEY_COMPAT, theme); } catch (_e) {}
  }

  function resolveInitialTheme() {
    const demoHost = document.querySelector('.oaw-demo-chrome');
    return readUrlTheme() || readStoredTheme(THEME_KEY_PRIMARY) || readStoredTheme(THEME_KEY_COMPAT) ||
      normalizeTheme(document.documentElement.dataset.theme) || normalizeTheme(demoHost && demoHost.dataset.theme) || 'white';
  }

  function withThemeParam(rawHref, theme) {
    const trimmed = String(rawHref || '').trim();
    if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('//') || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(trimmed)) return null;
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

  function syncHeadMeta(name, content) {
    if (!content) return;
    let meta = document.querySelector('meta[name="' + name + '"]');
    if (!meta && document.head) {
      meta = document.createElement('meta');
      meta.setAttribute('name', name);
      document.head.appendChild(meta);
    }
    if (meta) meta.setAttribute('content', content);
  }

  function resolveThemeColor(theme, demoHost) {
    if (typeof window.getComputedStyle === 'function') {
      const target = demoHost || document.documentElement;
      if (target) {
        const cs = window.getComputedStyle(target);
        const tokenColor = (cs.getPropertyValue('--bg-elevated') || cs.getPropertyValue('--bg-canvas') || '').trim();
        if (tokenColor) return tokenColor;
      }
    }
    return THEME_COLORS[theme] || THEME_COLORS.white;
  }

  function applyTheme(rawTheme) {
    const theme = normalizeTheme(rawTheme) || 'white';
    const demoHost = document.querySelector('.oaw-demo-chrome');
    document.documentElement.dataset.theme = theme;
    if (demoHost) demoHost.dataset.theme = theme;
    syncHeadMeta('color-scheme', DARK_THEMES.has(theme) ? 'dark' : 'light');
    syncHeadMeta('theme-color', resolveThemeColor(theme, demoHost));
    document.querySelectorAll('[data-theme-opt]').forEach(function (btn) {
      const on = btn.getAttribute('data-theme-opt') === theme;
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.classList.toggle('is-active', on);
    });
    document.querySelectorAll(ROUTE_LINK_SEL).forEach(function (link) {
      const nextHref = withThemeParam(link.getAttribute('href'), theme);
      if (nextHref !== null) link.setAttribute('href', nextHref);
    });
    return theme;
  }

  function initThemeControls() {
    const urlTheme = readUrlTheme();
    const initial = applyTheme(resolveInitialTheme());
    if (urlTheme) writeStoredTheme(initial);

    document.addEventListener('click', function (ev) {
      const opt = ev.target && typeof ev.target.closest === 'function' ? ev.target.closest('[data-theme-opt]') : null;
      if (!opt) return;
      const nextTheme = applyTheme(opt.getAttribute('data-theme-opt'));
      writeStoredTheme(nextTheme);
      if (!document.querySelector('.oaw-demo-chrome')) {
        try { const u = new URL(window.location.href); u.searchParams.set('theme', nextTheme); window.history.replaceState(null, '', u.toString()); } catch (_e) {}
      }
      dispatchThemeChange(nextTheme);
    });

    window.addEventListener('oaw:studio-theme-sync', function (ev) {
      const t = ev && ev.detail ? normalizeTheme(ev.detail.theme) : null;
      if (t) applyTheme(t);
    });

    window.addEventListener('storage', function (ev) {
      if (ev.storageArea && ev.storageArea !== window.localStorage) return;
      if (ev.key !== null && ev.key !== THEME_KEY_PRIMARY && ev.key !== THEME_KEY_COMPAT) return;
      const next = ev.key === null ? 'white'
        : (normalizeTheme(ev.newValue) || readStoredTheme(THEME_KEY_PRIMARY) || readStoredTheme(THEME_KEY_COMPAT) || 'white');
      const prev = document.documentElement.dataset.theme;
      const applied = applyTheme(next);
      if (applied !== prev) dispatchThemeChange(applied);
    });
  }

  function clearInlinePos(popEl) {
    ['position', 'position-area', 'margin', 'inset', 'top', 'left'].forEach(function (p) { popEl.style.removeProperty(p); });
  }

  function clampPopover(popEl, trigEl, alignRight) {
    if (!popEl || !trigEl) return;
    clearInlinePos(popEl);
    const r = popEl.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    const vw = window.innerWidth, vh = window.innerHeight;
    const overflows = r.left < VIEWPORT_PAD || r.right > vw - VIEWPORT_PAD || r.top < VIEWPORT_PAD || r.bottom > vh - VIEWPORT_PAD;
    if (hasAnchorCss && !overflows) return;
    const tr = trigEl.getBoundingClientRect();
    const maxL = Math.max(VIEWPORT_PAD, vw - r.width - VIEWPORT_PAD);
    const rawL = hasAnchorCss ? r.left : (alignRight ? tr.right - r.width : tr.left);
    let rawT = hasAnchorCss ? r.top : tr.bottom + POPOVER_GAP;
    if (!hasAnchorCss && rawT + r.height > vh - VIEWPORT_PAD && tr.top - POPOVER_GAP - r.height >= VIEWPORT_PAD) rawT = tr.top - r.height - POPOVER_GAP;
    const top = Math.min(Math.max(VIEWPORT_PAD, rawT), Math.max(VIEWPORT_PAD, vh - r.height - VIEWPORT_PAD));
    const left = Math.min(Math.max(VIEWPORT_PAD, rawL), maxL);
    popEl.style.position = 'fixed';
    popEl.style.setProperty('position-area', 'none');
    popEl.style.margin = '0';
    popEl.style.inset = 'auto';
    popEl.style.top = Math.round(top) + 'px';
    popEl.style.left = Math.round(left) + 'px';
  }

  const isEntryActive = function (entry) { return !entry.responsiveMax900 || !isDesktopViewport(); };

  function isEntryOpen(entry) {
    if (!isEntryActive(entry)) return false;
    if (supportsPopover && entry.pop.hasAttribute('popover')) {
      try { if (entry.pop.matches(':popover-open')) return true; } catch (_e) {}
    }
    return entry.pop.getAttribute('data-open') === 'true' || entry.pop.classList.contains('is-open');
  }

  function setEntryOpen(entry, open, restoreFocus, allEntries) {
    if (open && !isEntryActive(entry)) return;
    if (supportsPopover && entry.pop.hasAttribute('popover')) {
      if (open) {
        entry.pop.removeAttribute('hidden');
        try { if (!isEntryOpen(entry) && typeof entry.pop.showPopover === 'function') entry.pop.showPopover(); return; } catch (_e) {}
      } else {
        if (typeof entry.pop.hidePopover === 'function') { try { if (entry.pop.matches(':popover-open')) entry.pop.hidePopover(); } catch (_e) {} }
        entry.pop.removeAttribute('data-open');
        entry.pop.classList.remove('is-open');
        entry.btn.setAttribute('aria-expanded', 'false');
        clearInlinePos(entry.pop);
        if (restoreFocus) entry.btn.focus();
        return;
      }
    }
    if (open && allEntries) allEntries.forEach(function (o) { if (o !== entry) setEntryOpen(o, false, false, null); });
    entry.pop.hidden = !open;
    if (open) {
      entry.pop.setAttribute('data-open', 'true');
      entry.pop.classList.add('is-open');
      clampPopover(entry.pop, entry.btn, entry.alignRight);
    } else {
      entry.pop.removeAttribute('data-open');
      entry.pop.classList.remove('is-open');
      clearInlinePos(entry.pop);
    }
    entry.btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (!open && restoreFocus) entry.btn.focus();
  }

  function wirePopoverEntry(entry, allEntries) {
    const btn = entry.btn, pop = entry.pop;
    const hasNativeInvoker = supportsPopover && btn.getAttribute('popovertarget') === pop.id;
    if (supportsPopover) {
      const onPopToggle = function (ev, clamp) {
        if (!isEntryActive(entry)) { btn.setAttribute('aria-expanded', 'false'); pop.classList.remove('is-open'); return clearInlinePos(pop); }
        const open = ev && typeof ev.newState === 'string' ? ev.newState === 'open' : isEntryOpen(entry);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        pop.classList.toggle('is-open', open);
        if (clamp) { if (open) clampPopover(pop, btn, entry.alignRight); else clearInlinePos(pop); }
      };
      pop.addEventListener('beforetoggle', function (ev) { onPopToggle(ev, false); });
      pop.addEventListener('toggle', function (ev) { onPopToggle(ev, true); });
    }
    if (!hasNativeInvoker) {
      btn.addEventListener('click', function (ev) {
        if (!isEntryActive(entry)) return;
        ev.preventDefault();
        setEntryOpen(entry, !isEntryOpen(entry), false, allEntries);
      });
    }
    if (!supportsPopover && isEntryActive(entry)) setEntryOpen(entry, false, false, null);
    else btn.setAttribute('aria-expanded', isEntryOpen(entry) ? 'true' : 'false');
    pop.addEventListener('click', function (ev) {
      if (entry.closeOnLinkClick && isEntryActive(entry) && ev.target && typeof ev.target.closest === 'function' && ev.target.closest('a[href]')) {
        setEntryOpen(entry, false, false, allEntries);
      }
    });
  }

  function initPopovers() {
    const entries = POPOVER_SPECS.map(function (s) {
      return {
        btn: document.getElementById(s.btnId), pop: document.getElementById(s.popId),
        alignRight: s.alignRight, closeOnLinkClick: s.closeOnLinkClick, responsiveMax900: Boolean(s.responsiveMax900)
      };
    }).filter(function (e) { return Boolean(e.btn && e.pop); });
    const routeEntry = entries.find(function (e) { return e.responsiveMax900; }) || null;
    let lastDesktop = null;
    const syncRouteMode = function () {
      if (!routeEntry) return;
      const desktop = isDesktopViewport();
      if (desktop === lastDesktop) return;
      lastDesktop = desktop;
      setEntryOpen(routeEntry, false, false, entries);
      if (desktop) { routeEntry.pop.removeAttribute('popover'); routeEntry.pop.removeAttribute('hidden'); }
      else { routeEntry.pop.setAttribute('popover', 'auto'); if (supportsPopover) routeEntry.pop.removeAttribute('hidden'); else routeEntry.pop.hidden = true; }
    };
    syncRouteMode();
    entries.forEach(function (e) { wirePopoverEntry(e, entries); });
    if (desktopMq) {
      if (typeof desktopMq.addEventListener === 'function') desktopMq.addEventListener('change', syncRouteMode);
      else if (typeof desktopMq.addListener === 'function') desktopMq.addListener(syncRouteMode);
    }
    if (!supportsPopover && entries.length > 0) {
      document.addEventListener('click', function (ev) {
        entries.forEach(function (e) { if (isEntryOpen(e) && !e.pop.contains(ev.target) && !e.btn.contains(ev.target)) setEntryOpen(e, false, false, entries); });
      });
    }
    document.addEventListener('keydown', function (ev) {
      if (ev.isComposing || ev.keyCode === 229) return;
      if (ev.key !== 'Escape' || document.querySelector('dialog[open]')) return;
      const openEntry = entries.find(isEntryOpen);
      if (!openEntry) return;
      ev.preventDefault();
      ev.stopPropagation();
      if (typeof ev.stopImmediatePropagation === 'function') ev.stopImmediatePropagation();
      setEntryOpen(openEntry, false, true, entries);
    });
    window.addEventListener('resize', function () {
      syncRouteMode();
      entries.forEach(function (e) { if (isEntryOpen(e)) clampPopover(e.pop, e.btn, e.alignRight); });
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
    try { area.select(); area.setSelectionRange(0, text.length); copied = typeof document.execCommand === 'function' && document.execCommand('copy'); }
    catch (_e) { copied = false; }
    finally { area.remove(); if (prevFocus && typeof prevFocus.focus === 'function') prevFocus.focus({ preventScroll: true }); }
    return copied;
  }

  function writeClipboard(text) {
    if (!text) return Promise.resolve(false);
    if (window.navigator && window.navigator.clipboard && typeof window.navigator.clipboard.writeText === 'function') {
      return window.navigator.clipboard.writeText(text).then(function () { return true; }).catch(function () { return fallbackCopyText(text); });
    }
    return Promise.resolve(fallbackCopyText(text));
  }

  function setCopiedFeedback(btn) {
    const isSlug = btn.classList.contains('oaw-cmd-slug');
    if (!isSlug && !btn.dataset.copyLabel) btn.dataset.copyLabel = (btn.textContent || '').trim() || 'Copy';
    const prevTimer = copyTimers.get(btn);
    if (prevTimer) window.clearTimeout(prevTimer);
    btn.setAttribute('data-copied', 'true');
    if (!isSlug) btn.textContent = 'Copied';
    let live = document.querySelector('#oaw-live-status, [data-oaw-live-status]');
    if (!live && document.body) {
      live = document.createElement('div');
      live.id = 'oaw-live-status';
      live.className = 'oaw-sr-only';
      live.setAttribute('aria-live', 'polite');
      live.setAttribute('aria-atomic', 'true');
      document.body.appendChild(live);
    }
    if (live) live.textContent = 'Copied to clipboard';
    copyTimers.set(btn, window.setTimeout(function () {
      btn.removeAttribute('data-copied');
      if (!isSlug) btn.textContent = btn.dataset.copyLabel || 'Copy';
      if (live && live.textContent === 'Copied to clipboard') live.textContent = '';
      copyTimers.delete(btn);
    }, 1600));
  }

  function resolveCopyPayload(btn) {
    if (btn.hasAttribute('data-copy-text')) return btn.getAttribute('data-copy-text') || '';
    const block = btn.closest('.oaw-code-block');
    if (block) { const c = block.querySelector('pre code, pre'); return c ? c.textContent || '' : ''; }
    const cmd = btn.closest('.oaw-install-cmd');
    const code = cmd ? cmd.querySelector('code') : null;
    return code ? code.textContent || '' : '';
  }

  function initCopyButtons() {
    document.addEventListener('click', function (ev) {
      const btn = ev.target && typeof ev.target.closest === 'function'
        ? ev.target.closest('.oaw-copy-btn, .oaw-copy-code-btn, .oaw-cmd-slug[data-copy-text]') : null;
      if (!btn) return;
      const text = resolveCopyPayload(btn);
      if (text) writeClipboard(text).then(function (ok) { if (ok) setCopiedFeedback(btn); });
    });
  }

  function init() { initThemeControls(); initPopovers(); initCopyButtons(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
}(window, document));
