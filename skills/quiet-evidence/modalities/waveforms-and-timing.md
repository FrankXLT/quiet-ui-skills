# Modality: Waveforms and Timing Scopes

Multi-channel Hardware-In-The-Loop (HIL) oscilloscopes, digital bus analyzers, and clock-domain timing diagrams capture transient dynamics, edge jitter, and protocol handshakes.

---

## 1. Visual Anatomy & Multi-Channel Trace Stacking

Quiet UI waveform visualizers vertically stack synchronized analog and digital channels against a unified horizontal timebase:

```
+-----------------------------------------------------------------------+
| TIMEBASE: 2.00 µs/div | SAMPLE RATE: 2.50 GS/s | TRIGGER: CH1 RISING  |
+-----------------------------------------------------------------------+
| CH1: Optical Phase Residual (mrad)                   0.0 mrad --------|
|   |---/\------/\-----------------/\-----------------------------------|
+-----------------------------------------------------------------------+
| CH2: BCJR Soft Metric (LLR)                          0.0 LLR ---------|
|   |=====|====|====\_____________/=====================================|
+-----------------------------------------------------------------------+
| CH3: Feedback Error Voltage (mV)                    +15.0 mV --------|
|   |~~~~~~~~~~~~\________________/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
+-----------------------------------------------------------------------+
| CH4: Master Clock Gate Enable (Digital)                               |
|   |____|‾‾‾‾‾‾‾‾|____|‾‾‾‾‾‾‾‾|____|‾‾‾‾‾‾‾‾|____|‾‾‾‾‾‾‾‾|___________|
+-----------------------------------------------------------------------+
| CURSOR READOUT: t_A = 12.40 µs | t_B = 18.85 µs | Δt = 6.45 µs (155 kHz)|
+-----------------------------------------------------------------------+
```

---

## 2. The Rigor Continuum Progression Table

Waveform scopes adapt their channel complexity and cursor metrology across the three rigor levels:

| Rigor Level | Target Audience | Primary Focus | Scope Mechanics & Display Depth |
| :--- | :--- | :--- | :--- |
| **L1 Orientation** | High-Level Systems Operator | Bus activity & operational health | Single composite activity trace, eye-diagram mask pass/fail badge, cycle duration overview, zero complex time cursors. |
| **L2 Governance** | Hardware Quality Engineer, Systems Integrator | Protocol specification & setup/hold margins | Bus transaction decoded states, setup and hold margin bars, timing violation flags, contractual delay budgets. |
| **L3 Physical / Metrological** | Silicon Validation Engineer, DSP/RF Specialist | Physical analog signals & cursor timing proof | Multi-channel synchronized analog/digital channels, dual time cursors ($t_A, t_B, \Delta t, 1/\Delta t$), discrete sample pips, dropout gaps, and raw voltage calibrations. |

---

## 3. Universal Schema: `urn:quiet-ui:schema:v9:waveform`

All multi-channel scope captures must validate against the offline Quiet UI waveform schema:

```json
{
  "$schema": "urn:quiet-ui:schema:v9:waveform",
  "id": "scope-hil-quad-channel-capture-01",
  "metadata": {
    "title": "Quad-Channel HIL Optical Receiver Demodulation",
    "description": "High-speed optical receiver timing, carrier recovery, and error feedback",
    "rigor_level": "L3",
    "timestamp_utc": "2026-11-16T19:30:00Z"
  },
  "timebase": {
    "quantity": "t",
    "quantity_calculus": "t / µs",
    "unit": "µs",
    "sample_rate_hz": 2500000000.0,
    "time_per_division_us": 2.0,
    "total_span_us": 20.0,
    "trigger": {
      "channel_id": "ch1",
      "edge": "rising",
      "threshold_value": 0.0,
      "position_pct": 20.0
    }
  },
  "cursors": {
    "cursor_a": {
      "id": "cur-a",
      "time_us": 12.40,
      "label": "T_A",
      "stroke_color": "var(--tint-violet-fg)"
    },
    "cursor_b": {
      "id": "cur-b",
      "time_us": 18.85,
      "label": "T_B",
      "stroke_color": "var(--accent-primary)"
    },
    "delta_readout": {
      "delta_t_us": 6.45,
      "equivalent_frequency_khz": 155.038,
      "unit": "µs"
    }
  },
  "channels": [
    {
      "id": "ch1",
      "name": "Optical Phase Residual",
      "type": "analog",
      "quantity_calculus": "Delta_phi / mrad",
      "unit": "mrad",
      "vertical_scale_per_div": 25.0,
      "vertical_offset": 0.0,
      "trace_color": "var(--accent-focal)",
      "sample_count": 50000,
      "threshold_envelopes": [
        {"type": "upper_abort", "value": 65.0, "color": "var(--status-danger)"},
        {"type": "lower_abort", "value": -65.0, "color": "var(--status-danger)"}
      ]
    },
    {
      "id": "ch2",
      "name": "BCJR Soft Metric LLR",
      "type": "analog",
      "quantity_calculus": "Lambda_LLR",
      "unit": "1",
      "vertical_scale_per_div": 2.0,
      "vertical_offset": 0.0,
      "trace_color": "var(--status-ok)"
    },
    {
      "id": "ch3",
      "name": "Feedback Error Voltage",
      "type": "analog",
      "quantity_calculus": "V_err / mV",
      "unit": "mV",
      "vertical_scale_per_div": 50.0,
      "vertical_offset": 0.0,
      "trace_color": "var(--status-warn)"
    },
    {
      "id": "ch4",
      "name": "Master Clock Gate Enable",
      "type": "digital",
      "logic_high_label": "ASSERTED",
      "logic_low_label": "DEASSERTED",
      "trace_color": "var(--text-primary)"
    }
  ],
  "dropout_handling": {
    "detection_multiplier": 1.5,
    "interpolate": false,
    "unroll_on_print": true
  }
}
```

