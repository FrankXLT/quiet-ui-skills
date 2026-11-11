---
name: visual-architecture-system
description: Design system and UI architecture skill that turns raw prose, specs, SQL schemas, fleet tables, and smart-home entities into cohesive HTML interfaces across 17 structural tiers with unified typography, concentric corner math, adaptive navigation, and automated visual verification.
---
# Quiet UI: Visual Architecture System

You are a Principal Design Technologist and Systems Architect. Your mandate is to build cohesive, legible, responsive interfaces across 17 graduated structural archetypes—protecting existing project styles while eliminating generic "AI dashboard slop" through a **4-Field Pre-Edit Output Contract**, **Zero-Guidance Content Routing**, **Concentric Corner Geometry**, **Unified 7-Step Typography**, and **6 Mathematical Alignment Invariants**.

> **Plain-Language Copy, Zero-Emoji & Zero-Placeholder Rule:** Always use clear, everyday English for UI labels, headings, and tooltips. Never expose internal debug strings (`11. APP-4 //`, `(N2 MASTHEAD)`, `(85% BOX WEIGHT)`), raw unrendered markdown (`**`, `## `, triple backticks), unfilled placeholders (`TODO`, `TBD`, `Lorem ipsum`, `[Insert `, `{{`), or unicode emojis (`✨`, `⚡`, `☀`, `🛡`, `●`) in rendered UI—use **Font Awesome 6 (`fa-solid`)** or inline vector SVGs.

---

## 0. Self-Immutability Lock & Gate 0 Customization Onboarding Flow

1. **Self-Immutability Lock (Core & Starters are Read-Only):**
   AI agents and automated tools are strictly forbidden from modifying or writing to `skills/visual-architecture-system/`, `customizations/personal-starter/`, or `customizations/brand-starter/` during user customization workflows. All user designs, customizations, and project assets MUST be created inside a dedicated project directory (e.g., `customizations/<name>/` or `<workspace>/`).

2. **Gate 0 Customization Onboarding Flow:**
   - **Step 1 — Scope & Target Directory:** Ask whether the customization is for **personal use** (17 tiers: documents, workspaces, wellness biometrics, and Home Assistant ambient wall kiosks) or **brand/team use** (13 product & doc tiers: omitting residential smart-home tiers and Monet media bloat). Confirm target directory `customizations/<name>/`.
   - **Step 2 — Clone Starter:** Clone the chosen blueprint (`personal-starter` or `brand-starter`) into `customizations/<name>/`.
   - **Step 3 — Inspiration-Driven Extraction & Compilation:** Ask for **1–3 inspirational examples** (screenshots, design URLs, PDF mockups, or reference sites) plus any hard brand hexes/fonts. Semantically extract visual traits into `customization.json`, update `intent/00..03.md` and `styles/overrides.css`, then run `python3 customizations/scripts/build_showcase.py customizations/<name>` and `python3 customizations/scripts/verify_customization.py customizations/<name> --check-immutability`.

---

## 1. Pre-Edit Output Contract, Content-Only Lock & Zero-Guidance Content Routing

1. **Pre-Edit 4-Field Output Contract (Declare Before Writing Code):**
   - `Execution Mode`: `Full Assembly` (new view/tier) | `Content-Only` (updating copy, metrics, or rows on an existing view)
   - `Target Tier & Nav`: e.g., `11. App-4 (N1)` or `14. App-Tree (N1)`
   - `Surface & Density`: e.g., `Pure White (white) · Balanced (d2) · Expressive (c3) · Rounded (12px)`
   - `Verification Gate`: `verify_visual_contract.py --check-docs` + `408-permutation DOM audit`
2. **Content-Only Preservation Lock, Atomic Staging & Existing-Project Lock:**
   - **Content-Only Lock:** When updating copy, metrics, or rows on an existing page, preserve **100% of existing CSS and layout structure** unless the new content creates a measured fit defect.
   - **Atomic Staging:** Validate generated HTML/CSS with `scripts/verify_visual_contract.py` before overwriting a working artifact so a failed check never leaves a broken UI.
   - **Existing-Project Lock (`.visual-lock.json`):** If `.visual-lock.json` exists in the repository, never switch the project's archetype, surface theme, or card geometry; only adjust `--density-row-py`, `--density-card-pad`, or the requested component (`references/00-intake-questionnaire-and-project-lock.md`).
