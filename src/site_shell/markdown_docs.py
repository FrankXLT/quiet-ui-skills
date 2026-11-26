# SPDX-License-Identifier: Apache-2.0
"""Pure-stdlib Markdown compiler with Quiet Evidence diagram compilation, TOC, and search index."""

from __future__ import annotations

import html
import html.entities
import json
import posixpath
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any

_EVIDENCE_SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "quiet-evidence" / "scripts"
_URN_PREFIX = "urn:quiet-ui:schema:v9:"
_SAFE_KEEP_ENTITIES = frozenset({"lt", "gt", "amp", "quot", "apos"})
_EMOJI_RE = re.compile(r"(?:\u2728|\u26a1|\u2600|\U0001f6e1|\u25cf|&#10024;|\U0001f680|\U0001f4a1|\U0001f525|\u26a0\ufe0f?|\u274c|\u2705)")
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_FENCE_OPEN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^\s`~]*)(.*)$")
_HR_RE = re.compile(r"^\s*(?:([-*_])(?:\s*\1){2,})\s*$")
_LIST_ITEM_RE = re.compile(r"^(\s*)(?:([-*+])|(\d+)\.)\s+(.*)$")
_TABLE_DELIM_RE = re.compile(r"^\s*(?:\|?\s*:?-{1,}:?\s*(?:\|\s*:?-{1,}:?\s*)+\|?|\|\s*:?-{1,}:?\s*\|)\s*$")
_ALERT_RE = re.compile(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(.*)$", re.I)
_ENTITY_RE = re.compile(r"&([A-Za-z][A-Za-z0-9]{1,15});")
_CODE_SPAN_RE = re.compile(r"(`+)([^\n]*?)\1")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(((?:[^()\s\n]+|\([^()\s\n]*\))+)(?:\s+\"[^\"\n]*\")?\)")
_LINK_RE = re.compile(r"\[((?:[^\[\]\n]|\x00T\d+\x00)+)\]\(((?:[^()\s\n]+|\([^()\s\n]*\))+)(?:\s+\"[^\"\n]*\")?\)")
_ANCHOR_HREF_RE = re.compile(r'<a\b([^>]*?\s)href="([^"]*)"', re.I)
_SVG_BAD_ELEM = r"(?:script|foreignObject|iframe|object|embed|animate|animateMotion|animateTransform|set)"
_SVG_BAD_PAIR_RE = re.compile(rf"<\s*({_SVG_BAD_ELEM})\b(?:(?:[^\"'>]|\"[^\"]*\"|'[^']*')*|[^>]*)>.*?<\s*/\s*\1\b[^>]*(?:>|$)", re.I | re.S)
_SVG_BAD_TAG_RE = re.compile(rf"<\s*/?\s*{_SVG_BAD_ELEM}\b[^>]*(?:>|$)", re.I | re.S)
_SVG_TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9:_-]*)((?:[^\"'>]|\"[^\"]*\"|'[^']*')*|[^>]*)>")
_SVG_ATTR_RE = re.compile(r"""([\s/]+|(?<=["']))([a-zA-Z_:][a-zA-Z0-9_.:-]*)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s<>`]+?(?=\s|/?$))|(?!\s*=))""")


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _decode_entities(text: str) -> str:
    def _sub(m: re.Match[str]) -> str:
        name = m.group(1)
        if name.lower() in _SAFE_KEEP_ENTITIES:
            return m.group(0)
        val = html.entities.html5.get(name + ";") or html.entities.html5.get(name)
        return _EMOJI_RE.sub("", val) if val is not None else m.group(0)

    return _ENTITY_RE.sub(_sub, _EMOJI_RE.sub("", text))


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


def _unique_id(base: str, used: set[str]) -> str:
    cand, idx = base, 2
    while cand in used:
        cand, idx = f"{base}-{idx}", idx + 1
    used.add(cand)
    return cand


def _is_safe_url(raw_url: str) -> str | None:
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", html.unescape(raw_url)).strip()
    if cleaned.startswith("<") and cleaned.endswith(">"):
        cleaned = cleaned[1:-1].strip()
    compact = re.sub(r"[\x00-\x20\x7f\s]+", "", cleaned)
    if not compact or compact.startswith(("//", "\\\\", "/\\", "\\/")):
        return None
    if cleaned.startswith("#"):
        return cleaned
    for probe in (cleaned, compact):
        if (scheme := urllib.parse.urlsplit(probe).scheme):
            return cleaned if scheme.lower() in {"http", "https"} else None
    return None if ":" in re.split(r"[/?#]", compact, maxsplit=1)[0] else cleaned


def _sanitize_svg_html(raw_html: str) -> str:
    out = raw_html
    while (nxt := _SVG_BAD_PAIR_RE.sub("", out)) != out:
        out = nxt
    out = _SVG_BAD_TAG_RE.sub("", out)

    def _clean_tag(m: re.Match[str]) -> str:
        tag, attrs = m.group(1), m.group(2)
        kept, has_fill, pos = [], False, 0
        for am in _SVG_ATTR_RE.finditer(attrs):
            sep, name, val = am.group(1), am.group(2), am.group(3)
            if am.start() > pos and attrs[pos:am.start()].strip():
                kept.append(attrs[pos:am.start()])
            pos, lname = am.end(), name.lower()
            if val is not None:
                raw = val[1:-1] if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'" else val
                if re.match(r"^on[a-z0-9_-]+$", lname) or (lname == "preserveaspectratio" and raw.strip().lower() == "none"):
                    continue
                if lname == "href" or lname.endswith(":href"):
                    norm = re.sub(r"[\x00-\x20\x7f\s]+", "", html.unescape(raw)).lower()
                    if norm.startswith(("javascript:", "vbscript:")) or (norm.startswith("data:") and not re.match(r"^data:image/(?:png|jpeg|jpg|gif|webp)[;,]", norm)):
                        continue
            has_fill = has_fill or lname == "fill"
            kept.append(f"{' ' if (not sep or '/' in sep) else sep}{name}" + (f"={val}" if val is not None else ""))
        prefix = ' fill="none"' if tag.lower() == "path" and not has_fill else ""
        return f"<{tag}{prefix}{''.join(kept)}{attrs[pos:]}>"

    return _EMOJI_RE.sub("", _SVG_TAG_RE.sub(_clean_tag, out))


def compile_diagram_spec(spec: dict[str, Any], rigor: str | None = None) -> str:
    """Compile an offline urn:quiet-ui:schema:v9:* spec dict into deterministic HTML/SVG."""
    if not isinstance(spec, dict):
        raise ValueError(f"Expected diagram spec dict, got {type(spec).__name__}")
    if str(_EVIDENCE_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_EVIDENCE_SCRIPTS))
    from compile_evidence import compile_spec

    meta = spec.get("metadata") if isinstance(spec.get("metadata"), dict) else {}
    eff_rigor = str(rigor or meta.get("rigor_level") or spec.get("rigor") or "L2").upper()
    return _sanitize_svg_html(compile_spec(spec, rigor=eff_rigor, medium="m2", theme="white", standalone=False))


def _apply_emph(segment: str, tokens: list[str], *, plain: bool) -> str:
    s = _decode_entities(segment) if plain else _esc(_decode_entities(segment))
    s = re.sub(r"\*\*\*([^\s*](?:[^\n*]*?[^\s*])?)\*\*\*", r"\1" if plain else r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*([^\s*](?:(?!\*\*).)*?[^\s*]|[^\s*])\*\*", r"\1" if plain else r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^\s*](?:[^\n*]*?[^\s*])?)\*(?!\*)", r"\1" if plain else r"<em>\1</em>", s)
    s = s.replace("\x00BR\x00", " " if plain else "<br />")
    return re.sub(r"\x00T(\d+)\x00", lambda m: tokens[int(m.group(1))], s)


def _render_inline(text: str, *, plain: bool = False) -> str:
    tokens: list[str] = []
    work = text.replace("\x00", "")
    work = work.replace("\n", " ") if plain else re.sub(r" {2,}\n", "\x00BR\x00", work).replace("\n", " ")

    def _keep(val: str) -> str:
        tokens.append(val)
        return f"\x00T{len(tokens) - 1}\x00"

    def _sub_code(m: re.Match[str]) -> str:
        b = m.group(2)[1:-1] if len(m.group(1)) > 1 and len(m.group(2)) >= 2 and m.group(2).startswith(" ") and m.group(2).endswith(" ") else m.group(2)
        clean = _EMOJI_RE.sub("", b)
        return _keep(clean if plain else f"<code>{_esc(clean)}</code>")

    def _sub_img(m: re.Match[str]) -> str:
        alt = _EMOJI_RE.sub("", m.group(1))
        safe = None if plain else _is_safe_url(m.group(2))
        return _keep(alt if plain else (f'<img src="{_esc(safe)}" alt="{_esc(alt)}" />' if safe else _esc(alt)))

    def _sub_link(m: re.Match[str]) -> str:
        lbl = _apply_emph(m.group(1), tokens, plain=plain)
        safe = None if plain else _is_safe_url(m.group(2))
        return _keep(lbl if plain else (f'<a href="{_esc(safe)}">{lbl}</a>' if safe else lbl))

    work = _LINK_RE.sub(_sub_link, _IMAGE_RE.sub(_sub_img, _CODE_SPAN_RE.sub(_sub_code, work)))
    out = _apply_emph(work, tokens, plain=plain)
    return " ".join(out.split()) if plain else out


def _strip_frontmatter(lines: list[str]) -> tuple[list[str], dict[str, str]]:
    if not lines or lines[0].strip() != "---":
        return lines, {}
    meta: dict[str, str] = {}
    for idx in range(1, min(len(lines), 40)):
        s = lines[idx].strip()
        if s in {"---", "..."}:
            return lines[idx + 1 :], meta
        if ":" in s and not s.startswith(("-", "#")):
            k, v = s.split(":", 1)
            meta[k.strip().lower()] = v.strip().strip("\"'")
    return lines, {}


def _split_pipe_row(line: str) -> list[str]:
    spans: list[str] = []
    masked = _CODE_SPAN_RE.sub(lambda m: (spans.append(m.group(0)), f"\x00C{len(spans) - 1}\x00")[1], line.strip())
    s = masked[1:] if masked.startswith("|") else masked
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [
        re.sub(r"\x00C(\d+)\x00", lambda m: spans[int(m.group(1))], cell).replace("\\|", "|").strip()
        for cell in re.split(r"(?<!\\)\|", s)
    ]


def _parse_table(lines: list[str], start: int) -> tuple[str, str, int]:
    headers = _split_pipe_row(lines[start])
    aligns = ["center" if c.startswith(":") and c.endswith(":") else ("right" if c.endswith(":") else "") for c in (dc.strip() for dc in _split_pipe_row(lines[start + 1]))]
    ncols = max(len(headers), 1)
    aligns.extend([""] * max(0, ncols - len(aligns)))

    def _cell(tag: str, val: str, align: str) -> str:
        return f'<{tag}{f" data-align={chr(34)}{align}{chr(34)}" if align else ""}>{_render_inline(val)}</{tag}>'

    th_html = "".join(_cell("th", headers[c], aligns[c]) for c in range(ncols))
    plain_parts = [_render_inline(h, plain=True) for h in headers if h]
    rows_html, idx = [], start + 2
    while idx < len(lines) and (ln := lines[idx]).strip() and "|" in ln and not _HEADING_RE.match(ln) and not _FENCE_OPEN_RE.match(ln):
        row = _split_pipe_row(ln)
        padded = [row[c] if c < len(row) else "" for c in range(ncols)]
        rows_html.append("<tr>" + "".join(_cell("td", padded[c], aligns[c]) for c in range(ncols)) + "</tr>")
        plain_parts.extend(_render_inline(v, plain=True) for v in padded if v)
        idx += 1
    html_out = f'<div class="va-table-wrap"><table class="booktabs"><thead><tr>{th_html}</tr></thead><tbody>{"".join(rows_html)}</tbody></table></div>'
    return html_out, " ".join(p for p in plain_parts if p), idx


def _render_code_fence(lang: str, body: str) -> tuple[str, str]:
    lang_clean, lang_low = lang.strip(), lang.strip().lower()
    if lang_low in {"quiet-evidence", "json-diagram", "json"}:
        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            schema_id = str(parsed.get("$schema") or parsed.get("schema") or "")
            explicit = bool(parsed.get("diagram")) or str(parsed.get("render", "")).strip().lower() == "compile"
            if schema_id.startswith(_URN_PREFIX) and (lang_low in {"quiet-evidence", "json-diagram"} or explicit):
                try:
                    compiled = compile_diagram_spec(parsed)
                    meta = parsed.get("metadata") if isinstance(parsed.get("metadata"), dict) else {}
                    plain = " ".join(str(x) for x in (meta.get("title", ""), meta.get("description", "")) if x)
                    return f'<div class="oaw-compiled-diagram">{compiled}</div>', plain
                except (ValueError, KeyError, TypeError):
                    pass
    clean_body = _EMOJI_RE.sub("", body)
    code_html = (f'<div class="oaw-code-block"><div class="oaw-code-hdr"><span class="oaw-code-lang">{_esc(lang_clean or "text")}</span>'
                 f'<button type="button" class="oaw-copy-code-btn" aria-label="Copy code">Copy</button></div><pre><code>{_esc(clean_body)}</code></pre></div>')
    return code_html, " ".join(clean_body.split())


def _is_table_start(lines: list[str], idx: int) -> bool:
    return idx + 1 < len(lines) and "|" in lines[idx] and bool(_TABLE_DELIM_RE.match(lines[idx + 1]))


def _is_block_start(lines: list[str], idx: int) -> bool:
    ln = lines[idx]
    return not ln.strip() or bool(_HEADING_RE.match(ln) or _FENCE_OPEN_RE.match(ln) or _HR_RE.match(ln) or ln.lstrip().startswith(">") or _LIST_ITEM_RE.match(ln) or _is_table_start(lines, idx))


def _next_nonblank(lines: list[str], idx: int) -> int:
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    return idx


def _parse_list(lines: list[str], start: int, base_indent: int | None = None) -> tuple[str, str, int]:
    first = _LIST_ITEM_RE.match(lines[start])
    assert first is not None
    indent0, is_ol = len(first.group(1)) if base_indent is None else base_indent, first.group(3) is not None
    tag = "ol" if is_ol else "ul"
    items_html, plain_parts, idx = [], [], start
    while idx < len(lines):
        nxt = idx if lines[idx].strip() else _next_nonblank(lines, idx + 1)
        m = _LIST_ITEM_RE.match(lines[nxt]) if nxt < len(lines) else None
        if not m or len(m.group(1)) != indent0 or bool(m.group(3)) != is_ol:
            break
        text_lines, nested_html, idx = [m.group(4)], [], nxt + 1
        while idx < len(lines):
            peek = idx if lines[idx].strip() else _next_nonblank(lines, idx + 1)
            if peek >= len(lines):
                break
            ln = lines[peek]
            if (nm := _LIST_ITEM_RE.match(ln)):
                if len(nm.group(1)) > indent0:
                    sub_h, sub_p, idx = _parse_list(lines, peek, len(nm.group(1)))
                    nested_html.append(sub_h)
                    plain_parts.append(sub_p)
                    continue
                break
            if peek > idx or (_is_block_start(lines, idx) and len(ln) - len(ln.lstrip()) <= indent0):
                break
            text_lines.append(ln.strip())
            idx += 1
        joined = "\n".join(text_lines)
        plain_parts.append(_render_inline(joined, plain=True))
        items_html.append(f"<li>{_render_inline(joined)}{''.join(nested_html)}</li>")
    return f"<{tag}>{''.join(items_html)}</{tag}>", " ".join(p for p in plain_parts if p), idx


def _parse_blockquote(lines: list[str], start: int) -> tuple[str, str, int]:
    inner, idx = [], start
    while idx < len(lines) and lines[idx].lstrip().startswith(">"):
        inner.append(re.sub(r"^>\s?", "", lines[idx].lstrip(), count=1))
        idx += 1
    alert_kind: str | None = None
    if inner and (am := _ALERT_RE.match(inner[0].strip())):
        alert_kind = am.group(1).lower()
        rem = am.group(2).strip()
        inner = ([rem] if rem else []) + inner[1:]
    body_html, body_plain = _parse_block_seq(inner)
    if alert_kind:
        out = f'<aside class="oaw-callout" data-callout="{alert_kind}"><div class="oaw-callout-title">{alert_kind.title()}</div>{body_html}</aside>'
        return out, " ".join(p for p in (alert_kind.title(), body_plain) if p), idx
    return f"<blockquote>{body_html}</blockquote>", body_plain, idx


def _consume_fence(lines: list[str], start: int) -> tuple[str, str, int]:
    fm = _FENCE_OPEN_RE.match(lines[start])
    assert fm is not None
    indent, fence, lang = len(fm.group(1)), fm.group(2), fm.group(3)
    close_re = re.compile(rf"^\s*{re.escape(fence[0])}{{{len(fence)},}}\s*$")
    buf, idx = [], start + 1
    while idx < len(lines) and not close_re.match(lines[idx]):
        ln = lines[idx]
        buf.append(ln[indent:] if indent and len(ln) - len(ln.lstrip()) >= indent else ln)
        idx += 1
    return (*_render_code_fence(lang, "\n".join(buf)), min(idx + 1, len(lines)))


def _parse_block_seq(
    lines: list[str], *, doc_id: str = "", doc_title: str = "", category: str = "",
    used_ids: set[str] | None = None, headings_out: list[dict[str, Any]] | None = None,
    search_out: list[dict[str, Any]] | None = None,
) -> tuple[str, str]:
    blocks_html, all_plain, cur_chunks = [], [], []
    cur_sid, cur_heading, emitted = f"doc-{doc_id}", doc_title, 0

    def _flush_search() -> None:
        nonlocal emitted
        if search_out is None or not cur_chunks:
            return
        body_txt = " ".join(c for c in cur_chunks if c).strip()
        cur_chunks.clear()
        if not body_txt:
            return
        excerpt = body_txt if len(body_txt) <= 180 else body_txt[:177].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
        search_out.append({"id": cur_sid, "doc_id": doc_id, "title": doc_title, "category": category,
                           "heading": cur_heading, "excerpt": excerpt, "text": " ".join(p for p in (cur_heading, body_txt) if p)})
        emitted += 1

    idx, n = 0, len(lines)
    while idx < n:
        ln = lines[idx]
        if not ln.strip():
            idx += 1
            continue
        if _FENCE_OPEN_RE.match(ln):
            blk_h, blk_p, idx = _consume_fence(lines, idx)
        elif (hm := _HEADING_RE.match(ln)):
            level, raw_h = len(hm.group(1)), hm.group(2).strip()
            plain_h = _render_inline(raw_h, plain=True)
            hid = _unique_id(f"{doc_id}-{_slugify(plain_h)}", used_ids) if (used_ids is not None and level <= 4) else f"{doc_id}-{_slugify(plain_h)}"
            if headings_out is not None and level <= 4:
                headings_out.append({"id": hid, "text": plain_h, "level": level})
            if search_out is not None:
                had = bool(cur_chunks)
                _flush_search()
                cur_sid = cur_sid if (not had and cur_sid == f"doc-{doc_id}" and level == 1) else hid
                cur_heading = plain_h
            blk_h, blk_p, idx = f'<h{level} id="{_esc(hid)}">{_render_inline(raw_h)}</h{level}>', "", idx + 1
        elif _HR_RE.match(ln):
            blk_h, blk_p, idx = "<hr />", "", idx + 1
        elif ln.lstrip().startswith(">"):
            blk_h, blk_p, idx = _parse_blockquote(lines, idx)
        elif _is_table_start(lines, idx):
            blk_h, blk_p, idx = _parse_table(lines, idx)
        elif _LIST_ITEM_RE.match(ln):
            blk_h, blk_p, idx = _parse_list(lines, idx)
        else:
            plines, idx = [ln.strip()], idx + 1
            while idx < n and not _is_block_start(lines, idx):
                plines.append(lines[idx].strip())
                idx += 1
            joined = "\n".join(plines)
            blk_h, blk_p = f"<p>{_render_inline(joined)}</p>", _render_inline(joined, plain=True)
        blocks_html.append(blk_h)
        if blk_p:
            all_plain.append(blk_p)
            cur_chunks.append(blk_p)

    _flush_search()
    if search_out is not None and emitted == 0:
        search_out.append({"id": f"doc-{doc_id}", "doc_id": doc_id, "title": doc_title, "category": category,
                           "heading": cur_heading or doc_title, "excerpt": doc_title, "text": cur_heading or doc_title})
    return "\n".join(blocks_html), " ".join(all_plain)


def _resolve_doc_path(path: Path) -> Path | None:
    try:
        return path.resolve()
    except OSError:
        return None


def _read_source_markdown(src: dict[str, Any], base_dir: Path) -> tuple[str, str, Path | None, str | None]:
    if (raw_path := src.get("path") or src.get("file")) is not None:
        raw_str = str(raw_path)
        if not raw_str.strip() or "\x00" in raw_str or raw_str.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", raw_str) or (p := Path(raw_str)).is_absolute():
            raise ValueError(f"Markdown source path must be relative to base_dir: {raw_str!r}")
        base_resolved = base_dir.resolve()
        resolved = (base_resolved / p).resolve()
        if not resolved.is_relative_to(base_resolved) or resolved == base_resolved:
            raise ValueError(f"Markdown source path escapes base_dir: {raw_str!r}")
        return resolved.read_text(encoding="utf-8"), (base_resolved / p).stem, resolved, raw_str
    if any(k in src for k in ("markdown", "content", "text")):
        return str(src.get("markdown") or src.get("content") or src.get("text") or ""), "doc", None, None
    raise ValueError(f"Markdown source missing 'path' or inline content: {src!r}")


def _rewrite_doc_links(article_html: str, cur_path: Path | None, cur_raw: str | None,
                       lookup: dict[Any, dict[str, Any] | None], base_resolved: Path) -> str:
    def _sub_href(m: re.Match[str]) -> str:
        parsed = urllib.parse.urlsplit(raw_href := html.unescape(m.group(2)))
        rel = urllib.parse.unquote(parsed.path).replace("\\", "/")
        if not raw_href or raw_href.startswith("#") or parsed.scheme or parsed.netloc or not rel or rel.startswith("/"):
            return m.group(0)
        norm_rel = posixpath.normpath(rel)
        cands: list[Any] = [*([cur_path.parent / rel, posixpath.normpath(posixpath.join(posixpath.dirname((cur_raw or "").replace("\\", "/")), rel))] if cur_path else []), base_resolved / rel, norm_rel, *((("name", norm_rel),) if "/" not in norm_rel else ())]
        if (target := next((v for c in cands if (k := (_resolve_doc_path(c) if isinstance(c, Path) else c)) in lookup and (v := lookup[k]) is not None), None)) is None:
            return m.group(0)
        doc_id, frag = str(target["id"]), urllib.parse.unquote(parsed.fragment).strip()
        hids = [str(h["id"]) for h in target["headings"] if h.get("id")]
        slug = re.sub(r"[^a-z0-9]+", "-", frag.lower()).strip("-") if frag else ""
        anchor = next((c for c in ([frag, slug, f"{doc_id}-{slug}"] if slug else [frag]) if c and c in hids), "") or (next((h for h in hids if h.endswith(f"-{slug}")), "") if slug else "")
        tid = _esc(anchor or f"doc-{doc_id}")
        return f'<a{m.group(1)}href="#{tid}" data-doc-jump="{tid}"'

    return _ANCHOR_HREF_RE.sub(_sub_href, article_html)


def compile_markdown_docs(sources: list[dict[str, Any]], base_dir: Path) -> dict[str, Any]:
    """Compile Markdown doc sources into HTML sections, hierarchical TOC, and client search index."""
    base_resolved = _resolve_doc_path(base := Path(base_dir)) or base
    compiled, toc, search_index, used_ids = [], [], [], set()
    lookup: dict[Any, dict[str, Any] | None] = {}
    for src in sources:
        md_raw, stem, abs_path, raw_str = _read_source_markdown(src, base)
        lines, fm = _strip_frontmatter(md_raw.lstrip("\ufeff").splitlines())
        raw_id = str(src.get("id") or _slugify(str(src.get("title") or fm.get("name") or stem)))
        doc_id = _unique_id(f"doc-{re.sub(r'[^a-zA-Z0-9_-]+', '-', raw_id.strip()).strip('-') or 'doc'}", used_ids)[4:]
        inferred_h1 = next((_render_inline(m.group(2), plain=True) for ln in lines if (m := _HEADING_RE.match(ln)) and len(m.group(1)) == 1), "")
        title = str(src.get("title") or fm.get("title") or inferred_h1 or fm.get("name") or doc_id)
        category, headings = str(src.get("category") or ""), []
        inner_html, _ = _parse_block_seq(lines, doc_id=doc_id, doc_title=title, category=category, used_ids=used_ids, headings_out=headings, search_out=search_index)
        toc.append(doc_meta := {"id": doc_id, "title": title, "category": category, "headings": headings})
        compiled.append((inner_html, doc_meta, abs_path, raw_str))
        if raw_str is not None:
            lookup.setdefault(posixpath.normpath(raw_str.replace("\\", "/")), doc_meta)
        if abs_path is not None:
            for k in (abs_path, *((abs_path.relative_to(base_resolved).as_posix(),) if abs_path.is_relative_to(base_resolved) else ())):
                lookup.setdefault(k, doc_meta)
            nkey = ("name", abs_path.name)
            lookup[nkey] = doc_meta if nkey not in lookup else (lookup[nkey] if lookup[nkey] and lookup[nkey]["id"] == doc_id else None)
    return {"sections_html": "\n".join(f'<article class="oaw-doc-section" id="doc-{_esc(dm["id"])}">\n{_rewrite_doc_links(h, ap, rs, lookup, base_resolved)}\n</article>' for h, dm, ap, rs in compiled), "toc": toc, "search_index": search_index}
