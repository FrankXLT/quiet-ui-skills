# Quiet UI Customizations Architecture (v6.2)

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

| Blueprint | Scope | Tiers | Monet Art | Best For |
| :--- | :--- | :---: | :---: | :--- |
| **`personal-starter`** | Personal & Spatial Living | 17 Tiers | Included | Personal workspaces, wellness trackers, Home Assistant wall kiosks, and mobile companions. |
| **`brand-starter`** | Team & Product Portal | 13 Tiers | Omitted | Enterprise software, SaaS platforms, B2B dashboards, and technical documentation hubs. |

> [!NOTE]
> `brand-starter` disables residential smart-home tiers (`HA-1`..`HA-3`) and wellness planning (`App-5`), reducing showcase bundle size by over 65% for lean corporate deployment.

---

## 3. Directory Layout

```text
customizations/
├── README.md                          # This architecture guide
├── LICENSE                            # Standalone MIT License (0 NOTICE obligations)
├── personal-starter/                  # Read-only 17-tier blueprint
│   ├── customization.json             # Manifest (mode: personal, all 17 tiers)
│   ├── intent/                        # Architectural design rationale
│   │   ├── 00-global-structure.md     # Layout, chrome & 7-step typography
│   │   ├── 01-docs-and-specs.md       # Editorial & spec tiers (01..06)
│   │   ├── 02-workspaces-apps.md      # Workspaces & telemetry tiers (07..14)
│   │   └── 03-spatial-ambient.md      # Wall kiosk & mobile companion (15..17)
│   ├── styles/
│   │   ├── quiet-ui-tokens.css        # MIT base design tokens
│   │   └── overrides.css              # Custom :root variables & CSS rules
│   └── showcase.html                  # Pre-compiled 17-tier preview
├── brand-starter/                     # Read-only 13-tier product blueprint
│   └── ...                            # Same anatomy with 13 product tiers
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
- **Starter Immutability Lock:** AI agents and automated scripts are strictly prohibited from mutating `personal-starter/`, `brand-starter/`, `skills/quiet-ui/`, or `skills/quiet-ui-diagrams/`. All user modifications must reside in dedicated subfolders (`customizations/<name>/`). Both `quiet-ui` (17-tier UI shells) and `quiet-ui-diagrams` (45-type SVG diagrams & charts) automatically read `customizations/<name>/customization.json` for brand palette and typography cohesion.
