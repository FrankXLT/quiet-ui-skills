#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.5 — World 06 (Smart Home & Energy) Authentic HA Builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from world_common import assemble_world_bundle, cm_val, embed_compile, load_world_inputs, render_params_aside
except ImportError:
    from src.views.world_common import assemble_world_bundle, cm_val, embed_compile, load_world_inputs, render_params_aside

_ICONS = {
    "solar": '<circle cx="12" cy="12" r="4" fill="none"/><path fill="none" d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/>',
    "home": '<path fill="none" d="M3 10.5 12 3l9 7.5V21h-6v-6h-6v6H3Z"/>',
    "grid": '<path fill="none" d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>',
    "battery": '<rect x="3" y="7" width="16" height="10" rx="2" fill="none"/><path fill="none" d="M21 10v4M7 10v4m4-4v4"/>',
    "thermo": '<path fill="none" d="M14 14.76V5a2 2 0 1 0-4 0v9.76a4 4 0 1 0 4 0Z"/>',
    "fan": '<path fill="none" d="M12 12c-2-2.67-2-5.33 0-8 2 0 3.5 1.5 3.5 3.5 0 2-1.5 3.5-3.5 4.5Zm0 0c2.67-2 5.33-2 8 0 0 2-1.5 3.5-3.5 3.5-2 0-3.5-1.5-4.5-3.5Zm0 0c2 2.67 2 5.33 0 8-2 0-3.5-1.5-3.5-3.5 0-2 1.5-3.5 3.5-4.5Zm0 0c-2.67 2-5.33 2-8 0 0-2 1.5-3.5 3.5-3.5 2 0 3.5 1.5 4.5 3.5Z"/>',
    "bulb": '<path fill="none" d="M9 18h6m-5 3h4M12 2a7 7 0 0 0-4 12.7c.7.5 1 1.3 1 2.3h6c0-1 .3-1.8 1-2.3A7 7 0 0 0 12 2Z"/>',
    "speaker": '<rect x="5" y="2" width="14" height="20" rx="2" fill="none"/><circle cx="12" cy="14" r="4" fill="none"/><circle cx="12" cy="6.5" r="1" fill="none"/>',
    "droplet": '<path fill="none" d="M12 2.7 6.3 10a7 7 0 1 0 11.4 0L12 2.7Z"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2" fill="none"/><path fill="none" d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "garage": '<path fill="none" d="M3 21V9l9-6 9 6v12"/><path fill="none" d="M7 21v-8h10v8M7 16h10"/>',
}


def _icon(name: str) -> str:
    body = _ICONS.get(name, _ICONS["home"])
    return f'<svg class="v18-svg-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'


