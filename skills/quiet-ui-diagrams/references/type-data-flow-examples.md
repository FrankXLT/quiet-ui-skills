# Data Flow — Rules, Reference & Examples

Companion reference for role-scoped data flow diagrams covering focal rules, tokens, chips, and examples.

## 5. Focal rule
The data-flow diagram is built around **one cross-role handoff** that defines its central claim. Three focal slots, exactly one entry each:

- **One focal step** (`steps[j].focal: true`) — typically the analytical pivot (Analyze, Model, …). Header chip and legend chip both render in accent.
- **One focal node** (`nodes[i].focal: true`) — the node that *receives* the focal handoff. Accent border + accent role chip + ink title.
- **One focal arrow** (`arrows[i].style: "accent"`) — the cross-role handoff into the focal node. Solid accent stroke + labeled with a short payload descriptor (e.g., `anon data`).

If zero or >1 of any focal slot are declared, halt and ask the user.

---

## 6. Dark mode

| Token | Light | Dark |
|---|---|---|
| Paper | `paper` | `ink` |
| Ink | `ink` | `paper` |
| Muted | `muted` | `soft` |
| Soft | `soft` | `rule-solid` |
| Accent | `accent` | `accent` |
| Link | `link` | `link` |
| Dot pattern | `ink @ 0.10` | `paper @ 0.10` |
| Lane tint | `ink @ 0.018` | `paper @ 0.025` |
| Dividers | `ink @ 0.12` | `paper @ 0.12` |
| Default chip fill | `ink @ 0.12` | `paper @ 0.12` |
| Focal chip fill | `accent @ 0.20` | `accent @ 0.22` |
| Default node fill | `paper` | `paper @ 0.04` |
| Default node stroke | `ink @ 0.25` | `paper @ 0.20` |
| Focal node fill | `accent @ 0.07` | `accent @ 0.12` |
| Focal node stroke | `accent` | `accent` |
| Custom component colors | `C` | `C_light` (lighten ~15%) |

---

## 7. Reproducibility checklist (taste gate)

Before emitting SVG, verify **every** item:

1. `viewBox = "0 0 {viewBox_w} {viewBox_h}"` derived from `n_steps` and `n_lanes` via §2.
2. Header strip at `y=0..36`; legend strip at `y=legend_y_top..viewBox_h` (`legend_y_top = 36 + n_lanes * 80`).
3. Every node at `(step_cx(j) - 50, lane_y_top(k) + 8)` size `100×64`.
4. Empty cells render nothing — no placeholder rect, no text.
5. Exactly **one** focal step (`steps[j].focal: true`).
6. Exactly **one** focal node (`nodes[i].focal: true`).
7. Exactly **one** focal arrow (`style: accent`). Labeled, with a paper-masked rect behind the label.
8. All other arrows unlabelled.
9. All arrows emitted before any node rect (z-order rule).
10. Single-bend routing only — no diagonals. Q-bezier `r=8` at each bend.
11. Custom component colors ≤ 3 (in addition to the focal pair). Arrows never recolored by component `color`.
12. Subtitle and tool labels stay muted regardless of any component `color`.

---

## 8. Data-type chips reference (input + output)

Small `16×8 rx=3` badges at the bottom of each node, one for input and one for output. Position is **non-negotiable**:

- **Input chip** at `(node_x+4, node_y+54)` — bottom-**left** of the node. Represents the payload format *entering* the node from upstream.
- **Output chip** at `(node_x+80, node_y+54)` — bottom-**right** of the node. Represents the payload format *leaving* the node toward downstream.

Either chip may be omitted (e.g., a sink node has only an input chip; a source-only node has only an output chip). Reading the diagram becomes a payload-transformation trace: scan a row, read each node's input → output, and you see exactly what shape the data takes at each hand-off.

### Chip codes

| Code | Color | Meaning |
|------|-------|---------|
| `WB` | `#6e6479` (mauve) | Web / Public data |
| `DB` | `#5e7a9b` (steel-blue) | Dataset / Raw file |
| `TB` | `#b8915a` (amber) | Table / Analysis-ready |
| `FL` | `#9c6b50` (sienna) | File / Report / Export |
| `LS` | `#4a7c59` (forest) | Live stream / Event |

Text inside chip: white, `eyebrow` role at 11px, weight 700.

Data-type chip colors are a **separate semantic axis** from the per-node color override (§4). The chip colors describe *payload format*; the node color override describes *concern type* (governance, observability, …). Don't conflate them — a node can have both an `out: TB` amber chip and a rust-red border color simultaneously.

---

## 9. Legend (3- or 4-row strip)

Each row introduced by a category label at `x=144`. The default legend has **3 rows** (`STEPS` / `DATA TYPE` / `FLOW`); when one or more nodes carry a `color` override (§4), add a 4th `CONCERN` row and grow `legend_h` to 100 (so `viewBox_h = header_h + n_lanes·80 + 100`).

- **Row 1 — `STEPS`** at `y = legend_y_top + 16`: repeat the header chips with their labels. Focal step keeps accent fill.
- **Row 2 — `DATA TYPE`** at `y = legend_y_top + 37`: one swatch per chip type actually used in the diagram. **Append a small sub-hint** in the muted `sublabel` role after the chips: `left chip = input · right chip = output`. This makes the position-based input/output convention explicit for first-time readers.
- **Row 3 — `CONCERN`** (only when color overrides are present) at `y = legend_y_top + 58`: one mini-rect per custom color used, with its semantic label (e.g., `Identity · Governance`, `Data Quality · Observability`). The focal accent swatch is also shown here so the reader sees all three colored axes side-by-side.
- **Row 4 — `FLOW`** (last row, position depends on whether `CONCERN` row exists): short line segments with their marker + text label, one per arrow style actually used.

All legend items align on a single horizontal strip per row. Do not stack vertically inside a box.

---

## 10. Complexity budget

| Dimension | Max |
|---|---|
| Lanes (roles) | 4 |
| Steps | 6 |
| Nodes per lane | Nodes = active steps only — empty cells are invisible (no placeholder box) |
| Labelled arrows | 1 (focal accent only) |
| Data-type chips per node | 2 |
| Custom-colored elements (§4) | 3 (in addition to focal node + focal step) |

Above 4 lanes or 6 steps: split into two diagrams (e.g., ingestion pipeline / analytics pipeline).

---

## 11. Anti-patterns

- **Placeholder empty cells** — if a role doesn't participate in a step, leave the cell empty (no box, no text).
- **More than one labelled arrow** — only the focal cross-role handoff gets a label.
- **Diagonal arrows** — always horizontal-first, then vertical; single right-angle bend.
- **`title` role for node titles** — node titles use the `node-name` role (technical context). Only the page `<h1>` uses `title`.
- **Accent on more than one node, one step, one arrow** — focal = one node + one step + one arrow, max.
- **`node-name` role for role labels** — lane labels always use the uppercase `eyebrow` role (they are identifiers, not prose).
- **`color` override on a focal element** — ignored. Accent always wins.
- **Custom-colored arrows** — arrows are topology-driven. Color on a node never spreads to its edges.
- **Lane tints over-applied** — a tint on every lane reads as decoration, not signal. Apply to ≤1 lane.

---

## 12. Examples

- `assets/example-data-flow.html` — minimal light (the platform, 4-role × 5-step: Admin, Engineers, Scientists, Consumers). Gallery default.
- `assets/example-data-flow-dark.html` — same, dark skin.
- `assets/example-data-flow-full.html` — same, editorial-card frame.

---

See [type-data-flow.md](type-data-flow.md) for parameters and geometry formulas.
