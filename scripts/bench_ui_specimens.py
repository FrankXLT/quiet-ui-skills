#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 6.1 — Pillar 1 (UI) & Pillar 3 (BR) Interactive Bench Specimen Compilers."""

from __future__ import annotations

from html import escape as _esc
from typing import Any

from bench_data_contracts import contract_for_ui_specimen


def _wrap_card(spec_id: str, mod_code: str, schema_mod: str, rigor: str, title: str, kicker: str, subtitle: str, body_html: str) -> str:
    contract_html = contract_for_ui_specimen(spec_id)
    return (
        f'<article class="qe-specimen qe-specimen-wide" data-modality="{_esc(mod_code)}" '
        f'data-schema-modality="{_esc(schema_mod)}" data-rigor="{_esc(rigor)}">'
        f'<div class="va-card qe-bench-card" id="{_esc(spec_id)}">'
        '<div class="qe-fig-hdr">'
        '<div>'
        f'<div class="qe-fig-kicker">{_esc(kicker)}</div>'
        f'<h2 class="qe-fig-title">{_esc(title)}</h2>'
        '</div>'
        f'<div class="qe-fig-badges"><span class="va-pill" data-variant="tag">{_esc(mod_code)} · {_esc(rigor)}</span></div>'
        '</div>'
        f'<p class="qe-fig-desc">{_esc(subtitle)}</p>'
        f'<div class="qe-bench-body">{body_html}</div>'
        f'{contract_html}'
        '</div></article>'
    )


def _spec_31_pills() -> str:
    body = (
        '<div class="v9-demo-stack">'
        '<div class="v9-demo-grid">'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Status Badges (Non-Interactive · Nominal Borderless)</div>'
        '<div class="v9-demo-row">'
        '<span class="va-pill" data-variant="status" data-state="nominal">NOMINAL · 99.8%</span>'
        '<span class="va-pill" data-variant="status" data-state="warn">CAUTION · THERMAL</span>'
        '<span class="va-pill" data-variant="status" data-state="fault">TRIP · 2OO3 QUORUM</span>'
        '</div>'
        '</div>'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Monochrome Keycap Tags (2px Sharp Radius)</div>'
        '<div class="v9-demo-row">'
        '<span class="va-pill" data-variant="tag">NIST SP 811</span>'
        '<span class="va-pill" data-variant="tag">READ ONLY</span>'
        '<span class="va-pill" data-variant="tag">ISO-101 CONFORMANT</span>'
        '</div>'
        '</div>'
        '</div>'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Interactive Action Filter Chips (Button · 999px Pill Radius)</div>'
        '<div class="v9-demo-row v9-demo-chips" role="group" aria-label="Telemetry stream filter">'
        '<button type="button" class="va-pill" data-variant="chip" aria-pressed="true">Critical Only</button>'
        '<button type="button" class="va-pill" data-variant="chip" aria-pressed="false">Calibrated Sensors</button>'
        '<button type="button" class="va-pill" data-variant="chip" aria-pressed="false">Scheduled Hold</button>'
        '<span class="va-nums qe-fig-desc" data-chip-readout aria-live="polite">Active filter: Critical Only</span>'
        '</div>'
        '</div></div>'
    )
    return _wrap_card(
        "ui-pill-and-status-grammar",
        "UI",
        "ui-grammar",
        "L2",
        "3-Tier Pill & Status Annunciator Grammar",
        "PILLAR 1 · ATOMIC GRAMMAR",
        "Separates borderless nominal status dots, sharp 2px taxonomy tags, and 999px interactive action buttons.",
        body,
    )


