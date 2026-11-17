# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 6 Routing: Enclaves, 78-ohm 1553B Bus & ISA P&ID."""

from __future__ import annotations

from typing import Any

from .tokens_and_scales import avoid_label_overlaps, esc, halo_text, pill_halo_text, resolve_term_colors, resolve_token


def _ortho_segments(p1: tuple[float, float], p2: tuple[float, float], mid_x: float | None = None) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Build orthogonal Manhattan segments from p1 to p2."""
    x1, y1 = p1
    x2, y2 = p2
    if abs(y1 - y2) < 0.5 or abs(x1 - x2) < 0.5:
        return [((x1, y1), (x2, y2))]
    mx = mid_x if mid_x is not None else (x1 + x2) / 2.0
    return [((x1, y1), (mx, y1)), ((mx, y1), (mx, y2)), ((mx, y2), (x2, y2))]


def _segments_to_svg_path(segs: list[tuple[tuple[float, float], tuple[float, float]]], verticals_other: list[tuple[float, float, float]]) -> str:
    """Convert orthogonal segments to SVG path with 5px bridge arcs over vertical crossings."""
    cmds: list[str] = []
    for idx, ((x1, y1), (x2, y2)) in enumerate(segs):
        if idx == 0:
            cmds.append(f"M {x1:.1f} {y1:.1f}")
        if abs(y1 - y2) < 0.5 and abs(x2 - x1) > 12.0:
            lo_x, hi_x = min(x1, x2), max(x1, x2)
            crossings = sorted({vx for vx, vy0, vy1 in verticals_other if lo_x + 6 < vx < hi_x - 6 and min(vy0, vy1) < y1 < max(vy0, vy1)})
            if crossings and x2 < x1:
                crossings.reverse()
            for vx in crossings:
                if x2 > x1:
                    cmds.append(f"L {vx - 5.0:.1f} {y1:.1f} A 5 5 0 0 1 {vx + 5.0:.1f} {y1:.1f}")
                else:
                    cmds.append(f"L {vx + 5.0:.1f} {y1:.1f} A 5 5 0 0 0 {vx - 5.0:.1f} {y1:.1f}")
        cmds.append(f"L {x2:.1f} {y2:.1f}")
    return " ".join(cmds)


def _resolve_enclaves(enclaves: list[dict[str, Any]], nodes: list[dict[str, Any]], node_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Partition and compute non-contaminating perimeter boxes for every enclave_id."""
    enc_list = [dict(e) for e in enclaves]
    known_ids = {e["id"] for e in enc_list if e.get("id")}
    for nd in nodes:
        eid = nd.get("enclave_id")
        if eid and eid not in known_ids:
            enc_list.append({"id": eid, "label": str(eid), "border_style": "dashed", "fill_token": "var(--bg-elevated)"})
            known_ids.add(eid)

    resolved: list[dict[str, Any]] = []
    for enc in enc_list:
        eid = enc.get("id")
        own = [node_map[n["id"]] for n in nodes if n.get("enclave_id") == eid]
        foreign = [node_map[n["id"]] for n in nodes if n.get("enclave_id") and n.get("enclave_id") != eid]
        has_box = all(k in enc for k in ("x", "y", "w", "h"))
        if has_box:
            ex, ey, ew, eh = float(enc["x"]), float(enc["y"]), float(enc["w"]), float(enc["h"])
            contaminated = any(fn["x"] + fn["w"] > ex and fn["x"] < ex + ew and fn["y"] + fn["h"] > ey and fn["y"] < ey + eh for fn in foreign)
        else:
            ex, ey, ew, eh, contaminated = 20.0, 24.0, 300.0, 260.0, True
        if (not has_box or contaminated) and own:
            ex = min(n["x"] for n in own) - 14.0
            ey = max(8.0, min(n["y"] for n in own) - 44.0)
            ew = max(n["x"] + n["w"] for n in own) + 14.0 - ex
            eh = max(n["y"] + n["h"] for n in own) + 14.0 - ey
        resolved.append({**enc, "x": ex, "y": ey, "w": ew, "h": eh})
    return resolved


