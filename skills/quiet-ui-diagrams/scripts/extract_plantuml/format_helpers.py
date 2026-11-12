# SPDX-License-Identifier: MIT
"""Markdown escaping and summary helpers for PlantUML digests.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import html
import re
from typing import Any

from .analyzer import parse_block
from .models import Diagram, ExtractError, SourceBlock


def _escape_markdown(text: str) -> str:
    encoded = html.escape(text, quote=False)
    return re.sub(r"([\\`*{}\[\]()#+\-.!_|>])", r"\\\1", encoded)


def _escape_table(text: str) -> str:
    return _escape_markdown(text.replace("\n", " ⏎ "))


def _message_span(first: int | None, last: int | None) -> str:
    if first is None or last is None:
        return "no messages"
    return f"msg {first}" if first == last else f"msgs {first}-{last}"


def _note_summary(item: dict[str, Any]) -> str:
    text = _escape_markdown(item["text"].replace("\n", " ⏎ "))
    position = item["position"]
    if item["message"] is not None:
        return f"{position} of msg {item['message']}: {text}"
    where = position
    if item["participants"]:
        joiner = " " if position in {"over", "across"} else " of "
        where += joiner + ", ".join(
            _escape_markdown(name) for name in item["participants"]
        )
    if item["after_message"] is not None:
        where += f" @{item['after_message']}"
    return f"{where}: {text}"


def _fragment_summary(item: dict[str, Any]) -> str:
    label = _escape_markdown(item["label"] or "unlabeled")
    if item["kind"] == "divider":
        return f"divider({label}) after msg {item['after_message']}"
    indent = f"depth {item['depth']}, " if item["depth"] else ""
    regions = item["regions"]
    parts = [
        f"{item['kind']}({label}) {indent}"
        f"{_message_span(regions[0]['first_message'], regions[0]['last_message'])}"
    ]
    for region in regions[1:]:
        parts.append(
            f"else({_escape_markdown(region['label'] or 'unlabeled')}) "
            f"{_message_span(region['first_message'], region['last_message'])}"
        )
    return "; ".join(parts)


def _block_summary(block: SourceBlock, selected: list[Diagram]) -> str:
    diagram = next((item for item in selected if item.index == block.index), None)
    if diagram is None:
        try:
            diagram = parse_block(block)
        except ExtractError as error:
            return f"[{block.index}] unparsed: {_escape_markdown(str(error))}"
    return f"[{diagram.index}] {diagram.kind} ({len(diagram.nodes)}n/{len(diagram.edges)}e)"
