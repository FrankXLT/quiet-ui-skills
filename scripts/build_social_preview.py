#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build or verify deterministic 1280x640 SVG and PNG social preview assets."""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.site_shell import load_site_config, render_social_png, render_social_svg  # noqa: E402

MAX_PNG_BYTES = 250 * 1024
DEFAULT_TARGETS: tuple[tuple[Path, Path, bool], ...] = (
    (REPO_ROOT / "src" / "chrome" / "quiet-ui-site.json", REPO_ROOT / "docs", True),
    (
        REPO_ROOT / "customizations" / "project-site-starter" / "oaw-site.json",
        REPO_ROOT / "customizations" / "project-site-starter" / "site",
        False,
    ),
)


def _read_png_dimensions(png_path: Path) -> tuple[int, int]:
    header = png_path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Invalid PNG header: {png_path}")
    return struct.unpack(">II", header[16:24])


def _resolve_targets(config: dict, out_dir: Path) -> tuple[Path, Path]:
    sp = config.get("social_preview") if isinstance(config.get("social_preview"), dict) else {}
    raw_rel = str(sp.get("image_path") or "assets/quiet-ui-social.png").strip()
    png_rel = Path(raw_rel)
    if png_rel.is_absolute() or ".." in png_rel.parts:
        raise ValueError(f"social_preview.image_path must be a safe relative path, got {raw_rel!r}")
    png_path = out_dir / png_rel
    svg_path = png_path.with_suffix(".svg")
    return svg_path, png_path


def _check_outputs(
    svg_path: Path, png_path: Path, expected_svg: bytes, expected_size: tuple[int, int], svg_only: bool
) -> int:
    issues: list[str] = []
    if not svg_path.is_file() or svg_path.read_bytes() != expected_svg:
        issues.append(f"SVG drift or missing: {svg_path}")
    if not svg_only:
        if not png_path.is_file():
            issues.append(f"PNG missing: {png_path}")
        else:
            byte_len = png_path.stat().st_size
            try:
                dims = _read_png_dimensions(png_path)
            except ValueError as exc:
                issues.append(str(exc))
            else:
                if dims != expected_size:
                    issues.append(f"PNG dimensions {dims[0]}x{dims[1]} != {expected_size[0]}x{expected_size[1]}")
            if byte_len > MAX_PNG_BYTES:
                issues.append(f"PNG exceeds {MAX_PNG_BYTES} bytes: {byte_len}")
    if issues:
        for issue in issues:
            print(f"[FAIL] {issue}", file=sys.stderr)
        return 1
    print(f"[OK] Social preview assets verified ({svg_path.name}" + ("" if svg_only else f", {png_path.name}") + ")")
    return 0


def _process_target(config_path: Path, out_dir: Path, trailing_nl: bool, args: argparse.Namespace) -> int:
    config = load_site_config(config_path)
    sp = config.get("social_preview", {})
    expected_size = (int(sp.get("width", 1280)), int(sp.get("height", 640)))
    svg_path, png_path = _resolve_targets(config, out_dir)
    raw_svg = render_social_svg(config)
    svg_bytes = (raw_svg.rstrip() + "\n" if trailing_nl else raw_svg).encode("utf-8")

    if args.check:
        return _check_outputs(svg_path, png_path, svg_bytes, expected_size, args.svg_only)

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_bytes(svg_bytes)
    print(f"[OK] Wrote {svg_path} ({len(svg_bytes)} bytes)")
    if not args.svg_only:
        render_social_png(config, png_path, theme=args.theme)
        dims = _read_png_dimensions(png_path)
        print(f"[OK] Wrote {png_path} ({dims[0]}x{dims[1]}, {png_path.stat().st_size} bytes, theme={args.theme})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Render 1280x640 Quiet UI social preview SVG and PNG.")
    parser.add_argument("--config", default=None, help="Site config JSON (default: Quiet UI + starter)")
    parser.add_argument("--out-dir", default=None, help="Output site root directory (default: docs + starter/site)")
    parser.add_argument("--theme", default="white", choices=("white", "dark"), help="PNG card theme (default: white)")
    parser.add_argument("--svg-only", action="store_true", help="Write/check SVG only and skip PNG rendering")
    parser.add_argument("--check", action="store_true", help="Verify existing outputs without modifying files")
    args = parser.parse_args()

    if args.config or args.out_dir:
        cfg_path = Path(args.config) if args.config else DEFAULT_TARGETS[0][0]
        out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_TARGETS[0][1]
        targets: tuple[tuple[Path, Path, bool], ...] = ((cfg_path, out_dir, True),)
    else:
        targets = DEFAULT_TARGETS

    rc = 0
    for cfg_path, out_dir, trailing_nl in targets:
        if _process_target(cfg_path, out_dir, trailing_nl, args) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
