/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.0 — Portal Scaler Math & Drag Resizing Controller
 */
(function(window) {
  'use strict';

  function parseDimensions(vpStr) {
    if (!vpStr || vpStr === 'fill') return null;
    const parts = vpStr.split('x').map(function(s) { return parseInt(s.trim(), 10); });
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
      return { width: parts[0], height: parts[1] };
    }
    return null;
  }

  function computeScale(width, height, matEl, zoomMode) {
    if (zoomMode === '1:1') {
      return { scale: 1, scalerW: width, scalerH: height };
    }
    const availW = Math.max(100, matEl.clientWidth - 28);
    const availH = Math.max(100, matEl.clientHeight - 28);
    const scale = Math.min(1, availW / width, availH / height);
    return {
      scale: scale,
      scalerW: Math.round(width * scale),
      scalerH: Math.round(height * scale)
    };
  }

  function applyPortalDimensions(scalerEl, portalEl, matEl, dims, zoomMode) {
    if (!scalerEl || !portalEl || !matEl) return;

    if (!dims) {
      // Fill mode: 100% fluid responsive stage
      scalerEl.style.width = '100%';
      scalerEl.style.height = '100%';
      scalerEl.classList.remove('has-hinge');
      portalEl.style.width = '100%';
      portalEl.style.height = '100%';
      portalEl.style.transform = 'none';
      return;
    }

    const fit = computeScale(dims.width, dims.height, matEl, zoomMode);

    // Hinge line for 820x1180 foldable diagnostics
    const isFold = (dims.width === 820 && dims.height === 1180) ||
                   (dims.width === 1180 && dims.height === 820);
    scalerEl.classList.toggle('has-hinge', isFold);

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
      dragDir = handle.classList.contains('va-drag-w') ? 'w' :
                handle.classList.contains('va-drag-e') ? 'e' : 's';
      startX = e.clientX;
      startY = e.clientY;
      startW = parseInt(portalEl.style.width, 10) || scalerEl.clientWidth;
      startH = parseInt(portalEl.style.height, 10) || scalerEl.clientHeight;

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
      document.body.style.userSelect = 'none';
    }

    function onMouseMove(e) {
      if (!isDragging) return;
      let newW = startW;
      let newH = startH;

      if (dragDir === 'e') {
        newW = Math.max(320, startW + (e.clientX - startX) * 2);
      } else if (dragDir === 'w') {
        newW = Math.max(320, startW - (e.clientX - startX) * 2);
      } else if (dragDir === 's') {
        newH = Math.max(480, startH + (e.clientY - startY));
      }

      applyPortalDimensions(scalerEl, portalEl, matEl, { width: newW, height: newH }, 'fit');
    }

    function onMouseUp(e) {
      if (!isDragging) return;
      isDragging = false;
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.userSelect = '';

      const finalW = parseInt(portalEl.style.width, 10);
      const finalH = parseInt(portalEl.style.height, 10);
      if (typeof onResizeEnd === 'function') {
        onResizeEnd(finalW, finalH);
      }
    }

    scalerEl.addEventListener('mousedown', onMouseDown);
  }

  window.QuietPortalResize = {
    parseDimensions: parseDimensions,
    computeScale: computeScale,
    applyPortalDimensions: applyPortalDimensions,
    initResizeHandles: initResizeHandles
  };
})(typeof window !== 'undefined' ? window : this);
