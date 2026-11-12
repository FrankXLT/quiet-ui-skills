#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract a normalized intermediate representation (IR) from a draw.io file.

The deterministic half of the draw.io import flow: this script never makes a
design decision. It decodes whatever draw.io wrote (raw XML, deflate+base64
payloads, PNG/SVG files with an embedded mxfile), flattens the mxGraphModel
into absolute-positioned nodes and edges, and reports structural signals — hubs,
containers, depth, cycles, leaf clusters — that the skill uses to pick a diagram
type and a level of detail.

Usage:
    python3 drawio_extract.py <file.drawio> [--page N|NAME] [--json]
                             [--max-rows N] [--out PATH]

Default output is a compact Markdown digest for local review.
--json emits the full IR instead (every node, every edge, every style).

Exit codes: 0 ok, 2 unreadable / unsupported input.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure package imports resolve when invoked directly or from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_drawio import digest, parse_file, select_pages, to_json
from extract_drawio.models import _fail


def _configure_stdout_utf8() -> None:
    """Emit digests as UTF-8 even when Windows selects a legacy codepage."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="strict")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("file", help=".drawio / .xml / .drawio.png / .drawio.svg")
    parser.add_argument(
        "--page",
        help="page index, page name, or 'all' (default: first page)",
    )
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
        parser.error("--max-rows must be at least 1")

    path = Path(args.file)
    if not path.is_file():
        _fail(f"{path}: no such file")

    pages = parse_file(path)
    selected = select_pages(pages, args.page)
    text = (
        to_json(path, pages, selected)
        if args.json
        else digest(path, pages, selected, args.max_rows)
    )
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
