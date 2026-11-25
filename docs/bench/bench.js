/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 — Evidence Component Library Interactive Controls.
 */
(function (window, document) {
  'use strict';

  function applyTheme(theme) {
    const val = ['white', 'paper', 'dark-paper', 'dark'].includes(theme) ? theme : 'white';
    document.documentElement.setAttribute('data-theme', val);
    const meta = document.querySelector('meta[name="color-scheme"]');
    if (meta) {
      meta.setAttribute('content', val === 'dark' || val === 'dark-paper' ? 'dark' : 'light');
    }
    const sel = document.getElementById('bench-theme-select');
    if (sel) sel.value = val;
    if (window.QuietEChartsAdapter) window.QuietEChartsAdapter.refresh(document);
  }

  function applyMedium(medium) {
    const val = medium === 'm1' ? 'm1' : 'm2';
    document.documentElement.setAttribute('data-medium', val);
    const sel = document.getElementById('bench-medium-select');
    if (sel) sel.value = val;
    document.querySelectorAll('.qe-figure').forEach(function (fig) {
      fig.setAttribute('data-qe-medium', val);
    });
    if (window.QuietEChartsAdapter) window.QuietEChartsAdapter.refresh(document);
  }

  function applyFilters() {
    const modSel = document.getElementById('bench-modality-filter');
    const rigSel = document.getElementById('bench-rigor-filter');
    const modVal = modSel ? modSel.value : 'all';
    const rigVal = rigSel ? rigSel.value : 'all';
    const cards = document.querySelectorAll('.qe-specimen');
    let visible = 0;

    cards.forEach(function (card) {
      const m = card.getAttribute('data-modality') || '';
      const r = card.getAttribute('data-rigor') || '';
      const ok = (modVal === 'all' || m === modVal) && (rigVal === 'all' || r === rigVal);
      if (ok) {
        card.removeAttribute('hidden');
        visible += 1;
      } else {
        card.setAttribute('hidden', '');
      }
    });

    const countEl = document.getElementById('bench-visible-count');
    if (countEl) {
      countEl.textContent = String(visible) + ' of ' + String(cards.length) + ' specimens visible';
    }
  }

  function bindBenchInteractiveControls() {
    function selectTriageRow(root, target, shouldFocus) {
      root.querySelectorAll('.v9-triage-row').forEach(function (r) {
        var on = r === target;
        r.setAttribute('aria-selected', on ? 'true' : 'false');
        r.tabIndex = on ? 0 : -1;
      });
      const box = root.querySelector('[data-triage-detail-box]');
      if (box) box.textContent = target ? (target.dataset.triageDetail || '') : 'No matching items in filter.';
      if (shouldFocus && target && target.focus) target.focus();
    }

    function setTreeFocus(root, target, shouldFocus) {
      root.querySelectorAll('[role="treeitem"]').forEach(function (item) {
        item.tabIndex = item === target ? 0 : -1;
      });
      if (shouldFocus && target && target.focus) target.focus();
    }

    function selectTreeNode(treeNode) {
      const root = treeNode.closest('[data-tree-root]');
      root.querySelectorAll('[role="treeitem"]').forEach(function (b) {
        var on = b === treeNode;
        b.setAttribute('aria-selected', on ? 'true' : 'false');
        b.tabIndex = on ? 0 : -1;
      });
      const ttl = root.querySelector('[data-tree-title]');
      const bdg = root.querySelector('[data-tree-badge]');
      const sla = root.querySelector('[data-tree-sla]');
      const note = root.querySelector('[data-tree-note]');
      if (ttl) ttl.textContent = treeNode.dataset.nodeTitle || '';
      if (bdg) {
        bdg.dataset.state = treeNode.dataset.nodeState || 'nominal';
        bdg.textContent = (treeNode.dataset.nodeState || 'nominal').toUpperCase();
      }
      if (sla) sla.textContent = 'SLO: ' + (treeNode.dataset.nodeSla || '');
      if (note) note.textContent = treeNode.dataset.nodeNote || '';
    }

    function toggleTreeBranch(toggleBtn, forceOpen) {
      const li = toggleBtn.parentElement;
      const sub = li && li.querySelector(':scope > [role="group"]');
      const isOpen = toggleBtn.getAttribute('aria-expanded') === 'true';
      const nextOpen = typeof forceOpen === 'boolean' ? forceOpen : !isOpen;
      toggleBtn.setAttribute('aria-expanded', nextOpen ? 'true' : 'false');
      if (sub) sub.hidden = !nextOpen;
      return nextOpen;
    }

    document.addEventListener('click', function (ev) {
      const chip = ev.target.closest('.v9-demo-chips .va-pill[data-variant="chip"]');
      if (chip) {
        const grp = chip.closest('.v9-demo-chips');
        grp.querySelectorAll('.va-pill[data-variant="chip"]').forEach(function (b) {
          b.setAttribute('aria-pressed', b === chip ? 'true' : 'false');
        });
        const out = grp.querySelector('[data-chip-readout]');
        if (out) out.textContent = 'Active filter: ' + chip.textContent.trim();
        return;
      }
      const armBtn = ev.target.closest('[data-guard-arm]');
      if (armBtn) {
        const pad = armBtn.closest('[data-guard-pad]');
        const cfm = pad && pad.querySelector('[data-guard-confirm]');
        const can = pad && pad.querySelector('[data-guard-cancel]');
        const st = pad && pad.querySelector('[data-guard-state]');
        const disarm = armBtn.getAttribute('aria-expanded') === 'true';
        armBtn.classList.toggle('is-armed', !disarm);
        armBtn.setAttribute('aria-expanded', disarm ? 'false' : 'true');
        if (cfm) cfm.hidden = disarm;
        if (can) can.hidden = disarm;
        if (st) {
          st.dataset.state = disarm ? 'nominal' : 'warn';
          st.textContent = disarm ? 'SAFE · LOCKED' : 'ARMED · CONFIRM';
        }
        return;
      }
      const cancelBtn = ev.target.closest('[data-guard-cancel], [data-guard-confirm]');
      if (cancelBtn) {
        const pad = cancelBtn.closest('[data-guard-pad]');
        const arm = pad && pad.querySelector('[data-guard-arm]');
        const cfm = pad && pad.querySelector('[data-guard-confirm]');
        const can = pad && pad.querySelector('[data-guard-cancel]');
        const st = pad && pad.querySelector('[data-guard-state]');
        const executed = cancelBtn.hasAttribute('data-guard-confirm');
        if (arm) { arm.classList.remove('is-armed'); arm.setAttribute('aria-expanded', 'false'); }
        if (cfm) cfm.hidden = true;
        if (can) can.hidden = true;
        if (st) {
          st.dataset.state = executed ? 'fault' : 'nominal';
          st.textContent = executed ? 'EXECUTED · LATCHED' : 'SAFE · LOCKED';
        }
        if (arm && arm.focus) arm.focus();
        return;
      }
      const seg = ev.target.closest('.v9-seg-btn');
      if (seg) {
        seg.closest('.v9-seg-group').querySelectorAll('.v9-seg-btn').forEach(function (b) {
          b.setAttribute('aria-pressed', b === seg ? 'true' : 'false');
        });
        return;
      }
      const stepBtn = ev.target.closest('[data-step-delta]');
      if (stepBtn) {
        const wrap = stepBtn.closest('[data-stepper]');
        const cur = parseFloat(wrap.dataset.val || '21.0');
        const next = Math.min(parseFloat(wrap.dataset.max || '26'), Math.max(parseFloat(wrap.dataset.min || '16'), cur + parseFloat(stepBtn.dataset.stepDelta || '0')));
        wrap.dataset.val = next.toFixed(1);
        const disp = wrap.querySelector('[data-step-display]');
        if (disp) disp.textContent = next.toFixed(1) + ' °C';
        return;
      }
      const tFilter = ev.target.closest('[data-triage-filter]');
      if (tFilter) {
        const root = tFilter.closest('[data-triage-root]');
        const want = tFilter.dataset.triageFilter;
        root.querySelectorAll('[data-triage-filter]').forEach(function (b) {
          b.setAttribute('aria-pressed', b === tFilter ? 'true' : 'false');
        });
        const visible = [];
        root.querySelectorAll('.v9-triage-row').forEach(function (r) {
          r.hidden = want !== 'all' && r.dataset.triageState !== want;
          if (!r.hidden) visible.push(r);
        });
        const curSel = root.querySelector('.v9-triage-row[aria-selected="true"]');
        if (!curSel || curSel.hidden) selectTriageRow(root, visible[0] || null, false);
        return;
      }
      const tRow = ev.target.closest('.v9-triage-row');
      if (tRow) {
        selectTriageRow(tRow.closest('[data-triage-root]'), tRow, false);
        return;
      }
      const treeToggle = ev.target.closest('[data-tree-toggle]');
      if (treeToggle) {
        toggleTreeBranch(treeToggle);
        setTreeFocus(treeToggle.closest('[data-tree-root]'), treeToggle, false);
        return;
      }
      const treeNode = ev.target.closest('[data-tree-node]');
      if (treeNode) selectTreeNode(treeNode);
    });

    document.addEventListener('keydown', function (ev) {
      const opt = ev.target && ev.target.closest ? ev.target.closest('[data-triage-root] .v9-triage-row[role="option"]') : null;
      if (opt) {
        const root = opt.closest('[data-triage-root]');
        const vis = Array.prototype.slice.call(root.querySelectorAll('.v9-triage-row')).filter(function (r) { return !r.hidden; });
        const idx = vis.indexOf(opt);
        if (idx < 0 || !vis.length) return;
        var nextIdx = -1;
        if (ev.key === 'ArrowDown') nextIdx = Math.min(vis.length - 1, idx + 1);
        else if (ev.key === 'ArrowUp') nextIdx = Math.max(0, idx - 1);
        else if (ev.key === 'Home') nextIdx = 0;
        else if (ev.key === 'End') nextIdx = vis.length - 1;
        if (nextIdx >= 0) {
          ev.preventDefault();
          selectTriageRow(root, vis[nextIdx], true);
        }
        return;
      }
      const ti = ev.target && ev.target.closest ? ev.target.closest('[data-tree-root] [role="treeitem"]') : null;
      if (!ti) return;
      const root = ti.closest('[data-tree-root]');
      const visItems = Array.prototype.slice.call(root.querySelectorAll('[role="treeitem"]')).filter(function (el) {
        const grp = el.closest('[role="group"]');
        return !grp || !grp.hidden;
      });
      const idx = visItems.indexOf(ti);
      if (ev.key === 'ArrowDown' && idx >= 0 && idx + 1 < visItems.length) {
        ev.preventDefault(); setTreeFocus(root, visItems[idx + 1], true);
      } else if (ev.key === 'ArrowUp' && idx > 0) {
        ev.preventDefault(); setTreeFocus(root, visItems[idx - 1], true);
      } else if (ev.key === 'Home' && visItems.length) {
        ev.preventDefault(); setTreeFocus(root, visItems[0], true);
      } else if (ev.key === 'End' && visItems.length) {
        ev.preventDefault(); setTreeFocus(root, visItems[visItems.length - 1], true);
      } else if (ev.key === 'ArrowRight' && ti.hasAttribute('aria-expanded')) {
        ev.preventDefault();
        if (ti.getAttribute('aria-expanded') === 'false') toggleTreeBranch(ti, true);
        else if (idx >= 0 && idx + 1 < visItems.length) setTreeFocus(root, visItems[idx + 1], true);
      } else if (ev.key === 'ArrowLeft') {
        ev.preventDefault();
        if (ti.hasAttribute('aria-expanded') && ti.getAttribute('aria-expanded') === 'true') {
          toggleTreeBranch(ti, false);
        } else {
          const parentLi = ti.closest('[role="group"]') && ti.closest('[role="group"]').parentElement;
          const parentToggle = parentLi && parentLi.querySelector('[data-tree-toggle]');
          if (parentToggle) setTreeFocus(root, parentToggle, true);
        }
      }
    });

    document.addEventListener('click', function (ev) {
      const tbBtn = ev.target && ev.target.closest ? ev.target.closest('[data-joined-toolbar] .va-tb-btn') : null;
      if (tbBtn) {
        const bar = tbBtn.closest('[data-joined-toolbar]');
        const status = bar && bar.parentElement ? bar.parentElement.querySelector('[data-tb-status]') : null;
        if (tbBtn.dataset.tbGroup) {
          bar.querySelectorAll('.va-tb-btn[data-tb-group="' + tbBtn.dataset.tbGroup + '"]').forEach(function (b) {
            b.setAttribute('aria-pressed', b === tbBtn ? 'true' : 'false');
          });
        } else if (tbBtn.dataset.tbAction === 'reset') {
          bar.querySelectorAll('.va-tb-btn[data-tb-group]').forEach(function (b) {
            const def = b.dataset.tbVal === '24h' || b.dataset.tbVal === 'all';
            b.setAttribute('aria-pressed', def ? 'true' : 'false');
          });
        }
        if (status) {
          const wAct = bar.querySelector('.va-tb-btn[data-tb-group="window"][aria-pressed="true"]');
          const sAct = bar.querySelector('.va-tb-btn[data-tb-group="scope"][aria-pressed="true"]');
          const extra = tbBtn.dataset.tbAction === 'export' ? ' · Export CSV queued (real endpoint)' : '';
          status.textContent = 'Window: ' + (wAct ? wAct.textContent.trim() : '24h') + ' · Scope: ' + (sAct ? sAct.textContent.trim() : 'All Runs') + extra;
        }
        return;
      }
      const kpiBtn = ev.target && ev.target.closest ? ev.target.closest('[data-kpi-toggle-state]') : null;
      if (kpiBtn) {
        const root = kpiBtn.closest('[data-kpi-demo-wrap]');
        const warmup = kpiBtn.getAttribute('aria-pressed') !== 'true';
        kpiBtn.setAttribute('aria-pressed', warmup ? 'true' : 'false');
        const note = root ? root.querySelector('[data-kpi-warmup-note]') : null;
        const valEl = root ? root.querySelector('[data-kpi-warmup-val]') : null;
        const fillEl = root ? root.querySelector('[data-kpi-warmup-fill]') : null;
        const barEl = root ? root.querySelector('[data-kpi-warmup-bar]') : null;
        if (warmup) {
          if (valEl) valEl.textContent = '3 / 50 calls';
          if (fillEl) fillEl.style.inlineSize = '6%';
          if (barEl) barEl.setAttribute('aria-valuenow', '6');
          if (note) note.textContent = 'Warming up — 3 samples collected (uptime 12m)';
        } else {
          if (valEl) valEl.textContent = '36 / 50 calls';
          if (fillEl) fillEl.style.inlineSize = '72%';
          if (barEl) barEl.setAttribute('aria-valuenow', '72');
          if (note) note.textContent = 'Steady window — 36 / 50 samples (24h)';
        }
      }
      const scReset = ev.target && ev.target.closest ? ev.target.closest('[data-scope-reset]') : null;
      if (scReset) {
        const chip = scReset.closest('.va-scope-chip');
        const lbl = chip ? chip.querySelector('[data-scope-label]') : null;
        if (chip && lbl) {
          const allMode = chip.dataset.level !== 'all';
          chip.dataset.level = allMode ? 'all' : 'entity';
          lbl.textContent = allMode ? 'All Substations' : 'Substation B · Transformer 02';
          scReset.hidden = allMode;
        }
      }
    });
    document.addEventListener('quiet:period-change', function (ev) {
      const st = ev.target && ev.target.closest ? ev.target.closest('[data-stepper-demo]') : null;
      const msg = st ? st.querySelector('[data-stepper-status]') : null;
      const d = (ev && ev.detail) || {};
      if (msg && d.preset) {
        const bin = d.preset === 'r52w' ? '1w' : '1d';
        msg.textContent = 'Active window: ' + (d.label || d.preset) + (d.span ? ' · ' + d.span : '') + ' · Adaptive bin: ' + bin;
      }
    });
    const s44 = document.querySelector('[data-s44-root]');
    if (s44) {
      const form = s44.querySelector('[data-s44-form]'), inp = s44.querySelector('#s44-threshold-input');
      const errEl = s44.querySelector('#s44-threshold-err'), gateEl = s44.querySelector('[data-s44-gate-reason]');
      const pill = s44.querySelector('[data-s44-rule-pill]'), toast = s44.querySelector('[data-s44-toast]');
      let prev = { text: 'Active · 250 ms', state: 'nominal' }, timer = null;
      const syncInp = function (showErr) {
        const val = Number(inp.value), ok = inp.value.trim() !== '' && Number.isFinite(val) && val >= 10 && val <= 5000;
        if (!ok && !showErr) return false;
        inp.setAttribute('aria-invalid', ok ? 'false' : 'true');
        inp.setAttribute('aria-describedby', ok ? 's44-threshold-hint' : 's44-threshold-hint s44-threshold-err');
        if (errEl) errEl.hidden = ok;
        if (gateEl) {
          gateEl.dataset.state = ok ? 'nominal' : 'fault';
          gateEl.textContent = ok ? ('Ready: active threshold ' + Math.round(val) + ' ms can be saved or archived safely.') : 'Blocked: enter 10–5000 ms to enable saving.';
        }
        return ok;
      };
      const armTimer = function () {
        clearTimeout(timer);
        timer = setTimeout(function () { if (toast && !toast.matches(':hover, :focus-within')) toast.hidden = true; else if (toast && !toast.hidden) armTimer(); }, 7000);
      };
      if (inp) {
        inp.addEventListener('blur', function () { syncInp(true); });
        inp.addEventListener('input', function () { if (inp.getAttribute('aria-invalid') === 'true') syncInp(false); });
      }
      if (form) form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        if (!syncInp(true)) { inp.focus(); return; }
        clearTimeout(timer); if (toast) toast.hidden = true;
        if (pill) { pill.dataset.state = 'nominal'; pill.textContent = 'Active · ' + Math.round(Number(inp.value)) + ' ms'; }
        if (gateEl) { gateEl.dataset.state = 'nominal'; gateEl.textContent = 'Saved: ' + Math.round(Number(inp.value)) + ' ms threshold active.'; }
      });
      s44.addEventListener('click', function (ev) {
        const t = ev.target && ev.target.closest ? ev.target : null;
        if (!t) return;
        if (t.closest('[data-s44-archive]') && pill && toast) {
          if (pill.dataset.state !== 'warn') prev = { text: pill.textContent, state: pill.dataset.state || 'nominal' };
          pill.dataset.state = 'warn'; pill.textContent = 'Archived · Pending'; toast.hidden = false; armTimer();
          if (gateEl) { gateEl.dataset.state = 'warn'; gateEl.textContent = 'Archived rule paused — use Undo within 7 s to restore.'; }
        } else if (t.closest('[data-s44-undo]') && pill && toast) {
          clearTimeout(timer); toast.hidden = true; pill.dataset.state = prev.state; pill.textContent = prev.text;
          if (gateEl) { gateEl.dataset.state = 'nominal'; gateEl.textContent = 'Restored: ' + prev.text + ' active.'; }
        } else if (t.closest('[data-s44-toast-dismiss]') && toast) {
          clearTimeout(timer); toast.hidden = true;
        } else if (t.closest('[data-s44-tabs] .va-tab')) {
          const tab = t.closest('[data-s44-tabs] .va-tab'), kind = tab.dataset.s44Kind;
          s44.querySelectorAll('[data-s44-tabs] .va-tab').forEach(function (b) { b.setAttribute('aria-selected', b === tab ? 'true' : 'false'); });
          s44.querySelectorAll('[data-s44-panel]').forEach(function (p) { p.hidden = p.dataset.s44Panel !== kind; });
        } else if (t.closest('[data-s44-clear-filters]') || t.closest('[data-s44-reapply-filters]')) {
          const clr = !!t.closest('[data-s44-clear-filters]');
          s44.querySelector('[data-s44-filtered-title]').textContent = clr ? 'Filters cleared — 48 runs restored' : '0 runs match "region:ap-east · status:fault"';
          s44.querySelector('[data-s44-filtered-copy]').textContent = clr ? 'All 48 recorded spans in the active window are now visible.' : 'Two active filters exclude all 48 recorded spans in this window.';
          s44.querySelector('[data-s44-clear-filters]').hidden = clr;
          s44.querySelector('[data-s44-reapply-filters]').hidden = !clr;
        } else if (t.closest('[data-s44-connect]')) t.closest('[data-s44-connect]').textContent = 'Collector probe queued';
        else if (t.closest('[data-s44-retry]')) t.closest('[data-s44-retry]').textContent = 'Sync retried (still offline)';
      });
    }
  }

  function bootBench() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('embed') === '1') {
      document.documentElement.setAttribute('data-bench-embed', '1');
    }
    const qTheme = params.get('theme');
    if (qTheme) {
      applyTheme(qTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      applyTheme('dark');
    }
    const qDen = params.get('density');
    if (['d1', 'd2', 'd3', 'd4'].includes(qDen)) document.documentElement.dataset.density = qDen;
    const qCor = params.get('corners');
    if (['auto', 'sharp', 'subtle', 'rounded', 'soft'].includes(qCor)) document.documentElement.dataset.corners = qCor;
    if (params.get('medium')) applyMedium(params.get('medium'));

    window.addEventListener('message', function (ev) {
      const msg = ev && ev.data;
      if (!msg || msg.type !== 'quiet-ui-sync') return;
      if (msg.theme) applyTheme(msg.theme);
      if (msg.medium) applyMedium(msg.medium === 'auto' ? 'm2' : msg.medium);
      if (['d1', 'd2', 'd3', 'd4'].includes(msg.density)) document.documentElement.dataset.density = msg.density;
      if (['auto', 'sharp', 'subtle', 'rounded', 'soft'].includes(msg.corners)) document.documentElement.dataset.corners = msg.corners;
    });

    const themeSel = document.getElementById('bench-theme-select');
    if (themeSel) themeSel.addEventListener('change', function () { applyTheme(themeSel.value); });
    const medSel = document.getElementById('bench-medium-select');
    if (medSel) medSel.addEventListener('change', function () { applyMedium(medSel.value); });
    const modSel = document.getElementById('bench-modality-filter');
    if (modSel) modSel.addEventListener('change', applyFilters);
    const rigSel = document.getElementById('bench-rigor-filter');
    if (rigSel) rigSel.addEventListener('change', applyFilters);

    if (params.get('modality') && modSel) modSel.value = params.get('modality');
    if (params.get('rigor') && rigSel) rigSel.value = params.get('rigor');
    bindBenchInteractiveControls();
    applyFilters();
    if (window.QuietEChartsAdapter) window.QuietEChartsAdapter.boot(document);
    if (window.QuietWave2Runtime) window.QuietWave2Runtime.boot(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootBench);
  } else {
    bootBench();
  }

  window.QuietEvidenceBench = {
    applyTheme: applyTheme,
    applyMedium: applyMedium,
    applyFilters: applyFilters,
  };
})(window, document);
