# SPDX-License-Identifier: Apache-2.0
"""Generate compact Data Inputs & Honest Fallback contracts for Component Library specimens."""

from __future__ import annotations

from html import escape as _esc
from typing import Any


UI_BRIDGE_CONTRACTS: dict[str, tuple[str, str, str]] = {
    "ui-pill-and-status-grammar": (
        "telemetry.state (nominal|warn|fault), metadata.flags[]",
        "excursion.margin_pct, protocol.mode_tag (omit when unbacked)",
        "Render neutral 'Nominal' dot or 'Warming up — N samples collected' when N < 10.",
    ),
    "ui-guarded-and-consumer-controls": (
        "actuator.state, interlock.armed (bool), command_endpoint",
        "command.ack_latency_ms, operator_note (omit when absent)",
        "Disable EXECUTE when interlock state or ACK timestamp is stale/unknown.",
    ),
    "ui-compact-triage-queue": (
        "items[].{id, title, severity, status, owner}",
        "items[].target_window, filter.bucket_counts (omit if untracked)",
        "Show '0 matching items' empty row rather than stubbed triage tasks.",
    ),
    "ui-coupled-tree-explorer": (
        "tree.nodes[].{id, label, role, children[]}, node.summary",
        "node.telemetry_note, node.uptime_pct (omit when missing)",
        "Render empty inspector card with node ID only; never fabricate 24h drop counts.",
    ),
    "br-review-room-gate-band": (
        "gate.verdict, gate.checklist[].{label, status, state}",
        "gate.blocker_reason, gate.signoff_ts (omit if not recorded)",
        "Hold verdict neutral ('Pending Signoff') until every gate check reports real status.",
    ),
    "br-split-runbook-and-callout": (
        "steps[].{seq, title, action, outcome}, safety.warning",
        "telemetry.live_probe, step.elapsed_s (omit when offline)",
        "Display documented static step copy paired with explicit 'Telemetry offline' note.",
    ),
    "ui-dense-kpi-gauge-cards": (
        "cards[].{id, label, used_pct, used_label, limit_label, n_samples}",
        "cards[].daily_target_pct (omit pin when null), cards[].sub_stats[] (up to 3)",
        "Keep proportional gauge + numerator/limit; show 'Warming up — N samples collected' when N < 10.",
    ),
    "ui-joined-workspace-toolbar": (
        "filters.{window_opts[], scope_opts[]}, actions[].{id, label}",
        "active_count, export_href (disable/omit if endpoint unavailable)",
        "Render compact joined buttons with aria-pressed on stateful toggles; expand to 44px on touch.",
    ),
    "ui-period-stepper-popover": (
        "period.{preset, start_iso, end_iso, step_delta}, scope.{level, entity, item}",
        "preset.disabled_reason (disable unsupported offline presets with explanatory title)",
        "Preserve both Calendar-to-Date and Rolling presets; restore trigger focus and close overlays cleanly on selection.",
    ),
    "qe-cyclical-whiskers": (
        "buckets[].{label (00h..23h|Mon..Sun), min, avg, max, activeDays}",
        "buckets[].recent (Last 24h | Current Cycle marker; omit if current cycle empty)",
        "Skip slots with activeDays === 0 rather than zero-filling; never plot multi-day raw sums on cyclical axes.",
    ),
    "qe-forms-zero-states": (
        "threshold_ms (10..5000), sync.{status, last_sync_utc}, filter_query",
        "gate_reason (when blocked), cached_last_good.{p95_ms, error_pct}",
        "Retain last valid values with STALE badge on timeout; expose Clear filters on filtered zero-results.",
    ),
}


def render_data_contract_html(required: str, optional: str, warmup: str) -> str:
    """Render a compact collapsed data-binding contract disclosure for a specimen card."""
    return (
        '<details class="qe-data-contract">'
        '<summary>Data Inputs &amp; Honest Fallback</summary>'
        '<div class="qe-data-contract-body">'
        f'<div><strong>Required inputs:</strong> <code>{_esc(required)}</code></div>'
        f'<div><strong>Optional (omit if null):</strong> <code>{_esc(optional)}</code></div>'
        f'<div><strong>Warmup / empty fallback:</strong> {_esc(warmup)}</div>'
        '</div></details>'
    )


def _join_keys(keys: list[str]) -> str:
    seen: list[str] = []
    for k in keys:
        if k and k not in seen:
            seen.append(k)
    return ", ".join(seen)


