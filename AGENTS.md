# AGENTS.md — Quiet UI Skills (`v9.4.0`)

Instructions for AI coding agents working in or consuming `quiet-ui-skills`. Follow the mode boundary, commands, and invariants below verbatim.

---

## 1. Mode Selection (Choose One First)

1. **Using Quiet UI Skills (Default for Application & Visualization Tasks)**:
   - Inspect target root for `.quiet-ui.md` first (`--init-context` to scaffold) and bind every view strictly from real API/schema fields via `skills/quiet-ui/foundation/data-grounding-and-widget-binding.md`.
   - Compile quantitative evidence specs via `skills/quiet-evidence/scripts/compile_evidence.py` (or `window.QuietSvgLayout` for dynamic browser SVG plots).
   - Audit generated HTML/CSS/JS via `skills/quiet-ui/scripts/audit_quiet_html.py` (auto-discovers `.quiet-ui.md`; add `--strict-drift` for token bypasses and inline style drift).
   - Brand or personalize a showcase by cloning `customizations/brand-starter/` or `customizations/personal-starter/` into `customizations/<my-brand>/`.
   - **Treat `skills/`, `tokens/`, and both `*-starter/` directories as strictly READ-ONLY.**
2. **Contributing to Quiet UI Core**:
   - Edit source modules in `src/`, compilers in `skills/quiet-evidence/scripts/compilers/`, skill docs in `skills/`, scripts in `scripts/`, or tests in `tests/`.
   - Always regenerate all derived outputs with `python3 -B scripts/build_all.py` after editing core sources, tokens, or `llms.txt`.

---

## 2. Exact Build, Audit, Test & Preview Commands

```bash
# Install Antigravity plugin + portable skills (~/.agents/skills/{quiet-ui,quiet-evidence,quiet-bridge})
./install.sh

# Compile a deterministic evidence figure or standalone HTML5 document (zero runtime deps)
python3 -B skills/quiet-evidence/scripts/compile_evidence.py spec.json --rigor L3 --theme white --out chart.html
python3 -B skills/quiet-evidence/scripts/compile_evidence.py spec.json --fragment

# Initialize .quiet-ui.md and audit external HTML/CSS/JS tree or URL (--strict-drift / --cdp)
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py --init-context path/to/repo/.quiet-ui.md
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py path/to/web/v9 --mount-prefix /web=/path/to/web --exclude "*.min.js" --strict-drift
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py http://127.0.0.1:8788/ --cdp --context path/to/repo/.quiet-ui.md

# Sync mirrors, rebuild skills/quiet-evidence/assets/, Studio, Component Library & starters
python3 -B scripts/build_all.py
python3 -B scripts/build_all.py --check

# Run zero-dependency unit, corpora, hygiene & portability tests (skips CDP if Chrome absent)
python3 -B -m unittest discover -s tests -v

# Run full verification including all 21 Studio CDP gates + 44 Bench specimens + /docs root test
QUIET_REQUIRE_CDP=1 python3 -B -m unittest discover -s tests -v

# Serve local preview (http://127.0.0.1:8788/)
python3 -B scripts/serve_showcase.py --port 8788
```

---

## 3. Repository Map

