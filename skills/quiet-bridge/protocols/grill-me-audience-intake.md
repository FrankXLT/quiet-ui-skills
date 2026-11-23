# Translation Protocol: "Grill Me" Audience Intake

This protocol establishes the mandatory pre-build interrogation sequence executed before designing, drafting, or coding any technical interface, dashboard, document, or data presentation under Quiet UI Pillar 3.

---

## 1. Purpose & The Anti-Assumptive Mandate

Engineers and designers habitually commit the **Projection Fallacy**: they assume that what matters to them (internal architectural beauty, micro-optimizations, raw terminal output) is what the audience requires to make a decision.

The "Grill Me" Audience Intake protocol eliminates this failure mode through a structured, mandatory 5-question interrogation anchored to the **4 Universal Audience Evaluation Invariants** ((1) **Baseline & Corridor**, (2) **Epistemic Provenance**, (3) **Margin & Consequence**, (4) **Actionable Disposition**). **Before asking intake questions on an existing workspace, always inspect the target root (or parent workspace) for `.quiet-ui.md`**—honor locked values (`Project Mode`, `Primary Medium`, `Chromatic Budget`, `Navigation Shell`, `Capability Parity Ledger`, `Deprecation Blocklist`) rather than re-interrogating settled decisions, and persist newly agreed answers back into `.quiet-ui.md` (`--init-context`) before building.

```
[TARGET REPO .quiet-ui.md FOUND?] --(yes)--> [LOAD & VERIFY LOCKED CONTRACT]
             | (no)
             v
[GRILL-ME AUDIENCE INTAKE (5 QUESTIONS + 4 INVARIANTS)]
- Question 1: Who is the Primary Decision Authority?
- Question 2: What is the Operational Decision Tempo?
- Question 3: What is the Native Unit of Proof (+ Baseline & Margin)?
- Question 4: What is the Physical Delivery Medium?
- Question 5: What is the Hard Abort / Rejection Redline?
             |
             v
[FROZEN INTAKE CONTRACT -> PERSIST .quiet-ui.md]
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
  - *Discipline Specialist* (RF, Thermal, Clinical Biostatistician `CONSORT`, SRE/AI Eval `OpenTelemetry` / `NIST AI RMF 100-1`, SPC Lead `NIST/SEMATECH SPC`, Treasury Analyst `FRED/SEC`).
  - *Project Systems Engineer / Technical Assessor* (PSE, `FDA IEC 62366` Human-Factors Lead, `NIST SP 800-207` Zero-Trust / ATO Assessor, `ISA-101` / `NRC NUREG-0700` Controls Architect, `GAO` Audit Lead).
  - *Program Manager / Resource Allocator* (PM, IPT Lead, Clinical Trial Director, Platform Reliability Director, Civic Capital Board Chair).
  - *Field Technician / Operator* (Flight controller, ICU bedside clinician, on-call SRE, SCADA `Modbus` plant operator, treasury settlement operator).
  - *Educator & Mentor* (Course instructor, clinical preceptor, apprentice mentor).
  - *Student & Learner* (STEM student, nursing/clinical trainee, SRE apprentice, civic data intern).
  - *Common Reader / Enterprise User* (Patient/caregiver, public oversight inspector, cloud subscriber, municipal resident).

### Question 2: Operational Decision Tempo
- **Query**: "Under what operational time constraint will this decision be made?"
- **Options**:
  - *Tactical Seconds (5–15 s)*: Live anomaly triage, ICU bedside pump alarm, SRE production incident containment, SCADA/nuclear control tripwire.
  - *Executive Minutes (1–3 min)*: Milestone gate GO/NO-GO, clinical DSMB hold/continue, SLO release freeze, municipal bond reserve release.
  - *Analytical Deep Dive (10–45 min)*: Peer review, CDR/PDR, `CONSORT` trial audit, `OpenTelemetry` postmortem, `SPC C_pk` capability study, `GAO` fiscal review.

### Question 3: Native Unit of Proof (Baseline, Provenance & Margin)
- **Query**: "What exact numerical or physical evidence compels this authority to say YES, and how does it satisfy the 4 Universal Invariants?"
- **Guidance**: Must be expressed in explicit units with baseline corridor and margin:
  - Discipline: Picosecond slack, $\text{dBm}$ margin, $\pm 3\sigma$ bounds, `CONSORT` 95% CI, `OpenTelemetry` p99 ms, `NIST/SEMATECH SPC` $C_{pk}$, `FRED/SEC` real DSCR.
  - Systems: ICD pin/API/Modbus register matrix, `NIST SP 800-207` PEP & PPSM rules, `FDA IEC 62366` use-error guardrails, `GAO` ledger hash chain.
  - Programmatic: Schedule float $\Delta \text{days}$, risk exposure $\$$, CPI/SPI, error-budget burn $\%$, yield/scrap $\$$, obligated vs. reserve ratio.
  - Operator: Pin/tag (`J3-14`, `Modbus 40012`, `Pump Ch-2`, OTel span ID), discrete corridor, guarded interlock state.
  - Educator: Cognitive Speed Limit compliance, one-variable sweep pacing, term-to-visual color binding.
  - Student: Hypothesis verification, controlled variables table, apparatus/study schematic, discrete error bars.
  - Consumer: Plain-English impact, hours of runtime or reserve coverage, direct action steps.

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

### Template E: Clinical Safety & Trial DSMB (`FDA IEC 62366`, `CONSORT`)
```yaml
intake_profile: clinical_safety_and_trial
primary_authority: ICU Attending / DSMB Safety Chair
secondary_auditor: Clinical Biostatistician & Human-Factors Lead
decision_tempo: tactical_seconds (10 s bedside) / executive_minutes (2 min DSMB)
native_unit_of_proof: "CONSORT cohort N with 95% CI; IEC 62366 dose-rate corridor (mL/hr)"
delivery_medium: M4_walkup_poi_terminal / M2_editorial_web
hard_abort_redlines:
  - "Bare p-value without cohort sample size N or 95% confidence interval"
  - "High-alert infusion rate override lacking dual-clinician confirmation"
