# Line Chart Variants — Ridgeline, Streamgraph & Bump Chart

Quantitative chart variants for stacked distributions, breathing flow composition, and rank movement across ordered periods.

### Ridgeline
**Best for:** one **distribution** per series, stacked at a fixed pitch with deliberate overlap, when the shape of each distribution is the story and the series are directly comparable — request latency per service, build duration per pipeline, session length per cohort. The line chart above plots one value per x; a ridgeline plots a whole distribution per row, and the reading is the silhouette: where the mass sits, how tight it is, whether there is a second peak. A p50/p99 pair cannot show a bimodal service, and a box plot (the Scatter variant) flattens it to a rectangle.

Not for: a single distribution (that is a histogram — one ridge is a ridgeline with the comparison removed); series measured in different units or on different x-ranges, which cannot share the one x-scale the type requires; time series, where each row is one value per moment rather than one distribution; or distributions so similar that the ridges are five copies of one shape, which a table of percentiles says shorter.

#### Layout conventions

- **One baseline per ridge at a fixed pitch**, inside the `0 0 1000 500` viewBox the other Line variants use. The shipped example runs five baselines at `y` 152/208/264/320/376, a 56px pitch.
- **The x-run is the slopegraph's**, `x` 320 → 680, sampled at 13 bins 30px apart. The gutters are symmetric about it: names right-aligned ending at `x=304`, ranges starting at `x=696`, both 16px clear of the plot.
- **Name left of the baseline, range right of it**, each on its ridge's own row (`y = baseline + 3.5`). The range is the span of the ridge's nonzero mass in x-axis units, which is the number a silhouette cannot give you.
- **Bin ticks** in the `eyebrow` role at 11px at `y=400`, centred on bin positions and tracked `0.14em`, with the x-axis caption at `y=424`. The rotated amplitude caption sits at `x=24`, as in the parent chart.
- **Ridge count 3–12, bins 8–40.** Below three ridges there is no family of shapes to compare and two distributions are a pair of small multiples; past twelve the stack is taller than a reader can hold one silhouette in mind across. Below eight bins the outline is a histogram wearing a curve's clothes; past forty the bins are narrower than the noise in them.
- **Straight segments between bins, closed with `Z`.** Not splines: the source line states the drawing is unsmoothed, and a curve through binned counts puts extrema between bins that the sample never measured. The draft this variant came from permits Catmull-Rom with vertices on true values; the shipped grammar does not use it, because unsmoothed bins need no footnote about what the curve is allowed to invent.
- **No gridlines.** The baselines are the rules, and every ridge prints its own range.

#### Colour

The slopegraph's colour section holds here unchanged, with one addition for the fill. One accent on the editorially focal ridge (stroke `accent`, fill the accent at `0.16`), an `ink` opacity ramp for the rest (`0.80 → 0.62`, floor `0.53`) ordered top row to bottom, and focus carried by stroke weight — 2.4px against 1.2px — rather than tone. Labels stay `ink` (names) and `muted` (ranges) on every ridge including the focal one.

- **Fill `ink` at `0.12` on every non-focal ridge**, low enough that two overlapping ridges read as depth rather than as a third tone. This is the one place the type needs a fill at all: the outline alone does not say which side of the curve is mass.
- **Legend wording stays skin-neutral** — "strongest tone", never "darkest". The ramp is ink-at-opacity, so its top is the darkest line on light paper and the lightest on dark, and a legend that says "darker" ships false in one of the two skins while rendering perfectly in both.
- **The accent marks the ridge the story is about, not the worst performer.** In the shipped example it marks the service whose *shape* is unusual, not the slowest one.

#### Honest-data rule

**One amplitude on every ridge, stated in the source line.** That is the entire claim of the type: the ridges are stacked so their silhouettes can be compared, and per-ridge normalisation destroys exactly that while rendering beautifully — a rare, flat distribution given its own scale wears the same shape as a tight one. `scripts/verify-ridgeline.py` derives the figure's single amplitude and holds every vertex of every ridge to it.

