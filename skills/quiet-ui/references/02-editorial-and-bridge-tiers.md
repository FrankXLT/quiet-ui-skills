# Reference 02: Editorial Publications, Technical Specifications & Parametric Worksheets (`01. Doc-1` $\rightarrow$ `06. Bridge-1`)

Quiet UI Editorial and Bridge tiers provide calm, authoritative, publication-grade reading environments designed for deep human focus and analytical rigor. They balance contemplative reading rhythm with dense technical artifacts—eliminating generic dashboard noise, unstyled walls of text, and micro-stubs stranded in empty white space.

---

## 1. Editorial Core Principles: Human Tempo, Typographic Voice & Bleed Breakouts

### 1.1 Human Tempo & Cognitive Cadence
- **Contemplative Scholarly Tempo (`01. Doc-1`):** Designed for unhurried, linear comprehension of complex mathematical derivations, telemetry physics, and experimental monographs. Text flows in a comfortable `--measure-prose: 72ch` reading column at `16.5px / 1.7 line-height` with margin annotations that reward sustained attention.
- **Executive Scanning Tempo (`02. Doc-2`):** Built for rapid synthesis by decision-makers. Employs a Bottom Line Up Front (**BLUF**) executive frame, a 4-KPI impact strip, and an asymmetric risk ledger before delving into narrative background.
- **Normative Precision Tempo (`03. Doc-3`):** Structured for deterministic engineering compliance. Features an RFC-standard masthead, bitfield protocol diagrams, and a filterable requirement ledger (`SHALL`, `MUST NOT`, `SHOULD`).
- **Operational Precision Tempo (`04. Doc-4B`, `05. Doc-4A`):** Structured for quick retrieval and live procedural execution with synchronized code snippets, register maps, and sequence lifelines.
- **Interactive Solver Cadence (`06. Bridge-1`):** Blends narrative context with live parametric sliders, real-time recalculation, and coupled verification matrices.

### 1.2 Typographic Voice & Role Separation
Quiet UI strictly differentiates typographic voice across three curated roles:
1. **Scholarly Voice (`--font-serif`):** `Newsreader`, `Georgia`, `Source Serif Pro`, or system serif. Used exclusively for academic monograph body prose (`01. Doc-1`), formal display headings (`H1`), and mathematical abstracts. Conveys timeless institutional authority.
2. **Executive & Operational Voice (`--font-sans`):** `Inter`, system-ui, -apple-system, sans-serif. Used for executive memos (`02. Doc-2`), runbook procedural steps, navigation chrome, section kicker headers (`--ts-xs: 11px`), and interactive buttons.
3. **Machine & Telemetry Voice (`--font-mono`):** `JetBrains Mono`, `ui-monospace`, monospace. Used strictly for machine literals, register bitfields, protocol headers, mathematical equation numbers (`(Eq. 1.1)`), code blocks, and tabular figures. Never blanket entire prose paragraphs in monospace.

### 1.3 The Wide Breakout Pattern (`.va-bleed-wide`)
A major architectural defect in legacy dashboards is trapping high-column data tables and multi-panel figures inside the narrow `72ch` body prose column, causing awkward horizontal scrolling on large displays.
- **Body Prose Anchor:** Body prose remains pinned to `max-width: var(--measure-prose, 72ch)` for optimal reading comfort.
- **Breakout Canvas (`.va-bleed-wide`):** Complex multi-column tables, register maps, and multi-panel figures deliberately break out to `96ch–116ch` (`--stage-editorial-max: 116rem`).
- **CSS Architecture for Breakouts:**
```css
.va-bleed-wide {
  width: 100%;
  max-width: var(--stage-editorial-max, 116rem);
  margin-inline: auto;
  box-sizing: border-box;
}
```
Tables within `.va-bleed-wide` wrap in `.va-figure-scroll` with `role="region"` and `tabindex="0"`. On viewports `< 1280px`, horizontal scroll is allowed; on desktop (`>= 1280px`), columns automatically distribute so `scrollWidth <= clientWidth + 1`.

---

## 2. Tier-by-Tier Component Anatomy & Contracts

