#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.3 — Specimen 43: Cyclical Hourly Min-Avg-Max + Last 24h Whisker Plot."""

from __future__ import annotations

import json
from html import escape as _esc

from bench_data_contracts import contract_for_ui_specimen

HOURLY_BUCKETS: tuple[dict[str, object], ...] = (
    {"label": "00h", "min": 2, "avg": 5.2, "max": 11, "recent": 4, "activeDays": 14},
    {"label": "01h", "min": 1, "avg": 3.4, "max": 8, "recent": 3, "activeDays": 14},
    {"label": "02h", "min": 0, "avg": 2.1, "max": 6, "recent": 1, "activeDays": 14},
    {"label": "03h", "min": 0, "avg": 1.8, "max": 5, "recent": 2, "activeDays": 14},
    {"label": "04h", "min": 1, "avg": 2.4, "max": 7, "recent": 2, "activeDays": 14},
    {"label": "05h", "min": 1, "avg": 3.9, "max": 9, "recent": 5, "activeDays": 14},
    {"label": "06h", "min": 3, "avg": 6.8, "max": 13, "recent": 8, "activeDays": 14},
    {"label": "07h", "min": 5, "avg": 11.4, "max": 19, "recent": 12, "activeDays": 14},
    {"label": "08h", "min": 8, "avg": 16.2, "max": 26, "recent": 18, "activeDays": 14},
    {"label": "09h", "min": 10, "avg": 20.8, "max": 31, "recent": 24, "activeDays": 14},
    {"label": "10h", "min": 12, "avg": 23.5, "max": 35, "recent": 27, "activeDays": 14},
    {"label": "11h", "min": 11, "avg": 22.1, "max": 34, "recent": 21, "activeDays": 14},
    {"label": "12h", "min": 9, "avg": 18.7, "max": 29, "recent": 17, "activeDays": 14},
    {"label": "13h", "min": 11, "avg": 21.6, "max": 33, "recent": 25, "activeDays": 14},
    {"label": "14h", "min": 13, "avg": 24.4, "max": 37, "recent": 29, "activeDays": 14},
    {"label": "15h", "min": 12, "avg": 22.9, "max": 35, "recent": 22, "activeDays": 14},
    {"label": "16h", "min": 10, "avg": 19.6, "max": 31, "recent": 20, "activeDays": 14},
    {"label": "17h", "min": 8, "avg": 16.8, "max": 27, "recent": 15, "activeDays": 14},
    {"label": "18h", "min": 6, "avg": 13.5, "max": 23, "recent": 14, "activeDays": 14},
    {"label": "19h", "min": 5, "avg": 11.9, "max": 21, "recent": 13, "activeDays": 14},
    {"label": "20h", "min": 4, "avg": 10.6, "max": 19, "recent": 9, "activeDays": 14},
    {"label": "21h", "min": 4, "avg": 9.4, "max": 17, "recent": 11, "activeDays": 14},
    {"label": "22h", "min": 3, "avg": 7.8, "max": 15, "recent": 8, "activeDays": 14},
    {"label": "23h", "min": 2, "avg": 6.1, "max": 13, "recent": 5, "activeDays": 14},
)


