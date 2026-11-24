# SPDX-License-Identifier: Apache-2.0
"""Civic & public-data plot compilers: paired subgroup bars + dual count/% slopegraph."""

from __future__ import annotations

import math
from typing import Any

from .svg_labels import halo_text, svg_knockout_label
from .tokens_and_scales import (
    SERIES_STYLES,
    compute_linear_125_scale,
    esc,
    finite_float,
    format_tick_numeral,
    resolve_token,
)


def _approx_px(text: str, font_size: float = 11.6) -> float:
    """Estimate proportional label width comfortably without external font dependencies."""
    units = 0.0
    for ch in str(text):
        if ord(ch) > 0x2E80:
            units += 1.05
        elif ch in "MW@#%&Q":
            units += 0.88
        elif ch in "ijlI1.,|:;' ":
            units += 0.34
        elif ch.isupper():
            units += 0.68
        else:
            units += 0.56
    return units * font_size + 4.0


def _decollide_ys(targets: list[tuple[int, float]], min_y: float, max_y: float, min_gap: float = 17.0) -> dict[int, float]:
    """Separate vertical anchor targets greedily while staying cleanly inside [min_y, max_y]."""
    if not targets:
        return {}
    ordered = sorted(targets, key=lambda kv: (kv[1], kv[0]))
    ys = [max(min_y, min(max_y, y)) for _, y in ordered]
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < min_gap:
            ys[i] = ys[i - 1] + min_gap
    if ys[-1] > max_y:
        ys[-1] = max_y
        for i in range(len(ys) - 2, -1, -1):
            if ys[i + 1] - ys[i] < min_gap:
                ys[i] = ys[i + 1] - min_gap
    if ys[0] < min_y:
        shift = min_y - ys[0]
        ys = [min(max_y, y + shift) for y in ys]
    return {ordered[i][0]: ys[i] for i in range(len(ordered))}


def _bar_ink(fill: str) -> str:
    """Choose WCAG-safe dark/light ink for explicit hex fills, or --text-on-accent for tokens."""
    s = str(fill or "").strip()
    if not s.startswith("#"):
        return "var(--text-on-accent, #FFFFFF)"
    h = s.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        return "var(--text-on-accent, #FFFFFF)"
    try:
        lin = [((int(h[i : i + 2], 16) / 255.0) / 12.92 if int(h[i : i + 2], 16) / 255.0 <= 0.03928 else ((int(h[i : i + 2], 16) / 255.0 + 0.055) / 1.055) ** 2.4) for i in (0, 2, 4)]
    except ValueError:
        return "var(--text-on-accent, #FFFFFF)"
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return "#FFFFFF" if (1.05 / (lum + 0.05)) > ((lum + 0.05) / 0.0585) else "#0F172A"


