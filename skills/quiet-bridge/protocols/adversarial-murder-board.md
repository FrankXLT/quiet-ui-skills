# Translation Protocol: Adversarial Murder Board

This protocol establishes the adversarial red-team review procedure executed to stress-test technical interfaces, design packages, and milestone briefings before they are submitted to formal external review boards.

---

## 1. Purpose & The Red-Team Mandate

In aerospace, clinical medicine, cloud/AI operations, industrial process control, and public finance, formal milestone reviews (PDR, CDR, FRR, Clinical DSMB, Production Cutover, and Capital Boards) are not collaborative brainstorms; they are adversarial audits where appointed reviewers actively search for ungrounded assumptions, unallocated margins, unmodeled risks, and compliance breaches.

The **Adversarial Murder Board** simulates this audit environment internally. Before examining role-specific redlines, every board enforces the **4 Universal Audience Evaluation Invariants**:
1. **Baseline & Corridor**: Anchor every readout in a calibrated reference band (healthy vitals, `UCL/CL/LCL`, SLO threshold, or policy corridor).
2. **Epistemic Provenance**: Distinguish discrete measurements ($\pm 1\sigma$ / 95% CI) from fitted models and flag stale or uncalibrated feeds.
3. **Margin & Consequence**: Expose headroom (`CMD vs ACT`, $C_{pk}$, error-budget burn, liquidity runway) explicitly without mental math.
4. **Actionable Disposition**: Bind the quantitative state to a single bounded next action, escalation, or guarded control step.

A design team convenes orthogonal red-team personas to systematically challenge the artifact against explicit failure rubrics. If an artifact trips any hard block criterion, it is rejected back to the author before it ever reaches the external board.

```
[PROPOSED DESIGN / PRESENTATION ARTIFACT]
                   |
                   v
[ADVERSARIAL MURDER BOARD RED-TEAM REVIEW]
   +----------------------------+----------------------------+
   | Chief Engineer / SPC Lead  | Program Manager / Civic Bd |
   +----------------------------+----------------------------+
   | ISSM / ATO / SRE Incident  | Field Tech / Clinical Safety|
   +----------------------------+----------------------------+
   | Educator / Learner Scaffold| 4 Universal Invariants     |
   +----------------------------+----------------------------+
                   |
     +-------------+-------------+
     |                           |
     v (Any Hard Block Tripped)  v (All Applicable Rubrics Cleared)
[FORMAL REJECTION NOTICE]   [BOARD PASS CERTIFICATE]
- Remediation Task Assigned   - Authorized for Release
- Re-run Intake Protocol      - Digital Signature Hash
```

---

## 2. Role-Specific Red-Team Rubrics

The Murder Board evaluates the artifact through four orthogonal, adversarial personas:

### 2.1 Chief Engineer Redline Rubric (Physical Conservation & Metrology)
*Focus: First-principles physics, thermodynamic conservation, timing closure, statistical error.*

- **CR-1: Conservation Law Auditing**: Does the thermal dissipation, mass rollup, or power draw sum to 100% of the physical budget without negative reserves or unallocated residuals?
- **CR-2: Discrete Scatter vs. Spline Smoothing**: Are continuous curves drawn through sparse empirical data points? If splines exist without discrete scatter markers and error bars, **FLAG AS FRAUDULENT FIT**.
- **CR-3: Environmental Envelope Stressing**: Are parameters stated across worst-case operating temperatures ($-40^\circ\text{C}\text{ to }+85^\circ\text{C}$), vacuum pressures, and voltage rail transients?
- **CR-4: Timing & Metastability Margin**: Is clock jitter, setup/hold slack, and FIFO depth margin rigorously calculated against worst-case propagation delays?
- **CR-5: Calibration Traceability**: Does every displayed measurement cite a valid NIST/ISO calibration standard ID and expiration timestamp?

### 2.2 Program Manager Redline Rubric (Schedule Float & Resource Reserve)
*Focus: Critical path variance, earned value integrity, risk exposure, supply chain lead time.*

- **PR-1: Critical Path Float Preservation**: Does the proposed baseline preserve positive schedule float on the critical path? Any negative float without an authorized recovery schedule is an **IMMEDIATE GATE HALT**.
- **PR-2: Risk Exposure vs. Management Reserve**: Does the expected monetary value (EMV) of open technical risks exceed 80% of unallocated contingency reserve?
- **PR-3: Concrete Trade Space**: When an anomaly is reported, does the presenter provide at least two viable remediation options with quantified cost and schedule impacts?
- **PR-4: Supply Chain Single-Point Vulnerability**: Are long-lead components (> 16 weeks) identified with qualified alternate domestic suppliers?
- **PR-5: VCRM Closure Currency**: Are requirement verification closures backed by signed test reports rather than self-reported completion estimates?

