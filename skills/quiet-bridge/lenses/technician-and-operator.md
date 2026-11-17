# Audience Lens: Technician and Field Operator

This guide defines the translation rules, verification criteria, and presentation standards for interfaces delivered to field technicians, flight-line mechanics, plant operators, and bench testing specialists.

---

## 1. Persona Profile & Operational Context

| Dimension | Operational Specification |
| :--- | :--- |
| **Role Archetypes** | Avionics Field Technician, Substation Operator, Network Operations Specialist, Integration & Test (I&T) Mechanic |
| **Operational Environment** | Flight line, industrial switchgear vault, test stand, mobile operations van, high-noise and high-vibration bays |
| **Physical Constraints** | Heavy nitrile or leather gloves, safety glasses with tint, direct sunlight or low-lux emergency lighting, 1.0 m to 1.8 m stand-off viewing distance |
| **Decision Window** | 5 seconds (alarm tripwire) to 3 minutes (step sign-off) |
| **Cognitive Stance** | Skeptical of abstract software assertions; requires physical, verifiable proof before actuating switches or signing procedures |

Field operators bear direct accountability for hardware survival, personal safety, and mission continuity. They do not trust synthesized health indices or ungrounded trendlines; they require discrete physical measurements mapped to identifiable test points, connector pins, and mechanical switch states.

---

## 2. Native Units of Proof

To establish credibility with this audience, every displayed status must tie directly to measurable physical entities:

1. **Connector Pins and Terminal Blocks**: Explicit designators conforming to interface wiring diagrams (e.g., `J3-Pin 14`, `TB-04-Pos 2`, `P102-B / CAN_H`).
2. **Discrete Electrical Tolerances**: Raw voltage with explicit limits rather than binary "OK" (e.g., `28.2 VDC [26.0–30.0 VDC limit]`, not "Power Normal").
3. **RF and Optical Margins**: Explicit signal levels and attenuation (e.g., `Rx Power: -14.2 dBm [Margin: +4.8 dB above receiver sensitivity]`).
4. **Physical Switch and Interlock States**: Direct state telemetry (e.g., `Relay K4: ENERGIZED (NO Closed)`, `Interlock S2: OPEN (Tripped)`).
5. **Procedure Step Bindings**: One-to-one mapping between UI actionable controls and numbered runbook operational steps (e.g., `Runbook SOP-704 Step 4.2.1`).
6. **Calibration Traceability Stubs**: Displaying the active calibration certificate ID and expiration date for any measuring channel generating displayed numbers.

---

## 3. Presenter Biases to Scrub

When translating engineering documentation into operator interfaces, remove the following habitual presenter artifacts:

```
[DISCIPLINE PRESENTER BIAS]                        [OPERATOR SCRUB RULE]
------------------------------------------------------------------------------------------------------------------------
Abstract mathematical derivations (e.g. S-parameters)  --> Replace with calibrated VSWR/dBm pass-fail reading.
Continuous Bezier curves through discrete samples       --> Display actual point measurements with tolerance bands.
Multi-quarter budgetary or lifecycle forecasting        --> Strip entirely; operators require current operational state.
High-level synthetic health scores (e.g., "94% Ready")  --> Unroll into discrete component status table.
Unreferenced hex register offsets (e.g., "Reg 0x3F")    --> Translate to human-readable bitfield and actuator state.
Floating-point micro-precision (e.g., "28.183921 V")    --> Round to calibrated resolution of field instrument (e.g., "28.2 V").
```

---

## 4. Receiver Dealbreakers

An interface presented to an operator will be immediately rejected or cause operational error if it contains any of the following flaws:

