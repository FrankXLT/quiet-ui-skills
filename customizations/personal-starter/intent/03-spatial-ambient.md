# Personal Blueprint — 03 Optical Viewport HUD & Tactile Console

## 1. Scope & Tiers
Brings mission-critical spatial observation and direct subsystem control into high-consequence operational environments:
- **15. HUD-1 (Optical Viewport / AR HUD):** Features `>= 65%` unobstructed central sightline with floating smoked-glass telemetry pods (`.va-hud-pod`), Apollo 8 Earthrise (`as08-14-2383`) backplate, and collimated optical readouts.
- **16. Ctrl-1 (Tactile Subsystem Console):** Arm's-reach walk-up touch interface with 2-step guarded effector controls (`ARM` $\rightarrow$ `EXECUTE`), commanded-vs-actual state discrepancy badges, and subsystem rack selectors.

## 2. Invariants & Universal Responsive Support
Smoked-glass pods enforce subtle white borders and backdrop blur (`backdrop-filter: blur(18px) saturate(150%)`), while interactive effectors provide distinct touch boundaries (`>= 44px` on coarse pointers). Dedicated mobile tiers are retired in favor of universal responsive layouts (`390×844` phone thumb bar, `820×1180` crease-aware tablet split) across all 16 tiers.
