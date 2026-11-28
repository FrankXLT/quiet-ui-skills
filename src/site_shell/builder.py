# SPDX-License-Identifier: Apache-2.0
"""Static HTML builder for Quiet UI v9.8.0 three-route OAW project sites."""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

from .markdown_docs import _sanitize_svg_html, compile_diagram_spec, compile_markdown_docs
from .search_index import build_project_search_index, write_project_search_index
from .templates import (
    ASSETS_DIR, LAYER_ORDER, REPO_ROOT, _LAYER_DECL_RE, esc, escape_tag_body, is_external,
    json_embed, read_asset, render_chrome_top, render_footer, render_head, route_defs, safe_href, svg_icon,
)

_SAFE_DOC_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")
_ROOT_FONT_RE = re.compile(r"\bfont-size\s*:\s*clamp\([^;]+;\s*")


def render_demo_chrome_css(tokens_css: str = "") -> str:
    """Build scoped token + @layer shell/search CSS so /demo/ reuses the 46px OAW topbar identically."""
    tok_p = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
    tok_src = tokens_css or (tok_p.read_text(encoding="utf-8") if tok_p.is_file() else "")
    tok_scoped = re.sub(r"^\s*h1,\s*h2,[^\n]+\n?", "", re.sub(r":root\b", ".oaw-demo-chrome", _ROOT_FONT_RE.sub("", tok_src)), flags=re.MULTILINE)
    shell_css = read_asset("site-shell.css")
    m = re.search(r"/\*\s*@oaw-shell-start\s*\*/(.*?)/\*\s*@oaw-shell-end\s*\*/", shell_css, flags=re.S)
    shell_block = m.group(1).strip() if m else _LAYER_DECL_RE.sub("", shell_css).strip()
    search_block = _LAYER_DECL_RE.sub("", read_asset("site-search.css")).strip()
    scoped_reset = (
        "@layer reset {\n"
        "  .oaw-demo-chrome, .oaw-demo-chrome *, .oaw-demo-chrome *::before, .oaw-demo-chrome *::after { box-sizing: border-box; }\n"
        "  .oaw-demo-chrome button { font: inherit; color: inherit; background: none; border: none; padding: 0; cursor: pointer; }\n"
        "  .oaw-demo-chrome a { text-decoration: none; }\n}\n"
        "@layer utilities {\n  .oaw-demo-chrome [hidden]:not([hidden=\"until-found\"]) { display: none; }\n}"
    )
    parts = [f"{LAYER_ORDER}\n@layer tokens {{\n{tok_scoped}\n}}", scoped_reset, shell_block, *([search_block] if search_block else [])]
    body = escape_tag_body("\n\n".join(parts), "style")
    return f'  <style id="va-demo-site-strip-css">\n{body}\n  </style>'


def render_demo_return_bar(config: dict[str, Any], *, current: str = "demo") -> str:
    """Render the unified 46px OAW topbar wrapper for the /demo/ route."""
    return render_chrome_top(config, current=current, rel_prefix="../", is_demo=True)


def _resolve_style_inputs(
    config: dict[str, Any], tokens_path: Path | None, overrides_path: Path | None, tokens_css: str | None, overrides_css: str | None,
) -> tuple[Path | None, str, Path | None, str | None]:
    tok_src = Path(tokens_path) if tokens_path is not None else (REPO_ROOT / "tokens" / "quiet-ui-tokens.css")
    tok_txt = tokens_css if tokens_css is not None else (tok_src.read_text(encoding="utf-8") if tok_src.is_file() else "")
    ovr_src = Path(overrides_path) if overrides_path is not None else None
    if ovr_src is None and overrides_css is None and config.get("base_dir"):
        base_dir = Path(str(config["base_dir"]))
        ovr_src = next((c for c in (base_dir / "styles" / "overrides.css", base_dir / "overrides.css") if c.is_file()), None)
    ovr_txt = overrides_css if overrides_css is not None else (ovr_src.read_text(encoding="utf-8") if ovr_src and ovr_src.is_file() else None)
    return (tok_src if tokens_css is None and tok_src.is_file() else None), tok_txt, (ovr_src if overrides_css is None and ovr_src and ovr_src.is_file() else None), ovr_txt


