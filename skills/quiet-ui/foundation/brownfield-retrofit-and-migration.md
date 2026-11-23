# Brownfield Retrofit & Side-by-Side Migration Guide

> **Greenfield vs. Brownfield Retrofit**: Greenfield apps design endpoints, DOM structure, and stylesheets together. Brownfield retrofits inherit live APIs, user workflows, legacy CSS cascades, and regression tests—stripping any existing capability without explicit user sign-off is an unacceptable regression.

---

## 1. Mode Selection Matrix (Greenfield vs. Brownfield)

Declare **`Project Mode: Greenfield | Brownfield Retrofit`** at the top of the Pre-Edit Output Contract in [SKILL.md](../SKILL.md):

| Dimension | Greenfield (New Build) | Brownfield Retrofit (Existing App Overhaul) |
| :--- | :--- | :--- |
| **Requirement Baseline** | Derived from fresh specs + telemetry schemas. | Audited against every active route, filter, export, and table in the live UI. |
| **Control Simplification** | Choose consolidated `.va-period-stepper` + `.va-preset-popover` from day 1. | Collapse legacy button sprawl **only** after proving 100% state parity in the Capability Parity Ledger. |
| **API & Wire Payloads** | Clean greenfield JSON without legacy keys. | Ignore unrequested legacy wire fields via a strict **Deprecation Blocklist**; evolve shared endpoints strictly additively. |
| **Routing & Cutover** | Single entry route. | Parallel strangler route (`/v2` or `?ui=quiet`) with bidirectional switch until sign-off. |
| **CSS Integration** | Single authored `@layer` stack. | Host stylesheets quarantined inside `@import url(...) layer(legacy);` so Quiet UI `@layer` precedence holds without `!important`. |

---

## 1A. Persistent Project Contract (`.quiet-ui.md`)

Multi-session upgrades fail when agents forget previously agreed mediums, mount prefixes, parity rules, or banned legacy selectors between turns. Before re-running intake questions, check the target repository root (auto-discovered up to 3 ancestor directories, or explicit `--context PATH`):

