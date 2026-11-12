# SPDX-License-Identifier: MIT
"""Geometry validation package for diagrams.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from .checker import check, contained, overlap, parse_rects
from .connectors import check_connectors, connectors, stroked_nodes
from .models import Rect, Segment
from .path_math import arc, bezier, path_segments

__all__ = [
    "Rect",
    "Segment",
    "arc",
    "bezier",
    "check",
    "check_connectors",
    "connectors",
    "contained",
    "overlap",
    "parse_rects",
    "path_segments",
    "stroked_nodes",
]
