# Audience Lens: Project Systems Engineer & Technical Assessor

This guide defines the interface architecture, traceability protocols, and metrological rigor for technical artifacts delivered to Project Systems Engineers (PSE), Lead Systems Engineers (LSE), Interface Working Group (IWG) Chairs, and Authorizing Officials (AO / ATO Assessors).

---

## 1. Persona Profile & Systems Accountability

| Dimension | Systems Engineering Specification |
| :--- | :--- |
| **Role Archetypes** | Project Systems Engineer (PSE), Chief Systems Architect, Medical Device Human-Factors Lead (`FDA IEC 62366`), Zero-Trust / Cloud Security Architect (`NIST SP 800-207`, `NIST AI RMF 100-1`), Industrial Controls Architect (`ISA-101`, `NRC NUREG-0700`, `Modbus`), Civic Audit Systems Lead (`GAO`, `FRED/SEC`) |
| **Primary Workflow** | Interface Control Document (ICD) baselining, Verification Cross-Reference Matrix (VCRM) closure, timing/latency/SPC budget reconciliation, trust boundary auditing |
| **Cognitive Framework** | Contractual interfaces, boundary enclaves, end-to-end timing and telemetry chains, and total allocation conservation ($\sum \text{allocated} + \text{reserve} = \text{total capability}$) |
| **Acceptance Standard** | No requirement exists without an unambiguous verification method; no interface exists without an explicit port, protocol, pin or API/register contract, and margin entry |
| **Review Velocity** | Systematic, cross-boundary verification audits (15 to 45 minutes per interface envelope) |

Systems engineers and technical assessors operate at the physical, clinical, and digital seams between subsystems. They are acutely aware that multi-million dollar or life-safety failures rarely happen within well-modeled components; they occur at boundaries where assumptions drift, timing jitter or `OpenTelemetry` trace context is lost, `Modbus` registers or pin assignments mismatch, `FDA IEC 62366` use-error guards fail, or zero-trust enclaves fail to enforce mutual cryptographic authentication.

---

## 2. Native Units of Proof

To satisfy a Project Systems Engineer or Technical Assessor, documentation and UI displays must center on the following native units of proof:

1. **ICD Boundary Pin, Register, & API Matrices**: Precise table definitions containing source subsystem, destination subsystem, physical connector/port (`RS-422`, `LVDS`, `Modbus TCP` coil/register range, or `OpenTelemetry` gRPC/OTLP endpoint), schema version, and framing format.
2. **Verification Cross-Reference Matrices (VCRM)**: Direct mapping between subsystem requirement IDs, verification methods (Analysis, Inspection, Test, `FDA IEC 62366` Summative Usability, `CONSORT` protocol check), test procedure identifiers, and numerical margin status.
3. **End-to-End Interface Timing & Latency Chains**: Chronological budgets itemizing hardware serialization/setup/hold slack ($\Delta t_{\text{margin}}$ in ps/ns), `OpenTelemetry` cross-service p99 latency budgets, or `Modbus` SCADA polling scan cycles.
4. **Ports, Protocols, Services & Zero-Trust Policy (PPSM / `NIST SP 800-207`)**: Deterministic security table declaring IP transport protocol, port, unidirectional flow or Policy Enforcement Point (PEP) rule, cryptographic suite, and `NIST AI RMF 100-1` model gateway guardrails.
5. **Cryptographic & Safety Enclaves**: Architectural delineations identifying hardware perimeter boundaries (`FIPS 140-3` CMVP certs), `ISA-101` / `NRC NUREG-0700` safety-PLC air-gaps, or clinical PHI isolation zones.
6. **Margin Conservation Trees**: Hierarchical rollups proving that allocations for mass, peak electrical power, cloud error budgets, `NIST/SEMATECH SPC C_pk` tolerances, or `GAO` / `FRED/SEC` capital encumbrances conserve total system budgets without negative margin.
7. **Traceability Hash Chains**: Cryptographic SHA-256 hashes binding each interface line to the exact repository commit, test artifact, `SEC` filing/ledger snapshot, and verification dataset.

---

## 3. Presenter Biases to Scrub

When compiling interface packages for systems engineers, scrub the following presentation flaws:

```
[PRESENTER BIAS]                                   [SYSTEMS SCRUB DIRECTIVE]
------------------------------------------------------------------------------------------------------------------------
Hyper-detailed SPICE transistor micro-simulations   --> Abstract to interface pin characteristics: Zin, Voh, Vol, tr/tf.
High-level non-technical summary bullets            --> Replace with explicit ICD clause numbers and VCRM verification rows.
Floating subsystem metrics without margin budgets   --> Bind every metric to its parent system allocation and remaining delta.
Ad-hoc undocumented protocol dialect extensions    --> Force standard RFC/MIL-STD compliance or log as formal ICD waiver.
Untraced engineering modifications ("we adjusted")  --> Require formal Engineering Change Proposal (ECP) reference ID.
Broad trust assertions ("secure internal network")  --> Explicitly define PPSM port rules, TLS version, and enclave boundary.
Subjective compliance claims ("partially tested")   --> Report discrete numerical VCRM closure: OPEN, CLOSED-TEST, or WAIVED.
```

---

## 4. Receiver Dealbreakers

An artifact presented to a Project Systems Engineer or ATO Assessor will be rejected with prejudice upon encountering any of the following triggers:

- **Unallocated Timing Jitter or Asynchronous Clock Drift**: Declaring bus interfaces without defining clock domains, FIFO depth margins, or metastability MTBF.
- **Undefined Port Protocols or Framing Schemas**: Labeling a connection as "Telemetry Link" without stating Ethernet encapsulation, UDP port number, packet header structure, and byte endianness.
- **Missing FIPS or Cryptographic Boundary Declarations**: Omitting the physical or logical enclave perimeter across which unencrypted sensitive telemetry traverses.
- **Orphan Requirements in VCRM**: Presenting an interface requirement with an unassigned verification method or without a mapped test script.
- **Negative Mass, Power, or Bandwidth Reserve**: Hiding negative margin through optimistic duty cycles or ungrounded "future optimization" claims.
- **Uncoordinated Pin Reassignments**: Changing a pin signal definition on one side of an interface without a verified counter-signature from the mating subsystem owner.

---

## 5. Systems Engineer to ATO Authorizing Official Translation Bridge

The following translation matrix bridges systems engineering architectural designs into security assessment controls:

| Systems Engineering ICD Specification | ATO Security Assessment Verification Contract | PPSM & Boundary Rule |
| :--- | :--- | :--- |
| "Subsystem A transmits health telemetry to Subsystem B over internal 100BASE-TX Ethernet at 10 Hz rate." | **Boundary Control AC-4 / SC-8**: Bidirectional traffic prohibited; hardware diode or iptables firewall enforces unidirectional UDP stream. Zero unauthenticated control commands accepted on port. | PPSM Entry: Port 40102/UDP, Payload: Encrypted JSON, Rate: 64 kbps, Ingress filter: Subsys-B only. |
| "Payload command bus uses mutual TLS 1.3 with hardware-backed Elliptic Curve certificates." | **Cryptographic Assurance SC-12 / IA-5**: Ephemeral ECDHE key exchange over Curve25519; certificates issued by offline project CA; private keys stored inside FIPS 140-3 Level 3 HSM. | PPSM Entry: Port 8443/TCP, FIPS Module Cert #4412, Session timeout: 300 s, Re-auth on disconnect. |
| "Chassis maintenance port allows diagnostic firmware updates during pre-flight integration." | **Physical Enclave Isolation PE-3 / MP-6**: Physical locking cover over RJ-45 connector; micro-switch interlock disconnects internal programming pins when flight plug is installed. | Port Disconnect: Mechanically isolated in flight configuration; zero remote access vector. |
| "FPGA Bitstream loaded from non-volatile SPI Flash upon power-on reset." | **Supply Chain & Integrity SI-7**: Bitstream signed with ECDSA-P384; cryptographic signature verified by hard-wired secure boot ROM before release of system reset. | Boot Vector: SHA-384 hash validated in hardware engine; zero unauthenticated bitstream execution. |
| "External serial sensor interface uses RS-422 differential signaling at 115.2 kbps." | **Interface Sanitization SI-10**: Ingress UART buffer enforces strict length bounds and schema verification; malformed packets dropped with error counter incremented. | PPSM Entry: Hardware Serial Port UART-3, Payload: Fixed-length 64-byte frame, Hardware CRC-16. |
| "Smart infusion pump orders sync via HL7/FHIR from EHR pharmacy engine (`CONSORT` trial arm)." | **Clinical Use-Risk Guard (`FDA IEC 62366`)**: Dose ceiling hard-stop and dual-clinician confirmation enforced at pump UI boundary; mismatched units rejected. | Boundary Rule: TLS 1.3 + signed HL7 schema; soft/hard limit mismatch halts actuation. |
| "AI triage inference gateway calls vector store and LLM service across multi-tenant VPC." | **Zero-Trust & AI Boundary (`NIST SP 800-207`, `NIST AI RMF 100-1`, `OpenTelemetry`)**: Per-request mTLS via Policy Enforcement Point; OTLP `traceparent` propagated; low-confidence outputs routed to deterministic fallback. | PPSM Entry: Port 443/gRPC, SPIFFE/mTLS, OTel span attestation, prompt-guard filter. |
| "PLC Line 4 reads 64 pressure/temperature tags over `Modbus TCP` to Plant Historian." | **ICS Enclave & Control Room (`ISA-101`, `NRC NUREG-0700`, `NIST/SEMATECH SPC`)**: Unidirectional data diode separates Level 1 PLC from Level 3 Historian; `Modbus` write coils disabled from IT zone. | PPSM Entry: Port 502/TCP read-only diode; `SPC` tag scan <= 250 ms; alarm rate <= 6/10 min. |
| "Municipal treasury ERP posts daily debt-service and grant drawdown feeds to public portal." | **Fiscal Integrity & Audit Boundary (`GAO`, `FRED/SEC`)**: Immutable append-only ledger hashes every disbursement against appropriated budget line and `FRED`/`SEC` benchmark feed. | Boundary Rule: Dual-key HSM sign-off; SHA-256 ledger digest archived per `GAO` Green Book. |

