# SPDX-License-Identifier: Apache-2.0
"""Component Library (39 Specimens), Live ECharts, /docs Standalone Root & Portable Auditor CDP Gates."""

from __future__ import annotations

import struct
import sys
import time
import urllib.request
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


BENCH_INTERACT_JS = """
const specs = document.querySelectorAll('.qe-specimen'), contracts = document.querySelectorAll('.qe-specimen .qe-data-contract');
if (specs.length !== 53) return 'expected 53 specimens, found ' + specs.length;
if (contracts.length !== 53) return 'expected 53 data contracts, found ' + contracts.length;
const s45 = document.getElementById('m4-l1-us-hex-tile-map');
if (!s45 || s45.querySelectorAll('.va-hex-tile').length !== 51) return 'Specimen 45 missing 51 US hex tiles';
const s44 = document.getElementById('qe-forms-zero-states');
if (!s44) return 'missing Specimen 44 #qe-forms-zero-states';
const s44Inp = s44.querySelector('#s44-threshold-input'), s44Err = s44.querySelector('#s44-threshold-err');
if (!s44Inp || !s44Err || s44Inp.getAttribute('aria-invalid') !== 'false') return 'Specimen 44 missing validated threshold input';
s44Inp.value = '2'; s44Inp.dispatchEvent(new Event('blur', { bubbles: true }));
if (s44Inp.getAttribute('aria-invalid') !== 'true' || s44Err.hidden) return 'Specimen 44 blur failed to mark invalid';
s44Inp.value = '300'; s44Inp.dispatchEvent(new Event('input', { bubbles: true }));
if (s44Inp.getAttribute('aria-invalid') !== 'false' || !s44Err.hidden) return 'Specimen 44 input failed to clear error';
s44.querySelector('[data-s44-archive]')?.click(); s44.querySelector('[data-s44-archive]')?.click();
if (s44.querySelector('[data-s44-toast]')?.hidden !== false) return 'Specimen 44 undo toast did not reveal';
s44.querySelector('[data-s44-undo]')?.click();
if (s44.querySelector('[data-s44-toast]')?.hidden !== true || !s44.querySelector('[data-s44-rule-pill]')?.textContent.includes('Active')) return 'Specimen 44 Undo failed';
s44.querySelector('[data-s44-archive]')?.click(); s44.querySelector('[data-s44-save]')?.click();
if (s44.querySelector('[data-s44-toast]')?.hidden !== true || !s44.querySelector('[data-s44-rule-pill]')?.textContent.includes('Active')) return 'Specimen 44 Save failed to dismiss toast';
s44.querySelector('[data-s44-clear-filters]')?.click(); if (!s44.querySelector('[data-s44-filtered-title]')?.textContent.includes('Filters cleared')) return 'Specimen 44 Clear filters failed';
s44.querySelector('[data-s44-reapply-filters]')?.click(); s44.querySelector('#s44-tab-stale')?.click();
if (s44.querySelector('#s44-panel-stale')?.hidden !== false) return 'Specimen 44 Stale tab switch failed';
s44.querySelector('#s44-tab-filtered')?.click();
const cyc = document.querySelector('#qe-cyclical-whiskers .qe-plot-wrap[data-quiet-echarts]');
if (!cyc || cyc.dataset.echartsActive !== 'true' || !cyc.querySelector('.qe-echarts-host svg')) return 'Specimen 43 #qe-cyclical-whiskers failed to default to Live ECharts';
cyc.querySelector('.qe-mode-btn[data-qe-mode="svg"]')?.click(); if (cyc.dataset.echartsActive !== 'false') return 'Specimen 43 SVG fallback toggle failed';
cyc.querySelector('.qe-mode-btn[data-qe-mode="echarts"]')?.click();
const pTrig = document.querySelector('#ui-period-stepper-popover .va-period-trigger'), pPop = document.querySelector('#ui-period-stepper-popover .va-preset-popover'), pStatus = document.querySelector('[data-stepper-status]');
if (!pTrig || !pPop || !pStatus) return 'missing period stepper specimen 42';
pTrig.click(); if (pPop.hasAttribute('hidden') || pTrig.getAttribute('aria-expanded') !== 'true') return 'period popover failed to open';
const r52Btn = pPop.querySelector('[data-preset="r52w"]'); if (!r52Btn) return 'missing Last 52w rolling preset';
r52Btn.click(); if (!pStatus.textContent.includes('Last 52w') || !pStatus.textContent.includes('1w')) return 'period stepper failed rolling 52w selection';
document.querySelector('#ui-period-stepper-popover [data-preset="mtd"]')?.click();
const tbBtn = document.querySelector('[data-joined-toolbar] .va-tb-btn[data-tb-val="7d"]'), tbStatus = document.querySelector('[data-tb-status]');
if (!tbBtn || !tbStatus) return 'missing joined toolbar specimen 38';
tbBtn.click(); if (!tbStatus.textContent.includes('7d')) return 'joined toolbar failed state update';
const kpiToggle = document.querySelector('[data-kpi-toggle-state]'), kpiNote = document.querySelector('[data-kpi-warmup-note]'), kpiBar = document.querySelector('[data-kpi-warmup-bar]');
if (!kpiToggle || !kpiNote || !kpiBar || !kpiNote.textContent.includes('Warming up')) return 'missing warmup KPI specimen 37';
if (kpiBar.getAttribute('aria-valuenow') !== '6') return 'expected initial warmup aria-valuenow=6';
kpiToggle.click(); if (kpiBar.getAttribute('aria-valuenow') !== '72' || !kpiNote.textContent.includes('Steady window')) return 'KPI toggle failed aria-valuenow=72 update';
kpiToggle.click(); if (kpiBar.getAttribute('aria-valuenow') !== '6') return 'KPI toggle failed return to warmup';
const wraps = [...document.querySelectorAll('.qe-plot-wrap[data-quiet-echarts]')];
if (wraps.length < 12) return 'expected >=12 ECharts specimens, found ' + wraps.length;
for (const w of wraps) {
  w.querySelector('.qe-mode-btn[data-qe-mode="echarts"]')?.click();
  if (w.dataset.echartsActive !== 'true' || !w.querySelector('.qe-echarts-host svg')) return 'ECharts failed on specimen';
  const ls = w.querySelector('.qe-legend-series');
  if (ls && getComputedStyle(ls).display !== 'none') return 'duplicate legend under active ECharts';
}
const drw = document.querySelector('.qe-eco-drawer');
if (!drw) return 'missing eco drawer';
drw.open = true; const tabs = [...drw.querySelectorAll('.qe-eco-tab[role="tab"]')];
if (tabs.length !== 5) return 'eco tabs != 5';
tabs[1].click(); if (!drw.querySelector('.qe-eco-panel:not([hidden]) pre')?.textContent.includes('go.Scatter')) return 'plotly tab failed';
drw.querySelector('.qe-copy-btn')?.click();
document.querySelector('#ui-guarded-and-consumer-controls [data-guard-arm]')?.click(); document.querySelector('#ui-guarded-and-consumer-controls [data-guard-confirm]')?.click();
if (!document.querySelector('#ui-guarded-and-consumer-controls [data-guard-state]')?.textContent.includes('EXECUTED')) return 'guard pad failed';
document.querySelector('#ui-guarded-and-consumer-controls [data-step-delta="0.5"]')?.click();
if (!document.querySelector('#ui-guarded-and-consumer-controls [data-step-display]')?.textContent.includes('21.5')) return 'stepper failed';
document.querySelectorAll('#ui-coupled-tree-explorer [data-tree-node]')[1]?.click();
if (!document.querySelector('#ui-coupled-tree-explorer [data-tree-title]')?.textContent.includes('Worker Queue Pool')) return 'tree explorer failed';
return '';
"""


