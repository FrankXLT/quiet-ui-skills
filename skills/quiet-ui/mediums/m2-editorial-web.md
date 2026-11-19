# Quiet UI — Medium M2: Editorial Web & Monograph Publishing

Medium M2 governs long-form technical monographs, architectural decision records (ADRs), system design specifications, and whitepaper research briefs viewed on modern high-resolution computer monitors. It bridges rigorous typography with modern responsive web capabilities.

---

## 1. Physical Optics & Viewing Geometry

```
+-------------------------------------------------------------+
|                      M2 OPTICAL PROFILE                     |
|                                                             |
|  Viewing Distance:  50 – 70 cm (Ergonomic desktop workstation)|
|  Display Hardware:  1080p, 1440p, 4K Monitors (24" – 32")   |
|  Pixel Density:     110 – 163 PPI (Standard & Retina Scale)  |
|  Illumination:      Direct Emissive Backlit Display          |
|  Cognitive Mode:    Sustained deep reading & analytical focus|
|  Primary Shell:     N0 (Undecorated Stage) or N2 (Subtle Top)|
+-------------------------------------------------------------+
```

### Optical Constraints & Display Parameters

| Parameter | Specifications | Rationale |
| :--- | :--- | :--- |
| **Root Font Scaling** | `clamp(16px, calc(12.4px + 0.25vw), 22px)` | Automatically expands text for comfortable viewing at 60cm distance. |
| **Monograph Prose Measure** | `max-inline-size: 72ch` | Prevents eye fatigue by maintaining 65–75 characters per line. |
| **Breakout Canvas Ceiling** | `max-inline-size: 116ch` (`.va-bleed-wide`) | Expands multi-pane charts and architecture diagrams beyond prose bounds. |
| **Vertical Rhythm** | `line-height: 1.65` for prose, `1.2` for headings | Generates open, breathable reading cadence on emissive displays. |
| **Surface Contrast** | `[data-theme="paper"]` or `[data-theme="white"]` | Warm paper lowers glare during multi-hour technical review sessions. |

---

## 2. Layout Architecture: Centered Monograph & Floating TOC

The M2 layout employs a 3-zone spatial model:
1. **Left Margin**: Floating or sticky table of contents (TOC) highlighting active reading position.
2. **Center Column**: Dedicated 72ch typographic column hosting prose, mathematical formulas, and inline citations.
3. **Breakout Stage**: Fluid breakouts (`.va-bleed-wide`) allowing complex comparative figures to span up to 116ch without unseating the reader.

```
+---------------------------------------------------------------------------------+
|  M2 Editorial Canvas (Max 116ch)                                                |
|                                                                                 |
|  +--------+   +---------------------------------------+   +------------------+  |
|  | Sticky |   | Centered Monograph Column (Max 72ch)  |   | Marginalia       |  |
|  | TOC    |   |                                       |   | Footnotes &      |  |
|  |        |   | Prose paragraph with Newsreader serif |   | Sidenotes        |  |
|  | Sec 1  |   | title and crisp sans body text.       |   | [^1] Citation    |  |
|  | Sec 2  |   |                                       |   |                  |  |
|  |        |   +---------------------------------------+   +------------------+  |
|  |        |   |                                                              |  |
|  |        |   | .va-bleed-wide Breakout Figure (108ch)                       |  |
|  |        |   | [ 3-Pane Logic Analyzer & System Telemetry Comparison Plot ] |  |
|  |        |   |                                                              |  |
|  +--------+   +--------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
```

---

## 3. Typographic Hierarchy & Footnote Mechanics

M2 articles prioritize editorial elegance while preserving scientific rigor:
- **Title (`.va-editorial-h1`)**: Rendered in `--font-serif` (Newsreader / Charter) with balanced text wrapping (`text-wrap: balance`).
- **Body (`.va-prose`)**: Rendered in `--font-sans` (Inter) for maximum screen legibility at `var(--ts-prose)`.
- **Marginalia & Footnotes**: Positioned in right gutter on wide screens ($\ge 1440\text{px}$) and folded into numbered footnotes at the document base on narrow screens.

---

## 4. Concrete CSS Architecture

