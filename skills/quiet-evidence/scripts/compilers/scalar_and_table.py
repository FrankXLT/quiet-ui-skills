# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 1 (Scalar/Gauge) & Modality 2 (Table/Matrix) Compilers."""

from __future__ import annotations

from typing import Any

from .tokens_and_scales import (
    ANNUNCIATOR_STATES,
    compute_linear_125_scale,
    esc,
    format_math_html,
    format_quantity_header,
    format_tick_numeral,
    format_value_unit,
    halo_text,
)


def _wrap_id(text: str) -> str:
    """Insert <wbr> break hints in long identifiers to prevent desktop clipping."""
    escaped = esc(text)
    for sep in ("-", "/", ":", "_"):
        escaped = escaped.replace(sep, f"{sep}<wbr>")
    return escaped


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
    gauge = spec.get("gauge", {})
    limits = spec.get("limits", {})
    meas = spec.get("measurement", {})
    unit = spec.get("quantity", {}).get("unit", "")
    act = float(meas.get("nominal_value", gauge.get("marker_position", 0.0)))
    cmd = limits.get("nominal_target", gauge.get("commanded_value"))
    warn = limits.get("warning_thresholds", {})
    abort = limits.get("abort_thresholds", {})
    lo_abort, hi_abort = abort.get("lower"), abort.get("upper")
    lo_warn, hi_warn = warn.get("lower"), warn.get("upper")
    smin = float(gauge["min_scale"]) if gauge.get("min_scale") is not None else ((float(lo_abort) if lo_abort is not None else act - 5.0) - 1.0)
    smax = float(gauge["max_scale"]) if gauge.get("max_scale") is not None else ((float(hi_abort) if hi_abort is not None else act + 5.0) + 1.0)

    x0, x1, y_bar, bh = 38.0, 642.0, 38.0, 14.0
    bw = x1 - x0
    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-680" viewBox="0 0 680 92" role="img" '
        f'aria-label="{esc(spec.get("metadata", {}).get("title", "Linear Gauge"))}">'
    ]
    parts.append(f'<rect x="{x0}" y="{y_bar}" width="{bw}" height="{bh}" rx="3" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1"/>')

    def _zone(lo: float | None, hi: float | None, fill: str) -> None:
        if lo is None or hi is None:
            return
        zx0, _ = _clamp_x(float(lo), smin, smax, x0, bw)
        zx1, _ = _clamp_x(float(hi), smin, smax, x0, bw)
        if zx1 > zx0:
            parts.append(f'<rect x="{zx0:.1f}" y="{y_bar + 1:.1f}" width="{zx1 - zx0:.1f}" height="{bh - 2:.1f}" fill="{fill}"/>')

    if lo_abort is not None:
        _zone(smin, lo_abort, "var(--status-err-bg)")
    if hi_abort is not None:
        _zone(hi_abort, smax, "var(--status-err-bg)")
    if lo_warn is not None:
        _zone(lo_abort if lo_abort is not None else smin, lo_warn, "var(--status-warn-bg)")
    if hi_warn is not None:
        _zone(hi_warn, hi_abort if hi_abort is not None else smax, "var(--status-warn-bg)")

    for thr, col in ((lo_abort, "var(--status-danger)"), (hi_abort, "var(--status-danger)"),
                     (lo_warn, "var(--status-warn)"), (hi_warn, "var(--status-warn)")):
        if thr is not None:
            tx, _ = _clamp_x(float(thr), smin, smax, x0, bw)
            parts.append(f'<line x1="{tx:.1f}" y1="{y_bar - 3}" x2="{tx:.1f}" y2="{y_bar + bh + 3}" stroke="{col}" stroke-width="1.6"/>')

    scale = compute_linear_125_scale(smin, smax, target_ticks=5)
    last_lx = -999.0
    for tick in scale["majors"]:
        if tick < smin - 1e-9 or tick > smax + 1e-9:
            continue
        tx, _ = _clamp_x(tick, smin, smax, x0, bw)
        parts.append(f'<line x1="{tx:.1f}" y1="{y_bar + bh}" x2="{tx:.1f}" y2="{y_bar + bh + 5}" stroke="var(--border-strong)" stroke-width="1"/>')
        if tx - last_lx >= 48.0:
            lbl = format_tick_numeral(tick, step=scale["step"])
            parts.append(halo_text(tx, y_bar + bh + 19, lbl, anchor="middle", size=11.5, fill="var(--text-muted)", halo=False))
            last_lx = tx

    if cmd is not None and rigor in {"L2", "L3"}:
        cx, _ = _clamp_x(float(cmd), smin, smax, x0, bw)
        parts.append(f'<polygon points="{cx:.1f},{y_bar - 1} {cx - 5:.1f},{y_bar - 9} {cx + 5:.1f},{y_bar - 9}" fill="var(--bg-canvas)" stroke="var(--text-primary)" stroke-width="1.4"/>')
        parts.append(halo_text(cx, y_bar - 14, f"CMD\u00a0{float(cmd):g}", anchor="middle", size=11.5, weight="600", fill="var(--text-secondary)"))

    ax, ovf = _clamp_x(act, smin, smax, x0, bw)
    ann = spec.get("status_annunciator", {})
    st_code = _resolve_threshold_state(act, limits, ann, str(ann.get("state", "NOMINAL")).upper())
    pin_col = ANNUNCIATOR_STATES.get(st_code, ANNUNCIATOR_STATES["NOMINAL"])["fg"]
    parts.append(f'<polygon points="{ax:.1f},{y_bar + 2} {ax - 5.5:.1f},{y_bar + bh + 6} {ax + 5.5:.1f},{y_bar + bh + 6}" fill="{pin_col}" stroke="var(--bg-canvas)" stroke-width="1"/>')
    act_lbl = f"ACT\u00a0{format_value_unit(act, unit)}" if ovf == 0 else ("◀ CLAMPED" if ovf < 0 else "CLAMPED ▶")
    lbl_anchor = "start" if ax < 110 else ("end" if ax > 570 else "middle")
    parts.append(halo_text(ax, 88.0, act_lbl, anchor=lbl_anchor, size=11.5, weight="700", fill=pin_col))
    parts.append("</svg>")
    return "\n".join(parts)


