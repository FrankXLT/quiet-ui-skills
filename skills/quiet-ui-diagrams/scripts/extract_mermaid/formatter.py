# SPDX-License-Identifier: MIT
"""Digest formatting and JSON serialization for Mermaid diagram extractions.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .analyzer import analyze, parse_block
from .constants import REGION_KEYWORDS
from .models import Diagram, ExtractError, SourceBlock, _fail


def _escape_markdown(text: str) -> str:
    encoded = html.escape(text, quote=False)
    return re.sub(r"([\\`*{}\[\]()#+\-.!_|>])", r"\\\1", encoded)


def _escape_table(text: str) -> str:
    return _escape_markdown(text.replace("\n", " ⏎ "))


def _block_summary(block: SourceBlock, selected: list[Diagram]) -> str:
    diagram = next((item for item in selected if item.index == block.index), None)
    if diagram is None:
        try:
            diagram = parse_block(block)
        except ExtractError as error:
            return f"[{block.index}] unparsed: {_escape_markdown(str(error))}"
    return f"[{diagram.index}] {diagram.kind} ({len(diagram.nodes)}n/{len(diagram.edges)}e)"


def _fragment_digest(item: dict[str, Any]) -> str:
    keyword = REGION_KEYWORDS.get(item["kind"], "else")
    parts = [item["label"] or "unlabeled"] + [
        f"{keyword}: {region or 'unlabeled'}" for region in item["regions"]
    ]
    return " | ".join(_escape_table(part) for part in parts)


def digest(
    path: Path,
    blocks: list[SourceBlock],
    selected: list[Diagram],
    max_rows: int,
) -> str:
    output = [f"# Mermaid IR — {path.name}", ""]
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
                f"- source layout: none (Mermaid is layout-free); direction: {diagram.direction}",
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
        if any(diagram.discarded.values()):
            output.append(
                f"- discarded: {diagram.discarded['style_directives']} style directives, "
                f"{diagram.discarded['click_handlers']} click handlers, "
                f"{diagram.discarded['config_directives']} config directives"
            )
        if diagram.fragments:
            fragments = ", ".join(
                f"{item['kind']}({_fragment_digest(item)})"
                for item in diagram.fragments
            )
            output.append(f"- fragments: {fragments}")
        if diagram.autonumber:
            numbering = "; ".join(
                "off"
                if item["off"]
                else f"from {item['start']}, step {item['step']}"
                for item in diagram.autonumber
            )
            output.append(f"- autonumber: {numbering}")
        if diagram.notes:
            output.append(
                f"- notes: {'; '.join(_escape_markdown(note) for note in diagram.notes[:6])}"
            )
        if info["hubs"]:
            output.append(
                "- hubs (focal candidates): "
                + ", ".join(
                    f"{_escape_markdown(hub['label'])}({hub['degree']})"
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
                "| id | label | shape | depth | parent | deg | fields |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for node in diagram.nodes[:max_rows]:
            output.append(
                f"| {_escape_table(node.id)} | {_escape_table(node.label)} | {node.shape} | "
                f"{node.depth} | {node.parent or '-'} | {node.in_degree}/{node.out_degree} | "
                f"{_escape_table('; '.join(node.fields)) or '-'} |"
            )
        if len(diagram.nodes) > max_rows:
            output.append(
                f"| … | +{len(diagram.nodes) - max_rows} more (use --json) | | | | | |"
            )

        output.extend(
            [
                "",
                "### Edges",
                "",
                "| source | target | label | style |",
                "|---|---|---|---|",
            ]
        )
        names = {node.id: node.label.split("\n")[0] for node in diagram.nodes}
        for edge in diagram.edges[:max_rows]:
            marks = [edge.style, edge.arrowhead]
            if edge.bidirectional:
                marks.append("bidir")
            if edge.undirected:
                marks.append("undirected")
            output.append(
                f"| {_escape_table(names.get(edge.source, edge.source))} | "
                f"{_escape_table(names.get(edge.target, edge.target))} | "
                f"{_escape_table(edge.label) or '-'} | {' '.join(marks)} |"
            )
        if len(diagram.edges) > max_rows:
            output.append(
                f"| … | +{len(diagram.edges) - max_rows} more (use --json) | | |"
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
                    "analysis": analyze(diagram),
                    "discarded": diagram.discarded,
                    "fragments": diagram.fragments,
                    "notes": diagram.notes,
                    "autonumber": diagram.autonumber,
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
    if selector.isdecimal():
        index = int(selector)
        selected = [block for block in blocks if block.index == index]
        if not selected:
            _fail(f"no diagram with index {index} (have 0..{len(blocks) - 1})")
        return selected
    _fail("--diagram must be an index or 'all'")
