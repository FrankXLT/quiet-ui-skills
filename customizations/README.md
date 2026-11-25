# Quiet UI Customizations Architecture (v9.2)

> **Customize in 60 Seconds (Show Inspiration Examples)**  
> Transform Quiet UI into your own bespoke design system in under a minute by providing 1–3 inspirational examples (screenshots, URLs, brand guides) or brand hexes.

---

## 1. Quick Start: Customize in 60 Seconds

Provide an AI agent (or paste into your assistant) this prompt:

```text
I want to customize Quiet UI for [personal / brand] use in customizations/<my-project>/.
Here are 1–3 inspirational design references:
- Reference 1: [URL, screenshot, or description]
- Reference 2: [URL, screenshot, or description]
Brand Hexes / Fonts:
- Primary Accent: #...
- Secondary / Focal: #...
- Surface / Canvas: #FFFFFF / #F8FAFC
- Typography: [Sans font] / [Serif font] / [Mono font]

Please clone the starter, extract design tokens into customization.json, update intent/ blueprints and styles/overrides.css, and compile/verify the showcase.
```

---

## 2. Choosing a Starter Blueprint

| Blueprint | Scope | Coverage | Optical Backplates | Best For |
| :--- | :--- | :---: | :---: | :--- |
| **`personal-starter`** | Personal & Spatial Workspaces | 22 Views | 8 CC0 / PD Photos | Personal research, clinical/grid consoles, optical HUDs, and smart-home decks. |
| **`brand-starter`** | Team & Product Portal | 18 Views | Omitted | Enterprise software products, SaaS platforms, B2B dashboards, and technical documentation hubs. |

> [!NOTE]
> `brand-starter` omits optical HUD overlays and residential smart-home views, keeping enterprise software and engineering deployments focused across 18 views.

---

## 3. Directory Layout

```text
customizations/
├── README.md                          # This architecture guide
├── LICENSE                            # Standalone MIT License (0 NOTICE obligations)
├── personal-starter/                  # Read-only 22-view blueprint
│   ├── customization.json             # Manifest (mode: personal, all 22 views)
│   ├── intent/                        # Architectural design rationale
│   │   ├── 00-global-structure.md     # Layout, chrome & 7-step typography
│   │   ├── 01-docs-and-specs.md       # Editorial & regulatory spec rationale
│   │   ├── 02-workspaces-apps.md      # Workspaces, SCADA & telemetry rationale
│   │   └── 03-spatial-ambient.md      # Optical HUD & tactile console rationale
│   ├── styles/
│   │   ├── quiet-ui-tokens.css        # MIT base design tokens
│   │   └── overrides.css              # Custom :root variables & CSS rules
│   └── showcase.html                  # Pre-compiled 26-view preview
├── brand-starter/                     # Read-only 22-view product blueprint
│   └── ...                            # Same anatomy with 22 product views
└── scripts/                           # Build & verification toolchain
    ├── build_showcase.py              # Compiles showcase from customization.json
    └── verify_customization.py        # Validates WCAG contrast & geometric gates
```

---

## 4. Manual Customization Workflow

If you prefer building without an agent:

1. **Clone Starter:**
   ```bash
   cp -r customizations/brand-starter customizations/my-brand
   ```
2. **Edit Manifest:** Update `customizations/my-brand/customization.json` with your title, palette hexes, and font choices.
3. **Compile Showcase:**
   ```bash
   python3 customizations/scripts/build_showcase.py customizations/my-brand
   ```
4. **Verify Design Contract:**
   ```bash
   python3 customizations/scripts/verify_customization.py customizations/my-brand --check-immutability
   ```

---

## 5. Licensing & Immutability Rules

- **Pure MIT License:** All files in `customizations/` and all output HTML/CSS/JS are licensed under MIT (`customizations/LICENSE`). You own your designs 100% with zero `NOTICE` requirements on shipped products.
- **Starter Immutability Lock:** AI agents and automated scripts are strictly prohibited from mutating `personal-starter/`, `brand-starter/`, `skills/quiet-ui/`, `skills/quiet-evidence/`, or `skills/quiet-bridge/`. All user modifications must reside in dedicated subfolders (`customizations/<name>/`). Both `quiet-ui` (responsive delivery mediums) and `quiet-evidence` (calibrated SVG compilers) automatically read `customizations/<name>/customization.json` for brand palette and typography cohesion.
