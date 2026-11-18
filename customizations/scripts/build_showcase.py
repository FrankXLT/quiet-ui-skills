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
import html as _html
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


def _filter_v9_showcase(html: str, manifest: dict, disabled_tiers: list[str], mode: str) -> tuple[str, str]:
    """Filter v9 world/view selectors, JSON manifest, and templates."""
    m = re.search(r'(<script[^>]*id="va-v9-manifest"[^>]*>)(.*?)(</script>)', html, flags=re.S)
    if not m:
        return html, "0 views"
    v9_data = json.loads(m.group(2))
    enabled_worlds = manifest.get("enabled_worlds")
    enabled_views = manifest.get("enabled_views")
    brand_excluded: set[str] = set()
    if mode == "brand":
        if "hud-1" in disabled_tiers:
            brand_excluded.add("v15-collimated-flight-hud")
        if "ctrl-1" in disabled_tiers or "hud-1" in disabled_tiers:
            brand_excluded.add("v16-transparent-window-overlay")
    kept_worlds, disabled_views = [], []
    for w in v9_data.get("worlds", []):
        if enabled_worlds and w["world_id"] not in enabled_worlds:
            disabled_views.extend(vw["view_id"] for vw in w.get("views", []))
            continue
        kept_views = []
        for vw in w.get("views", []):
            vid = vw["view_id"]
            if (enabled_views and vid not in enabled_views) or vid in brand_excluded:
                disabled_views.append(vid)
            else:
                kept_views.append(vw)
        if kept_views:
            w_copy = dict(w)
            w_copy["views"] = kept_views
            kept_worlds.append(w_copy)
    v9_data["worlds"] = kept_worlds
    new_json = json.dumps(v9_data, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e")
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    w_opts = "\n".join(
        f'          <option value="{_html.escape(str(w["world_id"]), quote=True)}">{_html.escape(str(w["world_label"]))}</option>'
        for w in kept_worlds
    )
    first_views = kept_worlds[0]["views"] if kept_worlds else []
    v_opts = "\n".join(
        f'        <option value="{_html.escape(str(vw["view_id"]), quote=True)}">{_html.escape(str(vw["option_label"]))}</option>'
        for vw in first_views
    )
    for sid in ("va-domain-select", "va-sheet-domain-select"):
        html = re.sub(
            rf'(<select\s+id="{sid}"[^>]*>)(.*?)(</select>)',
            lambda match: f"{match.group(1)}\n{w_opts}\n        {match.group(3)}",
            html,
            flags=re.S,
        )
    html = re.sub(
        r'(<select\s+id="va-view-select"[^>]*>)(.*?)(</select>)',
        lambda match: f"{match.group(1)}\n{v_opts}\n      {match.group(3)}",
        html,
        flags=re.S,
    )
    for vid in disabled_views:
        html = re.sub(rf'\n\s*<template\s+id="tpl-view-{re.escape(vid)}"[^>]*>.*?</template>', "", html, flags=re.S)
    total_views = sum(len(w["views"]) for w in kept_worlds)
    return html, f"{len(kept_worlds)} worlds, {total_views} views"


def build_showcase(
    target_dir: Path,
    source_html_path: Path,
    output_html_path: Path,
    bundle: bool = False,
) -> None:
    manifest = load_manifest(target_dir)
    title = str(manifest.get("title", "Quiet UI Showcase"))
    mode = str(manifest.get("mode", "personal"))

    raw_enabled = manifest.get("enabled_tiers", ALL_16_TIERS)
    enabled = normalize_tiers(raw_enabled) or list(ALL_16_TIERS)
    raw_disabled = manifest.get("disabled_tiers", [t for t in ALL_16_TIERS if t not in enabled])
    disabled = normalize_tiers(raw_disabled)
    for t in ALL_16_TIERS:
        if t not in enabled and t not in disabled:
            disabled.append(t)

    if not source_html_path.exists():
        raise FileNotFoundError(f"Source master showcase not found: {source_html_path}")

    html = source_html_path.read_text(encoding="utf-8")
    safe_title = _html.escape(title, quote=True)
    html = re.sub(r"<title>.*?</title>", lambda _m: f"<title>{safe_title} — Quiet UI Showcase</title>", html, count=1)

    tokens_path = target_dir / "styles" / "quiet-ui-tokens.css"
    overrides_path = target_dir / "styles" / "overrides.css"
    custom_attr = 'data-custom-styles="true"'
    if bundle:
        custom_attr += ' data-inline-custom-css="true"'
        tok_css = re.sub(r"</\s*style", "<\\/style", tokens_path.read_text(encoding="utf-8"), flags=re.I) if tokens_path.exists() else ""
        ovr_css = re.sub(r"</\s*style", "<\\/style", overrides_path.read_text(encoding="utf-8"), flags=re.I) if overrides_path.exists() else ""
        bundle_block = f'\n  <style id="custom-tokens">\n{tok_css}\n  </style>\n  <style id="custom-overrides">\n{ovr_css}\n  </style>\n'
        html = html.replace("</head>", f"{bundle_block}</head>", 1)
    else:
        links_block = '  <link rel="stylesheet" href="./styles/quiet-ui-tokens.css" />\n  <link rel="stylesheet" href="./styles/overrides.css" />\n'
        html = html.replace("</head>", f"{links_block}</head>", 1)
    html = re.sub(r'<html\b([^>]*)>', lambda m: f'<html{m.group(1)} {custom_attr}>', html, count=1)

    if 'id="va-v9-manifest"' in html:
        html, summary = _filter_v9_showcase(html, manifest, disabled, mode)
        output_html_path.write_text(html, encoding="utf-8")
        print(f"[OK] Built {mode} v9 showcase ({summary}) -> {output_html_path}")
        return

    def filter_select(match: re.Match) -> str:
        tag_start, inner, tag_end = match.group(1), match.group(2), match.group(3)
        kept = [
            f'        <option value="{TIER_ALIASES.get(m.group(1), m.group(1))}">{m.group(2)}</option>'
            for m in re.finditer(r'<option\s+value="([^"]+)">([^<]+)</option>', inner)
            if TIER_ALIASES.get(m.group(1), m.group(1)) in enabled
        ]
        return f"{tag_start}\n" + "\n".join(kept) + f"\n      {tag_end}"

    html = re.sub(r'(<select\s+id="va-(?:studio-)?tier-select"[^>]*>)(.*?)(</select>)', filter_select, html, flags=re.S)
    for dis in disabled:
        html = re.sub(rf'\n\s*<template\s+id="tpl-tier-{re.escape(dis)}"[^>]*>.*?</template>', "", html, flags=re.S)
        html = re.sub(rf'\n\s*<section\s+id="tier-{re.escape(dis)}"[^>]*>.*?</section>', "", html, flags=re.S)
        html = re.sub(rf'\s*<button\s+[^>]*data-tier="{re.escape(dis)}"[^>]*>.*?</button>', "", html)

    first_tier = enabled[0] if enabled else "doc-1"
    html = re.sub(r'data-tier="[^"]*"', f'data-tier="{first_tier}"', html, count=1)
    output_html_path.write_text(html, encoding="utf-8")
    print(f"[OK] Built {mode} showcase ({len(enabled)} tiers enabled, {len(disabled)} disabled) -> {output_html_path}")


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
