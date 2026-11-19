# SPDX-License-Identifier: Apache-2.0
"""Apache ECharts & Multi-Ecosystem Serialization Adapter for Quiet Evidence."""

from __future__ import annotations

import json
import math
from typing import Any

from .math_eval import eval_equation
from .tokens_and_scales import esc


def _sample_analytical_series(spec: dict[str, Any], s: dict[str, Any], x_min: float, x_max: float, log_x: bool) -> list[list[float]]:
    pts_raw = s.get("data_points") or s.get("points")
    if pts_raw:
        return [[float(p["x"]), float(p["y"])] for p in pts_raw if p.get("y") is not None]
    eq = str(s.get("equation") or "").strip()
    if not eq:
        return []
    eq_rhs = eq.split("=")[-1].strip()
    env_base: dict[str, float] = {}
    for p in spec.get("parametric_legend", []):
        sym = str(p.get("symbol") or "").strip()
        val = p.get("value")
        if sym.isidentifier() and isinstance(val, (int, float)) and not isinstance(val, bool):
            env_base[sym] = float(val)
    for k, v in (s.get("params") or {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            env_base[str(k)] = float(v)
    out: list[list[float]] = []
    steps = 36
    for i in range(steps + 1):
        t = i / steps
        if log_x and x_min > 0 and x_max > x_min:
            xv = x_min * ((x_max / x_min) ** t)
        else:
            xv = x_min + (x_max - x_min) * t
        env = dict(env_base)
        for alias in ("x", "tau", "f", "t", "IMEP", "L", "N"):
            env.setdefault(alias, xv)
        env["x"] = xv
        try:
            yv = eval_equation(eq_rhs, **env)
            if math.isfinite(yv):
                out.append([round(xv, 10) if abs(xv) < 1e-3 else round(xv, 5), round(yv, 15) if abs(yv) < 1e-3 else round(yv, 5)])
        except Exception:
            continue
    return out


def _extract_token(color: Any, fallback: str = "--accent-focal") -> str:
    txt = str(color or "")
    if "var(" in txt:
        inner = txt.split("var(", 1)[1].split(")", 1)[0].split(",")[0].strip()
        return inner or fallback
    return fallback


def _plain_text(val: Any) -> str:
    txt = str(val or "")
    for pat, sub in (
        ("p_hat", "p\u0302"),
        ("f_obs", "f(obs)"),
        ("eta_bte", "\u03b7(bte)"),
        ("P_pv", "P(pv)"),
        ("P_load", "P(load)"),
        ("P_grid", "P(grid)"),
        ("P_rx", "P(rx)"),
        ("tau_s", "\u03c4"),
        ("+/-", "\u00b1"),
        ("u_y", "u"),
    ):
        txt = txt.replace(pat, sub)
    return txt


def build_echarts_payload(spec: dict[str, Any], rigor: str = "L3", medium: str = "m2") -> dict[str, Any] | None:
    """Build deterministic semantic ECharts descriptor (tokens resolved at runtime)."""
    kind = str(spec.get("plot_kind") or "cartesian")
    meta = spec.get("metadata") or {}
    if kind == "waterfall":
        cats: list[str] = []
        bases: list[float] = []
        pos_vals: list[float | str] = []
        neg_vals: list[float | str] = []
        running = 0.0
        for step in spec.get("steps", []):
            cats.append(_plain_text(step.get("label") or ""))
            val = float(step.get("delta") if "delta" in step else step.get("value", 0.0))
            step_kind = str(step.get("kind") or ("total" if step.get("is_total") else "delta")).lower()
            if step_kind in {"start", "total"}:
                running = val if ("value" in step or step_kind == "start") else running
                bases.append(0.0)
                pos_vals.append(round(running, 4) if running >= 0 else "-")
                neg_vals.append(round(abs(running), 4) if running < 0 else "-")
            elif val >= 0:
                bases.append(round(running, 4))
                pos_vals.append(round(val, 4))
                neg_vals.append("-")
                running += val
            else:
                running += val
                bases.append(round(running, 4))
                pos_vals.append("-")
                neg_vals.append(round(abs(val), 4))
        return {
            "kind": "waterfall",
            "title": _plain_text(meta.get("title") or "Waterfall Budget"),
            "rigor": rigor,
            "medium": medium,
            "yName": _plain_text((spec.get("axes") or {}).get("y_axis", {}).get("quantity_calculus") or "Value"),
            "categories": cats,
            "bases": bases,
            "positive": pos_vals,
            "negative": neg_vals,
        }

    if kind != "cartesian":
        return None

    axes = spec.get("axes") or {}
    xa = axes.get("x_axis") or {}
    ya = axes.get("y_axis") or {}
    x_dom = xa.get("domain") or [0.0, 10.0]
    y_dom = ya.get("domain") or [0.0, 100.0]
    x_min, x_max = float(x_dom[0]), float(x_dom[1])
    y_min, y_max = float(y_dom[0]), float(y_dom[1])
    log_x = str(xa.get("scale_type") or "").lower() in {"log", "logarithmic"}
    log_y = str(ya.get("scale_type") or "").lower() in {"log", "logarithmic"}

    series_out: list[dict[str, Any]] = []
    for s in spec.get("series", []):
        stype = str(s.get("epistemic_type") or "discrete_measurement")
        tok = _extract_token(s.get("marker_color") or s.get("stroke_color"), "--accent-focal")
        if stype == "analytical_model":
            pts = _sample_analytical_series(spec, s, x_min, x_max, log_x)
            if not pts:
                continue
            series_out.append({
                "id": str(s.get("id") or "model"),
                "name": _plain_text(s.get("name") or "Model"),
                "epistemic": "analytical_model",
                "term": str(s.get("term") or s.get("id") or ""),
                "token": tok,
                "dashed": str(s.get("stroke_style") or "dashed") != "solid",
                "data": pts,
            })
        else:
            pts_err: list[list[float | None]] = []
            for p in (s.get("data_points") or s.get("points") or []):
                xv = float(p["x"])
                yv = None if p.get("y") is None else float(p["y"])
                uy = float(p.get("u_y") or 0.0)
                pts_err.append([xv, yv, uy])
            series_out.append({
                "id": str(s.get("id") or "meas"),
                "name": _plain_text(s.get("name") or "Measurement"),
                "epistemic": "discrete_measurement",
                "term": str(s.get("term") or s.get("id") or ""),
                "token": tok,
                "connect": bool(s.get("connect_piecewise", True)),
                "symbol": str(s.get("marker_glyph") or "circle"),
                "data": pts_err,
            })

    if not series_out:
        return None

    env_out = [
        {
            "label": _plain_text(e.get("label") or ""),
            "value": float(e.get("threshold_value", 0.0)),
            "type": str(e.get("type") or "warning"),
            "token": _extract_token(e.get("stroke_color"), "--status-warn" if e.get("type") != "abort" else "--status-danger"),
        }
        for e in spec.get("envelopes", [])
        if "threshold_value" in e
    ]

    return {
        "kind": "cartesian",
        "title": _plain_text(meta.get("title") or "Analytical Plot"),
        "rigor": rigor,
        "medium": medium,
        "x": {"name": _plain_text(xa.get("quantity_calculus") or xa.get("quantity") or "x"), "min": x_min, "max": x_max, "log": log_x},
        "y": {"name": _plain_text(ya.get("quantity_calculus") or ya.get("quantity") or "y"), "min": y_min, "max": y_max, "log": log_y},
        "series": series_out,
        "envelopes": env_out,
    }


def render_echarts_toggle_bar() -> str:
    """Render accessible [Quiet SVG | Live ECharts] bench mode toggle."""
    return (
        '<div class="qe-plot-modebar" role="group" aria-label="Plot rendering backend">'
        '<span class="qe-modebar-label">Renderer</span>'
        '<button type="button" class="qe-mode-btn is-active" data-qe-mode="svg" aria-pressed="true">Quiet SVG</button>'
        '<button type="button" class="qe-mode-btn" data-qe-mode="echarts" aria-pressed="false">Live ECharts</button>'
        '</div>'
    )


def render_ecosystem_drawer(spec: dict[str, Any]) -> str:
    """Render progressive-disclosure 3-ecosystem code snippet drawer for Bench M4 cards."""
    payload = build_echarts_payload(spec, rigor=str((spec.get("metadata") or {}).get("rigor_level", "L3")))
    if payload is None:
        return ""
    x_label = str(payload.get("x", {}).get("name") or "Category")
    y_label = str(payload.get("y", {}).get("name") or payload.get("yName") or "Value")
    echarts_cfg = json.dumps(
        {
            "renderer": "svg",
            "xAxis": {"name": x_label, "type": "log" if payload.get("x", {}).get("log") else ("category" if payload["kind"] == "waterfall" else "value")},
            "yAxis": {"name": y_label, "type": "log" if payload.get("y", {}).get("log") else "value"},
            "markLine": [{"yAxis": e["value"], "name": e["label"]} for e in payload.get("envelopes", [])],
        },
        indent=2,
    )
    plotly_code = (
        f"fig.add_trace(go.Scatter(x=x, y=y, mode='markers+lines',\n"
        f"    error_y=dict(type='data', array=u_y, visible=True), name='Discrete'))\n"
        f"fig.update_layout(template='plotly_white', xaxis_title='{x_label}', yaxis_title='{y_label}')"
    )
    mpl_code = (
        f"ax.errorbar(x, y, yerr=u_y, fmt='o-', capsize=3, elinewidth=1.2)\n"
        f"ax.spines[['top', 'right']].set_visible(False)\n"
        f"ax.set(xlabel='{x_label}', ylabel='{y_label}')"
    )
    return (
        '<details class="qe-eco-drawer">'
        '<summary class="qe-eco-summary">Inspect Ecosystem Config (ECharts · Plotly · Matplotlib)</summary>'
        '<div class="qe-eco-grid">'
        '<section class="qe-eco-block"><h4 class="qe-eco-head">Apache ECharts (SVG · CSS Tokens)</h4>'
        f'<pre tabindex="0" role="region" aria-label="Apache ECharts configuration"><code>{esc(echarts_cfg)}</code></pre></section>'
        '<section class="qe-eco-block"><h4 class="qe-eco-head">Plotly (Python · NIST Error Bars)</h4>'
        f'<pre tabindex="0" role="region" aria-label="Plotly snippet"><code>{esc(plotly_code)}</code></pre></section>'
        '<section class="qe-eco-block"><h4 class="qe-eco-head">Matplotlib (Archival Despine)</h4>'
        f'<pre tabindex="0" role="region" aria-label="Matplotlib snippet"><code>{esc(mpl_code)}</code></pre></section>'
        '</div></details>'
    )