def contract_for_evidence_spec(spec: dict[str, Any]) -> str:
    """Derive Data Inputs & Honest Fallback contract directly from a canonical JSON evidence spec."""
    schema = str(spec.get("$schema") or "")
    mod = schema.rsplit(":", 1)[-1] if ":" in schema else "plot"

    if mod == "scalar":
        unit = str((spec.get("quantity") or {}).get("unit") or spec.get("unit") or "").strip() or "unitless"
        if spec.get("items"):
            req = ["items[].{label, command_value|target_value, actual_value, unit}"]
            opt = ["items[].status_annunciator", "items[].tolerance_band"]
        else:
            req = ["quantity.{symbol,unit}", f"measurement.nominal_value ({unit})", "limits|gauge|sparkline"]
            opt = ["measurement.expanded_uncertainty", "limits.warning_thresholds", "limits.abort_thresholds"]
        fb = "Render neutral gauge without target pin if absent; show 'Warming up — N samples collected' if N < 10."
        return render_data_contract_html(_join_keys(req), _join_keys(opt), fb)

    if mod == "table":
        cols = [str(c.get("key") or c.get("label") or "") for c in (spec.get("columns") or [])[:4]]
        req = ["columns[]", "rows[]"] + ([f"cells({', '.join(c for c in cols if c)})"] if any(cols) else [])
        opt = ["row.flag", "row.uncertainty", "footnotes[]"]
        fb = "Show column headers with explicit '0 observed rows' state; emit '—' for null cells instead of 0."
        return render_data_contract_html(_join_keys(req), _join_keys(opt), fb)

    if mod == "bitfield":
        wb = int(spec.get("word_bits") or 32)
        req = [f"word_bits ({wb})", "fields[].{msb,lsb,name,access}"]
        opt = ["reset_value", "live_register_hex", "lock_bits"]
        fb = "Render decode table with 'Live register unreadable (0x—)' rather than synthetic reset bits."
        return render_data_contract_html(_join_keys(req), _join_keys(opt), fb)

    if mod == "waveform":
        wkind = str(spec.get("waveform_kind") or "oscilloscope")
        if wkind == "day_arc":
            req = ["waveform_kind (day_arc)", "phases[]", "events[].{time,label}"]
        elif wkind == "sequence":
            req = ["waveform_kind (sequence)", "actors[]", "steps[].{from,to,label}"]
        elif wkind == "strip_chart":
            req = ["waveform_kind (strip_chart)", "tracks[].{label,unit,samples[]}", "timebase"]
        else:
            req = [f"waveform_kind ({wkind})", "channels[].{label,unit,samples[]}", "timebase"]
        opt = ["cursors[]", "dropout_handling", "test_environment"]
        fb = "Keep calibrated axis bounds and show 'DROPOUT / Warming up — N samples collected' for gaps or N < 10."
        return render_data_contract_html(_join_keys(req), _join_keys(opt), fb)

    if mod == "schematic":
        skind = str(spec.get("schematic_kind") or spec.get("kind") or "topology")
        req_map = {
            "sequence": "participants[], messages[].{from,to,label}",
            "n2_matrix": "subsystems[], interfaces[].{from,to,label}",
            "fault_tree": "top_event, branches[].{gate,children[]}",
            "er_lineage": "tables[].{name,columns[]}, relations[].{from,to,cardinality}",
        }
        req = req_map.get(skind, f"schematic_kind ({skind}), nodes[], connections[]")
        opt = "cutoff_probabilities, phases, enclave_annotations"
        fb = "Render structural skeleton only; display 'No live measurements attached' instead of guessed rates."
        return render_data_contract_html(req, opt, fb)

    pkind = str(spec.get("plot_kind") or "cartesian")
    if pkind == "waterfall":
        req_s = "axes.y_axis.{unit}, steps[].{label,kind,delta|value}"
        opt_s = "envelopes[].{label,threshold_value}, total_check"
    elif pkind == "gantt":
        req_s = "axes.x_axis.{unit}, tasks[].{id,label,start,end}"
        opt_s = "tasks[].float_days, tasks[].depends_on, today_day"
    elif pkind == "heatmap":
        req_s = "x_categories[], y_categories[], matrix[][], unit"
        opt_s = "thresholds, cell_annotations"
    elif pkind in {"dumbbell", "forest"}:
        req_s = "axes, items[].{label, before|estimate, after|ci_low..ci_high}"
        opt_s = "null_value, pooled_summary, policy_effective_date"
    elif pkind == "sankey":
        req_s = "nodes[].{id,label}, links[].{source,target,value,unit}"
        opt_s = "loss_nodes, stage_subtotals"
    elif pkind == "us_hex_tile_map":
        req_s = "states{51}.{value}, unit, focus_state"
        opt_s = "bin_breaks[], palette[], states[].note"
    elif pkind == "arrow_dumbbell":
        req_s = "items[].{label,start,end}, start_label, end_label"
        opt_s = "items[].fallback_vintage, sort, unit"
    elif pkind == "paired_subgroup_bars":
        req_s = "groups[].{label,a,b,overall}, subgroups[2], overall_label"
        opt_s = "color_a, color_b, decimals"
    elif pkind == "dual_slopegraph":
        req_s = "series[].{label,left_start,left_end,right_start,right_end}"
        opt_s = "crossover.label, left_unit, right_unit"
    else:
        req_s = f"axes.{{x_axis,y_axis}}, series[].{{label,epistemic,data_points[]}} ({pkind})"
        opt_s = "envelopes[], uncertainty_bands[], baseline_fit, policy_effective_date"
    fb_s = "Preserve unit axes and window; show 'Warming up — N samples collected' when N < 10 and omit absent envelopes."
    return render_data_contract_html(req_s, opt_s, fb_s)


def contract_for_ui_specimen(spec_id: str) -> str:
    """Return Data Inputs & Honest Fallback HTML for a Pillar 1 (UI) or Pillar 3 (BR) specimen."""
    req, opt, fb = UI_BRIDGE_CONTRACTS.get(
        spec_id,
        ("verified_state_fields[]", "optional_subslots (omit if null)", "Warming up — N samples collected when N < 10."),
    )
    return render_data_contract_html(req, opt, fb)
