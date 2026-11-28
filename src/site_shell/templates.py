# SPDX-License-Identifier: Apache-2.0
"""HTML/CSS/head template helpers for Quiet UI v9.8.0 project-site routes."""

from __future__ import annotations

import html
import json
import re
import urllib.parse
from pathlib import Path
from typing import Any

_PKG_DIR = Path(__file__).resolve().parent
ASSETS_DIR = _PKG_DIR / "assets"
REPO_ROOT = _PKG_DIR.parents[1]
LAYER_ORDER = "@layer reset, tokens, shell, archetypes, evidence, components, views, utilities;"
_LAYER_DECL_RE = re.compile(r"^\s*@layer\s+[a-z0-9_-]+\s*,[^;]+;\s*", re.IGNORECASE | re.MULTILINE)
_THEME_CHOICES = (("white", "Pure White"), ("paper", "Warm Paper"), ("dark", "Dark"), ("dark-paper", "Dark Paper"))
_DEFAULT_PILLARS = (
    {"id": "home", "title": "Home", "desc": "Open Agentic Workbench overview", "href": "https://oaworkbench.org/", "status": "link"},
    {"id": "learn", "title": "Learn", "desc": "Interactive science worlds, chemistry and equations", "href": "https://learn.oaworkbench.org/", "status": "preview", "badge": "Open Preview"},
    {"id": "projects", "title": "Projects", "desc": "Open-source developer tools and browser demos", "href": "https://projects.oaworkbench.org/", "status": "active", "badge": "Active"},
    {"id": "research", "title": "Research", "desc": "Primary-source manuscript and historical studies", "href": "https://research.oaworkbench.org/", "status": "preview", "badge": "Preview"},
)
_SVG_PATHS = {
    "chev": '<path fill="none" d="M4 6l4 4 4-4"/>',
    "chevron-down": '<path fill="none" d="M4 6l4 4 4-4"/>',
    "arrow-left": '<path fill="none" d="M12.5 8H3.5M7 4.5 3.5 8 7 11.5"/>',
    "check": '<path fill="none" d="M3.5 8.5 6.5 11.5 12.5 5"/>',
    "user": '<circle cx="8" cy="5.2" r="2.6" fill="none"/><path fill="none" d="M3 13.5c.8-2.3 2.7-3.5 5-3.5s4.2 1.2 5 3.5"/>',
    "grid": (
        '<circle cx="3" cy="3" r="1.35" fill="currentColor"/><circle cx="8" cy="3" r="1.35" fill="currentColor"/><circle cx="13" cy="3" r="1.35" fill="currentColor"/>'
        '<circle cx="3" cy="8" r="1.35" fill="currentColor"/><circle cx="8" cy="8" r="1.35" fill="currentColor"/><circle cx="13" cy="8" r="1.35" fill="currentColor"/>'
        '<circle cx="3" cy="13" r="1.35" fill="currentColor"/><circle cx="8" cy="13" r="1.35" fill="currentColor"/><circle cx="13" cy="13" r="1.35" fill="currentColor"/>'
    ),
    "layers": '<path fill="none" d="M8 2 14 5.2 8 8.4 2 5.2 8 2Z"/><path fill="none" d="M2 8.2l6 3.2 6-3.2"/><path fill="none" d="M2 11.2l6 3.2 6-3.2"/>',
    "cubes": '<path fill="none" d="M8 2 13.5 5v6L8 14 2.5 11V5L8 2Z"/><path fill="none" d="M2.5 5 8 8l5.5-3M8 8v6"/>',
    "desktop": '<rect x="2" y="2.8" width="12" height="8.4" rx="1.4" fill="none"/><path fill="none" d="M5.5 13.5h5M8 11.2v2.3"/>',
    "terminal": '<path fill="none" d="M3 4.5 6.5 8 3 11.5M8.5 11.5H13"/>',
    "home": '<path fill="none" d="M2.5 7.5 8 3l5.5 4.5V13.5h-4v-3.5h-3v3.5h-4z"/>',
    "book": '<path fill="none" d="M2.5 3.5h4.2c.7 0 1.3.5 1.3 1.2v8.3c-.4-.5-1-.7-1.6-.7H2.5zm11 0H9.3c-.7 0-1.3.5-1.3 1.2v8.3c.4-.5 1-.7 1.6-.7h3.9z"/>',
    "compass": '<circle cx="8" cy="8" r="5.5" fill="none"/><path fill="none" d="M10.4 5.6 9 9l-3.4 1.4L7 7z"/>',
    "code": '<path fill="none" d="M5.5 4.5 2 8l3.5 3.5M10.5 4.5 14 8l-3.5 3.5M9 3.5l-2 9"/>',
    "search": '<circle cx="7" cy="7" r="4.5" fill="none"/><path fill="none" d="M10.5 10.5L14 14"/>',
    "columns": '<path fill="none" d="M2.5 13.5h11M3.5 11.5h9M4.5 6.5v5M8 6.5v5M11.5 6.5v5M2.5 6.5 8 2.5l5.5 4z"/>',
    "chapters": '<path fill="none" d="M2.5 4h1.5M6 4h7.5M2.5 8h1.5M6 8h7.5M2.5 12h1.5M6 12h7.5"/>',
}


