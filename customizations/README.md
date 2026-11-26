# Quiet UI Customizations Architecture (v9.8)

> **Customize in 60 Seconds:** Turn Quiet UI into your own branded showcase—or launch a 3-route OAW project website—from one MIT-licensed starter folder with zero runtime build dependencies.

---

## 1. Choosing a Starter Blueprint

| Blueprint | Scope | Coverage | Best For |
| :--- | :--- | :--- | :--- |
| **[`personal-starter/`](personal-starter/customization.json)** | Personal & Spatial Workspaces | **26 Views** (All 6 domains, 8 CC0/PD photos) | Personal research, clinical/grid consoles, optical HUDs, and smart-home energy decks. |
| **[`brand-starter/`](brand-starter/customization.json)** | Team & Product Portal | **22 Views** (Domains `01–05`, omits HUD/home) | Enterprise software products, SaaS platforms, B2B dashboards, and engineering hubs. |
| **[`project-site-starter/`](project-site-starter/README.md)** | Reusable 3-Route OAW Site | **Overview + Docs + optional Demo** (`oaw-site.json`) | Open-source repositories needing a landing page, searchable Markdown docs, and `1280x640` social cards. |

---

## 2. Directory Layout

```text
customizations/
├── README.md                          # This architecture & workflow guide
├── LICENSE                            # Standalone MIT License (zero NOTICE obligations)
├── personal-starter/                  # Read-only 26-view personal/spatial blueprint
│   ├── customization.json             # Manifest (mode: personal, 26 views)
│   ├── intent/                        # 00..03 architectural rationale docs
│   ├── styles/                        # quiet-ui-tokens.css + overrides.css
│   └── showcase.html                  # Pre-compiled 26-view preview
├── brand-starter/                     # Read-only 22-view product blueprint (Domains 01–05)
│   └── ...                            # Same anatomy with 22 product views
├── project-site-starter/              # Read-only 3-route OAW project-site shell template
│   ├── README.md                      # 60-second setup & flag reference
│   ├── oaw-site.json                  # Manifest: project info, hub links, routes, docs, social card
│   ├── docs/                          # Markdown guides with optional quiet-evidence diagram fences
│   └── styles/overrides.css           # @layer tokens overrides for accents & typography
└── scripts/
    ├── build_showcase.py              # Compiles showcase.html from customization.json
    ├── verify_customization.py        # Validates WCAG contrast & immutability gates
    └── build_project_site.py          # Compiles Overview, Docs, optional Demo & 1280x640 cards
```

---

## 3. Customize with an AI Agent (60 Seconds)

Paste this prompt into your AI coding assistant alongside 1–3 reference screenshots or brand hexes:

```text
I want to customize Quiet UI for [personal / brand / project-site] use in customizations/<my-project>/.
Here are 1–3 visual references:
- Reference 1: [URL, screenshot, or description]
Brand Hexes / Fonts:
- --accent-primary: #1D4ED8 | --accent-focal: #0F766E | --text-on-accent: #FFFFFF
- --font-sans / --font-serif / --font-mono: [Fonts]

Please copy the matching starter, update the manifest and @layer tokens overrides, and compile and verify the output.
```

---

## 4. Manual Workflows

### A. Branded or Personal Showcase (`brand-starter/` or `personal-starter/`)

1. **Clone a starter:**
   ```bash
   cp -r customizations/brand-starter customizations/my-brand
   ```
2. **Edit manifest & tokens:** Update `customizations/my-brand/customization.json` and `customizations/my-brand/styles/overrides.css` inside `@layer tokens` (zero `!important`).
3. **Compile & verify with [`build_showcase.py`](scripts/build_showcase.py) and [`verify_customization.py`](scripts/verify_customization.py):**
   ```bash
   python3 -B customizations/scripts/build_showcase.py customizations/my-brand
   python3 -B customizations/scripts/verify_customization.py customizations/my-brand --check-immutability
   ```

### B. Reusable 3-Route OAW Project Site (`project-site-starter/`)

1. **Clone the site shell template:**
   ```bash
   cp -r customizations/project-site-starter customizations/my-site
   ```
2. **Edit manifest, guides & overrides:** Configure [`oaw-site.json`](project-site-starter/oaw-site.json), author Markdown guides in `docs/*.md` (optionally embedding fenced `quiet-evidence` JSON diagrams), and set `--accent-primary`, `--accent-focal`, `--text-on-accent`, and `--font-sans` in `styles/overrides.css`.
3. **Build static site & `1280x640` social card via [`build_project_site.py`](scripts/build_project_site.py):**
   ```bash
   python3 -B customizations/scripts/build_project_site.py \
     --config customizations/my-site/oaw-site.json \
     --out dist/my-site \
     --social-svg --social-png
   ```
   Pass `--bundle` to inline `quiet-ui-tokens.css` and `styles/overrides.css` directly into generated HTML pages.
4. **Verify static drift & WCAG contrast via [`audit_quiet_html.py`](../skills/quiet-ui/scripts/audit_quiet_html.py):**
   ```bash
   python3 -B skills/quiet-ui/scripts/audit_quiet_html.py dist/my-site --strict-drift
   ```

See [`project-site-starter/README.md`](project-site-starter/README.md) for full `oaw-site.json` fields, search-index behavior, and `--cdp` verification commands.

---

## 5. Licensing & Immutability Rules

- **Pure MIT License ([`LICENSE`](LICENSE)):** Everything in `customizations/` and 100% of generated HTML, CSS, JS, SVG, and PNG output is MIT-licensed with **zero `NOTICE` or attribution obligations** on shipped sites or apps.
- **Starter Immutability Lock:** Never mutate `personal-starter/`, `brand-starter/`, `project-site-starter/`, `skills/quiet-ui/`, `skills/quiet-evidence/`, or `skills/quiet-bridge/`. Always work inside dedicated subfolders (`customizations/<name>/`) or separate site directories.
