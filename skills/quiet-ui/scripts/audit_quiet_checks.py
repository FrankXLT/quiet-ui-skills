# SPDX-License-Identifier: Apache-2.0
"""Static, asset-resolution, data-honesty, and CDP SVG/DOM check helpers for Quiet UI."""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path
from typing import Any

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
VIEWPORTS: tuple[tuple[int, int], ...] = ((390, 844), (900, 1080), (1440, 900))

_IMPORTANT_RE = re.compile(r"!\s*important\b", re.IGNORECASE)
_FONT_PX_RE = re.compile(r"(?<![A-Za-z0-9_-])font-size\s*:\s*([0-9]*\.?[0-9]+)\s*px\b", re.IGNORECASE)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_NARROW_AT_RE = re.compile(r"@media[^{]*?(?:max-width\s*:\s*\d+px|pointer\s*:\s*coarse)[^{]*\{", re.IGNORECASE)
OVERFLOW_RULE_RE = re.compile(r"([^{};]+)\{[^{}]*overflow(?:-x)?\s*:\s*(?:auto|scroll)\b[^{}]*\}", re.IGNORECASE | re.DOTALL)
WRAPPER_CLASS_HINTS = {"va-table-wrap", "qe-table-wrap", "table-wrap", "table-scroll", "overflow-x-auto"}
SELF_BADGE_RE = re.compile(
    r"\b(?:(?:v\d+(?:\.\d+)*|\d+\.\d+(?:\.\d+)*)\s*[·•|-]?\s*Quiet(?:[\s-]+UI)?|Quiet(?:[\s-]+UI)(?:\s+v\d|\s+Pillar|\s+Skills)?|Quiet-Evidence\s+L[1-3]|Pillar\s+[123]\s+M[1-7])\b",
    re.IGNORECASE,
)
BRAIN_TEXT_RE = re.compile(r"(?:\bbrain:[0-9a-z_-]{6,}\b|\.gemini/antigravity/brain/)", re.IGNORECASE)
_BRAIN_JS_RE = re.compile(
    r"(?:`[^`]*brain:\$\{[^`]+`|['\"]brain:['\"]\s*\+|\bbrain:[0-9a-z_-]{6,}\b|\.gemini/antigravity/brain/)",
    re.IGNORECASE,
)
_NAMED_MOCK_ARR_RE = re.compile(
    r"(?:const|let|var)?\s*\b(?:(?:MOCK|FAKE|DUMMY|STUB)_[A-Z0-9_]+|(?:mock|fake|dummy|demo|stub)(?:Rows|Runs|Series|Data|Items|Metrics|Logs|Events|Cards))\s*=\s*\[\s*\{",
    re.IGNORECASE,
)
_DEMO_GUARD_RE = re.compile(
    r"\b(?:isDemo|demoMode|useDemo)\b|\bdemo\s*[!=]==?|(?:get|has)\(\s*['\"]demo['\"]",
    re.IGNORECASE,
)
_DEMO_TERNARY_RE = re.compile(
    r"\b(?:isDemo|demoMode|useDemo)\b\s*\?\s*\[\s*\{[\s\S]{1,400}?\}\s*,\s*\{",
    re.IGNORECASE,
)
_MULTI_OBJ_ARR_RE = re.compile(r"(?:=|\breturn)\s*\[\s*\{[\s\S]{1,400}?\}\s*,\s*\{", re.IGNORECASE)

