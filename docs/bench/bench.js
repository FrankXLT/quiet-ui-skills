/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.0 Phase 2 — Standalone Visual Qualification Bench Controls.
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
  }

  function applyMedium(medium) {
    const val = medium === 'm1' ? 'm1' : 'm2';
    document.documentElement.setAttribute('data-medium', val);
    const sel = document.getElementById('bench-medium-select');
    if (sel) sel.value = val;
    document.querySelectorAll('.qe-figure').forEach(function (fig) {
      fig.setAttribute('data-qe-medium', val);
    });
  }

  function applyFilters() {
    const modSel = document.getElementById('bench-modality-filter');
    const rigSel = document.getElementById('bench-rigor-filter');
    const modVal = modSel ? modSel.value : 'all';
    const rigVal = rigSel ? rigSel.value : 'all';
    let visible = 0;

    document.querySelectorAll('.qe-specimen').forEach(function (card) {
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
      countEl.textContent = String(visible) + ' of 18 specimens visible';
    }
  }

  function bootBench() {
    const params = new URLSearchParams(window.location.search);
    const qTheme = params.get('theme');
    if (qTheme) {
      applyTheme(qTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      applyTheme('dark');
    }
    if (params.get('medium')) applyMedium(params.get('medium'));

    const themeSel = document.getElementById('bench-theme-select');
    if (themeSel) {
      themeSel.addEventListener('change', function () { applyTheme(themeSel.value); });
    }
    const medSel = document.getElementById('bench-medium-select');
    if (medSel) {
      medSel.addEventListener('change', function () { applyMedium(medSel.value); });
    }
    const modSel = document.getElementById('bench-modality-filter');
    if (modSel) modSel.addEventListener('change', applyFilters);
    const rigSel = document.getElementById('bench-rigor-filter');
    if (rigSel) rigSel.addEventListener('change', applyFilters);

    if (params.get('modality') && modSel) modSel.value = params.get('modality');
    if (params.get('rigor') && rigSel) rigSel.value = params.get('rigor');
    applyFilters();
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
