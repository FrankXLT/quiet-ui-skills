# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Schedule Gantt & 2D Matrix Heatmap SVG Compilers."""

from __future__ import annotations

import math
import zlib
from typing import Any

from .svg_labels import halo_text
from .tokens_and_scales import compute_linear_125_scale, esc, format_math_svg, format_tick_numeral

# Cividis-inspired Blue -> Amber -> Copper sequential ramp calibrated for light & dark surfaces
_HEATMAP_STOPS: tuple[tuple[float, tuple[int, int, int]], ...] = (
    (0.00, (239, 246, 255)),  # #EFF6FF
    (0.25, (147, 197, 253)),  # #93C5FD
    (0.50, (253, 230, 138)),  # #FDE68A
    (0.75, (251, 191, 36)),   # #FBBF24
    (1.00, (110, 38, 14)),    # #6E260E
)


def _interp_heatmap_rgb(t: float) -> tuple[str, str]:
    u = max(0.0, min(1.0, float(t)))
    c0, c1 = _HEATMAP_STOPS[0][1], _HEATMAP_STOPS[-1][1]
    t0, t1 = 0.0, 1.0
    for idx in range(len(_HEATMAP_STOPS) - 1):
        a_t, a_rgb = _HEATMAP_STOPS[idx]
        b_t, b_rgb = _HEATMAP_STOPS[idx + 1]
        if a_t <= u <= b_t:
            t0, t1, c0, c1 = a_t, b_t, a_rgb, b_rgb
            break
    frac = (u - t0) / (t1 - t0) if t1 > t0 else 0.0
    r = int(round(c0[0] + frac * (c1[0] - c0[0])))
    g = int(round(c0[1] + frac * (c1[1] - c0[1])))
    b = int(round(c0[2] + frac * (c1[2] - c0[2])))

    def _lin(ch: int) -> float:
        s = ch / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    lum = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    cr_white = 1.05 / (lum + 0.05)
    cr_dark = (lum + 0.05) / 0.0585  # #0F172A luminance ~= 0.0085
    ink = "#FFFFFF" if cr_white >= cr_dark else "#0F172A"
    return f"#{r:02X}{g:02X}{b:02X}", ink


