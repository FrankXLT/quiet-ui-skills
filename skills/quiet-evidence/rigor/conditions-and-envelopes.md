# Test Conditions, Envelopes, and Trace Ergonomics

In Quiet UI Pillar 2, every quantitative visualization must declare its operational environment, distinguish measured data from theoretical models, and render unambiguous safety envelopes with non-interfering typographical halos.

---

## 1. Test-Condition Header Blocks

Data is meaningless without declared provenance and boundary conditions. Every telemetry capture, analytical plot, or waveform inspection view must embed a standard **Test-Condition Header Block**.

### Mandatory Environmental & Acquisition Fields
1. **Chamber / Ambient Temperature ($T_{\mathrm{amb}}$)**: Specified in degrees Celsius or kelvins with calibration tolerance (e.g., $23.0 \pm 0.5\ ^{\circ}\mathrm{C}$).
2. **Master Timebase / Clock Reference**: Oscillator type and stability (e.g., `10 MHz Rubidium Frequency Standard PRS10`, `GPS-Disciplined OCXO`).
3. **Sampling Rate ($f_s$) & Acquisition Span**: Nominal sample frequency (e.g., $f_s = 2.50\ \mathrm{GS/s}$) and total record length (e.g., $N = 1\,048\,576\ \mathrm{samples}$).
4. **Device Under Test (DUT)**: Hardware identifier, board serial number, and firmware build hash.
5. **Traceability & Timestamp**: ISO 8601 UTC timestamp and calibration certificate reference.

### Placement & Visual Presentation
- In printed or PDF artifacts (Medium M1), the condition block appears directly above the upper graticule margin as a compact horizontal telemetry strip.
- In interactive web applications (Medium M3), conditions occupy a collapsible drawer or persistent metadata breadcrumb.
- In heads-up displays (Medium M6), conditions are compressed into an alphanumeric status banner.

---

## 2. The Epistemological Trace Invariant

Visualizations must communicate the true epistemic status of every data stroke.

```
+-----------------------------------------------------------------------+
| Trace Type      | Representation          | Stroke / Marker Standard  |
+-----------------------------------------------------------------------+
| Measured Data   | Discrete Markers        | Circles, squares, diamonds|
| Analytical Model| Continuous Vector Line  | Solid line (1.5 px)       |
| Sim Baseline    | Dashed Vector Line      | Dashed (4 4, 1.0 px)      |
| Abort Limit     | Heavy Boundary Line     | Solid red / orange (2.0 px|
+-----------------------------------------------------------------------+
```

### The Core Law
- **Measured Data Points**: Because laboratory sensors collect samples at discrete intervals, empirical data must be displayed using **discrete geometric glyphs** (open circles $\circ$, filled circles $\bullet$, squares $\square$, or triangles $\triangle$).
- **Ban on Arbitrary Bezier Smoothing**: Visual builders must never connect discrete empirical points with aesthetic cubic splines that fabricate non-existent physical states. If line connections are required between dense points, use straight piecewise linear segments (`stroke-linejoin: round;`).
- **Continuous Models**: Continuous curves are reserved exclusively for closed-form mathematical equations, physical transfer functions, or regression baselines.

---

## 3. Directional Pass/Fail Abort Envelopes

Safety-critical interfaces require immediate perceptual awareness of operating margins. Pillar 2 defines two operational envelopes:

### A. The Advisory / Warning Corridor (Amber)
- Represents the nominal tolerance boundary (typically $\pm 2\sigma$ or $80\%$ of allowable operating limit).
- Rendered as a translucent shaded band (`var(--status-warn-bg)`) bounded by a subtle dashed line (`stroke-dasharray: 3 3; stroke: var(--status-warn);`).
- Crossing into the warning corridor signals impending excursion but does not trip hardware interlocks.

### B. The Hard Abort / Redline Limit (Crimson)
- Represents the maximum non-destructive rating, regulatory threshold, or automated interlock tripwire.
- Rendered as a prominent solid or dash-dot line (`stroke-width: 2.0px; stroke: var(--status-danger); stroke-dasharray: 6 2;`).
- In directional telemetry (e.g., maximum permissible jitter or minimum supply voltage), indicate the forbidden zone with unilateral chevron tick pips pointed toward the violation region.

---

## 4. Typography Ergonomics: Text Halos and Leader Lines

When data traces, noise bands, and graticule grids intersect text annotations, labels become illegible. Pillar 2 prohibits opaque bounding rectangular boxes that hide underlying traces. Instead, apply **SVG Text Halos**.

### CSS / SVG Text Halo Specification
The text halo utilizes the CSS `paint-order` property to render an expanded stroke of the background surface color beneath the legible text fill:

```css
.chart-annotation-label {
  font-family: var(--font-mono);
  font-size: 11px;
  fill: var(--text-primary);
  stroke: var(--bg-surface);
  stroke-width: 3.5px;
  stroke-linejoin: round;
  stroke-linecap: round;
  paint-order: stroke fill;
}
```

This guarantees high contrast across dense multi-trace waveforms while preserving visibility of the underlying waveform trajectory.

### Leader Line Standards
- When an annotation cannot sit directly adjacent to a feature without crowding, attach a leader line.
- Leader lines must be straight lines or single 45-degree dog-leg bends.
- The anchor point terminates at the target coordinate with a filled terminal dot ($\varnothing = 3.0\ \mathrm{px}$).

---

## 5. Declarative Conditions & Envelopes Schema

The following JSON schema fragment models test conditions and safety corridors:

```json
{
  "test_environment": {
    "dut_id": "BOARD-REV-D-0842",
    "firmware_version": "v4.12.0-rc3",
    "timestamp_utc": "2026-11-16T19:30:00Z",
    "temperature_c": 23.4,
    "relative_humidity_pct": 42.1,
    "reference_clock": "PRS10-10MHz-SN1094",
    "sample_rate_hz": 2500000000.0
  },
  "envelopes": [
    {
      "id": "env-advisory-upper",
      "type": "warning",
      "direction": "upper",
      "threshold_value": 1.25e-12,
      "unit": "s",
      "label": "Advisory Limit (+2σ)",
      "stroke_color": "var(--status-warn)",
      "fill_color": "var(--status-warn-bg)"
    },
    {
      "id": "env-abort-ceiling",
      "type": "abort",
      "direction": "upper",
      "threshold_value": 2.00e-12,
      "unit": "s",
      "label": "Interlock Tripwire Limit",
      "stroke_color": "var(--status-danger)",
      "tripwire_action": "TRIGGER_OPTICAL_SHUTTER"
    }
  ]
}
```

---

## 6. Pre-Render Validation Audit

Before compiling any evidence figure:
- [ ] Condition block contains ambient temperature, clock reference, sample rate, and DUT ID.
- [ ] Measured sensor data uses discrete glyphs; continuous lines are reserved for models.
- [ ] Safety envelopes clearly separate advisory corridors (amber) from hard abort limits (crimson).
- [ ] All floating text labels utilize `paint-order: stroke fill` with background halos.
- [ ] Leader lines use single dog-leg transitions with circular anchor dots.

---

## 7. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [metrology-and-nist-units.md](metrology-and-nist-units.md)
- Scales & Uncertainty: [scales-ticks-and-uncertainty.md](scales-ticks-and-uncertainty.md)
- Analytical Plots Modality: [analytical-and-spectral-plots.md](../modalities/analytical-and-spectral-plots.md)
- Schematics & Topologies: [schematics-and-topologies.md](../modalities/schematics-and-topologies.md)
