# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Modality 6 (Schematics & System Topologies) Dispatcher."""

from __future__ import annotations

from typing import Any

from .schematic_routing import compile_differential_bus, compile_pid_loop, compile_topology_enclave
from .schematic_variants import (
    compile_delta_lanes,
    compile_er_lineage,
    compile_fsm,
    compile_optical_stack,
    compile_sankey,
    compile_wardley,
)
from .tokens_and_scales import esc, render_test_condition_strip


def compile_schematic(spec: dict[str, Any], rigor: str | None = None, medium: str = "m2", theme: str = "white", chrome: str = "bench") -> str:
    """Compile Modality 6 (urn:quiet-ui:schema:v9:schematic) into orthogonal HTML/SVG."""
    meta = spec.get("metadata", {})
    eff_rigor = (rigor or meta.get("rigor_level", "L2")).upper()
    kind = str(spec.get("schematic_kind", "topology")).lower()

    dispatch = {
        "mil1553b": compile_differential_bus,
        "differential_bus": compile_differential_bus,
        "fieldbus": compile_differential_bus,
        "can_fd": compile_differential_bus,
        "rs485": compile_differential_bus,
        "modbus": compile_differential_bus,
        "pid_loop": lambda s: compile_pid_loop(s, eff_rigor),
        "optical_stack": compile_optical_stack,
        "delta_lanes": compile_delta_lanes,
        "fsm": compile_fsm,
        "wardley": compile_wardley,
        "sankey": compile_sankey,
        "er_lineage": compile_er_lineage,
    }

    panels: list[str] = []
    if spec.get("panels"):
        for sub in spec["panels"]:
            sk = str(sub.get("schematic_kind", "topology")).lower()
            renderer = dispatch.get(sk, lambda s: compile_topology_enclave(s, eff_rigor))
            title = sub.get("title", "")
            cap = f'<div class="qe-subpanel-title">{esc(title)}</div>' if title else ""
            panels.append(f'<div class="qe-subpanel">{cap}<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(title or meta.get("title", "Schematic"))}">{renderer(sub)}</div></div>')
    else:
        renderer = dispatch.get(kind, lambda s: compile_topology_enclave(s, eff_rigor))
        panels.append(f'<div class="va-figure-scroll" tabindex="0" role="region" aria-label="{esc(meta.get("title", "Schematic"))}">{renderer(spec)}</div>')

    cond = render_test_condition_strip(spec.get("test_environment"), eff_rigor)
    dwg = f'<span class="qe-dwg-num va-nums">DWG: {esc(meta["drawing_number"])}</span>' if (meta.get("drawing_number") and eff_rigor in {"L2", "L3"}) else ""
    hdr = f'<div class="qe-schematic-hdr">{cond}{dwg}</div>' if (cond or dwg) else ""
    return f'<div class="qe-schematic-wrap" data-rigor="{esc(eff_rigor)}" data-medium="{esc(medium)}">{hdr}{"".join(panels)}</div>'
