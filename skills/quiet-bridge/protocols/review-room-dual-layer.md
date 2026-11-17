# Translation Protocol: Review Room Dual-Layer Architecture

This protocol establishes the architectural layout, CSS container specifications, and cross-audience state synchronization required to construct dual-layer review-room interfaces under Quiet UI Pillar 3.

---

## 1. Purpose & The Dual-Audience Synchronization Problem

Major program milestone reviews (such as Flight Readiness Reviews, Critical Design Reviews, and Operational Cutover Boards) assemble two radically different audiences in the same room:
1. **Executive Decision Authorities**: Need rapid, high-level gate compression (1–3 minutes), clear BLUF disposition status, and unvarnished trade spaces.
2. **Discipline Specialists & Technical Assessors**: Demand uncompromised Layer 3 (L3) physical proof, raw scatter data, error bounds, and mathematical derivations.

Traditional presentations fail this environment completely: if the presenter displays high-level slides, the technical specialists distrust the assertions; if the presenter displays deep physics and code traces, the executives lose situational awareness and decision momentum.

The **Review Room Dual-Layer Architecture** solves this through a vertically synchronized layout:
- **Upper Executive Gate Band (180–240px)**: Pinned at the top of the viewport; presents the BLUF disposition pill, a 4-KPI metric strip in native SI units, and the critical path trade box.
- **Lower Evidentiary Proof Stage**: A scrollable, high-density analytical workbench presenting governing equations, discrete scatter plots, residual distributions, and calibration provenance.

---

## 2. Structural Layout & CSS Container Specifications

The interface is structured using modern CSS Grid and Flexbox with strict height allocations:

```
+----------------------------------------------------------------------------------------------------------------------+
| VIEWPORT (100vh / 100vw)                                                                                            |
| +------------------------------------------------------------------------------------------------------------------+ |
| | UPPER EXECUTIVE GATE BAND: Pinned, sticky container (Height: 210px, z-index: 100)                                | |
| | - BLUF Disposition Pill (GO / NO-GO / CONDITIONAL GO)                                                            | |
| | - 4-KPI Metric Strip (Preserved SI Units: Timing Slack, Optical Margin, Schedule Float, Risk Reserve)          | |
| | - Critical Path Trade Box & Active Precondition Directives                                                      | |
| +------------------------------------------------------------------------------------------------------------------+ |
| | LOWER EVIDENTIARY PROOF STAGE: Scrollable container (Height: calc(100vh - 210px), overflow-y: auto)               | |
| | - Left Sidebar: Section Navigation Spine (Width: 240px)                                                          | |
| | - Center Stage: Deep Analytical Figures, Math Derivations, Eye Diagrams, Residual Plots (Width: 1fr)             | |
| | - Right Inspector: Parameter Allocation Matrix, NIST Cal Hashes, Git Commit Provenance (Width: 320px)           | |
| +------------------------------------------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------------------------------------------+
```

### CSS Implementation Blueprint

```css
/* Container Shell */
.va-review-room {
  display: grid;
  grid-template-rows: 210px 1fr;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  background-color: var(--bg-canvas, oklch(0.18 0.02 250));
  color: var(--text-primary, oklch(0.92 0.01 250));
  font-family: var(--font-sans, system-ui, sans-serif);
  overflow: hidden;
}

/* Pinned Upper Executive Gate Band */
.va-gate-band {
  position: sticky;
  top: 0;
  height: 210px;
  background-color: var(--bg-elevated, oklch(0.22 0.02 250));
  border-bottom: 2px solid var(--border-hairline, oklch(0.32 0.02 250));
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}

/* Lower Evidentiary Proof Stage */
.va-proof-stage {
  display: grid;
  grid-template-columns: 240px 1fr 320px;
  height: 100%;
  overflow-y: auto;
  scroll-behavior: smooth;
  gap: 1.5rem;
  padding: 1.5rem;
}

@media (max-width: 1200px) {
  .va-proof-stage {
    grid-template-columns: 200px 1fr;
  }
  .va-inspector-rail {
    display: none;
  }
}
```

---

## 3. Cross-Audience State Synchronization

The Upper Gate Band and Lower Proof Stage are not isolated; they maintain continuous bidirectional state synchronization:

```
[EXECUTIVE BAND: USER CLICKS "OPTICAL LINK MARGIN: +2.4 dB"]
                            |
                            v
[EVENT: dispatchEvent("va:kpi-select", { metricId: "OPTICAL_MARGIN" })]
                            |
                            v
[LOWER PROOF STAGE: SYNCHRONIZED REACTION]
1. Lower stage smoothly scrolls to Section 3.2 ("Optical Link Metrology").
2. The corresponding Laser Launch vs. Receiver Eye Diagram highlights with a 2px focus ring.
3. The right-hand Metrology Inspector automatically loads NIST calibration certificate NIST-OPT-881.
4. The governing link budget formula highlights the term: Margin = Prx - Psens.
```

This interaction allows the executive to demand: *"Where does that +2.4 dB come from?"* and the presenter or specialist to answer instantly by clicking the tile, revealing the underlying physics in 200 milliseconds.

---

