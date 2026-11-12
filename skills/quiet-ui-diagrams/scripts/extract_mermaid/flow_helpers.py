# SPDX-License-Identifier: MIT
"""Statement parsing, shape classification, and expression masks for Mermaid flowcharts.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from typing import NoReturn

from .constants import (
    EXPANDED_SHAPE_FAMILIES,
    MAX_STATEMENT_CHARS,
    SHAPE_FOR_DELIMITERS,
)
from .models import _fail, clean_label


def _top_level_mask(text: str) -> str:
    """Keep top-level syntax positions and blank quoted/bracketed content."""
    output = list(text)
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    pairs = {"]": "[", ")": "(", "}": "{"}
    for index, character in enumerate(text):
        if quote is not None:
            output[index] = " "
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in "\"'`":
            quote = character
            output[index] = " "
            continue
        if character in "[({":
            stack.append(character)
            output[index] = " "
            continue
        if character in "])}":
            if stack and stack[-1] == pairs[character]:
                stack.pop()
            output[index] = " "
            continue
        if stack:
            output[index] = " "
    return "".join(output)


def _split_top_level(text: str, delimiter: str) -> list[str]:
    mask = _top_level_mask(text)
    parts: list[str] = []
    start = 0
    for index, character in enumerate(mask):
        if character == delimiter:
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return parts


def _statement_complete(text: str) -> bool:
    """Return whether quotes and node delimiters close within a statement."""
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    pairs = {"]": "[", ")": "(", "}": "{"}
    for character in text:
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in "\"'`":
            quote = character
        elif character in "[({":
            stack.append(character)
        elif character in "])}":
            if stack and stack[-1] == pairs[character]:
                stack.pop()
    return quote is None and not stack


def _statement_too_long(line_number: int) -> NoReturn:
    _fail(
        f"statement at line {line_number} exceeds the "
        f"{MAX_STATEMENT_CHARS}-character limit"
    )


def _logical_statements(
    lines: list[tuple[int, str]],
) -> list[tuple[int, str]]:
    """Join multiline Mermaid strings before parsing semicolon statements."""
    logical: list[tuple[int, str]] = []
    pending: list[str] = []
    start_line = 0
    for line_number, raw in lines:
        if not pending and not raw.strip():
            continue
        if not pending:
            start_line = line_number
        pending.append(raw)
        combined = "\n".join(pending)
        statements = _split_top_level(combined, ";")
        complete = _statement_complete(combined)
        for statement in statements if complete else statements[:-1]:
            if len(statement) > MAX_STATEMENT_CHARS:
                _statement_too_long(start_line)
            logical.append((start_line, statement))
        if complete:
            pending = []
            continue
        if len(statements[-1]) > MAX_STATEMENT_CHARS:
            _statement_too_long(start_line)
        pending = [statements[-1]]
    if pending:
        _fail(f"unterminated statement at line {start_line}")
    return logical


def classify_shape(expression: str) -> str:
    """Return the normalized Mermaid shape family for a node suffix."""
    for opening, closing, shape in SHAPE_FOR_DELIMITERS:
        if expression.startswith(opening) and expression.endswith(closing):
            return shape
    return "rect"


def _strip_class_suffix(text: str) -> str:
    """Drop Mermaid's `:::class` attachment; source styling is discarded."""
    mask = _top_level_mask(text)
    index = mask.find(":::")
    if index == -1:
        return text
    end = index + 3
    while end < len(text) and (text[end].isalnum() or text[end] in "_-"):
        end += 1
    return (text[:index] + text[end:]).strip()


def _parse_expanded_attributes(text: str) -> tuple[str, str] | None:
    """Normalize Mermaid v11.3+ @{ ... } node attributes."""
    if not text.startswith("@{") or not text.endswith("}"):
        return None
    values: dict[str, str] = {}
    for raw_attribute in _split_top_level(text[2:-1], ","):
        key, separator, raw_value = raw_attribute.partition(":")
        if not separator:
            continue
        key = key.strip().casefold()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            continue
        values[key] = clean_label(raw_value)
    shape_name = values.get("shape", "").casefold()
    if not shape_name:
        if "img" in values:
            shape_name = "image"
        elif "icon" in values:
            shape_name = "icon"
        elif "shape" not in values:
            return values.get("label", ""), ""
        else:
            shape_name = "rect"
    if not re.fullmatch(r"[a-z][a-z0-9-]*", shape_name):
        shape_name = "rect"
    shape = EXPANDED_SHAPE_FAMILIES.get(shape_name, shape_name)
    return values.get("label", ""), shape


def _parse_node_expression(expression: str) -> tuple[str, str, str] | None:
    text = _strip_class_suffix(expression.strip().rstrip(";").strip())
    if not text:
        return None
    match = re.match(r"^([\w.:-]+)", text, re.UNICODE)
    if match is None:
        return None
    node_id = match.group(1)
    rest = text[match.end() :].strip()
    if not rest:
        return node_id, node_id, ""
    expanded = _parse_expanded_attributes(rest)
    if expanded is not None:
        label, shape = expanded
        return node_id, label or node_id, shape
    for opening, closing, _shape in SHAPE_FOR_DELIMITERS:
        if rest.startswith(opening) and rest.endswith(closing):
            label = rest[len(opening) : len(rest) - len(closing)]
            return node_id, clean_label(label), classify_shape(rest)
    return None
