# High-Level Architecture — Connectors, Branching & Examples

Companion reference for high-level container architecture diagrams covering connector rules, branching, chevrons, and examples.

## 3. Connector rules (mandatory)
These are non-negotiable. Pick the style **automatically** from the topology — do not let the user override style on focal-touching or bar-originating edges.

| `style` | Stroke | Width | Dash | Marker | When required |
|---|---|---|---|---|---|
| `primary` | `accent` | 1.2 | — | `arrow-accent` | Every edge whose endpoint is the `focal` node. |
| `secondary` | `muted` | 1.0 | — | `arrow` | Default for source→component and component→component when neither endpoint is focal. |
| `trigger` | `muted` | 1.0 | `4,3` | `arrow-sm` | Every edge originating from a `kind: bar` component. |
| `query` | `ink @ 0.30` | 1.0 | `4,3` | `arrow` | Read-back edges (e.g., focal ↔ Trino). |

**Defs block** (required, exactly these four markers):

```svg
<defs>
  <marker id="arrow"        markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{muted}"/></marker>
  <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{accent}"/></marker>
  <marker id="arrow-sm"     markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto"><polygon points="0 0, 6 2.5, 0 5" fill="{muted}"/></marker>
  <marker id="arrow-dim"    markerWidth="8" markerHeight="6" refX="7" refY="3"   orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ink @ 0.45}"/></marker>
</defs>
```

### 3.1 Exit / entry sides (non-negotiable)

| Edge kind | Exit side of source | Entry side of target |
|---|---|---|
| Source → cluster node | **right** of source node | **left** of target |
| Component → component (within cluster) | **right** | **left** |
| Bar component → node | **bottom** of bar | **top** of node |
| Cross-cutting bar | — (emits no edges) | — |
| Vertical chevron | — (labels only; emits no edges) | — |

### 3.2 Routing

- Orthogonal elbows, **at most two bends** per path.
- Use a Q-bezier 8-px corner radius at every bend.
- Z-order: draw **all connectors before any node rectangle** (so node fills mask the line ends).
- Exactly one `marker-end` per `<path>` / `<line>`. Never both `marker-start` and `marker-end`.
- Labels: every `primary` and `secondary` connector gets a label (small mono, opaque paper-filled rect mask behind). `trigger` and `query` connectors are unlabelled.

### 3.3 Crossings

- Avoid. Re-route via the chevron divider trunk (§4) before accepting a crossing.
- If unavoidable, the path drawn second carries a 6-px arc hop over the first.

### 3.4 Component color override

A component may declare an optional `color: "#hex"` (CSS color string). The override **only** retints the component's container and content — connectors are never recolored. Edges keep their topology-driven style from §3.

**Where the color is applied** (given `C = color`):

| Element | Light mode | Dark mode |
|---|---|---|
| Container fill (`rect` body) | `rgba(C, 0.06)` | `rgba(C, 0.10)` |
| Container stroke | `rgba(C, 0.35)` (`stroke-width=1` for nodes, `0.8` for bars) | `rgba(C, 0.45)` |
| Role badge stroke (nodes) | `rgba(C, 0.40)` | `rgba(C, 0.55)` |
| Role badge text (nodes) | `rgba(C, 0.85)` | `rgba(C, 1.0)` |
| Icon fill / stroke | `C` | lighten `C` by ~15% (or use `C` if already light) |
| Name text | `C` | lighten `C` |
| Subtitle text | **unchanged** (`muted`) | **unchanged** (`muted`) |
| Connectors touching this component | **unchanged** (still topology-driven) | **unchanged** |

The subtitle stays muted because it's parenthetical metadata — only the primary identity (name + icon + border) carries the color signal.

**Rules**:

- **Never on the focal node.** The focal node is already colored with the accent (§2.7). A `color` on the focal node is ignored — accent wins.
- **Never on source nodes.** Sources live outside the cluster and stay neutral.
- **Cap at 2 custom-colored components** per diagram (in addition to the focal). Three or more colored things erases the signal — the same reason §1 limits accent to 1–2 elements.
- **No color on connectors.** If you find yourself wanting a colored edge, the right move is to pick a different `style` from §3, not to override.

**Semantic uses** (recommended):
- `#b85450` (rust-red) — Security / Identity (Keycloak, Vault)
- `#5a7d9a` (slate-blue) — Observability (Prometheus, Datadog)
- `#7a8c47` (olive-green) — Governance / Lineage (OpenMetadata)
- `#8c6d3f` (warm-brown) — Backup / DR

Stick to these unless the user's brand demands otherwise. Random hex per component is exactly the failure mode this skill avoids.

---

## 4. Block branching rules (fan-out)

The single biggest reproducibility hazard. Fix these rules and the diagram becomes predictable.

