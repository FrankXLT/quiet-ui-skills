# Operational Decision Tempo: Analytical Deep Dive (10–45 Minutes)

This guide defines the layout architecture, evidentiary density standards, and peer-review protocols required for analytical deep-dive sessions (10 to 45 minutes), including Preliminary/Critical Design Reviews (PDR/CDR), failure review boards, and forensic metrology investigations.

---

## 1. Operating Tempo & Review Rigor

| Dimension | Analytical Investigation Specification |
| :--- | :--- |
| **Review Window** | 10 to 45 minutes per subsystem, cohort, service, or fiscal audit |
| **Operational Modes** | Preliminary/Critical Design Review (PDR/CDR), Failure Review Board (FRB), `CONSORT` / `FDA IEC 62366` Clinical Safety Root-Cause, `OpenTelemetry` / `NIST AI RMF 100-1` Postmortem, `NIST/SEMATECH SPC` Capability & `NRC NUREG-0700` Audit, `GAO` / `FRED/SEC` Fiscal Variance Audit |
| **Cognitive Framework** | Uncompromising evidentiary scrutiny; forensic examination of mathematical assumptions, raw data distributions, and error propagation |
| **Information Density** | High-density `L3 · Physical, Clinical & Metrological` proof; complete parameter matrices, governing models, raw scatter/CI plots, and residual plots |
| **Interaction Standard** | Synchronized cross-probing between equations, tables, and time-series plots; persistent metadata inspectability |

In an analytical deep dive, summarization is viewed as a liability. Reviewers (discipline specialists, clinical biostatisticians, principal SREs, SPC quality leads, and `GAO` auditors) actively seek out the rawest available layer of truth. The presentation must expose every link in the evidentiary chain: from the physical transducer, clinical case report, `OpenTelemetry` span, `Modbus` register, or `SEC` filing down to filtering, calibration corrections, and final statistical models.

---

## 2. Evidentiary Standards for Layer 3 (`L3`) Proof

An analytical deep-dive presentation must meet four unbending evidentiary standards:

1. **Complete Mathematical Articulation**: Every model must be accompanied by its governing differential, statistical, or accounting equation, explicitly defining all variables, bounds, and sample sizes ($n$).
2. **Synchronized Residual & Confidence Channels**: Scatter plots and fitted curves must feature an aligned residual deviation sub-panel immediately below, displaying $(y_{\text{data}} - y_{\text{model}})$ against $\pm 3\sigma$ or 95% confidence bounds.
3. **Data Provenance & Cryptographic Traceability**: Every figure and data table must feature a provenance block containing:
   - Data collection timestamp (UTC) and duration.
   - Test facility / clinical site / VPC region / plant line / fiscal ledger reference.
   - Instrument serial numbers and `NIST` cal certs, `OpenTelemetry` trace IDs, `Modbus` tag revision, or `FRED/SEC` series IDs.
   - Raw data repository URL, commit hash, and dataset SHA-256 digest.
4. **Error Budget Decomposition Trees**: Total measurement or model uncertainty must be broken down into systematic (bias) and random components, tracing error propagation using Root-Sum-Square (RSS) or heteroskedastic variance math.

### 2.1 Cross-Domain L3 Evidentiary Equivalents

