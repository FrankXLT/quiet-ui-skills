#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Self-check diagram HTML for accessible SVG, containment, and offline Quiet UI rules.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lint.runner import verify


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Diagram HTML files to check")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="verify no external network stylesheet or script references",
    )
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        try:
            errors = verify(path, offline=args.offline)
        except (OSError, UnicodeError) as exc:
            errors = [str(exc)]
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
