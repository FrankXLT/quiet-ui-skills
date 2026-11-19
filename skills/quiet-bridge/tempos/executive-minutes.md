# Operational Decision Tempo: Executive Minutes (1–3 Minutes)

This guide defines the compression rules, disposition architecture, and progressive-disclosure patterns required when presenting mission-critical decisions to executive authorities within a 1 to 3 minute review window.

---

## 1. Operating Tempo & Executive Compression Mandate

| Dimension | Executive Decision Specification |
| :--- | :--- |
| **Review Window** | 60 to 180 seconds from first glance to binding executive authorization |
| **Operational Modes** | Milestone Go / No-Go gates, Flight Readiness Reviews (FRR), Clinical DSMB (`CONSORT`, `FDA IEC 62366`), SRE / AI Release Gates (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`), Plant Cutover (`NIST/SEMATECH SPC C_pk`, `ISA-101`, `NRC NUREG-0700`, `Modbus`), Civic Capital Votes (`GAO`, `FRED/SEC`) |
| **Core Principle** | **Compress presentation volume, never remove units.** Deliver exact physical, clinical, statistical, or fiscal margins in the leader's native discipline. |
| **Cognitive Framework** | Bottom Line Up Front (BLUF), bounded trade spaces, quantified residual risk exposure, unambiguous exit criteria |
| **Screen Architecture** | Single-screen view; zero vertical page jumping; click-to-expand progressive disclosure for `L3` proof data |

Executive leaders do not require simplistic consumer language, nor do they tolerate marketing summaries. An engineering vice president expects exact picosecond timing slack; a DSMB chair expects `CONSORT` hazard ratios with 95% CI; a VP of Reliability expects `OpenTelemetry` error-budget burn; a plant director expects $C_{pk}$ capability margins; a municipal CFO expects `FRED`-deflated DSCR. The executive tempo succeeds by ruthless prioritization of decision-critical parameters, not by dumbing down the underlying reality.

---

## 2. The Preservation of Native Units Law

A catastrophic failure pattern in leadership presentations is replacing native metrics with arbitrary color badges or normalized progress bars (e.g. "Safety: Green" or "Health: 85%").

Under Quiet UI Pillar 3, the **Preservation of Native Units Law** mandates:
- **Engineering Chief**: $+18.6\text{ ps}$ timing margin, $+2.4\text{ dB}$ link margin, $89.2^\circ\text{C}$ junction ceiling.
- **Program Director**: $-3\text{ calendar days}$ critical path variance, $\$45,000$ risk exposure, $\text{CPI} = 1.04$.
- **Clinical / DSMB Chair (`FDA IEC 62366`, `CONSORT`)**: Hazard ratio $0.71$ ($95\%\text{ CI } 0.58\text{--}0.87$), $0$ high-alert dose-error near-misses.
- **SRE / CISO (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`)**: $22\%$ SLO error-budget left, p99 $= 185\text{ ms}$, ECE drift $= 0.024$, $100\%$ PEP mTLS enforcement.
- **Plant Operations VP (`NIST/SEMATECH SPC`, `ISA-101`, `NRC NUREG-0700`, `Modbus`)**: Line $C_{pk} = 1.48$ ($\ge 1.33$), alarm flood rate $= 3/10\text{ min}$, `Modbus` PLC safety interlocks verified.
- **Civic Capital / Treasury Chair (`GAO`, `FRED/SEC`)**: Real DSCR $= 1.24\times$ (`FRED` CPI-U adjusted), $142\text{ days}$ unobligated cash runway, $0$ `GAO`/`SEC` audit exceptions.

Never present a unitless score, a 1-to-5 star rating, or an arbitrary 0–100% health score to an executive decision-maker.

---

## 3. Executive Single-Screen Layout Architecture

The executive presentation stage consists of three synchronized visual zones designed for immediate scanning:

