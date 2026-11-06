# `quiet-ui-skills` — Featuring *The Quiet UI Canvas* (17-Tier Anti-Slop Visual Architecture System v4.6)

> **Eliminate generic AI-generated layout slop, top-of-page KPI card bloat, and "pill/color soup" — while embracing Universal Pure White (`S1`) Default legibility, a Non-Overlapping Top Studio Bar + OA Workbench Sidebar Swatches, Earned Expressiveness (`C3`), tactile corner control, and vector icon precision.**
> **`quiet-ui-skills`** equips coding agents (**Claude Code**, **Google Antigravity**, **Gemini CLI**, **Devin Desktop**, and **Cursor**) with a deterministic, 100% brand-free **17-Tier Graduated Visual Architecture System**, standalone CSS tokens ([`tokens/quiet-ui-tokens.css`](tokens/quiet-ui-tokens.css)), and **The Quiet UI Canvas** interactive showcase ([`quiet-ui-showcase.html`](quiet-ui-showcase.html) & [`docs/index.html`](docs/index.html)).

> [!TIP]
> ### 1-File Standalone Desktop Viewer ([`quiet-ui-showcase.html`](quiet-ui-showcase.html))
> Want to explore all **17 Mediums**, **4 Color Themes (`S1–S4`)**, **4 Densities (`D1–D4`)**, **5 Corner Stops (`0px`–`18px`)**, **3 Color Policies (`C1–C3`)**, and **5 Navigation Topologies (`N0–N4`)** offline?
> Download **[`quiet-ui-showcase.html`](quiet-ui-showcase.html)** (a 100% self-contained single HTML file with embedded assets, including the CC0 Claude Monet *Water Lilies* canvas) and double-click it on your desktop (`file:///`) in any browser—**zero build step, zero server, and zero external local file dependencies required.**

![The Quiet UI Canvas — 4-Family Architectural Overview](docs/assets/hero_4family_overview.png)

---

## Quickstart Installation

```bash
git clone https://github.com/FrankXLT/quiet-ui-skills.git
cd quiet-ui-skills
bash install.sh
```

- Installs `visual-architecture-system` into `~/.agents/skills/visual-architecture-system` and `~/.gemini/config/skills/visual-architecture-system` (or pass a custom path: `bash install.sh ./my-repo/.agents/skills/visual-architecture-system`).
- **Standalone CSS Tokens (Dual-Licensed MIT for Commercial Embedding):** Import [`tokens/quiet-ui-tokens.css`](tokens/quiet-ui-tokens.css) directly into any HTML, React, Vue, Svelte, or Home Assistant project:
  ```html
  <link rel="stylesheet" href="tokens/quiet-ui-tokens.css">
  ```
- **Live Interactive Showcase:** Open [`quiet-ui-showcase.html`](quiet-ui-showcase.html) (or [`docs/index.html`](docs/index.html)) directly in any browser or enable GitHub Pages on `/docs`.

---

## What's New in v4.6 (Pure White Default, Non-Overlapping Top Studio Bar, OA Sidebar Swatches & `App-Tree` Domain Workbench)

1. **Universal Pure White (`S1`, `data-theme="white"`) Default Across All 17 Tiers:** Every tier loads in crisp daylight Pure White (`#ffffff`) by default (`switchTier()` preserves your active theme selection), with theme-aware light surfaces on `15. HA-1` (Frosted Light Glass HUD in `S1`/`S2` modes), `05. Doc-4A` sticky code panes, and `.va-mermaid-code` source blocks.
2. **Outer Perimeter Breathing Room & Inset Stage Frame (`.va-stage-outer`):** Wraps the active tier stage in an `8px 10px` shell buffer with a `1px solid var(--border-grid)` rounded stage border and `2px 6px` inset left-rail items featuring a `3px` accent bar + soft pill fill when `.active`.
3. **Non-Overlapping Top Studio Control Bar (`#va-floating-dock`) + OA Workbench Sidebar Footer Swatches (`.va-oa-sidebar-footer`):**
   - Replaces the floating bottom overlay with a dedicated `40px` sticky **Top Studio Bar** (`[‹ Prev]`, direct 17-tier `<select>`, `[Next ›]`, recessed `[Auto|N0|N1|N2|N3|N4]` trough, 4 circular theme swatches, Corners `Auto/0/6/12/18`, Density `D1–D4`, and 1-click `[Copy Prompt]`) that never covers bottom `N4` docks or right-hand inspectors.
   - Every left sidebar includes a sticky bottom `.va-oa-sidebar-footer` tray with 4 circular theme swatches (`White`, `Paper`, `Sepia`, `Dark`), `Soft / Crisp`, and `D1 / D2 / D3` pills.
