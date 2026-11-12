# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v7.1 Workspace Figures (App-3 Dumbbell, Heatmap, App-Tree ER)."""


def render_app3_tile4_proof() -> str:
    """Render App-3 Tile 4 dumbbell and trajectory hybrid proof SVG."""
    return """<!-- QUIET-UI-V71-APP3T4-START -->
            <div class="bento-layer3-proof">
              <svg width="100%" height="96" viewBox="0 0 480 96" preserveAspectRatio="none" role="img" aria-label="Sector Throughput Dumbbell Trajectory">
                <line x1="10" y1="84" x2="470" y2="84" stroke="var(--border-grid)" stroke-width="1"/>
                <polyline fill="none" stroke="currentColor" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="3,3" points="40,72 115,68 190,64 265,60 340,55 415,50"/>
                <path d="M 40 58 C 77 53, 77 48, 115 48 C 152 48, 152 38, 190 38 C 227 38, 227 28, 265 28 C 302 28, 302 20, 340 20 C 377 20, 377 12, 415 12" fill="none" stroke="var(--accent-focal)" stroke-width="2"/>
                <!-- Sector 1 -->
                <line x1="40" y1="72" x2="40" y2="58" stroke="var(--border-strong)" stroke-width="1.4"/>
                <circle cx="40" cy="72" r="3" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <circle cx="40" cy="58" r="3.5" fill="var(--accent-focal)"/>
                <text x="40" y="93" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">SEC-1</text>
                <!-- Sector 2 -->
                <line x1="115" y1="68" x2="115" y2="48" stroke="var(--border-strong)" stroke-width="1.4"/>
                <circle cx="115" cy="68" r="3" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <circle cx="115" cy="48" r="3.5" fill="var(--accent-focal)"/>
                <text x="115" y="93" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">SEC-2</text>
                <!-- Sector 3 -->
                <line x1="190" y1="64" x2="190" y2="38" stroke="var(--border-strong)" stroke-width="1.4"/>
                <circle cx="190" cy="64" r="3" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <circle cx="190" cy="38" r="3.5" fill="var(--accent-focal)"/>
                <text x="190" y="93" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">SEC-3</text>
                <!-- Sector 4 -->
                <line x1="265" y1="60" x2="265" y2="28" stroke="var(--border-strong)" stroke-width="1.4"/>
                <circle cx="265" cy="60" r="3" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <circle cx="265" cy="28" r="3.5" fill="var(--accent-focal)"/>
                <text x="265" y="93" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">SEC-4</text>
                <!-- Sector 5 -->
                <line x1="340" y1="55" x2="340" y2="20" stroke="var(--border-strong)" stroke-width="1.4"/>
                <circle cx="340" cy="55" r="3" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <circle cx="340" cy="20" r="3.5" fill="var(--accent-focal)"/>
                <text x="340" y="93" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">SEC-5</text>
                <!-- Sector 6 -->
                <line x1="415" y1="50" x2="415" y2="12" stroke="var(--border-strong)" stroke-width="1.4"/>
                <circle cx="415" cy="50" r="3" fill="var(--bg-canvas)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <circle cx="415" cy="12" r="3.5" fill="var(--accent-focal)"/>
                <text x="415" y="93" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">SEC-6</text>
              </svg>
            </div>
            <!-- QUIET-UI-V71-APP3T4-END -->"""


def render_app3_tile5_proof() -> str:
    """Render App-3 Tile 5 paired heatmap SVG and disposition table."""
    return """<!-- QUIET-UI-V71-APP3T5-START -->
            <div class="bento-layer3-proof">
              <svg width="100%" height="54" viewBox="0 0 280 54" style="margin-bottom:6px;" role="img" aria-label="8-Node Phase Excursion Heatmap">
                <!-- Column Headers -->
                <text x="48" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N1</text>
                <text x="76" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N2</text>
                <text x="104" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N3</text>
                <text x="132" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N4</text>
                <text x="160" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N5</text>
                <text x="188" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-warn)">N6</text>
                <text x="216" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N7</text>
                <text x="244" y="10" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">N8</text>
                <!-- Row Labels -->
                <text x="4" y="24" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">-10m</text>
                <text x="4" y="36" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">-5m</text>
                <text x="4" y="48" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">Live</text>
                <!-- Row 1: -10m -->
                <rect x="36" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="64" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="92" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="120" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="148" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="176" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="204" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="232" y="16" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <!-- Row 2: -5m -->
                <rect x="36" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="64" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="92" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="120" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="148" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="176" y="28" width="24" height="10" rx="2" fill="var(--status-warn-bg)" stroke="var(--status-warn)" stroke-width="1.2"/>
                <rect x="204" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="232" y="28" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <!-- Row 3: Live -->
                <rect x="36" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="64" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="92" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="120" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="148" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="176" y="40" width="24" height="10" rx="2" fill="var(--status-warn-bg)" stroke="var(--status-warn)" stroke-width="1.4"/>
                <rect x="204" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
                <rect x="232" y="40" width="24" height="10" rx="2" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1"/>
              </svg>
              <table class="t5-table" style="font-size:11px;">
                <tbody>
                  <tr>
                    <td><span class="sq-status sq-warn"></span>WR-NODE-06</td>
                    <td>SFP_RX_MARGIN</td>
                    <td class="num" style="color:var(--status-warn);">-13.6 dBm</td>
                  </tr>
                  <tr>
                    <td><span class="sq-status sq-ok"></span>WR-NODE-01</td>
                    <td>PHASE_LOCKED</td>
                    <td class="num">+64.2 ps</td>
                  </tr>
                  <tr>
                    <td><span class="sq-status sq-ok"></span>WR-NODE-04</td>
                    <td>PHASE_LOCKED</td>
                    <td class="num">+29.4 ps</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- QUIET-UI-V71-APP3T5-END -->"""


