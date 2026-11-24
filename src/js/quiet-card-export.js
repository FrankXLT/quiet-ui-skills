/* Quiet UI v9.6.0 — Card Export (Chart/Table Toggle, Copy TSV, Copy for AI) & Civic Brief Controls */
(() => {
  if (typeof window === 'undefined' || typeof document === 'undefined' || !document || typeof document.addEventListener !== 'function' || window.__quietCardExportInit) return;
  window.__quietCardExportInit = true;

  let toggleSeq = 0;

  function writeClipboard(text) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      return navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
    }
    return fallbackCopy(text);
  }

  function fallbackCopy(text) {
    return new Promise((resolve, reject) => {
      const prev = document.activeElement;
      const ta = document.createElement('textarea');
      try {
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '0';
        ta.style.left = '0';
        ta.style.opacity = '0';
        ta.style.pointerEvents = 'none';
        document.body.appendChild(ta);
        ta.focus({ preventScroll: true });
        ta.select();
        ta.setSelectionRange(0, text.length);
        if (document.execCommand('copy')) resolve();
        else reject(new Error('Clipboard copy rejected'));
      } catch (err) {
        reject(err);
      } finally {
        ta.remove();
        if (prev && typeof prev.focus === 'function') prev.focus({ preventScroll: true });
      }
    });
  }

  function announceStatus(card, label, isErr, triggerBtn) {
    if (triggerBtn && triggerBtn.classList && triggerBtn.classList.contains('va-footer-copy-link')) {
      const txtEl = triggerBtn.querySelector('.va-copy-link-label') || triggerBtn;
      clearTimeout(triggerBtn._qeBtnTimer);
      txtEl.textContent = label;
      triggerBtn.classList.toggle('is-copied', !isErr);
      triggerBtn.classList.toggle('is-error', !!isErr);
      triggerBtn._qeBtnTimer = setTimeout(() => {
        txtEl.textContent = 'Copy for AI';
        triggerBtn.classList.remove('is-copied', 'is-error');
      }, 2800);
    }
    const status = card.querySelector('.va-copy-status, .qe-copy-status');
    if (!status) return;
    toggleSeq = (toggleSeq + 1) % 2;
    status.textContent = label + (toggleSeq ? '\u00A0' : '');
    status.classList.add('is-visible');
    status.classList.toggle('is-error', !!isErr);
    clearTimeout(status._qeTimer);
    status._qeTimer = setTimeout(() => {
      status.classList.remove('is-visible', 'is-error');
      status.textContent = '';
    }, 2800);
  }

  let syncScheduled = false;
  const _cueObserver = typeof ResizeObserver === 'function'
    ? new ResizeObserver((entries) => {
        entries.forEach((entry) => {
          const el = entry.target;
          el.classList.toggle('has-overflow', el.scrollWidth > el.clientWidth + 2);
        });
      })
    : null;

  function syncScrollCues() {
    syncScheduled = false;
    document.querySelectorAll('.va-diverging-scroll').forEach((el) => {
      if (_cueObserver && !el._qeObserved) {
        el._qeObserved = true;
        _cueObserver.observe(el);
      }
      el.classList.toggle('has-overflow', el.scrollWidth > el.clientWidth + 2);
    });
  }

  function scheduleSyncScrollCues() {
    if (syncScheduled) return;
    syncScheduled = true;
    safeRaf(syncScrollCues);
  }

  const safeRaf = (fn) => (typeof requestAnimationFrame === 'function' ? requestAnimationFrame(fn) : setTimeout(fn, 0));

  function setCardMode(card, mode) {
    const chartPanel = card.querySelector('.va-card-chart-panel');
    const tablePanel = card.querySelector('.va-card-table-panel');
    const btnChart = card.querySelector('[data-qe-view="chart"]');
    const btnTable = card.querySelector('[data-qe-view="table"]');
    const edToggle = card.querySelector('[data-qe-editorial-toggle]');
    if (!chartPanel || !tablePanel) return;
    const showTable = mode === 'table';
    chartPanel.hidden = showTable;
    if (showTable) {
      tablePanel.removeAttribute('hidden');
    } else {
      tablePanel.setAttribute('hidden', 'until-found');
    }
    if (btnChart) {
      btnChart.setAttribute('aria-pressed', showTable ? 'false' : 'true');
      btnChart.classList.toggle('is-active', !showTable);
    }
    if (btnTable) {
      btnTable.setAttribute('aria-pressed', showTable ? 'true' : 'false');
      btnTable.classList.toggle('is-active', showTable);
    }
    if (edToggle) {
      edToggle.textContent = showTable ? 'Show chart' : 'Show data table';
      const targetId = showTable ? chartPanel.id : tablePanel.id;
      if (targetId) edToggle.setAttribute('aria-controls', targetId);
    }
    if (!showTable && window.QuietEChartsAdapter && typeof window.QuietEChartsAdapter.refresh === 'function') {
      safeRaf(() => window.QuietEChartsAdapter.refresh(card.ownerDocument || document));
    }
    scheduleSyncScrollCues();
  }

  function readPayload(card) {
    const el = card.querySelector('script.qe-export-payload');
    if (!el) return null;
    try { return JSON.parse(el.textContent || '{}'); } catch (_err) { return null; }
  }

  document.addEventListener('beforematch', (e) => {
    const panel = e.target && e.target.closest ? e.target.closest('.va-card-table-panel') : null;
    if (!panel) return;
    const card = panel.closest('.qe-figure, .va-figure-card');
    if (card) setCardMode(card, 'table');
  });

  document.addEventListener('click', (e) => {
    if (!e.target || typeof e.target.closest !== 'function') return;
    const viewBtn = e.target.closest('[data-qe-view]');
    if (viewBtn) {
      const card = viewBtn.closest('.qe-figure, .va-figure-card');
      if (card) setCardMode(card, viewBtn.getAttribute('data-qe-view'));
      return;
    }

    const edBtn = e.target.closest('[data-qe-editorial-toggle]');
    if (edBtn) {
      const card = edBtn.closest('.qe-figure, .va-figure-card');
      if (!card) return;
      const tblPanel = card.querySelector('.va-card-table-panel');
      const isTableOpen = Boolean(tblPanel && !tblPanel.hasAttribute('hidden'));
      setCardMode(card, isTableOpen ? 'chart' : 'table');
      return;
    }

    const copyBtn = e.target.closest('[data-qe-copy]');
    if (copyBtn) {
      const card = copyBtn.closest('.qe-figure, .va-figure-card');
      if (!card) return;
      const payload = readPayload(card);
      if (!payload) return;
      const kind = copyBtn.getAttribute('data-qe-copy');
      const text = kind === 'ai' ? (payload.markdown || payload.tsv || '') : (payload.tsv || '');
      if (!text) return;
      writeClipboard(text).then(
        () => announceStatus(card, kind === 'ai' ? 'Copied for AI' : 'Copied data', false, copyBtn),
        () => announceStatus(card, 'Copy failed', true, copyBtn),
      );
      return;
    }

    const hexTile = e.target.closest('.va-hex-tile');
    if (hexTile) {
      activateHexTile(hexTile);
      return;
    }

    const scopeBtn = e.target.closest('[data-v22-scope]');
    if (scopeBtn) {
      const root = scopeBtn.closest('.va-question-brief');
      applyBriefScope(root, scopeBtn.getAttribute('data-v22-scope'));
    }
  });

  document.addEventListener('change', (e) => {
    const sel = e.target && e.target.closest ? e.target.closest('[data-v22-scope-select]') : null;
    if (!sel) return;
    applyBriefScope(sel.closest('.va-question-brief'), sel.value);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const hexTile = e.target && e.target.closest ? e.target.closest('.va-hex-tile') : null;
    if (hexTile) {
      e.preventDefault();
      activateHexTile(hexTile);
    }
  });

  function updateHexRing(svg, tile) {
    const ring = svg ? svg.querySelector('.va-hex-focus-ring') : null;
    if (!ring) return;
    const poly = tile ? tile.querySelector('polygon') : null;
    const pts = poly ? poly.getAttribute('points') : '';
    if (pts) {
      ring.setAttribute('points', pts);
      ring.removeAttribute('visibility');
    } else {
      ring.setAttribute('points', '');
      ring.setAttribute('visibility', 'hidden');
    }
  }

  function activateHexTile(tile) {
    const stage = tile.closest('.va-figure-card, .qe-figure, .va-hex-stage') || tile.parentElement;
    if (!stage) return;
    stage.querySelectorAll('.va-hex-tile.is-selected').forEach((n) => n.classList.remove('is-selected'));
    tile.classList.add('is-selected');
    updateHexRing(tile.closest('svg'), tile);
    const card = tile.closest('.va-figure-card, .qe-figure') || stage.parentElement;
    const ro = card ? card.querySelector('.va-hex-readout') : null;
    if (ro) {
      const nm = tile.getAttribute('data-state-name') || '';
      const ab = tile.getAttribute('data-state') || '';
      const fv = tile.getAttribute('data-full-value') || tile.getAttribute('data-value') || '';
      const note = tile.getAttribute('data-note') || '';
      ro.textContent = `${nm} (${ab}): ${fv}${note ? ' · ' + note : ''}`;
    }
  }

  function applyBriefScope(root, scope) {
    if (!root || !scope) return;
    const sel = root.querySelector('[data-v22-scope-select]');
    if (sel && sel.value !== scope) sel.value = scope;
    root.querySelectorAll('[data-v22-scope]').forEach((b) => {
      const on = b.getAttribute('data-v22-scope') === scope;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.classList.toggle('is-active', on);
    });
    const payloadEl = root.querySelector('script.v22-scope-payload');
    if (!payloadEl) return;
    let scopes = {};
    try { scopes = JSON.parse(payloadEl.textContent || '{}'); } catch (_err) { return; }
    const d = scopes[scope];
    if (!d) return;
    const lead = root.querySelector('[data-v22-lead]');
    if (lead) {
      const span = document.createElement('span');
      span.className = 'va-lead-highlight';
      span.textContent = d.lead_clause || '';
      lead.replaceChildren(span, document.createTextNode(' ' + (d.lead_rest || '')));
    }
    const callouts = root.querySelectorAll('[data-v22-callout]');
    const stats = Array.isArray(d.callouts) ? d.callouts : [];
    callouts.forEach((box, idx) => {
      const s = stats[idx];
      if (!s) return;
      const numEl = box.querySelector('.va-callout-num');
      const descEl = box.querySelector('.va-callout-desc');
      if (numEl) numEl.textContent = s.num || '';
      if (descEl) descEl.textContent = s.desc || '';
    });
    if (d.focus_state) {
      const tile = Array.from(root.querySelectorAll('.va-hex-tile')).find((el) => el.getAttribute('data-state') === d.focus_state);
      if (tile) activateHexTile(tile);
    } else {
      root.querySelectorAll('.va-hex-tile.is-selected').forEach((n) => n.classList.remove('is-selected'));
      updateHexRing(root.querySelector('.va-hex-map-svg'), null);
      const ro = root.querySelector('#v22-map .va-hex-readout, .va-hex-readout');
      if (ro) ro.textContent = d.focus_summary || 'Select any state hex tile to inspect exact rate and bin.';
    }
  }

  if (typeof window.addEventListener === 'function') window.addEventListener('resize', scheduleSyncScrollCues, { passive: true });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scheduleSyncScrollCues);
  else scheduleSyncScrollCues();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(scheduleSyncScrollCues);
  const obsRoot = document.body || document.documentElement;
  if (typeof MutationObserver === 'function' && obsRoot) {
    new MutationObserver(scheduleSyncScrollCues).observe(obsRoot, { childList: true, subtree: true });
  }
})();