### 2.3 ATO / Security Assessor Redline Rubric (Trust Enclaves & PPSM)
*Focus: Cryptographic compliance, PPSM enforcement, hardware boundaries, zeroization.*

- **SR-1: Deterministic PPSM Matrix**: Is every open port, socket, and serial protocol documented with transport protocol, source IP/MAC, destination, and payload format?
- **SR-2: FIPS 140-3 Cryptographic Boundary**: Does all sensitive telemetry traversing outside the physical enclave use hardware-validated FIPS 140-3 cryptographic modules?
- **SR-3: Diagnostic Port Hardware Interlocks**: Are debug, JTAG, and maintenance ports mechanically isolated or electrically disconnected during flight/production configuration?
- **SR-4: Cryptographic Key Management & Zeroization**: Is there an automated, test-verified zeroization mechanism capable of wiping cryptographic keys within 100 ms of tamper detection?
- **SR-5: Firmware Secure Boot Chain of Trust**: Is every executable binary and FPGA bitstream verified via hardware-enforced ECDSA/SHA-384 signatures before release of reset?

### 2.4 Field Technician & Operator Redline Rubric (Runbook Bindings & LOTO)
*Focus: Physical pinouts, discrete LED indicators, guarded effectors, safety interlocks.*

- **TR-1: Physical Pin and Port Specificity**: Is every interface signal mapped to an explicit connector and pin number matching approved wiring schematics?
- **TR-2: Unambiguous Tolerance Display**: Does every sensor readout state its nominal value alongside lower and upper shutdown redlines in the same SI units?
- **TR-3: Guarded Two-Step Actuation**: Are all destructive, high-voltage, or irreversible controls protected by a two-step Arm $\rightarrow$ Actuate latch with auto-disarm timeout?
- **TR-4: Lockout / Tagout (LOTO) Determinism**: Are upstream electrical disconnects and mechanical lockouts clearly visible before downstream effectors can be armed?
- **TR-5: Procedure Step Synchronization**: Does every operational action explicitly reference the active revision, section, and step number of the governing SOP?

### 2.5 Master Educator Redline Rubric (Cognitive Speed Limit & Semantic Binding)
*Focus: One-variable pacing, equation-to-visual term binding, color rationing, progressive disclosure.*

- **ER-1: Cognitive Speed Limit**: Does any viewport or slide introduce more than one new physical concept simultaneously? If multiple new variables vary without isolation, **FLAG AS PEDAGOGICAL OVERLOAD**.
- **ER-2: Semantic Equation-to-Visual Term Binding**: Is every term in displayed governing equations visually tied to a corresponding diagram curve or geometry via a unified role color token?
- **ER-3: Surface Neutrality Ratio**: Does the interface preserve $\ge 90\%$ neutral surface ink, with color strictly rationed to the active focal variable?
- **ER-4: Incremental Scaffold Progression**: Does the instructional arc progress systematically from qualitative orientation (L1) through governance (L2) to full physical rigor (L3)?
- **ER-5: Direct Parameter Anotation**: Are mathematical variables defined with physical units and textual tooltips directly adjacent to the equation rather than hidden in distant appendices?

### 2.6 First-Time Learner Redline Rubric (Cognitive Load & Grounded Abstractions)
*Focus: Plain-language anchors, apparatus schematics, error bars vs. theoretical curves.*

- **LR-1: Grounded Physical Anchor**: Does abstract theory begin with a concrete physical apparatus schematic or observable phenomenon before unrolling differential equations?
- **LR-2: Error Bar Grounding**: Are theoretical model curves displayed alongside discrete measured student data points carrying explicit experimental error bars?
- **LR-3: Acronym & Jargon De-Barnacling**: Is any unexplained institutional acronym or domain abbreviation present in introductory text?
- **LR-4: Controlled Variables Table**: Does the experiment layout feature an unambiguous table listing independent, dependent, and strictly held constant variables?
- **LR-5: Self-Check Diagnostics**: Are formative comprehension checkpoints embedded after each major derivation step before moving to advanced consequences?

### 2.7 Clinical Trial & Bedside Safety Rubric (`FDA IEC 62366` & `CONSORT`)
*Focus: Patient cohort integrity, use-related error guards, dosing corridors, alarm fatigue.*

- **CL-1: CONSORT Flow & Confidence Bounds**: Are enrolled, excluded, and lost-to-follow-up cohort counts ($n$) paired with 95% confidence intervals rather than bare p-values?
- **CL-2: Dose & Rate Hard-Stop Interlocks**: Per `FDA IEC 62366`, do infusion or therapeutic controls enforce unambiguous concentration units and dual-clinician confirmation for high-alert overrides?
- **CL-3: Bedside Alarm Fatigue Suppression**: Are non-actionable physiological transients prevented from triggering Tier-1 audible alarms?

