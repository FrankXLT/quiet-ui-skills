# Audience Lens: Student & Learner

> **Document Class**: Foundational Audience Lens Specification  
> **Target Version**: Quiet UI v9.0 (`Pillar 3: Directional Translation`)  
> **Perspective**: Empirical Discovery, Scaffolded Inquiry & Rigorous Lab Reporting  
> **Audience Code**: `LENS-STU`

---

## 1. Native Unit of Proof & Learner Spectrum

The **Student & Learner** lens spans STEM students (secondary through undergraduate) and junior engineers onboarding into complex physical disciplines. Unlike a Consumer who treats technology as an opaque black box, the Student seeks to construct an accurate internal representation of physical mechanisms.

The Student's native units of proof are:
1. **Physical Cause-and-Effect Demonstration**: Direct observable correspondence between an input perturbation and an output response.
2. **Explicit Unit Calculus**: Step-by-step unit dimensional analysis showing how compound units cancel (e.g., $[V] / [A] = [\Omega]$).
3. **Controlled Empirical Comparison**: Discrete experimental measurements compared directly against a mathematical theoretical model.
4. **Quantified Uncertainty**: Clear visualization of experimental repeatability ($\pm 1\sigma$ spread) and systematic instrument limits.

---

## 2. Dual Operational Perspectives

### 2.1 As Audience (`Educator / Senior Engineer -> Student`)
When receiving technical material:
- **Demands Cognitive Speed Limits**: New terminology must be introduced at a digestible pace ($\le 3$ novel concepts per section).
- **Requires Plain-Language Glossaries**: A hoverable or adjacent symbol key must define all Greek and Roman symbols with SI units.
- **Relies on Worked Intermediate Steps**: Algebraic derivations must not skip factoring, substitutions, or unit conversions.
- **Benefits from Low-Stakes Self-Check Gates**: Integrated interactive questions ("What will happen to current if resistance doubles?") ground comprehension before proceeding.

### 2.2 As Presenter (`Student -> Educator / Review Panel / Capstone Judge`)
When authoring laboratory reports, design capstones, or technical presentations:
- **Scrubs Chronological Data Dumping**: Students frequently present raw uncurated oscilloscope logs in the order they were captured. The lens restructures this into rigorous scientific hierarchy.
- **Enforces Controlled Variable Discipline**: Explicitly declares independent, dependent, and controlled variables before displaying results.
- **Demands Apparatus Provenance**: Mandates a schematic diagram of the test setup with model numbers and cable impedances.
- **Requires Honest Residual Analysis**: Mandates plotting the mathematical difference between measured data and theoretical curves.

---

## 3. Habitual Student Sender Biases to Scrub

When students author technical reports or presentations, they habitually exhibit distinct structural pitfalls:

| Student Sender Bias | Concrete Manifestation | Quiet UI Remediation Rule |
| :--- | :--- | :--- |
| **Chronological Diary Dumping** | "First we plugged in the cable, then we saw noise, then we adjusted knob 3..." | **Scientific Hypothesis Structure**: Lead with hypothesis and controlled variables; describe setup schematically. |
| **Blind Connecting of Dots** | Drawing straight or jagged lines through scatter points with severe noise. | **Discrete Data Point Rule**: Render raw measurements as discrete glyphs; overlay a smooth curve only if plotting a fitted model. |
| **Missing Dimensional Analysis** | Writing equations with naked numerals ($y = 2.4x + 1.2$) omitting physical units. | **Unit Propagation Rule**: Every constant and coefficient must carry SI units ($2.4\,\text{mV/K}$). |
| **Absence of Error Analysis** | Claiming "the experiment proved the theory 100%" despite 15% scatter. | **Uncertainty Envelope Rule**: Always plot $\pm 1\sigma$ error bars and discuss physical sources of measurement error. |
| **Decorative Visual Distraction** | Adding colorful 3D bar charts or stock photography to technical posters. | **Quiet Visual Focus**: Restrict graphics to high-data-ink schematics and calibrated NIST $1\text{--}2\text{--}5$ plots. |

---

## 4. Receiver Dealbreakers

When a student reviews instructional materials or an instructor reviews a student report, the following four redlines trigger immediate failure:
1. **Uncalibrated Axes**: Plots lacking physical units or using non-standard arbitrary tick sequences (e.g., $0, 3, 7, 11$). Major scales must follow NIST $1\text{--}2\text{--}5$ steps.
2. **Missing Apparatus Schematics**: Discussing electrical, optical, or mechanical measurements without showing the circuit or physical block diagram.
3. **Ambiguous Variable Roles**: Presenting charts where it is impossible to identify which parameter was manipulated and which was measured.
4. **Unannotated Math Walls**: Presenting a block of four consecutive equations without intervening explanatory sentences describing the physical intuition.