def _build_v17_html(corpus: dict[str, Any]) -> str:
    cm = corpus["canonical_metrics"]
    pv_kw = float(cm_val(cm, "solar_pv_kw"))
    soc = float(cm_val(cm, "battery_soc_pct"))
    temp_c = float(cm_val(cm, "living_temp_c"))
    rh_pct = float(cm_val(cm, "living_rh_pct"))
    dry_cnt = int(cm_val(cm, "leak_sensors_clear"))
    temp_f = round(temp_c * 9.0 / 5.0 + 32.0)

    return f"""<div class="v9-stage-inner v9-view-v17">
  <section id="v17-kiosk" class="v17-frame-viewport" data-v17-scene="evening" data-v17-backdrop="art" data-temp-unit="c" aria-label="Framed Smart Home Wall Kiosk">
    <div class="v17-mat-window">
      <img id="v17-photo-art" class="v17-art-photo is-active" data-backdrop="art" data-asset="assets/opt_frame_art.jpg" fetchpriority="high" alt="Albert Bierstadt Mount Corcoran fine art mountain landscape painting" />
      <img id="v17-photo-landscape" class="v17-art-photo" data-backdrop="landscape" data-asset="assets/opt_frame_landscape.jpg" fetchpriority="low" alt="Calm mountain lake twilight reflection photograph" />
      <div class="v17-ambient-scrim" aria-hidden="true"></div>

      <div class="v17-visor-bar">
        <div class="v17-glass-pod v17-clock-pod" aria-label="Time, Weather and Living Room Comfort">
          <div class="v17-clock-row">
            <span class="v17-clock-time va-nums">7:42 PM</span>
            <span class="v17-clock-meta">Wed, Nov 18 · Clear <span class="v17-temp-num" data-temp-c="14 °C" data-temp-f="57 °F">14 °C</span></span>
          </div>
          <div class="v17-comfort-row va-nums">
            <span>Living Room <span class="v17-temp-num" data-temp-c="{temp_c:.1f} °C" data-temp-f="{temp_f:.0f} °F">{temp_c:.1f} °C</span></span>
            <span>·</span>
            <span>{rh_pct:.0f}%</span>
          </div>
        </div>

        <div class="v17-glass-pod v17-energy-pod" aria-label="Home Solar, Battery and Leak Status">
          <div class="v17-energy-line va-nums">
            <span>Solar {pv_kw:.1f} kW</span>
            <span>·</span>
            <span>Battery {soc:.0f}%</span>
          </div>
          <div class="v17-energy-sub va-nums">
            <span>All {dry_cnt} Leak Sensors Dry</span>
          </div>
        </div>
      </div>

      <div class="v17-scene-bar" role="toolbar" aria-label="Lighting Scene, Artwork and Units">
        <div class="v17-btn-group" role="group" aria-label="Lighting Scene">
          <button type="button" class="v17-scene-btn" data-v17-scene="morning" aria-pressed="false">Morning</button>
          <button type="button" class="v17-scene-btn is-active" data-v17-scene="evening" aria-pressed="true">Evening</button>
          <button type="button" class="v17-scene-btn" data-v17-scene="movie" aria-pressed="false">Movie</button>
          <button type="button" class="v17-scene-btn" data-v17-scene="goodnight" aria-pressed="false">Goodnight</button>
        </div>
        <span class="v17-dock-sep" aria-hidden="true"></span>
        <div class="v17-btn-group" role="group" aria-label="Artwork Style">
          <button type="button" class="v17-scene-btn is-active" data-v17-backdrop="art" aria-pressed="true">Fine Art</button>
          <button type="button" class="v17-scene-btn" data-v17-backdrop="landscape" aria-pressed="false">Photo</button>
        </div>
        <span class="v17-dock-sep" aria-hidden="true"></span>
        <button type="button" id="v17-unit-btn" class="v17-scene-btn v17-unit-toggle" data-v17-unit="c" aria-pressed="false" aria-label="Toggle Fahrenheit or Celsius">°F | °C</button>
      </div>
    </div>
  </section>
</div>"""


def _v18_energy_kpis(pv_kw: float, load_kw: float, net_kw: float, soc: float) -> str:
    cards = [
        ("solar", "amber", "Solar Production", f"{pv_kw:.2f} kW", "South roof array"),
        ("home", "teal", "Home Usage", f"{load_kw:.2f} kW", "Afternoon steady baseline"),
        ("grid", "indigo", "Grid Export", f"{net_kw:+.2f} kW", "Sending surplus to utility"),
        ("battery", "emerald", "Home Battery", f"{soc:.0f}%", "Reserved for 16:00–21:00 peak"),
    ]
    tiles = "\n".join(
        f"""      <div class="v18-kpi-card">
        <span class="v18-mush-icon v18-tone-{tone}">{_icon(ico)}</span>
        <div class="v18-kpi-copy">
          <span class="va-kicker">{label}</span>
          <span class="v9-kpi-val va-nums">{val}</span>
          <span class="v9-kpi-sub">{sub}</span>
        </div>
      </div>"""
        for ico, tone, label, val, sub in cards
    )
    return f"""  <section id="v18-kpis" class="v18-kpi-strip" aria-label="Home Energy Summary">
{tiles}
  </section>"""