---

## 6. End-to-End Interface Timing Chain Breakdown

Systems engineers demand absolute timing certainty across synchronous and asynchronous physical boundaries. The timing chain must account for every picosecond:

```
+----------------------------------------------------------------------------------------------------------------------+
| SYNCHRONOUS BUS TIMING CHAIN: 100 MHz SYSTEM CLOCK DOMAIN (T_clk = 10.00 ns)                                        |
+----------------------------------------------------------------------------------------------------------------------+
| TRANSMITTER SUBSYSTEM (FPGA-A)     | PCB INTERCONNECT & HARNESS         | RECEIVER SUBSYSTEM (ASIC-B)                |
|                                    |                                    |                                            |
| Clock-to-Output Delay (T_co):      | Trace Propagation Flight Time:     | Setup Time Requirement (T_setup):          |
|   Min: 1.20 ns | Max: 2.80 ns      |   T_pd = 1.65 ns (+/- 0.15 ns)     |   Minimum: 1.40 ns                         |
|                                    |                                    |                                            |
| Transmitter Clock Skew (T_skew_tx):| Differential Pair Skew (T_skew_p):| Hold Time Requirement (T_hold):           |
|   Max: 0.18 ns                     |   Max: 0.08 ns                     |   Minimum: 0.60 ns                         |
|                                    |                                    |                                            |
| Jitter Budget (T_jitter):          | Intersymbol Interference Penalty:  | Receiver Clock Skew (T_skew_rx):           |
|   Max: 0.22 ns                     |   Max: 0.14 ns                     |   Max: 0.24 ns                             |
+------------------------------------+------------------------------------+--------------------------------------------+
| TIMING CLOSURE MARGIN CALCULATION:                                                                                   |
| Setup Margin: T_clk - [T_co_max + T_pd_max + T_skew_total + T_jitter + T_isi + T_setup]                              |
| Setup Margin: 10.00 ns - [2.80 + 1.80 + 0.50 + 0.22 + 0.14 + 1.40] ns = 10.00 ns - 6.86 ns = +3.14 ns (31.4% MARGIN)|
| Hold Margin:  T_co_min + T_pd_min - T_skew_total - T_hold = 1.20 + 1.50 - 0.50 - 0.60 = +1.60 ns (POSITIVE HOLD)   |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Interface Control Matrix (ICD) Interface Display Pattern

When displaying interface boundaries on a systems workbench or review display, enforce tabular clarity:

```
+----------------------------------------------------------------------------------------------------------------------+
| ICD BOUNDARY SPECIFICATION: SUBSYSTEM INTERFACE MATRIX [ICD-AV-408 REV C]                   | STATUS: BASELINED       |
+----------------------------------------------------------------------------------------------------------------------+
| IF ID   | SOURCE   | DEST     | PHYSICAL PORT | PROTOCOL / RATE | TIMING MARGIN | ENCLAVE TRUST | VCRM CLOSURE STATUS|
|---------+----------+----------+---------------+-----------------+---------------+---------------+--------------------|
| IF-101  | GNC-FC-1 | THRUST-A | J4-Pins 12-14 | RS-422 / 1 Mbps | +420 ns (32%) | Flight-Crit 1 | CLOSED (TEST-GNC-4)|
| IF-102  | GNC-FC-1 | SENS-IMU | J2-Pins 01-08 | SPI / 10 MHz    | +18.4 ns (28%)| Flight-Crit 1 | CLOSED (TEST-IMU-2)|
| IF-201  | TELEM-TX | GROUND-S | LC-OPT-01     | 10G-LR / 10.3G  | +3.2 dB (opt) | Payld-Enc 2   | OPEN (AIR-TEST-08) |
| IF-304  | PWR-DIST | BAT-MON  | CAN-J1-Pins3/4| CAN-2.0B / 500k | +110 ns (19%) | Housekeep 0   | CLOSED (TEST-PWR-1)|
+----------------------------------------------------------------------------------------------------------------------+
| TOTAL BUS BANDWIDTH UTILIZATION BUDGET: 42.1% [MAX ALLOCATED: 60.0%] | REMAINING MARGIN: +17.9% [ACCEPTABLE]          |
| TOTAL SUBSYSTEM DC POWER ALLOCATION: 184.2 W [MAX VEHICLE ALLOCATED: 220.0 W] | UNALLOCATED RESERVE: 35.8 W (16.3%)   |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 8. Systems Engineer Interface Verification Rubric