def _render_single_scalar(spec: dict[str, Any], rigor: str, medium: str) -> str:
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
    subsys = meta.get("subsystem", "TELEMETRY")
    ts = meta.get("timestamp_utc", "")
    margin = ann.get("margin_remaining_pct")
    if st_key == "STALE":
        quality_badge = '<span class="va-stale-badge">[ STALE DATA ]</span>'
    elif st_key == "FAULT":
        quality_badge = '<span class="va-badge va-badge-err">[ SENSOR FAULT ]</span>'
    else:
        quality_badge = ""

    lines: list[str] = ['<div class="qe-scalar-card">']
    lines.append(f'<div class="qe-scalar-zone1"><span class="va-kicker">{esc(subsys)}</span><span class="qe-scalar-ts va-nums">{esc(ts)} {quality_badge}</span></div>')
    lines.append(f'<h3 class="qe-scalar-title">{esc(meta.get("title", "Scalar Readout"))}</h3>')
    lines.append('<div class="qe-scalar-zone2">')
    lines.append(f'  <div class="qe-scalar-val-wrap"><span class="qe-scalar-val va-nums">{esc(val_text)}</span><span class="qe-scalar-calc qe-unit">{format_math_html(calculus)}</span></div>')
    margin_txt = f" · Margin: {margin:+.1f}%" if (margin is not None and rigor in {"L2", "L3"}) else ""
    lines.append(f'  <span class="va-badge {disp_info["cls"]}" data-state="{esc(disp_key)}">{esc(disp_info["pill"])}{esc(margin_txt)}</span>')
    lines.append("</div>")

    if rigor == "L1" and spec.get("sparkline"):
        pts = [float(v) for v in spec["sparkline"]]
        lo, hi = min(pts), max(pts)
        span = hi - lo if hi != lo else 1.0
        coords = " ".join(f"{16 + i * (288.0 / max(len(pts) - 1, 1)):.1f},{28 - ((v - lo) / span) * 20:.1f}" for i, v in enumerate(pts))
        lines.append(f'<svg class="qe-svg qe-spark-svg" viewBox="0 0 320 34" role="img" aria-label="Trend sparkline"><polyline fill="none" stroke="{disp_info["fg"]}" stroke-width="1.8" points="{coords}"/></svg>')
    elif rigor in {"L2", "L3"} and (spec.get("gauge") or limits):
        lines.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Gauge"))}">{_render_gauge_svg(spec, rigor)}</div>')

    if rigor == "L2" and limits.get("tolerance_band"):
        tol = limits["tolerance_band"]
        tgt = limits.get("nominal_target", "")
        lines.append(f'<div class="qe-scalar-meta va-nums">Target: {esc(format_value_unit(tgt, unit))} | Tolerance Band: [{esc(tol[0])}, +{esc(tol[1])}] {esc(unit)}</div>')

    if rigor == "L3":
        k_cov = meas.get("coverage_factor", 2.0)
        conf = meas.get("confidence_pct", 95.45)
        lines.append(f'<div class="qe-scalar-meta va-nums">Expanded Uncertainty: {esc(val_text)} | k={esc(k_cov)} | {esc(conf)}% CI</div>')
        prov: list[str] = []
        if meas.get("sensor_id"):
            prov.append(f'Sensor: {meas["sensor_id"]}')
        if meas.get("calibration_id"):
            prov.append(f'Cal: {meas["calibration_id"]}')
        if meas.get("raw_adc_counts") is not None:
            prov.append(f'Raw ADC: {meas["raw_adc_counts"]} cts')
        if prov:
            lines.append(f'<div class="qe-scalar-prov va-nums">{esc(" | ".join(prov))}</div>')
    lines.append("</div>")
    return "\n".join(lines)


