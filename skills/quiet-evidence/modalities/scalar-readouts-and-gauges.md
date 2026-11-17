# Modality: Scalar Readouts and Gauges

Scalar readouts, single-value callouts, status annunciator pills, and dynamic linear gauges translate point-in-time telemetry into immediate operational comprehension.

---

## 1. Visual Anatomy & Component Architecture

A Quiet UI scalar readout card is structured into five distinct vertical zones to guarantee zero optical ambiguity:

```
+-----------------------------------------------------------------------+
| ZONE 1: Context Header                                                |
| [Subsystem Identifier]               [Timestamp UTC / Stale Indicator]|
| Cryogenic Cold Finger Temperature                                     |
+-----------------------------------------------------------------------+
| ZONE 2: Primary Physical Metric & Annunciator                         |
|   77.342 K                         +-------------------------------+  |
|   T_cryo / K                       | [OK] NOMINAL (Margin: +82.5%) |  |
|                                    +-------------------------------+  |
+-----------------------------------------------------------------------+
| ZONE 3: Linear Envelope Bar Gauge                                     |
| Low Abort     Low Warn        Nominal Target     High Warn High Abort |
| [75.0]        [76.2]             [77.0]           [77.8]   [78.5]     |
|   |--------------[========|========▼========]----------------|        |
+-----------------------------------------------------------------------+
| ZONE 4: Metrology & Uncertainty Micro-Strip                           |
| Expanded Uncertainty: (77.342 ± 0.015) K | k=2.0 | 95.45% Confidence  |
+-----------------------------------------------------------------------+
| ZONE 5: Provenance & Traceability Footer                              |
| Sensor: PT100-PLAT-0842 | Cal: NIST-2026-8812A | Raw ADC: 24891 cts   |
+-----------------------------------------------------------------------+
```

---

## 2. The Rigor Continuum Progression Table

In Quiet UI, every scalar visual adapts across the three-tier rigor continuum depending on operational tempo and audience lens:

| Rigor Level | Target Audience | Primary Focus | Display Anatomy & Content |
| :--- | :--- | :--- | :--- |
| **L1 Orientation** | Common Reader, Executive Briefing | High-level system state & qualitative health | Large formatted integer/decimal, status pill (`NOMINAL`, `ADVISORY`, `ALERT`), calm descriptive label, sparkline trend indicator without complex ticks. |
| **L2 Governance** | Program Manager, Systems Engineer | Contract compliance & operating margins | Nominal value, tolerance window ($\pm \Delta$), delta relative to baseline target, remaining margin percentage, and governance disposition flag. |
| **L3 · Physical, Clinical & Metrological** | Discipline Engineer, Intensivist, Metrologist | Traceable physical proof & uncertainty | Full NIST SP 811 quantity calculus ($Quantity / Unit$), nominal value with expanded uncertainty ($U = k \cdot u_c$), sensor/bedside probe ID, calibration date, and raw sample count. |

---

## 3. Universal Schema: `urn:quiet-ui:schema:v9:scalar`

All scalar components must validate against the offline Quiet UI scalar schema specification:

```json
{
  "$schema": "urn:quiet-ui:schema:v9:scalar",
  "id": "readout-cryo-temp-sensor-04",
  "metadata": {
    "title": "Cryogenic Cold Finger Temperature",
    "description": "Primary focal plane array Dewar temperature monitoring",
    "rigor_level": "L3",
    "timestamp_utc": "2026-11-16T19:30:00.000Z",
    "subsystem": "THERMAL-CONTROL-SUBSYSTEM"
  },
  "quantity": {
    "symbol": "T_cryo",
    "name": "Absolute Temperature",
    "unit": "K",
    "quantity_calculus": "T_cryo / K"
  },
  "measurement": {
    "nominal_value": 77.342,
    "display_value": "77.342",
    "expanded_uncertainty": 0.015,
    "coverage_factor": 2.0,
    "confidence_pct": 95.45,
    "raw_adc_counts": 24891,
    "calibration_id": "CAL-NIST-2026-8812A"
  },
  "limits": {
    "nominal_target": 77.0,
    "tolerance_band": [-0.5, 0.5],
    "warning_thresholds": {
      "lower": 76.2,
      "upper": 77.8
    },
    "abort_thresholds": {
      "lower": 75.0,
      "upper": 78.5
    }
  },
  "status_annunciator": {
    "state": "NOMINAL",
    "color_token": "var(--status-ok)",
    "bg_token": "var(--status-ok-bg)",
    "label": "NORMAL RANGE",
    "margin_remaining_pct": 82.5
  },
  "gauge": {
    "type": "linear_horizontal",
    "min_scale": 74.0,
    "max_scale": 80.0,
    "major_step": 1.0,
    "marker_position": 77.342
  }
}
```

---

## 4. Gauge Linear Coordinate Normalization

Linear bar gauges must project physical quantities onto screen coordinates without clipping or non-linear distortion.

For a physical value $x \in [x_{\min}, x_{\max}]$ mapped across display width $W_{\mathrm{gauge}}$:

$$X_{\mathrm{pixel}} = W_{\mathrm{gauge}} \times \left( \frac{x - x_{\min}}{x_{\max} - x_{\min}} \right)$$

When $x$ exceeds operational scale limits, the indicator pin clamps to $0$ or $W_{\mathrm{gauge}}$ with an expanded overflow chevron indicator ($\blacktriangleleft$ or $\blacktriangleright$) to prevent silent off-screen clipping.

---

## 5. Annunciator Status State Machine

