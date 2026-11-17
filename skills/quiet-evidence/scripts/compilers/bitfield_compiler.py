# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 3 (Hardware Bitfields & Protocol Registers) Compiler."""

from __future__ import annotations

from typing import Any

from .tokens_and_scales import esc, halo_text

ACCESS_STYLE: dict[str, dict[str, str]] = {
    "RO": {"fill": "var(--bg-elevated)", "stroke": "var(--border-strong)", "dash": "none", "fg": "var(--text-primary)"},
    "RW": {"fill": "var(--tint-indigo-bg)", "stroke": "var(--accent-primary)", "dash": "none", "fg": "var(--tint-indigo-fg)"},
    "W1C": {"fill": "var(--tint-amber-bg)", "stroke": "var(--status-warn)", "dash": "4,3", "fg": "var(--tint-amber-fg)"},
    "RC": {"fill": "var(--tint-violet-bg)", "stroke": "var(--tint-violet-fg)", "dash": "2,2", "fg": "var(--tint-violet-fg)"},
    "WO": {"fill": "var(--tint-rose-bg)", "stroke": "var(--status-danger)", "dash": "none", "fg": "var(--tint-rose-fg)"},
}


def _parse_int(val: Any, default: int = 0) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        s = val.strip()
        try:
            return int(s, 16) if s.lower().startswith("0x") else int(s)
        except ValueError:
            return default
    return default


def _fit_field_label(name: str, short_name: str | None, width_px: float) -> str:
    """Select label that fits comfortably inside bit-span rectangle without overflowing."""
    if short_name and len(name) * 7.2 > width_px - 10:
        return short_name
    max_chars = max(2, int((width_px - 10) / 7.2))
    return name if len(name) <= max_chars else name[:max_chars]


def _extract_field_val(meta: dict[str, Any], f: dict[str, Any], cur_reg: int) -> tuple[int, int, int, int]:
    msb, lsb = int(f["bit_range"][0]), int(f["bit_range"][1])
    if msb < lsb:
        msb, lsb = lsb, msb
    lsb = max(0, lsb)
    width = msb - lsb + 1
    mask = (1 << width) - 1
    val = (cur_reg >> lsb) & mask if meta.get("current_value") is not None else _parse_int(f.get("current_value", 0))
    return msb, lsb, width, val


def _render_l1_overview(meta: dict[str, Any], fields: list[dict[str, Any]]) -> str:
    """Render L1 Orientation readiness pills decoded cleanly without register syntax."""
    cur_reg = _parse_int(meta.get("current_value", 0))
    pills: list[str] = []
    for f in fields:
        name = str(f.get("name", "FIELD"))
        if name.upper() == "RESERVED":
            continue
        _, _, _, cur = _extract_field_val(meta, f, cur_reg)
        label = name.replace("_", " ").title()
        is_fault = "FAULT" in name.upper() or "LOS" in name.upper() or "ERR" in name.upper()
        if is_fault:
            cls, state_txt = ("va-badge-err", f"{label}: FAULT") if cur > 0 else ("va-badge-ok", f"{label}: CLEAR")
        elif cur > 0:
            cls, state_txt = "va-badge-ok", f"{label}: ACTIVE ({cur})"
        else:
            cls, state_txt = "va-badge-neutral", f"{label}: INACTIVE"
        pills.append(f'<span class="va-badge {cls}">{esc(state_txt)}</span>')
    title = meta.get("title", "Subsystem Readiness")
    return (
        f'<div class="qe-bitfield-l1"><div class="qe-bf-hdr"><span class="va-kicker">SUBSYSTEM STATUS</span>'
        f'<span class="qe-bf-meta">{esc(title)}</span></div>'
        f'<div class="qe-bf-pill-row">{"".join(pills)}</div></div>'
    )


def _render_bit_strip_svg(meta: dict[str, Any], fields: list[dict[str, Any]], rigor: str) -> str:
    """Render 16-bit-per-row hardware bitfield SVG with exact bit index rulers."""
    width_bits = max(1, int(meta.get("register_width_bits", 32)))
    bits_per_row = 16 if width_bits >= 16 else width_bits
    num_rows = max(1, (width_bits + bits_per_row - 1) // bits_per_row)
    cur_reg = _parse_int(meta.get("current_value", 0))

    x0, cell_w = 40.0, 40.0
    row_pitch, box_top, box_h = 98.0, 22.0, 48.0
    vb_w = int(x0 * 2 + bits_per_row * cell_w)
    vb_h = int(18 + num_rows * row_pitch + 16)

    parts: list[str] = [
        f'<svg class="qe-svg qe-svg-720" viewBox="0 0 {vb_w} {vb_h}" role="img" '
        f'aria-label="{esc(meta.get("title", "Hardware Register Map"))}">'
    ]

    for r_idx in range(num_rows):
        msb_row = width_bits - 1 - r_idx * bits_per_row
        lsb_row = max(0, msb_row - bits_per_row + 1)
        ry = 14.0 + r_idx * row_pitch

        for col in range(bits_per_row):
            bit_idx = msb_row - col
            if bit_idx < lsb_row:
                break
            cx = x0 + col * cell_w
            parts.append(f'<rect x="{cx:.1f}" y="{ry:.1f}" width="{cell_w:.1f}" height="{box_top:.1f}" fill="var(--bg-header)" stroke="var(--border-hairline)" stroke-width="0.8"/>')
            parts.append(halo_text(cx + cell_w / 2.0, ry + 15.0, str(bit_idx), anchor="middle", size=11.5, weight="600", fill="var(--text-muted)", halo=False))

        for f in fields:
            f_msb, f_lsb, _, _ = _extract_field_val(meta, f, cur_reg)
            seg_msb = min(f_msb, msb_row)
            seg_lsb = max(f_lsb, lsb_row)
            if seg_msb < seg_lsb:
                continue
            col_start = msb_row - seg_msb
            span_bits = seg_msb - seg_lsb + 1
            fx = x0 + col_start * cell_w
            fw = span_bits * cell_w
            acc = str(f.get("access", "RO")).upper()
            st = ACCESS_STYLE.get(acc, ACCESS_STYLE["RO"])
            dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] != "none" else ""
            parts.append(f'<rect x="{fx:.1f}" y="{ry + box_top:.1f}" width="{fw:.1f}" height="{box_h:.1f}" fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="1.4"{dash}/>')

            lbl = _fit_field_label(str(f.get("name", "")), f.get("short_name"), fw)
            parts.append(halo_text(fx + fw / 2.0, ry + box_top + 20.0, lbl, anchor="middle", size=11.5, weight="700", fill=st["fg"], halo=False))
            parts.append(halo_text(fx + fw / 2.0, ry + box_top + 37.0, acc, anchor="middle", size=11.5, weight="500", fill="var(--text-secondary)", halo=False))

            if rigor == "L3":
                for b in range(seg_msb, seg_lsb - 1, -1):
                    b_col = msb_row - b
                    bx = x0 + b_col * cell_w + cell_w / 2.0
                    bit_val = (cur_reg >> b) & 1
                    bit_col = "var(--accent-focal)" if bit_val else "var(--text-muted)"
                    parts.append(halo_text(bx, ry + box_top + box_h + 15.0, str(bit_val), anchor="middle", size=11.5, weight="700" if bit_val else "400", fill=bit_col, halo=False))

    parts.append("</svg>")
    return "\n".join(parts)