| Path | Purpose |
| :--- | :--- |
| `skills/quiet-ui/` | Pillar 1 router (`SKILL.md`), foundation (`data-grounding-and-widget-binding.md`, `brownfield-retrofit-and-migration.md`, `forms-states-and-resilience.md`, `tokens-and-surfaces.md`, `typography-and-hierarchy.md`, `chromatic-purpose-budgets.md`, `navigation-morphing.md`), 7 mediums (`M1–M7`), `tokens/`, portable `scripts/audit_quiet_html.py` + `audit_ux_and_drift.py`. |
| `skills/quiet-evidence/` | Pillar 2 router, metrology guides, deterministic compilers, and standalone `assets/quiet-evidence-bundle.{css,js}` (incl. CJK-safe `QuietSvgLayout` + `QuietEChartsDefaults` + `QuietPeriodStepper`). |
| `skills/quiet-bridge/` | Pillar 3 router, 7 audience lenses, 3 decision tempos, and `.quiet-ui.md`-aware Intake / Murder Board / Dual-Layer protocols. |
| `tokens/` | Canonical MIT-licensed 4-theme CSS custom properties (`white`, `paper`, `dark-paper`, `dark`, incl. `--bg-subtle`). |
| `customizations/` | MIT starter kits (`personal-starter/`, `brand-starter/`) and starter build/verify scripts. |
| `content/corpora/` | 6 domain corpora (`21` views, `26` JSON specs, `181` conserved metric checks) + attribution docs. |
| `src/` | First-party Studio shell (`chrome/`), `@layer` CSS (`css/00..14`), JS runtimes (`js/` incl. `quiet-svg-chart-layout.js`, `quiet-time-binning.js`, `quiet-cyclical-whiskers.js`, `quiet-period-stepper.js`), and domain builders (`views/`). |
| `docs/` | GitHub Pages web root (`index.html`, `bench/evidence-bench.html` with `44` specimens, `WORKFLOWS.md`, vendored `echarts.min.js`, CC0/PD photos). |
| `scripts/` | Build & preview CLI (`build_all.py`, `build_showcase.py`, `build_evidence_bench.py`, `bench_forms_specimen.py`, `build_readme_hero.py`, `serve_showcase.py`). |
| `tests/` | Unified `unittest` suite (`test_compilers.py`, `test_corpora.py`, `test_portable_auditor.py`, `test_repo_hygiene.py`, `test_cdp_visuals.py`, `test_v922_hardening.py`, `test_v922_round2.py`, `test_v930_endstate_lessons.py`, `test_v940_context_forms_drift.py`). |
| `quiet-ui-showcase.html` | Compiled standalone 6-domain, 21-view Studio portal (mirrored byte-for-byte to `docs/index.html`). |

---

## 4. Pillar Invocation Contracts & Schema Matrix

