#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 5 — World 04 (Civic Budget, Treasury Stress & STEM Lab) Builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from world_directional_views import build_v20_html
except ImportError:
    from src.views.world_directional_views import build_v20_html

try:
    from world_common import (
        assemble_world_bundle,
        cm_val,
        embed_compile,
        esc,
        format_math_html,
        load_world_inputs,
        render_params_aside,
    )
except ImportError:
    from src.views.world_common import (
        assemble_world_bundle,
        cm_val,
        embed_compile,
        esc,
        format_math_html,
        load_world_inputs,
        render_params_aside,
    )


def _build_v10_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    open_m = float(cm_val(cm, "opening_reserve_musd"))
    grant_m = float(cm_val(cm, "state_grant_musd"))
    bond_m = float(cm_val(cm, "utility_bond_musd"))
    hvac_m = float(cm_val(cm, "school_hvac_musd"))
    water_m = float(cm_val(cm, "water_main_musd"))
    close_m = float(cm_val(cm, "closing_contingency_musd"))
    floor_m = float(cm_val(cm, "reserve_floor_musd"))
    cov_pct = float(cm_val(cm, "reserve_coverage_pct"))
    waterfall_html = embed_compile(specs["waterfall"], "L2", "m2")
    table_html = embed_compile(specs["table"], "L2", "m2")

    return f"""<div class="v9-stage-inner v9-view-v10">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">FY2027 MUNICIPAL CAPITAL LEDGER · GAO GREEN BOOK · USWDS</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">FLOOR {floor_m:.1f} M USD</span>
        <span class="va-pill" data-variant="status" data-state="warn">WATER MAIN REVIEW</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">FY2027 Civic Capital Budget &amp; Reserve Policy Deck</h1>
    <p class="v9-masthead-sub">Six-step capital cash reconciliation from {open_m:.1f} M USD opening reserve to {close_m:.1f} M USD closing balance ({cov_pct:.1f}% statutory coverage).</p>
  </header>

  <section id="v10-gate" class="v9-gate-band" data-state="warn" aria-label="Board Trade Disposition">
    <div class="v9-gate-top">
      <h2 class="v9-gate-rec">APPROVE SCHOOL HVAC ({hvac_m:.1f} M USD); HOLD WATER MAIN ({water_m:.1f} M USD) OPTION B SPLIT</h2>
      <span class="va-pill" data-variant="status" data-state="warn">OPTION B HOLD</span>
    </div>
    <div class="v9-kpi-strip">
      <div class="v9-kpi-tile">
        <span class="va-kicker">OPENING + INFLOWS</span>
        <span class="v9-kpi-val va-nums">{open_m + grant_m + bond_m:.1f} M USD</span>
        <span class="v9-kpi-sub">{open_m:.1f} + {grant_m:.1f} Grant + {bond_m:.1f} Bond</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">CAPITAL OUTLAYS</span>
        <span class="v9-kpi-val va-nums" data-tone="warn">-{hvac_m + water_m:.1f} M USD</span>
        <span class="v9-kpi-sub">HVAC {hvac_m:.1f}M + Water {water_m:.1f}M</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">CLOSING CONTINGENCY</span>
        <span class="v9-kpi-val va-nums" data-tone="ok">{close_m:.1f} M USD</span>
        <span class="v9-kpi-sub">+{close_m - floor_m:.1f} M USD above {floor_m:.1f}M floor</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">RESERVE COVERAGE RATIO</span>
        <span class="v9-kpi-val va-nums">{cov_pct:.1f}%</span>
        <span class="v9-kpi-sub">Target Floor = 100.0% ({floor_m:.1f} M USD)</span>
      </div>
    </div>
    <div id="v10-fund-chips" class="v9-filter-bar va-sheet-hide" role="group" aria-label="Filter Capital Matrix Rows">
      <button type="button" class="va-pill v9-chip is-active" data-variant="chip" data-fund="all" aria-pressed="true" data-summary="Showing all 6 capital ledger rows (closing balance 26.9 M USD, 179.3% coverage).">All Lines (6)</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-fund="inflow" aria-pressed="false" data-summary="Base & Inflows: 48.0 M USD base + 16.5 M USD grant + 22.0 M USD utility bond (86.5 M USD pool).">Inflows (+38.5M)</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-fund="outlay" aria-pressed="false" data-summary="Capital Outlays: -28.4 M USD School HVAC GMP and -31.2 M USD Water Main Option B.">Outlays (-59.6M)</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-fund="review" aria-pressed="false" data-summary="REVIEW Item: Mainline Water Main Replacement (31.2 M USD) pending ductile-iron quote lock.">Review Only (1)</button>
    </div>
    <div id="v10-fund-readout" class="v9-filter-readout va-sheet-hide" aria-live="polite">Showing all 6 capital ledger rows (closing balance 26.9 M USD, 179.3% coverage).</div>
  </section>

  <section id="v10-waterfall" aria-label="FY2027 Capital Reserve Waterfall">{waterfall_html}</section>
  <section id="v10-budget-table" aria-label="GAO/USWDS Capital Obligation Matrix">{table_html}</section>
</div>"""