4. **Domain-Safe `N0–N4` Adaptability (`14. App-Tree`) & Theme-Matched Drawer Scrim:** `14. App-Tree` preserves its `Object Explorer` DB Schema + File Tree pane across `N0`, `N2`, and `N4` with `28px` collapsible edge tabs (`«`/`»`), live object/row filters, 8 boundary-node rows with `4px` status bars, and a TimescaleDB compression KPI strip.
5. **Non-Overlapping `30px` Label Headers in All Composite Screenshots (`docs/assets/*.png`):** Every multi-panel composite and contact sheet allocates a dedicated `30px` header bar above each panel (`0px` overlap on top `N2`/`N3` taskbars).

---

## The 17-Tier Graduated Continuum (Universal `S1` Pure White Default $\rightarrow$ Live 4-Theme Switching)

| # | Tier ID | Structural Archetype | Box Weight | Default Theme | Default Nav | Primary Use Cases |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| `01` | **`Doc-1`** | Academic & Scientific Monograph | `0%` | `S1` White | `N1` | Whitepapers, mathematical derivations, research monographs |
| `02` | **`Doc-2`** | Executive Decision Memo (`BLUF` + Mermaid) | `15%` | `S1` White | `N0` | Board memos, architecture decision records, post-mortems |
| `03` | **`Doc-3`** | Normative RFC Specification (+ Mermaid FSM) | `25%` | `S1` White | `N0` | Protocol specs, RFCs, `MUST`/`SHALL` compliance audits |
| `04` | **`Doc-4B`** | Encyclopedic SDK & API Reference | `25%` | `S1` White | `N3` | Library SDK references, module/class/function dictionaries |
| `05` | **`Doc-4A`** | Split-Pane Operational Runbook (+ Mermaid Seq) | `45%` | `S1` White | `N1` | Deployment playbooks, incident response SOPs, tutorials |
| `06` | **`Bridge-1`** | Parametric Engineering Worksheet | `50%` | `S1` White | `N0` | Interactive trade studies, link-budget calculators, notebooks |
| `07` | **`Deck-1`** | Viewport-Locked Briefing Stage | `60%` | `S1` White | `N1` | `100dvh` assertion-evidence briefings with zero page scroll |
| `08` | **`Bridge-2`** | High-Density Data Table & Status Grid (`1px` Grid) | `100% 1px Grid` | `S1` White | `N2` | High-density tabular ledgers, fleet audits, benchmark grids |
| `09` | **`App-2`** | Live Metrics & Time-Series Console | `100% 1px Grid` | `S1` White | `N1` | Multi-channel strip charts, timing analyzers, register matrices |
| `10` | **`App-1`** | Compact Issue & Ticket Tracker | `0% Cards (Rows)` | `S1` White | `N1` | `36px` single-line issue queues + live right inspector |
| `11` | **`App-4`** | Task & Calendar Planner (+ Focus Hero) | `80%` | `S1` White | `N1` | Active Focus Session Hero, 3-zone staging backlog, time blocks |
| `12` | **`App-3`** | KPI & Analytics Dashboard (Bento Grid) | `100% Cards` | `S1` White | `N2` | 12-col executive KPI & SLA health grid (4 layers per card) |
| `13` | **`App-5`** | Daily Pacing & Wellness Planner (+ Readiness Hero) | `75%` | `S1` White | `N1` | Readiness Ring Hero (`84 · Steady`), 24h Day Arc, vertical timeline |
| `14` | **`App-Tree`** | Hierarchical Tree, Schema & File Explorer | `90% 3-Pane` | `S1` White | `N1` | 3-pane coupled Schema/File tree (`1px` indent guides) + 3-tab workbench |
| `15` | **`HA-1`** | Ambient Wall Kiosk Screensaver (Monet + Light Glass) | `20% HUD` | `S1` White | `N0` | 10-foot `60/40` Claude Monet canvas + `blur(22px)` frosted light/dark glass HUD |
| `16` | **`HA-2`** | Room-First Wall Control Panel | `85%` | `S1` White | `N1` | Walk-up room cards (`<= 4` metrics/room, `.va-icon-well`) + fixture dock |
| `17` | **`HA-3`** | Crease-Aware Foldable & Phone Controller | `85%` | `S1` White | `N4` | `56px` full-row slider tiles, `820px` 50/50 fold split & `390px` thumb bar |

