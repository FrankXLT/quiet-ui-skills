"""Quiet UI v9.7.0 Wave 2 — Bench Specimens 51-53 (Diff Gate, Triage Inspector, Trade-Space)."""
from __future__ import annotations

import html
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bench_data_contracts import contract_for_ui_specimen
from src.views.world_wave2_infra_calc import _v26_chart_svg, compute_v26_model
from src.views.world_wave2_ops import build_v23_table_rows, generate_v24_events


def _wrap_specimen(spec_id: str, schema_mod: str, kicker: str, title: str, badge: str, rigor: str, desc: str, body: str) -> str:
    contract = contract_for_ui_specimen(schema_mod)
    return (
        f'<article class="qe-specimen qe-specimen-wide" data-modality="UI" '
        f'data-schema-modality="{schema_mod}" data-rigor="{rigor}">'
        f'<div class="va-card qe-bench-card" id="{spec_id}">'
        '<div class="qe-fig-hdr"><div>'
        f'<div class="qe-fig-kicker">{kicker}</div>'
        f'<h2 class="qe-fig-title">{title}</h2></div>'
        f'<div class="qe-fig-badges"><span class="va-pill" data-variant="tag">{badge}</span></div></div>'
        f'<p class="qe-fig-desc">{desc}</p>'
        f'<div class="qe-bench-body">{body}</div>'
        f'{contract}</div></article>'
    )


def _specimen_51_diff_gate() -> str:
    body = (
        '<div class="w2-stack" data-v23-scope="bench" data-v23-phase="baseline">'
        '<div class="w2-toolbar" role="region" aria-label="Specimen 51 diff filters">'
        '<div class="w2-btn-group">'
        '<button type="button" class="w2-filter-btn" data-v23-filter="all" aria-pressed="true">All Changes (6)</button>'
        '<button type="button" class="w2-filter-btn" data-v23-filter="security" aria-pressed="false">Security (3)</button>'
        '<button type="button" class="w2-filter-btn" data-v23-filter="capacity" aria-pressed="false">Capacity (3)</button>'
        '</div>'
        '<label class="w2-check-lbl" for="s51-ctx-toggle">'
        '<input type="checkbox" id="s51-ctx-toggle" data-v23-context/>'
        '<span>Show unchanged context (6)</span></label>'
        '<span class="va-pill" data-variant="status" data-state="nominal" data-v23-pill>BASELINE r41</span></div>'
        '<div class="va-table-wrap w2-table-wrap"><table class="w2-table" aria-label="Specimen 51 parameter diff table">'
        '<thead><tr><th>Parameter Key</th><th>Baseline r41</th><th>Candidate r42</th>'
        '<th>Policy Impact</th><th>Clusters</th><th>Risk</th></tr></thead>'
        f'<tbody data-v23-tbody>{build_v23_table_rows()}</tbody></table></div>'
        '<div class="w2-promote-bar">'
        '<div class="w2-gate-meta"><span class="w2-gate-status-line" data-v23-gate-status>Baseline r41 active — 1-click r41 revert pre-armed</span></div>'
        '<div class="w2-btn-group w2-gate-actions">'
        '<button type="button" class="w2-action-btn" data-tone="primary" data-v23-stage>1. Stage r42 Canary</button>'
        '<button type="button" class="w2-action-btn" data-v23-confirm disabled>2. Confirm Promotion</button>'
        '<button type="button" class="w2-action-btn" data-v23-revert disabled>Revert to r41</button>'
        '</div></div>'
        '<div class="va-undo-toast" data-v23-toast hidden role="status" aria-live="polite">'
        '<span>Promoted r42 across 14 clusters.</span>'
        '<button type="button" class="w2-action-btn" data-v23-toast-revert>Undo to r41</button></div></div>'
    )
    return _wrap_specimen(
        "ui-semantic-diff-gate", "ui-semantic-diff-gate",
        "PILLAR 1 · WAVE 2 · SEMANTIC PARAMETER DIFF",
        "Semantic Parameter Diff &amp; Two-Step Rollout Gate",
        "UI · Reversible Gate", "L2",
        "Structured before/after config diff highlighting breaking pinning risks, optional unchanged context rows, and a two-step reversible rollout bar.",
        body,
    )