### 01. Tier `Doc-1`: Academic & Scientific Monograph (`0%` Box Weight, Default `white`, `N1`)
- **Three-Column Grid:** `max-width: var(--stage-editorial-max, 116rem); margin: 0 auto; display: grid; grid-template-columns: 200px minmax(0, 72ch) 240px; gap: 2.75rem;`
- **Left Rail (Outline TOC):** Sticky outline table of contents with `--font-sans` `13px` links (`.va-side-link`) and a `.va-hamburger-btn` (`toggleLeftRailCollapse()`) collapsing the rail to a `60px` icon mode.
- **Center Column (Narrative Monograph):**
  - **Kicker & Axis Alignment:** Section kicker (`--font-sans`, `--ts-xs: 11px`, letter-spacing `0.08em`), display H1 (`--font-serif`, `--ts-display: clamp(24px, 2.5vw, 28px)`), and body paragraphs (`--font-serif`, `16.5px`, line-height `1.7`) share the exact same left X-coordinate (`|kicker.left - h1.left| <= 2px`).
  - **Numbered Sections:** 5 deep sections (`1.0 Executive Summary`, `2.0 Deep Space Optical Transceiver Architecture`, `3.0 Allan Deviation & Modulation Stability`, `4.0 Link Budget Formulations`, `5.0 Experimental Flight Validation`).
  - **Display Equations:** Three numbered display equations with horizontal framing rules and right-aligned equation numbers:
    $$\sigma_y^2(\tau) = \frac{1}{2(M-1)} \sum_{k=1}^{M-1} (\bar{y}_{k+1} - \bar{y}_k)^2 \quad \text{(Eq. 1.1)}$$
  - **Booktabs Tables:** Click-to-sort `table.booktabs` (`2px` top/bottom rules, `1px` header rule, zero vertical gridlines).
  - **Multi-Layer SVG Figures:** Two multi-layer SVG figures: (1) exploded 3-plane optical stack with SMF-28e fiber base, DDMTD beat detector, and PCIe BAR0 TAI ring, and (2) Allan deviation $\sigma_y(\tau)$ curve with shaded stability corridor.
- **Right Column (Margin Citations & Sidenotes):**
  - Tufte-style `.sidenote-box` entries (`border-left: 1px solid var(--border-grid); padding-left: 0.75rem; font-size: var(--ts-sm); font-family: var(--font-sans);`) aligned vertically with corresponding superscript citations (`[1]`..`[8]`). Hovering a citation highlights the corresponding sidenote.

### 02. Tier `Doc-2`: Executive Decision Memo (`15%` Box Weight, Default `white`, `N0`)
- **Container & Typography:** `max-width: 860px; margin: 0 auto; padding: 2rem 2rem 4rem;` with `--font-sans` display H1 (`--ts-xl`) and `--ts-prose: 15.5px` body copy.
- **5 Mandatory Core Elements:**
  1. **Top BLUF Decision Ledger (`.bluf-frame`):** 4-column hairline metadata strip (`DATE`, `AUTHORITY: KDP-C`, `RECOMMENDATION: OPTION B`, `COST DELTA: -$4.2M`) over a shaded Bottom Line Up Front synthesis paragraph.
  2. **Mid-Page 4-Cell Hairline Metric Strip (`.kpi-4strip`):** 4-column strip (`border-block: 1px solid var(--border-strong)`) displaying critical trade metrics (Throughput Gain `+340%`, Downlink Availability `99.4%`, Phase Jitter `< 85 ps`, Life-Cycle Cost `$18.2M`).
  3. **Architecture Delta SVG (`.va-mermaid-figure`):** Inline vector diagram showing legacy RF baseline vs. proposed hybrid optical/RF architecture with a `[Diagram | Mermaid Source]` toggle.
  4. **Asymmetric Left-Rule Risk Matrix (`.risk-left-bar`):** High-visibility callout (`border-left: 3px solid var(--status-err); background: var(--bg-card); padding: 0.85rem 1.25rem;`) detailing schedule risk, atmospheric attenuation mitigations, and fallback downlink protocols.
  5. **Full-Width 4-Option Trade Study Table:** A comprehensive comparison matrix across Option A (Heritage Ka-Band), Option B (Hybrid DSOC), Option C (Arrayed 4x Optical), and Option D (Commercial Relay).

### 03. Tier `Doc-3`: Normative RFC Specification (`25%` Box Weight, Default `white`, `N0`)
- **Container & Typography:** `max-width: 920px; margin: 0 auto;` with normative `--font-sans` titles, standard RFC header block, and `--font-mono` specification tables.
- **6 Mandatory Components:**
  1. **CCSDS Specification Masthead:** Official document header block (`Standard: CCSDS 133.0-B-2`, `Status: PROPOSED STANDARD`, `Distribution: UNLIMITED`, `Working Group: SLS-RFM`).
  2. **6-Byte Bitfield Header Diagram:** Inline SVG schematic illustrating the primary Space Packet header (Version Number [3b], Packet Type [1b], Secondary Header Flag [1b], APID [11b], Sequence Flags [2b], Sequence Count [14b], Packet Data Length [16b]).
  3. **Filterable 12-Clause Normative Ledger:** Interactive filter bar (`ALL`, `SHALL`, `MUST NOT`, `SHOULD`) filtering 12+ standard conformance clauses with bordered `.req-badge` tags.
  4. **FOP-1 Protocol State Machine SVG:** Visual finite state machine diagram detailing states `IDLE_UNLOCKED`, `CARRIER_ACQUISITION`, `FRAME_SYNC_LOCKED`, `DATA_TRANSFER`, and `HOLDOVER_FAULT`.
  5. **Character-Grid ASCII State Table:** Bordered `<pre>` table specifying transition triggers, guards, and timeout limits.
  6. **Configuration Schema Diff:** Unified diff block (`-` removal in crimson, `+` addition in emerald) verifying backwards compatibility.