def _v18_mushroom_cards(temp_c: float, rh_pct: float, soc: float, dry_cnt: int, tariff: float) -> str:
    temp_f = round(temp_c * 9.0 / 5.0 + 32.0)
    items = [
        ("climate", "thermo", "amber", "Living Room",
         f'<span class="v18-temp-num" data-temp-c="{temp_c:.1f} °C" data-temp-f="{temp_f:.0f} °F">{temp_c:.1f} °C</span> · {rh_pct:.0f}% Humidity',
         "Heat pump idling"),
        ("climate", "fan", "teal", "Home Office",
         '<span class="v18-temp-num" data-temp-c="20.8 °C" data-temp-f="69 °F">20.8 °C</span> · 42% Humidity',
         "Fresh air circulating"),
        ("media", "bulb", "gold", "Living Room Lights", "Evening Glow · 65%", "Warm white dimming active"),
        ("media", "speaker", "indigo", "Family Room Media", "Standby · Quiet", "Living speakers idle"),
        ("safety", "droplet", "emerald", "Water Leak Sensors", f"All {dry_cnt} Dry", "Kitchen, bath & basement clear"),
        ("energy", "battery", "sky", "Home Battery", f"{soc:.0f}% Charged", f"Ready for ${tariff:.2f}/kWh peak"),
    ]
    tiles = "\n".join(
        f"""      <article class="v18-zone-tile v18-mush-card" data-v18-cat="{cat}">
        <span class="v18-mush-icon v18-tone-{tone}">{_icon(ico)}</span>
        <div class="v18-mush-body">
          <div class="v18-mush-name">{title}</div>
          <div class="v18-mush-primary va-nums">{primary}</div>
          <div class="v18-mush-sub">{sub}</div>
        </div>
      </article>"""
        for cat, ico, tone, title, primary, sub in items
    )
    return f"""  <section id="v18-rooms" class="v18-section-card" aria-label="Home Rooms and Devices">
    <div class="v18-card-head">
      <h2 class="v18-card-title">Home Rooms &amp; Devices</h2>
      <div class="v18-filter-bar" role="group" aria-label="Filter home rooms and devices">
        <button type="button" class="v18-filter-btn is-active" data-v18-filter="all" aria-pressed="true">All</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="climate" aria-pressed="false">Climate</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="media" aria-pressed="false">Lights &amp; Media</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="safety" aria-pressed="false">Safety</button>
        <button type="button" class="v18-filter-btn" data-v18-filter="energy" aria-pressed="false">Energy</button>
      </div>
    </div>
    <div class="v18-room-grid">
{tiles}
    </div>
  </section>"""


