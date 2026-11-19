# Operational Decision Tempo: Tactical Seconds (5–15 Seconds)

This guide defines the interface architecture, alarm management standards, and interaction physics required for high-velocity operational environments where human decisions must be executed within 5 to 15 seconds.

---

## 1. Operating Tempo & Cognitive Constraints

| Parameter | Operational Specification |
| :--- | :--- |
| **Decision Window** | 5 to 15 seconds from visual stimulus to verified effector or intervention actuation |
| **Operational Modes** | Flight/test-stand abort, ICU bedside smart-pump & vitals triage (`FDA IEC 62366`, `CONSORT`), SRE / AI production incident containment (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`), SCADA / nuclear plant tripwire (`ISA-101`, `NRC NUREG-0700`, `Modbus`, `NIST/SEMATECH SPC`), treasury settlement circuit-breaker (`GAO`, `FRED/SEC`) |
| **Cognitive Stress Level** | High acute stress, tunnel vision, degraded working memory, elevated heart rate |
| **Sensory Channel** | Peripheral visual glance, high-contrast optical annunciator tiles, deterministic acoustic alerts |
| **Interaction Standard** | Zero-latency rendering (< 16 ms), zero nested menus, guarded physical or software 2-step effectors |

Under acute tactical conditions, human cognitive bandwidth collapses to immediate perceptual processing. Complex hierarchical navigation, hidden drawers, and ambiguous multi-state icons become catastrophic failure modes—whether in an aerospace control room, an ICU bay (`FDA IEC 62366`), a cloud incident bridge, or a `NRC NUREG-0700` / `ISA-101` industrial console. The interface must act as an unvarnished transducer of real-time state, presenting unambiguous bounds and immediate guarded action paths.

---

## 2. Information Density & Anti-Decoration Mandate

In the tactical seconds tempo, information density is strictly calibrated to essential telemetry:

1. **Zero Non-Critical Chrome**: Eliminate all decorative gradients, ambient drop shadows, brand headers, and promotional banners (`ISA-101` / `NRC NUREG-0700` dull-screen principle).
2. **Glanceable State Dominance**: The primary operational state (`NORMAL`, `DEGRADED`, `TRIPWIRE`, `ABORT`) must occupy immediate visual hierarchy, readable from 2.0 meters away.
3. **High Signal-to-Ink Ratio**: Every pixel on the screen must convey operational meaning. Grid lines, borders, and typography must serve functional grouping.
4. **Deterministic Spatial Fixity**: Telemetry indicators must never shift position, reorder dynamically, or reflow during an anomaly. Spatial memory must remain 100% reliable.
5. **Calibrated Color Tokens**: Colors are reserved strictly for operational state transitions according to `ANSI/ISA-18.2` and `FDA IEC 62366` alarm-fatigue safeguards.

---

## 3. ANSI/ISA-18.2 Alarm Prioritization Hierarchy

To prevent operator alarm flooding and cognitive paralysis during cascade anomalies, alarms are partitioned into four deterministic tiers:

| Tier | Priority Label | Visual Cue & Color Token | Audio Cue | Target Operator Action |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **CRITICAL / TRIPWIRE** | High-contrast Solid Brick Red (`oklch(0.60 0.22 25)`), 3px solid border | 1000 Hz continuous pulse | Immediate protective action to prevent loss of life, vehicle, or facility (< 10 seconds). |
| **Tier 2** | **WARNING / HIGH** | High-contrast Warm Amber (`oklch(0.72 0.16 65)`), 2px solid border | 500 Hz intermittent tone | Timely corrective intervention to prevent automatic trip or damage (< 60 seconds). |
| **Tier 3** | **ADVISORY / MEDIUM** | Subdued Slate Yellow (`oklch(0.78 0.08 85)`), 1px solid border | Single 250 Hz chime | Procedural awareness of parameter drift outside nominal band. |
| **Tier 4** | **DIAGNOSTIC / LOW** | Muted Slate Gray (`oklch(0.65 0.02 240)`), 1px dashed border | Silent (Visual log only) | Informational status; logged for post-test analysis. |

### The Anti-Flash Invariant
Never use flashing, blinking, or pulsating CSS animations on text or containers. Flashing induces visual fatigue, obscures typographical legibility, and impairs cognitive reading speed under stress. State changes are communicated via immediate color transition, high-contrast borders, and prominent textual alarm badges.

---

## 4. Glanceable Annunciator Grid Pattern

Tactical interfaces rely on a spatial annunciator grid where every cell represents a discrete subsystem health envelope:

```
+----------------------------------------------------------------------------------------------------------------------+
| TACTICAL FLIGHT CONTROLLER CONSOLE: RUN 14B                                          | MISSION TIME: T+00:04:18.42   |
+----------------------------------------------------------------------------------------------------------------------+
| ANNUNCIATOR MATRIX (4x2 SUBSYSTEM HEALTH MATRIX)                                                                     |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
| | MAIN PROPULSION (ZONE 1)| GUIDANCE & NAV (ZONE 2) | ELECTRICAL BUS (ZONE 3) | THERMAL REJECTION (ZONE 4)         | |
| | [ STATE: NOMINAL ]      | [ STATE: NOMINAL ]      | [ STATE: NOMINAL ]      | [ STATE: WARNING - TIER 2 ]        | |
| | Chamber P: 184.2 psia   | Gyro Drift: 0.002 deg/s | Bus Volts: 28.18 VDC    | Loop B Pump: CAVITATING            | |
| | Flow: 42.1 kg/s         | Attitude Err: 0.04 deg  | Load: 42.4 A (52%)      | Delta-P: 11.4 psia [LIMIT: 12.0]   | |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
| | CRYOGENIC FEED (ZONE 5) | TELEMETRY RF (ZONE 6)   | PAYLOAD LINK (ZONE 7)   | SAFETY INTERLOCKS (ZONE 8)         | |
| | [ STATE: NOMINAL ]      | [ STATE: NOMINAL ]      | [ STATE: NOMINAL ]      | [ STATE: NOMINAL ]                 | |
| | Tank Ullage: 44.1 psia  | Rx Margin: +8.4 dB      | BER: 1.2e-11            | Range Destruct: ARMED              | |
| | Boil-off: 0.12 kg/hr    | S11: -18.2 dB           | Frame Slip: 0           | Pad Gantry: DISENGAGED             | |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
|                                                                                                                      |
| ACTIVE TRIPWIRE INTERVENTION: THERMAL LOOP B CAVITATION                                                              |
| Required Response: Command Hot-Standby Pump A to active primary; depressurize Loop B return bypass.                 |
+----------------------------------------------------------------------------------------------------------------------+
```

### 4.1 Cross-Domain Tactical Annunciator & Guarded Effector Examples

| Domain | Fixed Annunciator Telemetry & Corridor | Guarded Two-Step Effector (`Arm -> Actuate`) |
| :--- | :--- | :--- |
| **Clinical Safety / ICU (`FDA IEC 62366`, `CONSORT`)** | Pump Ch-2 Occlusion `480 mmHg [Limit <= 450]`; SpO2 `91% [Floor 92%]`. | Step 1: Arm Bolus Pause -> Step 2: Dual-clinician confirm & verify flow = `0.0 mL/hr`. |
| **SRE / AI Ops (`OpenTelemetry`, `NIST AI RMF 100-1`, `NIST SP 800-207`)** | Auth PEP p99 `1,420 ms [Limit <= 250]`; AI ECE drift `0.09 [Fallback 0.05]`. | Step 1: Arm Pod-7 Drain / Rule Fallback -> Step 2: Confirm OTel traffic shift to Pod-8. |
| **Industrial SCADA (`ISA-101`, `NRC NUREG-0700`, `Modbus`, `SPC C_pk`)** | `Modbus` Reg `40012` Temp `74 C [Redline 72]`; `SPC` $C_{pk}$ `1.08 [Min 1.33]`. | Step 1: Arm Bypass `BV-02` -> Step 2: Confirm `Modbus` limit-switch closed & temp drop. |
| **Civic Treasury Settlement (`GAO`, `FRED/SEC`)** | Intraday Liquidity `104% [Floor 110%]`; Margin Reserve Delta `-$1.8M`. | Step 1: Arm Outbound Batch-14 Hold -> Step 2: Dual-officer HSM token sign-off. |

---

## 5. Guarded Two-Step Effector Controls

To eliminate inadvertent triggering of high-energy or mission-critical effectors while preserving sub-10-second response times, tactical interfaces enforce a deterministic two-step interaction latch:

```
[RESTING STATE: GUARDED]
+-------------------------------------------------------------+
| [ STEP 1: ARM AUX PUMP A ]  (STATUS: DISARMED)              |
+-------------------------------------------------------------+
               |
               v (Operator clicks or taps ARM)
[STATE 2: ARMED - 10 SECOND COUNTDOWN LATCH]
+-------------------------------------------------------------+
| [ ARMED: 00:08s REMAINING ] -> [ CLICK TO ENERGIZE PUMP A ] |
+-------------------------------------------------------------+
               |
               +--> [NO ACTION WITHIN 10s] --> REVERTS TO DISARMED
               |
               v (Operator executes Step 2 within window)
[STATE 3: EXECUTED & TELEMETRY CONFIRMED]
+-------------------------------------------------------------+
| [ PUMP A: ENERGIZED ] | CONFIRMED: 4.2 A DRAW AT TP-04      |
+-------------------------------------------------------------+
```

### Invariants for Guarded Effectors
- **No Ambiguous Modals**: Avoid standard web popups with "Cancel" and "OK" that obscure background telemetry.
- **In-Place Morphing**: The button or switch container morphs within its existing spatial bounding box.
- **Auto-Disarm Timeout**: If the second action is not executed within 10 seconds, the latch automatically disarms to prevent accidental late actuation.
- **Physical Telemetry Confirmation**: The success state is verified by downstream physical current/flow sensors, not merely by the issuance of the control command.

---

## 6. Immediate Tripwire Overrides

When an emergency threshold is breached, the tactical interface provides dedicated, direct-action tripwire abort controls that bypass procedural sequences:

```
+----------------------------------------------------------------------------------------------------------------------+
| EMERGENCY OVERRIDE STRIP (PERSISTENT STAGE HEADER - 64px HEIGHT)                                                     |
| [ ! EMERGENCY MANUAL SHUTDOWN ! ]                                            [ ABORT SEQUENCE LATCH: DISARMED ]      |
| Hold for 1.5 seconds to trip Master Fuel Valve Isolation                   (Slide right or enter shortcut Alt+Shift+Q)|
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Audit Trail & Black Box Telemetry Logging

Every tactical interaction, state transition, and operator acknowledgement must be recorded to a high-speed non-volatile audit journal:

```json
{
  "event_id": "EVT-2026-11-16-90412",
  "timestamp_utc": "2026-11-16T19:42:04.182Z",
  "epoch_ms": 1763322124182,
  "alarm_tier": "TIER_2_WARNING",
  "sensor_id": "PUMP_B_SUCTION_DP",
  "measured_value": 11.4,
  "redline_limit": 12.0,
  "operator_id": "FLIGHT_CONTROLLER_3",
  "action_executed": "ARM_AND_ENERGIZE_PUMP_A",
  "latency_to_arm_ms": 2410,
  "latency_to_actuate_ms": 1840,
  "total_response_time_ms": 4250,
  "downstream_telemetry_verified": true,
  "verified_current_amps": 4.18
}
```

---

## 8. Tactical Seconds Verification Rubric

Before deploying an interface for tactical operations, verify against these seven mission-readiness criteria:

1. **Sub-15-Second Action Path**: Can a trained operator identify the anomalous subsystem, arm the effector, and execute corrective action within 15 seconds?
2. **Deterministic Spatial Layout**: Are all critical indicators fixed in permanent screen coordinates that never reflow or scroll?
3. **ANSI/ISA-18.2 Prioritization**: Are alarms strictly separated into four discrete tiers with clear color and acoustic distinctions?
4. **Zero Flashing Elements**: Are all flashing, strobing, or animated UI elements eliminated?
5. **Guarded Two-Step Controls**: Do all irreversible commands require an explicit Arm $\rightarrow$ Actuate confirmation latch with auto-disarm timeout?
6. **Telemetry Verification Feedback**: Does the UI display physical sensor confirmation of the actuation within 500 ms of command transmission?
7. **Complete Audit Journaling**: Is every operator keystroke, click, and alarm acknowledgment logged with millisecond timestamps?

---

## 9. Cross-Reference Links

- For field operator pinouts and physical test point verification, see [../lenses/technician-and-operator.md](../lenses/technician-and-operator.md).
- For executive minute-by-minute gate compression, see [executive-minutes.md](executive-minutes.md).
- For analytical post-test investigation (10–45 min), see [analytical-deep-dive.md](analytical-deep-dive.md).
- For adversarial red-team stress testing of emergency controls, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).
