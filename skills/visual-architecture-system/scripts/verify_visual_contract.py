#!/usr/bin/env python3
"""
Automated Visual Architecture Contract Verifier (v4.6 - 17-Tier Continuum + Pure White Default + Top Studio Bar & OA Swatches)
License: GNU AGPLv3 + Section 7 NOTICE (with Unconditional Commercial UI Output Exemption;
         tokens/quiet-ui-tokens.css dual-licensed MIT)
Usage:
  python3 scripts/verify_visual_contract.py <path_to_html_file> [--tier DOC-1|...|APP-4|APP-5|APP-TREE|HA-1|HA-2|HA-3|ALL]
"""

import re
import sys
from pathlib import Path

REQUIRED_SECTION_IDS = {
    "DOC-1": "tier-doc-1",
    "DOC-2": "tier-doc-2",
    "DOC-3": "tier-doc-3",
    "DOC-4B": "tier-doc-4b",
    "DOC-4A": "tier-doc-4a",
    "BRIDGE-1": "tier-bridge-1",
    "DECK-1": "tier-deck-1",
    "BRIDGE-2": "tier-bridge-2",
    "APP-2": "tier-app-2",
    "APP-1": "tier-app-1",
    "APP-4": "tier-app-4",
    "APP-3": "tier-app-3",
    "APP-5": "tier-app-5",
    "APP-TREE": "tier-app-tree",
    "HA-1": "tier-ha-1",
    "HA-2": "tier-ha-2",
    "HA-3": "tier-ha-3",
}

FORBIDDEN_PII_PATTERNS = (
    r"\bfr\x61nk\b",
    r"\bfr\x61nkxlt\b",
    r"\bk\x61tzenberger\b",
    r"\bk\x69m\b",
    r"\bev\x61\b",
    r"\beliz\x61beth\s+hills\b",
    r"\bser\x65nity\s*creek\b",
    r"\bser\x65nitycreek\b",
    r"\bexp\x61nse\.l\x61n\b",
    r"\bds\x31821\b",
    r"/home/fr\x61nkxlt",
    r"\bmt\x61sker\b",
    r"\bchr\x6fnos\b",
    r"\bfk\s*·",
)

FORBIDDEN_EMOJIS = ("✨", "⚡", "☀", "🛡", "●", "&#10024;")


