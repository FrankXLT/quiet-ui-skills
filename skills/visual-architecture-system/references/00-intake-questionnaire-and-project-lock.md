# Gate 0: Brownfield Project Lock (`.visual-lock.json`) & 6-Axis Intake Scorecard

## 1. Brownfield Protection Law (Never Clobber Existing Project Identity)

Before modifying any file in an existing repository (such as a **Task & Calendar Planner** or an existing **Home Assistant** dashboard), inspect the project root for `.visual-lock.json` or existing theme stylesheets:
1. **When `.visual-lock.json` exists (`Mode M1`):**
   - Treat `color_theme`, `card_chrome`, `layout_shells`, and `locked_invariants` as immutable invariants.
   - If the user asks to *"make the view more compact"* or *"tighten spacing"*, ONLY adjust the Orthogonal Density Dial (`D1` $\rightarrow$ `D4`) and local padding/gaps. Never replace the project's light/paper surface with a dark terminal or strip its custom components.
2. **When working on an unlocked existing repo (`Mode M2`):**
   - Offer to generate `.visual-lock.json` capturing its current palette, typography, corner geometry, and view topology before applying targeted changes.

### Canonical `.visual-lock.json` Schema (Workspace Planner Reference Lock)

```json
{
  "$schema": "https://visual-architecture.local/schemas/visual-lock-v4.5.json",
  "project": "Workspace Planner",
  "mode": "M1_PRESERVE_AND_TUNE",
  "archetype_tier": "11. App-4 (Task & Calendar Planner)",
  "color_theme": "S1_PURE_WHITE_ALABASTER",
  "default_density": "D2_BALANCED_WORKSPACE",
  "color_restraint": "C3_MODERN_EXPRESSIVE",
  "corner_geometry": "ROUNDED_12PX",
  "navigation_topology": "N1_FULL_HEIGHT_LEFT_SIDEBAR",
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

## 2. Single-Pass 6-Question Intake Scorecard (Greenfield `Mode M3`)

When a user requests a brand-new deliverable and has not specified its visual parameters, present this compact scorecard so they can reply with a single 6-code shorthand (e.g., `11, D2, S1, C3, rounded, N1` or `14, D3, S4, C2, subtle, N1`):

> **Visual Architecture v4.5 Intake Scorecard** *(Reply with 6 codes, e.g. `11, D2, S1, C3, rounded, N1` or `14, D3, S4, C2, subtle, N1`):*
> 1. **Deliverable Archetype (`01`–`17`):**
>    - *Docs & Decks:* `01` Academic Monograph · `02` Executive Memo (`BLUF` + Mermaid) · `03` Normative RFC (+ Mermaid FSM) · `04` SDK/API Reference · `05` Split-Pane Runbook (+ Mermaid Seq) · `06` Parametric Worksheet · `07` Briefing Stage
>    - *Data, Workspaces & Explorers:* `08` High-Density Data Table (`1px` Grid) · `09` Live Metrics & Time-Series Console · `10` Compact Issue & Ticket Tracker · `11` Task & Calendar Planner (+ Focus Hero) · `12` KPI & Analytics Dashboard (Bento Grid) · `13` Daily Pacing & Wellness Planner (+ Readiness Ring Hero) · `14` **`App-Tree` Schema, Tree & File Explorer Workbench**
>    - *Home Assistant:* `15` HA-1 Ambient Wall Kiosk (Monet + Frosted Glass) · `16` HA-2 Room-First Wall Control Panel · `17` HA-3 Crease-Aware Foldable & Phone Controller
> 2. **Compactness / Density (`D1`–`D4`):** `D1` Relaxed · `D2` Balanced *(Default)* · `D3` Compact · `D4` Ultra-Dense Hairline
> 3. **Color Theme (`S1–S4`):** `S1` Pure White · `S2` Warm Paper *(Default)* · `S3` Dark Paper · `S4` Obsidian Dark
> 4. **Color Policy (`C1–C3`):** `C1` Quiet Cockpit (Monochrome) · `C2` Semantic Accents · `C3` **Modern Expressive** (1 Tinted Hero Card + `.va-icon-well` Soft Tints)
> 5. **Corner Geometry (`auto|sharp|subtle|rounded|soft`):** `auto` Tier Default · `sharp` (`0px`) · `subtle` (`6px`) · `rounded` (`12px`) · `soft` (`18px`)
> 6. **Native Navigation Topology (`N0`–`N4`):**
>    - `N0` **Zero-Chrome Kiosk / Ambient Canvas** (`07. Deck-1`, `15. HA-1` — `0px` nav bars)
>    - `N1` **Full-Height Left Sidebar / Spine** (`10. App-1`, `11. App-4`, `13. App-5`, `14. App-Tree`, `16. HA-2` — `220px` collapsible to `60px` via `.va-hamburger-btn`)
>    - `N2` **Single Top Command Bar** (`08. Bridge-2`, `12. App-3` — single `42px` borderless `.va-tab-link` bar)
>    - `N3` **Hybrid Enterprise L-Shell** (`04. Doc-4B` — `38px` global top bar + `220px` local left section tree)
>    - `N4` **Sticky Bottom Thumb-Zone Dock** (`17. HA-3` and `R5` `390px` mobile — `48px–52px` 5-slot bottom thumb bar)
