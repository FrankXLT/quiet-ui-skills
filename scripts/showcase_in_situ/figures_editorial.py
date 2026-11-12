# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v7.1 Editorial Figures (Doc-1, Doc-2, Doc-3, Doc-4B, Doc-4A)."""


def render_doc1_figure() -> str:
    """Render Doc-1 Figure 1.1 with 3-plane stack and Allan deviation plot."""
    return """<!-- QUIET-UI-V71-DOC1-START -->
            <figure style="margin:1.5rem 0; border-top:1px solid var(--border-grid); border-bottom:1px solid var(--border-grid); padding:1rem 0;">
              <div style="overflow-x:auto;">
                <svg width="100%" height="220" viewBox="0 0 660 220" role="img" aria-label="Optical Syntonization Stack and Allan Deviation Plot">
                  <text x="20" y="22" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-secondary)">EXPLODED 3-PLANE OPTICAL STACK</text>
                  <!-- Plane 3 (Top: PCIe BAR0 TAI Ring) -->
                  <polygon points="45,45 200,32 255,62 100,75" fill="var(--tint-indigo-bg)" stroke="var(--border-strong)" stroke-width="1.3"/>
                  <line x1="255" y1="62" x2="280" y2="52" stroke="var(--text-secondary)" stroke-width="1"/><circle cx="280" cy="52" r="2" fill="var(--accent-focal)"/>
                  <text x="40" y="62" font-family="var(--font-serif)" font-size="11" font-style="italic" fill="var(--text-main)">Plane 3 · PCIe BAR0 TAI Ring</text>
                  <!-- Plane 2 (Mid: DDMTD Beat Detector) -->
                  <polygon points="45,95 200,82 255,112 100,125" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.3"/>
                  <line x1="255" y1="112" x2="280" y2="102" stroke="var(--text-secondary)" stroke-width="1"/><circle cx="280" cy="102" r="2" fill="var(--accent-focal)"/>
                  <text x="40" y="112" font-family="var(--font-serif)" font-size="11" font-style="italic" fill="var(--text-main)">Plane 2 · DDMTD Beat (N=2^14)</text>
                  <!-- Plane 1 (Base: SMF-28e+ Fiber) -->
                  <polygon points="45,145 200,132 255,162 100,175" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.3"/>
                  <line x1="255" y1="162" x2="280" y2="152" stroke="var(--text-secondary)" stroke-width="1"/><circle cx="280" cy="152" r="2" fill="var(--accent-focal)"/>
                  <text x="40" y="162" font-family="var(--font-serif)" font-size="11" font-style="italic" fill="var(--text-main)">Plane 1 · 1490/1310nm SMF-28e+</text>
                  <line x1="305" y1="18" x2="305" y2="202" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="4,4"/>
                  <!-- Right Panel: Allan Deviation σ_y(τ) -->
                  <text x="365" y="22" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-secondary)">MODIFIED ALLAN DEVIATION σ_y(τ)</text>
                  <line x1="365" y1="36" x2="365" y2="175" stroke="currentColor" stroke-width="1"/><line x1="365" y1="175" x2="640" y2="175" stroke="currentColor" stroke-width="1"/>
                  <line x1="365" y1="80" x2="640" y2="80" stroke="currentColor" stroke-opacity="0.18" stroke-dasharray="3,3"/><line x1="365" y1="125" x2="640" y2="125" stroke="currentColor" stroke-opacity="0.18" stroke-dasharray="3,3"/>
                  <polyline fill="none" stroke="currentColor" stroke-opacity="0.45" stroke-width="1.3" stroke-dasharray="5,4" points="375,56 430,76 495,96 555,108 605,102 635,112"/>
                  <polyline fill="none" stroke="var(--accent-focal)" stroke-width="1.9" points="375,72 430,98 495,124 555,142 605,150 635,153"/>
                  <g stroke="var(--accent-focal)" stroke-width="1.2">
                    <line x1="430" y1="92" x2="430" y2="104"/><line x1="495" y1="118" x2="495" y2="130"/><line x1="555" y1="137" x2="555" y2="147"/><line x1="605" y1="145" x2="605" y2="155"/>
                    <circle cx="430" cy="98" r="2.5" fill="var(--bg-canvas)"/><circle cx="495" cy="124" r="2.5" fill="var(--bg-canvas)"/><circle cx="555" cy="142" r="2.5" fill="var(--bg-canvas)"/><circle cx="605" cy="150" r="2.5" fill="var(--bg-canvas)"/>
                  </g>
                  <text x="360" y="42" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">1e-12</text><text x="360" y="85" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">1e-13</text><text x="360" y="130" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">1e-14</text><text x="360" y="175" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">1e-15</text>
                  <text x="375" y="194" font-family="var(--font-mono)" font-size="11" fill="currentColor">τ=1s</text><text x="480" y="194" font-family="var(--font-mono)" font-size="11" fill="currentColor">τ=100s</text><text x="560" y="194" font-family="var(--font-mono)" font-size="11" fill="currentColor">τ=1,000s</text>
                  <text x="475" y="92" font-family="var(--font-mono)" font-size="11" fill="currentColor" opacity="0.65">Uncompensated Coax</text>
                  <text x="445" y="138" font-family="var(--font-mono)" font-size="11" font-weight="600" fill="var(--accent-focal)">DWDM Locked 0.81 ps RMS</text>
                </svg>
              </div>
              <figcaption style="font-family:var(--font-serif); font-size:12px; font-style:italic; color:var(--text-secondary); margin-top:0.35rem;">
                Figure 1.1: 3-Plane Optical Syntonization Stack (Left) paired with Modified Allan deviation σ_y(τ) across integration intervals τ ∈ [1, 10⁴] seconds (Right) demonstrating 0.81 ps RMS phase lock.
              </figcaption>
            </figure>
            <!-- QUIET-UI-V71-DOC1-END -->"""


