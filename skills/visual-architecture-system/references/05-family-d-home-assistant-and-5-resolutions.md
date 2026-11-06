# Reference 05: Family D — Home Assistant Spatial Archetypes (`15. HA-1` $\rightarrow$ `17. HA-3`) & 5-Resolution Engine

Home Assistant dashboards fail when designed like desktop SaaS web apps or when every smart bulb and nominal sensor is dumped onto the main screen. Always route by **Viewing Distance**, **Touch Ergonomics**, and **Progressive Disclosure**.

---

## 1. Tier `15. HA-1` — Ambient Wall Kiosk Screensaver (`20% HUD`, Default `S1` White, `N0` Zero-Chrome)

- **Target Hardware & Distance:** Wall-mounted display (`1920×1080` or `2560×1440`) viewed from `>= 2m` (`10–16 ft`).
- **60/40 Asymmetric Split (`100dvh` starting at `(0,0)`):**
  - **Full-Bleed Fine-Art / Architectural Backdrop:** Renders an authentic CC0 Claude Monet *Water Lilies (1906)* painting (`<img class="ha1-monet-img" src="assets/monet_water_lilies_1906.jpg" alt="Claude Monet Water Lilies 1906" />`) with a subtle radial readability vignette, or switches live to an Isometric Residence Blueprint (`blueprint`) or OLED Night Minimal (`oled`) canvas.
  - **Left 60%:** Giant tabular clock (`clamp(3.2rem, 6.8cqi, 6.2rem)`), date, perimeter status badge, and museum artwork caption. Zero top mode ribbon in `N0` mode.
  - **Right 40% Theme-Aware Frosted Glass HUD (`.ha1-glass-hud`):** Translucent **Frosted Light Glass** in `S1` White / `S2` Paper modes (`background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(22px) saturate(145%);`) and **Frosted Dark Glass** in `S3` / `S4` modes (`background: rgba(12, 16, 24, 0.46);`), strictly capped at **3 calm blocks**:
    1. **Weather & 4-Slot Horizon:** Current outdoor condition + 4 upcoming time slots (`09:00`, `12:00`, `15:00`, `18:00`) with Font Awesome 6 weather icons (`fa-cloud-sun`, `fa-sun`, `fa-wind`, `fa-moon`).
    2. **Zero-Nominal Exception Pills:** Surfaces ONLY active exceptions (open garage bay, active person detection, running HVAC warmup). Nominal/closed states are hidden.
    3. **Next 3 Upcoming Agenda & Planner Items:** Next 3 household events or scheduled tasks.

---

## 2. Tier `16. HA-2` — Room-First Wall Control Panel (`85%` Box Weight, Default `S2` Paper, `N1` `68px` Rail)

- **Target Hardware & Distance:** Walk-up wall tablet (`1920×1080` / `2560×1440`) at arm's length (`0.5m–1m`).
- **Default `N1` Left Vertical Zone Rail (`.ha2-left-rail`, `68px` wide, `100dvh`):**
  - Houses the live clock (`05:19`), outdoor temperature (`54°F`), `.va-hamburger-btn` rail collapse toggle, and `52px × 52px` walk-up zone filter buttons (`ALL`, `1F`, `2F`, `EXT`) with Font Awesome 6 icons (`fa-border-all`, `fa-couch`, `fa-bed`, `fa-warehouse`). **Single-Bar Law:** Never show two top bars simultaneously; `.ha2-top-strip` is hidden when `.va-poly-n3-topbar` is visible.
- **Decluttered Room Containers (`.ha2-room-card`, `<= 4` metrics per room):**
  - **Header:** Shows `.va-icon-well` (`fa-couch`, `fa-utensils`, `fa-bed`, `fa-server`) + `Room Name` + `71°F · 45%` climate badge.
  - **Body:** Holds at most **1 master `.ha2-slider-tile` group dimmer bar** (`52px` tall) + a 2-column grid of compact `44px` `.ha2-entity-tile` state pills.
- **Contextual Right Inspector Dock (`.ha2-right-dock`, `330px` wide):**
  - Top card: **1 live IP Camera / WebRTC stream** with detection badge.
  - Bottom card (`#ha2-room-inspector`): **Selected-Room Fixture Inspector** with individual fixture sliders, color temperature presets (`2200K`–`5000K`), and **Proportional Background-Fill Circuit Load Breakdown Rows (`.va-prop-bar-row`)** (`HVAC Heat Pump 46.5%`, `Kitchen Induction 26.6%`, `Rack & PoE 17.4%`, `Outdoor 9.5%`) under a recessed `[Circuit | Room | Phase]` switcher.

---

## 3. Tier `17. HA-3` — Full-Viewport Crease-Aware Foldable & Phone Companion App (`85%` Box Weight, Default `S4` Dark, `N4` Thumb Dock)

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
| **Tablet, Foldable & Split-Screen** | `@media (min-width: 641px) and (max-width: 1099px)` | All `N1`/`N3` left sidebars auto-collapse into a **`60px` centered icon-only rail** (`grid-template-columns: 60px minmax(0, 1fr)`); clicking `.va-hamburger-btn` opens a `240px` fixed slide-over drawer (`html.is-drawer-open`); 3rd-column right inspectors dock cleanly below the main column; `HA-3` enters 50/50 crease-aware split |
| **Phone / Narrow** | `@media (max-width: 640px)` | Left sidebars hide off-canvas (`display: none` unless `html.is-drawer-open`), top `N2`/`N3` bars hide, all multi-column grids stack (`minmax(0, 1fr)`), and the **5-slot `52px` sticky bottom thumb bar** activates full-width at `bottom: 0` |
