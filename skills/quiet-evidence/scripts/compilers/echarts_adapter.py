# SPDX-License-Identifier: Apache-2.0
"""Apache ECharts & Multi-Ecosystem Serialization Adapter for Quiet Evidence."""

from __future__ import annotations

import math
import re
from typing import Any

from .echarts_snippets import render_ecosystem_drawer_from_payload
from .plot_helpers import (
    axis_scale,
    build_corridor_band,
    clip_curve_to_y,
    compute_normalized_residuals,
    round_coord,
    sample_model_points,
    visible_series,
)
from .sankey_and_strip import build_sankey_echarts_payload, build_strip_chart_echarts_payload
from .tokens_and_scales import compute_linear_125_scale, finite_float

_MATH_SUBS: tuple[tuple[str, str], ...] = (
    (", B_cap", ""), ("B_cap", "B"), ("L_ratio", "L"), ("eta_bte", "\u03b7"), ("f_obs", "f\u2092\u1d66\u209b"),
    ("p_hat", "p\u0302"), ("y_hat", "y\u0302"), ("X_bar", "X\u0304"), ("sigma_y", "\u03c3\u1d67"), ("C_pk", "C\u209a\u2096"),
    ("P_load", "Home Load"), ("P_grid", "Net Grid"), ("P_pv", "Solar Power"), ("P_rx", "P\u1d63\u2093"),
    ("V_0", "V\u2080"), ("f_0", "f\u2080"), ("V_c", "V"), ("t_rms", "t\u1d63\u2098\u209b"), ("R_net", "R\u2099\u2091\u209c"),
    ("alpha_fiber", "\u03b1"), ("tau_s", "\u03c4"), ("D^3", "D\u00b3"), ("+/-", "\u00b1"), ("u_y", "u"),
)
_WORD_TAU_RE = re.compile(r"\btau\b")
_SIGMA_WORD_RE = re.compile(r"\bsigma\b")


def _sample_analytical_series(spec: dict[str, Any], s: dict[str, Any], x_min: float, x_max: float, log_x: bool) -> list[list[float]]:
    pts = sample_model_points(s, {"min": x_min, "max": x_max, "is_log": log_x}, n=37, legend=spec.get("parametric_legend"))
    return [[round_coord(xv), round_coord(yv)] for xv, yv in pts]


def _extract_token(color: Any, fallback: str = "--accent-focal") -> str:
    txt = str(color or "")
    if "var(" in txt:
        inner = txt.split("var(", 1)[1].split(")", 1)[0].split(",")[0].strip()
        return inner or fallback
    return txt.strip() if txt.strip().startswith("#") else fallback


def _plain_text(val: Any) -> str:
    txt = str(val or "")
    for pat, sub in _MATH_SUBS:
        txt = txt.replace(pat, sub)
    txt = _WORD_TAU_RE.sub("\u03c4", txt)
    txt = _SIGMA_WORD_RE.sub("\u03c3", txt)
    return txt