- **Missing Pin, Port, or Terminal Identifiers**: Showing a failed signal without stating the exact physical port or pin connector.
- **Ambiguous Advisory Colors**: Using yellow or amber for an informative non-actionable status, creating alarm fatigue.
- **Hidden or Undocumented Override Procedures**: Requiring complex menu nesting to execute an emergency interlock bypass.
- **Unstated Environmental Redlines**: Showing temperature or pressure without the absolute shutdown limit adjacent to the gauge.
- **Unlatched Transient Alarms**: Alarms that disappear when the physical condition normalizes before the operator can acknowledge and read the fault signature.
- **Unclear Lockout / Tagout (LOTO) Boundaries**: Displaying an actuator control as available when physical upstream disconnects or safety interlocks are tripped.

---

## 5. Discipline Engineer to Operator Translation Bridge

The following translation matrix bridges theoretical discipline specifications into operational field directives:

| Discipline Engineering Assertion | Operator Translation Specification | Verification Checkpoint |
| :--- | :--- | :--- |
| "RF amplifier $S_{11}$ input return loss degrades to $-11\text{ dB}$ at $2.45\text{ GHz}$ under thermal saturation." | **Port RF-IN (SMA-J1)**: High reflection detected. Standing Wave Ratio is **1.78:1** (Limit: $\le 1.50:1$). Reduce drive power or inspect cable J1. | Field Power Meter reading at test port TP-4. |
| "Bus voltage ripple exceeds 450 mV peak-to-peak during transient pulse load." | **Main DC Bus (P1-A/B)**: Voltage spike detected. Instantaneous swing: **27.1 to 29.8 VDC** (Max allowable ripple: $0.40\text{ VDC}$). | Oscilloscope probe at TP-12. |
| "Optical transceiver exhibits 2.8 dB link budget degradation due to dirty ferrule." | **Fiber Channel A (LC-Rx-01)**: Input light level is **-18.4 dBm** (Minimum link threshold: $-16.0\text{ dBm}$). Clean optical ferrule with dry cassette. | Optical Power Meter (1310 nm). |
| "FPGA core junction temperature exceeds $85^\circ\text{C}$ margin ceiling." | **Processing Unit Heat Sink (Zone 2)**: Core temp is **$89^\circ\text{C}$** (Redline: $85^\circ\text{C}$, Abort: $95^\circ\text{C}$). Auxiliary cooling fan B must be energized. | Thermocouple channel TC-08. |
| "Differential pressure sensor $\Delta P$ delta approaches cavitation boundary." | **Cooling Loop Pump 1**: Suction pressure is **14.2 psia** (Cavitation redline: $\le 12.0\text{ psia}$). Bleed accumulator valve V-102. | Analog pressure gauge PG-102. |
| "CAN-bus physical layer frame CRC error rate exceeds 1.2e-4 errors/frame." | **Harness W-102 (Pins J2-7 / J2-8)**: High frame errors. Check termination resistor $R_T = 120\,\Omega \pm 2\,\Omega$ across lines CAN_H and CAN_L. | Digital Multimeter across pin 7 and pin 8 with power de-energized. |

---

## 6. Concrete Operator Console Interface Pattern

Field-grade interfaces must present deterministic state information with guarded execution controls.