### 2.8 SRE Incident Command & AI/Zero-Trust Rubric (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`)
*Focus: Tail latency provenance, SLO error-budget burn, AI calibration drift, zero-trust policy enforcement.*

- **SR-6: OTel Trace & Percentile Fidelity**: Are `OpenTelemetry` p95/p99/p99.9 tail curves backed by span counts and sampling rates rather than masked by mean averages?
- **SR-7: AI Calibration & Fallback Gate (`NIST AI RMF 100-1`)**: Does every probabilistic model surface report out-of-distribution drift / ECE bounds and route low-confidence outputs to deterministic fallback?
- **SR-8: Zero-Trust PEP Provenance (`NIST SP 800-207`)**: Are east-west service calls attested via Policy Enforcement Points with short-lived identities rather than implicit flat-subnet trust?

### 2.9 Manufacturing SPC & SCADA Quality Lead Rubric (`NIST/SEMATECH SPC`, `ISA-101`, `NRC NUREG-0700`, `Modbus`)
*Focus: Process capability margins, control-room situational awareness, field-bus safety interlocks.*

- **MF-1: Unmasked Process Capability ($C_{pk}$)**: Are `NIST/SEMATECH SPC` $\bar{X}/R$ limits (`UCL/CL/LCL`) and $C_{pk}$ margins reported with subgroup sample size $n$ rather than raw pass/fail percentages?
- **MF-2: Control-Room Situation Awareness (`ISA-101` / `NRC NUREG-0700`)**: Do operator consoles enforce low-chroma neutral backgrounds, suppress alarm floods, and bind `Modbus` register states to physical valve/interlock status?

### 2.10 Civic Capital & Treasury Board Rubric (`GAO` & `FRED/SEC`)
*Focus: Inflation-adjusted liquidity, obligated vs. reserve solvency, verifiable ledger provenance.*

- **CC-1: Real-Terms Deflation & Coverage (`FRED/SEC`)**: Are multi-year capital projections deflated using cited `FRED` price indices and `SEC` 10-Q/bond covenants with stressed DSCR floors?
- **CC-2: Appropriated Reserve & Audit Lineage (`GAO`)**: Are unobligated balances, contingency drawdowns, and grant expirations reconciled to `GAO` Green Book hash-verifiable ledgers?

---

## 3. Pass / Block Hard Rejection Triggers

If an artifact triggers any of the following **Hard Block Triggers**, the Murder Board must immediately reject the presentation without proceeding to a general vote:

| Trigger ID | Failure Category | Hard Rejection Trigger Description |
| :--- | :--- | :--- |
| **TRG-01** | **Physical Metrology** | Smooth Bezier curve or spline interpolation drawn through sparse discrete data points without showing raw scatter glyphs and error bars. |
| **TRG-02** | **Timing Closure** | Negative timing slack ($\Delta t < 0\text{ ps}$) or unallocated asynchronous clock domain crossing on a flight-critical bus. |
| **TRG-03** | **Programmatic Float** | Critical path schedule variance reporting negative float ($\Delta t_{\text{cp}} < 0\text{ days}$) without an attached, costed recovery plan. |
| **TRG-04** | **Security Boundary** | Undocumented open network port, implicit subnet trust violating `NIST SP 800-207`, or unencrypted telemetry crossing a trust boundary. |
| **TRG-05** | **Human Factors** | Flashing or pulsing UI elements; or destructive/high-alert clinical (`FDA IEC 62366`) or SCADA effector lacking a guarded two-step latch. |
| **TRG-06** | **Operational Safety** | Actuator switch control enabled while physical upstream LOTO or `ISA-101` / `NRC NUREG-0700` / `Modbus` safety interlock is open or unconfirmed. |
| **TRG-07** | **Traceability Breach** | Telemetry, VCRM row, `OpenTelemetry` SLI, or `GAO`/`SEC` ledger item lacking a direct reference to a test script, cal cert, trace, or commit hash. |
| **TRG-08** | **Audience Mismatch** | Presenting raw register hex dumps to an executive board, or presenting unitless color blobs to a discipline specialist. |
| **TRG-09** | **Pedagogical Overload** | Varying two independent variables simultaneously or unrolling dense equations without visual term-to-diagram color binding in an educational interface. |
| **TRG-10** | **Clinical Integrity** | Omitting `CONSORT` sample attrition / 95% CI bounds or masking `FDA IEC 62366` dose-unit mismatches. |
| **TRG-11** | **AI / Tail Blindspot** | Reporting mean latency instead of `OpenTelemetry` p99 tail bounds, or deploying probabilistic AI without `NIST AI RMF 100-1` drift/fallback gates. |
| **TRG-12** | **SPC Capability Masking** | Reporting batch yield without `NIST/SEMATECH SPC` $C_{pk}$ and `UCL/CL/LCL` corridor limits. |
| **TRG-13** | **Fiscal Illusion** | Presenting nominal multi-year civic capital returns without `FRED` inflation adjustment or `GAO`/`SEC` debt-coverage margins. |

