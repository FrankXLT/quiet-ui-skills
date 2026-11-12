# SPDX-License-Identifier: MIT
"""Digest formatting and JSON serialization for PlantUML diagram extractions.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .analyzer import analyze, node_ref
from .format_helpers import (
    _block_summary,
    _escape_markdown,
    _escape_table,
    _fragment_summary,
    _note_summary,
)
from .models import Diagram, SourceBlock, _fail


def digest(
    path: Path,
    blocks: list[SourceBlock],
    selected: list[Diagram],
    max_rows: int,
) -> str:
    output = [f"# PlantUML IR — {path.name}", ""]
    output.append(
        f"{len(blocks)} diagram(s): "
        + ", ".join(_block_summary(block, selected) for block in blocks)
    )
    for diagram in selected:
        info = analyze(diagram)
        output.extend(
            [
                "",
                f"## Diagram {diagram.index} — {diagram.kind}",
                "",
                f"- source layout: none (PlantUML is layout-free); direction: {diagram.direction}",
                f"- nodes: {info['nodes_total']} total / {info['nodes_drawable']} drawable / "
                f"{info['containers']} containers, depth {info['max_depth']}",
                f"- edges: {info['edges_total']} ({info['edges_labeled']} labeled, "
                f"{info['edges_dangling']} dangling), cycle: {info['has_cycle']}",
                f"- shapes: {info['shapes']}",
                f"- type candidates: {', '.join(info['type_candidates'])}",
                f"- budget: nodes {'OVER' if info['over_node_budget'] else 'ok'} (max 9), "
                f"edges {'OVER' if info['over_edge_budget'] else 'ok'} (max 12)",
            ]
        )
        if diagram.title:
            output.append(f"- title: {_escape_markdown(diagram.title)}")
        if diagram.discarded["skin"] or diagram.discarded["includes"]:
            parts = []
            if diagram.discarded["skin"]:
                parts.append(f"{diagram.discarded['skin']} skinparam")
            if diagram.discarded["includes"]:
                parts.append(f"{diagram.discarded['includes']} includes")
            output.append(f"- discarded: {', '.join(parts)}")
        if diagram.fragments:
            output.append(
                "- fragments (message numbers are the edge `#` column):"
            )
            for item in diagram.fragments:
                output.append(f"  - {_fragment_summary(item)}")
        if diagram.activations:
            output.append(
                "- activations (after message #): "
                + ", ".join(
                    f"{_escape_markdown(item['participant'])}:{item['action']}"
                    f"@{item['after_message']}"
                    for item in diagram.activations[:max_rows]
                )
                + (
                    f", +{len(diagram.activations) - max_rows} more (use --json)"
                    if len(diagram.activations) > max_rows
                    else ""
                )
            )
        if diagram.note_details:
            shown = diagram.note_details[:max_rows]
            output.append(
                "- notes (after message #): "
                + "; ".join(_note_summary(item) for item in shown)
                + (
                    f"; +{len(diagram.note_details) - len(shown)} more (use --json)"
                    if len(diagram.note_details) > len(shown)
                    else ""
                )
            )
        if info["hubs"]:
            output.append(
                "- hubs (focal candidates): "
                + ", ".join(
                    f"{_escape_markdown(hub['ref'])}({hub['degree']})"
                    for hub in info["hubs"]
                )
            )
        if info["entry_points"]:
            output.append(
                f"- entry points: {', '.join(_escape_markdown(label) for label in info['entry_points'])}"
            )
        if info["terminals"]:
            output.append(
                f"- terminals: {', '.join(_escape_markdown(label) for label in info['terminals'])}"
            )
        if info["orphans"]:
            output.append(
                f"- unconnected: {', '.join(_escape_markdown(label) for label in info['orphans'])}"
            )
        if info["collapsible_groups"]:
            output.append("- collapsible groups (simplify here first):")
            for group in info["collapsible_groups"]:
                output.append(
                    f"  - {_escape_markdown(group['label'])} — {group['children']} children: "
                    + ", ".join(
                        _escape_markdown(label)
                        for label in group["child_labels"]
                    )
                )

        output.extend(
            [
                "",
                "### Nodes",
                "",
                "| id | label | shape | stereotype | depth | parent | deg | fields |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for node in diagram.nodes[:max_rows]:
            output.append(
                f"| {_escape_table(node.id)} | {_escape_table(node.label)} | {node.shape} | "
                f"{_escape_table(node.stereotype) or '-'} | "
                f"{node.depth} | {_escape_table(node.parent) if node.parent else '-'} | "
                f"{node.in_degree}/{node.out_degree} | "
                f"{_escape_table('; '.join(node.fields)) or '-'} |"
            )
        if len(diagram.nodes) > max_rows:
            output.append(
                f"| … | +{len(diagram.nodes) - max_rows} more (use --json) | | | | | | |"
            )

        output.extend(
            [
                "",
                "### Edges",
                "",
                "| # | source | target | label | style |",
                "|---|---|---|---|---|",
            ]
        )
        names = {node.id: node_ref(node) for node in diagram.nodes}
        for edge in diagram.edges[:max_rows]:
            marks = [edge.style, edge.arrowhead]
            if edge.bidirectional:
                marks.append("bidir")
            if edge.undirected:
                marks.append("undirected")
            if edge.navigable:
                marks.append(f"navigable {edge.navigable}")
            if edge.source_cardinality or edge.target_cardinality:
                ends = []
                if edge.source_cardinality:
                    ends.append(
                        f"{_escape_table(edge.source_cardinality)} (source)"
                    )
                if edge.target_cardinality:
                    ends.append(
                        f"{_escape_table(edge.target_cardinality)} (target)"
                    )
                marks.append("cardinality " + " .. ".join(ends))
            output.append(
                f"| {edge.order} | {_escape_table(names.get(edge.source, edge.source))} | "
                f"{_escape_table(names.get(edge.target, edge.target))} | "
                f"{_escape_table(edge.label) or '-'} | {' '.join(marks)} |"
            )
        if len(diagram.edges) > max_rows:
            output.append(
                f"| … | +{len(diagram.edges) - max_rows} more (use --json) | | | |"
            )
    output.append("")
    return "\n".join(output)


def to_json(
    path: Path, blocks: list[SourceBlock], selected: list[Diagram]
) -> str:
    return json.dumps(
        {
            "source": str(path),
            "diagrams_total": len(blocks),
            "diagrams": [
                {
                    "index": diagram.index,
                    "kind": diagram.kind,
                    "source_line": diagram.source_line,
                    "direction": diagram.direction,
                    "title": diagram.title,
                    "analysis": analyze(diagram),
                    "discarded": diagram.discarded,
                    "fragments": diagram.fragments,
                    "activations": diagram.activations,
                    "notes": diagram.notes,
                    "note_details": diagram.note_details,
                    "nodes": [asdict(node) for node in diagram.nodes],
                    "edges": [asdict(edge) for edge in diagram.edges],
                }
                for diagram in selected
            ],
        },
        indent=2,
        ensure_ascii=False,
    )


def select_blocks(
    blocks: list[SourceBlock], selector: str | None
) -> list[SourceBlock]:
    """Pick blocks before parsing, so a bad block fails only when selected."""
    if selector is None:
        return blocks[:1]
    if selector == "all":
        return blocks
    if selector.isdigit():
        index = int(selector)
        selected = [block for block in blocks if block.index == index]
        if not selected:
            _fail(f"no diagram with index {index} (have 0..{len(blocks) - 1})")
        return selected
    _fail("--diagram must be an index or 'all'")
