# Onboarding Tokens & Customization Profiles

Extract and map design tokens from installed skills or local design repositories into Quiet UI's 4-theme token architecture.

## § Skill
Extract tokens from an installed Agent Skill that carries its own design system (e.g. a `brand-design` or `ui-kit` skill).

### Invocation

> *"Onboard quiet-ui-diagrams from my `acme-design` skill"*

Or the gate offers this as option (b) and the user names the skill.

### Step 1 — locate the skill

Use the installed-skill location exposed by the current agent when available. Otherwise search locations for the active harness:

**Pi:**

1. `~/.pi/agent/skills/<skill-name>/` and `~/.agents/skills/<skill-name>/` (user installs)
2. `.pi/skills/<skill-name>/` in the current directory, plus `.agents/skills/<skill-name>/` from the current directory through the repo root (project installs)
3. Package paths listed in `~/.pi/agent/settings.json` or `.pi/settings.json`; managed packages live under `~/.pi/agent/git/`, `~/.pi/agent/npm/`, `.pi/git/`, or `.pi/npm/`

**Claude Code:**

1. `~/.claude/skills/<skill-name>/` (user install)
2. `.claude/skills/<skill-name>/` (project install)

**Kiro:**

1. `.kiro/skills/<skill-name>/` (workspace install)
2. `~/.kiro/skills/<skill-name>/` (global install)

**OpenCode:**

1. `.opencode/skills/<skill-name>/` (project install)
2. `~/.config/opencode/skills/<skill-name>/` (global install)

**Cursor:**

1. `.cursor/skills/<skill-name>/` or `.agents/skills/<skill-name>/` (project install)
2. `~/.cursor/skills/<skill-name>/` or `~/.agents/skills/<skill-name>/` (user install)

**Cline (CLI or VS Code):**

1. `.cline/skills/<skill-name>/` or `.agents/skills/<skill-name>/` (workspace install)
2. `~/.cline/skills/<skill-name>/` or `~/.agents/skills/<skill-name>/` (user install)

**Codex:**

1. The skill root exposed by an active marketplace plugin
2. `~/.agents/skills/<skill-name>/` (user install or editable-clone link)

**GitHub Copilot:**

1. `.github/skills/<skill-name>/`, `.agents/skills/<skill-name>/`, or `.claude/skills/<skill-name>/` (project install)
2. `~/.copilot/skills/<skill-name>/`, `~/.agents/skills/<skill-name>/`, or `~/.claude/skills/<skill-name>/` (user install)

**Factory Droid:**

1. `~/.factory/skills/<skill-name>/` (personal install)
2. `.factory/skills/<skill-name>/` from the current directory through the repo root (folder-specific or project install)
3. The active path shown in `/skills` under **Plugins**; installed plugins keep the shared `skills/<skill-name>/` directory inside Droid's plugin cache

Finally, check any path the user provides explicitly. If the skill is still not found, ask the user to confirm the name or provide its path.

### Step 2 — read token sources

Glob the skill directory for any of these files and read them all:

| Priority | Pattern | What to look for |
|---|---|---|
| 1 | `*.css`, `colors*.css`, `tokens.css` | CSS custom properties in `:root { --color-*: …; }` |
| 2 | `tokens.json`, `design-tokens.json`, `*.tokens.json` | Style Dictionary / Figma token JSON |
| 3 | `SKILL.md`, `README.md` | Markdown tables listing colors, fonts, hex values |
| 4 | `style-guide.md`, `*design*.md` | Any narrative design documentation |
| 5 | `*.html` (preview/example files) | Inline `<style>` blocks — scan `:root` and `body` rules |

Read all matches and merge — CSS custom properties take priority over inferred values from HTML.

### Step 3 — extract colors and fonts

**From CSS custom properties:**
Map variable names to semantic roles using name-heuristics:

| If the variable name contains… | Map to role |
|---|---|
| `background`, `bg`, `paper`, `surface`, `canvas` | `paper` |
| `foreground`, `text`, `body`, `ink`, `on-surface` | `ink` |
| `muted`, `subtle`, `secondary`, `caption` | `muted` |
| `accent`, `brand`, `primary`, `cta`, `highlight` | `accent` |
| `border`, `rule`, `divider`, `outline` | `rule` |
| `mono`, `code`, `pre` | `sublabel` font |

