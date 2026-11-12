# Data Flow

**Best for:** visualising how data moves through a pipeline *across organisational roles* — who initiates, who processes, who publishes, and who consumes. The canonical use case is a multi-role data platform (Admin → Engineers → Scientists → Consumers) with 4–6 process steps. Use when the reader needs to understand **who does what at each stage**, not just the technical components.

Prefer standard **Swimlane** for cross-functional business processes (HR approvals, support tickets). Use **Data flow** when the subject is a data pipeline with typed payloads (raw files, tables, reports) and role-scoped access boundaries.

This type is **parametric** — the inputs schema in §1 drives every coordinate via the formulas in §2. Two generations from the same inputs must produce visually identical SVG.

---

## 1. Inputs — the parameter contract

```yaml
lanes:                              # 1..4 horizontal swimlanes (top to bottom)
  - { name: ["DATA", "ADMINS"],     key: "ADM" }
  - { name: ["DATA", "ENGINEERS"],  key: "ENG" }
  - { name: ["DATA", "SCIENTISTS"], key: "SCI" }
  - { name: ["DATA", "CONSUMERS"],  key: "CON" }

steps:                              # 1..6 columns (left to right)
  - { number: "01", label: "COLLECT" }
  - { number: "02", label: "STORE" }
  - { number: "03", label: "TRANSFORM" }
  - { number: "04", label: "ANALYZE",  focal: true }   # focal step header chip — accent fill
  - { number: "05", label: "PUBLISH" }

nodes:                              # explicit per-cell entries; empty cells render nothing
  - { lane: "ADM", step: 0, title: "Project Setup",   sub: "create · assign roles",     tool: "Platform console" }
  - { lane: "ADM", step: 1, title: "Access Control",  sub: "bucket policies · LDAP",    tool: "MinIO · LDAP console",
      color: "#b85450" }            # tinted rust-red to flag governance/identity concern
  - { lane: "ENG", step: 0, title: "Source Ingest",   sub: "ext. sources → raw",        tool: "NiFi · API · SFTP",
      chips: {in: "WB", out: "DB"} }                    # web payload in, dataset out
  - { lane: "ENG", step: 1, title: "Raw Store",       sub: "raw landing zones",         tool: "MinIO raw",
      chips: {in: "DB", out: "DB"} }                    # raw stays raw inside the landing zone
  - { lane: "ENG", step: 2, title: "Clean & Stage",   sub: "raw → staging → anon",      tool: "NiFi · Trino",
      chips: {in: "DB", out: "TB"} }                    # raw dataset → analysis-ready table
  - { lane: "SCI", step: 3, title: "Explore & Model", sub: "anon data → insights",      tool: "JupyterHub · Trino",
      chips: {in: "TB", out: "FL"}, focal: true }       # focal — table in, file/report out
  - { lane: "SCI", step: 4, title: "Publish Findings", sub: "models → dashboards",      tool: "Superset · Reports",
      chips: {in: "FL", out: "FL"} }                    # report in, report out (pass-through to publish)
  - { lane: "CON", step: 4, title: "Query Insights",   sub: "aggregated views",         tool: "Trino (read-only)",
      chips: {in: "TB", out: "TB"} }                    # consumers read tables, hand off tables

arrows:                             # explicit edges; styles bind to topology (see §3)
  - { from: {lane: "ADM", step: 0}, to: {lane: "ADM", step: 1}, style: "muted" }
  - { from: {lane: "ADM", step: 0}, to: {lane: "ENG", step: 0}, style: "trigger" }   # dashed governance
  - { from: {lane: "ADM", step: 1}, to: {lane: "ENG", step: 1}, style: "trigger" }
  - { from: {lane: "ENG", step: 0}, to: {lane: "ENG", step: 1}, style: "muted" }
  - { from: {lane: "ENG", step: 1}, to: {lane: "ENG", step: 2}, style: "muted" }
  - { from: {lane: "ENG", step: 2}, to: {lane: "SCI", step: 3}, style: "accent",     # focal cross-role
      label: "anon data" }
  - { from: {lane: "SCI", step: 3}, to: {lane: "SCI", step: 4}, style: "muted" }
  - { from: {lane: "SCI", step: 4}, to: {lane: "CON", step: 4}, style: "link" }     # teal: published

dark: false
```

**Reserved field semantics:**
- `lanes[k].key` — the 3-letter role chip text (e.g., `ADM`, `ENG`, `SCI`, `CON`). Used inside every node in that lane.
- `lanes[k].name` — two-line lane label; both lines use the uppercase `eyebrow` role.
- `steps[j].focal: true` — exactly **one** step may declare this. Header chip renders in accent.
- `nodes[i].focal: true` — exactly **one** node may declare this. Renders with accent border (§5).
- `nodes[i].chips` — data-type chips for the node. Either form accepted:
  - **Object form (preferred):** `{in: "<CODE>", out: "<CODE>"}` — explicit input/output semantic. Either side optional.
  - **Array form:** `["<INPUT_CODE>", "<OUTPUT_CODE>"]` — first item is input, second is output.
  - Codes from §8 (`WB`, `DB`, `TB`, `FL`, `LS`). Position is **fixed**: input chip on the node's bottom-**left**, output chip on the bottom-**right**.
