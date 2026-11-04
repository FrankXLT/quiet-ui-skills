# Socratic User Discovery Protocol, Color Theme (`S1–S4`), Earned Expressiveness (`C1–C3`) & 5-Stop Corner Dial

## 1. How to Grill the User (Functional Triage Forks for M2/M3 Builds)

Never ask vague aesthetic questions (*"What colors or layout style do you want?"*). When a greenfield (`M3`) or hybrid (`M2`) request is ambiguous across tiers, ask the matching functional fork question below:

### Fork A: "Write a report / summary / analysis on [Topic]"
> *"Who is the primary reader and how will they use this document?*
> - **Option A — Academic & Scientific Monograph (`01. Doc-1`, `0%` Boxes):** Continuous serif prose, inline equations, right-margin sidenotes, and sortable horizontal-rule `booktabs` tables.
> - **Option B — Executive Decision Memo (`02. Doc-2`, `15%` Boxes):** Anchored at the top by a 4-cell Bottom-Line-Up-Front (`BLUF`) Decision Ledger, theme-aware Mermaid topology diagram, 4-cell hairline metric strip, and a risk callout.
> - **Option C — Parametric Engineering Worksheet (`06. Bridge-1`, `50%` Boxes):** Editorial prose and tables with an embedded `1px` hairline interactive slider solver and live sensitivity plot."

### Fork B: "Document [System / API / CLI]"
> *"How will engineers use this documentation day-to-day?*
> - **Option A — Split-Pane Operational Runbook (`05. Doc-4A`, `45%` Boxes):** Sequential operator steps and Mermaid sequence diagram in the center synchronized with full config files (`YAML`/`CLI`/`systemd`) pinned in a sticky right-hand dark console.
> - **Option B — Encyclopedic SDK & API Reference (`04. Doc-4B`, `25%` Boxes):** 2-column lookup with a left symbol tree and `<dl>/<dt>/<dd>` signature bands, parameter tables, `¶` permalinks, and `[>>>]` copyable REPL blocks.
> - **Option C — Normative RFC Specification (`03. Doc-3`, `25%` Boxes):** `100%` monospace specification with `MUST`/`SHOULD` requirement matrices, Mermaid state machine, and unified schema diffs."

### Fork C: "Build a dashboard / workspace / schema explorer / tracker for [System]"
> *"What is the primary workflow on this view?*
> - **Option A — High-Density Data Table (`08. Bridge-2`) or Live Time-Series Console (`09. App-2`):** Sharp `1px` hairline grid with a 5-cell sparkline strip (`Bridge-2`) or synchronized multi-channel waveforms (`App-2`).
> - **Option B — Compact Issue Tracker (`10. App-1`) or Task & Calendar Planner (`11. App-4`):** `36px` issue rows with a right-hand inspector (`App-1`), or an active Focus Session Hero, 3-zone staging backlog, and time-blocked calendar lanes (`App-4`).
> - **Option C — Hierarchical Tree, Schema & File Explorer (`14. App-Tree`, `90% 3-Pane`):** 3-pane coupled workbench with a collapsible `260px` Schema/File tree (`1px` `.va-tree-guide` indent guides + type badges), a 3-tab center workbench (`Data Grid`, `DDL Spec`, `SQL/Grep Console`), and a `280px` metadata inspector.
> - **Option D — KPI & Analytics Dashboard (`12. App-3`, `100% Cards`):** 12-column Bento grid where every card contains 4 layers."

### Fork D: "Build a personal/household pacing app or Home Assistant dashboard"
> *"Where and how is this screen viewed?*
> - **Option A — Daily Pacing & Wellness Planner (`13. App-5`, `75%` Boxes):** Single-Anchor Readiness Ring Hero (`84 · Steady`), 24h Day Arc, vertical Day Timeline (`09:00`–`18:00`), `+40%` transition buffers, and 1-tap Afternoon Reset.
> - **Option B — Ambient Wall Kiosk Screensaver (`15. HA-1`, `20% HUD`):** 10-foot `60/40` Claude Monet *Water Lilies* canvas + `backdrop-filter: blur(22px)` frosted glass HUD (`N0` zero nav bars).
> - **Option C — Room-First Wall Control Panel (`16. HA-2`) or Foldable/Phone Controller (`17. HA-3`):** Walk-up room cards (`<= 4` metrics/room, `.va-icon-well` badges) + fixture dock (`HA-2`), or `56px` touch slider tiles (`HA-3`)."

---

## 2. Earned Expressiveness (`C3`), 3-Zone Envelope & 5-Stop Corner Radius Dial

1. **The 3-Zone Expressiveness Envelope (`C1` $\rightarrow$ `C2` $\rightarrow$ `C3`):**
   - **Zone 1 (`>= 75%` Calm Neutral Canvas):** Backgrounds (`S1–S4`) remain neutral paper, alabaster, warm slate, or obsidian.
   - **Zone 2 (`<= 20%` Soft Surface Tints & Single-Anchor Hero):** Under `C2` and `C3`, views may feature **at most 1 tinted Hero Card** (`.app5-hero-card.primary-hero`, `.app4-focus-hero`) and soft surface-tinted icon wells (`.va-icon-well`: `34px×34px`, `9px` radius using `--tint-indigo-bg`, `--tint-emerald-bg`, `--tint-amber-bg`, `--tint-rose-bg`, `--tint-violet-bg`).
   - **Zone 3 (`<= 5%` Saturated Signal Ink):** High-saturation colors reserved strictly for primary CTAs (`.va-pill-btn.primary`), active SVG progress rings, and live fault indicators.
2. **Interactive Affordance Pill Law & 5-Stop Corner Radius Dial (`data-corners="auto|sharp|subtle|rounded|soft"`):**
   - Structural cards obey `--radius-card` (`0px`, `6px`, `12px`, `18px`), while interactive buttons (`.va-pill-btn`), segmented controls (`.va-seg-pills`), and `.va-icon-well` badges ALWAYS preserve tactile rounded geometry (`999px` / `9px`) even when `data-corners="sharp"` is active.
   - Scope editorial `0px` overrides strictly to `:root[data-corners="auto"] .editorial-zero-box` and `:root[data-corners="sharp"]` so choosing `subtle`, `rounded`, or `soft` visibly rounds cards across all 17 tiers.
