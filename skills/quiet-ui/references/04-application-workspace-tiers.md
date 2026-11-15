# Reference 04: Application Workspace & Explorer Tiers (`10. App-1` $\rightarrow$ `14. App-Tree`)

Quiet UI Application Workspace tiers power daily operational productivity, dispatch triage, multidimensional telemetry analytics, and structural schema exploration. They strictly enforce **De-Barnacling Budgets**, **Domain-Authentic Navigation** (strictly zero generic "Home / Telemetry / Specs" dummy rails), and a **Desktop N4 Guardrail** (bottom docks are strictly confined to handheld viewports `< 700px`).

---

## 1. Workspace Core Principles: De-Barnacling, Domain-Authentic Nav & Zero Grid Holes

### 1.1 De-Barnacling Budgets & Progressive Disclosure
Dense operational tools frequently suffer from feature creep ("barnacles")—nested frames, excessive badges, and conflicting borders that produce visual noise. Quiet UI enforces strict visual limits:
- **Maximum 1 Status Strip:** At most one prominent status strip per card or panel.
- **Maximum 2 Nested Border Depths:** Never exceed two levels of inset borders (`panel > sub-card`).
- **Maximum 4 Active Font Sizes:** Within any single workspace card, typography is restricted to at most 4 sizes from the 7-step scale (e.g., `11px`, `13px`, `15.5px`, `22px`).
- **Maximum 2 Text Contrast Rungs:** Primary body uses `var(--text-primary)`; supporting metadata uses `var(--text-secondary)`. Muted text (`var(--text-muted)`) is reserved for inactive disabled states.
- **Progressive Disclosure Overlays:** Secondary diagnostic logs, deep schema properties, and batch triage workflows use native `<dialog closedby="any">` or popovers rather than cluttering primary views.

### 1.2 Domain-Authentic Navigation & Desktop N4 Prohibition
- **Domain-Specific Hierarchy:** Rails and command bars must reflect actual domain capabilities (e.g., `Triage Queue`, `Flight Logs`, `Telemetry Staging`, `Schema Trees`, `Mission Assets`). Generic dummy rails (`Home`, `Telemetry`, `Specs`, `Settings`) are strictly prohibited in showcase implementations.
- **Desktop N4 Prohibition:** Bottom thumb docks (`N4`) exist exclusively for thumb ergonomics on narrow handheld screens (`< 700px`). On desktop screens (`>= 700px`), `data-default-nav="auto"` automatically renders `N1` (left rail) or `N2` (top bar). Hardcoding `data-default-nav="n4"` on desktop is a critical contract violation.

### 1.3 Zero-Hole Bento Geometry
Every card in an executive Bento grid (`12. App-3`) must have a functional purpose and complete spatial fill. Empty grid cells, mismatched card heights, and floating whitespace voids (`> 30%` unused vertical canvas) are strictly rejected.

---

## 2. Tier-by-Tier Component Anatomy & Contracts

### 10. Tier `App-1`: Compact Flight Discrepancy Queue (`0% Cards (Rows)`, Default `white`, `N1`)
- **Structure:** Zero floating cards (`0%` card ratio). Uses a full-viewport 3-pane triage layout:
  - Left: `220px` Collapsible Discrepancy Filter Spine (`ALL (14)`, `CRITICAL (3)`, `WARNING (6)`, `RESOLVED (5)`).
  - Center: `1fr` 36px-row Flight Discrepancy Stream with 14+ discrete telemetry anomaly items (`DISC-0101` through `DISC-0114`). Columns: Discrepancy ID, Subsystem Tag, Severity Pill, Anomaly Summary, Assignee, SLA Countdown.
  - Right: `340px` Live Flight Inspector detailing root cause, real-time waveform excerpt, disposition actions (`ACKNOWLEDGE`, `DEFER`, `ESCALATE`), and audit history.
- **Ergonomics:** Compact 36px row height allows reviewing dozens of open flight anomalies without excessive scrolling.

