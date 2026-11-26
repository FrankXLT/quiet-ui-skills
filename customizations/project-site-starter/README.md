<!-- SPDX-License-Identifier: MIT -->
# OAW Project Site Starter (Quiet UI v9.8.0)

MIT-licensed static project-site template for Open Agentic Workbench (OAW) repositories. Compiles an Overview landing page, an optional `/demo/` wrapper bar, a searchable Markdown `/docs/` reader with `quiet-evidence` diagrams, and 1280x640 social preview cards with zero runtime frontend build steps.

## Starter Layout

```text
project-site-starter/
├── README.md                 # This 60-second setup guide
├── oaw-site.json             # Manifest: project info, hub links, routes, docs, social card
├── docs/
│   ├── getting-started.md    # Onboarding & configuration guide
│   └── architecture.md       # Three-route shell & inline schematic pipeline
├── site/                     # Prebuilt static preview output (HTML, CSS, assets, docs/)
└── styles/
    ├── overrides.css         # @layer tokens overrides for accents & typography
    └── quiet-ui-tokens.css   # Canonical 4-theme Quiet UI CSS custom properties
```

## 60-Second Setup

### 1. Clone `project-site-starter`

Copy the read-only starter into a dedicated folder inside `customizations/` or into a sibling OAW repository (for example, `site/`):

```bash
cp -r customizations/project-site-starter customizations/my-site
```

Always edit your cloned copy; leave `customizations/project-site-starter/` unmodified as the baseline template.

### 2. Edit `oaw-site.json`, `docs/*.md`, and `styles/overrides.css`

1. **Manifest ([`oaw-site.json`](oaw-site.json))**:
   - Update `project` (`slug`, `title`, `tagline`, `version`, `repo_url`, `site_url`).
   - Update `hub.projects` so the header switcher links cleanly across sibling OAW tools (`current: true` on your site).
   - Set `routes.demo.enabled` (`false` by default) and `demo_wrapper` if bundling an interactive HTML demo.
   - Update `overview` (`kicker`, `headline`, `summary`, CTAs, `install_commands`, `plain_language_blocks`, `architecture_diagrams`).
   - Register Markdown guides under `docs_reader.sources` and customize `social_preview` (`image_path`, `eyebrow`, `title`, `subtitle`, `pills`, `accent_hex`, `routes`).
   - Keep every asset path relative; `load_site_config()` rejects home directory prefixes, private/loopback IPv4 literals, private mDNS hostnames, and internal agent storage identifiers.

2. **Markdown Guides ([`docs/getting-started.md`](docs/getting-started.md), [`docs/architecture.md`](docs/architecture.md))**:
   - Author standard headings, tables, and GitHub-style `[!NOTE]` / `[!TIP]` callouts inside `docs/*.md`.
   - Embed fenced `quiet-evidence` blocks (`$schema: "urn:quiet-ui:schema:v9:schematic"`) to render theme-aware inline SVG diagrams.

3. **Theme & Typography Overrides ([`styles/overrides.css`](styles/overrides.css))**:
   - Customize `--accent-primary`, `--accent-focal`, `--text-on-accent`, and `--font-sans` / `--font-serif` / `--font-mono` inside `@layer tokens` across `:root, [data-theme="white"]`, `[data-theme="paper"]`, `[data-theme="dark-paper"]`, and `[data-theme="dark"]` while preserving `>= 4.5:1` contrast and zero CSS priority-escalation flags.

### 3. Build Static Site & 1280x640 Social Preview Card

Run [`build_project_site.py`](../scripts/build_project_site.py) from the `quiet-ui-skills` repository root:

```bash
# Build HTML, CSS, docs search index, and 1280x640 SVG preview (--social-svg defaults to on)
python3 -B customizations/scripts/build_project_site.py \
  --config customizations/my-site/oaw-site.json \
  --out dist/my-site \
  --social-svg

# Also render a 1280x640 PNG social preview card (requires Pillow: pip install pillow)
python3 -B customizations/scripts/build_project_site.py \
  --config customizations/my-site/oaw-site.json \
  --out dist/my-site \
  --social-svg --social-png
```

Useful optional flags:

| Flag | Behavior |
| :--- | :--- |
| `--social-svg` / `--no-social-svg` | Writes or skips the 1280x640 SVG preview next to `social_preview.image_path` (default: enabled). |
| `--social-png` | Renders the 1280x640 RGB PNG social card (`<= 250 KB`) using lazy-imported Pillow. |
| `--bundle` | Inlines `quiet-ui-tokens.css` and `styles/overrides.css` directly into generated HTML pages. |

### 4. Verify with `audit_quiet_html.py`

Run [`audit_quiet_html.py`](../../skills/quiet-ui/scripts/audit_quiet_html.py) against your stylesheet or compiled output before publishing:

```bash
# Static CSS/HTML/JS & strict token-drift audit on overrides and generated output
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py customizations/my-site/styles/overrides.css --strict-drift
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py dist/my-site --strict-drift

# Optional live Headless Chrome sweep across 390px, 820px, and 1440px (requires selenium + Chrome)
python3 -m http.server 8788 --directory dist/my-site
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py http://localhost:8788/ --cdp
```

## License

All files in `customizations/project-site-starter/` and all static output produced from your manifest are licensed under the [MIT License](../LICENSE) with zero `NOTICE` obligations.
