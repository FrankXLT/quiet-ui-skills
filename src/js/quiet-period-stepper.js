// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  function positionPopover(trigger, popover) {
    if (!trigger || !popover) return;
    var hasLinkedAnchor = popover.hasAttribute('popover') && popover.id &&
      trigger.getAttribute('popovertarget') === popover.id &&
      typeof CSS !== 'undefined' && typeof CSS.supports === 'function' &&
      CSS.supports('position-area', 'block-end');
    if (hasLinkedAnchor) return;
    var doc = popover.ownerDocument;
    var tr = trigger.getBoundingClientRect();
    var vw = (root.innerWidth || (doc && doc.documentElement && doc.documentElement.clientWidth) || 1024);
    var vh = (root.innerHeight || (doc && doc.documentElement && doc.documentElement.clientHeight) || 768);
    var isRtl = doc && ((doc.documentElement && doc.documentElement.dir === 'rtl') || doc.dir === 'rtl');
    popover.style.positionArea = 'none';
    popover.style.position = 'fixed';
    var pr = popover.getBoundingClientRect();
    var popW = Math.max(pr.width || 240, 220), popH = Math.max(pr.height || 180, 140);
    var anchorX = isRtl ? (tr.right - popW) : tr.left;
    var left = Math.max(8, Math.min(vw - popW - 8, anchorX));
    var spaceBelow = vh - tr.bottom - 12;
    var spaceAbove = tr.top - 12;
    var top;
    if (popH <= spaceBelow || spaceBelow >= spaceAbove) top = Math.max(8, Math.min(vh - popH - 8, tr.bottom + 6));
    else top = Math.max(8, tr.top - popH - 6);
    popover.style.left = Math.round(left) + 'px';
    popover.style.top = Math.round(top) + 'px';
  }

  function isPopOpen(pop) {
    if (!pop) return false;
    return pop.dataset.open === 'true' || (typeof pop.matches === 'function' && pop.matches(':is(:popover-open, .\\:popover-open)'));
  }

  function closeOtherPopovers(doc, exceptStepper) {
    if (!doc) return;
    doc.querySelectorAll('.va-period-stepper').forEach(function (st) {
      if (st !== exceptStepper) closePopover(st, false);
    });
  }

  function closePopover(stepper, restoreFocus) {
    if (!stepper) return;
    var trigger = stepper.querySelector('.va-period-trigger');
    var pop = stepper.querySelector('.va-preset-popover');
    if (!pop || !isPopOpen(pop)) return;
    pop.dataset.open = 'false';
    if (!(pop.hasAttribute('popover') && trigger && pop.id && trigger.getAttribute('popovertarget') === pop.id)) {
      pop.setAttribute('hidden', '');
    }
    if (pop.hasAttribute('popover') && typeof pop.hidePopover === 'function') {
      try { if (pop.matches(':is(:popover-open, .\\:popover-open)')) pop.hidePopover(); } catch (_e) {}
    }
    if (trigger) {
      trigger.setAttribute('aria-expanded', 'false');
      if (restoreFocus) trigger.focus({ preventScroll: true });
    }
  }

  function openPopover(stepper, focusFirst) {
    if (!stepper) return;
    var trigger = stepper.querySelector('.va-period-trigger');
    var pop = stepper.querySelector('.va-preset-popover');
    if (!trigger || !pop) return;
    closeOtherPopovers(stepper.ownerDocument, stepper);
    pop.removeAttribute('hidden');
    pop.dataset.open = 'true';
    trigger.setAttribute('aria-expanded', 'true');
    if (pop.hasAttribute('popover') && typeof pop.showPopover === 'function') {
      try { if (!pop.matches(':is(:popover-open, .\\:popover-open)')) pop.showPopover({ source: trigger }); } catch (_e) {}
    }
    positionPopover(trigger, pop);
    if (focusFirst) {
      var items = [].slice.call(pop.querySelectorAll('.va-preset-item:not(:disabled)'));
      var active = pop.querySelector('.va-preset-item[aria-checked="true"]:not(:disabled)') || items[0];
      if (active) active.focus({ preventScroll: true });
    }
  }

  function applyPresetChoice(stepper, item) {
    if (!stepper || !item || item.disabled) return;
    var val = item.dataset.preset || item.textContent.trim();
    var lbl = item.dataset.label || item.textContent.trim();
    var spanTxt = item.dataset.span || '';
    stepper.dataset.value = val;
    stepper.querySelectorAll('.va-preset-item').forEach(function (b) {
      b.setAttribute('aria-checked', b === item ? 'true' : 'false');
    });
    var lblEl = stepper.querySelector('[data-period-label]');
    if (lblEl) lblEl.textContent = spanTxt ? (lbl + ' · ' + spanTxt) : lbl;
    var todayBtn = stepper.querySelector('[data-period-today]');
    if (todayBtn) todayBtn.hidden = item.dataset.atToday === 'true';
    closePopover(stepper, true);
    if (typeof root.CustomEvent === 'function') {
      stepper.dispatchEvent(new root.CustomEvent('quiet:period-change', { bubbles: true, detail: { preset: val, label: lbl, span: spanTxt } }));
    }
  }

  function bindStepper(stepper) {
    if (!stepper || stepper.dataset.quietBound === '1') return;
    stepper.dataset.quietBound = '1';
    var doc = stepper.ownerDocument;
    var trigger = stepper.querySelector('.va-period-trigger');
    var pop = stepper.querySelector('.va-preset-popover');
    if (trigger && pop) {
      var isNativeLinked = pop.hasAttribute('popover') && !!pop.id && trigger.getAttribute('popovertarget') === pop.id;
      if (isNativeLinked) {
        pop.removeAttribute('hidden');
        pop.addEventListener('toggle', function (ev) {
          var opening = ev && ev.newState === 'open';
          pop.dataset.open = opening ? 'true' : 'false';
          trigger.setAttribute('aria-expanded', opening ? 'true' : 'false');
          if (opening) {
            closeOtherPopovers(doc, stepper);
            positionPopover(trigger, pop);
          }
        });
      } else {
        trigger.addEventListener('click', function (ev) {
          if (isPopOpen(pop)) closePopover(stepper, false);
          else openPopover(stepper, ev.detail === 0);
        });
      }
      trigger.addEventListener('keydown', function (ev) {
        if (ev.key === 'ArrowDown') { ev.preventDefault(); openPopover(stepper, true); }
        else if (ev.key === 'Escape') { closePopover(stepper, true); }
      });
      pop.addEventListener('keydown', function (ev) {
        var items = [].slice.call(pop.querySelectorAll('.va-preset-item:not(:disabled)'));
        if (ev.key === 'Escape') { ev.preventDefault(); closePopover(stepper, true); return; }
        if (!items.length) return;
        var idx = items.indexOf(doc.activeElement);
        if (ev.key === 'ArrowDown') { ev.preventDefault(); items[(idx + 1) % items.length].focus(); }
        else if (ev.key === 'ArrowUp') { ev.preventDefault(); items[(idx - 1 + items.length) % items.length].focus(); }
        else if (ev.key === 'Home') { ev.preventDefault(); items[0].focus(); }
        else if (ev.key === 'End') { ev.preventDefault(); items[items.length - 1].focus(); }
      });
      pop.addEventListener('click', function (ev) {
        var item = ev.target && ev.target.closest ? ev.target.closest('.va-preset-item') : null;
        if (item) applyPresetChoice(stepper, item);
      });
    }
    stepper.addEventListener('click', function (ev) {
      var stepBtn = ev.target && ev.target.closest ? ev.target.closest('[data-period-step]') : null;
      if (stepBtn && typeof root.CustomEvent === 'function') {
        stepper.dispatchEvent(new root.CustomEvent('quiet:period-change', { bubbles: true, detail: { step: Number(stepBtn.dataset.periodStep || 0), preset: stepper.dataset.value || '' } }));
      }
      var todayBtn = ev.target && ev.target.closest ? ev.target.closest('[data-period-today]') : null;
      if (todayBtn && !todayBtn.hidden) {
        todayBtn.hidden = true;
        if (typeof root.CustomEvent === 'function') {
          stepper.dispatchEvent(new root.CustomEvent('quiet:period-change', { bubbles: true, detail: { today: true, preset: stepper.dataset.value || '' } }));
        }
      }
    });
  }

  function expandActiveBranches(rail) {
    if (!rail) return;
    rail.querySelectorAll('.va-tree-dest[aria-current="page"], .va-tree-dest.is-active').forEach(function (dest) {
      var grp = dest.closest('.va-tree-group, .va-tree-children');
      while (grp && rail.contains(grp)) {
        grp.hidden = false;
        var parentRow = grp.previousElementSibling;
        var caret = parentRow && parentRow.querySelector ? parentRow.querySelector('.va-tree-caret') : null;
        if (caret) caret.setAttribute('aria-expanded', 'true');
        grp = grp.parentElement ? grp.parentElement.closest('.va-tree-group, .va-tree-children') : null;
      }
    });
  }

  function applyTreeChildCaps(rail) {
    if (!rail || !rail.ownerDocument) return;
    var doc = rail.ownerDocument;
    rail.querySelectorAll('.va-tree-children, .va-tree-group').forEach(function (grp) {
      if (grp.dataset.treeCap === 'false' || grp.querySelector(':scope > .va-tree-more')) return;
      var parsedMax = parseInt(grp.dataset.maxVisible || '5', 10);
      var maxVis = Math.max(1, Number.isFinite(parsedMax) ? parsedMax : 5);
      var kids = [].slice.call(grp.children).filter(function (el) {
        return !el.classList.contains('va-tree-more') && !el.classList.contains('va-tree-group') && !el.classList.contains('va-tree-children');
      });
      if (kids.length <= maxVis) return;
      var actIdx = kids.findIndex(function (el) {
        return el.matches('.is-active, [aria-current="page"]') || !!el.querySelector('.is-active, [aria-current="page"]');
      });
      var hiddenKids = [];
      kids.forEach(function (el, idx) {
        var keep = actIdx >= maxVis ? (idx < maxVis - 1 || idx === actIdx) : (idx < maxVis);
        if (!keep) {
          el.hidden = true;
          el.dataset.treeOverflow = '1';
          hiddenKids.push(el);
          var sub = el.nextElementSibling;
          if (sub && (sub.classList.contains('va-tree-group') || sub.classList.contains('va-tree-children')) && !sub.hidden) {
            sub.hidden = true;
            sub.dataset.treeOverflow = '1';
          }
        }
      });
      if (hiddenKids.length) {
        var btn = doc.createElement('button');
        btn.type = 'button';
        btn.className = 'va-tree-more';
        btn.textContent = '+ Show ' + hiddenKids.length + ' older…';
        grp.appendChild(btn);
      }
    });
  }

  function getBackdropFor(rail, doc) {
    if (rail && rail.nextElementSibling && rail.nextElementSibling.classList && rail.nextElementSibling.classList.contains('va-drawer-backdrop')) {
      return rail.nextElementSibling;
    }
    return doc ? doc.querySelector('.va-drawer-backdrop') : null;
  }

  function getTriggersFor(rail, doc) {
    if (!rail || !doc) return [];
    if (rail.id) {
      return [].slice.call(doc.querySelectorAll('[aria-controls="' + rail.id + '"], [data-rail-trigger="' + rail.id + '"]'));
    }
    return [].slice.call(doc.querySelectorAll('[data-rail-trigger=""]'));
  }

  function setRailOpen(rail, backdrop, open, restoreFocus) {
    if (!rail) return;
    if (open) expandActiveBranches(rail);
    rail.dataset.open = open ? 'true' : 'false';
    rail.classList.toggle('is-open', !!open);
    var doc = rail.ownerDocument;
    var isOverlay = rail.dataset.mode === 'overlay' || (root.innerWidth || 1200) < 1080;
    var bd = backdrop || getBackdropFor(rail, doc);
    if (bd) {
      var showBd = !!(open && isOverlay);
      bd.dataset.open = showBd ? 'true' : 'false';
      bd.classList.toggle('is-open', showBd);
    }
    var trigs = getTriggersFor(rail, doc);
    trigs.forEach(function (btn) { btn.setAttribute('aria-expanded', open ? 'true' : 'false'); });
    if (!open && restoreFocus && trigs[0] && typeof trigs[0].focus === 'function') trigs[0].focus({ preventScroll: true });
  }

  function bindRail(rail) {
    if (!rail || rail.dataset.quietBound === '1') return;
    rail.dataset.quietBound = '1';
    applyTreeChildCaps(rail);
    var doc = rail.ownerDocument;
    var backdrop = getBackdropFor(rail, doc);
    if (backdrop) backdrop.addEventListener('click', function () { setRailOpen(rail, backdrop, false, true); });
    rail.addEventListener('click', function (ev) {
      var moreBtn = ev.target && ev.target.closest ? ev.target.closest('.va-tree-more') : null;
      if (moreBtn) {
        var grp = moreBtn.closest('.va-tree-children, .va-tree-group');
        if (grp) {
          var firstShown = null;
          [].slice.call(grp.children).forEach(function (el) {
            if (el.hidden && el.dataset.treeOverflow === '1') {
              el.hidden = false;
              delete el.dataset.treeOverflow;
              if (!firstShown) firstShown = el;
            }
          });
          moreBtn.remove();
          var focusEl = firstShown && (firstShown.matches('button, a') ? firstShown : firstShown.querySelector('button, a'));
          if (focusEl && typeof focusEl.focus === 'function') focusEl.focus({ preventScroll: true });
        }
        return;
      }
      var caret = ev.target && ev.target.closest ? ev.target.closest('.va-tree-caret') : null;
      if (caret) {
        ev.stopPropagation();
        var exp = caret.getAttribute('aria-expanded') === 'true';
        caret.setAttribute('aria-expanded', exp ? 'false' : 'true');
        var row = caret.closest('.va-tree-row');
        var next = row ? row.nextElementSibling : null;
        var sub = (next && (next.classList.contains('va-tree-group') || next.classList.contains('va-tree-children'))) ? next : null;
        if (sub) sub.hidden = exp;
        return;
      }
      var dest = ev.target && ev.target.closest ? ev.target.closest('.va-tree-dest') : null;
      if (dest) {
        rail.querySelectorAll('.va-tree-dest').forEach(function (d) { d.removeAttribute('aria-current'); d.classList.remove('is-active'); });
        dest.setAttribute('aria-current', 'page');
        dest.classList.add('is-active');
        if (rail.dataset.mode === 'overlay' || (root.innerWidth || 1200) < 1080) setRailOpen(rail, backdrop, false, false);
        if (typeof root.CustomEvent === 'function') {
          rail.dispatchEvent(new root.CustomEvent('quiet:tree-navigate', { bubbles: true, detail: { target: dest.dataset.target || '', label: dest.textContent.trim() } }));
        }
        return;
      }
      if (ev.target && ev.target.closest && ev.target.closest('[data-rail-close]')) setRailOpen(rail, backdrop, false, true);
    });
  }

  function bindModalSheets(scope) {
    if (!scope || !scope.querySelectorAll) return;
    if (typeof HTMLDialogElement !== 'undefined' && !('closedBy' in HTMLDialogElement.prototype)) {
      scope.querySelectorAll('dialog.va-modal-sheet[closedby="any"]').forEach(function (dlg) {
        if (dlg.dataset.quietClosedBy === '1') return;
        dlg.dataset.quietClosedBy = '1';
        var pressedOut = false;
        var outside = function (ev) {
          if (ev.target !== dlg || (ev.button != null && ev.button !== 0)) return false;
          var r = dlg.getBoundingClientRect();
          return ev.clientX < r.left || ev.clientX > r.right || ev.clientY < r.top || ev.clientY > r.bottom;
        };
        dlg.addEventListener('pointerdown', function (ev) { pressedOut = outside(ev); });
        dlg.addEventListener('pointercancel', function () { pressedOut = false; });
        dlg.addEventListener('pointerup', function (ev) { if (pressedOut && outside(ev)) dlg.close(); pressedOut = false; });
      });
    }
  }

  var _docBound = false;
  function boot(container) {
    var scope = container && container.querySelectorAll ? container : (root.document || null);
    if (!scope) return;
    scope.querySelectorAll('[data-period-stepper], .va-period-stepper').forEach(bindStepper);
    scope.querySelectorAll('.va-side-rail').forEach(bindRail);
    bindModalSheets(scope);
    if (!_docBound && root.document) {
      _docBound = true;
      var doc = root.document;
      doc.addEventListener('click', function (ev) {
        var openDlgBtn = ev.target && ev.target.closest ? ev.target.closest('[data-dialog-open]') : null;
        if (openDlgBtn) {
          bindModalSheets(doc);
          doc.querySelectorAll('.va-period-stepper').forEach(function (st) { closePopover(st, false); });
          var dlg = doc.getElementById(openDlgBtn.dataset.dialogOpen);
          if (dlg && typeof dlg.showModal === 'function' && !dlg.open) dlg.showModal();
          return;
        }
        var closeDlgBtn = ev.target && ev.target.closest ? ev.target.closest('[data-dialog-close]') : null;
        if (closeDlgBtn) {
          var parentDlg = closeDlgBtn.closest('dialog');
          if (parentDlg && typeof parentDlg.close === 'function') parentDlg.close();
          return;
        }
        var trig = ev.target && ev.target.closest ? ev.target.closest('[data-rail-trigger]') : null;
        if (trig) {
          var targetId = trig.getAttribute('aria-controls') || trig.dataset.railTrigger;
          var rail = targetId ? doc.getElementById(targetId) : doc.querySelector('.va-side-rail');
          if (rail) setRailOpen(rail, getBackdropFor(rail, doc), !(rail.dataset.open === 'true' || rail.classList.contains('is-open')), false);
        }
        doc.querySelectorAll('.va-period-stepper').forEach(function (st) {
          if (!st.contains(ev.target)) closePopover(st, false);
        });
      });
      doc.addEventListener('keydown', function (ev) {
        if (doc.querySelector('dialog.va-modal-sheet[open], dialog:modal')) return;
        if (ev.key === 'Escape') {
          doc.querySelectorAll('.va-period-stepper').forEach(function (st) { closePopover(st, true); });
          doc.querySelectorAll('.va-side-rail[data-open="true"], .va-side-rail.is-open').forEach(function (r) {
            setRailOpen(r, getBackdropFor(r, doc), false, true);
          });
        }
      });
      var reposRaf = 0;
      var repositionOpen = function () {
        if (reposRaf) return;
        var rafFn = typeof root.requestAnimationFrame === 'function' ? root.requestAnimationFrame.bind(root) : function (fn) { fn(); return 0; };
        reposRaf = rafFn(function () {
          reposRaf = 0;
          doc.querySelectorAll('.va-period-stepper').forEach(function (st) {
            var pop = st.querySelector('.va-preset-popover');
            var trig = st.querySelector('.va-period-trigger');
            if (pop && trig && isPopOpen(pop)) positionPopover(trig, pop);
          });
        });
      };
      if (typeof root.addEventListener === 'function') root.addEventListener('resize', repositionOpen);
      doc.addEventListener('scroll', repositionOpen, true);
    }
  }

  if (root.document) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { boot(root.document); });
    else boot(root.document);
  }

  var stepperApi = { boot: boot, openPopover: openPopover, closePopover: closePopover, applyPresetChoice: applyPresetChoice, positionPopover: positionPopover };
  var railApi = { boot: boot, setRailOpen: setRailOpen, expandActiveBranches: expandActiveBranches, applyTreeChildCaps: applyTreeChildCaps };
  root.QuietPeriodStepper = stepperApi;
  root.QuietRailTree = railApi;
  if (typeof module === 'object' && module.exports) module.exports = { QuietPeriodStepper: stepperApi, QuietRailTree: railApi };
}(typeof window !== 'undefined' ? window : globalThis));
