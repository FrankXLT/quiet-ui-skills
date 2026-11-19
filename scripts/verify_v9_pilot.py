#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 4 — World 01 Vertical Pilot CDP & Retina Proof Verifier (<= 400L)."""

from __future__ import annotations

import argparse
import functools
import re
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from verify_v9_helpers import (  # noqa: E402
    STAGE_AUDIT_JS,
    capture_gate41_gallery,
    capture_gate5_gallery,
    set_viewport,
)

REPO_ROOT = SCRIPT_DIR.parent
PILOT_HTML = REPO_ROOT / "docs" / "pilot" / "world-01-pilot.html"
UNIFIED_HTML = REPO_ROOT / "docs" / "v9" / "quiet-ui-v9-showcase.html"
PERSONAL_V9 = REPO_ROOT / "customizations" / "personal-starter" / "showcase-v9.html"
BRAND_V9 = REPO_ROOT / "customizations" / "brand-starter" / "showcase-v9.html"

ALL_WORLDS_VIEWS: list[tuple[str, tuple[str, ...]]] = [
    ("01-clinical-icu-and-trials", ("v01-icu-bedside-terminal", "v02-trial-regulatory-brief", "v03-patient-recovery-companion")),
    ("02-cloud-cyber-and-ai-ops", ("v04-sre-incident-workbench", "v05-zero-trust-ato-spec", "v06-ai-drift-and-lineage-ide")),
    ("03-industrial-grid-and-manufacturing", ("v07-grid-scada-poi-console", "v08-plant-floor-wall-kiosk", "v09-spc-quality-and-modbus-report")),
    ("04-civic-finance-and-stem-learning", ("v10-civic-capital-budget-deck", "v11-treasury-stress-test-solver", "v12-stem-interactive-lab")),
    ("05-physical-systems-auto-and-aero", ("v13-propulsion-archival-monograph", "v14-fieldbus-and-scope-debugger", "v15-collimated-flight-hud", "v16-transparent-window-overlay")),
]


class _QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return


def _start_server() -> tuple[ThreadingHTTPServer, int]:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_QuietHandler, directory=str(REPO_ROOT)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.1)
    return srv, int(srv.server_address[1])


