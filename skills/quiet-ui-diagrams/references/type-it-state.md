# IT current-state

**Best for:** documenting the *before* picture of a modernization proposal — the legacy IT landscape grouped by phase or department (Collection → Processing → Dissemination, or Frontend / Backend / Storage, or Survey → Analysts → Reports), with pain-points flagged, file-based hand-offs labelled (CSV / Excel / Email / Copy), and pre-platform tooling visible. The companion to `type-dp-integration.md`: this type shows the gap that a data-platform proposal is going to close.

Use when stakeholders need to see the friction in the current setup — siloed scripts, manual file shuffles, missing version control, single-points-of-failure — and the path from those to a target platform topology.

This type is **parametric** — the inputs schema in §1 drives every coordinate via the formulas in §2. The rule shape mirrors `type-dp-integration.md` (zones + cross-cutting footer bars), `type-process.md` (rounded right-angle connectors), and `type-medallion.md` (per-element `color` override) so the focal rule, color override, dark mode, and reproducibility checklist read identically across types.

---

## 1. Inputs — the parameter contract

```yaml
title:    "Current IT Landscape"
subtitle: "Data pipeline before the platform"
eyebrow:  "NatStat · Before the platform"

orientation: horizontal      # horizontal (default, zones L→R) | vertical (zones T→B)

zones:                       # 2..4 zones, ordered along the orientation axis
  - name: "COLLECTION"
    components:              # 1..5 components per zone
      - id: survey-solutions
        name: "Survey Solutions"
        sub:  "CAPI · PostgreSQL"
        icon: postgres               # any id from references/primitive-icons.md
        kind: standard               # standard | focal | external (external → dashed stroke)
      - { id: aspnet,    name: "ASP.NET Apps",    sub: "migration · admin portals", icon: server }
      - { id: civil-reg, name: "Civil Registry",  sub: "external · CRVS data",      icon: database, kind: external }
  - name: "PROCESSING"
    components:
      - { id: shared-drive,  name: "Shared Drive",     sub: "No version control · Windows file share", icon: file,      kind: focal }
      - { id: analyst-mach,  name: "Analyst Machines", sub: "SPSS · SAS · Stata · Excel",              icon: desktop }
      - { id: sql-server,    name: "SQL Server",       sub: "on-premises · core RDBMS",                icon: sqlserver, color: "#7a8c47" }  # custom olive
  - name: "DISSEMINATION"
    components:
      - { id: legacy-portal,   name: "LegacyPortal",      sub: "manual bottleneck",     icon: cloud,    kind: focal }
      - { id: natstat-website, name: "NatStat Website",   sub: "public · static pages", icon: internet }
      - { id: ministry,        name: "Ministry Partners", sub: "~6 ministries",         icon: users,    kind: external }

connectors:                   # ordered list; each links two component ids
  - { from: survey-solutions, to: shared-drive,   label: "CSV",     icon: csv,   style: link }
  - { from: aspnet,           to: shared-drive,   label: "EMAIL",   icon: file,  style: link }      # `mail` MISSING in catalog → falls back to `file`
  - { from: civil-reg,        to: shared-drive,   label: "EXCEL",   icon: excel, style: link, dashed: true }
  - { from: shared-drive,     to: analyst-mach,   label: "COPY",                 style: accent, dashed: true }
  - { from: analyst-mach,     to: sql-server,     label: "LOAD",                 style: neutral }
  - { from: analyst-mach,     to: legacy-portal,   label: "EXCEL",  icon: excel, style: accent }
  - { from: legacy-portal,    to: natstat-website, label: "WEB",                 style: neutral }
  - { from: natstat-website,  to: ministry,        label: "CSV DL", icon: csv,   style: link, dashed: true }

footer:                       # 0..3 optional full-canvas-width bars (cross-cutting concerns)
  - { name: "Identity Manager", sub: "Active Directory · LDAP · SSO", icon: active-directory }
  - { name: "Observability",    sub: "logs · metrics · alerts",       icon: monitoring }

legend:                       # auto-generated from styles used; user can override labels
  - { swatch: link,    label: "data flow" }
  - { swatch: accent,  label: "pain-point" }
  - { swatch: dashed,  label: "external" }
  - { swatch: focal,   label: "bottleneck" }

dark: false
```

