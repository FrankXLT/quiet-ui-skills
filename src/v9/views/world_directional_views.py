# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 6.2 — Directional Audience & Planner Views (v19, v20, v21)."""

from __future__ import annotations

from typing import Any

try:
    from world_common import cm_val, embed_compile, esc
except ImportError:
    from src.v9.views.world_common import cm_val, embed_compile, esc


def build_v19_html(corpus: dict[str, Any], specs: dict[str, Any]) -> str:
    """Eng Lead -> PM/Product: Release Critical-Path Gantt + 38px Interactive Blocker Triage."""
    cm = corpus["canonical_metrics"]
    p99 = float(cm_val(cm, "p99_threshold_ms"))
    gap = float(cm_val(cm, "scrape_dropout_s"))
    hex_pol = str(cm_val(cm, "fips_policy_hex"))
    flt = float(cm_val(cm, "roadmap_float_days"))
    n_blk = int(cm_val(cm, "tracked_blockers"))
    gantt_html = embed_compile(specs["roadmap_gantt"], "L2", "m3")

    rows = [
        ("r1", "blocked", "P1", "Patch 12.0 s OTel scrape blindness before canary", "fault", "BLOCKED", "Owner: Observability · Critical Path (Day 0 → 4) · 0.0 d float"),
        ("r2", "blocked", "P1", f"Restore API p99 latency under {p99:.1f} ms ceiling", "fault", "CRITICAL", "Owner: Core Proxy · Depends on OTel patch (Day 4 → 8) · 0.0 d float"),
        ("r3", "active", "P2", f"Enforce strict TLS {hex_pol} policy gate across zones", "warn", f"+{flt:.1f} d FLOAT", f"Owner: Security · Non-blocking parallel track (+{flt:.1f} d schedule float)"),
        ("r4", "done", "P2", "Sign off 4-blocker soak checklist and GA cutover", "nominal", "TRACKED", f"Owner: Release PM · Verifies all {n_blk} tracked launch blockers before GA"),
    ]
    rows_html = "".join(
        f'<button type="button" class="v9-triage-row" role="option" aria-selected="{"true" if i == 0 else "false"}" '
        f'tabindex="{"0" if i == 0 else "-1"}" '
        f'data-v19-state="{st}" data-v19-meta="{esc(meta)}">'
        f'<span class="va-pill" data-variant="tag">{esc(prio)}</span>'
        f'<span class="v9-triage-title">{esc(ttl)}</span>'
        f'<span class="va-pill" data-variant="status" data-state="{sstate}">{esc(slbl)}</span>'
        '</button>'
        for i, (_rid, st, prio, ttl, sstate, slbl, meta) in enumerate(rows)
    )
    return f"""<div class="v9-stage-inner v9-view-v19">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">PLATFORM-GA-ROADMAP · CRITICAL-PATH-GANTT · PRODUCT-TRIAGE</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">{esc(hex_pol)}</span>
        <span class="va-pill" data-variant="status" data-state="warn">HOLD · +{flt:.1f} D FLOAT</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Product Release Roadmap &amp; Critical-Path Blocker Triage</h1>
    <p class="v9-masthead-sub">Conserves {p99:.1f} ms tail ceiling, {gap:.1f} s scrape gap fix, {esc(hex_pol)} policy gate, +{flt:.1f} d parallel security buffer, and {n_blk} tracked launch blockers.</p>
  </header>

  <section id="v19-disposition" class="v9-br-banner" aria-label="Release Readiness Summary">
    <div class="v9-br-head">
      <h2 class="v9-sec-title">Release Gate: CONDITIONAL HOLD · {n_blk} Tracked Launch Blockers Open</h2>
      <span class="va-pill" data-variant="status" data-state="warn">HOLD · +{flt:.1f} D FLOAT</span>
    </div>
    <p class="qe-fig-desc">Critical path locks GA behind OTel telemetry gap closure ({gap:.1f} s blindspot) and tail latency recovery (≤ {p99:.1f} ms), while {esc(hex_pol)} mTLS verification retains +{flt:.1f} d parallel buffer.</p>
    <div class="v9-br-checks">
      <div class="v9-br-check"><span>p99 Ceiling Target</span><strong class="va-nums">≤ {p99:.1f} ms</strong></div>
      <div class="v9-br-check"><span>Scrape Gap Patch</span><strong class="va-nums">{gap:.1f} s window</strong></div>
      <div class="v9-br-check"><span>Policy Register</span><strong class="va-nums">{esc(hex_pol)}</strong></div>
      <div class="v9-br-check"><span>Security Track Buffer</span><strong class="va-nums">+{flt:.1f} d ({n_blk} blockers)</strong></div>
    </div>
  </section>

  <section id="v19-gantt" aria-label="Release Critical-Path Gantt">{gantt_html}</section>

  <section id="v19-triage" class="va-card" aria-label="Launch Blocker Triage Queue">
    <div class="v9-triage-wrap">
      <div class="v9-triage-bar">
        <h2 class="v9-sec-title">Launch Blocker Queue ({n_blk} Workstreams)</h2>
        <div class="v9-demo-row" id="v19-filter-chips" role="group" aria-label="Filter blockers">
          <button type="button" class="va-pill" data-variant="chip" data-v19-filter="all" aria-pressed="true">All ({n_blk})</button>
          <button type="button" class="va-pill" data-variant="chip" data-v19-filter="blocked" aria-pressed="false">Critical Path (2)</button>
          <button type="button" class="va-pill" data-variant="chip" data-v19-filter="active" aria-pressed="false">Parallel Float (1)</button>
        </div>
      </div>
      <div class="v9-triage-list" role="listbox" aria-label="Release blockers">{rows_html}</div>
      <div class="v9-triage-meta" id="v19-triage-detail" aria-live="polite">{esc(rows[0][6])}</div>
    </div>
  </section>
</div>"""