def render_doc2_figure() -> str:
    """Render Doc-2 Figure 2.1 before/after architecture-delta figure."""
    return """<!-- QUIET-UI-V71-DOC2-START -->
        <figure class="va-mermaid-figure" id="doc2-mermaid-fig">
          <div class="va-mermaid-hdr">
            <span><i class="fa-solid fa-diagram-project" style="margin-right:6px;"></i>Figure 2.1 — Bidirectional DWDM White Rabbit Timing Distribution Topology (Architecture Delta)</span>
            <button type="button" class="va-pill-btn" onclick="toggleMermaidSource(this)"><i class="fa-solid fa-code"></i><span>Diagram | Mermaid Source</span></button>
          </div>
          <svg class="va-mermaid-svg" viewBox="0 0 740 192" role="img" aria-label="DWDM Optical Timing Architecture Delta">
            <defs>
              <marker id="mm-arr-1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--border-strong)"/></marker>
              <marker id="mm-arr-focal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--accent-focal)"/></marker>
              <marker id="mm-arr-ok" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-ok)"/></marker>
            </defs>
            <!-- Legacy Lane -->
            <rect x="20" y="24" width="130" height="48" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4,4"/>
            <text x="85" y="46" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">NIST-H4 MASER</text><text x="85" y="60" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">10MHz / 1PPS</text>
            <rect x="185" y="24" width="230" height="48" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4,4"/>
            <text x="300" y="44" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">LDF4-50A COAX DISTRIBUTION</text><text x="300" y="58" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-err)">194.2 ps skew · -$620k/yr</text>
            <rect x="450" y="24" width="270" height="48" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4,4"/>
            <text x="585" y="44" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">LEGACY RECEIVERS [RETIRING]</text><text x="585" y="58" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">Phase Drift Ceiling Exceeded</text>
            <line x1="150" y1="48" x2="185" y2="48" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4,4" marker-end="url(#mm-arr-1)"/>
            <line x1="415" y1="48" x2="450" y2="48" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4,4" marker-end="url(#mm-arr-1)"/>
            <!-- Target Ring -->
            <rect x="20" y="116" width="130" height="52" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
            <text x="85" y="138" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">NIST-H4 MASER</text><text x="85" y="154" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">TAI Atomic Ref</text>
            <rect x="186" y="116" width="164" height="52" rx="6" fill="var(--bg-card)" stroke="var(--accent-focal)" stroke-width="1.8"/>
            <text x="268" y="138" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">DWDM GRANDMASTER</text><text x="268" y="154" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--accent-focal)">1490nm Tx / 1310nm Rx</text>
            <rect x="384" y="116" width="162" height="52" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
            <text x="465" y="138" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">DDMTD HELPER PLL</text><text x="465" y="154" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">alpha=2.742e-4 [NEW]</text>
            <rect x="580" y="116" width="140" height="52" rx="6" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1.5"/>
            <text x="650" y="138" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">8x SECTORS [NEW]</text><text x="650" y="154" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-main)">81.4 ps SLA PASS</text>
            <line x1="150" y1="142" x2="186" y2="142" stroke="var(--border-strong)" stroke-width="1.5" marker-end="url(#mm-arr-1)"/>
            <line x1="350" y1="142" x2="384" y2="142" stroke="var(--accent-focal)" stroke-width="1.5" marker-end="url(#mm-arr-focal)"/>
            <line x1="546" y1="142" x2="580" y2="142" stroke="var(--status-ok)" stroke-width="1.5" marker-end="url(#mm-arr-ok)"/>
          </svg>
          <pre class="va-mermaid-code">flowchart TD
  subgraph LEGACY["Legacy Coaxial Baseline [RETIRING]"]
    M1["NIST-H4 Maser"] -.-> C1["LDF4-50A Coax Splitter (194.2 ps skew)"]
    C1 -.-> R1["Legacy Receivers (-$620k/yr OPEX)"]
  end
  subgraph TARGET["Active DWDM Optical Array [ADDED]"]
    M2["NIST-H4 Maser"] --> G2["DWDM Grandmaster (1490/1310nm)"]
    G2 --> D2["DDMTD Helper PLL (alpha=2.742e-4)"]
    D2 --> R2["8x Sector Receivers (81.4 ps SLA PASS)"]
  end</pre>
        </figure>
        <!-- QUIET-UI-V71-DOC2-END -->"""


