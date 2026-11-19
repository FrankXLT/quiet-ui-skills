#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.3 — M6 MIL-STD-1787B Flight HUD & M7 Photographic Smart-Glass Optics."""

from __future__ import annotations

from typing import Any

try:
    from world_common import cm_val
except ImportError:
    from src.v9.views.world_common import cm_val


def _v15_reticle_svg(bte: float) -> str:
    """Build stroke-only MIL-STD-1787B P43 phosphor combiner symbology (1200x720)."""
    hdg_ticks = "".join(
        f'<line x1="{600 + (d2 - 168) * 6}" y1="48" x2="{600 + (d2 - 168) * 6}" y2="{39 if d2 % 10 == 0 else 43}" stroke-width="1.6"/>'
        + (f'<text x="{600 + (d2 - 168) * 6}" y="65" text-anchor="middle" font-size="13">{d2 // 2:03d}</text>' if d2 in (140, 150, 160, 180, 190, 200) else "")
        for d2 in range(140, 205, 5)
    )
    spd_ticks = "".join(
        f'<line x1="{122 if spd % 10 == 0 else 128}" y1="{345 - (spd - 142) * 6}" x2="136" y2="{345 - (spd - 142) * 6}" stroke-width="1.6"/>'
        + (f'<text x="115" y="{350 - (spd - 142) * 6}" text-anchor="end" font-size="13">{spd}</text>' if spd % 10 == 0 and spd != 140 else "")
        for spd in range(110, 175, 5)
    )
    alt_ticks = "".join(
        f'<line x1="1064" y1="{345 - round((alt - 8520) * 0.85)}" x2="{1078 if alt % 100 == 0 else 1072}" y2="{345 - round((alt - 8520) * 0.85)}" stroke-width="1.6"/>'
        + (f'<text x="1084" y="{350 - round((alt - 8520) * 0.85)}" text-anchor="start" font-size="13">{alt:,}</text>' if alt % 100 == 0 and alt != 8500 else "")
        for alt in range(8300, 8750, 50)
    )
    return f"""<svg class="v15-reticle-layer" viewBox="0 0 1200 720" preserveAspectRatio="xMidYMid meet" role="img" aria-label="MIL-STD-1787B Collimated Optical Flight Symbology">
      <g stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <line x1="384" y1="48" x2="816" y2="48" stroke-width="1.8"/>
        {hdg_ticks}
        <path d="M594 48 L600 40 L606 48 Z" fill="none" stroke-width="1.8"/>
        <rect x="564" y="12" width="72" height="24" rx="2" fill="none" stroke-width="2"/>
        <text x="600" y="30" text-anchor="middle" font-size="17">084°</text>
        <path d="M462 122 A275 275 0 0 1 738 122" fill="none" stroke-width="1.2" opacity="0.72"/>
        <path d="M600 92 L594 102 L606 102 Z" fill="none" stroke-width="1.8"/>
        <line x1="552" y1="96" x2="550" y2="86" stroke-width="1.5"/>
        <line x1="648" y1="96" x2="650" y2="86" stroke-width="1.5"/>
        <line x1="505" y1="106" x2="500" y2="96" stroke-width="1.5"/>
        <line x1="695" y1="106" x2="700" y2="96" stroke-width="1.5"/>
        <line x1="464" y1="121" x2="457" y2="111" stroke-width="1.6"/>
        <line x1="736" y1="121" x2="743" y2="111" stroke-width="1.6"/>

        <text x="136" y="136" text-anchor="end" font-size="12">KT IAS</text>
        <line x1="136" y1="150" x2="136" y2="540" stroke-width="2"/>
        {spd_ticks}
        <path d="M136 297 L146 291 L146 303 Z" fill="none" stroke-width="1.8"/>
        <path d="M42 325 L126 325 L140 345 L126 365 L42 365 Z" fill="none" stroke-width="2.2"/>
        <text x="90" y="352" text-anchor="middle" font-size="19">142</text>
        <text x="44" y="576" text-anchor="start" font-size="13">GS 148 KT</text>
        <text x="44" y="616" text-anchor="start" font-size="14">PROP BTE {bte:.1f}% · IMEP 14.0 BAR</text>

        <text x="1064" y="136" text-anchor="start" font-size="12">FT MSL</text>
        <line x1="1064" y1="150" x2="1064" y2="540" stroke-width="2"/>
        {alt_ticks}
        <path d="M1060 345 L1074 325 L1162 325 L1162 365 L1074 365 Z" fill="none" stroke-width="2.2"/>
        <text x="1116" y="352" text-anchor="middle" font-size="18">8,520</text>
        <text x="1158" y="576" text-anchor="end" font-size="13">VS -650 FPM</text>
        <text x="1158" y="598" text-anchor="end" font-size="13">29.92 IN</text>

        <line x1="395" y1="350" x2="532" y2="350" stroke-width="1.8" opacity="0.86"/>
        <line x1="668" y1="350" x2="805" y2="350" stroke-width="1.8" opacity="0.86"/>
        <path d="M572 314 L586 314 L593 323 L600 314 L607 323 L614 314 L628 314" fill="none" stroke-width="2.2"/>

        <path d="M484 180 v-12 h64 M652 168 h64 v12" fill="none" stroke-width="2"/>
        <text x="476" y="173" text-anchor="end" font-size="13">+10</text>
        <text x="724" y="173" text-anchor="start" font-size="13">+10</text>
        <path d="M484 271 v-12 h64 M652 259 h64 v12" fill="none" stroke-width="2"/>
        <text x="476" y="264" text-anchor="end" font-size="13">+5</text>
        <text x="724" y="264" text-anchor="start" font-size="13">+5</text>

        <path d="M484 429 v12 h64 M652 441 h64 v-12" fill="none" stroke-width="2" stroke-dasharray="10 7"/>
        <text x="476" y="446" text-anchor="end" font-size="13">-5</text>
        <text x="724" y="446" text-anchor="start" font-size="13">-5</text>
        <path d="M484 520 v12 h64 M652 532 h64 v-12" fill="none" stroke-width="2" stroke-dasharray="10 7"/>
        <text x="476" y="537" text-anchor="end" font-size="13">-10</text>
        <text x="724" y="537" text-anchor="start" font-size="13">-10</text>

        <circle cx="600" cy="395" r="11" fill="none" stroke-width="2.2"/>
        <path d="M568 395 H589 M611 395 H632 M600 384 V371" fill="none" stroke-width="2.2"/>
      </g>
    </svg>"""


