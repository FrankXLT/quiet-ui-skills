# Quiet UI — Chromatic Purpose Budgets

Quiet UI treats color as an exhaustible cognitive budget rather than aesthetic decoration. Uncontrolled chroma induces visual fatigue and masks critical state transitions. Every Quiet UI interface must declare and adhere to one of four mutually exclusive **Chromatic Purpose Budgets**:

1. **Archival Proof** (High-integrity reports, RFC specifications, scientific evidence)
2. **Pedagogical Flow** (Step-by-step tutorials, multi-stage pipelines, onboarding journeys)
3. **Decision Contrast** (Comparison matrices, trade-off forks, branching logic)
4. **Quiet Cockpit** (Grid SCADA, ICU bedside monitoring, operations centers)

---

## 1. The Four Chromatic Purpose Budgets

```
+-----------------------------------------------------------------------------+
|                          CHROMATIC PURPOSE DIAL                             |
|                                                                             |
|  [Archival Proof]      [Pedagogical Flow]  [Decision Contrast] [Quiet Cockpit] |
|  >= 90% Neutral Ink    Role Hue Pipeline   50% Muted Baseline  Monochrome Nom |
|  1 Focal Accent        Discovery -> Deploy Accent Choice Path  Zero Passive Red|
+-----------------------------------------------------------------------------+
```

### Budget Specification Matrix

| Purpose Budget | Color Invariant | Primary Tokens Permitted | Strict Chromatic Restriction |
| :--- | :--- | :--- | :--- |
| **Archival Proof** | $\ge 90\%$ surface area composed of monochrome neutral ink. Single focal accent. | `--text-primary`, `--text-secondary`, `--border-hairline`, `--accent-focal` | Zero multi-hue decorative badges. No secondary accent gradients. |
| **Pedagogical Flow**| Predictable step-to-hue binding across multi-stage sequences. | `--tint-indigo-*`, `--tint-emerald-*`, `--tint-amber-*`, `--tint-violet-*` | Hues must never change semantic meaning between steps. |
| **Decision Contrast**| Background options rendered at 50% opacity neutral baseline. Winner receives full saturation. | `--text-muted`, `--border-hairline`, `--accent-primary`, `--status-ok` | Non-selected branches must never compete for focal visual weight. |
| **Quiet Cockpit** | 100% monochrome dark theme during nominal telemetry. Chroma reserved for faults. | `--bg-shell`, `--bg-card`, `--text-secondary`, `--status-warn`, `--status-err` | Amber and Crimson strictly forbidden on passive labels and cards. |

---

## 2. Detailed Budget Protocols

### Budget A: Archival Proof
Targeted at peer-reviewed scientific papers, security audit findings, and regulatory filings.
- **Surface**: Pure white (`#FFFFFF`) or paper (`#FCFBF8`).
- **Contrast**: Text ink must exceed 12:1 contrast ratio against the canvas.
- **Focal Allocation**: Exactly one single chromatic element per viewport section (e.g., the primary regression curve or the verified security badge).

### Budget B: Pedagogical Flow
Guides operators through structured multi-phase cognitive procedures (Discovery $\rightarrow$ Configure $\rightarrow$ Verify $\rightarrow$ Deploy).
- Stage 1 (Discovery): Cool Slate / Indigo (`--tint-indigo-fg`, `--tint-indigo-bg`).
- Stage 2 (Configuration): Warm Bronze / Amber (`--tint-amber-fg`, `--tint-amber-bg`).
- Stage 3 (Verification): Luminous Violet (`--tint-violet-fg`, `--tint-violet-bg`).
- Stage 4 (Acquisition / Active): Verified Emerald (`--tint-emerald-fg`, `--tint-emerald-bg`).

### Budget C: Decision Contrast
Designed for architectural trade-off evaluations and bifurcated decision trees.
- Baseline or discarded alternatives render in desaturated monochrome (`opacity: 0.55`, `color: var(--text-muted)`).
- The recommended, selected, or active path renders with 100% opacity, crisp hairline border (`var(--accent-focal)`), and high-contrast callout chips.

### Budget D: Quiet Cockpit (`ISA-101` / `NRC NUREG-0700` / `FDA IEC 62366` / `NASA-STD-3001`)
In a power grid control room, ICU bedside monitor, or mission operations center, "quiet" means no saturated colors are illuminated during nominal operations:
- **Nominal Operations (`data-variant="status"` + Heatmaps)**: Nominal pills render strictly quiet — transparent fill, `0px` border, Title Case `Nominal` in `var(--text-secondary)` with a subtle `6px` CSS dot indicator (`::before`). Nominal telemetry cells (`data-role="bitcell"` / matrix heatmaps) render in neutral `var(--bg-elevated)` rather than green capsules so isolated excursions immediately pop.
- **Out-of-Spec Excursions**: High-chroma Amber (`--status-warn` via `color-mix(in oklab, ...)`, `2.5px` start bar, `▲` glyph) triggers only upon advisory/warning/stale threshold breach. High-chroma Crimson (`--status-danger`, `2.5px` start bar, `◆` glyph) triggers only upon critical tripwire, emergency fault, or interlock violation.
- **Atomic Label Purity**: Never concatenate `[ BRACKETED ]` wrappers or quantitative margins (`Margin +18.0%`) inside a status pill. Print atomic state text inside `.va-pill` and render quantitative margin in its own adjacent `.qe-scalar-margin` span.
- **Monochrome Metadata Keycaps (`data-variant="tag"`)**: Hardware access bits (`W1C`, `RW`), interlocks, live hex values, and specimen provenance render exclusively in neutral surface/hairline contrast (`--bg-elevated`, `--border-subtle`, `--text-secondary`). Under no circumstances may passive labels, specimen counters, or read-only (`RO`) text borrow alarm hues or green badges.