def verify_html(file_path: Path, tier: str = "ALL") -> list[str]:
    errors: list[str] = []
    if not file_path.exists():
        return [f"File not found: {file_path}"]

    content = file_path.read_text(encoding="utf-8")

    # 0. Automated Zero-PII & Internal Homelab Leak Gate
    for pat in FORBIDDEN_PII_PATTERNS:
        m = re.search(pat, content, flags=re.IGNORECASE)
        if m:
            errors.append(f"[PII_VIOLATION] Forbidden personal/internal identifier matched: '{m.group(0)}'")

    # 0B. Zero-Emoji & Font Awesome 6 Vector Icon Contract (v4.6)
    for emoji in FORBIDDEN_EMOJIS:
        if emoji in content:
            errors.append(f"[EMOJI_VIOLATION] Banned unicode emoji/entity found: {emoji!r}. Use Font Awesome 6 (fa-solid).")
    for fa_tok in ("font-awesome", "fa-solid", "va-hamburger-btn", "toggleLeftRailCollapse"):
        if fa_tok not in content:
            errors.append(f"[ICON_NAV_VIOLATION] Missing v4.6 Font Awesome / rail-collapse token: '{fa_tok}'.")

    # 1. Offline Font & Tabular Numeral Contract
    if "fonts.googleapis.com" in content or "fonts.gstatic.com" in content:
        errors.append("[OFFLINE_VIOLATION] External Google Fonts link detected. Use native OS font stacks.")
    if "tabular-nums" not in content:
        errors.append("[TYPOGRAPHY_VIOLATION] Missing 'tabular-nums' numeric discipline in CSS.")

    # 2. Zero-Hotkey & v4.6 Top Studio Bar + OA Sidebar Swatches Contract
    if re.search(r"addEventListener\(\s*['\"]keydown['\"]", content):
        errors.append("[HOTKEY_VIOLATION] Global keydown listener detected. Theme/density/tier switching must use UI controls.")
    if 'id="va-topbar"' in content or 'class="continuum-topbar"' in content:
        errors.append("[TOPBAR_VIOLATION] Legacy #va-topbar / .continuum-topbar is forbidden.")
    for tok in (
        'id="va-floating-dock"',
        'id="va-studio-tier-select"',
        'id="va-display-trigger"',
        'id="va-dock-nav-cycle"',
        'id="va-display-popover"',
        'class="va-oa-sidebar-footer',
        'id="va-drawer-scrim"',
    ):
        if tok not in content:
            errors.append(f"[STUDIO_BAR_VIOLATION] Missing v4.6 Top Studio Bar / OA Swatches token: {tok}")

    # 3. 4-Mode Color Theme (S1 Pure White Default), Density Dial (d1..d4), 5-Stop Corner Dial, C3 Expressive & N0-N4 Nav Shell
    if 'data-theme="white"' not in content[:600]:
        errors.append('[WHITE_DEFAULT_VIOLATION] <html> tag must default to data-theme="white" (S1 Pure White).')
    for theme_attr in ('data-theme="white"', 'data-theme="paper"', 'data-theme="dark-paper"', 'data-theme="dark"'):
        if theme_attr not in content:
            errors.append(f"[THEME_ENGINE_VIOLATION] Missing CSS selector for {theme_attr} in 4-mode color theme engine.")
    for density_attr in ('data-density="d1"', 'data-density="d2"', 'data-density="d3"', 'data-density="d4"'):
        if density_attr not in content:
            errors.append(f"[DENSITY_ENGINE_VIOLATION] Missing CSS selector for {density_attr} in 4-level compactness dial.")
    for corner_tok in ('id="corners-switcher-bar"', 'data-corners="sharp"', 'data-corners="subtle"', 'data-corners="rounded"', 'data-corners="soft"', "--radius-card", "--radius-inner", "--radius-pill", "setCornerStyle"):
        if corner_tok not in content:
            errors.append(f"[CORNER_DIAL_VIOLATION] Missing v4.6 5-stop Corner Radius Dial token: '{corner_tok}'.")
    for c3_tok in ('data-color-policy="c3"', "--tint-indigo-bg", "va-icon-well", "va-pill-btn", "va-seg-pills"):
        if c3_tok not in content:
            errors.append(f"[EXPRESSIVE_C3_VIOLATION] Missing v4.6 C3 Modern Expressive / Pill Affordance token: '{c3_tok}'.")
    for media_tok in (
        "@media (min-width: 1100px)",
        "@media (min-width: 641px) and (max-width: 1099px)",
        "@media (max-width: 640px)",
        'id="va-live-viewport-readout"',
        "updateViewportReadout",
        "is-drawer-open",
        ':root[data-effective-nav="n1"]',
        ':root[data-effective-nav="n4"]',
    ):
        if media_tok not in content:
            errors.append(f"[MEDIA_RESPONSIVE_VIOLATION] Missing native @media responsive token: '{media_tok}'.")
    if "@container va-stage" in content or "container-name: va-stage" in content:
        errors.append("[CONTAINER_QUERY_COLLISION] Legacy @container va-stage rules are forbidden; use native @media breakpoints.")
    if "fa-brackets-curly" in content:
        errors.append("[FA_PRO_VIOLATION] Font Awesome Pro-only icon 'fa-brackets-curly' is forbidden; use Free 'fa-code'.")
    if 'id="res-popover-bar"' in content:
        errors.append("[FAKE_RESOLUTION_VIOLATION] Legacy #res-popover-bar is forbidden; use #va-live-viewport-readout and native @media queries.")
    if "data-nav-shell" not in content or "setNavShell" not in content or "cycleNavShell" not in content:
        errors.append("[NAV_SHELL_VIOLATION] Missing N0-N4 Native Navigation Shell topology switcher.")

    # 4. App Shell Essentials Contract
    for meta_tok in ('id="va-account-pod"', "va-account-popover", "va-pulse-drawer", "va-tripwire-banner", "va-mobile-thumb-bar"):
        if meta_tok not in content:
            errors.append(f"[APP_SHELL_VIOLATION] Missing App Shell Essentials token '{meta_tok}'.")

    # 5. Tier Presence & Structural Checks
    tiers_to_check = list(REQUIRED_SECTION_IDS.keys()) if tier == "ALL" else [tier]
    for t in tiers_to_check:
        sec_id = REQUIRED_SECTION_IDS.get(t)
        if sec_id and f'id="{sec_id}"' not in content:
            errors.append(f"[TIER_MISSING] Missing required section container id='{sec_id}' for tier {t}.")

    if tier in ("ALL", "DOC-1", "DOC-2", "DOC-3", "DOC-4A", "DOC-4B"):
        if "border-radius: 0px !important" not in content:
            errors.append("[EDITORIAL_VIOLATION] Family A must enforce 'border-radius: 0px !important' under auto/sharp corners.")
        for mm_tok in ("va-mermaid-figure", "va-mermaid-svg", "va-mermaid-code", "toggleMermaidSource"):
            if mm_tok not in content:
                errors.append(f"[MERMAID_VIOLATION] Missing theme-aware Mermaid diagram token '{mm_tok}'.")

    if tier in ("ALL", "BRIDGE-1"):
        for s_id in ("b1-slider-span", "b1-slider-temp", "b1-slider-bw"):
            if s_id not in content:
                errors.append(f"[BRIDGE1_VIOLATION] Missing interactive parametric input '{s_id}'.")

    if tier in ("ALL", "BRIDGE-2"):
        if "t5-table" not in content or "b2-spark-strip" not in content:
            errors.append("[BRIDGE2_VIOLATION] Missing .t5-table or .b2-spark-strip in Bridge-2.")

    if tier in ("ALL", "APP-1"):
        for req_cls in ("app1-shell", "app1-row", "app1-inspector"):
            if req_cls not in content:
                errors.append(f"[APP1_VIOLATION] Missing required class '.{req_cls}' in App-1.")

    if tier in ("ALL", "APP-4"):
        for req_cls in ("app4-focus-hero", "app4-staging-tray", "app4-command-composer", "app4-token-preview", "app4-continuity-strip"):
            if req_cls not in content:
                errors.append(f"[APP4_VIOLATION] Missing v4.6 Temporal Workbench class '.{req_cls}' in App-4.")

    if tier in ("ALL", "APP-3"):
        for layer_cls in ("bento-layer1-header", "bento-layer2-hero", "bento-layer3-proof", "bento-layer4-footer"):
            if layer_cls not in content:
                errors.append(f"[APP3_VIOLATION] Missing mandatory 4-layer Bento class '.{layer_cls}'.")

    if tier in ("ALL", "APP-5"):
        for req_cls in ("app5-hero-grid", "app5-readiness-ring", "app5-day-timeline", "life1-stepping-stones", "--state-anchor", "--state-buffer", "--state-held"):
            if req_cls not in content:
                errors.append(f"[APP5_VIOLATION] Missing v4.6 Restorative Companion token '{req_cls}' in App-5.")

    if tier in ("ALL", "APP-TREE"):
        for req_cls in ("va-tree-workbench", "va-tree-pane", "va-tree-node", "va-tree-guide", "va-tree-inspector", "setTreeMode", "switchTreeTab", "toggleAppTreePane"):
            if req_cls not in content:
                errors.append(f"[APPTREE_VIOLATION] Missing v4.6 Tree/Schema Explorer token '{req_cls}' in App-Tree.")

    if tier in ("ALL", "HA-1"):
        for req_cls in ("ha1-stage", "ha1-monet-img", "monet_water_lilies_1906.jpg", "ha1-glass-hud", "ha1-giant-clock"):
            if req_cls not in content:
                errors.append(f"[HA1_VIOLATION] Missing required HA-1 Monet/glass token '{req_cls}'.")

    if tier in ("ALL", "HA-2"):
        for req_cls in ("ha2-left-rail", "ha2-room-card", "ha2-slider-tile", "ha2-right-dock", "ha2-room-inspector"):
            if req_cls not in content:
                errors.append(f"[HA2_VIOLATION] Missing required HA-2 wall-matrix token '{req_cls}'.")

    if tier in ("ALL", "HA-3"):
        for req_cls in ("ha3-split-body", "ha3-fold-crease", "ha3-tile-grid", "ha3-thumb-dock", "ha3-detail-inspector"):
            if req_cls not in content:
                errors.append(f"[HA3_VIOLATION] Missing required HA-3 companion app token '{req_cls}'.")
        if 'id="ha3-device-frame"' in content:
            errors.append("[HA3_BOX_VIOLATION] Fake hardware bezel #ha3-device-frame is forbidden; HA-3 must fill 100% viewport width.")

    return errors


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 verify_visual_contract.py <html_file> [--tier TIER_ID|ALL]")
        sys.exit(2)

    html_file = Path(sys.argv[1])
    tier_arg = "ALL"
    if "--tier" in sys.argv:
        idx = sys.argv.index("--tier")
        if idx + 1 < len(sys.argv):
            tier_arg = sys.argv[idx + 1].upper()

    errs = verify_html(html_file, tier_arg)
    if errs:
        print(f"[FAIL] Visual Architecture Contract Verification failed ({len(errs)} issues):")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"[PASS] 100% of Visual Architecture v4.6 checks succeeded for '{html_file}' (Tier={tier_arg}).")
        sys.exit(0)


if __name__ == "__main__":
    main()
