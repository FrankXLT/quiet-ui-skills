# 60-Second Brand Customization

You do not need to edit core skill files or hand-tune twenty separate stylesheets to match your product palette. Quiet UI drives both interface shells and compiled charts from a single manifest so your brand stays consistent everywhere.

## One Manifest for Shells and Charts

Every customization lives in its own folder under `customizations/<my-brand>/` with a `customization.json` manifest and a `styles/overrides.css` file:

- **UI shells read your tokens** for page canvases, card surfaces, text ink, buttons, corner radius, and density.
- **Compiled SVG and ECharts figures read the same palette** so axis highlights, focal series, and status badges match the surrounding page automatically across all four surface themes (`white`, `paper`, `dark-paper`, and `dark`).

> [!IMPORTANT]
> Treat `skills/`, `tokens/`, `customizations/brand-starter/`, and `customizations/personal-starter/` as read-only blueprints. Always copy a starter into a new folder such as `customizations/acme-app/` before editing.

## Choosing the Right Starter

Quiet UI ships three MIT-licensed starters depending on what you are building:

| Starter | Scope | Included Surfaces | Best For |
| :--- | :--- | :--- | :--- |
| **`brand-starter`** | **22 views** (Domains 01–05) | Editorial briefs, RFCs, dashboards, data grids, and tree explorers; omits optical HUDs and residential smart-home views | SaaS products, engineering platforms, B2B dashboards, and internal tools |
| **`personal-starter`** | **26 views** (All 6 domains) | Full showcase range including 8 CC0/PD photo backplates, optical HUD pods, and home energy consoles | Personal research workbenches, ambient wall displays, and spatial prototypes |
| **`project-site-starter`** | **3-route public site** (`oaw-site.json`) | `Overview` landing page, optional `Demo` wrapper, and searchable `Docs` Markdown reader | Open-source repositories, SDK documentation portals, and static project sites |

## Option A: Customize with an AI Coding Agent

Paste this prompt into your AI assistant along with 1–3 visual references or brand hex codes:

```text
I want to customize Quiet UI for [personal / brand] use in customizations/<my-brand>/.
Here are 1-3 inspirational design references:
- Reference 1: [URL, screenshot, or description]
- Reference 2: [URL, screenshot, or description]
Brand Hexes / Fonts:
- Primary Accent: #1D4ED8
- Focal Accent: #0F766E
- Surface / Canvas: #FFFFFF / #F8FAFC
- Typography: Inter / Newsreader / JetBrains Mono

Please clone the matching starter, update customization.json and styles/overrides.css, and compile and verify the showcase.
```

## Option B: Manual CLI Workflow

To customize a product or workspace showcase directly from the terminal:

1. **Clone a starter into your own folder:**

```bash
cp -r customizations/brand-starter customizations/my-brand
```

2. **Edit `customizations/my-brand/customization.json`:** Update `name`, `title`, `palette` hexes, `fonts`, `corner_geometry` (`auto`, `sharp`, `subtle`, `rounded`, `soft`), and `density`.

3. **Override tokens cleanly in CSS:** Wrap palette and typography changes inside `@layer tokens` inside `customizations/my-brand/styles/overrides.css` so they sit neatly in the cascade (`@layer reset, tokens, shell, archetypes, evidence, views, utilities;`) with zero `!important` rules:

```css
@layer tokens {
  :root {
    --accent-primary: #1D4ED8;
    --accent-focal: #0F766E;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
  }

  :root[data-theme="white"] {
    --bg-canvas: #F8FAFC;
    --bg-surface: #FFFFFF;
    --text-primary: #0F172A;
    --text-secondary: #334155;
  }

  :root:is([data-theme="dark"], [data-theme="dark-paper"]) {
    --accent-primary: #60A5FA;
    --accent-focal: #2DD4BF;
    --bg-canvas: #090D16;
    --bg-surface: #0F1624;
    --text-primary: #F1F5F9;
    --text-secondary: #CBD5E1;
  }
}
```

4. **Compile and verify your customized showcase:**

```bash
python3 -B customizations/scripts/build_showcase.py customizations/my-brand
python3 -B customizations/scripts/verify_customization.py customizations/my-brand --check-immutability
```

The verifier checks WCAG text-to-surface contrast ratios (`>= 4.5:1`), confirms zero `!important` overrides, and verifies that none of the read-only starter or skill directories were modified.

## Building a 3-Route Public Project Site

If you want a clean project website (`Overview`, `Docs`, and an optional `Demo` tab) rather than a showcase explorer, start from `customizations/project-site-starter/`:

```bash
cp -r customizations/project-site-starter site
```

Update `site/oaw-site.json` with your project metadata, Markdown guide list (`docs_reader.sources`), and install commands, then compile the static site:

```bash
python3 -B customizations/scripts/build_project_site.py --config site/oaw-site.json --out dist/
```

Every output file in `dist/` is static HTML, CSS, and SVG ready for GitHub Pages or any static web server. Read [Workflows & Reusable Project-Site Shell](./05-workflows-and-project-site.md) for full `oaw-site.json` schema details.
