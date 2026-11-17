# Translation Protocol: "Grill Me" Audience Intake

This protocol establishes the mandatory pre-build interrogation sequence executed before designing, drafting, or coding any technical interface, dashboard, document, or data presentation under Quiet UI Pillar 3.

---

## 1. Purpose & The Anti-Assumptive Mandate

Engineers and designers habitually commit the **Projection Fallacy**: they assume that what matters to them (internal architectural beauty, micro-optimizations, raw terminal output) is what the audience requires to make a decision.

The "Grill Me" Audience Intake protocol eliminates this failure mode through a structured, mandatory 5-question interrogation. Before generating any HTML, CSS, SVG, or documentation artifact, the author must explicitly execute this intake and freeze the resulting contract.

```
[USER / STAKEHOLDER REQUEST]
             |
             v
[GRILL-ME AUDIENCE INTAKE (5 QUESTIONS)]
- Question 1: Who is the Primary Decision Authority?
- Question 2: What is the Operational Decision Tempo?
- Question 3: What is the Native Unit of Proof?
- Question 4: What is the Physical Delivery Medium?
- Question 5: What is the Hard Abort / Rejection Redline?
             |
             v
[FROZEN INTAKE OUTPUT CONTRACT]
             |
             v
[ARCHITECTURE & CODE IMPLEMENTATION]
```

---

## 2. The 5 Core Interrogation Questions

When initiating an artifact build, the system asks the user or project lead the following five calibrated questions:

### Question 1: Primary Decision Authority & Secondary Stakeholder
- **Query**: "Who is the specific individual or role authorized to make a binding decision based on this interface? Who is the secondary reader who will review or audit the underlying data?"
- **Options**:
  - *Discipline Specialist* (RF, Thermal, Structural, Optical, DSP).
  - *Project Systems Engineer / Technical Assessor* (PSE, LSE, ATO Assessor).
  - *Program Manager / Resource Allocator* (PM, IPT Lead, Acquisition Director).
  - *Field Technician / Operator* (Flight controller, test stand tech, plant mechanic).
  - *Educator & Mentor* (Course instructor, laboratory director, apprentice mentor).
  - *Student & Learner* (First-time learner, university student, engineering intern).
  - *Common Reader / Enterprise User* (Public auditor, executive sponsor, non-specialist customer).

### Question 2: Operational Decision Tempo
- **Query**: "Under what operational time constraint will this decision be made?"
- **Options**:
  - *Tactical Seconds (5–15 s)*: Live anomaly triage, active flight control, emergency shutdown.
  - *Executive Minutes (1–3 min)*: Milestone gate GO/NO-GO, budget authorization, risk acceptance.
  - *Analytical Deep Dive (10–45 min)*: Peer review, CDR/PDR, laboratory instruction, failure review board.

### Question 3: Native Unit of Proof
- **Query**: "What exact numerical or physical evidence compels this authority to say YES?"
- **Guidance**: Must be expressed in explicit units:
  - Discipline: Picosecond timing slack, $\text{dBm}$ receiver sensitivity, $\pm 3\sigma$ residual bounds.
  - Systems: ICD pin assignments, PPSM port filter rules, bus utilization $\%$.
  - Programmatic: Schedule critical path $\Delta \text{days}$, cost risk exposure $\$$, CPI/SPI.
  - Operator: Connector pin designators (`J3-14`), relay continuity, breaker state.
  - Educator: Cognitive Speed Limit compliance, one-variable sweep pacing, term-to-visual color binding.
  - Student: Hypothesis verification, controlled variables table, apparatus schematic, discrete error bars.
  - Consumer: Plain English impact, hours of runtime remaining, direct action steps.

### Question 4: Delivery Medium & Physical Constraints
- **Query**: "On what physical surface and in what environmental setting will this interface be viewed?"
- **Mapping to Quiet UI Pillar 1**:
  - `M1`: Paper & Archival Print (`@page`, monochrome/high-contrast ink).
  - `M2`: Editorial Web Monograph (72ch prose column, deep figures).
  - `M3`: Stateful Web Application / Workbench (bento grid, interactive controls).
  - `M4`: Walk-up POI Touch Terminal (high contrast, guarded touch targets).
  - `M5`: 10-Foot Ambient Wall Display (stand-off glanceability, high optical scale).
  - `M6`: Collimated Optical HUD (monochrome green/cyan, $\ge 65\%$ keep-out).
  - `M7`: Transparent Window Overlay (high-contrast text halos, glare rejection).

### Question 5: Hard Abort / Rejection Redline
- **Query**: "What specific parameter value, missing metadata, or formatting flaw causes this reviewer to immediately REJECT or ABORT the artifact?"
- **Guidance**: Identify the receiver dealbreakers (e.g., missing pin numbers, unstated sigma bounds, smooth curves without raw data glyphs, negative schedule float).

---

## 3. Concrete Intake Templates by Domain

The intake protocol adapts its defaults based on the target operational domain:

### Template A: Discipline Engineering / Laboratory Test
```yaml
intake_profile: discipline_metrology
primary_authority: Lead RF Payload Specialist
secondary_auditor: Project Systems Engineer
decision_tempo: analytical_deep_dive (30 minutes)
native_unit_of_proof: Log-decade Allan deviation sigma_y(tau) with +/- 1 sigma error bars
delivery_medium: M3_stateful_web_app (dual-pane metrology workbench)
hard_abort_redlines:
  - "Absence of raw discrete scatter points behind fitted polynomial regression"
  - "Unstated sensor calibration certificate ID or expired cal date"
  - "Spline smoothing drawn across unmonitored frequency gaps"
```

