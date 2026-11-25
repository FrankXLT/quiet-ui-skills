# Quiet UI — Typography and Hierarchy

Quiet UI enforces strict typographic discipline designed for high-density systems, scientific publishing, and telemetry consoles. This guide details the 3-role offline font stack, the fluid 4K viewing-distance root scale, line-length constraints, the zero desktop table clipping invariant, and minimum legibility floors.

---

## 1. 3-Role Offline Font Stack & Tabular Numerals

Typography in Quiet UI is strictly partitioned into three specialized roles, eliminating decorative typeface pollution while guaranteeing 100% offline availability across operating systems:

```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-serif: 'Newsreader', 'Charter', 'Source Serif 4', Georgia, serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  --font-nums: tabular-nums slashed-zero;
}
```

### Typographic Role Mapping Table

| Role Token | Priority Fallback Sequence | Target Semantics | Ergonomic Invariant |
| :--- | :--- | :--- | :--- |
| `--font-sans` | Inter, system-ui, -apple-system, Segoe UI | Body copy, navigation rails, button labels, form inputs, tooltips | High x-height, neutral aperture, optimal legibility at small sizes |
| `--font-serif` | Newsreader, Charter, Source Serif 4, Georgia | Editorial headers, executive monograph summaries, pull quotes | High stroke contrast, rhythmic cadence for sustained reading |
| `--font-mono` | JetBrains Mono, Fira Code, ui-monospace | Hardware registers, memory hex offsets, code blocks, JSON payloads | Clear 0/O and 1/l disambiguation, fixed character pitch |
| `--font-nums` | `tabular-nums slashed-zero` | Telemetry readouts, financial balances, data tables, timer counts | Identical digit widths to prevent column jitter during live updates |

---

## 2. Fluid 4K Root Font Scale Clamp

Quiet UI rejects discrete, jarring responsive font jumps in favor of a continuous viewport-calibrated scale. The root font scale preserves human visual angle across viewing distances from 390px mobile screens to 3840px 4K wall consoles:

```css
:root {
  font-size: clamp(16px, calc(12.4px + 0.25vw), 22px);
  interpolate-size: allow-keywords;
  text-wrap: pretty;
  font-synthesis: none;
  -webkit-font-smoothing: antialiased;
}
```

### Viewport Calibration Curve

| Viewport Width | Typical Hardware Medium | Viewing Distance | Effective Root Size | Magnification |
| :--- | :--- | :--- | :--- | :--- |
| `390px` | Mobile phone | 25–35 cm | `16.00px` | 1.000x baseline |
| `820px` | Foldable / tablet | 35–45 cm | `16.00px` | 1.000x baseline |
| `1280px` | Laptop workstation | 45–55 cm | `16.00px` | 1.000x baseline |
| `1920px` | Full HD monitor | 55–65 cm | `17.20px` | 1.075x scale |
| `2560px` | 1440p / QHD monitor | 60–75 cm | `18.80px` | 1.175x scale |
| `3840px` | 4K UHD display | 75–120 cm | `22.00px` | 1.375x scale |

---

## 3. Typographic Step Tokens & Minimum Floor Rule

All text sizes derive from a 7-step fluid `rem` scale with an uncompromising lower floor to guarantee legibility on high-DPI panels:

```css
:root {
  --ts-xs: max(11px, 0.6875rem);           /* Hard legibility floor: 11px */
  --ts-sm: max(12px, 0.78125rem);          /* Badges, table cells */
  --ts-nav: max(12.5px, 0.8125rem);        /* Sidebar navigation links */
  --ts-base: max(13.5px, 0.875rem);        /* Standard UI body text */
  --ts-prose: max(15px, 0.96875rem);       /* Sustained monograph reading */
  --ts-md: max(15.5px, 1rem);              /* Section subheadings */
  --ts-xl: clamp(1.25rem, 1.1rem + 0.45vw, 1.55rem);    /* Card titles & primary KPIs */
  --ts-display: clamp(1.5rem, 1.3rem + 0.65vw, 1.9rem); /* Monograph titles, main heroes */
}
```

> **The Minimum Floor Rule**: No font size rendered in a Quiet UI system may drop below `11px` (`var(--ts-xs)`), regardless of nested container transforms, density scaling, or zoom states.

---

## 4. Line Length Constraints: 72ch vs. `.va-bleed-wide`

Unconstrained line length induces saccadic reader fatigue and return-sweep tracking errors. Quiet UI enforces strict typographic width boundaries:

- **Prose Reading Ceiling (`72ch`)**: Monograph paragraphs, analysis briefs, and changelog documentation must never exceed `72ch` (`--measure-prose: 72ch`).
- **Breakout Canvas (`.va-bleed-wide`)**: High-column telemetry tables, multi-trace logic analyzer waveforms, and topological diagrams break out of the 72ch prose flow up to `96ch` or `116ch`.

```
[--- Container Max Width: 116ch ----------------------------------------------------]
  
  [--- Centered Monograph Prose: 72ch Max ---]
  Typography in Quiet UI respects human visual
  reading angles and maintains rhythmic cadence.
  
  [================== Bleed-Wide Table Breakout: 104ch ===================]
  | Register | Offset | Bit 7 | Bit 6 | Bit 5 | Bit 4 | Mode | Status    |
  | CR0      | 0x0000 | PE    | MP    | EM    | TS    | R/W  | ARMED     |
  [=======================================================================]
  
  [--- Centered Monograph Prose: 72ch Max ---]
  Return to the sustained reading flow without
  losing visual tracking anchor points.
```

