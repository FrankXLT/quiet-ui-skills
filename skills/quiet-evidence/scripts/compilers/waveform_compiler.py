# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 5 (Waveforms, Day-Arcs, Sequence & HIL Scopes)."""

from __future__ import annotations

import json
import math
from typing import Any

from .svg_labels import avoid_label_overlaps, halo_text, svg_knockout_label
from .tokens_and_scales import (
    SERIES_STYLES,
    compute_linear_125_scale,
    esc,
    format_math_html,
    format_math_svg,
    format_tick_numeral,
    render_test_condition_strip,
    resolve_token,
)

_TIME_UNIT_SECONDS = {"fs": 1e-15, "ps": 1e-12, "ns": 1e-9, "µs": 1e-6, "us": 1e-6, "ms": 1e-3, "s": 1.0, "min": 60.0, "h": 3600.0}


def _safe_float(val: Any) -> float | None:
    """Return finite float or None for null, bool, non-numeric, or NaN/Inf values."""
    if val is None or isinstance(val, bool):
        return None
    try:
        out = float(val)
        return out if math.isfinite(out) else None
    except (TypeError, ValueError):
        return None


def _format_freq_reciprocal(dt: float, t_unit: str) -> str:
    scale_s = _TIME_UNIT_SECONDS.get(t_unit.strip())
    if not scale_s or dt <= 0.0:
        return ""
    freq = 1.0 / (dt * scale_s)
    for thresh, suffix in ((1e9, "GHz"), (1e6, "MHz"), (1e3, "kHz"), (1.0, "Hz")):
        if freq >= thresh:
            return f" (1/Δt = {freq / thresh:.2f}\u00a0{suffix})"
    return f" (1/Δt = {freq:.3g}\u00a0Hz)"


def _format_gap_dur(dur: float) -> str:
    return f"{dur:.1f}" if abs(dur - round(dur, 1)) < 0.02 else f"{dur:.2f}".rstrip("0").rstrip(".")


