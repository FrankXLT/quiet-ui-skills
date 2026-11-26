# Getting Started

Quiet User Interface Skills gives developers and AI coding agents a calm, zero-dependency front-end toolkit. Instead of fighting cluttered dashboards, unreadable dark themes, or hand-coded SVG coordinates, you work from one shared design contract that compiles clean interfaces and exact charts out of the box.

## What Quiet User Interface Skills Solves

- **Calm screens without clutter:** Pages follow clear reading widths, balanced spacing, and predictable navigation across phones, desktops, wall displays, and control consoles.
- **Honest 1-2-5 charts:** Quantitative plots snap to clean `1`, `2`, and `5` axis steps, label units and uncertainty ranges plainly, and show missing-data gaps honestly instead of smoothing over them.
- **Automatic 4-theme contrast:** One CSS token stylesheet (`tokens/quiet-ui-tokens.css`) switches smoothly across **Pure White**, **Warm Paper**, **Dark**, and **Dark Paper** while meeting contrast standards without `!important`.
- **Built-in HTML and CSS verification:** An offline Python auditor inspects your generated pages and stylesheets for clipped labels, low contrast, unlabeled form fields, and style drift before you ship.

> [!NOTE]
> Core engine modules (`skills/`, `src/`, `scripts/`, `tests/`) are licensed under Apache 2.0. Design tokens, starter kits in `customizations/`, and every page or chart you generate are MIT-licensed with zero attribution requirements.

## Install in One Command

Clone the repository and run the installer to register both the native Antigravity plugin and portable cross-agent skills (Claude Code, Cursor, Codex, and Windsurf):

```bash
git clone https://github.com/FrankXLT/quiet-ui-skills.git
cd quiet-ui-skills
./install.sh
```

Running `./install.sh` installs the plugin bundle to `~/.gemini/config/plugins/quiet-ui-skills/` and copies the three portable skills into `~/.agents/skills/{quiet-ui,quiet-evidence,quiet-bridge}/`.

If you prefer installing individual pillars through the Skills CLI, pick the ones you need:

```bash
npx skills add https://github.com/FrankXLT/quiet-ui-skills --skill quiet-ui
npx skills add https://github.com/FrankXLT/quiet-ui-skills --skill quiet-evidence
npx skills add https://github.com/FrankXLT/quiet-ui-skills --skill quiet-bridge
```

## Your First Figure or Page in Under 2 Minutes

You can try Quiet UI immediately using pure Python (`>= 3.10`) with zero third-party packages.

### 1. Compile a Calibrated Chart

Compile one of the included evidence specs into a standalone, 4-theme HTML5 page:

```bash
python3 -B skills/quiet-evidence/scripts/compile_evidence.py \
  content/corpora/02-cloud-cyber-and-ai-ops/evidence/v06_ai_calibration_plot.json \
  --rigor L2 --theme white --out first-chart.html
```

Swap `--fragment` in place of `--out` when you want an embeddable HTML/SVG fragment to drop directly into an existing app or Markdown guide.

### 2. Build a Calm Page with Design Tokens

Link `tokens/quiet-ui-tokens.css` (and optionally `skills/quiet-evidence/assets/quiet-evidence-bundle.css`) inside your HTML `<head>`, then set `data-theme="white"` on `<html>`:

```html
<!doctype html>
<html lang="en" data-theme="white">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Service Health Summary</title>
  <link rel="stylesheet" href="./tokens/quiet-ui-tokens.css" />
  <style>
    body {
      margin: 0;
      padding: 2rem;
      background: var(--bg-canvas);
      color: var(--text-primary);
      font-family: var(--font-sans);
    }
    .summary-card {
      max-inline-size: 46rem;
      padding: 1.5rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      border-radius: var(--radius-card);
    }
  </style>
</head>
<body>
  <main class="summary-card">
    <h1>API Gateway Readiness</h1>
    <p>All regional probes remain within target response tolerances.</p>
  </main>
</body>
</html>
```

### 3. Verify Layout, Contrast, and Drift

Run the portable auditor against your generated HTML file to catch contrast issues, clipped SVGs, unlabeled controls, or style drift:

```bash
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py first-chart.html --strict-drift
```

When working inside an ongoing codebase, initialize a `.quiet-ui.md` context file once so agents remember your layout mode and blocklist rules across sessions:

```bash
python3 -B skills/quiet-ui/scripts/audit_quiet_html.py --init-context .quiet-ui.md
```

### 4. Preview Locally

Serve the local studio and documentation portal on port `8788`:

```bash
python3 -B scripts/serve_showcase.py --port 8788
```

## Where Everything Lives

Use this map to jump straight to the right part of the Quiet UI Skills site:

| Surface | Path | What You Will Find |
| :--- | :--- | :--- |
| **Overview** | `index.html` | Plain-language summary, install commands, 6-domain preview cards, and ecosystem flow diagram. |
| **Demo** | `demo/index.html` | Interactive 6-domain, 26-view Studio covering memos, runbooks, dashboards, and hardware consoles. |
| **Docs** | `docs/index.html` | Searchable two-column Markdown reader with section outlines, quick jumps, and live diagrams. |
| **Component Library** | `demo/index.html?mode=components` | 53 compiled UI, SVG plot, ECharts, schematic, form, and zero-state specimens (`docs/bench/evidence-bench.html`). |

## Next Steps

- **Adapt colors and fonts in one minute:** Read [60-Second Brand Customization](./02-customization.md).
- **Understand the three pillars:** Read [Architecture & Three Pillars](./03-architecture-and-pillars.md).
- **Explore charts and verification rules:** Read [Calibrated Charts & Layout Auditor](./04-evidence-and-auditor.md).
