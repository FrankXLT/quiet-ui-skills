#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Deterministic Evidence Compiler CLI & Python API.

Usage:
  python3 -B skills/quiet-evidence/scripts/compile_evidence.py spec.json [--rigor L1|L2|L3] [--medium m1..m7] [--theme white|paper|dark-paper|dark]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from compilers import (  # noqa: E402
    compile_bitfield,
    compile_plot,
    compile_scalar,
    compile_schematic,
    compile_table,
    compile_waveform,
)
from compilers.civic_matrix_and_export import wrap_takeaway_card  # noqa: E402
from compilers.echarts_adapter import render_ecosystem_drawer  # noqa: E402
from compilers.tokens_and_scales import esc  # noqa: E402

URN_PREFIX = "urn:quiet-ui:schema:v9:"
MODALITY_DISPATCH = {
    "scalar": compile_scalar,
    "table": compile_table,
    "bitfield": compile_bitfield,
    "plot": compile_plot,
    "waveform": compile_waveform,
    "schematic": compile_schematic,
}


def detect_modality(spec: dict[str, Any]) -> str:
    """Resolve modality name from offline schema URN."""
    schema_id = str(spec.get("$schema") or spec.get("schema") or "")
    if schema_id.startswith(URN_PREFIX):
        mod = schema_id[len(URN_PREFIX):].split(":")[0].strip().lower()
        if mod in MODALITY_DISPATCH:
            return mod
    raise ValueError(f"Unsupported or missing offline schema URN: {schema_id!r}")


def _load_bundle_asset(bundle_name: str, repo_rel_paths: tuple[str, ...]) -> str:
    """Load portable skill asset bundle first; fall back to repo sources if absent."""
    bundled = SCRIPT_DIR.parent / "assets" / bundle_name
    if bundled.is_file():
        return bundled.read_text(encoding="utf-8")
    repo_root = SCRIPT_DIR.parent.parent.parent
    chunks = [(repo_root / rp).read_text(encoding="utf-8") for rp in repo_rel_paths if (repo_root / rp).is_file()]
    return "\n".join(chunks)


