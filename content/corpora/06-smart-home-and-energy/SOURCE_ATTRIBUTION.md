# World 06 Public-Domain & Open-Standard Source Attribution

World 06 (`06-smart-home-and-energy`) models residential distributed energy
resource (DER) telemetry, indoor environmental monitoring, safety interlocks, and
ambient picture-frame kiosk presentation using purely synthetic home device IDs,
open metrology standards, and verified `CC0 1.0` backplate imagery.

> **Synthetic Identifier & Privacy Guarantee:** Every device, circuit, zone,
> and lock identifier in World 06 (`PANEL-MAIN-200A`, `PV-STRING-SOUTH`,
> `BATT-WALL-13KWH`, `ZONE-LIVING`, `LOCK-FRONT-01`, `GARAGE-BAY-01`,
> `LEAK-LOOP-06`, `EVSE-GARAGE-48A`) is 100% synthetic with zero personal names,
> addresses, network hostnames, LAN IPs, SSIDs, or tokens.

## 1. Energy Metrology & Smart-Home Protocol Standards (`v17`, `v18`)

| Standard / Reference | Target Views | Scope & Canonical Parameters | Disposition |
| :--- | :--- | :--- | :--- |
| `ASHRAE-55 / NIST-SP-811` | `v17`, `v18` | Indoor thermal comfort band (`21.5 °C`, `44.0 %RH`) formatted under strict quantity calculus (`Quantity / Unit`, `+/- u_y`) | `OPEN_STANDARD_REF` |
| `IEEE-2030.5 / CTA-2045` | `v18` | Residential PV generation (`5.10 kW`), whole-home demand (`3.42 kW`), net grid export (`-1.68 kW`), battery state-of-charge (`84.0 %`), and TOU tariff (`$0.34 / kWh`) | `OPEN_STANDARD_REF` |
| `CSA-MATTER-1.4` | `v17`, `v18` | Non-proprietary smart-home device abstraction for leak loops (`LEAK-LOOP-06` = `6 / 6` dry), door lock (`LOCK-FRONT-01`), and garage bay barrier (`GARAGE-BAY-01`) | `SYNTHETIC_BENCH_REF` |

## 2. Picture-Frame Kiosk Backplates (`v17`, EXIF-Free `1600×1000` `CC0 1.0`)

Both `v17` backdrop options carry zero attribution obligations (`AttributionRequired == "false"`):

| Asset Path | Mode | Source Title & Archive | License | Output Size |
| :--- | :--- | :--- | :--- | :--- |
| `docs/assets/opt_frame_art.jpg` | `art` | [`Albert Bierstadt, Mount Corcoran, c. 1876-1877, NGA 166428`](https://commons.wikimedia.org/wiki/File:Albert_Bierstadt,_Mount_Corcoran,_c._1876-1877,_NGA_166428.jpg) (National Gallery of Art Open Access) | `CC0 1.0` | `1600×1000` (`163,978 B`) |
| `docs/assets/opt_frame_landscape.jpg` | `landscape` | [`Beautiful mountain reflection (Unsplash)`](https://commons.wikimedia.org/wiki/File:Beautiful_mountain_reflection_(Unsplash).jpg) (Wikimedia Commons / Unsplash CC0 Archive) | `CC0 1.0` | `1600×1000` (`105,166 B`) |
