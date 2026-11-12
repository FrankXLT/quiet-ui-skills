# SPDX-License-Identifier: MIT
"""CSS rule analysis, selector decomposition, and network reference checks.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable

from .models import (
    CSS_ATTRIBUTE_RE,
    CSS_CLASS_RE,
    CSS_COMBINATOR_RE,
    CSS_COMMENT_RE,
    CSS_ESCAPE_RE,
    CSS_ID_RE,
    CSS_IMAGE_SET_RE,
    CSS_IMPORT_RE,
    CSS_KEYFRAMES_RE,
    CSS_PARENS_RE,
    CSS_REMOTE_RE,
    CSS_RULE_RE,
    CSS_STRING_RE,
    CSS_TAG_RE,
    CSS_URL_RE,
    UNSTATIC_CSS_PREFIXES,
    UNSTATIC_CSS_PROPERTIES,
)

if TYPE_CHECKING:
    from .html_parser import DiagramParser


def normalize_css_escapes(source: str) -> str:
    source = source.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")

    def replace(match: re.Match[str]) -> str:
        if match.group(1) is None:
            escaped = match.group(2)
            return "" if escaped == "\n" else escaped
        codepoint = int(match.group(1), 16)
        if codepoint == 0 or codepoint > 0x10FFFF:
            return "\N{REPLACEMENT CHARACTER}"
        return chr(codepoint)

    return CSS_ESCAPE_RE.sub(replace, source)


def check_css_references(parser: DiagramParser, errors: list[str]) -> None:
    source = normalize_css_escapes("\n".join(parser.styles + parser.css_attributes))
    found_loader = False
    if CSS_IMPORT_RE.search(source):
        errors.append("CSS @import is not allowed")
        found_loader = True
    for match in CSS_URL_RE.finditer(source):
        val = match.group(1).strip().strip("'\"").strip()
        if not val.startswith("#"):
            errors.append("non-fragment CSS url() is not allowed")
            found_loader = True
    if CSS_IMAGE_SET_RE.search(source):
        errors.append("CSS image-set() is not allowed")
        found_loader = True
    if CSS_REMOTE_RE.search(source) and not found_loader:
        errors.append("remote reference in CSS is not allowed")


def reference_error(tag: str, rel: str, value: str) -> str | None:
    stripped = value.strip()
    lowered = stripped.casefold()
    if not stripped or stripped.startswith("#"):
        return None
    if lowered.startswith("javascript:") or lowered.startswith("data:text/html"):
        return f"executable URL on <{tag}>: {stripped[:80]}"
    remote = lowered.startswith(("http://", "https://", "//")) or (
        ":" in stripped.split("/", 1)[0] and not lowered.startswith("data:")
    )
    if not remote:
        if lowered.startswith("data:") and not lowered.startswith("data:image/"):
            return f"non-image data URL on <{tag}>: {stripped[:80]}"
        return None
    if tag == "link" and "stylesheet" in rel.casefold().split():
        return f"external network stylesheet dependency not allowed: {stripped[:80]}"
    return f"remote reference on <{tag}>: {stripped[:80]}"


def declares_unstatic_css(declarations: str) -> bool:
    for declaration in declarations.split(";"):
        name = declaration.split(":", 1)[0].strip().casefold()
        if name in UNSTATIC_CSS_PROPERTIES or name.startswith(UNSTATIC_CSS_PREFIXES):
            return True
    return False


def selector_subjects(selector: str) -> list[tuple[str, set[str], set[str], set[str]]]:
    subjects = []
    for alternative in CSS_PARENS_RE.sub("", CSS_STRING_RE.sub("", selector)).split(","):
        parts = [part for part in CSS_COMBINATOR_RE.split(alternative.strip()) if part]
        if not parts:
            continue
        compound = parts[-1].split("::", 1)[0]
        tag = CSS_TAG_RE.match(compound)
        subjects.append(
            (
                tag.group(0).casefold() if tag else "",
                set(CSS_CLASS_RE.findall(compound)),
                set(CSS_ID_RE.findall(compound)),
                {name.casefold() for name in CSS_ATTRIBUTE_RE.findall(compound)},
            )
        )
    return subjects


def unstatic_css_subjects(source: str) -> list[tuple[str, set[str], set[str], set[str]]]:
    styles = re.findall(r"<style\b[^>]*>(.*?)</style\s*>", source, re.IGNORECASE | re.DOTALL)
    sheet = CSS_KEYFRAMES_RE.sub("", CSS_COMMENT_RE.sub("", "\n".join(styles)))
    subjects = []
    for selector, declarations in CSS_RULE_RE.findall(sheet):
        if declares_unstatic_css(declarations):
            subjects.extend(selector_subjects(selector))
    return subjects


def matches_subject(
    tag: str,
    attrs: dict[str, str],
    subject: tuple[str, set[str], set[str], set[str]],
) -> bool:
    subject_tag, classes, ids, attribute_names = subject
    if subject_tag not in {"", "*", tag}:
        return False
    if not classes <= set(attrs.get("class", "").split()):
        return False
    if not ids <= {attrs.get("id", "")}:
        return False
    return attribute_names <= set(attrs)


def declaring_css_subjects(
    source: str, declares: Callable[[str], bool]
) -> list[tuple[str, set[str], set[str], set[str]]]:
    styles = re.findall(r"<style\b[^>]*>(.*?)</style\s*>", source, re.IGNORECASE | re.DOTALL)
    sheet = CSS_KEYFRAMES_RE.sub("", CSS_COMMENT_RE.sub("", "\n".join(styles)))
    subjects = []
    for selector, declarations in CSS_RULE_RE.findall(sheet):
        names = {part.split(":", 1)[0].strip().casefold() for part in declarations.split(";")}
        if any(declares(name) for name in names):
            subjects.extend(selector_subjects(selector))
    return subjects
