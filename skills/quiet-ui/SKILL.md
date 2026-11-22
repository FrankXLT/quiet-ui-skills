---
name: quiet-ui
description: Design system and UI architecture skill generating responsive HTML interfaces across 7 delivery mediums with 4-theme tokens, concentric geometry, and human-factors controls grounded in ISA-101, FDA IEC 62366, and NASA-STD-3001.
---

# Quiet UI v9.2.2 — Qualitative Delivery Medium Physics & Shells

Quiet UI Pillar 1 manages physical optical constraints, viewing distance, container geometry, and chromatic budgets across seven delivery mediums—serving clinical bedside stations, grid SCADA consoles, industrial kiosks, editorial briefs, and optical HUDs alike.

---

## 1. Gate 0 Self-Immutability & Customization Lock

Before proposing or generating any interface code, verify project scope isolation:
1. **Never mutate core tokens or templates in an active feature chat**: Core files in `tokens/`, `src/css/`, and `src/chrome/` are immutable during feature development.
2. **Project-Specific Customizations**: All custom styling must live in `customizations/<brand>/styles/overrides.css` and be declared in `customization.json`.
3. **4-Way Token Mirror Parity**: Any authorized token addition must be synchronized across all 4 mirror targets with identical SHA-256 hashes.

---

## 2. Pre-Edit Output Contract

Every interface response MUST inspect real source schemas first and declare the **Pre-Edit Output Contract**:
- **Project Mode**: Declare **`Greenfield`** (new build) or **`Brownfield Retrofit`** (existing app overhaul). Whenever **`Brownfield Retrofit`** is active, you MUST also declare a **Capability Parity Ledger (`KEEP | CONSOLIDATE | DEPRECATE`)** mapping every existing filter mode, breakdown table, and export action, plus a **Deprecation Blocklist** of retired controls banned from resurrection despite legacy wire keys.
- **Data-to-Widget Binding Map**: Source endpoint/fields, units, omitted absent sub-slots, visible on-card legends for `>= 2` series, trackless `.va-kpi-card` for unbounded totals vs. `.va-kpi-gauge-card` for bounded shares, and warmup fallback (`Warming up — N samples collected` if `N < 10`).
- **Medium**: Selected from `M1` through `M7`.
- **Chromatic Purpose Budget**: Selected from `Archival Proof`, `Pedagogical Flow`, `Decision Contrast`, or `Quiet Cockpit`.
- **Navigation Shell**: Selected from `N0` (undecorated stage), `N1` (overlay/rail `.va-side-rail` + `.va-drawer-backdrop`), `N2` (top bar), `N3` (composite), or `N4` (mobile bottom dock `< 700px`).
- **Container Geometry**: Declared max-width (`max-inline-size: 1480px` desktop cap `>= 1920px`) and concentric corner radii (`--radius-card`, `--radius-inner`, `--radius-sm`).

---

## 3. Progressive-Disclosure Architecture & File Router

Load ONLY the specific foundation and medium guides matching your active vector:

### Foundation Guides
- [foundation/data-grounding-and-widget-binding.md](foundation/data-grounding-and-widget-binding.md): Mandatory Data-to-Widget Binding Map, on-card series legends, `.va-kpi-card` unbounded rules, composite `[Chart + Table]` 1-column rule, `N < 10` warmup labels, zero mock JS/JSON fixtures/self-badges/raw `brain:` IDs.
- [foundation/brownfield-retrofit-and-migration.md](foundation/brownfield-retrofit-and-migration.md): Greenfield vs. Brownfield Retrofit guardrails, Capability Parity Ledger (`KEEP | CONSOLIDATE | DEPRECATE`), Deprecation Blocklist & wire-field decoupling, monolith-to-zoom decomposition, side-by-side strangler routes, and `@layer` cascade quarantine (`layer(legacy)`).
- [foundation/tokens-and-surfaces.md](foundation/tokens-and-surfaces.md): 4-theme OKLCH tokens (incl. `--bg-subtle`), 4-way mirror parity, canonical `@layer reset, tokens, shell, archetypes, evidence, views, utilities;` order, concentric radius math, and border depth rules.
- [foundation/typography-and-hierarchy.md](foundation/typography-and-hierarchy.md): 3-role font stack, fluid 4K scale, 72ch prose vs. `.va-bleed-wide`, plain everyday copy, and zero chrome emojis (`<svg>` icons).
- [foundation/chromatic-purpose-budgets.md](foundation/chromatic-purpose-budgets.md): Archival Proof, Pedagogical Flow, Decision Contrast, Quiet Cockpit rations, plus Page-Wide Coherence (`<= 3` card structures, `<= 1` chart/half-width card, 1 `--chart-1..5` palette).
- [foundation/navigation-morphing.md](foundation/navigation-morphing.md): Polymorphic shells `N0–N4`, left-of-brand topbar trigger + `.va-side-rail[data-mode="overlay"]` + `.va-rail-footer`, `.va-period-stepper`/`.va-preset-popover`, `.va-scope-chip`, `.va-tree-row`, `<= 88px` (`< 680px`) / `<= 64px` (`>= 680px`) sticky budgets, and `@media print`.

