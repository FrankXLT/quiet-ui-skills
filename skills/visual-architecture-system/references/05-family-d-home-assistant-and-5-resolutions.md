# Reference 05: Home Assistant Spatial Archetypes (`15. HA-1` $\rightarrow$ `17. HA-3`) & 3-Breakpoint Viewport Engine

Smart-home dashboards fail when designed like desktop SaaS web apps or when every smart bulb and nominal sensor is dumped onto the main screen. Always route by **Viewing Distance**, **Touch Ergonomics**, and **Progressive Disclosure**.

---

## 1. Tier `15. HA-1` — Ambient Wall Kiosk Screensaver (`20% HUD`, Default `white`, `N0` Zero-Chrome)

- **Target Hardware & Distance:** Wall-mounted display (`1920×1080` or `2560×1440`) viewed from `>= 2m` (`10–16 ft`).
- **Full-Bleed Monet Artwork Stage (`.ha1-stage.ha1-monet-stage`, `100dvh` starting at `(0,0)`):**
  - Renders the authentic CC0 Claude Monet *Water Lilies (1906)* painting (`<img class="ha1-monet-img" src="assets/monet_water_lilies_1906.jpg" alt="Claude Monet Water Lilies 1906" />`) across `100%` of the stage (`object-fit: cover; object-position: center;`) so every control panel, HUD header, dimmer slider, and scene pill floats directly over the artwork and refracts its oil pigments. Also switches live to an Isometric Residence Blueprint (`blueprint`) or OLED Night Minimal (`oled`) canvas.
- **True Optical Glassmorphism Control Panels (`.va-glass-panel`, `.va-glass-tile`, `.va-glass-slider`, `.va-glass-pill`):**
  - **Outer Glass Panels (`.ha1-glass-hud, .va-glass-panel`):** Enforce `backdrop-filter: blur(22px) saturate(165%) !important; -webkit-backdrop-filter: blur(22px) saturate(165%) !important;` with adaptive translucent surfaces across all 4 themes (never an opaque `rgb()` fill):
    - **Light Glass (`white`, `paper`):** `background: linear-gradient(135deg, rgba(255, 255, 255, 0.60) 0%, rgba(248, 250, 252, 0.38) 100%) !important; border: 1px solid rgba(255, 255, 255, 0.52) !important; box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.72), 0 16px 36px -8px rgba(15, 23, 42, 0.22) !important;`
    - **Dark Smoked Glass (`dark-paper`, `dark`):** `background: linear-gradient(135deg, rgba(15, 23, 42, 0.62) 0%, rgba(15, 23, 42, 0.38) 100%) !important; border: 1px solid rgba(255, 255, 255, 0.20) !important; box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.26), 0 16px 36px -8px rgba(2, 6, 23, 0.55) !important;`
  - **Concentric Inner Glass Controls (`.va-glass-tile`, `.va-glass-pill`, `.va-glass-slider`):** Derive their corner radius from `var(--radius-inner)` (`max(0px, calc(var(--radius-card, 8px) - var(--inset-pad, 4px)))`) with `backdrop-filter: blur(12px) saturate(140%) !important`, translucent inner fill (`rgba(255,255,255,0.34)` in light / `rgba(30,41,59,0.44)` in dark), and a `1px` specular top catch-light (`inset 0 1px 0 rgba(255,255,255,0.45)`).
  - **3 Interactive Glass Control Panels Floating Over the Monet Stage:**
    1. **Panel 1 — Ambient Weather, Time & Conservatory Climate Glass HUD (`.va-glass-panel`):** Outdoor/indoor humidity & temp capsules, HVAC mode pills (`.va-glass-pill`: `Heat 71.5°F`, `Auto Eco`, `Humidifier 45%`), and 4-slot `.ha1-hour-cell.va-glass-tile` horizon.
    2. **Panel 2 — Lighting & Dimmer Glass Control Deck (`.va-glass-panel`):** Interactive glass dimmer sliders (`.va-glass-slider`: `Conservatory Pendants 72%`, `Gallery Wall Wash 45%`, `Garden Path & Pond 100%`) with glowing Monet-palette `rgba` fill tracks, plus a 2×2 grid of concentric `.va-glass-tile` room/scene toggles (`Monet Pond`, `Morning Mist`, `Evening Warmth`, `Night Watch`).
    3. **Panel 3 — Algorithmic Monet 10-Color Palette & Sensor Dock (`.va-glass-panel`):** Bottom-left glass dock displaying the 10 extracted Monet oil-painting swatches (`#142238`..`#F3DAD2` in `.va-glass-tile` cells), artwork metadata caption, and live telemetry pills (`.va-glass-pill`).

---

## 2. Tier `16. HA-2` — Room-First Wall Control Panel (`85%` Box Weight, Default `white`, `N1` `68px` Rail)