def _build_waterfall_payload(spec: dict[str, Any], rigor: str, medium: str) -> dict[str, Any]:
    cats, bases, totals, pos_vals, neg_vals, kinds, signed_vals, spans, bounds = [], [], [], [], [], [], [], [], [0.0]
    running = 0.0
    ya = (spec.get("axes") or {}).get("y_axis") or {}
    for step in spec.get("steps", []):
        cats.append(_plain_text(step.get("label") or ""))
        val = float(step.get("delta") if "delta" in step else step.get("value", 0.0))
        step_kind = str(step.get("kind") or ("total" if step.get("is_total") else "delta")).lower()
        kinds.append(step_kind)
        if step_kind in {"start", "total"}:
            if step_kind == "total" and ("value" in step or "delta" in step) and abs(val - running) > 1e-4:
                raise ValueError(f"Waterfall conservation violated at '{step.get('label')}': expected {running:.4f}, got {val:.4f}")
            running = val if ("value" in step or step_kind == "start") else running
            lo, hi = min(0.0, running), max(0.0, running)
            bases.append(0.0)
            totals.append(round(running, 4))
            pos_vals.append("-")
            neg_vals.append("-")
            signed_vals.append(round(running, 4))
            spans.append([round(lo, 4), round(hi, 4), round(running, 4), step_kind])
            bounds.extend((lo, hi))
        elif val >= 0:
            nxt = running + val
            bases.append(round(running, 4))
            totals.append("-")
            pos_vals.append(round(val, 4))
            neg_vals.append("-")
            signed_vals.append(round(val, 4))
            spans.append([round(running, 4), round(nxt, 4), round(val, 4), "inc"])
            bounds.extend((running, nxt))
            running = nxt
        else:
            nxt = running + val
            bases.append(round(nxt, 4))
            totals.append("-")
            pos_vals.append("-")
            neg_vals.append(round(abs(val), 4))
            signed_vals.append(round(val, 4))
            spans.append([round(nxt, 4), round(running, 4), round(val, 4), "dec"])
            bounds.extend((nxt, running))
            running = nxt
    envs = spec.get("envelopes") or [] if (rigor in {"L2", "L3"} or spec.get("show_l1_envelopes")) else []
    env_out = [
        {
            "label": _plain_text(e.get("label") or ""),
            "value": float(e["threshold_value"]),
            "type": str(e.get("type") or "abort"),
            "direction": str(e.get("direction") or "lower"),
            "token": _extract_token(e.get("stroke_color"), "--status-warn" if e.get("type") == "warning" else "--status-danger"),
        }
        for e in envs if e.get("threshold_value") is not None and math.isfinite(float(e["threshold_value"]))
    ]
    bounds.extend(e["value"] for e in env_out)
    lo_b, hi_b = min(bounds), max(bounds)
    sc = compute_linear_125_scale(lo_b * (1.12 if lo_b < 0 else 1.0), hi_b * (1.12 if hi_b > 0 else 1.0), target_ticks=5)
    return {
        "kind": "waterfall",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "Waterfall Budget"),
        "rigor": rigor,
        "medium": medium,
        "unit": str(ya.get("unit") or ""),
        "yName": _plain_text(ya.get("quantity_calculus") or "Value"),
        "y": {"name": _plain_text(ya.get("quantity_calculus") or "Value"), "min": sc["min"], "max": sc["max"], "interval": sc["step"]},
        "categories": cats,
        "stepKinds": kinds,
        "signedValues": signed_vals,
        "spans": spans,
        "bases": bases,
        "totals": totals,
        "positive": pos_vals,
        "negative": neg_vals,
        "envelopes": env_out,
    }


def _build_stacked_bar_payload(spec: dict[str, Any], rigor: str, medium: str) -> dict[str, Any] | None:
    series_list = spec.get("series") or []
    if not series_list:
        return None
    axes = spec.get("axes") or {}
    xa, ya = axes.get("x_axis") or {}, axes.get("y_axis") or {}
    raw_cats = xa.get("categories") or []
    n_pts = max((len(s.get("data_points") or []) for s in series_list), default=1)
    cats = [str(c) for c in raw_cats] if len(raw_cats) == n_pts and n_pts > 0 else [f"{i:02d}:00" for i in range(max(n_pts, 1))]
    pos_sum, neg_sum = [0.0] * len(cats), [0.0] * len(cats)
    all_y: list[float] = []
    series_out: list[dict[str, Any]] = []
    for s in series_list:
        stype = str(s.get("series_type") or "bar").lower()
        pts = [float(p.get("y") or 0.0) if math.isfinite(float(p.get("y") or 0.0)) else 0.0 for p in (s.get("data_points") or [])]
        if stype == "line":
            all_y.extend(pts)
        else:
            for idx, v in enumerate(pts):
                if idx < len(cats):
                    pos_sum[idx] += max(0.0, v)
                    neg_sum[idx] += min(0.0, v)
        series_out.append({
            "id": str(s.get("id") or "series"),
            "name": _plain_text(s.get("name") or "Series"),
            "seriesType": stype,
            "stack": str(s.get("stack") or "energy"),
            "color": _extract_token(s.get("marker_color") or s.get("stroke_color"), "--accent-focal"),
            "data": pts,
        })
    y_sc = axis_scale(ya, all_y + pos_sum + neg_sum)
    env_out = [
        {"label": _plain_text(e.get("label") or ""), "value": float(e["threshold_value"]), "type": str(e.get("type") or "reference"), "token": _extract_token(e.get("stroke_color"), "--text-secondary")}
        for e in spec.get("envelopes", [])
        if e.get("threshold_value") is not None and math.isfinite(float(e["threshold_value"]))
    ]
    return {
        "kind": "stacked_bar",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "Stacked Energy Flow"),
        "rigor": rigor,
        "medium": medium,
        "categories": cats,
        "x": {"name": _plain_text(xa.get("quantity_calculus") or "Hour")},
        "y": {"name": _plain_text(ya.get("quantity_calculus") or "Value"), "min": y_sc["min"], "max": y_sc["max"], "interval": y_sc.get("step")},
        "series": series_out,
        "envelopes": env_out,
    }