### Delivery Medium Physics
- [mediums/m1-paper-and-print.md](mediums/m1-paper-and-print.md): Paper & Print sheet physics, `@page` rules, high-contrast ink, and unrolled figures.
- [mediums/m2-editorial-web.md](mediums/m2-editorial-web.md): Editorial monographs, RFC specifications, research briefs, and multi-column figures.
- [mediums/m3-stateful-web-app.md](mediums/m3-stateful-web-app.md): Stateful workbenches, `.va-workbench-panes` hairline panes, opaque `.va-side-rail`, `.va-kpi-gauge-card`/`.va-kpi-card`, `.va-toolbar-joined`, `.va-tab-strip`, `.va-plot-row` `subgrid`, 1-col `[Chart + Table]`, `1480px` ultrawide cap, and `observeChartResize` + `min-width: 0` chart hosts.
- [mediums/m4-walkup-poi-terminal.md](mediums/m4-walkup-poi-terminal.md): Point-of-Interest kiosks, guarded touch targets, and high-visibility contrast.
- [mediums/m5-ambient-wall-kiosk.md](mediums/m5-ambient-wall-kiosk.md): 10-foot ambient wall displays, high-readability telemetry, and status glanceability.
- [mediums/m6-collimated-optical-hud.md](mediums/m6-collimated-optical-hud.md): Collimated optical HUD, >=65% central keep-out, peripheral symbology, and monochrome green/cyan.
- [mediums/m7-transparent-window-overlay.md](mediums/m7-transparent-window-overlay.md): Variable luminance smoked scrims, stroke text halos, and environmental glare rejection.

---

## 4. Portable HTML/CSS Auditor (`scripts/audit_quiet_html.py`)

Verify any external HTML/CSS/JS asset tree or live localhost URL (`~/.agents/skills/quiet-ui/` or `skills/quiet-ui/`) against Quiet UI styling (`[HIDDEN_LAYER]`, `[IMPORTANT]`, `[FONT_FLOOR]`), chrome & layout budgets (`[STICKY_CHROME_BLOAT]` `> 64px`, `[PLOT_AXIS_MISALIGN]` `> 2px`, `[PILL_SPRAWL]`, `[NAVBAR_SHIFT]`, `[PANE_CONTROL_CLIPPED]`), data honesty (`[SELF_BADGE]`, `[FAKE_UNBOUNDED_GAUGE]`, `[JSON_MOCK_FIXTURE]`, `[EMOJI_IN_CHROME]`, raw `brain:` IDs, mock JS arrays), SVG overlaps/hairlines/clipping (`[AXIS_LABEL_CLIPPED]`, `[BAR_HAIRLINE_DENSITY]`), and label truncation. Subdirectory/subpath `--mount-prefix` audits check asset existence (`[MISSING_ASSET]`) while scoping CSS/JS linting unless `--audit-mounted-external` or `--exclude` is passed:

```bash
# Zero-dependency static audit across mounted assets (subpath-scoped by default)
python3 -B scripts/audit_quiet_html.py path/to/web/v9 --mount-prefix /web=/path/to/web --exclude "*.min.js"

# Live Headless Chrome sweep across 390px, 820px, and 1440px (requires selenium + Chrome)
python3 -B scripts/audit_quiet_html.py http://127.0.0.1:8788/ --cdp --mount-prefix /web=/path/to/web
```

---

## 5. Integration with Complementary Pillars
- **Quantitative Metrology & Schematics**: Consult [quiet-evidence](../quiet-evidence/SKILL.md) for calibrated plots, bitfields, HIL waveforms, and topologies.
- **Audience Translation & Murder Board**: Consult [quiet-bridge](../quiet-bridge/SKILL.md) for persona scrub rubrics and review-room dual-layer patterns.
