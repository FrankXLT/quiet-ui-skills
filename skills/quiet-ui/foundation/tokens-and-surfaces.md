# Quiet UI — Tokens and Surfaces

Surface polarity tokens, concentric corner geometry, and border hierarchy establish the physical substrate of every Quiet UI interface. This specification defines the 4-theme token contract, concentric radius math, the de-barnacling border depth rule, and the 4-way mirror parity governance system.

---

## 1. 4-Theme OKLCH Polarity Surface Contract

Quiet UI rejects arbitrary palette proliferation. All background, border, and text relationships are governed by four polarity themes bound to the root DOM node via `data-theme`:

| Token Role | `white` (Clinical / Bright) | `paper` (Warm Editorial) | `dark-paper` (Warm Charcoal) | `dark` (Deep Telemetry) |
| :--- | :--- | :--- | :--- | :--- |
| `--bg-shell` | `#EEF2F6` (Cool Slate Tint) | `#EAE5DC` (Warm Ochre Tint) | `#0D0C0B` (Smoked Umber) | `#05070B` (Abyssal Navy) |
| `--bg-canvas` | `#FFFFFF` (Pure Bright) | `#F6F4EF` (Book Linen) | `#141312` (Deep Charcoal) | `#090D16` (Deep Midnight) |
| `--bg-surface` | `#FFFFFF` (Flat Card Plane) | `#FCFBF8` (Uncoated Parchment) | `#1C1B19` (Card Charcoal) | `#0F1624` (Card Obsidian) |
| `--bg-card` | `var(--bg-surface)` | `var(--bg-surface)` | `var(--bg-surface)` | `var(--bg-surface)` |
| `--bg-elevated` | `#F8FAFC` (Header / Rail) | `#EFECE5` (Header / Rail) | `#252421` (Header / Rail) | `#172135` (Header / Rail) |
| `--bg-header` | `var(--bg-elevated)` | `var(--bg-elevated)` | `var(--bg-elevated)` | `var(--bg-elevated)` |
| `--bg-glass` | `rgba(255,255,255,0.88)` | `rgba(252,251,248,0.90)` | `rgba(28,27,25,0.88)` | `rgba(15,22,36,0.88)` |
| `--text-primary` | `#0F172A` (95% Contrast) | `#1C1917` (Stone Black) | `#F0EDE8` (Warm Milk) | `#F1F5F9` (Frost White) |
| `--text-secondary`| `#334155` (Slate Grey) | `#44403C` (Warm Ash) | `#C7C2BA` (Silver Drift) | `#CBD5E1` (Muted Ice) |
| `--text-muted` | `#475569` (Caption Slate) | `#57534E` (Caption Ash) | `#A19B93` (Deep Silver) | `#94A3B8` (Slate Fog) |
| `--border-hairline`| `#E2E8F0` (0.5px Optical) | `#E5E0D6` (0.5px Warm) | `#2E2C29` (Subtle Smoked) | `#1E293B` (Subtle Cyanide) |
| `--border-strong` | `#CBD5E1` (Focus / Heavy) | `#D6CFC5` (Focus / Heavy) | `#46433E` (Focus / Heavy) | `#334155` (Focus / Heavy) |
| `--accent-focal` | `#1D4ED8` (Focal Sapphire) | `#1E40AF` (Editorial Indigo) | `#60A5FA` (Luminous Sky) | `#38BDF8` (Signal Cyan) |

### DOM Attribute Contract
The root `html` element must declare the active theme via the `data-theme` attribute:

```html
<!DOCTYPE html>
<html lang="en" data-theme="white">
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="../tokens/quiet-ui-tokens.css" />
</head>
<body class="va-shell">
  <!-- Content renders within the specified theme context -->
</body>
</html>
```

---

## 2. Concentric Corner Radius Mathematics

Visual discord occurs when nested containers share identical corner radii or when inner corners collide with borders. Quiet UI enforces concentric curvature math across all card containers and child elements:

$$\text{Radius}_{\text{inner}} = \max(0\text{px}, \text{Radius}_{\text{card}} - \text{Padding}_{\text{inset}})$$

