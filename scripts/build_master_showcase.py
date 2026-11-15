#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Quiet UI v8.0.1 — Universal Responsive Stage Portal Master Compiler
Compiles tokens, layer-scoped CSS, JS controllers, and tier templates into showcase HTML.
License: MIT (https://github.com/FrankXLT/quiet-ui-skills)
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ALL_16_TIERS = [
    ("doc-1", "01. Doc-1 Research Monograph"),
    ("doc-2", "02. Doc-2 Policy Brief"),
    ("doc-3", "03. Doc-3 Tech Whitepaper"),
    ("doc-4b", "04. Doc-4b API Docs Portal"),
    ("doc-4a", "05. Doc-4a Ops Runbook"),
    ("bridge-1", "06. Bridge-1 Telemetry Dash"),
    ("deck-1", "07. Deck-1 Executive Briefing"),
    ("bridge-2", "08. Bridge-2 Telemetry Matrix"),
    ("app-2", "09. App-2 Wave Workbench"),
    ("app-1", "10. App-1 Queue Dispatch"),
    ("app-4", "11. App-4 Task Dual-Pane"),
    ("app-3", "12. App-3 Responsive Bento"),
    ("app-5", "13. App-5 Circadian Companion"),
    ("app-tree", "14. App-Tree Hierarchy"),
    ("hud-1", "15. HUD-1 Optical Glass"),
    ("ctrl-1", "16. Ctrl-1 Mission Control"),
]


def bundle_portal_css(repo_root: Path) -> str:
    parts: list[str] = ["@layer reset, tokens, shell, archetypes, utilities;"]
    tok_f = repo_root / "tokens" / "quiet-ui-tokens.css"
    if tok_f.exists():
        parts.append(f"@layer tokens {{\n{tok_f.read_text(encoding='utf-8')}\n}}")
    css_dir = repo_root / "src" / "css"
    for i in range(7):
        for f in sorted(css_dir.glob(f"0{i}-*.css")):
            parts.append(f.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def load_tier_templates(repo_root: Path) -> str:
    tiers_dir = repo_root / "src" / "tiers"
    tpls: list[str] = []
    found_slugs: set[str] = set()

    if tiers_dir.exists():
        for f in sorted(tiers_dir.glob("*.html")):
            slug = re.sub(r"^\d+[-_]", "", f.stem)
            content = f.read_text(encoding="utf-8").strip()
            if content.lstrip().startswith("<template"):
                tpls.append(f"  {content}")
            else:
                tpls.append(f'  <template id="tpl-tier-{slug}">\n{content}\n  </template>')
            found_slugs.add(slug)

    for slug, label in ALL_16_TIERS:
        if slug not in found_slugs:
            tpls.append(
                f'  <template id="tpl-tier-{slug}">\n'
                f'    <div class="va-panel-tonal" style="padding: 2rem;">\n'
                f'      <h2>{label}</h2>\n'
                f'      <p>Content for {slug} stage portal.</p>\n'
                f'    </div>\n'
                f'  </template>'
            )
    return "\n".join(tpls)


def load_tier_js(repo_root: Path) -> str:
    js_dir = repo_root / "src" / "js"
    family_files = [
        js_dir / f"tiers-family-{fam}.js"
        for fam in ("a", "b", "c", "d")
    ]
    if all(f.exists() for f in family_files):
        return "\n\n".join(f.read_text(encoding="utf-8") for f in family_files)
    legacy = js_dir / "tier-interactions.js"
    if legacy.exists():
        return legacy.read_text(encoding="utf-8")
    return ""


def assemble_showcase(repo_root: Path) -> str:
    css_dir = repo_root / "src" / "css"
    chrome_css = "\n\n".join(
        f.read_text(encoding="utf-8")
        for f in (css_dir / "07-studio-portal-chrome.css", css_dir / "08-studio-sheet.css")
        if f.exists()
    )
    js_dir = repo_root / "src" / "js"
    studio_js = "\n\n".join(
        (js_dir / name).read_text(encoding="utf-8")
        for name in ("portal-resize.js", "studio-sheet.js", "studio-portal.js")
        if (js_dir / name).exists()
    )
    tier_options = "\n".join(
        f'        <option value="{slug}">{label}</option>'
        for slug, label in ALL_16_TIERS
    )
    shell_html = (repo_root / "src" / "chrome" / "studio-shell.html").read_text(encoding="utf-8")
    replacements = {
        "__CHROME_CSS__": chrome_css,
        "__TIER_OPTIONS__": tier_options,
        "__PORTAL_CSS__": bundle_portal_css(repo_root),
        "__TIER_JS__": load_tier_js(repo_root),
        "__TIER_TEMPLATES__": load_tier_templates(repo_root),
        "__STUDIO_JS__": studio_js,
    }
    for token, val in replacements.items():
        shell_html = shell_html.replace(token, val)
    return shell_html


def build_starters(repo_root: Path) -> None:
    build_script = repo_root / "customizations" / "scripts" / "build_showcase.py"
    if not build_script.exists():
        return
    for st in ("personal-starter", "brand-starter"):
        st_dir = repo_root / "customizations" / st
        if st_dir.exists():
            subprocess.run([sys.executable, "-B", str(build_script), str(st_dir)], cwd=repo_root, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Quiet UI v8.0.1 Master Showcase")
    parser.add_argument("--skip-starters", action="store_true", help="Skip compiling starter showcases")
    parser.add_argument("--output", default="", help="Custom output path")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    html = assemble_showcase(repo_root)

    out_file = Path(args.output) if args.output else repo_root / "quiet-ui-showcase.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"[OK] Master showcase written -> {out_file}")

    docs_index = repo_root / "docs" / "index.html"
    if docs_index.parent.exists():
        shutil.copy2(out_file, docs_index)
        print(f"[OK] Copied to docs index -> {docs_index}")

    if not args.skip_starters:
        build_starters(repo_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
