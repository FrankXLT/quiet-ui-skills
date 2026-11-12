# SPDX-License-Identifier: MIT
"""Source file reader, markdown fence extractor, and preprocessor for Mermaid text.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re
from pathlib import Path

from .constants import (
    FRONTMATTER_MAX_LINES,
    MARKDOWN_SUFFIXES,
    MAX_SOURCE_BYTES,
    MERMAID_SUFFIXES,
    SUPPORTED_KINDS,
    UNSUPPORTED_KINDS,
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


def load_blocks(path: Path) -> list[SourceBlock]:
    suffix = path.suffix.casefold()
    if suffix not in MERMAID_SUFFIXES | MARKDOWN_SUFFIXES:
        _fail(f"{path.name}: not a Mermaid file")
    source = _read_bounded(path)
    if suffix in MERMAID_SUFFIXES:
        return [SourceBlock(0, source, 1)]

    blocks: list[SourceBlock] = []
    lines = source.splitlines()
    start: int | None = None
    fence = ""
    content: list[str] = []
    capture = False
    for line_number, line in enumerate(lines, 1):
        if start is None:
            match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
            if (
                match
                and not (match.group(1)[0] == "`" and "`" in match.group(2))
                and (
                    match.group(2).strip().casefold() == "mermaid"
                    or re.match(r"^ {0,3}[`~]", line)
                )
            ):
                start = line_number + 1
                fence = match.group(1)
                capture = match.group(2).strip().casefold() == "mermaid"
                content = []
            continue
        if re.match(
            rf"^\s*{re.escape(fence[0])}{{{len(fence)},}}\s*$", line
        ) and (capture or re.match(r"^ {0,3}[`~]", line)):
            if capture:
                blocks.append(SourceBlock(len(blocks), "\n".join(content), start))
            start = None
            fence = ""
            content = []
        elif capture:
            content.append(line)
    if start is not None and capture:
        _fail(f"{path.name}: unterminated mermaid fence starting at line {start - 1}")
    if not blocks:
        _fail(f"{path.name}: no fenced mermaid block found")
    return blocks


def _frontmatter_end(lines: list[str]) -> int:
    """Return the last line index of a leading `---` frontmatter block, or -1."""
    first = next(
        (index for index, line in enumerate(lines) if line.strip()),
        None,
    )
    if first is None or lines[first].strip() != "---":
        return -1
    limit = min(len(lines), first + FRONTMATTER_MAX_LINES + 1)
    for index in range(first + 1, limit):
        if lines[index].strip() == "---":
            return index
    return -1


def _prepared_lines(block: SourceBlock) -> tuple[list[tuple[int, str]], int]:
    """Blank out comments and config, returning the lines and config directive count."""
    prepared: list[tuple[int, str]] = []
    in_directive = False
    lines = block.text.splitlines()
    frontmatter_end = _frontmatter_end(lines)
    config_directives = 1 if frontmatter_end >= 0 else 0
    for offset, raw in enumerate(lines):
        line_number = block.source_line + offset
        stripped = raw.strip()
        if offset <= frontmatter_end:
            prepared.append((line_number, ""))
            continue
        if in_directive:
            if "}%%" in stripped:
                in_directive = False
            prepared.append((line_number, ""))
            continue
        if stripped.startswith("%%{"):
            config_directives += 1
            if "}%%" not in stripped:
                in_directive = True
            prepared.append((line_number, ""))
            continue
        if stripped.startswith("%%"):
            prepared.append((line_number, ""))
            continue
        prepared.append((line_number, raw.rstrip()))
    return prepared, config_directives


def _kind_and_direction(
    lines: list[tuple[int, str]],
) -> tuple[str, str, int]:
    for position, (line_number, raw) in enumerate(lines):
        text = raw.strip()
        if not text:
            continue
        match = re.match(r"^(flowchart|graph)\s+(TD|TB|LR|RL|BT)\b", text, re.I)
        if match:
            return "flowchart", match.group(2).upper(), position
        if re.match(r"^sequenceDiagram\b", text, re.I):
            return "sequenceDiagram", "LR", position
        if re.match(r"^stateDiagram(?:-v2)?(?![\w-])", text, re.I):
            return "stateDiagram-v2", "TD", position
        if re.match(r"^erDiagram\b", text, re.I):
            return "erDiagram", "TD", position
        token = text.split(maxsplit=1)[0]
        if token.casefold() in UNSUPPORTED_KINDS:
            _fail(
                f"unsupported diagram kind: `{token}` (supported: {SUPPORTED_KINDS})"
            )
        _fail(f"not a Mermaid file at line {line_number}")
    _fail("not a Mermaid file")
