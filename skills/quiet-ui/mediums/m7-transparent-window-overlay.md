# Quiet UI — Medium M7: Transparent Window Overlay & Spatial Glass

Medium M7 governs spatial computing window overlays, transparent architectural smart glass, vehicle windshield displays, and augmented reality (AR) optical viewports. Unlike M6 collimated HUDs (which use infinity optics and peripheral tapes), M7 hosts structured interactive glass windows that hover against volatile real-world physical backgrounds.

---

## 1. Physical Optics & Environmental Glare Dynamics

```
+-------------------------------------------------------------+
|                      M7 OPTICAL PROFILE                     |
|                                                             |
|  Optical Physics:    Transparent Spatial Plane (Near to Mid)|
|  Ambient Glare:      Highly volatile (0 lux night to        |
|                      100,000 lux direct midday sunlight)    |
|  Scrim Technology:   Luminance-adaptive smoked-glass scrim  |
|  Legibility Armor:   Stroke text halos (paint-order)        |
|  Contrast Anchor:    2.0px luminous edge contrast border    |
|  Primary Palette:    HUD glass tokens (--hud-pod-*)         |
+-------------------------------------------------------------+
```

### Environmental Contrast Dilemma

| Background Environment | Incident Lux | Unshielded Text Result | M7 Smoked Scrim + Halo Fix |
| :--- | :--- | :--- | :--- |
| **Direct Outdoor Sun** | 80,000 – 100,000 lux | Total wash-out; text becomes 100% invisible | Smoked scrim darkens background; dark halo provides 4.5:1 edge ratio |
| **White Office Wall** | 500 – 1,000 lux | White text bleeds into drywall texture | 1.5px dark stroke halo preserves letterform silhouettes |
| **Dark Machinery Room** | 50 – 150 lux | Dark text disappears into shadow | Luminous frosty glass plate + high-light foreground ink |
| **Specular Window Reflections** | Dynamic bursts | Causes intermittent blinking and visual stutter | Deep bilateral blur filter (`blur(24px) saturate(160%)`) |

---

## 2. Luminance-Adaptive Smoked Scrim Architecture

Transparent glass windows require an optical substrate to isolate user content from distracting background motion without completely occluding real-world vision:

```
[EXTERNAL REAL-WORLD BACKGROUND: Dynamic 10,000 Lux Light & Motion]
  │
  ├── [BILATERAL BLUR LAYER: backdrop-filter: blur(20px)]
  │     (Diffuses high-frequency background edges into smooth gradient)
  │
  ├── [SMOKED SCRIM: rgba(9, 14, 24, 0.72) to rgba(28, 27, 25, 0.85)]
  │     (Attenuates bright background photons by 70%)
  │
  ├── [EDGE ANCHOR BORDER: 1px to 1.5px rgba(226, 232, 240, 0.28)]
  │     (Defines spatial card perimeter in 3D depth)
  │
  └── [FOREGROUND TEXT WITH STROKE HALO: paint-order: stroke fill]
        (Guarantees character edge contrast under all lighting angles)
```

---

## 3. Stroke Text Halos & Edge Contrast Enforcement

When text renders over semi-transparent glass, bright background artifacts can penetrate character bodies. Quiet UI enforces SVG and CSS stroke text halos:

```css
.va-glass-halo-text {
  color: #FFFFFF;
  -webkit-text-stroke: 2.5px rgba(0, 0, 0, 0.75);
  paint-order: stroke fill;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
}
```

> **The Halo Invariant**: `paint-order: stroke fill` ensures the dark stroke halo renders **behind** the white fill, preserving sharp glyph anatomy without eroding font weight or legibility.

---

## 4. Concrete CSS Architecture

```css
@layer quiet.mediums, quiet.glass;

@layer quiet.glass {
  /* M7 Spatial Glass Pod */
  .va-m7-glass-card {
    background: var(--hud-pod-bg, rgba(9, 14, 24, 0.75));
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    border: 1.5px solid var(--hud-pod-border, rgba(226, 232, 240, 0.28));
    border-radius: var(--radius-card, 12px);
    padding: var(--density-card-pad, 1.25rem);
    color: var(--hud-pod-text, #F8FAFC);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  }

  /* Stroke Halo Text Class */
  .va-m7-halo-title {
    font-family: var(--font-sans);
    font-size: var(--ts-xl);
    font-weight: 700;
    color: #FFFFFF;
    -webkit-text-stroke: 2.5px rgba(9, 14, 24, 0.85);
    paint-order: stroke fill;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }

  .va-m7-halo-body {
    font-family: var(--font-sans);
    font-size: var(--ts-base);
    color: #F1F5F9;
    -webkit-text-stroke: 1.5px rgba(9, 14, 24, 0.8);
    paint-order: stroke fill;
  }

  /* Edge Contrast Highlighting on Interactive Focus */
  .va-m7-glass-card:focus-within {
    border-color: var(--accent-focal);
    box-shadow: 0 0 0 2px var(--accent-focal), 0 8px 32px 0 rgba(0, 0, 0, 0.5);
  }

  /* Glare Rejection Chip */
  .va-m7-chip {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.24);
    border-radius: var(--radius-pill);
    padding: 0.25rem 0.75rem;
    font-size: var(--ts-xs);
    font-weight: 600;
    color: #E2E8F0;
  }
}
```

---

## 5. HTML Macro Implementation

```html
<section class="va-m7-glass-card" style="max-inline-size: 480px;">
  <!-- Header with Halo Title -->
  <header style="display: flex; justify-content: space-between; align-items: center; margin-block-end: 1rem;">
    <span class="va-kicker" style="color: #94A3B8;">SPATIAL TELEMETRY OVERLAY</span>
    <span class="va-m7-chip">TRACKING LOCKED</span>
  </header>

  <h2 class="va-m7-halo-title">
    Structural Stress Point #A-42
  </h2>

  <div class="va-m7-halo-body" style="margin-block: 0.75rem;">
    Localized shear load: <strong class="va-nums">1,420 N/mm²</strong>. Exceeds standard operating threshold by 12%.
  </div>

  <!-- Interactive Controls within Smoked Scrim -->
  <footer style="display: flex; gap: 0.75rem; margin-block-start: 1.25rem;">
    <button type="button" class="va-pill-btn" style="background: rgba(56, 189, 248, 0.2); border-color: #38BDF8; color: #FFFFFF;">
      ISOLATE SEGMENT
    </button>
    <button type="button" class="va-pill-btn" style="background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.2); color: #E2E8F0;">
      DISMISS
    </button>
  </footer>
</section>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | Spatial Hazard | Quiet UI Resolution |
| :--- | :--- | :--- |
| Zero backdrop blur on transparent cards | High-contrast background patterns show through, rendering text unreadable. | Apply `backdrop-filter: blur(20px) saturate(150%)`. |
| Thin white text without stroke halo | Completely washed out when a bright sunbeam crosses behind the glass. | Apply `paint-order: stroke fill` with 2px dark outer stroke. |
| Borderless transparent floating cards | User loses depth perception of window boundaries in 3D spatial space. | Mandate crisp 1.5px luminous perimeter borders (`--hud-pod-border`). |
| Opaque black boxes blocking real world | Defeats the purpose of transparent smart glass and creates safety blind spots. | Use calibrated smoked scrims (`rgba(9, 14, 24, 0.75)`). |
| Standard thin CSS box-shadows | Shadows disappear against dynamic ambient backgrounds. | Use deep multidirectional shadows (`0 8px 32px rgba(0,0,0,0.4)`). |
