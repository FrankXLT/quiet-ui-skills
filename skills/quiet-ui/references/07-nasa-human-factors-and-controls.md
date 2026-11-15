# Reference 07: NASA Human-Factors Engineering & High-Consequence Controls

Adheres to **NASA-STD-3001 Volume 2 Revision C** (Human Factors, Habitability, and Environmental Health) and the **Human Integration Design Handbook (HIDH, NASA/SP-2010-3407)** for complex operational environments across Tiers `09. App-2` through `16. Ctrl-1`.

---

## 1. NASA-STD-3001 Human-Factors Principles

### 1.1 Visual Separation: Passive Telemetry vs. Active Effectors
Operators must instantaneously distinguish passive sensor readouts from interactive control effectors without trial-and-error hovering:
- **Passive Telemetry:** Flat containers, muted labels (`--text-muted`), tabular numerals (`--font-nums`), and non-interactive status glyphs. Telemetry elements must never present raised button borders, hover states, or affordances that mimic clickable controls.
- **Active Effectors:** Raised or distinct boundaries (`border: 1px solid var(--border-strong)`), clear affordance labels, action verbs, and active focus rings. Every interactive actuator must explicitly indicate its actionable state.

### 1.2 Commanded-vs-Actual (`CMD` / `ACT`) State Feedback
In high-consequence operations, issuing a command does not guarantee execution. Interfaces must never assume an effector reached its commanded state:
- **Dual-State Annunciation:** Always display both Commanded (`CMD`) and Actual (`ACT`) states when latency, mechanics, or transit times exist (e.g., valve positions, thruster gimbal angles, heater relays).
- **Discrepancy Highlighting:** When `CMD !== ACT` beyond acceptable transit tolerance, apply `--status-warn` highlight and transit indicator dots until hardware confirmation is received.

### 1.3 Two-Step Guarded Actuation (`ARM` $\rightarrow$ `EXECUTE`)
Accidental activation of irreversible, safety-critical, or high-impact effectors must be mechanically or digitally prevented:
- **Two-Action Sequence:** Destructive, high-energy, or abort-level actions require deliberate two-stage actuation:
  1. **ARM:** Operator disengages protective interlock (e.g., toggle switch, slide-guard, or distinct `ARM` trigger). State changes to armed with visible amber warning indicator.
  2. **EXECUTE:** Dedicated actuation button illuminates. Execution fires only upon a distinct second confirmation click.
- **Auto-Disarm Timeout:** If the second confirmation click is not received within a calibrated safety window (e.g., 5 seconds), the control automatically disarms and reverts to safe neutral.

### 1.4 Dark & Quiet Cockpit Philosophy (Nominal Neutrality)
Avoid visual noise and operator fatigue by maintaining nominal neutrality:
- **Nominal Operations are Quiet:** Normal, expected conditions remain neutral in ink and contrast. Green and neutral tones indicate nominal steady-state without demanding attention.
- **Chromatically Silent:** Saturated warning colors (`amber`, `rose`/`red`) are strictly forbidden during nominal operations. Saturated ink is reserved exclusively for unacknowledged faults, threshold excursions, and immediate operator interventions.
- **Auditory & Visual Silence:** No flashing, pulsing, or high-contrast strobe effects on non-critical status items.

### 1.5 Explicit Data Freshness & `STALE` Indicators
Telemetry without verified timestamp freshness is untrustworthy:
- **Stale Telemetry Flagging:** When sensor packet heartbeats exceed the maximum expected sample interval, telemetry fields must visibly display a `STALE` badge and drop text opacity.
- **Never Freeze Silently:** Do not retain static values without an active freshness indicator or countdown watchdog.

### 1.6 Information Architecture & Navigation Depth Limit
Human performance degrades under stress when navigation hierarchies are deep:
- **`<= 4`-Step Navigation Depth:** An operator must reach any safety-critical command, emergency shutdown, or subsystem diagnostic within at most **4 navigational interactions** (clicks or taps) from the top-level operational console.
- **Persistent Abort / Safety Access:** Emergency safing controls and master alarm acknowledgements remain globally accessible across all views.

---

## 2. Implementation Code Patterns & Token Bindings

### 2.1 Commanded vs. Actual Discrepancy Component
```html
<div class="cmd-act-pair" role="group" aria-label="Valves V-101 Command Feedback">
  <div class="pair-cell">
    <span class="pair-label">CMD</span>
    <span class="pair-val">OPEN</span>
  </div>
  <div class="pair-divider">/</div>
  <div class="pair-cell is-discrepant">
    <span class="pair-label">ACT</span>
    <span class="pair-val">TRANSIT</span>
    <span class="va-transit-pulse" title="Hardware moving to target state"></span>
  </div>
</div>
```

