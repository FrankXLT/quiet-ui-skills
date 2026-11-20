# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Live DOM Audit Script & Proof Capture Helpers."""
from __future__ import annotations

import functools
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_ephemeral_server(repo_root: Path) -> tuple[ThreadingHTTPServer, int]:
    handler = functools.partial(SilentHandler, directory=str(repo_root))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    srv.daemon_threads = True
    port = int(srv.server_address[1])
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)
    return srv, port


DOM_AUDIT_JS = """
const errs = [];
if (document.documentElement.scrollWidth > window.innerWidth + 2) {
  errs.push(`Horizontal overflow: scrollWidth=${document.documentElement.scrollWidth} > innerWidth=${window.innerWidth}`);
}
for (const u of document.querySelectorAll('.qe-table th .qe-unit')) {
  if (window.getComputedStyle(u).textTransform !== 'none') errs.push(`SI unit textTransform=${window.getComputedStyle(u).textTransform}`);
  if (/\\b(PS|DBM|KHZ|MRAD|MMHG)\\b/.test(u.innerText)) errs.push(`Uppercase SI unit leak: ${u.innerText}`);
}
for (const svg of document.querySelectorAll('svg')) {
  const sr = svg.getBoundingClientRect();
  if (sr.width <= 12 || sr.height <= 12) continue;
  const vb = svg.viewBox && svg.viewBox.baseVal ? svg.viewBox.baseVal : null;
  if (vb && vb.width > 0) {
    const ar = (sr.width / vb.width) / (sr.height / vb.height);
    if (ar < 0.94 || ar > 1.06) errs.push(`SVG distorted aspect ${ar.toFixed(3)}`);
  }
  const boxes = [];
  for (const t of svg.querySelectorAll('text')) {
    if (!t.textContent || !t.textContent.trim()) continue;
    const cs = window.getComputedStyle(t);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const ctm = t.getScreenCTM();
    if (ctm && ctm.a > 0) {
      const rfs = parseFloat(cs.fontSize) * Math.hypot(ctm.a, ctm.b);
      if (rfs < 10.0 || rfs > 15.5) {
        errs.push(`SVG text '${t.textContent.trim().slice(0,24)}' rendered=${rfs.toFixed(2)}px outside [10.0, 15.5]`);
      }
    }
    const r = t.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      if (r.bottom > sr.bottom + 2.0 || r.top < sr.top - 2.0) errs.push(`SVG text '${t.textContent.trim().slice(0,18)}' clipped by viewBox`);
      boxes.push({el: t, r, cs, txt: t.textContent.trim()});
    }
  }
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], c = boxes[j];
      const dx = Math.min(a.r.right, c.r.right) - Math.max(a.r.left, c.r.left);
      const dy = Math.min(a.r.bottom, c.r.bottom) - Math.max(a.r.top, c.r.top);
      if (dx > 3 && dy > 3) {
        errs.push(`Text overlap '${a.txt.slice(0,18)}' vs '${c.txt.slice(0,18)}'`);
      }
    }
  }
  const vbRects = Array.from(svg.querySelectorAll('rect'));
  if (vb && vb.width > 0) {
    for (const rNode of vbRects) {
      const rx = parseFloat(rNode.getAttribute('x') || '0');
      const rw = parseFloat(rNode.getAttribute('width') || '0');
      const ry = parseFloat(rNode.getAttribute('y') || '0');
      const rh = parseFloat(rNode.getAttribute('height') || '0');
      if (rx + rw > vb.width + 1.5 || ry + rh > vb.height + 1.5) {
        errs.push(`SVG rect (${rx}+${rw}, ${ry}+${rh}) overflows viewBox (${vb.width}x${vb.height})`);
      }
    }
  }
  const rects = vbRects.map(r => r.getBoundingClientRect()).filter(b => b.width > 24 && b.height > 16 && b.width < 320);
  for (const item of boxes) {
    if ((item.el.getAttribute('text-anchor') || '') !== 'middle') continue;
    const cx = (item.r.left + item.r.right) / 2, cy = (item.r.top + item.r.bottom) / 2;
    for (const rb of rects) {
      if (cx >= rb.left + 6 && cx <= rb.right - 6 && cy >= rb.top + 4 && cy <= rb.bottom - 4) {
        if (item.r.width > rb.width + 6) {
          errs.push(`SVG text '${item.txt.slice(0,22)}' (${Math.round(item.r.width)}px) overflows rect (${Math.round(rb.width)}px)`);
        }
      }
    }
  }
}
for (const eqTerm of document.querySelectorAll('.qe-eq-term[data-term]')) {
  if (eqTerm.tabIndex < 0) errs.push(`Equation term '${eqTerm.textContent}' is not keyboard focusable`);
}
for (const grid of document.querySelectorAll('.qe-scalar-grid')) {
  const rows = new Map();
  for (const card of grid.querySelectorAll(':scope > .qe-scalar-card')) {
    const key = Math.round(card.getBoundingClientRect().top / 8);
    if (!rows.has(key)) rows.set(key, []);
    rows.get(key).push(card);
  }
  for (const cards of rows.values()) {
    if (cards.length < 2) continue;
    for (const sel of ['.qe-scalar-title', '.qe-scalar-val-row', 'svg.qe-gauge-svg']) {
      const tops = cards.map(c => c.querySelector(sel)?.getBoundingClientRect().top).filter(v => Number.isFinite(v));
      if (tops.length >= 2 && Math.max(...tops) - Math.min(...tops) > 1.0)
        errs.push(`[BASELINE_LOCK] ${sel} sibling vertical drift ${(Math.max(...tops) - Math.min(...tops)).toFixed(2)}px > 1.0px`);
    }
  }
}
if (document.querySelectorAll('.qe-label-pill').length > 0) errs.push('[SVG_KNOCKOUT] Legacy .qe-label-pill detected');
for (const r of document.querySelectorAll('svg .qe-svg-knockout rect')) {
  const cs = getComputedStyle(r);
  if (cs.stroke && cs.stroke !== 'none' && parseFloat(cs.strokeWidth || '0') > 0) errs.push('[SVG_KNOCKOUT] Stroked knockout rect found');
}
for (const p of document.querySelectorAll('.va-pill')) {
  const cs = getComputedStyle(p);
  const rad = parseFloat(cs.borderTopLeftRadius || '0');
  const v = p.dataset.variant, st = p.dataset.state, txt = p.textContent || '';
  if (/[\\x5b\\x5d]|\\bMargin\\b/.test(txt)) errs.push(`[ATOMIC_PILL] Non-atomic pill text: '${txt}'`);
  if ((v === 'status' || v === 'tag') && rad >= 12) errs.push(`[ROUND_CLICK] Non-interactive pill '${txt}' (${v}) has radius ${rad}px`);
  if (v === 'chip' && (!p.matches('button, a[href], input, [role="button"]') || rad < 99)) errs.push(`[ROUND_CLICK] Chip '${txt}' must be clickable & 999px pill`);
  if (v === 'status' && st === 'nominal' && (parseFloat(cs.borderTopWidth) > 0 || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent')))
    errs.push(`[QUIET_NOMINAL] Nominal status pill '${txt}' has non-transparent bg or border`);
}
for (const el of document.querySelectorAll('.qe-bench-grid .va-card :is(span, div, p)')) {
  if (el.closest('svg') || el.classList.contains('va-pill')) continue;
  const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
  if (r.width > 14 && r.height > 14 && parseFloat(cs.borderTopLeftRadius || '0') >= 99 && !el.matches('[role="button"], button, a[href]'))
    errs.push(`[ROUND_CLICK] Unmarked non-interactive rounded capsule: '${(el.textContent || '').trim().slice(0, 24)}'`);
}
for (const cell of document.querySelectorAll('rect.qe-heatmap-cell[data-state="nominal"]')) {
  const m = getComputedStyle(cell).fill.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
  if (m && (+m[2] - +m[1] > 18 && +m[2] - +m[3] > 15)) errs.push(`[QUIET_HEATMAP] Nominal heatmap cell has green fill ${m[0]}`);
}
for (const wsvg of document.querySelectorAll('svg.qe-waveform-svg')) {
  const spans = [...wsvg.querySelectorAll('rect[data-role="dropout-zone"]')].map(r => {
    const x = parseFloat(r.getAttribute('x') || '0');
    return [x, x + parseFloat(r.getAttribute('width') || '0')];
  }).sort((a, b) => a[0] - b[0]);
  const merged = [];
  for (const [a, b] of spans) {
    if (!merged.length || a > merged[merged.length - 1][1] + 1.0) merged.push([a, b]);
    else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b);
  }
  const labels = [...wsvg.querySelectorAll('text')].filter(t => (t.textContent || '').includes('DROPOUT')).length;
  if (merged.length > 0 && labels !== merged.length) errs.push(`[SINGLE_DROPOUT] Expected ${merged.length} shared DROPOUT label(s), found ${labels}`);
}
return errs;
"""


