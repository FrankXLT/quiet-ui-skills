# Quiet UI v9.0 — Master Engineering Workflows & Architecture

> **Document Class**: Authoritative Architecture Specification  
> **Target Version**: Quiet UI v9.0 (`3-Pillar Unified Continuum`)  
> **Standards Basis**: NIST SP 811, FDA IEC 62366, ISA-101 / NRC NUREG-0700, NIST AI RMF 100-1, SAE J1939, NAVAIR FTM-108, NASA-STD-3001, GAO/USWDS

---

## 1. The 3-Pillar Compositional Philosophy

Quiet UI v9.0 abandons rigid monolithic page templates and artificial walls between "diagrams" and "dashboards." Instead, any user-facing interface, monograph, console, or report—across **Clinical Care & Life Sciences, Cloud/Cyber/AI Ops, Industrial Grid & Manufacturing, Automotive & Embedded Hardware, Civic Finance & Risk, and Earth Science & STEM Education**—is decomposed into three strictly orthogonal concerns:

```
                                      QUIET UI v9.0
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
   - Formulates communication as an asymmetric vector across **6 Universal Domain Clusters (18 presenter-to-audience pairs)**: `Presenter Source` &rarr; `Audience Lens` $\times$ `Decision Tempo`.
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

### Step 2. Medium & Chromatic Lock
The agent consults `skills/quiet-ui/` to emit the Pre-Edit Output Contract:
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
- Selects the target rigor level (`L1`, `L2`, or `L3`).
- Emits a clean JSON specification conforming to `urn:quiet-ui:schema:v9:<modality>`.
- Passes the JSON specification to the deterministic compiler for exact SVG coordinate generation.

### Step 4. Adversarial Murder Board Audit
Before declaring the interface complete, the agent runs the Murder Board rubric matching the audience lens. If any redline triggers (e.g., missing units on numbers, ungrounded Bezier splines, amber status during nominal states, or table truncation on desktop), the artifact is blocked.

---

## 3. Workflow B — Multi-Audience Distillation & Numerical Conservation

A frequent failure mode in technical reporting is creating separate, unlinked documents for executives, engineers, and operators, causing numbers to drift. Quiet UI v9.0 enforces the **Numerical Conservation Law**:

> **Numerical Conservation Invariant**: When distilling one primary system or incident into multiple audience views, the underlying physical truth (parameters, sample rates, abort limits, timestamps, and citations) MUST derive from a single canonical JSON dataset. Presentation alters only framing, compression tempo, and coordinate density—never the underlying numbers.

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
  body {
    background: #ffffff !important;
    color: #0f172a !important;
  }
  .va-shell-topbar,
  .va-shell-rail,
  .va-shell-bottomdock,
  #va-studio-bar,
  .va-interactive-cursor {
    display: none !important;
  }
  .va-prose {
    max-inline-size: 100% !important;
  }
  .va-card,
  .va-panel-tonal {
    break-inside: avoid;
    border: 1px solid #cbd5e1;
    background: #ffffff !important;
  }
  .va-table-wrap {
    overflow: visible !important;
  }
  .va-test-condition-block {
    display: table !important;
    inline-size: 100%;
    margin-block-end: 1rem;
    border: 1px solid #94a3b8;
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

## 6. Workflow E — Backward-Compatible Diagram AST & Starter Customization Flows

Quiet UI v9.0 maintains complete backward compatibility for existing diagram AST extractors and starter kits:

### 6.1 Diagram AST Extractors
The existing AST extraction tools in `skills/quiet-ui-diagrams/scripts/`:
- `mermaid_extract.py` (flowcharts, sequence diagrams, state/ER diagrams)
- `plantuml_extract.py` (class diagrams, component diagrams)
- `drawio_extract.py` (compressed XML shapes, connections)
- `excalidraw_extract.py` (handcrafted canvas primitives)

**Routing Strategy**: When an incoming file or prompt contains Mermaid or PlantUML AST code, the `quiet-ui-diagrams/SKILL.md` adapter:
1. Ingests the AST via the appropriate parser.
2. If the diagram represents system architecture or flow, routes to `quiet-evidence` Modality 6 (*Schematics & Topologies*).
3. If the diagram represents numerical series or charts, routes to `quiet-evidence` Modality 4 (*Analytical & Spectral Plots*).
4. Emits compliant SVG bound to the 4-theme token system.

### 6.2 Starter Customization Kits (`personal-starter` & `brand-starter`)
The customization workspaces under `customizations/`:
- `customizations/personal-starter/` (personal portfolio / workspace theme)
- `customizations/brand-starter/` (enterprise brand palette)

**Inheritance Rule**: Starters override token values via `styles/overrides.css` while inheriting the core `@layer` hierarchy and Stage Portal machinery. In v9.0:
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

### 7.2 The Asymmetric Flow: Educator vs. Student

```
[Educator as Presenter] ──► Prerequisite Anchoring ──► Worked Derivations ──► Interactive Probing
                                                                                      │
                                                                                      ▼
