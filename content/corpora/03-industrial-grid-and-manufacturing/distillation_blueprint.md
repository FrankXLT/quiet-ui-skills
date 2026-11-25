# World 03 Distillation Blueprint — Industrial Grid SCADA & Manufacturing Quality

This blueprint governs asymmetric presenter-to-audience translation, bias scrubbing, numerical conservation, and adversarial Murder-Board auditing across all three views of **World 03 (`03-industrial-grid-and-manufacturing`)**.

---

## 1. Presenter-to-Audience Matrix

| View ID | Presenter Source | Target Audience | Lenses | Tempos | Mediums | Chromatic Budget | Nav Shell | Rigor | Bound Evidence Specs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `v07-grid-scada-poi-console` | Grid Controls Engineer | Control Room Operator | Technician / Operator | `T1` | `M4` | Quiet Cockpit | `N3` | `L3` | `v07_grid_scada_pid_and_bus.json`, `v07_synchrophasor_scalars.json` |
| `v08-plant-floor-wall-kiosk` | Plant Operations | Line Crew & Facility Visitors | Technician / Operator, Consumer / Common Reader | `T1` | `M5` | Quiet Cockpit | `N0` | `L1` | `v07_synchrophasor_scalars.json` |
| `v09-spc-quality-and-modbus-report` | Quality Engineer | Line Lead & Plant Manager | Discipline Engineer, Program Manager | `T2`, `T3` | `M1`, `M2` | Decision Contrast | `N2` | `L3` | `v09_spc_control_plot.json`, `v09_modbus_plc_bitfield.json` |
| `v25-subsea-corridor-and-link-margin` | Subsea Optical Engineer | Marine Network Operations | Discipline Engineer, Technician / Operator | `T2`, `T3` | `M3` | Quiet Cockpit | `N2` | `L3` | `v25_subsea_osnr_plot.json`, `v25_subsea_corridor_table.json` |

---

## 2. Scrubbed Presenter Bias & Intake Contract Freeze

- **From `v07-grid-scada-poi-console` (Controls Engineer -> Control Room Operator)**:
  - *Scrubbed*: Decorative 3D turbine animations, rainbow status badges on nominal equipment, uncalibrated percentages without SI units, and single-click unguarded breaker trips.
  - *Retained*: `ISA-101` / `NRC NUREG-0700` monochrome nominal Quiet Cockpit surface, `ISA-5.1` P&ID tags (`FCV-101`, `FT-101`, `TT-102`, `PT-204`, `XI-301`), `120 Ω` RS-485/Modbus RTU trunk wiring, and `CMD vs ACT` linear gauges.
- **From `v08-plant-floor-wall-kiosk` (Plant Operations -> Line Crew & Facility Visitors)**:
  - *Scrubbed*: Raw hexadecimal Modbus register dumps (`0x0104`), `C_pk` statistical calculus, and dense P&ID loop numbers unreadable at 10 feet.
  - *Retained*: `L1` Orientation scalar tiles (`23.6 MW`, `59.985 Hz`, `78.4 %`, `94.2 %`) with calm `[ NOMINAL ]` non-color-only pills and micro-trend sparklines on an undecorated `N0` `M5` wall stage.
- **From `v09-spc-quality-and-modbus-report` (Quality Engineer -> Line Lead & Plant Manager)**:
  - *Scrubbed*: Bare pass/fail batch percentages that mask process centering drift, Bezier-smoothed curves lacking discrete subgroup points, and unverified interlock assumptions.
  - *Retained*: Full `NIST/SEMATECH SPC` Shewhart `X_bar` control chart (`C_pk = 1.64`, `n = 5`, `±u_y` whiskers, residual strip) paired with the exact 16-bit `PLC_BREAKER_INTERLOCK_WORD` (`0x0104` = `0x0A15`) decode ledger.
- **From `v25-subsea-corridor-and-link-margin` (Subsea Engineer -> Marine Operations)**:
  - *Scrubbed*: Unscaled cartoon cable maps that detach bathymetric slope hazards from repeater optical OSNR margin degradation.
  - *Retained*: Distance-locked `0–640 km` 2D seabed corridor (`BU-03` at `240 km`, `Span S5` `+4.8 dB` anchor fault at `362 km` `-1420 m`) directly above the aligned `OSNR` link-margin curve (`16.4 dB` vs `15.0 dB` SD-FEC floor) and `1.12 A` constant-current ledger.