def build_v15_hud_html(corpus: dict[str, Any]) -> str:
    """Build v15 M6 Collimated Optical Flight HUD over 3 public-domain aerospace photographs."""
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    return f"""<div class="v9-stage-inner v9-view-v15">
  <div id="v15-hud-stage" class="v15-hud-stage" data-backplate="earthrise">
    <img class="v9-opt-photo v15-photo" data-photo-mode="earthrise" data-asset="assets/as08-14-2383.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="high" decoding="async"/>
    <img class="v9-opt-photo v15-photo" data-photo-mode="daylight" data-asset="assets/opt_hud_daylight_rwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    <img class="v9-opt-photo v15-photo" data-photo-mode="lowlight" data-asset="assets/opt_hud_night_rwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    {_v15_reticle_svg(bte)}
    <div id="v15-backplate-chips" class="v15-hud-mode-strip" role="group" aria-label="Optical Backplate Scene">
      <button type="button" class="va-pill v15-hud-chip is-active" data-variant="chip" data-backplate="earthrise" aria-pressed="true">Orbital</button>
      <button type="button" class="va-pill v15-hud-chip" data-variant="chip" data-backplate="daylight" aria-pressed="false">Daylight RWY</button>
      <button type="button" class="va-pill v15-hud-chip" data-variant="chip" data-backplate="lowlight" aria-pressed="false">Night NVG</button>
    </div>
  </div>
</div>"""


def build_v16_glass_html(corpus: dict[str, Any]) -> str:
    """Build v16 M7 Conformal See-Through Windshield Smart-Glass Overlay over real highway photos."""
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    return f"""<div class="v9-stage-inner v9-view-v16">
  <div id="v16-glass-viewport" class="v16-glass-viewport" data-luminance="daylight" data-contrast="10.8:1">
    <img class="v9-opt-photo v16-photo" data-photo-mode="daylight" data-asset="assets/opt_glass_day_hwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="high" decoding="async"/>
    <img class="v9-opt-photo v16-photo" data-photo-mode="dusk" data-asset="assets/opt_glass_dusk_hwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    <img class="v9-opt-photo v16-photo" data-photo-mode="night" data-asset="assets/opt_glass_night_hwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    <div class="v16-visor-bar">
      <section class="v16-glass-pod v16-pod-left" aria-label="Speed, Route and Efficiency">
        <div class="v16-speed-row">
          <span class="v16-speed-val va-nums">42</span>
          <span class="v16-speed-unit">mph</span>
          <span class="v16-speed-cap va-nums">45 mph DERATE LIMIT</span>
        </div>
        <div class="v16-route-line">E-Bound Highway · 2.4 mi to Maint Turnout</div>
        <div class="v16-eff-line va-nums">Cruise: <strong>{bte:.1f}% BTE</strong> · Following Gap: 2.8 s</div>
      </section>
      <section class="v16-glass-pod v16-pod-right v16-pod-warn" aria-label="Drivetrain Advisory">
        <span class="va-pill" data-variant="status" data-state="warn">DRIVETRAIN DERATE</span>
        <div class="v16-warn-title">MCU Thermal Limit (85 °C)</div>
        <div class="v16-warn-action">Hold &lt;= 45 mph · Inspect Rear Harness Stub at Stop</div>
      </section>
    </div>
    <div id="v16-luminance-chips" class="v16-ctrl-chips" role="group" aria-label="Ambient Glare Mode">
      <button type="button" class="va-pill v16-lum-chip is-active" data-variant="chip" data-luminance="daylight" data-contrast="10.8:1" aria-pressed="true">Daylight Glare</button>
      <button type="button" class="va-pill v16-lum-chip" data-variant="chip" data-luminance="dusk" data-contrast="11.9:1" aria-pressed="false">Horizon Dusk</button>
      <button type="button" class="va-pill v16-lum-chip" data-variant="chip" data-luminance="night" data-contrast="13.4:1" aria-pressed="false">Night Cabin</button>
    </div>
  </div>
</div>"""
