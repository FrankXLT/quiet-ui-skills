#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.1 — Modular Multi-Domain Showcase Compiler."""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
VIEWS_DIR = REPO_ROOT / "src" / "views"
if str(VIEWS_DIR) not in sys.path:
    sys.path.insert(0, str(VIEWS_DIR))

from world_01_clinical import build_world_01  # noqa: E402
from world_02_cloud_cyber_ai import build_world_02  # noqa: E402
from world_03_industrial_grid import build_world_03  # noqa: E402
from world_04_civic_finance_stem import build_world_04  # noqa: E402
from world_05_physical_systems import build_world_05  # noqa: E402
from world_06_smart_home import build_world_06  # noqa: E402

WORLD_BUILDERS: dict[str, Callable[[Path], dict[str, Any]]] = {
    "01-clinical-icu-and-trials": build_world_01,
    "02-cloud-cyber-and-ai-ops": build_world_02,
    "03-industrial-grid-and-manufacturing": build_world_03,
    "04-civic-finance-and-stem-learning": build_world_04,
    "05-physical-systems-auto-and-aero": build_world_05,
    "06-smart-home-and-energy": build_world_06,
}


def bundle_stage_css(repo_root: Path) -> str:
    """Bundle layered tokens, core shells, pill grammar, evidence styles & view rules."""
    parts: list[str] = ["@layer reset, tokens, shell, archetypes, evidence, views, utilities;"]
    tok_f = repo_root / "tokens" / "quiet-ui-tokens.css"
    if tok_f.exists():
        parts.append(f"@layer tokens {{\n{tok_f.read_text(encoding='utf-8')}\n}}")
    for rel in (
        "src/css/00-layers-and-reset.css",
        "src/css/01-stage-and-containers.css",
        "src/css/02-nav-shells-and-drawers.css",
        "src/css/03-pills-and-annunciators.css",
        "src/css/05-evidence-stage.css",
        "src/css/12-period-and-scope.css",
        "src/css/13-split-reader-dialog.css",
        "src/css/14-forms-and-states.css",
        "src/css/06-stage-remediations.css",
        "src/css/07-world-01-views.css",
        "src/css/08-world-02-05-views.css",
        "src/css/09-m5-m6-m7-physics.css",
        "src/css/10-world-06-smart-home.css",
        "src/css/11-directional-and-planner.css",
    ):
        fpath = repo_root / rel
        if fpath.exists():
            txt = fpath.read_text(encoding="utf-8")
            if rel == "src/css/00-layers-and-reset.css":
                txt = re.sub(r"^@layer\s+[a-zA-Z0-9_,\s-]+;\s*", "", txt, flags=re.M)
            parts.append(txt)
    return "\n\n".join(parts)


def bundle_stage_js(repo_root: Path) -> str:
    """Bundle stage runtime, ECharts adapters, and per-domain interactions."""
    return "\n\n".join(
        (repo_root / rel).read_text(encoding="utf-8")
        for rel in (
            "src/js/evidence-runtime.js",
            "src/js/quiet-svg-chart-layout.js",
            "src/js/echarts-layers.js",
            "src/js/echarts-schedule-heatmap.js",
            "src/js/echarts-sankey-strip.js",
            "src/js/quiet-time-binning.js",
            "src/js/echarts-layout-defaults.js",
            "src/js/quiet-cyclical-whiskers.js",
            "src/js/quiet-period-stepper.js",
            "src/js/quiet-sankey-layout.js",
            "src/js/echarts-quiet-adapter.js",
            "src/js/world-01-interactions.js",
            "src/js/world-02-05-interactions.js",
            "src/js/world-06-interactions.js",
        )
        if (repo_root / rel).exists()
    )


def build_showcase(repo_root: Path, world_ids: list[str] | None = None) -> str:
    """Assemble standalone Quiet UI Studio HTML for selected domain(s)."""
    selected_ids = list(WORLD_BUILDERS.keys()) if world_ids is None else world_ids
    corpora_dir = repo_root / "content" / "corpora"
    worlds_meta: list[dict[str, Any]] = []
    all_templates: dict[str, str] = {}

    for wid in selected_ids:
        if wid not in WORLD_BUILDERS:
            raise ValueError(f"Unsupported or unregistered domain ID: {wid}")
        built = WORLD_BUILDERS[wid](corpora_dir)
        worlds_meta.append(built["world_meta"])
        all_templates.update(built["templates"])

    chrome_css = "\n\n".join(
        (repo_root / "src" / "css" / name).read_text(encoding="utf-8")
        for name in ("04-studio-portal.css", "04b-studio-landing.css")
    )
    studio_js = "\n\n".join(
        (repo_root / "src" / "js" / name).read_text(encoding="utf-8")
        for name in (
            "portal-resize.js",
            "studio-sheet.js",
            "studio-presets-and-rail.js",
            "studio-landing.js",
            "studio-portal.js",
        )
    )
    esc = lambda s: html_lib.escape(str(s), quote=True)
    world_options = "\n".join(
        f'          <option value="{esc(w["world_id"])}">{esc(w["world_label"])}</option>'
        for w in worlds_meta
    )
    first_views = worlds_meta[0]["views"] if worlds_meta else []
    view_options = "\n".join(
        f'        <option value="{esc(v["view_id"])}">{esc(v["option_label"])}</option>'
        for v in first_views
    )
    view_templates = "\n".join(
        f'  <template id="tpl-view-{esc(vid)}">\n{html}\n  </template>'
        for vid, html in all_templates.items()
    )
    manifest_json = json.dumps({"worlds": worlds_meta}, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e")

    shell_html = (repo_root / "src" / "chrome" / "studio-shell.html").read_text(encoding="utf-8")
    replacements = {
        "__CHROME_CSS__": chrome_css,
        "__WORLD_OPTIONS__": world_options,
        "__VIEW_OPTIONS__": view_options,
        "__PORTAL_CSS__": bundle_stage_css(repo_root),
        "__STAGE_JS__": bundle_stage_js(repo_root),
        "__V9_MANIFEST_JSON__": manifest_json,
        "__VIEW_TEMPLATES__": view_templates,
        "__STUDIO_JS__": studio_js,
    }
    pat = re.compile("|".join(re.escape(k) for k in replacements))
    return pat.sub(lambda m: replacements[m.group(0)], shell_html)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Quiet UI v9.5 Multi-Domain Showcase")
    parser.add_argument("--worlds", default="all", help="Comma-separated domain IDs or 'all' (default: all)")
    parser.add_argument("--output", default="quiet-ui-showcase.html", help="Output HTML file path")
    args = parser.parse_args()

    selected = list(WORLD_BUILDERS.keys()) if args.worlds == "all" else [w.strip() for w in args.worlds.split(",") if w.strip()]
    html_out = build_showcase(REPO_ROOT, selected)
    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"[OK] Built Quiet UI v9.5 showcase ({len(selected)} domain(s)) -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