def svg_icon(name: str, size: int = 15, cls: str = "") -> str:
    """Return an inline currentColor SVG icon with explicit fill on all paths."""
    body = _SVG_PATHS.get(name, _SVG_PATHS["layers"])
    cls_attr = f' class="{esc(cls)}"' if cls else ""
    return (
        f'<svg{cls_attr} width="{size}" height="{size}" viewBox="0 0 16 16" '
        f'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


SUPPLEMENTAL_CSS = """
@layer evidence {
  .va-figure-card.qe-figure { margin: 0; color: var(--text-primary); display: flex; flex-direction: column; gap: 0.75rem; }
  .va-figure-hdr.qe-card-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.5rem; }
  .qe-fig-title { margin: 0; font-size: var(--ts-md); font-weight: 700; color: var(--text-primary); line-height: 1.3; }
  .qe-fig-badges { display: inline-flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; }
  .va-pill[data-variant="tag"] {
    display: inline-flex; align-items: center; padding: 0.15rem 0.45rem; border-radius: var(--radius-xs, 2px);
    border: 1px solid var(--border-hairline); background: var(--bg-elevated); color: var(--text-secondary);
    font-family: var(--font-mono); font-size: var(--ts-xs); font-weight: 600;
  }
  .qe-schematic-wrap, .va-figure-scroll { min-inline-size: 0; max-inline-size: 100%; overflow-x: auto; }
  .qe-spec-drawer { border-block-start: 1px solid var(--border-hairline); padding-block-start: 0.55rem; }
  .qe-spec-summary { font-size: var(--ts-xs); font-weight: 600; color: var(--text-muted); }
  .qe-spec-pre {
    margin: 0.5rem 0 0; padding: 0.75rem; border-radius: var(--radius-sm, 6px); border: 1px solid var(--border-hairline);
    background: var(--bg-elevated); color: var(--text-primary); font-size: var(--ts-xs); line-height: 1.5; max-inline-size: 100%; overflow-x: auto;
  }
}
@layer views {
  .oaw-docs-intro { display: flex; flex-direction: column; gap: 0.45rem; }
  .oaw-docs-intro h1 { font-family: var(--font-serif); font-size: var(--ts-display); line-height: 1.2; font-weight: 700; color: var(--text-primary); }
  .oaw-docs-intro p { font-size: var(--ts-prose); line-height: 1.55; color: var(--text-secondary); max-inline-size: min(var(--measure-prose, 72ch), 100%); }
  .oaw-docs-rail-link.oaw-docs-sub { padding-inline-start: 1.15rem; font-size: var(--ts-xs); color: var(--text-muted); }
  .oaw-code-hdr {
    display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
    padding-block-end: 0.5rem; margin-block-end: 0.55rem; border-block-end: 1px solid var(--border-hairline);
    font-size: var(--ts-xs); color: var(--text-muted);
  }
  .oaw-code-lang { font-family: var(--font-mono); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
  .oaw-callout {
    display: flex; flex-direction: column; gap: 0.35rem; padding: 0.75rem 0.95rem;
    border: 1px solid var(--border-hairline); border-inline-start: 3px solid var(--accent-primary);
    border-radius: 0 var(--radius-sm, 6px) var(--radius-sm, 6px) 0; background: var(--bg-elevated);
  }
  .oaw-callout-title { font-size: var(--ts-xs); font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--accent-primary); }
  .oaw-diagram-caption { font-size: var(--ts-xs); color: var(--text-muted); line-height: 1.45; }
}
""".strip()


def esc(val: Any) -> str:
    """HTML-escape any value including quotes."""
    return html.escape(str(val or ""), quote=True)


def json_embed(obj: Any) -> str:
    """Serialize JSON safely for inline HTML <script> embedding."""
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")


def escape_tag_body(text: str, tag: str) -> str:
    """Prevent closing style/script tags inside inline blocks."""
    return re.sub(rf"</\s*{tag}", f"<\\/{tag}", text, flags=re.IGNORECASE)


def read_asset(name: str) -> str:
    """Read a packaged CSS/JS asset file, stripping any leading Apache-2.0 SPDX header."""
    raw = (ASSETS_DIR / name).read_text(encoding="utf-8")
    return re.sub(r"^\s*/\*\s*SPDX-License-Identifier:\s*Apache-2\.0\s*\*/[ \t]*\r?\n?", "", raw)


def safe_href(raw: Any, fallback: str = "") -> str:
    """Allow http(s), relative, and hash URLs while rejecting unsafe schemes."""
    cleaned = re.sub(r"[\x00-\x20\x7f]", "", str(raw or "")).strip()
    if not cleaned or cleaned.startswith(("//", "\\\\", "/\\", "\\/")):
        return fallback
    parsed = urllib.parse.urlsplit(cleaned)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        return fallback
    first_seg = cleaned.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    return fallback if (not parsed.scheme and ":" in first_seg) else cleaned


def is_external(href: str) -> bool:
    """Return True for absolute/schemed/hash/network-path URLs that need no rel_prefix."""
    cleaned = re.sub(r"[\x00-\x20\x7f]", "", str(href or "")).strip()
    return cleaned.startswith(("//", "\\\\", "/\\", "\\/", "#")) or bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", cleaned))


def to_page_href(raw_href: str, rel_prefix: str) -> str:
    """Resolve a root-relative route path relative to current page depth."""
    href = safe_href(raw_href)
    if not href or is_external(href):
        return href
    cleaned = href[2:] if href.startswith("./") else href.lstrip("/")
    return f"{rel_prefix}{cleaned}index.html" if cleaned.endswith("/") else f"{rel_prefix}{cleaned}"


def route_defs(config: dict[str, Any], *, from_subdir: str = "") -> dict[str, dict[str, Any]]:
    """Compute normalized overview/demo/docs labels, hrefs, and flags."""
    routes, dw = config.get("routes") or {}, config.get("demo_wrapper") or {}
    rel_prefix = "../" if from_subdir else "./"
    ov_raw, dm_raw, dc_raw = routes.get("overview") or {}, routes.get("demo") or {}, routes.get("docs") or {}
    return {
        "overview": {"label": str(ov_raw.get("label") or "Overview"), "href": to_page_href(str(ov_raw.get("href") or "index.html"), rel_prefix)},
        "demo": {
            "label": str(dm_raw.get("label") or "Demo"),
            "href": "./index.html" if from_subdir == "demo" else to_page_href(str(dm_raw.get("href") or "demo/index.html"), rel_prefix),
            "enabled": bool(dm_raw.get("enabled", dw.get("enabled", False))),
            "legacy_query_keys": [str(k) for k in (dm_raw.get("legacy_query_keys") or []) if str(k).strip()],
        },
        "docs": {"label": str(dc_raw.get("label") or "Docs"), "href": "./index.html" if from_subdir == "docs" else to_page_href(str(dc_raw.get("href") or "docs/index.html"), rel_prefix)},
    }


def render_styles_head(
    *, bundle: bool, rel_prefix: str, tok_txt: str, ovr_txt: str | None, include_docs: bool, include_overview: bool = False,
) -> str:
    """Render layered <style> and/or <link> stylesheet tags for <head>."""
    shell_css = read_asset("site-shell.css")
    overview_css = read_asset("site-overview.css") if include_overview else ""
    docs_css = read_asset("site-docs.css") if include_docs else ""
    search_css = read_asset("site-search.css")
    extra_css = [_LAYER_DECL_RE.sub("", c).strip() for c in (shell_css, overview_css, docs_css, search_css) if c.strip()]
    if bundle:
        parts = [LAYER_ORDER, f"@layer tokens {{\n{tok_txt}\n}}"]
        if ovr_txt is not None:
            ovr_clean = _LAYER_DECL_RE.sub("", ovr_txt).strip()
            parts.append(ovr_clean if "@layer" in ovr_clean else f"@layer tokens {{\n{ovr_clean}\n}}")
        parts.extend([*extra_css, SUPPLEMENTAL_CSS])
        merged = escape_tag_body("\n\n".join(parts), "style")
        return f'  <style id="oaw-site-styles">\n{merged}\n  </style>'

    links = [f'  <style id="oaw-layer-order">{LAYER_ORDER}</style>', f'  <link rel="stylesheet" href="{esc(rel_prefix)}styles/tokens.layered.css">']
    if ovr_txt is not None:
        links.append(f'  <link rel="stylesheet" href="{esc(rel_prefix)}styles/overrides.css">')
    merged_shell = escape_tag_body("\n\n".join([*extra_css, SUPPLEMENTAL_CSS]), "style")
    links.append(f'  <style id="oaw-site-shell-css">\n{merged_shell}\n  </style>')
    return "\n".join(links)


def render_head(
    config: dict[str, Any], *, page_title: str, description: str, rel_prefix: str, bundle: bool, tok_txt: str, ovr_txt: str | None, include_docs: bool, include_overview: bool = False, subpath: str = "",
) -> str:
    """Render <head> metadata, OpenGraph/Twitter tags, FOUC theme guard, and legacy redirect."""
    proj, sp, routes = config.get("project") or {}, config.get("social_preview") or {}, route_defs(config)
    site_url = safe_href(proj.get("site_url"))
    canonical = urllib.parse.urljoin(site_url.rstrip("/") + "/", subpath) if site_url else ""
    img_rel = str(sp.get("image_path") or "").lstrip("./")
    og_image = urllib.parse.urljoin(site_url.rstrip("/") + "/", img_rel) if (img_rel and site_url) else (f"{rel_prefix}{img_rel}" if img_rel else "")
    og_title, og_desc = str(sp.get("title") or page_title), str(sp.get("subtitle") or description)

    favicon_svg = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
        "%3Crect width='16' height='16' rx='3.5' fill='%231D4ED8'/%3E"
        "%3Cpath d='M3.5 5.2h9M3.5 8h9M3.5 10.8h5.5' fill='none' stroke='%23FFFFFF' stroke-width='1.6' stroke-linecap='round'/%3E%3C/svg%3E"
    )
    metas = [
        '  <meta charset="utf-8">', '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        '  <meta name="color-scheme" content="light dark">', f'  <link rel="icon" type="image/svg+xml" href="{favicon_svg}">',
        f"  <title>{esc(page_title)}</title>",
        f'  <meta name="description" content="{esc(description)}">', '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{esc(og_title)}">', f'  <meta property="og:description" content="{esc(og_desc)}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{esc(og_title)}">', f'  <meta name="twitter:description" content="{esc(og_desc)}">',
    ]
    if canonical:
        metas.extend([f'  <link rel="canonical" href="{esc(canonical)}">', f'  <meta property="og:url" content="{esc(canonical)}">'])
    if og_image:
        metas.extend([
            f'  <meta property="og:image" content="{esc(og_image)}">',
            f'  <meta property="og:image:width" content="{int(sp.get("width") or 1280)}">',
            f'  <meta property="og:image:height" content="{int(sp.get("height") or 640)}">',
            f'  <meta name="twitter:image" content="{esc(og_image)}">',
        ])
    fouc_js = (
        "(function(){try{var v={white:1,paper:1,'dark-paper':1,dark:1};var p=new URLSearchParams(window.location.search).get('theme');"
        "var t=(p&&v[p])?p:null;if(!t){try{var s1=window.localStorage.getItem('oaw_theme_v99'),s2=window.localStorage.getItem('quiet-ui-site-theme');"
        "var s=(s1&&v[s1])?s1:((s2&&v[s2])?s2:null);if(s)t=s;}catch(_e){}}"
        "t=t||'white';document.documentElement.dataset.theme=t;var m=document.querySelector('meta[name=\"color-scheme\"]');"
        "if(m)m.setAttribute('content',(t==='dark'||t==='dark-paper')?'dark':'light');}catch(_e){}})();"
    )
    metas.append(f"  <script>{fouc_js}</script>")
    if not include_docs and routes["demo"]["enabled"] and routes["demo"]["legacy_query_keys"]:
        keys_js, demo_js = json_embed(routes["demo"]["legacy_query_keys"]), json_embed(routes["demo"]["href"])
        metas.append(
            f"  <script>(function(){{try{{var k={keys_js},q=new URLSearchParams(window.location.search);"
            "for(var i=0;i<k.length;i+=1){if(q.has(k[i])&&!(k[i]==='mode'&&(q.get('mode')||'').toLowerCase()==='overview'))"
            f"{{window.location.replace({demo_js}+window.location.search+window.location.hash);return;}}}}}}catch(_e){{}}}})();</script>"
        )
    metas.append(
        render_styles_head(
            bundle=bundle, rel_prefix=rel_prefix, tok_txt=tok_txt, ovr_txt=ovr_txt,
            include_docs=include_docs, include_overview=include_overview,
        )
    )
    return "<head>\n" + "\n".join(metas) + "\n</head>"


