#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Quiet UI — Dynamic Showcase Builder (v6.2)
Compiles a customized Quiet UI showcase HTML file based on customization.json manifest.
Filters tiers and navigation strictly to enabled_tiers and links or bundles customization styles.
License: MIT (https://github.com/FrankXLT/quiet-ui-skills)
"""

import argparse
import json
import re
import sys
from pathlib import Path

ALL_17_TIERS = [
    "doc-1", "doc-2", "doc-3", "doc-4b", "doc-4a", "bridge-1",
    "deck-1", "bridge-2", "app-2",
    "app-1", "app-4", "app-3", "app-5", "app-tree",
    "ha-1", "ha-2", "ha-3",
]


def load_manifest(target_dir: Path) -> dict:
    manifest_path = target_dir / "customization.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_showcase(
    target_dir: Path,
    source_html_path: Path,
    output_html_path: Path,
    bundle: bool = False,
) -> None:
    manifest = load_manifest(target_dir)
    title = manifest.get("title", "Quiet UI Showcase")
    mode = manifest.get("mode", "personal")
    enabled = manifest.get("enabled_tiers", ALL_17_TIERS)
    disabled = manifest.get(
        "disabled_tiers",
        [t for t in ALL_17_TIERS if t not in enabled],
    )

    if not source_html_path.exists():
        raise FileNotFoundError(f"Source master showcase not found: {source_html_path}")

    html = source_html_path.read_text(encoding="utf-8")

    # 1. Update <title>
    html = re.sub(
        r"<title>.*?</title>",
        f"<title>{title} — Quiet UI Showcase</title>",
        html,
        count=1,
    )

    # 2. Wire CSS tokens and overrides
    tokens_path = target_dir / "styles" / "quiet-ui-tokens.css"
    overrides_path = target_dir / "styles" / "overrides.css"

    if bundle:
        tok_css = tokens_path.read_text(encoding="utf-8") if tokens_path.exists() else ""
        ovr_css = overrides_path.read_text(encoding="utf-8") if overrides_path.exists() else ""
        bundle_block = (
            f"\n  <style id=\"custom-tokens\">\n{tok_css}\n  </style>\n"
            f"  <style id=\"custom-overrides\">\n{ovr_css}\n  </style>\n"
        )
        html = html.replace("</head>", f"{bundle_block}</head>", 1)
    else:
        links_block = (
            "  <link rel=\"stylesheet\" href=\"./styles/quiet-ui-tokens.css\" />\n"
            "  <link rel=\"stylesheet\" href=\"./styles/overrides.css\" />\n"
        )
        html = html.replace("</head>", f"{links_block}</head>", 1)

    # 3. Filter <select id="va-studio-tier-select">
    def filter_select(match: re.Match) -> str:
        tag_start, inner, tag_end = match.group(1), match.group(2), match.group(3)
        kept_options: list[str] = []
        for opt_match in re.finditer(r'<option\s+value="([^"]+)">([^<]+)</option>', inner):
            val, lbl = opt_match.group(1), opt_match.group(2)
            if val in enabled:
                kept_options.append(f'        <option value="{val}">{lbl}</option>')
        return f"{tag_start}\n" + "\n".join(kept_options) + f"\n      {tag_end}"

    html = re.sub(
        r'(<select\s+id="va-studio-tier-select"[^>]*>)(.*?)(</select>)',
        filter_select,
        html,
        flags=re.S,
    )

    # 4. Filter <div id="tier-switcher-bar">
    def filter_switcher(match: re.Match) -> str:
        outer = match.group(0)
        # Filter each family group
        def filter_group(g_match: re.Match) -> str:
            g_content = g_match.group(0)
            kept_btns: list[str] = []
            for b_match in re.finditer(r'<button\s+[^>]*data-tier="([^"]+)"[^>]*>.*?</button>', g_content):
                b_tier = b_match.group(1)
                if b_tier in enabled:
                    kept_btns.append(f"          {b_match.group(0)}")
            if not kept_btns:
                return ""
            tag_m = re.search(r'<span class="pop-family-tag">([^<]+)</span>', g_content)
            tag_lbl = tag_m.group(1) if tag_m else "Tiers"
            return (
                f'      <div class="pop-family-group">\n'
                f'        <span class="pop-family-tag">{tag_lbl}</span>\n'
                f'        <div class="pop-tier-strip">\n'
                + "\n".join(kept_btns)
                + "\n        </div>\n      </div>"
            )

        new_groups = re.sub(
            r'<div class="pop-family-group">.*?</div>\s*</div>',
            filter_group,
            outer,
            flags=re.S,
        )
        return new_groups

    html = re.sub(
        r'<div class="pop-sec" id="tier-switcher-bar">.*?<!-- 2\. Native Navigation Shell',
        lambda m: filter_switcher(m) + "\n\n    <!-- 2. Native Navigation Shell",
        html,
        flags=re.S,
    )

    # 5. Remove disabled tier sections
    for dis in disabled:
        pattern = rf'\n\s*<section id="tier-{re.escape(dis)}"[^>]*>.*?</section>'
        html = re.sub(pattern, "", html, flags=re.S)

    # 6. Update tierOrder JavaScript array
    js_tier_array = ",\n      ".join(f"'{t}'" for t in enabled)
    html = re.sub(
        r"const tierOrder = \[[^\]]*\];",
        f"const tierOrder = [\n      {js_tier_array}\n    ];",
        html,
    )

    # 7. Ensure active tier is among enabled tiers
    first_tier = enabled[0] if enabled else "doc-1"
    if "doc-1" not in enabled:
        html = re.sub(r'data-active-tier="[^"]*"', f'data-active-tier="{first_tier}"', html, count=1)
        # Mark first section as active
        html = re.sub(
            rf'<section id="tier-{re.escape(first_tier)}" class="([^"]*)"',
            rf'<section id="tier-{re.escape(first_tier)}" class="\1 active"',
            html,
            count=1,
        )
        # Mark first button as active
        html = re.sub(
            rf'<button([^>]*data-tier="{re.escape(first_tier)}"[^>]*)class="tier-btn"',
            r'<button\1class="tier-btn active"',
            html,
            count=1,
        )

    output_html_path.write_text(html, encoding="utf-8")
    print(
        f"[OK] Built {mode} showcase ({len(enabled)} tiers enabled, {len(disabled)} disabled) "
        f"-> {output_html_path}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Quiet UI Customized Showcase")
    parser.add_argument("target", type=str, help="Target customization folder (e.g. customizations/brand-starter)")
    parser.add_argument("--source", type=str, default="", help="Path to master showcase HTML")
    parser.add_argument("--output", type=str, default="", help="Path to output showcase HTML")
    parser.add_argument("--bundle", action="store_true", help="Inline styles instead of external links")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    target_dir = (repo_root / args.target).resolve() if not Path(args.target).is_absolute() else Path(args.target)
    source_html = Path(args.source) if args.source else repo_root / "quiet-ui-showcase.html"
    output_html = Path(args.output) if args.output else target_dir / "showcase.html"

    if not target_dir.exists():
        print(f"[FAIL] Target directory does not exist: {target_dir}", file=sys.stderr)
        return 1

    build_showcase(target_dir, source_html, output_html, bundle=args.bundle)
    return 0


if __name__ == "__main__":
    sys.exit(main())
