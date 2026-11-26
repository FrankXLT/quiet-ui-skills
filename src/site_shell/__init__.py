# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.8.0 zero-dependency static project-site shell package."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

from .config import load_site_config


def _bind_optional(module_rel: str, attr: str) -> Any:
    """Resolve an optional sibling export eagerly when present, or lazily on call."""
    pkg = __package__ or __name__
    if importlib.util.find_spec(module_rel, pkg) is not None:
        mod = importlib.import_module(module_rel, pkg)
        return getattr(mod, attr)

    def _lazy_wrapper(*args: Any, **kwargs: Any) -> Any:
        mod = importlib.import_module(module_rel, pkg)
        return getattr(mod, attr)(*args, **kwargs)

    _lazy_wrapper.__name__ = attr
    _lazy_wrapper.__qualname__ = attr
    return _lazy_wrapper


compile_markdown_docs = _bind_optional(".markdown_docs", "compile_markdown_docs")
render_social_svg = _bind_optional(".social_card", "render_social_svg")
render_social_png = _bind_optional(".social_card", "render_social_png")
build_project_site = _bind_optional(".builder", "build_project_site")
render_demo_return_bar = _bind_optional(".builder", "render_demo_return_bar")
render_demo_chrome_css = _bind_optional(".builder", "render_demo_chrome_css")

__all__ = [
    "build_project_site",
    "compile_markdown_docs",
    "load_site_config",
    "render_demo_chrome_css",
    "render_demo_return_bar",
    "render_social_png",
    "render_social_svg",
]
