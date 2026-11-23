/* SPDX-License-Identifier: Apache-2.0 */
/* Quiet UI v9.5.0 R2 — Waveform Presets, Table Row Inspector & Microgrid Node Selector */
(function (global) {
  'use strict';

  function escHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function fmtTime(val, unit) {
    const n = Number(val);
    if (!Number.isFinite(n)) return '';
    const s = Math.abs(n) >= 10 ? n.toFixed(1) : (Math.abs(n) >= 1 ? n.toFixed(2).replace(/0$/, '') : n.toFixed(2));
    return unit ? (s + '\u00a0' + unit) : s;
  }

  function computeScopePresets(meta) {
    const channels = Array.isArray(meta.channels) ? meta.channels : [];
    const maxGap = Number(meta.max_gap);
    const tMin = Number(meta.t_min) || 0;
    const tSpan = Number(meta.t_span) || 1;
    let dropT = null;
    let recT = null;
    let peakT = null;
    let peakMag = -Infinity;

    for (let c = 0; c < channels.length; c++) {
      const samples = Array.isArray(channels[c].samples) ? channels[c].samples : [];
      for (let i = 0; i < samples.length; i++) {
        const s = samples[i];
        if (!Array.isArray(s) || s.length < 2) continue;
        const t = Number(s[0]);
        const v = s[1];
        if ((v === null || v === undefined) && dropT === null) {
          dropT = t;
          for (let j = i + 1; j < samples.length; j++) {
            if (Array.isArray(samples[j]) && samples[j][1] !== null && samples[j][1] !== undefined) {
              recT = Number(samples[j][0]);
              break;
            }
          }
        }
        if (i + 1 < samples.length && Number.isFinite(maxGap) && maxGap > 0) {
          const nt = Number(samples[i + 1][0]);
          if (nt - t > maxGap && dropT === null) {
            dropT = t + (nt - t) * 0.5;
            recT = nt;
          }
        }
        if (c === 0 && v !== null && v !== undefined && Number.isFinite(Number(v))) {
          const mag = Math.abs(Number(v));
          if (mag > peakMag) {
            peakMag = mag;
            peakT = t;
          }
        }
      }
    }
    if (dropT === null) dropT = tMin + tSpan * 0.35;
    if (recT === null) recT = tMin + tSpan * 0.55;
    if (peakT === null) peakT = tMin + tSpan * 0.25;
    return [
      { key: 'dropout', label: 'Inspect Dropout (' + fmtTime(dropT, meta.t_unit) + ')', t: dropT },
      { key: 'recovery', label: 'Recovery (' + fmtTime(recT, meta.t_unit) + ')', t: recT },
      { key: 'peak', label: 'Peak Excursion (' + fmtTime(peakT, meta.t_unit) + ')', t: peakT }
    ];
  }

  function elementYBand(el) {
    if (typeof el.getBBox === 'function') {
      try {
        const b = el.getBBox();
        if (b && b.height >= 0) return [b.y, b.y + b.height];
      } catch (_e) {}
    }
    if (el.hasAttribute('y')) {
      const y = parseFloat(el.getAttribute('y') || '0');
      const h = parseFloat(el.getAttribute('height') || '0');
      return [y, y + h];
    }
    if (el.hasAttribute('y1') && el.hasAttribute('y2')) {
      const y1 = parseFloat(el.getAttribute('y1')), y2 = parseFloat(el.getAttribute('y2'));
      return [Math.min(y1, y2), Math.max(y1, y2)];
    }
    const pts = el.getAttribute('points') || '';
    if (pts) {
      const m = pts.match(/[\d.-]+[\s,]+([\d.-]+)/);
      if (m) { const py = parseFloat(m[1]); return [py, py]; }
    }
    if (el.tagName && el.tagName.toLowerCase() === 'path') {
      const m = (el.getAttribute('d') || '').match(/^[ML]\s*[\d.-]+[\s,]+([\d.-]+)/i);
      if (m) { const py = parseFloat(m[1]); return [py, py]; }
    }
    return null;
  }

  function applyChannelFocus(svg, focusIdx) {
    const rects = Array.from(svg.querySelectorAll('rect[data-role="channel"]'));
    if (!rects.length) return;
    const bands = rects.map(function (r) {
      const y = parseFloat(r.getAttribute('y') || '0');
      const h = parseFloat(r.getAttribute('height') || '0');
      return { y0: y - 1, y1: y + h + 1, h: h };
    });
    svg.querySelectorAll('rect, path, line, text, polyline').forEach(function (el) {
      if (el.classList.contains('qe-scope-cursor') || el.classList.contains('qe-live-cursor') ||
          el.closest('.qe-scope-cursor, .qe-live-cursor')) return;
      el.classList.remove('qe-ch-dim', 'qe-ch-focus');
      if (focusIdx < 0) return;
      const span = elementYBand(el);
      if (!span || !Number.isFinite(span[0]) || !Number.isFinite(span[1])) return;
      const cy = (span[0] + span[1]) * 0.5;
      let lane = -1;
      for (let i = 0; i < bands.length; i++) {
        if (cy >= bands[i].y0 && cy <= bands[i].y1) { lane = i; break; }
      }
      if (lane < 0 || (span[1] - span[0]) > bands[lane].h * 1.15) return;
      if (lane === focusIdx) el.classList.add('qe-ch-focus');
      else el.classList.add('qe-ch-dim');
    });
  }

  function initScopeInspectors(doc) {
    const rt = (doc.defaultView && doc.defaultView.QuietEvidenceRuntime) || global.QuietEvidenceRuntime;
    if (!rt || typeof rt.renderScopeAtTime !== 'function') return;
    const win = doc.defaultView || global;

    doc.querySelectorAll('svg[data-qe-scope="true"]').forEach(function (svg) {
      const wrap = svg.closest('.qe-waveform-wrap');
      if (!wrap || wrap.dataset.richScopeBound === '1') return;
      const dataEl = wrap.querySelector('.qe-scope-data');
      if (!dataEl) return;
      let meta = null;
      try { meta = JSON.parse(dataEl.textContent || '{}'); } catch (_e) { return; }
      wrap.dataset.richScopeBound = '1';

      const presets = computeScopePresets(meta);
      const bar = doc.createElement('div');
      bar.className = 'qe-scope-preset-bar';
      bar.setAttribute('role', 'toolbar');
      bar.setAttribute('aria-label', 'Waveform Cursor Presets and Channels');

      const leftGrp = doc.createElement('div');
      leftGrp.className = 'qe-scope-preset-group';
      const lbl = doc.createElement('span');
      lbl.className = 'qe-scope-group-lbl';
      lbl.textContent = 'Inspector:';
      leftGrp.appendChild(lbl);

      let sweepId = 0;
      const presetBtns = [];
      let sweepBtn = null;
      function stopSweep() {
        if (sweepId) { win.clearInterval(sweepId); sweepId = 0; }
        if (sweepBtn) sweepBtn.setAttribute('aria-pressed', 'false');
      }

      presets.forEach(function (p) {
        const btn = doc.createElement('button');
        btn.type = 'button';
        btn.className = 'qe-scope-preset-btn';
        btn.setAttribute('data-scope-preset', p.key);
        btn.setAttribute('aria-pressed', 'false');
        btn.textContent = p.label;
        btn.addEventListener('click', function () {
          stopSweep();
          const already = btn.getAttribute('aria-pressed') === 'true';
          presetBtns.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
          if (already && typeof rt.clearScopeCursor === 'function') {
            rt.clearScopeCursor(svg);
          } else {
            btn.setAttribute('aria-pressed', 'true');
            rt.renderScopeAtTime(svg, meta, p.t);
          }
        });
        presetBtns.push(btn);
        leftGrp.appendChild(btn);
      });

      sweepBtn = doc.createElement('button');
      sweepBtn.type = 'button';
      sweepBtn.className = 'qe-scope-preset-btn';
      sweepBtn.setAttribute('data-scope-preset', 'sweep');
      sweepBtn.setAttribute('aria-pressed', 'false');
      sweepBtn.textContent = 'Sweep Scan';
      sweepBtn.addEventListener('click', function () {
        if (sweepId) { stopSweep(); return; }
        presetBtns.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
        sweepBtn.setAttribute('aria-pressed', 'true');
        const t0 = Number(meta.t_min) || 0;
        const span = Number(meta.t_span) || 1;
        let stepIdx = 0;
        sweepId = win.setInterval(function () {
          if (doc.hidden || !doc.body || !doc.body.contains(svg) || svg.getClientRects().length === 0) {
            stopSweep();
            return;
          }
          const t = t0 + ((stepIdx % 20) / 19) * span;
          stepIdx += 1;
          rt.renderScopeAtTime(svg, meta, t);
        }, 160);
      });
      svg.addEventListener('pointerdown', stopSweep);
      svg.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape' || ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') stopSweep();
      });
      doc.addEventListener('visibilitychange', function () { if (doc.hidden) stopSweep(); });
      if (typeof win.addEventListener === 'function') win.addEventListener('pagehide', stopSweep);
      leftGrp.appendChild(sweepBtn);
      bar.appendChild(leftGrp);

      const channels = Array.isArray(meta.channels) ? meta.channels : [];
      if (channels.length > 1) {
        const chGrp = doc.createElement('div');
        chGrp.className = 'qe-scope-ch-group';
        const chBtns = [];
        channels.forEach(function (ch, idx) {
          const cb = doc.createElement('button');
          cb.type = 'button';
          cb.className = 'qe-scope-preset-btn';
          cb.setAttribute('data-scope-channel', String(idx));
          cb.setAttribute('aria-pressed', 'false');
          cb.textContent = String(ch.id || ('CH' + (idx + 1))).toUpperCase();
          cb.addEventListener('click', function () {
            const on = cb.getAttribute('aria-pressed') !== 'true';
            chBtns.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
            cb.setAttribute('aria-pressed', on ? 'true' : 'false');
            applyChannelFocus(svg, on ? idx : -1);
          });
          chBtns.push(cb);
          chGrp.appendChild(cb);
        });
        bar.appendChild(chGrp);
      }

      const readout = wrap.querySelector('.qe-scope-readout');
      if (readout && readout.parentNode) readout.parentNode.insertBefore(bar, readout.nextSibling);
      else wrap.appendChild(bar);
    });
  }

  function nextVisibleRow(rows, startIdx, dir) {
    for (let i = startIdx + dir; i >= 0 && i < rows.length; i += dir) {
      const r = rows[i];
      if (!r.hidden && !r.classList.contains('v10-row-hidden') && r.getClientRects().length > 0) return r;
    }
    return null;
  }

  function initTableRowInspectors(doc) {
    doc.querySelectorAll('table.qe-table').forEach(function (tbl) {
      if (tbl.dataset.richRowsBound === '1') return;
      const tbody = tbl.querySelector('tbody');
      const anchor = tbl.closest('.qe-table-wrap') || tbl;
      if (!tbody || !anchor || !anchor.parentNode) return;
      const rows = Array.from(tbody.querySelectorAll('tr'));
      if (!rows.length) return;
      tbl.dataset.richRowsBound = '1';
      if (!tbl.hasAttribute('role')) tbl.setAttribute('role', 'grid');

      const headers = Array.from(tbl.querySelectorAll('thead th')).map(function (th) {
        return th.textContent.replace(/\s+/g, ' ').trim();
      });
      const srLive = doc.createElement('span');
      srLive.className = 'qe-sr-live';
      srLive.setAttribute('role', 'status');
      srLive.setAttribute('aria-live', 'polite');
      const inspector = doc.createElement('div');
      inspector.className = 'qe-row-inspector';
      inspector.setAttribute('hidden', '');
      anchor.parentNode.insertBefore(srLive, anchor.nextSibling);
      anchor.parentNode.insertBefore(inspector, srLive.nextSibling);

      function selectRow(row) {
        const wasSel = row.classList.contains('is-selected-row');
        rows.forEach(function (r) {
          r.classList.remove('is-selected-row');
          r.setAttribute('aria-selected', 'false');
        });
        if (wasSel) {
          inspector.setAttribute('hidden', '');
          srLive.textContent = 'Record selection cleared';
          return;
        }
        row.classList.add('is-selected-row');
        row.setAttribute('aria-selected', 'true');
        const cells = Array.from(row.children).map(function (td) {
          return td.textContent.replace(/\s+/g, ' ').trim();
        });
        const pairs = cells.slice(1, 5).map(function (val, i) {
          const h = headers[i + 1] || ('Col ' + (i + 2));
          return '<span><strong>' + escHtml(h) + ':</strong> ' + escHtml(val) + '</span>';
        }).join('');
        inspector.innerHTML = '<span class="qe-row-inspector-lbl">Selected Record</span>' +
          '<strong>' + escHtml(cells[0] || '') + '</strong>' + pairs;
        inspector.removeAttribute('hidden');
        srLive.textContent = 'Selected record: ' + (cells[0] || '');
      }

      const guardSel = 'a,button,input,select,textarea,summary,[role="button"]';
      rows.forEach(function (row, idx) {
        if (!row.hasAttribute('tabindex')) row.setAttribute('tabindex', '0');
        row.setAttribute('aria-selected', 'false');
        row.addEventListener('click', function (ev) {
          if (ev.target && ev.target.closest(guardSel) && ev.target.closest('tr') === row) return;
          selectRow(row);
        });
        row.addEventListener('keydown', function (ev) {
          if (ev.target && ev.target !== row && ev.target.closest(guardSel)) return;
          if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); selectRow(row); }
          else if (ev.key === 'ArrowDown') { const nxt = nextVisibleRow(rows, idx, 1); if (nxt) { ev.preventDefault(); nxt.focus(); } }
          else if (ev.key === 'ArrowUp') { const prv = nextVisibleRow(rows, idx, -1); if (prv) { ev.preventDefault(); prv.focus(); } }
        });
      });
    });

    doc.querySelectorAll('.v9-kpi-tile').forEach(function (tile) {
      if (tile.dataset.richTileBound === '1') return;
      tile.dataset.richTileBound = '1';
      if (!tile.hasAttribute('role')) tile.setAttribute('role', 'button');
      if (!tile.hasAttribute('tabindex')) tile.setAttribute('tabindex', '0');
      if (!tile.hasAttribute('aria-pressed')) tile.setAttribute('aria-pressed', 'false');
      function toggleTile() {
        const parent = tile.parentNode;
        if (parent) {
          parent.querySelectorAll('.v9-kpi-tile').forEach(function (t) {
            if (t !== tile) { t.classList.remove('is-selected-tile'); t.setAttribute('aria-pressed', 'false'); }
          });
        }
        const active = tile.classList.toggle('is-selected-tile');
        tile.setAttribute('aria-pressed', active ? 'true' : 'false');
      }
      tile.addEventListener('click', toggleTile);
      tile.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggleTile(); }
      });
    });
  }

  function initV07NodeSelector(doc) {
    const bar = doc.getElementById('v07-node-chips');
    const diag = doc.getElementById('v07-node-diag');
    if (!bar || bar.dataset.richV07Bound === '1') return;
    bar.dataset.richV07Bound = '1';
    const buttons = Array.from(bar.querySelectorAll('button[data-v07-node]'));
    const scalars = Array.from(doc.querySelectorAll('#v07-scalars .qe-scalar-card'));
    const panels = Array.from(doc.querySelectorAll('#v07-topology .qe-subpanel'));
    const defaultDiag = diag ? diag.textContent : '';
    const map = {
      poi: { sc: [0, 1], pn: [0] },
      gt: { sc: [3], pn: [0] },
      bess: { sc: [2], pn: [0] },
      rs485: { sc: [0], pn: [1] }
    };

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const key = btn.getAttribute('data-v07-node') || '';
        const activate = btn.getAttribute('aria-pressed') !== 'true';
        buttons.forEach(function (b) {
          b.classList.remove('is-active');
          b.setAttribute('aria-pressed', 'false');
        });
        scalars.forEach(function (c) { c.classList.remove('is-node-highlight'); });
        panels.forEach(function (p) { p.classList.remove('is-node-highlight'); });
        if (!activate) {
          if (diag) diag.textContent = defaultDiag;
          return;
        }
        btn.classList.add('is-active');
        btn.setAttribute('aria-pressed', 'true');
        const rule = map[key] || { sc: [], pn: [] };
        rule.sc.forEach(function (i) { if (scalars[i]) scalars[i].classList.add('is-node-highlight'); });
        rule.pn.forEach(function (i) { if (panels[i]) panels[i].classList.add('is-node-highlight'); });
        if (diag && btn.getAttribute('data-v07-diag')) diag.textContent = btn.getAttribute('data-v07-diag');
      });
    });
  }

  function boot(doc) {
    const d = doc || (typeof document !== 'undefined' ? document : null);
    if (!d) return;
    initScopeInspectors(d);
    initTableRowInspectors(d);
    initV07NodeSelector(d);
  }

  global.QuietStageRichV9 = { boot: boot };
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { boot(document); });
    else boot(document);
  }
})(typeof window !== 'undefined' ? window : globalThis);
