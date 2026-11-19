# World 05 Public-Domain & Open-Standard Source Attribution

World 05 (`05-physical-systems-auto-and-aero`) synthesizes propulsion dynamometer
efficiency curves, differential vehicle/aerospace fieldbus diagnostics, and
collimated / spatial crew display constraints from publicly released U.S.
Government datasets, open engineering standards, and NIST metrology guides.

> **Non-Endorsement Notice (`14 CFR Part 1221` / DOE Open Data):** Reference to
> Argonne National Laboratory, NASA, NIST, NAVAIR, SAE, or ISO publications is
> strictly for quiet-evidence schema verification and human-factors UI
> demonstration and does not imply agency or standards-body endorsement.

## 1. Propulsion Dynamometer & Thermodynamic Sources (`v13`)

| Source ID | Target Views | Title & Scope | Disposition |
| :--- | :--- | :--- | :--- |
| `ANL-D3-DYN` | `v13`, `v15` | Argonne National Laboratory `D^3` Downloadable Dynamometer Database — steady-state & transient Brake Thermal Efficiency (`eta_bte / %`) vs. Indicated Mean Effective Pressure (`IMEP / bar`, 2–20 bar), peak `42.8 %` at `14.0 bar` | `DOE_PUBLIC_DATA` |
| `NIST-SP-811` | `v13`, `v14` | NIST Special Publication 811 — *Guide for the Use of the International System of Units (SI)* (quantity calculus `Quantity / Unit`, `+/- u_y` parenthetical uncertainty) | `GOV_PUBLIC_DOMAIN` |
| `NAVAIR-FTM-108` | `v13`, `v14` | NAVAIR FTM-108 — *Flight Test Engineering Guidelines* (`1-2-5 x 10^n` major tick scaling and residual normalization) | `GOV_PUBLIC_DOMAIN` |

## 2. Differential Fieldbus & Bitfield Protocol Sources (`v14`, `v16`)

| Standard / Reference | Target Views | Scope & Canonical Parameters | Disposition |
| :--- | :--- | :--- | :--- |
| `SAE-J1939-11 / ISO-11898-2` | `v14`, `v16` | High-speed `CAN-FD` twisted-pair physical layer (`120 Ω` end-of-line termination, direct drop `Stub <= 0.3 m`, `500 kbps` arbitration / `2 Mbps` data phase) | `OPEN_STANDARD_REF` |
| `SAE-J1939-21` | `v14` | 29-bit Extended Arbitration Header (`0x18FEF100` PGN `0xFEF1` CCVS1, `PRIORITY=6`, `EDP=0`, `DP=0`, `PF_PGN_HI=0xFE`, `PS_PGN_LO=0xF1`, `SOURCE_ADDR=0x00`) | `OPEN_STANDARD_REF` |
| `HIL-SCOPE-TIMING` | `v14` | Synchronized 3-channel bench capture (`CAN_H - CAN_L` `V_diff / V`, Common-Mode Noise `mV`, `ACK_DELIM` digital gate) with `0.35 µs` impedance-mismatch dropout | `SYNTHETIC_BENCH_REF` |

## 3. Crew Human-Factors & Optical Display Sources (`v15`, `v16`)

| NTRS / Standard ID | Target Views | Title & Canonical Constraint | Disposition |
| :--- | :--- | :--- | :--- |
| `NASA-STD-3001-V2C` | `v15`, `v16` | NASA-STD-3001 Vol 2 Rev C (`20130000738`) — Crew display/effector separation, guarded controls, and zero-flashing alarm discipline | `GOV_PUBLIC_USE_PERMITTED` |
| `NASA-NTRS-20250011652` | `v15` | Review of Advanced Informatics and Display Systems for Extravehicular & Flight HUDs (`M6` collimated infinity optics, `>= 65.0 %` central sightline keep-out) | `GOV_PUBLIC_USE_PERMITTED` |
| `QUIET-UI-M7-OPTICS` | `v16` | Medium `M7` Transparent Window Overlay specification (luminance-adaptive smoked scrim `>= 7.0:1` contrast ratio with `paint-order` stroke halos) | `REPO_SPEC_V9` |

## 4. Real-World Optical Backplate Photographs (`v15`, `v16`, EXIF-Free `1600×1000`)

All optical viewport photographs carry zero attribution requirements for shipped deliverables (`17 U.S.C. § 105` U.S. Government Public Domain or `CC0 1.0 Universal` dedication, verified `AttributionRequired == "false"` via `scripts/fetch_optical_backplates.py`).

| Asset Path | View & Mode | Source Title & Agency | License | Output Size |
| :--- | :--- | :--- | :--- | :--- |
| `docs/assets/as08-14-2383.jpg` | `v15` `earthrise` | Apollo 8 Earthrise (`as08-14-2383`, NASA JSC) | `PD-USGov-NASA` | `1600×1000` (`30,948 B`) |
| `docs/assets/opt_hud_daylight_rwy.jpg` | `v15` `daylight` | [`DF-ST-83-04217 An aerial view of the runway approach`](https://commons.wikimedia.org/wiki/File:DF-ST-83-04217_An_aerial_view_of_the_runway_approach.jpeg) (U.S. DoD / DVIC, `2820×1850`) | `Public domain` | `1600×1000` (`178,006 B`) |
| `docs/assets/opt_hud_night_rwy.jpg` | `v15` `lowlight` | [`KBTP at dusk`](https://commons.wikimedia.org/wiki/File:KBTP_at_dusk.jpg) (Wikimedia Commons, airborne final approach Runway 26, `2869×2038`) | `CC0 1.0` | `1600×1000` (`128,694 B`) |
| `docs/assets/opt_glass_day_hwy.jpg` | `v16` `daylight` | [`A steel arch bridge over calm water (Unsplash)`](https://commons.wikimedia.org/wiki/File:A_steel_arch_bridge_over_calm_water_(Unsplash).jpg) (Wikimedia Commons / Unsplash CC0 Archive, `6981×4659`) | `CC0 1.0` | `1600×1000` (`172,119 B`) |
| `docs/assets/opt_glass_dusk_hwy.jpg` | `v16` `dusk` | [`Coast Guard Cutter Hamilton (15782225475)`](https://commons.wikimedia.org/wiki/File:Coast_Guard_Cutter_Hamilton_(15782225475).jpg) (U.S. Coast Guard Public Domain, `4128×2322`) | `Public domain` | `1600×1000` (`172,410 B`) |
| `docs/assets/opt_glass_night_hwy.jpg` | `v16` `night` | [`Red Night at Tran Thi Ly Bridge (Unsplash)`](https://commons.wikimedia.org/wiki/File:Red_Night_at_Tran_Thi_Ly_Bridge_(Unsplash).jpg) (Wikimedia Commons / Unsplash CC0 Archive, `3840×2400`) | `CC0 1.0` | `1600×1000` (`162,834 B`) |
