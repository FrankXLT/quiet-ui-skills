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

  function announceStatus(card, label, isErr) {
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

  function setCardMode(card, mode) {
    const chartPanel = card.querySelector('.va-card-chart-panel');
    const tablePanel = card.querySelector('.va-card-table-panel');
    const btnChart = card.querySelector('[data-qe-view="chart"]');
    const btnTable = card.querySelector('[data-qe-view="table"]');
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
        () => announceStatus(card, kind === 'ai' ? 'Copied for AI' : 'Copied data', false),
        () => announceStatus(card, 'Copy failed', true),
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
      applyBriefScope(scopeBtn);
      return;
    }

    const fmtBtn = e.target.closest('[data-v22-format]');
    if (fmtBtn) {
      applyBriefFormat(fmtBtn);
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const hexTile = e.target && e.target.closest ? e.target.closest('.va-hex-tile') : null;
    if (hexTile) {
      e.preventDefault();
      activateHexTile(hexTile);
    }
  });

  function activateHexTile(tile) {
    const stage = tile.closest('.va-figure-card, .qe-figure, .va-hex-stage') || tile.parentElement;
    if (!stage) return;
    stage.querySelectorAll('.va-hex-tile.is-selected').forEach((n) => n.classList.remove('is-selected'));
    tile.classList.add('is-selected');
    if (tile.parentNode) tile.parentNode.appendChild(tile);
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

  function applyBriefScope(btn) {
    const root = btn.closest('.va-question-brief');
    if (!root) return;
    const scope = btn.getAttribute('data-v22-scope');
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
      const ro = root.querySelector('#v22-map .va-hex-readout, .va-hex-readout');
      if (ro) ro.textContent = d.focus_summary || 'Select any state hex tile to inspect exact rate and bin.';
    }
  }

  function applyBriefFormat(btn) {
    const root = btn.closest('.va-question-brief');
    if (!root) return;
    const fmt = btn.getAttribute('data-v22-format');
    root.querySelectorAll('[data-v22-format]').forEach((b) => {
      const on = b.getAttribute('data-v22-format') === fmt;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.classList.toggle('is-active', on);
    });
    const webPane = root.querySelector('.va-brief-web');
    const slidePane = root.querySelector('.va-brief-slides');
    const isDeck = fmt === 'deck';
    if (webPane) webPane.hidden = isDeck;
    if (slidePane) slidePane.hidden = !isDeck;
  }
})();
