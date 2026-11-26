#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""CLI entrypoint for building a Quiet UI v9.8.0 static project-site shell."""

from __future__ import annotations

import argparse
import inspect
import shutil
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.site_shell import build_project_site, load_site_config, render_social_svg  # noqa: E402


def _resolve_style_sources(config_dir: Path) -> tuple[Path, Path | None]:
    local_tokens = config_dir / "styles" / "quiet-ui-tokens.css"
    tokens_src = local_tokens if local_tokens.is_file() else REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
    overrides_src: Path | None = None
    for candidate in (config_dir / "styles" / "overrides.css", config_dir / "overrides.css"):
        if candidate.is_file():
            overrides_src = candidate
            break
    return tokens_src, overrides_src


def _copy_if_needed(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)


def _call_site_builder(
    config: dict[str, Any],
    out_dir: Path,
    *,
    bundle: bool,
    tokens_src: Path,
    overrides_src: Path | None,
) -> None:
    kwargs: dict[str, Any] = {"bundle": bundle}
    try:
        params = inspect.signature(build_project_site).parameters
    except (TypeError, ValueError):
        params = {}
    if "tokens_path" in params:
        kwargs["tokens_path"] = tokens_src
    if "overrides_path" in params and overrides_src is not None:
        kwargs["overrides_path"] = overrides_src
    build_project_site(config, out_dir, **kwargs)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a static project-site shell (Overview, Docs, optional Demo) from an oaw-site.json manifest."
    )
    parser.add_argument("--config", required=True, type=Path, help="Path to oaw-site.json manifest")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for generated static site")
    parser.add_argument(
        "--social-svg",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write 1280x640 social preview SVG sibling (default: enabled)",
    )
    parser.add_argument(
        "--social-png",
        action="store_true",
        help="Render 1280x640 social preview PNG (requires Pillow)",
    )
    parser.add_argument(
        "--bundle",
        action="store_true",
        help="Inline token and override CSS directly into generated HTML pages",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = args.config.resolve()
    if not config_path.is_file():
        print(f"[FAIL] Config file not found: {config_path}", file=sys.stderr)
        return 1

    config = load_site_config(config_path)
    config_dir = Path(config["base_dir"])
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    tokens_src, overrides_src = _resolve_style_sources(config_dir)
    if not args.bundle:
        _copy_if_needed(tokens_src, out_dir / "styles" / "quiet-ui-tokens.css")
        if overrides_src is not None:
            _copy_if_needed(overrides_src, out_dir / "styles" / "overrides.css")

    _call_site_builder(
        config,
        out_dir,
        bundle=args.bundle,
        tokens_src=tokens_src,
        overrides_src=overrides_src,
    )

    rel_img = config.get("social_preview", {}).get("image_path") or "assets/social-preview.png"
    png_path = (out_dir / rel_img).resolve()
    if not png_path.is_relative_to(out_dir) or png_path == out_dir:
        raise ValueError(f"social_preview.image_path escapes output directory: {rel_img!r}")
    if args.social_svg:
        svg_path = png_path.with_suffix(".svg")
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_text = render_social_svg(config).rstrip("\n") + "\n"
        svg_path.write_text(svg_text, encoding="utf-8")

    if args.social_png:
        from src.site_shell import render_social_png  # lazy import only when --social-png is requested

        png_out = png_path.with_suffix(".png")
        png_out.parent.mkdir(parents=True, exist_ok=True)
        render_social_png(config, png_out)

    print(f"[OK] Built project site -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
