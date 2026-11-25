---
name: quiet-ui
description: Design system and UI architecture skill generating responsive HTML interfaces across 7 delivery mediums with 4-theme tokens, concentric geometry, and human-factors controls grounded in ISA-101, FDA IEC 62366, and NASA-STD-3001.
---

# Quiet UI v9.7.0 — Qualitative Delivery Medium Physics & Shells

Quiet UI Pillar 1 manages physical optical constraints, viewing distance, container geometry, and chromatic budgets across seven delivery mediums—serving clinical bedside stations, grid SCADA consoles, industrial kiosks, civic data briefs, and optical HUDs alike.

---

## 1. Gate 0 Self-Immutability & Customization Lock

Before proposing or generating any interface code, verify project scope isolation:
1. **Never mutate core tokens or templates in an active feature chat**: Core files in `tokens/`, `src/css/`, and `src/chrome/` are immutable during feature development.
2. **Project-Specific Customizations**: All custom styling must live in `customizations/<brand>/styles/overrides.css` and be declared in `customization.json`.
3. **4-Way Token Mirror Parity**: Any authorized token addition must be synchronized across all 4 mirror targets with identical SHA-256 hashes.

---

## 2. Pre-Edit Output Contract

Every interface response MUST inspect the target root for `.quiet-ui.md` (and live API schemas) first, persist any updated scope contract via `--init-context`, and declare the **Pre-Edit Output Contract**:
- **Project Mode**: Declare **`Greenfield`** (new build) or **`Brownfield Retrofit`** (existing app overhaul). Whenever **`Brownfield Retrofit`** is active, you MUST also declare a **Capability Parity Ledger (`KEEP | CONSOLIDATE | DEPRECATE`)** mapping every existing filter mode, breakdown table, and export action, plus a **Deprecation Blocklist** (`selector:` / `copy:`) synced in `.quiet-ui.md`.
- **Data-to-Widget Binding Map**: Source endpoint/fields, units, omitted absent sub-slots, visible on-card legends for `>= 2` series, trackless `.va-kpi-card` for unbounded totals vs. `.va-kpi-gauge-card` for bounded shares, effective-dated rate epochs, Cyclical Anti-Sum rules, and warmup fallback (`Warming up — N samples collected` if `N < 10`).
- **Medium & Controls**: `Medium` (`M1–M7`), `Chromatic Budget`, `Navigation Shell` (`N0–N4`, using strict **Path A** `N0` `68ch` Journalistic Article vs. **Path B** Full-Width Interactive Explorer on public data), max-width (`1480px` cap `>= 1920px`), concentric corner radii, 4-way zero-states, action reversibility tiering, readable `--disabled-*` safety gates (`>= 3.0:1`), `601–980px` unbroken monospace parameter keys, `>= 6px` SVG label-to-line clearance, and `>= 24px` `@media print` horizontal safe margins.

---

## 3. Progressive-Disclosure Architecture & File Router

Load ONLY the specific foundation and medium guides matching your active vector:

### Foundation Guides
- [foundation/data-grounding-and-widget-binding.md](foundation/data-grounding-and-widget-binding.md): Data-to-Widget Binding Map, on-card series legends, `.va-kpi-card` unbounded rules, Cyclical Whisker Anti-Sum Rule, effective-dated rate epochs, `SHA-256[:12]` showcase sanitization, `N < 10` warmup labels, zero mock JS/JSON fixtures/self-badges/raw `brain:` IDs.
- [foundation/public-data-and-storytelling.md](foundation/public-data-and-storytelling.md): Strict Path A (`N0` `68ch` Journalistic Article, `56rem` breakouts, inline sentence scope `<select>`, quiet `Source` footer links) vs. Path B (Full-Width Interactive Explorer toolbar, compact toggle rules, `0.0 pp` mobility baseline, conditional scroll cues, `@media print`).
- [foundation/brownfield-retrofit-and-migration.md](foundation/brownfield-retrofit-and-migration.md): `.quiet-ui.md` persistent context contract, Greenfield vs. Brownfield Retrofit guardrails, Capability Parity Ledger (`KEEP | CONSOLIDATE | DEPRECATE`), Deprecation Blocklist, monolith-to-zoom decomposition, strangler routes, `@layer` quarantine (`layer(legacy)`), and Guardrail 6 Day-30 Extract & Normalize (`--strict-drift`).
- [foundation/forms-states-and-resilience.md](foundation/forms-states-and-resilience.md): Accessible labels (`[UNLABELED_FORM_CONTROL]`), progressive `blur`/`input`/submit `:user-invalid` validation, `.va-gate-reason`, `[aria-busy="true"]`, 4-way zero-data taxonomy (`first-run`, `filtered` `Clear filters`, `warmup`, `.va-stale-retained`), and 3-tier reversibility (`.va-undo-toast` `>= 7s`, `ARM -> EXECUTE`, `<dialog closedby="any">`).
- [foundation/tokens-and-surfaces.md](foundation/tokens-and-surfaces.md): 4-theme OKLCH tokens (incl. `--bg-subtle`), 4-way mirror parity, canonical `@layer reset, tokens, shell, archetypes, evidence, views, utilities;` order, concentric radius math, and border depth rules.
- [foundation/typography-and-hierarchy.md](foundation/typography-and-hierarchy.md): 3-role font stack, fluid 4K scale, 72ch prose vs. `.va-bleed-wide`, plain everyday copy, and zero chrome emojis (`<svg>` icons).
- [foundation/chromatic-purpose-budgets.md](foundation/chromatic-purpose-budgets.md): Archival Proof, Pedagogical Flow, Decision Contrast, Quiet Cockpit rations, plus Page-Wide Coherence (`<= 3` card structures, `<= 1` chart/half-width card, 1 `--chart-1..5` palette).
- [foundation/navigation-morphing.md](foundation/navigation-morphing.md): Polymorphic shells `N0–N4`, left-of-brand trigger + single-row `40px` `.va-rail-footer` (`.va-swatch-row` left, 2-stop `Compact | Comfortable` right), flat borderless `.va-tree-row`/`.va-tree-children` (`<= 5` kids + `.va-tree-more`), `.va-split-reader-gallery` (`>= 60%` prose + `< 760px` `<dialog closedby="any">`), `.va-period-stepper`/`.va-preset-popover`, `.va-scope-chip`, sticky budgets, and `@media print`.

