# Tiers 07 to 09: Viewport-Locked Briefing Stage, High-Density Data Table & Live Metrics Console

## 07. Tier `Deck-1`: Viewport-Locked Briefing Stage (`60%` Box Weight, Default `S1` White, `N1`)
- **Hard Viewport Lock:** `display: grid; grid-template-columns: minmax(0, 1fr); grid-template-rows: auto minmax(0, 1fr) auto; width: 100%; max-width: 100%; height: 100dvh; overflow: hidden;`
- **Row 1 (`48px` Header):** Slide/step counter badge (`SLIDE 01 / 04 • STEP 1/3`, `--ts-xs: 11px`) + full-sentence quantitative **Assertion Headline** in `var(--font-sans)` (`--ts-display: clamp(24px, 2.5vw, 28px)`).
- **Row 2 (`400px` Left Stepper | `1fr` Right 3-Band Visual Stage):**
  - Left Pane: 3 vertical `.deck-step-card` blocks (`opacity: 0.38` when inactive, `1.0` with `3px` left accent bar when active). Clicking any step card or `[Next Step / Slide →]` advances `step 0 -> 1 -> 2` before advancing slides.
  - Right Stage: Full-height flex column (`justify-content: space-between`) with (Band 1) 4-cell `1px` hairline metric readout strip, (Band 2) `flex: 1` interactive SVG plot, and (Band 3) bottom parameter control bar with live `<input type="range">` sliders.

---

## 08. Tier `Bridge-2`: High-Density Data Table & Fleet Grid (`1px` Grid) (`100% 1px Grid`, Default `S1` White, `N2`)

This is the canonical tabular engineering and container-fleet console (`t5-console`) bridging documents and dashboards. It pairs `1px` hairline matrices (`--ts-sm: 12.5px` cells, `--ts-xs: 11px` headers) with **Portainer 3-Zone Fleet Cards (`.va-fleet-card-3zone`)**, a **Scoped Context Box (`.va-scoped-nav-box`)**, and a **Stateful Bulk-Action Table Toolbar (`.va-bulk-action-bar`)**:

~~~html
<div class="t5-console">
  <!-- Top Dense Toolbar + Stateful Bulk-Action Bar (.va-bulk-action-bar) -->
  <div class="t5-panel-hdr">
    <span>ARRAY-01 // HIGH-DENSITY DATA TABLE &amp; FLEET GRID (1PX HAIRLINE MATRIX)</span>
    <div>
      <button class="c-btn" onclick="filterT5Nodes('ALL')">ALL (8)</button>
      <button class="c-btn" onclick="filterT5Nodes('LOCKED')">LOCKED (7)</button>
      <button class="c-btn" onclick="filterT5Nodes('HOLDOVER')">HOLDOVER (1)</button>
    </div>
  </div>

  <!-- 5-Cell High-Data-Ink Strip (gap: 1px over --border-grid; stroke="currentColor" monochrome sparklines) -->
  <div class="t5-grid" style="grid-template-columns: repeat(5, 1fr);">
    <div class="t5-cell">
      <div class="t5-cell-head"><span>ARRAY MEAN JITTER</span><span>SLA &lt; 150ps</span></div>
      <div class="t5-cell-main">
        <strong class="t5-big-num" id="kpi-jitter">81.4 ps</strong>
        <span style="color:var(--status-ok); font-size:var(--ts-xs, 11px);">-68.6 ps vs SLA</span>
      </div>
      <svg width="100%" height="18" viewBox="0 0 120 18" preserveAspectRatio="none">
        <polyline fill="none" stroke="currentColor" stroke-width="1.2" points="0,12 15,10 30,13 45,9 60,11 75,8 90,10 105,7 120,9"/>
      </svg>
    </div>
    <!-- Repeat for remaining 4 cells -->
  </div>

  <!-- Main 2fr / 1fr Split: 28px Compact Node Matrix + Distribution Histogram -->
  <div class="t5-grid" style="grid-template-columns: 2fr 1fr;">
    <div style="background:var(--bg-canvas);">
      <div class="t5-panel-hdr"><span>NODE STATUS MATRIX (28PX COMPACT ROWS)</span><span>POLL: 1000ms</span></div>
      <table class="t5-table" id="t5-node-table">
        <thead>
          <tr><th>Node ID</th><th>State</th><th>Optical Link</th><th class="num">RTT Delay (ns)</th><th class="num">Phase Skew (ps)</th><th>Jitter Budget</th><th class="num">SFP Temp</th></tr>
        </thead>
        <tbody>
          <tr data-state="LOCKED">
            <td><strong>WR-NODE-01</strong></td>
            <td><span class="sq-status sq-ok"></span>LOCKED</td>
            <td>1490/1310 WDM</td>
            <td class="num">41,208.114</td>
            <td class="num">+64.2</td>
            <td><span class="inline-bar-track"><span class="inline-bar-fill" style="width:43%;"></span></span>43%</td>
            <td class="num">42.1 &deg;C</td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- Right Column: Monochrome Distribution Bars + Recent Event Ledger -->
  </div>
</div>
~~~

---

## 09. Tier `App-2`: Live Metrics & Time-Series Console (`100% 1px Grid`, Default `S1` White, `N1`)
- **Strict Ban on Top KPI Cards:** Do not place summary metric cards above the strip charts.
- **3-Column `1px` Hairline Grid (`width: 100%; max-width: 100%; grid-template-columns: 230px minmax(0, 1fr) 280px; gap: 1px; background: var(--border-grid); border-radius: 0 !important;`):**
  1. **Left Column (`230px`):** Compact channel tree with `7px` `.sq-status` squares and live cursor readouts.
  2. **Center Column (`1fr` Hybrid Stack):**
     - **Top Half:** 2 to 3 vertically stacked multi-channel SVG strip charts with thin `1.3px` traces, shaded nominal/abort bands, and a **synchronized vertical crosshair cursor** (`onmousemove`) that scrubs across all channels simultaneously.
     - **Bottom Half:** A docked **`28px`-row Channel Matrix (`table.t5-table`)** + **Proportional Background-Fill Subsystem Ranking Rows (`.va-prop-bar-row`)** under a recessed `[Subsystem | Rail | Node]` switcher (`width: var(--share-pct)`) and **Cumulative Trajectory vs. Historical Baseline Curve (`.va-trajectory-chart`)**.
  3. **Right Column (`280px`):** Register snapshot + **5-Segment Threshold Gauge Bar (`.va-threshold-gauge`)** + automated verification check log.

