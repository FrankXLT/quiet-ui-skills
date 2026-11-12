# Data Platform Integration — Connectors, Overrides & Examples

Companion reference for data platform integration diagrams covering connectors, color overrides, and worked examples.

## 3. Connector rules (mandatory)
Five styles, bound to topology. Don't let user override style on focal-touching, bar-originating, or Trino → consumer edges — those are fixed by rule.

| `style` | Stroke | Width | Dash | Marker | When required |
|---|---|---|---|---|---|
| `primary` | `focal_accent` (default `accent`) | 1.4 | — | `arrow-focal` | Every edge whose endpoint is a `focal: true` component. Also every Trino → consumer edge (serve-flow rule). |
| `secondary` | `muted` | 1.2 | — | `arrow` | Default for internal platform-component edges and source → platform edges that don't touch focal. |
| `federated` | `link` | 1.0 | `4,3` | `arrow-link` | Federation queries (e.g., source DB → Trino). |
| `trigger` | `muted` | 1.0 | `4,3` | `arrow` | Every edge originating from a `kind: bar` component (Airflow drops). Unlabelled. |
| `auth` | `accent` | 1.2 | `5,4` | `arrow-accent` | Every edge from a footer node up to the zone bottom edge. **Never to a specific component.** |

**Defs block** (required, six markers — exactly):

```svg
<defs>
  <marker id="arrow"        markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{muted}"/></marker>
  <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{accent}"/></marker>
  <marker id="arrow-focal"  markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{focal_accent}"/></marker>
  <marker id="arrow-link"   markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{link}"/></marker>
  <marker id="arrow-sm"     markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto"><polygon points="0 0, 6 2.5, 0 5" fill="{muted}"/></marker>
  <marker id="arrow-dim"    markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ink @ 0.45}"/></marker>
</defs>
```

### 3.1 Exit / entry sides (non-negotiable)

| Edge kind | Exit side of source | Entry side of target |
|---|---|---|
| Source → platform component | **right** of source | **left** of target |
| Platform → platform (same row) | **right** | **left** |
| Bar → row node (vertical drop) | **bottom** of bar at `node_cx(target)` | **top** of target |
| Platform → consumer | **right** of source platform component | **left** of consumer |
| Footer → zone | **top** of footer (at `footer_auth_x(k)`) | zone bottom edge `y = zone_y + zone_h` |
| Footer → component (any specific one) | **forbidden** |

### 3.2 Routing

- Orthogonal elbows with at most two bends; Q-bezier `r=8` at every corner.
- **Fan-out staggering:** when one node fans out to N targets on the same side, stagger the exit y by ±4 px per index so arrows don't overlap (e.g., Trino → 4 consumers exits at y=124, 132, 140, 148). The vertical segments run in the corridor between the zone edge and the consumer column, also y-staggered.
- **Z-order:** all connectors drawn **before** any rect (so node fills mask the line ends).
- **Markers:** exactly one `marker-end` per `<line>` / `<path>`. Never `marker-start`.
- **Labels:** every `primary`, `secondary`, `federated`, `auth` edge gets a protocol label (the `arrow-label` role at 8 px, paper-filled rect mask with 6–10 px clear gap above the stroke). `trigger` edges are unlabelled.

### 3.3 Footer → zone trunk

When N=1 footer: single vertical line at `x = zone_cx` from `footer_y(0)` to `zone_y + zone_h`.

When N≥2 footers: stagger AUTH lines so they don't overlap stacked footers. For footer index `k`:

```
footer_auth_x(k) = zone_cx + (k - (N-1)/2) * 32     # 32-px stride per footer
```

Examples:
- N=1 → 560
- N=2 → 544, 576
- N=3 → 528, 560, 592

Each AUTH line goes from `(footer_auth_x(k), footer_y(k))` up to `(footer_auth_x(k), zone_y + zone_h)`. AUTH labels sit just above the arrowhead at the zone bottom edge.

### 3.4 Crossings

Avoid. Re-route via the corridor x positions before accepting a crossing. If unavoidable, the path drawn second carries a 6-px arc hop over the first.

---

## 4. Component color override (mirrors `type-high-level.md` §3.4)

