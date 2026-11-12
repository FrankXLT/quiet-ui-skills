# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Showcase v7.1 In-Situ Diagrams and Blending Package.

Provides editorial, interactive, and workspace SVG figure generators and an
idempotent showcase HTML transformer.
"""

from .apply_in_situ import apply_in_situ
from .figures_editorial import (
    render_doc1_figure,
    render_doc2_figure,
    render_doc3_figure,
    render_doc4a_figure,
    render_doc4b_figure,
)
from .figures_interactive import render_deck1_switcher_and_slides
from .figures_workspace import (
    render_app3_tile4_proof,
    render_app3_tile5_proof,
    render_apptree_er_figure,
)

__all__ = [
    "apply_in_situ",
    "render_doc1_figure",
    "render_doc2_figure",
    "render_doc3_figure",
    "render_doc4a_figure",
    "render_doc4b_figure",
    "render_deck1_switcher_and_slides",
    "render_app3_tile4_proof",
    "render_app3_tile5_proof",
    "render_apptree_er_figure",
]
