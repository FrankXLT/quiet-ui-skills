#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unified Quiet UI build & zero-drift verification entrypoint (--check)."""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from build_evidence_bench import render_bench_html  # noqa: E402
from build_showcase import WORLD_BUILDERS, build_showcase as compile_studio  # noqa: E402
from customizations.scripts.build_showcase import build_showcase as compile_starter  # noqa: E402

TOKEN_MIRRORS: tuple[str, ...] = (
    "skills/quiet-ui/tokens/quiet-ui-tokens.css",
    "customizations/personal-starter/styles/quiet-ui-tokens.css",
    "customizations/brand-starter/styles/quiet-ui-tokens.css",
)
LLMS_MIRRORS: tuple[str, ...] = ("docs/llms.txt", "skills/quiet-ui/llms.txt")
EVIDENCE_CSS_PARTS: tuple[str, ...] = (
    "src/css/00-layers-and-reset.css",
    "src/css/01-stage-and-containers.css",
    "src/css/03-pills-and-annunciators.css",
    "src/css/12-period-and-scope.css",
    "src/css/13-split-reader-dialog.css",
    "src/css/14-forms-and-states.css",
    "docs/bench/evidence-bench.css",
    "src/css/17-editorial-research-brief.css",
    "src/css/18-editorial-print-rules.css",
    "src/css/19-alarm-lifecycle.css",
    "src/css/20-wave2-archetypes.css",
)


def _extract_workbench_shell_css() -> str:
    raw = (REPO_ROOT / "src/css/02-nav-shells-and-drawers.css").read_text(encoding="utf-8")
    m = re.search(r"/\*\s*BEGIN_WORKBENCH_PANES\s*\*/(.*?)/\*\s*END_WORKBENCH_PANES\s*\*/", raw, flags=re.S)
    return f"@layer shell {{\n{m.group(1).strip()}\n}}" if m else ""


def _render_evidence_bundle_css() -> str:
    parts: list[str] = ["@layer reset, tokens, shell, archetypes, evidence, views, utilities;"]
    tok = (REPO_ROOT / "tokens" / "quiet-ui-tokens.css").read_text(encoding="utf-8")
    parts.append(f"@layer tokens {{\n{tok}\n}}")
    for rel in EVIDENCE_CSS_PARTS:
        raw = (REPO_ROOT / rel).read_text(encoding="utf-8")
        parts.append(re.sub(r"^@layer\s+[a-zA-Z0-9_,\s-]+;\s*", "", raw, flags=re.M))
    wb = _extract_workbench_shell_css()
    if wb:
        parts.append(wb)
    return re.sub(r"</\s*style", r"<\/style", "\n\n".join(parts), flags=re.I)


def _render_evidence_bundle_js() -> str:
    js_files = (
        "src/js/evidence-runtime.js",
        "src/js/quiet-svg-chart-layout.js",
        "src/js/quiet-time-binning.js",
        "src/js/echarts-layout-defaults.js",
        "src/js/quiet-cyclical-whiskers.js",
        "src/js/quiet-period-stepper.js",
        "src/js/quiet-sankey-layout.js",
        "src/js/quiet-card-export.js",
        "src/js/quiet-alarm-trace.js",
        "src/js/quiet-alarm-lifecycle.js",
        "src/js/quiet-wave2-svg.js",
        "src/js/quiet-wave2-interactions.js",
    )
    parts = [
        (REPO_ROOT / rel).read_text(encoding="utf-8")
        for rel in js_files
        if (REPO_ROOT / rel).exists()
    ]
    js = "\n\n".join(parts)
    return re.sub(r"</\s*script", r"<\/script", js, flags=re.I)


def compute_all_artifacts() -> dict[Path, bytes]:
    """Compute exact bytes for every mirrored token, bundle, showcase, and starter."""
    outputs: dict[Path, bytes] = {}
    tok_bytes = (REPO_ROOT / "tokens" / "quiet-ui-tokens.css").read_bytes()
    for rel in TOKEN_MIRRORS:
        outputs[REPO_ROOT / rel] = tok_bytes

    llms_bytes = (REPO_ROOT / "llms.txt").read_bytes()
    for rel in LLMS_MIRRORS:
        outputs[REPO_ROOT / rel] = llms_bytes

    assets_dir = REPO_ROOT / "skills" / "quiet-evidence" / "assets"
    outputs[assets_dir / "quiet-evidence-bundle.css"] = _render_evidence_bundle_css().encode("utf-8")
    outputs[assets_dir / "quiet-evidence-bundle.js"] = _render_evidence_bundle_js().encode("utf-8")

    outputs[REPO_ROOT / "docs" / "bench" / "evidence-bench.html"] = render_bench_html().encode("utf-8")

    studio_html = compile_studio(REPO_ROOT, list(WORLD_BUILDERS.keys()))
    studio_bytes = studio_html.encode("utf-8")
    outputs[REPO_ROOT / "quiet-ui-showcase.html"] = studio_bytes
    outputs[REPO_ROOT / "docs" / "index.html"] = studio_bytes

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        src_html = tmp_dir / "quiet-ui-showcase.html"
        src_html.write_bytes(studio_bytes)
        for starter in ("personal-starter", "brand-starter"):
            out_tmp = tmp_dir / f"{starter}.html"
            with contextlib.redirect_stdout(io.StringIO()):
                compile_starter(REPO_ROOT / "customizations" / starter, src_html, out_tmp, bundle=False)
            outputs[REPO_ROOT / "customizations" / starter / "showcase.html"] = out_tmp.read_bytes()

    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify all Quiet UI derived artifacts.")
    parser.add_argument("--check", action="store_true", help="Fail if any committed artifact has drifted.")
    args = parser.parse_args(argv)

    outputs = compute_all_artifacts()
    if args.check:
        drifted: list[str] = []
        for path, expected in outputs.items():
            rel = path.relative_to(REPO_ROOT).as_posix()
            if not path.is_file() or path.read_bytes() != expected:
                drifted.append(rel)
        if drifted:
            for rel in drifted:
                print(f"[DRIFT] {rel} is out of date; run: python3 -B scripts/build_all.py", file=sys.stderr)
            return 1
        print(f"[PASS] All {len(outputs)} generated artifacts match canonical sources (0 byte drift).")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"[OK] Synchronized and built {len(outputs)} artifacts cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
