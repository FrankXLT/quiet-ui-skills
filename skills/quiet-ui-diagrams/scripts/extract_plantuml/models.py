# SPDX-License-Identifier: MIT
"""Data structures, IR graph models, and label sanitizers for PlantUML diagrams.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Any, NoReturn

from .constants import MAX_EDGES, MAX_NODES


class ExtractError(Exception):
    """An input the extractor refuses. main() reports it and exits 2."""


def _fail(message: str) -> NoReturn:
    raise ExtractError(message)


@dataclass
class Node:
    id: str
    label: str = ""
    shape: str = "rect"
    parent: str | None = None
    depth: int = 0
    container: bool = False
    children: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    stereotype: str = ""
    in_degree: int = 0
    out_degree: int = 0


@dataclass
class Edge:
    id: str
    source: str
    target: str
    label: str = ""
    style: str = "solid"
    arrowhead: str = "arrow"
    bidirectional: bool = False
    undirected: bool = False
    cardinality: str = ""
    source_cardinality: str = ""
    target_cardinality: str = ""
    navigable: str = ""
    order: int = 0


@dataclass
class Diagram:
    index: int
    kind: str
    source_line: int
    direction: str = "TD"
    title: str = ""
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    fragments: list[dict[str, Any]] = field(default_factory=list)
    activations: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    note_details: list[dict[str, Any]] = field(default_factory=list)
    discarded: dict[str, int] = field(
        default_factory=lambda: {"skin": 0, "includes": 0}
    )
    _nodes_by_id: dict[str, Node] = field(default_factory=dict, init=False, repr=False)
    detected_roles: dict[int, str] = field(default_factory=dict, init=False, repr=False)
    parsed_roles: dict[int, str] = field(default_factory=dict, init=False, repr=False)
    _aliases: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _bare_names: dict[str, list[str]] = field(default_factory=dict, init=False, repr=False)

    @property
    def node_map(self) -> dict[str, Node]:
        return self._nodes_by_id

    def resolve(self, token: str, scope: list[str] | None = None) -> str:
        key = token.strip()
        for package in reversed(scope or []):
            qualified = f"{package}.{key}"
            if qualified in self._nodes_by_id:
                return qualified
        if key in self._nodes_by_id:
            return key
        if key in self._aliases:
            return self._aliases[key]
        matches = self._bare_names.get(key, [])
        if len(matches) > 1:
            _fail(
                f"ambiguous class name `{key}` (declared in several packages: "
                f"{', '.join(matches)}); qualify it"
            )
        if matches:
            return matches[0]
        return key

    def alias(self, alias: str, node_id: str) -> None:
        self._aliases.setdefault(alias, node_id)

    def bare_name(self, name: str, node_id: str) -> None:
        ids = self._bare_names.setdefault(name, [])
        if node_id not in ids:
            ids.append(node_id)

    def add_node(
        self,
        node_id: str,
        label: str = "",
        shape: str = "rect",
        parent: str | None = None,
        container: bool = False,
        stereotype: str = "",
    ) -> Node:
        existing = self._nodes_by_id.get(node_id)
        if existing is not None:
            if label and (label != node_id or existing.label == existing.id):
                existing.label = label
            if shape != "rect" or not existing.shape:
                existing.shape = shape
            if parent is not None and existing.parent is None:
                existing.parent = parent
                existing.depth = self._depth_for(parent)
                self._attach(parent, node_id)
            existing.container = existing.container or container
            if stereotype and not existing.stereotype:
                existing.stereotype = stereotype
            return existing
        if len(self.nodes) >= MAX_NODES:
            _fail(f"node limit exceeded (max {MAX_NODES})")
        node = Node(
            id=node_id,
            label=label or node_id,
            shape=shape,
            parent=parent,
            depth=self._depth_for(parent),
            container=container,
            stereotype=stereotype,
        )
        self.nodes.append(node)
        self._nodes_by_id[node_id] = node
        self.alias(node_id, node_id)
        if parent is not None:
            self._attach(parent, node_id)
        return node

    def _depth_for(self, parent: str | None) -> int:
        if parent is None:
            return 0
        parent_node = self._nodes_by_id.get(parent)
        return (parent_node.depth + 1) if parent_node is not None else 1

    def _attach(self, parent: str, child: str) -> None:
        parent_node = self._nodes_by_id.get(parent)
        if parent_node is not None and child not in parent_node.children:
            parent_node.children.append(child)
            parent_node.container = True

    def add_edge(
        self,
        source: str,
        target: str,
        label: str = "",
        style: str = "solid",
        arrowhead: str = "arrow",
        bidirectional: bool = False,
        undirected: bool = False,
        source_cardinality: str = "",
        target_cardinality: str = "",
        navigable: str = "",
    ) -> Edge:
        if len(self.edges) >= MAX_EDGES:
            _fail(f"edge limit exceeded (max {MAX_EDGES})")
        edge = Edge(
            id=f"e{len(self.edges) + 1}",
            source=source,
            target=target,
            label=label,
            style=style,
            arrowhead=arrowhead,
            bidirectional=bidirectional,
            undirected=undirected,
            cardinality=(
                f"{source_cardinality or '-'} .. {target_cardinality or '-'}"
                if source_cardinality or target_cardinality
                else ""
            ),
            source_cardinality=source_cardinality,
            target_cardinality=target_cardinality,
            navigable=navigable,
            order=len(self.edges) + 1,
        )
        self.edges.append(edge)
        return edge

    def add_activation(
        self, participant: str, action: str, after_message: int | None = None
    ) -> None:
        self.activations.append(
            {
                "participant": participant,
                "action": action,
                "order": len(self.activations) + 1,
                "after_message": (
                    len(self.edges) if after_message is None else after_message
                ),
            }
        )


@dataclass
class SourceBlock:
    index: int
    text: str
    source_line: int
    start_kind: str = "uml"
    error: str | None = None


_MARKUP_TAGS = (
    "abbr|applet|audio|back|base|big|blockquote|body|br|button|canvas|center|"
    "code|color|del|div|em|embed|font|form|frame|frameset|h[1-6]|head|hr|html|"
    "iframe|img|input|ins|kbd|label|li|link|mark|math|meta|noscript|object|ol|"
    "option|plain|pre|script|select|size|small|source|span|strike|strong|style|"
    "sub|sup|svg|table|td|template|textarea|th|title|tr|tt|ul|video|wbr|xmp"
)
_ACTIVE_TAGS = (
    "applet|audio|base|button|canvas|embed|form|frame|frameset|iframe|img|input|"
    "link|math|meta|noscript|object|option|script|select|source|style|svg|"
    "template|textarea|video|xmp"
)
MARKUP_TAG_RE = re.compile(
    r"</?(?i:" + _ACTIVE_TAGS + r")(?=[\s/>:=])[^<>]*>"
    r"|(?<!<)</?(?:(?i:" + _MARKUP_TAGS + r")|[abipqsuw])(?=[\s/>:=])[^<>]*>(?!>)"
    r"|<[$&][^<>]*>"
)


def clean_label(value: str) -> str:
    """Flatten PlantUML / Creole / HTML label markup without interpreting it."""
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1]
    text = text.replace("\\n", "\n")
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    previous = None
    while previous != text:
        previous = text
        text = MARKUP_TAG_RE.sub("", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"//(.*?)//", r"\1", text)
    text = re.sub(r'""(.*?)""', r"\1", text)
    text = re.sub(r"--([^-]+)--+", r"\1", text)
    text = text.replace('\\"', '"').replace("\\'", "'")
    return "\n".join(part.strip() for part in text.splitlines()).strip()