### Delivery Medium Physics
- [mediums/m1-paper-and-print.md](mediums/m1-paper-and-print.md): Paper & Print sheet physics, `@page` rules, high-contrast ink, and unrolled figures.
- [mediums/m2-editorial-web.md](mediums/m2-editorial-web.md): Editorial monographs, RFC specifications, research briefs, and multi-column figures.
- [mediums/m3-stateful-web-app.md](mediums/m3-stateful-web-app.md): Stateful workbenches, `.va-workbench-panes` hairline panes, opaque `.va-side-rail` + single-row `.va-rail-footer`, 2-stop density cap, `.va-split-reader-gallery` (`>= 60%` prose + `dialog.va-modal-sheet[closedby="any"]`), shortcut suppression while `dialog[open]`, `.va-kpi-gauge-card`/`.va-kpi-card`, `.va-toolbar-joined`, `.va-tab-strip`, `.va-plot-row` `subgrid`, `1480px` cap, and `observeChartResize`.
- [mediums/m4-walkup-poi-terminal.md](mediums/m4-walkup-poi-terminal.md): Point-of-Interest kiosks, guarded touch targets, and high-visibility contrast.
- [mediums/m5-ambient-wall-kiosk.md](mediums/m5-ambient-wall-kiosk.md): 10-foot ambient wall displays, high-readability telemetry, and status glanceability.
- [mediums/m6-collimated-optical-hud.md](mediums/m6-collimated-optical-hud.md): Collimated optical HUD, >=65% central keep-out, peripheral symbology, and monochrome green/cyan.
- [mediums/m7-transparent-window-overlay.md](mediums/m7-transparent-window-overlay.md): Variable luminance smoked scrims, stroke text halos, and environmental glare rejection.

---

## 4. Portable HTML/CSS Auditor (`scripts/audit_quiet_html.py`)

Verify any external HTML/CSS/JS asset tree or live localhost URL (`~/.agents/skills/quiet-ui/` or `skills/quiet-ui/`) against Quiet UI styling (`[HIDDEN_LAYER]`, `[IMPORTANT]`, `[FONT_FLOOR]`), `.quiet-ui.md` blocklists (`[BLOCKLIST_RESURRECTION]`), `--strict-drift` (`[TOKEN_BYPASS_HEX]`, `[INLINE_STYLE_SPRAWL]`), form/disabled/key contracts (`[UNLABELED_FORM_CONTROL]`, `[DEAD_END_ZERO_STATE]`, `[DISABLED_CONTROL_LOW_CONTRAST]`, `[PARAM_KEY_MIDWORD_WRAP]`), chrome budgets (`[STICKY_CHROME_BLOAT]`, `[DENSITY_STOP_SPRAWL]`, `[RAIL_FOOTER_CLUTTER]`, `[PROSE_PANE_CRAMPED]`, `[TREE_NESTED_CARD_BORDERS]`, `[PLOT_AXIS_MISALIGN]`, `[PILL_SPRAWL]`, `[NAVBAR_SHIFT]`, `[PANE_CONTROL_CLIPPED]`), editorial/print checks (`[PRINT_FLOW_COLLISION]`, `[PRINT_EDGE_CLIP]`, `[PROSE_COLUMN_STARVATION]`, `[NESTED_PROSE_SCROLL]`, `[CODE_LUMINANCE_SHOCK]`, `[DIAGONAL_TICK_OR_ROTATED_Y_TITLE]`, `[END_LABEL_CLIP]`), data honesty (`[SELF_BADGE]`, `[FAKE_UNBOUNDED_GAUGE]`, `[JSON_MOCK_FIXTURE]`, `[EMOJI_IN_CHROME]`, `[JARGON_TERMINOLOGY]`), and SVG bounds (`[AXIS_LABEL_CLIPPED]`, `[BAR_HAIRLINE_DENSITY]`, `[SVG_LABEL_STROKE_COLLISION]`):

```bash
# Scaffold .quiet-ui.md and run static + strict drift audit (auto-discovers .quiet-ui.md)
python3 -B scripts/audit_quiet_html.py --init-context path/to/repo/.quiet-ui.md
python3 -B scripts/audit_quiet_html.py path/to/web/v9 --context path/to/repo/.quiet-ui.md --strict-drift

# Live Headless Chrome sweep across 390px, 820px, and 1440px (requires selenium + Chrome)
python3 -B scripts/audit_quiet_html.py http://127.0.0.1:8788/ --cdp --mount-prefix /web=/path/to/web
```

---

## 5. Integration with Complementary Pillars
- **Quantitative Metrology & Schematics**: Consult [quiet-evidence](../quiet-evidence/SKILL.md) for calibrated plots, bitfields, HIL waveforms, and topologies.
- **Audience Translation & Murder Board**: Consult [quiet-bridge](../quiet-bridge/SKILL.md) for persona scrub rubrics and review-room dual-layer patterns.
