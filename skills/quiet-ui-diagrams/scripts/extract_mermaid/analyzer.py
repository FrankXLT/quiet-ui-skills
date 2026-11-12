# SPDX-License-Identifier: MIT
"""Block parser, graph topology, degree calculations, and cycle analysis for Mermaid.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from typing import Any

from .flow_parser import _parse_flowchart
from .loader import _kind_and_direction, _prepared_lines
from .models import Diagram, Edge, Node, SourceBlock
from .sequence_parser import _parse_sequence
from .state_er_parser import _parse_er, _parse_state


def parse_block(block: SourceBlock) -> Diagram:
    lines, config_directives = _prepared_lines(block)
    kind, direction, header_position = _kind_and_direction(lines)
    if kind == "flowchart":
        line_number, header = lines[header_position]
        rest = re.match(
            r"^\s*(?:flowchart|graph)\s+(?:TD|TB|LR|RL|BT)\b", header, re.I
        )
        tail = header[rest.end() :].lstrip() if rest else ""
        if tail.startswith(";"):
            lines[header_position] = (line_number, header[: rest.end()])
            lines.insert(header_position + 1, (line_number, tail[1:]))
    diagram = Diagram(block.index, kind, block.source_line, direction=direction)
    diagram.discarded["config_directives"] = config_directives
    if kind == "flowchart":
        _parse_flowchart(diagram, lines, header_position)
    elif kind == "sequenceDiagram":
        _parse_sequence(diagram, lines, header_position)
    elif kind == "stateDiagram-v2":
        _parse_state(diagram, lines, header_position)
    else:
        _parse_er(diagram, lines, header_position)
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


def shape_family(shape: str) -> str:
    return "container" if shape == "container" else shape


def analyze(diagram: Diagram) -> dict[str, Any]:
    containers = [
        node for node in diagram.nodes if node.container or node.children
    ]
    leaves = [
        node for node in diagram.nodes if not (node.container or node.children)
    ]
    shapes: dict[str, int] = {}
    for node in diagram.nodes:
        family = shape_family(node.shape)
        shapes[family] = shapes.get(family, 0) + 1

    def name(node: Node) -> str:
        return node.label.replace("\n", " · ") or node.id

    hubs = [
        {
            "id": node.id,
            "label": name(node),
            "degree": node.in_degree + node.out_degree,
        }
        for node in sorted(
            leaves,
            key=lambda item: (item.in_degree + item.out_degree, item.id),
            reverse=True,
        )[:5]
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
    candidates = {
        "flowchart": [
            "flowchart" if shapes.get("rhombus") else "architecture",
            "architecture",
        ],
        "sequenceDiagram": ["sequence"],
        "stateDiagram-v2": ["state machine"],
        "erDiagram": ["ER / data model"],
    }[diagram.kind]
    candidates = list(dict.fromkeys(candidates))
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
