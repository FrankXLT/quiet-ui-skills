# World 01 Distillation Blueprint: Clinical ICU & Phase III Trials

This blueprint documents the asymmetric translation of `01-clinical-icu-and-trials` from canonical truth (`corpus.json`) across three distinct clinical audiences, operational tempos, and delivery mediums while upholding the Quiet UI **Numerical Conservation Law**.

---

## 1. Presenter -> Audience Matrix

| View ID | Presenter | Target Audience | Lenses | Tempos | Mediums | Chromatic Budget | Nav Shells | Rigor | Bound Evidence Specs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `v01-icu-bedside-terminal` | ICU Informaticist | Bedside Nurse & Intensivist | Technician / Operator | `T1` (5-15 s) | `M4` (Walk-up POI Terminal) | Quiet Cockpit | `N0`, `N3` | `L3` | `v01_icu_ventilator_scalars.json`, `v01_icu_hemodynamic_scope.json` |
| `v02-trial-regulatory-brief` | Clinical Biostatistician | FDA Reviewer & Hospital CMO | Discipline Engineer, Program Manager | `T2` (1-3 min), `T3` (10-45 min) | `M1` (Archival Print), `M2` (Editorial Web) | Decision Contrast | `N1` | `L3` | `v02_trial_consort_forest.json`, `v02_trial_adverse_events_table.json` |
| `v03-patient-recovery-companion` | Clinical Care Team | Discharged Patient & Family | Consumer / Common Reader | `T3` (10-45 min) | `M3` (Stateful Web App) | Pedagogical Flow | `N2`, `N4` | `L1` | `v01_icu_ventilator_scalars.json` |

---

## 2. Scrubbed Bias Ledger

| View ID | Presenter Bias Identified | Risk to Target Audience | Scrubbed / Distilled Replacement |
| :--- | :--- | :--- | :--- |
| `v01-icu-bedside-terminal` | Raw HL7/ADC hex frames, rainbow-colored nominal vital tiles, and spline-interpolated flatline fills during motion artifact | Alarm fatigue under `T1` triage; clinicians mistake interpolated waveform for true perfusion | Quiet Cockpit monochrome nominal tiles; amber `[ CAUTION ]` reserved for `MAP = 63.5 mmHg < 65.0 mmHg`; explicit `2.4 s` `null` gap with `T_A`/`T_B` cursors |
| `v02-trial-regulatory-brief` | Cherry-picked p-value claims (`p < 0.01`) divorced from subgroup variance, missing control-arm incidence, and unbracketed adverse events | FDA reviewer / CMO cannot verify clinical net benefit or renal safety margins | Full `CONSORT` subgroup forest plot (`HR` + `95% CI` vs `1.0` null) paired with Booktabs safety ledger (`±` binomial uncertainty and DSMB status pills) |
| `v03-patient-recovery-companion` | Unexplained ICU acronyms (`PEEP`, `k=2`, `ADC counts`, `KDIGO`) and dense calibration certificates on primary screen | Patient/family anxiety and misinterpretation of discharge recovery targets | `L1` progressive disclosure showing 10-point trend sparklines, plain-language home targets (`SpO2 >= 92%`), and calm status pills without `L3` probe noise |

---

## 3. Four Universal Audience Evaluation Invariants Audit

| Invariant | `v01-icu-bedside-terminal` (`L3`) | `v02-trial-regulatory-brief` (`L3`) | `v03-patient-recovery-companion` (`L1`) |
| :--- | :--- | :--- | :--- |
| **1. Baseline & Corridor** | `MAP` anchored to `75.0 mmHg` target, `65.0 mmHg` caution floor, `55.0 mmHg` abort floor; `PEEP` anchored to `10.0 cmH2O` CMD vs `10.2 cmH2O` ACT | Forest plot anchored to `HR = 1.0` vertical null line; adverse event rows pair Protocol Arm against Control Arm (`11.4%` vs `14.8%` AKI) | `SpO2` (`94.2%`) and `MAP` (`63.5 mmHg`) anchored to home-monitoring lower bounds with clear sparkline trajectory |
| **2. Epistemic Provenance** | `k=2` `95.45%` expanded uncertainty (`± 1.5 mmHg`, `± 0.2 cmH2O`, `± 0.8%`), sensor/cal IDs, and un-interpolated `2.4 s` dropout break | `SAP-v2.4-ITT` (`n=1,240`) test-condition strip, exact `95% CI` whiskers, and `±` incidence uncertainties in Booktabs columns | Discrete 10-sample trend sparkline derived identically from `v01_icu_ventilator_scalars.json` without synthetic smoothing |
| **3. Margin & Consequence** | Explicit `-2.3%` margin excursion on `MAP`, `+95.0%` margin on `PEEP`, and `+55.0%` margin on `SpO2` computed without mental math | Subgroups crossing null (`Age >= 65 CI [0.62, 1.01]`) rendered in muted secondary ink vs statistically decisive `SOFA >= 8` (`[0.52, 0.89]`) | Explicit recovery gap framing showing how close oxygen saturation remains above the `92%` clinic-call threshold |
| **4. Actionable Disposition** | Verify arterial transducer zeroing post-dropout before titrating vasopressors | Authorize protocol for `SOFA >= 8` / `Lactate > 2 mmol/L` with mandatory KDIGO renal monitoring | Continue home pulse-oximetry log; call triage nurse if `SpO2 < 92%` or systolic/MAP drops persistently |

