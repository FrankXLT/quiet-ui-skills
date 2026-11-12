# SPDX-License-Identifier: MIT
"""Connector path routing analysis, border riding, and port collision verification.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import math
from pathlib import Path

from .models import (
    AXIS_TOLERANCE,
    BORDER_MIN_RUN,
    BORDER_TOLERANCE,
    CORNER_CLEARANCE,
    NODE_MIN_H,
    NODE_MIN_W,
    PORT_TOLERANCE,
    SAMPLE_STEP,
    SHARED_PORT_MIN,
    SMALL_EDGE,
    SMALL_PORT_MIN,
    STACK_TOLERANCE,
    Rect,
    Segment,
)
from .path_math import (
    attribute,
    bounds,
    distance_to_segment,
    number,
    path_segments,
    shapes,
    shifted,
)


def connectors(source: str) -> list[tuple[int, str, list[Segment] | None]]:
    found: list[tuple[int, str, list[Segment] | None]] = []
    for tag, attrs, start, frame in shapes(source):
        if tag == "rect" or frame is None:
            continue
        if attribute(attrs, "marker-end") is None and attribute(attrs, "marker-start") is None:
            continue
        if "spoke" in (attribute(attrs, "class") or "").split():
            continue
        line = source.count("\n", 0, start) + 1
        if tag == "line":
            coords = [number(attrs, key) for key in ("x1", "y1", "x2", "y2")]
            if None in coords:
                continue
            x1, y1, x2, y2 = coords  # type: ignore[misc]
            segments: list[Segment] | None = [("line", x1, y1, x2, y2)]
            label = f"<line {x1:g},{y1:g} -> {x2:g},{y2:g}>"
        else:
            d = attribute(attrs, "d") or ""
            segments = path_segments(d)
            label = f'<path d="{d if len(d) <= 48 else d[:45] + "..."}">'
        if segments is None:
            found.append((line, label, None))
        elif segments:
            found.append((line, label, shifted(segments, frame)))
    return found


def stroked_nodes(source: str) -> list[Rect]:
    nodes: list[Rect] = []
    for tag, attrs, start, frame in shapes(source):
        if tag != "rect" or frame is None:
            continue
        x, y, w, h = (number(attrs, key) for key in ("x", "y", "width", "height"))
        if None in (x, y, w, h) or w < NODE_MIN_W or h < NODE_MIN_H:  # type: ignore[operator]
            continue
        stroke = (attribute(attrs, "stroke") or "none").strip().lower()
        if stroke in {"none", "transparent"} or number(attrs, "stroke-width") == 0:
            continue
        line = source.count("\n", 0, start) + 1
        nodes.append(Rect(x + frame[0], y + frame[1], w, h, line, start))
    return nodes


def rides_border(segment: Segment, node: Rect) -> str | None:
    _, x1, y1, x2, y2 = segment
    if abs(y1 - y2) <= AXIS_TOLERANCE:
        low, high = sorted((x1, x2))
        shared = min(high, node.right) - max(low, node.x)
        for edge, name in ((node.y, "top"), (node.bottom, "bottom")):
            if abs(y1 - edge) <= BORDER_TOLERANCE and shared > BORDER_MIN_RUN:
                return name
    if abs(x1 - x2) <= AXIS_TOLERANCE:
        low, high = sorted((y1, y2))
        shared = min(high, node.bottom) - max(low, node.y)
        for edge, name in ((node.x, "left"), (node.right, "right")):
            if abs(x1 - edge) <= BORDER_TOLERANCE and shared > BORDER_MIN_RUN:
                return name
    return None


def attached(px: float, py: float, node: Rect) -> bool:
    outside_x = max(node.x - px, 0.0, px - node.right)
    outside_y = max(node.y - py, 0.0, py - node.bottom)
    inside = min(px - node.x, node.right - px, py - node.y, node.bottom - py)
    return max(outside_x, outside_y) <= PORT_TOLERANCE and inside <= PORT_TOLERANCE


def port_edge(px: float, py: float, node: Rect) -> tuple[str, float, float]:
    distances = {
        "top": abs(py - node.y),
        "bottom": abs(py - node.bottom),
        "left": abs(px - node.x),
        "right": abs(px - node.right),
    }
    side = min(distances, key=distances.__getitem__)
    if side in {"top", "bottom"}:
        return side, node.w, px
    return side, node.h, py


def near_corner(px: float, py: float, node: Rect) -> tuple[float, float] | None:
    if not attached(px, py, node):
        return None
    for cx in (node.x, node.right):
        for cy in (node.y, node.bottom):
            if max(abs(px - cx), abs(py - cy)) < CORNER_CLEARANCE:
                return cx, cy
    return None


def shared_run(a: list[Segment], b: list[Segment]) -> float:
    left, top, right, bottom = bounds(b, STACK_TOLERANCE)
    a_left, a_top, a_right, a_bottom = bounds(a, 0.0)
    if a_right < left or a_left > right or a_bottom < top or a_top > bottom:
        return 0.0
    a_start, a_end = (a[0][1], a[0][2]), (a[-1][3], a[-1][4])
    b_start, b_end = (b[0][1], b[0][2]), (b[-1][3], b[-1][4])
    joints = [
        joint
        for joint, other in ((a_end, b_start), (a_start, b_end))
        if math.dist(joint, other) <= STACK_TOLERANCE
    ]
    boxes = [bounds([segment], STACK_TOLERANCE) for segment in b]

    def near(px: float, py: float) -> bool:
        if not (left <= px <= right and top <= py <= bottom):
            return False
        if any(math.dist((px, py), joint) < CORNER_CLEARANCE for joint in joints):
            return False
        return any(
            bx0 <= px <= bx1 and by0 <= py <= by1
            and distance_to_segment(px, py, segment) <= STACK_TOLERANCE
            for segment, (bx0, by0, bx1, by1) in zip(b, boxes)
        )

    longest = run = 0
    for _, x1, y1, x2, y2 in a:
        steps = max(1, math.ceil(math.hypot(x2 - x1, y2 - y1) / SAMPLE_STEP))
        for i in range(steps):
            if near(x1 + (x2 - x1) * i / steps, y1 + (y2 - y1) * i / steps):
                run += 1
                longest = max(longest, run)
            else:
                run = 0
    return longest * SAMPLE_STEP


def stacked_connectors(path: Path, parsed: list[tuple[int, str, list[Segment]]]) -> list[str]:
    findings: list[str] = []
    for i, (line_a, label_a, segments_a) in enumerate(parsed):
        for line_b, label_b, segments_b in parsed[i + 1 :]:
            shared = max(shared_run(segments_a, segments_b), shared_run(segments_b, segments_a))
            if shared > BORDER_MIN_RUN:
                findings.append(
                    f"{path.name}:{line_b}: connector {label_b} runs on top of {label_a}"
                    f" (line {line_a}) for about {shared:g}px - offset one route by at least"
                    f" {SHARED_PORT_MIN:g}px so each arrow stays traceable"
                )
    return findings


def shared_ports(
    path: Path, nodes: list[Rect], ports: list[tuple[int, float, float, int, str, str, int]]
) -> list[str]:
    findings: list[str] = []
    for i, (node_a, ax, ay, line_a, label_a, role_a, id_a) in enumerate(ports):
        for node_b, bx, by, line_b, label_b, role_b, id_b in ports[i + 1 :]:
            if node_a != node_b or id_a == id_b or role_a != role_b:
                continue
            node = nodes[node_a]
            side_a, length, along_a = port_edge(ax, ay, node)
            side_b, _, along_b = port_edge(bx, by, node)
            if side_a != side_b:
                continue
            minimum = SMALL_PORT_MIN if length < SMALL_EDGE else SHARED_PORT_MIN
            gap = abs(along_a - along_b)
            if gap < minimum:
                findings.append(
                    f"{path.name}:{line_b}: connector {label_b} attaches {gap:g}px from"
                    f" {label_a} (line {line_a}) on the {side_a} edge of node {node}"
                    f" (line {node.line}) - fan the ports at least {minimum:g}px apart"
                )
    return findings


def check_connectors(path: Path, source: str) -> list[str]:
    nodes = stroked_nodes(source)
    findings: list[str] = []
    ports: list[tuple[int, float, float, int, str, str, int]] = []
    parsed: list[tuple[int, str, list[Segment]]] = []
    for ident, (line, label, segments) in enumerate(connectors(source)):
        where = f"{path.name}:{line}: connector {label}"
        if segments is None:
            findings.append(
                f"{where} has path data the checker cannot parse"
                f" - write it with absolute M/L/H/V/Q/C/A commands"
            )
            continue
        parsed.append((line, label, segments))
        for kind, x1, y1, x2, y2 in segments:
            if kind == "line" and abs(x1 - x2) > AXIS_TOLERANCE and abs(y1 - y2) > AXIS_TOLERANCE:
                findings.append(
                    f"{where} has a diagonal segment {x1:g},{y1:g} -> {x2:g},{y2:g}"
                    f" - route it as a rounded right-angle elbow"
                )
                break
        for segment in segments:
            if segment[0] != "line":
                continue
            hit = next(((node, side) for node in nodes if (side := rides_border(segment, node))), None)
            if hit:
                node, side = hit
                findings.append(
                    f"{where} runs along the {side} border of node {node} (line {node.line})"
                    f" - leave the node perpendicular to the edge the port sits on"
                )
                break
        ends = ((segments[0][1], segments[0][2]), (segments[-1][3], segments[-1][4]))
        for px, py in ends:
            corner = next(((node, c) for node in nodes if (c := near_corner(px, py, node))), None)
            if corner:
                node, (cx, cy) = corner
                findings.append(
                    f"{where} attaches at {px:g},{py:g}, within {CORNER_CLEARANCE:g}px of the"
                    f" {cx:g},{cy:g} corner of node {node} (line {node.line})"
                    f" - move the port onto the straight part of the edge"
                )
                break
        for (px, py), role in zip(ends, ("start", "end")):
            for index, node in enumerate(nodes):
                if attached(px, py, node):
                    ports.append((index, px, py, line, label, role, ident))
    findings.extend(shared_ports(path, nodes, ports))
    findings.extend(stacked_connectors(path, parsed))
    return findings
