# World 06 Distillation Blueprint: Smart Home & Energy

Asymmetric communication specification for `06-smart-home-and-energy` (`world_index: 6`),
projecting household comfort, water leak protection, entry security interlocks,
and 24-hour home energy flow across a matted picture-frame wall kiosk
(`v17`, `M5/M7`) and a Mushroom-styled Home Assistant companion & Energy console (`v18`, `M3`, `N2 <-> N4`).

---

## 1. Asymmetric Translation Matrix

| View ID | Presenter Source | Target Audience | Lens(es) | Tempo | Medium(s) | Chromatic Budget | Nav Shell(s) | Rigor | Evidence Refs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `v17-picture-frame-home-kiosk` | Residential Spatial UI Designer | Household Resident (Glance & Ambiance) | Technician / Operator | `T1` | `M5`, `M7` | Quiet Cockpit | `N0` | `L1` | `evidence/v17_home_comfort_and_safety_scalars.json` |
| `v18-home-assistant-companion-console` | Home Automation Systems Architect | Household Operator (Mobile & Desktop) | Technician / Operator; Project / Systems Engineer | `T1`, `T2` | `M3` | Quiet Cockpit | `N2`, `N4` | `L2` | `evidence/v18_whole_home_energy_plot.json`, `evidence/v18_zone_device_and_sensor_table.json` |

---

## 2. Scrubbed Presenter Bias

| View ID | Habitual Presenter Bias | Receiver Scrub Rule Applied |
| :--- | :--- | :--- |
| `v17-picture-frame-home-kiosk` | Wall tablets covered in switches and industrial SCADA tags plastered over personal photography. | Wrap artwork in a physical gallery frame and warm mat border keeping `>= 76.0 %` unobstructed art (`Fine Art | Photo`), paired with soft whisper-glass corner chips (`21.5 °C` / `71 °F`, `44.0 % RH`, Solar `5.10 kW`, Battery `84.0 %`, all `6` leak sensors dry). |
| `v18-home-assistant-companion-console` | Industrial panel IDs (`PANEL-MAIN-200A`, `ZONE-LIVING`, `LOCK-FRONT-01`), single-tap unguarded lock toggles, and SCADA line plots. | Present warm human room & Mushroom device cards, a two-step safety interlock on `Front Door` and `Garage Door`, responsive `N4` bottom thumb navigation on mobile, and a 24-hour stacked Solar / Grid / Battery Energy bar chart (`-1.68 kW` export at `14:00`). |

---

## 3. Verification of the 4 Universal Audience Evaluation Invariants

1. **Baseline & Corridor**:
   - `v17`: Displays indoor comfort (`21.5 °C`, `44.0 % RH`) and leak status (`6` / `6` dry) in calm whisper glass so nominal operation never competes with the framed artwork.
   - `v18`: Anchors 24-hour home energy dispatch (`5.10 kW` solar production, `3.42 kW` home usage, `-1.68 kW` grid export, `84.0 %` home battery) against the `$0.34 / kWh` evening peak window (`16:00–21:00`).
2. **Epistemic Provenance**:
   - `v17` & `v18`: Derive all scalar, stacked-bar energy, and household device ledger values directly from calibrated home solar, battery, grid meter, thermostat, and moisture telemetry.
3. **Margin & Consequence**:
   - `v17`: Surfaces gentle corner glass orientation without intruding on the living space.
   - `v18`: Highlights the `84.0 %` home battery reserve ahead of the `$0.34 / kWh` peak rate window and enforces `Arm -> Confirm` on Front Door and Garage Door access.
4. **Actionable Disposition**:
   - `v17`: Switch room scenes (`Morning`, `Evening`, `Movie`, `Goodnight`), `Fine Art | Photo`, and `°F | °C` smoothly inside a compact bottom pill dock.
   - `v18`: Filter rooms (`All`, `Climate`, `Lights & Media`, `Safety`), inspect hourly Solar / Grid / Battery bars, and operate doors safely via two-step confirmation.

---

## 4. Canonical Numerical Conservation Ledger

| Metric Key | Canonical Value | Unit | Bound Evidence File & Path | Conserved Across Views |
| :--- | :--- | :--- | :--- | :--- |
| `solar_pv_kw` | `5.10` | `kW` | `evidence/v18_whole_home_energy_plot.json` (`$.series[0].data_points[14].y`), `evidence/v17_home_comfort_and_safety_scalars.json` | `v17`, `v18` |
| `home_load_kw` | `3.42` | `kW` | `evidence/v18_whole_home_energy_plot.json` (`$.series[5].data_points[14].y`), `evidence/v17_home_comfort_and_safety_scalars.json` | `v17`, `v18` |
| `net_grid_export_kw` | `-1.68` | `kW` | `evidence/v18_whole_home_energy_plot.json` (`$.series[3].data_points[14].y`), `evidence/v17_home_comfort_and_safety_scalars.json` | `v17`, `v18` |
| `battery_soc_pct` | `84.0` | `%` | `evidence/v17_home_comfort_and_safety_scalars.json` (`$.items[3].measurement.nominal_value`) | `v17`, `v18` |
| `living_temp_c` | `21.5` | `°C` | `evidence/v17_home_comfort_and_safety_scalars.json` (`$.items[0].measurement.nominal_value`) | `v17`, `v18` |
| `living_rh_pct` | `44.0` | `%` | `evidence/v17_home_comfort_and_safety_scalars.json` (`$.items[1].measurement.nominal_value`) | `v17`, `v18` |
| `leak_sensors_clear` | `6` | `1` | `evidence/v18_zone_device_and_sensor_table.json` (`$.rows[4].numeric_value`) | `v17`, `v18` |
| `peak_evening_tariff_usd_kwh` | `0.34` | `USD/kWh` | `evidence/v18_whole_home_energy_plot.json` (`$.tariff_schedule.peak_evening_usd_kwh`) | `v18` |

---

## 5. Adversarial Audit Table

| Audit Sector | Rubric Basis | Weight | Score (0–100) | Verified Evidence & Hard-Block Clearance |
| :--- | :--- | :--- | :--- | :--- |
| 1. Energy Conservation & Metrology | `CR-1`..`CR-5`, `NIST SP 811` | 30% | `97 / 100` | Every hour balances `Solar Production + Grid Used + Battery Used + Grid Export + Battery Stored = Home Load` (`5.10 - 1.68 = 3.42 kW` at `14:00`). |
| 2. Framed Gallery & Whisper Glass | `M5/M7`, WCAG `AAA` | 25% | `96 / 100` | `v17` leaves `>= 76%` unobstructed framed art with calm whisper-glass pills and zero SCADA entity IDs. |
| 3. Physical Access Safety | Guarded Actuators | 25% | `96 / 100` | `Front Door` and `Garage Door` enforce two-step arm-before-trigger actuation; calm room Mushroom cards hide alert chrome when nominal. |
| 4. Responsive Shell Adaptation | `N2 <-> N4` | 20% | `95 / 100` | `v18` adapts cleanly from desktop sidebar (`1440px`) to `>= 44x44px` bottom thumb dock (`390px`) with zero horizontal overflow. |

- **Composite Audit Score**: `96.1 / 100` (Pass Threshold: `>= 85.0`)
- **Disposition**: `APPROVED` — Ready for Quiet UI v9.0 Gate 5.5 across `M3`, `M5`, and `M7`.
