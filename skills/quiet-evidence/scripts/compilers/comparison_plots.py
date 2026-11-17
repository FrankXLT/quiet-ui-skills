# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Waterfall & Dumbbell Comparison Sub-Compilers."""

from __future__ import annotations

from typing import Any

from .svg_labels import halo_text, svg_knockout_label
from .tokens_and_scales import compute_linear_125_scale, esc, format_tick_numeral


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
        v = float(s["value"])
        kind = s.get("kind", "delta")
        if kind in {"start", "total"}:
            lo, hi = min(0.0, v), max(0.0, v)
            spans.append((lo, hi, v, kind, str(s["label"])))
            running = v
        else:
            nxt = running + v
            lo, hi = min(running, nxt), max(running, nxt)
            spans.append((lo, hi, v, kind, str(s["label"])))
            running = nxt
        bounds.extend((lo, hi))

    envs = spec.get("envelopes", []) if rigor in {"L2", "L3"} else []
    bounds.extend(float(e.get("threshold_value", 0.0)) for e in envs)
    lo_b, hi_b = min(bounds), max(bounds)
    if lo_b == hi_b:
        hi_b = lo_b + 1.0
    sc = compute_linear_125_scale(
        lo_b * (1.12 if lo_b < 0 else 1.0),
        hi_b * (1.12 if hi_b > 0 else 1.0),
        target_ticks=5,
    )

    x0, y0, pw, ph = 84.0, 26.0, 600.0, 210.0
    parts: list[str] = [f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 294" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Waterfall Plot"))}">']
    for yv in sc["majors"]:
        py = _proj_lin_y(yv, sc, y0, ph)
        parts.append(f'<line x1="{x0}" y1="{py:.1f}" x2="{x0 + pw}" y2="{py:.1f}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(x0 - 8, py + 4, format_tick_numeral(yv, step=sc["step"]), anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    y_axis_base = _proj_lin_y(0.0, sc, y0, ph) if sc["min"] <= 0.0 <= sc["max"] else (y0 + ph)
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>')
    parts.append(f'<line x1="{x0}" y1="{y_axis_base:.1f}" x2="{x0 + pw}" y2="{y_axis_base:.1f}" stroke="var(--text-primary)" stroke-width="1.1"/>')

    slot = pw / max(len(spans), 1)
    bw = min(84.0, slot * 0.62)
    sep = "" if unit in {"%", "°"} else "\u00a0"
    for i, (lo, hi, val, kind, lbl) in enumerate(spans):
        bx = x0 + i * slot + (slot - bw) / 2.0
        yt = _proj_lin_y(hi, sc, y0, ph)
        yb = _proj_lin_y(lo, sc, y0, ph)
        bh = max(4.0, yb - yt)
        fill = "var(--status-ok-bg)" if kind == "total" else ("var(--tint-indigo-bg)" if val < 0 else "var(--bg-card)")
        stroke = "var(--status-ok)" if kind == "total" else ("var(--accent-focal)" if val < 0 else "var(--border-strong)")
        lbl_col = "var(--status-ok)" if kind == "total" else ("var(--accent-focal)" if val < 0 else "var(--text-primary)")
        parts.append(f'<rect data-role="bar" x="{bx:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        val_txt = f"{val:+.1f}{sep}{unit}" if kind == "delta" else f"{val:.1f}{sep}{unit}"
        parts.append(halo_text(bx + bw / 2.0, yt - 7.0, val_txt, anchor="middle", size=11.5, weight="700", fill=lbl_col))
        parts.append(halo_text(bx + bw / 2.0, y0 + ph + 19.0, lbl, anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
        if i < len(spans) - 1:
            run_end = lo if (val < 0 and kind == "delta") else hi
            end_y = _proj_lin_y(run_end, sc, y0, ph)
            nx = x0 + (i + 1) * slot + (slot - bw) / 2.0
            parts.append(f'<line x1="{bx + bw:.1f}" y1="{end_y:.1f}" x2="{nx:.1f}" y2="{end_y:.1f}" stroke="var(--border-strong)" stroke-width="1" stroke-dasharray="3,3"/>')

    for env in envs:
        thr = float(env.get("threshold_value", 0.0))
        ey = max(y0 + 12.0, min(y0 + ph - 12.0, _proj_lin_y(thr, sc, y0, ph)))
        parts.append(f'<line x1="{x0}" y1="{ey:.1f}" x2="{x0 + pw}" y2="{ey:.1f}" stroke="var(--status-danger)" stroke-width="1.6" stroke-dasharray="6,3"/>')
        parts.append(svg_knockout_label(x0 + pw * 0.48, ey + 4.0, f'{env.get("label", "Ceiling")} ({thr:g}{sep}{unit})', anchor="middle", size=11.5, weight="700", fill="var(--status-danger)", surface_fill="var(--bg-surface)", x_bounds=(x0 + 8.0, x0 + pw - 8.0), math=False))
    parts.append(f'<text x="20" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 20 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="12.0" font-weight="700" fill="var(--text-primary)">{esc(y_lbl)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def compile_dumbbell(spec: dict[str, Any]) -> str:
    """Compile sector comparison dumbbell chart supporting signed negative/positive ranges."""
    items = spec.get("dumbbells", [])
    unit = str(spec.get("axes", {}).get("y_axis", {}).get("unit", "Gbps"))
    y_lbl = spec.get("axes", {}).get("y_axis", {}).get("quantity_calculus", f"Throughput / {unit}")
    vals = [float(it["before"]) for it in items] + [float(it["after"]) for it in items]
    lo_v = min([0.0] + vals)
    hi_v = max([0.0] + vals)
    if lo_v == hi_v:
        hi_v = lo_v + 1.0
    sc = compute_linear_125_scale(
        lo_v * (1.15 if lo_v < 0 else 1.0),
        hi_v * (1.15 if hi_v > 0 else 1.0),
        target_ticks=5,
    )
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
    parts.append(f'<text x="20" y="{y0 + ph / 2.0:.1f}" transform="rotate(-90 20 {y0 + ph / 2.0:.1f})" text-anchor="middle" font-family="var(--font-mono)" font-size="12.0" font-weight="700" fill="var(--text-primary)">{esc(y_lbl)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def compile_forest(spec: dict[str, Any]) -> str:
    """Compile subgroup confidence-interval forest plot with vertical null-effect line."""
    items = spec.get("items", spec.get("subgroups", []))
    x_ax = spec.get("axes", {}).get("x_axis", {})
    null_v = float(spec.get("null_value", 1.0))
    vals = [null_v] + [float(v) for it in items for v in (it["ci_low"], it["estimate"], it["ci_high"])]
    dom = x_ax.get("domain")
    sc = compute_linear_125_scale(float(dom[0]) if dom else min(vals), float(dom[1]) if dom else max(vals), target_ticks=5)
    x0, y0, pw, row_h = 196.0, 26.0, 326.0, 28.0
    ph = max(72.0, len(items) * row_h)
    vb_h = int(y0 + ph + 48.0)
    span = sc["max"] - sc["min"] or 1.0
    px_map = lambda v: x0 + ((v - sc["min"]) / span) * pw

    parts: list[str] = [f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Forest CI Plot"))}">']
    for xv in sc["majors"]:
        px = px_map(xv)
        parts.append(f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0 + ph}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(px, y0 + ph + 18.0, format_tick_numeral(xv, step=sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
    nx = px_map(null_v)
    parts.append(f'<line x1="{nx:.1f}" y1="{y0}" x2="{nx:.1f}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.4" stroke-dasharray="5,3"/>')
    parts.append(f'<rect data-role="frame" x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 38.0, x_ax.get("quantity_calculus", "Treatment Effect (95% CI)"), anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))

    for idx, it in enumerate(items):
        cy = y0 + (idx + 0.5) * row_h
        est, lo, hi = float(it["estimate"]), float(it["ci_low"]), float(it["ci_high"])
        sig = (hi < null_v) or (lo > null_v)
        col = "var(--accent-focal)" if sig else "var(--text-secondary)"
        px_lo, px_m, px_hi = px_map(lo), px_map(est), px_map(hi)
        parts.append(halo_text(x0 - 10.0, cy + 4.0, str(it["label"]), anchor="end", size=11.5, weight="600", fill="var(--text-primary)", halo=False))
        parts.append(f'<line x1="{px_lo:.1f}" y1="{cy:.1f}" x2="{px_hi:.1f}" y2="{cy:.1f}" stroke="{col}" stroke-width="1.8"/>')
        parts.append(f'<line x1="{px_lo:.1f}" y1="{cy - 4:.1f}" x2="{px_lo:.1f}" y2="{cy + 4:.1f}" stroke="{col}" stroke-width="1.4"/>')
        parts.append(f'<line x1="{px_hi:.1f}" y1="{cy - 4:.1f}" x2="{px_hi:.1f}" y2="{cy + 4:.1f}" stroke="{col}" stroke-width="1.4"/>')
        parts.append(f'<rect data-role="marker" x="{px_m - 4:.1f}" y="{cy - 4:.1f}" width="8" height="8" fill="{col}" stroke="var(--bg-canvas)" stroke-width="1"/>')
        parts.append(halo_text(x0 + pw + 10.0, cy + 4.0, f"{est:.2f} ({lo:.2f}–{hi:.2f})", anchor="start", size=11.5, weight="600", fill=col, halo=False))
    parts.append("</svg>")
    return "\n".join(parts)
