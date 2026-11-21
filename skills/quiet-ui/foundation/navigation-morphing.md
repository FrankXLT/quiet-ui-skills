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
- **First-Viewport Chrome Budget (`<= 56px` Sticky / `<= 96px` Inspector Header)**: Sticky/fixed top bars MUST fit on **one single `space-between` row (`<= 56px` tall)** (`<= 64px` audited cumulative cap `[STICKY_CHROME_BLOAT]`; hide mode-specific filter strips when viewing other modes, and set `scroll-padding-top` so focused targets clear sticky bars). Detail/inspector headers must stay **`<= 2` compact rows (`<= 96px`)** so primary content starts within the top 30% of the screen, and `0`-issue diagnostic/audit tables should collapse inside `<details>` by default (`ISA-101` quiet nominal principle).
- **Zero Synthetic In-Page Jump Sidebars**: Never invent a floating or left-rail section jump menu (`6–7` anchor links) for a single vertically scrollable page unless genuine multi-view route state requires navigation.

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

  /* Unfolded Foldable >= 780px Split Reader + Sticky < 1100px Single-Row Compaction */
  @media (min-width: 780px) {
    .va-split-reader {
      display: grid;
      grid-template-columns: minmax(15rem, 36%) minmax(0, 1fr);
      gap: 0.75rem;
    }
    .va-chart-grid-2, .va-plot-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.75rem;
    }
  }
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

## 7. Anti-Patterns & Operational Violations

| Violation | Problem Caused | Architectural Solution |
| :--- | :--- | :--- |
| N4 Bottom Dock on `>= 700px` screens | Stretches icons across bottom; breaks tablet/desktop chrome. | Enforce N4 Desktop Ban: switch to N1 or N2 on screens $\ge 700\text{px}$. |
| Inventing an in-page jump sidebar on one continuous scroll page | Wastes horizontal space and fabricates fake multi-view navigation. | Omit left section-jump rails; use compact top section pills if needed. |
| Stacked multi-row sticky header `> 64px` (`[STICKY_CHROME_BLOAT]`) | Steals top viewport height on `390px` phones and `820px` foldables. | Fit sticky bars on 1 single row (`<= 56px`), hide unused mode controls, collapse `0`-issue tables in `<details>`. |
| Full-screen modal viewer at `820px` foldable width | Hides master list because split waited for `860–1200px`. | Lower split-reader & 2-col plot grid threshold to `>= 780px` (`820px` CSS tested). |
| Coarse-pointer `44px` rule inflating static `.va-badge`/`.va-pill` labels or `44px` filled thumbnail circles | Turns compact metadata chips into button lookalikes and obscures media. | Scope `44px` strictly to interactive controls `< 700px`, use `32–34px` toolbars `>= 768px`, and extend corner overlays via invisible `::after`. |
| Navigation rails visible on printed reports | Wastes paper and inks interactive navigation links on sheets. | Place `@media print { nav { display: none; } }` inside the terminal `@layer`. |
