# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 1 (Scalar/Gauge) & Modality 2 (Table/Matrix) Compilers."""

from __future__ import annotations

import math
import re
from typing import Any

from .svg_labels import halo_text, render_pill_html
from .tokens_and_scales import (
    ANNUNCIATOR_STATES,
    compute_linear_125_scale,
    esc,
    format_math_html,
    format_quantity_header,
    format_tick_numeral,
    format_value_unit,
)

_ISO_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T(\d{2}):(\d{2})(?::\d{2})?Z?$")
_SI_UNIT_WRAP_RE = re.compile(r"\b(mmHg|cmH2O|mmol/L|mEq/L|mg/dL|kPa|hPa|kHz|MHz|GHz|mrad|dBm|ps|ms|mV|kW|MW|mA)\b")


def _finite_num(val: Any, default: float | None = None) -> float | None:
    try:
        n = float(val)
        return n if math.isfinite(n) else default
    except (TypeError, ValueError):
        return default


def _fmt_signed(val: Any) -> str:
    n = _finite_num(val)
    if n is None:
        return esc(val)
    return "0" if n == 0.0 else esc(f"{n:+g}")


def _format_l1_timestamp(ts: str) -> str:
    """Convert ISO-8601 UTC stamp to plain-language time for L1 consumer views."""
    s = str(ts).strip()
    m = _ISO_TS_RE.match(s)
    if not m:
        return s
    h24, mins = int(m.group(1)), int(m.group(2))
    ampm = "AM" if h24 < 12 else "PM"
    h12 = h24 % 12 or 12
    return f"Checked Today · {h12}:{mins:02d} {ampm}"


def _format_l1_goal(qty: dict[str, Any], limits: dict[str, Any], unit: str) -> str:
    """Render plain-language target text instead of NIST slash calculus for L1."""
    if qty.get("target_label"):
        return str(qty["target_label"])
    warn = limits.get("warning_thresholds", {})
    if warn.get("lower") is not None:
        return f"Goal: {format_value_unit(float(warn['lower']), unit)} or higher"
    if warn.get("upper") is not None:
        return f"Goal: {format_value_unit(float(warn['upper']), unit)} or lower"
    if limits.get("nominal_target") is not None:
        return f"Goal: {format_value_unit(float(limits['nominal_target']), unit)}"
    return str(qty.get("name", ""))


def _l1_status_label(disp_key: str, ann: dict[str, Any]) -> str:
    if ann.get("l1_label"):
        return str(ann["l1_label"])
    return {
        "NOMINAL": "On Track",
        "ADVISORY": "Recheck in 15 min",
        "WARNING": "Recheck in 15 min",
        "CRITICAL": "Call Clinic Now",
        "STALE": "Check Sensor",
        "FAULT": "Check Sensor",
    }.get(disp_key, "On Track")


def _wrap_id(text: str) -> str:
    """Insert <wbr> break hints in long identifiers and shield SI units from uppercase CSS."""
    escaped = esc(text)
    parts = _SI_UNIT_WRAP_RE.split(escaped)
    out: list[str] = []
    for idx, seg in enumerate(parts):
        if idx % 2 == 1:
            out.append(f'<span class="qe-unit">{seg}</span>')
            continue
        for sep in ("-", "/", ":", "_"):
            seg = seg.replace(sep, f"{sep}<wbr>")
        out.append(seg)
    return "".join(out)


def _clamp_x(val: float, xmin: float, xmax: float, x0: float, width: float) -> tuple[float, int]:
    """Normalize value to SVG X pixel coordinate with overflow flag (-1, 0, +1)."""
    span = xmax - xmin if xmax != xmin else 1.0
    if val < xmin:
        return x0, -1
    if val > xmax:
        return x0 + width, 1
    return x0 + ((val - xmin) / span) * width, 0


def _resolve_threshold_state(nom: Any, limits: dict[str, Any], ann: dict[str, Any], st_key: str) -> str:
    """Derive threshold disposition independently of data-quality state (STALE/FAULT)."""
    if st_key in {"NOMINAL", "ADVISORY", "WARNING", "CRITICAL"}:
        return st_key
    explicit = str(ann.get("threshold_state", "")).upper()
    if explicit in {"NOMINAL", "ADVISORY", "WARNING", "CRITICAL"}:
        return explicit
    try:
        v = float(nom)
    except (TypeError, ValueError):
        return "NOMINAL"
    abort = limits.get("abort_thresholds", {})
    warn = limits.get("warning_thresholds", {})
    if (abort.get("lower") is not None and v <= float(abort["lower"])) or (abort.get("upper") is not None and v >= float(abort["upper"])):
        return "CRITICAL"
    if (warn.get("lower") is not None and v <= float(warn["lower"])) or (warn.get("upper") is not None and v >= float(warn["upper"])):
        return "WARNING"
    return "NOMINAL"


