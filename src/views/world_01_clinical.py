#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 4 — World 01 (Clinical ICU, Phase III Trials & Patient Companion) Builder."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

try:
    from world_common import (
        assemble_world_bundle,
        embed_compile,
        format_math_html,
        inject_fig_class,
        load_world_inputs,
        render_alarm_console_close,
        render_alarm_console_open,
        render_handoff_link,
        render_params_aside,
    )
except ImportError:
    from src.views.world_common import (
        assemble_world_bundle,
        embed_compile,
        format_math_html,
        inject_fig_class,
        load_world_inputs,
        render_alarm_console_close,
        render_alarm_console_open,
        render_handoff_link,
        render_params_aside,
    )


def _inject_mobile_tile(scalars_html: str, dropout_s: float) -> str:
    tile = (
        '\n<div class="qe-scalar-card v01-mobile-only-tile">'
        '<div class="qe-scalar-zone1 qe-scalar-top"><span class="va-kicker">SIGNAL QUALITY</span>'
        '<span class="qe-scalar-ts va-nums">6.4–8.8 s Window</span></div>'
        '<h3 class="qe-scalar-title">Signal Dropout</h3>'
        '<div class="qe-scalar-zone2 qe-scalar-val-row">'
        f'<div class="qe-scalar-val-wrap"><span class="qe-scalar-val va-nums">{dropout_s:.1f}\u00a0s</span>'
        '<span class="qe-scalar-calc qe-unit">Uninterpolated null gap</span></div>'
        '<div class="qe-scalar-disp"><span class="va-pill" data-variant="status" data-state="warn">CHECK</span></div>'
        '</div></div>'
    )
    marker = '</div><figcaption class="va-figure-caption">'
    if marker in scalars_html:
        return scalars_html.replace(marker, tile + marker, 1)
    return scalars_html