CDP_AUDIT_JS = r"""
const opts = arguments[0] || {};
const allowShowcase = !!opts.allowShowcase;
const errs = [], seen = new Set(), vw = window.innerWidth;
function pushErr(msg) { if (!seen.has(msg)) { seen.add(msg); errs.push(msg); } }
const SELF_BADGE_RE = /\b(?:(?:v\d+(?:\.\d+)*|\d+\.\d+(?:\.\d+)*)\s*[·•|-]?\s*Quiet(?:[\s-]+UI)?|Quiet(?:[\s-]+UI)(?:\s+v\d|\s+Pillar|\s+Skills)?|Quiet-Evidence\s+L[1-3]|Pillar\s+[123]\s+M[1-7])\b/i;
const BRAIN_RE = /(?:\bbrain:[0-9a-z_-]{6,}\b|\.gemini\/antigravity\/brain\/)/i;
const MATH_INTERVAL_RE = /(?:\[[^\]\[]+,\s*[^()\[]+\)|\([^()\[]+,\s*[^\]\[]+\])/g;

function isVis(el, cs) {
  if (!el || !cs || cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') === 0) return false;
  const r = el.getBoundingClientRect();
  return r.width > 1 && r.height > 1;
}

function unclosedDelim(txt) {
  const cleaned = String(txt || '').replace(MATH_INTERVAL_RE, '');
  let p = 0, b = 0;
  for (const ch of cleaned) {
    if (ch === '(') p += 1;
    else if (ch === ')' && p > 0) p -= 1;
    else if (ch === '[') b += 1;
    else if (ch === ']' && b > 0) b -= 1;
  }
  return p > 0 || b > 0;
}

function getRotDeg(el, cs) {
  const tf = (cs && cs.transform && cs.transform !== 'none') ? cs.transform : (el.getAttribute('transform') || '');
  if (!tf) return 0;
  const mRot = tf.match(/rotate\(\s*([-0-9.]+)/i);
  if (mRot) return Math.abs(parseFloat(mRot[1]) || 0);
  const mMat = tf.match(/matrix\(\s*([-0-9.eE]+)\s*,\s*([-0-9.eE]+)/i);
  if (mMat) {
    const a = parseFloat(mMat[1]), b = parseFloat(mMat[2]);
    return (Number.isFinite(a) && Number.isFinite(b)) ? Math.abs(Math.atan2(b, a) * 180 / Math.PI) : 0;
  }
  return 0;
}

function isTransparentPaint(c) {
  return !c || c === 'none' || c === 'transparent' || /^rgba\([^)]*,\s*0(?:\.0+)?\s*\)$/.test(c);
}

function hasTextHalo(doc, txtEl, win) {
  if (txtEl.classList && txtEl.classList.contains('va-svg-halo-text')) return true;
  const cs = win.getComputedStyle(txtEl);
  const po = String(txtEl.getAttribute('paint-order') || cs.paintOrder || '').toLowerCase();
  const st = String(txtEl.getAttribute('stroke') || cs.stroke || 'none').toLowerCase();
  const sw = parseFloat(txtEl.getAttribute('stroke-width') || cs.strokeWidth || '0');
  if (po.includes('stroke') && !isTransparentPaint(st) && sw >= 2) return true;
  const prev = txtEl.previousElementSibling;
  if (prev && (prev.tagName || '').toLowerCase() === 'rect') {
    const pf = String(prev.getAttribute('fill') || win.getComputedStyle(prev).fill || 'none').toLowerCase();
    if (!isTransparentPaint(pf)) {
      const pr = prev.getBoundingClientRect(), tr = txtEl.getBoundingClientRect();
      if (pr.left <= tr.left + 2 && pr.right >= tr.right - 2 && pr.top <= tr.top + 2 && pr.bottom >= tr.bottom - 2) return true;
    }
  }
  return false;
}

function auditSvg(svg, doc, win, ctxTag) {
  if (svg.getAttribute('aria-hidden') === 'true') return;
  const sr = svg.getBoundingClientRect();
  if (sr.width < 30 || sr.height < 20) return;

  const allNodes = [...svg.querySelectorAll('*')];
  const nodeOrder = new Map();
  allNodes.forEach((el, idx) => nodeOrder.set(el, idx));

  const texts = [];
  for (const t of svg.querySelectorAll('text')) {
    const cs = win.getComputedStyle(t);
    if (!isVis(t, cs)) continue;
    const raw = (t.textContent || '').trim();
    if (!raw) continue;
    const r = t.getBoundingClientRect();
    texts.push({ el: t, txt: raw, r, rot: getRotDeg(t, cs), idx: nodeOrder.get(t) || 0, halo: hasTextHalo(doc, t, win) });
    if (raw.length >= 6 && unclosedDelim(raw)) {
      pushErr(`[LABEL_TRUNCATED${ctxTag}] @${vw}px: SVG text truncated with unclosed delimiter '${raw.slice(0, 36)}'`);
    }
  }

  for (let i = 0; i < texts.length; i += 1) {
    for (let j = i + 1; j < texts.length; j += 1) {
      const a = texts[i], b = texts[j];
      const ovW = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const ovH = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (ovW <= 2.5 || ovH <= 4.5) continue;
      if (a.rot > 8 || b.rot > 8) {
        const dx = (a.r.left + a.r.width / 2) - (b.r.left + b.r.width / 2);
        const dy = (a.r.top + a.r.height / 2) - (b.r.top + b.r.height / 2);
        if (Math.hypot(dx, dy) > Math.min(a.r.width, b.r.width) * 0.65) continue;
      }
      pushErr(`[SVG_TEXT_OVERLAP${ctxTag}] @${vw}px: '${a.txt.slice(0, 24)}' overlaps '${b.txt.slice(0, 24)}' (${ovW.toFixed(1)}x${ovH.toFixed(1)}px)`);
    }
  }

  const plates = [];
  for (const sh of svg.querySelectorAll('rect, path, polygon')) {
    const cs = win.getComputedStyle(sh);
    if (!isVis(sh, cs)) continue;
    const fill = String(sh.getAttribute('fill') || cs.fill || 'none').toLowerCase();
    const fo = parseFloat(sh.getAttribute('fill-opacity') || cs.fillOpacity || '1');
    if (fill === 'none' || fill === 'transparent' || fill === 'rgba(0, 0, 0, 0)' || fo < 0.7) continue;
    plates.push({ r: sh.getBoundingClientRect(), idx: nodeOrder.get(sh) || 0 });
  }

  for (const ln of svg.querySelectorAll('line, path')) {
    const tag = (ln.tagName || '').toLowerCase();
    const cs = win.getComputedStyle(ln);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') < 0.05) continue;
    const stroke = String(ln.getAttribute('stroke') || cs.stroke || 'none').toLowerCase();
    if (!stroke || stroke === 'none' || stroke === 'transparent' || stroke === 'rgba(0, 0, 0, 0)') continue;
    const lr = ln.getBoundingClientRect();
    const isH = lr.width >= 10 && lr.height <= 4;
    const isV = lr.height >= 10 && lr.width <= 4;
    if (tag === 'path' && !isH && !isV) continue;
    if (!isH && !isV) continue;
    const lIdx = nodeOrder.get(ln) || 0;
    const lCy = lr.top + lr.height * 0.5, lCx = lr.left + lr.width * 0.5;
    for (const t of texts) {
      if (t.halo && lIdx < t.idx) continue;
      const tr = t.r;
      const cutH = isH && lr.left < tr.right - 2 && lr.right > tr.left + 2 && lCy > tr.top + 2 && lCy < tr.bottom - 2;
      const cutV = isV && lr.top < tr.bottom - 2 && lr.bottom > tr.top + 2 && lCx > tr.left + 2 && lCx < tr.right - 2;
      if (!cutH && !cutV) continue;
      if (lIdx < t.idx) {
        const covered = plates.some((p) => p.idx > lIdx && p.idx < t.idx && p.r.left <= tr.left + 2 && p.r.right >= tr.right - 2 && p.r.top <= tr.top + 2 && p.r.bottom >= tr.bottom - 2);
        if (covered) continue;
      }
      pushErr(`[SVG_LINE_COLLISION${ctxTag}] @${vw}px: SVG ${isH ? 'horizontal' : 'vertical'} line cuts through '${t.txt.slice(0, 28)}' without halo`);
    }
  }
}

function auditDoc(doc, maxW, ctxTag) {
  if (!doc || !doc.documentElement) return;
  const win = doc.defaultView || window;
  if (doc.documentElement.scrollWidth > maxW + 2) {
    pushErr(`[OVERFLOW${ctxTag}] @${vw}px: scrollWidth=${doc.documentElement.scrollWidth} > width=${maxW}`);
  }
  for (const tbl of doc.querySelectorAll('table')) {
    const tr = tbl.getBoundingClientRect();
    if (tr.width <= 0 || tr.height <= 0) continue;
    if (tr.right > maxW + 2) {
      let scroller = null, p = tbl.parentElement;
      while (p) {
        const ox = win.getComputedStyle(p).overflowX;
        if ((ox === 'auto' || ox === 'scroll') && p.getBoundingClientRect().right <= maxW + 2) { scroller = p; break; }
        p = p.parentElement;
      }
      if (!scroller) pushErr(`[TABLE_CLIP${ctxTag}] @${vw}px: table right=${tr.right.toFixed(1)}px > ${maxW}px without scroll container`);
    }
  }
  for (const el of doc.querySelectorAll('.va-pill, .v9-pill, .va-nav-link, nav a, [class*="nav"] a, [class*="pill"], [class*="badge"], button, .va-tb-btn, .va-tb-group')) {
    const cs = win.getComputedStyle(el);
    if (!isVis(el, cs) || el.closest('pre, code')) continue;
    const raw = (el.textContent || '').trim();
    if (!raw) continue;
    if (el.clientWidth > 12 && (cs.textOverflow === 'ellipsis' || cs.overflowX === 'hidden') && el.scrollWidth > el.clientWidth + 2) {
      pushErr(`[LABEL_TRUNCATED${ctxTag}] @${vw}px: clipped control '${raw.slice(0, 32)}' (scroll=${el.scrollWidth} > client=${el.clientWidth})`);
    } else if (!el.classList.contains('va-tb-group') && raw.length >= 6 && unclosedDelim(raw)) {
      pushErr(`[LABEL_TRUNCATED${ctxTag}] @${vw}px: control has unclosed delimiter '${raw.slice(0, 32)}'`);
    }
  }
  if (!allowShowcase) {
    for (const hdr of doc.querySelectorAll('header, nav, .va-topbar, .v9-topbar, .va-brand, .v9-brand, [class*="kicker"], [class*="badge"], [class*="pill"]')) {
      const cs = win.getComputedStyle(hdr);
      if (!isVis(hdr, cs)) continue;
      const t = (hdr.textContent || '').trim();
      const m = t.match(SELF_BADGE_RE);
      if (m) pushErr(`[SELF_BADGE${ctxTag}] @${vw}px: application chrome contains framework self-badge '${m[0]}'`);
    }
  }
  for (const svg of doc.querySelectorAll('svg')) auditSvg(svg, doc, win, ctxTag);
  const walker = doc.createTreeWalker(doc.body || doc.documentElement, NodeFilter.SHOW_TEXT);
  let n, fontChecked = false;
  while ((n = walker.nextNode())) {
    const raw = n.nodeValue ? n.nodeValue.trim() : '';
    if (!raw) continue;
    const el = n.parentElement;
    if (!el || el.closest('script,style,noscript,svg,sub,sup')) continue;
    const cs = win.getComputedStyle(el), r = el.getBoundingClientRect();
    if (cs.display === 'none' || cs.visibility === 'hidden' || r.width <= 2 || r.height <= 2) continue;
    const bm = raw.match(BRAIN_RE);
    if (bm && !el.closest('pre, code')) pushErr(`[INTERNAL_ID${ctxTag}] @${vw}px: raw internal identifier '${bm[0]}' visible in DOM`);
    if (!fontChecked) {
      const fs = parseFloat(cs.fontSize || '16');
      if (fs < 10.8) { pushErr(`[FONT_FLOOR_CDP${ctxTag}] @${vw}px: '${raw.slice(0, 24)}' computed fontSize=${fs.toFixed(1)}px < 11px`); fontChecked = true; }
    }
  }
  for (const fr of doc.querySelectorAll('iframe')) {
    try {
      const fdoc = fr.contentDocument;
      if (fdoc && fdoc.documentElement) {
        const fw = Math.round(fr.clientWidth || maxW);
        auditDoc(fdoc, fw > 0 ? fw : maxW, ctxTag + ' iframe#' + (fr.id || 'frame'));
      }
    } catch (_err) {}
  }
}
auditDoc(document, vw, '');
return errs;
"""