```markdown
# .quiet-ui.md — Persistent Quiet UI Project Contract
- **Project Mode**: Brownfield Retrofit
- **Primary Medium**: M3
- **Chromatic Budget**: Quiet Cockpit
- **Navigation Shell**: N1
- **Strict Drift**: false
- **Mount Prefixes**: `/web=./web`, `/assets=./dist/assets`
- **Excludes**: `*.min.js`, `vendor/**`

## Capability Parity Ledger
| Existing Capability | Disposition | Target Pattern |
| :--- | :--- | :--- |
| Calendar + Rolling Windows | CONSOLIDATE | `.va-period-stepper` + `.va-preset-popover` |

## Deprecation Blocklist
- selector: `#legacy-quota-gauge`
- copy: `diurnal`
```

Initialize a starter contract with `python3 -B scripts/audit_quiet_html.py --init-context path/to/repo/.quiet-ui.md`. During audits, CLI `--mount-prefix`, `--exclude`, and `--strict-drift` flags merge additively on top of `.quiet-ui.md` (with explicit CLI prefixes taking precedence on conflicts), while every `selector:` and `copy:` entry triggers `[BLOCKLIST_RESURRECTION]` across static HTML, non-comment JS strings, and live `--cdp` DOM/text checks.

---

## 2. Six Mandatory Brownfield Guardrails

### Guardrail 1 — Capability Parity Ledger (`KEEP | CONSOLIDATE | DEPRECATE`)
Every brownfield overhaul fails when visual "cleanup" silently deletes inline breakdown tables, rolling vs. calendar-to-date presets, or batch exports (`CSV`, `PNG`, `ZIP`). Before removing or merging **any** existing widget:

1. Inventory every interactive control, filter state, table column group, and export action in the existing view.
2. Assign one disposition per capability and include this ledger in your Pre-Edit Output Contract:

```markdown
### Capability Parity Ledger
| Existing Capability / Control | Disposition | Target Pattern / Location | Parity Proof |
| :--- | :--- | :--- | :--- |
| Calendar periods (`MTD`, `QTD`, `YTD`) + prev/next | `CONSOLIDATE` | `.va-period-stepper` + `.va-preset-popover` (`Calendar-to-Date` group) | Same window math & prev/next bounds |
| Rolling ranges (`Last 7d`, `30d`, `90d`, `52w`) | `CONSOLIDATE` | Same `.va-preset-popover` (`Rolling Windows` group) | Reached in 1 click without dropping options |
| Per-entity breakdown summary `<table>` | `KEEP` | Inline 1-column `.booktabs` card directly below trend plot | Identical sortable metrics & units |
| Batch exports (`Export CSV`, `Save PNG`, `ZIP`) | `KEEP` | View action strip / Overflow `<div role="menu">` | Working real download handlers |
| Legacy unitless KPI spark gauge (`legacyQuota`) | `DEPRECATE` | Removed from DOM (user-approved; listed in Blocklist) | Absent in DOM & CDP check |
```

3. Never hide required multi-series chart legends inside closed drawers or hover-only tooltips—keep visible legends or inline summary tables adjacent to the chart.

---

### Guardrail 2 — Deprecation Blocklist & Wire-Field Decoupling
Backend APIs feeding brownfield consoles regularly retain deprecated JSON keys to avoid breaking older clients or external automations:

- Maintain an explicit **Deprecation Blocklist** listing retired controls, jargon terms, or metric concepts banned by user feedback.
- **Zero Wire-Driven UI Creep**: Never render a card, badge, toggle, or column merely because a field still exists in JSON telemetry.
- **Additive Legacy Opt-Out**: Pass an additive opt-out parameter (for example `?include_legacy=0`) on the overhauled view's fetches where supported, while preserving default payloads for legacy callers.
- **DOM Absence Assertions**: Add explicit unit/CDP test assertions verifying zero blocklisted selectors or legacy copy strings render anywhere in the retrofit route.

---

### Guardrail 3 — Monolith-to-Zoom Decomposition & Honest Demo Parity
Legacy consoles frequently flatten three distinct focal scales onto one scrolling document:

1. **`Overview`**: Fleet health, active anomalies, and top-level KPI corridors.
2. **`Scoped Entity Analytics`**: Single cluster, clinician cohort, subsystem, or budget view (using **`.va-scope-chip`** breadcrumb filters: `All` -> `Entity ×` -> `Entity / Item`).
3. **`Item Workspace`**: High-density split inspector (`>= 780px`), raw logs, registers, or artifact diffs.

Audit which zoom level an existing screen spans before restyling it, and route hierarchical navigation cleanly into an auto-closing **`.va-side-rail[data-mode="overlay"]`** + **`.va-tree-row`** split-intent rows so drill-down never spawns competing left jump sidebars or hides primary data.

- **Offline & `?demo=1` Preset Integrity**: When serving a static recorded snapshot (`Recorded Snapshot — YYYY-MM-DD`), either recompute scoped/rolling presets accurately from snapshot rows OR explicitly mark unbundled presets `disabled` with an explanatory `title` attribute (for example `title="Disabled in recorded preview — live query required"`). Never keep presets clickable while silently painting stale global totals.

---

### Guardrail 4 — Side-by-Side Strangler Route, Storage Isolation & Additive API Flags
Zero-downtime retrofits coexist safely alongside the original interface during verification:

- **Strangler Route Staging**: Serve the new Quiet UI surface on an additive parallel path (`/v2` or `?ui=quiet`) carrying a single unobtrusive `< Classic` link in `.va-shell-topbar`'s trailing utility slot (keeping `.va-rail-footer` strictly 1-row with `.va-swatch-row` + 2-stop density toggle) and a matching `New ↗` link in the legacy footer until full stakeholder sign-off.
- **Client Storage Namespacing**: Prefix newly persisted UI state keys cleanly (e.g., `qui.v2.density`, `qui.v2.period`) so retrofit preferences never corrupt legacy `localStorage` schemas, while continuing to share existing auth cookies or bearer sessions transparently.
- **Additive Endpoint Evolution**: Extend backend handlers strictly via optional query flags (`?bin=1d`, `?window=rolling_30d`, `?tz=UTC`) rather than breaking field types expected by legacy routes or existing test suites. Every existing backend and UI test on the classic route must stay 100% green throughout the migration.

---

### Guardrail 5 — `@layer` Cascade Quarantine & Overlay Surface Isolation
Under CSS Cascade Level 5, **unlayered styles beat every `@layer` rule regardless of selector specificity**:

1. **Quarantine Legacy Stylesheets**: Whenever a brownfield shell must share a document with legacy stylesheet rules, import or wrap legacy rules inside a lower-precedence layer *above* Quiet UI's terminal layers (`@layer legacy, reset, tokens, shell, archetypes, evidence, views, utilities;`), via `@import url("legacy.css") layer(legacy);`.
2. **Isolate Overlay Surfaces**: Never mix transparent structural pane classes (`.va-pane { background: transparent }`) onto floating overlay containers (`.va-side-rail`, `.va-preset-popover`, `.va-popover`, `<dialog>`). Keep explicit opaque `background-color: var(--bg-surface)` in terminal utility order without `!important`, verified dynamically by `--cdp` `[TRANSPARENT_OVERLAY]`.
3. **Scrollable Header Clearance**: Add `scroll-padding-top` matching sticky topbar height (`64px` desktop, up to `88px` compact 2-row phone bar `< 680px`) so in-page focus/hash anchors never vanish beneath sticky chrome.

---

### Guardrail 6 — Post-Migration Drift Normalization (`Extract & Normalize`)
Initial brownfield stabilization fixes bugs fast; without a scheduled Day-30 cleanup pass, ad-hoc inline `style="..."` patches, raw `#hex`/`rgb()` colors, duplicated view-local card layouts, and lingering `layer(legacy)` rules quietly recreate a second monolith:

1. **Detect Entropy (`--strict-drift`)**: Run `python3 -B scripts/audit_quiet_html.py <web_root> --context .quiet-ui.md --strict-drift` (or enable `Strict Drift: true` inside `.quiet-ui.md`) to inventory every `[TOKEN_BYPASS_HEX]` literal in application stylesheets (exempting `@layer tokens`, `@layer legacy`, `[data-theme]`, `@media print`, `forced-colors`, `var(--tok, #fallback)`, and explicit `/* token-exempt */` lines) and every `[INLINE_STYLE_SPRAWL]` attribute override.
2. **Extract & Consolidate (Multi-PR Sequence)**:
   - **PR 1 (Tokens & Inline Attributes)**: Hoist inline style color/padding/margin hacks into semantic view classes bound to `--bg-*`, `--border-*`, and `--text-*` tokens.
   - **PR 2 (Shared Shell Patterns & Micro-States)**: Consolidate duplicate forms, empty views, and undo alerts onto `@layer shell` `.va-form-grid`, `.va-empty-state`, and `.va-undo-toast` rules ([forms-states-and-resilience.md](forms-states-and-resilience.md)).
   - **PR 3 (Sunset `layer(legacy)` Rules)**: Prune orphaned selectors from legacy stylesheets, delete dead compatibility shims listed in the Deprecation Blocklist, and lock `Strict Drift: true` in `.quiet-ui.md` for ongoing CI enforcement.

---

## 3. Concrete Brownfield Integration Snippet

```html
<head>
  <style>
    @layer legacy, reset, tokens, shell, archetypes, evidence, views, utilities;
    @import url("/static/legacy-base.css") layer(legacy);
    @import url("/static/quiet-evidence-bundle.css");
  </style>