### 04. Tier `Doc-4B`: Encyclopedic SDK, CLI & Skill Reference (`25%` Box Weight, Default `white`, `N3`)
- **Layout:** 2-column shell (`display: grid; grid-template-columns: 250px minmax(0, 1fr); width: 100%;`) with `N3` top command bar and 2-level numbered sidebar (`1.0`, `1.1 /lock_carrier`, `2.0`).
- **Core Elements:**
  1. **6-Stage Numbered Flow Spine (`.va-flow-spine`):** Horizontal pipeline (`01 Discover` $\rightarrow$ `02 Configure` $\rightarrow$ `03 Calibrate` $\rightarrow$ `04 Syntonize` $\rightarrow$ `05 Acquire` $\rightarrow$ `06 Verify`) with clickable `/command` pills (`11px` floor).
  2. **Situation-to-Tier Decision Table:** Router table linking operational failure modes to corrective procedures.
  3. **32-Bit FPGA Register Map:** Bitfield table detailing register offsets, access modes (`RO`, `RW`, `R/W1C`), reset values, and bit masks.
  4. **Multi-Method SDK Reference:** Nested definition lists (`<dl>/<dt class="sig-band">/<dd class="sig-body">`) with signature pills, parameter tables, and interactive doctest blocks with copy buttons.

### 05. Tier `Doc-4A`: Split-Pane Operational Runbook (`45%` Box Weight, Default `white`, `N1`)
- **Three-Pane Split:** `display: grid; grid-template-columns: 220px minmax(0, 1fr) 430px; width: 100%;`
- **Left Rail (Step Navigator):** Sticky procedural step tree (`1.0 Pre-Pass Safing`, `2.0 Ground Station Handshake`, `3.0 Laser Beam Divergence`, `4.0 High-Rate Downlink`, `5.0 Post-Pass Telemetry Dump`, `6.0 Safing`).
- **Center Column (Procedure Engine):**
  - **Interlock Safety Banner:** High-visibility procedural warning with required authorization role (`FLIGHT DIRECTOR / MISSION LEAD`).
  - **Sequence Lifeline SVG:** 4-lifeline sequence diagram (`Operator CLI` $\rightarrow$ `DSOC Ground Asset` $\rightarrow$ `Flight Transceiver` $\rightarrow$ `Science Archive`).
  - **6 Sequenced Steps:** Each step contains clear prerequisites, commands, expected responses, and safety rollbacks. Clicking any step highlights it and synchronizes the right console.
- **Right Column (Sticky Multimodal Console):** Pinned dark terminal console with tabbed language switchers (`CLI`, `Python`, `YAML`, `FPGA-CSR`) and one-click copy affordance.

### 06. Tier `Bridge-1`: Parametric Engineering Worksheet (`50%` Box Weight, Default `white`, `N0`)
- **Header & Mathematical Formulation:** Title `Parametric Engineering Worksheet` with mathematical formulas for link margin:
  $$M = P_t + G_t + G_r - L_{free} - L_{atm} - L_{point} - P_{req} \quad \text{[dB]}$$
- **Solver Frame (`.b1-solver-frame`):** Split card featuring:
  - Left: 4 grouped link-budget parameter sliders (`Transmit Laser Power [W]`, `Flight Aperture [cm]`, `Range Distance [AU]`, `Ground Detector Efficiency [%]`).
  - Right: Real-time 2-curve SVG sensitivity plot showing received power vs. required threshold across interplanetary distances (0.1 to 2.8 AU).
- **Coupled Multi-Mission Verification Ledger:** Full-width bottom table evaluating link margin across 8 planetary mission profiles (`DSOC Psyche Cruise`, `Mars 2026 Opposition`, `Europa Clipper Relay`, `Titan Dragonfly En Route`, `Deep Space Lunar Gateway`, `JWST L2 Halo`, `Lagrange Sun-Earth L1`, `Asteroid Sample Return`). Moving any slider dynamically updates calculated margins and `PASS`/`MARGINAL` badges in the ledger.

