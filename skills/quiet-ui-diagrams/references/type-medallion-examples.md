# Medallion Architecture — Connectors, Overrides & Examples

Companion reference for medallion lakehouse diagrams covering connectors, color overrides, and worked examples.

## 3. Connector rules (mandatory)
Three styles, bound to topology. Mirror §3 of `type-process.md` so the rule reads identically.

```svg
<defs>
  <marker id="arrow"        markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{muted}"/></marker>
  <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{accent}"/></marker>
  <!-- Per-color markers: declare one per custom tier color in use. -->
  <marker id="arrow-yellow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#c9a23a"/></marker>
</defs>
```

Add a new `<marker>` for each `color` override used in the diagram. Naming convention: `arrow-{semantic}` (e.g., `arrow-yellow`, `arrow-slate`, `arrow-red`) — matches the recommended palette so the marker id reads cleanly in source.

**Z-order:** promotion arcs draw **before** any tier card rect, so the cards layer on top and any arc overshoot is masked inside the cards.

**Arc shape rule:** medallion promotions are always **cubic arcs over the top** of the tier strip, anchored at the **top-center** of source and target tiers; control points directly above anchors at y=0. No horizontal "through the gap" lines — the arc-over-top is what makes connector + label both clearly visible.

---

## 4. Component color override

Any tier or path entry accepts an optional `color: "#hex"`. Mirrors `type-process.md` §4 / `type-data-flow.md` §4.

### 4.1 Per-tier `color`

Applied to:

| Element | Light | Dark |
|---|---|---|
| Card fill | `rgba(C, 0.07)` | `rgba(C_light, 0.10)` |
| Card stroke | `C` (width 1.4) | `C_light` (width 1.4) |
| Header band fill | `rgba(C, 0.14)` | `rgba(C_light, 0.18)` |
| Title text | ink (unchanged — title stays readable) | ink (unchanged) |
| Bucket text | `C` | `C_light` |
| Example values | `C` | `C_light` |
| Field labels / field values | **unchanged** (ink / muted) | **unchanged** |
| Connectors touching this tier | **unchanged** — topology-driven | **unchanged** |

`C_light` = the same hex lightened ~15% for dark-mode contrast.

### 4.2 Per-path `color`

Replaces the path card's stroke with `rgba(C, 0.45)` and the tag chip stroke with `rgba(C, 0.55)`. Tag text and title text use `C`. Sub stays muted.

### 4.3 Rules

- **Never on focal tiers.** The accent already carries that signal — a `color` on the focal tier is ignored.
- **Never on the `cold` tier in addition to its dashed treatment.** Pick either dashed-cold or a custom color, not both.
- **Cap at 2 custom-colored elements** per diagram (tier or path), in addition to the focal tier.
- **Promotion arrows inherit the target tier's color** (§3 auto-style rule). A `color: "#c9a23a"` on the Staging tier means the CLEAN+WEIGHT arc landing in Staging is also rendered in yellow — connector, label, and arrowhead match. This keeps visual coherence: the colored tier and its incoming flow read as a single "concern" group. Arrows do **not** inherit color from the source tier — only the target — so the arc *out of* a colored tier reverts to muted (or to the next target's color/style).

### 4.4 Semantic palette (recommended)

Same palette as the other parametric types so a reader scanning multiple diagrams sees the same colors meaning the same thing:

- `#b85450` rust-red — Security / Identity / Governance (PII-bearing tiers, audit tiers)
- `#5a7d9a` slate-blue — Observability / Quality (validated tiers, monitored zones)
- `#7a8c47` olive-green — Data Products / Publication (consumer-facing aggregates, public-release tiers)
- `#c9a23a` warm yellow / gold — Analytical / Working zones (staging tier, scientist sandbox, intermediate computation surface)
- `#8c6d3f` warm-brown — Backup / DR / Archive (alternative cold-tier styling)

---

## 5. Focal rule

Exactly **one** focal tier per diagram. Defaults to the tier marked `focal: true` in inputs; if none is marked, defaults to the analytical pivot tier (typically `Aggregated` or whichever tier downstream consumers query).

