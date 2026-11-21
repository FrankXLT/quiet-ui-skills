# Quiet UI — Medium M3: Stateful Web Application

Medium M3 governs interactive workstations, operations consoles, dual-pane queue dispatchers, hardware-in-the-loop (HIL) telemetry scopes, and developer workbenches. It is optimized for continuous multi-hour keyboard-and-mouse manipulation with dense information display.

---

## 1. Physical Optics & Operational Profile

```
+-------------------------------------------------------------+
|                      M3 OPTICAL PROFILE                     |
|                                                             |
|  Viewing Distance:  45 – 65 cm (Desktop / Laptop Workstation)|
|  Display Hardware:  1080p, 1440p, QHD, 4K Multi-Monitor Arrays|
|  Interactive Modality: Keyboard shortcuts, low-latency mouse |
|  Density Target:    High Information Density (D2 Default / D3)|
|  Primary Shell:     N1 (Persistent Rail) or N3 (Composite)   |
|  Focus Mode:        Active state mutation, real-time streams |
+-------------------------------------------------------------+
```

### Operational Characteristics

| Attribute | Specification | Ergonomic Justification |
| :--- | :--- | :--- |
| **Shell Archetype** | N1 (Left Rail) or N3 (Composite Header + Rail) | Guarantees instant access to multi-module workspaces without context loss. |
| **Density Setting** | `[data-density="d2"]` (Default) or `[data-density="d3"]` | Maximizes visible rows and parameters without causing mis-clicks. |
| **Stage Constraint** | `max-inline-size: var(--stage-workspace-max, 96rem)` | Prevents excessive ocular traversal across ultra-wide monitors. |
| **Surface Palette** | `[data-theme="white"]` or `[data-theme="dark"]` | High-contrast clarity for dense tabular and graphical inspection. |
| **Tabular Numbers** | Mandatory `font-variant-numeric: tabular-nums` | Eliminates horizontal layout jitter during real-time telemetry streaming. |

---

## 2. Layout Architecture: Dual-Pane Dispatcher & Collapsible Inspector

The standard M3 workbench is composed of three coordinated functional zones:
1. **Module Rail (`.va-rail`)**: Fixed 240px persistent navigation rail displaying domains, filters, and workspaces.
2. **Master Queue / Dispatcher (`.va-master-pane`)**: High-density interactive list or data table supporting keyboard navigation, batch selection, and live sorting.
3. **Detail Inspector (`.va-detail-pane`)**: Collapsible context panel displaying deep telemetry, hex dumps, and mutation forms.

```
+-----------------------------------------------------------------------------------------+
| Top Bar (Shell N3 Optional): Global Scope / Active Project / User Status                |
+---------+-----------------------------------+-------------------------------------------+
| Nav     | Master Queue Dispatcher           | Detail Inspector / Scope (Collapsible)    |
| Rail    | - Priority Work Queue             | - Live HIL Waveform Stream                |
| (240px) | - Filtering & Facets              | - Hardware Register Inspection            |
|         | - Batch Selection Rows            | - Form Controls & Mutation Triggers       |
|         |                                   |                                           |
| Status  | [ Item 001 | Pending  | 14:02:01 ]| V_IN: 12.04 V       STATUS: NOMINAL       |
| Telemetry| [ Item 002 | Running  | 14:02:04 ]| I_OUT: 1.84 A       FREQ: 400.0 kHz       |
| Config  | [ Item 003 | Queued   | 14:02:10 ]| [ Waveform Canvas: 100 kHz Oscilloscope ] |
+---------+-----------------------------------+-------------------------------------------+
```

---

## 3. Real-Time Telemetry & Hardware Scopes

M3 consoles frequently host high-frequency telemetry streams. To avoid UI thrashing:
- Telemetry readouts must use **CSS custom properties** rather than full React/DOM re-renders for gauge updates.
- Oscilloscope canvases must use `requestAnimationFrame` and offscreen rendering buffers.
- Status indicator dots must use hardware-accelerated transforms (`transform: scale()`), avoiding layout reflows.

---

## 4. Concrete CSS Architecture

