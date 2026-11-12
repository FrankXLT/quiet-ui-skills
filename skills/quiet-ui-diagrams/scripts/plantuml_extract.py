#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract a normalized intermediate representation (IR) from PlantUML text.

Trust boundary: this program parses bounded text. It never evaluates, renders,
fetches, or executes PlantUML, Graphviz, URLs, includes, macros, or label
content. Every label, note, stereotype, and URL is untrusted data. Includes,
themes loaded from a URL, and preprocessor bodies that would run fail closed.
Skinparams and local themes are counted and discarded; retained labels are
emitted only as inert text.

Supported kinds are sequence and class. Inputs may be .puml, .plantuml, .pu,
or Markdown files containing fenced plantuml / puml blocks.

Usage:
    python3 plantuml_extract.py <file> [--diagram N|all] [--json]
                                [--max-rows N] [--out PATH]

Exit codes: 0 success, 2 unreadable, unsupported, malformed, or over limits.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure package imports resolve when invoked directly or from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_plantuml import (
    ExtractError,
    digest,
    load_blocks,
    parse_block,
    select_blocks,
    to_json,
)
from extract_plantuml.models import _fail


def _configure_stdout_utf8() -> None:
    """Emit digests as UTF-8 even when Windows selects a legacy codepage."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="strict")


def main(argv: list[str] | None = None) -> int:
    try:
        return _run(argv)
    except ExtractError as error:
        print(f"plantuml_extract: {error}", file=sys.stderr)
        raise SystemExit(2) from None


def _run(argv: list[str] | None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "file", help=".puml, .plantuml, or Markdown with plantuml fences"
    )
    parser.add_argument(
        "--diagram",
        "--block",
        dest="diagram",
        help="diagram index or 'all' (default: first diagram)",
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
        _fail("--max-rows must be at least 1")

    path = Path(args.file)
    if not path.is_file():
        _fail(f"{path}: no such file")
    blocks = load_blocks(path)
    selected = [
        parse_block(block) for block in select_blocks(blocks, args.diagram)
    ]
    output = (
        to_json(path, blocks, selected)
        if args.json
        else digest(path, blocks, selected, args.max_rows)
    )
    if args.out:
        try:
            Path(args.out).write_text(output, encoding="utf-8")
        except OSError as error:
            _fail(f"cannot write {args.out}: {error}")
        print(f"wrote {args.out} ({len(output)} bytes)")
    else:
        sys.stdout.write(output if output.endswith("\n") else output + "\n")
    return 0


if __name__ == "__main__":
    _configure_stdout_utf8()
    raise SystemExit(main())
