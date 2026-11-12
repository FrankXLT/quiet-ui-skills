# SPDX-License-Identifier: MIT
"""CSS tokenization, selector classification, and AST rule parsing.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re
from typing import Iterator

from .xml_sanitize import CDATA_SECTION_RE, html_tokens

CHROME_SELECTOR_RE = re.compile(
    r"^(?:\*|html|body|main|header|footer|h1|h2|h3|p|\.frame|\.eyebrow|\.summary|\.cards?|\.card|\.footer|\.header)(?:\s|:|,|$)",
    re.IGNORECASE,
)
SVG_TYPE_PREFIX_RE = re.compile(r"^svg(?![\w-])", re.IGNORECASE)
BODY_INHERITED_RE = re.compile(r"(?:^|;)\s*(color|font-family)\s*:\s*([^;]+)", re.IGNORECASE)
CSS_COMMENT_OR_LITERAL_RE = re.compile(
    r'''"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*'|\\[\s\S]|/\*.*?\*/''',
    re.DOTALL,
)
CSS_RULE_ATOM = r'''(?:/\*(?:[^*]|\*(?!/))*\*/|\\[\s\S]|"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*'|/(?!\*)|[^{}"'\\/])'''
RULE_RE = re.compile(rf"({CSS_RULE_ATOM}+)\{{({CSS_RULE_ATOM}*)\}}", re.DOTALL)


def strip_css_comments(css: str) -> str:
    return CSS_COMMENT_OR_LITERAL_RE.sub(
        lambda tok: "" if tok.group(0).startswith("/*") else tok.group(0), css
    )


def css_escape(text: str, pos: int) -> tuple[str, int] | None:
    end = pos + 1
    if end == len(text) or text[end] in "\n\r\f":
        return None
    start = end
    while end < min(start + 6, len(text)) and text[end] in "0123456789abcdefABCDEF":
        end += 1
    if end == start:
        return text[end], end + 1
    code = int(text[start:end], 16)
    value = chr(code) if 0 < code <= 0x10FFFF and not 0xD800 <= code <= 0xDFFF else "\ufffd"
    if end < len(text) and text[end] in " \t\n\r\f":
        end += 2 if text[end : end + 2] == "\r\n" else 1
    return value, end


def decoded_css_url_fragment(fragment: str) -> str:
    decoded: list[str] = []
    pos = 0
    while pos < len(fragment):
        if fragment[pos] == "\\":
            escaped = css_escape(fragment, pos)
            if escaped is None:
                return fragment
            val, pos = escaped
            decoded.append(val)
        else:
            decoded.append(fragment[pos])
            pos += 1
    return "".join(decoded)


def css_id_token(text: str, pos: int) -> tuple[str, int] | None:
    def starts_name(index: int) -> bool:
        char = text[index : index + 1]
        return bool(char) and (
            char in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            or ord(char) >= 128
            or (char == "\\" and css_escape(text, index) is not None)
        )

    if not starts_name(pos) and not (
        text[pos : pos + 1] == "-" and (starts_name(pos + 1) or text[pos + 1 : pos + 2] == "-")
    ):
        return None
    out: list[str] = []
    while pos < len(text):
        char = text[pos]
        if char == "\\":
            escaped = css_escape(text, pos)
            if escaped is None:
                break
            val, pos = escaped
            out.append(val)
        elif char in "_-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" or ord(char) >= 128:
            out.append(char)
            pos += 1
        else:
            break
    return "".join(out), pos


def selector_list_parts(selector: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote = ""
    pos = 0
    while pos < len(selector):
        char = selector[pos]
        if char == "\\":
            escape = css_escape(selector, pos)
            if escape:
                pos = escape[1]
                continue
        if quote:
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(selector[start:pos])
            start = pos + 1
        pos += 1
    parts.append(selector[start:])
    return parts


def is_chrome_selector(selector: str) -> bool:
    parts = [part.strip() for part in selector_list_parts(selector) if part.strip()]
    if not parts:
        return True
    return all(
        part.lower() == "svg" or CHROME_SELECTOR_RE.match(part) is not None for part in parts
    )


def _css_segments(text: str, separator: str) -> list[str]:
    pieces: list[str] = []
    start, parentheses, braces = 0, 0, 0
    quote = ""
    escaped = False
    comment = False
    index = 0
    while index < len(text):
        char = text[index]
        if comment:
            if text.startswith("*/", index):
                comment = False
                index += 1
        elif escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote:
            if char == quote:
                quote = ""
        elif text.startswith("/*", index):
            comment = True
            index += 1
        elif char in "\"'":
            quote = char
        elif char == "(":
            parentheses += 1
        elif char == ")":
            parentheses = max(0, parentheses - 1)
        elif char == "{" and parentheses == 0:
            braces += 1
        elif char == "}" and parentheses == 0:
            braces = max(0, braces - 1)
        elif char == separator and parentheses == 0 and braces == 0:
            pieces.append(text[start:index])
            start = index + 1
        index += 1
    pieces.append(text[start:])
    return pieces


class _CssRule:
    def __init__(self, css: str, start: int, opening: int):
        self.css = css
        self.selector = css[start:opening].strip()
        self.start = opening + 1
        self.end = opening + 1
        self.children: list[_CssRule] = []
        self.group = False
        self.statement = False


def _css_rule_tree(css: str) -> list[_CssRule]:
    roots: list[_CssRule] = []
    stack: list[_CssRule] = []
    nodes: list[_CssRule] = []
    starts = [0]
    quote = ""
    escaped = False
    parentheses = 0
    for index, char in enumerate(css):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in "\"'":
            quote = char
        elif char == "(":
            parentheses += 1
        elif char == ")":
            parentheses = max(0, parentheses - 1)
        elif char == "{" and parentheses == 0:
            if len(stack) >= 1024:
                raise ValueError("diagram CSS nesting exceeds the supported limit of 1024 blocks")
            rule = _CssRule(css, starts[-1], index)
            (stack[-1].children if stack else roots).append(rule)
            nodes.append(rule)
            stack.append(rule)
            starts.append(index + 1)
        elif char == "}" and parentheses == 0:
            if stack:
                stack.pop().end = index
                starts.pop()
            starts[-1] = index + 1
        elif char == ";" and parentheses == 0:
            selector = css[starts[-1] : index].strip()
            if re.match(r"@layer\b", selector, re.IGNORECASE):
                rule = _CssRule(css, starts[-1], index)
                rule.statement = True
                rule.end = index
                (stack[-1].children if stack else roots).append(rule)
                nodes.append(rule)
            starts[-1] = index + 1
    if stack or quote:
        raise ValueError("diagram CSS has an unclosed rule or string")
    for rule in reversed(nodes):
        selector = rule.selector
        if not rule.statement and selector.startswith("@") and not re.match(r"@(?:(?:-webkit-)?keyframes|font-face)\b", selector, re.IGNORECASE):
            rule.group = bool(re.match(r"@(?:media|supports|layer|container)\b", selector, re.IGNORECASE)) or any(
                not child.selector.startswith("@") or child.group or child.statement
                or re.match(r"@(?:(?:-webkit-)?keyframes|font-face)\b", child.selector, re.IGNORECASE) is not None
                for child in rule.children
            )
    return roots


def _css_rule_nodes(rules: list[_CssRule]) -> Iterator[_CssRule]:
    pending = list(reversed(rules))
    while pending:
        rule = pending.pop()
        yield rule
        if rule.group:
            pending.extend(reversed(rule.children))


def _html_css_rules(html: str) -> list[_CssRule]:
    rules: list[_CssRule] = []
    for token, in_svg, body_end, _ in html_tokens(html):
        if (token.group("tag") or "").lower() != "style" or token.group("close"):
            continue
        block = html[token.end() : body_end]
        if in_svg:
            block = CDATA_SECTION_RE.sub(lambda m: m.group(1), block)
        rules.extend(_css_rule_tree(strip_css_comments(block)))
    return rules
