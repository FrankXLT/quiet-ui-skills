# DP integration

**Best for:** the integration topology of a data platform — which source systems plug in, which consumer surfaces plug out, and which protocol each one speaks. Hub-and-spoke layout wrapped in an explicit **Data platform** layer; no time/phase axis.

Use when the question is *"what surfaces does this platform expose, and over what wire?"* rather than *"how does data move through phases?"*.

This type is **parametric** — like `type-high-level.md`, every coord is derived from a small inputs schema. Two generations from the same inputs must produce visually identical SVG.

---

## 1. Inputs — the parameter contract

```yaml
sources:                            # left column, 0..6 nodes
  - { name: "Databases",  type: "db",        subtitle: "SQL · MariaDB",
      connects_to: [{to: "NiFi", label: "JDBC"},
                    {to: "Trino", label: "FEDERATE", style: "federated"}] }
  - { name: "SFTP drops", type: "sftp",      subtitle: "scheduled pulls",
      connects_to: [{to: "NiFi", label: "SFTP"}] }
  - { name: "Email",      type: "mail",      subtitle: "IMAP attachments",
      connects_to: [{to: "NiFi", label: "IMAP"}] }
  - { name: "IBM legacy", type: "mainframe", subtitle: "file export",
      connects_to: [{to: "NiFi", label: "FILE"}] }

platform:
  name: "DATA PLATFORM"             # zone label (paper-masked top border)
  rows:                             # ordered top→bottom; each is bar or row
    - { kind: bar, name: "Trino",   icon: trino,   subtitle: "federated query · push-down",
        role: "SQL", focal: true }
    - { kind: row, nodes: [
        { name: "Apache NiFi",  icon: nifi,    role: "INGEST",   subtitle: "flow-based ETL" },
        { name: "MinIO",        icon: minio,   role: "STORE",    subtitle: "S3 object store · medallion", focal: true },
        { name: "JupyterLab",   icon: jupyter, role: "NOTEBOOK", subtitle: "Python · R · pandas" }
      ]}
    - { kind: bar, name: "Apache Airflow", icon: airflow,
        subtitle: "scheduler · DAG triggers · backfill", role: "DAG" }

consumers:                          # right column, 0..6 nodes
  - { name: "Desktop apps",   type: "monitor", subtitle: "SPSS · SAS · Stata",
      connects_from: [{from: "Trino", label: "ODBC"}] }
  - { name: "BI & reports",   type: "chart",   subtitle: "Tableau · Power BI",
      connects_from: [{from: "Trino", label: "JDBC"}] }
  - { name: "Public website", type: "globe",   subtitle: "NatStat portal",
      connects_from: [{from: "Trino", label: "HTTPS"}] }
  - { name: "API gateway",    type: "api",     subtitle: "3rd-party / OAuth2",
      connects_from: [{from: "Trino", label: "REST"}] }

footer:                             # 0..N cross-cutting bars stacked below zone (full-canvas width)
  - { name: "Active Directory", icon: key,        subtitle: "LDAP · SSO · group RBAC",
      color: "#b85450" }            # tinted red to flag the security concern
  # additional footer nodes (Observability, Backup, …) stack below this one

internal_connections:               # explicit platform-component edges
  - { from: "NiFi",        to: "MinIO",      style: "primary",   label: "WRITE" }
  - { from: "MinIO",       to: "JupyterLab", style: "secondary", label: "READ"  }
  - { from: "MinIO",       to: "Trino",      style: "secondary" }
  - { from: "JupyterLab",  to: "Trino",      style: "secondary", dashed: true }
  - { from: "Airflow",     to: ["Apache NiFi", "MinIO", "JupyterLab"], style: "trigger" }

focal_accent: accent                # one color for all focal components; the `accent` role by default,
                                    # or an explicit "#hex" to override it
dark: false
```

**Reserved `kind` values for `platform.rows`:**
- `bar` — full-zone-width strip. Default height 44 px (focal bars get 56 px). Required fields: `name`, `icon`. Optional: `subtitle`, `role`, `color`, `focal`.
- `row` — N nodes evenly spaced across zone width. Required: `nodes` list. Each node has `name`, `icon`, optional `role`, `subtitle`, `color`, `focal`.

**Source/consumer `type` values** → icon mapping (extends `references/primitive-icons.md`):
- `db` → cylinder, `sftp` → folder-with-arrow, `mail` → envelope, `mainframe` → server-with-vents
- `monitor` → desktop screen, `chart` → bar-chart, `globe` → globe, `api` → curly braces
- `key` → key + ring (identity / IDP)
- Any explicit icon name in `primitive-icons.md` is also accepted.

**Per-component `color: "#hex"`** is optional on any node, bar, or footer entry. See §4.

---

## 2. Layout formulas — deterministic geometry

