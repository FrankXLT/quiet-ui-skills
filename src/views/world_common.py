#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 — Shared World Builder & Corpus Provenance Utilities."""

from __future__ import annotations

import copy
import html as _html
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
if str(EVIDENCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EVIDENCE_SCRIPTS))

from compile_evidence import compile_spec  # noqa: E402
from compilers.tokens_and_scales import esc, format_math_html  # noqa: E402
try:
    from rationale_formatter import (  # noqa: E402
        format_ledger_rows,
        format_vector_summary,
        humanize_rubric_title,
        scrub_prose,
    )
except ImportError:
    from src.views.rationale_formatter import (  # noqa: E402
        format_ledger_rows,
        format_vector_summary,
        humanize_rubric_title,
        scrub_prose,
    )

_INV_TOKENS = (("Baseline", "baseline"), ("Provenance", "provenance"), ("Margin", "margin"), ("Disposition", "disposition"))


def embed_compile(spec: dict[str, Any], rigor: str, medium: str) -> str:
    """Compile a v9 evidence JSON spec cleanly for embedded stage placement."""
    return compile_spec(spec, rigor=rigor, medium=medium, theme="white", include_spec_drawer=False, chrome="embedded")


def slice_schematic_panel(
    spec: dict[str, Any], panel_idx: int, new_id: str | None = None,
    title: str | None = None, description: str | None = None,
) -> dict[str, Any]:
    """Return a deep-copied schematic spec restricted to a single panel."""
    out = copy.deepcopy(spec)
    panels = list(out.get("panels") or [])
    if 0 <= panel_idx < len(panels):
        out["panels"] = [panels[panel_idx]]
    if new_id:
        out["id"] = new_id
    meta = dict(out.get("metadata") or {})
    if title:
        meta["title"] = title
    if description:
        meta["description"] = description
    if meta:
        out["metadata"] = meta
    return out


def inject_fig_class(fig_html: str, extra_cls: str) -> str:
    """Append view-specific CSS class to the first embedded evidence figure card."""
    return fig_html.replace('class="va-figure-card qe-figure"', f'class="va-figure-card qe-figure {extra_cls}"', 1)


def cm_val(cm: dict[str, Any], key: str) -> Any:
    """Extract scalar or nested .value entry from corpus canonical_metrics."""
    raw = cm[key]
    return raw["value"] if isinstance(raw, dict) and "value" in raw else raw


def _clean_md(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text.replace("`", "").replace("**", "")).strip()


def _parse_blueprint_prose(md_text: str) -> dict[str, Any]:
    """Extract bulleted Bias and numbered 4-Invariant blocks from non-tabular blueprints."""
    sections: dict[str, str] = {}
    cur_sec, buf = "", []
    for raw in md_text.splitlines():
        if raw.startswith("## "):
            if cur_sec:
                sections[cur_sec] = "\n".join(buf)
            cur_sec, buf = raw[3:].strip(), []
        elif cur_sec:
            buf.append(raw)
    if cur_sec:
        sections[cur_sec] = "\n".join(buf)

    bias_prose: dict[str, dict[str, str]] = {}
    inv_prose: dict[str, dict[str, str]] = {}
    for heading, body in sections.items():
        low = heading.lower()
        if "bias" in low:
            cur_vid = ""
            for raw in body.splitlines():
                hm = re.match(r"^-\s+\*\*(?:From\s+)?`?([a-z0-9-]+)`?", raw.strip())
                if hm:
                    cur_vid = hm.group(1)
                    for key in (cur_vid, cur_vid.split("-")[0]):
                        bias_prose.setdefault(key, {})
                    continue
                if cur_vid:
                    sm = re.match(r"^\s*-\s+\*(Scrubbed|Retained|Risk)\*:\s*(.+)$", raw)
                    if sm:
                        field = {"Scrubbed": "removed", "Retained": "replacement", "Risk": "risk"}[sm.group(1)]
                        for key in (cur_vid, cur_vid.split("-")[0]):
                            bias_prose[key][field] = _clean_md(sm.group(2))
        elif "invariant" in low:
            cur_inv = ""
            for raw in body.splitlines():
                im = re.match(r"^\d+\.\s+\*\*([^*]+)\*\*[:\s]*(.*)$", raw.strip())
                if im:
                    cur_inv = next((dst for tok, dst in _INV_TOKENS if tok in im.group(1)), "")
                    if cur_inv and im.group(2).strip():
                        inv_prose.setdefault("_shared", {})[cur_inv] = _clean_md(im.group(2))
                    continue
                if cur_inv:
                    bm = re.match(r"^\s+-\s+([^:]+):\s*(.+)$", raw)
                    if bm:
                        for vtag in re.findall(r"\bv\d{2}\b", bm.group(1)):
                            inv_prose.setdefault(vtag, {})[cur_inv] = _clean_md(bm.group(2))
    return {"bias": bias_prose, "invariants": inv_prose}


