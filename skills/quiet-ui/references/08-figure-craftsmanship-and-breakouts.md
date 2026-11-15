# Reference 08: Figure Craftsmanship, Vector Halos & Responsive Breakouts

Quiet UI publication figures and technical schematics bridge high-fidelity vector graphics with responsive document layouts. This reference establishes the mandatory engineering standards for multi-layer SVGs, zero line-through-text collisions, shaded stability corridors, and `@container` responsive breakouts.

---

## 1. Multi-Layer Publication SVG Architecture

Technical figures in Quiet UI are composed as calibrated 4-layer vector stacks that ensure clear visual separation between background reference frames, data curves, and annotations:

### Layer 1: Reference Corridors & Shaded Regions
- **Nominal Operational Corridors:** Use semantic tint backgrounds (`var(--tint-emerald-bg)`, `var(--tint-indigo-bg)`) at `0.25–0.40` opacity to denote nominal tolerance bands, stability envelopes, or allowable jitter corridors.
- **Abort / Fault Regions:** Use muted warning fills (`var(--tint-amber-bg)`, `var(--tint-rose-bg)`) to demarcate danger thresholds or link-margin deficits.

### Layer 2: Metric Axes, Gridlines & Explicit Unit Labels
- **Gridline Styling:** Hairline rules (`stroke: var(--border-grid); stroke-width: 1px; stroke-dasharray: 4, 4;`).
- **Explicit Axis Units:** Every numerical axis must state its exact engineering unit (`[dB]`, `[AU]`, `[ps]`, `[K]`, `[MHz]`) in monospace (`--font-mono`, `--ts-xs: 11px`). Naked, unlabeled numbers are strictly prohibited.

### Layer 3: Physical Data Traces & Exploded Mechanical Planes
- **Data Curves:** Clean hairline vector paths (`stroke-width: 1.5px` to `2.0px`) bound to theme accents (`var(--accent-focal)`, `var(--text-primary)`).
- **Physical Storytelling:** Isometric or 2.5D planar projections (such as the exploded 3-plane optical syntonization stack in `01. Doc-1`) illustrate mechanical layer stacks:
  - Base Plane: Physical fiber/medium layer.
  - Middle Plane: Hardware detector / mixer logic.
  - Top Plane: PCIe bus / MMIO registers.

### Layer 4: Text Annotations, Halos & Leader Callouts
- **Text Labels:** Primary labels use `--font-sans` or `--font-serif` at weight 600; numerical markers use `--font-mono`.
- **Zero Line-Through-Text Invariant:** Visual traces, gridlines, or connector paths must NEVER slice through text glyphs.

---

## 2. Preventing Line-Through-Text Collisions: SVG Halos & Leaders

When data curves cross near text labels, collisions destroy legibility. Quiet UI employs two non-negotiable remediation strategies:

### 2.1 CSS `paint-order` Text Halos
For inline SVG text elements situated over traces, apply an opaque background stroke halo matching the canvas background:
```css
.va-svg-halo-text {
  font-family: var(--font-sans);
  font-size: var(--ts-xs, 11px);
  fill: var(--text-primary);
  paint-order: stroke fill;
  stroke: var(--bg-canvas);
  stroke-width: 4px;
  stroke-linejoin: round;
  stroke-linecap: round;
}
```
This automatically carves an unclipped 4px protective clearance mask around every letter without requiring complex SVG `<clipPath>` definitions.

### 2.2 Leader Callout Lines
When annotations point to specific curve points, anchor callout text outside the dense data area using an orthogonal leader line:
```html
<g class="va-svg-leader-callout">
  <!-- Curve Target Point -->
  <circle cx="495" cy="124" r="3" fill="var(--accent-focal)"/>
  <!-- Leader Line with 8px clearance -->
  <polyline points="495,124 530,95 590,95" fill="none" stroke="var(--text-secondary)" stroke-width="1"/>
  <!-- Callout Text positioned at leader terminus -->
  <text x="595" y="99" font-family="var(--font-mono)" font-size="11" fill="var(--text-primary)">
    DWDM Locked 0.81 ps
  </text>
</g>
```

---

## 3. Container-Query Responsive Stacking (`@container`)

Multi-panel technical figures (such as combined schematic + analytical plot cards) must maintain legibility across both mobile screens (`390px`) and widescreen displays (`1920px+`):

### 3.1 The 2-Card Figure Container Split
Wrap multi-panel figures in a container-aware parent:
```css
.va-figure-container {
  container-type: inline-size;
  width: 100%;
}

.va-figure-split-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@container (min-width: 680px) {
  .va-figure-split-grid {
    grid-template-columns: 1.15fr 1fr;
  }
}
```
- **Narrow Containers (`< 680px`):** The two panels stack vertically (`1fr`), allowing each SVG diagram to use full available width without text compression.
- **Wide Containers (`>= 680px`):** Panels sit side-by-side (`1.15fr 1fr`), pairing schematic context on the left with analytical proof plots on the right.

---

## 4. Implementation Code Patterns

