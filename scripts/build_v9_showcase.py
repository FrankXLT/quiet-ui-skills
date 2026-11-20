#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 — Modular Multi-World Showcase Compiler."""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
V9_VIEWS_DIR = REPO_ROOT / "src" / "v9" / "views"
if str(V9_VIEWS_DIR) not in sys.path:
    sys.path.insert(0, str(V9_VIEWS_DIR))

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


def bundle_v9_stage_css(repo_root: Path) -> str:
    """Bundle layered tokens, core shells, pill grammar, evidence styles & v9 remediations."""
    parts: list[str] = ["@layer reset, tokens, shell, archetypes, views, evidence, utilities;"]
    tok_f = repo_root / "tokens" / "quiet-ui-tokens.css"
    if tok_f.exists():
        parts.append(f"@layer tokens {{\n{tok_f.read_text(encoding='utf-8')}\n}}")
    for rel in (
        "src/css/00-layers-and-reset.css",
        "src/css/01-stage-and-containers.css",
        "src/css/02-nav-shells-and-drawers.css",
        "src/css/06-b-pills-and-annunciators.css",
        "src/v9/css/02-evidence-stage.css",
        "src/v9/css/03-stage-remediations.css",
        "src/v9/css/04-world-01-views.css",
        "src/v9/css/05-world-02-05-views.css",
        "src/v9/css/06-m5-m6-m7-physics.css",
        "src/v9/css/07-world-06-smart-home.css",
        "src/v9/css/08-directional-and-planner.css",
    ):
        fpath = repo_root / rel
        if fpath.exists():
            txt = fpath.read_text(encoding="utf-8")
            if rel == "src/css/00-layers-and-reset.css":
                txt = txt.replace("@layer reset, tokens, shell, archetypes, utilities;", "")
            parts.append(txt)
    return "\n\n".join(parts)


def bundle_v9_stage_js(repo_root: Path) -> str:
    return "\n\n".join(
        (repo_root / rel).read_text(encoding="utf-8")
        for rel in (
            "src/js/evidence-runtime.js",
            "src/v9/js/echarts-layers.js",
            "src/v9/js/echarts-schedule-heatmap.js",
            "src/v9/js/echarts-sankey-strip.js",
            "src/v9/js/echarts-quiet-adapter.js",
            "src/v9/js/world-01-interactions.js",
            "src/v9/js/world-02-05-interactions.js",
            "src/v9/js/world-06-interactions.js",
        )
        if (repo_root / rel).exists()
    )


def build_v9_showcase(repo_root: Path, world_ids: list[str]) -> str:
    """Assemble standalone Quiet UI v9.0 Studio Portal HTML for selected world(s)."""
    corpora_dir = repo_root / "content" / "corpora"
    worlds_meta: list[dict[str, Any]] = []
    all_templates: dict[str, str] = {}

    for wid in world_ids:
        if wid not in WORLD_BUILDERS:
            raise ValueError(f"Unsupported or unregistered world ID: {wid}")
        built = WORLD_BUILDERS[wid](corpora_dir)
        worlds_meta.append(built["world_meta"])
        all_templates.update(built["templates"])

    chrome_css = (repo_root / "src" / "v9" / "css" / "01-studio-portal-v9.css").read_text(encoding="utf-8")
    studio_js = "\n\n".join(
        (repo_root / "src" / "v9" / "js" / name).read_text(encoding="utf-8")
        for name in ("portal-resize-v9.js", "studio-sheet-v9.js", "studio-portal-v9.js")
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

    shell_html = (repo_root / "src" / "v9" / "chrome" / "studio-shell-v9.html").read_text(encoding="utf-8")
    replacements = {
        "__CHROME_CSS__": chrome_css,
        "__WORLD_OPTIONS__": world_options,
        "__VIEW_OPTIONS__": view_options,
        "__PORTAL_CSS__": bundle_v9_stage_css(repo_root),
        "__STAGE_JS__": bundle_v9_stage_js(repo_root),
        "__V9_MANIFEST_JSON__": manifest_json,
        "__VIEW_TEMPLATES__": view_templates,
        "__STUDIO_JS__": studio_js,
    }
    pat = re.compile("|".join(re.escape(k) for k in replacements))
    return pat.sub(lambda m: replacements[m.group(0)], shell_html)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Quiet UI v9.0 Multi-Domain Showcase")
    parser.add_argument("--worlds", default="all", help="Comma-separated world IDs or 'all' (default: all)")
    parser.add_argument("--output", default="quiet-ui-showcase.html", help="Output HTML file path")
    args = parser.parse_args()

    selected = list(WORLD_BUILDERS.keys()) if args.worlds == "all" else [w.strip() for w in args.worlds.split(",") if w.strip()]
    html_out = build_v9_showcase(REPO_ROOT, selected)
    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"[OK] Built Quiet UI v9.0 showcase ({len(selected)} world(s)) -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