def render_doc3_figure() -> str:
    """Render Doc-3 Figure 3.1 normative finite state machine figure."""
    return """<!-- QUIET-UI-V71-DOC3-START -->
        <figure class="va-mermaid-figure" id="doc3-mermaid-fig">
          <div class="va-mermaid-hdr">
            <span><i class="fa-solid fa-diagram-project" style="margin-right:6px;"></i>Figure 3.1 — Normative White Rabbit PTP Port State Machine (SPEC-9412 §2)</span>
            <button type="button" class="va-pill-btn" onclick="toggleMermaidSource(this)"><i class="fa-solid fa-code"></i><span>Diagram | Mermaid Source</span></button>
          </div>
          <svg class="va-mermaid-svg" viewBox="0 0 740 188" role="img" aria-label="PTP Port State Machine Diagram">
            <defs>
              <marker id="sm-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--border-strong)"/></marker>
              <marker id="sm-arr-ok" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-ok)"/></marker>
              <marker id="sm-arr-warn" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-warn)"/></marker>
              <marker id="sm-arr-err" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-err)"/></marker>
            </defs>
            <circle cx="28" cy="46" r="8" fill="var(--text-main)"/><circle cx="28" cy="46" r="14" fill="none" stroke="var(--text-main)" stroke-width="1.5"/>
            <rect x="68" y="22" width="114" height="48" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.4"/>
            <text x="125" y="44" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">UNCALIBRATED</text><text x="125" y="58" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">Port Init</text>
            <rect x="220" y="22" width="125" height="48" rx="6" fill="var(--bg-card)" stroke="var(--accent-focal)" stroke-width="1.5"/>
            <text x="282" y="44" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">PHASE_CALIBRATE</text><text x="282" y="58" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--accent-focal)">DDMTD Sweep</text>
            <rect x="385" y="22" width="115" height="48" rx="6" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1.6"/>
            <text x="442" y="44" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">SLAVE_LOCKED</text><text x="442" y="58" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-main)">skew &lt; 85ps</text>
            <rect x="540" y="22" width="100" height="48" rx="6" fill="var(--status-warn-bg)" stroke="var(--status-warn)" stroke-width="1.6"/>
            <text x="590" y="44" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-warn)">HOLDOVER</text><text x="590" y="58" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-main)">OCXO Drift</text>
            <rect x="670" y="22" width="55" height="48" rx="6" fill="var(--status-err-bg)" stroke="var(--status-err)" stroke-width="2"/>
            <rect x="673" y="25" width="49" height="42" rx="4" fill="none" stroke="var(--status-err)" stroke-width="1"/>
            <text x="697" y="50" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-err)">FAULT</text>
            <line x1="42" y1="46" x2="68" y2="46" stroke="var(--border-strong)" stroke-width="1.4" marker-end="url(#sm-arr)"/>
            <line x1="182" y1="46" x2="220" y2="46" stroke="var(--border-strong)" stroke-width="1.4" marker-end="url(#sm-arr)"/><text x="201" y="38" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">link_up</text>
            <line x1="345" y1="46" x2="385" y2="46" stroke="var(--status-ok)" stroke-width="1.5" marker-end="url(#sm-arr-ok)"/><text x="365" y="38" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-ok)">alpha_ok</text>
            <line x1="500" y1="46" x2="540" y2="46" stroke="var(--status-warn)" stroke-width="1.5" marker-end="url(#sm-arr-warn)"/><text x="520" y="38" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-warn)">rx_los</text>
            <line x1="640" y1="46" x2="670" y2="46" stroke="var(--status-err)" stroke-width="1.4" marker-end="url(#sm-arr-err)"/><text x="655" y="38" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-err)">&gt;42m</text>
            <path d="M 590 70 L 590 132 A 8 8 0 0 1 582 140 L 133 140 A 8 8 0 0 1 125 132 L 125 70" fill="none" stroke="var(--text-secondary)" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#sm-arr)"/>
            <text x="355" y="134" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">re-lock_sweep [10k DDMTD samples]</text>
          </svg>
          <pre class="va-mermaid-code">stateDiagram-v2
  [*] --> UNCALIBRATED : sfp_link_up
  UNCALIBRATED --> PHASE_CALIBRATE : alpha_sweep
  PHASE_CALIBRATE --> SLAVE_LOCKED : |skew| < 85ps
  SLAVE_LOCKED --> HOLDOVER : sfp_los || skew > 150ps
  HOLDOVER --> FAULT : flywheel_expired (>42m)
  HOLDOVER --> UNCALIBRATED : re-lock_sweep [10k DDMTD]</pre>
        </figure>
        <!-- QUIET-UI-V71-DOC3-END -->"""


