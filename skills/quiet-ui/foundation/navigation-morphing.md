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

## 3. Foldable 820px–1050px Eyebrow Compaction

Dual-screen and foldable devices (e.g., 820px width) suffer from severe vertical fold congestion when stacked breadcrumbs, title bars, and status bars consume the top 450px of the viewport:

- **Full Desktop Mode ($\ge 1100\text{px}$)**: Eyebrow kicker, H1 title, status chips, and action buttons stack in three distinct horizontal rows.
- **Compact Eyebrow Mode ($820\text{px} - 1050\text{px}$)**: Eyebrow kicker and title compress into a single inline flex line; action buttons convert into icon-only pill triggers; status chips fold into a compact summary dropdown.

```
[Desktop Stack >= 1100px]
+---------------------------------------------------------------+
| KICKER: SUBSYSTEM / TELEMETRY                                 |
| H1: Orbital Propulsion Stage Array Analysis                   |
| Status: [ONLINE]  Version: 2.4.1  Timestamp: 14:02:11Z        |
+---------------------------------------------------------------+

[Compact Foldable 820px Eyebrow Line]
+---------------------------------------------------------------+
| SUBSYSTEM / H1: Orbital Propulsion Array  [ONLINE] [v2.4] [...]|
+---------------------------------------------------------------+
```

---

## 4. Mobile 390px Touch Hit Targets & KPI Strips

At mobile widths ($< 700\text{px}$ and down to 390px phone screens):
- **NASA-STD-3001 & WCAG 2.5.5 Touch Conformance**: All interactive touch targets must meet a hard floor of **$44\text{px} \times 44\text{px}$** (`--res-touch-min: 44px`).
- **Telemetry Inversion**: Heavy waveform charts or multi-series tables must not push key metrics below the fold. Place a compact **$2\times 2$ grid or horizontal swipeable KPI strip** directly above the primary canvas.

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

  /* Foldable Eyebrow Compaction */
  @media (min-width: 820px) and (max-width: 1050px) {
    .va-header-stack {
      display: flex;
      align-items: baseline;
      gap: 0.75rem;
    }
    .va-header-stack .va-kicker {
      margin-inline-end: 0.25rem;
    }
    .va-header-stack h1 {
      font-size: var(--ts-base);
      display: inline;
    }
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
| N4 Bottom Dock on 1440p desktop screen | Stretches 4 icons across 2560px bottom; looks broken and unprofessional. | Enforce N4 Desktop Ban: switch to N1 or N2 on screens $\ge 700\text{px}$. |
| Uncollapsed 3-row header on 820px foldable | Consumes 40% of the upper screen before any data or chart is visible. | Apply inline eyebrow compaction on viewports $820\text{px} - 1050\text{px}$. |
| Touch buttons under 44px on mobile | Operator mis-taps adjacent telemetry switches in high-stress field conditions. | Enforce `--res-touch-min: 44px` on coarse pointers and mobile viewports. |
| Navigation rails visible on printed reports | Wastes paper and inks useless software navigation links on static sheets. | Place `@media print { nav { display: none; } }` inside the terminal `@layer`. |
| Unclosable drawer overlay on small desktop | Obscures data table columns and prevents simultaneous inspection. | Auto-morph N1 from drawer to persistent rail at $\ge 1100\text{px}$. |