```
+----------------------------------------------------------------------------------------------------------------------+
| EXECUTIVE GATE DISPOSITION: FLIGHT READINESS REVIEW [FRR-DWDM-OPTICAL]                      | 2026-11-16 19:40 UTC   |
+----------------------------------------------------------------------------------------------------------------------+
| [ BLUF DISPOSITION: CONDITIONAL GO ]                                                         DECISION AUTHORITY: LSE |
| Primary Prerequisite: Optical Transceiver Channel B attenuation within margin; pending coupon burn-in sign-off at T-2h.|
+----------------------------------------------------------------------------------------------------------------------+
| 4-KPI METRIC STRIP (PRESERVED NATIVE UNITS)                                                                          |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
| | TIMING SLACK MARGIN     | OPTICAL LINK MARGIN     | CRITICAL PATH FLOAT     | UNMITIGATED RISK EXPOSURE          | |
| | +3.14 ns (+31.4%)       | +2.4 dB (Min: +1.5 dB)  | +4 Days (Ahead)         | $38,000 (15.8% Reserve)            | |
| | Target: >= 2.0 ns       | Target: >= 1.5 dB       | Target: >= 0 Days       | Reserve: $240,000                  | |
| | Status: PASS (NOMINAL)  | Status: PASS (NOMINAL)  | Status: PASS (ON SCHED) | Status: LOW EXPOSURE               | |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
|                                                                                                                      |
| CRITICAL PATH TRADE & RESIDUAL RISK SPACE                                                                            |
| [TRADE OPTION A: AUTHORIZE IMMEDIATE CUTOVER] (RECOMMENDED)                                                          |
| - Physics Margin: Optical margin +2.4 dB exceeds requirement by 0.9 dB.                                              |
| - Program Impact: 0 days critical path delay. Unlocks Milestone Gate 4 progress payment.                             |
| - Residual Risk: 4.2% probability of single-frame transient drop during thermal ramp; absorbed by FEC.              |
|                                                                                                                      |
| [TRADE OPTION B: POSTPONE CUTOVER BY 48 HOURS]                                                                       |
| - Physics Margin: Additional 48-hour soak test confirms zero drift across 5 cold cycles.                             |
| - Program Impact: Consumes 2 days of schedule float. Overtime cost: $12,400.                                         |
+----------------------------------------------------------------------------------------------------------------------+
| [ DRILL DOWN: EXPAND L3 EVIDENTIARY PROOF DATA (VCRM ROWS, SPECTRAL PLOTS, NIST CAL HASHES) ]                       |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Progressive Disclosure: In-Context Evidentiary Drawers

Executives must never be forced to leave the summary screen to inspect supporting technical proof. When an executive questions a KPI, clicking that metric expands an in-context evidentiary drawer immediately below:

```
[KPI TILE: CLICKED BY EXECUTIVE]
[ OPTICAL LINK MARGIN: +2.4 dB ]
          |
          v (Smooth accordion animation expands L3 stage inline)
+----------------------------------------------------------------------------------------------------------------------+
| L3 PROOF DRAWER: OPTICAL LINK BUDGET RECONCILIATION [NIST-CAL-OPT-881]                                               |
| - Laser Launch Power (Tx):        +0.2 dBm (+/- 0.1 dBm) [Calibrated 2026-11-10]                                    |
| - Fiber Cable Insertion Loss:     -14.8 dB (Measured across 42 km field link)                                        |
| - Optical Connector Losses (4x):  -1.2 dB (-0.30 dB per mate, cleaned per SOP-OPT-04)                                |
| - Receiver Sensitivity Ceiling:   -18.2 dBm (BER <= 1.0e-12 threshold)                                               |
| - Net Received Power:             -15.8 dBm                                                                          |
| - Exact Link Margin:              -15.8 dBm - (-18.2 dBm) = +2.4 dB [PASS]                                           |
| Link to Raw Metrology Dataset: [hash: 4f8a9e2c... / git: payload/optics@b4e18c]                                      |
+----------------------------------------------------------------------------------------------------------------------+
```

### 4.1 Cross-Domain Gate & L3 Drawer Equivalents

| Domain | BLUF KPI Strip (Preserved Native Units) | In-Context `L3` Proof Drawer |
| :--- | :--- | :--- |
| **Clinical Safety / ICU (`FDA IEC 62366`, `CONSORT`)** | HR $0.71$ (95% CI $0.58\text{--}0.87$), cohort $N=1,240$, $0$ IEC 62366 use-errors. | `CONSORT` flow table, Kaplan-Meier survival residuals, summative simulation log. |
| **SRE / Cloud / AI Ops (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`)** | p99 $= 185\text{ ms}$, SLO budget left $= 22\%$, ECE drift $= 0.024$, PEP $= 100\%$. | `OpenTelemetry` span waterfall, OOD calibration curve, `NIST SP 800-207` PEP policy diff. |
| **Industrial Plant / SCADA (`NIST/SEMATECH SPC C_pk`, `ISA-101`, `NRC NUREG-0700`, `Modbus`)** | Line $C_{pk} = 1.48$ ($\ge 1.33$), alarm rate $= 3/10\text{ min}$, `Modbus` interlocks PASS. | Shewhart $\bar{X}/R$ (`UCL/CL/LCL`), `Modbus` scan jitter log, EOP test sign-off. |
| **Civic Capital / Treasury (`GAO`, `FRED/SEC`)** | Real DSCR $= 1.24\times$ (`FRED` CPI-U), cash runway $= 142\text{ days}$, $0$ `GAO` exceptions. | `SEC` 10-Q debt schedule, `+200 bps` stress table, SHA-256 ledger digest. |

