# SPDX-License-Identifier: MIT
"""Sequence diagram parser for PlantUML messages, activations, notes, and fragments.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from typing import Any

from .arrow_helpers import (
    _activation_shortcut,
    _edge_split,
    _endpoint_code,
    _sequence_arrow,
)
from .constants import (
    MAX_STATEMENT_CHARS,
    SEQ_ARROW_RE,
    UNSUPPORTED_SEQUENCE,
)
from .loader import _statement_too_long
from .models import Diagram, _fail, clean_label
from .skin_notes import _SkinBlocks, _parse_note, _record_note
from .token_helpers import (
    _parse_participant,
    _partition_unquoted,
    _split_unquoted,
    _strip_trailing_colors,
)


def _parse_sequence(diagram: Diagram, lines: list[tuple[int, str]]) -> None:
    fragment_stack: list[dict[str, Any]] = []
    open_note: dict[str, Any] | None = None
    note_lines: list[str] = []
    note_start = 0
    skin = _SkinBlocks()

    def next_message() -> int:
        return len(diagram.edges) + 1

    def close_region(entry: dict[str, Any]) -> None:
        region = entry["regions"][-1]
        region["last_message"] = len(diagram.edges)
        if region["last_message"] < region["first_message"]:
            region["first_message"] = region["last_message"] = None

    def close_note() -> None:
        nonlocal open_note, note_lines
        body = clean_label("\n".join(note_lines))
        if body and open_note is not None:
            _record_note(diagram, open_note, body)
        open_note = None
        note_lines = []

    def note_participants(raw: str, line_number: int) -> list[str]:
        text = _strip_trailing_colors(raw)
        if not text:
            return []
        resolved_ids: list[str] = []
        for token in _split_unquoted(text, ","):
            node_id = lifeline(
                token, f"malformed statement at line {line_number}"
            )
            if node_id not in resolved_ids:
                resolved_ids.append(node_id)
        return resolved_ids

    def add_message(
        split: tuple[str, re.Match[str], str], line_number: int
    ) -> None:
        left, arrow, right = split
        right, message = _partition_unquoted(right, ":")
        right, actions = _activation_shortcut(right)
        if left in {"[", "?"} or right in {"]", "?"}:
            _fail(
                f"unsupported sequence construct: boundary message at line {line_number}"
            )
        edge_error = f"malformed edge at line {line_number}"
        source = lifeline(left, edge_error, allow_as=True)
        target = lifeline(right, edge_error, allow_as=True)
        style, arrowhead, reverse, bidirectional = _sequence_arrow(arrow)
        if reverse:
            source, target = target, source
        diagram.add_edge(
            source,
            target,
            clean_label(message),
            style,
            arrowhead,
            bidirectional=bidirectional,
        )
        for action in actions:
            diagram.add_activation(
                source if action == "deactivate" else target, action
            )

    def lifeline(token: str, error: str, *, allow_as: bool = False) -> str:
        parsed = _endpoint_code(token, allow_as=allow_as)
        if parsed is None:
            _fail(error)
        code, display = parsed
        if code not in diagram.node_map:
            diagram.add_node(code, clean_label(display) or code, "lifeline")
        return code

    for line_number, raw in lines:
        text = raw.strip()
        if not text:
            continue
        if len(text) > MAX_STATEMENT_CHARS:
            _statement_too_long(line_number)
        lowered = text.casefold()
        if open_note is not None:
            if lowered in {"end note", "endnote"}:
                close_note()
                continue
            note_lines.append(text)
            continue
        if skin.consume(diagram, text, line_number):
            continue
        split = _edge_split(text, "sequence")
        if split:
            diagram.parsed_roles[line_number] = "edge"
            add_message(split, line_number)
            continue
        diagram.parsed_roles[line_number] = "statement"
        title = re.match(r"^title\s+(.+)$", text, re.I)
        if title:
            diagram.title = clean_label(title.group(1))
            continue
        participant = _parse_participant(text, line_number)
        if participant:
            diagram.parsed_roles[line_number] = "declaration"
            node_id, label, shape, stereotype = participant
            diagram.add_node(node_id, label, shape, stereotype=stereotype)
            continue
        divider = re.match(r"^==+\s*(.*?)\s*==+$", text)
        if divider:
            diagram.fragments.append(
                {
                    "kind": "divider",
                    "label": clean_label(divider.group(1)),
                    "line": line_number,
                    "depth": len(fragment_stack),
                    "after_message": len(diagram.edges),
                    "regions": [],
                }
            )
            continue
        fragment = re.match(r"^(alt|opt|loop)\b\s*(.*)$", text, re.I)
        if fragment:
            label = clean_label(fragment.group(2))
            entry = {
                "kind": fragment.group(1).casefold(),
                "label": label,
                "line": line_number,
                "depth": len(fragment_stack),
                "first_message": next_message(),
                "last_message": None,
                "regions": [
                    {
                        "label": label,
                        "line": line_number,
                        "first_message": next_message(),
                        "last_message": None,
                    }
                ],
            }
            diagram.fragments.append(entry)
            fragment_stack.append(entry)
            continue
        region = re.match(r"^else\b\s*(.*)$", text, re.I)
        if region:
            if not fragment_stack:
                _fail(f"malformed statement at line {line_number}")
            close_region(fragment_stack[-1])
            fragment_stack[-1]["regions"].append(
                {
                    "label": clean_label(region.group(1)),
                    "line": line_number,
                    "first_message": next_message(),
                    "last_message": None,
                }
            )
            continue
        if lowered == "end":
            if fragment_stack:
                entry = fragment_stack.pop()
                close_region(entry)
                entry["last_message"] = len(diagram.edges)
                entry["end_line"] = line_number
                if entry["last_message"] < entry["first_message"]:
                    entry["first_message"] = entry["last_message"] = None
                continue
            _fail(f"malformed statement at line {line_number}")
        first = lowered.split(maxsplit=1)[0]
        if first in UNSUPPORTED_SEQUENCE:
            _fail(f"unsupported sequence construct: {first}")
        activate = re.match(
            r"^(activate|deactivate|destroy)\s+(.+)$", text, re.I
        )
        if activate:
            action = activate.group(1).casefold()
            target = lifeline(
                _strip_trailing_colors(activate.group(2)),
                f"malformed statement at line {line_number}",
            )
            diagram.add_activation(target, action)
            continue
        note = _parse_note(text)
        if note:
            position, rest, note_body = note
            of_prefix = re.match(r"^of\b\s*(.*)$", rest, re.I)
            if of_prefix:
                rest = of_prefix.group(1)
            participants = note_participants(rest, line_number)
            message: int | None = None
            if not participants:
                if position in {"left", "right"} and not of_prefix:
                    if not diagram.edges:
                        _fail(f"malformed statement at line {line_number}")
                    message = len(diagram.edges)
                elif position != "across":
                    _fail(f"malformed statement at line {line_number}")
            elif position == "across":
                _fail(f"malformed statement at line {line_number}")
            open_note = {
                "position": position,
                "participants": participants,
                "after_message": len(diagram.edges),
                "message": message,
                "line": line_number,
            }
            if note_body is not None:
                note_lines = [note_body]
                close_note()
            else:
                note_lines = []
                note_start = line_number
            continue
        if lowered.startswith("note "):
            _fail(f"malformed statement at line {line_number}")
        if SEQ_ARROW_RE.search(text):
            _fail(f"malformed edge at line {line_number}")
        _fail(f"malformed statement at line {line_number}")
    if open_note is not None:
        _fail(f"unterminated note at line {note_start}")
    skin.check_closed()
    if fragment_stack:
        _fail(f"unterminated fragment at line {fragment_stack[-1]['line']}")
