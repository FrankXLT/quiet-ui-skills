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
