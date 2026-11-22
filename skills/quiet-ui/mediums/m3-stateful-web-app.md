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
1. **Topbar Drawer Trigger + Auto-Closing Overlay Rail (`.va-side-rail[data-mode="overlay"]` + `.va-drawer-backdrop` + `.va-rail-footer`)**: Place the left-of-brand panel toggle inside `.va-shell-topbar`, keep high-frequency scope/period selectors (`.va-period-stepper` + `.va-preset-popover` + `.va-scope-chip`) visible in the sticky topbar, and route hierarchical navigation through a closed-by-default opaque `var(--bg-surface)` overlay rail (`100dvw × 100svh` `< 680px`, `50dvw` `680–1199px`, `min(28rem, 42dvw)` `>= 1200px`) with split `.va-tree-row` branches and low-frequency utilities in `.va-rail-footer`.
2. **Master Queue / Dispatcher (`.va-pane` inside `.va-workbench-panes`)**: High-density interactive list or data table supporting keyboard navigation, batch selection, and live sorting.
3. **Detail Inspector (`.va-pane` inside `.va-workbench-panes`)**: Collapsible context panel displaying deep telemetry, 1-tap `.va-tab-strip` document switchers (`<= 6` siblings), and mutation forms.

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

1. **Compact Operational KPI Gauge Row (`.va-kpi-gauge-grid` / `.va-kpi-gauge-card`) & Trackless Totals (`.va-kpi-grid` / `.va-kpi-card`)**: Use bounded `.va-kpi-gauge-card` strips (`.va-kpi-gauge-track` / `.va-kpi-gauge-fill` + shared-denominator `.va-kpi-gauge-target` omitted when unbacked) strictly for ratios with a real capacity ceiling; render unbounded cumulative totals (`steps`, `tokens`, `calls` without ceiling) using trackless `.va-kpi-card` inside `.va-kpi-grid` (`[FAKE_UNBOUNDED_GAUGE]`).
2. **Joined Workspace Toolbar & Coarse-Pointer Discipline (`.va-toolbar-joined` / `.va-overlay-control`)**: Group toggles (`role="toolbar"` wrapping `--bg-subtle` `.va-tb-group` segments with `flex: 0 0 auto;`) using raised `--bg-surface` active state + `inset 0 0 0 1px var(--border-strong)` (`forced-colors: active` Highlight)—reserving accent bottom underlines exclusively for `.va-tab` navigation. Use `26–28px` desktop (`32–34px` on `pointer: coarse` tablets/foldables `>= 768px`; `44px` strictly `< 700px` handsets), compact `20–22px` static `.va-badge`/`.va-pill` tags, and `44x44px` `::after` hit boxes on `.va-overlay-control`.
3. **Composite `[Chart + Table]` 1-Column Rule, Chart-Only 2-Up `.va-plot-row` & Ultrawide `1480px` Cap**: Composite cards combining **both a chart AND a multi-column table** MUST span **1 column full-width** across all viewports so stacked vertical `[x_left, x_right]` axes stay aligned and tables never cram into 3-line wrapped cells. Reserve side-by-side 2-up `.va-plot-row` / `.va-plot-grid` pairs (`>= 780px` / `>= 1080px` `subgrid`) strictly for **compact chart-only cards**, and cap full-width stages at `max-inline-size: 1480px; margin-inline: auto;` above `1920px`.
4. **Topbar Drawer Trigger, Auto-Closing Overlay Rail & Period Stepper (`.va-side-rail[data-mode="overlay"]` + `.va-rail-footer` + `.va-period-stepper`)**: Mount the drawer toggle at the far left of `.va-shell-topbar`, keep high-frequency `.va-period-stepper` + `.va-preset-popover` (`Calendar-to-Date` vs. `Rolling Windows`, preventing `[TOOLBAR_CONTROL_SPRAWL]`) and `.va-scope-chip` (`All` / `Entity ×` / `Entity / Item`) visible in the sticky topbar, move low-frequency app utilities (`D1–D4`, theme, version, `< Classic`) into `.va-rail-footer`, split inline `.va-tree-caret` expand vs. 1-tap `.va-tree-dest` navigation inside `.va-tree-row` (auto-closing the opaque rail and auto-expanding active parent branches on reopen; `[TRANSPARENT_OVERLAY]`), and render `<= 6` sibling docs as `.va-tab-strip` underline `.va-tab` tabs (`[PANE_CONTROL_CLIPPED]`).
5. **Foldable Split Panes, Responsive Sticky Budget & Unified `M3` Frame (`.va-workbench-panes` / `.va-pane` / `.va-pane-hdr`)**: Keep `.va-split-reader` open down to `>= 780px`, enforce `<= 64px` (`<= 56px` target) single-row sticky topbars at `>= 680px` and `<= 88px` (2 compact rows) on `< 680px` portrait phones (`[STICKY_CHROME_BLOAT]`), keep inspector headers `<= 96px`, collapse `0`-issue tables in `<details>`, strip GFM checkbox bullets (`ul.contains-task-list`), use `.va-media-contain` + `.va-compare-grid[data-orient="landscape"]`, render `[Left | Center | Right]` flat peers in `.va-workbench-panes` (`40px` `.va-pane-hdr`, plain `.va-pane-count`), and limit pages to `<= 3` repeating card structures + one `--chart-1..5` palette.
6. **`ResizeObserver` & `min-width: 0` Chart Hosts (`observeChartResize`)**: Wrap dynamic ECharts hosts with `QuietEChartsDefaults.observeChartResize(hostEl, chart)` (`ResizeObserver` + `requestAnimationFrame` with cleanup returned for unmount/dispose) and enforce `min-width: 0; max-width: 100%;` on `.va-card`, `.va-pane`, `.qe-plot-wrap`, `.qe-echarts-host`, and grid children so half-screen (`~720px`) snaps never freeze charts or clip controls.

