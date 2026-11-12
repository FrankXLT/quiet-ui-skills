# SPDX-License-Identifier: MIT
"""Data models, limits, and label sanitizers for Excalidraw scenes.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass, field
from typing import Any, NoReturn

MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_ELEMENTS = 10000
MAX_NODES = 2000
MAX_EDGES = 5000

EXCALIDRAW_SUFFIXES = (".excalidraw", ".json")
EXPORT_SUFFIXES = (".png", ".svg")

NODE_SHAPES = {
    "rectangle": "rect",
    "ellipse": "ellipse",
    "diamond": "rhombus",
    "image": "image",
    "embeddable": "embed",
    "iframe": "embed",
}
EDGE_TYPES = {"arrow", "line"}
CONTAINER_TYPES = {"frame", "magicframe"}


def _fail(message: str) -> NoReturn:
    print(f"excalidraw_extract: {message}", file=sys.stderr)
    raise SystemExit(2)


@dataclass
class Node:
    id: str
    label: str = ""
    shape: str = "rect"
    parent: str | None = None
    depth: int = 0
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    fill: str = ""
    stroke: str = ""
    dashed: bool = False
    container: bool = False
    children: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    in_degree: int = 0
    out_degree: int = 0


@dataclass
class Edge:
    id: str
    source: str | None
    target: str | None
    label: str = ""
    dashed: bool = False
    bidirectional: bool = False
    undirected: bool = False
    waypoints: int = 0
    stroke: str = ""


@dataclass
class Scene:
    name: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    discarded: dict[str, int] = field(
        default_factory=lambda: {
            "freedraw_strokes": 0,
            "image_payloads": 0,
            "links": 0,
            "embeds": 0,
            "deleted_elements": 0,
            "unknown_elements": 0,
        }
    )

    @property
    def node_map(self) -> dict[str, Node]:
        return {node.id: node for node in self.nodes}


def clean_label(value: Any) -> str:
    """Excalidraw text is plain, but normalize whitespace defensively."""
    if not isinstance(value, str):
        return ""
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(ch for ch in text if ch == "\n" or ch >= " " or ch == "\t")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def text_label(element: dict[str, Any]) -> str:
    """The text as typed, not as wrapped to its box."""
    original = element.get("originalText")
    return clean_label(
        original if isinstance(original, str) and original else element.get("text")
    )


def _num(element: dict[str, Any], key: str) -> float:
    """A geometry field as a finite float; absent or non-numeric reads as 0."""
    value = element.get(key, 0)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    try:
        value = float(value)
    except OverflowError:
        _fail(f"invalid geometry: {key} is out of range")
    if not math.isfinite(value):
        _fail(f"invalid geometry: {key} must be finite")
    return value
