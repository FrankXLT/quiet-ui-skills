# AGENTS.md — Quiet UI Skills (`v9.2.0`)

Instructions for AI coding agents working in or consuming `quiet-ui-skills`. Follow the mode boundary, commands, and invariants below verbatim.

---

## 1. Mode Selection (Choose One First)

1. **Using Quiet UI Skills (Default for Application & Visualization Tasks)**:
   - Bind every view strictly from real API/schema fields first via `skills/quiet-ui/foundation/data-grounding-and-widget-binding.md`.
   - Compile quantitative evidence specs via `skills/quiet-evidence/scripts/compile_evidence.py` (or `window.QuietSvgLayout` for dynamic browser SVG plots).
   - Audit generated HTML/CSS/JS via `skills/quiet-ui/scripts/audit_quiet_html.py`.
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

# Audit any external HTML/CSS/JS tree or URL (static stdlib or --cdp across 390px, 900px, 1440px)
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py path/to/page.html --web-root path/to/dist
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py http://127.0.0.1:8788/ --cdp --mount-prefix /web=/path/to/web

# Sync mirrors, rebuild skills/quiet-evidence/assets/, Studio, Component Library & starters
python3 -B scripts/build_all.py
python3 -B scripts/build_all.py --check

# Run zero-dependency unit, corpora, hygiene & portability tests (skips CDP if Chrome absent)
python3 -B -m unittest discover -s tests -v

# Run full verification including all 21 Studio CDP gates + 41 Bench specimens + /docs root test
QUIET_REQUIRE_CDP=1 python3 -B -m unittest discover -s tests -v

# Serve local preview (http://127.0.0.1:8788/)
python3 -B scripts/serve_showcase.py --port 8788
```

---

## 3. Repository Map

| Path | Purpose |
| :--- | :--- |
| `skills/quiet-ui/` | Pillar 1 router (`SKILL.md`), data-grounding contract, 7 delivery mediums (`M1–M7`), `tokens/`, portable `scripts/audit_quiet_html.py`. |
| `skills/quiet-evidence/` | Pillar 2 router, metrology guides, deterministic compilers, and standalone `assets/quiet-evidence-bundle.{css,js}` (incl. `QuietSvgLayout`). |
| `skills/quiet-bridge/` | Pillar 3 router, 7 audience lenses, 3 decision tempos, and Murder Board / Dual-Layer protocols. |
| `tokens/` | Canonical MIT-licensed 4-theme CSS custom properties (`white`, `paper`, `dark-paper`, `dark`). |
| `customizations/` | MIT starter kits (`personal-starter/`, `brand-starter/`) and starter build/verify scripts. |
| `content/corpora/` | 6 domain corpora (`21` views, `26` JSON specs, `181` conserved metric checks) + attribution docs. |
| `src/` | First-party Studio shell (`chrome/`), `@layer` CSS (`css/00..11`), JS runtimes (`js/` incl. `quiet-svg-chart-layout.js`), and domain builders (`views/`). |
| `docs/` | GitHub Pages web root (`index.html`, `bench/evidence-bench.html`, `WORKFLOWS.md`, vendored `echarts.min.js`, CC0/PD photos). |
| `scripts/` | Build & preview CLI (`build_all.py`, `build_showcase.py`, `build_evidence_bench.py`, `build_readme_hero.py`, `serve_showcase.py`). |
| `tests/` | Unified `unittest` suite (`test_compilers.py`, `test_corpora.py`, `test_portable_auditor.py`, `test_repo_hygiene.py`, `test_cdp_visuals.py`). |
| `quiet-ui-showcase.html` | Compiled standalone 6-domain, 21-view Studio portal (mirrored byte-for-byte to `docs/index.html`). |

---

## 4. Pillar Invocation Contracts & Schema Matrix

### Pillar 1 — `quiet-ui` (7 Delivery Mediums & `N0–N4` Morphing Shells)
- Draft a **Data-to-Widget Binding Map** first (`skills/quiet-ui/foundation/data-grounding-and-widget-binding.md`): omit absent sub-slots, never borrow targets across cards, show `Warming up — N samples collected` when `N < 10`, and ban inline mock arrays or Quiet self-badges in app chrome.
- Select one primary medium matching physical viewing distance and chrome weight:
  - `M1` Paper & Print (`0%` box weight, static SVG fallback, `break-inside: avoid`)
  - `M2` Editorial Web / Spec / RFC (`15%–25%` hairline rules, prose measure `<= 72ch`)
  - `M3` Stateful Web App / Workbench (`N1` left spine or `N3` dual nav, compact `.va-toolbar-joined`, `.va-kpi-gauge-card`, unfolded foldable split reader at `>= 860px`)
  - `M4` Walk-Up POI Terminal (`N1` zone rail, guarded `ARM -> EXECUTE` effectors, `>= 44px` touch targets)
  - `M5` Ambient Wall Kiosk (10-foot luminance figure-ground contrast, enlarged telemetry readouts)
  - `M6` Collimated Optical HUD (`>= 65%` open central sightline, monochrome phosphor peripheral symbology)
  - `M7` Transparent Window Overlay (smoked-glass `.va-hud-pod` cards, stroke text halos, glare rejection)
- Never activate bottom mobile dock `N4` at desktop/tablet widths (`>= 700px`), never invent single-page jump sidebars on clean single-scroll views, and hide subheader utility bars on sticky `< 1100px`.

### Pillar 2 — `quiet-evidence` (Metrology & Offline Schemas)
- Supported canonical `$schema` URNs: `urn:quiet-ui:schema:v9:scalar`, `table`, `bitfield`, `plot` (`plot_kind`: `cartesian`, `waterfall`, `stacked_bar`, `gantt`, `heatmap`, `dumbbell`, `forest`, `sankey`), `waveform` (including `waveform_kind: "strip_chart"`), and `schematic` (`sequence` `ITU-T Z.120`, `n2_matrix` `NASA SP-2016-6105`, `fault_tree` `NRC NUREG-0492`, `pid_loop`, `differential_bus`/`can_fd`/`fieldbus`/`rs485`/`modbus`/`mil1553b`, `enclave_topology`, `er_lineage`).
- Dynamic browser-built SVGs use `window.QuietSvgLayout` (`niceScale125`, `wrapLabelLines`, `measureCategoryGutter`, `filterNonOverlappingTicks`, `placeReferenceLabel` with knockout halos); ECharts plots use `containLabel: true` and haloed `markLine` defaults, falling back identically to deterministic Python SVGs.
- Standalone usage outside this repo works cleanly via bundled `skills/quiet-evidence/assets/quiet-evidence-bundle.{css,js}` and `skills/quiet-evidence/scripts/compile_evidence.py`.

### Pillar 3 — `quiet-bridge` (Audience Lenses & Numerical Conservation)
- Tailor framing without mutating physical ground truth across `L1` Executive / Board (`BLUF` top card + delta risk), `L2` Peer / Review Engineering (`1–2–5` tolerances + traceability), and `L3` Operator / Patient / Learner (`<= 12` technical jargon terms, plain-English action guidance).
- Enforce the **Numerical Conservation Law**: quantitative claims across narrative prose, KPI scalars, and compiled figures MUST bind to one canonical JSON dataset, omit unbacked targets, and disclose `Warming up — N samples collected` on thin buffers.

---

## 5. CSS `@layer` Cascade & Status Pill Grammar

- Preserve the canonical cascade order declared in `src/css/00-layers-and-reset.css`:
  `@layer reset, tokens, shell, archetypes, views, evidence, utilities;`
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