### Template B: Executive Milestone Review Board
```yaml
intake_profile: executive_gate_review
primary_authority: Program Executive / Flight Readiness Director
secondary_auditor: Chief Financial Officer
decision_tempo: executive_minutes (2 minutes)
native_unit_of_proof: Critical path float in days paired with link margin in dB
delivery_medium: M2_editorial_web (single-screen briefing view with expandable L3 drawer)
hard_abort_redlines:
  - "Missing critical path float variance in working days"
  - "Unitless health scores or ungrounded color pills"
  - "Single-option problem presentation without cost/schedule trade alternatives"
```

### Template C: Field Flight-Line Operations
```yaml
intake_profile: field_operations_runbook
primary_authority: Flight-Line Avionics Master Technician
secondary_auditor: Quality Assurance Inspector
decision_tempo: tactical_seconds (10 seconds)
native_unit_of_proof: Pin continuity on J2-Pin 4 and voltage at TP-01 [26.0 - 30.0 VDC]
delivery_medium: M4_walkup_poi_terminal (ruggedized touch tablet, high ambient sunlight)
hard_abort_redlines:
  - "Ambiguous yellow advisory status without explicit tolerance band"
  - "Destructive or high-voltage command without two-step guarded confirmation latch"
  - "Action step missing reference to authorizing SOP step number"
```

### Template D: Pedagogical Lecture & Student Lab
```yaml
intake_profile: pedagogical_concept_delivery
primary_authority: Master Educator / Course Instructor
secondary_auditor: Student / Apprentice Learner
decision_tempo: analytical_deep_dive (20 minutes)
native_unit_of_proof: One-variable parameter sweep with equation-to-curve color term binding
delivery_medium: M2_editorial_web (monograph with synchronized stepped figures)
pedagogical_constraints:
  cognitive_speed_limit: "Maximum 1 new physical concept per viewport / step"
  neutral_surface_ration: ">= 90% neutral ink; color strictly reserved for active variable"
  pacing_enforcement: "Step-by-step progressive disclosure; no premature equation unrolling"
hard_abort_redlines:
  - "Simultaneous variation of two independent variables without intermediate baseline"
  - "Unbound mathematical symbol lacking color-matched diagram label"
  - "Dense multiline equation lacking physical parameter annotations"
```

---

## 4. Frozen Intake Output Contract Schema

Once the intake interrogation is complete, the resulting specification must be serialized and frozen at the head of the project brief or design artifact:

```json
{
  "intake_protocol_version": "1.0.0",
  "contract_hash": "b4e89f21c10948a7e0984128f731aa881029c3f9104b99824c62b53e81039da5",
  "freeze_timestamp_utc": "2026-11-16T19:50:00Z",
  "stakeholder_alignment": {
    "primary_decision_role": "PROJECT_SYSTEMS_ENGINEER",
    "secondary_audit_role": "ATO_SECURITY_ASSESSOR",
    "operational_tempo": "EXECUTIVE_MINUTES",
    "time_budget_seconds": 120
  },
  "evidentiary_contract": {
    "native_unit_of_proof": "ICD Boundary Pin/Protocol Matrix & Timing Slack in ns",
    "required_si_units": ["ns", "ps", "VDC", "Mbps"],
    "minimum_margin_threshold": "+20.0% timing slack"
  },
  "physical_medium": {
    "medium_code": "M3",
    "screen_resolution": "1920x1080",
    "color_purpose_budget": "Decision Contrast",
    "nav_shell": "N2_top_bar"
  },
  "rejection_triggers": [
    "Unallocated timing jitter exceeding 100 ps",
    "Missing PPSM port security filtering rule",
    "Undefined pin electrical standard (e.g. RS-422 vs LVDS)"
  ]
}
```

---

## 5. Intake Verification Rubric

Before releasing any interface specification or beginning layout implementation, verify compliance against this five-point audit:

1. **Intake Contract Frozen**: Has the 5-question intake contract been formally completed and documented?
2. **Explicit Decision Authority**: Is the interface tuned to the exact cognitive model and native unit of proof of the designated primary authority?
3. **Calibrated Tempo Alignment**: Does the information density strictly conform to the declared decision tempo (Seconds, Minutes, Deep Dive)?
4. **Medium-Specific Physics Enforced**: Are the layout, fonts, and contrast ratios mapped directly to the selected Quiet UI medium (`M1` through `M7`)?
5. **Redlines Pre-Emptively Scrubbed**: Have all identified receiver dealbreakers and presenter biases been scrubbed from the proposed presentation?
6. **Pedagogical Pacing Enforced**: If the delivery targets students or apprentices, is the Cognitive Speed Limit verified with zero multi-variable jumps and $\ge 90\%$ neutral ink ratio?

---

## 6. Cross-Reference Links

- For audience persona lenses, see [../lenses/discipline-engineer.md](../lenses/discipline-engineer.md), [../lenses/project-systems-engineer.md](../lenses/project-systems-engineer.md), [../lenses/program-manager.md](../lenses/program-manager.md), [../lenses/educator-and-mentor.md](../lenses/educator-and-mentor.md), and [../lenses/student-and-learner.md](../lenses/student-and-learner.md).
- For operational tempos, see [../tempos/tactical-seconds.md](../tempos/tactical-seconds.md), [../tempos/executive-minutes.md](../tempos/executive-minutes.md), and [../tempos/analytical-deep-dive.md](../tempos/analytical-deep-dive.md).
- For adversarial red-team testing of intake contracts, see [adversarial-murder-board.md](adversarial-murder-board.md).
- For review-room dual-layer layout implementations, see [review-room-dual-layer.md](review-room-dual-layer.md).
