# SPDX-License-Identifier: Apache-2.0
"""Component Library (39 Specimens), Live ECharts, /docs Standalone Root & Portable Auditor CDP Gates."""

from __future__ import annotations

import sys
import time
from typing import Any

from . import REPO_ROOT, set_viewport, start_http_server

DOM_AUDIT_JS = """
const errs = [];
if (document.documentElement.scrollWidth > window.innerWidth + 2) errs.push(`Overflow: ${document.documentElement.scrollWidth} > ${window.innerWidth}`);
for (const u of document.querySelectorAll('.qe-table th .qe-unit')) {
  if (getComputedStyle(u).textTransform !== 'none' || /\\b(PS|DBM|KHZ|MRAD|MMHG)\\b/.test(u.innerText)) errs.push(`Unit leak: ${u.innerText}`);
}
for (const svg of document.querySelectorAll('svg')) {
  const sr = svg.getBoundingClientRect();
  if (sr.width <= 12 || sr.height <= 12) continue;
  const vb = svg.viewBox?.baseVal;
  if (vb && vb.width > 0) {
    const ar = (sr.width / vb.width) / (sr.height / vb.height);
    if (ar < 0.94 || ar > 1.06) errs.push(`SVG distorted aspect ${ar.toFixed(3)}`);
  }
  const boxes = [];
  for (const t of svg.querySelectorAll('text')) {
    if (!t.textContent?.trim()) continue;
    const cs = getComputedStyle(t);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const ctm = t.getScreenCTM();
    if (ctm && ctm.a > 0) {
      const rfs = parseFloat(cs.fontSize) * Math.hypot(ctm.a, ctm.b);
      if (rfs < 10.0 || rfs > 15.5) errs.push(`SVG text '${t.textContent.trim().slice(0, 20)}' size=${rfs.toFixed(1)}px`);
    }
    const r = t.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      if (r.bottom > sr.bottom + 2 || r.top < sr.top - 2) errs.push(`SVG text clipped '${t.textContent.trim().slice(0, 18)}'`);
      boxes.push({r, txt: t.textContent.trim()});
    }
  }
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const dx = Math.min(boxes[i].r.right, boxes[j].r.right) - Math.max(boxes[i].r.left, boxes[j].r.left);
    const dy = Math.min(boxes[i].r.bottom, boxes[j].r.bottom) - Math.max(boxes[i].r.top, boxes[j].r.top);
    if (dx > 3 && dy > 3) errs.push(`SVG text overlap '${boxes[i].txt.slice(0, 15)}' vs '${boxes[j].txt.slice(0, 15)}'`);
  }
}
for (const eq of document.querySelectorAll('.qe-eq-term[data-term]')) if (eq.tabIndex < 0) errs.push('eqTerm not focusable');
for (const grid of document.querySelectorAll('.qe-scalar-grid')) {
  const rows = new Map();
  for (const c of grid.querySelectorAll(':scope > .qe-scalar-card')) {
    const k = Math.round(c.getBoundingClientRect().top / 8);
    (rows.get(k) || rows.set(k, []).get(k)).push(c);
  }
  for (const cards of rows.values()) if (cards.length >= 2) {
    for (const sel of ['.qe-scalar-title', '.qe-scalar-val-row', 'svg.qe-gauge-svg']) {
      const tops = cards.map(c => c.querySelector(sel)?.getBoundingClientRect().top).filter(Number.isFinite);
      if (tops.length >= 2 && Math.max(...tops) - Math.min(...tops) > 1.0) errs.push(`Baseline drift ${sel}`);
    }
  }
}
if (document.querySelectorAll('.qe-label-pill').length) errs.push('Legacy .qe-label-pill');
return errs;
"""