def compile_topology_enclave(spec: dict[str, Any], rigor: str) -> str:
    """Compile Manhattan orthogonal topology or NIST Zero-Trust ATO Enclave map."""
    nodes, edges = spec.get("nodes", []), spec.get("edges", [])
    vb_w, vb_h = int(spec.get("width", 720)), int(spec.get("height", 330))

    node_map: dict[str, dict[str, float]] = {}
    for nd in nodes:
        node_map[nd["id"]] = {"x": float(nd.get("x", 40)), "y": float(nd.get("y", 70)), "w": float(nd.get("w", 156)), "h": float(nd.get("h", 58))}

    enclaves = _resolve_enclaves(spec.get("enclaves", []), nodes, node_map)
    if rigor in {"L2", "L3"} and enclaves:
        vb_h = max(vb_h, max(int(e["y"] + e["h"] + 16) for e in enclaves))

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 {vb_w} {vb_h}" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", "Topology"))}">',
        '<defs><marker id="qe-topo-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-primary)"/></marker>'
        '<marker id="qe-topo-focal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--accent-focal)"/></marker></defs>',
    ]
    if rigor in {"L2", "L3"}:
        for enc in enclaves:
            ex, ey, ew, eh = float(enc["x"]), float(enc["y"]), float(enc["w"]), float(enc["h"])
            dash = "6,3,2,3" if enc.get("border_style") == "dash-dot" else "5,4"
            fill = resolve_token(enc.get("fill_token"), "var(--bg-elevated)")
            parts.append(f'<rect x="{ex:.1f}" y="{ey:.1f}" width="{ew:.1f}" height="{eh:.1f}" rx="8" fill="{fill}" stroke="var(--border-strong)" stroke-width="1.4" stroke-dasharray="{dash}"/>')
            parts.append(halo_text(ex + 12.0, ey + 18.0, str(enc.get("label", "")), anchor="start", size=11.5, weight="700", fill="var(--text-primary)"))
            if enc.get("fips_level"):
                parts.append(halo_text(ex + 12.0, ey + 34.0, str(enc["fips_level"]), anchor="start", size=11.5, weight="600", fill="var(--accent-focal)"))

    routed: list[tuple[dict[str, Any], list[tuple[tuple[float, float], tuple[float, float]]]]] = []
    all_verts: list[tuple[int, float, float, float]] = []
    for ei, ed in enumerate(edges):
        s = node_map.get(str(ed.get("from", ed.get("from_port", ""))).split(":")[0])
        d = node_map.get(str(ed.get("to", ed.get("to_port", ""))).split(":")[0])
        if not s or not d:
            continue
        if s["x"] + s["w"] <= d["x"] + 2.0:
            segs = _ortho_segments((s["x"] + s["w"], s["y"] + s["h"] / 2.0), (d["x"], d["y"] + d["h"] / 2.0), ed.get("mid_x"))
        elif d["y"] >= s["y"] + s["h"] - 2.0:
            segs = _ortho_segments((s["x"] + s["w"] / 2.0, s["y"] + s["h"]), (d["x"] + d["w"] / 2.0, d["y"]), ed.get("mid_x"))
        else:
            s_cx, d_cx = s["x"] + s["w"] / 2.0, d["x"] + d["w"] / 2.0
            y_bot = min(vb_h - 14.0, max(s["y"] + s["h"], d["y"] + d["h"]) + 18.0)
            segs = [((s_cx, s["y"] + s["h"]), (s_cx, y_bot)), ((s_cx, y_bot), (d_cx, y_bot)), ((d_cx, y_bot), (d_cx, d["y"] + d["h"]))]
        routed.append((ed, segs))
        for (ax, ay), (bx, by) in segs:
            if abs(ax - bx) < 0.5:
                all_verts.append((ei, ax, ay, by))

    lbl_cands: list[dict[str, Any]] = []
    for ei, (ed, segs) in enumerate(routed):
        other_v = [(vx, vy0, vy1) for oi, vx, vy0, vy1 in all_verts if oi != ei]
        d_str = _segments_to_svg_path(segs, other_v)
        term = ed.get("term")
        col = resolve_token(ed.get("stroke_color"), resolve_term_colors(term)["fg"] if term else "var(--text-primary)")
        dash = ' stroke-dasharray="5,3"' if ed.get("style") == "dashed" else ""
        mk = "qe-topo-focal" if ed.get("crosses_enclave_boundary") else "qe-topo-arr"
        t_attr = f' data-term="{esc(term)}"' if term else ""
        parts.append(f'<path d="{d_str}" fill="none" stroke="{col}" stroke-width="1.6"{dash}{t_attr} marker-end="url(#{mk})"/>')
        raw_lbl = str(ed.get("label", ""))
        if raw_lbl and not (rigor == "L1" and raw_lbl.upper().startswith("PPSM")):
            mx = (segs[0][0][0] + segs[-1][1][0]) / 2.0
            my = (segs[0][0][1] + segs[-1][1][1]) / 2.0 + 4.0
            lbl_cands.append({"x": mx, "y": my, "text": raw_lbl, "anchor": "middle", "fill": col, "weight": "700", "border": col, "attrs": t_attr})

    for lbl in avoid_label_overlaps(lbl_cands, min_y=28.0, max_y=vb_h - 14.0):
        parts.append(pill_halo_text(lbl["x"], lbl["y"], lbl["text"], anchor=lbl["anchor"], size=11.5, weight=lbl["weight"], fill=lbl["fill"], border=lbl.get("border", "var(--border-hairline)"), x_bounds=(8.0, vb_w - 8.0), attrs=lbl.get("attrs", ""), math=False))

    for nd in nodes:
        b = node_map[nd["id"]]
        term = nd.get("term")
        t_attr = f' data-term="{esc(term)}"' if term else ""
        stroke = resolve_term_colors(term)["fg"] if term else ("var(--accent-focal)" if nd.get("focal") else "var(--border-strong)")
        parts.append(f'<rect x="{b["x"]:.1f}" y="{b["y"]:.1f}" width="{b["w"]:.1f}" height="{b["h"]:.1f}" rx="5" fill="var(--bg-card)" stroke="{stroke}" stroke-width="1.5"{t_attr}/>')
        parts.append(halo_text(b["x"] + b["w"] / 2.0, b["y"] + 24.0, str(nd["label"]), anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
        if nd.get("sublabel"):
            parts.append(halo_text(b["x"] + b["w"] / 2.0, b["y"] + 42.0, str(nd["sublabel"]), anchor="middle", size=11.5, fill="var(--text-muted)", halo=False))

    parts.append("</svg>")
    return "\n".join(parts)


def _resistor_zigzag(x: float, y: float, horiz: bool = True) -> str:
    """Emit crisp IEEE resistor symbol path with explicit fill=none."""
    if horiz:
        return f"M {x - 16:.1f} {y:.1f} L {x - 12:.1f} {y - 5:.1f} L {x - 6:.1f} {y + 5:.1f} L {x:.1f} {y - 5:.1f} L {x + 6:.1f} {y + 5:.1f} L {x + 12:.1f} {y - 5:.1f} L {x + 16:.1f} {y:.1f}"
    return f"M {x:.1f} {y - 12:.1f} L {x + 4:.1f} {y - 8:.1f} L {x - 4:.1f} {y - 4:.1f} L {x + 4:.1f} {y:.1f} L {x - 4:.1f} {y + 4:.1f} L {x + 4:.1f} {y + 8:.1f} L {x:.1f} {y + 12:.1f}"


_BUS_PROFILES: dict[str, dict[str, str]] = {
    "mil1553b": {"title": "MIL-STD-1553B DUAL-REDUNDANT 78 Ω TWINAXIAL BUS (TRANSFORMER-COUPLED)", "line_a": "BUS A", "line_b": "BUS B", "term": "78 Ω", "coupler": "58.5 Ω XFMR", "mode": "xfmr"},
    "can_fd": {"title": "SAE J1939 / ISO 11898 CAN-FD 120 Ω DIFFERENTIAL BUS (DIRECT STUB DROPS)", "line_a": "CAN_H", "line_b": "CAN_L", "term": "120 Ω", "coupler": "Stub ≤0.3 m", "mode": "diff"},
    "sae_j1939": {"title": "SAE J1939 / ISO 11898 CAN-FD 120 Ω DIFFERENTIAL BUS (DIRECT STUB DROPS)", "line_a": "CAN_H", "line_b": "CAN_L", "term": "120 Ω", "coupler": "Stub ≤0.3 m", "mode": "diff"},
    "rs485": {"title": "TIA-485 / MODBUS RTU 120 Ω DAISY-CHAIN BUS (FAILSAFE BIAS + EOL)", "line_a": "D+ (B)", "line_b": "D- (A)", "term": "120 Ω", "coupler": "560 Ω Bias", "mode": "diff"},
    "modbus": {"title": "TIA-485 / MODBUS RTU 120 Ω DAISY-CHAIN BUS (FAILSAFE BIAS + EOL)", "line_a": "D+ (B)", "line_b": "D- (A)", "term": "120 Ω", "coupler": "560 Ω Bias", "mode": "diff"},
}


def compile_differential_bus(spec: dict[str, Any]) -> str:
    """Compile L3 terminated differential fieldbus (78 Ω MIL-STD-1553B, 120 Ω CAN-FD, 120 Ω RS-485)."""
    std = str(spec.get("bus_standard", "mil1553b")).lower()
    prof = _BUS_PROFILES.get(std, _BUS_PROFILES["mil1553b"])
    terminals = spec.get("terminals", [])
    bx0, bx1, ya, yb, yc, yt = 124.0, 624.0, 58.0, 106.0, 168.0, 226.0
    slot = (bx1 - bx0 - 40.0) / max(len(terminals), 1)
    stub_a_xs = [bx0 + 20.0 + (i + 0.5) * slot - 18.0 for i in range(len(terminals))]
    drop_end_y = yc - 16.0 if prof["mode"] == "xfmr" else yt
    bus_b_path = _segments_to_svg_path([((bx0, yb), (bx1, yb))], [(xa, ya, drop_end_y) for xa in stub_a_xs])

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 310" role="img" aria-label="{esc(spec.get("metadata", {}).get("title", prof["title"]))}">',
        halo_text(360.0, 22.0, prof["title"], anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False),
        f'<line x1="{bx0}" y1="{ya}" x2="{bx1}" y2="{ya}" stroke="var(--accent-focal)" stroke-width="2.2"/>',
        f'<path d="{bus_b_path}" fill="none" stroke="var(--tint-violet-fg)" stroke-width="2.2"/>',
        halo_text(74.0, ya + 4.0, prof["line_a"], anchor="end", size=11.5, weight="700", fill="var(--accent-focal)", halo=False),
        halo_text(74.0, yb + 4.0, prof["line_b"], anchor="end", size=11.5, weight="700", fill="var(--tint-violet-fg)", halo=False),
    ]
    if prof["mode"] == "xfmr":
        for rx_end in (bx0 - 16.0, bx1 + 16.0):
            for ry, col in ((ya, "var(--accent-focal)"), (yb, "var(--tint-violet-fg)")):
                parts.append(f'<path d="{_resistor_zigzag(rx_end, ry, True)}" fill="none" stroke="{col}" stroke-width="1.5"/>')
                parts.append(halo_text(rx_end, ry - 10.0, prof["term"], anchor="middle", size=11.5, weight="700", fill="var(--text-primary)"))
    else:
        for rx_end in (bx0, bx1):
            mid_y = (ya + yb) / 2.0
            parts.append(f'<line x1="{rx_end}" y1="{ya}" x2="{rx_end}" y2="{mid_y - 12:.1f}" stroke="var(--text-primary)" stroke-width="1.5"/>')
            parts.append(f'<path d="{_resistor_zigzag(rx_end, mid_y, False)}" fill="none" stroke="var(--text-primary)" stroke-width="1.5"/>')
            parts.append(f'<line x1="{rx_end}" y1="{mid_y + 12:.1f}" x2="{rx_end}" y2="{yb}" stroke="var(--text-primary)" stroke-width="1.5"/>')
            parts.append(halo_text(rx_end + (-10.0 if rx_end == bx0 else 10.0), mid_y + 4.0, prof["term"], anchor="end" if rx_end == bx0 else "start", size=11.5, weight="700", fill="var(--text-primary)"))

    for i, term in enumerate(terminals):
        cx = bx0 + 20.0 + (i + 0.5) * slot
        xa, xb = cx - 18.0, cx + 18.0
        parts.append(f'<line x1="{xa:.1f}" y1="{ya}" x2="{xa:.1f}" y2="{drop_end_y:.1f}" stroke="var(--accent-focal)" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{xa:.1f}" cy="{ya}" r="3.2" fill="var(--text-primary)"/>')
        parts.append(f'<line x1="{xb:.1f}" y1="{yb}" x2="{xb:.1f}" y2="{drop_end_y:.1f}" stroke="var(--tint-violet-fg)" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{xb:.1f}" cy="{yb}" r="3.2" fill="var(--text-primary)"/>')

        if prof["mode"] == "xfmr":
            parts.append(f'<rect x="{cx - 46:.1f}" y="{yc - 16:.1f}" width="92" height="40" rx="4" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.2"/>')
            parts.append(f'<line x1="{xa:.1f}" y1="{yc - 12}" x2="{xa:.1f}" y2="{yc}" stroke="var(--accent-focal)" stroke-width="1.5" stroke-dasharray="2,2"/>')
            parts.append(f'<line x1="{xb:.1f}" y1="{yc - 12}" x2="{xb:.1f}" y2="{yc}" stroke="var(--tint-violet-fg)" stroke-width="1.5" stroke-dasharray="2,2"/>')
            parts.append(f'<line x1="{cx - 38:.1f}" y1="{yc + 2}" x2="{cx + 38:.1f}" y2="{yc + 2}" stroke="var(--border-hairline)" stroke-width="0.9"/>')
            parts.append(halo_text(cx, yc + 17.0, prof["coupler"], anchor="middle", size=11.5, weight="600", fill="var(--text-secondary)", halo=False))
            parts.append(f'<line x1="{xa:.1f}" y1="{yc + 24}" x2="{xa:.1f}" y2="{yt}" stroke="var(--accent-focal)" stroke-width="1.5"/>')
            parts.append(f'<line x1="{xb:.1f}" y1="{yc + 24}" x2="{xb:.1f}" y2="{yt}" stroke="var(--tint-violet-fg)" stroke-width="1.5"/>')
        else:
            parts.append(pill_halo_text(cx, yc + 4.0, prof["coupler"], anchor="middle", size=11.5, weight="600", fill="var(--text-secondary)", border="var(--border-hairline)", x_bounds=(8.0, 712.0), math=False))

        st_col = "var(--status-warn)" if term.get("status") == "warn" else ("var(--accent-focal)" if term.get("role") in {"BC", "MASTER", "ECU"} else "var(--border-strong)")
        parts.append(f'<rect x="{cx - 56:.1f}" y="{yt:.1f}" width="112" height="60" rx="5" fill="var(--bg-card)" stroke="{st_col}" stroke-width="1.6"/>')
        parts.append(halo_text(cx, yt + 24.0, str(term["label"]), anchor="middle", size=12.0, weight="700", fill="var(--text-primary)", halo=False))
        parts.append(halo_text(cx, yt + 43.0, str(term.get("sublabel", "")), anchor="middle", size=11.5, fill="var(--text-muted)", halo=False))
    parts.append("</svg>")
    return "\n".join(parts)


compile_mil1553b_bus = compile_differential_bus


def compile_pid_loop(spec: dict[str, Any], rigor: str = "L3") -> str:
    """Compile ISA-5.1 P&ID fluid/thermal control loop with instrument bubbles."""
    base = compile_topology_enclave(spec, rigor)
    if rigor == "L1":
        return base
    bubbles: list[str] = []
    for inst in spec.get("instruments", []):
        cx, cy = float(inst["x"]), float(inst["y"])
        col = resolve_token(inst.get("color"), "var(--accent-focal)")
        bubbles.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="20" fill="var(--bg-card)" stroke="{col}" stroke-width="1.5"/>')
        bubbles.append(f'<line x1="{cx - 20:.1f}" y1="{cy:.1f}" x2="{cx + 20:.1f}" y2="{cy:.1f}" stroke="{col}" stroke-width="1.0"/>')
        bubbles.append(halo_text(cx, cy - 4.0, str(inst.get("tag", "TT")), anchor="middle", size=11.5, weight="700", fill="var(--text-primary)", halo=False))
        bubbles.append(halo_text(cx, cy + 13.0, str(inst.get("loop", "101")), anchor="middle", size=11.5, fill=col, halo=False))
    return base.replace("</svg>", "".join(bubbles) + "</svg>") if bubbles else base
