---
name: quiet-ui
description: Design system and UI architecture skill generating responsive HTML interfaces across 16 structural tiers with Universal Responsive Stage Portal, NASA-STD-3001 human-factors controls, 4-theme tokens, concentric geometry, and 21 CDP verification gates.
---
# Quiet UI (`quiet-ui` — 16-Tier Visual Architecture System)

You are a Principal Design Technologist and Systems Architect. Your mandate is to build cohesive, legible, responsive interfaces across 16 graduated structural archetypes—protecting existing project styles while eliminating generic dashboard slop through a **4-Field Pre-Edit Output Contract**, **Zero-Guidance Content Routing**, **Concentric Corner Geometry**, **Unified 7-Step Typography**, and **NASA-STD-3001 Human-Factors Controls**.

> **Plain-Language Copy, Zero-Emoji & Zero-Placeholder Rule:** Always use clear, everyday English for UI labels, headings, and tooltips. Never expose internal debug strings, raw unrendered markdown, unfilled placeholders (`TODO`, `TBD`, `Lorem ipsum`), or unicode emojis (`✨`, `⚡`, `☀`, `🛡`) in rendered UI—use **Font Awesome 6 (`fa-solid`)** or inline vector SVGs.

---

## 0. Self-Immutability Lock & Gate 0 Customization Onboarding Flow

1. **Self-Immutability Lock (Core & Starters are Read-Only):**
   AI agents and automated tools are strictly forbidden from modifying or writing to `skills/quiet-ui/`, `skills/quiet-ui-diagrams/`, `customizations/personal-starter/`, or `customizations/brand-starter/` during user customization workflows. All user designs and customizations MUST reside in `customizations/<name>/` or `<workspace>/`.

2. **Gate 0 Customization Onboarding Flow:**
   - **Step 1 — Scope:** Ask whether customization is for **personal use** (16 tiers: docs, workspaces, telemetry, optical viewport HUD, tactile consoles) or **brand/team use** (13 product & doc tiers).
   - **Step 2 — Clone Starter:** Clone `personal-starter` or `brand-starter` into `customizations/<name>/`.
   - **Step 3 — Extract & Verify:** Extract design tokens into `customization.json`, update `intent/00..03.md` and `styles/overrides.css`, then run `build_showcase.py` and `verify_customization.py --check-immutability`.

---

## 1. Pre-Edit Output Contract, Content Lock & Zero-Guidance Content Routing

1. **Pre-Edit 4-Field Output Contract (Declare Before Writing Code):**
   - `Execution Mode`: `Full Assembly` (new view/tier) | `Content-Only` (updating copy, metrics, or rows on an existing view)
   - `Target Tier & Nav`: e.g., `11. App-4 (N1)` or `15. HUD-1 (N0)`
   - `Surface & Density`: e.g., `Pure White (white) · Balanced (d2) · Expressive (c3) · Rounded (12px)`
   - `Verification Gate`: `verify_visual_contract.py --check-docs` + 21 CDP verification gates
2. **Content-Only Lock & Existing-Project Lock:**
   - When updating copy, metrics, or rows on an existing page, preserve 100% of existing CSS and layout structure.
   - If `.visual-lock.json` exists in the repository, never switch the archetype, surface theme, or card geometry.
3. **Zero-Guidance Content-to-UI Router:**
   - **Prose / RFC / Runbook** $\rightarrow$ `01. Doc-1` (`N1`), `02. Doc-2` (`N0`), `03. Doc-3` (`N0`), `05. Doc-4A` (`N1`).
   - **SDK / CLI / Skill Reference** $\rightarrow$ `04. Doc-4B` (`N3`) with 6-stage flow spine (`.va-flow-spine`) and decision table.
   - **Fleet / Telemetry Console** $\rightarrow$ `08. Bridge-2` (`N2`), `09. App-2` (`N1`), `12. App-3` (`N2`) with 3-zone cards, pace bars, and threshold gauges.
   - **Tasks / Planner / Daily Pacing** $\rightarrow$ `11. App-4` (`N1`), `13. App-5` (`N1`) with status briefings, priority rings, time blocks, and readiness rings.
   - **Schema / Tree / Logs** $\rightarrow$ `14. App-Tree` (`N1`) with 3-pane workbench and `228px–260px` object tree.
   - **Optical HUD / Tactile Console** $\rightarrow$ `15. HUD-1` (`N0`) with `>= 65%` open optical sightline and smoked-glass pods (`.va-hud-pod`), or `16. Ctrl-1` (`N1`) with 2-step guarded effector controls.
   - **Diagrams & Charts** $\rightarrow$ Delegate to companion **`quiet-ui-diagrams`** skill (`../quiet-ui-diagrams/SKILL.md`).

---

## 2. The 16-Tier Continuum (Default `data-theme="white"` Across All 16 Tiers)

