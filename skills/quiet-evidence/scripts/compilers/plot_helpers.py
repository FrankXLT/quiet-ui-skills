# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Scale, Projection, Residual Strip & Legend Swatch Helpers."""

from __future__ import annotations

import math
import re
from typing import Any

from .math_eval import eval_equation
from .svg_labels import halo_text, render_marker
from .tokens_and_scales import (
    compute_linear_125_scale,
    compute_log_decade_scale,
    esc,
)

DASH_RE = re.compile(r"^[0-9.,\s]+$")
STYLE_DASHES = {"solid": "none", "dashed": "5,4", "dotted": "2,3", "dash-dot": "8,3,2,3"}


def resolve_series_dash(sr: dict[str, Any], st: dict[str, str]) -> str:
    """Resolve effective SVG stroke-dasharray for a plot series."""
    raw = sr.get("stroke_dasharray")
    if raw:
        return str(raw).strip()
    return STYLE_DASHES.get(str(sr.get("stroke_style", "")).lower(), st["dash"])


def axis_scale(ax: dict[str, Any], vals: list[float]) -> dict[str, Any]:
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


def proj_x(val: float, sc: dict[str, Any], x0: float, w: float) -> float:
    """Project data X value to SVG pixel coordinate."""
    if sc["is_log"]:
        l0, l1 = math.log10(sc["min"]), math.log10(sc["max"])
        span = l1 - l0 if l1 != l0 else 1.0
        return x0 + ((math.log10(max(val, sc["min"] * 0.1)) - l0) / span) * w
    span = sc["max"] - sc["min"]
    return x0 + ((val - sc["min"]) / (span if span else 1.0)) * w


def proj_y(val: float, sc: dict[str, Any], y0: float, h: float) -> float:
    """Project data Y value to SVG pixel coordinate."""
    if sc["is_log"]:
        l0, l1 = math.log10(sc["min"]), math.log10(sc["max"])
        span = l1 - l0 if l1 != l0 else 1.0
        return y0 + h - ((math.log10(max(val, sc["min"] * 0.1)) - l0) / span) * h
    span = sc["max"] - sc["min"]
    return y0 + h - ((val - sc["min"]) / (span if span else 1.0)) * h


def visible_series(spec: dict[str, Any], rigor: str) -> list[dict[str, Any]]:
    """Return rigor-filtered plot series (L1 shows primary curve/series only unless pedagogical equation)."""
    series = spec.get("series", [])
    if rigor in {"L2", "L3"} or spec.get("pedagogical_equation"):
        return series
    return series[:1]


def build_eq_env(legend: list[dict[str, Any]] | None = None, sr: dict[str, Any] | None = None) -> dict[str, float]:
    """Collect numeric parameter constants from parametric_legend and series params."""
    env: dict[str, float] = {}
    for p in (legend or []):
        sym, val = str(p.get("symbol") or "").strip(), p.get("value")
        if sym.isidentifier() and isinstance(val, (int, float)) and not isinstance(val, bool):
            env[sym] = float(val)
    if sr:
        for k, v in (sr.get("params") or {}).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                env[str(k)] = float(v)
    return env


def sample_model_points(
    sr: dict[str, Any],
    x_sc: dict[str, Any],
    n: int = 90,
    legend: list[dict[str, Any]] | None = None,
) -> list[tuple[float, float]]:
    """Sample analytical model curve over linear or log-spaced X domain."""
    pts_raw = sr.get("points") or sr.get("data_points")
    if pts_raw:
        return [
            (float(p["x"]), float(p["y"]))
            for p in pts_raw
            if p.get("x") is not None and p.get("y") is not None
            and math.isfinite(float(p["x"])) and math.isfinite(float(p["y"]))
        ]
    eq = str(sr.get("equation") or "").strip()
    if not eq:
        return []
    eq_rhs = eq.split("=")[-1].strip()
    env_base = build_eq_env(legend, sr)
    pts: list[tuple[float, float]] = []
    for i in range(n):
        t = i / max(1, n - 1)
        xv = (
            10.0 ** (math.log10(x_sc["min"]) + t * (math.log10(x_sc["max"]) - math.log10(x_sc["min"])))
            if x_sc["is_log"]
            else x_sc["min"] + t * (x_sc["max"] - x_sc["min"])
        )
        env = dict(env_base)
        for alias in ("x", "tau", "f", "t", "IMEP", "L", "N"):
            env.setdefault(alias, xv)
        env["x"] = xv
        try:
            yv = eval_equation(eq_rhs, **env)
            if math.isfinite(yv):
                pts.append((xv, yv))
        except Exception:
            continue
    return pts


