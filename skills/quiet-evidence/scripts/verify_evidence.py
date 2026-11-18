#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Automated Metrology Verifier & Headless Selenium CDP Suite.

Usage:
  python3 -B skills/quiet-evidence/scripts/verify_evidence.py [--cdp] [--screenshots-dir DIR]
"""

from __future__ import annotations

import argparse
import functools
import json
import re
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from compile_evidence import compile_spec  # noqa: E402
from compilers.tokens_and_scales import (  # noqa: E402
    compute_linear_125_scale,
    compute_log_decade_scale,
    format_quantity_header,
)


def _find_repo_root() -> Path:
    curr = Path(__file__).resolve().parent
    for _ in range(6):
        if (curr / "tokens" / "quiet-ui-tokens.css").exists():
            return curr
        curr = curr.parent
    return REPO_ROOT


def verify_static_metrology(repo_root: Path) -> list[str]:
    """Verify 1-2-5 scales, log minor ticks, NIST units, discrete markers, and dropout breaks."""
    errs: list[str] = []
    for lo, hi in ((0.0, 100.0), (-65.0, 65.0), (74.0, 80.0), (1e-6, 7.5e-6)):
        sc = compute_linear_125_scale(lo, hi, target_ticks=6)
        if sc["mantissa"] not in (1, 2, 5):
            errs.append(f"[SCALE_125] Non-1-2-5 mantissa {sc['mantissa']} for [{lo}, {hi}]")

    log_sc = compute_log_decade_scale(1e-3, 1e4)
    if len(log_sc["majors"]) != 8 or len(log_sc["minors"]) != 7 * 8:
        errs.append(f"[LOG_TICKS] Expected 8 majors and 56 minors, got {len(log_sc['majors'])} / {len(log_sc['minors'])}")

    bad_hdr = format_quantity_header("f", "Frequency", "GHz")
    if "[" in bad_hdr or "]" in bad_hdr:
        errs.append(f"[NIST_UNIT] Square brackets detected in header: {bad_hdr}")

    spec_dir = repo_root / "docs" / "bench" / "specimens"
    total = 0
    for fpath in sorted(spec_dir.glob("*.json")):
        specs = json.loads(fpath.read_text(encoding="utf-8"))
        for sp in specs:
            total += 1
            out = compile_spec(sp)
            if sp.get("metadata", {}).get("rigor_level") == "L3" and sp.get("$schema", "").endswith((":plot", ":waveform")):
                if "va-test-condition-block" not in out:
                    errs.append(f"[L3_COND] {sp['id']} missing Test-Condition Header Block")
            if sp.get("$schema", "").endswith(":plot") and sp.get("series"):
                has_disc = any(s.get("epistemic_type") == "discrete_measurement" for s in sp["series"])
                if has_disc and re.search(r'<path[^>]*\bd="[^"]*\bC\b', out):
                    errs.append(f"[NO_BEZIER] {sp['id']} emitted cubic Bezier path in plot")
            if sp.get("id") == "bench-m1-l3-nasa-cmd-act":
                body_out = compile_spec(sp, include_wrapper=False)
                if body_out.count("STALE DATA") != 1 or 'data-variant="status"' not in body_out or "CAUTION" not in body_out or "Margin +18.0%" not in body_out:
                    errs.append("[SCALAR_ANN] M1-L3 duplicated STALE DATA or broke atomic CAUTION + Margin")
            if sp.get("id") == "bench-m2-l3-booktabs-heatmap":
                if 'class="qe-unit"' not in out or "qe-caption-sr" not in out:
                    errs.append("[TABLE_UNIT] M2-L3 missing .qe-unit case shield or .qe-caption-sr")
            if sp.get("id") == "bench-m4-l3-allan-deviation":
                m_leg = re.search(r'data-epistemic="model"[^>]*>.*?</svg>', out, re.S)
                d_leg = re.search(r'data-epistemic="discrete"[^>]*>.*?</svg>', out, re.S)
                if not m_leg or 'stroke-dasharray="5,4"' not in m_leg.group(0) or "<circle" in m_leg.group(0):
                    errs.append("[LEGEND_MODEL] M4-L3 model legend swatch mismatched dashed curve")
                if not d_leg or "<circle" not in d_leg.group(0):
                    errs.append("[LEGEND_DISC] M4-L3 discrete legend swatch missing circle glyph")
                if "2.0 × 10⁻¹² τ⁻⁰·⁵" not in out:
                    errs.append("[MATH_FMT] M4-L3 missing formatted Unicode math ceiling label")
            if sp.get("id") == "bench-m5-l3-hil-manchester-scope":
                paths = re.findall(r'<path[^>]*\bd="([^"]+)"', out)
                if not any(len(re.findall(r"\bM\s+", d)) >= 2 for d in paths):
                    errs.append("[WAVE_DROPOUT] M5-L3 scope did not break <path> with M across null dropout")
                if "+70" not in out or "-70" not in out or "+8" not in out:
                    errs.append("[SCOPE_YSPINE] M5-L3 missing calibrated min/0/max Y-spine ticks")
            if sp.get("id") == "bench-m6-l2-ato-enclave":
                if "ENCLAVE-HIL-TEST" not in out or out.count('stroke-dasharray="5,4"') + out.count('stroke-dasharray="6,3,2,3"') < 4:
                    errs.append("[ENCLAVE_PART] M6-L2 missing separate perimeter rect for ENCLAVE-HIL-TEST")
            if sp.get("id") == "bench-m6-l3-1553b-and-variants":
                if out.count("78 Ω") < 4 or "58.5 Ω XFMR" not in out or "120 Ω" not in out or "A 5 5" not in out:
                    errs.append("[BUS_STD] M6-L3 missing 78-ohm 1553B, 120-ohm CAN-FD, couplers, or bridges")
            if sp.get("id") == "specimen-19-sequence" and ("SPIFFE ID" not in out or "WORM Audit Log" not in out):
                errs.append("[SYS_SEQ] Specimen 19 sequence missing lifeline nodes/messages")
            if sp.get("id") == "specimen-20-n2-matrix" and "NASA SP-2016-6105" not in out:
                errs.append("[SYS_N2] Specimen 20 missing NASA N2 interface matrix header")
            if sp.get("id") == "specimen-21-fault-tree" and ("NRC NUREG-0492" not in out or ">OR<" not in out or ">AND<" not in out):
                errs.append("[SYS_FT] Specimen 21 fault tree missing NRC NUREG-0492 OR/AND gates")

    if total != 21:
        errs.append(f"[BENCH_COUNT] Expected 21 component specimens, compiled {total}")
    return errs


class _SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return


def _start_ephemeral_server(repo_root: Path) -> tuple[ThreadingHTTPServer, int]:
    handler = functools.partial(_SilentHandler, directory=str(repo_root))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    srv.daemon_threads = True
    port = int(srv.server_address[1])
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)
    return srv, port


_DOM_AUDIT_JS = """
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
for (const el of document.querySelectorAll('#bench-gallery .va-card :is(span, div, p)')) {
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


def _capture_proof_shots(driver: Any, base_url: str, shots_dir: Path) -> None:
    """Capture 8 high-resolution 1440x900 (deviceScaleFactor=2) individual proof screenshots."""
    shots_dir.mkdir(parents=True, exist_ok=True)
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": 1440, "height": 900, "deviceScaleFactor": 2, "mobile": False},
    )

    def _snap(url: str, focus_id: str | None, fname: str, print_mode: bool = False) -> None:
        driver.get(url)
        time.sleep(0.25)
        if print_mode:
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
            time.sleep(0.15)
        else:
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
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