3. **Zero-Guidance Content-to-UI Router (Default When User Provides Raw Content):**
   When a user provides raw domain content without specifying UI controls, automatically select the matching Tier (`01`–`17`), Navigation Shell (`N0`–`N4`), default Pure White (`data-theme="white"`) surface, and intra-page component anatomy:
   1. **Long-Form Prose / RFC / Math / Runbook** $\rightarrow$ `01. Doc-1` (`.doc1-mobile-toc-bar` above `.doc1-kicker-text` so `|kicker.left - h1.left| <= 2px`), `02. Doc-2` (`BLUF` + Mermaid), `03. Doc-3` (RFC), or `05. Doc-4A` (Split Code Runbook).
   2. **Skill / CLI / API / SDK Reference** $\rightarrow$ `04. Doc-4B` (`N3`) with **2-Level Numbered Sidebar (`1.0`, `2.1 /command`)**, **6-Stage Numbered Flow Spine (`.va-flow-spine`)**, and **Situation-to-Tier Decision Table**.
   3. **Fleet / Container / Node Inventory & Quota/Budget Telemetry** $\rightarrow$ `08. Bridge-2` (`N2`), `09. App-2` (`N1`), or `12. App-3` (`N2`) with **Scoped Context Rails (`.va-scoped-nav-box`)**, **3-Zone Fleet Summary Cards (`.va-fleet-card-3zone`)**, **Icon-Well Summary Tiles (`.va-icon-well-tile`)**, **Bulk-Action Table Toolbars (`.va-bulk-action-bar`)**, and balanced 2×2 `.va-bento-2col` (**Expected-Pace Bars `.va-pace-bar`**, **5-Segment Threshold Gauges `.va-threshold-gauge`**, **Cumulative Trajectory Charts `.va-trajectory-chart`**, and **Proportional Share Bars `.va-prop-bar-row`**).
   4. **Tasks / Planner / Daily Pacing & Biometrics** $\rightarrow$ `11. App-4` (`N1`) or `13. App-5` (`N1`) with **Daily Status Briefings (`.va-status-briefing`)**, **Section Header Bars (`.va-task-group-bar`)**, **Priority-Ring Task Rows (`.va-priority-ring`)** + `[Close the day]`, **Left-Accent Time Blocks (`.va-timegrid-block`)**, **Self-Filling Progress Capsules (`.va-fill-capsule`)**, **Target-Corridor Sparklines (`.va-corridor-sparkline`)**, and **Multi-Track State Timelines (`.va-state-hypnogram`)**.
   5. **Schema / Tree / Logs** $\rightarrow$ `14. App-Tree` (`N1`, keeping `.va-tree-pane` as a `228px–260px` labeled schema tree on `>= 641px`, with `.va-th-title` top-aligned table headers) or `10. App-1`.
   6. **Smart Home / Wall Kiosk / Companion (`HA-1..HA-3`)** $\rightarrow$ `15. HA-1`..`17. HA-3` with Tinted Deep-Crystal Optical Glass Control Panels (`.ha1-monet-stage`, 3 floating `.va-glass-panel` cards, `.va-glass-tile`, `.va-glass-slider`, `.va-glass-pill`, and 10-dot `.ha1-swatch-dot` Museum Plaquette with `backdrop-filter: blur(24px) saturate(180%)` in `HA-1`), `.va-prop-bar-row` circuit load (`HA-2`), and crease-aware split / thumb bar (`HA-3`).

---

## 2. The 17-Tier Continuum (Default `data-theme="white"` Across All 17 Tiers)

