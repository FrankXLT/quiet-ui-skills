# Quiet UI — Navigation Morphing & Shell Polymorphism

Quiet UI navigation shells morph dynamically across screen dimensions and delivery form factors. Rather than forcing a static desktop sidebar or an arbitrary mobile burger menu, Quiet UI defines five distinct shell archetypes (`N0` through `N4`), fold-aware eyebrow compaction, touch ergonomics, and strict media print stripping.

---

## 1. Five Polymorphic Navigation Shells

```
[N0: Undecorated Stage]  [N1: Persistent Left Rail]   [N2: Top Header Bar]
+---------------------+  +-------+------------------+  +---------------------+
| Clean Document Body |  | Rail  | Main Workspace   |  | Header Bar / Brand  |
| (M1 Print, M2 Mono) |  | >=1.1k|                  |  +---------------------+
+---------------------+  +-------+------------------+  | Body Stage          |
                                                       +---------------------+

[N3: Composite Header + Left Rail]     [N4: Mobile Bottom Dock]
+------------------------------------+  +---------------------+
| Header Bar (System Scope, User)    |  | Main Mobile Viewport|
+---------+--------------------------+  | Touch-Optimized     |
| Rail    | Primary Content Stage    |  +---------------------+
| Modules |                          |  | [1]  [2]  [3]  [4]  | (<700px)
+---------+--------------------------+  +---------------------+
```

### Shell Archetype Specification

| Shell Archetype | Structural Target | Viewport Range | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **N0** (Undecorated Stage) | Zero persistent navigation chrome. | Any viewport width | M1 Print, M2 Monograph briefs, M6 Optical HUD, clean standalone cards |
| **N1** (Adaptive Left Rail) | Persistent left rail $\ge 1100\text{px}$, slides into off-canvas drawer $< 1100\text{px}$. | $\ge 1100\text{px}$ rail, $< 1100\text{px}$ drawer | M3 Multi-module workbenches, telemetry dispatchers |
| **N2** (Adaptive Top Bar) | Sticky top banner with brand, primary status, and modal hamburger toggle. | $700\text{px}$ to $1920\text{px}$ | POI kiosks, briefing decks, documentation portals |
| **N3** (Composite Matrix) | Global horizontal header bar coupled with persistent domain left rail. | Ultra-wide displays ($\ge 1440\text{px}$) | Mission command systems, complex enterprise IDEs |
| **N4** (Mobile Bottom Dock) | Fixed bottom tab bar with thumb-accessible touch targets. | Strictly $< 700\text{px}$ | Handheld field tablets, mobile phones (390px) |

---

## 2. Desktop Ban on N4 Bottom Docks

> **The N4 Desktop Ban Rule**: An interface with `html[data-effective-nav="n4"]` is **strictly forbidden on viewports $\ge 700\text{px}$**. Desktop browsers must never render floating or fixed mobile thumb docks at the bottom of a wide screen.

Desktop layouts have expansive horizontal real estate. Placing mobile dock navigation on wide screens disrupts visual reading flow and introduces wasted vertical letterboxing.

---

## 3. Foldable >= 780px Split Reader, First-Screen & Sticky Budget

Dual-screen and unfolded foldable devices (e.g., `780px–1099px` width; Pixel/Galaxy Fold at `820px` CSS px) suffer from vertical fold congestion when stacked header rows consume the first screen or master-detail views fall back to full-screen modals instead of side-by-side split readers:

- **Full Desktop Mode ($\ge 1100\text{px}$)**: Eyebrow kicker, H1 title, status chips, and compact joined toolbar rows sit cleanly above content; split drawers open side-by-side.
- **Unfolded Foldable Mode ($\ge 780\text{px}$ to $1099\text{px}$)**: Lower the split-reader (`.va-split-reader`) and 2-column secondary chart/plot grid (`.va-chart-grid-2`, `.va-plot-row`, `.va-plot-grid`) breakpoint to **`>= 780px`** so side-by-side panes and `subgrid` plot cards stay open concurrently at `820px` instead of triggering modal overlays.
- **Sticky Chrome Budget (`<= 64px` `>= 680px` / `<= 88px` `< 680px`)**: Sticky topbars MUST fit on a single row (`<= 56px` target, `<= 64px` `[STICKY_CHROME_BLOAT]` cap) on `>= 680px` foldable & desktop viewports, and allow up to `<= 88px` (2 compact rows: brand/menu + `.va-period-stepper`/`.va-scope-chip`) on `< 680px` portrait handsets. Set `scroll-padding-top` to clear sticky bars, keep detail inspector headers `<= 96px`, collapse `0`-issue audit tables inside `<details>`, and avoid floating section jump rails on continuous scroll pages.

