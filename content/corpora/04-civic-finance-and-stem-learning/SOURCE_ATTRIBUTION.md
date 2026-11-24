# World 04 Source Attribution: Civic Finance & STEM Learning (`Quiet UI v9.0`)

All municipal capital accounting conventions, treasury liquidity stress-test frameworks,
and physics laboratory metrology practices across World 04 (`04-civic-finance-and-stem-learning`)
derive from public-domain United States Government standards (`17 U.S.C. § 105`),
federal statistical series, and open engineering pedagogy specifications.

> **Non-Endorsement & Synthetic Corpus Notice:** Numerical capital line items
> (`48.0 M USD` opening reserve, `28.4 M USD` School HVAC, `31.2 M USD` Water Main,
> `26.9 M USD` closing contingency), `+250 bps` Monte Carlo liquidity trajectories,
> and `RC` bench discharge samples (`V_0 = 5.00 V`, `tau = 2.40 s`) are synthetic
> benchmark scenarios constructed strictly against the public methodologies cited below.
> No real municipality, issuer, student, or private entity is represented.

---

## 1. Authoritative Standards & Methodological Corpus

| Standard / Reference ID | Target Views | Domain Scope & Methodology | Disposition |
| :--- | :--- | :--- | :--- |
| **GAO Green Book (`GAO-14-704G`)** | `v10`, `v11` | *Standards for Internal Control in the Federal Government*: fund segregation, obligation audit lineage, and reserve floor accountability | `GOV_PUBLIC_DOMAIN` |
| **USWDS Design System (`v3.x`)** | `v10` | *U.S. Web Design System*: plain-language public financial disclosure, accessible table semantics, and non-color-only status indicators | `GOV_PUBLIC_DOMAIN` |
| **GASB Statement No. 54** | `v10` | Fund balance reporting and governmental fund type definitions (unobligated base, restricted grants, debt proceeds, contingency floor) | `PUBLIC_ACCOUNTING_STD` |
| **FRED Economic Data (`CPIAUCSL` / `DGS10`)** | `v10`, `v11` | Federal Reserve Bank of St. Louis CPI-U inflation deflator baseline and 10-Year Treasury yield shock (`+250 bps`) reference curve | `PUBLIC_STATISTICAL_SERIES` |
| **SEC Form 10-Q / Liquidity Rule (`17 CFR § 270.22e-4`)** | `v11` | Quarterly liquidity risk stress-testing, duration-convexity shock accounting, and minimum `20.0%` highly liquid asset floor | `GOV_REGULATORY_STD` |
| **NIST SP 811 (`2008 Ed.`)** | `v10`, `v11`, `v12` | *Guide for the Use of the International System of Units (SI)*: quantity calculus headers (`V_c / V`, `t / s`) and uncertainty notation | `GOV_PUBLIC_DOMAIN` |
| **NAVAIR FTM-108** | `v11`, `v12` | Fixed-point `1-2-5` linear scale intervals for distortion-free manual interpolation across screen (`M2`/`M3`) and print (`M1`) | `GOV_PUBLIC_DOMAIN` |
| **GUM (`JCGM 100:2008`)** | `v12` | *Evaluation of Measurement Data*: Type A/B repeatability uncertainty whiskers (`±u_y`) and normalized residual diagnostics | `OPEN_METROLOGY_STD` |

---

## 2. View-to-Source Traceability Matrix

### 2.1 View `v10-civic-capital-budget-deck` (Civic Capital Board & Public Oversight)
- **Primary Evidence Specs**:
  - `evidence/v10_civic_capital_waterfall.json` (`urn:quiet-ui:schema:v9:plot`, `waterfall`, `L2`)
  - `evidence/v10_civic_budget_table.json` (`urn:quiet-ui:schema:v9:table`, `L2`)