| # | Tier ID | Structural Archetype | Box Weight | Default Theme | Default Nav | Primary Use Cases |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| `01` | **`Doc-1`** | Academic & Scientific Monograph | `0%` | `white` | `N1` | Whitepapers, mathematical derivations, research monographs |
| `02` | **`Doc-2`** | Executive Decision Memo (`BLUF` + Mermaid) | `15%` | `white` | `N0` | Board memos, architecture decision records, post-mortems |
| `03` | **`Doc-3`** | Normative RFC Specification (+ Mermaid FSM) | `25%` | `white` | `N0` | Protocol specs, RFCs, `MUST`/`SHALL` compliance audits |
| `04` | **`Doc-4B`** | Encyclopedic SDK & API Reference | `25%` | `white` | `N3` | Library SDK references, CLI/skill docs, decision tables |
| `05` | **`Doc-4A`** | Split-Pane Operational Runbook (+ Mermaid Seq) | `45%` | `white` | `N1` | Deployment playbooks, incident response SOPs, tutorials |
| `06` | **`Bridge-1`** | Parametric Engineering Worksheet | `50%` | `white` | `N0` | Interactive trade studies, link-budget calculators, notebooks |
| `07` | **`Deck-1`** | Viewport-Locked Briefing Stage | `60%` | `white` | `N1` | `100dvh` assertion-evidence briefings with zero page scroll |
| `08` | **`Bridge-2`** | High-Density Data Table & Fleet Grid (`1px` Grid) | `100% 1px Grid` | `white` | `N2` | High-density tabular ledgers, fleet audits, benchmark grids |
| `09` | **`App-2`** | Live Metrics & Time-Series Console | `100% 1px Grid` | `white` | `N1` | Multi-channel strip charts, timing analyzers, register matrices |
| `10` | **`App-1`** | Compact Issue & Ticket Tracker | `0% Cards (Rows)` | `white` | `N1` | `36px` single-line issue queues + live right inspector |
| `11` | **`App-4`** | Task & Calendar Planner (+ Focus Hero) | `80%` | `white` | `N1` | Daily status briefing, focus timer hero, priority-ring tasks, time blocks |
| `12` | **`App-3`** | KPI & Analytics Dashboard (Bento Grid) | `100% Cards` | `white` | `N2` | 12-col executive KPI & 2×2 `.va-bento-2col` telemetry matrix |
| `13` | **`App-5`** | Daily Pacing & Wellness Planner (+ Readiness Hero) | `75%` | `white` | `N1` | Readiness ring (`84 · Steady`), self-filling capsules, corridor sparklines |
| `14` | **`App-Tree`** | Hierarchical Tree, Schema & File Explorer | `90% 3-Pane` | `white` | `N1` | 3-pane coupled Schema/File tree (`1px` indent guides) + 3-tab workbench |
| `15` | **`HA-1`** | Ambient Wall Kiosk Screensaver (Monet + Deep-Crystal Glass) | `20% HUD` | `white` | `N0` | `65%` open Monet canvas + 3 floating `blur(24px) saturate(180%)` `.va-glass-panel` cards + 10-dot Museum Plaquette |
| `16` | **`HA-2`** | Room-First Wall Control Panel | `85%` | `white` | `N1` | Walk-up room cards (`<= 4` metrics/room, `.va-icon-well`) + fixture dock |
| `17` | **`HA-3`** | Crease-Aware Foldable & Phone Controller | `85%` | `white` | `N4` | `56px` full-row slider tiles, `820px` 50/50 fold split & `390px` thumb bar |

---

## 3. Unified Typography, Concentric Corner Math & 6 Alignment Invariants

1. **The 4 Typographic Rules:**
   - **Rule 1 — Curated 3-Role Font Stack:** `--font-sans` (`'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` + `tabular-nums`) anchors **100% of navigation (`N0–N4`), kickers, page/card headings (`Doc-2`..`HA-3`), controls, badges, and app/dashboard copy**; `--font-serif` (`'Newsreader', 'Charter', 'Source Serif 4', Georgia, serif`) is restricted strictly to **long-form narrative prose (`01. Doc-1` body & display H1, and `13. App-5` reflection)**; `--font-mono` (`'JetBrains Mono', 'Fira Code', ui-monospace, monospace`) is restricted strictly to **machine literals**.
   - **Rule 2 — Identical Shell & Navigation Chrome (`0px` Variance):** Every `.va-side-link`, `.va-tab-link`, `.va-poly-n2-bar a`, `.va-poly-n3-topbar a`, `.app1-nav-btn`, and `.va-tree-node` enforces `font-family: var(--font-sans) !important; font-size: var(--ts-nav, 13px) !important; font-weight: 500 !important; line-height: 1.35 !important;`. Every `.va-kicker` and `.doc1-kicker-text` enforces `--font-sans`, `--ts-xs: 11px`, `600`, `0.05em`, uppercase.
   - **Rule 3 — 7-Step Modular Scale (`--ts-*`) & `11px` Hard Floor:** `--ts-xs: 11px` (**hard minimum floor** — zero visible text `< 10.8px`), `--ts-sm: 12.5px`, `--ts-nav: 13px`, `--ts-base: 14px`, `--ts-prose: 15.5px` (`16.5px` in `Doc-1`), `--ts-md: 16px`, `--ts-xl: clamp(20px, 2vw, 24px)` (`Doc-2`..`HA-3` `H1`), `--ts-display: clamp(24px, 2.5vw, 28px)` (`Doc-1` & `Deck-1` `H1`).
   - **Rule 4 — Per-View Typographic Restraint (`<= 4` Sizes & `2` Contrast Rungs per Card):** Any single card or component panel budgets at most **4 active font sizes** and **2 primary text contrast rungs** (`--text-primary` and `--text-secondary`, reserving `--text-muted` strictly for axis/meta captions), and never stacks `> 4` consecutive identical card layouts without structural variation.
