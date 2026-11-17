# Quiet UI — Medium M4: Walkup Point-of-Interest (POI) Terminal

Medium M4 governs walkup touch kiosks, factory floor terminals, cleanroom dispatch stations, and public information points. Operators interact while standing without physical keyboards, frequently wearing gloves or under fluctuating overhead warehouse lighting.

---

## 1. Physical Optics & Operational Profile

```
+-------------------------------------------------------------+
|                      M4 OPTICAL PROFILE                     |
|                                                             |
|  Viewing Distance:  40 – 50 cm (Standing operator)          |
|  Display Hardware:  24" – 32" Projected Capacitive Touch    |
|  Ambient Lighting:  Fluctuating overhead fluorescent / LED  |
|  Input Modality:    Direct finger touch (Gloves, parallax)  |
|  Hit Target Floor:  >= 48px x 48px (NASA-STD-3001 Grade)    |
|  Safety Protocol:   Guarded 2-Step Action (ARM -> EXECUTE)  |
+-------------------------------------------------------------+
```

### Optical & Ergonomic Constraints

| Constraint | Value / Standard | Operational Rationale |
| :--- | :--- | :--- |
| **Minimum Touch Target** | $\ge 48\text{px} \times 48\text{px}$ | Accommodates finger pad flattening and parallax on thick cover glass. |
| **Touch Target Separation** | $\ge 12\text{px}$ dead-band space | Prevents adjacent button mis-triggers in vibrating industrial environments. |
| **Primary Typography Floor**| $\ge 16\text{px}$ (`--ts-md` baseline) | Legible from standing oblique angles ($30^\circ - 45^\circ$). |
| **Surface Contrast** | High-contrast `white` or high-contrast `dark` | Rejects overhead specular glare and maintains legibility under 800 lux ambient. |
| **Timeout Guard** | Inactivity reset timer (60s) | Protects sensitive workflows when an operator walks away mid-operation. |

---

## 2. Guarded 2-Step Confirmation Architecture (ARM $\rightarrow$ EXECUTE)

Accidental touches on industrial walkup terminals can cause catastrophic state corruption or physical equipment damage. Quiet UI forbids destructive single-tap triggers:

```
[IDLE STATE]
  │
  ├── User Taps: [ ARM VALVE DISCHARGE ]
  │     │
  │     ▼
[ARMED STATE - 5-Second Countdown Timer]
  │   - Primary button turns high-contrast focal accent.
  │   - Displays flashing confirmation ring.
  │   - Audio chime emits.
  │
  ├── User Taps: [ CONFIRM EXECUTION ] (Within 5s) ──► [STATE MUTATED]
  │
  └── Inactivity Timeout (After 5s) ────────────────► [REVERT TO IDLE]
```

### Touch Safety States

| State | Visual Treatment | Interactive Behavior | Timeout |
| :--- | :--- | :--- | :--- |
| **Idle** | Neutral surface (`var(--bg-elevated)`), muted label | Tapping transitions button to Armed | None |
| **Armed** | High-contrast border (`var(--accent-focal)`), active countdown pulse | Tapping triggers mutation; cancel button enabled | 5.0 seconds auto-revert |
| **Executed** | Emerald confirmation badge (`var(--status-ok)`) | UI locks for 2 seconds to confirm physical feedback | 2.0 seconds auto-transition |

---

## 3. Glare Rejection & High-Contrast Visual Stacking

Walkup kiosk glass surfaces frequently suffer from overhead luminaire reflection:
- **Card Separation**: Never rely on subtle drop shadows (which wash out under glare). Use crisp 1.5px high-contrast borders (`var(--border-strong)`).
- **Surface Elevation**: Step through distinct solid surface levels (`--bg-surface` onto `--bg-shell`) without translucent glass effects.
- **Button Feedback**: Provide instantaneous physical visual depression (`transform: translateY(2px)`) and audible click feedback upon touch down.

---

## 4. Concrete CSS Architecture

