#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 5 — World 03 (Grid SCADA, M5 Plant Wall Kiosk & SPC Audit) Builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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


def _build_v07_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    p_act = float(cm_val(cm, "bess_power_act_mw"))
    p_cmd = float(cm_val(cm, "bess_power_cmd_mw"))
    freq = float(cm_val(cm, "grid_freq_hz"))
    soc = float(cm_val(cm, "bess_soc_pct"))
    reg_val = esc(cm_val(cm, "modbus_reg_value"))
    scalars_html = embed_compile(specs["scalars"], "L3", "m4")
    pid_bus_html = embed_compile(specs["pid_bus"], "L3", "m4")

    return f"""<div class="v9-stage-inner v9-view-v07">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">POI-MGRID-03 · ISA-5.1 / ISA-101 · DWG-SCADA-POI-0307-R2</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">CAL-PMU-2026-031</span>
        <span id="v07-gate-pill" class="va-pill" data-variant="status" data-state="nominal">BREAKER 52-M CLOSED</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Microgrid POI Dispatch, ISA-5.1 P&amp;ID &amp; RS-485 Console</h1>
    <p class="v9-masthead-sub">Active dispatch {p_act:.1f} MW (CMD {p_cmd:.1f} MW), synchrophasor {freq:.3f} Hz, BESS SoC {soc:.1f}%, and 120 Ω RS-485 fieldbus telemetry.</p>
  </header>

  <section id="v07-scalars" aria-label="Synchrophasor and BESS Telemetry">{scalars_html}</section>
  <section id="v07-node-bar" class="v07-node-bar" aria-label="Microgrid Node Telemetry Selector">
    <div id="v07-node-chips" class="v07-node-chips" role="group" aria-label="Inspect Microgrid Node">
      <button type="button" class="v07-node-chip" data-v07-node="poi" aria-pressed="false" data-v07-diag="POI Breaker 52-M Closed · Active Dispatch {p_act:.1f} MW (CMD {p_cmd:.1f} MW) · Synchrophasor {freq:.3f} Hz (±0.005 Hz)">POI 52-M · {p_act:.1f} MW</button>
      <button type="button" class="v07-node-chip" data-v07-node="gt" aria-pressed="false" data-v07-diag="Gas Turbine Skid (FT-101 / FCV-101) · 14.2 MW Dispatch Share · 13.8 kV Bus Sync · OEE Yield 94.2%">Gas Turbine · 14.2 MW</button>
      <button type="button" class="v07-node-chip" data-v07-node="bess" aria-pressed="false" data-v07-diag="24.0 MW / DC 1500 V Grid-Forming BESS · State of Charge {soc:.1f}% (Target 80.0%) · 88% Corridor Margin">BESS · {soc:.1f}% SoC</button>
      <button type="button" class="v07-node-chip" data-v07-node="rs485" aria-pressed="false" data-v07-diag="120 Ω RS-485 / Modbus RTU Bus · PLC-01 Master -> RTU-02 GT / BMS-03 BESS / PMU-04 POI · Nominal Link">RS-485 Bus · 120 Ω</button>
    </div>
    <div id="v07-node-diag" class="v07-node-diag va-nums" role="status">Select a node above to spotlight its scalar telemetry and schematic panel.</div>
  </section>
  <section id="v07-topology" aria-label="ISA-5.1 P&amp;ID Loop and 120 Ohm Fieldbus">{pid_bus_html}</section>

  <section id="v07-interlock" aria-label="POI Breaker 52-M Islanding Interlock">
    <div id="v07-interlock-card" class="v9-interlock-card">
      <div class="v9-interlock-ctrl">
        <div class="v9-interlock-head">
          <h2 class="v9-interlock-title">Guarded POI Breaker 52-M Islanding Interlock ({reg_val})</h2>
          <span class="va-pill" data-variant="tag">REG 0x0104 · LOTO CLEAR</span>
        </div>
        <p class="v9-interlock-note">
          Verify LOTO bit [10] = 0 clear state and IEEE 1547 Synchrocheck 25 ({freq:.3f} Hz) before arming island transfer.
        </p>
        <div class="v9-interlock-pad">
          <button type="button" id="v07-loto-btn" class="v9-tactile-btn" aria-pressed="false">1. Verify LOTO [10] Clear</button>
          <button type="button" id="v07-arm-btn" class="v9-tactile-btn" aria-pressed="false">2. ARM Island Transfer</button>
          <button type="button" id="v07-exec-btn" class="v9-tactile-btn v9-tactile-exec" disabled>EXECUTE TRANSFER</button>
        </div>
      </div>
      <div id="v07-log" class="v9-audit-box" role="log" aria-live="polite" aria-label="SCADA Interlock Log">
        <span class="va-kicker">SCADA PROTECTION EVENT LOG</span>
        <div id="v07-audit-list" class="v9-audit-list">
          <div class="v9-audit-item">[21:30:00Z] Reg 0x0104={reg_val}: ISLAND_ARMED=1, LOTO=0, 52-M Closed ({p_act:.1f} MW POI).</div>
          <div class="v9-audit-item">[21:29:52Z] IEEE C37.118 PMU freq {freq:.3f} Hz within ±0.020 Hz nominal corridor.</div>
        </div>
      </div>
    </div>
  </section>
</div>"""