def parse_blueprint_tables(md_text: str) -> dict[str, Any]:
    """Parse markdown tables and prose Bias/Invariant blocks from distillation_blueprint.md."""
    sections: dict[str, Any] = {}
    cur_sec, headers = "", []
    for raw in md_text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            cur_sec, headers = line[3:].strip(), []
            sections[cur_sec] = []
        elif line.startswith("|") and cur_sec:
            cells = [c.strip().replace("`", "").replace("**", "") for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                continue
            if not headers:
                headers = cells
            elif len(cells) == len(headers):
                sections[cur_sec].append(dict(zip(headers, cells)))
    sections["__prose__"] = _parse_blueprint_prose(md_text)
    return sections


def load_world_inputs(
    corpora_dir: Path, world_slug: str, spec_files: dict[str, str]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    """Load corpus JSON, parsed distillation blueprint sections, and evidence spec dicts."""
    wdir = corpora_dir / world_slug
    corpus = json.loads((wdir / "corpus.json").read_text(encoding="utf-8"))
    bp = parse_blueprint_tables((wdir / "distillation_blueprint.md").read_text(encoding="utf-8"))
    specs = {k: json.loads((wdir / "evidence" / fn).read_text(encoding="utf-8")) for k, fn in spec_files.items()}
    return corpus, bp, specs


def render_params_aside(title: str, rows: list[tuple[str, str]], math_keys: tuple[str, ...] = ()) -> str:
    """Render an M2 desktop right-margin parameters aside (unboxed automatically in M1/print)."""
    stitle = _html.escape(str(title), quote=True)
    math_set = set(math_keys)
    items = "".join(
        f'<div class="v9-param-row"><dt>{_html.escape(str(k))}</dt><dd class="va-nums">{format_math_html(str(v)) if k in math_set else _html.escape(str(v))}</dd></div>'
        for k, v in rows
    )
    return f'<aside class="v9-params-aside" aria-label="{stitle}"><h3>{stitle}</h3><dl class="v9-params-list">{items}</dl></aside>'


def _find_section_rows(bp: dict[str, Any], keyword: str) -> list[dict[str, str]]:
    for heading, rows in bp.items():
        if heading != "__prose__" and keyword.lower() in heading.lower() and isinstance(rows, list) and rows:
            return rows
    return []


def _extract_ledger_rows(bp: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for r in _find_section_rows(bp, "Conservation Ledger"):
        out.append({
            "metric_id": r.get("metric_id") or r.get("Conserved Key") or r.get("Canonical Metric ID") or r.get("Canonical Metric Key") or r.get("Metric Key") or "",
            "canonical_value": r.get("Canonical Value") or r.get("Conserved Value") or "",
            "unit": r.get("Unit") or r.get("SI / Protocol Unit") or "",
            "views": r.get("Views Consuming") or r.get("Views Consuming Key") or r.get("Conserved Across Views") or r.get("Bound Evidence Files") or r.get("Bound Evidence File(s)") or "",
        })
    return out


def _format_disposition(vw: dict[str, Any], cfg: dict[str, Any]) -> str:
    if vw.get("actionable_disposition"):
        return str(vw["actionable_disposition"])
    gate = vw.get("decision_gate")
    if isinstance(gate, dict):
        return f'{gate.get("status", "NOMINAL")}: {gate.get("primary_margin", "")} — {gate.get("bounded_action", "")}'.strip(" —")
    return str(cfg.get("actionable_disposition", ""))


def assemble_world_bundle(
    corpus: dict[str, Any], bp: dict[str, Any], world_label: str,
    view_cfg: dict[str, dict[str, Any]], html_map: dict[str, str],
) -> dict[str, Any]:
    """Package compiled view templates and Quiet-Bridge provenance metadata for a world."""
    bias_rows = _find_section_rows(bp, "Bias")
    bias_by_id = {r.get("View ID", ""): r for r in bias_rows if r.get("View ID")}
    prose = bp.get("__prose__", {})
    inv_rows, mb_rows, ledger_rows = _find_section_rows(bp, "Invariant"), _find_section_rows(bp, "Murder-Board"), _extract_ledger_rows(bp)
    views_meta: list[dict[str, Any]] = []
    templates: dict[str, str] = {}
    for vw in corpus["views"]:
        vid = vw.get("view_id") or vw.get("id") or ""
        cfg = view_cfg[vid]
        short_tag, inv_col = cfg["short_tag"], cfg["inv_col"]
        bias = bias_by_id.get(vid) or bias_by_id.get(short_tag) or {}
        pb = prose.get("bias", {}).get(vid) or prose.get("bias", {}).get(short_tag) or {}
        inv_dict: dict[str, str] = dict(prose.get("invariants", {}).get("_shared", {}))
        inv_dict.update(prose.get("invariants", {}).get(short_tag, {}))
        for row in inv_rows:
            inv_label = row.get("Invariant") or next(iter(row.values()), "")
            val = row.get(inv_col) or row.get(vid) or row.get(short_tag) or ""
            for token, dst in _INV_TOKENS:
                if token in inv_label and val:
                    inv_dict[dst] = val
        for dst, val in cfg.get("invariants_fallback", {}).items():
            if dst in {"baseline", "provenance", "margin", "disposition"} and not inv_dict.get(dst):
                inv_dict[dst] = val

        mb_list: list[dict[str, str]] = []
        mb_kw = tuple(cfg.get("mb_keywords") or (short_tag, vid))
        for r in mb_rows:
            scope = r.get("Audited View(s)") or r.get("View ID") or r.get("Target View(s)") or r.get("Target Scope") or ""
            rubric = r.get("Rubric / Persona") or r.get("Applicable Rubric & Trigger") or r.get("Audit Gate / Trigger") or r.get("Audit Gate / Rubric ID") or r.get("Audit Sector") or ""
            finding = r.get("Audit Finding") or r.get("Audited Condition") or r.get("Verification Evidence & Disposition") or r.get("Observed Evidence & Status") or r.get("Verified Evidence & Hard-Block Clearance") or ""
            in_scope = (short_tag in scope or vid in scope or scope == "All") if scope else (
                any(k in finding or k in rubric for k in mb_kw) or not re.search(r"\bv\d{2}\b", finding)
            )
            if in_scope:
                clean_finding = scrub_prose(finding)
                mb_list.append({
                    "rubric": humanize_rubric_title(rubric, clean_finding),
                    "finding": clean_finding,
                    "verdict": scrub_prose(r.get("Verdict") or r.get("Status") or r.get("Disposition") or "PASS"),
                })
        clean_inv = {k: scrub_prose(v) for k, v in inv_dict.items()}
        views_meta.append({
            "view_id": vid, "title": scrub_prose(vw["title"]), "option_label": cfg["option_label"],
            "default_medium": cfg["default_medium"], "chromatic_code": cfg["chromatic_code"],
            "default_nav": cfg["default_nav"], "allowed_navs": cfg["allowed_navs"],
            "nav_icon": cfg["nav_icon"], "nav_brand": cfg["nav_brand"], "topbar_brand": cfg["topbar_brand"],
            "rail_brand": cfg["rail_brand"], "topbar_status": cfg["topbar_status"],
            "nav_items": cfg["nav_items"], "nav_anchors": cfg["nav_anchors"],
            "vector_summary": format_vector_summary(vw),
            "actionable_disposition": scrub_prose(_format_disposition(vw, cfg)),
            "bias_removed": scrub_prose(bias.get("Presenter Bias Identified") or bias.get("Habitual Presenter Bias") or pb.get("removed") or cfg.get("bias_removed", "")),
            "bias_risk": scrub_prose(bias.get("Risk to Target Audience") or pb.get("risk") or cfg.get("bias_risk", "")),
            "bias_replacement": scrub_prose(bias.get("Scrubbed / Distilled Replacement") or bias.get("Quiet Bridge Scrub Directive") or bias.get("Receiver Scrub Rule Applied") or pb.get("replacement") or cfg.get("bias_replacement", "")),
            "invariants": clean_inv, "murder_board": mb_list,
        })
        templates[vid] = html_map[vid]
    return {
        "world_meta": {"world_id": corpus["world_id"], "world_label": world_label, "title": scrub_prose(corpus["title"]), "views": views_meta, "conservation_ledger": format_ledger_rows(ledger_rows)},
        "templates": templates,
    }


def render_alarm_console_open(cfg: dict[str, Any], initial_phase: str = "nominal", takeover_label: str = "Active Unacknowledged Alarm Takeover") -> str:
    """Open reusable 4-phase ISA-18.2 alarm lifecycle host wrapper and balanced body slot."""
    cfg_attr = esc(json.dumps(cfg, separators=(",", ":")))
    return (
        f'<div class="va-alarm-console" data-alarm-config="{cfg_attr}" data-alarm-phase="{esc(initial_phase)}">'
        '<div class="va-sr-only va-alarm-live" aria-live="polite" aria-atomic="true"></div>'
        '<div class="va-alarm-banner" data-alarm-banner></div>'
        f'<section class="va-alarm-takeover" data-alarm-takeover aria-label="{esc(takeover_label)}"></section>'
        '<div class="va-alarm-balanced-wrap" data-alarm-balanced>'
    )


def render_alarm_console_close() -> str:
    """Close reusable 4-phase ISA-18.2 alarm lifecycle host wrapper."""
    return "</div></div>"


def render_handoff_link(world_id: str, view_id: str, label: str) -> str:
    """Render an accessible cross-view handoff navigation pill for Studio and standalone frames."""
    href = f"?world={esc(quote(str(world_id), safe=''))}&amp;view={esc(quote(str(view_id), safe=''))}"
    return (
        f'<a class="va-handoff-link" href="{href}" '
        f'data-quiet-handoff-world="{esc(world_id)}" data-quiet-handoff-view="{esc(view_id)}">'
        f"{esc(label)}</a>"
    )

