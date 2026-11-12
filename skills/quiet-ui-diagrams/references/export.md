# Export to PNG / SVG

Convert a generated diagram HTML file into a portable `.svg` and/or `.png` next to it. **Manual only — never run unprompted.**

## Trigger

Load this file when:

- The user invokes `/quiet-ui-diagrams:export-diagram <html-file>` (the plugin's slash command — defined in `commands/export-diagram.md` at the repo root).
- The user asks in natural language to export, save, rasterize, convert, or download a diagram in `.svg` or `.png` form. Typical phrasings:
  - "export this as PNG"
  - "save as SVG"
  - "give me a PNG of that diagram"
  - "rasterize it"
  - "convert to png and svg"

The slash command is a thin wrapper that delegates here — both paths run the same procedure below.

## Scope

Both formats are **diagram-only** — just the `<svg>` node. Editorial wrappers (header, summary cards, footer in `-full` variants) are intentionally dropped: the export deliverable is the diagram itself, suitable for Figma, slides, social cards, or blog images.

The SVG-only export keeps the source `<title>` and `<desc>` with the diagram. Their per-diagram and per-variant prefixed IDs keep accessible names unique when several figures share a page.

Inlining several exported SVGs in one host document also requires namespaced `<defs>` IDs (markers, patterns, gradients, filters, clip paths, masks, symbols). The export procedure prefixes those IDs with the source file slug and rewrites matching `url(#…)` / `href="#…"` references, so a light figure next to its `-dark` twin does not silently share arrowheads. The accessible-name guarantee alone is not enough.

If the user explicitly asks for "a screenshot of the whole page including the cards", that's a different request — fall back to a normal full-page screenshot via the user's OS or browser.

## SVG export procedure

**Prefer the packaged helper.** From this skill's directory run:

```
python3 scripts/export_svg.py <html-file> [<out.svg>] [--system-fonts]
```

`--system-fonts` skips the Google Fonts `@import` and carried `@font-face` declarations (step 5) so the SVG makes no network request; use it when the skin's font source is `system` (see [style-guide.md § Font source](style-guide.md#font-source)). The diagram CSS still carries over.

Source read and output write failures return exit 2 with an error diagnostic. The viewport must contain four finite SVG numbers with positive width and height; empty or disabled viewports are refused. The class-without-style gate inspects nonempty actual `class` attributes; comments, visible text, empty class values, and `data-class` metadata do not require a stylesheet. Export selects a live SVG and carries live style blocks; HTML comments and script literals do not contribute diagrams or CSS. The selected SVG ends at its own closing tag, so nested icon `<svg>` elements stay inside it. Comments inside the selected SVG remain intact, except that XML forbids `--` inside a comment and a comment ending in `-`: each `--` becomes `- -` and a trailing `-` gets a space. That script is the source of truth for the transform below (CSS carry-forward, defs ID namespacing, rgba normalization, and the class-without-style gate). Reimplement only when the helper is unavailable; keep the behaviour identical.

Numeric character references in text and attributes follow HTML decoding, including decimal/hexadecimal forms without a semicolon and the `&#128;` → `€` mapping. Escaped references are decoded once; comments, CDATA and raw style/script bodies are not decoded by this normalization. Characters that XML cannot represent fail export rather than being silently removed.

### Manual algorithm (what the helper does)

1. Read the source HTML file.
2. Extract the **first** top-level `<svg ...>...</svg>` element. Skip HTML comments, `<script>` and `<style>` content, then count `<svg` openings and `</svg>` closings (a self-closing `<svg .../>` does not open one) and stop when the count returns to zero. Read quoted attribute values whole so a `>` or `/>` inside one does not end the tag. A non-greedy regex stops at a nested icon's `</svg>` and truncates the diagram. Most generated diagrams have only one top-level SVG; if there are multiple, the first is the diagram (gallery files are an exception — see *Edge cases*).
3. Make it standalone:
   - Ensure the opening tag has `xmlns="http://www.w3.org/2000/svg"`. Add it if missing. The SVG namespace must belong to the root SVG element; a namespace on a descendant does not satisfy it. An explicit incompatible root namespace is refused.
   - Ensure a `viewBox` is present. The skill's templates always include one; warn the user if absent rather than guessing.
   - Preserve `role="img"`, `aria-labelledby`, and the first-child `<title>` / `<desc>` exactly as authored.
   - Rewrite HTML-only attribute syntax as XML: a valueless attribute (`<g data-motion-item>`) becomes `data-motion-item=""`, and an unquoted value gets double quotes. Known named HTML character references in labels and attributes become equivalent XML-safe text (for example, `&nbsp;` becomes a nonbreaking space). HTML's legacy names such as `&copy` and `&nbsp` also decode without the semicolon, except inside an attribute value when the next character is a letter, digit, or `=`, as browsers do. Decode once and escape XML delimiters; already escaped references remain escaped. Comments, CDATA and raw style/script content stay as written; style/script opening-tag attributes follow the same reference conversion as other attributes.
   - Make comments valid XML. Inside each `<!-- ... -->` outside CDATA, turn every `--` into `- -` and add a space after a body that ends in `-`. Refuse a comment that a browser closes before the next `-->` (`<!-->`, `<!--->`, or one containing `--!>`): the markup after it is live, and rewriting the comment would hide it.
   - Set `id="<slug>-root"` on the opening `<svg>` tag, where `<slug>` is the source basename without extension (e.g. `example-loop.html` → `example-loop`). This ID scopes carried CSS so several inlined figures do not leak rules into each other. When replacing an existing SVG root ID, retarget whole CSS ID tokens for that root in the carried CSS, including escaped identifier spellings; compound selectors such as `.diagram#original` remain bound to the root without adding another ancestor. Descendant IDs and quoted selector values remain unchanged; an unescaped dot belongs to a class selector, not to the ID token.
4. **Carry page CSS into the SVG.** Class-styled diagrams (the loop family, process, medallion, data-flow, and others) declare fills and type in the page `<style>` block — `.station`, `.hub`, `.node-name`, and so on. Extracting the bare `<svg>` without those rules yields black boxes. Copy the page's diagram rules into a `<style>` inside `<defs>`, then:
   - Unwrap CDATA sections in SVG stylesheet text before parsing rules, then strip real CSS comments, so neither XML delimiters nor a comment becomes part of a selector. Preserve comment-looking text inside quoted strings and escapes: `[data-label="net/*retained*/revenue"]` must still match the original attribute value. Keep CDATA content as raw text rather than XML-decoding it; the carried copy is XML-escaped below. The original embedded stylesheet stays in the SVG. CDATA-looking text in an HTML stylesheet remains literal, including inside SVG `foreignObject`, `desc`, or `title` elements. A nested `<svg>` inside HTML switches back to SVG stylesheet handling.
   - Keep diagram rules inside their original `@media` conditions, including nested conditions; print-only paint must not become screen paint. Keyframe bodies remain intact; ordinary identifier names (also quoted) and matching stylesheet/inline `animation` or `animation-name` bindings are prefixed with the SVG root ID so inlined figures cannot share an animation name. Inline style character references are decoded once before inspecting CSS names and escaped once when written as XML; declaration comments are preserved. A custom property's `{ … }` value is token data and stays literal, including any `animation` text inside it. Duration variables with a literal animation name remain supported. Escaped/complex names, unresolved variable animation names, ambiguous shorthand keyword names, SVG-local animation stylesheets, and nested ordinary-rule animation declarations bound to renamed keyframes are refused explicitly rather than silently retargeted. These unsupported animation cases return exit 2 without writing an SVG. Block at-rules containing ordinary rules, including `@layer` and `@container`, retain their grouping and scoped paint. Unsupported declaration-only blocks are dropped with a warning; stray closing braces between rules are ignored, matching browser CSS recovery.
   - Re-scope `:root { … }` custom properties onto `#<slug>-root` so the figure keeps its own tokens.
   - Start selectors that begin at the `<svg>` element at the root instead: `svg .zone` becomes `#<slug>-root .zone` and `svg text` becomes `#<slug>-root text`. The exported root element is the `<svg>` itself, so `#<slug>-root svg .zone` would match nothing.
   - Split selector lists only at top-level commas. Preserve quoted and escaped attribute values, function arguments, and meaningful whitespace while scoping.
   - Prefix every other kept selector with `#<slug>-root ` (e.g. `.station` → `#example-loop-root .station`).
   - **Drop** page chrome: `*`, `html`, `body`, `main`, `h1`/`h2`/`h3`, `p`, `.frame`, `.eyebrow`, `.summary`, `.card(s)`, `.footer`, `.header`, and the bare `svg { min-width: … }` layout rule. Only the bare `svg` selector is layout; `svg .zone` and `svg text` are diagram rules (see above). Those must not follow a fragment.
   - Carry `color` and `font-family` from the dropped `body` rule onto `#<slug>-root`. SVG content inherits both: `stroke="currentColor"` reads `color`, and text without its own font rule reads `font-family`.
   - **XML-escape** the carried CSS text (`&` → `&amp;`, `<` → `&lt;`) before inserting it into the SVG. Rule bodies can contain XML-sensitive characters (e.g. `content: "R&D"`); a bare `&` makes the standalone file fail to parse.
5. Inject Google Fonts `@import` so the SVG renders with correct typography in a browser. **XML-escape the `&` separators as `&amp;`** — a standalone `.svg` is parsed as strict XML, where a bare `&` starts an entity reference and makes the whole file fail to parse. (Don't copy the raw URL from the HTML `<link href>`; that ampersand form is only valid in HTML.) Merge into the same `<defs>` `<style>` as the carried rules (don't add a second `<defs>`). If a new `<defs>` is needed, insert it after the existing leading `<title>` and `<desc>` so the first-child accessible-title contract is preserved:
     ```svg
     <defs>
       <style>@import url('/* Offline Font Stacks: Inter, Newsreader, JetBrains Mono */');
       /* …scoped diagram rules… */
       </style>
       <!-- existing markers / patterns stay here -->
     </defs>
     ```
6. **Namespace `<defs>` IDs.** Prefix every referenceable defs ID — on `marker`, `pattern`, `linearGradient`, `radialGradient`, `filter`, `clipPath`, `mask`, `symbol`, and reusable graphics (`g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `text`, `image`, and `use`) — with `<slug>-`, and rewrite matching `url(#…)` and `href="#…"` / `xlink:href="#…"` references. Compare ID and fragment values after XML character-reference decoding, so equivalent named and numeric references stay connected. For recognized local CSS URL forms (literal `url(...)`, case-insensitive) in paint/reference attributes, inline styles, and stylesheets, decode hex escapes before comparing fragment identity, and preserve the original escape spelling when adding the prefix; `url(#\70 aint)` must stay connected to the namespaced `paint` definition. URL-looking metadata and quoted CSS string contents remain literal. Retarget ID selectors in embedded style rules while leaving declaration colors and unrelated IDs unchanged. Preserve URL quotes and match fragment IDs case-sensitively (the CSS `url` keyword remains case-insensitive). Rewrite **longest-id-first** so `arrow-accent` is not clipped by a shorter `arrow` rule. Quoted local URLs (`url("#arrow")`, `url('#arrow')`, including XML-escaped quotes in attributes) follow the same rewrite as unquoted URLs. Unrelated fragment IDs and non-local URLs remain unchanged. Example: `id="arrow"` in `example-loop.html` becomes `id="example-loop-arrow"` with `marker-end="url(#example-loop-arrow)"`.
7. Normalize colors for strict SVG 1.1 consumers. This design system's tokens are authored as `rgba(...)` (see `style-guide.md`) and render correctly wherever colors are read as CSS — browsers, Figma, Illustrator. Older presentation consumers may misinterpret rgba fills. The exporter normalizes presentation paint (`fill="..."` and `stroke="..."`) to hex plus `fill-opacity` / `stroke-opacity` attributes while preserving CSS cascades and descendant rules (implemented in `scripts/export_svg.py`).

8. **Gate:** if the exported SVG still contains `class=` but no diagram CSS rules, stop and fix the CSS carry step — that fragment will render as black boxes. A fonts-only `<style>` (Google Fonts `@import` with no rules) does **not** satisfy the gate.
9. Prepend `<?xml version="1.0" encoding="UTF-8"?>\n` so the file is well-formed XML.
10. Write to `<basename>.svg` next to the source (e.g. `example-architecture.html` → `example-architecture.svg`). Honour an explicit output path if the user provides one.

### Caveat to surface to the user

Tools that don't fetch remote fonts at import time (offline Illustrator, some Figma import paths, older SVG viewers) will substitute typography. The SVG renders correctly in any modern browser. For pixel-perfect portability, recommend the PNG export.

---

## PNG Export

For raster PNG generation with headless Chrome / Selenium (`--headless=new`), see [export-png.md](export-png.md).
