#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.7 — Standalone 50-Specimen 3-Pillar Component Library Builder."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILER_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
if str(COMPILER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMPILER_SCRIPTS))

from bench_alarm_specimen import compile_alarm_lifecycle_specimen  # noqa: E402
from bench_cyclical_specimen import compile_cyclical_whisker_specimen  # noqa: E402
from bench_data_contracts import contract_for_evidence_spec  # noqa: E402
from bench_forms_specimen import compile_forms_specimen  # noqa: E402
from bench_ui_specimens import compile_ui_bridge_specimens  # noqa: E402
from compile_evidence import compile_spec, detect_modality  # noqa: E402
from compilers.tokens_and_scales import esc  # noqa: E402

SPECIMEN_FILES: tuple[tuple[str, str], ...] = (
    ("M1", "m1_scalars.json"),
    ("M2", "m2_tables.json"),
    ("M3", "m3_bitfields.json"),
    ("M4", "m4_plots.json"),
    ("M4", "m4_everyday_charts.json"),
    ("M4", "m4_civic_research.json"),
    ("M5", "m5_waveforms.json"),
    ("M6", "m6_schematics.json"),
    ("M6", "m6_systems_schematics.json"),
    ("M6", "m6_everyday_topologies.json"),
)
_SPECIMEN_PREFIX_RE = re.compile(r"^(?:M[1-6]-L[1-3]|Specimen\s+\d+)\s*[:—-]\s*")


def _compile_bench_cards(spec_dir: Path) -> str:
    """Compile all 43 JSON specimens + 9 Pillar 1/3 interactive specimens + Specimens 43–44."""
    cards_html: list[str] = []
    for mod_code, fname in SPECIMEN_FILES:
        items = json.loads((spec_dir / fname).read_text(encoding="utf-8"))
        for spec in items:
            render_spec = dict(spec)
            meta = dict(spec.get("metadata") or {})
            if "title" in meta:
                meta["title"] = _SPECIMEN_PREFIX_RE.sub("", str(meta["title"]))
            render_spec["metadata"] = meta
            modality = detect_modality(render_spec)
            rigor = str(meta.get("rigor_level", "L2")).upper()
            fig_html = compile_spec(render_spec, rigor=rigor, medium="m2", theme="white")
            contract_html = contract_for_evidence_spec(render_spec)
            if fig_html.endswith("</figure>"):
                fig_html = fig_html[:-9] + contract_html + "</figure>"
                contract_tail = ""
            else:
                contract_tail = contract_html
            is_wide = rigor == "L3" or modality in {"table", "bitfield", "plot", "waveform", "schematic"} or mod_code == "M2"
            wide_cls = " qe-specimen-wide" if is_wide else ""
            eff_mod = "M2" if modality == "table" else mod_code
            cards_html.append(
                f'<article class="qe-specimen{wide_cls}" data-modality="{esc(eff_mod)}" '
                f'data-schema-modality="{esc(modality)}" data-rigor="{esc(rigor)}">{fig_html}{contract_tail}</article>'
            )
    cards_html.append(compile_ui_bridge_specimens())
    cards_html.append(compile_cyclical_whisker_specimen())
    cards_html.append(compile_forms_specimen())
    cards_html.append(compile_alarm_lifecycle_specimen())
    return "".join(cards_html)


def _bundle_bench_css() -> str:
    """Bundle layered tokens, shell, pills, bench, and view styles inline for GitHub Pages."""
    parts: list[str] = ["@layer reset, tokens, shell, archetypes, evidence, views, utilities;"]
    tok_f = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
    if tok_f.exists():
        parts.append(f"@layer tokens {{\n{tok_f.read_text(encoding='utf-8')}\n}}")
    for rel in (
        "src/css/00-layers-and-reset.css",
        "src/css/01-stage-and-containers.css",
        "src/css/03-pills-and-annunciators.css",
        "docs/bench/evidence-bench.css",
        "src/css/11-directional-and-planner.css",
        "src/css/12-period-and-scope.css",
        "src/css/13-split-reader-dialog.css",
        "src/css/14-forms-and-states.css",
        "src/css/17-editorial-research-brief.css",
        "src/css/18-editorial-print-rules.css",
        "src/css/19-alarm-lifecycle.css",
    ):
        fpath = REPO_ROOT / rel
        if fpath.exists():
            txt = re.sub(r"^@layer\s+[a-zA-Z0-9_,\s-]+;\s*", "", fpath.read_text(encoding="utf-8"), flags=re.M)
            parts.append(txt)
    wb_raw = (REPO_ROOT / "src/css/02-nav-shells-and-drawers.css").read_text(encoding="utf-8")
    wb_m = re.search(r"/\*\s*BEGIN_WORKBENCH_PANES\s*\*/(.*?)/\*\s*END_WORKBENCH_PANES\s*\*/", wb_raw, flags=re.S)
    if wb_m:
        parts.append(f"@layer shell {{\n{wb_m.group(1).strip()}\n}}")
    return re.sub(r"</\s*style", r"<\/style", "\n\n".join(parts), flags=re.I)