Any source, consumer, platform component (node or bar), or footer node accepts an optional `color: "#hex"`. Mirrors high-level so the rule reads identically across types.

**Where the color is applied** (`C = color`):

| Element | Light | Dark |
|---|---|---|
| Container fill (`rect` body) | `rgba(C, 0.06)` | `rgba(C_light, 0.10)` |
| Container stroke | `rgba(C, 0.35)` (`stroke-width=1` for nodes, `0.8` for bars) | `rgba(C_light, 0.45)` |
| Role badge stroke | `rgba(C, 0.40)` | `rgba(C_light, 0.55)` |
| Role badge text | `rgba(C, 0.85)` | `rgba(C_light, 1.0)` |
| Icon stroke / fill | `C` | `C_light` |
| Name text | `C` | `C_light` |
| Subtitle text | **unchanged** (muted) | **unchanged** (muted) |
| Connectors touching this component | **unchanged** — topology-driven | **unchanged** |

`C_light` = the same hex lightened ~15% for dark-mode contrast (e.g., `#b85450` → `#d97a78`).

**Rules:**

- **Never on focal components.** `focal_accent` always wins — a `color` on a focal component is ignored.
- **Never on connectors.** If you want a colored edge, pick a different `style` from §3, not a color override.
- **Cap at 2 custom-colored components** per diagram (in addition to the focal pair).

**Semantic palette** (use these unless brand demands otherwise):
- `#b85450` rust-red — Security / Identity (AD, Keycloak, Vault)
- `#5a7d9a` slate-blue — Observability (Prometheus, Datadog, OpenTelemetry)
- `#7a8c47` olive-green — Governance / Lineage (OpenMetadata, DataHub)
- `#8c6d3f` warm-brown — Backup / DR (Velero, Restic)

---

## 5. Focal rule

**Exactly two focal components.** Default: the storage hub (MinIO / S3 / similar) and the federation engine (Trino / Dremio / similar). These two surfaces distinguish a "platform" from a pile of tools. Everything else (NiFi, Jupyter, Airflow, AD, all sources, all consumers) stays ink / muted.

- Mark with `focal: true` on the component entry.
- A focal `kind: bar` uses `bar_h_focal=56` (taller) and accent styling.
- A focal `kind: row` node keeps `row_h=72` but uses accent styling.
- The **Trino → all consumers** edges are always `primary` (accent), regardless of focal flag on each consumer — this is the serve-flow rule.
- If fewer than 2 or more than 2 components are marked `focal: true`, halt and ask the user.

---

## 6. Dark mode

`paper`, `ink`, `muted`, `soft`, `accent`, and `link` invert with the skin: take their values from the dark column in [`style-guide.md`](style-guide.md). A **role at an opacity** needs no dark-mode handling, since `ink @ 0.32` resolves against whichever ink is active.

Only these differ between modes:

| Element | Light | Dark | Why it differs |
|---|---|---|---|
| Side-column fill | `muted @ 0.06` | `ink @ 0.06` | The slate tint reads as mud on dark paper; plain ink stays neutral |
| Side-column stroke | `soft` | `ink @ 0.30` | ditto |
| Zone fill | `ink @ 0.025` | `ink @ 0.04` | A wash needs slightly more presence on dark paper |
| Non-focal bar fill | `ink @ 0.05` | `ink @ 0.06` | ditto |
| Focal fill | `accent @ 0.08` | `accent @ 0.12` | ditto |

Unchanged across modes: zone stroke `ink @ 0.32`, focal stroke `accent`, and custom component colors (`C` light → `C_light`, lightened ~15%).

---

## 7. Reproducibility checklist (taste gate)

Before emitting SVG, verify **every** item:

1. `viewBox = "0 0 1200 {viewBox_h}"` where `viewBox_h = max(600, footer_bottom + 84)`.
2. Platform zone at `x=260 y=72 w=696 h=col_h`. Zone label paper-masked across top border at `y=zone_y+3`.
3. Left column at `x=40..200`, right column at `x=1000..1160` — both 160 wide.
4. Source / consumer rows top at `y=92`, stride 88 px.
5. `platform.rows` entries stack inside zone via the §2.1 cursor algorithm; total y-span ≤ `zone_h`.
6. Inside each `kind: row`, node x-centers are evenly spaced across zone width (§2.2).
7. **Exactly 2** focal components (`focal: true`).
8. Every edge originating from a `kind: bar` component uses `style: trigger` (dashed, unlabelled).
9. Every Trino → consumer edge uses `style: primary` (the serve-flow rule).
10. Footer nodes connect only to the zone bottom edge via `auth` style. **No** edge from a footer to a specific component.
11. Custom component colors ≤ 2 (in addition to the focal pair). Connectors never recolored by component `color`.
12. All connectors emitted before any node rect (z-order rule).

