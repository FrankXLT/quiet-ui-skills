# Audience Lens: Program Manager & Resource Allocator

This guide establishes the translation protocols, metric syntheses, and decision gate structures required when presenting technical engineering data to Program Managers (PM), Integrated Product Team (IPT) Leads, Acquisition Directors, and Milestone Gate Authorities.

---

## 1. Persona Profile & Decision Mandate

| Dimension | Program Management Specification |
| :--- | :--- |
| **Role Archetypes** | Program Manager (PM), IPT Director, Mission Acquisition Executive, Resource & Budget Authority |
| **Primary Workflow** | Milestone gate reviews (PDR, CDR, MRR, FRR), critical path management, earned value analysis, risk reserve allocation |
| **Cognitive Framework** | Schedule critical path variance ($\Delta \text{days}$), cost performance index (CPI), schedule performance index (SPI), risk burn-down dollars |
| **Acceptance Standard** | Technical excellence is necessary but insufficient; every engineering finding must translate into cost, schedule, risk, or trade space |
| **Review Velocity** | Rapid gate compression (1 to 5 minutes per milestone decision block) |

Program Managers carry ultimate fiduciary and programmatic responsibility for mission delivery. They are constantly navigating the iron triangle of scope, cost, and schedule. When technical teams present raw physics derivations, register dumps, or academic dissertations without tying them to critical path variance or budget exposure, the PM cannot assess risk or authorize resource reallocations.

---

## 2. Native Units of Proof

To establish immediate decision readiness with a Program Manager, technical briefings must present the following native units of proof:

1. **Critical Path Variance ($\Delta t_{\text{cp}}$)**: Variance expressed strictly in calendar working days relative to the baselined schedule network (e.g., `Critical Path Delta: -4.5 Days [Path: Payload Flight FPGA -> Subsystem HIL Integration]`).
2. **Earned Value Management (EVM) Metrics**:
   - Budgeted Cost of Work Scheduled ($\text{BCWS}$) vs. Budgeted Cost of Work Performed ($\text{BCWP}$).
   - Actual Cost of Work Performed ($\text{ACWP}$).
   - Cost Performance Index ($\text{CPI} = \text{BCWP} / \text{ACWP}$) and Schedule Performance Index ($\text{SPI} = \text{BCWP} / \text{BCWS}$).
3. **Management Reserve and Risk Exposure**: Unallocated financial reserve dollars vs. expected monetary value (EMV) of open risks ($\sum P_i \times C_i$).
4. **Milestone Go / No-Go Gate Criteria**: Binary, test-verified preconditions required to transition through major program milestones (e.g., CDR Gate 4: "100% of flight schematic reviews signed, thermal margin $\ge 15\%$, timing margin $\ge 20\%$").
5. **Supply Chain Lead-Time Buffers**: Procurement lead time against inventory delivery thresholds (e.g., `Rad-Hard ADC: 26 weeks lead time, inventory buffer: 4 weeks reserve`).
6. **Technical Debt Dollar Encumbrance**: Estimated remediation cost and schedule penalty if an architectural work-around is carried into production rather than resolved immediately.
7. **Resource Burn-Rate Ratios**: Actual engineering hours burned per calendar week compared against the baselined staffing profile.

---

## 3. Presenter Biases to Scrub

When translating engineering status for a Program Manager, strip out the following presentation flaws:

```
[PRESENTER BIAS]                                   [PROGRAM MANAGER SCRUB DIRECTIVE]
------------------------------------------------------------------------------------------------------------------------
Raw register hex dumps and bitfields                --> Summarize as functional capability achieved vs. remaining defect count.
Endless academic paper citations without impact     --> State exact engineering trade-off: mass savings vs. schedule days.
Theoretical trade studies exceeding gate schedule  --> Freeze trade space; present bounded options within current milestone.
Qualitative "feeling good about progress" claims    --> State SPI, CPI, and verified verification requirement closure count.
Unbounded technical perfectionism                   --> State "Compliant with specification margin" and lock design.
Isolated physics anomalies without critical path    --> Quantify impact: "Pushes HIL test entry by 3 days; absorbed by float."
Unbudgeted feature expansion ("nice to have")      --> Block scope creep; log as deferred block upgrade for future phase.
```

---

## 4. Receiver Dealbreakers

