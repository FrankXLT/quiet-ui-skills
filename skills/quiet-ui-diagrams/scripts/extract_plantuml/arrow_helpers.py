# SPDX-License-Identifier: MIT
"""Arrow matching, relationship lexing, and endpoint token extraction for PlantUML.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

from .constants import CLASS_ARROW_AT, CLASS_HEADS, SEQ_ARROW_AT
from .models import _fail

COLOR_TOKEN_RE = re.compile(r"^#{1,2}(?:\[[^\]]*\])?[\w:;.#/\\|-]*$")
_BARE_NAME = r'[^\s"\'<>:\[\]{}|,#][^\s"\'<>:\[\]{}|,]*'
ENDPOINT_RE = re.compile(rf'^(?:"[^"]+"|{_BARE_NAME})$')
INLINE_DECLARATION_RE = re.compile(
    rf'^(?:"(?P<long>[^"]+)"\s*as\s+(?P<long_code>{_BARE_NAME})'
    rf'|(?P<code>{_BARE_NAME})\s+as\s*"(?P<code_long>[^"]+)")$',
    re.I,
)


def _endpoint_code(token: str, *, allow_as: bool = False) -> tuple[str, str] | None:
    """Return (code, display) for a reference, or None when it is not one name."""
    text = token.strip()
    if allow_as:
        inline = INLINE_DECLARATION_RE.match(text)
        if inline:
            if inline.group("long") is not None:
                return inline.group("long_code"), inline.group("long")
            return inline.group("code"), inline.group("code_long")
    if not ENDPOINT_RE.match(text):
        return None
    if text.startswith('"'):
        return text[1:-1], text[1:-1]
    return text, text


def _scan_arrow(text: str, kind: str) -> tuple[str, re.Match[str], str] | None:
    """Split text around its first whole arrow outside double quotes."""
    pattern = SEQ_ARROW_AT if kind == "sequence" else CLASS_ARROW_AT
    in_quote = False
    for index, character in enumerate(text):
        if character == '"':
            in_quote = not in_quote
            continue
        if in_quote or character not in "<-.*o#x}+^":
            continue
        match = pattern.match(text, index)
        if not match:
            continue
        left_head, right_head = match.group("left"), match.group("right")
        before = text[index - 1] if index else " "
        if kind == "sequence":
            if match.group("lead") and not (before.isspace() or before == '"'):
                continue
            if not (left_head or right_head):
                continue
        else:
            if left_head in {"o", "x"} and not (before.isspace() or before == '"'):
                continue
            body = len(match.group("body1")) + len(match.group("body2"))
            if not (left_head or right_head) and (
                body < 2 or not (before.isspace() or before == '"')
            ):
                continue
        return text[:index].strip(), match, text[match.end() :].strip()
    return None


def _is_structural_link(match: re.Match[str]) -> bool:
    """True for an inheritance, composition, or aggregation head."""
    heads = {match.group("left") or "", match.group("right") or ""}
    body = len(match.group("body1")) + len(match.group("body2"))
    if "o" in heads and match.group("char") == "-" and body < 2:
        heads = heads - {"o", "<", ">"}
    return bool(heads & {"<|", "|>", "^", "*", "o"})


def _split_cardinality(side: str, *, before_arrow: bool) -> tuple[str, str]:
    """Split a class name from the quoted cardinality written next to the arrow."""
    text = side.strip()
    if before_arrow:
        trailing = re.match(r'^(.+?)\s+"([^"]*)"$', text)
        if trailing:
            return trailing.group(1).strip(), trailing.group(2)
        return text, ""
    leading = re.match(r'^"([^"]*)"\s+(.+)$', text)
    if leading:
        return leading.group(2).strip(), leading.group(1)
    return text, ""


def _edge_split(text: str, kind: str) -> tuple[str, re.Match[str], str] | None:
    """The one edge classifier, shared by kind detection and both parsers."""
    split = _scan_arrow(text, kind)
    if not split:
        return None
    left = split[0]
    if kind == "sequence":
        if left in {"[", "?"}:
            return split
        return split if _endpoint_code(left, allow_as=True) else None
    left_name, _cardinality = _split_cardinality(left, before_arrow=True)
    return split if _endpoint_code(left_name) else None


def _class_relationship(
    match: re.Match[str], line_number: int
) -> tuple[str, str, bool, bool, bool, bool, str]:
    """Return (arrowhead, style, reverse, bidirectional, undirected, hidden, navigable)."""
    style_hint = (match.group("style") or "").casefold()
    dashed = match.group("char") == "." or "dashed" in style_hint or "dotted" in style_hint
    style = "dashed" if dashed else "solid"
    hidden = "hidden" in style_hint
    left = CLASS_HEADS.get(
        match.group("left") or "", "" if not match.group("left") else None
    )
    right = CLASS_HEADS.get(
        match.group("right") or "", "" if not match.group("right") else None
    )
    if left is None or right is None:
        _fail(
            f"unsupported relationship arrow `{match.group(0)}` at line {line_number}"
        )
    if not left and not right:
        return "association", style, False, False, True, hidden, ""
    if left == "plain" and right == "plain":
        return "association", style, False, True, False, hidden, ""
    if left and right:
        if left in {"composition", "aggregation"} and right == "plain":
            return left, style, False, False, False, hidden, "target"
        if right in {"composition", "aggregation"} and left == "plain":
            return right, style, True, False, False, hidden, "source"
        _fail(
            f"unsupported relationship arrow `{match.group(0)}` at line {line_number}"
        )
    head = left or right
    if head == "plain":
        return "association", style, bool(left), False, False, hidden, ""
    if head == "inheritance":
        return "inheritance", style, bool(left), False, False, hidden, ""
    return head, style, bool(right), False, False, hidden, ""


def _sequence_arrow(match: re.Match[str]) -> tuple[str, str, bool, bool]:
    """Return (style, arrowhead, reverse, bidirectional) for a sequence arrow."""
    left, right = match.group("left"), match.group("right")
    style_hint = (match.group("style") or "").casefold()
    dashes = len(match.group("body1")) + len(match.group("body2"))
    dashed = dashes >= 2 or "dashed" in style_hint or "dotted" in style_hint
    decoration = match.group("decoration") or match.group("lead")
    if decoration == "x":
        arrowhead = "lost"
    elif decoration == "o":
        arrowhead = "circle"
    elif left == "<<" or right == ">>":
        arrowhead = "async"
    else:
        arrowhead = "arrow"
    return (
        ("dashed" if dashed else "solid"),
        arrowhead,
        bool(left and not right),
        bool(left and right),
    )


ACTIVATION_SHORTCUT_RE = re.compile(
    r"^(?P<name>.+?)\s*(?P<mark>\+\+--|--\+\+|\+\+|--|\*\*|!!)?\s*"
    r"(?P<color>#{1,2}[\w:;.#-]*)?$"
)
SHORTCUT_ACTIONS = {
    "++": ("activate",),
    "--": ("deactivate",),
    "--++": ("deactivate", "activate"),
    "++--": ("activate", "deactivate"),
    "**": ("create",),
    "!!": ("destroy",),
}


def _activation_shortcut(text: str) -> tuple[str, tuple[str, ...]]:
    """Split receiver name and shortcut actions."""
    match = ACTIVATION_SHORTCUT_RE.match(text.strip())
    if not match:
        return text.strip(), ()
    return match.group("name").strip(), SHORTCUT_ACTIONS.get(
        match.group("mark") or "", ()
    )
