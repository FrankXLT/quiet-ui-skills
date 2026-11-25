"""Quiet UI v9.7.0 Wave 2 view builders: Subsea Corridor (v25) and Trade-Space Calculator (v26)."""
from __future__ import annotations

import html

_V25_STATIONS: tuple[tuple[str, int, int, int, float, float, str, str], ...] = (
    ("CLS-Alpha Shore Landing", 0, 0, 1120, 0.4, 26.0, "NOMINAL", "shelf"),
    ("Span S1 / Repeater R1", 68, -110, 420, 13.6, 24.2, "NOMINAL", "shelf"),
    ("Span S2 / Repeater R2", 140, -180, 430, 14.1, 22.9, "NOMINAL", "shelf"),
    ("Span S3 / Repeater R3", 210, -420, 425, 13.8, 21.8, "NOMINAL", "shelf"),
    ("Branching Unit BU-03", 240, -760, 390, 6.1, 20.9, "NOMINAL", "branch"),
    ("Span S4 / Repeater R4", 302, -1180, 435, 14.4, 20.1, "NOMINAL", "branch"),
    ("Span S5 (+4.8 dB) / R5", 362, -1420, 510, 19.2, 16.4, "WARN", "fault"),
    ("Span S6 / Repeater R6", 440, -2940, 440, 14.2, 17.3, "NOMINAL", "deep"),
    ("Span S7 / Repeater R7", 515, -3680, 438, 14.0, 17.8, "NOMINAL", "deep"),
    ("Span S8 / R8 -> CLS-Bravo", 640, 0, 432, 13.9, 18.2, "NOMINAL", "deep"),
)

_V25_PROFILE_XY: tuple[tuple[int, int], ...] = (
    (0, 0), (68, -110), (140, -180), (210, -420), (240, -760),
    (302, -1180), (362, -1420), (440, -2940), (515, -3680), (585, -3850), (618, -1250), (640, 0),
)


def _km_to_x(km: float) -> float:
    return 76.0 + (km / 640.0) * 740.0


def _depth_to_y(depth_m: float) -> float:
    return 36.0 + (abs(depth_m) / 4000.0) * 144.0


def _osnr_to_y(osnr_db: float) -> float:
    clamped = max(12.0, min(28.0, osnr_db))
    return 184.0 - ((clamped - 12.0) / 16.0) * 150.0


