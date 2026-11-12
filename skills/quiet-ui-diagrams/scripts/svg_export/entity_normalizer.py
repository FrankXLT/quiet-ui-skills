# SPDX-License-Identifier: MIT
"""HTML entity decoding and XML character reference normalization.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import html as html_entities
import re

XML_REFERENCE_RE = re.compile(r"&(?:(amp|lt|gt|quot|apos);|#[0-9]+;?|#[xX][0-9A-Fa-f]+;?)")
XML_NAMED = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}
LEGACY_ENTITY_NAMES = tuple(
    name for name in html_entities.entities.html5 if not name.endswith(";")
)


def decode_xml_references(value: str) -> str:
    return XML_REFERENCE_RE.sub(
        lambda m: XML_NAMED[m.group(1)] if m.group(1) else html_entities.unescape(m.group(0)),
        value,
    )


def normalize_html_entities(svg: str) -> str:
    opaque = re.compile(
        r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|"
        r"(?P<opening><(?P<tag>style|script)\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>)"
        r".*?</(?P=tag)\s*>",
        re.DOTALL | re.IGNORECASE,
    )
    references = re.compile(
        r"&(?:(?P<numeric>#[xX][0-9A-Fa-f]+;?|#[0-9]+;?)|[A-Za-z][A-Za-z0-9]+;|(?P<legacy>"
        + "|".join(sorted((re.escape(n) for n in LEGACY_ENTITY_NAMES), key=len, reverse=True))
        + r"))"
    )
    tag = re.compile(r"<[A-Za-z/!?](?:[^>\"']|\"[^\"]*\"|'[^']*')*>")

    def replace_entity(match: re.Match[str], in_attribute: bool = False) -> str:
        orig = match.group(0)
        if orig in ("&amp;", "&lt;", "&gt;", "&apos;", "&quot;"):
            return orig
        if match.group("numeric") is not None:
            num = orig[2:].rstrip(";")
            hexadecimal = num.startswith(("x", "X"))
            digits = (num[1:] if hexadecimal else num).lstrip("0") or "0"
            codepoint = int(digits, 16 if hexadecimal else 10) if len(digits) <= 8 else 0x110000
            if codepoint == 0 or 0xD800 <= codepoint <= 0xDFFF or codepoint > 0x10FFFF:
                decoded = "\ufffd"
            elif 0x80 <= codepoint <= 0x9F:
                decoded = html_entities.unescape(f"&#{codepoint};")
            else:
                decoded = chr(codepoint)
        elif match.group("legacy") is not None:
            following = match.string[match.end() : match.end() + 1]
            if in_attribute and (following == "=" or following.isalnum()):
                return orig
            decoded = html_entities.entities.html5[match.group("legacy")]
        else:
            decoded = html_entities.entities.html5.get(orig[1:])
        if decoded is None:
            return orig
        return (
            html_entities.escape(decoded, quote=True)
            .replace("\t", "&#9;")
            .replace("\n", "&#10;")
            .replace("\r", "&#13;")
        )

    bare_amp = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#[0-9]+|#[xX][0-9A-Fa-f]+);)")

    def clean_bare_amps(text: str) -> str:
        return bare_amp.sub("&amp;", text)

    def normalize_region(region: str) -> str:
        parts: list[str] = []
        cursor = 0
        for tok in tag.finditer(region):
            parts.append(clean_bare_amps(references.sub(replace_entity, region[cursor : tok.start()])))
            parts.append(clean_bare_amps(references.sub(lambda m: replace_entity(m, True), tok.group(0))))
            cursor = tok.end()
        parts.append(clean_bare_amps(references.sub(replace_entity, region[cursor:])))
        return "".join(parts)

    out: list[str] = []
    pos = 0
    for match in opaque.finditer(svg):
        out.append(normalize_region(svg[pos : match.start()]))
        opening = match.group("opening")
        if opening is not None:
            norm_open = clean_bare_amps(references.sub(lambda m: replace_entity(m, True), opening))
            out.append(norm_open + match.group(0)[len(opening):])
        else:
            out.append(match.group(0))
        pos = match.end()
    out.append(normalize_region(svg[pos:]))
    return "".join(out)
