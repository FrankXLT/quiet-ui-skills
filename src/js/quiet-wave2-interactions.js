/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.7.0 Wave 2 — Client Runtime for v23/v24/v25/v26 & Specimens 51-53 */
(function (global) {
  'use strict';

  function sevState(sev) {
    if (sev === 'CRITICAL' || sev === 'BREAKING') return 'fault';
    if (sev === 'WARN' || sev === 'MODERATE') return 'warn';
    return 'nominal';
  }

  function syncV23PhaseUi(els, phase) {
    var btnStates = {
      baseline: [false, true, true, true, 'nominal', 'BASELINE r41', 'Baseline r41 active on 14/14 clusters — snapshot revert verified.', 'warn', '2 of 14 clusters', '14.3% traffic · ewr-edge-01, fra-edge-02'],
      staged: [true, false, false, true, 'warn', 'CANARY r42 STAGED', 'Candidate r42 staged on 2/14 canary clusters (14.3% traffic · 30 min soak running).', 'warn', '2 of 14 clusters', '14.3% traffic · Canary r42 soaking (ewr-edge-01, fra-edge-02)'],
      promoted: [true, true, false, false, 'nominal', 'PROMOTED r42', 'Candidate r42 promoted across 14/14 clusters (1-click r41 revert ready).', 'nominal', '14 of 14 clusters', '100% traffic · Global r42 active'],
    }[phase];
    if (!btnStates) return;
    if (els.stage) els.stage.disabled = btnStates[0];
    if (els.confirm) els.confirm.disabled = btnStates[1];
    if (els.revert) els.revert.disabled = btnStates[2];
    if (els.toast) els.toast.hidden = btnStates[3];
    if (els.pill) { els.pill.setAttribute('data-state', btnStates[4]); els.pill.textContent = btnStates[5]; }
    if (els.gate) els.gate.textContent = btnStates[6];
    if (els.blastTile) els.blastTile.setAttribute('data-state', btnStates[7]);
    if (els.blastVal) els.blastVal.textContent = btnStates[8];
    if (els.blastSub) els.blastSub.textContent = btnStates[9];
  }

  function wireV23(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var activeFilter = 'all', timerId = 0;
    var filterBtns = scope.querySelectorAll('[data-v23-filter]');
    var ctxCheck = scope.querySelector('[data-v23-context]');
    var rows = scope.querySelectorAll('.v23-row');
    var toast = scope.querySelector('[data-v23-toast]');
    var els = {
      pill: scope.querySelector('#v23-header-status-pill, [data-v23-pill]'),
      gate: scope.querySelector('[data-v23-gate-status]'),
      stage: scope.querySelector('[data-v23-stage]'),
      confirm: scope.querySelector('[data-v23-confirm]'),
      revert: scope.querySelector('[data-v23-revert]'),
      toast: toast,
      blastTile: scope.querySelector('[data-v23-kpi-tile="blast"]'),
      blastVal: scope.querySelector('[data-v23-kpi="blast"]'),
      blastSub: scope.querySelector('[data-v23-kpi="blast_sub"]'),
    };
    function applyRows() {
      var showCtx = !!(ctxCheck && ctxCheck.checked);
      rows.forEach(function (tr) {
        var cat = tr.getAttribute('data-v23-cat') || '';
        tr.hidden = !(cat === 'context' ? showCtx : (activeFilter === 'all' || cat === activeFilter));
      });
    }
    function clearUndoTimer() { if (timerId) { global.clearTimeout(timerId); timerId = 0; } }
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
      syncV23PhaseUi(els, phase);
      if (phase === 'promoted' && toast) armUndoTimer();
    }
    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activeFilter = btn.getAttribute('data-v23-filter') || 'all';
        filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        applyRows();
      });
    });
    if (ctxCheck) ctxCheck.addEventListener('change', applyRows);
    if (els.stage) els.stage.addEventListener('click', function () { setPhase('staged'); });
    if (els.confirm) els.confirm.addEventListener('click', function () { setPhase('promoted'); });
    if (els.revert) els.revert.addEventListener('click', function () { setPhase('baseline'); });
    var toastRevert = scope.querySelector('[data-v23-toast-revert]');
    if (toastRevert) toastRevert.addEventListener('click', function () { setPhase('baseline'); });
    if (toast) {
      var maybeArm = function () { if (!toast.hidden && (!toast.matches || !toast.matches(':hover, :focus-within'))) armUndoTimer(); };
      toast.addEventListener('mouseenter', clearUndoTimer);
      toast.addEventListener('focusin', clearUndoTimer);
      toast.addEventListener('mouseleave', maybeArm);
      toast.addEventListener('focusout', maybeArm);
    }
    applyRows();
  }

  function v24SetInspectorEmpty(scope, isEmpty) {
    var emp = scope.querySelector('[data-v24-insp-empty]');
    var bdy = scope.querySelector('[data-v24-insp-body]');
    var sev = scope.querySelector('[data-insp-sev]');
    var copyBtn = scope.querySelector('[data-v24-copy]');
    if (emp) emp.hidden = !isEmpty;
    if (bdy) bdy.hidden = isEmpty;
    if (sev) sev.hidden = isEmpty;
    if (copyBtn) copyBtn.disabled = isEmpty;
  }

  function v24SelectRow(scope, rows, row, copyOut) {
    if (!row) return;
    v24SetInspectorEmpty(scope, false);
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

  function v24SyncBucketButtons(scope, activeBucket) {
    scope.dataset.v24ActiveBucket = activeBucket === null ? '' : String(activeBucket);
    scope.querySelectorAll('.w2-svg-bar-grp[data-v24-bucket]').forEach(function (g) {
      g.setAttribute('aria-pressed', g.getAttribute('data-v24-bucket') === activeBucket ? 'true' : 'false');
    });
  }

  function v24BindRowEvents(scope, rows, copyOut) {
    rows.forEach(function (row) {
      row.addEventListener('click', function () { v24SelectRow(scope, rows, row, copyOut); });
      row.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          v24SelectRow(scope, rows, row, copyOut);
        } else if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
          ev.preventDefault();
          var vis = rows.filter(function (r) { return !r.hidden; });
          var next = vis[vis.indexOf(row) + (ev.key === 'ArrowDown' ? 1 : -1)];
          if (next) { next.focus(); v24SelectRow(scope, rows, next, copyOut); }
        }
      });
    });
  }

  function v24BindCopy(scope, rows, copyBtn, copyOut) {
    if (!copyBtn) return;
    copyBtn.addEventListener('click', function () {
      var active = scope.querySelector('.v24-row[aria-selected="true"]') || rows[0];
      if (!active || active.hidden) return;
      var summary = ['data-ev-ts', 'data-ev-svc', 'data-ev-span', 'data-ev-trace', 'data-ev-code', 'data-ev-msg']
        .map(function (attr) { return active.getAttribute(attr); }).join(' | ');
      if (global.navigator && global.navigator.clipboard && global.navigator.clipboard.writeText) {
        global.navigator.clipboard.writeText(summary).catch(function () {});
      }
      if (copyOut) copyOut.textContent = 'Copied ' + (active.getAttribute('data-ev-trace') || 'trace');
    });
  }

  function wireV24(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var activeCat = 'all', activeBucket = null;
    var filterBtns = scope.querySelectorAll('[data-v24-filter]');
    var searchInput = scope.querySelector('[data-v24-search]');
    var rows = Array.prototype.slice.call(scope.querySelectorAll('.v24-row'));
    var tableEl = scope.querySelector('[data-v24-table]');
    var emptyEl = scope.querySelector('[data-v24-empty]');
    var clearBtn = scope.querySelector('[data-v24-clear]');
    var countEl = scope.querySelector('[data-v24-visible-count]');
    var copyOut = scope.querySelector('[data-v24-copy-status]');

    function applyFilters() {
      var q = searchInput ? searchInput.value.trim().toLowerCase() : '', visibleRows = [];
      rows.forEach(function (tr) {
        var okCat = activeCat === 'all' || (tr.getAttribute('data-v24-cat') || '') === activeCat;
        var okB = activeBucket === null || (tr.getAttribute('data-v24-bucket') || '') === String(activeBucket);
        var okQ = !q || (tr.getAttribute('data-v24-search') || '').indexOf(q) !== -1;
        var vis = okCat && okB && okQ;
        tr.hidden = !vis;
        if (vis) visibleRows.push(tr);
      });
      if (countEl) countEl.textContent = 'Showing ' + visibleRows.length + ' / ' + rows.length + ' events';
      if (tableEl) tableEl.hidden = visibleRows.length === 0;
      if (emptyEl) emptyEl.hidden = visibleRows.length !== 0;
      if (visibleRows.length === 0) {
        rows.forEach(function (r) { r.setAttribute('aria-selected', 'false'); });
        v24SetInspectorEmpty(scope, true);
      } else if (visibleRows.every(function (r) { return r.getAttribute('aria-selected') !== 'true'; })) {
        v24SelectRow(scope, rows, visibleRows[0], copyOut);
      } else {
        v24SetInspectorEmpty(scope, false);
      }
    }
    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activeCat = btn.getAttribute('data-v24-filter') || 'all';
        if (activeCat === 'all') { activeBucket = null; v24SyncBucketButtons(scope, null); }
        filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        applyFilters();
      });
    });
    function toggleBucket(grp) {
      var b = grp.getAttribute('data-v24-bucket');
      activeBucket = activeBucket === b ? null : b;
      v24SyncBucketButtons(scope, activeBucket);
      applyFilters();
    }
    scope.addEventListener('click', function (ev) {
      var grp = ev.target && ev.target.closest ? ev.target.closest('.w2-svg-bar-grp[data-v24-bucket]') : null;
      if (grp) toggleBucket(grp);
    });
    scope.addEventListener('keydown', function (ev) {
      var grp = ev.target && ev.target.closest ? ev.target.closest('.w2-svg-bar-grp[data-v24-bucket]') : null;
      if (grp && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); toggleBucket(grp); }
    });
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        activeCat = 'all'; activeBucket = null;
        if (searchInput) searchInput.value = '';
        filterBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v24-filter') === 'all' ? 'true' : 'false'); });
        v24SyncBucketButtons(scope, null);
        applyFilters();
      });
    }
    v24BindRowEvents(scope, rows, copyOut);
    v24BindCopy(scope, rows, scope.querySelector('[data-v24-copy]'), copyOut);
  }

  function wireV25(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    scope.dataset.v25ActiveSpan = 'all';
    var btns = scope.querySelectorAll('[data-v25-span]');
    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var grp = btn.getAttribute('data-v25-span') || 'all';
        scope.dataset.v25ActiveSpan = grp;
        btns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        scope.querySelectorAll('.w2-span-node, .w2-span-mark, .w2-span-row').forEach(function (el) {
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
    var opts = [
      { name: 'Option B Hybrid', tot: totalB, ok: feasB },
      { name: 'Option A PayGo', tot: totalA, ok: feasA },
      { name: 'Option C Colo', tot: totalC, ok: feasC },
    ];
    var compliant = opts.filter(function (x) { return x.ok && x.tot <= 5.20; }).sort(function (x, y) { return x.tot - y.tot; });
    var anyRun = opts.some(function (x) { return x.ok; });
    var cStatus = compliant.length ? 'compliant' : (anyRun ? 'over_constrained' : 'runway_blocked');
    var winner = compliant.length ? compliant[0].name : (anyRun ? 'Over-Constrained' : 'None (Runway Blocked)');
    var recState = compliant.length ? 'nominal' : (anyRun ? 'warn' : 'fault');
    return {
      ptsA: ptsA, ptsB: ptsB, ptsC: ptsC, upB: Math.round(upB * 100) / 100,
      totalA: totalA, totalB: totalB, totalC: totalC,
      savings: Math.round((totalA - totalB) * 100) / 100, savingsC: Math.round((totalA - totalC) * 100) / 100,
      crossover: cross, crossoverC: crossC, runA: runA, runB: runB, runC: runC,
      feasA: feasA, feasB: feasB, feasC: feasC, winner: winner, recState: recState, constraintStatus: cStatus,
      yMax: Math.max(totalA, totalB, totalC) > 6.2 ? 8.0 : 6.5,
    };
  }

  function readV26Geom(scope) {
    var svg = scope.querySelector('[data-v26-svg]'), g = null;
    try { g = svg ? JSON.parse(svg.getAttribute('data-v26-geom') || 'null') : null; } catch (e) { g = null; }
    var ml = g && g.ml ? g.ml : 48, mr = g && g.mr ? g.mr : 14, w = g && g.w ? g.w : 1120;
    var yTop = g && g.yTop && g.yTop >= 32 ? g.yTop : 38, lineTop = g && g.lineTop ? g.lineTop : 24, yBot = g && g.yBot ? g.yBot : 232;
    return { ml: ml, mr: mr, w: w, pw: Math.max(180, w - ml - mr), yTop: yTop, lineTop: lineTop, yBot: yBot, spanY: yBot - yTop, mobile: !!(g && g.mobile) };
  }

  function polyPath(vals, yMax, geom) {
    return 'M ' + vals.map(function (v, m) {
      return (geom.ml + (m / 36.0) * geom.pw).toFixed(1) + ' ' + (geom.yBot - (Math.min(yMax, v) / yMax) * geom.spanY).toFixed(1);
    }).join(' L ');
  }

  function setAttrs(el, attrs) {
    if (el) Object.keys(attrs).forEach(function (k) { el.setAttribute(k, String(attrs[k])); });
  }

  function renderV26YGrid(yGrid, yMax, geom) {
    if (!yGrid || !yGrid.ownerDocument) return;
    while (yGrid.firstChild) yGrid.removeChild(yGrid.firstChild);
    var ns = 'http://www.w3.org/2000/svg';
    (yMax > 7.0 ? [0.0, 2.0, 4.0, 6.0, 8.0] : [0.0, 2.0, 4.0, 6.0]).forEach(function (v) {
      var yy = geom.yBot - (v / yMax) * geom.spanY;
      var ln = yGrid.ownerDocument.createElementNS(ns, 'line');
      setAttrs(ln, { x1: geom.ml, y1: yy.toFixed(1), x2: geom.ml + geom.pw, y2: yy.toFixed(1), stroke: 'var(--border-subtle)', 'stroke-dasharray': '2 3' });
      var tx = yGrid.ownerDocument.createElementNS(ns, 'text');
      setAttrs(tx, { x: geom.ml - 6, y: (yy + 4).toFixed(1), 'text-anchor': 'end', 'font-size': '11.5', fill: 'var(--text-muted)' });
      tx.textContent = '$' + v.toFixed(1) + 'M';
      yGrid.appendChild(ln); yGrid.appendChild(tx);
    });
  }

  function fmtSav(diff) { return diff >= 0 ? '$' + diff.toFixed(2) + 'M saved' : '+$' + Math.abs(diff).toFixed(2) + 'M cost'; }

  function syncV26MatrixAndCards(scope, mod, r) {
    var cbTxt = mod.crossover !== null ? 'Month ' + mod.crossover : 'No crossover';
    var savTxt = mod.savings >= 0 ? 'Saves $' + mod.savings.toFixed(2) + 'M vs PayGo' : '+$' + Math.abs(mod.savings).toFixed(2) + 'M vs PayGo';
    if (mod.constraintStatus === 'over_constrained') savTxt = 'Raise commit >= 75% or adjust $5.20M ceiling';
    else if (mod.constraintStatus === 'runway_blocked') savTxt = 'No option meets ' + r + ' mo runway floor';
    var kpiMap = {
      winner: mod.winner, savings: savTxt, crossover: cbTxt,
      cross_sub: mod.crossover !== null ? 'Option B crosses below Option A' : 'Option B stays above Option A',
      total_b: '$' + mod.totalB.toFixed(2) + 'M',
      total_sub: mod.totalB > 5.20 ? '+$' + (mod.totalB - 5.20).toFixed(2) + 'M over $5.20M ceiling' : 'vs $5.20M budget ceiling',
      runway_b: mod.runB + ' mo', runway_note: 'Option C ' + mod.runC + ' mo vs ' + r + ' mo floor',
    };
    Object.keys(kpiMap).forEach(function (k) { var el = scope.querySelector('[data-v26-kpi="' + k + '"]'); if (el) el.textContent = kpiMap[k]; });
    var winTile = scope.querySelector('[data-v26-kpi-tile="winner"]'), totTile = scope.querySelector('[data-v26-kpi-tile="total"]');
    var runTile = scope.querySelector('[data-v26-kpi-tile="runway"]'), badge = scope.querySelector('[data-v26-rec-badge]');
    if (winTile) winTile.setAttribute('data-state', mod.recState);
    if (totTile) totTile.setAttribute('data-state', mod.totalB > 5.20 ? 'warn' : 'nominal');
    if (runTile) runTile.setAttribute('data-state', mod.feasC ? 'nominal' : 'warn');
    if (badge) {
      badge.setAttribute('data-state', mod.recState);
      badge.textContent = mod.constraintStatus === 'over_constrained' ? 'OVER-CONSTRAINED · > $5.20M CEILING' : (mod.recState === 'fault' ? 'RUNWAY GATE BLOCKED' : 'RECOMMENDED: ' + mod.winner.toUpperCase());
    }
    var disp = function (name, feas, tot) { return !feas ? 'RUNWAY BLOCKED' : (tot > 5.20 ? 'OVER CEILING' : (mod.winner === name ? 'RECOMMENDED' : 'VIABLE')); };
    var mat = {
      upfront: ['$0.00M', '$' + mod.upB.toFixed(2) + 'M', '$2.10M'],
      total: ['$' + mod.totalA.toFixed(2) + 'M', '$' + mod.totalB.toFixed(2) + 'M', '$' + mod.totalC.toFixed(2) + 'M'],
      savings: ['$0.00M (Base)', fmtSav(mod.savings), fmtSav(mod.savingsC)],
      crossover: ['Baseline', cbTxt, mod.crossoverC !== null ? 'Month ' + mod.crossoverC : 'No crossover'],
      runway: [mod.runA + ' mo', mod.runB + ' mo', mod.runC + ' mo'],
      cap: [mod.totalA <= 5.2 ? 'Within Cap' : 'Over Ceiling', mod.totalB <= 5.2 ? 'Within Cap' : 'Over Ceiling', mod.totalC <= 5.2 ? 'Within Cap' : 'Over Ceiling'],
      disp: [disp('Option A PayGo', mod.feasA, mod.totalA), disp('Option B Hybrid', mod.feasB, mod.totalB), disp('Option C Colo', mod.feasC, mod.totalC)],
    };
    Object.keys(mat).forEach(function (rk) {
      var row = scope.querySelector('[data-v26-row="' + rk + '"]');
      if (row) ['a', 'b', 'c'].forEach(function (col, idx) { var cell = row.querySelector('[data-col="' + col + '"]'); if (cell) cell.textContent = mat[rk][idx]; });
    });
  }

  function wireV26(scope) {
    if (!scope || scope.dataset.w2Bound === '1') return;
    scope.dataset.w2Bound = '1';
    var gEl = scope.querySelector('[data-v26-input="growth"]'), cEl = scope.querySelector('[data-v26-input="commit"]'), rEl = scope.querySelector('[data-v26-input="runway"]');
    if (!gEl || !cEl || !rEl) return;
    function update() {
      [gEl, cEl, rEl].forEach(function (inp) {
        var mn = Number(inp.min || 0), mx = Number(inp.max || 100), val = Number(inp.value || 0);
        inp.style.setProperty('--pct', (mx > mn ? ((val - mn) / (mx - mn)) * 100 : 50).toFixed(1) + '%');
      });
      var g = Number(gEl.value), c = Number(cEl.value), r = Number(rEl.value), mod = computeV26(g, c, r), geom = readV26Geom(scope);
      var outs = { growth: g + '%', commit: c + '%', runway: r + ' mo' };
      Object.keys(outs).forEach(function (k) { var el = scope.querySelector('[data-v26-out="' + k + '"]'); if (el) el.textContent = outs[k]; });
      syncV26MatrixAndCards(scope, mod, r);
      renderV26YGrid(scope.querySelector('[data-v26-ygrid]'), mod.yMax, geom);
      var yCeil = geom.yBot - (5.2 / mod.yMax) * geom.spanY;
      setAttrs(scope.querySelector('[data-v26-ceil-line]'), { x1: geom.ml, x2: geom.ml + geom.pw, y1: yCeil.toFixed(1), y2: yCeil.toFixed(1) });
      setAttrs(scope.querySelector('[data-v26-ceil-bg]'), { x: geom.ml + 6, y: (yCeil - 18).toFixed(1) });
      setAttrs(scope.querySelector('[data-v26-ceil-lbl]'), { x: geom.ml + 12, y: (yCeil - 6).toFixed(1) });
      setAttrs(scope.querySelector('[data-v26-path="a"]'), { d: polyPath(mod.ptsA, mod.yMax, geom) });
      setAttrs(scope.querySelector('[data-v26-path="b"]'), { d: polyPath(mod.ptsB, mod.yMax, geom) });
      setAttrs(scope.querySelector('[data-v26-path="c"]'), { d: polyPath(mod.ptsC, mod.yMax, geom) });
      var cl = scope.querySelector('[data-v26-cross-line]'), cd = scope.querySelector('[data-v26-cross-dot]');
      var cb = scope.querySelector('[data-v26-cross-bg]'), ct = scope.querySelector('[data-v26-cross-lbl]');
      if (mod.crossover === null) {
        [cl, cd, cb, ct].forEach(function (n) { if (n) n.setAttribute('display', 'none'); });
      } else {
        var cx = geom.ml + (mod.crossover / 36.0) * geom.pw, cy = geom.yBot - (Math.min(mod.yMax, mod.ptsB[mod.crossover]) / mod.yMax) * geom.spanY;
        var boxW = geom.mobile ? 132 : 184, boxX = Math.min(cx + 8.0, geom.ml + geom.pw - boxW);
        [cl, cd, cb, ct].forEach(function (n) { if (n) n.removeAttribute('display'); });
        setAttrs(cl, { x1: cx.toFixed(1), x2: cx.toFixed(1), y1: geom.lineTop, y2: geom.yBot });
        setAttrs(cd, { cx: cx.toFixed(1), cy: cy.toFixed(1) });
        setAttrs(cb, { x: boxX.toFixed(1), y: Math.max(20.0, cy - 26).toFixed(1), width: boxW });
        setAttrs(ct, { x: (boxX + 6).toFixed(1), y: Math.max(33.0, cy - 13).toFixed(1) });
        if (ct) ct.textContent = geom.mobile ? 'Crossover (Mo ' + mod.crossover + ')' : 'Break-Even Crossover (Mo ' + mod.crossover + ')';
      }
    }
    scope._v26Refresh = update;
    [gEl, cEl, rEl].forEach(function (el) { el.addEventListener('input', update); el.addEventListener('change', update); });
    update();
  }

  function bootWave2(root) {
    var doc = root || document;
    doc.querySelectorAll('[data-v23-scope]').forEach(wireV23);
    doc.querySelectorAll('[data-v24-scope]').forEach(wireV24);
    doc.querySelectorAll('[data-v25-scope]').forEach(wireV25);
    doc.querySelectorAll('[data-v26-root]').forEach(wireV26);
    if (global.QuietWave2Svg && typeof global.QuietWave2Svg.boot === 'function') {
      global.QuietWave2Svg.boot(doc);
    }
  }

  global.QuietWave2Runtime = { boot: bootWave2 };
  if (typeof document !== 'undefined' && document) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { bootWave2(document); });
    else bootWave2(document);
  }
})(typeof window !== 'undefined' ? window : globalThis);