---

## 4. Adversarial Murder-Board Red-Team Audit

| Rubric / Persona | Audited View(s) | Hard-Block Criterion Checked | Audit Finding | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Clinical Safety (`CL-1`)** | `v02` | `CONSORT` cohort counts (`n`) paired with `95% CI`, never bare p-values | All 4 subgroups state exact `n` (`1,240`, `612`, `486`, `704`) and `95% CI` whiskers against `HR = 1.0` | `PASS` |
| **Clinical Safety (`CL-2 / CL-3`)** | `v01` | Unambiguous concentration/pressure units and alarm-fatigue suppression | `cmH2O`, `mmHg`, `%` isolated in `.qe-unit` headers; only `MAP` (`63.5 <= 65.0`) triggers `[ CAUTION ]` | `PASS` |
| **Chief Engineer (`CR-2 / CR-5`)** | `v01`, `v02` | Zero Bezier interpolation across dropouts; NIST/ISO calibration traceability | `v01` scope breaks SVG `<path>` cleanly with `M` across `6.4 s` to `8.8 s` (`2.4 s`); all 3 scalars cite `CAL-*` IDs | `PASS` |
| **Field Operator (`TR-2 / TR-3`)** | `v01` | Nominal vs lower/upper thresholds in identical SI units; `CMD vs ACT` marker | `PEEP` renders `CMD 10.0` vs `ACT 10.2 cmH2O` on linear horizontal gauge without radial dial clutter | `PASS` |
| **First-Time Learner (`LR-3`)** | `v03` | Acronym de-barnacling and cognitive speed limit in consumer companion | `L1` compilation hides `raw_adc_counts`, `k=2`, and `calibration_id` while retaining conserved scalar truth | `PASS` |

---

## 5. Canonical Numerical Conservation Ledger

Every `value` in `corpus.json` (`canonical_metrics`) is conserved identically across its bound `evidence/*.json` specs and all distilled views:

| `metric_id` | Canonical Value | Unit | `corpus.json` Key | Bound Evidence File(s) | Views Consuming |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `map_mmhg` | `63.5` (± `1.5`, target `75.0`, lower `65.0`) | `mmHg` | `canonical_metrics.map_mmhg.value` | `evidence/v01_icu_ventilator_scalars.json`, `evidence/v01_icu_hemodynamic_scope.json` | `v01`, `v03` |
| `peep_cmd_cmh2o` | `10.0` | `cmH2O` | `canonical_metrics.peep_cmd_cmh2o.value` | `evidence/v01_icu_ventilator_scalars.json` | `v01`, `v03` |
| `peep_act_cmh2o` | `10.2` (± `0.2`) | `cmH2O` | `canonical_metrics.peep_act_cmh2o.value` | `evidence/v01_icu_ventilator_scalars.json` | `v01`, `v03` |
| `spo2_pct` | `94.2` (± `0.8`, lower `92.0`) | `%` | `canonical_metrics.spo2_pct.value` | `evidence/v01_icu_ventilator_scalars.json`, `evidence/v01_icu_hemodynamic_scope.json` | `v01`, `v03` |
| `dropout_duration_s` | `2.4` (`T_A=6.4 s`, `T_B=8.8 s`) | `s` | `canonical_metrics.dropout_duration_s.value` | `evidence/v01_icu_hemodynamic_scope.json` | `v01` |
| `overall_hr` | `0.74` (`[0.61, 0.90]`) | `1` | `canonical_metrics.overall_hr.value` | `evidence/v02_trial_consort_forest.json`, `evidence/v02_trial_adverse_events_table.json` | `v02` |
| `age_ge65_hr` | `0.79` (`[0.62, 1.01]`) | `1` | `canonical_metrics.age_ge65_hr.value` | `evidence/v02_trial_consort_forest.json` | `v02` |
| `sofa_ge8_hr` | `0.68` (`[0.52, 0.89]`) | `1` | `canonical_metrics.sofa_ge8_hr.value` | `evidence/v02_trial_consort_forest.json` | `v02` |
| `lactate_gt2_hr` | `0.71` (`[0.54, 0.93]`) | `1` | `canonical_metrics.lactate_gt2_hr.value` | `evidence/v02_trial_consort_forest.json` | `v02` |
| `aki_rate_pct` | `11.4` (± `1.8`, control `14.8`) | `%` | `canonical_metrics.aki_rate_pct.value` | `evidence/v02_trial_adverse_events_table.json` | `v02` |
