#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 5.4 — World 06 (Smart Home & Energy) Builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from world_common import (
        assemble_world_bundle,
        cm_val,
        embed_compile,
        esc,
        load_world_inputs,
        render_params_aside,
    )
except ImportError:
    from src.v9.views.world_common import (
        assemble_world_bundle,
        cm_val,
        embed_compile,
        esc,
        load_world_inputs,
        render_params_aside,
    )


def _build_v17_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    pv_kw = float(cm_val(cm, "solar_pv_kw"))
    load_kw = float(cm_val(cm, "home_load_kw"))
    net_kw = float(cm_val(cm, "net_grid_export_kw"))
    soc = float(cm_val(cm, "battery_soc_pct"))
    temp_c = float(cm_val(cm, "living_temp_c"))
    rh_pct = float(cm_val(cm, "living_rh_pct"))
    dry_cnt = int(cm_val(cm, "leak_sensors_clear"))

    return f"""<div class="v9-stage-inner v9-view-v17">
  <section id="v17-kiosk" class="v17-frame-viewport" data-v17-scene="evening-warm" data-v17-backdrop="art" aria-label="Ambient Picture-Frame Smart Home Kiosk">
    <img id="v17-photo-art" class="v17-art-photo is-active" data-backdrop="art" data-asset="assets/opt_frame_art.jpg" fetchpriority="high" alt="Albert Bierstadt Mount Corcoran fine art mountain landscape painting" />
    <img id="v17-photo-landscape" class="v17-art-photo" data-backdrop="landscape" data-asset="assets/opt_frame_landscape.jpg" fetchpriority="low" alt="Calm mountain lake twilight reflection photograph" />
    <div class="v17-ambient-scrim" aria-hidden="true"></div>

    <div class="v17-visor-bar">
      <div class="v17-glass-pod v17-clock-pod" aria-label="Time and Living Zone Comfort">
        <div class="v17-clock-row">
          <span class="v17-clock-time va-nums">14:00</span>
          <span class="v17-clock-meta">Nov 18 · Clear 14 °C</span>
        </div>
        <div class="v17-comfort-row va-nums">
          <span>ZONE-LIVING {temp_c:.1f} °C</span>
          <span>·</span>
          <span>{rh_pct:.0f}% RH</span>
        </div>
      </div>

      <div class="v17-glass-pod v17-energy-pod" aria-label="Home Energy and Moisture Loop">
        <div class="v17-energy-line va-nums">
          <span>PV {pv_kw:.2f} kW</span>
          <span>·</span>
          <span>Load {load_kw:.2f} kW</span>
          <span>·</span>
          <span>Net {net_kw:+.2f} kW</span>
        </div>
        <div class="v17-energy-sub va-nums">
          <span>BATT {soc:.0f}%</span>
          <span class="va-pill" data-variant="status" data-state="nominal">LEAK {dry_cnt}/{dry_cnt} DRY</span>
        </div>
      </div>
    </div>

    <div class="v17-scene-bar" role="toolbar" aria-label="Gallery Backdrop and Lighting Scene Controls">
      <div class="v17-btn-group" role="group" aria-label="Canvas Backdrop">
        <button type="button" class="v17-scene-btn is-active" data-v17-backdrop="art" aria-pressed="true">Fine Art</button>
        <button type="button" class="v17-scene-btn" data-v17-backdrop="landscape" aria-pressed="false">Landscape</button>
      </div>
      <div class="v17-btn-group" role="group" aria-label="Lighting Scene">
        <button type="button" class="v17-scene-btn is-active" data-v17-scene="evening-warm" aria-pressed="true">Evening Warm</button>
        <button type="button" class="v17-scene-btn" data-v17-scene="cinema-dim" aria-pressed="false">Cinema Dim</button>
        <button type="button" class="v17-scene-btn" data-v17-scene="night-quiet" aria-pressed="false">Night Quiet</button>
      </div>
      <span id="v17-scene-readout" class="v17-readout" aria-live="polite">Fine Art · Evening Warm</span>
    </div>
  </section>
</div>"""