def _build_gantt_payload(spec: dict[str, Any], rigor: str, medium: str) -> dict[str, Any] | None:
    tasks_raw = spec.get("tasks") or []
    if not tasks_raw:
        return None
    xa = (spec.get("axes") or {}).get("x_axis") or {}
    unit = str(xa.get("unit") or ("h" if "Hour" in str(xa.get("quantity_calculus") or "") else "d"))
    vals: list[float] = [float(t.get("start", 0.0)) for t in tasks_raw] + [float(t.get("end", 0.0)) + max(0.0, float(t.get("float_days") or t.get("float_hours") or 0.0)) for t in tasks_raw]
    if spec.get("today_day") is not None:
        vals.append(float(spec["today_day"]))
    x_sc = axis_scale(xa, vals)
    tasks_out = [
        {
            "id": str(t.get("id") or f"t{i}"),
            "label": _plain_text(t.get("label") or f"Task {i + 1}"),
            "phase": _plain_text(t.get("phase") or "Execution"),
            "start": float(t.get("start", 0.0)),
            "end": float(t.get("end", t.get("start", 0.0))),
            "float": max(0.0, float(t.get("float_days") or t.get("float_hours") or 0.0)),
            "critical": bool(t.get("critical", False)),
            "milestone": bool(t.get("milestone", False)),
            "dependsOn": [str(d) for d in (t.get("depends_on") or [])],
            "owner": _plain_text(t.get("owner") or ""),
        }
        for i, t in enumerate(tasks_raw)
    ]
    return {
        "kind": "gantt",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "Schedule Gantt"),
        "rigor": rigor,
        "medium": medium,
        "unit": unit,
        "x": {"name": _plain_text(xa.get("quantity_calculus") or f"Schedule, t / {unit}"), "min": x_sc["min"], "max": x_sc["max"], "interval": x_sc.get("step")},
        "y": {"name": "Workstream / Task"},
        "todayMarker": float(spec["today_day"]) if spec.get("today_day") is not None else None,
        "todayLabel": _plain_text(spec.get("today_label") or "") or None,
        "tasks": tasks_out,
    }

def _build_heatmap_payload(spec: dict[str, Any], rigor: str, medium: str) -> dict[str, Any] | None:
    x_cats = [_plain_text(c) for c in (spec.get("x_categories") or [])]
    y_cats = [_plain_text(c) for c in (spec.get("y_categories") or [])]
    matrix = spec.get("matrix") or []
    if not x_cats or not y_cats or not matrix:
        return None
    vals: list[float] = []
    cells: list[list[Any]] = []
    n_y = len(y_cats)
    for ri, row in enumerate(matrix[:n_y]):
        yi = n_y - 1 - ri
        for ci, raw_v in enumerate(row[:len(x_cats)]):
            if raw_v is not None and math.isfinite(float(raw_v)):
                fv = float(raw_v)
                vals.append(fv)
                cells.append([ci, yi, round(fv, 3)])
    dom = (spec.get("scale") or {}).get("domain")
    v_min = float(dom[0]) if isinstance(dom, (list, tuple)) and len(dom) == 2 else min(vals or [0.0])
    v_max = float(dom[1]) if isinstance(dom, (list, tuple)) and len(dom) == 2 else max(vals or [100.0])
    z_sc = compute_linear_125_scale(v_min, v_max if v_max > v_min else v_min + 1.0, target_ticks=5)
    z_lbl = _plain_text((spec.get("scale") or {}).get("quantity_calculus") or "Intensity / %")
    return {
        "kind": "heatmap",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "2D Matrix Heatmap"),
        "rigor": rigor,
        "medium": medium,
        "x": {"name": _plain_text(((spec.get("axes") or {}).get("x_axis") or {}).get("quantity_calculus") or "Dimension X")},
        "y": {"name": _plain_text(((spec.get("axes") or {}).get("y_axis") or {}).get("quantity_calculus") or "Dimension Y")},
        "xCategories": x_cats,
        "yCategories": list(reversed(y_cats)),
        "cells": cells,
        "min": z_sc["min"],
        "max": z_sc["max"],
        "unit": str((spec.get("scale") or {}).get("unit") or ""),
        "quantityLabel": z_lbl,
    }