def _copy_style_safe(src_path: Path | None, css_text: str | None, dst_path: Path) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if src_path is not None and src_path.is_file():
        if not (dst_path.exists() and os.path.samefile(src_path, dst_path)):
            shutil.copy2(src_path, dst_path)
    elif css_text is not None:
        dst_path.write_text(css_text, encoding="utf-8")


def _load_diagram_asset(base_dir: Path, rel_path: str, alt: str) -> str:
    if not rel_path or "\x00" in rel_path or rel_path.startswith(("/", "\\")):
        raise ValueError(f"Diagram path escapes project directory: {rel_path!r}")
    base_resolved = base_dir.resolve()
    fp = (base_dir / rel_path).resolve()
    if not fp.is_relative_to(base_resolved):
        raise ValueError(f"Diagram path escapes project directory: {rel_path!r}")
    if fp.suffix.lower() == ".json" and fp.is_file():
        return compile_diagram_spec(json.loads(fp.read_text(encoding="utf-8")))
    if fp.suffix.lower() == ".svg" and fp.is_file():
        return _sanitize_svg_html(fp.read_text(encoding="utf-8"))
    href = safe_href(rel_path)
    return f'<img src="{esc(href)}" alt="{esc(alt)}">' if href else ""


def _render_diagram_item(entry: str | dict[str, Any], base_dir: Path) -> str:
    if isinstance(entry, str):
        body, elem_id, caption = _load_diagram_asset(base_dir, entry, "Architecture diagram"), "", ""
    else:
        elem_id, caption = str(entry.get("id") or ""), str(entry.get("caption") or "")
        alt = str(entry.get("alt") or entry.get("title") or "Architecture diagram")
        spec = entry.get("spec") if isinstance(entry.get("spec"), dict) else (entry if str(entry.get("$schema") or "").startswith("urn:quiet-ui:schema:v9:") else None)
        if spec is not None:
            body = compile_diagram_spec(spec)
        elif entry.get("svg"):
            body = _sanitize_svg_html(str(entry["svg"]))
        elif (rel_p := next((str(entry[k]) for k in ("path", "src", "file", "svg_path", "image_path") if entry.get(k)), "")):
            body = _load_diagram_asset(base_dir, rel_p, alt)
        else:
            body = ""
    if not body:
        return ""
    id_attr = f' id="diagram-{esc(elem_id)}"' if elem_id else ""
    cap_html = f'\n      <p class="oaw-diagram-caption">{esc(caption)}</p>' if caption else ""
    return f'    <div class="oaw-diagram-panel"{id_attr}>\n      {body}{cap_html}\n    </div>'


def _render_hero_section(proj: dict[str, Any], ov: dict[str, Any]) -> str:
    headline = str(ov.get("headline") or proj.get("title") or proj.get("slug") or "Project")
    summary = str(ov.get("summary") or proj.get("tagline") or "")
    pills_html: list[str] = []
    for raw_p in ov.get("command_pills") or []:
        slug = str(raw_p.get("slug") or raw_p.get("label") or "" if isinstance(raw_p, dict) else raw_p).strip()
        if not slug:
            continue
        href = safe_href(raw_p.get("href")) if isinstance(raw_p, dict) else ""
        inner = f'<span class="oaw-cmd-caret" aria-hidden="true">&gt;</span><span>{esc(slug)}</span><span class="oaw-cmd-cursor" aria-hidden="true">_</span>'
        if href:
            pills_html.append(f'<a class="oaw-cmd-slug" href="{esc(href)}">{inner}</a>')
        else:
            pills_html.append(f'<span class="oaw-cmd-slug">{inner}</span>')
    ctas = [
        f'<a class="{cls}" href="{esc(href)}">{esc(cta["label"])}</a>'
        for key, cls in (("primary_cta", "oaw-btn-primary"), ("secondary_cta", "oaw-btn-secondary"), ("tertiary_cta", "oaw-btn"))
        if isinstance((cta := ov.get(key)), dict) and cta.get("label") and (href := safe_href(cta.get("href")))
    ]
    parts = [
        f'      <p class="oaw-hero-kicker">{esc(ov["kicker"])}</p>' if ov.get("kicker") else "",
        f"      <h1>{esc(headline)}</h1>",
        f'      <p class="oaw-hero-lead">{esc(summary)}</p>' if summary else "",
        f'      <div class="oaw-hero-cmd-strip">{" ".join(pills_html)}</div>' if pills_html else "",
        f'      <div class="oaw-cta-row">{" ".join(ctas)}</div>' if ctas else "",
    ]
    hero = "\n".join(p for p in parts if p)
    return f'    <section class="oaw-hero">\n{hero}\n    </section>'