![All 17 Tiers @ Full Desktop Viewport](docs/assets/contact_sheet_full.png)

---

## Visual Proof Gallery

### 1. Color Theme (`S1–S4`), Earned Expressiveness (`C1–C3`) & 5-Stop Corner Radius Dial

![4-Mode Color Theme Engine (S1 White, S2 Paper, S3 Dark Paper, S4 Dark)](docs/assets/surface_polarity_4modes.png)

### 2. Task & Calendar Planner (`11. App-4`) & Daily Pacing & Wellness Planner (`13. App-5`)

| `11. App-4` · Task & Calendar Planner (+ Focus Hero) | `13. App-5` · Daily Pacing & Wellness Planner (+ Readiness Hero) |
| :---: | :---: |
| ![Tier 11 App-4 Task and Calendar Planner](docs/assets/tier_11_app4_temporal_workbench.png) | ![Tier 13 App-5 Daily Pacing and Wellness Planner](docs/assets/tier_13_app5_restorative_companion.png) |

### 3. Progressive-Disclosure Home Assistant Architecture (`15. HA-1` Monet Glass, `16. HA-2`, `17. HA-3`)

![Family D Home Assistant Tiers (HA-1, HA-2, HA-3)](docs/assets/tier_14_15_16_home_assistant.png)

### 4. Responsive Navigation (`R1–R3` Desktop $\rightarrow$ `R4` `900px` Foldable Icon Rail $\rightarrow$ `R5` `390px` Phone Bottom Dock)

![Responsive Navigation Across Desktop, Foldable 900px, and Phone 390px](docs/assets/nav_morphing_desktop_fold_phone.png)

| Unfolded Foldable (`R4 · 900px` Across All 17 Tiers) | Portrait Phone Handset (`R5 · 390px` Across All 17 Tiers) |
| :---: | :---: |
| ![All 17 Tiers @ Foldable 900px](docs/assets/contact_sheet_fold.png) | ![All 17 Tiers @ Phone 390px](docs/assets/contact_sheet_phone.png) |

---

## Automated Visual Contract & Zero-PII Verifier

```bash
python3 skills/visual-architecture-system/scripts/verify_visual_contract.py quiet-ui-showcase.html --tier ALL
python3 skills/visual-architecture-system/scripts/verify_visual_contract.py docs/index.html --tier ALL
```

---

## License & Commercial Output Exemption (`GNU AGPLv3` + `NOTICE`)

This repository is licensed under the **GNU Affero General Public License v3.0 ([`LICENSE`](LICENSE))** with **AGPLv3 Section 7 Additional Terms & Commercial Output Exemption ([`NOTICE`](NOTICE))**:

1. **Unconditional Commercial UI Output Exemption:** Any HTML, CSS, web applications, dashboards, slide decks, or documents generated *using* `quiet-ui-skills`—including embedding [`tokens/quiet-ui-tokens.css`](tokens/quiet-ui-tokens.css) (which is dual-licensed under the **MIT License** for runtime embedding) into proprietary or commercial software—belong 100% to you and may be distributed or sold commercially without restriction.
2. **No Standalone Skill Repackaging or Paid Skill Marketplaces:** You may not repackage, rebrand, or sell `quiet-ui-skills` itself (`SKILL.md`, `references/`, `verify_visual_contract.py`, or `quiet-ui-showcase.html`) as a paid standalone agent skill or prompt pack.
3. **Mandatory Upstream Link & Fork Attribution (`AGPLv3 §7(b)–(c) & §5(a)`):** Any modified version or redistribution of the skill must retain [`NOTICE`](NOTICE), clearly date all modifications, and link back to the canonical upstream repository (`https://github.com/FrankXLT/quiet-ui-skills`).
