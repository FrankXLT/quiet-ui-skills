# Audience Lens: Discipline Specialist Engineer

This guide defines the analytical requirements, metrological rigor, and presentation protocols for interfaces delivered to discipline specialist engineers (RF, thermal, structural dynamics, optical, signal processing, and power electronics).

---

## 1. Persona Profile & Analytical Mindset

| Dimension | Analytical Specification |
| :--- | :--- |
| **Role Archetypes** | RF Payload Engineer, Thermal Analysis Lead, Guidance/Navigation/Control (GNC) Specialist, Structural Dynamicist, Optical Metrology Lead |
| **Primary Workflow** | Hardware-in-the-loop (HIL) testing, parameter extraction, simulation correlation, root-cause anomaly investigation, peer design reviews |
| **Cognitive Framework** | First-principles conservation laws (mass, momentum, energy, charge); empirical validation via statistical inference |
| **Acceptance Standard** | A claim does not exist without governing equations, error distributions, calibration coefficients, and measurement bounds |
| **Review Velocity** | Deliberate, methodical, deep-dive examination (10 to 45 minutes per figure or dataset) |

Discipline specialists are unimpressed by clean UI chrome or polished summary cards. They view over-simplified representations with deep suspicion. If an interface suppresses error bars, omits the measurement bandwidth, or draws smooth splines through sparse discrete data points, the specialist immediately concludes the author is either mathematically naive or concealing unfavorable physics.

---

## 2. Native Units of Proof

To satisfy the evidentiary threshold of a discipline engineer, data presentations must include the following native units of proof:

