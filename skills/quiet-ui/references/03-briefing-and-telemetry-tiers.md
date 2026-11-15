# Reference 03: Viewport-Locked Briefing Stage, High-Density Fleet Grid & HIL Console (`07. Deck-1` $\rightarrow$ `09. App-2`)

Quiet UI Briefing and Telemetry tiers present high-density quantitative instruments, live hardware-in-the-loop (HIL) telemetry, and viewport-locked executive briefings. They adhere to strict information-density budgets, dark/quiet cockpit principles, and non-negotiable typography floors—ensuring high situational awareness without operator cognitive overload.

---

## 1. Quantitative Core Principles: High Data-Ink, Synchronized Cursors & Monospace Telemetry

### 1.1 High Data-Ink Ratio & Zero Fluff
- **Zero Decorative Ornaments:** Every pixel in telemetry tiers conveys functional signal. Drop shadows, glossy gradients, decorative card halos, and arbitrary floating cards are strictly eliminated in favor of continuous `1px` hairlines (`var(--border-grid)`).
- **Tabular Numerals & Monospace Alignment:** All numeric telemetry readouts, timestamps, register offsets, and frequencies enforce `font-family: var(--font-mono)` with `font-variant-numeric: tabular-nums` to guarantee jitter-free vertical alignment during live stream refreshes.
- **The `11px` Typography Floor (`--ts-xs`):** Sub-11px labels are unreadable on mobile viewports and high-DPI displays. Every axis tick, tag, port label, and threshold marker enforces `font-size: var(--ts-xs, 11px)` or greater.

### 1.2 Layout Topologies: Zero-Scroll Deck vs. 1px Telemetry Grids
- **Deck-1 (100dvh Zero-Scroll):** Designed for executive briefings, mission readiness reviews (FRR/PDR), and board presentations. Enforces a rigid 16:9 aspect ratio contained within `100dvh` with zero page scrolling.
- **Bridge-2 & App-2 (100% 1px Grid):** Replaces card clutter with continuous grid walls. Adjacent panels share exact `1px` dividers without double-border escalation:
```css
.t5-console {
  display: grid;
  grid-template-columns: 230px minmax(0, 1fr) 280px;
  gap: 1px;
  background: var(--border-grid);
  border: 1px solid var(--border-strong);
}
```

---

## 2. Tier-by-Tier Component Anatomy & Contracts

### 07. Tier `Deck-1`: Viewport-Locked Briefing Stage (`60%` Box Weight, Default `white`, `N1`)
- **100dvh 16:9 Zero-Scroll Stage:** `display: grid; grid-template-columns: minmax(0, 1fr); grid-template-rows: auto minmax(0, 1fr) auto; width: 100%; height: 100dvh; overflow: hidden;`
- **Row 1 (`48px` Header):**
  - Left: Slide counter badge (`SLIDE 01 / 04 · STEP 1/3`, `--ts-xs: 11px`, `--font-mono`).
  - Center: Full-sentence quantitative **Assertion Headline** in `--font-sans` (`--ts-display: 22px`, weight 600) stating the empirical takeaway (e.g., *"DSOC link margin sustains 3.4 dB at 2.6 AU across Palomar 5.1m aperture"*).
  - Right: Viewport mode switcher (`16:9 HD` / `Kiosk Fullscreen`).
- **Row 2 (`400px` Stepper Left | `1fr` 3-Band Stage Right):**
  - **Left Pane (3-Step Narrative Card Rail):** Three vertical `.deck-step-card` blocks. Inactive cards sit at `opacity: 0.38`; the active card renders at `opacity: 1.0` with a `3px` solid accent bar (`var(--accent-focal)`). Each card provides a step thesis and empirical bullet points. Clicking any card activates that narrative step.
  - **Right Stage (3-Band Evidence Column):**
    - **Band 1 (4-Cell Metric Strip):** 4-cell hairline metric strip showing primary parameters with status badges.
    - **Band 2 (Interactive Evidence Plot):** Scaled vector SVG chart or architecture diagram with unit-labeled axes and collision-free callout labels.
    - **Band 3 (Parameter Sensitivity Controls):** Interactive `<input type="range">` sliders allowing real-time sensitivity exploration during the briefing.
- **Row 3 (`44px` Footer Toolbar):** Slide navigation buttons (`[← Prev]`, `[Next Step / Slide →]`), slide index pills (`01`, `02`, `03`, `04`), and speaker notes toggle.
- **4 Distinct Mission Slides:**
  1. *Slide 1 — Interplanetary Optical Link Margin:* Evaluates received signal power vs. quantum noise limit across Mars opposition distances.
  2. *Slide 2 — Palomar Hale 5.1m Coupling:* Ground station optical wavefront sensor coupling and cryogenic SNSPD photon counting efficiency.
  3. *Slide 3 — Flight Terminal Beam Point-Ahead:* Sub-micro-radian point-ahead angle calibration accounting for relativistic aberration.
  4. *Slide 4 — Ground Segment Verification & Flight Readiness:* 12-aperture DSN arraying schedule, atmospheric turbulence budget, and launch go/no-go criteria.

