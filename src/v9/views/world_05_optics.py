#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.2 — M6 MIL-STD-1787B Flight HUD & M7 Conformal Smart-Glass Optics."""

from __future__ import annotations

from typing import Any

try:
    from world_common import cm_val
except ImportError:
    from src.v9.views.world_common import cm_val


def _v15_scene_svg() -> str:
    """Render full-bleed scenic backplates for Daylight RWY 08 and Night Coastal Approach."""
    return """<svg class="v15-scene-svg" viewBox="0 0 1200 720" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <linearGradient id="v15-day-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#2563EB"/>
          <stop offset="48%" stop-color="#60A5FA"/>
          <stop offset="84%" stop-color="#DBEAFE"/>
          <stop offset="100%" stop-color="#F8FAFC"/>
        </linearGradient>
        <linearGradient id="v15-day-ground" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#64748B"/>
          <stop offset="28%" stop-color="#475569"/>
          <stop offset="100%" stop-color="#334155"/>
        </linearGradient>
        <linearGradient id="v15-night-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#020617"/>
          <stop offset="65%" stop-color="#071526"/>
          <stop offset="100%" stop-color="#0F263D"/>
        </linearGradient>
        <linearGradient id="v15-night-sea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#07111F"/>
          <stop offset="100%" stop-color="#030712"/>
        </linearGradient>
      </defs>
      <g class="v15-scene-day">
        <rect x="0" y="0" width="1200" height="370" fill="url(#v15-day-sky)"/>
        <path d="M0 360 L0 336 Q130 318 270 332 T560 336 T880 326 T1200 338 L1200 360 Z" fill="#94A3B8" opacity="0.62"/>
        <g fill="#FFFFFF">
          <ellipse cx="145" cy="272" rx="150" ry="52" fill="#E2E8F0"/>
          <ellipse cx="165" cy="256" rx="120" ry="44" fill="#FFFFFF"/>
          <ellipse cx="360" cy="285" rx="165" ry="48" fill="#F1F5F9"/>
          <ellipse cx="385" cy="270" rx="115" ry="38" fill="#FFFFFF"/>
          <ellipse cx="835" cy="282" rx="160" ry="46" fill="#F1F5F9"/>
          <ellipse cx="855" cy="264" rx="125" ry="40" fill="#FFFFFF"/>
          <ellipse cx="1055" cy="268" rx="155" ry="50" fill="#E2E8F0"/>
          <ellipse cx="1040" cy="252" rx="120" ry="42" fill="#FFFFFF"/>
        </g>
        <rect x="0" y="346" width="1200" height="24" fill="#F8FAFC" opacity="0.45"/>
        <rect x="0" y="362" width="1200" height="358" fill="url(#v15-day-ground)"/>
        <path d="M562 362 L638 362 L945 720 L255 720 Z" fill="#1E293B"/>
        <path d="M565 362 L569 362 L285 720 L272 720 Z" fill="#F8FAFC" opacity="0.88"/>
        <path d="M631 362 L635 362 L928 720 L915 720 Z" fill="#F8FAFC" opacity="0.88"/>
        <g>
          <path d="M350 658 L372 658 L360 688 L334 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M402 658 L424 658 L415 688 L391 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M454 658 L476 658 L470 688 L447 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M506 658 L528 658 L525 688 L503 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M672 658 L694 658 L697 688 L675 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M724 658 L746 658 L753 688 L730 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M776 658 L798 658 L809 688 L785 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M828 658 L850 658 L866 688 L840 688 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M452 572 L494 572 L482 598 L434 598 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M706 572 L748 572 L766 598 L718 598 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M597 380 L603 380 L604 398 L596 398 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M596 414 L604 414 L605 440 L595 440 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M595 464 L605 464 L606 498 L594 498 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M594 528 L606 528 L608 574 L592 574 Z" fill="#F8FAFC" opacity="0.9"/>
          <path d="M592 612 L608 612 L611 670 L589 670 Z" fill="#F8FAFC" opacity="0.9"/>
        </g>
      </g>
      <g class="v15-scene-night">
        <rect x="0" y="0" width="1200" height="370" fill="url(#v15-night-sky)"/>
        <g fill="#93C5FD" opacity="0.55">
          <circle cx="195" cy="88" r="1.3"/><circle cx="318" cy="134" r="1.1"/><circle cx="485" cy="72" r="1.4"/>
          <circle cx="712" cy="96" r="1.2"/><circle cx="888" cy="128" r="1.5"/><circle cx="1015" cy="78" r="1.1"/>
        </g>
        <path d="M0 362 L0 330 Q175 308 360 328 T760 326 T1200 334 L1200 362 Z" fill="#0B1626"/>
        <rect x="0" y="362" width="1200" height="358" fill="url(#v15-night-sea)"/>
        <path d="M556 362 L644 362 L960 720 L240 720 Z" fill="#0A101C"/>
        <g fill="#22C55E">
          <circle cx="348" cy="650" r="3.4"/><circle cx="412" cy="650" r="3.4"/><circle cx="476" cy="650" r="3.4"/>
          <circle cx="540" cy="650" r="3.4"/><circle cx="660" cy="650" r="3.4"/><circle cx="724" cy="650" r="3.4"/>
          <circle cx="788" cy="650" r="3.4"/><circle cx="852" cy="650" r="3.4"/>
        </g>
        <g fill="#FDE047">
          <circle cx="322" cy="680" r="3.8"/><circle cx="378" cy="612" r="3.3"/><circle cx="430" cy="548" r="2.9"/>
          <circle cx="474" cy="492" r="2.5"/><circle cx="512" cy="444" r="2.2"/><circle cx="542" cy="404" r="1.8"/>
          <circle cx="878" cy="680" r="3.8"/><circle cx="822" cy="612" r="3.3"/><circle cx="770" cy="548" r="2.9"/>
          <circle cx="726" cy="492" r="2.5"/><circle cx="688" cy="444" r="2.2"/><circle cx="658" cy="404" r="1.8"/>
        </g>
        <g fill="#E2E8F0" opacity="0.9">
          <circle cx="600" cy="622" r="2.8"/><circle cx="600" cy="560" r="2.4"/><circle cx="600" cy="505" r="2.1"/>
          <circle cx="600" cy="458" r="1.8"/><circle cx="600" cy="418" r="1.6"/><circle cx="600" cy="386" r="1.3"/>
        </g>
        <circle cx="458" cy="532" r="4" fill="#F8FAFC"/><circle cx="474" cy="532" r="4" fill="#F8FAFC"/>
        <circle cx="490" cy="532" r="4" fill="#EF4444"/><circle cx="506" cy="532" r="4" fill="#EF4444"/>
      </g>
    </svg>"""


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

        <text x="1064" y="136" text-anchor="start" font-size="12">FT MSL</text>
        <line x1="1064" y1="150" x2="1064" y2="540" stroke-width="2"/>
        {alt_ticks}
        <path d="M1060 345 L1074 325 L1162 325 L1162 365 L1074 365 Z" fill="none" stroke-width="2.2"/>
        <text x="1116" y="352" text-anchor="middle" font-size="18">8,520</text>
        <text x="1158" y="576" text-anchor="end" font-size="13">VS -650 FPM</text>
        <text x="1158" y="598" text-anchor="end" font-size="13">29.92 IN</text>

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

        <circle cx="600" cy="405" r="11" fill="none" stroke-width="2.2"/>
        <path d="M568 405 H589 M611 405 H632 M600 394 V381" fill="none" stroke-width="2.2"/>
        <text x="44" y="684" text-anchor="start" font-size="14">PROP BTE {bte:.1f}% · IMEP 14.0 BAR</text>
      </g>
    </svg>"""


def build_v15_hud_html(corpus: dict[str, Any]) -> str:
    """Build v15 M6 Collimated Optical Flight HUD with 3 multi-layer backplates."""
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    return f"""<div class="v9-stage-inner v9-view-v15">
  <div id="v15-hud-stage" class="v15-hud-stage" data-backplate="earthrise">
    <img id="v15-earthrise-img" class="v15-earthrise-img" alt="" decoding="async"/>
    {_v15_scene_svg()}
    {_v15_reticle_svg(bte)}
    <div id="v15-backplate-chips" class="v15-hud-mode-strip" role="group" aria-label="Optical Backplate Scene">
      <button type="button" class="va-pill v15-hud-chip is-active" data-variant="chip" data-backplate="earthrise" aria-pressed="true">Orbital</button>
      <button type="button" class="va-pill v15-hud-chip" data-variant="chip" data-backplate="daylight" aria-pressed="false">Daylight RWY</button>
      <button type="button" class="va-pill v15-hud-chip" data-variant="chip" data-backplate="lowlight" aria-pressed="false">Night NVG</button>
    </div>
  </div>
