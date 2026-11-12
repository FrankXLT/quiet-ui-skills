# SPDX-License-Identifier: MIT
"""Animation keyframe extraction, namespacing, and inline declaration rewriting.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import html as html_entities
import re

from .css_rules import (
    CSS_COMMENT_OR_LITERAL_RE,
    _CssRule,
    _css_rule_nodes,
    _css_segments,
    decoded_css_url_fragment,
    strip_css_comments,
)
from .xml_sanitize import START_TAG_RE, TAG_ATTR_RE, _rewrite_start_tags

STYLE_BLOCK_RE = re.compile(
    r"<style\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>(.*?)</style\s*>",
    re.IGNORECASE | re.DOTALL,
)


def _keyframe_names(rules: list[_CssRule], root_id: str) -> dict[str, str]:
    names: dict[str, str] = {}
    for rule in _css_rule_nodes(rules):
        keyframe = re.fullmatch(r"@(?:-webkit-)?keyframes\s+(.+)", rule.selector, re.IGNORECASE)
        if keyframe is None:
            continue
        name = keyframe.group(1).strip()
        if name[:1] in ("\"", "'") and name[-1:] == name[:1]:
            name = name[1:-1]
        if not re.fullmatch(r"[A-Za-z_][\w-]*", name):
            raise ValueError(f"unsupported CSS keyframe name in SVG export: {rule.selector}")
        names[name] = f"{root_id}-{name}"
    return names


def _animation_component(value: str, names: dict[str, str], shorthand: bool) -> str:
    tokens = re.compile(
        r"/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|(?<![\w.\\-])[-_A-Za-z][\w-]*|[()]",
        re.DOTALL,
    )
    depth = 0
    replacements: list[tuple[int, int, str]] = []
    found_name = False
    variable = False
    keywords = {
        "linear", "ease", "ease-in", "ease-out", "ease-in-out", "step-start",
        "step-end", "infinite", "normal", "reverse", "alternate", "alternate-reverse",
        "none", "forwards", "backwards", "both", "running", "paused"
    }
    for match in tokens.finditer(value):
        token = match.group(0)
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
        elif depth == 0 and not token.startswith("/*"):
            quote = token[:1] if token[:1] in ("\"", "'") else ""
            name = token[1:-1] if quote else token
            function = not quote and re.match(r"\s*\(", value[match.end():]) is not None
            variable = variable or (function and name.lower() == "var")
            if function or (not quote and name.lower() == "important" and re.search(r"!\s*$", value[:match.start()])):
                continue
            if not quote and name.lower() in {"none", "inherit", "initial", "unset", "revert", "revert-layer"}:
                continue
            if name in names:
                if shorthand and not quote and name.lower() in keywords:
                    raise ValueError("ambiguous CSS animation name in SVG export; use animation-name")
                replacements.append((match.start(), match.end(), f"{quote}{names[name]}{quote}"))
                found_name = True
    if "\\" in strip_css_comments(value) or (variable and not found_name):
        raise ValueError("unresolved CSS animation name in SVG export")
    for start, end, replacement in reversed(replacements):
        value = value[:start] + replacement + value[end:]
    return value


def _animation_property(prop: str) -> str:
    return decoded_css_url_fragment(strip_css_comments(prop).strip()).lower().removeprefix("-webkit-")


def _has_animation_property(css: str) -> bool:
    escape = r"\\(?:[0-9a-fA-F]{1,6}(?:\r\n|[ \t\r\n\f])?|[^\r\n\f])"
    tokens = re.compile(
        CSS_COMMENT_OR_LITERAL_RE.pattern + rf"|(?:^|[;{{])\s*(?P<prop>(?:{escape}|[\w-])+)\s*:",
        re.DOTALL,
    )
    return any(
        match.group("prop") is not None
        and _animation_property(match.group("prop")) in ("animation", "animation-name")
        for match in tokens.finditer(css)
    )


def _animation_declarations(body: str, names: dict[str, str]) -> str:
    if not names:
        return body
    segments = _css_segments(body, ";")
    for index, segment in enumerate(segments):
        parts = _css_segments(segment, ":")
        prop, colon, value = parts[0], ":" if len(parts) > 1 else "", ":".join(parts[1:])
        key = _animation_property(prop)
        if colon and key in ("animation", "animation-name"):
            value = ",".join(
                _animation_component(part, names, key == "animation")
                for part in _css_segments(value, ",")
            )
            segments[index] = prop + colon + value
    return ";".join(segments)


def namespace_inline_animations(svg: str, names: dict[str, str]) -> str:
    if not names:
        return svg
    if any(
        re.search(r"@(?:-webkit-)?keyframes\b", block, re.IGNORECASE) or _has_animation_property(block)
        for block in (strip_css_comments(b) for b in STYLE_BLOCK_RE.findall(svg))
    ):
        raise ValueError("unsupported SVG-local animation stylesheet in SVG export")

    def rewrite_tag(match: re.Match[str]) -> str:
        tag, attrs, end = match.groups()

        def rewrite_attr(attr: re.Match[str]) -> str:
            space, key, equals, value = attr.groups()
            if key == "style" and value is not None:
                quote = value[0]

                def decode_reference(ref: re.Match[str]) -> str:
                    raw = ref.group(0)
                    if raw.startswith("&#"):
                        return html_entities.unescape(raw)
                    return html_entities.entities.html5.get(raw[1:], raw)

                decoded = re.sub(
                    r"&(?:#(?:[xX][0-9A-Fa-f]+|[0-9]+)|[A-Za-z][A-Za-z0-9]+);",
                    decode_reference,
                    value[1:-1],
                )
                rewritten = _animation_declarations(decoded, names)
                encoded = (
                    html_entities.escape(rewritten, quote=True)
                    .replace("\t", "&#9;")
                    .replace("\n", "&#10;")
                    .replace("\r", "&#13;")
                )
                return space + key + equals + quote + encoded + quote
            return attr.group(0)

        return f"<{tag}{TAG_ATTR_RE.sub(rewrite_attr, attrs)}{end}>"

    return _rewrite_start_tags(svg, rewrite_tag)
