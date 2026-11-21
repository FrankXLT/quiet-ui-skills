# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Flow-Conserving SVG Sankey & Multi-Track Telemetry Strip Chart Compilers."""

from __future__ import annotations

import json
import math
from typing import Any

from .svg_labels import halo_text
from .tokens_and_scales import (
    SERIES_STYLES,
    compute_linear_125_scale,
    esc,
    finite_float,
    format_math_svg,
    format_math_unicode,
    format_tick_numeral,
    resolve_token,
)

_SANK_COLS = ("var(--status-ok)", "var(--accent-focal)", "var(--status-warn)", "var(--tint-violet-fg)", "var(--status-danger)")


def _safe_f(val: Any) -> float | None:
    return finite_float(val)


def _extract_tok(color: Any, fallback: str = "--accent-focal") -> str:
    txt = str(color or "")
    if "var(" in txt:
        return txt.split("var(", 1)[1].split(")", 1)[0].split(",")[0].strip() or fallback
    return txt.strip() if txt.strip().startswith("#") else fallback


def _fmt_val(v: float) -> str:
    return f"{v:.1f}" if abs(v) >= 10.0 else (f"{v:.2f}".rstrip("0").rstrip(".") or "0")


def _parse_sankey(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    """Normalize Sankey nodes/links, infer topological stages, and compute conserved flow totals."""
    raw_nodes = [dict(n) for n in (spec.get("nodes") or []) if isinstance(n, dict) and n.get("id")]
    raw_links = [dict(lk) for lk in (spec.get("links") or spec.get("flows") or []) if isinstance(lk, dict)]
    unit = str(spec.get("unit") or "").strip()
    nmap: dict[str, dict[str, Any]] = {}
    for idx, nd in enumerate(raw_nodes):
        nid = str(nd["id"])
        nd.update({"_id": nid, "_col": resolve_token(nd.get("color") or nd.get("stroke"), _SANK_COLS[idx % len(_SANK_COLS)]), "_in": 0.0, "_out": 0.0})
        nmap[nid] = nd
    links: list[dict[str, Any]] = []
    for lk in raw_links:
        src, dst = str(lk.get("source") or lk.get("from") or ""), str(lk.get("target") or lk.get("to") or "")
        val = _safe_f(lk.get("value"))
        if src in nmap and dst in nmap and val is not None and val > 0.0:
            nmap[src]["_out"] += val
            nmap[dst]["_in"] += val
            links.append({"source": src, "target": dst, "value": val, "color": resolve_token(lk.get("color") or lk.get("fill"), nmap[src]["_col"])})
    if all(("stage" in n or "column" in n or "col" in n) for n in raw_nodes):
        for nd in raw_nodes:
            nd["_stage"] = int(nd.get("stage", nd.get("column", nd.get("col", 0))))
    else:
        for nd in raw_nodes:
            nd["_stage"] = 0
        for _ in range(len(raw_nodes)):
            for lk in links:
                if nmap[lk["target"]]["_stage"] <= nmap[lk["source"]]["_stage"]:
                    nmap[lk["target"]]["_stage"] = nmap[lk["source"]]["_stage"] + 1
    for nd in raw_nodes:
        nd["_val"] = max(nd["_in"], nd["_out"], _safe_f(nd.get("value")) or 0.0)
    return raw_nodes, links, unit


def _relax_label_ys(ys: list[float], min_dy: float, y_min: float, y_max: float) -> list[float]:
    if not ys:
        return []
    out = list(ys)
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + min_dy)
    if out[-1] > y_max:
        shift = out[-1] - y_max
        out = [y - shift for y in out]
    for i in range(len(out) - 2, -1, -1):
        out[i] = min(out[i], out[i + 1] - min_dy)
    if out[0] < y_min:
        out[0] = y_min
        for i in range(1, len(out)):
            out[i] = max(out[i], out[i - 1] + min_dy)
    return out