def _render_showcase_section(ov: dict[str, Any]) -> str:
    step_items = []
    default_icons = ("cubes", "desktop", "terminal")
    for idx, step in enumerate(ov.get("quickstart_steps") or [], start=1):
        if not isinstance(step, dict):
            continue
        icon = str(step.get("icon") or default_icons[(idx - 1) % 3])
        title, body = str(step.get("title") or f"Step {idx}"), str(step.get("body") or "")
        step_items.append(
            f'        <div class="oaw-step-item">'
            f'<div class="oaw-step-icon" aria-hidden="true">{svg_icon(icon, 16)}</div>'
            f'<h3 class="oaw-step-title">{esc(title)}</h3>'
            f'<p class="oaw-step-desc">{esc(body)}</p></div>'
        )
    install_cards = []
    for idx, item in enumerate(ov.get("install_commands") or [], 1):
        lbl = str(item.get("label") if isinstance(item, dict) else f"Install Step {idx}")
        cmd = str(item.get("command") or item.get("cmd") or "" if isinstance(item, dict) else item)
        if cmd:
            install_cards.append(
                f'        <article class="oaw-install-card"><h3>{esc(lbl)}</h3>'
                f'<div class="oaw-install-cmd"><code>{esc(cmd)}</code>'
                f'<button type="button" class="oaw-copy-btn" data-copy-text="{esc(cmd)}" aria-label="Copy {esc(lbl)}">Copy</button></div></article>'
            )
    if not step_items and not install_cards:
        return ""
    steps_block = ('      <div class="oaw-steps-grid">\n' + "\n".join(step_items) + "\n      </div>\n") if step_items else ""
    qs_block = ""
    if install_cards:
        cards_html = "\n".join(install_cards)
        qs_block = (
            '      <div class="oaw-quickstart-box">\n'
            '        <div class="oaw-quickstart-top"><h2 id="oaw-install-hdr">Quick Install</h2><span>Copy and run locally</span></div>\n'
            f'        <div class="oaw-install-grid">\n{cards_html}\n        </div>\n      </div>\n'
        )
    aria = ' aria-labelledby="oaw-install-hdr"' if install_cards else ' aria-label="Getting Started"'
    return f'    <section{aria}>\n      <div class="oaw-showcase-card">\n{steps_block}{qs_block}      </div>\n    </section>'


def _render_overview_sections(config: dict[str, Any]) -> list[str]:
    proj, ov, base_dir = config.get("project") or {}, config.get("overview") or {}, Path(str(config.get("base_dir") or "."))
    sections = [_render_hero_section(proj, ov)]
    if showcase := _render_showcase_section(ov):
        sections.append(showcase)

    if (blocks := ov.get("plain_language_blocks") or []):
        cols = "2" if len(blocks) in (2, 4) else "3"
        cards = []
        for blk in blocks:
            bd = blk if isinstance(blk, dict) else {"title": "Overview", "body": str(blk)}
            bid = f' id="{esc(bd["id"])}"' if bd.get("id") else ""
            tag = f'<span class="oaw-tag">{esc(bd["eyebrow"])}</span>' if bd.get("eyebrow") else ""
            cta = f'<a class="oaw-btn" href="{esc(bh)}" data-oaw-route-link>{esc(bd.get("cta_label") or "Read guide")}</a>' if (bh := safe_href(bd.get("href"))) else ""
            cards.append(f'        <article class="oaw-pillar-card"{bid}>{tag}<h3>{esc(bd.get("title") or "")}</h3><p>{esc(bd.get("body") or "")}</p>{cta}</article>')
        cards_html = "\n".join(cards)
        sections.append(f'    <section aria-labelledby="oaw-highlights-hdr">\n      <div class="oaw-section-hdr"><h2 id="oaw-highlights-hdr">Key Capabilities</h2></div>\n      <div class="oaw-pillars-grid" data-cols="{cols}">\n{cards_html}\n      </div>\n    </section>')

    domain_cards = []
    for pv in (ov.get("domain_previews") or []):
        if not isinstance(pv, dict):
            continue
        tag = f'<span class="oaw-tag">{esc(pv["badge"])}</span>' if pv.get("badge") else ""
        link = f'<a class="oaw-btn" href="{esc(href)}">Open View</a>' if (href := safe_href(pv.get("href"))) else ""
        domain_cards.append(f'        <article class="oaw-domain-card">{tag}<h3>{esc(pv.get("title") or "")}</h3><p>{esc(pv.get("subtitle") or "")}</p>{link}</article>')
    if domain_cards:
        cards_html = "\n".join(domain_cards)
        sections.append(f'    <section aria-labelledby="oaw-domains-hdr">\n      <div class="oaw-section-hdr"><h2 id="oaw-domains-hdr">Domain Previews</h2><span>Interactive reference surfaces</span></div>\n      <div class="oaw-domains-grid">\n{cards_html}\n      </div>\n    </section>')

    if (diags := [d for raw in (ov.get("architecture_diagrams") or []) if (d := _render_diagram_item(raw, base_dir))]):
        diags_html = "\n".join(diags)
        sections.append(f'    <section aria-labelledby="oaw-arch-hdr">\n      <div class="oaw-section-hdr"><h2 id="oaw-arch-hdr">Architecture</h2></div>\n{diags_html}\n    </section>')
    return sections


