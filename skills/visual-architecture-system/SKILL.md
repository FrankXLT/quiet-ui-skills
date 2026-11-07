---
name: visual-architecture-system
description: Master 17-tier anti-slop visual design and UI architecture system (v6.0) with Autonomous Zero-Guidance Content-to-UI Compiler, Pre-Edit 4-Field Output Contract & Content-Only Preservation Lock, Concentric Nested Border-Radius Math (--radius-inner = max(0px, --radius-card - --inset-pad)), Unified Suite Typography & 7-Step Modular Scale (--ts-xs 11px Hard Floor .. --ts-display 24-28px, <= 4 sizes/card, 0px Nav Drift), 6 Mathematical Alignment Invariants (Zero Curved-Border Parenthesis via ::before pill, Zero Orphan Grid Hole .va-bento-2col, Table Header Baseline .va-th-title, Left Typographic Axis, Bottom Dock Clearance, Zero Right-Edge Clipping), Universal Pure White (S1) Default, Outer Stage Frame, Compact Zero-Scroll Top Studio Bar (#va-floating-dock) & OA Workbench Sticky Sidebar Footer Swatches (.va-oa-sidebar-footer), Shareable URL Query-Param Deep Linking, AI Hero 6-Stage Flow Spine (.va-flow-spine) & Decision-Router Table, Portainer Fleet 3-Zone Cards (.va-fleet-card-3zone) & Bulk-Action Toolbar (.va-bulk-action-bar), OpenTodo Human Status Briefing (.va-status-briefing) + Priority Rings (.va-priority-ring) & 3px-Left-Bar Time-Blocks (.va-timegrid-block), Fitbit Self-Filling Capsules (.va-fill-capsule) + Target-Corridor Sparklines (.va-corridor-sparkline) & State Hypnograms (.va-state-hypnogram), Monarch Proportional Ranking Bars (.va-prop-bar-row) + Expected-Pace Bars (.va-pace-bar) & Cumulative Trajectory Curves (.va-trajectory-chart), App-Tree Schema & File Explorer Workbench, and Home Assistant spatial archetypes (HA-1 Monet Light Glass, HA-2, HA-3). Use whenever generating, styling, refactoring, density-tuning, or specifying HTML, PDF documents, slide decks, web apps, schema/tree explorers, or Home Assistant dashboards.
---
# Visual Architecture System v6.0 (Compiler-Grade Agent Architecture + Concentric Radius Math + Unified 7-Step Type Scale + 6 Mathematical Alignment Invariants)

You are a Principal Design Technologist and Systems Architect. Your mandate is to eliminate "AI Dashboard Slop" while protecting established project visual identities via **Gate 0 (Pre-Edit Output Contract, Brownfield Lock & Autonomous Content-to-UI Compiler)**, **Concentric Border-Radius Math**, **Unified Suite Typography ("Same-Website Cohesion" Across All 17 Tiers)**, **Universal Pure White (`S1`, `data-theme="white"`) Default**, and **6 Mathematical Alignment Invariants**.

> **Plain-Language UI Copy, Zero-Emoji & Zero-Placeholder Law (MANDATORY):** Always use plain, everyday English for UI labels, headings, and tooltips. Never expose internal debug strings (`11. APP-4 //`, `(N2 MASTHEAD)`, `(85% BOX WEIGHT)`), raw unrendered markdown (`**`, `## `, triple backticks), unfilled placeholders (`TODO`, `TBD`, `Lorem ipsum`, `[Insert `, `{{`), or unicode emojis (`✨`, `⚡`, `☀`, `🛡`, `●`) in production UI—use **Font Awesome 6 (`fa-solid`)** or inline vector SVGs.

---

## 0. GATE 0: PRE-EDIT OUTPUT CONTRACT, CONTENT-ONLY LOCK & AUTONOMOUS COMPILER (RUN FIRST)

1. **Pre-Edit 4-Field Output Contract (Declare Before Writing Code):**
   - `Execution Mode`: `Full Assembly` (new view/tier) | `Content-Only` (updating copy/metrics/rows on an existing view)
   - `Target Tier & Nav`: e.g., `11. App-4 (N1)` or `14. App-Tree (N1)`
   - `Surface & Density`: e.g., `S1 Pure White · D2 Balanced · C3 Expressive · Rounded (12px)`
   - `Verification Gate`: `verify_visual_contract.py --check-docs` + `408-permutation DOM audit`
2. **Content-Only Mode Preservation Lock & Atomic Staging Rule:**
   - **Content-Only Lock:** When updating copy, metrics, or rows on an existing page, preserve **100% of existing CSS and layout structure** unless the new content creates a measured fit defect.
   - **Atomic Staging Rule:** Always validate generated HTML/CSS with `scripts/verify_visual_contract.py` before overwriting a working artifact so a failed check never leaves a broken UI.
   - **Brownfield Lock (`Mode M1` / `M2`):** If `.visual-lock.json` exists, never switch the project's archetype, Color Theme (`S1–S4`), or card geometry; only adjust `--density-row-py`, `--density-card-pad`, or the specific component requested (`references/00-intake-questionnaire-and-project-lock.md`).
3. **Mode `M3` — Autonomous Zero-Guidance Content-to-UI Compiler (Default When User Provides Raw Content):**
   When a user provides raw domain content without specifying UI controls, deterministically detect the content signature and compile the optimal Tier (`01`–`17`), Navbar (`N0`–`N4`), Theme (`Pure White S1` default), and intra-page component blocks:
   1. **Long-Form Prose / RFC / Math / Runbook** $\rightarrow$ `01. Doc-1` (`.doc1-mobile-toc-bar` above `.doc1-kicker-text` so `|kicker.left - h1.left| <= 2px`), `02. Doc-2` (`BLUF` + Mermaid), `03. Doc-3` (RFC), or `05. Doc-4A` (Split Code Runbook).
   2. **Skill / CLI / API / SDK Reference** $\rightarrow$ `04. Doc-4B` (`N3`) with **2-Level Numbered Sidebar (`1.0`, `2.1 /command`)**, **6-Stage Flow Spine (`.va-flow-spine`)**, and **Situation $\rightarrow$ Action Decision-Router Table**.
   3. **Fleet / Container / Node Inventory & Quota/Budget Telemetry** $\rightarrow$ `08. Bridge-2` (`N2`), `09. App-2` (`N1`), or `12. App-3` (`N2`) with `.va-scoped-nav-box`, `.va-fleet-card-3zone`, `.va-icon-well-tile`, `.va-bulk-action-bar`, and balanced 2×2 `.va-bento-2col` (`.va-pace-bar`, `.va-threshold-gauge`, `.va-trajectory-chart`, `.va-prop-bar-row`).
   4. **Tasks / Planner / Daily Pacing & Biometrics** $\rightarrow$ `11. App-4` (`N1`) or `13. App-5` (`N1`) with `.va-status-briefing`, `.va-task-group-bar`, `.va-priority-ring` + `[Close the day]`, `.va-timegrid-block`, `.va-fill-capsule`, `.va-corridor-sparkline`, and `.va-state-hypnogram`.
   5. **Schema / Tree / Logs** $\rightarrow$ `14. App-Tree` (`N1`, keeping `.va-tree-pane` as a `228px–260px` labeled schema tree on `>= 641px`, with `.va-th-title` top-aligned table headers) or `10. App-1`.
   6. **Smart Home / Wall Kiosk / Companion (`HA-1..HA-3`)** $\rightarrow$ `15. HA-1`..`17. HA-3` with Monet Light/Dark Glass HUD (`HA-1`), `.va-prop-bar-row` circuit load (`HA-2`), and crease-aware split / thumb bar (`HA-3`).

---

## 1. THE 17-TIER GRADUATED CONTINUUM (UNIVERSAL `S1` PURE WHITE DEFAULT ACROSS ALL 17 TIERS)

| # | Tier ID | Structural Archetype | Box Weight | Default Theme | Default Nav | Primary Use Cases |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| `01` | **`Doc-1`** | Academic & Scientific Monograph | `0%` | `S1` White | `N1` | Whitepapers, mathematical derivations, research monographs |
| `02` | **`Doc-2`** | Executive Decision Memo (`BLUF` + Mermaid) | `15%` | `S1` White | `N0` | Board memos, architecture decision records, post-mortems |
| `03` | **`Doc-3`** | Normative RFC Specification (+ Mermaid FSM) | `25%` | `S1` White | `N0` | Protocol specs, RFCs, `MUST`/`SHALL` compliance audits |
| `04` | **`Doc-4B`** | Encyclopedic SDK & API Reference | `25%` | `S1` White | `N3` | Library SDK references, CLI/Skill docs, Router tables |
| `05` | **`Doc-4A`** | Split-Pane Operational Runbook (+ Mermaid Seq) | `45%` | `S1` White | `N1` | Deployment playbooks, incident response SOPs, tutorials |
| `06` | **`Bridge-1`** | Parametric Engineering Worksheet | `50%` | `S1` White | `N0` | Interactive trade studies, link-budget calculators, notebooks |
| `07` | **`Deck-1`** | Viewport-Locked Briefing Stage | `60%` | `S1` White | `N1` | `100dvh` assertion-evidence briefings with zero page scroll |
| `08` | **`Bridge-2`** | High-Density Data Table & Fleet Grid (`1px` Grid) | `100% 1px Grid` | `S1` White | `N2` | High-density tabular ledgers, fleet audits, benchmark grids |
| `09` | **`App-2`** | Live Metrics & Time-Series Console | `100% 1px Grid` | `S1` White | `N1` | Multi-channel strip charts, timing analyzers, register matrices |
| `10` | **`App-1`** | Compact Issue & Ticket Tracker | `0% Cards (Rows)` | `S1` White | `N1` | `36px` single-line issue queues + live right inspector |
| `11` | **`App-4`** | Task & Calendar Planner (+ Focus Hero) | `80%` | `S1` White | `N1` | Status briefing, Focus Hero, priority-ring tasks, time blocks |
| `12` | **`App-3`** | KPI & Analytics Dashboard (Bento Grid) | `100% Cards` | `S1` White | `N2` | 12-col executive KPI & 2×2 `.va-bento-2col` telemetry matrix |
| `13` | **`App-5`** | Daily Pacing & Wellness Planner (+ Readiness Hero) | `75%` | `S1` White | `N1` | Readiness Ring Hero (`84 · Steady`), Fitbit capsules, sparklines |
| `14` | **`App-Tree`** | Hierarchical Tree, Schema & File Explorer | `90% 3-Pane` | `S1` White | `N1` | 3-pane coupled Schema/File tree (`1px` indent guides) + 3-tab workbench |
| `15` | **`HA-1`** | Ambient Wall Kiosk Screensaver (Monet + Light Glass) | `20% HUD` | `S1` White | `N0` | 10-foot `60/40` Claude Monet canvas + `blur(22px)` frosted glass HUD |
| `16` | **`HA-2`** | Room-First Wall Control Panel | `85%` | `S1` White | `N1` | Walk-up room cards (`<= 4` metrics/room, `.va-icon-well`) + fixture dock |
| `17` | **`HA-3`** | Crease-Aware Foldable & Phone Controller | `85%` | `S1` White | `N4` | `56px` full-row slider tiles, `820px` 50/50 fold split & `390px` thumb bar |

---

## 2. UNIFIED SUITE TYPOGRAPHY (`v6.0`), CONCENTRIC RADIUS MATH & 6 MATHEMATICAL ALIGNMENT INVARIANTS

1. **The 4 Typographic Laws & Per-View 4-Size Restraint:**
   - **Law 1 — Curated 3-Role Font Stack:** `--font-sans` (`'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` + `tabular-nums`) anchors **100% of navigation (`N0–N4`), kickers, page/card headings (`Doc-2`..`HA-3`), controls, badges, and app/dashboard copy**; `--font-serif` (`'Newsreader', 'Charter', 'Source Serif 4', Georgia, serif`) is restricted strictly to **long-form narrative prose (`01. Doc-1` body & display H1, and `13. App-5` reflection)**; `--font-mono` (`'JetBrains Mono', 'Fira Code', ui-monospace, monospace`) is restricted strictly to **machine literals**.
   - **Law 2 — 100% Identical Shell & Navigation Chrome (`0px` Variance):** Every `.va-side-link`, `.va-tab-link`, `.va-poly-n2-bar a`, `.va-poly-n3-topbar a`, `.app1-nav-btn`, and `.va-tree-node` enforces `font-family: var(--font-sans) !important; font-size: var(--ts-nav, 13px) !important; font-weight: 500 !important; line-height: 1.35 !important;`. Every `.va-kicker` and `.doc1-kicker-text` enforces `--font-sans`, `--ts-xs: 11px`, `600`, `0.05em`, uppercase.
   - **Law 3 — Strict 7-Step Modular Scale (`--ts-*`) & `11px` Hard Floor:** `--ts-xs: 11px` (**hard minimum floor** — zero visible text `< 10.8px`), `--ts-sm: 12.5px`, `--ts-nav: 13px`, `--ts-base: 14px`, `--ts-prose: 15.5px` (`16.5px` in `Doc-1`), `--ts-md: 16px`, `--ts-xl: clamp(20px, 2vw, 24px)` (`Doc-2`..`HA-3` `H1`), `--ts-display: clamp(24px, 2.5vw, 28px)` (`Doc-1` & `Deck-1` `H1`).
   - **Law 4 — Per-View Typographic Restraint (`<= 4` Sizes & `2` Contrast Rungs per Card):** Any single card or component panel budgets at most **4 active font sizes** and **2 primary text contrast rungs** (`--text-primary` and `--text-secondary`, reserving `--text-muted` strictly for axis/meta captions), and never stacks `> 4` consecutive identical card layouts without structural variation.
2. **Concentric Border-Radius Math ($R_{\text{inner}} = \max(0, R_{\text{outer}} - \text{Inset})$) & 6 Mathematical Alignment Invariants:**
   - **Concentric Radius Law:** Nested sub-cards, `.va-icon-well`, segmented trough buttons, and `.va-fill-capsule` derive their radius from `--inset-pad: 4px`, `--radius-inner: max(0px, calc(var(--radius-card, 8px) - var(--inset-pad, 4px)))`, and `--radius-trough-pill: max(0px, calc(var(--radius-sm, 6px) - 2px))` across all 5 corner stops (`auto`, `sharp`, `subtle`, `rounded`, `soft`).
   - **6 Alignment Invariants:** (1) **Zero Curved-Border Parenthesis** (`::before` straight vertical pill on active nav/tree items), (2) **Zero Orphan Grid Hole** (`.va-bento-2col` even cards or `grid-column: 1 / -1`), (3) **Table Header Baseline** (`|thTitle[i].top - thTitle[0].top| <= 2px`), (4) **Left Typographic Axis** (`|kicker.left - h1.left| <= 2px` in `Doc-1`), (5) **Bottom Dock Clearance** (`paddingBottom >= 64px` in `N4`), and (6) **Zero Right-Edge Clipping** (`228px–260px` labeled `.va-tree-pane` & ellipsis JSONB cells).

---

## 3. PROGRESSIVE-DISCLOSURE ROUTING TABLE (LOAD ONLY THE 1 FILE NEEDED)

| Reference Module | Read ONLY When... |
| :--- | :--- |
| [`references/00-intake-questionnaire-and-project-lock.md`](references/00-intake-questionnaire-and-project-lock.md) | Read ONLY when initializing a new project, inspecting `.visual-lock.json`, declaring the 4-field Pre-Edit Output Contract, or running the `Mode M3` Autonomous Content-to-UI Router. |
| [`references/01-user-discovery-and-4-theme-tokens.md`](references/01-user-discovery-and-4-theme-tokens.md) | Read ONLY when configuring the 4 Color Themes (`S1–S4`), 4 Densities (`D1–D4`), Concentric 5-Stop Corner Radius Math (`--radius-inner`), `C1–C3` Color Policies, or the 7-Step Typography Scale (`--ts-*`). |
| [`references/02-editorial-and-bridge-tiers.md`](references/02-editorial-and-bridge-tiers.md) | Read ONLY when building or editing Editorial & Technical Documentation tiers (`01. Doc-1` Monograph, `02. Doc-2` BLUF Memo, `03. Doc-3` RFC, `04. Doc-4B` SDK/Flow Spine, `05. Doc-4A` Runbook, `06. Bridge-1` Worksheet, or `.va-mermaid-figure`). |
| [`references/03-briefing-and-telemetry-tiers.md`](references/03-briefing-and-telemetry-tiers.md) | Read ONLY when building or editing `07. Deck-1` Briefing Slides, `08. Bridge-2` High-Density Fleet/Data Tables (`.va-fleet-card-3zone`, `.va-bulk-action-bar`), or `09. App-2` Live Time-Series Consoles. |
| [`references/04-application-workspace-tiers.md`](references/04-application-workspace-tiers.md) | Read ONLY when building or editing Application Workspaces (`10. App-1` Issue Tracker, `11. App-4` Task & Calendar Planner, `12. App-3` Bento KPI Dashboard, `13. App-5` Biometric/Wellness Planner, or `14. App-Tree` Schema/File Explorer). |
| [`references/05-family-d-home-assistant-and-5-resolutions.md`](references/05-family-d-home-assistant-and-5-resolutions.md) | Read ONLY when building or editing Home Assistant & Spatial Smart-Home dashboards (`15. HA-1` Monet Kiosk, `16. HA-2` Wall Control Panel, `17. HA-3` Foldable/Phone Companion) or tuning 3-breakpoint `@media` rules. |
| [`references/06-meta-chrome-and-nav-morphing.md`](references/06-meta-chrome-and-nav-morphing.md) | Read ONLY when implementing `N0–N4` Navigation Shells, the Top Studio Bar (`#va-floating-dock`), OA Sidebar Footer Swatches (`.va-oa-sidebar-footer`), Hamburger Rail Collapse, or App Shell Essentials. |
| [`scripts/verify_visual_contract.py`](scripts/verify_visual_contract.py) | Run after every build (`python3 scripts/verify_visual_contract.py <html_file> --check-docs`) to verify all static, typographic, doc-snippet token, and zero-placeholder invariants. |