### 08. Tier `Bridge-2`: High-Density Data Table & Fleet Grid (`100% 1px Grid`, Default `white`, `N2`)
- **Header Toolbar & Filter Strip:** Single command row featuring title `ARRAY-01 // DEEP SPACE NETWORK APERTURE FLEET`, status pill filters (`ALL (12)`, `LOCKED (9)`, `TRACKING (2)`, `CALIBRATING (1)`), and refresh cadence indicator (`POLL: 1000ms`).
- **6-Cell High-Data-Ink KPI Strip (`.t5-grid`):**
  - `ARRAY MEAN JITTER` (nominal `81.4 ps`, SLA `< 150 ps`, sparkline trend).
  - `CARRIER LOCK SNR` (nominal `24.6 dB`, sparkline trend).
  - `AZ/EL TRACKING SKEW` (nominal `+12.4 nrad`, sparkline trend).
  - `BIT ERROR RATE` (nominal `1.2e-7`, sparkline trend).
  - `CRYOGENIC SNSPD TEMP` (nominal `0.85 K`, sparkline trend).
  - `DATA BUFFER FILL` (nominal `42.8%`, sparkline trend).
- **Main 2fr / 1fr Split:**
  - **Left 2fr (12-Aperture Fleet Matrix):** Compact 28px-row data table (`table.t5-table`) covering all 12 canonical DSN apertures:
    - Goldstone (GDSCC): `DSS-24 34m BWG`, `DSS-26 34m BWG`, `DSS-14 70m`, `DSS-13 Hybrid Opt`.
    - Madrid (MDSCC): `DSS-54 34m BWG`, `DSS-55 34m BWG`, `DSS-56 34m BWG`, `DSS-63 70m`.
    - Canberra (CDSCC): `DSS-34 34m BWG`, `DSS-35 34m BWG`, `DSS-36 34m BWG`, `DSS-43 70m`.
    - Columns: Aperture ID, Subsystem State (`.sq-status`), Downlink Freq, RTT Delay (ms), Phase Skew (ps), Jitter Budget Bar (`.inline-bar-track`), Cryo Temp.
  - **Right 1fr (Distribution Histogram & Event Log):**
    - Phase Skew Distribution Histogram (`-100 ps` to `+100 ps` distribution bins in vector SVG).
    - Live Chronological Audit Log (`.t5-log-box`) with timestamped carrier acquisition and frame synchronizer events.

### 09. Tier `App-2`: Live Metrics & HIL Console (`100% 1px Grid`, Default `white`, `N1`)
- **Strict Architectural Invariant:** Summary KPI cards must NEVER be placed above real-time strip charts. Real-time waveforms demand immediate visual prominence at the top of the canvas.
- **Three-Column Full-Height Shell:**
  - **Left Column (`230px` Channel Inspector):**
    - Channel selector tree (`CH-01 Carrier Phase`, `CH-02 Symbol Timing`, `CH-03 Laser Divergence`, `CH-04 Photodiode Bias`).
    - Live cursor readout coordinates (`t = 142.80s`, `y = 1.042 V`).
    - Channel gain and coupling controls (`AC`, `DC`, `50Ω`).
  - **Center Column (`1fr` Live Waveform & Analytical Stack):**
    - **Top Half (4 Synchronized Waveform Strips):** 4 synchronized SVG strip charts (`CH-01` through `CH-04`). Traces render with thin `1.3px` hairline strokes over shaded nominal bands. Synchronized vertical crosshair scrubs across all 4 channels on mouse hover.
    - **Crisp HTML Threshold Overlay Pills:** Upper and lower threshold bounds render as crisp `11px` monospace HTML overlay pills docked to strip chart edges (never stretched or blurred SVG `<text>`).
    - **Bottom Half (Channel Matrix & Share Breakdown):** Docked 28px-row matrix + proportional share bars (`.va-prop-bar-row`) detailing packet error distribution across SCPPM orders ($M=4, 8, 16, 32, 64, 128$).
  - **Right Column (`280px` Hardware Inspector):**
    - PCIe BAR0 Register Hex Dump (`0x0000: 44 53 4F 43 01 00 ...`).
    - 5-Segment Threshold Gauge (`.va-threshold-gauge`) indicating instantaneous optical power margin.
    - Automated HIL Verification Log with pass/warn/fail telemetry assert statements.

---

## 3. Implementation Code Patterns & Token Bindings

