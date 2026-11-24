# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 4 (Analytical, Spectral, Waterfall & Dumbbell Plots)."""

from __future__ import annotations

import json
import math
import zlib
from typing import Any

from .civic_bars_and_slope import compile_dual_slopegraph, compile_paired_subgroup_bars
from .civic_maps_and_dumbbells import compile_arrow_dumbbell, compile_us_hex_tile_map
from .civic_matrix_and_export import compile_diverging_matrix
from .comparison_plots import compile_dumbbell, compile_forest, compile_stacked_bar, compile_waterfall
from .echarts_adapter import build_echarts_payload, render_echarts_toggle_bar
from .sankey_and_strip import compile_sankey
from .schedule_and_heatmap import compile_gantt, compile_heatmap
from .plot_helpers import (
    DASH_RE as _DASH_RE,
    STYLE_DASHES as _STYLE_DASHES,
    axis_scale as _axis_scale,
    legend_swatch_svg as _legend_swatch_svg,
    proj_x as _proj_x,
    proj_y as _proj_y,
    render_residual_strip as _render_residual_strip,
    resolve_series_dash as _resolve_series_dash,
    sample_model_points as _sample_model_points,
    series_has_uncertainty as _series_has_uncertainty,
    visible_series as _visible_series,
)
from .svg_labels import (
    avoid_label_overlaps,
    halo_text,
    render_marker,
    svg_knockout_label,
)
from .tokens_and_scales import (
    SERIES_STYLES,
    esc,
    format_math_html,
    format_math_svg,
    format_quantity_header,
    format_tick_numeral,
    format_value_unit,
    render_test_condition_strip,
    resolve_term_colors,
    resolve_token,
)


def _render_graticule(
    x_sc: dict[str, Any],
    y_sc: dict[str, Any],
    x_ax: dict[str, Any],
    y_ax: dict[str, Any],
    box: tuple[float, float, float, float],
    data_x: tuple[float, float],
    rigor: str,
    medium: str,
) -> list[str]:
    x0, y0, pw, ph = box
    dx0, dpw = data_x
    parts: list[str] = []
    fine = medium == "m1"
    maj_col = "var(--border-strong)" if fine else "var(--border-hairline)"
    minor_cls = "qe-grid-minor" if fine else "qe-grid-minor qe-m1-only"

    if rigor in {"L2", "L3"} or not x_sc["is_log"]:
        for xm in x_sc["minors"]:
            px = _proj_x(xm, x_sc, dx0, dpw)
            parts.append(f'<line class="{minor_cls}" x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0 + ph}" stroke="var(--border-hairline)" stroke-width="0.5" stroke-dasharray="1,3"/>')
            parts.append(f'<line x1="{px:.1f}" y1="{y0 + ph}" x2="{px:.1f}" y2="{y0 + ph + 4}" stroke="var(--border-strong)" stroke-width="0.8"/>')
    if rigor in {"L2", "L3"} or not y_sc["is_log"]:
        for ym in y_sc["minors"]:
            py = _proj_y(ym, y_sc, y0, ph)
            parts.append(f'<line class="{minor_cls}" x1="{x0}" y1="{py:.1f}" x2="{x0 + pw}" y2="{py:.1f}" stroke="var(--border-hairline)" stroke-width="0.5" stroke-dasharray="1,3"/>')
            parts.append(f'<line x1="{x0 - 4}" y1="{py:.1f}" x2="{x0}" y2="{py:.1f}" stroke="var(--border-strong)" stroke-width="0.8"/>')

    last_x = -999.0
    for xv in x_sc["majors"]:
        px = _proj_x(xv, x_sc, dx0, dpw)
        parts.append(f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0 + ph}" stroke="{maj_col}" stroke-width="0.9"/>')
        if px - last_x >= 44.0:
            lbl = format_tick_numeral(xv, is_log=x_sc["is_log"], step=x_sc.get("step"))
            parts.append(halo_text(px, y0 + ph + 22.0, lbl, anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
            last_x = px

    for yv in y_sc["majors"]:
        py = _proj_y(yv, y_sc, y0, ph)
        parts.append(f'<line x1="{x0}" y1="{py:.1f}" x2="{x0 + pw}" y2="{py:.1f}" stroke="{maj_col}" stroke-width="0.9"/>')
        lbl = format_tick_numeral(yv, is_log=y_sc["is_log"], step=y_sc.get("step"))
        parts.append(halo_text(x0 - 8.0, py + 3.0, lbl, anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))

    parts.append(f'<rect data-role="frame" x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="var(--text-primary)" stroke-width="1.1"/>')
    xlbl = x_ax.get("quantity_calculus") or format_quantity_header(x_ax.get("quantity", "x"), None, x_ax.get("unit", ""))
    ylbl = y_ax.get("quantity_calculus") or format_quantity_header(y_ax.get("quantity", "y"), None, y_ax.get("unit", ""))
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 40.0, xlbl, anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))
    y_lbl_sz = 11.0 if len(str(ylbl)) > 28 else 12.0
    parts.append(f'<text x="22" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 22 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="{y_lbl_sz:.1f}" font-weight="700" fill="var(--text-primary)">{format_math_svg(ylbl, 9.2)}</text>')
    return parts


