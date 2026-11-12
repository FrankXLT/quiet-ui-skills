---
name: quiet-ui-diagrams
description: Editorial SVG diagram and quantitative chart engine covering 45 diagram types, 9 semantic patterns, Mermaid/draw.io/Excalidraw/PlantUML AST import, multi-theme Quiet UI CSS token binding, geometry verification, and standalone SVG/PNG export.
---

# Quiet UI Diagrams (`quiet-ui-diagrams`)

Editorial SVG diagram and quantitative chart engine designed for technical documentation, RFCs, architecture blueprints, and analytical dashboards. Built on a 4-theme token architecture (`white`, `paper`, `dark-paper`, `dark`) with strict orthogonal connector geometry, 4px layout grid, offline system typography, and zero-PII compliance.

---

## 0. Self-Immutability Lock & Unified Customization Gate

1. **Self-Immutability Lock (Core & Starters are Strictly Read-Only):**
   Automated tools and AI agents are strictly forbidden from modifying or writing to `skills/quiet-ui/`, `skills/quiet-ui-diagrams/`, `customizations/personal-starter/`, or `customizations/brand-starter/` during user workflows.
2. **Unified Customization Gate:**
   Before generating or styling diagrams, resolve styling from the workspace:
   - **Step 1:** Check for `customizations/<name>/customization.json` or `.visual-lock.json` in the active workspace. When present, inherit Quiet UI's 4-theme tokens:
     - Backgrounds: `var(--bg-canvas)`, `var(--bg-surface)`, `var(--bg-elevated)`
     - Typography: `var(--text-primary)`, `var(--text-secondary)`, `var(--text-muted)`
     - Hairlines: `var(--border-hairline)`, `var(--border-strong)`
     - Accents & Tints: `var(--accent-primary)`, `var(--tint-indigo-bg)`, `var(--tint-emerald-bg)`, `var(--tint-amber-bg)`
   - **Step 2:** If no workspace customization exists, check for saved client profiles in `~/.config/quiet-ui/diagram-profiles/<slug>.md` (see [profiles.md](references/profiles.md)).
   - **Step 3:** Fall back to Quiet UI Pure White (`data-theme="white"`) defaults (see [style-guide.md](references/style-guide.md)).
   - For custom brand extraction and token onboarding, follow [onboarding.md](references/onboarding.md) and [onboarding-tokens.md](references/onboarding-tokens.md).

---

## 1. Offline Font Stack & `11px` Typography Floor

1. **Zero External Font Requests:**
   Never link to external font services, remote stylesheets, or CDN domains. All diagrams use Quiet UI's offline font stacks:
   - **Node Titles & UI Chrome:** `var(--font-sans)` (`Inter`, system-ui, -apple-system, sans-serif) at weight 600.
   - **Editorial Titles & Callouts:** `var(--font-serif)` (`Newsreader`, `Georgia`, serif) — 400 upright for page H1s, *italic* for editorial callouts ([primitive-annotation.md](references/primitive-annotation.md)).
   - **Technical Literals & Numerals:** `var(--font-mono)` (`JetBrains Mono`, `ui-monospace`, monospace) strictly for ports, CIDRs, SQL types, CLI flags, JSON keys, and tabular numerals (`tabular-nums`). Never blanket prose.
2. **`11px` Minimum Typography Floor:**
   Every text element in an inline Quiet UI diagram must satisfy `>= 11px` (`var(--ts-xs, 11px)`):
   - Tags, ports, and connector pill labels: `11px` (`var(--ts-xs)`).
   - Technical sublabels & descriptions: `12.5px` (`var(--ts-sm)`).
   - Node titles & headings: `14–15px` (`var(--ts-body)`) in standard `1:1` viewBox.
   Sub-11px labels fail legibility checks across mobile viewports and high-density screens.

---

## 2. 45-Type Visual Router & 9 Semantic Patterns Index

### 2.1 9 Semantic Behavioral Patterns
Choose a behavioral pattern first when flow or lifecycle dictates structure ([semantic-patterns.md](references/semantic-patterns.md)):
- **Fan-in / Queue Bottleneck:** [type-data-flow.md](references/type-data-flow.md) & [type-data-flow-examples.md](references/type-data-flow-examples.md)
- **Stage Framework with Slots:** [type-process.md](references/type-process.md) & [type-process-examples.md](references/type-process-examples.md)
- **Unstructured to Structured Artifact:** [type-data-flow.md](references/type-data-flow.md)
- **Paired Policy Evaluation Traces:** [type-flowchart.md](references/type-flowchart.md)
- **Secure Paved Road:** [type-architecture.md](references/type-architecture.md) & [type-architecture-delta.md](references/type-architecture-delta.md)
- **Governance & Control Catalog:** [type-layers.md](references/type-layers.md)
- **Compensating Security Layers:** [type-layers.md](references/type-layers.md)
- **Traceable Block Decomposition:** [type-tree.md](references/type-tree.md)
- **Lifecycle Phase Map:** [type-state.md](references/type-state.md)

