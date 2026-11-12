# High-Level

**Best for:** end-to-end data stack overviews — ingestion → storage → query → analytics → visualization — deployed on a container orchestrator (Kubernetes, ECS, Nomad). Combines a phase chevron banner, deployment boundary, orchestration bar, identity footer, and (optionally) a right-side vertical chevron strip for cross-cutting concerns (Orchestration, Security, Observability).

This type is **parametric**. The diagram is fully determined by a small list of inputs (chevrons, sources, components, connections). The formulas below tell you exactly where every shape lands given those inputs — two generations from the same inputs must produce visually identical SVG.

---

## 1. Inputs — the parameter contract

Before drawing, collect these from the user (or accept them as a YAML/JSON block). Everything in this reference is derived from these inputs. Don't invent geometry on the fly.

```yaml
chevrons:                       # ordered left → right; reserved names auto-promote to vertical
  - { name: "Data sources",         columns: 1 }
  - { name: "Ingestion",            columns: 1 }
  - { name: "Storage",              columns: 1 }
  - { name: "Transformation",       columns: 1 }
  - { name: "Visualization",        columns: 1 }
  - { name: "Orchestration",        vertical: true }                     # reserved → pairs with the bar
  - { name: "Security",             vertical: true, color: "#b85450" }   # tinted to match the Identity bar below
  - { name: "Observability",        vertical: true }                     # reserved → pairs with crosscut #2

sources:                        # external; rendered in the dashed zone on the left
  - { name: "PostgreSQL", type: "db",     connects_to: ["NiFi"] }
  - { name: "SFTP drop",  type: "ftp",    connects_to: ["NiFi"] }
  - { name: "Web forms",  type: "web",    connects_to: ["NiFi"] }
  - { name: "Legacy",     type: "legacy", connects_to: ["NiFi"] }

components:                     # inside the cluster, plus bars and cross-cutting rows
  - { name: "NiFi",       chevron: "Ingestion",      kind: node,          icon: nifi,     role: "COLL"  }
  - { name: "MinIO",      chevron: "Storage",        kind: node,          icon: minio,    role: "STORE", focal: true }
  - { name: "Trino",      chevron: "Storage",        kind: node,          icon: trino,    role: "VIRT"  }
  - { name: "Notebooks",  chevron: "Transformation", kind: node,          icon: jupyter,  role: "ANLZ"  }
  - { name: "Superset",   chevron: "Visualization",  kind: node,          icon: superset, role: "DASH" }
  - { name: "Airflow",    chevron: "Orchestration",  kind: bar,           icon: airflow,    subtitle: "Apache Airflow" }
  - { name: "Identity",   chevron: "Security",       kind: cross-cutting, icon: keycloak,   subtitle: "Keycloak · LDAP · OIDC",     color: "#b85450" }
  - { name: "Monitoring", chevron: "Observability",  kind: cross-cutting, icon: prometheus, subtitle: "Prometheus · Grafana · Loki" }

connections:                    # explicit edges; focal-touching ones become accent automatically
  - { from: "NiFi",    to: "MinIO",                style: "primary" }
  - { from: "NiFi",    to: "Trino",                style: "secondary" }
  - { from: "MinIO",   to: "Notebooks",            style: "primary" }
  - { from: "Trino",   to: "MinIO",                style: "query" }   # read-back (dashed)
  - { from: "Notebooks", to: "Superset",           style: "secondary" }
  - { from: "Airflow", to: ["NiFi", "Trino", "Notebooks"], style: "trigger" }

focal: "MinIO"                  # exactly one; defaults to first kind=node under "Storage"
dark: false
```

**Reserved chevron names** (always vertical, even if `vertical: true` is omitted): `Orchestration`, `Security`, `Observability`, `Governance`, `Backup`.

**Reserved `kind` values:**
- `node` — a standard box inside the cluster (default).
- `bar` — a horizontal strip spanning the cluster top. Typically one (Orchestration); see §5 for the pairing rule.
- `cross-cutting` — a horizontal strip spanning the body width (stops at the strip margin), stacked below the cluster. **Zero or more allowed**; each stacks 44 px below the previous (§2.5) and pairs 1:1 with a vertical chevron (§5).

**Optional `color`** (per component, hex string): tints the component's container and content while leaving connectors untouched. See §3.4. Use sparingly — a custom color is a semantic flag (e.g., red = security concern), not decoration.

**Source `type` values** → icon mapping (use `references/primitive-icons.md`):
- `db` → `database`
- `ftp` → `bucket` or upload arrow
- `web` → `internet`
- `legacy` → `server`
- `api` → `api`
- Any explicit icon name in `primitive-icons.md` is also accepted.

---

## 2. Layout formulas — deterministic geometry

Every coordinate below is derived from the inputs. **No hardcoded numbers in examples that aren't justified here.**

### 2.1 Canvas

