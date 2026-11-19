# Third-Party Licenses & Provenance Declaration

Quiet UI Skills v9.0 contains **zero third-party runtime dependencies, zero vendored CDN stylesheets, and zero third-party source code** across its 3-pillar architecture (`skills/quiet-ui/`, `skills/quiet-evidence/`, `skills/quiet-bridge/`).

---

## 1. First-Party Deterministic Engine

All UI layout shells, Studio chrome, inline `<svg>` control glyphs, and deterministic Python SVG compilers (`skills/quiet-evidence/scripts/compilers/`) are 100% first-party authored under the repository's Apache 2.0 / MIT split license (`LICENSE`).

---

## 2. Open Technical Notation Standards Implemented (Clean-Room)

The clean-room systems schematic compilers in `skills/quiet-evidence/scripts/compilers/schematic_systems.py` implement non-proprietary open engineering notation standards directly in Python:

- **Timed Sequence Lifelines (`sequence`)** — ITU-T Recommendation Z.120 Message Sequence Chart (MSC) semantics
- **$N^2$ Interface Matrix (`n2_matrix`)** — NASA Systems Engineering Handbook (`NASA/SP-2016-6105`) $N^2$ coupling matrix conventions
- **Fault Tree Logic (`fault_tree`)** — U.S. Nuclear Regulatory Commission Fault Tree Handbook (`NUREG-0492`) standard logic gate topology

---

## 3. Verification Environment Dependencies (Dev / CI Only)

Browser-based Chrome DevTools Protocol (CDP) contract verification runs locally via Python (`selenium` / Chromium WebDriver) and never embeds third-party packages inside generated HTML or SVG deliverables.

---

## 4. Public-Domain & `CC0 1.0` Optical Viewport Photographs (`docs/assets/`)

All optical backplate photographs used in `hud-1`, `v15` (`M6`), and `v16` (`M7`) are EXIF-free `1600×1000` JPEGs sourced strictly under United States Government Public Domain (`17 U.S.C. § 105`) or `CC0 1.0 Universal` dedication (`AttributionRequired == "false"`), imposing zero attribution obligations on generated deliverables:

- `docs/assets/as08-14-2383.jpg` — Apollo 8 Earthrise (`NASA JSC`, `PD-USGov-NASA`)
- `docs/assets/opt_hud_daylight_rwy.jpg` — `DF-ST-83-04217` Runway Final Approach (`U.S. DoD / DVIC`, `Public domain`)
- `docs/assets/opt_hud_night_rwy.jpg` — `KC-10 landing at night 130811-F-AB304-254` (`U.S. Air Force / DVIDS`, `Public domain`)
- `docs/assets/opt_glass_day_hwy.jpg` — Catskill Interstate Highway Daylight (`Wikimedia / Unsplash CC0 Archive`, `CC0 1.0`)
- `docs/assets/opt_glass_dusk_hwy.jpg` — Sunset Highway Horizon Glare (`Wikimedia / Unsplash CC0 Archive`, `CC0 1.0`)
- `docs/assets/opt_glass_night_hwy.jpg` — Night Multi-Lane Highway Traffic (`Wikimedia / Unsplash CC0 Archive`, `CC0 1.0`)
