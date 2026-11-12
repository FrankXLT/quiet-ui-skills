# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v7.1 Deck-1 Interactive Stage and Multi-Slide Visualizations."""


def render_deck1_switcher_and_slides() -> str:
    """Render Deck-1 Band 2 header switcher and 4 slide views."""
    return """<!-- QUIET-UI-V71-DECK1-START -->
            <div class="deck1-band2-canvas">
              <div style="display:flex; justify-content:space-between; align-items:center; font-family:var(--font-mono); font-size:11px; color:var(--text-secondary); margin-bottom:6px; flex-wrap:wrap; gap:6px;">
                <span>SYNTHESIZED KA-BAND BRIEFING STAGE [CONTINUUM]</span>
                <div class="deck1-slide-switcher" style="display:inline-flex;gap:4px;background:var(--bg-card);padding:2px;border:1px solid var(--border-grid);border-radius:var(--radius-pill,16px);">
                  <button type="button" class="va-pill-btn deck1-slide-pill active" onclick="setDeck1Slide(1)" style="padding:2px 8px;font-size:11px;">01 Beam Taper</button>
                  <button type="button" class="va-pill-btn deck1-slide-pill" onclick="setDeck1Slide(2)" style="padding:2px 8px;font-size:11px;">02 Jitter Waterfall</button>
                  <button type="button" class="va-pill-btn deck1-slide-pill" onclick="setDeck1Slide(3)" style="padding:2px 8px;font-size:11px;">03 Wardley Map</button>
                  <button type="button" class="va-pill-btn deck1-slide-pill" onclick="setDeck1Slide(4)" style="padding:2px 8px;font-size:11px;">04 Telemetry Sankey</button>
                </div>
              </div>

              <!-- Slide 1: Interactive Ka-Band Radiation Pattern SVG (Height: 265 for 100dvh Zero-Scroll) -->
              <svg id="deck1-viz-1" width="100%" height="265" viewBox="0 0 760 265" preserveAspectRatio="none" role="img" aria-label="Phased Array Radiation Pattern">
                <line x1="50" y1="15" x2="50" y2="235" stroke="currentColor" stroke-width="1"/>
                <line x1="50" y1="235" x2="730" y2="235" stroke="currentColor" stroke-width="1"/>
                <line id="deck1-sll-line" x1="50" y1="150" x2="730" y2="150" stroke="var(--status-err)" stroke-width="1.2" stroke-dasharray="4,4"/>
                <text x="725" y="144" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="var(--status-err)">SIDELOBE CEILING (-44 dBc)</text>
                <polyline fill="none" stroke="currentColor" stroke-opacity="0.35" stroke-width="1.3" stroke-dasharray="4,3"
                  points="60,195 110,148 160,190 210,132 260,184 310,110 355,176 390,20 425,176 470,110 520,184 570,132 620,190 670,148 720,195"/>
                <polyline id="deck1-beam-poly" fill="none" stroke="var(--accent-focal)" stroke-width="2.1"
                  points="60,224 110,184 160,220 210,172 260,216 310,160 360,208 390,18 420,208 470,160 520,216 570,172 620,220 670,184 720,224"/>
                <text x="44" y="24" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">0 dBc</text>
                <text x="44" y="95" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">-20 dBc</text>
                <text x="44" y="165" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">-40 dBc</text>
                <text x="44" y="232" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="currentColor">-60 dBc</text>
                <text x="60" y="252" font-family="var(--font-mono)" font-size="11" fill="currentColor">-60° Az</text>
                <text x="365" y="252" font-family="var(--font-mono)" font-size="11" fill="currentColor">0° Boresight</text>
                <text x="680" y="252" font-family="var(--font-mono)" font-size="11" fill="currentColor">+60° Az</text>
              </svg>

              <!-- Slide 2: Waterfall Phase-Error Budget Chart -->
              <svg id="deck1-viz-2" width="100%" height="265" viewBox="0 0 760 265" preserveAspectRatio="none" style="display:none;" role="img" aria-label="Waterfall Phase Error Budget">
                <line x1="50" y1="210" x2="730" y2="210" stroke="currentColor" stroke-width="1"/>
                <line x1="50" y1="85" x2="730" y2="85" stroke="var(--status-err)" stroke-width="1.2" stroke-dasharray="4,4"/>
                <text x="725" y="78" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="var(--status-err)">150.0 ps SPEC SLA CEILING</text>
                <!-- Bar 1: Coax Baseline 194.2 ps -->
                <rect x="70" y="48" width="90" height="162" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.4"/>
                <text x="115" y="40" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">194.2 ps</text>
                <text x="115" y="228" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">Coax Baseline</text>
                <line x1="160" y1="48" x2="200" y2="48" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <!-- Bar 2: SMF-28e+ DWDM -74.0 ps -->
                <rect x="200" y="48" width="90" height="62" fill="var(--tint-indigo-bg)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <text x="245" y="40" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">-74.0 ps</text>
                <text x="245" y="228" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">DWDM Optical</text>
                <line x1="290" y1="110" x2="330" y2="110" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <!-- Bar 3: DDMTD Beat -31.6 ps -->
                <rect x="330" y="110" width="90" height="26" fill="var(--tint-indigo-bg)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <text x="375" y="104" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">-31.6 ps</text>
                <text x="375" y="228" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">DDMTD Beat</text>
                <line x1="420" y1="136" x2="460" y2="136" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <!-- Bar 4: Kalman -7.2 ps -->
                <rect x="460" y="136" width="90" height="8" fill="var(--tint-indigo-bg)" stroke="var(--border-strong)" stroke-width="1.3"/>
                <text x="505" y="130" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">-7.2 ps</text>
                <text x="505" y="228" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">Kalman Filter</text>
                <line x1="550" y1="144" x2="590" y2="144" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <!-- Bar 5: Verified Net 81.4 ps -->
                <rect x="590" y="144" width="90" height="66" fill="var(--status-ok-bg)" stroke="var(--status-ok)" stroke-width="1.8"/>
                <text x="635" y="136" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">81.4 ps NET</text>
                <text x="635" y="228" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">SLA PASS</text>
              </svg>

              <!-- Slide 3: Wardley Map (Value-Chain Evolution) -->
              <svg id="deck1-viz-3" width="100%" height="265" viewBox="0 0 760 265" preserveAspectRatio="none" style="display:none;" role="img" aria-label="Wardley Map">
                <line x1="60" y1="20" x2="60" y2="215" stroke="currentColor" stroke-width="1"/>
                <line x1="60" y1="215" x2="730" y2="215" stroke="currentColor" stroke-width="1"/>
                <line x1="225" y1="20" x2="225" y2="215" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <line x1="395" y1="20" x2="395" y2="215" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <line x1="565" y1="20" x2="565" y2="215" stroke="var(--border-grid)" stroke-width="1" stroke-dasharray="3,3"/>
                <text x="142" y="235" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">GENESIS</text>
                <text x="310" y="235" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">CUSTOM</text>
                <text x="480" y="235" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">PRODUCT</text>
                <text x="645" y="235" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">COMMODITY</text>
                <polyline fill="none" stroke="var(--border-strong)" stroke-width="1.3" stroke-dasharray="4,3" points="260,50 360,100 500,125 640,180"/>
                <line x1="360" y1="100" x2="150" y2="140" stroke="var(--border-strong)" stroke-width="1.2" stroke-dasharray="4,3"/>
                <circle cx="260" cy="50" r="5" fill="var(--accent-focal)"/>
                <text x="270" y="54" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Beam Coherency SLA</text>
                <circle cx="150" cy="140" r="5" fill="var(--status-warn)"/>
                <text x="160" y="144" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">Cryo Optical Comb</text>
                <circle cx="360" cy="100" r="5" fill="var(--status-ok)"/>
                <text x="370" y="104" font-family="var(--font-mono)" font-size="11" font-weight="600" fill="var(--text-main)">DDMTD Helper FPGA</text>
                <circle cx="500" cy="125" r="5" fill="var(--accent-focal)"/>
                <text x="510" y="129" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">DWDM SFP+ Optics</text>
                <circle cx="640" cy="180" r="5" fill="var(--text-dim)"/>
                <text x="625" y="196" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">SMF-28e+ Fiber</text>
              </svg>

              <!-- Slide 4: Telemetry Flow Sankey -->
              <svg id="deck1-viz-4" width="100%" height="265" viewBox="0 0 760 265" preserveAspectRatio="none" style="display:none;" role="img" aria-label="Zero-Copy Telemetry Sankey">
                <!-- Stage 1: 8 Sectors -->
                <rect x="50" y="35" width="140" height="170" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
                <text x="120" y="115" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">8x SECTORS</text>
                <text x="120" y="135" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-ok)">142.8 Gbps Net</text>
                <!-- Ribbons Stage 1 -> 2 -->
                <path d="M 190 55 C 240 55, 240 55, 290 55 L 290 120 C 240 120, 240 145, 190 145 Z" fill="var(--tint-indigo-bg)" stroke="var(--border-grid)" stroke-width="1"/>
                <path d="M 190 155 C 240 155, 240 165, 290 165 L 290 200 C 240 200, 240 200, 190 200 Z" fill="var(--tint-amber-bg)" stroke="var(--border-grid)" stroke-width="1"/>
                <!-- Stage 2: Ingestion & Audit -->
                <rect x="290" y="35" width="150" height="95" rx="4" fill="var(--bg-card)" stroke="var(--accent-focal)" stroke-width="1.5"/>
                <text x="365" y="80" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">PCIe BAR0 Ring</text>
                <text x="365" y="98" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--accent-focal)">133.6 Gbps DMA</text>
                <rect x="290" y="145" width="150" height="60" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.5"/>
                <text x="365" y="175" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Kalman Audit</text>
                <text x="365" y="193" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-ok)">9.2 Gbps Filter</text>
                <!-- Ribbons Stage 2 -> 3 -->
                <path d="M 440 50 C 485 50, 485 50, 530 50 L 530 85 C 485 85, 485 90, 440 90 Z" fill="var(--tint-emerald-bg)" stroke="var(--border-grid)" stroke-width="1"/>
                <path d="M 440 95 C 485 95, 485 115, 530 115 L 530 145 C 485 145, 485 125, 440 125 Z" fill="var(--tint-indigo-bg)" stroke="var(--border-grid)" stroke-width="1"/>
                <path d="M 440 160 C 485 160, 485 175, 530 175 L 530 200 C 485 200, 485 195, 440 195 Z" fill="var(--tint-amber-bg)" stroke="var(--border-grid)" stroke-width="1"/>
                <!-- Stage 3: Sinks -->
                <rect x="530" y="35" width="180" height="55" rx="4" fill="var(--bg-card)" stroke="var(--status-ok)" stroke-width="1.4"/>
                <text x="620" y="62" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--status-ok)">TimescaleDB Gorilla</text>
                <text x="620" y="78" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">92.4 Gbps Compressed</text>
                <rect x="530" y="100" width="180" height="48" rx="4" fill="var(--bg-card)" stroke="var(--accent-focal)" stroke-width="1.4"/>
                <text x="620" y="124" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Live HIL Stream</text>
                <text x="620" y="140" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--accent-focal)">41.2 Gbps Waveform</text>
                <rect x="530" y="158" width="180" height="47" rx="4" fill="var(--bg-card)" stroke="var(--border-strong)" stroke-width="1.4"/>
                <text x="620" y="180" text-anchor="middle" font-family="var(--font-mono)" font-size="11" font-weight="700" fill="var(--text-main)">Alert Ledger</text>
                <text x="620" y="196" text-anchor="middle" font-family="var(--font-mono)" font-size="11" fill="var(--status-warn)">9.2 Gbps Tripwire</text>
              </svg>
            </div>
            <!-- QUIET-UI-V71-DECK1-END -->"""