</head>
```

```javascript
// Namespaced retrofit UI prefs + additive server query without mutating classic callers
const STORE_PREFIX = 'ops.v2.';
localStorage.setItem(STORE_PREFIX + 'period_preset', 'rolling_30d');
fetch('/api/telemetry/summary?window=rolling_30d&bin=1d&include_legacy=0');
```

---

## 4. Brownfield Sign-Off Gate

Verify every box before proposing cutover or removing the topbar `< Classic` strangler switch:

| Gate Criterion | Required Evidence | Failure Action |
| :--- | :--- | :--- |
| **100% Capability Parity** | Every `KEEP` and `CONSOLIDATE` item verified at `390px`, `820px`, and `1440px` (Calendar-to-Date + Rolling presets, tables, and exports). | Block cutover; restore missing control before proceeding. |
| **Deprecation Absence** | Zero blocklisted `.quiet-ui.md` selectors, copy phrases (`[BLOCKLIST_RESURRECTION]`), or legacy endpoints render in static/JS/CDP probes. | Reject PR under `BF-1` / `BF-2`; strip legacy leakage. |
| **Classic Suite Green** | 100% of original classic route API and UI tests pass alongside retrofit tests (`QUIET_REQUIRE_CDP=1`). | Revert shared endpoint breakage; restore additive flag. |
| **Live `--cdp` & Strict Drift Clean** | Zero `[TRANSPARENT_OVERLAY]`, `[ORPHAN_SERIES_LEGEND]`, `[TOOLBAR_CONTROL_SPRAWL]`, `[STICKY_CHROME_BLOAT]`, `[UNLABELED_FORM_CONTROL]`, `[DEAD_END_ZERO_STATE]`, or `--strict-drift` findings. | Fix CSS layer order, stepper grouping, form labels, or token bypasses. |

Never declare a brownfield retrofit "done" from visual appearance alone: `.quiet-ui.md`, the Capability Parity Ledger, and the Day-30 Extract & Normalize `--strict-drift` sweep must verify zero capability regression and zero legacy clutter concurrently.

- **Pre-Cutover Handoff Bundle**: Attach `.quiet-ui.md` (with `Strict Drift: true`), completed Capability Parity Ledger, Deprecation Blocklist absence output, classic-route green test log, and side-by-side `390px` / `820px` / `1440px` CDP screenshots before removing `?ui=quiet` or topbar `< Classic`.
- **Single Source of Truth**: Keep shared API responses backwards-compatible (`?include_legacy=0` opt-out only) so automated monitors, exports, and classic users observe unchanged canonical metrics throughout rollout.