def _build_v01_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    map_m, peep_cmd, peep_act, drop_m = cm["map_mmhg"], cm["peep_cmd_cmh2o"], cm["peep_act_cmh2o"], cm["dropout_duration_s"]
    ta_html, tb_html = format_math_html("T_A"), format_math_html("T_B")
    scalars_html = _inject_mobile_tile(inject_fig_class(embed_compile(specs["scalars"], "L3", "m4"), "v01-scalars-fig"), float(drop_m["value"]))
    scope_html = inject_fig_class(embed_compile(specs["scope"], "L3", "m4"), "v01-scope-fig")
    alarm_cfg = {
        "viewId": "v01-icu-bedside-terminal",
        "initialMode": "auto",
        "paramLabel": "Mean Arterial Pressure (MAP)",
        "channelTag": "BED ICU-04 · HEMODYNAMICS",
        "unit": "mmHg",
        "decimals": 1,
        "threshold": float(map_m["lower_limit"]),
        "direction": "below",
        "nominalStart": float(map_m["target"]),
        "breachPeak": float(map_m["value"]) - 4.0,
        "breachReason": f"< {map_m['lower_limit']:.1f} mmHg Floor",
        "ackActionHint": "Acknowledge alert and verify radial transducer zero before titration.",
        "siblings": [
            {"label": "PEEP Act", "val": f"{peep_act['value']:.1f} cmH2O"},
            {"label": "SpO2", "val": f"{cm['spo2_pct']['value']:.1f}%"},
            {"label": "Dropout", "val": f"{drop_m['value']:.1f} s"},
        ],
    }
    handoff = render_handoff_link("01-clinical-icu-and-trials", "v03-patient-recovery-companion", "Patient Recovery View ->")

    return f"""<div class="v9-stage-inner v9-view-v01">
  <div class="va-m1-block-only v9-m1-folio">
    <span>ARCHIVAL CLINICAL RECORD · ICU-BED-04</span>
    <span>CALIBRATION: CAL-NIST-ICU-2026-401 · 2026-11-17T05:30:00Z</span>
  </div>
  <header class="v9-masthead v9-masthead-compact">
    <div class="v01-masthead-left">
      <span class="va-kicker">ADULT ICU · BED 04 · SEPSIS PROTOCOL</span>
      <h1 class="v9-masthead-title">Hemodynamic &amp; Ventilator Telemetry</h1>
    </div>
    {handoff}
  </header>
  {render_alarm_console_open(alarm_cfg, "nominal", "Mean Arterial Pressure Unacknowledged Alarm")}
  <section id="v01-vent" data-alarm-fault-target="1" aria-label="Bedside Vital and Ventilator Scalars">
    {scalars_html}
  </section>

  <section id="v01-hemo" aria-label="Synchronized Hemodynamic Scope">
    {scope_html}
  </section>

  <section id="v01-infusions" aria-label="Guarded Vasopressor Titration Strip">
    <div id="v01-titration-card" class="v01-titration-card">
      <div class="v01-titration-ctrl">
        <div class="v01-titration-head">
          <h2 class="v01-titration-title">Guarded Vasopressor Titration Interlock</h2>
          <span id="v01-titration-state" class="va-pill" data-variant="tag">HOLD FOR ZERO CHECK</span>
        </div>
        <p class="v01-titration-note">
          Current Norepinephrine: <strong id="v01-norepi-rate" class="mono va-nums">0.08 µg/(kg·min)</strong> ·
          Verify radial transducer zeroing after the {drop_m["value"]:.1f}\u00a0s motion-artifact dropout ({drop_m["cursor_a_s"]:.1f}\u00a0s–{drop_m["cursor_b_s"]:.1f}\u00a0s) before executing titration.
        </p>
        <div class="v01-titration-pad">
          <button type="button" id="v01-zero-btn" class="v01-tactile-btn v01-zero-btn" aria-pressed="false">1. Zero Transducer Check</button>
          <button type="button" id="v01-arm-btn" class="v01-tactile-btn v01-arm-btn" aria-pressed="false">2. ARM Norepinephrine +0.02</button>
          <button type="button" id="v01-exec-btn" class="v01-tactile-btn v01-exec-btn" disabled>EXECUTE</button>
        </div>
      </div>
      <div id="v01-alarms" class="v01-audit-box" role="log" aria-live="polite" aria-label="Clinical Interlock Audit Log">
        <span class="va-kicker">CLINICAL TITRATION AUDIT LOG</span>
        <div id="v01-audit-list" class="v01-audit-list">
          <div class="v01-audit-item">[05:30:00Z] Motion-artifact dropout ({drop_m["value"]:.1f} s) bracketed {ta_html}={drop_m["cursor_a_s"]:.1f} s to {tb_html}={drop_m["cursor_b_s"]:.1f} s; verify transducer before titration.</div>
          <div class="v01-audit-item">[05:29:54Z] MAP excursion {map_m["value"]:.1f} mmHg below {map_m["lower_limit"]:.1f} mmHg floor (abort {map_m["abort_lower_limit"]:.1f} mmHg); PEEP {peep_act["value"]:.1f} vs {peep_cmd["value"]:.1f} cmH<sub>2</sub>O CMD.</div>
        </div>
      </div>
    </div>
  </section>
  {render_alarm_console_close()}
</div>"""


