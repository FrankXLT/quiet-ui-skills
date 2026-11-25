# Public Data, Journalistic Articles & Interactive Explorers

Guidelines for turning empirical civic, policy, demographic, and scientific datasets into serene web articles and standalone interactive data explorers—extending Pillar 1 medium rules (`m1` / `m2`) with Pillar 2 chart compilers and Pillar 3 numerical conservation. **Strict Architectural Rule:** Every public-data screen MUST commit 100% to **Path A (Fluid Journalistic Article)** OR **Path B (Full-Width Interactive Data Explorer)**—never hybridize magazine prose with persistent sidebars, slide-deck toggles, or boxed button toolbars wedged above charts.

---

## 1. Strict Path A vs. Path B Architecture

1. **Path A — Fluid Journalistic Data Article (`N0` Full Reading Canvas)**:
   - **Zero App Sidebar**: Open in full-canvas `N0` mode (no persistent left rail, collapsible Brief Sections drawer, badge counts, or Compact/Comfortable footer).
   - **Provenance Eyebrow & Question Headline**: Place one quiet provenance eyebrow line (`.va-provenance-eyebrow`) directly above the serif Question-First `<h1>` (*"How have reading proficiency and household income mobility shifted across U.S. states?"*).
   - **Inline Sentence Scope Dropdown**: Weave one underlined inline `<select class="va-inline-scope-select" aria-label="Select jurisdiction scope">` naturally into `.va-lead-answer` (`Across [the United States ▾], ...`) so changing scope updates `.va-lead-highlight`, the three unboxed `.va-editorial-callouts`, and `.va-hex-tile.is-selected`.
   - **Centered `68ch` Spine & `56rem` Breakouts**: Flow all body prose cleanly down one centered `min(68ch, 100%)` spine column, widening cleanly only on `.va-breakout-wide` (`max-inline-size: min(56rem, 100%)`) for charts and tables. Remove 50/50 text-beside-chart splits, slide-deck toggles, and code slabs in general-reader articles.
2. **Path B — Full-Width Interactive Data Explorer (`qe-specimen-wide` / Analytical Stage)**:
   - Give standalone workbench explorers and Component Library specimens 100% container width with zero side-by-side essay columns squeezing visuals, a single boxed `.va-card-actions` top bar, and methodology notes tucked underneath.

```css
@layer views {
  .va-editorial-article {
    display: flex;
    flex-direction: column;
    gap: 1.4rem;
    inline-size: 100%;
  }
  .va-editorial-article > * { inline-size: 100%; max-inline-size: min(68ch, 100%); margin-inline: auto; min-inline-size: 0; }
  .va-editorial-article > .va-breakout-wide { max-inline-size: min(56rem, 100%); }
}
```

---

## 2. Takeaway Figure Controls (Path A Quiet Footer Links vs. Path B Toolbar)

Every civic or research figure follows a clean 4-part vertical cadence (**1. Finding Headline `.qe-fig-title`** -> **2. Metric, Unit & Window `.qe-takeaway-subtitle`** -> **3. Direct Visual / Accessible Table `.va-card-chart-panel` / `.va-card-table-panel`** -> **4. Plain-English Footer `.qe-takeaway-footer`**):

- **Path A Editorial Mode (`chrome="editorial"`, `.is-editorial`)**:
  - Render visuals unboxed directly on canvas separated by clean whitespace and a top hairline rule (`border-top: 1px solid var(--border-hairline)`).
  - **Zero button toolbars above visuals**: move interactive actions into quiet plain-text `<button class="va-footer-link">` controls on the `.va-editorial-footer-line` (`Source: NAEP 2024 · Show data table · Copy for AI`). Clicking `Show data table` swaps cleanly to an accessible booktabs table (`Show chart` to flip back; `.qe-caption-sr` caption prevents duplicate headings; right-aligned numeric `.num` columns), and `Copy for AI` briefly reads `Copied for AI` with zero layout jump via CSS inline-grid width reservation.
- **Path B Explorer Mode (`.va-card-actions`)**:
  - Render segmented `Chart` | `Table` (`aria-pressed` + `hidden="until-found"` + `beforematch`), **`Copy data`** (TSV), and **`Copy for AI`** (Markdown brief), keeping `<span class="va-copy-status" role="status" aria-live="polite"></span>` positioned cleanly outside flex flow (`position: absolute`).
  - **Principled Toggle Placement**: Enable `Chart | Table` (`takeaway: true`) on multi-bin analytical curves (`8–51` points such as 51-state hex maps, slopegraphs, Treasury 8-quarter stress curves, and 10-bin AI calibration curves) where exact coordinate lookup helps; omit `Chart | Table` on compact `<= 6`-row `paired_subgroup_bars` already printing all rows and `All Adults` totals inline.

