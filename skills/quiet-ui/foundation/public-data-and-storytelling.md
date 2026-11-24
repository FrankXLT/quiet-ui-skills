# Public Data, Research Briefs & Multi-Format Storytelling

Guidelines for turning empirical civic, policy, demographic, and scientific datasets into clear web articles, `16:9` slide briefings, and collision-free print handouts—extending Pillar 1 medium rules (`m1` / `m2`) with Pillar 2 chart compilers and Pillar 3 numerical conservation.

---

## 1. Question-First Brief & Unboxed Editorial Callouts

1. **Question-First Headline**: Phrase the main article or brief title as an everyday human question (*"How have reading proficiency and household income mobility shifted across U.S. states?"*). Pair long headlines with a compact `.va-freshness-stamp` in the left margin (`border-inline-start: 2px solid var(--border-strong)`) displaying the publication cycle and data vintage.
2. **Direct First-Sentence Answer**: Highlight the decisive quantitative answer in the very first sentence (`.va-lead-answer > .va-lead-highlight`) rather than burying key outcomes beneath methodology notes.
3. **Interactive Scope Switcher (`.va-scope-bar`)**: When a brief compares a national aggregate alongside highlighted jurisdictions (e.g., `US National` | `Maryland` | `Wyoming`), render a compact joined bar (`border-radius: var(--radius-sm)`) that atomically updates the lead sentence, unboxed callouts, and map selection.
4. **Unboxed Key Numbers (`.va-editorial-callouts`)**: Place 2–4 headline metrics directly on the page canvas without heavy dashboard card borders (`border: 0; background: transparent; padding: 0;`), anchored by a plain-English 1-line description and inline source citation.

```css
@layer views {
  .va-editorial-callouts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
    gap: 0.85rem 1.5rem;
    border-bottom: 1px solid var(--border-hairline);
  }
  :is([data-theme="white"], [data-theme="paper"]) .va-code-surface {
    background: var(--bg-subtle);
    color: var(--text-primary);
    border: 1px solid var(--border-strong);
  }
}
```

---

## 2. Four-Part Takeaway Figure Cards & In-Card Controls

Every civic, policy, or research visualization is authored as a `.va-figure-card` following a strict four-part vertical cadence:

| Band | Class / Role | Contract |
| :--- | :--- | :--- |
| **1. Finding Headline** | `.qe-fig-title` | Plain-English takeaway sentence stating what changed and by how much (zero internal slugs). |
| **2. Metric, Unit & Window** | `.qe-takeaway-subtitle` | Exact population denominator, unit (`%`, `USD`, `$B`), and date bounds (`2019 -> 2024`). |
| **3. Direct Visual + Table** | `.va-card-chart-panel` / `.va-card-table-panel` | Compiled `<svg>` chart paired in-place with an accessible `<table>` (`hidden="until-found"` + `beforematch` auto-reveal) switched via `.va-chart-table-switch`. |
| **4. Plain-English Footer** | `.qe-takeaway-footer` | Transparent **Note:** (fallback reporting years `*`, cohort boundaries, equal-chance baseline) and **Source:** provenance attribution. |

### Action Toolbar Ergonomics (`.va-card-actions`)
- Provide explicit segmented toggle buttons (`Chart` | `Table`) using `aria-pressed="true|false"` paired with matching `aria-controls`.
- Provide **`Copy data`** (clean TSV table for spreadsheets) and **`Copy for AI`** (structured Markdown brief containing headline, subtitle, exact Markdown table, `Note:`, and `Source:`).
- Place `<span class="va-copy-status" role="status" aria-live="polite"></span>` **outside** action buttons so status updates announce cleanly without disabling triggers or replacing accessible button names.

---

## 3. Five Specialized Public-Data Compilers (`quiet-evidence`)

Select the appropriate canonical schema rather than guessing freehand SVGs or wrapping illegible end labels:

1. **Equal-Area US 51-Hex Tile Map (`plot_kind: "us_hex_tile_map"`)**:
   - Places all 50 states plus DC on equal-area hexagon cells so `DC`, `MD`, `DE`, and `RI` stay legible and uniformly clickable (`role="button"`, `tabindex="0"`).
   - Stepped 5-bin 1–2–5 legend sits cleanly above the grid; label ink switches dynamically between dark (`#0F172A`) and white (`#FFFFFF`) via computed WCAG relative luminance per bin.
2. **Ranked Directional Arrow Dumbbell (`plot_kind: "arrow_dumbbell"`)**:
   - Ranks jurisdictions or cohorts along vector arrows (`→` gain, `←` decline) with non-overlapping endpoint numbers.
   - Any series retaining a prior-cycle survey window MUST carry an asterisk `*` paired with an explicit `fallback_vintage` footnote.
3. **Paired Subgroup Bars + Shaded Overall (`plot_kind: "paired_subgroup_bars"`)**:
   - Pairs subgroup horizontal bars using fixed decimals, flips text ink for wide vs narrow bars, and aligns a shaded right-hand `Overall` column row-for-row.