```css
@layer quiet.mediums, quiet.workspace, utilities;

@layer quiet.workspace {
  /* M3 Workbench Root Grid */
  .va-m3-workbench {
    display: grid;
    grid-template-columns: 240px minmax(350px, 1fr) minmax(400px, 1.2fr);
    block-size: 100vh;
    overflow: hidden;
    background: var(--bg-canvas);
    color: var(--text-primary);
  }

  /* Persistent Nav Rail */
  .va-m3-rail {
    background: var(--bg-elevated);
    border-inline-end: 1px solid var(--border-hairline);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  /* Master Queue Pane */
  .va-m3-master {
    overflow-y: auto;
    border-inline-end: 1px solid var(--border-hairline);
    background: var(--bg-surface);
  }

  /* Detail & Scope Inspector */
  .va-m3-inspector {
    overflow-y: auto;
    background: var(--bg-surface);
    padding: var(--density-card-pad, 0.9rem);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* Real-time Oscilloscope Canvas Pod */
  .va-m3-scope-pod {
    background: var(--bg-card);
    border: 1px solid var(--border-hairline);
    border-radius: var(--radius-card);
    padding: 0.75rem;
    position: relative;
  }

  .va-m3-scope-canvas {
    inline-size: 100%;
    block-size: 180px;
    background: var(--bg-canvas);
    border-radius: var(--radius-inner);
    border: 1px solid var(--border-hairline);
    display: block;
  }

  /* Keyboard Focus Ring Discipline */
  .va-m3-master [role="row"]:focus-visible,
  .va-m3-inspector input:focus-visible,
  .va-m3-inspector button:focus-visible {
    outline: 2px solid var(--accent-focal);
    outline-offset: -1px;
  }
}

@layer utilities {
  .hidden,
  [hidden]:not([hidden="until-found"]) {
    display: none;
  }
}
```

---

## 5. HTML Macro Implementation

```html
<div class="va-m3-workbench" data-theme="dark" data-density="d2">
  <!-- Nav Rail -->
  <aside class="va-m3-rail">
    <span class="va-kicker">STATION ALPHA</span>
    <nav class="va-rail-links">
      <a href="#queue" class="is-active">Telemetry Dispatch</a>
      <a href="#registers">Register Map</a>
      <a href="#hil">HIL Loop Test</a>
    </nav>
  </aside>

  <!-- Master Queue -->
  <section class="va-m3-master">
    <table class="va-data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Sensor Node</th>
          <th>State</th>
          <th>Latency</th>
        </tr>
      </thead>
      <tbody>
        <tr tabindex="0" class="is-selected">
          <td class="va-nums">0x10A</td>
          <td>Gimbal Rate Gyro</td>
          <td><span class="va-chip-leaf">ARMED</span></td>
          <td class="va-nums">1.2 ms</td>
        </tr>
      </tbody>
    </table>
  </section>

  <!-- Detail Inspector -->
  <main class="va-m3-inspector">
    <header class="va-inspector-header">
      <span class="va-kicker">LIVE INSPECTOR // NODE 0x10A</span>
      <h2>Gimbal Rate Gyroscope Active Telemetry</h2>
    </header>

    <div class="va-m3-scope-pod">
      <span class="va-kicker">OSCILLOSCOPE: ANGULAR VELOCITY (RAD/S)</span>
      <canvas class="va-m3-scope-canvas" id="gyro-scope"></canvas>
    </div>
  </main>
</div>
```

---

## 6. Dense Cockpit Controls, Foldable Split (`>= 780px`) & Media Rules

Follow these mandatory `M3` density, coarse-pointer, and first-viewport constraints on operational dashboards, documentation readers, and runbooks:

