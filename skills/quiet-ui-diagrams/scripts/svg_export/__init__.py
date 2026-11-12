# SPDX-License-Identifier: MIT
"""Standalone SVG export package for Quiet UI diagrams.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from .exporter import export_svg_document
from .registry import export_registry
from .var_resolver import QUIET_UI_THEMES, resolve_svg_variables

__all__ = [
    "QUIET_UI_THEMES",
    "export_registry",
    "export_svg_document",
    "resolve_svg_variables",
]