- `nodes[i].color` — optional **per-node color override**. Any valid `"#hex"` string is accepted; the §4 palette is recommended for cross-diagram consistency but not required. Every node can carry its own color independently of others.

---

## 2. Layout formulas — deterministic geometry

```
label_col_w      = 140
step_slot_w      = 112
right_pad        = 28
n_steps          = len(steps)
n_lanes          = len(lanes)

# Canvas
viewBox_w        = label_col_w + n_steps * step_slot_w + right_pad   # 5 steps → 728
header_h         = 36
lane_h           = 80
has_color_row    = any(node.color or step.color or lane.color in inputs)
legend_h         = 100 if has_color_row else 80                      # 4 rows when colors are present
viewBox_h        = header_h + n_lanes * lane_h + legend_h            # 4 lanes, no colors → 436; with colors → 456

# Header strip (top)
header_y         = 0                                                  # ends at header_h = 36
step_chip_y      = 6                                                  # 16-px chip at y=6..22
step_label_y     = 29                                                 # text line below chip

# Lane positions
lane_y_top(k)    = header_h + k * lane_h                              # 36, 116, 196, 276
lane_y_mid(k)    = lane_y_top(k) + lane_h/2                           # 76, 156, 236, 316
lane_label_x     = label_col_w / 2                                    # 70

# Step / node center x
step_cx(j)       = label_col_w + j * step_slot_w + step_slot_w/2      # 196, 308, 420, 532, 644

# Nodes
node_w           = 100
node_h           = 64
node_x(j)        = step_cx(j) - node_w/2                              # 146, 258, 370, 482, 594
node_y(k)        = lane_y_top(k) + 8                                  # 44, 124, 204, 284

# Legend strip (bottom)
legend_y_top     = header_h + n_lanes * lane_h                        # 356
legend_row_y     = [legend_y_top + 16, legend_y_top + 37, legend_y_top + 59]
                                                                      # 372, 393, 415
```

### 2.1 Background structure

- Paper fill across full viewBox.
- Dot pattern: 22×22 grid, `circle r=0.8`, `fill ink @ 0.10`.
- Alternating lane tints: odd-indexed lanes (0, 2, …) receive `ink @ 0.018` fill.
- Lane dividers: horizontal hairlines at every `lane_y_top(k)` and at `legend_y_top`, stroke `ink @ 0.12` width 0.8.
- Label column right border: vertical hairline at `x = label_col_w`, from `y = header_h` to `y = legend_y_top`.

### 2.2 Step header chip

Per step `j`:

```
chip_x(j)        = step_cx(j) - 16        # 16×16 chip
chip_y           = 6
chip_w           = 32
chip_h           = 16
chip_rx          = 8                       # pill-shaped
number_anchor    = (step_cx(j), 14)
label_anchor     = (step_cx(j), 29)
```

Default fill: `ink @ 0.12`, number text ink, label text muted.
Focal fill: `accent @ 0.20`, number + label text accent.
Per-step `color` override (§4): replaces the fill with `rgba(C, 0.20)` and the text fill with `C`.

### 2.3 Lane labels

Two-line `eyebrow` role label, both lines uppercase, fill muted:
- Line 1 at `(lane_label_x, lane_y_mid(k) - 4)`
- Line 2 at `(lane_label_x, lane_y_mid(k) + 8)`

Per-lane `color` override (§4): replaces the label fill with `C` and the lane tint with `rgba(C, 0.04)` (instead of the default `ink @ 0.018`).

### 2.4 Node content layout (inside the 100×64 rect)

```
role_chip          rect 18×10 at (node_x+4, node_y+4),  rx=3
role_chip_text     centered at (node_x+13, node_y+9), eyebrow role, font-size=11, weight=600
title              centered at (step_cx(j), node_y+23), node-name role, font-size=11
sub                centered at (step_cx(j), node_y+35), sublabel role, font-size=11, muted
tool               centered at (step_cx(j), node_y+47), sublabel role, font-size=11, soft
data chip IN       rect 16×8 at (node_x+4,   node_y+54), rx=3      # payload type entering the node
data chip OUT      rect 16×8 at (node_x+80,  node_y+54), rx=3      # payload type leaving the node
```

Empty cells (no node entry) render **nothing**. No placeholder rect, no role chip, no label — the cell is invisible.

---

## 3. Arrow rules (mandatory)

