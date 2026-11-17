# Modality: Tables and Matrices

Structured tabular grids, compliance registers, Ports Protocols & Services Management (PPSM) matrices, and correlation heatmaps structure high-density multidimensional engineering evidence.

---

## 1. The Rigor Continuum Progression Table

Tables and matrices adapt their column density, cryptographic detail, and physical parameters across the three rigor levels:

| Rigor Level | Target Audience | Primary Focus | Grid Anatomy & Column Allocations |
| :--- | :--- | :--- | :--- |
| **L1 Orientation** | Program Executive, Non-Specialist | High-level service catalog & operational state | Service Name, Endpoint / Domain, Operational Role, Status (`ACTIVE`, `DEGRADED`, `OFFLINE`). Minimal technical jargon, aggregated metrics. |
| **L2 Governance** | Security Officer (ISSM/ISSO), Systems Engineer | Boundary compliance, PPSM, & ATO certification | PPSM Protocol ID, Boundary Interface, Trust Enclave Source/Dest, Transport Protocol / Port, Encryption Standard (e.g., FIPS 140-3 TLS 1.3), ATO Disposition, Approval Ticket. |
| **L3 Physical / Metrological** | Network Architect, Communications Engineer | Physical socket, MTU, timing, & packet error metrology | Exact IP / CIDR, Physical MAC / NIC Port, MTU / Buffer Depth, Measured Latency with Uncertainty ($(4.12 \pm 0.08)\ \mathrm{ms}$), Packet Jitter, Bit Error Rate (BER). |

---

## 2. Universal Schema: `urn:quiet-ui:schema:v9:table`

All quantitative tabular data and security matrices must validate against the offline Quiet UI table schema:

```json
{
  "$schema": "urn:quiet-ui:schema:v9:table",
  "id": "matrix-ppsm-enclave-boundary",
  "metadata": {
    "title": "Ports, Protocols, and Services Matrix (PPSM)",
    "description": "Cross-enclave boundary network security and cryptographic disposition",
    "rigor_level": "L2",
    "timestamp_utc": "2026-11-16T19:30:00Z",
    "classification": "UNCLASSIFIED // CONTROLLED TECHNICAL DATA"
  },
  "columns": [
    {
      "key": "ppsm_id",
      "label": "PPSM ID",
      "data_type": "string",
      "alignment": "left",
      "priority": 1,
      "width_hint": "110px"
    },
    {
      "key": "service_name",
      "label": "Service Designation",
      "data_type": "string",
      "alignment": "left",
      "priority": 1,
      "width_hint": "180px"
    },
    {
      "key": "source_enclave",
      "label": "Source Enclave",
      "data_type": "string",
      "alignment": "left",
      "priority": 2,
      "width_hint": "140px"
    },
    {
      "key": "dest_enclave",
      "label": "Destination Enclave",
      "data_type": "string",
      "alignment": "left",
      "priority": 2,
      "width_hint": "140px"
    },
    {
      "key": "port_protocol",
      "label": "Transport / Port",
      "data_type": "string",
      "alignment": "left",
      "priority": 1,
      "width_hint": "120px"
    },
    {
      "key": "crypto_standard",
      "label": "Cryptographic Protection",
      "data_type": "string",
      "alignment": "left",
      "priority": 2,
      "width_hint": "160px"
    },
    {
      "key": "latency_ms",
      "label": "Latency (ms)",
      "quantity_calculus": "t_lat / ms",
      "unit": "ms",
      "data_type": "numeric",
      "alignment": "right",
      "priority": 3,
      "width_hint": "100px"
    },
    {
      "key": "disposition",
      "label": "ATO Disposition",
      "data_type": "status",
      "alignment": "center",
      "priority": 1,
      "width_hint": "120px"
    }
  ],
  "default_sort": {
    "key": "ppsm_id",
    "direction": "ascending"
  },
  "rows": [
    {
      "id": "row-01",
      "ppsm_id": "PPSM-0842-A",
      "service_name": "Precision Timing PTP",
      "source_enclave": "ENCLAVE-TIME-01",
      "dest_enclave": "ENCLAVE-TELEMETRY",
      "port_protocol": "UDP / 319-320",
      "crypto_standard": "IEEE 1588-2019 Annex P",
      "latency_ms": 0.084,
      "disposition": "AUTHORIZED"
    },
    {
      "id": "row-02",
      "ppsm_id": "PPSM-0842-B",
      "service_name": "Optical Telemetry Stream",
      "source_enclave": "ENCLAVE-OPTICAL",
      "dest_enclave": "ENCLAVE-CORE-ENG",
      "port_protocol": "TCP / 8443",
      "crypto_standard": "TLS 1.3 / AES-256-GCM",
      "latency_ms": 1.420,
      "disposition": "AUTHORIZED"
    },
    {
      "id": "row-03",
      "ppsm_id": "PPSM-0842-C",
      "service_name": "Legacy Serial Diagnostic",
      "source_enclave": "ENCLAVE-HIL-TEST",
      "dest_enclave": "ENCLAVE-LEGACY-BUS",
      "port_protocol": "TCP / 2023",
      "crypto_standard": "PLAINTEXT (ISOLATED VLAN)",
      "latency_ms": 8.650,
      "disposition": "CONDITIONAL"
    }
  ]
}
```

