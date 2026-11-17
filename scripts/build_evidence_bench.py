#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 2 — Standalone 18-Specimen Evidence Qualification Bench Builder."""

from __future__ import annotations

import json
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
)


def _compile_bench_cards(spec_dir: Path) -> str:
    """Compile all 18 JSON specimens into grid article cards."""
    cards_html: list[str] = []
    for mod_code, fname in SPECIMEN_FILES:
        items = json.loads((spec_dir / fname).read_text(encoding="utf-8"))
        for spec in items:
            modality = detect_modality(spec)
            rigor = str((spec.get("metadata") or {}).get("rigor_level", "L2")).upper()
            fig_html = compile_spec(spec, rigor=rigor, medium="m2", theme="white")
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
  <title>Quiet UI v9.0 Phase 2 — Evidence Qualification Bench (18 Specimens)</title>
  <link rel="stylesheet" href="../../tokens/quiet-ui-tokens.css" />
  <link rel="stylesheet" href="../../src/css/00-layers-and-reset.css" />
  <link rel="stylesheet" href="../../src/css/01-stage-and-containers.css" />
  <link rel="stylesheet" href="../../src/css/06-b-pills-and-annunciators.css" />
  <link rel="stylesheet" href="./evidence-bench.css" />
</head>
<body>
  <a href="#bench-main" class="qe-skip-link">Skip to evidence specimens</a>
  <header class="qe-topbar">
    <div class="qe-topbar-inner">
      <div class="qe-brand">
        <span class="va-kicker">QUIET UI v9.0 PILLAR 2 · DETERMINISTIC EVIDENCE BENCH</span>
        <h1>Visual Metrology Qualification Bench (6 Modalities × L1 / L2 / L3)</h1>
      </div>
      <nav class="qe-controls" aria-label="Bench Controls">
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
          <label class="qe-ctrl-label" for="bench-medium-select">Medium</label>
          <select id="bench-medium-select" class="qe-select">
            <option value="m2">Screen (M2/M3)</option>
            <option value="m1">M1 Paper Sheet</option>
          </select>
        </div>
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-modality-filter">Modality</label>
          <select id="bench-modality-filter" class="qe-select">
            <option value="all">All (M1–M6)</option>
            <option value="M1">M1 · Scalars &amp; Gauges</option>
            <option value="M2">M2 · Tables &amp; Matrices</option>
            <option value="M3">M3 · Bitfields &amp; Registers</option>
            <option value="M4">M4 · Analytical Plots</option>
            <option value="M5">M5 · Waveforms &amp; Timing</option>
            <option value="M6">M6 · Schematics &amp; Topologies</option>
          </select>
        </div>
        <div class="qe-ctrl-group">
          <label class="qe-ctrl-label" for="bench-rigor-filter">Rigor</label>
          <select id="bench-rigor-filter" class="qe-select">
            <option value="all">All (L1–L3)</option>
            <option value="L1">L1 · Orientation</option>
            <option value="L2">L2 · Governance</option>
            <option value="L3">L3 · Physical, Clinical &amp; Metrological</option>
          </select>
        </div>
      </nav>
    </div>
  </header>
  <main id="bench-main" class="qe-bench-main" tabindex="-1">
    <section class="qe-bench-summary" aria-label="Qualification Overview">
      <div><strong>Zero-Dependency Compiler Verification</strong> · NAVAIR FTM-108 1-2-5 scales, mandatory 2..9 minor log decades, NIST SP 811 units, paint-order text halos, and Manhattan orthogonal routing.</div>
      <span id="bench-visible-count" class="qe-visible-count va-nums">18 of 18 specimens visible</span>
    </section>
    <section class="qe-bench-grid" aria-label="18 Benchmark Specimens">{cards_markup}</section>
  </main>
  <script src="../../src/js/evidence-runtime.js"></script>
  <script src="./bench.js"></script>
</body>
</html>
"""


def build_bench(out_path: Path | None = None) -> Path:
    """Compile all 18 JSON benchmark specimens into docs/bench/evidence-bench.html."""
    cards_markup = _compile_bench_cards(REPO_ROOT / "docs" / "bench" / "specimens")
    target = out_path or (REPO_ROOT / "docs" / "bench" / "evidence-bench.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_bench_shell(cards_markup), encoding="utf-8")
    return target


if __name__ == "__main__":
    written = build_bench()
    print(f"[OK] Built standalone qualification bench -> {written}")