---

## 5. Zero Desktop Table Clipping Invariant

Data tables are core scientific instruments. Table truncation or clipped cell values on desktop screens indicate UI architectural failure:

> **The Zero Clipping Invariant**: On screens $\ge 1280\text{px}$, tabular data views must **never render horizontal scrollbars** or clip columns. Column widths must automatically adapt using flexible fractional track distribution and compact header kickers.

### Table Layout Strategy
1. **Desktop ($\ge 1280\text{px}$)**: Full multi-column view with proportional `fr` tracks. No scrollbar.
2. **Compact Viewport ($< 1280\text{px}$)**: Progressive column collapse hiding secondary metrics into expandable disclosure drawers.
3. **Mobile ($< 700\text{px}$)**: Morph table rows into card-based key-value pairs.

---

## 6. Concrete CSS Architecture

```css
@layer quiet.typography, quiet.layout;

@layer quiet.typography {
  .va-prose {
    font-family: var(--font-sans);
    font-size: var(--ts-prose);
    line-height: 1.6;
    max-inline-size: var(--measure-prose, 72ch);
    margin-inline: auto;
    color: var(--text-primary);
  }

  .va-editorial-h1 {
    font-family: var(--font-serif);
    font-size: var(--ts-display);
    font-weight: 500;
    line-height: 1.2;
    letter-spacing: -0.015em;
    text-wrap: balance;
    color: var(--text-primary);
  }

  .va-kicker {
    font-family: var(--font-sans);
    font-size: var(--ts-xs);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
  }

  .va-nums {
    font-variant-numeric: var(--font-nums);
    font-feature-settings: 'tnum' 1, 'zero' 1;
  }

  .va-bleed-wide {
    inline-size: 100%;
    max-inline-size: var(--stage-editorial-max, 116ch);
    margin-inline: auto;
  }

  .va-data-table {
    inline-size: 100%;
    border-collapse: collapse;
    font-size: var(--ts-sm);
    font-variant-numeric: var(--font-nums);
  }

  .va-data-table th {
    font-family: var(--font-sans);
    font-size: var(--ts-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border-strong);
    padding: var(--density-row-py) var(--density-row-px);
    text-align: left;
  }

  .va-data-table td {
    padding: var(--density-row-py) var(--density-row-px);
    border-bottom: 1px solid var(--border-hairline);
    color: var(--text-primary);
  }
}
```

---

## 7. Plain Everyday Copy, Chrome Icon Discipline & Anti-Patterns

- **Plain Everyday Headings & Chart Titles**: Write clear, scannable labels matched to user mental models (for example, **`"Activity by Hour of Day"`** instead of opaque jargon like `"Diurnal Rhythm"`, or **`"Daily Cost & Token Mix"`** instead of `"Stochastic Expenditure Manifold"`). Reserve formal physics/metrology nomenclature strictly for analytical proof views (`L2`/`L3`).
- **Zero Chrome Pictographic Emojis (`[EMOJI_IN_CHROME]`)**: Never place Unicode pictographic emojis (`U+1F300–U+1FAFF`, `U+2600–U+27BF` lock/sparkles/warning/check/cross glyphs) inside `<header>`, `<nav>`, `<button>`, `[role="tab"]`, or `[role="toolbar"]` chrome—render crisp `14–16px` inline `<svg aria-hidden="true">` icons inheriting `stroke="currentColor"` instead.

| Anti-Pattern | Operational Consequence | Architectural Remedy |
| :--- | :--- | :--- |
| Prose container spanning 100% of 1920px screen | Lines exceed 150ch; reader loses tracking on every carriage return. | Constrain prose blocks to `max-inline-size: 72ch`. |
| Obscure jargon or pictographic emojis inside chrome controls | Confuses everyday operators and breaks forced-colors / screen readers (`[EMOJI_IN_CHROME]`). | Use plain everyday titles paired with `currentColor` `<svg>` icons. |
| Proportional digits in live telemetry readouts | Text characters jump horizontally as numbers increment (1 vs 8). | Declare `font-variant-numeric: tabular-nums slashed-zero`. |
| Horizontal scrollbars on desktop table displays | Vital telemetry obscured off-screen during mission analysis. | Use responsive grid collapsing and `.va-bleed-wide` breakouts. |
| Mid-word breaks on monospace parameter keys (`820–900px`) | `overflow-wrap: anywhere` slices dotted keys (`sanitizat`/`ion`) instead of wrapping prose columns (`[PARAM_KEY_MIDWORD_WRAP]`). | Keep `td > code` / `.w2-code` `white-space: nowrap; word-break: normal` at `min-width: 601px` and stack rows cleanly `<= 600px`. |
| Font size reduction below 11px for "compactness" | Unreadable on non-Retina displays; triggers accessibility audit failure. | Enforce minimum floor `max(11px, ...)`. |
| Mixing sans-serif and serif indiscriminately | Visual chaos and diluted editorial voice. | Strictly reserve `--font-serif` for headers and monograph abstracts. |
