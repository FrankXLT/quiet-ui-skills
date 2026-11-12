/* SPDX-License-Identifier: MIT */
/* Quiet UI Diagrams Atlas — Systems & Cloud (11) and Data & Schema (6) Catalog */

(function() {
  const b = (x, y, w, h, t, s, f) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="${f||'var(--bg-surface)'}" stroke="var(--border-strong)" stroke-width="1.2"/><text x="${x+w/2}" y="${y+h/2-(s?4:0)}" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">${t}</text>${s?`<text x="${x+w/2}" y="${y+h/2+12}" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">${s}</text>`:''}`;
  const wSvg = (inner, desc) => `<svg viewBox="0 0 320 176" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${desc}">${inner}</svg>`;

  const items = [
    {
      id: "architecture", title: "Architecture", family: "systems", familyName: "Systems & Cloud", pattern: "Secure Paved Road",
      desc: "Component topology of White Rabbit optical array connecting Grandmaster, DDMTD PLL, and node array.",
      prompt: "Create a Quiet UI architecture diagram for WR-NODE-01..08 optical phase-lock array with grandmaster and DDMTD helper PLL.",
      doc: "references/type-architecture.md",
      svg: wSvg(`${b(15, 58, 85, 60, "Grandmaster", "DWDM 10MHz")}<path d="M 100 88 L 130 88" stroke="var(--border-strong)" stroke-width="1.5"/>${b(130, 58, 85, 60, "DDMTD PLL", "Helper Loop", "var(--tint-indigo-bg)")}<path d="M 215 88 L 242 88" stroke="var(--border-strong)" stroke-width="1.5"/>${b(242, 58, 68, 60, "WR-NODE", "01..08")}`, "Architecture Topology")
    },
    {
      id: "architecture-delta", title: "Architecture Delta", family: "systems", familyName: "Systems & Cloud", pattern: "Secure Paved Road",
      desc: "Baseline vs proposed layout highlighting addition of DDMTD helper loop and deprecation of legacy coax.",
      prompt: "Generate an architecture-delta diagram showing migration from legacy coaxial distribution to optical phase lock.",
      doc: "references/type-architecture-delta.md",
      svg: wSvg(`${b(15, 25, 98, 50, "Grandmaster", "Atomic Clock")}${b(15, 100, 98, 50, "Legacy Coax", "[- Retiring]", "var(--tint-rose-bg)")}<path d="M 113 50 L 155 50" stroke="var(--accent-primary)" stroke-width="1.5"/>${b(155, 25, 150, 50, "DDMTD Phase Lock", "[+ Proposed]", "var(--tint-indigo-bg)")}<path d="M 113 125 L 200 125" stroke="var(--status-danger)" stroke-width="1.5" stroke-dasharray="4 2"/>`, "Architecture Delta")
    },
    {
      id: "high-level", title: "High-Level Overview", family: "systems", familyName: "Systems & Cloud", pattern: "Stage Framework",
      desc: "Three-tier macro system overview: Optical Reference, Distribution Network, and Endpoints.",
      prompt: "Draw a high-level 3-tier system overview for White Rabbit optical phase-lock distribution.",
      doc: "references/type-high-level.md",
      svg: wSvg(`${b(15, 20, 290, 36, "Tier 1: Atomic Reference (DWDM Grandmaster)", "")}<path d="M 160 56 L 160 70" stroke="var(--border-strong)" stroke-width="1.5"/>${b(15, 70, 290, 36, "Tier 2: Optical Distribution (DDMTD PLL Switched)", "")}<path d="M 160 106 L 160 120" stroke="var(--border-strong)" stroke-width="1.5"/>${b(15, 120, 290, 36, "Tier 3: Sensor Endpoints (WR-NODE-01..08)", "")}`, "High Level Overview")
    },
    {
      id: "it-state", title: "IT Operational State", family: "systems", familyName: "Systems & Cloud", pattern: "Lifecycle Phase Map",
      desc: "Operational health of distributed nodes: Grandmaster locked, nodes synchronized, calibration active.",
      prompt: "Create an IT state health dashboard map showing locked nodes and active calibration loops.",
      doc: "references/type-it-state.md",
      svg: wSvg(`${b(15, 30, 135, 50, "Grandmaster 01", "Locked 10MHz", "var(--tint-emerald-bg)")}${b(170, 30, 135, 50, "WR-NODE-01", "Phase Jitter 0.8ps", "var(--tint-emerald-bg)")}${b(15, 96, 135, 50, "WR-NODE-02", "Calibrating Loop", "var(--tint-amber-bg)")}${b(170, 96, 135, 50, "Hypertable Ingest", "45k rows/sec", "var(--tint-indigo-bg)")}`, "IT Operational State")
    },
    {
      id: "deployment", title: "Deployment Topology", family: "systems", familyName: "Systems & Cloud", pattern: "Governance & Control",
      desc: "Physical 1U chassis mapping, PCIe accelerator slots, fiber patch panel, and database nodes.",
      prompt: "Diagram the physical hardware deployment topology of WR-01..08 across server racks.",
      doc: "references/type-deployment.md",
      svg: wSvg(`<rect x="15" y="20" width="135" height="136" rx="6" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="82" y="40" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Rack Chassis 1U</text>${b(25, 50, 115, 40, "Grandmaster 1U", "PCIe Slot 0")}${b(25, 100, 115, 44, "DDMTD Carrier", "Virtex FPGA", "var(--tint-indigo-bg)")}<path d="M 150 90 L 175 90" stroke="var(--border-strong)" stroke-width="1.5"/><rect x="175" y="20" width="130" height="136" rx="6" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="240" y="40" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Worker Nodes</text>${b(185, 50, 110, 40, "WR-NODE-01", "PCIe Slot 1")}${b(185, 100, 110, 44, "Timescale Host", "Hypertable DB")}`, "Deployment Topology")
    },
    {
      id: "dependency", title: "Dependency Matrix", family: "systems", familyName: "Systems & Cloud", pattern: "Traceable Block",
      desc: "Inter-component dependency graph connecting master clock, calibration loops, and telemetry sinks.",
      prompt: "Generate a dependency graph showing critical clock and telemetry relationships.",
      doc: "references/type-dependency.md",
      svg: wSvg(`${b(110, 20, 100, 44, "Grandmaster", "Ref Source")}<path d="M 160 64 L 65 105" stroke="var(--accent-primary)" stroke-width="1.5"/><path d="M 160 64 L 255 105" stroke="var(--accent-primary)" stroke-width="1.5"/>${b(15, 105, 100, 48, "DDMTD Loop", "Helper PLL", "var(--tint-indigo-bg)")}${b(205, 105, 100, 48, "TimescaleDB", "Telemetry", "var(--tint-emerald-bg)")}<path d="M 115 129 L 205 129" stroke="var(--border-strong)" stroke-width="1.5" stroke-dasharray="3 3"/>`, "Dependency Map")
    },
    {
      id: "layers", title: "Architectural Layers", family: "systems", familyName: "Systems & Cloud", pattern: "Compensating Security",
      desc: "Stacked horizontal architectural layers from optical physics to analytical telemetry queries.",
      prompt: "Draw a 4-tier layered architecture diagram for the White Rabbit system.",
      doc: "references/type-layers.md",
      svg: wSvg(`${b(15, 16, 290, 32, "Layer 4 · Telemetry & Hypertable Analytics", "", "var(--tint-indigo-bg)")}${b(15, 54, 290, 32, "Layer 3 · Precision Time Protocol Engine", "")}${b(15, 92, 290, 32, "Layer 2 · DDMTD Phase Offset DSP", "")}${b(15, 130, 290, 32, "Layer 1 · DWDM Optical Physical Carrier", "", "var(--tint-emerald-bg)")}`, "Architectural Layers")
    },
    {
      id: "nested", title: "Nested Containers", family: "systems", familyName: "Systems & Cloud", pattern: "Traceable Block",
      desc: "Nested boundary containment: Optical Rack Chassis containing FPGA blade containing DDMTD core.",
      prompt: "Create a nested containment diagram showing chassis and DSP sub-modules.",
      doc: "references/type-nested.md",
      svg: wSvg(`<rect x="15" y="16" width="290" height="144" rx="8" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="30" y="36" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Rack Chassis · WR-RACK-01</text><rect x="30" y="48" width="260" height="96" rx="6" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="45" y="68" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">FPGA Accelerator Blade</text>${b(45, 80, 230, 50, "DDMTD Phase Detector Engine", "Virtex-UP DSP Slice", "var(--tint-indigo-bg)")}`, "Nested Containers")
    },
    {
      id: "exploded", title: "Exploded Hardware Planes", family: "systems", familyName: "Systems & Cloud", pattern: "Traceable Block",
      desc: "Layered isometric perspective of stacked optical transceiver board, FPGA carrier, and power module.",
      prompt: "Render an exploded isometric view of the optical transceiver and FPGA board stack.",
      doc: "references/type-exploded.md",
      svg: wSvg(`<polygon points="36,30 236,16 284,48 84,62" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)" stroke-width="1.2"/><text x="160" y="43" fill="var(--tint-indigo-fg)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Plane 3: Optical Receiver</text><polygon points="36,78 236,64 284,96 84,110" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="160" y="91" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Plane 2: FPGA DDMTD Core</text><polygon points="36,126 236,112 284,144 84,158" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="160" y="139" fill="var(--text-muted)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Plane 1: Power &amp; Clock Base</text>`, "Exploded Hardware")
    },
    {
      id: "axonometric-plan", title: "Axonometric Facility Plan", family: "systems", familyName: "Systems & Cloud", pattern: "Traceable Block",
      desc: "Isometric floorplan layout of the timing laboratory with fiber conduit routes and node racks.",
      prompt: "Generate an axonometric plan of the timing lab racks and optical fiber routing.",
      doc: "references/type-axonometric-plan.md",
      svg: wSvg(`<polygon points="20,80 160,20 300,80 160,140" fill="var(--bg-elevated)" stroke="var(--border-strong)" stroke-width="1.2"/><polygon points="80,70 120,52 140,62 100,80" fill="var(--bg-surface)" stroke="var(--border-strong)"/><text x="110" y="68" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Rack A</text><polygon points="180,70 220,52 240,62 200,80" fill="var(--bg-surface)" stroke="var(--border-strong)"/><text x="210" y="68" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Rack B</text><line x1="110" y1="80" x2="160" y2="105" stroke="var(--accent-primary)" stroke-width="2"/><line x1="210" y1="80" x2="160" y2="105" stroke="var(--accent-primary)" stroke-width="2"/><text x="160" y="125" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Optical Fiber Trunk</text>`, "Axonometric Facility Plan")
    },
    {
      id: "dp-security-matrix", title: "Security Matrix", family: "systems", familyName: "Systems & Cloud", pattern: "Compensating Security",
      desc: "Trust zones matrix: Grandmaster Core (mTLS), Node Ingest (HMAC), and Hypertable Sink (RBAC).",
      prompt: "Create a data protection security matrix for the White Rabbit control and telemetry planes.",
      doc: "references/type-dp-security-matrix.md",
      svg: wSvg(`${b(15, 20, 90, 42, "Grandmaster", "Zone: Vault", "var(--tint-rose-bg)")}${b(115, 20, 90, 42, "Field Nodes", "Zone: Array", "var(--tint-amber-bg)")}${b(215, 20, 90, 42, "Hypertable", "Zone: Storage", "var(--tint-emerald-bg)")}${b(15, 72, 90, 40, "mTLS PKI", "Hardware Root")}${b(115, 72, 90, 40, "HMAC-SHA256", "Frame Auth")}${b(215, 72, 90, 40, "Row-Level RBAC", "TLS Ingest")}${b(15, 120, 290, 36, "Mutual Audit Logging &amp; SIEM Stream", "Zero Trust Compliant", "var(--tint-indigo-bg)")}`, "Security Matrix")
    },
    {
      id: "data-flow", title: "Data Flow Pipeline", family: "data", familyName: "Data & Schema", pattern: "Fan-in / Queue Bottleneck",
      desc: "Queue buffering and phase error transformation flow from FPGA detectors to database ingestion.",
      prompt: "Draw a data-flow diagram showing telemetry ingress, queue buffer, and hypertable batching.",
      doc: "references/type-data-flow.md",
      svg: wSvg(`${b(15, 60, 80, 56, "WR Detector", "100k fps")}<path d="M 95 88 L 120 88" stroke="var(--border-strong)" stroke-width="1.5"/><rect x="120" y="60" width="75" height="56" rx="5" fill="var(--tint-amber-bg)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="157" y="84" fill="var(--tint-amber-fg)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">FIFO Buffer</text><text x="157" y="100" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">512KB Ring</text><path d="M 195 88 L 220 88" stroke="var(--border-strong)" stroke-width="1.5"/>${b(220, 60, 85, 56, "TimescaleDB", "Batch Writer", "var(--tint-emerald-bg)")}`, "Data Flow Pipeline")
    },
    {
      id: "medallion", title: "Medallion Data Architecture", family: "data", familyName: "Data & Schema", pattern: "Unstructured to Structured",
      desc: "Bronze raw frames, Silver calibrated offsets, and Gold Allan deviation hypertable rollups.",
      prompt: "Render a Medallion architecture showing Bronze, Silver, and Gold data transformations.",
      doc: "references/type-medallion.md",
      svg: wSvg(`${b(15, 30, 90, 116, "Bronze", "Raw UDP Packets", "var(--tint-amber-bg)")}<path d="M 105 88 L 115 88" stroke="var(--border-strong)" stroke-width="1.5"/>${b(115, 30, 90, 116, "Silver", "DDMTD Offset", "var(--bg-elevated)")}<path d="M 205 88 L 215 88" stroke="var(--border-strong)" stroke-width="1.5"/>${b(215, 30, 90, 116, "Gold", "Allan Deviation", "var(--tint-emerald-bg)")}`, "Medallion Pipeline")
    },
    {
      id: "dp-integration", title: "Data Pipeline Integration", family: "data", familyName: "Data & Schema", pattern: "Stage Framework",
      desc: "Integration bus connecting streaming telemetry, processing workers, and analytical visualizers.",
      prompt: "Create a data pipeline integration blueprint with Kafka event bus and consumers.",
      doc: "references/type-dp-integration.md",
      svg: wSvg(`${b(15, 35, 75, 46, "WR-NODE", "Producer")}${b(15, 95, 75, 46, "Grandmaster", "Producer")}<path d="M 90 58 L 120 88" stroke="var(--border-strong)" stroke-width="1.5"/><path d="M 90 118 L 120 88" stroke="var(--border-strong)" stroke-width="1.5"/><rect x="120" y="50" width="75" height="76" rx="5" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)" stroke-width="1.2"/><text x="157" y="84" fill="var(--tint-indigo-fg)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Event Bus</text><text x="157" y="100" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">wr.telemetry</text><path d="M 195 88 L 225 88" stroke="var(--border-strong)" stroke-width="1.5"/>${b(225, 60, 80, 56, "TimescaleDB", "Consumer", "var(--tint-emerald-bg)")}`, "Data Integration")
    },
    {
      id: "er", title: "Entity Relationship", family: "data", familyName: "Data & Schema", pattern: "Traceable Block",
      desc: "Entity-Relationship model linking clock devices, optical channels, and timestamped phase readings.",
      prompt: "Model the ER diagram for optical nodes, calibration channels, and phase samples.",
      doc: "references/type-er.md",
      svg: wSvg(`${b(15, 40, 120, 96, "optical_node", "PK: node_id (INT)")}<line x1="135" y1="88" x2="185" y2="88" stroke="var(--border-strong)" stroke-width="1.5"/><text x="145" y="82" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">1</text><text x="175" y="82" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">N</text>${b(185, 40, 120, 96, "phase_sample", "FK: node_id, time")}`, "Entity Relationship")
    },
    {
      id: "db-schema", title: "Database Schema", family: "data", familyName: "Data & Schema", pattern: "Traceable Block",
      desc: "TimescaleDB Hypertable schema definitions with partition keys, timestamp indexes, and column types.",
      prompt: "Draw a database schema table card for the wr_phase_telemetry hypertable.",
      doc: "references/type-db-schema.md",
      svg: wSvg(`<rect x="25" y="20" width="270" height="136" rx="6" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.2"/><rect x="25" y="20" width="270" height="32" rx="6" fill="var(--bg-elevated)" stroke="var(--border-strong)"/><text x="40" y="42" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">wr_phase_telemetry (Hypertable)</text><text x="40" y="74" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11">PK time</text><text x="150" y="74" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">TIMESTAMPTZ</text><text x="40" y="98" fill="var(--text-primary)" font-family="var(--font-mono)" font-size="11">FK node_id</text><text x="150" y="98" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">INT4</text><text x="40" y="122" fill="var(--text-primary)" font-family="var(--font-mono)" font-size="11">offset_ps</text><text x="150" y="122" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">NUMERIC(10,3)</text><text x="40" y="146" fill="var(--text-primary)" font-family="var(--font-mono)" font-size="11">allan_dev</text><text x="150" y="146" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">FLOAT8</text>`, "Database Schema")
    },
    {
      id: "uml-class", title: "UML Class Diagram", family: "data", familyName: "Data & Schema", pattern: "Traceable Block",
      desc: "Object-oriented class structures for PhaseController, DdmtdDetector, and TelemetryWriter.",
      prompt: "Create a UML class model showing inheritance and composition in the White Rabbit controller.",
      doc: "references/type-uml-class.md",
      svg: wSvg(`${b(15, 20, 130, 60, "PhaseController", "+ lockPhase(): bool")}<path d="M 80 80 L 80 100" stroke="var(--border-strong)" stroke-width="1.5"/>${b(15, 100, 130, 60, "DdmtdDetector", "- vcxo_offset: float")}<path d="M 145 50 L 175 50" stroke="var(--border-strong)" stroke-width="1.5"/>${b(175, 20, 130, 60, "TelemetryWriter", "+ append(sample): int")}`, "UML Class Diagram")
    }
  ];

  window.ATLAS_CATALOG = (window.ATLAS_CATALOG || []).concat(items);
})();