def _poll_js(driver: Any, script: str, *args: Any, timeout: float = 3.0) -> bool:
    """Poll a boolean JS predicate until truthy or timeout expires."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if driver.execute_script(script, *args):
            return True
        time.sleep(0.08)
    return bool(driver.execute_script(script, *args))


def _collect_theme_bgs(driver: Any) -> set[str]:
    """Cycle #oaw-user-popover theme buttons across all 4 themes and return distinct body bgs."""
    bgs: set[str] = set()
    for th in ("white", "paper", "dark-paper", "dark"):
        bg = driver.execute_script(
            "if(document.getElementById('oaw-theme-select')) return '';"
            "const b=document.querySelector(`.oaw-theme-opt[data-theme-opt='${arguments[0]}']`);"
            "if(!b) return ''; b.click();"
            "return document.documentElement.dataset.theme===arguments[0] ? getComputedStyle(document.body).backgroundColor : '';",
            th,
        )
        if bg:
            bgs.add(str(bg))
    return bgs


def _check_bench_page(driver: Any, bench_url: str, errs: list[str]) -> None:
    """Audit bench themes, mobile layout, M1 dark print ground, and 53 interactive specimens."""
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
    ec_err = driver.execute_script(BENCH_INTERACT_JS)
    if ec_err:
        errs.append(f"[BENCH_INTERACT] {ec_err}")


