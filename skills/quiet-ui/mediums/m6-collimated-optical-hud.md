# Quiet UI — Medium M6: Collimated Optical HUD

Medium M6 governs head-up displays (HUD), helmet-mounted displays (HMD), and collimated optical combiner viewports used in aerospace, flight simulation, and marine navigation. Symbology is focused at optical infinity and projected directly across an unpredictable real-world visual scene.

---

## 1. Physical Optics & Infinity Collimation

```
+-------------------------------------------------------------+
|                      M6 OPTICAL PROFILE                     |
|                                                             |
|  Optical Focal Depth: Infinity-Collimated (Parallax-Free)   |
|  Combiner Physics:    Partially reflective see-through glass|
|  Background Scene:    Variable sky, clouds, sun (10,000 lux)|
|  Sightline Keep-Out:  >= 65% central bore clear of symbology|
|  Color Space:         Monochrome Narrowband P43 Phosphor    |
|                       Green (543 nm) or Signal Cyan (490 nm)|
|  Primary Shell:       N0 (Undecorated Infinity Viewport)    |
+-------------------------------------------------------------+
```

### Optical Constraints & Physics

| Parameter | Specification | Physical Justification |
| :--- | :--- | :--- |
| **Focal Distance** | Collimated to optical infinity ($\infty$) | Pilot does not need to re-accommodate eye lens between distant targets and symbology. |
| **Color Palette** | Monochromatic Green (`#4ADE80`) or Cyan (`#38BDF8`) | Human eye photopic sensitivity peaks near 555 nm (maximum photon efficiency). |
| **Background Transmittance** | $70\% - 85\%$ through combiner glass | Symbology must never obscure terrain, runway lights, or collision hazards. |
| **Stroke Rendering** | Vector stroke-only (`fill: none; stroke: 1.5px`) | Solid filled polygons blind the pilot to external real-world flight objects. |
| **Boresight Keep-Out** | $\ge 65\%$ unobstructed central circle | Preserves unobstructed central field of view during flight maneuvering. |

---

## 2. Central Boresight Keep-Out Area ($\ge 65\%$)

Placing dense digital graphics in the center of an optical combiner induces spatial disorientation and increases mid-air collision hazards:

> **The Central Keep-Out Invariant**: A minimum circular area encompassing **$65\%$ of the total combiner diameter** must remain entirely clear of static symbology, text cards, or telemetry pods. Only dynamic flight-path vectors, waterline marks, or target lock reticles may enter this zone.

```
+-----------------------------------------------------------------------------------+
|  M6 Optical Combiner Viewport                                                     |
|                                                                                   |
|    [AIRSPEED TAPE]                                        [ALTITUDE TAPE]         |
|    | 320 |                                                | 14,200 |              |
|    | 310 |                                                | 14,100 |              |
|    | 300 |◄---           +-------------------+            | 14,000 |◄---          |
|    | 290 |               |                   |            | 13,900 |              |
|                          |   BORESIGHT       |                                    |
|                          |   KEEP-OUT ZONE   |                                    |
|                          |   (>= 65% CLEAR)  |                                    |
|                          |                   |                                    |
|                          +-------------------+                                    |
|                                                                                   |
|                               -.- [ -W- ] -.- (Waterline Pitch Ladder)            |
|                                                                                   |
|    [G-METER: +1.2G]                                       [HEADING TAPE: 270°]    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Narrowband Phosphor Symbology Palette

Optical see-through displays cannot project "black" (black is simply transparent glass). Contrast is achieved strictly through additive luminance against outdoor ambient light:

- **Primary Green Phosphor**: `oklch(0.85 0.22 145)` or `#4ADE80` (High outdoor luminance penetration).
- **Secondary Cyan Phosphor**: `oklch(0.82 0.18 215)` or `#38BDF8` (High-contrast navigation cue).
- **Zero Filled Surfaces**: All containers, scales, and tapes render with transparent backgrounds (`background: transparent; border: 1.5px solid var(--hud-stroke)`).

---

## 4. Concrete CSS Architecture

