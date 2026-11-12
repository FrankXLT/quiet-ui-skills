# SPDX-License-Identifier: MIT
"""State diagram and entity-relationship (ER) diagram parsers for Mermaid.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

from .constants import (
    ER_CARDINALITIES,
    ER_CARDINALITY,
    ER_IDENTIFICATIONS,
    ER_IDENTIFICATION,
    ER_NAME,
    ER_QUOTED_NAME,
    _er_entity,
)
from .flow_helpers import _parse_node_expression, _strip_class_suffix
from .flow_parser import _discard_nonsemantic
from .models import Diagram, Node, _fail, clean_label


def _state_endpoint(
    diagram: Diagram,
    token: str,
    role: str,
    parent: str | None,
) -> str | None:
    value = _strip_class_suffix(token.strip())
    if value == "[*]":
        prefix = "start" if role == "source" else "end"
        count = sum(node.id.startswith("__" + prefix) for node in diagram.nodes)
        node_id = f"__{prefix}_{count + 1}"
        diagram.add_node(node_id, f"[{prefix}]", prefix, parent)
        return node_id
    parsed = _parse_node_expression(value)
    if parsed is None:
        return None
    node_id, label, shape = parsed
    if not shape:
        existing = diagram.node_map.get(node_id)
        shape = existing.shape if existing is not None else "state"
    elif shape == "rect":
        shape = "state"
    diagram.add_node(node_id, label, shape, parent)
    return node_id


def _parse_state(
    diagram: Diagram, lines: list[tuple[int, str]], header_position: int
) -> None:
    containers: list[str] = []
    note_start: int | None = None
    descriptions: dict[str, list[str]] = {}
    pending_descriptions = diagram._state_descriptions
    for line_number, raw in lines[header_position + 1 :]:
        text = raw.strip()
        if not text:
            continue
        if note_start is not None:
            if re.fullmatch(r"end\s+note", text, re.I):
                note_start = None
            continue
        note = re.fullmatch(
            r"note\s+(?:left|right)\s+of\s+[^\s:]+(?:\s*:\s*(.*))?", text, re.I
        )
        if note:
            if note.group(1) is None:
                note_start = line_number
            else:
                diagram.notes.append(clean_label(note.group(1)))
            continue
        if _discard_nonsemantic(diagram, text):
            continue
        if text == "}":
            if containers:
                containers.pop()
            continue
        parent = containers[-1] if containers else None
        direction_match = re.match(r"^direction\s+(TD|TB|LR|RL|BT)$", text, re.I)
        if direction_match and not containers:
            diagram.direction = direction_match.group(1).upper()
            continue
        composite = re.match(r"^state\s+([\w.:-]+)\s*\{$", text, re.I)
        if composite:
            node_id = composite.group(1)
            diagram.add_node(node_id, node_id, "container", parent, container=True)
            containers.append(node_id)
            continue
        alias = re.match(r'^state\s+"(.*?)"\s+as\s+([\w.:-]+)\s*(\{)?$', text, re.I)
        if alias:
            label, node_id, opening = alias.groups()
            diagram.add_node(
                node_id,
                clean_label(label),
                "container" if opening else "state",
                parent,
                container=bool(opening),
            )
            if node_id not in pending_descriptions:
                descriptions.pop(node_id, None)
            if opening:
                containers.append(node_id)
            continue
        stereotype = re.match(
            r"^state\s+([\w.:-]+)\s+<<(fork|join|choice)>>$", text, re.I
        )
        if stereotype:
            diagram.add_node(
                stereotype.group(1),
                stereotype.group(1),
                stereotype.group(2).casefold(),
                parent,
            )
            continue
        if "-->" in text:
            source_text, target_text = text.split("-->", 1)
            label = ""
            label_separator = re.search(r"(?<!:):(?!:)", target_text)
            if label_separator:
                label = target_text[label_separator.end() :]
                target_text = target_text[: label_separator.start()]
            source = _state_endpoint(diagram, source_text, "source", parent)
            target = _state_endpoint(diagram, target_text, "target", parent)
            if source is None or target is None:
                _fail(f"malformed edge at line {line_number}")
            diagram.add_edge(source, target, clean_label(label))
            continue
        description = re.match(r"^([\w.-]+)\s*:\s*(.+)$", text)
        if description:
            node_id, label = description.group(1), clean_label(description.group(2))
            if node_id not in descriptions:
                existing = diagram.node_map.get(node_id)
                descriptions[node_id] = (
                    [existing.label] if existing and existing.label != node_id else []
                )
            descriptions[node_id].append(label)
            diagram.add_node(node_id, label, "state", parent)
            pending_descriptions[node_id] = descriptions[node_id]
            continue
        plain = re.match(r"^state\s+([\w.:-]+)$", text, re.I)
        if plain:
            diagram.add_node(plain.group(1), plain.group(1), "state", parent)
            continue
        if text != "--" and re.fullmatch(r"[\w.:-]+", text):
            if text not in diagram.node_map:
                diagram.add_node(text, text, "state", parent)

    if note_start is not None:
        _fail(f"unterminated state note at line {note_start}")

    for node_id, parts in pending_descriptions.items():
        label = "\n".join(parts)
        if label:
            diagram.node_map[node_id].label = label
    pending_descriptions.clear()


def _er_label(token: str) -> str:
    return clean_label(token) if token.startswith('"') else token


def _er_declaration(
    match: re.Match[str] | None,
) -> tuple[str, str, bool, bool] | None:
    if match is None:
        return None
    name_token, alias_token, block = match.groups()
    name = _er_entity(name_token)
    if name is None:
        return None
    if alias_token is None:
        return name, _er_label(name_token), False, block is not None
    if _er_entity(alias_token) is None:
        return None
    return name, _er_label(alias_token), True, block is not None


def _er_table(
    diagram: Diagram,
    aliased_names: set[str],
    name: str,
    label: str,
    aliased: bool = False,
) -> Node:
    existing = diagram.node_map.get(name)
    if aliased and name not in aliased_names:
        aliased_names.add(name)
        if existing is not None:
            existing.label = label
            return existing
    elif existing is not None:
        return existing
    return diagram.add_node(name, label, "table")


def _parse_er(
    diagram: Diagram, lines: list[tuple[int, str]], header_position: int
) -> None:
    current: Node | None = None
    aliased_names: set[str] = set()
    relationship = re.compile(
        rf"^({ER_NAME})\s+"
        rf"(?i:({ER_CARDINALITY})\s*({ER_IDENTIFICATION})\s*({ER_CARDINALITY}))\s+"
        rf"({ER_NAME})\s*(?::\s*(.*))?$"
    )
    declaration = re.compile(rf"^({ER_NAME})(?:\s*\[({ER_NAME})\])?\s*(\{{)?$")
    for line_number, raw in lines[header_position + 1 :]:
        text = raw.strip()
        if not text:
            continue
        if _discard_nonsemantic(diagram, text):
            continue
        if text == "}":
            current = None
            continue
        direction_match = re.match(r"^direction\s+(TD|TB|LR|RL|BT)$", text, re.I)
        if direction_match and current is None:
            diagram.direction = direction_match.group(1).upper()
            continue
        declared = _er_declaration(declaration.match(text))
        if declared is not None and declared[3]:
            current = _er_table(diagram, aliased_names, *declared[:3])
            continue
        if current is not None:
            current.fields.append(clean_label(text))
            continue
        edge = relationship.match(text)
        if edge and _er_entity(edge.group(1)) and _er_entity(edge.group(5)):
            source_tok, left, link, right, target_tok, rel_label = edge.groups()
            s_ent, t_ent = _er_entity(source_tok), _er_entity(target_tok)
            source = _er_table(diagram, aliased_names, s_ent, _er_label(source_tok)).id
            target = _er_table(diagram, aliased_names, t_ent, _er_label(target_tok)).id
            separator = ER_IDENTIFICATIONS[link.casefold()]
            left_sym = ER_CARDINALITIES[left.casefold()][0]
            right_sym = ER_CARDINALITIES[right.casefold()][1]
            label_parts = [f"{left_sym} {separator} {right_sym}"]
            if rel_label:
                label_parts.append(clean_label(rel_label))
            diagram.add_edge(
                source,
                target,
                " · ".join(label_parts),
                "dashed" if separator == ".." else "solid",
                "cardinality",
                undirected=True,
            )
            continue
        unquoted = re.sub(ER_QUOTED_NAME, '""', text)
        if "--" in unquoted or ".." in unquoted:
            _fail(f"malformed edge at line {line_number}")
        if declared is not None:
            _er_table(diagram, aliased_names, *declared[:3])
