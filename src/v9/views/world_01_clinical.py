#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 4 — World 01 (Clinical ICU, Phase III Trials & Patient Companion) Builder."""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
if str(EVIDENCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EVIDENCE_SCRIPTS))

from compile_evidence import compile_spec  # noqa: E402


def _embed_compile(spec: dict[str, Any], rigor: str, medium: str) -> str:
    return compile_spec(spec, rigor=rigor, medium=medium, theme="white", include_spec_drawer=False, chrome="embedded")


def _parse_blueprint_tables(md_text: str) -> dict[str, list[dict[str, str]]]:
    """Parse markdown tables from distillation_blueprint.md by section heading."""
    sections: dict[str, list[dict[str, str]]] = {}
    cur_sec = ""
    headers: list[str] = []
    for raw in md_text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            cur_sec = line[3:].strip()
            headers = []
            sections[cur_sec] = []
        elif line.startswith("|") and cur_sec:
            cells = [c.strip().replace("`", "").replace("**", "") for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                continue
            if not headers:
                headers = cells
            elif len(cells) == len(headers):
                sections[cur_sec].append(dict(zip(headers, cells)))
    return sections


def _inject_fig_class(fig_html: str, extra_cls: str) -> str:
    return fig_html.replace('class="va-figure-card qe-figure"', f'class="va-figure-card qe-figure {extra_cls}"', 1)


def _inject_mobile_tile(scalars_html: str, dropout_s: float) -> str:
    tile = (
        '\n<div class="qe-scalar-card v01-mobile-only-tile">'
        '<h3 class="qe-scalar-title">Artifact Gap</h3>'
        '<div class="qe-scalar-zone2 qe-scalar-val-row">'
        f'<div class="qe-scalar-val-wrap"><span class="qe-scalar-val va-nums">{dropout_s:.1f}\u00a0s</span></div>'
        '<div class="qe-scalar-disp"><span class="va-pill" data-variant="status" data-state="warn">CHECK</span></div>'
        '</div></div>'
    )
    marker = '</div><figcaption class="va-figure-caption">'
    if marker in scalars_html:
        return scalars_html.replace(marker, tile + marker, 1)
    return scalars_html


def _build_v01_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    map_m = cm["map_mmhg"]
    peep_cmd = cm["peep_cmd_cmh2o"]
    peep_act = cm["peep_act_cmh2o"]
    drop_m = cm["dropout_duration_s"]

    scalars_html = _embed_compile(specs["scalars"], "L3", "m4")
    scalars_html = _inject_fig_class(scalars_html, "v01-scalars-fig")
    scalars_html = _inject_mobile_tile(scalars_html, float(drop_m["value"]))

    scope_html = _embed_compile(specs["scope"], "L3", "m4")
    scope_html = _inject_fig_class(scope_html, "v01-scope-fig")

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
    <div class="v9-masthead-tags">
      <span class="va-pill" data-variant="tag">PT-0482</span>
      <span class="va-pill" data-variant="status" data-state="warn">CAUTION</span>
    </div>
  </header>

  <section id="v01-vent" aria-label="Bedside Vital and Ventilator Scalars">
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
          <div class="v01-audit-item">[05:30:00Z] Motion-artifact dropout ({drop_m["value"]:.1f} s) bracketed T_A={drop_m["cursor_a_s"]:.1f} s to T_B={drop_m["cursor_b_s"]:.1f} s; verify transducer before titration.</div>
          <div class="v01-audit-item">[05:29:54Z] MAP excursion {map_m["value"]:.1f} mmHg below {map_m["lower_limit"]:.1f} mmHg floor (abort {map_m["abort_lower_limit"]:.1f} mmHg); PEEP {peep_act["value"]:.1f} vs {peep_cmd["value"]:.1f} cmH2O CMD.</div>
        </div>
      </div>
    </div>
  </section>
</div>"""


def _build_v02_html(corpus: dict[str, Any], specs: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    ov, ag, sf, lc, aki = cm["overall_hr"], cm["age_ge65_hr"], cm["sofa_ge8_hr"], cm["lactate_gt2_hr"], cm["aki_rate_pct"]
    forest_html = compile_spec(specs["forest"], rigor="L3", medium="m2", theme="white", include_spec_drawer=False, chrome="embedded")
    table_html = compile_spec(specs["ae_table"], rigor="L3", medium="m2", theme="white", include_spec_drawer=False, chrome="embedded")

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
    <p class="v9-masthead-sub">Executive gate disposition for CMO triage paired with CONSORT subgroup hazard ratios and KDIGO renal safety register.</p>
  </header>

  <div class="v02-book-spread">
    <div class="v02-left-page">
      <section id="v02-disposition" class="v02-gate-band" aria-label="Executive Gate Disposition">
        <div class="v02-gate-top">
          <h2 class="v02-gate-rec">RECOMMEND CONDITIONAL AUTHORIZATION: SOFA &gt;= 8 &amp; Lactate &gt; 2 <span class="qe-unit">mmol/L</span></h2>
          <span class="va-pill" data-variant="status" data-state="warn">CONDITIONAL</span>
        </div>
        <div class="v02-kpi-strip">
          <div class="v02-kpi-tile">
            <span class="va-kicker">28-DAY MORTALITY HR</span>
            <span class="v02-kpi-val va-nums">{ov["value"]:.2f} [{ov["ci_low"]:.2f}, {ov["ci_high"]:.2f}]</span>
            <span class="v02-kpi-sub">Primary ITT (n = {ov["cohort_n"]:,})</span>
          </div>
          <div class="v02-kpi-tile">
            <span class="va-kicker">SOFA &gt;= 8 STRATUM</span>
            <span class="v02-kpi-val va-nums">{sf["value"]:.2f} [{sf["ci_low"]:.2f}, {sf["ci_high"]:.2f}]</span>
            <span class="v02-kpi-sub">Decisive benefit (n = {sf["cohort_n"]})</span>
          </div>
          <div class="v02-kpi-tile">
            <span class="va-kicker">LACTATE &gt; 2 <span class="qe-unit">mmol/L</span></span>
            <span class="v02-kpi-val va-nums">{lc["value"]:.2f} [{lc["ci_low"]:.2f}, {lc["ci_high"]:.2f}]</span>
            <span class="v02-kpi-sub">Decisive benefit (n = {lc["cohort_n"]})</span>
          </div>
          <div class="v02-kpi-tile">
            <span class="va-kicker">KDIGO STAGE &gt;= 2 AKI</span>
            <span class="v02-kpi-val va-nums">{aki["value"]:.1f} ± {aki["expanded_uncertainty"]:.1f}%</span>
            <span class="v02-kpi-sub">vs {aki["control_value"]:.1f}% Control Arm</span>
          </div>
        </div>
        <div id="v02-subgroup-chips" class="v02-filter-bar va-sheet-hide" role="group" aria-label="Filter Clinical Subgroups">
          <button type="button" class="va-pill v02-chip is-active" data-variant="chip" data-subgroup="all" aria-pressed="true" data-summary="All 4 CONSORT strata shown (ITT n=1,240; Overall HR 0.74 [0.61, 0.90]).">All Strata</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="overall" aria-pressed="false" data-summary="Overall Cohort (n=1,240): HR 0.74 [0.61, 0.90] — statistically decisive below HR=1.0.">Overall (n=1,240)</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="age" aria-pressed="false" data-summary="Age >= 65 yr (n=612): HR 0.79 [0.62, 1.01] crosses null (1.0); muted secondary series.">Age &gt;= 65 (n=612)</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="sofa" aria-pressed="false" data-summary="SOFA >= 8 (n=486): HR 0.68 [0.52, 0.89] — strongest vasopressor-sparing effect.">SOFA &gt;= 8 (n=486)</button>
          <button type="button" class="va-pill v02-chip" data-variant="chip" data-subgroup="lactate" aria-pressed="false" data-summary="Lactate > 2 mmol/L (n=704): HR 0.71 [0.54, 0.93] — decisive survival margin.">Lactate &gt; 2 (n=704)</button>
        </div>
        <div id="v02-filter-readout" class="v02-filter-readout va-sheet-hide" aria-live="polite">All 4 CONSORT strata shown (ITT n=1,240; Overall HR 0.74 [0.61, 0.90]).</div>
      </section>

      <article id="v02-methods" class="v02-prose-col">
        <h2>Cohort Design, Null-Crossing Stratification &amp; Renal Safety</h2>
        <p>Across the intention-to-treat population (n = {ov["cohort_n"]:,}, 620 protocol vs. 620 control), the protocol achieved an overall 28-day mortality hazard ratio of {ov["value"]:.2f} (95% CI [{ov["ci_low"]:.2f}, {ov["ci_high"]:.2f}]). Decisive benefit concentrates in high-acuity strata: SOFA &gt;= 8 (n = {sf["cohort_n"]}, HR {sf["value"]:.2f} [{sf["ci_low"]:.2f}, {sf["ci_high"]:.2f}]) and Lactate &gt; 2 mmol/L (n = {lc["cohort_n"]}, HR {lc["value"]:.2f} [{lc["ci_low"]:.2f}, {lc["ci_high"]:.2f}]).</p>
        <p>Conversely, the Age &gt;= 65 yr subgroup (n = {ag["cohort_n"]}, HR {ag["value"]:.2f} [{ag["ci_low"]:.2f}, {ag["ci_high"]:.2f}]) crosses the 1.0 null boundary and remains deemphasized relative to significant high-acuity strata. KDIGO Stage &gt;= 2 acute kidney injury decreased to {aki["value"]:.1f} ± {aki["expanded_uncertainty"]:.1f}% versus {aki["control_value"]:.1f}% control, while refractory hypotension (MAP &lt; 65 mmHg, 8.6 ± 1.5% vs. 11.2%) remains under mandatory WATCH surveillance.</p>
      </article>
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
    map_item["quantity"]["target_label"] = "Goal: 65 mmHg or higher"
    map_item["status_annunciator"]["l1_label"] = "Recheck in 15 min"

    spo2_item = copy.deepcopy(raw_sc["items"][2])
    spo2_item["metadata"]["title"] = "Oxygen Level (Pulse Oximeter)"
    spo2_item["metadata"]["plain_label"] = "Finger Sensor Check"
    spo2_item["metadata"].pop("subsystem", None)
    spo2_item["quantity"]["target_label"] = "Goal: 92% or higher"
    spo2_item["status_annunciator"]["l1_label"] = "On Track"

    l1_spec = {
        "$schema": "urn:quiet-ui:schema:v9:scalar",
        "id": "v03-patient-home-vitals",
        "metadata": {
            "title": "Your Daily Recovery Vitals",
            "description": "Plain-language home targets from your hospital discharge plan.",
            "rigor_level": "L1",
            "timestamp_utc": "2026-11-17T05:30:00Z",
        },
        "items": [spo2_item, map_item],
    }
    html = compile_spec(l1_spec, rigor="L1", medium="m3", theme="white", include_spec_drawer=False, chrome="embedded")
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
            {"label": "Goal >= 92%", "threshold_value": 92.0, "type": "warning", "direction": "lower", "stroke_color": "var(--tint-emerald-fg)"},
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
    chart_a = compile_spec(spo2_plot, rigor="L1", medium="m3", theme="white", include_spec_drawer=False, chrome="embedded")
    chart_b = compile_spec(bp_plot, rigor="L1", medium="m3", theme="white", include_spec_drawer=False, chrome="embedded")
    return (
        '<div class="qe-equation-bar" aria-label="Daily Care Plan">'
        '<span class="qe-eq-lhs">Daily Plan = </span>'
        '<button type="button" class="va-pill qe-eq-term qe-term-oxygen-goal" data-variant="chip" data-term="oxygen-goal" aria-pressed="false">Oxygen Target &gt;= 92%</button>'
        '<span class="qe-eq-op"> + </span>'
        '<button type="button" class="va-pill qe-eq-term qe-term-hydration-check" data-variant="chip" data-term="hydration-check" aria-pressed="false">Hydration &amp; Standing Check</button>'
        '<span class="qe-eq-op"> -&gt; </span>'
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
    <span>OXYGEN GOAL &gt;= {spo2_m["lower_limit"]:.1f}% · BP CHECK-IN {map_m["lower_limit"]:.1f} mmHg</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">HOME RECOVERY PLAN · DISCHARGE DAY 2</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">Morning Check-In</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Post-Hospital Home Recovery Guide</h1>
    <p class="v9-masthead-sub">Clear daily oxygen and blood pressure goals without hospital jargon.</p>
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
        <h3>1. Oxygen Target &gt;= {spo2_m["lower_limit"]:.1f}%</h3>
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
    wdir = corpora_dir / "01-clinical-icu-and-trials"
    corpus = json.loads((wdir / "corpus.json").read_text(encoding="utf-8"))
    bp = _parse_blueprint_tables((wdir / "distillation_blueprint.md").read_text(encoding="utf-8"))
    spec_files = {
        "scalars": "v01_icu_ventilator_scalars.json", "scope": "v01_icu_hemodynamic_scope.json",
        "forest": "v02_trial_consort_forest.json", "ae_table": "v02_trial_adverse_events_table.json",
    }
    specs = {k: json.loads((wdir / "evidence" / fn).read_text(encoding="utf-8")) for k, fn in spec_files.items()}
    bias_by_id = {r["View ID"]: r for r in bp.get("2. Scrubbed Bias Ledger", [])}
    inv_rows = bp.get("3. Four Universal Audience Evaluation Invariants Audit", [])
    mb_rows = bp.get("4. Adversarial Murder-Board Red-Team Audit", [])
    ledger_rows = [
        {"metric_id": r.get("metric_id", ""), "canonical_value": r.get("Canonical Value", ""), "unit": r.get("Unit", ""), "views": r.get("Views Consuming", "")}
        for r in bp.get("5. Canonical Numerical Conservation Ledger", [])
    ]
    html_map = {
        "v01-icu-bedside-terminal": _build_v01_html(corpus, specs),
        "v02-trial-regulatory-brief": _build_v02_html(corpus, specs),
        "v03-patient-recovery-companion": _build_v03_html(corpus, specs),
    }
    map_val = float(corpus["canonical_metrics"]["map_mmhg"]["value"])
    v01_status = [
        {"text": f"1 Active Caution: MAP {map_val:.1f} mmHg", "variant": "status", "state": "warn"},
        {"text": "NTP Synced", "variant": "status", "state": "nominal"},
    ]
    view_cfg = {
        "v01-icu-bedside-terminal": ("v01 · ICU Bedside Terminal (M4 · L3)", "m4", "c4", "n3", ["n3", "n0", "n2"], "fa-heart-pulse", "Bed ICU-04", "BED ICU-04 · PT-0482 · Sepsis Protocol", "Monitor Subsystems", v01_status, ["Hemodynamics", "Ventilator", "Infusions", "Event Log"], ["v01-hemo", "v01-vent", "v01-infusions", "v01-alarms"], "v01-icu-bedside-terminal (L3)", "v01"),
        "v02-trial-regulatory-brief": ("v02 · Trial Regulatory Brief (M2↔M1 · L3)", "m2", "c3", "n1", ["n1", "n2", "n0"], "fa-file-medical", "CONSORT Brief", "CONSORT Brief", "CONSORT Brief", [], ["Disposition", "Cohort & Methods", "Subgroup Forest", "KDIGO Safety", "SAP Appendix"], ["v02-disposition", "v02-methods", "v02-forest", "v02-safety", "v02-sap"], "v02-trial-regulatory-brief (L3)", "v02"),
        "v03-patient-recovery-companion": ("v03 · Patient Recovery (M3 · L1)", "m3", "c2", "n2", ["n2", "n4", "n0"], "fa-hand-holding-medical", "Recovery Guide", "Recovery Guide", "Recovery Guide", [], ["Today", "Vitals Log", "Care Guide", "Care Team"], ["v03-today", "v03-vitals", "v03-guide", "v03-care-team"], "v03-patient-recovery-companion (L1)", "v03"),
    }
    inv_keys = (("Baseline", "baseline"), ("Provenance", "provenance"), ("Margin", "margin"), ("Disposition", "disposition"))
    views_meta, templates = [], {}
    for vw in corpus["views"]:
        vid = vw["view_id"]
        opt_lbl, def_med, chrom, def_nav, allowed, icon, brand, top_brand, rail_brand, top_status, nav_items, anchors, inv_col, short_tag = view_cfg[vid]
        bias = bias_by_id.get(vid, {})
        inv_dict = {dst: row.get(inv_col, "") for row in inv_rows for token, dst in inv_keys if token in row.get("Invariant", "")}
        mb_list = [
            {"rubric": r.get("Rubric / Persona", ""), "finding": r.get("Audit Finding", ""), "verdict": r.get("Verdict", "PASS")}
            for r in mb_rows if short_tag in r.get("Audited View(s)", "")
        ]
        views_meta.append({
            "view_id": vid, "title": vw["title"], "option_label": opt_lbl,
            "default_medium": def_med, "chromatic_code": chrom, "default_nav": def_nav, "allowed_navs": allowed,
            "nav_icon": icon, "nav_brand": brand, "topbar_brand": top_brand, "rail_brand": rail_brand,
            "topbar_status": top_status, "nav_items": nav_items, "nav_anchors": anchors,
            "vector_summary": f'{vw["presenter"]} -> {vw["audience"]} × {"/".join(vw["tempos"])} × {"/".join(vw["mediums"])} × {vw["chromatic_budget"]} × {vw["rigor_level"]}',
            "actionable_disposition": vw["actionable_disposition"],
            "bias_removed": bias.get("Presenter Bias Identified", ""),
            "bias_risk": bias.get("Risk to Target Audience", ""),
            "bias_replacement": bias.get("Scrubbed / Distilled Replacement", ""),
            "invariants": inv_dict, "murder_board": mb_list,
        })
        templates[vid] = html_map[vid]

    return {
        "world_meta": {
            "world_id": corpus["world_id"],
            "world_label": "01 · Clinical ICU & Trials",
            "title": corpus["title"],
            "views": views_meta,
            "conservation_ledger": ledger_rows,
        },
        "templates": templates,
    }