The focal tier:
- Uses `style: focal` (accent fill + stroke 1.6 + accent header band).
- Renders bucket text and example-value lines in accent.
- Has its **incoming** promotion arrow auto-promoted to `style: focal` (accent).
- Has its **outgoing** promotion arrow (if any) — typically into the cold archive — kept at the user-declared style (usually `lifecycle` dashed).

If zero or >1 tiers carry `focal: true`, halt and ask the user.

---

## 6. Dark mode

| Token | Light | Dark |
|---|---|---|
| Paper | `paper` | `ink` |
| Ink | `ink` | `paper` |
| Muted | `muted` | `soft` |
| Accent | `accent` | `accent` |
| Fog (cold tier fill) | `paper-2` | `paper @ 0.06` |
| White (default card fill) | `#FFFFFF` | `paper @ 0.04` |
| Card stroke ink (default style) | `ink` | `paper @ 0.30` |
| Header band ink-tint | `ink @ 0.06` | `paper @ 0.08` |
| Header band muted-tint | `muted @ 0.10` | `soft @ 0.16` |
| Header band cold-tint | `muted @ 0.18` | `soft @ 0.24` |
| Header band accent-tint | `accent @ 0.14` | `accent @ 0.20` |
| Custom component colors | `C` | `C_light` (lighten ~15%) |

---

## 7. Reproducibility checklist (taste gate)

Before emitting SVG, verify **every** item:

1. `viewBox = "0 0 {viewBox_w} {viewBox_h}"` derived via §2 (5 tiers + 2 paths → 1040 × 548).
2. Each tier card at `(tier_x(i), 80)` size `172 × 380`, `rx=6`.
3. Tier header band fills `(tier_x(i), 80, 172, 40)` plus a 10-px extension under the band.
4. Exactly **one** focal tier; its incoming arc auto-styled to `focal`.
5. Promotion arcs render as cubic Béziers over the top of adjacent tiers; anchors at `(tier_cx(i), 80)` → `(tier_cx(i+1), 80)`, controls at y=0. Label inside the arc at `(arc_peak_x, 50)`, no mask.
6. Bottom path row only present when `len(paths) > 0`. Cards at `y=476`, height 56.
7. Custom component colors ≤ 2 in addition to the focal tier. Never on arrows.
8. All promotion arrows + label masks emitted **before** any tier rect (z-order rule — cards mask the line ends inside the cards).
9. The focal tier's bucket text and example values render in accent; the rest stay muted.
10. `rx=6` on every tier and path card; `rx=2` on tag chips.

---

## 8. Anti-patterns

- **More than one focal tier** — focal exists to mark the central analytical surface; >1 erases the signal.
- **Cold styling on a non-archive tier** — the dashed fog look is reserved for retention/archive tiers.
- **Bidirectional promotion arrows** — promotions always flow left → right. Backflow (e.g., an aggregate writing back to raw) is wrong for this type; use a different diagram.
- **Custom-colored arrows** — connectors are topology-driven; color on a tier never spreads to its edges.
- **Path cards explaining tier semantics** — paths describe *write methods* (how data moves between tiers), not what each tier holds. If you find yourself writing "Raw stores …" in a path card, that content belongs in the Raw tier's fields.
- **Missing `example_label` content** — every tier should show a concrete example payload (quarterly survey rows, customer records, claims, …). Without it the diagram becomes abstract and stops earning its space.
- **Promotion arrow label longer than the tier-gap label mask** — keep labels to ≤ 14 chars in the uppercase `arrow-label` role. Long verbs ("CALCULATE & SUMMARIZE") break the rhythm; shorten to "AGGREGATE" or split into two diagrams.

---

## 9. Examples

- `assets/example-medallion.html` — minimal light (NatStat quarterly survey: 5 tiers, 2 path cards, Aggregated focal). Gallery default.
- `assets/example-medallion-dark.html` — same, dark skin.
- `assets/example-medallion-full.html` — same, editorial-card frame with subtitle + summary cards.

---

## 10. Worked YAML

The YAML in §1 is the **complete** inputs definition for the shipped `example-medallion.html`. Every coordinate in that file's SVG is derivable from §2 applied to those inputs. The same YAML is embedded as a top-of-file HTML comment inside `example-medallion.html` so source view shows the parametric inputs immediately above the SVG.

---

See [type-medallion.md](type-medallion.md) for inputs schema and layout formulas.