def _build_dumbbell_payload(spec: dict[str, Any], rigor: str, medium: str) -> dict[str, Any] | None:
    items = spec.get("dumbbells") or []
    if not items:
        return None
    ya = (spec.get("axes") or {}).get("y_axis") or {}
    xa = (spec.get("axes") or {}).get("x_axis") or {}
    vals = [float(it["before"]) for it in items] + [float(it["after"]) for it in items]
    dom = ya.get("domain") or xa.get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) == 2:
        lo_d, hi_d = float(dom[0]), float(dom[1])
    else:
        lo_r, hi_r = min(vals), max(vals)
        sp = (hi_r - lo_r) or abs(hi_r) or 1.0
        lo_d = 0.0 if (0.0 < lo_r <= hi_r * 0.25) else (lo_r - sp * 0.15)
        hi_d = hi_r + sp * 0.15
    y_sc = compute_linear_125_scale(lo_d, hi_d, target_ticks=5)
    lbls = spec.get("series_labels") or ["Baseline", "After"]
    return {
        "kind": "dumbbell",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "Before vs After Comparison"),
        "rigor": rigor,
        "medium": medium,
        "unit": str(ya.get("unit") or ""),
        "x": {"name": _plain_text(xa.get("quantity_calculus") or "Segment")},
        "y": {"name": _plain_text(ya.get("quantity_calculus") or "Metric"), "min": y_sc["min"], "max": y_sc["max"], "interval": y_sc["step"]},
        "beforeLabel": _plain_text(lbls[0] if len(lbls) > 0 else "Baseline"),
        "afterLabel": _plain_text(lbls[1] if len(lbls) > 1 else "After"),
        "categories": [_plain_text(it["label"]) for it in items],
        "items": [{"label": _plain_text(it["label"]), "before": float(it["before"]), "after": float(it["after"])} for it in items],
    }


def _build_forest_payload(spec: dict[str, Any], rigor: str, medium: str) -> dict[str, Any] | None:
    items = spec.get("items") or spec.get("subgroups") or []
    if not items:
        return None
    xa = (spec.get("axes") or {}).get("x_axis") or {}
    null_v = float(spec.get("null_value", 1.0))
    vals = [null_v] + [float(v) for it in items for v in (it["ci_low"], it["estimate"], it["ci_high"])]
    dom = xa.get("domain")
    x_sc = compute_linear_125_scale(float(dom[0]) if dom else min(vals), float(dom[1]) if dom else max(vals), target_ticks=5)
    rev_items = list(reversed(items))
    return {
        "kind": "forest",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "Subgroup Confidence Forest"),
        "rigor": rigor,
        "medium": medium,
        "nullValue": null_v,
        "x": {"name": _plain_text(xa.get("quantity_calculus") or "Effect (95% CI)"), "min": x_sc["min"], "max": x_sc["max"], "interval": x_sc["step"]},
        "y": {"name": "Subgroup"},
        "categories": [_plain_text(it["label"]) for it in rev_items],
        "items": [
            {
                "label": _plain_text(it["label"]),
                "estimate": float(it["estimate"]),
                "ciLow": float(it["ci_low"]),
                "ciHigh": float(it["ci_high"]),
                "pooled": bool(it.get("pooled") or it.get("kind") == "pooled"),
                "sig": float(it["ci_high"]) < null_v or float(it["ci_low"]) > null_v,
            }
            for it in rev_items
        ],
    }


