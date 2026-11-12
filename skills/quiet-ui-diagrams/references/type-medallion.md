# Medallion

**Best for:** documenting a multi-tier data-storage layout where each tier is a distinct *quality / access level* of the same dataset — typically raw landing zone, anonymised, staging/cleaned, aggregated business indicators, and cold archive. Used when the reader needs to see at a glance *what each bucket contains*, *who writes it*, *with what tool and format*, and *how data is promoted between tiers*.

Prefer **Process** if the subject is a workflow with role lanes. Prefer **High-Level** if the subject is the cluster architecture rather than the storage tier organisation.

This type is **parametric** — the inputs schema in §1 drives every coordinate via the formulas in §2. Two generations from the same inputs must produce visually identical SVG. The rule shapes mirror `type-process.md` and `type-data-flow.md` so color override, focal rule, and reproducibility checklist read identically across types.

---

## 1. Inputs — the parameter contract

```yaml
title:    "Five-Tier Medallion Architecture"
subtitle: "Quarterly survey through Raw → Anonymized → Staging → Aggregated → Archive"

tiers:                                # 3..6 tier columns, ordered left → right
  - { name: "Raw",        bucket: "raw-bucket",        style: "outer",
      fields: { tool: "NiFi · raw write",          format: "CSV · Parquet · JSON", writer: "Data Engineer",
                example: ["Q1 dump · w/ PII", "verbatim CAPI export"] } }
  - { name: "Anonymized", bucket: "anon-bucket",       style: "default",
      fields: { tool: "Trino INSERT",              format: "Iceberg · partitioned", writer: "Data Engineer",
                example: ["no name · address", "stable household ID"] } }
  - { name: "Staging",    bucket: "staging-bucket",    style: "default",  color: "#c9a23a",   # warm yellow — analytical working zone
      fields: { tool: "Trino · JupyterHub",        format: "Iceberg · cleaned",     writer: "Data Scientist",
                example: ["weighted records", "harmonised codings"] } }
  - { name: "Aggregated", bucket: "aggregated-bucket", style: "focal",  focal: true,
      fields: { tool: "Trino INSERT · SAS JDBC",   format: "Iceberg · indicators",  writer: "Data Scientist",
                example: ["unemployment rate", "labour participation"] } }
  - { name: "Archive",    bucket: "archive-bucket",    style: "cold",
      fields: { tool: "MinIO lifecycle",           format: "cold tier · immutable", writer: "Data Administrator",
                example: ["historical Q1–Q4 sets", "5+ years retained"] } }

example_label: "Quarterly survey example" # bottom field label (varies per domain)

promotions:                           # adjacent-tier arrows; len = n_tiers - 1
  - { from: 0, to: 1, label: "PII REMOVE",    style: "normal"    }
  - { from: 1, to: 2, label: "CLEAN+WEIGHT",  style: "normal"    }
  - { from: 2, to: 3, label: "AGGREGATE",     style: "focal"     }    # auto-accent because target is focal
  - { from: 3, to: 4, label: "LIFECYCLE",     style: "lifecycle" }    # dashed

paths:                                # 0..2 write-method cards at the bottom (optional)
  - { tag: "SQL PATH",      title: "Trino INSERT INTO … SELECT",
      sub: "filter · reshape · join · aggregate — set-based transforms" }
  - { tag: "NOTEBOOK PATH", title: "DuckDB + Python/R in JupyterHub",
      sub: "stats · ML · interactive analysis — row-iterative work" }

dark: false
```

**Reserved field semantics:**
- `tiers[i].style` — one of `outer`, `default`, `focal`, `cold`. Drives the card's fill/stroke palette (§2.4).
- `tiers[i].focal: true` — exactly **one** tier may declare this. Overrides `style` to `focal` and switches the promotion arrow *into* this tier to `focal` automatically.
- `tiers[i].fields` — `{tool, format, writer, example}`. `example` is a 1- or 2-item list; the section heading uses `example_label`.
- `tiers[i].color` — optional `"#hex"` per-tier color override. See §4.
- `promotions[].style` — `normal` | `focal` | `lifecycle`. The connector rule (§3) binds each style to fixed stroke / dash / marker.
- `paths` — 0–2 entries. When 0 entries, the bottom row is omitted and `viewBox_h` shrinks accordingly.

---

## 2. Layout formulas — deterministic geometry