def verify_static(all_worlds: bool = False) -> list[str]:
    errs: list[str] = []
    if not PILOT_HTML.is_file():
        return [f"[MISSING_PILOT] Run build_v9_showcase.py first: {PILOT_HTML}"]
    for p in sorted((REPO_ROOT / "src" / "v9").rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        txt = p.read_text(encoding="utf-8")
        lines = len(txt.splitlines())
        if lines > 450:
            errs.append(f"[LINE_BUDGET] {p.relative_to(REPO_ROOT)} has {lines} lines > 450")
        if p.suffix in {".css", ".html"} and "!important" in txt.lower():
            errs.append(f"[IMPORTANT_VIOLATION] {p.relative_to(REPO_ROOT)} contains !important")
    for p in sorted((REPO_ROOT / "skills" / "quiet-evidence" / "scripts" / "compilers").glob("*.py")):
        lines = len(p.read_text(encoding="utf-8").splitlines())
        if lines > 450:
            errs.append(f"[LINE_BUDGET] {p.relative_to(REPO_ROOT)} has {lines} lines > 450")
    for rel in ("scripts/build_v9_showcase.py", "scripts/verify_v9_pilot.py", "scripts/verify_v9_helpers.py", "tests/test_v9_pilot.py"):
        lines = len((REPO_ROOT / rel).read_text(encoding="utf-8").splitlines())
        if lines > 400:
            errs.append(f"[LINE_BUDGET] {rel} has {lines} lines > 400")
    targets = [PILOT_HTML]
    if all_worlds:
        targets.extend([UNIFIED_HTML, PERSONAL_V9, BRAND_V9])
    for html_p in targets:
        if not html_p.is_file():
            errs.append(f"[MISSING_HTML] Missing build artifact {html_p.relative_to(REPO_ROOT)}")
            continue
        htxt = html_p.read_text(encoding="utf-8")
        if "!important" in htxt.lower():
            errs.append(f"[IMPORTANT_VIOLATION] {html_p.relative_to(REPO_ROOT)} contains !important")
        if "●" in htxt:
            errs.append(f"[BANNED_GLYPH] {html_p.relative_to(REPO_ROOT)} contains literal U+25CF")
        for bad_cdn in ("cdnjs.cloudflare.com", "font-awesome", "fa-solid"):
            if bad_cdn in htxt.lower():
                errs.append(f"[THIRD_PARTY_ICON] {html_p.relative_to(REPO_ROOT)} references '{bad_cdn}'")
    return errs


def _audit_stage(driver: Any, url: str, width: int, height: int, tag: str) -> list[str]:
    set_viewport(driver, width, height, 1)
    driver.get(url)
    for _ in range(15):
        time.sleep(0.08)
        if driver.execute_script("const d=document.getElementById('va-stage-portal')?.contentDocument;const m=d?.getElementById('va-stage-main');return !!(m&&m.children.length&&[...d.querySelectorAll('img.v9-opt-photo')].every(i=>i.complete&&i.naturalWidth>0));"):
            break
    errs: list[str] = []
    bar_err = driver.execute_script(
        "const b=document.getElementById('va-studio-bar');"
        "if(!b) return 'missing #va-studio-bar';"
        "if(b.getBoundingClientRect().height>48.5) return 'bar height='+b.getBoundingClientRect().height;"
        "if(document.documentElement.scrollWidth>document.documentElement.clientWidth+1) return 'studio overflow';"
        "return '';"
    )
    if bar_err:
        errs.append(f"[{tag}_STUDIO] {bar_err}")
    driver.switch_to.frame("va-stage-portal")
    try:
        stage_errs = driver.execute_script(STAGE_AUDIT_JS)
        errs.extend(f"[{tag}] {e}" for e in stage_errs)
    finally:
        driver.switch_to.default_content()
    return errs


def _verify_interactions_and_conservation(driver: Any, base_url: str) -> list[str]:
    errs: list[str] = []
    set_viewport(driver, 1440, 900, 1)
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.28)
    driver.switch_to.frame("va-stage-portal")
    v01_txt = driver.execute_script("return document.body.innerText;")
    for num in ("63.5", "10.2", "94.2", "2.4"):
        if num not in v01_txt:
            errs.append(f"[CONSERVATION_V01] Missing {num}")
    driver.execute_script("document.getElementById('v01-zero-btn').click();document.getElementById('v01-arm-btn').click();document.getElementById('v01-exec-btn').click();")
    after = driver.execute_script("return document.getElementById('v01-norepi-rate').textContent + '|' + document.getElementById('v01-audit-list').textContent;")
    if "0.10" not in after or "EXECUTED" not in after:
        errs.append(f"[V01_TITRATION] Guarded execution failed: {after}")
    if not driver.execute_script("const a=document.querySelector('a[href^=\"#\"]'); if (a) { a.click(); return true; } return false;"):
        errs.append("[SRCDOC_ANCHOR] No #anchor link found in v01")
    driver.switch_to.default_content()

    driver.execute_script("document.getElementById('va-step-next').click();")
    time.sleep(0.2)
    driver.switch_to.frame("va-stage-portal")
    driver.execute_script("document.querySelector('button[data-subgroup=\"sofa\"]').click();")
    if "0.68" not in driver.execute_script("return document.getElementById('v02-filter-readout').textContent;"):
        errs.append("[V02_CHIP] Subgroup chip failed")
    driver.switch_to.default_content()

    driver.execute_script("document.getElementById('va-step-next').click();")
    time.sleep(0.2)
    driver.switch_to.frame("va-stage-portal")
    if driver.execute_script("document.querySelector('.v03-pedagogy-panel button[data-term=\"oxygen-goal\"]').click(); return document.querySelectorAll('.v03-pedagogy-panel .is-term-active').length;") < 2:
        errs.append("[V03_TERM] Pedagogical chip active count < 2")
    driver.switch_to.default_content()

    # Dark -> Print tokens & M1 sheet toggle on v02
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v02-trial-regulatory-brief&theme=dark")
    time.sleep(0.25)
    driver.switch_to.frame("va-stage-portal")
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
    time.sleep(0.12)
    dark_print = driver.execute_script("return getComputedStyle(document.documentElement).getPropertyValue('--tint-emerald-fg').trim().toUpperCase();")
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
    driver.switch_to.default_content()
    if dark_print != "#065F46":
        errs.append(f"[DARK_PRINT_TOKENS] Expected #065F46, got {dark_print}")

    driver.execute_script("document.getElementById('va-customize-btn').click();const m=document.getElementById('va-sheet-medium-select');m.value='m1';m.dispatchEvent(new Event('change'));document.getElementById('va-customize-sheet').close();")
    time.sleep(0.18)
    driver.switch_to.frame("va-stage-portal")
    if not driver.execute_script("return document.documentElement.dataset.medium + '|' + getComputedStyle(document.querySelector('.va-stage')).backgroundColor;").startswith("m1|rgb(255, 255, 255)"):
        errs.append("[M1_SHEET_OLED] M1 sheet failed")
    driver.switch_to.default_content()

    driver.execute_script("document.getElementById('va-bridge-btn').click();")
    time.sleep(0.15)
    if not driver.execute_script("const d=document.getElementById('va-bridge-dialog'),t=d?d.innerText:'';return !!(d&&d.open&&t.includes('0.74')&&!/Murder-Board|QUIET-BRIDGE|Scrubbed|\\.json|_row_status|\\b(?:CL|CR|CC|PR|ER|TRG)-/.test(t));"):
        errs.append("[BRIDGE_DIALOG] Why? Design Rationale dialog missing or leaked jargon")

    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white&vp=fill")
    time.sleep(0.2)
    drag_w = driver.execute_script(
        "const h=document.querySelector('.va-drag-e'), p=document.getElementById('va-stage-portal');"
        "if (!h || !p) return -1; const r=h.getBoundingClientRect();"
        "h.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,clientX:r.left,clientY:r.top+10}));"
        "document.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.left-20,clientY:r.top+10}));"
        "document.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,clientX:r.left-20,clientY:r.top+10}));"
        "return parseInt(p.style.width || '0', 10);"
    )
    if drag_w <= 1000:
        errs.append(f"[FILL_RESIZE] Drag from Fill snapped to {drag_w}px")
    return errs


