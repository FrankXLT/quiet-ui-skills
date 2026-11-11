#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Quiet UI — Customization Verifier (v6.2)
Verifies user and starter customizations against design contract, WCAG contrast,
concentric geometry invariants, and repository immutability gates.
License: MIT (https://github.com/FrankXLT/quiet-ui-skills)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FORBIDDEN_EMOJIS = ("✨", "⚡", "☀", "🛡", "●", "&#10024;")
REQUIRED_INTENT_FILES = (
    "00-global-structure.md",
    "01-docs-and-specs.md",
    "02-workspaces-apps.md",
    "03-spatial-ambient.md",
)


def hex_to_relative_luminance(hex_str: str) -> float:
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    channels = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in (r, g, b)
    ]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = hex_to_relative_luminance(hex1)
    l2 = hex_to_relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def verify_palette_contrast(palette: dict) -> list[str]:
    errs: list[str] = []
    text_pri = palette.get("text_primary")
    text_sec = palette.get("text_secondary")
    surface = palette.get("surface") or palette.get("canvas") or "#FFFFFF"

    if text_pri and re.match(r"^#[0-9a-fA-F]{3,6}$", text_pri) and re.match(r"^#[0-9a-fA-F]{3,6}$", surface):
        r_pri = contrast_ratio(text_pri, surface)
        if r_pri < 4.5:
            errs.append(f"[WCAG_CONTRAST] Primary text {text_pri} vs surface {surface} ratio {r_pri:.2f} < 4.5:1")

    if text_sec and re.match(r"^#[0-9a-fA-F]{3,6}$", text_sec) and re.match(r"^#[0-9a-fA-F]{3,6}$", surface):
        r_sec = contrast_ratio(text_sec, surface)
        if r_sec < 3.0:
            errs.append(f"[WCAG_CONTRAST] Secondary text {text_sec} vs surface {surface} ratio {r_sec:.2f} < 3.0:1")

    return errs


def verify_showcase(html_path: Path, enabled: list[str], disabled: list[str]) -> list[str]:
    errs: list[str] = []
    if not html_path.exists():
        return [f"[FILE_MISSING] Showcase file not found: {html_path}"]

    content = html_path.read_text(encoding="utf-8")

    # 1. Enabled tiers present in DOM & selectors
    for t in enabled:
        sec_id = f'id="tier-{t}"'
        if sec_id not in content:
            errs.append(f"[TIER_DOM_MISSING] Enabled tier '{t}' missing section container {sec_id}")
        opt_token = f'<option value="{t}">'
        if opt_token not in content:
            errs.append(f"[TIER_SELECT_MISSING] Enabled tier '{t}' missing studio select option {opt_token}")
        btn_token = f'data-tier="{t}"'
        if btn_token not in content:
            errs.append(f"[TIER_BTN_MISSING] Enabled tier '{t}' missing popover switch button {btn_token}")

    # 2. Disabled tiers absent from DOM & selectors
    for d in disabled:
        sec_id = f'id="tier-{d}"'
        if sec_id in content:
            errs.append(f"[DISABLED_TIER_LEAK] Disabled tier '{d}' found in DOM section {sec_id}")
        opt_token = f'<option value="{d}">'
        if opt_token in content:
            errs.append(f"[DISABLED_TIER_SELECT] Disabled tier '{d}' found in studio select")
        btn_token = f'data-tier="{d}"'
        if btn_token in content:
            errs.append(f"[DISABLED_TIER_BTN] Disabled tier '{d}' found in switcher bar")

    # 3. Geometric & Typographic Invariants
    if "tabular-nums" not in content:
        errs.append("[TYPOGRAPHY_VIOLATION] Missing 'tabular-nums' numeric discipline in CSS.")
    sub11 = re.search(r"font-size\s*:\s*(?:[0-9]|10)(?:\.[0-9]+)?px", content, flags=re.I)
    if sub11:
        errs.append(f"[SUB_11PX_VIOLATION] Sub-11px font size rule detected: '{sub11.group(0)}'")
    for em in FORBIDDEN_EMOJIS:
        if em in content:
            errs.append(f"[EMOJI_VIOLATION] Forbidden unicode emoji/entity found: {em!r}")

    for rad_tok in ("--radius-card", "--radius-inner"):
        if rad_tok not in content:
            errs.append(f"[CONCENTRIC_RADIUS] Missing concentric radius token '{rad_tok}'")

    visible_html = re.sub(r"<(script|style|pre|code)\b[^>]*>.*?</\1>", "", content, flags=re.S | re.I)
    visible_text = re.sub(r"<[^>]+>", " ", visible_html)
    for ph in (r"\bTODO\b", r"\bTBD\b", r"Lorem\s+ipsum", r"\[Insert\s", r"\{\{"):
        m = re.search(ph, visible_text)
        if m:
            errs.append(f"[PLACEHOLDER_VIOLATION] Unfilled placeholder found in text: '{m.group(0)}'")

    return errs


