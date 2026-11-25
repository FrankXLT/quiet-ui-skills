#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.7.0 — Specimen 50: Automated 4-Phase Operational Alarm Lifecycle."""

from __future__ import annotations

import html
import json

from bench_data_contracts import contract_for_ui_specimen


def compile_alarm_lifecycle_specimen() -> str:
    """Compile Component Library Specimen 50 demonstrating the 4-phase ISA-18.2 alarm lifecycle."""
    config = {
        "viewId": "specimen-50-alarm",
        "initialMode": "ack",
        "benchControls": True,
        "paramLabel": "Feeder-B Bus Voltage",
        "channelTag": "ISA-18.2 / IEC 60601-1-8",
        "unit": "% nominal",
        "decimals": 1,
        "threshold": 94.0,
        "direction": "below",
        "nominalStart": 98.2,
        "breachPeak": 91.4,
        "breachReason": "94.0% Floor Breach",
        "ackActionHint": "Click Acknowledge Alarm to restore balanced sibling grid with latched steady fault.",
        "siblings": [
            {"label": "Feeder-A Voltage", "val": "99.1%"},
            {"label": "Grid Sync Freq", "val": "59.985 Hz"},
            {"label": "Reserve SoC", "val": "78.4%"},
        ],
    }
    cfg_json = html.escape(json.dumps(config, separators=(",", ":")), quote=True)
    contract_html = contract_for_ui_specimen("ui-alarm-lifecycle")
    body = (
        f'<div class="va-alarm-console" data-alarm-config="{cfg_json}" data-alarm-phase="ack">'
        '<div class="va-sr-only va-alarm-live" aria-live="polite" aria-atomic="true"></div>'
        '<div class="va-alarm-banner" data-alarm-banner></div>'
        '<section class="va-alarm-takeover" data-alarm-takeover aria-label="Specimen 50 Unacknowledged Alarm Takeover"></section>'
        '<div class="va-alarm-balanced-wrap" data-alarm-balanced>'
        '<div class="v9-demo-grid">'
        '<div class="v9-demo-subcard" data-alarm-fault-target="1">'
        '<div class="v9-demo-label">Feeder-B Bus Voltage (Monitored Channel)</div>'
        '<div class="v9-demo-row"><strong>Threshold: &gt;= 94.0% nominal</strong>'
        '<span class="va-pill" data-variant="status" data-state="fault">LATCHED EXCURSION · 91.4%</span></div>'
        '<p class="qe-fig-desc">Steps 1–4 demonstrate Calm Baseline, Amber Approaching Limit, Reduced-Motion-Safe Takeover, and Acknowledged Diagnostic restoration.</p>'
        '</div>'
        '<div class="v9-demo-subcard">'
        '<div class="v9-demo-label">Nominal Sibling Channels</div>'
        '<div class="v9-demo-row">'
        '<span class="va-pill" data-variant="status" data-state="nominal">FEEDER-A 99.1%</span>'
        '<span class="va-pill" data-variant="status" data-state="nominal">SYNC 59.985 Hz</span>'
        '<span class="va-pill" data-variant="status" data-state="nominal">BESS 78.4%</span>'
        '</div>'
        '</div>'
        '</div></div></div>'
    )
    return (
        '<article class="qe-specimen qe-specimen-wide" data-modality="UI" '
        'data-schema-modality="ui-alarm-lifecycle" data-rigor="L3">'
        '<div class="va-card qe-bench-card" id="ui-alarm-lifecycle">'
        '<div class="qe-fig-hdr">'
        '<div>'
        '<div class="qe-fig-kicker">PILLAR 1 · ISA-18.2 / IEC 60601-1-8 ALARM LIFECYCLE</div>'
        '<h2 class="qe-fig-title">Automated 4-Phase Alarm Takeover &amp; Acknowledge Flow</h2>'
        '</div>'
        '<div class="qe-fig-badges"><span class="va-pill" data-variant="tag">UI · M3 / M4 / M5</span></div>'
        '</div>'
        '<p class="qe-fig-desc">Transitions calmly from Safe Baseline through Pre-Breach Approach to Reduced-Motion-Safe Autonomous Takeover, then restores the balanced layout after Acknowledgement.</p>'
        f'<div class="qe-bench-body">{body}</div>'
        f'{contract_html}'
        '</div></article>'
    )