def render_doc4b_figure() -> str:
    """Render Doc-4B Medallion pipeline figure."""
    return """<!-- QUIET-UI-V71-DOC4B-START -->
          <figure class="va-mermaid-figure" id="doc4b-medallion-fig" style="margin:12px 0 16px 0;">
            <div class="va-mermaid-hdr">
              <span><i class="fa-solid fa-layer-group" style="margin-right:6px;"></i>Figure 4B.1 — optical_pll.syntonizer Medallion Telemetry Pipeline</span>
            </div>
            <svg class="va-mermaid-svg" viewBox="0 0 740 156" role="img" aria-label="Medallion Telemetry Pipeline Diagram">
              <defs>
                <marker id="med-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--border-strong)"/></marker>
              </defs>
              <rect x="20" y="42" width="200" height="86" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
              <text x="120" y="66" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-secondary)">BRONZE · INGESTION</text><text x="120" y="86" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Raw BAR0 FIFO Stream</text><text x="120" y="106" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">62.5 MHz beat words</text>
              <rect x="270" y="42" width="200" height="86" rx="6" fill="var(--bg-card)" stroke="var(--accent-focal)" stroke-width="1.5"/>
              <text x="370" y="66" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--accent-focal)">SILVER · CALIBRATED</text><text x="370" y="86" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Calibrated TAI Frames</text><text x="370" y="106" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">alpha = 2.742e-4</text>
              <rect x="520" y="42" width="200" height="86" rx="6" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1.5"/>
              <text x="620" y="66" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">GOLD · ANALYTICS</text><text x="620" y="86" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Allan &amp; SLA Rollups</text><text x="620" y="106" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-ok)">wr_skew_1m_cagg · 0.81 ps</text>
              <line x1="220" y1="85" x2="270" y2="85" stroke="var(--border-strong)" stroke-width="1.5" marker-end="url(#med-arr)"/>
              <line x1="470" y1="85" x2="520" y2="85" stroke="var(--status-ok)" stroke-width="1.5" marker-end="url(#med-arr)"/>
            </svg>
          </figure>
          <!-- QUIET-UI-V71-DOC4B-END -->"""