### 4.1 Multi-Layer Allan Deviation Curve with Halo Text
```html
<svg width="100%" height="220" viewBox="0 0 660 220" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Allan Deviation Curve">
  <!-- Layer 1: Nominal Stability Corridor -->
  <rect x="365" y="80" width="275" height="45" fill="var(--tint-emerald-bg)" opacity="0.35"/>
  
  <!-- Layer 2: Reference Gridlines & Units -->
  <line x1="365" y1="36" x2="365" y2="175" stroke="var(--border-strong)" stroke-width="1"/>
  <line x1="365" y1="175" x2="640" y2="175" stroke="var(--border-strong)" stroke-width="1"/>
  <text x="360" y="42" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">1e-12</text>
  <text x="360" y="175" text-anchor="end" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">1e-15</text>
  <text x="375" y="195" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">τ=1s</text>
  <text x="560" y="195" font-family="var(--font-mono)" font-size="11" fill="var(--text-secondary)">τ=1,000s</text>
  
  <!-- Layer 3: Traces -->
  <polyline fill="none" stroke="var(--border-strong)" stroke-dasharray="4,4" stroke-width="1.3" points="375,56 430,76 495,96 555,108 635,112"/>
  <polyline fill="none" stroke="var(--accent-focal)" stroke-width="2" points="375,72 430,98 495,124 555,142 635,153"/>
  
  <!-- Layer 4: Halo-Protected Text Callout (Zero Line Collision) -->
  <text class="va-svg-halo-text" x="480" y="90" font-weight="600">
    Uncompensated Coax Drift
  </text>
  <text class="va-svg-halo-text" x="450" y="136" font-weight="600" fill="var(--accent-focal)">
    DWDM Locked 0.81 ps RMS
  </text>
</svg>
```

### 4.2 Exploded 3-Plane Isometric Mechanical Stack
```html
<svg width="100%" height="220" viewBox="0 0 320 220" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Exploded Optical Syntonization Stack">
  <!-- Plane 3 (Top: PCIe BAR0 TAI Ring) -->
  <polygon points="45,45 200,32 255,62 100,75" fill="var(--tint-indigo-bg)" stroke="var(--border-strong)" stroke-width="1.3"/>
  <line x1="255" y1="62" x2="280" y2="52" stroke="var(--text-secondary)" stroke-width="1"/>
  <circle cx="280" cy="52" r="2" fill="var(--accent-focal)"/>
  <text x="40" y="62" font-family="var(--font-serif)" font-size="11" font-style="italic" fill="var(--text-primary)">Plane 3 · PCIe BAR0 TAI Ring</text>

  <!-- Plane 2 (Mid: DDMTD Beat Detector) -->
  <polygon points="45,95 200,82 255,112 100,125" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.3"/>
  <line x1="255" y1="112" x2="280" y2="102" stroke="var(--text-secondary)" stroke-width="1"/>
  <circle cx="280" cy="102" r="2" fill="var(--accent-focal)"/>
  <text x="40" y="112" font-family="var(--font-serif)" font-size="11" font-style="italic" fill="var(--text-primary)">Plane 2 · DDMTD Beat (N=2^14)</text>

  <!-- Plane 1 (Base: SMF-28e Fiber) -->
  <polygon points="45,145 200,132 255,162 100,175" fill="var(--bg-surface)" stroke="var(--border-strong)" stroke-width="1.3"/>
  <line x1="255" y1="162" x2="280" y2="152" stroke="var(--text-secondary)" stroke-width="1"/>
  <circle cx="280" cy="152" r="2" fill="var(--accent-focal)"/>
  <text x="40" y="162" font-family="var(--font-serif)" font-size="11" font-style="italic" fill="var(--text-primary)">Plane 1 · 1550nm SMF-28e Fiber</text>
</svg>
```

### 4.3 Automated Text-Path Collision Detection Logic
```python
def check_svg_text_collision(text_bbox: tuple[float, float, float, float], path_segments: list[tuple[float, float, float, float]], has_halo: bool) -> bool:
    """Verify whether a polyline or path segment collides with unmasked text."""
    if has_halo:
        # Halo stroke carves 4px clearance; zero collision risk
        return False
    tx1, ty1, tx2, ty2 = text_bbox
    for x1, y1, x2, y2 in path_segments:
        # Line segment bounding box intersection test
        if max(x1, x2) >= tx1 and min(x1, x2) <= tx2 and max(y1, y1) >= ty1 and min(y1, y2) <= ty2:
            return True  # Collision detected!
    return False
```

---

## 5. Verification & Audit Checklist for Figures & Breakouts
- [ ] Every visible SVG `<text>` satisfies `10.0px <= rendered_px <= 16.0px` across all 5 standard viewports.
- [ ] Gate 19 Verification: Zero unmasked SVG stroke-through-text collisions across all diagrams.
- [ ] Multi-panel figures stack cleanly without clipping on mobile viewports (`390px`).
- [ ] All numeric axes feature explicit engineering units in monospace typography.
- [ ] SVGs enforce valid aspect ratios (`xMidYMid meet`) and strictly eliminate `preserveAspectRatio="none"`.
- [ ] Explosive mechanical stacks maintain clean planar clearance between layer labels.
