/* SPDX-License-Identifier: MIT */
/* Quiet UI Diagrams Atlas — Flows & State (9) and Product & Strategy (8) Catalog */

(function() {
  const b = (x, y, w, h, t, s, f) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="${f||'var(--bg-surface)'}" stroke="var(--border-strong)" stroke-width="1.2"/><text x="${x+w/2}" y="${y+h/2-(s?4:0)}" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">${t}</text>${s?`<text x="${x+w/2}" y="${y+h/2+12}" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">${s}</text>`:''}`;
  const wSvg = (inner, desc) => `<svg viewBox="0 0 320 176" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${desc}">${inner}</svg>`;

  const items = [
    {
      id: "flowchart", title: "Flowchart", family: "flows", familyName: "Flows & State", pattern: "Paired Policy Evaluation",
      desc: "Branching decision logic evaluating picosecond phase errors and triggering corrective VCXO tuning.",
      prompt: "Create a flowchart evaluating phase error tolerance (> 1.2ps) and routing to tuning or logging.",
      doc: "references/type-flowchart.md",
      svg: wSvg(`${b(15, 68, 75, 40, "Read Phase", "")}<path d="M 90 88 L 120 88" stroke="var(--border-strong)" stroke-width="1.5"/><polygon points="160,56 200,88 160,120 120,88" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.2"/><text x="160" y="92" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">&gt; 1.2ps?</text><path d="M 160 56 L 160 38 L 225 38" stroke="var(--status-warn)" stroke-width="1.5"/><text x="175" y="48" fill="var(--status-warn)" font-family="var(--font-mono)" font-size="11">Yes</text>${b(225, 18, 80, 40, "Tune VCXO", "DDMTD Loop", "var(--tint-amber-bg)")}<path d="M 200 88 L 225 88" stroke="var(--status-ok)" stroke-width="1.5"/><text x="210" y="82" fill="var(--status-ok)" font-family="var(--font-mono)" font-size="11">No</text>${b(225, 68, 80, 40, "Log Ingest", "TimescaleDB", "var(--tint-emerald-bg)")}`, "Flowchart Decision Logic")
    },
    {
      id: "process", title: "Process Workflow", family: "flows", familyName: "Flows & State", pattern: "Stage Framework",
      desc: "Four-stage linear progression: Laser Power, Fiber Compensation, DDMTD Locking, and Telemetry.",
      prompt: "Render a staged process flow diagram for White Rabbit node synchronization.",
      doc: "references/type-process.md",
      svg: wSvg(`${b(15, 20, 65, 136, "1. Laser", "Optics", "var(--tint-indigo-bg)")}${b(85, 20, 70, 136, "2. Delay", "Calibrate")}${b(160, 20, 70, 136, "3. Lock", "DDMTD PLL", "var(--tint-emerald-bg)")}${b(235, 20, 70, 136, "4. Ingest", "Hypertable")}`, "Process Stages")
    },
    {
      id: "sequence", title: "Sequence Diagram", family: "flows", familyName: "Flows & State", pattern: "Stage Framework",
      desc: "Synchronous handshake and timing packet exchange between Master, Helper, and Node endpoints.",
      prompt: "Draw a sequence diagram detailing the PTP phase calibration handshake.",
      doc: "references/type-sequence.md",
      svg: wSvg(`${b(20, 15, 75, 26, "Grandmaster", "")}${b(120, 15, 80, 26, "DDMTD PLL", "")}${b(225, 15, 75, 26, "WR-NODE-01", "")}<line x1="57" y1="41" x2="57" y2="160" stroke="var(--border-strong)" stroke-dasharray="3 3"/><line x1="160" y1="41" x2="160" y2="160" stroke="var(--border-strong)" stroke-dasharray="3 3"/><line x1="262" y1="41" x2="262" y2="160" stroke="var(--border-strong)" stroke-dasharray="3 3"/><line x1="57" y1="65" x2="160" y2="65" stroke="var(--border-strong)" stroke-width="1.5"/><text x="108" y="60" fill="var(--text-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">1. Sync Beacon</text><line x1="160" y1="95" x2="262" y2="95" stroke="var(--accent-primary)" stroke-width="1.5"/><text x="211" y="90" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">2. Phase Error</text><line x1="262" y1="125" x2="160" y2="125" stroke="var(--border-strong)" stroke-width="1.5" stroke-dasharray="3 3"/><text x="211" y="120" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">3. Ack Lock</text>`, "Sequence Handshake")
    },
    {
      id: "state", title: "State Machine", family: "flows", familyName: "Flows & State", pattern: "Lifecycle Phase Map",
      desc: "Finite state machine transitions: INITIALIZING, ACQUIRING, LOCKED, HOLDOVER, and RECOVERY.",
      prompt: "Generate a finite state machine diagram modeling the optical phase-lock lifecycle.",
      doc: "references/type-state.md",
      svg: wSvg(`${b(15, 30, 85, 42, "INIT", "Booting")}<path d="M 100 51 L 125 51" stroke="var(--border-strong)" stroke-width="1.5"/>${b(125, 30, 85, 42, "ACQUIRING", "Coarse Lock", "var(--tint-amber-bg)")}<path d="M 210 51 L 235 51" stroke="var(--border-strong)" stroke-width="1.5"/>${b(235, 30, 75, 42, "LOCKED", "0.8ps Jitter", "var(--tint-emerald-bg)")}<path d="M 272 72 L 272 105 L 180 105" stroke="var(--status-warn)" stroke-width="1.5"/><text x="235" y="100" fill="var(--status-warn)" font-family="var(--font-mono)" font-size="11">Fiber Drift</text>${b(80, 95, 100, 42, "HOLDOVER", "Internal VCXO", "var(--tint-rose-bg)")}`, "State Machine")
    },
    {
      id: "swimlane", title: "Swimlane Workflow", family: "flows", familyName: "Flows & State", pattern: "Governance & Control",
      desc: "Cross-functional responsibility lanes: Optics Hardware, FPGA Firmware, and Cloud Ingestion.",
      prompt: "Create a swimlane diagram coordinating hardware, firmware, and telemetry responsibilities.",
      doc: "references/type-swimlane.md",
      svg: wSvg(`<rect x="15" y="15" width="290" height="42" fill="var(--bg-elevated)" stroke="var(--border-hairline)"/><text x="25" y="40" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Optics</text>${b(90, 21, 95, 30, "Align Laser", "")}<rect x="15" y="60" width="290" height="42" fill="var(--bg-surface)" stroke="var(--border-hairline)"/><text x="25" y="85" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">FPGA</text>${b(150, 66, 100, 30, "DDMTD Detect", "", "var(--tint-indigo-bg)")}<rect x="15" y="105" width="290" height="42" fill="var(--bg-elevated)" stroke="var(--border-hairline)"/><text x="25" y="130" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Cloud</text>${b(205, 111, 90, 30, "Ingest SQL", "", "var(--tint-emerald-bg)")}`, "Swimlane Responsibilities")
    },
    {
      id: "loop", title: "Closed Feedback Loop", family: "flows", familyName: "Flows & State", pattern: "Lifecycle Phase Map",
      desc: "Continuous phase error detection, VCXO DAC correction, and real-time optical loopback.",
      prompt: "Diagram the closed-loop feedback control cycle of the DDMTD phase correction circuit.",
      doc: "references/type-loop.md",
      svg: wSvg(`${b(115, 15, 90, 38, "Phase Detect", "DDMTD Mixer")}<path d="M 205 34 C 270 34 270 142 205 142" stroke="var(--accent-primary)" stroke-width="2" fill="none"/><text x="265" y="88" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11">DAC Tune</text>${b(115, 123, 90, 38, "VCXO Control", "Laser Bias")}<path d="M 115 142 C 50 142 50 34 115 34" stroke="var(--status-ok)" stroke-width="2" fill="none"/><text x="55" y="88" fill="var(--status-ok)" font-family="var(--font-mono)" font-size="11">Fiber Loop</text>`, "Feedback Loop")
    },
    {
      id: "fishbone", title: "Fishbone Root Cause", family: "flows", familyName: "Flows & State", pattern: "Traceable Block",
      desc: "Ishikawa analysis of phase dispersion factors: Thermal Gradient, Fiber Stress, Laser Chirp, Power Jitter.",
      prompt: "Construct a fishbone diagram analyzing root causes of optical phase jitter in the array.",
      doc: "references/type-fishbone.md",
      svg: wSvg(`<line x1="20" y1="88" x2="220" y2="88" stroke="var(--border-strong)" stroke-width="2"/>${b(220, 68, 85, 40, "Phase Jitter", "&gt; 1.5ps Drift", "var(--tint-rose-bg)")}<line x1="60" y1="25" x2="100" y2="88" stroke="var(--border-strong)" stroke-width="1.5"/><text x="35" y="22" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Thermal</text><line x1="140" y1="25" x2="180" y2="88" stroke="var(--border-strong)" stroke-width="1.5"/><text x="120" y="22" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Laser Chirp</text><line x1="60" y1="150" x2="100" y2="88" stroke="var(--border-strong)" stroke-width="1.5"/><text x="35" y="165" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Fiber Stress</text><line x1="140" y1="150" x2="180" y2="88" stroke="var(--border-strong)" stroke-width="1.5"/><text x="120" y="165" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">Power Ripple</text>`, "Fishbone Root Cause")
    },
    {
      id: "timeline", title: "Chronological Timeline", family: "flows", familyName: "Flows & State", pattern: "Lifecycle Phase Map",
      desc: "Timing lock acquisition timeline from Cold Start T0 to Continuous Picosecond Calibration.",
      prompt: "Generate an operational milestone timeline for White Rabbit network synchronization.",
      doc: "references/type-timeline.md",
      svg: wSvg(`<line x1="20" y1="88" x2="300" y2="88" stroke="var(--border-strong)" stroke-width="2"/><circle cx="50" cy="88" r="6" fill="var(--accent-primary)"/><text x="50" y="65" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">T0: Boot</text><text x="50" y="112" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Power On</text><circle cx="140" cy="88" r="6" fill="var(--status-warn)"/><text x="140" y="65" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">T+10ms</text><text x="140" y="112" fill="var(--status-warn)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">Coarse Lock</text><circle cx="250" cy="88" r="6" fill="var(--status-ok)"/><text x="250" y="65" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">T+60s</text><text x="250" y="112" fill="var(--status-ok)" font-family="var(--font-mono)" font-size="11" text-anchor="middle">0.8ps Stable</text>`, "Milestone Timeline")
    },
    {
      id: "gantt", title: "Gantt Schedule", family: "flows", familyName: "Flows & State", pattern: "Stage Framework",
      desc: "Deployment task Gantt bar chart: Laser Calibration, Fiber Laying, DDMTD Tuning, Acceptance Testing.",
      prompt: "Render a Gantt chart tracking tasks and durations for optical array commissioning.",
      doc: "references/type-gantt.md",
      svg: wSvg(`<line x1="90" y1="20" x2="90" y2="155" stroke="var(--border-strong)"/><text x="20" y="42" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">Laser Cal</text><rect x="95" y="28" width="80" height="20" rx="3" fill="var(--accent-primary)"/><text x="20" y="77" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">Fiber Install</text><rect x="135" y="63" width="90" height="20" rx="3" fill="var(--tint-indigo-bg)" stroke="var(--accent-primary)"/><text x="20" y="112" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">DDMTD Test</text><rect x="180" y="98" width="75" height="20" rx="3" fill="var(--tint-emerald-bg)" stroke="var(--status-ok)"/><text x="20" y="147" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">Hypertable</text><rect x="230" y="133" width="70" height="20" rx="3" fill="var(--status-ok)"/>`, "Gantt Schedule")
    },
    {
      id: "wardley", title: "Wardley Value Map", family: "strategy", familyName: "Product & Strategy", pattern: "Governance & Control",
      desc: "Value chain vs Evolution mapping from Genesis (optical research) to Commodity (atomic reference).",
      prompt: "Draw a Wardley Map positioning optical phase locking along the evolution axis.",
      doc: "references/type-wardley.md",
      svg: wSvg(`<line x1="30" y1="150" x2="300" y2="150" stroke="var(--border-strong)"/><line x1="30" y1="20" x2="30" y2="150" stroke="var(--border-strong)"/><text x="35" y="32" fill="var(--text-muted)" font-family="var(--font-sans)" font-size="11">Value</text><text x="240" y="145" fill="var(--text-muted)" font-family="var(--font-sans)" font-size="11">Commodity</text><circle cx="60" cy="50" r="5" fill="var(--accent-primary)"/><text x="70" y="54" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">DDMTD R&amp;D</text><circle cx="150" cy="80" r="5" fill="var(--accent-primary)"/><text x="160" y="84" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">WR Node PCIe</text><circle cx="270" cy="120" r="5" fill="var(--status-ok)"/><text x="220" y="115" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11">Atomic Clock</text>`, "Wardley Map")
    },
    {
      id: "service-blueprint", title: "Service Blueprint", family: "strategy", familyName: "Product & Strategy", pattern: "Stage Framework",
      desc: "Multi-tier blueprint aligning telemetry dashboards, FPGA daemons, and physical fiber trunks.",
      prompt: "Construct a service blueprint for the timing network synchronization service.",
      doc: "references/type-service-blueprint.md",
      svg: wSvg(`${b(15, 18, 290, 32, "User Line · Grafana Observability Dashboard", "")}<line x1="15" y1="56" x2="305" y2="56" stroke="var(--accent-primary)" stroke-dasharray="4 2"/><text x="25" y="70" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11">Line of Interaction</text>${b(15, 76, 290, 32, "Frontstage · TimescaleDB Hypertable API", "", "var(--tint-indigo-bg)")}${b(15, 120, 290, 32, "Backstage · FPGA DDMTD Phase Tracking PLL", "", "var(--tint-emerald-bg)")}`, "Service Blueprint")
    },
    {
      id: "journey", title: "Operator Journey", family: "strategy", familyName: "Product & Strategy", pattern: "Lifecycle Phase Map",
      desc: "Experience curve of a network engineer provisioning nodes, diagnosing jitter, and locking phase.",
      prompt: "Map the operator journey and satisfaction curve during optical array commissioning.",
      doc: "references/type-journey.md",
      svg: wSvg(`<path d="M 30 110 Q 90 40 160 90 T 290 30" stroke="var(--accent-primary)" stroke-width="2.5" fill="none"/><circle cx="30" cy="110" r="4" fill="var(--accent-primary)"/><text x="30" y="130" fill="var(--text-muted)" font-family="var(--font-sans)" font-size="11">1. Rack</text><circle cx="110" cy="56" r="4" fill="var(--status-ok)"/><text x="110" y="42" fill="var(--status-ok)" font-family="var(--font-sans)" font-size="11">2. Light On</text><circle cx="190" cy="82" r="4" fill="var(--status-warn)"/><text x="190" y="102" fill="var(--status-warn)" font-family="var(--font-sans)" font-size="11">3. Calibrate</text><circle cx="290" cy="30" r="4" fill="var(--status-ok)"/><text x="250" y="24" fill="var(--status-ok)" font-family="var(--font-sans)" font-size="11">4. Sub-ps Lock</text>`, "Operator Journey")
    },
    {
      id: "story-map", title: "Story Map", family: "strategy", familyName: "Product & Strategy", pattern: "Stage Framework",
      desc: "Sprint release slicing across user activities: Hardware Ingest, Phase Locking, and Analytics.",
      prompt: "Draw a user story map with backbone epics and release slices for the White Rabbit project.",
      doc: "references/type-story-map.md",
      svg: wSvg(`${b(15, 18, 90, 34, "Epic: Hardware", "")}${b(115, 18, 90, 34, "Epic: Lock", "")}${b(215, 18, 90, 34, "Epic: Analytics", "")}<line x1="15" y1="62" x2="305" y2="62" stroke="var(--border-hairline)"/><text x="20" y="78" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">Release 1.0 (MVP)</text>${b(15, 86, 90, 32, "Laser SFP+", "", "var(--tint-indigo-bg)")}${b(115, 86, 90, 32, "Coarse PTP", "", "var(--tint-indigo-bg)")}${b(215, 86, 90, 32, "Raw Ingest", "", "var(--tint-indigo-bg)")}${b(115, 126, 90, 32, "DDMTD 0.8ps", "", "var(--tint-emerald-bg)")}${b(215, 126, 90, 32, "Allan Dev", "", "var(--tint-emerald-bg)")}`, "Story Map")
    },
    {
      id: "kanban", title: "Kanban Board", family: "strategy", familyName: "Product & Strategy", pattern: "Stage Framework",
      desc: "Kanban work-in-progress board organizing node calibration across Backlog, Active, and Locked.",
      prompt: "Render a Kanban board visualizing White Rabbit node commissioning tasks.",
      doc: "references/type-kanban.md",
      svg: wSvg(`<rect x="15" y="16" width="90" height="144" rx="5" fill="var(--bg-elevated)" stroke="var(--border-strong)"/><text x="60" y="34" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Backlog (2)</text>${b(22, 44, 76, 32, "WR-NODE-07", "")}${b(22, 84, 76, 32, "WR-NODE-08", "")}<rect x="115" y="16" width="90" height="144" rx="5" fill="var(--bg-elevated)" stroke="var(--border-strong)"/><text x="160" y="34" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Calibrating (1)</text>${b(122, 44, 76, 32, "WR-NODE-06", "DDMTD Run", "var(--tint-amber-bg)")}<rect x="215" y="16" width="90" height="144" rx="5" fill="var(--bg-elevated)" stroke="var(--border-strong)"/><text x="260" y="34" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600" text-anchor="middle">Locked (5)</text>${b(222, 44, 76, 32, "WR-01..05", "Sub-ps Sync", "var(--tint-emerald-bg)")}`, "Kanban Board")
    },
    {
      id: "org-chart", title: "Engineering Org Chart", family: "strategy", familyName: "Product & Strategy", pattern: "Governance & Control",
      desc: "Hierarchical division of responsibilities: Timing Systems Lead -> Hardware, Firmware, Infrastructure.",
      prompt: "Generate an org chart showing engineering team ownership of the optical array.",
      doc: "references/type-org-chart.md",
      svg: wSvg(`${b(105, 18, 110, 36, "Timing Lead", "Systems Arch")}<line x1="160" y1="54" x2="160" y2="76" stroke="var(--border-strong)"/><line x1="55" y1="76" x2="265" y2="76" stroke="var(--border-strong)"/><line x1="55" y1="76" x2="55" y2="92" stroke="var(--border-strong)"/><line x1="160" y1="76" x2="160" y2="92" stroke="var(--border-strong)"/><line x1="265" y1="76" x2="265" y2="92" stroke="var(--border-strong)"/>${b(15, 92, 85, 48, "Optics Eng", "Fiber Carrier")}${b(115, 92, 90, 48, "FPGA Team", "DDMTD Core")}${b(220, 92, 85, 48, "Data Infra", "TimescaleDB")}`, "Org Chart")
    },
    {
      id: "tree", title: "Decision Tree", family: "strategy", familyName: "Product & Strategy", pattern: "Traceable Block",
      desc: "Hierarchical selection logic choosing between Optical Phase Lock and Coaxial Backup.",
      prompt: "Construct a decision tree taxonomy for timing synchronization protocol selection.",
      doc: "references/type-tree.md",
      svg: wSvg(`${b(15, 66, 85, 44, "Sync Method", "Requirements")}<path d="M 100 88 L 135 50" stroke="var(--accent-primary)" stroke-width="1.5"/><text x="110" y="60" fill="var(--accent-primary)" font-family="var(--font-mono)" font-size="11">&lt; 1ps</text>${b(135, 28, 170, 44, "Optical White Rabbit", "DDMTD Phase Lock", "var(--tint-emerald-bg)")}<path d="M 100 88 L 135 126" stroke="var(--border-strong)" stroke-width="1.5"/><text x="110" y="120" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="11">&gt; 1ns</text>${b(135, 104, 170, 44, "Standard PTP / NTP", "Coaxial Fallback")}`, "Decision Tree")
    },
    {
      id: "quadrant", title: "Precision-Complexity Matrix", family: "strategy", familyName: "Product & Strategy", pattern: "Governance & Control",
      desc: "2x2 positioning matrix comparing timing accuracy vs engineering complexity across architectures.",
      prompt: "Render a 2x2 quadrant matrix mapping synchronization protocols by accuracy and complexity.",
      doc: "references/type-quadrant.md",
      svg: wSvg(`<line x1="160" y1="20" x2="160" y2="155" stroke="var(--border-strong)"/><line x1="20" y1="88" x2="300" y2="88" stroke="var(--border-strong)"/><text x="290" y="80" fill="var(--text-muted)" font-family="var(--font-sans)" font-size="11" text-anchor="end">Complexity &rarr;</text><text x="170" y="32" fill="var(--text-muted)" font-family="var(--font-sans)" font-size="11">Accuracy &uarr;</text><circle cx="80" cy="125" r="5" fill="var(--text-muted)"/><text x="90" y="129" fill="var(--text-secondary)" font-family="var(--font-sans)" font-size="11">NTP</text><circle cx="110" cy="70" r="5" fill="var(--accent-primary)"/><text x="120" y="74" fill="var(--text-secondary)" font-family="var(--font-sans)" font-size="11">PTP IEEE1588</text><circle cx="240" cy="40" r="6" fill="var(--status-ok)"/><text x="180" y="44" fill="var(--text-primary)" font-family="var(--font-sans)" font-size="11" font-weight="600">WR Optical PLL</text>`, "2x2 Matrix")
    }
  ];

  window.ATLAS_CATALOG = (window.ATLAS_CATALOG || []).concat(items);
})();
