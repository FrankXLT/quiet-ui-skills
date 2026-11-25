# SPDX-License-Identifier: Apache-2.0
"""Civic & public-data plot compilers: US 51-hex tile map and directional arrow dumbbell."""

from __future__ import annotations

import math
from typing import Any

from .svg_labels import halo_text
from .tokens_and_scales import compute_linear_125_scale, esc, finite_float, format_tick_numeral, resolve_token

# 50 states + DC in a 12-column x 8-row offset hex grid (even rows unshifted, odd rows +0.5 col).
US_HEX_GRID: tuple[tuple[str, str, int, int], ...] = (
    ("AK", "Alaska", 0, 0), ("ME", "Maine", 0, 11),
    ("WI", "Wisconsin", 1, 5), ("VT", "Vermont", 1, 9), ("NH", "New Hampshire", 1, 10),
    ("WA", "Washington", 2, 1), ("ID", "Idaho", 2, 2), ("MT", "Montana", 2, 3),
    ("ND", "North Dakota", 2, 4), ("MN", "Minnesota", 2, 5), ("IL", "Illinois", 2, 6),
    ("MI", "Michigan", 2, 7), ("NY", "New York", 2, 9), ("MA", "Massachusetts", 2, 10),
    ("OR", "Oregon", 3, 1), ("NV", "Nevada", 3, 2), ("WY", "Wyoming", 3, 3),
    ("SD", "South Dakota", 3, 4), ("IA", "Iowa", 3, 5), ("IN", "Indiana", 3, 6),
    ("OH", "Ohio", 3, 7), ("PA", "Pennsylvania", 3, 8), ("NJ", "New Jersey", 3, 9),
    ("CT", "Connecticut", 3, 10), ("RI", "Rhode Island", 3, 11),
    ("CA", "California", 4, 1), ("UT", "Utah", 4, 2), ("CO", "Colorado", 4, 3),
    ("NE", "Nebraska", 4, 4), ("MO", "Missouri", 4, 5), ("KY", "Kentucky", 4, 6),
    ("WV", "West Virginia", 4, 7), ("VA", "Virginia", 4, 8), ("MD", "Maryland", 4, 9),
    ("DE", "Delaware", 4, 10),
    ("AZ", "Arizona", 5, 2), ("NM", "New Mexico", 5, 3), ("KS", "Kansas", 5, 4),
    ("AR", "Arkansas", 5, 5), ("TN", "Tennessee", 5, 6), ("NC", "North Carolina", 5, 7),
    ("SC", "South Carolina", 5, 8), ("DC", "District of Columbia", 5, 9),
    ("OK", "Oklahoma", 6, 4), ("LA", "Louisiana", 6, 5), ("MS", "Mississippi", 6, 6),
    ("AL", "Alabama", 6, 7), ("GA", "Georgia", 6, 8),
    ("HI", "Hawaii", 7, 0), ("TX", "Texas", 7, 3), ("FL", "Florida", 7, 8),
)

_DEFAULT_HEX_BINS: tuple[str, ...] = ("#E2E8F0", "#BAE6FD", "#38BDF8", "#0369A1", "#1E3A8A")


