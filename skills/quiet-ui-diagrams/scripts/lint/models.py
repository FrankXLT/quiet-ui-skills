# SPDX-License-Identifier: MIT
"""Token models, regex patterns, and tag specifications for diagram linting.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re

MODES = {"none", "reveal", "step", "loop"}
ACTIONS = {"play", "pause", "replay", "prev", "next"}

ASCII_DECIMAL_RE = re.compile(r"^[0-9]+$")
CSS_ESCAPE_RE = re.compile(r"\\(?:([0-9a-fA-F]{1,6})[ \t\r\n\f]?|(.))", re.DOTALL)
CSS_IMPORT_RE = re.compile(r"@import\b", re.IGNORECASE)
CSS_URL_RE = re.compile(r"url\(\s*([^)]+?)\s*\)", re.IGNORECASE)
CSS_IMAGE_SET_RE = re.compile(r"(?:-webkit-)?image-set\s*\(", re.IGNORECASE)
CSS_REMOTE_RE = re.compile(r"(?:https?:)?//", re.IGNORECASE)

CSS_REFERENCE_ATTRS = {
    "style",
    "fill",
    "stroke",
    "filter",
    "clip-path",
    "mask",
    "marker",
    "marker-start",
    "marker-mid",
    "marker-end",
    "cursor",
}
REFERENCE_ATTRS = {
    "src",
    "href",
    "xlink:href",
    "poster",
    "srcset",
    "action",
    "formaction",
}

VIEWBOX_TOLERANCE = 2.0
SANS_ADVANCE = 0.60
MONO_ADVANCE = 0.62
WIDE_ADVANCE = 1.0

TEXT_FIT_PROPERTIES = ("font-size", "font-family", "text-anchor", "letter-spacing")
TEXT_FIT_IGNORED = {"font-weight", "font-style"}
PAINT_PROPERTIES = frozenset(
    {"fill", "stroke", "stroke-width", "fill-opacity", "stroke-opacity", "opacity"}
)
TEXT_LAYOUT_PROPERTIES = (
    "direction",
    "unicode-bidi",
    "writing-mode",
    "white-space",
    "xml:space",
)
TEXT_FIT_TOLERANCE_EM = 0.3

SVG_NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
SVG_NUMBER_RE = re.compile(SVG_NUMBER)
SVG_PLAIN_NUMBER_RE = re.compile(rf"^\s*{SVG_NUMBER}\s*$")
TRANSLATE_RE = re.compile(
    rf"^\s*translate\(\s*({SVG_NUMBER})(?:[\s,]+({SVG_NUMBER}))?\s*\)\s*$"
)
REPLACEMENT_CHAR = "\ufffd"

PAIRED_CONTAINER_TAGS = (
    "title",
    "desc",
    "div",
    "section",
    "main",
    "article",
    "header",
    "footer",
    "figure",
    "figcaption",
    "svg",
    "g",
    "defs",
    "pattern",
    "marker",
    "style",
    "script",
    "span",
    "text",
    "tspan",
)

UNPAINTED_TAGS = {
    "defs",
    "symbol",
    "marker",
    "pattern",
    "clippath",
    "mask",
    "foreignobject",
    "svg",
}

UNSTATIC_CSS_PROPERTIES = {
    "transform",
    "translate",
    "rotate",
    "scale",
    "display",
    "visibility",
    "x",
    "y",
    "cx",
    "cy",
    "r",
    "rx",
    "ry",
    "width",
    "height",
}
UNSTATIC_CSS_PREFIXES = ("animation", "offset", "clip", "mask")

CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_KEYFRAMES_RE = re.compile(
    r"@(?:-[a-z]+-)?keyframes[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", re.IGNORECASE
)
CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
CSS_STRING_RE = re.compile(r"\"[^\"]*\"|'[^']*'")
CSS_PARENS_RE = re.compile(r"\([^()]*\)")
CSS_COMBINATOR_RE = re.compile(r"\s*[>+~]\s*|\s+")
CSS_TAG_RE = re.compile(r"^[a-zA-Z][\w-]*")
CSS_CLASS_RE = re.compile(r"\.([\w-]+)")
CSS_ID_RE = re.compile(r"#([\w-]+)")
CSS_ATTRIBUTE_RE = re.compile(r"\[\s*([\w:-]+)")

GEOMETRY_ATTRS = {
    "rect": ("x", "y", "width", "height"),
    "line": ("x1", "y1", "x2", "y2"),
    "circle": ("cx", "cy", "r"),
    "ellipse": ("cx", "cy", "rx", "ry"),
    "polygon": ("points",),
    "polyline": ("points",),
    "text": ("x", "y"),
}