def _num(d: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    for k in keys:
        fv = finite_float(d.get(k))
        if fv is not None:
            return fv
    return default


def compile_paired_subgroup_bars(spec: dict[str, Any], rigor: str, medium: str, chrome: str = "bench") -> str:
    """Compile two-step subgroup comparison bars with shaded row-aligned Overall column."""
    groups = list(spec.get("groups") or spec.get("items") or [])
    sub_labels = list(spec.get("subgroups") or ["Group A", "Group B"])
    if len(sub_labels) < 2:
        sub_labels = [sub_labels[0] if sub_labels else "Group A", "Group B"]
    overall_lbl = str(spec.get("overall_label") or "Overall")
    unit = str(spec.get("unit") or "%").strip()
    dec_raw = spec.get("decimals")
    decimals = 1 if dec_raw is None else int(dec_raw)
    col_a = resolve_token(spec.get("color_a"), "var(--accent-focal)")
    col_b = resolve_token(spec.get("color_b"), "var(--status-ok)")

    vals: list[float] = [0.0]
    for g in groups:
        for k in ("a", "b", "overall"):
            fv = finite_float(g.get(k))
            if fv is not None:
                vals.append(fv)
    sc = compute_linear_125_scale(0.0, max(vals) * 1.08, target_ticks=4)
    wide_bench = chrome == "bench"
    vb_w = 880 if wide_bench else 640
    svg_cls = "qe-svg qe-svg-880" if wide_bench else "qe-svg qe-svg-640"
    x0, x_bar_max, x_col, col_w = (176.0, 712.0, 738.0, 128.0) if wide_bench else (160.0, 496.0, 520.0, 108.0)
    track_w = x_bar_max - x0 - 44.0
    row_h, y0 = 52.0, 44.0
    ph = max(92.0, len(groups) * row_h)
    vh = int(y0 + ph + 44)
    span = max(sc["max"] - sc["min"], 1e-9)
    px = lambda v: x0 + max(0.0, min(1.0, (float(v) - sc["min"]) / span)) * track_w
    fmt = lambda v: f"{v:.{decimals}f}{unit}" if unit == "%" else f"{v:.{decimals}f}"

    legend_html = (
        '<div class="qe-legend-series va-subgroup-legend">'
        f'<span><span class="va-hex-swatch" style="--swatch:{esc(col_a)}"></span> {esc(sub_labels[0])}</span>'
        f'<span><span class="va-hex-swatch" style="--swatch:{esc(col_b)}"></span> {esc(sub_labels[1])}</span>'
        f'<span><span class="va-hex-swatch is-overall" style="--swatch:var(--bg-elevated)"></span> {esc(overall_lbl)}</span>'
        "</div>"
    )
    title = str(spec.get("metadata", {}).get("title") or "Paired Subgroup Comparison")
    parts: list[str] = [f'<svg class="{svg_cls}" viewBox="0 0 {vb_w} {vh}" role="img" aria-label="{esc(title)}">']
    parts.append(f'<rect x="{x_col:.1f}" y="14" width="{col_w:.1f}" height="{y0 + ph - 14:.1f}" rx="4" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(halo_text(x_col + col_w / 2.0, 30.0, overall_lbl, anchor="middle", size=11.8, weight="700", fill="var(--text-primary)", halo=False))
    parts.append(f'<line x1="{x_col - 10:.1f}" y1="16" x2="{x_col - 10:.1f}" y2="{y0 + ph:.1f}" stroke="var(--border-hairline)" stroke-width="1"/>')
    for xv in sc["majors"]:
        xx = px(xv)
        parts.append(f'<line x1="{xx:.1f}" y1="{y0 - 4:.1f}" x2="{xx:.1f}" y2="{y0 + ph:.1f}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(xx, y0 + ph + 18.0, format_tick_numeral(xv, step=sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(f'<line x1="{x0:.1f}" y1="{y0 - 4:.1f}" x2="{x0:.1f}" y2="{y0 + ph:.1f}" stroke="var(--text-primary)" stroke-width="1.1"/>')

    for i, g in enumerate(groups):
        cy = y0 + (i + 0.5) * row_h
        lbl = str(g.get("label") or f"Group {i + 1}")
        parts.append(f'<line x1="12" y1="{y0 + (i + 1) * row_h:.1f}" x2="{x_col + col_w:.1f}" y2="{y0 + (i + 1) * row_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.7"/>')
        parts.append(halo_text(x0 - 10.0, cy + 4.0, lbl, anchor="end", size=11.8, weight="600", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        for _idx_sub, (key, col, dy_off) in enumerate((("a", col_a, -18.5), ("b", col_b, 1.5))):
            val = finite_float(g.get(key), 0.0) or 0.0
            bw = max(2.0, px(val) - x0)
            by = cy + dy_off
            parts.append(f'<rect x="{x0:.1f}" y="{by:.1f}" width="{bw:.1f}" height="16.5" rx="2" fill="{esc(col)}"/>')
            v_txt = fmt(val)
            txt_w = _approx_px(v_txt, 11.5)
            if bw >= txt_w + 16.0:
                parts.append(halo_text(x0 + bw - 6.0, by + 12.2, v_txt, anchor="end", size=11.5, weight="700", fill=_bar_ink(col), halo=False))
            else:
                parts.append(halo_text(x0 + bw + 6.0, by + 12.2, v_txt, anchor="start", size=11.5, weight="600", fill="var(--text-primary)", halo=True))
        ov = finite_float(g.get("overall"))
        ov_txt = fmt(ov) if ov is not None else "—"
        parts.append(halo_text(x_col + col_w / 2.0, cy + 4.5, ov_txt, anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False))

    parts.append("</svg>")
    return f'{legend_html}<div class="va-figure-scroll">{chr(10).join(parts)}</div>'


def _crossover_coords(pts_list: list[tuple[float, float, float, float]]) -> tuple[float, float] | None:
    """Find crossing point (px_frac, y_norm) between first crossing pair in list of (y1, y2, py1, py2)."""
    n = len(pts_list)
    for i in range(n):
        for j in range(i + 1, n):
            a1, a2, ya1, ya2 = pts_list[i]
            b1, b2, yb1, yb2 = pts_list[j]
            d1, d2 = a1 - b1, a2 - b2
            if d1 * d2 < 0 and abs(d1 - d2) > 1e-6:
                t = abs(d1) / abs(d1 - d2)
                return t, ya1 + t * (ya2 - ya1)
    return None


def compile_dual_slopegraph(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile side-by-side Count | % Share dual slopegraph with step-leader gutter & unit-once top row."""
    rows = list(spec.get("series") or spec.get("items") or [])
    left_title = str(spec.get("left_title") or "Total Count")
    right_title = str(spec.get("right_title") or "Share of Total")
    left_unit = str(spec.get("left_unit") or "B").strip()
    right_unit = str(spec.get("right_unit") or "%").strip()
    t0_lbl = str(spec.get("start_label") or "Baseline")
    t1_lbl = str(spec.get("end_label") or "Current")
    l_dec = 1 if spec.get("left_decimals") is None else int(spec["left_decimals"])
    r_dec = 1 if spec.get("right_decimals") is None else int(spec["right_decimals"])

    y_top, y_bot = 68.0, 274.0
    l_vals = [_num(r, k) for r in rows for k in ("left_start", "left_end")] or [0.0, 1.0]
    r_vals = [_num(r, k, k.replace("right_", "pct_")) for r in rows for k in ("right_start", "right_end")] or [0.0, 1.0]
    l_lo, l_hi = min(l_vals), max(l_vals)
    r_lo, r_hi = min(r_vals), max(r_vals)
    l_pad_lo = max(0.0, l_lo - max(l_hi - l_lo, 1.0) * 0.08) if l_lo >= 0.0 else (l_lo - max(l_hi - l_lo, 1.0) * 0.08)
    r_pad_lo = max(0.0, r_lo - max(r_hi - r_lo, 1.0) * 0.08) if r_lo >= 0.0 else (r_lo - max(r_hi - r_lo, 1.0) * 0.08)
    l_sc = compute_linear_125_scale(l_pad_lo, l_hi + max(l_hi - l_lo, 1.0) * 0.06, target_ticks=4)
    r_sc = compute_linear_125_scale(r_pad_lo, r_hi + max(r_hi - r_lo, 1.0) * 0.06, target_ticks=4)
    l_span, r_span = max(l_sc["max"] - l_sc["min"], 1e-9), max(r_sc["max"] - r_sc["min"], 1e-9)
    py_l = lambda v: y_bot - ((float(v) - l_sc["min"]) / l_span) * (y_bot - y_top)
    py_r = lambda v: y_bot - ((float(v) - r_sc["min"]) / r_span) * (y_bot - y_top)

    top_l0 = min(range(len(rows)), key=lambda i: py_l(_num(rows[i], "left_start"))) if rows else -1
    top_l1 = min(range(len(rows)), key=lambda i: py_l(_num(rows[i], "left_end"))) if rows else -1
    top_r0 = min(range(len(rows)), key=lambda i: py_r(_num(rows[i], "right_start", "pct_start"))) if rows else -1
    top_r1 = min(range(len(rows)), key=lambda i: py_r(_num(rows[i], "right_end", "pct_end"))) if rows else -1

    max_gutter_txt = max(
        (_approx_px(f"{_num(r, 'right_end', 'pct_end'):.{r_dec}f}{right_unit if idx == top_r1 else ''} · {r.get('label') or f'Series {idx + 1}'}", 11.5) for idx, r in enumerate(rows)),
        default=110.0,
    )
    gutter_w = min(280.0, max(128.0, max_gutter_txt + 8.0))
    xr2 = max(310.0, 632.0 - gutter_w - 26.0)
    xr1 = max(254.0, xr2 - 74.0)
    x_sep = xr1 - 48.0
    xl2 = x_sep - 48.0
    xl1 = 68.0

    palette = [resolve_token(r.get("color"), SERIES_STYLES[i % len(SERIES_STYLES)]["stroke"]) for i, r in enumerate(rows)]

    yl0_map = _decollide_ys([(i, py_l(_num(r, "left_start"))) for i, r in enumerate(rows)], y_top - 4, y_bot + 10, 16.5)
    yl1_map = _decollide_ys([(i, py_l(_num(r, "left_end"))) for i, r in enumerate(rows)], y_top - 4, y_bot + 10, 16.5)
    yr0_map = _decollide_ys([(i, py_r(_num(r, "right_start", "pct_start"))) for i, r in enumerate(rows)], y_top - 4, y_bot + 10, 16.5)
    yr1_map = _decollide_ys([(i, py_r(_num(r, "right_end", "pct_end"))) for i, r in enumerate(rows)], y_top - 4, y_bot + 10, 18.0)

    title = str(spec.get("metadata", {}).get("title") or "Count and Share Dual Slopegraph")
    parts: list[str] = [f'<svg class="qe-svg qe-svg-640" viewBox="0 0 640 310" role="img" aria-label="{esc(title)}">']
    parts.append(halo_text((xl1 + xl2) / 2.0, 24.0, left_title, anchor="middle", size=12.2, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
    parts.append(halo_text((xr1 + xr2) / 2.0, 24.0, right_title, anchor="middle", size=12.2, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
    parts.append(f'<line x1="{x_sep:.1f}" y1="16" x2="{x_sep:.1f}" y2="{y_bot + 22:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
    for xx, txt in ((xl1, t0_lbl), (xl2, t1_lbl), (xr1, t0_lbl), (xr2, t1_lbl)):
        parts.append(f'<line x1="{xx:.1f}" y1="{y_top - 8:.1f}" x2="{xx:.1f}" y2="{y_bot + 4:.1f}" stroke="var(--border-hairline)" stroke-width="1"/>')
        parts.append(halo_text(xx, y_bot + 22.0, txt, anchor="middle", size=11.5, weight="600", fill="var(--text-secondary)", halo=False))

    right_coords: list[tuple[float, float, float, float]] = []
    for i, r in enumerate(rows):
        col = palette[i]
        ls, le = _num(r, "left_start"), _num(r, "left_end")
        rs, re_v = _num(r, "right_start", "pct_start"), _num(r, "right_end", "pct_end")
        yls, yle, yrs, yre = py_l(ls), py_l(le), py_r(rs), py_r(re_v)
        right_coords.append((rs, re_v, yrs, yre))

        parts.append(f'<line x1="{xl1:.1f}" y1="{yls:.1f}" x2="{xl2:.1f}" y2="{yle:.1f}" stroke="{esc(col)}" stroke-width="2.2"/>')
        parts.append(f'<circle cx="{xl1:.1f}" cy="{yls:.1f}" r="4.0" fill="var(--bg-canvas)" stroke="{esc(col)}" stroke-width="2.1"/>')
        parts.append(f'<circle cx="{xl2:.1f}" cy="{yle:.1f}" r="4.0" fill="var(--bg-canvas)" stroke="{esc(col)}" stroke-width="2.1"/>')
        ls_txt = f"{ls:.{l_dec}f}{left_unit if i == top_l0 else ''}"
        le_txt = f"{le:.{l_dec}f}{left_unit if i == top_l1 else ''}"
        parts.append(halo_text(xl1 - 9.0, yl0_map[i] + 4.0, ls_txt, anchor="end", size=11.5, weight="600", fill=col, halo=True))
        parts.append(halo_text(xl2 + 9.0, yl1_map[i] + 4.0, le_txt, anchor="start", size=11.5, weight="600", fill=col, halo=True))

        parts.append(f'<line x1="{xr1:.1f}" y1="{yrs:.1f}" x2="{xr2:.1f}" y2="{yre:.1f}" stroke="{esc(col)}" stroke-width="2.2"/>')
        parts.append(f'<circle cx="{xr1:.1f}" cy="{yrs:.1f}" r="4.0" fill="var(--bg-canvas)" stroke="{esc(col)}" stroke-width="2.1"/>')
        parts.append(f'<circle cx="{xr2:.1f}" cy="{yre:.1f}" r="4.0" fill="var(--bg-canvas)" stroke="{esc(col)}" stroke-width="2.1"/>')
        rs_txt = f"{rs:.{r_dec}f}{right_unit if i == top_r0 else ''}"
        re_txt = f"{re_v:.{r_dec}f}{right_unit if i == top_r1 else ''} · {r.get('label') or f'Series {i+1}'}"
        parts.append(halo_text(xr1 - 9.0, yr0_map[i] + 4.0, rs_txt, anchor="end", size=11.5, weight="600", fill=col, halo=True))
        ty_r, elbow_x = yr1_map[i], xr2 + 8.0
        parts.append(f'<polyline fill="none" stroke="{esc(col)}" stroke-width="1.1" opacity="0.7" points="{xr2 + 5:.1f},{yre:.1f} {elbow_x:.1f},{yre:.1f} {elbow_x + 7:.1f},{ty_r:.1f} {elbow_x + 12:.1f},{ty_r:.1f}"/>')
        parts.append(halo_text(elbow_x + 15.0, ty_r + 4.0, re_txt, anchor="start", size=11.5, weight="700", font="var(--font-sans)", fill=col, halo=False))

    cross_cfg = spec.get("crossover") or {}
    cross = _crossover_coords(right_coords)
    if cross and cross_cfg.get("label"):
        t_c, cy_c = cross
        cx_c = xr1 + t_c * (xr2 - xr1)
        cy_lbl = max(y_top + 14.0, cy_c - 22.0)
        parts.append(f'<circle cx="{cx_c:.1f}" cy="{cy_c:.1f}" r="3.6" fill="var(--bg-canvas)" stroke="var(--text-primary)" stroke-width="1.6"/>')
        parts.append(f'<line x1="{cx_c:.1f}" y1="{cy_c - 4:.1f}" x2="{cx_c:.1f}" y2="{cy_lbl + 4:.1f}" stroke="var(--text-secondary)" stroke-width="1.0" stroke-dasharray="2,2"/>')
        parts.append(svg_knockout_label(cx_c, cy_lbl, str(cross_cfg["label"]), anchor="middle", size=11.4, weight="600", fill="var(--text-primary)", surface_fill="var(--bg-canvas)", x_bounds=(xr1 + 4.0, xr2 - 4.0)))

    parts.append("</svg>")
    return f'<div class="va-figure-scroll">{chr(10).join(parts)}</div>'
