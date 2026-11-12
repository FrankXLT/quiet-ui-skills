# SPDX-License-Identifier: MIT
"""Standalone SVG 1.1 exporter pipeline and export gate validation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .animation_packer import _keyframe_names, namespace_inline_animations
from .color_normalizer import normalize_rgba_presentation_attrs
from .css_rules import RULE_RE, _html_css_rules, strip_css_comments
from .css_scoper import _diagram_css_rules
from .defs_packer import (
    REFERENCE_REGION_RE,
    STYLE_BLOCK_RE,
    merge_style_into_defs,
    namespace_defs_ids,
    slug_for,
)
from .var_resolver import resolve_svg_variables
from .xml_sanitize import (
    START_TAG_RE,
    TAG_ATTR_RE,
    decode_xml_references,
    ensure_viewbox,
    ensure_xmlns,
    extract_first_svg,
    normalize_html_entities,
    set_root_id,
    xml_safe_comments,
    xmlify_attributes,
)


def has_diagram_stylesheet(svg: str) -> bool:
    for block in STYLE_BLOCK_RE.findall(svg):
        stripped = re.sub(r"@import\b[^;]*;", "", block, flags=re.IGNORECASE)
        stripped = strip_css_comments(stripped)
        if RULE_RE.search(stripped):
            return True
    return False


def assert_export_gate(svg: str) -> None:
    uses_classes = False
    for region in REFERENCE_REGION_RE.finditer(svg):
        tag = START_TAG_RE.fullmatch(region.group(0))
        if tag is None:
            continue
        for attr in TAG_ATTR_RE.finditer(tag.group(2)):
            if attr.group(2) == "class" and attr.group(4) is not None:
                uses_classes |= bool(decode_xml_references(attr.group(4)[1:-1]).strip())
    if uses_classes and not has_diagram_stylesheet(svg):
        raise ValueError(
            "exported SVG uses class= but has no diagram CSS rules; class-based "
            "fills would render as black boxes. Carry the page CSS into the SVG."
        )


def export_svg_document(
    html: str,
    source_path: Path,
    theme: str = "white",
    system_fonts: bool = True,
) -> str:
    slug = slug_for(source_path)
    root_id = f"{slug}-root"
    svg = normalize_html_entities(xmlify_attributes(extract_first_svg(html)))
    ensure_viewbox(svg)
    svg = ensure_xmlns(svg)
    opening = START_TAG_RE.match(svg)
    assert opening is not None
    original_root_id = next(
        (
            decode_xml_references(attr.group(4)[1:-1])
            for attr in TAG_ATTR_RE.finditer(opening.group(2))
            if attr.group(2) == "id" and attr.group(4) is not None
        ),
        "",
    )
    svg = set_root_id(svg, root_id)
    rules = _html_css_rules(html)
    names = _keyframe_names(rules, root_id)
    diagram_css = _diagram_css_rules(
        rules, root_id, names, original_root_id, system_fonts=system_fonts
    )
    svg = namespace_inline_animations(svg, names)
    svg = merge_style_into_defs(svg, diagram_css)
    svg = namespace_defs_ids(svg, slug)
    svg = xml_safe_comments(svg)
    svg = resolve_svg_variables(svg, theme=theme, html_source=html)
    svg = normalize_rgba_presentation_attrs(svg)
    assert_export_gate(svg)

    document = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n"
    try:
        ET.fromstring(document)
    except ET.ParseError as exc:
        raise ValueError(f"exported SVG is not well-formed XML: {exc}") from exc
    return document
