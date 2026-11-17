# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 4 (Analytical, Spectral, Waterfall & Dumbbell Plots)."""

from __future__ import annotations

import math
import re
from typing import Any

from .comparison_plots import compile_dumbbell, compile_forest, compile_waterfall
from .math_eval import eval_equation
from .tokens_and_scales import (
    SERIES_STYLES,
    avoid_label_overlaps,
    compute_linear_125_scale,
    compute_log_decade_scale,
    esc,
    format_math_html,
    format_math_svg,
    format_quantity_header,
    format_tick_numeral,
    format_value_unit,
    halo_text,
    pill_halo_text,
    render_marker,
    render_test_condition_strip,
    resolve_term_colors,
    resolve_token,
)

_DASH_RE = re.compile(r"^[0-9.,\s]+$")
_STYLE_DASHES = {"solid": "none", "dashed": "5,4", "dotted": "2,3", "dash-dot": "8,3,2,3"}


def _resolve_series_dash(sr: dict[str, Any], st: dict[str, str]) -> str:
    raw = sr.get("stroke_dasharray")
    if raw:
        return str(raw).strip()
    return _STYLE_DASHES.get(str(sr.get("stroke_style", "")).lower(), st["dash"])


def _visible_series(spec: dict[str, Any], rigor: str) -> list[dict[str, Any]]:
    series = spec.get("series", [])
    if rigor in {"L2", "L3"} or spec.get("pedagogical_equation"):
        return series
    return series[:1]


def _axis_scale(ax: dict[str, Any], vals: list[float]) -> dict[str, Any]:
    """Build exact 1-2-5 linear or log-decade scale from axis config and data."""
    is_log = ax.get("scale_type") == "logarithmic"
    dom = ax.get("domain")
    fin_vals = [v for v in vals if math.isfinite(v) and (v > 0.0 or not is_log)]
    lo = float(dom[0]) if dom else (min(fin_vals) if fin_vals else (1.0 if is_log else 0.0))
    hi = float(dom[1]) if dom else (max(fin_vals) if fin_vals else (10.0 if is_log else 1.0))
    if is_log:
        sc = compute_log_decade_scale(lo, hi)
        sc["is_log"] = True
        return sc
    sc = compute_linear_125_scale(lo, hi, target_ticks=6)
    sc["is_log"] = False
    return sc


def _proj_x(val: float, sc: dict[str, Any], x0: float, w: float) -> float:
    if sc["is_log"]:
        l0, l1 = math.log10(sc["min"]), math.log10(sc["max"])
        span = l1 - l0 if l1 != l0 else 1.0
        return x0 + ((math.log10(max(val, sc["min"] * 0.1)) - l0) / span) * w
    span = sc["max"] - sc["min"]
    return x0 + ((val - sc["min"]) / (span if span else 1.0)) * w


def _proj_y(val: float, sc: dict[str, Any], y0: float, h: float) -> float:
    if sc["is_log"]:
        l0, l1 = math.log10(sc["min"]), math.log10(sc["max"])
        span = l1 - l0 if l1 != l0 else 1.0
        return y0 + h - ((math.log10(max(val, sc["min"] * 0.1)) - l0) / span) * h
    span = sc["max"] - sc["min"]
    return y0 + h - ((val - sc["min"]) / (span if span else 1.0)) * h


def _sample_model_points(sr: dict[str, Any], x_sc: dict[str, Any], n: int = 90) -> list[tuple[float, float]]:
    if sr.get("points"):
        return [(float(p["x"]), float(p["y"])) for p in sr["points"] if p.get("x") is not None and p.get("y") is not None and math.isfinite(float(p["x"])) and math.isfinite(float(p["y"]))]
    eq = sr.get("equation")
    if not eq:
        return []
    pts: list[tuple[float, float]] = []
    for i in range(n):
        t = i / (n - 1)
        xv = 10.0 ** (math.log10(x_sc["min"]) + t * (math.log10(x_sc["max"]) - math.log10(x_sc["min"]))) if x_sc["is_log"] else x_sc["min"] + t * (x_sc["max"] - x_sc["min"])
        try:
            yv = eval_equation(eq, x=xv, tau=xv, f=xv)
            if math.isfinite(yv):
                pts.append((xv, yv))
        except Exception:
            continue
    return pts


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

    parts.append(f'<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="var(--text-primary)" stroke-width="1.1"/>')
    xlbl = x_ax.get("quantity_calculus") or format_quantity_header(x_ax.get("quantity", "x"), None, x_ax.get("unit", ""))
    ylbl = y_ax.get("quantity_calculus") or format_quantity_header(y_ax.get("quantity", "y"), None, y_ax.get("unit", ""))
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 40.0, xlbl, anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))
    parts.append(f'<text x="18" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 18 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="12.0" font-weight="700" fill="var(--text-primary)">{format_math_svg(ylbl, 9.2)}</text>')
    return parts


