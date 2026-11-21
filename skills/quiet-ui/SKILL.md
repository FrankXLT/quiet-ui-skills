---
name: quiet-ui
description: Design system and UI architecture skill generating responsive HTML interfaces across 7 delivery mediums with 4-theme tokens, concentric geometry, and human-factors controls grounded in ISA-101, FDA IEC 62366, and NASA-STD-3001.
---

# Quiet UI v9.1 — Qualitative Delivery Medium Physics & Shells

Quiet UI Pillar 1 manages physical optical constraints, viewing distance, container geometry, and chromatic budgets across seven delivery mediums—serving clinical bedside stations, grid SCADA consoles, industrial kiosks, editorial briefs, and optical HUDs alike.

---

## 1. Gate 0 Self-Immutability & Customization Lock

Before proposing or generating any interface code, verify project scope isolation:
1. **Never mutate core tokens or templates in an active feature chat**: Core files in `tokens/`, `src/css/`, and `src/chrome/` are immutable during feature development.
2. **Project-Specific Customizations**: All custom styling must live in `customizations/<brand>/styles/overrides.css` and be declared in `customization.json`.
3. **4-Way Token Mirror Parity**: Any authorized token addition must be synchronized across all 4 mirror targets with identical SHA-256 hashes.

---

## 2. Pre-Edit Output Contract

Every interface response MUST begin by explicitly declaring the **Pre-Edit Output Contract**:
- **Medium**: Selected from `M1` through `M7`.
- **Chromatic Purpose Budget**: Selected from `Archival Proof`, `Pedagogical Flow`, `Decision Contrast`, or `Quiet Cockpit`.
- **Navigation Shell**: Selected from `N0` (undecorated stage), `N1` (left rail/drawer), `N2` (top bar), `N3` (composite), or `N4` (mobile bottom dock).
- **Container Geometry**: Declared max-width and concentric corner radii (`--radius-card`, `--radius-inner`, `--radius-sm`).

---

## 3. Progressive-Disclosure Architecture & File Router

Load ONLY the specific foundation and medium guides matching your active vector:

### Foundation Guides
- [foundation/tokens-and-surfaces.md](foundation/tokens-and-surfaces.md): 4-theme OKLCH tokens, 4-way mirror parity, concentric radius math, and border depth rules.
- [foundation/typography-and-hierarchy.md](foundation/typography-and-hierarchy.md): 3-role font stack, fluid 4K scale, 72ch prose vs. `.va-bleed-wide`, table clipping rules.
- [foundation/chromatic-purpose-budgets.md](foundation/chromatic-purpose-budgets.md): Archival Proof, Pedagogical Flow, Decision Contrast, and Quiet Cockpit token rations.
- [foundation/navigation-morphing.md](foundation/navigation-morphing.md): Polymorphic shells `N0–N4`, foldable 820px eyebrow nav, mobile 390px touch hit targets, and `@media print`.

### Delivery Medium Physics
- [mediums/m1-paper-and-print.md](mediums/m1-paper-and-print.md): Paper & Print sheet physics, `@page` rules, high-contrast ink, and unrolled figures.
- [mediums/m2-editorial-web.md](mediums/m2-editorial-web.md): Editorial monographs, RFC specifications, research briefs, and multi-column figures.
- [mediums/m3-stateful-web-app.md](mediums/m3-stateful-web-app.md): Stateful workbenches, dual-pane task dispatchers, and responsive bento grids.
- [mediums/m4-walkup-poi-terminal.md](mediums/m4-walkup-poi-terminal.md): Point-of-Interest kiosks, guarded touch targets, and high-visibility contrast.
- [mediums/m5-ambient-wall-kiosk.md](mediums/m5-ambient-wall-kiosk.md): 10-foot ambient wall displays, high-readability telemetry, and status glanceability.
- [mediums/m6-collimated-optical-hud.md](mediums/m6-collimated-optical-hud.md): Collimated optical HUD, >=65% central keep-out, peripheral symbology, and monochrome green/cyan.
- [mediums/m7-transparent-window-overlay.md](mediums/m7-transparent-window-overlay.md): Variable luminance smoked scrims, stroke text halos, and environmental glare rejection.

---

## 4. Portable HTML/CSS Auditor (`scripts/audit_quiet_html.py`)

Verify any external HTML/CSS file, directory, or live localhost URL (run inside `~/.agents/skills/quiet-ui/` or prefix `skills/quiet-ui/` from the repo root) against Quiet UI's `!important` ban, `>= 11px` font floor, accessible `<svg>` `viewBox`/label contract, and responsive `<table>` wrapping:

```bash
# Zero-dependency static audit (runs anywhere via stdlib Python)
python3 -B scripts/audit_quiet_html.py path/to/page.html

# Live Headless Chrome sweep across 390px, 820px, and 1440px (requires selenium + Chrome)
python3 -B scripts/audit_quiet_html.py http://127.0.0.1:8788/ --cdp
```

---

## 5. Integration with Complementary Pillars
- **Quantitative Metrology & Schematics**: Consult [quiet-evidence](../quiet-evidence/SKILL.md) for calibrated plots, bitfields, HIL waveforms, and topologies.
- **Audience Translation & Murder Board**: Consult [quiet-bridge](../quiet-bridge/SKILL.md) for persona scrub rubrics and review-room dual-layer patterns.
