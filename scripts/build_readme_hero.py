#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.3 — Reproducible README 2x2 Hero Banner Builder (1600x920, <= 280 KB)."""
from __future__ import annotations

import base64
import functools
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "docs" / "assets" / "quiet-ui-hero.png"
BOLD_FONT_CANDIDATES = (
    "/usr/share/fonts/google-carlito-fonts/Carlito-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)
MONO_FONT_CANDIDATES = (
    "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf",
    "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Menlo.ttc",
    "C:/Windows/Fonts/consola.ttf",
)
CAP_W, CAP_H, PANEL_W, PANEL_H, HDR_H = 1440, 746, 770, 425, 26


class _SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return


def _font(candidates: tuple[str, ...], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _shot(driver: Any) -> Image.Image:
    time.sleep(0.3)
    raw = driver.execute_cdp_cmd("Page.captureScreenshot", {"format": "png", "fromSurface": True})["data"]
    return Image.open(BytesIO(base64.b64decode(raw))).convert("RGB").resize((PANEL_W, PANEL_H - HDR_H), Image.Resampling.LANCZOS)


def _capture_showcase(
    driver: Any, base_url: str, wid: str, vid: str, theme: str, extra_js: str = "", fit_sel: str = ""
) -> Image.Image:
    cap_w, cap_h = CAP_W, CAP_H
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": cap_w, "height": cap_h, "deviceScaleFactor": 1.0, "mobile": False})
    driver.get(f"{base_url}/quiet-ui-showcase.html?world={wid}&view={vid}&theme={theme}&vp=fill")
    for _ in range(50):
        ok = driver.execute_script(
            "const f=document.getElementById('va-stage-portal'),d=f&&f.contentDocument,m=d&&d.getElementById('va-stage-main');"
            "if(!m||!m.children.length||!d||d.documentElement.dataset.view!==arguments[0])return false;"
            "return [...d.querySelectorAll('img')].filter(i=>getComputedStyle(i).display!=='none').every(i=>i.complete&&i.naturalWidth>0);",
            vid,
        )
        if ok:
            break
        time.sleep(0.08)
    if fit_sel:
        need_h = driver.execute_script(
            "const f=document.getElementById('va-stage-portal'),d=f&&f.contentDocument,el=d&&d.querySelector(arguments[0]);"
            "return el ? Math.ceil(el.getBoundingClientRect().bottom + 14) : 0;",
            fit_sel,
        )
        if need_h and int(need_h) > cap_h:
            cap_h = int(need_h)
            cap_w = round(cap_h * PANEL_W / (PANEL_H - HDR_H))
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": cap_w, "height": cap_h, "deviceScaleFactor": 1.0, "mobile": False})
            time.sleep(0.12)
    driver.execute_script(
        "const bar=document.getElementById('va-studio-bar');if(bar)bar.style.display='none';"
        "['va-portal-mat','va-portal-scaler','va-stage-portal'].forEach(id=>{const el=document.getElementById(id);if(el){el.style.height=arguments[0]+'px';el.style.minHeight=arguments[0]+'px';}});"
        "const f=document.getElementById('va-stage-portal'),d=f&&f.contentDocument;"
        + extra_js +
        "if(f&&f.contentWindow&&f.contentWindow.QuietEChartsAdapter)f.contentWindow.QuietEChartsAdapter.refresh(d);",
        cap_h,
    )
    return _shot(driver)


def _capture_bench(driver: Any, base_url: str) -> Image.Image:
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": CAP_W, "height": CAP_H, "deviceScaleFactor": 1.0, "mobile": False})
    driver.get(f"{base_url}/docs/bench/evidence-bench.html?theme=dark-paper")
    for _ in range(50):
        if driver.execute_script("return document.querySelectorAll('.qe-specimen').length===44&&!!window.QuietEChartsAdapter;"):
            break
        time.sleep(0.08)
    driver.execute_script(
        "document.querySelectorAll('.qe-topbar,.qe-bench-summary').forEach(el=>el.style.display='none');"
        "const mn=document.getElementById('bench-main');if(mn){mn.style.padding='14px 18px';mn.style.maxWidth='none';}"
        "const gr=document.querySelector('.qe-bench-grid');if(gr){gr.style.gridTemplateColumns='repeat(2,minmax(0,1fr))';gr.style.gap='14px';}"
        "document.querySelectorAll('.qe-specimen').forEach(c=>{const t=c.textContent||'';const keep=t.includes('Critical-Path Release Timeline')||t.includes('Zero-Trust ATO Enclave');"
        "if(!keep)c.setAttribute('hidden','');else{c.classList.remove('qe-specimen-wide');"
        "c.querySelectorAll('.qe-spec-drawer,.qe-eco-drawer').forEach(d=>d.style.display='none');"
        "c.querySelectorAll('.qe-mode-btn[data-qe-mode=\"echarts\"]').forEach(b=>b.click());}});"
        "if(window.QuietEChartsAdapter)window.QuietEChartsAdapter.refresh(document);"
    )
    return _shot(driver)


def _composite(panels: list[tuple[str, str, Image.Image]]) -> Image.Image:
    canvas = Image.new("RGB", (1600, 920), "#0F172A")
    draw = ImageDraw.Draw(canvas)
    f_title, f_sub, f_tag = _font(BOLD_FONT_CANDIDATES, 19), _font(MONO_FONT_CANDIDATES, 12), _font(BOLD_FONT_CANDIDATES, 13)
    draw.rectangle([0, 0, 1600, 42], fill="#0B1120")
    draw.line([(0, 42), (1600, 42)], fill="#1E293B", width=1)
    draw.text((24, 10), "QUIET UI v9.5", fill="#38BDF8", font=f_title)
    draw.text((152, 14), "6-Domain Studio (21 Views)  ·  44 Modular Evidence & UI Specimens", fill="#E2E8F0", font=f_tag)
    rb = "Themes: White  ·  Dark  ·  Paper  ·  Dark-Paper   |   NIST 1-2-5  ·  Zero Truncation"
    draw.text((1576 - draw.textbbox((0, 0), rb, font=f_sub)[2], 15), rb, fill="#94A3B8", font=f_sub)
    for (x, y), (label, badge, img) in zip([(24, 52), (806, 52), (24, 487), (806, 487)], panels):
        draw.rounded_rectangle([x - 1, y - 1, x + PANEL_W + 1, y + PANEL_H + 1], radius=8, fill="#1E293B", outline="#334155", width=1)
        canvas.paste(img, (x, y + HDR_H))
        draw.rectangle([x, y, x + PANEL_W, y + HDR_H], fill="#1E293B")
        draw.text((x + 12, y + 6), label, fill="#F8FAFC", font=f_tag)
        draw.text((x + PANEL_W - 12 - draw.textbbox((0, 0), badge, font=f_sub)[2], y + 7), badge, fill="#7DD3FC", font=f_sub)
    return canvas


def main() -> int:
    for p_dir in ("/usr/local/bin", "/usr/bin", "/bin"):
        if p_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{os.environ.get('PATH', '')}:{p_dir}".strip(":")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_SilentHandler, directory=str(REPO_ROOT)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    opts = Options()
    for arg in (
        "--headless=new",
        "--ozone-platform=headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-vulkan",
        "--use-gl=angle",
        "--use-angle=swiftshader-webgl",
    ):
        opts.add_argument(arg)
    driver = None
    try:
        driver = webdriver.Chrome(options=opts)
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        night_js = "const nb=d&&d.querySelector('#v15-backplate-chips [data-backplate=\"lowlight\"]');if(nb)nb.click();"
        panels = [
            ("v01 · Clinical ICU Waveform & Vital Scope", "DOMAIN 01 · WHITE", _capture_showcase(driver, base, "01-clinical-icu-and-trials", "v01-icu-bedside-terminal", "white", fit_sel="#v01-hemo")),
            ("v15 · Collimated Night Flight HUD Optics", "DOMAIN 05 · DARK", _capture_showcase(driver, base, "05-physical-systems-auto-and-aero", "v15-collimated-flight-hud", "dark", night_js)),
            ("v18 · Home Assistant Energy & Climate", "DOMAIN 06 · PAPER", _capture_showcase(driver, base, "06-smart-home-and-energy", "v18-home-assistant-companion-console", "paper")),
            ("Component Library · ECharts Gantt & ATO Enclave", "44 SPECIMENS · DARK-PAPER", _capture_bench(driver, base)),
        ]
        hero = _composite(panels)
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        meta = PngInfo()
        hero.save(OUT_PATH, format="PNG", optimize=True, pnginfo=meta)
        if OUT_PATH.stat().st_size > 280 * 1024:
            hero.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(OUT_PATH, format="PNG", optimize=True, pnginfo=meta)
        assert OUT_PATH.stat().st_size <= 280 * 1024, f"Hero exceeded 280 KB: {OUT_PATH.stat().st_size}"
        print(f"[OK] Hero banner -> {OUT_PATH} ({hero.size}, {OUT_PATH.stat().st_size // 1024} KB)")
        return 0
    finally:
        if driver:
            driver.quit()
        srv.shutdown()
        srv.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
