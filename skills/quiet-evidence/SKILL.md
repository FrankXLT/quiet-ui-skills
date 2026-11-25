---
name: quiet-evidence
description: Quantitative data metrology and structural topology skill compiling NIST 1-2-5 plots, bitfields, HIL waveforms, and MIL-STD schematics from deterministic JSON schemas.
---

# Quiet UI Pillar 2 (`v9.7.0`) — Unified Quantitative Evidence & Metrology

Quiet UI Pillar 2 governs data fidelity, unit calculus, scale intervals, and physical topology across six modalities and a three-level rigor continuum (`L1 · Orientation`, `L2 · Governance`, `L3 · Physical, Clinical & Metrological`).

---

## 1. The 6-Invariant Pre-Evidence Reasoning Contract

Before compiling or generating any quantitative visual, complete the [Data-to-Widget Binding Map](../quiet-ui/foundation/data-grounding-and-widget-binding.md) (omit absent targets/baselines, use trackless `.va-kpi-card` for unbounded totals, never hardcode inline demo/JSON mock fixtures, evaluate pricing comparisons per `effective_from` epoch, and disclose `Warming up — N samples collected` when `N < 10`) and verify all physical invariants:
1. **Governing Relationship / Equation**: Declare the physical model, transfer function, or algebraic relation governing the series.
2. **NIST Quantities & SI Units**: Enforce NIST SP 811 quantity calculus (`Quantity / Unit`). Label all axes and parameters with explicit units.
3. **Scale Steps & Bounds**: Major ticks must follow $1\text{--}2\text{--}5 \times 10^n$ steps or integer log decades. Minor log ticks ($2\dots 9$) are mandatory on log scales.
4. **Trace Epistemology**: Measured physical data points MUST use discrete geometric markers. Analytical models MUST use continuous curves. Never connect discrete points with arbitrary Bezier splines.
5. **Limit, Abort & Label-Clearance Envelopes**: Operational ceilings, abort boundaries, and confidence corridors ($\pm 1\sigma$, $95\%\,\text{CI}$) must be explicitly demarcated with haloed labels; never grade prior runs retroactively without an effective-date annotation. Visible `<text>` labels across `1440px`, `900px`, and `390px` MUST maintain `>= 6px` clearance from non-grid plotted curves/polylines unless enclosed in an opaque `<rect>` badge plate (`[SVG_LABEL_STROKE_COLLISION]`).
6. **Grayscale & Dash Redundancy**: Multi-series plots must be distinguishable by stroke dash pattern or marker glyph in pure black-and-white print.
7. **Cross-Plot Axis, Time Binning & Spine Registration**: Co-displayed plots MUST bin dense series cleanly (`QuietEChartsDefaults.binTimeSeries` -> `1h` `<= 3d`, `1d` `4–92d`, ISO `1w` `> 92d`), use wide-script/CJK-aware `measureCategoryGutter` (`visualUnits` `1.75x` fullwidth + combining-mark exclusion, `mono` detection, `axisLabelMargin`), align column `[x_left, x_right]` / row `[y_top, y_bottom]` `containLabel: false` pixel spines (`computeGridFrameGutters` / `alignPlotGridFrames`), and lock shared `1–2–5` Y ceilings per unit (`sharedNiceScale125`) — auto-enabling `independentXSpan` across disparate X formats (`YYYY-MM-DD` vs. `00h..23h`).
8. **Chart Form by Category Count (`N`) & Cyclical Anti-Sum Rule**: `N <= 3` categories render as stat strips or micro-bars (`<= 72px`); `N <= 8` comparisons use `.va-inline-bar` bullet tables (`<= 32px`/row); composite `[Chart + Table]` cards stay 1-column full-width. For cyclical hour/weekday/month cadences, never sum raw totals across days—plot active-day `Min–Max` range whiskers + `Active Avg` bar + `Recent` marker via `QuietEChartsDefaults.buildCyclicalWhiskerOption` (`"Activity by Hour of Day"`, never jargon `"diurnal"`, `[JARGON_TERMINOLOGY]`).
9. **Civic & Research Storytelling Forms (`us_hex_tile_map`, `arrow_dumbbell`, `paired_subgroup_bars`, `dual_slopegraph`, `diverging_matrix`)**: Wrap public-data cards via 4-part Takeaway Figure Cards with `[Chart | Table]`, `Copy data` TSV, `Copy for AI` Markdown, luminance-adaptive ink, unit-once top slope rows, step-leader right gutters (`[END_LABEL_CLIP]`), and unshaded `$` levels beside diverging `%` tints.

