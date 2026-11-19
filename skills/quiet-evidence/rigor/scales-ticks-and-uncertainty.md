# Scales, Ticks, and Uncertainty Representation

In Quiet UI Pillar 2, axis scale intervals, logarithmic graticules, uncertainty intervals, and telemetry discontinuities are governed by strict metrological invariants derived from **NAVAIR FTM-108** (*Flight Test Manual: Data Presentation*) and **NIST Engineering Statistics Handbook (e-Handbook)**.

---

## 1. The NAVAIR FTM-108 1-2-5 Interval Law

Every linear axis major tick step $\Delta_{\text{step}}$ must strictly conform to the **1–2–5 interval sequence**:

$$\Delta_{\text{step}} = c \times 10^n, \quad \text{where } c \in \{1, 2, 5\} \text{ and } n \in \mathbb{Z}$$

Permitted step sizes include:
- $n = -2$: $0.01, 0.02, 0.05$
- $n = -1$: $0.1, 0.2, 0.5$
- $n = 0$: $1, 2, 5$
- $n = 1$: $10, 20, 50$
- $n = 2$: $100, 200, 500$

### Prohibited Tick Intervals
- **Arbitrary Fractional Steps**: Steps of $3, 4, 6, 7, 8, 9 \times 10^n$ (e.g., $0, 3, 6, 9\dots$ or $0, 4, 8, 12\dots$) are strictly prohibited because they impede rapid mental interpolation.
- **Floating-point roundoff artifacts**: Ticks such as `0.15000000000000002` or `1.333`.

### Tick Generation Algorithm
Given minimum value $y_{\min}$, maximum value $y_{\max}$, and target tick count $k_{\text{target}} \in [4, 8]$:
1. Compute raw span: $S = y_{\max} - y_{\min}$.
2. Compute rough step: $\Delta_0 = S / k_{\text{target}}$.
3. Determine decade order: $n = \lfloor \log_{10} \Delta_0 \rfloor$.
4. Compute normalized fraction: $f = \Delta_0 / 10^n$.
5. Select $c$ by nearest Euclidean threshold:
   - If $f < \sqrt{1 \times 2} \approx 1.414 \implies c = 1$
   - Else if $f < \sqrt{2 \times 5} \approx 3.162 \implies c = 2$
   - Else if $f < \sqrt{5 \times 10} \approx 7.071 \implies c = 5$
   - Else $\implies c = 10$ ($n \leftarrow n + 1, c \leftarrow 1$)
6. Quantize axis bounds: $y_{\text{start}} = \lfloor y_{\min} / \Delta_{\text{step}} \rfloor \times \Delta_{\text{step}}$, $y_{\text{end}} = \lceil y_{\max} / \Delta_{\text{step}} \rceil \times \Delta_{\text{step}}$.

---

## 2. Logarithmic Axis Graticules & Mandatory Minor Decades

Logarithmic plots (such as Allan deviation, power spectral density, and Bode magnitude/phase) must visually communicate non-linear dynamic range through standard logarithmic graticules:

### A. Major Decades
- Major ticks and graticule lines are located exclusively at integer powers of ten: $10^n$ (e.g., $10^{-3}, 10^{-2}, 10^{-1}, 10^0, 10^1$).
- Major tick labels use scientific notation ($10^{-3}, 10^0, 10^3$) or SI engineering prefixes (`1 m`, `1`, `1 k`).

### B. Mandatory Minor Decades ($2\dots 9$)
- Within every log decade $[10^n, 10^{n+1}]$, visual builders **must** render minor tick pips or subdued graticule lines at the seven intermediate multipliers:
  $$\tau_m = m \times 10^n, \quad \text{for } m \in \{2, 3, 4, 5, 6, 7, 8, 9\}$$
- **Ban on Blank Decades**: A logarithmic axis that omits minor ticks creates optical illusions of linearity and violates Pillar 2 standards.
- **Graticule Weighting**:
  - Major lines: `stroke-width: 1.0px; stroke: var(--border-strong); stroke-dasharray: none;`
  - Minor lines: `stroke-width: 0.5px; stroke: var(--border-hairline); stroke-dasharray: 1 3;`

---

## 3. Uncertainty Representation: Corridors & Error Bars

Physical telemetry carries measurement uncertainty. In accordance with JCGM 100:2008:

### A. Discrete Measured Points with Error Bars
- When displaying discrete calibration points $(x_i, y_i)$, vertical error bars represent the expanded uncertainty:
  $$U_i = k \cdot u_c(y_i)$$
  where $k=2$ corresponds to an approximate $95.45\%$ coverage probability.
- Symmetrical bars terminate in clean horizontal caps (width $4\ \text{px}$) or capless precision ticks.
- If asymmetrical confidence intervals are computed (e.g., Poisson count statistics), separate upper and lower error bounds ($+U_{i,\text{upper}}, -U_{i,\text{lower}}$) must be declared.

