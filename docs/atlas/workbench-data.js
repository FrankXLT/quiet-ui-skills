/* SPDX-License-Identifier: MIT */
/* Quiet UI Diagrams Atlas — DSL Import Before-and-After Workbench Data */

window.ATLAS_WORKBENCH_DATA = {
  mermaid: {
    id: "mermaid",
    name: "1. Mermaid (.mmd)",
    typeSlug: "architecture-delta",
    cli: "python3 skills/quiet-ui-diagrams/scripts/mermaid_extract.py wr_phase_array.mmd",
    source: `graph LR
  GM[DWDM Grandmaster] -->|10 MHz Ref| PLL[DDMTD Helper PLL]
  PLL -->|Optical Phase Lock| WR1[WR-NODE-01]
  WR1 -.->|Phase Drift Jitter| WR2[WR-NODE-02]
  WR1 -->|Picosecond Telemetry| DB[(TimescaleDB Hypertable)]
  classDef proposed stroke:#2563EB,stroke-width:2px;
  class PLL proposed;`,
    ast: `# Mermaid IR — wr_phase_array.mmd
- Grammar: flowchart (LR) | Direction: LR
- Nodes: 5 total / 5 drawable / 0 containers
- Edges: 4 (4 labeled, 1 dashed delta)
- Type Candidate: architecture-delta
- Focal Hubs: DDMTD Helper PLL (2), WR-NODE-01 (3)
- Terminals: TimescaleDB Hypertable

| id  | label                  | shape    | deg |
|-----|------------------------|----------|-----|
| GM  | DWDM Grandmaster       | rect     | 0/1 |
| PLL | DDMTD Helper PLL       | rect     | 1/1 |
| WR1 | WR-NODE-01             | rect     | 1/2 |
| DB  | TimescaleDB Hypertable | cylinder | 1/0 |`,
    svg: `<svg viewBox="0 0 460 220" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Rebuilt Architecture Delta">
  <rect x="16" y="24" width="120" height="60" rx="6" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="76" y="52" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">DWDM Master</text>
  <text x="76" y="68" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Atomic Cs Ref</text>
  <path d="M 136 54 L 176 54" stroke="var(--border-strong)" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
  <rect x="176" y="24" width="130" height="60" rx="6" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)" stroke-width="2"/>
  <text x="241" y="48" fill="var(--tint-indigo-fg)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">DDMTD Helper PLL</text>
  <text x="241" y="64" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11" font-weight="600" text-anchor="middle">[+ Proposed]</text>
  <path d="M 306 54 L 346 54" stroke="var(--border-strong)" stroke-width="1.5" fill="none"/>
  <rect x="346" y="24" width="98" height="60" rx="6" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="395" y="52" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">WR-NODE-01</text>
  <text x="395" y="68" fill="var(--status-ok)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Locked 0.8ps</text>
  <path d="M 395 84 L 395 120 L 241 120 L 241 146" stroke="var(--border-strong)" stroke-width="1.5" fill="none"/>
  <rect x="166" y="146" width="150" height="54" rx="6" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="241" y="170" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">TimescaleDB</text>
  <text x="241" y="186" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Phase Hypertable</text>
  <defs><marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 1 L 8 5 L 0 9 z" fill="var(--border-strong)"/></marker></defs>
</svg>`
  },
  drawio: {
    id: "drawio",
    name: "2. draw.io (.drawio XML)",
    typeSlug: "deployment",
    cli: "python3 skills/quiet-ui-diagrams/scripts/drawio_extract.py wr_deploy.drawio",
    source: `<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="gm" value="Grandmaster Chassis 1U"
      style="rounded=1;fillColor=#FFFFFF" vertex="1" parent="1">
      <mxGeometry x="40" y="60" width="160" height="80" as="geometry"/>
    </mxCell>
    <mxCell id="pll" value="FPGA Accelerator PCIe"
      style="rounded=1;fillColor=#EEF2FF" vertex="1" parent="1">
      <mxGeometry x="260" y="60" width="160" height="80" as="geometry"/>
    </mxCell>
    <mxCell id="e1" value="DWDM Optical Trunk" edge="1"
      source="gm" target="pll" parent="1"/>
  </root>
</mxGraphModel>`,
    ast: `# draw.io IR — wr_deploy.drawio
- Geometry: unscaled mxGraphModel | Direction: LR
- Nodes: 3 physical chassis / host containers
- Edges: 2 orthogonal optical fiber trunks
- Type Candidate: deployment
- Deployment Tiers: Timing Core, Field Node, Storage

| id  | label                 | tier        |
|-----|-----------------------|-------------|
| gm  | Grandmaster 1U        | Timing Core |
| pll | DDMTD Helper PCIe     | Accelerator |
| db  | TimescaleDB Cluster   | Ingestion   |`,
    svg: `<svg viewBox="0 0 460 220" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Rebuilt Deployment Diagram">
  <rect x="20" y="24" width="124" height="156" rx="8" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="82" y="48" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">Rack 01 · Hub</text>
  <rect x="30" y="62" width="104" height="46" rx="4" fill="var(--bg-surface)" stroke="var(--border-hairline)"/>
  <text x="82" y="84" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Grandmaster 1U</text>
  <text x="82" y="98" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">10 MHz Atomic</text>
  <path d="M 144 85 L 184 85" stroke="var(--accent-primary)" stroke-width="2" fill="none"/>
  <rect x="184" y="24" width="140" height="156" rx="8" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="254" y="48" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">Compute Node WR-01</text>
  <rect x="194" y="62" width="120" height="46" rx="4" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)"/>
  <text x="254" y="84" fill="var(--tint-indigo-fg)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">DDMTD PCIe Card</text>
  <text x="254" y="98" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Virtex UltraScale+</text>
  <rect x="194" y="118" width="120" height="46" rx="4" fill="var(--bg-surface)" stroke="var(--border-hairline)"/>
  <text x="254" y="140" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">WR Core Daemon</text>
  <path d="M 324 85 L 356 85" stroke="var(--border-strong)" stroke-width="1.5" fill="none"/>
  <rect x="356" y="24" width="90" height="156" rx="8" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="401" y="48" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="12" font-weight="600" text-anchor="middle">Storage</text>
  <rect x="364" y="62" width="74" height="46" rx="4" fill="var(--bg-surface)" stroke="var(--border-hairline)"/>
  <text x="401" y="84" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Timescale</text>
  <text x="401" y="98" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Cluster</text>
</svg>`
  },
  excalidraw: {
    id: "excalidraw",
    name: "3. Excalidraw (.excalidraw)",
    typeSlug: "medallion",
    cli: "python3 skills/quiet-ui-diagrams/scripts/excalidraw_extract.py wr_pipeline.excalidraw",
    source: `{
  "type": "excalidraw",
  "version": 2,
  "elements": [
    {"type": "rectangle", "id": "raw", "text": "Bronze: UDP Phase Packets"},
    {"type": "arrow", "start": "raw", "end": "silver"},
    {"type": "rectangle", "id": "silver", "text": "Silver: Calibrated Offset"},
    {"type": "arrow", "start": "silver", "end": "gold"},
    {"type": "rectangle", "id": "gold", "text": "Gold: Allan Variance"}
  ]
}`,
    ast: `# Excalidraw IR — wr_pipeline.excalidraw
- Raw Elements: 5 (3 shapes, 2 directional links)
- Layout: 3 linear pipeline stages (Bronze -> Silver -> Gold)
- Type Candidate: medallion
- Data Quality: Raw Telemetry -> Filtered Phase -> Analytical Allan Dev

| stage  | table / entity          | quality gate       |
|--------|-------------------------|--------------------|
| Bronze | wr_raw_phase_udp        | Raw packet ingest  |
| Silver | wr_calibrated_sync      | Outlier rejection  |
| Gold   | wr_allan_dev_hypertable | 100ms aggregation  |`,
    svg: `<svg viewBox="0 0 460 220" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Rebuilt Medallion Pipeline">
  <rect x="18" y="36" width="124" height="140" rx="8" fill="var(--tint-amber-bg)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="80" y="66" fill="var(--tint-amber-fg)" font-family="var(--font-sans)" font-size="13" font-weight="700" text-anchor="middle">BRONZE</text>
  <text x="80" y="86" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Raw UDP Frames</text>
  <text x="80" y="104" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">100k samples/s</text>
  <text x="80" y="150" fill="var(--status-warn)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Unfiltered</text>
  <path d="M 142 106 L 168 106" stroke="var(--border-strong)" stroke-width="1.5" fill="none"/>
  <rect x="168" y="36" width="124" height="140" rx="8" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="230" y="66" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="13" font-weight="700" text-anchor="middle">SILVER</text>
  <text x="230" y="86" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">DDMTD Filtered</text>
  <text x="230" y="104" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Phase Calibrated</text>
  <text x="230" y="150" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">0.1ps Residual</text>
  <path d="M 292 106 L 318 106" stroke="var(--border-strong)" stroke-width="1.5" fill="none"/>
  <rect x="318" y="36" width="124" height="140" rx="8" fill="var(--tint-emerald-bg)" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="380" y="66" fill="var(--tint-emerald-fg)" font-family="var(--font-sans)" font-size="13" font-weight="700" text-anchor="middle">GOLD</text>
  <text x="380" y="86" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">TimescaleDB</text>
  <text x="380" y="104" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Allan Deviation</text>
  <text x="380" y="150" fill="var(--status-ok)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">100ms Rollups</text>
</svg>`
  },
  plantuml: {
    id: "plantuml",
    name: "4. PlantUML (.puml)",
    typeSlug: "sequence",
    cli: "python3 skills/quiet-ui-diagrams/scripts/plantuml_extract.py wr_sync.puml",
    source: `@startuml
participant "DWDM Grandmaster" as GM
participant "DDMTD Helper PLL" as PLL
participant "WR-NODE-01" as WR
participant "TimescaleDB" as DB

GM -> PLL: Sync Beacon (10 MHz PPS)
PLL -> WR: Phase Offset (<1.2ps)
WR -> PLL: Feedback Adjustment
WR -> DB: Append Telemetry Record
@enduml`,
    ast: `# PlantUML IR — wr_sync.puml
- Grammar: sequenceDiagram (4 lifelines)
- Lifelines: GM, PLL, WR, DB
- Messages: 4 sync/telemetry transactions
- Type Candidate: sequence
- Protocol: White Rabbit Low-Jitter Phase Tracking

| step | source | target | payload / message       |
|------|--------|--------|-------------------------|
| 1    | GM     | PLL    | Sync Beacon (10MHz PPS) |
| 2    | PLL    | WR     | Phase Offset (<1.2ps)   |
| 3    | WR     | PLL    | Feedback Adjustment     |
| 4    | WR     | DB     | Append Telemetry Record |`,
    svg: `<svg viewBox="0 0 460 220" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Rebuilt Sequence Diagram">
  <rect x="20" y="16" width="80" height="30" rx="4" fill="var(--bg-surface)" stroke="var(--border-strong)"/>
  <text x="60" y="36" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Grandmaster</text>
  <line x1="60" y1="46" x2="60" y2="200" stroke="var(--border-strong)" stroke-dasharray="3 3"/>
  <rect x="130" y="16" width="90" height="30" rx="4" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)"/>
  <text x="175" y="36" fill="var(--tint-indigo-fg)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">DDMTD PLL</text>
  <line x1="175" y1="46" x2="175" y2="200" stroke="var(--border-strong)" stroke-dasharray="3 3"/>
  <rect x="250" y="16" width="80" height="30" rx="4" fill="var(--bg-surface)" stroke="var(--border-strong)"/>
  <text x="290" y="36" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">WR-NODE-01</text>
  <line x1="290" y1="46" x2="290" y2="200" stroke="var(--border-strong)" stroke-dasharray="3 3"/>
  <rect x="360" y="16" width="80" height="30" rx="4" fill="var(--bg-surface)" stroke="var(--border-strong)"/>
  <text x="400" y="36" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">TimescaleDB</text>
  <line x1="400" y1="46" x2="400" y2="200" stroke="var(--border-strong)" stroke-dasharray="3 3"/>
  <line x1="60" y1="75" x2="175" y2="75" stroke="var(--border-strong)" stroke-width="1.5"/>
  <text x="117" y="70" fill="var(--text-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">1. Sync 10MHz</text>
  <line x1="175" y1="105" x2="290" y2="105" stroke="var(--accent-primary)" stroke-width="1.5"/>
  <text x="232" y="100" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">2. Phase Offset &lt;1.2ps</text>
  <line x1="290" y1="135" x2="175" y2="135" stroke="var(--border-strong)" stroke-width="1.5" stroke-dasharray="4 2"/>
  <text x="232" y="130" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">3. Tune VCXO</text>
  <line x1="290" y1="165" x2="400" y2="165" stroke="var(--status-ok)" stroke-width="1.5"/>
  <text x="345" y="160" fill="var(--status-ok)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">4. Log Hypertable</text>
</svg>`
  }
};