def build_v25_bathymetry_svg() -> str:
    """Render 2D linear shore-to-shore seabed profile & repeater corridor (0-640 km)."""
    pts = [(_km_to_x(km), _depth_to_y(d)) for km, d in _V25_PROFILE_XY]
    cable_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    sea_d = cable_d + f" L {_km_to_x(640):.1f} 36.0 L {_km_to_x(0):.1f} 36.0 Z"
    grid = "".join(
        f'<line x1="76" y1="{_depth_to_y(-d):.1f}" x2="816" y2="{_depth_to_y(-d):.1f}" stroke="var(--border-subtle)" stroke-dasharray="2 3"/>'
        f'<text x="68" y="{_depth_to_y(-d) + 4:.1f}" text-anchor="end" font-size="11.5" fill="var(--text-muted)">{"0 m" if d == 0 else f"-{d} m"}</text>'
        for d in (0, 1000, 2000, 3000, 4000)
    )
    nodes = []
    for name, km, depth, _pump, _loss, _osnr, status, grp in _V25_STATIONS:
        cx, cy = _km_to_x(km), _depth_to_y(depth)
        pos_map = {
            640: ("CLS-Bravo", "middle", 0.0, 24.0),
            0: ("CLS-Alpha", "middle", 0.0, 24.0),
            68: ("Repeater R1", "middle", 0.0, 24.0),
            140: ("Repeater R2", "middle", 0.0, 24.0),
            210: ("Repeater R3", "end", -8.0, 65.0),
            240: ("BU-03", "start", 8.0, 57.0),
            302: ("Repeater R4", "end", -8.0, 95.0),
            362: ("R5", "end", -8.0, 102.0),
            440: ("Repeater R6", "start", 8.0, 134.0),
            515: ("Repeater R7", "start", 8.0, 162.0),
        }
        lbl, anchor, dx, ty = pos_map[km]
        color = "var(--status-warn)" if status == "WARN" else ("var(--accent-focal)" if "BU-03" in name else "var(--text-primary)")
        r = 6.5 if status == "WARN" or "BU-03" in name else 4.5
        nodes.append(
            f'<g class="w2-span-node" data-span-group="{grp}">'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}" stroke="var(--bg-surface)" stroke-width="1.8"/>'
            f'<text x="{cx + dx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" font-size="11.5" font-weight="600" fill="{color}">{lbl}</text>'
            '</g>'
        )
    x_fault = _km_to_x(362)
    callout = (
        f'<line x1="{x_fault:.1f}" y1="28" x2="{x_fault:.1f}" y2="196" stroke="var(--status-warn)" stroke-dasharray="4 3" stroke-width="1.5"/>'
        f'<rect x="{x_fault + 8:.1f}" y="46.0" width="222" height="20" rx="3" fill="var(--bg-surface)" stroke="var(--status-warn)"/>'
        f'<text x="{x_fault + 14:.1f}" y="60.0" font-size="11.5" font-weight="650" fill="var(--status-warn)">Span S5 Fault (+4.8 dB · 362 km)</text>'
    )
    return (
        '<svg viewBox="0 0 880 206" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="Subsea corridor bathymetry profile from CLS-Alpha 0 km to CLS-Bravo 640 km with fault Span S5 at 362 km">'
        f'<path d="{sea_d}" fill="var(--accent-focal)" opacity="0.08"/>'
        f'{grid}'
        f'<path d="{cable_d}" fill="none" stroke="var(--text-primary)" stroke-width="2.2"/>'
        f'{callout}{"".join(nodes)}</svg>'
    )


def build_v25_osnr_svg() -> str:
    """Render distance-aligned OSNR link-margin profile (0-640 km) locked to corridor X axis."""
    pts = [(_km_to_x(row[1]), _osnr_to_y(row[5]), row[6], row[7], row[5], row[1]) for row in _V25_STATIONS]
    line_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y, *_ in pts)
    y_fec = _osnr_to_y(15.0)
    grid_y = "".join(
        f'<line x1="76" y1="{_osnr_to_y(db):.1f}" x2="816" y2="{_osnr_to_y(db):.1f}" stroke="var(--border-subtle)" stroke-dasharray="2 3"/>'
        f'<text x="68" y="{_osnr_to_y(db) + 4:.1f}" text-anchor="end" font-size="11.5" fill="var(--text-muted)">{db} dB</text>'
        for db in (12, 16, 20, 24, 28)
    )
    grid_x = "".join(
        f'<text x="{_km_to_x(km):.1f}" y="204" text-anchor="middle" font-size="11.5" fill="var(--text-muted)">{km} km</text>'
        for km in (0, 160, 240, 362, 480, 640)
    )
    markers = []
    for x, y, status, grp, osnr, km in pts:
        fill = "var(--status-warn)" if status == "WARN" else "var(--accent-focal)"
        markers.append(
            f'<g class="w2-span-mark" data-span-group="{grp}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6.0 if status == "WARN" else 4.2}" fill="{fill}" stroke="var(--bg-surface)" stroke-width="1.6"/>'
            '</g>'
        )
    x_f = _km_to_x(362)
    return (
        '<svg viewBox="0 0 880 214" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="Distance-aligned OSNR link-margin profile across 0 to 640 km above 15.0 dB SD-FEC floor">'
        f'{grid_y}{grid_x}'
        f'<line x1="{_km_to_x(240):.1f}" y1="24" x2="{_km_to_x(240):.1f}" y2="184" stroke="var(--border-strong)" stroke-dasharray="2 4"/>'
        f'<line x1="{x_f:.1f}" y1="18" x2="{x_f:.1f}" y2="184" stroke="var(--status-warn)" stroke-dasharray="4 3" stroke-width="1.5"/>'
        f'<line x1="76" y1="{y_fec:.1f}" x2="816" y2="{y_fec:.1f}" stroke="var(--status-danger)" stroke-dasharray="6 4" stroke-width="1.6"/>'
        f'<rect x="642" y="{y_fec - 18:.1f}" width="166" height="16" rx="2" fill="var(--bg-surface)" opacity="0.94"/>'
        f'<text x="804" y="{y_fec - 6:.1f}" text-anchor="end" font-size="11.5" font-weight="650" fill="var(--status-danger)">SD-FEC Floor (15.0 dB)</text>'
        f'<path d="{line_d}" fill="none" stroke="var(--accent-focal)" stroke-width="2.3"/>'
        f'{"".join(markers)}'
        f'<rect x="{x_f + 8:.1f}" y="42.0" width="198" height="20" rx="3" fill="var(--bg-surface)" stroke="var(--status-warn)"/>'
        f'<text x="{x_f + 14:.1f}" y="56.0" font-size="11.5" font-weight="650" fill="var(--status-warn)">Min OSNR 16.4 dB (+1.4 dB)</text>'
        '</svg>'
    )


