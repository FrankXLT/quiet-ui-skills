# Reference 00: Pre-Edit Output Contract, Project Lock (`.visual-lock.json`) & Zero-Guidance Content Routing

## 0. Self-Immutability Lock & Gate 0 Customization Onboarding Flow

1. **Self-Immutability Lock (Core & Starters are Read-Only):**
   AI agents and automated tools are strictly forbidden from modifying or writing to `skills/quiet-ui/`, `skills/quiet-ui-diagrams/`, `customizations/personal-starter/`, or `customizations/brand-starter/` during user customization workflows. All user designs, customizations, and project assets MUST be created inside a dedicated project directory (e.g., `customizations/<name>/` or `<workspace>/`).

2. **Gate 0 Customization Onboarding Flow:**
   - **Step 1 — Scope & Target Directory:** Ask whether the customization is for **personal use** (17 tiers: documents, workspaces, wellness biometrics, and Home Assistant ambient wall kiosks) or **brand/team use** (13 product & doc tiers: omitting residential smart-home tiers and Monet media bloat). Confirm target directory `customizations/<name>/`.
   - **Step 2 — Clone Starter:** Clone the chosen blueprint (`personal-starter` or `brand-starter`) into `customizations/<name>/`.
   - **Step 3 — Inspiration-Driven Extraction & Compilation:** Ask for **1–3 inspirational examples** (screenshots, design URLs, PDF mockups, or reference sites) plus any hard brand hexes/fonts. Semantically extract visual traits into `customization.json`, update `intent/00..03.md` and `styles/overrides.css`, then run `python3 customizations/scripts/build_showcase.py customizations/<name>` and `python3 customizations/scripts/verify_customization.py customizations/<name> --check-immutability`.

---

## 1. Pre-Edit 4-Field Output Contract, Content-Only Lock & Existing-Project Protection

Before modifying or generating any UI file, declare the compact **4-Field Output Contract** and enforce **Content-Only Preservation** and **Atomic Staging**:
1. **Pre-Edit 4-Field Output Contract:**
   - `Execution Mode`: `Full Assembly` (new view/tier) | `Content-Only` (updating copy, metrics, or rows on an existing page)
   - `Target Tier & Nav`: e.g., `11. App-4 (N1)` or `04. Doc-4B (N3)`
   - `Surface & Density`: e.g., `Pure White (white) · Balanced (d2) · Expressive (c3) · Rounded (12px)`
   - `Verification Gate`: `verify_visual_contract.py --check-docs` + `408-permutation DOM audit`
2. **Content-Only Preservation Lock & Atomic Staging:**
   - When `Execution Mode = Content-Only`, preserve **100% of existing CSS and layout structure** unless the new content creates a measured fit defect.
   - Always validate generated HTML/CSS with `scripts/verify_visual_contract.py` before overwriting a working artifact so a failed check never leaves a broken UI.
3. **Existing-Project Protection (`.visual-lock.json`):**
   - **When `.visual-lock.json` exists:** Treat `color_theme`, `card_chrome`, `layout_shells`, and `locked_invariants` as immutable invariants. If the user asks to *"make the view more compact"*, only adjust the Orthogonal Density Dial (`d1` $\rightarrow$ `d4`).
   - **When working on an unlocked existing repository:** Offer to generate `.visual-lock.json` capturing its current palette, typography, corner geometry, and view topology before applying targeted changes.

### Example `.visual-lock.json` Schema

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

## 2. Zero-Guidance Content-to-UI Router

When a user provides raw domain content (markdown notes, API specs, container/node lists, tasks, SQL schemas, or smart-home entities) without specifying UI controls, **do not block on boilerplate questions**—automatically classify the input and compose the matching Tier, Navigation Shell (`N0`–`N4`), default Pure White (`data-theme="white"`) surface, Unified 7-Step Typography (`--ts-xs: 11px` floor .. `--ts-display`), and component blocks:

| # | Input Content Signature | Target Tier & Nav | Mandatory Intra-Page Component Building Blocks |
| :-: | :--- | :--- | :--- |
| **1** | **Long-Form Prose / RFC / Math / Runbook** | `01. Doc-1` (`N1`), `02. Doc-2` (`N0`), `03. Doc-3` (`N0`), or `05. Doc-4A` (`N1`) | `text-wrap: balance` headings, `.va-breakout-grid` (`68ch–74ch` prose + wide tables), `.doc1-mobile-toc-bar` above `.doc1-kicker-text` (`0px` left-axis drift), theme-aware `.va-mermaid-figure`, and (`Doc-4A`) split code runbook |
| **2** | **Skill / CLI / API / SDK Reference** | `04. Doc-4B` (`N3`) | **2-Level Numbered Sidebar** (`1.0`, `2.1 /command`), **6-Stage Numbered Flow Spine (`.va-flow-spine`)** with `/slash-command` pills, and **Situation-to-Tier Decision Table** with `[View Full Table]` expand toggle |
| **3** | **Fleet / Container / Node Inventory & Quota Telemetry** | `08. Bridge-2` (`N2`), `09. App-2` (`N1`), or `12. App-3` (`N2`) | **Scoped Context Rails (`.va-scoped-nav-box`)**, **3-Zone Fleet Summary Cards (`.va-fleet-card-3zone`)**, **Icon-Well Summary Tiles (`.va-icon-well-tile`)**, **Bulk-Action Table Toolbars (`.va-bulk-action-bar`)**, **Proportional Share Bars (`.va-prop-bar-row`)**, **Expected-Pace Bars (`.va-pace-bar` + `.va-invariant-strip`)**, **5-Segment Threshold Gauges (`.va-threshold-gauge`)**, and **Cumulative Trajectory Charts (`.va-trajectory-chart`)** |
| **4** | **Tasks / Planner / Daily Pacing & Biometrics** | `11. App-4` (`N1`) or `13. App-5` (`N1`) | **Daily Status Briefings (`.va-status-briefing`)**, **Section Header Bars (`.va-task-group-bar`)**, **Priority-Ring Task Rows (`.va-priority-ring`)** + `[Close the day]`, **Left-Accent Time Blocks (`.va-timegrid-block`)**, **Self-Filling Progress Capsules (`.va-fill-capsule`)**, **Target-Corridor Sparklines (`.va-corridor-sparkline`)**, and **Multi-Track State Timelines (`.va-state-hypnogram`)** |
| **5** | **Schema / Tree / Logs** | `14. App-Tree` (`N1`) or `10. App-1` (`N1`) | Coupled 3-pane explorer (`.va-tree-pane` preserved as a `228px–260px` labeled schema tree on `>=641px`), `.va-th-title` top-aligned table headers, `28px` edge collapse tabs, and 3-column row inspection |
| **6** | **Smart Home / Wall Kiosk / Companion** | `15. HA-1` (`N0`), `16. HA-2` (`N1`), or `17. HA-3` (`N4`) | `HA-1` fine-art canvas + Frosted Glass HUD (`.ha1-glass-hud`), `HA-2` room cards + `.va-prop-bar-row` circuit load breakdown, `HA-3` circular quick-toggle matrix & split-capsule thumb bar |

---

## 3. Interactive 6-Option Configuration Scorecard (Optional Manual Override)

When a user explicitly asks to choose visual parameters before building, present this compact scorecard so they can reply with a single 6-code shorthand (e.g., `11, d2, white, c3, rounded, N1`):

> **Quiet UI Configuration Scorecard** *(Reply with 6 codes, e.g. `11, d2, white, c3, rounded, N1`):*
> 1. **Deliverable Archetype (`01`–`17`):**
>    - *Docs & Decks:* `01` Academic Monograph · `02` Executive Memo (`BLUF` + Mermaid) · `03` Normative RFC (+ Mermaid FSM) · `04` SDK/Skill Reference (Flow Spine + Decision Table) · `05` Split-Pane Runbook (+ Mermaid Seq) · `06` Parametric Worksheet · `07` Briefing Stage
>    - *Data, Workspaces & Explorers:* `08` High-Density Fleet/Data Table (`1px` Grid + Bulk Toolbar) · `09` Live Metrics & Time-Series Console · `10` Compact Issue & Ticket Tracker · `11` Task & Calendar Planner (Status Briefing + Priority Rings + Time Blocks) · `12` KPI & Fleet Bento Dashboard · `13` Daily Pacing & Wellness Planner · `14` `App-Tree` Schema, Tree & File Explorer Workbench
>    - *Home Assistant:* `15` HA-1 Ambient Wall Kiosk · `16` HA-2 Room-First Wall Control Panel · `17` HA-3 Crease-Aware Foldable & Phone Controller
> 2. **Compactness / Density (`d1`–`d4`):** `d1` Relaxed · `d2` Balanced *(Default)* · `d3` Compact · `d4` Ultra-Dense Hairline
> 3. **Surface Theme (`white|paper|dark-paper|dark`):** `white` Pure White *(Default)* · `paper` Warm Paper · `dark-paper` Warm Sepia Dark · `dark` Carbon Dark
> 4. **Color Policy (`c1–c3`):** `c1` Quiet Monochrome · `c2` Semantic Accents · `c3` Modern Expressive (1 Tinted Hero Card + `.va-icon-well` Soft Tints)
> 5. **Corner Geometry (`auto|sharp|subtle|rounded|soft`):** `auto` Tier Default · `sharp` (`0px`) · `subtle` (`6px`) · `rounded` (`12px`) · `soft` (`18px`)
> 6. **Navigation Shell (`N0`–`N4`):** `N0` Zero-Chrome Kiosk · `N1` Full-Height Left Sidebar · `N2` Single Top Command Bar · `N3` Hybrid Top + Left L-Shell · `N4` Bottom Thumb Dock