```
# Canvas
viewBox_w        = 1200
n_sources        = len(sources)
n_consumers      = len(consumers)
n_footer         = len(footer)

# Side columns (sources left, consumers right)
col_top          = 92
col_node_h       = 64
col_gap          = 24                    # stride = col_node_h + col_gap = 88
col_h_min        = 336                   # default fits 4 sources (4 * 88 - 24)
col_h            = max(col_h_min, max(n_sources, n_consumers) * 88 - 24)
left_x           = 40
left_w           = 160
right_x          = 1000
right_w          = 160
col_node_y(k)    = col_top + k * 88
col_node_cy(k)   = col_node_y(k) + col_node_h/2     # 124, 212, 300, 388 by default

# Platform zone
zone_x           = 260
zone_w           = 696
zone_y           = 72
zone_h           = col_h                            # zone always matches column height
zone_cx          = zone_x + zone_w/2                # 608
zone_pad_x       = 16                               # inside left/right padding for bars
zone_label_y     = zone_y + 3                       # paper-masked label across top border

# Footer bars (below zone — each cross-cutting concern is a full-width bar)
footer_top       = zone_y + zone_h + 52             # 52-px gap below zone
footer_bar_h     = 56
footer_bar_x     = 40                               # aligned with source column left edge
footer_bar_w     = viewBox_w - 80                   # = 1120 — spans from source col left to consumer col right
footer_gap       = 8
footer_y(k)      = footer_top + k * (footer_bar_h + footer_gap)
footer_bottom    = footer_top + n_footer * (footer_bar_h + footer_gap) - footer_gap

viewBox_h        = max(600, footer_bottom + 84)     # 84 reserved for legend

# Platform.rows allocation inside zone
bar_h_focal      = 56
bar_h_default    = 44
row_h            = 72
row_gap          = 16
```

### 2.1 Row placement (cursor algorithm)

Allocate each `platform.rows` entry top-to-bottom. The single `row` (or first row when N>1) anchors to side-column row 2 so its connectors stay horizontal:

```
primary_row_idx  = index of first kind=row in platform.rows
primary_row_top  = col_node_y(1) - (row_h - col_node_h)/2     # 176 by default
                                                              # 4-px nudge so cy aligns with side row 2

# Place rows above primary
y = primary_row_top
for entry in platform.rows[:primary_row_idx] reversed:
    y -= row_gap
    entry.h     = bar_h_focal if (entry.kind == bar and entry.focal) else bar_h_default
    y          -= entry.h
    entry.y_top = y                                            # Trino bar lands at y=104

# Place primary row
platform.rows[primary_row_idx].y_top = primary_row_top         # NiFi/MinIO/Jupyter at y=176
platform.rows[primary_row_idx].h     = row_h

# Place rows below primary
y = primary_row_top + row_h
for entry in platform.rows[primary_row_idx+1:]:
    y          += row_gap
    entry.y_top = y
    entry.h     = bar_h_focal if (entry.kind == bar and entry.focal) else bar_h_default
    y          += entry.h

# Constraint: y <= zone_y + zone_h
```

This produces the canonical layout for the standard shape (top bar / 3-node row / bottom bar): Trino at `y=104 h=56`, primary row at `y=176 h=72`, Airflow at `y=324 h=44`. Bottom anchor of Airflow at y=368 (40-px clear from zone bottom at y=408). **Note**: with the canonical layout there's a 76-px gap between the primary row's bottom (y=248) and Airflow's top (y=324). That gap is intentional — Airflow visually sits at the same y-band as source/consumer row 4 (cy=388), so it reads as a sibling of the bottom side-column row.

### 2.2 Node placement inside a `row` entry

```
N            = len(row.nodes)
node_w       = (zone_w - 2*zone_pad_x - (N-1) * 16) / N
node_x(j)    = zone_x + zone_pad_x + j * (node_w + 16)
node_cx(j)   = node_x(j) + node_w/2
```

For the canonical 3-node row: `node_w = (696 - 32 - 32) / 3 = 210.67`. The shipped example uses fixed `node_w=160` with custom x positions (`288, 480, 672`) chosen so each node's `cx` aligns to the column for connector convenience: 368, 560, 752. **Both layouts are valid**; the formula above is the default for new diagrams. Document any deviation in the rendered SVG with a comment.

### 2.3 Bar (full-zone-width) placement

```
bar_x      = zone_x + zone_pad_x         # 276
bar_w      = zone_w - 2*zone_pad_x       # 664
bar_cx     = zone_cx                     # 608
```

Bars span the full zone width minus 16-px padding on each side. Bars marked `focal: true` use `bar_h_focal=56` and accent styling (fill `rgba(focal_accent, 0.08)`, stroke `focal_accent`). Non-focal bars use `bar_h_default=44` with muted styling (fill `ink @ 0.05`, stroke `ink @ 0.32`).

### 2.4 Source / consumer placement (side columns)

```
source_y(k)       = col_top + k * 88            # 92, 180, 268, 356, …
source_cy(k)      = source_y(k) + col_node_h/2  # 124, 212, 300, 388, …
consumer_y(k)     = source_y(k)                 # mirrored
consumer_cy(k)    = source_cy(k)
```

All side-column nodes use fixed `w=160 h=64`. Same fill / stroke pattern: fill `muted @ 0.06`, stroke `soft`, stroke-width 1.

---

---

## Connectors, Overrides & Examples

For connector routing, component color overrides, dark mode, checklist, and full YAML examples, see [type-dp-integration-examples.md](type-dp-integration-examples.md).
