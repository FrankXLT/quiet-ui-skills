---
name: quiet-evidence
description: Quantitative data metrology and structural topology skill compiling NIST 1-2-5 plots, bitfields, HIL waveforms, and MIL-STD schematics from deterministic JSON schemas.
---

# Quiet UI Pillar 2 — Unified Quantitative Evidence & Metrology

Quiet UI Pillar 2 governs data fidelity, unit calculus, scale intervals, and physical topology across six modalities and a three-level rigor continuum (`L1 · Orientation`, `L2 · Governance`, `L3 · Physical, Clinical & Metrological`).

---

## 1. The 6-Invariant Pre-Evidence Reasoning Contract

Before compiling or generating any quantitative visual, complete the [Data-to-Widget Binding Map](../quiet-ui/foundation/data-grounding-and-widget-binding.md) (omit absent targets/baselines, never hardcode inline demo arrays, and disclose `Warming up — N samples collected` when `N < 10`) and verify all six physical invariants:
1. **Governing Relationship / Equation**: Declare the physical model, transfer function, or algebraic relation governing the series.
2. **NIST Quantities & SI Units**: Enforce NIST SP 811 quantity calculus (`Quantity / Unit`). Label all axes and parameters with explicit units.
3. **Scale Steps & Bounds**: Major ticks must follow $1\text{--}2\text{--}5 \times 10^n$ steps or integer log decades. Minor log ticks ($2\dots 9$) are mandatory on log scales.
4. **Trace Epistemology**: Measured physical data points MUST use discrete geometric markers. Analytical models MUST use continuous curves. Never connect discrete points with arbitrary Bezier splines.
5. **Limit & Abort Envelopes**: Operational ceilings, abort boundaries, and confidence corridors ($\pm 1\sigma$, $95\%\,\text{CI}$) must be explicitly demarcated with haloed labels; never grade prior runs retroactively without an effective-date annotation.
6. **Grayscale & Dash Redundancy**: Multi-series plots must be distinguishable by stroke dash pattern or marker glyph in pure black-and-white print.

> [!IMPORTANT]
> **Hard Ban on Freehand SVG Guessing**: LLMs MUST NOT guess SVG coordinate numbers freehand. Author `urn:quiet-ui:schema:v9:<modality>` JSON via `compile_evidence.py`, or route dynamic browser SVGs through bundled `window.QuietSvgLayout` (`quiet-evidence-bundle.js`).

---

## 2. Progressive-Disclosure Architecture & File Router

Load ONLY the specific rigor and modality guides matching your active visualization:

### Rigor & Metrology Standards
- [rigor/metrology-and-nist-units.md](rigor/metrology-and-nist-units.md): NIST SP 811 unit calculus, SI prefixes, Roman vs. italic symbols, significant figures, and parameter blocks.
- [rigor/scales-ticks-and-uncertainty.md](rigor/scales-ticks-and-uncertainty.md): NAVAIR FTM-108 $1\text{--}2\text{--}5$ intervals, minor log ticks, $\pm 1\sigma$ corridors, dropout gaps, and interpolation grids.
- [rigor/conditions-and-envelopes.md](rigor/conditions-and-envelopes.md): Test-condition headers, discrete test markers vs. model curves, limit envelopes, and stroke halos.
- [rigor/ecosystem-adapters.md](rigor/ecosystem-adapters.md): Standards-compliant `window.QuietSvgLayout` SVG helpers, Apache ECharts (`containLabel: true` + haloed `markLine`), Plotly, Matplotlib, Bokeh, and Mermaid.

### The 6 Visual Modalities
- [modalities/scalar-readouts-and-gauges.md](modalities/scalar-readouts-and-gauges.md): Scalar readouts, single-value callouts, dynamic gauges, and status annunciator pills.
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
