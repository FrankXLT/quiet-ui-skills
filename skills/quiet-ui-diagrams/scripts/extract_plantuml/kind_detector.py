# SPDX-License-Identifier: MIT
"""Diagram kind detection (class vs sequence) for PlantUML source text.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

from .arrow_helpers import _edge_split, _is_structural_link, _scan_arrow
from .constants import CLASS_DECL_RE, SEQ_DECL_RE, SUPPORTED_KINDS
from .models import Diagram, _fail
from .skin_notes import _SkinBlocks


def _unsupported_kind_message(token: str) -> str:
    return f"unsupported diagram kind: `{token}` (supported: {SUPPORTED_KINDS})"


def _unsupported_body_kind(text: str) -> str | None:
    """Return a named unsupported kind when the body is clearly not sequence/class."""
    if text.startswith("[*]"):
        return "state"
    if re.match(r"^state\b", text, re.I) and not _scan_arrow(text, "sequence"):
        return "state"
    match = re.match(r"^(component|usecase)\b", text, re.I)
    if match and not _scan_arrow(text, "sequence"):
        return match.group(1).casefold()
    return None


def _note_has_inline_body(text: str) -> bool:
    """True for a one-line note (note over A : text), False for a block opener."""
    in_quote: str | None = None
    for character in text:
        if in_quote:
            if character == in_quote:
                in_quote = None
        elif character == '"':
            in_quote = character
        elif character == ":":
            return True
    return False


def _statement_lines(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Return statement text, skipping note, legend, styling, and class bodies."""
    statements: list[tuple[int, str]] = []
    skin = _SkinBlocks()
    scratch = Diagram(0, "", 0)
    in_note = False
    in_class_body = False
    for _line_number, raw in lines:
        text = raw.strip()
        if not text:
            continue
        if in_note:
            if text.casefold() in {"end note", "endnote"}:
                in_note = False
            continue
        if in_class_body:
            if text == "}":
                in_class_body = False
            continue
        if skin.consume(scratch, text, _line_number):
            continue
        statements.append((_line_number, text))
        if _edge_split(text, "sequence") or _edge_split(text, "class"):
            continue
        if re.match(r"^note\b", text, re.I) and not _note_has_inline_body(text):
            in_note = True
        elif CLASS_DECL_RE.match(text) and text.endswith("{"):
            in_class_body = True
    return statements


def _detect_kind(lines: list[tuple[int, str]]) -> tuple[str, dict[int, str]]:
    """Return the diagram kind and the role of each statement line for it."""
    has_class = False
    has_seq_decl = False
    has_class_rel = False
    has_seq_arrow = False
    unsupported: str | None = None
    readings: list[tuple[int, bool, bool, bool, bool]] = []
    for line_number, text in _statement_lines(lines):
        seq_split = _edge_split(text, "sequence")
        class_split = _edge_split(text, "class")
        is_class_decl = is_seq_decl = False
        if seq_split or class_split:
            if class_split and _is_structural_link(class_split[1]):
                has_class_rel = True
            if seq_split:
                has_seq_arrow = True
        else:
            is_class_decl = bool(CLASS_DECL_RE.match(text))
            is_seq_decl = bool(SEQ_DECL_RE.match(text))
            has_class = has_class or is_class_decl
            has_seq_decl = has_seq_decl or is_seq_decl
            hint = _unsupported_body_kind(text)
            if hint and unsupported is None:
                unsupported = hint
        readings.append(
            (
                line_number,
                bool(seq_split),
                bool(class_split),
                is_seq_decl,
                is_class_decl,
            )
        )
    if has_class and has_seq_decl:
        _fail("mixed or unknown kind")
    if unsupported and not has_class and not has_seq_decl:
        _fail(_unsupported_kind_message(unsupported))
    if has_class or (has_class_rel and not has_seq_decl):
        kind = "class"
    elif has_seq_decl or has_seq_arrow:
        kind = "sequence"
    elif unsupported:
        _fail(_unsupported_kind_message(unsupported))
    else:
        _fail("mixed or unknown kind")
    roles: dict[int, str] = {}
    for line_number, seq_sp, class_sp, is_seq_d, is_class_d in readings:
        if kind == "class":
            roles[line_number] = (
                "edge"
                if class_sp
                else "declaration"
                if is_class_d
                else "statement"
            )
        else:
            roles[line_number] = (
                "edge"
                if seq_sp
                else "declaration"
                if is_seq_d
                else "statement"
            )
    return kind, roles
