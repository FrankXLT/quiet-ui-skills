# Data Grounding & Widget Binding Contract

> **Data First, Specimen Second**: Inspect live API endpoints, SQL/JSON schemas, or `urn:quiet-ui:schema:v9:*` payloads *before* selecting any layout or component specimen. An empty or omitted sub-slot always beats an invented number.

---

## 1. Mandatory Pre-Build Workflow (Data-to-Widget Binding Map)

Agents must never start by browsing `docs/bench/evidence-bench.html`, picking an attractive card or chart, and back-filling fake numbers to make every sub-element look populated. Execute these three steps in order before writing HTML or JavaScript:

1. **Inventory Live Payloads First**: Read the actual route handlers, state stores, or dataset schemas to list every available field, its exact physical unit (`%`, `ms`, `req/min`, `USD`), its valid domain/bounds, and whether the field can be `null` or short-window.
2. **Draft a Data-to-Widget Binding Map**: Map each candidate component slot strictly to verified payload keys before rendering markup.
3. **Prune Unbound Slots**: Delete any target line, delta pill, badge, or secondary stat row whose backing field is absent or belongs to a different domain/cohort.

| UI Slot / Specimen | Verified Source Field | Physical Unit & Scale | Window / Denominator (`N`) | Absent / Short-Window Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Hero KPI Gauge (`4-up`)** | `quota.pool_used_pct` | `%` (`0–100%`) | `window_hours`, `n_requests` | Omit target pin if `daily_target_pct == null`; show warmup if `n_requests < 10` |
| **Gauge Fill Fraction** | `quota.used_tokens / quota.limit_tokens` | exact token ratio | active billing window | Render `—` for ratio if `limit_tokens` is `null` or `<= 0` |
| **Primary Trend Plot** | `series[].points[] -> {ts, val}` | SI unit from payload | `[t_min, t_max]` UTC | Omit comparison curve if baseline series is missing |
| **Operational Table Cell** | `runs[].steps` | integer count (`>= 0`) | per-run `run_id` | Render `—` for missing telemetry; never substitute `0` |
| **Alert / Envelope Line** | `policy.ceiling_steps` | matches Y axis unit | `policy.effective_date` | Draw only when all rendered runs occurred under the same policy version |

---

## 2. Sub-Slot Omission vs. Visual Symmetry

Component Library cards demonstrate maximum anatomical density—they are **not** checklists requiring every sub-element to appear in every production instance:

- **Zero Cross-Domain Target Borrowing**: Never copy a policy target from one resource pool onto an unrelated metric card just to match card heights. Example: placing `"Target 14.28% partner/d"` onto an unlimited or Google-pool model gauge misleads operators because that target applies to weekly partner-pool allocation, not per-model throughput.
- **Omit When Absent**: Inside `.va-kpi-gauge-card`, keep headline metric + horizontal fill gauge when `limit` is known, and omit optional `delta` or `target_pin` DOM nodes when absent rather than inserting `"Target: N/A"` filler lines or placeholder percentages.
- **Preserve Quantitative Density & Select Form by Category Count (`N`)**:
  - **`N <= 3` Categories -> Stat Strip or Micro-Bar (`<= 72px` tall)**: Never ship a `>= 180px` Cartesian bar chart dominated by blank space for 2–3 categories; use a stat strip or horizontal micro-bar.
  - **Zero Duplicate Time-Series Denominators**: Never render a standalone total-volume chart next to a stacked breakdown over the same buckets; merge into **one** stacked chart with `Avg` / `P95` total reference lines.
  - **`N <= 8` Comparison + Exact Figures -> Inline Bullet-Bar Table**: Never stack a 4–8 bar chart above a matching table; embed `.va-inline-bar` / `.va-inline-bar-fill` / `.va-inline-bar-pin` directly inside `.va-row-compact` table rows (`<= 32px`/row).
- **Reject Engineering Self-Filler & Pill Sprawl**: Do not pad operational user dashboards with internal repository or code-hygiene badges (e.g., `"64/64 <= 500L"`, git commit SHAs, file-count pills) unless the view specifically serves CI/repository auditing. Render dates, versions, counts, subtitles, hashes, and units as plain unboxed muted text (`.va-meta-inline`), use `.va-tab-strip` / `.va-tab` (`4–6px` or underline) for file/mode switchers, and reserve `.va-badge` (`--radius-sm`, max `1` per card header) strictly for semantic state exceptions (`HEALTHY`/`WARN`/`FAULT`).

