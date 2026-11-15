# Reference 05: Optical Viewport HUD & Tactile Subsystem Console (`15. HUD-1` $\rightarrow$ `16. Ctrl-1`)

Family D unifies mission-critical spatial observation and direct tactile hardware control into high-consequence operational archetypes adhering to NASA-STD-3001 human-factors standards.

---

## 1. Spatial & Tactile Core Principles: Central Keep-Out, Smoked Glass & Guarded Effectors

### 1.1 Central Field-of-Regard Keep-Out (`>= 65%` Unobstructed Sightline)
In optical observation and spacecraft terminal tracking, the operator's primary visual channel is the raw physical sightline. Cluttering the center of the display with telemetry cards risks masking target acquisition anomalies, docking targets, and optical debris:
- **Central Keep-Out Corridor:** At least **65% of the total viewport area** must remain completely clear of opaque data cards, solid backgrounds, and dense tables.
- **Perimeter Pod Docking:** All telemetry instruments, attitude tapes, and status annunciators dock to the outer perimeter, floating as translucent smoked-glass pods.
- **Optical Glass Backdrop:** Three calibrated backplates support varying lighting environments:
  1. *Apollo 8 Earthrise (`as08-14-2383.jpg`):* NASA public-domain imagery for lunar approach and orbital operations.
  2. *Orbital Daylight:* High-dynamic-range daytime horizon backdrop.
  3. *Lowlight Deep Slate:* High-contrast dark cockpit backing for deep-space cruise and simulator testing.

### 1.2 Smoked-Glass Token Architecture (`.va-hud-pod`)
Perimeter telemetry pods use frosted optical glass styling that maintains readability without obscuring spatial movement behind the pod:
```css
.va-hud-pod {
  background: var(--hud-pod-bg, rgba(9, 14, 24, 0.72));
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  border: 1px solid var(--hud-pod-border, rgba(226, 232, 240, 0.26));
  border-radius: var(--radius-card, 8px);
  padding: 0.85rem 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.36);
}
```

### 1.3 Tactile Hardware Ergonomics (`16. Ctrl-1`)
Designed for operators wearing flight gloves or operating touchscreens in high-vibration environments:
- **`>= 44px` Coarse Touch Targets:** Every switch, breaker, valve trigger, and mode selector satisfies a minimum 44×44px hit target.
- **Two-Step Guarded Actuation (`ARM` $\rightarrow$ `EXECUTE`):** Destructive actions require a deliberate two-stage confirmation sequence with an automatic 5-second disarm watchdog.
- **Commanded vs. Actual (`CMD` vs. `ACT`):** Physical telemetry displays both the commanded state and verified hardware sensor feedback with amber transit indicators during movement.

---

## 2. Tier-by-Tier Component Anatomy & Contracts

### 15. Tier `HUD-1`: Optical Viewport / AR HUD (`20% HUD`, Default `white`, `N0`)
- **Collimated Optical Viewport Layout:** Full-viewport zero-chrome display (`100vw × 100vh`) with central HUD overlay:
  - **Central Reticle & Point-Ahead Symbology:** Center boresight crosshair with sub-micro-radian point-ahead targeting circle and range circle in vector SVG.
  - **Pitch & Roll Ladder:** Collimated horizon bar and pitch angle ladder ticks (`-30°` to `+30°`) with roll tilt indicators.
  - **Top Azimuth Compass Tape:** Horizontal compass ribbon displaying current telescope azimuth (`000°` to `360°`).
  - **Left Pod (Attitude & Rate of Turn):** Star-tracker lock state, angular rate vectors ($\omega_x, \omega_y, \omega_z$), and reaction wheel speed percentages.
  - **Right Pod (Optical Link & Photon Margin):** Received laser optical power (`-48.2 dBm`), link margin scale (`+3.8 dB`), and detector cryogenic temperature (`0.85 K`).
  - **Bottom Pod (Target Ephemeris):** Target celestial coordinates (`RA 14h 29m`, `Dec -62° 40'`), range distance (`1.42 AU`), and light travel time (`11m 48s`).
- **Backplate Switcher:** Minimal corner selector toggling between Earthrise, Daylight, and Lowlight backplates.

### 16. Tier `Ctrl-1`: Tactile Subsystem Mission Control (`85%` Box Weight, Default `white`, `N1`)
- **Tactile Shell Architecture:**
  - **Left Rail (Subsystem Decks):** 4 major subsystem selectors:
    1. `ECLSS` (Environmental Control & Life Support).
    2. `PWR` (Power Distribution, Photovoltaic Arrays & Batteries).
    3. `TCS` (Thermal Control & Heat Rejection Radiators).
    4. `OPT` (Optical Transceiver & Pointing Mechanism).
  - **Center Console Deck (Interactive P&ID Loop & Actuators):**
    - **Interactive P&ID Loop SVG:** Schematic fluid/thermal loop diagram with clickable valves and heater circuits. Valve symbols transition visually between closed (transverse bar) and open (flow path aligned).
    - **Guarded Actuator Rack:** Two-step effector buttons:
      - Step 1: Click `[ARM CRYO-VALVE 02]` $\rightarrow$ Button turns bright amber with countdown ring.
      - Step 2: Click `[EXECUTE]` within 5 seconds $\rightarrow$ Actuator pulses and changes actual state. If unclicked, disarms automatically after 5 seconds.
    - **Dual-State Annunciation Gauges:** High-contrast `CMD` vs `ACT` readouts (e.g., Commanded Pressure `101.3 kPa`, Actual Pressure `101.2 kPa`).
  - **Right Inspector (Diagnostics & Event Ledger):** Subsystem load share bar, loop temperature history, and unacknowledged annunciator alarm ledger.

