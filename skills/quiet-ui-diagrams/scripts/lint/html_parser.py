# SPDX-License-Identifier: MIT
"""HTML structure parsers, document completeness checks, and SVG accessibility validation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re

from .models import (
    CSS_REFERENCE_ATTRS,
    PAIRED_CONTAINER_TAGS,
    REFERENCE_ATTRS,
    REPLACEMENT_CHAR,
)


class DiagramParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.roots: list[dict[str, str]] = []
        self.items: list[dict[str, str]] = []
        self.actions: set[str] = set()
        self.controls = 0
        self.statuses: list[dict[str, str]] = []
        self.statuses_in_controls = 0
        self.scripts: list[dict[str, object]] = []
        self.styles: list[str] = []
        self.css_attributes: list[str] = []
        self.svgs: list[dict[str, object]] = []
        self.ids: Counter[str] = Counter()
        self.unsafe: list[str] = []
        self.references: list[tuple[str, str, str]] = []
        self._svg_depth = 0
        self._current_svg: dict[str, object] | None = None
        self._capture: str | None = None
        self._current_script: dict[str, object] | None = None
        self._in_style = False
        self._element_stack: list[str] = []
        self._motion_root_depth: int | None = None
        self._controls_depth: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        normalized_attrs = [(key.casefold(), value or "") for key, value in attrs]
        data: dict[str, str] = {}
        for key, value in normalized_attrs:
            data.setdefault(key, value)
        if data.get("id"):
            self.ids[data["id"]] += 1
        if tag in {"base", "embed", "object", "iframe"}:
            self.unsafe.append(f"<{tag}> is not allowed in a diagram file")
        for key, value in normalized_attrs:
            if key.startswith("on"):
                self.unsafe.append(f"executable attribute {key} on <{tag}>")
            if key == "srcdoc":
                self.unsafe.append(f"srcdoc attribute on <{tag}>")
            if key in REFERENCE_ATTRS:
                self.references.append((tag, data.get("rel", ""), value))
            if key in CSS_REFERENCE_ATTRS:
                self.css_attributes.append(value)
        if "data-motion-root" in data:
            self.roots.append(data)
            if self._motion_root_depth is None:
                self._motion_root_depth = len(self._element_stack)
        if self._motion_root_depth is not None:
            if "data-motion-item" in data:
                self.items.append(data)
            if "data-motion-action" in data:
                self.actions.add(data["data-motion-action"])
            if "data-motion-controls" in data:
                self.controls += 1
                if self._controls_depth is None:
                    self._controls_depth = len(self._element_stack)
            if "data-motion-status" in data:
                self.statuses.append(data)
                if self._controls_depth is not None:
                    self.statuses_in_controls += 1
        if tag == "script":
            self._current_script = {
                "attrs": data,
                "attr_names": [name for name, _value in normalized_attrs],
                "body": [],
                "closed": False,
            }
            self.scripts.append(self._current_script)
        if tag == "style":
            self._in_style = True
        self._element_stack.append(tag)
        if tag == "svg" and self._svg_depth == 0:
            self._svg_depth = 1
            self._current_svg = {"attrs": data, "first": None, "title": {}, "desc": {}}
            self.svgs.append(self._current_svg)
            return
        if self._svg_depth:
            self._svg_depth += 1
            assert self._current_svg is not None
            if self._svg_depth == 2 and self._current_svg["first"] is None:
                self._current_svg["first"] = tag
            if self._svg_depth == 2 and tag in {"title", "desc"}:
                self._current_svg[tag] = {"attrs": data, "text": ""}
                self._capture = tag

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "script" and self._current_script is not None:
            self._current_script["closed"] = True
            self._current_script = None
        if tag == "style":
            self._in_style = False
        if self._svg_depth:
            if tag in {"title", "desc"}:
                self._capture = None
            self._svg_depth -= 1
            if self._svg_depth == 0:
                self._current_svg = None
        for index in range(len(self._element_stack) - 1, -1, -1):
            if self._element_stack[index] == tag:
                del self._element_stack[index:]
                break
        if self._motion_root_depth is not None and len(self._element_stack) <= self._motion_root_depth:
            self._motion_root_depth = None
        if self._controls_depth is not None and len(self._element_stack) <= self._controls_depth:
            self._controls_depth = None

    def handle_data(self, data: str) -> None:
        if self._current_script is not None:
            body = self._current_script["body"]
            assert isinstance(body, list)
            body.append(data)
        if self._in_style:
            self.styles.append(data)
        if self._capture and self._current_svg:
            node = self._current_svg[self._capture]
            assert isinstance(node, dict)
            node["text"] = str(node.get("text", "")) + data


class BalanceParser(HTMLParser):
    RCDATA_ELEMENTS = ("title", "textarea")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.opens: Counter[str] = Counter()
        self.closes: Counter[str] = Counter()
        self.rcdata = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.rcdata:
            return
        self.opens[tag] += 1
        if tag in self.RCDATA_ELEMENTS:
            self.rcdata = tag

    def handle_endtag(self, tag: str) -> None:
        if self.rcdata:
            if tag == self.rcdata:
                self.rcdata = ""
                self.closes[tag] += 1
            return
        self.closes[tag] += 1


def parsed_document(source: str) -> DiagramParser:
    parser = DiagramParser()
    parser.feed(source)
    parser.close()
    return parser


def ends_with_shell_close(source: str) -> bool:
    tail = source.rstrip()
    while True:
        start = tail.rfind("<!--")
        if start < 0:
            break
        end = tail.find("-->", start + 4)
        if end < 0 or tail[end + 3 :].strip():
            break
        tail = tail[:start].rstrip()
    return re.search(r"</html\s*>\Z", tail, re.IGNORECASE) is not None


def check_document_completeness(source: str, errors: list[str]) -> None:
    if not ends_with_shell_close(source):
        errors.append("document does not end with </html>; the file looks truncated")

    replacements = source.count(REPLACEMENT_CHAR)
    if replacements:
        line = source[: source.index(REPLACEMENT_CHAR)].count("\n") + 1
        errors.append(
            f"contains {replacements} U+FFFD replacement character(s), first on line {line}:"
            " the file has mojibake or a truncated multi-byte character"
        )

    parser = BalanceParser()
    parser.feed(source)
    parser.close()
    if parser.rcdata:
        errors.append(
            f"<{parser.rcdata}> is never closed; the rest of the document reads as its text"
        )
        return
    for tag in PAIRED_CONTAINER_TAGS:
        opens, closes = parser.opens[tag], parser.closes[tag]
        if opens != closes:
            errors.append(
                f"<{tag}> opens {opens} time(s) and closes {closes} time(s);"
                " the document is not balanced"
            )


def check_svgs(parser: DiagramParser, errors: list[str]) -> None:
    checkable = [
        svg
        for svg in parser.svgs
        if isinstance(svg["attrs"], dict)
        and str(svg["attrs"].get("aria-hidden", "")).casefold() != "true"
    ]
    if not checkable:
        errors.append("diagram file needs at least one accessible (non-aria-hidden) SVG")
    for number, svg in enumerate(checkable, 1):
        attrs = svg["attrs"]
        assert isinstance(attrs, dict)
        if attrs.get("role") != "img":
            errors.append(f"svg {number} needs role=img")
        labelled = attrs.get("aria-labelledby", "").split()
        title = svg["title"]
        desc = svg["desc"]
        assert isinstance(title, dict) and isinstance(desc, dict)
        title_attrs = title.get("attrs", {})
        desc_attrs = desc.get("attrs", {})
        assert isinstance(title_attrs, dict) and isinstance(desc_attrs, dict)
        if svg["first"] != "title":
            errors.append(f"svg {number} title must be its first child")
        if not str(title.get("text", "")).strip() or not str(desc.get("text", "")).strip():
            errors.append(f"svg {number} needs non-empty title and desc")
        title_id = title_attrs.get("id", "")
        desc_id = desc_attrs.get("id", "")
        if title_id in {"", "title"} or desc_id in {"", "desc"}:
            errors.append(f"svg {number} title/desc IDs must be diagram-prefixed, never bare")
        for naming_id in dict.fromkeys((title_id, desc_id)):
            if parser.ids[naming_id] > 1:
                errors.append(f"duplicate accessible SVG naming ID {naming_id!r}")
        if labelled != [title_id, desc_id]:
            errors.append(f"svg {number} aria-labelledby must name title then desc")
