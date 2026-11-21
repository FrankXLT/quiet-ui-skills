# Quiet UI — Medium M1: Paper & Print

Medium M1 governs physical paper documentation, technical whitepapers, calibration certificates, and formal hardware acceptance test reports. Printed media operates under fundamentally different optical, tactile, and physical physics than emissive digital screens.

---

## 1. Physical Optics & Viewing Geometry

```
+-------------------------------------------------------------+
|                      M1 OPTICAL PROFILE                     |
|                                                             |
|  Viewing Distance:  30 – 40 cm (Desk / Clipboard reading)   |
|  Physical Spatial:  300 – 600 DPI (Micro-line resolution)   |
|  Illumination:      Reflective ambient light (Zero emissive)|
|  Form Factor:       Letter Portrait (215.9mm x 279.4mm)     |
|                     or A4 Portrait (210mm x 297mm)          |
|  Dynamic Range:     Subtractive CMYK Ink on Paper (~50:1)   |
+-------------------------------------------------------------+
```

### Optical Constraints vs. Emissive Screens

| Parameter | Digital Emissive Screen (M2/M3) | Printed Paper Sheet (M1) |
| :--- | :--- | :--- |
| **Photon Source** | Backlit LED / OLED emitting photons | Incident ambient light reflected off cellulose fibers |
| **Spatial Resolution** | 96 – 220 PPI (Sub-pixel rendering) | 300 – 1200 DPI (Continuous tone halftones) |
| **Color Space** | Additive sRGB / Display P3 | Subtractive CMYK / Spot Ink |
| **Interaction Model** | Dynamic hover, click, scroll, pan | Static unrolled pagination, margin notes, physical archival |
| **Contrast Ratio** | 1,000:1 to 1,000,000:1 (Infinite black) | 30:1 to 60:1 (Paper reflectance limits dark ink) |

---

## 2. Layout, Margins & Pagination Geometry

Printed documents must adhere strictly to physical page boundaries, avoiding orphaned table headers and fractured data figures:

```css
@page {
  size: letter portrait;
  margin: 15mm 15mm 20mm 15mm;
  @bottom-right {
    content: "Page " counter(page) " of " counter(pages);
    font-family: var(--font-sans);
    font-size: 8pt;
    color: #475569;
  }
}
```

### Pagination Protection Rules
1. **Zero Figure Fracture**: Data charts, pinout schematics, and waveform oscillograms must declare `break-inside: avoid` (and legacy `page-break-inside: avoid`).
2. **Orphan & Widow Control**: Paragraph text must maintain minimum 3 lines before and after page breaks (`orphans: 3; widows: 3;`).
3. **Repeated Table Headers**: Multi-page tables must repeat `<thead>` rows on every printed continuation page.

---

## 3. Grayscale Survival & 1-2-5 Interpolation Grids

Monochrome laser printers and photocopy degradation can completely erase subtle color differentiations:

> **The Grayscale Survival Invariant**: Every line series, chart plot, and state classification must remain 100% distinguishable when rendered in pure black-and-white photocopy reproduction. Color alone must never convey state.

### Multi-Trace Distinction Tactics
- **Line 1 (Baseline)**: Solid stroke (`stroke-dasharray: none; stroke-width: 1.5pt`).
- **Line 2 (Tolerance Upper)**: Dashed stroke (`stroke-dasharray: 4, 3; stroke-width: 1.2pt`).
- **Line 3 (Tolerance Lower)**: Dotted stroke (`stroke-dasharray: 1, 2; stroke-width: 1.2pt`).
- **Line 4 (Measured Actual)**: Solid heavy stroke with filled circle markers (`stroke-width: 2.0pt`).

### Fine 1-2-5 Interpolation Grids
Chart axes must use calibrated engineering divisions (1, 2, 5, 10, 20, 50, 100) rendered with 0.25pt hairline grids (`#E2E8F0` or 10% black ink) rather than heavy borders, ensuring pencil annotations remain legible.

---

## 4. Concrete CSS Architecture for Print