### 3.1 Synchronized Strip Chart Waveform with HTML Threshold Pill
```html
<div class="hil-strip-card" style="position: relative; border-bottom: 1px solid var(--border-grid);">
  <div class="hil-strip-header">
    <span class="ch-tag">CH-01 // CARRIER PHASE SYNTONIZATION</span>
    <span class="ch-readout" id="ch1-readout">81.4 ps RMS</span>
  </div>
  <!-- Crisp HTML Threshold Overlay Pill -->
  <span class="va-threshold-pill" style="position: absolute; right: 8px; top: 32px;">
    UPPER LIMIT: 120.0 ps
  </span>
  <svg class="hil-waveform-svg" width="100%" height="90" viewBox="0 0 600 90" preserveAspectRatio="xMidYMid meet">
    <!-- Shaded Nominal Corridor -->
    <rect x="0" y="20" width="600" height="50" fill="var(--tint-emerald-bg)" opacity="0.35"/>
    <line x1="0" y1="45" x2="600" y2="45" stroke="var(--border-hairline)" stroke-dasharray="3,3"/>
    <!-- Signal Waveform Trace -->
    <polyline fill="none" stroke="var(--accent-focal)" stroke-width="1.3" points="0,48 50,42 100,50 150,41 200,44 250,46 300,43 350,49 400,40 450,44 500,46 550,42 600,45"/>
    <!-- Interactive Synchronized Cursor -->
    <line class="hil-cursor-line" x1="300" y1="0" x2="300" y2="90" stroke="var(--text-primary)" stroke-width="1" stroke-dasharray="2,2"/>
  </svg>
</div>
```

### 3.2 Deck-1 Slide Stepper Card Interaction
```html
<div class="deck-step-card is-active" data-step="0" onclick="selectDeckStep(0)">
  <div class="step-badge">STEP 01 / 03</div>
  <h4 class="step-title">Atmospheric Channel Characterization</h4>
  <p class="step-desc">Palomar optical ground station measures Fried parameter r0 >= 8.5 cm under clear sky conditions.</p>
</div>
```

### 3.3 High-Density Tabular Row & Inline Budget Bar (Bridge-2)
```html
<table class="t5-table" id="t5-aperture-table">
  <thead>
    <tr>
      <th>Aperture ID</th>
      <th>Status</th>
      <th>Downlink Band</th>
      <th class="num">RTT Delay (ms)</th>
      <th class="num">Phase Skew (ps)</th>
      <th>Jitter Budget</th>
      <th class="num">Cryo Temp</th>
    </tr>
  </thead>
  <tbody>
    <tr data-complex="GDSCC" data-state="LOCKED">
      <td><strong>DSS-24</strong> 34m BWG</td>
      <td><span class="sq-status sq-ok"></span>LOCKED</td>
      <td>1550nm Laser</td>
      <td class="num">2,842.18</td>
      <td class="num">+14.2</td>
      <td>
        <div class="inline-bar-track">
          <div class="inline-bar-fill" style="width: 28%; background: var(--status-ok);"></div>
        </div>
      </td>
      <td class="num">0.82 K</td>
    </tr>
  </tbody>
</table>
```

### 3.4 PCIe BAR0 Register Hex Dump & Threshold Gauge (App-2)
```html
<div class="bar0-dump-panel">
  <div class="t5-panel-hdr"><span>PCIe BAR0 MMIO REGISTERS</span><span>OFFSET 0x0000</span></div>
  <pre class="bar0-hex-stream">
0x0000: 44 53 4F 43 01 00 00 00  // IDENT: DSOC_DEV_01
0x0008: 00 00 02 67 00 00 04 28  // BITRATE: 267.0 Mbps
0x0010: 00 00 00 06 00 00 00 01  // SCPPM_M: 64, LOCKED
0x0018: 00 00 1F 40 00 00 00 55  // LASER_PWR: 1250 mW
  </pre>
</div>

<div class="va-threshold-gauge" role="meter" aria-valuenow="78" aria-valuemin="0" aria-valuemax="100">
  <div class="gauge-segment is-active" style="background: var(--tint-indigo-bg); border-color: var(--accent-focal);"></div>
  <div class="gauge-segment is-active" style="background: var(--tint-indigo-bg); border-color: var(--accent-focal);"></div>
  <div class="gauge-segment is-active" style="background: var(--tint-emerald-bg); border-color: var(--status-ok);"></div>
  <div class="gauge-segment is-active" style="background: var(--tint-emerald-bg); border-color: var(--status-ok);"></div>
  <div class="gauge-segment" style="background: var(--bg-surface); border-color: var(--border-grid);"></div>
</div>
```

---

## 4. Verification & Audit Checklist for Briefing & Telemetry Tiers
- [ ] Deck-1 maintains strict `100dvh` zero-scroll invariant across all viewports.
- [ ] Bridge-2 features all 12 canonical DSN apertures across Goldstone, Madrid, and Canberra.
- [ ] App-2 strip charts contain zero top-level summary cards above live waveforms.
- [ ] Waveform threshold indicators use crisp HTML overlay pills rather than stretched SVG text.
- [ ] Synchronized cursor scrubs smoothly across all 4 channels without DOM layout thrashing.
- [ ] All table rows adhere to compact 28px height with tabular-num monospace alignment.
- [ ] Every SVG diagram maintains valid aspect ratios with zero `preserveAspectRatio="none"`.