def _v08_tile_svg(pts: tuple[float, ...], pct: float, target_pct: float, accent: str) -> str:
    """Render compact M5 inline trend sparkline and target fill gauge."""
    xs = [round(8 + i * (464 / (len(pts) - 1)), 1) for i in range(len(pts))]
    poly = " ".join(f"{x},{round(31 - y * 23, 1)}" for x, y in zip(xs, pts))
    ty = round(31 - target_pct * 23, 1)
    ex, ey = xs[-1], round(31 - pts[-1] * 23, 1)
    fill_w = round(max(4.0, min(464.0, pct * 464.0)), 1)
    t_x = round(8 + target_pct * 464.0, 1)
    return (
        f'<div class="v08-kpi-visual" aria-hidden="true">'
        f'<svg class="v08-kpi-spark" viewBox="0 0 480 46" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
        f'<line x1="8" y1="{ty}" x2="472" y2="{ty}" stroke="var(--border-strong)" stroke-width="1" stroke-dasharray="4 3"/>'
        f'<polyline fill="none" stroke="{accent}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" points="{poly}"/>'
        f'<circle cx="{ex}" cy="{ey}" r="3.5" fill="{accent}"/>'
        f'<rect x="8" y="38" width="464" height="5" rx="2.5" fill="var(--bg-elevated)" stroke="var(--border-hairline)" stroke-width="0.6"/>'
        f'<rect x="8" y="38" width="{fill_w}" height="5" rx="2.5" fill="{accent}"/>'
        f'<line x1="{t_x}" y1="36" x2="{t_x}" y2="45" stroke="var(--text-primary)" stroke-width="1.5"/>'
        f'</svg></div>'
    )