def _spec_32_controls() -> str:
    body = (
        '<div class="v9-demo-grid">'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Industrial Two-Step Guarded Interlock</div>'
        '<div class="v9-guard-pad" data-guard-pad>'
        '<button type="button" class="v9-guard-btn" data-guard-arm aria-expanded="false">Arm Feeder Transfer</button>'
        '<button type="button" class="v9-guard-btn v9-guard-confirm" data-guard-confirm hidden>Confirm Execute</button>'
        '<button type="button" class="v9-guard-btn" data-guard-cancel hidden>Cancel</button>'
        '<span class="va-pill" data-variant="status" data-state="nominal" data-guard-state aria-live="polite">SAFE · LOCKED</span>'
        '</div>'
        '</div>'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Calm Consumer Segmented Preset &amp; Trim Stepper</div>'
        '<div class="v9-demo-row">'
        '<div class="v9-seg-group" role="group" aria-label="Comfort mode preset">'
        '<button type="button" class="v9-seg-btn" aria-pressed="false">Away</button>'
        '<button type="button" class="v9-seg-btn" aria-pressed="true">Comfort</button>'
        '<button type="button" class="v9-seg-btn" aria-pressed="false">Eco Night</button>'
        '</div>'
        '<div class="v9-stepper" data-stepper data-min="16.0" data-max="26.0" data-step="0.5" data-val="21.0">'
        '<button type="button" class="v9-stepper-btn" data-step-delta="-0.5" aria-label="Decrease setpoint">-</button>'
        '<span class="v9-stepper-val va-nums" data-step-display aria-live="polite">21.0 °C</span>'
        '<button type="button" class="v9-stepper-btn" data-step-delta="0.5" aria-label="Increase setpoint">+</button>'
        '</div>'
        '</div></div></div>'
    )
    return _wrap_card(
        "ui-guarded-and-consumer-controls",
        "UI",
        "ui-controls",
        "L2",
        "Guarded Industrial Switch & Calm Discrete Controls",
        "PILLAR 1 · ERGONOMIC ACTUATION",
        "Two-step arming for hazardous switchgear paired with low-friction segmented modes and 0.5 °C trim steppers.",
        body,
    )


def _spec_33_triage() -> str:
    rows = [
        ("r1", "open", "API token rotation grace window blocks canary ingest", "P1", "fault", "BLOCKED", "Owner: Security Gate · Target +1.0 d"),
        ("r2", "open", "TSN boundary clock drift spikes under 85 °C thermal ramp", "P1", "warn", "TRIAGED", "Owner: Controls Lab · Target +2.5 d"),
        ("r3", "done", "Verify zero SVG clipping on 390 px mobile viewport sweep", "P2", "nominal", "VERIFIED", "Owner: Release QA · Merged to integration"),
        ("r4", "open", "Publish calibrated RC cooling repeatability summary table", "P2", "warn", "REVIEW", "Owner: Lab Bench · Target +0.5 d"),
    ]
    row_html = "".join(
        f'<button type="button" class="v9-triage-row" role="option" aria-selected="{"true" if i == 0 else "false"}" '
        f'tabindex="{"0" if i == 0 else "-1"}" '
        f'data-triage-state="{st}" data-triage-detail="{_esc(det)}">'
        f'<span class="va-pill" data-variant="tag">{_esc(prio)}</span>'
        f'<span class="v9-triage-title">{_esc(ttl)}</span>'
        f'<span class="va-pill" data-variant="status" data-state="{sstate}">{_esc(slbl)}</span>'
        '</button>'
        for i, (_rid, st, ttl, prio, sstate, slbl, det) in enumerate(rows)
    )
    body = (
        '<div class="v9-triage-wrap" data-triage-root>'
        '<div class="v9-triage-bar">'
        '<div class="v9-demo-row" role="group" aria-label="Filter triage queue">'
        '<button type="button" class="va-pill" data-variant="chip" data-triage-filter="all" aria-pressed="true">All (4)</button>'
        '<button type="button" class="va-pill" data-variant="chip" data-triage-filter="open" aria-pressed="false">Open (3)</button>'
        '<button type="button" class="va-pill" data-variant="chip" data-triage-filter="done" aria-pressed="false">Verified (1)</button>'
        '</div>'
        '</div>'
        f'<div class="v9-triage-list" role="listbox" aria-label="Issue triage rows">{row_html}</div>'
        '<div class="v9-triage-meta" data-triage-detail-box aria-live="polite">Owner: Security Gate · Target +1.0 d</div>'
        '</div>'
    )
    return _wrap_card(
        "ui-compact-triage-queue",
        "UI",
        "ui-triage",
        "L1",
        "Dense 38px Issue Triage Queue & State Filters",
        "PILLAR 1 · WORKSPACE TRIAGE",
        "Single-scan horizontal triage strips with inline priority tags, state filters, and click-to-inspect owner metadata.",
        body,
    )