def _build_v11_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    shock = int(cm_val(cm, "rate_shock_bps"))
    floor_pct = float(cm_val(cm, "liquidity_floor_pct"))
    q1_pct = float(cm_val(cm, "q1_mc_median_liquidity_pct"))
    q8_pct = float(cm_val(cm, "q8_mc_median_liquidity_pct"))
    plot_html = embed_compile(specs["drawdown"], "L3", "m3")

    return f"""<div class="v9-stage-inner v9-view-v11">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">TREASURY-POOL-04 · FRED-CPIU-2026Q4 · n=10,000 MONTE CARLO</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">FLOOR {floor_pct:.1f}%</span>
        <span id="v11-gate-pill" class="va-pill" data-variant="status" data-state="nominal">HEADROOM +{q8_pct - floor_pct:.1f}%</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Treasury +{shock} bps Rate-Shock Liquidity Drawdown Solver</h1>
    <p class="v9-masthead-sub">Monte Carlo 10,000-path liquidity medians (±u_y) vs deterministic convexity decay against the {floor_pct:.1f}% statutory floor.</p>
  </header>

  <section id="v11-solver" class="v9-gate-band" aria-label="Rate-Shock Solver Summary">
    <div id="v11-shock-chips" class="v9-filter-bar va-sheet-hide" role="group" aria-label="Select Parallel Rate Shock">
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-q1="36.4%" data-q8="33.8%" data-headroom="+13.8%" data-state="nominal" data-pill="HEADROOM +13.8%" data-summary="0 bps Baseline: Q8 median liquidity 33.8% (+13.8% above 20.0% regulatory floor)." aria-pressed="false">0 bps Baseline</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-q1="36.4%" data-q8="29.4%" data-headroom="+9.4%" data-state="nominal" data-pill="HEADROOM +9.4%" data-summary="+150 bps Moderate Shock: Q8 median liquidity 29.4% (+9.4% above 20.0% floor)." aria-pressed="false">+150 bps Shock</button>
      <button type="button" class="va-pill v9-chip is-active" data-variant="chip" data-q1="{q1_pct:.1f}%" data-q8="{q8_pct:.1f}%" data-headroom="+{q8_pct - floor_pct:.1f}%" data-state="nominal" data-pill="HEADROOM +{q8_pct - floor_pct:.1f}%" data-summary="+{shock} bps Canonical Stress: Q1 {q1_pct:.1f}% -> Q8 {q8_pct:.1f}% ± 1.8% (+{q8_pct - floor_pct:.1f}% headroom above 20.0% floor)." aria-pressed="true">+{shock} bps Canonical</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-q1="36.4%" data-q8="21.4%" data-headroom="+1.4%" data-state="warn" data-pill="TIGHT +1.4%" data-summary="+350 bps Severe Tail Shock: Q8 median liquidity narrows to 21.4% (+1.4% margin above 20.0% floor; pause long-bond roll)." aria-pressed="false">+350 bps Severe</button>
    </div>
    <div id="v11-shock-readout" class="v9-filter-readout va-sheet-hide" aria-live="polite">+{shock} bps Canonical Stress: Q1 {q1_pct:.1f}% -&gt; Q8 {q8_pct:.1f}% ± 1.8% (+{q8_pct - floor_pct:.1f}% headroom above 20.0% floor).</div>
    <div class="v9-kpi-strip">
      <div class="v9-kpi-tile">
        <span class="va-kicker">Q1 OPENING LIQUIDITY</span>
        <span id="v11-q1-val" class="v9-kpi-val va-nums">{q1_pct:.1f}%</span>
        <span class="v9-kpi-sub">IQR Uncertainty ±1.1%</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">Q8 HORIZON MEDIAN</span>
        <span id="v11-q8-val" class="v9-kpi-val va-nums">{q8_pct:.1f}%</span>
        <span class="v9-kpi-sub">IQR Uncertainty ±1.8%</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">FLOOR HEADROOM (Q8)</span>
        <span id="v11-headroom-val" class="v9-kpi-val va-nums" data-tone="ok">+{q8_pct - floor_pct:.1f}%</span>
        <span class="v9-kpi-sub">Regulatory Floor: {floor_pct:.1f}%</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">COMMITTEE ACTION</span>
        <span class="v9-kpi-val va-nums">HOLD LADDER</span>
        <span class="v9-kpi-sub">Zero forced liquidation</span>
      </div>
    </div>
  </section>

  <section id="v11-plot" aria-label="Treasury Drawdown Plot">{plot_html}</section>
</div>"""


