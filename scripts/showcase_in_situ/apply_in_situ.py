# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v7.1 Showcase In-Situ Applicator and Multi-File Synchronizer."""

import re
import shutil
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from figures_editorial import (
        render_doc1_figure,
        render_doc2_figure,
        render_doc3_figure,
        render_doc4a_figure,
        render_doc4b_figure,
    )
    from figures_interactive import render_deck1_switcher_and_slides
    from figures_workspace import (
        render_app3_tile4_proof,
        render_app3_tile5_proof,
        render_apptree_er_figure,
    )
else:
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

ATLAS_BTN = (
    "<!-- QUIET-UI-V71-ATLASBTN-START -->\n"
    '      <button type="button" id="va-atlas-link-btn" class="va-pill-btn" onclick="openDiagramAtlas()" '
    'title="Open 45-Type Editorial SVG Diagram &amp; Chart Atlas">'
    '<i class="fa-solid fa-diagram-project"></i><span class="va-studio-btn-label">45 Diagrams</span></button>\n'
    "      <!-- QUIET-UI-V71-ATLASBTN-END -->"
)

SCOPED_CSS = """<!-- QUIET-UI-V71-CSS-START -->
    .va-seq-step-band { opacity: 0.55; cursor: pointer; transition: opacity 0.15s ease; }
    .va-seq-step-band.is-active { opacity: 1.0; }
    .va-seq-step-band.is-active rect.seq-band-bg { fill: var(--tint-indigo-bg); stroke: var(--accent-focal); stroke-width: 1.2; }
    .deck1-slide-pill { transition: background 0.15s ease, color 0.15s ease; }
    .deck1-slide-pill.active { background: var(--accent-focal); color: #ffffff; border-color: var(--accent-focal); }
    .va-er-entity { transition: filter 0.15s ease; }
    .va-er-entity.is-active rect.er-box { stroke: var(--accent-focal); stroke-width: 2; fill: var(--tint-indigo-bg); }
    <!-- QUIET-UI-V71-CSS-END -->"""

OPEN_ATLAS_JS = """<!-- QUIET-UI-V71-ATLASJS-START -->
    function openDiagramAtlas() {
      const theme = document.documentElement.getAttribute('data-theme') || 'white';
      const p = window.location.pathname;
      const base = p.includes('/customizations/') ? '../../docs/diagrams.html' : (p.endsWith('quiet-ui-showcase.html') ? './docs/diagrams.html' : './diagrams.html');
      window.location.href = base + '?theme=' + encodeURIComponent(theme);
    }
    <!-- QUIET-UI-V71-ATLASJS-END -->"""

DECK1_SLIDE_JS = """<!-- QUIET-UI-V71-DECK1JS-START -->
    function setDeck1Slide(slideNum) {
      deck1Slide = slideNum;
      for (let i = 1; i <= 4; i++) {
        const el = document.getElementById('deck1-viz-' + i);
        if (el) el.style.display = (i === slideNum) ? 'block' : 'none';
      }
      document.querySelectorAll('.deck1-slide-pill').forEach((btn, idx) => {
        btn.classList.toggle('active', (idx + 1) === slideNum);
      });
      const badge = document.getElementById('deck1-counter-badge');
      if (badge) badge.textContent = `SLIDE 0${deck1Slide} / 04 • STEP ${deck1Step + 1}/3`;
    }
    <!-- QUIET-UI-V71-DECK1JS-END -->"""


def patch_doc_figures(html: str) -> str:
    """Apply Doc-1, Doc-2, Doc-3, Doc-4B, Doc-4A figures."""
    if "<!-- QUIET-UI-V71-DOC1-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DOC1-START -->.*?<!-- QUIET-UI-V71-DOC1-END -->", render_doc1_figure(), html, flags=re.S)
    else:
        html = re.sub(r'<figure style="margin:1\.5rem 0; border-top:1px solid var\(--border-grid\); border-bottom:1px solid var\(--border-grid\); padding:1rem 0;">.*?</figure>', render_doc1_figure(), html, count=1, flags=re.S)

    if "<!-- QUIET-UI-V71-DOC2-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DOC2-START -->.*?<!-- QUIET-UI-V71-DOC2-END -->", render_doc2_figure(), html, flags=re.S)
    else:
        html = re.sub(r'<figure class="va-mermaid-figure" id="doc2-mermaid-fig">.*?</figure>', render_doc2_figure(), html, count=1, flags=re.S)

    if "<!-- QUIET-UI-V71-DOC3-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DOC3-START -->.*?<!-- QUIET-UI-V71-DOC3-END -->", render_doc3_figure(), html, flags=re.S)
    else:
        html = re.sub(r'<figure class="va-mermaid-figure" id="doc3-mermaid-fig">.*?</figure>', render_doc3_figure(), html, count=1, flags=re.S)

    if "<!-- QUIET-UI-V71-DOC4B-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DOC4B-START -->.*?<!-- QUIET-UI-V71-DOC4B-END -->", render_doc4b_figure(), html, flags=re.S)
    else:
        html = html.replace("<!-- v4.8 Situation -> Action Decision-Router Table", f"{render_doc4b_figure()}\n          <!-- v4.8 Situation -> Action Decision-Router Table", 1)

    if "<!-- QUIET-UI-V71-DOC4A-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DOC4A-START -->.*?<!-- QUIET-UI-V71-DOC4A-END -->", render_doc4a_figure(), html, flags=re.S)
    else:
        html = re.sub(r'<figure class="va-mermaid-figure" id="doc4a-mermaid-fig">.*?</figure>', render_doc4a_figure(), html, count=1, flags=re.S)
    return html


