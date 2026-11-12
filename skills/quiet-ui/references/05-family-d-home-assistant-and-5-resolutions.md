# Reference 05: Home Assistant Spatial Archetypes (`15. HA-1` $\rightarrow$ `17. HA-3`) & 3-Breakpoint Viewport Engine

Smart-home dashboards fail when designed like desktop SaaS web apps or when every smart bulb and nominal sensor is dumped onto the main screen. Always route by **Viewing Distance**, **Touch Ergonomics**, and **Progressive Disclosure**.

---

## 1. Tier `15. HA-1` — Ambient Wall Kiosk Screensaver (`20% HUD`, Default `white`, `N0` Zero-Chrome)

- **Target Hardware & Distance:** Wall-mounted display (`1920×1080` or `2560×1440`) viewed from `>= 2m` (`10–16 ft`).
- **Full-Bleed Monet Artwork Stage + Transparent Right Card Stack (`65%` Unobstructed Painting):**
  - Renders the authentic CC0 Claude Monet *Water Lilies (1906)* painting (`<img class="ha1-monet-img" src="assets/monet_water_lilies_1906.jpg" alt="Claude Monet Water Lilies 1906" />`) across `100%` of `.ha1-stage.ha1-monet-stage` (`object-fit: cover; object-position: center;`).
  - The outer right container (`.ha1-glass-hud.ha1-hud-rail`) is strictly transparent (`background: transparent !important; border: none !important; box-shadow: none !important; backdrop-filter: none !important; height: auto !important; gap: 12px !important;`) so the Monet painting is completely visible between and below the 3 compact floating `.va-glass-panel` cards (`>= 1024px`: `1fr 370px`; `641px–1023px`: 2-column bottom card grid preserving `45%–50%` open artwork stage).
- **Tinted Deep-Crystal Optical Glass Formula (All 4 Themes Over the Dark Monet Canvas):**
  - **Floating Glass Cards (`.va-glass-panel`):** `background: linear-gradient(135deg, rgba(16, 28, 44, 0.58) 0%, rgba(12, 22, 36, 0.42) 100%) !important; backdrop-filter: blur(24px) saturate(180%) !important; -webkit-backdrop-filter: blur(24px) saturate(180%) !important; border: 1px solid rgba(255, 255, 255, 0.22) !important; box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.34), 0 20px 40px -12px rgba(2, 6, 23, 0.50) !important; border-radius: var(--radius-card, 18px) !important; color: #F8FAFC !important; padding: 14px 16px !important;`
  - **Concentric Inner Glass Controls (`.va-glass-tile`, `.va-glass-pill`, `.va-glass-slider` — Zero Chalky White Boxes):** Derive their corner radius from `var(--radius-inner)` with `background: rgba(255, 255, 255, 0.10) !important; border: 1px solid rgba(255, 255, 255, 0.18) !important; box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22) !important; color: #F8FAFC !important; backdrop-filter: blur(12px) saturate(140%) !important;`. `.va-glass-slider` tracks render a luminous warm Monet-gold fill bar (`linear-gradient(90deg, rgba(229, 184, 105, 0.48), rgba(235, 168, 178, 0.42))`).
  - **Plain-Language Floating Cards & Sleek 10-Dot Museum Plaquette:**
    1. **`Conservatory Climate` (`.va-glass-panel`):** Outdoor/indoor humidity & temp capsules, HVAC mode pills (`.va-glass-pill`: `Heat 71.5°F`, `Auto Eco`, `Humidifier 45%`), and 4-slot `.ha1-hour-cell.va-glass-tile` horizon.
    2. **`Lighting & Scenes` (`.va-glass-panel`):** Interactive glass dimmer sliders (`.va-glass-slider`: `Conservatory Pendants 72%`, `Gallery Wall Wash 45%`, `Garden Path & Pond 100%`) + 2×2 `.va-glass-tile` room/scene toggles (`Monet Pond`, `Morning Mist`, `Evening Warmth`, `Night Watch`).
    3. **`Household Activity` (`.va-glass-panel`):** Zero-nominal active exception rows (`Driveway AI · Person Detected`, `1st Floor HVAC · Morning Warmup`).
    4. **Bottom-Left Clock & Sleek Museum Plaquette (`.va-glass-panel`):** Anchors the `05:19` clock (`clamp(42px, 4.5vw, 56px)`) directly above a compact glass plaquette displaying *Water Lilies (Evening Effect · 1906)*, **10 circular `18px × 18px` oil-pigment dots** (`.ha1-swatch-dot`, `#142238`..`#F3DAD2`), and glass mode pills (`Monet`, `Blueprint`, `OLED`, `Alert`).

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
