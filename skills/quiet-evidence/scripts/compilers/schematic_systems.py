# SPDX-License-Identifier: Apache-2.0
"""Clean-room open-standards systems schematic compilers for Quiet Evidence v9.0.

Implements deterministic, theme-token-bound SVG generators for:
- sequence    (ITU-T Z.120 Timed Sequence Lifelines)
- n2_matrix   (NASA SP-2016-6105 N^2 Interface Matrix)
- fault_tree  (NRC NUREG-0492 Fault Tree Logic)
"""

from __future__ import annotations

import hashlib
import textwrap
from typing import Any

from .svg_labels import halo_text, svg_knockout_label
from .tokens_and_scales import esc, resolve_token


_TONE_COLOR: dict[str, str] = {
    "focal": "var(--accent-focal)",
    "ok": "var(--status-ok)",
    "warn": "var(--status-warn)",
    "err": "var(--status-err)",
    "muted": "var(--text-muted)",
    "neutral": "var(--border-strong)",
}

_TONE_FILL: dict[str, str] = {
    "focal": "var(--tint-indigo-bg)",
    "ok": "var(--status-ok-bg)",
    "warn": "var(--status-warn-bg)",
    "err": "var(--status-err-bg)",
    "muted": "var(--bg-elevated)",
    "neutral": "var(--bg-surface)",
}


def _short_uid(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:6]


def _tone_pair(tone: str | None) -> tuple[str, str]:
    key = (tone or "neutral").lower()
    stroke = _TONE_COLOR.get(key, "var(--border-strong)")
    fill = _TONE_FILL.get(key, "var(--bg-surface)")
    return stroke, fill


def _wrap_lines(label: str, max_chars: int, max_lines: int = 2) -> list[str]:
    wrapped = textwrap.wrap(str(label or "").strip(), width=max(8, max_chars))
    if not wrapped:
        return [""]
    if len(wrapped) > max_lines:
        tail = wrapped[max_lines - 1]
        wrapped = wrapped[:max_lines - 1] + [tail[: max(4, max_chars - 1)] + "…"]
    return wrapped


def _arrow_defs(uid: str) -> str:
    return (
        "<defs>"
        f'<marker id="seq-fill-{uid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 1 1 L 9 5 L 1 9 z" fill="context-stroke"/>'
        "</marker>"
        f'<marker id="seq-open-{uid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 2 1 L 8 5 L 2 9" fill="none" stroke="context-stroke" stroke-width="1.6"/>'
        "</marker>"
        "</defs>"
    )


def _draw_sequence_header_and_lifelines(
    parts: list[str],
    participants: list[dict[str, Any]],
    centers: dict[str, float],
    box_w: float,
    life_top: float,
    life_bot: float,
) -> None:
    for p in participants:
        pid = str(p["id"])
        cx = centers[pid]
        stroke, fill = _tone_pair(p.get("tone"))
        bx = cx - box_w / 2.0
        parts.append(
            f'<rect x="{bx:.1f}" y="16" width="{box_w:.1f}" height="44" rx="4" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
        )
        lines = _wrap_lines(str(p.get("label", pid)), max(10, int((box_w - 14) / 6.8)), 2)
        if len(lines) == 1:
            parts.append(halo_text(cx, 42.0, lines[0], anchor="middle", size=11.5, weight="600", font="var(--font-sans)", halo=False))
        else:
            parts.append(halo_text(cx, 33.5, lines[0], anchor="middle", size=11.5, weight="600", font="var(--font-sans)", halo=False))
            parts.append(halo_text(cx, 49.0, lines[1], anchor="middle", size=11.5, weight="500", fill="var(--text-secondary)", font="var(--font-sans)", halo=False))
        parts.append(
            f'<line x1="{cx:.1f}" y1="{life_top:.1f}" x2="{cx:.1f}" y2="{life_bot:.1f}" '
            'stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4 4"/>'
        )