def _build_v12_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    v0 = float(cm_val(cm, "rc_v0_v"))
    tau = float(cm_val(cm, "rc_tau_s"))
    rc_html = embed_compile(specs["rc_lab"], "L3", "m2")

    return f"""<div class="v9-stage-inner v9-view-v12">
  <div class="va-m1-block-only v9-m1-folio">
    <span>FIRST-ORDER RC DISCHARGE LAB · RC-BENCH-RIG-04 · NIST-RC-LAB-2026</span>
    <span>{format_math_html("V_0")}={v0:.2f} V · τ={tau:.2f} s · LETTER 8.5×11 IN</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">STEM PHYSICS LAB · FIRST-ORDER DECAY · <span class="qe-unit">{format_math_html("f_s")} = 1.00 kHz</span></span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="status" data-state="nominal">RESIDUALS &lt; 0.8σ</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">First-Order RC Discharge &amp; Experimental Residual Lab</h1>
    <p class="v9-masthead-sub">Term-bound exponential decay V(t) = {v0:.2f} · exp(−t / {tau:.2f}) compared with 9 student oscilloscope points (±{format_math_html("u_y")}).</p>
  </header>

  <div class="v9-filter-bar va-sheet-hide" id="v12-role-chips" role="group" aria-label="Switch Audience Perspective">
    <button type="button" class="va-pill v9-chip is-active" data-variant="chip" data-role="student" aria-pressed="true">Student Lab View</button>
    <button type="button" class="va-pill v9-chip" data-variant="chip" data-role="instructor" aria-pressed="false">Instructor Rubric</button>
  </div>

  <section id="v12-student-note" class="v12-rubric-card" aria-label="Student Lab Procedure">
    <h2>Bench Procedure: Click Either Equation Term to Trace Curve vs. Scope Data</h2>
    <p>Check the oscilloscope crossing at 1·τ = {tau:.2f} s (predicted {format_math_html("V_c")} = 1.84 V vs observed 1.82 ± 0.05 V). Verify all 9 discrete voltage samples lie within the ±0.8σ normalized residual band before starting Lab Section 2.</p>
  </section>

  <section id="v12-instructor-note" class="v12-rubric-card v12-panel-hidden" aria-label="Instructor Grading Rubric">
    <h2>Instructor Metrology Rubric &amp; Uncertainty Audit</h2>
    <p>Require piecewise discrete oscilloscope points with explicit ±{format_math_html("u_y")} Type-B scope quantization bars (0.03–0.06 V) separated from the continuous analytical corridor (±4% rel). Penalize cubic Bezier smoothing over sparse bench samples.</p>
  </section>

  <section id="v12-lab" class="qe-pedagogy-scope" aria-label="Interactive RC Discharge Experiment">
    {rc_html}
    <div class="v12-step-grid">
      <article class="v12-step-card" data-term="tx">
        <h3>Oscilloscope Samples ({format_math_html("V_0")} = {v0:.2f} V)</h3>
        <p>Nine discrete Scope-10MHz-Ref captures starting at 4.98 ± 0.06 V and decaying to 0.08 ± 0.03 V at t = 10.0 s.</p>
      </article>
      <article class="v12-step-card" data-term="path_loss">
        <h3>Time-Constant Law (τ = {tau:.2f} s)</h3>
        <p>Analytical decay exp(−t / {tau:.2f}) drops to 1/e ≈ 36.8% of initial charge ({v0:.2f} V) at 2.40 s = 1.84 V.</p>
      </article>
    </div>
  </section>
</div>"""