Before submitting interface revisions, architectures, or review documentation to a Systems Engineering panel, audit against these seven criteria:

1. **Explicit Boundary Definition**: Is every interconnecting node identified with physical connector designators, signal electrical levels, and pin assignments?
2. **Timing Budget Closure**: Are bus propagation, sampling latencies, and clock skew variations calculated with positive margins against worst-case temperature?
3. **PPSM Completeness**: Is every network socket, port, and serial channel documented with protocol, source/destination IP/MAC, and filtering policy?
4. **Traceability to Level-2 Requirements**: Does every line in the ICD link directly to an approved systems requirement in the engineering baseline?
5. **VCRM Method Specification**: Is the verification approach explicitly categorized into Analysis, Inspection, Test, or Demonstration with assigned test document IDs?
6. **Margin Conservation**: Are shared resources (power, bandwidth, mass, thermal capacity) balanced to ensure zero negative margins across the complete operational envelope?
7. **Trust Boundary Hardening**: Are data paths crossing security enclaves authenticated with validated cryptographic hardware mechanisms?

---

## 9. ICD Change Control & Interface Waiver Lifecycle

Interfaces between subsystems are contractual commitments. When an interface fails to meet baselined allocations, it enters the formal waiver lifecycle:

```
[DISCIPLINE VARIANCE DETECTED]
              |
              v
[STEP 1: IMPACT QUANTIFICATION]
- Calculate Delta-Timing (ps), Delta-Power (W), Delta-Mass (g).
- Identify all affected mating subsystems and pin assignments.
              |
              v
[STEP 2: TRADE-OFF RECONCILIATION]
- Can the absorbing subsystem surrender reserve margin without exceeding ceiling?
- If YES: Submit Engineering Change Proposal (ECP) with bilateral concurrence.
- If NO: Escalate to Interface Working Group (IWG) for architecture redline.
              |
              v
[STEP 3: FORMAL WAIVER BASELINE]
- Record approved waiver ID in VCRM closure column (e.g. "WAIVED-WVR-2026-04").
- Append expiration timestamp and flight phase constraints to canonical ICD JSON.
```

---

## 10. Cross-Reference Links

- For component-level physical proofs and raw sensor telemetry, see [discipline-engineer.md](discipline-engineer.md).
- For technician-level wiring harnesses, pinouts, and test points, see [technician-and-operator.md](technician-and-operator.md).
- For executive gate decision matrices and critical path scheduling, see [program-manager.md](program-manager.md).
- For formal adversarial review room procedures, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).