[Student as Presenter]  ──► Scientific Hypothesis   ──► Apparatus Diagram  ──► Measured vs Theory
```

- **Educator as Presenter**: Scrubs the "curse of expertise" (unexplained leaps in derivations, ungrounded notation), enforces worked examples before problem sets, and embeds interactive parameter sliders.
- **Student as Presenter (Lab Reports & Capstones)**: Replaces chronological data dumping with formal scientific structure: *Hypothesis* &rarr; *Controlled/Independent/Dependent Variables* &rarr; *Apparatus Schematic* &rarr; *Discrete Runs with $\pm 1\sigma$ Error Bars vs. Theoretical Model* &rarr; *Physical Error Analysis*.

---

## 8. Hard Anti-Patterns & Quality Corridors

To guarantee visual calm, metrological integrity, and accessibility, every Quiet UI artifact must avoid the following operational traps:

1. **Ungrounded Bezier Splines**: Never draw smooth curves through discrete measurements. If data points are discrete, render discrete markers; if a continuous curve is shown, it must represent a calculated analytical model or calibration fit.
2. **Missing Unit Calculus**: Never display a bare number without physical units. Compound parameters must use unambiguous SI notation (`ps/km`, `nW/cm²`, `rad/s`).
3. **Table Truncation on Desktop ($\ge 1280\,\text{px}$)**: Tables must never produce horizontal scrollbars on desktop viewports. Wrap cells intelligently or split multi-attribute tables into linked panels.
4. **Saturated Cockpit Alarms**: Amber and crimson tokens (`--status-warn`, `--status-err`) must never be used for passive branding, section headers, or decorative badges. They are strictly reserved for active out-of-spec excursions.
5. **Freehand SVG Guessing**: Never ask an LLM to guess SVG coordinate numbers freehand. Author structured JSON specifications against `urn:quiet-ui:schema:v9:*` and compile through deterministic Python/JS builders.

---

## 9. Interface Lifecycle Transition & Verification Gates

```
Artifact Inception ──► [Gate 0: Contract Lock] ──► [Gate 1: Schema Spec] ──► [Gate 2: Visual Review] ──► Delivery
```

| Lifecycle Phase | Active Pillar | Artifact Produced | Verification Gate Rule |
| :--- | :--- | :--- | :--- |
| **0. Intake & Scoping** | `quiet-bridge` | Audience Vector Contract | 3-question "Grill Me" response recorded |
| **1. Shell & Medium** | `quiet-ui` | `@layer` HTML Skeleton | Shell `N0–N4` valid, concentric radius satisfied |
| **2. Evidence Modeling**| `quiet-evidence` | Structured JSON Spec | Schema validation passed against offline URN |
| **3. Compilation** | `quiet-evidence` | Calibrated SVG Figures | $1\text{--}2\text{--}5$ ticks verified, halos rendered |
| **4. Dual-Layer Audit** | `quiet-bridge` | Review-Room Composition | BLUF band aligned with physics proof below |
| **5. Pre-Flight Signoff**| Multi-Agent | 21 Selenium CDP Gates | Zero `!important`, zero PII, zero broken links |