def compile_gantt(spec: dict[str, Any], rigor: str = "L2", medium: str = "m2") -> str:
    """Compile critical-path Gantt timeline with float tails, dependencies, milestones, and Today cursor."""
    tasks = spec.get("tasks") or []
    xa = (spec.get("axes") or {}).get("x_axis") or {}
    unit = str(xa.get("unit") or ("h" if "Hour" in str(xa.get("quantity_calculus") or "") else "d"))
    axis_lbl = str(xa.get("quantity_calculus") or f"Schedule, t / {unit}")

    dom = xa.get("domain")
    vals = [float(t.get("start", 0.0)) for t in tasks] + [
        float(t.get("end", t.get("start", 0.0))) + max(0.0, float(t.get("float_days") or t.get("float_hours") or 0.0))
        for t in tasks
    ]
    if spec.get("today_day") is not None:
        vals.append(float(spec["today_day"]))
    lo_d = float(dom[0]) if isinstance(dom, (list, tuple)) and len(dom) == 2 else min(vals or [0.0])
    hi_d = float(dom[1]) if isinstance(dom, (list, tuple)) and len(dom) == 2 else max(vals or [10.0])
    sc = compute_linear_125_scale(lo_d, hi_d if hi_d > lo_d else lo_d + 1.0, target_ticks=6)

    x0, y0, pw, row_h = 198.0, 42.0, 494.0, 30.0
    ph = max(90.0, len(tasks) * row_h)
    vb_h = int(y0 + ph + 46.0)
    span = sc["max"] - sc["min"] or 1.0
    px_map = lambda v: x0 + ((float(v) - sc["min"]) / span) * pw

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Schedule Gantt"))}">',
        '<defs><marker id="qe-gantt-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-muted)"/></marker></defs>',
    ]

    for xv in sc["majors"]:
        px = px_map(xv)
        parts.append(f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0 + ph}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(px, y0 + ph + 18.0, format_tick_numeral(xv, step=sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))

    for i in range(1, len(tasks)):
        ry = y0 + i * row_h
        parts.append(f'<line x1="{x0}" y1="{ry:.1f}" x2="{x0 + pw}" y2="{ry:.1f}" stroke="var(--border-hairline)" stroke-width="0.7"/>')

    pos_by_id: dict[str, tuple[float, float, float]] = {}
    for idx, t in enumerate(tasks):
        cy = y0 + (idx + 0.5) * row_h
        px_s = px_map(float(t.get("start", 0.0)))
        px_e = px_map(float(t.get("end", t.get("start", 0.0))))
        pos_by_id[str(t.get("id") or f"t{idx}")] = (px_s, px_e, cy)

    # Orthogonal dependency connectors drawn behind bars
    for idx, t in enumerate(tasks):
        tid = str(t.get("id") or f"t{idx}")
        dst_s, _dst_e, dst_cy = pos_by_id[tid]
        for dep_id in t.get("depends_on") or []:
            src = pos_by_id.get(str(dep_id))
            if not src:
                continue
            _src_s, src_e, src_cy = src
            if dst_s >= src_e + 10.0:
                mid_x = src_e + 6.0
                d = f"M {src_e:.1f} {src_cy:.1f} H {mid_x:.1f} V {dst_cy:.1f} H {dst_s - 2:.1f}"
            else:
                mid_y = (src_cy + dst_cy) / 2.0
                d = f"M {src_e:.1f} {src_cy:.1f} H {src_e + 7:.1f} V {mid_y:.1f} H {max(x0 + 2, dst_s - 8):.1f} V {dst_cy:.1f} H {dst_s - 2:.1f}"
            parts.append(f'<path d="{d}" fill="none" stroke="var(--text-muted)" stroke-width="1.1" marker-end="url(#qe-gantt-arr)"/>')

    # Task labels, bars, float buffers, and milestone markers
    for idx, t in enumerate(tasks):
        cy = y0 + (idx + 0.5) * row_h
        lbl_raw = str(t.get("label") or f"Task {idx + 1}")
        lbl = lbl_raw if len(lbl_raw) <= 26 else lbl_raw[:25] + "\u2026"
        crit = bool(t.get("critical", False))
        mile = bool(t.get("milestone", False))
        px_s, px_e, _ = pos_by_id[str(t.get("id") or f"t{idx}")]
        flt = max(0.0, float(t.get("float_days") or t.get("float_hours") or 0.0))
        px_f = px_map(float(t.get("end", t.get("start", 0.0))) + flt)
        parts.append(
            halo_text(
                x0 - 10.0, cy + 4.0, lbl, anchor="end", size=11.5,
                weight="700" if crit else "600", font="var(--font-sans)",
                fill="var(--text-primary)", halo=False,
            )
        )
        if mile:
            pts = f"{px_e:.1f},{cy - 7:.1f} {px_e + 7:.1f},{cy:.1f} {px_e:.1f},{cy + 7:.1f} {px_e - 7:.1f},{cy:.1f}"
            parts.append(f'<polygon points="{pts}" fill="var(--status-warn)" stroke="var(--bg-canvas)" stroke-width="1.2"/>')
            m_lbl = f"{float(t.get('end', 0.0)):g} {unit}"
            if px_e < x0 + pw - 74.0:
                parts.append(halo_text(px_e + 11.0, cy + 4.0, m_lbl, anchor="start", size=11.5, weight="700", fill="var(--status-warn)", halo=False))
            else:
                parts.append(halo_text(px_e - 11.0, cy + 4.0, m_lbl, anchor="end", size=11.5, weight="700", fill="var(--status-warn)", halo=False))
        else:
            bw = max(5.0, px_e - px_s)
            b_fill = "var(--accent-focal)" if crit else "var(--tint-indigo-bg)"
            b_stroke = "var(--bg-canvas)" if crit else "var(--accent-primary)"
            b_sw = "0.9" if crit else "1.2"
            parts.append(f'<rect x="{px_s:.1f}" y="{cy - 7:.1f}" width="{bw:.1f}" height="14" rx="2.5" fill="{b_fill}" stroke="{b_stroke}" stroke-width="{b_sw}"/>')
            if flt > 0.0 and px_f > px_e + 2.0:
                fw = max(4.0, px_f - px_e)
                parts.append(f'<rect x="{px_e:.1f}" y="{cy - 5:.1f}" width="{fw:.1f}" height="10" rx="2" fill="var(--bg-surface)" stroke="var(--text-muted)" stroke-width="1.1" stroke-dasharray="3,2"/>')
            if rigor in {"L2", "L3"}:
                note = f"+{flt:g}{unit}" if flt > 0.0 else f"{float(t.get('end', 0.0)) - float(t.get('start', 0.0)):g}{unit}"
                note_col = "var(--text-muted)" if flt > 0.0 else "var(--accent-focal)"
                anchor_r = px_f if flt > 0.0 else px_e
                if anchor_r < x0 + pw - 46.0:
                    parts.append(halo_text(anchor_r + 6.0, cy + 4.0, note, anchor="start", size=11.5, weight="600", fill=note_col, halo=False))
                elif px_s > x0 + 48.0:
                    parts.append(halo_text(px_s - 6.0, cy + 4.0, note, anchor="end", size=11.5, weight="600", fill=note_col, halo=False))

    if spec.get("today_day") is not None:
        td = float(spec["today_day"])
        tx = max(x0, min(x0 + pw, px_map(td)))
        parts.append(f'<line x1="{tx:.1f}" y1="{y0 - 6:.1f}" x2="{tx:.1f}" y2="{y0 + ph:.1f}" stroke="var(--status-danger)" stroke-width="1.6" stroke-dasharray="4,3"/>')
        lbl_tx = max(x0 + 46.0, min(x0 + pw - 46.0, tx))
        t_lbl = str(spec.get("today_label") or f"Today ({td:g}{unit})")
        parts.append(halo_text(lbl_tx, 24.0, t_lbl, anchor="middle", size=11.5, weight="700", fill="var(--status-danger)", halo=False))

    parts.append(f'<rect data-role="frame" x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 38.0, axis_lbl, anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))
    parts.append("</svg>")
    return "\n".join(parts)


def compile_heatmap(spec: dict[str, Any], rigor: str = "L2", medium: str = "m2") -> str:
    """Compile calibrated 2D matrix heatmap with perceptual scale, contrast-locked cell values, and colorbar."""
    x_cats = [str(c) for c in (spec.get("x_categories") or [])]
    y_cats = [str(c) for c in (spec.get("y_categories") or [])]
    matrix = spec.get("matrix") or []
    scale_meta = spec.get("scale") or {}
    unit = str(scale_meta.get("unit") or "")
    z_lbl = str(scale_meta.get("quantity_calculus") or f"Value / {unit or '1'}")
    x_lbl = str(((spec.get("axes") or {}).get("x_axis") or {}).get("quantity_calculus") or "Column")

    flat_vals = [
        float(v) for row in matrix[:len(y_cats)] for v in row[:len(x_cats)]
        if v is not None and math.isfinite(float(v))
    ]
    dom = scale_meta.get("domain")
    v_min = float(dom[0]) if isinstance(dom, (list, tuple)) and len(dom) == 2 else min(flat_vals or [0.0])
    v_max = float(dom[1]) if isinstance(dom, (list, tuple)) and len(dom) == 2 else max(flat_vals or [100.0])
    sc = compute_linear_125_scale(v_min, v_max if v_max > v_min else v_min + 1.0, target_ticks=5)
    z_lo, z_hi = float(sc["min"]), float(sc["max"])
    z_span = z_hi - z_lo or 1.0

    n_cols, n_rows = max(len(x_cats), 1), max(len(y_cats), 1)
    x0, y0, gw, ch = 152.0, 54.0, 420.0, 34.0
    cw = gw / n_cols
    gh = n_rows * ch
    vb_h = int(y0 + gh + 44.0)
    fmt_prec = int(scale_meta.get("decimals", 1))
    grad_id = f"qe-hm-{zlib.crc32(str(spec.get('id') or 'heatmap').encode('utf-8')) & 0xFFFF:04x}"

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Matrix Heatmap"))}">',
        f'<defs><linearGradient id="{grad_id}" x1="0" y1="1" x2="0" y2="0">'
        + "".join(
            f'<stop offset="{int(round(st * 100))}%" stop-color="#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"/>'
            for st, rgb in _HEATMAP_STOPS
        )
        + '</linearGradient></defs>',
    ]

    for ci, clbl in enumerate(x_cats):
        cx = x0 + (ci + 0.5) * cw
        short_c = clbl if len(clbl) <= 10 else clbl[:9] + "\u2026"
        parts.append(halo_text(cx, y0 - 14.0, short_c, anchor="middle", size=11.5, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))

    for ri, rlbl in enumerate(y_cats):
        ry = y0 + ri * ch
        cy = ry + ch / 2.0 + 4.0
        short_r = rlbl if len(rlbl) <= 18 else rlbl[:17] + "\u2026"
        parts.append(halo_text(x0 - 10.0, cy, short_r, anchor="end", size=11.5, weight="600", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        row_vals = matrix[ri] if ri < len(matrix) else []
        for ci in range(len(x_cats)):
            raw_cell = row_vals[ci] if ci < len(row_vals) else None
            val = float(raw_cell) if raw_cell is not None and math.isfinite(float(raw_cell)) else 0.0
            rx = x0 + ci * cw
            fill_hex, ink_hex = _interp_heatmap_rgb((val - z_lo) / z_span)
            parts.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{cw:.1f}" height="{ch:.1f}" fill="{fill_hex}" stroke="var(--bg-canvas)" stroke-width="1.2"/>')
            if rigor in {"L2", "L3"} and cw >= 42.0:
                v_str = f"{val:.{fmt_prec}f}" if fmt_prec > 0 else f"{val:.0f}"
                parts.append(halo_text(rx + cw / 2.0, cy, v_str, anchor="middle", size=11.5, weight="700", fill=ink_hex, halo=False))

    parts.append(f'<rect data-role="frame" x="{x0}" y="{y0}" width="{gw}" height="{gh}" fill="none" stroke="var(--border-strong)" stroke-width="1"/>')

    # Right calibrated colorbar legend
    bx, bw = x0 + gw + 24.0, 14.0
    parts.append(f'<rect x="{bx:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{gh:.1f}" fill="url(#{grad_id})" stroke="var(--border-strong)" stroke-width="1"/>')
    unit_hdr = unit if unit else z_lbl.split("/")[-1].strip()
    parts.append(halo_text(bx + bw / 2.0, y0 - 14.0, unit_hdr, anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
    ticks = sc["majors"]
    for idx, tv in enumerate(ticks):
        if len(ticks) > 4 and idx % 2 == 1 and idx != len(ticks) - 1:
            continue
        ty = y0 + gh - ((float(tv) - z_lo) / z_span) * gh
        parts.append(f'<line x1="{bx + bw:.1f}" y1="{ty:.1f}" x2="{bx + bw + 4:.1f}" y2="{ty:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
        parts.append(halo_text(bx + bw + 7.0, ty + 4.0, format_tick_numeral(tv, step=sc["step"]), anchor="start", size=11.5, fill="var(--text-secondary)", halo=False))

    y_axis_lbl = str(((spec.get("axes") or {}).get("y_axis") or {}).get("quantity_calculus") or "")
    if y_axis_lbl:
        parts.append(halo_text(14.0, y0 - 14.0, y_axis_lbl, anchor="start", size=11.5, weight="700", fill="var(--text-secondary)", halo=False, math=True))
    parts.append(halo_text(x0 + gw / 2.0, y0 + gh + 30.0, x_lbl, anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))
    parts.append("</svg>")
    return "\n".join(parts)