```
has_vertical       = any(c.vertical or c.name in reserved_names for c in chevrons)
right_strip_w      = 28  if has_vertical else 0
strip_margin       = 8   if has_vertical else 0   # gap between body and right strip
effective_w        = 1000 - right_strip_w - strip_margin     # 1000 or 964

n_cross            = count of components with kind == "cross-cutting"
strip_y_bot        = max(428, 388 + n_cross * 44 - 4)        # extends to last crosscut row
viewBox_h          = max(540, strip_y_bot + 112)             # 112 reserved for legend
viewBox            = f"0 0 1000 {viewBox_h}"
```

Every horizontal element (chevron banner, cluster, orchestration bar, identity / cross-cutting bars) ends at `effective_w`. The right strip sits at `x = 1000 - right_strip_w` (= 972). The 8-px band between them is visual breathing room — never put content there.

`viewBox_h` grows when more than one cross-cutting bar is declared: 1 crosscut → 540, 2 → 600 (or 584 if you want it tight; the rule rounds to the next multiple of 20 for clean grids).

### 2.2 Horizontal chevron banner

```
y_banner           = 4
h_banner           = 28
horizontals        = [c for c in chevrons if not c.vertical and c.name not in reserved_names]
sum_columns        = sum(c.columns for c in horizontals)
base_unit          = floor_to_4(effective_w / sum_columns)        # multiple of 4
widths             = [max(120, base_unit * c.columns) for c in horizontals]
widths[-1]         += effective_w - sum(widths)                   # trailing absorbs remainder
x_boundaries       = cumulative_sum([0] + widths)                 # length sum_columns+1
chevron_cx(C)      = (x_boundaries[index(C)] + x_boundaries[index(C)+1]) / 2
```

**Polygon shapes:**
- First (leftmost): `(x0,4) (x1-12,4) (x1,18) (x1-12,32) (x0,32)`
- Middle: `(x0,4) (x1-12,4) (x1,18) (x1-12,32) (x0,32) (x0+12,18)`
- Last (rightmost): `(x0,4) (effective_w,4) (effective_w,32) (x0,32) (x0+12,18)`

Fills alternate between two steps of the **phase-band palette** (§6.1): `band-1` / `band-2` in light mode, `band-2` / `band-3` in dark. Labels: `band-label` fill, `eyebrow` role (mono), `font-size=11`, `letter-spacing=0.14em`, `text-anchor=middle`, centered at `chevron_cx, 21`.

**Color override** (per chevron, both horizontal and vertical): a chevron may declare an optional `color: "#hex"` that replaces the alternation fill for that one chevron. Use it to flag a phase that pairs with a custom-colored component (e.g., `Security` chevron in red when the Identity bar uses `color: "#b85450"`). Rules:

- Override applies to the polygon fill only. The label stays `band-label`; it never takes the active skin's `paper`.
- The alternation index doesn't shift; neighboring chevrons keep their natural fill, even if it produces two adjacent same-fill chevrons. Don't try to "fix" this — overrides should be rare (≤ 2 per diagram).
- In dark mode, use the same hex unless contrast against `band-label` falls below 4.5:1; if it does, pick a darker shade for dark mode and document it as a `color_dark` field on that chevron.
- A chevron color override is independent of any paired component's color, but pairing them (same hex on chevron + bar) is the conventional way to make the column "read" as one concern.

### 2.3 Source zone (dashed, external)

```
sources_x          = 4
sources_y          = 40
sources_w          = x_boundaries[1] - 8           # width of the first chevron, minus 4px gutter each side
sources_h          = 336
```

Stroke: `ink @ 0.20`, `stroke-width=0.8`, `stroke-dasharray=6,3`, `rx=6`. Zone fill: `ink @ 0.02`.

### 2.4 Cluster boundary (solid)

```
cluster_x          = x_boundaries[1] + 4           # starts at end of source zone + 4px gutter
cluster_y          = 40
cluster_w          = effective_w - cluster_x       # extends to right strip / canvas edge
cluster_h          = 336
```

Stroke: `ink @ 0.18`, `stroke-width=1.2`, `rx=8`. Fill: `ink @ 0.02`. K8s icon + label at `(cluster_x + 16, 352)` (icon) and `(cluster_x + 40, 362)` (text).

### 2.5 Cross-cutting bars (identity, observability, …)

Zero or more `kind: cross-cutting` components stack below the cluster. Each gets its own 40-px row with a 4-px gap.

```
crosscuts          = [c for c in components if c.kind == "cross-cutting"]   # ordered as declared
cross_x            = 4
cross_y(k)         = 388 + k * 44                  # 388, 432, 476, …
cross_w            = effective_w - 4               # spans body width, stops at the strip margin
cross_h            = 40
```

Stroke: `ink @ 0.20`, `stroke-width=0.8`, `rx=6`. Fill: `ink @ 0.05`. Icon at `(16, cross_y(k) + 10)`, name centered at `(effective_w / 2, cross_y(k) + 22)`, subtitle at `(effective_w / 2, cross_y(k) + 34)`.

Reserved cross-cutting *concerns* (informational; user can name the actual bar whatever they want):
- **Identity / Security** — Keycloak, LDAP/AD, Okta, Auth0, OIDC providers
- **Observability** — Prometheus + Grafana, Datadog, OpenTelemetry, Loki
- **Backup / DR** — Velero, Restic, snapshot orchestrators
- **Governance / Lineage** — OpenMetadata, DataHub, Apache Atlas
- **Secrets / config** — Vault, Sealed Secrets, External Secrets