def patch_deck1_and_workspaces(html: str) -> str:
    """Apply Deck-1, App-3, and App-Tree figures."""
    if "<!-- QUIET-UI-V71-DECK1-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DECK1-START -->.*?<!-- QUIET-UI-V71-DECK1-END -->", render_deck1_switcher_and_slides(), html, flags=re.S)
    else:
        html = re.sub(r'<div class="deck1-band2-canvas">.*?</div>\s*<!-- Band 3:', f"{render_deck1_switcher_and_slides()}\n\n            <!-- Band 3:", html, count=1, flags=re.S)

    if "<!-- QUIET-UI-V71-APP3T4-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-APP3T4-START -->.*?<!-- QUIET-UI-V71-APP3T4-END -->", render_app3_tile4_proof(), html, flags=re.S)
    else:
        pat_t4 = r'(<!-- Tile 4 [^>]*>.*?<div class="bento-layer2-hero">.*?</div>\s*)<div class="bento-layer3-proof">.*?</div>'
        html = re.sub(pat_t4, rf"\g<1>{render_app3_tile4_proof()}", html, count=1, flags=re.S)

    if "<!-- QUIET-UI-V71-APP3T5-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-APP3T5-START -->.*?<!-- QUIET-UI-V71-APP3T5-END -->", render_app3_tile5_proof(), html, flags=re.S)
    else:
        pat_t5 = r'(<!-- Tile 5 [^>]*>.*?<div class="bento-layer2-hero">.*?</div>\s*)<div class="bento-layer3-proof">.*?</div>'
        html = re.sub(pat_t5, rf"\g<1>{render_app3_tile5_proof()}", html, count=1, flags=re.S)

    html = html.replace("<span>Query &amp; AST Preview</span>", "<span>ER Lineage &amp; SQL AST</span>", 1)
    if "<!-- QUIET-UI-V71-APPTREE-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-APPTREE-START -->.*?<!-- QUIET-UI-V71-APPTREE-END -->", render_apptree_er_figure(), html, flags=re.S)
    else:
        html = html.replace('<pre class="mono" style="background:var(--bg-header);border:1px solid var(--border-strong)', f"{render_apptree_er_figure()}\n            <pre class=\"mono\" style=\"background:var(--bg-header);border:1px solid var(--border-strong)", 1)
    return html