```
# Tier dimensions
tier_w           = 172
tier_h           = 380
tier_gap         = 16
left_pad         = 16
right_pad        = 100
n_tiers          = len(tiers)

# Canvas
viewBox_w        = left_pad + n_tiers * tier_w + (n_tiers - 1) * tier_gap + right_pad
                                                    # 5 tiers → 16 + 860 + 64 + 100 = 1040
arc_band_h       = 80                               # space above tiers reserved for promotion arcs
path_h           = 56
path_gap         = 16                               # gap between tier row and path row
bottom_pad       = 16
viewBox_h        = arc_band_h + tier_h + (path_gap + path_h if paths else 0) + bottom_pad
                                                    # with paths → 80+380+72+16 = 548
                                                    # without paths → 80+380+16 = 476

# Tier positions
tier_x(i)        = left_pad + i * (tier_w + tier_gap)    # 16, 204, 392, 580, 768
tier_y           = arc_band_h                            # 80 — tier tops sit just below the arc band
tier_cx(i)       = tier_x(i) + tier_w/2                  # 102, 290, 478, 666, 854

# Promotion arcs (between adjacent tiers — over the top, anchored at tier top-centers)
arc_src_x(i)     = tier_cx(i)                            # top-center of tier i      (102, 290, 478, 666)
arc_dst_x(i)     = tier_cx(i+1)                          # top-center of tier i+1    (290, 478, 666, 854)
arc_peak_x(i)    = (arc_src_x(i) + arc_dst_x(i)) / 2     # midpoint                  (196, 384, 572, 760)
arc_label_y      = 50                                    # label sits inside the arc, 30px below tier top

# Path row (bottom)
path_y           = tier_y + tier_h + path_gap            # 476
path_w           = (viewBox_w - 2*left_pad - path_gap) / 2 if len(paths) == 2 else (viewBox_w - 2*left_pad)
                                                          # Canonical 5-tier shape uses path_w=460 explicitly (see §2.5)
```

### 2.1 Background

Solid paper fill across the full viewBox. No dot pattern.

### 2.2 Tier card (172 × 380)

Each tier renders as a rounded-rect card with a tinted header band, a centered bucket name, four labeled field rows, and a separated `example_label` section near the bottom.

```
tier_x(i),  tier_y       =  card top-left  (tier_y = 80, just below the arc band)
header_band_h            = 40            # band from y=tier_y to y=tier_y+40 (i.e., 80..120)
header_band_extra        = 10            # 10-px extension below band, same tint

# Inside the card (absolute y; tier_y = 80):
title_text            at (tier_cx(i), 106)                # node-name role, 13px, weight 700, ink
bucket_text           at (tier_cx(i), 144)                # sublabel role, muted (accent on focal tier)

field_x               = tier_x(i) + 16                    # 16-px left inset for field text
field_w               = 140                               # 172-px tier_w minus two 16-px insets
field rows (absolute y):
  tool_label  at 180,    tool_value  at 186 (foreignObject, height 24)
  format_label at 220,   format_value at 226 (foreignObject, height 24)
  writer_label at 260,   writer_value at 266 (foreignObject, height 24)
  # gap (open whitespace below writer row, above the example section)
  example_label_text at 360,  example_line_0 at 374,  example_line_1 at 388
```

**Field-value wrapping rule:** field values (tool / format / writer) render inside an SVG `<foreignObject>` with an HTML `<div>` so they auto-wrap when text exceeds 140 px. Each `foreignObject` is 140 wide × 24 tall (fits 2 lines in the `sublabel` role at 1.25 line-height). The 26-px gap to the next field's label absorbs the second line cleanly.

```svg
<foreignObject x="{field_x}" y="{value_top}" width="140" height="24">
  <div xmlns="http://www.w3.org/1999/xhtml"
       style="font-family: {sublabel}; color: {muted}; line-height: 1.25;">
    {field_value}
  </div>
</foreignObject>
```

The HTML namespace declaration on the `<div>` is required for SVG to render the inline content. Browsers and Selenium headless Chrome/Chromium render this faithfully; if your export target doesn't support `<foreignObject>` (some older Inkscape builds), hand-split long values into two `<tspan>` lines instead.

Field labels use the `node-name` role at 11px in ink. Field values use the `sublabel` role in muted. Bucket and field values can be retinted by `color` override (§4).

### 2.3 Tier styles

Four canonical styles, picked per tier via `tiers[i].style`. Default mapping if `style` is omitted: tier 0 → `outer`, last tier → `cold`, focal tier (if any) → `focal`, others → `default`.

| `style` | Card fill | Card stroke | Header band fill | Bucket text | Example value text |
|---|---|---|---|---|---|
| `outer` | `#FFFFFF` | `muted` 1.0 solid | `muted @ 0.10` | `muted` | `muted` |
| `default` | `#FFFFFF` | `ink` 1.0 solid | `ink @ 0.06` | `muted` | `muted` |
| `focal` | `accent @ 0.07` | `accent` 1.6 solid | `accent @ 0.14` | `accent` | `accent` |
| `cold` | `paper-2` | `muted` 1.0 dashed `5,3` | `muted @ 0.18` | `muted` | `muted` |

`rx = 6` on all card rects.

**Focal styling note:** the focal tier's accent treatment cascades — its bucket text and its example-value lines render in accent. Other field values (tool/format/writer) stay muted; only the bucket name and the example payload carry the focal signal so the tier card doesn't fully drown in coral.

### 2.4 Promotion arcs (over the top of the tiers)