---

## 3. Window Honesty, Retroactive Grading & Warmup States

Statistical clarity requires separating thin live buffers from established historical baselines and annotating rule boundaries honestly:

### 3.1 Warmup Disclosure (`N < 10` or Post-Restart Buffer)
- In-memory instrumentation resets on process restart. If a metric buffer currently contains only `"3 calls"` (or fewer than `10` samples over a sub-hour uptime window), **never** style the widget as a settled steady-state trend or long-horizon convergence metric.
- Replace trend verdicts with the explicit disclosure string **`Warming up — N samples collected`** (with observed uptime/window, e.g., `Warming up — 3 samples collected since 10:15 UTC`), and hold alert classification badges neutral (`--text-muted` / `--status-info`) until minimum sample power is reached.

### 3.2 Zero Retroactive Policy Grading
- When a new operational guardrail or ceiling is introduced on date `T` (for example, lowering a subagent step budget to `120` steps), **never** re-score 30–90 day historical runs prior to `T` as `"violations"` against the new rule without explicit disclosure.
- Either scope violation counts and red threshold overlays to runs with `created_at >= policy.effective_date`, or annotate historical overlays visibly as `"Evaluated against ceiling effective YYYY-MM-DD (historical runs predate rule)"`.

### 3.3 Explicit Denominators & Physical Scope
- Every derived percentage or rate (`78.4%`, `103 tokens/s`) must carry sample size `N` (`n = 35`) or denominator context nearby so readers can tell a `3/4` post-restart spike apart from a `300/400` sustained average.

---

## 4. Zero Hardcoded Demo Mocks (`?demo=1` & Offline Previews)

Preview modes exist to inspect real schemas safely—not to invent flattering numbers inside frontend code:

1. **Banned Inline Mock Arrays**: Never hardcode multi-row synthetic JS fixtures (`const MOCK_RUNS = [...]`, `FAKE_METRICS`, `demoRows = [...]`, or literal multi-object arrays returned inside `if (isDemo)` / `demoMode` client view functions).
2. **Approved Snapshot Mechanism**: When `?demo=1` is supported, fetch an explicit server-side or external anonymized runtime snapshot file carrying a top-level metadata banner: `Recorded Snapshot — YYYY-MM-DD (Sanitized)`.
3. **Honest Empty Fallback**: When no snapshot exists and no live telemetry has arrived yet, render the real empty structural shell paired with **`Warming up — 0 samples collected`** and clear instructions for ingesting live data.

---

## 5. Chrome Branding & Internal Identifier Hygiene

Interfaces shipped with Quiet UI represent the **host application**, never Quiet UI's internal documentation taxonomy or agent storage layout:

- **Zero Framework Self-Badges**: Remove self-referential header badges (`Quiet UI`, `v9.x Quiet`, `Pillar 1 M3`, `Quiet-Evidence`) from live third-party application headers, nav pills, and footer bars. Label the actual product (`Nexus Ops`, `Fleet Telemetry`, `Ward Monitor`) cleanly. *(Showcase and Component Bench views inside `quiet-ui-skills` opt in explicitly during build verification.)*
- **Strip Internal Storage Prefixes**: Never expose raw agent artifact namespaces (`brain:<uuid>`, `.gemini/antigravity/brain/...`) or local workstation paths in visible tables, headers, detail drawers, or HTML templates. Map artifact references to human-readable titles or sanitized short IDs before rendering.

---

## 6. Concrete Grounding Examples (Right vs. Wrong)

Compare how an agent handles partial telemetry without fabricating fields or stripping density:

### 6.1 Hero Pool Cards (Quota & Compute Monitors)
- **Wrong**: Copying a partner-pool daily allocation badge (`Target 14.28% partner/d`) onto a Google Carbon/Argon card that has no daily target, converting progress gauges into text-only summary boxes, and padding card footers with repo lint counts (`64/64 <= 500L`).
- **Right**: Use `.va-kpi-gauge-card` bound strictly to `pool.used_tokens / pool.limit_tokens` and `pool.pct`. Render the target pin *only* on the partner pool card (`pool.daily_target_pct != null`), omit the target pin on Google pools, and keep engineering lint counts solely inside a dedicated CI Audit page.