- **Methodology Basis**:
  - Waterfall cash-flow conservation reconciles opening balance (`48.0 M USD`) plus grant (`+16.5 M USD`) and bond (`+22.0 M USD`) inflows against School HVAC (`-28.4 M USD`) and Water Main (`-31.2 M USD`) capital outlays, leaving `26.9 M USD` closing contingency (`179.3%` coverage of the `15.0 M USD` statutory reserve floor).
  - Plain-language citizen framing follows **USWDS** readability standards while preserving exact **GAO** ledger classifications and **FRED** materials-escalation risk notes on the Water Main line item (`REVIEW`).

### 2.2 View `v11-treasury-stress-test-solver` (Treasury & Investment Committee)
- **Primary Evidence Spec**:
  - `evidence/v11_treasury_drawdown_plot.json` (`urn:quiet-ui:schema:v9:plot`, `cartesian`, `L3`)
- **Methodology Basis**:
  - Evaluates an 8-quarter portfolio liquidity coverage trajectory under an instantaneous `+250 bps` parallel yield-curve shock (`FRED DGS10` methodology) against a `20.0%` minimum regulatory liquidity floor (`direction: "lower"`).
  - Compares `n = 10,000` Monte Carlo path medians (`±u_y` interquartile dispersion whiskers) against a deterministic duration-convexity decay equation (`36.5 - 12.0 * (1.0 - exp(-0.35 * (x - 1.0)))`), preserving epistemic separation and bottom normalized residual telemetry.

### 2.3 View `v12-stem-interactive-lab` (Undergraduate Physics / Circuits Lab)
- **Primary Evidence Spec**:
  - `evidence/v12_stem_rc_cooling_lab.json` (`urn:quiet-ui:schema:v9:plot`, `cartesian`, `L3`)
- **Methodology Basis**:
  - Models first-order RC capacitor discharge (`V(t) = V_0 * exp(-t / tau)` with `V_0 = 5.00 V` and `tau = 2.40 s`) using **Pedagogical Flow** semantic term tokens (`tx` for `V_0`, `path_loss` for `exp(-t / tau)`).
  - Discrete student oscilloscope captures (`f_s = 1.00 kHz`, `T_amb = 22.4 ± 0.2 °C`, `±u_y` probe uncertainty) are plotted strictly as scatter glyphs with uncertainty whiskers and a synchronized bottom residual strip per **NIST SP 811** and **JCGM 100:2008**.

### 2.4 View `v22-reading-and-mobility-brief` (Public Data & Research Storytelling)
- **Primary Evidence Specs**:
  - `evidence/v22_reading_hex_map.json` (`urn:quiet-ui:schema:v9:plot`, `us_hex_tile_map`, `L1`)
  - `evidence/v22_reading_arrow_dumbbell.json` (`urn:quiet-ui:schema:v9:plot`, `arrow_dumbbell`, `L2`)
  - `evidence/v22_mobility_matrix.json` (`urn:quiet-ui:schema:v9:table`, `diverging_matrix`, `L2`)
- **Methodology Basis**:
  - Grounded in public-domain US Department of Education NAEP Grade 4 Reading benchmarks and US Census Bureau ACS 1-Year household income / intergenerational mobility baseline comparisons (`17 U.S.C. § 105`).
  - Enforces Takeaway Figure Card ergonomics (`[Chart | Table]` toggle, `Copy data`, `Copy for AI`), equal-chance `20.0%` baseline disclosure, and dual-physics Web Brief / Slide Deck / Print Sheet alignment.

---

## 3. Clean-Room & Licensing Compliance

1. **Zero PII & Zero Proprietary Telemetry**: All account IDs (`TREASURY-POOL-04`), bench rigs (`RC-BENCH-RIG-04`), and capital program labels are synthetic clean-room identifiers.
2. **Permissive Attribution**: Published under the repository's Apache-2.0 license with full public-domain attribution to GAO, USWDS, NAEP, US Census Bureau, NIST, NAVAIR, and SEC methodological standards.

