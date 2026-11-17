# Quiet UI — Medium M5: Ambient Wall Kiosk & 10-Foot Overview

Medium M5 governs large wall-mounted displays across power grid control rooms (`ISA-101` / `NRC NUREG-0700`), hospital census/ICU command boards (`FDA IEC 62366`), mission operations centers (`NASA-STD-3001`), and industrial plant floors viewed from 3 to 5 meters by standing or walking teams.

---

## 1. Physical Optics & Viewing Geometry (10-Foot UI)

```
+-------------------------------------------------------------+
|                      M5 OPTICAL PROFILE                     |
|                                                             |
|  Viewing Distance:  3 – 5 meters (10-foot to 16-foot UI)    |
|  Display Hardware:  55" – 85" Ultra-HD 4K Commercial Panels |
|  Cognitive Mode:    Peripheral awareness, glanceability     |
|  Input Modality:    Non-interactive passive monitoring      |
|  Typography Floor:  >= 24px (Minimum readable character size)|
|  Layout Density:    Spacious Macro-Tiles (Low information   |
|                     density, high semantic signal)          |
+-------------------------------------------------------------+
```

### Optical Parameters vs. Desktop Displays

| Parameter | Desktop Workstation (M3) | Ambient Wall Kiosk (M5) |
| :--- | :--- | :--- |
| **Viewing Distance** | 50 cm | 300 – 500 cm (6x to 10x further) |
| **Subtended Visual Angle** | Small characters ($11\text{px} - 14\text{px}$) easily resolved | Characters require minimum $24\text{px}$ to subtend $\ge 20'$ arc |
| **Interaction Frequency** | Continuous clicks, keystrokes, dragging | Passive situational awareness; zero local touch inputs |
| **Information Density** | High density (tables, multiple lines of code) | Macro tiles, massive KPI numbers, high-chroma excursion flags |
| **Prose Permitted** | Long paragraphs and descriptions allowed | Strictly zero prose blocks; maximum 3-word status kickers |

---

## 2. Glanceability & Macro-Tile Hierarchy

An operator glancing at an M5 wall screen for two seconds must instantly comprehend:
1. **System Health Status**: Overall facility status (Nominal, Degraded, Critical).
2. **Key Metric Values**: Massive, readable numerical figures with clear engineering units.
3. **Out-of-Spec Flags**: Immediate visual pop for any sub-system threshold violation.

```
+-----------------------------------------------------------------------------------+
|  OVERVIEW STATUS: [ ALL SYSTEMS OPERATIONAL - NOMINAL ORBIT ]                     |
+-------------------------+-------------------------+-------------------------------+
|  PRIMARY TELEMETRY      |  SECONDARY VOLTAGE      |  THERMAL CORE TEMP            |
|                         |                         |                               |
|       420.8             |        12.4             |       304.2                   |
|       KILOWATTS         |        VOLTS            |       KELVIN                  |
|                         |                         |                               |
|  [NOMINAL RATING]       |  [BUS REGULATED]        |  [CHAMBER COOLED]             |
+-------------------------+-------------------------+-------------------------------+
|  FACILITY POWER GRID    |  NETWORK BACKBONE       |  ENVIRONMENTAL AIR            |
|  Status: ACTIVE 100%    |  Packet Loss: 0.00%     |  O2 Partial: 21.2 kPa         |
+-------------------------+-------------------------+-------------------------------+
```

---

## 3. High-Glance Typography & Legibility Invariants

- **Minimum Body Floor (`24px`)**: No text rendered on an M5 screen may drop below 24px (`1.5rem`).
- **KPI Number Scale (`48px – 96px`)**: Primary metrics render in massive tabular numbers (`font-size: clamp(3rem, 6vw, 6rem)`).
- **Prose Exclusion Rule**: Prose paragraphs longer than 15 words are strictly forbidden on M5 ambient kiosks.

---

## 4. Concrete CSS Architecture

