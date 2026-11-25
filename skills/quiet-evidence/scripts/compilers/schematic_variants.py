# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 6 Generalized v7.1 Structural Variants."""

from __future__ import annotations

from typing import Any

from .svg_labels import halo_text, svg_knockout_label
from .tokens_and_scales import esc, resolve_token


def compile_optical_stack(spec: dict[str, Any]) -> str:
    """Compile exploded 3-plane optical stack (recovered from v7.1)."""
    planes = spec.get("planes", [])
    vb_h = max(210, 54 + len(planes) * 58)
    parts: list[str] = [f'<svg class="qe-svg qe-svg-680" viewBox="0 0 680 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Optical Stack"))}">']
    for idx, pl in enumerate(planes):
        py = 36.0 + idx * 56.0
        fill = resolve_token(pl.get("fill_token"), "var(--tint-indigo-bg)" if idx == 0 else "var(--bg-card)")
        stroke = "var(--accent-focal)" if idx == 0 else "var(--border-strong)"
        pts = f"64,{py + 14:.1f} 256,{py:.1f} 324,{py + 32:.1f} 132,{py + 46:.1f}"
        parts.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        parts.append(f'<line x1="324" y1="{py + 32:.1f}" x2="366" y2="{py + 22:.1f}" stroke="var(--text-secondary)" stroke-width="1.1"/>')
        parts.append(f'<circle cx="366" cy="{py + 22:.1f}" r="2.6" fill="var(--accent-focal)"/>')
        parts.append(halo_text(376.0, py + 26.0, str(pl["label"]), anchor="start", size=12.0, weight="700", fill="var(--text-primary)", halo=False))
        if pl.get("detail"):
            parts.append(halo_text(376.0, py + 43.0, str(pl["detail"]), anchor="start", size=11.5, fill="var(--text-muted)", halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


def compile_delta_lanes(spec: dict[str, Any]) -> str:
    """Compile Baseline vs Proposed vs Decommissioned architecture delta lanes."""
    lanes = spec.get("lanes", [])
    vb_h = max(180, 32 + len(lanes) * 86)
    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Architecture Delta"))}">',
        '<defs><marker id="qe-dl-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-secondary)"/></marker>'
        '<marker id="qe-dl-ok" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-ok)"/></marker></defs>',
    ]
    for li, lane in enumerate(lanes):
        ly = 18.0 + li * 84.0
        kind = str(lane.get("kind", "baseline")).lower()
        nodes = lane.get("nodes", [])
        stroke = "var(--status-ok)" if kind == "proposed" else ("var(--status-danger)" if kind == "decommissioned" else "var(--border-strong)")
        hdr_col = "var(--status-ok)" if kind == "proposed" else ("var(--status-danger)" if kind == "decommissioned" else "var(--text-secondary)")
        dash = ' stroke-dasharray="4,4"' if kind != "proposed" else ""
        parts.append(halo_text(22.0, ly + 12.0, str(lane.get("title", kind.upper())), anchor="start", size=11.5, weight="700", fill=hdr_col, halo=False))
        slot = 676.0 / max(len(nodes), 1)
        bw = min(192.0, slot - 34.0)
        for ni, nd in enumerate(nodes):
            bx = 22.0 + ni * slot
            by = ly + 20.0
            fill = "var(--status-ok-bg)" if kind == "proposed" else ("var(--status-err-bg)" if kind == "decommissioned" else "var(--bg-card)")
            parts.append(f'<rect data-role="node" x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="48" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
            parts.append(halo_text(bx + bw / 2.0, by + 20.0, str(nd["label"]), anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
            parts.append(halo_text(bx + bw / 2.0, by + 37.0, str(nd.get("sublabel", "")), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
            if ni < len(nodes) - 1:
                mk = "qe-dl-ok" if kind == "proposed" else "qe-dl-arr"
                parts.append(f'<line x1="{bx + bw:.1f}" y1="{by + 24:.1f}" x2="{bx + slot - 2:.1f}" y2="{by + 24:.1f}" stroke="{hdr_col}" stroke-width="1.5" marker-end="url(#{mk})"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def compile_fsm(spec: dict[str, Any]) -> str:
    """Compile normative state machine with bullseye start, fault double-ring & padded loopback."""
    states = spec.get("states", [])
    transitions = spec.get("transitions", [])
    x_pos: dict[str, float] = {}
    n_st = max(len(states), 1)
    x_cur, gap = 50.0, 20.0
    bw = min(112.0, (704.0 - x_cur - max(0, n_st - 1) * gap) / n_st)
    bh, y_row = 48.0, 34.0
    for idx, st in enumerate(states):
        x_pos[st["id"]] = x_cur + idx * (bw + gap)

    ret_count = sum(1 for tr in transitions if (x_pos.get(tr["to"], 0) <= x_pos.get(tr["from"], 0)) and tr["from"] in x_pos and tr["to"] in x_pos)
    vb_h = int(max(132.0, y_row + bh + (34.0 + ret_count * 52.0 if ret_count else 24.0)))
    cy_mid = y_row + bh / 2.0

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="Finite State Machine">',
        '<defs><marker id="qe-fsm-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-primary)"/></marker></defs>',
        f'<circle cx="24" cy="{cy_mid:.1f}" r="7" fill="var(--text-primary)"/><circle cx="24" cy="{cy_mid:.1f}" r="12" fill="none" stroke="var(--text-primary)" stroke-width="1.4"/>',
    ]
    for idx, st in enumerate(states):
        sx = x_pos[st["id"]]
        tone = str(st.get("tone", "neutral")).lower()
        t_style = {
            "focal": ("var(--bg-card)", "var(--accent-focal)", "var(--accent-focal)"),
            "ok": ("var(--status-ok-bg)", "var(--status-ok)", "var(--status-ok)"),
            "warn": ("var(--status-warn-bg)", "var(--status-warn)", "var(--status-warn)"),
            "err": ("var(--status-err-bg)", "var(--status-danger)", "var(--status-danger)"),
        }.get(tone, ("var(--bg-card)", "var(--border-strong)", "var(--text-primary)"))
        parts.append(f'<rect data-role="node" x="{sx:.1f}" y="{y_row}" width="{bw:.1f}" height="{bh}" rx="5" fill="{t_style[0]}" stroke="{t_style[1]}" stroke-width="1.6"/>')
        if tone == "err":
            parts.append(f'<rect data-role="node-ring" x="{sx + 3:.1f}" y="{y_row + 3}" width="{max(4.0, bw - 6):.1f}" height="{bh - 6}" rx="3" fill="none" stroke="{t_style[1]}" stroke-width="1"/>')
        parts.append(halo_text(sx + bw / 2.0, y_row + 21.0, str(st["label"]), anchor="middle", size=11.5, weight="700", fill=t_style[2], halo=False))
        parts.append(halo_text(sx + bw / 2.0, y_row + 37.0, str(st.get("sublabel", "")), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
        if idx == 0:
            parts.append(f'<line x1="36" y1="{cy_mid:.1f}" x2="{sx:.1f}" y2="{cy_mid:.1f}" stroke="var(--border-strong)" stroke-width="1.4" marker-end="url(#qe-fsm-arr)"/>')

    ret_idx = 0
    for tr in transitions:
        sx, dx = x_pos.get(tr["from"]), x_pos.get(tr["to"])
        if sx is None or dx is None:
            continue
        if dx > sx:
            parts.append(f'<line x1="{sx + bw:.1f}" y1="{cy_mid:.1f}" x2="{dx:.1f}" y2="{cy_mid:.1f}" stroke="var(--text-primary)" stroke-width="1.4" marker-end="url(#qe-fsm-arr)"/>')
            parts.append(halo_text((sx + bw + dx) / 2.0, y_row - 10.0, str(tr["label"]), anchor="middle", size=11.5, fill="var(--text-secondary)", halo=False))
        else:
            cx_s, cx_d = sx + bw / 2.0, dx + bw / 2.0
            loop_y = y_row + bh + 44.0 + ret_idx * 44.0
            d = f"M {cx_s:.1f} {y_row + bh} L {cx_s:.1f} {loop_y - 8.0:.1f} A 8 8 0 0 1 {cx_s - 8:.1f} {loop_y:.1f} L {cx_d + 8:.1f} {loop_y:.1f} A 8 8 0 0 1 {cx_d:.1f} {loop_y - 8.0:.1f} L {cx_d:.1f} {y_row + bh}"
            parts.append(f'<path d="{d}" fill="none" stroke="var(--text-secondary)" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#qe-fsm-arr)"/>')
            parts.append(svg_knockout_label((cx_s + cx_d) / 2.0, loop_y + 20.0, str(tr["label"]), anchor="middle", size=11.5, weight="600", fill="var(--text-secondary)", surface_fill="var(--bg-surface)", x_bounds=(8.0, 712.0), math=False))
            ret_idx += 1
    parts.append("</svg>")
    return "\n".join(parts)


def compile_wardley(spec: dict[str, Any]) -> str:
    """Compile Wardley evolution map (Genesis -> Custom -> Product -> Commodity)."""
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    x0, y0, pw, ph = 64.0, 24.0, 624.0, 196.0
    stages = ("GENESIS", "CUSTOM", "PRODUCT", "COMMODITY")
    parts: list[str] = [
        '<svg class="qe-svg qe-svg-720" viewBox="0 0 720 264" role="img" aria-label="Wardley Value Chain Map">',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>',
        f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="var(--text-primary)" stroke-width="1.1"/>',
    ]
    for i, stg in enumerate(stages):
        sx = x0 + i * (pw / 4.0)
        if i > 0:
            parts.append(f'<line x1="{sx:.1f}" y1="{y0}" x2="{sx:.1f}" y2="{y0 + ph}" stroke="var(--border-hairline)" stroke-width="1" stroke-dasharray="3,3"/>')
        parts.append(halo_text(sx + pw / 8.0, y0 + ph + 20.0, stg, anchor="middle", size=11.5, weight="700", fill="var(--text-secondary)", halo=False))

    pos = {n["id"]: (x0 + float(n["evolution"]) * pw, y0 + (1.0 - float(n["visibility"])) * ph) for n in nodes}
    for ed in edges:
        p1, p2 = pos.get(ed["from"]), pos.get(ed["to"])
        if p1 and p2:
            parts.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="var(--border-strong)" stroke-width="1.4" stroke-dasharray="4,3"/>')
    for nd in nodes:
        px, py = pos[nd["id"]]
        col = resolve_token(nd.get("color"), "var(--accent-focal)")
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{col}" stroke="var(--bg-canvas)" stroke-width="1.2"/>')
        anchor = "end" if px > x0 + pw * 0.72 else "start"
        dx = -10.0 if anchor == "end" else 10.0
        parts.append(halo_text(px + dx, py + 4.0, str(nd["label"]), anchor=anchor, size=11.5, weight="600", fill="var(--text-primary)"))
    parts.append("</svg>")
    return "\n".join(parts)


from .sankey_and_strip import compile_sankey  # noqa: F401


def compile_er_lineage(spec: dict[str, Any]) -> str:
    """Compile Crow's-Foot ER database lineage schema (auto 2x2 grid for >= 4 entities)."""
    entities = spec.get("entities", [])
    rels = spec.get("relations", [])
    is_grid = len(entities) >= 4
    rows = (len(entities) + 1) // 2 if is_grid else 1
    vb_h = int(16 + rows * 132) if is_grid else 192
    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="ER Schema Lineage">',
        '<defs><marker id="qe-er-many" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto"><path d="M 0 1 L 10 6 L 0 11 M 5 1 L 5 11" fill="none" stroke="var(--border-strong)" stroke-width="1.2"/></marker>'
        '<marker id="qe-er-one" viewBox="0 0 12 12" refX="2" refY="6" markerWidth="8" markerHeight="8" orient="auto"><path d="M 4 1 L 4 11 M 8 1 L 8 11" fill="none" stroke="var(--border-strong)" stroke-width="1.4"/></marker></defs>',
    ]
    layout: dict[str, dict[str, Any]] = {}
    for idx, e in enumerate(entities):
        if is_grid:
            col_i, row_i = idx % 2, idx // 2
            ex, ey, ew, eh = (36.0 if col_i == 0 else 388.0), 14.0 + row_i * 132.0, 296.0, 104.0
        else:
            ex, ey, ew, eh = float(e["x"]), float(e["y"]), float(e.get("w", 190)), float(e.get("h", 120))
        layout[e["id"]] = {"x": ex, "y": ey, "w": ew, "h": eh, "row": idx // 2 if is_grid else 0, "col": idx % 2 if is_grid else idx}
        hdr_bg = "var(--tint-indigo-bg)" if e.get("focal") else "var(--bg-header)"
        stroke = "var(--accent-focal)" if e.get("focal") else "var(--border-strong)"
        parts.append(f'<rect data-role="node" x="{ex:.1f}" y="{ey:.1f}" width="{ew:.1f}" height="{eh:.1f}" rx="5" fill="var(--bg-card)" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<rect data-role="node-header" x="{ex:.1f}" y="{ey:.1f}" width="{ew:.1f}" height="22" rx="5" fill="{hdr_bg}"/>')
        parts.append(halo_text(ex + ew / 2.0, ey + 15.0, str(e["label"]), anchor="middle", size=11.5, weight="700", fill=stroke if e.get("focal") else "var(--text-primary)", halo=False))
        for ci, col_txt in enumerate(e.get("columns", [])):
            parts.append(halo_text(ex + 12.0, ey + 37.5 + ci * 15.5, str(col_txt), anchor="start", size=11.5, fill="var(--text-secondary)", halo=False))

    for r in rels:
        s, d = layout.get(r["from"]), layout.get(r["to"])
        if not s or not d:
            continue
        if is_grid and (s["row"] != d["row"] or s["col"] != d["col"]):
            if s["row"] == d["row"] and s["col"] < d["col"]:
                sy, sx, dx = s["y"] + s["h"] / 2.0, s["x"] + s["w"], d["x"]
                parts.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{dx:.1f}" y2="{sy:.1f}" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#qe-er-one)" marker-end="url(#qe-er-many)"/>')
            elif s["col"] == d["col"]:
                vx = s["x"] + s["w"] / 2.0 + (22.0 if r.get("route") == "bottom" else 0.0)
                sy, dy = s["y"] + s["h"], d["y"]
                parts.append(f'<line x1="{vx:.1f}" y1="{sy:.1f}" x2="{vx:.1f}" y2="{dy:.1f}" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#qe-er-one)" marker-end="url(#qe-er-many)"/>')
            else:
                sx, sy = s["x"] + s["w"] * 0.38, s["y"] + s["h"]
                dx, dy = d["x"] + d["w"] * 0.62, d["y"]
                ym = (sy + dy) / 2.0
                p = f"M {sx:.1f} {sy:.1f} L {sx:.1f} {ym:.1f} L {dx:.1f} {ym:.1f} L {dx:.1f} {dy:.1f}"
                parts.append(f'<path d="{p}" fill="none" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#qe-er-one)" marker-end="url(#qe-er-many)"/>')
        elif not is_grid and r.get("route") == "bottom":
            sx, sy = s["x"] + s["w"] / 2.0, s["y"] + s["h"]
            dx, dy = d["x"] + d["w"] / 2.0, d["y"] + d["h"]
            p = f"M {sx:.1f} {sy:.1f} L {sx:.1f} 166 A 6 6 0 0 0 {sx + 6:.1f} 172 L {dx - 6:.1f} 172 A 6 6 0 0 0 {dx:.1f} 166 L {dx:.1f} {dy:.1f}"
            parts.append(f'<path d="{p}" fill="none" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#qe-er-one)" marker-end="url(#qe-er-many)"/>')
        else:
            sx, sy = s["x"] + s["w"], s["y"] + s["h"] / 2.0
            dx, dy = d["x"], d["y"] + d["h"] / 2.0
            parts.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#qe-er-one)" marker-end="url(#qe-er-many)"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def compile_pipeline(spec: dict[str, Any]) -> str:
    """Compile multi-stage DAG data/prerequisite pipeline with orthogonal routed connectors."""
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    stages = spec.get("stages", [])
    if not nodes:
        return '<svg class="qe-svg qe-svg-720" viewBox="0 0 720 180" role="img" aria-label="Pipeline DAG"></svg>'

    by_stage: dict[int, list[dict[str, Any]]] = {}
    for nd in nodes:
        st = int(nd.get("stage", nd.get("col", 0)))
        by_stage.setdefault(st, []).append(nd)
    n_cols = max(by_stage.keys()) + 1
    max_rows = max(len(v) for v in by_stage.values())
    x0, y0 = 16.0, 40.0 if stages else 22.0
    col_step = 688.0 / max(n_cols, 1)
    nw = min(176.0, max(108.0, col_step - 24.0))
    row_step = 66.0
    nh = 46.0
    vb_h = int(y0 + max_rows * row_step + 14.0)

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Pipeline DAG"))}">',
        '<defs><marker id="qe-pipe-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--border-strong)"/></marker></defs>',
    ]
    for ci, st_lbl in enumerate(stages[:n_cols]):
        hx = x0 + ci * col_step + nw / 2.0
        parts.append(halo_text(hx, 22.0, str(st_lbl), anchor="middle", size=11.5, weight="700", font="var(--font-sans)", fill="var(--text-secondary)", halo=False))

    coords: dict[str, tuple[float, float, float, float]] = {}
    for st_idx, st_nodes in sorted(by_stage.items()):
        total_h = len(st_nodes) * row_step
        top_pad = (max_rows * row_step - total_h) / 2.0
        for ri, nd in enumerate(st_nodes):
            nx = float(nd.get("x")) if "x" in nd else (x0 + st_idx * col_step)
            ny = float(nd.get("y")) if "y" in nd else (y0 + top_pad + ri * row_step)
            coords[str(nd["id"])] = (nx, ny, nw, nh)

    for ed in edges:
        src, dst = coords.get(str(ed.get("from"))), coords.get(str(ed.get("to")))
        if not src or not dst:
            continue
        if abs(dst[0] - src[0]) < 1.0:
            vx = src[0] + src[2] / 2.0
            sy = src[1] + src[3] if dst[1] >= src[1] else src[1]
            dy = dst[1] - 2.0 if dst[1] >= src[1] else dst[1] + dst[3] + 2.0
            d = f"M {vx:.1f} {sy:.1f} V {dy:.1f}"
        else:
            sx, sy = src[0] + src[2], src[1] + src[3] / 2.0
            dx, dy = dst[0], dst[1] + dst[3] / 2.0
            mx = (sx + dx) / 2.0
            d = f"M {sx:.1f} {sy:.1f} H {mx:.1f} V {dy:.1f} H {dx - 2:.1f}"
        parts.append(f'<path d="{d}" fill="none" stroke="var(--border-strong)" stroke-width="1.4" marker-end="url(#qe-pipe-arr)"/>')

    for nd in nodes:
        nx, ny, w, h = coords[str(nd["id"])]
        focal = bool(nd.get("focal"))
        col = resolve_token(nd.get("stroke"), "var(--accent-focal)" if focal else "var(--border-strong)")
        bg = "var(--tint-indigo-bg)" if focal else "var(--bg-card)"
        parts.append(f'<rect data-role="node" x="{nx:.1f}" y="{ny:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="{bg}" stroke="{col}" stroke-width="1.5"/>')
        lbl = str(nd.get("label") or nd["id"])
        metric = str(nd.get("metric") or "")
        ty = ny + (18.0 if metric else 27.0)
        parts.append(halo_text(nx + w / 2.0, ty, lbl, anchor="middle", size=11.5, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        if metric:
            parts.append(halo_text(nx + w / 2.0, ny + 36.0, metric, anchor="middle", size=11.5, fill="var(--accent-focal)" if focal else "var(--text-secondary)", halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


def compile_interlock(spec: dict[str, Any]) -> str:
    """Compile safety voting interlock schematic (sensors -> 2oo3 voter -> final trip actuator + truth strip)."""
    sensors = spec.get("sensors") or []
    voter = spec.get("voter") or {"label": "2oo3 Safety Voter", "rule": "Trip if >= 2 Channels"}
    actuators = spec.get("actuators") or [{"label": "Shutoff Relay", "state": "DE-ENERGIZED"}]
    truth_rows = spec.get("truth_rows") or []
    vb_h = 276 if truth_rows else 222

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Safety Interlock Matrix"))}">',
        '<defs><marker id="qe-il-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--border-strong)"/></marker></defs>',
    ]
    vx, vy, vw, vh = 276.0, 52.0, 168.0, 96.0
    for idx, ch in enumerate(sensors[:4]):
        sy = 24.0 + idx * 54.0
        tripped = bool(ch.get("tripped"))
        sc = "var(--status-danger)" if tripped else "var(--status-ok)"
        bg = "var(--status-err-bg)" if tripped else "var(--bg-card)"
        parts.append(f'<rect data-role="node" x="24" y="{sy:.1f}" width="184" height="42" rx="4" fill="{bg}" stroke="{sc}" stroke-width="1.5"/>')
        parts.append(halo_text(116.0, sy + 17.0, str(ch.get("label") or f"CH-{idx+1}"), anchor="middle", size=11.5, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        parts.append(halo_text(116.0, sy + 33.0, str(ch.get("reading") or ("TRIP" if tripped else "ARMED")), anchor="middle", size=11.5, weight="600", fill=sc, halo=False))
        port_y = vy + 20.0 + idx * 28.0
        parts.append(f'<path d="M 208 {sy + 21:.1f} H 242 V {port_y:.1f} H {vx - 2:.1f}" fill="none" stroke="{sc if tripped else "var(--border-strong)"}" stroke-width="1.4" marker-end="url(#qe-il-arr)"/>')

    parts.append(f'<rect data-role="node" x="{vx:.1f}" y="{vy:.1f}" width="{vw:.1f}" height="{vh:.1f}" rx="6" fill="var(--tint-amber-bg)" stroke="var(--status-warn)" stroke-width="1.8"/>')
    parts.append(halo_text(vx + vw / 2.0, vy + 36.0, str(voter.get("label") or "2oo3 Voter"), anchor="middle", size=12.0, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
    parts.append(halo_text(vx + vw / 2.0, vy + 58.0, str(voter.get("rule") or "2-of-3 Majority"), anchor="middle", size=11.5, fill="var(--status-warn)", halo=False))
    if voter.get("decision"):
        parts.append(halo_text(vx + vw / 2.0, vy + 78.0, str(voter["decision"]), anchor="middle", size=11.5, weight="700", fill="var(--status-danger)", halo=False))

    for ai, act in enumerate(actuators[:2]):
        ay = 52.0 + ai * 62.0
        is_trip = bool(act.get("tripped"))
        ac = "var(--status-danger)" if is_trip else "var(--accent-focal)"
        parts.append(f'<path d="M {vx + vw:.1f} {vy + 32 + ai * 32:.1f} H 480 V {ay + 22:.1f} H 510" fill="none" stroke="{ac}" stroke-width="1.6" marker-end="url(#qe-il-arr)"/>')
        parts.append(f'<rect data-role="node" x="512" y="{ay:.1f}" width="184" height="44" rx="4" fill="var(--bg-card)" stroke="{ac}" stroke-width="1.6"/>')
        parts.append(halo_text(604.0, ay + 18.0, str(act.get("label") or "Actuator"), anchor="middle", size=11.5, weight="700", font="var(--font-sans)", fill="var(--text-primary)", halo=False))
        parts.append(halo_text(604.0, ay + 34.0, str(act.get("state") or "SAFE"), anchor="middle", size=11.5, weight="700", fill=ac, halo=False))

    if truth_rows:
        parts.append('<rect x="24" y="206" width="672" height="54" rx="4" fill="var(--bg-elevated)" stroke="var(--border-hairline)" stroke-width="1"/>')
        parts.append(halo_text(38.0, 224.0, "Truth Table:", anchor="start", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
        col_w = 520.0 / max(len(truth_rows), 1)
        for ti, tr in enumerate(truth_rows[:4]):
            tx = 150.0 + ti * col_w
            parts.append(halo_text(tx, 224.0, str(tr.get("pattern") or ""), anchor="start", size=11.5, fill="var(--text-secondary)", halo=False))
            tcol = "var(--status-danger)" if tr.get("trip") else "var(--status-ok)"
            parts.append(halo_text(tx, 245.0, str(tr.get("outcome") or ""), anchor="start", size=11.5, weight="700", fill=tcol, halo=False))

    parts.append("</svg>")
    return "\n".join(parts)