def _fmt_nom(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-6 else _fmt_val(v)


def _target_label_y(nd_g: dict[str, float], total: int, vb_h: int) -> float:
    mid = nd_g["y"] + nd_g["h"] / 2.0
    if nd_g["h"] < 26.0 and total > 1:
        return max(24.0, nd_g["y"] - 17.0)
    return mid


def compile_sankey(spec: dict[str, Any], rigor: str = "L2", medium: str = "m2") -> str:
    """Compile true flow-conserving multi-stage SVG Sankey with slim node bars and proportional Bezier ribbons."""
    nodes, links, unit = _parse_sankey(spec)
    if not nodes or not links:
        return '<svg class="qe-svg qe-svg-720" viewBox="0 0 720 260" role="img" aria-label="Flow Sankey"></svg>'
    by_stage: dict[int, list[dict[str, Any]]] = {}
    for nd in nodes:
        by_stage.setdefault(nd["_stage"], []).append(nd)
    stages = sorted(by_stage.keys())
    max_stage = stages[-1]
    stage_sums = [sum(n["_val"] for n in by_stage[st]) for st in stages]
    total_flow = stage_sums[0] if stage_sums and stage_sums[0] > 0.0 else max(stage_sums or [1.0])

    vb_w, vb_h, y_top, y_bot, node_w, node_gap = 720, 286, 20.0, 266.0, 14.0, 24.0
    avail_h = y_bot - y_top
    scale = min((avail_h - max(0, len(by_stage[st]) - 1) * node_gap) / max(sum(n["_val"] for n in by_stage[st]), 1e-9) for st in stages)
    x_step = (684.0 - 22.0) / max(len(stages) - 1, 1)
    geom: dict[str, dict[str, float]] = {}
    for si, st in enumerate(stages):
        st_nodes = by_stage[st]
        bx = 22.0 + si * x_step
        block_h = sum(max(4.0, n["_val"] * scale) for n in st_nodes) + max(0, len(st_nodes) - 1) * node_gap
        cur_y = y_top + max(0.0, (avail_h - block_h) / 2.0)
        for nd in st_nodes:
            nh = max(4.0, nd["_val"] * scale)
            geom[nd["_id"]] = {"x": bx, "y": cur_y, "h": nh, "out_y": cur_y, "in_y": cur_y}
            cur_y += nh + node_gap

    parts = [f'<svg class="qe-svg qe-svg-720 qe-sankey-svg" viewBox="0 0 {vb_w} {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Flow Sankey"))}">']
    for lk in sorted(links, key=lambda l: (geom[l["source"]]["y"], geom[l["target"]]["y"])):
        sg, dg = geom[lk["source"]], geom[lk["target"]]
        lh = max(1.6, lk["value"] * scale)
        sy0, sy1 = sg["out_y"], min(sg["y"] + sg["h"], sg["out_y"] + lh)
        dy0, dy1 = dg["in_y"], min(dg["y"] + dg["h"], dg["in_y"] + lh)
        sg["out_y"], dg["in_y"] = sy1, dy1
        x1, x2 = sg["x"] + node_w, dg["x"]
        mx = (x1 + x2) / 2.0
        p = f"M {x1:.1f} {sy0:.1f} C {mx:.1f} {sy0:.1f}, {mx:.1f} {dy0:.1f}, {x2:.1f} {dy0:.1f} L {x2:.1f} {dy1:.1f} C {mx:.1f} {dy1:.1f}, {mx:.1f} {sy1:.1f}, {x1:.1f} {sy1:.1f} Z"
        parts.append(f'<path d="{p}" fill="{lk["color"]}" fill-opacity="0.28" stroke="{lk["color"]}" stroke-opacity="0.58" stroke-width="0.9"/>')

    for st in stages:
        st_nodes = by_stage[st]
        is_last = st == max_stage and len(stages) > 1
        anchor = "end" if is_last else "start"
        lbl_ys = _relax_label_ys([_target_label_y(geom[n["_id"]], len(st_nodes), vb_h) for n in st_nodes], 30.0, 22.0, vb_h - 18.0)
        for nd, ly in zip(st_nodes, lbl_ys):
            g = geom[nd["_id"]]
            parts.append(f'<rect data-role="node" x="{g["x"]:.1f}" y="{g["y"]:.1f}" width="{node_w:.1f}" height="{g["h"]:.1f}" rx="2" fill="{nd["_col"]}" stroke="var(--bg-surface)" stroke-width="1"/>')
            lx = (g["x"] - 8.0) if is_last else (g["x"] + node_w + 8.0)
            pct = (nd["_val"] / total_flow * 100.0) if total_flow > 0.0 else 0.0
            m_txt = nd.get("metric") or f"{_fmt_val(nd['_val'])}{(' ' + unit) if unit else ''}"
            parts.append(halo_text(lx, ly - 3.0, str(nd.get("label") or nd["_id"]), anchor=anchor, size=11.5, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=True, stroke_width=3.6))
            parts.append(halo_text(lx, ly + 12.0, f"{m_txt} ({pct:.1f}%)", anchor=anchor, size=11.5, weight="600", fill=nd["_col"], halo=True, stroke_width=3.6))
    parts.append("</svg>")
    return "\n".join(parts)


def build_sankey_echarts_payload(spec: dict[str, Any], rigor: str = "L2", medium: str = "m2") -> dict[str, Any] | None:
    """Build deterministic Apache ECharts descriptor for a flow-conserving Sankey."""
    nodes, links, unit = _parse_sankey(spec)
    if not nodes or not links:
        return None
    id_to_name = {n["_id"]: str(n.get("label") or n["_id"]) for n in nodes}
    st_sums: dict[int, float] = {}
    for n in nodes:
        st_sums[n["_stage"]] = st_sums.get(n["_stage"], 0.0) + n["_val"]
    total_flow = st_sums.get(min(st_sums), 1.0) or 1.0
    return {
        "kind": "sankey",
        "title": format_math_unicode((spec.get("metadata") or {}).get("title") or "Flow Sankey"),
        "rigor": rigor, "medium": medium, "unit": unit, "totalFlow": round(total_flow, 3),
        "nodes": [{"id": n["_id"], "name": id_to_name[n["_id"]], "stage": n["_stage"], "value": round(n["_val"], 3), "token": _extract_tok(n.get("color") or n.get("stroke"), "--accent-focal")} for n in nodes],
        "links": [{"source": id_to_name[l["source"]], "target": id_to_name[l["target"]], "value": round(l["value"], 3)} for l in links],
    }


def _strip_track_metrics(tr: dict[str, Any]) -> tuple[list[tuple[float, float]], float, float, float, bool]:
    pts = [(t, v) for s in tr.get("samples", []) if isinstance(s, (list, tuple)) and len(s) >= 2 and (t := _safe_f(s[0])) is not None and (v := _safe_f(s[1])) is not None]
    if not pts:
        return [], 0.0, 0.0, 0.0, False
    vals = [v for _, v in pts]
    cur_v, max_v, min_v = vals[-1], max(vals), min(vals)
    wh, wl = _safe_f(tr.get("warn_high")), _safe_f(tr.get("warn_low"))
    return pts, cur_v, max_v, min_v, (wh is not None and max_v > wh) or (wl is not None and min_v < wl)


def _render_strip_lane(
    parts: list[str], idx: int, tr: dict[str, Any], ly: float, lane_h: float,
    x0: float, pw: float, t_min: float, t_span: float, t_sc: dict[str, Any], minor_cls: str,
) -> dict[str, Any]:
    hdr_h, wave_top, wave_h = 20.0, ly + 20.0, lane_h - 20.0
    y_hi_px, y_lo_px = wave_top + 4.0, ly + lane_h - 4.0
    col = resolve_token(tr.get("color") or tr.get("trace_color"), SERIES_STYLES[idx % len(SERIES_STYLES)]["stroke"])
    pts, cur_v, max_v, min_v, breached = _strip_track_metrics(tr)
    dom = tr.get("domain") if isinstance(tr.get("domain"), (list, tuple)) and len(tr.get("domain")) >= 2 else [min([v for _, v in pts] or [0.0]), max([v for _, v in pts] or [1.0])]
    y_min = _safe_f(dom[0])
    y_max = _safe_f(dom[1])
    if y_min is None:
        y_min = 0.0
    if y_max is None or y_max <= y_min:
        y_max = y_min + 1.0
    span_y = y_max - y_min
    proj_y = lambda v: max(y_hi_px, min(y_lo_px, y_lo_px - ((v - y_min) / span_y) * (y_lo_px - y_hi_px)))
    proj_x = lambda t: x0 + ((t - t_min) / t_span) * pw

    parts.append(f'<rect data-role="channel" x="{x0}" y="{ly:.1f}" width="{pw}" height="{lane_h:.1f}" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1"/>')
    parts.append(f'<rect data-role="channel-hdr" x="{x0 + 0.5:.1f}" y="{ly + 0.5:.1f}" width="{pw - 1:.1f}" height="{hdr_h - 0.5:.1f}" fill="var(--bg-elevated)"/>')
    parts.append(f'<line x1="{x0}" y1="{wave_top:.1f}" x2="{x0 + pw}" y2="{wave_top:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')
    nom = tr.get("nominal_band")
    nom_lo = _safe_f(nom[0]) if isinstance(nom, (list, tuple)) and len(nom) == 2 else None
    nom_hi = _safe_f(nom[1]) if isinstance(nom, (list, tuple)) and len(nom) == 2 else None
    if nom_lo is not None and nom_hi is not None:
        ny_top, ny_bot = proj_y(nom_hi), proj_y(nom_lo)
        if ny_bot > ny_top:
            parts.append(f'<rect x="{x0 + 0.5:.1f}" y="{ny_top:.1f}" width="{pw - 1:.1f}" height="{ny_bot - ny_top:.1f}" fill="var(--status-ok-bg)" opacity="0.65"/>')
    for xm in t_sc["minors"]:
        if t_min <= xm <= t_min + t_span:
            parts.append(f'<line class="{minor_cls}" x1="{proj_x(xm):.1f}" y1="{wave_top:.1f}" x2="{proj_x(xm):.1f}" y2="{ly + lane_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.5" stroke-dasharray="1,3"/>')
    for xmaj in t_sc["majors"]:
        if t_min - 1e-9 <= xmaj <= t_min + t_span + 1e-9:
            parts.append(f'<line x1="{proj_x(xmaj):.1f}" y1="{wave_top:.1f}" x2="{proj_x(xmaj):.1f}" y2="{ly + lane_h:.1f}" stroke="var(--border-hairline)" stroke-width="0.8"/>')

    step_y = (y_max - y_min) / 2.0
    parts.append(halo_text(x0 - 6.0, wave_top + 11.0, format_tick_numeral(y_max, step=step_y), anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(halo_text(x0 - 6.0, wave_top + wave_h / 2.0 + 4.0, format_tick_numeral(0.5 * (y_min + y_max), step=step_y), anchor="end", size=11.5, fill="var(--text-muted)", halo=False))
    parts.append(halo_text(x0 - 6.0, ly + lane_h - 2.0, format_tick_numeral(y_min, step=step_y), anchor="end", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(halo_text(x0 - 8.0, ly + 14.0, f"T{idx + 1}", anchor="end", size=11.5, weight="700", fill=col, halo=False))
    hdr_txt = f'{tr.get("name", f"Track {idx + 1}")} ({tr.get("quantity_calculus", tr.get("unit", ""))})'
    parts.append(f'<text x="{x0 + 8.0:.1f}" y="{ly + 14.0:.1f}" text-anchor="start" font-family="var(--font-mono)" font-size="11.5" font-weight="600" fill="var(--text-primary)">{format_math_svg(hdr_txt, 8.8)}</text>')

    wh, wl = _safe_f(tr.get("warn_high")), _safe_f(tr.get("warn_low"))
    for thr in (wh, wl):
        if thr is not None and y_min <= thr <= y_max:
            parts.append(f'<line x1="{x0}" y1="{proj_y(thr):.1f}" x2="{x0 + pw}" y2="{proj_y(thr):.1f}" stroke="var(--status-warn)" stroke-width="1.1" stroke-dasharray="4,3"/>')
    if pts:
        d = " ".join(f'{"M" if i == 0 else "L"} {proj_x(t):.1f} {proj_y(v):.1f}' for i, (t, v) in enumerate(pts))
        parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/>')
        exc_segs, cur_exc = [], []
        for t, v in pts:
            if (wh is not None and v > wh) or (wl is not None and v < wl):
                cur_exc.append(f'{"M" if not cur_exc else "L"} {proj_x(t):.1f} {proj_y(v):.1f}')
            elif cur_exc:
                exc_segs.append(" ".join(cur_exc)); cur_exc = []
        if cur_exc:
            exc_segs.append(" ".join(cur_exc))
        if exc_segs:
            parts.append(f'<path d="{" ".join(exc_segs)}" fill="none" stroke="var(--status-warn)" stroke-width="2.4" stroke-linejoin="round"/>')
            ext_t, ext_v = max(pts, key=lambda p: p[1]) if (wh is not None and max_v > wh) else min(pts, key=lambda p: p[1])
            px_e, py_e = proj_x(ext_t), proj_y(ext_v)
            parts.append(f'<polygon points="{px_e:.1f},{py_e - 4.5:.1f} {px_e + 4.5:.1f},{py_e:.1f} {px_e:.1f},{py_e + 4.5:.1f} {px_e - 4.5:.1f},{py_e:.1f}" fill="var(--status-warn)" stroke="var(--bg-surface)" stroke-width="1"/>')

    gx, gw = x0 + pw + 8.0, 130.0
    st_col = "var(--status-warn)" if breached else "var(--status-ok)"
    unit_s = str(tr.get("unit") or "").strip()
    u_suf = f"\u00a0{unit_s}" if unit_s else ""
    ext_txt = f"Min {_fmt_val(min_v)}{u_suf}" if (wl is not None and min_v < wl) else f"Peak {_fmt_val(max_v)}{u_suf}"
    parts.append(f'<rect data-role="readout-box" x="{gx:.1f}" y="{ly:.1f}" width="{gw:.1f}" height="{lane_h:.1f}" rx="4" fill="var(--bg-elevated)" stroke="{st_col if breached else "var(--border-strong)"}" stroke-width="1.2"/>')
    parts.append(halo_text(gx + 8.0, ly + 17.0, "EXCURSION" if breached else "NOMINAL", anchor="start", size=11.5, weight="700", fill=st_col, halo=False))
    parts.append(halo_text(gx + 8.0, ly + 39.0, f"{_fmt_val(cur_v)}{u_suf}", anchor="start", size=13.5, weight="700", fill="var(--text-primary)", halo=False))
    parts.append(halo_text(gx + 8.0, ly + 58.0, ext_txt, anchor="start", size=11.5, weight="600", fill=st_col if breached else "var(--text-secondary)", halo=False))
    if nom_lo is not None and nom_hi is not None:
        parts.append(halo_text(gx + 8.0, ly + 75.0, f"Nom {_fmt_nom(nom_lo)}–{_fmt_nom(nom_hi)}", anchor="start", size=11.5, fill="var(--text-muted)", halo=False))
    return {"id": tr.get("id", f"t{idx + 1}"), "name": tr.get("name", ""), "unit": unit_s, "samples": tr.get("samples", [])}


def _render_strip_core(spec: dict[str, Any], rigor: str, medium: str) -> tuple[str, str, str]:
    tb = spec.get("timebase") or {}
    t_unit = str(tb.get("unit") or "s")
    tracks = spec.get("tracks") or spec.get("channels") or []
    vis_tracks = tracks[:2] if rigor == "L1" else tracks
    raw_min, raw_span = _safe_f(tb.get("start_time")), _safe_f(tb.get("total_span"))
    t_min = raw_min if raw_min is not None else 0.0
    t_span = raw_span if (raw_span is not None and raw_span > 0) else 60.0
    t_max, t_sc = t_min + t_span, compute_linear_125_scale(t_min, t_min + t_span, target_ticks=6)
    x0, y0, pw, lane_h, lane_gap = 78.0, 14.0, 496.0, 84.0, 10.0
    tot_h = len(vis_tracks) * lane_h + max(0, len(vis_tracks) - 1) * lane_gap
    vb_h = int(y0 + tot_h + 44.0)
    parts = [f'<svg class="qe-svg qe-svg-720 qe-waveform-svg" data-qe-scope="true" tabindex="0" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Telemetry Strip Chart"))}">']
    minor_cls = "qe-grid-minor" if medium == "m1" else "qe-grid-minor qe-m1-only"
    meta_ch = [_render_strip_lane(parts, i, tr, y0 + i * (lane_h + lane_gap), lane_h, x0, pw, t_min, t_span, t_sc, minor_cls) for i, tr in enumerate(vis_tracks)]
    for xm in t_sc["minors"]:
        if t_min <= xm <= t_max:
            parts.append(f'<line x1="{x0 + ((xm - t_min) / t_span) * pw:.1f}" y1="{y0 + tot_h}" x2="{x0 + ((xm - t_min) / t_span) * pw:.1f}" y2="{y0 + tot_h + 4}" stroke="var(--border-strong)" stroke-width="0.8"/>')
    for xmaj in t_sc["majors"]:
        if t_min - 1e-9 <= xmaj <= t_max + 1e-9:
            parts.append(halo_text(x0 + ((xmaj - t_min) / t_span) * pw, y0 + tot_h + 18.0, format_tick_numeral(xmaj, step=t_sc["step"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
    parts.append(halo_text(x0 + pw / 2.0, y0 + tot_h + 36.0, tb.get("quantity_calculus", f"t / {t_unit}"), anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False, math=True))
    parts.append(f'<line class="qe-live-cursor" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + tot_h}" stroke="var(--accent-focal)" stroke-width="1.3" visibility="hidden"/>')
    parts.append("</svg>")
    dt_v = _safe_f(tb.get("nominal_dt"))
    meta_obj: dict[str, Any] = {"t_min": t_min, "t_span": t_span, "t_unit": t_unit, "max_gap": t_span, "x0": x0, "pw": pw, "channels": meta_ch}
    if dt_v is not None and dt_v > 0:
        meta_obj["dt"] = dt_v
    meta_json = json.dumps(meta_obj, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    def_msg = "Hover, drag, or use Left/Right keys to scrub synchronized telemetry strips"
    readout = f'<div class="qe-scope-readout va-nums" data-default="{def_msg}" aria-live="polite">{def_msg}</div>'
    script = f'<script type="application/json" class="qe-scope-data">{meta_json}</script>'
    return "".join(parts), readout, script


def compile_strip_chart(spec: dict[str, Any], rigor: str = "L3", medium: str = "m2", include_scroll: bool = True) -> str:
    """Compile synchronized multi-track telemetry strip chart with nominal corridors & pinned digital readout."""
    svg_html, readout, script = _render_strip_core(spec, rigor, medium)
    scroll = f'<div class="va-figure-scroll qe-scope-scroll" tabindex="0" role="region" aria-label="{esc(spec.get("metadata", {}).get("title", "Telemetry Strip Chart"))}">{svg_html}</div>'
    return f'<div class="qe-waveform-wrap">{scroll}{readout}{script}</div>' if include_scroll else f"{scroll}{readout}{script}"


def build_strip_chart_echarts_payload(spec: dict[str, Any], rigor: str = "L3", medium: str = "m2") -> dict[str, Any] | None:
    """Build synchronized multi-grid ECharts descriptor for a telemetry strip chart."""
    tb = spec.get("timebase") or {}
    vis_tracks = (spec.get("tracks") or spec.get("channels") or [])[: (2 if rigor == "L1" else None)]
    if not vis_tracks:
        return None
    raw_min, raw_span = _safe_f(tb.get("start_time")), _safe_f(tb.get("total_span"))
    t_min = raw_min if raw_min is not None else 0.0
    t_span = raw_span if (raw_span is not None and raw_span > 0) else 60.0
    t_sc = compute_linear_125_scale(t_min, t_min + t_span, target_ticks=6)
    out_tracks: list[dict[str, Any]] = []
    for idx, tr in enumerate(vis_tracks):
        pts, cur_v, max_v, min_v, breached = _strip_track_metrics(tr)
        dom = tr.get("domain") if isinstance(tr.get("domain"), (list, tuple)) and len(tr.get("domain")) >= 2 else [min_v, max_v]
        y_lo = _safe_f(dom[0])
        y_hi = _safe_f(dom[1])
        if y_lo is None:
            y_lo = min_v
        if y_hi is None or y_hi <= y_lo:
            y_hi = y_lo + 1.0
        out_tracks.append({
            "id": str(tr.get("id") or f"t{idx + 1}"), "name": format_math_unicode(tr.get("name") or f"Track {idx + 1}"),
            "calculus": format_math_unicode(tr.get("quantity_calculus") or tr.get("unit") or ""), "unit": str(tr.get("unit") or ""),
            "min": y_lo, "max": y_hi, "interval": round((y_hi - y_lo) / 2.0, 4), "nominalBand": tr.get("nominal_band"),
            "warnHigh": _safe_f(tr.get("warn_high")), "warnLow": _safe_f(tr.get("warn_low")),
            "token": _extract_tok(tr.get("color") or tr.get("trace_color"), _extract_tok(SERIES_STYLES[idx % len(SERIES_STYLES)]["stroke"])),
            "current": round(cur_v, 3), "peak": round(max_v, 3), "minVal": round(min_v, 3), "breached": breached,
            "data": [[round(t, 4), round(v, 4)] for t, v in pts],
        })
    return {
        "kind": "strip_chart", "title": format_math_unicode((spec.get("metadata") or {}).get("title") or "Telemetry Strip Chart"),
        "rigor": rigor, "medium": medium, "tracks": out_tracks,
        "x": {"name": format_math_unicode(tb.get("quantity_calculus") or f"Time, t / {tb.get('unit', 's')}"), "unit": str(tb.get("unit") or "s"), "min": t_sc["min"], "max": t_sc["max"], "interval": t_sc["step"]},
    }


def compile_strip_chart_block(spec: dict[str, Any], rigor: str = "L3", medium: str = "m2", chrome: str = "bench") -> str:
    """Wrap strip chart SVG + Live ECharts toggle bar & host container with pinned SVG readout."""
    payload = build_strip_chart_echarts_payload(spec, rigor, medium)
    payload_attr = f' data-quiet-echarts="{esc(json.dumps(payload, separators=(",", ":"), allow_nan=False))}"' if payload is not None else ""
    bar = (
        '<div class="qe-plot-modebar" role="group" aria-label="Plot rendering backend">'
        '<span class="qe-modebar-label">Renderer</span>'
        '<button type="button" class="qe-mode-btn is-active" data-qe-mode="svg" aria-pressed="true">Quiet SVG</button>'
        '<button type="button" class="qe-mode-btn" data-qe-mode="echarts" aria-pressed="false">Live ECharts</button></div>'
    ) if (chrome == "bench" and payload is not None) else ""
    svg_only, readout, script = _render_strip_core(spec, rigor, medium)
    host = '<div class="qe-echarts-host" hidden></div>' if payload is not None else ""
    title_lbl = esc((spec.get("metadata") or {}).get("title", "Telemetry Strip Chart"))
    scroll = f'<div class="va-figure-scroll qe-scope-scroll" tabindex="0" role="region" aria-label="{title_lbl}"><div class="qe-svg-fallback">{svg_only}</div>{host}</div>'
    return f'<div class="qe-plot-wrap" data-rigor="{esc(rigor)}" data-medium="{esc(medium)}"{payload_attr}>{bar}{scroll}<div class="qe-svg-fallback">{readout}</div>{script}</div>'