def parse_mount_prefixes(raw_items: list[str] | None) -> dict[str, Path]:
    """Parse repeatable PREFIX=DIR CLI flags into normalized mount prefix mappings."""
    out: dict[str, Path] = {}
    for item in raw_items or ():
        if "=" not in item:
            continue
        pfx, raw_dir = item.split("=", 1)
        norm = "/" + pfx.strip().strip("/") if pfx.strip() != "/" else "/"
        out[norm] = Path(raw_dir).expanduser().resolve()
    return out


def resolve_asset_path(
    ref: str,
    base_dir: Path | None = None,
    web_root: Path | None = None,
    mount_prefixes: dict[str, Path] | None = None,
) -> Path | None:
    """Resolve an HTML stylesheet or script src reference cleanly inside mounted roots."""
    if not ref or ref.startswith(("http://", "https://", "//", "data:", "blob:")):
        return None
    raw = urllib.parse.unquote(ref.split("?", 1)[0].split("#", 1)[0]).strip()
    if not raw:
        return None
    if raw.startswith("/"):
        for pfx, mdir in sorted((mount_prefixes or {}).items(), key=lambda kv: len(kv[0]), reverse=True):
            if raw == pfx or raw.startswith(pfx.rstrip("/") + "/"):
                mdir_res = mdir.resolve()
                tail = raw[len(pfx):].lstrip("/")
                cand = (mdir_res / tail).resolve() if tail else mdir_res
                if not cand.is_relative_to(mdir_res):
                    return None
                if cand.is_file():
                    return cand
        if web_root is not None:
            wr = web_root.resolve()
            cand = (wr / raw.lstrip("/")).resolve()
            if cand.is_relative_to(wr) and cand.is_file():
                return cand
    for root in (base_dir, web_root):
        if root is None:
            continue
        rdir = root.resolve()
        cand = (rdir / raw.lstrip("/")).resolve() if raw.startswith("/") else (rdir / raw).resolve()
        if cand.is_relative_to(rdir) and cand.is_file():
            return cand
    return None