## 4. Concrete Walkthrough Scenario: DWDM Optical Cutover FRR

The following walkthrough illustrates the dual-layer architecture applied to a high-consequence Flight Readiness Review (FRR) for Dense Wavelength Division Multiplexing (DWDM) payload cutover:

```
+----------------------------------------------------------------------------------------------------------------------+
| UPPER GATE BAND (210px) - FLIGHT READINESS REVIEW: DWDM OPTICAL PAYLOAD CUTOVER             | MISSION TIME: T-01:30  |
+----------------------------------------------------------------------------------------------------------------------+
| [ DISPOSITION: CONDITIONAL GO ] | REQUISITE: Fiber Ch-B ferrule visual inspection tag verified before T-00:30        |
|                                                                                                                      |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
| | TIMING SLACK MARGIN     | OPTICAL LINK MARGIN     | CRITICAL PATH FLOAT     | OPEN RISK EXPOSURE                 | |
| | +3.14 ns (+31.4%)       | +2.4 dB (Req: >= 1.5 dB)| +4 Days (Ahead)         | $38,000 (15.8% Contingency)        | |
| | [Status: PASS]          | [Status: PASS - ACTIVE] | [Status: ON SCHEDULE]   | [Status: LOW EXPOSURE]             | |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
+----------------------------------------------------------------------------------------------------------------------+
| LOWER PROOF STAGE (calc(100vh - 210px)) - SCROLLABLE ANALYTICAL WORKBENCH                                            |
|                                                                                                                      |
| [NAV SPINE]       | 3.2 OPTICAL LINK BUDGET RECONCILIATION & EYE DIAGRAM                    | [METROLOGY INSPECTOR]  |
| - 1. Executive    | Governing Equation:                                                     | Channel: DWDM Lambda 4 |
| - 2. Pinouts      |   P_rx = P_tx - alpha_fiber * L - N_conn * Loss_conn - Loss_mod         | Wavelength: 1550.12 nm |
| - 3. Optics [ACT] | Measured Parameters:                                                    | Launch Power: +0.2 dBm |
| - 4. Timing       | - Laser Output Power (P_tx):        +0.20 dBm (+/- 0.05 dBm)            | Fiber Length: 42.1 km  |
| - 5. Security     | - Fiber Attenuation (alpha * L):   -14.80 dB (0.35 dB/km @ 1550 nm)     | Total Loss: -16.00 dB  |
| - 6. VCRM Rows    | - Connector Loss (4x mates):        -1.20 dB (0.30 dB/mate)             | Sensitivity: -18.2 dBm |
|                   | - Received Power (P_rx):           -15.80 dBm                           | Margin: +2.40 dB       |
|                   | - Receiver Sensitivity Threshold:  -18.20 dBm (BER <= 1.0e-12)          | NIST Cert: NIST-OPT-881|
|                   | - Link Margin:                     -15.80 - (-18.20) = +2.40 dB [PASS]  | Cal Date: 2026-11-10   |
|                   |                                                                         | Hash: 4f8a9e2c...      |
|                   | [ PERSISTENCE EYE DIAGRAM: EXTINCTION RATIO = 10.2 dB | SNR = 14.8 dB ] | Status: VERIFIED       |
|                   |                                                                         |                        |
|                   | 3.3 RESIDUAL FIT ANALYSIS                                               | [ RAW DATASET (12MB) ] |
|                   | Residual drift across 5 thermal cycles: +/- 0.12 dB (within 3-sigma).   | Format: HDF5 / CSV     |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 5. Review Room Verification Rubric

Before deploying a dual-layer review-room interface for a milestone board, verify against these seven architectural gates:

1. **Gate Band Pinned & Immovable**: Is the upper executive band fixed at 180–240px height with a distinct boundary elevation?
2. **Preserved SI Units in KPI Strip**: Does every KPI tile display explicit physical or programmatic SI units rather than unitless scores?
3. **Smooth Bidirectional Sync**: Does clicking any upper KPI tile scroll smoothly to the corresponding lower proof section within 250 ms?
4. **Autonomous Lower Stage Scrolling**: Does the lower evidentiary stage scroll independently without causing the upper band to jump or hide?
5. **Traceability Inspector Rail**: Does the interface provide a dedicated side panel for instrument calibration IDs, git commit hashes, and dataset downloads?
6. **Responsive Layout Resilience**: Does the layout gracefully degrade to a two-column or stacked view on viewports narrower than 1200px?
7. **Zero Decorative Distraction**: Are ambient animations, carousel auto-plays, and non-functional graphical flourishes completely scrubbed?

---

## 6. Cross-Reference Links

- For the executive decision compression tempo, see [../tempos/executive-minutes.md](../tempos/executive-minutes.md).
- For analytical deep-dive metrology standards, see [../tempos/analytical-deep-dive.md](../tempos/analytical-deep-dive.md).
- For pre-build intake protocols, see [grill-me-audience-intake.md](grill-me-audience-intake.md).
- For adversarial red-team rubrics and hard block triggers, see [adversarial-murder-board.md](adversarial-murder-board.md).
- For Quiet UI styling and container tokens, see [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md).
