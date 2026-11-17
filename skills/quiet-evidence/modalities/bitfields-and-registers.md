# Modality: Bitfields and Hardware Registers

Bitfield maps, Base Address Register (BAR) memory layouts, and Memory-Mapped I/O (MMIO) visualizers provide deterministic inspection of low-level embedded hardware registers.

---

## 1. Visual Anatomy & Bitfield Strip Representation

Quiet UI renders hardware registers as contiguous horizontal bit strips indexed from Most Significant Bit (MSB) down to Least Significant Bit (LSB):

```
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
| 31 | 30 | 29 | 28 | 27 | 26 | 25 | 24 | 23 | 22 | 21 | 20 | 19 | 18 | 17 | 16 |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
| EN |LOCK|  PWR_MODE |    CHAN_SEL     |           TEMP_WARN_LIMIT             |
| RW | RO |    RW     |       RW        |                 RW                    |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
| 15 | 14 | 13 | 12 | 11 | 10 |  9 |  8 |  7 |  6 |  5 |  4 |  3 |  2 |  1 |  0 |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
|TX_F|LOS |         RESERVED            |            BURST_ERROR_CNT            |
|W1C | RO |            RO               |                  RC                   |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
```

---

## 2. The Rigor Continuum Progression Table

Register visualizers adapt their technical depth across the three rigor levels:

| Rigor Level | Target Audience | Primary Focus | Display Anatomy & Content |
| :--- | :--- | :--- | :--- |
| **L1 Orientation** | High-Level Systems Operator | Functional module readiness & operational state | High-level status pill (`TRANSMITTER READY`, `PLL LOCKED`), mode summary, zero raw bit manipulation. |
| **L2 Governance** | Embedded Firmware Developer, FPGA Architect | Memory mapping, bit offsets, & access rules | Symbolic register name, hexadecimal address offset, bit range spans (`[31:28]`), access types (`RO`, `RW`, `W1C`), default reset values, and interlock masks. |
| **L3 Physical / Metrological** | Silicon Validation Engineer, Driver Author | Bit-level truth, live memory dumps, & hardware hazards | Exact bit-level grid (31..0), live hexadecimal register value (`0x8004A01C`), side-effect flags (read-to-clear, self-clearing), bus latency, and errata references. |

---

## 3. Universal Schema: `urn:quiet-ui:schema:v9:bitfield`

All register and bitfield specifications must conform to the offline schema:

```json
{
  "$schema": "urn:quiet-ui:schema:v9:bitfield",
  "id": "reg-bar0-optical-csr-0040",
  "metadata": {
    "title": "Optical Transceiver Control and Status Register",
    "mnemonic": "CSR_OPTICAL_STATUS_CTRL",
    "description": "BAR0 MMIO transceiver control, PLL status, and burst error counter",
    "rigor_level": "L3",
    "address_offset": "0x0040",
    "register_width_bits": 32,
    "reset_value": "0x00000000",
    "current_value": "0x8004A01C"
  },
  "fields": [
    {
      "name": "LASER_ENABLE",
      "bit_range": [31, 31],
      "access": "RW",
      "reset": 0,
      "current_value": 1,
      "description": "Master optical pump laser enable. 1 = Active emission, 0 = Standby.",
      "safety_critical": true
    },
    {
      "name": "PLL_LOCK_STATUS",
      "bit_range": [30, 30],
      "access": "RO",
      "reset": 0,
      "current_value": 0,
      "description": "Hardware clock synthesiser PLL lock flag. 1 = Locked, 0 = Unlocked."
    },
    {
      "name": "OPTICAL_POWER_MODE",
      "bit_range": [29, 28],
      "access": "RW",
      "reset": 0,
      "current_value": 0,
      "description": "Power attenuation mode. 00 = 0 dB, 01 = -3 dB, 10 = -6 dB, 11 = Mute."
    },
    {
      "name": "CHANNEL_SELECT",
      "bit_range": [27, 24],
      "access": "RW",
      "reset": 0,
      "current_value": 4,
      "description": "DWDM ITU optical grid channel index (0..15)."
    },
    {
      "name": "TEMP_WARN_LIMIT",
      "bit_range": [23, 16],
      "access": "RW",
      "reset": 0,
      "current_value": 160,
      "description": "Temperature alarm threshold in 0.5 °C steps (0x00 = 0 °C, 0xA0 = 80 °C)."
    },
    {
      "name": "TX_FAULT_FLAG",
      "bit_range": [15, 15],
      "access": "W1C",
      "reset": 0,
      "current_value": 1,
      "description": "Transmitter optical over-current fault. Write 1 to clear."
    },
    {
      "name": "RX_LOSS_OF_SIGNAL",
      "bit_range": [14, 14],
      "access": "RO",
      "reset": 0,
      "current_value": 0,
      "description": "Optical receiver Loss of Signal (LOS). 1 = Signal lost, 0 = Power normal."
    },
    {
      "name": "RESERVED",
      "bit_range": [13, 8],
      "access": "RO",
      "reset": 0,
      "current_value": 0,
      "description": "Reserved for future hardware revision. Must be preserved as 0."
    },
    {
      "name": "BURST_ERROR_COUNT",
      "bit_range": [7, 0],
      "access": "RC",
      "reset": 0,
      "current_value": 28,
      "description": "Cumulative burst parity error counter. Reading register clears count."
    }
  ]
}
```