def _pick_s52_events() -> list[dict[str, str]]:
    all_ev = generate_v24_events()
    quotas = {"critical": 3, "warning": 4, "auth_tls": 2, "nominal": 3}
    counts = {k: 0 for k in quotas}
    picked: list[dict[str, str]] = []
    for ev in all_ev:
        cat = ev["cat"]
        if counts[cat] < quotas[cat]:
            picked.append(ev)
            counts[cat] += 1
    return picked


def _specimen_52_triage() -> str:
    rows = _pick_s52_events()
    first = rows[0]
    trs = []
    for i, ev in enumerate(rows):
        st = "fault" if ev["sev"] == "CRITICAL" else ("warn" if ev["sev"] == "WARN" else "nominal")
        trs.append(
            f'<tr class="v24-row" tabindex="0" aria-selected="{"true" if i == 0 else "false"}" '
            f'data-v24-cat="{ev["cat"]}" data-v24-bucket="{ev["bucket"]}" '
            f'data-v24-search="{html.escape((ev["svc"] + " " + ev["span"] + " " + ev["trace"] + " " + ev["msg"]).lower())}" '
            f'data-ev-ts="{ev["ts"]}" data-ev-svc="{ev["svc"]}" data-ev-span="{ev["span"]}" '
            f'data-ev-trace="{ev["trace"]}" data-ev-dur="{ev["dur"]}" data-ev-sev="{ev["sev"]}" '
            f'data-ev-caller="{ev["caller"]}" data-ev-code="{ev["code"]}" data-ev-msg="{html.escape(ev["msg"])}">'
            f'<td class="w2-num">{ev["ts"]}</td><td><code class="w2-code">{ev["svc"]}</code></td>'
            f'<td class="w2-num">{ev["span"]}</td><td class="w2-num">{ev["dur"]}</td>'
            f'<td><span class="va-pill" data-variant="tag" data-state="{st}">{ev["sev"]}</span></td>'
            f'<td>{html.escape(ev["msg"])}</td></tr>'
        )
    body = (
        '<div class="w2-stack" data-v24-scope="bench">'
        '<div class="w2-toolbar" role="region" aria-label="Specimen 52 log filters">'
        '<div class="w2-btn-group">'
        '<button type="button" class="w2-filter-btn" data-v24-filter="all" aria-pressed="true">All (12)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="critical" aria-pressed="false">Critical (3)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="warning" aria-pressed="false">Warnings (4)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="auth_tls" aria-pressed="false">Auth &amp; TLS (2)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="nominal" aria-pressed="false">Nominal (3)</button>'
        '</div>'
        '<div class="w2-search-wrap">'
        '<label class="w2-search-lbl" for="s52-search-input">Search stream</label>'
        '<input type="search" id="s52-search-input" class="w2-search-input" placeholder="Service, span, trace..." data-v24-search/>'
        '</div><span class="w2-num" data-v24-visible-count>Showing 12 / 12 events</span></div>'
        '<div class="v24-split">'
        '<div class="va-table-wrap w2-table-wrap v24-table-scroll">'
        '<table class="w2-table" data-v24-table aria-label="Specimen 52 log stream">'
        '<thead><tr><th>UTC</th><th>Service</th><th>Span</th><th>Dur.</th><th>Level</th><th>Summary</th></tr></thead>'
        f'<tbody data-v24-tbody>{"".join(trs)}</tbody></table>'
        '<div class="va-empty-state" data-kind="filtered" data-v24-empty hidden>'
        '<p><strong>No matching events</strong> found for the current query.</p>'
        '<button type="button" class="w2-action-btn" data-tone="primary" data-v24-clear>Clear filters</button>'
        '</div></div>'
        '<aside class="w2-inspector" aria-label="Specimen 52 row inspector" data-v24-inspector>'
        '<div class="w2-card-hdr"><h4 class="w2-card-title w2-inspector-title">Row Inspector</h4>'
        f'<span class="va-pill" data-variant="tag" data-state="{"fault" if first["sev"] == "CRITICAL" else ("warn" if first["sev"] == "WARN" else "nominal")}" data-insp-sev>{first["sev"]}</span></div>'
        '<dl class="w2-dl">'
        f'<dt>Timestamp</dt><dd class="w2-num" data-insp-ts>{first["ts"]}</dd>'
        f'<dt>Service</dt><dd class="w2-code" data-insp-svc>{first["svc"]}</dd>'
        f'<dt>Span ID</dt><dd class="w2-num" data-insp-span>{first["span"]}</dd>'
        f'<dt>Trace ID</dt><dd class="w2-num" data-insp-trace>{first["trace"]}</dd>'
        f'<dt>Upstream</dt><dd class="w2-code" data-insp-caller>{first["caller"]}</dd>'
        f'<dt>Status / Dur.</dt><dd class="w2-num" data-insp-code>{first["code"]} · {first["dur"]}</dd>'
        f'<dt>Detail</dt><dd data-insp-msg>{html.escape(first["msg"])}</dd></dl>'
        '<div class="w2-btn-group"><button type="button" class="w2-action-btn" data-v24-copy>Copy Trace Summary</button>'
        '<span class="w2-kpi-sub" role="status" aria-live="polite" data-v24-copy-status></span></div>'
        '</aside></div></div>'
    )
    return _wrap_specimen(
        "ui-triage-log-inspector", "ui-triage-log-inspector",
        "PILLAR 1 · WAVE 2 · HIGH-ROW TRIAGE DESK",
        "Dense Log Stream, Filter Bar &amp; Row Inspector",
        "UI · Triage Inspector", "L2",
        "Dense tabular event stream paired with category chips, instant text filtering, a synchronized attribute inspector, and empty-state recovery.",
        body,
    )