def capture_proof_shots(driver: Any, base_url: str, shots_dir: Path) -> None:
    """Capture 8 high-resolution 1440x900 (deviceScaleFactor=2) individual proof screenshots."""
    shots_dir.mkdir(parents=True, exist_ok=True)
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": 1440, "height": 900, "deviceScaleFactor": 2, "mobile": False},
    )

    def _snap(url: str, focus_id: str | None, fname: str, print_mode: bool = False) -> None:
        driver.get(url)
        time.sleep(0.25)
        driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print" if print_mode else "screen"})
        time.sleep(0.15)
        if focus_id:
            driver.execute_script(
                "const el = document.getElementById(arguments[0]); if (el) el.scrollIntoView({block: 'start', behavior: 'instant'}); window.scrollBy(0, -68);",
                focus_id,
            )
            time.sleep(0.15)
        driver.save_screenshot(str(shots_dir / fname))

    _snap(f"{base_url}?theme=white&modality=M1&rigor=L3", "bench-m1-l3-nasa-cmd-act", "01_m1_scalar_l3_nasa_cmd_act.png")
    _snap(f"{base_url}?theme=paper&modality=M2", "bench-m2-l2-ppsm-matrix", "02_m2_table_l2_l3_ppsm_heatmap.png")
    _snap(f"{base_url}?theme=white&modality=M3&rigor=L3", "bench-m3-l3-1553b-and-mmio", "03_m3_bitfield_l3_1553b_mmio.png")
    _snap(f"{base_url}?theme=white&modality=M4&rigor=L3", "bench-m4-l3-allan-deviation", "04_m4_plot_l3_allan_residual.png")
    _snap(f"{base_url}?theme=white&modality=M5&rigor=L3", "bench-m5-l3-hil-manchester-scope", "05_m5_waveform_l3_hil_dropout.png")
    _snap(f"{base_url}?theme=white&modality=M6&rigor=L3", "bench-m6-l3-1553b-and-variants", "06_m6_schematic_l3_1553b_bus.png")
    _snap(f"{base_url}?theme=dark&modality=M6&rigor=L2", "bench-m6-l2-ato-enclave", "07_dark_theme_m6_ato_enclave.png")
    _snap(f"{base_url}?theme=white&medium=m1&modality=M4&rigor=L3", "bench-m4-l3-allan-deviation", "08_print_emulation_m1_sheet.png", print_mode=True)
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
