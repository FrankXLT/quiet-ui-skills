#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify diagram connector routing and label mask clip geometry.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from geometry.checker import check

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"


def targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        if ASSET_DIR.is_dir():
            return sorted(ASSET_DIR.glob("*.html"))
        return sorted(Path.cwd().glob("*.html"))
    return [Path(p) for p in args.files]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="HTML diagrams to check")
    parser.add_argument("--all", action="store_true", help="check every diagram asset")
    args = parser.parse_args(argv)

    paths = targets(args)
    if not paths:
        parser.error("pass one or more files, or --all")

    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"{path}: file not found")
            continue
        findings.extend(check(path))

    for finding in findings:
        print(finding)
    print(f"Summary: {len(paths)} file(s) checked, {len(findings)} finding(s).")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
