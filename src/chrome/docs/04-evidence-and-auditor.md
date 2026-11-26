# Calibrated Charts & Layout Auditor

Most chart bugs happen when code draws raw pixels by hand or hides missing measurements behind smooth curves. Quiet UI solves both problems in two steps: **compile charts from structured JSON specs** so math and labels stay exact, then **run an automated layout auditor** to catch visual and accessibility regressions before shipping.

---

## Why Quiet UI Compiles Charts from JSON Specs

Writing `<svg>` coordinates manually in an editor or asking an AI model to guess `x`/`y` numbers leads to clipped text, awkward tick marks, and misleading trends. Describing a figure in `urn:quiet-ui:schema:v9:<modality>` JSON gives every chart five built-in guarantees:

- **`1-2-5` steps**: Axes snap to clean human-readable intervals (`1`, `2`, `5` times powers of `10`) rather than irregular fractions like `3.7` or `14.3`, making mental estimation effortless.
- **Explicit unit labels**: Every axis and readout pairs the quantity with its unit (for example, `Active Power, P / kW` or `η_bte / %`) so readers never guess whether a value is watts, kilowatts, or percent.
- **Honest gaps**: Missing or `null` samples stay visible as broken gaps in lines and waveforms instead of being silently bridged by fake interpolation.
- **`Chart | Table` toggle**: Takeaway figure cards pair the visual chart with a clean data table so screen readers, keyboard users, and detail checkers can inspect exact numbers.
- **`Copy data` and `Copy for AI`**: One click exports tab-separated values (`TSV`) for spreadsheets (`Copy data`) or a structured Markdown summary (`Copy for AI`) ready to paste into an analysis prompt.

---

## When to Use `compile_evidence.py` vs. `window.QuietSvgLayout`

Choose the compiler path that matches how your page delivers data:

| Approach | When to Use It | Runtime Dependencies | Primary Entry Point |
| :--- | :--- | :--- | :--- |
| **`compile_evidence.py`** | Static reports, print briefs (`M1`), docs pages, bitfields, HIL scopes, and system schematics built from known JSON specs | **Zero JS** (pure Python stdlib emitting standalone HTML or `<figure>` SVG) | `python3 -B skills/quiet-evidence/scripts/compile_evidence.py spec.json --rigor L3 --theme white --out chart.html` |
| **`window.QuietSvgLayout`** | Live dashboards (`M3`/`M5`) where users filter ranges, resize panes, or stream dynamic data in the browser | Bundled `quiet-evidence-bundle.js` + CSS tokens (`QuietSvgLayout` & `QuietEChartsDefaults`) | `niceScale125`, `sharedNiceScale125`, `measureCategoryGutter`, `placeReferenceLabel`, `binTimeSeries` |

Use `--fragment` with `compile_evidence.py` when embedding a compiled `<figure>` inside an existing page, or import `compile_spec(...)` directly in Python build scripts. When building interactive browser charts, route dynamic scales through `window.QuietSvgLayout` and `QuietEChartsDefaults` so theme switches (`white`, `paper`, `dark`, `dark-paper`) and resize events re-measure labels automatically.

---

## How `audit_quiet_html.py` Protects Every Page

`skills/quiet-ui/scripts/audit_quiet_html.py` is a portable quality gate you can run against a single file, a static build directory, or a live local server. Think of it as an automated design and accessibility reviewer with three layers:

1. **Static HTML, CSS, JS & JSON checks**: Scans source files immediately—with no browser needed—to catch CSS overrides (`!important`), tiny hardcoded fonts (`< 11px`), missing form labels, dead-end empty states, chrome emojis, and inline mock fixtures.
2. **Token discipline (`--strict-drift`)**: Flags raw `#hex`, `rgb()`, and `hsl()` colors in application CSS or inline presentation styles so pages use semantic `var(--*)` tokens instead of drifting off-theme.
3. **Persistent `.quiet-ui.md` project contract**: Run `--init-context` once to create `.quiet-ui.md` in your repo root (or pass `--context`). It remembers Greenfield vs. Brownfield mode, mount prefixes, file exclusions, `--strict-drift`, and your **Deprecation Blocklist** (`selector:` / `copy:`) so removed legacy UI never creeps back in.
4. **Live browser checks (`--cdp`)**: Launches Headless Chrome (requires `selenium` + Chrome) at **`390px`** (phone), **`820px`** (unfolded foldable / tablet), and **`1440px`** (desktop) to measure real rendered pixel bounds—catching oversized sticky headers, clipped controls, and SVG labels colliding with plotted lines.

```bash
# 1. Create starter .quiet-ui.md contract (auto-discovered by future runs)
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py --init-context path/to/repo/.quiet-ui.md

# 2. Run static + strict token-drift checks
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py path/to/web --context path/to/repo/.quiet-ui.md --strict-drift

# 3. Run live Headless Chrome sweep at 390px, 820px, and 1440px
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py http://127.0.0.1:8788/ --cdp --mount-prefix /web=/path/to/web
```

---

## Common Auditor Findings Reference

| Finding Code | Check Type | What Triggered It | How to Fix It |
| :--- | :--- | :--- | :--- |
| **`[IMPORTANT]`** | Static CSS | Stylesheet contains a forbidden `!important` declaration. | Remove `!important` and place overrides in the proper `@layer` (`reset, tokens, shell, archetypes, evidence, views, utilities`). |
| **`[FONT_FLOOR]`** | Static CSS (`[FONT_FLOOR_CDP]` in `--cdp`) | Hardcoded `font-size` below `11px` (or computed text under `10.8px` in `--cdp`). | Use `--ts-xs` (`max(11px, 0.6875rem)`) or larger fluid typography tokens. |
| **`[STICKY_CHROME_BLOAT]`** | Live `--cdp` (`390` / `820` / `1440px`) | Top sticky/fixed header height exceeds `64px` (`>= 680px` viewports) or `88px` (`< 680px`). | Keep topbars to a single compact row on desktop/foldables and at most two compact rows on mobile. |
| **`[TOKEN_BYPASS_HEX]`** | Static CSS (`--strict-drift`) | Raw `#hex`, `rgb()`, or `hsl()` color literal used outside token/theme layers. | Replace the literal color with a semantic CSS token such as `var(--text-primary)` or `var(--status-warn)`. |
| **`[DEAD_END_ZERO_STATE]`** | Static HTML & `--cdp` | Filtered empty-state box has no recovery `<button>` or `<a href>` action. | Add a visible `Clear filters` or `Reset` button/link inside the empty-state container. |
| **`[SVG_LABEL_STROKE_COLLISION]`** | Live `--cdp` | Visible SVG `<text>` label sits closer than `6px` to a plotted curve/line without an opaque badge plate or halo. | Route labels through `placeReferenceLabel` / `svg_knockout_label` or increase offset clearance to `>= 6px`. |

> [!TIP]
> Pass `--json` to `audit_quiet_html.py` in CI pipelines to capture machine-readable pass/fail counts and exact file/line diagnostics.
