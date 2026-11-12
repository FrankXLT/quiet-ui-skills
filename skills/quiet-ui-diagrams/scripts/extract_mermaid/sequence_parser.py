# SPDX-License-Identifier: MIT
"""Sequence diagram parser for participants, messages, activations, and fragments.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from typing import Any

from .constants import MAX_AUTONUMBER_DIGITS
from .flow_parser import _discard_nonsemantic
from .models import Diagram, _fail, clean_label


def _parse_sequence(
    diagram: Diagram, lines: list[tuple[int, str]], header_position: int
) -> None:
    fragment_stack: list[dict[str, Any] | None] = []
    semantic_depth = 0
    participant_re = re.compile(
        r"^(?:create\s+)?(participant|actor)\s+"
        r"(?:\"([^\"]+)\"|'([^']+)'|([\w.:-]+))"
        r"(?:\s+as\s+(.+))?$",
        re.I,
    )
    message_re = re.compile(
        r"^([\w.:-]+?(?: [\w.:-]+)*?)(?:\(\))?\s*"
        r"(<<--?>>|--?>>|--?>|--?\)|--?x)"
        r"\s*[+-]?\s*(?:\(\))?([\w.:-]+?(?: [\w.:-]+)*?)\s*:\s*(.*)$"
    )
    for line_number, raw in lines[header_position + 1 :]:
        text = raw.strip()
        if not text:
            continue
        lowered = text.casefold()
        if _discard_nonsemantic(diagram, text):
            continue
        participant = participant_re.match(text)
        if participant:
            kind = participant.group(1).casefold()
            quoted = participant.group(2) or participant.group(3)
            bare = participant.group(4)
            alias = participant.group(5)
            if quoted is not None:
                node_id = alias or quoted
                label = quoted
            else:
                node_id = bare
                label = alias or bare
            diagram.add_node(
                node_id,
                clean_label(label),
                "actor" if kind == "actor" else "lifeline",
            )
            continue
        if (
            re.match(r"^rect\s+", text, re.I)
            and message_re.match(text) is None
            and re.match(
                r"^rect\s+(?:<<--?>>|--?>>|--?>|--?\)|--?x)", text, re.I
            )
            is None
        ):
            fragment_stack.append(None)
            continue
        fragment = re.match(
            r"^(alt|opt|loop|par|critical|break)\b\s*(.*)$", text, re.I
        )
        if fragment:
            entry = {
                "kind": fragment.group(1).casefold(),
                "label": clean_label(fragment.group(2)),
                "line": line_number,
                "depth": semantic_depth,
                "regions": [],
            }
            diagram.fragments.append(entry)
            fragment_stack.append(entry)
            semantic_depth += 1
            continue
        region = re.match(r"^(else|and|option)\b\s*(.*)$", text, re.I)
        if region and fragment_stack and fragment_stack[-1] is not None:
            fragment_stack[-1]["regions"].append(clean_label(region.group(2)))
            continue
        if lowered == "end":
            if fragment_stack and fragment_stack.pop() is not None:
                semantic_depth -= 1
            continue
        if lowered.startswith(("activate ", "deactivate ", "+", "-")):
            continue
        numbering = re.match(
            r"^autonumber(?:\s+(off)|\s+(\d+)(?:\s+(\d+))?)?$", text, re.I
        )
        if numbering:
            off, start, step = numbering.groups()
            entry = {"line": line_number, "off": bool(off)}
            if not off:
                if any(
                    len(value or "") > MAX_AUTONUMBER_DIGITS
                    for value in (start, step)
                ):
                    _fail(
                        f"autonumber value exceeds {MAX_AUTONUMBER_DIGITS} digits "
                        f"at line {line_number}"
                    )
                entry.update(start=int(start or 1), step=int(step or 1))
            diagram.autonumber.append(entry)
            continue
        if lowered.startswith("note "):
            _, separator, note = text.partition(":")
            diagram.notes.append(clean_label(note if separator else text[5:]))
            continue
        message = message_re.match(text)
        if message:
            source, token, target, label = message.groups()
            for endpoint in (source, target):
                if endpoint not in diagram.node_map:
                    diagram.add_node(endpoint, endpoint, "lifeline")
            if token.endswith("x"):
                arrowhead = "cross"
            elif token.endswith(")"):
                arrowhead = "async"
            elif token.endswith(">>"):
                arrowhead = "arrow"
            else:
                arrowhead = "none"
            diagram.add_edge(
                source,
                target,
                clean_label(label),
                "dashed"
                if token.startswith("--") or token.startswith("<<--")
                else "solid",
                arrowhead,
                bidirectional=token.startswith("<<"),
                undirected=arrowhead == "none",
            )
            continue
        if re.search(r"<<--?>>|--?>>|--?>|--?\)|--?x", text):
            _fail(f"malformed edge at line {line_number}")
