# Changelog

All notable changes to **Quiet UI Skills** are documented in this file following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

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
