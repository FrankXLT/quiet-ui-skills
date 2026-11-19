# Third-Party Licenses & Provenance Declaration

Quiet UI Skills v9.0 operates with **zero external CDN requests and zero non-Apache/MIT runtime dependencies** across its 3-pillar architecture (`skills/quiet-ui/`, `skills/quiet-evidence/`, `skills/quiet-bridge/`). All shipped HTML deliverables are 100% self-contained and offline-capable.

---

## 1. First-Party Deterministic Engine

All UI layout shells, Studio chrome, inline `<svg>` control glyphs, and deterministic Python SVG compilers (`skills/quiet-evidence/scripts/compilers/`) are first-party authored under the repository's Apache 2.0 / MIT split license (`LICENSE`).

---

## 2. Vendored Interactive Visualization Runtime (`Apache-2.0`)

- **Apache ECharts (`v5.6.0`)** — Vendored offline at `docs/assets/vendor/echarts.min.js` (`renderer: 'svg'` default, zero external network fetches).
  - **License**: Apache License, Version 2.0 (`Apache-2.0`)
  - **Copyright**: Copyright 2017–2024 The Apache Software Foundation (includes zrender notice preserved in upstream distribution)
  - **Scope**: Optional interactive charting layer mounted progressively onto Quiet UI containers in `docs/v9/` and `docs/bench/`, falling back automatically to deterministic first-party Python SVG output for `M1` print/archival exports and `scripts/compile_evidence.py` standalone output.

---

## 3. Open Technical Notation Standards Implemented (Clean-Room)

The clean-room systems schematic compilers in `skills/quiet-evidence/scripts/compilers/schematic_systems.py` implement non-proprietary open engineering notation standards directly in Python:

- **Timed Sequence Lifelines (`sequence`)** — ITU-T Recommendation Z.120 Message Sequence Chart (MSC) semantics
- **$N^2$ Interface Matrix (`n2_matrix`)** — NASA Systems Engineering Handbook (`NASA/SP-2016-6105`) $N^2$ coupling matrix conventions
- **Fault Tree Logic (`fault_tree`)** — U.S. Nuclear Regulatory Commission Fault Tree Handbook (`NUREG-0492`) standard logic gate topology

---

## 4. Verification Environment Dependencies (Dev / CI Only)

Browser-based Chrome DevTools Protocol (CDP) contract verification runs locally via Python (`selenium` / Chromium WebDriver) and never embeds dev/test packages inside generated HTML or SVG deliverables.

---

## 5. Public-Domain & `CC0 1.0` Optical & Ambient Gallery Photographs (`docs/assets/`)

All backplate photographs used in `hud-1`, `v15` (`M6`), `v16` (`M7`), and `v17` (`06-smart-home-and-energy`) are EXIF-free `1600×1000` JPEGs sourced strictly under United States Government Public Domain (`17 U.S.C. § 105`) or `CC0 1.0 Universal` dedication (`AttributionRequired == "false"`), imposing zero attribution obligations on generated deliverables:

- `docs/assets/as08-14-2383.jpg` — Apollo 8 Earthrise (`NASA JSC`, `PD-USGov-NASA`)
- `docs/assets/opt_hud_daylight_rwy.jpg` — `DF-ST-83-04217` Runway Final Approach (`U.S. DoD / DVIC`, `Public domain`)
- `docs/assets/opt_hud_night_rwy.jpg` — Airborne Final Approach Runway 26 at Dusk (`KBTP at dusk`, `Wikimedia Commons`, `CC0 1.0`)
- `docs/assets/opt_glass_day_hwy.jpg` — Steel Arch Navigation Bridge over Calm River Channel (`Wikimedia / Unsplash CC0 Archive`, `CC0 1.0`)
- `docs/assets/opt_glass_dusk_hwy.jpg` — Coast Guard Cutter Bow Sunset Harbor Channel Glare (`U.S. Coast Guard`, `Public domain`)
- `docs/assets/opt_glass_night_hwy.jpg` — Night River Navigation Channel & Illuminated Cable-Stay Bridge (`Wikimedia / Unsplash CC0 Archive`, `CC0 1.0`)
- `docs/assets/opt_frame_art.jpg` — Albert Bierstadt, *Mount Corcoran*, c. 1876–1877 (`National Gallery of Art Open Access`, `CC0 1.0`)
- `docs/assets/opt_frame_landscape.jpg` — Calm Mountain Lake Reflection (`Wikimedia / Unsplash CC0 Archive`, `CC0 1.0`)