Each cross-cutting bar pairs 1:1 with a vertical chevron in the right strip (§5).

### 2.6 Orchestration bar component (inside cluster)

```
bar_x              = cluster_x + 12
bar_y              = 52
bar_w              = cluster_w - 24
bar_h              = 44
```

Stroke: `ink @ 0.18`, `stroke-width=0.8`, `rx=4`. Fill: `ink @ 0.05`. Tool icon at the far right (`bar_x + bar_w - 50, 58`); name centered at `(bar_x + bar_w/2, 71)`; subtitle at `(bar_x + bar_w/2, 84)`.

### 2.7 Component nodes (inside cluster)

```
node_w             = 152
node_h             = 80                            # focal same height, accent border
node_cx(N)         = chevron_cx(N.chevron)         # ← non-negotiable
node_x(N)          = node_cx(N) - node_w/2
```

If a chevron has K nodes assigned, stack them vertically:

```
first_top_y        = 120 if any bar in this column else 64
gap                = 16
row_top(k)         = first_top_y + k * (node_h + gap)   # k = 0..K-1
```

**Focal node:** `fill="{accent @ 0.08}"`, `stroke="{accent}"`, `stroke-width=1.2`. Title text in `accent`. All other nodes: white fill, `stroke={ink @ 0.25}`, `stroke-width=1`.

Role badge top-left at `(node_x+8, node_y+6)`, size 12 high. Icon top-right at `(node_x+node_w-32, node_y+6)`, 24×24, monochrome via `currentColor`. Name centered at `(node_cx, node_y+44)` size 11 sans semibold. Subtitle at `(node_cx, node_y+56)` size 8 mono muted.

### 2.8 Source nodes (inside dashed zone)

```
src_node_w         = sources_w - 8
src_node_h         = 64                            # uniform; chosen to fit ≤ 4 sources
src_node_x         = sources_x + 4
src_first_top_y    = 60
src_gap            = 16
src_row_top(k)     = src_first_top_y + k * (src_node_h + src_gap)
```

Same role-badge / icon / name / subtitle pattern as cluster nodes (icon at `src_node_x+54, row_top(k)+6`; name centered at `src_node_x+src_node_w/2, row_top(k)+42`; subtitle one line below). Role badge text: `EXT`. Caps at 4 sources; for more, split into a separate diagram.

### 2.9 Right strip — vertical chevrons

```
strip_x            = 1000 - right_strip_w       # 972 when present
strip_w            = 28
verticals          = [c for c in chevrons if c.vertical or c.name in reserved_names]
strip_y_top        = 40
strip_y_bot        = max(428, 388 + n_cross * 44 - 4)   # extends to last crosscut row (see §2.1)
strip_h_total      = strip_y_bot - strip_y_top
heights            = [floor_to_4(strip_h_total / len(verticals))] * len(verticals)
heights[-1]       += strip_h_total - sum(heights)       # last absorbs remainder
```

Examples:
- 2 verticals (Orchestration + Security), 1 crosscut → `heights = [192, 196]`, layout `[40..232, 232..428]`.
- 3 verticals (Orchestration + Security + Observability), 2 crosscuts → `strip_y_bot = 472`, `strip_h_total = 432`, `heights = [144, 144, 144]`, layout `[40..184, 184..328, 328..472]`.

Adjacent edges share the same y (no gap), like horizontal chevrons share x at their boundary.

**Polygon shapes** (top-to-bottom flow, mirrors horizontal §2.2):
- First (topmost): flat top, point at bottom — `(strip_x, y0) (strip_x+strip_w, y0) (strip_x+strip_w, y1-12) (strip_x+strip_w/2, y1) (strip_x, y1-12)`
- Middle: notch on top, point on bottom — `(strip_x, y0) (strip_x+strip_w/2, y0+12) (strip_x+strip_w, y0) (strip_x+strip_w, y1-12) (strip_x+strip_w/2, y1) (strip_x, y1-12)`
- Last (bottommost): notch on top, flat bottom — `(strip_x, y0) (strip_x+strip_w/2, y0+12) (strip_x+strip_w, y0) (strip_x+strip_w, y1) (strip_x, y1)`

Fills alternate `band-1` / `band-2` (same phase-band palette as the horizontals, §6.1). Labels: `band-label` fill, `eyebrow` role (mono), `font-size=11`, `letter-spacing=0.14em`, **rotated −90°**, anchored at `(strip_x + strip_w/2, (y0+y1)/2)`.

Vertical chevrons honor the per-chevron `color` override documented in §2.2 — apply the hex to the polygon fill, leave the rotated label `band-label`. Pair the override with the same hex on the chevron's paired bar/crosscut to bind them visually as one concern.

---

---

## Connectors, Branching & Examples

For connector rules, fan-out branching, chevrons, checklist, and examples, see [type-high-level-examples.md](type-high-level-examples.md).
