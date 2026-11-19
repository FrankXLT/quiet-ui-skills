#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 2 — Standalone 18-Specimen Evidence Qualification Bench Builder."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILER_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
if str(COMPILER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMPILER_SCRIPTS))

from compile_evidence import compile_spec, detect_modality  # noqa: E402
from compilers.tokens_and_scales import esc  # noqa: E402

SPECIMEN_FILES: tuple[tuple[str, str], ...] = (
    ("M1", "m1_scalars.json"),
    ("M2", "m2_tables.json"),
    ("M3", "m3_bitfields.json"),
    ("M4", "m4_plots.json"),
    ("M5", "m5_waveforms.json"),
    ("M6", "m6_schematics.json"),
    ("M6", "m6_systems_schematics.json"),
)
_SPECIMEN_PREFIX_RE = re.compile(r"^M[1-6]-L[1-3]:\s*")


def _compile_bench_cards(spec_dir: Path) -> str:
    """Compile all 21 JSON specimens into grid article cards."""
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
            is_wide = rigor == "L3" or modality in {"bitfield", "plot", "waveform", "schematic"} or (mod_code == "M2" and rigor == "L2")
            wide_cls = " qe-specimen-wide" if is_wide else ""
            cards_html.append(
                f'<article class="qe-specimen{wide_cls}" data-modality="{esc(mod_code)}" '
                f'data-schema-modality="{esc(modality)}" data-rigor="{esc(rigor)}">{fig_html}</article>'
            )
    return "".join(cards_html)


def _render_bench_shell(cards_markup: str) -> str:
    """Wrap compiled bench cards into accessible HTML5 shell."""
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="white" data-medium="m2">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <title>Quiet UI v9.0 — Evidence Component Library (21 Specimens)</title>
  <link rel="stylesheet" href="../../tokens/quiet-ui-tokens.css" />
  <link rel="stylesheet" href="../../src/css/00-layers-and-reset.css" />
  <link rel="stylesheet" href="../../src/css/01-stage-and-containers.css" />
  <link rel="stylesheet" href="../../src/css/06-b-pills-and-annunciators.css" />
  <link rel="stylesheet" href="./evidence-bench.css" />
</head>
<body>
  <a href="#bench-main" class="qe-skip-link">Skip to evidence components</a>
  <header class="qe-topbar">
    <div class="qe-topbar-inner">
      <div class="qe-brand">
        <span class="va-kicker">QUIET UI v9.0 · EVIDENCE COMPONENT LIBRARY</span>
        <h1>Evidence Component Library (21 Specimens × 4 Themes)</h1>
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
          <label class="qe-ctrl-label" for="bench-modality-filter">Component</label>
          <select id="bench-modality-filter" class="qe-select">
            <option value="all">All Types</option>
            <option value="M1">Scalars &amp; Gauges</option>
            <option value="M2">Tables &amp; Matrices</option>
            <option value="M3">Bitfields &amp; Registers</option>
            <option value="M4">Analytical Plots</option>
            <option value="M5">Waveforms &amp; Timing</option>
            <option value="M6">Schematics &amp; Systems</option>
          </select>
        </div>
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-rigor-filter">Detail</label>
          <select id="bench-rigor-filter" class="qe-select">
            <option value="all">All Levels</option>
            <option value="L1">Executive Summary</option>
            <option value="L2">Operational Spec</option>
            <option value="L3">Detailed Metrology</option>
          </select>
        </div>
      </nav>
    </div>
  </header>
  <main id="bench-main" class="qe-bench-main" tabindex="-1">
    <section class="qe-bench-summary" aria-label="Component Library Overview">
      <div><strong>Zero-Dependency Compiler Library</strong> · 1–2–5 scale ticks, mandatory log decades, SI/NIST units, paint-order text halos, and clean-room systems schematics (ITU-T Z.120, NASA SP-2016-6105, NRC NUREG-0492).</div>
      <span id="bench-visible-count" class="qe-visible-count va-nums">21 of 21 specimens visible</span>
    </section>
    <section class="qe-bench-grid" aria-label="21 Evidence Components">{cards_markup}</section>
  </main>
  <script src="../assets/vendor/echarts.min.js"></script>
  <script src="../../src/js/evidence-runtime.js"></script>
  <script src="../../src/v9/js/echarts-layers.js"></script>
  <script src="../../src/v9/js/echarts-quiet-adapter.js"></script>
  <script src="./bench.js"></script>
</body>
</html>
"""


def build_bench(out_path: Path | None = None) -> Path:
    """Compile all 21 JSON component specimens into docs/bench/evidence-bench.html."""
    cards_markup = _compile_bench_cards(REPO_ROOT / "docs" / "bench" / "specimens")
    target = out_path or (REPO_ROOT / "docs" / "bench" / "evidence-bench.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_bench_shell(cards_markup), encoding="utf-8")
    return target


if __name__ == "__main__":
    written = build_bench()
    print(f"[OK] Built Evidence Component Library (21 specimens) -> {written}")