### Pillar 1 — `quiet-ui` (7 Delivery Mediums, Forms/Zero-States, Brownfield & `N0–N4`)
- Declare **`Project Mode: Greenfield | Brownfield Retrofit`** first (`skills/quiet-ui/SKILL.md` + `foundation/brownfield-retrofit-and-migration.md`), persisting `.quiet-ui.md` (`Strict Drift`, `--mount-prefix`, `Capability Parity Ledger`, `Deprecation Blocklist`), `layer(legacy)` cascade quarantine + Guardrail 6 Day-30 Extract & Normalize (`[TOKEN_BYPASS_HEX]`, `[INLINE_STYLE_SPRAWL]`, `[BLOCKLIST_RESURRECTION]`), and **Data-to-Widget Binding Map** (`data-grounding-and-widget-binding.md`): omit absent sub-slots, render visible on-card legends for `>= 2` series (`[ORPHAN_SERIES_LEGEND]`), use trackless `.va-kpi-card` on unbounded totals (`[FAKE_UNBOUNDED_GAUGE]`), use effective-dated rate epochs + `SHA-256[:12]` showcase sanitization, show `Warming up — N samples collected` when `N < 10`, and ban mock JS/JSON fixtures (`[JSON_MOCK_FIXTURE]`), chrome emojis (`[EMOJI_IN_CHROME]`), or Quiet self-badges.
- Enforce **Accessible Forms, 4-Way Zero-States & 3-Tier Reversibility** (`foundation/forms-states-and-resilience.md` + `14-forms-and-states.css`): label all controls (`[UNLABELED_FORM_CONTROL]`), trigger `:user-invalid`/`.va-field-error` only after `blur`/`submit` and clear on `input`, explain blocked controls via `.va-gate-reason`, give every `filtered` zero-state a 1-click `Clear filters` button (`[DEAD_END_ZERO_STATE]`), retain `.va-stale-retained` cached values, and use `>= 7s` hover/focus-paused `.va-undo-toast` for soft actions.
- Select one medium (`M1–M7`): `M3` declares stage archetypes `.va-stage[data-stage="canvas|workbench|ops"]` + `[data-width="reading|workbench"]` (`[WORKBENCH_STAGE_TUNNEL]`), single-owner nav (`N4` hides top `.va-tab-strip`, `[DUPLICATE_PRIMARY_NAV]`), `<= 22%` chrome height (`<= 25%` `[CHROME_HEIGHT_BUDGET]`), `20px` caret + `2.25rem` `.va-tree-children` indent (`[TREE_INDENT_INVERSION]`), bordered `.va-toolbar-joined` (`[UNBORDERED_SEGMENTED_TRACK]`), `.va-workbench-panes`/`.va-pane-hdr` (`40px`), left-of-brand topbar drawer toggle + closed-by-default opaque `.va-side-rail[data-mode="overlay"]` + single-row `40px` `.va-rail-footer` (`.va-swatch-row` left + `Compact -> d3` / `Comfortable -> d2` right, `[DENSITY_STOP_SPRAWL]`, `[RAIL_FOOTER_CLUTTER]`), `.va-split-reader-gallery` (`>= 60%` prose `>= 760px` + `< 760px` `dialog.va-modal-sheet[closedby="any"]`), bounded `.va-period-stepper`, `.va-scope-chip`, `.booktabs td[data-nowrap]`, and Guardrail 7 parity (`[VISIBLE_HITBOX_OUTLINE]`, `[RAW_SLUG_OR_GRAMMAR_LEAK]`).
- Enforce **Page-Wide Coherence & Sticky Budgets**: `<= 3` repeating card structures, unified `.booktabs`, one `--chart-1..5` palette, plain `.va-meta-inline`, `<= 1` `.va-badge`/header (`[PILL_SPRAWL]`), and `<= 88px` (`< 680px`) / `<= 64px` (`>= 680px`) sticky chrome (`[STICKY_CHROME_BLOAT]`, `[NAVBAR_SHIFT]`, `[PANE_CONTROL_CLIPPED]`).

### Pillar 2 — `quiet-evidence` (Metrology & Offline Schemas)
- Supported canonical `$schema` URNs: `urn:quiet-ui:schema:v9:scalar`, `table`, `bitfield`, `plot` (`cartesian`, `waterfall`, `stacked_bar`, `gantt`, `heatmap`, `dumbbell`, `forest`, `sankey`), `waveform` (incl. `strip_chart`), and `schematic` (`sequence`, `n2_matrix`, `fault_tree`, `pid_loop`, `differential_bus`, `enclave_topology`, `er_lineage`).
- Dynamic browser plots use `window.QuietSvgLayout` (`niceScale125`, `sharedNiceScale125`, `buildCanonicalTimeGrid`, `computeGridFrameGutters`, wide-script/CJK `visualUnits` + `wrapLabelLines` + `measureCategoryGutter`, `filterNonOverlappingTicks`, `placeReferenceLabel`), `QuietSankeyLayout` (`sortColumnsTopologically`, `computeActiveSlice`, `dedupeStemEmail`), `QuietTimeBinning` (`binTimeSeries` `1h`/`1d`/`1w`, `resolvePeriodBounds`, `heatmapZeroCellStyle` with `oklch`/`var(--)`), `QuietPeriodStepper` (`resolveWindowBounds`, `setPeriodMode`), and `QuietEChartsDefaults` (`buildCyclicalWhiskerOption`, `trimTrailingFutureWeeks`, `alignPlotGridFrames`/`alignSharedAxes`). Keep `N <= 3` as stat/micro-bars and `N <= 8` as `.va-inline-bar` tables.
- Standalone usage outside this repo works cleanly via bundled `skills/quiet-evidence/assets/quiet-evidence-bundle.{css,js}` and `skills/quiet-evidence/scripts/compile_evidence.py`.

