# DP security matrix

**Best for:** documenting per-role / per-component access permissions for a data platform — a grid where each row is a platform component (Keycloak, MinIO bucket, Trino catalog, JupyterHub, NiFi, …) and each column is a role / AD group (Data Administrators, Data Engineers, Data Scientists, Data Consumers, …). Each intersection cell holds a permission value (Admin / Full / R/W / Read / SELECT / Login / No access) with a visual category that matches the permission level. One cell may be marked focal to flag a critical access rule (e.g., "Data Consumers can ONLY `SELECT` from the aggregated catalog — sole consumer access").

Use when stakeholders need to audit *who can do what* across the platform. Prefer **DP integration** when the question is *who can talk to what* (topology/protocol) rather than *who can write/read what* (permissions).

This type is **parametric** — the inputs schema in §1 drives every coordinate via the formulas in §2. The rule shape mirrors `type-medallion.md` / `type-process.md` / `type-data-flow.md` so the focal rule, color override, dark mode, and reproducibility checklist read identically across types.

---

## 1. Inputs — the parameter contract

```yaml
title:    "Platform Access Matrix"
subtitle: "Four canonical groups × platform components"

roles:                                  # 2..6 columns, ordered left → right
  - { name: "Data Administrators", code: "DL-DataAdmins"      }
  - { name: "Data Engineers",      code: "DL-DataEngineers"   }
  - { name: "Data Scientists",     code: "DL-DataScientists"  }
  - { name: "Data Consumers",      code: "DL-DataConsumers"   }

components:                             # 2..14 rows, ordered top → bottom
  - { name: "Keycloak",                          hint: "SSO" }   # `hint` = right-aligned aside in label cell
  - { name: "MinIO · raw bucket" }
  - { name: "MinIO · anon · staging · agg" }
  - { name: "Trino · raw catalog" }
  - { name: "Trino · anon-staging" }
  - { name: "Trino · aggregated" }
  - { name: "JupyterHub" }
  - { name: "NiFi" }

cells:                                  # explicit (row, col) entries; omitted → defaults to "none"
  # value = displayed text (free-form)
  # level = visual category: full | rw | read | none  (closed vocabulary, drives styling)
  # focal: true (max 1)            — overrides level to focal styling
  # sub: "second-line text"        — used inside focal cell
  # color: "#hex"                  — optional per-cell color override (§4)
  - { row: 0, col: 0, value: "Admin", level: "full" }
  - { row: 0, col: 1, value: "Login", level: "read" }
  - { row: 0, col: 2, value: "Login", level: "read" }
  - { row: 0, col: 3, value: "Login", level: "read" }

  - { row: 1, col: 0, value: "Full",       level: "full" }
  - { row: 1, col: 1, value: "R/W",        level: "rw"   }
  - { row: 1, col: 2, value: "No access",  level: "none" }
  - { row: 1, col: 3, value: "No access",  level: "none" }

  # ... rows 2..4 follow the same pattern ...

  - { row: 5, col: 0, value: "Full",       level: "full" }
  - { row: 5, col: 1, value: "R/W",        level: "rw"   }
  - { row: 5, col: 2, value: "SELECT",     level: "read" }
  - { row: 5, col: 3, value: "SELECT only", sub: "sole consumer access", focal: true }

  # ... rows 6..7 ...

none_label: "No access"                 # default text rendered when a cell is omitted
dark: false
```

**Reserved field semantics:**
- `roles[j].name` — primary role label (`node-name` role at 11px, white text on the ink banner)
- `roles[j].code` — secondary AD-group identifier (`sublabel` role, white text at 0.85 opacity)
- `components[i].hint` — optional right-aligned `sublabel` text in the label cell (e.g., `"SSO"`, `"S3 API"`)
- `cells[k].level` — closed vocabulary `full | rw | read | none`. Drives fill/stroke/text-color per §2.4.
- `cells[k].value` — free-form display text. Domain-specific labels (`"R/W"`, `"SELECT"`, `"Login"`) work without inventing new levels.
- `cells[k].focal: true` — exactly **one** cell may declare this. Overrides `level` to focal styling.
- `cells[k].sub` — optional 2nd-line text (used with focal). Renders in the `sublabel` role at 11px below the primary value.
- `cells[k].color: "#hex"` — optional per-cell color override (§4).

---

## 2. Layout formulas — deterministic geometry

