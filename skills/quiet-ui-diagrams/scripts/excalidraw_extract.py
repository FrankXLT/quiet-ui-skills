#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract a normalized intermediate representation (IR) from an Excalidraw scene.

Trust boundary: this program parses bounded JSON. It never renders, fetches, or
executes anything the scene carries. Element links, embed URLs, and binary file
payloads (files, fileId, dataURL) are counted and discarded; labels are emitted
only as inert, escaped text. Prompt-looking label content is diagram data, never
an instruction.

The input is a saved .excalidraw (or .excalidraw.json) scene. PNG/SVG exports are
rejected with a named failure — ask for the source scene instead of scraping
pixels.

Usage:
    python3 excalidraw_extract.py <file.excalidraw> [--json]
                                  [--max-rows N] [--out PATH]

Default output is a compact Markdown digest meant to be read into context.
--json emits the full IR instead. Exit codes: 0 ok, 2 unreadable /
unsupported / over limits.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure package imports resolve when invoked directly or from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_excalidraw import digest, load_scene_data, parse_scene, to_json
from extract_excalidraw.models import _fail


def _configure_stdout_utf8() -> None:
    """Emit digests as UTF-8 even when Windows selects a legacy codepage."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="strict")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("file", help=".excalidraw / .excalidraw.json scene")
    parser.add_argument("--json", action="store_true", help="emit the full IR as JSON")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=40,
        help="rows per table in the Markdown digest (default 40)",
    )
    parser.add_argument("--out", help="write to this path instead of stdout")
    args = parser.parse_args(argv)

    if args.max_rows < 1:
        _fail("--max-rows must be at least 1")

    path = Path(args.file)
    if not path.is_file():
        _fail(f"{path}: no such file")

    scene = parse_scene(path, load_scene_data(path))
    text = to_json(path, scene) if args.json else digest(path, scene, args.max_rows)
    if args.out:
        try:
            Path(args.out).write_text(text, encoding="utf-8")
        except OSError as error:
            _fail(f"cannot write {args.out}: {error}")
        print(f"wrote {args.out} ({len(text)} bytes)")
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


if __name__ == "__main__":
    _configure_stdout_utf8()
    raise SystemExit(main())