def _hex_rel_luminance(hex_color: str) -> float:
    """Compute WCAG 2.1 relative luminance for #RGB or #RRGGBB fill hex colors."""
    s = str(hex_color or "").strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        return 0.5
    try:
        chans = [int(s[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    except ValueError:
        return 0.5
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _adaptive_ink(fill_hex: str) -> str:
    """Select maximum-contrast dark (#0F172A) or white (#FFFFFF) ink from fill luminance."""
    lum = _hex_rel_luminance(fill_hex)
    contrast_white = 1.05 / (lum + 0.05)
    contrast_dark = (lum + 0.05) / (0.0085 + 0.05)
    return "#FFFFFF" if contrast_white > contrast_dark else "#0F172A"


def _hex_polygon_points(cx: float, cy: float, r: float) -> str:
    """Build pointy-top hexagon vertex coordinates around (cx, cy)."""
    pts = []
    for k in range(6):
        ang = math.radians(60 * k - 30)
        pts.append(f"{cx + r * math.cos(ang):.1f},{cy + r * math.sin(ang):.1f}")
    return " ".join(pts)


def _fval(item: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    for k in keys:
        fv = finite_float(item.get(k))
        if fv is not None:
            return fv
    return default


def _compute_hex_bins(values: list[float], spec: dict[str, Any]) -> tuple[list[float], list[str], list[str]]:
    """Compute 5 stepped thresholds and palette colors (1-2-5 friendly breaks or explicit bins)."""
    raw_pal = list(spec.get("palette") or _DEFAULT_HEX_BINS)
    palette = [resolve_token(raw_pal[i], _DEFAULT_HEX_BINS[i % len(_DEFAULT_HEX_BINS)]) if i < len(raw_pal) else _DEFAULT_HEX_BINS[i % len(_DEFAULT_HEX_BINS)] for i in range(5)]
    raw_breaks = spec.get("bin_breaks")
    if isinstance(raw_breaks, (list, tuple)) and len(raw_breaks) >= 4:
        parsed = [finite_float(b) for b in raw_breaks[:4]]
        if all(b is not None for b in parsed):
            breaks = [float(b) for b in parsed]  # type: ignore[arg-type]
        else:
            raw_breaks = None
    if not (isinstance(raw_breaks, (list, tuple)) and len(raw_breaks) >= 4):
        lo, hi = (min(values), max(values)) if values else (0.0, 100.0)
        sc = compute_linear_125_scale(lo, hi, target_ticks=5)
        span = max(sc["max"] - sc["min"], 1e-6)
        breaks = [sc["min"] + span * (i / 5.0) for i in range(1, 5)]
    unit = str(spec.get("unit") or "%").strip()
    fmt = lambda v: f"{v:g}{unit}" if unit == "%" else f"{v:g} {unit}".strip()
    labels = [f"< {fmt(breaks[0])}"] + [f"{fmt(breaks[i])}–{fmt(breaks[i + 1])}" for i in range(3)] + [f"{fmt(breaks[3])}+"]
    return breaks, palette, labels


def _assign_bin(val: float | None, breaks: list[float]) -> int:
    if val is None or not math.isfinite(val):
        return -1
    for i, b in enumerate(breaks):
        if val < b:
            return i
    return 4


def compile_us_hex_tile_map(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile equal-area US 51-hex tile map with stepped 5-bin legend & luminance-adaptive ink."""
    raw_states = spec.get("states") or spec.get("items") or []
    state_map: dict[str, dict[str, Any]] = {}
    if isinstance(raw_states, dict):
        for k, v in raw_states.items():
            abbr = str(k).strip().upper()
            state_map[abbr] = v if isinstance(v, dict) else {"value": v}
    else:
        for item in raw_states:
            abbr = str(item.get("abbr") or item.get("state") or item.get("code") or "").strip().upper()
            if abbr:
                state_map[abbr] = item

    vals = [finite_float(d.get("value")) for d in state_map.values()]
    valid_vals = [v for v in vals if v is not None]
    breaks, palette, bin_labels = _compute_hex_bins(valid_vals, spec)
    unit = str(spec.get("unit") or "%").strip()
    decimals = 0 if spec.get("decimals") is None else int(spec["decimals"])
    raw_focus = spec.get("focus_state")
    focus_state = str(raw_focus).strip().upper() if raw_focus is not None else ""
    title = str(spec.get("metadata", {}).get("title") or "US 51-State Equal-Area Tile Map")

    r, dx, dy = 23.0, 42.4, 37.5
    x0, y0 = (640.0 - 11.5 * dx) / 2.0, 42.0

    legend_pills = [
        f'<span class="va-hex-bin-item"><span class="va-hex-swatch" style="--swatch:{esc(palette[i])}"></span>'
        f'<span>{esc(bin_labels[i])}</span></span>'
        for i in range(5)
    ]
    legend_html = f'<div class="qe-legend-series va-hex-legend" role="list" aria-label="Scale bins">{"".join(legend_pills)}</div>'

    svg_parts: list[str] = [f'<svg class="qe-svg qe-svg-640 va-hex-map-svg" viewBox="0 0 640 342" role="group" aria-label="{esc(title)}"><title>{esc(title)}</title>']
    focus_summary = str(spec.get("focus_summary") or "")
    selected_pts = ""
    for abbr, name, row, col in US_HEX_GRID:
        cx, cy = x0 + (col + (0.5 if row % 2 else 0.0)) * dx, y0 + row * dy
        entry = state_map.get(abbr) or {}
        val = finite_float(entry.get("value"))
        b_idx = _assign_bin(val, breaks)
        fill = palette[b_idx] if b_idx >= 0 else "#CBD5E1"
        ink = _adaptive_ink(fill)
        val_txt = f"{val:.{decimals}f}{unit}" if (val is not None and unit == "%") else (f"{val:.{decimals}f}" if val is not None else "n/a")
        val_full = f"{val_txt} {unit}".strip() if (val is not None and unit != "%") else val_txt
        note_txt = str(entry.get("note") or "")
        selected = bool(focus_state and abbr == focus_state)
        is_focus = " is-selected" if selected else ""
        pts = _hex_polygon_points(cx, cy, r - 1.4)
        if selected:
            selected_pts = pts
            if val is not None:
                focus_summary = f"{name} ({abbr}): {val_full}" + (f" · {note_txt}" if note_txt else "")
        tile_svg = (
            f'<g class="va-hex-tile{is_focus}" data-state="{esc(abbr)}" data-state-name="{esc(name)}" '
            f'data-value="{esc(val_txt)}" data-full-value="{esc(val_full)}" data-note="{esc(note_txt)}" '
            f'data-bin="{b_idx}" tabindex="0" role="button" aria-label="{esc(name)} ({esc(abbr)}): {esc(val_full)}">'
            f'<polygon points="{pts}" fill="{esc(fill)}" stroke="var(--bg-surface)" stroke-width="1.8"/>'
            f'<text x="{cx:.1f}" y="{cy - 3.0:.1f}" text-anchor="middle" font-family="var(--font-sans)" font-size="11.6" font-weight="700" fill="{esc(ink)}">{esc(abbr)}</text>'
            f'<text x="{cx:.1f}" y="{cy + 12.2:.1f}" text-anchor="middle" font-family="var(--font-mono)" font-size="11.4" font-weight="600" fill="{esc(ink)}">{esc(val_txt)}</text>'
            "</g>"
        )
        svg_parts.append(tile_svg)
    ring_hidden = "" if selected_pts else ' visibility="hidden"'
    svg_parts.append(f'<polygon class="va-hex-focus-ring" points="{selected_pts}" fill="none" stroke="var(--text-primary)" stroke-width="2.8" stroke-linejoin="round" pointer-events="none"{ring_hidden}/>')
    svg_parts.append("</svg>")
    if focus_summary and " · Select " in focus_summary:
        head, tail = focus_summary.split(" · Select ", 1)
        readout_inner = f'{esc(head)}<span class="va-hex-prompt">{esc(" · Select " + tail)}</span>'
    elif focus_summary:
        readout_inner = esc(focus_summary)
    else:
        readout_inner = '<span class="va-hex-prompt">Select any state hex tile to inspect exact rate and bin.</span>'
    readout = f'<div class="va-hex-readout" role="status" aria-live="polite">{readout_inner}</div>'
    return f'{legend_html}<div class="va-figure-scroll va-hex-stage">{"".join(svg_parts)}</div>{readout}'


def _arrow_head_points(x_tip: float, cy: float, direction: int) -> str:
    """Build crisp triangle arrowhead pointing right (+1) or left (-1)."""
    dx = 7.5 * direction
    return f"{x_tip:.1f},{cy:.1f} {x_tip - dx:.1f},{cy - 4.4:.1f} {x_tip - dx:.1f},{cy + 4.4:.1f}"


def _arrow_dumbbell_mobile_svg(
    items: list[dict[str, Any]],
    sc: dict[str, Any],
    title: str,
    x_lbl: str,
    fmt: Any,
    row_lbl_fn: Any,
) -> str:
    vb_w, x0, pw, y0, row_h = 340, 18.0, 304.0, 14.0, 46.0
    ph = max(72.0, len(items) * row_h)
    vh = int(y0 + ph + 48)
    span = max(sc["max"] - sc["min"], 1e-12)
    px = lambda v: x0 + max(0.0, min(1.0, (float(v) - sc["min"]) / span)) * pw
    parts = [f'<svg class="qe-svg qe-svg-340" viewBox="0 0 {vb_w} {vh}" role="img" aria-label="{esc(title)}">']
    grid_xs = [px(xv) for xv in sc["majors"] if x0 + 4 <= px(xv) <= x0 + pw - 4]
    prev_tx = -99.0
    for xv in sc["majors"]:
        xx = px(xv)
        if xx - prev_tx >= 42.0:
            anc = "start" if xx < 30.0 else ("end" if xx > vb_w - 30.0 else "middle")
            parts.append(halo_text(xx, y0 + ph + 16.0, format_tick_numeral(xv, step=sc["step"]), anchor=anc, size=10.8, fill="var(--text-secondary)", halo=False))
            prev_tx = xx
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 36.0, x_lbl, anchor="middle", size=11.0, weight="700", fill="var(--text-primary)", halo=False))
    for i, it in enumerate(items):
        top_y = y0 + i * row_h
        cy = top_y + 31.0
        for gxx in grid_xs:
            parts.append(f'<line x1="{gxx:.1f}" y1="{top_y + 21.0:.1f}" x2="{gxx:.1f}" y2="{top_y + 41.0:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')
        s_val = _fval(it, "start", "min")
        e_val = _fval(it, "end", "max")
        lbl, _ = row_lbl_fn(it, i)
        short_lbl = lbl if len(lbl) <= 27 else f"{lbl[:25].rstrip()}…"
        xs, xe = px(s_val), px(e_val)
        unchanged = abs(xe - xs) < 2.0
        col = "var(--accent-focal)" if unchanged else resolve_token(it.get("color"), "var(--accent-focal)" if e_val >= s_val else "var(--status-danger)")
        val_txt = f"{fmt(e_val)} (unchanged)" if unchanged else f"{fmt(s_val)} to {fmt(e_val)}"
        parts.append(halo_text(12.0, top_y + 14.0, short_lbl, anchor="start", size=11.2, weight="600", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        parts.append(halo_text(vb_w - 12.0, top_y + 14.0, val_txt, anchor="end", size=10.8, weight="700", fill=col if not unchanged else "var(--text-primary)", halo=False))
        parts.append(f'<line x1="{x0:.1f}" y1="{cy:.1f}" x2="{x0 + pw:.1f}" y2="{cy:.1f}" stroke="var(--border-hairline)" stroke-width="0.6" stroke-dasharray="2,3"/>')
        if unchanged:
            parts.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="4.2" fill="var(--bg-surface)" stroke="var(--accent-focal)" stroke-width="1.8"/>')
            parts.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="1.8" fill="var(--accent-focal)"/>')
        else:
            direction = 1 if xe >= xs else -1
            shaft_end = xe - direction * 5.8 if abs(xe - xs) > 8.0 else xs
            parts.append(f'<line x1="{xs:.1f}" y1="{cy:.1f}" x2="{shaft_end:.1f}" y2="{cy:.1f}" stroke="{esc(col)}" stroke-width="2.2"/>')
            parts.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="3.6" fill="var(--bg-surface)" stroke="var(--text-secondary)" stroke-width="1.6"/>')
            parts.append(f'<polygon points="{_arrow_head_points(xe, cy, direction)}" fill="{esc(col)}"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def _arrow_dumbbell_legend(start_lbl: str, end_lbl: str) -> str:
    return (
        '<div class="qe-legend-series va-arrow-legend">'
        f'<span><span class="va-dot-swatch" style="--swatch:var(--text-secondary)"></span>{esc(start_lbl)}</span>'
        '<span><svg class="va-arrow-swatch is-gain" width="18" height="10" viewBox="0 0 18 10" aria-hidden="true">'
        '<line x1="1" y1="5" x2="11.5" y2="5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'
        f'<polygon points="17,5 10.5,1.2 10.5,8.8" fill="currentColor"/></svg>{esc(end_lbl)} gain</span>'
        '<span><svg class="va-arrow-swatch is-drop" width="18" height="10" viewBox="0 0 18 10" aria-hidden="true">'
        '<line x1="6.5" y1="5" x2="17" y2="5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'
        f'<polygon points="1,5 7.5,1.2 7.5,8.8" fill="currentColor"/></svg>{esc(end_lbl)} decline</span>'
        "</div>"
    )


def compile_arrow_dumbbell(spec: dict[str, Any], rigor: str, medium: str, chrome: str = "bench") -> str:
    """Compile ranked directional arrow dumbbell comparing start -> end values with fallback vintage notes."""
    items = list(spec.get("items") or spec.get("series_items") or [])
    sort_mode = str(spec.get("sort") or "as_is").lower()
    if sort_mode == "delta_desc":
        items.sort(key=lambda it: _fval(it, "end", "max") - _fval(it, "start", "min"), reverse=True)
    elif sort_mode == "end_desc":
        items.sort(key=lambda it: _fval(it, "end", "max"), reverse=True)

    unit = str(spec.get("unit") or "").strip()
    decimals = 1 if spec.get("decimals") is None else int(spec["decimals"])
    start_lbl = str(spec.get("start_label") or "Baseline")
    end_lbl = str(spec.get("end_label") or "Current")
    vals = [_fval(it, k0, k1) for it in items for k0, k1 in (("start", "min"), ("end", "max"))]
    lo_raw, hi_raw = (min(vals), max(vals)) if vals else (0.0, 100.0)
    span_raw = max(hi_raw - lo_raw, 1.0)
    sc = compute_linear_125_scale(lo_raw - span_raw * 0.14, hi_raw + span_raw * 0.14, target_ticks=5)
    fmt = lambda v: f"{v:.{decimals}f}{unit}" if unit == "%" else (f"{v:.{decimals}f}" if decimals else f"{v:g}")

    def _row_lbl(it: dict[str, Any], idx: int) -> tuple[str, str]:
        raw_lbl = str(it.get("label") or f"Row {idx + 1}").rstrip()
        fb = str(it.get("fallback_vintage") or "").strip()
        lbl = raw_lbl if (not fb or raw_lbl.endswith("*")) else f"{raw_lbl} *"
        return lbl, fb

    max_l_px = max((len(_row_lbl(it, i)[0]) * 7.2 for i, it in enumerate(items)), default=110.0)
    max_r_px = max(
        (
            len(fmt(max(_fval(it, "start", "min"), _fval(it, "end", "max"))) + (" (unchanged)" if abs(_fval(it, "end", "max") - _fval(it, "start", "min")) <= 1e-6 else "")) * 7.0
            for it in items
        ),
        default=48.0,
    )
    wide_bench = chrome in {"bench", "editorial"}
    vb_w = 880 if wide_bench else 640
    svg_cls = "qe-svg qe-svg-880" if wide_bench else "qe-svg qe-svg-640"
    x0 = min(220.0, max(150.0 if wide_bench else 142.0, max_l_px + 22.0))
    pw = max(440.0 if wide_bench else 270.0, (vb_w - 14.0) - x0 - max_r_px - 20.0)
    y0, row_h = 32.0, 34.0
    ph = max(72.0, len(items) * row_h)
    vh = int(y0 + ph + 54)
    span = max(sc["max"] - sc["min"], 1e-12)
    px = lambda v: x0 + max(0.0, min(1.0, (float(v) - sc["min"]) / span)) * pw

    legend_html = _arrow_dumbbell_legend(start_lbl, end_lbl)
    title = str(spec.get("metadata", {}).get("title") or "Directional Arrow Dumbbell")
    parts: list[str] = [f'<svg class="{svg_cls}" viewBox="0 0 {vb_w} {vh}" role="img" aria-label="{esc(title)}">']
    for xv in sc["majors"]:
        xx = px(xv)
        if xx < x0 + 6 or xx > x0 + pw - 6:
            continue
        parts.append(f'<line x1="{xx:.1f}" y1="{y0 - 4:.1f}" x2="{xx:.1f}" y2="{y0 + ph:.1f}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
        parts.append(halo_text(xx, y0 + ph + 18.0, format_tick_numeral(xv, step=sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))

    x_lbl = f"{spec.get('x_label') or 'Value'}" + (f" ({unit})" if unit and unit != "%" else (" (%)" if unit == "%" else ""))
    parts.append(halo_text(x0 + pw / 2.0, y0 + ph + 40.0, x_lbl, anchor="middle", size=11.8, weight="700", fill="var(--text-primary)", halo=False))

    fallback_notes: list[str] = []
    for i, it in enumerate(items):
        cy = y0 + (i + 0.5) * row_h
        s_val, e_val = _fval(it, "start", "min"), _fval(it, "end", "max")
        lbl, fb = _row_lbl(it, i)
        if fb:
            fallback_notes.append(f"{lbl.rstrip(' *')}: {fb}")
        xs, xe = px(s_val), px(e_val)
        parts.append(f'<line x1="{x0:.1f}" y1="{cy:.1f}" x2="{x0 + pw:.1f}" y2="{cy:.1f}" stroke="var(--border-hairline)" stroke-width="0.6" stroke-dasharray="2,3"/>')
        parts.append(halo_text(x0 - 10.0, cy + 4.0, lbl, anchor="end", size=12.0, weight="600", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        if abs(xe - xs) < 2.0:
            parts.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="4.6" fill="var(--bg-surface)" stroke="var(--accent-focal)" stroke-width="2.0"/>')
            parts.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="2.0" fill="var(--accent-focal)"/>')
            parts.append(halo_text(xs + 12.5, cy + 4.0, f"{fmt(e_val)} (unchanged)", anchor="start", size=11.5, weight="600", fill="var(--text-primary)", halo=True))
        else:
            col = resolve_token(it.get("color"), "var(--accent-focal)" if e_val >= s_val else "var(--status-danger)")
            direction = 1 if xe >= xs else -1
            shaft_end = xe - direction * 6.5 if abs(xe - xs) > 9.0 else xs
            parts.append(f'<line x1="{xs:.1f}" y1="{cy:.1f}" x2="{shaft_end:.1f}" y2="{cy:.1f}" stroke="{esc(col)}" stroke-width="2.4"/>')
            parts.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="4.0" fill="var(--bg-surface)" stroke="var(--text-secondary)" stroke-width="1.8"/>')
            parts.append(f'<polygon points="{_arrow_head_points(xe, cy, direction)}" fill="{esc(col)}"/>')
            left_is_end = xe < xs
            lx, rx = (xe, xs) if left_is_end else (xs, xe)
            l_txt, r_txt = (fmt(e_val), fmt(s_val)) if left_is_end else (fmt(s_val), fmt(e_val))
            l_col, r_col = (col, "var(--text-secondary)") if left_is_end else ("var(--text-secondary)", col)
            parts.append(halo_text(lx - 12.0, cy + 4.0, l_txt, anchor="end", size=11.5, weight="600", fill=l_col, halo=True))
            parts.append(halo_text(rx + 12.0, cy + 4.0, r_txt, anchor="start", size=11.5, weight="700" if not left_is_end else "600", fill=r_col, halo=True))

    parts.append("</svg>")
    if wide_bench:
        parts.append(_arrow_dumbbell_mobile_svg(items, sc, title, x_lbl, fmt, _row_lbl))
    fb_html = f'<p class="va-fallback-note">* Prior-year fallback series: {esc("; ".join(fallback_notes))}.</p>' if fallback_notes else ""
    return f'{legend_html}<div class="va-figure-scroll">{chr(10).join(parts)}</div>{fb_html}'