def build_v25_html() -> str:
    """Build View v25 Subsea Optical Cable & Bathymetric Repeater Corridor workbench."""
    kpis = (
        ("Trunk Span", "640 km · 8 Repeaters", "CLS-Alpha (0 km) to CLS-Bravo (640 km) · BU-03 @ 240 km", "nominal"),
        ("Worst-Span Excess Loss", "+4.8 dB on Span S5", "19.2 dB total vs 14.4 dB baseline @ 362 km shelf break", "warn"),
        ("Minimum OSNR Margin", "16.4 dB vs 15.0 dB FEC", "+1.4 dB net margin above SD-FEC limit", "warn"),
        ("Wet-Plant Line Feed", "1.12 A Constant Current", "Zero ground shunt fault detected across repeaters", "nominal"),
    )
    kpi_html = "".join(
        f'<div class="w2-kpi-tile" data-state="{st}"><span class="w2-kpi-lbl">{lbl}</span>'
        f'<span class="w2-kpi-val">{val}</span><span class="w2-kpi-sub">{sub}</span></div>'
        for lbl, val, sub, st in kpis
    )
    rows_html = "".join(
        f'<tr class="w2-span-row" data-span-group="{grp}">'
        f'<td>{html.escape(name)}</td><td class="w2-num">{km} km</td><td class="w2-num">{depth} m</td>'
        f'<td class="w2-num">{pump} mA</td><td class="w2-num">{loss:.1f} dB</td><td class="w2-num">{osnr:.1f} dB</td>'
        f'<td><span class="va-pill" data-variant="tag" data-state="{"warn" if st == "WARN" else "nominal"}">{st}</span></td></tr>'
        for name, km, depth, pump, loss, osnr, st, grp in _V25_STATIONS
    )
    return (
        '<div class="w2-stack" data-v25-scope="studio">'
        f'<div class="w2-kpi-grid">{kpi_html}</div>'
        '<section class="w2-card" aria-labelledby="v25-corr-title">'
        '<div class="w2-card-hdr"><div>'
        '<h2 id="v25-corr-title" class="w2-card-title">Subsea Bathymetry Corridor &amp; Distance-Aligned OSNR Profile</h2>'
        '<p class="w2-card-sub">Synchronized 0–640 km wet-plant geometry locking seabed depth, Branch BU-03, and Span S5 OSNR margin.</p>'
        '</div><span class="va-pill" data-variant="status" data-state="warn" data-v25-pill>SPAN S5 ALERT (+4.8 dB)</span></div>'
        '<div class="w2-toolbar" role="region" aria-label="Corridor span highlight filters">'
        '<div class="w2-btn-group">'
        '<button type="button" class="w2-filter-btn" data-v25-span="all" aria-pressed="true">All Spans (10)</button>'
        '<button type="button" class="w2-filter-btn" data-v25-span="shelf" aria-pressed="false">Shelf R1–R3</button>'
        '<button type="button" class="w2-filter-btn" data-v25-span="branch" aria-pressed="false">Branch BU-03</button>'
        '<button type="button" class="w2-filter-btn" data-v25-span="fault" aria-pressed="false">Fault Span S5</button>'
        '<button type="button" class="w2-filter-btn" data-v25-span="deep" aria-pressed="false">Deep R6–R8</button>'
        '</div></div>'
        f'<div class="w2-svg-box">{build_v25_bathymetry_svg()}</div>'
        f'<div class="w2-svg-box">{build_v25_osnr_svg()}</div>'
        '<div class="w2-legend-row" aria-label="Subsea corridor chart legend">'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="focal"></span>Channel OSNR (dB) &amp; Branch BU-03</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="warn"></span>Span S5 Anchor Anomaly (362 km)</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="danger"></span>15.0 dB SD-FEC Limit Floor</span>'
        '</div>'
        '<div class="va-table-wrap w2-table-wrap w2-table-mt"><table class="w2-table" aria-label="Repeater and span telemetry ledger">'
        '<thead><tr><th>Node / Span</th><th>Dist.</th><th>Depth</th><th>Pump Current</th><th>Span Loss</th><th>OSNR</th><th>Status</th></tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div></section></div>'
    )


