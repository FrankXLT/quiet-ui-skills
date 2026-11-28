#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unified Quiet UI build & zero-drift verification entrypoint (--check)."""

from __future__ import annotations

import argparse
import contextlib
import html as html_lib
import io
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from build_evidence_bench import render_bench_html  # noqa: E402
from build_showcase import WORLD_BUILDERS, build_showcase as compile_studio  # noqa: E402
from customizations.scripts.build_showcase import build_showcase as compile_starter  # noqa: E402
from src.site_shell import (  # noqa: E402
    build_project_site,
    load_site_config,
    render_demo_chrome_css,
    render_demo_return_bar,
    render_social_svg,
)
from src.site_shell.templates import escape_tag_body, read_asset  # noqa: E402

TOKEN_MIRRORS: tuple[str, ...] = (
    "skills/quiet-ui/tokens/quiet-ui-tokens.css",
    "customizations/personal-starter/styles/quiet-ui-tokens.css",
    "customizations/brand-starter/styles/quiet-ui-tokens.css",
    "customizations/project-site-starter/styles/quiet-ui-tokens.css",
    "docs/styles/quiet-ui-tokens.css",
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


_STUDIO_BASE_URL = "https://projects.oaworkbench.org/quiet-ui-skills/demo/"
_BENCH_BASE_URL = "https://projects.oaworkbench.org/quiet-ui-skills/bench/evidence-bench.html"
_BENCH_MODALITY_LABELS: dict[str, str] = {
    "M1": "Key Numbers & Gauges",
    "M2": "Tables & Comparisons",
    "M3": "Hardware Registers",
    "M4": "Charts, Timelines & Heatmaps",
    "M5": "Live Signals & Waveforms",
    "M6": "System Diagrams",
    "UI": "Forms, Menus & Controls",
    "BR": "Summaries & Checklists",
}


def _strip_tags(raw: str) -> str:
    return " ".join(html_lib.unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def _search_tokens(*texts: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for txt in texts:
        for tok in re.findall(r"[a-z0-9][a-z0-9._-]*", str(txt or "").lower()):
            clean = tok.strip("._-")
            if len(clean) >= 2 and clean not in seen:
                seen.add(clean)
                out.append(clean)
                if len(out) >= 16:
                    return out
    return out


def _collect_studio_search_entries() -> list[dict[str, Any]]:
    """Collect deterministic search entries for all 26 Studio Demo views."""
    corpora_dir = REPO_ROOT / "content" / "corpora"
    entries: list[dict[str, Any]] = []
    for wid, builder in WORLD_BUILDERS.items():
        wm = builder(corpora_dir)["world_meta"]
        w_label = str(wm.get("world_label") or wid).strip()
        for view in wm.get("views") or []:
            vid = str(view.get("view_id") or "").strip()
            if not vid:
                continue
            title = str(view.get("title") or view.get("option_label") or vid).strip()
            opt = str(view.get("option_label") or "").strip()
            desc = str(view.get("vector_summary") or opt or title).strip()
            nav_txt = " ".join(str(x) for x in (view.get("nav_items") or []))
            entries.append({
                "id": f"studio-{vid}",
                "title": title,
                "category": "Studio Demo",
                "summary": f"{w_label} — {desc}",
                "keywords": _search_tokens("studio", wid, vid, w_label, opt, title, nav_txt),
                "url": f"{_STUDIO_BASE_URL}?domain={wid}&view={vid}",
            })
    return entries


def _collect_bench_search_entries(bench_html: str) -> list[dict[str, Any]]:
    """Collect deterministic search entries for all 53 Evidence Bench specimens."""
    entries: list[dict[str, Any]] = []
    for attrs, body in re.findall(r"<article\b([^>]*)>(.*?)</article>", bench_html, flags=re.S):
        id_m = re.search(r'<figure\b[^>]*\bid="([^"]+)"', body) or re.search(r'\bid="([^"]+)"', body)
        head_m = re.search(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", body, flags=re.S)
        if not id_m or not head_m:
            continue
        elem_id = id_m.group(1).strip()
        title = _strip_tags(head_m.group(1))
        mod = (m.group(1) if (m := re.search(r'data-modality="([^"]+)"', attrs)) else "").strip()
        smod = (m.group(1) if (m := re.search(r'data-schema-modality="([^"]+)"', attrs)) else "").strip()
        rigor = (m.group(1) if (m := re.search(r'data-rigor="([^"]+)"', attrs)) else "").strip()
        cap_m = re.search(r"<figcaption\b[^>]*>(.*?)</figcaption>", body, flags=re.S)
        cap_txt = _strip_tags(cap_m.group(1)) if cap_m else ""
        mod_label = _BENCH_MODALITY_LABELS.get(mod, mod or "Component")
        eid = elem_id if elem_id.startswith("bench-") else f"bench-{elem_id}"
        entries.append({
            "id": eid,
            "title": title,
            "category": "Evidence Bench",
            "summary": cap_txt or f"{mod_label} ({rigor or 'L2'}) — {title}",
            "keywords": _search_tokens("evidence-bench", elem_id, mod, smod, rigor, mod_label, title),
            "url": f"{_BENCH_BASE_URL}#{elem_id}",
        })
    return entries


def _add_project_site_outputs(
    outputs: dict[Path, bytes], tok_bytes: bytes, tmp_dir: Path, bench_html: str
) -> None:
    """Populate Quiet UI 3-route docs/ and project-site-starter static site outputs."""
    tok_src = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
    extra_entries = _collect_studio_search_entries() + _collect_bench_search_entries(bench_html)

    quiet_cfg = load_site_config(REPO_ROOT / "src" / "chrome" / "quiet-ui-site.json")
    quiet_dir = tmp_dir / "quiet-site"
    build_project_site(
        quiet_cfg,
        quiet_dir,
        bundle=False,
        tokens_path=tok_src,
        overrides_path=None,
        render_demo=False,
        render_search_index=True,
        extra_search_entries=extra_entries,
    )
    docs_root = REPO_ROOT / "docs"
    outputs[docs_root / "index.html"] = (quiet_dir / "index.html").read_bytes()
    outputs[docs_root / "docs" / "index.html"] = (quiet_dir / "docs" / "index.html").read_bytes()
    outputs[docs_root / "search-index.json"] = (quiet_dir / "search-index.json").read_bytes()
    outputs[docs_root / "assets" / "site-search.js"] = (quiet_dir / "assets" / "site-search.js").read_bytes()
    outputs[docs_root / "styles" / "tokens.layered.css"] = (quiet_dir / "styles" / "tokens.layered.css").read_bytes()
    outputs[docs_root / "assets" / "quiet-ui-social.svg"] = render_social_svg(quiet_cfg).encode("utf-8")
    shell_js = escape_tag_body(read_asset("site-shell.js"), "script")
    site_nav_js = (
        f'  <script id="va-demo-site-shell-js">\n{shell_js}\n  </script>\n'
        '  <script defer src="../assets/site-search.js"></script>'
    )
    outputs[docs_root / "demo" / "index.html"] = compile_studio(
        REPO_ROOT,
        list(WORLD_BUILDERS.keys()),
        docs_base="..",
        default_studio_view="examples",
        is_demo_route=True,
        site_nav_html=render_demo_return_bar(quiet_cfg, current="demo"),
        site_nav_assets=render_demo_chrome_css(tok_bytes.decode("utf-8")),
        site_nav_js=site_nav_js,
    ).encode("utf-8")

    starter_root = REPO_ROOT / "customizations" / "project-site-starter"
    starter_cfg = load_site_config(starter_root / "oaw-site.json")
    overrides_src = starter_root / "styles" / "overrides.css"
    starter_dir = tmp_dir / "starter-site"
    build_project_site(
        starter_cfg,
        starter_dir,
        bundle=False,
        tokens_path=tok_src,
        overrides_path=overrides_src,
        render_search_index=True,
    )
    site_dir = starter_root / "site"
    outputs[site_dir / "index.html"] = (starter_dir / "index.html").read_bytes()
    outputs[site_dir / "docs" / "index.html"] = (starter_dir / "docs" / "index.html").read_bytes()
    outputs[site_dir / "search-index.json"] = (starter_dir / "search-index.json").read_bytes()
    outputs[site_dir / "assets" / "site-search.js"] = (starter_dir / "assets" / "site-search.js").read_bytes()
    outputs[site_dir / "styles" / "quiet-ui-tokens.css"] = tok_bytes
    outputs[site_dir / "styles" / "tokens.layered.css"] = (starter_dir / "styles" / "tokens.layered.css").read_bytes()
    outputs[site_dir / "styles" / "overrides.css"] = overrides_src.read_bytes()
    outputs[site_dir / "assets" / "social-preview.svg"] = render_social_svg(starter_cfg).encode("utf-8")


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

    bench_html = render_bench_html()
    outputs[REPO_ROOT / "docs" / "bench" / "evidence-bench.html"] = bench_html.encode("utf-8")

    studio_html = compile_studio(REPO_ROOT, list(WORLD_BUILDERS.keys()))
    studio_bytes = studio_html.encode("utf-8")
    outputs[REPO_ROOT / "quiet-ui-showcase.html"] = studio_bytes

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        src_html = tmp_dir / "quiet-ui-showcase.html"
        src_html.write_bytes(studio_bytes)
        for starter in ("personal-starter", "brand-starter"):
            out_tmp = tmp_dir / f"{starter}.html"
            with contextlib.redirect_stdout(io.StringIO()):
                compile_starter(REPO_ROOT / "customizations" / starter, src_html, out_tmp, bundle=False)
            outputs[REPO_ROOT / "customizations" / starter / "showcase.html"] = out_tmp.read_bytes()
        _add_project_site_outputs(outputs, tok_bytes, tmp_dir, bench_html)

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
