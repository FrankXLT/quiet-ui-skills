# NIST SP 811 Metrology & Physical Unit Calculus

In Quiet UI Pillar 2, all quantitative values, scales, and readouts are governed by the rigorous dimensional principles of **NIST Special Publication 811** (*Guide for the Use of the International System of Units*) and the International Bureau of Weights and Measures (BIPM) SI brochure.

Quantitative visuals must communicate physical reality without ambiguity. A raw number without an explicit unit is metrologically invalid.

---

## 1. NIST SP 811 Quantity Calculus

Quantity calculus treats physical quantities as the mathematical product of a numerical value $\{A\}$ and a measurement unit $[A]$:

$$A = \{A\} \cdot [A]$$

Therefore, when labelling axis coordinates, table headers, and readout labels, divide the physical quantity symbol by the measurement unit to isolate the pure dimensionless numeral:

### Permitted Header Formats

1. **Pure Quotient Form (Preferred for Axis Lines & Graticules)**:
   - `f / GHz` (Frequency in gigahertz)
   - `t / ps` (Time in picoseconds)
   - `P / dBm` (Power referenced to one milliwatt)
   - `T / K` (Absolute thermodynamic temperature in kelvins)
   - `\sigma_y(\tau)` (Dimensionless fractional frequency deviation)

2. **Parenthetical Parameter Form (Permitted for Tables & Parametric Blocks)**:
   - `Frequency (GHz)`
   - `Elapsed Time (ms)`
   - `Supply Voltage (V)`
   - `Noise Spectral Density (dBc/Hz)`

### Strictly Forbidden Notations
- **Square brackets for units**: `f [GHz]` is non-standard under BIPM/NIST SP 811 (square brackets denote the dimension or unit function itself: $[f] = \text{Hz}$).
- **Compound slash ambiguities**: `W/m/K` or `J/kg/K`. Always use negative exponents or parentheses: `W/(m·K)` or `W·m⁻¹·K⁻¹`.
- **Bare numbers without reference**: Ticks displaying `0.0000000000814` without prefix scaling.
- **Unit abbreviations in variable subscripts**: Do not write $V_{\text{AC}}$ or $P_{\text{Watts}}$; write $V_{\text{alt}}$ with unit $\text{V}$, or $P$ with unit $\text{W}$.

---

## 2. SI Prefix Engineering Scaling Law ($0.1 \le \text{Tick} \le 999$)

To eliminate unreadable floating-point exponents and trailing zero runs, visual builders must scale data axes so major tick labels stay within the human-parseable range **$0.1 \le \{A\} \le 999$**.

| Multiplier | Prefix | Symbol | Exemplar Raw Value | Calibrated Presentation |
| :--- | :--- | :--- | :--- | :--- |
| $10^{-15}$ | femto | f | $4.2 \times 10^{-14}\ \text{s}$ | `42.0 fs` |
| $10^{-12}$ | pico | p | $8.14 \times 10^{-11}\ \text{s}$ | `81.4 ps` |
| $10^{-9}$ | nano | n | $3.5 \times 10^{-7}\ \text{s}$ | `350 ns` |
| $10^{-6}$ | micro | $\mu$ | $2.5 \times 10^{-5}\ \text{m}$ | `25.0 µm` |
| $10^{-3}$ | milli | m | $4.8 \times 10^{-2}\ \text{A}$ | `48.0 mA` |
| $10^{0}$ | (none) | — | $1.25\ \text{V}$ | `1.25 V` |
| $10^{3}$ | kilo | k | $4.75 \times 10^{4}\ \Omega$ | `47.5 kΩ` |
| $10^{6}$ | mega | M | $1.42 \times 10^{7}\ \text{Hz}$ | `14.2 MHz` |
| $10^{9}$ | giga | G | $9.8 \times 10^{9}\ \text{Hz}$ | `9.80 GHz` |
| $10^{12}$ | tera | T | $1.5 \times 10^{12}\ \text{bits/s}$ | `1.50 Tbps` |

> [!IMPORTANT]
> **Prefix Boundary Hysteresis**: In dynamically streaming telemetry, axis scales must not flicker between prefixes across consecutive frames. Hysteresis requires the signal to cross $1050$ or $0.095$ for 3 consecutive buffer updates before switching prefix regimes.

---

## 3. Typographical Grammar & Glyph Rules

High-fidelity metrological rendering enforces ISO 80000-1 typographical distinctions:

### A. Italic Physical Quantities vs. Upright Roman Units
- **Physical Variables & Parameters**: Must be rendered in *slanted italics* ($f$, $t$, $V$, $I$, $p$, $T$, $\tau$, $\sigma$).
- **Units of Measure**: Must be rendered in upright **Roman** (`s`, `ps`, `Hz`, `GHz`, `dBm`, `K`, `V`, `A`, `Ω`, `rad/s`).
- **Mathematical Constants & Operators**: Must be rendered upright (`d` in differential $\mathrm{d}x$, `e` for base of natural logs, $\mathrm{i}$ or $\mathrm{j}$ for imaginary unit, $\pi$).

### B. Subscript Conventions
- **Variable index**: Rendered in italics (e.g., $V_i$, $C_k$, $x_n$).
- **Descriptive qualifier or label**: Rendered upright Roman (e.g., $V_{\mathrm{ref}}$, $T_{\mathrm{amb}}$, $P_{\mathrm{peak}}$, $f_{\mathrm{sampling}}$).