- **The baseline never lies.** Each ridge declares the row it rises from, and that row must sit on the stack's fixed pitch with its rule drawn across the full bin run. A baseline nudged up to give one ridge headroom is the same falsification as a private amplitude, told with different arithmetic — and it is the harder one to see, because the silhouette above it is untouched.
- **Every ridge shares one x-scale.** A peak at one x means one latency on every row, or the column comparison the type exists for is fiction.
- **State the overlap, and keep it overlap.** Ridges are meant to intrude on the row above — that is how the stack reads as depth. A peak that reaches the row *two* above is occluded by the peaks it passes, and the fix is more pitch, never a smaller amplitude on one ridge. The checker enforces the ceiling; the source line states the amplitude so the reader can convert a height back into a number.
- **A ridge starts and ends on its own baseline.** The first and last bins are zero, so the outline closes along the baseline. A distribution clipped mid-mass draws a cliff, and a cliff reads as data.
- **No smoothing beyond what the footnote states.** The shipped grammar smooths nothing at all. If a figure ever does smooth, the footnote names the method and the vertices stay on true values — a spline that invents a second peak is indistinguishable, on the page, from a service that has one.
- **Height is share, not volume.** Each ridge is normalised to its own series' count before the shared amplitude is applied, so the tallest ridge is the most concentrated, not the busiest. Say so in the source line; a reader who assumes height is traffic reads the figure exactly backwards.

#### Declaring the values

The binding contract is the slopegraph's, applied to areas: the outline declares its bins and its baseline, and every visible string is bound to what it describes.

```svg
<line data-ridge="checkout-api" data-role="baseline" x1="320" y1="320" x2="680" y2="320" stroke="{ink @ 0.25}" stroke-width="1"/>
<path data-ridge="checkout-api" data-baseline="320" data-bins="0,1,6,17,21,14,8,6,7,9,7,4,0" d="M320,320 L350,317.6 L380,305.6 L410,279.2 L440,269.6 L470,286.4 L500,300.8 L530,305.6 L560,303.2 L590,298.4 L620,303.2 L650,310.4 L680,320 Z" fill="{accent @ 0.16}" stroke="{accent}" stroke-width="2.4" stroke-linejoin="round"/>
<text data-ridge="checkout-api" data-role="name" x="304" y="323.5" fill="{ink}" font-size="11" font-weight="600" font-family="{node-name}" text-anchor="end">checkout-api</text>
<text data-ridge="checkout-api" data-role="range" x="696" y="323.5" fill="{muted}" font-size="11" font-family="{sublabel}">40–440 ms</text>
<text data-tick="2" data-bin="240" x="500" y="400" fill="{muted}" font-size="11" font-family="{eyebrow}" letter-spacing="0.14em" text-anchor="middle">240</text>
```

`data-bins` is the basis of every geometric check, and it is this contract's own vocabulary: the slopegraph above binds `data-series` on a `<line>`, this variant binds `data-bins` on a `<path>`, and neither gate reads the other's attribute, so neither claims the other's file. Any further Line variant should take its own attribute for the same reason — a shared name means two checkers holding one figure to two contracts, and the one that loses rejects it for lacking elements it never said it had. `data-baseline` is what makes a moved row detectable; without it the checker would have to infer the zero from the drawing, which is the very thing being falsified. The printed range is cross-checked against the first and last nonzero bin through the figure's own tick scale, so a range widened by a word is a finding. `scripts/verify-ridgeline.py` covers the amplitude, the pitch, the baseline rules, the shared bins, the segment grammar, the overlap ceiling, the focus pairing and every label binding; `scripts/test-verify-ridgeline.py` proves each check in both polarities and pins the scope treaty with the sibling gates.