---

## 7. Anti-Patterns & Operational Violations

| Violation | System Failure | Quiet UI Resolution |
| :--- | :--- | :--- |
| Non-tabular numbers in live streaming table | Column numbers vibrate horizontally, causing nausea and misreading. | Always apply `font-variant-numeric: tabular-nums`. |
| Unconstrained stage spanning 1920–3840px monitors | Heatmaps/bars stretch paper-thin and cause neck strain. | Built-in `max-inline-size: 1480px; margin-inline: auto;` stage cap (`>= 1920px`). |
| Chart + multi-column table jammed inside 2-up half card | Cramped 3-line wrapped table cells and misaligned chart X spines. | Span composite `[Chart + Table]` cards 1-column full-width (`va-plot-row` chart-only). |
| Progress track `.va-kpi-gauge-track` on unbounded totals | Fabricates artificial fill % (`[FAKE_UNBOUNDED_GAUGE]`). | Render trackless `.va-kpi-card` in `.va-kpi-grid`; match bar & target denominators. |
| Full-screen modal viewer at `820px` foldable width | Blocks master list when unfolded tablet width easily fits split reader. | Use `.va-split-reader` / `.va-plot-row` (`subgrid`) at `>= 780px`. |
| Multi-row sticky bar `> 88px` phone / `> 64px` desktop or `> 6` window buttons | Steals first viewport (`[STICKY_CHROME_BLOAT]`, `[TOOLBAR_CONTROL_SPRAWL]`). | Keep sticky chrome `<= 64px` `>= 680px` (`<= 88px` `< 680px`) and use `.va-period-stepper` + `.va-preset-popover`. |
| Inflated `40px` read-only `.va-pill` / `44px` filled corner circles on tablets | Static badges look clickable and circles obscure media thumbnails. | Keep badges `20–22px`, toolbars `32–34px` `>= 768px`, corner rings `22px` + `::after`. |
| Drawer trigger scrolls away, transparent `.va-pane` overlay, or clipped tabs | Traps users scrolled down, bleeds page copy (`[TRANSPARENT_OVERLAY]`), or clips (`[PANE_CONTROL_CLIPPED]`). | Place sticky left-of-brand toggle in `.va-shell-topbar`, use opaque overlay `.va-side-rail` + `.va-rail-footer`, and use scrollable `.va-tab-strip`. |
| `evidence` placed after `views` or `.hidden` outside `@layer utilities` | Bundle styles block custom view overrides and flex/grid breaks `.hidden`. | Declare `@layer reset, tokens, shell, archetypes, evidence, views, utilities;` cleanly. |

