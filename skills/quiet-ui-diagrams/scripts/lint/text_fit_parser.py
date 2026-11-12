# SPDX-License-Identifier: MIT
"""HTML/SVG parser for collecting text lines and background rects in paint order.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

from html.parser import HTMLParser

from .css_rules import declaring_css_subjects, matches_subject, unstatic_css_subjects
from .models import PAINT_PROPERTIES
from .viewbox_check import child_offset, painted_points, svg_length


class TextFitParser(HTMLParser):
    def __init__(self, source: str, restyles_fn, zero_alpha_fn, inline_paint_fn, inline_style_fn) -> None:
        super().__init__(convert_charrefs=True)
        self.svgs: list[dict[str, object]] = []
        self._css_subjects = unstatic_css_subjects(source)
        self._text_subjects = declaring_css_subjects(source, restyles_fn)
        self._paint_subjects = declaring_css_subjects(source, PAINT_PROPERTIES.__contains__)
        self._restyles = restyles_fn
        self._zero_alpha = zero_alpha_fn
        self._inline_paint = inline_paint_fn
        self._inline_style = inline_style_fn
        self._frames: list[
            tuple[str, tuple[float, float] | None, dict[str, str] | None, dict[str, str] | None]
        ] = []
        self._text: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        data = {key.casefold(): value or "" for key, value in attrs}
        if not self._frames:
            if tag == "svg":
                self.svgs.append({"attrs": data, "rects": [], "lines": [], "papers": set()})
                style, paint = self._inherit(tag, data, {}, {})
                self._frames.append((tag, (0.0, 0.0), style, paint))
            return
        _, parent_offset, parent_style, parent_paint = self._frames[-1]
        offset = child_offset(tag, data, parent_offset, self._css_subjects)
        style, paint = self._inherit(tag, data, parent_style, parent_paint)
        self._frames.append((tag, offset, style, paint))
        svg = self.svgs[-1]
        if offset is None:
            if tag in {"text", "tspan"} and self._text is not None:
                self._text["static"] = False
            return
        if tag == "rect" and self._text is None:
            fill: str | None = None
            stroked = False
            if paint is not None:
                fill = paint.get("fill", "black")
                stroke = paint.get("stroke", "none")
                stroked = stroke not in {"none", "transparent"} and paint.get("stroke-width") != "0"
                faded = [
                    self._zero_alpha(v)
                    for v in (
                        paint["opacity"],
                        fill,
                        paint.get("fill-opacity", "1"),
                        stroke,
                        paint.get("stroke-opacity", "1"),
                    )
                ]
                if None in faded:
                    fill, stroked = None, False
                else:
                    if faded[0] or faded[1] or faded[2]:
                        fill = "none"
                    stroked = stroked and not (faded[0] or faded[3] or faded[4])
                if data.get("width", "").strip() == "100%":
                    papers = svg["papers"]
                    assert isinstance(papers, set)
                    papers.add(fill)
            points = painted_points(tag, data)
            if points and (fill not in {"none", "transparent"} or stroked):
                (x0, y0), (x1, y1) = points
                rects = svg["rects"]
                assert isinstance(rects, list)
                rects.append(
                    (x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1], fill, stroked)
                )
        elif tag == "text" and self._text is None:
            x, y = svg_length(data, "x"), svg_length(data, "y")
            shifted = any(n in data for n in ("dx", "dy", "rotate", "textlength"))
            self._text = {"static": x is not None and y is not None and not shifted, "lines": []}
            if x is not None and y is not None:
                self._start_line(x + offset[0], y + offset[1], style)
        elif tag == "tspan" and self._text is not None:
            if any(n in data for n in ("dx", "rotate", "textlength")):
                self._text["static"] = False
            x = svg_length(data, "x")
            lines = self._text["lines"]
            assert isinstance(lines, list)
            if "x" in data:
                if x is None:
                    self._text["static"] = False
                    return
                dy = svg_length(data, "dy", 0.0)
                y = svg_length(data, "y")
                prev_y = lines[-1]["y"] if lines else 0.0
                line_y = (y + offset[1]) if y is not None else prev_y + (dy or 0.0)
                self._start_line(x + offset[0], line_y, style)
            elif "y" in data or "dy" in data:
                self._text["static"] = False

    def _inherit(
        self,
        tag: str,
        data: dict[str, str],
        parent_style: dict[str, str] | None,
        parent_paint: dict[str, str] | None,
    ) -> tuple[dict[str, str] | None, dict[str, str] | None]:
        style: dict[str, str] | None = None
        if parent_style is not None and not any(
            matches_subject(tag, data, s) for s in self._text_subjects
        ):
            own = self._inline_style(data)
            style = None if "" in own.values() else {**parent_style, **own}
        paint: dict[str, str] | None = None
        if parent_paint is not None and not any(
            matches_subject(tag, data, s) for s in self._paint_subjects
        ):
            own = self._inline_paint(data)
            hidden = parent_paint.get("opacity") == "0" or self._zero_alpha(own.get("opacity", "1"))
            paint = {**parent_paint, **own, "opacity": "0" if hidden else "1"}
            if hidden is None:
                paint = None
        return style, paint

    def _start_line(self, x: float, y: float, style: dict[str, str] | None) -> None:
        assert self._text is not None
        lines = self._text["lines"]
        assert isinstance(lines, list)
        rects = self.svgs[-1]["rects"]
        assert isinstance(rects, list)
        anchor = (style or {}).get("text-anchor", "start").strip().casefold()
        lines.append({"x": x, "y": y, "anchor": anchor, "runs": [], "rects": len(rects)})

    def handle_data(self, data: str) -> None:
        if self._text is None or not self._frames:
            return
        lines = self._text["lines"]
        assert isinstance(lines, list)
        if not lines:
            return
        style = self._frames[-1][2]
        if style is None:
            self._text["static"] = False
            return
        lines[-1]["runs"].append((data, style))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        for index in range(len(self._frames) - 1, -1, -1):
            if self._frames[index][0] == tag:
                del self._frames[index:]
                break
        if tag == "text" and self._text is not None:
            if self._text["static"] and self.svgs:
                svg_lines = self.svgs[-1]["lines"]
                assert isinstance(svg_lines, list)
                svg_lines.extend(self._text["lines"])
            self._text = None
