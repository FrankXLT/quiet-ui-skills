# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Waterfall & Dumbbell Comparison Sub-Compilers."""

from __future__ import annotations

import math
from typing import Any

from .svg_labels import halo_text, svg_knockout_label
from .tokens_and_scales import (
    SERIES_STYLES,
    compute_linear_125_scale,
    esc,
    format_math_svg,
    format_tick_numeral,
    resolve_token,
)


def _proj_lin_y(val: float, sc: dict[str, Any], y0: float, ph: float) -> float:
    span = sc["max"] - sc["min"]
    return y0 + ph - ((val - sc["min"]) / (span if span else 1.0)) * ph


def compile_waterfall(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile SLA waterfall budget with 1-2-5 ticks, signed spans, and step connectors."""
    steps = spec.get("steps", [])
    unit = str(spec.get("axes", {}).get("y_axis", {}).get("unit", "ps"))
    y_lbl = spec.get("axes", {}).get("y_axis", {}).get("quantity_calculus", f"Budget / {unit}")
    running, spans, bounds = 0.0, [], [0.0]
    for s in steps:
        v = float(s["delta"] if "delta" in s else s["value"])
        kind = s.get("kind", "delta")
        if kind in {"start", "total"}:
            if kind == "total" and ("value" in s or "delta" in s) and abs(v - running) > 1e-4:
                raise ValueError(f"Waterfall conservation violated at '{s.get('label')}': expected {running:.4f}, got {v:.4f}")
            lo, hi = min(0.0, v), max(0.0, v)
            spans.append((lo, hi, v, kind, str(s["label"])))
            running = v
        else:
            nxt = running + v
            lo, hi = min(running, nxt), max(running, nxt)
            spans.append((lo, hi, v, kind, str(s["label"])))
            running = nxt
        bounds.extend((lo, hi))

    envs = spec.get("envelopes") or [] if rigor in {"L2", "L3"} else []
    bounds.extend(float(e["threshold_value"]) for e in envs if e.get("threshold_value") is not None and math.isfinite(float(e["threshold_value"])))
    lo_b, hi_b = min(bounds), max(bounds)
    if lo_b == hi_b:
        hi_b = lo_b + 1.0
    sc = compute_linear_125_scale(
        lo_b * (1.12 if lo_b < 0 else 1.0),
        hi_b * (1.12 if hi_b > 0 else 1.0),
        target_ticks=5,
    )

    x0, y0, pw, ph = 78.0, 26.0, 536.0, 206.0
    parts: list[str] = [f'<svg class="qe-svg qe-svg-640" viewBox="0 0 640 296" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Waterfall Plot"))}">']
    for yv in sc["majors"]:
        py = _proj_lin_y(yv, sc, y0, ph)
        parts.append(f'<line x1="{x0}" y1="{py:.1f}" x2="{x0 + pw}" y2="{py:.1f}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(x0 - 8, py + 4, format_tick_numeral(yv, step=sc["step"]), anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    y_axis_base = _proj_lin_y(0.0, sc, y0, ph) if sc["min"] <= 0.0 <= sc["max"] else (y0 + ph)
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>')
    parts.append(f'<line x1="{x0}" y1="{y_axis_base:.1f}" x2="{x0 + pw}" y2="{y_axis_base:.1f}" stroke="var(--text-primary)" stroke-width="1.1"/>')

    slot = pw / max(len(spans), 1)
    bw = min(68.0, slot * 0.62)
    sep = "" if unit in {"%", "°"} else "\u00a0"
    for i, (lo, hi, val, kind, lbl) in enumerate(spans):
        bx = x0 + i * slot + (slot - bw) / 2.0
        cx = bx + bw / 2.0
        yt = _proj_lin_y(hi, sc, y0, ph)
        yb = _proj_lin_y(lo, sc, y0, ph)
        bh = max(4.0, yb - yt)
        fill = "var(--status-ok-bg)" if kind == "total" else ("var(--tint-indigo-bg)" if val < 0 else "var(--bg-card)")
        stroke = "var(--status-ok)" if kind == "total" else ("var(--accent-focal)" if val < 0 else "var(--border-strong)")
        lbl_col = "var(--status-ok)" if kind == "total" else ("var(--accent-focal)" if val < 0 else "var(--text-primary)")
        parts.append(f'<rect data-role="bar" x="{bx:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        val_txt = f"{val:+.1f}{sep}{unit}" if kind == "delta" else f"{val:.1f}{sep}{unit}"
        ly = max(y0 + 12.0, min(y0 + ph - 8.0, (yb + 14.0 if (val < 0 and yb + 22.0 < y0 + ph) else yt - 7.0)))
        parts.append(halo_text(cx, ly, val_txt, anchor="middle", size=11.5, weight="700", fill=lbl_col))
        words = lbl.split()
        if len(words) >= 2 and len(lbl) > 9:
            mid = len(words) // 2
            l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
            parts.append(
                f'<text x="{cx:.1f}" y="{y0 + ph + 18.0:.1f}" text-anchor="middle" font-family="var(--font-mono)" '
                f'font-size="11.5" font-weight="500" fill="var(--text-secondary)">'
                f'<tspan x="{cx:.1f}">{esc(l1)}</tspan><tspan x="{cx:.1f}" dy="14">{esc(l2)}</tspan></text>'
            )
        else:
            parts.append(halo_text(cx, y0 + ph + 19.0, lbl, anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
        if i < len(spans) - 1:
            run_end = lo if val < 0 else hi
            end_y = _proj_lin_y(run_end, sc, y0, ph)
            nx = x0 + (i + 1) * slot + (slot - bw) / 2.0
            parts.append(f'<line x1="{bx + bw:.1f}" y1="{end_y:.1f}" x2="{nx:.1f}" y2="{end_y:.1f}" stroke="var(--border-strong)" stroke-width="1" stroke-dasharray="3,3"/>')

    for env in envs:
        raw_thr = env.get("threshold_value")
        if raw_thr is None or not math.isfinite(float(raw_thr)):
            continue
        thr = float(raw_thr)
        ey = max(y0 + 12.0, min(y0 + ph - 12.0, _proj_lin_y(thr, sc, y0, ph)))
        parts.append(f'<line x1="{x0}" y1="{ey:.1f}" x2="{x0 + pw}" y2="{ey:.1f}" stroke="var(--status-danger)" stroke-width="1.6" stroke-dasharray="6,3"/>')
        parts.append(svg_knockout_label(x0 + pw * 0.48, ey + 4.0, f'{env.get("label", "Ceiling")} ({thr:g}{sep}{unit})', anchor="middle", size=11.5, weight="700", fill="var(--status-danger)", surface_fill="var(--bg-surface)", x_bounds=(x0 + 8.0, x0 + pw - 8.0), math=False))
    parts.append(f'<text x="20" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 20 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="12.0" font-weight="700" fill="var(--text-primary)">{format_math_svg(y_lbl, 9.2)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def compile_dumbbell(spec: dict[str, Any]) -> str:
    """Compile sector comparison dumbbell chart supporting signed negative/positive ranges."""
    items = spec.get("dumbbells", [])
    unit = str(spec.get("axes", {}).get("y_axis", {}).get("unit", "Gbps"))
    y_lbl = spec.get("axes", {}).get("y_axis", {}).get("quantity_calculus", f"Throughput / {unit}")
    vals = [float(it["before"]) for it in items] + [float(it["after"]) for it in items]
    lo_raw, hi_raw = (min(vals), max(vals)) if vals else (0.0, 1.0)
    span_raw = (hi_raw - lo_raw) or abs(hi_raw) or 1.0
    ax_map = spec.get("axes", {})
    dom = ax_map.get("y_axis", {}).get("domain") or ax_map.get("x_axis", {}).get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) == 2:
        lo_d, hi_d = float(dom[0]), float(dom[1])
    else:
        lo_d = 0.0 if (0.0 < lo_raw <= hi_raw * 0.25) else (lo_raw - span_raw * 0.15)
        hi_d = hi_raw + span_raw * 0.15
    sc = compute_linear_125_scale(lo_d, hi_d, target_ticks=5)
    x0, y0, pw, ph = 84.0, 26.0, 600.0, 196.0
    parts: list[str] = [f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 278" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Dumbbell Plot"))}">']
    for yv in sc["majors"]:
        py = _proj_lin_y(yv, sc, y0, ph)
        parts.append(f'<line x1="{x0}" y1="{py:.1f}" x2="{x0 + pw}" y2="{py:.1f}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(x0 - 8, py + 4, format_tick_numeral(yv, step=sc["step"]), anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>')

    slot = pw / max(len(items), 1)
    b_pts, a_pts, markers, labels = [], [], [], []
    sep = "" if unit in {"%", "°"} else "\u00a0"
    for i, it in enumerate(items):
        cx = x0 + (i + 0.5) * slot
        yb = _proj_lin_y(float(it["before"]), sc, y0, ph)
        ya = _proj_lin_y(float(it["after"]), sc, y0, ph)
        b_pts.append(f"{cx:.1f},{yb:.1f}")
        a_pts.append(f"{cx:.1f},{ya:.1f}")
        markers.append(f'<line x1="{cx:.1f}" y1="{yb:.1f}" x2="{cx:.1f}" y2="{ya:.1f}" stroke="var(--border-strong)" stroke-width="2.0"/>')
        markers.append(f'<circle cx="{cx:.1f}" cy="{yb:.1f}" r="4.5" fill="var(--bg-canvas)" stroke="var(--text-muted)" stroke-width="1.6"/>')
        markers.append(f'<circle cx="{cx:.1f}" cy="{ya:.1f}" r="4.8" fill="var(--accent-focal)" stroke="var(--bg-canvas)" stroke-width="1.2"/>')
        labels.append(halo_text(cx, ya - 9.0, f'{float(it["after"]):.1f}{sep}{unit}', anchor="middle", size=11.5, weight="700", fill="var(--accent-focal)"))
        labels.append(halo_text(cx, y0 + ph + 19.0, str(it["label"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))

    if len(b_pts) >= 2:
        parts.append(f'<polyline fill="none" stroke="var(--text-muted)" stroke-width="1.3" stroke-dasharray="4,3" points="{" ".join(b_pts)}"/>')
        parts.append(f'<polyline fill="none" stroke="var(--accent-focal)" stroke-width="1.8" points="{" ".join(a_pts)}"/>')
    parts.extend(markers)
    parts.extend(labels)
    parts.append(f'<text x="20" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 20 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="12.0" font-weight="700" fill="var(--text-primary)">{format_math_svg(y_lbl, 9.2)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def compile_forest(spec: dict[str, Any]) -> str:
    """Compile subgroup confidence-interval forest plot in compact 560px viewBox for foldable readability."""
    items = spec.get("items", spec.get("subgroups", []))
    x_ax = spec.get("axes", {}).get("x_axis", {})
    null_v = float(spec.get("null_value", 1.0))
    vals = [null_v] + [float(v) for it in items for v in (it["ci_low"], it["estimate"], it["ci_high"])]
    dom = x_ax.get("domain")
    sc = compute_linear_125_scale(float(dom[0]) if dom else min(vals), float(dom[1]) if dom else max(vals), target_ticks=5)
    x0, y0, pw, row_h = 180.0, 22.0, 240.0, 28.0
    ph = max(72.0, len(items) * row_h)
    vb_h = int(y0 + ph + 48.0)
    span = sc["max"] - sc["min"] or 1.0
    px_map = lambda v: x0 + ((v - sc["min"]) / span) * pw
    px_clamp = lambda v: max(x0, min(x0 + pw, px_map(v)))

    parts: list[str] = [f'<svg class="qe-svg qe-svg-560" viewBox="0 0 560 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Forest CI Plot"))}">']
    for xv in sc["majors"]:
        px = px_map(xv)
        parts.append(f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0 + ph}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(px, y0 + ph + 18.0, format_tick_numeral(xv, step=sc["step"]), anchor="middle", size=12.0, fill="var(--text-secondary)", halo=False))
    nx = px_clamp(null_v)
    parts.append(f'<line x1="{nx:.1f}" y1="{y0}" x2="{nx:.1f}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.4" stroke-dasharray="5,3"/>')
    parts.append(f'<rect data-role="frame" x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 38.0, x_ax.get("quantity_calculus", "Treatment Effect (95% CI)"), anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))

    for idx, it in enumerate(items):
        cy = y0 + (idx + 0.5) * row_h
        est, lo, hi = float(it["estimate"]), float(it["ci_low"]), float(it["ci_high"])
        sig = (hi < null_v) or (lo > null_v)
        col = "var(--accent-focal)" if sig else "var(--text-secondary)"
        px_lo, px_m, px_hi = px_clamp(lo), px_clamp(est), px_clamp(hi)
        parts.append(halo_text(x0 - 8.0, cy + 4.0, str(it["label"]), anchor="end", size=12.8, weight="600", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        parts.append(f'<line x1="{px_lo:.1f}" y1="{cy:.1f}" x2="{px_hi:.1f}" y2="{cy:.1f}" stroke="{col}" stroke-width="1.8"/>')
        parts.append(f'<line x1="{px_lo:.1f}" y1="{cy - 4:.1f}" x2="{px_lo:.1f}" y2="{cy + 4:.1f}" stroke="{col}" stroke-width="1.4"/>')
        parts.append(f'<line x1="{px_hi:.1f}" y1="{cy - 4:.1f}" x2="{px_hi:.1f}" y2="{cy + 4:.1f}" stroke="{col}" stroke-width="1.4"/>')
        parts.append(f'<rect data-role="marker" x="{px_m - 4:.1f}" y="{cy - 4:.1f}" width="8" height="8" fill="{col}" stroke="var(--bg-canvas)" stroke-width="1"/>')
        parts.append(halo_text(x0 + pw + 8.0, cy + 4.0, f"{est:.2f} ({lo:.2f}–{hi:.2f})", anchor="start", size=12.0, weight="600", fill=col, halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


def compile_stacked_bar(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile 24h positive/negative stacked bars + line overlay with NAVAIR 1-2-5 ticks."""
    series_list = spec.get("series") or []
    axes = spec.get("axes") or {}
    xa, ya = axes.get("x_axis") or {}, axes.get("y_axis") or {}
    n_pts = max((len(s.get("data_points") or []) for s in series_list), default=1)
    cats = list(xa.get("categories") or [f"{i:02d}:00" for i in range(max(n_pts, 1))])
    n_cats = max(len(cats), 1)
    bar_series = [s for s in series_list if str(s.get("series_type") or "bar").lower() != "line"]
    line_series = [s for s in series_list if str(s.get("series_type") or "bar").lower() == "line"]
    pos_tot, neg_tot, all_y = [0.0] * n_cats, [0.0] * n_cats, [0.0]
    for s in bar_series:
        for i, pt in enumerate((s.get("data_points") or [])[:n_cats]):
            v = float(pt.get("y") or 0.0)
            if math.isfinite(v):
                pos_tot[i] += max(0.0, v)
                neg_tot[i] += min(0.0, v)
    for s in line_series:
        for pt in (s.get("data_points") or [])[:n_cats]:
            yv = float(pt.get("y") or 0.0)
            if math.isfinite(yv):
                all_y.append(yv)
    dom = ya.get("domain")
    lo_b = float(dom[0]) if dom else min(min(neg_tot), min(all_y))
    hi_b = float(dom[1]) if dom else max(max(pos_tot), max(all_y))
    sc = compute_linear_125_scale(lo_b, hi_b, target_ticks=5)
    x0, y0, pw, ph = 66.0, 22.0, 550.0, 212.0
    parts: list[str] = [f'<svg class="qe-svg qe-svg-640" viewBox="0 0 640 296" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Stacked Energy Bar Chart"))}">']
    for yv in sc["majors"]:
        py = _proj_lin_y(yv, sc, y0, ph)
        parts.append(f'<line x1="{x0}" y1="{py:.1f}" x2="{x0 + pw}" y2="{py:.1f}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(x0 - 8, py + 4, format_tick_numeral(yv, step=sc["step"]), anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    y_zero = _proj_lin_y(0.0, sc, y0, ph) if sc["min"] <= 0.0 <= sc["max"] else (y0 + ph)
    slot = pw / n_cats
    bw = max(4.0, slot * 0.68)
    for idx in range(n_cats):
        bx = x0 + idx * slot + (slot - bw) / 2.0
        pos_acc, neg_acc = 0.0, 0.0
        for s_idx, sr in enumerate(bar_series):
            pts = sr.get("data_points") or []
            v = float(pts[idx].get("y") or 0.0) if idx < len(pts) else 0.0
            if not math.isfinite(v) or abs(v) < 1e-9:
                continue
            col = resolve_token(sr.get("marker_color") or sr.get("stroke_color"), SERIES_STYLES[s_idx % len(SERIES_STYLES)]["stroke"])
            if v > 0:
                yt, yb = _proj_lin_y(pos_acc + v, sc, y0, ph), _proj_lin_y(pos_acc, sc, y0, ph)
                pos_acc += v
            else:
                yt, yb = _proj_lin_y(neg_acc, sc, y0, ph), _proj_lin_y(neg_acc + v, sc, y0, ph)
                neg_acc += v
            parts.append(f'<rect data-role="bar" x="{bx:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{max(1.5, yb - yt):.1f}" rx="1.5" fill="{col}" opacity="0.92"/>')
        if idx % 4 == 0:
            cx = x0 + (idx + 0.5) * slot
            parts.append(halo_text(cx, y0 + ph + 18.0, str(cats[idx]), anchor="middle", size=11.0, fill="var(--text-secondary)", halo=False))
    parts.append(f'<line x1="{x0}" y1="{y_zero:.1f}" x2="{x0 + pw}" y2="{y_zero:.1f}" stroke="var(--text-primary)" stroke-width="1.1"/>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>')
    for sr in line_series:
        pts = sr.get("data_points") or []
        col = resolve_token(sr.get("stroke_color") or sr.get("marker_color"), "var(--text-primary)")
        coords = " ".join(
            f"{x0 + (i + 0.5) * slot:.1f},{_proj_lin_y(float(pts[i].get('y') or 0.0), sc, y0, ph):.1f}"
            for i in range(min(n_cats, len(pts)))
            if math.isfinite(float(pts[i].get("y") or 0.0))
        )
        if coords:
            parts.append(f'<polyline fill="none" stroke="{col}" stroke-width="2.1" points="{coords}"/>')
    for env in (spec.get("envelopes") or [] if rigor in {"L2", "L3"} else []):
        raw_thr = env.get("threshold_value")
        if raw_thr is not None and math.isfinite(float(raw_thr)):
            ey = max(y0 + 10.0, min(y0 + ph - 10.0, _proj_lin_y(float(raw_thr), sc, y0, ph)))
            parts.append(f'<line x1="{x0}" y1="{ey:.1f}" x2="{x0 + pw}" y2="{ey:.1f}" stroke="var(--text-secondary)" stroke-width="1.2" stroke-dasharray="5,3"/>')
            parts.append(svg_knockout_label(x0 + pw * 0.72, ey - 5.0, str(env.get("label") or ""), anchor="middle", size=10.5, weight="600", fill="var(--text-secondary)", surface_fill="var(--bg-surface)", x_bounds=(x0 + 8.0, x0 + pw - 8.0), math=False))
    y_lbl = str(ya.get("quantity_calculus") or "Power (kW)")
    x_lbl = str(xa.get("quantity_calculus") or "Hour of Day")
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 38.0, x_lbl, anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False, math=False))
    parts.append(f'<text x="18" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 18 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="11.5" font-weight="700" fill="var(--text-primary)">{format_math_svg(y_lbl, 9.0)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