**Reserved field semantics:**

- `orientation` — `horizontal` (zones run L→R, components stack vertically inside each zone) or `vertical` (zones stack T→B, components run L→R inside each zone).
- `zones[i].name` — uppercase short label (≤ 14 chars). Rendered at the top-left of the zone box in the `eyebrow` role with letter-spacing 0.14em, on a paper-masked break in the zone border.
- `components[i][k].id` — globally unique slug; referenced by `connectors[].from/to`.
- `components[i][k].name` — `node-name` role (the human-readable label).
- `components[i][k].sub` — `sublabel` role at 11px in muted (the technical sub-label; up to 2 lines via auto-wrap when component height grows to 72).
- `components[i][k].icon` — any id from `references/primitive-icons.md`. If missing → no icon, the name shifts left. (Catalog has 41 icons; `mail` is currently missing — use `icon: file` as fallback for email hand-offs.)
- `components[i][k].kind` — `standard | focal | external`. `focal` triggers the accent palette (§5); `external` switches to a 4-2 dashed stroke and muted ink to signal "this is outside our scope."
- `components[i][k].color` — optional per-component color override (§4). Ignored on `kind: focal` (accent wins).
- `connectors[k].from` / `connectors[k].to` — refer to a component `id`. Cross-zone, cross-row, same-zone vertical, and same-zone horizontal all legal; routing chosen by §3.
- `connectors[k].label` — uppercase short text (≤ 8 chars). `arrow-label` role at 11px, weight 600.
- `connectors[k].icon` — optional inline icon to the left of the text. Same catalog as component icons.
- `connectors[k].style` — `neutral | link | accent`. Drives stroke color + marker.
- `connectors[k].dashed` — `true | false`.
- `footer[k]` — optional cross-cutting bar. Spans full canvas width minus margins. No connectors drawn from a footer.
- `legend[k].swatch` — `link | accent | dashed | focal | neutral`. Auto-curated based on what the diagram actually uses; user can re-order or rename.

---

## 2. Layout formulas — deterministic geometry

```
# Horizontal orientation (default)
left_pad        = 16
right_pad       = 16
zone_gap        = 20
zone_y          = 52
zone_h          = 360
n_zones         = len(zones)

# Zone widths: base 200 + 24 per component to give vertical room for icons + 2-line subs.
# In the canonical example (3 / 3 / 3 components) the replication used 256 / 360 / 272 —
# the formula approximates that with hand-picked widths in the worked YAML (§10).
zone_w(i)       = base + n_components_i * comp_slack             # base ≈ 200, slack ≈ 24
viewBox_w       = left_pad + Σ zone_w(i) + (n_zones-1) * zone_gap + right_pad

# Component placement within zone i
comp_pad_x      = 20                                              # x-inset from zone border
comp_h          = 56                                              # 68 for focal (2-line sub), 72 if both sub lines present
comp_gap        = 32
comp_y(i, k)    = zone_y + 28 + k * (comp_h + comp_gap)

# Component centerlines (used for connector routing)
comp_x(i)       = zone_x(i) + comp_pad_x
comp_w(i)       = zone_w(i) - 2 * comp_pad_x
comp_cx(i)      = comp_x(i) + comp_w(i)/2
comp_cy(i, k)   = comp_y(i, k) + comp_h/2

# Footer bars (if present)
footer_bar_h    = 56
footer_gap      = 8
footer_top      = zone_y + zone_h + 24
footer_y(k)     = footer_top + k * (footer_bar_h + footer_gap)
footer_bottom   = footer_top + N_footer * (footer_bar_h + footer_gap) - footer_gap

# Total canvas height
legend_block_h  = 40
content_bottom  = N_footer > 0 ? footer_bottom : zone_y + zone_h
viewBox_h       = content_bottom + legend_block_h + 24
```