_FALLBACK_TOKENS_CSS = (
    ':root,[data-theme="white"]{--bg-shell:#EEF2F6;--bg-canvas:#FFFFFF;--bg-surface:#FFFFFF;'
    '--bg-card:#FFFFFF;--bg-elevated:#F8FAFC;--bg-header:#F8FAFC;--text-primary:#0F172A;'
    '--text-secondary:#334155;--text-muted:#475569;--border-hairline:#E2E8F0;--border-subtle:#E2E8F0;--border-strong:#CBD5E1;'
    '--accent-primary:#1D4ED8;--accent-focal:#1D4ED8;--status-ok:#15803D;--status-ok-bg:#ECFDF5;'
    '--status-warn:#B45309;--status-warn-bg:#FFFBEB;--status-danger:#B91C1C;--status-err:var(--status-danger);--status-err-bg:#FFF1F2;'
    '--tint-indigo-bg:#EEF2FF;--tint-indigo-fg:#3730A3;--tint-emerald-bg:#ECFDF5;--tint-emerald-fg:#065F46;'
    '--tint-amber-bg:#FFFBEB;--tint-amber-fg:#92400E;--tint-rose-bg:#FFF1F2;--tint-rose-fg:#9F1239;'
    '--tint-violet-bg:#F5F3FF;--tint-violet-fg:#5B21B6;--font-sans:system-ui,sans-serif;'
    '--font-mono:ui-monospace,monospace;--font-serif:Georgia,serif;--font-nums:tabular-nums slashed-zero;--ts-xs:11.5px;--ts-sm:12.5px;'
    '--ts-base:14px;--ts-md:16px;--ts-xl:21px;--radius-card:8px;--radius-sm:6px;--radius-xs:2px;--radius-inner:4px;--radius-pill:999px;}'
    '[data-theme="paper"]{--bg-shell:#EAE5DC;--bg-canvas:#F6F4EF;--bg-surface:#FCFBF8;'
    '--bg-card:#FCFBF8;--bg-elevated:#EFECE5;--bg-header:#EFECE5;--text-primary:#1C1917;'
    '--text-secondary:#44403C;--text-muted:#57534E;--border-hairline:#E5E0D6;--border-subtle:#E5E0D6;--border-strong:#D6CFC5;'
    '--accent-primary:#1E40AF;--accent-focal:#1E40AF;--status-ok:#15803D;--status-ok-bg:#E8F5EE;'
    '--status-warn:#92400E;--status-warn-bg:#FDF5E6;--status-danger:#9F1239;--status-err:var(--status-danger);--status-err-bg:#FCEEEF;'
    '--tint-indigo-bg:#EBF0FA;--tint-indigo-fg:#312E81;--tint-emerald-bg:#E8F5EE;--tint-emerald-fg:#065F46;'
    '--tint-amber-bg:#FDF5E6;--tint-amber-fg:#92400E;--tint-rose-bg:#FCEEEF;--tint-rose-fg:#9F1239;'
    '--tint-violet-bg:#F1EEFA;--tint-violet-fg:#5B21B6;}'
    '[data-theme="dark-paper"]{--bg-shell:#0D0C0B;--bg-canvas:#141312;--bg-surface:#1C1B19;'
    '--bg-card:#1C1B19;--bg-elevated:#252421;--bg-header:#252421;--text-primary:#F0EDE8;'
    '--text-secondary:#C7C2BA;--text-muted:#A19B93;--border-hairline:#2E2C29;--border-subtle:#2E2C29;--border-strong:#46433E;'
    '--accent-primary:#60A5FA;--accent-focal:#60A5FA;--status-ok:#4ADE80;--status-ok-bg:rgba(34,197,94,0.15);'
    '--status-warn:#FBBF24;--status-warn-bg:rgba(245,158,11,0.15);--status-danger:#F87171;--status-err:var(--status-danger);--status-err-bg:rgba(239,68,68,0.15);'
    '--tint-indigo-bg:rgba(99,102,241,0.16);--tint-indigo-fg:#C7D2FE;--tint-emerald-bg:rgba(16,185,129,0.16);'
    '--tint-emerald-fg:#A7F3D0;--tint-amber-bg:rgba(245,158,11,0.16);--tint-amber-fg:#FDE68A;'
    '--tint-rose-bg:rgba(244,63,94,0.16);--tint-rose-fg:#FECDD3;--tint-violet-bg:rgba(139,92,246,0.16);--tint-violet-fg:#DDD6FE;}'
    '[data-theme="dark"]{--bg-shell:#05070B;--bg-canvas:#090D16;--bg-surface:#0F1624;--bg-card:#0F1624;'
    '--bg-elevated:#172135;--bg-header:#172135;--text-primary:#F1F5F9;--text-secondary:#CBD5E1;'
    '--text-muted:#94A3B8;--border-hairline:#1E293B;--border-subtle:#1E293B;--border-strong:#334155;--accent-primary:#38BDF8;'
    '--accent-focal:#38BDF8;--status-ok:#4ADE80;--status-ok-bg:rgba(34,197,94,0.16);--status-warn:#FBBF24;'
    '--status-warn-bg:rgba(245,158,11,0.16);--status-danger:#F87171;--status-err:var(--status-danger);--status-err-bg:rgba(239,68,68,0.16);'
    '--tint-indigo-bg:rgba(99,102,241,0.18);--tint-indigo-fg:#C7D2FE;--tint-emerald-bg:rgba(16,185,129,0.18);'
    '--tint-emerald-fg:#A7F3D0;--tint-amber-bg:rgba(245,158,11,0.18);--tint-amber-fg:#FDE68A;'
    '--tint-rose-bg:rgba(244,63,94,0.18);--tint-rose-fg:#FECDD3;--tint-violet-bg:rgba(139,92,246,0.18);'
    '--tint-violet-fg:#DDD6FE;}body{margin:0;padding:1.5rem;background:var(--bg-shell);color:var(--text-primary);font-family:var(--font-sans);}'
)


