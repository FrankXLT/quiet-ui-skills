#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Quiet UI — Dynamic Showcase Builder (v8.0)
Compiles a customized Quiet UI showcase HTML file based on customization.json manifest.
Filters 16-tier continuum and navigation strictly to enabled_tiers and configures styles.
License: MIT (https://github.com/FrankXLT/quiet-ui-skills)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALL_16_TIERS = [
    "doc-1", "doc-2", "doc-3", "doc-4b", "doc-4a", "bridge-1",
    "deck-1", "bridge-2", "app-2",
    "app-1", "app-4", "app-3", "app-5", "app-tree",
    "hud-1", "ctrl-1",
]

TIER_ALIASES = {
    "ha-1": "hud-1",
    "ha-2": "ctrl-1",
    "ha-3": None,
}


def normalize_tiers(tier_list: list[str]) -> list[str]:
    """Map legacy aliases and filter valid v8.0 tiers preserving order."""
    normalized: list[str] = []
    for t in tier_list:
        resolved = TIER_ALIASES.get(t, t)
        if resolved and resolved in ALL_16_TIERS and resolved not in normalized:
            normalized.append(resolved)
    return normalized


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

    raw_enabled = manifest.get("enabled_tiers", ALL_16_TIERS)
    enabled = normalize_tiers(raw_enabled)
    if not enabled:
        enabled = list(ALL_16_TIERS)

    raw_disabled = manifest.get("disabled_tiers", [t for t in ALL_16_TIERS if t not in enabled])
    disabled = normalize_tiers(raw_disabled)
    for t in ALL_16_TIERS:
        if t not in enabled and t not in disabled:
            disabled.append(t)

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

    # 2. Stamp custom styles attributes & bundle/link styles
    tokens_path = target_dir / "styles" / "quiet-ui-tokens.css"
    overrides_path = target_dir / "styles" / "overrides.css"

    custom_attr = 'data-custom-styles="true"'
    if bundle:
        custom_attr += ' data-inline-custom-css="true"'
        tok_css = tokens_path.read_text(encoding="utf-8") if tokens_path.exists() else ""
        ovr_css = overrides_path.read_text(encoding="utf-8") if overrides_path.exists() else ""
        bundle_block = (
            f'\n  <style id="custom-tokens">\n{tok_css}\n  </style>\n'
            f'  <style id="custom-overrides">\n{ovr_css}\n  </style>\n'
        )
        html = html.replace("</head>", f"{bundle_block}</head>", 1)
    else:
        links_block = (
            '  <link rel="stylesheet" href="./styles/quiet-ui-tokens.css" />\n'
            '  <link rel="stylesheet" href="./styles/overrides.css" />\n'
        )
        html = html.replace("</head>", f"{links_block}</head>", 1)

    html = re.sub(r'<html\b([^>]*)>', rf'<html\1 {custom_attr}>', html, count=1)

    # 3. Filter <select id="va-tier-select"> and <select id="va-studio-tier-select">
    def filter_select(match: re.Match) -> str:
        tag_start, inner, tag_end = match.group(1), match.group(2), match.group(3)
        kept_options: list[str] = []
        for opt_match in re.finditer(r'<option\s+value="([^"]+)">([^<]+)</option>', inner):
            val, lbl = opt_match.group(1), opt_match.group(2)
            res_val = TIER_ALIASES.get(val, val)
            if res_val in enabled:
                kept_options.append(f'        <option value="{res_val}">{lbl}</option>')
        return f"{tag_start}\n" + "\n".join(kept_options) + f"\n      {tag_end}"

    html = re.sub(
        r'(<select\s+id="va-(?:studio-)?tier-select"[^>]*>)(.*?)(</select>)',
        filter_select,
        html,
        flags=re.S,
    )

    # 4. Remove disabled <template id="tpl-tier-{dis}"> blocks
    for dis in disabled:
        pattern = rf'\n\s*<template\s+id="tpl-tier-{re.escape(dis)}"[^>]*>.*?</template>'
        html = re.sub(pattern, "", html, flags=re.S)
        legacy_pat = rf'\n\s*<section\s+id="tier-{re.escape(dis)}"[^>]*>.*?</section>'
        html = re.sub(legacy_pat, "", html, flags=re.S)

    # 5. Filter legacy switcher buttons if present
    for dis in disabled:
        btn_pat = rf'\s*<button\s+[^>]*data-tier="{re.escape(dis)}"[^>]*>.*?</button>'
        html = re.sub(btn_pat, "", html)

    # 6. Ensure default tier is among enabled tiers
    first_tier = enabled[0] if enabled else "doc-1"
    html = re.sub(r'data-tier="[^"]*"', f'data-tier="{first_tier}"', html, count=1)

    output_html_path.write_text(html, encoding="utf-8")
    print(
        f"[OK] Built {mode} showcase ({len(enabled)} tiers enabled, {len(disabled)} disabled) "
        f"-> {output_html_path}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Quiet UI Customized Showcase")
    parser.add_argument("target", type=str, help="Target customization folder")
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