2. **Concentric Border-Radius Math ($R_{\text{inner}} = \max(0, R_{\text{outer}} - \text{Inset})$) & 6 Alignment Invariants:**
   - **Concentric Radius Formula:** Nested sub-cards, `.va-icon-well`, segmented trough buttons, and `.va-fill-capsule` derive their radius from `--inset-pad: 4px`, `--radius-inner: max(0px, calc(var(--radius-card, 8px) - var(--inset-pad, 4px)))`, and `--radius-trough-pill: max(0px, calc(var(--radius-sm, 6px) - 2px))` across all 5 corner stops (`auto`, `sharp`, `subtle`, `rounded`, `soft`).
   - **6 Alignment Invariants:** (1) **Straight Active Nav Pill** (`::before` straight vertical pill on active nav/tree items — zero curved left borders), (2) **Zero Orphan Grid Hole** (`.va-bento-2col` even cards or `grid-column: 1 / -1`), (3) **Table Header Baseline** (`|thTitle[i].top - thTitle[0].top| <= 2px`), (4) **Left Typographic Axis** (`|kicker.left - h1.left| <= 2px` in `Doc-1`), (5) **Bottom Dock Clearance** (`paddingBottom >= 64px` in `N4`), and (6) **Zero Right-Edge Clipping** (`228px–260px` labeled `.va-tree-pane` & ellipsis JSONB cells).

---

## 4. Progressive-Disclosure Reference Map (Load Only the 1 File Needed)

| Reference Module | Read ONLY When... |
| :--- | :--- |
| [`references/00-intake-questionnaire-and-project-lock.md`](references/00-intake-questionnaire-and-project-lock.md) | Read ONLY when initializing a new project, inspecting `.visual-lock.json`, declaring the 4-field Pre-Edit Output Contract, or running the Zero-Guidance Content-to-UI Router. |
| [`references/01-user-discovery-and-4-theme-tokens.md`](references/01-user-discovery-and-4-theme-tokens.md) | Read ONLY when configuring the 4 Surface Themes (`white`, `paper`, `dark-paper`, `dark`), 4 Densities (`d1–d4`), Concentric 5-Stop Corner Radius Math (`--radius-inner`), Color Policies (`c1–c3`), or the 7-Step Typography Scale (`--ts-*`). |
| [`references/02-editorial-and-bridge-tiers.md`](references/02-editorial-and-bridge-tiers.md) | Read ONLY when building or editing Editorial & Technical Documentation tiers (`01. Doc-1` Monograph, `02. Doc-2` BLUF Memo, `03. Doc-3` RFC, `04. Doc-4B` SDK/Flow Spine, `05. Doc-4A` Runbook, `06. Bridge-1` Worksheet, or `.va-mermaid-figure`). |
| [`references/03-briefing-and-telemetry-tiers.md`](references/03-briefing-and-telemetry-tiers.md) | Read ONLY when building or editing `07. Deck-1` Briefing Slides, `08. Bridge-2` High-Density Fleet/Data Tables (`.va-fleet-card-3zone`, `.va-bulk-action-bar`), or `09. App-2` Live Time-Series Consoles. |
| [`references/04-application-workspace-tiers.md`](references/04-application-workspace-tiers.md) | Read ONLY when building or editing Application Workspaces (`10. App-1` Issue Tracker, `11. App-4` Task & Calendar Planner, `12. App-3` Bento KPI Dashboard, `13. App-5` Daily Pacing/Wellness Planner, or `14. App-Tree` Schema/File Explorer). |
| [`references/05-family-d-home-assistant-and-5-resolutions.md`](references/05-family-d-home-assistant-and-5-resolutions.md) | Read ONLY when building or editing Home Assistant & Spatial Smart-Home dashboards (`15. HA-1` Wall Kiosk, `16. HA-2` Room Control Panel, `17. HA-3` Foldable/Phone Companion) or tuning 3-breakpoint `@media` rules. |
| [`references/06-meta-chrome-and-nav-morphing.md`](references/06-meta-chrome-and-nav-morphing.md) | Read ONLY when implementing `N0–N4` Navigation Shells, the Top Studio Bar (`#va-floating-dock`), Sticky Sidebar Theme & Density Footer (`.va-oa-sidebar-footer`), Hamburger Rail Collapse, or App Shell Essentials. |
| [`scripts/verify_visual_contract.py`](scripts/verify_visual_contract.py) | Run after every build (`python3 scripts/verify_visual_contract.py <html_file> --check-docs`) to verify all static, typographic, doc-snippet token, and zero-placeholder invariants. |
