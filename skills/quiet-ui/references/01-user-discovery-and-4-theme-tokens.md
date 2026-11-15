# Reference 01: Functional Discovery Forks, 4 Themes, Fluid 4K Root & @layer Architecture

## 1. Functional Triage Forks (When Content Is Ambiguous Across Tiers)

Never ask vague aesthetic questions (*"What colors or layout do you want?"*). Ask the matching functional fork question:
- **Fork A — Report / Analysis / Specification:**
  - *Academic Monograph (`01. Doc-1`, `0%` Boxes):* Continuous serif prose, inline equations, margin sidenotes, `booktabs` tables.
  - *Executive Decision Memo (`02. Doc-2`, `15%` Boxes):* Top `BLUF` ledger, Mermaid decision flowchart, 4-cell hairline metric strip.
  - *Normative RFC Specification (`03. Doc-3`, `25%` Boxes):* `MUST`/`SHALL` requirement matrix, Mermaid state machine, schema diff.
  - *Parametric Worksheet (`06. Bridge-1`, `50%` Boxes):* Editorial prose coupled to `1px` interactive slider solver and live SVG plot.
- **Fork B — Documentation / Runbook / API:**
  - *Split Runbook (`05. Doc-4A`, `45%` Boxes):* Operator steps and Mermaid sequence flow coupled to pinned right code console.
  - *SDK & API Reference (`04. Doc-4B`, `25%` Boxes):* 2-column symbol tree, **6-Stage Numbered Flow Spine (`.va-flow-spine`)**, and decision table.
- **Fork C — Dashboard / Workspace / Telemetry:**
  - *High-Density Table (`08. Bridge-2`)* or *Time-Series Console (`09. App-2`)*: `1px` hairline grid, 3-zone fleet cards, strip charts.
  - *Compact Issue Tracker (`10. App-1`)* or *Task Planner (`11. App-4`)*: `36px` triage rows, or status briefing, focus hero, time blocks.
  - *KPI Bento Dashboard (`12. App-3`)* or *Daily Pacing (`13. App-5`)*: 12-col bento grid, or readiness ring, self-filling capsules, hypnogram.
  - *Hierarchical Explorer (`14. App-Tree`)*: 3-pane schema/file explorer with `228px–260px` tree and 3-tab workbench.
- **Fork D — Optical HUD / Tactile Console:**
  - *Optical Viewport HUD (`15. HUD-1`, `20% HUD`):* `>= 65%` open optical sightline + smoked-glass perimeter pods (`.va-hud-pod`).
  - *Tactile Subsystem Console (`16. Ctrl-1`, `85%` Boxes):* Arm's-reach walk-up touch interface with 2-step guarded effector controls (`ARM` -> `EXECUTE`).

---

## 2. 4 Themes, Color Discipline (`c1–c3`) & Concentric Corner Math

1. **4 Surface Themes (Default `white`):** `white` (Pure Alabaster), `paper` (Warm Paper), `dark-paper` (Sepia Dark), `dark` (Carbon Dark).
2. **3-Zone Expressiveness:** Zone 1 (`>= 75%` calm neutral canvas), Zone 2 (`<= 20%` soft tints & single hero card), Zone 3 (`<= 5%` signal ink for active CTAs, progress rings, and alarms).
3. **Concentric Corner Geometry ($R_{\text{inner}} = \max(0, R_{\text{outer}} - \text{Inset})$):**
   `--inset-pad: 4px; --radius-inner: max(0px, calc(var(--radius-card, 8px) - var(--inset-pad, 4px))); --radius-trough-pill: max(0px, calc(var(--radius-sm, 6px) - 2px));` applied across `auto`, `sharp` (`0px`), `subtle` (`6px`), `rounded` (`12px`), `soft` (`18px`).

---

## 3. Fluid 4K Root Scale, rem Typography & 11px Legibility Floor

1. **Fluid 4K Root:** `font-size: clamp(16px, calc(12.4px + 0.25vw), 22px);` scales naturally with viewing distance (16px at 1440p, 17.2px at 1080p-scaled, 22px at 4K).
2. **Modular `rem` Scale (`--ts-*`) with `11px` Hard Floor:**
   - `--ts-xs: max(11px, 0.6875rem)` — **Hard floor** for kickers, badges, axes (zero visible elements `< 10.8px`).
   - `--ts-sm: max(12px, 0.78125rem)` — Dense table cells, captions, status pills.
   - `--ts-nav: max(12.5px, 0.8125rem)` — Navigation links, buttons, tab bars.
   - `--ts-base: max(13.5px, 0.875rem)` — Standard body copy; `--ts-prose: max(15px, 0.96875rem)` for editorial docs.
   - `--ts-md: max(15.5px, 1rem)` — Card titles, H3 subheadings.
   - `--ts-xl: clamp(1.25rem, 1.1rem + 0.45vw, 1.55rem)` — Page H1 and primary Bento KPIs.
   - `--ts-display: clamp(1.5rem, 1.3rem + 0.65vw, 1.9rem)` — Monograph & Deck-1 display H1.
3. **Typographic Restraint:** At most **4 active font sizes** and **2 primary contrast rungs** per card.

---

## 4. Zero-Specificity Cascade Layer Architecture (@layer)

All Quiet UI CSS declares explicit cascade layers to completely eliminate specificity battles:
```css
@layer reset, tokens, shell, archetypes, utilities;
```
- Layer precedence guarantees utilities override archetypes, archetypes override shell, and shell overrides tokens cleanly without specificity conflicts.
- 100% of custom rules and theme overrides integrate into their appropriate layer, ensuring zero specificity escalation.