def _render_envelopes(
    envs: list[dict[str, Any]],
    x_sc: dict[str, Any],
    y_sc: dict[str, Any],
    box: tuple[float, float, float, float],
    data_x: tuple[float, float],
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    x0, y0, pw, ph = box
    dx0, dpw = data_x
    parts: list[str] = []
    labels: list[dict[str, Any]] = []
    gutter: list[dict[str, Any]] = []
    sloped: list[str] = []
    for env in envs:
        col = resolve_token(env.get("stroke_color"), "var(--status-danger)")
        eq, thr = env.get("equation"), env.get("threshold_value")
        is_horiz = False
        if eq:
            pts = _sample_model_points({"equation": eq}, x_sc, n=60)
            px_pts = [(max(x0, min(x0 + pw, _proj_x(xv, x_sc, dx0, dpw))), max(y0, min(y0 + ph, _proj_y(yv, y_sc, y0, ph)))) for xv, yv in pts]
        elif thr is not None:
            is_horiz = True
            py_thr = max(y0, min(y0 + ph, _proj_y(float(thr), y_sc, y0, ph)))
            px_pts = [(x0, py_thr), (x0 + pw, py_thr)]
        else:
            continue
        if not px_pts:
            continue
        d = " ".join(f'{"M" if i == 0 else "L"} {px:.1f} {py:.1f}' for i, (px, py) in enumerate(px_pts))
        direc = str(env.get("direction", "upper")).lower()
        fill_bg = "var(--status-warn-bg)" if env.get("type") == "warning" else "var(--status-err-bg)"
        if direc == "upper":
            poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in px_pts) + f" {px_pts[-1][0]:.1f},{y0:.1f} {px_pts[0][0]:.1f},{y0:.1f}"
            parts.append(f'<polygon points="{poly}" fill="{fill_bg}" opacity="0.50"/>')
        elif direc == "lower":
            poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in px_pts) + f" {px_pts[-1][0]:.1f},{y0 + ph:.1f} {px_pts[0][0]:.1f},{y0 + ph:.1f}"
            parts.append(f'<polygon points="{poly}" fill="{fill_bg}" opacity="0.45"/>')
        dash = _STYLE_DASHES.get(str(env.get("stroke_style", "dashed")).lower(), "6,3")
        dash_attr = f' stroke-dasharray="{dash}"' if dash != "none" else ""
        parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.7"{dash_attr}/>')

        raw_lbl = str(env.get("label", "Limit"))
        if is_horiz:
            if len(raw_lbl) <= 15:
                parts.append(f'<line x1="{x0 + pw:.1f}" y1="{px_pts[0][1]:.1f}" x2="{x0 + pw + 5.0:.1f}" y2="{px_pts[0][1]:.1f}" stroke="{col}" stroke-width="1.5"/>')
                gutter.append({"x": x0 + pw + 8.0, "y": px_pts[0][1] + 4.0, "text": raw_lbl, "anchor": "start", "fill": col, "weight": "700", "w": 110.0})
            else:
                labels.append({"x": x0 + pw * 0.5, "y": px_pts[0][1] + 4.0, "text": raw_lbl, "anchor": "middle", "fill": col, "weight": "700"})
        else:
            interior = [i for i, (px, py) in enumerate(px_pts) if (y0 + 18.0 <= py <= y0 + ph - 18.0) and (dx0 + 60.0 <= px <= dx0 + dpw - 60.0)]
            if not interior:
                interior = [i for i, (_, py) in enumerate(px_pts) if y0 + 14.0 <= py <= y0 + ph - 14.0]
            mid_i = interior[int(len(interior) * 0.36)] if len(interior) > 4 else (interior[len(interior) // 2] if interior else len(px_pts) // 2)
            cx, cy = px_pts[mid_i]
            p0, p1 = px_pts[max(0, mid_i - 4)], px_pts[min(len(px_pts) - 1, mid_i + 4)]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(dx, dy) or 1.0
            theta = math.degrees(math.atan2(dy, dx))
            if theta > 90.0:
                theta -= 180.0
            elif theta < -90.0:
                theta += 180.0
            nx, ny = dy / ln, -dx / ln
            if (direc == "lower" and ny < 0) or (direc != "lower" and ny > 0):
                nx, ny = -nx, -ny
            lx = max(x0 + 72.0, min(x0 + pw - 72.0, cx + nx * 20.0))
            ly = max(y0 + 18.0, min(y0 + ph - 18.0, cy + ny * 20.0))
            sloped.append(halo_text(lx, ly, raw_lbl, anchor="middle", size=11.5, weight="700", fill=col, halo=True, math=True, rotate_deg=theta, stroke_width=4.0, dominant_baseline="central"))
    return parts, labels, gutter, sloped


# Residual strip moved to plot_helpers.render_residual_strip


def _render_series_layers(
    sr: dict[str, Any],
    idx: int,
    x_sc: dict[str, Any],
    y_sc: dict[str, Any],
    box: tuple[float, float, float, float],
    data_x: tuple[float, float],
    rigor: str,
    legend: list[dict[str, Any]] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Render one series split into (corridors, curves, markers) paint layers."""
    x0, y0, pw, ph = box
    dx0, dpw = data_x
    st = SERIES_STYLES[idx % len(SERIES_STYLES)]
    ep = sr.get("epistemic_type", "discrete_measurement")
    term = sr.get("term")
    term_attr = f' data-term="{esc(term)}"' if term else ""
    stroke = resolve_token(sr.get("stroke_color") or sr.get("marker_color"), resolve_term_colors(term)["fg"] if term else st["stroke"])
    bands, strokes, markers = [], [], []

    if ep == "analytical_model":
        pts = [(x, y) for x, y in _sample_model_points(sr, x_sc, legend=legend) if (not x_sc["is_log"] or x > 0.0) and (not y_sc["is_log"] or y > 0.0)]
        if rigor in {"L2", "L3"} and (sr.get("corridor_rel") or sr.get("corridor_abs")) and pts:
            rel, abs_c = float(sr.get("corridor_rel") or 0.0), float(sr.get("corridor_abs") or 0.0)
            up, lo = [], []
            for x, y in pts:
                hi_y = max(y * (1.0 + rel), y * (1.0 - rel)) + abs_c
                lo_y = min(y * (1.0 + rel), y * (1.0 - rel)) - abs_c
                if y_sc["is_log"]:
                    lo_y = max(lo_y, y_sc["min"] * 0.99)
                up.append((_proj_x(x, x_sc, dx0, dpw), max(y0, min(y0 + ph, _proj_y(hi_y, y_sc, y0, ph)))))
                lo.append((_proj_x(x, x_sc, dx0, dpw), max(y0, min(y0 + ph, _proj_y(lo_y, y_sc, y0, ph)))))
            poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in up + list(reversed(lo)))
            bands.append(f'<polygon points="{poly}" fill="{stroke}" opacity="0.14"/>')
        if pts:
            d = " ".join(f'{"M" if i == 0 else "L"} {_proj_x(x, x_sc, dx0, dpw):.1f} {max(y0, min(y0 + ph, _proj_y(y, y_sc, y0, ph))):.1f}' for i, (x, y) in enumerate(pts))
            dash = _resolve_series_dash(sr, st)
            dash_attr = f' stroke-dasharray="{esc(dash)}"' if dash and dash != "none" and _DASH_RE.match(dash) else ""
            sw = float(sr.get("stroke_width", 1.8))
            strokes.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw:g}"{dash_attr}{term_attr}/>')
        return bands, strokes, markers

    glyph = sr.get("marker_glyph", st["marker"])
    msz = float(sr.get("marker_size_px", 6.5))
    pts = [
        p for p in (sr.get("data_points") or [])
        if p.get("x") is not None and p.get("y") is not None
        and math.isfinite(float(p["x"])) and math.isfinite(float(p["y"]))
        and (not x_sc["is_log"] or float(p["x"]) > 0.0) and (not y_sc["is_log"] or float(p["y"]) > 0.0)
    ]
    if sr.get("connect_piecewise") and len(pts) >= 2:
        pts_px = [
            (max(x0, min(x0 + pw, _proj_x(float(p["x"]), x_sc, dx0, dpw))),
             max(y0, min(y0 + ph, _proj_y(float(p["y"]), y_sc, y0, ph))))
            for p in pts
        ]
        d = " ".join(f'{"M" if i == 0 else "L"} {cx:.1f} {cy:.1f}' for i, (cx, cy) in enumerate(pts_px))
        strokes.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.3" opacity="0.65"{term_attr}/>')
    for p in pts:
        xv, yv = float(p["x"]), float(p["y"])
        px = max(x0, min(x0 + pw, _proj_x(xv, x_sc, dx0, dpw)))
        py = max(y0, min(y0 + ph, _proj_y(yv, y_sc, y0, ph)))
        uy = p.get("u_y")
        if uy is not None and rigor in {"L2", "L3"} and math.isfinite(float(uy)):
            u_val = abs(float(uy))
            y_hi = max(y0, min(y0 + ph, _proj_y(yv + u_val, y_sc, y0, ph)))
            y_lo = max(y0, min(y0 + ph, _proj_y(max(yv - u_val, y_sc["min"] * 0.99) if y_sc["is_log"] else yv - u_val, y_sc, y0, ph)))
            markers.append(f'<line x1="{px:.1f}" y1="{y_hi:.1f}" x2="{px:.1f}" y2="{y_lo:.1f}" stroke="{stroke}" stroke-width="1.3"/>')
            markers.append(f'<line x1="{px - 3:.1f}" y1="{y_hi:.1f}" x2="{px + 3:.1f}" y2="{y_hi:.1f}" stroke="{stroke}" stroke-width="1.2"/>')
            markers.append(f'<line x1="{px - 3:.1f}" y1="{y_lo:.1f}" x2="{px + 3:.1f}" y2="{y_lo:.1f}" stroke="{stroke}" stroke-width="1.2"/>')
        markers.append(f'<g{term_attr}>{render_marker(px, py, glyph, msz, stroke, "var(--bg-canvas)")}</g>')
    return bands, strokes, markers


def _compile_cartesian(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile linear, semi-log, or log-log plot with 3.5% spine inset, right-gutter limits, and residual strip."""
    axes = spec.get("axes", {})
    x_ax, y_ax = axes.get("x_axis", {}), axes.get("y_axis", {})
    vis_series = _visible_series(spec, rigor)
    envs = spec.get("envelopes", []) if (rigor in {"L2", "L3"} or spec.get("show_l1_envelopes")) else []
    show_res = bool(spec.get("residual_strip", {}).get("enabled")) and rigor == "L3"
    has_gutter = any(not e.get("equation") and e.get("threshold_value") is not None and len(str(e.get("label", ""))) <= 15 for e in envs)

    xs = [float(p["x"]) for s in vis_series for p in ((s.get("data_points") or []) + (s.get("points") or [])) if p.get("x") is not None and math.isfinite(float(p["x"]))]
    x_sc = _axis_scale(x_ax, xs)
    ys: list[float] = []
    for s in vis_series:
        for p in (s.get("data_points") or []) + (s.get("points") or []):
            if p.get("y") is None or not math.isfinite(float(p["y"])):
                continue
            yv = float(p["y"])
            ys.append(yv)
            uy = p.get("u_y")
            if uy is not None and rigor in {"L2", "L3"} and math.isfinite(float(uy)):
                ys.extend((yv + abs(float(uy)), max(yv - abs(float(uy)), 1e-12) if y_ax.get("scale_type") == "logarithmic" else yv - abs(float(uy))))
        if s.get("epistemic_type") == "analytical_model" and not y_ax.get("domain"):
            ys.extend(yv for _, yv in _sample_model_points(s, x_sc, n=36, legend=spec.get("parametric_legend")) if math.isfinite(yv))
    if not y_ax.get("domain"):
        ys.extend(float(e["threshold_value"]) for e in envs if e.get("threshold_value") is not None and math.isfinite(float(e["threshold_value"])))
    y_sc = _axis_scale(y_ax, ys)
    x0, y0, pw, ph = (78.0, 26.0, 404.0, 224.0) if has_gutter else (78.0, 26.0, 496.0, 224.0)
    inset_x = pw * 0.035
    data_x = (x0 + inset_x, pw - 2.0 * inset_x)
    vb_h = 402 if show_res else 306
    clip_key = f"{spec.get('id', '')}|{x_ax.get('quantity', '')}|{y_ax.get('quantity', '')}".encode("utf-8")
    clip_uid = f"qe-clip-{zlib.crc32(clip_key) % 999983}"
    parts: list[str] = [f'<svg class="qe-svg qe-svg-600" viewBox="0 0 600 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Analytical Plot"))}">']
    parts.append(f'<defs><clipPath id="{clip_uid}"><rect x="{x0}" y="{y0}" width="{pw}" height="{ph}"/></clipPath></defs>')
    parts.extend(_render_graticule(x_sc, y_sc, x_ax, y_ax, (x0, y0, pw, ph), data_x, rigor, medium))

    env_svg, labels, gutter_lbls, sloped_lbls = _render_envelopes(envs, x_sc, y_sc, (x0, y0, pw, ph), data_x)
    bands_all, strokes_all, markers_all = [], [], []
    for idx, sr in enumerate(vis_series):
        b, s, m = _render_series_layers(sr, idx, x_sc, y_sc, (x0, y0, pw, ph), data_x, rigor, legend=spec.get("parametric_legend"))
        bands_all.extend(b)
        strokes_all.extend(s)
        markers_all.extend(m)
    parts.append(f'<g clip-path="url(#{clip_uid})">')
    parts.extend(env_svg)
    parts.extend(bands_all)
    parts.extend(strokes_all)
    parts.extend(markers_all)
    parts.append("</g>")
    parts.extend(sloped_lbls)

    for g in avoid_label_overlaps(gutter_lbls, min_y=y0 + 10.0, max_y=y0 + ph + 4.0, step_y=15.0):
        parts.append(halo_text(g["x"], g["y"], g["text"], anchor="start", size=11.5, weight="700", fill=g["fill"], halo=False, math=True))

    vis_ids = {s.get("id") for s in vis_series if s.get("id")}
    for ann in spec.get("annotations", []):
        if ann.get("series_id") and ann["series_id"] not in vis_ids:
            continue
        raw_x, raw_y = ann.get("x"), ann.get("y")
        if raw_x is None or raw_y is None:
            continue
        xv_a, yv_a = float(raw_x), float(raw_y)
        if not (math.isfinite(xv_a) and math.isfinite(yv_a)):
            continue
        ax_p = _proj_x(xv_a, x_sc, data_x[0], data_x[1])
        ay_p = _proj_y(yv_a, y_sc, y0, ph)
        tx = max(x0 + 20, min(x0 + pw - 20, ax_p + float(ann.get("dx", 24))))
        ty = max(y0 + 18, min(y0 + ph - 12, ay_p + float(ann.get("dy", -20))))
        t_col = resolve_term_colors(ann.get("term"))["fg"] if ann.get("term") else "var(--accent-focal)"
        t_attr = f'data-term="{esc(ann["term"])}"' if ann.get("term") else ""
        parts.append(f'<line x1="{ax_p:.1f}" y1="{ay_p:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{t_col}" stroke-width="1.2" {t_attr}/>')
        parts.append(f'<circle cx="{ax_p:.1f}" cy="{ay_p:.1f}" r="2.8" fill="{t_col}"/>')
        labels.append({"x": tx, "y": ty - 4, "text": str(ann["label"]), "anchor": "start" if tx < x0 + pw * 0.6 else "end", "fill": t_col, "weight": "700", "attrs": t_attr})

    for lbl in avoid_label_overlaps(labels, min_y=y0 + 18, max_y=y0 + ph - 8):
        parts.append(svg_knockout_label(lbl["x"], lbl["y"], lbl["text"], anchor=lbl["anchor"], size=11.5, weight=lbl.get("weight", "600"), fill=lbl["fill"], surface_fill="var(--bg-surface)", x_bounds=(x0 + 4.0, x0 + pw - 4.0), attrs=lbl.get("attrs", "")))

    if show_res:
        parts.extend(_render_residual_strip(vis_series, x_sc, (x0, y0 + ph + 56.0, pw, 72.0), data_x, legend=spec.get("parametric_legend")))
    parts.append("</svg>")
    return "\n".join(parts)


# Legend swatch builder moved to plot_helpers.legend_swatch_svg


def compile_plot(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white", chrome: str = "bench") -> str:
    """Compile Modality 4 (urn:quiet-ui:schema:v9:plot) into NIST-calibrated HTML/SVG."""
    meta = spec.get("metadata", {})
    eff_rigor = (rigor or meta.get("rigor_level", "L3")).upper()
    kind = spec.get("plot_kind", "cartesian")
    payload = build_echarts_payload(spec, eff_rigor, medium)
    payload_attr = f' data-quiet-echarts="{esc(json.dumps(payload, separators=(",", ":"), allow_nan=False))}"' if payload is not None else ""
    parts: list[str] = [f'<div class="qe-plot-wrap" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}"{payload_attr}>']

    if chrome == "bench" and payload is not None:
        parts.append(render_echarts_toggle_bar())

    hide_cond = chrome == "embedded" and (eff_rigor == "L1" or kind == "stacked_bar")
    cond_html = "" if hide_cond else render_test_condition_strip(spec.get("test_environment"), eff_rigor)
    if cond_html:
        parts.append(cond_html)

    if spec.get("pedagogical_equation"):
        eq = spec["pedagogical_equation"]
        tokens_html = " ".join(
            f'<button type="button" class="va-pill qe-eq-term qe-term-{esc(t["term"])}" data-variant="chip" data-term="{esc(t["term"])}">'
            f'<span>{format_math_html(t["symbol"])}</span></button>' if t.get("term") else f'<span class="qe-eq-op">{format_math_html(t["symbol"])}</span>'
            for t in eq.get("terms", [])
        )
        parts.append(f'<div class="qe-equation-bar" aria-label="Governing Equation"><span class="qe-eq-lhs">{format_math_html(eq.get("lhs", ""))} = </span>{tokens_html}</div>')

    _plot_kinds = {
        "waterfall": lambda s, r, m: compile_waterfall(s, r, m),
        "stacked_bar": lambda s, r, m: compile_stacked_bar(s, r, m),
        "gantt": lambda s, r, m: compile_gantt(s, r, m),
        "heatmap": lambda s, r, m: compile_heatmap(s, r, m),
        "dumbbell": lambda s, r, m: compile_dumbbell(s),
        "forest": lambda s, r, m: compile_forest(s),
        "sankey": lambda s, r, m: compile_sankey(s, r, m),
        "us_hex_tile_map": compile_us_hex_tile_map,
        "arrow_dumbbell": lambda s, r, m: compile_arrow_dumbbell(s, r, m, chrome=chrome),
        "paired_subgroup_bars": lambda s, r, m: compile_paired_subgroup_bars(s, r, m, chrome=chrome),
        "dual_slopegraph": compile_dual_slopegraph,
        "diverging_matrix": lambda s, r, m: compile_diverging_matrix(s, r, m),
    }

    def _emit_plot(sub: dict[str, Any], k: str) -> str:
        fn = _plot_kinds.get(k)
        return fn(sub, eff_rigor, medium) if fn else _compile_cartesian(sub, eff_rigor, medium)

    echarts_host = '<div class="qe-echarts-host" hidden></div>' if payload is not None else ""
    parts.append(
        f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Analytical Plot"))}">'
        f'<div class="qe-svg-fallback">{_emit_plot(spec, kind)}</div>{echarts_host}</div>'
    )
    comps = list(spec.get("companions", []))
    if spec.get("companion"):
        comps.insert(0, spec["companion"])
    if comps:
        if len(comps) > 1:
            parts.append('<div class="qe-companions-grid">')
        for comp in comps:
            ck = comp.get("plot_kind", "dumbbell")
            comp_inner = (
                f'<div class="qe-subpanel-title">{format_math_html(comp.get("title", "Companion Plot"))}</div>'
                f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(comp.get("title", "Companion Plot"))}">{_emit_plot(comp, ck)}</div>'
            )
            parts.append(f'<div class="qe-companion-item">{comp_inner}</div>' if len(comps) > 1 else comp_inner)
        if len(comps) > 1:
            parts.append("</div>")

    _self_labeled = {"us_hex_tile_map", "arrow_dumbbell", "paired_subgroup_bars", "dual_slopegraph"}
    vis_series = _visible_series(spec, eff_rigor) if kind == "cartesian" else ([] if kind in _self_labeled else spec.get("series", []))
    series_items: list[str] = []
    param_items: list[str] = []
    omit_l1_legend = eff_rigor == "L1" and chrome == "embedded" and len(vis_series) <= 1 and not spec.get("parametric_legend")
    if not omit_l1_legend:
        for idx, sr in enumerate(vis_series):
            st = SERIES_STYLES[idx % len(SERIES_STYLES)]
            term = sr.get("term")
            col = resolve_token(sr.get("stroke_color") or sr.get("marker_color"), resolve_term_colors(term)["fg"] if term else st["stroke"])
            ep_kind = "discrete" if sr.get("epistemic_type") == "discrete_measurement" else "model"
            has_unc = _series_has_uncertainty(sr)
            ep_lbl = ('Discrete Sample\u00a0<span class="qe-unit-nw">(&#177;u<sub>y</sub>)</span>' if has_unc else 'Discrete Sample') if ep_kind == "discrete" else "Analytical Model"
            swatch = _legend_swatch_svg(sr, st, col)
            if (eff_rigor == "L1" and chrome == "embedded") or kind == "stacked_bar":
                series_items.append(f'<span class="qe-leg-item">{swatch}<span class="qe-leg-txt">{format_math_html(sr.get("name", "Series"))}</span></span>')
            else:
                series_items.append(f'<span class="qe-leg-item" data-epistemic="{ep_kind}">{swatch}<span class="qe-leg-txt">{format_math_html(sr.get("name", "Series"))} · {ep_lbl}</span></span>')
    if kind == "gantt":
        series_items.extend([
            '<span class="qe-leg-item"><svg width="16" height="10" aria-hidden="true"><rect x="1" y="2" width="14" height="6" rx="1.5" fill="var(--accent-focal)"/></svg>Critical Path</span>',
            '<span class="qe-leg-item"><svg width="16" height="10" aria-hidden="true"><rect x="1" y="2" width="14" height="6" rx="1.5" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)" stroke-width="1.1"/></svg>Standard / Float</span>',
            '<span class="qe-leg-item"><svg width="14" height="10" aria-hidden="true"><polygon points="7,1 12,5 7,9 2,5" fill="var(--status-warn)"/></svg>Milestone</span>',
        ])
    elif kind == "dumbbell" and not series_items:
        lbls = spec.get("series_labels") or ["Baseline", "After"]
        series_items.extend([
            f'<span class="qe-leg-item"><svg width="12" height="10" aria-hidden="true"><circle cx="6" cy="5" r="3.5" fill="var(--bg-canvas)" stroke="var(--text-muted)" stroke-width="1.5"/></svg>{esc(str(lbls[0]))}</span>',
            f'<span class="qe-leg-item"><svg width="12" height="10" aria-hidden="true"><circle cx="6" cy="5" r="3.8" fill="var(--accent-focal)"/></svg>{esc(str(lbls[1] if len(lbls) > 1 else "After"))}</span>',
        ])
    for param in spec.get("parametric_legend", []):
        u = str(param.get("unit", ""))
        param_items.append(f'<span class="qe-leg-param va-nums">{format_math_html(param["symbol"])} = {esc(format_value_unit(param["value"], u))}</span>')
    if series_items or param_items:
        s_span = f'<span class="qe-legend-series">{"".join(series_items)}</span>' if series_items else ""
        p_span = f'<span class="qe-param-strip">{"".join(param_items)}</span>' if param_items else ""
        parts.append(f'<div class="qe-param-legend">{s_span}{p_span}</div>')

    parts.append("</div>")
    return "\n".join(parts)