def round_coord(val: float) -> float:
    """Round small scientific floats without losing sub-milli precision."""
    return round(val, 15) if 0.0 < abs(val) < 1e-3 else round(val, 6)


def clip_curve_to_y(pts: list[list[float]], y_min: float, y_max: float, log_x: bool = False, log_y: bool = False) -> list[list[float]]:
    """Clip sampled polyline to [y_min, y_max] with boundary intersections so sloped envelopes stop cleanly on the frame."""
    clean = [p for p in pts if math.isfinite(p[0]) and math.isfinite(p[1]) and (not log_x or p[0] > 0.0) and (not log_y or p[1] > 0.0)]
    if len(clean) < 2:
        return [p for p in clean if y_min <= p[1] <= y_max]

    def _cross(p0: list[float], p1: list[float], yb: float) -> list[float] | None:
        if (p0[1] - yb) * (p1[1] - yb) > 0 or p0[1] == p1[1]:
            return None
        t = ((math.log10(yb) - math.log10(p0[1])) / (math.log10(p1[1]) - math.log10(p0[1]))) if (log_y and p0[1] > 0 and p1[1] > 0 and yb > 0) else ((yb - p0[1]) / (p1[1] - p0[1]))
        xv = 10.0 ** (math.log10(p0[0]) + t * (math.log10(p1[0]) - math.log10(p0[0]))) if (log_x and p0[0] > 0 and p1[0] > 0) else (p0[0] + t * (p1[0] - p0[0]))
        return [round_coord(xv), round_coord(yb)]

    out: list[list[float]] = []
    for i, cur in enumerate(clean):
        in_cur = y_min <= cur[1] <= y_max
        if i > 0:
            prv = clean[i - 1]
            if (y_min <= prv[1] <= y_max) != in_cur:
                cross_pts = [cp for yb in (y_min, y_max) if (cp := _cross(prv, cur, yb)) is not None]
                cross_pts.sort(key=lambda pt: abs(pt[0] - prv[0]))
                out.extend(cross_pts)
        if in_cur:
            out.append([round_coord(cur[0]), round_coord(cur[1])])
    return out


def build_corridor_band(pts: list[list[float]], s: dict[str, Any], y_min: float, y_max: float) -> list[list[float]]:
    """Build [x, lo_y, hi_y] analytical uncertainty envelope band clamped to [y_min, y_max]."""
    rel, abs_c = float(s.get("corridor_rel") or 0.0), float(s.get("corridor_abs") or 0.0)
    if (rel == 0.0 and abs_c == 0.0) or not pts:
        return []
    band: list[list[float]] = []
    for xv, yv in pts:
        hi_y = min(y_max, max(yv * (1.0 + rel), yv * (1.0 - rel)) + abs_c)
        lo_y = max(y_min, min(yv * (1.0 + rel), yv * (1.0 - rel)) - abs_c)
        if hi_y >= lo_y:
            band.append([round_coord(xv), round_coord(lo_y), round_coord(hi_y)])
    return band


def compute_normalized_residuals(series: list[dict[str, Any]], log_x: bool = False, legend: list[dict[str, Any]] | None = None) -> list[tuple[float, float]]:
    """Compute r_i = clamp((y_i - y_hat_i) / u_y, -2.8, 2.8) for discrete measurements."""
    model_s = next((s for s in series if s.get("epistemic_type") == "analytical_model" and s.get("equation")), None)
    meas_s = next((s for s in series if s.get("epistemic_type") == "discrete_measurement"), None)
    if not meas_s or not (meas_s.get("data_points") or meas_s.get("points")):
        return []
    env_base = build_eq_env(legend, model_s)
    eq_rhs = str((model_s or {}).get("equation") or "").split("=")[-1].strip()
    res_pts: list[tuple[float, float]] = []
    for p in (meas_s.get("data_points") or meas_s.get("points") or []):
        if p.get("x") is None or p.get("y") is None:
            continue
        xv, yv = float(p["x"]), float(p["y"])
        if not (math.isfinite(xv) and math.isfinite(yv)) or (log_x and xv <= 0.0):
            continue
        raw_u = p.get("u_y")
        uv = abs(float(raw_u)) if (raw_u is not None and math.isfinite(float(raw_u)) and float(raw_u) != 0.0) else (abs(yv) * 0.05 or 1.0)
        if p.get("residual") is not None:
            rv = float(p["residual"])
        elif eq_rhs:
            env = dict(env_base)
            for alias in ("x", "tau", "f", "t", "IMEP", "L", "N"):
                env.setdefault(alias, xv)
            env["x"] = xv
            try:
                rv = (yv - eval_equation(eq_rhs, **env)) / max(uv, 1e-30)
            except (ValueError, ArithmeticError):
                continue
        else:
            rv = 0.0
        if math.isfinite(rv):
            res_pts.append((xv, max(-2.8, min(2.8, rv))))
    return res_pts