### 2.1 Background and zone frame

Solid paper fill across `viewBox`. No dot pattern. Each zone box:

```svg
<rect x="zone_x(i)" y="zone_y" width="zone_w(i)" height="zone_h"
      fill="{ink @ 0.02}" stroke="{ink @ 0.10}" stroke-width="0.8" rx="8"/>
<!-- paper-masked break for the zone label -->
<rect x="zone_x(i)+20" y="zone_y-8" width="{label_w}" height="16" fill="{paper}"/>
<text x="zone_x(i)+24" y="zone_y+4" fill="{soft}"
      font-family="{eyebrow}" letter-spacing="0.14em">{name}</text>
```

### 2.2 Component box

Three visual kinds:

| `kind` | Fill | Stroke | Stroke width | Stroke dash | Name ink | Sub ink |
| --- | --- | --- | --- | --- | --- | --- |
| `standard` | `#FFFFFF` | `ink` | 1 | — | `ink` | `muted` |
| `focal` | `accent @ 0.07` | `accent` | 1.4 | — | `ink` | `accent` (line 1) + `muted` (line 2) |
| `external` | `#FFFFFF` | `muted` | 1 | `4,3` | `ink` | `muted` |

**Icon placement** (24×24, monochrome via `currentColor` — see `references/primitive-icons.md`):

```svg
<g transform="translate(comp_x + 12, comp_y + (comp_h - 24)/2)" color="{ink_for_kind}">
  <use href="#icon-{name}"/>            <!-- or inline the SVG path from the catalog -->
</g>
```

Icon takes 24 × 24 → 36-px total horizontal footprint with the 12-px left pad. Name and sub-label baseline shifts right by 40 px.

**Name + sub baselines** (left-aligned, with icon to the left):

```
name_x = comp_x + 44
name_y = comp_y + (comp_h/2) - 2
sub_y  = comp_y + (comp_h/2) + 14
```

### 2.3 Connector geometry (§3 holds the routing rules)

```
src_right  = comp_x(i_src) + comp_w(i_src)
src_left   = comp_x(i_src)
src_top    = comp_y(i_src, k_src)
src_bot    = src_top + comp_h_src
src_cy     = src_top + comp_h_src/2

dst_left   = comp_x(i_dst)
dst_right  = comp_x(i_dst) + comp_w(i_dst)
dst_top    = comp_y(i_dst, k_dst)
dst_bot    = dst_top + comp_h_dst
dst_cx     = comp_cx(i_dst)
dst_cy     = dst_top + comp_h_dst/2

# Corridor x for cross-zone H+Q+V routing
corridor_x = dst_cx                            # land arrow on dst horizontal center, enter via top/bot
```

### 2.4 Footer bar

```svg
<rect x="left_pad" y="footer_y(k)" width="viewBox_w - 2*left_pad" height="footer_bar_h"
      fill="{ink @ 0.03}" stroke="{ink @ 0.18}" stroke-width="0.8" rx="8"/>
<g transform="translate(left_pad + 20, footer_y(k) + (footer_bar_h - 24)/2)" color="{ink}">
  <use href="#icon-{name}"/>
</g>
<text x="left_pad + 56" y="footer_y(k) + 24" font-family="{node-name}" font-size="14" fill="{ink}">{name}</text>
<text x="left_pad + 56" y="footer_y(k) + 40" font-family="{sublabel}" font-size="12" fill="{muted}">{sub}</text>
```

Footer bars are layer-wide services. **No connectors emerge from them.** They sit visually below the zones and let the reader see the cross-cutting concerns at a glance.

### 2.5 Legend strip

Hairline divider at `y = content_bottom + 16`, then a row of swatches + labels at `y = content_bottom + 36`. Only the styles actually used by `connectors[]` (plus `focal` and `external` if those component kinds are present) appear in the legend.

---

---

## Connectors, Overrides & Worked YAML

For connector rules, color overrides, focal rules, dark mode, checklist, and worked YAML, see [type-it-state-examples.md](type-it-state-examples.md).