### 4.1 Source fan-out (one source → N components)

```
exit_x   = source.right
trunk_x  = cluster_x - 8                     # 4-px gutter before cluster border
```

Path per target: `M exit_x,source_cy → H trunk_x → V target_cy → H target.left`. Use Q-bezier corners.

### 4.2 Component fan-out (one component → N components)

```
exit_x   = node.right
trunk_x  = x_boundaries[index(source.chevron) + 1] + 4   # 4 px past the chevron divider
```

Path per target: `M exit_x,source_cy → H trunk_x → V target_cy → H target.left`.

### 4.3 Fan-out cap

**Max 3 outgoing edges per node.** Above 3, introduce a hub (usually the `focal` node). The chevron banner is the legend; if a node is fanning out to four downstream targets, it's secretly the hub — make it explicit.

### 4.4 Bar drops (Airflow → N nodes)

```
drop_x(target) = target.cx
drop_y_start   = bar.bottom
drop_y_end     = target.top
```

Straight vertical line, `style: trigger`. One per target. No bends — bar drops never elbow.

### 4.5 Source vertical staggering

When multiple sources connect to the same single target (e.g. four sources → NiFi), stagger their entry y on the target:

```
entry_y(k) = target.top + 8 + k * (target_h - 16) / (N - 1)   # k = 0..N-1, evenly spaced
```

This avoids overlapping arrowheads at the target's left edge.

---

## 5. Vertical chevrons — semantics

Reserved names `Orchestration`, `Security`, `Observability`, `Governance`, `Backup` always render in the right strip (§2.9). Any chevron with `vertical: true` is treated as a reserved-style vertical regardless of name. The rules:

- **Pairing rule (mandatory, 1:1):** every vertical chevron pairs with exactly one cross-spanning component, and every cross-spanning component pairs with exactly one vertical chevron. The two component kinds that pair:
  - `kind: bar` — lives inside the cluster (top row). Conventionally paired with `Orchestration`.
  - `kind: cross-cutting` — lives below the cluster, one row per component. Paired with `Security`, `Observability`, `Governance`, etc.

  If the inputs declare a vertical chevron without a paired component (or vice versa), halt and ask the user — the diagram is incomplete.

- **Count constraint:** `len(verticals) == len(bars) + len(crosscuts)`. The right strip is split evenly among all verticals (§2.9), so visual alignment between a chevron and its bar/row is approximate — the *label* is what matters, not the y-pixel match.

- **Ordering convention:** declare verticals top-down in the order: bar-paired first (Orchestration), then crosscut-paired in the same order the crosscuts appear below the cluster. This keeps the visual reading order consistent.

- **No edges:** vertical chevrons emit no connectors themselves. They are *labels for a column of cross-cutting concern*.

- **No node placement:** no `kind: node` may be assigned to a vertical chevron. Nodes always belong to a horizontal phase.

- **Right strip presence:** if any vertical chevron exists, the right strip is reserved (`effective_w = 964`) and **all** horizontal chevron widths and cluster geometry shrink accordingly. Do not draw a vertical chevron on top of the cluster.

The visual contract: the vertical chevron's column visually "owns" the bar/cross-cutting row at its approximate y-band. Orchestration (top of strip) ↔ Airflow bar (top of cluster). Security ↔ Identity bar. Observability ↔ monitoring bar (below identity). And so on.

---

## 6. Dark mode

`paper`, `ink`, `muted`, and `accent` invert with the skin: take their values from the dark column in [`style-guide.md`](style-guide.md). Every derived value in this reference is a **role at an opacity**, so `ink @ 0.18` resolves to dark ink on light paper and light ink on dark paper with no extra handling.

Only these differ between modes:

| Element | Light | Dark | Why it differs |
|---|---|---|---|
| Muted text | `muted` | `ink @ 0.65` | Dark mode softens secondary text by opacity rather than by hue |
| Dashed border | `ink @ 0.20` | `ink @ 0.22` | A hairline needs marginally more presence on dark paper |
| Node fill | `#ffffff` (white) | `ink @ 0.06` | White is opaque; on dark paper the node lifts off the ground instead |
| Node stroke | `ink @ 0.25` | `ink @ 0.20` | Light ink on dark paper reads stronger at equal opacity |
| Focal fill | `accent @ 0.08` | `accent @ 0.12` | ditto |
| Phase bands | `band-1` / `band-2` | `band-2` / `band-3` | The alternation shifts one step lighter (§6.1) |

Unchanged across modes: cluster border `ink @ 0.18`, dot pattern `ink @ 0.10`, focal stroke `accent`, accent connector `accent`, and the chevron label, which is always `band-label`.

### 6.1 Phase-band palette

