# SPDX-License-Identifier: MIT
"""Flowchart graph parsing, edge operator lexing, and subgraph hierarchy for Mermaid.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

from .constants import _EDGE_ID, STYLE_DIRECTIVES
from .flow_helpers import (
    _logical_statements,
    _parse_node_expression,
    _split_top_level,
    _top_level_mask,
)
from .models import Diagram, _Operator, _fail, clean_label


def _operator_style(token: str) -> tuple[str, str, bool, bool]:
    if token.startswith("~"):
        return "invisible", "none", False, True
    style = "dashed" if "." in token else "thick" if "=" in token else "solid"
    arrowhead = (
        "cross"
        if token.endswith("x")
        else "circle"
        if token.endswith("o")
        else "arrow"
    )
    undirected = ">" not in token and not token.endswith(("x", "o"))
    bidirectional = (token.startswith("<") and token.endswith(">")) or (
        token.startswith(("x", "o")) and token.endswith(("x", "o"))
    )
    return style, arrowhead, bidirectional, undirected


def _edge_operators(text: str) -> list[_Operator]:
    mask = _top_level_mask(text)
    operators: list[_Operator] = []
    occupied: list[tuple[int, int]] = []

    text_edge = re.compile(
        r"(?P<opening>"
        r"<(?:--|==)"
        r"|(?<![\w.:-])[xo](?:--|==)"
        r"|(?:--|==)"
        r")"
        r"(?:\s(?P<spaced>.+?)\s|(?![-=.\s])(?P<compact>[^\s|<>]+?))"
        r"(?P<closing>-{2,}>|--[xo]|=+>|={2,}|-{3,})"
    )
    dotted_edge = re.compile(
        r"(?P<opening>"
        r"<-\."
        r"|(?<![\w.:-])[xo]-\."
        r"|-\."
        r")"
        r"(?:\s(?P<spaced>.+?)\s|(?![-=.\s])(?P<compact>[^\n|<>]+?))"
        r"(?P<closing>\.-+[>xo]|\.-+)"
    )
    trailing_operator = re.compile(
        r"(?:\.-+[>xo]|\.-+|-{2,}>|--[xo]|=+>|={2,}|-{3,}|~{3,})"
        r"(?:\|[^|\n]*\|)?\s*$"
    )
    for edge_pattern in (text_edge, dotted_edge):
        for match in edge_pattern.finditer(mask):
            opening = match.group("opening")
            operator_start = match.start()
            if opening.startswith(("x", "o")):
                prefix = mask[:operator_start]
                if not prefix.strip() or trailing_operator.search(prefix):
                    operator_start += 1
                    opening = opening[1:]
            token = opening + match.group("closing")
            style, arrowhead, bidirectional, undirected = _operator_style(token)
            operators.append(
                _Operator(
                    operator_start,
                    match.end(),
                    clean_label(text[match.end("opening") : match.start("closing")]),
                    style,
                    arrowhead,
                    bidirectional,
                    undirected,
                )
            )
            occupied.append((operator_start, match.end()))

    pattern = re.compile(
        r"[xo][-=.]+[xo]|<[-=.]+>|-+\.+-+>|=+>|-+(?:>|x|o)|-+\.+-+|={3,}|-{3,}|~{3,}"
    )
    for match in pattern.finditer(mask):
        if any(start <= match.start() < end for start, end in occupied):
            continue
        token = match.group()
        end = match.end()
        label = ""
        opening_pipe = end
        while opening_pipe < len(text) and text[opening_pipe] in " \t":
            opening_pipe += 1
        if opening_pipe < len(text) and text[opening_pipe] == "|":
            close = text.find("|", opening_pipe + 1)
            if close != -1:
                label = clean_label(text[opening_pipe + 1 : close])
                end = close + 1
        style, arrowhead, bidirectional, undirected = _operator_style(token)
        operators.append(
            _Operator(
                match.start(), end, label, style, arrowhead, bidirectional, undirected
            )
        )
        occupied.append((match.start(), end))
    return sorted(operators, key=lambda operator: operator.start)


def _endpoint_group(
    diagram: Diagram, text: str, parent: str | None
) -> list[str] | None:
    identifiers: list[str] = []
    for raw in _split_top_level(text.strip(), "&"):
        parsed = _parse_node_expression(raw)
        if parsed is None:
            return None
        node_id, label, shape = parsed
        diagram.add_node(node_id, label, shape, parent)
        identifiers.append(node_id)
    return identifiers or None


def _strip_edge_ids(text: str) -> tuple[str, list[str]]:
    """Drop Mermaid v11.6+ edge IDs (A e1@--> B) and return the IDs found."""
    mask = _top_level_mask(text)
    operator_starts = {operator.start for operator in _edge_operators(text)}
    ids: list[str] = []
    pieces: list[str] = []
    cursor = 0
    for match in _EDGE_ID.finditer(mask):
        if match.end() not in operator_starts:
            continue
        pieces.append(text[cursor : match.start()])
        cursor = match.end()
        ids.append(match.group(1))
    if not ids:
        return text, ids
    pieces.append(text[cursor:])
    return "".join(pieces), ids


def _discard_nonsemantic(diagram: Diagram, text: str) -> bool:
    lowered = text.casefold()
    if any(lowered.startswith(prefix.casefold()) for prefix in STYLE_DIRECTIVES):
        diagram.discarded["style_directives"] += 1
        return True
    if lowered.startswith("click "):
        diagram.discarded["click_handlers"] += 1
        return True
    return False


def _parse_flowchart(
    diagram: Diagram, lines: list[tuple[int, str]], header_position: int
) -> None:
    containers: list[str] = []
    invisible_links = 0
    edge_ids: set[str] = set()
    for line_number, raw in _logical_statements(lines[header_position + 1 :]):
        text = raw.strip()
        if not text:
            continue
        lowered = text.casefold()
        if _discard_nonsemantic(diagram, text):
            continue
        id_match = re.match(r"^([A-Za-z_][\w-]*)@\{", text)
        if id_match and id_match.group(1) in edge_ids:
            continue
        if lowered.startswith("direction "):
            if not containers:
                direction = text.split(maxsplit=1)[1].upper()
                if direction in {"TD", "TB", "LR", "RL", "BT"}:
                    diagram.direction = direction
            continue
        if lowered.startswith("subgraph "):
            spec = text.split(maxsplit=1)[1].strip()
            parsed = _parse_node_expression(spec)
            if parsed is None:
                cnt = len([node for node in diagram.nodes if node.container]) + 1
                node_id, label = f"subgraph-{cnt}", clean_label(spec)
            else:
                node_id, label, _shape = parsed
            parent = containers[-1] if containers else None
            diagram.add_node(node_id, label, "container", parent, container=True)
            containers.append(node_id)
            continue
        if lowered == "end":
            if containers:
                containers.pop()
            continue

        text, found_ids = _strip_edge_ids(text)
        edge_ids.update(found_ids)
        operators = _edge_operators(text)
        parent = containers[-1] if containers else None
        if operators:
            segments: list[str] = []
            cursor = 0
            for operator in operators:
                segments.append(text[cursor : operator.start])
                cursor = operator.end
            segments.append(text[cursor:])
            if len(segments) != len(operators) + 1:
                _fail(f"malformed edge at line {line_number}")
            groups = [_endpoint_group(diagram, seg, parent) for seg in segments]
            if any(group is None for group in groups):
                _fail(f"malformed edge at line {line_number}")
            valid_groups = [g for g in groups if g is not None]
            for idx, operator in enumerate(operators):
                if operator.style == "invisible":
                    invisible_links += 1
                    continue
                for source in valid_groups[idx]:
                    for target in valid_groups[idx + 1]:
                        diagram.add_edge(
                            source,
                            target,
                            operator.label,
                            operator.style,
                            operator.arrowhead,
                            operator.bidirectional,
                            operator.undirected,
                        )
            continue
        if re.search(r"(?:--|==|-.).*?(?:>|x|o|-)", _top_level_mask(text)):
            _fail(f"malformed edge at line {line_number}")
        parsed = _parse_node_expression(text)
        if parsed is not None:
            node_id, label, shape = parsed
            diagram.add_node(node_id, label, shape, parent)
    if invisible_links:
        diagram.notes.append(f"{invisible_links} invisible layout links ignored")
