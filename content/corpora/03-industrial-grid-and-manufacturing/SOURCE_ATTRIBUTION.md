# Industrial Grid & Manufacturing Public-Domain Source Attribution (World 03)

All control-room ergonomics, process instrumentation symbols, fieldbus electrical specifications, and statistical process control (SPC) formulas used in **World 03 (`03-industrial-grid-and-manufacturing`)** derive from publicly available United States Government handbooks (`17 U.S.C. § 105`) and open industrial engineering standards.

> **Non-Endorsement & Synthetic Telemetry Notice**: Reference to `NIST`, `NRC`, `ISA`, `IEEE`, `TIA`, and `Modbus` standards is strictly for open-source Quiet UI v9.0 engineering demonstration and does not imply endorsement by any standards body or regulator. All facility tag IDs, PLC register live words, calibration certificate numbers, and subgroup bore measurements are deterministic synthetic demonstration data calibrated to published tolerance norms.

---

## 1. Public-Domain Government Handbooks & Standards

| Standard / Document ID | Target Views | Scope & Grounded Parameters | Disposition |
| :--- | :--- | :--- | :--- |
| **NIST/SEMATECH e-Handbook § 6.3** | `v09-spc-quality-and-modbus-report` | Shewhart `X_bar` control chart limits (`UCL`, `CL`, `LCL` at `±3 sigma`), `USL`/`LSL` envelopes, and process capability `C_pk = 1.64` (`n = 5` subgroups) | `GOV_PUBLIC_USE_PERMITTED` |
| **NIST SP 811 (2008 Ed.)** | `v07`, `v08`, `v09` | SI quantity calculus (`Quantity / Unit`), non-breaking unit spacing, parenthetical expanded uncertainty (`k = 2.0`), and exact unit casing (`MW`, `Hz`, `mm`, `Ω`) | `GOV_PUBLIC_USE_PERMITTED` |
| **NRC NUREG-0700 Rev. 3** | `v07-grid-scada-poi-console`, `v08-plant-floor-wall-kiosk` | Human-System Interface Design Review Guidelines: low-chroma dull-screen normal state, CMD-vs-ACT indicator pairing, and two-step guarded breaker actuation | `GOV_PUBLIC_USE_PERMITTED` |

---

## 2. Open Industrial Automation & Grid Standards

| Standard | Target Views | Grounded Engineering Specifications |
| :--- | :--- | :--- |
| **ANSI/ISA-101.01-2015** | `v07`, `v08` | High-performance HMI philosophy (*Quiet Cockpit*): monochrome nominal background (`--bg-shell`, `--bg-card`), chroma rationed strictly to off-nominal alarms and interlocks |
| **ANSI/ISA-5.1-2022** | `v07` | Piping & Instrumentation Diagram (P&ID) functional tag bubbles (`FT-101`, `TT-102`, `PT-204`, `XI-301`) and control valve (`FCV-101`) loop nomenclature |
| **IEEE Std 1547-2018 & C37.118.1** | `v07`, `v08` | Microgrid Point of Interconnection (POI) active power dispatch (`24.0 MW` CMD / `23.6 MW` ACT), BESS SoC (`78.4 %`), and PMU synchrophasor frequency (`60.000 Hz` / `59.985 Hz`) |
| **TIA-485-A & Modbus v1.1b3** | `v07`, `v09` | Differential `120 Ω` end-of-line terminated RS-485 trunk (`D+`/`D-`, `560 Ω` fail-safe bias) and 16-bit Holding Register `0x0104` (`PLC_BREAKER_INTERLOCK_WORD = 0x0A15`) |

---

## 3. Canonical Parameter Anchors

- **Grid Dispatch & Synchrophasor**: `P_cmd = 24.0 MW`, `P_act = (23.6 ± 0.1) MW`, `f_cmd = 60.000 Hz`, `f_act = (59.985 ± 0.005) Hz`, `SoC_bess = (78.4 ± 0.5) %`, `OEE = (94.2 ± 0.4) %`.
- **Fieldbus & Interlock Hardware**: `Z_bus = 120 Ω` TIA-485/Modbus RTU differential trunk; Holding Register `0x0104` (`PLC_BREAKER_INTERLOCK_WORD = 0x0A15`, bit `11` `ISLAND_ARMED = 1`).
- **Statistical Process Control**: Turbine shaft bearing bore `X_bar` (`n = 5`), `CL = 10.000 mm`, `UCL = 10.042 mm`, `LCL = 9.958 mm`, `USL = 10.070 mm`, `LSL = 9.930 mm`, `C_pk = 1.64`.