Annunciator pills must transition across six deterministic states with non-reliance on color alone:

| State Code | Pill Label | Variant & State | Visual Rendering | Operational Invariant |
| :--- | :--- | :--- | :--- | :--- |
| `NOMINAL` | `Nominal` | `status` / `nominal` | Borderless transparent, `6px` dot (`::before`), `var(--text-secondary)` | Value within nominal target envelope (`ISA-101` quiet background) |
| `ADVISORY`| `ADVISORY` | `status` / `warn` | `10%` warn wash, `2.5px` start bar, `▲`, `var(--status-warn)` | Operating outside preferred regime |
| `WARNING` | `CAUTION` | `status` / `warn` | `10%` warn wash, `2.5px` start bar, `▲`, `var(--status-warn)` | Operating within warning envelope ($\ge 80\%$) |
| `CRITICAL`| `TRIPWIRE` | `status` / `fault` | `12%` danger wash, `2.5px` start bar, `◆`, `var(--status-danger)` | Crossed hard abort threshold; interlock armed |
| `STALE`   | `STALE DATA` | `status` / `warn` | `10%` warn wash, `2.5px` start bar, `▲`, `var(--status-warn)` | No sample update received within $2.0 \times \Delta t_{\mathrm{sample}}$ |
| `FAULT`   | `SENSOR FAULT` | `status` / `fault` | `12%` danger wash, `2.5px` start bar, `◆`, `var(--status-danger)` | ADC open-circuit, short-circuit, or parity error |

---

## 6. Medium Adaptation Rules

The rendering engine adapts the scalar visual across different delivery surfaces while preserving numerical truth:

### Medium M1: Precision Static Print & PDF
- **Typography**: Uses high-contrast tabular figures (`font-variant-numeric: tabular-nums;`). Units are explicitly attached using non-breaking spaces.
- **Baseline Alignment Lock & Atomic Separation**: Side-by-side `.qe-scalar-card` blocks lock `.qe-scalar-top` (`min-block-size: 1.375rem`), card title block, `.qe-scalar-val-row`, and `.qe-gauge-svg` baselines within `<= 1.0px` regardless of stale/warn annunciator presence. Quantitative margins (`Margin +18.0%`) live in `.qe-scalar-margin` adjacent to the `.va-pill`, never concatenated inside it.
- **Quiet-Nominal Matrix Heatmaps**: Nominal `3×8` telemetry matrix cells (`data-role="bitcell" data-state="nominal"`) use calm `--bg-elevated` surfaces so isolated `warn` (`▲`) and `fault` (`◆`) excursions stand out cleanly.
- **Grayscale Redundancy**: Status annunciator pills must not rely on color alone. Excursions combine distinct alphanumeric text (`CAUTION`, `TRIPWIRE`), shape prefixes (`▲`, `◆`), and `2.5px` start borders; nominal states render quietly in `var(--text-secondary)` with a subtle `6px` dot (`::before`).
- **Footnotes**: In L3 mode, expanded uncertainty and calibration certificate IDs are printed as compact superscripted annotations directly below the scalar block.

### Medium M3: Stateful Web Application
- **Micro-Trend Sparkline**: Displays an inline 60-second historical sparkline with discrete minimum and maximum extents.
- **Live State Transitions**: When the scalar value updates via WebSocket, numerical values transition smoothly without layout shift.
- **Interactive Inspection**: Hovering or clicking reveals a popover containing the raw ADC bit count, sensor thermal transfer curve, and sensor serial number.

### Medium M6: Optical HUD & Tactile Console
- **Glanceability Under Stress**: The primary numerical readout is rendered in large monospace glyphs (at least 32px or 2rem) with background text halos.
- **Peripheral Linear Gauge**: Replaces round automobile-style gauges with an ultra-compact linear progress strip where the active reading is a sharp triangular needle against green/amber/red envelope zones.

---

## 7. Design Guidelines & Anti-Patterns

### Prohibited Patterns
- **No Radial "Speedometer" Dials**: Circular analog dials waste display real estate, obscure precise decimal fractions, and fail NASA-STD-3001 glanceability standards. Use linear bar gauges or digital readouts.
- **Color-Only Status Indicators**: Never represent go/no-go states solely with a red or green dot. Colorblind users must have explicit text tokens (`NOMINAL`, `WARN`, `ABORT`).
- **Unbracketed Uncertainty**: Never print `77.342 ± 0.015 K`. According to NIST SP 811, parentheses are mandatory: `(77.342 ± 0.015) K`.

### Required Practices
- Always right-align or decimal-align numerical values in tabular scalar cards.
- Maintain consistent significant digits matching sensor resolution.

---

## 8. Verification Checklist

Before emitting component templates:
- [ ] Conforms to schema URI `urn:quiet-ui:schema:v9:scalar`.
- [ ] Progression level (L1, L2, or L3) matches the audience requirement.
- [ ] Status pill includes explicit text label in addition to color tokens.
- [ ] Numerical uncertainty and tolerances are declared with identical precision to the measurement.

---

## 9. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [../rigor/metrology-and-nist-units.md](../rigor/metrology-and-nist-units.md)
- Conditions & Envelopes: [../rigor/conditions-and-envelopes.md](../rigor/conditions-and-envelopes.md)
- Tables & Matrices Modality: [tables-and-matrices.md](tables-and-matrices.md)
- Delivery Mediums: [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md)
- Audience Translation: [../../quiet-bridge/SKILL.md](../../quiet-bridge/SKILL.md)