def _wrap_standalone_html(body_html: str, title: str, theme: str, medium: str) -> str:
    """Wrap compiled fragment(s) into a portable self-contained HTML5 document."""
    css = _load_bundle_asset(
        "quiet-evidence-bundle.css",
        (
            "tokens/quiet-ui-tokens.css",
            "src/css/00-layers-and-reset.css",
            "src/css/01-stage-and-containers.css",
            "src/css/03-pills-and-annunciators.css",
            "src/css/12-period-and-scope.css",
            "src/css/13-split-reader-dialog.css",
            "src/css/14-forms-and-states.css",
            "src/css/17-editorial-research-brief.css",
            "docs/bench/evidence-bench.css",
        ),
    ) or _FALLBACK_TOKENS_CSS
    js = _load_bundle_asset(
        "quiet-evidence-bundle.js",
        (
            "src/js/evidence-runtime.js",
            "src/js/quiet-svg-chart-layout.js",
            "src/js/quiet-time-binning.js",
            "src/js/echarts-layout-defaults.js",
            "src/js/quiet-cyclical-whiskers.js",
            "src/js/quiet-period-stepper.js",
            "src/js/quiet-card-export.js",
        ),
    )
    scheme = "dark" if theme in {"dark", "dark-paper"} else "light"
    return (
        "<!DOCTYPE html>\n"
        f'<html lang="en" data-theme="{esc(theme)}" data-medium="{esc(medium)}">\n<head>\n'
        '<meta charset="utf-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f'<meta name="color-scheme" content="{scheme}" />\n<title>{esc(title)}</title>\n'
        f"<style>\n{css}\n</style>\n</head>\n<body>\n"
        f'<main class="qe-bench-main" tabindex="-1">{body_html}</main>\n'
        + (f"<script>\n{js}\n</script>\n" if js else "")
        + "</body>\n</html>\n"
    )


def _compile_single_dict(
    data: dict[str, Any],
    raw_text: str,
    rigor: str | None,
    medium: str,
    theme: str,
    include_wrapper: bool,
    include_spec_drawer: bool,
    chrome: str = "bench",
) -> str:
    modality = detect_modality(data)
    meta = data.get("metadata") or {}
    eff_rigor = (rigor or meta.get("rigor_level", "L2")).upper()
    compiler = MODALITY_DISPATCH[modality]
    inner_html = compiler(data, rigor=eff_rigor, medium=medium, theme=theme, chrome=chrome)
    if not include_wrapper:
        return inner_html

    fig_id = esc(data.get("id", f"qe-{modality}"))
    inner_html = wrap_takeaway_card(data, inner_html, modality, fig_id)
    title = esc(meta.get("title", modality.title()))
    desc = str(meta.get("description", ""))
    desc_html = ""
    if desc:
        import re as _re
        d_uni = _re.sub(r"\btau\b", "τ", desc.replace("+/-", "±").replace("p_hat", "p̂").replace("y_hat", "ŷ"))
        d_html = _re.sub(
            r"(?<![A-Za-z0-9_])((?:p̂|ŷ|σ|[A-Za-z]))_([a-z0-9]{1,3})(?![A-Za-z0-9_])",
            r"\1<sub>\2</sub>",
            esc(d_uni),
        )
        desc_html = f'<figcaption class="va-figure-caption">{d_html}</figcaption>'
    drawer = ""
    if include_spec_drawer:
        drawer = (
            '<details class="qe-spec-drawer">'
            '<summary class="qe-spec-summary">Inspect JSON Spec ('
            f'{esc(data.get("$schema", ""))}'
            ")</summary>"
            f'<pre class="va-mermaid-code qe-spec-pre" tabindex="0" role="region" aria-label="Raw JSON specification for {title}"><code>{esc(raw_text)}</code></pre>'
            "</details>"
        )
    eco_drawer = render_ecosystem_drawer(data) if (include_spec_drawer and chrome == "bench" and (modality == "plot" or data.get("waveform_kind") == "strip_chart")) else ""
    badges = (
        f'<span class="qe-fig-badges"><span class="va-pill" data-variant="tag">{esc(modality.upper())}</span>'
        f'<span class="va-pill" data-variant="tag">{esc(eff_rigor)}</span></span>'
        if chrome == "bench"
        else ""
    )
    caption = desc_html
    return (
        f'<figure class="va-figure-card qe-figure" id="{fig_id}" '
        f'data-qe-modality="{esc(modality)}" data-qe-rigor="{esc(eff_rigor)}" '
        f'data-qe-medium="{esc(medium)}" data-qe-theme="{esc(theme)}">'
        f'<div class="va-figure-hdr qe-card-head">'
        f'<h2 class="qe-fig-title">{title}</h2>'
        f'{badges}'
        f"</div>"
        f"{inner_html}"
        f"{caption}"
        f"{eco_drawer}"
        f"{drawer}"
        "</figure>"
    )


