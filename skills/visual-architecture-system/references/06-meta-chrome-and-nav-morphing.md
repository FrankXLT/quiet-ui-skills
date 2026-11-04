# Reference 06: Clean `N0–N4` Navigation Topologies, Font Awesome 6 Taxonomy, Hamburger Rail Collapse & App Shell Essentials

Every production deliverable across the 17-Tier Continuum must follow deterministic navigation selection rules, **Font Awesome 6 (`fa-solid`) vector icon taxonomy (zero unicode emojis)**, **borderless `.va-tab-link` / `.va-side-link` nav anatomy**, **Hamburger Rail Collapse (`toggleLeftRailCollapse()`)**, and the **Single-Bar Law** (`<= 1` visible top, left, and bottom bar at any time).

---

## 1. Architectural Selection Law (`N0` vs. `N1` vs. `N2` vs. `N3` vs. `N4`) & Single-Bar Invariant

1. **`N0 · Zero-Chrome Kiosk` (`02. Doc-2`, `03. Doc-3`, `06. Bridge-1`, `15. HA-1`):**
   - **Rule:** Zero navigation bars (`0px`). Stage owns `100vw × 100dvh`.
2. **`N1 · Full-Height Left Sidebar / Spine` (`01. Doc-1`, `05. Doc-4A`, `07. Deck-1`, `09. App-2`, `10. App-1`, `11. App-4`, `13. App-5`, `14. App-Tree`, `16. HA-2`):**
   - **When to Choose:** Vertical height (`100dvh`) is the scarce resource or navigation has `> 5` items/tree nodes.
   - **Hamburger Rail Collapse (`.va-hamburger-btn`):** Every `N1` / `N3` sidebar includes `<button type="button" class="va-hamburger-btn" onclick="toggleLeftRailCollapse()"><i class="fa-solid fa-bars"></i></button>` that toggles `html.is-rail-collapsed`, smoothly collapsing the `220px–260px` sidebar into a `60px` icon-only rail (`labels hidden`, icons centered).
3. **`N2 · Pure Single Top Command Bar` (`08. Bridge-2`, `12. App-3`):**
   - **When to Choose:** Horizontal width (`100vw`) is scarce and top-level navigation has `<= 5` views.
   - **Borderless Tab Anatomy (`.va-tab-link`):** Never put boxy `.c-btn` buttons inside `<nav>` or `<header>`. Use borderless `.va-tab-link` (`height: 42px`, `border-bottom: 2px solid transparent`, `.active { border-bottom-color: var(--accent-focal); }`) with `<i class="fa-solid ..."></i>` + label.
4. **`N3 · Hybrid Enterprise L-Shell (Top + Left)` (`04. Doc-4B`):**
   - **Single-Bar & Anti-Duplication Law:** At most `1` top bar and `1` left rail may be visible simultaneously. Never show `switchTier()` tier numbers in `N3` bars, and never show two stacked top bars (e.g. hide `.ha2-top-strip` when `.va-poly-n3-topbar` is visible).
5. **`N4 · Sticky Bottom Thumb-Zone Dock` (`17. HA-3` and all `R5 · Phone 390px` views):**
   - **Rule:** `48px–52px` bottom bar with 5 thumb-reachable slots (icon stacked above `10px` label); strictly zero top navbar.

---

## 2. Font Awesome 6 (`fa-solid`) Vector Icon Taxonomy & Zero-Emoji Law

Load Font Awesome 6 CSS (`https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css`) with an offline CSS glyph fallback table so icons render cleanly both online and air-gapped. **Strictly forbid unicode emojis (`✨`, `⚡`, `☀`, `🛡`, `●`, `&#10024;`) anywhere in the HTML.**

| Domain / Function | Standard `fa-solid` Icon Classes |
| :--- | :--- |
| **Navigation & Shell** | `fa-bars` (Hamburger collapse), `fa-magnifying-glass` (Search), `fa-user-astronaut` (Profile), `fa-Sliders` |
| **Editorial & Mermaid** | `fa-book-open`, `fa-scroll`, `fa-scale-balanced`, `fa-code`, `fa-terminal`, `fa-diagram-project`, `fa-file-pdf` |
| **Workspaces (`App-1..5`)** | `fa-layer-group`, `fa-bolt` (Active/Focus), `fa-clock`, `fa-calendar-week`, `fa-wand-magic-sparkles`, `fa-heart-pulse`, `fa-leaf` |
| **Tree & Schema (`App-Tree`)** | `fa-database`, `fa-table`, `fa-key` (PK), `fa-link` (FK), `fa-folder-open`, `fa-file-code`, `fa-chevron-right` |
| **Home Assistant (`HA-1..3`)** | `fa-lightbulb`, `fa-temperature-half`, `fa-shield-halved`, `fa-video`, `fa-couch`, `fa-utensils`, `fa-bed`, `fa-warehouse` |

---

## 3. Editorial Purity & Zero Debug Header Law