```
# Constants
left_pad         = 12
right_pad        = 48
comp_col_w       = 208
comp_role_gap    = 12
role_col_w       = 148
role_col_gap     = 16
header_h         = 52
row_h            = 36
row_stride       = 40

# Counts
n_roles          = len(roles)        # 2..6
n_components     = len(components)   # 2..14

# Canvas
viewBox_w        = left_pad + comp_col_w + comp_role_gap
                   + n_roles * role_col_w + (n_roles - 1) * role_col_gap
                   + right_pad
                   # 4 roles → 12 + 208 + 12 + 592 + 48 + 48 = 920

header_y         = 72
row_y(k)         = 140 + k * row_stride                  # 140, 180, 220, ...
rows_bottom      = row_y(n_components - 1) + row_h       # 8 rows → 456
legend_y_top     = rows_bottom + 20                      # 476 for 8-row canonical
viewBox_h        = legend_y_top + 44                     # 520 for 8-row canonical

# Column positions
comp_col_x       = left_pad                                                       # 12
role_col_x(j)    = left_pad + comp_col_w + comp_role_gap
                   + j * (role_col_w + role_col_gap)
                                                                                  # 232, 396, 560, 724
role_col_cx(j)   = role_col_x(j) + role_col_w / 2                                 # 306, 470, 634, 798
```

### 2.1 Background

Solid paper fill across the full viewBox. No dot pattern.

### 2.2 Header row (`y = 72, h = 52`)

**Component-column header cell:**
- Rect: `(comp_col_x, header_y, comp_col_w, header_h)`, fill white, stroke `ink @ 0.12` 0.8, `rx=6`
- Two-line label centered at `(comp_col_x + comp_col_w/2, header_y+24)` and `(…, header_y+40)`:
  - Line 1: `"Component"` — `node-name` role at 11px, ink
  - Line 2: `"vs. AD group"` — `sublabel` role, muted

**Role banners (one per role):**
- Rect: `(role_col_x(j), header_y, role_col_w, header_h)`, fill `ink`, `rx=6`
- Two-line label centered:
  - Line 1 at `y=92`: `roles[j].name` — `node-name` role at 11px, white
  - Line 2 at `y=108`: `roles[j].code` — `sublabel` role, white at opacity 0.85

### 2.3 Data row (`y = row_y(k), h = 36`)

**Component label cell:**
- Rect: `(comp_col_x, row_y(k), comp_col_w, row_h)`, fill white, stroke `ink @ 0.12` 0.8, `rx=4`
- Name at `(comp_col_x + 12, row_y(k) + 22)`: `node-name` role at 11px, ink, left-aligned
- Hint (if present) at `(comp_col_x + comp_col_w − 12, row_y(k) + 22)`: `sublabel` role, muted, right-aligned

**Value cells (one per role × component):**
- Rect: `(role_col_x(j), row_y(k), role_col_w, row_h)`, `rx=4`, stroke `ink @ 0.12` 0.6
- Fill and text-color depend on `level` (or focal flag) — see §2.4
- Value text centered at `(role_col_cx(j), row_y(k) + 22)`: `node-name` role at 11px
- Focal cell uses a slightly raised primary text at `y=18` and a sub-line at `y=30` (`sublabel` role at 11px)

### 2.4 Cell style table

| `level` | Fill | Stroke | Text color | Text weight |
|---|---|---|---|---|
| `full` | `ink @ 0.08` | `ink @ 0.12` | `ink` | 600 |
| `rw` | `#FFFFFF` | `ink @ 0.12` | `ink` | 400 |
| `read` | `muted @ 0.08` | `ink @ 0.12` | `muted` | 400 |
| `none` | `paper` | `ink @ 0.12` | `soft` | 400 |
| **focal** | `accent @ 0.07` | `accent` (1.4) | `accent` | 600 |

The focal cell can carry a 2nd line (`sub:`) rendered in `accent` with the `sublabel` role at 11px and 0.85 opacity.

### 2.5 Legend (`y_top = legend_y_top, h ≈ 30`)

Hairline separator at `legend_y_top`. Below the separator, one row of style swatches with their labels — only the styles actually used in the diagram appear in the legend.

- "LEGEND" eyebrow at `(left_pad, legend_y_top + 20)`: `eyebrow` role, muted, letter-spacing 0.14em
- Each style: swatch rect (14×12 `rx=2`) followed by a `sublabel` role label
- Item x-positions are tabulated left-to-right with ~120-px stride; legend wraps onto a second visual row only if `n_roles ≥ 6` (otherwise fits in one line)

---

---

## Cell Styling, Overrides & Worked YAML

For cell rendering, color overrides, focal rules, checklist, and full worked YAML, see [type-dp-security-examples.md](type-dp-security-examples.md).