def _build_v18_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    cm = corpus["canonical_metrics"]
    pv_kw = float(cm_val(cm, "solar_pv_kw"))
    load_kw = float(cm_val(cm, "home_load_kw"))
    net_kw = float(cm_val(cm, "net_grid_export_kw"))
    soc = float(cm_val(cm, "battery_soc_pct"))
    temp_c = float(cm_val(cm, "living_temp_c"))
    rh_pct = float(cm_val(cm, "living_rh_pct"))
    dry_cnt = int(cm_val(cm, "leak_sensors_clear"))
    tariff = float(cm_val(cm, "peak_evening_tariff_usd_kwh"))

    energy_plot_html = embed_compile(specs["energy_plot"], "L2", "m3")
    device_table_html = embed_compile(specs["device_table"], "L2", "m3")
    params_aside = render_params_aside(
        "Panel & Tariff Bounds",
        [
            ("Main Service", "PANEL-MAIN-200A (240 V)"),
            ("Peak Solar PV", f"{pv_kw:.2f} kW (PV-STRING-SOUTH)"),
            ("Simultaneous Load", f"{load_kw:.2f} kW"),
            ("Net Grid Exchange", f"{net_kw:+.2f} kW (exporting)"),
            ("Battery Reserve", f"{soc:.0f} % (BATT-WALL-13KWH)"),
            ("Peak TOU Window", f"16:00-21:00 (${tariff:.2f}/kWh)"),
        ],
    )

    return f"""<div class="v9-stage-inner v9-view-v18">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">PANEL-MAIN-200A · PV-STRING-SOUTH · BATT-WALL-13KWH</span>
      <div class="v9-masthead-tags">
        <span class="va-pill" data-variant="tag">MATTER-1.4</span>
        <span class="va-pill" data-variant="status" data-state="nominal">ALL ZONES NOMINAL</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Home Assistant Companion &amp; Whole-Home Energy Console</h1>
    <p class="v9-masthead-sub">Net {net_kw:+.2f} kW grid export at {pv_kw:.2f} kW solar output ahead of the ${tariff:.2f}/kWh evening peak window.</p>
  </header>

  <section id="v18-kpis" class="v9-gate-band" data-state="nominal" aria-label="Whole-Home Energy KPIs">
    <div class="v9-kpi-strip">
      <div class="v9-kpi-tile">
        <span class="va-kicker">SOLAR PV OUTPUT</span>
        <span class="v9-kpi-val va-nums">{pv_kw:.2f} kW</span>
        <span class="v9-kpi-sub">PV-STRING-SOUTH · MPPT active</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">WHOLE-HOME LOAD</span>
        <span class="v9-kpi-val va-nums">{load_kw:.2f} kW</span>
        <span class="v9-kpi-sub">PANEL-MAIN-200A · 14.3 A eq.</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">NET GRID EXPORT</span>
        <span class="v9-kpi-val va-nums">{net_kw:+.2f} kW</span>
        <span class="v9-kpi-sub">EVSE-GARAGE-48A standby</span>
      </div>
      <div class="v9-kpi-tile">
        <span class="va-kicker">BATTERY &amp; LEAK LOOP</span>
        <span class="v9-kpi-val va-nums">{soc:.0f}% SOC</span>
        <span class="v9-kpi-sub">LEAK-LOOP-06: {dry_cnt} / {dry_cnt} clear</span>
      </div>
    </div>
  </section>

  <section id="v18-rooms" class="v18-section-card" aria-label="Quiet Nominal Rooms and Energy Scenes">
    <div class="v18-card-head">
      <h2 class="v18-card-title">Residential Zones &amp; Quiet-Nominal Status</h2>
      <div class="v18-filter-bar" role="group" aria-label="Filter home subsystems">
        <button type="button" class="v18-filter-btn is-active" data-v18-filter="all" aria-pressed="true">All</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="climate" aria-pressed="false">Climate</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="energy" aria-pressed="false">Energy</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="safety" aria-pressed="false">Safety</button>
      </div>
    </div>
    <div class="v18-room-grid">
      <article class="v18-zone-tile" data-v18-cat="climate">
        <div class="v18-zone-top"><span class="v18-zone-id">ZONE-LIVING</span><span class="va-pill" data-variant="status" data-state="nominal">NOMINAL</span></div>
        <div class="v18-zone-val va-nums">{temp_c:.1f} °C · {rh_pct:.0f}% RH</div>
        <div class="v18-zone-meta">Heat pump idle · target 21.5 °C</div>
      </article>
      <article class="v18-zone-tile" data-v18-cat="climate">
        <div class="v18-zone-top"><span class="v18-zone-id">ZONE-STUDY</span><span class="va-pill" data-variant="status" data-state="nominal">NOMINAL</span></div>
        <div class="v18-zone-val va-nums">20.8 °C · 42% RH</div>
        <div class="v18-zone-meta">Balanced air · damper open 35%</div>
      </article>
      <article class="v18-zone-tile" data-v18-cat="energy">
        <div class="v18-zone-top"><span class="v18-zone-id">BATT-WALL-13KWH</span><span class="va-pill" data-variant="status" data-state="nominal">RESERVE</span></div>
        <div class="v18-zone-val va-nums">{soc:.0f}% Charged</div>
        <div class="v18-zone-meta">Dispatch armed for 16:00 TOU (${tariff:.2f}/kWh)</div>
      </article>
      <article class="v18-zone-tile" data-v18-cat="safety">
        <div class="v18-zone-top"><span class="v18-zone-id">LEAK-LOOP-06</span><span class="va-pill" data-variant="status" data-state="nominal">DRY</span></div>
        <div class="v18-zone-val va-nums">{dry_cnt} / {dry_cnt} Clear</div>
        <div class="v18-zone-meta">Main shutoff valve in standby ready</div>
      </article>
    </div>
  </section>

  <section id="v18-security" class="v18-section-card" aria-label="Guarded Entry and Garage Actuators">
    <div class="v18-card-head">
      <h2 class="v18-card-title">Guarded Access Interlocks (Two-Step Activation)</h2>
      <span id="v18-sec-log" class="v18-sec-log" aria-live="polite">Deadbolt locked · Garage bay closed</span>
    </div>
    <div class="v18-security-grid">
      <div class="v9-interlock-card" id="v18-lock-card">
        <div class="v9-interlock-head">
          <h3 class="v9-interlock-title">LOCK-FRONT-01 · Front Entry Deadbolt</h3>
          <span id="v18-lock-pill" class="va-pill" data-variant="status" data-state="nominal">LOCKED</span>
        </div>
        <p class="v9-interlock-note">Requires explicit Arm authorization before actuating cylinder bolt.</p>
        <div class="v9-interlock-pad">
          <button type="button" id="v18-lock-arm" class="v9-tactile-btn" aria-pressed="false">1. Arm LOCK-FRONT-01</button>
          <button type="button" id="v18-lock-exec" class="v9-tactile-btn v9-tactile-exec" disabled>2. Unlock Entry</button>
        </div>
      </div>

      <div class="v9-interlock-card" id="v18-garage-card">
        <div class="v9-interlock-head">
          <h3 class="v9-interlock-title">GARAGE-BAY-01 · Overhead Door</h3>
          <span id="v18-garage-pill" class="va-pill" data-variant="status" data-state="nominal">CLOSED</span>
        </div>
        <p class="v9-interlock-note">Photo-eye clear · EVSE-GARAGE-48A cable stowed.</p>
        <div class="v9-interlock-pad">
          <button type="button" id="v18-garage-arm" class="v9-tactile-btn" aria-pressed="false">1. Verify Clear &amp; Arm</button>
          <button type="button" id="v18-garage-exec" class="v9-tactile-btn v9-tactile-exec" disabled>2. Open Bay Door</button>
        </div>
      </div>
    </div>
  </section>

  <section id="v18-energy" aria-label="24-Hour Whole-Home Solar and Load Plot">
    {energy_plot_html}
  </section>

  <section id="v18-ledger" class="v18-ledger-grid" aria-label="Device Ledger and Tariff Bounds">
    <div>{device_table_html}</div>
    {params_aside}
  </section>
</div>"""