def _compile_day_arc(spec: dict[str, Any]) -> str:
    """Compile L1 24-hour operational phase-arc timeline."""
    phases = spec.get("phases", [])
    x0, y0, pw, bh = 54.0, 48.0, 612.0, 28.0
    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 132" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "24h Phase Timeline"))}">',
        f'<rect data-role="track" x="{x0}" y="{y0}" width="{pw}" height="{bh}" rx="4" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1"/>',
    ]
    for ph in phases:
        s_h, e_h = float(ph["start_h"]), float(ph["end_h"])
        px0, px1 = x0 + (s_h / 24.0) * pw, x0 + (e_h / 24.0) * pw
        col, bg = resolve_token(ph.get("color"), "var(--accent-focal)"), resolve_token(ph.get("bg"), "var(--tint-indigo-bg)")
        parts.append(f'<rect data-role="phase" x="{px0:.1f}" y="{y0 + 1:.1f}" width="{max(4.0, px1 - px0):.1f}" height="{bh - 2:.1f}" fill="{bg}" stroke="{col}" stroke-width="1.2"/>')
        lbl_txt = str(ph["label"])
        if px1 - px0 >= len(lbl_txt) * 8.0 + 12.0:
            parts.append(halo_text((px0 + px1) / 2.0, y0 + 18.0, lbl_txt, anchor="middle", size=11.5, weight="700", fill=col, halo=False))
    for h in range(0, 25, 4):
        tx = x0 + (h / 24.0) * pw
        parts.append(f'<line x1="{tx:.1f}" y1="{y0 + bh}" x2="{tx:.1f}" y2="{y0 + bh + 5}" stroke="var(--border-strong)" stroke-width="1"/>')
        parts.append(halo_text(tx, y0 + bh + 19.0, f"{h:02d}:00", anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
    for ev in spec.get("events", []):
        ex = x0 + (float(ev["hour"]) / 24.0) * pw
        ecol = resolve_token(ev.get("color"), "var(--status-warn)")
        parts.append(f'<line x1="{ex:.1f}" y1="{y0 - 8}" x2="{ex:.1f}" y2="{y0 + bh + 2}" stroke="{ecol}" stroke-width="1.6" stroke-dasharray="3,2"/>')
        parts.append(svg_knockout_label(ex, y0 - 15.0, str(ev["label"]), anchor="middle", size=11.5, weight="700", fill=ecol, surface_fill="var(--bg-surface)", x_bounds=(8.0, 712.0), math=False))
    parts.append("</svg>")
    return "\n".join(parts)


def _compile_sequence(spec: dict[str, Any]) -> str:
    """Compile L2 4-lifeline protocol/runbook sequence diagram with interlocks."""
    actors = spec.get("actors", [])
    steps = spec.get("steps", [])
    vb_w, step_h, y_hdr, hdr_h = 720, 48.0, 16.0, 28.0
    y_start = y_hdr + hdr_h + 30.0
    vb_h = int(y_start + len(steps) * step_h + 22.0)
    col_w = (vb_w - 80.0) / max(len(actors), 1)
    cx_map: dict[str, float] = {}

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 {vb_w} {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Sequence Interlock"))}">',
        "<defs>"
        '<marker id="qe-seq-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-primary)"/></marker>'
        '<marker id="qe-seq-focal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--accent-focal)"/></marker>'
        '<marker id="qe-seq-ok" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-ok)"/></marker>'
        "</defs>",
    ]
    for i, act in enumerate(actors):
        cx = 40.0 + (i + 0.5) * col_w
        cx_map[act["id"]] = cx
        bw = min(136.0, col_w - 14.0)
        parts.append(f'<rect data-role="node" x="{cx - bw / 2:.1f}" y="{y_hdr}" width="{bw:.1f}" height="{hdr_h}" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.3"/>')
        parts.append(halo_text(cx, y_hdr + 18.0, str(act["label"]), anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
        parts.append(f'<line x1="{cx:.1f}" y1="{y_hdr + hdr_h}" x2="{cx:.1f}" y2="{vb_h - 14}" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="3,3"/>')

    for idx, st in enumerate(steps):
        sy = y_start + idx * step_h
        x1, x2 = cx_map.get(st["from"], 80.0), cx_map.get(st["to"], 240.0)
        status = str(st.get("status", "neutral")).lower()
        stroke, mk = ("var(--accent-focal)", "qe-seq-focal") if status == "focal" else (("var(--status-ok)", "qe-seq-ok") if status == "ok" else ("var(--text-primary)", "qe-seq-arr"))
        dash = ' stroke-dasharray="5,3"' if st.get("style") == "dashed" else ""
        parts.append(f'<line x1="{x1:.1f}" y1="{sy:.1f}" x2="{x2:.1f}" y2="{sy:.1f}" stroke="{stroke}" stroke-width="1.6"{dash} marker-end="url(#{mk})"/>')
        parts.append(svg_knockout_label((x1 + x2) / 2.0, sy - 10.0, str(st["label"]), anchor="middle", size=11.5, weight="600", fill=stroke, surface_fill="var(--bg-surface)", x_bounds=(8.0, 712.0), math=False))
    parts.append("</svg>")
    return "\n".join(parts)


def _resolve_analog_domain(ch: dict[str, Any]) -> tuple[float, float]:
    """Resolve [y_min, y_max] from explicit domain, V/div scale, or 1-2-5 snapped data."""
    dom = ch.get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) >= 2:
        lo, hi = _safe_float(dom[0]), _safe_float(dom[1])
        if lo is not None and hi is not None and hi > lo:
            return lo, hi
    if (sd := _safe_float(ch.get("vertical_scale_per_div"))) is not None:
        sd = abs(sd) or 1.0
        return -2.0 * sd, 2.0 * sd
    vals = [fv for s in ch.get("samples", []) if isinstance(s, (list, tuple)) and len(s) >= 2 and (fv := _safe_float(s[1])) is not None]
    for env in ch.get("threshold_envelopes", []):
        if (ev := _safe_float(env.get("value"))) is not None:
            vals.append(ev)
    if not vals:
        return -1.0, 1.0
    lo_raw, hi_raw = min(vals), max(vals)
    lo_raw = 0.0 if (lo_raw >= 0.0 and lo_raw < 0.7 * hi_raw) else lo_raw
    sc = compute_linear_125_scale(lo_raw, hi_raw, target_ticks=4)
    return float(sc["min"]), float(sc["max"])


def _project_analog_y(val: float, y_min: float, y_max: float, y_hi_px: float, y_lo_px: float) -> float:
    span = y_max - y_min if y_max > y_min else 1.0
    return max(y_hi_px, min(y_lo_px, y_lo_px - ((val - y_min) / span) * (y_lo_px - y_hi_px)))


def _analog_segments(
    samples: list[Any], t_min: float, t_span: float, x0: float, pw: float,
    y_hi_px: float, y_lo_px: float, y_min: float, y_max: float, max_gap: float,
) -> tuple[list[str], list[tuple[float, float]]]:
    """Build piecewise linear path strings breaking cleanly across null/timeout dropouts."""
    t_span = t_span if (math.isfinite(t_span) and t_span > 0.0) else 1.0
    segs, gaps, cur, prev_t, drop_start = [], [], [], None, None
    for s in samples:
        if not isinstance(s, (list, tuple)) or len(s) < 2:
            continue
        t, v = _safe_float(s[0]), _safe_float(s[1])
        if t is None or v is None:
            if cur:
                segs.append(" ".join(cur)); cur = []
            if drop_start is None and t is not None:
                drop_start = prev_t if prev_t is not None else t
            prev_t = t if t is not None else prev_t
            continue
        if drop_start is not None:
            gaps.append((drop_start, t)); drop_start = None
        elif prev_t is not None and (t - prev_t) > max_gap and cur:
            segs.append(" ".join(cur)); cur = []; gaps.append((prev_t, t))
        px = x0 + ((t - t_min) / t_span) * pw
        py = _project_analog_y(v, y_min, y_max, y_hi_px, y_lo_px)
        cur.append(f'{"M" if not cur else "L"} {px:.1f} {py:.1f}')
        prev_t = t
    if cur:
        segs.append(" ".join(cur))
    return segs, gaps


def _digital_segments(
    samples: list[Any], t_min: float, t_span: float, x0: float, pw: float, y_top: float, lane_h: float,
) -> tuple[list[str], list[tuple[float, float]]]:
    """Build step-after orthogonal digital / Manchester II path segments breaking at None."""
    t_span = t_span if (math.isfinite(t_span) and t_span > 0.0) else 1.0
    segs, gaps, cur, prev_py, prev_t, drop_start = [], [], [], None, None, None
    y_lo, y_mid, y_hi = y_top + lane_h - 10.0, y_top + lane_h / 2.0, y_top + 10.0
    for s in samples:
        if not isinstance(s, (list, tuple)) or len(s) < 2:
            continue
        t, v = _safe_float(s[0]), _safe_float(s[1])
        if t is None or v is None:
            if cur:
                segs.append(" ".join(cur)); cur = []
            if drop_start is None and t is not None:
                drop_start = prev_t if prev_t is not None else t
            prev_py = None
            prev_t = t if t is not None else prev_t
            continue
        if drop_start is not None:
            gaps.append((drop_start, t)); drop_start = None
        px = x0 + ((t - t_min) / t_span) * pw
        py = y_hi if v > 0.2 else (y_lo if v < -0.2 or v == 0 else y_mid)
        cur.append(f"M {px:.1f} {py:.1f}" if not cur else (f"H {px:.1f} V {py:.1f}" if (prev_py is not None and py != prev_py) else f"H {px:.1f}"))
        prev_py, prev_t = py, t
    if cur:
        segs.append(" ".join(cur))
    return segs, gaps


def _collect_scope_gaps(
    vis_ch: list[dict[str, Any]], t_min: float, t_span: float, x0: float, pw: float, wave_h: float, max_gap: float,
) -> list[tuple[float, float]]:
    raw_gaps: list[tuple[float, float]] = []
    for ch in vis_ch:
        samples = ch.get("samples", [])
        if ch.get("type") == "digital":
            _, g_list = _digital_segments(samples, t_min, t_span, x0, pw, 0.0, wave_h)
        else:
            y_min, y_max = _resolve_analog_domain(ch)
            _, g_list = _analog_segments(samples, t_min, t_span, x0, pw, 4.0, wave_h - 4.0, y_min, y_max, max_gap)
        raw_gaps.extend(g_list)
    tol = max(t_span * 1e-3, t_span * (5.0 / pw))
    unique_gaps: list[tuple[float, float]] = []
    for gt0, gt1 in sorted(raw_gaps):
        if not unique_gaps or gt0 > unique_gaps[-1][1] + tol:
            unique_gaps.append((gt0, gt1))
        else:
            unique_gaps[-1] = (unique_gaps[-1][0], max(unique_gaps[-1][1], gt1))
    return unique_gaps


def _render_analog_channel(
    parts: list[str], ch: dict[str, Any], t_min: float, t_span: float,
    x0: float, pw: float, wave_top: float, wave_h: float, ly: float, lane_h: float, max_gap: float, rigor: str,
) -> tuple[list[str], list[tuple[float, float]]]:
    y_min, y_max = _resolve_analog_domain(ch)
    y_hi_px, y_lo_px = wave_top + 4.0, ly + lane_h - 4.0
    ym = wave_top + wave_h / 2.0
    is_bipolar = y_min < 0.0 < y_max
    y_mid_px = _project_analog_y(0.0, y_min, y_max, y_hi_px, y_lo_px) if is_bipolar else ym
    step = (y_max - y_min) / 2.0
    top_lbl = f"+{format_tick_numeral(y_max, step=step)}" if (is_bipolar and y_max > 0) else format_tick_numeral(y_max, step=step)
    bot_lbl = format_tick_numeral(y_min, step=step)
    mid_lbl = "0 ▶" if is_bipolar else format_tick_numeral(0.5 * (y_min + y_max), step=step)

    parts.append(f'<line x1="{x0}" y1="{y_mid_px:.1f}" x2="{x0 + pw}" y2="{y_mid_px:.1f}" stroke="var(--border-hairline)" stroke-width="0.8" stroke-dasharray="2,3"/>')
    for ty in (y_hi_px, y_mid_px, y_lo_px):
        parts.append(f'<line x1="{x0 - 4}" y1="{ty:.1f}" x2="{x0}" y2="{ty:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(halo_text(x0 - 7.0, wave_top + 13.0, top_lbl, anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    if (y_mid_px - y_hi_px >= 13.0 and y_lo_px - y_mid_px >= 13.0) or not is_bipolar:
        parts.append(halo_text(x0 - 7.0, y_mid_px + 4.0, mid_lbl, anchor="end", size=11.5, weight="700" if is_bipolar else "500", fill="var(--text-muted)" if is_bipolar else "var(--text-secondary)", halo=False))
    parts.append(halo_text(x0 - 7.0, ly + lane_h - 3.0, bot_lbl, anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))

    if rigor in {"L2", "L3"}:
        thr_cands: list[dict[str, Any]] = []
        unit = str(ch.get("unit", "")).strip()
        for env in ch.get("threshold_envelopes", []):
            ev_val = _safe_float(env.get("value"))
            if ev_val is None:
                continue
            ev_y = _project_analog_y(ev_val, y_min, y_max, y_hi_px, y_lo_px)
            ecol = resolve_token(env.get("color"), "var(--status-danger)")
            parts.append(f'<line x1="{x0}" y1="{ev_y:.1f}" x2="{x0 + pw + 5:.1f}" y2="{ev_y:.1f}" stroke="{ecol}" stroke-width="1.2" stroke-dasharray="4,3"/>')
            txt = f"{f'{ev_val:+g}' if is_bipolar else f'{ev_val:g}'}\u00a0{unit}" if unit else (f"{ev_val:+g}" if is_bipolar else f"{ev_val:g}")
            thr_cands.append({"x": x0 + pw + 8.0, "y": ev_y + 4.0, "text": txt, "anchor": "start", "fill": ecol, "w": 84.0})
        for th in avoid_label_overlaps(thr_cands, min_y=wave_top + 11.0, max_y=ly + lane_h - 3.0, step_y=14.0):
            parts.append(halo_text(th["x"], th["y"], th["text"], anchor="start", size=11.5, weight="700", fill=th["fill"], halo=False))

    return _analog_segments(ch.get("samples", []), t_min, t_span, x0, pw, y_hi_px, y_lo_px, y_min, y_max, max_gap)


def _render_cursor_overlays(
    parts: list[str], cursor_xs: list[tuple[float, str, str]],
    unique_gaps: list[tuple[float, float]], has_dropouts: bool,
    t_min: float, t_span: float, t_unit: str, x0: float, pw: float, y0: float,
) -> None:
    cy_lbl = 14.0 if has_dropouts else (y0 - 8.0)
    if len(cursor_xs) == 1:
        cx, ccol, clbl = cursor_xs[0]
        half_w = len(clbl) * 3.6 + 6.0
        parts.append(halo_text(max(x0 + half_w, min(712.0 - half_w, cx)), cy_lbl, clbl, anchor="middle", size=11.5, weight="700", fill=ccol, math=True))
    elif len(cursor_xs) >= 2:
        (ax, acol, albl), (bx, bcol, blbl) = sorted(cursor_xs, key=lambda c: c[0])[:2]
        wa, wb = len(albl) * 7.2 + 8.0, len(blbl) * 7.2 + 8.0
        if (bx - wb / 2.0) - (ax + wa / 2.0) < 10.0 or bx + wb / 2.0 > 712.0 or ax - wa / 2.0 < x0:
            tax = max(x0 + wa, min(710.0 - wb - 12.0, ax - 4.0))
            tbx = max(tax + 10.0, min(712.0 - wb, bx + 4.0))
            parts.append(halo_text(tax, cy_lbl, albl, anchor="end", size=11.5, weight="700", fill=acol, math=True))
            parts.append(halo_text(tbx, cy_lbl, blbl, anchor="start", size=11.5, weight="700", fill=bcol, math=True))
        else:
            parts.append(halo_text(ax, cy_lbl, albl, anchor="middle", size=11.5, weight="700", fill=acol, math=True))
            parts.append(halo_text(bx, cy_lbl, blbl, anchor="middle", size=11.5, weight="700", fill=bcol, math=True))
    if has_dropouts:
        span_y = y0 - 5.0
        for gt0, gt1 in unique_gaps:
            gx0, gx1 = x0 + ((gt0 - t_min) / t_span) * pw, x0 + ((gt1 - t_min) / t_span) * pw
            parts.append(f'<line x1="{gx0:.1f}" y1="{span_y - 4:.1f}" x2="{gx0:.1f}" y2="{span_y + 3:.1f}" stroke="var(--status-danger)" stroke-width="1.3"/>')
            parts.append(f'<line x1="{gx1:.1f}" y1="{span_y - 4:.1f}" x2="{gx1:.1f}" y2="{span_y + 3:.1f}" stroke="var(--status-danger)" stroke-width="1.3"/>')
            parts.append(f'<line x1="{gx0:.1f}" y1="{span_y:.1f}" x2="{gx1:.1f}" y2="{span_y:.1f}" stroke="var(--status-danger)" stroke-width="1.2"/>')
            parts.append(svg_knockout_label((gx0 + gx1) / 2.0, span_y - 5.0, f"DROPOUT {_format_gap_dur(gt1 - gt0)}\u00a0{t_unit}", anchor="middle", size=11.5, weight="700", fill="var(--status-danger)", surface_fill="var(--bg-surface)", x_bounds=(x0 + 4.0, x0 + pw - 4.0), math=False))


def _resolve_timebase(tb: dict[str, Any], vis_ch: list[dict[str, Any]]) -> tuple[float, float]:
    dom = tb.get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) >= 2:
        lo, hi = _safe_float(dom[0]), _safe_float(dom[1])
        if lo is not None and hi is not None and hi > lo:
            return lo, hi - lo
    t_min = _safe_float(tb.get("start_time")) or 0.0
    t_span = _safe_float(tb.get("total_span_us", tb.get("total_span", 20.0)))
    if t_span is not None and t_span > 0.0:
        return t_min, t_span
    ts = [ft for ch in vis_ch for s in ch.get("samples", []) if isinstance(s, (list, tuple)) and s and (ft := _safe_float(s[0])) is not None]
    return (min(ts), max(ts) - min(ts)) if len(ts) >= 2 and max(ts) > min(ts) else (t_min, 1.0)


def _render_scope_lane(
    parts: list[str], idx: int, ch: dict[str, Any], ly: float, lane_h: float, hdr_h: float,
    x0: float, pw: float, t_min: float, t_span: float, t_sc: dict[str, Any],
    minor_cls: str, max_gap: float, rigor: str, cursor_xs: list[tuple[float, str, str]],
) -> dict[str, Any]:
    wave_top, wave_h = ly + hdr_h, lane_h - hdr_h
    t_max = t_min + t_span
    col = resolve_token(ch.get("trace_color"), SERIES_STYLES[idx % len(SERIES_STYLES)]["stroke"])
    parts.append(f'<rect data-role="channel" x="{x0}" y="{ly:.1f}" width="{pw}" height="{lane_h:.1f}" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(f'<rect data-role="channel-hdr" x="{x0 + 0.5:.1f}" y="{ly + 0.5:.1f}" width="{pw - 1:.1f}" height="{hdr_h - 0.5:.1f}" fill="var(--bg-elevated)"/>')
    parts.append(f'<line x1="{x0}" y1="{wave_top:.1f}" x2="{x0 + pw}" y2="{wave_top:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')
    for xm in t_sc["minors"]:
        if t_min <= xm <= t_max:
            px = x0 + ((xm - t_min) / t_span) * pw
            parts.append(f'<line class="{minor_cls}" x1="{px:.1f}" y1="{wave_top:.1f}" x2="{px:.1f}" y2="{ly + lane_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.5" stroke-dasharray="1,3"/>')
    for xmaj in t_sc["majors"]:
        if t_min - 1e-9 <= xmaj <= t_max + 1e-9:
            px = x0 + ((xmaj - t_min) / t_span) * pw
            parts.append(f'<line x1="{px:.1f}" y1="{wave_top:.1f}" x2="{px:.1f}" y2="{ly + lane_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')
    parts.append(halo_text(x0 - 8.0, ly + 15.0, str(ch.get("id", f"CH{idx + 1}")).upper(), anchor="end", size=11.5, weight="700", fill=col, halo=False))
    ch_hdr = f'{ch.get("name", "")} ({ch.get("quantity_calculus", ch.get("unit", ""))})'
    parts.append(f'<text x="{x0 + 8.0:.1f}" y="{ly + 15.0:.1f}" text-anchor="start" font-family="var(--font-mono)" font-size="11.5" font-weight="600" fill="var(--text-primary)">{format_math_svg(ch_hdr, 8.8)}</text>')

    samples = ch.get("samples", [])
    if ch.get("type") == "digital":
        has_neg = any(isinstance(s, (list, tuple)) and len(s) >= 2 and (fv := _safe_float(s[1])) is not None and fv < 0 for s in samples)
        parts.append(f'<line x1="{x0 - 4}" y1="{wave_top + 10:.1f}" x2="{x0}" y2="{wave_top + 10:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
        parts.append(f'<line x1="{x0 - 4}" y1="{ly + lane_h - 10:.1f}" x2="{x0}" y2="{ly + lane_h - 10:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
        parts.append(halo_text(x0 - 7.0, wave_top + 14.0, "+1" if has_neg else "1", anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
        if has_neg:
            parts.append(halo_text(x0 - 7.0, wave_top + wave_h / 2.0 + 4.0, "0 ▶", anchor="end", size=11.5, weight="700", fill="var(--text-muted)", halo=False))
        parts.append(halo_text(x0 - 7.0, ly + lane_h - 6.0, "-1" if has_neg else "0", anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
        segs, gaps = _digital_segments(samples, t_min, t_span, x0, pw, wave_top, wave_h)
    else:
        segs, gaps = _render_analog_channel(parts, ch, t_min, t_span, x0, pw, wave_top, wave_h, ly, lane_h, max_gap, rigor)

    for gt0, gt1 in (gaps if rigor in {"L2", "L3"} else []):
        gx0, gx1 = x0 + ((gt0 - t_min) / t_span) * pw, x0 + ((gt1 - t_min) / t_span) * pw
        parts.append(f'<rect data-role="dropout-zone" x="{gx0:.1f}" y="{wave_top + 1:.1f}" width="{max(4.0, gx1 - gx0):.1f}" height="{wave_h - 2:.1f}" fill="var(--status-err-bg)" opacity="0.55"/>')
    for cx, ccol, _ in cursor_xs:
        parts.append(f'<line x1="{cx:.1f}" y1="{wave_top:.1f}" x2="{cx:.1f}" y2="{ly + lane_h:.1f}" stroke="{ccol}" stroke-width="1.4" stroke-dasharray="5,3"/>')
    if segs:
        parts.append(f'<path d="{" ".join(segs)}" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/>')
    return {"id": ch.get("id", f"ch{idx + 1}"), "name": ch.get("name", ""), "unit": ch.get("unit", ""), "samples": samples}


def _compile_scope(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile multi-channel time-synced HIL oscilloscope & Manchester II traces."""
    tb = spec.get("timebase", {})
    t_unit = str(tb.get("unit", "µs"))
    channels = spec.get("channels", [])
    vis_ch = channels[:1] if rigor == "L1" else channels
    t_min, t_span = _resolve_timebase(tb, vis_ch)
    t_max = t_min + t_span

    x0, pw, lane_h, hdr_h, lane_gap = 84.0, 536.0, 94.0, 22.0, 14.0
    wave_h = lane_h - hdr_h
    t_sc = compute_linear_125_scale(t_min, t_max, target_ticks=6)
    nom_dt = _safe_float(tb.get("nominal_dt"))
    mult = _safe_float(spec.get("dropout_handling", {}).get("detection_multiplier"))
    max_gap = max(1e-12, (nom_dt if (nom_dt and nom_dt > 0) else t_span / 40.0) * (mult if (mult and mult > 0) else 1.5))

    cursors = spec.get("cursors", {}) if rigor == "L3" else {}
    cursor_xs: list[tuple[float, str, str]] = []
    for ck in ("cursor_a", "cursor_b"):
        if (cur := cursors.get(ck)) and (ct := _safe_float(cur.get("time_us", cur.get("time", 0.0)))) is not None:
            cursor_xs.append((x0 + ((ct - t_min) / t_span) * pw, resolve_token(cur.get("stroke_color"), "var(--accent-primary)"), f'{cur.get("label", ck)}: {ct:.2f}\u00a0{t_unit}'))

    unique_gaps = _collect_scope_gaps(vis_ch, t_min, t_span, x0, pw, wave_h, max_gap)
    has_dropouts = bool(unique_gaps) and rigor in {"L2", "L3"}
    y0 = 46.0 if (has_dropouts and cursor_xs) else (34.0 if (has_dropouts or cursor_xs) else 24.0)
    tot_h = len(vis_ch) * lane_h + max(0, len(vis_ch) - 1) * lane_gap
    vb_h = int(y0 + tot_h + 44.0)

    parts = [f'<svg class="qe-svg qe-svg-720 qe-waveform-svg" data-qe-scope="true" tabindex="0" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Multi-Channel Scope"))}">']
    for xm in t_sc["minors"]:
        if t_min <= xm <= t_max:
            px = x0 + ((xm - t_min) / t_span) * pw
            parts.append(f'<line x1="{px:.1f}" y1="{y0 + tot_h}" x2="{px:.1f}" y2="{y0 + tot_h + 4}" stroke="var(--border-strong)" stroke-width="0.8"/>')
    for xmaj in t_sc["majors"]:
        if t_min - 1e-9 <= xmaj <= t_max + 1e-9:
            px = x0 + ((xmaj - t_min) / t_span) * pw
            parts.append(halo_text(px, y0 + tot_h + 18.0, format_tick_numeral(xmaj, step=t_sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(halo_text(max(140.0, min(580.0, x0 + pw / 2.0)), y0 + tot_h + 36.0, tb.get("quantity_calculus", f"t / {t_unit}"), anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))

    minor_cls = "qe-grid-minor" if medium == "m1" else "qe-grid-minor qe-m1-only"
    scope_meta_channels = [_render_scope_lane(parts, idx, ch, y0 + idx * (lane_h + lane_gap), lane_h, hdr_h, x0, pw, t_min, t_span, t_sc, minor_cls, max_gap, rigor, cursor_xs) for idx, ch in enumerate(vis_ch)]
    _render_cursor_overlays(parts, cursor_xs, unique_gaps, has_dropouts, t_min, t_span, t_unit, x0, pw, y0)
    parts.append(f'<line class="qe-live-cursor" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + tot_h}" stroke="var(--accent-focal)" stroke-width="1.3" visibility="hidden"/>')
    parts.append("</svg>")

    delta_banner = ""
    if rigor == "L3" and (ca := cursors.get("cursor_a")) and (cb := cursors.get("cursor_b")):
        ta, tb_v = _safe_float(ca.get("time_us", ca.get("time", 0.0))), _safe_float(cb.get("time_us", cb.get("time", 0.0)))
        if ta is not None and tb_v is not None:
            dt = abs(tb_v - ta)
            delta_banner = f'T_A = {ta:.2f}\u00a0{t_unit}  |  T_B = {tb_v:.2f}\u00a0{t_unit}  |  Δt = {dt:.2f}\u00a0{t_unit}{_format_freq_reciprocal(dt, t_unit)}'

    meta_json = json.dumps({"t_min": t_min, "t_span": t_span, "t_unit": t_unit, "max_gap": max_gap, "x0": x0, "pw": pw, "channels": scope_meta_channels}, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    def_msg = esc(delta_banner.replace("T_A", "TA").replace("T_B", "TB")) if delta_banner else "Hover, drag, or use Left/Right keys across channels to inspect timebase samples"
    def_html = format_math_html(delta_banner) if delta_banner else def_msg
    readout = f'<div class="qe-scope-readout va-nums" data-default="{def_msg}" aria-live="polite">{def_html}</div>'
    return f'<div class="va-figure-scroll qe-scope-scroll" tabindex="0" role="region" aria-label="{esc(spec.get("metadata", {}).get("title", "Scope"))}">{"".join(parts)}</div>{readout}<script type="application/json" class="qe-scope-data">{meta_json}</script>'


def compile_waveform(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white", chrome: str = "bench") -> str:
    """Compile Modality 5 (urn:quiet-ui:schema:v9:waveform) into HTML/SVG."""
    meta = spec.get("metadata", {})
    eff_rigor = (rigor or meta.get("rigor_level", "L3")).upper()
    kind = spec.get("waveform_kind", "scope")
    parts: list[str] = [f'<div class="qe-waveform-wrap" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}">']
    cond = render_test_condition_strip(spec.get("test_environment"), eff_rigor)
    if cond:
        parts.append(cond)
    if kind == "day_arc":
        parts.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Day Arc"))}">{_compile_day_arc(spec)}</div>')
    elif kind == "sequence":
        parts.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Sequence Diagram"))}">{_compile_sequence(spec)}</div>')
    else:
        parts.append(_compile_scope(spec, eff_rigor, medium))
    parts.append("</div>")
    return "\n".join(parts)
