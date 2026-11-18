#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 5 — World 05 (Propulsion, CAN-FD, M6 HUD & M7 Glass) Builder."""

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
    from src.v9.views.world_common import (
        assemble_world_bundle,
        cm_val,
        embed_compile,
        load_world_inputs,
        render_params_aside,
    )


def _build_v13_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    eta_html = format_math_html("eta_bte")
    fs_html = format_math_html("f_s")
    uy_html = format_math_html("u_y")
    bte_html = embed_compile(specs["bte_plot"], "L3", "m2")

    return f"""<div class="v9-stage-inner v9-view-v13">
  <div class="va-m1-block-only v9-m1-folio">
    <span>ARGONNE D<sup>3</sup> PROPULSION MONOGRAPH · ANL-D3-2.0L-CRDI · NIST-TRQ-2026-05</span>
    <span>PEAK {eta_html} = {bte:.1f}% @ 14.0 bar IMEP · LETTER 8.5×11 IN</span>
  </div>
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">ANL-D3-2.0L-CRDI · ARGONNE D<sup>3</sup> DYN-CELL · {fs_html} = 100.0 Hz</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">NIST-TRQ-2026-05</span>
        <span class="va-pill" data-variant="status" data-state="nominal">PEAK {bte:.1f}% BTE</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Argonne D³ Propulsion Efficiency Archival Monograph</h1>
    <p class="v9-masthead-sub">Steady-state Brake Thermal Efficiency ({eta_html} peak {bte:.1f}% at 14.0 bar IMEP) with cubic analytical fit, ±{uy_html} bars, and residual audit.</p>
  </header>

  <div class="v9-editorial-grid">
    <article id="v13-prose" class="v9-prose-card">
      <h2>Torque-Cell Metrology, Polynomial Fit &amp; Operating Envelopes</h2>
      <p>Ten steady-state Argonne D³ dynamometer operating points spanning 2.0 to 20.0 bar Indicated Mean Effective Pressure (IMEP) establish peak Brake Thermal Efficiency {eta_html} = {bte:.1f} ± 0.4% at 14.0 bar. Uncorrelated discrete bench measurements preserve experimental variance separately from the cubic analytical curve and ±0.7% model envelope.</p>
      <p>Cruising below the 35.0% efficiency floor incurs severe part-load pumping losses below 6.8 bar IMEP, whereas extrapolating above the 46.0% thermal and knock derate ceiling violates turbine-inlet temperature margins. Bottom normalized residuals remain bounded within ±0.8 sigma.</p>
    </article>
    {render_params_aside("Dynamometer Test Cell", [
        ("Engine Unit", "ANL-D3-2.0L-CRDI"),
        ("Torque Standard", "NIST-TRQ-2026-05"),
        ("Ambient Cell Temp", "25.0 ± 0.5 °C"),
        ("Acquisition Rate", "100.0 Hz Steady-State"),
        ("Peak Efficiency", f"η_bte = {bte:.1f}% @ 14.0 bar"),
    ])}
  </div>

  <section id="v13-plot" aria-label="Brake Thermal Efficiency Curve">{bte_html}</section>
</div>"""