def _render_overview_html(config: dict[str, Any], *, bundle: bool, tok_txt: str, ovr_txt: str | None) -> str:
    proj, ov = config.get("project") or {}, config.get("overview") or {}
    proj_title = str(proj.get("title") or proj.get("slug") or "Project")
    desc = str(ov.get("summary") or proj.get("tagline") or proj_title)
    head = render_head(
        config, page_title=proj_title, description=desc, rel_prefix="./",
        bundle=bundle, tok_txt=tok_txt, ovr_txt=ovr_txt, include_docs=False, include_overview=True,
    )
    shell_js = escape_tag_body(read_asset("site-shell.js"), "script")
    body = "\n".join(_render_overview_sections(config))
    return (
        f'<!DOCTYPE html>\n<html lang="en" data-theme="white" data-oaw-route="overview">\n{head}\n<body>\n'
        f'{render_chrome_top(config, current="overview", rel_prefix="./")}\n'
        f'  <main id="oaw-main-content" class="oaw-main">\n{body}\n  </main>\n'
        f'{render_footer(config)}\n  <script>\n{shell_js}\n  </script>\n'
        '  <script defer src="./assets/site-search.js"></script>\n</body>\n</html>\n'
    )


def _normalize_quick_jumps(raw_jumps: list[Any], doc_ids: set[str], *, demo_enabled: bool) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in raw_jumps:
        if isinstance(item, str):
            tid = item.lstrip("#").strip()
            tid = f"doc-{tid}" if (tid and tid not in doc_ids and f"doc-{tid}" in doc_ids) else tid
            if _SAFE_DOC_ID_RE.match(tid):
                out.append({"kind": "doc", "label": tid, "target": tid})
            continue
        if not isinstance(item, dict):
            continue
        lbl, kind = str(item.get("label") or "").strip(), str(item.get("kind") or "").strip().lower()
        raw_t = str(item.get("target") or item.get("href") or "").strip()
        if not lbl or not raw_t:
            continue
        kind = kind or ("doc" if raw_t.startswith("#") else "route")
        if kind == "doc":
            tid = raw_t.lstrip("#").strip()
            tid = f"doc-{tid}" if (tid not in doc_ids and f"doc-{tid}" in doc_ids) else tid
            if _SAFE_DOC_ID_RE.match(tid):
                out.append({"kind": "doc", "label": lbl, "target": tid})
        elif (href := safe_href(raw_t)) and (demo_enabled or ("demo/" not in href and not href.endswith("/demo"))):
            out.append({"kind": "route", "label": lbl, "target": href})
    return out


def _render_jump_control(jump: dict[str, str], *, cls: str = "") -> str:
    cls_attr = f' class="{cls}"' if cls else ""
    if jump["kind"] == "doc":
        return f'<button type="button"{cls_attr} data-doc-jump="{esc(jump["target"])}">{esc(jump["label"])}</button>'
    r_attr = "" if is_external(jump["target"]) else " data-oaw-route-link"
    return f'<a{cls_attr} href="{esc(jump["target"])}"{r_attr}>{esc(jump["label"])}</a>'