**No `transform` on any of it**, for the reason the slopegraph section gives: the checker reads raw coordinates, so a transform on an outline, a baseline rule, a bound label, an ancestor `<g>` or a CSS rule moves the rendered mark away from the bin that was verified. The rotated amplitude caption is fine — it is neither verified geometry nor a bound label.

#### Anti-patterns

- Per-ridge normalisation, or any second amplitude anywhere in the figure — the type's one unforgivable error.
- A baseline moved off the pitch to buy one ridge headroom, or a baseline rule drawn somewhere other than the row its ridge declares.
- Ridges sampled on different x-ranges, or an x-scale that is not printed at all.
- Smoothing that puts a peak between two bins, and any spline in a figure whose footnote says the drawing is unsmoothed.
- A ridge clipped mid-mass so the outline closes as a cliff.
- Pitch so tight that peaks hide behind peaks — increase the pitch, never shrink one ridge.
- One hue per ridge instead of the ink ramp plus a single accent.
- A legend that says "darker is faster", which is false on one of the two skins.
- Fewer than 3 ridges (that is a histogram or a pair of small multiples) or more than 12.
- Reading traffic off ridge height, or shipping a figure whose source line lets a reader do so.
### Streamgraph

**Best for:** how a total and its composition breathe across many periods — build minutes by pipeline, traffic by service, error budget by subsystem. The symmetric baseline makes the envelope the hero: the stream's height at any period *is* the total, and each layer keeps its share inside it. No other line form gives both at once — a plain multi-series line loses the total, a 100%-stacked area loses it on purpose.