def _build_v08_html(corpus: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    p_act = float(cm_val(cm, "bess_power_act_mw"))
    p_cmd = float(cm_val(cm, "bess_power_cmd_mw"))
    freq = float(cm_val(cm, "grid_freq_hz"))
    freq_cmd = float(cm_val(cm, "grid_freq_cmd_hz"))
    soc = float(cm_val(cm, "bess_soc_pct"))
    oee = float(cm_val(cm, "oee_yield_pct"))
    cpk = float(cm_val(cm, "spc_cpk"))
    sp1 = _v08_tile_svg((0.72, 0.78, 0.81, 0.76, 0.84, 0.88, 0.85, 0.90), p_act / 26.0, p_cmd / 26.0, "var(--accent-focal)")
    sp2 = _v08_tile_svg((0.52, 0.56, 0.50, 0.48, 0.54, 0.49, 0.51, 0.46), 0.72, 0.75, "var(--accent-primary)")
    sp3 = _v08_tile_svg((0.48, 0.54, 0.60, 0.65, 0.70, 0.74, 0.77, 0.784), soc / 100.0, 0.80, "var(--accent-focal)")
    sp4 = _v08_tile_svg((0.86, 0.88, 0.90, 0.91, 0.92, 0.93, 0.94, 0.942), oee / 100.0, 0.95, "var(--status-ok)")

    return f"""<div class="v9-stage-inner v9-view-v08">
  <header class="v08-wall-header">
    <div>
      <span class="v08-wall-kicker">PLANT FLOOR CELL-03 &amp; MICROGRID POI</span>
      <h1 class="v08-wall-title">Live Microgrid &amp; Production Yield Overview</h1>
    </div>
    <div class="v08-wall-status">
      <span class="va-pill" data-variant="status" data-state="nominal">ALL SYSTEMS NOMINAL</span>
      <span class="va-pill" data-variant="tag">52-M CLOSED · LOTO CLEAR</span>
    </div>
  </header>

  <div class="v08-kpi-grid" aria-label="Primary Plant Floor Telemetry">
    <article class="v08-kpi-card">
      <div class="v08-kpi-head"><span class="v08-kpi-label">Microgrid Active Dispatch</span><span class="va-pill" data-variant="status" data-state="nominal">POI SYNCED</span></div>
      {sp1}
      <div class="v08-kpi-hero">
        <span class="v08-kpi-val va-nums">{p_act:.1f} MW</span>
        <span class="v08-kpi-target va-nums">Target {p_cmd:.1f} MW · Nominal</span>
      </div>
    </article>
    <article class="v08-kpi-card">
      <div class="v08-kpi-head"><span class="v08-kpi-label">Grid Synchrophasor Frequency</span><span class="va-pill" data-variant="status" data-state="nominal">LOCK ±0.02 Hz</span></div>
      {sp2}
      <div class="v08-kpi-hero">
        <span class="v08-kpi-val va-nums">{freq:.3f} Hz</span>
        <span class="v08-kpi-target va-nums">Reference {freq_cmd:.3f} Hz</span>
      </div>
    </article>
    <article class="v08-kpi-card">
      <div class="v08-kpi-head"><span class="v08-kpi-label">Battery Storage Charge (BESS)</span><span class="va-pill" data-variant="status" data-state="nominal">DISCHARGE READY</span></div>
      {sp3}
      <div class="v08-kpi-hero">
        <span class="v08-kpi-val va-nums">{soc:.1f}%</span>
        <span class="v08-kpi-target va-nums">Target 80.0% · Ready</span>
      </div>
    </article>
    <article class="v08-kpi-card" data-accent="emerald">
      <div class="v08-kpi-head"><span class="v08-kpi-label">Cell-03 Plant OEE Yield</span><span class="va-pill" data-variant="status" data-state="nominal">SHIFT A</span></div>
      {sp4}
      <div class="v08-kpi-hero">
        <span class="v08-kpi-val va-nums">{oee:.1f}%</span>
        <span class="v08-kpi-target va-nums">Target 95.0% · Shift A On Track</span>
      </div>
    </article>
  </div>

  <footer class="v08-wall-footer">
    <span>CNC-CELL-03 Bearing Bore Process Capability: {format_math_html("C_pk")} = {cpk:.2f} (10.000 ± 0.042 mm Control Limits)</span>
    <span>POI Dispatch Synced · Zero Out-of-Control Lots</span>
  </footer>
</div>"""


def _build_v09_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    cl = float(cm_val(cm, "spc_cl_mm"))
    ucl = float(cm_val(cm, "spc_ucl_mm"))
    lcl = float(cm_val(cm, "spc_lcl_mm"))
    usl = float(cm_val(cm, "spc_usl_mm"))
    lsl = float(cm_val(cm, "spc_lsl_mm"))
    cpk = float(cm_val(cm, "spc_cpk"))
    n_sub = int(cm_val(cm, "spc_subgroup_size"))
    raw_reg = str(cm_val(cm, "modbus_reg_value"))
    reg_val = esc(raw_reg)
    cpk_html = format_math_html("C_pk")
    xbar_html = format_math_html("X_bar")
    uy_html = format_math_html("u_y")
    spc_html = embed_compile(specs["spc"], "L3", "m2")
    mod_html = embed_compile(specs["modbus"], "L3", "m2")

    return f"""<div class="v9-stage-inner v9-view-v09">
  <div class="va-m1-block-only v9-m1-folio">
    <span>MANUFACTURING QUALITY &amp; PLC INTERLOCK AUDIT · CAL-CMM-ISO10360-2026-07</span>
    <span>SUBGROUP n={n_sub} · {cpk_html}={cpk:.2f} · LETTER 8.5×11 IN</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">CNC-CELL-03-BORE · NIST/SEMATECH SPC · MODBUS REG 0x0104</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">{cpk_html} = {cpk:.2f}</span>
        <span class="va-pill" data-variant="status" data-state="nominal">IN CONTROL</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Bearing Bore Shewhart {xbar_html} SPC &amp; Modbus Interlock Report</h1>
    <p class="v9-masthead-sub">Metrological capability proof across 12 subgroups (n = {n_sub}, ±{uy_html} uncertainty whiskers) paired with 16-bit Modbus interlock decode {reg_val}.</p>
  </header>

  <section id="v09-capability" class="v9-gate-band" aria-label="Process Capability Gate">
    <div class="v9-kpi-strip">
      <div class="v9-kpi-tile">
        <span class="va-kicker">PROCESS CAPABILITY {cpk_html}</span>
        <span class="v9-kpi-val va-nums" data-tone="ok">{cpk:.2f}</span>
        <span class="v9-kpi-sub">Minimum Gate ≥ 1.33 (+0.31)</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">CONTROL BAND (±3σ)</span>
        <span class="v9-kpi-val va-nums">{cl:.3f} mm</span>
        <span class="v9-kpi-sub">LCL {lcl:.3f} .. UCL {ucl:.3f} mm</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">ENGINEERING TOLERANCE</span>
        <span class="v9-kpi-val va-nums">[{lsl:.3f}, {usl:.3f}]</span>
        <span class="v9-kpi-sub">mm Abort Envelope · 0 Breaches</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">PLC INTERLOCK WORD</span>
        <span class="v9-kpi-val va-nums">{reg_val}</span>
        <span class="v9-kpi-sub">Reg 0x0104 · LOTO [10]=0 · 52-M=1</span>
      </div>
    </div>
  </section>

  <div class="v9-editorial-grid">
    <article id="v09-methods" class="v9-prose-card">
      <h2>Subgroup Metrology, Control Boundaries &amp; Safety Interlock Proof</h2>
      <p>Twelve coordinate-measuring machine (CMM) subgroups of n = {n_sub} bearing bores remain squarely inside the ±3 sigma statistical control band (CL = {cl:.3f} mm, UCL = {ucl:.3f} mm, LCL = {lcl:.3f} mm) and wide of engineering tolerance limits (LSL {lsl:.3f} mm to USL {usl:.3f} mm), sustaining {cpk_html} = {cpk:.2f} without spline smoothing.</p>
      <p>Machine cell safety ties to Holding Register 0x0104 ({reg_val}). Safety-critical latch bits verify that LOTO Lockout bit [10] and E-Stop bit [8] are clear (0) while Synchrocheck bit [9] and Breaker 52-M Auxiliary bit [0] stay asserted (1).</p>
    </article>
    {render_params_aside("CMM & Modbus Audit Parameters", [
        ("Calibration Certificate", "CAL-CMM-ISO10360-2026-07"),
        ("Ambient Lab Temp", "20.0 ± 0.2 °C"),
        ("Subgroup Sample Size", f"n = {n_sub} parts/lot"),
        ("Process Capability", f"C_pk = {cpk:.2f} (Gate >= 1.33)"),
        ("Modbus Register", f"0x0104 = {raw_reg}"),
    ])}
  </div>

  <section id="v09-spc" aria-label="Shewhart X̄ SPC Plot">{spc_html}</section>
  <section id="v09-modbus" aria-label="16-Bit Modbus Holding Register">{mod_html}</section>
</div>"""


def build_world_03(corpora_dir: Path) -> dict[str, Any]:
    """Compile World 03 views, templates, and Quiet-Bridge provenance metadata."""
    spec_files = {
        "scalars": "v07_synchrophasor_scalars.json",
        "pid_bus": "v07_grid_scada_pid_and_bus.json",
        "spc": "v09_spc_control_plot.json",
        "modbus": "v09_modbus_plc_bitfield.json",
    }
    corpus, bp, specs = load_world_inputs(corpora_dir, "03-industrial-grid-and-manufacturing", spec_files)
    cm = corpus["canonical_metrics"]
    p_act = float(cm_val(cm, "bess_power_act_mw"))
    freq = float(cm_val(cm, "grid_freq_hz"))

    html_map = {
        "v07-grid-scada-poi-console": _build_v07_html(corpus, specs),
        "v08-plant-floor-wall-kiosk": _build_v08_html(corpus),
        "v09-spc-quality-and-modbus-report": _build_v09_html(corpus, specs),
    }
    v07_status = [
        {"text": f"POI {p_act:.1f} MW", "variant": "plain", "state": "nominal"},
        {"text": f"{freq:.3f} Hz", "variant": "plain", "state": "nominal"},
        {"text": "NOMINAL", "variant": "status", "state": "nominal"},
    ]
    view_cfg = {
        "v07-grid-scada-poi-console": {
            "option_label": "v07 · Grid SCADA POI Console", "default_medium": "m4",
            "chromatic_code": "c4", "default_nav": "n3", "allowed_navs": ["n3", "n0", "n2"],
            "nav_icon": "bolt", "nav_brand": "Microgrid POI-03",
            "topbar_brand": "Microgrid POI-03 · IEEE 1547 · TIA-485", "rail_brand": "SCADA Views",
            "topbar_status": v07_status, "nav_items": ["PMU Scalars", "P&ID & Fieldbus", "52-M Interlock", "Event Log"],
            "nav_anchors": ["v07-scalars", "v07-topology", "v07-interlock", "v07-log"],
            "inv_col": "v07-grid-scada-poi-console", "short_tag": "v07",
            "bias_risk": "Decorative animations, rainbow nominal badges, and single-click trip controls risk alarm fatigue and unsafe breaker switching.",
            "actionable_disposition": f"Hold POI Breaker 52-M closed at {p_act:.1f} MW / {freq:.3f} Hz; require LOTO bit [10]=0 before islanding transfer.",
        },
        "v08-plant-floor-wall-kiosk": {
            "option_label": "v08 · Plant-Floor Wall Display", "default_medium": "m5",
            "chromatic_code": "c3", "default_nav": "n0", "allowed_navs": ["n0"],
            "nav_icon": "tv", "nav_brand": "Plant Wall Display",
            "topbar_brand": "Plant Wall Display", "rail_brand": "Plant Wall Display",
            "topbar_status": [], "nav_items": [], "nav_anchors": [],
            "inv_col": "v08-plant-floor-wall-kiosk", "short_tag": "v08",
            "bias_risk": "Raw hexadecimal Modbus registers and capability ratios cannot be scanned across a 10-foot factory floor.",
            "actionable_disposition": "Ambient 10-ft display: confirm 94.2% OEE and 78.4% BESS SoC across shift change.",
        },
        "v09-spc-quality-and-modbus-report": {
            "option_label": "v09 · SPC Quality & Modbus Audit", "default_medium": "m2",
            "chromatic_code": "c3", "default_nav": "n1", "allowed_navs": ["n1", "n2", "n0"],
            "nav_icon": "chart-line", "nav_brand": "SPC & Modbus Audit",
            "topbar_brand": "SPC & Modbus Audit", "rail_brand": "Audit Sections",
            "topbar_status": [], "nav_items": ["Capability Gate", "Analysis", "Shewhart SPC", "Modbus Reg"],
            "nav_anchors": ["v09-capability", "v09-methods", "v09-spc", "v09-modbus"],
            "inv_col": "v09-spc-quality-and-modbus-report", "short_tag": "v09",
            "bias_risk": "Bare yield percentages and smoothed spline fits conceal centering drift and interlock status.",
            "actionable_disposition": "Authorize release of 12 bearing bore lots (C_pk = 1.64 >= 1.33, 0 USL/LSL breaches).",
        },
    }
    return assemble_world_bundle(corpus, bp, "03 · Grid & Manufacturing", view_cfg, html_map)