### 2.2 Complete 45 Visual Types Directory
- **System & Software Architecture:** [type-architecture.md](references/type-architecture.md) · [type-architecture-delta.md](references/type-architecture-delta.md) · [type-high-level.md](references/type-high-level.md) ([examples](references/type-high-level-examples.md)) · [type-it-state.md](references/type-it-state.md) ([examples](references/type-it-state-examples.md)) · [type-deployment.md](references/type-deployment.md) · [type-layers.md](references/type-layers.md) · [type-nested.md](references/type-nested.md) · [type-dependency.md](references/type-dependency.md) · [type-uml-class.md](references/type-uml-class.md)
- **Data Pipelines & Storage:** [type-data-flow.md](references/type-data-flow.md) ([examples](references/type-data-flow-examples.md)) · [type-dp-integration.md](references/type-dp-integration.md) ([examples](references/type-dp-integration-examples.md)) · [type-dp-security-matrix.md](references/type-dp-security-matrix.md) ([examples](references/type-dp-security-examples.md)) · [type-medallion.md](references/type-medallion.md) ([examples](references/type-medallion-examples.md)) · [type-db-schema.md](references/type-db-schema.md) · [type-er.md](references/type-er.md)
- **Processes, Logic & Sequences:** [type-flowchart.md](references/type-flowchart.md) · [type-sequence.md](references/type-sequence.md) · [type-state.md](references/type-state.md) · [type-process.md](references/type-process.md) ([examples](references/type-process-examples.md)) · [type-swimlane.md](references/type-swimlane.md) · [type-service-blueprint.md](references/type-service-blueprint.md) · [type-journey.md](references/type-journey.md) · [type-loop.md](references/type-loop.md) · [type-timeline.md](references/type-timeline.md) · [type-gantt.md](references/type-gantt.md) · [type-story-map.md](references/type-story-map.md) · [type-kanban.md](references/type-kanban.md)
- **Hierarchy, Trees & Spatial Plans:** [type-tree.md](references/type-tree.md) · [type-org-chart.md](references/type-org-chart.md) · [type-exploded.md](references/type-exploded.md) · [type-axonometric-plan.md](references/type-axonometric-plan.md) · [type-pyramid.md](references/type-pyramid.md) · [type-venn.md](references/type-venn.md) · [type-wardley.md](references/type-wardley.md) · [type-fishbone.md](references/type-fishbone.md)
- **Quantitative & Statistical Charts:** [type-bar.md](references/type-bar.md) · [type-line.md](references/type-line.md) ([variants: slopegraph, ridgeline, streamgraph, bump](references/type-line-variants.md)) · [type-scatter.md](references/type-scatter.md) · [type-heatmap.md](references/type-heatmap.md) · [type-treemap.md](references/type-treemap.md) · [type-sankey.md](references/type-sankey.md) · [type-radar.md](references/type-radar.md) · [type-polar.md](references/type-polar.md) · [type-quadrant.md](references/type-quadrant.md) · [type-waterfall.md](references/type-waterfall.md)
- **Primitives & Extensions:** [primitives-core.md](references/primitives-core.md) · [primitive-annotation.md](references/primitive-annotation.md) · [primitive-icons.md](references/primitive-icons.md) ([tech](references/icons-tech.md), [cloud](references/icons-cloud.md), [general](references/icons-general.md)) · [primitive-sketchy.md](references/primitive-sketchy.md) · [primitive-terminal.md](references/primitive-terminal.md) · [animation.md](references/animation.md) · [layout-budget.md](references/layout-budget.md) · [output-spec.md](references/output-spec.md) · [doctor.md](references/doctor.md)

---

## 3. Import, Verification & Export Pipeline

1. **AST Extraction (Never Render Directly):**
   - Mermaid: `python3 scripts/mermaid_extract.py <input>` ([import-mermaid.md](references/import-mermaid.md))
   - Draw.io: `python3 scripts/drawio_extract.py <input>` ([import-drawio.md](references/import-drawio.md))
   - Excalidraw: `python3 scripts/excalidraw_extract.py <input>` ([import-excalidraw.md](references/import-excalidraw.md))
   - PlantUML: `python3 scripts/plantuml_extract.py <input>` ([import-plantuml.md](references/import-plantuml.md))
2. **Deterministic Verification Gate:**
   - Geometry Invariants: `python3 scripts/verify_geometry.py <file>` (checks 6 connector rules, label margins, non-overlap).
   - Document Integrity: `python3 scripts/self_check.py <file>` (checks accessible `<title>`/`<desc>`, viewBox clipping, offline fonts).
3. **Export Pipeline (Diagram-Only SVG & PNG):**
   - Standalone SVG: `python3 scripts/export_svg.py <src.html> [<out.svg>] --theme white|paper|dark-paper|dark` ([export.md](references/export.md) & [export-registry.md](references/export-registry.md)).
   - Standalone PNG: `python3 scripts/export_png.py <src.html> [<out.png>] [scale]` using Selenium + headless Chrome (`--headless=new`) with transparent background ([export-png.md](references/export-png.md)). Strictly zero Selenium headless Chrome.

---

## 4. Complexity Budget & Mandatory Connector Rules

- **Complexity Ceiling:** Max 9 nodes, max 12 connectors, max 2 accent elements per diagram ([layout-budget.md](references/layout-budget.md)).
- **6 Non-Negotiable Connector Rules:**
  1. Orthogonal right-angle elbows only (`r=8` arc). Never diagonal lines.
  2. 6–10px visible gap between label mask rect and connector stroke.
  3. No overlapping or co-linear connectors (offset parallel routes ≥ 12px; bridge crossings).
  4. Distinct fan-out attachment points per edge (≥ 12px apart).
  5. Never transit behind non-endpoint boxes.
  6. Label masks must be emitted before subsequent node rects (or drawn in proper z-order).