def _build_v14_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    ohm = int(cm_val(cm, "canfd_termination_ohm"))
    stub_m = float(cm_val(cm, "canfd_stub_max_m"))
    drop_us = float(cm_val(cm, "scope_dropout_us"))
    frame_hex = esc(cm_val(cm, "canfd_arb_frame_hex"))
    bus_html = embed_compile(specs["canfd_bus"], "L3", "m3")
    bit_html = embed_compile(specs["canfd_bit"], "L3", "m3")
    scope_html = embed_compile(specs["canfd_scope"], "L3", "m3")

    return f"""<div class="v9-stage-inner v9-view-v14">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">SAE J1939 CAN-FD · ISO 11898-2 · PGN 0xFEF1 ({frame_hex})</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">{ohm} Ω · Stub &lt;= {stub_m:.1f} m</span>
        <span id="v14-gate-pill" class="va-pill" data-variant="status" data-state="warn">MCU 0xEF WARN</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">CAN-FD Bus Topology, Arbitration Header &amp; Reflection Scope Debugger</h1>
    <p class="v9-masthead-sub">500 kbps arbitration / 2.0 Mbps data phase across {ohm} Ω EOL trunk with uninterpolated {drop_us:.2f} µs reflection dropout (0.90–1.25 µs).</p>
  </header>

  <div class="v9-dual-grid">
    <div class="v9-dual-col">
      <section id="v14-topology" aria-label="SAE J1939 Differential Bus Topology">{bus_html}</section>
      <section id="v14-header" aria-label="29-Bit Arbitration Header Bitfield">{bit_html}</section>
    </div>
    <div class="v9-dual-col">
      <section id="v14-scope" aria-label="CAN-FD Physical Reflection Scope">{scope_html}</section>
      <section id="v14-interlock" class="v9-interlock-card" aria-label="Bus W1C Arbitration Latch Clear">
        <div class="v9-interlock-ctrl">
          <div class="v9-interlock-head">
            <h2 class="v14-interlock-title v9-interlock-title">SOF_ARB_ERR [31] W1C Interlock Clear</h2>
            <span class="va-pill" data-variant="tag">FRAME {frame_hex}</span>
          </div>
          <p class="v9-interlock-note">Verify dual {ohm} Ω termination and Stub &lt;= {stub_m:.1f} m before clearing W1C bit [31].</p>
          <div class="v9-interlock-pad">
            <button type="button" id="v14-term-btn" class="v9-tactile-btn" aria-pressed="false">1. Verify {ohm} Ω / {stub_m:.1f} m</button>
            <button type="button" id="v14-arm-btn" class="v9-tactile-btn" aria-pressed="false">2. ARM W1C Reset</button>
            <button type="button" id="v14-exec-btn" class="v9-tactile-btn v9-tactile-exec" disabled>CLEAR LATCH</button>
          </div>
        </div>
        <div id="v14-log" class="v9-audit-box" role="log" aria-live="polite" aria-label="Fieldbus Audit Log">
          <span class="va-kicker">CAN-FD HARNESS AUDIT LOG</span>
          <div id="v14-audit-list" class="v9-audit-list">
            <div class="v9-audit-item">[05:30:00Z] Stub overshoot +2.68 V / +425 mV common-mode spike preceding {drop_us:.2f} µs dropout.</div>
            <div class="v9-audit-item">[05:29:55Z] MCU (0xEF) thermal warn 85 °C alongside ECM (0x00), BMS (0xF3).</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</div>"""


