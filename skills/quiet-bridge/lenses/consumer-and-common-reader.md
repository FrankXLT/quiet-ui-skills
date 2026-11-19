# Audience Lens: Consumer & Common Reader

This guide defines the translation principles, plain-language guidelines, and calm interface standards required when communicating complex technical and engineering operations to non-specialist stakeholders, consumers, enterprise users, and public oversight bodies.

---

## 1. Persona Profile & Reader Psychology

| Dimension | Common Reader Specification |
| :--- | :--- |
| **Role Archetypes** | Patient / Caregiver, Cloud Service Subscriber, Plant Neighbor / Municipal Resident, Enterprise User, Public Oversight Inspector, Homeowner |
| **Context of Use** | Daily operational tracking, bedside or outpatient care updates, service outage inquiry, municipal utility/budget oversight, routine verification |
| **Cognitive Framework** | Outcome-oriented ("Is my system or care safe and working? What was delivered? Do I need to take action? How long will it take?") |
| **Acceptance Standard** | Plain English, unambiguous status anchors, transparent explanations without condescension, clear actionable next steps |
| **Reading Window** | 10 to 30 seconds for routine confirmation; 1 to 2 minutes during unexpected service degradation |

The common reader does not possess an engineering, clinical, or financial degree in your discipline, nor should they be required to have one to understand whether their service, care, or public infrastructure is functional and safe. When technical systems present raw memory addresses, clinical trial hazard ratios, cryptographic handshake jargon, or cryptic internal abbreviations, users experience anxiety and cognitive overload. Conversely, when explanations are over-simplified into meaningless marketing platitudes, users feel distrustful and manipulated.

---

## 2. Native Units of Proof

The common reader requires evidence rooted in human-scale reality and demonstrable utility:

1. **Clear Status Anchors**: Deterministic health states expressed in everyday language (`Operating Normally`, `Performance Slightly Reduced`, `Action Required: Action Needed by You`, `Service Offline for Scheduled Maintenance`).
2. **Plain-English Impact Summaries**: Quantified statements of delivered outcome (e.g., "All 42,000 files backed up safely to secondary storage at 3:15 AM", not "CRON job 14 completed with exit code 0"; or "In a `CONSORT`-tracked trial of 400 patients, 82% recovered within 48 hours vs. 64% on standard care").
3. **Direct Action Paths**: Unambiguous directives stating exactly who needs to do what, with an estimated duration (e.g., "Step 1 of 1: Check that the blue network cable is plugged firmly into the rear port. This takes 30 seconds.").
4. **Human Time Formats**: Absolute local time and relative elapsed duration (e.g., "Today at 2:15 PM (14 minutes ago)", rather than raw epoch integers `1763320500`).
5. **Real-World Physical Equivalents**: Converting abstract measurements into relatable dimensions (e.g., "1.2 GB of data — equivalent to roughly 300 high-resolution photos", or "Reserve balance covers 4.5 months of municipal operating costs per `GAO` audit rules").
6. **Transparent Diagnostic Context**: Explaining the *why* behind an anomaly in simple physical terms (e.g., "Network speed slowed because an automated system update was downloading", or "Infusion paused because `FDA IEC 62366` tubing occlusion sensor detected a kink").

---

## 3. Presenter Biases to Scrub

When translating technical telemetry for common readers, systematically eliminate the following presenter flaws:

```
[TECHNICAL PRESENTER BIAS]                         [COMMON READER SCRUB DIRECTIVE]
------------------------------------------------------------------------------------------------------------------------
Internal project acronyms (e.g., "DWDM", "LNA")     --> Translate to function: "High-capacity fiber connection", "Signal booster".
Hex register error codes (e.g., "ERR_0x8004100E")   --> Translate to cause: "Unable to reach database server".
Raw algorithmic notation (e.g., "O(N log N)")       --> Translate to user experience: "Search completes in less than 1 second".
Raw epoch millisecond timestamps                    --> Display human-readable local time: "Today at 9:30 AM".
Panic-inducing warning badges on benign background  --> Reserve amber/red strictly for conditions requiring active user intervention.
Passive engineering deflection ("an error occurred")--> State what happened and the system's self-healing response: "Reconnecting...".
```

---

## 4. Receiver Dealbreakers

An interface presented to a consumer or non-technical stakeholder will fail or induce user distress if it includes any of the following:

