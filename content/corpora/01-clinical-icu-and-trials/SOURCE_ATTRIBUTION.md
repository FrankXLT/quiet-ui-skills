# Clinical ICU & Phase III Trial Synthetic Corpus Attribution (`World 01`)

All clinical waveforms, ventilator setpoints, hemodynamic thresholds, and Phase III trial subgroup statistics in `01-clinical-icu-and-trials` are **fully synthetic reference datasets** authored strictly for Quiet UI human-factors, metrology, and multi-audience translation verification.

> **De-Identification & Non-Endorsement Notice (`45 CFR § 164.514`):** Zero real patient records, Protected Health Information (PHI), Personally Identifiable Information (PII), hospital identifiers, or proprietary device firmware traces appear anywhere in this corpus. All device IDs (`ICU-BED-04`, `ART-LINE-04A`, `TRIAL-SEPSIS-2026-P3`) are synthetic placeholders.

## 1. Clinical Engineering & Human-Factors Standards

| Standard / Guideline | Target Views | Scope Applied in World 01 | Disposition |
| :--- | :--- | :--- | :--- |
| **FDA IEC 62366-1:2015** | `v01`, `v03` | Non-color-only alarm annunciation (`[ CAUTION ]`, `[ NOMINAL ]`), use-error mitigation, and Quiet Cockpit monochrome nominal discipline | `PUBLIC_STANDARD_REF` |
| **Surviving Sepsis Campaign (2021)** | `v01`, `v03` | Resuscitation baseline corridor anchoring Mean Arterial Pressure (`MAP >= 65.0 mmHg`, target `75.0 mmHg`) | `CLINICAL_GUIDELINE_REF` |
| **ISO 80601-2-12:2020 & ISO 80601-2-61:2017** | `v01` | Critical-care ventilator PEEP commanded-vs-actual tolerances (`cmH2O`) and pulse oximetry (`SpO2 / %`) calibration provenance | `PUBLIC_STANDARD_REF` |
| **CONSORT 2010 / 2025 Statement** | `v02` | Intention-to-treat (`n=1,240`) subgroup 95% confidence interval forest plots (`HR` vs null `1.0`) and structured harms reporting | `OPEN_REPORTING_STD` |
| **KDIGO 2012 AKI Guideline** | `v02` | Standardized Stage >= 2 Acute Kidney Injury endpoint definition (`11.4% ± 1.8%` vs `14.8%` control) | `CLINICAL_GUIDELINE_REF` |
| **NIST SP 811** | `v01`, `v02` | Quantity calculus column headers (`MAP / mmHg`, `PEEP / cmH2O`, `SpO2 / %`) and `k=2` expanded uncertainty brackets | `GOV_PUBLIC_USE_PERMITTED` |

## 2. Structural Signal Conventions

- **Physiological Waveform Geometry**: Multi-channel arterial pressure (`P_art / mmHg`), photoplethysmography (`SpO2_pleth / %`), and capnography (`P_etCO2 / mmHg`) traces follow open critical-care monitoring conventions (such as PhysioNet/MIMIC signal taxonomy) using mathematically generated synthetic time-series samples rather than clinical recordings.
- **Dropout & Artifact Handling**: The `2.4 s` `null` discontinuity (`t = 6.4 s` to `8.8 s`) models an arterial line transducer motion artifact where interpolation across missing telemetry is strictly prohibited.