def compile_sequence(spec: dict[str, Any]) -> str:
    """Compile ITU-T Z.120 Timed Sequence Lifelines schematic."""
    participants = spec.get("participants", [])
    messages = spec.get("messages", [])
    phases = spec.get("phases", [])
    uid = _short_uid(spec.get("title", "sequence"))
    n = max(len(participants), 1)
    left_margin = 94.0
    col_w = (706.0 - left_margin) / n
    box_w = min(132.0, col_w - 12.0)
    centers = {str(p["id"]): left_margin + (i + 0.5) * col_w for i, p in enumerate(participants)}

    row_step = 44.0
    msg_y0 = 108.0
    life_top = 60.0
    life_bot = msg_y0 + max(len(messages), 1) * row_step + 14.0
    vb_h = int(life_bot + 18)

    parts = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("title", "Sequence diagram"))}">',
        _arrow_defs(uid),
    ]
    for ph in phases:
        sr, er = int(ph.get("start_row", 0)), int(ph.get("end_row", 0))
        y1 = msg_y0 + sr * row_step - 34.0
        y2 = msg_y0 + er * row_step + 18.0
        stroke, fill = _tone_pair(ph.get("tone", "neutral"))
        parts.append(
            f'<rect x="12" y="{y1:.1f}" width="696" height="{max(32.0, y2 - y1):.1f}" rx="4" '
            f'fill="{fill}" fill-opacity="0.45" stroke="{stroke}" stroke-opacity="0.45" stroke-width="1"/>'
        )
        parts.append(halo_text(20.0, y1 + 14.0, str(ph.get("label", "")), anchor="start", size=11.5, weight="600", fill="var(--text-secondary)", font="var(--font-sans)", halo=False))

    _draw_sequence_header_and_lifelines(parts, participants, centers, box_w, life_top, life_bot)

    for idx, msg in enumerate(messages):
        y = msg_y0 + idx * row_step
        x1 = centers.get(str(msg.get("from")), left_margin + 40.0)
        x2 = centers.get(str(msg.get("to")), left_margin + 120.0)
        kind = str(msg.get("kind", "sync")).lower()
        stroke = _TONE_COLOR.get(str(msg.get("tone", "focal" if kind == "sync" else "neutral")), "var(--text-primary)")
        timing = str(msg.get("timing", ""))
        if timing:
            parts.append(halo_text(86.0, y + 4.0, timing, anchor="end", size=11.5, fill="var(--text-muted)", font="var(--font-mono)", halo=False))
        for aid in msg.get("active", []):
            if str(aid) in centers:
                ax = centers[str(aid)]
                parts.append(f'<rect x="{ax - 4.5:.1f}" y="{y - 10:.1f}" width="9" height="24" rx="2" fill="var(--bg-elevated)" stroke="var(--accent-focal)" stroke-width="1.2"/>')
        if abs(x2 - x1) < 2.0:
            parts.append(
                f'<path d="M {x1:.1f} {y - 6:.1f} H {x1 + 32:.1f} V {y + 10:.1f} H {x1 + 4:.1f}" '
                f'fill="none" stroke="{stroke}" stroke-width="1.5" marker-end="url(#seq-fill-{uid})"/>'
            )
            parts.append(svg_knockout_label(x1 + 38.0, y - 6.0, str(msg.get("label", "")), anchor="start", size=11.5, x_bounds=(left_margin, 708.0), math=False))
        else:
            dash = ' stroke-dasharray="5 3"' if kind == "reply" else ""
            marker = f"seq-open-{uid}" if kind in ("reply", "async") else f"seq-fill-{uid}"
            off1 = 5.0 if x2 > x1 else -5.0
            off2 = -5.0 if x2 > x1 else 5.0
            parts.append(f'<line x1="{x1 + off1:.1f}" y1="{y:.1f}" x2="{x2 + off2:.1f}" y2="{y:.1f}" stroke="{stroke}" stroke-width="1.6"{dash} marker-end="url(#{marker})"/>')
            parts.append(svg_knockout_label((x1 + x2) / 2.0, y - 9.0, str(msg.get("label", "")), anchor="middle", size=11.5, x_bounds=(left_margin - 4.0, 708.0), math=False))

    parts.append("</svg>")
    return "\n".join(parts)