1. **Compact Operational KPI Gauge Row (`.va-kpi-gauge-grid` / `.va-kpi-gauge-card`)**: Use a 4-up desktop (`2-up` `< 960px`) card strip carrying headline scalar, proportional fill gauge (`.va-kpi-gauge-track` / `.va-kpi-gauge-fill`), optional target pin marker (`.va-kpi-gauge-target` — omit completely if unbacked), and 2–3 tabular sub-stats. Never replace real gauge progress with 8 puffy text-only prose boxes.
2. **Joined Workspace Toolbar & Coarse-Pointer Discipline (`.va-toolbar-joined` / `.va-overlay-control`)**: Group related toggles (`role="toolbar"` wrapping `role="group"` segments) at `26–28px` desktop (`32–34px` on `pointer: coarse` tablets/foldables `>= 768px`; `44px` only on interactive `< 700px` handset controls). Keep read-only `.va-pill` / `.va-badge` pills compact (`20–22px`, `2–4px` vertical padding), and give `20–24px` overlay corner controls an invisible `44x44px` `::after` hit box (`.va-overlay-control`).
3. **Foldable Split-Pane Readers & Subgrid Plots (`>= 780px` / `820px` CSS)** + Sticky Budget: Keep `.va-split-reader`, `.va-chart-grid-2`, and `.va-plot-row` / `.va-plot-grid` (`subgrid` card tracks `[header, plot-stage, footer]`) open concurrently down to `>= 780px` (matching real `780–841px` unfolded foldables). Keep sticky header bars to **1 single `space-between` row (`<= 56px`)** (hiding inactive mode filters; enforced `< 64px` by `[STICKY_CHROME_BLOAT]`), keep inspector headers **`<= 2` compact rows (`<= 96px`)** so primary content enters within the top 30%, collapse `0`-issue audit tables inside `<details>`, and never invent synthetic jump sidebars for a single continuous page.
4. **GFM Task Lists, Outline Links & Aspect-Safe Galleries (`object-fit: contain`)**: Strip `list-style: none` on `ul.contains-task-list li.task-list-item` so `[x]` / `[ ]` checkboxes never double with bullet dots. Ensure `<a class="va-nav-link">` outline items wrap cleanly. Use `.va-media-contain` (`object-fit: contain`) on mixed-aspect galleries, and set `.va-compare-grid[data-orient="landscape"]` to stack 16:9 / 1440x900 landscape captures vertically (`1fr`).
5. **Unified Hairline `M3` Multi-Pane Frame & Page-Wide Coherence (`.va-workbench-panes` / `.va-pane` / `.va-pane-hdr`)**: Render `[Left Sidebar | Center Reader | Right Gallery]` as flat peer panes inside `.va-workbench-panes` divided by `1px solid var(--border-subtle)` hairlines with aligned `40px` `.va-pane-hdr` headers, plain right-aligned tabular counts (`.va-pane-count`, e.g. `15` instead of circle bubbles), and zero nested cards-inside-cards. Limit the entire page to `<= 3` repeating card structures, `<= 1` chart per half-width card, unified `.booktabs` row styling, and one cohesive `--chart-1..5` palette.
6. **`ResizeObserver` & `min-width: 0` Chart Hosts (`observeChartResize`)**: Wrap dynamic ECharts hosts with `QuietEChartsDefaults.observeChartResize(hostEl, chart)` (`ResizeObserver` + `requestAnimationFrame` with cleanup returned for unmount/dispose) and enforce `min-width: 0; max-width: 100%;` on `.va-card`, `.va-pane`, `.qe-plot-wrap`, `.qe-echarts-host`, and grid children so half-screen (`~720px`) snaps and vertical tab bars never freeze charts at partial width or spawn horizontal scrollbars.

---

## 7. Anti-Patterns & Operational Violations

| Violation | System Failure | Quiet UI Resolution |
| :--- | :--- | :--- |
| Non-tabular numbers in live streaming table | Column numbers vibrate horizontally, causing nausea and misreading. | Always apply `font-variant-numeric: tabular-nums`. |
| Unconstrained stage spanning 3840px monitors | Left rail at x=0, inspector at x=3800; operator experiences extreme neck strain. | Constrain workspace stage using `var(--stage-workspace-max)`. |
| Ambiguous keyboard focus or sticky bar overlap | Focused element hidden behind sticky bar on keyboard navigation. | Set `scroll-padding-top` to header height + visible 2px focus rings. |
| Full-screen modal viewer at `820px` foldable width | Blocks master list when unfolded tablet width easily fits split reader. | Use `.va-split-reader` / `.va-plot-row` (`subgrid`) at `>= 780px`. |
| Multi-row `> 64px` sticky bars, `> 96px` headers, or expanded `0`-issue tables | Pushes primary evidence below top 30% fold (`[STICKY_CHROME_BLOAT]`). | Enforce 1-row `<= 56px` sticky bar, `<= 2`-row header, collapsed `<details>` audit tables. |
| Inflated `40px` read-only `.va-pill` / `44px` filled corner circles on tablets | Static badges look clickable and circles obscure media thumbnails. | Keep badges `20–22px`, toolbars `32–34px` `>= 768px`, corner rings `22px` + `::after`. |
| `.hidden` declared inside `@layer reset` or `@layer base` | Later `shell`/`views` flex/grid rules silently override `.hidden`. | Declare `utilities` last in `@layer` order and put `.hidden, [hidden]:not([hidden="until-found"]) { display: none; }` inside `@layer utilities`. |

