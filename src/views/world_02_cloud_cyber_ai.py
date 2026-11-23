#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 5 — World 02 (Cloud SRE, Zero-Trust ATO & AI Drift) Builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from world_directional_views import build_v19_html
except ImportError:
    from src.views.world_directional_views import build_v19_html

try:
    from world_common import (
        assemble_world_bundle,
        cm_val,
        embed_compile,
        esc,
        format_math_html,
        load_world_inputs,
        render_params_aside,
        slice_schematic_panel,
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
        slice_schematic_panel,
    )


def _build_v04_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    p99_peak = float(cm_val(cm, "p99_peak_ms"))
    p99_lim = float(cm_val(cm, "p99_threshold_ms"))
    burn = float(cm_val(cm, "error_budget_burn_pct_hr"))
    burn_lim = float(cm_val(cm, "error_budget_burn_limit_pct_hr"))
    drop_s = float(cm_val(cm, "scrape_dropout_s"))
    ca_s = float(cm_val(cm, "cursor_a_s"))
    cb_s = float(cm_val(cm, "cursor_b_s"))
    scope_html = embed_compile(specs["scope"], "L3", "m3")

    return f"""<div class="v9-stage-inner v9-view-v04">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">API-EDGE-CLUSTER-W2 · SRE-SLO-250MS · OTEL-COL-V0.114.0</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">PROM-SCRAPE-4S</span>
        <span id="v04-gate-pill" class="va-pill" data-variant="status" data-state="danger">CANARY TRIPPED</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">SRE Incident Command &amp; Tail-Latency Workbench</h1>
    <p class="v9-masthead-sub">p99 tail-latency breach ({p99_peak:.1f} ms &gt; {p99_lim:.1f} ms), error-budget burn ({burn:.1f} %/h), and uninterpolated {drop_s:.1f} s scrape dropout.</p>
  </header>

  <section id="v04-incident" class="v9-gate-band" data-state="warn" aria-label="SLO Incident Summary">
    <div class="v9-kpi-strip">
      <div class="v9-kpi-tile">
        <span class="va-kicker">API p99 LATENCY PEAK</span>
        <span class="v9-kpi-val va-nums" data-tone="danger">{p99_peak:.1f} ms</span>
        <span class="v9-kpi-sub">SLO Ceiling: {p99_lim:.1f} ms (+{p99_peak - p99_lim:.1f} ms)</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">ERROR-BUDGET BURN</span>
        <span class="v9-kpi-val va-nums" data-tone="warn">{burn:.1f} %/h</span>
        <span class="v9-kpi-sub">Abort Ceiling: {burn_lim:.1f} %/h</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">OTEL SCRAPE DROPOUT</span>
        <span class="v9-kpi-val va-nums">{drop_s:.1f} s</span>
        <span class="v9-kpi-sub">Window 44.0 s–56.0 s (uninterpolated)</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">CANARY TRAFFIC GATE</span>
        <span class="v9-kpi-val va-nums" data-tone="danger">0 (TRIPPED)</span>
        <span class="v9-kpi-sub">Cursors {format_math_html("T_A")}={ca_s:.1f} s .. {format_math_html("T_B")}={cb_s:.1f} s</span>
      </div>
    </div>
  </section>

  <section id="v04-scope" aria-label="Synchronized SRE Tail-Latency Scope">
    {scope_html}
  </section>

  <section id="v04-interlock" aria-label="Canary Traffic Isolation Interlock">
    <div id="v04-interlock-card" class="v9-interlock-card">
      <div class="v9-interlock-ctrl">
        <div class="v9-interlock-head">
          <h2 class="v9-interlock-title">Two-Step Canary Traffic Drain Interlock</h2>
          <span class="va-pill" data-variant="tag">ZERO-HOLD GATE</span>
        </div>
        <p class="v9-interlock-note">
          Confirm OTel Collector scrape resume after the {drop_s:.1f} s gap and arm drain before locking canary weight at 0%.
        </p>
        <div class="v9-interlock-pad">
          <button type="button" id="v04-otel-btn" class="v9-tactile-btn" aria-pressed="false">1. Verify OTel Resume</button>
          <button type="button" id="v04-arm-btn" class="v9-tactile-btn" aria-pressed="false">2. ARM Canary Drain</button>
          <button type="button" id="v04-exec-btn" class="v9-tactile-btn v9-tactile-exec" disabled>ISOLATE CANARY</button>
        </div>
      </div>
      <div id="v04-log" class="v9-audit-box" role="log" aria-live="polite" aria-label="Incident Audit Log">
        <span class="va-kicker">SRE INTERLOCK EVENT LOG</span>
        <div id="v04-audit-list" class="v9-audit-list">
          <div class="v9-audit-item">[04:15:00Z] Canary gate tripped to 0 at t = 36.0 s after {p99_peak:.1f} ms p99 breach.</div>
          <div class="v9-audit-item">[04:14:48Z] Uninterpolated OTel scrape null gap ({drop_s:.1f} s) bracketed within {format_math_html("T_A")}..{format_math_html("T_B")} ({cb_s - ca_s:.1f} s).</div>
        </div>
      </div>
    </div>
  </section>
</div>"""