```css
@layer quiet.mediums, quiet.layout;

@layer quiet.mediums {
  /* M2 Monograph Stage Container */
  .va-m2-stage {
    display: grid;
    grid-template-columns: 1fr min(72ch, 100%) 1fr;
    column-gap: 2rem;
    padding-inline: 1.5rem;
    padding-block: 3rem;
    background-color: var(--bg-canvas);
    color: var(--text-primary);
  }

  /* Center Column Mapping */
  .va-m2-stage > * {
    grid-column: 2;
  }

  /* Breakout Figure Canvas */
  .va-m2-stage > .va-bleed-wide {
    grid-column: 1 / -1;
    inline-size: 100%;
    max-inline-size: min(116ch, 100%);
    margin-inline: auto;
    margin-block: 2.5rem;
  }

  /* Floating Sticky Table of Contents */
  .va-m2-toc {
    position: sticky;
    inset-block-start: 2rem;
    max-block-size: calc(100vh - 4rem);
    overflow-y: auto;
    font-size: var(--ts-xs);
    color: var(--text-muted);
    border-inline-end: 1px solid var(--border-hairline);
    padding-inline-end: 1rem;
  }

  .va-m2-toc a {
    display: block;
    padding-block: 0.35rem;
    color: inherit;
    text-decoration: none;
    transition: color 0.15s ease;
  }

  .va-m2-toc a.is-active {
    color: var(--accent-focal);
    font-weight: 600;
  }
}
```

---

## 5. HTML Macro Implementation

```html
<article class="va-m2-stage" data-theme="paper">
  <!-- Eyebrow & Monograph Header -->
  <header>
    <span class="va-kicker">ENGINEERING MEMORANDUM #EM-2026-09</span>
    <h1 class="va-editorial-h1">Non-Blocking Memory Bus Arbiters for High-Reliability RTOS Nodes</h1>
    <p class="va-lead-abstract">
      A comparative timing analysis of round-robin versus weighted-fair queued bus arbiters under sustained 40 Gbps burst stress.
    </p>
  </header>

  <!-- Centered Prose Body -->
  <div class="va-prose">
    <p>
      Deterministic latency guarantees require hardware bus controllers to arbitrate multi-master requests without introducing priority inversion. Current silicon implementations rely on speculative grants...
    </p>
  </div>

  <!-- Bleed-Wide Multi-Pane Breakout Figure -->
  <figure class="va-bleed-wide va-card">
    <div class="va-figure-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
      <div class="va-plot-pane">
        <span class="va-kicker">TRACE A: ROUND-ROBIN JITTER</span>
        <!-- Calibrated SVG Plot -->
      </div>
      <div class="va-plot-pane">
        <span class="va-kicker">TRACE B: WEIGHTED-FAIR QUEUED</span>
        <!-- Calibrated SVG Plot -->
      </div>
    </div>
    <figcaption class="va-caption">
      <strong>Figure 4:</strong> Latency distribution under 100,000 synthetic transaction cycles.
    </figcaption>
  </figure>

  <!-- Continuation Prose -->
  <div class="va-prose">
    <p>
      As demonstrated in Figure 4, tail latencies for the weighted-fair implementation plateau at 14.2 ns, representing a 3.4x improvement over naive arbitration loops.
    </p>
  </div>
</article>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | Cognitive Disruption | Quiet UI Fix |
| :--- | :--- | :--- |
| Prose spanning 100% of widescreen monitor | Reader cannot track lines over 160ch; leads to severe eye fatigue. | Constrain prose container to `max-inline-size: 72ch`. |
| Complex diagrams jammed into narrow 72ch column | Microscopic labels, clipped axes, illegible legends. | Use `.va-bleed-wide` breakout class spanning up to 116ch. |
| Incompatible serif font in dense data tables | Poor numeral alignment and illegible tiny superscript text. | Use `--font-sans` and `--font-nums` with `font-variant-numeric: tabular-nums`. |
| Sticky header consuming 120px on desktop | Letterboxes vertical reading area; degrades immersive monograph focus. | Use shell `N0` (undecorated) or lightweight auto-hiding `N2`. |
| Broken footnote anchor links | Reader disoriented when jumping back from citations. | Implement CSS scroll-margin-top on footnote target anchors. |