def build_v20_html(corpus: dict[str, Any], specs: dict[str, Any]) -> str:
    """Student -> Educator/Judge upward lab report following Claim -> Method -> Data -> Error -> Critique."""
    cm = corpus["canonical_metrics"]
    v0 = float(cm_val(cm, "rc_v0_v"))
    tau = float(cm_val(cm, "rc_tau_s"))
    v_tau = float(cm_val(cm, "rc_vtau_v"))
    v_mean = float(cm_val(cm, "rc_mean_trial_v"))
    u_cal = float(cm_val(cm, "rc_uncertainty_v"))
    sig = float(cm_val(cm, "rc_sigma_bound"))
    scope_html = embed_compile(specs["rc_lab"], "L3", "m2")
    dumb_html = embed_compile(specs["repeatability"], "L3", "m2")

    return f"""<div class="v9-stage-inner v9-view-v20">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">CAPSTONE-RC-LAB · 5-BENCH-REPEATABILITY · STUDENT-TO-EDUCATOR</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">V₀ = {v0:.2f} V</span>
        <span class="va-pill" data-variant="status" data-state="nominal">PASS · ≤ {sig:.1f} σ</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Student Capstone RC Discharge Repeatability Report</h1>
    <p class="v9-masthead-sub">Upward verification from {v0:.2f} V initial charge: five-station 1τ mean {v_mean:.2f} V matches {v_tau:.2f} V law at τ = {tau:.2f} s within ±{u_cal:.2f} V uncertainty.</p>
  </header>

  <section id="v20-claim" aria-label="Headline Experimental Claim">
    <div class="v20-claim-box">
      <div class="v9-br-head">
        <h2 class="v9-sec-title">Headline Claim: Bench RC Decay Confirms τ = {tau:.2f} s Within ±{u_cal:.2f} V Repeatability</h2>
        <span class="va-pill" data-variant="status" data-state="nominal">PASS · ≤ {sig:.1f} σ</span>
      </div>
      <p class="qe-fig-desc">Discharging from {v0:.2f} V across five lab benches yielded mean 1τ voltage {v_mean:.2f} V vs {v_tau:.2f} V theoretical crossing (exp(−1) · {v0:.2f} V), holding every residual inside ±{sig:.1f} σ with combined instrument uncertainty ±{u_cal:.2f} V.</p>
      <div class="v20-rubric-bar" id="v20-rubric-chips" role="group" aria-label="Reviewer rubric lens">
        <span class="v9-demo-label">Rubric Focus:</span>
        <button type="button" class="va-pill" data-variant="chip" data-v20-focus="claim" aria-pressed="true">Claim &amp; Theory</button>
        <button type="button" class="va-pill" data-variant="chip" data-v20-focus="repeat" aria-pressed="false">Bench Repeatability</button>
        <button type="button" class="va-pill" data-variant="chip" data-v20-focus="error" aria-pressed="false">Error Bounds</button>
      </div>
    </div>
    <div class="v20-method-grid">
      <div class="v9-demo-subcard" data-v20-card="claim"><span class="v9-demo-label">Step Input &amp; Law</span><strong class="va-nums">{v0:.2f} V · τ = {tau:.2f} s</strong><span class="qe-fig-desc">Theoretical 1τ target = {v_tau:.2f} V</span></div>
      <div class="v9-demo-subcard" data-v20-card="repeat"><span class="v9-demo-label">5-Station Mean</span><strong class="va-nums">{v_mean:.2f} V observed</strong><span class="qe-fig-desc">Pre-zero offset drift corrected</span></div>
      <div class="v9-demo-subcard" data-v20-card="error"><span class="v9-demo-label">Uncertainty &amp; Residual</span><strong class="va-nums">±{u_cal:.2f} V · ≤ {sig:.1f} σ</strong><span class="qe-fig-desc">All 9 scope runs within envelope</span></div>
    </div>
  </section>

  <section id="v20-evidence" class="v9-dual-grid" aria-label="Replicated Evidence &amp; Station Dumbbell">
    <div id="v20-repeatability" class="v9-dual-col">{dumb_html}</div>
    <div id="v20-trace" class="v9-dual-col">{scope_html}</div>
  </section>

  <section id="v20-critique" class="va-card" aria-label="Self-Critique &amp; Judge Checklist">
    <div class="v9-br-head">
      <h2 class="v9-sec-title">Error Budget &amp; Self-Critique Verification Checklist</h2>
      <span class="va-nums" id="v20-focus-note" aria-live="polite">Focus: Claim &amp; Theory verified against {v_tau:.2f} V model</span>
    </div>
    <div class="v9-br-checks">
      <div class="v9-br-check" data-v20-card="claim"><span>1. Zero-adjusted 1τ fit matches exp(−1) law ({v_tau:.2f} V)</span><span class="va-pill" data-variant="status" data-state="nominal">VERIFIED</span></div>
      <div class="v9-br-check" data-v20-card="repeat"><span>2. 5-station spread bounded around {v_mean:.2f} V mean</span><span class="va-pill" data-variant="status" data-state="nominal">VERIFIED</span></div>
      <div class="v9-br-check" data-v20-card="error"><span>3. Probe offset zeroed within ±{u_cal:.2f} V repeatability</span><span class="va-pill" data-variant="status" data-state="nominal">VERIFIED</span></div>
      <div class="v9-br-check" data-v20-card="error"><span>4. Max standardized residual bounded ≤ {sig:.1f} σ</span><span class="va-pill" data-variant="status" data-state="nominal">VERIFIED</span></div>
    </div>
  </section>
</div>"""


