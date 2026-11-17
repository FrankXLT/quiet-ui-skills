/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI Pillar 2 — Progressive-Enhancement Evidence Runtime (<= 250L, zero deps).
 * Features:
 *   1. Synchronized multi-channel waveform cursor readout ([data-qe-scope="true"])
 *   2. Pedagogical Flow equation-to-visual term highlighting ([data-term])
 *   3. Spec drawer metadata & copy-JSON feedback
 */
(function (window, document) {
  'use strict';

  var termsBound = false;

  function findNearestSample(samples, targetT, maxGap) {
    if (!Array.isArray(samples) || samples.length === 0) return null;
    for (let i = 0; i < samples.length - 1; i++) {
      const a = samples[i];
      const b = samples[i + 1];
      if (!Array.isArray(a) || !Array.isArray(b) || a.length < 2 || b.length < 2) continue;
      const t0 = Number(a[0]);
      const t1 = Number(b[0]);
      if (targetT >= t0 && targetT <= t1) {
        if (a[1] === null || a[1] === undefined || b[1] === null || b[1] === undefined) {
          return null;
        }
        if (Number.isFinite(maxGap) && maxGap > 0 && (t1 - t0) > maxGap) {
          return null;
        }
      }
    }
    let best = null;
    let bestDt = Infinity;
    for (let i = 0; i < samples.length; i++) {
      const s = samples[i];
      if (!Array.isArray(s) || s.length < 2) continue;
      const dt = Math.abs(Number(s[0]) - targetT);
      if (dt < bestDt) {
        bestDt = dt;
        best = s;
      }
    }
    return best;
  }

  function renderScopeAtTime(svg, meta, targetT) {
    if (!Number.isFinite(meta.x0) || !Number.isFinite(meta.pw) || meta.pw <= 0) return;
    if (!Number.isFinite(meta.t_min) || !Number.isFinite(meta.t_span) || meta.t_span <= 0) return;
    const t = Math.max(meta.t_min, Math.min(meta.t_min + meta.t_span, targetT));
    const clampedX = meta.x0 + ((t - meta.t_min) / meta.t_span) * meta.pw;
    svg.dataset.qeCursorT = String(t);

    const cursorLine = svg.querySelector('.qe-live-cursor');
    if (cursorLine) {
      cursorLine.setAttribute('x1', clampedX.toFixed(1));
      cursorLine.setAttribute('x2', clampedX.toFixed(1));
      cursorLine.setAttribute('visibility', 'visible');
    }

    const wrap = svg.closest('.qe-waveform-wrap');
    const readout = wrap ? wrap.querySelector('.qe-scope-readout') : null;
    if (!readout) return;

    const gapLim = Number(meta.max_gap);
    const vals = (meta.channels || []).map(function (ch) {
      const cid = String((ch && ch.id) || 'CH').toUpperCase();
      const s = findNearestSample(ch && ch.samples, t, gapLim);
      if (!s || s[1] === null || s[1] === undefined) {
        return cid + ': DROPOUT';
      }
      const vStr = typeof s[1] === 'number' ? Number(s[1]).toFixed(2) : String(s[1]);
      return cid + ': ' + vStr + (ch.unit ? '\u00a0' + ch.unit : '');
    });
    readout.textContent = 't = ' + t.toFixed(2) + '\u00a0' + (meta.t_unit || '') + '  |  ' + vals.join('  |  ');
  }

  function updateScopeCursor(svg, meta, clientX) {
    const rect = svg.getBoundingClientRect();
    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!rect.width || !vb || !vb.width || !meta.pw || meta.pw <= 0) return;
    const svgX = ((clientX - rect.left) / rect.width) * vb.width;
    const clampedX = Math.max(meta.x0, Math.min(meta.x0 + meta.pw, svgX));
    const t = meta.t_min + ((clampedX - meta.x0) / meta.pw) * meta.t_span;
    renderScopeAtTime(svg, meta, t);
  }

  function clearScopeCursor(svg) {
    const cursorLine = svg.querySelector('.qe-live-cursor');
    if (cursorLine) cursorLine.setAttribute('visibility', 'hidden');
    const wrap = svg.closest('.qe-waveform-wrap');
    const readout = wrap ? wrap.querySelector('.qe-scope-readout') : null;
    if (readout && readout.dataset.default) {
      readout.textContent = readout.dataset.default;
    }
  }

  function initWaveforms() {
    document.querySelectorAll('svg[data-qe-scope="true"]').forEach(function (svg) {
      if (svg.dataset.qeScopeBound === '1') return;
      const wrap = svg.closest('.qe-waveform-wrap');
      const dataEl = wrap ? wrap.querySelector('.qe-scope-data') : null;
      if (!dataEl) return;
      let meta = null;
      try {
        meta = JSON.parse(dataEl.textContent || '{}');
      } catch (_err) {
        return;
      }
      svg.dataset.qeScopeBound = '1';
      svg.addEventListener('pointermove', function (ev) { updateScopeCursor(svg, meta, ev.clientX); });
      svg.addEventListener('pointerdown', function (ev) { updateScopeCursor(svg, meta, ev.clientX); });
      svg.addEventListener('pointerleave', function () { clearScopeCursor(svg); });
      svg.addEventListener('keydown', function (ev) {
        const curT = Number(svg.dataset.qeCursorT || meta.t_min);
        const step = (meta.t_span || 1) / 40;
        if (ev.key === 'ArrowRight') { ev.preventDefault(); renderScopeAtTime(svg, meta, curT + step); }
        else if (ev.key === 'ArrowLeft') { ev.preventDefault(); renderScopeAtTime(svg, meta, curT - step); }
        else if (ev.key === 'Home') { ev.preventDefault(); renderScopeAtTime(svg, meta, meta.t_min); }
        else if (ev.key === 'End') { ev.preventDefault(); renderScopeAtTime(svg, meta, meta.t_min + meta.t_span); }
        else if (ev.key === 'Escape') { clearScopeCursor(svg); }
      });
    });
  }

  function setActiveTerm(scopeRoot, termKey) {
    if (!scopeRoot) return;
    scopeRoot.querySelectorAll('[data-term]').forEach(function (el) {
      if (!termKey) {
        el.classList.remove('is-term-active', 'is-term-dimmed');
      } else if (el.getAttribute('data-term') === termKey) {
        el.classList.add('is-term-active');
        el.classList.remove('is-term-dimmed');
      } else {
        el.classList.remove('is-term-active');
        el.classList.add('is-term-dimmed');
      }
    });
  }

  function initPedagogicalTerms() {
    if (termsBound) return;
    termsBound = true;
    const resolveScope = function (ev) {
      const target = ev.target && ev.target.closest ? ev.target.closest('[data-term]') : null;
      return target ? { target: target, scope: target.closest('.qe-figure, .qe-pedagogy-scope') || document } : null;
    };
    document.addEventListener('pointerover', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, r.target.getAttribute('data-term')); });
    document.addEventListener('pointerout', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, null); });
    document.addEventListener('focusin', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, r.target.getAttribute('data-term')); });
    document.addEventListener('focusout', function (ev) { const r = resolveScope(ev); if (r) setActiveTerm(r.scope, null); });
  }

  function copyWithFallback(txt, btn) {
    const markCopied = function () {
      btn.textContent = 'Copied';
      window.setTimeout(function () { btn.textContent = 'Copy JSON Spec'; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(markCopied).catch(function () {});
      return;
    }
    const ta = document.createElement('textarea');
    ta.value = txt;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { if (document.execCommand('copy')) markCopied(); } catch (_err) {}
    document.body.removeChild(ta);
  }

  function initSpecDrawers() {
    document.querySelectorAll('.qe-spec-drawer').forEach(function (dlg) {
      if (dlg.querySelector('.qe-copy-spec-btn')) return;
      const pre = dlg.querySelector('pre');
      if (!pre) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'va-pill-btn qe-copy-spec-btn';
      btn.textContent = 'Copy JSON Spec';
      btn.addEventListener('click', function () { copyWithFallback(pre.textContent || '', btn); });
      pre.parentNode.insertBefore(btn, pre);
    });
  }

  function boot() {
    initWaveforms();
    initPedagogicalTerms();
    initSpecDrawers();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.QuietEvidenceRuntime = { boot: boot, setActiveTerm: setActiveTerm };
})(window, document);
