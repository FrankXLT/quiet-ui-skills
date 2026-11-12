# SPDX-License-Identifier: MIT
"""draw.io diagram extraction package.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from .analyzer import analyze, page_bounds
from .formatter import digest, select_pages, to_json
from .loader import load_mxfile
from .models import Edge, Node, Page, PayloadTooLarge, classify_shape, shape_family
from .parser import parse_file, parse_page
from .style_helpers import clean_label, parse_style

__all__ = [
    "PayloadTooLarge",
    "Node",
    "Edge",
    "Page",
    "classify_shape",
    "shape_family",
    "load_mxfile",
    "parse_style",
    "clean_label",
    "parse_page",
    "parse_file",
    "analyze",
    "page_bounds",
    "digest",
    "to_json",
    "select_pages",
]
