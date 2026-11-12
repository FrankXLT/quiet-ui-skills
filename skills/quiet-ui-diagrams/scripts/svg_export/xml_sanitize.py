# SPDX-License-Identifier: MIT
"""XML sanitization, comment rewriting, and SVG root attribute fixing.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import math
import re
from typing import Callable, Iterator

from .entity_normalizer import decode_xml_references, normalize_html_entities

XML_OPAQUE_OPEN_RE = re.compile(r"<!--|<!\[CDATA\[")
START_TAG_RE = re.compile(
    r"<([A-Za-z][\w:.-]*)"
    r"((?:\s+[^\s\"'<>/=]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*)"
    r"(\s*/?)>"
)
TAG_ATTR_RE = re.compile(
    r"(\s+)([^\s\"'<>/=]+)(?:(\s*=\s*)(\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?"
)
SVG_TAG_RE = re.compile(
    r"<svg(?=[\s/>])(?:[^>\"']|\"[^\"]*\"|'[^']*')*>|</svg\s*>", re.IGNORECASE
)
HTML_TOKEN_RE = re.compile(
    r"<!--.*?(?:-->|$)|<!\[CDATA\[.*?(?:\]\]>|$)|"
    r"<(?P<close>/)?(?P<tag>[A-Za-z][^\s/>]*)"
    r"(?:[^>\"']|\"[^\"]*\"|'[^']*')*>",
    re.IGNORECASE | re.DOTALL,
)
CDATA_SECTION_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)


def html_tokens(source: str) -> Iterator[tuple[re.Match[str], bool, int, int]]:
    contexts: list[str] = []
    pos = 0
    while token := HTML_TOKEN_RE.search(source, pos):
        name = (token.group("tag") or "").lower()
        in_svg = bool(contexts and contexts[-1] == "svg")
        body_end = end = token.end()
        self_closing = token.group(0).endswith("/>")
        text_element = name in {"script", "style"} or (
            not in_svg
            and name in {"textarea", "title", "xmp", "iframe", "noembed", "noframes", "noscript", "plaintext"}
        )
        if name and not token.group("close") and text_element and not (in_svg and self_closing):
            closing = (
                None
                if name == "plaintext"
                else re.compile(
                    r"</" + name + r"(?=[\s/>])(?:[^>\"']|\"[^\"]*\"|'[^']*')*>",
                    re.IGNORECASE,
                ).search(source, end)
            )
            body_end = closing.start() if closing else len(source)
            end = closing.end() if closing else len(source)
        elif name in {"svg", "foreignobject", "desc", "title"}:
            if token.group("close"):
                for index in range(len(contexts) - 1, -1, -1):
                    if contexts[index] == name:
                        del contexts[index:]
                        break
            elif not self_closing and (name == "svg" or in_svg):
                contexts.append(name)
        yield token, in_svg, body_end, end
        pos = end


def mask_opaque_html(source: str, *, styles: bool = False) -> str:
    out: list[str] = []
    pos = 0
    for token, _, _, end in html_tokens(source):
        out.append(source[pos : token.start()])
        name = (token.group("tag") or "").lower()
        if not name or (end > token.end() and (styles or name != "style")):
            out.append(" " * (end - token.start()))
        else:
            suffix = "/>" if token.group(0).endswith("/>") else ">"
            attr_start = token.end("tag")
            out.append(source[token.start() : attr_start])
            out.append(" " * (token.end() - len(suffix) - attr_start) + suffix)
            out.append(source[token.end() : end])
        pos = end
    out.append(source[pos:])
    return "".join(out)


def extract_first_svg(html: str) -> str:
    start = None
    depth = 0
    for tag in SVG_TAG_RE.finditer(mask_opaque_html(html, styles=True)):
        token = tag.group(0)
        if token.startswith("</"):
            if start is None:
                continue
            depth -= 1
            if depth == 0:
                return html[start : tag.end()]
        elif not token.endswith("/>"):
            if start is None:
                start = tag.start()
            depth += 1
    raise ValueError("no <svg> block found in source")


def xml_safe_comments(svg: str) -> str:
    out: list[str] = []
    pos = 0
    while True:
        opener = XML_OPAQUE_OPEN_RE.search(svg, pos)
        if opener is None:
            out.append(svg[pos:])
            break
        out.append(svg[pos : opener.start()])
        if opener.group(0) == "<!--":
            close_at = svg.find("-->", opener.end())
            if close_at == -1:
                out.append(svg[opener.start() :])
                break
            body = svg[opener.end() : close_at]
            if body.startswith((">", "->")) or "--!>" in body:
                raise ValueError("exported SVG has a comment a browser closes early")
            while "--" in body:
                body = body.replace("--", "- -")
            if body.endswith("-"):
                body += " "
            out.append("<!--" + body + "-->")
            pos = close_at + 3
        else:
            close_at = svg.find("]]>", opener.end())
            stop = len(svg) if close_at == -1 else close_at + 3
            out.append(svg[opener.start() : stop])
            pos = stop
            if close_at == -1:
                break
    return "".join(out)


def _xml_start_tag(match: re.Match[str]) -> str:
    def attr(m: re.Match[str]) -> str:
        space, name, equals, value = m.groups()
        if value is None:
            return f'{space}{name}=""'
        if value[0] in "\"'":
            return m.group(0)
        return f'{space}{name}{equals}"{value}"'

    name, attrs, end = match.groups()
    return f"<{name}{TAG_ATTR_RE.sub(attr, attrs)}{end}>"


def _rewrite_start_tags(svg: str, transform: Callable[[re.Match[str]], str]) -> str:
    out: list[str] = []
    pos = 0
    while True:
        opener = XML_OPAQUE_OPEN_RE.search(svg, pos)
        text_end = opener.start() if opener else len(svg)
        out.append(START_TAG_RE.sub(transform, svg[pos:text_end]))
        if opener is None:
            break
        closer = "-->" if opener.group(0) == "<!--" else "]]>"
        close_at = svg.find(closer, opener.end())
        stop = len(svg) if close_at == -1 else close_at + len(closer)
        out.append(svg[opener.start() : stop])
        pos = stop
        if close_at == -1:
            break
    return "".join(out)


def xmlify_attributes(svg: str) -> str:
    return _rewrite_start_tags(svg, _xml_start_tag)


def ensure_xmlns(svg: str) -> str:
    opening = START_TAG_RE.match(svg)
    if opening is None or opening.group(1) != "svg":
        raise ValueError("cannot identify SVG root namespace")
    for attr in TAG_ATTR_RE.finditer(opening.group(2)):
        if attr.group(2) == "xmlns":
            val = attr.group(4)
            if val is not None and decode_xml_references(val[1:-1]) == "http://www.w3.org/2000/svg":
                return svg
            raise ValueError("SVG root namespace must be http://www.w3.org/2000/svg")
    return re.sub(r"<svg\b", '<svg xmlns="http://www.w3.org/2000/svg"', svg, count=1)


def ensure_viewbox(svg: str) -> None:
    opening = START_TAG_RE.match(svg)
    raw = next(
        (
            attr.group(4)
            for attr in TAG_ATTR_RE.finditer(opening.group(2))
            if attr.group(2) == "viewBox"
        ),
        None,
    ) if opening is not None and opening.group(1).lower() == "svg" else None
    if raw is None:
        raise ValueError("SVG is missing a viewBox; refuse to guess")
    val = decode_xml_references(raw[1:-1] if raw[0] in "\"'" else raw).strip(" \t\r\n")
    number = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    separator = r"(?:[ \t\r\n]*,[ \t\r\n]*|[ \t\r\n]+)"
    parsed = re.fullmatch(separator.join([f"({number})"] * 4), val)
    if parsed is None:
        raise ValueError("SVG viewBox must contain four finite numbers")
    coords = [float(t) for t in parsed.groups()]
    if not all(math.isfinite(t) for t in coords) or min(coords[2:]) <= 0:
        raise ValueError("SVG viewBox must be finite with positive width and height")


def set_root_id(svg: str, root_id: str) -> str:
    opening = START_TAG_RE.match(svg)
    assert opening is not None
    name, attrs, end = opening.groups()
    replaced = False

    def replace_attr(attr: re.Match[str]) -> str:
        nonlocal replaced
        if attr.group(2) != "id":
            return attr.group(0)
        replaced = True
        return f'{attr.group(1)}id="{root_id}"'

    attrs = TAG_ATTR_RE.sub(replace_attr, attrs)
    if not replaced:
        attrs += f' id="{root_id}"'
    return f"<{name}{attrs}{end}>" + svg[opening.end() :]


def escape_css_for_xml(css: str) -> str:
    return css.replace("&", "&amp;").replace("<", "&lt;")
