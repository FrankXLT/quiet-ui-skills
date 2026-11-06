# Reference 04: Application Workspace & Explorer Tiers (`10. App-1` $\rightarrow$ `14. App-Tree`)

All application workspace tiers own the **full `100vw × 100dvh` viewport** starting at `(0,0)`, use **Font Awesome 6 (`fa-solid`)** vector icons with `.va-hamburger-btn` collapsible left rails (`220px` $\leftrightarrow$ `60px`), and implement **Earned Expressiveness (`C3`)** and **App Shell Essentials** (`references/06-meta-chrome-and-nav-morphing.md`).

---

## 1. Tier `10. App-1` — Compact Issue & Ticket Tracker (`0% Cards (Rows)`, Default `S4` Dark, `N1`)

- **Structural Mandate:** Zero floating cards (`0%` card ratio). Uses a 3-pane full-viewport shell (`220px` collapsible left filter spine + `1fr` center `36px` issue row stream + `330px` right live inspector).
- **App Shell Integration:** Includes the `Inbox · 4` monochrome sidebar route, bottom-left `#va-account-pod`, Tier 1 Inline Summary Bar (`<= 36px`) toggling `.va-pulse-drawer`, and `.va-mobile-thumb-bar` on `R5` (`390px`).

---

## 2. Tier `11. App-4` — Task & Calendar Planner (+ Active Focus Session Hero) (`80%` Box Weight, Default `S1` White, `N1`)

Couples an unscheduled backlog staging rail with a time-blocked calendar stage and a Single-Anchor Focus Session Hero:
- **Single-Anchor Focus Session Hero (`.app4-focus-hero`):**
  - Anchors the top of the main stage with a `.va-icon-well` (`fa-bolt`), active time-block title (`Deep Work · Calibration Verification`), `60×60` SVG progress ring (`2/4 Done`), live tabular countdown timer (`00:45:00`), and rounded `.va-pill-btn` duration extenders (`[+15m]`, `[+30m]`).
- **3-Zone Coupled Geometry:**
  1. `220px` Left Sidebar (`N1`, collapsible to `60px` via `.va-hamburger-btn`) with Font Awesome 6 icons (`fa-sun`, `fa-calendar-week`, `fa-inbox`, `fa-chart-pie`) and bottom-left `#va-account-pod`.
  2. `280px` Unscheduled & Backlog Staging Rail (`.app4-staging-tray`) with a rounded `.va-pill-btn.primary` (`fa-wand-magic-sparkles` `Process All`) toggling the inline 2-pane batch triage split.
  3. `1fr` Horizon & Time-Block Stage with `.app4-focus-hero`, In-Place Morphing Command Composer (`.app4-command-composer` + `.app4-token-preview`), and Stateful Time-Block Continuity Strips (`.app4-continuity-strip`).

---

## 3. Tier `12. App-3` — KPI & Analytics Dashboard (Bento Grid) (`100% Cards`, Default `S1` White, `N2`)

- **Structural Mandate:** 12-column CSS Grid (`.app3-grid-12`) of `1px` hairline cards with specular top rim, paired with a balanced 2×2 `.va-bento-2col` executive telemetry strip (`0` empty grid holes; `.va-bento-2col > :last-child:nth-child(odd) { grid-column: 1 / -1; }`). Serves as the **Tier 3 Dedicated `Insights` Route** for `App-1`, `App-4`, and `App-5`.
- **Mandatory 4-Layer Card Anatomy + v4.9/v5.0 Monarch Patterns:** Every `.bento-card` MUST contain `.bento-layer1-header` (with `.va-card-hdr-actions` `[fa-wand-magic-sparkles] [fa-ellipsis]` micro-actions), `.bento-layer2-hero`, `.bento-layer3-proof`, and `.bento-layer4-footer`, supplemented by the 4-card `.va-bento-2col` matrix:
  1. **Card 1 — Expected-Pace Progress Bar (`.va-pace-bar` + `.va-pace-tick`):** Horizontal quota/budget bar with a vertical `|` tick (`left: var(--expected-pct)`) showing expected pace vs. actual consumption.
  2. **Card 2 — 5-Segment Threshold Gauge (`.va-threshold-gauge`):** Multi-band health index (`300 / 580 / 670 / 740 / 800`).
  3. **Card 3 — Cumulative Trajectory vs. Baseline Curve (`.va-trajectory-chart`):** Active cumulative trace stopping at today with vertical drop-fill over a full-period dashed baseline.
  4. **Card 4 — Subsystem Share Ranking (`.va-prop-bar-row`):** Ranked category rows whose CSS `linear-gradient(90deg, ... var(--share-pct), transparent var(--share-pct))` fills the row proportionally.

