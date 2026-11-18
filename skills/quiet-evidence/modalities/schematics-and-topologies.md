# Modality: Schematics and System Topologies

System topologies, Authority to Operate (ATO) trust enclave diagrams, MIL-STD-1553B avionics bus layouts, Piping & Instrumentation Diagrams (P&ID), and entity schemas translate complex structural architectures into deterministic graphical evidence.

---

## 1. The Rigor Continuum Progression Table

Schematic topologies scale their abstraction and terminal detail across three rigor levels:

| Rigor Level | Target Audience | Primary Focus | Schematic Mechanics & Topology Semantics |
| :--- | :--- | :--- | :--- |
| **L1 Orientation** | Program Executive, Non-Specialist | High-level system flows & operational concepts | Conceptual block diagrams, primary signal flow direction (left-to-right), subsystem bubbles, zero terminal pinouts or wire numbers. |
| **L2 Governance** | Security Architect (ISSM), Project Systems Engineer | Boundary compliance, trust enclaves, & delta lanes | ATO trust enclave perimeters, FIPS 140-3 boundary tags, PPSM IDs, architecture delta lanes (Baseline vs. Proposed vs. Decommissioned), compliance gates. |
| **L3 · Physical, Clinical & Metrological** | Electrical Engineer, Process/Grid Controls Specialist, ML Architect | Physical hardware wiring, industrial buses, & state interlocks | `120 Ω` SAE J1939 CAN-FD & RS-485/Modbus fieldbuses, `78 Ω` MIL-STD-1553B buses, `ISA-5.1` P&ID fluid/grid loops, normative FSM state machines, 4-lifeline safety interlocks, Crow's-foot ER lineage. |

---

## 2. Universal Schema: `urn:quiet-ui:schema:v9:schematic`

All topological and schematic structures must validate against the offline Quiet UI schematic schema:

```json
{
  "$schema": "urn:quiet-ui:schema:v9:schematic",
  "id": "schematic-optical-syntonization-3plane",
  "metadata": {
    "title": "3-Plane Optical Syntonization and DWDM Timing Distribution",
    "description": "Master clock reference, optical comb syntonizer, and DWDM edge distribution",
    "rigor_level": "L3",
    "timestamp_utc": "2026-11-16T19:30:00Z",
    "drawing_number": "DWG-OPT-SYNTH-8812-C"
  },
  "enclaves": [
    {
      "id": "enclave-atomic-vault",
      "label": "ENCLAVE 1: Master Atomic Frequency Standard",
      "trust_tier": "HIGH_CONFIDENCE_CORE",
      "fips_level": "FIPS 140-3 Level 3",
      "fill_token": "var(--bg-elevated)",
      "border_style": "dash-dot"
    },
    {
      "id": "enclave-dwdm-distribution",
      "label": "ENCLAVE 2: Optical DWDM Timing Network",
      "trust_tier": "MANAGED_DISTRIBUTION",
      "fips_level": "FIPS 140-3 Level 2",
      "fill_token": "var(--bg-elevated)",
      "border_style": "dashed"
    }
  ],
  "nodes": [
    {
      "id": "node-atomic-prs10",
      "enclave_id": "enclave-atomic-vault",
      "label": "PRS10 Rubidium Standard",
      "category": "frequency_reference",
      "nominal_frequency": "10.000000 MHz",
      "ports": [
        {"id": "p-rf-out", "label": "10MHz_OUT", "direction": "output", "impedance_ohms": 50}
      ]
    },
    {
      "id": "node-comb-synth",
      "enclave_id": "enclave-atomic-vault",
      "label": "Optical Frequency Comb Synthesizer",
      "category": "synthesizer",
      "ports": [
        {"id": "p-rf-in", "label": "REF_10M_IN", "direction": "input", "impedance_ohms": 50},
        {"id": "p-opt-out", "label": "OPT_COMB_OUT", "direction": "output", "wavelength_nm": 1550.12}
      ]
    },
    {
      "id": "node-dwdm-mux",
      "enclave_id": "enclave-dwdm-distribution",
      "label": "16-Channel ITU DWDM Multiplexer",
      "category": "optical_network",
      "ports": [
        {"id": "p-opt-in", "label": "LINE_IN", "direction": "input"},
        {"id": "p-drop-1", "label": "DROP_CH1", "direction": "output"},
        {"id": "p-mil-ctrl", "label": "1553B_RT", "direction": "bidirectional", "impedance_ohms": 78}
      ]
    }
  ],
  "edges": [
    {
      "id": "edge-rf-lock",
      "from_port": "node-atomic-prs10:p-rf-out",
      "to_port": "node-comb-synth:p-rf-in",
      "protocol": "COAXIAL_10MHZ",
      "cable_spec": "RG-316 / 50-ohm Double-Shielded",
      "style": "solid",
      "stroke_width": 2.0
    },
    {
      "id": "edge-optical-link",
      "from_port": "node-comb-synth:p-opt-out",
      "to_port": "node-dwdm-mux:p-opt-in",
      "protocol": "OPTICAL_DWDM_CH16",
      "fiber_type": "Corning SMF-28 Ultra",
      "crosses_enclave_boundary": true,
      "style": "solid",
      "stroke_color": "var(--accent-primary)"
    },
    {
      "id": "edge-avionics-bus",
      "from_port": "node-dwdm-mux:p-mil-ctrl",
      "to_port": "node-bus-controller:p-rt3",
      "protocol": "MIL-STD-1553B",
      "cable_spec": "Twinaxial Shielded Twisted Pair (78 ohm)",
      "termination": "78 ohm isolated stub",
      "style": "dashed",
      "stroke_color": "var(--tint-violet-fg)"
    }
  ],
  "routing": {
    "algorithm": "manhattan_orthogonal",
    "bridge_wire_crossings": true,
    "snap_to_grid_px": 16
  }
}
```

