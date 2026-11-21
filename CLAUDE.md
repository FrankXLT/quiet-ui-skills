# CLAUDE.md

Read and follow [AGENTS.md](AGENTS.md) as the authoritative instruction set for this repository.

- **Architecture & Workflows**: See [docs/WORKFLOWS.md](docs/WORKFLOWS.md) and [llms.txt](llms.txt).
- **Data-First Grounding**: Inspect live data schemas first per [skills/quiet-ui/foundation/data-grounding-and-widget-binding.md](skills/quiet-ui/foundation/data-grounding-and-widget-binding.md); omit unbacked sub-slots and disclose `Warming up — N samples collected` when `N < 10`.
- **Skill Entrypoints**: [skills/quiet-ui/SKILL.md](skills/quiet-ui/SKILL.md), [skills/quiet-evidence/SKILL.md](skills/quiet-evidence/SKILL.md), and [skills/quiet-bridge/SKILL.md](skills/quiet-bridge/SKILL.md).
- **Zero-Drift Build & Verification**: Run `python3 -B scripts/build_all.py --check` and `python3 -B -m unittest discover -s tests -v` before committing.