1. **Zero SaaS Account Pod in Editorial Tiers (`01. Doc-1`–`06. Bridge-1`):** Documentation, RFCs, API references, and worksheets must NEVER render `.va-account-pod` (`AR · Author`) or account popovers. Replace right-hand masthead slots with document-native utilities (`[/] Search Corpus` + `.va-pill-btn` `PDF`).
2. **Zero Internal Debug Strings in Headers:** Never render `11. APP-4 //`, `(N2 MASTHEAD)`, or `(85% BOX WEIGHT)` in visible `<header>`, `<nav>`, `<aside>`, or `<h1>` elements. Tier numbers belong exclusively inside the Layer 0 `#va-floating-dock` / `#va-display-popover`.

---

## 4. The 3-Tier Summary Bar Law, Account Menu & 3-Channel Notifications (Workspaces `07`–`17`)

1. **3-Tier Summary Bar Law:** Tier 1 Inline Summary Bar (`<= 36px` `.va-pulse-strip`), Tier 2 On-Demand Summary Drawer (`.va-pulse-drawer`), Tier 3 Dedicated `Insights` Route (`12. App-3`).
2. **Standardized Account Menu (`#va-account-pod` + `.va-account-popover`):** Pinned to bottom-left of `N1` sidebars and top-right of `N2`/`N3` bars in application tiers (`07`–`17`).
3. **3-Channel Notification Discipline:** Monochrome `Inbox · 4` pill (`.va-inbox-pill`), `6px` sync heartbeat dot (`.va-sync-dot`), and dismissible `32px` `.va-tripwire-banner`.

---

## 5. 3-Breakpoint Responsive Nav Morphing & 408-Permutation Invariants (`17 Mediums × 3 Screens × 8 Nav States`)

1. **Unified Effective-Nav Selectors (`:root[data-effective-nav="..."]`):**
   - Bind 100% of polymorphic navbar visibility and grid track rules to `:root[data-effective-nav="n0..n4"]` rather than `:root[data-nav-shell]` so `Auto` and explicit `N0–N4` share identical layout geometry (`0` duplicate headers on `Bridge-2` / `App-2`, preserved `.deck1-hdr` masthead on `Deck-1`).
2. **Desktop (`@media (min-width: 1100px)`):**
   - Scope all multi-column desktop grid tracks (`220px minmax(0, 1fr) 330px`, `html.is-rail-collapsed` `60px` rail tracks, and `N4` single-column/centered resets) strictly inside `@media (min-width: 1100px)` so desktop multi-column tracks never leak into tablet or phone viewports.
3. **Tablet / Unfolded Foldable (`@media (min-width: 641px) and (max-width: 1099px)`):**
   - **Closed `60px` Icon Rail (`N1` / `N3`):** Auto-collapse left sidebars to `60px` (`grid-template-columns: 60px minmax(0, 1fr)`), centering icons, `.va-account-pod` (`44px`), and styling `.va-side-link.active` as a centered `44px × 36px` rounded icon pill (`border-left: none; border-radius: var(--radius-inner, 6px); margin: 0 auto`).
   - **In-Flow `220px` Grid Expansion (`html.is-drawer-open`, Zero Overlap):** At `641px–1099px`, clicking `.va-hamburger-btn` MUST expand the left sidebar **in-flow inside the CSS Grid** (`position: sticky; top: 0; width: 220px; grid-template-columns: 220px minmax(0, 1fr)`), pushing the main content column cleanly to `x >= 220px` (`mainRect.left >= railRect.right - 2`, **strictly zero horizontal overlap or sliced prose/headings**). Never use a fixed overlay drawer at `641px–1099px`.
   - **Nav-Switch & Tier-Switch State-Reset Law:** Every call to `setNavShell()`, `cycleNavShell()`, or `switchTier()` (and `syncEffectiveNav()` whenever `eff !== 'n1' && eff !== 'n3'`) MUST execute `document.documentElement.classList.remove('is-drawer-open', 'is-rail-collapsed')`, and all `html.is-drawer-open` CSS rules MUST be qualified with `:root:not([data-effective-nav="n0"]):not([data-effective-nav="n2"]):not([data-effective-nav="n4"])` so an expanded sidebar can never bleed into `N0`, `N2`, or `N4`.
   - **Full-Width `N0` / `N2` / `N4`:** Force `grid-template-columns: minmax(0, 1fr) !important` and stack right-hand inspector/code panes full-width below (`grid-column: 1 / -1`) with `0px` empty right-hand holes.
4. **Phone (`@media (max-width: 640px)`):**
   - **`Auto` & `N4`:** Resolve `Auto` to `N4` (`52px` fixed 5-slot bottom thumb bar, `0` top/left bars).
   - **`N2`:** Single-row `42px` horizontally scrollable top bar (`flex-wrap: nowrap; overflow-x: auto; max-width: 100vw`) with `0px` horizontal page overflow.
   - **`N1` & `N3`:** Compact `42px` single-row top bar with `.va-hamburger-btn` (`hamCount = 1`) that toggles the **`240px` fixed overlay drawer** (`position: fixed; top: 42px; width: 240px; z-index: 600` — scoped strictly to `@media (max-width: 640px)`), while main content spans `100%` of the phone viewport.
   - **Zero `@container` vs. `@media` Collisions:** Never attach `container-type: inline-size` to `.va-viewport-stage`; drive all responsive reflows via `@media` breakpoints.

