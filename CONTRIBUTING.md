# Contributing to Quiet UI Skills

Thank you for contributing to Quiet UI Skills! Both human contributors and AI coding agents follow the same lightweight, deterministic engineering rules.

---

## 1. Architecture & Licensing Boundaries

Quiet UI Skills is structured into three orthogonal pillars plus MIT starter kits:

- **`skills/quiet-ui/` (Apache-2.0)**: Delivery medium physics (`M1–M7`), polymorphic shells (`N0–N4`), and the portable `audit_quiet_html.py` HTML/CSS linter.
- **`skills/quiet-evidence/` (Apache-2.0)**: Deterministic JSON-to-SVG/HTML evidence compilers across 6 modalities (`scalar`, `table`, `bitfield`, `plot`, `waveform`, `schematic`), NIST SP 811 unit calculus, and `1–2–5` ticks.
- **`skills/quiet-bridge/` (Apache-2.0)**: Asymmetric audience translation across 7 audience lenses, 3 decision tempos, and Murder Board checks.
- **`tokens/` & `customizations/` (MIT)**: Standalone 4-theme CSS custom properties and starter kits (`personal-starter/`, `brand-starter/`). Outputs produced by Quiet UI Skills are 100% MIT with zero attribution obligations.

See [AGENTS.md](AGENTS.md) and [docs/WORKFLOWS.md](docs/WORKFLOWS.md) for the complete architecture contract.

---

## 2. Development Setup

### Zero-Dependency Contributor Path (Python `>= 3.10` Stdlib Only)

Core builders, compilers, static auditors, corpora conservation tests, and repository hygiene checks require **zero third-party `pip` packages**:

```bash
git clone https://github.com/FrankXLT/quiet-ui-skills.git
cd quiet-ui-skills
python3 -B scripts/build_all.py --check
QUIET_SKIP_CDP=1 python3 -B -m unittest discover -s tests -v
```

### Full Browser CDP Verification Setup (`[dev]`)

To run the full 21-gate Headless Chrome CDP suite and regenerate `docs/assets/quiet-ui-hero.png`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
QUIET_REQUIRE_CDP=1 python3 -B -m unittest discover -s tests -v
```

---

## 3. Common Contribution Workflows

1. **Adding an Evidence Modality or Plot Variant**:
   - Implement clean-room deterministic SVG generation under `skills/quiet-evidence/scripts/compilers/` (`<= 450` lines/file, `0` `!important`, explicit `fill=` on every `<path>`, `viewBox` + `role="img"` + `aria-label` on `<svg>`).
   - Register specimen fixtures in `docs/bench/specimens/` and add unit + isolated portability assertions in `tests/test_compilers.py`.
2. **Adding or Updating a Domain Corpus (`content/corpora/`)**:
   - Preserve exact numerical conservation across `corpus.json`, `distillation_blueprint.md`, `evidence/*.json`, and `src/views/`.
   - Document public-domain / CC0 sources in `SOURCE_ATTRIBUTION.md`.
   - Run `python3 -B -m unittest tests/test_corpora.py -v` to confirm `204+` conservation checks pass.
3. **Creating a Starter Customization (`customizations/<name>/`)**:
   - Copy `customizations/brand-starter/` or `customizations/personal-starter/` without altering the read-only starters or `skills/`.
   - Compile with `python3 -B customizations/scripts/build_showcase.py customizations/<name>` and validate with `python3 -B customizations/scripts/verify_customization.py customizations/<name> --check-immutability`.

---

## 4. Coding & Review Checklist

- Keep every source/doc file **`<= 450` lines** (`SKILL.md <= 140` lines).
- Maintain **`0` `!important`** declarations and **`>= 11px`** minimum typography.
- Never introduce external CDN dependencies (`cdnjs`, Font Awesome, Google Fonts `<link>`).
- Run `python3 -B scripts/build_all.py` whenever modifying `src/`, `tokens/`, `llms.txt`, or `docs/bench/`, then verify `python3 -B scripts/build_all.py --check` exits `0`.
- Ensure `python3 -B -m unittest discover -s tests -v` passes cleanly before opening a PR.