A presentation or dashboard presented to a Program Manager will trigger immediate escalation or gate freeze upon encountering any of the following flaws:

- **Missing Cost / Schedule Trade Space**: Presenting a technical problem without providing at least two quantified remediation options (Cost, Schedule, Scope).
- **Hidden Technical Debt Risks**: Masking a failed verification test as "informally passed with caveats" without registering a tracked program risk.
- **Unquantified Critical Path Delays**: Stating that a subsystem is "experiencing minor delays" without providing the updated CPM (Critical Path Method) float calculation.
- **Single-Source Bottlenecks Omitted**: Concealing component single-source vulnerability until delivery dates slip beyond flight integration gates.
- **Unstated Resource Consumptive Burn**: Reporting progress while concealing that engineering overtime burn-rate is exhausting IPT cost reserves at 1.4x baseline.
- **Surprise Gate Redlines**: Introducing critical blockers during the final gate review that were omitted from weekly status dashboards.

---

## 5. Chief Engineer to Program Manager Translation Bridge

The following matrix illustrates how discipline engineering findings must be translated into programmatic decision parameters:

| Discipline Engineering Finding | Programmatic Decision Translation | Decision Impact & Action Authority |
| :--- | :--- | :--- |
| "FPGA static timing analysis failed on $250\text{ MHz}$ core clock domain with $-320\text{ ps}$ slack due to routing congestion in block B." | **Critical Path Slip: 3 Days**. Requires pipelining refactor (20 engineering hours). Absorbed by 5-day integration buffer. Net Gate D impact: **0 Days**. | Action: PM approves 1 engineer overtime allocation; design freeze preserved. |
| "Thermal vacuum testing revealed cold plate interface temperature reaches $52^\circ\text{C}$, exceeding $45^\circ\text{C}$ qualification limit." | **Risk Elevation (Risk R-108)**: 50% probability of requiring heat pipe redesign. Cost exposure: **$45,000**. Schedule slip if unmitigated: **14 Days**. | Action: Authorize parallel coupon test for thermal gap pad upgrade ($6,500 spend). |
| "Optical transceiver vendor notified us of an 8-week delay on custom hermetic DIP package." | **Critical Path Breach: -18 Days**. Subsystem delivery slips beyond environmental chamber reservation date. | Action: PM initiates secondary domestic vendor qualification; expedites $18,000 procurement fee. |
| "Mass property rollup indicates total instrument dry mass is $14.2\text{ kg}$ against $15.0\text{ kg}$ allocation ($+0.8\text{ kg}$ margin)." | **Mass Margin Green**: 5.3% positive reserve. No launch vehicle payload penalties triggered. Design mass locked. | Action: Freeze mechanical interface drawings; close mass tracking action item. |
| "Bit Error Rate test completed $10^{13}$ bits with zero errors at nominal power." | **Milestone Closure**: VCRM Requirement REQ-COMM-04 verified. Unlocks Milestone Progress Payment Gate 3 ($120,000). | Action: Sign milestone completion certificate; release vendor invoice. |

---

## 6. Risk Burndown & Reserve Tracking Ledger

Program Managers manage program health through active risk valuation and contingency reserve management:

| Risk ID | Title & Root Cause | Prob (%) | Cost Exposure | Float Impact | Mitigation Strategy | Owner | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-102** | FPGA core routing congestion slips timing closure | 30% | $12,500 | -3 Days | Insert 2 pipelining registers into FIR filter core | Lead DSP | MITIGATING |
| **R-108** | Cold plate heat flux exceeds thermal gap pad rating | 50% | $45,000 | -14 Days | Procure carbon-nanotube thermal interface material | Thermal Lead | ACTIVE |
| **R-114** | Single-source optical modulator assembly lead-time | 65% | $32,000 | -18 Days | Place non-cancellable pre-order with alternate foundry | Supply Chain | ESCALATED |
| **R-121** | Harness routing exceeds vehicle mass reserve by 180 g | 20% | $8,000 | 0 Days | Substitute copper braid with silver-plated aluminum | Mech Lead | MONITORING |

---

## 7. Program Manager Executive Gate Display Pattern

When delivering milestone gate status to a Program Manager, use the structured executive quadrant layout:

