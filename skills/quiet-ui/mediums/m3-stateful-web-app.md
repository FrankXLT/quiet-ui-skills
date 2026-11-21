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
@layer quiet.mediums, quiet.workspace;

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

## 6. Dense Cockpit Controls, Foldable Split (>= 860px) & Media Comparison Rules

Follow these mandatory `M3` density and layout constraints on operational dashboards, documentation readers, and runbooks:

1. **Compact Operational KPI Gauge Row (`.va-kpi-gauge-grid` / `.va-kpi-gauge-card`)**: Use a 4-up desktop (`2-up` `< 960px`) card strip carrying headline scalar, proportional fill gauge (`.va-kpi-gauge-track` / `.va-kpi-gauge-fill`), optional target pin marker (`.va-kpi-gauge-target` — omit completely if unbacked), and 2–3 tabular sub-stats. Never replace real gauge progress with 8 puffy text-only prose boxes.
2. **Joined Single-Row Workspace Toolbar (`.va-toolbar-joined` / `.va-tb-group` / `.va-tb-btn`)**: Group related filter toggles, scope selectors, and export actions (`role="toolbar"` wrapping `role="group"` button clusters separated by `.va-tb-sep`) inside compact `26–28px` desktop strips (`44px` minimum under `@media (pointer: coarse)` or `< 720px`) instead of letting `32px` loose pills wrap across `4–5` rows. Apply `aria-pressed` only to stateful toggle buttons.
3. **Foldable Split-Pane Readers (`>= 860px`) & Zero Synthetic Jump Sidebars**: Keep list + document readers side-by-side down to `>= 860px` (unfolded foldable screens) instead of hiding behind full-screen modals until `1200px`. Collapse scrolled sticky chrome `< 1100px` to the brand row only, and never invent a `6–7` link left-rail jump sidebar for a single continuous page.
4. **GFM Task Lists, Outline Links & Aspect-Safe Galleries (`object-fit: contain`)**: Strip `list-style: none` on `ul.contains-task-list li.task-list-item` so `[x]` / `[ ]` checkboxes never double with bullet dots. Ensure `<a class="va-nav-link">` outline items wrap instead of `text-overflow` clipping mid-word. Use `.va-media-contain` (`object-fit: contain`) on mixed-aspect galleries, and set `.va-compare-grid[data-orient="landscape"]` to stack 16:9 / 1440x900 landscape captures vertically (`1fr`) rather than squeezing them side-by-side inside narrow portrait frames.

---

## 7. Anti-Patterns & Operational Violations

| Violation | System Failure | Quiet UI Resolution |
| :--- | :--- | :--- |
| Non-tabular numbers in live streaming table | Column numbers vibrate horizontally, causing nausea and misreading. | Always apply `font-variant-numeric: tabular-nums`. |
| Unconstrained stage spanning 3840px monitors | Left rail at x=0, inspector at x=3800; operator experiences extreme neck strain. | Constrain workspace stage using `var(--stage-workspace-max)`. |
| Full-page re-renders on telemetry packet arrival | UI drops frames, freezes mouse clicks, and causes input stutter. | Isolate real-time updates to dedicated CSS variables and `<canvas>`. |
| Ambiguous keyboard focus states | Operator triggers destructive state change on unintended node. | Implement visible 2px solid focus rings on all interactive rows. |
| Full-screen modal viewer at 900px foldable width | Blocks master list when unfolded tablet width easily fits split reader. | Use `.va-split-reader` at `>= 860px` instead of full-screen modal overlays. |
| Five-row wrapped `32px` filter pills & sticky 3-bar headers | Consumes half the vertical viewport on desktops and foldables. | Consolidate into `.va-toolbar-joined` (`26–28px`) and brand-only sticky `< 1100px`. |
| Double bullet + checkbox or clipped outline nav links | Corrupted markdown task lists and truncated navigation labels (`inspect_visu`). | Reset `list-style: none` on `.contains-task-list` and allow multi-line outline wrapping. |
| Landscape (`1440x900`) shots side-by-side in portrait `Compare (2)` | Leaves `60–70%` vertical letterbox voids and unreadable thumbnail text. | Use `object-fit: contain` (`.va-media-contain`) and stack landscape comparisons (`1fr`). |