### 11. Tier `App-4`: Task & Calendar Planner (+ Focus Hero) (`80%` Box Weight, Default `white`, `N1`)
- **Three-Zone Shell:**
  - Left (`220px`): Category Spine (`NRHO Operations`, `EVA-01 Prep`, `Cryo Servicing`, `Ground Comm Pass`).
  - Center-Left (`280px` Unscheduled Staging Inbox): Quick task capture input (press `/` to focus), priority rings (`.p1` rose, `.p2` amber, `.p3` indigo, `.p4` slate), and draggable staging cards.
  - Right (`1fr` Horizon & Calendar Stage):
    - **Single-Anchor Focus Hero (`.app4-focus-hero`):** Prominent circular countdown timer (`00:45:00`), SVG progress ring, task thesis (*"Calibrate Palomar Adaptive Optics Deformable Mirror"*), and quick duration extenders (`[+15m]`, `[+30m]`).
    - **Hourly NRHO Operations Calendar:** Grid timeline with current-time marker (`.va-now-line`), left-accent time blocks (`border-left: 3px solid ...`), and conflict resolution popover alert.

### 12. Tier `App-3`: Executive Bento Dashboard (`100% Cards`, Default `white`, `N2`)
- **Complete 6-Card Bento Matrix (Zero Empty Holes):**
  - **Card 1 (Throughput Pacing Bar):** Cumulative data volume received vs. mission model, featuring an expected-pace vertical tick (`.va-pace-bar`).
  - **Card 2 (5-Segment Threshold Gauge):** Multi-band operational optical link health index (`.va-threshold-gauge`).
  - **Card 3 (Trajectory Range Plot):** Deep Space optical link range plot (0.2 AU to 2.8 AU) stopping precisely at today's mission date with dashed projected trajectory and collision-free text halos.
  - **Card 4 (DSN Complex Share Bars):** Proportional category share bars (`.va-prop-bar-row`) showing aperture allocation across Goldstone (42%), Madrid (33%), and Canberra (25%).
  - **Card 5 (Subsystem Unit Economics):** High-density sparkbars showing cost per gigabit downlinked ($/Gb) compared to legacy Ka-band RF downlinks.
  - **Card 6 (Atmospheric Optical Transmittance Matrix):** Atmospheric channel visibility and cloud cover across ground optical reception sites (Palomar, Table Mountain, Haleakala).
- **Time Horizon Controls:** Header pill switcher (`24H`, `7D`, `30D`, `Mission Orbit`).

### 13. Tier `App-5`: Circadian Pacing & Workload Planner (`75%` Box Weight, Default `white`, `N1`)
- **Restorative Hero Split (`1.35fr 1fr`, 16px Radius):**
  - **Left Hero Card:**
    - Readiness Ring (`88 · Steady`), segmented readiness pills (`Physical`, `Cognitive`, `Atmospheric`).
    - **3 Self-Filling Progress Capsules (`.va-fill-capsule`):** (1) *Restorative Sleep (8.2h / 8.0h target)*, (2) *Zone 2 Aerobic Movement (45m / 45m target)*, (3) *Deep Cognitive Focus (3.5h / 4.0h target)*.
  - **Right Hero Card:**
    - 24-Hour Segmented Day Arc Bar.
    - **Collision-Free Target Corridor Sparkline (`.va-corridor-sparkline`):** Melatonin and cortisol circadian corridor with shaded nominal range and halo-protected callouts.
    - **4-Stage Sleep Hypnogram (`.va-state-hypnogram`):** Deep, REM, Light, and Wake sleep cycles across the 8-hour sleep window.
- **Vertical Day-Arc Timeline (`.app5-day-timeline`):** Chronological timeline with live `NOW` marker and holding tray.

### 14. Tier `App-Tree`: Hierarchical Schema & Bitfield Explorer (`90% 3-Pane`, Default `white`, `N1`)
- **Domain Workbench Architecture:**
  - Left Pane (`240px` Object Hierarchy Tree): Expandable `catalog -> schema -> table -> column` navigation with search filter. Stays expanded on desktop and collapses to `28px` edge rail on demand.
  - Center Pane (`1fr` Workbench Tabs): 3 tabbed views (`Table Data`, `Bitfields Spec`, `ER Lineage`). Displays 14+ clickable CCSDS Space Packet telemetry records with header alignment (`|th.top - th0.top| <= 2px`) and ellipsis-protected JSONB columns.
  - Right Pane (`320px` Inspector): Synchronized telemetry payload inspector displaying raw hex, parsed bitfield layout, and JSON schema properties.

