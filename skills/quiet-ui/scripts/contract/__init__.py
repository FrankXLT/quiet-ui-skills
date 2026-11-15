# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v8.0 Visual Contract Verification Package."""

from .atlas_and_hud_gates import (
    check_gate_14_atlas_embedded,
    check_gate_14_atlas_standalone,
    check_gate_15_backplates_contrast,
    check_gate_15_field_of_regard,
    run_atlas_and_hud_gates,
)
from .constants import (
    ATLAS_TOTAL_CARDS,
    HUD_BACKPLATES,
    MAX_LINE_BUDGET,
    ROOT_FONT_SCALE_TARGETS,
    THEMES,
    TIERS,
    TOKEN_MIRROR_PATHS,
    VIEWPORTS,
)
from .flagship_craft_gates import (
    check_gate_18_desktop_tables,
    check_gate_19_svg_text_halos,
    check_gate_20_domain_layout,
    check_gate_21_substance_landmarks,
    run_flagship_craft_gates,
)
from .selenium_gates import (
    create_headless_driver,
    run_selenium_gates_1_to_13,
    select_tier,
    switch_to_outer,
    switch_to_portal,
)
from .static_gates import (
    run_static_gates,
    verify_docs_contract,
    verify_hygiene_static,
    verify_line_counts,
    verify_svg_static_rules,
    verify_tables_static_rules,
    verify_token_mirror_parity,
    verify_zero_important,
)

__all__ = [
    "ATLAS_TOTAL_CARDS",
    "HUD_BACKPLATES",
    "MAX_LINE_BUDGET",
    "ROOT_FONT_SCALE_TARGETS",
    "THEMES",
    "TIERS",
    "TOKEN_MIRROR_PATHS",
    "VIEWPORTS",
    "check_gate_14_atlas_embedded",
    "check_gate_14_atlas_standalone",
    "check_gate_15_backplates_contrast",
    "check_gate_15_field_of_regard",
    "check_gate_18_desktop_tables",
    "check_gate_19_svg_text_halos",
    "check_gate_20_domain_layout",
    "check_gate_21_substance_landmarks",
    "create_headless_driver",
    "run_atlas_and_hud_gates",
    "run_flagship_craft_gates",
    "run_selenium_gates_1_to_13",
    "run_static_gates",
    "select_tier",
    "switch_to_outer",
    "switch_to_portal",
    "verify_docs_contract",
    "verify_hygiene_static",
    "verify_line_counts",
    "verify_svg_static_rules",
    "verify_tables_static_rules",
    "verify_token_mirror_parity",
    "verify_zero_important",
]