- **Target Hardware & Distance:** Walk-up wall tablet (`1920×1080` / `2560×1440`) at arm's length (`0.5m–1m`).
- **Default `N1` Left Vertical Zone Rail (`.ha2-left-rail`, `68px` wide, `100dvh`):**
  - Houses the live clock (`05:19`), outdoor temperature (`54°F`), `.va-hamburger-btn` rail collapse toggle, and `52px × 52px` walk-up zone filter buttons (`ALL`, `1F`, `2F`, `EXT`) with Font Awesome 6 icons (`fa-border-all`, `fa-couch`, `fa-bed`, `fa-warehouse`). **Single-Bar Rule:** Never show two top bars simultaneously; `.ha2-top-strip` is hidden when `.va-poly-n3-topbar` is visible.
- **Decluttered Room Containers (`.ha2-room-card`, `<= 4` metrics per room):**
  - **Header:** Shows `.va-icon-well` (`fa-couch`, `fa-utensils`, `fa-bed`, `fa-server`) + `Room Name` + `71°F · 45%` climate badge.
  - **Body:** Holds at most **1 master `.ha2-slider-tile` group dimmer bar** (`52px` tall) + a 2-column grid of compact `44px` `.ha2-entity-tile` state pills.
- **Contextual Right Inspector Dock (`.ha2-right-dock`, `330px` wide):**
  - Top card: **1 live IP Camera / WebRTC stream** with detection badge.
  - Bottom card (`#ha2-room-inspector`): **Selected-Room Fixture Inspector** with individual fixture sliders, color temperature presets (`2200K`–`5000K`), and **Proportional Share Bars (`.va-prop-bar-row`)** showing circuit load breakdown (`HVAC Heat Pump 46.5%`, `Kitchen Induction 26.6%`, `Rack & PoE 17.4%`, `Outdoor 9.5%`) under a recessed `[Circuit | Room | Phase]` switcher.

---

## 3. Tier `17. HA-3` — Full-Viewport Crease-Aware Foldable & Phone Companion App (`85%` Box Weight, Default `white`, `N4` Thumb Dock)

- **Zero Fake Hardware Bezels:** `HA-3` is never trapped inside a simulated `390px`/`820px` `#ha3-device-frame` box. It owns `100%` of the real browser viewport (`min-height: 100dvh`) and adapts via native `@media` queries:
  - **Desktop (`@media (min-width: 1100px)`):** `.ha3-split-body` renders a multi-column left tile grid (`repeat(auto-fill, minmax(210px, 1fr))`) paired with a `360px` right `#ha3-detail-inspector` (`grid-template-columns: minmax(0, 1fr) 360px`) and a centered `560px` floating `N4` bottom pill dock.
  - **Unfolded Foldable & Tablet (`@media (min-width: 641px) and (max-width: 1099px)`):** `.ha3-split-body` snaps into a **50/50 crease-aware master-detail split** (`grid-template-columns: 1fr 1fr`) with `.ha3-fold-crease` visible at `left: 50%`, 2-column `.ha3-tile-grid` on the left, and `#ha3-detail-inspector` on the right.
  - **Portrait Phone (`@media (max-width: 640px)`):** `.ha3-split-body` stacks into a single column (`minmax(0, 1fr)`) with a 2-column grid of `56px` `.ha3-tile` cards on top, `#ha3-detail-inspector` docked below, and a full-width sticky `52px` 5-slot `.ha3-thumb-dock` at `bottom: 0`.

---

## 4. Native 3-Breakpoint `@media` Viewport Engine (`#va-live-viewport-readout`)

Every tier always owns `100%` of the real browser window (`width: 100%; max-width: 100%`) and adapts automatically on window resize:

| Breakpoint | `@media` Query | Navigation & Grid Adaptation Across All 17 Tiers |
| :--- | :--- | :--- |
| **Desktop & Wall** | `@media (min-width: 1100px)` | Full `220px–260px` left sidebars (`N1`/`N3`, collapsible to `60px` via `.va-hamburger-btn`), 3-column workbenches, centered `560px` `N4` pill dock |
| **Tablet, Foldable & Split-Screen** | `@media (min-width: 641px) and (max-width: 1099px)` | All `N1`/`N3` left sidebars auto-collapse into a **`60px` centered icon-only rail** (`grid-template-columns: 60px minmax(0, 1fr)`); clicking `.va-hamburger-btn` expands the sidebar in-flow (`html.is-drawer-open`); 3rd-column right inspectors dock cleanly below the main column; `HA-3` enters 50/50 crease-aware split |
| **Phone / Narrow** | `@media (max-width: 640px)` | Left sidebars hide off-canvas (`display: none` unless `html.is-drawer-open`), top `N2`/`N3` bars hide, all multi-column grids stack (`minmax(0, 1fr)`), and the **5-slot `52px` sticky bottom thumb bar** activates full-width at `bottom: 0` |