def _render_docs_toc(toc: list[dict[str, Any]], jumps: list[dict[str, str]]) -> str:
    parts: list[str] = []
    if jumps:
        parts.append('<div class="oaw-docs-rail-title">Quick Jumps</div>')
        parts.extend(_render_jump_control(j, cls="oaw-docs-rail-link") for j in jumps)
    if toc:
        parts.append('<div class="oaw-docs-rail-title">Guides</div>')
        for doc in toc:
            did = f'doc-{doc["id"]}'
            parts.append(f'<a class="oaw-docs-rail-link" href="#{esc(did)}" data-doc-jump="{esc(did)}">{esc(doc["title"])}</a>')
            for hd in doc.get("headings") or []:
                if hd.get("level") == 2 and hd.get("id") and hd.get("text"):
                    parts.append(f'<a class="oaw-docs-rail-link oaw-docs-sub" href="#{esc(hd["id"])}" data-doc-jump="{esc(hd["id"])}">{esc(hd["text"])}</a>')
    return "\n      ".join(parts)


def _render_docs_html(
    config: dict[str, Any], *, bundle: bool, tok_txt: str, ovr_txt: str | None, compiled: dict[str, Any] | None = None,
) -> str:
    proj, dr = config.get("project") or {}, config.get("docs_reader") or {}
    routes = route_defs(config, from_subdir="docs")
    compiled = compiled if compiled is not None else compile_markdown_docs(dr.get("sources") or [], Path(str(config.get("base_dir") or ".")))
    toc = compiled["toc"]
    jumps = _normalize_quick_jumps(dr.get("quick_jumps") or [], {f"doc-{d['id']}" for d in toc}, demo_enabled=routes["demo"]["enabled"])
    toc_html = _render_docs_toc(toc, jumps)

    docs_title, docs_sub = str(dr.get("title") or "Documentation"), str(dr.get("subtitle") or "")
    first_doc_title = str(toc[0]["title"]) if toc else docs_title
    proj_title = str(proj.get("title") or proj.get("slug") or "Project")
    empty_jumps = [_render_jump_control(j) for j in jumps] if jumps else (
        [f'<button type="button" data-doc-jump="doc-{esc(toc[0]["id"])}">Open {esc(toc[0]["title"])}</button>'] if toc else []
    )
    empty_extra = ("\n          " + "\n          ".join(empty_jumps)) if empty_jumps else ""
    sub_html = f"\n        <p>{esc(docs_sub)}</p>" if docs_sub else ""
    head = render_head(
        config, page_title=f"{docs_title} — {proj_title}", description=docs_sub or str(proj.get("tagline") or docs_title),
        rel_prefix="../", bundle=bundle, tok_txt=tok_txt, ovr_txt=ovr_txt, include_docs=True, subpath="docs/",
    )
    shell_js = escape_tag_body(read_asset("site-shell.js"), "script")
    docs_js = escape_tag_body(read_asset("site-docs-search.js"), "script")
    subbar = (
        '  <div id="oaw-docs-subbar" class="oaw-docs-subbar">'
        '<button id="oaw-docs-toc-trigger" class="oaw-docs-toc-trigger" type="button" aria-haspopup="dialog" aria-controls="oaw-docs-toc-dialog" aria-expanded="false">'
        f'{svg_icon("chapters", 14)}<span>Chapters</span></button>'
        '<span class="oaw-docs-subbar-sep" aria-hidden="true">/</span>'
        f'<span id="oaw-docs-current-chapter" class="oaw-docs-subbar-chapter">{esc(first_doc_title)}</span></div>'
    )
    return (
        f'<!DOCTYPE html>\n<html lang="en" data-theme="white" data-oaw-route="docs">\n{head}\n<body>\n'
        f'{render_chrome_top(config, current="docs", rel_prefix="../")}\n{subbar}\n'
        '  <main id="oaw-main-content" class="oaw-docs-layout">\n'
        f'    <aside class="oaw-docs-rail" aria-label="Documentation Outline">\n      {toc_html}\n    </aside>\n'
        '    <div class="oaw-docs-main">\n'
        f'      <section class="oaw-docs-intro">\n        <h1>{esc(docs_title)}</h1>{sub_html}\n      </section>\n'
        '      <div class="oaw-docs-searchbar" role="search">\n'
        '        <label class="oaw-sr-only" for="oaw-docs-search">Search documentation</label>\n'
        '        <input type="search" id="oaw-docs-search" aria-label="Search documentation" placeholder="Search guides (press /)" autocomplete="off">\n'
        '        <span id="oaw-docs-search-count" class="oaw-docs-search-count" aria-live="polite"></span>\n'
        '        <button type="button" id="oaw-docs-search-clear" class="oaw-docs-search-clear">Clear</button>\n      </div>\n'
        '      <div id="oaw-docs-empty" class="va-empty-state" data-kind="filtered" hidden>\n'
        '        <h2 class="va-empty-title">No matching sections</h2>\n'
        '        <p class="va-empty-copy">No guides matched your search query. Clear the filter or jump directly to a guide.</p>\n'
        f'        <div class="oaw-empty-actions">\n          <button type="button" id="oaw-empty-clear-btn">Clear search</button>{empty_extra}\n        </div>\n      </div>\n'
        f'      <div class="oaw-docs-prose">\n{compiled["sections_html"]}\n      </div>\n'
        '    </div>\n  </main>\n'
        '  <dialog id="oaw-docs-toc-dialog" class="va-modal-sheet" closedby="any" aria-labelledby="oaw-docs-toc-title">\n'
        '    <div class="va-modal-sheet-hdr">\n      <h2 id="oaw-docs-toc-title">Chapters</h2>\n'
        '      <button type="button" data-close-dialog aria-label="Close outline">Close</button>\n    </div>\n'
        f'    <div class="va-modal-sheet-body">\n      <nav class="oaw-docs-toc-list" aria-label="Mobile Documentation Outline">\n      {toc_html}\n      </nav>\n    </div>\n  </dialog>\n'
        f'{render_footer(config)}\n  <script type="application/json" id="oaw-docs-search-index">{json_embed(compiled["search_index"])}</script>\n'
        f'  <script>\n{shell_js}\n  </script>\n  <script>\n{docs_js}\n  </script>\n'
        '  <script defer src="../assets/site-search.js"></script>\n</body>\n</html>\n'
    )