```
[Desktop Stack >= 1100px]
+---------------------------------------------------------------+
| KICKER: SUBSYSTEM / H1: Propulsion Array  [ONLINE] [v2.4]     |
+---------------------------------------------------------------+

[Compact Foldable 780px..1099px Eyebrow Line (<= 56px sticky)]
+---------------------------------------------------------------+
| SUBSYSTEM / H1: Propulsion Array         [ONLINE] [Filter v]  |
+---------------------------------------------------------------+
```

---

## 4. Coarse-Pointer `44px` Interactive vs. `20–22px` Badges & KPI Strips

Across handsets (`< 700px` / `390px`) and coarse-pointer tablets/foldables (`>= 768px`):
- **Interactive-Only `44px` Hit Targets**: `@media (pointer: coarse)` `44x44px` sizing applies **only to interactive controls** (`button`, `a[href]`, `select`, `input`, `[role="button"]`, `[role="tab"]`, `[role="checkbox"]`) on `< 700px` handsets (or coarse `< 768px`).
- **Compact `20–22px` Read-Only Badges**: Static `.va-pill` status/tag labels (`.va-pill:not(button):not(a):not([role="button"]):not([role="tab"])`) and `.va-badge` pills MUST stay `20–22px` tall (`2–4px` vertical pad) on phones, tablets, and foldables so metadata never inflates into `40px` button lookalikes.
- **Tablet & Foldable Joined Toolbars (`>= 768px`)**: On `pointer: coarse` tablets and unfolded foldables (`>= 768px`), `.va-toolbar-joined` segments use `32–34px` visual height (`44px` visual height applies strictly `< 700px`).
- **Overlay Corner Hit Boxes (`.va-overlay-control`)**: Corner controls keep a `20–24px` visible circle and provide `44x44px` touch tolerance via an invisible `::after { inset: -11px; }` pseudo-element.
- **Telemetry Inversion**: Place a compact **$2\times 2$ grid or swipeable KPI strip** directly above primary handset charts.

---

## 5. Media Print Shell Stripping

Paper output must represent raw data without software navigation chrome:

> **Print Stripping Invariant**: In `@media print`, all navigation rails, top headers, bottom docks, hamburger buttons, and modal drawers must be completely removed from layout flow (`display: none` inside the final cascade layer).

---

## 6. Concrete CSS Architecture

```css
@layer quiet.navigation, quiet.responsive, quiet.print;

@layer quiet.navigation {
  /* N1 Left Rail */
  .va-nav-rail {
    position: fixed;
    inset-block-start: 0;
    inset-inline-start: 0;
    inline-size: 240px;
    block-size: 100vh;
    background: var(--bg-elevated);
    border-inline-end: 1px solid var(--border-hairline);
    padding: 1.5rem 1rem;
    z-index: 100;
  }

  /* N4 Mobile Bottom Dock */
  .va-nav-dock {
    position: fixed;
    inset-block-end: 0;
    inset-inline: 0;
    block-size: 56px;
    background: var(--bg-surface);
    border-block-start: 1px solid var(--border-hairline);
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 200;
  }

  .va-nav-dock a,
  .va-nav-dock button {
    min-inline-size: var(--res-touch-min, 44px);
    min-block-size: var(--res-touch-min, 44px);
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  /* Unfolded Foldable & Desktop >= 60% Prose Split Reader + < 760px Modal Sheet */
  .va-split-reader-gallery { display: grid; grid-template-columns: minmax(0, 1fr); gap: 0.75rem; }
  .va-split-reader-primary, .va-split-reader-companion { min-inline-size: 0; }
  @media (min-width: 760px) {
    .va-split-reader-gallery { grid-template-columns: minmax(0, calc(64% - 0.375rem)) minmax(0, calc(36% - 0.375rem)); }
    .va-chart-grid-2, .va-plot-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
  }
  @media (min-width: 1280px) {
    .va-split-reader-gallery { grid-template-columns: minmax(0, calc(60% - 0.375rem)) minmax(0, calc(40% - 0.375rem)); }
  }
  dialog.va-modal-sheet[open] {
    display: flex; flex-direction: column; max-inline-size: min(44rem, calc(100dvw - 1.5rem));
    max-block-size: min(86svh, 46rem); background: var(--bg-surface); border: 1px solid var(--border-strong);
  }
  dialog.va-modal-sheet:modal { overscroll-behavior: contain; }
  dialog.va-modal-sheet::backdrop { background: rgba(15, 23, 42, 0.56); overflow: hidden; overscroll-behavior: contain; }
  @media (min-width: 780px) and (max-width: 1099px) {
    .va-header-stack { display: flex; align-items: baseline; justify-content: space-between; gap: 0.75rem; }
    .va-header-subbar { display: none; }
  }
}

/* Strict Media Print Stripping (final @layer beats base navigation rules without !important) */
@media print {
  @layer quiet.print {
    .va-nav-rail,
    .va-nav-dock,
    .va-nav-top,
    .va-btn-drawer,
    dialog.va-modal-sheet,
    header[role="banner"],
    nav {
      display: none;
    }

    body {
      padding: 0;
      margin: 0;
      background: #FFFFFF;
      color: #000000;
    }
  }
}
```