def compile_spec(
    spec: dict[str, Any] | list[dict[str, Any]] | str | Path,
    rigor: str | None = None,
    medium: str = "m2",
    theme: str = "white",
    include_wrapper: bool = True,
    include_spec_drawer: bool = True,
    standalone: bool = False,
    chrome: str = "bench",
) -> str:
    """Compile a JSON evidence spec (or list of specs) into semantic HTML/SVG."""
    if isinstance(spec, (str, Path)):
        raw_text = Path(spec).read_text(encoding="utf-8")
        data = json.loads(raw_text)
    else:
        data = spec
        raw_text = json.dumps(data, indent=2)

    if isinstance(data, list):
        frags = [
            _compile_single_dict(item, json.dumps(item, indent=2), rigor, medium, theme, include_wrapper, include_spec_drawer, chrome)
            for item in data if isinstance(item, dict)
        ]
        body = "\n".join(frags)
        doc_title = "Quiet UI Compiled Evidence Collection"
    elif isinstance(data, dict):
        body = _compile_single_dict(data, raw_text, rigor, medium, theme, include_wrapper, include_spec_drawer, chrome)
        doc_title = str((data.get("metadata") or {}).get("title", "Quiet UI Evidence"))
    else:
        raise ValueError(f"Expected JSON object or array of objects, got {type(data).__name__}")

    if standalone:
        return _wrap_standalone_html(body, doc_title, theme, medium)
    return body


def main() -> None:
    parser = argparse.ArgumentParser(description="Quiet UI Pillar 2 Evidence Compiler")
    parser.add_argument("spec_json", help="Path to JSON specification (urn:quiet-ui:schema:v9:*)")
    parser.add_argument("--rigor", choices=["L1", "L2", "L3"], default=None)
    parser.add_argument("--medium", choices=["m1", "m2", "m3", "m4", "m5", "m6", "m7"], default="m2")
    parser.add_argument("--theme", choices=["white", "paper", "dark-paper", "dark"], default="white")
    parser.add_argument("--chrome", choices=["bench", "embedded"], default="bench")
    parser.add_argument("--standalone", action="store_true", help="Wrap output in full self-contained HTML5 doc")
    parser.add_argument("--fragment", action="store_true", help="Force HTML fragment output even when writing --out .html")
    parser.add_argument("--out", default=None, help="Optional output HTML path")
    args = parser.parse_args()

    use_standalone = args.standalone or (args.out is not None and not args.fragment)
    html_out = compile_spec(
        Path(args.spec_json),
        rigor=args.rigor,
        medium=args.medium,
        theme=args.theme,
        standalone=use_standalone,
        chrome=args.chrome,
    )
    if args.out:
        Path(args.out).write_text(html_out, encoding="utf-8")
    else:
        print(html_out)


if __name__ == "__main__":
    main()