---

## 3. Five Specialized Public-Data Compilers (`quiet-evidence`)

Select the appropriate canonical schema rather than guessing freehand SVGs or wrapping illegible end labels:

1. **Equal-Area US 51-Hex Tile Map (`plot_kind: "us_hex_tile_map"`)**:
   - Places all 50 states plus DC on equal-area hexagon cells so `DC`, `MD`, `DE`, and `RI` stay legible and uniformly clickable (`role="button"`, `tabindex="0"`).
   - Stepped 5-bin 1–2–5 legend sits cleanly above the grid; label ink switches dynamically between dark (`#0F172A`) and white (`#FFFFFF`) via computed WCAG relative luminance per bin.
2. **Ranked Directional Arrow Dumbbell (`plot_kind: "arrow_dumbbell"`)**:
   - Ranks jurisdictions or cohorts along vector arrows (`→` gain, `←` decline) with non-overlapping endpoint numbers (`880` wide breakout canvas in both `bench` and `editorial` modes) and stationary dual-ring `(unchanged)` markers when `start == end`.
   - Any series retaining a prior-cycle survey window MUST carry an asterisk `*` paired with an explicit `fallback_vintage` footnote.
3. **Paired Subgroup Bars + Shaded Overall (`plot_kind: "paired_subgroup_bars"`)**:
   - Pairs subgroup horizontal bars using fixed decimals, flips text ink for wide vs narrow bars, borders light `.is-overall` swatches for Paper contrast, and aligns a shaded right-hand `Overall` column row-for-row.
4. **Dual `Count | % Share` Slopegraph (`plot_kind: "dual_slopegraph"`)**:
   - Splits raw volume (left) and percentage share (right) with direct right-hand endpoint labels, omitting redundant top swatch rows and generic bottom `Series · Analytical Model` fallback legends.
5. **Diverging `% Change` + Unshaded `$ Level` Matrix (`table_kind: "diverging_matrix"`)**:
   - Shades percentage-point and rate columns (`data-diverge="pos-hi|pos-lo|neg-lo|neg-hi"`) with calm semantic tokens (`var(--status-ok-bg)`, `var(--status-err-bg)`) while keeping dollar levels unshaded, headers sentence-case, and numbers right-aligned.
   - Disclose percentage-point units (`Mobility vs 20% Baseline (pp)`, anchored at `0.0 pp` neutral national benchmark = `20.0%` equal-chance expectation) and reveal `.va-scroll-cue` ONLY when `scrollWidth > clientWidth + 2` (always hidden in Paper `m1` and `@media print`).

---

## 4. Automated Editorial, Notebook & Print Quality Gates

| Audit Code | Failure Mode Caught | Remediation Rule |
| :--- | :--- | :--- |
| **`[PRINT_FLOW_COLLISION]`** | Persistent fixed navbars stamping over print plots, figures overlapping prose, or tables clipping right page margins. | Strip topbars/rails/action buttons/footer links in `@media print`, set `position: static`, `break-inside: avoid`, and expand `.va-diverging-matrix` full-width. |
| **`[PRINT_EDGE_CLIP]`** | Zeroed horizontal padding (`padding-inline: 0`) pushing standalone/editorial print text flush against `x = 0` or right paper edge. | Keep `box-sizing: border-box; padding-inline: max(1.5rem, 24px);` on `.va-editorial-article`, `.va-question-brief`, and `.v9-stage-inner` under `@media print`. |
| **`[PROSE_COLUMN_STARVATION]`** | Split commentary squeezed `< 35ch` (`< 260px`) beside desktop charts. | Avoid 50/50 splits around long-form data stories; flow prose cleanly along a `68ch` centered column. |
| **`[NESTED_PROSE_SCROLL]`** | Prose trapped in short inner scrollboxes or fade-out gradient masks. | Let editorial prose expand at full natural flow height (`overflow: visible`). |
| **`[CODE_LUMINANCE_SHOCK]`** | Pitch-black `#000000` `<pre><code>` blocks glaring inside `white`/`paper` briefs. | Use `var(--bg-subtle)` cool-slate surfaces with `1px solid var(--border-strong)` on technical developer specs (omit raw code in general civic articles). |
| **`[DIAGONAL_TICK_OR_ROTATED_Y_TITLE]`** | Sawtooth rotated X-axis ticks or stacked vertical Y-axis prose duplicating subtitle units. | Keep horizontal X ticks and place metric units once in `.qe-takeaway-subtitle`. |
| **`[END_LABEL_CLIP]`** | Right-edge line labels clipping SVG bounds or ending with ellipsis (`...`). | Measure widest label dynamically (`_approx_px` / `QuietSvgLayout`) and separate vertically with step leaders. |
| **`[SVG_LABEL_STROKE_COLLISION]`** | Plotted curve, slope, or cable polyline slicing through or crowding `< 6px` near visible SVG text labels. | Position vertex/annotation labels `>= 6px` clear of non-grid strokes across `1440px`, `900px`, and `390px` unless inside an opaque badge `<rect>`. |

