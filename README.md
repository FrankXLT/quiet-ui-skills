# Quiet UI Skills (`v7.0`)

[![License: Apache 2.0](https://img.shields.io/badge/Plugin%20%26%20UI%20Engine-Apache%202.0-blue.svg)](LICENSE)
[![Customizations, Tokens & Diagrams: MIT](https://img.shields.io/badge/Customizations%2C%20Tokens%20%26%20Diagrams-MIT-0F766E.svg)](customizations/LICENSE)
[![Suite: 17 UI Tiers + 45 Diagram Types](https://img.shields.io/badge/Suite-17%20UI%20Tiers%20%2B%2045%20Diagram%20Types-2563EB.svg)](https://FrankXLT.github.io/quiet-ui-skills/)

**Quiet UI Skills** is a unified open-source design plugin and CSS token suite for AI coding agents (Google Antigravity, Claude Code, Cursor, Codex, and Windsurf). It pairs **macro responsive page architecture** with **micro editorial SVG schematics and quantitative charts** under one 4-theme design token contract, one offline 3-role typographic scale (`11px` hard floor), and one 60-second brand customization workflow:

1. **`quiet-ui` (17-Tier UI & Document System):** Turns raw prose, RFCs, SQL schemas, fleet tables, schedules, and smart-home entities into cohesive HTML interfaces across **17 graduated structural archetypes** (`0%` unboxed monograph prose up to `100%` `1px` hairline telemetry grids and optical-glass wall panels).
2. **`quiet-ui-diagrams` (45-Type SVG Schematic & Chart Engine):** Produces bespoke inline SVG architecture diagrams, medallion pipelines, sequence flows, axonometric stacks, Wardley maps, and quantitative charts—with zero-dependency AST/XML importers for **Mermaid, draw.io, Excalidraw, and PlantUML**, geometric collision checks, and standalone SVG/PNG export.

![Quiet UI 17-Tier Overview](docs/assets/hero_4family_overview.png)

---

## Quick Start & Installation

- **Interactive 17-Tier Showcase:** [**https://FrankXLT.github.io/quiet-ui-skills/**](https://FrankXLT.github.io/quiet-ui-skills/) (or open [`quiet-ui-showcase.html`](quiet-ui-showcase.html) locally — zero build step required).
- **Deep-Link Any State:** Append `?tier=app-3&nav=n2&theme=white&density=d2&corners=rounded` to share an exact archetype, navigation shell, surface theme, and corner geometry.

```bash
# Install native Antigravity Plugin (~/.gemini/config/plugins/quiet-ui-skills)
# plus cross-agent skills (~/.agents/skills/{quiet-ui,quiet-ui-diagrams})
git clone https://github.com/FrankXLT/quiet-ui-skills.git
cd quiet-ui-skills
./install.sh

# Or install individual skills via the Skills CLI
npx skills add https://github.com/FrankXLT/quiet-ui-skills --skill quiet-ui
npx skills add https://github.com/FrankXLT/quiet-ui-skills --skill quiet-ui-diagrams
```

---

## Customize in 60 Seconds (`customizations/`)

One manifest (`customizations/<name>/customization.json`) skins **both** your 17-tier UI shells and your 45-type SVG diagrams simultaneously:

| Starter Blueprint | Scope | Enabled Tiers | Artwork | Target Use Cases |
| :--- | :---: | :---: | :---: | :--- |
| **`personal-starter`** | Personal & Spatial | All 17 Tiers | Monet Canvas | Personal workspaces, circadian pacing, Home Assistant wall kiosks, mobile companions. |
| **`brand-starter`** | Team & Product | 13 Tiers | Omitted | Enterprise software products, SaaS dashboards, engineering docs & architecture diagrams. |

```text
I want to customize Quiet UI for [personal / brand] use in customizations/<my-name>/.
Here are 1–3 inspirational design references:
- Reference 1: [URL, screenshot, or design link]
Brand Hexes / Fonts:
- Primary Accent: #... | Surface / Canvas: #FFFFFF / #F8FAFC
- Typography: [Sans font] / [Serif font] / [Mono font]

Please clone the starter, extract design tokens into customization.json, update intent/ blueprints and styles/overrides.css, and compile/verify the showcase.
```

---

## Macro + Micro Routing: How the Two Skills Work Together

| What You Hand the Agent | Activated Skill | What It Builds Automatically |
| :--- | :---: | :--- |
| **Long-form essays, derivations, ADRs, RFCs, CLI/SDK docs, or runbooks** | `quiet-ui` | Unboxed `68ch` Monograph (`01. Doc-1`), `BLUF` Memo (`02. Doc-2`), RFC (`03. Doc-3`), SDK Flow Spine (`04. Doc-4B`), or Split Runbook (`05. Doc-4A`) |
| **Node fleets, time-series metrics, issue queues, schedules, or SQL schemas** | `quiet-ui` | `1px` Fleet Grid (`08. Bridge-2`), Strip Console (`09. App-2`), Planner (`11. App-4`), Bento KPI (`12. App-3`), or 3-Pane Tree Explorer (`14. App-Tree`) |
| **Smart-home wall tablets, room dimmers, or foldable phone controllers** | `quiet-ui` | Monet + Optical Glass HUD (`15. HA-1`), Room Matrix (`16. HA-2`), or Crease-Aware Foldable Companion (`17. HA-3`) |
| **System architecture, C4/delta diffs, cloud deployment, or data pipelines** | `quiet-ui-diagrams` | Editorial inline SVG schematics (`architecture`, `architecture-delta`, `high-level`, `medallion`, `data-flow`, `deployment`, `exploded`, `axonometric-plan`) |
| ** Quantitative series, distributions, hierarchies, or strategic maps** | `quiet-ui-diagrams` | Precision SVG charts (`line`/slope/ridgeline/streamgraph, `bar`/dumbbell, `scatter`/beeswarm/box, `waterfall`, `sankey`, `treemap`, `heatmap`, `wardley`) |
| **Existing `.drawio`, `.excalidraw`, Mermaid (`.mmd`), or PlantUML (`.puml`) files** | `quiet-ui-diagrams` | Deterministic AST/XML extraction (`*_extract.py --json`) rebuilt into publication-grade Quiet UI HTML/SVG/PNG figures |

---

## 1. `quiet-ui`: The 17-Tier UI Continuum

All 17 tiers default to **Pure White (`data-theme="white"`)** and switch live across **Warm Paper (`paper`)**, **Warm Sepia Dark (`dark-paper`)**, and **Carbon Dark (`dark`)**:

| # | Tier ID | Structural Archetype | Box Weight | Default Nav | Primary Use Cases |
| :-: | :--- | :--- | :---: | :---: | :--- |
| `01` | **`Doc-1`** | Academic & Scientific Monograph | `0%` | `N1` Left Spine | Whitepapers, mathematical derivations, research monographs |
| `02` | **`Doc-2`** | Executive Decision Memo (`BLUF` + Diagram) | `15%` | `N0` Kiosk | Architecture decision records, board memos, post-mortems |
| `03` | **`Doc-3`** | Normative RFC Specification | `25%` | `N0` Kiosk | Protocol specs, `MUST`/`SHALL` compliance matrices, state machines |
| `04` | **`Doc-4B`** | Encyclopedic SDK & API Reference | `25%` | `N3` Top + Left | Library SDK references, CLI/skill docs, decision router tables |
| `05` | **`Doc-4A`** | Split-Pane Operational Runbook | `45%` | `N1` Left Spine | Deployment playbooks, incident response SOPs, interactive tutorials |
| `06` | **`Bridge-1`** | Parametric Engineering Worksheet | `50%` | `N0` Kiosk | Interactive trade studies, link-budget calculators, solver sheets |
| `07` | **`Deck-1`** | Viewport-Locked Briefing Stage | `60%` | `N1` Left Spine | `100dvh` assertion-evidence briefings with zero vertical scroll |
| `08` | **`Bridge-2`** | High-Density Data Table & Fleet Grid | `100% 1px Grid` | `N2` Top Bar | Container fleet inventories, node ledgers, benchmark matrices |
| `09` | **`App-2`** | Live Metrics & Time-Series Console | `100% 1px Grid` | `N1` Left Spine | Synchronized strip charts, subsystem rankings, threshold gauges |
| `10` | **`App-1`** | Compact Issue & Ticket Tracker | `0% Cards` | `N1` Left Spine | `36px` single-line triage queues with docked right inspector |
| `11` | **`App-4`** | Task & Calendar Planner | `80%` | `N1` Left Spine | Daily status briefing, focus timer hero, backlog staging, time grid |
| `12` | **`App-3`** | KPI & Analytics Dashboard (Bento Grid) | `100% Cards` | `N2` Top Bar | 12-column executive KPI grid and balanced 2×2 `.va-bento-2col` |
| `13` | **`App-5`** | Daily Pacing & Wellness Planner | `75%` | `N1` Left Spine | Readiness ring, self-filling progress capsules, corridor sparklines |
| `14` | **`App-Tree`** | Hierarchical Tree, Schema & File Explorer | `90% 3-Pane` | `N1` Left Spine | Coupled object tree, 3-tab table/DDL/AST stage, and FK inspector |
| `15` | **`HA-1`** | Ambient Wall Kiosk (Monet + Deep-Crystal Glass) | `20% HUD` | `N0` Kiosk | `65%` open Monet canvas + 3 floating `.va-glass-panel` HUD cards |
| `16` | **`HA-2`** | Room-First Wall Control Panel | `85%` | `N1` Zone Rail | Walk-up room cards, fixture dimmer dock, circuit load breakdown |
| `17` | **`HA-3`** | Crease-Aware Foldable & Phone Controller | `85%` | `N4` Thumb Dock | `56px` touch slider tiles, `820px` 50/50 fold split, `390px` thumb bar |

---

## 2. `quiet-ui-diagrams`: 45 Diagram & Chart Types + 4 DSL Importers

| Domain Family | Supported Visual Types (`skills/quiet-ui-diagrams/references/`) |
| :--- | :--- |
| **Systems & Cloud Architecture (11)** | `architecture`, `architecture-delta`, `high-level`, `it-state`, `deployment`, `dependency` (arc), `layers`, `nested`, `exploded` (axonometric), `axonometric-plan`, `dp-security-matrix` |
| **Data, Schema & Pipelines (6)** | `data-flow`, `medallion` (Bronze/Silver/Gold), `dp-integration`, `er` (entity-relationship), `db-schema`, `uml-class` |
| **Flows, State & Operations (9)** | `flowchart`, `process`, `sequence`, `state` (FSM), `swimlane`, `loop` (flywheel), `fishbone` (Ishikawa), `timeline`, `gantt` |
| **Product, Strategy & Org (8)** | `wardley`, `service-blueprint`, `journey`, `story-map`, `kanban`, `org-chart`, `tree`, `quadrant` |
| **Quantitative Charts (11)** | `line` (slopegraph, ridgeline, streamgraph, bump), `bar` (column, dumbbell), `scatter` (bubble, beeswarm, box plot), `waterfall`, `sankey`, `treemap` (marimekko), `heatmap`, `radar`, `polar`, `pyramid`, `venn` |

---

## Verification Toolchain & Repository Layout

```bash
# 1. Verify 17-tier UI showcase + markdown CSS token & reference integrity
python3 skills/quiet-ui/scripts/verify_visual_contract.py quiet-ui-showcase.html --check-docs

# 2. Verify starter customizations & self-immutability lock
python3 customizations/scripts/verify_customization.py customizations/personal-starter
python3 customizations/scripts/verify_customization.py customizations/brand-starter

# 3. Verify diagram geometry, offline self-check, and standalone SVG/PNG export
python3 skills/quiet-ui-diagrams/scripts/verify_geometry.py <diagram.html>
python3 skills/quiet-ui-diagrams/scripts/self_check.py <diagram.html> --offline
python3 skills/quiet-ui-diagrams/scripts/export_svg.py <diagram.html> --theme white -o <diagram.svg>
```

```text
quiet-ui-skills/
├── plugin.json                                      # Native Antigravity plugin manifest (v7.0.0)
├── assets/logo.svg                                  # High-contrast square plugin icon
├── LICENSE / NOTICE / TRADEMARKS.md                 # Apache 2.0 Core + MIT Customizations & Output
├── THIRD_PARTY_LICENSES.md                          # Upstream MIT attributions (Cathryn Lavery & icons)
├── install.sh                                       # 1-command plugin & cross-agent skill installer
├── quiet-ui-showcase.html                           # Self-contained 17-tier interactive showcase
├── tokens/quiet-ui-tokens.css                       # Standalone 4-theme CSS design tokens (MIT)
├── customizations/                                  # Personal (17-tier) & Brand (13-tier) starters (MIT)
└── skills/
    ├── quiet-ui/                                    # Macro 17-tier HTML UI & document skill
    └── quiet-ui-diagrams/                           # Micro 45-type SVG diagram, chart & DSL import skill
```

---

## Licensing & Acknowledgements

- **Core Plugin & UI Engine (`Apache-2.0`):** Covers `plugin.json`, `skills/quiet-ui/`, root verifiers, and `quiet-ui-showcase.html` (`LICENSE`, `NOTICE`, `TRADEMARKS.md`).
- **Diagram Engine & Upstream Credit (`MIT`):** `skills/quiet-ui-diagrams/` incorporates refactored specifications, DSL extractors, and SVG geometry tools adapted from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) (`Copyright (c) 2025 Cathryn Lavery`, MIT License — see [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)).
- **Customizations, Tokens & 100% Commercial Output Exemption (`MIT`):** All files in `customizations/`, `tokens/quiet-ui-tokens.css`, and 100% of HTML, CSS, JS, SVG, and PNG deliverables generated with Quiet UI Skills belong to you under pure MIT with **zero `NOTICE` or attribution obligations** on shipped websites, apps, or decks.
