# Project Site Shell Architecture

The OAW Project Site Shell separates marketing overview, live interactive demos, and long-form documentation into three focused routes. Splitting these jobs keeps the landing page calm, gives interactive tools full viewport room, and turns Markdown guides into a fast, searchable reader.

## Three-Route Layout

| Route | Purpose | Key Chrome & Behavior |
| :--- | :--- | :--- |
| `/` (Overview) | Introduce the project in plain language | Unified `46px` OAW topbar, hero summary, copyable install commands, domain previews, and architecture visuals |
| `/demo/` (Interactive Demo) | Host an existing HTML app or studio | Unified `46px` OAW topbar wrapping the app entry (`demo_wrapper.entry_path`) with inline route tabs (`>= 900px`) or route pill (`< 900px`) |
| `/docs/` (Searchable Reader) | Read and search technical guides | Sticky left navigation rail (`>= 960px`), `38px` `Chapters` sub-bar (`< 960px`), instant filter, `Ctrl+K` search, and compiled diagrams |

### `/` Overview

The root route (`index.html`) answers three questions in seconds: what the tool does, how to install it, and where to try or read more. Content comes from the `overview` section of `oaw-site.json`, paired with optional social preview metadata (`social_preview`) for clean link cards.

### `/demo/` Interactive Demo

When `demo_wrapper.enabled` is `true`, the builder wraps your standalone demo page (`demo_wrapper.entry_path`) inside `/demo/`. The wrapper mounts the unified `46px` OAW topbar cleanly above the workspace so users can switch routes, open `Ctrl+K` search, or change color themes without leaving the demo.

### `/docs/` Searchable Reader

Every Markdown file listed under `docs_reader.sources` compiles into the `/docs/` reader. At `>= 960px`, a sticky left rail lists chapters and headings; below `960px`, a `38px` `Chapters` sub-bar opens a touch-friendly outline dialog. Client-side filtering narrows visible sections without a backend server, and fenced `quiet-evidence` blocks compile directly into theme-aware inline SVG schematics.

## Shared Shell Chrome

All three routes share the unified design token layer and a `46px` OAW topbar:

- **Direct `PROJECTS` Popover:** Pairs the project identity with a direct `PROJECTS` menu that pins `All Projects` on Row 1 above sibling OAW project links.
- **Responsive Route Navigation:** Renders inline route tabs (`Overview`, `Demo`, `Docs`) at `>= 900px` and collapses into a compact `< 900px` route pill (`Overview`/`Demo`/`Docs` popover) on narrower screens.
- **Lazy `Ctrl+K` Search:** Defers building the search modal until triggered via `Ctrl+K` (or the topbar search button), querying `search-index.json` across `This Space` and `All OAW` scopes.
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
    {"id": "demo", "label": "/demo/ Wrapper", "metric": "46px OAW Topbar", "stage": 3},
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
