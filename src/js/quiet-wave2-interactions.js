/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.7.0 Wave 2 — Client Runtime for v23/v24/v25/v26 & Specimens 51-53 */
(function (global) {
  'use strict';

  function sevState(sev) {
    if (sev === 'CRITICAL' || sev === 'BREAKING') return 'fault';
    if (sev === 'WARN' || sev === 'MODERATE') return 'warn';
    return 'nominal';
  }

  function wireV23(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var activeFilter = 'all';
    var timerId = 0;
    var filterBtns = scope.querySelectorAll('[data-v23-filter]');
    var ctxCheck = scope.querySelector('[data-v23-context]');
    var rows = scope.querySelectorAll('.v23-row');
    var hdrPill = scope.querySelector('#v23-header-status-pill, [data-v23-pill]');
    var gateStatus = scope.querySelector('[data-v23-gate-status]');
    var stageBtn = scope.querySelector('[data-v23-stage]');
    var confirmBtn = scope.querySelector('[data-v23-confirm]');
    var revertBtn = scope.querySelector('[data-v23-revert]');
    var toast = scope.querySelector('[data-v23-toast]');
    var toastRevert = scope.querySelector('[data-v23-toast-revert]');

    function applyRows() {
      var showCtx = !!(ctxCheck && ctxCheck.checked);
      rows.forEach(function (tr) {
        var cat = tr.getAttribute('data-v23-cat') || '';
        var vis = cat === 'context' ? showCtx : (activeFilter === 'all' || cat === activeFilter);
        tr.hidden = !vis;
      });
    }

    function clearUndoTimer() {
      if (timerId) {
        global.clearTimeout(timerId);
        timerId = 0;
      }
    }

    function armUndoTimer() {
      clearUndoTimer();
      timerId = global.setTimeout(function () {
        timerId = 0;
        if (toast && (!toast.matches || !toast.matches(':hover, :focus-within'))) toast.hidden = true;
      }, 7500);
    }

    function setPhase(phase) {
      scope.setAttribute('data-v23-phase', phase);
      clearUndoTimer();
      if (phase === 'baseline') {
        if (stageBtn) stageBtn.disabled = false;
        if (confirmBtn) confirmBtn.disabled = true;
        if (revertBtn) revertBtn.disabled = true;
        if (toast) toast.hidden = true;
        if (hdrPill) { hdrPill.setAttribute('data-state', 'nominal'); hdrPill.textContent = 'BASELINE r41'; }
        if (gateStatus) gateStatus.textContent = 'Baseline r41 active on 14/14 clusters — snapshot revert verified.';
      } else if (phase === 'staged') {
        if (stageBtn) stageBtn.disabled = true;
        if (confirmBtn) confirmBtn.disabled = false;
        if (revertBtn) revertBtn.disabled = false;
        if (toast) toast.hidden = true;
        if (hdrPill) { hdrPill.setAttribute('data-state', 'warn'); hdrPill.textContent = 'CANARY r42 STAGED'; }
        if (gateStatus) gateStatus.textContent = 'Candidate r42 staged on 2/14 canary clusters (14.3% traffic · 30 min soak running).';
      } else {
        if (stageBtn) stageBtn.disabled = true;
        if (confirmBtn) confirmBtn.disabled = true;
        if (revertBtn) revertBtn.disabled = false;
        if (toast) { toast.hidden = false; armUndoTimer(); }
        if (hdrPill) { hdrPill.setAttribute('data-state', 'nominal'); hdrPill.textContent = 'PROMOTED r42'; }
        if (gateStatus) gateStatus.textContent = 'Candidate r42 promoted across 14/14 clusters (1-click r41 revert ready).';
      }
    }

    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activeFilter = btn.getAttribute('data-v23-filter') || 'all';
        filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        applyRows();
      });
    });
    if (ctxCheck) ctxCheck.addEventListener('change', applyRows);
    if (stageBtn) stageBtn.addEventListener('click', function () { setPhase('staged'); });
    if (confirmBtn) confirmBtn.addEventListener('click', function () { setPhase('promoted'); });
    if (revertBtn) revertBtn.addEventListener('click', function () { setPhase('baseline'); });
    if (toastRevert) toastRevert.addEventListener('click', function () { setPhase('baseline'); });
    if (toast) {
      var maybeArm = function () {
        if (!toast.hidden && (!toast.matches || !toast.matches(':hover, :focus-within'))) armUndoTimer();
      };
      toast.addEventListener('mouseenter', clearUndoTimer);
      toast.addEventListener('focusin', clearUndoTimer);
      toast.addEventListener('mouseleave', maybeArm);
      toast.addEventListener('focusout', maybeArm);
    }
    applyRows();
  }

  function wireV24(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var activeCat = 'all';
    var activeBucket = null;
    var filterBtns = scope.querySelectorAll('[data-v24-filter]');
    var bucketBtns = scope.querySelectorAll('[data-v24-bucket]');
    var searchInput = scope.querySelector('[data-v24-search]');
    var rows = Array.prototype.slice.call(scope.querySelectorAll('.v24-row'));
    var tableEl = scope.querySelector('[data-v24-table]');
    var emptyEl = scope.querySelector('[data-v24-empty]');
    var clearBtn = scope.querySelector('[data-v24-clear]');
    var countEl = scope.querySelector('[data-v24-visible-count]');
    var copyBtn = scope.querySelector('[data-v24-copy]');
    var copyOut = scope.querySelector('[data-v24-copy-status]');

    function selectRow(row) {
      if (!row) return;
      rows.forEach(function (r) { r.setAttribute('aria-selected', r === row ? 'true' : 'false'); });
      var map = {
        '[data-insp-ts]': row.getAttribute('data-ev-ts') || '',
        '[data-insp-svc]': row.getAttribute('data-ev-svc') || '',
        '[data-insp-span]': row.getAttribute('data-ev-span') || '',
        '[data-insp-trace]': row.getAttribute('data-ev-trace') || '',
        '[data-insp-caller]': row.getAttribute('data-ev-caller') || '',
        '[data-insp-code]': (row.getAttribute('data-ev-code') || '') + ' · ' + (row.getAttribute('data-ev-dur') || ''),
        '[data-insp-msg]': row.getAttribute('data-ev-msg') || '',
      };
      Object.keys(map).forEach(function (sel) {
        var el = scope.querySelector(sel);
        if (el) el.textContent = map[sel];
      });
      var sevPill = scope.querySelector('[data-insp-sev]');
      if (sevPill) {
        var sev = row.getAttribute('data-ev-sev') || 'NOMINAL';
        sevPill.textContent = sev;
        sevPill.setAttribute('data-state', sevState(sev));
      }
      if (copyOut) copyOut.textContent = '';
    }

    function applyFilters() {
      var q = searchInput ? searchInput.value.trim().toLowerCase() : '';
      var visibleRows = [];
      rows.forEach(function (tr) {
        var cat = tr.getAttribute('data-v24-cat') || '';
        var b = tr.getAttribute('data-v24-bucket') || '';
        var hay = tr.getAttribute('data-v24-search') || '';
        var okCat = activeCat === 'all' || cat === activeCat;
        var okB = activeBucket === null || b === String(activeBucket);
        var okQ = !q || hay.indexOf(q) !== -1;
        var vis = okCat && okB && okQ;
        tr.hidden = !vis;
        if (vis) visibleRows.push(tr);
      });
      if (countEl) countEl.textContent = 'Showing ' + visibleRows.length + ' / ' + rows.length + ' events';
      if (tableEl) tableEl.hidden = visibleRows.length === 0;
      if (emptyEl) emptyEl.hidden = visibleRows.length !== 0;
      if (visibleRows.length > 0 && visibleRows.every(function (r) { return r.getAttribute('aria-selected') !== 'true'; })) {
        selectRow(visibleRows[0]);
      }
    }

    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activeCat = btn.getAttribute('data-v24-filter') || 'all';
        if (activeCat === 'all') {
          activeBucket = null;
          bucketBtns.forEach(function (g) { g.setAttribute('aria-pressed', 'false'); });
        }
        filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        applyFilters();
      });
    });
    bucketBtns.forEach(function (grp) {
      function toggleB() {
        var b = grp.getAttribute('data-v24-bucket');
        activeBucket = activeBucket === b ? null : b;
        bucketBtns.forEach(function (g) { g.setAttribute('aria-pressed', g.getAttribute('data-v24-bucket') === activeBucket ? 'true' : 'false'); });
        applyFilters();
      }
      grp.addEventListener('click', toggleB);
      grp.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggleB(); } });
    });
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        activeCat = 'all';
        activeBucket = null;
        if (searchInput) searchInput.value = '';
        filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v24-filter') === 'all' ? 'true' : 'false'); });
        bucketBtns.forEach(function (g) { g.setAttribute('aria-pressed', 'false'); });
        applyFilters();
      });
    }
    rows.forEach(function (row) {
      row.addEventListener('click', function () { selectRow(row); });
      row.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          selectRow(row);
        } else if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
          ev.preventDefault();
          var vis = rows.filter(function (r) { return !r.hidden; });
          var idx = vis.indexOf(row);
          var next = vis[idx + (ev.key === 'ArrowDown' ? 1 : -1)];
          if (next) { next.focus(); selectRow(next); }
        }
      });
    });
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        var active = scope.querySelector('.v24-row[aria-selected="true"]') || rows[0];
        if (!active) return;
        var summary = [
          active.getAttribute('data-ev-ts'), active.getAttribute('data-ev-svc'),
          active.getAttribute('data-ev-span'), active.getAttribute('data-ev-trace'),
          active.getAttribute('data-ev-code'), active.getAttribute('data-ev-msg'),
        ].join(' | ');
        if (global.navigator && global.navigator.clipboard && global.navigator.clipboard.writeText) {
          global.navigator.clipboard.writeText(summary).catch(function () {});
        }
        if (copyOut) copyOut.textContent = 'Copied ' + (active.getAttribute('data-ev-trace') || 'trace');
      });
    }
  }

  function wireV25(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var btns = scope.querySelectorAll('[data-v25-span]');
    var targets = scope.querySelectorAll('.w2-span-node, .w2-span-mark, .w2-span-row');
    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var grp = btn.getAttribute('data-v25-span') || 'all';
        btns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        targets.forEach(function (el) {
          var mine = el.getAttribute('data-span-group') === grp;
          if (grp === 'all') {
            el.removeAttribute('data-span-dim');
            el.removeAttribute('data-span-hot');
          } else {
            el.setAttribute('data-span-dim', mine ? '0' : '1');
            el.setAttribute('data-span-hot', mine ? '1' : '0');
          }
        });
      });
    });
  }

  function computeV26(gPct, cPct, floorMo) {
    var g = gPct / 100.0, c = cPct / 100.0, upB = (250.0 + 275.0 * c) / 1000.0;
    var multB = c * 0.56 + (1.0 - c) * 1.05, ptsA = [0.0], ptsB = [upB], ptsC = [2.10];
    var cumA = 0.0, cumB = upB, cumC = 2.10, cross = null, crossC = null;
    for (var m = 1; m <= 36; m += 1) {
      var paygo = (110.0 * Math.pow(1.0 + g, (m - 1) / 12.0)) / 1000.0;
      var colo = (64.0 + 12.0 * Math.pow(1.0 + 0.5 * g, (m - 1) / 12.0)) / 1000.0;
      cumA += paygo; cumB += paygo * multB; cumC += colo;
      ptsA.push(cumA); ptsB.push(cumB); ptsC.push(cumC);
      if (cross === null && cumB <= cumA) cross = m;
      if (crossC === null && cumC <= cumA) crossC = m;
    }
    var runA = Math.max(14, Math.round(38 - g * 18)), runB = Math.max(16, Math.round(36 - c * 4 - g * 10)), runC = Math.max(10, Math.round(22 - g * 12));
    var totalA = Math.round(cumA * 100) / 100, totalB = Math.round(cumB * 100) / 100, totalC = Math.round(cumC * 100) / 100;
    var feasA = runA >= floorMo, feasB = runB >= floorMo, feasC = runC >= floorMo;
    var cands = [
      { name: 'Option B Hybrid', tot: totalB, ok: feasB },
      { name: 'Option A PayGo', tot: totalA, ok: feasA },
      { name: 'Option C Colo', tot: totalC, ok: feasC },
    ].filter(function (x) { return x.ok; }).sort(function (x, y) { return x.tot - y.tot; });
    var winner = cands.length ? cands[0].name : 'None (Runway Blocked)';
    var recState = !cands.length ? 'fault' : (cands[0].tot > 5.2 ? 'warn' : 'nominal');
    return {
      ptsA: ptsA, ptsB: ptsB, ptsC: ptsC, upB: Math.round(upB * 100) / 100,
      totalA: totalA, totalB: totalB, totalC: totalC,
      savings: Math.round((totalA - totalB) * 100) / 100, savingsC: Math.round((totalA - totalC) * 100) / 100,
      crossover: cross, crossoverC: crossC, runA: runA, runB: runB, runC: runC,
      feasA: feasA, feasB: feasB, feasC: feasC, winner: winner, recState: recState,
      yMax: Math.max(totalA, totalB, totalC) > 6.2 ? 8.0 : 6.5,
    };
  }

  function polyPath(vals, yMax) {
    return 'M ' + vals.map(function (v, m) {
      return (74.0 + (m / 36.0) * 724.0).toFixed(1) + ' ' + (232.0 - (Math.min(yMax, v) / yMax) * 194.0).toFixed(1);
    }).join(' L ');
  }

  function setAttrs(el, attrs) {
    if (el) Object.keys(attrs).forEach(function (k) { el.setAttribute(k, String(attrs[k])); });
  }

  function renderV26YGrid(yGrid, yMax) {
    if (!yGrid || !yGrid.ownerDocument) return;
    while (yGrid.firstChild) yGrid.removeChild(yGrid.firstChild);
    var ns = 'http://www.w3.org/2000/svg';
    (yMax > 7.0 ? [0.0, 2.0, 4.0, 6.0, 8.0] : [0.0, 2.0, 4.0, 6.0]).forEach(function (v) {
      var yy = 232.0 - (v / yMax) * 194.0;
      var ln = yGrid.ownerDocument.createElementNS(ns, 'line');
      setAttrs(ln, { x1: 74, y1: yy.toFixed(1), x2: 798, y2: yy.toFixed(1), stroke: 'var(--border-subtle)', 'stroke-dasharray': '2 3' });
      var tx = yGrid.ownerDocument.createElementNS(ns, 'text');
      setAttrs(tx, { x: 66, y: (yy + 4).toFixed(1), 'text-anchor': 'end', 'font-size': '11.5', fill: 'var(--text-muted)' });
      tx.textContent = '$' + v.toFixed(1) + 'M';
      yGrid.appendChild(ln); yGrid.appendChild(tx);
    });
  }

  function fmtSav(diff) {
    return diff >= 0 ? '$' + diff.toFixed(2) + 'M saved' : '+$' + Math.abs(diff).toFixed(2) + 'M cost';
  }

  function wireV26(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var gEl = scope.querySelector('[data-v26-input="growth"]');
    var cEl = scope.querySelector('[data-v26-input="commit"]');
    var rEl = scope.querySelector('[data-v26-input="runway"]');
    if (!gEl || !cEl || !rEl) return;
    var dispLbl = function (optName, feas, winner) { return !feas ? 'RUNWAY BLOCKED' : (winner === optName ? 'RECOMMENDED' : 'VIABLE'); };

    function update() {
      [gEl, cEl, rEl].forEach(function (inp) {
        var mn = Number(inp.min || 0), mx = Number(inp.max || 100), val = Number(inp.value || 0);
        inp.style.setProperty('--pct', (mx > mn ? ((val - mn) / (mx - mn)) * 100 : 50).toFixed(1) + '%');
      });
      var g = Number(gEl.value), c = Number(cEl.value), r = Number(rEl.value);
      var outs = { growth: g + '%', commit: c + '%', runway: r + ' mo' };
      Object.keys(outs).forEach(function (k) { var el = scope.querySelector('[data-v26-out="' + k + '"]'); if (el) el.textContent = outs[k]; });

      var mod = computeV26(g, c, r);
      var cbTxt = mod.crossover !== null ? 'Month ' + mod.crossover : 'No crossover';
      var kpiMap = {
        winner: mod.winner,
        savings: mod.savings >= 0 ? 'Saves $' + mod.savings.toFixed(2) + 'M vs PayGo' : '+$' + Math.abs(mod.savings).toFixed(2) + 'M vs PayGo',
        crossover: cbTxt,
        cross_sub: mod.crossover !== null ? 'Option B crosses below Option A' : 'Option B stays above Option A',
        total_b: '$' + mod.totalB.toFixed(2) + 'M',
        runway_b: mod.runB + ' mo',
        runway_note: 'Option C ' + mod.runC + ' mo vs ' + r + ' mo floor',
      };
      Object.keys(kpiMap).forEach(function (k) { var el = scope.querySelector('[data-v26-kpi="' + k + '"]'); if (el) el.textContent = kpiMap[k]; });
      var badge = scope.querySelector('[data-v26-rec-badge]');
      if (badge) {
        badge.setAttribute('data-state', mod.recState);
        badge.textContent = mod.recState === 'fault' ? 'RUNWAY GATE BLOCKED' : 'RECOMMENDED: ' + mod.winner.toUpperCase();
      }

      renderV26YGrid(scope.querySelector('[data-v26-ygrid]'), mod.yMax);
      var yCeil = 232.0 - (5.2 / mod.yMax) * 194.0;
      setAttrs(scope.querySelector('[data-v26-ceil-line]'), { y1: yCeil.toFixed(1), y2: yCeil.toFixed(1) });
      setAttrs(scope.querySelector('[data-v26-ceil-bg]'), { y: (yCeil - 18).toFixed(1) });
      setAttrs(scope.querySelector('[data-v26-ceil-lbl]'), { y: (yCeil - 6).toFixed(1) });
      setAttrs(scope.querySelector('[data-v26-path="a"]'), { d: polyPath(mod.ptsA, mod.yMax) });
      setAttrs(scope.querySelector('[data-v26-path="b"]'), { d: polyPath(mod.ptsB, mod.yMax) });
      setAttrs(scope.querySelector('[data-v26-path="c"]'), { d: polyPath(mod.ptsC, mod.yMax) });

      var cl = scope.querySelector('[data-v26-cross-line]'), cd = scope.querySelector('[data-v26-cross-dot]');
      var cb = scope.querySelector('[data-v26-cross-bg]'), ct = scope.querySelector('[data-v26-cross-lbl]');
      if (mod.crossover === null) {
        [cl, cd, cb, ct].forEach(function (n) { if (n) n.setAttribute('display', 'none'); });
      } else {
        var cx = 74.0 + (mod.crossover / 36.0) * 724.0;
        var cy = 232.0 - (Math.min(mod.yMax, mod.ptsB[mod.crossover]) / mod.yMax) * 194.0;
        var boxX = Math.min(cx + 8.0, 646.0);
        [cl, cd, cb, ct].forEach(function (n) { if (n) n.removeAttribute('display'); });
        setAttrs(cl, { x1: cx.toFixed(1), x2: cx.toFixed(1) });
        setAttrs(cd, { cx: cx.toFixed(1), cy: cy.toFixed(1) });
        setAttrs(cb, { x: boxX.toFixed(1), y: Math.max(20.0, cy - 26).toFixed(1) });
        setAttrs(ct, { x: (boxX + 6).toFixed(1), y: Math.max(33.0, cy - 13).toFixed(1) });
        if (ct) ct.textContent = 'Break-Even Crossover (Mo ' + mod.crossover + ')';
      }

      var mat = {
        upfront: ['$0.00M', '$' + mod.upB.toFixed(2) + 'M', '$2.10M'],
        total: ['$' + mod.totalA.toFixed(2) + 'M', '$' + mod.totalB.toFixed(2) + 'M', '$' + mod.totalC.toFixed(2) + 'M'],
        savings: ['$0.00M (Base)', fmtSav(mod.savings), fmtSav(mod.savingsC)],
        crossover: ['Baseline', cbTxt, mod.crossoverC !== null ? 'Month ' + mod.crossoverC : 'No crossover'],
        runway: [mod.runA + ' mo', mod.runB + ' mo', mod.runC + ' mo'],
        cap: [mod.totalA <= 5.2 ? 'Within Cap' : 'Over Ceiling', mod.totalB <= 5.2 ? 'Within Cap' : 'Over Ceiling', mod.totalC <= 5.2 ? 'Within Cap' : 'Over Ceiling'],
        disp: [dispLbl('Option A PayGo', mod.feasA, mod.winner), dispLbl('Option B Hybrid', mod.feasB, mod.winner), dispLbl('Option C Colo', mod.feasC, mod.winner)],
      };
      Object.keys(mat).forEach(function (rk) {
        var row = scope.querySelector('[data-v26-row="' + rk + '"]');
        if (row) ['a', 'b', 'c'].forEach(function (col, idx) { var cell = row.querySelector('[data-col="' + col + '"]'); if (cell) cell.textContent = mat[rk][idx]; });
      });
    }

    [gEl, cEl, rEl].forEach(function (el) { el.addEventListener('input', update); el.addEventListener('change', update); });
    update();
  }

  function bootWave2(root) {
    var doc = root || document;
    doc.querySelectorAll('[data-v23-scope]').forEach(wireV23);
    doc.querySelectorAll('[data-v24-scope]').forEach(wireV24);
    doc.querySelectorAll('[data-v25-scope]').forEach(wireV25);
    doc.querySelectorAll('[data-v26-root]').forEach(wireV26);
  }

  global.QuietWave2Runtime = { boot: bootWave2 };
  if (typeof document !== 'undefined' && document) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () { bootWave2(document); });
    } else {
      bootWave2(document);
    }
  }
})(typeof window !== 'undefined' ? window : globalThis);