def _fmt_sav(diff: float) -> str:
    return f"${diff:.2f}M saved" if diff >= 0 else f"+${abs(diff):.2f}M cost"


def compute_v26_model(growth_pct: int = 25, commit_pct: int = 60, runway_floor: int = 24) -> dict[str, object]:
    """Compute exact 36-month cumulative spend trajectories, crossover month, and runway feasibility."""
    g, c = growth_pct / 100.0, commit_pct / 100.0
    up_b = (250.0 + 275.0 * c) / 1000.0
    mult_b = c * 0.56 + (1.0 - c) * 1.05
    pts_a, pts_b, pts_c = [0.0], [up_b], [2.10]
    cum_a, cum_b, cum_c = 0.0, up_b, 2.10
    cross_b: int | None = None
    cross_c: int | None = None
    for m in range(1, 37):
        paygo_m = (110.0 * ((1.0 + g) ** ((m - 1) / 12.0))) / 1000.0
        colo_m = (64.0 + 12.0 * ((1.0 + 0.5 * g) ** ((m - 1) / 12.0))) / 1000.0
        cum_a += paygo_m
        cum_b += paygo_m * mult_b
        cum_c += colo_m
        pts_a.append(round(cum_a, 3))
        pts_b.append(round(cum_b, 3))
        pts_c.append(round(cum_c, 3))
        if cross_b is None and cum_b <= cum_a:
            cross_b = m
        if cross_c is None and cum_c <= cum_a:
            cross_c = m
    runway_a = max(14, round(38 - g * 18))
    runway_b = max(16, round(36 - c * 4 - g * 10))
    runway_c = max(10, round(22 - g * 12))
    total_a, total_b, total_c = round(cum_a, 2), round(cum_b, 2), round(cum_c, 2)
    feas_a, feas_b, feas_c = runway_a >= runway_floor, runway_b >= runway_floor, runway_c >= runway_floor
    cands = [
        (name, tot)
        for name, tot, ok in (("Option B Hybrid", total_b, feas_b), ("Option A PayGo", total_a, feas_a), ("Option C Colo", total_c, feas_c))
        if ok
    ]
    winner = min(cands, key=lambda x: x[1])[0] if cands else "None (Runway Blocked)"
    win_tot = next((t for n, t in cands if n == winner), 0.0)
    rec_state = "fault" if not cands else ("warn" if win_tot > 5.20 else "nominal")
    y_max = 8.0 if max(total_a, total_b, total_c) > 6.2 else 6.5
    return {
        "pts_a": pts_a, "pts_b": pts_b, "pts_c": pts_c,
        "total_a": total_a, "total_b": total_b, "total_c": total_c,
        "savings": round(total_a - total_b, 2), "savings_c": round(total_a - total_c, 2),
        "crossover": cross_b, "crossover_c": cross_c,
        "runway_a": runway_a, "runway_b": runway_b, "runway_c": runway_c,
        "feas_a": feas_a, "feas_b": feas_b, "feas_c": feas_c,
        "winner": winner, "rec_state": rec_state, "up_b": round(up_b, 2), "y_max": y_max,
    }