```
+----------------------------------------------------------------------------------------------------------------------+
| RUNBOOK: SOP-ENG-204 | STEP 3.4: HIGH-VOLTAGE ENERGIZE                       | STATION: BAY-04 | OPERATOR: TECH-2    |
+----------------------------------------------------------------------------------------------------------------------+
| [SYSTEM STATUS: INTERLOCK READY]                                                     CURRENT TIME: 14:22:08 UTC     |
|                                                                                                                      |
| PHYSICAL SENSOR METROLOGY & PINOUT VERIFICATION                                                                      |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
| | TEST POINT TP-01        | TEST POINT TP-02        | CONNECTOR J2-PIN 4      | BREAKER CB-104                     | |
| | Physical: Harness W-10  | Physical: Harness W-12  | Signal: SAFETY_INTLK_RTN| Line: Inverter Primary Feed        | |
| | Measured: +28.18 VDC    | Measured: 4.12 A        | State: CLOSED           | State: CLOSED                      | |
| | Limits: [26.0 - 30.0]   | Limits: [0.00 - 8.00]   | Redline: CONTINUITY     | Trip Rating: 15.0 A                | |
| | Cal: NIST-8820 (Exp 12m)| Cal: NIST-8820 (Exp 12m)| Loop: Dry Contact       | Status: ARMED                      | |
| | Status: PASS (NORMAL)   | Status: PASS (NORMAL)   | Status: PASS (ARMED)    | Visual Tag: TAG-104-CLEAR          | |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
|                                                                                                                      |
| STEP EXECUTION GUARD & LOTO SAFETY MATRIX                                                                            |
| Required Action: Energize Primary Inverter Bus via Switch SW-01.                                                     |
| Prerequisites: TP-01 in band, Interlock closed, Breaker set. ALL VERIFIED.                                          |
|                                                                                                                      |
| [ STEP 3.4.1: CONFIRM PREREQUISITES ]   [ STEP 3.4.2: ARM CONTACTOR ]   [ STEP 3.4.3: DEPRESS SW-01 TO ENERGIZE ]    |
| (STATUS: VERIFIED AUTOMATICALLY)        (STATUS: ARMED - 10s TIMEOUT)   [GUARDED EFFECTOR: REQUIRES DUAL-KEY / LATCH]|
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Field Operator Troubleshooting Decision Ladder

When a parameter deviates outside normal acceptance bands, the interface must provide an unambiguous, non-recursive diagnostic sequence:

```
[OBSERVED FAULT SIGNATURE]
           |
           v
[LEVEL 1: HARNESS & INTERCONNECT]
- Measure continuity across designated connector pins (J[x] to P[y]).
- Verify mating torque (e.g. 8 in-lbs on SMA connectors).
- Inspect optical fiber end-faces with 400x scope for contamination.
           |
           +--> IF FAULT PERSISTS
           |
           v
[LEVEL 2: POWER & GROUND VERIFICATION]
- Probe secondary DC rail at test point TP-02 with calibrated DMM.
- Verify chassis ground bonding resistance <= 2.5 mOhm.
- Confirm AC phase balance within +/- 2.0% on 3-phase feeds.
           |
           +--> IF FAULT PERSISTS
           |
           v
[LEVEL 3: LINE REPLACEABLE UNIT (LRU) SWAP]
- Record active register error codes to non-volatile run log.
- Execute Lockout/Tagout (LOTO) procedure SOP-SAF-012.
- Swap LRU module; re-verify baseline cal certificate before re-energizing.
```

---

## 8. Field Operator Redline Rubric

Before releasing any artifact, diagram, or UI view intended for technician or operator consumption, evaluate it against this seven-point audit:

1. **Pin and Port Specificity**: Is every physical interface tagged with its engineering drawing identifier (`J[x]`, `P[x]`, `TB[x]`)?
2. **Tolerance Band Display**: Does every numerical readout state its lower and upper acceptance redlines in the same physical unit?
3. **No Decorative Ambiguity**: Are all decorative graphical flourishes, smooth splines, and uncalibrated progress bars eliminated?
4. **Guarded Action Path**: Do destructive or high-energy actions require a two-step deliberate confirmation sequence?
5. **Runbook Synchronization**: Does the view reference the exact revision, section, and step number of the authorizing procedure?
6. **Calibration Evidence**: Are measuring channels accompanied by valid calibration expiration stamps?
7. **LOTO Visibility**: Is upstream safety isolation state prominently declared before presenting any downstream actuator control?

---

## 9. Cross-Reference Links

- For higher-level system boundary definitions, see [project-systems-engineer.md](project-systems-engineer.md).
- For first-principles physics and raw sensor derivation, see [discipline-engineer.md](discipline-engineer.md).
- For tactical second-by-second anomaly response layouts, see [../tempos/tactical-seconds.md](../tempos/tactical-seconds.md).
- For adversarial pre-flight redline audits, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).
