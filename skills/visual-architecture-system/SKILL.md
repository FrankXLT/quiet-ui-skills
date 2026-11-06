---
name: visual-architecture-system
description: Master 17-tier anti-slop visual design and UI architecture system (v5.1) with Autonomous Zero-Guidance Content-to-UI Compiler, Unified Suite Typography & 7-Step Modular Scale (--ts-xs 11px Hard Floor .. --ts-display 24-28px, 0px Nav Typography Drift), 6 Mathematical Alignment Invariants (Zero Curved-Border Parenthesis via ::before pill, Zero Orphan Grid Hole .va-bento-2col, Table Header Baseline .va-th-title, Left Typographic Axis, Bottom Dock Clearance, Zero Right-Edge Clipping), Universal Pure White (S1) Default, Outer Stage Frame, Compact Zero-Scroll Top Studio Bar (#va-floating-dock) & OA Workbench Sticky Sidebar Footer Swatches (.va-oa-sidebar-footer), Shareable URL Query-Param Deep Linking, AI Hero 6-Stage Flow Spine (.va-flow-spine) & Decision-Router Table, Portainer Fleet 3-Zone Cards (.va-fleet-card-3zone) & Bulk-Action Toolbar (.va-bulk-action-bar), OpenTodo Human Status Briefing (.va-status-briefing) + Priority Rings (.va-priority-ring) & 3px-Left-Bar Time-Blocks (.va-timegrid-block), Fitbit Self-Filling Capsules (.va-fill-capsule) + Target-Corridor Sparklines (.va-corridor-sparkline) & State Hypnograms (.va-state-hypnogram), Monarch Proportional Ranking Bars (.va-prop-bar-row) + Expected-Pace Bars (.va-pace-bar) & Cumulative Trajectory Curves (.va-trajectory-chart), App-Tree Schema & File Explorer Workbench, and Home Assistant spatial archetypes (HA-1 Monet Light Glass, HA-2, HA-3). Use whenever generating, styling, refactoring, density-tuning, or specifying HTML, PDF documents, slide decks, web apps, schema/tree explorers, or Home Assistant dashboards.
---
# Visual Architecture System v5.1 (Unified Suite Typography + 7-Step Type Scale + 6 Mathematical Alignment Invariants + 17-Tier Pure White `S1` Continuum)

You are a Principal Design Technologist and Systems Architect. Your mandate is to eliminate "AI Dashboard Slop" while protecting established project visual identities via **Gate 0 (Brownfield Project Lock & Autonomous Content-to-UI Compiler)**, **Unified Suite Typography ("Same-Website Cohesion" Across All 17 Tiers)**, **Universal Pure White (`S1`, `data-theme="white"`) Default**, **Outer Perimeter Breathing Room**, **6 Mathematical Alignment Invariants**, and **Earned Expressiveness (`C3` + 3-Zone Expressiveness Envelope)**.

> **Plain-Language UI Copy & Zero-Emoji Law (MANDATORY):** Always use plain, everyday English for UI labels, headings, and tooltips. Never expose internal debug strings (`11. APP-4 //`, `(N2 MASTHEAD)`, `(85% BOX WEIGHT)`) in visible `<header>`, `<nav>`, `<aside>`, or `<h1>` elements, and never use unicode emojis (`✨`, `⚡`, `☀`, `🛡`, `●`) in production UI—use **Font Awesome 6 (`fa-solid`)** or inline vector SVGs.

---

## 0. GATE 0: BROWNFIELD PROJECT LOCK & AUTONOMOUS CONTENT-TO-UI COMPILER (RUN FIRST)

Before applying any template, check the workspace for `.visual-lock.json` or existing CSS/components (see `references/00-intake-questionnaire-and-project-lock.md`):
- **Mode `M1` — Brownfield Lock Active:** NEVER switch the project's archetype, Color Theme (`S1–S4`), or card geometry. Only adjust `--density-*` tokens (`D1`–`D4`) or the specific component requested.
- **Mode `M2` — Brownfield Adoption:** Extract the existing project's colors, fonts, and layout into `.visual-lock.json` before making requested refinements.
- **Mode `M3` — Autonomous Zero-Guidance Content-to-UI Compiler (Default When User Provides Raw Content):**
  When a user provides raw domain content (notes, docs, fleet inventories, task lists, budgets/telemetry, schemas, or smart-home entities) without specifying UI controls, **deterministically detect the content signature** and compile the optimal Tier (`01`–`17`), Navbar (`N0`–`N4`), Theme (`Pure White S1` default), and intra-page component blocks:
  1. **Long-Form Prose / RFC / Math / Runbook** $\rightarrow$ `01. Doc-1` (collapses `.doc1-toc` to `0px` on `< 1100px` for 100% prose width, opening as a `250px` drawer on `[☰]` placed in `.doc1-mobile-toc-bar` above the kicker so `|kicker.left - h1.left| <= 1px`), `02. Doc-2` (`BLUF` + Mermaid), or `05. Doc-4A` (Split Code Runbook + `28px` right-edge collapse tab).
  2. **Skill / CLI / API / SDK Reference** $\rightarrow$ `04. Doc-4B` (`N3`) with **2-Level Numbered Sidebar (`1.0`, `2.1 /command`)**, **6-Stage Numbered Flow Spine (`.va-flow-spine`)** with `/slash-command` pills, and **Situation $\rightarrow$ Action Decision-Router Table** with `[View Full Table]` expand toggle.
  3. **Fleet / Container / Node Inventory & Quota/Budget Telemetry (Portainer / Monarch / Grafana shape)** $\rightarrow$ `08. Bridge-2` (`N2`), `09. App-2` (`N1`), or `12. App-3` (`N2`) with **Scoped Sidebar Context Box (`.va-scoped-nav-box`)**, **3-Zone Fleet Cards (`.va-fleet-card-3zone`)**, **2×3 Icon-Well Summary Tiles (`.va-icon-well-tile`)**, **Stateful Bulk-Action Table Toolbar (`.va-bulk-action-bar`)**, **Balanced 2×2 `.va-bento-2col` Grid** (with **Expected-Pace Progress Bar `.va-pace-bar`**, **5-Segment Threshold Gauge `.va-threshold-gauge`**, **Cumulative Trajectory vs. Baseline Curve `.va-trajectory-chart`**, and **Proportional Category Ranking Card `.va-prop-bar-row`** — zero empty grid holes).
  4. **Tasks / Planner / Daily Pacing & Biometrics (OpenTodo / Fitbit shape)** $\rightarrow$ `11. App-4` (`N1`) or `13. App-5` (`N1`) with **1-Sentence Human Status Briefing (`.va-status-briefing`)**, **Tinted Section Header Bars with Batch Actions (`.va-task-group-bar`)**, **Priority-Ring Task Rows (`.va-priority-ring`)** + `[Close the day]`, **Pastel `3px`-Left-Bar Hourly Time-Blocks (`.va-timegrid-block`)**, **Self-Filling Two-Tone Progress Capsules (`.va-fill-capsule`)**, **Target-Corridor 7-Day Sparklines (`.va-corridor-sparkline`)**, and **Connected State Hypnogram (`.va-state-hypnogram`)**.
  5. **Schema / Tree / Logs (App-Tree / Grafana shape)** $\rightarrow$ `14. App-Tree` (`N1`, keeping `.va-tree-pane` as a `240px–260px` labeled schema tree on `>= 641px`—never an unlabelled `60px` icon strip, with `.va-th-title` top-aligned table headers and ellipsis-protected JSONB cells) or `10. App-1`.
  6. **Smart Home / Wall Kiosk / Companion (`HA-1..HA-3`)** $\rightarrow$ `15. HA-1`..`17. HA-3` with circular quick-toggle matrix, `.va-prop-bar-row` circuit load breakdown (`HA-2`), and split-capsule bottom bar (`HA-3`).
- **Mode `M4` — Interactive Greenfield Scorecard:** If the user explicitly asks to choose options before building, present the **6-Axis Single-Pass Intake Scorecard** (`M, D, S, C, R, N`) from `references/00-intake-questionnaire-and-project-lock.md`.

---

## 1. THE 17-TIER GRADUATED CONTINUUM (UNIVERSAL `S1` PURE WHITE DEFAULT ACROSS ALL 17 TIERS)

All 17 tiers load in **Pure White (`S1`, `data-theme="white"`)** by default for crisp daylight legibility and instant visual comparison, while supporting 1-click live switching across all 4 surface polarities (`S1` Pure White, `S2` Warm Paper, `S3` Warm Obsidian, `S4` Carbon Slate):

| # | Tier ID | Structural Archetype | Box Weight | Default Theme | Default Nav | Primary Use Cases |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| `01` | **`Doc-1`** | Academic & Scientific Monograph | `0%` | `S1` White | `N1` | Whitepapers, mathematical derivations, research monographs |
| `02` | **`Doc-2`** | Executive Decision Memo (`BLUF` + Mermaid) | `15%` | `S1` White | `N0` | Board memos, architecture decision records, post-mortems |
| `03` | **`Doc-3`** | Normative RFC Specification (+ Mermaid FSM) | `25%` | `S1` White | `N0` | Protocol specs, RFCs, `MUST`/`SHALL` compliance audits |
| `04` | **`Doc-4B`** | Encyclopedic SDK & API Reference | `25%` | `S1` White | `N3` | Library SDK references, module/class/function dictionaries |
| `05` | **`Doc-4A`** | Split-Pane Operational Runbook (+ Mermaid Seq) | `45%` | `S1` White | `N1` | Deployment playbooks, incident response SOPs, tutorials |
| `06` | **`Bridge-1`** | Parametric Engineering Worksheet | `50%` | `S1` White | `N0` | Interactive trade studies, link-budget calculators, notebooks |
| `07` | **`Deck-1`** | Viewport-Locked Briefing Stage | `60%` | `S1` White | `N1` | `100dvh` assertion-evidence briefings with zero page scroll |
| `08` | **`Bridge-2`** | High-Density Data Table & Status Grid (`1px` Grid) | `100% 1px Grid` | `S1` White | `N2` | High-density tabular ledgers, fleet audits, benchmark grids |
| `09` | **`App-2`** | Live Metrics & Time-Series Console | `100% 1px Grid` | `S1` White | `N1` | Multi-channel strip charts, timing analyzers, register matrices |
| `10` | **`App-1`** | Compact Issue & Ticket Tracker | `0% Cards (Rows)` | `S1` White | `N1` | `36px` single-line issue queues + live right inspector |
| `11` | **`App-4`** | Task & Calendar Planner (+ Focus Hero) | `80%` | `S1` White | `N1` | Active Focus Session Hero, 3-zone staging backlog, time blocks |
| `12` | **`App-3`** | KPI & Analytics Dashboard (Bento Grid) | `100% Cards` | `S1` White | `N2` | 12-col executive KPI & SLA health grid (4 layers per card) |
| `13` | **`App-5`** | Daily Pacing & Wellness Planner (+ Readiness Hero) | `75%` | `S1` White | `N1` | Readiness Ring Hero (`84 · Steady`), 24h Day Arc, vertical timeline |
| `14` | **`App-Tree`** | Hierarchical Tree, Schema & File Explorer | `90% 3-Pane` | `S1` White | `N1` | 3-pane coupled Schema/File tree (`1px` indent guides) + 3-tab workbench |
| `15` | **`HA-1`** | Ambient Wall Kiosk Screensaver (Monet + Light Glass) | `20% HUD` | `S1` White | `N0` | 10-foot `60/40` Claude Monet canvas + `blur(22px)` frosted light/dark glass HUD |
| `16` | **`HA-2`** | Room-First Wall Control Panel | `85%` | `S1` White | `N1` | Walk-up room cards (`<= 4` metrics/room, `.va-icon-well`) + fixture dock |
| `17` | **`HA-3`** | Crease-Aware Foldable & Phone Controller | `85%` | `S1` White | `N4` | `56px` full-row slider tiles, `820px` 50/50 fold split & `390px` thumb bar |

---

## 2. UNIFIED SUITE TYPOGRAPHY (`v5.1`), 7-STEP MODULAR SCALE (`--ts-*`) & 6 MATHEMATICAL ALIGNMENT INVARIANTS

1. **The 4 Typographic Laws ("Same-Website Cohesion" Across All 17 Tiers):**
   - **Law 1 — Curated 3-Role Font Stack (Zero Random Font Drift):** `--font-sans` (`'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` + `tabular-nums` for KPIs) anchors **100% of navigation (`N0–N4`), kickers, page/card headings (`Doc-2`..`HA-3`), controls, badges, and app/dashboard copy**; `--font-serif` (`'Newsreader', 'Charter', 'Source Serif 4', Georgia, serif`) is restricted strictly to **long-form narrative prose (`01. Doc-1` body & display H1, and optional `13. App-5` reflection copy)**; `--font-mono` (`'JetBrains Mono', 'Fira Code', ui-monospace, monospace`) is restricted strictly to **machine literals** (code, CLI `/slash-cmd`, UUIDs, SQL types, raw logs).
   - **Law 2 — 100% Identical Shell & Navigation Chrome Across All 17 Tiers (`0px` Variance):** Every `.va-side-link`, `.va-tab-link`, `.va-poly-n2-bar a`, `.va-poly-n3-topbar a`, `.app1-nav-btn`, and `.va-tree-node` enforces `font-family: var(--font-sans) !important; font-size: var(--ts-nav, 13px) !important; font-weight: 500 !important; line-height: 1.35 !important;`. Every `.va-kicker` and `.doc1-kicker-text` enforces `--font-sans`, `--ts-xs: 11px`, `600`, `0.05em`, uppercase.
   - **Law 3 — Strict 7-Step Modular Scale (`--ts-*`) & `11px` Hard Floor (Ban `9px`–`10px` Micro-Text):**
     - `--ts-xs: 11px` (`lh: 1.35`, **hard minimum floor** — zero visible text `< 10.8px`), `--ts-sm: 12.5px` (`lh: 1.45`), `--ts-nav: 13px` (`lh: 1.35`), `--ts-base: 14px` (`lh: 1.5` workspace body), `--ts-prose: 15.5px` (`lh: 1.65` editorial docs `Doc-2`..`Bridge-1`; `16.5px` for `Doc-1`), `--ts-md: 16px` (`lh: 1.4`, weight `600` card titles), `--ts-xl: clamp(20px, 2vw, 24px)` (`lh: 1.22`, weight `700` universal `H1` across `Doc-2`..`HA-3`), `--ts-display: clamp(24px, 2.5vw, 28px)` (`lh: 1.18`, weight `700` `Doc-1` & `Deck-1` `H1` — within `4px` of `--ts-xl`).
2. **Outer Stage Frame (`.va-stage-outer`), Top Studio Bar (`#va-floating-dock`) & 6 Mathematical Alignment Invariants (`v5.0`):**
   - **Invariant 1 — Zero Curved-Border Parenthesis Gate (`::before` Straight Pill):** Never use `border-left` or `inset` horizontal `box-shadow` on rounded active nav/tree items; use `::before { left: 4px; top: 6px; bottom: 6px; width: 3px; border-radius: 99px; background: var(--accent-focal); }` (`display: none` when collapsed to `60px`).
   - **Invariant 2 — Zero Orphan Grid Hole Gate (`.va-bento-2col`):** Every 2-column Bento grid has an even card count (`2N`) OR `.va-bento-2col > :last-child:nth-child(odd) { grid-column: 1 / -1; }`.
   - **Invariant 3 — Table Header Baseline Gate (`|thTitle[i].top - thTitle[0].top| <= 2px`):** `table.va-tree-grid th` enforces `vertical-align: top !important; white-space: nowrap !important;` with `.va-th-title` above `.th-type`.
   - **Invariant 4 — Left Typographic Axis Gate (`|kicker.left - h1.left| <= 2px`):** In `01. Doc-1`, place `[☰]` in `.doc1-mobile-toc-bar` above `.doc1-kicker-text`.
   - **Invariant 5 — Bottom Dock Clearance Gate (`paddingBottom >= 64px` in `N4`):** Enforce `padding-bottom: 76px !important` on `.tier-section.active`, `.va-tree-center`, and `#tree-tab-rows` in `N4`.
   - **Invariant 6 — Zero Mid-Character Right-Edge Clipping Gate:** `.va-tree-pane` maintains `240px–260px` width on `>= 641px` and `table.va-tree-grid td:last-child` enforces `max-width: 180px; text-overflow: ellipsis;`.

---

## 3. PROGRESSIVE DISCLOSURE REFERENCE MAP

- **Intake Questionnaire (`M, D, S, C, R, N`), `.visual-lock.json` & Preset:** `references/00-intake-questionnaire-and-project-lock.md`
- **Unified Suite Typography (`--ts-*`), Color Theme (`S1–S4`), `C1–C3` & 5-Stop Corner Dial:** `references/01-user-discovery-and-4-theme-tokens.md`
- **Editorial & Bridge Tiers (`01. Doc-1` $\rightarrow$ `06. Bridge-1` + Theme-Aware Mermaid):** `references/02-editorial-and-bridge-tiers.md`
- **Briefing & Telemetry Tiers (`07. Deck-1` $\rightarrow$ `09. App-2`):** `references/03-briefing-and-telemetry-tiers.md`
- **Application Workspaces (`10. App-1`, `11. App-4`, `12. App-3`, `13. App-5`, `14. App-Tree`):** `references/04-application-workspace-tiers.md`
- **Home Assistant Tiers (`15. HA-1` Monet Light/Dark Glass, `16. HA-2`, `17. HA-3`) & 5-Resolution Engine:** `references/05-family-d-home-assistant-and-5-resolutions.md`
- **Clean `N0–N4` Navigation, Top Studio Bar, OA Sidebar Swatches & Hamburger Rail Collapse:** `references/06-meta-chrome-and-nav-morphing.md`
- **Automated Contract Verifier (`verify_visual_contract.py`):** `scripts/verify_visual_contract.py`

