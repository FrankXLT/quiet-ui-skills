# Personal Blueprint — 00 Global Structure

## 1. Intent & Identity
The Personal Starter establishes an unhurried, focused environment spanning technical research, daily execution, and ambient physical spaces. It adopts clinical Pure White (`data-theme="white"`) as the baseline surface, balanced with deep dark-mode support for nighttime study and wall displays.

## 2. Navigation Architecture
- **N0 (Zero-Chrome):** Dedicated to distraction-free reading (`Doc-2`, `Doc-3`) and ambient art stages (`HA-1`).
- **N1 (Left Rail):** Standard persistent workstation layout for documentation, temporal planning, and telemetry consoles.
- **N2 (Sub-Header Tabs):** Scoped contextual views for high-density ledgers and executive metric matrices.
- **N3 (Dual-Rail Spine):** Encyclopedic reference and developer runbooks with 6-stage flow spines.
- **N4 (Mobile Bottom Thumb Bar):** Compact controllers and handheld smart-home remotes.

## 3. Geometric & Typographic Discipline
- **Concentric Radius:** All cards enforce `var(--radius-card, 12px)`, inner elements derive `max(0px, calc(var(--radius-card) - 4px))`.
- **Typographic Scale:** 7-step scale anchored by `--font-sans` for navigation and chrome, `--font-serif` for narrative monographs, and `--font-mono` for metrics and code literals.
- **11px Hard Minimum Floor:** Zero text below 11px ensures full legibility across handheld and wall-mounted devices.