def _check_bench_page(driver: Any, bench_url: str, errs: list[str]) -> None:
    bgs: set[str] = set()
    for th in ("white", "paper", "dark-paper", "dark"):
        set_viewport(driver, 1440, 900, 1)
        driver.get(f"{bench_url}?theme={th}")
        time.sleep(0.2)
        bgs.add(str(driver.execute_script("return getComputedStyle(document.body).backgroundColor;")))
        errs.extend(f"[BENCH_{th.upper()}] {e}" for e in driver.execute_script(DOM_AUDIT_JS))
    if len(bgs) < 3:
        errs.append(f"[BENCH_THEMES] distinct bgs={bgs}")

    set_viewport(driver, 390, 844, 1)
    driver.get(f"{bench_url}?theme=white")
    time.sleep(0.2)
    errs.extend(f"[BENCH_MOBILE] {e}" for e in driver.execute_script(DOM_AUDIT_JS))

    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{bench_url}?theme=dark&medium=m1")
    time.sleep(0.15)
    m1_err = driver.execute_script(
        "const f=document.querySelector('.qe-figure');return f&&getComputedStyle(f).backgroundColor!=='rgb(255, 255, 255)'?'dark M1 bg not white':'';"
    )
    if m1_err:
        errs.append(f"[BENCH_M1] {m1_err}")

    driver.get(f"{bench_url}?theme=white")
    time.sleep(0.25)
    ec_err = driver.execute_script("""
        const specs = document.querySelectorAll('.qe-specimen');
        if (specs.length !== 41) return 'expected 41 specimens, found ' + specs.length;
        const contracts = document.querySelectorAll('.qe-specimen .qe-data-contract');
        if (contracts.length !== 41) return 'expected 41 data contracts, found ' + contracts.length;
        const tbBtn = document.querySelector('[data-joined-toolbar] .va-tb-btn[data-tb-val="7d"]');
        const tbStatus = document.querySelector('[data-tb-status]');
        if (!tbBtn || !tbStatus) return 'missing joined toolbar specimen 38';
        tbBtn.click();
        if (!tbStatus.textContent.includes('7d')) return 'joined toolbar failed state update';
        const kpiToggle = document.querySelector('[data-kpi-toggle-state]');
        const kpiNote = document.querySelector('[data-kpi-warmup-note]');
        const kpiBar = document.querySelector('[data-kpi-warmup-bar]');
        if (!kpiToggle || !kpiNote || !kpiBar || !kpiNote.textContent.includes('Warming up')) return 'missing warmup KPI specimen 37';
        if (kpiBar.getAttribute('aria-valuenow') !== '6') return 'expected initial warmup aria-valuenow=6';
        kpiToggle.click();
        if (kpiBar.getAttribute('aria-valuenow') !== '72' || !kpiNote.textContent.includes('Steady window')) return 'KPI toggle failed aria-valuenow=72 update';
        kpiToggle.click();
        if (kpiBar.getAttribute('aria-valuenow') !== '6') return 'KPI toggle failed return to warmup';
        const wraps = [...document.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]')];
        if (wraps.length < 11) return 'expected >=11 ECharts specimens, found ' + wraps.length;
        for (const w of wraps) {
            w.querySelector('.qe-mode-btn[data-qe-mode="echarts"]')?.click();
            if (w.dataset.echartsActive !== 'true' || !w.querySelector('.qe-echarts-host svg')) return 'ECharts failed on specimen';
            const ls = w.querySelector('.qe-legend-series');
            if (ls && getComputedStyle(ls).display !== 'none') return 'duplicate legend under active ECharts';
        }
        const drw = document.querySelector('.qe-eco-drawer');
        if (!drw) return 'missing eco drawer';
        drw.open = true;
        const tabs = [...drw.querySelectorAll('.qe-eco-tab[role="tab"]')];
        if (tabs.length !== 5) return 'eco tabs != 5';
        tabs[1].click();
        if (!drw.querySelector('.qe-eco-panel:not([hidden]) pre')?.textContent.includes('go.Scatter')) return 'plotly tab failed';
        drw.querySelector('.qe-copy-btn')?.click();
        document.querySelector('#ui-guarded-and-consumer-controls [data-guard-arm]')?.click();
        document.querySelector('#ui-guarded-and-consumer-controls [data-guard-confirm]')?.click();
        if (!document.querySelector('#ui-guarded-and-consumer-controls [data-guard-state]')?.textContent.includes('EXECUTED')) return 'guard pad failed';
        document.querySelector('#ui-guarded-and-consumer-controls [data-step-delta="0.5"]')?.click();
        if (!document.querySelector('#ui-guarded-and-consumer-controls [data-step-display]')?.textContent.includes('21.5')) return 'stepper failed';
        document.querySelectorAll('#ui-coupled-tree-explorer [data-tree-node]')[1]?.click();
        if (!document.querySelector('#ui-coupled-tree-explorer [data-tree-title]')?.textContent.includes('Worker Queue Pool')) return 'tree explorer failed';
        return '';
    """)
    if ec_err:
        errs.append(f"[BENCH_INTERACT] {ec_err}")


