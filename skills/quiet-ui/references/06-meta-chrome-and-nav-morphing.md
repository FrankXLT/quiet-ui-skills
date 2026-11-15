# Reference 06: Universal Responsive Stage Portal, Navigation Topologies (`N0–N4`) & Responsive Drawers

Quiet UI pairs a universal viewport simulation portal (`<iframe id="va-stage-portal">`) with deterministic navigation topologies, a single-row 44px outer studio bar, borderless navigation affordances, and responsive `<dialog closedby="any">` drawers.

---

## 1. Stage Portal & Studio Bar Architecture

### 1.1 Universal Responsive Stage Portal (`<iframe id="va-stage-portal">`)
The Stage Portal isolates and previews any tier under calibrated physical hardware envelopes without resizing the parent browser window:
- **Calibrated Physical Hardware Presets:**
  - `Fill`: Unconstrained 100% parent container width and height.
  - `390×844`: Modern handheld phone portrait envelope (390×844 CSS px).
  - `820×1180`: Tablet, foldable, and split-screen operational envelope (820×1180 CSS px).
  - `1080p` (`1920×1080`): Standard high-definition display and wall kiosk.
  - `1440p` (`2560×1440`): QHD operator workstation.
  - `4K` (`3840×2160`): Ultra-high-resolution mission operations canvas.
- **Continuous Drag Resizing & Auto-Fit:**
  - Right-edge and bottom-corner drag handles enable continuous interactive width/height stress-testing.
  - `Auto-Fit / 1:1` toggle scales the iframe smoothly via CSS `transform: scale(...)` to fit available screen space without clipping, or renders at exact 1:1 pixel fidelity.

### 1.2 Single-Row 44px Outer Studio Bar (`#va-studio-bar`)
The outer studio bar provides persistent session control in a single `44px` row without vertical multi-row stack bloat:
- **Left Section (Mode Toggle):**
  - Segmented `[UI | Atlas]` pill toggle switching between the 16 interactive UI tiers and the 45-Type Diagram Atlas.
  - Conditional badge (`45`) displayed when Atlas mode is active.
- **Center Section (Tier & View Stepper):**
  - Left chevron `[‹]` button.
  - Native `<select id="va-tier-select">` dropdown with all 16 canonical UI tiers (or 7 Atlas family jump anchors).
  - Right chevron `[›]` button.
- **Right Section (Viewport-Adaptive Fast Actions):**
  - **Narrow Viewports (`< 700px`):** `[◐]` quick theme cycle button + `[⚙]` settings sheet trigger with a `6px` configuration indicator dot.
  - **Medium Viewports (`700px–1099px`):** 4 Theme Dots (`white`, `paper`, `dark-paper`, `dark`) + `Nav` dropdown + `[⚙]` settings trigger.
  - **Wide Desktop (`>= 1100px`):** 4 Theme Dots + `Nav` dropdown + `Stage` preset pills (`Fill`, `390`, `820`, `1080p`, `1440p`, `4K`, `1:1`) + `[⚙]` settings trigger.
- **Mobile Auto-Tuck Ergonomics:** On handheld screens (`< 700px`), the studio bar automatically tucks away (`transform: translateY(-100%)`) on scroll down and smoothly restores on scroll up or hover.

---

## 2. Deterministic Navigation Topologies (`N0–N4`)

### 2.1 Per-Tier Navigation Compatibility Matrix
Every archetype defines compatible navigation shells. Incompatible combinations automatically fall back to the tier's default:

| Navigation Shell | Archetype Compatibility Matrix | Primary Characteristics |
| :--- | :--- | :--- |
| **`N0 · Zero-Chrome Kiosk`** | `02. Doc-2`, `03. Doc-3`, `06. Bridge-1`, `15. HUD-1` | Zero chrome (`0px`). Viewport owns full canvas. Maximum immersion. |
| **`N1 · Full-Height Left Rail`** | `01. Doc-1`, `05. Doc-4A`, `07. Deck-1`, `09. App-2`, `10. App-1`, `11. App-4`, `13. App-5`, `14. App-Tree`, `16. Ctrl-1` | `220px–260px` sidebar with `.va-hamburger-btn` collapsing to `60px` icon rail. |
| **`N2 · Single Top Command Bar`** | `08. Bridge-2`, `12. App-3` | `42px` borderless horizontal tabs (`.va-tab-link`). |
| **`N3 · Hybrid L-Shell`** | `04. Doc-4B` | Single top bar + left symbol tree. Strictly `<= 1` top and left bar. |
| **`N4 · Bottom Thumb Dock`** | Handheld viewports (`< 700px`) ONLY | `52px` 5-slot bottom thumb bar. Prohibited on desktop viewports. |