def _render_decode_table(meta: dict[str, Any], fields: list[dict[str, Any]], rigor: str) -> str:
    """Render synchronized bit-decode table below hardware strip."""
    cur_reg = _parse_int(meta.get("current_value", 0))
    title = f'{meta.get("mnemonic", "Register")} Bit Decode Ledger'
    out: list[str] = [
        f'<div class="va-bleed-wide va-table-wrap" tabindex="0" role="region" aria-label="{esc(title)}">',
        '<table class="booktabs qe-table">',
        f'<caption class="qe-table-caption">{esc(title)}</caption>',
        '<thead><tr><th scope="col">Bits</th><th scope="col">Field</th><th scope="col">Access</th>'
        '<th scope="col" class="num">Reset</th><th scope="col" class="num">Value</th><th scope="col">Operational Decode</th></tr></thead><tbody>',
    ]
    for f in fields:
        msb, lsb, width, val = _extract_field_val(meta, f, cur_reg)
        span_str = f"[{msb}]" if msb == lsb else f"[{msb}:{lsb}]"
        val_fmt = f"0b{val:0{width}b} ({val})" if width <= 6 else f"0x{val:X} ({val})"
        rst = _parse_int(f.get("reset", 0))
        acc = str(f.get("access", "RO")).upper()
        note = str(f.get("description", "")) if rigor == "L3" else str(f.get("description", "")).split(".")[0]
        safety = ' <span class="va-badge va-badge-warn">INTERLOCK</span>' if f.get("safety_critical") else ""
        out.append(
            f'<tr><th scope="row" class="va-nums" data-label="Bits">{esc(span_str)}</th>'
            f'<td data-label="Field"><code>{esc(f.get("name", ""))}</code>{safety}</td>'
            f'<td data-label="Access"><span class="va-badge va-badge-neutral">{esc(acc)}</span></td>'
            f'<td class="num" data-label="Reset">0x{rst:X}</td>'
            f'<td class="num" data-label="Value">{esc(val_fmt)}</td>'
            f'<td data-label="Decode">{esc(note)}</td></tr>'
        )
    out.append("</tbody></table></div>")
    return "\n".join(out)


def _compile_single_register(meta: dict[str, Any], fields: list[dict[str, Any]], eff_rigor: str, medium: str) -> str:
    if eff_rigor == "L1":
        return _render_l1_overview(meta, fields)
    hdr_bits = [
        f'<span class="va-kicker">{esc(meta.get("mnemonic", "MMIO_REG"))}</span>',
        f'<span class="qe-bf-addr va-nums">Offset: {esc(meta.get("address_offset", "0x0000"))}</span>',
        f'<span class="qe-bf-addr va-nums">Reset: {esc(meta.get("reset_value", "0x0"))}</span>',
    ]
    if meta.get("current_value") is not None:
        hdr_bits.append(f'<span class="va-badge va-badge-ok va-nums">Live: {esc(meta["current_value"])}</span>')
    header = f'<div class="qe-bf-hdr">{"".join(hdr_bits)}</div>'
    svg = f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Register Strip"))}">{_render_bit_strip_svg(meta, fields, eff_rigor)}</div>'
    table = _render_decode_table(meta, fields, eff_rigor)
    return f'<div class="qe-bitfield-wrap" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}">{header}{svg}{table}</div>'


def compile_bitfield(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white") -> str:
    """Compile Modality 3 (urn:quiet-ui:schema:v9:bitfield) into semantic HTML/SVG."""
    meta = spec.get("metadata", {})
    eff_rigor = (rigor or meta.get("rigor_level", "L3")).upper()
    if spec.get("registers"):
        return "\n".join(
            _compile_single_register(r.get("metadata", meta), r.get("fields", []), eff_rigor, medium)
            for r in spec["registers"]
        )
    return _compile_single_register(meta, spec.get("fields", []), eff_rigor, medium)
