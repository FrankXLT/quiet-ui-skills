# Quiet UI v9.6.0 — Master Engineering Workflows & Architecture

> **Document Class**: Authoritative Architecture Specification  
> **Target Version**: Quiet UI v9.6.0 (`3-Pillar Unified Continuum`)  
> **Standards Basis**: NIST SP 811, FDA IEC 62366, ISA-101 / NRC NUREG-0700, NIST AI RMF 100-1, SAE J1939, NAVAIR FTM-108, NASA-STD-3001, GAO/USWDS, NAEP/Census ACS

---

## 1. The 3-Pillar Compositional Philosophy

Quiet UI v9.6 abandons rigid monolithic page templates and artificial walls between "diagrams" and "dashboards." Instead, any user-facing interface, monograph, console, or report—across **Clinical Care & Life Sciences, Cloud/Cyber/AI Ops, Industrial Grid & Manufacturing, Automotive & Embedded Hardware, Civic Finance & Public Data, and Earth Science & STEM Education**—is decomposed into three strictly orthogonal concerns:

```
                                      QUIET UI v9.6
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        ▼                                   ▼                                   ▼
  Pillar 1: quiet-ui              Pillar 2: quiet-evidence            Pillar 3: quiet-bridge
(Qualitative Delivery Mediums)     (Quantitative Metrology & Data)    (Presenter -> Audience Vector)
```

1. **Pillar 1 — Qualitative Delivery Medium Physics & Shells (`skills/quiet-ui/`)**:
   - Manages physical optical constraints, viewing distance, container bounds, and chromatic rations across seven operational mediums: `Paper/Print` (M1), `Editorial Web` (M2), `Stateful Web App` (M3), `Walk-Up Terminal` (M4), `Ambient Kiosk` (M5), `Collimated Optical HUD` (M6), and `Transparent Window Overlay` (M7).
   - Rations color through four strict semantic budgets: *Archival Proof* (90% neutral ink), *Pedagogical Flow*, *Decision Contrast*, and *Quiet Cockpit* (monochrome nominal state grounded equally in `ISA-101`, `FDA IEC 62366`, and `NASA-STD-3001`; amber/crimson reserved exclusively for active off-nominal excursions).
   - Provides pre-built zero-`!important` `@layer` CSS and canonical HTML shells (`N0` to `N4`).

2. **Pillar 2 — Unified Quantitative Evidence & Metrology (`skills/quiet-evidence/`)**:
   - Manages data fidelity, unit calculus, scale intervals, and physical topology from raw truth outward across six modalities: (1) *Scalars & Gauges*, (2) *Tables & Matrices*, (3) *Bitfields & Registers*, (4) *Analytical & Spectral Plots*, (5) *Waveforms & Timing*, and (6) *Schematics & Topologies*.
   - Scales each modality across a three-level rigor continuum: `L1 · Orientation` (Mermaid grade, rapid mental models), `L2 · Governance & Architecture` (SysML/ATO/CONSORT grade, trust boundaries, PPSM matrices), and `L3 · Physical, Clinical & Metrological` (clinical, industrial & laboratory metrology grade: NIST $1\text{--}2\text{--}5$ intervals, log-decade ticks, Shewhart SPC `UCL/CL/LCL`, $\pm 1\sigma$/95% CI bands, discrete measured markers vs. continuous analytical models).
   - Enforces deterministic compilation via zero-dependency Python/JS builders consuming structured JSON specs (`urn:quiet-ui:schema:v9:*`), completely terminating freehand SVG coordinate guessing.