4. **Dual `Count | % Share` Slopegraph (`plot_kind: "dual_slopegraph"`)**:
   - Splits raw volume (left) and percentage share (right) with a vertical hairline divider, hollow endpoint rings, and optional crossover pointer.
   - Emits unit suffixes (`B`, `%`) strictly once on the top visual row and calculates right-gutter width with step-leader brackets so zero category labels truncate (`...`).
5. **Diverging `% Change` + Unshaded `$ Level` Matrix (`table_kind: "diverging_matrix"`)**:
   - Shades percentage-change cells (`data-diverge="pos-hi|pos-lo|neg-lo|neg-hi"`) with calm semantic tokens (`var(--status-ok-bg)`, `var(--status-err-bg)`) while keeping dollar levels unshaded and right-aligned.
   - Precedes quintile matrices with compact `.va-cohort-defs` chips and discloses equal-chance null expectations (`20.0%` per quintile) inside `Note:`.

---

## 4. Automated Editorial, Notebook & Print Quality Gates

| Audit Code | Failure Mode Caught | Remediation Rule |
| :--- | :--- | :--- |
| **`[PRINT_FLOW_COLLISION]`** | Persistent fixed navbars stamping over print plots, figures overlapping prose, or tables clipping right page margins. | Strip topbars/rails/action buttons in `@media print`, set `position: static`, `break-inside: avoid`, and expand `.va-diverging-matrix` full-width. |
| **`[PROSE_COLUMN_STARVATION]`** | Split commentary squeezed `< 35ch` (`< 260px`) beside desktop charts. | Apply `minmax(36ch, 0.92fr) minmax(0, 1.35fr)` track minimums on `.va-brief-split`. |
| **`[NESTED_PROSE_SCROLL]`** | Prose trapped in short inner scrollboxes or fade-out gradient masks. | Let editorial prose expand at full natural flow height (`overflow: visible`). |
| **`[CODE_LUMINANCE_SHOCK]`** | Pitch-black `#000000` `<pre><code>` blocks glaring inside `white`/`paper` briefs. | Use `var(--bg-subtle)` cool-slate surfaces with `1px solid var(--border-strong)`. |
| **`[DIAGONAL_TICK_OR_ROTATED_Y_TITLE]`** | Sawtooth rotated X-axis ticks or stacked vertical Y-axis prose duplicating subtitle units. | Keep horizontal X ticks and place metric units once in `.qe-takeaway-subtitle`. |
| **`[END_LABEL_CLIP]`** | Right-edge line labels clipping SVG bounds or ending with ellipsis (`...`). | Measure widest label dynamically (`_approx_px` / `QuietSvgLayout`) and separate vertically with step leaders. |

---

## 5. Schema Quick-Reference (`urn:quiet-ui:schema:v9`)

```json
{
  "$schema": "urn:quiet-ui:schema:v9:plot",
  "id": "state-reading-hex-map",
  "plot_kind": "us_hex_tile_map",
  "takeaway": true,
  "unit": "%",
  "focus_state": "MD",
  "metadata": {
    "title": "Thirty-one percent of US fourth-graders read proficiently in 2024",
    "subtitle": "Share of Grade 4 students at or above NAEP Proficient (%), 2024",
    "note": "Each jurisdiction occupies equal hex area; ink polarity adapts automatically.",
    "source": "NAEP Nation's Report Card (2024 Public Assessment)"
  }
}
```

| Format / Medium | Layout Rule | Data Conservation Rule |
| :--- | :--- | :--- |
| **`Web Brief` (`.va-brief-web`)** | One anchor visual per question; full-height `.va-editorial-prose` alongside visual (`>= 35ch`). | Every figure exposes `[Chart \| Table]`, TSV `Copy data`, and Markdown `Copy for AI`. |
| **`Briefing Slide` (`.va-slide-deck`)** | One finding per `16:9` `.va-slide-frame` card plus methodological Appendix slide. | Slide KPI tables read directly from the same `corpus.json` metric dictionary. |
| **`Print Sheet` (`@media print` / `M1`)** | Topbars, side rails, scope pills, and action toolbars hidden; `.va-diverging-matrix` full-width. | Note blocks, cohort bounds, fallback years (`*`), and `Source:` stay attached to figures. |

---

## 6. Multi-Format Pre-Flight Checklist

1. Does the main heading pose an everyday reader question answered directly in the first clause?
2. Do unboxed `.va-editorial-callouts` carry verified figures and source citations without card clutter?
3. Are rate-of-change table columns quietly tinted while raw currency levels (`$ Level`) remain unshaded?
4. Does toggling `Table` reveal an exact accessible `<table>` (`hidden="until-found"`), and does `Copy for AI` trigger the external `role="status"` confirmation?
5. Do `Brief`, `Slide Deck (16:9)`, and `Paper` Print Sheet share one canonical dataset and pass `audit_quiet_html.py --cdp` with zero overlap, zero scroll-trapped prose, and zero dark code shock?
6. Are all 51 hex tiles (`AL..WY` + `DC`) legible and focusable (`aria-label`, `tabindex="0"`) with luminance-flipped ink contrasting `>= 4.5:1` across every theme?
7. Do prior-cycle survey rows in ranked dumbbells retain an asterisk (`*`) paired with a plain-English `fallback_vintage` footnote rather than blending mismatched years silently?