def _render_projects_switcher(config: dict[str, Any], rel_prefix: str, proj_title: str, hub_label: str, hub_url: str) -> str:
    hub_projects = [p for p in ((config.get("hub") or {}).get("projects") or []) if isinstance(p, dict)]
    if not hub_projects:
        return ""
    chev = svg_icon("chev", 12, "oaw-btn-chev")
    rows = [
        f'<li class="oaw-pop-row-sep"><a class="oaw-pop-item" href="{esc(hub_url)}">'
        f'<span class="oaw-pop-icon-well" aria-hidden="true">{svg_icon("arrow-left", 14)}</span>'
        '<span class="oaw-pop-row-body"><span class="oaw-pop-row-title">All Projects</span></span></a></li>'
    ]
    for item in hub_projects:
        raw_u = str(item.get("url") or "")
        url = to_page_href(raw_u, rel_prefix) if (raw_u and not is_external(raw_u)) else safe_href(raw_u, "#")
        is_curr = bool(item.get("current"))
        curr_attr = ' aria-current="page"' if is_curr else ""
        icon_name = "layers" if "ui" in str(item.get("slug") or "") else "cubes"
        sub = f'<span class="oaw-pop-row-sub">{esc(item["tagline"])}</span>' if item.get("tagline") else ""
        trail = svg_icon("check", 14, "oaw-pop-check") if is_curr else (f'<span class="oaw-pop-badge">{esc(item["badge"])}</span>' if item.get("badge") else "")
        rows.append(
            f'<li><a class="oaw-pop-item{" is-active" if is_curr else ""}" href="{esc(url)}"{curr_attr}>'
            f'<span class="oaw-pop-icon-well" aria-hidden="true">{svg_icon(icon_name, 14)}</span>'
            f'<span class="oaw-pop-row-body"><span class="oaw-pop-row-title">{esc(item.get("title") or item.get("slug") or "")}</span>{sub}</span>'
            f"{trail}</a></li>"
        )
    rows_html = "\n          ".join(rows)
    return (
        '      <div class="oaw-switcher-wrap">\n'
        f'        <button type="button" id="oaw-projects-btn" class="oaw-projects-btn" popovertarget="oaw-projects-popover" aria-controls="oaw-projects-popover" aria-expanded="false">'
        f'<span class="oaw-projects-label">{esc(proj_title)}</span>{chev}</button>\n'
        '        <div id="oaw-projects-popover" class="oaw-popover oaw-projects-popover" popover="auto" aria-label="Projects Switcher">\n'
        '          <div class="oaw-popover-label">Projects</div>\n'
        f'          <ul class="oaw-pop-list">\n          {rows_html}\n          </ul>\n        </div>\n      </div>\n'
    )