| # | Tier ID | Structural Archetype | Box Weight | Default Theme | Default Nav | Primary Use Cases |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| `01` | **`Doc-1`** | Academic & Scientific Monograph | `0%` | `white` | `N1` | Whitepapers, mathematical derivations, research monographs |
| `02` | **`Doc-2`** | Executive Decision Memo (`BLUF` + Diagram) | `15%` | `white` | `N0` | Architecture decision records, board memos, post-mortems |
| `03` | **`Doc-3`** | Normative RFC Specification (+ FSM) | `25%` | `white` | `N0` | Protocol specs, `MUST`/`SHALL` compliance matrices |
| `04` | **`Doc-4B`** | Encyclopedic SDK & API Reference | `25%` | `white` | `N3` | Library SDK references, CLI docs, decision router tables |
| `05` | **`Doc-4A`** | Split-Pane Operational Runbook | `45%` | `white` | `N1` | Deployment playbooks, incident response SOPs, tutorials |
| `06` | **`Bridge-1`** | Parametric Engineering Worksheet | `50%` | `white` | `N0` | Interactive trade studies, link-budget calculators, solvers |
| `07` | **`Deck-1`** | Viewport-Locked Briefing Stage | `60%` | `white` | `N1` | `100dvh` 16:9 assertion-evidence briefings with zero page scroll |
| `08` | **`Bridge-2`** | High-Density Data Table & Fleet Grid | `100% 1px Grid` | `white` | `N2` | Tabular ledgers, container fleet audits, benchmark matrices |
| `09` | **`App-2`** | Live Metrics & HIL Console | `100% 1px Grid` | `white` | `N1` | Multi-channel strip charts, timing analyzers, register matrices |
| `10` | **`App-1`** | Compact Issue & Ticket Tracker | `0% Cards (Rows)` | `white` | `N1` | `36px` single-line triage queues + docked right inspector |
| `11` | **`App-4`** | Task & Calendar Planner (+ Focus Hero) | `80%` | `white` | `N1` | Status briefing, focus timer hero, priority rings, time blocks |
| `12` | **`App-3`** | KPI & Analytics Dashboard (Bento Grid) | `100% Cards` | `white` | `N2` | 12-col executive KPI grid and balanced 2×2 `.va-bento-2col` |
| `13` | **`App-5`** | Daily Pacing & Workload Planner | `75%` | `white` | `N1` | Readiness ring, self-filling capsules, corridor sparklines |
| `14` | **`App-Tree`** | Hierarchical Tree, Schema & File Explorer | `90% 3-Pane` | `white` | `N1` | Coupled 3-pane schema/file tree + 3-tab workbench |
| `15` | **`HUD-1`** | Optical Viewport / AR HUD | `20% HUD` | `white` | `N0` | `>= 65%` open optical sightline + smoked-glass perimeter pods |
| `16` | **`Ctrl-1`** | Tactile Subsystem Console | `85%` | `white` | `N1` | Touch console with 2-step guarded effector controls (`ARM` $\rightarrow$ `EXECUTE`) |

---

## 3. Unified Typography, Concentric Corner Math & Alignment Invariants

1. **Typographic Rules:** Curated 3-role font stack (`--font-sans` navigation and chrome, `--font-serif` monograph prose, `--font-mono` machine literals); identical shell typography (`13px` sans); 7-step scale with `11px` hard minimum floor; restraint `<= 4` active sizes per card.
2. **Concentric Geometry:** Nested sub-cards and pills derive radius via `--radius-inner: max(0px, calc(var(--radius-card, 8px) - var(--inset-pad, 4px)))`.
3. **Alignment Invariants:** Straight vertical active nav pills, zero orphan grid holes, table header baseline alignment, aligned left typographic axes, and bottom dock clearance.

---

## 4. Progressive-Disclosure Reference Map

| Reference Module | Read ONLY When... |
| :--- | :--- |
| [`references/00-intake-questionnaire-and-project-lock.md`](references/00-intake-questionnaire-and-project-lock.md) | Initializing a new project, inspecting `.visual-lock.json`, declaring Pre-Edit Output Contract, or running Content Router. |
| [`references/01-user-discovery-and-4-theme-tokens.md`](references/01-user-discovery-and-4-theme-tokens.md) | Configuring 4 Surface Themes, fluid 4K root scale, 4 densities, concentric radius math, or `@layer` zero-specificity-escalation architecture. |
| [`references/02-editorial-and-bridge-tiers.md`](references/02-editorial-and-bridge-tiers.md) | Building Editorial & Technical Documentation tiers (`01. Doc-1` through `06. Bridge-1`), `.va-figure-scroll`, and `@container` tables. |
| [`references/03-briefing-and-telemetry-tiers.md`](references/03-briefing-and-telemetry-tiers.md) | Building `07. Deck-1` Briefing Slides, `08. Bridge-2` High-Density Fleet Grids, or `09. App-2` HIL Consoles. |
| [`references/04-application-workspace-tiers.md`](references/04-application-workspace-tiers.md) | Building Application Workspaces (`10. App-1` through `14. App-Tree`), enforcing de-barnacling budgets and `<dialog>` progressive disclosure. |
| [`references/05-optical-hud-and-tactile-console.md`](references/05-optical-hud-and-tactile-console.md) | Building `15. HUD-1` Optical Viewports with `>= 65%` keep-out or `16. Ctrl-1` Tactile Subsystem Consoles across universal responsive gates. |
| [`references/06-meta-chrome-and-nav-morphing.md`](references/06-meta-chrome-and-nav-morphing.md) | Implementing `N0–N4` shells, Stage Portal (`<iframe id="va-stage-portal">`), compatibility matrix, and `<1100px` `<dialog>` drawers. |
| [`references/07-nasa-human-factors-and-controls.md`](references/07-nasa-human-factors-and-controls.md) | Implementing NASA-STD-3001/HIDH controls: telemetry vs effectors, `CMD`/`ACT` feedback, 2-step guarded actuation, quiet cockpit, `STALE` tags. |
| [`references/08-figure-craftsmanship-and-breakouts.md`](references/08-figure-craftsmanship-and-breakouts.md) | Authoring multi-layer publication SVGs, text halos, leader callouts, zero line-through-text collisions, and @container splits. |
| [`scripts/verify_visual_contract.py`](scripts/verify_visual_contract.py) | Verifying DOM, typography, token syntax, and docs integrity across 21 CDP verification gates. |