```css
@layer quiet.mediums, quiet.wall;

@layer quiet.wall {
  /* M5 Wall Display Root Stage */
  .va-m5-wall {
    inline-size: 100vw;
    block-size: 100vh;
    padding: 3rem;
    background: var(--bg-canvas);
    color: var(--text-primary);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  /* Global Status Banner */
  .va-m5-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-block-end: 2px solid var(--border-strong);
    padding-block-end: 1.5rem;
  }

  .va-m5-banner-title {
    font-size: 2rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Macro Tile Bento Grid */
  .va-m5-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: 1.2fr 0.8fr;
    gap: 2rem;
    flex-grow: 1;
  }

  /* Glanceable Telemetry Tile */
  .va-m5-tile {
    background: var(--bg-card);
    border: 2px solid var(--border-hairline);
    border-radius: var(--radius-card);
    padding: 2.5rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .va-m5-tile-kicker {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .va-m5-tile-val {
    font-size: clamp(3.5rem, 5vw, 6rem);
    font-weight: 800;
    line-height: 1.0;
    font-variant-numeric: tabular-nums slashed-zero;
    color: var(--text-primary);
  }

  .va-m5-tile-unit {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-inline-start: 0.5rem;
  }

  /* Excursion State on Tile */
  .va-m5-tile[data-status="alarm"] {
    border-color: var(--status-danger);
    background: var(--status-err-bg);
  }

  .va-m5-tile[data-status="alarm"] .va-m5-tile-val {
    color: var(--status-danger);
  }
}
```

---

## 5. HTML Macro Implementation

```html
<div class="va-m5-wall" data-theme="dark">
  <!-- Top Global Facility Banner -->
  <header class="va-m5-banner">
    <div class="va-m5-banner-title">
      PROPULSION TEST COMPLEX // GLOBAL OVERVIEW
    </div>
    <div class="va-chip-leaf" style="font-size: 1.25rem; padding: 0.5rem 1.25rem;">
      FACILITY STATUS: NOMINAL
    </div>
  </header>

  <!-- Macro Grid -->
  <main class="va-m5-grid">
    <!-- Macro Tile 1 -->
    <div class="va-m5-tile">
      <span class="va-m5-tile-kicker">TOTAL LOOP POWER</span>
      <div class="va-m5-tile-val">
        420.8<span class="va-m5-tile-unit">kW</span>
      </div>
      <span class="va-chip-leaf">BUS A+B REGULATED</span>
    </div>

    <!-- Macro Tile 2 -->
    <div class="va-m5-tile">
      <span class="va-m5-tile-kicker">CHAMBER PRESSURE</span>
      <div class="va-m5-tile-val">
        101.3<span class="va-m5-tile-unit">kPa</span>
      </div>
      <span class="va-chip-leaf">SEAL STABLE</span>
    </div>

    <!-- Macro Tile 3 -->
    <div class="va-m5-tile">
      <span class="va-m5-tile-kicker">EXHAUST TEMP</span>
      <div class="va-m5-tile-val">
        304.2<span class="va-m5-tile-unit">K</span>
      </div>
      <span class="va-chip-leaf">COOLANT FLOW OK</span>
    </div>
  </main>
</div>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | System Hazard | Quiet UI Resolution |
| :--- | :--- | :--- |
| Text size under 16px on wall displays | Operators cannot read numbers from across the room; walk across floor to squint. | Enforce minimum 24px floor for all labels, 48px+ for metrics. |
| Complex multi-column data tables on wall | Dense text blurs into an indistinguishable grey mass from 4 meters away. | Convert tables into macro KPI tiles with large numbers and units. |
| Narrative prose blocks on status boards | Diverts cognitive attention from critical alarms; impossible to parse quickly. | Replace prose with succinct 2-to-3 word status kickers. |
| Fine 0.5px hairline borders on 4K wall panel | Thin borders vanish optically at 4-meter viewing distance. | Use minimum 2px solid border lines (`border: 2px solid ...`). |
| Interactive scrollbars or hover dropdowns | Wall displays lack mouse input; users cannot access hidden content. | Design 100% passive, static-viewport layouts without scrolling. |
