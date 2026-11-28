# SPDX-License-Identifier: Apache-2.0
"""Deterministic OAW project search-index compiler (shared v1.5.0 schema)."""

from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path
from typing import Any

SEARCH_INDEX_VERSION = "1.5.0"
DEFAULT_UPDATED_AT = "2026-11-27"
MAX_SUMMARY_LEN = 180
MAX_KEYWORDS = 16

_FORBIDDEN_DOC_TOKEN_RE = re.compile(r"demo([_-])(?:doc|session|transcript)", re.I)
_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "into", "is", "it", "of", "on", "or", "our", "that", "the", "their",
    "this", "to", "with", "your",
})


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"


def _safe_doc_entry_id(slug: str, suffix: str) -> str:
    clean = suffix[4:] if suffix.startswith("doc-") else suffix
    cand = f"{slug}-{clean}" if (slug and clean == "docs") else (f"{slug}-doc-{clean}" if slug else (clean if clean == "docs" else f"doc-{clean}"))
    if _FORBIDDEN_DOC_TOKEN_RE.search(cand):
        repl = "guides" if clean == "docs" else f"guide-{clean}"
        return f"{slug}-{repl}" if slug else repl
    return cand


def _summarize(text: Any, limit: int = MAX_SUMMARY_LEN) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    head = clean[: limit - 3].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{head or clean[: limit - 3]}..."


def _normalize_site_url(raw_url: Any) -> str:
    cleaned = str(raw_url or "").strip()
    return f"{cleaned.rstrip('/')}/" if cleaned else ""


def _resolve_url(raw_href: Any, site_url: str) -> str:
    href = str(raw_href or "").strip()
    if not href:
        return site_url
    if href.startswith(("http://", "https://")):
        return href
    if href.startswith("#"):
        return f"{site_url}{href}" if site_url else href
    rel = re.sub(r"^(?:\.\./|\./|/)+", "", href)
    return urllib.parse.urljoin(site_url, rel) if site_url else rel


def _route_dir_url(raw_href: Any, default_dir: str, site_url: str) -> str:
    href = str(raw_href or default_dir).strip() or default_dir
    if href.endswith("/index.html"):
        href = href[: -len("index.html")]
    elif href == "index.html":
        href = ""
    return _resolve_url(href, site_url)


def _extract_tokens(text: Any) -> list[str]:
    return [
        tok for raw in re.findall(r"[a-z0-9][a-z0-9._-]*", str(text or "").lower())
        if len(tok := raw.strip("._-")) >= 2 and tok not in _STOPWORDS
    ]


def _normalize_keywords(
    explicit: Any = None, *, text_sources: tuple[Any, ...] = (), limit: int = MAX_KEYWORDS
) -> list[str]:
    items: list[str] = []
    if isinstance(explicit, str):
        items.extend(part.strip().lower() for part in explicit.split(","))
    elif isinstance(explicit, (list, tuple, set)):
        items.extend(entry.strip().lower() for entry in explicit if isinstance(entry, str))
    for src in text_sources:
        vals = src if isinstance(src, (list, tuple, set)) else (src,)
        for v in vals:
            items.extend(_extract_tokens(v))
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
            if len(out) >= limit:
                break
    return out


def _make_entry(eid: str, title: str, cat: str, summary: str, keywords: list[str], url: str) -> dict[str, Any]:
    return {"id": eid, "pillar": "projects", "title": title, "category": cat, "summary": _summarize(summary or title), "keywords": keywords[:MAX_KEYWORDS], "url": url}


def _overview_item_url(item: dict[str, Any], group_key: str, site_url: str) -> str:
    if item.get("anchor"):
        return _resolve_url(f"#{str(item['anchor']).lstrip('#')}", site_url)
    if item.get("url"):
        return _resolve_url(item["url"], site_url)
    if item.get("id") and (group_key == "plain_language_blocks" or not item.get("href")):
        return _resolve_url(f"#{item['id']}", site_url)
    return _resolve_url(item.get("href"), site_url) if item.get("href") else site_url