Four styles, bound to topology. Connectors are drawn **before** all node rects (z-order rule).

| `style` | Stroke | Width | Dash | Marker | When required |
|---|---|---|---|---|---|
| `muted` | `muted` | 1.0 | — | `arr-muted` | Standard data hand-off between steps or within a lane. |
| `trigger` | `muted` | 1.0 | `4,3` | `arr-muted` | Governance trigger — an admin action enables downstream work. Unlabelled. |
| `accent` | `accent` | 1.2 | — | `arr-accent` | Focal cross-role handoff. **Exactly one per diagram**, labeled. |
| `link` | `link` | 1.0 | — | `arr-link` | Published / externally-consumed output. |

**Defs block** (required, three markers):

```svg
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="11" cy="11" r="0.8" fill="{ink @ 0.10}"/>
  </pattern>
  <marker id="arr-muted"  markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{muted}"/></marker>
  <marker id="arr-accent" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{accent}"/></marker>
  <marker id="arr-link"   markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{link}"/></marker>
</defs>
```

### 3.1 Routing rules (non-negotiable)

- **Single-bend routing:** horizontal-first, then vertical. Exit a node from the **right edge**; enter from the **left** (same-lane horizontal) or **top/bottom** (cross-lane vertical).
- **No diagonals.** Bends use an 8-px Q-bezier corner.
- **Same-step cross-lane (vertical)**: line directly between `(step_cx(j), lane_y_top(k_to)−12)` and `(step_cx(j), lane_y_top(k_to))`. Used for admin → engineers triggers under the same step.
- **Cross-lane cross-step (focal)**: exit right, run horizontal past the source node's right edge to a corridor x just before the target's step, then drop vertically.
- **Labels:** only the `accent` arrow gets a label. Use a paper-filled rect mask (opaque) 6 px behind the text. Other arrows are unlabelled.
- **Z-order:** all arrows emitted before any node rect (the rect fills mask the line ends inside the node).

---

## 4. Component color override

Any node, lane, or step may declare an optional `color: "#hex"`. Mirrors high-level §3.4 and dp-integration §4 so the rule reads identically across types.

### 4.1 Per-node `color`

Applied to:

| Element | Light | Dark |
|---|---|---|
| Container fill (`rect`) | `rgba(C, 0.06)` | `rgba(C_light, 0.10)` |
| Container stroke | `rgba(C, 0.35)` (stroke-width 1) | `rgba(C_light, 0.45)` |
| Role chip fill | `rgba(C, 0.18)` | `rgba(C_light, 0.22)` |
| Role chip text | `C` | `C_light` |
| Title text | `C` | `C_light` |
| Sub-label | **unchanged** (muted) | **unchanged** (muted) |
| Tool label | **unchanged** (soft) | **unchanged** (soft) |
| Data-type chips | **unchanged** | **unchanged** |
| Arrows touching this node | **unchanged** — topology-driven | **unchanged** |

`C_light` = the same hex lightened ~15% for dark-mode contrast (e.g., `#b85450` → `#d97a78`).

### 4.2 Per-step `color`

Replaces the step header chip's fill with `rgba(C, 0.20)` and the chip's number + label text fill with `C`. The legend's matching step entry uses the same colors.

### 4.3 Per-lane `color`

Replaces the lane stripe tint with `rgba(C, 0.04)` (only for odd-indexed lanes that receive a tint by default — or extend to all lanes if explicitly chosen) and the lane label text fill with `C`. Use sparingly; lane tints are easy to over-apply.

### 4.4 Rules

- **Never on focal nodes / focal steps.** The accent already carries that signal. A `color` on a focal element is ignored.
- **Never on arrows.** Arrows are topology-driven. If you want a colored edge, pick a different `style` from §3, not a color override.
- **Cap at 3 custom-colored elements** per diagram (nodes + lanes + steps combined), in addition to the focal pair (focal node + focal step header). Above 3 the visual signal starts to fragment — if you need more, split the diagram or rethink whether each color carries distinct meaning.
- **Subtitles and tool labels stay muted.** Only the primary identity (border + role chip + title + icon) carries the color signal.

### 4.5 Semantic palette (recommended)

Same palette as high-level / dp-integration so a reader scanning multiple diagrams sees the same colors meaning the same thing:

- `#b85450` rust-red — Security / Identity / Governance (admin nodes, LDAP, access control)
- `#5a7d9a` slate-blue — Observability / Quality (monitoring, data-quality gates, lineage)
- `#7a8c47` olive-green — Governance / Lineage (catalog, metadata)
- `#8c6d3f` warm-brown — Backup / DR / Archive

---

---

## Guidelines & Checklist

For focal rules, dark mode tokens, reproducibility checklist, data chips reference, and examples, see [type-data-flow-examples.md](type-data-flow-examples.md).
