# Architecture & Three Pillars

Quiet UI separates how a screen looks, how numbers are plotted, and how the message is written into three focused skills—**`quiet-ui`**, **`quiet-evidence`**, and **`quiet-bridge`**. Instead of asking an AI coding agent or developer to juggle layout physics, SVG coordinate math, and executive framing in one giant prompt, each pillar owns one clear job.

> [!NOTE]
> You do not need to learn every technical rule up front. Start with plain goals—readable text, honest numbers, and a layout tailored to the reader—and let each pillar supply the exact building blocks.

---

## Plain-Language Overview of the Three Pillars

### 1. `quiet-ui` — Surfaces, Shells, and Physical Readability
Think of `quiet-ui` as the **room and furniture** of your interface. Whether someone is reading a printed handout, tapping a hospital bedside screen, or inspecting a desktop workbench, the surface automatically adapts:
- **7 delivery mediums (`M1`–`M7`)**: Tuned rules for paper and print (`M1`), editorial web articles (`M2`), stateful desktop/mobile web apps (`M3`), walk-up point-of-interest kiosks (`M4`), 10-foot ambient wall displays (`M5`), collimated optical HUDs (`M6`), and transparent window overlays (`M7`).
- **5 polymorphic navigation shells (`N0`–`N4`)**: Layouts morph cleanly from a distraction-free document stage (`N0`), an adaptive left rail (`N1`), a sticky top bar (`N2`), or a header-plus-rail command deck (`N3`), down to a thumb-friendly mobile bottom dock (`N4`, strictly restricted to viewports under `700px`).
- **4 calibrated themes (`white`, `paper`, `dark`, `dark-paper`)**: Built with OKLCH color tokens and a shared `--chart-1..5` palette so light, warm-paper, and dark surfaces stay readable without manual color tweaking.
- **Hard `11px` legibility floor**: No CSS rule or rendered element is allowed to shrink below `11px`, and sticky header bars stay compact so content owns the first screen.

### 2. `quiet-evidence` — Calibrated Charts and Engineering Diagrams
Think of `quiet-evidence` as the **drafting table**. Instead of letting an LLM guess SVG pixel coordinates freehand—which often causes overlapping labels or clipped axes—you describe data or system topology in a structured JSON spec and let a deterministic compiler draw the figure:
- **6 calibrated modalities**: Covers (1) scalar readouts and gauges, (2) tables and matrices, (3) hardware bitfields and registers, (4) analytical and spectral plots, (5) multi-channel waveforms and timing diagrams, and (6) schematics and topologies.
- **Zero freehand SVG guessing**: Static specs compile through `compile_evidence.py`, while live browser charts route through `window.QuietSvgLayout` and `QuietEChartsDefaults` so tick intervals, margins, and label clearances stay mathematically consistent.

### 3. `quiet-bridge` — Plain-Language Framing Without Changing the Numbers
Think of `quiet-bridge` as the **translator** in the room. A plant operator, a systems engineer, and a program manager all look at the same system, yet each needs a different level of detail and speed:
- **7 audience lenses**: `Technician & Operator`, `Discipline Engineer`, `Project Systems Engineer`, `Program Manager`, `Consumer & Common Reader`, `Educator & Mentor`, and `Student & Learner`.
- **3 decision tempos**: `Tactical Seconds` (5–15 second anomaly triage), `Executive Minutes` (1–3 minute gate review), and `Analytical Deep Dive` (10–45 minute peer-reviewed proof).
- **The Numerical Conservation Law**: Presentation may adjust wording and jargon density, **never** the underlying truth. Sample counts (`N`), timestamps, units, limits, and baselines must trace back to the same verified data source across web briefs, slide decks, and printed handouts.

---

## Pillar Comparison Table