### 2.2 The Single-Bar Invariant
At most **one top command bar**, **one left rail**, and **one bottom dock** may be active simultaneously. Stacking multiple top navigation bars or combining duplicate left rails is strictly prohibited.

### 2.3 Active Navigation Indicator Architecture
Active navigation pills, sidebar links, and object tree nodes enforce a straight vertical indicator pseudo-element rather than curved or rounded borders:
```css
.va-side-link.is-active::before,
.va-tab-link.is-active::before {
  content: "";
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 3px;
  border-radius: 99px;
  background: var(--accent-focal);
}
```

---

## 3. Responsive Drawer Behavior & `<dialog>` Overlays

### 3.1 Tablet & Medium Screens (`641px–1099px`)
- Left rails auto-collapse to a compact `60px` centered icon rail.
- Clicking the `.va-hamburger-btn` expands the rail in-flow within the grid (`220px minmax(0, 1fr)`) with `0px` inline overlap and zero sliced content.

### 3.2 Mobile Screens (`<= 640px`)
- Sidebars open via lightweight `<dialog closedby="any">` overlay drawers (`position: fixed; top: 44px; width: 240px; z-index: 600`) with theme backdrop scrim.
- Primary navigation routes transfer to the bottom thumb dock (`N4`).
- Main scroll container applies `padding-bottom: max(64px, env(safe-area-inset-bottom, 20px))` to prevent bottom dock obstruction.

---

## 4. Implementation Code Patterns & Token Bindings

### 4.1 Studio Bar Single-Row Layout
```css
#va-studio-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 1rem;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-hairline);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

#va-studio-bar.is-tucked {
  transform: translateY(-100%);
}
```

### 4.2 Labeled Settings Sheet Dialog (`#va-studio-sheet`)
```html
<dialog id="va-studio-sheet" class="va-settings-sheet" aria-labelledby="sheet-title" closedby="any">
  <div class="sheet-header">
    <h3 id="sheet-title">Showcase Studio Settings</h3>
    <button type="button" class="va-pill-btn" onclick="closeStudioSheet()">Close</button>
  </div>
  <div class="sheet-body">
    <div class="sheet-row">
      <label for="sheet-theme-select">Surface Theme</label>
      <select id="sheet-theme-select">
        <option value="white">Pure White (Default)</option>
        <option value="paper">Warm Editorial Paper</option>
        <option value="dark-paper">Dark Technical Paper</option>
        <option value="dark">Deep Space Optical Dark</option>
      </select>
    </div>
    <div class="sheet-row">
      <label for="sheet-density-select">Interface Density</label>
      <select id="sheet-density-select">
        <option value="compact">Compact (High Density)</option>
        <option value="balanced" selected>Balanced (Standard)</option>
        <option value="comfortable">Comfortable</option>
      </select>
    </div>
    <div class="sheet-row">
      <label for="sheet-corners-select">Corner Geometry</label>
      <select id="sheet-corners-select">
        <option value="auto" selected>Concentric Auto</option>
        <option value="sharp">Technical Sharp (0px)</option>
      </select>
    </div>
  </div>
</dialog>
```

### 4.3 Mobile Bottom Thumb Dock (N4) Architecture
```css
.va-bottom-dock {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 52px;
  background: var(--bg-surface);
  border-top: 1px solid var(--border-hairline);
  z-index: 500;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

@media (max-width: 640px) {
  .va-bottom-dock {
    display: flex;
  }
}

.dock-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-family: var(--font-sans);
  font-size: 10px;
  color: var(--text-secondary);
  text-decoration: none;
}

.dock-slot.is-active {
  color: var(--accent-focal);
  font-weight: 600;
}
```

---

## 5. Verification & Audit Checklist for Meta Chrome & Navigation
- [ ] Studio bar maintains exact `44px` single-row height across all screen resolutions.
- [ ] Studio bar fast actions adapt responsively (`< 700px`, `700–1099px`, `>= 1100px`).
- [ ] Settings sheet opens cleanly via `<dialog id="va-studio-sheet">` with full keyboard escape support.
- [ ] Desktop default navigation (`>= 700px`) is strictly `N1` or `N2` (zero desktop `N4`).
- [ ] Mobile viewports (`<= 640px`) render `N4` bottom dock with safe bottom clearance.
- [ ] Active navigation indicators use straight vertical pseudo-elements with zero curved borders.