1. **Governing Physical Equations**: Explicit formulas stating variables, boundary conditions, and constitutive relations (e.g., thermal dissipation $q = -k \nabla T$, Allan variance $\sigma_y^2(\tau) = \frac{1}{2(M-1)} \sum_{i=1}^{M-1} (\bar{y}_{i+1} - \bar{y}_i)^2$).
2. **Confidence Intervals and Statistical Dispersion**: Point estimates paired with explicit confidence bands ($\pm 1\sigma, \pm 3\sigma$, 95% confidence intervals, Student's t degrees of freedom).
3. **Log-Decade Frequency-Domain Curves**: Allan deviation plots $\sigma_y(\tau)$ over decades $10^{-2} \le \tau \le 10^5\text{ s}$, power spectral density (PSD) in $\text{dBc/Hz}$ or $g^2/\text{Hz}$ with stated windowing function (e.g., Hann, 64k FFT, 50% overlap).
4. **Polynomial Calibration Coefficients**: Polynomial parameters ($a_0, a_1, a_2, \dots, a_n$) with residual sum of squares ($R^2$ or $\chi^2_{\text{red}}$) and calibration temperature reference ($T_{\text{ref}} = 293.15\text{ K}$).
5. **Residual Error Distributions**: Difference plots $(y_{\text{measured}} - y_{\text{modeled}})$ presented adjacent to nominal fit lines to reveal unmodeled higher-order systematic errors.
6. **Environmental Test Vectors**: Explicit test context including chamber pressure ($P_{\text{amb}} \le 1.0 \times 10^{-5}\text{ Torr}$), baseplate temperature ($T_{\text{plate}} = 25.0 \pm 0.5^\circ\text{C}$), and supply rail ripple ($V_{\text{rip}} \le 15\text{ mV}_{\text{p-p}}$).
7. **Raw Sampling Rate and Filter Disclosures**: ADC sampling frequency ($f_s = 100.0\text{ MSPS}$), anti-aliasing filter cut-off (-3 dB at 42 MHz), and effective number of bits (ENOB = 11.4 bits).

---

## 3. Presenter Biases to Scrub

When compiling technical briefings for discipline specialists, eliminate the following presentation anti-patterns:

```
[PRESENTER BIAS]                                   [DISCIPLINE SCRUB DIRECTIVE]
------------------------------------------------------------------------------------------------------------------------
Hand-wavy marketing claims ("high reliability")     --> Replace with verified MTBF (hours) and 95% confidence lower bound.
Smooth Bezier curves through discrete samples       --> Render explicit scatter glyphs with error bars; no spline smoothing.
Uncalibrated nominal values ("operates at 5.0 V")   --> State tolerance envelope: 5.000 V +/- 0.025 V (3-sigma, 0 to 50 C).
Linear extrapolation beyond measured range          --> Truncate curves strictly to qualified domain; mark extrapolation dashed.
Qualitative adjectives ("adequate heat sinking")   --> State thermal margin: delta-T_margin = 18.4 K below junction ceiling.
Normalized arbitrary axis scales (0.0 to 1.0)       --> Enforce physical SI units (W/m^2, Pa, rad/s, A/cm^2, ps/m).
Unstated decibel reference planes                   --> Explicitly declare dBm (50 ohm), dBW, dBc, or dBuV reference points.
```

---

## 4. Receiver Dealbreakers

A presentation or UI view presented to a discipline specialist will face immediate technical rejection upon any of the following triggers:

- **Unstated Sigma Bounds**: Displaying an error corridor or shaded band without explicitly defining whether it denotes $\pm 1\sigma$, $\pm 2\sigma$, $\pm 3\sigma$, or min/max envelope.
- **Continuous Splines Across Discrete Missing Data**: Drawing unbroken curves across unmonitored time intervals or skipped frequency bins.
- **Missing Environmental Context**: Showing RF phase drift, oscillator jitter, or structural deflection without the synchronized temperature and vibration telemetry.
- **Uncited Calibration Heritage**: Presenting calibrated telemetry without referencing the laboratory calibration certificate, date, and serial number of the reference standard.
- **Truncated Dynamic Range**: Clamping negative residual spikes or spectral sidelobes below an arbitrary noise floor.
- **Unstated Windowing or Decimation Functions**: Presenting Fourier transforms or spectral power without identifying whether Welch, Blackman-Harris, or rectangular windowing was applied.

---

## 5. Discipline Engineer to Systems Engineer Translation Bridge

Specialist findings must be translated into cross-subsystem interface allocations without losing mathematical rigor:

| Specialist Analysis & Mathematical Proof | Systems Engineering ICD Allocation | Allocation Boundary Verification |
| :--- | :--- | :--- |
| "Thermal dissipation: $Q = 48.2\text{ W}$ concentrated on $4.0\text{ cm} \times 4.0\text{ cm}$ ASIC package, yielding heat flux $q'' = 3.01\text{ W/cm}^2$. Conductive interface requires $\theta_{jc} \le 0.45\text{ K/W}$." | **Thermal ICD Alloc 4.2**: Payload Subsystem interface cold plate must maintain $\le 45^\circ\text{C}$ with heat load of $55.0\text{ W}$ (includes 14% margin). | Dual-sensor heat flux transducer test per MIL-STD-1540E. |
| "Allan deviation $\sigma_y(\tau = 1\text{ s}) = 1.2 \times 10^{-12}$; white phase noise floor is $-142\text{ dBc/Hz}$ at $10\text{ kHz}$ offset. Integrated timing jitter is $18.4\text{ ps}$ RMS." | **Timing ICD Alloc 7.1**: Master Reference Clock distribution budget allocates $\le 25.0\text{ ps}$ RMS jitter to Subsystem B. Margin is $+6.6\text{ ps}$. | High-bandwidth real-time oscilloscope jitter analysis at J101. |
| "First structural resonance mode $f_1 = 38.4\text{ Hz}$ with $Q = 22.0$ (damping ratio $\zeta = 0.0227$). Dynamic amplification at launch load yields $14.2\text{ g}$ RMS." | **Structural ICD Alloc 2.4**: Subsystem bracket fundamental frequency must exceed $35.0\text{ Hz}$. Notched random vibration profile certified to $16.0\text{ g}$ RMS. | Tri-axial accelerometer survey during base-shake sine sweep. |
| "Phase margin $\Phi_m = 42.1^\circ$ at gain crossover $f_c = 14.8\text{ kHz}$; gain margin $G_m = 9.8\text{ dB}$. Right-half-plane zero identified at $182\text{ kHz}$." | **Control Loop Stability Req 3.1**: DC-DC converter output regulation loop requires $\ge 40.0^\circ$ phase margin under full $0\text{ to }10\text{ A}$ step transient. | Network analyzer injection test across feedback isolation resistor. |
| "Receiver optical sensitivity $P_{\text{sens}} = -23.8\text{ dBm}$ at $\text{BER} \le 10^{-9}$; inter-symbol interference penalty is $1.1\text{ dB}$ due to chromatic dispersion." | **Optical Link ICD Alloc 5.3**: Ground-to-vehicle optical transceiver link budget requires total path loss $\le 19.5\text{ dB}$ for $0\text{ dBm}$ launch power. | Automated bit error rate tester (BERT) with optical attenuator sweep. |

---

## 6. Concrete Analytical Display Pattern: Metrology Dual Stage

When designing an interface for peer design review or laboratory analysis, use the synchronized dual-panel metrology layout:

```
+----------------------------------------------------------------------------------------------------------------------+
| SPECIALIST METROLOGY CONSOLE: CHANNEL B2 - ULTRA-STABLE OSCILLATOR (USO) RUN 409B            | 2026-11-16 19:10 UTC   |
+----------------------------------------------------------------------------------------------------------------------+
| PRIMARY CURVE: ALLAN DEVIATION sigma_y(tau)          | SECONDARY STAGE: FIT RESIDUALS & NOISE RESIDUAL DISTRIBUTION   |
|                                                      |                                                                |
| 1e-11 |                                              | +0.4 ps |   *     *           *       *  *                     |
|       | *                                            |         |  * *   * *   * *   * *     *    *   [+3 sigma bound]  |
| 1e-12 |   * *                                        |  0.0 ps +-----------------------------------------------------+|
|       |       * *   [Measured Data +/- 1 sigma]      |         |     * *   * * *   *   * * *       [-3 sigma bound]  |
| 1e-13 |           * * *                              | -0.4 ps |            *             *                           |
|       |                 * * *                        |                                                                |
| 1e-14 |                       * * * [Flicker Floor]  | FIT POLYNOMIAL: delta_t(T) = a0 + a1*(T - T0) + a2*(T - T0)^2  |
|       +--------------------------------------------  | a0 = 1.042e-12 | a1 = -3.120e-15/K | a2 = 4.881e-18/K^2        |
|      1e-2    1e-1     1e0     1e1     1e2    1e3 (s) | Cal Standard: NIST-FREQ-4412 | R^2 = 0.99982 | DoF = 1,024     |
+----------------------------------------------------------------------------------------------------------------------+
| ENVIRONMENTAL SENSORS: Chamber Pressure: 4.2e-6 Torr | Shaker Profile: Random 6.4 g RMS | Baseplate Temp: 24.8 +/-0.1 C |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Numerical Conservation & Schema Integrity

When discipline data feeds multi-tier UI views, it must originate from a canonical physical dataset. The schema preserves exact calibration metadata:

```json
{
  "parameter_id": "RF_LNA_GAIN_CAL",
  "physical_quantity": "Gain",
  "si_unit": "dB",
  "nominal_value": 24.32,
  "confidence_bounds": {
    "sigma_level": 3,
    "lower_bound": 24.15,
    "upper_bound": 24.49
  },
  "calibration_model": {
    "type": "polynomial_degree_2",
    "coefficients": {
      "a0": 24.321,
      "a1": -0.0142,
      "a2": 0.00011
    },
    "temperature_reference_kelvin": 293.15,
    "r_squared": 0.9994
  },
  "provenance": {
    "calibration_station_id": "CAL-RF-08",
    "standard_cert_id": "NIST-RF-2026-9041",
    "sample_timestamp_utc": "2026-11-16T18:40:12Z",
    "ambient_temp_c": 21.4,
    "ambient_humidity_pct": 34.2
  }
}
```

---

## 8. Discipline Engineering Inspection Rubric

Prior to publishing any data visualization or analytical brief targeted at discipline specialists, audit against these seven verification gates:

1. **Explicit Error Architecture**: Are error bars, confidence intervals, or variance envelopes explicitly labeled with their mathematical definition ($\pm 1\sigma$, $\pm 3\sigma$, 95% CI)?
2. **Discrete Scatter Fidelity**: Are measured data points rendered as distinct glyphs before any continuous regression model is overlaid?
3. **Calibrated Baseline Evidence**: Does every plot state the test conditions, instrument serial numbers, and calibration dates in the caption or metrology block?
4. **Residual Inspection Channel**: Are non-linear regression fits accompanied by a residual deviation sub-panel?
5. **No Clamped Dynamic Range**: Are high-frequency spectral components and noise floors displayed without artificial numerical clipping?
6. **Physical Conservation Consistency**: Does the summation of component parameters strictly conserve total mass, energy, power, and timing margins across the interface?
7. **Windowing and Sampling Transparency**: Are FFT decimation rates, window functions, and Nyquist cutoffs fully documented in the chart header?

---

## 9. Cross-Reference Links

- For translating specialist parameters into contractual interface documents, see [project-systems-engineer.md](project-systems-engineer.md).
- For converting physical thresholds into field operator runbooks, see [technician-and-operator.md](technician-and-operator.md).
- For structuring deep-dive analytical presentations (10–45 min), see [../tempos/analytical-deep-dive.md](../tempos/analytical-deep-dive.md).
- For stress-testing discipline assumptions before review panels, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).