def _spec_34_tree() -> str:
    body = (
        '<div class="v9-tree-shell" data-tree-root>'
        '<ul class="v9-tree-nav" role="tree" aria-label="System Subsystem Hierarchy">'
        '<li role="none">'
        '<button type="button" class="v9-tree-btn" role="treeitem" data-tree-toggle aria-expanded="true" aria-selected="false" tabindex="-1"><span>Core Cluster (Prod)</span><span aria-hidden="true">▾</span></button>'
        '<ul role="group">'
        '<li role="none"><button type="button" class="v9-tree-btn" role="treeitem" data-tree-node aria-selected="true" tabindex="0" '
        'data-node-title="Edge Ingress Gateway" data-node-state="nominal" data-node-sla="99.94% · 14.2 ms p99" '
        'data-node-note="Zero packet drop across dual TLS terminators in last 24h.">Edge Ingress Gateway</button></li>'
        '<li role="none"><button type="button" class="v9-tree-btn" role="treeitem" data-tree-node aria-selected="false" tabindex="-1" '
        'data-node-title="Worker Queue Pool" data-node-state="warn" data-node-sla="97.80% · Depth 412" '
        'data-node-note="Elevated backlog from schema migration batch window.">Worker Queue Pool</button></li>'
        '<li role="none"><button type="button" class="v9-tree-btn" role="treeitem" data-tree-node aria-selected="false" tabindex="-1" '
        'data-node-title="Ledger Write Replica" data-node-state="nominal" data-node-sla="100.0% · 0.0 s lag" '
        'data-node-note="Synchronous quorum replication verified on 3 zones.">Ledger Write Replica</button></li>'
        '</ul></li></ul>'
        '<div class="v9-tree-detail" data-tree-detail aria-live="polite">'
        '<div class="v9-demo-row">'
        '<strong data-tree-title>Edge Ingress Gateway</strong>'
        '<span class="va-pill" data-variant="status" data-state="nominal" data-tree-badge>NOMINAL</span>'
        '</div>'
        '<div class="va-nums" data-tree-sla>SLO: 99.94% · 14.2 ms p99</div>'
        '<p class="qe-fig-desc" data-tree-note>Zero packet drop across dual TLS terminators in last 24h.</p>'
        '</div></div>'
    )
    return _wrap_card(
        "ui-coupled-tree-explorer",
        "UI",
        "ui-tree",
        "L3",
        "WAI-ARIA Coupled Tree Explorer & Inspector",
        "PILLAR 1 · HIERARCHICAL NAVIGATOR",
        "Native keyboard-accessible tree disclosure coupled synchronously with an operational SLA detail inspector.",
        body,
    )


def _spec_35_bridge_gate() -> str:
    body = (
        '<div class="v9-br-banner">'
        '<div class="v9-br-head">'
        '<strong>Verdict: CONDITIONAL HOLD — Complete Failover Drill Prior to Cutover</strong>'
        '<span class="va-pill" data-variant="status" data-state="warn">HOLD · 3/4 GATES PASS</span>'
        '</div>'
        '<p class="qe-fig-desc">Primary schema backfill and telemetry unit normalization passed verification; final Canary signoff requires green multi-AZ failover latency under 250.0 ms.</p>'
        '<div class="v9-br-checks">'
        '<div class="v9-br-check"><span>1. Type &amp; Build Parity</span><span class="va-pill" data-variant="status" data-state="nominal">PASS</span></div>'
        '<div class="v9-br-check"><span>2. Metric Conservation</span><span class="va-pill" data-variant="status" data-state="nominal">PASS</span></div>'
        '<div class="v9-br-check"><span>3. Multi-AZ Failover (&lt; 250 ms)</span><span class="va-pill" data-variant="status" data-state="warn">PENDING</span></div>'
        '<div class="v9-br-check"><span>4. Rollback Snapshot Verified</span><span class="va-pill" data-variant="status" data-state="nominal">PASS</span></div>'
        '</div></div>'
    )
    return _wrap_card(
        "br-review-room-gate-band",
        "BR",
        "bridge-gate",
        "L2",
        "Decision Gate Banner & Readiness Checklist",
        "PILLAR 3 · EXECUTIVE BLUF BRIDGE",
        "Lead-with-verdict gate banner tying executive go/hold posture directly to quantitative verification checkboxes.",
        body,
    )