3. **Pillar 3 — Directional Presenter-to-Audience Bridge & Murder Board (`skills/quiet-bridge/`)**:
   - Formulates communication as an asymmetric vector across **6 Universal Domain Clusters (22 presenter-to-audience views)**: `Presenter Source` &rarr; `Audience Lens` $\times$ `Decision Tempo`.
   - Projects across seven foundational audience lenses: *Technician/Operator*, *Discipline Engineer*, *Project/Systems Engineer*, *Program Manager*, *Consumer/Common Reader*, *Educator/Mentor*, and *Student/Learner*.
   - Operates across three decision tempos: *Tactical* (5–15s anomaly intervention), *Executive* (1–3m gate compression *within that leader's discipline*), and *Analytical* (10–45m full evidentiary proof).
   - Enforces the **4 Universal Audience Evaluation Invariants** across every domain view:
     1. **Baseline & Corridor**: Every live reading sits inside a calibrated reference band, healthy clinical/operating range, or `UCL/LCL` corridor.
     2. **Epistemic Provenance**: Discrete empirical observations (`±1σ` / `95% CI`), continuous theoretical/analytical fits, and stale/faulty channels are optically distinct.
     3. **Margin & Consequence**: Threshold distance and directional hazard (`CMD vs ACT`, titration headroom, `C_pk`, error-budget burn) remain legible without mental arithmetic.
     4. **Actionable Disposition**: Each screen pairs evaluation truth with the single clear next decision, protocol escalation, or guarded `ARM -> EXECUTE` step.
   - Enforces active protocols: *"Grill Me" Audience Intake*, *Adversarial Murder Board*, and the *Review-Room Dual-Layer Pattern*.

---

## 2. Workflow A — New Interface / Document Intake

When an agent or engineer receives a request to build, redesign, or audit an interface, the workflow executes through four sequential gates:

```
[User Prompt] ──► Gate 1: Bridge Intake ──► Gate 2: Medium Lock ──► Gate 3: Evidence Spec ──► Gate 4: Murder Board
```

### Step 1. Audience Intake ("Grill Me" Protocol)
Before touching HTML or CSS, the agent executes the 3-question intake interrogation:
1. **Audience Lens**: Who is the final decision-maker?
   - *Technician / Operator*: Requires physical pinouts, step-by-step interlocks, go/no-go redlines.
   - *Discipline Engineer*: Requires first-principles physics, governing equations, residuals, and $\pm 1\sigma$ uncertainty.
   - *Project / Systems Engineer*: Requires interface boundaries, verification matrices, and cross-subsystem margins.
   - *Program Manager*: Requires schedule critical path, earned value, risk corridors, and cost variance.
   - *Consumer / Common Reader*: Requires plain-language human anchors, clear summaries, and direct call-to-actions.
   - *Educator / Mentor*: Requires concept-before-symbol pacing, prerequisite DAG anchoring, worked derivations, and interactive parameters.
   - *Student / Learner*: Requires Cognitive Speed Limit scaffolding, structured experimental reporting, apparatus schematics, and authentic NIST units.
2. **Decision Tempo**: Under what operational clock will this artifact be consumed?
   - *Tactical (5–15 seconds)*: Live anomaly triage or execution checklist.
   - *Executive (1–3 minutes)*: Gate compression in the leader's native discipline.
   - *Analytical (10–45 minutes)*: Full peer-reviewed evidentiary proof.
3. **Delivery Medium**: What physical surface displays the artifact?
   - Print sheet (`M1`), desktop monitor (`M2`/`M3`), walk-up POI (`M4`), ambient wall (`M5`), or optical HUD (`M6`/`M7`).

### Step 2. Data-to-Widget Binding, Medium & Chromatic Lock
The agent inspects real backend schemas and emits the **Pre-Edit Output Contract** (`skills/quiet-ui/foundation/data-grounding-and-widget-binding.md`):
- **Data-to-Widget Binding Map**: Exact source field, physical unit, omitted absent sub-slots (`target == null`), and `Warming up — N samples collected` fallback when `N < 10`.
- **Medium**: Selected from `M1` through `M7`.
- **Chromatic Purpose Budget**: Selected from:
  - *Archival Proof*: $\ge 90\%$ neutral black/gray ink, single accent token for focal result.
  - *Pedagogical Flow*: Consistent thematic role tints across process phases.
  - *Decision Contrast*: Muted baseline series vs. prominent recommended branch.
  - *Quiet Cockpit*: Completely monochrome during nominal operations; high-chroma amber/crimson reserved strictly for active excursions.
- **Navigation Shell**: Selected from `N0` (undecorated stage), `N1` (left rail/drawer), `N2` (top bar), `N3` (composite), or `N4` (mobile bottom dock).
- **Container Geometry**: Concentric radii math:
  $$\text{radius}_{\text{inner}} = \max(0, \text{radius}_{\text{card}} - \text{padding})$$

### Step 3. Quantitative Evidence Modeling
For every plot, table, gauge, or schematic, the agent consults `skills/quiet-evidence/`:
- Formulates the governing equation and NIST SP 811 units.
- Selects the target rigor level (`L1`, `L2`, or `L3`) and verifies sample size `N` and policy effective dates before grading historical runs.
- Emits a clean JSON specification conforming to `urn:quiet-ui:schema:v9:<modality>`.
- Compiles SVG geometry deterministically via `compile_evidence.py`, or routes browser-drawn SVG charts through `window.QuietSvgLayout` (`quiet-svg-chart-layout.js`) so ticks, gutters, label wrapping, and reference halos never collide.

### Step 4. Adversarial Murder Board Audit
Before declaring the interface complete, the agent runs the Murder Board rubric matching the audience lens. If any redline triggers (e.g., data-slot fabrication, cross-pool borrowed targets, missing units, ungrounded Bezier splines, amber status during nominal states, or table truncation on desktop), the artifact is blocked.

---

## 3. Workflow B — Multi-Audience Distillation & Numerical Conservation

A frequent failure mode in technical reporting is creating separate, unlinked documents for executives, engineers, and operators, causing numbers to drift. Quiet UI v9.2 enforces the **Numerical Conservation Law**:

> **Numerical Conservation Invariant**: When distilling one primary system or incident into multiple audience views, the underlying physical truth (parameters, sample rates, abort limits, timestamps, and citations) MUST derive from a single canonical JSON dataset and explicit Data-to-Widget Binding Map. Presentation alters only framing, compression tempo, and coordinate density—never the underlying numbers or unbacked targets.

```
                         Canonical Numerical Dataset (JSON Truth)
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        ▼                                   ▼                                   ▼
  Operator View (Tactical)            Executive View (Minutes)           Discipline Engineer (Proof)
- Real-time limit redlines          - Net margin & critical path        - Log-decade Allan deviation
- Interlock override switches       - Variance & mitigation cost        - Residual errors & ±1σ CI
- Connector pinout callouts         - Go/No-Go decision matrix          - Calibration temperature
```

### Multi-Audience Projection Matrix

| Audience Lens | Primary Unit of Proof | Essential Visual Modality | Information Scrubbed |
| :--- | :--- | :--- | :--- |
| **Operator** | Relay interlock states, dB margin | Waveforms (M5) & Schematics (M6) | Multi-year budget variance, academic citations |
| **Discipline Eng** | Allan deviation $\sigma_y(\tau)$, $\pm 1\sigma$ bands | Analytical Plots (M4) & Bitfields (M3) | High-level marketing summaries, vague trendlines |
| **Systems Eng** | Interface control margins, PPSM tables | Structured Matrices (M2) & Schematics (M6) | Low-level transistor physics, vendor pitch decks |
| **Program Manager** | Critical path variance, risk envelope | Gauges (M1) & Decision Tables (M2) | Uncalibrated raw telemetry sweeps, debug registers |
| **Common Reader** | Physical safety status, simple impact | Plain Gauges (M1) & Linear Flows (M6) | Hexadecimal offsets, raw logarithmic calculus |
| **Educator & Mentor** | Step-by-step DAG progression, worked derivations | Parametric Schematics (M6) & Interactive Sweeps (M4) | Unanchored symbolic formulas without intuition |
| **Student & Learner** | Controlled experiment variables, apparatus schematics | Scaffolding Plots (M4) & Structured Glossaries (M2) | Unexplained jargon, compressed multi-step jumps |

---

## 4. Workflow C — Screen-to-Paper Dual Physics (`@media screen` <-> `@media print` / `@page`)

Quiet UI documents are authored in standard semantic HTML, but behave as dual-physics systems across screen and print mediums:

| Feature / Attribute | Screen Mediums (`M2`, `M3`, `M4`) | Paper & Print Medium (`M1`) |
| :--- | :--- | :--- |
| **Shell Navigation** | Interactive topbars, rails, drawers, tabs (`N1–N4`) | Completely stripped (`display: none;`) |
| **Viewport Bounds** | Fluid `100vw`, `100dvh`, container queries | Fixed `@page { size: letter portrait; margin: 15mm; }` |
| **Color Surfaces** | Dark, dark-paper, paper, white themes | High-contrast black ink on white/paper surface |
| **Grid Lines** | Muted hairlines (`var(--border-hairline)`) | Fine printable interpolation grid ($1\text{--}2\text{--}5$ ruler) |
| **Interactive Elements**| Hover tooltips, scrubbable cursors, accordions | Unrolled multi-slide strips, static callouts |
| **Test Conditions** | Collapsible drawer or modal inspect dialog | Explicit inline tabular metadata header block |

### The CSS Implementation Rule
All shell navigation and interactive dock elements are scoped inside `@layer shell`. In `src/css/01-stage-and-containers.css`, the print media block cleanly unrolls the content:

```css
@page {
  size: letter portrait;
  margin: 15mm 15mm 20mm 15mm;
}
@media print {
  @layer utilities {
    body {
      background: #ffffff;
      color: #0f172a;
    }
    .va-shell-topbar,
    .va-shell-rail,
    .va-shell-bottomdock,
    #va-studio-bar,
    .va-interactive-cursor {
      display: none;
    }
    .va-prose {
      max-inline-size: 100%;
    }
    .va-card,
    .va-panel-tonal {
      break-inside: avoid;
      border: 1px solid #cbd5e1;
      background: #ffffff;
    }
    .va-table-wrap {
      overflow: visible;
    }
    .va-test-condition-block {
      display: table;
      inline-size: 100%;
      margin-block-end: 1rem;
      border: 1px solid #94a3b8;
    }
  }
}
```

---

## 5. Workflow D — Review-Room Dual-Layer Pattern

In critical engineering reviews (Flight Readiness Reviews, Key Decision Points, and Incident Tiger Teams), program managers and chief engineers sit in the same room. A dashboard catering to only one audience triggers failure: executives get lost in raw traces, while engineers distrust simplified summaries.

Quiet UI formalizes the **Review-Room Dual-Layer Pattern**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ UPPER LAYER: Executive & Program Gate Disposition Band (Decision Tempo: 1-3 Minutes)            │
│ ┌──────────────────────────┐ ┌──────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Disposition: GO (Pass)   │ │ Net Timing Margin: 18.6ps│ │ Critical Path Impact: 0 Days (On) │ │
│ └──────────────────────────┘ └──────────────────────────┘ └───────────────────────────────────┘ │
│ Recommendation: Authorize cutover to DWDM Grandmaster ring based on verified SLA compliance.    │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ LOWER LAYER: Discipline Engineering & Physical Evidence Proof (Decision Tempo: 15-45 Minutes)   │
│ ┌───────────────────────────────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ Modality 4: Modified Allan Deviation σ_y(τ) [L3]      │ │ Modality 5: Quad-Channel HIL Wave │ │
│ │ - Log-decade τ ∈ [1, 10⁴]s with ±1σ confidence bands  │ │ - 200ms sweep, 142ms cursor lock  │ │
│ │ - Test conditions: 193.4 THz, 293.15 K, 62.5 Msps     │ │ - Real-time BCJR LLR & Piezo Verr │ │
│ └───────────────────────────────────────────────────────┘ └───────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Upper Layer (Executive Gate Band)**:
   - Occupies the top $180\text{--}240\,\text{px}$.
   - Displays concise BLUF disposition (GO / CAUTION / NO-GO), quantitative margin ($+18.6\,\text{ps}$ safety buffer), critical path delta, and risk trade-space.
   - Preserves actual engineering units on all numbers.
2. **Lower Layer (Evidentiary Proof Stage)**:
   - Occupies the primary stage below.
   - Displays the uncompromised L3 physical data: spectral plots, HIL waveforms, and finite state machines proving the executive claim.
   - Provides full parameter blocks and mathematical provenance.

---

## 6. Workflow E — Clean-Room Open-Standards Schematic & Starter Customization Flows

Quiet UI v9.2 generates every systems schematic through first-party deterministic Python compilers and supports customized brand starters:

### 6.1 Clean-Room Open-Standards Schematic Compilers (`quiet-evidence`)
Structured topology and systems diagrams route through `skills/quiet-evidence/scripts/compilers/schematic_compiler.py` (`urn:quiet-ui:schema:v9:schematic`), covering:
- **Timed Sequence Lifelines (`sequence`)** — ITU-T Z.120 actors, lifelines, activation bars, sync/reply arrows, and timing annotations.
- **$N^2$ Interface Matrix (`n2_matrix`)** — NASA SP-2016-6105 diagonal subsystem blocks with upper/lower off-diagonal coupling callouts.
- **Fault Tree Analysis (`fault_tree`)** — NRC NUREG-0492 top event, OR/AND gates, and primary basic events.
- **Plant/Bus/Pipeline/Interlock/ER (`pid`, `bus`, `pipeline`, `interlock`, `er_lineage`) & Schedule/Matrix/Flow/Strip (`gantt`, `heatmap`, `sankey`, `strip_chart`)** — Orthogonal process instrumentation, DAG data pipelines, `2oo3` safety voting matrices, critical-path Gantt charts, WCAG-calibrated 2D heatmaps, flow-conserving Sankeys, 2D multivariate scatter clouds, and synchronized multi-track telemetry strip charts.

**Routing Strategy**: Author a structured JSON spec for the required system topology, validate conservation laws and bounds, and compile deterministic theme-bound `<svg>` output with halo labels and zero ungrounded freehand coordinates.

### 6.2 Starter Customization Kits (`personal-starter` & `brand-starter`)
The customization workspaces under `customizations/`:
- `customizations/personal-starter/` (personal portfolio / workspace theme — all 22 domain views)
- `customizations/brand-starter/` (enterprise brand palette — 18 product/engineering domain views)

**Inheritance Rule**: Starters override token values via `styles/overrides.css` while inheriting the core `@layer` hierarchy and Stage Portal machinery. In v9.2:
- Starters compile deterministically using `customizations/scripts/build_showcase.py`.
- They gain immediate access to all seven delivery mediums (`M1`–`M7`) and six data modalities (`M1`–`M6`) without modifying their `customization.json` schema.

---

## 7. Workflow F — Pedagogical Scaffolding & Experimental Lab Reporting (`Educator <-> Student`)

The `Educator <-> Student / Learner` vector is distinct from both specialist-to-specialist reviews and common-reader summaries. It optimizes for **durable mental-model construction under a strict Cognitive Speed Limit** without teaching sloppy, unitless habits:

### 7.1 The Three Pedagogical Pillars
1. **Concept-Before-Symbol & One-Variable-at-a-Time Pacing**:
   - Establish qualitative cause-and-effect intuition before introducing formal algebraic symbols or dense multi-variable equations.
   - For multi-parameter models, freeze all variables except one, graph the isolated relationship, then systematically introduce secondary perturbations.
2. **Semantic Equation-to-Visual Term Binding**:
   - Utilize `quiet-ui`'s `Pedagogical Flow` chromatic budget to bind individual equation terms (`OKLCH` role accents) directly to their corresponding schematic nodes, waveform channels, and plot curves on $\ge 90\%$ neutral surfaces.
   - Example: In the optical link budget equation $P_{rx} = P_{tx} \cdot G_{tx} \cdot L_{free} \cdot G_{rx}$, each gain and loss factor shares a unique semantic color token with its physical block in the receiver schematic.
3. **Developmental `L1 -> L2 -> L3` Rigor Ramp**:
   - Progression intentionally ramps from `L1` (conceptual mental model and high-level block diagram) to `L2` (functional interface states and parameter tables) to `L3` (authentic NIST units, $1\text{--}2\text{--}5$ intervals, discrete measured runs with repeatability corridors vs. continuous theoretical curves).
   - Students are never shown ungrounded cartoon charts; authentic metrology is scaffolded with clear explanatory callouts and plain-language glossaries.

### 7.2 The Asymmetric Flow: Educator vs. Student & Field Tech -> Systems Lead

```
[Educator as Presenter] ──► Prerequisite Anchoring ──► Worked Derivations ──► Interactive Probing
                                                                                      │
                                                                                      ▼
[Student as Presenter]  ──► Headline Claim & Law   ──► Bench Dumbbell     ──► Error & Critique
[Technician Escalation] ──► Symptom & Measurements ──► Bus/Thermal Isolate──► Recovery Gantt
```

- **Educator as Presenter**: Scrubs the "curse of expertise" (unexplained leaps in derivations, ungrounded notation), enforces worked examples before problem sets, and embeds interactive parameter sliders.
- **Student as Presenter (Lab Reports & Capstones)**: Replaces chronological data dumping with formal upward structure: *Headline Claim* &rarr; *Apparatus & Controlled Variables* &rarr; *Replicated Repeatability Dumbbell with $\pm 1\sigma$ Bounds* &rarr; *Physical Error Analysis & Self-Critique*.
- **Field Technician -> Systems Engineer (TSN Escalation)**: Structures field troubleshooting from observed physical symptom, hardware isolation checklist, and bay recovery Gantt before escalation signoff.

---

## 7A. Workflow G — Brownfield Retrofit, Persistent `.quiet-ui.md` & Drift Normalization

When replacing or overhauling a live production console rather than building greenfield from scratch, execute these seven migration controls so visual refinement never removes working features or drifts back into ad-hoc CSS:

1. **Load/Persist `.quiet-ui.md` + Capability Parity Ledger**: Check the target repo root for `.quiet-ui.md` before re-asking scoping questions (`audit_quiet_html.py --init-context`), and map every timeframe preset (`MTD`/`QTD`/`YTD` + Rolling `30d`/`90d`/`52w`), table, and export (`CSV`, `PNG`, `ZIP`) as `KEEP`, `CONSOLIDATE`, or `DEPRECATE`.
2. **Enforce Deprecation Blocklist**: Never render retired widgets merely because legacy keys remain on wire JSON; list retired selectors/copy under `## Deprecation Blocklist` in `.quiet-ui.md` (`[BLOCKLIST_RESURRECTION]`), pass `?include_legacy=0`, and assert DOM absence.
3. **Decompose Monolith Zooms & Keep Demo Parity Honest**: Split mixed `Overview` / `.va-scope-chip` Entity / `Item Workspace` hierarchies with an auto-closing `.va-side-rail[data-mode="overlay"]` + `.va-tree-row` drawer and stage archetypes (`.va-stage[data-stage="canvas|workbench|ops"]`), and either recompute presets on `?demo=1` fixtures or set `disabled` + explanatory `title`.
4. **Stage on a Parallel Strangler Route**: Expose the retrofit at `/v2` (or `?ui=quiet`) with `< Classic` / `New ↗` links, namespaced `localStorage` keys, and additive backend query flags so 100% of classic API/UI tests stay green.
5. **Quarantine Unlayered CSS (`layer(legacy)`) & Harden Overlays**: Wrap legacy sheets via `@import url(...) layer(legacy);` above `@layer reset, tokens, shell, archetypes, evidence, views, utilities;` and keep explicit opaque `var(--bg-surface)` on floating overlays.
6. **Guardrail 6 — Day-30 Post-Migration Drift Normalization (`Extract & Normalize`)**: Run `--context .quiet-ui.md --strict-drift` after launch stabilization to sweep `[TOKEN_BYPASS_HEX]` literals and `[INLINE_STYLE_SPRAWL]` hacks into shared `@layer shell` / view classes, retire lingering `layer(legacy)` rules, and flip `Strict Drift: true`.
7. **Guardrail 7 — Mass-Conservation Parity & Zero-Downtime Cutover**: Extract shared enums, cursors, and pluralization to the backend, assert `KPI == Sum(Sankey Col_k) == Sum(Heatmap Cells) == List total_matching` under live interactive toggles in headless CDP, adopt `QuietSankeyLayout` + bounded `QuietPeriodStepper` (`minDate`/`maxDate`, `Cal-to-Date` vs `Rolling`), and execute `/` -> `302 /v2` -> `/v1` Settings fallback -> legacy route retirement.

---

## 8. Hard Anti-Patterns & Quality Corridors

To guarantee visual calm, metrological integrity, and accessibility, every Quiet UI artifact must avoid the following operational traps:

1. **Ungrounded Bezier Splines**: Never draw smooth curves through discrete measurements. If data points are discrete, render discrete markers; if a continuous curve is shown, it must represent a calculated analytical model or calibration fit.
2. **Missing Unit Calculus**: Never display a bare number without physical units. Compound parameters must use unambiguous SI notation (`ps/km`, `nW/cm²`, `rad/s`).
3. **Table Truncation on Desktop ($\ge 1280\,\text{px}$)**: Tables must never produce horizontal scrollbars on desktop viewports. Wrap cells intelligently or split multi-attribute tables into linked panels.
4. **Saturated Cockpit Alarms**: Amber and crimson tokens (`--status-warn`, `--status-err`) must never be used for passive branding, section headers, or decorative badges. They are strictly reserved for active out-of-spec excursions.
5. **Freehand SVG Guessing**: Never ask an LLM to guess SVG coordinate numbers freehand. Author structured JSON specifications against `urn:quiet-ui:schema:v9:*` and compile through deterministic Python/JS builders.
6. **4-Variant Pill Grammar & Baseline Alignment Lock**: Never use unstyled bordered capsules or `[ BRACKETED ]` prose for status, metadata, or chart annotations. Route every badge/tag/label through the 4 strict Quiet UI variants:

| Variant | Class / API | Visual Shape & Chrome | Permitted Domain |
| :--- | :--- | :--- | :--- |
| **1. `status`** | `.va-pill[data-variant="status"]` | `18px` fixed box (`--radius-xs: 2px`). `nominal` is borderless (`transparent`, `6px` dot via CSS `::before`, Title Case `Nominal`). Excursions (`warn`/`fault`) use `10–12%` `in oklab` tint + `2.5px` start bar + `▲`/`◆`. | Live operational state (`Nominal`, `ADVISORY`, `CAUTION`, `TRIPWIRE`, `STALE DATA`, `SENSOR FAULT`). Keep `Margin +X.X%` outside the pill. |
| **2. `tag`** | `.va-pill[data-variant="tag"]` | `18px` monochrome keycap (`--radius-xs: 2px`, `--bg-elevated`, `1px solid var(--border-subtle)`). | Hardware/protocol metadata (`W1C`, `RW`, `INTERLOCK`, `Live: 0x...`, modality/rigor badges). Plain counts & `RO` render unboxed. |
| **3. `chip`** | `<button class="va-pill" data-variant="chip">` | `22px` stadium capsule (`--radius-pill: 999px`). **Round = Clickable**. | Interactive filter chips, modal triggers, clickable pedagogical equation terms (`<button>`, `<a>`, `[role="button"]`). |
| **4. `svg-knockout`** | `svg_knockout_label()` / right-gutter | Borderless canvas/enclave-matched SVG `<rect stroke="none">` + `<text>` or right-gutter `text-anchor="start"`. | Chart envelopes, diagonal slope text (`atan2`), schematic wire labels, shared waveform `DROPOUT` banners. |

   Side-by-side scalar cards MUST lock `.qe-scalar-top` (`min-block-size: 1.375rem`), title height, `.qe-scalar-val-wrap`, and `<svg class="qe-gauge-svg">` baselines within `<= 1.0px`.
7. **Rate-Epoch Comparisons, Cyclical Anti-Sum & Zero-Leak Showcases (`SHA-256[:12]`)**: Never borrow targets across pools, fabricate metrics, render `.va-kpi-gauge-track` on unbounded totals (`[FAKE_UNBOUNDED_GAUGE]`), omit `Warming up — N samples collected` when `N < 10`, compare spend across quota/tariff changes without `effective_from` rate epochs, sum cyclical hour/weekday/month patterns instead of active-day `Min–Avg–Max + Recent` whiskers (`QuietEChartsDefaults.buildCyclicalWhiskerOption`), or ship hardcoded mock JS/JSON fixtures (`[JSON_MOCK_FIXTURE]`). Sanitize public showcase snapshots via deterministic **`SHA-256[:12]`** slug aliasing and a `0`-match grep gate (`Recorded Snapshot — YYYY-MM-DD (Sanitized)`).
8. **Chrome Self-Badges, Plain Copy & Zero Emojis (`[EMOJI_IN_CHROME]`, `[JARGON_TERMINOLOGY]`)**: Never stamp `v9.x Quiet` / `Quiet UI` badges into external application chrome (`header`, `footer`, `nav`, `[role="banner"]`, `.topbar`), expose `brain:<uuid>` storage paths, use obscure jargon headings (`"Activity by Hour of Day"` over `"diurnal"`), or place Unicode pictographic emojis inside interactive buttons/tabs/toolbars—use inline `currentColor` `<svg>` icons instead.
9. **Time Binning, Wide-Script/CJK Gutters, Top Margin & Heatmap Contrast**: Bin dense time series deterministically (`QuietEChartsDefaults.binTimeSeries` -> `1h` `<= 3d`, `1d` `4–92d`, ISO `1w` `> 92d`; `[BAR_HAIRLINE_DENSITY]`), size category gutters and SVG knockout labels using East-Asian wide (`1.75x`) & zero-width combining-mark math (`visual_char_units` / `QuietSvgLayout.visualUnits` + CJK grapheme wrap, `measureCategoryGutter` with `mono` + `axisLabelMargin`; `grid.top >= 30, nameGap >= 12`; `[AXIS_LABEL_CLIPPED]` `+0.5px` top edge), align spines (`computeGridFrameGutters`, `alignPlotGridFrames`, `alignSharedAxes` engaging `independentXSpan` + distinct `yUnit`; `[PLOT_AXIS_MISALIGN]`), trim trailing future week columns (`trimTrailingFutureWeeks`) with `>= 0.06` past zero-cell contrast, use `.va-inline-bar` for `N <= 8`, and keep `[Chart + Table]` 1-column full-width while reserving 2-up `.va-plot-row` for chart-only cards.
10. **Single-Row `.va-rail-footer`, `>= 60%` Split Reader & `< 760px` `<dialog closedby="any">`**: Anchor the left-of-brand drawer trigger in `.va-shell-topbar`; consolidate `.va-rail-footer` into a horizontal `40px` `space-between` row pairing `.va-swatch-row`/`.va-swatch-btn` left with a **2-stop density toggle (`Compact | Comfortable`)** right—banning stacked footer rows, `3+` density stops, `Lock`, `< Classic`, or version pills (`[DENSITY_STOP_SPRAWL]`, `[RAIL_FOOTER_CLUTTER]`). Render rail navigation flat and borderless without `.va-card` boxes (`36px` `.va-tree-row`, `<= 1` `.va-tree-action`, `<= 5` visible children ahead of `.va-tree-more`; `[TREE_NESTED_CARD_BORDERS]`). Use `.va-split-reader-gallery` (`60–64%` prose `>= 760px`, `[PROSE_PANE_CRAMPED]` `< 55%`) + `< 760px` `<dialog class="va-modal-sheet" closedby="any">` (with global key shortcuts disabled while `dialog[open]`), `.va-period-stepper`/`.va-preset-popover` (`[TOOLBAR_CONTROL_SPRAWL]`), and `<= 88px` (`< 680px`) / `<= 64px` (`>= 680px`) sticky budgets (`[STICKY_CHROME_BLOAT]`).
11. **Canonical `@layer` Order, Overlay Opacity & `.hidden`**: Declare `@layer legacy, reset, tokens, shell, archetypes, evidence, views, utilities;` (with `legacy` optional for brownfield imports), enforce opaque `var(--bg-surface)` in terminal utility priority on overlays (`[TRANSPARENT_OVERLAY] < 0.92` alpha rejected), and keep `.hidden, [hidden]:not([hidden="until-found"]) { display: none; }` last (`[HIDDEN_LAYER]`).
12. **Page-Wide Coherence, Pill Restraint (`[PILL_SPRAWL]`), Hairline Panes & `ResizeObserver`**: Limit pages to `<= 3` repeating card structures, `<= 1` chart/half-width card, unified `.booktabs` rows, one `--chart-1..5` ramp, plain `.va-meta-inline` metadata, `.va-workbench-panes`/`.va-pane`/`.va-pane-hdr` (`40px`), and `observeChartResize(hostEl, chart)` + `min-width: 0; max-width: 100%;`.
13. **Accessible Forms, 4-Way Zero-States & 3-Tier Reversibility**: Pair every input/select/textarea with a persistent label (`[UNLABELED_FORM_CONTROL]`), trigger `:user-invalid` / `.va-field-error` on `blur`/`submit` and clear immediately on `input`, explain disabled actions with `.va-gate-reason`, give every `filtered` zero-result view a 1-click `Clear filters` button (`[DEAD_END_ZERO_STATE]`), retain cached telemetry inside `.va-stale-retained` (`opacity: 0.84`), and route soft actions through `>= 7s` pause-on-hover/focus `.va-undo-toast` rather than heavyweight confirmation dialogs.

---

## 9. Interface Lifecycle Transition & Verification Gates

```
Artifact Inception ──► [Gate 0: .quiet-ui.md & Parity] ──► [Gate 1: Schema Spec] ──► [Gate 2: Visual Review] ──► Delivery
```

| Lifecycle Phase | Active Pillar | Artifact Produced | Verification Gate Rule |
| :--- | :--- | :--- | :--- |
| **0. Intake & Scoping** | `quiet-bridge` + `quiet-ui` | `.quiet-ui.md` + Parity Ledger | `Project Mode`, `KEEP`/`CONSOLIDATE`/`DEPRECATE`, `Deprecation Blocklist`, `effective_from` epochs, `N < 10` warmup |
| **1. Shell & Medium** | `quiet-ui` | `@layer` HTML Skeleton | Single-row `.va-rail-footer`, 2-stop density, flat `.va-tree-children` (`<= 5`), labeled forms & 4-way zero-states |
| **2. Evidence Modeling**| `quiet-evidence` | Structured JSON Spec | Cyclical Whiskers (`buildCyclicalWhiskerOption`), `binTimeSeries`, on-card legend (`[ORPHAN_SERIES_LEGEND]`), `SHA-256[:12]` snapshot |
| **3. Compilation** | `quiet-evidence` | Calibrated SVG / ECharts Figures | `1–2–5` ticks, CJK-safe `measureCategoryGutter`, `grid.top >= 30`, `+0.5px` `[AXIS_LABEL_CLIPPED]`, zero `"diurnal"` jargon |
| **4. Dual-Layer Audit** | `quiet-bridge` | Review-Room / Extract & Normalize | BLUF aligned with physics proof; `--strict-drift` zero `[TOKEN_BYPASS_HEX]` / `[INLINE_STYLE_SPRAWL]`; `[BLOCKLIST_RESURRECTION]` clear |
| **5. Pre-Flight Signoff**| `audit_quiet_html.py` + `tests/` | Unified Stdlib + CDP Gates | `390/820/1440/1920px` (`[CHROME_HEIGHT_BUDGET]`, `[WORKBENCH_STAGE_TUNNEL]`, `[DUPLICATE_PRIMARY_NAV]`, `[VISIBLE_HITBOX_OUTLINE]`, `[TREE_INDENT_INVERSION]`, `[RAW_SLUG_OR_GRAMMAR_LEAK]`, `--check`) |

Run the full verification loop before shipping:

```bash
python3 -B scripts/build_all.py --check
QUIET_SKIP_CDP=1 python3 -B -m unittest discover -s tests -v
QUIET_REQUIRE_CDP=1 python3 -B -m unittest discover -s tests -v
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py quiet-ui-showcase.html --cdp --allow-showcase-chrome
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py path/to/app/web --context path/to/app/.quiet-ui.md --strict-drift
```

---

## 10. Studio Portal Navigation & Stage Interaction Contract (`v9.6.0`)

1. **Unified `<optgroup>` Domain + View Picker (`#va-view-select`)**: The Studio topbar consolidates domain and example selection inside a single `<optgroup>` selector paired with seamless cross-domain `<` and `>` stepping (`1 / 22`..`22 / 22`), resetting per-view curated form-factor and theme presets on every view switch (`<`, `>`, or picker change).
2. **Viewport-Pinned Sticky Rail & Stage-Only Scroll (`N1` / `N3`)**: On desktop (`>= 1100px`), `.va-shell-rail` is clamped to `calc(100dvh - var(--va-topbar-sticky-h, 0px))` with an internal `.va-rail-scroll` list and pinned `.va-rail-footer`. Anchor clicks use explicit stage `window.scrollTo` offset math (`spotlightAnchor`) instead of `scrollIntoView` so neither `.va-shell-topbar` nor `.va-shell-rail` ever shifts off-screen.
3. **Device Frame Presets & Full-Bleed Appliances (`Tablet` / `v08` / `v15`–`v17`)**: Portal framing supports `1080p`, `Tablet` (`1280×800` anodized bezel for `v08` interactive Plant Test & HMI Display), `Paper`, `Mobile`, and `Fill`. Optical HUD (`v15`), maritime smart-glass visor with default-on peripheral AR channel markers (`v16`), and museum-matted living-room art frame (`v17`) bleed `100%` edge-to-edge without outer white stage margins.
4. **Overview Standards Ledger (`#va-landing-standards`)**: The Studio `Overview` landing documents the 4 foundational authorities (`NIST SP 811` / `ISO 80000`, `ISA-101` / `NUREG-0700`, `FDA IEC 62366` / `NASA-STD-3001`, and `SAE J1939` / `ITU-T Z.120` / `NIST AI RMF 100-1`).

---

## 11. Workflow E — Multi-Format Research & Civic Storytelling (`v9.6.0`)

When transforming public datasets, policy briefs, or survey waves into reader-facing articles, slide briefings, and printed PDFs (`v22-reading-and-mobility-brief` and Specimens `45–49`):
1. **Question-First Lead, Unboxed Callouts & Hex Scope Sync**: Open sections with an everyday reader question, a left-margin `.va-freshness-stamp`, an interactive scope switcher (`US National | Maryland | Wyoming`) atomically driving `.va-lead-highlight`, 3 unboxed `.va-editorial-callouts` numbers, and `.va-hex-tile.is-selected` (zero state outline on national scope; exact state outline + top SVG paint order on `Maryland` / `Wyoming`).
2. **Takeaway Figure Cards, Unchanged Dumbbell Spacing & Data Portability**: Render plots (`us_hex_tile_map` with WCAG luminance-adaptive ink, `arrow_dumbbell` with stationary dual-ring + `(unchanged)` markers when `start == end` plus `>= 12px` text clearance and single `*` fallback notes, `paired_subgroup_bars`, `dual_slopegraph` with unit-once top rows and dynamic step-leader gutters, and `diverging_matrix` keeping `$ Level` columns unshaded alongside diverging `% Change` tints and `20.0%` baseline notes) inside 4-part Takeaway Figure Cards with `[Chart | Table]` (`hidden="until-found"`), TSV `Copy data`, and Markdown `Copy for AI` (`role="status"`).
3. **Sticky-Header Scroll Clearance, Multi-Format Sync & Editorial/Print CDP Gates**: Declare `scroll-padding-top: 5.5rem` on `.qe-topbar` pages and `scroll-margin-top: 5.5rem` on `.qe-specimen`, `.va-figure-card`, `.qe-figure`, and `section[id]` anchors so jumps never collide beneath sticky chrome; project one conserved ledger across Web Brief, `16:9` `.va-slide-frame` Deck, and `@media print` enforcing zero `[PRINT_FLOW_COLLISION]`, `[PROSE_COLUMN_STARVATION]`, `[NESTED_PROSE_SCROLL]`, `[CODE_LUMINANCE_SHOCK]`, `[DIAGONAL_TICK_OR_ROTATED_Y_TITLE]`, and `[END_LABEL_CLIP]`.
