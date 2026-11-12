# SPDX-License-Identifier: MIT
"""Style parsing, label normalization, and geometry conversion for draw.io cells.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import html
import math
import re
from xml.etree import ElementTree as ET

from .models import _fail

BR_RE = re.compile(r"<br\s*/?>|</p\s*>|</div\s*>", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_TAG = (
    "a|b|blockquote|br|code|del|div|em|font|h[1-6]|hr|i|img|ins|li|mark|ol|p|pre|"
    "s|small|span|strike|strong|sub|sup|table|tbody|td|th|thead|tr|u|ul|wbr"
)
TAG_RE = re.compile(
    rf"</?(?:{_HTML_TAG})\b[^>]*>|</?[A-Za-z][\w-]*:[\w:-]*[^>]*>",
    re.IGNORECASE,
)


def parse_style(style: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not style:
        return out
    for part in style.split(";"):
        part = part.strip()
        if not part:
            continue
        key, sep, value = part.partition("=")
        out[key.strip()] = value.strip() if sep else "1"
    return out


def clean_label(value: str | None, *, is_html: bool = False) -> str:
    """Flatten HTML-enabled cells; preserve angle brackets in plain labels."""
    if not value:
        return ""
    text = value
    if is_html:
        text = HTML_COMMENT_RE.sub("", text)
        text = BR_RE.sub("\n", text)
        text = TAG_RE.sub("", text)
        text = html.unescape(text)
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln).strip()


def _num(geom: ET.Element | None, key: str) -> float:
    if geom is None:
        return 0.0
    try:
        value = float(geom.get(key, "0") or 0)
    except (OverflowError, ValueError):
        return 0.0
    if not math.isfinite(value):
        _fail(f"invalid geometry: {key} must be finite")
    return value