---

## 5. Schema & Path Quick-Reference (`urn:quiet-ui:schema:v9`)

| Decision Dimension | Path A — Journalistic Article | Path B — Interactive Data Explorer |
| :--- | :--- | :--- |
| **Navigation Shell** | `N0` full reading canvas (zero app rail or drawer) | `N1`–`N4` workbench shell as task demands |
| **Measure & Framing** | `68ch` centered prose + `56rem` unboxed breakouts | `100%` fluid width (`qe-specimen-wide`) |
| **Scope Switching** | Inline `<select>` woven inside lead prose | Top filter chips / grouped dropdown controls |
| **Figure Actions** | Quiet `Source` footer links (`Show data table · Copy for AI`) | Boxed `.va-card-actions` toolbar (`Chart \| Table`, TSV, AI) |
| **Code & Slide Controls** | Omitted in general civic stories | Permitted where interactive analysis requires |

```json
{
  "$schema": "urn:quiet-ui:schema:v9:plot",
  "id": "state-reading-hex-map",
  "plot_kind": "us_hex_tile_map",
  "takeaway": true,
  "unit": "%",
  "metadata": {
    "title": "Thirty-one percent of US fourth-graders read proficiently in 2024",
    "subtitle": "Share of Grade 4 students at or above NAEP Proficient (%), 2024",
    "note": "Each jurisdiction occupies equal hex area; ink polarity adapts automatically.",
    "source": "NAEP Nation's Report Card (2024 Public Assessment)"
  }
}
```

```bash
# Path A unboxed article figure vs Path B boxed explorer specimen
python3 -B skills/quiet-evidence/scripts/compile_evidence.py spec.json --chrome editorial --fragment
python3 -B skills/quiet-evidence/scripts/compile_evidence.py spec.json --chrome bench --out explorer.html
```

| Format / Medium | Layout Rule | Data Conservation Rule |
| :--- | :--- | :--- |
| **Path A Article (`N0`, `M2`)** | Zero sidebar; `68ch` prose spine + `56rem` unboxed breakouts; quiet `Source` footer links. | Inline `<select>` atomically synchronizes lead copy, callouts, and hex map from `corpus.json`. |
| **Path B Explorer (`M2`/`M3`)** | Full-width `qe-specimen-wide`; unified boxed `.va-card-actions` bar above visual. | Tables preserve exact coordinate values (`hidden="until-found"`), TSV, and AI Markdown. |
| **Print Sheet (`@media print` / `M1`)** | Chrome, action buttons, `.va-footer-link` controls, and `.va-scroll-cue` hidden; tables full-width. | Notes, cohort ranges, `*` fallback vintages, and `Source:` attribution remain printed cleanly. |

---

## 6. Path A & Path B Pre-Flight Checklist

1. Does the screen commit cleanly to EITHER **Path A** (unboxed `68ch`/`56rem` article with `N0` zero sidebar and footer links) OR **Path B** (full-width Explorer card with boxed top toolbar)?
2. Does Path A open with a provenance eyebrow, Question-First headline, inline `<select>` sentence dropdown, and unboxed `.va-editorial-callouts` without card clutter?
3. Are rate-of-change and mobility `pp` columns (`0.0 pp = 20.0%` baseline) quietly tinted while dollar levels remain unshaded, right-aligned in tabular numerals?
4. Are `.qe-caption-sr` captions hidden visually on toggled tables, ECharts plots refreshed cleanly on `Table -> Chart`, and `.va-scroll-cue` hidden whenever a table fits without horizontal overflow or prints?
5. Do all 51 hex tiles (`AL..WY` + `DC`) remain focusable (`tabindex="0"`) with adaptive `>= 4.5:1` ink contrast, and do prior-cycle rows carry explicit `*` `fallback_vintage` notes?