def _collect_overview_entries(
    slug: str, project_title: str, site_url: str, config: dict[str, Any], demo_enabled: bool
) -> list[dict[str, Any]]:
    proj = config.get("project") if isinstance(config.get("project"), dict) else {}
    ov = config.get("overview") if isinstance(config.get("overview"), dict) else {}
    pills = [p.get("slug") or p.get("label") if isinstance(p, dict) else p for p in (ov.get("command_pills") or [])]
    ov_summary = str(ov.get("summary") or proj.get("tagline") or ov.get("headline") or project_title)
    ov_kw = _normalize_keywords(pills, text_sources=(slug, project_title, proj.get("tagline"), ov.get("kicker"), ov.get("headline")))
    entries = [_make_entry(f"{slug}-overview" if slug else "overview", project_title, "Overview", ov_summary, ov_kw, site_url)]

    for group_key in ("highlights", "cards", "sections", "plain_language_blocks"):
        raw_items = ov.get(group_key)
        if not isinstance(raw_items, list):
            continue
        default_cat = "Highlight" if group_key in ("highlights", "cards", "plain_language_blocks") else "Overview"
        for idx, raw_item in enumerate(raw_items, start=1):
            item = raw_item if isinstance(raw_item, dict) else {"title": f"Highlight {idx}", "body": str(raw_item)}
            title = str(item.get("title") or item.get("label") or item.get("name") or "").strip()
            body = str(item.get("summary") or item.get("description") or item.get("desc") or item.get("body") or item.get("subtitle") or "").strip()
            if not title and not body:
                continue
            raw_id = str(item.get("id") or item.get("slug") or _slugify(title or body[:40])).strip()
            eid = f"{slug}-{_slugify(raw_id)}" if slug else _slugify(raw_id)
            cat = str(item.get("category") or default_cat).strip() or default_cat
            kw = _normalize_keywords(item.get("keywords") or item.get("tags"), text_sources=(slug, raw_id, item.get("eyebrow"), item.get("badge"), title, body))
            entries.append(_make_entry(eid, title or raw_id, cat, body or title, kw, _overview_item_url(item, group_key, site_url)))

    if demo_enabled and isinstance(ov.get("domain_previews"), list):
        for pv in ov["domain_previews"]:
            if not isinstance(pv, dict) or not pv.get("title"):
                continue
            vid = str(pv.get("view_id") or pv.get("world_id") or _slugify(str(pv["title"]))).strip()
            eid = f"{slug}-preview-{_slugify(vid)}" if slug else f"preview-{_slugify(vid)}"
            kw = _normalize_keywords(pv.get("keywords"), text_sources=(slug, pv.get("world_id"), pv.get("view_id"), pv.get("badge"), pv["title"], pv.get("subtitle")))
            entries.append(_make_entry(eid, str(pv["title"]).strip(), "Domain Preview", str(pv.get("subtitle") or pv["title"]), kw, _resolve_url(pv.get("href") or "demo/", site_url)))
    return entries


def _collect_demo_entry(slug: str, project_title: str, site_url: str, config: dict[str, Any]) -> dict[str, Any] | None:
    routes = config.get("routes") if isinstance(config.get("routes"), dict) else {}
    demo_route = routes.get("demo") if isinstance(routes.get("demo"), dict) else {}
    if not bool(demo_route.get("enabled")):
        return None
    proj = config.get("project") if isinstance(config.get("project"), dict) else {}
    ov = config.get("overview") if isinstance(config.get("overview"), dict) else {}
    sp = config.get("social_preview") if isinstance(config.get("social_preview"), dict) else {}
    label = str(demo_route.get("label") or "Demo").strip() or "Demo"
    demo_url = _route_dir_url(demo_route.get("href"), "demo/", site_url)
    summary = str(sp.get("subtitle") or ov.get("summary") or proj.get("tagline") or f"Interactive {project_title} {label}")
    kw = _normalize_keywords(["demo", "interactive", label.lower()], text_sources=(slug, project_title, sp.get("pills"), demo_route.get("legacy_query_keys")))
    return _make_entry(f"{slug}-demo" if slug else "demo", f"{project_title} {label}", "Demo", summary, kw, demo_url)


def _collect_docs_entries(
    slug: str, project_title: str, site_url: str, config: dict[str, Any], docs_payload: dict[str, Any] | None
) -> list[dict[str, Any]]:
    routes = config.get("routes") if isinstance(config.get("routes"), dict) else {}
    docs_route = routes.get("docs") if isinstance(routes.get("docs"), dict) else {}
    if docs_payload is None or (docs_route.get("enabled") is not None and not bool(docs_route.get("enabled"))):
        return []

    proj = config.get("project") if isinstance(config.get("project"), dict) else {}
    dr = config.get("docs_reader") if isinstance(config.get("docs_reader"), dict) else {}
    docs_url = _route_dir_url(docs_route.get("href"), "docs/", site_url)
    docs_title = str(dr.get("title") or f"{project_title} Documentation").strip()
    docs_sub = str(dr.get("subtitle") or proj.get("tagline") or docs_title).strip()
    toc = [d for d in (docs_payload.get("toc") or []) if isinstance(d, dict)]
    chunks = [c for c in (docs_payload.get("search_index") or []) if isinstance(c, dict)]

    landing_kw = _normalize_keywords(["docs", "documentation", "guides"], text_sources=(slug, docs_title, docs_sub, *[d.get("title") for d in toc]))
    entries = [_make_entry(_safe_doc_entry_id(slug, "docs"), docs_title, "Docs", docs_sub, landing_kw, docs_url)]

    chunks_by_doc: dict[str, list[dict[str, Any]]] = {}
    for chunk in chunks:
        chunks_by_doc.setdefault(str(chunk.get("doc_id") or "").strip(), []).append(chunk)

    covered: set[str] = set()
    for doc in toc:
        doc_id = str(doc.get("id") or _slugify(str(doc.get("title") or "guide"))).strip()
        doc_title = str(doc.get("title") or doc_id).strip()
        doc_cat = str(doc.get("category") or "Docs").strip() or "Docs"
        covered.add(anchor := f"doc-{doc_id}")
        excerpt = next((str(c.get("excerpt") or "").strip() for c in chunks_by_doc.get(doc_id, []) if c.get("excerpt")), "")
        headings = [str(h.get("text") or "") for h in (doc.get("headings") or []) if isinstance(h, dict)]
        summary = excerpt or (" · ".join(headings[:3]) if headings else doc_title)
        kw = _normalize_keywords([doc_id, doc_cat.lower()], text_sources=(slug, doc_title, *headings[:8], excerpt))
        entries.append(_make_entry(_safe_doc_entry_id(slug, doc_id), doc_title, doc_cat, summary, kw, f"{docs_url}#{anchor}"))

    for chunk in chunks:
        cid = str(chunk.get("id") or "").strip()
        if not cid or cid in covered:
            continue
        covered.add(cid)
        doc_title = str(chunk.get("title") or "").strip()
        heading = str(chunk.get("heading") or doc_title or cid).strip()
        title = f"{doc_title} — {heading}" if (doc_title and heading and heading.lower() != doc_title.lower()) else (heading or doc_title)
        cat = str(chunk.get("category") or "Docs").strip() or "Docs"
        summary = str(chunk.get("excerpt") or chunk.get("text") or title).strip()
        kw = _normalize_keywords([str(chunk.get("doc_id") or ""), cat.lower()], text_sources=(slug, doc_title, heading, summary))
        entries.append(_make_entry(_safe_doc_entry_id(slug, cid), title, cat, summary, kw, f"{docs_url}#{cid}"))
    return entries