---

## 5. Decision Gate Contract Schema

Every executive review session produces a deterministic decision record encoded as a structured JSON artifact:

```json
{
  "gate_review_id": "FRR-DWDM-2026-11-16",
  "review_title": "DWDM Optical Cutover Flight Readiness Review",
  "disposition": "CONDITIONAL_GO",
  "timestamp_utc": "2026-11-16T19:40:00Z",
  "decision_authority": {
    "name_title": "Chief Systems Engineer / Flight Director",
    "signature_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "evaluated_kpis": [
    {
      "metric_name": "Timing Slack Margin",
      "value_reported": 3.14,
      "unit": "ns",
      "margin_pct": 31.4,
      "gate_status": "PASS"
    },
    {
      "metric_name": "Optical Link Margin",
      "value_reported": 2.4,
      "unit": "dB",
      "minimum_threshold": 1.5,
      "gate_status": "PASS"
    },
    {
      "metric_name": "Critical Path Float",
      "value_reported": 4.0,
      "unit": "days",
      "gate_status": "PASS"
    }
  ],
  "authorized_contingency": {
    "option_selected": "OPTION_A",
    "authorized_cost_usd": 0.0,
    "conditions_precedent": [
      "Thermal coupon burn-in completed at T-2h with zero unrecoverable frame slips",
      "Field technician confirms optical ferrule visual inspection tag TAG-OPT-102"
    ]
  }
}
```

---

## 6. Executive Presentation Redline Rubric

Before placing an artifact before an executive board or decision authority, audit against these seven rules:

1. **BLUF Disposition Prominence**: Is the overarching disposition (GO, NO-GO, CONDITIONAL GO) visible within the top 80 pixels of the stage?
2. **Preservation of Units**: Are all displayed KPIs accompanied by explicit physical or financial SI units rather than naked numbers or color blobs?
3. **Bounded Trade Space**: Are decision alternatives structured into discrete, mutually exclusive options with quantified cost and schedule deltas?
4. **Single-Screen Footprint**: Does the primary executive summary fit entirely within a standard 1080p viewport without requiring page scrolling?
5. **Direct L3 Proof Traceability**: Can every summary KPI be expanded in-place to inspect underlying raw sensor telemetry, equations, and calibration hashes?
6. **No Subjective Platitudes**: Are adjectives such as "very strong", "nominal progress", and "minimal risk" replaced with concrete numerical margins?
7. **Actionable Preconditions**: For conditional approvals, are the exit criteria stated as verifiable, binary test checkpoints?

---

## 7. Cross-Reference Links

- For high-velocity tactical second-by-second anomaly displays, see [tactical-seconds.md](tactical-seconds.md).
- For uncompromised 10–45 minute technical deep-dive evaluations, see [analytical-deep-dive.md](analytical-deep-dive.md).
- For program manager schedule float and earned value details, see [../lenses/program-manager.md](../lenses/program-manager.md).
- For dual-layer review room architecture combining executive and evidentiary stages, see [../protocols/review-room-dual-layer.md](../protocols/review-room-dual-layer.md).