---

## 3. Orthogonal Routing, Port Anchoring, and Wire Crossing Jumps

Quiet UI schematics adhere to strict electrical drafting conventions:

### A. Manhattan Orthogonal Routing
- All signal paths, optical links, and data buses must route exclusively along horizontal and vertical axes (Manhattan geometry). Diagonal cuts across component bodies are prohibited.
- Minimum bend radius for rounded turns is $4\ \mathrm{px}$ (`rx: 4; ry: 4;`).

### B. Wire Crossing Bridge Glyphs vs. Junction Solder Dots
To avoid catastrophic ambiguity between crossing wires and connected junctions:
- **Connected Junctions (Tees & Crossings)**: Must be rendered with a solid circular solder dot ($\varnothing = 5.0\ \mathrm{px}$, fill `var(--text-primary)`).
- **Non-Connecting Intersections**: When two wires cross without electrical contact, the horizontal line bridges over the vertical line using a semi-circular arc jump ($\cap$, radius $5\ \mathrm{px}$).

### C. Signal Flow Directionality (NASA-STD-3001)
- Primary nominal signal flow progresses from **left to right**.
- High-level power distribution enters from the **top**.
- System ground, returns, and structural chassis anchor to the **bottom**.
- Closed-loop feedback paths route along the **lower perimeter** from right to left.

---

## 4. Architecture Delta Lanes: Baseline vs. Proposed vs. Decommissioned

In L2 governance reviews, schematics illustrate structural mutations using delta lanes:

```
+-----------------------------------------------------------------------+
| ARCHITECTURE DELTA LANES                                              |
| [ ] BASELINE (Unchanged): Solid neutral stroke (1.5 px)               |
| [+] PROPOSED (New Scope): Heavy primary stroke (2.5 px, green badge)  |
| [-] DECOMMISSIONED (Sunset): Strike-through red dashed line (1.5 px)  |
+-----------------------------------------------------------------------+
```

Components marked `DECOMMISSIONED` are visually retained in place but rendered with a subtle strikethrough hatch to provide contextual provenance for safety audits.

---

## 5. Medium Adaptation Rules

### Medium M1: Precision Static Print & PDF
- **Full Architecture Sheet**: Compiles to standard engineering title block format (ANSI D or ISO A3 landscape).
- **Monochrome Hatching**: Trust enclave boundaries use distinct pattern fills (`cross-hatch`, `dots`, `slanted-lines`) rather than solid color fills to ensure 100% legibility in pure black-and-white photocopy.

### Medium M3: Stateful Web Application
- **Interactive Enclave Expansion**: Clicking an enclave boundary collapses or expands internal subsystem nodes.
- **Signal Trace Highlighting**: Clicking any edge highlights the entire end-to-end signal route from origin oscillator to edge receiver while dimming unrelated components.

### Medium M6: Optical HUD & Tactical Console
- **Subsystem Status Vector**: Nodes display real-time go/no-go health rings. Fault propagation paths animate with flowing directional pulses.

---

## 6. Parameterized Differential Fieldbuses (`bus_standard`) & Enclave Partitioning

- **Parameterized `differential_bus` (`schematic_kind`)**: Set `"bus_standard"` to emit **`"can_fd"` / `"sae_j1939"`** (`120 Ω` split-termination automotive stubs `<= 0.3 m` on `CAN_H`/`CAN_L`), **`"rs485"` / `"modbus"`** (`120 Ω` end terminations + `560 Ω` fail-safe pull-up/down bias on `A`/`B`), or **`"mil1553b"`** (`78 Ω` twinaxial trunk + `58.5 Ω` transformer-coupled stubs).
- **Zero-Contamination Enclaves**: Every distinct `enclave_id` receives its own bounded perimeter rectangle; cross-enclave edges carry opaque `--bg-surface` label pills.

### Open-Standards Systems Compilers (`sequence`, `n2_matrix`, `fault_tree`)
Clean-room deterministic renderers in `compilers/schematic_systems.py` implement three open systems engineering standards:
- **`sequence` (`ITU-T Z.120`):** Actor headers, dashed lifelines, active execution bars, sync/async/reply message arrows, left timing gutter, and horizontal phase bands.
- **`n2_matrix` (`NASA SP-2016-6105`):** Diagonal subsystem nodes with orthogonally routed forward outputs (upper triangle) and telemetry/calibration feedback (lower triangle).
- **`fault_tree` (`NRC NUREG-0492`):** Top hazard box, standard geometric `OR`/`AND` logic gates, intermediate fault branches, circular basic events, and diamond undeveloped events.

## 7. Verification Checklist

Before emitting SVG markup:
- [ ] Conforms to schema URI `urn:quiet-ui:schema:v9:schematic`.
- [ ] Progression level matches target audience (`L1` orientation vs `L2` isolated ATO enclaves vs `L3` CAN-FD/Modbus/MIL-STD physical wiring).
- [ ] Non-connecting wire crossings utilize semi-circular bridge jumps ($\cap$).
- [ ] Connected electrical junctions carry prominent solder dots.
- [ ] Flow direction strictly follows left-to-right signal progression.

---

## 7. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [../rigor/metrology-and-nist-units.md](../rigor/metrology-and-nist-units.md)
- Conditions & Envelopes: [../rigor/conditions-and-envelopes.md](../rigor/conditions-and-envelopes.md)
- Tables & Matrices Modality: [tables-and-matrices.md](tables-and-matrices.md)
- Waveforms & Timing Modality: [waveforms-and-timing.md](waveforms-and-timing.md)
- Delivery Mediums: [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md)
- Audience Translation: [../../quiet-bridge/SKILL.md](../../quiet-bridge/SKILL.md)
