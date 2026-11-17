---
name: quiet-ui-diagrams
description: Forward-compatible adapter for editorial diagrams and AST importers, routing topologies and quantitative plots directly into Quiet UI v9.0 quiet-evidence modalities.
---

# Quiet UI Diagrams (`quiet-ui-diagrams`) — Forward-Compatible Adapter

This skill serves as the forward-compatible AST ingestion and diagram export adapter for Quiet UI v9.0. It ingests legacy diagram ASTs, enforces orthogonal connector geometry, and routes visualization requests into the **Quiet UI v9.0 3-Pillar Continuum**.

---

## 1. Quiet UI v9.0 3-Pillar Forward Routing

All diagram and chart requests are routed into Pillar 2 ([quiet-evidence](../quiet-evidence/SKILL.md)) and Pillar 1 ([quiet-ui](../quiet-ui/SKILL.md)):

| Incoming Diagram Category | Legacy Target | v9.0 Canonical Routing Target |
| :--- | :--- | :--- |
| **System & Software Architecture** | `type-architecture.md` | [schematics-and-topologies.md](../quiet-evidence/modalities/schematics-and-topologies.md) (`L1/L2`) |
| **Architecture Delta & Migrations** | `type-architecture-delta.md` | [schematics-and-topologies.md](../quiet-evidence/modalities/schematics-and-topologies.md) (`L2`) |
| **Data Pipelines & Storage** | `type-data-flow.md`, `type-er.md` | [schematics-and-topologies.md](../quiet-evidence/modalities/schematics-and-topologies.md) (`L2/L3`) |
| **Sequence & State Machines** | `type-sequence.md`, `type-state.md` | [schematics-and-topologies.md](../quiet-evidence/modalities/schematics-and-topologies.md) (`L2/L3`) |
| **Quantitative & Statistical Charts**| `type-line.md`, `type-bar.md` | [analytical-and-spectral-plots.md](../quiet-evidence/modalities/analytical-and-spectral-plots.md) (`L2/L3`) |
| **Timing & Waveforms** | `type-waterfall.md`, `timeline.md` | [waveforms-and-timing.md](../quiet-evidence/modalities/waveforms-and-timing.md) (`L3`) |
| **Delivery Medium Wrapping** | Raw SVG Embedding | [quiet-ui Foundation](../quiet-ui/SKILL.md) (`M1–M7` Medium Shells) |

---

## 2. AST Extraction Pipeline

When incoming source code or documents contain Mermaid, PlantUML, Draw.io, or Excalidraw, use the standalone extraction scripts:

1. **Mermaid AST Extraction**:
   `python3 scripts/mermaid_extract.py <input.mmd>` &rarr; extracts flowcharts, sequence diagrams, and state machines.
2. **PlantUML AST Extraction**:
   `python3 scripts/plantuml_extract.py <input.puml>` &rarr; extracts class, component, and sequence structures.
3. **Draw.io AST Extraction**:
   `python3 scripts/drawio_extract.py <input.drawio>` &rarr; parses uncompressed XML shape hierarchies.
4. **Excalidraw AST Extraction**:
   `python3 scripts/excalidraw_extract.py <input.excalidraw>` &rarr; extracts canvas elements and connectors.

---

## 3. Mandatory Orthogonal Connector Invariants

When rendering structural diagrams and topologies, maintain the 6 non-negotiable geometry rules:
1. **Orthogonal right-angle elbows only** (`r=8px` arc). Never draw diagonal connector lines.
2. **6–10px visible gap** between label mask rect and connector stroke.
3. **No overlapping or co-linear connectors**: Offset parallel routes by $\ge 12\,\text{px}$; use bridge arcs for crossings.
4. **Distinct fan-out attachment points**: Multiple edges attaching to a single side must be separated by $\ge 12\,\text{px}$.
5. **Clear transit paths**: Connectors must never transit behind non-endpoint boxes.
6. **Z-order mask discipline**: Label masks must be emitted before subsequent node rects or ordered explicitly in defs.

---

## 4. Standalone Export Pipeline

- **Standalone SVG Export**:
  `python3 scripts/export_svg.py <src.html> [<out.svg>] --theme white|paper|dark-paper|dark`
- **Standalone PNG Export**:
  `python3 scripts/export_png.py <src.html> [<out.png>] [scale]` (using headless Chrome with zero-PII metadata).
- **Geometry Verification Gate**:
  `python3 scripts/verify_geometry.py <file>` (checks connector orthogonality, label margins, and non-overlap).