---

## 4. Access Type Classification & Visual Semantics

Register fields use standardized color-coding and border treatments to prevent operational mistakes:

| Access Type | Description | Palette Token | Border Treatment |
| :--- | :--- | :--- | :--- |
| **RO** (Read-Only) | Status flag or counter driven exclusively by hardware logic | `var(--bg-elevated)` | Solid subtle border |
| **RW** (Read-Write) | Configuration parameter written by driver software | `var(--tint-indigo-bg)` | Solid distinct border |
| **W1C** (Write-1-to-Clear) | Latched interrupt or fault; writing binary `1` resets flag | `var(--tint-amber-bg)` | Dashed amber border |
| **RC** (Read-to-Clear) | Hardware counter reset to zero upon read access | `var(--tint-violet-bg)` | Dotted purple border |
| **WO** (Write-Only) | Hardware trigger command; reading returns undefined data | `var(--tint-rose-bg)` | Solid warning border |

---

## 5. Medium Adaptation Rules

### Medium M1: Precision Static Print & PDF
- **Row Splitting**: On standard A4/US-Letter portrait pages, 32-bit and 64-bit registers automatically split into two 16-bit or four 8-bit stacked rows to prevent illegible micro-typography.
- **Printed Legend**: An explicit tabular footnote itemizes all bit spans, access types, reset defaults, and physical units.

### Medium M3: Stateful Web Application
- **Interactive Bit Toggling**: In RW fields, users can click individual bits to toggle between `0` and `1`. An instant hex preview updates in real time.
- **Direct Hex/Binary Calculator**: Two-way synchronization between hex input box (`0x8004A01C`) and the graphical bitfield layout.
- **Side-Effect Warning**: Clicking W1C or RC fields triggers a non-modal confirmation banner warning of hardware state destruction.

### Medium M6: Optical HUD & Tactile Console
- **Glanceable Segment Ribbon**: Renders as a continuous 32-segment LED bar. Bits with active fault flags (`TX_FAULT_FLAG = 1`) pulse at $2\ \mathrm{Hz}$ in high-contrast amber.
- **Monospace Value Callout**: Current value is displayed in large monospace text: `BAR0+0040: 8004_A01C`.

---

## 6. Verification Checklist

Before finalizing any register visual:
- [ ] Conforms to schema URI `urn:quiet-ui:schema:v9:bitfield`.
- [ ] All 32 (or 16/64) bits are accounted for without unexplained index gaps.
- [ ] Access types (`RO`, `RW`, `W1C`, `RC`) are explicitly designated with correct styling.
- [ ] Reset vectors and current values are declared in valid hexadecimal notation.
- [ ] Reserved bits are marked `RO` with reset value `0`.

---

## 7. Integration Links
- Back to Pillar Overview: [SKILL.md](../SKILL.md)
- NIST Metrology & Units: [../rigor/metrology-and-nist-units.md](../rigor/metrology-and-nist-units.md)
- Tables & Matrices Modality: [tables-and-matrices.md](tables-and-matrices.md)
- Waveforms & Timing Modality: [waveforms-and-timing.md](waveforms-and-timing.md)
- Delivery Mediums: [../../quiet-ui/SKILL.md](../../quiet-ui/SKILL.md)
