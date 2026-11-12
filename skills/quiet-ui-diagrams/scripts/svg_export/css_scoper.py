# SPDX-License-Identifier: MIT
"""CSS scoping, root-binding, body inheritance, and rule rendering.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re
import sys

from .animation_packer import _animation_declarations, _animation_property
from .css_rules import (
    BODY_INHERITED_RE,
    SVG_TYPE_PREFIX_RE,
    _CssRule,
    _css_rule_nodes,
    _css_segments,
    _html_css_rules,
    css_escape,
    css_id_token,
    is_chrome_selector,
    selector_list_parts,
    strip_css_comments,
)
from .xml_sanitize import escape_css_for_xml


def root_bound_compound(selector: str, root_id: str) -> bool:
    pos = 0
    depth = 0
    quote = ""
    while pos < len(selector):
        char = selector[pos]
        if char == "\\":
            escaped = css_escape(selector, pos)
            pos = escaped[1] if escaped else pos + 1
            continue
        if quote:
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char in "[(":
            depth += 1
        elif char in "])":
            depth -= 1
        elif depth == 0 and (char.isspace() or char in ">+~"):
            break
        elif depth == 0 and char == "#":
            token = css_id_token(selector, pos + 1)
            if token:
                value, pos = token
                if value == root_id:
                    return True
                continue
        pos += 1
    return False


def scope_selector(selector: str, root_id: str) -> str:
    scoped: list[str] = []
    for part in selector_list_parts(selector):
        part = part.strip()
        if not part:
            continue
        if part == ":root" or part.startswith(":root"):
            remainder = part[len(":root") :].strip()
            scoped.append(f"#{root_id}" + (f" {remainder}" if remainder else ""))
        elif root_bound_compound(part, root_id):
            scoped.append(part)
        elif part.startswith("#"):
            scoped.append(part)
        elif SVG_TYPE_PREFIX_RE.match(part):
            rest = part[len("svg") :]
            if rest:
                scoped.append(f"#{root_id}{rest}")
        else:
            scoped.append(f"#{root_id} {part}")
    return ", ".join(scoped)


def body_inherited_css(selector: str, body: str, root_id: str) -> str:
    parts = [part.strip().lower() for part in selector_list_parts(selector)]
    if "body" not in parts:
        return ""
    declarations = [
        f"{name.lower()}: {value.strip()}" for name, value in BODY_INHERITED_RE.findall(body)
    ]
    if not declarations:
        return ""
    return f"#{root_id} {{ {'; '.join(declarations)}; }}"


def retarget_root_selector(selector: str, original_id: str, root_id: str) -> str:
    out: list[str] = []
    quote = ""
    pos = 0
    while pos < len(selector):
        char = selector[pos]
        if char == "\\":
            escaped = css_escape(selector, pos)
            end = escaped[1] if escaped else pos + 1
            out.append(selector[pos:end])
            pos = end
            continue
        if quote:
            out.append(char)
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
            out.append(char)
        elif char == "#":
            token = css_id_token(selector, pos + 1)
            if token:
                value, end = token
                out.append(f"#{root_id}" if value == original_id else selector[pos:end])
                pos = end
                continue
            out.append(char)
        else:
            out.append(char)
        pos += 1
    return "".join(out)


def _diagram_css_leaf(
    rule: _CssRule,
    root_id: str,
    names: dict[str, str],
    original_root_id: str,
    system_fonts: bool,
) -> str:
    kept: list[str] = []
    selector = rule.selector.strip()
    if rule.statement:
        return escape_css_for_xml(selector + ";")
    body = rule.css[rule.start : rule.end].strip()
    if not selector or not body:
        return ""
    if re.match(r"@(?:-webkit-)?keyframes\b", selector, re.IGNORECASE):
        prefix, name = selector.rsplit(None, 1)
        quote = name[:1] if name[:1] in ("\"", "'") else ""
        original = name[1:-1] if quote else name
        kept.append(escape_css_for_xml(f"{prefix} {quote}{names[original]}{quote} {{ {body} }}"))
        return "\n      ".join(kept)
    if re.match(r"@font-face\b", selector, re.IGNORECASE):
        if not system_fonts:
            kept.append(escape_css_for_xml(f"{selector} {{ {body} }}"))
        return "\n      ".join(kept)
    if selector.startswith("@"):
        print(f"warning: dropping unsupported CSS block in SVG export: {selector}", file=sys.stderr)
        return "\n      ".join(kept)
    if original_root_id:
        selector = retarget_root_selector(selector, original_root_id, root_id)
    selector = selector.strip()
    if names:
        pending_nested = list(rule.children)
        if any(not re.fullmatch(r"--[\w-]+\s*:", strip_css_comments(c.selector).strip()) for c in rule.children):
            pending_nested.append(rule)
        while pending_nested:
            nested = pending_nested.pop()
            if re.fullmatch(r"--[\w-]+\s*:", strip_css_comments(nested.selector).strip()):
                continue
            pending_nested.extend(nested.children)
            segments: list[str] = []
            cursor = nested.children[0].end + 1 if nested is rule else nested.start
            for child in (nested.children[1:] if nested is rule else nested.children):
                segments.extend(_css_segments(nested.css[cursor : child.start - 1], ";")[:-1])
                cursor = child.end + 1
            segments.extend(_css_segments(nested.css[cursor : nested.end], ";"))
            for segment in segments:
                parts = _css_segments(segment, ":")
                key = _animation_property(parts[0])
                if len(parts) > 1 and key in ("animation", "animation-name"):
                    raise ValueError("unsupported nested CSS animation declaration in SVG export")
    body = _animation_declarations(body, names)
    inherited = body_inherited_css(selector, body, root_id)
    if inherited:
        kept.append(escape_css_for_xml(inherited))
    if is_chrome_selector(selector):
        return "\n      ".join(kept)
    kept.append(escape_css_for_xml(f"{scope_selector(selector, root_id)} {{ {body} }}"))
    return "\n      ".join(kept)


def _diagram_css_rules(
    rules: list[_CssRule],
    root_id: str,
    names: dict[str, str],
    original_root_id: str = "",
    system_fonts: bool = False,
) -> str:
    nodes = list(_css_rule_nodes(rules))
    ordinary: dict[_CssRule, bool] = {}
    for rule in reversed(nodes):
        ordinary[rule] = (
            any(ordinary[child] for child in rule.children)
            if rule.group
            else not rule.selector.startswith("@")
        )
    for rule in nodes:
        if rule.group and ordinary[rule] and re.match(r"@scope\b", rule.selector, re.IGNORECASE):
            raise ValueError("unsupported CSS scope with paint rules in SVG export; move paint outside @scope")
    leaves = {
        rule: _diagram_css_leaf(rule, root_id, names, original_root_id, system_fonts)
        for rule in nodes
        if not rule.group
    }
    retained: dict[_CssRule, bool] = {}
    for rule in reversed(nodes):
        retained[rule] = any(retained[child] for child in rule.children) if rule.group else bool(leaves[rule])
    output: list[str] = []

    def siblings(items: list[_CssRule]) -> list[tuple[_CssRule, str]]:
        kept = [rule for rule in items if retained[rule]]
        return list(reversed([(rule, "" if index == 0 else "\n      ") for index, rule in enumerate(kept)]))

    pending: list[tuple[_CssRule, str] | str] = siblings(rules)
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            output.append(item)
            continue
        rule, separator = item
        output.append(separator)
        if rule.group:
            output.append(escape_css_for_xml(rule.selector) + " {\n")
            pending.append("\n}")
            pending.extend(siblings(rule.children))
        else:
            output.append(leaves[rule])
    return "".join(output)


def diagram_css_from_html(
    html: str, root_id: str, original_root_id: str = "", system_fonts: bool = False
) -> str:
    rules = _html_css_rules(html)
    return _diagram_css_rules(
        rules, root_id, names={}, original_root_id=original_root_id, system_fonts=system_fonts
    )