def _check_docs_routes_and_social(driver: Any, docs_root_url: str, errs: list[str]) -> None:
    """Verify zero 4xx/5xx responses across routes and 1280x640 social preview image."""
    set_viewport(driver, 1440, 900, 1)
    for path in ("/", "/demo/", "/docs/", "/bench/evidence-bench.html"):
        driver.get(f"{docs_root_url}{path}")
        time.sleep(0.3)
        failed = driver.execute_script(
            "return [...performance.getEntriesByType('navigation'), ...performance.getEntriesByType('resource')]"
            ".filter(r => r.responseStatus && r.responseStatus >= 400).map(r => r.name + ':' + r.responseStatus);"
        )
        if failed:
            errs.append(f"[DOCS_ROOT_404] {path}: {failed}")

    try:
        with urllib.request.urlopen(f"{docs_root_url}/assets/quiet-ui-social.png", timeout=5) as resp:
            raw = resp.read(250_001)
            dims = struct.unpack(">II", raw[16:24]) if len(raw) >= 24 else (0, 0)
            if resp.status != 200 or not (0 < len(raw) <= 250_000) or not raw.startswith(b"\x89PNG\r\n\x1a\n") or dims != (1280, 640):
                errs.append(f"[DOCS_SOCIAL_PNG] HTTP {resp.status} len={len(raw)} dims={dims[0]}x{dims[1]}")
    except Exception as exc:
        errs.append(f"[DOCS_SOCIAL_PNG] {exc}")


def _check_docs_overview_route(driver: Any, docs_root_url: str, errs: list[str]) -> None:
    """Audit Route 1 `/` Overview across 390/900/1440px and 4-theme switching."""
    for vp_w, vp_h in ((390, 844), (900, 900), (1440, 900)):
        set_viewport(driver, vp_w, vp_h, 1)
        driver.get(f"{docs_root_url}/?theme=white")
        time.sleep(0.2)
        ov_err = driver.execute_script(
            "if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) return 'horizontal overflow';"
            "const tb = document.querySelector('.oaw-topbar'), r = tb ? tb.getBoundingClientRect() : null;"
            "if (!r || r.height < 44 || r.height > 48) return 'invalid .oaw-topbar height=' + (r ? r.height : 0);"
            "if (document.getElementById('oaw-theme-select')) return 'unexpected #oaw-theme-select';"
            "for (const [bid, pid] of [['oaw-projects-btn','oaw-projects-popover'],['oaw-pillar-btn','oaw-pillar-popover'],['oaw-user-btn','oaw-user-popover']]) {"
            "  const btn = document.getElementById(bid), pop = document.getElementById(pid);"
            "  if (!btn || !pop) return 'missing ' + bid + ' or ' + pid;"
            "  btn.click(); const open = (typeof pop.matches==='function'&&pop.matches(':popover-open'))||pop.getAttribute('data-open')==='true';"
            "  if (!open) return pid + ' failed to open';"
            "  if (typeof pop.hidePopover==='function'&&pop.matches(':popover-open')) pop.hidePopover(); else btn.click();"
            "}"
            "if (!document.querySelector('.oaw-showcase-card .oaw-quickstart-box') || !document.querySelector('.oaw-cmd-slug')) return 'missing hero slugs or showcase';"
            "const svgs = [...document.querySelectorAll('.oaw-compiled-diagram svg, .oaw-diagram-panel svg')];"
            "if (!svgs.some(s => {const x=s.getBoundingClientRect(); return x.width>50 && x.height>30;})) return 'missing compiled architecture SVG';"
            "const ctas = [...document.querySelectorAll('.oaw-cta-row a')].map(a => a.getAttribute('href') || '');"
            "if (!ctas.some(h => h.includes('demo/index.html')) || !ctas.some(h => h.includes('docs/index.html'))) return 'missing demo/docs CTAs';"
            "const cmds = [...document.querySelectorAll('.oaw-install-cmd')];"
            "return (!cmds.length || cmds.some(c => !c.querySelector('code')?.textContent?.trim() || !c.querySelector('.oaw-copy-btn[data-copy-text]'))) ? 'invalid install cmds' : '';"
        )
        if ov_err:
            errs.append(f"[DOCS_OVERVIEW_{vp_w}] {ov_err}")

    bgs = _collect_theme_bgs(driver)
    if len(bgs) < 3:
        errs.append(f"[DOCS_OVERVIEW_THEMES] expected >=3 distinct bgs, got {bgs}")