- **Alarmist Warning Colors for Safe States**: Rendering routine background tasks in bright orange or red badges, triggering unnecessary panic calls to support.
- **Dead-End Error Dialogs**: Informing the user of a malfunction without providing a clear next step, retry button, or support contact reference.
- **Opaque Technical Jargon**: Forcing users to decipher acronyms or network transport terms to understand basic billing or service status.
- **Condescending Simplification**: Using infantile language ("Oopsie! Something went wrong") that masks serious data loss or system degradation.
- **Hidden Progress State**: Displaying an indefinite spinning circle without text indicating the current sub-task or estimated remaining time.
- **Unbounded Wait Times**: Leaving the user uncertain whether a process takes 5 seconds, 5 minutes, or 5 hours.

---

## 5. Technical Team to Common Reader Translation Bridge

The following translation matrix bridges raw engineering phenomena into clear, human-centered language:

| Technical Telemetry & Failure Mode | Common Reader Translation Specification | Recommended Action Directive |
| :--- | :--- | :--- |
| "Egress queue buffer overflow on port eth0 resulting in 2.4% packet loss." | **Network Traffic High**: Your connection is experiencing heavy traffic, which may cause video or voice calls to briefly stutter. | "No action required. The system is prioritizing voice traffic automatically." |
| "Database connection pool exhausted; HTTP 503 Service Unavailable returned." | **System Busy**: Our servers are currently handling an unusually large number of requests. | "Please wait a moment and refresh this page in 2 minutes." |
| "TLS certificate expired on auxiliary metrics endpoint." | **Secure Connection Update**: We are renewing a security certificate on our background monitoring service. | "Your personal data and active sessions remain fully protected." |
| "Li-ion battery pack state of charge at 14%; cell balance delta 45 mV." | **Battery Low (14% Remaining)**: Estimated battery runtime is approximately 25 minutes under current usage. | "Plug in your charging adapter to avoid unexpected shutdown." |
| "SHA-256 verification mismatch on downloaded firmware image package." | **Download Verification Incomplete**: The downloaded update file was corrupted in transit. | "Click 'Restart Download' to safely download a fresh copy." |
| "HVAC compressor thermal tripwire open due to high head pressure." | **Cooling Temporarily Paused**: The air conditioning unit paused to protect its motor from overheating. | "Check the exterior intake filter for dust or debris; resumes in 10 min." |
| "Smart pump occlusion >= 450 mmHg (`FDA IEC 62366`); `CONSORT` arm B AE rate 1.8%." | **Medication Delivery Paused**: The IV pump stopped safely because it detected resistance in the tubing. | "Keep your arm straight and call your nurse to inspect the tubing." |
| "`OpenTelemetry` p99 > 4.2 s; `NIST AI RMF 100-1` fallback; `NIST SP 800-207` session re-auth." | **Slower Responses & Extra Sign-In**: Cloud AI search is running in safe mode during high load. | "Your saved work is intact; sign in again if prompted (~15 seconds)." |
| "`Modbus` Reg 40012 turbidity 1.4 NTU (`ISA-101` / `NRC NUREG-0700` interlock; `SPC C_pk` 1.18)." | **Water Filtration Maintenance**: Plant filter line 2 switched to backup so drinking water stays crystal clear. | "No boil-water notice. Normal pressure returns by 4:00 PM today." |
| "`GAO` fund balance covers 142 days; `FRED/SEC` municipal bond DSCR at 1.24x." | **City Capital Reserve Healthy**: Municipal reserve funds cover nearly five months of operations. | "No emergency tax surcharge needed; annual audit report is linked below." |

---

## 6. Calm Consumer Card Display Pattern

Consumer-facing status interfaces must emphasize calm visual anchors and clear text:

```
+----------------------------------------------------------------------------------------------------------------------+
| HOME POWER & STORAGE STATUS                                                              | TODAY: NOV 16, 2:30 PM    |
+----------------------------------------------------------------------------------------------------------------------+
| [ STATUS: OPERATING NORMALLY ]                                                                                       |
| All systems are healthy and running on clean solar power.                                                            |
|                                                                                                                      |
| CURRENT PERFORMANCE SNAPSHOT                                                                                         |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
| | SOLAR GENERATION        | HOME ELECTRIC USAGE     | BATTERY STORAGE LEVEL   | GRID ELECTRICITY                   | |
| | 4.8 kW (Strong Sunlight)| 1.4 kW (Normal Usage)   | 92% (Fully Charged)     | 0.0 kW (Self-Sufficient)           | |
| | Powering your home and  | Primary use: Refrig,    | Provides ~14 hours of   | You are currently sending excess   | |
| | charging home battery.  | Lighting, & AC fans.    | backup power tonight.   | clean energy back to the grid.     | |
| +-------------------------+-------------------------+-------------------------+------------------------------------+ |
|                                                                                                                      |
| UPCOMING SCHEDULED EVENT                                                                                             |
| Routine Maintenance: Automated overnight battery diagnostic scheduled for tonight at 2:00 AM.                       |
| Impact: No interruption to your home power. Diagnostic takes roughly 15 minutes.                                     |
| Recommended Action: None needed.                                                                                     |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 7. Flesch-Kincaid & Calm Palette Benchmarks

To guarantee accessibility across diverse reading backgrounds, all non-specialist interfaces must meet established readability and chromatic standards:

### Readability Standards
- **Grade Level Benchmark**: Target Flesch-Kincaid Grade Level between **6.0 and 8.5** (accessible to 85%+ of general readers).
- **Sentence Length**: Maximum 20 words per sentence; average 12 to 15 words.
- **Active Voice**: Minimum 80% active voice constructions ("We completed the update" rather than "The update was completed by our systems").
- **Acronym Elimination**: Zero undefined acronyms. If an acronym is industry standard (e.g., "Wi-Fi"), use it without parenthetical explanation.

### Calm Status Chromatic Palette
- **Normal / Healthy**: Subdued sage green (`oklch(0.72 0.08 145)`). Never neon or high-chroma green.
- **Informative Notice**: Neutral slate blue (`oklch(0.68 0.04 240)`).
- **User Action Required**: Warm amber (`oklch(0.74 0.12 75)`).
- **Service Outage / Stop**: Muted brick red (`oklch(0.62 0.14 25)`).

---

## 8. Common Reader Verification Rubric

Prior to publishing any consumer interface or stakeholder announcement, verify against these seven checklist items:

1. **Reading Level Compliance**: Does the text score at or below the 8th-grade Flesch-Kincaid readability benchmark?
2. **Zero Internal Acronyms**: Are all engineering project codes, internal subsystem names, and protocol acronyms eliminated?
3. **Explicit Next Action**: Does the interface tell the user what to do next, or clearly confirm that no action is needed?
4. **Calm Color Mapping**: Are bright warning colors withheld unless the user must take immediate action to prevent failure?
5. **Humanized Time Stamps**: Are timestamps presented in local 12-hour or 24-hour time with relative "minutes ago" context?
6. **Quantified Practical Impact**: Is the real-world impact clearly stated in units the reader cares about (minutes, dollars, files, hours of power)?
7. **Empathetic and Dignified Tone**: Does the explanation respect the reader's intelligence without relying on childish error cliches?

---

## 9. Before-and-After Translation Case Study

The following comparison illustrates a direct translation from internal engineering diagnostic logs into a calm consumer card:

```
[BEFORE: UNTRANSLATED ENGINEERING TELEMETRY]
[ERROR] 2026-11-16T19:04:12.891Z - PID 4812 - Daemon::IngressSyncWorker
Failed to complete periodic sync on socket /var/run/syncd.sock.
Errno: ETIMEDOUT (110: Connection timed out). Retry counter exceeded max_attempts (5).
Falling back to offline journal queue /var/spool/sync_journal.wal.
Dirty buffers: 48,192 bytes across 14 uncommitted transactions.

========================================================================================

[AFTER: CALM CONSUMER CARD TRANSLATION]
+--------------------------------------------------------------------------------------+
| SYNC STATUS: CONNECTING TO CLOUD BACKUP                                              |
+--------------------------------------------------------------------------------------+
| Your computer is temporarily unable to reach the backup server.                      |
|                                                                                      |
| What is happening:                                                                   |
| 14 recent documents are safely saved on your local computer.                         |
| They will be uploaded automatically as soon as your internet connection stabilizes.  |
|                                                                                      |
| Recommended Action:                                                                  |
| No action required. You can continue working normally.                              |
+--------------------------------------------------------------------------------------+
```

---

## 10. Cross-Reference Links

- For high-level schedule and program budgets, see [program-manager.md](program-manager.md).
- For technician-level physical pinouts and test procedures, see [technician-and-operator.md](technician-and-operator.md).
- For quick executive decision gate compression, see [../tempos/executive-minutes.md](../tempos/executive-minutes.md).
- For adversarial red-team audits of user-facing language, see [../protocols/adversarial-murder-board.md](../protocols/adversarial-murder-board.md).

