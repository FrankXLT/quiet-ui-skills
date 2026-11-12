# SPDX-License-Identifier: MIT
"""Block parser, graph topology, degree calculations, and cycle analysis for PlantUML.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

from typing import Any

from .class_parser import _parse_class
from .constants import UNSUPPORTED_STARTS
from .kind_detector import _detect_kind, _unsupported_kind_message
from .loader import _blank_comments, _refuse_includes
from .models import Diagram, Edge, Node, SourceBlock, _fail
from .sequence_parser import _parse_sequence


def parse_block(block: SourceBlock) -> Diagram:
    if block.error:
        _fail(block.error)
    if block.start_kind != "uml":
        token = block.start_kind
        if token in UNSUPPORTED_STARTS or token != "uml":
            _fail(
                _unsupported_kind_message(
                    token if token != "uml" else block.start_kind
                )
            )
    lines_raw = _blank_comments(block.text.splitlines())
    lines = [
        (block.source_line + offset, raw)
        for offset, raw in enumerate(lines_raw)
    ]
    _refuse_includes(lines)
    kind, detected_roles = _detect_kind(lines)
    diagram = Diagram(block.index, kind, block.source_line)
    diagram.detected_roles = detected_roles
    if kind == "sequence":
        _parse_sequence(diagram, lines)
    else:
        _parse_class(diagram, lines)
    _finalize_degrees(diagram)
    return diagram


def _finalize_degrees(diagram: Diagram) -> None:
    nodes = diagram.node_map
    for edge in diagram.edges:
        if edge.source in nodes:
            nodes[edge.source].out_degree += 1
        if edge.target in nodes:
            nodes[edge.target].in_degree += 1
        if edge.bidirectional:
            if edge.source in nodes:
                nodes[edge.source].in_degree += 1
            if edge.target in nodes:
                nodes[edge.target].out_degree += 1


def _has_cycle(nodes: list[Node], edges: list[Edge]) -> bool:
    adjacency: dict[str, list[str]] = {node.id: [] for node in nodes}
    for edge in edges:
        if edge.source in adjacency and edge.target in adjacency:
            adjacency[edge.source].append(edge.target)
            if edge.bidirectional:
                adjacency[edge.target].append(edge.source)
    WHITE, GREY, BLACK = 0, 1, 2
    colors = {node.id: WHITE for node in nodes}

    def visit(start: str) -> bool:
        stack: list[tuple[str, Any]] = [(start, iter(adjacency[start]))]
        colors[start] = GREY
        while stack:
            node_id, targets = stack[-1]
            for target in targets:
                if colors.get(target, BLACK) == GREY:
                    return True
                if colors.get(target, BLACK) == WHITE:
                    colors[target] = GREY
                    stack.append((target, iter(adjacency.get(target, []))))
                    break
            else:
                colors[node_id] = BLACK
                stack.pop()
        return False

    return any(colors[node.id] == WHITE and visit(node.id) for node in nodes)


def node_ref(node: Node) -> str:
    """The canonical display name of a node in prose and digests."""
    label = (node.label.split("\n")[0] if node.label else "").strip()
    if not label or label == node.id:
        return node.id
    if "." in node.id and label in node.id:
        return f"{node.id} ({label})"
    return f"{label} ({node.id})"


def analyze(diagram: Diagram) -> dict[str, Any]:
    containers = [
        node for node in diagram.nodes if node.container or node.children
    ]
    leaves = [
        node for node in diagram.nodes if not (node.container or node.children)
    ]
    shapes: dict[str, int] = {}
    for node in diagram.nodes:
        family = "container" if node.shape == "container" else node.shape
        shapes[family] = shapes.get(family, 0) + 1

    def name(node: Node) -> str:
        return node_ref(node)

    ranked = sorted(
        leaves,
        key=lambda item: (item.in_degree + item.out_degree, item.id),
        reverse=True,
    )
    hubs = [
        {
            "id": node.id,
            "label": node.label.replace("\n", " · ") or node.id,
            "ref": name(node),
            "degree": node.in_degree + node.out_degree,
        }
        for node in ranked[:5]
        if node.in_degree + node.out_degree > 0
    ]
    entry_points = [
        name(node) for node in leaves if node.out_degree and not node.in_degree
    ]
    terminals = [
        name(node) for node in leaves if node.in_degree and not node.out_degree
    ]
    orphans = [
        name(node)
        for node in leaves
        if not node.in_degree and not node.out_degree
    ]
    candidates = (
        ["sequence"] if diagram.kind == "sequence" else ["UML class"]
    )
    collapsible = [
        {
            "id": node.id,
            "label": name(node),
            "children": len(node.children),
            "child_labels": [
                name(diagram.node_map[child])
                for child in node.children
                if child in diagram.node_map
            ][:8],
        }
        for node in containers
        if node.children
    ]
    collapsible.sort(key=lambda item: item["children"], reverse=True)
    drawable = len(leaves)
    return {
        "nodes_total": len(diagram.nodes),
        "nodes_drawable": drawable,
        "containers": len(containers),
        "leaves": len(leaves),
        "edges_total": len(diagram.edges),
        "edges_labeled": sum(bool(edge.label) for edge in diagram.edges),
        "edges_dangling": 0,
        "max_depth": max((node.depth for node in diagram.nodes), default=0),
        "shapes": dict(
            sorted(shapes.items(), key=lambda item: (-item[1], item[0]))
        ),
        "has_cycle": _has_cycle(diagram.nodes, diagram.edges),
        "hubs": hubs,
        "entry_points": entry_points[:6],
        "terminals": terminals[:6],
        "orphans": orphans[:6],
        "type_candidates": candidates,
        "collapsible_groups": collapsible[:8],
        "over_node_budget": drawable > 9,
        "over_edge_budget": len(diagram.edges) > 12,
    }