</div>"""


def _v16_scene_svg() -> str:
    """Render perspective suspension causeway, skyline, and conformal road AR lines."""
    return """<svg class="v16-scene-svg" viewBox="0 0 1200 720" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <linearGradient id="v16-sky-day" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#38BDF8"/><stop offset="52%" stop-color="#BAE6FD"/><stop offset="100%" stop-color="#F8FAFC"/>
        </linearGradient>
        <linearGradient id="v16-sky-dusk" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#1E3A8A"/><stop offset="56%" stop-color="#B45309"/><stop offset="100%" stop-color="#F59E0B"/>
        </linearGradient>
        <linearGradient id="v16-sky-night" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#020617"/><stop offset="65%" stop-color="#0B1324"/><stop offset="100%" stop-color="#1E293B"/>
        </linearGradient>
        <radialGradient id="v16-sun-glare" cx="0.62" cy="0.34" r="0.34">
          <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.92"/>
          <stop offset="40%" stop-color="#FEF3C7" stop-opacity="0.45"/>
          <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="v16-road-deck" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#475569"/><stop offset="100%" stop-color="#1E293B"/>
        </linearGradient>
      </defs>
      <rect class="v16-sky-fill v16-only-day" x="0" y="0" width="1200" height="320" fill="url(#v16-sky-day)"/>
      <rect class="v16-sky-fill v16-only-dusk" x="0" y="0" width="1200" height="320" fill="url(#v16-sky-dusk)"/>
      <rect class="v16-sky-fill v16-only-night" x="0" y="0" width="1200" height="320" fill="url(#v16-sky-night)"/>
      <rect class="v16-only-day" x="0" y="0" width="1200" height="320" fill="url(#v16-sun-glare)"/>
      <rect class="v16-only-dusk" x="0" y="0" width="1200" height="320" fill="url(#v16-sun-glare)" opacity="0.65"/>
      <g class="v16-clouds">
        <ellipse cx="180" cy="128" rx="190" ry="42" fill="#FFFFFF" opacity="0.72"/>
        <ellipse cx="1010" cy="142" rx="195" ry="44" fill="#FFFFFF" opacity="0.68"/>
      </g>
      <path d="M0 315 L0 264 Q140 232 300 266 L460 288 L760 288 L930 256 Q1080 236 1200 268 L1200 315 Z" fill="#475569" opacity="0.68"/>
      <rect x="0" y="310" width="1200" height="410" fill="#1E293B"/>
      <g class="v16-bridge-structure">
        <rect x="170" y="42" width="16" height="310" fill="#334155"/><rect x="218" y="42" width="16" height="310" fill="#334155"/>
        <rect x="170" y="76" width="64" height="12" fill="#475569"/><rect x="170" y="168" width="64" height="12" fill="#475569"/>
        <rect x="966" y="42" width="16" height="310" fill="#334155"/><rect x="1014" y="42" width="16" height="310" fill="#334155"/>
        <rect x="966" y="76" width="64" height="12" fill="#475569"/><rect x="966" y="168" width="64" height="12" fill="#475569"/>
        <g stroke="#CBD5E1" stroke-width="2.2" opacity="0.72">
          <line x1="178" y1="54" x2="10" y2="296"/><line x1="178" y1="54" x2="86" y2="306"/>
          <line x1="226" y1="54" x2="310" y2="308"/><line x1="226" y1="54" x2="392" y2="308"/>
          <line x1="974" y1="54" x2="808" y2="308"/><line x1="974" y1="54" x2="890" y2="308"/>
          <line x1="1022" y1="54" x2="1114" y2="306"/><line x1="1022" y1="54" x2="1190" y2="296"/>
        </g>
        <g class="v16-only-night" fill="#EF4444">
          <circle cx="178" cy="40" r="4"/><circle cx="226" cy="40" r="4"/>
          <circle cx="974" cy="40" r="4"/><circle cx="1022" cy="40" r="4"/>
        </g>
      </g>
      <path d="M510 310 L690 310 L1180 720 L20 720 Z" fill="#64748B"/>
      <path d="M522 310 L678 310 L1132 720 L68 720 Z" fill="url(#v16-road-deck)"/>
      <g>
        <path d="M532 325 L536 325 L230 720 L216 720 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M664 325 L668 325 L984 720 L970 720 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M572 340 L575 340 L565 376 L559 376 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M551 404 L558 404 L535 478 L522 478 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M504 532 L520 532 L478 656 L450 656 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M625 340 L628 340 L641 376 L635 376 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M642 404 L649 404 L678 478 L665 478 Z" fill="#E2E8F0" opacity="0.82"/>
        <path d="M680 532 L696 532 L750 656 L722 656 Z" fill="#E2E8F0" opacity="0.82"/>
      </g>
      <g transform="translate(556, 376)">
        <path d="M12 22 L20 4 H68 L76 22 L84 26 V52 H4 V26 Z" fill="#0F172A" stroke="#475569" stroke-width="1.5"/>
        <path d="M22 7 H66 L72 20 H16 Z" fill="#334155"/>
        <rect x="8" y="29" width="15" height="6" rx="1" fill="#EF4444"/>
        <rect x="65" y="29" width="15" height="6" rx="1" fill="#EF4444"/>
      </g>
      <path d="M542 468 L658 468 L774 696 L426 696 Z" fill="#38BDF8" opacity="0.11"/>
      <path d="M542 468 L426 696 M658 468 L774 696" fill="none" stroke="#38BDF8" stroke-width="3" opacity="0.88"/>
      <path d="M498 548 V536 M498 548 H702 M702 548 V536" fill="none" stroke="#7DD3FC" stroke-width="3" opacity="0.95"/>
    </svg>"""


def build_v16_glass_html(corpus: dict[str, Any]) -> str:
    """Build v16 M7 Conformal See-Through Windshield Smart-Glass Overlay."""
    cm = corpus["canonical_metrics"]
    bte = float(cm_val(cm, "peak_bte_pct"))
    return f"""<div class="v9-stage-inner v9-view-v16">
  <div id="v16-glass-viewport" class="v16-glass-viewport" data-luminance="daylight" data-contrast="10.8:1">
    {_v16_scene_svg()}
    <section class="v16-glass-pod v16-pod-left" aria-label="Speed, Route and Efficiency">
      <div class="v16-speed-row">
        <span class="v16-speed-val va-nums">42</span>
        <span class="v16-speed-unit">mph</span>
        <span class="v16-speed-cap va-nums">45 mph DERATE LIMIT</span>
      </div>
      <div class="v16-route-line">E-Bound Bay Causeway · 2.4 mi to Maint Turnout</div>
      <div class="v16-eff-line va-nums">Cruise Efficiency: <strong>{bte:.1f}% BTE</strong></div>
    </section>
    <section class="v16-glass-pod v16-pod-right v16-pod-warn" aria-label="Drivetrain Advisory">
      <span class="va-pill" data-variant="status" data-state="warn">DRIVETRAIN DERATE</span>
      <div class="v16-warn-title">MCU Thermal Limit (85 °C)</div>
      <div class="v16-warn-action">Hold &lt;= 45 mph · Inspect Rear Harness Stub at Next Stop</div>
    </section>
    <div class="v16-road-gap-badge va-nums" aria-label="Conformal Safe Following Distance">2.8 s · 53 m SAFE FOLLOWING GAP</div>
    <div id="v16-luminance-chips" class="v16-ctrl-chips" role="group" aria-label="Ambient Glare Mode">
      <button type="button" class="va-pill v16-lum-chip is-active" data-variant="chip" data-luminance="daylight" data-contrast="10.8:1" aria-pressed="true">Daylight Glare</button>
      <button type="button" class="va-pill v16-lum-chip" data-variant="chip" data-luminance="dusk" data-contrast="11.9:1" aria-pressed="false">Horizon Dusk</button>
      <button type="button" class="va-pill v16-lum-chip" data-variant="chip" data-luminance="night" data-contrast="13.4:1" aria-pressed="false">Night Cabin</button>
    </div>
  </div>
</div>"""
