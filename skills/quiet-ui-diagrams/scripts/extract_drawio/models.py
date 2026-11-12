# SPDX-License-Identifier: MIT
"""Data models and shape classification for draw.io extraction.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NoReturn
import sys


class PayloadTooLarge(ValueError):
    """Raised when compressed metadata expands beyond the supported limit."""


def _fail(msg: str) -> NoReturn:
    print(f"drawio_extract: {msg}", file=sys.stderr)
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
    font_color: str = ""
    dashed: bool = False
    rounded: bool = False
    container: bool = False
    children: list[str] = field(default_factory=list)
    link: str = ""
    attrs: dict[str, str] = field(default_factory=dict)
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
    style_name: str = ""
    waypoints: int = 0
    stroke: str = ""


@dataclass
class Page:
    id: str
    name: str
    index: int
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    @property
    def node_map(self) -> dict[str, Node]:
        return {n.id: n for n in self.nodes}


SHAPE_FAMILIES = (
    ("mxgraph.aws", "aws"),
    ("mxgraph.azure", "azure"),
    ("mxgraph.gcp", "gcp"),
    ("mxgraph.kubernetes", "kubernetes"),
    ("mxgraph.cisco", "network"),
    ("mxgraph.veeam", "infra"),
    ("mxgraph.flowchart", "flowchart"),
    ("mxgraph.bpmn", "bpmn"),
    ("mxgraph.er", "er"),
    ("mxgraph.sysml", "uml"),
    ("mxgraph.archimate", "archimate"),
)

SHAPE_KEYS = (
    ("swimlane", "swimlane"),
    ("ellipse", "ellipse"),
    ("rhombus", "rhombus"),
    ("triangle", "triangle"),
    ("cylinder", "cylinder"),
    ("cylinder3", "cylinder"),
    ("hexagon", "hexagon"),
    ("cloud", "cloud"),
    ("actor", "actor"),
    ("umlActor", "actor"),
    ("note", "note"),
    ("card", "card"),
    ("step", "step"),
    ("process", "process"),
    ("parallelogram", "parallelogram"),
    ("document", "document"),
    ("datastore", "cylinder"),
    ("umlLifeline", "lifeline"),
    ("umlFrame", "frame"),
    ("table", "table"),
    ("tableRow", "table-row"),
    ("partialRectangle", "table-row"),
    ("image", "image"),
    ("text", "text"),
    ("group", "group"),
)


def classify_shape(style: dict[str, str]) -> str:
    raw = style.get("shape", "")
    if raw:
        for key, name in SHAPE_KEYS:
            if raw == key:
                return name
        for key, name in SHAPE_KEYS:
            if raw.startswith(key):
                return name
        for prefix, family in SHAPE_FAMILIES:
            if raw.startswith(prefix):
                return f"icon:{family}"
        return f"shape:{raw}"
    for key, name in SHAPE_KEYS:
        if key in style:
            return name
    if style.get("ellipse") == "1":
        return "ellipse"
    return "rect"


def shape_family(shape: str) -> str:
    if shape.startswith("icon:"):
        return shape.split(":", 1)[1]
    if shape.startswith("shape:"):
        return "custom"
    return shape