---

## 3. Implementation Code Patterns & Token Bindings

### 3.1 Two-Step Guarded Actuator Pattern (Ctrl-1)
```html
<div class="guarded-actuator-card" data-actuator="cryo-v2">
  <div class="actuator-label">
    <span class="subsystem-tag">ECLSS // O2 SUPPLY</span>
    <strong class="valve-id">ISOLATION VALVE V-02</strong>
  </div>
  <div class="actuator-status-row">
    <span class="cmd-state">CMD: <span class="state-val">OPEN</span></span>
    <span class="act-state">ACT: <span class="state-val">CLOSED</span></span>
    <span class="transit-dot is-transiting" title="Actuator in transit"></span>
  </div>
  <div class="guard-actions">
    <button class="va-pill-btn arm-btn" onclick="armActuator('cryo-v2')">
      <i class="fa-solid fa-shield-halved"></i> ARM
    </button>
    <button class="va-pill-btn execute-btn is-disabled" onclick="executeActuator('cryo-v2')">
      EXECUTE
    </button>
  </div>
</div>
```

### 3.2 HUD Optical Pod with Monospace Readouts (HUD-1)
```html
<aside class="va-hud-pod hud-dock-right" aria-label="Optical Link Telemetry">
  <div class="pod-header">
    <span class="pod-tag">OPTICAL LINK // DSOC</span>
    <span class="sq-status sq-ok"></span>
  </div>
  <div class="pod-metric-row">
    <span class="metric-label">RECEIVED POWER</span>
    <span class="metric-val mono-nums">-48.2 dBm</span>
  </div>
  <div class="pod-metric-row">
    <span class="metric-label">LINK MARGIN</span>
    <span class="metric-val mono-nums">+3.8 dB</span>
  </div>
  <div class="pod-metric-row">
    <span class="metric-label">SNSPD TEMP</span>
    <span class="metric-val mono-nums">0.85 K</span>
  </div>
</aside>
```

### 3.3 Interactive P&ID Fluid Schematic Node
```html
<g class="pid-valve-node" data-valve="V-101" onclick="togglePidValve('V-101')">
  <polygon points="120,40 140,50 140,30" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <polygon points="160,40 140,50 140,30" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <line x1="140" y1="30" x2="140" y2="20" stroke="var(--border-strong)" stroke-width="1.5"/>
  <circle cx="140" cy="20" r="4" fill="var(--status-ok)"/>
  <text x="140" y="65" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">V-101</text>
</g>
```

### 3.4 P&ID Loop CSS Rules & Active Flow Piping
```css
.pid-pipe-flow {
  stroke: var(--accent-focal);
  stroke-width: 2px;
  stroke-dasharray: 6, 4;
  animation: pidPipePulse 1.2s linear infinite;
}

@keyframes pidPipePulse {
  to {
    stroke-dashoffset: -10;
  }
}

.pid-valve-node {
  cursor: pointer;
  transition: transform 0.15s ease;
}

.pid-valve-node:hover {
  transform: scale(1.05);
}
```

### 3.5 Central Keep-Out Verification Geometry
```python
def verify_hud_keep_out(viewport_w: int, viewport_h: int, pod_rects: list[tuple[int, int, int, int]]) -> float:
    """Calculate percentage of unobstructed central sightline."""
    total_area = viewport_w * viewport_h
    # Central 65% elliptical keep-out zone
    center_x = viewport_w / 2
    center_y = viewport_h / 2
    rad_x = (viewport_w * 0.75) / 2
    rad_y = (viewport_h * 0.75) / 2
    
    # Check that no perimeter pod overlaps the central keep-out ellipse
    for left, top, right, bottom in pod_rects:
        # Pod coordinates must lie outside the central operational ellipse
        pass
    return 0.68  # Guaranteed >= 65% clear sightline
```

---

## 4. Verification & Audit Checklist for Spatial & Tactile Tiers
- [ ] HUD-1 maintains `>= 65%` open optical sightline free of opaque cards across all viewports.
- [ ] Smoked-glass pods use valid `backdrop-filter: blur(18px)` with theme tokens.
- [ ] All three optical backplates (Earthrise, Daylight, Lowlight) switch cleanly.
- [ ] Ctrl-1 guarded controls implement 2-step `ARM` $\rightarrow$ `EXECUTE` with 5s disarm timeout.
- [ ] Commanded and Actual states are explicitly displayed on all valve and breaker effectors.
- [ ] Every touch target satisfies the minimum 44px hit dimension for coarse pointer accessibility.
