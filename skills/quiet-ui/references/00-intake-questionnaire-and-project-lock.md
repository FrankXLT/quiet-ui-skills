# Reference 00: Pre-Edit Output Contract, Project Lock (`.visual-lock.json`) & Zero-Guidance Content Routing

## 0. Self-Immutability Lock & Gate 0 Customization Onboarding Flow

1. **Self-Immutability Lock (Core & Starters are Read-Only):**
   AI agents and automated tools are strictly forbidden from modifying or writing to `skills/quiet-ui/`, `skills/quiet-ui-diagrams/`, `customizations/personal-starter/`, or `customizations/brand-starter/` during user customization workflows. All user designs, customizations, and project assets MUST be created inside a dedicated project directory (e.g., `customizations/<name>/` or `<workspace>/`).

2. **Gate 0 Customization Onboarding Flow:**
   - **Step 1 — Scope & Target Directory:** Ask whether the customization is for **personal use** (16 tiers: documents, workspaces, telemetry, optical viewport HUD, and tactile subsystem consoles) or **brand/team use** (13 product & doc tiers: omitting specialized mission-control tiers). Confirm target directory `customizations/<name>/`.
   - **Step 2 — Clone Starter:** Clone the chosen blueprint (`personal-starter` or `brand-starter`) into `customizations/<name>/`.
   - **Step 3 — Inspiration-Driven Extraction & Compilation:** Ask for **1–3 inspirational examples** (screenshots, design URLs, PDF mockups, or reference sites) plus any brand hexes/fonts. Semantically extract visual traits into `customization.json`, update `intent/00..03.md` and `styles/overrides.css`, then run `python3 customizations/scripts/build_showcase.py customizations/<name>` and `python3 customizations/scripts/verify_customization.py customizations/<name> --check-immutability`.

---

## 1. Pre-Edit 4-Field Output Contract, Content-Only Lock & Existing-Project Protection

1. **Pre-Edit 4-Field Output Contract:** Declare before writing code:
   - `Execution Mode`: `Full Assembly` (new view/tier) | `Content-Only` (updating copy, metrics, or rows on an existing page)
   - `Target Tier & Nav`: e.g., `11. App-4 (N1)` or `04. Doc-4B (N3)`
   - `Surface & Density`: e.g., `Pure White (white) · Balanced (d2) · Expressive (c3) · Rounded (12px)`
   - `Verification Gate`: `verify_visual_contract.py --check-docs` + Stage Portal CDP validation
2. **Content-Only Preservation Lock & Atomic Staging:**
   - When `Execution Mode = Content-Only`, preserve 100% of existing CSS and layout structure unless new content causes a measured fit defect.
   - Always validate generated HTML/CSS before overwriting a working artifact so a failed check never leaves broken UI.
3. **Existing-Project Protection (`.visual-lock.json`):**
   - When `.visual-lock.json` exists, treat `color_theme`, `card_chrome`, `layout_shells`, and `locked_invariants` as immutable invariants. Only adjust the Orthogonal Density Dial (`d1` $\rightarrow$ `d4`).

```json
{
  "$schema": "https://visual-architecture.local/schemas/visual-lock.json",
  "project": "Workspace Planner",
  "mode": "PRESERVE_AND_TUNE",
  "archetype_tier": "11. App-4 (Task & Calendar Planner)",
  "color_theme": "PURE_WHITE_ALABASTER",
  "default_density": "D2_BALANCED_WORKSPACE",
  "color_restraint": "C3_MODERN_EXPRESSIVE",
  "corner_geometry": "ROUNDED_12PX_CONCENTRIC",
  "navigation_topology": "N1_FULL_HEIGHT_LEFT_SIDEBAR",
  "typography_scale": "UNIFIED_7STEP_11PX_FLOOR_MAX4_PER_CARD",
  "surface_palette": { "bg_canvas": "#F8FAFC", "bg_card": "#FFFFFF", "border_hairline": "#E2E8F0" },
  "locked_invariants": [
    "NEVER replace the Alabaster/White card surface with a dark-mode terminal",
    "NEVER collapse the 3-zone Task & Calendar Planner layout into a single-screen Kanban"
  ]
}
```

---

## 2. Zero-Guidance Content-to-UI Router

When raw domain content is provided without UI instructions, automatically classify input and compose matching Tier, Nav Shell (`N0`–`N4`), Pure White (`data-theme="white"`), and typography:

| # | Input Content Signature | Target Tier & Nav | Mandatory Intra-Page Building Blocks |
| :-: | :--- | :--- | :--- |
| **1** | **Long-Form Prose / RFC / Math / Runbook** | `01. Doc-1` (`N1`), `02. Doc-2` (`N0`), `03. Doc-3` (`N0`), `05. Doc-4A` (`N1`) | `text-wrap: balance` headings, `.va-breakout-grid` (`68ch–74ch`), `.doc1-mobile-toc-bar` above kicker (`0px` left-axis drift), `.va-mermaid-figure`, split code runbook |
| **2** | **Skill / CLI / API / SDK Reference** | `04. Doc-4B` (`N3`) | **2-Level Numbered Sidebar**, **6-Stage Numbered Flow Spine (`.va-flow-spine`)** with `/slash-command` pills, and **Situation-to-Tier Decision Table** |
| **3** | **Fleet / Hardware Inventory & Telemetry** | `08. Bridge-2` (`N2`), `09. App-2` (`N1`), `12. App-3` (`N2`) | **Scoped Context Rails (`.va-scoped-nav-box`)**, **3-Zone Fleet Cards (`.va-fleet-card-3zone`)**, **Bulk-Action Toolbars (`.va-bulk-action-bar`)**, **Proportional Share Bars (`.va-prop-bar-row`)**, **Expected-Pace Bars (`.va-pace-bar`)**, **5-Segment Threshold Gauges (`.va-threshold-gauge`)**, **Cumulative Trajectory Charts (`.va-trajectory-chart`)** |
| **4** | **Tasks / Planner / Daily Pacing & Workload** | `11. App-4` (`N1`), `13. App-5` (`N1`) | **Daily Status Briefings (`.va-status-briefing`)**, **Section Header Bars (`.va-task-group-bar`)**, **Priority-Ring Task Rows (`.va-priority-ring`)**, **Left-Accent Time Blocks (`.va-timegrid-block`)**, **Self-Filling Progress Capsules (`.va-fill-capsule`)**, **Target-Corridor Sparklines (`.va-corridor-sparkline`)**, **State Timelines (`.va-state-hypnogram`)** |
| **5** | **Schema / Tree / Logs** | `14. App-Tree` (`N1`), `10. App-1` (`N1`) | Coupled 3-pane explorer (`.va-tree-pane` `228px–260px` schema tree on `>=641px`), `.va-th-title` top-aligned headers, `28px` edge tabs, 3-column row inspection |
| **6** | **Optical HUD / Tactile Console** | `15. HUD-1` (`N0`), `16. Ctrl-1` (`N1`) | `HUD-1` `>=65%` open optical viewport + smoked glass pods (`.va-hud-pod`), `Ctrl-1` subsystem rack + 2-step guarded effector controls (`ARM` -> `EXECUTE`) |

---

## 3. Interactive 6-Option Configuration Scorecard

> **Quiet UI Configuration Scorecard** *(Reply with 6 codes, e.g. `11, d2, white, c3, rounded, N1`):*
> 1. **Deliverable Archetype (`01`–`16`):**
>    - *Docs & Decks:* `01` Monograph · `02` Memo (`BLUF`) · `03` RFC · `04` SDK Reference · `05` Runbook · `06` Worksheet · `07` Briefing Stage
>    - *Data, Workspaces & Explorers:* `08` Fleet Table · `09` Time-Series Console · `10` Issue Tracker · `11` Task Planner · `12` KPI Bento · `13` Daily Pacing · `14` Schema Explorer
>    - *Optical HUD & Tactile Consoles:* `15` HUD-1 Optical Viewport · `16` Ctrl-1 Tactile Subsystem Console
> 2. **Compactness / Density (`d1`–`d4`):** `d1` Relaxed · `d2` Balanced *(Default)* · `d3` Compact · `d4` Ultra-Dense Hairline
> 3. **Surface Theme (`white|paper|dark-paper|dark`):** `white` Pure White *(Default)* · `paper` Warm Paper · `dark-paper` Sepia Dark · `dark` Carbon Dark
> 4. **Color Policy (`c1–c3`):** `c1` Monochrome · `c2` Semantic Accents · `c3` Expressive (1 Hero Card + `.va-icon-well` Tints)
> 5. **Corner Geometry (`auto|sharp|subtle|rounded|soft`):** `auto` Default · `sharp` (`0px`) · `subtle` (`6px`) · `rounded` (`12px`) · `soft` (`18px`)
> 6. **Navigation Shell (`N0`–`N4`):** `N0` Kiosk · `N1` Left Sidebar · `N2` Top Command Bar · `N3` Hybrid L-Shell · `N4` Bottom Thumb Dock