### 6.2 Post-Restart Execution Telemetry & Historical Runs
- **Wrong**: Plotting a `3`-call post-restart memory buffer as a steady convergence chart alongside 90-day runs marked as "violations" against yesterday's `120`-step ceiling, plus a hardcoded 6-row `demoRows = [...]` JS fixture for `?demo=1`.
- **Right**: Show **`Warming up — 3 samples collected`** (`uptime 14m`) for the live buffer, annotate historical runs as `"Pre-policy baseline (120-step ceiling effective 2026-11-20)"` or filter violations to `ts >= policy_effective`, and load `?demo=1` exclusively from a timestamped server/external snapshot JSON (`Recorded Snapshot — YYYY-MM-DD`).

### 6.3 Clinical & Building Telemetry (Non-Software Domains)
- **Clinical SpO2 / Bedside Ward**: Bind numeric gauge to `patient.spo2_pct` (`min: 70`, `max: 100`) and ordered alarm bound `patient.spo2_low_limit`; if arterial pH lab draw is older than `4h` or absent, render `Last lab >4h ago (—)` instead of interpolating a curve or synthesizing a normal value.
- **Solar & Microgrid Controller**: When inverter BMS drops off CAN bus (`bms_soc == null`), freeze gauge fill in neutral muted ink without false status urgency and show `Warming up — 0 samples collected` / `BMS offline`, preserving prior logged timestamp without carrying forward a stale `"100% Charged"` badge.

---

## 7. Interactive Spec Disclosure & Auditor Enforcement

Every specimen in `docs/bench/evidence-bench.html` exposes a compact `<details class="qe-data-contract">Data Inputs &amp; Honest Fallback</details>` contract listing required fields, optional slots to omit when null, and warmup fallback wording.

Before declaring UI work complete, run the updated portable auditor (mounts under `--mount-prefix` automatically verify existence via `[MISSING_ASSET]` and scope CSS/JS linting to subdirectory/subpath targets unless `--audit-mounted-external` is passed; use `--exclude` for vendored/legacy assets):

```bash
# Static check across mounted web assets (stdlib only, zero dependencies)
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py /path/to/dist/v9 \
  --mount-prefix /web=/path/to/dist --exclude "*.min.js"

# Live headless inspection across 390x844, 820x1080, and 1440x900
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py http://127.0.0.1:8765/web/v9?demo=1 \
  --cdp --mount-prefix /web=/path/to/web
```

The auditor enforces terminal `@layer utilities` `.hidden` placement (`[HIDDEN_LAYER]`), cumulative sticky/fixed header height `<= 64px` (`[STICKY_CHROME_BLOAT]`), `<= 2px` inner plot-box axis alignment (`[PLOT_AXIS_MISALIGN]`), pill restraint (`[PILL_SPRAWL]`), zero chrome `Quiet` badges (exempting kebab-case repo/ticket slugs like `quiet-ui-skills`), zero raw `brain:` IDs, zero inline mock arrays, zero clipped controls, and zero SVG text/line collisions.

---

## 8. Pre-Render Sign-Off Checklist

1. **Field Verification**: Have you inspected exact field names, units, and nullable keys in every endpoint backing this view?
2. **Traceability**: Does every KPI card, table column, and chart trace point directly to a documented field in your Data-to-Widget Binding Map?
3. **Sub-Slot Omission**: Are absent targets, baselines, and tolerances cleanly omitted rather than borrowed or hardcoded?
4. **Warmup Honesty**: Do thin buffers (`N < 10`) show **`Warming up — N samples collected`** instead of false steady-state claims?
5. **Policy Scoping**: Are historical runs shielded from retroactive scoring against newly enacted policies?
6. **Chrome Hygiene**: Is application header chrome 100% free of Quiet UI framework badges and raw internal `brain:` storage IDs?
7. **Snapshot Purity**: Are preview/demo states loaded from explicit server or external captured snapshots rather than hardcoded inline JS arrays?
8. **Zero Self-Filler**: Have internal CI linter or file-budget counts been excluded from end-user operational widgets?

> [!NOTE]
> **Conservation Over Decoration**: Whenever payload telemetry is incomplete, post-restart, or pre-policy, Quiet UI preserves interface credibility by omitting unbacked annotations, holding warmup bounds neutral, and letting empty state communicate honestly rather than synthesizing plausible-looking numbers.