```

### Template F: SRE / Cloud / AI Ops (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`)
```yaml
intake_profile: sre_ai_zero_trust_ops
primary_authority: SRE Incident Commander / CISO
secondary_auditor: Principal Reliability & AI Eval Lead
decision_tempo: tactical_seconds (15 s triage) / analytical_deep_dive (30 min postmortem)
native_unit_of_proof: "OpenTelemetry p99 latency (ms), SLO error-budget burn (%), ECE drift"
delivery_medium: M3_stateful_web_app (trace + policy workbench)
hard_abort_redlines:
  - "Mean latency reported in place of p95/p99 tail percentile with span count"
  - "AI confidence score shown without NIST AI RMF 100-1 fallback threshold"
```

### Template G: Industrial Plant Quality & SCADA (`NIST/SEMATECH SPC C_pk`, `ISA-101`, `NRC NUREG-0700`, `Modbus`)
```yaml
intake_profile: industrial_scada_spc
primary_authority: Control Room Lead Operator / Plant Quality Director
secondary_auditor: ICS Controls & Metrology Engineer
decision_tempo: tactical_seconds (10 s console) / analytical_deep_dive (25 min SPC audit)
native_unit_of_proof: "Modbus register value vs ISA-101 redline; SPC C_pk with UCL/CL/LCL"
delivery_medium: M5_ambient_wall / M3_stateful_web_app
hard_abort_redlines:
  - "Actuator command enabled while upstream LOTO or Modbus interlock is unconfirmed"
  - "High-chroma animated background violating ISA-101 / NRC NUREG-0700 dull-screen norm"
```

### Template H: Civic Capital & Treasury Board (`GAO`, `FRED/SEC`)
```yaml
intake_profile: civic_capital_treasury
primary_authority: Municipal CFO / Capital Appropriations Chair
secondary_auditor: GAO / External Bond Auditor
decision_tempo: executive_minutes (3 min board vote)
native_unit_of_proof: "Real DSCR (FRED CPI-U deflated), unobligated reserve days, SEC 10-Q"
delivery_medium: M2_editorial_web / M1_archival_print
hard_abort_redlines:
  - "Nominal multi-year projections lacking FRED inflation deflator or stressed DSCR"
  - "Disbursement ledger missing GAO Green Book SHA-256 reconciliation trail"
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

Before releasing any interface specification or beginning layout implementation, verify compliance against this seven-point audit:

1. **Intake Contract Frozen**: Has the 5-question intake contract been formally completed and documented?
2. **4 Universal Audience Evaluation Invariants Bound**: Does the contract explicitly lock (1) Baseline & Corridor, (2) Epistemic Provenance, (3) Margin & Consequence, and (4) Actionable Disposition?
3. **Explicit Decision Authority**: Is the interface tuned to the exact cognitive model and native unit of proof of the designated primary authority?
4. **Calibrated Tempo Alignment**: Does the information density strictly conform to the declared decision tempo (Seconds, Minutes, Deep Dive)?
5. **Medium-Specific Physics Enforced**: Are the layout, fonts, and contrast ratios mapped directly to the selected Quiet UI medium (`M1` through `M7`)?
6. **Redlines Pre-Emptively Scrubbed**: Have all identified receiver dealbreakers and presenter biases been scrubbed from the proposed presentation?
7. **Pedagogical Pacing Enforced**: If the delivery targets students or apprentices, is the Cognitive Speed Limit verified with zero multi-variable jumps and $\ge 90\%$ neutral ink ratio?

---

## 6. Cross-Reference Links

- For audience persona lenses, see [../lenses/discipline-engineer.md](../lenses/discipline-engineer.md), [../lenses/project-systems-engineer.md](../lenses/project-systems-engineer.md), [../lenses/program-manager.md](../lenses/program-manager.md), [../lenses/educator-and-mentor.md](../lenses/educator-and-mentor.md), and [../lenses/student-and-learner.md](../lenses/student-and-learner.md).
- For operational tempos, see [../tempos/tactical-seconds.md](../tempos/tactical-seconds.md), [../tempos/executive-minutes.md](../tempos/executive-minutes.md), and [../tempos/analytical-deep-dive.md](../tempos/analytical-deep-dive.md).
- For adversarial red-team testing of intake contracts, see [adversarial-murder-board.md](adversarial-murder-board.md).
- For review-room dual-layer layout implementations, see [review-room-dual-layer.md](review-room-dual-layer.md).