---

## 7. Overlay Filter Rails (`.va-side-rail`), Single-Row Footer, Split Sheets & Anti-Patterns

- **Single-Row `.va-rail-footer` (`40px`), Swatch Rail & 2-Stop Density Cap**: Keep a permanent drawer trigger at the far left of `.va-shell-topbar` (`[NAVBAR_SHIFT]`), keep `.va-period-stepper` / `.va-preset-popover` and `.va-scope-chip` in the topbar, and consolidate `.va-rail-footer` into a **single horizontal `40px` `space-between` row** pairing `.va-swatch-row` circular swatch triggers (`.va-swatch-btn`, `20px` dot with `44×44px` `::after` coarse hit area, active ring, `aria-label`, zero text) on the left with a **2-stop density toggle (`Compact | Comfortable`)** on the right. Never stack multiple footer rows, `3+` density stops, `Lock`, `< Classic`, or version pills (`[DENSITY_STOP_SPRAWL]`, `[RAIL_FOOTER_CLUTTER]`).
- **Flat Borderless Rail Trees (`<= 5` Visible Children + `.va-tree-more`) & `>= 60%` Split Reader / `<dialog closedby="any">`**: Inside `.va-side-rail`, render borderless single-line `36px` `.va-tree-row` links with `.va-tree-label` ellipsis, `<= 1` trailing `.va-tree-action`, and `<= 5` visible children in `.va-tree-children` followed by `.va-tree-more` (`+ Show N older…`), flagging nested `.va-card` boxes (`[TREE_NESTED_CARD_BORDERS]`). Use `.va-split-reader-gallery` (`>= 60%` prose width at `>= 760px`, hiding `.va-split-mode-toggle` `< 760px` behind `.va-split-sheet-trigger` -> `<dialog class="va-modal-sheet" closedby="any">`, suppressing global key shortcuts while `dialog[open]`), and render `<= 6` sibling tabs via `.va-tab-strip` / `.va-tab`.

| Violation | Problem Caused | Architectural Solution |
| :--- | :--- | :--- |
| N4 Bottom Dock on `>= 700px` screens | Stretches icons across bottom; breaks tablet/desktop chrome. | Enforce N4 Desktop Ban: switch to N1 or N2 on screens $\ge 700\text{px}$. |
| Stacked `.va-rail-footer` or `3+` density buttons | Bloats drawer footer with `Lock`/`< Classic`/multi-row pills (`[RAIL_FOOTER_CLUTTER]`, `[DENSITY_STOP_SPRAWL]`). | Single `40px` `space-between` row: `.va-swatch-row` left + `2`-stop `Compact \| Comfortable` right. |
| Nested bordered cards inside `.va-side-rail` tree | Creates visual clutter and pushes old trees past fold (`[TREE_NESTED_CARD_BORDERS]`). | Flat borderless `36px` `.va-tree-row` (`<= 1` `.va-tree-action`) + `<= 5` child cap + `.va-tree-more`. |
| Conditional header buttons shifting brand/tabs across routes | Shifts global brand/tab strip horizontally across views (`[NAVBAR_SHIFT]`). | Keep persistent left-of-brand drawer trigger & fixed `.va-shell-topbar` slots. |
| Transparent drawer overlay or `< 55%` cramped prose split | Copy bleeds through (`[TRANSPARENT_OVERLAY]`) or prose wraps awkwardly (`[PROSE_PANE_CRAMPED]`). | Opaque `.va-side-rail`, `.va-split-reader-gallery` (`>= 60%` prose), `< 760px` `<dialog closedby="any">`. |
| `> 6` temporal buttons or clipped `.va-pane-hdr` | Compresses filter bars (`[TOOLBAR_CONTROL_SPRAWL]`, `[PANE_CONTROL_CLIPPED]`). | Consolidate presets in `.va-period-stepper` + `.va-preset-popover` and `.va-tab-strip`. |
| Sticky bar `> 88px` phone or `> 64px` desktop | Steals first viewport height (`[STICKY_CHROME_BLOAT]`). | Fit `<= 64px` single row `>= 680px` (`<= 88px` `< 680px`) + `<details>` tables. |
| Unscoped `dialog { display: flex }` without `[open]` | Traps backdrop behind normal flow and leaks scroll to underlying page. | Scope `display: flex` to `dialog.va-modal-sheet[open]`; lock `:modal`/`::backdrop` scroll. |
| Navigation rails visible on printed reports | Wastes paper and inks interactive navigation links on sheets. | Place `@media print { nav { display: none; } }` inside the terminal `@layer`. |
