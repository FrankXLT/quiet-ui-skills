# SPDX-License-Identifier: Apache-2.0
"""Diverging % change + $ level matrix compiler and Takeaway Card export/table builder."""

from __future__ import annotations

import json
from typing import Any

from .tokens_and_scales import esc, finite_float


def _diverge_band(val: float | None, hi_thr: float = 5.0) -> str:
    """Map % change value into subtle WCAG-safe diverging band without flagging noise."""
    if val is None:
        return "flat"
    if val >= hi_thr:
        return "pos-hi"
    if val > 0.25:
        return "pos-lo"
    if val <= -hi_thr:
        return "neg-hi"
    if val < -0.25:
        return "neg-lo"
    return "flat"


def _cell_str(val: Any) -> str:
    return "—" if val is None or val == "" else str(val)


def _fmt_matrix_cell(raw: Any, col: dict[str, Any]) -> str:
    role = str(col.get("role") or col.get("data_type") or "").lower()
    if raw is None or raw == "":
        return "—"
    fv = finite_float(raw)
    if fv is None:
        return esc(raw)
    dec_raw = col.get("decimals")
    decimals = (1 if role == "rate_pct" else 0) if dec_raw is None else int(dec_raw)
    prefix = str(col.get("prefix") or ("$" if "usd" in role else ""))
    suffix = str(col.get("suffix") or ("%" if role == "rate_pct" else ""))
    if role == "rate_pct" and fv > 0:
        return esc(f"+{fv:,.{decimals}f}{suffix}")
    return esc(f"{prefix}{fv:,.{decimals}f}{suffix}")


