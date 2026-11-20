#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Automated Metrology Verifier & Headless Selenium CDP Suite."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from compile_evidence import compile_spec  # noqa: E402
from compilers.tokens_and_scales import compute_linear_125_scale, compute_log_decade_scale, format_quantity_header  # noqa: E402
from verify_evidence_helpers import DOM_AUDIT_JS, capture_proof_shots, start_ephemeral_server  # noqa: E402


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
            if sp.get("id") == "bench-24-m4-forest-pooled" and "<polygon" not in out:
                errs.append("[FOREST_POOLED] Specimen 24 missing diamond <polygon> pooled marker")
            if sp.get("id") == "bench-25-m4-schedule-gantt" and ("Today (Day 11)" not in out or "Critical Path" not in out):
                errs.append("[GANTT_STD] Specimen 25 missing Today marker or Critical Path legend")
            if sp.get("id") == "bench-26-m4-coverage-heatmap" and ("linearGradient" not in out or "#0F172A" not in out):
                errs.append("[HEATMAP_STD] Specimen 26 missing calibrated gradient or WCAG contrast ink")
            if sp.get("id") == "bench-29-m6-interlock-2oo3" and ("2oo3 Logic Voter" not in out or "SAFE TRIP" not in out):
                errs.append("[INTERLOCK_STD] Specimen 29 missing 2oo3 voter or truth table output")

    if total != 30:
        errs.append(f"[BENCH_COUNT] Expected 30 JSON component specimens, compiled {total}")
    return errs


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

    srv, port = start_ephemeral_server(repo_root)
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
            t_errs = driver.execute_script(DOM_AUDIT_JS)
            errs.extend(f"[CDP_{theme.upper()}_1440] {e}" for e in t_errs)

        if len(set(theme_bgs.values())) < 3:
            errs.append(f"[THEME_SWITCH] Themes did not produce distinct backgrounds: {theme_bgs}")

        driver.set_window_size(390, 844)
        driver.get(f"{base_url}?theme=white")
        time.sleep(0.2)
        m_errs = driver.execute_script(DOM_AUDIT_JS)
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

        driver.get(f"{base_url}?theme=white")
        time.sleep(0.25)
        ec_bench_err = driver.execute_script("""
            const wrap = document.querySelector('.qe-plot-wrap[data-quiet-echarts]');
            const btn = wrap && wrap.querySelector('.qe-mode-btn[data-qe-mode="echarts"]');
            const drw = document.querySelector('.qe-eco-drawer');
            if (!wrap || !btn || !drw) return 'missing bench echarts controls';
            btn.click(); drw.open = true;
            if (wrap.dataset.echartsActive !== 'true' || !wrap.querySelector('.qe-echarts-host svg')) return 'echarts did not activate';
            const ls = wrap.querySelector('.qe-legend-series');
            if (ls && getComputedStyle(ls).display !== 'none') return 'duplicate legend series visible with active echarts';
            const tabs = [...drw.querySelectorAll('.qe-eco-tab[role="tab"]')];
            if (tabs.length !== 5) return 'expected 5 tabs in ecosystem drawer, got ' + tabs.length;
            tabs[1].click();
            const openPre = drw.querySelector('.qe-eco-panel:not([hidden]) pre');
            if (!openPre || !openPre.textContent.includes('go.Scatter')) return 'plotly tab panel did not activate';
            if (openPre.scrollWidth > openPre.clientWidth + 2) return 'eco pre horizontal scrollbar';
            const cbtn = drw.querySelector('.qe-copy-btn');
            if (!cbtn) return 'missing eco copy button';
            cbtn.click();
            return '';
        """)
        if ec_bench_err:
            errs.append(f"[BENCH_ECHARTS] {ec_bench_err}")
        else:
            time.sleep(0.15)
            cpy_txt = driver.execute_script("return document.querySelector('.qe-eco-drawer .qe-copy-status')?.textContent || '';")
            if not cpy_txt.strip():
                errs.append("[BENCH_COPY] Copy Snippet click did not update status")
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
            time.sleep(0.15)
            pr_ec_err = driver.execute_script("""
                const wrap = document.querySelector('.qe-plot-wrap[data-quiet-echarts]');
                if (!wrap) return 'plot wrap missing in print';
                const fb = wrap.querySelector('.qe-svg-fallback'), host = wrap.querySelector('.qe-echarts-host'), ls = wrap.querySelector('.qe-legend-series');
                if (!fb || getComputedStyle(fb).display === 'none') return 'static fallback stayed hidden on active echarts print';
                if (host && getComputedStyle(host).display !== 'none') return 'echarts host visible during print';
                if (ls && getComputedStyle(ls).display === 'none') return 'legend stayed hidden during print';
                return '';
            """)
            if pr_ec_err:
                errs.append(f"[BENCH_ECHARTS_PRINT] {pr_ec_err}")
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})

        p61_err = driver.execute_script("""
            const specs = document.querySelectorAll('.qe-specimen');
            if (specs.length !== 36) return 'expected 36 specimens, found ' + specs.length;
            for (const cid of ['bench-23-m4-dumbbell-12', 'bench-24-m4-forest-pooled', 'bench-25-m4-schedule-gantt', 'bench-26-m4-coverage-heatmap']) {
              const card = document.getElementById(cid);
              const btn = card && card.querySelector('.qe-mode-btn[data-qe-mode="echarts"]');
              if (!btn) return 'missing echarts button on ' + cid;
              btn.click();
              const hostSvg = card.querySelector('.qe-echarts-host svg');
              if (!hostSvg || hostSvg.getBoundingClientRect().width < 80) return 'echarts svg missing on ' + cid;
            }
            const gCard = document.getElementById('bench-25-m4-schedule-gantt');
            const gLeg = gCard && gCard.querySelector('.qe-legend-series');
            if (gLeg && getComputedStyle(gLeg).display !== 'none') return 'gantt legend stayed visible under active echarts';

            const armBtn = document.querySelector('#ui-guarded-and-consumer-controls [data-guard-arm]');
            const cfmBtn = document.querySelector('#ui-guarded-and-consumer-controls [data-guard-confirm]');
            const st = document.querySelector('#ui-guarded-and-consumer-controls [data-guard-state]');
            if (!armBtn || !cfmBtn || !st) return 'missing guarded pad controls';
            armBtn.click();
            if (cfmBtn.hidden) return 'confirm button did not reveal on arm';
            cfmBtn.click();
            if (!st.textContent.includes('EXECUTED')) return 'guard confirm did not latch state: ' + st.textContent;

            const stepPlus = document.querySelector('#ui-guarded-and-consumer-controls [data-step-delta="0.5"]');
            const stepVal = document.querySelector('#ui-guarded-and-consumer-controls [data-step-display]');
            if (!stepPlus || !stepVal) return 'missing stepper';
            stepPlus.click();
            if (!stepVal.textContent.includes('21.5')) return 'stepper failed: ' + stepVal.textContent;

            const tNode = document.querySelectorAll('#ui-coupled-tree-explorer [data-tree-node]')[1];
            const tTitle = document.querySelector('#ui-coupled-tree-explorer [data-tree-title]');
            if (!tNode || !tTitle) return 'missing tree nodes';
            tNode.click();
            if (!tTitle.textContent.includes('Worker Queue Pool')) return 'tree click failed: ' + tTitle.textContent;
            return '';
        """)
        if p61_err:
            errs.append(f"[PHASE61_BENCH] {p61_err}")
        if screenshots_dir is not None:
            capture_proof_shots(driver, base_url, screenshots_dir)
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
    errors = verify_static_metrology(_find_repo_root())
    if args.cdp:
        errors.extend(verify_live_cdp(_find_repo_root(), Path(args.screenshots_dir) if args.screenshots_dir else None))
    if errors:
        print(f"[FAIL] {len(errors)} metrology verification error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("[PASS] 100% of Quiet UI Pillar 2 metrology & CDP gates succeeded!")

if __name__ == "__main__":
    main()