def _check_docs_legacy_and_demo_route(driver: Any, docs_root_url: str, errs: list[str]) -> None:
    """Verify legacy deep-link redirects from `/`, Route 2 `/demo/` components tab, and 8 optical photos."""
    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{docs_root_url}/?mode=components")
    if not _poll_js(
        driver,
        "const p=document.getElementById('va-stage-portal');"
        "return location.pathname.endsWith('/demo/index.html') && location.search.includes('mode=components')"
        " && p?.contentDocument?.querySelectorAll('.qe-specimen').length === 53;",
    ):
        errs.append("[DOCS_LEGACY_COMPONENTS] /?mode=components failed redirect or 53-specimen mount")

    driver.get(f"{docs_root_url}/?world=04-civic-finance-and-stem-learning&view=v10-civic-capital-budget-deck")
    _poll_js(
        driver,
        "const d=document.getElementById('va-stage-portal')?.contentDocument;"
        "return location.pathname.endsWith('/demo/index.html') && d?.documentElement?.dataset?.view==='v10-civic-capital-budget-deck'"
        " && (d.getElementById('va-stage-main')?.children.length || 0) > 0;",
    )
    v10_err = driver.execute_script(
        "if (!location.pathname.endsWith('/demo/index.html')) return 'not redirected to /demo/index.html';"
        "const d=document.getElementById('va-stage-portal')?.contentDocument;"
        "if (d?.documentElement?.dataset?.view !== 'v10-civic-capital-budget-deck') return 'v10 not loaded';"
        "const strip=document.querySelector('.va-demo-site-strip');"
        "if (!strip || getComputedStyle(strip).position !== 'static') return 'invalid .va-demo-site-strip position';"
        "const h = strip.getBoundingClientRect().height; if (h < 44 || h > 48) return 'strip height=' + h;"
        "if (!strip.querySelector('.oaw-topbar-left .oaw-nav-links')) return 'nav tabs not inside .oaw-topbar-left';"
        "const opt=document.querySelector('.oaw-theme-opt[data-theme-opt=\"paper\"]'); if(!opt) return 'missing demo theme opt';"
        "opt.click(); if (d.documentElement.dataset.theme !== 'paper') return 'demo user menu theme sync failed';"
        "const ov=document.getElementById('va-tab-overview');"
        "return (ov && getComputedStyle(ov).display !== 'none' && !ov.hidden) ? '#va-tab-overview not hidden' : '';"
    )
    if v10_err:
        errs.append(f"[DOCS_LEGACY_V10] {v10_err}")

    driver.get(f"{docs_root_url}/demo/")
    time.sleep(0.25)
    driver.execute_script("document.getElementById('va-tab-components')?.click();")
    if not _poll_js(driver, "return document.getElementById('va-stage-portal')?.contentDocument?.querySelectorAll('.qe-specimen').length === 53;"):
        errs.append("[DOCS_DEMO_COMPONENTS] expected 53 specimens on /demo/")

    for wid, vid, expected_n in (
        ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", 3),
        ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", 3),
        ("06-smart-home-and-energy", "v17-picture-frame-home-kiosk", 2),
    ):
        driver.get(f"{docs_root_url}/demo/?world={wid}&view={vid}&theme=white")
        ok_ph = _poll_js(
            driver,
            "const d=document.getElementById('va-stage-portal')?.contentDocument;"
            "return d && [...d.querySelectorAll('img.v9-opt-photo, img.v17-art-photo')].filter(i=>i.complete&&i.naturalWidth>=1200).length===arguments[0];",
            expected_n,
        )
        if not ok_ph:
            errs.append(f"[DOCS_DEMO_PHOTOS_{vid}] expected {expected_n} >=1200px photos")


