# SPDX-License-Identifier: MIT
"""Font metric advance calculation and text box overflow verification.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re
import unicodedata

from .models import (
    MONO_ADVANCE,
    PAINT_PROPERTIES,
    SANS_ADVANCE,
    SVG_NUMBER,
    TEXT_FIT_IGNORED,
    TEXT_FIT_PROPERTIES,
    TEXT_FIT_TOLERANCE_EM,
    TEXT_LAYOUT_PROPERTIES,
    WIDE_ADVANCE,
)
from .text_fit_parser import TextFitParser


def inline_paint(attrs: dict[str, str]) -> dict[str, str]:
    values = {name: attrs[name].strip().casefold() for name in PAINT_PROPERTIES if name in attrs}
    for declaration in attrs.get("style", "").split(";"):
        name, _, value = declaration.partition(":")
        name = name.strip().casefold()
        if name in PAINT_PROPERTIES:
            values[name] = value.strip().casefold()
    return values


def inline_text_style(attrs: dict[str, str]) -> dict[str, str]:
    values = {name: attrs[name] for name in TEXT_FIT_PROPERTIES if name in attrs}
    values.update({name: "" for name in TEXT_LAYOUT_PROPERTIES if name in attrs})
    for declaration in attrs.get("style", "").split(";"):
        name, _, value = declaration.partition(":")
        name = name.strip().casefold()
        if restyles_text_width(name):
            values[name] = value.strip() if name in TEXT_FIT_PROPERTIES else ""
    return values


def restyles_text_width(name: str) -> bool:
    if name in TEXT_FIT_IGNORED:
        return False
    return (
        name.startswith(("font", "letter-spacing", "word-spacing"))
        or name == "text-anchor"
        or name in TEXT_LAYOUT_PROPERTIES
    )


def zero_alpha(value: str) -> bool | None:
    value = value.strip().casefold()
    if value in {"none", "transparent"}:
        return True
    if value.startswith("var("):
        return None
    num = re.fullmatch(rf"({SVG_NUMBER})(%?)", value)
    if num:
        return float(num.group(1)) <= 0
    if re.fullmatch(r"#[0-9a-f]{4}|#[0-9a-f]{8}", value):
        return int(value[4] if len(value) == 5 else value[7:], 16) == 0
    func = re.fullmatch(r"(?:rgba?|hsla?)\((.*)\)", value)
    if func:
        parts = [p for p in re.split(r"[\s,/]+", func.group(1).strip()) if p]
        return zero_alpha(parts[3]) if len(parts) == 4 else False
    return False if value.startswith("#") or value.isalpha() else None


def text_advance(text: str, mono: bool) -> float:
    narrow = MONO_ADVANCE if mono else SANS_ADVANCE
    advance = 0.0
    for char in text:
        if unicodedata.category(char) in {"Mn", "Me"}:
            continue
        advance += WIDE_ADVANCE if unicodedata.east_asian_width(char) in {"W", "F"} else narrow
    return advance


def font_size_px(style: dict[str, str]) -> float | None:
    match = re.fullmatch(rf"\s*({SVG_NUMBER})\s*(?:px)?\s*", style.get("font-size", ""))
    return float(match.group(1)) if match else None


def text_run_width(text: str, style: dict[str, str]) -> float | None:
    size = font_size_px(style)
    if size is None:
        return None
    spacing = style.get("letter-spacing", "normal").strip().casefold()
    match = re.fullmatch(rf"({SVG_NUMBER})\s*(em|px)?", spacing)
    if spacing == "normal":
        tracking = 0.0
    elif match is None:
        return None
    else:
        tracking = float(match.group(1)) * (size if match.group(2) == "em" else 1)
    glyphs = sum(1 for c in text if unicodedata.category(c) not in {"Mn", "Me"})
    mono = "mono" in style.get("font-family", "").casefold()
    return text_advance(text, mono) * size + tracking * glyphs


def rect_area(rect: tuple) -> float:
    return (rect[2] - rect[0]) * (rect[3] - rect[1])


def check_text_fit(source: str, errors: list[str]) -> None:
    parser = TextFitParser(
        source,
        restyles_text_width,
        zero_alpha,
        inline_paint,
        inline_text_style,
    )
    parser.feed(source)
    parser.close()
    checkable = [
        svg
        for svg in parser.svgs
        if isinstance(svg["attrs"], dict)
        and svg["attrs"].get("aria-hidden", "").casefold() != "true"
    ]
    for number, svg in enumerate(checkable, 1):
        rects, lines, papers = svg["rects"], svg["lines"], svg["papers"]
        assert isinstance(rects, list) and isinstance(lines, list) and isinstance(papers, set)
        for line in lines:
            runs = [(re.sub(r"\s+", " ", r), st) for r, st in line["runs"]]
            text = "".join(r for r, _ in runs)
            if not text.strip():
                continue
            runs[0] = (runs[0][0].lstrip(), runs[0][1])
            runs[-1] = (runs[-1][0].rstrip(), runs[-1][1])
            widths = [text_run_width(r, st) for r, st in runs]
            if any(w is None for w in widths):
                continue
            width = sum(widths)
            size = max(font_size_px(st) or 0.0 for _, st in runs)
            x, y = line["x"], line["y"]
            behind = [
                r for r in rects[: line["rects"]]
                if r[0] <= x <= r[2] and r[1] <= y <= r[3]
            ]
            visible = [r for r in behind if r[5] or (r[4] is not None and r[4] not in papers)]
            if not visible:
                continue
            box = min(visible, key=rect_area)
            if min(rect_area(r) for r in behind) < rect_area(box) or box[4] is None:
                continue
            left, right = box[0], box[2]
            anchor = line["anchor"]
            start = x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x
            overshoot = max(left - start, start + width - right)
            if overshoot > TEXT_FIT_TOLERANCE_EM * size:
                errors.append(
                    f"svg {number}: text {text.strip()!r} at ({x:g}, {y:g}) is budgeted at "
                    f"{width:.0f}px and overflows its {right - left:g}px box by {overshoot:.0f}px; "
                    "widen the box or shorten the label (budget: 0.60em sans, 0.62em mono per char)"
                )