The chevron banner needs a **dark band with a light label in both modes**. `ink` and `paper` swap places between modes, so the banner can't be built from them. It uses four fixed tokens that ignore the light/dark flip:

| Token | Value | Use |
|---|---|---|
| `band-1` | `#2d3142` | Darkest step: odd chevrons, light mode |
| `band-2` | `#3d4460` | Middle step: even chevrons light, odd chevrons dark |
| `band-3` | `#4a5270` | Lightest step: even chevrons, dark mode |
| `band-label` | `#f5f5f5` | Fixed label color: 11.82:1, 8.78:1, and 7.05:1 against the three bands |

**These are type-scoped tokens, not skin roles, and they do not invert.** They are the one deliberate exception to the rule that hex values live only in [`style-guide.md`](style-guide.md). `scripts/lint-skin.py` rejects `band-2` and `band-3` as off-palette, which is why the shipped high-level examples are listed in `scripts/lint-skin-baseline.txt`. Phase labels always use `band-label`, and `band-label` has to hold at least 4.5:1 against every band, because these are 7px labels in either mode. When you re-skin, derive three analogous steps from the new brand's darkest neutral and pick a fixed label color that holds 4.5:1 against all three.

---

## 7. Reproducibility checklist (the taste gate)

Before emitting SVG, verify **every** item. If any fails, fix it — don't ship.

1. Every cluster `node.cx` equals its chevron's `cx` (§2.2 + §2.7). This is what makes the chevron banner a real legend.
2. Every chevron `width` is a multiple of 4 and ≥ 120.
3. The reserved right strip (28 px) exists **iff** any vertical chevron is declared. If yes, `effective_w = 964`; if no, `effective_w = 1000`.
4. Exactly **one** `focal` node. If `focal` is unset in inputs, default to the first `kind: node` under chevron "Storage".
5. Every edge whose endpoint is the focal node uses `style: primary` (accent stroke + `arrow-accent` marker).
6. Every edge originating from a `kind: bar` component uses `style: trigger` (dashed + `arrow-sm`).
7. The cross-cutting bar (if any) emits **no** edges.
8. No node has > 3 outgoing edges, or if it does, it is the declared `focal` / hub.
9. All `<path>` and `<line>` connectors are emitted **before** any node `<rect>` (z-order).
10. Each vertical chevron pairs **1:1** with exactly one `bar` or `cross-cutting` component (§5 pairing rule). `len(verticals) == len(bars) + len(crosscuts)`.
11. `viewBox_h = max(540, strip_y_bot + 112)` — grow the canvas when multiple crosscuts are declared so the legend still fits.
12. Custom component colors (§3.4) apply only to container + icon + name; connectors stay topology-driven. Cap at 2 custom-colored components in addition to the focal.
13. The diagram passes SKILL.md §9 (4-px grid; ≤ 2 accent elements; mono only for technical content; hairlines; no shadows; no `rounded-2xl`).

---

## 8. Anti-patterns

- Chevron banner omitted — it's the key that maps visual columns to functional phases.
- Node x-center off-chevron (§7 #1) — breaks the "banner-as-legend" contract.
- Vertical chevron drawn on the cluster (overlay) instead of in a reserved right strip.
- More than one focal node — MinIO/S3 (or whichever storage hub) is *the* focal point.
- External zone with solid border — dashed border is the signal that these components are outside the cluster.
- Identity bar inside the cluster boundary — it applies to all components and must span the full canvas width.
- Vertical chevron without a paired bar/cross-cutting component — see §5 pairing rule.
- Bar-component edges drawn solid — orchestration triggers must be dashed.
- Source fanning out to >3 components without a hub.

---

## 9. Examples

- `assets/example-high-level.html` — horizontal-only, 5 phases, light skin.
- `assets/example-high-level-dark.html` — same, dark skin.
- `assets/example-high-level-full.html` — same, editorial-card frame.
- `assets/example-high-level-vertical.html` — adds vertical Orchestration + Security chevrons, Airflow bar, Keycloak cross-cutting. **Reference render of the full parametric pattern.**
- `assets/example-high-level-vertical-dark.html` — vertical pattern, dark skin.
- `assets/example-high-level-vertical-full.html` — vertical pattern, editorial-card frame.
- `assets/example-datalake.html` — unclustered five-phase data stack (Sources → Ingest → Data Lake → Query → Consume), zone-based flow without a container-orchestrator boundary. The MinIO lake is the focal node; vertical concerns are flattened into the horizontal chevron banner. Light skin.
- `assets/example-datalake-dark.html` — same, dark skin.
- `assets/example-datalake-full.html` — same, editorial-card frame.

---

See [type-high-level.md](type-high-level.md) for inputs schema and layout formulas.