def _check_docs_reader_route(driver: Any, docs_root_url: str, errs: list[str]) -> None:
    """Audit Route 3 `/docs/` across 390/900/1440px, search filter + recovery, 4 themes, and mobile TOC dialog."""
    for vp_w, vp_h in ((390, 844), (900, 900), (1440, 900)):
        set_viewport(driver, vp_w, vp_h, 1)
        driver.get(f"{docs_root_url}/docs/?theme=white")
        time.sleep(0.2)
        doc_err = driver.execute_script(
            "if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) return 'horizontal overflow';"
            "const svgs = [...document.querySelectorAll('.oaw-compiled-diagram svg')];"
            "if (!svgs.some(s => {const r=s.getBoundingClientRect(); return r.width>50 && r.height>30;})) return 'missing .oaw-compiled-diagram svg';"
            "return document.querySelectorAll('[data-doc-jump]').length ? '' : 'missing [data-doc-jump] quick-jumps';"
        )
        if doc_err:
            errs.append(f"[DOCS_READER_{vp_w}] {doc_err}")

    search_err = driver.execute_script(
        "const secs = [...document.querySelectorAll('.oaw-docs-section, .oaw-doc-section')];"
        "const inp = document.getElementById('oaw-docs-search'), empty = document.querySelector('#oaw-docs-empty.va-empty-state[data-kind=\"filtered\"]');"
        "const clr = document.getElementById('oaw-empty-clear-btn');"
        "if (!secs.length || !inp || !empty || !clr) return 'missing docs search/empty DOM';"
        "const vis = () => secs.filter(s => !s.hidden).length;"
        "inp.value = 'brand'; inp.dispatchEvent(new Event('input', { bubbles: true }));"
        "if (vis() <= 0 || vis() >= secs.length || !empty.hidden) return 'brand search filter unexpected count';"
        "inp.value = 'zzzxqynonexistent999'; inp.dispatchEvent(new Event('input', { bubbles: true }));"
        "if (vis() !== 0 || empty.hidden || getComputedStyle(empty).display === 'none') return 'zero-results empty state failed';"
        "clr.click();"
        "return (inp.value === '' && empty.hidden && vis() === secs.length) ? '' : 'clear search failed to restore';"
    )
    if search_err:
        errs.append(f"[DOCS_READER_SEARCH] {search_err}")

    bgs = _collect_theme_bgs(driver)
    if len(bgs) < 3:
        errs.append(f"[DOCS_READER_THEMES] expected >=3 distinct bgs, got {bgs}")

    set_viewport(driver, 390, 844, 1)
    driver.get(f"{docs_root_url}/docs/?theme=white")
    time.sleep(0.2)
    toc_err = driver.execute_script(
        "const t=document.getElementById('oaw-docs-toc-trigger'), d=document.getElementById('oaw-docs-toc-dialog');"
        "if (!t || !d || getComputedStyle(t).display === 'none') return 'missing/hidden #oaw-docs-toc-trigger';"
        "t.click(); if (!d.open) return 'TOC dialog failed to open';"
        "if (typeof d.close === 'function') d.close(); return '';"
    )
    if toc_err:
        errs.append(f"[DOCS_READER_MOBILE_TOC] {toc_err}")


def _check_docs_http_root(driver: Any, errs: list[str]) -> None:
    """Serve docs/ and project-site-starter/site as web roots and run three-route + auditor CDP gates."""
    auditor_scripts = REPO_ROOT / "skills" / "quiet-ui" / "scripts"
    if str(auditor_scripts) not in sys.path:
        sys.path.insert(0, str(auditor_scripts))
    from audit_quiet_html import audit_cdp_urls  # noqa: E402

    srv, port = start_http_server(REPO_ROOT / "docs")
    docs_root_url = f"http://127.0.0.1:{port}"
    try:
        _check_docs_routes_and_social(driver, docs_root_url, errs)
        _check_docs_overview_route(driver, docs_root_url, errs)
        _check_docs_legacy_and_demo_route(driver, docs_root_url, errs)
        _check_docs_reader_route(driver, docs_root_url, errs)
        docs_urls = [f"{docs_root_url}/", f"{docs_root_url}/demo/", f"{docs_root_url}/docs/", f"{docs_root_url}/bench/evidence-bench.html"]
        errs.extend(f"[PORTABLE_AUDITOR_CDP] {e}" for e in audit_cdp_urls(docs_urls, allow_showcase_chrome=True))
    finally:
        srv.shutdown()
        srv.server_close()

    starter_srv, starter_port = start_http_server(REPO_ROOT / "customizations" / "project-site-starter" / "site")
    starter_url = f"http://127.0.0.1:{starter_port}"
    try:
        errs.extend(f"[STARTER_AUDITOR_CDP] {e}" for e in audit_cdp_urls([f"{starter_url}/", f"{starter_url}/docs/"], allow_showcase_chrome=False))
    finally:
        starter_srv.shutdown()
        starter_srv.server_close()


