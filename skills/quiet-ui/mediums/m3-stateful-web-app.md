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
4. **Topbar Drawer Trigger, Single-Row `.va-rail-footer` & Flat Trees (`.va-side-rail[data-mode="overlay"]` + `.va-swatch-row` + `.va-period-stepper`)**: Mount the drawer toggle at the far left of `.va-shell-topbar`, keep `.va-period-stepper` + `.va-preset-popover` (`[TOOLBAR_CONTROL_SPRAWL]`) and `.va-scope-chip` (`All` / `Entity ×` / `Entity / Item`) visible in the sticky topbar, and keep `.va-rail-footer` to a **single `40px` `space-between` horizontal row** holding left circular theme swatches (`.va-swatch-row` / `20px` `.va-swatch-btn` with `44×44px` `::after` hit area, active ring, `aria-label`, zero text) and right **2-stop density toggle (`Compact | Comfortable`)**—banning `Lock`, `< Classic`, version badges, or `> 2` density buttons (`[DENSITY_STOP_SPRAWL]`, `[RAIL_FOOTER_CLUTTER]`). Render navigation trees flat and borderless inside `.va-side-rail` without `.va-card` borders (`[TREE_NESTED_CARD_BORDERS]`), constraining `.va-tree-row` to single-line `36px` height, `<= 1` trailing `.va-tree-action`, and `<= 5` visible children inside `.va-tree-children` ahead of `.va-tree-more` (`+ Show N older…`), rendering `<= 6` sibling docs as `.va-tab-strip` `.va-tab` buttons.
5. **Prose-Floor Split Reader (`>= 60%`), `< 760px` Native `<dialog closedby="any">` & Shortcut Guard (`.va-split-reader-gallery` / `dialog.va-modal-sheet`)**: Replace narrow split readers with `.va-split-reader-gallery`: `>= 1280px` renders `60%` primary prose / `40%` 2-col companion gallery, `760–1279px` renders `64%` prose / `36%` 1-col companion (`[PROSE_PANE_CRAMPED]` flags panes `< 55%` of split width), and `< 760px` switches to a full-width primary reader (hiding `.va-split-mode-toggle`) plus inline `.va-split-sheet-trigger` opening a native top-layer `<dialog class="va-modal-sheet" closedby="any">` (styles scoped strictly to `[open]` + `:modal` / `::backdrop` scroll lock). Always guard global keyboard shortcuts with `if (document.querySelector('dialog[open]')) return;` so `Escape` and shortcuts never fight active modal sheets. Enforce `<= 64px` sticky topbars (`>= 680px`) and `<= 88px` (`< 680px`, `[STICKY_CHROME_BLOAT]`).
6. **`ResizeObserver` & `min-width: 0` Chart Hosts (`observeChartResize`)**: Wrap dynamic ECharts hosts with `QuietEChartsDefaults.observeChartResize(hostEl, chart)` (`ResizeObserver` + `requestAnimationFrame` with cleanup returned for unmount/dispose) and enforce `min-width: 0; max-width: 100%;` on `.va-card`, `.va-pane`, `.qe-plot-wrap`, `.qe-echarts-host`, and grid children so half-screen (`~720px`) snaps never freeze charts or clip controls.

---

## 7. Anti-Patterns & Operational Violations

| Violation | System Failure | Quiet UI Resolution |
| :--- | :--- | :--- |
| Non-tabular numbers in live streaming table | Column numbers vibrate horizontally, causing nausea and misreading. | Always apply `font-variant-numeric: tabular-nums`. |
| Unconstrained stage spanning 1920–3840px monitors | Heatmaps/bars stretch paper-thin and cause neck strain. | Built-in `max-inline-size: 1480px; margin-inline: auto;` stage cap (`>= 1920px`). |
| Chart + multi-column table jammed inside 2-up half card | Cramped 3-line wrapped table cells and misaligned chart X spines. | Span composite `[Chart + Table]` cards 1-column full-width (`va-plot-row` chart-only). |
| Progress track `.va-kpi-gauge-track` on unbounded totals | Fabricates artificial fill % (`[FAKE_UNBOUNDED_GAUGE]`). | Render trackless `.va-kpi-card` in `.va-kpi-grid`; match bar & target denominators. |
| Cramped `< 55%` prose reader on desktop/foldable | Forces awkward 35–45ch line wraps while companion media hogs width (`[PROSE_PANE_CRAMPED]`). | Use `.va-split-reader-gallery` (`60–64%` primary prose) + `< 760px` `<dialog class="va-modal-sheet" closedby="any">`. |
| `3+` density buttons or stacked `Lock`/`< Classic` footer | Crowds drawer footer and creates vertical scrollbars (`[DENSITY_STOP_SPRAWL]`, `[RAIL_FOOTER_CLUTTER]`). | Use 1-row `40px` `.va-rail-footer` (`Space-Between`): `.va-swatch-row` left, 2-stop `Compact \| Comfortable` right. |
| Bordered `.va-card` boxes inside `.va-side-rail` tree | Creates visual box-in-box noise and clips long tree titles (`[TREE_NESTED_CARD_BORDERS]`). | Render borderless `.va-tree-row` (`36px`), ellipsis label, `<= 1` `.va-tree-action`, and `.va-tree-more` after `5` kids. |
| Multi-row sticky bar `> 88px` phone / `> 64px` desktop | Steals first viewport (`[STICKY_CHROME_BLOAT]`, `[TOOLBAR_CONTROL_SPRAWL]`). | Keep sticky chrome `<= 64px` `>= 680px` (`<= 88px` `< 680px`) and use `.va-period-stepper` + `.va-preset-popover`. |
| Drawer trigger scrolls away, transparent `.va-pane` overlay, or clipped tabs | Traps users scrolled down, bleeds page copy (`[TRANSPARENT_OVERLAY]`), or clips (`[PANE_CONTROL_CLIPPED]`). | Place sticky left-of-brand toggle in `.va-shell-topbar`, use opaque overlay `.va-side-rail` + `.va-rail-footer`, and use scrollable `.va-tab-strip`. |
| `evidence` placed after `views` or `.hidden` outside `@layer utilities` | Bundle styles block custom view overrides and flex/grid breaks `.hidden`. | Declare `@layer reset, tokens, shell, archetypes, evidence, views, utilities;` cleanly. |

