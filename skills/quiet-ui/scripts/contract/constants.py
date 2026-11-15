# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v8.0 Visual Contract Constants & Tolerances."""

from __future__ import annotations

# Canonical Viewport Presets: (width, height)
VIEWPORTS: list[tuple[int, int]] = [
    (390, 844),    # Mobile Portrait
    (820, 1180),   # Foldable / Tablet
    (1920, 1080),  # Desktop 1080p
    (2560, 1440),  # Desktop 1440p
    (3840, 2160),  # Desktop 4K
]

VIEWPORT_NAMES: dict[str, tuple[int, int]] = {
    "mobile": (390, 844),
    "fold": (820, 1180),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4k": (3840, 2160),
}

# 16 Canonical Continuum Tiers
TIERS: list[str] = [
    "doc-1", "doc-2", "doc-3", "doc-4b", "doc-4a",
    "bridge-1", "deck-1", "bridge-2",
    "app-2", "app-1", "app-4", "app-3", "app-5", "app-tree",
    "hud-1", "ctrl-1",
]

# SHA-256 Parity Token Mirror Targets
TOKEN_MIRROR_PATHS: list[str] = [
    "tokens/quiet-ui-tokens.css",
    "skills/quiet-ui/tokens/quiet-ui-tokens.css",
    "docs/atlas/quiet-ui-tokens.css",
    "customizations/personal-starter/styles/quiet-ui-tokens.css",
    "customizations/brand-starter/styles/quiet-ui-tokens.css",
]

# Surface Color Themes
THEMES: tuple[str, ...] = ("white", "paper", "dark-paper", "dark")

# Line budgets across repo (v8.2 Rebalanced Budgets)
MAX_LINE_BUDGET: int = 350
CODE_LINE_BUDGET: int = 350
REFERENCES_LINE_BUDGET: int = 450
TIER_HTML_LINE_RANGE: tuple[int, int] = (260, 550)
TIER_HTML_FLOOR: int = 240
EXCLUDED_LINE_BUDGET_EXACT: set[str] = {
    "quiet-ui-showcase.html",
    "docs/index.html",
}

# Fluid 4K Root Font Scale targets: width -> (expected_px, tolerance_px)
ROOT_FONT_SCALE_TARGETS: dict[int, tuple[float, float]] = {
    390: (16.0, 0.2),
    820: (16.0, 0.2),
    1920: (17.2, 0.3),
    2560: (18.8, 0.3),
    3840: (22.0, 0.3),
}

# Editorial Prose Max Width Constraints (doc-1..doc-4a)
PROSE_MAX_WIDTH: dict[int, float] = {
    1920: 960.0,
    3840: 1260.0,
}

# Forbidden PII Patterns
FORBIDDEN_PII_PATTERNS: tuple[str, ...] = (
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
    r"\b192\.168\.\d{1,3}\.\d{1,3}\b",
)

# Forbidden Unicode Emojis & Entities
FORBIDDEN_EMOJIS: tuple[str, ...] = (
    "✨", "⚡", "☀", "🛡", "●", "&#10024;", "🚀", "💡", "🔥", "⚠️", "❌", "✅",
)

# Forbidden Prompt Meta Strings in visible content
FORBIDDEN_META_STRINGS: tuple[str, ...] = (
    "EXPECTED TICK",
    "PROPORTIONAL BARS",
    "QUIET COCKPIT GATE",
    "FROSTED HUD",
    "CREASE-AWARE",
)

# Forbidden Brand Names in Documentation
FORBIDDEN_BRANDS: tuple[str, ...] = (
    "Fitbit",
    "Monarch",
    "Portainer",
    "OpenTodo",
    "AI Hero",
    "OA Workbench",
)

# Atlas Diagram Family Counts (Family 1..5 = 45 total)
ATLAS_FAMILY_EXPECTED_COUNTS: dict[str, int] = {
    "systems": 11,
    "data": 6,
    "flows": 9,
    "strategy": 8,
    "charts": 11,
}
ATLAS_TOTAL_CARDS: int = 45

# HUD Backplates for Gate 15
HUD_BACKPLATES: tuple[str, ...] = ("earthrise", "daylight", "lowlight")
