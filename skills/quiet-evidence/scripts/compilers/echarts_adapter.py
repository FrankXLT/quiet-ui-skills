# SPDX-License-Identifier: Apache-2.0
"""Apache ECharts & Multi-Ecosystem Serialization Adapter for Quiet Evidence."""

from __future__ import annotations

import json
import math
import re
from typing import Any

from .plot_helpers import (
    axis_scale,
    build_corridor_band,
    clip_curve_to_y,
    compute_normalized_residuals,
    round_coord,
    sample_model_points,
    visible_series,
)
from .tokens_and_scales import compute_linear_125_scale, esc

_MATH_SUBS: tuple[tuple[str, str], ...] = (
    (", B_cap", ""),
    ("B_cap", "B"),
    ("L_ratio", "L"),
    ("eta_bte", "\u03b7"),
    ("f_obs", "f\u2092\u1d66\u209b"),
    ("p_hat", "p\u0302"),
    ("y_hat", "y\u0302"),
    ("X_bar", "X\u0304"),
    ("sigma_y", "\u03c3\u1d67"),
    ("C_pk", "C\u209a\u2096"),
    ("P_load", "Home Load"),
    ("P_grid", "Net Grid"),
    ("P_pv", "Solar Power"),
    ("P_rx", "P\u1d63\u2093"),
    ("V_0", "V\u2080"),
    ("f_0", "f\u2080"),
    ("V_c", "V"),
    ("t_rms", "t\u1d63\u2098\u209b"),
    ("R_net", "R\u2099\u2091\u209c"),
    ("alpha_fiber", "\u03b1"),
    ("tau_s", "\u03c4"),
    ("D^3", "D\u00b3"),
    ("+/-", "\u00b1"),
    ("u_y", "u"),
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


def build_echarts_payload(spec: dict[str, Any], rigor: str = "L3", medium: str = "m2") -> dict[str, Any] | None:
    """Build deterministic semantic ECharts descriptor matching plot_compiler domain scaling."""
    kind = str(spec.get("plot_kind") or "cartesian")
    if kind == "waterfall":
        return _build_waterfall_payload(spec, rigor, medium)
    if kind == "stacked_bar":
        return _build_stacked_bar_payload(spec, rigor, medium)
    if kind != "cartesian":
        return None
    axes = spec.get("axes") or {}
    xa, ya = axes.get("x_axis") or {}, axes.get("y_axis") or {}
    log_x = str(xa.get("scale_type") or "").lower() in {"log", "logarithmic"}
    log_y = str(ya.get("scale_type") or "").lower() in {"log", "logarithmic"}
    x_dom, y_dom = xa.get("domain"), ya.get("domain")
    x_vals: list[float] = [float(x_dom[0]), float(x_dom[1])] if x_dom else []
    y_vals: list[float] = [float(y_dom[0]), float(y_dom[1])] if y_dom else []
    raw_series = visible_series(spec, rigor)
    show_u = rigor in {"L2", "L3"}
    for s in raw_series:
        if str(s.get("epistemic_type") or "discrete_measurement") != "analytical_model":
            for p in (s.get("data_points") or s.get("points") or []):
                x_vals.append(float(p["x"]))
                if p.get("y") is not None:
                    yv = float(p["y"])
                    y_vals.append(yv)
                    raw_u = p.get("u_y")
                    if show_u and raw_u is not None and math.isfinite(float(raw_u)):
                        uv = abs(float(raw_u))
                        y_vals.extend((yv + uv, max(yv - uv, 1e-12) if log_y else (yv - uv)))
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
            pts_err = [[float(p["x"]), None if p.get("y") is None else float(p["y"]), float(p.get("u_y") or 0.0) if show_u else 0.0] for p in (s.get("data_points") or s.get("points") or [])]
            series_out.append({"id": str(s.get("id") or "meas"), "name": _plain_text(s.get("name") or "Measurement"), "epistemic": "discrete_measurement", "term": str(s.get("term") or s.get("id") or ""), "token": tok, "colorExplicit": col_exp, "connectPiecewise": bool(s.get("connect_piecewise", False)), "symbol": str(s.get("marker_glyph") or "circle"), "data": pts_err})
    if not series_out:
        return None
    envs_raw = spec.get("envelopes") or [] if (rigor in {"L2", "L3"} or spec.get("show_l1_envelopes")) else []
    if not y_dom:
        y_vals.extend(float(e["threshold_value"]) for e in envs_raw if "threshold_value" in e and math.isfinite(float(e["threshold_value"])))
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
        elif "threshold_value" in e and math.isfinite(float(e["threshold_value"])):
            env_out.append({**edef, "value": float(e["threshold_value"])})
    out: dict[str, Any] = {
        "kind": "cartesian",
        "title": _plain_text((spec.get("metadata") or {}).get("title") or "Analytical Plot"),
        "rigor": rigor,
        "medium": medium,
        "x": {"name": _plain_text(xa.get("quantity_calculus") or xa.get("quantity") or "x"), "min": x_sc["min"], "max": x_sc["max"], "interval": x_sc.get("step"), "log": log_x},
        "y": {"name": _plain_text(ya.get("quantity_calculus") or ya.get("quantity") or "y"), "min": y_sc["min"], "max": y_sc["max"], "interval": y_sc.get("step"), "log": log_y},
        "series": series_out,
        "envelopes": env_out,
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
        '<button type="button" class="qe-mode-btn" data-qe-mode="echarts" aria-pressed="false">Live ECharts</button>'
        '</div>'
    )


def _eco_snippets(payload: dict[str, Any]) -> list[tuple[str, str, str]]:
    kind = payload["kind"]
    x_lbl = str(payload.get("x", {}).get("name") or "Category")
    y_lbl = str(payload.get("y", {}).get("name") or payload.get("yName") or "Value")
    echarts_cfg = json.dumps({
        "renderer": "svg",
        "xAxis": {"name": x_lbl, "type": "log" if payload.get("x", {}).get("log") else ("category" if kind in {"waterfall", "stacked_bar"} else "value")},
        "yAxis": {"name": y_lbl, "type": "log" if payload.get("y", {}).get("log") else "value", "min": payload.get("y", {}).get("min"), "max": payload.get("y", {}).get("max"), "interval": payload.get("y", {}).get("interval")},
        "markLine": [{"yAxis": e["value"], "name": e["label"]} for e in payload.get("envelopes", []) if "value" in e],
    }, indent=2, ensure_ascii=False)
    if kind == "stacked_bar":
        plotly = f"for s in stack_series:\n    fig.add_bar(x=hours, y=s['data'], name=s['name'])\nfig.update_layout(barmode='relative', template='plotly_white', yaxis_title='{y_lbl}')"
        mpl = f"ax.bar(hours, solar, label='Solar'); ax.bar(hours, export, label='Export')\nax.spines[['top', 'right']].set_visible(False)\nax.set(xlabel='{x_lbl}', ylabel='{y_lbl}')"
        bokeh = f"p = figure(x_range=hours, y_axis_label='{y_lbl}', toolbar_location=None)\np.vbar_stack(['solar', 'grid', 'batt'], x='hour', width=0.7, source=src)"
        mermaid = f"xychart-beta\n    title \"{payload.get('title', 'Energy')}\"\n    x-axis [\"00:00\", \"06:00\", \"12:00\", \"14:00\", \"18:00\", \"23:00\"]\n    y-axis \"{y_lbl}\" {payload['y']['min']} --> {payload['y']['max']}\n    bar [0, 0.28, 4.94, 5.10, 1.12, 0]"
    else:
        plotly = f"fig.add_trace(go.Scatter(x=x, y=y, mode='markers+lines', error_y=dict(type='data', array=u_y)))\nfig.update_layout(template='plotly_white', xaxis_title='{x_lbl}', yaxis_title='{y_lbl}')"
        mpl = f"ax.errorbar(x, y, yerr=u_y, fmt='o-', capsize=3, elinewidth=1.2)\nax.spines[['top', 'right']].set_visible(False)\nax.set(xlabel='{x_lbl}', ylabel='{y_lbl}')"
        bokeh = f"p = figure(x_axis_label='{x_lbl}', y_axis_label='{y_lbl}', toolbar_location=None)\np.line(x, y, line_width=2); p.add_layout(Whisker(base='x', upper='hi', lower='lo', source=src))"
        mermaid = f"xychart-beta\n    title \"{payload.get('title', 'Plot')}\"\n    y-axis \"{y_lbl}\"\n    line [0, 25, 50, 75, 100]"
    return [
        ("echarts", "Apache ECharts", echarts_cfg),
        ("plotly", "Plotly (Python)", plotly),
        ("matplotlib", "Matplotlib", mpl),
        ("bokeh", "Bokeh", bokeh),
        ("mermaid", "Mermaid", mermaid),
    ]


def render_ecosystem_drawer(spec: dict[str, Any]) -> str:
    """Render full-width 5-tab ecosystem code viewer with Copy Snippet button."""
    payload = build_echarts_payload(spec, rigor=str((spec.get("metadata") or {}).get("rigor_level", "L3")))
    if payload is None:
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", str(spec.get("id") or "plot").lower()).strip("-") or "plot"
    uid = f"qe-eco-{slug}"
    tabs: list[str] = []
    panels: list[str] = []
    for idx, (key, label, code) in enumerate(_eco_snippets(payload)):
        sel = "true" if idx == 0 else "false"
        t_idx = "0" if idx == 0 else "-1"
        hid = "" if idx == 0 else ' hidden="until-found"'
        tid, pid = f"{uid}-tab-{key}", f"{uid}-panel-{key}"
        tabs.append(
            f'<button type="button" class="qe-eco-tab" role="tab" id="{tid}" aria-controls="{pid}" '
            f'aria-selected="{sel}" tabindex="{t_idx}">{esc(label)}</button>'
        )
        panels.append(
            f'<div class="qe-eco-panel" role="tabpanel" id="{pid}" aria-labelledby="{tid}"{hid}>'
            f'<pre class="qe-eco-pre" tabindex="0"><code>{esc(code)}</code></pre></div>'
        )
    return (
        f'<details class="qe-eco-drawer" data-eco-root="{uid}">'
        '<summary class="qe-eco-summary">Inspect Ecosystem Config (ECharts · Plotly · Matplotlib · Bokeh · Mermaid)</summary>'
        '<div class="qe-eco-tabs-wrap">'
        '<div class="qe-eco-bar">'
        '<div class="qe-eco-tablist" role="tablist" aria-label="Plotting Ecosystem Formats">'
        f'{"".join(tabs)}</div>'
        '<div class="qe-eco-copy-wrap">'
        '<button type="button" class="qe-copy-btn" aria-label="Copy active ecosystem code snippet">Copy Snippet</button>'
        '<span class="qe-copy-status" role="status" aria-live="polite"></span>'
        '</div></div>'
        f'<div class="qe-eco-panels">{"".join(panels)}</div>'
        '</div></details>'
    )
