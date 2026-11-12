# SPDX-License-Identifier: MIT
"""Digest formatting and JSON serialization for Excalidraw scenes.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import asdict
from pathlib import Path

from .analyzer import analyze, scene_bounds
from .models import Scene


def _escape_markdown(text: str) -> str:
    encoded = html.escape(text, quote=False)
    return re.sub(r"([\\`*{}\[\]()#+\-.!_|>])", r"\\\1", encoded)


def _fold_lines(text: str, replacement: str) -> str:
    return replacement.join(text.splitlines())


def _escape_inline(text: str) -> str:
    return _escape_markdown(_fold_lines(text, " · "))


def _escape_table(text: str) -> str:
    return _escape_markdown(_fold_lines(text, " ⏎ "))


def digest(path: Path, scene: Scene, max_rows: int) -> str:
    info = analyze(scene)
    x0, y0, x1, y1 = scene_bounds(scene)
    out: list[str] = []
    out.append(f"# Excalidraw IR — {_escape_inline(path.name)}")
    out.append("")
    out.append(
        f"1 scene: {_escape_inline(scene.name)} "
        f"({len(scene.nodes)}n/{len(scene.edges)}e)"
    )
    out.append("")
    out.append(f"## Scene — {_escape_inline(scene.name)}")
    out.append("")
    out.append(
        f"- source canvas: {int(x1 - x0)}×{int(y1 - y0)} px "
        f"(aspect {((x1 - x0) / (y1 - y0)):.2f})"
        if y1 > y0
        else "- source canvas: empty"
    )
    out.append(
        f"- nodes: {info['nodes_total']} total / {info['nodes_drawable']} drawable "
        f"/ {info['containers']} containers, depth {info['max_depth']}"
    )
    out.append(
        f"- edges: {info['edges_total']} ({info['edges_labeled']} labeled, "
        f"{info['edges_dangling']} dangling), cycle: {info['has_cycle']}"
    )
    out.append(f"- shapes: {info['shapes']}")
    out.append(f"- type candidates: {', '.join(info['type_candidates'])}")
    out.append(
        f"- budget: nodes {'OVER' if info['over_node_budget'] else 'ok'} (max 9), "
        f"edges {'OVER' if info['over_edge_budget'] else 'ok'} (max 12)"
    )
    dropped = {key: count for key, count in scene.discarded.items() if count}
    if dropped:
        out.append(
            "- discarded: "
            + ", ".join(
                f"{count} {key.replace('_', ' ')}" for key, count in dropped.items()
            )
        )
    if info["hubs"]:
        hubs = ", ".join(
            f"{_escape_inline(h['label'] or h['id'])}({h['degree']})"
            for h in info["hubs"]
        )
        out.append(f"- hubs (focal candidates): {hubs}")
    if info["entry_points"]:
        out.append(
            f"- entry points: {', '.join(_escape_inline(label) for label in info['entry_points'])}"
        )
    if info["terminals"]:
        out.append(
            f"- terminals: {', '.join(_escape_inline(label) for label in info['terminals'])}"
        )
    if info["orphans"]:
        out.append(
            f"- unconnected: {', '.join(_escape_inline(label) for label in info['orphans'])}"
        )
    if info["collapsible_groups"]:
        out.append("- collapsible groups (simplify here first):")
        for group in info["collapsible_groups"]:
            kids = ", ".join(_escape_inline(label) for label in group["child_labels"])
            out.append(
                f"  - {_escape_inline(group['label'])} — "
                f"{group['children']} children: {kids}"
            )

    out.append("")
    out.append("### Nodes")
    out.append("")
    out.append("| id | label | shape | depth | parent | deg | box |")
    out.append("|---|---|---|---|---|---|---|")
    listed = [n for n in scene.nodes if n.label or n.children]
    for node in listed[:max_rows]:
        out.append(
            f"| {_escape_table(node.id)} | {_escape_table(node.label)} | "
            f"{_escape_table(node.shape)} | {node.depth} | "
            f"{_escape_table(node.parent or '-')} | {node.in_degree}/{node.out_degree} | "
            f"{int(node.x)},{int(node.y)} {int(node.w)}×{int(node.h)} |"
        )
    if len(listed) > max_rows:
        out.append(f"| … | +{len(listed) - max_rows} more (use --json) | | | | | |")

    out.append("")
    out.append("### Edges")
    out.append("")
    out.append("| source | target | label | style |")
    out.append("|---|---|---|---|")
    names = {n.id: (n.label.split("\n")[0] or n.id) for n in scene.nodes}
    for edge in scene.edges[:max_rows]:
        marks = []
        if edge.dashed:
            marks.append("dashed")
        if edge.bidirectional:
            marks.append("bidir")
        if edge.undirected:
            marks.append("undirected")
        out.append(
            f"| {_escape_table(names.get(edge.source or '', '?'))} | "
            f"{_escape_table(names.get(edge.target or '', '?'))} | "
            f"{_escape_table(edge.label) or '-'} | {' '.join(marks) or '-'} |"
        )
    if len(scene.edges) > max_rows:
        out.append(f"| … | +{len(scene.edges) - max_rows} more (use --json) | | |")
    out.append("")
    return "\n".join(out)


def to_json(path: Path, scene: Scene) -> str:
    payload = {
        "source": str(path),
        "scene": {
            "name": scene.name,
            "bounds": dict(zip(("x0", "y0", "x1", "y1"), scene_bounds(scene))),
            "analysis": analyze(scene),
            "discarded": scene.discarded,
            "nodes": [asdict(node) for node in scene.nodes],
            "edges": [asdict(edge) for edge in scene.edges],
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
