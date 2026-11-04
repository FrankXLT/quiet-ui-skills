# Tiers 01 to 06: Editorial Publications, Theme-Aware Mermaid Diagrams & Parametric Document Bridge

Under `data-corners="auto"` (default) or `data-corners="sharp"`, all tiers in this module enforce `border-radius: 0px !important; box-shadow: none !important;` on structural frames while preserving rounded `.va-pill-btn` interactive affordances.
- **Zero SaaS Account Clutter Law:** Never render `.va-account-pod` (`AR · Author`) or `toggleAccountPopover` triggers inside Editorial tiers (`01. Doc-1` through `06. Bridge-1`).

## 01. Tier `Doc-1`: Academic & Scientific Monograph (`0%` Box Weight, Default `S2` Paper, `N1`)
- **Grid:** `max-width: 1260px; margin: 0 auto; padding: 2.25rem 2rem; display: grid; grid-template-columns: 200px minmax(0, 68ch) 230px; gap: 2.75rem;`
- **Left Column (`200px`):** Sticky outline Table of Contents (`border-top: 2px solid var(--border-strong)`) with a `.va-hamburger-btn` (`toggleLeftRailCollapse()`) that collapses the outline to a compact `60px` rail.
- **Center Column (`68ch`):** `var(--font-serif)` prose (`1.08rem`, `line-height: 1.68`), `var(--font-sans)` numbered section headers (`1.0`, `2.0`), flat bottom-bordered `[/]` section filter input, horizontal-rule display equations with `(Eq. 1.1)` right-aligned numbers, and click-to-sort `table.booktabs` (`2px` top/bottom rules, `1px` header rule, zero vertical lines).
- **Right Column (`230px`):** Margin `.sidenote-box` items (`border-left: 1px solid var(--border-grid); padding-left: 0.75rem; font-size: 11.5px;`) that highlight when hovering superscript `[1]` references.

## 02. Tier `Doc-2`: Executive Decision Memo (`BLUF` + Mermaid) (`15%` Box Weight, Default `S2` Paper, `N0`)
- **Container:** `max-width: 820px; margin: 0 auto; padding: 2rem 2rem 4rem;`
- **4 Core Architectural Elements:**
  1. **Top BLUF Decision Ledger (`.bluf-frame`):** `border: 1px solid var(--border-strong); border-top: 4px solid var(--border-strong); background: var(--bg-card);` containing a 4-column hairline metadata strip above a Bottom Line Up Front synthesis paragraph.
  2. **Mid-Page 4-Cell Hairline Metric Strip (`.kpi-4strip`):** `border-top: 2px solid var(--border-strong); border-bottom: 1px solid var(--border-strong); display: grid; grid-template-columns: repeat(4, 1fr);`.
  3. **Theme-Aware Mermaid Architecture Figure (`.va-mermaid-figure`):** Multi-node architecture decision flowchart (`<svg class="va-mermaid-svg">`) with a `[Diagram | Mermaid Source]` toggle button (`toggleMermaidSource(this)`) revealing `<pre class="va-mermaid-code">`.
  4. **Asymmetric Left-Rule Risk Callout (`.risk-left-bar`):** `border-left: 3px solid var(--status-err); background: var(--bg-card); padding: 0.75rem 1.1rem;`.

## 03. Tier `Doc-3`: Normative RFC Specification (`25%` Box Weight, Default `S1` White, `N0`)
- **Container:** `max-width: 900px; margin: 0 auto; font-family: var(--font-mono); font-size: 12.5px;`
- **6 Mandatory Components:**
  1. Top `2px`-bordered Specification Metadata Table (`Document ID`, `Status: PROPOSED STANDARD`, `Category`, `Authors`, `License: MIT`).
  2. Interactive Normative Clause Filter Bar (`ALL`, `MUST`, `MUST NOT`, `SHOULD`).
  3. Bordered Normative Requirements Table (`table.rfc-grid`) with `1px` bordered `.req-badge` tags.
  4. **Theme-Aware Mermaid State Machine (`.va-mermaid-figure`):** Visual `stateDiagram-v2` SVG (`IDLE_UNLOCKED` $\rightarrow$ `FREQ_LOCK_ACQ` $\rightarrow$ `PHASE_CALIBRATE` $\rightarrow$ `PHASE_ALIGNED` $\rightarrow$ `HOLDOVER_FAULT`) with `[Diagram | Mermaid Source]` toggle.
  5. Character-grid ASCII State Machine inside a bordered `<pre>` block.
  6. Unified configuration schema diff block (`-` removal / `+` addition lines).

## 04. Tier `Doc-4B`: Encyclopedic SDK & API Reference (`25%` Box Weight, Default `S1` White, `N3`)
- **2-Column Shell:** `display: grid; grid-template-columns: 250px minmax(0, 1fr); width: 100%; max-width: 100%;` with clean N3 topbar and `.va-hamburger-btn` collapsible left symbol index.
- **Right Column (`84ch`):** Summary operations matrix (`table.booktabs`) + nested semantic definition lists (`<dl>` / `<dt class="sig-band">` / `<dd class="sig-body">`) + `.doctest-box` with `[>>>]` prompt stripper.

## 05. Tier `Doc-4A`: Split-Pane Operational Runbook (`45%` Box Weight, Default `S1` White, `N1`)
- **Full-Stage 3-Pane Split (`width: 100%; max-width: 100%; display: grid; grid-template-columns: 230px minmax(0, 1fr) 430px;`):**
  - Left (`230px`): Sticky runbook step index with `.va-hamburger-btn` rail collapse.
  - Center (`72ch`): **Theme-Aware Mermaid Sequence Diagram (`.va-mermaid-figure`)** (`Operator CLI` $\rightarrow$ `Primary GM-A` $\rightarrow$ `Sector-7 FPGA` $\rightarrow$ `Standby GM-B`) + unboxed `.step-anchor` procedural blocks. Clicking any step syncs the right console.
  - Right (`430px`): Sticky dark code console (`YAML / systemd / Python / CLI` tabs + `Copy` button).

## 06. Tier `Bridge-1`: Parametric Engineering Worksheet (`50%` Box Weight, Default `S2` Paper, `N0`)
- **Anatomy:** Preserves `var(--font-serif)` prose and `table.booktabs` tables (`max-width: 900px`), while embedding a `1px` hairline interactive solver frame (`.b1-solver-frame`: 3 `<input type="range">` sliders on the left coupled to a live SVG sensitivity curve and `booktabs` table row on the right).

## 07. Theme-Aware Mermaid Diagram Contract (`.va-mermaid-figure`)
Always style Mermaid diagrams using CSS custom properties (`var(--bg-canvas)`, `var(--bg-header)`, `var(--text-main)`, `var(--accent-focal)`, `var(--tint-indigo-bg)`, `var(--tint-emerald-bg)`, `var(--tint-amber-bg)`) rather than Mermaid's default yellow/purple fills, and provide a 1-click `toggleMermaidSource(btn)` button to inspect the raw Mermaid DSL.