def audit_css_text(css_text: str, source: str, errs: list[str]) -> None:
    clean_css = COMMENT_RE.sub("", css_text)
    if _IMPORTANT_RE.search(clean_css):
        errs.append(f"[IMPORTANT] {source}: contains forbidden '!important' declaration")
    for m in _FONT_PX_RE.finditer(clean_css):
        if float(m.group(1)) < 11.0:
            errs.append(f"[FONT_FLOOR] {source}: hardcoded font-size {m.group(1)}px < 11px")


def _find_closing_delim(text: str, start: int, open_ch: str, close_ch: str) -> int:
    depth, i, n, quote = 1, start + 1, len(text), ""
    while i < n and depth > 0:
        ch = text[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in ("'", '"', "`"):
            quote = ch
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            nl = text.find("\n", i + 2)
            i = n if nl < 0 else nl + 1
            continue
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
        i += 1
    return i if depth == 0 else -1


def has_demo_branch_mock_array(js_text: str) -> bool:
    if _DEMO_TERNARY_RE.search(js_text):
        return True
    n = len(js_text)
    for m in re.finditer(r"\bif\s*\(", js_text, re.IGNORECASE):
        cond_end = _find_closing_delim(js_text, m.end() - 1, "(", ")")
        if cond_end < 0 or not _DEMO_GUARD_RE.search(js_text[m.end() : cond_end - 1]):
            continue
        i = cond_end
        while i < n and js_text[i].isspace():
            i += 1
        if i >= n:
            continue
        if js_text[i] == "{":
            blk_end = _find_closing_delim(js_text, i, "{", "}")
            body = js_text[i : blk_end if blk_end > 0 else n]
        else:
            b_depth, k_depth, j, quote = 0, 0, i, ""
            while j < n:
                ch = js_text[j]
                if quote:
                    if ch == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if ch == quote:
                        quote = ""
                    j += 1
                    continue
                if ch in ("'", '"', "`"):
                    quote = ch
                elif ch == "{":
                    b_depth += 1
                elif ch == "}":
                    if b_depth == 0 and k_depth == 0:
                        break
                    b_depth = max(0, b_depth - 1)
                elif ch == "[":
                    k_depth += 1
                elif ch == "]":
                    k_depth = max(0, k_depth - 1)
                elif ch in (";", "\n") and b_depth == 0 and k_depth == 0:
                    j += 1
                    break
                j += 1
            body = js_text[i:j]
        if _MULTI_OBJ_ARR_RE.search(body):
            return True
    return False


def audit_js_text(js_text: str, source: str, errs: list[str]) -> None:
    fname = Path(urllib.parse.urlsplit(source).path or source).name.lower()
    if fname.startswith("demo_snapshot") or fname.endswith(".min.js"):
        return
    m_id = _BRAIN_JS_RE.search(js_text)
    if m_id:
        errs.append(f"[INTERNAL_ID] {source}: exposes raw agent storage identifier '{m_id.group(0)[:40]}'")
    if _NAMED_MOCK_ARR_RE.search(js_text) or has_demo_branch_mock_array(js_text):
        errs.append(f"[INLINE_MOCK_DATA] {source}: contains hardcoded inline demo/mock object array")


def has_responsive_table_stacking(css_text: str) -> bool:
    for m in _NARROW_AT_RE.finditer(css_text):
        start, depth, i = m.end(), 1, m.end()
        while i < len(css_text) and depth > 0:
            if css_text[i] == "{":
                depth += 1
            elif css_text[i] == "}":
                depth -= 1
            i += 1
        block = css_text[start:i]
        if re.search(r"\btable\b", block, re.I) and re.search(r"display\s*:\s*(?:block|grid|flex)", block, re.I):
            return True
    return False
