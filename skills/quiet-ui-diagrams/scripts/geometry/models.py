# SPDX-License-Identifier: MIT
"""Data structures, types, and geometric thresholds for diagram validation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re

NODE_MIN_W = 60.0
NODE_MIN_H = 40.0
MASK_MIN_W = 20.0
MASK_MAX_W = 200.0
MASK_MIN_H = 8.0
MASK_MAX_H = 14.0
EPSILON = 0.5

AXIS_TOLERANCE = 0.5
BORDER_TOLERANCE = 1.0
BORDER_MIN_RUN = 4.0
PORT_TOLERANCE = 4.0
CORNER_CLEARANCE = 8.0
SHARED_PORT_MIN = 12.0
SMALL_PORT_MIN = 8.0
SMALL_EDGE = 48.0

STACK_TOLERANCE = 1.0
SAMPLE_STEP = 1.0
CHORD_LENGTH = 2.0

DEFINITION_TAGS = {"defs", "symbol", "marker", "pattern", "clippath", "mask"}
PATH_ARITY = {
    "M": 2,
    "L": 2,
    "H": 1,
    "V": 1,
    "Q": 4,
    "T": 2,
    "C": 6,
    "S": 4,
    "A": 7,
    "Z": 0,
}

TAG_RE = re.compile(
    r"<!--[\s\S]*?-->|<(?P<close>/?)(?P<tag>g|svg|defs|symbol|marker|pattern|clipPath|mask|rect|path|line)\b"
    r"(?P<attrs>(?:\"[^\"]*\"|'[^']*'|[^'\">])*?)(?P<empty>/?)>",
    re.IGNORECASE,
)
ATTR_RE = re.compile(r'''([^\s"'>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|[^\s>]*))?''')
TRANSLATE_RE = re.compile(
    r"^\s*translate\(\s*([-+]?[\d.]+)(?:[\s,]+([-+]?[\d.]+))?\s*\)\s*$"
)
PATH_COMMAND_RE = re.compile(r"[\s,]*([MmLlHhVvQqCcSsTtAaZz])")
PATH_NUMBER_RE = re.compile(r"[\s,]*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
PATH_FLAG_RE = re.compile(r"[\s,]*([01])")
PATH_END_RE = re.compile(r"[\s,]*$")

Segment = tuple[str, float, float, float, float]
Offset = tuple[float, float]


class Rect:
    __slots__ = ("x", "y", "w", "h", "line", "offset")

    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        line: int,
        offset: int,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.line = line
        self.offset = offset

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def __repr__(self) -> str:
        return f"({self.x:g},{self.y:g} {self.w:g}x{self.h:g})"