def _v26_chart_svg(model: dict[str, object]) -> str:
    y_max = float(model.get("y_max", 6.5))  # type: ignore[arg-type]

    def _poly(vals: list[float]) -> str:
        return "M " + " L ".join(
            f"{74.0 + (m / 36.0) * 724.0:.1f} {232.0 - min(y_max, v) / y_max * 194.0:.1f}"
            for m, v in enumerate(vals)
        )

    ticks = (0.0, 2.0, 4.0, 6.0, 8.0) if y_max > 7.0 else (0.0, 2.0, 4.0, 6.0)
    grid_y = "".join(
        f'<line x1="74" y1="{232.0 - (v / y_max) * 194.0:.1f}" x2="798" y2="{232.0 - (v / y_max) * 194.0:.1f}" stroke="var(--border-subtle)" stroke-dasharray="2 3"/>'
        f'<text x="66" y="{236.0 - (v / y_max) * 194.0:.1f}" text-anchor="end" font-size="11.5" fill="var(--text-muted)">${v:.1f}M</text>'
        for v in ticks
    )
    grid_x = "".join(
        f'<text x="{74.0 + (m / 36.0) * 724.0:.1f}" y="252" text-anchor="middle" font-size="11.5" fill="var(--text-muted)">Mo {m}</text>'
        for m in (0, 6, 12, 18, 24, 30, 36)
    )
    y_ceil = 232.0 - (5.2 / y_max) * 194.0
    cross_m = model["crossover"]
    cm = int(cross_m) if cross_m is not None else 14  # type: ignore[arg-type]
    cx = 74.0 + (cm / 36.0) * 724.0
    cy = 232.0 - min(y_max, float(model["pts_b"][cm])) / y_max * 194.0  # type: ignore[index]
    box_x = min(cx + 8.0, 646.0)
    c_disp = "" if cross_m is not None else ' display="none"'
    return (
        '<svg data-v26-svg viewBox="0 0 840 264" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="36-month cumulative spend curves for Options A, B, and C with break-even crossover marker">'
        f'<g data-v26-ygrid>{grid_y}</g>{grid_x}'
        f'<line data-v26-ceil-line x1="74" y1="{y_ceil:.1f}" x2="798" y2="{y_ceil:.1f}" stroke="var(--status-danger)" stroke-dasharray="6 4" stroke-width="1.5"/>'
        f'<rect data-v26-ceil-bg x="80" y="{y_ceil - 18:.1f}" width="174" height="16" rx="2" fill="var(--bg-surface)" opacity="0.94"/>'
        f'<text data-v26-ceil-lbl x="86" y="{y_ceil - 6:.1f}" text-anchor="start" font-size="11.5" font-weight="650" fill="var(--status-danger)">Budget Ceiling ($5.20M)</text>'
        f'<line data-v26-cross-line{c_disp} x1="{cx:.1f}" y1="24" x2="{cx:.1f}" y2="232" stroke="var(--accent-focal)" stroke-dasharray="4 3" stroke-width="1.4"/>'
        f'<path data-v26-path="a" d="{_poly(model["pts_a"])}" fill="none" stroke="var(--text-muted)" stroke-width="2.1"/>'  # type: ignore[arg-type]
        f'<path data-v26-path="c" d="{_poly(model["pts_c"])}" fill="none" stroke="var(--status-warn)" stroke-width="2.1" stroke-dasharray="5 3"/>'  # type: ignore[arg-type]
        f'<path data-v26-path="b" d="{_poly(model["pts_b"])}" fill="none" stroke="var(--accent-focal)" stroke-width="2.6"/>'  # type: ignore[arg-type]
        f'<circle data-v26-cross-dot{c_disp} cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="var(--accent-focal)" stroke="var(--bg-surface)" stroke-width="1.8"/>'
        f'<rect data-v26-cross-bg{c_disp} x="{box_x:.1f}" y="{max(20.0, cy - 26):.1f}" width="184" height="19" rx="3" fill="var(--bg-surface)" stroke="var(--accent-focal)"/>'
        f'<text data-v26-cross-lbl{c_disp} x="{box_x + 6:.1f}" y="{max(33.0, cy - 13):.1f}" font-size="11.5" font-weight="650" fill="var(--accent-focal)">Break-Even Crossover (Mo {cm})</text>'
        '</svg>'
    )


