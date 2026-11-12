# SPDX-License-Identifier: MIT
"""Defs packaging, stable slug generation, and referenceable ID namespacing.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import html as html_entities
from pathlib import Path
import re

from .css_rules import RULE_RE, css_escape, css_id_token, decoded_css_url_fragment
from .css_scoper import retarget_root_selector
from .entity_normalizer import decode_xml_references
from .xml_sanitize import CDATA_SECTION_RE, START_TAG_RE, TAG_ATTR_RE, escape_css_for_xml

DEFS_ID_TAGS = (
    "marker", "pattern", "linearGradient", "radialGradient", "filter",
    "clipPath", "mask", "symbol", "g", "path", "rect", "circle", "ellipse",
    "line", "polyline", "polygon", "text", "image", "use",
)
CSS_URL_ATTRIBUTES = {
    "fill", "stroke", "filter", "clip-path", "mask", "cursor", "marker",
    "marker-start", "marker-mid", "marker-end",
}
STYLE_BLOCK_RE = re.compile(
    r"<style\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>(.*?)</style\s*>",
    re.IGNORECASE | re.DOTALL,
)
REFERENCE_REGION_RE = re.compile(
    r"(?P<skip><!\[CDATA\[.*?\]\]>|<script\b.*?</script\s*>)"
    r"|<!--.*?-->|<style\b[^>]*>.*?</style\s*>"
    r"|<[A-Za-z/?!](?:[^>\"']|\"[^\"]*\"|'[^']*')*>",
    re.IGNORECASE | re.DOTALL,
)


def slug_for(path: Path) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-")
    if not slug:
        raise ValueError(f"cannot derive an ID slug from {path.name!r}")
    return f"d-{slug}" if slug[0].isdigit() else slug


def leading_accessibility_end(svg: str, pos: int) -> int:
    token = re.compile(r"<!--.*?-->|<title\b[^>]*>|<desc\b[^>]*>", re.DOTALL | re.IGNORECASE)
    while True:
        start = re.match(r"\s*", svg[pos:])
        next_pos = pos + (start.end() if start else 0)
        opening = token.match(svg, next_pos)
        if opening is None:
            return pos
        if opening.group(0).startswith("<!--"):
            pos = opening.end()
            continue
        name = "title" if opening.group(0).lower().startswith("<title") else "desc"
        endings = re.compile(rf"<!--.*?-->|<!\[CDATA\[.*?\]\]>|</{name}\s*>", re.DOTALL | re.IGNORECASE)
        close = next((m for m in endings.finditer(svg, opening.end()) if m.group(0).startswith("</")), None)
        if close is None:
            return pos
        pos = close.end()


def merge_style_into_defs(svg: str, style_css: str) -> str:
    if not style_css.strip():
        return svg
    style_tag = "<style>\n      " + style_css.strip() + "\n    </style>"
    defs_match = re.search(r"<defs\b[^>]*>", svg, re.IGNORECASE)
    if defs_match:
        insert_at = defs_match.end()
        return svg[:insert_at] + "\n      " + style_tag + svg[insert_at:]
    open_match = re.match(r"<svg\b[^>]*>", svg, re.IGNORECASE)
    assert open_match is not None
    insert_at = leading_accessibility_end(svg, open_match.end())
    return svg[:insert_at] + f"\n  <defs>\n      {style_tag}\n  </defs>" + svg[insert_at:]


def namespace_defs_ids(svg: str, prefix: str) -> str:
    live_svg = re.sub(r"<!\[CDATA\[.*?\]\]>|<!--.*?-->", "", svg, flags=re.DOTALL)
    commented_defs_tags = {
        "marker", "pattern", "lineargradient", "radialgradient", "filter", "clippath", "mask", "symbol"
    }

    def markup_ids(markup: str, allowed: set[str] | None = None) -> set[str]:
        found: set[str] = set()
        for tag in START_TAG_RE.finditer(markup):
            if allowed is not None and tag.group(1).lower() not in allowed:
                continue
            for attr in TAG_ATTR_RE.finditer(tag.group(2)):
                _, name, _, quoted = attr.groups()
                if name == "id" and quoted is not None and quoted[0] in "\"'":
                    found.add(decode_xml_references(quoted[1:-1]))
        return found

    live_defs_tags = {k.lower() for k in DEFS_ID_TAGS}
    live_ids = set().union(*(markup_ids(b, live_defs_tags) for b in re.findall(r"<defs\b[^>]*>(.*?)</defs>", live_svg, re.I | re.S)))
    commented_ids = set().union(*(markup_ids(c, commented_defs_tags) for c in re.findall(r"<!--.*?-->", svg, re.S)))
    unrenamed_live_ids = markup_ids(live_svg) - live_ids
    live_reference_ids = live_ids | (commented_ids - unrenamed_live_ids)
    ids = live_ids | commented_ids
    if not ids:
        return svg

    replacements = {old: html_entities.escape(f"{prefix}-{old}", quote=True) for old in ids}
    live_replacements = {old: replacements[old] for old in live_reference_ids}
    url_ref = re.compile(
        r"(?<![A-Za-z0-9_\\\-\u0080-\U0010ffff])(?i:url)\(\s*(?P<quote>[\"']|&quot;|&apos;|)\s*#\s*(?P<ident>.*?)\s*(?P=quote)\s*\)",
        re.DOTALL,
    )
    raw_url_ref = re.compile(
        r"(?<![A-Za-z0-9_\\\-\u0080-\U0010ffff])(?i:url)\(\s*(?P<quote>[\"']|)\s*#\s*(?P<ident>.*?)\s*(?P=quote)\s*\)",
        re.DOTALL,
    )
    css_string = re.compile(r'''(?:"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*')''', re.DOTALL)

    def rewrite_css_urls(css: str, commented: bool = False) -> str:
        out, pos = [], 0
        while pos < len(css):
            if css[pos] in "\"'":
                lit = css_string.match(css, pos)
                end = lit.end() if lit else len(css)
            elif css.startswith("/*", pos):
                closing = css.find("*/", pos + 2)
                end = closing + 2 if closing >= 0 else len(css)
            else:
                tok = css_id_token(css, pos)
                if tok is not None:
                    _, end = tok
                    if css[pos:end].lower() == "url" and css[end : end + 1] == "(":
                        ref = raw_url_ref.match(css, pos)
                        if ref is not None:
                            out.append(rewrite_raw_url(ref, commented))
                            pos = ref.end()
                            continue
                else:
                    escaped = css_escape(css, pos) if css[pos] == "\\" else None
                    end = escaped[1] if escaped else pos + 1
            out.append(css[pos:end])
            pos = end
        return "".join(out)

    def rewrite_raw_url(match: re.Match[str], commented: bool = False) -> str:
        ident = decoded_css_url_fragment(match.group("ident"))
        if ident not in (ids if commented else live_reference_ids):
            return match.group(0)
        return f"url({match.group('quote')}#{prefix}-{match.group('ident')}{match.group('quote')})"

    def rewrite_url(match: re.Match[str], commented: bool = False) -> str:
        mapping = replacements if commented else live_replacements
        new = mapping.get(decoded_css_url_fragment(decode_xml_references(match.group("ident"))))
        return match.group(0) if new is None else f"url({match.group('quote')}#{prefix}-{match.group('ident')}{match.group('quote')})"

    def rewrite_tag(tag: re.Match[str], commented: bool = False) -> str:
        mapping = replacements if commented else live_replacements
        anim_vals = {"set": {"to"}, "animate": {"from", "to", "values", "by"}}
        target = next((
            decode_xml_references(a.group(4)[1:-1])
            for a in TAG_ATTR_RE.finditer(tag.group(2))
            if a.group(2) == "attributeName" and a.group(4) is not None and a.group(4)[0] in "\"'"
        ), "")
        anim_attrs = anim_vals.get(tag.group(1), set()) if target in CSS_URL_ATTRIBUTES else set()

        def rewrite_css_attribute(raw: str) -> str:
            val = decode_xml_references(re.sub(r"\r\n?|[\n\t]", " ", raw))
            rw = rewrite_css_urls(val, commented)
            if rw == val:
                return raw
            return (
                escape_css_for_xml(rw).replace('"', "&quot;").replace("'", "&apos;")
                .replace("\t", "&#9;").replace("\n", "&#10;").replace("\r", "&#13;")
            )

        def attribute(match: re.Match[str]) -> str:
            sp, name, eq, q = match.groups()
            if q is None or q[0] not in "\"'":
                return match.group(0)
            raw, val = q[1:-1], decode_xml_references(q[1:-1])
            if name == "id" and val in replacements and (
                tag.group(1).lower() in commented_defs_tags if commented
                else val in live_ids and tag.group(1).lower() in live_defs_tags
            ):
                raw = replacements[val]
            elif name.lower() in {"href", "xlink:href"} and val.startswith("#") and val[1:] in mapping:
                raw = "#" + mapping[val[1:]]
            elif name.lower() == "style" or name in anim_attrs:
                raw = rewrite_css_attribute(raw)
            elif name.lower() in CSS_URL_ATTRIBUTES:
                raw = url_ref.sub(lambda r: rewrite_url(r, commented), raw)
            return sp + name + eq + q[0] + raw + q[-1]

        return "<" + tag.group(1) + TAG_ATTR_RE.sub(attribute, tag.group(2)) + tag.group(3) + ">"

    comment_tokens = re.compile(START_TAG_RE.pattern + "|" + url_ref.pattern, re.DOTALL)

    def rewrite_comment_token(match: re.Match[str]) -> str:
        tok = match.group(0)
        t = START_TAG_RE.fullmatch(tok)
        return rewrite_tag(t, commented=True) if t is not None else rewrite_url(url_ref.fullmatch(tok), commented=True)

    def retarget_style_selectors(region: str) -> str:
        style = STYLE_BLOCK_RE.fullmatch(region)
        if style is None:
            return url_ref.sub(rewrite_url, region)

        def retarget(css: str) -> str:
            for old in sorted(live_reference_ids, key=len, reverse=True):
                esc_new = "".join(
                    c if c.isalnum() or c in "_-" or ord(c) >= 128
                    else f"\\{ord(c):x} " if ord(c) < 32 or ord(c) == 127 else "\\" + c
                    for c in f"{prefix}-{old}"
                )
                css = RULE_RE.sub(
                    lambda r, old=old, new=esc_new: retarget_root_selector(r.group(1), old, new) + "{" + r.group(2) + "}",
                    css,
                )
            return rewrite_css_urls(css)

        content = style.group(1)
        parts, pos = [], 0
        for cd in CDATA_SECTION_RE.finditer(content):
            parts.append(escape_css_for_xml(retarget(decode_xml_references(content[pos : cd.start()]))))
            parts.append("<![CDATA[" + retarget(cd.group(1)) + "]]>")
            pos = cd.end()
        parts.append(escape_css_for_xml(retarget(decode_xml_references(content[pos:]))))
        return url_ref.sub(rewrite_url, region[: style.start(1)]) + "".join(parts) + url_ref.sub(rewrite_url, region[style.end(1) :])

    def rewrite(region: re.Match[str]) -> str:
        tok = region.group(0)
        if region.group("skip"):
            return tok
        t = START_TAG_RE.fullmatch(tok)
        if t is not None:
            return rewrite_tag(t)
        if tok.startswith("<!--"):
            return comment_tokens.sub(rewrite_comment_token, tok)
        if tok[:6].lower() == "<style":
            return retarget_style_selectors(tok)
        return url_ref.sub(rewrite_url, tok)

    return REFERENCE_REGION_RE.sub(rewrite, svg)