```css
@layer quiet.mediums, quiet.hud;

@layer quiet.hud {
  /* M6 HUD Root Viewport */
  .va-m6-hud {
    position: fixed;
    inset: 0;
    inline-size: 100vw;
    block-size: 100vh;
    background: transparent;
    color: #4ADE80; /* Phosphor Green */
    font-family: var(--font-mono);
    pointer-events: none;
    overflow: hidden;
  }

  /* Optical Vector Stroke Rules */
  .va-hud-stroke {
    fill: none;
    stroke: #4ADE80;
    stroke-width: 1.5px;
    stroke-linecap: round;
    stroke-linejoin: round;
    filter: drop-shadow(0 0 2px rgba(74, 222, 128, 0.6));
  }

  /* Central Boresight Keep-Out Boundary (Verification Only) */
  .va-hud-keepout-ring {
    position: absolute;
    inset: 17.5%;
    inline-size: 65%;
    block-size: 65%;
    border-radius: 50%;
    pointer-events: none;
  }

  /* Peripheral Airspeed & Altitude Tapes */
  .va-hud-tape-speed {
    position: absolute;
    inset-block-start: 25%;
    inset-inline-start: 5%;
    inline-size: 60px;
    block-size: 50%;
    border-inline-end: 1.5px solid #4ADE80;
  }

  .va-hud-tape-alt {
    position: absolute;
    inset-block-start: 25%;
    inset-inline-end: 5%;
    inline-size: 70px;
    block-size: 50%;
    border-inline-start: 1.5px solid #4ADE80;
  }

  /* Waterline Boresight Reference */
  .va-hud-waterline {
    position: absolute;
    inset-block-start: 50%;
    inset-inline-start: 50%;
    transform: translate(-50%, -50%);
  }
}
```

---

## 5. HTML Macro Implementation

```html
<div class="va-m6-hud" aria-hidden="true">
  <!-- Central Waterline Reticle -->
  <svg class="va-hud-waterline" width="60" height="20" viewBox="0 0 60 20">
    <path class="va-hud-stroke" d="M 0 10 L 20 10 L 25 15 L 30 10 L 35 15 L 40 10 L 60 10" />
  </svg>

  <!-- Peripheral Left Airspeed Tape -->
  <aside class="va-hud-tape-speed">
    <div style="font-size: 14px; text-align: right; padding-inline-end: 6px;">320</div>
    <div style="font-size: 18px; font-weight: 700; text-align: right; padding-inline-end: 6px;">310◄</div>
    <div style="font-size: 14px; text-align: right; padding-inline-end: 6px;">300</div>
  </aside>

  <!-- Peripheral Right Altitude Tape -->
  <aside class="va-hud-tape-alt">
    <div style="font-size: 14px; padding-inline-start: 6px;">14,200</div>
    <div style="font-size: 18px; font-weight: 700; padding-inline-start: 6px;">►14,100</div>
    <div style="font-size: 14px; padding-inline-start: 6px;">14,000</div>
  </aside>

  <!-- Peripheral Bottom Compass Heading -->
  <footer style="position: absolute; inset-block-end: 8%; inset-inline-start: 50%; transform: translateX(-50%); font-size: 16px;">
    [ 260 ··· 270 ··· 280 ]
  </footer>
</div>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | Flight Hazard | Quiet UI Resolution |
| :--- | :--- | :--- |
| Opaque card backgrounds on combiner glass | Blinds the pilot to real-world aircraft, terrain, and runway edges. | Enforce `background: transparent; fill: none;` on all HUD elements. |
| Heavy symbology placed in center 65% area | Masks external flight hazards directly in the pilot's line of sight. | Maintain strict $\ge 65\%$ central keep-out area. |
| Multi-color red, yellow, and blue text elements | Color dispersion through optical prism; causes chromatic aberration. | Use single-wavelength narrow phosphor green or cyan only. |
| Mouse hover or touch interaction bindings | Pilot hands are on flight stick/throttle; cursor interactions fail completely. | HUD is strictly read-only symbology driven by vehicle avionics bus. |
| Non-monospaced proportional numbers on tapes | Altitude readout numbers shift laterally during rapid climbs. | Apply `font-family: var(--font-mono)` with `tabular-nums`. |
