# Forms, Micro-States & Action Resilience Guide

> **Micro-State Completeness**: Every stateful dashboard or workbench fails users at its edges—unlabeled controls, hostile red borders on the first keystroke, dead-end `0 matching rows` states, wiped cache metrics during transient API outages, and confirmation modals interrupting trivial soft actions. This guide standardizes Quiet UI `v9.4.0` form ergonomics, 4-way zero-data resilience, and 3-tier action reversibility using `@layer shell` classes defined in `src/css/14-forms-and-states.css`.

---

## 1. Accessible Form Controls & Mobile Ergonomics (`[UNLABELED_FORM_CONTROL]`)

Every `<input>`, `<select>`, and `<textarea>` (excluding `hidden`, `submit`, `reset`, `button`, and `image` types) MUST expose an explicit accessible label verified both statically and dynamically via `--cdp`:

1. **Label Binding Rule**: Pair every control with a visible `<label for="control-id" class="va-field-label">`, a wrapping `<label>`, or explicit `aria-label` / `aria-labelledby`. Never rely on `placeholder` text as a substitute for a visible `<label>`—placeholders vanish as soon as typing starts and fail assistive technology and visual scanability.
2. **Grid & Field Structure**: Group inputs inside `.va-form-grid` (`repeat(auto-fit, minmax(min(220px, 100%), 1fr))`) and `.va-field` containers using `.va-input`, `.va-select`, and `.va-textarea`.
3. **Coarse-Pointer & Mobile Zoom Floor**: Controls enforce `min-block-size: 36px` on desktop viewports and automatically step up to `min-block-size: 44px` with `font-size: max(1rem, var(--ts-base))` (`>= 16px`) under `@media (max-width: 699px)` or `@media (pointer: coarse) and (max-width: 767px)`, eliminating accidental tap misses and iOS viewport zoom.
4. **Hints Before Errors**: Attach static constraints (for example units, bounds, or format syntax) to a persistent `.va-field-hint` node referenced in `aria-describedby` ahead of the live error container so operators read valid ranges before typing.

---

## 2. Progressive Validation Timing, Gate Reasons & `[aria-busy]`

Hostile client validation marks fields invalid while a user is mid-keystroke. Enforce progressive interaction timing paired with explicit prerequisite feedback:

| Phase | Trigger Event | DOM & CSS Contract | Rationale |
| :--- | :--- | :--- | :--- |
| **1. Initial / Untouched** | Page load | Neutral `.va-input` (`--border-strong`), empty `.va-field-error` | Do not flag unvisited required fields with error chrome before user interaction. |
| **2. First Error** | `blur` or `submit` | Set `aria-invalid="true"`, update `.va-field-error`, preserve `aria-describedby` | `:is(:user-invalid, [aria-invalid="true"])` applies `--status-danger` border + `--status-err-bg`. |
| **3. Live Recovery** | `input` / `change` | Clear `[aria-invalid]` and empty `.va-field-error` immediately once valid | Immediate positive feedback reduces correction latency without jittering invalid edits. |
| **4. Submit Focus** | Invalid `submit` | Focus first invalid control; update summary inside `[aria-live="polite"]` | Announces failure cleanly to assistive tech without stealing focus mid-typing. |

```javascript
// Progressive validation timing: never error before interaction; clear immediately on recovery
const errEl = document.getElementById('latency-err');
const validateField = (input, forceShow) => {
  const ok = input.checkValidity();
  if (ok) {
    input.removeAttribute('aria-invalid');
    errEl.textContent = '';
  } else if (forceShow || input.getAttribute('aria-invalid') === 'true') {
    input.setAttribute('aria-invalid', 'true');
    errEl.textContent = input.validationMessage || 'Enter a number between 10 and 5000 ms.';
  }
  return ok;
};
inputEl.addEventListener('blur', () => validateField(inputEl, true));
inputEl.addEventListener('input', () => validateField(inputEl, false));
```

