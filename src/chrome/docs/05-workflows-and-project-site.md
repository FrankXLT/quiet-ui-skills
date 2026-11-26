# Workflows & Reusable Project-Site Shell

Quiet UI turns common interface, reporting, and documentation tasks into ten repeatable workflows (`WF-01` through `WF-10`). Each workflow pairs plain-language goals with built-in layout, chart, and verification rules, and `WF-10` packages the reusable **Open Agentic Workbench (OAW) Project-Site Shell** so any repository can publish an overview, optional interactive demo, and searchable docs site from one JSON manifest.

---

## The 10 Quiet UI Workflows in Plain English

Whether you are building a brand-new dashboard, cleaning up a legacy console, or publishing documentation for an open-source tool, start by matching your task to one of these ten workflows:

| Workflow | Real-World Task | What Quiet UI Enforces |
| :--- | :--- | :--- |
| **`WF-01`** | **New screen intake** | Answers who the reader is, how fast they need a decision, and which surface (`M1`–`M7`) fits before writing HTML, locking real data fields and final audit gates. |
| **`WF-02`** | **Consistent numbers across views** | Enforces the **Numerical Conservation Law**: operator, engineer, and manager views read from one verified dataset so counts, units, and limits never drift apart. |
| **`WF-03`** | **Print-ready dual physics** | Strips interactive rails, topbars, and cursors automatically in `@media print` while unwrapping tables and locking clean paper margins (`M1`). |
| **`WF-04`** | **Executive + engineer review rooms** | Pairs a top Go / Caution / No-Go summary band (1–3 minute scan) directly above full calibrated curves and waveforms (10–45 minute proof). |
| **`WF-05`** | **Clean-room schematics & starters** | Compiles sequence, fault-tree, P&ID, pipeline, and interface diagrams from JSON specs (`compile_evidence.py`), paired with MIT starter kits. |
| **`WF-06`** | **Teaching labs & student reports** | Uses concept-before-symbol pacing, linked equation colors, and structured lab reporting (claim, apparatus, repeatability bounds, and error critique). |
| **`WF-07`** | **Brownfield legacy upgrades** | Saves `.quiet-ui.md` project rules, tracks feature parity and retired selectors, isolates old CSS inside `layer(legacy)`, and strips style drift after launch. |
| **`WF-08`** | **Public data briefs vs. explorers** | Commits each page cleanly to either a focused reading brief (`N0`) or a full-width explorer with `Chart \| Table`, `Copy data`, and `Copy for AI`. |
| **`WF-09`** | **4-phase alarm lifecycles** | Separates calm monitoring from critical alerts: quiet baseline, approaching-limit warning, focused unacknowledged alert takeover, and latched diagnostics. |
| **`WF-10`** | **Reusable OAW project sites** | Compiles a static 3-route project portal (`Overview`, optional `Demo`, and searchable `Docs`) plus `1280x640` social cards from one `oaw-site.json` file. |

> [!TIP]
> You do not need to memorize workflow codes. Describe the task in plain English—such as "upgrade a legacy console without losing exports" (`WF-07`) or "publish docs with a live demo tab" (`WF-10`)—and follow the matching checklist.

---

## Reusable OAW Project-Site Shell (`WF-10`)

Instead of maintaining a heavy JavaScript framework for repository websites, `WF-10` builds a fast, zero-dependency static site from `customizations/project-site-starter/` and `customizations/scripts/build_project_site.py`.

### The Three-Route Pattern

1. **`Overview` (`index.html` at root)**: Presents the project headline, copy-ready install commands, plain-language feature blocks, optional domain preview cards, compiled architecture diagrams, and a top hub switcher linking sibling OAW projects.
2. **`Demo` (`demo/index.html`, optional)**: Wraps an interactive studio or app entry inside a subfolder with a **slim top return bar** (`Overview` and `Docs` links) and preserves query parameters such as `mode`, `view`, `world`, and `domain`. Set `routes.demo.enabled` and `demo_wrapper.enabled` to `false` for docs-only repositories.
3. **`Docs` (`docs/index.html`)**: Renders repository Markdown files into a two-column reader with a sticky table of contents, a light-dismiss mobile `<dialog closedby="any">` outline drawer, quick-jump pills, and instant client-side filtering.

