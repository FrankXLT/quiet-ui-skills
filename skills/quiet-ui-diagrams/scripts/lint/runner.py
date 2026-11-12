# SPDX-License-Identifier: MIT
"""Main orchestration runner for diagram self-checks and lint validation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from pathlib import Path

from .css_rules import check_css_references, reference_error
from .html_parser import (
    check_document_completeness,
    check_svgs,
    parsed_document,
)
from .motion_check import check_motion, check_scripts
from .text_fit import check_text_fit
from .viewbox_check import check_viewbox


def verify(path: Path, offline: bool = False) -> list[str]:
    source = path.read_text(encoding="utf-8")
    parser = parsed_document(source)
    errors: list[str] = []
    errors.extend(parser.unsafe)
    check_document_completeness(source, errors)
    check_css_references(parser, errors)
    for tag, rel, value in parser.references:
        finding = reference_error(tag, rel, value)
        if finding:
            errors.append(finding)
    check_svgs(parser, errors)
    check_viewbox(source, errors)
    check_text_fit(source, errors)
    check_scripts(parser, errors)
    check_motion(parser, source, errors)
    return errors
