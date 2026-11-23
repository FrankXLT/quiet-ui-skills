#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.3 — M6 MIL-STD-1787B Flight HUD & M7 Photographic Smart-Glass Optics."""

from __future__ import annotations

from typing import Any

try:
    from world_common import cm_val
except ImportError:
    from src.views.world_common import cm_val


def _v15_reticle_svg(bte: float) -> str:
    """Build stroke-only MIL-STD-1787B P43 phosphor combiner symbology (1200x720)."""
    hdg_ticks = "".join(
        f'<line x1="{600 + (d2 - 168) * 6}" y1="48" x2="{600 + (d2 - 168) * 6}" y2="{39 if d2 % 10 == 0 else 43}" stroke-width="1.6"/>'
        + (f'<text x="{600 + (d2 - 168) * 6}" y="65" text-anchor="middle" font-size="13">{d2 // 2:03d}</text>' if d2 in (140, 150, 160, 180, 190, 200) else "")
        for d2 in range(140, 205, 5)
    )
    spd_ticks = "".join(
        f'<line x1="{122 if spd % 10 == 0 else 128}" y1="{360 - (spd - 138) * 6}" x2="136" y2="{360 - (spd - 138) * 6}" stroke-width="1.6"/>'
        + (f'<text x="115" y="{365 - (spd - 138) * 6}" text-anchor="end" font-size="13">{spd}</text>' if spd % 10 == 0 and abs((spd - 138) * 6) >= 28 else "")
        for spd in range(110, 170, 5)
    )
    alt_ticks = "".join(
        f'<line x1="1064" y1="{360 - round((alt - 1180) * 0.85)}" x2="{1078 if alt % 100 == 0 else 1072}" y2="{360 - round((alt - 1180) * 0.85)}" stroke-width="1.6"/>'
        + (f'<text x="1084" y="{365 - round((alt - 1180) * 0.85)}" text-anchor="start" font-size="13">{alt:,}</text>' if alt % 100 == 0 and abs(round((alt - 1180) * 0.85)) >= 28 else "")
        for alt in range(1000, 1450, 50)
    )
    ils_loc_dots = "".join(
        f'<circle cx="{x}" cy="560" r="2.2" fill="none" stroke-width="1.5"/>'
        for x in (530, 565, 600, 635, 670)
    )
    ils_gs_dots = "".join(
        f'<circle cx="770" cy="{y}" r="2.2" fill="none" stroke-width="1.5"/>'
        for y in (290, 325, 360, 395, 430)
    )
    return f"""<svg class="v15-reticle-layer" viewBox="0 0 1200 720" preserveAspectRatio="xMidYMid meet" role="img" aria-label="MIL-STD-1787B Collimated Optical Flight Symbology">
      <g stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <line x1="384" y1="48" x2="816" y2="48" stroke-width="1.8"/>
        {hdg_ticks}
        <path d="M594 48 L600 40 L606 48 Z" fill="none" stroke-width="1.8"/>
        <rect x="564" y="12" width="72" height="24" rx="2" fill="none" stroke-width="2"/>
        <text x="600" y="30" text-anchor="middle" font-size="17">084°</text>
        <text id="v15-hud-hdg-ref" x="600" y="81" text-anchor="middle" font-size="11" opacity="0.88">TRUE HDG</text>
        <path d="M462 122 A275 275 0 0 1 738 122" fill="none" stroke-width="1.2" opacity="0.72"/>
        <path d="M600 92 L594 102 L606 102 Z" fill="none" stroke-width="1.8"/>
        <line x1="552" y1="96" x2="550" y2="86" stroke-width="1.5"/>
        <line x1="648" y1="96" x2="650" y2="86" stroke-width="1.5"/>
        <line x1="505" y1="106" x2="500" y2="96" stroke-width="1.5"/>
        <line x1="695" y1="106" x2="700" y2="96" stroke-width="1.5"/>
        <line x1="464" y1="121" x2="457" y2="111" stroke-width="1.6"/>
        <line x1="736" y1="121" x2="743" y2="111" stroke-width="1.6"/>

        <g id="v15-hud-spd-grp">
          <text id="v15-hud-spd-unit" x="136" y="146" text-anchor="end" font-size="12">KT IAS</text>
          <line x1="136" y1="160" x2="136" y2="560" stroke-width="2"/>
          <g id="v15-spd-ticks">{spd_ticks}</g>
          <path d="M136 312 L146 306 L146 318 Z" fill="none" stroke-width="1.8"/>
          <path d="M42 340 L126 340 L140 360 L126 380 L42 380 Z" fill="none" stroke-width="2.2"/>
          <text id="v15-hud-spd-val" x="90" y="367" text-anchor="middle" font-size="19">138</text>
          <text id="v15-hud-spd-sub" x="44" y="590" text-anchor="start" font-size="13">GS 144 KT</text>
          <text id="v15-hud-prop-line" x="44" y="624" text-anchor="start" font-size="14" data-bte="{bte:.1f}">PROP BTE {bte:.1f}% · IMEP 14.0 BAR</text>
        </g>

        <g id="v15-hud-alt-grp">
          <text id="v15-hud-alt-unit" x="1064" y="146" text-anchor="start" font-size="12">FT MSL</text>
          <line x1="1064" y1="160" x2="1064" y2="560" stroke-width="2"/>
          <g id="v15-alt-ticks">{alt_ticks}</g>
          <path d="M1060 360 L1074 340 L1162 340 L1162 380 L1074 380 Z" fill="none" stroke-width="2.2"/>
          <text id="v15-hud-alt-val" x="1116" y="367" text-anchor="middle" font-size="18">1,180</text>
          <text id="v15-hud-rad-line" x="1158" y="572" text-anchor="end" font-size="13">640 FT AGL · 3.0° GS</text>
          <text id="v15-hud-vs-line" x="1158" y="594" text-anchor="end" font-size="13">VS -650 FPM</text>
          <text id="v15-hud-baro-line" x="1158" y="616" text-anchor="end" font-size="13">29.92 IN</text>
        </g>

        <line x1="395" y1="360" x2="532" y2="360" stroke-width="1.8" opacity="0.86"/>
        <line x1="668" y1="360" x2="805" y2="360" stroke-width="1.8" opacity="0.86"/>
        <path d="M572 324 L586 324 L593 333 L600 324 L607 333 L614 324 L628 324" fill="none" stroke-width="2.2"/>

        <path d="M484 190 v-12 h64 M652 178 h64 v12" fill="none" stroke-width="2"/>
        <text x="476" y="183" text-anchor="end" font-size="13">+10</text>
        <text x="724" y="183" text-anchor="start" font-size="13">+10</text>
        <path d="M484 281 v-12 h64 M652 269 h64 v12" fill="none" stroke-width="2"/>
        <text x="476" y="274" text-anchor="end" font-size="13">+5</text>
        <text x="724" y="274" text-anchor="start" font-size="13">+5</text>

        <path d="M484 439 v12 h64 M652 451 h64 v-12" fill="none" stroke-width="2" stroke-dasharray="10 7"/>
        <text x="476" y="456" text-anchor="end" font-size="13">-5</text>
        <text x="724" y="456" text-anchor="start" font-size="13">-5</text>
        <path d="M484 530 v12 h64 M652 542 h64 v-12" fill="none" stroke-width="2" stroke-dasharray="10 7"/>
        <text x="476" y="547" text-anchor="end" font-size="13">-10</text>
        <text x="724" y="547" text-anchor="start" font-size="13">-10</text>

        <g id="v15-hud-fpm" transform="translate(0,0)">
          <circle cx="600" cy="410" r="11" fill="none" stroke-width="2.2"/>
          <path d="M568 410 H589 M611 410 H632 M600 399 V386" fill="none" stroke-width="2.2"/>
        </g>
        <g id="v15-hud-ils-scale" opacity="0">
          {ils_loc_dots}
          <polygon points="606,551 614,560 606,569 598,560" fill="none" stroke-width="1.8"/>
          {ils_gs_dots}
          <polygon points="770,357 779,365 770,373 761,365" fill="none" stroke-width="1.8"/>
          <text x="684" y="564" text-anchor="start" font-size="11">LOC</text>
          <text x="770" y="278" text-anchor="middle" font-size="11">GS</text>
        </g>
      </g>
    </svg>"""


