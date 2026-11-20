# Modality: Analytical and Spectral Plots

Analytical curves, Modified Allan Deviation $\mathrm{Mod}\,\sigma_y(\tau)$ charts, Power Spectral Density (PSD) waterfalls, and Bode magnitude/phase plots convey high-rigor physical models and parametric frequency telemetry.

---

## 1. The Rigor Continuum Progression Table

Analytical plots adapt across the three rigor levels depending on audience and decision tempo:

| Rigor Level | Target Audience | Primary Focus | Visual Mechanics & Evidence Density |
| :--- | :--- | :--- | :--- |
| **L1 Orientation** | Program Executive, Non-Specialist | Qualitative system stability & milestone performance | Single smoothed trend curve, primary stability floor callout (`Minimum Jitter at tau = 100 s`), simplified axis ticks, status badge (`STABLE`). |
| **L2 Governance** | Project Systems Engineer, Mission Assurance | Specification compliance & contractual margins | Measured response curve overlaid against contractual requirement mask, shaded margin corridor, verification test pass/fail stamp, milestone signoff. |
| **L3 · Physical, Clinical & Metrological** | Discipline Metrologist, Biostatistician, Quality Engineer | Traceable first-principles proof, SPC, CI & residual statistics | Full 1-2-5 or log-decade graticules with mandatory minor ticks ($2\dots 9$), discrete data points with $\pm 1\sigma$ or 95% CI whiskers, Shewhart SPC limits (`UCL/CL/LCL`, `USL/LSL`), continuous fits, residual strip ($y_i - \hat{y}_i$), and complete test conditions. |

---

## 2. Universal Schema: `urn:quiet-ui:schema:v9:plot`

All analytical and spectral plot specifications must validate against the offline Quiet UI plot schema:

```json
{
  "$schema": "urn:quiet-ui:schema:v9:plot",
  "id": "plot-mvar-synthesizer-stability",
  "metadata": {
    "title": "Modified Allan Deviation of Optical Synthesizer",
    "description": "Short-term phase noise and long-term thermal drift evaluation",
    "rigor_level": "L3",
    "timestamp_utc": "2026-11-16T19:30:00Z"
  },
  "test_environment": {
    "dut_id": "SYNTH-OPT-8810",
    "firmware_version": "v3.8.4",
    "ambient_temperature_c": 23.2,
    "temperature_uncertainty_c": 0.2,
    "reference_oscillator": "Rubidium-Atomic-PRS10",
    "sampling_rate_hz": 10000.0,
    "sample_count": 86400000
  },
  "axes": {
    "x_axis": {
      "quantity": "tau",
      "quantity_calculus": "tau / s",
      "unit": "s",
      "scale_type": "logarithmic",
      "domain": [0.001, 10000.0],
      "major_ticks": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0],
      "minor_log_ticks": true
    },
    "y_axis": {
      "quantity": "Mod_sigma_y(tau)",
      "quantity_calculus": "Mod_sigma_y(tau)",
      "unit": "1",
      "scale_type": "logarithmic",
      "domain": [1e-15, 1e-11],
      "major_ticks": [1e-15, 1e-14, 1e-13, 1e-12, 1e-11],
      "minor_log_ticks": true
    }
  },
  "envelopes": [
    {
      "id": "env-spec-ceiling",
      "type": "abort",
      "label": "Contract Specification Ceiling",
      "stroke_style": "dash-dot",
      "stroke_color": "var(--status-danger)",
      "equation": "2.0e-12 * tau^(-0.5)"
    }
  ],
  "series": [
    {
      "id": "series-theoretical-floor",
      "name": "Thermal White FM Noise Baseline",
      "epistemic_type": "analytical_model",
      "stroke_style": "dashed",
      "stroke_color": "var(--text-muted)",
      "stroke_width": 1.5,
      "equation": "1.2e-13 * tau^(-1.5)"
    },
    {
      "id": "series-measured-mvar",
      "name": "Measured Mod sigma_y(tau)",
      "epistemic_type": "discrete_measurement",
      "marker_glyph": "circle",
      "marker_size_px": 5,
      "marker_color": "var(--accent-focal)",
      "has_error_bars": true,
      "error_bar_confidence_pct": 95.45,
      "data_points": [
        {"x": 0.001, "y": 4.12e-12, "u_y": 2.1e-13},
        {"x": 0.01,  "y": 1.30e-12, "u_y": 6.8e-14},
        {"x": 0.1,   "y": 4.10e-13, "u_y": 2.2e-14},
        {"x": 1.0,   "y": 1.28e-13, "u_y": 7.0e-15},
        {"x": 10.0,  "y": 4.05e-14, "u_y": 2.4e-15},
        {"x": 100.0, "y": 1.25e-14, "u_y": 8.0e-16},
        {"x": 1000.0,"y": 1.82e-14, "u_y": 1.5e-15},
        {"x": 10000.0,"y": 6.45e-14, "u_y": 6.0e-15}
      ]
    }
  ],
  "residual_strip": {
    "enabled": true,
    "relative_height_pct": 25,
    "centerline_value": 0.0,
    "residual_quantity_calculus": "(y_i - y_hat) / sigma",
    "boundary_corridor_sigma": 2.0
  }
}
```

---

## 3. Compiler Coordinate Transformation Mathematics