Not for: exact per-period values (the reader gets shape, not numbers — use a **bar chart** or print a table); two or three periods (that is the parent line chart, or a **slopegraph**); a single series (the parent chart's area fill already does this against a zero baseline); or ranking stories (a bump chart reads rank, a stream reads volume).

#### Layout conventions

- **Period columns** evenly spaced across the plot, `x` 80 → 960 inside the `0 0 1000 500` viewBox — the parent chart's margins. The shipped example runs 12 weekly columns at 80px pitch. Budget: **3–24 periods, 2–6 layers**. Below 3 periods there is no flow to show; above 6 layers the ramp runs out of distinguishable tones.
- **Symmetric baseline at `y=230`**, the vertical middle of the 40 → 420 plot. Each period's stack is centred on it: envelope top and bottom always average back to the midline, so the silhouette is the total mirrored about a constant axis. The baseline is a *derived* line, not a drawn one — do not paint it.
- **One shared linear scale** for every layer at every period. The shipped example uses 1.25px per build-minute; state the scale or the bucket size in the source line so the reader can calibrate the envelope.
- **Boundaries are Catmull-Rom smoothed, control points at 1/6 chord, vertices on true values.** Smoothing bends only the *drawing between* periods; every on-curve vertex sits exactly where the stacked value puts it, which is what lets `scripts/verify-streamgraph.py` read the geometry back. Between-vertex overshoot near a sharp change is the honest cost of smoothing — never move a vertex to tame it.
- **Stack order is fixed for the whole figure, largest totals innermost** — the two biggest layers hug the midline, smaller ones ride the outer edges where the curvature is. Order never changes per period.
- **Layer boundaries get a 1px `paper` hairline** so adjacent tones separate where they run thin.
- **Period captions** in the `arrow-label` role at 11px, centred under each column at `y=440`, tracked `0.08em`.
- **No y-axis ticks and no gridlines.** The form is about the shape of the envelope; per-layer totals are printed in the legend, and a tick grid would invite reading precise values off a curve that cannot deliver them.
- **Annotate at most one landmark period** — a short hairline above the envelope and a mono label, as the shipped example marks the week the focal layer becomes the largest. More than one and the shape stops being the hero.
- **Legend keys are 16×8 rects** (area fills, like the parent chart), one entry per layer **with its total** — `Unit · 789 min`. The legend is where the numbers live. House rhythm as everywhere: rule at `y=462`, `LEGEND` at `478`, keys at `488` with text at `496`.
- **4px grid** applies to the designed constants — columns, caption baselines, legend rows. Boundary `y` values are data-scaled and exempt.

#### Colour

- **One accent layer — the editorially focal series — and an `ink` opacity ramp for the rest**, never the series palette. Layers are named in the legend, so hue would re-encode what the labels already say. The shipped ramp runs 0.78 → 0.30, **strongest tone on the largest layer**; adjacent tones in the stack need at least ~0.15 of separation or the hairline is doing all the work.
- Fills may run lighter than a line could: these are areas bounded by `paper` hairlines with no text on them, so the 3:1 stroke floor that binds the slopegraph ramp does not bind here. What does bind: every fill must still be `ink` at opacity (or `accent`), and no text ever sits on a layer.
- **Legend wording must be skin-neutral** — "strongest tone", never "darkest". The ramp inverts on dark paper.
- **Layer names must not contain digits.** The legend prints one number per entry (the total) and the checker refuses a label carrying two numeric tokens — `E2E` fails, `End-to-end` passes.

#### Honest-data rule

**The envelope is a claim about the total, and the layers are a claim about its parts.** Both are enforced by `scripts/verify-streamgraph.py` against the values each layer declares.

- **Zero-sum baseline, stated.** Every period centres on one midline — baseline = −total/2, the classic silhouette. Say so in the source line. A baseline that drifts per period to minimise wiggle re-orders what the eye reads as growth; a baseline pinned to the bottom is a stacked area wearing a costume. Neither is this type.
- **One scale, every layer, every period.** A layer drawn at its own scale makes its share a lie while the envelope stays plausible.
- **Zero periods stay in the domain — the pinch IS data.** The shipped docs pipeline runs nothing in weeks five and six, so its band pinches to zero thickness and reopens. Never bridge, resample, or drop a zero to prettify the flow.
- **No layer dropped silently.** Every drawn layer appears in the legend with its total, and every legend entry has a drawn layer. A stream that quietly loses a small series overstates every share that remains.
- **State the bucket size** (weekly, daily, per release) in the source line. Resampling to a coarser bucket smooths the story; the reader deserves to know which story they got.
- **Totals are sums, not typed numbers.** The legend total must equal the sum of the layer's declared per-period values — one number, three statements (values, geometry, print), zero chances to disagree.

#### Declaring the values

**Each layer's path declares its per-period values, and the drawn geometry must put every vertex where those values stack.** Same contract as the slopegraph: every meaningful visible string is bound to an attribute stating the same thing.

```svg
<!-- A layer: closed region, top boundary left-to-right, then bottom back.
     Absolute M/C/L/Z only; on-curve vertices at every period column. -->
<path data-layer="Docs" data-values="8,9,7,6,0,0,5,7,8,8,9,9"
      d="M 80 297.5 C … L 960 403.8 C … Z"
      fill="{ink @ 0.30}" stroke="{paper}" stroke-width="1"/>

<!-- Period captions: data-index places the column, data-period binds the text -->
<text data-period="W05" data-index="4" x="400" y="440" fill="{muted}" font-size="11" font-family="{arrow-label}" letter-spacing="0.08em" text-anchor="middle">W05</text>

<!-- Legend entries: data-total binds the printed per-layer total. The family is the
     node-name family at regular weight; swap in the active skin's sans stack. -->
<text data-layer="Docs" data-total="76" x="808" y="496" fill="{muted}" font-size="11" font-family="'Geist', sans-serif">Docs · 76 min · paused</text>
```

What the checker holds against those bindings: every layer's on-curve vertices sit at the shared period columns; per-period thickness matches `data-values` on one shared scale; layers tile with no gap or overlap; the envelope stays centred on one midline; control points sit where Catmull-Rom at 1/6 chord puts them (so the curve between vertices is determined by the vertices, not free to editorialise); each legend entry names its own layer and no other, and its total matches both its printed text and the sum of the declared values; and each period caption sits on its own column reading exactly its `data-period`. Paths must use plain absolute `M`/`C`/`L`/`Z` — anything else is refused rather than half-parsed, and **no `transform`** may touch a layer path, a bound label, or an ancestor group, for the same reason as the slopegraph: the checker reads raw coordinates.

#### Anti-patterns

- A wiggle-minimised baseline that reorders layers per period — the legend stops meaning anything.
- A bottom-pinned baseline presented as a streamgraph — that is a stacked area; the symmetric silhouette is the type.
- One hue per layer instead of the ink ramp plus a single accent.
- Y-axis ticks, or reading a precise value off a layer's thickness — totals live in the legend.
- Bridging or dropping zero periods, or resampling to a bucket the source line does not state.
- More than 6 layers (indistinguishable tones) or fewer than 3 periods (no flow to show).
- Text on a layer fill, or a layer name carrying digits.
- Moving a vertex off its true value to tame smoothing overshoot or open room for an annotation.
- A `transform` on a layer path, a bound label, an ancestor group, or in CSS.
- An unbound visible string: a period caption, a legend name or a legend total with no attribute stating the same thing. An entry printing one layer's name above another's `data-layer` satisfies every number in the figure and still hands the reader the wrong band.

### Bump chart

**Best for:** rank movement across **3–6 ordered snapshots** when position, not magnitude, is the story — package popularity by quarter, team standings by sprint, top queries by month. The slopegraph above shows two moments and keeps magnitude; a bump chart trades magnitude away entirely to show *several* moments of pure position. That trade is the type: the vertical axis is rank, every row is one rank apart, and a flat line means "nothing displaced it", not "nothing changed".

Not for: exactly two snapshots (that is the **slopegraph** above); magnitude stories — a series whose downloads doubled while its rank held draws a flat line, and if that surprise matters the reader needed a **line chart**; fewer than 4 series (a sentence is shorter) or more than 8 (spaghetti with a legend).

#### Layout conventions

- **One vertical axis rule per snapshot**, evenly pitched inside the plot, with the label gutters of the slopegraph: names right-aligned ending at `x=272` and first ranks at `x=304` on the left, mirrored from `x=696` (ranks) and `x=728` (names) on the right. The shipped example runs four axes at `x` 320/440/560/680 — the same 360px run as the slopegraph, spent in three segments instead of one.
- **Rank rows on a fixed pitch.** The shipped grid is `y = 88 + 56 × (rank − 1)`. Rank is ordinal, so — unlike the slopegraph, whose endpoint `y` values are data-scaled and grid-exempt — **every vertex lands exactly on the 4px grid**, and `scripts/verify-bump.py` enforces the row placement with no tolerance at all. There is no honest reason for a vertex to sit off its row.
- **Straight segments between adjacent snapshots, dots at every vertex** (`r=3`, focal `r=4`). Never splines: a curve between two quarterly snapshots draws a trajectory nobody measured. The draft this variant came from calls them subway curves and bans them outright.
- **Labels at first and last appearance** — name and rank (`#1`…`#6`, the sigil keeps a rank from reading as a magnitude) at both ends, each on its own series' row **and in the gutter outboard of the end it names**. Both coordinates are required and both are checked: the row says which series a label belongs to, the column says which *end* of it, and neither implies the other. A first-end label slid along its row into the plot prints every rank correctly and reads against the wrong snapshot.
- **Snapshot captions** in the `eyebrow` role at 11px, centred under each axis, bound with `data-axis` / `data-state` exactly as the slopegraph binds its two.
- **Series count 4–8, snapshots 3–6.** Two snapshots are a slopegraph; past six the columns compress until rank changes cannot be followed.
- **No gridlines.** The dots are the readable positions and the axis rules are the columns.

#### Colour

Everything the slopegraph's colour section says holds here unchanged: one accent on the editorially focal series, an `ink` opacity ramp (`0.80 → 0.62`, floor 0.53) for the rest — ordered by first-snapshot rank, so the legend can say "strongest tone was highest-ranked", skin-neutrally — focus carried by stroke weight (2.4px against 1.2px) and dot size rather than tone, and labels in `ink`/`muted` on every series including the focal one. The accent marks the series the story is about, never the winner: the shipped example spends it on the package that *fell*.

#### Honest-data rule

**State the ranking key and the tie-break in the source line.** Rank hides magnitude by design, so the footnote is where a reader learns what "first" means and why no two series ever share a row. `scripts/verify-bump.py` gates the geometry half: every snapshot's ranks must be a permutation of 1..N — a duplicated rank is a tie the stated tie-break cannot produce, and a skipped rank is an empty row the reader fills with a series that is not there.

- **If the ranking measure changed definition between snapshots, the chart is invalid** — ranks under different measures are not comparable, and no drawing convention repairs that.
- **A series that enters late or leaves early starts or stops.** A real gap is drawn as absence, never interpolated across. The shipped grammar has no way to *declare* a gap yet, so `verify-bump.py` requires every series to visit every snapshot — a series with fewer vertices than columns is a finding until a gap declaration exists, because widening the rule without one would let a truncated series pass as a deliberate exit.
- **Never smooth a tie into a crossing.** The tie-break decides the order; drawing anything else invents a rank.
- **Never nudge a vertex off its row** to dodge a label collision — it reads as a rank between two ranks, and the checker treats it as the lie it is.

#### Declaring the values

The binding contract is the slopegraph's, one level up: the path declares its ranks, and every visible string is bound to what it describes.

```svg
<path data-series="legacy-http" data-ranks="1,2,4,6" d="M320,88 L440,144 L560,256 L680,368" fill="none" stroke="{accent}" stroke-width="2.4"/>
<text data-series="legacy-http" data-end="first" data-role="name" x="272" y="91.5" fill="{ink}" font-size="11" font-weight="600" font-family="{node-name}" text-anchor="end">legacy-http</text>
<text data-series="legacy-http" data-end="first" data-role="rank" x="304" y="91.5" fill="{muted}" font-size="11" font-family="{sublabel}" text-anchor="end">#1</text>
<text data-axis="0" data-state="Q1" x="320" y="416" fill="{muted}" font-size="11" font-family="{eyebrow}" letter-spacing="0.14em" text-anchor="middle">Q1</text>
```

`data-ranks` is the basis of every geometric check, so a series whose labels go missing stays in the verified set and the missing label is itself reported. `scripts/verify-bump.py` covers the grid, the permutations, the segments, the dots, the focus pairing, the label bindings, label placement on both axes and the captions; `scripts/test-verify-bump.py` proves each check in both polarities. The gutter x is read off the figure — every label sharing an end and a role must agree on one column — so a resized plot needs no constant changed here.

## Examples

- `assets/example-line.html` — minimal light
- `assets/example-line-dark.html` — minimal dark
- `assets/example-line-full.html` — full editorial
- `assets/example-slopegraph.html` — slopegraph, minimal light
- `assets/example-slopegraph-dark.html` — slopegraph, minimal dark
- `assets/example-slopegraph-full.html` — slopegraph, full editorial
- `assets/example-ridgeline.html` — ridgeline, minimal light
- `assets/example-ridgeline-dark.html` — ridgeline, minimal dark
- `assets/example-ridgeline-full.html` — ridgeline, full editorial
- `assets/example-streamgraph.html` — streamgraph, minimal light
- `assets/example-streamgraph-dark.html` — streamgraph, minimal dark
- `assets/example-streamgraph-full.html` — streamgraph, full editorial
- `assets/example-bump.html` — bump chart, minimal light
- `assets/example-bump-dark.html` — bump chart, minimal dark
- `assets/example-bump-full.html` — bump chart, full editorial

---

See [type-line.md](type-line.md) for standard line charts and slopegraphs.