def _disp_lbl(opt_name: str, feas: bool, winner: object) -> str:
    return "RUNWAY BLOCKED" if not feas else ("RECOMMENDED" if winner == opt_name else "VIABLE")


def build_v26_matrix_rows(model: dict[str, object]) -> str:
    """Build 10-row Constrained Trade-Space Decision Matrix shared between v26 and Specimen 53."""
    cb = f"Month {model['crossover']}" if model["crossover"] is not None else "No crossover"
    cc = f"Month {model['crossover_c']}" if model["crossover_c"] is not None else "No crossover"
    ta, tb, tc = float(model["total_a"]), float(model["total_b"]), float(model["total_c"])  # type: ignore[arg-type]
    rows = (
        ("Upfront Cash Outlay", "$0.00M", f"${model['up_b']:.2f}M", "$2.10M", "upfront"),
        ("36-Month Total Spend", f"${ta:.2f}M", f"${tb:.2f}M", f"${tc:.2f}M", "total"),
        ("Net Savings vs PayGo", "$0.00M (Base)", _fmt_sav(float(model["savings"])), _fmt_sav(float(model["savings_c"])), "savings"),  # type: ignore[arg-type]
        ("Break-Even Crossover", "Baseline", cb, cc, "crossover"),
        ("Cash Runway Headroom", f"{model['runway_a']} mo", f"{model['runway_b']} mo", f"{model['runway_c']} mo", "runway"),
        ("Budget Ceiling Fit ($5.20M)", "Within Cap" if ta <= 5.2 else "Over Ceiling", "Within Cap" if tb <= 5.2 else "Over Ceiling", "Within Cap" if tc <= 5.2 else "Over Ceiling", "cap"),
        ("Peak Burst Elasticity", "Unbounded", "Auto Cloud Burst", "Hardware Lead-Time (10 wk)", "burst"),
        ("Committed Unit Discount", "0% list pricing", "44% reserved base", "Lowest marginal rack power", "discount"),
        ("Vendor Lock-In / Exit Cost", "Zero exit penalty", "3-yr commit balance", "Sunk CapEx + 24 mo colocation lease", "exit"),
        ("Governance Disposition", _disp_lbl("Option A PayGo", bool(model["feas_a"]), model["winner"]), _disp_lbl("Option B Hybrid", bool(model["feas_b"]), model["winner"]), _disp_lbl("Option C Colo", bool(model["feas_c"]), model["winner"]), "disp"),
    )
    return "".join(
        f'<tr data-v26-row="{key}"><td>{lbl}</td>'
        f'<td class="w2-num" data-col="a">{a}</td>'
        f'<td class="w2-num" data-col="b"><strong>{b}</strong></td>'
        f'<td class="w2-num" data-col="c">{c}</td></tr>'
        for lbl, a, b, c, key in rows
    )