def render_residual_strip(
    series: list[dict[str, Any]],
    x_sc: dict[str, Any],
    box: tuple[float, float, float, float],
    data_x: tuple[float, float],
    legend: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Render synchronized bottom residual strip r_i = (y_i - y_hat) / u_y."""
    x0, ry0, pw, rh = box
    dx0, dpw = data_x
    res_pts = compute_normalized_residuals(series, log_x=bool(x_sc["is_log"]), legend=legend)
    if not res_pts and not next((s for s in series if s.get("epistemic_type") == "discrete_measurement" and s.get("data_points")), None):
        return []

    r_sc = {"min": -3.0, "max": 3.0, "is_log": False}
    y_top, y_bot, y_zero = proj_y(2.0, r_sc, ry0, rh), proj_y(-2.0, r_sc, ry0, rh), proj_y(0.0, r_sc, ry0, rh)
    parts: list[str] = [
        f'<rect x="{x0}" y="{y_top:.1f}" width="{pw}" height="{y_bot - y_top:.1f}" fill="var(--bg-elevated)" opacity="0.8"/>',
        f'<line x1="{x0}" y1="{y_zero:.1f}" x2="{x0 + pw}" y2="{y_zero:.1f}" stroke="var(--border-strong)" stroke-width="1"/>',
        f'<rect data-role="frame" x="{x0}" y="{ry0}" width="{pw}" height="{rh}" fill="none" stroke="var(--text-primary)" stroke-width="1"/>',
        halo_text(x0 - 8, y_top + 4, "+2σ", anchor="end", size=11.5, fill="var(--text-muted)", halo=False),
        halo_text(x0 - 8, y_zero + 4, "0", anchor="end", size=11.5, fill="var(--text-secondary)", halo=False),
        halo_text(x0 - 8, y_bot + 4, "-2σ", anchor="end", size=11.5, fill="var(--text-muted)", halo=False),
    ]
    for xv, rv in res_pts:
        px = proj_x(xv, x_sc, dx0, dpw)
        py = max(ry0 + 5.0, min(ry0 + rh - 5.0, proj_y(rv, r_sc, ry0, rh)))
        parts.append(f'<line x1="{px:.1f}" y1="{y_zero:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="var(--accent-focal)" stroke-width="1.2"/>')
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="var(--bg-canvas)" stroke="var(--accent-focal)" stroke-width="1.4"/>')
    parts.append(halo_text(x0 + 6, ry0 + 13, "Normalized Residuals (y_i - y_hat_i) / u_y", anchor="start", size=11.5, weight="600", fill="var(--text-muted)", math=True))
    return parts


def legend_swatch_svg(sr: dict[str, Any], st: dict[str, str], col: str) -> str:
    """Emit legend swatch matching the exact series epistemic_type, dash pattern, and glyph."""
    if sr.get("series_type") == "bar":
        return f'<svg class="qe-leg-svg" width="20" height="14" viewBox="0 0 20 14" aria-hidden="true"><rect x="3" y="2" width="14" height="10" rx="2" fill="{col}"/></svg>'
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
    dash = resolve_series_dash(sr, st)
    dash_attr = f' stroke-dasharray="{esc(dash)}"' if dash and dash != "none" and DASH_RE.match(dash) else ""
    band = f'<rect x="1" y="3" width="18" height="8" fill="{col}" opacity="0.16"/>' if (sr.get("corridor_rel") or sr.get("corridor_abs")) else ""
    return f'<svg class="qe-leg-svg" width="20" height="14" viewBox="0 0 20 14" aria-hidden="true">{band}<line x1="1" y1="7" x2="19" y2="7" stroke="{col}" stroke-width="2"{dash_attr}/></svg>'