def render_doc4a_figure() -> str:
    """Render Doc-4A Figure 4A.1 4-lifeline sequence diagram with interactive step bands."""
    return """<!-- QUIET-UI-V71-DOC4A-START -->
        <figure class="va-mermaid-figure" id="doc4a-mermaid-fig">
          <div class="va-mermaid-hdr">
            <span><i class="fa-solid fa-code-branch" style="margin-right:6px;"></i>Cutover Verification Pipeline (4-Lifeline Interlock Sequence)</span>
            <button type="button" class="va-pill-btn" onclick="toggleMermaidSource(this)"><i class="fa-solid fa-code"></i><span>Diagram | Mermaid Source</span></button>
          </div>
          <svg class="va-mermaid-svg" viewBox="0 0 660 214" role="img" aria-label="Cutover Gate Sequence Diagram">
            <defs>
              <marker id="seq-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-main)"/></marker>
              <marker id="seq-arr-focal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--accent-focal)"/></marker>
              <marker id="seq-arr-ok" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="var(--status-ok)"/></marker>
            </defs>
            <!-- Lifeline Headers -->
            <rect x="30" y="8" width="100" height="26" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2"/>
            <text x="80" y="25" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Operator CLI</text>
            <rect x="180" y="8" width="120" height="26" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2"/>
            <text x="240" y="25" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">DWDM GM</text>
            <rect x="360" y="8" width="120" height="26" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2"/>
            <text x="420" y="25" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Sector-7 FPGA</text>
            <rect x="525" y="8" width="110" height="26" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.2"/>
            <text x="580" y="25" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">OCXO Flywheel</text>
            <line x1="80" y1="34" x2="80" y2="204" stroke="var(--border-grid)" stroke-width="1.2" stroke-dasharray="3,3"/><line x1="240" y1="34" x2="240" y2="204" stroke="var(--border-grid)" stroke-width="1.2" stroke-dasharray="3,3"/>
            <line x1="420" y1="34" x2="420" y2="204" stroke="var(--border-grid)" stroke-width="1.2" stroke-dasharray="3,3"/><line x1="580" y1="34" x2="580" y2="204" stroke="var(--border-grid)" stroke-width="1.2" stroke-dasharray="3,3"/>
            <!-- 4 Interactive Step Bands -->
            <g class="va-seq-step-band is-active" data-seq-step="0" onclick="selectRunbookStep(0)">
              <rect class="seq-band-bg" x="15" y="42" width="630" height="38" rx="4" fill="transparent"/>
              <line x1="80" y1="62" x2="238" y2="62" stroke="var(--text-main)" stroke-width="1.4" marker-end="url(#seq-arr)"/>
              <text x="160" y="56" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-main)">01. query_sfp_ddm() [Rx &gt; -14 dBm]</text>
            </g>
            <g class="va-seq-step-band" data-seq-step="1" onclick="selectRunbookStep(1)">
              <rect class="seq-band-bg" x="15" y="84" width="630" height="38" rx="4" fill="transparent"/>
              <line x1="240" y1="104" x2="418" y2="104" stroke="var(--text-main)" stroke-width="1.4" marker-end="url(#seq-arr)"/>
              <text x="330" y="98" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-main)">02. write_alpha(2.742e-4) [10k sweep]</text>
            </g>
            <g class="va-seq-step-band" data-seq-step="2" onclick="selectRunbookStep(2)">
              <rect class="seq-band-bg" x="15" y="126" width="630" height="38" rx="4" fill="transparent"/>
              <line x1="420" y1="146" x2="82" y2="146" stroke="var(--accent-focal)" stroke-width="1.6" marker-end="url(#seq-arr-focal)"/>
              <text x="250" y="140" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="600" fill="var(--accent-focal)">03. bar0_dma_lock (SYNC_VALID=1, jitter &lt; 90ps)</text>
            </g>
            <g class="va-seq-step-band" data-seq-step="3" onclick="selectRunbookStep(3)">
              <rect class="seq-band-bg" x="15" y="168" width="630" height="38" rx="4" fill="transparent"/>
              <line x1="420" y1="188" x2="578" y2="188" stroke="var(--status-ok)" stroke-width="1.4" marker-end="url(#seq-arr-ok)"/>
              <text x="500" y="182" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-ok)">04. holdover_gate (drift &lt; 1.2ps/m)</text>
            </g>
          </svg>
          <pre class="va-mermaid-code">sequenceDiagram
  autonumber
  actor Op as Operator CLI
  participant GM as DWDM Grandmaster
  participant FPGA as Sector-7 FPGA
  participant OCXO as OCXO Flywheel
  Op->>GM: 01. query_sfp_ddm() [Rx > -14 dBm]
  GM->>FPGA: 02. write_alpha(2.742e-4) + sweep
  FPGA-->>Op: 03. bar0_dma_lock [SYNC_VALID=1]
  FPGA->>OCXO: 04. test_holdover_gate() [<1.2ps/min]</pre>
        </figure>
        <!-- QUIET-UI-V71-DOC4A-END -->"""