### B. Continuous Uncertainty Corridors
- When displaying a fitted physical model $\hat{y}(x)$, the uncertainty is rendered as a shaded polygonal corridor centered on $\hat{y}(x)$:
  - $\pm 1\sigma$ corridor: 68.27% confidence band, fill opacity $\alpha = 0.18$.
  - $\pm 2\sigma$ corridor: 95.45% confidence band, fill opacity $\alpha = 0.08$.
- Shaded corridors must be rendered behind all trace strokes and data markers to prevent obscuring point centroids.

---

## 4. NIST 4-Plot Residual Strip Pairing

Whenever a parameterized theoretical model $\hat{y}(x; \mathbf{\theta})$ or baseline curve is fitted to measured data $y_i$, visual builders must render a **synchronously projected residual strip** directly below the main plot:

$$r_i = y_i - \hat{y}(x_i)$$

```
+-----------------------------------------------------------+
| Main Evidence Panel (75% Vertical Height)                 |
| - Discrete measured points with error bars                |
| - Continuous fitted regression model                      |
| - Upper/lower abort envelope corridors                    |
+-----------------------------------------------------------+
| Residual Strip Panel (25% Vertical Height)                |
| - Centerline r = 0 (solid reference line)                 |
| - Residual points r_i aligned with identical X-scale      |
| - ±2*sigma_residual dashed boundary corridor              |
+-----------------------------------------------------------+
```

### Residual Strip Invariants
1. **Shared Abscissa**: The residual horizontal axis must use the exact coordinate mapping, limits, and tick alignment as the upper main plot.
2. **Homoscedasticity Verification**: The residual strip enables instantaneous visual detection of model drift, systematic curvature, or variance flare.

---

## 5. Telemetry Dropout Gaps & Missing Frame Policy

A critical flaw in consumer graphing libraries is the automatic interpolation of smooth splines across missing telemetry frames.

> [!CAUTION]
> **Zero Interpolation Across Dropouts**: A visual builder must NEVER connect discrete telemetry samples across a communication dropout or sensor blindness interval.

### Telemetry Gap Rules
1. **Gap Detection Threshold**: An interval $[t_k, t_{k+1}]$ is classified as a telemetry gap when:
   $$\Delta t = t_{k+1} - t_k > 1.5 \times \Delta t_{\text{nominal}}$$
   or when sample payload values are explicitly flagged `null` or `NaN`.
2. **Rendering Behavior**:
   - The primary line trace terminates at $(t_k, y_k)$ (`path M...L...`) and begins a fresh path segment at $(t_{k+1}, y_{k+1})$ (`M...`).
   - The dropout span $[t_k, t_{k+1}]$ is visually demarked by a subtle vertical hatch or translucent backdrop (`rgba(128, 128, 128, 0.08)`).
   - In L3 metrological mode, the gap is annotated with the dropout duration $\Delta t_{\text{gap}}$.

---

## 6. Scales and Uncertainty JSON Specification

The following JSON configuration illustrates declarative scale, tick, and uncertainty definition:

```json
{
  "axes": {
    "x_axis": {
      "quantity": "tau",
      "unit": "s",
      "scale_type": "logarithmic",
      "domain": [0.001, 10000.0],
      "major_ticks": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0],
      "minor_log_ticks": true,
      "tick_format": "engineering"
    },
    "y_axis": {
      "quantity": "sigma_y(tau)",
      "unit": "1",
      "scale_type": "logarithmic",
      "domain": [1e-15, 1e-10],
      "major_ticks": [1e-15, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10],
      "minor_log_ticks": true,
      "tick_format": "scientific"
    }
  },
  "uncertainty": {
    "model": "gaussian",
    "coverage_factor_k": 2.0,
    "confidence_level_pct": 95.45,
    "corridor_alpha": 0.15,
    "show_error_bars": true
  },
  "dropout_handling": {
    "max_interval_factor": 1.5,
    "interpolate_nulls": false,
    "highlight_gaps": true
  }
}
```

---

## 7. Verification Checklist

Before emitting SVG markup or Canvas paths:
- [ ] Major linear ticks follow $1, 2, 5 \times 10^n$ steps exclusively.
- [ ] Logarithmic axes include minor ticks at $2, 3, 4, 5, 6, 7, 8, 9 \times 10^n$.
- [ ] Continuous models have shaded uncertainty envelopes rendered beneath lines.
- [ ] Fitted curves are accompanied by a synchronized residual strip.
- [ ] Missing telemetry frames are rendered as open path breaks, not interpolated lines.

---

## 8. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- Metrology & NIST Units: [metrology-and-nist-units.md](metrology-and-nist-units.md)
- Conditions & Envelopes: [conditions-and-envelopes.md](conditions-and-envelopes.md)
- Analytical Plots Modality: [analytical-and-spectral-plots.md](../modalities/analytical-and-spectral-plots.md)
- Waveforms & Timing Modality: [waveforms-and-timing.md](../modalities/waveforms-and-timing.md)