def build_world_04(corpora_dir: Path) -> dict[str, Any]:
    """Compile World 04 views, templates, and plain-English design rationale metadata."""
    spec_files = {
        "waterfall": "v10_civic_capital_waterfall.json",
        "table": "v10_civic_budget_table.json",
        "drawdown": "v11_treasury_drawdown_plot.json",
        "rc_lab": "v12_stem_rc_cooling_lab.json",
        "repeatability": "v20_student_repeatability_dumbbell.json",
    }
    corpus, bp, specs = load_world_inputs(corpora_dir, "04-civic-finance-and-stem-learning", spec_files)
    html_map = {
        "v10-civic-capital-budget-deck": _build_v10_html(corpus, specs),
        "v11-treasury-stress-test-solver": _build_v11_html(corpus, specs),
        "v12-stem-interactive-lab": _build_v12_html(corpus, specs),
        "v20-student-capstone-lab-report": build_v20_html(corpus, specs),
    }
    view_cfg = {
        "v10-civic-capital-budget-deck": {
            "option_label": "v10 · Civic Capital Budget", "default_medium": "m2",
            "chromatic_code": "c3", "default_nav": "n1", "allowed_navs": ["n1", "n2", "n0"],
            "nav_icon": "landmark", "nav_brand": "Civic Budget FY27",
            "topbar_brand": "Civic Capital Budget FY2027", "rail_brand": "Budget Sections",
            "topbar_status": [], "nav_items": ["Trade Gate", "Cash Waterfall", "Reserve Table"],
            "nav_anchors": ["v10-gate", "v10-waterfall", "v10-budget-table"],
            "inv_col": "v10-civic-capital-budget-deck", "short_tag": "v10",
            "bias_removed": "Opaque Municipal Fund Jargon & Fiscal Illusion",
            "bias_risk": "Masks declining net contingency behind gross bond receipts.",
            "bias_replacement": "Six-step cash waterfall (48.0 → 26.9 M USD) with explicit Water Main Review flag.",
        },
        "v11-treasury-stress-test-solver": {
            "option_label": "v11 · Treasury Stress Solver", "default_medium": "m3",
            "chromatic_code": "c3", "default_nav": "n2", "allowed_navs": ["n2", "n1", "n0"],
            "nav_icon": "scale-balanced", "nav_brand": "Treasury Risk",
            "topbar_brand": "Treasury +250 bps Rate-Shock Solver", "rail_brand": "Solver Controls",
            "topbar_status": [], "nav_items": ["Shock Solver", "Drawdown Curve"],
            "nav_anchors": ["v11-solver", "v11-plot"],
            "inv_col": "v11-treasury-stress-test-solver", "short_tag": "v11",
            "bias_removed": "Deterministic Point-Forecast Masking",
            "bias_risk": "Hides Monte Carlo lower-tail liquidity dispersion.",
            "bias_replacement": "n=10,000 Monte Carlo medians (±u_y) paired with deterministic corridor and 20.0% minimum floor.",
        },
        "v12-stem-interactive-lab": {
            "option_label": "v12 · STEM RC Discharge Lab", "default_medium": "m2",
            "chromatic_code": "c2", "default_nav": "n1", "allowed_navs": ["n1", "n2", "n0"],
            "nav_icon": "flask", "nav_brand": "RC Physics Lab",
            "topbar_brand": "RC Discharge Lab · τ = 2.40 s", "rail_brand": "Lab Sections",
            "topbar_status": [], "nav_items": ["Lens Guide", "Experiment Plot"],
            "nav_anchors": ["v12-role-chips", "v12-lab"],
            "inv_col": "v12-stem-interactive-lab", "short_tag": "v12",
            "bias_removed": "Notation-First Overload & Dot-Connecting",
            "bias_risk": "Learners mistake smoothed splines for physical oscilloscope data.",
            "bias_replacement": "Term-bound V₀ and exp(−t/τ) pills coupled to discrete ±u_y oscilloscope samples + residuals.",
        },
        "v20-student-capstone-lab-report": {
            "option_label": "v20 · Student Capstone Lab Report", "default_medium": "m2",
            "chromatic_code": "c2", "default_nav": "n1", "allowed_navs": ["n1", "n2", "n0"],
            "nav_icon": "graduation-cap", "nav_brand": "Capstone Lab",
            "topbar_brand": "Capstone Lab Report · τ = 2.40 s", "rail_brand": "Report Sections",
            "topbar_status": [], "nav_items": ["Headline Claim", "Bench Repeatability", "Self-Critique"],
            "nav_anchors": ["v20-claim", "v20-evidence", "v20-critique"],
            "inv_col": "v20-student-capstone-lab-report", "short_tag": "v20",
            "invariants_fallback": {
                "baseline": "First-order RC discharge V_0 * exp(-t / tau) from V_0 = 5.00 V predicting 1.84 V at tau = 2.40 s.",
                "provenance": "Pairs five-bench repeatability dumbbell against raw calibrated oscilloscope curve and error budget.",
                "margin": "Five-station mean 1.82 V matches 1.84 V theory within ±0.05 V repeatability and <= 0.8 sigma.",
                "disposition": "Cleared student self-critique checklist for educator and capstone judge grading signoff.",
            },
            "bias_removed": "Narrative-Last Lab Logs & Uncalibrated Averaging",
            "bias_risk": "Forces judges to hunt through chronology for whether error bounds actually hold across rigs.",
            "bias_replacement": "Lead-with-claim capstone defense pairing repeatability dumbbell with error bounds and self-critique.",
        },
    }
    return assemble_world_bundle(corpus, bp, "04 · Finance & STEM Lab", view_cfg, html_map)
