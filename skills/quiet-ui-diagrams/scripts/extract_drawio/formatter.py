# SPDX-License-Identifier: MIT
"""Digest formatting and JSON serialization for draw.io extractions.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import asdict
from pathlib import Path

from .analyzer import analyze, page_bounds
from .models import Page, _fail


def _escape_markdown(text: str) -> str:
    encoded = html.escape(text, quote=False)
    return re.sub(r"([\\`*{}\[\]()#+\-.!_|>])", r"\\\1", encoded)


def _fold_lines(text: str, replacement: str) -> str:
    return replacement.join(text.splitlines())


def _escape_inline(text: str) -> str:
    return _escape_markdown(_fold_lines(text, " · "))


def _escape_table(text: str) -> str:
    return _escape_markdown(_fold_lines(text, " ⏎ "))


def digest(path: Path, pages: list[Page], selected: list[Page], max_rows: int) -> str:
    out: list[str] = []
    out.append(f"# draw.io IR — {_escape_inline(path.name)}")
    out.append("")
    out.append(
        f"{len(pages)} page(s): "
        + ", ".join(
            f"[{p.index}] {_escape_inline(p.name)} ({len(p.nodes)}n/{len(p.edges)}e)"
            for p in pages
        )
    )
    for page in selected:
        info = analyze(page)
        x0, y0, x1, y1 = page_bounds(page)
        out.append("")
        out.append(f"## Page {page.index} — {_escape_inline(page.name)}")
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
        listed = [n for n in page.nodes if n.label or n.children]
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
        names = {n.id: (n.label.split("\n")[0] or n.id) for n in page.nodes}
        for edge in page.edges[:max_rows]:
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
        if len(page.edges) > max_rows:
            out.append(f"| … | +{len(page.edges) - max_rows} more (use --json) | | |")
    out.append("")
    return "\n".join(out)


def to_json(path: Path, pages: list[Page], selected: list[Page]) -> str:
    payload = {
        "source": str(path),
        "pages_total": len(pages),
        "pages": [
            {
                "id": p.id,
                "name": p.name,
                "index": p.index,
                "bounds": dict(zip(("x0", "y0", "x1", "y1"), page_bounds(p))),
                "analysis": analyze(p),
                "nodes": [asdict(n) for n in p.nodes],
                "edges": [asdict(e) for e in p.edges],
            }
            for p in selected
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def select_pages(pages: list[Page], selector: str | None) -> list[Page]:
    if selector is None:
        return pages if len(pages) == 1 else pages[:1]
    if selector == "all":
        return pages
    if selector.isdecimal():
        index = int(selector)
        match = [p for p in pages if p.index == index]
        if not match:
            _fail(f"no page with index {index} (have 0..{len(pages) - 1})")
        return match
    match = [p for p in pages if p.name.lower() == selector.lower()]
    if not match:
        names = ", ".join(p.name for p in pages)
        _fail(f"no page named {selector!r} (have: {names})")
    return match