def _verify_worlds_02_05_and_studio(driver: Any, base_url: str, root_url: str) -> list[str]:
    errs: list[str] = []
    set_viewport(driver, 1440, 900, 1)
    checks = [
        ("02-cloud-cyber-and-ai-ops", "v04-sre-incident-workbench", "document.getElementById('v04-otel-btn').click();document.getElementById('v04-arm-btn').click();document.getElementById('v04-exec-btn').click();return document.getElementById('v04-gate-pill').textContent;", "CANARY ISOLATED"),
        ("02-cloud-cyber-and-ai-ops", "v05-zero-trust-ato-spec", "document.querySelector('#v05-enclave-chips [data-enclave=\"compute\"]').click();return document.getElementById('v05-enclave-readout').textContent;", "SPIFFE"),
        ("03-industrial-grid-and-manufacturing", "v07-grid-scada-poi-console", "document.getElementById('v07-loto-btn').click();document.getElementById('v07-arm-btn').click();document.getElementById('v07-exec-btn').click();return document.getElementById('v07-gate-pill').textContent;", "ISLAND ARMED"),
        ("04-civic-finance-and-stem-learning", "v10-civic-capital-budget-deck", "document.querySelector('#v10-fund-chips [data-fund=\"review\"]').click();return String(document.querySelectorAll('#v10-budget-table tbody tr:not(.v10-row-hidden)').length);", "1"),
        ("04-civic-finance-and-stem-learning", "v11-treasury-stress-test-solver", "document.querySelector('#v11-shock-chips button:last-child').click();return document.getElementById('v11-q8-val').textContent;", "21.4%"),
        ("04-civic-finance-and-stem-learning", "v12-stem-interactive-lab", "document.querySelector('#v12-role-chips [data-role=\"instructor\"]').click();return document.getElementById('v12-instructor-note').className;", "v12-rubric-card"),
        ("05-physical-systems-auto-and-aero", "v14-fieldbus-and-scope-debugger", "document.getElementById('v14-term-btn').click();document.getElementById('v14-arm-btn').click();document.getElementById('v14-exec-btn').click();return document.getElementById('v14-gate-pill').textContent;", "SOF_ARB_ERR W1C OK"),
        ("05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "document.querySelector('#v15-backplate-chips [data-backplate=\"daylight\"]').click();return document.getElementById('v15-hud-stage').dataset.backplate;", "daylight"),
        ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay", "document.querySelector('#v16-luminance-chips [data-luminance=\"night\"]').click();const vp=document.getElementById('v16-glass-viewport');return vp.dataset.luminance+'|'+vp.dataset.contrast;", "night|13.4:1"),
    ]
    for wid, vid, js, expect in checks:
        driver.get(f"{base_url}?world={wid}&view={vid}&theme=white")
        time.sleep(0.24)
        driver.switch_to.frame("va-stage-portal")
        res = str(driver.execute_script(js))
        driver.switch_to.default_content()
        if expect not in res:
            errs.append(f"[W25_INTERACT] {vid}: expected '{expect}', got '{res}'")

    # Verify v16 >= 7.0:1 scrim contrast across all 3 ambient luminance modes & clean Why? dialog
    driver.get(f"{base_url}?domain=05-physical-systems-auto-and-aero&view=v16-transparent-window-overlay&theme=white")
    time.sleep(0.24)
    for lum_mode in ("daylight", "dusk", "night"):
        driver.switch_to.frame("va-stage-portal")
        driver.execute_script(f"document.querySelector('#v16-luminance-chips [data-luminance=\"{lum_mode}\"]').click();")
        time.sleep(0.1)
        errs.extend(f"[V16_{lum_mode.upper()}] {e}" for e in driver.execute_script(STAGE_AUDIT_JS))
        driver.switch_to.default_content()
    for wid, vid in (("02-cloud-cyber-and-ai-ops", "v04-sre-incident-workbench"), ("05-physical-systems-auto-and-aero", "v16-transparent-window-overlay")):
        driver.get(f"{base_url}?domain={wid}&view={vid}&theme=white")
        time.sleep(0.22)
        driver.execute_script("document.getElementById('va-bridge-btn').click();")
        time.sleep(0.12)
        bad_dlg = driver.execute_script("const b=document.getElementById('va-bridge-body').innerText;const m=b.match(/\\bT[123]\\b|\\bv\\d{2}-[a-z0-9]+-[a-z0-9-]+|\\bV\\d{2}:/);return m?m[0]:'';")
        if bad_dlg:
            errs.append(f"[WHY_POLISH] {vid} #va-bridge-body leaked '{bad_dlg}'")

    # M1 unboxed checks across v05, v09, v13
    for wid, vid in (("02-cloud-cyber-and-ai-ops", "v05-zero-trust-ato-spec"), ("03-industrial-grid-and-manufacturing", "v09-spc-quality-and-modbus-report"), ("05-physical-systems-auto-and-aero", "v13-propulsion-archival-monograph")):
        errs.extend(_audit_stage(driver, f"{base_url}?world={wid}&view={vid}&medium=m1&theme=white", 1440, 900, f"M1_{vid[:3].upper()}"))

    # Studio 2-Mode switching: Examples -> Components (21 Specimens) -> Examples
    driver.get(f"{base_url}?domain=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white")
    time.sleep(0.28)
    driver.execute_script("document.getElementById('va-tab-components').click();")
    time.sleep(0.6)
    comp_ok = driver.execute_script(
        "const p=document.getElementById('va-stage-portal'),d=document.querySelector('.va-domain-ctrl'),pd=p&&p.contentDocument;"
        "return !!(document.documentElement.dataset.studioView==='components' && p.src.includes('bench/evidence-bench.html') && "
        "getComputedStyle(d).display==='none' && pd && pd.querySelectorAll('.qe-specimen').length===21 && pd.querySelectorAll('[data-schema-modality=\"schematic\"] svg').length>=6);"
    )
    if not comp_ok:
        errs.append("[STUDIO_MODE] Components tab failed to mount 21-specimen library or hide Domain selector")
    driver.execute_script("document.getElementById('va-tab-examples').click();")
    time.sleep(0.35)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='examples' && !p.hasAttribute('src');"):
        errs.append("[STUDIO_MODE] Failed to return from Components to Examples")

    # Starters check
    for rel, min_views in (("customizations/personal-starter/showcase-v9.html", 16), ("customizations/brand-starter/showcase-v9.html", 14)):
        driver.get(f"{root_url}/{rel}")
        time.sleep(0.35)
        cnt = driver.execute_script("const m=JSON.parse(document.getElementById('va-v9-manifest').textContent);return m.worlds.reduce((a,w)=>a+w.views.length,0);")
        if int(cnt) != min_views:
            errs.append(f"[STARTER_V9] {rel}: expected {min_views} views, got {cnt}")
    return errs


def _verify_phase5_edge_cases(driver: Any, base_url: str, root_url: str) -> list[str]:
    errs: list[str] = []
    # 1. v12 click-to-pin across sibling pedagogy cards & equation bar
    driver.get(f"{base_url}?domain=04-civic-finance-and-stem-learning&view=v12-stem-interactive-lab&theme=white")
    time.sleep(0.28)
    driver.switch_to.frame("va-stage-portal")
    pin_ok = driver.execute_script(
        "const b=document.querySelector('#v12-lab button[data-term=\"tx\"]');b.click();"
        "const a=document.querySelector('#v12-lab article[data-term=\"tx\"]').classList.contains('is-term-active');"
        "const d=document.querySelector('#v12-lab article[data-term=\"path_loss\"]').classList.contains('is-term-dimmed');"
        "b.click();const clr=document.querySelectorAll('#v12-lab .is-term-dimmed').length===0;return a && d && clr;"
    )
    driver.switch_to.default_content()
    if not pin_ok:
        errs.append("[V12_PIN] v12 click-to-pin failed to activate/unpin sibling pedagogy cards")

    # 2. Starter dark/paper theme polarity isolation
    for rel, th, max_lum in (("customizations/personal-starter/showcase-v9.html", "dark", 0.08), ("customizations/brand-starter/showcase-v9.html", "dark", 0.08), ("customizations/personal-starter/showcase-v9.html", "paper", 0.96)):
        driver.get(f"{root_url}/{rel}?theme={th}")
        time.sleep(0.35)
        driver.switch_to.frame("va-stage-portal")
        res = driver.execute_script(
            "const parse=(s)=>(s.match(/[\\d.]+/g)||[0,0,0]).map(Number);"
            "const lum=([r,g,b])=>{const f=v=>{const x=v/255;return x<=0.04045?x/12.92:Math.pow((x+0.055)/1.055,2.4)};return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b);};"
            "const bg=parse(getComputedStyle(document.body).backgroundColor),fg=parse(getComputedStyle(document.body).color);"
            "const l1=lum(bg),l2=lum(fg);return {l1,cr:(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05),th:document.documentElement.dataset.theme};"
        )
        driver.switch_to.default_content()
        if res["th"] != th or res["cr"] < 4.5 or (th == "dark" and res["l1"] > max_lum):
            errs.append(f"[STARTER_POLARITY] {rel}?theme={th} failed: {res}")

    # 3. Direct ?mode=components, legacy ?mode=bench alias, ?domain= & ?view= resolution
    driver.get(f"{base_url}?mode=components&theme=dark&medium=m1")
    time.sleep(0.6)
    driver.execute_script("const m=document.getElementById('va-sheet-medium-select');m.value='auto';m.dispatchEvent(new Event('change'));")
    time.sleep(0.15)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='components' && p.contentDocument.documentElement.dataset.theme==='dark' && p.contentDocument.documentElement.dataset.medium==='m2';"):
        errs.append("[STUDIO_DEEPLINK] ?mode=components failed theme/medium auto restore sync")
    driver.get(f"{base_url}?mode=bench&theme=dark")
    time.sleep(0.6)
    if not driver.execute_script("const p=document.getElementById('va-stage-portal');return document.documentElement.dataset.studioView==='components' && p.src.includes('evidence-bench.html');"):
        errs.append("[STUDIO_DEEPLINK] Legacy ?mode=bench alias failed")
    driver.get(f"{base_url}?view=v10-civic-capital-budget-deck")
    time.sleep(0.3)
    if not driver.execute_script("const s=window.QuietStudioPortalV9.state;return s.world==='04-civic-finance-and-stem-learning' && s.view==='v10-civic-capital-budget-deck';"):
        errs.append("[STUDIO_DEEPLINK] ?view=v10 without ?domain= failed to resolve Domain 04")

    # 4. Decluttered topbar, Settings theme swatch cards, 840px foldable & 390px mobile bar checks
    chrome_err = driver.execute_script(
        "const b=document.getElementById('va-studio-bar'),txt=b?b.innerText:'';"
        "for(const j of ['Worlds','Bench','Atlas','Corpus']) if(txt.includes(j)) return 'Jargon in topbar: '+j;"
        "for(const gone of ['va-sheet-toggle-btn','va-print-btn','va-nav-select','va-vp-select','va-rotate-btn','va-zoom-btn']) if(document.getElementById(gone)) return 'Clutter id: '+gone;"
        "if(document.querySelectorAll('#va-studio-bar .va-theme-dot').length) return 'Theme dots still in topbar';"
        "const sw=document.querySelectorAll('#va-customize-sheet .va-theme-card[data-sheet-theme]');"
        "if(sw.length!==4) return 'Expected 4 theme swatches, got '+sw.length;"
        "for(const c of sw){c.click();if(document.getElementById('va-stage-portal').contentDocument.documentElement.dataset.theme!==c.dataset.sheetTheme) return 'Swatch fail '+c.dataset.sheetTheme;}"
        "return '';"
    )
    if chrome_err:
        errs.append(f"[GATE51_CHROME] {chrome_err}")
    for vp_w, vp_h, min_vw in ((840, 1050, 180), (390, 844, 100)):
        set_viewport(driver, vp_w, vp_h, 1)
        time.sleep(0.15)
        bar_ok = driver.execute_script(f"const b=document.getElementById('va-studio-bar'),s=document.getElementById('va-view-select');return b.scrollWidth<=b.clientWidth+1 && b.getBoundingClientRect().height<=48.5 && s.getBoundingClientRect().width>={min_vw};")
        if not bar_ok:
            errs.append(f"[STUDIO_BAR_{vp_w}] Overflow or view select < {min_vw}px at {vp_w}x{vp_h}")
    return errs


def verify_cdp(screenshots_dir: Path | None = None, all_worlds: bool = False) -> list[str]:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"):
        opts.add_argument(arg)
    srv, port = _start_server()
    root_url = f"http://127.0.0.1:{port}"
    base_url = f"{root_url}/docs/v9/quiet-ui-v9-showcase.html" if all_worlds else f"{root_url}/docs/pilot/world-01-pilot.html"
    worlds = ALL_WORLDS_VIEWS if all_worlds else ALL_WORLDS_VIEWS[:1]
    errs: list[str] = []
    driver = None
    try:
        driver = webdriver.Chrome(options=opts)
        for vp_w, vp_h in ((390, 844), (840, 1050), (1440, 900), (1920, 1080), (3840, 2160)):
            for wid, views in worlds:
                for vw in views:
                    errs.extend(_audit_stage(driver, f"{base_url}?world={wid}&view={vw}&theme=white", vp_w, vp_h, f"{vw.split('-')[0].upper()}_{vp_w}"))
        for th in ("white", "paper", "dark-paper", "dark"):
            errs.extend(_audit_stage(driver, f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme={th}", 1440, 900, f"TH_{th}"))
        errs.extend(_verify_interactions_and_conservation(driver, base_url))
        if all_worlds:
            for th in ("dark-paper", "dark"):
                errs.extend(_audit_stage(driver, f"{base_url}?world=05-physical-systems-auto-and-aero&view=v15-collimated-flight-hud&theme={th}", 1440, 900, f"V15_{th}"))
            errs.extend(_verify_worlds_02_05_and_studio(driver, base_url, root_url))
            errs.extend(_verify_phase5_edge_cases(driver, base_url, root_url))
        if screenshots_dir is not None:
            if all_worlds:
                capture_gate5_gallery(driver, base_url, screenshots_dir)
            else:
                capture_gate41_gallery(driver, base_url, screenshots_dir)
    finally:
        if driver:
            driver.quit()
        srv.shutdown()
        srv.server_close()
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Quiet UI v9.0 Pilot & 5-World CDP Verifier")
    parser.add_argument("--cdp", action="store_true", help="Run Headless Chrome CDP matrix & behavioral gates")
    parser.add_argument("--all-worlds", action="store_true", help="Verify all 5 Worlds x 16 Views on docs/v9/quiet-ui-v9-showcase.html")
    parser.add_argument("--screenshots-dir", default=None, help="Directory to write Retina proof PNGs")
    args = parser.parse_args()

    errs = verify_static(all_worlds=args.all_worlds)
    if args.cdp:
        errs.extend(verify_cdp(Path(args.screenshots_dir) if args.screenshots_dir else None, all_worlds=args.all_worlds))
    if errs:
        print(f"[FAIL] {len(errs)} v9 verification error(s):")
        for e in errs:
            print(f"  - {e}")
        return 1
    scope = "5 Worlds x 16 Views" if args.all_worlds else "World 01 Pilot"
    print(f"[PASS] 100% of Quiet UI v9.0 ({scope}) static & CDP gates succeeded!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