---

## 3. Implementation Code Patterns & Token Bindings

### 3.1 Academic Monograph Grid & Kicker Alignment (Doc-1)
```css
.doc1-stage {
  max-width: var(--stage-editorial-max, 116rem);
  margin-inline: auto;
  padding: 2.5rem 2rem 6rem;
  display: grid;
  grid-template-columns: 200px minmax(0, var(--measure-prose, 72ch)) 240px;
  gap: 2.75rem;
  box-sizing: border-box;
}

.doc1-kicker {
  font-family: var(--font-sans);
  font-size: var(--ts-xs, 11px);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.doc1-title {
  font-family: var(--font-serif);
  font-size: var(--ts-display, clamp(24px, 2.5vw, 28px));
  font-weight: 400;
  line-height: 1.25;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
}

.doc1-prose p {
  font-family: var(--font-serif);
  font-size: 16.5px;
  line-height: 1.7;
  color: var(--text-primary);
  margin-bottom: 1.25rem;
}
```

### 3.2 Executive BLUF Box & Metric Strip (Doc-2)
```html
<section class="bluf-frame" aria-label="Executive Bottom Line Up Front">
  <div class="bluf-meta-grid">
    <div class="bluf-meta-cell"><span class="lbl">DATE</span><strong>2026-11-14</strong></div>
    <div class="bluf-meta-cell"><span class="lbl">GATE</span><strong>KDP-C Baseline</strong></div>
    <div class="bluf-meta-cell"><span class="lbl">DECISION</span><strong>Hybrid Optical/RF</strong></div>
    <div class="bluf-meta-cell"><span class="lbl">SAVINGS</span><strong>-$4.2M Delta</strong></div>
  </div>
  <p class="bluf-summary">
    <strong>BLUF:</strong> The project review board baseline confirms transition of deep-space optical terminal to primary science downlink with Ka-band fallback, yielding a 340% throughput increase at zero mass penalty.
  </p>
</section>

<div class="kpi-4strip" role="region" aria-label="Key Decision Metrics">
  <div class="kpi-cell"><span class="kpi-label">Throughput Gain</span><strong class="kpi-val">+340%</strong><span class="kpi-sub">vs Ka-band baseline</span></div>
  <div class="kpi-cell"><span class="kpi-label">Availability</span><strong class="kpi-val">99.4%</strong><span class="kpi-sub">triple-site DSN hybrid</span></div>
  <div class="kpi-cell"><span class="kpi-label">Phase Jitter</span><strong class="kpi-val">&lt; 85 ps</strong><span class="kpi-sub">Allan dev at 1000s</span></div>
  <div class="kpi-cell"><span class="kpi-label">Lifecycle Cost</span><strong class="kpi-val">$18.2M</strong><span class="kpi-sub">within Phase C budget</span></div>
</div>
```

### 3.3 CCSDS Specification Bitfield & Clause Filter (Doc-3)
```html
<div class="rfc-masthead">
  <div class="rfc-title-row">
    <span class="rfc-badge">PROPOSED STANDARD</span>
    <span class="rfc-id">CCSDS 133.0-B-2</span>
  </div>
  <h1 class="rfc-heading">Space Packet Protocol Specification</h1>
</div>

<div class="rfc-filter-bar">
  <button class="va-pill-btn is-active" data-filter="ALL">ALL (14)</button>
  <button class="va-pill-btn" data-filter="SHALL">SHALL (8)</button>
  <button class="va-pill-btn" data-filter="MUST-NOT">MUST NOT (3)</button>
  <button class="va-pill-btn" data-filter="SHOULD">SHOULD (3)</button>
</div>
```

### 3.4 Parametric Link Budget Solver Layout (Bridge-1)
```css
.b1-solver-frame {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1.5rem;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-card, 8px);
  background: var(--bg-surface);
  padding: 1.5rem;
}

@container (max-width: 720px) {
  .b1-solver-frame {
    grid-template-columns: 1fr;
  }
}
```

---

## 4. Verification & Audit Checklist for Editorial Tiers
- [ ] Left rail collapse operates cleanly between `200px` and `60px` with zero text truncation.
- [ ] Body prose strictly adheres to `--measure-prose: 72ch` while figures/tables break out cleanly to `--stage-editorial-max: 116rem`.
- [ ] Typographic axis test passes: `|kicker.left - h1.left| <= 2px` on Doc-1.
- [ ] Booktabs tables enforce `2px` top/bottom rules, `1px` header rule, zero vertical lines, and full keyboard accessibility (`tabindex="0" role="region"`).
- [ ] All SVG diagrams provide responsive viewports with zero text clipping and zero line-through-text collisions.