To ensure mathematical precision, visual compilers must translate physical data tuples $(x, y)$ into viewport SVG pixels $(X, Y)$ using explicit coordinate transforms:

### A. Linear Coordinate Mapping
Given plot bounding box with origin $(X_0, Y_0)$, width $W$, and height $H$, where $Y_0$ is the top coordinate:

$$X = X_0 + \left( \frac{x - x_{\min}}{x_{\max} - x_{\min}} \right) \times W$$

$$Y = Y_0 + H - \left( \frac{y - y_{\min}}{y_{\max} - y_{\min}} \right) \times H$$

### B. Logarithmic Coordinate Mapping
For logarithmic axes spanning decades $[x_{\min}, x_{\max}]$ and $[y_{\min}, y_{\max}]$ where $x, y > 0$:

$$X = X_0 + \left( \frac{\log_{10}(x) - \log_{10}(x_{\min})}{\log_{10}(x_{\max}) - \log_{10}(x_{\min})} \right) \times W$$

$$Y = Y_0 + H - \left( \frac{\log_{10}(y) - \log_{10}(y_{\min})}{\log_{10}(y_{\max}) - \log_{10}(y_{\min})} \right) \times H$$

### C. Logarithmic Minor Tick Computation
Within each decade $[10^n, 10^{n+1}]$, minor tick positions for multiplier $m \in \{2, 3, 4, 5, 6, 7, 8, 9\}$ project to:

$$X_m = X_{\text{decade } n} + \log_{10}(m) \times \Delta X_{\text{decade}}$$

where $\Delta X_{\text{decade}} = W / \log_{10}(x_{\max} / x_{\min})$ represents the screen distance per decade.

---

## 4. Residual Strip Pairing & Graticule Layout

Quiet UI mandates a split-panel configuration whenever measured data is compared against analytical equations:

```
+-----------------------------------------------------------+
| Main Plot Area (75% Total Viewport Height)                |
| - Logarithmic decades: 10^-3 to 10^4 s                    |
| - Mod sigma_y(tau): 10^-15 to 10^-11                      |
| - Discrete markers with vertical error whiskers           |
| - Continuous model line & spec ceiling mask               |
+-----------------------------------------------------------+
| X-Axis Divider & Synchronized Graticule Alignment         |
+-----------------------------------------------------------+
| Residual Panel (25% Total Viewport Height)                |
| - Zero residual reference line: r = 0                     |
| - Normalized residual points: (y_i - y_hat) / sigma_i     |
| - Shaded ±2sigma acceptance corridor                      |
+-----------------------------------------------------------+
```

---

## 5. Cross-Domain Statistical, Schedule & Matrix Variants (`forest`, `waterfall`, `dumbbell`, `gantt`, `heatmap`, Shewhart SPC)

The plot compiler consumes `"plot_kind"` (`"cartesian"` default, `"forest"`, `"waterfall"`, `"dumbbell"`, `"stacked_bar"`, `"gantt"`, `"heatmap"`) and optional `"companions"` subpanels under `urn:quiet-ui:schema:v9:plot`:
- **Shewhart SPC Control Charts** (`cartesian`): Pair empirical subgroup runs (`X_bar`) against `CL` centerline, dashed `UCL/LCL` (`±3σ`), and redline `USL/LSL` specification envelopes, tagging `C_pk` and subgroup size `n` in `test_environment`.
- **Subgroup CI Forest Plots** (`forest`): Render point estimates, `95% CI` horizontal whiskers, diamond pooled markers (`pooled: true`), and null-effect reference lines (`OR = 1.0` or `HR = 1.0`) calibrated on NAVAIR `1-2-5` ticks.
- **Schedule Gantt Charts** (`gantt`): Accepts `tasks` (`[{id, label, phase, start, end, float_days|float_hours, critical, milestone, depends_on}]`), `today_day`, and `axes.x_axis` (`t / d` or `t / h`) on NAVAIR `1-2-5` ticks with orthogonal dependency elbows and dashed margin tails.
- **Calibrated 2D Matrix Heatmaps** (`heatmap`): Accepts `x_categories`, `y_categories`, `matrix` (2D numeric grid), and `scale` (`quantity_calculus`, `unit`, `domain`, `decimals`), binding WCAG-calibrated Blue-to-Copper ramp stops and auto-contrast cell numerals (`#0F172A` vs `#FFFFFF`).

---

## 6. Verification Checklist

Before emitting SVG or Canvas renders:
- [ ] Conforms to schema URI `urn:quiet-ui:schema:v9:plot`.
- [ ] Progression level matches target audience (`L1` executive summary vs `L3 · Physical, Clinical & Metrological`).
- [ ] Logarithmic axes include minor ticks at $2, 3, 4, 5, 6, 7, 8, 9 \times 10^n$.
- [ ] Empirical data is rendered with discrete markers; models and SPC/CI bounds match legend swatches (`epistemic_type`).
- [ ] Residual strip uses identical horizontal coordinate mapping and `3.5%` spine inset as main plot.

---

## 6. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [../rigor/metrology-and-nist-units.md](../rigor/metrology-and-nist-units.md)
- Scales & Uncertainty: [../rigor/scales-ticks-and-uncertainty.md](../rigor/scales-ticks-and-uncertainty.md)
- Waveforms & Timing Modality: [waveforms-and-timing.md](waveforms-and-timing.md)
- Delivery Mediums: [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md)