| Domain | Governing Model & Scatter | Residual / Provenance Anchor |
| :--- | :--- | :--- |
| **Clinical Safety / ICU (`FDA IEC 62366`, `CONSORT`)** | Kaplan-Meier survival & Cox hazard model with `CONSORT` attrition counts ($N$). | 95% CI funnel residuals; IRB protocol rev + `FDA IEC 62366` use-error trace log. |
| **SRE / Cloud / AI Ops (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`)** | HDR tail-latency distribution ($p50/p95/p99$) & ECE calibration reliability curve. | Span-level waterfall residuals; OTel `traceparent` + `NIST SP 800-207` PEP policy hash. |
| **Industrial Plant / SCADA (`NIST/SEMATECH SPC C_pk`, `ISA-101`, `NRC NUREG-0700`, `Modbus`)** | Shewhart $\bar{X}/R$ control chart with `UCL/CL/LCL` and $C_{pk}$ capability index. | Subgroup variance ($n=5$); `Modbus` register poll digest + `NIST` gauge cert ID. |
| **Civic Capital / Treasury (`GAO`, `FRED/SEC`)** | Real cash-flow & DSCR stress model deflated by `FRED` CPI-U series. | Forecast-vs-actual variance bars; `SEC` 10-Q / `GAO` Green Book SHA-256 ledger digest. |

---

## 3. Dual-Column Structured Layout Architecture

To accommodate deep technical reading alongside active data exploration, analytical layouts employ a structured two-column grid with a sticky navigation spine:

```
+----------------------------------------------------------------------------------------------------------------------+
| DEEP DIVE INVESTIGATION: OPTICAL MODULATOR JITTER ANOMALY [FRB-2026-081]                    | 2026-11-16 19:45 UTC   |
+----------------------------------------------------------------------------------------------------------------------+
| [NAV SPINE: 220px] | [PRIMARY ANALYTICAL STAGE: 860px]                       | [METROLOGY INSPECTOR: 320px]          |
| 1. Executive BLUF  | 3.1 GOVERNING JITTER DECOMPOSITION MODEL                | DATA PROVENANCE BLOCK                 |
| 2. Timeline & Logs | Total jitter (TJ) modeled via dual-Dirac model:         | Facility: Optical Test Bay 3          |
| 3. Jitter Model    |   TJ(BER) = DJ_delta-delta + 2 * Q(BER) * RJ_rms        | Chamber: Thermal Vac T-02             |
| 4. Allan Deviation | Where Q(10^-12) = 7.034. Random jitter (RJ) originates  | Pressure: 2.1e-6 Torr                 |
| 5. Residuals       | from laser phase noise; deterministic jitter (DJ) is    | Baseplate: 24.8 +/- 0.1 C             |
| 6. Corrective Act  | driven by 125 MHz switching power supply ripple.        | Instrument: Agilent DCA-X 86100D      |
|                    |                                                         | Serial: US48102914 (Cal Exp: Dec 26)  |
|                    | 3.2 TIME-DOMAIN EYE DIAGRAM & HISTOGRAM RECONCILIATION  | Git Hash: payload/sim@8f419b          |
|                    | [ HIGH DENSITY PERSISTENCE PLOT: 100,000 WAVEFORMS ]    | Dataset Hash: SHA-256 9a4c8...        |
|                    | +-----------------------------------------------------+ |                                       |
|                    | | Eye Opening: 84.2 ps | Jitter P-P: 18.4 ps          | | COMPONENT ALLOCATION MATRIX           |
|                    | | Crossing: 49.8%      | SNR: 14.8 dB                 | | Parameter | Alloc   | Meas  | Margin| |
|                    | +-----------------------------------------------------+ | |-----------+---------+-------+-------| |
|                    |                                                         | | TJ (ps)   | <= 25.0 | 18.4  | +6.6  | |
|                    | 3.3 RESIDUAL FIT DEVIATION                              | | RJ (ps)   | <= 1.20 | 0.88  | +0.32 | |
|                    | +0.4 ps +--*--*-----*---*-----*---*-------------------+ | | DJ (ps)   | <= 8.00 | 6.10  | +1.90 | |
|                    |  0.0 ps +---------------------------------------------+ | | Ext Ratio | >= 8.5  | 10.2  | +1.7dB| |
|                    | -0.4 ps +----*---*--------*-----*---*-----------------+ |                                       |
|                    | R^2 = 0.99984 | Chi-Square Reduced = 1.04               | [ DOWNLOAD RAW METROLOGY HDF5 (14MB) ]|
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Root-Sum-Square (RSS) Error Budget Decomposition

Analytical reviews require mathematical proof of total system uncertainty. The following structured table provides the canonical RSS error budget format:

| Error Source / Transducer Stage | Error Type | Distribution Model | Sensitivity ($\partial y / \partial x_i$) | Standard Uncertainty ($u_i$) | Variance Contribution ($u_i^2$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ADC Quantization Noise** | Systematic | Uniform ($1/\sqrt{12}$) | $1.00\text{ V/V}$ | $0.288\text{ mV}$ | $0.083\text{ mV}^2$ |
| **Transimpedance Amplifier Thermal Drift** | Random | Normal ($\pm 1\sigma$) | $1.42\text{ V/K}$ | $0.340\text{ mV}$ | $0.116\text{ mV}^2$ |
| **Optical Attenuator Insertion Repeatability** | Systematic | Triangular ($1/\sqrt{6}$) | $0.85\text{ V/dB}$ | $0.412\text{ mV}$ | $0.170\text{ mV}^2$ |
| **Environmental Temperature Ripple** | Random | Normal ($\pm 1\sigma$) | $0.22\text{ V/K}$ | $0.180\text{ mV}$ | $0.032\text{ mV}^2$ |
| **TOTAL COMBINED UNCERTAINTY ($u_c$)** | **RSS** | **Normal ($k=2$, 95% CI)** | **Root-Sum-Square** | **$0.633\text{ mV}$** | **Expanded: $\pm 1.27\text{ mV}$** |

---

## 5. Synced Cross-Probing & Parameter Inspection

Analytical environments must support real-time mathematical cross-probing. When a reviewer hovers over or selects a mathematical symbol in the governing equation (e.g., $RJ_{\text{rms}}$), the interface simultaneously:
1. Highlights the corresponding parameter row in the metrology table.
2. Draws the confidence interval boundary on the time-series distribution plot.
3. Reveals the instrument calibration certificate and measurement formula in the side inspector.

This removes cognitive translation delays and allows instant verification of analytical continuity.

---

## 6. Analytical Deep-Dive Evidentiary Schema

Every analytical finding presented during a deep-dive review is backed by a structured evidentiary record:

```json
{
  "investigation_id": "FRB-2026-081",
  "review_title": "Optical Modulator Jitter Anomaly Root Cause",
  "author_fellow": "Principal Metrology Specialist",
  "governing_model": {
    "equation_latex": "TJ(\\text{BER}) = DJ_{\\delta\\delta} + 2 Q(\\text{BER}) \\cdot RJ_{\\text{rms}}",
    "parameters": {
      "TJ": {"value": 18.4, "unit": "ps", "spec_limit": 25.0, "margin": 6.6},
      "DJ": {"value": 6.10, "unit": "ps", "spec_limit": 8.0, "margin": 1.9},
      "RJ": {"value": 0.88, "unit": "ps_rms", "spec_limit": 1.2, "margin": 0.32}
    },
    "residual_reduced_chi_square": 1.04
  },
  "provenance": {
    "test_facility": "Optical Metrology Lab Bay 3",
    "chamber_id": "TVAC-02",
    "calibrated_standard_id": "NIST-OPT-4410",
    "dataset_sha256": "9a4c8f18e47b31d99b28f731aa881029c3f9104b99824c62b53e81039da58f14",
    "git_commit": "payload/metrology@8f419b7"
  }
}
```

---

## 7. Forensic Root-Cause Corrective Action (RCCA) Sequence

When investigating an anomaly, the analytical view guides the peer board through five sequential diagnostic milestones:

```
[TELEMETRY ANOMALY IDENTIFIED]
             |
             v
[PHASE 1: PROVENANCE FREEZE & DATA VALIDATION]
- Check NIST calibration certificates and sensor timestamps.
- Verify environmental conditions remained within chamber spec.
             |
             v
[PHASE 2: EMPIRICAL DISPERSION AUDIT]
- Overlay measured raw scatter over governing theoretical equations.
- Inspect residual plot for unmodeled non-linear systematic drift.
             |
             v
[PHASE 3: RSS ERROR TREE RECONCILIATION]
- Calculate expanded uncertainty (k=2, 95% CI).
- Confirm observed deviation exceeds combined measurement uncertainty.
             |
             v
[PHASE 4: ISOLATION TO HARDWARE / FIRMWARE FAULT]
- Correlate spectral peaks with known hardware oscillators.
- Re-run HIL automated test script on identical engineering unit.
             |
             v
[PHASE 5: ROOT CAUSE BASELINE & PEER SIGN-OFF]
- Baseline corrective action in formal engineering change order.
- Archive raw HDF5 dataset with signed SHA-256 commit hash.
```

---

## 8. Analytical Deep-Dive Peer Review Rubric

Before submitting any documentation or interactive display to a formal PDR, CDR, or Failure Review Board, verify compliance against these seven rigorous criteria:

1. **Governing Equation Articulation**: Is every theoretical model, regression curve, or simulation accompanied by its complete LaTeX mathematical formulation?
2. **Residual Plot Coupling**: Does every non-linear fit or calibration curve include a synchronized residual plot showing variance against $3\sigma$ bounds?
3. **Data Provenance Block**: Is every plot grounded with test bay IDs, environmental conditions, instrument serial numbers, and calibration dates?
4. **Direct Raw Data Traceability**: Is a direct link or hash provided enabling reviewers to inspect or download the raw, un-decimated data points?
5. **Conserved Unit Hierarchy**: Are all measurements reported in rigorous SI or standard discipline units without arbitrary normalized scaling?
6. **Error Budget Root-Sum-Square (RSS)**: Is total measurement uncertainty broken down into systematic instrument bias and random dispersion?
7. **Cross-Probing Continuity**: Does the document or interface clearly link equation variables directly to physical table rows and chart glyphs?

---

## 9. Cross-Reference Links

- For high-speed tactical alarm triage (5–15 sec), see [tactical-seconds.md](tactical-seconds.md).
- For executive minute-by-minute gate compression (1–3 min), see [executive-minutes.md](executive-minutes.md).
- For discipline specialist equations and metrology norms, see [../lenses/discipline-engineer.md](../lenses/discipline-engineer.md).
- For formal adversarial review room procedures, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).