---

## 4. Tier `13. App-5` (`Life-1`) — Daily Pacing & Wellness Planner (+ Readiness Hero, Fitbit Capsules & Corridor Sparklines) (`75%` Box Weight, Default `S1` White, `N1`)

Designed for finite daily human energy, transition-friction visibility, and realistic 24-hour time budgeting:
- **2-Column Restorative Hero Grid (`.app5-hero-grid`: `1.35fr 1fr`, `18px` Radius):**
  - **Left Hero Card (`.app5-hero-card`):** Soft radial surface tint, `.va-icon-well.tint-emerald` (`fa-heart-pulse`), plain-English headline, `96×96` SVG Readiness Ring (`.app5-readiness-ring` showing `84 · Steady`), segmented pill bar (`.va-seg-pills`), and **3 Stacked Self-Filling Two-Tone Progress Capsules (`.va-fill-capsule`)** (`Restorative Sleep 7h 48m`, `Zone 2 Movement 38/45m`, `Cognitive Focus 3.5/4.5h`).
  - **Right Hero Card:** Proportional 24-Hour (1,440-Minute) Day Arc bar + **2-Up Target-Corridor 7-Day Sparklines (`.va-corridor-sparkline`)** (`S S M T W T (F)` with circled current day and `[In range]` badge) + **Connected State Hypnogram (`.va-state-hypnogram`)**.
- **Visual Vertical Day-Arc Timeline (`.app5-day-timeline`):**
  - Chronological vertical spine with a red `NOW 11:25` marker (`.va-now-line`) paired with inline Stepping Stones (`.life1-stepping-stones`) and the right-hand *"Held for Tomorrow"* tray.

---

## 5. Tier `14. App-Tree` — Hierarchical Tree, Schema & File Explorer Workbench (`90% 3-Pane`, Default `S1` White, `N1`)

Dedicated archetype for Database Schema Browsers, Git/IDE File Explorers, JSON/AST Inspectors, and Configuration Hierarchies:
- **Domain Workbench Pane Preservation Across `N0`, `N2`, and `N4` + Never Collapse Into Unlabelled `60px` Strip (`v5.0`):**
  - Unlike ordinary navigation sidebars, `.va-tree-pane` (`Object Explorer`) is the primary **Domain Workbench Pane** of `14. App-Tree` and remains a **labeled `228px–260px` schema tree across all `>= 641px` states** (never collapsing schema columns into unlabelled icons in a `60px` strip, and never clipping `wr_phase_samples` or `sample_id`).
  - Both `.va-tree-pane` (`#va-tree-left-pane`) and `.va-tree-inspector` (`#va-tree-right-pane`) include `«` / `»` collapse triggers (`toggleAppTreePane('left'|'right')`) that collapse either pane into a `28px` vertical edge tab (`#va-tree-left-edge-tab`, `#va-tree-right-edge-tab`).
- **3-Pane Coupled Layout & `v5.0` Alignment Invariants:**
  1. **Left Hierarchical Tree Explorer (`.va-tree-pane`, `260px` desktop / `228px` tablet):** Active tree nodes (`.va-tree-node.active`) use a straight `::before` vertical pill (`left: 4px; top: 6px; bottom: 6px; width: 3px; border-radius: 99px`) with zero curved parenthesis glitch.
  2. **Center 3-Tab Multi-Mode Workbench (`1fr`):**
     - **Single-Line Tabs (`#tree-center-tabs`):** `flex-wrap: nowrap; white-space: nowrap; overflow-x: auto;` so tabs never orphan onto a second line.
     - **Tab 1 (`Table Data · 142,840 rows`):** Top filter bar with 2-column `.va-tree-filter-selects` (`Node` & `Status`), `table.va-tree-grid th { vertical-align: top !important; }` with `<span class="va-th-title">` (`|thTitle[i].top - thTitle[0].top| <= 2px`), ellipsis-protected JSONB column (`td:last-child { max-width: 180px; text-overflow: ellipsis; }`), and `padding-bottom: 76px` in `N4`.
     - **Tab 2 (`Column Spec & Indexes`) & Tab 3 (`Query & AST Preview`).**
  3. **Right Contextual Object & FK Inspector (`.va-tree-inspector`, `280px`).**
