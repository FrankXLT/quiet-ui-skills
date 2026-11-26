# Getting Started with the OAW Project Site Shell

The OAW Project Site Shell gives an open-source repository a clean, fast documentation and showcase website with zero runtime build dependencies. You write plain Markdown guides, describe your project in `oaw-site.json`, and compile static HTML ready for GitHub Pages or any static host.

## 1. Copy the Starter into Your Repository

Copy `customizations/project-site-starter` into your project repository (for example, into a `site/` folder) so your team owns every configuration file, guide, and stylesheet directly.

```text
site/
├── oaw-site.json           # Site metadata, routes, hub links, and doc list
├── docs/
│   ├── getting-started.md  # Maintainer onboarding guide
│   └── architecture.md     # Three-route layout and pipeline diagram
└── styles/
    └── overrides.css       # Optional brand palette and font overrides
```

## 2. Configure `oaw-site.json`

Open `oaw-site.json` and update the project title, tagline, repository URL, and documentation list. Every path in the manifest must stay relative to the folder containing `oaw-site.json`.

| Section | Purpose | Key Fields |
| :--- | :--- | :--- |
| `project` | Core identity and links | `slug`, `title`, `tagline`, `version`, `repo_url`, `site_url` |
| `hub` | Sibling-project switcher menu | `label`, `hub_url`, `projects` (`title`, `url`, `current`) |
| `routes` | Labels and paths for the three routes | `overview`, `demo` (`enabled`), `docs` |
| `overview` | Hero copy, install steps, and previews | `kicker`, `headline`, `summary`, `primary_cta`, `install_commands` |
| `docs_reader` | Guides shown in the `/docs/` reader | `title`, `subtitle`, `sources` (`path`, `id`, `title`), `quick_jumps` |
| `demo_wrapper` | Optional interactive app at `/demo/` | `enabled`, `entry_path`, `docs_base`, `topbar_links` |
| `social_preview` | Open Graph card metadata | `image_path`, `eyebrow`, `title`, `subtitle`, `accent_hex` |

## 3. Add Markdown Guides

Place new `.md` files inside `docs/` and register each one in `docs_reader.sources` inside `oaw-site.json`:

```json
{
  "docs_reader": {
    "title": "Project Guides",
    "sources": [
      { "path": "docs/getting-started.md", "id": "getting-started", "title": "Getting Started" },
      { "path": "docs/architecture.md", "id": "architecture", "title": "Architecture" }
    ]
  }
}
```

You can use standard GitHub-style headings, tables, `[!NOTE]` / `[!TIP]` callouts, and inline `quiet-evidence` diagram blocks inside any guide.

> [!TIP]
> Keep all guide links relative (such as `./architecture.md`), and avoid workstation filesystem paths or internal network addresses in `oaw-site.json`. The config validator blocks private network tokens automatically so public builds stay clean.

## 4. Override Colors and Fonts in `styles/overrides.css`

Edit `styles/overrides.css` to adapt the palette and font stack while keeping light and dark themes readable. Use the built-in Quiet UI custom properties so contrast stays consistent across every route:

```css
@layer reset, tokens, shell, archetypes, evidence, views, utilities;

@layer tokens {
  :root,
  [data-theme="white"] {
    --accent-primary: #1D4ED8;
    --accent-focal: #0F766E;
    --text-on-accent: #FFFFFF;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  }

  [data-theme="paper"] {
    --accent-primary: #1E40AF;
    --accent-focal: #115E59;
    --text-on-accent: #FFFFFF;
  }

  :is([data-theme="dark"], [data-theme="dark-paper"]) {
    --accent-primary: #60A5FA;
    --accent-focal: #2DD4BF;
    --text-on-accent: #0F172A;
  }
}
```

## 5. Build the Static Site

Run `build_project_site.py` against your site directory to validate `oaw-site.json`, compile your Markdown guides and diagrams, and generate the output bundle:

```bash
python3 -B customizations/scripts/build_project_site.py --config oaw-site.json --out dist/
```

Once the build completes, open `dist/index.html` locally or publish `dist/` to static hosting. To understand how the three generated routes fit together, read the [architecture guide](./architecture.md).
