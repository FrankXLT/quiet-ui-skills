#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.4 — Specimen 44: Validated Threshold Form, 4-Way Zero-States & Reversible Undo."""

from __future__ import annotations

from bench_data_contracts import contract_for_ui_specimen


def compile_forms_specimen() -> str:
    """Compile Specimen 44 (#qe-forms-zero-states) demonstrating forms, 4 zero-states, and undo."""
    contract_html = contract_for_ui_specimen("qe-forms-zero-states")
    form_pane = (
        '<section class="va-pane" aria-labelledby="s44-form-hdr">'
        '<div class="va-pane-hdr">'
        '<strong id="s44-form-hdr" class="v9-sec-title">Threshold Form &amp; Reversible Undo</strong>'
        '<span class="va-pill" data-variant="status" data-state="nominal" data-s44-rule-pill>Active · 250 ms</span>'
        '</div>'
        '<div class="va-pane-body v9-demo-stack">'
        '<form class="v9-demo-stack" data-s44-form novalidate>'
        '<div class="va-field">'
        '<label class="va-field-label" for="s44-threshold-input">Alert Ceiling (ms)</label>'
        '<span id="s44-threshold-hint" class="va-field-hint">Allowed range: 10–5000 ms (validates on blur/submit; clears on input).</span>'
        '<input class="va-input va-nums" id="s44-threshold-input" name="ceiling_ms" type="number" '
        'min="10" max="5000" required value="250" aria-invalid="false" '
        'aria-describedby="s44-threshold-hint" data-error="s44-threshold-err">'
        '<div id="s44-threshold-err" class="va-field-error" hidden>Enter an integer ceiling between 10 and 5000 ms.</div>'
        '</div>'
        '<div class="va-gate-reason" data-s44-gate-reason data-state="nominal" aria-live="polite">'
        'Ready: active threshold 250 ms can be saved or archived safely.'
        '</div>'
        '<div class="v9-demo-row">'
        '<button type="submit" class="va-btn-primary" data-s44-save>Save Threshold</button>'
        '<button type="button" class="va-btn-ghost" data-s44-archive>Archive Rule</button>'
        '</div>'
        '</form>'
        '<div class="va-undo-toast" data-s44-toast role="status" aria-live="polite" hidden>'
        '<span class="va-undo-msg" data-s44-toast-msg>Rule archived.</span>'
        '<span class="va-undo-actions">'
        '<button type="button" class="va-tb-btn" data-s44-undo>Undo</button>'
        '<button type="button" class="va-tb-btn" data-s44-toast-dismiss aria-label="Dismiss notification">Dismiss</button>'
        '</span>'
        '</div>'
        '</div>'
        '</section>'
    )

    tabs = (
        '<div class="va-tab-strip" role="tablist" aria-label="Zero-data state taxonomy" data-s44-tabs>'
        '<button type="button" class="va-tab" role="tab" id="s44-tab-filtered" aria-selected="true" '
        'aria-controls="s44-panel-filtered" data-s44-kind="filtered">Filtered (0)</button>'
        '<button type="button" class="va-tab" role="tab" id="s44-tab-first-run" aria-selected="false" '
        'aria-controls="s44-panel-first-run" data-s44-kind="first-run">First-Run</button>'
        '<button type="button" class="va-tab" role="tab" id="s44-tab-warmup" aria-selected="false" '
        'aria-controls="s44-panel-warmup" data-s44-kind="warmup">Warmup (N=4)</button>'
        '<button type="button" class="va-tab" role="tab" id="s44-tab-stale" aria-selected="false" '
        'aria-controls="s44-panel-stale" data-s44-kind="stale">Stale Cache</button>'
        '</div>'
    )

    panels = (
        '<div id="s44-panel-filtered" role="tabpanel" aria-labelledby="s44-tab-filtered" data-s44-panel="filtered">'
        '<div class="va-empty-state" data-kind="filtered">'
        '<h3 class="va-empty-title" data-s44-filtered-title>0 runs match "region:ap-east · status:fault"</h3>'
        '<p class="va-empty-copy" data-s44-filtered-copy>Two active filters exclude all 48 recorded spans in this window.</p>'
        '<div class="va-empty-actions">'
        '<button type="button" class="va-btn-primary" data-s44-clear-filters>Clear filters</button>'
        '<button type="button" class="va-btn-ghost" data-s44-reapply-filters hidden>Re-apply filter</button>'
        '</div>'
        '</div>'
        '</div>'
        '<div id="s44-panel-first-run" role="tabpanel" aria-labelledby="s44-tab-first-run" data-s44-panel="first-run" hidden>'
        '<div class="va-empty-state" data-kind="first-run">'
        '<h3 class="va-empty-title">No collectors connected</h3>'
        '<p class="va-empty-copy">Attach an OpenTelemetry or Modbus probe endpoint to stream verified latencies.</p>'
        '<div class="va-empty-actions">'
        '<button type="button" class="va-btn-primary" data-s44-connect>Connect Collector</button>'
        '</div>'
        '</div>'
        '</div>'
        '<div id="s44-panel-warmup" role="tabpanel" aria-labelledby="s44-tab-warmup" data-s44-panel="warmup" hidden>'
        '<div class="va-empty-state" data-kind="warmup">'
        '<h3 class="va-empty-title">Warming up — 4 samples collected</h3>'
        '<p class="va-empty-copy">Sampling every 30 s; steady baseline percentiles unlock once N &ge; 10 samples arrive.</p>'
        '</div>'
        '</div>'
        '<div id="s44-panel-stale" role="tabpanel" aria-labelledby="s44-tab-stale" data-s44-panel="stale" hidden>'
        '<div class="va-empty-state" data-kind="stale">'
        '<h3 class="va-empty-title">Upstream sync timed out — showing last valid values</h3>'
        '<div class="va-stale-retained">'
        '<span>p95 Latency: 142 ms · Error Rate: 0.4%</span>'
        '<span class="va-pill" data-variant="status" data-state="warn">STALE · Last sync 14:22:08 UTC</span>'
        '</div>'
        '<div class="va-empty-actions">'
        '<button type="button" class="va-btn-ghost" data-s44-retry>Retry now</button>'
        '</div>'
        '</div>'
        '</div>'
    )

    states_pane = (
        '<section class="va-pane" aria-labelledby="s44-states-hdr">'
        '<div class="va-pane-hdr">'
        '<strong id="s44-states-hdr" class="v9-sec-title">4-Way Zero-Data Taxonomy</strong>'
        '<span class="va-pane-count">4 states</span>'
        '</div>'
        f'<div class="va-pane-body v9-demo-stack">{tabs}{panels}</div>'
        '</section>'
    )

    body = f'<div class="va-workbench-panes" data-s44-root>{form_pane}{states_pane}</div>'

    return (
        '<article class="qe-specimen qe-specimen-wide" data-modality="UI" '
        'data-schema-modality="ui-forms-states" data-rigor="L2">'
        '<div class="va-card qe-bench-card" id="qe-forms-zero-states">'
        '<div class="qe-fig-hdr">'
        '<div>'
        '<div class="qe-fig-kicker">PILLAR 1 · FORMS, ZERO-STATES &amp; REVERSIBILITY</div>'
        '<h2 class="qe-fig-title">Validated Threshold Form, 4-Way Zero-States &amp; Reversible Undo</h2>'
        '</div>'
        '<div class="qe-fig-badges"><span class="va-pill" data-variant="tag">UI · L2</span></div>'
        '</div>'
        '<p class="qe-fig-desc">Demonstrates blur/submit validation with corrective input clearing, '
        'explicit gate reasons, 4 honest zero-data patterns (with 1-click filter recovery), and reversible Undo toasts.</p>'
        f'<div class="qe-bench-body">{body}</div>'
        f'{contract_html}'
        '</div></article>'
    )
