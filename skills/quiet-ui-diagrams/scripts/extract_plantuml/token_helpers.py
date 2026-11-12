# SPDX-License-Identifier: MIT
"""Token extraction, classifier headers, and declaration tails for PlantUML.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from typing import NoReturn

from .arrow_helpers import COLOR_TOKEN_RE
from .constants import CLASSIFIER_KINDS, LIFELINE_KINDS
from .models import _fail, clean_label
from .skin_notes import (
    _SkinBlocks,
    _is_skin,
    _parse_note,
    _record_note,
)

STEREOTYPE_AT = re.compile(r"<<\s*(?:\(\s*[^)]*\)\s*)?(?P<name>[^<>]*?)\s*>>")
DECLARED_NAME_AT = re.compile(r'"(?P<quoted>[^"]*)"|(?P<bare>[^\s"<>{}#]+)')


def _quoted_or_token(text: str) -> tuple[str, str]:
    stripped = text.strip()
    if stripped[:1] in "\"'":
        quote = stripped[0]
        end = 1
        while end < len(stripped):
            if stripped[end] == quote and stripped[end - 1] != "\\":
                break
            end += 1
        else:
            return stripped, ""
        return stripped[1:end], stripped[end + 1 :].strip()
    match = re.match(r"^([A-Za-z_][\w.-]*|[\w.-]+)\s*(.*)$", stripped)
    if not match:
        return stripped, ""
    return match.group(1), match.group(2).strip()


def _strip_trailing_colors(text: str) -> str:
    tokens = text.split()
    while tokens and COLOR_TOKEN_RE.match(tokens[-1]):
        tokens.pop()
    return " ".join(tokens)


def _split_generic(text: str, line_number: int) -> tuple[str, str]:
    depth = 0
    for index, character in enumerate(text):
        if character == "<":
            depth += 1
        elif character == ">":
            depth -= 1
            if depth == 0:
                return text[: index + 1], text[index + 1 :].strip()
    _fail(f"malformed statement at line {line_number}")


def _parse_declaration_tail(
    rest: str,
    line_number: int,
    *,
    allow_order: bool = False,
    allow_generic: bool = False,
) -> tuple[str, str, str, list[str]]:
    def malformed() -> NoReturn:
        _fail(f"malformed statement at line {line_number}")

    text = rest.strip()
    name = DECLARED_NAME_AT.match(text)
    if not name or not (name.group("quoted") or name.group("bare")):
        malformed()
    quoted_display = name.group("quoted") is not None
    display = name.group("quoted") if quoted_display else name.group("bare")
    position = name.end()
    generic = ""
    generic_at = len(text) - len(text[position:].lstrip())
    if (
        allow_generic
        and not quoted_display
        and text.startswith("<", generic_at)
        and not text.startswith("<<", generic_at)
    ):
        generic, remainder = _split_generic(text[generic_at:], line_number)
        position = len(text) - len(remainder)
    node_id, label = display, display
    alias_match = re.compile(r"\s*as\s+", re.I).match(text, position)
    if alias_match:
        alias = DECLARED_NAME_AT.match(text, alias_match.end())
        if not alias or not (alias.group("quoted") or alias.group("bare")):
            malformed()
        if alias.group("quoted") is not None and not quoted_display:
            node_id, label = display, alias.group("quoted")
        else:
            node_id = (
                alias.group("quoted")
                if alias.group("quoted") is not None
                else alias.group("bare")
            )
        position = alias.end()
    stereotypes: list[str] = []
    body: list[str] = []
    while True:
        while position < len(text) and text[position].isspace():
            position += 1
        if position >= len(text):
            break
        stereo = STEREOTYPE_AT.match(text, position)
        if stereo:
            stereotypes.append(clean_label(stereo.group("name")))
            position = stereo.end()
            continue
        if text[position] == "{":
            tail = text[position:]
            if tail == "{":
                body = ["{"]
            elif (
                tail.endswith("}")
                and tail.count("{") == 1
                and tail.count("}") == 1
            ):
                inner = tail[1:-1].strip()
                body = ["{}"] + ([inner] if inner else [])
            else:
                malformed()
            break
        token = re.compile(r"[^\s{]+").match(text, position)
        if token and COLOR_TOKEN_RE.match(token.group(0)):
            position = token.end()
            continue
        order = re.compile(r"order\s+-?\d+(?=\s|\{|$)", re.I).match(
            text, position
        )
        if allow_order and order:
            position = order.end()
            continue
        malformed()
    stereotype = ", ".join(item for item in stereotypes if item)
    return node_id, (clean_label(label) or node_id) + generic, stereotype, body


def _parse_classifier_header(
    text: str, line_number: int = 0
) -> tuple[str, str, str, str, bool, list[str]] | None:
    match = re.match(
        r"^(abstract\s+class|class|interface|enum)\s+(.+)$",
        text,
        re.I,
    )
    if not match:
        return None
    kind = re.sub(r"\s+", " ", match.group(1).casefold())
    node_id, label, stereotype, body = _parse_declaration_tail(
        match.group(2).strip(), line_number, allow_generic=True
    )
    opens = body == ["{"]
    members = body[1:] if body[:1] == ["{}"] else []
    return node_id, label, CLASSIFIER_KINDS[kind], stereotype, opens, members


def _parse_participant(
    text: str, line_number: int = 0
) -> tuple[str, str, str, str] | None:
    match = re.match(
        rf"^({'|'.join(LIFELINE_KINDS)})\s+(.+)$",
        text,
        re.I,
    )
    if not match:
        return None
    kind = match.group(1).casefold()
    node_id, label, stereotype, body = _parse_declaration_tail(
        match.group(2).strip(), line_number, allow_order=True
    )
    if body:
        _fail(f"malformed statement at line {line_number}")
    return node_id, label, LIFELINE_KINDS[kind], stereotype


def _partition_unquoted(text: str, separator: str) -> tuple[str, str]:
    in_quote = False
    for index, character in enumerate(text):
        if character == '"':
            in_quote = not in_quote
        elif character == separator and not in_quote:
            return text[:index], text[index + 1 :]
    return text, ""


def _split_unquoted(text: str, separator: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_quote = False
    for character in text:
        if character == '"':
            in_quote = not in_quote
        if character == separator and not in_quote:
            parts.append("".join(current))
            current = []
            continue
        current.append(character)
    parts.append("".join(current))
    return parts
