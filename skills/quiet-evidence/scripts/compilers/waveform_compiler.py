# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 5 (Waveforms, Day-Arcs, Sequence & HIL Scopes)."""

from __future__ import annotations

import json
import math
from typing import Any

from .tokens_and_scales import (
    SERIES_STYLES,
    compute_linear_125_scale,
    esc,
    format_math_svg,
    format_tick_numeral,
    halo_text,
    pill_halo_text,
    render_test_condition_strip,
    resolve_token,
)

_TIME_UNIT_SECONDS: dict[str, float] = {
    "fs": 1e-15, "ps": 1e-12, "ns": 1e-9, "µs": 1e-6, "us": 1e-6,
    "ms": 1e-3, "s": 1.0, "min": 60.0, "h": 3600.0,
}


def _format_freq_reciprocal(dt: float, t_unit: str) -> str:
    scale_s = _TIME_UNIT_SECONDS.get(t_unit.strip())
    if not scale_s or dt <= 0.0:
        return ""
    freq = 1.0 / (dt * scale_s)
    for thresh, suffix in ((1e9, "GHz"), (1e6, "MHz"), (1e3, "kHz"), (1.0, "Hz")):
        if freq >= thresh:
            return f" (1/Δt = {freq / thresh:.2f}\u00a0{suffix})"
    return f" (1/Δt = {freq:.3g}\u00a0Hz)"