def compile_scalar(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white") -> str:
    """Compile Modality 1 (urn:quiet-ui:schema:v9:scalar) into semantic HTML/SVG."""
    eff_rigor = (rigor or spec.get("metadata", {}).get("rigor_level", "L2")).upper()
    items = spec.get("items")
    if isinstance(items, list) and items:
        grid = "\n".join(_render_single_scalar(it, eff_rigor, medium) for it in items)
        return f'<div class="qe-scalar-grid" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}">{grid}</div>'
    return _render_single_scalar(spec, eff_rigor, medium)


def _render_heatmap_svg(hm: dict[str, Any]) -> str:
    """Render calibrated R x C phase-excursion heatmap (v7.1 recovery)."""
    cols = hm.get("col_labels", [])
    rows = hm.get("rows", [])
    cell_w, cell_h, x0, y0 = 62.0, 24.0, 96.0, 26.0
    vb_w = int(max(620.0, x0 + len(cols) * cell_w + 24.0))
    vb_h = int(y0 + len(rows) * (cell_h + 6.0) + 18.0)
    parts: list[str] = [f'<svg class="qe-svg qe-svg-680" viewBox="0 0 {vb_w} {vb_h}" role="img" aria-label="{esc(hm.get("title", "Excursion Heatmap"))}">']
    for ci, clbl in enumerate(cols):
        cx = x0 + ci * cell_w + cell_w / 2.0
        parts.append(halo_text(cx, 16.0, str(clbl), anchor="middle", size=11.5, weight="700", fill="var(--text-secondary)", halo=False))
    status_style = {
        "ok": ("var(--status-ok-bg)", "var(--status-ok)", "1.0"),
        "warn": ("var(--status-warn-bg)", "var(--status-warn)", "1.8"),
        "err": ("var(--status-err-bg)", "var(--status-danger)", "2.0"),
    }
    for ri, row in enumerate(rows):
        ry = y0 + ri * (cell_h + 6.0)
        parts.append(halo_text(x0 - 10.0, ry + 16.0, str(row.get("label", "")), anchor="end", size=11.5, weight="600", fill="var(--text-muted)", halo=False))
        for ci, cell in enumerate(row.get("cells", [])):
            cx = x0 + ci * cell_w
            st = str(cell.get("status", "ok")).lower()
            bg, stroke, sw = status_style.get(st, status_style["ok"])
            dash = ' stroke-dasharray="4,2"' if st == "warn" else ""
            parts.append(f'<rect x="{cx + 2:.1f}" y="{ry:.1f}" width="{cell_w - 6:.1f}" height="{cell_h:.1f}" rx="3" fill="{bg}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
            val = str(cell.get("text", ""))
            if val:
                parts.append(halo_text(cx + (cell_w - 2) / 2.0, ry + 16.0, val, anchor="middle", size=11.5, weight="600", fill=stroke, halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


def _status_badge_html(val: Any) -> str:
    """Render non-color-only text status pill for table disposition cells."""
    s = str(val).upper()
    if s in {"AUTHORIZED", "NOMINAL", "ACTIVE", "PASS", "GO", "LOCKED", "VERIFIED", "APPROVED"}:
        cls = "va-badge-ok"
    elif s in {"CONDITIONAL", "CAUTION", "WARNING", "DEGRADED", "MARGINAL", "WATCH"}:
        cls = "va-badge-warn"
    elif s in {"REJECTED", "CRITICAL", "ABORT", "OFFLINE", "FAULT", "FAIL", "HOLD"}:
        cls = "va-badge-err"
    else:
        cls = "va-badge-neutral"
    return f'<span class="va-badge {cls}">{esc(val)}</span>'


def _format_col_header_html(c: dict[str, Any]) -> str:
    """Wrap NIST/SI units and quantity symbols in <span class='qe-unit'> to prevent uppercase corruption."""
    qc = c.get("quantity_calculus")
    if qc:
        return f'<span class="qe-unit">{format_math_html(qc)}</span>'
    lbl = str(c.get("label", c.get("key", "")))
    unit = str(c.get("unit", "")).strip()
    if unit and unit != "1":
        if unit not in lbl:
            return f'{esc(lbl)} (<span class="qe-unit">{esc(unit)}</span>)'
        return esc(lbl).replace(esc(unit), f'<span class="qe-unit">{esc(unit)}</span>', 1)
    return esc(lbl)


def compile_table(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white") -> str:
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