def _normalize_extra_entry(raw: dict[str, Any], slug: str, site_url: str, idx: int) -> dict[str, Any]:
    title = str(raw.get("title") or raw.get("label") or raw.get("name") or f"Item {idx}").strip()
    eid = str(raw.get("id") or raw.get("slug") or (f"{slug}-{_slugify(title)}" if slug else _slugify(title))).strip()
    category = str(raw.get("category") or "Reference").strip() or "Reference"
    summary = str(raw.get("summary") or raw.get("description") or raw.get("desc") or raw.get("excerpt") or title).strip()
    raw_kw = raw.get("keywords") if raw.get("keywords") is not None else raw.get("tags")
    keywords = _normalize_keywords(raw_kw) if raw_kw else _normalize_keywords(text_sources=(slug, title, category, summary))
    return _make_entry(eid, title, category, summary, keywords, _resolve_url(raw.get("url") or raw.get("href") or "", site_url))


def build_project_search_index(
    config: dict[str, Any],
    *,
    docs_payload: dict[str, Any] | None = None,
    extra_entries: list[dict[str, Any]] | None = None,
    updated_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic OAW v1.5.0 search-index payload for a project site."""
    proj = config.get("project") if isinstance(config.get("project"), dict) else {}
    routes = config.get("routes") if isinstance(config.get("routes"), dict) else {}
    slug = str(proj.get("slug") or "").strip()
    project_title = str(proj.get("title") or slug or "Project").strip()
    site_url = _normalize_site_url(proj.get("site_url"))
    resolved_updated = str(updated_at or proj.get("updated_at") or DEFAULT_UPDATED_AT).strip() or DEFAULT_UPDATED_AT
    demo_enabled = bool((routes.get("demo") or {}).get("enabled")) if isinstance(routes.get("demo"), dict) else False

    raw_entries = _collect_overview_entries(slug, project_title, site_url, config, demo_enabled)
    if (demo_entry := _collect_demo_entry(slug, project_title, site_url, config)) is not None:
        raw_entries.append(demo_entry)
    raw_entries.extend(_collect_docs_entries(slug, project_title, site_url, config, docs_payload))

    deduped: list[dict[str, Any]] = []
    index_by_id: dict[str, int] = {}
    for entry in raw_entries:
        if entry["id"] not in index_by_id:
            index_by_id[entry["id"]] = len(deduped)
            deduped.append(entry)

    extra_seen: set[str] = set()
    for idx, raw_extra in enumerate(extra_entries or (), start=1):
        if not isinstance(raw_extra, dict):
            continue
        norm = _normalize_extra_entry(raw_extra, slug, site_url, idx)
        if norm["id"] in extra_seen:
            continue
        extra_seen.add(norm["id"])
        if norm["id"] in index_by_id:
            deduped[index_by_id[norm["id"]]] = norm
        else:
            index_by_id[norm["id"]] = len(deduped)
            deduped.append(norm)

    return {
        "version": SEARCH_INDEX_VERSION,
        "updated_at": resolved_updated,
        "pillar": "projects",
        "project": slug,
        "project_title": project_title,
        "site_url": site_url,
        "entries": deduped,
    }


def write_project_search_index(out_dir: Path, payload: dict[str, Any]) -> Path:
    """Write deterministic formatted search-index.json inside out_dir."""
    dest_dir = Path(out_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / "search-index.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path