---

## 8. Sources and consumers — icon library

Define each icon as `<g id="ico-…">` in `<defs>`, drawn at translate(cx, cy) with `stroke="currentColor"` so it inherits the surrounding text color. Common icons:

- `ico-db` (cylinder) — relational sources
- `ico-sftp` (folder with down arrow) — file drops
- `ico-mail` (envelope) — email pulls
- `ico-mainframe` (server with vents) — legacy systems
- `ico-monitor` — desktop analytics tools
- `ico-chart` (bars) — BI / report tools
- `ico-globe` — public websites
- `ico-api` (brackets `{}`) — gateways and 3rd-party clients
- `ico-key` — identity / IDP
- `ico-monitoring` (chart-line) — observability stack

If you need more icons, browse `assets/icons.html` and define matching `<symbol>` blocks.

---

## 9. Identity, common services → connect to the layer, not to components

**Active Directory** (or Keycloak, IAM, OPA, any cross-cutting identity / policy / secrets store) authenticates *every* component in the platform. Wiring it to one specific tool would understate the trust scope. Connect it instead with a single arrow to the bottom edge of the platform zone, labeled `AUTH` (§3.3).

The same rule applies to any other layer-wide service: centralized logging, secrets vault, observability stack, audit sink, mTLS root. Each goes in the `footer` list, each gets its own row, each gets its own AUTH line up to the zone bottom edge (staggered by index per §3.3). The visual reading is "the platform layer delegates to all of these," which is the architectural truth.

---

## 10. Budget — this type exceeds the default

This is the one type where the default 9-node / 12-arrow budget is intentionally exceeded. A realistic platform integration shows:

- 4–6 source nodes
- 5 platform components
- 4–6 consumer nodes
- 1–3 footer nodes (identity, observability, backup, …)

That's **14–20 nodes**. The complexity is the point — the diagram is making a claim about the *number of distinct integration surfaces*. Compressing them collapses the claim.

When this gets unwieldy:
- Combine clearly-identical source rows (e.g., four MariaDB databases → one `Databases` node with sublabel `4 × MariaDB`)
- Split into two diagrams (one per integration plane: data vs. identity vs. observability)

---

## 11. Anti-patterns

- **Sources or consumers as a single collapsed node** when ≥3 distinct items exist — defeats the whole point of this type. Use Architecture or High-level if you want collapsing.
- **One bus arrow from "sources" to "the platform"** — every wire is labeled with its protocol; this is how integration teams read the diagram.
- **Per-tool color coding** (teal-NiFi, magenta-MinIO, yellow-Jupyter) inside the zone — collapses hierarchy; only the two focal accents earn coral, plus up to 2 custom colors on cross-cutting components (§4 cap).
- **More than 2 focal components** — focal exists to distinguish "platform" from "pile of tools"; >2 erases the signal (same rule as SKILL.md §1).
- **`color` override on a focal component** — ignored. Focal_accent always wins.
- **Footer wired to one specific tool** (e.g., AD → Airflow only) — wrong unless that service truly only protects one tool. The default is the layer-wide connection.
- **Footer or identity inside the zone** — identity gates the layer from outside. Drawing it inside misrepresents the trust model.
- **Phase chevrons across the top** — those belong on `high-level`.
- **Custom-colored connectors** — connectors are topology-driven. Style picks the color; `color` on a component never spreads to its edges.

---

## 12. Examples

- `assets/example-dp-integration.html` — minimal light (1 footer = AD). Gallery default.
- `assets/example-dp-integration-dark.html` — same, dark skin.
- `assets/example-dp-integration-full.html` — same, editorial-card frame.

---

See [type-dp-integration.md](type-dp-integration.md) for parameter contract and layout formulas.
