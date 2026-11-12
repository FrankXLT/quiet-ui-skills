# SPDX-License-Identifier: MIT
"""Source file reader, region splitter, and comment blanker for PlantUML.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NoReturn

from .constants import (
    DEFINE_INCLUDE_RE,
    END_RE,
    FENCE_OPEN_RE,
    INCLUDE_RE,
    MARKDOWN_SUFFIXES,
    MAX_SOURCE_BYTES,
    MAX_STATEMENT_CHARS,
    PLANTUML_SUFFIXES,
    START_RE,
    THEME_URL_RE,
)
from .models import SourceBlock, _fail


def _read_bounded(path: Path) -> str:
    try:
        with path.open("rb") as source:
            data = source.read(MAX_SOURCE_BYTES + 1)
    except OSError as error:
        _fail(f"{path}: {error}")
    if len(data) > MAX_SOURCE_BYTES:
        _fail(f"source exceeds the {MAX_SOURCE_BYTES // (1024 * 1024)} MiB limit")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        _fail(f"{path.name}: source is not valid UTF-8 text")


def _split_uml_regions(
    text: str, base_line: int
) -> list[tuple[int, str, str, str | None]]:
    """Return (start_line, body, start_kind, error) for each @start/@end region."""
    regions: list[tuple[int, str, str, str | None]] = []
    lines = text.splitlines()
    start: int | None = None
    kind = "uml"
    body: list[str] = []
    error: str | None = None
    comment_start: int | None = None
    for offset, raw in enumerate(lines):
        stripped = raw.strip()
        opened = START_RE.match(stripped)
        closed = END_RE.match(stripped)
        line_number = base_line + offset
        if start is None:
            if opened:
                start = line_number + 1
                kind = opened.group(1).casefold()
                body = []
                error = None
            continue
        if comment_start is not None:
            if not _strip_block_comments(raw, True)[1]:
                comment_start = None
            body.append(raw)
            continue
        if not stripped.startswith("'") and _strip_block_comments(raw, False)[1]:
            comment_start = base_line + offset
            body.append(raw)
            continue
        if closed:
            closing = closed.group(1).casefold()
            if closing != kind and error is None:
                error = (
                    f"`@end{closed.group(1)}` at line {line_number} does not close "
                    f"`@start{kind}` at line {start - 1}"
                )
            regions.append((start, "\n".join(body), kind, error))
            start = None
            body = []
            continue
        if opened and error is None:
            error = f"nested @start{opened.group(1).casefold()} at line {line_number}"
        body.append(raw)
    if start is not None:
        if comment_start is not None:
            error = f"unterminated block comment at line {comment_start}"
        elif error is None:
            error = f"missing @end{kind} for @start{kind} at line {start - 1}"
        regions.append((start, "\n".join(body), kind, error))
    return regions


def load_blocks(path: Path) -> list[SourceBlock]:
    suffix = path.suffix.casefold()
    if suffix not in PLANTUML_SUFFIXES | MARKDOWN_SUFFIXES:
        _fail(f"{path.name}: not a PlantUML file")
    source = _read_bounded(path)
    collected: list[SourceBlock] = []

    def add(
        start_line: int, text: str, start_kind: str, error: str | None = None
    ) -> None:
        collected.append(
            SourceBlock(len(collected), text, start_line, start_kind, error)
        )

    if suffix in PLANTUML_SUFFIXES:
        regions = _split_uml_regions(source, 1)
        if not regions:
            _fail(f"{path.name}: no @startuml block found")
        for start_line, text, kind, error in regions:
            add(start_line, text, kind, error)
        return collected

    lines = source.splitlines()
    start: int | None = None
    fence = ""
    capture = False
    content: list[str] = []
    for line_number, line in enumerate(lines, 1):
        if start is None:
            match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                is_plantuml = bool(FENCE_OPEN_RE.match(line))
                if is_plantuml or re.match(r"^ {0,3}[`~]", line):
                    start = line_number + 1
                    fence = match.group(1)
                    capture = is_plantuml
                    content = []
            continue
        if re.match(rf"^\s*{re.escape(fence[0])}{{{len(fence)},}}\s*$", line) and (
            capture or re.match(r"^ {0,3}[`~]", line)
        ):
            if capture:
                block_text = "\n".join(content)
                regions = _split_uml_regions(block_text, start)
                if regions:
                    for start_line, text, kind, error in regions:
                        add(start_line, text, kind, error)
                else:
                    add(start, block_text, "uml")
            start = None
            fence = ""
            content = []
        elif capture:
            content.append(line)
    if start is not None and capture:
        add(
            start,
            "\n".join(content),
            "uml",
            f"unterminated plantuml fence starting at line {start - 1}",
        )
    if not collected:
        _fail(f"{path.name}: no fenced plantuml block found")
    return collected


def _strip_block_comments(raw: str, in_block: bool) -> tuple[str, bool]:
    visible: list[str] = []
    index = 0
    while index <= len(raw):
        if in_block:
            close = raw.find("'/", index)
            if close == -1:
                break
            index = close + 2
            in_block = False
            continue
        opening = raw.find("/'", index)
        if opening == -1:
            visible.append(raw[index:])
            break
        visible.append(raw[index:opening])
        index = opening + 2
        in_block = True
    return "".join(visible), in_block


def _blank_comments(lines: list[str]) -> list[str]:
    prepared: list[str] = []
    in_block = False
    for raw in lines:
        if not in_block and raw.strip().startswith("'"):
            prepared.append("")
            continue
        visible, in_block = _strip_block_comments(raw, in_block)
        prepared.append(visible.rstrip())
    if in_block:
        _fail("unterminated block comment")
    return prepared


def _refuse_includes(lines: list[tuple[int, str]]) -> None:
    for _line_number, raw in lines:
        text = raw.strip()
        if not text:
            continue
        if (
            INCLUDE_RE.match(text)
            or DEFINE_INCLUDE_RE.match(text)
            or THEME_URL_RE.match(text)
        ):
            _fail("include not inlined")


def _statement_too_long(line_number: int) -> NoReturn:
    _fail(
        f"statement at line {line_number} exceeds the "
        f"{MAX_STATEMENT_CHARS}-character limit"
    )