Each promotion is a **cubic Bézier arc** anchored at the **top-center** of each adjacent tier — `(tier_cx(i), tier_y)` to `(tier_cx(i+1), tier_y)`. The arc rises into the 80-px `arc_band` above the cards, peaking at y ≈ 20. Both the connector and its label remain fully visible — no paper masks, no overlap with card content.

```svg
<path d="M {tier_cx(i)},{tier_y} C {tier_cx(i)},0 {tier_cx(i+1)},0 {tier_cx(i+1)},{tier_y}"
      fill="none" stroke="…" stroke-width="…" marker-end="…"/>
```

Concrete for the canonical 5-tier shape (`tier_y = 80`, tier centers at x = 102, 290, 478, 666, 854):
- 0→1: `M 102,80 C 102,0 290,0 290,80`
- 1→2: `M 290,80 C 290,0 478,0 478,80`
- 2→3: `M 478,80 C 478,0 666,0 666,80`  (focal — accent)
- 3→4: `M 666,80 C 666,0 854,0 854,80`  (lifecycle — dashed)

The cubic geometry: anchor y = 80 (tier top), control y = 0 (top of viewBox). Curve peak at t=0.5 sits at y ≈ 20 (computed from `0.125·80 + 0.375·0 + 0.375·0 + 0.125·80 = 20`). Each arc spans one full tier-stride (188 px on the canonical layout), giving the connector a clearly visible vertical excursion.

**Marker orientation:** `marker-end` with `orient="auto"` rotates the arrow to match the path tangent at the endpoint. The control point sits directly above the anchor so the tangent at landing is straight **down** — the arrowhead enters the top-center of tier *i+1* cleanly, pointing into the header band.

**Chained anchors:** consecutive arcs share their meeting points (arc 0→1 ends at the same `(tier_cx(1), 80)` where arc 1→2 begins). Visually each tier's top-center acts as a "joint" — data arrives at the top of the card, gets transformed inside, and leaves out the top toward the next tier. The arrow-head plunge plus the next arc's straight-up emergence read as a single payload-handoff motion.

| `style` | Stroke | Width | Dash | Marker |
|---|---|---|---|---|
| `normal` | `muted` | 1.4 | — | `arrow` |
| `focal` | `accent` | 1.6 | — | `arrow-accent` |
| `lifecycle` | `muted` | 1.4 | `4,3` | `arrow` |

**Auto-style rules:**
- If `promotions[k].to` references the **focal tier**, the style auto-promotes to `focal` (accent, width 1.6, `arrow-accent` marker).
- If `promotions[k].to` references a tier with a **`color` override** (§4), the arrow inherits that hex — stroke = `C`, label fill = `C`, marker-end uses a color-matched marker (e.g., `arrow-yellow` for `#c9a23a`). Width stays at 1.4 — the color override is a "concern" signal, not a focal promotion. Lifecycle/dashed arrows keep their dash but adopt the color.
- Focal wins if both apply (a colored tier marked focal still uses accent).

**Label inside the arc:**
- Anchored at `(arc_peak_x(k), arc_label_y)` = `((arc_src_x + arc_dst_x) / 2, 50)`.
- `arrow-label` role at 11px with `letter-spacing=0.08em`, uppercase. Color matches the arrow stroke.
- **No mask rect needed** — the cubic curve peaks at y ≈ 20 and the label sits at y=50, well below the curve. The label floats inside the open space *enclosed* by the arc, reading "X transforms into Y" with the arc itself as the visual frame.

For shorter inter-tier gaps (if `tier_gap` is overridden below the default 16 px), the arc anchors `arc_inset` may need to shrink correspondingly to keep the arc visible.

### 2.5 Path row (bottom, optional)

Up to **2** write-method cards. The canonical 5-tier shape (with `arc_band_h = 80`):

```
path_y      = 476       # tier_y + tier_h + path_gap = 80 + 380 + 16
path_h      = 56
path_x[0]   = 16
path_w[0]   = 460
path_x[1]   = 16 + 460 + 16 = 492
path_w[1]   = 460
```

(Both paths land 460-wide despite the viewBox being 1040 — the right pad is taken from the card's tier strip, not the path strip. Keep `path_w=460` for the canonical 5-tier shape. For other tier counts, derive `path_w = (viewBox_w - 2*left_pad - path_gap) / 2`.)

Per-card content:
- Container rect: white fill, `ink @ 0.20` stroke width 1, `rx=6`.
- Tag chip: rect at `(path_x + 8, path_y + 6)`, `h=12 rx=2`, fill transparent, stroke `ink @ 0.30` width 0.8. Tag text centered inside in the `eyebrow` role with letter-spacing 0.08em, ink.
- Title at `(path_x + 80, path_y + 30)`: `node-name` role at 11px, ink.
- Sub at `(path_x + 80, path_y + 46)`: `sublabel` role, muted.

---

---

## Connectors, Governance & Worked YAML

For connector rules, color overrides, focal rules, dark mode, checklist, and worked YAML, see [type-medallion-examples.md](type-medallion-examples.md).
