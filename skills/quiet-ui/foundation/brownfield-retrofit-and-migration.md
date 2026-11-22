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

## 2. Five Mandatory Brownfield Guardrails

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

- **Strangler Route Staging**: Serve the new Quiet UI surface on an additive parallel path (`/v2` or `?ui=quiet`) carrying a single unobtrusive `< Classic` link in `.va-rail-footer` (and a matching `New ↗` link in the legacy footer) until full stakeholder sign-off.
- **Client Storage Namespacing**: Prefix newly persisted UI state keys cleanly (e.g., `qui.v2.density`, `qui.v2.period`) so retrofit preferences never corrupt legacy `localStorage` schemas, while continuing to share existing auth cookies or bearer sessions transparently.
- **Additive Endpoint Evolution**: Extend backend handlers strictly via optional query flags (`?bin=1d`, `?window=rolling_30d`, `?tz=UTC`) rather than breaking field types expected by legacy routes or existing test suites. Every existing backend and UI test on the classic route must stay 100% green throughout the migration.

---

### Guardrail 5 — `@layer` Cascade Quarantine & Overlay Surface Isolation
Under CSS Cascade Level 5, **unlayered styles beat every `@layer` rule regardless of selector specificity**:

1. **Quarantine Legacy Stylesheets**: Whenever a brownfield shell must share a document with legacy stylesheet rules, import or wrap legacy rules inside a lower-precedence layer *above* Quiet UI's terminal layers (`@layer legacy, reset, tokens, shell, archetypes, evidence, views, utilities;`), via `@import url("legacy.css") layer(legacy);`.
2. **Isolate Overlay Surfaces**: Never mix transparent structural pane classes (`.va-pane { background: transparent }`) onto floating overlay containers (`.va-side-rail`, `.va-preset-popover`, `.va-popover`, `<dialog>`). Keep explicit opaque `background-color: var(--bg-surface)` in terminal utility order without `!important`, verified dynamically by `--cdp` `[TRANSPARENT_OVERLAY]`.
3. **Scrollable Header Clearance**: Add `scroll-padding-top` matching sticky topbar height (`64px` desktop, up to `88px` compact 2-row phone bar `< 680px`) so in-page focus/hash anchors never vanish beneath sticky chrome.

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

Verify every box before proposing cutover or removing the `< Classic` strangler switch:

| Gate Criterion | Required Evidence | Failure Action |
| :--- | :--- | :--- |
| **100% Capability Parity** | Every `KEEP` and `CONSOLIDATE` item verified at `390px`, `820px`, and `1440px` (Calendar-to-Date + Rolling presets, tables, and exports). | Block cutover; restore missing control before proceeding. |
| **Deprecation Absence** | Zero blocklisted legacy selectors, endpoints, or deprecated copy phrases exist in rendered DOM. | Reject PR under `BF-1` / `BF-2`; strip legacy leakage. |
| **Classic Suite Green** | 100% of original classic route API and UI tests pass alongside retrofit tests (`QUIET_REQUIRE_CDP=1`). | Revert shared endpoint breakage; restore additive flag. |
| **Live `--cdp` Clean** | Zero `[TRANSPARENT_OVERLAY]`, `[ORPHAN_SERIES_LEGEND]`, `[TOOLBAR_CONTROL_SPRAWL]`, `[STICKY_CHROME_BLOAT]`, or `[AXIS_LABEL_CLIPPED]` errors. | Fix CSS layer order, stepper grouping, or frame margins. |

Never declare a brownfield retrofit "done" from visual appearance alone: both the Capability Parity Ledger and the Deprecation Blocklist must prove zero capability regression and zero legacy clutter concurrently.

- **Pre-Cutover Handoff Bundle**: Attach the completed Capability Parity Ledger, the Deprecation Blocklist DOM-absence test output, the classic-route green test log, and side-by-side `390px` / `820px` / `1440px` CDP screenshots (`--cdp`) before removing `?ui=quiet` or `< Classic`.
- **Single Source of Truth**: Keep shared API responses backwards-compatible (`?include_legacy=0` opt-out only) so automated monitors, exports, and classic users observe unchanged canonical metrics throughout rollout.

