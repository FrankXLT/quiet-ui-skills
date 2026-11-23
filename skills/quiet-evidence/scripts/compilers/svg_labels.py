# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — SVG Knockout Labels, Text Halos, Glyphs & Pill HTML Helpers."""

from __future__ import annotations

import unicodedata
from typing import Any

from .tokens_and_scales import _SUB_TOKEN_RE, esc, format_math_svg, format_math_unicode


def visual_char_units(text: str) -> float:
    """Measure visual glyph units: 0 for combining marks, 1.75 for wide CJK, 1.0 otherwise."""
    units = 0.0
    for ch in str(text or ""):
        if unicodedata.combining(ch) or unicodedata.category(ch) in {"Mn", "Me", "Cf"}:
            continue
        units += 1.75 if unicodedata.east_asian_width(ch) in {"W", "F"} else 1.0
    return units


def render_pill_html(
    text: str,
    variant: str = "tag",
    state: str | None = None,
    extra_cls: str = "",
    tag: str = "span",
    attrs: str = "",
) -> str:
    """Emit a 4-variant Quiet UI .va-pill HTML element with atomic bracket-free content."""
    clean_txt = str(text).strip()
    if clean_txt.startswith("[") and clean_txt.endswith("]"):
        clean_txt = clean_txt[1:-1].strip()
    cls_str = f"va-pill {extra_cls}".strip() if extra_cls else "va-pill"
    st_attr = f' data-state="{esc(state)}"' if state else ""
    extra = f" {attrs.strip()}" if attrs.strip() else ""
    type_attr = ' type="button"' if tag == "button" and "type=" not in extra else ""
    return f'<{tag}{type_attr} class="{esc(cls_str)}" data-variant="{esc(variant)}"{st_attr}{extra}>{esc(clean_txt)}</{tag}>'


def halo_text(
    x: float,
    y: float,
    text: str,
    anchor: str = "start",
    size: float = 11.5,
    weight: str = "500",
    fill: str = "var(--text-primary)",
    font: str = "var(--font-mono)",
    halo: bool = True,
    cls: str = "",
    attrs: str = "",
    math: bool = False,
    rotate_deg: float | None = None,
    stroke_width: float = 3.2,
    dominant_baseline: str | None = None,
) -> str:
    """Emit SVG <text> with paint-order stroke halo, optional rotation, and >= 11px floor."""
    classes = " ".join(part for part in (cls, "va-svg-halo-text" if halo else "") if part)
    cls_attr = f' class="{esc(classes)}"' if classes else ""
    halo_attrs = (
        f' paint-order="stroke fill" stroke="var(--bg-surface)" stroke-width="{stroke_width:.1f}" stroke-linejoin="round"'
        if halo else ""
    )
    rot_attr = f' transform="rotate({rotate_deg:.2f} {x:.1f} {y:.1f})"' if rotate_deg is not None else ""
    base_attr = f' dominant-baseline="{esc(dominant_baseline)}"' if dominant_baseline else ""
    extra = f" {attrs.strip()}" if attrs.strip() else ""
    body = format_math_svg(text, size * 0.78) if math else esc(text)
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{font}" font-size="{size:.1f}" font-weight="{weight}" '
        f'fill="{fill}"{cls_attr}{halo_attrs}{rot_attr}{base_attr}{extra}>{body}</text>'
    )


def svg_knockout_label(
    x: float,
    y: float,
    text: str,
    anchor: str = "middle",
    size: float = 11.5,
    weight: str = "600",
    fill: str = "var(--text-primary)",
    surface_fill: str = "var(--bg-surface)",
    x_bounds: tuple[float, float] = (4.0, 716.0),
    cls: str = "",
    attrs: str = "",
    math: bool = True,
) -> str:
    """Emit borderless unstroked canvas-matched knock-out mask behind SVG <text>."""
    plain = format_math_unicode(text) if math else str(text)
    vis = _SUB_TOKEN_RE.sub(r"\1\2", plain) if math else plain
    w = max(28.0, visual_char_units(vis) * (size * 0.63) + 10.0)
    rx0 = x - w if anchor == "end" else (x - w / 2.0 if anchor == "middle" else x)
    rx0 = max(x_bounds[0], min(x_bounds[1] - w, rx0))
    tx = rx0 + w / 2.0
    extra = f" {attrs.strip()}" if attrs.strip() else ""
    mask_rect = (
        f'<rect class="qe-svg-knockout-bg" x="{rx0:.1f}" y="{y - 12.5:.1f}" '
        f'width="{w:.1f}" height="17.0" rx="2" fill="{surface_fill}" stroke="none"/>'
    )
    txt = halo_text(tx, y, text, anchor="middle", size=size, weight=weight, fill=fill, halo=False, cls=cls, math=math)
    return f'<g class="qe-svg-knockout"{extra}>{mask_rect}{txt}</g>'


def render_marker(cx: float, cy: float, glyph: str, size: float, stroke: str, fill: str) -> str:
    """Emit discrete epistemic geometric marker glyph for measured points."""
    r = size / 2.0
    if glyph == "square":
        return f'<rect data-role="marker" x="{cx - r:.1f}" y="{cy - r:.1f}" width="{size:.1f}" height="{size:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    if glyph == "triangle":
        pts = f"{cx:.1f},{cy - r - 0.8:.1f} {cx + r + 0.6:.1f},{cy + r:.1f} {cx - r - 0.6:.1f},{cy + r:.1f}"
        return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    if glyph == "diamond":
        pts = f"{cx:.1f},{cy - r - 0.8:.1f} {cx + r + 0.8:.1f},{cy:.1f} {cx:.1f},{cy + r + 0.8:.1f} {cx - r - 0.8:.1f},{cy:.1f}"
        return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def avoid_label_overlaps(
    items: list[dict[str, Any]],
    min_y: float = 16.0,
    max_y: float = 340.0,
    step_y: float = 19.0,
) -> list[dict[str, Any]]:
    """Nudge floating label boxes vertically to guarantee 0 text-on-text overlaps."""
    placed: list[tuple[float, float, float, float]] = []
    out: list[dict[str, Any]] = []
    for item in items:
        x, y = float(item["x"]), float(item["y"])
        w = float(item.get("w", max(44.0, visual_char_units(format_math_unicode(item.get("text", ""))) * 7.5 + 14.0)))
        h = float(item.get("h", 17.0))
        anchor = item.get("anchor", "start")
        x0 = x - w if anchor == "end" else (x - w / 2.0 if anchor == "middle" else x)
        x1 = x0 + w

        def _collides(cand_y: float) -> bool:
            y0, y1 = cand_y - h, cand_y + 4.0
            return any(not (x1 + 4.0 < px0 or x0 - 4.0 > px1 or y1 + 3.0 < py0 or y0 - 3.0 > py1) for px0, py0, px1, py1 in placed)

        best_y = y
        if _collides(best_y):
            for k in range(1, 16):
                for sign in (-1, 1):
                    cand = y + sign * k * step_y
                    if min_y <= cand <= max_y and not _collides(cand):
                        best_y = cand
                        break
                else:
                    continue
                break
        placed.append((x0, best_y - h, x1, best_y + 4.0))
        out.append({**item, "y": best_y})
    return out