def _bundle_bench_js() -> str:
    """Bundle bench runtime, ECharts adapters, and filter controls inline for GitHub Pages."""
    parts = [
        (REPO_ROOT / rel).read_text(encoding="utf-8")
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
            "src/js/quiet-card-export.js",
            "src/js/echarts-quiet-adapter.js",
            "src/js/quiet-alarm-trace.js",
            "src/js/quiet-alarm-lifecycle.js",
            "docs/bench/bench.js",
        )
        if (REPO_ROOT / rel).exists()
    ]
    return re.sub(r"</\s*script", r"<\/script", "\n\n".join(parts), flags=re.I)


def _render_bench_shell(cards_markup: str) -> str:
    """Wrap compiled bench cards into accessible HTML5 shell."""
    css_bundle = _bundle_bench_css()
    js_bundle = _bundle_bench_js()
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="white" data-medium="m2">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <title>Quiet UI v9.7 — Component Library (50 Building Blocks)</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3.5' fill='%230F172A'/%3E%3Cpath d='M8 2.4 13 5.2 8 8 3 5.2 8 2.4Z' fill='none' stroke='%2338BDF8' stroke-width='1.4' stroke-linejoin='round'/%3E%3Cpath d='M3 8l5 2.8L13 8M3 10.8 8 13.6l5-2.8' fill='none' stroke='%23BAE6FD' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E" />
  <style id="qe-bench-styles">
{css_bundle}
  </style>
</head>
<body>
  <a href="#bench-main" class="qe-skip-link">Skip to building blocks</a>
  <header class="qe-topbar">
    <div class="qe-topbar-inner">
      <div class="qe-brand">
        <span class="va-kicker">QUIET UI v9.7 · READY-TO-USE BUILDING BLOCKS</span>
        <h1>Component Library (50 Building Blocks · 4 Themes)</h1>
      </div>
      <nav class="qe-controls" aria-label="Component Library Controls">
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-theme-select">Theme</label>
          <select id="bench-theme-select" class="qe-select">
            <option value="white">White</option>
            <option value="paper">Paper</option>
            <option value="dark-paper">Dark-Paper</option>
            <option value="dark">Dark</option>
          </select>
        </div>
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-medium-select">Format</label>
          <select id="bench-medium-select" class="qe-select">
            <option value="m2">Screen Layout</option>
            <option value="m1">Print Sheet</option>
          </select>
        </div>
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-modality-filter">Category</label>
          <select id="bench-modality-filter" class="qe-select">
            <option value="all">All Categories</option>
            <option value="M1">Key Numbers &amp; Gauges</option>
            <option value="M2">Tables &amp; Comparisons</option>
            <option value="M3">Hardware Registers</option>
            <option value="M4">Charts, Timelines &amp; Heatmaps</option>
            <option value="M5">Live Signals &amp; Waveforms</option>
            <option value="M6">System Diagrams</option>
            <option value="UI">Forms, Menus &amp; Controls</option>
            <option value="BR">Summaries &amp; Checklists</option>
          </select>
        </div>
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-rigor-filter">Detail</label>
          <select id="bench-rigor-filter" class="qe-select">
            <option value="all">All Detail Levels</option>
            <option value="L1">Quick Summary</option>
            <option value="L2">Standard Detail</option>
            <option value="L3">Full Technical Detail</option>
          </select>
        </div>
      </nav>
    </div>
  </header>
  <main id="bench-main" class="qe-bench-main" tabindex="-1">
    <section class="qe-bench-summary" aria-label="Component Library Overview">
      <div><strong>50 Ready-to-Use Building Blocks</strong> · Clean forms, helpful empty-state messages, undo notifications, menus, summary cards, date pickers, readable charts, timelines, signal graphs, 4-phase alarm lifecycles, and system diagrams — each tested across all 4 light, paper, and dark themes.</div>
      <span id="bench-visible-count" class="qe-visible-count va-nums">50 of 50 specimens visible</span>
    </section>
    <section class="qe-bench-grid" aria-label="50 Building Blocks">{cards_markup}</section>
  </main>
  <script src="../assets/vendor/echarts.min.js"></script>
  <script id="qe-bench-runtime">
{js_bundle}
  </script>
</body>
</html>
"""


def render_bench_html() -> str:
    """Compile all 50 3-pillar component specimens and return the full HTML string."""
    cards_markup = _compile_bench_cards(REPO_ROOT / "docs" / "bench" / "specimens")
    return _render_bench_shell(cards_markup)


def build_bench(out_path: Path | None = None) -> Path:
    """Compile all 50 3-pillar component specimens into docs/bench/evidence-bench.html."""
    target = out_path or (REPO_ROOT / "docs" / "bench" / "evidence-bench.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_bench_html(), encoding="utf-8")
    return target


if __name__ == "__main__":
    written = build_bench()
    print(f"[OK] Built 3-Pillar Component Library (50 specimens) -> {written}")