def build_v15_hud_html(corpus: dict[str, Any]) -> str:
    """Build v15 M6 Collimated Optical Flight HUD over 3 public-domain aerospace photographs."""
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    return f"""<div class="v9-stage-inner v9-view-v15">
  <div id="v15-hud-stage" class="v15-hud-stage" data-backplate="daylight">
    <img class="v9-opt-photo v15-photo" data-photo-mode="daylight" data-asset="assets/opt_hud_daylight_rwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="high" decoding="async"/>
    <img class="v9-opt-photo v15-photo" data-photo-mode="lowlight" data-asset="assets/opt_hud_night_rwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    <img class="v9-opt-photo v15-photo" data-photo-mode="earthrise" data-asset="assets/as08-14-2383.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    {_v15_reticle_svg(bte)}
    <div id="v15-backplate-chips" class="v15-hud-mode-strip" role="group" aria-label="Optical Backplate Scene">
      <button type="button" class="va-pill v15-hud-chip is-active" data-variant="chip" data-backplate="daylight" aria-pressed="true">Daylight RWY</button>
      <button type="button" class="va-pill v15-hud-chip" data-variant="chip" data-backplate="lowlight" aria-pressed="false">Night ILS</button>
      <button type="button" class="va-pill v15-hud-chip" data-variant="chip" data-backplate="earthrise" aria-pressed="false">Orbital Limb</button>
    </div>
  </div>
</div>"""