- **Gate Reason Callouts (`.va-gate-reason`)**: Whenever a primary action is blocked or disabled by missing prerequisites, unconfirmed hardware interlocks, or cooldown timers, render an inline `.va-gate-reason` (with optional `data-state="warn|fault"`) directly adjacent to the trigger explaining the exact unlock condition rather than leaving an unexplained grey button.
- **In-Flight Latency (`[aria-busy="true"]`)**: Set `aria-busy="true"` on the active submit control or host card during asynchronous requests, render explicit text progress (for example `"Saving alert threshold..."`), and prevent duplicate submission without collapsing card geometry.

---

## 3. The 4-Way Zero-Data & Stale Resilience Taxonomy (`[DEAD_END_ZERO_STATE]`)

Never render a silent blank panel or synthetic `0` baseline when a dataset lacks rows. Route every non-nominal container through `.va-empty-state[data-kind="..."]` (`.va-empty-title`, `.va-empty-copy`, `.va-empty-actions`):

| `data-kind` | Operational Cause | Mandatory Surface Content & Recovery |
| :--- | :--- | :--- |
| **`first-run`** | New workspace or unconfigured telemetry source (`total == 0`) | Plain statement of what connects here + `.va-btn-primary` onboarding CTA (for example `Connect Collector`). |
| **`filtered`** | Active filters, search query, or date window exclude all rows | Show active filter summary + mandatory 1-click recovery `<button>` (`Clear filters` / `Reset filters`) or `<a href>` link (`[DEAD_END_ZERO_STATE]`). |
| **`warmup`** | Rolling cohort or baseline sample size `N < 10` | Explicitly disclose `Warming up — N samples collected`; omit unbacked SLA comparisons or confidence corridors until `N >= 10`. |
| **`stale`** | Upstream fetch timed out or failed while cached telemetry exists | Retain `.va-stale-retained` last-known-good metrics at `0.84` opacity with last-updated UTC timestamp, `.va-pill[data-variant="status"][data-state="warn"]` (`STALE`), and `.va-btn-ghost` `Retry`. |

---

## 4. Three-Tier Action Reversibility Matrix

Calibrate confirmation friction strictly to operational blast radius rather than placing modal barriers in front of cheap reversible operations:

| Tier | Blast Radius | Pattern & CSS Classes | Behavioral Invariants |
| :--- | :--- | :--- | :--- |
| **Tier 1 — Reversible Soft Action** | Mute alert, archive rule, filter reset, soft delete | `.va-undo-toast` (`.va-undo-msg` + `.va-undo-actions`) with `role="status"` / `aria-live="polite"` | Execute optimistically without blocking modal; offer `Undo` button for **>= 7s**, include explicit `Dismiss` control, and pause countdown timer on both pointer hover and keyboard `:focus-within`. |
| **Tier 2 — Physical / Guarded Effector** | Actuator relay toggle, PLC setpoint write, live fleet config push | Two-step latch (`ARM` -> `EXECUTE`) + `.va-gate-reason[data-state="warn"]` | Require deliberate arming transition with automatic timeout disarm, explicit `CMD` vs `ACT` readback, and upstream interlock check before enabling execution. |
| **Tier 3 — Irreversible Destructive** | Permanent delete, key revocation, factory reset | Native `<dialog class="va-modal-sheet" closedby="any">` via `showModal()` | State exact blast radius and target identifier, focus non-destructive `Cancel` by default, name destructive confirm control specifically (`Delete key`), and support `Esc` + backdrop dismissal cleanly. |

---

## 5. Canonical Markup References

