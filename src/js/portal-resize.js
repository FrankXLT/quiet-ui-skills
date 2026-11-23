/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.5 — Portal Scaler Math, Frame Bezel Classification & Drag Resizing
 */
(function (window) {
  'use strict';

  function parseDimensions(vpStr) {
    if (!vpStr || vpStr === 'fill') return null;
    const m = /^\s*(\d+)\s*x\s*(\d+)\s*$/.exec(String(vpStr));
    if (!m) return null;
    const w = parseInt(m[1], 10);
    const h = parseInt(m[2], 10);
    return (w >= 320 && h >= 360) ? { width: w, height: h } : null;
  }

  function classifyFrame(dims, medium) {
    if (!dims) return 'fill';
    if (medium === 'm1' || (dims.width === 1056 && dims.height === 1368)) return 'paper';
    if (dims.width <= 480) return 'mobile';
    if (
      (dims.width === 1280 && dims.height === 800) ||
      (dims.width === 800 && dims.height === 1280) ||
      (dims.width >= 760 && dims.width <= 1366 && medium !== 'm1')
    ) return 'tablet';
    return 'screen';
  }

  function computeScale(width, height, matEl, zoomMode, bezelPx) {
    if (zoomMode === '1:1') {
      return { scale: 1, scalerW: width, scalerH: height };
    }
    const bezel = typeof bezelPx === 'number' ? bezelPx : 12;
    const padX = (window.innerWidth < 700 ? 16 : 48) + bezel;
    const padY = (window.innerWidth < 700 ? 16 : 36) + bezel;
    const availW = Math.max(100, matEl.clientWidth - padX);
    const availH = Math.max(100, matEl.clientHeight - padY);
    const scale = Math.min(1, availW / width, availH / height);
    return {
      scale: scale,
      scalerW: Math.round(width * scale),
      scalerH: Math.round(height * scale),
    };
  }

  function isFoldableSize(w, h) {
    return (
      (w === 840 && h === 1050) || (w === 1050 && h === 840) ||
      (w === 820 && h === 1180) || (w === 1180 && h === 820)
    );
  }

  function applyPortalDimensions(scalerEl, portalEl, matEl, dims, zoomMode, medium) {
    if (!scalerEl || !portalEl || !matEl) return;
    const frame = classifyFrame(dims, medium);
    scalerEl.dataset.portalFrame = frame;
    matEl.dataset.portalFrame = frame;
    if (!dims) {
      scalerEl.style.width = '100%';
      scalerEl.style.height = '100%';
      scalerEl.classList.remove('has-hinge');
      portalEl.style.width = '100%';
      portalEl.style.height = '100%';
      portalEl.style.transform = 'none';
      return;
    }
    const fit = computeScale(dims.width, dims.height, matEl, zoomMode, frame === 'tablet' ? 12 : 8);
    scalerEl.scrollLeft = 0;
    scalerEl.scrollTop = 0;
    scalerEl.classList.toggle('has-hinge', isFoldableSize(dims.width, dims.height));
    scalerEl.style.width = fit.scalerW + 'px';
    scalerEl.style.height = fit.scalerH + 'px';
    portalEl.style.width = dims.width + 'px';
    portalEl.style.height = dims.height + 'px';
    portalEl.style.transform = 'scale(' + fit.scale + ')';
    portalEl.style.transformOrigin = 'top left';
  }

  function initResizeHandles(scalerEl, portalEl, matEl, onResizeEnd) {
    if (!scalerEl) return;
    let isDragging = false;
    let hasMoved = false;
    let dragDir = '';
    let startX = 0;
    let startY = 0;
    let startW = 0;
    let startH = 0;

    function onMouseDown(e) {
      const handle = e.target.closest('.va-drag-handle');
      if (!handle) return;
      e.preventDefault();
      isDragging = true;
      hasMoved = false;
      dragDir = handle.classList.contains('va-drag-w') ? 'w' :
        (handle.classList.contains('va-drag-e') ? 'e' : 's');
      startX = e.clientX;
      startY = e.clientY;
      startW = (portalEl.style.width || '').endsWith('px') ? parseInt(portalEl.style.width, 10) : scalerEl.clientWidth;
      startH = (portalEl.style.height || '').endsWith('px') ? parseInt(portalEl.style.height, 10) : scalerEl.clientHeight;
      portalEl.style.pointerEvents = 'none';
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
      document.body.style.userSelect = 'none';
    }

    function onMouseMove(e) {
      if (!isDragging) return;
      hasMoved = true;
      let newW = startW;
      let newH = startH;
      if (dragDir === 'e') newW = Math.max(320, startW + (e.clientX - startX) * 2);
      else if (dragDir === 'w') newW = Math.max(320, startW - (e.clientX - startX) * 2);
      else if (dragDir === 's') newH = Math.max(480, startH + (e.clientY - startY));
      applyPortalDimensions(scalerEl, portalEl, matEl, { width: newW, height: newH }, 'fit', document.documentElement.dataset.medium);
    }

    function onMouseUp() {
      if (!isDragging) return;
      isDragging = false;
      portalEl.style.pointerEvents = '';
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.userSelect = '';
      if (!hasMoved) return;
      const finalW = parseInt(portalEl.style.width, 10);
      const finalH = parseInt(portalEl.style.height, 10);
      if (typeof onResizeEnd === 'function' && finalW >= 320 && finalH >= 360) onResizeEnd(finalW, finalH);
    }

    scalerEl.addEventListener('mousedown', onMouseDown);
  }

  window.QuietPortalResize = {
    parseDimensions: parseDimensions,
    classifyFrame: classifyFrame,
    computeScale: computeScale,
    applyPortalDimensions: applyPortalDimensions,
    initResizeHandles: initResizeHandles,
  };
})(typeof window !== 'undefined' ? window : this);