```
+------------------------------------------------------+  R_outer = 12px
|                      Padding = 4px                   |
|   +----------------------------------------------+   |
|   |                                              |   |  R_inner = max(0, 12 - 4) = 8px
|   |           Nested Interactive Surface         |   |
|   |                                              |   |
|   +----------------------------------------------+   |
+------------------------------------------------------+
```

### Radius Dial Values

| Setting (`data-corners`) | `--radius-card` | `--inset-pad` | `--radius-inner` | `--radius-sm` | `--radius-xs` | Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sharp` | `0px` | `0px` | `0px` | `0px` | `0px` | M1 High-density print, aerospace grids |
| `subtle` | `6px` | `4px` | `2px` | `4px` | `2px` | Compact telemetry dashboards |
| `auto` (Default) | `8px` | `4px` | `4px` | `6px` | `2px` | Standard stateful web applications |
| `rounded` | `12px` | `4px` | `8px` | `8px` | `2px` | Editorial web, walkup kiosks |
| `soft` | `18px` | `4px` | `14px` | `10px` | `2px` | Consumer portals, ambient wall views |

### 4-Variant `.va-pill` Geometry, Pill Restraint & Unified Corner Family
Quiet UI replaces generic `999px` pill sprawl with strict restraint (`@layer shell` in `src/css/03-pills-and-annunciators.css` and `01-stage-and-containers.css`):
- **Ban Passive `999px` Pills (`[PILL_SPRAWL]`)**: Dates, versions, counts, subtitles, commit hashes, and units MUST render as plain unboxed muted text (`.va-meta-inline` — `color: var(--text-muted); font-size: var(--ts-xs); font-variant-numeric: tabular-nums;`). File/mode switchers use clean underline or rectangular `--radius-sm` (`4–6px`) tabs (`.va-tab-strip` / `.va-tab`, or `[data-variant="segmented"]`) instead of stadium capsules alongside square toolbars.
- **Unified `.va-badge` Corners & Restraint**: `.va-badge` shares `border-radius: var(--radius-sm, 5px)` with buttons and toolbars (`<= 1` semantic state exception badge `HEALTHY`/`WARN`/`FAULT` per card header; `> 2` header pills or `>= 6` passive body pills fail `[PILL_SPRAWL]`).
- **Round = Clickable Invariant**: Non-interactive annunciators and keycaps (`status`, `tag`) use `--radius-xs` (`2px`, or `0px` under `sharp`). Full stadium curvature (`--radius-pill: 999px`) is strictly limited to isolated clickable `chip` controls (`<= 2` per header).
- **Zero-Inflation `18px` / `22px` Baseline Lock & Cohesive Chart Ramp**: `.va-pill[data-variant="status"]` / `tag` lock `18px` height (`min-block-size: 1.375rem` row, `<= 1.0px` baseline drift). All charts page-wide bind to the unified `--chart-1`..`--chart-5` semantic ramp (`--accent-primary`, `--tint-indigo-fg`, `--tint-emerald-fg`, `--tint-amber-fg`, `--text-muted`).
- **Chromium-Safe Chroma Mixing & Token Parity**: Excursion borders use `color-mix(in oklab, ...)` and static keycaps bind to `var(--border-subtle)` across all 4 `[data-theme]` blocks.

---

## 3. De-Barnacling Border Depth Rule

Card nesting often introduces visual clutter termed "barnacles" (excessive borders stacked inside borders). Quiet UI strictly limits nested borders:

> **The De-Barnacling Invariant**: A viewport path from shell to actionable leaf must cross at most **two visible concentric border lines** before incurring a design contrast violation.

1. **Outer Boundary**: The structural card container (`1px solid var(--border-hairline)`).
2. **Inner Division**: Internal partition lines, segment headers, or input borders (`1px solid var(--border-hairline)`).
3. **Tertiary Sub-elements**: Must use **background contrast** (`var(--bg-elevated)` or `var(--bg-surface)`) instead of a 3rd border.

```
[SHELL: --bg-shell]
  │
  ├── [CARD CONTAINER: 1px border-hairline] (Border #1)
  │     │
  │     ├── [SECTION DIVIDER: 1px border-hairline] (Border #2 - LIMIT REACHED)
  │     │     │
  │     │     └── [DATA ITEM CHIP: background-color only, NO BORDER]
```

---

## 4. 4-Way SHA-256 Token Mirror Parity

To prevent styling fragmentation across distributed tools and runtimes, canonical design tokens reside in 4 strictly synchronized files:

1. `tokens/quiet-ui-tokens.css` (Repository root canonical definition)
2. `skills/quiet-ui/tokens/quiet-ui-tokens.css` (Skill bundle mirror)
3. `customizations/personal-starter/styles/quiet-ui-tokens.css` (Personal starter mirror)
4. `customizations/brand-starter/styles/quiet-ui-tokens.css` (Brand starter mirror)

### Mirror Verification Protocol
Whenever tokens are modified or audited, run SHA-256 verification:

```bash
sha256sum \
  tokens/quiet-ui-tokens.css \
  skills/quiet-ui/tokens/quiet-ui-tokens.css \
  customizations/personal-starter/styles/quiet-ui-tokens.css \
  customizations/brand-starter/styles/quiet-ui-tokens.css | awk '{print $1}' | uniq
```

If the output yields more than one unique hash, token mirror parity is broken and CI compilation halts.

---

## 5. CSS Architecture & Concrete Layer Classes

```css
@layer quiet.tokens, quiet.surfaces, quiet.components, utilities;

@layer quiet.surfaces {
  .va-shell {
    background-color: var(--bg-shell);
    color: var(--text-primary);
    min-block-size: 100vh;
    font-family: var(--font-sans);
  }

  .va-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-hairline);
    border-radius: var(--radius-card);
    padding: var(--density-card-pad, 0.9rem);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  }

  .va-card-nested {
    background-color: var(--bg-elevated);
    border: 1px solid var(--border-hairline);
    border-radius: var(--radius-inner);
    padding: calc(var(--density-card-pad, 0.9rem) - 0.2rem);
  }

  .va-chip-leaf {
    background-color: var(--bg-canvas);
    border: none; /* De-barnacled: zero 3rd border */
    border-radius: var(--radius-xs); /* Interactive <button> chips promote via .va-pill[data-variant="chip"] */
    padding: 0.25rem 0.5rem;
    font-size: var(--ts-xs);
    color: var(--text-secondary);
  }

  .va-glass-surface {
    background-color: var(--bg-glass);
    backdrop-filter: blur(16px) saturate(140%);
    -webkit-backdrop-filter: blur(16px) saturate(140%);
    border: 1px solid var(--border-hairline);
    border-radius: var(--radius-card);
  }
}