def build_echarts_payload(spec: dict[str, Any], rigor: str = "L3", medium: str = "m2") -> dict[str, Any] | None:
    """Build deterministic semantic ECharts descriptor matching plot_compiler domain scaling."""
    kind = str(spec.get("plot_kind") or spec.get("waveform_kind") or "cartesian")
    builders = {
        "waterfall": _build_waterfall_payload, "stacked_bar": _build_stacked_bar_payload,
        "gantt": _build_gantt_payload, "heatmap": _build_heatmap_payload,
        "dumbbell": _build_dumbbell_payload, "forest": _build_forest_payload,
        "sankey": build_sankey_echarts_payload, "strip_chart": build_strip_chart_echarts_payload,
    }
    if kind in builders:
        return builders[kind](spec, rigor, medium)
    if kind != "cartesian":
        return None
    axes = spec.get("axes") or {}
    xa, ya = axes.get("x_axis") or {}, axes.get("y_axis") or {}
    log_x = str(xa.get("scale_type") or "").lower() in {"log", "logarithmic"}
    log_y = str(ya.get("scale_type") or "").lower() in {"log", "logarithmic"}
    x_dom, y_dom = xa.get("domain"), ya.get("domain")
    x_vals: list[float] = [v for v in (finite_float(x_dom[0]), finite_float(x_dom[1])) if v is not None] if isinstance(x_dom, (list, tuple)) and len(x_dom) >= 2 else []
    y_vals: list[float] = [v for v in (finite_float(y_dom[0]), finite_float(y_dom[1])) if v is not None] if isinstance(y_dom, (list, tuple)) and len(y_dom) >= 2 else []
    raw_series = visible_series(spec, rigor)
    show_u = rigor in {"L2", "L3"}
    for s in raw_series:
        if str(s.get("epistemic_type") or "discrete_measurement") != "analytical_model":
            for p in (s.get("data_points") or s.get("points") or []):
                fx, fy, fu = finite_float(p.get("x")), finite_float(p.get("y")), finite_float(p.get("u_y"))
                if fx is not None:
                    x_vals.append(fx)
                if fy is not None:
                    y_vals.append(fy)
                    if show_u and fu is not None:
                        uv = abs(fu)
                        y_vals.extend((fy + uv, max(fy - uv, 1e-12) if log_y else (fy - uv)))
    x_sc = axis_scale(xa, x_vals)
    x_min, x_max = float(x_sc["min"]), float(x_sc["max"])
    series_out: list[dict[str, Any]] = []
    analyt_specs: list[tuple[int, dict[str, Any]]] = []
    for s in raw_series:
        stype = str(s.get("epistemic_type") or "discrete_measurement")
        raw_col = s.get("marker_color") or s.get("stroke_color")
        tok = _extract_token(raw_col, "--accent-focal")
        col_exp = bool(raw_col)
        if stype == "analytical_model":
            pts = _sample_analytical_series(spec, s, x_min, x_max, log_x)
            if not pts:
                continue
            analyt_specs.append((len(series_out), s))
            series_out.append({"id": str(s.get("id") or "model"), "name": _plain_text(s.get("name") or "Model"), "epistemic": "analytical_model", "term": str(s.get("term") or s.get("id") or ""), "token": tok, "colorExplicit": col_exp, "dashed": str(s.get("stroke_style") or "dashed") != "solid", "data": pts})
            if not y_dom:
                y_vals.extend(p[1] for p in pts)
        else:
            pts_err = [
                [float(p["x"]), None if (p.get("y") is None or not math.isfinite(float(p["y"]))) else float(p["y"]), float(p["u_y"]) if (show_u and p.get("u_y") is not None and math.isfinite(float(p["u_y"]))) else 0.0]
                for p in (s.get("data_points") or s.get("points") or [])
                if p.get("x") is not None and math.isfinite(float(p["x"]))
            ]
            series_out.append({"id": str(s.get("id") or "meas"), "name": _plain_text(s.get("name") or "Measurement"), "epistemic": "discrete_measurement", "term": str(s.get("term") or s.get("id") or ""), "token": tok, "colorExplicit": col_exp, "connectPiecewise": bool(s.get("connect_piecewise", False)), "symbol": str(s.get("marker_glyph") or "circle"), "data": pts_err})
    if not series_out:
        return None
    envs_raw = spec.get("envelopes") or [] if (rigor in {"L2", "L3"} or spec.get("show_l1_envelopes")) else []
    if not y_dom:
        y_vals.extend(float(e["threshold_value"]) for e in envs_raw if e.get("threshold_value") is not None and math.isfinite(float(e["threshold_value"])))
    y_sc = axis_scale(ya, y_vals)
    y_lo, y_hi = float(y_sc["min"]), float(y_sc["max"])
    if rigor in {"L2", "L3"}:
        for s_idx, s_raw in analyt_specs:
            band = build_corridor_band(series_out[s_idx]["data"], s_raw, y_lo, y_hi)
            if band:
                series_out[s_idx]["corridor"] = band
    env_out: list[dict[str, Any]] = []
    for e in envs_raw:
        etyp = str(e.get("type") or "warning")
        etok = _extract_token(e.get("stroke_color"), "--status-warn" if etyp != "abort" else "--status-danger")
        edef = {"label": _plain_text(e.get("label") or ""), "type": etyp, "direction": str(e.get("direction") or "upper"), "token": etok}
        if e.get("equation"):
            cpts = clip_curve_to_y(_sample_analytical_series(spec, {"equation": e["equation"]}, x_min, x_max, log_x), y_lo, y_hi, log_x=log_x, log_y=log_y)
            if len(cpts) >= 2:
                env_out.append({**edef, "points": cpts, "strokeStyle": str(e.get("stroke_style") or "dashed")})
        elif e.get("threshold_value") is not None and math.isfinite(float(e["threshold_value"])):
            env_out.append({**edef, "value": float(e["threshold_value"])})
    out: dict[str, Any] = {
        "kind": "cartesian", "title": _plain_text((spec.get("metadata") or {}).get("title") or "Analytical Plot"),
        "rigor": rigor, "medium": medium, "series": series_out, "envelopes": env_out,
        "x": {"name": _plain_text(xa.get("quantity_calculus") or xa.get("quantity") or "x"), "min": x_sc["min"], "max": x_sc["max"], "interval": x_sc.get("step"), "log": log_x},
        "y": {"name": _plain_text(ya.get("quantity_calculus") or ya.get("quantity") or "y"), "min": y_sc["min"], "max": y_sc["max"], "interval": y_sc.get("step"), "log": log_y},
    }
    if bool((spec.get("residual_strip") or {}).get("enabled")) and rigor == "L3":
        r_pts = compute_normalized_residuals(raw_series, log_x=log_x, legend=spec.get("parametric_legend"))
        if r_pts:
            out["residuals"] = {"label": "Normalized Residuals (y\u1d62 \u2212 y\u0302\u1d62) / u", "bound": 2.0, "points": [[round_coord(xv), round(rv, 3)] for xv, rv in r_pts]}
    return out

def render_echarts_toggle_bar() -> str:
    """Render accessible [Quiet SVG | Live ECharts] bench mode toggle."""
    return (
        '<div class="qe-plot-modebar" role="group" aria-label="Plot rendering backend">'
        '<span class="qe-modebar-label">Renderer</span>'
        '<button type="button" class="qe-mode-btn is-active" data-qe-mode="svg" aria-pressed="true">Quiet SVG</button>'
        '<button type="button" class="qe-mode-btn" data-qe-mode="echarts" aria-pressed="false">Live ECharts</button></div>'
    )

def render_ecosystem_drawer(spec: dict[str, Any]) -> str:
    """Render full-width 5-tab ecosystem code viewer with Copy Snippet button."""
    payload = build_echarts_payload(spec, rigor=str((spec.get("metadata") or {}).get("rigor_level", "L3")))
    return render_ecosystem_drawer_from_payload(spec, payload)