def _render_pillar_switcher(config: dict[str, Any], hub_url: str, rel_prefix: str = "./") -> str:
    pillars = [dict(p) for p in ((config.get("hub") or {}).get("pillars") or _DEFAULT_PILLARS) if isinstance(p, dict)]
    icon_map = {"home": "home", "learn": "book", "projects": "cubes", "research": "columns"}
    rows = []
    for item in pillars:
        pid = str(item.get("id") or "").lower()
        status = str(item.get("status") or "link").lower()
        href_raw = safe_href(item.get("href"))
        href = to_page_href(href_raw, rel_prefix) if href_raw else (hub_url if pid == "projects" else "")
        badge_cls = "oaw-pop-badge oaw-pop-badge--preview" if status == "preview" else "oaw-pop-badge"
        badge = f'<span class="{badge_cls}">{esc(item["badge"])}</span>' if item.get("badge") else ""
        body = (
            f'<span class="oaw-pop-icon-well" aria-hidden="true">{svg_icon(icon_map.get(pid, "cubes"), 14)}</span>'
            f'<span class="oaw-pop-row-body"><span class="oaw-pop-row-title">{esc(item.get("title") or "")}</span>'
            + (f'<span class="oaw-pop-row-sub">{esc(item["desc"])}</span>' if item.get("desc") else "")
            + f"</span>{badge}"
        )
        if status == "soon" or not href:
            rows.append(f'<li><div class="oaw-pop-item is-soon" aria-disabled="true">{body}</div></li>')
        else:
            is_act = status == "active"
            curr = ' aria-current="page"' if is_act else ""
            rows.append(f'<li><a class="oaw-pop-item{" is-active" if is_act else ""}" href="{esc(href)}"{curr}>{body}</a></li>')
    rows_html = "\n          ".join(rows)
    return (
        '      <div class="oaw-pillar-wrap">\n'
        f'        <button type="button" id="oaw-pillar-btn" class="oaw-pillar-btn" popovertarget="oaw-pillar-popover" aria-controls="oaw-pillar-popover" aria-expanded="false" aria-label="Open Agentic Workbench Ecosystem" title="Open Agentic Workbench">{svg_icon("grid", 14)}</button>\n'
        '        <div id="oaw-pillar-popover" class="oaw-popover oaw-pillar-popover" popover="auto" aria-label="Open Agentic Workbench Ecosystem">\n'
        '          <div class="oaw-popover-label">Open Agentic Workbench</div>\n'
        f'          <ul class="oaw-pop-list">\n          {rows_html}\n          </ul>\n        </div>\n      </div>\n'
    )