```css
@layer quiet.mediums, quiet.terminal;

@layer quiet.terminal {
  /* M4 Kiosk Touch Container */
  .va-m4-kiosk {
    inline-size: 100vw;
    block-size: 100vh;
    padding: 2rem;
    background: var(--bg-canvas);
    color: var(--text-primary);
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
  }

  /* Large Touch Target Button */
  .va-touch-btn {
    min-inline-size: 120px;
    min-block-size: 52px; /* Surpasses 48px floor */
    padding: 0.75rem 1.5rem;
    font-family: var(--font-sans);
    font-size: var(--ts-md);
    font-weight: 700;
    border: 2px solid var(--border-strong);
    border-radius: var(--radius-card);
    background: var(--bg-surface);
    color: var(--text-primary);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    transition: transform 0.05s ease, background-color 0.1s ease;
  }

  .va-touch-btn:active {
    transform: translateY(2px);
    background: var(--bg-elevated);
  }

  /* Guarded Action Two-Step Container */
  .va-guarded-action {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .va-touch-btn[data-state="armed"] {
    background: var(--status-warn-bg);
    border-color: var(--status-warn);
    color: var(--status-warn);
    box-shadow: 0 0 0 3px var(--status-warn);
    animation: va-pulse-armed 1s infinite alternate;
  }

  @keyframes va-pulse-armed {
    from { transform: scale(1); }
    to { transform: scale(1.02); }
  }

  /* Card Grid with High Specular Contrast */
  .va-kiosk-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .va-kiosk-card {
    background: var(--bg-surface);
    border: 2px solid var(--border-strong); /* Strong border for glare rejection */
    border-radius: var(--radius-card);
    padding: 1.5rem;
  }
}
```

---

## 5. HTML Macro Implementation

```html
<div class="va-m4-kiosk" data-theme="white">
  <header class="va-kiosk-header">
    <span class="va-kicker">DISPATCH WORKSTATION // BAY 04</span>
    <h1 style="font-size: var(--ts-xl);">Cryogenic Nitrogen Transfer System</h1>
  </header>

  <main class="va-kiosk-grid" style="margin-block-start: 2rem;">
    <!-- Telemetry Card -->
    <div class="va-kiosk-card">
      <span class="va-kicker">SYSTEM PRESSURE</span>
      <div style="font-size: 2.5rem; font-weight: 700; margin-block: 0.5rem;" class="va-nums">
        4.18 MPa
      </div>
      <span class="va-chip-leaf">NOMINAL FEED</span>
    </div>

    <!-- Guarded Actuation Card -->
    <div class="va-kiosk-card">
      <span class="va-kicker">CRITICAL VALVE ACTUATION</span>
      <p style="margin-block: 0.5rem; color: var(--text-secondary);">
        Initiate line purge. Requires 2-step operator physical confirmation.
      </p>
      
      <div class="va-guarded-action" style="margin-block-start: 1rem;">
        <button type="button" class="va-touch-btn" data-action="arm" data-state="idle">
          ARM PURGE SEQUENCE
        </button>
      </div>
    </div>
  </main>
</div>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | Field Hazard | Quiet UI Resolution |
| :--- | :--- | :--- |
| Sub-44px touch targets on kiosk screens | Operator wearing nitrile gloves mis-taps adjacent control. | Enforce minimum $48\text{px} \times 48\text{px}$ button dimensions. |
| Single-tap confirmation for destructive valve trip | Accidental brush of jacket sleeve initiates emergency vent. | Mandate Guarded 2-Step Confirmation (ARM $\rightarrow$ EXECUTE). |
| Subtle translucent drop shadows under bright lights | Glare from warehouse skylights washes out card boundaries. | Use crisp 2px solid border lines (`var(--border-strong)`). |
| Desktop hover tooltips on touch display | Tooltips never appear on touch devices, hiding critical safety notes. | Make all critical operational instructions permanently visible. |
| Virtual keyboard blocking form inputs | On-screen keyboard covers fields being filled, causing input errors. | Position input cards in the upper 50% of the display with bottom reserve. |
