# SPDX-License-Identifier: MIT
"""Structural analysis and geometry bounding for Excalidraw scenes.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import math
from typing import Any

from .models import Edge, Node, Scene, _fail


def _has_cycle(nodes: list[Node], edges: list[Edge]) -> bool:
    adjacency: dict[str, list[str]] = {node.id: [] for node in nodes}
    for edge in edges:
        if edge.source and edge.target and edge.source in adjacency:
            adjacency[edge.source].append(edge.target)
            if edge.bidirectional and edge.target in adjacency:
                adjacency[edge.target].append(edge.source)
    WHITE, GREY, BLACK = 0, 1, 2
    color = {node.id: WHITE for node in nodes}

    def visit(start: str) -> bool:
        stack = [(start, iter(adjacency.get(start, [])))]
        color[start] = GREY
        while stack:
            node_id, targets = stack[-1]
            advanced = False
            for target in targets:
                state = color.get(target, BLACK)
                if state == GREY:
                    return True
                if state == WHITE:
                    color[target] = GREY
                    stack.append((target, iter(adjacency.get(target, []))))
                    advanced = True
                    break
            if not advanced:
                color[node_id] = BLACK
                stack.pop()
        return False

    return any(color[node.id] == WHITE and visit(node.id) for node in nodes)


def scene_bounds(scene: Scene) -> tuple[float, float, float, float]:
    boxes = [(n.x, n.y, n.x + n.w, n.y + n.h) for n in scene.nodes if n.w and n.h]
    if any(not math.isfinite(value) for box in boxes for value in box):
        _fail("invalid geometry: bounding box overflow")
    if not boxes:
        return (0.0, 0.0, 0.0, 0.0)
    bounds = (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )
    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
    ratio = width / height if height > 0 else 0
    if not all(math.isfinite(value) for value in (width, height, ratio)):
        _fail("invalid geometry: canvas arithmetic overflow")
    return bounds


def analyze(scene: Scene) -> dict[str, Any]:
    nodes = scene.nodes
    edges = scene.edges
    drawable = [
        node for node in nodes if node.shape != "text" and (node.label or node.children)
    ]
    containers = [node for node in nodes if node.children]
    leaves = [node for node in nodes if not node.children]
    shapes: dict[str, int] = {}
    for node in nodes:
        shapes[node.shape] = shapes.get(node.shape, 0) + 1

    def name_of(node: Node) -> str:
        return node.label.replace("\n", " · ") or node.id

    ranked = sorted(leaves, key=lambda n: n.in_degree + n.out_degree, reverse=True)
    hubs = [
        {"id": node.id, "label": name_of(node), "degree": node.in_degree + node.out_degree}
        for node in ranked[:5]
        if node.in_degree + node.out_degree > 0
    ]
    sources = [name_of(n) for n in leaves if n.out_degree and not n.in_degree]
    sinks = [name_of(n) for n in leaves if n.in_degree and not n.out_degree]
    orphans = [
        name_of(n)
        for n in leaves
        if not n.in_degree and not n.out_degree and n.shape != "frame"
    ]

    candidates: list[str] = []
    if shapes.get("rhombus"):
        candidates.append("flowchart")
    if shapes.get("ellipse", 0) >= max(2, len(leaves) // 3) and edges:
        candidates.append("state")
    if containers:
        candidates.append("nested")
    if edges and not _has_cycle(nodes, edges) and len(sources) == 1:
        candidates.append("tree")
    candidates.append("architecture")
    seen: set[str] = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]

    collapsible = [
        {
            "id": container.id,
            "label": name_of(container),
            "children": len(container.children),
            "child_labels": [
                name_of(scene.node_map[child])
                for child in container.children
                if scene.node_map.get(child) and scene.node_map[child].label
            ][:8],
        }
        for container in containers
        if container.children
        and all(not scene.node_map[child].children for child in container.children)
    ]
    group_members: dict[str, list[Node]] = {}
    for node in nodes:
        seen_groups: set[str] = set()
        for group_id in node.groups:
            if not group_id or group_id in seen_groups:
                continue
            seen_groups.add(group_id)
            group_members.setdefault(group_id, []).append(node)
    for group_id, members in group_members.items():
        if len(members) < 2:
            continue
        collapsible.append(
            {
                "id": group_id,
                "label": f"group ({len(members)} members)",
                "children": len(members),
                "child_labels": [name_of(m) for m in members if m.label][:8],
            }
        )
    collapsible.sort(key=lambda c: c["children"], reverse=True)

    return {
        "nodes_total": len(nodes),
        "nodes_drawable": len(drawable),
        "containers": len(containers),
        "leaves": len(leaves),
        "edges_total": len(edges),
        "edges_labeled": sum(1 for e in edges if e.label),
        "edges_dangling": sum(1 for e in edges if not (e.source and e.target)),
        "max_depth": max((n.depth for n in nodes), default=0),
        "shapes": dict(sorted(shapes.items(), key=lambda kv: (-kv[1], kv[0]))),
        "has_cycle": _has_cycle(nodes, edges),
        "hubs": hubs,
        "entry_points": sources[:6],
        "terminals": sinks[:6],
        "orphans": orphans[:6],
        "type_candidates": candidates[:3],
        "collapsible_groups": collapsible[:8],
        "over_node_budget": len(drawable) > 9,
        "over_edge_budget": len(edges) > 12,
    }