def _render_fallback_svg() -> str:
    w, h = 680.0, 240.0
    x0, y0, pw, ph = 54.0, 28.0, 606.0, 174.0
    y_max = 40.0
    parts: list[str] = [
        f'<svg class="qe-svg-fallback qe-svg-680" viewBox="0 0 {int(w)} {int(h)}" role="img" '
        'aria-label="Activity by Hour of Day Min Avg Max Whiskers" preserveAspectRatio="xMidYMid meet">',
        '<title>Activity by Hour of Day — Min/Avg/Max Whiskers</title>',
        '<text x="54" y="18" font-family="var(--font-sans)" font-size="11" font-weight="600" '
        'fill="var(--text-secondary)">Activity / (calls/day)</text>',
    ]
    for tick in (0, 10, 20, 30, 40):
        yy = y0 + ph - (tick / y_max) * ph
        parts.append(
            f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x0 + pw:.1f}" y2="{yy:.1f}" '
            'stroke="var(--border-hairline)" stroke-dasharray="3 3" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x0 - 8:.1f}" y="{yy + 4:.1f}" text-anchor="end" font-family="var(--font-mono)" '
            f'font-size="11" fill="var(--text-secondary)">{tick}</text>'
        )
    parts.append(
        f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0:.1f}" y2="{y0 + ph:.1f}" stroke="var(--text-secondary)" stroke-width="1"/>'
    )
    parts.append(
        f'<line x1="{x0:.1f}" y1="{y0 + ph:.1f}" x2="{x0 + pw:.1f}" y2="{y0 + ph:.1f}" stroke="var(--text-secondary)" stroke-width="1"/>'
    )
    n = len(HOURLY_BUCKETS)
    dx = pw / max(1, n)
    for i, b in enumerate(HOURLY_BUCKETS):
        cx = x0 + (i + 0.5) * dx
        y_lo = y0 + ph - (float(b["min"]) / y_max) * ph
        y_hi = y0 + ph - (float(b["max"]) / y_max) * ph
        y_av = y0 + ph - (float(b["avg"]) / y_max) * ph
        y_rc = y0 + ph - (float(b["recent"]) / y_max) * ph
        parts.append(
            f'<line x1="{cx:.1f}" y1="{y_lo:.1f}" x2="{cx:.1f}" y2="{y_hi:.1f}" '
            'stroke="var(--text-secondary)" stroke-opacity="0.72" stroke-width="1.5"/>'
        )
        parts.append(
            f'<line x1="{cx - 3.5:.1f}" y1="{y_hi:.1f}" x2="{cx + 3.5:.1f}" y2="{y_hi:.1f}" '
            'stroke="var(--text-secondary)" stroke-opacity="0.72" stroke-width="1.5"/>'
        )
        parts.append(
            f'<line x1="{cx - 3.5:.1f}" y1="{y_lo:.1f}" x2="{cx + 3.5:.1f}" y2="{y_lo:.1f}" '
            'stroke="var(--text-secondary)" stroke-opacity="0.72" stroke-width="1.5"/>'
        )
        parts.append(
            f'<line x1="{cx - 7:.1f}" y1="{y_av:.1f}" x2="{cx + 7:.1f}" y2="{y_av:.1f}" '
            'stroke="var(--text-primary)" stroke-width="2.4"/>'
        )
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{y_rc:.1f}" r="3.6" fill="var(--accent-focal)" '
            'stroke="var(--bg-surface)" stroke-width="1.4"/>'
        )
        if i in (0, 4, 8, 12, 16, 20, 23):
            parts.append(
                f'<text x="{cx:.1f}" y="{y0 + ph + 18:.1f}" text-anchor="middle" font-family="var(--font-mono)" '
                f'font-size="11" fill="var(--text-secondary)">{_esc(str(b["label"]))}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def compile_cyclical_whisker_specimen() -> str:
    """Compile Specimen 43 (#qe-cyclical-whiskers) with Quiet SVG + Live ECharts parity."""
    payload = json.dumps(
        {
            "kind": "cyclical_whisker",
            "buckets": list(HOURLY_BUCKETS),
            "opts": {"unit": "calls/day", "recentLabel": "Last 24h", "rangeLabel": "Min–Max", "avgLabel": "Active Avg"},
        },
        separators=(",", ":"),
        allow_nan=False,
    )
    svg_fb = _render_fallback_svg()
    contract_html = contract_for_ui_specimen("qe-cyclical-whiskers")
    legend_html = (
        '<div class="qe-legend-series" aria-label="Series legend">'
        '<span class="qe-leg-item"><svg class="qe-leg-svg" width="14" height="12" viewBox="0 0 14 12" aria-hidden="true">'
        '<line x1="7" y1="1" x2="7" y2="11" stroke="var(--text-secondary)" stroke-width="1.5"/>'
        '<line x1="4" y1="1" x2="10" y2="1" stroke="var(--text-secondary)" stroke-width="1.5"/>'
        '<line x1="4" y1="11" x2="10" y2="11" stroke="var(--text-secondary)" stroke-width="1.5"/></svg>'
        '<span class="qe-leg-txt">Min–Max</span></span>'
        '<span class="qe-leg-item"><svg class="qe-leg-svg" width="14" height="12" viewBox="0 0 14 12" aria-hidden="true">'
        '<line x1="2" y1="6" x2="12" y2="6" stroke="var(--text-primary)" stroke-width="2.4"/></svg>'
        '<span class="qe-leg-txt">Active Avg</span></span>'
        '<span class="qe-leg-item"><svg class="qe-leg-svg" width="14" height="12" viewBox="0 0 14 12" aria-hidden="true">'
        '<circle cx="7" cy="6" r="3.5" fill="var(--accent-focal)"/></svg>'
        '<span class="qe-leg-txt">Last 24h</span></span>'
        '</div>'
    )
    modebar = (
        '<div class="qe-plot-modebar" role="group" aria-label="Plot rendering backend">'
        '<span class="qe-modebar-label">Renderer</span>'
        '<button type="button" class="qe-mode-btn" data-qe-mode="svg" aria-pressed="false">Quiet SVG</button>'
        '<button type="button" class="qe-mode-btn is-active" data-qe-mode="echarts" aria-pressed="true">Live ECharts</button></div>'
    )
    return (
        '<article class="qe-specimen qe-specimen-wide" data-modality="M4" '
        'data-schema-modality="cyclical_whisker" data-rigor="L2">'
        '<figure class="va-card qe-bench-card qe-figure" id="qe-cyclical-whiskers">'
        '<div class="qe-fig-hdr">'
        '<div>'
        '<div class="qe-fig-kicker">PILLAR 2 · M4 CYCLICAL WHISKERS</div>'
        '<h2 class="qe-fig-title">Activity by Hour of Day — Min/Avg/Max Whiskers</h2>'
        '</div>'
        '<div class="qe-fig-badges"><span class="va-pill" data-variant="tag">M4 · L2</span></div>'
        '</div>'
        '<p class="qe-fig-desc">Active-day per-slot Min–Max range stems, Active Avg crossbars, and Last 24h markers '
        'across 00h–23h (replaces raw multi-day sums whose bars scale artificially with window length).</p>'
        f'<div class="qe-plot-wrap" data-echarts-mode="echarts" data-quiet-echarts="{_esc(payload, quote=True)}">'
        f'{modebar}{legend_html}'
        '<div class="va-figure-scroll">'
        '<div class="qe-echarts-host"></div>'
        f'{svg_fb}'
        '</div></div>'
        f'{contract_html}'
        '</figure></article>'
    )