def _check_docs_http_root(driver: Any, errs: list[str]) -> None:
    """Serve docs/ directly as web root (GitHub Pages simulation) and verify 0 404s & 8/8 photos."""
    srv, port = start_http_server(REPO_ROOT / "docs")
    docs_root_url = f"http://127.0.0.1:{port}"
    try:
        set_viewport(driver, 1440, 900, 1)
        for path in ("/", "/bench/evidence-bench.html"):
            driver.get(f"{docs_root_url}{path}")
            time.sleep(0.35)
            failed_res = driver.execute_script(
                "return performance.getEntriesByType('resource').filter(r => r.responseStatus && r.responseStatus >= 400).map(r => r.name + ':' + r.responseStatus);"
            )
            if failed_res:
                errs.append(f"[DOCS_ROOT_404] {path}: {failed_res}")

        # Verify Components tab inside /docs root loads all 41 specimens
        driver.get(f"{docs_root_url}/")
        time.sleep(0.25)
        driver.execute_script("document.getElementById('va-tab-components').click();")
        time.sleep(0.5)
        cnt = driver.execute_script("return document.getElementById('va-stage-portal')?.contentDocument?.querySelectorAll('.qe-specimen').length || 0;")
        if int(cnt) != 41:
            errs.append(f"[DOCS_COMPONENTS_TAB] expected 41 specimens, got {cnt}")

        # Verify all 8 optical/gallery photos resolve cleanly under docs/ web root
        for wid, vid, expected_n in (
            ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", 3),
            ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", 3),
            ("06-smart-home-and-energy", "v17-picture-frame-home-kiosk", 2),
        ):
            driver.get(f"{docs_root_url}/?world={wid}&view={vid}&theme=white")
            time.sleep(0.35)
            loaded = driver.execute_script(
                "const d=document.getElementById('va-stage-portal')?.contentDocument;"
                "return d ? [...d.querySelectorAll('img.v9-opt-photo, img.v17-art-photo')].filter(i => i.complete && i.naturalWidth >= 1200).length : 0;"
            )
            if int(loaded) != expected_n:
                errs.append(f"[DOCS_PHOTOS_{vid}] expected {expected_n} >=1200px photos, got {loaded}")

        # Run portable audit_quiet_html.py CDP checks against docs root pages
        auditor_scripts = REPO_ROOT / "skills" / "quiet-ui" / "scripts"
        if str(auditor_scripts) not in sys.path:
            sys.path.insert(0, str(auditor_scripts))
        from audit_quiet_html import audit_cdp_urls  # noqa: E402

        errs.extend(
            f"[PORTABLE_AUDITOR_CDP] {e}"
            for e in audit_cdp_urls([f"{docs_root_url}/", f"{docs_root_url}/bench/evidence-bench.html"], allow_showcase_chrome=True)
        )
    finally:
        srv.shutdown()
        srv.server_close()


def run_bench_and_docs_gates(driver: Any, base_url: str, root_url: str) -> list[str]:
    """Verify standalone bench (41 specimens, ECharts, UI controls), Studio Components tab, and /docs HTTP root."""
    errs: list[str] = []
    _check_bench_page(driver, f"{root_url}/docs/bench/evidence-bench.html", errs)

    # Verify Studio Examples <-> Components toggle
    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.25)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    time.sleep(0.5)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='components'&&p?.contentDocument?.querySelectorAll('.qe-specimen').length===41;"):
        errs.append("[STUDIO_COMPONENTS_TAB] failed to mount 41 specimens")
    driver.execute_script("document.getElementById('va-tab-examples').click();")
    time.sleep(0.25)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='examples'&&!p.hasAttribute('src');"):
        errs.append("[STUDIO_EXAMPLES_RETURN] failed to return to Examples")

    _check_docs_http_root(driver, errs)
    return errs