---

## 5. Asymmetric Translation Bridges

### 5.1 Senior Engineer -> Student Bridge
- **Engineer Input**:
  > "Set the receiver threshold to $-14\,\text{dBm}$ to avoid BCJR soft demodulator frame dropouts during solar occultation."
- **Student Translation**:
  > "The optical sensor needs a minimum amount of light power to recognize data packets. At $-14\,\text{dBm}$ (about 40 microwatts), the decoder can reliably tell 1s from 0s. If optical power drops below this line—such as when the Sun passes behind the spacecraft—the receiver loses frame lock and data packets are lost."

### 5.2 Student -> Instructor / Capstone Judge Bridge
- **Student Draft**:
  > "We tested the laser detector and it worked pretty well. The graph shows the voltage going up when we turned up the power."
- **Scaffolded Scientific Translation**:
  > "We tested the cryogenic SNSPD receiver across optical power levels from $10\,\text{pW}$ to $1\,\text{nW}$ at $\lambda = 1550\,\text{nm}$. Figure 3 compares discrete count rate measurements against the theoretical quantum efficiency curve ($\eta = 78\%$). Measured saturation at $0.8\,\text{nW}$ matches predicted dead-time paralysis ($t_d = 12\,\text{ns}$)."

---

## 6. Canonical Scientific Lab Report Structure

When generating student-facing or student-authored reports, enforce the canonical five-section scientific macro:

```html
<article class="va-lab-report" aria-label="Experimental Laboratory Report">
  <!-- Section 1: Hypothesis & Mathematical Model -->
  <header class="va-lab-header">
    <span class="va-badge">Laboratory Report &middot; Physics of Optical Telemetry</span>
    <h1 class="va-lab-title">Measurement of Optical Beat Notes and Phase Stability</h1>
    <div class="va-hypothesis-card">
      <strong>Hypothesis:</strong> Dividing the optical beat frequency by N = 2<sup>14</sup> will scale
      picosecond phase drift into the sub-microsecond range, enabling sub-picosecond digital syntonization.
    </div>
  </header>

  <!-- Section 2: Controlled Variables Matrix -->
  <section class="va-variables-grid">
    <div class="va-var-box"><strong>Independent:</strong> Integration Time &tau; (1s to 10<sup>4</sup>s)</div>
    <div class="va-var-box"><strong>Dependent:</strong> Modified Allan Deviation &sigma;<sub>y</sub>(&tau;)</div>
    <div class="va-var-box"><strong>Controlled:</strong> Temperature (293.15 &plusmn; 0.1 K), Optical Power (-14 dBm)</div>
  </section>

  <!-- Section 3: Apparatus Schematic (L1/L2 Topology) -->
  <section class="va-apparatus-section">
    <h2>Apparatus &amp; Measurement Setup</h2>
    <div id="schematic-mount" class="va-schematic-box"></div>
  </section>

  <!-- Section 4: Experimental Data vs Model (L3 Plot) -->
  <section class="va-results-section">
    <h2>Experimental Results &amp; Theoretical Model Fit</h2>
    <div id="plot-results-mount" class="va-plot-box"></div>
  </section>

  <!-- Section 5: Residuals & Error Analysis -->
  <footer class="va-error-analysis">
    <h2>Physical Error Analysis</h2>
    <p>Measured residuals remain within &plusmn;0.12 ps of the theoretical Allan variance model...</p>
  </footer>
</article>
```

---

## 7. The Cognitive Speed Limit Rubric

To ensure technical interfaces do not overwhelm learners, apply the 4-tier cognitive check:

| Check | Threshold Limit | Failure Remediation |
| :--- | :--- | :--- |
| **Novel Term Density** | $\le 3$ new terms per view | Extract secondary terms into collapsible glossary drawer. |
| **Visual Element Hierarchy** | Max 1 primary focal element | De-emphasize secondary charts with muted border tokens. |
| **Formula Step Size** | Max 1 algebraic operation per line | Unroll combined operations into step-by-step lines with explanations. |
| **Interactive Latency** | $< 100\,\text{ms}$ response | Provide instantaneous visual feedback on slider adjustments. |

---

## 8. Verification Checklist for Student Artifacts

- [ ] Clear scientific hypothesis stated before any measurements are presented.
- [ ] Variables categorized into Independent, Dependent, and Controlled groups.
- [ ] Apparatus diagram included with labeled model numbers and port impedances.
- [ ] Raw measurements displayed as discrete glyphs with $\pm 1\sigma$ error bars.
- [ ] Continuous lines reserved strictly for theoretical models or calibrated fits.
- [ ] Physical error analysis explicitly addresses instrument resolution limits.
