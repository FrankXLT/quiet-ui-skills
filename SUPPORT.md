# Support & Documentation

## Live Previews & Documentation (`v9.8.0`)

- **Overview Hub (`/`)**: [https://FrankXLT.github.io/quiet-ui-skills/](https://FrankXLT.github.io/quiet-ui-skills/) (local [docs/index.html](docs/index.html)) — Plain-language introduction, architecture overview, and live layout preview.
- **Interactive Demo Studio (`/demo/` · 6 Domains · 26 Views)**: [https://FrankXLT.github.io/quiet-ui-skills/demo/](https://FrankXLT.github.io/quiet-ui-skills/demo/) (local `docs/demo/index.html` or [quiet-ui-showcase.html](quiet-ui-showcase.html)) — Full multi-domain studio with deep-link support (`?mode=...&domain=...&view=...`).
- **Searchable Docs Reader (`/docs/`)**: [https://FrankXLT.github.io/quiet-ui-skills/docs/](https://FrankXLT.github.io/quiet-ui-skills/docs/) (local `docs/docs/index.html`) — Plain-language guides, client-side search, and inline `quiet-evidence` diagrams.
- **3-Pillar Component Library (`53` Compiled Specimens)**: [https://FrankXLT.github.io/quiet-ui-skills/bench/evidence-bench.html](https://FrankXLT.github.io/quiet-ui-skills/bench/evidence-bench.html) (local [docs/bench/evidence-bench.html](docs/bench/evidence-bench.html))
- **Local 3-Route Preview**: Run `python3 -B scripts/build_all.py` then `python3 -B scripts/serve_showcase.py --port 8788` to inspect `/`, `/demo/`, `/docs/`, and `/bench/evidence-bench.html` locally.
- **Repository Documentation Map**:
  - [README.md](README.md) — Overview, 1-command installation, and customization quick-start
  - [AGENTS.md](AGENTS.md) — Open standard instructions and verification commands for AI agents
  - [docs/WORKFLOWS.md](docs/WORKFLOWS.md) — Deep architectural guide for `quiet-ui`, `quiet-evidence`, and `quiet-bridge`
  - [customizations/README.md](customizations/README.md) — 60-second brand & personal theme starter workflow
  - [customizations/project-site-starter/README.md](customizations/project-site-starter/README.md) — Reusable OAW 3-route project site starter (`oaw-site.json`, `/`, `/demo/`, `/docs/`)
  - [llms.txt](llms.txt) — Compact LLM-ready repository index

---

## Getting Help

- **Questions, Usage Help & Ideas**: Open an issue on [GitHub Issues](https://github.com/FrankXLT/quiet-ui-skills/issues) using the **Feature Request** or **Bug Report** template.
- **Standalone Skill Troubleshooting**:
  - Run `python3 -B skills/quiet-ui/scripts/audit_quiet_html.py <file.html>` to verify static HTML/CSS compliance without external dependencies.
  - Run `python3 -B skills/quiet-evidence/scripts/compile_evidence.py <spec.json> --out preview.html` to verify standalone evidence bundling.
- **Security Issues**: Follow [SECURITY.md](SECURITY.md) rather than posting publicly.