def _compile_day_arc(spec: dict[str, Any]) -> str:
    """Compile L1 24-hour operational phase-arc timeline."""
    phases = spec.get("phases", [])
    x0, y0, pw, bh = 54.0, 48.0, 612.0, 28.0
    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 132" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "24h Phase Timeline"))}">',
        f'<rect x="{x0}" y="{y0}" width="{pw}" height="{bh}" rx="4" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1"/>',
    ]
    for ph in phases:
        s_h, e_h = float(ph["start_h"]), float(ph["end_h"])
        px0, px1 = x0 + (s_h / 24.0) * pw, x0 + (e_h / 24.0) * pw
        col, bg = resolve_token(ph.get("color"), "var(--accent-focal)"), resolve_token(ph.get("bg"), "var(--tint-indigo-bg)")
        parts.append(f'<rect x="{px0:.1f}" y="{y0 + 1:.1f}" width="{max(4.0, px1 - px0):.1f}" height="{bh - 2:.1f}" fill="{bg}" stroke="{col}" stroke-width="1.2"/>')
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
        parts.append(pill_halo_text(ex, y0 - 15.0, str(ev["label"]), anchor="middle", size=11.5, weight="700", fill=ecol, border=ecol, x_bounds=(8.0, 712.0), math=False))
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
        parts.append(f'<rect x="{cx - bw / 2:.1f}" y="{y_hdr}" width="{bw:.1f}" height="{hdr_h}" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.3"/>')
        parts.append(halo_text(cx, y_hdr + 18.0, str(act["label"]), anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
        parts.append(f'<line x1="{cx:.1f}" y1="{y_hdr + hdr_h}" x2="{cx:.1f}" y2="{vb_h - 14}" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="3,3"/>')

    for idx, st in enumerate(steps):
        sy = y_start + idx * step_h
        x1, x2 = cx_map.get(st["from"], 80.0), cx_map.get(st["to"], 240.0)
        status = str(st.get("status", "neutral")).lower()
        stroke, mk = ("var(--accent-focal)", "qe-seq-focal") if status == "focal" else (("var(--status-ok)", "qe-seq-ok") if status == "ok" else ("var(--text-primary)", "qe-seq-arr"))
        dash = ' stroke-dasharray="5,3"' if st.get("style") == "dashed" else ""
        parts.append(f'<line x1="{x1:.1f}" y1="{sy:.1f}" x2="{x2:.1f}" y2="{sy:.1f}" stroke="{stroke}" stroke-width="1.6"{dash} marker-end="url(#{mk})"/>')
        parts.append(pill_halo_text((x1 + x2) / 2.0, sy - 10.0, str(st["label"]), anchor="middle", size=11.5, weight="600", fill=stroke, border="var(--border-hairline)", x_bounds=(8.0, 712.0), math=False))
    parts.append("</svg>")
    return "\n".join(parts)


def _analog_segments(samples: list[Any], t_min: float, t_span: float, x0: float, pw: float, ym: float, scale_div: float, lane_h: float, max_gap: float) -> tuple[list[str], list[tuple[float, float]]]:
    """Build piecewise linear path strings breaking cleanly across null/timeout dropouts."""
    t_span = t_span if (math.isfinite(t_span) and t_span > 0.0) else 1.0
    segs: list[str] = []
    gaps: list[tuple[float, float]] = []
    cur: list[str] = []
    prev_t: float | None = None
    drop_start: float | None = None
    px_per_unit = (lane_h / 4.0) / max(abs(scale_div), 1e-12)

    for s in samples:
        if not isinstance(s, (list, tuple)) or len(s) < 2:
            continue
        t, v = float(s[0]), s[1]
        if not math.isfinite(t) or v is None or not math.isfinite(float(v)):
            if cur:
                segs.append(" ".join(cur))
                cur = []
            if drop_start is None and math.isfinite(t):
                drop_start = prev_t if prev_t is not None else t
            if math.isfinite(t):
                prev_t = t
            continue
        if drop_start is not None:
            gaps.append((drop_start, t))
            drop_start = None
        elif prev_t is not None and (t - prev_t) > max_gap and cur:
            segs.append(" ".join(cur))
            cur = []
            gaps.append((prev_t, t))
        px = x0 + ((t - t_min) / t_span) * pw
        py = max(ym - lane_h / 2 + 4, min(ym + lane_h / 2 - 4, ym - float(v) * px_per_unit))
        cur.append(f'{"M" if not cur else "L"} {px:.1f} {py:.1f}')
        prev_t = t
    if cur:
        segs.append(" ".join(cur))
    return segs, gaps


def _digital_segments(samples: list[Any], t_min: float, t_span: float, x0: float, pw: float, y_top: float, lane_h: float) -> tuple[list[str], list[tuple[float, float]]]:
    """Build step-after orthogonal digital / Manchester II path segments breaking at None."""
    t_span = t_span if (math.isfinite(t_span) and t_span > 0.0) else 1.0
    segs: list[str] = []
    gaps: list[tuple[float, float]] = []
    cur: list[str] = []
    y_lo, y_mid, y_hi = y_top + lane_h - 10.0, y_top + lane_h / 2.0, y_top + 10.0
    prev_py: float | None = None
    prev_t: float | None = None
    drop_start: float | None = None

    for s in samples:
        if not isinstance(s, (list, tuple)) or len(s) < 2:
            continue
        t, v = float(s[0]), s[1]
        if not math.isfinite(t) or v is None or not math.isfinite(float(v)):
            if cur:
                segs.append(" ".join(cur))
                cur = []
            if drop_start is None and math.isfinite(t):
                drop_start = prev_t if prev_t is not None else t
            prev_py = None
            if math.isfinite(t):
                prev_t = t
            continue
        if drop_start is not None:
            gaps.append((drop_start, t))
            drop_start = None
        px = x0 + ((t - t_min) / t_span) * pw
        py = y_hi if float(v) > 0.2 else (y_lo if float(v) < -0.2 or float(v) == 0 else y_mid)
        if not cur:
            cur.append(f"M {px:.1f} {py:.1f}")
        else:
            cur.append(f"H {px:.1f} V {py:.1f}" if (prev_py is not None and py != prev_py) else f"H {px:.1f}")
        prev_py, prev_t = py, t
    if cur:
        segs.append(" ".join(cur))
    return segs, gaps


def _compile_scope(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile multi-channel time-synced HIL oscilloscope & Manchester II traces."""
    tb = spec.get("timebase", {})
    t_unit = str(tb.get("unit", "µs"))
    channels = spec.get("channels", [])
    vis_ch = channels[:1] if rigor == "L1" else channels

    t_span = float(tb.get("total_span_us", tb.get("total_span", 20.0)))
    t_min = float(tb.get("start_time", 0.0))
    if not math.isfinite(t_min):
        t_min = 0.0
    if not math.isfinite(t_span) or t_span <= 0.0:
        ts = [float(s[0]) for ch in vis_ch for s in ch.get("samples", []) if isinstance(s, (list, tuple)) and s and math.isfinite(float(s[0]))]
        t_min, t_span = (min(ts), max(ts) - min(ts)) if len(ts) >= 2 and max(ts) > min(ts) else (t_min, 1.0)
    t_max = t_min + t_span

    x0, y0, pw = 84.0, 28.0, 548.0
    lane_h, hdr_h, lane_gap = 94.0, 22.0, 14.0
    wave_h = lane_h - hdr_h
    tot_h = len(vis_ch) * lane_h + max(0, len(vis_ch) - 1) * lane_gap
    vb_h = int(y0 + tot_h + 44.0)
    t_sc = compute_linear_125_scale(t_min, t_max, target_ticks=6)
    nom_dt = float(tb.get("nominal_dt", t_span / 40.0))
    mult = float(spec.get("dropout_handling", {}).get("detection_multiplier", 1.5))
    max_gap = max(1e-12, (nom_dt if (math.isfinite(nom_dt) and nom_dt > 0) else t_span / 40.0) * (mult if (math.isfinite(mult) and mult > 0) else 1.5))

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" data-qe-scope="true" tabindex="0" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Multi-Channel Scope"))}">',
    ]
    for xm in t_sc["minors"]:
        if t_min <= xm <= t_max:
            px = x0 + ((xm - t_min) / t_span) * pw
            parts.append(f'<line x1="{px:.1f}" y1="{y0 + tot_h}" x2="{px:.1f}" y2="{y0 + tot_h + 4}" stroke="var(--border-strong)" stroke-width="0.8"/>')
    for xmaj in t_sc["majors"]:
        if t_min - 1e-9 <= xmaj <= t_max + 1e-9:
            px = x0 + ((xmaj - t_min) / t_span) * pw
            parts.append(halo_text(px, y0 + tot_h + 18.0, format_tick_numeral(xmaj, step=t_sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(halo_text(x0 + pw / 2.0, y0 + tot_h + 36.0, tb.get("quantity_calculus", f"t / {t_unit}"), anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))

    cursors = spec.get("cursors", {}) if rigor == "L3" else {}
    cursor_xs: list[tuple[float, str, str]] = []
    for ckey in ("cursor_a", "cursor_b"):
        cur = cursors.get(ckey)
        if cur:
            ct = float(cur.get("time_us", cur.get("time", 0.0)))
            cx = x0 + ((ct - t_min) / t_span) * pw
            ccol = resolve_token(cur.get("stroke_color"), "var(--accent-primary)")
            cursor_xs.append((cx, ccol, f'{cur.get("label", ckey)}: {ct:.2f}\u00a0{t_unit}'))

    scope_meta_channels: list[dict[str, Any]] = []
    minor_cls = "qe-grid-minor" if medium == "m1" else "qe-grid-minor qe-m1-only"
    for idx, ch in enumerate(vis_ch):
        ly = y0 + idx * (lane_h + lane_gap)
        wave_top = ly + hdr_h
        ym = wave_top + wave_h / 2.0
        col = resolve_token(ch.get("trace_color"), SERIES_STYLES[idx % len(SERIES_STYLES)]["stroke"])
        parts.append(f'<rect x="{x0}" y="{ly:.1f}" width="{pw}" height="{lane_h:.1f}" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1"/>')
        parts.append(f'<rect x="{x0 + 0.5:.1f}" y="{ly + 0.5:.1f}" width="{pw - 1:.1f}" height="{hdr_h - 0.5:.1f}" fill="var(--bg-elevated)"/>')
        parts.append(f'<line x1="{x0}" y1="{wave_top:.1f}" x2="{x0 + pw}" y2="{wave_top:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')
        for xm in t_sc["minors"]:
            if t_min <= xm <= t_max:
                px = x0 + ((xm - t_min) / t_span) * pw
                parts.append(f'<line class="{minor_cls}" x1="{px:.1f}" y1="{wave_top:.1f}" x2="{px:.1f}" y2="{ly + lane_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.5" stroke-dasharray="1,3"/>')
        for xmaj in t_sc["majors"]:
            if t_min - 1e-9 <= xmaj <= t_max + 1e-9:
                px = x0 + ((xmaj - t_min) / t_span) * pw
                parts.append(f'<line x1="{px:.1f}" y1="{wave_top:.1f}" x2="{px:.1f}" y2="{ly + lane_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')
        parts.append(f'<line x1="{x0}" y1="{ym:.1f}" x2="{x0 + pw}" y2="{ym:.1f}" stroke="var(--border-hairline)" stroke-width="0.8" stroke-dasharray="2,3"/>')
        parts.append(halo_text(x0 - 8.0, ly + 15.0, str(ch.get("id", f"CH{idx + 1}")).upper(), anchor="end", size=11.5, weight="700", fill=col, halo=False))

        ch_hdr = f'{ch.get("name", "")} ({ch.get("quantity_calculus", ch.get("unit", ""))})'
        parts.append(f'<text x="{x0 + 8.0:.1f}" y="{ly + 15.0:.1f}" text-anchor="start" font-family="var(--font-mono)" font-size="11.5" font-weight="600" fill="var(--text-primary)">{format_math_svg(ch_hdr, 8.8)}</text>')

        scale_div = float(ch.get("vertical_scale_per_div", 1.0))
        samples = ch.get("samples", [])
        if ch.get("type") == "digital":
            has_neg = any(isinstance(s, (list, tuple)) and len(s) >= 2 and s[1] is not None and float(s[1]) < 0 for s in samples)
            y_hi_lbl, y_lo_lbl = ("+1", "-1") if has_neg else ("1", "0")
            parts.append(f'<line x1="{x0 - 4}" y1="{wave_top + 10:.1f}" x2="{x0}" y2="{wave_top + 10:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
            parts.append(f'<line x1="{x0 - 4}" y1="{ly + lane_h - 10:.1f}" x2="{x0}" y2="{ly + lane_h - 10:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
            parts.append(halo_text(x0 - 7.0, wave_top + 14.0, y_hi_lbl, anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
            if has_neg:
                parts.append(halo_text(x0 - 7.0, ym + 4.0, "0 ▶", anchor="end", size=11.5, weight="700", fill="var(--text-muted)", halo=False))
            parts.append(halo_text(x0 - 7.0, ly + lane_h - 6.0, y_lo_lbl, anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
            segs, gaps = _digital_segments(samples, t_min, t_span, x0, pw, wave_top, wave_h)
        else:
            fs_val = 2.0 * abs(scale_div)
            parts.append(f'<line x1="{x0 - 4}" y1="{wave_top + 4:.1f}" x2="{x0}" y2="{wave_top + 4:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
            parts.append(f'<line x1="{x0 - 4}" y1="{ym:.1f}" x2="{x0}" y2="{ym:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
            parts.append(f'<line x1="{x0 - 4}" y1="{ly + lane_h - 4:.1f}" x2="{x0}" y2="{ly + lane_h - 4:.1f}" stroke="var(--border-strong)" stroke-width="1"/>')
            parts.append(halo_text(x0 - 7.0, wave_top + 13.0, f"+{fs_val:g}", anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
            parts.append(halo_text(x0 - 7.0, ym + 4.0, "0 ▶", anchor="end", size=11.5, weight="700", fill="var(--text-muted)", halo=False))
            parts.append(halo_text(x0 - 7.0, ly + lane_h - 3.0, f"-{fs_val:g}", anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
            segs, gaps = _analog_segments(samples, t_min, t_span, x0, pw, ym, scale_div, wave_h, max_gap)

        if rigor in {"L2", "L3"}:
            for env in ch.get("threshold_envelopes", []):
                ev_y = max(wave_top + 6.0, min(ly + lane_h - 6.0, ym - float(env["value"]) * ((wave_h / 4.0) / max(abs(scale_div), 1e-12))))
                ecol = resolve_token(env.get("color"), "var(--status-danger)")
                parts.append(f'<line x1="{x0}" y1="{ev_y:.1f}" x2="{x0 + pw + 5:.1f}" y2="{ev_y:.1f}" stroke="{ecol}" stroke-width="1.2" stroke-dasharray="4,3"/>')
                lbl_y = max(wave_top + 14.0, min(ly + lane_h - 4.0, ev_y + 4.0))
                parts.append(pill_halo_text(x0 + pw + 7.0, lbl_y, f'{env["value"]:+g}\u00a0{ch.get("unit", "")}', anchor="start", size=11.5, weight="700", fill=ecol, border=ecol, x_bounds=(x0 + pw + 5.0, 718.0), math=False))

        dropout_pills: list[str] = []
        for gt0, gt1 in gaps:
            gx0, gx1 = x0 + ((gt0 - t_min) / t_span) * pw, x0 + ((gt1 - t_min) / t_span) * pw
            parts.append(f'<rect x="{gx0:.1f}" y="{wave_top + 1:.1f}" width="{max(4.0, gx1 - gx0):.1f}" height="{wave_h - 2:.1f}" fill="var(--status-err-bg)" opacity="0.55"/>')
            if rigor in {"L2", "L3"} and (gx1 - gx0) >= 68.0:
                dropout_pills.append(pill_halo_text((gx0 + gx1) / 2.0, ym + 4.0, f"DROPOUT {gt1 - gt0:.1f}\u00a0{t_unit}", anchor="middle", size=11.5, weight="700", fill="var(--status-danger)", border="var(--status-danger)", x_bounds=(x0 + 4.0, x0 + pw - 4.0), math=False))
        for cx, ccol, _ in cursor_xs:
            parts.append(f'<line x1="{cx:.1f}" y1="{wave_top:.1f}" x2="{cx:.1f}" y2="{ly + lane_h:.1f}" stroke="{ccol}" stroke-width="1.4" stroke-dasharray="5,3"/>')
        if segs:
            parts.append(f'<path d="{" ".join(segs)}" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/>')
        parts.extend(dropout_pills)
        scope_meta_channels.append({"id": ch.get("id", f"ch{idx+1}"), "name": ch.get("name", ""), "unit": ch.get("unit", ""), "samples": samples})

    for cx, ccol, clbl in cursor_xs:
        parts.append(halo_text(cx, y0 - 8.0, clbl, anchor="middle", size=11.5, weight="700", fill=ccol, math=True))

    parts.append(f'<line class="qe-live-cursor" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + tot_h}" stroke="var(--accent-focal)" stroke-width="1.3" visibility="hidden"/>')
    parts.append("</svg>")

    delta_banner = ""
    if rigor == "L3" and cursors.get("cursor_a") and cursors.get("cursor_b"):
        ta = float(cursors["cursor_a"].get("time_us", cursors["cursor_a"].get("time", 0.0)))
        tb_v = float(cursors["cursor_b"].get("time_us", cursors["cursor_b"].get("time", 0.0)))
        dt = abs(tb_v - ta)
        delta_banner = f'T_A = {ta:.2f}\u00a0{t_unit}  |  T_B = {tb_v:.2f}\u00a0{t_unit}  |  Δt = {dt:.2f}\u00a0{t_unit}{_format_freq_reciprocal(dt, t_unit)}'

    meta_json = (
        json.dumps({"t_min": t_min, "t_span": t_span, "t_unit": t_unit, "max_gap": max_gap, "x0": x0, "pw": pw, "channels": scope_meta_channels}, separators=(",", ":"))
        .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )
    def_msg = esc(delta_banner) if delta_banner else "Hover, drag, or use Left/Right keys across channels to inspect timebase samples"
    readout = f'<div class="qe-scope-readout va-nums" data-default="{def_msg}" aria-live="polite">{def_msg}</div>'
    return f'<div class="va-figure-scroll qe-scope-scroll" tabindex="0" role="region" aria-label="{esc(spec.get("metadata", {}).get("title", "Scope"))}">{"".join(parts)}</div>{readout}<script type="application/json" class="qe-scope-data">{meta_json}</script>'


def compile_waveform(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white") -> str:
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