def _build_v05_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    enclaves = int(cm_val(cm, "enclave_count"))
    edges = int(cm_val(cm, "ppsm_cross_enclave_edges"))
    reg_hex = esc(cm_val(cm, "fips_policy_hex"))
    reg_off = esc(cm_val(cm, "fips_policy_offset_hex"))
    topo_spec = slice_schematic_panel(
        specs["schematics"], 0, "v05-zero-trust-topology",
        title="NIST SP 800-207 Zero-Trust Enclave & PPSM Boundary Topology",
        description="Segmented 3-enclave trust topology enforcing orthogonal cross-boundary PPSM ports (443, 8443, 9443, 4317) and zero implicit subnet trust.",
    )
    topo_html = embed_compile(topo_spec, "L2", "m2")
    bit_html = embed_compile(specs["bitfield"], "L2", "m2")

    return f"""<div class="v9-stage-inner v9-view-v05">
  <div class="va-m1-block-only v9-m1-folio">
    <span>ZERO-TRUST ATO BOUNDARY SPEC · {reg_hex} · {reg_off}</span>
    <span>FIPS 140-3 LEVEL 3 · LETTER 8.5×11 IN</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">ATO-ZTA-2026-R3 · NIST SP 800-52 REV 2 · FIPS 140-3</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">{reg_hex}</span>
        <span class="va-pill" data-variant="status" data-state="nominal">ATO READY</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Zero-Trust Enclave ATO Boundary &amp; mTLS Policy Spec</h1>
    <p class="v9-masthead-sub">Authorizing Official proof binding {enclaves} isolated enclaves and {edges} cross-enclave PPSM edges to register CSR_MTLS_POLICY.</p>
  </header>

  <section id="v05-disposition" class="v9-gate-band" aria-label="ATO Boundary Disposition">
    <div class="v9-gate-top">
      <h2 class="v9-gate-rec">APPROVE ATO BOUNDARY: FIPS_STRICT [31] = 1 · LEGACY_TLS_ALLOW [30] = 0</h2>
      <span class="va-pill" data-variant="status" data-state="nominal">APPROVED</span>
    </div>
    <div id="v05-enclave-chips" class="v9-filter-bar va-sheet-hide" role="group" aria-label="Inspect Trust Enclave">
      <button type="button" class="va-pill v9-chip is-active" data-variant="chip" data-enclave="all" aria-pressed="true" data-summary="All 3 trust enclaves and 4 cross-boundary PPSM ports verified active.">All Enclaves ({enclaves})</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-enclave="ingress" aria-pressed="false" data-summary="ENCLAVE-INGRESS: Edge API PEP & Policy Engine PDP enforcing PPSM-443-mTLS fail-closed rejection.">Ingress PEP/PDP</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-enclave="compute" aria-pressed="false" data-summary="ENCLAVE-COMPUTE: Inference Mesh & OTel Collector pinned to SPIFFE trust domain 0x1.">Compute Mesh</button>
      <button type="button" class="va-pill v9-chip" data-variant="chip" data-enclave="hsm" aria-pressed="false" data-summary="ENCLAVE-HSM-AUDIT: Cloud HSM KMS & WORM Vault bound via PKCS#11 (9443) and WORM OTLP (4317).">HSM &amp; Audit</button>
    </div>
    <div id="v05-enclave-readout" class="v9-filter-readout va-sheet-hide" aria-live="polite">All 3 trust enclaves and 4 cross-boundary PPSM ports verified active.</div>
    <div id="v05-enclave-cards" class="v9-kpi-strip">
      <div class="v9-kpi-tile qe-bit-card" data-enclave="ingress">
        <span class="va-kicker">ENCLAVE-INGRESS</span>
        <span class="v9-kpi-val va-nums">443 / 8443</span>
        <span class="v9-kpi-sub">mTLS + SPIFFE SVID Edge PEP</span>
      </div>
      <div class="v9-kpi-tile qe-bit-card" data-enclave="compute">
        <span class="va-kicker">ENCLAVE-COMPUTE</span>
        <span class="v9-kpi-val va-nums">CLS-ROUTER-V4</span>
        <span class="v9-kpi-sub">Zero implicit subnet trust</span>
      </div>
      <div class="v9-kpi-tile qe-bit-card" data-enclave="hsm">
        <span class="va-kicker">ENCLAVE-HSM-AUDIT</span>
        <span class="v9-kpi-val va-nums">9443 / 4317</span>
        <span class="v9-kpi-sub">FIPS 140-3 Level 3 HSM + WORM</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">CSR_MTLS_POLICY</span>
        <span class="v9-kpi-val va-nums">{reg_hex}</span>
        <span class="v9-kpi-sub">Offset {reg_off} · Reset 0x00000000</span>
      </div>
    </div>
  </section>

  <div class="v9-editorial-grid">
    <article id="v05-rationale" class="v9-prose-card">
      <h2>Enclave Perimeter Segregation &amp; Cryptographic Interlocks</h2>
      <p>Every cross-enclave link traverses an explicit Ports, Protocols, and Services Management (PPSM) boundary ({edges} cross-enclave edges across {enclaves} non-overlapping enclaves). Edge API PEP terminates client TLS 1.3 and queries PDP policy before issuing short-lived SPIFFE identities to the compute mesh.</p>
      <p>Cryptographic enforcement is hardware-latched in register CSR_MTLS_POLICY at offset {reg_off} (value {reg_hex}). Safety-critical bit [31] (FIPS_STRICT = 1) rejects non-FIPS ciphers at the policy enforcement point, while bit [30] (LEGACY_TLS_ALLOW = 0) and bit [14] (CRL_FAIL_OPEN = 0) prevent downgrade or fail-open bypass.</p>
    </article>
    {render_params_aside("ATO Enclave Control Plane", [
        ("Boundary Drawing", "ATO-ZTA-2026-R3"),
        ("Enclave Count", f"{enclaves} Segregated Zones"),
        ("Cross-Boundary Edges", f"{edges} Registered PPSM Links"),
        ("Policy Register", f"CSR_MTLS_POLICY ({reg_hex})"),
        ("Offset / Reset", f"{reg_off} / 0x00000000"),
    ])}
  </div>

  <section id="v05-topology" aria-label="Zero-Trust Topology Schematic">{topo_html}</section>
  <section id="v05-bitfield" aria-label="CSR_MTLS_POLICY 32-Bit Register Decode">{bit_html}</section>
</div>"""


