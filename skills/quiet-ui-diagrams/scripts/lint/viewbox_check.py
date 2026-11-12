# SPDX-License-Identifier: MIT
"""ViewBox bounds verification, coordinate parsing, and extent calculation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from html.parser import HTMLParser

from .css_rules import (
    declares_unstatic_css,
    matches_subject,
    unstatic_css_subjects,
)
from .models import (
    GEOMETRY_ATTRS,
    SVG_NUMBER_RE,
    SVG_PLAIN_NUMBER_RE,
    TRANSLATE_RE,
    UNPAINTED_TAGS,
    VIEWBOX_TOLERANCE,
)


class SvgExtent:
    def __init__(self, attrs: dict[str, str]) -> None:
        self.attrs = attrs
        self.points: list[tuple[float, float, str]] = []


def svg_length(attrs: dict[str, str], name: str, default: float | None = None) -> float | None:
    value = attrs.get(name)
    if value is None:
        return default
    return float(value) if SVG_PLAIN_NUMBER_RE.match(value) else None


def painted_points(tag: str, attrs: dict[str, str]) -> list[tuple[float, float]]:
    if tag == "rect":
        x, y = svg_length(attrs, "x", 0.0), svg_length(attrs, "y", 0.0)
        width, height = svg_length(attrs, "width"), svg_length(attrs, "height")
        if x is None or y is None or width is None or height is None or width <= 0 or height <= 0:
            return []
        return [(x, y), (x + width, y + height)]
    if tag == "line":
        ends = [
            (svg_length(attrs, "x1", 0.0), svg_length(attrs, "y1", 0.0)),
            (svg_length(attrs, "x2", 0.0), svg_length(attrs, "y2", 0.0)),
        ]
        return [(x, y) for x, y in ends if x is not None and y is not None]
    if tag in {"circle", "ellipse"}:
        cx, cy = svg_length(attrs, "cx", 0.0), svg_length(attrs, "cy", 0.0)
        rx = svg_length(attrs, "r" if tag == "circle" else "rx")
        ry = svg_length(attrs, "r" if tag == "circle" else "ry")
        if cx is None or cy is None or rx is None or ry is None or rx <= 0 or ry <= 0:
            return []
        return [(cx - rx, cy - ry), (cx + rx, cy + ry)]
    if tag in {"polygon", "polyline"}:
        numbers = [float(val) for val in SVG_NUMBER_RE.findall(attrs.get("points", ""))]
        return list(zip(numbers[0::2], numbers[1::2]))
    if tag == "text":
        x, y = svg_length(attrs, "x"), svg_length(attrs, "y")
        return [] if x is None or y is None else [(x, y)]
    return []


def child_offset(
    tag: str,
    attrs: dict[str, str],
    parent: tuple[float, float] | None,
    css_subjects: list[tuple[str, set[str], set[str], set[str]]],
) -> tuple[float, float] | None:
    if parent is None or tag in UNPAINTED_TAGS:
        return None
    if declares_unstatic_css(attrs.get("style", "")):
        return None
    if attrs.get("display", "").strip().casefold() == "none":
        return None
    if attrs.get("visibility", "").strip().casefold() in {"hidden", "collapse"}:
        return None
    if attrs.get("clip-path", "none").strip().casefold() != "none":
        return None
    if attrs.get("mask", "none").strip().casefold() != "none":
        return None
    if any(matches_subject(tag, attrs, subject) for subject in css_subjects):
        return None
    transform = attrs.get("transform")
    if transform is None:
        return parent
    match = TRANSLATE_RE.match(transform)
    if match is None:
        return None
    return parent[0] + float(match.group(1)), parent[1] + float(match.group(2) or 0)


class ViewBoxParser(HTMLParser):
    def __init__(self, css_subjects: list[tuple[str, set[str], set[str], set[str]]]) -> None:
        super().__init__(convert_charrefs=True)
        self.svgs: list[SvgExtent] = []
        self._css_subjects = css_subjects
        self._frames: list[tuple[str, tuple[float, float] | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        data = {key.casefold(): value or "" for key, value in attrs}
        if not self._frames:
            if tag == "svg":
                self.svgs.append(SvgExtent(data))
                self._frames.append((tag, (0.0, 0.0)))
            return
        offset = child_offset(tag, data, self._frames[-1][1], self._css_subjects)
        self._frames.append((tag, offset))
        if offset is None:
            return
        label = (
            " ".join(
                [f"<{tag}"]
                + [f'{n}="{data[n]}"' for n in GEOMETRY_ATTRS.get(tag, ()) if n in data]
            )
            + ">"
        )
        for x, y in painted_points(tag, data):
            self.svgs[-1].points.append((x + offset[0], y + offset[1], label))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        for index in range(len(self._frames) - 1, -1, -1):
            if self._frames[index][0] == tag:
                del self._frames[index:]
                return


def check_viewbox(source: str, errors: list[str]) -> None:
    parser = ViewBoxParser(unstatic_css_subjects(source))
    parser.feed(source)
    parser.close()
    checkable = [
        svg for svg in parser.svgs if svg.attrs.get("aria-hidden", "").casefold() != "true"
    ]
    for number, svg in enumerate(checkable, 1):
        box = [float(v) for v in SVG_NUMBER_RE.findall(svg.attrs.get("viewbox", ""))]
        if len(box) != 4 or box[2] <= 0 or box[3] <= 0:
            continue
        left, top, width, height = box
        worst: dict[str, tuple[float, str]] = {}
        for x, y, label in svg.points:
            for side, overshoot in (
                ("left", left - x),
                ("top", top - y),
                ("right", x - (left + width)),
                ("bottom", y - (top + height)),
            ):
                if overshoot > VIEWBOX_TOLERANCE and overshoot > worst.get(side, (0.0, ""))[0]:
                    worst[side] = (overshoot, label)
        for side, (overshoot, label) in worst.items():
            errors.append(
                f"svg {number}: {label} paints {overshoot:g}px past the viewBox {side} edge "
                "and is clipped; grow the viewBox or move the content inside it"
            )