---

## 3. Implementation Code Patterns & Token Bindings

### 3.1 Expected-Pace Consumption Bar (App-3)
```html
<div class="va-pace-bar-wrap" role="progressbar" aria-valuenow="68" aria-valuemin="0" aria-valuemax="100">
  <div class="va-pace-track">
    <div class="va-pace-fill" style="width: 68%; background: var(--accent-focal);"></div>
    <!-- Expected Pace Vertical Marker -->
    <div class="va-pace-expected-tick" style="left: 60%;" title="Expected Pace (60%)"></div>
  </div>
  <div class="va-pace-labels">
    <span>Downlinked: 68.0 TB</span>
    <span class="pace-delta is-ahead">+8.0 TB ahead of plan</span>
  </div>
</div>
```

### 3.2 Restorative Progress Capsule (App-5)
```html
<div class="va-fill-capsule">
  <div class="capsule-header">
    <span class="capsule-title">Deep Cognitive Work</span>
    <span class="capsule-val">3.5h / 4.0h</span>
  </div>
  <div class="capsule-track">
    <div class="capsule-fill" style="width: 87.5%; background: var(--tint-indigo-bg); border: 1px solid var(--accent-focal);"></div>
  </div>
</div>
```

### 3.3 Priority Ring Task Item (App-4)
```html
<div class="va-task-row">
  <button class="va-priority-ring p1" aria-label="Mark completed" title="Priority 1 · Critical"></button>
  <span class="va-task-text">Verify Palomar deformable mirror actuators prior to pass</span>
  <span class="va-task-time">14:30 UTC</span>
</div>
```

### 3.4 Focus Hero Timer & Duration Extenders (App-4)
```html
<section class="app4-focus-hero" aria-label="Active Focus Session">
  <div class="focus-timer-ring">
    <svg width="120" height="120" viewBox="0 0 120 120" preserveAspectRatio="xMidYMid meet">
      <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border-hairline)" stroke-width="4"/>
      <circle cx="60" cy="60" r="52" fill="none" stroke="var(--accent-focal)" stroke-width="4"
              stroke-dasharray="326.7" stroke-dashoffset="81.6" stroke-linecap="round"/>
    </svg>
    <div class="focus-digits">00:33:45</div>
  </div>
  <div class="focus-controls">
    <button class="va-pill-btn">+15m</button>
    <button class="va-pill-btn">+30m</button>
    <button class="va-pill-btn is-active">Pause</button>
  </div>
</section>
```

### 3.5 App-Tree 3-Pane Workbench Architecture
```css
.app-tree-shell {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr) 320px;
  width: 100%;
  height: 100%;
  gap: 1px;
  background: var(--border-grid);
  border: 1px solid var(--border-strong);
}

.tree-column {
  background: var(--bg-surface);
  overflow-y: auto;
  padding: 0.75rem;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.5rem;
  font-family: var(--font-sans);
  font-size: var(--ts-sm, 12.5px);
  color: var(--text-primary);
  border-radius: var(--radius-inner);
  cursor: pointer;
}

.tree-node.is-active {
  background: var(--tint-indigo-bg);
  color: var(--accent-focal);
  font-weight: 600;
}
```

---

## 4. Verification & Audit Checklist for Application Workspaces
- [ ] Strictly zero dummy rails (`Home`, `Telemetry`, `Specs`); all nav bars use domain-authentic routes.
- [ ] Desktop default nav (`>= 700px`) is `N1` or `N2`; `N4` is strictly prevented on desktop.
- [ ] Bento grid in App-3 has exactly 6 populated cards with zero empty grid holes.
- [ ] App-1 queue contains at least 12 distinct actionable discrepancy items.
- [ ] App-Tree features a functioning 3-pane shell with clickable CCSDS packet rows.
- [ ] All interactive buttons and inputs satisfy the minimum 44px touch target on mobile.
- [ ] Vertical whitespace void across workspaces stays below 30% of available viewport height.