def build_v21_html(corpus: dict[str, Any], specs: dict[str, Any]) -> str:
    """Field Tech -> Systems Engineer bottom-up Troubleshooting Note (TSN) + 8.0 h Bay Recovery."""
    cm = corpus["canonical_metrics"]
    ohm = int(cm_val(cm, "canfd_termination_ohm"))
    stub = float(cm_val(cm, "canfd_stub_max_m"))
    drop = float(cm_val(cm, "scope_dropout_us"))
    derate = float(cm_val(cm, "mcu_thermal_derate_c"))
    bte = float(cm_val(cm, "peak_bte_pct"))
    win_h = float(cm_val(cm, "bay_recovery_window_h"))
    bus_html = embed_compile(specs["bus_schematic"], "L2", "m3")
    gantt_html = embed_compile(specs["recovery_gantt"], "L2", "m3")

    return f"""<div class="v9-stage-inner v9-view-v21">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">TEST-BAY-04 · CAN-FD-STUB-TSN · FIELD-TO-SYSTEMS</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">DUAL {ohm} Ω EOL</span>
        <span class="va-pill" data-variant="status" data-state="fault" id="v21-esc-badge">ESCALATED · {win_h:.1f} H</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Field Anomaly Escalation TSN &amp; {win_h:.1f} h Bay Recovery</h1>
    <p class="v9-masthead-sub">Bottom-up handoff from bench troubleshooting: {drop:.2f} µs reflection dropout (&gt; {stub:.1f} m stub) plus {derate:.0f} °C MCU derate ahead of {bte:.1f}% BTE dyno re-qualification.</p>
  </header>

  <section id="v21-symptom" class="v21-handoff-banner" aria-label="Field Escalation Troubleshooting Note">
    <div class="v9-br-head">
      <h2 class="v9-sec-title">Fault Summary · Test-Bay 04 Stub Reflection &amp; MCU Thermal Derate</h2>
      <span class="va-pill" data-variant="status" data-state="fault">ESCALATED · {win_h:.1f} H</span>
    </div>
    <p class="qe-fig-desc">Tech bench isolated a {drop:.2f} µs CAN-FD frame dropout traced to an unterminated harness branch (&gt; {stub:.1f} m max stub against dual {ohm} Ω EOL) plus MCU enclosure excursion reaching {derate:.0f} °C derate ahead of {bte:.1f}% BTE dyno verification.</p>
    <div class="v9-br-checks">
      <div class="v9-br-check"><span>EOL Resistance</span><strong class="va-nums">Dual {ohm} Ω</strong></div>
      <div class="v9-br-check"><span>Stub Length Rule</span><strong class="va-nums">≤ {stub:.1f} m</strong></div>
      <div class="v9-br-check"><span>Measured Dropout</span><strong class="va-nums">{drop:.2f} µs</strong></div>
      <div class="v9-br-check"><span>Thermal / Retest</span><strong class="va-nums">{derate:.0f} °C · {bte:.1f}% BTE</strong></div>
    </div>
  </section>

  <section id="v21-diagnostics" class="v9-dual-grid" aria-label="Isolation Steps &amp; Bus Diagram">
    <div class="v9-dual-col va-card">
      <h2 class="v9-sec-title">Bench Isolation Sequence &amp; Handoff</h2>
      <div class="v21-step-nav" id="v21-step-chips" role="group" aria-label="Troubleshooting isolation stage">
        <button type="button" class="va-pill" data-variant="chip" data-v21-step="wire" aria-pressed="true">1. Harness &amp; {ohm} Ω</button>
        <button type="button" class="va-pill" data-variant="chip" data-v21-step="scope" aria-pressed="false">2. {drop:.2f} µs Scope</button>
        <button type="button" class="va-pill" data-variant="chip" data-v21-step="thermal" aria-pressed="false">3. {derate:.0f} °C Derate</button>
      </div>
      <div class="v9-demo-subcard v21-step-panel" data-v21-panel="wire">
        <strong>Physical Harness &amp; Stub Measurement</strong>
        <p class="qe-fig-desc">Trim temporary probe spur from 0.42 m down below {stub:.1f} m ceiling and confirm 60.0 Ω equivalent across CAN_H / CAN_L (dual {ohm} Ω EOL present).</p>
      </div>
      <div class="v9-demo-subcard v21-step-panel" data-v21-panel="scope" hidden>
        <strong>Differential Reflection Capture</strong>
        <p class="qe-fig-desc">Before trim, differential trace stalled for {drop:.2f} µs (0.90 to 1.25 µs window) triggering SOF arbitration fault recovery.</p>
      </div>
      <div class="v9-demo-subcard v21-step-panel" data-v21-panel="thermal" hidden>
        <strong>MCU Cooling &amp; Dyno Re-Qualification</strong>
        <p class="qe-fig-desc">Purge bay shroud until MCU case cools safely below {derate:.0f} °C derate threshold, then re-run full {bte:.1f}% BTE propulsion curve within {win_h:.1f} h.</p>
      </div>
      <div class="v9-guard-pad">
        <button type="button" class="v9-guard-btn" id="v21-handoff-arm" aria-expanded="false">Stage Systems Handoff</button>
        <button type="button" class="v9-guard-btn v9-guard-confirm" id="v21-handoff-send" hidden>Confirm Escalation Package</button>
        <button type="button" class="v9-guard-btn" id="v21-handoff-cancel" hidden>Cancel</button>
        <span class="va-pill" data-variant="status" data-state="warn" id="v21-handoff-status" aria-live="polite">BAY HOLD · PREPARE</span>
      </div>
    </div>
    <div id="v21-bus" class="v9-dual-col">{bus_html}</div>
  </section>

  <section id="v21-recovery" aria-label="Test-Bay {win_h:.1f} h Recovery Timeline">{gantt_html}</section>
</div>"""