def patch_scripts_and_styles(html: str) -> str:
    """Inject openDiagramAtlas, setDeck1Slide, and sync handlers."""
    if "<!-- QUIET-UI-V71-CSS-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-CSS-START -->.*?<!-- QUIET-UI-V71-CSS-END -->", SCOPED_CSS, html, flags=re.S)
    else:
        html = html.replace("</style>", f"  {SCOPED_CSS}\n  </style>", 1)

    if "<!-- QUIET-UI-V71-ATLASJS-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-ATLASJS-START -->.*?<!-- QUIET-UI-V71-ATLASJS-END -->", OPEN_ATLAS_JS, html, flags=re.S)
    else:
        html = html.replace("function copyTierPrompt(", f"{OPEN_ATLAS_JS}\n    function copyTierPrompt(", 1)

    if "<!-- QUIET-UI-V71-DECK1JS-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-DECK1JS-START -->.*?<!-- QUIET-UI-V71-DECK1JS-END -->", DECK1_SLIDE_JS, html, flags=re.S)
    else:
        html = html.replace("function setDeck1Step(", f"{DECK1_SLIDE_JS}\n    function setDeck1Step(", 1)

    new_sel_step = (
        "function selectRunbookStep(idx) {\n"
        "      currentRunbookStep = idx;\n"
        "      document.querySelectorAll('#tier-doc-4a .step-anchor').forEach((el, i) => {\n"
        "        el.classList.toggle('active', i === idx);\n"
        "      });\n"
        "      document.querySelectorAll('#doc4a-mermaid-fig .va-seq-step-band').forEach(el => {\n"
        "        const s = parseInt(el.getAttribute('data-seq-step'), 10);\n"
        "        el.classList.toggle('is-active', s === idx);\n"
        "      });\n"
        "      renderRunbookConsole();\n"
        "    }"
    )
    html = re.sub(r"function selectRunbookStep\(idx\)\s*\{.*?renderRunbookConsole\(\);\s*\}", new_sel_step, html, flags=re.S)

    adv_re = r"setDeck1Step\(next\);"
    if "setDeck1Slide(deck1Slide);" not in html:
        html = re.sub(r"function advanceDeck1\(delta\)\s*\{.*?" + adv_re, lambda m: m.group(0).replace("setDeck1Step(next);", "setDeck1Slide(deck1Slide);\n      setDeck1Step(next);"), html, flags=re.S)

    er_sync = (
        "      let targetEntity = 'wr_samples';\n"
        "      if (nodeKey === 'wr_nodes' || (typeof nodeKey === 'string' && nodeKey.startsWith('row_node_'))) targetEntity = 'wr_nodes';\n"
        "      else if (nodeKey === 'wr_alarms') targetEntity = 'wr_alarms';\n"
        "      else if (nodeKey === 'wr_samples' || (typeof nodeKey === 'string' && (nodeKey.startsWith('col_') || nodeKey.startsWith('row_')))) targetEntity = 'wr_samples';\n"
        "      document.querySelectorAll('#va-tree-er-svg .va-er-entity').forEach(el => {\n"
        "        el.classList.toggle('is-active', el.getAttribute('data-er-entity') === targetEntity);\n"
        "      });\n"
        "      const d = treeNodePayloads[nodeKey]"
    )
    if "let targetEntity = 'wr_samples';" not in html:
        html = html.replace("      const d = treeNodePayloads[nodeKey]", er_sync, 1)

    html = html.replace(
        "    let _urlParamsHydrated = false;\n    function syncUrlQueryParams() {\n      if (!_urlParamsHydrated) return;",
        "    function syncUrlQueryParams() {\n      if (!window._urlParamsHydrated) return;",
    )
    html = html.replace("      _urlParamsHydrated = true;\n", "      window._urlParamsHydrated = true;\n")
    if "window._urlParamsHydrated" not in html:
        html = html.replace(
            "    function syncUrlQueryParams() {\n      try {",
            "    function syncUrlQueryParams() {\n      if (!window._urlParamsHydrated) return;\n      try {",
            1,
        )
        html = html.replace(
            "      } catch (e) {}\n    }\n    window.addEventListener('DOMContentLoaded', applyUrlQueryParamsOnLoad);",
            "      } catch (e) {}\n      window._urlParamsHydrated = true;\n      syncUrlQueryParams();\n    }\n    if (document.readyState === 'loading') window.addEventListener('DOMContentLoaded', applyUrlQueryParamsOnLoad);\n    else applyUrlQueryParamsOnLoad();",
            1,
        )

    return html


def apply_in_situ(html: str) -> str:
    """Idempotently apply all v7.1 in-situ upgrades to Quiet UI showcase HTML."""
    html = re.sub(
        r"<title>.*?</title>",
        "<title>Quiet UI Skills v7.1 — 17-Tier UI Architecture &amp; Editorial SVG Diagram Continuum</title>",
        html,
        count=1,
    )
    if "<!-- QUIET-UI-V71-ATLASBTN-START -->" in html:
        html = re.sub(r"<!-- QUIET-UI-V71-ATLASBTN-START -->.*?<!-- QUIET-UI-V71-ATLASBTN-END -->", ATLAS_BTN, html, flags=re.S)
    else:
        html = html.replace('<button type="button" id="va-display-trigger"', f"{ATLAS_BTN}\n      <button type=\"button\" id=\"va-display-trigger\"", 1)

    html = patch_doc_figures(html)
    html = patch_deck1_and_workspaces(html)
    html = patch_scripts_and_styles(html)
    return html


def main() -> int:
    """Run in-situ upgrades on quiet-ui-showcase.html, docs/index.html, and starter packages."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    showcase_path = repo_root / "quiet-ui-showcase.html"
    docs_index_path = repo_root / "docs" / "index.html"

    print(f"Reading master showcase from {showcase_path}...")
    orig_html = showcase_path.read_text(encoding="utf-8")
    upgraded_html = apply_in_situ(orig_html)
    showcase_path.write_text(upgraded_html, encoding="utf-8")
    print(f"[OK] Successfully applied v7.1 in-situ upgrades to {showcase_path}")

    shutil.copyfile(showcase_path, docs_index_path)
    print(f"[OK] Synchronized copy to {docs_index_path}")

    # Build starter customizations
    build_script = repo_root / "customizations" / "scripts" / "build_showcase.py"
    sys.path.insert(0, str(build_script.parent))
    from build_showcase import build_showcase

    for starter in ("personal-starter", "brand-starter"):
        tdir = repo_root / "customizations" / starter
        out_html = tdir / "showcase.html"
        build_showcase(tdir, showcase_path, out_html)
        print(f"[OK] Re-compiled {starter} showcase -> {out_html}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