### C. Mandatory Non-Breaking Space
A non-breaking space (`&nbsp;` or Unicode `U+00A0`) must separate the numerical value from the unit symbol:
- Correct: `81.4&nbsp;ps`, `50&nbsp;Ω`, `24.0&nbsp;V`, `100&nbsp;kHz`
- Incorrect: `81.4ps` (no space), `50 Ω` (breaking regular space allowing line wrap)
- *Single Exception*: The superscripts for plane angular degrees, minutes, and seconds do not take a space (e.g., `45°`, `30′`, `15″`), but temperature in degrees Celsius requires a space: `21.5&nbsp;°C`.

---

## 4. Significant Figures & Uncertainty Consistency

In accordance with JCGM 100:2008 (*Evaluation of measurement data — Guide to the expression of uncertainty in measurement* / GUM):

1. **Resolution Matching**: The numerical value and its expanded uncertainty $U$ must terminate at the same decimal place.
   - Correct: `(10.042 ± 0.003) MHz`
   - Incorrect: `10.04239 ± 0.05 MHz` (excess precision in nominal value)
   - Incorrect: `10.04 ± 0.003 MHz` (missing resolution in nominal value)
2. **Uncertainty Significant Figures**: Expanded uncertainties should be stated to at most two significant figures (e.g., `±0.045 mV` or `±12 ps`).
3. **Coverage Factor Declaration**: Always declare the coverage factor $k$ (e.g., $k=2$ for an approximate $95\%$ confidence level under Gaussian assumptions).

---

## 5. Parametric Legend Blocks & Data Schema

Every quantitative plot, table, or waveform must embed a parameter metadata block specifying physical constants, operational conditions, and units.

```json
{
  "metrology": {
    "system": "SI",
    "standard": "NIST SP 811",
    "parameters": [
      {
        "symbol": "f_RF",
        "description": "RF Carrier Center Frequency",
        "nominal_value": 9.800000000,
        "display_value": "9.800",
        "display_unit": "GHz",
        "uncertainty": "±0.002",
        "coverage_factor": 2,
        "confidence_pct": 95.45
      },
      {
        "symbol": "P_in",
        "description": "Incident Drive Power",
        "nominal_value": 14.2,
        "display_value": "14.2",
        "display_unit": "dBm",
        "uncertainty": "±0.1",
        "coverage_factor": 2,
        "confidence_pct": 95.0
      },
      {
        "symbol": "T_amb",
        "description": "Chamber Ambient Temperature",
        "nominal_value": 296.15,
        "display_value": "23.0",
        "display_unit": "°C",
        "uncertainty": "±0.2",
        "coverage_factor": 2,
        "confidence_pct": 95.0
      }
    ]
  }
}
```

---

## 6. Metrological Checklist & Pre-Flight Invariants

Before releasing any Pillar 2 chart, matrix, or readout, audit these four invariants:

- [ ] **Quotient or Parenthetical Header**: All axes, table columns, and gauge displays carry explicit physical units via `Quantity / Unit` or `Quantity (Unit)`.
- [ ] **Magnitude Scaling**: Tick numbers fall within $[0.1, 999]$; prefixes are scaled to engineering increments ($10^{\pm 3n}$).
- [ ] **Typography Separation**: Variables are in italics; units, numerals, and descriptive qualifiers are in upright Roman.
- [ ] **Space Placement**: Every unit symbol is preceded by a non-breaking space `&nbsp;`.

---

## 7. Cross-Plot Domain & Pixel Spine Registration

When two or more quantitative plots are co-displayed or switched across peer cohort views:

1. **Shared X-Axis Canonical Time Grid**: Bind sibling plots covering the same time window to one zero-filled `[t_min, t_max]` bucket array (`QuietSvgLayout.buildCanonicalTimeGrid`), identical tick step, and column-locked inner `[x_left, x_right]` frame pixels so vertical comparisons never drift when a sparse series drops empty buckets.
2. **Unit-Locked `[0, Y_max]` Ceilings**: Lock co-displayed plots or filter cohorts sharing a physical unit (`yUnit`) to one unified $1\text{--}2\text{--}5$ scale and identical SI prefix (`QuietSvgLayout.sharedNiceScale125`). Mark magnified secondary cutouts explicitly (`Zoomed scale: 0..Y` / `quietZoomedScale`).
3. **Disparate Units & Differing Event Lengths**: Co-displayed plots *may* use independent X domains when X units differ (`Time` vs. `Distance`) or when comparing events of unequal duration (`eventKey` / `independentXSpan`), and *may* use independent Y domains when Y units differ (`kPa` vs. `°C` / `independentYSpan`) — while **always** keeping column `[x_left, x_right]` and row `[y_top, y_bottom]` inner plot-box pixels registered within $\le 2\,\text{px}$.

---

## 8. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- Scales & Ticks Architecture: [scales-ticks-and-uncertainty.md](scales-ticks-and-uncertainty.md)
- Conditions & Envelopes: [conditions-and-envelopes.md](conditions-and-envelopes.md)
- Delivery Mediums: [quiet-ui](../../quiet-ui/SKILL.md)
- Audience Translation: [quiet-bridge](../../quiet-bridge/SKILL.md)
