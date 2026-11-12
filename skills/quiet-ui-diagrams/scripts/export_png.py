# SPDX-License-Identifier: MIT
"""Rasterize diagram HTML using headless Chrome via Selenium.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import argparse
import io
import math
from pathlib import Path
import sys
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

sys.path.insert(0, str(Path(__file__).resolve().parent))


def exact_scale(value: str) -> float:
    try:
        scale = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("scale must be a number") from exc
    if not math.isfinite(scale) or not 1.0 <= scale <= 4.0:
        raise argparse.ArgumentTypeError("scale must be between 1.0 and 4.0")
    return scale


def rasterize(
    src: Path,
    out: Path,
    scale: float = 2.0,
    selector: str = "svg",
    padding: int = 0,
    background: str | None = None,
    size: tuple[int, int] | None = None,
) -> Path:
    src_path = src.resolve()
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument(f"--force-device-scale-factor={scale}")
    opts.add_argument("--window-size=2400,2000")

    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(src_path.as_uri() + "?motion=static")
        driver.execute_script("document.documentElement.setAttribute('data-motion', 'static');")
        try:
            driver.execute_async_script(
                "const done = arguments[0]; "
                "Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 4000))])"
                ".then(() => done());"
            )
        except Exception:
            pass

        svg = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script(
            """const el = arguments[0];
            const box = el.viewBox ? el.viewBox.baseVal : null;
            if (box && Number.isFinite(box.width) && box.width > 0) {
                for (const [axis, sz] of [['width', box.width], ['height', box.height]]) {
                    for (const pfx of ['', 'min-', 'max-']) {
                        el.style.setProperty(pfx + axis, sz + 'px', 'important');
                    }
                }
            }
            for (let a = el.parentElement; a; a = a.parentElement) {
                a.style.setProperty('overflow', 'visible', 'important');
            }""",
            svg,
        )

        rect = driver.execute_script("return arguments[0].getBoundingClientRect();", svg)
        req_w = max(2400, int(rect.get("right", 0) + 200))
        req_h = max(2000, int(rect.get("bottom", 0) + 200))
        driver.set_window_size(req_w, req_h)
        time.sleep(0.05)

        png_bytes = svg.screenshot_as_png
    finally:
        driver.quit()

    img = Image.open(io.BytesIO(png_bytes))
    if background and background.lower() != "transparent":
        bg = Image.new("RGBA", img.size, background)
        bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)
        img = bg.convert("RGB")

    if padding > 0:
        scaled_pad = int(round(padding * scale))
        if background and background.lower() != "transparent":
            pad_fill = background
        elif img.mode == "RGBA":
            pad_fill = (0, 0, 0, 0)
        else:
            pad_fill = img.getpixel((0, 0))
        canvas = Image.new(img.mode, (img.width + 2 * scaled_pad, img.height + 2 * scaled_pad), pad_fill)
        canvas.paste(img, (scaled_pad, scaled_pad))
        img = canvas

    if size is not None:
        img = img.resize(size, Image.Resampling.LANCZOS)

    clean = Image.frombytes(img.mode, img.size, img.tobytes())
    out.parent.mkdir(parents=True, exist_ok=True)
    clean.save(out, format="PNG")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", nargs="?", type=Path, help="diagram HTML input")
    parser.add_argument("out", nargs="?", type=Path, default=None, help="PNG output path")
    parser.add_argument("scale_pos", nargs="?", type=exact_scale, default=None, help="scale (1.0-4.0)")
    parser.add_argument("-i", "--input", dest="input_flag", type=Path, help="Input HTML file")
    parser.add_argument("-o", "--output", dest="output_flag", type=Path, help="Output PNG path")
    parser.add_argument("--scale", type=exact_scale, default=2.0, help="Device scale factor (1.0-4.0)")
    parser.add_argument("--selector", default="svg", help="CSS selector for SVG (default: svg)")
    parser.add_argument("--padding", type=int, default=0, help="Padding in CSS pixels")
    parser.add_argument("--background", default=None, help="Background color override")
    parser.add_argument("--size", default=None, help="Target size WxH (e.g. 1200x800)")

    args = parser.parse_args(argv)
    src = args.input_flag or args.src
    if not src:
        parser.error("input HTML diagram file is required")

    out = args.output_flag or args.out or src.with_suffix(".png")
    scale = args.scale_pos if args.scale_pos is not None else args.scale

    target_size = None
    if args.size:
        parts = args.size.lower().split("x")
        if len(parts) != 2:
            parser.error("--size must be in WxH format (e.g. 1200x800)")
        target_size = (int(parts[0]), int(parts[1]))

    try:
        result = rasterize(
            src=src,
            out=out,
            scale=scale,
            selector=args.selector,
            padding=args.padding,
            background=args.background,
            size=target_size,
        )
        print(result)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