```
+----------------------------------------------------------------------------------------------------------------------+
| PROGRAM STATUS WORKBENCH: PROJECT PHOBOS-DWDM | MILESTONE: CRITICAL DESIGN REVIEW (CDR)      | CYCLE: FY26-Q3        |
+----------------------------------------------------------------------------------------------------------------------+
| MILESTONE GATE DISPOSITION: [ CONDITIONAL GO ]       | EARNED VALUE METRICS: CPI = 1.04 | SPI = 0.98 | FLOAT: +4 DAYS  |
| Primary Driver: Optical module qualification buffer absorbed by vendor DIP package delay. Corrective action in place. |
+------------------------------------------------------+---------------------------------------------------------------+
| CRITICAL PATH SCHEDULE DELTA                         | RISK RESERVE & EXPOSURE BURNDOWN                              |
| Subsystem A (Digital Baseband):  +2 Days (Float)     | Total Management Reserve:        $240,000                     |
| Subsystem B (Optical Engine):    -3 Days [CRITICAL]  | Total Unmitigated Risk Exposure: $185,000 (77% of reserve)    |
| Subsystem C (Power Converter):   +6 Days (Float)     | Top Open Risk: R-108 (Thermal Gap Pad Re-qualification)       |
| Flight Software Release 2.1:     -1 Day  (Float)     | Risk Trend: 3 Closed this cycle | 1 Added | 0 Escalated       |
+------------------------------------------------------+---------------------------------------------------------------+
| TECHNICAL REQUIREMENT CLOSURE (VCRM)                 | RESOURCE RUN-RATE & SUPPLY CHAIN                              |
| Total Allocations:   148 Requirements                | Active Staffing:     14 FTEs (Baseline: 14 FTEs)              |
| Verified by Test:    94 (63.5%)                      | Monthly Burn Rate:   $182,000 / mo (On Budget)                |
| Verified by Analysis: 38 (25.7%)                     | Supply Chain Status: 92% parts in store | 1 long-lead active  |
| Open / In Progress:  16 (10.8%) [All on schedule]    | Next Milestone Gate: Environmental Test Readiness (42 Days)   |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 8. Milestone Gating Contract Schema

Every programmatic milestone must adhere to a strict machine-readable contract declaring required deliverables, verification closure thresholds, and financial release gates:

```json
{
  "milestone_id": "GATE_CDR_04",
  "milestone_name": "Critical Design Review - Optical Payload",
  "target_date_utc": "2026-11-30T17:00:00Z",
  "disposition_authority": "Program Executive Board",
  "exit_criteria": {
    "vcrm_closure_percentage_min": 85.0,
    "critical_path_float_min_days": 0.0,
    "unmitigated_risk_exposure_ceiling_usd": 200000.0,
    "open_priority_1_anomalies_max": 0
  },
  "financial_authorization": {
    "milestone_completion_payment_usd": 120000.0,
    "contingency_draw_authorized_usd": 25000.0
  }
}
```

---

## 9. Program Manager Verification Rubric

Before submitting any technical review presentation or milestone gate packet to a Program Manager, audit against these seven criteria:

1. **Explicit Schedule Float Quantification**: Is the impact on critical path float clearly stated in calendar days for every reported variance?
2. **Cost Exposure Translation**: Are engineering anomalies paired with dollar estimates for test replans, redesigns, or expediting fees?
3. **Dual Remediation Options**: Does every identified problem come accompanied by at least two viable mitigation options with trade-offs?
4. **VCRM Closure Percentage**: Is progress reported as the verified closure of technical requirements rather than subjective tasks?
5. **Supply Chain Lead Time Buffer**: Are long-lead components tracked against integration need dates with positive buffers?
6. **No Uncalibrated Register Dumps**: Are raw technical traces, hex offsets, and mathematical proofs moved to lower-layer appendices?
7. **Resource Burn Transparency**: Is the monthly cost burn rate aligned with planned earned value generation?

---

## 10. Cross-Reference Links

- For interface boundary contracts and VCRM engineering details, see [project-systems-engineer.md](project-systems-engineer.md).
- For first-principles physics and raw component models, see [discipline-engineer.md](discipline-engineer.md).
- For executive minute-by-minute gate compression templates, see [../tempos/executive-minutes.md](../tempos/executive-minutes.md).
- For formal adversarial review room procedures, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).
