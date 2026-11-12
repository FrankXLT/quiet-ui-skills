# SPDX-License-Identifier: MIT
"""Main geometry checker verifying paint order, containment, and node collisions.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from pathlib import Path

from .connectors import check_connectors
from .models import (
    EPSILON,
    MASK_MAX_H,
    MASK_MAX_W,
    MASK_MIN_H,
    MASK_MIN_W,
    NODE_MIN_H,
    NODE_MIN_W,
    Rect,
)
from .path_math import number, shapes


def parse_rects(source: str) -> list[Rect]:
    rects: list[Rect] = []
    for tag, attrs, start, frame in shapes(source):
        if tag != "rect" or frame is None:
            continue
        x, y, w, h = (number(attrs, key) for key in ("x", "y", "width", "height"))
        if None in (x, y, w, h):
            continue
        rects.append(
            Rect(
                x + frame[0],
                y + frame[1],
                w,
                h,
                source.count("\n", 0, start) + 1,
                start,
            )
        )
    return rects


def overlap(a: Rect, b: Rect) -> tuple[float, float]:
    return (
        min(a.right, b.right) - max(a.x, b.x),
        min(a.bottom, b.bottom) - max(a.y, b.y),
    )


def contained(inner: Rect, outer: Rect) -> bool:
    return (
        inner.x >= outer.x - EPSILON
        and inner.y >= outer.y - EPSILON
        and inner.right <= outer.right + EPSILON
        and inner.bottom <= outer.bottom + EPSILON
    )


def check(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    rects = parse_rects(source)
    nodes = [r for r in rects if r.w >= NODE_MIN_W and r.h >= NODE_MIN_H]
    masks = [
        r
        for r in rects
        if MASK_MIN_W <= r.w <= MASK_MAX_W and MASK_MIN_H <= r.h <= MASK_MAX_H
    ]

    findings: list[str] = []
    for mask in masks:
        for node in nodes:
            if node.offset <= mask.offset:
                continue
            dx, dy = overlap(mask, node)
            if dx <= 1.0 or dy <= 1.0 or contained(mask, node):
                continue
            findings.append(
                f"{path.name}:{mask.line}: label mask {mask} is clipped by node "
                f"{node} declared later at line {node.line} (overlap {dx:g}x{dy:g}px)"
                f" - move the label onto a free segment of its connector"
            )
            break
    findings.extend(check_connectors(path, source))
    return findings