---

## 3. The 4 Universal Audience Evaluation Invariants

1. **Baseline & Corridor**: Every readout and series is anchored to calibrated operating envelopes—grid frequency `60.000 Hz` (`±0.05 Hz` warn / `±0.10 Hz` abort), BESS dispatch `24.0 MW`, Shewhart `X_bar` bounds (`USL = 10.070 mm`, `CL = 10.000 mm`, `LSL = 9.930 mm`), and subsea SD-FEC floor (`15.0 dB` across `640 km`).
2. **Epistemic Provenance**: Discrete SPC subgroup points carry explicit `±u_y` uncertainty whiskers and `circle` markers while `CL = 10.000 mm` uses a dashed `analytical_model` line; subsea Coherent OTDR OSNR samples bind `8` wet-plant repeaters and depth profiles to shared `km` stations.
3. **Margin & Consequence**: Headroom is visible without mental arithmetic via `CMD vs ACT` pins (`24.0 MW` vs `23.6 MW`; `60.000 Hz` vs `59.985 Hz`), `C_pk = 1.64`, and `+1.4 dB` subsea OSNR margin (`16.4 dB` vs `15.0 dB` floor).
4. **Actionable Disposition**: Non-color-only `[ NOMINAL ]` / `[ WARN ]` pills and explicit interlock tags (`ISLAND_ARMED = 1`, `LOTO = 0`, `Span S5` `+4.8 dB` ROV dispatch) bind live plant state to guarded operator actions.

---

## 4. Canonical Conservation Ledger

Every number in `corpus.json["canonical_metrics"]` is conserved identically across the compiled `evidence/*.json` specifications and this blueprint:

| Canonical Metric ID | Conserved Value | SI / Protocol Unit | Tolerance / Envelope | Bound Evidence File(s) |
| :--- | :--- | :--- | :--- | :--- |
| `bess_power_cmd_mw` | `24.0` | `MW` | Target setpoint | `v07_grid_scada_pid_and_bus.json`, `v07_synchrophasor_scalars.json` |
| `bess_power_act_mw` | `23.6` | `MW` | `± 0.1 MW` (`k = 2.0`), abort `[18.0, 27.0]` | `v07_grid_scada_pid_and_bus.json`, `v07_synchrophasor_scalars.json` |
| `grid_freq_cmd_hz` | `60.000` | `Hz` | Nominal reference | `v07_synchrophasor_scalars.json` |
| `grid_freq_hz` | `59.985` | `Hz` | `± 0.005 Hz` (`k = 2.0`), abort `[59.90, 60.10]` | `v07_grid_scada_pid_and_bus.json`, `v07_synchrophasor_scalars.json` |
| `bess_soc_pct` | `78.4` | `%` | `± 0.5 %` (`k = 2.0`), abort `[10.0, 96.0]` | `v07_grid_scada_pid_and_bus.json`, `v07_synchrophasor_scalars.json` |
| `oee_yield_pct` | `94.2` | `%` | `± 0.4 %` (`k = 2.0`), warn `88.0 %` | `v07_synchrophasor_scalars.json` |
| `bus_impedance_ohm` | `120` | `Ω` | TIA-485 EOL + `560 Ω` bias | `v07_grid_scada_pid_and_bus.json` |
| `spc_cl_mm` | `10.000` | `mm` | Target centerline `CL` | `v09_spc_control_plot.json` |
| `spc_ucl_mm` | `10.042` | `mm` | `+3 sigma` control limit | `v09_spc_control_plot.json` |
| `spc_lcl_mm` | `9.958` | `mm` | `-3 sigma` control limit | `v09_spc_control_plot.json` |
| `spc_usl_mm` | `10.070` | `mm` | Upper spec abort ceiling | `v09_spc_control_plot.json` |
| `spc_lsl_mm` | `9.930` | `mm` | Lower spec abort floor | `v09_spc_control_plot.json` |
| `spc_cpk` | `1.64` | `1` | Minimum gate `>= 1.33` | `v09_spc_control_plot.json` |
| `spc_subgroup_size` | `5` | `1` | Subgroup sample size `n` | `v09_spc_control_plot.json` |
| `modbus_reg_addr` | `0x0104` | `hex` | Holding Register offset | `v07_grid_scada_pid_and_bus.json`, `v09_modbus_plc_bitfield.json` |
| `modbus_reg_value` | `0x0A15` | `hex` | `ISLAND_ARMED = 1`, `LOTO = 0` | `v09_modbus_plc_bitfield.json` |
| `subsea_trunk_length_km` | `640` | `km` | `CLS-Alpha` (`0`) to `CLS-Bravo` (`640`) | `v25_subsea_osnr_plot.json`, `v25_subsea_corridor_table.json` |
| `subsea_repeater_count` | `8` | `1` | Active repeaters `R1-R8` | `v25_subsea_osnr_plot.json`, `v25_subsea_corridor_table.json` |
| `subsea_fault_excess_loss_db` | `4.8` | `dB` | Anchor fault on `Span S5` (`362 km`) | `v25_subsea_corridor_table.json` |
| `subsea_min_osnr_db` | `16.4` | `dB` | Minimum channel OSNR (`+1.4 dB` margin) | `v25_subsea_osnr_plot.json`, `v25_subsea_corridor_table.json` |
| `subsea_fec_floor_db` | `15.0` | `dB` | SD-FEC abort threshold | `v25_subsea_osnr_plot.json` |
| `subsea_line_feed_a` | `1.12` | `A` | Constant current PFE trunk feed | `v25_subsea_corridor_table.json` |