def _render_gauge_svg(spec: dict[str, Any], rigor: str) -> str:
    """Render NASA/ISA/IEC linear envelope bar gauge with CMD vs ACT markers."""
    gauge, limits, meas = spec.get("gauge", {}), spec.get("limits", {}), spec.get("measurement", {})
    unit = spec.get("quantity", {}).get("unit", "")
    act = _finite_num(meas.get("nominal_value"), _finite_num(gauge.get("marker_position"), 0.0)) or 0.0
    cmd = _finite_num(limits.get("nominal_target"), _finite_num(gauge.get("commanded_value")))
    warn, abort = limits.get("warning_thresholds", {}), limits.get("abort_thresholds", {})
    lo_abort, hi_abort = _finite_num(abort.get("lower")), _finite_num(abort.get("upper"))
    lo_warn, hi_warn = _finite_num(warn.get("lower")), _finite_num(warn.get("upper"))
    bnd_vals = [v for v in (act, lo_abort, hi_abort, lo_warn, hi_warn, cmd if rigor in {"L2", "L3"} else None) if v is not None]
    span_guess = max((max(bnd_vals) - min(bnd_vals)) * 0.2, abs(act) * 0.1, 2.0)
    smin = _finite_num(gauge.get("min_scale"), min(bnd_vals) - span_guess)
    smax = _finite_num(gauge.get("max_scale"), max(bnd_vals) + span_guess)
    if smin > smax:
        smin, smax = smax, smin
    if math.isclose(smin, smax, rel_tol=1e-12, abs_tol=1e-12):
        pad = abs(smin) * 0.1 or 1.0
        smin, smax = smin - pad, smax + pad

    x0, x1, y_bar, bh = 24.0, 316.0, 25.0, 10.0
    bw = x1 - x0
    parts: list[str] = [
        f'<svg class="qe-svg qe-gauge-svg" viewBox="0 0 340 72" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Linear Gauge"))}">',
        f'<rect data-role="gauge-track" x="{x0}" y="{y_bar}" width="{bw}" height="{bh}" rx="2.5" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1"/>',
    ]

    def _zone(lo: float | None, hi: float | None, fill: str) -> None:
        if lo is not None and hi is not None:
            zx0, _ = _clamp_x(lo, smin, smax, x0, bw)
            zx1, _ = _clamp_x(hi, smin, smax, x0, bw)
            if zx1 > zx0:
                parts.append(f'<rect data-role="gauge-zone" x="{zx0:.1f}" y="{y_bar + 1:.1f}" width="{zx1 - zx0:.1f}" height="{bh - 2:.1f}" fill="{fill}"/>')

    for lo_z, hi_z, col in (
        (smin, lo_abort, "var(--status-err-bg)"), (hi_abort, smax, "var(--status-err-bg)"),
        (lo_abort if lo_abort is not None else smin, lo_warn, "var(--status-warn-bg)"),
        (hi_warn, hi_abort if hi_abort is not None else smax, "var(--status-warn-bg)"),
    ):
        if (col == "var(--status-err-bg)" and ((lo_z == smin and lo_abort is not None) or (hi_z == smax and hi_abort is not None))) or (
            col == "var(--status-warn-bg)" and ((lo_z is not None and hi_z == lo_warn and lo_warn is not None) or (lo_z == hi_warn and hi_warn is not None))
        ):
            _zone(lo_z, hi_z, col)
    for thr, col in ((lo_abort, "var(--status-danger)"), (hi_abort, "var(--status-danger)"), (lo_warn, "var(--status-warn)"), (hi_warn, "var(--status-warn)")):
        if thr is not None:
            tx, _ = _clamp_x(thr, smin, smax, x0, bw)
            parts.append(f'<line x1="{tx:.1f}" y1="{y_bar - 2.5}" x2="{tx:.1f}" y2="{y_bar + bh + 2.5}" stroke="{col}" stroke-width="1.5"/>')

    scale, last_lx = compute_linear_125_scale(smin, smax, target_ticks=4), -999.0
    for tick in scale["majors"]:
        if smin - 1e-9 <= tick <= smax + 1e-9:
            tx, _ = _clamp_x(tick, smin, smax, x0, bw)
            parts.append(f'<line x1="{tx:.1f}" y1="{y_bar + bh}" x2="{tx:.1f}" y2="{y_bar + bh + 3.5}" stroke="var(--border-strong)" stroke-width="1"/>')
            if tx - last_lx >= 42.0:
                parts.append(halo_text(tx, y_bar + bh + 15.5, format_tick_numeral(tick, step=scale["step"]), anchor="middle", size=12.7, fill="var(--text-muted)", halo=False))
                last_lx = tx

    if cmd is not None and rigor in {"L2", "L3"}:
        cx, _ = _clamp_x(cmd, smin, smax, x0, bw)
        cmd_lbl = f"CMD\u00a0{cmd:g}"
        hw = min(158.0, len(cmd_lbl) * 3.8)
        cx_txt = max(8.0 + hw, min(332.0 - hw, cx))
        parts.append(f'<polygon points="{cx:.1f},{y_bar - 1} {cx - 4:.1f},{y_bar - 7} {cx + 4:.1f},{y_bar - 7}" fill="var(--bg-canvas)" stroke="var(--text-primary)" stroke-width="1.2"/>')
        parts.append(halo_text(cx_txt, 15.5, cmd_lbl, anchor="middle", size=12.7, weight="600", fill="var(--text-secondary)", halo=False))

    ax, ovf = _clamp_x(act, smin, smax, x0, bw)
    ann = spec.get("status_annunciator", {})
    st_code = _resolve_threshold_state(act, limits, ann, str(ann.get("state", "NOMINAL")).upper())
    pin_col = ANNUNCIATOR_STATES.get(st_code, ANNUNCIATOR_STATES["NOMINAL"])["gauge_fg"]
    parts.append(f'<polygon points="{ax:.1f},{y_bar + 2} {ax - 4.5:.1f},{y_bar + bh + 4.5} {ax + 4.5:.1f},{y_bar + bh + 4.5}" fill="{pin_col}" stroke="var(--bg-canvas)" stroke-width="1"/>')
    act_lbl = f"ACT\u00a0{format_value_unit(act, unit)}" if ovf == 0 else ("◀ CLAMPED" if ovf < 0 else "CLAMPED ▶")
    act_w = min(320.0, len(act_lbl) * 7.7)
    if ax < 80.0:
        lbl_anchor, tx_act = "start", max(6.0, min(max(6.0, 334.0 - act_w), ax))
    elif ax > 260.0:
        lbl_anchor, tx_act = "end", min(334.0, max(min(334.0, 6.0 + act_w), ax))
    else:
        lbl_anchor, tx_act = "middle", max(min(170.0, 6.0 + act_w / 2.0), min(max(170.0, 334.0 - act_w / 2.0), ax))
    parts.append(halo_text(tx_act, 66.5, act_lbl, anchor=lbl_anchor, size=12.8, weight="700", fill=pin_col, halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


def _render_single_scalar(spec: dict[str, Any], rigor: str, medium: str, chrome: str = "bench") -> str:
    """Compile one scalar readout card across L1, L2, and L3 rigor."""
    meta = spec.get("metadata", {})
    qty = spec.get("quantity", {})
    meas = spec.get("measurement", {})
    ann = spec.get("status_annunciator", {})
    limits = spec.get("limits", {})
    st_key = str(ann.get("state", "NOMINAL")).upper()
    disp_key = _resolve_threshold_state(meas.get("nominal_value", 0), limits, ann, st_key)
    disp_info = ANNUNCIATOR_STATES.get(disp_key, ANNUNCIATOR_STATES["NOMINAL"])

    unit = str(qty.get("unit", ""))
    nom = meas.get("nominal_value", 0)
    unc = meas.get("expanded_uncertainty") if rigor == "L3" else None
    val_text = format_value_unit(nom, unit, unc)
    calculus = qty.get("quantity_calculus") or format_quantity_header(qty.get("symbol", "x"), None, unit)
    subsys = meta.get("plain_label", "") if rigor == "L1" else meta.get("subsystem", "TELEMETRY")
    ts = _format_l1_timestamp(meta.get("timestamp_utc", "")) if rigor == "L1" else meta.get("timestamp_utc", "")
    margin = ann.get("margin_remaining_pct")
    if st_key == "STALE":
        quality_pill = render_pill_html("STALE DATA", variant="status", state="warn")
    elif st_key == "FAULT":
        quality_pill = render_pill_html("SENSOR FAULT", variant="status", state="fault")
    else:
        quality_pill = ""

    lines: list[str] = ['<div class="qe-scalar-card">']
    ts_part = f"{esc(ts)} {quality_pill}".strip() if quality_pill else esc(ts)
    left_kicker = f'<span class="va-kicker">{esc(subsys)}</span>' if subsys else "<span></span>"
    lines.append(f'<div class="qe-scalar-zone1 qe-scalar-top">{left_kicker}<span class="qe-scalar-ts va-nums">{ts_part}</span></div>')
    lines.append(f'<h3 class="qe-scalar-title">{esc(meta.get("title", "Scalar Readout"))}</h3>')
    lines.append('<div class="qe-scalar-zone2 qe-scalar-val-row">')
    calc_html = esc(_format_l1_goal(qty, limits, unit)) if rigor == "L1" else format_math_html(calculus)
    lines.append(f'  <div class="qe-scalar-val-wrap"><span class="qe-scalar-val va-nums">{esc(val_text)}</span><span class="qe-scalar-calc qe-unit">{calc_html}</span></div>')
    pill_txt = _l1_status_label(disp_key, ann) if rigor == "L1" else disp_info["pill"]
    disp_pill = render_pill_html(pill_txt, variant="status", state=disp_info["state"])
    margin_html = f'<span class="qe-scalar-margin va-nums">Margin {float(margin):+.1f}%</span>' if (margin is not None and rigor in {"L2", "L3"}) else ""
    lines.append(f'  <div class="qe-scalar-disp">{disp_pill}{margin_html}</div>')
    lines.append("</div>")

    if rigor == "L1" and spec.get("sparkline"):
        pts = [float(v) for v in spec["sparkline"]]
        lo, hi = min(pts), max(pts)
        span = hi - lo if hi != lo else 1.0
        coords = " ".join(f"{16 + i * (288.0 / max(len(pts) - 1, 1)):.1f},{28 - ((v - lo) / span) * 20:.1f}" for i, v in enumerate(pts))
        lines.append(f'<svg class="qe-svg qe-spark-svg" viewBox="0 0 320 34" role="img" aria-label="Trend sparkline"><polyline fill="none" stroke="{disp_info["gauge_fg"]}" stroke-width="1.8" points="{coords}"/></svg>')
    elif rigor in {"L2", "L3"} and (spec.get("gauge") or limits):
        lines.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Gauge"))}">{_render_gauge_svg(spec, rigor)}</div>')

    if rigor == "L2" and isinstance(limits.get("tolerance_band"), (list, tuple)) and len(limits["tolerance_band"]) >= 2:
        tol = limits["tolerance_band"]
        tgt = limits.get("nominal_target", "")
        lines.append(f'<div class="qe-scalar-meta va-nums">Target: {esc(format_value_unit(tgt, unit))} | Tolerance Band: [{_fmt_signed(tol[0])}, {_fmt_signed(tol[1])}] {esc(unit)}</div>')

    if rigor == "L3":
        k_cov = meas.get("coverage_factor", 2.0)
        conf = meas.get("confidence_pct", 95.45)
        meta_div = f'<div class="qe-scalar-meta va-nums">Expanded Uncertainty: {esc(val_text)} | k={esc(k_cov)} | {esc(conf)}% CI</div>'
        prov: list[str] = []
        if meas.get("sensor_id"):
            prov.append(f'Sensor: {meas["sensor_id"]}')
        if meas.get("calibration_id"):
            prov.append(f'Cal: {meas["calibration_id"]}')
        if meas.get("raw_adc_counts") is not None:
            prov.append(f'Raw ADC: {meas["raw_adc_counts"]} cts')
        prov_div = f'<div class="qe-scalar-prov va-nums">{esc(" | ".join(prov))}</div>' if prov else ""
        if chrome == "embedded":
            try:
                k_txt = f"{float(k_cov):g}" if k_cov is not None else "2"
            except (TypeError, ValueError):
                k_txt = str(k_cov)
            lines.append(
                f'<details class="qe-cal-footer"><summary class="qe-cal-summary va-nums">'
                f'Calibration &amp; Sensor Provenance (k={esc(k_txt)} · NIST)</summary>'
                f'{meta_div}{prov_div}</details>'
            )
        else:
            lines.append(meta_div)
            if prov_div:
                lines.append(prov_div)
    lines.append("</div>")
    return "\n".join(lines)


def compile_scalar(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white", chrome: str = "bench") -> str:
    """Compile Modality 1 (urn:quiet-ui:schema:v9:scalar) into semantic HTML/SVG."""
    eff_rigor = (rigor or spec.get("metadata", {}).get("rigor_level", "L2")).upper()
    items = spec.get("items")
    if isinstance(items, list) and items:
        grid = "\n".join(_render_single_scalar(it, eff_rigor, medium, chrome=chrome) for it in items)
        return f'<div class="qe-scalar-grid" data-count="{len(items)}" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}">{grid}</div>'
    return _render_single_scalar(spec, eff_rigor, medium, chrome=chrome)


def _render_heatmap_svg(hm: dict[str, Any]) -> str:
    """Render calibrated R x C phase-excursion heatmap with ISA-101 quiet-nominal cells."""
    cols = hm.get("col_labels", [])
    rows = hm.get("rows", [])
    cell_w, cell_h, x0, y0 = 70.0, 24.0, 84.0, 26.0
    vb_w = int(max(640.0, x0 + len(cols) * cell_w + 20.0))
    vb_h = int(y0 + len(rows) * (cell_h + 6.0) + 18.0)
    parts: list[str] = [f'<svg class="qe-svg qe-svg-680" viewBox="0 0 {vb_w} {vb_h}" role="img" aria-label="{esc(hm.get("title", "Excursion Heatmap"))}">']
    for ci, clbl in enumerate(cols):
        cx = x0 + ci * cell_w + cell_w / 2.0
        parts.append(halo_text(cx, 16.0, str(clbl), anchor="middle", size=11.5, weight="700", fill="var(--text-secondary)", halo=False))
    status_style = {
        "ok": ("nominal", "var(--bg-elevated)", "var(--border-hairline)", "1.0", "var(--text-primary)", "500", ""),
        "warn": ("warn", "var(--status-warn-bg)", "var(--status-warn)", "1.8", "var(--status-warn)", "700", "▲ "),
        "err": ("fault", "var(--status-err-bg)", "var(--status-danger)", "2.0", "var(--status-danger)", "700", "◆ "),
    }
    for ri, row in enumerate(rows):
        ry = y0 + ri * (cell_h + 6.0)
        parts.append(halo_text(x0 - 10.0, ry + 16.0, str(row.get("label", "")), anchor="end", size=11.5, weight="600", fill="var(--text-muted)", halo=False))
        for ci, cell in enumerate(row.get("cells", [])):
            cx = x0 + ci * cell_w
            st = str(cell.get("status", "ok")).lower()
            st_attr, bg, stroke, sw, txt_col, txt_w, prefix = status_style.get(st, status_style["ok"])
            dash = ' stroke-dasharray="4,2"' if st == "warn" else ""
            parts.append(
                f'<rect class="qe-heatmap-cell" data-role="bitcell" data-state="{st_attr}" '
                f'x="{cx + 2:.1f}" y="{ry:.1f}" width="{cell_w - 6:.1f}" height="{cell_h:.1f}" rx="3" '
                f'fill="{bg}" stroke="{stroke}" stroke-width="{sw}"{dash}/>'
            )
            val = str(cell.get("text", ""))
            if val:
                parts.append(halo_text(cx + (cell_w - 2) / 2.0, ry + 16.0, f"{prefix}{val}", anchor="middle", size=11.5, weight=txt_w, fill=txt_col, halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


def _status_badge_html(val: Any) -> str:
    """Render ISA-101 quiet-nominal or framed excursion .va-pill for table cells."""
    raw = str(val).strip()
    s = raw.upper()
    if s in {"AUTHORIZED", "NOMINAL", "ACTIVE", "PASS", "GO", "LOCKED", "VERIFIED", "APPROVED"}:
        return render_pill_html(raw.title(), variant="status", state="nominal")
    if s in {"CONDITIONAL", "CAUTION", "WARNING", "DEGRADED", "MARGINAL", "WATCH", "REVIEW"}:
        return render_pill_html(s, variant="status", state="warn")
    if s in {"REJECTED", "CRITICAL", "ABORT", "OFFLINE", "FAULT", "FAIL", "HOLD", "BREACH"}:
        return render_pill_html(s, variant="status", state="fault")
    return render_pill_html(raw, variant="tag")


def _format_col_header_html(c: dict[str, Any]) -> str:
    """Wrap NIST/SI units and quantity symbols in <span class='qe-unit'> to prevent uppercase corruption."""
    qc = c.get("quantity_calculus")
    if qc:
        return f'<span class="qe-unit">{format_math_html(qc)}</span>'
    lbl = str(c.get("label", c.get("key", "")))
    unit = str(c.get("unit", "")).strip()
    if unit and unit != "1":
        m = re.search(rf"(?<![A-Za-z0-9_]){re.escape(unit)}(?![A-Za-z0-9_])", lbl)
        if m:
            return f'{esc(lbl[:m.start()])}<span class="qe-unit">{esc(m.group(0))}</span>{esc(lbl[m.end():])}'
        return f'{esc(lbl)} (<span class="qe-unit">{esc(unit)}</span>)'
    return esc(lbl)


def compile_table(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white", chrome: str = "bench") -> str:
    """Compile Modality 2 (urn:quiet-ui:schema:v9:table) into responsive Booktabs/PPSM HTML."""
    meta = spec.get("metadata", {})
    eff_rigor = (rigor or meta.get("rigor_level", "L2")).upper()
    max_prio = 1 if eff_rigor == "L1" else (2 if eff_rigor == "L2" else 3)
    all_cols = spec.get("columns", [])
    cols = [c for c in all_cols if int(c.get("priority", 1)) <= max_prio] or all_cols
    rows = spec.get("rows", [])
    title = meta.get("title", "Quantitative Ledger")

    out: list[str] = []
    if spec.get("heatmap") and eff_rigor in {"L2", "L3"}:
        hm = spec["heatmap"]
        out.append(f'<div class="va-figure-scroll qe-heatmap-wrap" tabindex="0" role="region" aria-label="{esc(hm.get("title", "Excursion Heatmap"))}">{_render_heatmap_svg(hm)}</div>')

    tbl_cls = "booktabs qe-table" if eff_rigor == "L3" else "va-data-table qe-table"
    out.append(f'<div class="va-bleed-wide va-table-wrap qe-table-wrap" tabindex="0" role="region" aria-label="{esc(title)}">')
    out.append(f'<table class="{tbl_cls}">')
    out.append(f'<caption class="qe-table-caption qe-caption-sr">{esc(title)}</caption>')
    out.append("<thead><tr>")
    for c in cols:
        align_cls = "num" if c.get("data_type") == "numeric" or c.get("alignment") == "right" else ""
        out.append(f'<th scope="col" class="{align_cls}">{_format_col_header_html(c)}</th>')
    out.append("</tr></thead><tbody>")

    for row in rows:
        row_st = str(row.get("_row_status", "")).lower()
        tr_cls = "va-row-warn" if row_st == "warn" else ("qe-row-winner" if row_st == "winner" else "")
        out.append(f'<tr class="{tr_cls}">' if tr_cls else "<tr>")
        for idx, c in enumerate(cols):
            key = c["key"]
            raw = row.get(key, "—")
            lbl_txt = str(c.get("label", key))
            u_txt = str(c.get("unit", ""))
            if u_txt and u_txt != "1" and u_txt not in lbl_txt:
                lbl_txt = f"{lbl_txt} / {u_txt}"
            lbl = esc(lbl_txt)
            dtype = c.get("data_type", "string")
            if dtype == "status":
                cell_html = _status_badge_html(raw)
                td_cls = "qe-cell-center"
            elif dtype == "numeric":
                unc_key = c.get("uncertainty_key")
                unc_val = row.get(unc_key) if unc_key else None
                if unc_val is not None and isinstance(raw, (int, float)):
                    cell_html = esc(f"{raw:.3f} \u00b1 {float(unc_val):.3f}")
                elif isinstance(raw, float):
                    cell_html = esc(f"{raw:.3f}")
                else:
                    cell_html = esc(raw)
                td_cls = "num"
            else:
                cell_html = _wrap_id(str(raw))
                td_cls = ""
            tag = "th" if idx == 0 else "td"
            scope = ' scope="row"' if idx == 0 else ""
            cls_attr = f' class="{td_cls}"' if td_cls else ""
            out.append(f'<{tag}{scope}{cls_attr} data-label="{lbl}">{cell_html}</{tag}>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)