def _render_user_menu(config: dict[str, Any]) -> str:
    proj = config.get("project") or {}
    um = config.get("user_menu") or {}
    repo_url = safe_href(proj.get("repo_url"))
    owner = ""
    if repo_url:
        parsed = urllib.parse.urlsplit(repo_url)
        segs = [s for s in parsed.path.split("/") if s]
        if parsed.netloc.lower() == "github.com" and segs:
            owner = segs[0]
    user_label = str(um.get("label") or (f"@{owner}" if owner else "@owner")).strip()
    profile_url = safe_href(um.get("profile_url")) or (f"https://github.com/{owner}" if owner else "")
    repo_label = str(um.get("repo_label") or "GitHub Repository").strip()
    theme_btns = "\n          ".join(
        f'<button type="button" class="oaw-theme-opt{" is-active" if val == "white" else ""}" data-theme-opt="{val}" aria-pressed="{"true" if val == "white" else "false"}">'
        f'<span class="oaw-theme-dot" data-theme="{val}" aria-hidden="true"></span>'
        f'<span class="oaw-theme-label">{esc(lbl)}</span>{svg_icon("check", 14, "oaw-theme-check")}</button>'
        for val, lbl in _THEME_CHOICES
    )
    links = []
    if repo_url:
        links.append(
            f'<a class="oaw-pop-row oaw-pop-row--compact" href="{esc(repo_url)}" target="_blank" rel="noopener noreferrer">'
            f'<span class="oaw-pop-icon-well" aria-hidden="true">{svg_icon("code", 14)}</span>'
            f'<span class="oaw-pop-row-body"><span class="oaw-pop-row-title">{esc(repo_label)}</span></span></a>'
        )
    if profile_url:
        links.append(
            f'<a class="oaw-pop-row oaw-pop-row--compact" href="{esc(profile_url)}" target="_blank" rel="noopener noreferrer">'
            f'<span class="oaw-pop-icon-well" aria-hidden="true">{svg_icon("user", 14)}</span>'
            f'<span class="oaw-pop-row-body"><span class="oaw-pop-row-title">{esc(user_label)}</span></span></a>'
        )
    links_html = ('\n          <hr class="oaw-pop-sep">\n          <div class="oaw-popover-label">Account &amp; Source</div>\n          <div class="oaw-pop-list">\n            ' + "\n            ".join(links) + "\n          </div>") if links else ""
    return (
        '      <div class="oaw-user-wrap">\n'
        f'        <button type="button" id="oaw-user-btn" class="oaw-user-btn" popovertarget="oaw-user-popover" aria-controls="oaw-user-popover" aria-expanded="false" aria-label="{esc(user_label)} menu and theme" title="{esc(user_label)}">'
        f'{svg_icon("user", 14)}<span class="oaw-user-label">{esc(user_label)}</span>{svg_icon("chev", 12, "oaw-btn-chev")}</button>\n'
        '        <div id="oaw-user-popover" class="oaw-popover oaw-user-popover" popover="auto" aria-label="Color Theme and Account Menu">\n'
        '          <div class="oaw-popover-label">Color Theme</div>\n'
        f'          <div class="oaw-theme-list" role="group" aria-label="Color Theme">\n          {theme_btns}\n          </div>{links_html}\n'
        '        </div>\n      </div>\n'
    )