---

## 5. Adversarial Murder-Board Audit Table

| Audit Gate / Trigger | Target View(s) | Red-Team Adversarial Challenge | Verification Evidence & Disposition |
| :--- | :--- | :--- | :--- |
| **MF-1 / TRG-12** (`SPC Capability Masking`) | `v09` | Does the quality report mask process drift behind a bare yield percentage? | **PASS**: `v09_spc_control_plot.json` exposes `C_pk = 1.64`, `n = 5`, `UCL 10.042 mm`, `CL 10.000 mm`, `LCL 9.958 mm`, `USL 10.070 mm`, `LSL 9.930 mm`, and normalized residuals. |
| **MF-2 / TRG-05** (`ISA-101 Quiet Cockpit`) | `v07`, `v08` | Do passive backgrounds or nominal readouts leak high-chroma amber/crimson or flashing widgets? | **PASS**: Both `v07` and `v08` bind `Quiet Cockpit`; nominal states use calm monochrome surfaces and non-color-only `[ NOMINAL ]` pills. |
| **TRG-01** (`Discrete vs. Spline Fit`) | `v09` | Are discrete subgroup means smoothed with cubic Bezier splines instead of discrete markers? | **PASS**: `epistemic_type: discrete_measurement` renders `circle` markers with `±u_y` error whiskers and piecewise straight chords only. |
| **TRG-06 / TR-4** (`LOTO & Modbus Interlock`) | `v07`, `v09` | Can a breaker close/island command execute without explicit LOTO and `ISLAND_ARMED` bit verification? | **PASS**: `v09_modbus_plc_bitfield.json` decodes `0x0104 = 0x0A15` with `safety_critical: true` on `ISLAND_ARMED`, `LOTO_LOCKOUT_ACTIVE`, `ESTOP_TRIP_LATCH`, and `BREAKER_TRIP_CMD`. |
| **TRG-08** (`Audience Mismatch`) | `v08`, `v09` | Are wall-kiosk visitors exposed to hex dumps, or discipline engineers given unitless blobs? | **PASS**: `v08` projects at `L1` (`N0` / `M5`) with plain scalars and sparklines; `v09` projects at `L3` (`M1` / `M2`) with NIST SP 811 units and bit-level decode tables. |
| **TRG-02 / SR-3** (`Corridor X-Scale Lock`) | `v25` | Does the bathymetric fault marker at `362 km` align pixel-for-pixel with the OSNR trough (`16.4 dB`) and `15.0 dB` FEC floor? | **PASS**: Both panels and the 10-row repeater ledger synchronize across `[0, 640 km]` with span filter highlighting and conserve `640`, `8`, `4.8`, `16.4`, `15.0`, `1.12`. |
| **CR-1 / CR-5** (`Conservation & Calibration`) | `v07`, `v08`, `v09`, `v25` | Do any values drift across views, or lack calibration IDs and `k = 2.0` uncertainty? | **PASS**: All canonical metrics match identically across `corpus.json`, `evidence/*.json`, and this ledger; all `L3` specs carry calibration IDs. |