def _build_v02_html(corpus: dict[str, Any], specs: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    ov, ag, sf, lc, aki = cm["overall_hr"], cm["age_ge65_hr"], cm["sofa_ge8_hr"], cm["lactate_gt2_hr"], cm["aki_rate_pct"]
    forest_html = embed_compile(specs["forest"], "L3", "m2")
    table_html = embed_compile(specs["ae_table"], "L3", "m2")

    return f"""<div class="v9-stage-inner v9-view-v02">
  <div class="va-m1-block-only v9-m1-folio">
    <span>CLINICAL STUDY ARCHIVAL BRIEF · TRIAL-SEPSIS-2026-P3 · SAP-v2.4-ITT</span>
    <span>DSMB LOCK: 2026-11-17T05:30:00Z · LETTER 8.5×11 IN</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">CLINICAL STUDY REPORT · SAP-v2.4-ITT · DSMB LOCK</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">TRIAL-SEPSIS-2026-P3</span>
        <span class="va-pill" data-variant="tag">n={ov["cohort_n"]:,}</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Sepsis Vasopressor-Sparing Trial — FDA &amp; CMO Review</h1>
    <p class="v9-masthead-sub">Reviews 28-day survival gains and 10 safety/monitoring cohorts (renal events, artifact dropouts, and lab holds) before authorizing protocol rollout.</p>
  </header>

  <div class="v02-book-spread">
    <div class="v02-left-page">
      <section id="v02-disposition" class="v02-gate-band" aria-label="Executive Gate Disposition">
        <div class="v02-gate-top">
          <h2 class="v02-gate-rec">RECOMMEND CONDITIONAL AUTHORIZATION: SOFA ≥ 8 &amp; Lactate &gt; 2 <span class="qe-unit">mmol/L</span></h2>
          <span class="va-pill" data-variant="status" data-state="warn">CONDITIONAL</span>
        </div>
        <div class="v02-kpi-strip">
          <div class="v02-kpi-tile">
            <span class="va-kicker">28-DAY MORTALITY HR</span>
            <span class="v02-kpi-val va-nums">{ov["value"]:.2f} [{ov["ci_low"]:.2f}, {ov["ci_high"]:.2f}]</span>
            <span class="v02-kpi-sub">Primary ITT (n = {ov["cohort_n"]:,})</span>
          </div>
          <div class="v02-kpi-tile">
            <span class="va-kicker">SOFA ≥ 8 STRATUM</span>
            <span class="v02-kpi-val va-nums">{sf["value"]:.2f} [{sf["ci_low"]:.2f}, {sf["ci_high"]:.2f}]</span>
            <span class="v02-kpi-sub">Decisive benefit (n = {sf["cohort_n"]})</span>
          </div>
          <div class="v02-kpi-tile">
            <span class="va-kicker">LACTATE &gt; 2 <span class="qe-unit">mmol/L</span></span>
            <span class="v02-kpi-val va-nums">{lc["value"]:.2f} [{lc["ci_low"]:.2f}, {lc["ci_high"]:.2f}]</span>
            <span class="v02-kpi-sub">Decisive benefit (n = {lc["cohort_n"]})</span>
          </div>
          <div class="v02-kpi-tile">
            <span class="va-kicker">KDIGO STAGE ≥ 2 AKI</span>
            <span class="v02-kpi-val va-nums">{aki["value"]:.1f} ± {aki["expanded_uncertainty"]:.1f}%</span>
            <span class="v02-kpi-sub">vs {aki["control_value"]:.1f}% Control Arm</span>
          </div>
        </div>
        <div id="v02-subgroup-chips" class="v02-filter-bar va-sheet-hide" role="group" aria-label="Filter Clinical Subgroups">
          <button type="button" class="va-pill v02-chip is-active" data-variant="chip" data-subgroup="all" aria-pressed="true" data-summary="All 4 CONSORT strata shown (ITT n=1,240; Overall HR 0.74 [0.61, 0.90]).">All Strata</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="overall" aria-pressed="false" data-summary="Overall Cohort (n=1,240): HR 0.74 [0.61, 0.90] — statistically decisive below HR=1.0.">Overall (n=1,240)</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="age" aria-pressed="false" data-summary="Age ≥ 65 yr (n=612): HR 0.79 [0.62, 1.01] crosses null (1.0); muted secondary series.">Age ≥ 65 (n=612)</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="sofa" aria-pressed="false" data-summary="SOFA ≥ 8 (n=486): HR 0.68 [0.52, 0.89] — strongest vasopressor-sparing effect.">SOFA ≥ 8 (n=486)</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="lactate" aria-pressed="false" data-summary="Lactate > 2 mmol/L (n=704): HR 0.71 [0.54, 0.93] — decisive survival margin.">Lactate &gt; 2 (n=704)</button>
        </div>
        <div id="v02-filter-readout" class="v02-filter-readout va-sheet-hide" aria-live="polite">All 4 CONSORT strata shown (ITT n=1,240; Overall HR 0.74 [0.61, 0.90]).</div>
      </section>

      <div class="v9-editorial-grid">
        <article id="v02-methods" class="v02-prose-col">
          <h2>Cohort Design, Null-Crossing Stratification &amp; Renal Safety</h2>
          <p>Across the intention-to-treat population (n = {ov["cohort_n"]:,}, 620 protocol vs. 620 control), the protocol achieved an overall 28-day mortality hazard ratio of {ov["value"]:.2f} (95% CI [{ov["ci_low"]:.2f}, {ov["ci_high"]:.2f}]). Decisive benefit concentrates in high-acuity strata: SOFA ≥ 8 (n = {sf["cohort_n"]}, HR {sf["value"]:.2f} [{sf["ci_low"]:.2f}, {sf["ci_high"]:.2f}]) and Lactate &gt; 2 mmol/L (n = {lc["cohort_n"]}, HR {lc["value"]:.2f} [{lc["ci_low"]:.2f}, {lc["ci_high"]:.2f}]).</p>
          <p>Conversely, the Age ≥ 65 yr subgroup (n = {ag["cohort_n"]}, HR {ag["value"]:.2f} [{ag["ci_low"]:.2f}, {ag["ci_high"]:.2f}]) crosses the 1.0 null boundary and remains deemphasized relative to significant high-acuity strata. KDIGO Stage ≥ 2 acute kidney injury decreased to {aki["value"]:.1f} ± {aki["expanded_uncertainty"]:.1f}% versus {aki["control_value"]:.1f}% control, while refractory hypotension (MAP &lt; 65 mmHg, 8.6 ± 1.5% vs. 11.2%) remains under mandatory WATCH surveillance.</p>
        </article>
        {render_params_aside("Protocol & DSMB Parameters", [
            ("Trial Identifier", "TRIAL-SEPSIS-2026-P3"),
            ("Analysis Set", "ITT (620 vs. 620, n = 1,240)"),
            ("Regression Model", "Stratified Cox PH (95% CI)"),
            ("Null Crossing Guard", f"Age ≥ 65 CI high = {ag['ci_high']:.2f}"),
            ("Renal Safety WATCH", "MAP < 65 mmHg (8.6% vs 11.2%)"),
        ])}
      </div>
    </div>

    <div class="v02-right-page">
      <section id="v02-forest" class="v02-bleed-block" aria-label="CONSORT Subgroup Forest Plot">
        {forest_html}
      </section>

      <section id="v02-safety" class="v02-bleed-block" aria-label="KDIGO Safety and Efficacy Register">
        {table_html}
      </section>

      <section id="v02-sap" class="v02-sap-appendix va-test-condition-block" aria-label="SAP Statistical Appendix">
        <span class="va-kicker">SAP-v2.4-ITT STATISTICAL ARCHIVAL APPENDIX</span>
        <div class="v02-sap-grid">
          <div><strong>Study ID:</strong> TRIAL-SEPSIS-2026-P3</div>
          <div><strong>Analysis Lock:</strong> DSMB-LOCK-2026-11</div>
          <div><strong>Model:</strong> Stratified Cox PH (95% CI)</div>
          <div><strong>Control Arm AKI:</strong> {aki["control_value"]:.1f}% vs {aki["value"]:.1f}%</div>
        </div>
      </section>
    </div>
  </div>
</div>"""


def _build_v03_vitals(specs: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    raw_sc = copy.deepcopy(specs["scalars"])
    map_item = copy.deepcopy(raw_sc["items"][0])
    map_item["metadata"]["title"] = "Resting Blood Pressure"
    map_item["metadata"]["plain_label"] = "Arm Cuff Check"
    map_item["metadata"].pop("subsystem", None)
    map_item["quantity"]["target_label"] = "Goal: ≥ 65 mmHg"
    map_item["status_annunciator"]["l1_label"] = "Recheck in 15 min"

    spo2_item = copy.deepcopy(raw_sc["items"][2])
    spo2_item["metadata"]["title"] = "Oxygen Level (Pulse Oximeter)"
    spo2_item["metadata"]["plain_label"] = "Finger Sensor Check"
    spo2_item["metadata"].pop("subsystem", None)
    spo2_item["quantity"]["target_label"] = "Goal: ≥ 92%"
    spo2_item["status_annunciator"]["l1_label"] = "On Track"

    spo2_card, map_card = copy.deepcopy(spo2_item), copy.deepcopy(map_item)
    spo2_card.pop("sparkline", None)
    map_card.pop("sparkline", None)

    l1_spec = {
        "$schema": "urn:quiet-ui:schema:v9:scalar",
        "id": "v03-patient-home-vitals",
        "metadata": {
            "title": "Your Daily Recovery Vitals",
            "description": "Plain-language home targets without redundant chart traces.",
            "rigor_level": "L1",
            "timestamp_utc": "2026-11-17T05:30:00Z",
        },
        "items": [spo2_card, map_card],
    }
    html = embed_compile(l1_spec, "L1", "m3")
    return html, spo2_item, map_item


def _build_v03_charts(spo2_item: dict[str, Any], map_item: dict[str, Any]) -> str:
    spo2_pts = [{"x": i + 1, "y": float(v)} for i, v in enumerate(spo2_item["sparkline"])]
    map_pts = [{"x": i + 1, "y": float(v)} for i, v in enumerate(map_item["sparkline"])]
    spo2_plot = {
        "$schema": "urn:quiet-ui:schema:v9:plot",
        "id": "v03-oxygen-trend-chart",
        "metadata": {"title": "Oxygen Level Trend", "rigor_level": "L1"},
        "plot_kind": "cartesian",
        "show_l1_envelopes": True,
        "axes": {
            "x_axis": {"quantity": "Check-In", "unit": "1", "quantity_calculus": "Check-In Reading (1 to 10)", "scale_type": "linear", "domain": [1, 10]},
            "y_axis": {"quantity": "Oxygen", "unit": "%", "quantity_calculus": "Oxygen Saturation (%)", "scale_type": "linear", "domain": [88, 100]},
        },
        "envelopes": [
            {"label": "Goal ≥ 92%", "threshold_value": 92.0, "type": "warning", "direction": "lower", "stroke_color": "var(--tint-emerald-fg)"},
        ],
        "series": [
            {"id": "spo2_home", "name": "Oxygen Level (%)", "epistemic_type": "discrete_measurement", "connect_piecewise": True, "term": "oxygen-goal", "stroke_color": "var(--tint-emerald-fg)", "marker_glyph": "circle", "data_points": spo2_pts},
        ],
    }
    bp_plot = {
        "$schema": "urn:quiet-ui:schema:v9:plot",
        "id": "v03-bp-trend-chart",
        "metadata": {"title": "Resting Blood Pressure Trend", "rigor_level": "L1"},
        "plot_kind": "cartesian",
        "show_l1_envelopes": True,
        "axes": {
            "x_axis": {"quantity": "Check-In", "unit": "1", "quantity_calculus": "Check-In Reading (1 to 10)", "scale_type": "linear", "domain": [1, 10]},
            "y_axis": {"quantity": "Blood Pressure", "unit": "mmHg", "quantity_calculus": "Blood Pressure (mmHg)", "scale_type": "linear", "domain": [55, 85]},
        },
        "envelopes": [
            {"label": "Call < 65 mmHg", "threshold_value": 65.0, "type": "warning", "direction": "lower", "stroke_color": "var(--status-warn)"},
        ],
        "series": [
            {"id": "map_home", "name": "Resting Blood Pressure (mmHg)", "epistemic_type": "discrete_measurement", "connect_piecewise": True, "term": "bp-threshold", "stroke_color": "var(--accent-focal)", "marker_glyph": "square", "data_points": map_pts},
        ],
    }
    chart_a = embed_compile(spo2_plot, "L1", "m3")
    chart_b = embed_compile(bp_plot, "L1", "m3")
    return (
        '<div class="qe-equation-bar" aria-label="Daily Care Plan">'
        '<span class="qe-eq-lhs">Daily Plan = </span>'
        '<button type="button" class="va-pill qe-eq-term qe-term-oxygen-goal" data-variant="chip" data-term="oxygen-goal" aria-pressed="false">Oxygen Target ≥ 92%</button>'
        '<span class="qe-eq-op"> + </span>'
        '<button type="button" class="va-pill qe-eq-term qe-term-hydration-check" data-variant="chip" data-term="hydration-check" aria-pressed="false">Hydration &amp; Standing Check</button>'
        '<span class="qe-eq-op"> → </span>'
        '<button type="button" class="va-pill qe-eq-term qe-term-bp-threshold" data-variant="chip" data-term="bp-threshold" aria-pressed="false">Clinic Call (&lt; 65 mmHg)</button>'
        '</div>'
        '<div class="v03-charts-grid">'
        f'<div class="v03-chart-slot" data-term="oxygen-goal">{chart_a}</div>'
        f'<div class="v03-chart-slot" data-term="bp-threshold">{chart_b}</div>'
        '</div>'
    )


def _build_v03_html(corpus: dict[str, Any], specs: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    map_m, spo2_m = cm["map_mmhg"], cm["spo2_pct"]
    l1_vitals_html, spo2_item, map_item = _build_v03_vitals(specs)
    charts_html = _build_v03_charts(spo2_item, map_item)

    return f"""<div class="v9-stage-inner v9-view-v03">
  <div class="va-m1-block-only v9-m1-folio">
    <span>HOME CARE SUMMARY · DISCHARGE RECOVERY PLAN</span>
    <span>OXYGEN GOAL ≥ {spo2_m["lower_limit"]:.1f}% · BP CHECK-IN {map_m["lower_limit"]:.1f} mmHg</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">HOME RECOVERY PLAN · DISCHARGE DAY 2</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">Morning Check-In</span>
        {render_handoff_link("01-clinical-icu-and-trials", "v01-icu-bedside-terminal", "<- Clinician Bedside Monitor")}
      </div>
    </div>
    <h1 class="v9-masthead-title">Post-Hospital Home Recovery Guide</h1>
    <p class="v9-masthead-sub">Shows daily oxygen and blood pressure goals in plain terms so patients know when to rest or call the nurse line.</p>
  </header>

  <section id="v03-today" class="v03-welcome-card" aria-label="Today's Summary">
    <h2>Today's Check-In Summary</h2>
    <p>Your oxygen level is <strong>{spo2_m["value"]:.1f}%</strong>, safely above your home goal of <strong>{spo2_m["lower_limit"]:.1f}%</strong>. Your resting blood pressure is <strong>{map_m["value"]:.1f} mmHg</strong>, just slightly below your <strong>{map_m["lower_limit"]:.1f} mmHg</strong> clinic check-in threshold—please hydrate, sit up slowly, and re-check in 15 minutes.</p>
  </section>

  <section id="v03-vitals" aria-label="Your Home Vitals">
    {l1_vitals_html}
  </section>

  <section id="v03-guide" class="v03-pedagogy-panel qe-pedagogy-scope" aria-label="Interactive Home Care Guide">
    {charts_html}
    <div class="v03-checklist-grid">
      <article class="v03-check-card" data-term="oxygen-goal">
        <h3>1. Oxygen Target ≥ {spo2_m["lower_limit"]:.1f}%</h3>
        <p>Current reading: {spo2_m["value"]:.1f}%. Sit upright for 2 minutes before clipping the finger sensor.</p>
        <label class="v03-check-label"><input type="checkbox" checked> Morning pulse-ox logged</label>
      </article>
      <article class="v03-check-card" data-term="hydration-check">
        <h3>2. Hydration &amp; Standing Check</h3>
        <p>Drink 1 glass of water and pause 30 seconds at the edge of the bed before standing.</p>
        <label class="v03-check-label"><input type="checkbox"> Morning hydration complete</label>
      </article>
      <article class="v03-check-card" data-term="bp-threshold">
        <h3>3. Clinic Call Threshold (&lt; {map_m["lower_limit"]:.1f} mmHg)</h3>
        <p>Current BP: {map_m["value"]:.1f} mmHg. Call triage if a repeat check stays below {map_m["lower_limit"]:.1f} mmHg or oxygen dips below {spo2_m["lower_limit"]:.1f}%.</p>
        <label class="v03-check-label"><input type="checkbox"> Repeat BP cuff check in 15 min</label>
      </article>
    </div>
  </section>

  <section id="v03-care-team" class="va-card" aria-label="Care Team Support">
    <h2 class="qe-fig-title">When to Contact Your Care Team</h2>
    <p>Call your post-ICU recovery nurse line if resting oxygen stays below <strong>{spo2_m["lower_limit"]:.1f}%</strong>, resting blood pressure repeats below <strong>{map_m["lower_limit"]:.1f} mmHg</strong>, or you feel dizzy upon standing.</p>
  </section>
</div>"""


def build_world_01(corpora_dir: Path) -> dict[str, Any]:
    """Compile World 01 views, templates, and Quiet-Bridge provenance metadata."""
    spec_files = {
        "scalars": "v01_icu_ventilator_scalars.json",
        "scope": "v01_icu_hemodynamic_scope.json",
        "forest": "v02_trial_consort_forest.json",
        "ae_table": "v02_trial_adverse_events_table.json",
    }
    corpus, bp, specs = load_world_inputs(corpora_dir, "01-clinical-icu-and-trials", spec_files)
    html_map = {
        "v01-icu-bedside-terminal": _build_v01_html(corpus, specs),
        "v02-trial-regulatory-brief": _build_v02_html(corpus, specs),
        "v03-patient-recovery-companion": _build_v03_html(corpus, specs),
    }
    map_val = float(corpus["canonical_metrics"]["map_mmhg"]["value"])
    v01_status = [
        {"text": "▲ 1 CAUTION", "variant": "status", "state": "warn"},
        {"text": f"MAP {map_val:.1f} mmHg", "variant": "plain", "state": "warn"},
        {"text": "NTP Synced", "variant": "status", "state": "nominal"},
    ]
    view_cfg = {
        "v01-icu-bedside-terminal": {
            "option_label": "v01 · Hospital Bedside Monitor", "default_medium": "m4",
            "chromatic_code": "c4", "default_nav": "n3", "allowed_navs": ["n3", "n0", "n2"],
            "nav_icon": "heart-pulse", "nav_brand": "Bed ICU-04",
            "topbar_brand": "BED ICU-04 · PT-0482 · Sepsis Protocol", "rail_brand": "Monitor Subsystems",
            "topbar_status": v01_status, "nav_items": ["Hemodynamics", "Ventilator", "Infusions", "Event Log"],
            "nav_anchors": ["v01-hemo", "v01-vent", "v01-infusions", "v01-alarms"],
            "inv_col": "v01-icu-bedside-terminal (L3)", "short_tag": "v01",
        },
        "v02-trial-regulatory-brief": {
            "option_label": "v02 · Clinical Trial Results", "default_medium": "m2",
            "chromatic_code": "c3", "default_nav": "n2", "allowed_navs": ["n2", "n0"],
            "nav_icon": "file-medical", "nav_brand": "CONSORT Brief",
            "topbar_brand": "CONSORT Brief", "rail_brand": "CONSORT Brief",
            "topbar_status": [], "nav_items": ["Disposition", "Cohort & Methods", "Subgroup Forest", "KDIGO Safety", "SAP Appendix"],
            "nav_anchors": ["v02-disposition", "v02-methods", "v02-forest", "v02-safety", "v02-sap"],
            "inv_col": "v02-trial-regulatory-brief (L3)", "short_tag": "v02",
        },
        "v03-patient-recovery-companion": {
            "option_label": "v03 · Patient Recovery Guide", "default_medium": "m3",
            "chromatic_code": "c2", "default_nav": "n2", "allowed_navs": ["n2", "n4", "n0"],
            "nav_icon": "hand-holding-medical", "nav_brand": "Recovery Guide",
            "topbar_brand": "Recovery Guide", "rail_brand": "Recovery Guide",
            "topbar_status": [], "nav_items": ["Today", "Vitals Log", "Care Guide", "Care Team"],
            "nav_anchors": ["v03-today", "v03-vitals", "v03-guide", "v03-care-team"],
            "inv_col": "v03-patient-recovery-companion (L1)", "short_tag": "v03",
        },
    }
    return assemble_world_bundle(corpus, bp, "01 · Healthcare & Trials", view_cfg, html_map)
