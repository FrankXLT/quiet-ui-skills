# SPDX-License-Identifier: Apache-2.0
"""Interactive workbench, stage-width, hitbox, tree-indent & copy-leak probes for Quiet UI."""

from __future__ import annotations

import re
import time
from html.parser import HTMLParser
from typing import Any

GRAMMAR_LEAK_RE = re.compile(r"(?:^|[^0-9.,])\b1\s+(?:messages|msgs)\b", re.IGNORECASE)
STEM_STUTTER_RE = re.compile(r"\b([a-z0-9][a-z0-9._-]{1,64})\s*[·•|/]\s*\1@", re.IGNORECASE)


class _TextLeakParser(HTMLParser):
    def __init__(self, source: str, errs: list[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.errs = errs
        self.skip_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in {"script", "style", "pre", "code", "template"}:
            self.skip_stack.append(t)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in self.skip_stack:
            idx = len(self.skip_stack) - 1 - self.skip_stack[::-1].index(t)
            del self.skip_stack[idx:]

    def handle_data(self, data: str) -> None:
        if self.skip_stack or not data.strip():
            return
        for pat, desc in (
            (GRAMMAR_LEAK_RE, "singular/plural grammar glitch"),
            (STEM_STUTTER_RE, "stuttering slug/email stem"),
        ):
            if pat is STEM_STUTTER_RE and "@" not in data:
                continue
            m = pat.search(data)
            if m:
                self.errs.append(f"[RAW_SLUG_OR_GRAMMAR_LEAK] {self.source}:{self.getpos()[0]}: {desc} '{m.group(0).strip()}'")


def audit_workbench_static(html_text: str, source: str, errs: list[str]) -> None:
    """Flag static visible copy leaks ('1 messages', '1 msgs', 'foo · foo@') outside code/pre."""
    parser = _TextLeakParser(source, errs)
    parser.feed(html_text)
    parser.close()


CDP_WORKBENCH_PROBES_JS = r"""
const GRAMMAR_LEAK_CDP_RE = /(?:^|[^0-9.,])\b1\s+(?:messages|msgs)\b/i;
const STEM_STUTTER_CDP_RE = /\b([a-z0-9][a-z0-9._-]{1,64})\s*[·•|/]\s*\1@/i;

function textStartEdge(el, win, isRtl) {
  const cs = win.getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const hasInnerLbl = !!el.querySelector('.va-tree-label, span:first-child');
  if (isRtl) return r.right - (hasInnerLbl ? 0 : (parseFloat(cs.paddingRight || '0') || 0));
  return r.left + (hasInnerLbl ? 0 : (parseFloat(cs.paddingLeft || '0') || 0));
}

function auditDocV940Workbench(doc, win, ctxTag, opts) {
  const allowShow = !!(opts && opts.allowShowcase);
  const notHiddenAnc = (el) => {
    for (let p = el; p && p.nodeType === 1; p = p.parentElement) {
      if (p.hasAttribute('hidden') || win.getComputedStyle(p).display === 'none') return false;
    }
    return true;
  };
  const isRtl = ((doc.documentElement && doc.documentElement.dir) || doc.dir || '').toLowerCase() === 'rtl';

  if (vw >= 1920) {
    for (const st of doc.querySelectorAll('.va-stage')) {
      if (!isVis(st, win.getComputedStyle(st)) || !notHiddenAnc(st)) continue;
      const wb = st.querySelector('.va-workbench-panes');
      if (!wb || !isVis(wb, win.getComputedStyle(wb))) continue;
      const cs = win.getComputedStyle(st);
      const rawMax = String(cs.maxInlineSize || cs.maxWidth || '').trim();
      if (rawMax && rawMax !== 'none') {
        const px = parseFloat(rawMax);
        if (Number.isFinite(px) && px > 0 && px < 1360) {
          pushErr(`[WORKBENCH_STAGE_TUNNEL${ctxTag}] @${vw}px: .va-stage holding .va-workbench-panes caps max-inline-size=${px.toFixed(0)}px (< 1360px)`);
        }
      }
    }
  }

  if (vw < 700) {
    const dock = doc.querySelector('.va-shell-bottomdock');
    const dockVis = dock && isVis(dock, win.getComputedStyle(dock)) && notHiddenAnc(dock);
    const topTabs = [...doc.querySelectorAll('.va-shell-topbar [role="tablist"], .va-shell-topbar .va-tab-strip')].some((t) => isVis(t, win.getComputedStyle(t)) && notHiddenAnc(t));
    if (dockVis && topTabs) {
      pushErr(`[DUPLICATE_PRIMARY_NAV${ctxTag}] @${vw}px: .va-shell-topbar [role="tablist"] and .va-shell-bottomdock both visible`);
    }
  }

  for (const tb of doc.querySelectorAll('.va-toolbar-joined')) {
    const cs = win.getComputedStyle(tb);
    if (!isVis(tb, cs) || !notHiddenAnc(tb)) continue;
    const rawBtns = [...tb.querySelectorAll('.va-tb-btn')].filter((b) => isVis(b, win.getComputedStyle(b)) && notHiddenAnc(b));
    const directOrUnboxed = rawBtns.filter((b) => {
      if (b.parentElement === tb) return true;
      const grp = b.closest('.va-tb-group');
      if (!grp || grp === tb) return true;
      const gcs = win.getComputedStyle(grp);
      const gBg = parseAlphaColor(gcs.backgroundColor) >= 0.05;
      const gBd = ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(gcs['border' + s + 'Width'] || '0') >= 0.5 && parseAlphaColor(gcs['border' + s + 'Color']) >= 0.05);
      return !(gBg || gBd);
    });
    if (directOrUnboxed.length < 2) continue;
    const hasBg = parseAlphaColor(cs.backgroundColor) >= 0.05;
    const hasBd = ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width'] || '0') >= 0.5 && parseAlphaColor(cs['border' + s + 'Color']) >= 0.05);
    if (!hasBg && !hasBd) {
      pushErr(`[UNBORDERED_SEGMENTED_TRACK${ctxTag}] @${vw}px: .va-toolbar-joined with ${directOrUnboxed.length} .va-tb-btn controls lacks segmented background/border`);
    }
  }

  for (const el of doc.querySelectorAll('svg .va-hit-target, svg [data-hit-target], svg [data-role="hit"], svg rect')) {
    const cs = win.getComputedStyle(el);
    if (!isVis(el, cs) || !notHiddenAnc(el)) continue;
    const isHitCls = el.matches('.va-hit-target, [data-hit-target], [data-role="hit"], [class*="hitbox"]');
    const fillAttr = String(el.getAttribute('fill') || '').trim().toLowerCase();
    const fillComp = String(cs.fill || '').trim().toLowerCase();
    const fo = parseFloat(el.getAttribute('fill-opacity') || cs.fillOpacity || '1');
    const isInteractive = cs.cursor === 'pointer' || cs.pointerEvents === 'all' || el.hasAttribute('tabindex') || el.getAttribute('role') === 'button';
    const isInteractiveRect = el.tagName.toLowerCase() === 'rect' && isInteractive && (
      fillAttr === 'transparent' || isTransparentPaint(fillComp) || (fo === 0 && fillAttr !== 'none')
    );
    if (!isHitCls && !isInteractiveRect) continue;
    const st = String(cs.stroke || el.getAttribute('stroke') || 'none').trim().toLowerCase();
    const sw = parseFloat(cs.strokeWidth || el.getAttribute('stroke-width') || '0');
    const so = parseFloat(el.getAttribute('stroke-opacity') || cs.strokeOpacity || '1');
    const hasStroke = !isTransparentPaint(st) && sw >= 0.5 && parseAlphaColor(st) > 0.05 && (!Number.isFinite(so) || so > 0.05);
    const outW = parseFloat(cs.outlineWidth || '0');
    const hasOutline = cs.outlineStyle && cs.outlineStyle !== 'none' && outW >= 0.5 && !isTransparentPaint(cs.outlineColor);
    if (hasStroke || hasOutline) {
      pushErr(`[VISIBLE_HITBOX_OUTLINE${ctxTag}] @${vw}px: transparent/hit SVG target renders visible stroke or outline`);
      break;
    }
  }

  const isTreeLayoutVisible = (el) => {
    for (let p = el; p && p.nodeType === 1; p = p.parentElement) {
      if (p.hasAttribute('hidden') || win.getComputedStyle(p).display === 'none') return false;
    }
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  for (const grp of doc.querySelectorAll('.va-tree-group, .va-tree-children')) {
    if (!isTreeLayoutVisible(grp)) continue;
    let pRow = grp.previousElementSibling;
    while (pRow && !pRow.classList.contains('va-tree-row') && !pRow.querySelector('.va-tree-dest')) pRow = pRow.previousElementSibling;
    if (!pRow) continue;
    const pEl = pRow.querySelector('.va-tree-label, .va-tree-dest > span:first-child, .va-tree-dest');
    if (!pEl || !isTreeLayoutVisible(pEl)) continue;
    const pEdge = textStartEdge(pEl, win, isRtl);
    for (const ch of grp.querySelectorAll(':scope > .va-tree-row, :scope > .va-tree-dest')) {
      const cEl = ch.matches('.va-tree-dest') ? ch : (ch.querySelector('.va-tree-label, .va-tree-dest > span:first-child, .va-tree-dest') || ch);
      if (!cEl || !isTreeLayoutVisible(cEl)) continue;
      const cEdge = textStartEdge(cEl, win, isRtl);
      const badIndent = isRtl ? (cEdge > pEdge - 8) : (cEdge < pEdge + 8);
      if (badIndent) {
        pushErr(`[TREE_INDENT_INVERSION${ctxTag}] @${vw}px: expanded tree child (${cEdge.toFixed(1)}px) not indented >=8px past parent (${pEdge.toFixed(1)}px)`);
        break;
      }
    }
  }

  if (!allowShow && vw >= 1000 && win.innerHeight >= 600) {
    let evTop = Infinity;
    for (const ev of doc.querySelectorAll('.va-workbench-panes, .qe-plot-wrap, .qe-figure, .va-figure-card, .va-table-wrap, .va-split-reader-gallery, table, svg')) {
      if (ev.closest('header, nav, .va-shell-topbar, .va-kpi-grid, .va-kpi-gauge-grid')) continue;
      if (!isVis(ev, win.getComputedStyle(ev)) || !notHiddenAnc(ev)) continue;
      const r = ev.getBoundingClientRect();
      if (r.width >= 180 && r.height >= 60) evTop = Math.min(evTop, r.top);
    }
    if (Number.isFinite(evTop) && evTop > 0) {
      const ivals = [];
      const addBox = (el) => {
        if (!isVis(el, win.getComputedStyle(el)) || !notHiddenAnc(el)) return;
        const r = el.getBoundingClientRect();
        if (r.height > 4 && r.top >= -4 && r.bottom <= evTop + 12) {
          ivals.push([Math.max(0, r.top), Math.min(win.innerHeight, r.bottom)]);
        }
      };
      for (const h of doc.querySelectorAll('header, .va-shell-topbar, .va-topbar, .v9-topbar, [role="banner"]')) {
        if (!h.closest('main, .va-workbench-panes')) addBox(h);
      }
      for (const bar of doc.querySelectorAll('.va-period-stepper, .va-filter-bar, .va-kpi-grid, .va-kpi-gauge-grid, .v9-kpi-strip, [data-chrome-corridor]')) {
        if (!bar.closest('.va-workbench-panes, .va-figure-card, .qe-figure')) addBox(bar);
      }
      ivals.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
      const merged = [];
      for (const [s, e] of ivals) {
        if (!merged.length || s > merged[merged.length - 1][1]) merged.push([s, e]);
        else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], e);
      }
      const chromeH = merged.reduce((acc, [s, e]) => acc + (e - s), 0);
      if (chromeH > win.innerHeight * 0.25) {
        pushErr(`[CHROME_HEIGHT_BUDGET${ctxTag}] @${vw}px: top chrome/corridor height=${chromeH.toFixed(0)}px > 25% of ${win.innerHeight}px`);
      }
    }
  }

  if (doc.body) {
    const tw = doc.createTreeWalker(doc.body, 4);
    for (let tn; (tn = tw.nextNode()); ) {
      const val = tn.nodeValue || '';
      if (!val.trim()) continue;
      const pe = tn.parentElement;
      if (!pe || pe.closest('pre, code, script, style') || !notHiddenAnc(pe)) continue;
      const gHit = GRAMMAR_LEAK_CDP_RE.test(val) ? val.match(GRAMMAR_LEAK_CDP_RE) : null;
      const sHit = (!gHit && val.includes('@') && STEM_STUTTER_CDP_RE.test(val)) ? val.match(STEM_STUTTER_CDP_RE) : null;
      const m = gHit || sHit;
      if (m) {
        pushErr(`[RAW_SLUG_OR_GRAMMAR_LEAK${ctxTag}] @${vw}px: copy leak '${m[0].trim()}'`);
        break;
      }
    }
  }
}
"""


def probe_workbench_1920(driver: Any, url: str, theme: str, payload: dict[str, Any], audit_js: str) -> list[str]:
    """Run 1920x1080 [WORKBENCH_STAGE_TUNNEL] check when .va-stage holds .va-workbench-panes."""
    has_wb = bool(driver.execute_script("return !!document.querySelector('.va-stage .va-workbench-panes');"))
    if not has_wb:
        return []
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False})
    time.sleep(0.08)
    raw_errs = driver.execute_script(audit_js, payload) or []
    return [f"[{url} theme={theme}] {e}" for e in raw_errs if "[WORKBENCH_STAGE_TUNNEL" in str(e)]