def run_bench_and_docs_gates(driver: Any, base_url: str, root_url: str) -> list[str]:
    """Verify standalone bench (53 specimens, ECharts, UI controls), Studio Components tab, and /docs HTTP root."""
    errs: list[str] = []
    _check_bench_page(driver, f"{root_url}/docs/bench/evidence-bench.html", errs)

    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.25)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    time.sleep(0.5)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='components'&&p?.contentDocument?.querySelectorAll('.qe-specimen').length===53;"):
        errs.append("[STUDIO_COMPONENTS_TAB] failed to mount 53 specimens")
    driver.execute_script("document.getElementById('va-tab-examples').click();")
    time.sleep(0.25)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='examples'&&!p.hasAttribute('src');"):
        errs.append("[STUDIO_EXAMPLES_RETURN] failed to return to Examples")

    _check_docs_http_root(driver, errs)
    _check_echarts_legend_guards(driver, f"{root_url}/docs/bench/evidence-bench.html", errs)
    return errs


def _check_echarts_legend_guards(driver: Any, bench_url: str, errs: list[str]) -> None:
    """Verify QuietEChartsDefaults.applySafeLegendLayout renders clean 390px SVG legends in Chrome."""
    set_viewport(driver, 390, 844, 1)
    driver.get(f"{bench_url}?theme=white")
    time.sleep(0.25)
    msg = driver.execute_script("""
        const D = window.QuietEChartsDefaults;
        if (!D || typeof D.applySafeLegendLayout !== 'function' || typeof window.echarts === 'undefined') return 'missing QuietEChartsDefaults';
        const opt = D.normalizeOption({
          animation: false, legend: { type: 'scroll', top: 2, right: 8, data: ['Payload (KB)', 'RPC Calls', 'SLA Ceiling', 'Warmup Avg'] },
          grid: { left: 10, right: 16, top: 30, bottom: 20, containLabel: true }, xAxis: { type: 'category', data: ['IDE', 'Cloud', 'CLI'] },
          yAxis: [{ type: 'value', name: 'KB' }, { type: 'value', name: 'Calls' }],
          series: [{ name: 'Payload (KB)', type: 'bar', yAxisIndex: 0, data: [12, 18, 9] }, { name: 'RPC Calls', type: 'bar', yAxisIndex: 1, data: [40, 22, 14] },
                   { name: 'SLA Ceiling', type: 'line', yAxisIndex: 0, data: [20, 20, 20] }, { name: 'Warmup Avg', type: 'line', yAxisIndex: 0, data: [10, 14, 11] }]
        }, null, null, 350);
        if (opt.legend.type !== 'plain' || opt.legend.bottom !== 0 || opt.legend.top !== undefined) return 'legend not normalized at 350px';
        if (opt.grid.bottom < 46) return 'grid.bottom too small: ' + opt.grid.bottom;
        const resOpt = D.normalizeOption({ legend: { top: 2, left: 64, data: ['Meas', 'Model'] }, grid: [{ top: 44, bottom: 132 }, { bottom: 46, height: 64 }],
          xAxis: [{ gridIndex: 0 }, { gridIndex: 1 }], yAxis: [{ gridIndex: 0 }, { gridIndex: 1 }], series: [] }, null, null, 350);
        if (resOpt.legend.top !== 2) return 'multi-grid residual legend wrongly moved';
        const box = document.createElement('div'); box.style.cssText = 'width:350px;height:260px;'; document.body.appendChild(box);
        const chart = window.echarts.init(box, null, { renderer: 'svg', width: 350, height: 260 });
        chart.setOption(opt, true);
        const texts = [...box.querySelectorAll('svg text')].map(t => ({ txt: (t.textContent || '').trim(), r: t.getBoundingClientRect() })).filter(x => x.txt && x.r.width > 0);
        if (texts.some(x => x.txt === '1/2')) { chart.dispose(); box.remove(); return 'scroll paginator 1/2 rendered'; }
        for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
          const ovW = Math.min(texts[i].r.right, texts[j].r.right) - Math.max(texts[i].r.left, texts[j].r.left);
          const ovH = Math.min(texts[i].r.bottom, texts[j].r.bottom) - Math.max(texts[i].r.top, texts[j].r.top);
          if (ovW > 2.5 && ovH > 4.5) { const bad = texts[i].txt + ' vs ' + texts[j].txt; chart.dispose(); box.remove(); return 'overlap at 350px: ' + bad; }
        }
        chart.dispose(); box.remove(); return '';
    """)
    if msg:
        errs.append(f"[ECHARTS_LEGEND_GUARD] {msg}")