def _render_demo_html(config: dict[str, Any], *, tok_txt: str = "") -> str | None:
    dw = config.get("demo_wrapper") or {}
    if not (dw.get("enabled") and dw.get("entry_path")):
        return None
    raw_entry = str(dw["entry_path"])
    if "\x00" in raw_entry or raw_entry.startswith(("/", "\\")):
        raise ValueError(f"Demo wrapper entry_path escapes project directory: {raw_entry!r}")
    base_resolved = Path(str(config.get("base_dir") or ".")).resolve()
    entry = (base_resolved / raw_entry).resolve()
    if not entry.is_relative_to(base_resolved) or entry == base_resolved:
        raise ValueError(f"Demo wrapper entry_path escapes project directory: {raw_entry!r}")
    if not entry.is_file():
        return None
    html_text = entry.read_text(encoding="utf-8")
    if "__CHROME_CSS__" in html_text or not re.search(r"<body\b[^>]*>", html_text, flags=re.I):
        return None
    if 'id="va-demo-site-strip-css"' not in html_text:
        head_re = r"</head>" if re.search(r"</head>", html_text, flags=re.I) else r"<body\b"
        html_text = re.sub(head_re, lambda m: f"{render_demo_chrome_css(tok_txt)}\n{m.group(0)}", html_text, count=1, flags=re.I)
    if not re.search(r'class\s*=\s*["\'][^"\']*\bva-demo-site-strip\b', html_text):
        bar_html = render_demo_return_bar(config, current="demo")
        html_text = re.sub(r"<body\b[^>]*>", lambda m: f"{m.group(0)}\n{bar_html}", html_text, count=1, flags=re.I)
    if 'id="va-demo-site-shell-js"' not in html_text:
        shell_js = escape_tag_body(read_asset("site-shell.js"), "script")
        body_end = r"</body>" if re.search(r"</body>", html_text, flags=re.I) else r"$"
        html_text = re.sub(body_end, lambda m: f'  <script id="va-demo-site-shell-js">\n{shell_js}\n  </script>\n{m.group(0)}', html_text, count=1, flags=re.I)
    if "assets/site-search.js" not in html_text:
        body_end = r"</body>" if re.search(r"</body>", html_text, flags=re.I) else r"$"
        html_text = re.sub(body_end, lambda m: f'  <script defer src="../assets/site-search.js"></script>\n{m.group(0)}', html_text, count=1, flags=re.I)
    return html_text