def _spec_36_bridge_runbook() -> str:
    body = (
        '<div class="v9-split-runbook">'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Field Diagnostic &amp; Recovery Sequence</div>'
        '<ol class="v9-runbook-steps">'
        '<li>Measure bus termination impedance across CAN_H / CAN_L (expect 60.0 Ω nominal with dual 120 Ω ends).</li>'
        '<li>Inspect optical/TSN grandmaster lock offset against 0.35 µs dropout ceiling before escalating.</li>'
        '<li>Capture deterministic trace bundle and attach calibration delta before resetting fault latch.</li>'
        '</ol>'
        '<pre class="v9-runbook-cmd" role="region" aria-label="Diagnostic command" tabindex="0"><code>diag-probe --bus tsn0 --check-eol --window 12s</code></pre>'
        '</div>'
        '<div class="v9-callout-stack">'
        '<div class="v9-callout-box is-warn">'
        '<strong>Thermal Derating Watch</strong><br/>Defer load step above 85 °C enclosure ambient until coolant delta recovers below 4 °C.'
        '</div>'
        '<div class="v9-callout-box">'
        '<strong>Escalation Threshold</strong><br/>Route unresolved cyclic frame jitter (&gt; 12.0 µs) directly to Systems Controls Desk.'
        '</div>'
        '</div></div>'
    )
    return _wrap_card(
        "br-split-runbook-and-callout",
        "BR",
        "bridge-runbook",
        "L2",
        "Split Verification Runbook & Escalation Callout",
        "PILLAR 3 · PROCEDURAL BRIDGE",
        "Asymmetric split pairing ordered diagnostic steps and copy-safe command blocks with fault escalation thresholds.",
        body,
    )


def _spec_37_kpi_gauge_cards() -> str:
    body = (
        '<div class="v9-demo-stack" data-kpi-demo-wrap>'
        '<div class="v9-demo-row" style="justify-content:space-between;align-items:center">'
        '<span class="v9-demo-label">4-up Desktop / 2-up Tablet KPI Gauges (Absent Sub-Slots Omitted Cleanly)</span>'
        '<button type="button" class="va-pill" data-variant="chip" data-kpi-toggle-state aria-pressed="true">Simulate Post-Restart Warmup (N=3)</button>'
        '</div>'
        '<div class="va-kpi-gauge-grid">'
        '<div class="va-kpi-gauge-card" data-state="nominal">'
        '<div class="va-kpi-gauge-head"><span class="va-kpi-gauge-label">Partner Quota</span><span class="va-pill" data-variant="status" data-state="nominal">Nominal</span></div>'
        '<div class="va-kpi-gauge-val">68.4%</div>'
        '<div class="va-kpi-gauge-track" role="progressbar" aria-label="Partner Quota Utilization" aria-valuenow="68" aria-valuemin="0" aria-valuemax="100">'
        '<div class="va-kpi-gauge-fill" style="inline-size:68.4%"></div>'
        '<span class="va-kpi-gauge-target" style="inset-inline-start:71.4%" title="Daily target 71.4%"></span>'
        '</div>'
        '<div class="va-kpi-gauge-stats"><span>6.84M / 10M</span><span>n=482</span><span>Target 71.4%</span></div>'
        '</div>'
        '<div class="va-kpi-gauge-card" data-state="nominal">'
        '<div class="va-kpi-gauge-head"><span class="va-kpi-gauge-label">Core Compute</span><span class="va-pill" data-variant="tag">NO TARGET PIN</span></div>'
        '<div class="va-kpi-gauge-val">41.2%</div>'
        '<div class="va-kpi-gauge-track" role="progressbar" aria-label="Core Compute Utilization" aria-valuenow="41" aria-valuemin="0" aria-valuemax="100">'
        '<div class="va-kpi-gauge-fill" style="inline-size:41.2%"></div>'
        '</div>'
        '<div class="va-kpi-gauge-stats"><span>82.4M / 200M</span><span>n=1,920</span></div>'
        '</div>'
        '<div class="va-kpi-gauge-card" data-state="warn">'
        '<div class="va-kpi-gauge-head"><span class="va-kpi-gauge-label">Queue Depth</span><span class="va-pill" data-variant="status" data-state="warn">ADVISORY</span></div>'
        '<div class="va-kpi-gauge-val">84.0%</div>'
        '<div class="va-kpi-gauge-track" role="progressbar" aria-label="Queue Depth" aria-valuenow="84" aria-valuemin="0" aria-valuemax="100">'
        '<div class="va-kpi-gauge-fill" style="inline-size:84%"></div>'
        '<span class="va-kpi-gauge-target" style="inset-inline-start:80%" title="Queue advisory threshold 80%"></span>'
        '</div>'
        '<div class="va-kpi-gauge-stats"><span>42 / 50 slots</span><span>p95 180 ms</span></div>'
        '</div>'
        '<div class="va-kpi-gauge-card" data-state="nominal">'
        '<div class="va-kpi-gauge-head"><span class="va-kpi-gauge-label">Post-Restart Buffer</span><span class="va-pill" data-variant="tag">WARMUP</span></div>'
        '<div class="va-kpi-gauge-val" data-kpi-warmup-val>3 calls</div>'
        '<div class="va-kpi-gauge-track" role="progressbar" data-kpi-warmup-bar aria-label="Warmup Sample Count" aria-valuenow="6" aria-valuemin="0" aria-valuemax="100">'
        '<div class="va-kpi-gauge-fill" data-kpi-warmup-fill style="inline-size:6%"></div>'
        '</div>'
        '<div class="va-kpi-gauge-stats"><span data-kpi-warmup-note>Warming up — 3 samples collected (uptime 12m)</span></div>'
        '</div>'
        '</div>'
        '</div>'
    )
    return _wrap_card(
        "ui-dense-kpi-gauge-cards",
        "UI",
        "ui-kpi-gauges",
        "M3",
        "Dense Operational KPI Gauge Row & Omitted Target Pin",
        "PILLAR 1 · M3 COCKPIT PRIMITIVE",
        "Compact 4-up/2-up gauge cards preserving used/limit tracks while omitting absent target pins and marking thin warmup buffers.",
        body,
    )