def _v18_access_cards() -> str:
    return f"""  <section id="v18-security" class="v18-section-card" aria-label="Home Access Controls">
    <div class="v18-card-head">
      <h2 class="v18-card-title">Doors &amp; Entry Access</h2>
      <span id="v18-sec-log" class="v18-sec-log" aria-live="polite">Front door locked · Garage door closed</span>
    </div>
    <div class="v18-security-grid">
      <div class="v9-interlock-card v18-access-card" id="v18-lock-card">
        <div class="v9-interlock-head">
          <div class="v18-access-label"><span class="v18-mush-icon v18-tone-emerald">{_icon("lock")}</span><h3 class="v9-interlock-title">Front Door</h3></div>
          <span id="v18-lock-pill" class="va-pill" data-variant="status" data-state="nominal">LOCKED</span>
        </div>
        <p class="v9-interlock-note">Deadbolt engaged. Two-step check prevents accidental taps.</p>
        <div class="v9-interlock-pad">
          <button type="button" id="v18-lock-arm" class="v9-tactile-btn" aria-pressed="false">1. Tap to Unlock</button>
          <button type="button" id="v18-lock-exec" class="v9-tactile-btn v9-tactile-exec" disabled>2. Confirm Unlock</button>
        </div>
      </div>

      <div class="v9-interlock-card v18-access-card" id="v18-garage-card">
        <div class="v9-interlock-head">
          <div class="v18-access-label"><span class="v18-mush-icon v18-tone-sky">{_icon("garage")}</span><h3 class="v9-interlock-title">Garage Door</h3></div>
          <span id="v18-garage-pill" class="va-pill" data-variant="status" data-state="nominal">CLOSED</span>
        </div>
        <p class="v9-interlock-note">Optical beam clear. Two-step check prevents accidental taps.</p>
        <div class="v9-interlock-pad">
          <button type="button" id="v18-garage-arm" class="v9-tactile-btn" aria-pressed="false">1. Tap to Open</button>
          <button type="button" id="v18-garage-exec" class="v9-tactile-btn v9-tactile-exec" disabled>2. Confirm Open</button>
        </div>
      </div>
    </div>
  </section>"""


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
        "Time-of-Use Tariff & Automations",
        [
            ("Off-Peak Rate Window", "21:00–16:00 ($0.14/kWh)"),
            ("Peak Rate Window", f"16:00–21:00 (${tariff:.2f}/kWh)"),
            ("Solar Export Rule", f"Export surplus above {soc:.0f}% SoC"),
            ("Emergency Backup Floor", "Hold 20% minimum battery reserve"),
            ("Pre-Cool Schedule", "Shift HVAC cycle ahead of 16:00"),
            ("Leak Auto-Shutoff", f"Armed ({dry_cnt} sensors dry)"),
        ],
    )

    return f"""<div class="v9-stage-inner v9-view-v18" data-temp-unit="c">
  <header class="v9-masthead">
    <div class="v9-masthead-eyebrow">
      <span class="va-kicker">Home Assistant · Living Comfort &amp; Energy</span>
      <div class="v9-masthead-tags">
        <div class="v18-unit-group" role="group" aria-label="Temperature Unit">
          <button type="button" class="v18-unit-btn is-active" data-v18-unit="c" aria-pressed="true">°C</button>
          <button type="button" class="v18-unit-btn" data-v18-unit="f" aria-pressed="false">°F</button>
        </div>
        <span class="va-pill" data-variant="status" data-state="nominal">All Systems Normal</span>
      </div>
    </div>
    <h1 class="v9-masthead-title">Home Assistant &amp; Daily Energy</h1>
    <p class="v9-masthead-sub">Producing {pv_kw:.2f} kW from solar and exporting {abs(net_kw):.2f} kW ({net_kw:+.2f} kW) before the ${tariff:.2f}/kWh evening peak window.</p>
  </header>

{_v18_energy_kpis(pv_kw, load_kw, net_kw, soc)}
{_v18_mushroom_cards(temp_c, rh_pct, soc, dry_cnt, tariff)}
{_v18_access_cards()}

  <section id="v18-energy" aria-label="24-Hour Home Energy Usage Bar Chart">
    {energy_plot_html}
  </section>

  <section id="v18-ledger" class="v18-ledger-grid" aria-label="Connected Devices and Electricity Plan">
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
        "v17-picture-frame-home-kiosk": _build_v17_html(corpus),
        "v18-home-assistant-companion-console": _build_v18_html(corpus, specs),
    }
    v18_status = [
        {"text": f"Solar {pv_kw:.2f} kW", "variant": "plain", "state": "nominal"},
        {"text": f"Grid {net_kw:+.2f} kW", "variant": "plain", "state": "nominal"},
        {"text": f"Battery {soc:.0f}%", "variant": "status", "state": "nominal"},
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
            "topbar_brand": "Framed Wall Kiosk · Living Room",
            "rail_brand": "Gallery Controls",
            "topbar_status": [],
            "nav_items": ["Frame"],
            "nav_anchors": ["v17-kiosk"],
            "inv_col": "v17-picture-frame-home-kiosk",
            "short_tag": "v17",
            "bias_risk": "Smart-home wall displays plaster switches and industrial device IDs over artwork.",
        },
        "v18-home-assistant-companion-console": {
            "option_label": "v18 · Home Assistant Companion Console",
            "default_medium": "m3",
            "chromatic_code": "c4",
            "default_nav": "n2",
            "allowed_navs": ["n2", "n4", "n1", "n0"],
            "nav_icon": "home",
            "nav_brand": "Home Assistant",
            "topbar_brand": "Home Assistant · Solar & Climate",
            "rail_brand": "Smart Home",
            "topbar_status": v18_status,
            "nav_items": ["Overview", "Rooms", "Doors", "Energy", "Devices"],
            "nav_anchors": ["v18-kpis", "v18-rooms", "v18-security", "v18-energy", "v18-ledger"],
            "inv_col": "v18-home-assistant-companion-console",
            "short_tag": "v18",
            "bias_risk": "Single-tap door toggles and SCADA line charts hide 24-hour energy flow and evening peak margins.",
        },
    }
    return assemble_world_bundle(corpus, bp, "06 · Smart Home & Energy", view_cfg, html_map)