### 2.2 Guarded Actuator State Machine (HTML & CSS)
```html
<div class="va-guarded-effector" data-state="armed">
  <div class="effector-header">
    <span class="effector-subsystem">PROPULSION // TANK 1</span>
    <strong class="effector-title">MAIN PYRO ISOLATION VALVE</strong>
  </div>
  <div class="effector-controls">
    <button class="va-pill-btn arm-toggle is-active" aria-pressed="true">
      <i class="fa-solid fa-lock-open"></i> ARMED (04s)
    </button>
    <button class="va-pill-btn execute-action is-ready" aria-label="Confirm Execution">
      FIRE ACTUATOR
    </button>
  </div>
</div>
```

```css
.va-guarded-effector {
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-card, 8px);
  padding: 1rem;
  background: var(--bg-surface);
}

.va-guarded-effector[data-state="armed"] {
  border-color: var(--status-warn);
  box-shadow: 0 0 0 1px var(--status-warn);
}

.execute-action.is-ready {
  background: var(--status-warn);
  color: #000000;
  font-weight: 700;
  cursor: pointer;
}
```

### 2.3 Stale Telemetry Indicator Badge
```html
<div class="telemetry-cell is-stale">
  <div class="cell-label-row">
    <span>O2 PARTIAL PRESSURE</span>
    <span class="va-stale-badge" title="No packet received for > 3000ms">STALE</span>
  </div>
  <div class="cell-num-row">
    <span class="telemetry-num">21.2 kPa</span>
    <span class="telemetry-age">3.8s ago</span>
  </div>
</div>
```

```css
.telemetry-cell.is-stale .telemetry-num {
  opacity: 0.45;
  color: var(--text-muted);
}

.va-stale-badge {
  font-family: var(--font-mono);
  font-size: var(--ts-xs, 11px);
  padding: 1px 4px;
  background: var(--tint-amber-bg);
  color: var(--status-warn);
  border: 1px solid var(--status-warn);
  border-radius: 3px;
}
```

### 2.4 Master Alarm Annunciator Matrix & Acknowledgment Protocol
```html
<section class="va-annunciator-strip" aria-label="Master Subsystem Annunciators">
  <div class="annunciator-cell is-warning" data-alarm="PWR-BATT-02">
    <span class="ann-id">PWR-02</span>
    <span class="ann-text">BATTERY BUS 2 BROWNOUT</span>
    <button class="ann-ack-btn" onclick="acknowledgeAlarm('PWR-BATT-02')">ACK</button>
  </div>
  <div class="annunciator-cell is-nominal">
    <span class="ann-id">ECLSS-01</span>
    <span class="ann-text">CABIN PRESSURE NOMINAL</span>
  </div>
  <div class="annunciator-cell is-nominal">
    <span class="ann-id">TCS-LOOP</span>
    <span class="ann-text">GLYCOL RADIATOR LOOP A OK</span>
  </div>
</section>
```

```css
.va-annunciator-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--border-grid);
  border: 1px solid var(--border-strong);
  margin-bottom: 1rem;
}

.annunciator-cell {
  background: var(--bg-surface);
  padding: 0.65rem 0.85rem;
  font-family: var(--font-mono);
  font-size: var(--ts-xs, 11px);
}

.annunciator-cell.is-warning {
  background: var(--tint-amber-bg);
  color: var(--status-warn);
  border-left: 3px solid var(--status-warn);
}
```

---

## 3. Verification & Audit Checklist for NASA-STD-3001 Controls
- [ ] Passive telemetry cards present zero button affordances or hover elevations.
- [ ] All high-consequence actuators require 2-step `ARM` $\rightarrow$ `EXECUTE` confirmation.
- [ ] Disarm timeout safely resets armed effectors to neutral after 5 seconds.
- [ ] Dual Commanded and Actual states are explicitly indicated with discrepancy highlights.
- [ ] Nominal telemetry displays zero saturated warning colors (Quiet Cockpit invariant).
- [ ] Dropped sensor heartbeats trigger visible `STALE` indicators and dimmed readouts.
- [ ] Touch targets on tactile consoles meet or exceed 44×44px under coarse pointer conditions.
- [ ] All emergency controls are reachable in `<= 4` navigational steps.
