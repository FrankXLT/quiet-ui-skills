# SPDX-License-Identifier: MIT
"""Styling block consumption and note storage helpers for PlantUML diagrams.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from typing import Any

from .arrow_helpers import _edge_split, _split_cardinality
from .constants import SKIN_RE, TEXT_BLOCK_RE
from .models import Diagram, _fail

NOTE_HEAD_RE = re.compile(
    r"^note\s+(?P<position>left|right|over|across|top|bottom)\b(?P<rest>.*)$",
    re.I,
)


def _parse_note(text: str) -> tuple[str, str, str | None] | None:
    head = NOTE_HEAD_RE.match(text)
    if not head:
        return None
    rest = head.group("rest")
    in_quote = False
    for index, character in enumerate(rest):
        if character == '"':
            in_quote = not in_quote
        elif character == ":" and not in_quote:
            return (
                head.group("position").casefold(),
                rest[:index].strip(),
                rest[index + 1 :].strip(),
            )
    return head.group("position").casefold(), rest.strip(), None


def _record_note(diagram: Diagram, placement: dict[str, Any], body: str) -> None:
    diagram.notes.append(body)
    diagram.note_details.append({"text": body, **placement})
    if len(placement["participants"]) == 1:
        node = diagram.node_map.get(placement["participants"][0])
        if node is not None:
            node.fields.append(body)


def _is_skin(text: str) -> bool:
    if re.match(r"^(?:left|right|center)\s+(?:header|footer)\b", text, re.I):
        return True
    match = SKIN_RE.match(text)
    if not match:
        return False
    split = _edge_split(text, "sequence") or _edge_split(text, "class")
    if split:
        left, _cardinality = _split_cardinality(split[0], before_arrow=True)
        if left.strip().casefold() == match.group(0).casefold():
            return False
    return True


class _SkinBlocks:
    def __init__(self) -> None:
        self.brace_depth = 0
        self.text_end: str | None = None
        self.start_line = 0

    @property
    def open(self) -> bool:
        return self.brace_depth > 0 or self.text_end is not None

    def consume(self, diagram: Diagram, text: str, line_number: int) -> bool:
        if self.text_end is not None:
            if re.match(rf"^end\s*{self.text_end}$", text, re.I):
                self.text_end = None
            return True
        if self.brace_depth:
            if text.endswith("{"):
                self.brace_depth += 1
            elif text == "}":
                self.brace_depth -= 1
            return True
        if not _is_skin(text):
            return False
        diagram.discarded["skin"] += 1
        self.start_line = line_number
        block = TEXT_BLOCK_RE.match(text)
        if block:
            self.text_end = block.group(1).casefold()
        elif text.endswith("{"):
            self.brace_depth = 1
        return True

    def check_closed(self) -> None:
        if self.open:
            _fail(f"unterminated styling block at line {self.start_line}")
