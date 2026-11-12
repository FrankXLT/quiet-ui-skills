#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Export a diagram HTML file to a standalone, inline-safe SVG 1.1 file.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from svg_export.exporter import export_svg_document
from svg_export.registry import export_registry
from svg_export.var_resolver import QUIET_UI_THEMES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export a diagram HTML file to a standalone SVG 1.1 file."
    )
    parser.add_argument("source", type=Path, help="Source .html diagram file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output .svg path (default: <source-stem>.svg next to source)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_flag",
        type=Path,
        default=None,
        help="Output .svg path (optional flag form)",
    )
    parser.add_argument(
        "--theme",
        choices=sorted(QUIET_UI_THEMES.keys()),
        default="white",
        help="Quiet UI theme token map to resolve (default: white)",
    )
    parser.add_argument(
        "--system-fonts",
        action="store_true",
        default=True,
        help="omit remote font imports for offline rendering (default: True)",
    )
    parser.add_argument(
        "--registry",
        action="store_true",
        help="export machine-readable .registry.json sidecar of data-block-* metadata",
    )
    args = parser.parse_args(argv)
    out_arg: Path | None = args.output_flag or args.output

    source: Path = args.source
    if not source.is_file():
        print(f"error: source not found: {source}", file=sys.stderr)
        return 2
    if source.name == "index.html" and source.parent.name == "assets":
        print(
            "error: refuse to export the gallery (assets/index.html); pick a specific diagram file",
            file=sys.stderr,
        )
        return 2

    if args.registry:
        try:
            reg_out = export_registry(source, out_arg)
            print(reg_out)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if out_arg is not None and out_arg.suffix == ".json":
            return 0

    try:
        html = source.read_text(encoding="utf-8")
        document = export_svg_document(
            html=html,
            source_path=source,
            theme=args.theme,
            system_fonts=args.system_fonts,
        )
    except RecursionError:
        print("error: diagram CSS nesting exceeds supported export depth", file=sys.stderr)
        return 2
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output = out_arg if (out_arg and out_arg.suffix != ".json") else source.with_suffix(".svg")
    try:
        output.write_text(document, encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot write {output}: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
