# Changelog

All notable changes to **Quiet UI Skills** are documented in this file following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

## [9.2.1] - 2026-11-21

### Added
- **Terminal `@layer utilities` `.hidden` Rule (`src/css/00-layers-and-reset.css`) + `[HIDDEN_LAYER]` Lint**: Defined `@layer utilities { .hidden, [hidden]:not([hidden="until-found"]) { display: none; } }` so `.hidden` beats earlier `shell`/`views` flex/grid rules without `!important` while preserving Find-in-page (`beforematch`) searchability, and flagged `.hidden` / bare `[hidden]` placed in non-final `@layer` blocks (`[HIDDEN_LAYER]`).
- **Cross-Plot Axis Spines & `R x C` Pixel Registration (`QuietSvgLayout` + `QuietEChartsDefaults`)**: Added `buildCanonicalTimeGrid`, `sharedNiceScale125`, and `computeGridFrameGutters` (`src/js/quiet-svg-chart-layout.js`) plus `alignPlotGridFrames` / `alignSharedAxes` (`src/js/echarts-layout-defaults.js`) to synchronize zero-filled X buckets, unit-matched `1–2–5` Y bounds, and column/row `containLabel: false` pixel gutters (`<= 2px` `[PLOT_AXIS_MISALIGN]`), paired with `.va-plot-row` / `.va-plot-grid` CSS `subgrid` alignment (`>= 780px`).
- **ECharts `390px` Scroll & Dual-Axis Legend Guard (`src/js/echarts-layout-defaults.js`, `src/js/echarts-quiet-adapter.js`)**: Added `applySafeLegendLayout(opt, containerWidth)` inside `normalizeOption` to convert narrow (`< 640px`) or non-opt-in `type: 'scroll'` legends into wrapping `'plain'` at `bottom: 0`, and anchor dual right-hand Y-axis legends to `bottom: 0` with `grid.bottom >= 38` clearance.
- **Chart Form Rules (`N`) & `.va-inline-bar` (`src/css/01-stage-and-containers.css`)**: Added `.va-inline-bar`, `.va-inline-bar-fill`, `.va-inline-bar-pin`, and `tr.va-row-compact` (`<= 32px`/row) for `N <= 8` inline bullet-bar tables; documented `N <= 3` stat/micro-bars (`<= 72px`) and zero duplicate time-series denominators.
- **Foldable `820px` Sweep, `[STICKY_CHROME_BLOAT]`, `[PLOT_AXIS_MISALIGN]` & `[PILL_SPRAWL]` (`audit_static_rules.py`, `audit_quiet_checks.py`)**: Updated `VIEWPORTS` to `((390, 844), (820, 1080), (1440, 900))`, added interval-union `[STICKY_CHROME_BLOAT]` (`> 64px`), `[PLOT_AXIS_MISALIGN]` (`> 2px`), and `[PILL_SPRAWL]` (`> 2` header stadium pills, `>= 6` passive body stadium pills, or stadium `[role="tablist"]` tabs alongside rectangular toolbars), extracted `audit_static_rules.py` (`<= 450L`), and added `--exclude`, `--audit-mounted-external`, `[MISSING_ASSET]`, and subpath-scoped `--mount-prefix`.
- **Anti-Pill Restraint, Unified Corner Family, Page-Wide Coherence & Hairline `M3` Panes (`01-stage-and-containers.css`, `02-nav-shells-and-drawers.css`, `tokens/quiet-ui-tokens.css`)**: Added `.va-meta-inline`, `.va-tab-strip`/`.va-tab`, `--chart-1..5` palette tokens, and `.va-workbench-panes`/`.va-pane`/`.va-pane-hdr` (`40px` flat hairline-divided columns with `.va-pane-count`), unified `.va-badge` / `.va-pill-btn` corners to `--radius-sm`, and documented `<= 3` repeating card structures & `<= 1` chart per half-width card.
- **`ResizeObserver` & `min-width: 0` Chart Hosts (`echarts-layout-defaults.js`, `echarts-quiet-adapter.js`, `01-stage-and-containers.css`, `05-evidence-stage.css`)**: Added `observeChartResize(hostEl, chart, opts)` (`ResizeObserver` + `requestAnimationFrame` with cleanup in `disposeWrap`), switched mounted ECharts hosts to fluid `100%` width, and enforced `min-width: 0; max-width: 100%;` across `.va-card`, `.va-pane`, `.qe-plot-wrap`, `.qe-echarts-host`, and grid children for half-screen (`~720px`) snaps.

### Fixed
- **Chrome-Scoped `[SELF_BADGE]` & Repo/Ticket Slug Exemption**: Tightened `SELF_BADGE_RE` in Python and `CDP_AUDIT_JS` to exempt kebab-case repository/ticket identifiers (`quiet-ui-skills*`) and scoped `[SELF_BADGE]` detection strictly to application chrome outside `<main>`.
- **Coarse-Pointer `44px` vs. `20–22px` Read-Only Badges (`src/css/01-stage-and-containers.css`, `tokens/quiet-ui-tokens.css`)**: Scoped `44px` hit sizing to interactive controls on `< 700px` handsets (or coarse `< 768px`), kept `>= 768px` coarse tablet/foldable toolbars at `32–34px`, protected static `.va-pill` / `.va-badge` chips at `20–22px`, added `.va-overlay-control` `::after` invisible `44x44px` hit areas, and lowered `.va-split-reader` / `.va-chart-grid-2` foldable breakpoints from `860px` to `>= 780px`.

## [9.2.0] - 2026-11-21

