# Changelog

All notable changes to **Quiet UI Skills** are documented in this file following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

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