def _copy_site_assets(dest: Path, *, render_overview: bool, render_docs: bool) -> None:
    """Copy packaged shell, search, overview, and docs static assets into dest/assets."""
    assets_out = dest / "assets"
    assets_out.mkdir(parents=True, exist_ok=True)
    names = ["site-shell.css", "site-search.css", "site-shell.js", "site-search.js"]
    if render_overview:
        names.append("site-overview.css")
    if render_docs:
        names.extend(["site-docs.css", "site-docs-search.js"])
    for name in names:
        src = ASSETS_DIR / name
        if src.is_file():
            dst = assets_out / name
            if not (dst.exists() and os.path.samefile(src, dst)):
                shutil.copy2(src, dst)


def build_project_site(
    config: dict[str, Any], out_dir: Path, *, bundle: bool = True, tokens_path: Path | None = None,
    overrides_path: Path | None = None, tokens_css: str | None = None, overrides_css: str | None = None,
    render_overview: bool = True, render_docs: bool = True, render_demo: bool = True,
    render_search_index: bool | None = None, extra_search_entries: list[dict[str, Any]] | None = None,
) -> dict[Path, bytes]:
    """Build Overview, Docs, optional Demo routes, and search-index.json for a Quiet UI v9.8.0 site."""
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    tok_src, tok_txt, ovr_src, ovr_txt = _resolve_style_inputs(config, tokens_path, overrides_path, tokens_css, overrides_css)

    if not bundle:
        styles_dir = dest / "styles"
        _copy_style_safe(tok_src, tok_txt, styles_dir / "quiet-ui-tokens.css")
        (styles_dir / "tokens.layered.css").write_text(f"{LAYER_ORDER}\n@layer tokens {{\n{tok_txt}\n}}\n", encoding="utf-8")
        if ovr_src is not None or ovr_txt is not None:
            _copy_style_safe(ovr_src, ovr_txt, styles_dir / "overrides.css")

    _copy_site_assets(dest, render_overview=render_overview, render_docs=render_docs)

    emit_search = render_overview if render_search_index is None else render_search_index
    dr_sources = (config.get("docs_reader") or {}).get("sources") or []
    base_dir = Path(str(config.get("base_dir") or "."))
    docs_payload: dict[str, Any] | None = None
    if render_docs:
        docs_payload = compile_markdown_docs(dr_sources, base_dir)
    elif emit_search and dr_sources:
        try:
            docs_payload = compile_markdown_docs(dr_sources, base_dir)
        except FileNotFoundError:
            docs_payload = None

    emitted: dict[Path, bytes] = {}
    if render_overview:
        ov_path = dest / "index.html"
        ov_bytes = _render_overview_html(config, bundle=bundle, tok_txt=tok_txt, ovr_txt=ovr_txt).encode("utf-8")
        ov_path.write_bytes(ov_bytes)
        emitted[ov_path] = ov_bytes
    if render_docs:
        dc_path = dest / "docs" / "index.html"
        dc_path.parent.mkdir(parents=True, exist_ok=True)
        dc_bytes = _render_docs_html(config, bundle=bundle, tok_txt=tok_txt, ovr_txt=ovr_txt, compiled=docs_payload).encode("utf-8")
        dc_path.write_bytes(dc_bytes)
        emitted[dc_path] = dc_bytes
    if render_demo and (dm_html := _render_demo_html(config, tok_txt=tok_txt)) is not None:
        dm_path = dest / "demo" / "index.html"
        dm_path.parent.mkdir(parents=True, exist_ok=True)
        dm_bytes = dm_html.encode("utf-8")
        dm_path.write_bytes(dm_bytes)
        emitted[dm_path] = dm_bytes
    if emit_search:
        payload = build_project_search_index(config, docs_payload=docs_payload, extra_entries=extra_search_entries)
        search_path = write_project_search_index(dest, payload)
        emitted[search_path] = search_path.read_bytes()
    return emitted
