# SPDX-License-Identifier: MIT
"""Path decomposition, Bezier curve evaluation, and elliptical arc tessellation.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import math
from typing import Iterator

from .models import (
    ATTR_RE,
    CHORD_LENGTH,
    DEFINITION_TAGS,
    PATH_ARITY,
    PATH_COMMAND_RE,
    PATH_END_RE,
    PATH_FLAG_RE,
    PATH_NUMBER_RE,
    TAG_RE,
    TRANSLATE_RE,
    Offset,
    Segment,
)


def attribute(attrs: str, name: str) -> str | None:
    for match in ATTR_RE.finditer(attrs):
        if match.group(1) == name:
            return match.group(2) if match.group(2) is not None else match.group(3)
    return None


def number(attrs: str, name: str) -> float | None:
    value = attribute(attrs, name)
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def chord_count(points: list[tuple[float, float]]) -> int:
    length = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
    return max(4, min(256, math.ceil(length / CHORD_LENGTH)))


def bezier(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    steps = chord_count(points)
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        level = points
        while len(level) > 1:
            level = [
                (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                for a, b in zip(level, level[1:])
            ]
        out.append(level[0])
    return out


def arc(
    start: tuple[float, float],
    rx: float,
    ry: float,
    rotation: float,
    large: float,
    sweep: float,
    end: tuple[float, float],
) -> list[tuple[float, float]]:
    (x1, y1), (x2, y2) = start, end
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0 or start == end:
        return [end]
    phi = math.radians(rotation)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    hx, hy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cos_p * hx + sin_p * hy, -sin_p * hx + cos_p * hy
    scale = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if scale > 1:
        rx, ry = rx * math.sqrt(scale), ry * math.sqrt(scale)
    denominator = (rx * y1p) ** 2 + (ry * x1p) ** 2
    numerator = (rx * ry) ** 2 - denominator
    root = math.sqrt(max(0.0, numerator / denominator)) if denominator else 0.0
    if large == sweep:
        root = -root
    cxp, cyp = root * rx * y1p / ry, -root * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2
    ux, uy = (x1p - cxp) / rx, (y1p - cyp) / ry
    vx, vy = (-x1p - cxp) / rx, (-y1p - cyp) / ry
    theta = math.atan2(uy, ux)
    delta = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi
    steps = max(4, min(256, math.ceil(abs(delta) * max(rx, ry) / CHORD_LENGTH)))
    out = []
    for i in range(1, steps + 1):
        angle = theta + delta * i / steps
        ex, ey = rx * math.cos(angle), ry * math.sin(angle)
        out.append((cos_p * ex - sin_p * ey + cx, sin_p * ex + cos_p * ey + cy))
    out[-1] = end
    return out


def path_segments(d: str) -> list[Segment] | None:
    segments: list[Segment] = []
    x = y = start_x = start_y = 0.0
    previous_control: tuple[str, float, float] | None = None
    command = ""
    pos = 0
    while not PATH_END_RE.match(d, pos):
        match = PATH_COMMAND_RE.match(d, pos)
        if match:
            command, pos = match.group(1), match.end()
            if command in "Zz":
                if (x, y) != (start_x, start_y):
                    segments.append(("line", x, y, start_x, start_y))
                x, y = start_x, start_y
                continue
        elif not command or command in "Zz":
            return None
        upper = command.upper()
        args: list[float] = []
        for slot in range(PATH_ARITY[upper]):
            pattern = PATH_FLAG_RE if upper == "A" and slot in (3, 4) else PATH_NUMBER_RE
            match = pattern.match(d, pos)
            if not match:
                return None
            args.append(float(match.group(1)))
            pos = match.end()
        relative = command.islower()
        ox, oy = (x, y) if relative else (0.0, 0.0)
        if upper == "H":
            nx, ny = args[0] + ox, y
        elif upper == "V":
            nx, ny = x, args[0] + oy
        else:
            nx, ny = args[-2] + ox, args[-1] + oy
        if upper == "M":
            x, y = start_x, start_y = nx, ny
            command = "l" if relative else "L"
            previous_control = None
            continue
        if upper in "LHV":
            segments.append(("line", x, y, nx, ny))
            previous_control = None
        else:
            pairs = [(args[i] + ox, args[i + 1] + oy) for i in range(0, len(args) - 1, 2)]
            if upper in "ST":
                family = "C" if upper == "S" else "Q"
                if previous_control and previous_control[0] == family:
                    reflected = (2 * x - previous_control[1], 2 * y - previous_control[2])
                else:
                    reflected = (x, y)
                pairs = [reflected] + pairs
            if upper == "A":
                points = arc((x, y), args[0], args[1], args[2], args[3], args[4], (nx, ny))
                previous_control = None
            else:
                points = bezier([(x, y)] + pairs)
                family = "C" if upper in "CS" else "Q"
                previous_control = (family, pairs[-2][0], pairs[-2][1])
            px, py = x, y
            for qx, qy in points:
                segments.append(("curve", px, py, qx, qy))
                px, py = qx, qy
        x, y = nx, ny
    return segments


def translation(attrs: str) -> Offset | None:
    transform = attribute(attrs, "transform")
    if transform is None:
        return 0.0, 0.0
    match = TRANSLATE_RE.match(transform)
    if not match:
        return None
    return float(match.group(1)), float(match.group(2) or 0.0)


def shapes(source: str) -> Iterator[tuple[str, str, int, Offset | None]]:
    stack: list[Offset | None] = []
    containers: list[str] = []
    for match in TAG_RE.finditer(source):
        if match.group("tag") is None:
            continue
        tag, attrs = match.group("tag").lower(), match.group("attrs")
        if tag in {"g", "svg"} or tag in DEFINITION_TAGS:
            if match.group("close"):
                if stack:
                    stack.pop()
                    containers.pop()
            elif not match.group("empty"):
                nested_svg = tag == "svg" and bool(stack)
                stack.append(None if nested_svg else translation(attrs))
                containers.append(tag)
            continue
        if any(container in DEFINITION_TAGS for container in containers):
            continue
        frame: Offset | None = (0.0, 0.0)
        for step in stack + [translation(attrs)]:
            if step is None or frame is None:
                frame = None
                break
            frame = (frame[0] + step[0], frame[1] + step[1])
        yield tag, attrs, match.start(), frame


def shifted(segments: list[Segment], frame: Offset) -> list[Segment]:
    dx, dy = frame
    return [(kind, x1 + dx, y1 + dy, x2 + dx, y2 + dy) for kind, x1, y1, x2, y2 in segments]


def bounds(segments: list[Segment], pad: float) -> tuple[float, float, float, float]:
    xs = [v for _, x1, _, x2, _ in segments for v in (x1, x2)]
    ys = [v for _, _, y1, _, y2 in segments for v in (y1, y2)]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def distance_to_segment(px: float, py: float, segment: Segment) -> float:
    _, x1, y1, x2, y2 = segment
    dx, dy = x2 - x1, y2 - y1
    length_sq = dx * dx + dy * dy
    t = 0.0 if not length_sq else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / length_sq))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