def compile_n2_matrix(spec: dict[str, Any]) -> str:
    """Compile NASA SP-2016-6105 N^2 Interface Matrix schematic."""
    subs = spec.get("subsystems", [])
    interfaces = spec.get("interfaces", [])
    n = max(len(subs), 1)
    idx_map = {str(s["id"]): i for i, s in enumerate(subs)}

    x0, y0 = 28.0, 34.0
    cell_w = 664.0 / n
    cell_h = 56.0
    vb_h = int(y0 + n * cell_h + 24)

    parts = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 {vb_h}" role="img" aria-label="{esc(spec.get("title", "N2 interface matrix"))}">',
        halo_text(x0, 20.0, "NASA SP-2016-6105 N² Interface Matrix", anchor="start", size=11.5, weight="600", fill="var(--text-secondary)", font="var(--font-sans)", halo=False),
        halo_text(x0 + 664.0, 20.0, "Feedforward → Upper | Feedback ← Lower", anchor="end", size=11.5, fill="var(--text-muted)", font="var(--font-sans)", halo=False),
    ]
    for r in range(n + 1):
        ry = y0 + r * cell_h
        parts.append(f'<line x1="{x0:.1f}" y1="{ry:.1f}" x2="{x0 + 664:.1f}" y2="{ry:.1f}" stroke="var(--border-hairline)" stroke-width="1"/>')
    for c in range(n + 1):
        cx = x0 + c * cell_w
        parts.append(f'<line x1="{cx:.1f}" y1="{y0:.1f}" x2="{cx:.1f}" y2="{y0 + n * cell_h:.1f}" stroke="var(--border-hairline)" stroke-width="1"/>')

    for iface in interfaces:
        r = idx_map.get(str(iface.get("from")))
        c = idx_map.get(str(iface.get("to")))
        if r is None or c is None or r == c:
            continue
        stroke, fill = _tone_pair(iface.get("tone", "focal" if c > r else "neutral"))
        src_cx, src_cy = x0 + (r + 0.5) * cell_w, y0 + (r + 0.5) * cell_h
        mid_cx, mid_cy = x0 + (c + 0.5) * cell_w, y0 + (r + 0.5) * cell_h
        dst_cx, dst_cy = x0 + (c + 0.5) * cell_w, y0 + (c + 0.5) * cell_h
        parts.append(
            f'<path d="M {src_cx:.1f} {src_cy:.1f} H {mid_cx:.1f} V {dst_cy:.1f}" '
            f'fill="none" stroke="{stroke}" stroke-width="1.35" stroke-opacity="0.72"/>'
        )
        pw, ph = cell_w - 14.0, cell_h - 14.0
        parts.append(f'<rect x="{mid_cx - pw / 2:.1f}" y="{mid_cy - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        lines = _wrap_lines(str(iface.get("label", "")), max(9, int((pw - 10) / 6.7)), 2)
        if len(lines) == 1:
            parts.append(halo_text(mid_cx, mid_cy + 4.0, lines[0], anchor="middle", size=11.5, weight="500", font="var(--font-sans)", halo=False))
        else:
            parts.append(halo_text(mid_cx, mid_cy - 3.5, lines[0], anchor="middle", size=11.5, weight="500", font="var(--font-sans)", halo=False))
            parts.append(halo_text(mid_cx, mid_cy + 11.5, lines[1], anchor="middle", size=11.5, weight="500", font="var(--font-sans)", halo=False))

    for i, s in enumerate(subs):
        dx = x0 + i * cell_w + 5.0
        dy = y0 + i * cell_h + 5.0
        dw, dh = cell_w - 10.0, cell_h - 10.0
        stroke, fill = _tone_pair(s.get("tone", "focal"))
        parts.append(f'<rect x="{dx:.1f}" y="{dy:.1f}" width="{dw:.1f}" height="{dh:.1f}" rx="4" fill="var(--bg-elevated)" stroke="{stroke}" stroke-width="1.6"/>')
        lines = _wrap_lines(str(s.get("label", s["id"])), max(9, int((dw - 10) / 6.9)), 2)
        cx, cy = dx + dw / 2.0, dy + dh / 2.0
        if len(lines) == 1:
            parts.append(halo_text(cx, cy + 4.0, lines[0], anchor="middle", size=11.5, weight="700", font="var(--font-sans)", halo=False))
        else:
            parts.append(halo_text(cx, cy - 3.5, lines[0], anchor="middle", size=11.5, weight="700", font="var(--font-sans)", halo=False))
            parts.append(halo_text(cx, cy + 11.5, lines[1], anchor="middle", size=11.5, weight="700", font="var(--font-sans)", halo=False))

    parts.append("</svg>")
    return "\n".join(parts)


def _nrc_gate(cx: float, top_y: float, kind: str, stroke: str, fill: str) -> str:
    gate = (kind or "OR").upper()
    if gate == "AND":
        d = f"M {cx - 16:.1f} {top_y + 14:.1f} A 16 14 0 0 1 {cx + 16:.1f} {top_y + 14:.1f} L {cx + 16:.1f} {top_y + 28:.1f} H {cx - 16:.1f} Z"
    else:
        d = f"M {cx:.1f} {top_y:.1f} Q {cx + 16:.1f} {top_y + 8:.1f} {cx + 16:.1f} {top_y + 28:.1f} Q {cx:.1f} {top_y + 20:.1f} {cx - 16:.1f} {top_y + 28:.1f} Q {cx - 16:.1f} {top_y + 8:.1f} {cx:.1f} {top_y:.1f} Z"
    return (
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>'
        + halo_text(cx, top_y + 19.0, gate, anchor="middle", size=11.5, weight="700", font="var(--font-mono)", halo=False)
    )


def _draw_fault_leaf(parts: list[str], cx: float, gate_y: float, leaf: dict[str, Any], slot_w: float) -> None:
    leaf_y = gate_y + 28.0
    stroke, fill = _tone_pair(leaf.get("tone", "neutral"))
    kind = str(leaf.get("kind", "basic")).lower()
    parts.append(f'<line x1="{cx:.1f}" y1="{gate_y - 2:.1f}" x2="{cx:.1f}" y2="{leaf_y:.1f}" stroke="var(--border-strong)" stroke-width="1.3"/>')
    if kind == "undeveloped":
        cy = leaf_y + 15.0
        parts.append(f'<path d="M {cx:.1f} {leaf_y:.1f} L {cx + 18:.1f} {cy:.1f} L {cx:.1f} {cy + 15:.1f} L {cx - 18:.1f} {cy:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
        text_y = cy + 31.0
    else:
        cy = leaf_y + 15.0
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="15" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
        text_y = cy + 31.0
    lines = _wrap_lines(str(leaf.get("label", "")), max(10, int((slot_w - 10) / 6.8)), 2)
    for idx, ln in enumerate(lines):
        parts.append(halo_text(cx, text_y + idx * 14.5, ln, anchor="middle", size=11.5, font="var(--font-sans)", halo=False))
    if leaf.get("prob"):
        prob_y = text_y + len(lines) * 14.5 + 1.0
        parts.append(halo_text(cx, prob_y, str(leaf["prob"]), anchor="middle", size=11.5, fill="var(--text-muted)", font="var(--font-mono)", halo=False))


def compile_fault_tree(spec: dict[str, Any]) -> str:
    """Compile NRC NUREG-0492 Fault Tree Logic schematic."""
    top = spec.get("top_event", {})
    branches = spec.get("branches", [])
    total_leaves = sum(max(len(b.get("children", [])), 1) for b in branches)
    col_unit = 688.0 / max(total_leaves, 1)

    parts = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 720 356" role="img" aria-label="{esc(spec.get("title", "NRC NUREG-0492 Fault Tree"))}">',
        halo_text(18.0, 22.0, "NRC NUREG-0492 Fault Tree", anchor="start", size=11.5, weight="600", fill="var(--text-secondary)", font="var(--font-sans)", halo=False),
    ]
    top_stroke, top_fill = _tone_pair(top.get("tone", "err"))
    parts.append(f'<rect x="215" y="14" width="290" height="44" rx="4" fill="{top_fill}" stroke="{top_stroke}" stroke-width="1.5"/>')
    parts.append(halo_text(360.0, 34.0, str(top.get("label", "Top Event")), anchor="middle", size=11.5, weight="700", font="var(--font-sans)", halo=False))
    if top.get("prob"):
        parts.append(halo_text(360.0, 50.0, str(top["prob"]), anchor="middle", size=11.5, fill="var(--text-secondary)", font="var(--font-mono)", halo=False))
    parts.append('<line x1="360" y1="58" x2="360" y2="70" stroke="var(--border-strong)" stroke-width="1.4"/>')
    parts.append(_nrc_gate(360.0, 70.0, str(top.get("gate", "OR")), top_stroke, top_fill))
    parts.append('<line x1="360" y1="98" x2="360" y2="112" stroke="var(--border-strong)" stroke-width="1.4"/>')

    branch_xs: list[float] = []
    cursor = 0
    for br in branches:
        children = br.get("children", []) or [br]
        span = len(children)
        bx = 16.0 + (cursor + span / 2.0) * col_unit
        branch_xs.append(bx)
        bw = min(210.0, span * col_unit - 16.0)
        b_stroke, b_fill = _tone_pair(br.get("tone", "warn"))
        parts.append(f'<line x1="{bx:.1f}" y1="112" x2="{bx:.1f}" y2="124" stroke="var(--border-strong)" stroke-width="1.3"/>')
        parts.append(f'<rect x="{bx - bw / 2:.1f}" y="124" width="{bw:.1f}" height="42" rx="4" fill="{b_fill}" stroke="{b_stroke}" stroke-width="1.3"/>')
        blines = _wrap_lines(str(br.get("label", "")), max(12, int((bw - 12) / 6.8)), 2)
        if len(blines) == 1:
            parts.append(halo_text(bx, 149.0, blines[0], anchor="middle", size=11.5, weight="600", font="var(--font-sans)", halo=False))
        else:
            parts.append(halo_text(bx, 140.0, blines[0], anchor="middle", size=11.5, weight="600", font="var(--font-sans)", halo=False))
            parts.append(halo_text(bx, 156.0, blines[1], anchor="middle", size=11.5, font="var(--font-sans)", halo=False))
        parts.append(f'<line x1="{bx:.1f}" y1="166" x2="{bx:.1f}" y2="178" stroke="var(--border-strong)" stroke-width="1.3"/>')
        parts.append(_nrc_gate(bx, 178.0, str(br.get("gate", "OR")), b_stroke, b_fill))
        parts.append(f'<line x1="{bx:.1f}" y1="206" x2="{bx:.1f}" y2="218" stroke="var(--border-strong)" stroke-width="1.3"/>')

        leaf_xs: list[float] = []
        for j, ch in enumerate(br.get("children", [])):
            lx = 16.0 + (cursor + j + 0.5) * col_unit
            leaf_xs.append(lx)
            _draw_fault_leaf(parts, lx, 224.0, ch, col_unit)
        if leaf_xs:
            parts.append(f'<line x1="{min(leaf_xs):.1f}" y1="218" x2="{max(leaf_xs):.1f}" y2="218" stroke="var(--border-strong)" stroke-width="1.3"/>')
            for lx in leaf_xs:
                parts.append(f'<line x1="{lx:.1f}" y1="218" x2="{lx:.1f}" y2="224" stroke="var(--border-strong)" stroke-width="1.3"/>')
        cursor += span

    if len(branch_xs) >= 2:
        parts.append(f'<line x1="{min(branch_xs):.1f}" y1="112" x2="{max(branch_xs):.1f}" y2="112" stroke="var(--border-strong)" stroke-width="1.4"/>')
    parts.append("</svg>")
    return "\n".join(parts)