def _build_v06_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    ece = float(cm_val(cm, "ece_drift_score"))
    ece_max = float(cm_val(cm, "ece_drift_threshold"))
    n_val = int(cm_val(cm, "sample_count"))
    er_cnt = int(cm_val(cm, "er_entity_count"))
    cal_html = embed_compile(specs["cal_plot"], "L3", "m3")
    er_spec = slice_schematic_panel(
        specs["schematics"], 1, "v06-telemetry-lineage",
        title="Crow's-Foot AI Telemetry & Drift Alert Lineage Schema",
        description="End-to-end immutable audit lineage from Raw Events through Feature Vectors and Model Snapshots to Drift Alerts.",
    )
    er_spec["metadata"] = {**er_spec.get("metadata", {}), "drawing_id": "AI-TELEMETRY-ER-06"}
    er_html = embed_compile(er_spec, "L3", "m3")

    return f"""<div class="v9-stage-inner v9-view-v06">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">CLS-ROUTER-V4 · CAL-ECE-2026-1104 · N={n_val}</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">ECE {ece:.3f} vs {ece_max:.3f}</span>
        <span class="va-pill" data-variant="status" data-state="warn">FALLBACK ROUTED</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">AI Calibration Drift &amp; Telemetry Lineage Workbench</h1>
    <p class="v9-masthead-sub">Expected Calibration Error (ECE = {ece:.3f} &gt; {ece_max:.3f}) across {n_val} validation samples with {er_cnt}-entity Crow's-Foot audit lineage.</p>
  </header>

  <section id="v06-drift" class="v9-gate-band" data-state="warn" aria-label="Calibration Fallback Gate">
    <div class="v9-kpi-strip">
      <div class="v9-kpi-tile">
        <span class="va-kicker">EXPECTED CAL ERROR</span>
        <span class="v9-kpi-val va-nums" data-tone="warn">{ece:.3f}</span>
        <span class="v9-kpi-sub">Ceiling: {ece_max:.3f} (+{ece - ece_max:.3f} Drift)</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">OVERCONFIDENCE @ p=0.85</span>
        <span class="v9-kpi-val va-nums" data-tone="danger">-0.120</span>
        <span class="v9-kpi-sub">{format_math_html("f_obs")} = 0.73 vs 0.85 predicted</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">ROUTING RULE</span>
        <span class="v9-kpi-val va-nums">{format_math_html("p_hat")} ≥ 0.75</span>
        <span class="v9-kpi-sub">Escalate to deterministic policy</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">TELEMETRY LINEAGE</span>
        <span class="v9-kpi-val va-nums">{er_cnt} Entities</span>
        <span class="v9-kpi-sub">Raw Events → Drift Alerts</span>
      </div>
    </div>
  </section>

  <div class="v9-dual-grid">
    <section id="v06-cal" class="v9-dual-col" aria-label="Classifier Reliability Plot">{cal_html}</section>
    <section id="v06-lineage" class="v9-dual-col" aria-label="Telemetry ER Lineage Diagram">{er_html}</section>
  </div>
</div>"""