def compile_diverging_matrix(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white", chrome: str = "bench") -> str:
    """Compile paired diverging % change + unshaded $ level comparison table with scroll cues."""
    meta = spec.get("metadata") or {}
    title = str(meta.get("title") or "Mobility & Distribution Matrix")
    cols = list(spec.get("columns") or [])
    rows = list(spec.get("rows") or [])
    hi_thr = finite_float(spec.get("diverging_threshold"), 5.0) or 5.0
    cohorts = list(spec.get("cohort_definitions") or [])

    parts: list[str] = []
    if cohorts:
        chips = "".join(
            f'<span class="va-cohort-item"><strong>{esc(c.get("label", ""))}</strong> {esc(c.get("range", ""))}</span>'
            for c in cohorts
        )
        parts.append(f'<div class="va-cohort-defs" role="note" aria-label="Cohort range definitions">{chips}</div>')

    hdr_id = esc(f"tbl-{meta.get('id', 'matrix')}")
    parts.append(f'<div class="va-table-region va-table-wrap qe-table-wrap va-diverging-scroll" tabindex="0" role="region" aria-label="{esc(title)}">')
    parts.append('<table class="booktabs qe-table va-diverging-matrix">')
    parts.append(f'<caption id="{hdr_id}" class="qe-table-caption qe-caption-sr">{esc(title)}</caption>')
    parts.append("<thead><tr>")
    for c in cols:
        role = str(c.get("role") or c.get("data_type") or "").lower()
        is_num = role in {"rate_pct", "level_usd", "numeric"} or c.get("alignment") == "right"
        parts.append(f'<th scope="col" class="{"num" if is_num else ""}" data-col-role="{esc(role)}">{esc(c.get("label") or c.get("key") or "")}</th>')
    parts.append("</tr></thead><tbody>")

    for row in rows:
        parts.append("<tr>")
        for idx, c in enumerate(cols):
            key = str(c.get("key") or "")
            role = str(c.get("role") or c.get("data_type") or "").lower()
            raw = row.get(key)
            cell_html = _fmt_matrix_cell(raw, c)
            is_num = role in {"rate_pct", "level_usd", "numeric"} or c.get("alignment") == "right"
            cls_list: list[str] = ["num"] if is_num else []
            div_attr = ""
            if role == "rate_pct":
                cls_list.append("va-cell-diverge")
                div_attr = f' data-diverge="{_diverge_band(finite_float(raw), hi_thr)}"'
            elif role in {"level_usd", "level"}:
                cls_list.append("va-cell-level")
            nowrap = ' data-nowrap="true"' if is_num else ""
            cls_attr = f' class="{" ".join(cls_list)}"' if cls_list else ""
            tag = "th" if idx == 0 else "td"
            scope = ' scope="row"' if idx == 0 else ""
            parts.append(f'<{tag}{scope}{cls_attr}{div_attr}{nowrap} data-label="{esc(c.get("label") or key)}">{cell_html}</{tag}>')
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    parts.append('<p class="va-scroll-cue" aria-hidden="true">Scroll table horizontally on compact screens — rate columns tinted, dollar levels unshaded.</p>')
    return "\n".join(parts)


def extract_table_model(spec: dict[str, Any]) -> tuple[list[str], list[list[str]]]:
    """Extract uniform (headers, rows) strings from any supported plot or table schema."""
    mod_cols = spec.get("columns")
    if isinstance(mod_cols, list) and isinstance(spec.get("rows"), list):
        headers = [str(c.get("label") or c.get("key") or "") for c in mod_cols]
        rows = [[_cell_str(r.get(str(c.get("key") or ""))) for c in mod_cols] for r in spec["rows"]]
        return headers, rows

    kind = str(spec.get("plot_kind") or "").lower()
    if kind == "us_hex_tile_map":
        raw_st = spec.get("states") or spec.get("items") or []
        unit = str(spec.get("unit") or "%").strip()
        items = [{"abbr": k, **(v if isinstance(v, dict) else {"value": v})} for k, v in raw_st.items()] if isinstance(raw_st, dict) else list(raw_st)
        headers = ["State", "Name", f"Value ({unit})"]
        rows = [[_cell_str(it.get("abbr")), _cell_str(it.get("name") or it.get("abbr")), _cell_str(it.get("value"))] for it in items]
        return headers, rows

    if kind in {"arrow_dumbbell", "dumbbell"}:
        s_lbl, e_lbl = str(spec.get("start_label") or "Start"), str(spec.get("end_label") or "Current")
        items = list(spec.get("items") or spec.get("series_items") or [])
        headers = ["Cohort / State", s_lbl, e_lbl, "Change", "Vintage Note"]
        rows = []
        for it in items:
            sv, ev = finite_float(it.get("start", it.get("min"))), finite_float(it.get("end", it.get("max")))
            delta = f"{ev - sv:+.1f}" if sv is not None and ev is not None else "—"
            rows.append([_cell_str(it.get("label")), _cell_str(sv), _cell_str(ev), delta, _cell_str(it.get("fallback_vintage") or "Current")])
        return headers, rows

    if kind == "paired_subgroup_bars":
        subs = list(spec.get("subgroups") or ["Group A", "Group B"])
        ov = str(spec.get("overall_label") or "Overall")
        headers = ["Category", str(subs[0]), str(subs[1] if len(subs) > 1 else "Group B"), ov]
        rows = [[_cell_str(g.get("label")), _cell_str(g.get("a")), _cell_str(g.get("b")), _cell_str(g.get("overall"))] for g in (spec.get("groups") or spec.get("items") or [])]
        return headers, rows

    if kind == "dual_slopegraph":
        t0, t1 = str(spec.get("start_label") or "Start"), str(spec.get("end_label") or "End")
        lu, ru = str(spec.get("left_unit") or "Count"), str(spec.get("right_unit") or "%")
        headers = ["Group", f"Count ({t0}, {lu})", f"Count ({t1}, {lu})", f"Share ({t0}, {ru})", f"Share ({t1}, {ru})"]
        rows = [[_cell_str(s.get("label")), _cell_str(s.get("left_start")), _cell_str(s.get("left_end")), _cell_str(s.get("right_start")), _cell_str(s.get("right_end"))] for s in (spec.get("series") or spec.get("items") or [])]
        return headers, rows

    series_list = list(spec.get("series") or [])
    if series_list:
        headers = ["Series", "X", "Y"]
        rows = [
            [_cell_str(sr.get("label") or sr.get("name") or sr.get("id") or "Series"), _cell_str(pt.get("x_label") if pt.get("x_label") is not None else pt.get("x")), _cell_str(pt.get("y"))]
            for sr in series_list
            for pt in (sr.get("data_points") or [])[:40]
        ]
        return headers, rows

    steps = list(spec.get("steps") or spec.get("items") or [])
    if steps:
        headers = ["Label", "Value"]
        rows = [[_cell_str(s.get("label")), _cell_str(s.get("value") if s.get("value") is not None else s.get("estimate"))] for s in steps]
        return headers, rows
    return [], []


def _tsv_cell(v: Any) -> str:
    return str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _md_cell(v: Any) -> str:
    return str(v).replace("|", "/").replace("\r", " ").replace("\n", " ")


def build_export_payload(spec: dict[str, Any], headers: list[str], rows: list[list[str]]) -> dict[str, Any]:
    """Build TSV spreadsheet data and structured Markdown Copy-for-AI brief."""
    meta = spec.get("metadata") or {}
    title = str(meta.get("title") or "Quiet Evidence Figure")
    subtitle = str(meta.get("subtitle") or "")
    note = str(meta.get("note") or spec.get("baseline_note") or "")
    source = str(meta.get("source") or meta.get("provenance") or "")

    tsv_lines = ["\t".join(_tsv_cell(h) for h in headers)] + ["\t".join(_tsv_cell(c) for c in r) for r in rows]
    md_parts = [f"### {title}"]
    if subtitle:
        md_parts.append(f"_{subtitle}_")
    if headers and rows:
        md_parts.append("")
        md_parts.append("| " + " | ".join(_md_cell(h) for h in headers) + " |")
        md_parts.append("| " + " | ".join("---" for _ in headers) + " |")
        for r in rows:
            md_parts.append("| " + " | ".join(_md_cell(c) for c in r) + " |")
    if note:
        md_parts.append(f"\n**Note:** {note}")
    if source:
        md_parts.append(f"**Source:** {source}")
    return {"title": title, "tsv": "\n".join(tsv_lines), "markdown": "\n".join(md_parts)}


def wrap_takeaway_card(spec: dict[str, Any], inner_html: str, modality: str, fig_id: str) -> str:
    """Wrap figure content with Takeaway subtitle, Chart/Table switcher, Copy for AI & Note/Source footer."""
    meta = spec.get("metadata") or {}
    subtitle = str(meta.get("subtitle") or "")
    note = str(meta.get("note") or spec.get("baseline_note") or "")
    source = str(meta.get("source") or meta.get("provenance") or "")
    want_takeaway = bool(spec.get("takeaway") or spec.get("takeaway_actions") or meta.get("subtitle") or meta.get("note") or meta.get("source"))
    if not want_takeaway:
        return inner_html

    safe_id = esc(fig_id)
    headers, rows = extract_table_model(spec)
    has_table_toggle = modality != "table" and bool(headers and rows)
    payload = build_export_payload(spec, headers, rows)
    safe_json = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")

    sub_html = f'<p class="qe-takeaway-subtitle">{esc(subtitle)}</p>' if subtitle else ""
    toggle_btns = ""
    if has_table_toggle:
        toggle_btns = (
            '<div class="va-toolbar-joined va-chart-table-switch" role="group" aria-label="View format">'
            f'<button type="button" class="va-seg-btn is-active" data-qe-view="chart" aria-pressed="true" aria-controls="{safe_id}-chart">Chart</button>'
            f'<button type="button" class="va-seg-btn" data-qe-view="table" aria-pressed="false" aria-controls="{safe_id}-table">Table</button>'
            "</div>"
        )
    actions_html = (
        f'<div class="va-card-actions" data-qe-card="{safe_id}">'
        f"{toggle_btns}"
        '<div class="va-copy-group">'
        '<button type="button" class="va-action-btn" data-qe-copy="tsv">Copy data</button>'
        '<button type="button" class="va-action-btn" data-qe-copy="ai">Copy for AI</button>'
        '<span class="va-copy-status qe-copy-status" role="status" aria-live="polite"></span>'
        "</div>"
        "</div>"
    )
    table_panel = ""
    if has_table_toggle:
        ths = "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
        trs = "".join(
            "<tr>" + "".join(
                f'<th scope="row">{esc(c)}</th>' if ci == 0 else f"<td>{esc(c)}</td>"
                for ci, c in enumerate(r)
            ) + "</tr>"
            for r in rows
        )
        table_panel = (
            f'<div class="va-card-table-panel va-table-wrap" id="{safe_id}-table" hidden="until-found" tabindex="0" role="region" aria-label="{esc(payload["title"])} data table">'
            f'<table class="booktabs qe-table"><caption>{esc(payload["title"])}</caption><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'
            "</div>"
        )

    footer_bits: list[str] = []
    if note:
        footer_bits.append(f'<p class="qe-takeaway-note"><strong>Note:</strong> {esc(note)}</p>')
    if source:
        footer_bits.append(f'<p class="qe-takeaway-source"><strong>Source:</strong> {esc(source)}</p>')
    footer_html = f'<footer class="qe-takeaway-footer">{"".join(footer_bits)}</footer>' if footer_bits else ""

    return (
        f"{sub_html}{actions_html}"
        f'<div class="va-card-chart-panel" id="{safe_id}-chart">{inner_html}</div>'
        f"{table_panel}{footer_html}"
        f'<script type="application/json" class="qe-export-payload">{safe_json}</script>'
    )