def check_immutability(repo_root: Path) -> list[str]:
    errs: list[str] = []
    res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    if res.returncode != 0:
        return [f"[GIT_ERROR] Failed to run git status: {res.stderr}"]

    protected_prefixes = (
        "skills/visual-architecture-system/",
        "customizations/personal-starter/",
        "customizations/brand-starter/",
    )
    for line in res.stdout.splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            fpath = parts[1]
            for pfx in protected_prefixes:
                if fpath.startswith(pfx):
                    errs.append(f"[IMMUTABILITY_BREACH] Protected starter/core file modified: {fpath}")
    return errs


def verify_customization(target_dir: Path, repo_root: Path, check_immutable: bool = False) -> list[str]:
    errors: list[str] = []
    manifest_file = target_dir / "customization.json"
    if not manifest_file.exists():
        return [f"[MANIFEST_MISSING] {manifest_file} not found"]

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"[MANIFEST_INVALID] Failed to parse customization.json: {exc}"]

    # Validate schema
    mode = manifest.get("mode")
    if mode not in ("personal", "brand"):
        errors.append(f"[MANIFEST_SCHEMA] Invalid mode '{mode}'. Must be 'personal' or 'brand'.")
    enabled = manifest.get("enabled_tiers", [])
    disabled = manifest.get("disabled_tiers", [])
    if not enabled:
        errors.append("[MANIFEST_SCHEMA] 'enabled_tiers' must not be empty.")
    overlap = set(enabled).intersection(set(disabled))
    if overlap:
        errors.append(f"[MANIFEST_SCHEMA] Overlap between enabled and disabled tiers: {overlap}")

    # Validate intent files
    intent_dir = target_dir / "intent"
    for req_intent in REQUIRED_INTENT_FILES:
        int_f = intent_dir / req_intent
        if not int_f.exists() or len(int_f.read_text(encoding="utf-8").strip()) < 20:
            errors.append(f"[INTENT_MISSING] Required intent file missing or empty: {int_f.name}")

    # Validate styles
    styles_dir = target_dir / "styles"
    for req_style in ("quiet-ui-tokens.css", "overrides.css"):
        st_f = styles_dir / req_style
        if not st_f.exists() or len(st_f.read_text(encoding="utf-8").strip()) < 10:
            errors.append(f"[STYLE_MISSING] Required style file missing or empty: {st_f.name}")

    # Validate palette WCAG contrast
    palette = manifest.get("palette", {})
    errors.extend(verify_palette_contrast(palette))

    # Validate showcase HTML
    showcase_path = target_dir / "showcase.html"
    errors.extend(verify_showcase(showcase_path, enabled, disabled))

    # Validate immutability if requested
    if check_immutable:
        errors.extend(check_immutability(repo_root))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Quiet UI Customization")
    parser.add_argument("target", type=str, help="Target customization folder (e.g. customizations/brand-starter)")
    parser.add_argument("--check-immutability", action="store_true", help="Enforce self-immutability lock on starters & core")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    target_dir = (repo_root / args.target).resolve() if not Path(args.target).is_absolute() else Path(args.target)

    if not target_dir.exists():
        print(f"[FAIL] Target directory does not exist: {target_dir}", file=sys.stderr)
        return 1

    issues = verify_customization(target_dir, repo_root, check_immutable=args.check_immutability)
    if issues:
        print(f"[FAIL] Customization verification failed for {target_dir.name} ({len(issues)} issues):")
        for i in issues:
            print(f"  - {i}")
        return 1

    print(f"[PASS] Customization verified 100% clean for {target_dir.name} (immutability={args.check_immutability})!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
