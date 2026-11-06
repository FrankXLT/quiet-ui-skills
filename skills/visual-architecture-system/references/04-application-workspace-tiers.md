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

## 3. Tier `12. App-3` — KPI & Analytics Dashboard (Bento Grid) (`100% Cards`, Default `S4` Dark, `N2`)

- **Structural Mandate:** 12-column CSS Grid (`.app3-grid-12`) of `1px` hairline cards with specular top rim. Serves as the **Tier 3 Dedicated `Insights` Route** for `App-1`, `App-4`, and `App-5`.
- **Mandatory 4-Layer Card Anatomy:** Every `.bento-card` MUST contain `.bento-layer1-header`, `.bento-layer2-hero`, `.bento-layer3-proof`, and `.bento-layer4-footer`.

---

## 4. Tier `13. App-5` (`Life-1`) — Daily Pacing & Wellness Planner (+ Readiness Hero & Day Timeline) (`75%` Box Weight, Default `S2` Paper, `N1`)

Designed for finite daily human energy, transition-friction visibility, and realistic 24-hour time budgeting:
- **2-Column Restorative Hero Grid (`.app5-hero-grid`: `1.35fr 1fr`, `18px` Radius):**
  - **Left Hero Card (`.app5-hero-card.primary-hero`):** Soft radial surface tint, `.va-icon-well.emerald` (`fa-heart-pulse`), plain-English headline (*"Steady Energy & Balanced Recovery"*), `96×96` SVG Readiness Ring (`.app5-readiness-ring` showing `84 · Steady`), and rounded segmented pill bar (`.va-seg-pills`: `Standard Rhythm | Gentle Pacing | Afternoon Reset`).
  - **Right Hero Card:** Proportional 24-Hour (1,440-Minute) Day Arc bar (`Sleep 8.0h + Anchors 8.5h + Buffered Focus 3.5h + Breathing Room 4.0h`) + 1-tap `Open +90m Breathing Room` pill button.
- **Visual Vertical Day-Arc Timeline (`.app5-day-timeline`):**
  - Chronological vertical spine (`09:00` Morning Deep Focus, `11:00` Clear Garage Workbench `+40% Buffer`, `15:30` School Pickup Protected Anchor, `18:00` Family Dinner & Unscheduled Margin) paired with inline Stepping Stones (`.life1-stepping-stones`) and the right-hand *"Held for Tomorrow"* tray.

---

## 5. Tier `14. App-Tree` — Hierarchical Tree, Schema & File Explorer Workbench (`90% 3-Pane`, Default `S1` White, `N1`)

Dedicated archetype for Database Schema Browsers, Git/IDE File Explorers, JSON/AST Inspectors, and Configuration Hierarchies:
- **Domain Workbench Pane Preservation Across `N0`, `N2`, and `N4` + `28px` Collapsible Edge Tabs (`v4.6`):**
  - Unlike ordinary navigation sidebars, `.va-tree-pane` (`Object Explorer`) is the primary **Domain Workbench Pane** of `14. App-Tree` and remains visible (`260px` on desktop, `200px` on `641–1099px`) even when `N0`, `N2`, or `N4` is selected.
  - Both `.va-tree-pane` (`#va-tree-left-pane`) and `.va-tree-inspector` (`#va-tree-right-pane`) include `«` / `»` collapse triggers (`toggleAppTreePane('left'|'right')`) that collapse either pane into a `28px` vertical edge tab (`#va-tree-left-edge-tab`, `#va-tree-right-edge-tab`).
- **3-Pane Coupled Layout:**
  1. **Left Hierarchical Tree Explorer (`.va-tree-pane`, `260px`):** Includes live `[/] Filter schema objects...` input (`filterTreeObjects()`), Dual-Mode Switcher (`.va-seg-pills`: `DB Schema` vs. `File Tree`), and nested `.va-tree-node` rows (`28px` height) with `1px` `.va-tree-guide` vertical indent lines, rotating `fa-chevron-right` carets, color-coded Font Awesome icons, and right-aligned monospace badges (`UUID PK`, `BIGINT`, `JSONB`, `142k`).
  2. **Center 3-Tab Multi-Mode Workbench (`1fr`):**
     - **Tab 1 (`Table Data · 142,840 rows`):** Top filter bar (`Node / Host` & `Status` selects calling `filterAppTreeRows()`), 8 boundary-node rows with `4px` left status bars (`.tr-status-ok`, `.tr-status-warn`), and a bottom 4-cell **TimescaleDB Hypertable & Gorilla Compression KPI Strip** (`.va-tree-kpi-strip`).
     - **Tab 2 (`Column Spec & Indexes`):** Column specification table + copyable PostgreSQL 16 / TimescaleDB `CREATE TABLE` DDL block.
     - **Tab 3 (`Query & AST Preview`):** Split SQL query editor + instant tabular execution timing ledger (`1.4 ms · Index Scan`).
  3. **Right Contextual Object & FK Inspector (`.va-tree-inspector`, `280px`):** Displays selected table/column cardinality, foreign-key lineage, and JSONB payload preview.