def _build_v15_html(corpus: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    keepout = float(cm_val(cm, "hud_sightline_keepout_pct"))

    return f"""<div class="v9-stage-inner v9-view-v15">
  <div id="v15-hud-stage" class="v15-hud-stage" data-backplate="earthrise">
    <svg class="v15-reticle-layer" viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid meet" aria-label="Collimated Optical Pitch Ladder">
      <line x1="420" y1="240" x2="465" y2="240" stroke="#22FF88" stroke-width="2" fill="none"/>
      <line x1="535" y1="240" x2="580" y2="240" stroke="#22FF88" stroke-width="2" fill="none"/>
      <line x1="420" y1="360" x2="465" y2="360" stroke="#22FF88" stroke-width="2" fill="none"/>
      <line x1="535" y1="360" x2="580" y2="360" stroke="#22FF88" stroke-width="2" fill="none"/>
      <polyline points="484,300 494,300 500,308 506,300 516,300" fill="none" stroke="#22FF88" stroke-width="2.5"/>
      <circle cx="500" cy="300" r="3" fill="none" stroke="#22FF88" stroke-width="2"/>
      <text x="412" y="244" text-anchor="end" font-size="13" fill="#22FF88">+5</text>
      <text x="588" y="244" text-anchor="start" font-size="13" fill="#22FF88">+5</text>
      <text x="412" y="364" text-anchor="end" font-size="13" fill="#22FF88">-5</text>
      <text x="588" y="364" text-anchor="start" font-size="13" fill="#22FF88">-5</text>
    </svg>

    <div class="v15-hud-top">
      <span class="v15-hud-lbl">HDG 084° MAG · WAYPOINT FL085</span>
      <span class="v15-hud-lbl">BORESIGHT {keepout:.0f}% CLEAR · NAV/PROPULSION HUD</span>
    </div>

    <div class="v15-hud-mids">
      <div class="v15-hud-rail">
        <div class="v15-hud-readout">
          <span class="v15-hud-lbl">AIRSPEED IAS</span>
          <span class="v15-hud-num">142 kt</span>
        </div>
        <div class="v15-hud-readout">
          <span class="v15-hud-lbl">PROPULSION BTE</span>
          <span class="v15-hud-num">{bte:.1f}%</span>
        </div>
      </div>

      <div class="v15-hud-rail v15-hud-rail-right">
        <div class="v15-hud-readout">
          <span class="v15-hud-lbl">ALTITUDE MSL</span>
          <span class="v15-hud-num">8,520 ft</span>
        </div>
        <div class="v15-hud-readout">
          <span class="v15-hud-lbl">IMEP OPTIMUM</span>
          <span class="v15-hud-num">14.0 bar</span>
        </div>
      </div>
    </div>

    <div class="v15-hud-bottom">
      <div id="v15-backplate-chips" class="v15-hud-mode-strip" role="group" aria-label="Optical Backplate Test">
        <button type="button" class="va-pill v9-chip v15-hud-chip is-active" data-variant="chip" data-backplate="earthrise" data-summary="Earthrise Limb Backplate: dual stroke halo against orbital horizon." aria-pressed="true">Earthrise</button>
        <button type="button" class="va-pill v9-chip v15-hud-chip" data-variant="chip" data-backplate="daylight" data-summary="High-Brightness Daylight Backplate: narrowband green phosphor holds stroke contrast." aria-pressed="false">Daylight</button>
        <button type="button" class="va-pill v9-chip v15-hud-chip" data-variant="chip" data-backplate="lowlight" data-summary="NVG Lowlight Backplate: calm monochrome zero-bloom horizon." aria-pressed="false">Lowlight</button>
      </div>
      <span id="v15-hud-readout" class="v15-hud-lbl" aria-live="polite">Earthrise Limb Backplate: dual stroke halo against orbital horizon.</span>
    </div>
  </div>
</div>"""


def _build_v16_html(corpus: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    ohm = int(cm_val(cm, "canfd_termination_ohm"))
    stub_m = float(cm_val(cm, "canfd_stub_max_m"))
    scrim_min = float(cm_val(cm, "window_scrim_min_contrast"))

    return f"""<div class="v9-stage-inner v9-view-v16">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">SPATIAL OPTICAL COMBINER · HIGH-CONTRAST GLASS OVERLAY</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">MIN SCRIM {scrim_min:.1f}:1</span>
        <span class="va-pill" data-variant="status" data-state="warn">MCU 0xEF WARN</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Bridge &amp; Vehicle Transparent Smart-Glass Bus Alert Pod</h1>
    <p class="v9-masthead-sub">Luminance-adaptive combiner overlay projecting CAN-FD MCU (0xEF) thermal warn and peak {bte:.1f}% propulsion efficiency without blocking forward sightline.</p>
  </header>

  <div id="v16-glass-viewport" class="v16-glass-viewport" data-luminance="daylight">
    <div id="v16-top-scrim" class="v16-scrim-band">
      <div class="v16-metric-strip">
        <div class="v16-metric">
          <span class="v16-metric-lbl">CAN-FD HARNESS</span>
          <span class="v16-metric-val">{ohm} Ω · Stub &lt;= {stub_m:.1f} m</span>
        </div>
        <div class="v16-metric">
          <span class="v16-metric-lbl">MCU NODE (0xEF)</span>
          <span class="v16-metric-val" data-tone="warn">85 °C DERATE WARN</span>
        </div>
        <div class="v16-metric">
          <span class="v16-metric-lbl">CRUISE EFFICIENCY</span>
          <span class="v16-metric-val" data-tone="accent">{bte:.1f}% BTE</span>
        </div>
      </div>
      <span class="v16-scrim-pill">1 BUS WARN · NO FLASH</span>
    </div>

    <div class="v16-corridor-spacer" aria-hidden="true">
      <div class="v16-lane-guide"></div>
    </div>

    <div id="v16-bottom-scrim" class="v16-scrim-band">
      <span class="v16-metric-lbl">PERIPHERAL SIGHTLINE CORRIDOR UNOBSTRUCTED</span>
      <span class="va-nums">EFFECTIVE SCRIM CONTRAST: <strong id="v16-contrast-val">10.6:1</strong> (Floor {scrim_min:.1f}:1)</span>
    </div>
  </div>

  <div class="v16-ctrl-bar va-sheet-hide">
    <div id="v16-luminance-chips" class="v16-ctrl-chips" role="group" aria-label="Ambient Luminance Test">
      <button type="button" class="va-pill v9-chip v16-lum-chip is-active" data-variant="chip" data-luminance="daylight" data-contrast="10.6:1" data-summary="Daylight Glare: darkened scrim preserves 10.6:1 minimum contrast against bright road and sky." aria-pressed="true">Daylight Glare</button>
      <button type="button" class="va-pill v9-chip v16-lum-chip" data-variant="chip" data-luminance="dusk" data-contrast="11.8:1" data-summary="Horizon Dusk: balanced scrim preserves 11.8:1 minimum contrast in twilight transitions." aria-pressed="false">Horizon Dusk</button>
      <button type="button" class="va-pill v9-chip v16-lum-chip" data-variant="chip" data-luminance="night" data-contrast="13.4:1" data-summary="Night Vision: low-bloom scrim preserves 13.4:1 contrast while protecting ambient dark adaptation." aria-pressed="false">Night Cabin</button>
    </div>
    <span id="v16-lum-readout" class="v9-filter-readout" aria-live="polite">Daylight Glare: darkened scrim preserves 10.6:1 minimum contrast against bright road and sky.</span>
  </div>
</div>"""


def build_world_05(corpora_dir: Path) -> dict[str, Any]:
    """Compile World 05 views, templates, and Quiet-Bridge provenance metadata."""
    spec_files = {
        "bte_plot": "v13_propulsion_bte_plot.json",
        "canfd_bus": "v14_canfd_bus_schematic.json",
        "canfd_bit": "v14_canfd_arb_bitfield.json",
        "canfd_scope": "v14_canfd_reflection_scope.json",
    }
    corpus, bp, specs = load_world_inputs(corpora_dir, "05-physical-systems-auto-and-aero", spec_files)
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    ohm = int(cm_val(cm, "canfd_termination_ohm"))
    frame_hex = esc(cm_val(cm, "canfd_arb_frame_hex"))

    html_map = {
        "v13-propulsion-archival-monograph": _build_v13_html(corpus, specs),
        "v14-fieldbus-and-scope-debugger": _build_v14_html(corpus, specs),
        "v15-collimated-flight-hud": _build_v15_html(corpus),
        "v16-transparent-window-overlay": _build_v16_html(corpus),
    }
    v14_status = [
        {"text": "1 BUS WARN", "variant": "status", "state": "warn"},
        {"text": f"{ohm} Ω · 2 Mbps", "variant": "plain", "state": "nominal"},
        {"text": str(cm_val(cm, "canfd_arb_frame_hex")), "variant": "plain", "state": "nominal"},
    ]
    view_cfg = {
        "v13-propulsion-archival-monograph": {
            "option_label": "v13 · Propulsion Monograph (M2↔M1 · L3)", "default_medium": "m2",
            "chromatic_code": "c3", "default_nav": "n1", "allowed_navs": ["n1", "n0"],
            "nav_icon": "fa-gauge-high", "nav_brand": "Argonne D³ Monograph",
            "topbar_brand": "Argonne D³ Propulsion Efficiency", "rail_brand": "Monograph",
            "topbar_status": [], "nav_items": ["Efficiency Prose", "D³ Curve & Residuals"],
            "nav_anchors": ["v13-prose", "v13-plot"],
            "inv_col": "v13-propulsion-archival-monograph", "short_tag": "v13",
            "mb_keywords": ("v13", "Physical Conservation"),
            "bias_risk": "Spline-smoothed torque curves without error bars obscure variance between measured operating points and knock ceilings.",
            "actionable_disposition": f"Peak BTE {bte:.1f}% at 14.0 bar IMEP; restrict continuous operation within [35.0%, 46.0%] envelope.",
        },
        "v14-fieldbus-and-scope-debugger": {
            "option_label": "v14 · CAN-FD Fieldbus Debugger (M3 · L3)", "default_medium": "m3",
            "chromatic_code": "c4", "default_nav": "n3", "allowed_navs": ["n3", "n0", "n2"],
            "nav_icon": "fa-microchip", "nav_brand": "CAN-FD Bench",
            "topbar_brand": f"SAE J1939 CAN-FD · {cm_val(cm, 'canfd_arb_frame_hex')}", "rail_brand": "Bench Tools",
            "topbar_status": v14_status, "nav_items": ["Bus Topology", "29-Bit Header", "Reflection Scope", "W1C Interlock"],
            "nav_anchors": ["v14-topology", "v14-header", "v14-scope", "v14-interlock"],
            "inv_col": "v14-fieldbus-and-scope-debugger", "short_tag": "v14",
            "mb_keywords": ("v14", "J1939", "SOF_ARB_ERR"),
            "bias_risk": "Unlinked hex dumps and bridged scope gaps hide termination reflection spikes before W1C latch clear.",
            "actionable_disposition": "Inspect 0.35 µs stub reflection gap (0.90–1.25 µs) and verify 120 Ω EOL before clearing SOF_ARB_ERR [31].",
        },
        "v15-collimated-flight-hud": {
            "option_label": "v15 · Collimated Flight HUD (M6 · L1)", "default_medium": "m6",
            "chromatic_code": "c4", "default_nav": "n0", "allowed_navs": ["n0"],
            "nav_icon": "fa-crosshairs", "nav_brand": "Flight Optical HUD",
            "topbar_brand": "Collimated Optical HUD", "rail_brand": "Flight HUD",
            "topbar_status": [], "nav_items": [], "nav_anchors": [],
            "inv_col": "v15-collimated-flight-hud", "short_tag": "v15",
            "mb_keywords": ("v15",),
            "bias_risk": "Centered opaque widgets and multi-series charts occlude runway/horizon sightlines on an infinity combiner.",
            "actionable_disposition": f"Hold >= 65% central boresight clear; display {bte:.1f}% BTE & 14.0 bar peripheral telemetry over stroke phosphor.",
        },
        "v16-transparent-window-overlay": {
            "option_label": "v16 · Smart-Glass Overlay Pod (M7 · L1)", "default_medium": "m7",
            "chromatic_code": "c4", "default_nav": "n0", "allowed_navs": ["n0"],
            "nav_icon": "fa-glasses", "nav_brand": "Smart Glass Pod",
            "topbar_brand": "Transparent Combiner Pod", "rail_brand": "Combiner Pod",
            "topbar_status": [], "nav_items": [], "nav_anchors": [],
            "inv_col": "v16-transparent-window-overlay", "short_tag": "v16",
            "mb_keywords": ("v16", "MCU"),
            "bias_risk": "Unbacked transparent overlays and dense wiring tables drop below legible contrast against 100,000 lux daylight glare.",
            "actionable_disposition": "Hold MCU (0xEF) 85 °C derate alert above >= 7.0:1 WCAG AAA smoked scrim across daylight glare.",
        },
    }
    return assemble_world_bundle(corpus, bp, "05 · Auto, CAN-FD & Aero HUD", view_cfg, html_map)
