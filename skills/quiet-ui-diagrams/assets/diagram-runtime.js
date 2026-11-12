// Quiet UI Diagrams — Motion Runtime Controller
(function() {
  'use strict';
  window.addEventListener('DOMContentLoaded', () => {
    const root = document.querySelector('[data-motion-root]');
    if (!root) return;
    const items = Array.from(root.querySelectorAll('[data-motion-item]'));
    const controls = document.querySelector('[data-motion-controls]');
    const status = document.querySelector('[data-motion-status]');
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
    const count = items.length;
    let step = 0;
    let playing = false;
    let timer = null;

    function render(targetStep) {
      step = Math.max(0, Math.min(count, targetStep));
      items.forEach((el, idx) => {
        if (idx < step) {
          el.classList.add('is-visible');
        } else {
          el.classList.remove('is-visible');
        }
      });
      if (status) status.textContent = `Step ${step} of ${count}`;
    }

    function pause() {
      playing = false;
      if (timer) clearTimeout(timer);
      root.classList.remove('is-playing');
    }

    function tick() {
      if (!playing) return;
      if (step >= count) { pause(); return; }
      render(step + 1);
      timer = setTimeout(tick, 700);
    }

    function play() {
      if (step >= count) render(0);
      playing = true;
      root.classList.add('is-playing');
      timer = setTimeout(tick, 700);
    }

    if (controls) {
      controls.style.display = 'flex';
      controls.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-motion-action]');
        if (!btn) return;
        const act = btn.dataset.motionAction;
        if (act === 'play') play();
        if (act === 'pause') pause();
        if (act === 'replay') { render(0); play(); }
        if (act === 'prev') { pause(); render(step - 1); }
        if (act === 'next') { pause(); render(step + 1); }
      });
    }

    if (reduce.matches) {
      render(count);
      if (controls) controls.style.display = 'none';
    } else {
      root.classList.add('motion-ready');
      render(0);
      play();
    }
  });
})();