**From JSON tokens:** follow the same heuristics on key names. If the JSON follows Style Dictionary format (`{ "color": { "brand": { "value": "#…" } } }`), flatten the path and apply heuristics to the leaf key.

**From Markdown tables:** look for rows with hex values (`#rrggbb`) adjacent to role-like words. A row like `| accent | #eb6c36 |` maps directly.

**Fonts:** look for `font-family` rules, `@import` or `@font-face` declarations, and Markdown mentions of font names alongside size/weight.

### Step 4 — map, validate, propose diff

Same as the URL method: fill the role table, run contrast checks, show the diff, ask for approval before writing.

### When skill extraction is ambiguous

- **Skill has no CSS or token files**: fall back to reading all `.md` files and look for hex values mentioned in prose. Surface what you found and ask the user to confirm mappings before applying.
- **Multiple accent candidates**: list them and ask the user to pick one. Don't guess.
- **Skill is dark-mode first**: ask whether to treat the dark values as the `paper`/`ink` defaults or to invert.

---

## § Folder

Extract tokens from a local directory — a checked-out design system repo, a Figma export, or any folder the user points you at.

### Invocation

> *"Onboard quiet-ui-diagrams from my design system at `~/projects/brand/design-tokens/`"*

Or the gate offers this as option (c) and the user provides the path.

### Step 1 — discover files

Glob the folder (recursively, up to 3 levels deep) for:

```
**/*.css
**/*.scss        (read @forward / $variable declarations)
**/tokens.json
**/*.tokens.json
**/design-tokens.json
**/colors.json
**/*style-guide*.md
**/*design-system*.md
**/README.md
**/*.html        (scan <style> blocks only)
```

If the result set is large (>20 files), prefer files in the root and files whose names contain `color`, `token`, `brand`, `palette`, `style`, or `theme`.

### Step 2 — read and merge

Read every discovered file. Apply the same extraction logic as the Skill method (§ Skill → Step 3). CSS custom properties and JSON tokens take priority over inferred values from prose.

**SCSS variables:** treat `$variable-name: value;` the same as a CSS custom property — apply name heuristics to `$variable-name`.

**Figma token JSON** (Figma Tokens Plugin format):

```json
{ "colors": { "brand": { "primary": { "value": "#eb6c36", "type": "color" } } } }
```

Walk the tree; the leaf `value` fields are the colors, the path segments supply the role heuristic.

### Step 3 — map, validate, propose diff

Same as the URL method: run contrast checks, show the full diff against current `style-guide.md`, and write only after the user approves.

### When folder extraction is ambiguous

- **No structured token files, only prose docs**: read every `.md` in the root and extract hex values found near role-like words. Show the user a table of what you inferred — don't silently apply uncertain mappings.
- **Multiple themes / color schemes found**: list them, ask the user which one to use as the diagram skin.
- **Folder has zero readable files**: tell the user and ask for a more specific path or switch to manual token entry.

---

## Multiple clients? Save a profile

After every onboarding method, offer to save the completed guide as a named client profile. Follow [`profiles.md`](profiles.md) for the canonical home-directory library, metadata header, strict slug validation, and project marker. A project with a `customizations/<name>/customization.json` marker reads its profile directly, so parallel client workspaces do not overwrite one shared working copy.

---

## Final step — user verifies the output

After applying the tokens and handling the profile choice, generate or rebuild a representative output document. If onboarding is part of a diagram request, use that requested output; otherwise use one representative example. Provide its local path and task the user explicitly:

> *"Please open `<output-path>` and verify the palette, typography, contrast, and overall rendering. Reply `approved` or tell me what should change."*

Automated checks do not replace this review. Leave onboarding marked **pending user verification** until the user explicitly confirms the output document. If the user requests corrections, apply them, rebuild the output document, provide its local path, and ask for approval again.

---

See [onboarding.md](onboarding.md) for Gate 0 and URL onboarding flow.