def _spec_38_joined_toolbar() -> str:
    body = (
        '<div class="v9-demo-stack">'
        '<div class="va-toolbar-joined" role="toolbar" aria-label="Telemetry filter and export controls" data-joined-toolbar>'
        '<div class="va-tb-group" role="group" aria-label="Time window">'
        '<button type="button" class="va-tb-btn" data-tb-group="window" data-tb-val="24h" aria-pressed="true">24h</button>'
        '<button type="button" class="va-tb-btn" data-tb-group="window" data-tb-val="7d" aria-pressed="false">7d</button>'
        '<button type="button" class="va-tb-btn" data-tb-group="window" data-tb-val="30d" aria-pressed="false">30d</button>'
        '</div>'
        '<span class="va-tb-sep" role="separator" aria-orientation="vertical"></span>'
        '<div class="va-tb-group" role="group" aria-label="Cohort scope">'
        '<button type="button" class="va-tb-btn" data-tb-group="scope" data-tb-val="all" aria-pressed="true">All Runs (482)</button>'
        '<button type="button" class="va-tb-btn" data-tb-group="scope" data-tb-val="excursions" aria-pressed="false">Excursions (19)</button>'
        '<button type="button" class="va-tb-btn" data-tb-group="scope" data-tb-val="post" aria-pressed="false">Since Ceiling Effective</button>'
        '</div>'
        '<span class="va-tb-sep" role="separator" aria-orientation="vertical"></span>'
        '<div class="va-tb-group" role="group" aria-label="Export actions">'
        '<button type="button" class="va-tb-btn" data-tb-action="export">Export CSV</button>'
        '<button type="button" class="va-tb-btn" data-tb-action="reset">Reset</button>'
        '</div>'
        '</div>'
        '<div class="v9-triage-meta" data-tb-status aria-live="polite">Window: 24h · Scope: All Runs (482)</div>'
        '</div>'
    )
    return _wrap_card(
        "ui-joined-workspace-toolbar",
        "UI",
        "ui-joined-toolbar",
        "M3",
        "Compact Joined Workspace Toolbar (27px Desktop / 44px Touch)",
        "PILLAR 1 · M3 TOOLBAR GRAMMAR",
        "Single-row ARIA toolbar with hairline-joined filter groups that wrap cleanly on 900px foldables and expand to 44px touch targets on phones.",
        body,
    )


def compile_ui_bridge_specimens() -> str:
    """Compile all 8 Pillar 1 (UI) and Pillar 3 (BR) interactive gallery cards."""
    return "".join([
        _spec_31_pills(),
        _spec_32_controls(),
        _spec_33_triage(),
        _spec_34_tree(),
        _spec_35_bridge_gate(),
        _spec_36_bridge_runbook(),
        _spec_37_kpi_gauge_cards(),
        _spec_38_joined_toolbar(),
    ])