### Added
- **Data-First Widget Binding (`skills/quiet-ui/foundation/data-grounding-and-widget-binding.md`)**: Mandates inspecting live data schemas before picking specimens (`Data-to-Widget Binding Map`), omitting unbacked sub-slots cleanly, labeling thin buffers as `Warming up — N samples collected`, blocking retroactive scoring against new thresholds, and banning inline demo mock arrays, Quiet self-badges in app chrome, and exposed `brain:` storage prefixes.
- **Component Library v9.2 (`41 Specimens` + Data Contracts)**: Added Specimen 37 (`.va-kpi-gauge-card` 4-up/2-up gauges omitting unbacked targets & marking warmup), Specimen 38 (`.va-toolbar-joined` 27px desktop / 44px touch ARIA toolbar), and `Data Inputs & Honest Fallback` disclosures on all 41 specimens.
- **Browser SVG & ECharts Chart Layout Helpers (`src/js/quiet-svg-chart-layout.js`, `src/js/echarts-layout-defaults.js`)**: Bundled `window.QuietSvgLayout` (`niceScale125`, `wrapLabelLines`, `measureCategoryGutter`, `filterNonOverlappingTicks`, `placeReferenceLabel`) into `quiet-evidence-bundle.js` and enforced ECharts `containLabel: true` + haloed inside `markLine` defaults and non-truncating mobile label wrapping.
- **Upgraded Portable Auditor (`skills/quiet-ui/scripts/audit_quiet_html.py` + `audit_quiet_checks.py`)**: Added `--web-root`, repeatable `--mount-prefix /prefix=dir`, `--allow-showcase-chrome`, static/DOM honesty checks (`[SELF_BADGE]`, `[INTERNAL_ID]`, `[INLINE_MOCK_DATA]`), and CDP `390px / 900px / 1440px` detection of SVG text/line overlaps (`[SVG_TEXT_OVERLAP]`, `[SVG_LINE_COLLISION]`) and unclosed/clipped labels (`[LABEL_TRUNCATED]`).

### Fixed
- **`install.sh`**: Removed `"visual-architecture-system"` from the legacy skill purge loop so `./install.sh` preserves external installed visual skills.
- **`schedule_and_heatmap.py` Gantt Halos**: Enabled SVG knockout halos on Gantt float/duration/milestone annotations that cross vertical gridlines.
- **M3 Foldable & Mixed-Aspect Rules**: Lowered split-reader breakpoint to `>= 860px`, compacted sticky `< 1100px` chrome to brand-only, documented GFM checkbox bullet cleanup, and added `.va-media-contain` + orientation-aware `.va-compare-grid`.

## [9.1.0] - 2026-11-20

### Added
- **Portable Agent Skills (`skills/`)**:
  - Added bundled standalone assets in `skills/quiet-evidence/assets/` (`quiet-evidence-bundle.css` and `quiet-evidence-bundle.js`) so `compile_evidence.py --out` renders full Quiet UI styling and waveform cursor scrubbing outside the repository.
  - Added `skills/quiet-ui/scripts/audit_quiet_html.py`, a universal zero-dependency static HTML/CSS linter (with optional `--cdp` Headless Chrome sweep) for any external file, directory, or URL.
  - Added CLI & Python API documentation to `skills/quiet-evidence/SKILL.md` and auditor usage to `skills/quiet-ui/SKILL.md`.
- **AI Agent & GitHub Community Standards**:
  - Added `AGENTS.md` (following the Agentic AI Foundation `agents.md` open standard) and `CLAUDE.md`.
  - Added `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `CHANGELOG.md`, `pyproject.toml`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, and `.github/workflows/ci.yml`.
- **Unified Build & Test Architecture**:
  - Added `scripts/build_all.py` with `--check` zero-drift verification for CI.
  - Consolidated verification into `python3 -B -m unittest discover -s tests -v` (`test_compilers.py`, `test_corpora.py`, `test_portable_auditor.py`, `test_repo_hygiene.py`, `test_cdp_visuals.py` + `tests/cdp_gates/`).

### Changed
- Flattened `src/v9/` directly into `src/` (`chrome/`, `css/00..11`, `js/`, `views/`) and renamed `scripts/build_v9_showcase.py` -> `scripts/build_showcase.py`.
- Renamed README hero asset to `docs/assets/quiet-ui-hero.png` with cross-platform font lookup in `scripts/build_readme_hero.py`.
- Replaced process-seeded `hash()` with `zlib.crc32()` in `plot_compiler.py` for 100% byte-deterministic builds across runs and platforms.
- Enforced `>= 11px` font floor on mobile Studio tabs (`04-studio-portal.css`) and explicit `aria-hidden="true"` on decorative `v08` sparkline `<svg>`.

### Removed
- Removed dormant v8 carryover templates (`src/tiers/`), unused v8 CSS/JS, 6-line `skills/quiet-ui/references/` stubs, duplicate `docs/v9/` showcase archive, and machine-specific scripts (`scripts/sync_mirrors.sh`, `scripts/verify_*.py`, `scripts/build_master_showcase.py`, `scripts/fetch_nasa_corpus.py`).

## [9.0.0] - 2026-11-20

### Added
- Unified 3-pillar Studio (`6 Domains · 21 Views`) and self-contained 39-specimen Component Library (`docs/bench/evidence-bench.html`) supporting `White`, `Paper`, `Dark-Paper`, and `Dark` themes.
- Directional audience views (`v19`, `v20`, `v21`), Sankey power balance, 2D scatter cloud, 4-track telemetry strip chart, physiological ABP waveform, and vendored offline Apache ECharts SVG adapter.
- Clean-room open-standards SVG compilers (`ITU-T Z.120` sequence, `NASA SP-2016-6105` $N^2$ matrix, `NRC NUREG-0492` fault tree) and `181` numerical conservation checks across 6 domain corpora.