def build_v16_glass_html(corpus: dict[str, Any]) -> str:
    """Build v16 M7 Maritime Wheelhouse Smart-Glass Bridge Window Overlay over channel photos."""
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    return f"""<div class="v9-stage-inner v9-view-v16">
  <div id="v16-glass-viewport" class="v16-glass-viewport" data-luminance="daylight" data-contrast="10.8:1" data-ais="true">
    <img class="v9-opt-photo v16-photo" data-photo-mode="daylight" data-asset="assets/opt_glass_day_hwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="high" decoding="async"/>
    <img class="v9-opt-photo v16-photo" data-photo-mode="dusk" data-asset="assets/opt_glass_dusk_hwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    <img class="v9-opt-photo v16-photo" data-photo-mode="night" data-asset="assets/opt_glass_night_hwy.jpg" alt="" aria-hidden="true" width="1600" height="1000" fetchpriority="low" decoding="async"/>
    <div class="v16-visor-bar">
      <section class="v16-glass-pod v16-pod-left" aria-label="Vessel Speed, Pier Range and Propulsion Efficiency">
        <div class="v16-speed-row">
          <span id="v16-speed-val" class="v16-speed-val va-nums">18.4</span>
          <span class="v16-speed-unit">kt SOG</span>
          <span id="v16-speed-cap" class="v16-speed-cap va-nums">HOLD &lt;= 18 kt</span>
        </div>
        <div class="v16-route-line va-nums"><strong>Pier 4</strong> · 1.20 nm · ETA <span id="v16-eta-val">03m 54s</span></div>
        <div class="v16-eff-line va-nums">Propulsion {bte:.1f}% BTE · UKC 8.4 m · Depth 14.2 m</div>
      </section>
      <div class="v16-glass-pod v16-compass-tape" aria-label="Heading and Cross-Track Tape">
        <span class="v16-compass-heading va-nums">075° &middot; [ 084°T BERTH APPROACH ] &middot; 095°</span>
        <span class="v16-compass-sub va-nums">XTE 0.02 nm STBD &middot; Wind 14 kt NE</span>
      </div>
      <section class="v16-glass-pod v16-pod-right v16-pod-warn" aria-label="Propulsion Advisory">
        <span id="v16-warn-pill" class="va-pill" data-variant="status" data-state="warn">STBD DRIVE DERATE</span>
        <div id="v16-warn-title" class="v16-warn-title">MCU Thermal Limit (85 °C)</div>
        <div id="v16-warn-action" class="v16-warn-action">Hold &lt;= 18 kt · Inspect Aft J1939 Drop at Berth</div>
      </section>
    </div>
    <div class="v16-ais-layer" aria-hidden="true">
      <svg class="v16-ais-svg" viewBox="0 0 1200 720" preserveAspectRatio="xMidYMid meet">
        <polygon points="96,406 108,420 96,434 84,420" fill="rgba(56,189,248,0.22)" stroke="#38BDF8" stroke-width="2.2"/>
        <line x1="96" y1="434" x2="96" y2="464" stroke="#38BDF8" stroke-width="1.6"/>
        <text x="116" y="424" text-anchor="start" font-size="12" fill="#E0F2FE">PORT 4G · 0.42 nm</text>
        <polygon points="1104,406 1116,420 1104,434 1092,420" fill="rgba(52,211,153,0.22)" stroke="#34D399" stroke-width="2.2"/>
        <line x1="1104" y1="434" x2="1104" y2="464" stroke="#34D399" stroke-width="1.6"/>
        <text x="1084" y="424" text-anchor="end" font-size="12" fill="#D1FAE5">STBD 4R · 0.80 nm</text>
        <path d="M 190 692 L 390 532" fill="none" stroke="#38BDF8" stroke-width="1.8" stroke-dasharray="10 7" opacity="0.88"/>
        <path d="M 1010 692 L 810 532" fill="none" stroke="#34D399" stroke-width="1.8" stroke-dasharray="10 7" opacity="0.88"/>
        <path d="M 350 538 A 360 90 0 0 1 850 538" fill="none" stroke="#BAE6FD" stroke-width="1.2" stroke-dasharray="5 6" opacity="0.72"/>
        <path d="M 275 590 A 440 110 0 0 1 925 590" fill="none" stroke="#BAE6FD" stroke-width="1.2" stroke-dasharray="5 6" opacity="0.72"/>
        <path d="M 205 645 A 520 130 0 0 1 995 645" fill="none" stroke="#BAE6FD" stroke-width="1.2" opacity="0.75"/>
        <text x="600" y="530" text-anchor="middle" font-size="11.5" fill="#E0F2FE">1.2 nm PIER 4</text>
        <text x="600" y="582" text-anchor="middle" font-size="11.5" fill="#E0F2FE">0.8 nm</text>
        <text x="600" y="638" text-anchor="middle" font-size="11.5" fill="#E0F2FE">0.4 nm</text>
      </svg>
      <div class="v16-ais-marker v16-ais-left va-nums">CH-BUOY 4G · 0.42 nm · BRG 261°</div>
      <div class="v16-ais-marker v16-ais-right va-nums">BERTH 4 GATE · 1.20 nm · CPA CLEAR</div>
    </div>
    <div class="v16-ctrl-chips" role="toolbar" aria-label="Ambient Glare and Bridge Controls">
      <div id="v16-luminance-chips" class="v16-lum-group" role="group" aria-label="Ambient Glare Mode">
        <button type="button" class="va-pill v16-lum-chip is-active" data-variant="chip" data-luminance="daylight" data-contrast="10.8:1" aria-pressed="true">Daylight Glare</button>
        <button type="button" class="va-pill v16-lum-chip" data-variant="chip" data-luminance="dusk" data-contrast="11.9:1" aria-pressed="false">Sunset Watch</button>
        <button type="button" class="va-pill v16-lum-chip" data-variant="chip" data-luminance="night" data-contrast="13.4:1" aria-pressed="false">Night Transit</button>
      </div>
      <div id="v16-bridge-toggles" class="v16-lum-group" role="group" aria-label="Bridge System Toggles">
        <button type="button" id="v16-derate-btn" class="va-pill v16-lum-chip" data-variant="chip" aria-pressed="false">Limit Speed (&lt;= 18 kt)</button>
        <button type="button" id="v16-ais-btn" class="va-pill v16-lum-chip is-active" data-variant="chip" aria-pressed="true">Show Channel Markers</button>
      </div>
    </div>
  </div>
</div>"""
