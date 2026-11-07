# Gate 0: Pre-Edit Output Contract, Brownfield Project Lock (`.visual-lock.json`) & Autonomous Compiler (`v6.0`)

## 1. Pre-Edit 4-Field Output Contract, Content-Only Mode Lock & Brownfield Protection Law

Before modifying or generating any UI file, declare the compact **4-Field Output Contract** and enforce **Content-Only Preservation** and **Atomic Staging**:
1. **Pre-Edit 4-Field Output Contract:**
   - `Execution Mode`: `Full Assembly` (new view/tier) | `Content-Only` (updating copy, metrics, or rows on an existing page)
   - `Target Tier & Nav`: e.g., `11. App-4 (N1)` or `04. Doc-4B (N3)`
   - `Surface & Density`: e.g., `S1 Pure White · D2 Balanced · C3 Expressive · Rounded (12px)`
   - `Verification Gate`: `verify_visual_contract.py --check-docs` + `408-permutation DOM audit`
2. **Content-Only Mode Preservation Lock & Atomic Staging Rule:**
   - When `Execution Mode = Content-Only`, preserve **100% of existing CSS and layout structure** unless the new content creates a measured fit defect.
   - Always validate generated HTML/CSS with `scripts/verify_visual_contract.py` before overwriting a working artifact so a failed check never leaves a broken UI.
3. **Brownfield Protection Law (`.visual-lock.json` — `Mode M1` & `Mode M2`):**
   - **When `.visual-lock.json` exists (`Mode M1`):** Treat `color_theme`, `card_chrome`, `layout_shells`, and `locked_invariants` as immutable invariants. If the user asks to *"make the view more compact"*, ONLY adjust the Orthogonal Density Dial (`D1` $\rightarrow$ `D4`).
   - **When working on an unlocked existing repo (`Mode M2`):** Offer to generate `.visual-lock.json` capturing its current palette, typography, corner geometry, and view topology before applying targeted changes.

### Canonical `.visual-lock.json` Schema (`v6.0` Workspace Planner Reference Lock)

```json
{
  "$schema": "https://visual-architecture.local/schemas/visual-lock-v6.0.json",
  "project": "Workspace Planner",
  "mode": "M1_PRESERVE_AND_TUNE",
  "archetype_tier": "11. App-4 (Task & Calendar Planner)",
  "color_theme": "S1_PURE_WHITE_ALABASTER",
  "default_density": "D2_BALANCED_WORKSPACE",
  "color_restraint": "C3_MODERN_EXPRESSIVE",
  "corner_geometry": "ROUNDED_12PX_CONCENTRIC",
  "navigation_topology": "N1_FULL_HEIGHT_LEFT_SIDEBAR",
  "typography_scale": "V60_UNIFIED_7STEP_11PX_FLOOR_MAX4_PER_CARD",
  "surface_palette": {
    "bg_canvas": "#F8FAFC",
    "bg_card": "#FFFFFF",
    "border_hairline": "#E2E8F0"
  },
  "locked_invariants": [
    "NEVER replace the Alabaster/White card surface with a dark-mode terminal",
    "NEVER remove drag handles or resize grips from Dashboard widgets",
    "NEVER collapse the 3-zone Task & Calendar Planner layout into a single-screen Kanban"
  ]
}
```

---

## 2. Autonomous Zero-Guidance Content-to-UI Compiler (`Mode M3` Default)

When a user provides raw domain content (markdown notes, API specs, container/node lists, tasks, SQL schemas, or Home Assistant entities) without specifying UI controls, **do not block on questions**—deterministically classify the input and compose the matching Tier, Navigation Shell (`N0`–`N4`), Pure White (`S1`) surface, Unified 7-Step Typography (`--ts-xs: 11px` floor .. `--ts-display`), and signature component blocks:

| # | Input Content Signature | Target Tier & Nav | Mandatory Intra-Page Component Building Blocks |
| :-: | :--- | :--- | :--- |
| **1** | **Long-Form Prose / RFC / Math / Runbook** | `01. Doc-1` (`N1`), `02. Doc-2` (`N0`), `03. Doc-3` (`N0`), or `05. Doc-4A` (`N1`) | `text-wrap: balance` headings, `.va-breakout-grid` (`68ch–74ch` prose + wide tables), `.doc1-mobile-toc-bar` above `.doc1-kicker-text` (`0px` left-axis drift), theme-aware `.va-mermaid-figure`, and (`Doc-4A`) split code runbook |
| **2** | **Skill / CLI / API / SDK Reference** | `04. Doc-4B` (`N3`) | **2-Level Numbered Sidebar** (`1.0`, `2.1 /command`), **6-Stage Numbered Flow Spine (`.va-flow-spine`)** with `/slash-command` pills, and **Situation $\rightarrow$ Action Decision-Router Table** with `[View Full Table]` expand toggle |
| **3** | **Fleet / Container / Node Inventory & Quota Telemetry** *(Portainer / Monarch / LibreNMS shape)* | `08. Bridge-2` (`N2`), `09. App-2` (`N1`), or `12. App-3` (`N2`) | **Scoped Context Box (`.va-scoped-nav-box`)**, **3-Zone Fleet Cards (`.va-fleet-card-3zone`)**, **2×3 Icon-Well Summary Tiles (`.va-icon-well-tile`)**, **Bulk-Action Toolbar (`.va-bulk-action-bar`)**, **Proportional Ranking Rows (`.va-prop-bar-row`)**, **Expected-Pace Progress Bars (`.va-pace-bar` + `.va-invariant-strip`)**, **5-Segment Threshold Gauge (`.va-threshold-gauge`)**, and **Cumulative Trajectory Chart (`.va-trajectory-chart`)** |
| **4** | **Tasks / Planner / Daily Pacing & Biometrics** *(OpenTodo / Fitbit / Linear shape)* | `11. App-4` (`N1`) or `13. App-5` (`N1`) | **1-Sentence Status Briefing (`.va-status-briefing`)**, **Tinted Section Header Bars (`.va-task-group-bar`)**, **Priority-Ring Task Rows (`.va-priority-ring`)** + `[Close the day]`, **Time-Grid Blocks (`.va-timegrid-block`)**, **Self-Filling Progress Capsules (`.va-fill-capsule`)**, **Target-Corridor 7-Day Sparklines (`.va-corridor-sparkline`)**, and **Connected State Hypnogram (`.va-state-hypnogram`)** |
| **5** | **Schema / Tree / Logs** *(App-Tree / Grafana shape)* | `14. App-Tree` (`N1`) or `10. App-1` (`N1`) | Coupled 3-pane explorer (`.va-tree-pane` preserved as a `228px–260px` labeled schema tree on `>=641px`), `.va-th-title` top-aligned table headers, `28px` edge collapse tabs, and 3-column row inspection |
| **6** | **Smart Home / Wall Kiosk / Companion** | `15. HA-1` (`N0`), `16. HA-2` (`N1`), or `17. HA-3` (`N4`) | `HA-1` Monet canvas + Frosted Glass HUD (`.ha1-glass-hud`), `HA-2` room cards + `.va-prop-bar-row` circuit load breakdown, `HA-3` circular quick-toggle matrix & split-capsule thumb bar |

---

## 3. Single-Pass 6-Question Intake Scorecard (Interactive Greenfield `Mode M4`)

When a user explicitly asks to configure visual parameters before building, present this compact scorecard so they can reply with a single 6-code shorthand (e.g., `11, D2, S1, C3, rounded, N1` or `14, D3, S4, C2, subtle, N1`):

> **Visual Architecture v6.0 Intake Scorecard** *(Reply with 6 codes, e.g. `11, D2, S1, C3, rounded, N1` or `14, D3, S1, C2, subtle, N1`):*
> 1. **Deliverable Archetype (`01`–`17`):**
>    - *Docs & Decks:* `01` Academic Monograph · `02` Executive Memo (`BLUF` + Mermaid) · `03` Normative RFC (+ Mermaid FSM) · `04` SDK/Skill Reference (Flow Spine + Router Table) · `05` Split-Pane Runbook (+ Mermaid Seq) · `06` Parametric Worksheet · `07` Briefing Stage
>    - *Data, Workspaces & Explorers:* `08` High-Density Fleet/Data Table (`1px` Grid + Bulk Toolbar) · `09` Live Metrics & Time-Series Console · `10` Compact Issue & Ticket Tracker · `11` Task & Calendar Planner (Status Briefing + Priority Rings + Time-Grid) · `12` KPI & Fleet Bento Dashboard (3-Zone Fleet Cards + `2x3` Icon-Well Tiles) · `13` Daily Pacing & Wellness Planner (+ Readiness Ring Hero) · `14` **`App-Tree` Schema, Tree & File Explorer Workbench**
>    - *Home Assistant:* `15` HA-1 Ambient Wall Kiosk (Monet + Frosted Glass) · `16` HA-2 Room-First Wall Control Panel · `17` HA-3 Crease-Aware Foldable & Phone Controller
> 2. **Compactness / Density (`D1`–`D4`):** `D1` Relaxed · `D2` Balanced *(Default)* · `D3` Compact · `D4` Ultra-Dense Hairline
> 3. **Color Theme (`S1–S4`):** `S1` Pure White *(Default across all 17 tiers)* · `S2` Warm Paper · `S3` Dark Paper · `S4` Obsidian Dark
> 4. **Color Policy (`C1–C3`):** `C1` Quiet Cockpit (Monochrome) · `C2` Semantic Accents · `C3` **Modern Expressive** (1 Tinted Hero Card + `.va-icon-well` Soft Tints)
> 5. **Corner Geometry (`auto|sharp|subtle|rounded|soft`):** `auto` Tier Default · `sharp` (`0px`) · `subtle` (`6px`) · `rounded` (`12px`) · `soft` (`18px`)
> 6. **Native Navigation Topology (`N0`–`N4`):**
>    - `N0` **Zero-Chrome Kiosk / Ambient Canvas** (`07. Deck-1`, `15. HA-1` — `0px` nav bars)
>    - `N1` **Full-Height Left Sidebar / Spine** (`10. App-1`, `11. App-4`, `13. App-5`, `14. App-Tree`, `16. HA-2` — `220px` collapsible to `60px` via `.va-hamburger-btn`)
>    - `N2` **Single Top Command Bar** (`08. Bridge-2`, `12. App-3` — single `42px` borderless `.va-tab-link` bar)
>    - `N3` **Hybrid Enterprise L-Shell** (`04. Doc-4B` — `42px` global top bar + `220px` local left section tree)
>    - `N4` **Sticky Bottom Thumb-Zone Dock** (`17. HA-3` and `R5` `390px` mobile — `40px` desktop pill / `52px` mobile 5-slot thumb bar)

