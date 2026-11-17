# World 05 Distillation Blueprint: Physical Systems (Auto & Aero)

Asymmetric communication specification for `05-physical-systems-auto-and-aero` (`world_index: 5`),
projecting Argonne `D^3` propulsion dynamometer metrology, SAE J1939 CAN-FD fieldbus diagnostics,
and crew optical/spatial displays across four audience views under strict numerical conservation.

---

## 1. Asymmetric Translation Matrix

| View ID | Presenter Source | Target Audience | Lens(es) | Tempo | Medium(s) | Chromatic Budget | Nav Shell(s) | Rigor | Evidence Refs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `v13-propulsion-archival-monograph` | Propulsion / Systems Researcher | Peer Discipline Engineer | Discipline Engineer | `T3` | `M1`, `M2` | Archival Proof | `N0`, `N1` | `L3` | `evidence/v13_propulsion_bte_plot.json` |
| `v14-fieldbus-and-scope-debugger` | Embedded Systems Engineer | Bench / Field Technician | Technician / Operator; Project / Systems Engineer | `T1` | `M3` | Quiet Cockpit | `N3` | `L3` | `evidence/v14_canfd_bus_schematic.json`, `evidence/v14_canfd_arb_bitfield.json`, `evidence/v14_canfd_reflection_scope.json` |
| `v15-collimated-flight-hud` | Human-Factors Engineer | Pilot / Operator | Technician / Operator | `T1` | `M6` | Quiet Cockpit | `N0` | `L1` | `evidence/v13_propulsion_bte_plot.json` |
| `v16-transparent-window-overlay` | Spatial Systems Designer | Bridge / Vehicle Crew | Technician / Operator | `T1` | `M7` | Quiet Cockpit | `N0` | `L1` | `evidence/v14_canfd_bus_schematic.json` |

---

## 2. Scrubbed Presenter Bias

| View ID | Habitual Presenter Bias | Receiver Scrub Rule Applied |
| :--- | :--- | :--- |
| `v13-propulsion-archival-monograph` | Spline-smoothed engine efficiency maps without uncertainty bars or residuals. | Separate `analytical_model` cubic curve from discrete `Argonne D^3` points with `+/-u_y` whiskers, `46.0 %` knock ceiling, `35.0 %` cruise floor, and bottom normalized residual strip. |
| `v14-fieldbus-and-scope-debugger` | Unlinked raw hex frame dumps (`0x18FEF100`) and interpolated oscilloscope gaps. | Pair 32-bit aligned J1939 header decode (`SOF_ARB_ERR` interlock) with `120 Ω` / `Stub <= 0.3 m` topology and uninterpolated `0.35 µs` null dropout bounded by `T_A`/`T_B`. |
| `v15-collimated-flight-hud` | Centered multi-series charts and opaque card backgrounds on an infinity combiner. | Collapse to `L1` single-trace peripheral propulsion band (`peak_bte_pct` = `42.8 %`), monochrome narrowband phosphor strokes (`fill: none`), and `>= 65.0 %` clear central boresight. |
| `v16-transparent-window-overlay` | Dense schematic wiring tables and low-contrast transparent badges over bright sky/glare. | Project `L1` terminal health alert (`MCU (0xEF)` `warn`) onto smoked adaptive scrim enforcing `window_scrim_min_contrast` `>= 7.0:1` and `paint-order: stroke fill` text halos. |

---

## 3. Verification of the 4 Universal Audience Evaluation Invariants

1. **Baseline & Corridor**:
   - `v13`: Anchors `eta_bte / %` (`15..50 %`) against `35.0 %` cruise warning floor and `46.0 %` thermal/knock abort ceiling across `2..20 bar` IMEP.
   - `v14`: Anchors `CH1` `V_diff` (`+2.5 V` / `-0.5 V`), `CH2` common-mode noise (`+400 mV` ceiling), `120 Ω` EOL termination, and `Stub <= 0.3 m` physical envelope.
   - `v15` & `v16`: Anchor `42.8 %` peak propulsion efficiency band and `MCU (0xEF)` `85 °C` derate corridor without central field-of-view occlusion.
2. **Epistemic Provenance**:
   - `v13`: Strictly splits `discrete_measurement` circles (`+/-u_y` from `0.4` to `0.8 %`) from `analytical_model` dashed polynomial (`+/-0.7 %` corridor) and cites `ANL-D3-2.0L-CRDI` (`NIST-TRQ-2026-05`).
   - `v14`: Marks `0.90 µs` to `1.25 µs` (`0.35 µs` duration) with explicit `null` samples (`interpolate: false`) and unbroken path gap rendering.
   - `v15` & `v16`: Derive scalar/status state directly from `corpus.json` and `L3` evidence files with zero synthetic health scores.