def build_world_02(corpora_dir: Path) -> dict[str, Any]:
    """Compile World 02 views, templates, and plain-English design rationale metadata."""
    spec_files = {
        "scope": "v04_sre_latency_scope.json",
        "bitfield": "v05_tls_policy_bitfield.json",
        "schematics": "v05_zero_trust_and_er_schematics.json",
        "cal_plot": "v06_ai_calibration_plot.json",
        "roadmap_gantt": "v19_release_roadmap_gantt.json",
    }
    corpus, bp, specs = load_world_inputs(corpora_dir, "02-cloud-cyber-and-ai-ops", spec_files)
    cm = corpus["canonical_metrics"]
    p99_peak = float(cm_val(cm, "p99_peak_ms"))
    burn = float(cm_val(cm, "error_budget_burn_pct_hr"))
    ece = float(cm_val(cm, "ece_drift_score"))

    html_map = {
        "v04-sre-incident-workbench": _build_v04_html(corpus, specs),
        "v05-zero-trust-ato-spec": _build_v05_html(corpus, specs),
        "v06-ai-drift-and-lineage-ide": _build_v06_html(corpus, specs),
        "v19-product-roadmap-and-triage": build_v19_html(corpus, specs),
    }
    v06_status = [
        {"text": "1 DRIFT ALERT", "variant": "status", "state": "warn"},
        {"text": f"ECE {ece:.3f} (>0.040)", "variant": "plain", "state": "warn"},
        {"text": f"p99 {p99_peak:.0f} ms / {burn:.1f}%", "variant": "plain", "state": "nominal"},
    ]
    view_cfg = {
        "v04-sre-incident-workbench": {
            "option_label": "v04 · Server Outage Console", "default_medium": "m3",
            "chromatic_code": "c4", "default_nav": "n2", "allowed_navs": ["n2", "n1", "n0"],
            "nav_icon": "alert-triangle", "nav_brand": "SRE Incident",
            "topbar_brand": "SRE Incident · API-EDGE-W2", "rail_brand": "SRE Console",
            "topbar_status": [], "nav_items": ["SLO Summary", "Latency Scope", "Canary Gate", "Event Log"],
            "nav_anchors": ["v04-incident", "v04-scope", "v04-interlock", "v04-log"],
            "inv_col": "v04-sre-incident-workbench", "short_tag": "v04",
            "bias_risk": "Mean latency and smoothed gaps mask 420.0 ms p99 tail breaches and the 12.0 s OTel blindspot.",
        },
        "v05-zero-trust-ato-spec": {
            "option_label": "v05 · Cloud Security Checklist", "default_medium": "m2",
            "chromatic_code": "c3", "default_nav": "n1", "allowed_navs": ["n1", "n2", "n0"],
            "nav_icon": "shield-halved", "nav_brand": "Zero-Trust Spec",
            "topbar_brand": "Zero-Trust Security Spec", "rail_brand": "Security Sections",
            "topbar_status": [], "nav_items": ["Disposition", "Rationale", "Enclave Map", "Policy Reg"],
            "nav_anchors": ["v05-disposition", "v05-rationale", "v05-topology", "v05-bitfield"],
            "inv_col": "v05-zero-trust-ato-spec", "short_tag": "v05",
            "bias_risk": "Topological marketing diagrams and latency telemetry obscure boundary accreditation and FIPS latches.",
        },
        "v06-ai-drift-and-lineage-ide": {
            "option_label": "v06 · AI Accuracy Tracker", "default_medium": "m3",
            "chromatic_code": "c3", "default_nav": "n3", "allowed_navs": ["n3", "n0", "n2"],
            "nav_icon": "code-branch", "nav_brand": "AI Drift IDE",
            "topbar_brand": "CLS-ROUTER-V4 · Calibration & Lineage", "rail_brand": "Model Telemetry",
            "topbar_status": v06_status, "nav_items": ["Fallback Gate", "Reliability", "ER Lineage"],
            "nav_anchors": ["v06-drift", "v06-cal", "v06-lineage"],
            "inv_col": "v06-ai-drift-and-lineage-ide", "short_tag": "v06",
            "bias_risk": "Aggregate accuracy scores mask severe high-confidence overconfidence (0.73 observed vs 0.85 predicted).",
        },
        "v19-product-roadmap-and-triage": {
            "option_label": "v19 · Product Release Roadmap", "default_medium": "m3",
            "chromatic_code": "c3", "default_nav": "n1", "allowed_navs": ["n1", "n2", "n0"],
            "nav_icon": "list-check", "nav_brand": "Release Roadmap",
            "topbar_brand": "Release Roadmap · 4 Launch Blockers", "rail_brand": "Roadmap Views",
            "topbar_status": [], "nav_items": ["Gate Summary", "Critical-Path Gantt", "Blocker Queue"],
            "nav_anchors": ["v19-disposition", "v19-gantt", "v19-triage"],
            "inv_col": "v19-product-roadmap-and-triage", "short_tag": "v19",
            "invariants_fallback": {
                "baseline": "GA cutover gated on <= 250.0 ms p99 latency, 12.0 s OTel gap fix, and 0x8003B104 FIPS check.",
                "provenance": "Schedule spans and float buffers trace directly to SRE, Security, and AI telemetry milestones.",
                "margin": "Parallel security track holds +3.0 d float while critical-path tasks carry zero schedule float.",
                "disposition": "Hold GA launch until all 4 tracked blockers clear and soak verification completes.",
            },
            "bias_removed": "Flat Unprioritized Ticket Cards & Hidden Critical Path",
            "bias_risk": "Flat Kanban cards hide critical-path dependencies and mask zero-float blockers behind parallel UI polish.",
            "bias_replacement": "Critical-path Gantt timelines coupled directly to 38px blocker triage rows and +3.0 d parallel float counters.",
        },
    }
    return assemble_world_bundle(corpus, bp, "02 · Cloud Software & AI", view_cfg, html_map)