---

## 3. Desktop Zero-Clipping Rules & Layout Engineering

Uncontrolled horizontal scrolling or cell clipping renders technical matrices unusable. Quiet UI enforces strict desktop layout rules:

### A. Column Alignment Standards
- **Numerical Quantities**: Must be **right-aligned** using tabular monospace figures (`font-variant-numeric: tabular-nums;`). Decimal points must align vertically.
- **Textual Identifiers & Strings**: Must be **left-aligned** with text-overflow handling.
- **Status Pills & Badges**: Must be **centered** within a fixed-width container.

### B. Priority-Tiered Column Hierarchy
When display widths contract, columns are managed according to declared priorities ($1 = \text{Essential}, 2 = \text{Secondary}, 3 = \text{Auxiliary}$):
- Priority 1 columns never hide or wrap into unreadable shapes.
- Priority 2 and 3 columns utilize compact abbreviations or tuck into expandable sub-rows rather than forcing desktop horizontal scrollbars.

### C. Zero Truncation of Critical Identifiers
Unique keys such as UUIDs, PPSM identifiers, IP addresses, and hash digests must **never be truncated** with ellipsis (`...`). Wrap strings using zero-width break opportunities (`<wbr>`) or allow monospace hyphenation.

---

## 4. Mobile Responsive Card View Fallback

On narrow viewports ($< 768\ \mathrm{px}$) or mobile technician tablets, traditional wide matrices break readability. Quiet UI compilers automatically transform tables into structured **Evidence Cards**:

```
+-----------------------------------------------------------+
| PPSM-0842-A                    [ AUTHORIZED ]             |
| Precision Timing PTP                                      |
+-----------------------------------------------------------+
| Transport:     UDP / 319-320                              |
| Source:        ENCLAVE-TIME-01                            |
| Destination:   ENCLAVE-TELEMETRY                          |
| Protection:    IEEE 1588-2019 Annex P                     |
| Latency:       0.084 ms (t_lat / ms)                      |
+-----------------------------------------------------------+
```

### Card Fallback Invariants
1. **Zero Data Loss**: Every column defined in the parent table must appear as a key-value pair within the card view.
2. **Preserved Sorting & Filtering**: Card stacks maintain identical sort order and search filters configured in the matrix header.
3. **Touch Targets**: Expand/collapse affordances must meet NASA-STD-3001 tap target minimums ($44 \times 44\ \mathrm{px}$).

---

## 5. Verification Checklist

Before emitting HTML or PDF tables:
- [ ] Conforms to schema URI `urn:quiet-ui:schema:v9:table`.
- [ ] Rigor progression table accurately maps columns to audience.
- [ ] Numerical columns are right-aligned with tabular figures.
- [ ] No unique identifiers or cryptographic keys are clipped with ellipses.
- [ ] Responsive breakpoint provides 100% data preservation in mobile card view.

---

## 6. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [../rigor/metrology-and-nist-units.md](../rigor/metrology-and-nist-units.md)
- Bitfields & Registers Modality: [bitfields-and-registers.md](bitfields-and-registers.md)
- Schematics & Topologies: [schematics-and-topologies.md](schematics-and-topologies.md)
- Delivery Mediums: [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md)