```html
<form class="va-form-grid" novalidate>
  <div class="va-field">
    <label for="latency-ceiling" class="va-field-label">Latency Threshold (ms)</label>
    <input id="latency-ceiling" class="va-input" type="number" min="10" max="5000" required
           aria-describedby="latency-hint latency-err">
    <span id="latency-hint" class="va-field-hint">Bounded SLA alert window: 10–5000 ms.</span>
    <span id="latency-err" class="va-field-error" role="status" aria-live="polite"></span>
  </div>
  <div class="va-gate-reason" data-state="warn">
    Enter a valid latency bound (10–5000 ms) to enable Save Rule.
  </div>
</form>

<section class="va-empty-state" data-kind="first-run">
  <h3 class="va-empty-title">No collectors connected yet</h3>
  <p class="va-empty-copy">Configure an OpenTelemetry endpoint to begin sampling service latency.</p>
  <div class="va-empty-actions">
    <button type="button" class="va-btn-primary">Connect collector</button>
  </div>
</section>

<section class="va-empty-state" data-kind="filtered">
  <h3 class="va-empty-title">No matching incidents in selected window</h3>
  <p class="va-empty-copy">0 rows matched status=Fault and window=Last 24h.</p>
  <div class="va-empty-actions">
    <button type="button" class="va-btn-primary">Clear filters</button>
  </div>
</section>

<section class="va-empty-state" data-kind="warmup">
  <h3 class="va-empty-title">Warming up — 4 samples collected</h3>
  <p class="va-empty-copy">Baseline percentile corridor unlocks once 10 samples arrive.</p>
</section>

<section class="va-empty-state" data-kind="stale">
  <div class="va-stale-retained">
    <span>Retained cache: p99 142 ms · Err 0.4% (2026-11-22 14:12 UTC)</span>
    <span class="va-pill" data-variant="status" data-state="warn">STALE</span>
  </div>
  <h3 class="va-empty-title">Collector feed timed out after 5s</h3>
  <p class="va-empty-copy">Showing last-known-good telemetry until refresh succeeds.</p>
  <div class="va-empty-actions">
    <button type="button" class="va-btn-ghost">Retry now</button>
  </div>
</section>

<aside class="va-undo-toast" role="status" aria-live="polite">
  <span class="va-undo-msg">Archived rule "Edge-p99-Alert". Auto-closes in 7s (pauses on hover/focus).</span>
  <div class="va-undo-actions">
    <button type="button" class="va-btn-ghost">Undo</button>
    <button type="button" class="va-tb-btn">Dismiss</button>
  </div>
</aside>

<dialog class="va-modal-sheet" closedby="any" aria-labelledby="revoke-title">
  <h3 id="revoke-title" class="va-empty-title">Revoke API token "edge-ingest-04"?</h3>
  <p class="va-empty-copy">Collectors using this key stop authenticating immediately. This action cannot be undone.</p>
  <div class="va-empty-actions">
    <button type="button" class="va-btn-ghost" autofocus>Cancel</button>
    <button type="button" class="va-btn-primary">Revoke token</button>
  </div>
</dialog>
```

```javascript
// Form submit guard with first-invalid focus + in-flight [aria-busy="true"] protection
formEl.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (!validateField(inputEl, true)) { inputEl.focus(); return; }
  if (submitBtn.getAttribute('aria-busy') === 'true') return;
  submitBtn.setAttribute('aria-busy', 'true');
  submitBtn.textContent = 'Saving rule...';
  try { await saveRulePayload(); } finally {
    submitBtn.removeAttribute('aria-busy');
    submitBtn.textContent = 'Save rule';
  }
});
```

---

## 6. Cross-Pillar Integration Checklist

1. **Data Grounding First**: Pair `warmup` (`N < 10`) and `stale` disclosures strictly with verified fields mapped in [data-grounding-and-widget-binding.md](data-grounding-and-widget-binding.md)—never invent placeholder series behind an empty state.
2. **Brownfield Parity**: Record legacy form validations, filter resets, and undo/confirmation behaviors inside the Capability Parity Ledger in [brownfield-retrofit-and-migration.md](brownfield-retrofit-and-migration.md) before retiring old dialogs.
3. **Top-Layer Sheet Parity**: For complex Tier-3 destructive confirmations or narrow-viewport companions (`< 760px`), reuse `<dialog class="va-modal-sheet" closedby="any">` documented in [navigation-morphing.md](navigation-morphing.md) and suppress global keyboard shortcuts whenever `dialog[open]` is active.
4. **Auditor Verification**: `scripts/audit_quiet_html.py` enforces zero `[UNLABELED_FORM_CONTROL]` inputs and zero `[DEAD_END_ZERO_STATE]` filtered views across `390px`, `820px`, and `1440px` (`--cdp`).