> [!IMPORTANT]
> **Hard Ban on Freehand SVG Guessing**: LLMs MUST NOT guess SVG coordinate numbers freehand. Author `urn:quiet-ui:schema:v9:<modality>` JSON via `compile_evidence.py`, or route dynamic browser plots through bundled `window.QuietSvgLayout` and `QuietEChartsDefaults` (`quiet-evidence-bundle.js`).

---

## 2. Progressive-Disclosure Architecture & File Router

Load ONLY the specific rigor and modality guides matching your active visualization:

### Rigor & Metrology Standards
- [rigor/metrology-and-nist-units.md](rigor/metrology-and-nist-units.md): NIST SP 811 unit calculus, SI prefixes, Roman vs. italic symbols, significant figures, and cross-plot unit/event span rules.
- [rigor/scales-ticks-and-uncertainty.md](rigor/scales-ticks-and-uncertainty.md): NAVAIR FTM-108 $1\text{--}2\text{--}5$ intervals, minor log ticks, $\pm 1\sigma$ corridors, dropout gaps, and interpolation grids.
- [rigor/conditions-and-envelopes.md](rigor/conditions-and-envelopes.md): Test-condition headers, discrete test markers vs. model curves, limit envelopes, and stroke halos.
- [rigor/ecosystem-adapters.md](rigor/ecosystem-adapters.md): `window.QuietSvgLayout` (`buildCanonicalTimeGrid`, `sharedNiceScale125`, `computeGridFrameGutters`, wide-script/CJK `visualUnits` + `measureCategoryGutter`), `QuietEChartsDefaults` (`binTimeSeries`, `buildCyclicalWhiskerOption`, `alignPlotGridFrames`, `alignSharedAxes`, separate parent/breakdown `yUnit` spans, `applySafeLegendLayout`), Plotly, Matplotlib, Bokeh, and Mermaid.

### The 6 Visual Modalities
- [modalities/scalar-readouts-and-gauges.md](modalities/scalar-readouts-and-gauges.md): Scalar readouts, trackless `.va-kpi-card` unbounded totals vs. `.va-kpi-gauge-card` bounded shares, dynamic gauges, and status pills.
- [modalities/tables-and-matrices.md](modalities/tables-and-matrices.md): Structured tabular data, PPSM matrices, correlation heatmaps, and disposition memos.
- [modalities/bitfields-and-registers.md](modalities/bitfields-and-registers.md): 16/32/64-bit hardware register maps, memory offsets, and bitfield boundary allocations.
- [modalities/analytical-and-spectral-plots.md](modalities/analytical-and-spectral-plots.md): Allan deviation, Bode frequency plots, Weibull reliability, and multi-series curves.
- [modalities/waveforms-and-timing.md](modalities/waveforms-and-timing.md): Multi-channel HIL scopes, bus timing diagrams, cursor readouts, and dropout gap handling.
- [modalities/schematics-and-topologies.md](modalities/schematics-and-topologies.md): Architecture delta lanes, ATO trust enclaves, MIL-STD-1553B buses, P&ID loops, and Crow's-foot schemas.

---

## 3. CLI & Python API Usage

Compile any `urn:quiet-ui:schema:v9:<modality>` JSON spec directly from `~/.agents/skills/quiet-evidence/` (or prefix `skills/quiet-evidence/` from the repo root) with zero third-party dependencies (`assets/quiet-evidence-bundle.{css,js}` includes `window.QuietSvgLayout` for dynamic browser charts):

```bash
# Write a portable self-contained HTML5 document (uses bundled CSS, QuietSvgLayout & scope runtime)
python3 -B scripts/compile_evidence.py spec.json --rigor L3 --theme white --out chart.html

# Emit an embeddable HTML/SVG <figure> fragment to stdout
python3 -B scripts/compile_evidence.py spec.json --rigor L2 --medium m3 --fragment
```

```python
from compile_evidence import compile_spec
html_doc = compile_spec("spec.json", rigor="L3", medium="m2", theme="dark", standalone=True)
```

---

## 4. Integration with Complementary Pillars
- **Delivery Mediums & Chromatic Budgets**: Consult [quiet-ui](../quiet-ui/SKILL.md) to wrap compiled visuals in calibrated medium shells.
- **Audience Translation & Lenses**: Consult [quiet-bridge](../quiet-bridge/SKILL.md) to select the appropriate level of rigor (`L1`, `L2`, or `L3`) for the intended audience.