def render_apptree_er_figure() -> str:
    """Render App-Tree Tab 3 Crow's-Foot schema lineage SVG."""
    return """<!-- QUIET-UI-V71-APPTREE-START -->
            <svg id="va-tree-er-svg" viewBox="0 0 680 176" style="margin-bottom:12px;width:100%;" role="img" aria-label="ER Schema Lineage Diagram">
              <defs>
                <marker id="er-crow-many" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto">
                  <path d="M 0 1 L 10 6 L 0 11 M 5 1 L 5 11" fill="none" stroke="var(--border-strong)" stroke-width="1.2"/>
                </marker>
                <marker id="er-bar-one" viewBox="0 0 12 12" refX="2" refY="6" markerWidth="8" markerHeight="8" orient="auto">
                  <line x1="4" y1="1" x2="4" y2="11" stroke="var(--border-strong)" stroke-width="1.4"/>
                  <line x1="8" y1="1" x2="8" y2="11" stroke="var(--border-strong)" stroke-width="1.4"/>
                </marker>
              </defs>
              <!-- Entity 1: wr_boundary_nodes -->
              <g class="va-er-entity" data-er-entity="wr_nodes" onclick="selectTreeNode('wr_nodes', null)" style="cursor:pointer;">
                <rect class="er-box" x="20" y="24" width="180" height="116" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
                <rect x="20" y="24" width="180" height="24" rx="6" fill="var(--bg-header)"/>
                <text x="110" y="40" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">WR_BOUNDARY_NODES</text>
                <text x="30" y="62" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--accent-focal)">PK id : TEXT</text>
                <text x="30" y="78" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">sector_id : INT</text>
                <text x="30" y="94" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">sfp_wavelength : INT</text>
                <text x="30" y="110" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">optical_status : TEXT</text>
              </g>
              <!-- Entity 2: wr_phase_samples (Active Hypertable) -->
              <g class="va-er-entity is-active" data-er-entity="wr_samples" onclick="selectTreeNode('wr_samples', null)" style="cursor:pointer;">
                <rect class="er-box" x="250" y="24" width="200" height="116" rx="6" fill="var(--bg-card)" stroke="var(--accent-focal)" stroke-width="1.8"/>
                <rect x="250" y="24" width="200" height="24" rx="6" fill="var(--tint-indigo-bg)"/>
                <text x="350" y="40" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--accent-focal)">WR_PHASE_SAMPLES</text>
                <text x="260" y="62" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">PK sample_id : UUID</text>
                <text x="260" y="78" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--accent-focal)">FK node_id : TEXT</text>
                <text x="260" y="94" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">tai_epoch_ns : BIGINT</text>
                <text x="260" y="110" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">phase_skew_ps : NUM</text>
                <text x="260" y="126" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">sfp_ddm : JSONB</text>
              </g>
              <!-- Entity 3: ptp_holdover_events -->
              <g class="va-er-entity" data-er-entity="wr_alarms" onclick="selectTreeNode('wr_alarms', null)" style="cursor:pointer;">
                <rect class="er-box" x="490" y="24" width="170" height="116" rx="6" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
                <rect x="490" y="24" width="170" height="24" rx="6" fill="var(--bg-header)"/>
                <text x="575" y="40" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">PTP_HOLDOVER_EVENTS</text>
                <text x="500" y="62" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">PK event_id : UUID</text>
                <text x="500" y="78" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-warn)">FK node_id : TEXT</text>
                <text x="500" y="94" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">holdover_duration_s</text>
                <text x="500" y="110" font-family="var(--font-mono)" font-size="11" fill="var(--text-dim)">drift_ps_per_min</text>
              </g>
              <!-- Relationship 1: wr_boundary_nodes 1 ---< wr_phase_samples -->
              <line x1="200" y1="82" x2="250" y2="82" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#er-bar-one)" marker-end="url(#er-crow-many)"/>
              <!-- Relationship 2: wr_boundary_nodes 1 ---< ptp_holdover_events via bottom bus -->
              <path d="M 110 140 L 110 156 A 6 6 0 0 0 116 162 L 569 162 A 6 6 0 0 0 575 156 L 575 140" fill="none" stroke="var(--border-strong)" stroke-width="1.5" marker-start="url(#er-bar-one)" marker-end="url(#er-crow-many)"/>
            </svg>
            <!-- QUIET-UI-V71-APPTREE-END -->"""