| Pillar | Plain-Language Role | Core Inventory | Primary Guarantee |
| :--- | :--- | :--- | :--- |
| **`quiet-ui`** | Layout, navigation, and visual comfort | 7 mediums (`M1`–`M7`), `N0–N4` shells, 4 themes | Readable typography (`>= 11px`), clean focus, strict CSS token use |
| **`quiet-evidence`** | Accurate charts, scopes, and schematics | 6 modalities, 3 rigor levels (`L1`–`L3`) | Deterministic geometry, explicit units, zero freehand SVG guessing |
| **`quiet-bridge`** | Audience framing and red-team review | 7 audience lenses, 3 decision tempos | Numerical Conservation Law—same verified facts at every depth |

---

## End-to-End 3-Pillar Flow

The pipeline diagram below is compiled directly from an inline `urn:quiet-ui:schema:v9:schematic` (`schematic_kind: "pipeline"`) JSON block—showing how verified tokens and data travel through all three pillars into audited screen, print, demo, and documentation outputs.

```quiet-evidence
{
  "$schema": "urn:quiet-ui:schema:v9:schematic",
  "id": "quiet-ui-three-pillar-flow",
  "schematic_kind": "pipeline",
  "metadata": {
    "title": "Quiet UI Three-Pillar Architecture Flow",
    "description": "Tokens and verified data flow through quiet-ui, quiet-evidence, and quiet-bridge into audited outputs.",
    "rigor_level": "L1",
    "audience": "Developers & Technical Reviewers"
  },
  "stages": [
    "Tokens + Data Truth",
    "Three-Pillar Engine",
    "Verified Outputs"
  ],
  "nodes": [
    {
      "id": "tokens",
      "label": "4-Theme CSS Tokens",
      "metric": "OKLCH · N0–N4",
      "stage": 0
    },
    {
      "id": "data",
      "label": "Verified Data Truth",
      "metric": "Units · Epochs · N",
      "stage": 0
    },
    {
      "id": "ui",
      "label": "quiet-ui",
      "metric": "7 Mediums · Shells",
      "stage": 1,
      "focal": true
    },
    {
      "id": "evidence",
      "label": "quiet-evidence",
      "metric": "6 Modalities · 1-2-5",
      "stage": 1,
      "focal": true
    },
    {
      "id": "bridge",
      "label": "quiet-bridge",
      "metric": "7 Lenses · 3 Tempos",
      "stage": 1,
      "focal": true
    },
    {
      "id": "screen-print",
      "label": "Screen & Print",
      "metric": "11px+ · Safe Margins",
      "stage": 2,
      "stroke": "var(--status-ok)"
    },
    {
      "id": "demo",
      "label": "Interactive Demo",
      "metric": "Chart | Table · Copy",
      "stage": 2,
      "stroke": "var(--status-ok)"
    },
    {
      "id": "docs",
      "label": "Verified Docs",
      "metric": "Static + CDP Pass",
      "stage": 2,
      "stroke": "var(--status-ok)"
    }
  ],
  "edges": [
    { "from": "tokens", "to": "ui" },
    { "from": "tokens", "to": "evidence" },
    { "from": "data", "to": "evidence" },
    { "from": "data", "to": "bridge" },
    { "from": "ui", "to": "screen-print" },
    { "from": "ui", "to": "demo" },
    { "from": "evidence", "to": "demo" },
    { "from": "evidence", "to": "docs" },
    { "from": "bridge", "to": "screen-print" },
    { "from": "bridge", "to": "docs" }
  ]
}
```

---

## Technical Contract Summary

1. **Token Layering**: Customizations live in `customizations/<brand>/styles/overrides.css` rather than mutating core files in `tokens/`, `src/css/`, or `src/chrome/` during feature work.
2. **Pre-Edit Grounding**: Every interface declares its target medium (`M1`–`M7`), shell (`N0`–`N4`), chromatic budget, and **Data-to-Widget Binding Map** before writing HTML or CSS.
3. **Zero-State & Reversibility Contracts**: Empty views distinguish first-run, filtered (`Clear filters` action), warmup (`Warming up — N samples collected` when `N < 10`), and stale retained feeds, while destructive actions follow tiered confirmation (`>= 7s` Undo Toast, `ARM -> EXECUTE`, or `<dialog closedby="any">`).
