# SPDX-License-Identifier: MIT
"""Class diagram parser for classifiers, packages, relationships, and members in PlantUML.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

from .arrow_helpers import (
    _class_relationship,
    _edge_split,
    _endpoint_code,
    _split_cardinality,
)
from .constants import CLASS_REL_RE, MAX_STATEMENT_CHARS, UNSUPPORTED_CLASS
from .loader import _statement_too_long
from .models import Diagram, Node, _fail, clean_label
from .skin_notes import _SkinBlocks, _parse_note, _record_note
from .token_helpers import (
    _parse_classifier_header,
    _parse_declaration_tail,
    _partition_unquoted,
    _strip_trailing_colors,
)


def _parse_class(diagram: Diagram, lines: list[tuple[int, str]]) -> None:
    current: Node | None = None
    current_line = 0
    blocks: list[tuple[str | None, int]] = []

    def scope() -> list[str]:
        return [block for block, _line in blocks if block is not None]

    def add_link(
        split: tuple[str, re.Match[str], str],
        line_number: int,
        link_scope: list[str],
    ) -> None:
        left, arrow, right = split
        right, label = _partition_unquoted(right, ":")
        left_name, left_card = _split_cardinality(left, before_arrow=True)
        right_name, right_card = _split_cardinality(right, before_arrow=False)
        edge_error = f"malformed edge at line {line_number}"
        source = class_ref(left_name, edge_error, link_scope)
        target = class_ref(right_name, edge_error, link_scope)
        (
            arrowhead,
            style,
            reverse,
            bidirectional,
            undirected,
            hidden,
            navigable,
        ) = _class_relationship(arrow, line_number)
        if reverse:
            source, target = target, source
            left_card, right_card = right_card, left_card
            navigable = {"source": "target", "target": "source"}.get(
                navigable, navigable
            )
        if hidden:
            diagram.discarded["skin"] += 1
            return
        diagram.add_edge(
            source,
            target,
            clean_label(label),
            style,
            arrowhead,
            bidirectional=bidirectional,
            undirected=undirected,
            source_cardinality=clean_label(left_card),
            target_cardinality=clean_label(right_card),
            navigable=navigable,
        )

    def class_ref(
        token: str, error: str, link_scope: list[str] | None = None
    ) -> str:
        parsed = _endpoint_code(token)
        if parsed is None:
            _fail(error)
        code, display = parsed
        node_id = diagram.resolve(
            code, scope() if link_scope is None else link_scope
        )
        if node_id not in diagram.node_map:
            diagram.add_node(node_id, clean_label(display) or node_id, "class")
        return node_id

    pending_links: list[tuple[tuple[str, re.Match[str], str], int, list[str]]] = []
    pending_notes: list[tuple[str, str, str, int, list[str]]] = []
    skin = _SkinBlocks()
    for line_number, raw in lines:
        text = raw.strip()
        if not text:
            continue
        if len(text) > MAX_STATEMENT_CHARS:
            _statement_too_long(line_number)
        if current is not None:
            if text == "}":
                current = None
                continue
            if text in {"--", "..", "==", "__"}:
                continue
            current.fields.append(clean_label(text))
            continue
        if skin.consume(diagram, text, line_number):
            continue
        split = _edge_split(text, "class")
        if split:
            diagram.parsed_roles[line_number] = "edge"
            pending_links.append((split, line_number, list(scope())))
            continue
        diagram.parsed_roles[line_number] = "statement"
        title = re.match(r"^title\s+(.+)$", text, re.I)
        if title:
            diagram.title = clean_label(title.group(1))
            continue
        if text == "}":
            if blocks:
                blocks.pop()
                continue
            _fail(f"malformed statement at line {line_number}")
        package = re.match(
            r"^(package|namespace|together)\b\s*(.*)$", text, re.I
        )
        if package:
            diagram.parsed_roles[line_number] = "declaration"
            rest = package.group(2).strip()
            opens = rest.endswith("{")
            if opens:
                rest = rest[:-1].strip()
            if package.group(1).casefold() == "together":
                if rest or not opens:
                    _fail(f"malformed statement at line {line_number}")
                blocks.append((None, line_number))
                continue
            name, label, stereotype, body = _parse_declaration_tail(
                rest, line_number
            )
            if body not in ([], ["{}"]):
                _fail(f"malformed statement at line {line_number}")
            enclosing = scope()
            parent = enclosing[-1] if enclosing else None
            node_id = f"{parent}.{name}" if parent else name
            diagram.add_node(
                node_id,
                label,
                "container",
                parent,
                True,
                stereotype=stereotype,
            )
            if opens:
                blocks.append((node_id, line_number))
            continue
        header = _parse_classifier_header(text, line_number)
        if header:
            diagram.parsed_roles[line_number] = "declaration"
            name, label, shape, stereotype, opens, members = header
            enclosing = scope()
            parent = enclosing[-1] if enclosing else None
            node_id = f"{parent}.{name}" if parent and "." not in name else name
            node = diagram.add_node(
                node_id, label, shape, parent, stereotype=stereotype
            )
            node.fields.extend(clean_label(member) for member in members)
            if node_id != name:
                diagram.bare_name(name, node_id)
            if opens:
                current = node
                current_line = line_number
            continue
        note = _parse_note(text)
        if note:
            position, rest, body = note
            of_prefix = re.match(r"^of\b\s*(.*)$", rest, re.I)
            raw_target = _strip_trailing_colors(
                of_prefix.group(1) if of_prefix else rest
            )
            if body is None or position in {"over", "across"}:
                _fail(f"malformed statement at line {line_number}")
            pending_notes.append(
                (position, raw_target, body, line_number, list(scope()))
            )
            continue
        if CLASS_REL_RE.search(text) or "--" in text or ".." in text:
            _fail(f"malformed edge at line {line_number}")
        first = text.casefold().split(maxsplit=1)[0]
        if first in UNSUPPORTED_CLASS:
            _fail(f"unsupported class construct: {first}")
        _fail(f"malformed statement at line {line_number}")
    for position, raw_target, body, line_number, note_scope in pending_notes:
        target = class_ref(
            raw_target,
            f"malformed statement at line {line_number}",
            note_scope,
        )
        cleaned = clean_label(body)
        if cleaned:
            _record_note(
                diagram,
                {
                    "position": position,
                    "participants": [target],
                    "after_message": None,
                    "message": None,
                    "line": line_number,
                },
                cleaned,
            )
    for split, line_number, link_scope in pending_links:
        add_link(split, line_number, link_scope)
    if current is not None:
        _fail(f"unterminated class body at line {current_line}")
    if blocks:
        _fail(f"unterminated package at line {blocks[-1][1]}")
    skin.check_closed()