---

## 4. Murder Board Scoring Worksheet

Reviewers record audit findings using the standard 100-point Murder Board evaluation worksheet:

```
+----------------------------------------------------------------------------------------------------------------------+
| ADVERSARIAL MURDER BOARD AUDIT WORKSHEET                                            | DATE: 2026-11-16 19:55 UTC     |
| REVIEW TARGET: DWDM Optical Payload Flight Readiness Package (Rev D)                | LEAD AUDITOR: CHIEF FELLOW     |
+----------------------------------------------------------------------------------------------------------------------+
| AUDIT SECTOR                         | WEIGHT | SCORE (0-100) | CRITICAL DEFICIENCIES IDENTIFIED                     |
|--------------------------------------+--------+---------------+------------------------------------------------------|
| 1. Physical Conservation & Metrology | 30%    | 94 / 100      | Optical link margin +2.4 dB verified; NIST cal valid |
| 2. Program Schedule & EVM Reserves   | 25%    | 88 / 100      | Critical path float +4 days; DIP delay mitigated     |
| 3. Security Enclave & PPSM Hardening | 25%    | 92 / 100      | TLS 1.3 mutual auth verified; PPSM table complete    |
| 4. Operator Safety & Runbook Binding | 20%    | 96 / 100      | 2-step latch verified; pinout J3-14 properly labeled |
+--------------------------------------+--------+---------------+------------------------------------------------------|
| COMPOSITE BOARD SCORE: 92.2 / 100 [PASS THRESHOLD: >= 85.0]                                                         |
| HARD BLOCK TRIGGERS CHECK: ZERO TRIGGERS TRIPPED [PASS]                                                              |
| DISPOSITION: APPROVED FOR EXTERNAL FLIGHT READINESS REVIEW BOARD RELEASE                                            |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 5. Post-Audit Remediation Workflow

When an artifact fails an Adversarial Murder Board audit, it follows a strict remediation protocol:

```
[AUDIT FAILED: REDLINE ISSUED]
              |
              v
[STEP 1: ROOT-CAUSE ASSIGNMENT]
- Audit Lead logs exact triggered rubric items and assigns designated engineering owner.
- Anomaly logged in project issue tracker with 24-hour resolution SLA.
              |
              v
[STEP 2: ARTIFACT REVISION & RE-TEST]
- Author updates presentation, re-runs HIL test script, or acquires missing cal certificates.
- Updates verified against "Grill Me" Audience Intake contract.
              |
              v
[STEP 3: DELTA RE-AUDIT]
- Auditor re-examines only the redlined items.
- Upon unanimous clearance: digital signature appended to Board Pass Certificate.
```

---

## 6. Murder Board Verification Rubric

Before certifying that a design package or briefing is ready for external delivery, verify against these six gates:

1. **4 Universal Invariants & Red-Team Coverage**: Did independent reviewers verify all 4 Universal Audience Evaluation Invariants across the applicable domain rubrics (Chief Engineer, PM, ATO/ISSM, Operator, Clinical Safety, SRE Incident Command, SPC Quality Lead, Civic Capital Board, and Educator/Learner)?
2. **Zero Hard Block Triggers**: Have all thirteen hard block triggers (TRG-01 through TRG-13) been explicitly checked and cleared?
3. **Composite Score $\ge 85$**: Does the composite score across all relevant audit sectors meet or exceed the 85-point threshold?
4. **All Redlines Closed**: Have all action items from previous audit cycles been resolved with documented physical, clinical, or audit proof?
5. **Calibrated Units Preserved**: Are all displayed parameters presented in explicit physical, clinical, statistical, or financial SI/audit units?
6. **Signed Board Certificate**: Is the formal JSON audit certificate digitally signed and archived in the project repository?

---

## 7. Cross-Reference Links

- For audience-specific requirements, see [../lenses/discipline-engineer.md](../lenses/discipline-engineer.md), [../lenses/program-manager.md](../lenses/program-manager.md), [../lenses/technician-and-operator.md](../lenses/technician-and-operator.md), [../lenses/educator-and-mentor.md](../lenses/educator-and-mentor.md), and [../lenses/student-and-learner.md](../lenses/student-and-learner.md).
- For pre-build intake protocols, see [grill-me-audience-intake.md](grill-me-audience-intake.md).
- For review-room dual-layer layout implementations, see [review-room-dual-layer.md](review-room-dual-layer.md).
- For deep-dive forensic investigation templates, see [../tempos/analytical-deep-dive.md](../tempos/analytical-deep-dive.md).
