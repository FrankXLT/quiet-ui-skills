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

from verify_v9_helpers import STAGE_AUDIT_JS, capture_gate41_gallery, set_viewport  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parent
PILOT_HTML = REPO_ROOT / "docs" / "pilot" / "world-01-pilot.html"


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


def verify_static() -> list[str]:
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
    pilot_txt = PILOT_HTML.read_text(encoding="utf-8")
    if "!important" in pilot_txt.lower():
        errs.append("[IMPORTANT_VIOLATION] docs/pilot/world-01-pilot.html contains !important")
    return errs


def _audit_stage(driver: Any, url: str, width: int, height: int, tag: str) -> list[str]:
    set_viewport(driver, width, height, 1)
    driver.get(url)
    time.sleep(0.28)
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
    time.sleep(0.3)

    # 1. Test v01 titration interlock + conservation + step -> v02 -> v03
    driver.switch_to.frame("va-stage-portal")
    v01_txt = driver.execute_script("return document.body.innerText;")
    for num in ("63.5", "10.2", "94.2", "2.4"):
        if num not in v01_txt:
            errs.append(f"[CONSERVATION_V01] Missing {num}")
    driver.execute_script("document.getElementById('v01-zero-btn').click();")
    driver.execute_script("document.getElementById('v01-arm-btn').click();")
    driver.execute_script("document.getElementById('v01-exec-btn').click();")
    after = driver.execute_script("return document.getElementById('v01-norepi-rate').textContent + '|' + document.getElementById('v01-audit-list').textContent;")
    if "0.10" not in after or "EXECUTED" not in after:
        errs.append(f"[V01_TITRATION] Guarded execution failed: {after}")
    has_anchor = driver.execute_script("const a=document.querySelector('a[href^=\"#\"]'); if (a) { a.click(); return true; } return false;")
    if not has_anchor:
        errs.append("[SRCDOC_ANCHOR] No #anchor link found in v01")
    else:
        time.sleep(0.15)
        nav_href = driver.execute_script("return location.href;")
        if not str(nav_href).startswith("about:srcdoc"):
            errs.append(f"[SRCDOC_ANCHOR] Anchor click navigated iframe to {nav_href}")
    driver.switch_to.default_content()

    # Step to v02 & test subgroup chips
    driver.execute_script("document.getElementById('va-step-next').click();")
    time.sleep(0.22)
    driver.switch_to.frame("va-stage-portal")
    if driver.execute_script("return document.documentElement.dataset.view;") != "v02-trial-regulatory-brief":
        errs.append("[STEP_NEXT] Failed to step v01 -> v02")
    v02_txt = driver.execute_script("return document.body.innerText;")
    for num in ("0.74", "11.4", "14.8", "0.68"):
        if num not in v02_txt:
            errs.append(f"[CONSERVATION_V02] Missing {num}")
    driver.execute_script("document.querySelector('button[data-subgroup=\"sofa\"]').click();")
    ro = driver.execute_script("return document.getElementById('v02-filter-readout').textContent;")
    if "0.68" not in ro:
        errs.append(f"[V02_CHIP] Subgroup chip failed: {ro}")
    driver.switch_to.default_content()

    # Step to v03 & test Pedagogical Flow chip + conservation
    driver.execute_script("document.getElementById('va-step-next').click();")
    time.sleep(0.22)
    driver.switch_to.frame("va-stage-portal")
    if driver.execute_script("return document.documentElement.dataset.view;") != "v03-patient-recovery-companion":
        errs.append("[STEP_NEXT] Failed to step v02 -> v03")
    v03_txt = driver.execute_script("return document.body.innerText;")
    for num in ("63.5", "94.2"):
        if num not in v03_txt:
            errs.append(f"[CONSERVATION_V03] Missing {num}")
    act_cnt = driver.execute_script(
        "const b=document.querySelector('.v03-pedagogy-panel button[data-term=\"oxygen-goal\"]');"
        "b.click(); return document.querySelectorAll('.v03-pedagogy-panel .is-term-active').length;"
    )
    if act_cnt < 2:
        errs.append(f"[V03_TERM] Pedagogical chip active count={act_cnt} < 2")
    driver.switch_to.default_content()

    # 2. OLED dark -> direct @media print (medium=auto) & [Sheet / Print] toggle on v02
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v02-trial-regulatory-brief&theme=dark")
    time.sleep(0.28)
    driver.switch_to.frame("va-stage-portal")
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
    time.sleep(0.15)
    dark_print = driver.execute_script(
        "const rs=getComputedStyle(document.documentElement), dlg=document.getElementById('va-shell-drawer');"
        "const wasOpen=dlg&&dlg.open; if(dlg&&!wasOpen) dlg.show();"
        "const disp=dlg?getComputedStyle(dlg).display:'missing';"
        "if(dlg&&!wasOpen) dlg.close();"
        "return rs.getPropertyValue('--tint-emerald-fg').trim().toUpperCase() + '|' + disp;"
    )
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
    driver.switch_to.default_content()
    if dark_print != "#065F46|none":
        errs.append(f"[DARK_PRINT_TOKENS] Expected #065F46|none, got {dark_print}")

    driver.execute_script("document.getElementById('va-sheet-toggle-btn').click();")
    time.sleep(0.2)
    driver.switch_to.frame("va-stage-portal")
    m1_res = driver.execute_script(
        "const st=document.querySelector('.va-stage');"
        "return document.documentElement.dataset.medium + '|' + getComputedStyle(st).backgroundColor + '|' + getComputedStyle(document.querySelector('.v9-masthead-title')).color;"
    )
    if not m1_res.startswith("m1|rgb(255, 255, 255)|rgb(15, 23, 42)"):
        errs.append(f"[M1_SHEET_OLED] Unexpected dark->M1 sheet style: {m1_res}")
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
    time.sleep(0.15)
    pr_res = driver.execute_script(
        "const rail=document.getElementById('va-shell-rail'), top=document.getElementById('va-shell-topbar');"
        "return getComputedStyle(rail).display + '|' + getComputedStyle(top).display + '|' + getComputedStyle(document.body).backgroundColor;"
    )
    driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
    if pr_res != "none|none|rgb(255, 255, 255)":
        errs.append(f"[PRINT_EMULATION] {pr_res}")
    driver.switch_to.default_content()

    # 3. [Why This View?] Quiet-Bridge dialog
    driver.execute_script("document.getElementById('va-bridge-btn').click();")
    time.sleep(0.15)
    br_ok = driver.execute_script(
        "const d=document.getElementById('va-bridge-dialog');"
        "const txt=d?d.innerText:''; return (d && d.open && txt.includes('PASS') && txt.includes('0.74')) ? 'ok' : txt.slice(0,80);"
    )
    if br_ok != "ok":
        errs.append(f"[BRIDGE_DIALOG] {br_ok}")

    # 4. Drag-resize .va-drag-e from Fill mode must keep width > 1000px
    driver.get(f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme=white&vp=fill")
    time.sleep(0.25)
    drag_w = driver.execute_script(
        "const h=document.querySelector('.va-drag-e'), p=document.getElementById('va-stage-portal');"
        "if (!h || !p) return -1; const r=h.getBoundingClientRect();"
        "h.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,clientX:r.left,clientY:r.top+10}));"
        "document.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.left-20,clientY:r.top+10}));"
        "document.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,clientX:r.left-20,clientY:r.top+10}));"
        "return parseInt(p.style.width || '0', 10);"
    )
    if drag_w <= 1000:
        errs.append(f"[FILL_RESIZE] Drag from Fill snapped width to {drag_w}px (<= 1000px)")
    return errs


def verify_cdp(screenshots_dir: Path | None = None) -> list[str]:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"):
        opts.add_argument(arg)
    srv, port = _start_server()
    base_url = f"http://127.0.0.1:{port}/docs/pilot/world-01-pilot.html"
    errs: list[str] = []
    driver = None
    try:
        driver = webdriver.Chrome(options=opts)
        for vp_w, vp_h in ((390, 844), (840, 1050), (1440, 900), (1920, 1080), (3840, 2160)):
            for vw in ("v01-icu-bedside-terminal", "v02-trial-regulatory-brief", "v03-patient-recovery-companion"):
                errs.extend(_audit_stage(driver, f"{base_url}?world=01-clinical-icu-and-trials&view={vw}&theme=white", vp_w, vp_h, f"{vw[:3].upper()}_{vp_w}"))
        for th in ("white", "paper", "dark-paper", "dark"):
            errs.extend(_audit_stage(driver, f"{base_url}?world=01-clinical-icu-and-trials&view=v01-icu-bedside-terminal&theme={th}", 1440, 900, f"TH_{th}"))
        errs.extend(_verify_interactions_and_conservation(driver, base_url))
        if screenshots_dir is not None:
            capture_gate41_gallery(driver, base_url, screenshots_dir)
    finally:
        if driver:
            driver.quit()
        srv.shutdown()
        srv.server_close()
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Quiet UI v9.0 Phase 4 Pilot Verifier")
    parser.add_argument("--cdp", action="store_true", help="Run Headless Chrome CDP matrix & behavioral gates")
    parser.add_argument("--screenshots-dir", default=None, help="Directory to write 9 Retina Gate 4 PNGs")
    args = parser.parse_args()

    errs = verify_static()
    if args.cdp:
        errs.extend(verify_cdp(Path(args.screenshots_dir) if args.screenshots_dir else None))
    if errs:
        print(f"[FAIL] {len(errs)} Phase 4 pilot verification error(s):")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("[PASS] 100% of Quiet UI v9.0 Phase 4 Pilot static & CDP gates succeeded!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
