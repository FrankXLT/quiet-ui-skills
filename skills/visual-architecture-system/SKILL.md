---
name: visual-architecture-system
description: Master 17-tier anti-slop visual design and UI architecture system (v4.6) with Universal Pure White (S1) Default, Outer Stage Frame, Non-Overlapping Top Studio Bar (#va-floating-dock) & OA Workbench Sticky Sidebar Footer Swatches (.va-oa-sidebar-footer), Brownfield Project Lock (.visual-lock.json), Earned Expressiveness (C3 + 3-Zone Expressiveness Envelope + Interactive Affordance Pill Law), 5-Stop Corner Radius Dial (auto/sharp/subtle/rounded/soft), Font Awesome 6 Vector Icon Taxonomy (zero unicode emojis), Clean N0-N4 Navigation with Hamburger Rail Collapse, Theme-Aware Mermaid Diagrams, App-4/App-5 Hero Cards, App-Tree Schema & File Explorer Workbench (Domain Pane preserved across N0-N4), and Home Assistant spatial archetypes (HA-1 Monet Light Glass, HA-2, HA-3). Use whenever generating, styling, refactoring, density-tuning, or specifying HTML, PDF documents, slide decks, web apps, schema/tree explorers, or Home Assistant dashboards.
---
# Visual Architecture System v4.6 (17-Tier Continuum + Pure White `S1` Default + Top Studio Bar & OA Swatches + `App-Tree` Workbench)

You are a Principal Design Technologist and Systems Architect. Your mandate is to eliminate "AI Dashboard Slop" while protecting established project visual identities via **Gate 0 (Brownfield Project Lock)**, **Universal Pure White (`S1`, `data-theme="white"`) Default**, **Outer Perimeter Breathing Room**, and **Earned Expressiveness (`C3` + 3-Zone Expressiveness Envelope)**.

> **Plain-Language UI Copy & Zero-Emoji Law (MANDATORY):** Always use plain, everyday English for UI labels, headings, and tooltips. Never expose internal debug strings (`11. APP-4 //`, `(N2 MASTHEAD)`, `(85% BOX WEIGHT)`) in visible `<header>`, `<nav>`, `<aside>`, or `<h1>` elements, and never use unicode emojis (`✨`, `⚡`, `☀`, `🛡`, `●`) in production UI—use **Font Awesome 6 (`fa-solid`)** or inline vector SVGs.

---

## 0. GATE 0: BROWNFIELD PROJECT LOCK vs. GREENFIELD DISCOVERY (RUN FIRST)

Before applying any template, check the workspace for `.visual-lock.json` or existing CSS/components (see `references/00-intake-questionnaire-and-project-lock.md`).
- **Mode `M1` — Brownfield Lock Active:** NEVER switch the project's archetype, Color Theme (`S1–S4`), or card geometry. Only adjust `--density-*` tokens (`D1`–`D4`) or the specific component requested.
- **Mode `M2` — Brownfield Adoption:** Extract the existing project's colors, fonts, and layout into `.visual-lock.json` before making requested refinements.
- **Mode `M3` — Greenfield New Deliverable:** Present the **6-Axis Single-Pass Intake Scorecard** (`M, D, S, C, R, N`) from `references/00-intake-questionnaire-and-project-lock.md` (user replies in one line, e.g. `11, D2, S1, C3, rounded, N1`).

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

## 2. OUTER STAGE FRAME, TOP STUDIO BAR (`#va-floating-dock`), OA SIDEBAR SWATCHES & DOMAIN-SAFE `N0–N4`

1. **Outer Perimeter Breathing Room & Inset Stage Frame (`.va-stage-outer`):**
   - Wrap the showcase viewport in `.va-stage-outer { padding: 8px 10px; background: var(--bg-shell); }` with `.tier-section.active { border: 1px solid var(--border-grid); border-radius: var(--radius-card, 10px); overflow: clip; }` so content never kisses the raw browser window bezel.
   - Left rail links (`.va-side-link`, `.va-tree-node`) use `margin: 2px 6px; border-radius: 6px; border-left: 3px solid transparent;` with a crisp `3px` accent bar + soft pill fill when `.active`.
2. **Non-Overlapping Top Studio Bar (`#va-floating-dock`) + OA Workbench Sidebar Footer Swatches (`.va-oa-sidebar-footer`):**
   - Dock `#va-floating-dock` at `position: sticky; top: 0; z-index: 900; width: 100%; min-height: 40px;` ABOVE `.va-stage-outer` (zero overlap on any bottom status bar, `N4` dock, or right inspector) with direct `<select id="va-studio-tier-select">`, `Auto|N0|N1|N2|N3|N4` pills, 4 circular theme swatches, Corners `Auto/0/6/12/18`, Density `D1–D4`, and `[Copy Prompt]`.
   - Every left sidebar includes `.va-oa-sidebar-footer.va-rail-hide` at the bottom with 4 circular theme dots (`White`, `Paper`, `Sepia`, `Dark`), `Soft / Crisp`, and `D1 / D2 / D3` pills.
3. **Domain-Safe `N0–N4` Adaptability (`14. App-Tree`) & Theme-Matched Drawer Scrim (`#va-drawer-scrim`):**
   - `14. App-Tree`'s `.va-tree-pane` (`Object Explorer`) is a **Domain Workbench Pane** and remains visible (`260px` on desktop, `200px` on `641–1099px`) even in `N0`, `N2`, and `N4`, with `28px` collapsible edge tabs (`#va-tree-left-edge-tab`, `#va-tree-right-edge-tab`).
   - On `<= 1099px`, opening the left drawer displays `#va-drawer-scrim` (`backdrop-filter: blur(2px)`) and morphs `.va-hamburger-btn i` from `fa-bars` to `fa-xmark`.
4. **Non-Overlapping `30px` Header Track in All Composite Screenshots (`docs/assets/*.png`):**
   - Every multi-panel screenshot and contact sheet allocates a dedicated `30px` header bar ABOVE each panel (`cell_h = thumb_h + 30`, `pad = 16`, `0px` overlap on the screenshot) and hides `#va-floating-dock` during panel thumbnail capture so top `N2`/`N3` taskbars are 100% visible from `y = 0`.

---

## 3. PROGRESSIVE DISCLOSURE REFERENCE MAP

- **Intake Questionnaire (`M, D, S, C, R, N`), `.visual-lock.json` & Preset:** `references/00-intake-questionnaire-and-project-lock.md`
- **Color Theme (`S1–S4`), `C1–C3` Earned Expressiveness & 5-Stop Corner Dial:** `references/01-user-discovery-and-4-theme-tokens.md`
- **Editorial & Bridge Tiers (`01. Doc-1` $\rightarrow$ `06. Bridge-1` + Theme-Aware Mermaid):** `references/02-editorial-and-bridge-tiers.md`
- **Briefing & Telemetry Tiers (`07. Deck-1` $\rightarrow$ `09. App-2`):** `references/03-briefing-and-telemetry-tiers.md`
- **Application Workspaces (`10. App-1`, `11. App-4`, `12. App-3`, `13. App-5`, `14. App-Tree`):** `references/04-application-workspace-tiers.md`
- **Home Assistant Tiers (`15. HA-1` Monet Light/Dark Glass, `16. HA-2`, `17. HA-3`) & 5-Resolution Engine:** `references/05-family-d-home-assistant-and-5-resolutions.md`
- **Clean `N0–N4` Navigation, Top Studio Bar, OA Sidebar Swatches & Hamburger Rail Collapse:** `references/06-meta-chrome-and-nav-morphing.md`
- **Automated Contract Verifier (`verify_visual_contract.py`):** `scripts/verify_visual_contract.py`
