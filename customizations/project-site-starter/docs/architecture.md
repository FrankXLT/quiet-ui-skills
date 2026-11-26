# Project Site Shell Architecture

The OAW Project Site Shell separates marketing overview, live interactive demos, and long-form documentation into three focused routes. Splitting these jobs keeps the landing page calm, gives interactive tools full viewport room, and turns Markdown guides into a fast, searchable reader.

## Three-Route Layout

| Route | Purpose | Key Chrome & Behavior |
| :--- | :--- | :--- |
| `/` (Overview) | Introduce the project in plain language | Sticky topbar, hero summary, copyable install commands, domain previews, and architecture visuals |
| `/demo/` (Interactive Demo) | Host an existing HTML app or studio | Slim 32 px return bar above the app entry (`demo_wrapper.entry_path`) with quick links back to Overview and Docs |
| `/docs/` (Searchable Reader) | Read and search technical guides | Sticky left navigation rail on desktop, responsive table-of-contents sheet on mobile, instant search, and compiled diagrams |

### `/` Overview

The root route (`index.html`) answers three questions in seconds: what the tool does, how to install it, and where to try or read more. Content comes from the `overview` section of `oaw-site.json`, paired with optional social preview metadata (`social_preview`) for clean link cards.

### `/demo/` Interactive Demo

When `demo_wrapper.enabled` is `true`, the builder wraps your standalone demo page (`demo_wrapper.entry_path`) inside `/demo/`. Instead of stacking a heavy navigation header on top of a dense workspace, the wrapper renders a slim 32 px return strip at the top so users can jump back to `/` or `/docs/` without losing canvas height.

### `/docs/` Searchable Reader

Every Markdown file listed under `docs_reader.sources` compiles into the `/docs/` reader. On wide screens, a sticky sidebar lists documents and section headings; on narrow screens, a touch-friendly drawer opens the same outline. Client-side search filters headings and passages without a backend server, and fenced `quiet-evidence` blocks compile directly into theme-aware inline SVG schematics.

## Shared Shell Chrome

All three routes share the unified design token layer and a compact `46px` top bar:

- **Two-Stage Project Switcher:** Displays your project's spelled-out name beside `OAW Projects`, with `All Projects` pinned at the top above sibling project links.
- **Top-Right Ecosystem & Color Switcher:** Pairs the 9-dot Open Agentic Workbench switcher (`Home`, `Learn`, `Projects`, `Research`) with the maintainer menu holding **Pure White**, **Warm Paper**, **Dark**, and **Dark Paper** color themes.
- **Keyboard & Touch Ergonomics:** Uses skip links, visible focus rings, and 44 px minimum touch targets on mobile viewports.

## Build Pipeline Overview

The schematic below traces how your configuration, Markdown guides, and CSS overrides compile into the three output routes:

```quiet-evidence
{
  "$schema": "urn:quiet-ui:schema:v9:schematic",
  "id": "oaw-site-shell-pipeline",
  "schematic_kind": "pipeline",
  "metadata": {
    "title": "OAW Project Site Shell Compilation Pipeline",
    "description": "Four-stage static build turning oaw-site.json, Markdown guides, and CSS overrides into Overview, Demo, and Docs routes.",
    "rigor_level": "L1",
    "audience": "Open-Source Maintainers"
  },
  "stages": ["Inputs", "Validation", "Compilation", "Output Routes"],
  "nodes": [
    {"id": "cfg", "label": "oaw-site.json", "metric": "Site Manifest", "stage": 0},
    {"id": "docs", "label": "docs/*.md", "metric": "Guides & Specs", "stage": 0},
    {"id": "css", "label": "overrides.css", "metric": "Theme Tokens", "stage": 0},
    {"id": "validate", "label": "Config Loader", "metric": "Path & Token Gate", "stage": 1, "focal": true},
    {"id": "build", "label": "build_project_site.py", "metric": "Static Builder", "stage": 2, "focal": true},
    {"id": "overview", "label": "/ Overview", "metric": "index.html", "stage": 3, "stroke": "var(--status-ok)"},
    {"id": "demo", "label": "/demo/ Wrapper", "metric": "Slim Return Bar", "stage": 3},
    {"id": "reader", "label": "/docs/ Reader", "metric": "Search & TOC", "stage": 3, "stroke": "var(--status-ok)"}
  ],
  "edges": [
    {"from": "cfg", "to": "validate"},
    {"from": "validate", "to": "build"},
    {"from": "docs", "to": "build"},
    {"from": "css", "to": "build"},
    {"from": "build", "to": "overview"},
    {"from": "build", "to": "demo"},
    {"from": "build", "to": "reader"}
  ]
}
```

Ready to set up your own copy? Follow the step-by-step instructions in the [getting-started guide](./getting-started.md).