def _render_envelopes(envs: list[dict[str, Any]], x_sc: dict[str, Any], y_sc: dict[str, Any], box: tuple[float, float, float, float], data_x: tuple[float, float]) -> tuple[list[str], list[dict[str, Any]]]:
    x0, y0, pw, ph = box
    dx0, dpw = data_x
    parts: list[str] = []
    labels: list[dict[str, Any]] = []
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

        if is_horiz:
            ly = px_pts[0][1] - 9.0 if px_pts[0][1] > y0 + 26.0 else px_pts[0][1] + 17.0
            labels.append({"x": x0 + pw - 8.0, "y": ly, "text": str(env.get("label", "Limit")), "anchor": "end", "fill": col, "weight": "700", "border": col})
        else:
            interior = [i for i, (px, py) in enumerate(px_pts) if (y0 + 20.0 <= py <= y0 + ph - 20.0) and (dx0 + 30.0 <= px <= dx0 + dpw - 40.0)]
            mid_i = interior[len(interior) // 2] if interior else len(px_pts) // 2
            cx, cy = px_pts[mid_i]
            p0, p1 = px_pts[max(0, mid_i - 3)], px_pts[min(len(px_pts) - 1, mid_i + 3)]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = dy / ln, -dx / ln
            if (direc == "lower" and ny < 0) or (direc != "lower" and ny > 0):
                nx, ny = -nx, -ny
            lx, ly = cx + nx * 24.0, max(y0 + 18.0, min(y0 + ph - 10.0, cy + ny * 24.0))
            anch = "start" if nx > 0.25 else ("end" if nx < -0.25 else "middle")
            labels.append({"x": lx, "y": ly, "text": str(env.get("label", "Limit")), "anchor": anch, "fill": col, "weight": "700", "border": col})
    return parts, labels


def _render_residual_strip(series: list[dict[str, Any]], x_sc: dict[str, Any], box: tuple[float, float, float, float], data_x: tuple[float, float]) -> list[str]:
    """Render synchronized bottom residual strip r_i = (y_i - y_hat) / u_y."""
    x0, ry0, pw, rh = box
    dx0, dpw = data_x
    model_eq = next((s.get("equation") for s in series if s.get("epistemic_type") == "analytical_model" and s.get("equation")), None)
    meas_s = next((s for s in series if s.get("epistemic_type") == "discrete_measurement"), None)
    if not meas_s or not meas_s.get("data_points"):
        return []
    res_pts: list[tuple[float, float]] = []
    for p in meas_s["data_points"]:
        if p.get("x") is None or p.get("y") is None:
            continue
        xv, yv = float(p["x"]), float(p["y"])
        if not (math.isfinite(xv) and math.isfinite(yv)) or (x_sc["is_log"] and xv <= 0.0):
            continue
        raw_u = p.get("u_y")
        uv = abs(float(raw_u)) if (raw_u is not None and math.isfinite(float(raw_u)) and float(raw_u) != 0.0) else (abs(yv) * 0.05 or 1.0)
        if p.get("residual") is not None:
            rv = float(p["residual"])
        elif model_eq:
            try:
                rv = (yv - eval_equation(model_eq, x=xv, tau=xv, f=xv)) / max(uv, 1e-30)
            except (ValueError, ArithmeticError):
                continue
        else:
            rv = 0.0
        if math.isfinite(rv):
            res_pts.append((xv, max(-2.8, min(2.8, rv))))

    r_sc = {"min": -3.0, "max": 3.0, "is_log": False}
    y_top, y_bot, y_zero = _proj_y(2.0, r_sc, ry0, rh), _proj_y(-2.0, r_sc, ry0, rh), _proj_y(0.0, r_sc, ry0, rh)
    parts: list[str] = [
        f'<rect x="{x0}" y="{y_top:.1f}" width="{pw}" height="{y_bot - y_top:.1f}" fill="var(--bg-elevated)" opacity="0.8"/>',
        f'<line x1="{x0}" y1="{y_zero:.1f}" x2="{x0 + pw}" y2="{y_zero:.1f}" stroke="var(--border-strong)" stroke-width="1"/>',
        f'<rect x="{x0}" y="{ry0}" width="{pw}" height="{rh}" fill="none" stroke="var(--text-primary)" stroke-width="1"/>',
        halo_text(x0 - 8, y_top + 4, "+2σ", anchor="end", size=11.5, fill="var(--text-muted)", halo=False),
        halo_text(x0 - 8, y_zero + 4, "0", anchor="end", size=11.5, fill="var(--text-secondary)", halo=False),
        halo_text(x0 - 8, y_bot + 4, "-2σ", anchor="end", size=11.5, fill="var(--text-muted)", halo=False),
    ]
    for xv, rv in res_pts:
        px = _proj_x(xv, x_sc, dx0, dpw)
        py = max(ry0 + 5.0, min(ry0 + rh - 5.0, _proj_y(rv, r_sc, ry0, rh)))
        parts.append(f'<line x1="{px:.1f}" y1="{y_zero:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="var(--accent-focal)" stroke-width="1.2"/>')
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="var(--bg-canvas)" stroke="var(--accent-focal)" stroke-width="1.4"/>')
    parts.append(halo_text(x0 + 6, ry0 + 13, "Normalized Residuals (y_i - y_hat_i) / u_y", anchor="start", size=11.5, weight="600", fill="var(--text-muted)", math=True))
    return parts


def _render_series_layers(
    sr: dict[str, Any],
    idx: int,
    x_sc: dict[str, Any],
    y_sc: dict[str, Any],
    box: tuple[float, float, float, float],
    data_x: tuple[float, float],
    rigor: str,
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
        pts = [(x, y) for x, y in _sample_model_points(sr, x_sc) if (not x_sc["is_log"] or x > 0.0) and (not y_sc["is_log"] or y > 0.0)]
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
        p for p in sr.get("data_points", [])
        if p.get("x") is not None and p.get("y") is not None
        and math.isfinite(float(p["x"])) and math.isfinite(float(p["y"]))
        and (not x_sc["is_log"] or float(p["x"]) > 0.0) and (not y_sc["is_log"] or float(p["y"]) > 0.0)
    ]
    if sr.get("connect_piecewise") and len(pts) >= 2:
        d = " ".join(f'{"M" if i == 0 else "L"} {_proj_x(float(p["x"]), x_sc, dx0, dpw):.1f} {_proj_y(float(p["y"]), y_sc, y0, ph):.1f}' for i, p in enumerate(pts))
        strokes.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.3" opacity="0.65"{term_attr}/>')
    for p in pts:
        xv, yv = float(p["x"]), float(p["y"])
        px, py = _proj_x(xv, x_sc, dx0, dpw), _proj_y(yv, y_sc, y0, ph)
        uy = p.get("u_y")
        if uy is not None and rigor in {"L2", "L3"} and math.isfinite(float(uy)):
            u_val = abs(float(uy))
            y_hi = max(y0, _proj_y(yv + u_val, y_sc, y0, ph))
            y_lo = min(y0 + ph, _proj_y(max(yv - u_val, y_sc["min"] * 0.99) if y_sc["is_log"] else yv - u_val, y_sc, y0, ph))
            markers.append(f'<line x1="{px:.1f}" y1="{y_hi:.1f}" x2="{px:.1f}" y2="{y_lo:.1f}" stroke="{stroke}" stroke-width="1.3"/>')
            markers.append(f'<line x1="{px - 3:.1f}" y1="{y_hi:.1f}" x2="{px + 3:.1f}" y2="{y_hi:.1f}" stroke="{stroke}" stroke-width="1.2"/>')
            markers.append(f'<line x1="{px - 3:.1f}" y1="{y_lo:.1f}" x2="{px + 3:.1f}" y2="{y_lo:.1f}" stroke="{stroke}" stroke-width="1.2"/>')
        markers.append(f'<g{term_attr}>{render_marker(px, py, glyph, msz, stroke, "var(--bg-canvas)")}</g>')
    return bands, strokes, markers


def _compile_cartesian(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile linear, semi-log, or log-log plot with 3.5% spine inset and optional residual strip."""
    axes = spec.get("axes", {})
    x_ax, y_ax = axes.get("x_axis", {}), axes.get("y_axis", {})
    vis_series = _visible_series(spec, rigor)
    envs = spec.get("envelopes", []) if rigor in {"L2", "L3"} else []
    show_res = bool(spec.get("residual_strip", {}).get("enabled")) and rigor == "L3"

    xs = [float(p["x"]) for s in vis_series for p in s.get("data_points", []) if p.get("x") is not None and math.isfinite(float(p["x"]))]
    ys = [float(p["y"]) for s in vis_series for p in s.get("data_points", []) if p.get("y") is not None and math.isfinite(float(p["y"]))]
    x_sc, y_sc = _axis_scale(x_ax, xs), _axis_scale(y_ax, ys)
    x0, y0, pw, ph = 94.0, 26.0, 590.0, 224.0
    inset_x = pw * 0.035
    data_x = (x0 + inset_x, pw - 2.0 * inset_x)
    vb_h = 402 if show_res else 306
    parts: list[str] = [f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Analytical Plot"))}">']
    parts.extend(_render_graticule(x_sc, y_sc, x_ax, y_ax, (x0, y0, pw, ph), data_x, rigor, medium))

    env_svg, labels = _render_envelopes(envs, x_sc, y_sc, (x0, y0, pw, ph), data_x)
    parts.extend(env_svg)

    bands_all, strokes_all, markers_all = [], [], []
    for idx, sr in enumerate(vis_series):
        b, s, m = _render_series_layers(sr, idx, x_sc, y_sc, (x0, y0, pw, ph), data_x, rigor)
        bands_all.extend(b)
        strokes_all.extend(s)
        markers_all.extend(m)
    parts.extend(bands_all)
    parts.extend(strokes_all)
    parts.extend(markers_all)

    vis_ids = {s.get("id") for s in vis_series if s.get("id")}
    for ann in spec.get("annotations", []):
        if ann.get("series_id") and ann["series_id"] not in vis_ids:
            continue
        ax_p = _proj_x(float(ann["x"]), x_sc, data_x[0], data_x[1])
        ay_p = _proj_y(float(ann["y"]), y_sc, y0, ph)
        tx = max(x0 + 20, min(x0 + pw - 20, ax_p + float(ann.get("dx", 24))))
        ty = max(y0 + 18, min(y0 + ph - 12, ay_p + float(ann.get("dy", -20))))
        t_col = resolve_term_colors(ann.get("term"))["fg"] if ann.get("term") else "var(--accent-focal)"
        t_attr = f'data-term="{esc(ann["term"])}"' if ann.get("term") else ""
        parts.append(f'<line x1="{ax_p:.1f}" y1="{ay_p:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{t_col}" stroke-width="1.2" {t_attr}/>')
        parts.append(f'<circle cx="{ax_p:.1f}" cy="{ay_p:.1f}" r="2.8" fill="{t_col}"/>')
        labels.append({"x": tx, "y": ty - 4, "text": str(ann["label"]), "anchor": "start" if tx < x0 + pw * 0.6 else "end", "fill": t_col, "weight": "700", "border": t_col, "attrs": t_attr})

    for lbl in avoid_label_overlaps(labels, min_y=y0 + 18, max_y=y0 + ph - 8):
        parts.append(pill_halo_text(lbl["x"], lbl["y"], lbl["text"], anchor=lbl["anchor"], size=11.5, weight=lbl.get("weight", "600"), fill=lbl["fill"], border=lbl.get("border", "var(--border-hairline)"), x_bounds=(x0 + 4.0, x0 + pw - 4.0), attrs=lbl.get("attrs", "")))

    if show_res:
        parts.extend(_render_residual_strip(vis_series, x_sc, (x0, y0 + ph + 56.0, pw, 72.0), data_x))
    parts.append("</svg>")
    return "\n".join(parts)


def _legend_swatch_svg(sr: dict[str, Any], st: dict[str, str], col: str) -> str:
    """Emit legend swatch matching the exact series epistemic_type, dash pattern, and glyph."""
    if sr.get("epistemic_type") == "discrete_measurement":
        glyph = sr.get("marker_glyph", st["marker"])
        conn = f'<line x1="1" y1="7" x2="19" y2="7" stroke="{col}" stroke-width="1.3" opacity="0.65"/>' if sr.get("connect_piecewise") else ""
        whisker = (
            f'<line x1="10" y1="1.5" x2="10" y2="12.5" stroke="{col}" stroke-width="1.2"/>'
            f'<line x1="7.5" y1="1.5" x2="12.5" y2="1.5" stroke="{col}" stroke-width="1.1"/>'
            f'<line x1="7.5" y1="12.5" x2="12.5" y2="12.5" stroke="{col}" stroke-width="1.1"/>'
        )
        glyph_svg = render_marker(10.0, 7.0, glyph, 5.5, col, "var(--bg-canvas)")
        return f'<svg class="qe-leg-svg" width="20" height="14" viewBox="0 0 20 14" aria-hidden="true">{conn}{whisker}{glyph_svg}</svg>'
    dash = _resolve_series_dash(sr, st)
    dash_attr = f' stroke-dasharray="{esc(dash)}"' if dash and dash != "none" and _DASH_RE.match(dash) else ""
    band = f'<rect x="1" y="3" width="18" height="8" fill="{col}" opacity="0.16"/>' if (sr.get("corridor_rel") or sr.get("corridor_abs")) else ""
    return f'<svg class="qe-leg-svg" width="20" height="14" viewBox="0 0 20 14" aria-hidden="true">{band}<line x1="1" y1="7" x2="19" y2="7" stroke="{col}" stroke-width="2"{dash_attr}/></svg>'


def compile_plot(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white") -> str:
    """Compile Modality 4 (urn:quiet-ui:schema:v9:plot) into NIST-calibrated HTML/SVG."""
    meta = spec.get("metadata", {})
    eff_rigor = (rigor or meta.get("rigor_level", "L3")).upper()
    kind = spec.get("plot_kind", "cartesian")
    parts: list[str] = [f'<div class="qe-plot-wrap" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}">']

    cond_html = render_test_condition_strip(spec.get("test_environment"), eff_rigor)
    if cond_html:
        parts.append(cond_html)

    if spec.get("pedagogical_equation"):
        eq = spec["pedagogical_equation"]
        tokens_html = " ".join(
            f'<span class="qe-eq-term qe-term-{esc(t["term"])}" data-term="{esc(t["term"])}" tabindex="0" role="button">'
            f'{format_math_html(t["symbol"])}</span>' if t.get("term") else f'<span class="qe-eq-op">{format_math_html(t["symbol"])}</span>'
            for t in eq.get("terms", [])
        )
        parts.append(f'<div class="qe-equation-bar" aria-label="Governing Equation"><span class="qe-eq-lhs">{format_math_html(eq.get("lhs", ""))} = </span>{tokens_html}</div>')

    def _emit_plot(sub: dict[str, Any], k: str) -> str:
        if k == "waterfall":
            return compile_waterfall(sub, eff_rigor, medium)
        if k == "dumbbell":
            return compile_dumbbell(sub)
        if k == "forest":
            return compile_forest(sub)
        return _compile_cartesian(sub, eff_rigor, medium)

    parts.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Analytical Plot"))}">{_emit_plot(spec, kind)}</div>')
    comps = list(spec.get("companions", []))
    if spec.get("companion"):
        comps.insert(0, spec["companion"])
    for comp in comps:
        ck = comp.get("plot_kind", "dumbbell")
        parts.append(f'<div class="qe-subpanel-title">{esc(comp.get("title", "Companion Plot"))}</div>')
        parts.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(comp.get("title", "Companion Plot"))}">{_emit_plot(comp, ck)}</div>')

    vis_series = _visible_series(spec, eff_rigor) if kind == "cartesian" else spec.get("series", [])
    legend_items: list[str] = []
    for idx, sr in enumerate(vis_series):
        st = SERIES_STYLES[idx % len(SERIES_STYLES)]
        term = sr.get("term")
        col = resolve_token(sr.get("stroke_color") or sr.get("marker_color"), resolve_term_colors(term)["fg"] if term else st["stroke"])
        ep_kind = "discrete" if sr.get("epistemic_type") == "discrete_measurement" else "model"
        ep_lbl = "Discrete Sample (&#177;u<sub>y</sub>)" if ep_kind == "discrete" else "Analytical Model"
        swatch = _legend_swatch_svg(sr, st, col)
        legend_items.append(f'<span class="qe-leg-item" data-epistemic="{ep_kind}">{swatch}{format_math_html(sr.get("name", "Series"))} · {ep_lbl}</span>')
    for param in spec.get("parametric_legend", []):
        u = str(param.get("unit", ""))
        legend_items.append(f'<span class="qe-leg-param va-nums">{format_math_html(param["symbol"])} = {esc(format_value_unit(param["value"], u))}</span>')
    if legend_items:
        parts.append(f'<div class="qe-param-legend">{"".join(legend_items)}</div>')

    parts.append("</div>")
    return "\n".join(parts)
