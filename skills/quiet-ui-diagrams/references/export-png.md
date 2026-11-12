# Export to PNG (Headless Chrome / Selenium)

Convert generated diagram HTML files into transparent PNGs using headless Chrome and Selenium. Standalone and script-free.

## PNG export procedure
Render **the original HTML** (not the extracted SVG) and screenshot only the `<svg>` element's bounding box. This keeps font loading reliable (already wired in the source HTML) while satisfying the "diagram only" rule. The PNG always has a **transparent background** (`omit_background=True`) so it can be placed on any slide or doc colour without a white halo. For motion-enabled HTML, append `?motion=static`, await `document.fonts.ready`, and assert the motion root has `data-frame="static"` before capture; never export at an arbitrary wall-clock delay.

### Detection

Before running anything, verify Selenium headless Chrome is installed in the Python interpreter
you will use for the export. Try:

```
python3 -c "import selenium"
```

If that fails, try `python -c "import selenium"` (the usual command on
Windows). Use whichever interpreter passes the import for the rasterization
command below. If both imports fail, surface this exact instruction to the user
and stop:

> Selenium headless Chrome is not available. PNG export requires an approved Selenium headless Chrome
> installation and a compatible browser to be provisioned by the host
> environment; the skill never installs runtime dependencies automatically.
> Then ask me to export again.

Don't auto-install. The user asked for one feature, not a system change.

### Rasterize

Keep the user's project directory as the working directory so relative input and
output paths still resolve there. Invoke the packaged renderer by its absolute
path under the resolved skill directory with the interpreter that passed
detection: `python3 <skill-dir>/scripts/export_png.py <src.html> <out.png> [scale]`
or `python <skill-dir>/scripts/export_png.py <src.html> <out.png> [scale]`.

If the `networkidle` wait times out (a stalled font or stylesheet behind a proxy), the helper cancels the outstanding load with `window.stop()` and captures with fallback typography, printing a warning to stderr — pass that warning on to the user. Any other error propagates and fails the export normally. The helper requests the complete static motion frame, waits for font readiness, and rejects a motion root that has not reached `data-frame="static"`; ordinary script-free diagrams need no motion root.

Default `device_scale_factor=2` for crisp output. Accept `1` for compact assets or `3` for print/retina hero use, passed as a third CLI arg. Fractional scales such as `1.25` are also accepted within the documented 1–4 range for exact pixel sizes.

The helper's overflow release matters for the wide presets. `min-width` equals the viewBox width (see [`output-spec.md`](output-spec.md)), so a `doc-wide` or `slide-16x9` SVG is 1280px inside a 1200px frame, and its `.diagram-container` scroller clips the last 80px on screen. The screenshot covers the SVG's box but not what an ancestor clipped, so without the release the PNG comes out full size with a blank right edge. This is the screen-side counterpart of the templates' `@media print` rule.

### Output naming

`example-architecture.html` → `example-architecture.png`, written next to the source. Honour explicit user-provided paths. The rasterizer encodes the absolute source path as a file URI, so literal `#` and `%` characters in filenames remain filename content.

## Sizing the export

The PNG's pixel dimensions are the SVG's `viewBox` × `device_scale_factor`. The rasterizer establishes the capture viewport from the finite, nonzero viewBox dimensions so page CSS cannot enlarge or shrink the promised output. So the size decision was already made when the diagram was drawn — see [`output-spec.md` §2](output-spec.md) for the presets. Export only picks the multiplier.

| Destination | Scale | Result from a 1280×720 `viewBox` |
|---|---|---|
| Docs, README, wiki | 2 | 2560×1440 |
| Slide deck (projected) | 2 | 2560×1440 |
| Print / PDF handout | 3 | 3840×2160 |
| Inline thumbnail, email | 1 | 1280×720 |

### Hitting an exact pixel size

When the user needs specific dimensions (an OG card at exactly 1200×630, a slide image at 1920×1080), compute the scale factor instead of guessing — Selenium headless Chrome accepts fractional values:

```
scale = target_width / viewBox_width
```

A 960-wide `viewBox` at a 1200px target is `scale=1.25`. Two rules:

- **Never scale below 1** to hit a small target — that soft-focuses the type. Redraw at a smaller preset instead.
- **Never scale past 4** — beyond that you're upscaling a layout that was designed for a smaller canvas; redraw at `slide-16x9` or a print preset.

If the target aspect ratio doesn't match the `viewBox` aspect ratio, say so and offer to redraw at the matching preset. Padding or cropping a finished diagram to fit a frame is not an export operation — it breaks the 40px safe margin.

## Edge cases

- **Source is `assets/index.html`** (the gallery, multiple SVGs in one file): refuse the export and ask the user which specific diagram file they meant. Don't guess.
- **No `<svg>` block found**: the source isn't a diagram file. Tell the user; don't write anything.
- **Surrounding HTML matters to the user**: they want cards/header in the image. Tell them this skill exports diagrams only, and recommend a browser-based full-page screenshot (or a separate PDF print).
- **Source is missing fonts at runtime**: Selenium headless Chrome will substitute, the screenshot will look off. Check that the source HTML has the `<!-- Offline Font Stacks (Inter / Newsreader / JetBrains Mono) -->` tag in `<head>`. If absent, the file isn't from a current template — fix the source rather than working around it in export.

## What this command never does

- Modifies the source HTML.
- Adds export buttons or `<script>` tags. Static diagrams remain script-free; an already motion-enabled source may retain the scoped controller from [`animation.md`](animation.md), but export never injects another controller.
- Auto-emits `.svg` or `.png` alongside HTML generation. Manual on every call.
- Embeds an HTML wrapper (cards, headers) into the SVG via `foreignObject`. Too fragile across renderers.

The exporter preserves `@font-face` and scopes ordinary rules within block at-rules such as `@supports`, `@media`, `@layer`, and `@container` without flattening their conditions. Groups containing only keyframes or font faces are also retained, including nested groups, so references outside the group keep their definitions. Declaration-only unsupported blocks are dropped with a warning rather than aborting the export. System-font mode continues to omit custom font-face declarations. Semicolons inside parenthesized CSS functions, including unquoted data URLs, remain value text instead of ending a statement.

CSS grouping rules are scanned once and preserved without recursively rescanning nested bodies. Exports deeper than 1,024 nested CSS blocks fail with a clear diagnostic (CLI exit 2) before writing output.

`@scope` groups containing ordinary paint rules are refused with a clear exit-2 diagnostic before output is written; definition-only scopes retain their keyframes and font faces. `@layer` order statements remain in source order with their layer blocks, including inside grouping rules, so cascade priority is preserved.
The exporter keeps optional defs in comments namespaced so they can be uncommented later. Only referenceable defs element types have their IDs renamed; live titles and other elements retain their IDs and accessibility references.

Animation property names are compared after CSS escape decoding, while their authored spelling is preserved. Page styles and inline attributes keep their binding to namespaced keyframes, including `anim\61 tion` and vendor-prefixed properties. Nested animation declarations and SVG-local animation stylesheets remain unsupported and fail clearly, including escaped property names.

---

See [export.md](export.md) for standalone SVG export.