def verify_live_cdp(repo_root: Path, screenshots_dir: Path | None = None) -> list[str]:
    """Run Headless Selenium CDP metrology audits across 4 themes, mobile, and @media print."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1440,900")

    srv, port = _start_ephemeral_server(repo_root)
    base_url = f"http://127.0.0.1:{port}/docs/bench/evidence-bench.html"
    errs: list[str] = []
    driver = None

    try:
        driver = webdriver.Chrome(options=opts)
        theme_bgs: dict[str, str] = {}
        for theme in ("white", "paper", "dark-paper", "dark"):
            driver.set_window_size(1440, 900)
            driver.get(f"{base_url}?theme={theme}")
            time.sleep(0.2)
            theme_bgs[theme] = str(driver.execute_script("return window.getComputedStyle(document.body).backgroundColor;"))
            t_errs = driver.execute_script(_DOM_AUDIT_JS)
            errs.extend(f"[CDP_{theme.upper()}_1440] {e}" for e in t_errs)

        if len(set(theme_bgs.values())) < 3:
            errs.append(f"[THEME_SWITCH] Themes did not produce distinct backgrounds: {theme_bgs}")

        driver.set_window_size(390, 844)
        driver.get(f"{base_url}?theme=white")
        time.sleep(0.2)
        m_errs = driver.execute_script(_DOM_AUDIT_JS)
        errs.extend(f"[CDP_MOBILE_390] {e}" for e in m_errs)

        driver.set_window_size(1440, 900)
        driver.get(f"{base_url}?theme=dark&medium=m1")
        time.sleep(0.15)
        m1_err = driver.execute_script("""
            const fig = document.querySelector('.qe-figure');
            const bg = fig ? window.getComputedStyle(fig).backgroundColor : '';
            if (bg !== 'rgb(255, 255, 255)') return 'M1 dark->paper figure bg=' + bg;
            const ttl = document.querySelector('.qe-fig-title');
            const fg = ttl ? window.getComputedStyle(ttl).color : '';
            if (fg !== 'rgb(15, 23, 42)') return 'M1 dark->paper title fg=' + fg;
            return '';
        """)
        if m1_err:
            errs.append(f"[M1_DARK_RESET] {m1_err}")

        # Verify interactive runtime: [data-term] highlight & print media emulation from dark theme
        driver.get(f"{base_url}?theme=dark")
        time.sleep(0.15)
        rt_ok = driver.execute_script("""
            const termEl = document.querySelector('[data-term="path_loss"]');
            if (!termEl) return 'missing [data-term]';
            termEl.dispatchEvent(new Event('focusin', {bubbles: true}));
            const activeCount = document.querySelectorAll('.is-term-active').length;
            termEl.dispatchEvent(new Event('focusout', {bubbles: true}));
            return activeCount >= 2 ? 'ok' : 'activeCount=' + activeCount;
        """)
        if rt_ok != "ok":
            errs.append(f"[RUNTIME_TERM] Pedagogical Flow highlight check failed: {rt_ok}")

        driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
        time.sleep(0.15)
        pr_err = driver.execute_script("""
            const bar = document.querySelector('.qe-topbar');
            if (bar && window.getComputedStyle(bar).display !== 'none') return 'topbar visible in print';
            const bg = window.getComputedStyle(document.body).backgroundColor;
            if (bg !== 'rgb(255, 255, 255)') return 'print body bg=' + bg;
            const fig = document.querySelector('.qe-figure');
            if (fig && window.getComputedStyle(fig).backgroundColor !== 'rgb(255, 255, 255)') {
                return 'print dark figure bg=' + window.getComputedStyle(fig).backgroundColor;
            }
            const ttl = document.querySelector('.qe-fig-title');
            if (ttl && window.getComputedStyle(ttl).color !== 'rgb(15, 23, 42)') {
                return 'print dark title fg=' + window.getComputedStyle(ttl).color;
            }
            return '';
        """)
        if pr_err:
            errs.append(f"[PRINT_EMULATION] {pr_err}")
        driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})

        if screenshots_dir is not None:
            _capture_proof_shots(driver, base_url, screenshots_dir)
    finally:
        if driver:
            driver.quit()
        srv.shutdown()
        srv.server_close()

    return errs


def main() -> None:
    parser = argparse.ArgumentParser(description="Quiet UI Pillar 2 Evidence Metrology Verifier")
    parser.add_argument("--cdp", action="store_true", help="Run live Headless Chrome CDP gates")
    parser.add_argument("--screenshots-dir", default=None, help="Directory to save 8 full-res proof PNGs")
    args = parser.parse_args()

    repo_root = _find_repo_root()
    errors = verify_static_metrology(repo_root)
    if args.cdp:
        shots_dir = Path(args.screenshots_dir) if args.screenshots_dir else None
        errors.extend(verify_live_cdp(repo_root, shots_dir))

    if errors:
        print(f"[FAIL] {len(errors)} metrology verification error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("[PASS] 100% of Quiet UI Pillar 2 metrology & CDP gates succeeded!")


if __name__ == "__main__":
    main()