---

## 2B. Page-Wide Visual Coherence Budget (`<= 3` Card Structures & `1` Palette)

Every multi-panel dashboard or monograph MUST read as one unified system rather than a sampler buffet across the 41 Component Library specimens:
- **`<= 3` Repeating Card Structures Per Page**: Every analytical card on a page must share **one header layout** (`Title` left + plain unboxed muted `.va-meta-inline` stat right, at most `1` semantic state `.va-badge`), **at most `1` chart per half-width card** (never stuffing 2 separate mini-charts side-by-side inside a half-width card), and **one unified `.booktabs` hairline row style** across all structured lists and directories (never mixing `.booktabs` tables with nested pill-box clouds).
- **One Cohesive Chart Palette Page-Wide**: Every chart on a page must draw from one consistent `--chart-1`..`--chart-5` token ramp (`--accent-primary`, `--tint-indigo-fg`, `--tint-emerald-fg`, `--tint-amber-fg`, `--text-muted`). Single-metric plots use `1` primary accent (`--chart-1`) plus neutral ink; categorical breakdowns reuse the same ordered `--chart-1..5` palette across rows rather than switching to uncoordinated blue/green/brown combos mid-page.

---

## 3. Token Allocation Table

| Token Reference | Archival Proof | Pedagogical Flow | Decision Contrast | Quiet Cockpit |
| :--- | :--- | :--- | :--- | :--- |
| `--accent-focal` | 1 Focal Target | Shared Pipeline | Winner Node | Fault Excursion |
| `--text-muted` | Footnotes only | Step Meta | Rejected Options | Nominal Telemetry |
| `--status-ok` | Final Seal | Stage Complete | Validated Path | Nominal Indicator |
| `--status-warn` | Forbidden | Attention Step | Degraded Tradeoff| Threshold Excursion |
| `--status-err` | Audit Failure | Blocking Step | Ineligible Option| Emergency Trip |

---

## 4. Concrete CSS Architecture

```css
@layer quiet.chromatic, quiet.components;

@layer quiet.chromatic {
  /* Archival Proof Container */
  .va-budget-archival {
    background: var(--bg-canvas);
    color: var(--text-primary);
    border: 1px solid var(--border-hairline);
  }
  .va-budget-archival .va-focal-point {
    color: var(--accent-focal);
    font-weight: 600;
  }

  /* Pedagogical Flow Stepper */
  .va-pipeline-step[data-stage="1"] {
    background: var(--tint-indigo-bg);
    color: var(--tint-indigo-fg);
  }
  .va-pipeline-step[data-stage="2"] {
    background: var(--tint-amber-bg);
    color: var(--tint-amber-fg);
  }
  .va-pipeline-step[data-stage="3"] {
    background: var(--tint-violet-bg);
    color: var(--tint-violet-fg);
  }
  .va-pipeline-step[data-stage="4"] {
    background: var(--tint-emerald-bg);
    color: var(--tint-emerald-fg);
  }

  /* Decision Contrast Baseline vs Winner */
  .va-decision-alt {
    opacity: 0.55;
    border: 1px dashed var(--border-hairline);
    filter: grayscale(100%);
    transition: opacity 0.2s ease, filter 0.2s ease;
  }
  .va-decision-focal {
    opacity: 1;
    border: 1px solid var(--accent-focal);
    background: var(--bg-surface);
    box-shadow: 0 0 0 1px var(--accent-focal);
  }

  /* Quiet Cockpit Telemetry Card */
  .va-cockpit-readout {
    background: var(--bg-card);
    border: 1px solid var(--border-hairline);
    color: var(--text-secondary);
  }
  .va-cockpit-readout[data-alarm="nominal"] .va-readout-value {
    color: var(--text-primary);
  }
  .va-cockpit-readout[data-alarm="warning"] {
    border-color: var(--status-warn);
    background: var(--status-warn-bg);
    color: var(--status-warn);
  }
  .va-cockpit-readout[data-alarm="critical"] {
    border-color: var(--status-danger);
    background: var(--status-err-bg);
    color: var(--status-danger);
  }
}
```

---

## 5. HTML Macro Implementation

```html
<!-- Archival Proof Monograph Figure -->
<figure class="va-budget-archival va-card">
  <figcaption class="va-kicker">Proof 04-A: Convergence Trajectory</figcaption>
  <div class="va-data-graph">
    <!-- 95% monochromatic traces in grey hairline -->
    <svg class="va-waveform">...</svg>
  </div>
  <p class="va-prose">
    Equilibrium established at <span class="va-focal-point">4.200 GHz</span> within certified tolerances.
  </p>
</figure>

<!-- Quiet Cockpit Telemetry Node -->
<div class="va-cockpit-readout va-card" data-alarm="nominal">
  <span class="va-kicker">REACTOR CORE PRESSURE</span>
  <span class="va-readout-value va-nums">14.72 MPa</span>
  <span class="va-readout-state">NOMINAL CRUISE</span>
</div>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | Operational Hazard | Quiet UI Resolution |
| :--- | :--- | :--- |
| Rainbow Status Badges in nominal monitoring | Operator habituates to colored noise; fails to recognize emergency alarm. | Apply Quiet Cockpit rule: 100% monochrome until threshold excursion. |
| Crimson decorative card borders | Operator interprets decorative element as critical hardware failure. | Reserve `--status-err` strictly for blocking faults and safety trips. |
| Multicolored pie chart with 12 distinct pastels | Impossible to cross-reference with legend in low light or on grayscale print. | Switch to monochrome bar chart sorted by value with direct label callouts. |
| Unmarked decision matrix columns with equal weight | Reader cannot discern recommended path from rejected trade-offs. | Apply Decision Contrast: 50% opacity on rejected options, focal accent on winner. |