def _specimen_53_tradespace() -> str:
    mod = compute_v26_model(25, 60, 24)
    body = (
        '<div class="w2-stack" data-v26-root data-v26-scope="bench">'
        '<div class="w2-card-hdr"><div class="w2-btn-group">'
        '<span class="w2-kpi-val" data-v26-kpi="winner">' + str(mod["winner"]) + '</span>'
        '<span aria-hidden="true">·</span>'
        '<span class="w2-kpi-sub" data-v26-kpi="crossover">Month ' + str(mod["crossover"]) + '</span>'
        '<span aria-hidden="true">·</span>'
        '<span class="w2-kpi-sub" data-v26-kpi="savings">Saves $' + f'{mod["savings"]:.2f}M vs PayGo</span>'
        '</div><span class="va-pill" data-variant="status" data-state="' + str(mod["rec_state"]) + '" data-v26-rec-badge>RECOMMENDED: OPTION B HYBRID</span></div>'
        '<div class="w2-sliders-grid" role="region" aria-label="Specimen 53 trade-space sliders">'
        '<div class="w2-slider-field"><label class="w2-slider-hdr" for="s53-growth"><span>Annual Growth</span>'
        '<span class="w2-slider-val" data-v26-out="growth">25%</span></label>'
        '<input type="range" id="s53-growth" class="w2-slider" data-v26-input="growth" min="10" max="50" step="5" value="25"/></div>'
        '<div class="w2-slider-field"><label class="w2-slider-hdr" for="s53-commit"><span>Commit Coverage</span>'
        '<span class="w2-slider-val" data-v26-out="commit">60%</span></label>'
        '<input type="range" id="s53-commit" class="w2-slider" data-v26-input="commit" min="20" max="80" step="5" value="60"/></div>'
        '<div class="w2-slider-field"><label class="w2-slider-hdr" for="s53-runway"><span>Runway Floor</span>'
        '<span class="w2-slider-val" data-v26-out="runway">24 mo</span></label>'
        '<input type="range" id="s53-runway" class="w2-slider" data-v26-input="runway" min="18" max="36" step="3" value="24"/></div>'
        '</div>'
        f'<div class="w2-svg-box">{_v26_chart_svg(mod)}</div>'
        '<div class="w2-legend-row" aria-label="Specimen 53 curve legend">'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="focal"></span>Option B: Hybrid Commit</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="muted"></span>Option A: Elastic PayGo</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="warn"></span>Option C: Colocation CapEx</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="danger"></span>Budget Ceiling ($5.20M)</span>'
        '</div></div>'
    )
    return _wrap_specimen(
        "ui-constrained-tradespace", "ui-constrained-tradespace",
        "PILLAR 1 · WAVE 2 · CONSTRAINED TRADE-SPACE",
        "Constrained Trade-Space Slider &amp; Crossover Calculator",
        "UI · Sensitivity Solver", "L2",
        "Three coupled range sliders dynamically updating 36-month cumulative capital trajectories, the break-even crossover marker, and feasibility disposition.",
        body,
    )


def compile_wave2_specimens() -> str:
    """Compile Component Library Specimens 51, 52, and 53."""
    return _specimen_51_diff_gate() + _specimen_52_triage() + _specimen_53_tradespace()