```css
@layer quiet.tokens, quiet.base, quiet.print;

@media print {
  @layer quiet.print {
    :root {
      --bg-canvas: #FFFFFF;
      --bg-surface: #FFFFFF;
      --bg-card: #FFFFFF;
      --text-primary: #000000;
      --text-secondary: #333333;
      --border-hairline: #CCCCCC;
      --border-strong: #000000;
      font-size: 10pt;
    }

    body {
      background: #FFFFFF;
      color: #000000;
      margin: 0;
      padding: 0;
      text-rendering: geometricPrecision;
    }

    /* Strip digital UI controls */
    nav,
    aside,
    button,
    .va-theme-toggle,
    .va-nav-dock,
    .va-nav-rail {
      display: none;
    }

    /* Prevent awkward card splits */
    .va-card,
    .va-figure,
    .va-test-condition-block,
    tr {
      break-inside: avoid;
      page-break-inside: avoid;
    }

    /* Unroll interactive elements into plain text */
    a[href]::after {
      content: " (" attr(href) ")";
      font-size: 8pt;
      color: #555555;
    }

    /* Test Condition Identification Block */
    .va-test-condition-block {
      border: 1pt solid #000000;
      padding: 8pt;
      margin-block: 12pt;
      font-size: 9pt;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6pt;
    }
  }
}
```

---

## 5. HTML Macro Implementation

```html
<section class="va-test-report">
  <header class="va-report-header">
    <span class="va-kicker">ACCEPTANCE TEST PROCEDURE #ATP-8802</span>
    <h1 class="va-editorial-h1">Cryogenic Valve Sealing Characterization</h1>
  </header>

  <!-- Inline Test-Condition Block -->
  <div class="va-test-condition-block">
    <div><strong>Ambient Temp:</strong> 294.2 K</div>
    <div><strong>Chamber Press:</strong> 101.3 kPa</div>
    <div><strong>Sensor S/N:</strong> PT-9941</div>
    <div><strong>Cert Date:</strong> 2026-11-17</div>
  </div>

  <!-- Unrolled Monograph Figure -->
  <figure class="va-figure va-card">
    <div class="va-chart-container">
      <svg class="va-plot" viewBox="0 0 500 250">
        <!-- Calibrated 1-2-5 engineering grid -->
        <line x1="50" y1="200" x2="480" y2="200" stroke="#CCCCCC" stroke-width="0.5" />
        <!-- Data line with explicit dash pattern for photocopy survival -->
        <path d="M 50 180 Q 250 80 480 30" fill="none" stroke="#000000" stroke-width="1.5" stroke-dasharray="6,4" />
      </svg>
    </div>
    <figcaption class="va-prose">
      <strong>Figure 1.2:</strong> Helium leak rate under 50 bar differential pressure. Dashed line denotes certified ceiling.
    </figcaption>
  </figure>
</section>
```

---

## 6. Anti-Patterns & Operational Violations

| Violation | Physical Real-World Consequence | Architectural Solution |
| :--- | :--- | :--- |
| Dark background cards printed on paper | Drenches page in ink; causes paper curl, smudging, and unreadable text. | Force `--bg-canvas: #FFFFFF` and `--text-primary: #000000` under `@media print`. |
| Figures split across page boundaries | Chart title on page 1, plot data on page 2; destroys readability. | Apply `break-inside: avoid` on all `.va-card` and `.va-figure` containers. |
| Relying solely on red vs. green lines | Photocopy turns both lines into identical black strokes; renders test invalid. | Use distinct dash arrays (`4,3` vs `solid`) and geometric markers (circle, square). |
| Hyperlinks printed as blue text without URL | Reader holding paper sheet cannot determine target reference URL. | Inject target URL using CSS `a[href]::after { content: " (" attr(href) ")"; }`. |
| Fine text below 8pt printed on paper | Legibility destroyed by ink bleeding into fiber matrix. | Enforce minimum printed font floor of `8pt` for metadata and `10pt` for body. |