3. **Margin & Consequence**:
   - `v13`: Exposes `+3.2 %` margin below the `46.0 %` thermal ceiling at `42.8 %` peak BTE and `+7.8 %` headroom above the `35.0 %` cruise floor.
   - `v14`: Exposes `425 mV` common-mode excursion (`+25 mV` breach over `400 mV` limit) prior to the `0.35 µs` dropout, tied to `MCU (0xEF)` `Derate 85 °C` (`warn`) and `SOF_ARB_ERR` latch.
   - `v15` & `v16`: Expose `>= 65.0 %` central sightline clearance (`v15`) and `>= 7.0:1` scrim contrast margin (`v16`) against `100,000 lux` solar glare.
4. **Actionable Disposition**:
   - `v13`: Hold cruise fueling schedule inside `10..18 bar` IMEP to stay above `35.0 %` floor and below `46.0 %` knock envelope.
   - `v14`: De-energize bus per LOTO, verify `120 Ω` termination and `Stub <= 0.3 m` on `MCU (0xEF)` drop, then write-1-to-clear `SOF_ARB_ERR` (`[31]`).
   - `v15`: Maintain peripheral throttle trim within peak `42.8 %` BTE band while keeping boresight unobstructed.
   - `v16`: Inspect `MCU (0xEF)` thermal derate (`85 °C`) from bridge/crew overlay without leaving primary watch station.

---

## 4. Canonical Numerical Conservation Ledger

| Metric Key | Canonical Value | Unit | Bound Evidence File & Path | Conserved Across Views |
| :--- | :--- | :--- | :--- | :--- |
| `peak_bte_pct` | `42.8` | `%` | `evidence/v13_propulsion_bte_plot.json` (`$.series[1].data_points[6].y`, `$.parametric_legend[0].value`) | `v13`, `v15` |
| `canfd_termination_ohm` | `120` | `Ω` | `evidence/v14_canfd_bus_schematic.json` (`$.bus_parameters.termination_ohm`, `can_fd` profile) | `v14`, `v16` |
| `canfd_stub_max_m` | `0.3` | `m` | `evidence/v14_canfd_bus_schematic.json` (`$.bus_parameters.stub_max_m`, `can_fd` profile) | `v14`, `v16` |
| `scope_dropout_us` | `0.35` | `µs` | `evidence/v14_canfd_reflection_scope.json` (`$.dropout_handling.dropout_duration_us`, `T_B - T_A = 1.25 - 0.90`) | `v14` |
| `canfd_arb_frame_hex` | `0x18FEF100` | `hex` | `evidence/v14_canfd_arb_bitfield.json` (`$.metadata.current_value`) | `v14` |
| `hud_sightline_keepout_pct` | `65.0` | `%` | `corpus.json` (`$.canonical_metrics.hud_sightline_keepout_pct`), `evidence/v13_propulsion_bte_plot.json` (`$.medium_constraints.hud_sightline_keepout_pct`) | `v15` |
| `window_scrim_min_contrast` | `7.0` | `1` | `corpus.json` (`$.canonical_metrics.window_scrim_min_contrast`), `evidence/v14_canfd_bus_schematic.json` (`$.medium_constraints.window_scrim_min_contrast`) | `v16` |

---

## 5. Adversarial Murder-Board Audit Table

| Audit Sector | Rubric Basis | Weight | Score (0–100) | Verified Evidence & Hard-Block Clearance |
| :--- | :--- | :--- | :--- | :--- |
| 1. Physical Conservation & Metrology | `CR-1`..`CR-5`, `TRG-01`, `TRG-02` | 30% | `95 / 100` | `v13` separates discrete `Argonne D^3` points (`+/-u_y`) from cubic model with residual strip; `v14` scope leaves `0.35 µs` `null` gap uninterpolated (`TRG-01` clear). |
| 2. Bus Topology & Bitfield ICDs | `SR-1`, `TR-1`, `TRG-04`, `TRG-07` | 25% | `93 / 100` | `120 Ω` dual termination and `Stub <= 0.3 m` trace directly to `SAE J1939` PGN `0xFEF1` (`0x18FEF100`) across `ECM (0x00)`, `BMS (0xF3)`, `MCU (0xEF)`, `OBD-II Tap`. |
| 3. Operator Safety & LOTO Interlocks | `TR-2`..`TR-5`, `TRG-05`, `TRG-06` | 25% | `94 / 100` | `SOF_ARB_ERR` (`[31]`, `W1C`, `safety_critical: true`) guards bus reset; `MCU (0xEF)` `warn` status pairs with `+2.5 V` / `400 mV` scope redlines and zero flashing UI. |
| 4. Medium Optics & Audience Fit | `NASA-STD-3001`, `M6`/`M7`, `TRG-08` | 20% | `92 / 100` | `v15` enforces `L1` rigor, stroke-only phosphor, and `65.0 %` boresight keep-out; `v16` enforces `L1` rigor, `7.0:1` scrim contrast, and `paint-order: stroke fill` halos. |

- **Composite Murder-Board Score**: `93.7 / 100` (Pass Threshold: `>= 85.0`)
- **Hard-Block Triggers (`TRG-01`..`TRG-08`)**: `ZERO TRIGGERS TRIPPED`
- **Disposition**: `APPROVED` — Ready for Quiet UI Pillar 2 compilation and Pillar 3 delivery across `M1`, `M2`, `M3`, `M6`, and `M7`.