### Pillar 3 — `quiet-bridge` (Audience Lenses & Numerical Conservation)
- Check/persist `.quiet-ui.md` in `protocols/grill-me-audience-intake.md`, use plain everyday UI copy across headings and chart titles (e.g. `"Activity by Hour of Day"`, never jargon `"diurnal"`, `[JARGON_TERMINOLOGY]`), and preserve truth across `L1` Executive (`BLUF` + delta risk), `L2` Peer Engineering (`1–2–5` tolerances + traceability), and `L3` Operator / Patient / Learner (`<= 12` jargon terms).
- Enforce the **Numerical Conservation Law**: quantitative claims across prose, KPI scalars, and figures MUST bind to one canonical dataset, omit unbacked targets, and disclose `Warming up — N samples collected` on thin buffers.

---

## 5. CSS `@layer` Cascade & Status Pill Grammar

- Preserve the canonical cascade order declared in `src/css/00-layers-and-reset.css`:
  `@layer reset, tokens, shell, archetypes, evidence, views, utilities;` (declare `evidence` before `views` so app views override component defaults cleanly, declare `utilities` last, and place `.hidden, [hidden]:not([hidden="until-found"]) { display: none; }` inside `@layer utilities`).
- Never write `!important` in stylesheets, inline styles, or templates.
- All themes bind semantically through `[data-theme]` on `<html>`: `white` (default), `paper`, `dark-paper`, and `dark`.
- Use the 4-variant `.va-pill` grammar (`data-variant="status|tag|chip"` with `data-state="nominal|warn|fault"`, plus borderless SVG knockout halos) backed strictly by semantic tokens (`--status-ok`, `--status-warn`, `--status-danger`, `--status-err`)—never color nominal telemetry amber or crimson.

---

## 6. Hard Architectural & Negative Rules (`DO NOT`)

- **DO NOT add required third-party runtime dependencies**: Core skills and compilers must run on pure Python stdlib (`>= 3.10`). `selenium` and `pillow` belong strictly in `[project.optional-dependencies] dev`.
- **DO NOT exceed file line budgets**: Every `.py`, `.js`, `.css`, `.md`, and `.json` source/doc file must stay **`<= 450` lines** (`SKILL.md <= 140` lines; `AGENTS.md` `115–155` lines; `docs/WORKFLOWS.md` `250–450` lines; only compiled showcases/bench/bundles are exempt).
- **DO NOT use `!important` anywhere in CSS or HTML** or violate the **`>= 11px` computed font floor** in UI controls, tables, or pills.
- **DO NOT hand-write SVG coordinates or evaluate unsafe math strings**: Author `urn:quiet-ui:schema:v9:<modality>` JSON and compile via `compile_evidence.py` (`ast`-only math evaluation).
- **DO NOT connect discrete empirical data points with Bezier splines** or omit physical units / measurement tolerances.
- **DO NOT edit mirrored files independently**: Modify `tokens/quiet-ui-tokens.css` or `llms.txt` at the root and propagate strictly via `python3 -B scripts/build_all.py` (never edit `docs/index.html`, `docs/bench/evidence-bench.html`, or `skills/quiet-evidence/assets/` by hand).
- **DO NOT mix license boundaries or leak private strings**: Core engine (`skills/`, `src/`, `scripts/`, `tests/`) is **Apache-2.0**; `tokens/`, `customizations/`, and all user-generated output are **MIT** (`0` attribution obligations). Keep private IPs, internal hostnames, and personal machine paths out of committed diffs.

---

## 7. Definition of Done

Before committing or opening a pull request:
1. Run `python3 -B scripts/build_all.py` and verify `python3 -B scripts/build_all.py --check` exits `0`.
2. Verify `python3 -B -m unittest discover -s tests -v` passes (`QUIET_REQUIRE_CDP=1` for UI/CSS/SVG/compiler changes).
3. Verify `python3 -B skills/quiet-ui/scripts/audit_quiet_html.py` passes on any added or edited HTML/CSS artifacts.
4. Confirm `git status` contains zero temporary scratch files or unintended edits to `skills/` / `*-starter/`.