```quiet-evidence
{
  "$schema": "urn:quiet-ui:schema:v9:schematic",
  "id": "oaw-project-site-flow",
  "schematic_kind": "pipeline",
  "metadata": {
    "title": "Reusable OAW Project-Site Build Pipeline",
    "description": "oaw-site.json and Markdown guides compile via build_project_site.py into Overview, Demo, Docs, and 1280x640 social previews.",
    "rigor_level": "L1",
    "audience": "Repository Maintainers"
  },
  "stages": ["1. Inputs", "2. Static Builder", "3. Published Routes"],
  "nodes": [
    { "id": "manifest", "stage": 0, "label": "oaw-site.json", "metric": "Schema v9 Manifest" },
    { "id": "markdown", "stage": 0, "label": "docs/*.md", "metric": "Guides + Diagrams" },
    { "id": "builder", "stage": 1, "label": "build_project_site.py", "metric": "Zero-Dep Compiler", "focal": true },
    { "id": "overview", "stage": 2, "label": "Overview", "metric": "index.html" },
    { "id": "demo", "stage": 2, "label": "Demo (Optional)", "metric": "demo/index.html" },
    { "id": "docs", "stage": 2, "label": "Searchable Docs", "metric": "docs/index.html" },
    { "id": "social", "stage": 2, "label": "Social Preview", "metric": "1280x640 SVG/PNG" }
  ],
  "edges": [
    { "from": "manifest", "to": "builder" },
    { "from": "markdown", "to": "builder" },
    { "from": "builder", "to": "overview" },
    { "from": "builder", "to": "demo" },
    { "from": "builder", "to": "docs" },
    { "from": "builder", "to": "social" }
  ]
}
```

### Inside `oaw-site.json` (`urn:quiet-ui:schema:v9:project-site`)

Every project site is driven by a validated `oaw-site.json` manifest. The loader (`load_site_config`) checks path confinement—blocking directory escapes outside the config folder—and rejects private IP addresses, internal local-network hostnames, and personal home directory paths before writing HTML:

| Manifest Section | Required / Purpose | Key Fields |
| :--- | :--- | :--- |
| **`$schema`** | Schema identifier | Must equal `"urn:quiet-ui:schema:v9:project-site"`. |
| **`project`** | Identity and links | `slug`, `title`, `version`, `tagline`, `repo_url`, `site_url`, `license_summary`. |
| **`hub`** | Sibling project switcher | `label`, `hub_url`, and `projects[]` (`slug`, `title`, `tagline`, `url`, `badge`, `current`). |
| **`routes`** | Top navigation tabs | `overview`, `demo` (`enabled`, `legacy_query_keys`), and `docs` (`href`, `label`). |
| **`overview`** | Root landing content | `kicker`, `headline`, `summary`, CTAs, `install_commands`, `plain_language_blocks`, `domain_previews`, `architecture_diagrams`. |
| **`docs_reader`** | Docs compiler inputs | `title`, `subtitle`, `sources[]` (`id`, `path`, `title`, `category`), and `quick_jumps[]`. |
| **`demo_wrapper`** | Optional demo shell | `enabled`, `entry_path`, `docs_base`, `default_studio_view`, `topbar_links[]`. |
| **`social_preview`** | Open Graph card metadata | `image_path`, `width` (`1280`), `height` (`640`), `eyebrow`, `title`, `subtitle`, `pills[]`, `accent_hex`. |

### Markdown Diagram Fences, Search Recovery & Social Previews

- **Inline `quiet-evidence` diagram fences**: Wrap any `urn:quiet-ui:schema:v9:*` JSON spec inside a ```` ```quiet-evidence ```` (or ```` ```json-diagram ````) fenced block in your Markdown guide. The compiler turns it into a crisp, theme-safe inline `<svg>` diagram at build time with zero client-side JavaScript.
- **Client-side search with zero-results recovery**: The docs compiler embeds an inline `#oaw-docs-search-index` payload covering titles, categories, headings, and body text. Pressing `/` focuses the search box; if a filter matches zero guides, the empty state displays a recovery button (`#oaw-empty-clear-btn`) to clear the query or jump straight to a recommended guide.
- **`1280x640` SVG & PNG social previews**: Every build writes a crisp `1280x640` SVG preview card beside `social_preview.image_path` by default (`--no-social-svg` to skip), and passing `--social-png` renders the matching PNG card using Pillow only when requested.

```bash
# Copy the MIT starter kit and customize oaw-site.json + docs/*.md
cp -r customizations/project-site-starter my-project-site

# Build Overview, Docs, optional Demo, and 1280x640 SVG + PNG social previews
python3 -B customizations/scripts/build_project_site.py \
  --config my-project-site/oaw-site.json --out dist/ --social-png
```

Add `--bundle` to inline `quiet-ui-tokens.css` and optional `styles/overrides.css` directly into the generated HTML pages for single-file portability.