def build_world_06(corpora_dir: Path) -> dict[str, Any]:
    """Compile World 06 (06-smart-home-and-energy) HTML views and manifest."""
    spec_files = {
        "scalars": "v17_home_comfort_and_safety_scalars.json",
        "energy_plot": "v18_whole_home_energy_plot.json",
        "device_table": "v18_zone_device_and_sensor_table.json",
    }
    corpus, bp, specs = load_world_inputs(corpora_dir, "06-smart-home-and-energy", spec_files)
    cm = corpus["canonical_metrics"]
    pv_kw = float(cm_val(cm, "solar_pv_kw"))
    net_kw = float(cm_val(cm, "net_grid_export_kw"))
    soc = float(cm_val(cm, "battery_soc_pct"))

    html_map = {
        "v17-picture-frame-home-kiosk": _build_v17_html(corpus, specs),
        "v18-home-assistant-companion-console": _build_v18_html(corpus, specs),
    }
    v18_status = [
        {"text": f"PV {pv_kw:.2f} kW", "variant": "plain", "state": "nominal"},
        {"text": f"Net {net_kw:+.2f} kW", "variant": "plain", "state": "nominal"},
        {"text": f"Batt {soc:.0f}%", "variant": "status", "state": "nominal"},
    ]
    view_cfg = {
        "v17-picture-frame-home-kiosk": {
            "option_label": "v17 · Picture-Frame Home Kiosk",
            "default_medium": "m7",
            "chromatic_code": "c4",
            "default_nav": "n0",
            "allowed_navs": ["n0"],
            "nav_icon": "frame",
            "nav_brand": "Ambient Frame",
            "topbar_brand": "Picture-Frame Kiosk · Living Wall",
            "rail_brand": "Frame Controls",
            "topbar_status": [],
            "nav_items": ["Frame"],
            "nav_anchors": ["v17-kiosk"],
            "inv_col": "v17-picture-frame-home-kiosk",
            "short_tag": "v17",
            "bias_risk": "Smart-home wall displays obscure artwork behind dense switches and intrusive HUD reticles.",
        },
        "v18-home-assistant-companion-console": {
            "option_label": "v18 · Home Assistant Companion Console",
            "default_medium": "m3",
            "chromatic_code": "c4",
            "default_nav": "n2",
            "allowed_navs": ["n2", "n4", "n1", "n0"],
            "nav_icon": "home",
            "nav_brand": "Home Console",
            "topbar_brand": "HOME-DER-PANEL · Solar & Climate",
            "rail_brand": "Smart Home",
            "topbar_status": v18_status,
            "nav_items": ["Overview", "Rooms", "Security", "24h Energy", "Devices"],
            "nav_anchors": ["v18-kpis", "v18-rooms", "v18-security", "v18-energy", "v18-ledger"],
            "inv_col": "v18-home-assistant-companion-console",
            "short_tag": "v18",
            "bias_risk": "Unguarded one-tap door toggles and smooth area charts obscure 16:00 TOU tariff margins and grid exports.",
        },
    }
    return assemble_world_bundle(corpus, bp, "06 · Smart Home & Energy", view_cfg, html_map)