@layer utilities {
  .hidden,
  [hidden]:not([hidden="until-found"]) {
    display: none;
  }
}
```

> [!IMPORTANT]
> Always declare `utilities` **last** in your `@layer ...;` statement and place `.hidden, [hidden]:not([hidden="until-found"]) { display: none; }` inside `@layer utilities` (`src/css/00-layers-and-reset.css`). Putting `.hidden` inside `@layer reset` or `@layer base` lets `display: flex` / `grid` in later layers (`shell`, `views`) override `.hidden` without `!important`, while `:not([hidden="until-found"])` keeps Find-in-page (`beforematch`) panels functional.

---

## 6. Anti-Patterns & Failure Modes

| Anti-Pattern | Why It Fails | Correct Architecture |
| :--- | :--- | :--- |
| Hardcoded Hex (`#ffffff`, `#111827`) | Breaks 4-theme swapping and optical inversion under dark-paper. | Use semantic tokens (`var(--bg-canvas)`, `var(--text-primary)`). |
| Uniform 12px Radius on Outer & Inner | Causes optical corner jamming where inner element cuts through margin. | Apply concentric formula: `var(--radius-inner) = max(0, card - inset)`. |
| 3+ Nested Border Lines | Creates visual noise ("barnacle cage") that degrades scan speed. | Replace inner borders with surface elevation tints (`var(--bg-elevated)`). |
| Per-Component Custom Themes | Destroys cognitive predictability across multi-panel interfaces. | Restrict surface tokens to the global `data-theme` scope. |
| `.hidden` in `@layer reset` or `@layer base` | Later layers (`display: flex` / `grid`) silently override `.hidden` (`[HIDDEN_LAYER]`). | Declare `utilities` last in `@layer` order and define `.hidden` inside `@layer utilities`. |
| Divergent Local Token Copies | Causes drift between local prototypes and production renders. | Enforce 4-way SHA-256 mirror parity check before commits. |
