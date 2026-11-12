# SPDX-License-Identifier: MIT
"""Color normalization, presentation attribute splitting, and RGBA opacity calculation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import html as html_entities
import math
import re
import xml.etree.ElementTree as ET

from .css_rules import (
    RULE_RE,
    selector_list_parts,
    strip_css_comments,
)
from .defs_packer import STYLE_BLOCK_RE
from .xml_sanitize import START_TAG_RE, TAG_ATTR_RE, _rewrite_start_tags

RGBA_ATTR_RE = re.compile(
    r'(fill|stroke)="rgba\(\s*([+-]?\d+)\s*,\s*([+-]?\d+)\s*,\s*([+-]?\d+)\s*,\s*([+-]?\d*\.?\d+)\s*\)"'
)
TRANSPARENT_ATTR_RE = re.compile(r'(fill|stroke)="transparent"')


def _decoded_css_property_text(style: str) -> str:
    style = strip_css_comments(html_entities.unescape(style))

    def escape(match: re.Match[str]) -> str:
        hexadecimal, literal = match.groups()
        if hexadecimal is not None:
            val = int(hexadecimal, 16)
            return chr(val) if 0 < val <= 0x10FFFF and not 0xD800 <= val <= 0xDFFF else "\ufffd"
        return "" if literal in "\r\n\f" else literal

    return re.sub(r"\\(?:([0-9a-fA-F]{1,6})(?:\r\n|[ \t\r\n\f])?|([\s\S]))", escape, style)


def _css_paint_may_target_descendants(selector: str, children: list[ET.Element]) -> bool:
    for branch in selector_list_parts(selector):
        if "\\" in branch:
            return True
        terminal = re.split(r"[\s>+~]+", branch.strip())[-1]
        if not re.fullmatch(r"(?:[A-Za-z][\w-]*|\*)?(?:[.#][\w-]+)*", terminal) or not terminal:
            return True
        tag = re.match(r"^[A-Za-z][\w-]*", terminal)
        classes = re.findall(r"\.([\w-]+)", terminal)
        ids = re.findall(r"#([\w-]+)", terminal)
        for child in children:
            if tag and child.tag.rsplit("}", 1)[-1] != tag.group(0):
                continue
            if all(name in child.get("class", "").split() for name in classes) and all(
                name == child.get("id") for name in ids
            ):
                return True
    return False


def normalize_rgba_presentation_attrs(svg: str) -> str:
    try:
        elements = list(ET.fromstring(svg).iter())
        descendants = {
            index: list(element.iter())[1:]
            for index, element in enumerate(elements)
            if len(element)
        }
    except ET.ParseError:
        return svg
    opacity_counts = {"fill-opacity": 0, "stroke-opacity": 0}
    styles = list(STYLE_BLOCK_RE.findall(svg))

    def collect_opacity_context(match: re.Match[str]) -> str:
        for attr in TAG_ATTR_RE.finditer(match.group(2)):
            key, value = attr.group(2), attr.group(4)
            if key in opacity_counts:
                opacity_counts[key] += 1
            elif key == "style" and value is not None:
                styles.append(value[1:-1])
        return match.group(0)

    _rewrite_start_tags(svg, collect_opacity_context)
    css_opacity = {
        key
        for key in opacity_counts
        if any(
            re.search(rf"(?:^|[;{{])\s*{key}\s*:", _decoded_css_property_text(st), re.IGNORECASE)
            for st in styles
        )
    }

    position = 0

    def normalize_tag(match: re.Match[str]) -> str:
        nonlocal position
        children = descendants.get(position, [])
        element = elements[position]
        position += 1
        name, attrs, end = match.groups()
        values = {
            attr.group(2): attr.group(4)[1:-1]
            for attr in TAG_ATTR_RE.finditer(attrs)
            if attr.group(4) is not None
        }
        updates: dict[str, str] = {}
        additions: list[str] = []
        for prop in ("fill", "stroke"):
            value = values.get(prop, "")
            if value == "transparent":
                updates[prop] = "none"
                continue
            rgba = RGBA_ATTR_RE.fullmatch(f'{prop}="{value}"')
            if rgba is None:
                continue
            _, r, g, b, alpha = rgba.groups()
            opacity_name = f"{prop}-opacity"
            inline_paint = re.search(
                rf"(?:^|[;{{])\s*{prop}\s*:",
                _decoded_css_property_text(element.get("style", "")),
                re.I,
            )
            descendant_paint = any(
                prop in child.attrib
                or re.search(
                    rf"(?:^|[;{{])\s*{prop}\s*:",
                    _decoded_css_property_text(child.get("style", "")),
                    re.I,
                )
                for child in children
            )
            stylesheet_paint = any(
                re.search(rf"(?:^|[;{{])\s*{prop}\s*:", _decoded_css_property_text(rule.group(2)), re.I)
                and _css_paint_may_target_descendants(rule.group(1), [element] + children)
                for style in STYLE_BLOCK_RE.findall(svg)
                for rule in RULE_RE.finditer(strip_css_comments(style))
            )
            if (
                inline_paint
                or descendant_paint
                or stylesheet_paint
                or opacity_name in css_opacity
                or opacity_counts[opacity_name] > int(opacity_name in values)
            ):
                continue
            opacity = alpha if 0 <= float(alpha) <= 1 else "0" if float(alpha) < 0 else "1"
            if opacity_name in values:
                try:
                    orig = values[opacity_name].strip()
                    amount = float(orig.rstrip("%")) / (100 if orig.endswith("%") else 1)
                except ValueError:
                    continue
                if not math.isfinite(amount):
                    continue
                opacity = format(min(1, max(0, amount)) * max(0, min(1, float(alpha))), ".12g")
                updates[opacity_name] = opacity
            else:
                additions.append(f' {opacity_name}="{opacity}"')
            updates[prop] = "#{:02x}{:02x}{:02x}".format(
                *(max(0, min(255, int(c))) for c in (r, g, b))
            )

        def replace_attr(attr: re.Match[str]) -> str:
            space, key, _, _ = attr.groups()
            return f'{space}{key}="{updates[key]}"' if key in updates else attr.group(0)

        return f"<{name}{TAG_ATTR_RE.sub(replace_attr, attrs)}{''.join(additions)}{end}>"

    return _rewrite_start_tags(svg, normalize_tag)