def _render_search_trigger(config: dict[str, Any], rel_prefix: str) -> str:
    """Render the unified topbar search modal trigger button."""
    site_url = safe_href((config.get("project") or {}).get("site_url"))
    return (
        f'      <button type="button" id="oaw-search-btn" class="oaw-search-trigger" '
        f'aria-haspopup="dialog" aria-controls="oaw-search-dialog" '
        f'data-search-index="{esc(rel_prefix)}search-index.json" data-site-url="{esc(site_url)}" '
        'aria-label="Search site and documentation (Ctrl+K)">'
        f'{svg_icon("search", 15)}<span class="oaw-search-text">Search</span>'
        '<kbd class="oaw-search-kbd">Ctrl+K</kbd></button>\n'
    )


def render_chrome_top(config: dict[str, Any], *, current: str, rel_prefix: str, is_demo: bool = False) -> str:
    """Render skip link, unified 46px single-bar OAW topbar, route menu, search trigger, and popovers."""
    proj, hub = config.get("project") or {}, config.get("hub") or {}
    from_sub = "demo" if (is_demo or current == "demo") else ("docs" if current == "docs" else "")
    routes = route_defs(config, from_subdir=from_sub)
    proj_title = str(proj.get("title") or proj.get("slug") or "Project")
    hub_label = str(hub.get("label") or "OAW Projects")
    hub_raw = safe_href(hub.get("hub_url"))
    hub_url = to_page_href(hub_raw, rel_prefix) if hub_raw else routes["overview"]["href"]

    nav_specs = [("overview", routes["overview"]["label"], routes["overview"]["href"])]
    if routes["demo"]["enabled"] or is_demo or current == "demo":
        nav_specs.append(("demo", routes["demo"]["label"], routes["demo"]["href"]))
    nav_specs.append(("docs", routes["docs"]["label"], routes["docs"]["href"]))

    active_route_label = next((lbl for key, lbl, _ in nav_specs if key == current), routes.get(current, {}).get("label") or "Overview")
    nav_cls = "oaw-nav-links va-demo-strip-links" if is_demo else "oaw-nav-links"
    route_items = "\n          ".join(
        f'<li><a class="oaw-nav-link{" is-active" if key == current else ""}" data-oaw-route-link="{key}" href="{esc(href)}"'
        + (' aria-current="page"' if key == current else "")
        + f'><span>{esc(lbl)}</span>{svg_icon("check", 14, "oaw-pop-check") if key == current else ""}</a></li>'
        for key, lbl, href in nav_specs
    )
    nav_wrap = (
        '      <nav class="oaw-nav-wrap" aria-label="Primary Navigation">\n'
        '        <button type="button" id="oaw-route-btn" class="oaw-route-btn" popovertarget="oaw-route-menu" '
        'aria-controls="oaw-route-menu" aria-expanded="false" aria-label="Switch route">'
        f'<span id="oaw-route-label" class="oaw-route-label">{esc(active_route_label)}</span>{svg_icon("chevron-down", 12)}</button>\n'
        '        <div id="oaw-route-menu" class="oaw-route-menu">\n'
        f'          <ul class="{nav_cls}" role="list">\n          {route_items}\n          </ul>\n'
        '        </div>\n      </nav>\n'
    )

    hdr_cls = "va-demo-site-strip oaw-topbar oaw-topbar--demo" if is_demo else "oaw-topbar"
    skip = "" if is_demo else '  <a class="oaw-skip-link" href="#oaw-main-content">Skip to content</a>\n'
    projects_ctrl = _render_projects_switcher(config, rel_prefix, proj_title, hub_label, hub_url)
    search_ctrl = _render_search_trigger(config, rel_prefix)
    pillar_ctrl = _render_pillar_switcher(config, hub_url, rel_prefix)
    user_ctrl = _render_user_menu(config)
    header = (
        f'  <header class="{hdr_cls}" role="banner">\n    <div class="oaw-topbar-left">\n'
        f'      <a class="oaw-brand-link" href="{esc(hub_url)}">{esc(hub_label)}</a>\n'
        f"{projects_ctrl}{nav_wrap}"
        '    </div>\n    <div class="oaw-topbar-right">\n'
        f"{search_ctrl}{pillar_ctrl}{user_ctrl}"
        '    </div>\n  </header>'
    )
    if is_demo:
        return f'<div class="oaw-demo-chrome" data-theme="white">\n{header}\n</div>'
    return f"{skip}{header}"


def render_footer(config: dict[str, Any]) -> str:
    """Render shared project-site footer."""
    proj, hub = config.get("project") or {}, config.get("hub") or {}
    parts = [str(proj.get("title") or proj.get("slug") or "Project")]
    if proj.get("version"):
        parts.append(f"v{proj['version']}")
    if proj.get("license_summary"):
        parts.append(str(proj["license_summary"]))
    links = [f'<a href="{esc(u)}">Repository</a>' for u in [safe_href(proj.get("repo_url"))] if u]
    if (hub_u := safe_href(hub.get("hub_url"))) and hub.get("label"):
        links.append(f'<a href="{esc(hub_u)}">{esc(hub["label"])}</a>')
    right_joined = " · ".join(links)
    right = f"      <span>{right_joined}</span>\n" if links else ""
    left_joined = esc(" · ".join(parts))
    return f'  <footer class="oaw-site-footer">\n    <div class="oaw-footer-inner">\n      <span>{left_joined}</span>\n{right}    </div>\n  </footer>'