---

## 4. Multi-Channel Vertical Stacking & Channel Alignment

Waveform displays must adhere to three mechanical alignment laws:

1. **Rigid Shared Timebase**: All channels in a stack share an identical horizontal coordinate projection. A cursor line dropped at time $t$ passes vertically through all channels simultaneously.
2. **Zero-Baseline Anchoring**: Every analog channel displays an explicit zero-reference indicator (left-hand marker `0-▶`) to prevent ambiguous vertical offset perception.
3. **Trace Stroke Separation**: Analog traces use continuous $1.5\ \mathrm{px}$ strokes; digital logic channels use hard step transitions (`step-after`) with $1.0\ \mathrm{px}$ bounding strokes.

---

## 5. Interactive Scrub vs. Static Print Unrolling

### Medium M1: Precision Static Print & PDF
- **Multi-Row Unrolling**: When a capture spans long time horizons (e.g., $100\ \mu\mathrm{s}$), the compiler automatically unrolls the waveform into multiple stacked sub-windows (e.g., $0\dots 25\ \mu\mathrm{s}$, $25\dots 50\ \mu\mathrm{s}$) so micro-features remain distinguishable.
- **Printed Cursor Box**: Dual cursors are rendered as vertical dashed rules ($t_A, t_B$) with a tabular cursor delta block printed directly above the graticule.

### Medium M3: Stateful Web Application
- **Interactive Scrubber & Zoom**: Users can pan along the timeline using drag handles or mouse wheel zoom.
- **Dynamic Cursors**: Cursors $t_A$ and $t_B$ can be dragged across the display, updating the floating delta readout ($\Delta t, \Delta V, 1/\Delta t$) at $60\ \mathrm{fps}$.
- **FFT Spectrum Drawer**: Clicking any analog channel header slides out an instant Power Spectral Density (PSD) plot computed via clientside WebAssembly FFT.

### Medium M6: Optical HUD & Tactile Console
- **Continuous Rolling Scope**: Renders the latest 1024 samples with an active phosphor sweep bar and exponential decay trail.
- **Tripwire Threshold Flash**: Crossing a channel envelope triggers a border pulse on that channel strip without interrupting display refresh.

---

## 6. Verification Checklist

Before emitting SVG markup or Canvas paths:
- [ ] Conforms to schema URI `urn:quiet-ui:schema:v9:waveform`.
- [ ] Rigor progression table matches the audience (L1 activity vs L3 dual cursor metrology).
- [ ] Timebase and all channels carry explicit NIST SP 811 quantity units.
- [ ] Zero interpolation across telemetry dropouts (gaps remain open).
- [ ] Dual cursor delta includes both $\Delta t$ and reciprocal frequency $1/\Delta t$.

---

## 7. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [../rigor/metrology-and-nist-units.md](../rigor/metrology-and-nist-units.md)
- Scales & Uncertainty: [../rigor/scales-ticks-and-uncertainty.md](../rigor/scales-ticks-and-uncertainty.md)
- Bitfields & Registers Modality: [bitfields-and-registers.md](bitfields-and-registers.md)
- Analytical Plots Modality: [analytical-and-spectral-plots.md](analytical-and-spectral-plots.md)
- Delivery Mediums: [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md)