def build_v26_html() -> str:
    """Build View v26 Constrained Trade-Space & Capital Runway Calculator."""
    model = compute_v26_model(25, 60, 24)
    cb_txt = f"Month {model['crossover']}" if model["crossover"] is not None else "No crossover"
    return (
        '<div class="w2-stack" data-v26-scope="studio" data-v26-root>'
        '<div class="w2-kpi-grid">'
        '<div class="w2-kpi-tile" data-state="nominal"><span class="w2-kpi-lbl">Recommended Trajectory</span>'
        f'<span class="w2-kpi-val" data-v26-kpi="winner">{model["winner"]}</span><span class="w2-kpi-sub" data-v26-kpi="savings">Saves ${model["savings"]:.2f}M vs PayGo</span></div>'
        '<div class="w2-kpi-tile" data-state="nominal"><span class="w2-kpi-lbl">Break-Even Crossover</span>'
        f'<span class="w2-kpi-val" data-v26-kpi="crossover">{cb_txt}</span><span class="w2-kpi-sub" data-v26-kpi="cross_sub">Option B crosses below Option A</span></div>'
        '<div class="w2-kpi-tile" data-state="nominal"><span class="w2-kpi-lbl">36-Month Total Spend</span>'
        f'<span class="w2-kpi-val" data-v26-kpi="total_b">${model["total_b"]:.2f}M</span><span class="w2-kpi-sub">vs $5.20M budget ceiling</span></div>'
        '<div class="w2-kpi-tile" data-state="warn"><span class="w2-kpi-lbl">Cash Runway Gate</span>'
        f'<span class="w2-kpi-val" data-v26-kpi="runway_b">{model["runway_b"]} mo</span><span class="w2-kpi-sub" data-v26-kpi="runway_note">Option C {model["runway_c"]} mo vs 24 mo floor</span></div>'
        '</div>'
        '<section class="w2-card" aria-labelledby="v26-calc-title">'
        '<div class="w2-card-hdr"><div>'
        '<h2 id="v26-calc-title" class="w2-card-title">36-Month Infrastructure Trade-Space &amp; Break-Even Calculator</h2>'
        '<p class="w2-card-sub">Adjust workload growth, commit coverage, and runway floor constraints to update 36-month capital curves.</p>'
        f'</div><span class="va-pill" data-variant="status" data-state="{model["rec_state"]}" data-v26-rec-badge>RECOMMENDED: {str(model["winner"]).upper()}</span></div>'
        '<div class="w2-sliders-grid" role="region" aria-label="Trade-space model parameters">'
        '<div class="w2-slider-field"><label class="w2-slider-hdr" for="v26-growth"><span>Annual Workload Growth</span>'
        '<span class="w2-slider-val" data-v26-out="growth">25%</span></label>'
        '<input type="range" id="v26-growth" class="w2-slider" data-v26-input="growth" min="10" max="50" step="5" value="25"/></div>'
        '<div class="w2-slider-field"><label class="w2-slider-hdr" for="v26-commit"><span>Reserved Commit Coverage</span>'
        '<span class="w2-slider-val" data-v26-out="commit">60%</span></label>'
        '<input type="range" id="v26-commit" class="w2-slider" data-v26-input="commit" min="20" max="80" step="5" value="60"/></div>'
        '<div class="w2-slider-field"><label class="w2-slider-hdr" for="v26-runway"><span>Minimum Cash Runway Floor</span>'
        '<span class="w2-slider-val" data-v26-out="runway">24 mo</span></label>'
        '<input type="range" id="v26-runway" class="w2-slider" data-v26-input="runway" min="18" max="36" step="3" value="24"/></div>'
        '</div>'
        f'<div class="w2-svg-box">{_v26_chart_svg(model)}</div>'
        '<div class="w2-legend-row" aria-label="Cumulative spend legend">'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="focal"></span>Option B: Hybrid 3-Yr Commit + Burst</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="muted"></span>Option A: Elastic Cloud Pay-As-You-Go</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="warn"></span>Option C: Dedicated Colocation CapEx</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="danger"></span>Budget Ceiling ($5.20M)</span>'
        '</div>'
        '<div class="va-table-wrap w2-table-wrap"><table class="w2-table" aria-label="10-row trade-space comparison matrix">'
        '<thead><tr><th>Evaluation Criterion</th><th>Option A · PayGo</th><th>Option B · Hybrid Commit</th><th>Option C · Colocation</th></tr></thead>'
        f'<tbody data-v26-tbody>{build_v26_matrix_rows(model)}</tbody></table></div></section></div>'
    )
