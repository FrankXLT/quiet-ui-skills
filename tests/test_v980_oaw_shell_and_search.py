#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""v9.8.0+ unified OAW shell, scoped Ctrl+K search, and search-index schema tests."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import unittest
from pathlib import Path
from typing import Any

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
AUDITOR_SCRIPTS = REPO_ROOT / "skills" / "quiet-ui" / "scripts"
for _p in (TESTS_DIR, AUDITOR_SCRIPTS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from audit_static_rules import audit_json_text  # noqa: E402
from cdp_gates import ALL_WORLDS_VIEWS, create_headless_driver, set_viewport, start_http_server  # noqa: E402

SITE_BASE = "https://projects.oaworkbench.org/quiet-ui-skills/"
REQUIRED_ENTRY_KEYS = {"id", "pillar", "title", "category", "summary", "keywords", "url"}
VIEWPORTS = ((390, 844), (860, 1000), (900, 1000), (1440, 900))


def _poll_js(driver: Any, script: str, *args: Any, timeout: float = 3.0) -> Any:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        res = driver.execute_script(script, *args)
        if res:
            return res
        time.sleep(0.06)
    return driver.execute_script(script, *args)


def _can_launch_cdp() -> tuple[bool, str]:
    if os.environ.get("QUIET_SKIP_CDP") == "1":
        return False, "QUIET_SKIP_CDP=1"
    try:
        drv = create_headless_driver()
        drv.quit()
        return True, ""
    except Exception as exc:
        return False, str(exc)


class TestOawShellAndSearchStatic(unittest.TestCase):
    """Static manifest schema, hygiene, and 3-route HTML shell contract checks."""

    def test_search_index_manifests_schema_and_hygiene(self) -> None:
        targets = (
            (REPO_ROOT / "docs" / "search-index.json", SITE_BASE),
            (REPO_ROOT / "customizations" / "project-site-starter" / "site" / "search-index.json", None),
        )
        for path, required_prefix in targets:
            raw = path.read_text(encoding="utf-8")
            errs: list[str] = []
            audit_json_text(raw, str(path), errs)
            self.assertEqual(errs, [], f"{path} failed audit_json_text: {errs}")

            data = json.loads(raw)
            self.assertEqual(data.get("version"), "1.5.0", str(path))
            self.assertEqual(data.get("updated_at"), "2026-11-27", str(path))
            self.assertRegex(str(data.get("updated_at")), r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(data.get("pillar"), "projects", str(path))

            prefix = required_prefix or str(data.get("site_url") or "")
            self.assertTrue(prefix.startswith("https://"), f"{path}: missing canonical site_url")
            entries = data.get("entries")
            self.assertIsInstance(entries, list)
            self.assertGreater(len(entries), 0)
            for idx, entry in enumerate(entries):
                self.assertEqual(set(entry.keys()), REQUIRED_ENTRY_KEYS, f"{path} entry[{idx}] keys")
                self.assertEqual(entry["pillar"], "projects")
                for key in ("id", "title", "category", "summary", "url"):
                    self.assertIsInstance(entry[key], str)
                    self.assertTrue(entry[key].strip(), f"{path} entry[{idx}].{key} empty")
                self.assertTrue(entry["url"].startswith(prefix), f"{path} entry[{idx}] url={entry['url']}")
                kws = entry["keywords"]
                self.assertIsInstance(kws, list)
                self.assertTrue(all(isinstance(k, str) and k.strip() for k in kws))

    def test_docs_search_index_covers_overview_demo_bench_and_chapters(self) -> None:
        data = json.loads((REPO_ROOT / "docs" / "search-index.json").read_text(encoding="utf-8"))
        urls = {e["url"] for e in data["entries"]}
        self.assertIn(SITE_BASE, urls)

        expected_views = [f"?domain={w}&view={v}" for w, views in ALL_WORLDS_VIEWS for v in views]
        self.assertEqual(len(expected_views), 26)
        for q in expected_views:
            self.assertTrue(any(u.startswith(f"{SITE_BASE}demo/") and q in u for u in urls), f"Missing Studio view {q}")

        bench_html = (REPO_ROOT / "docs" / "bench" / "evidence-bench.html").read_text(encoding="utf-8")
        specimen_ids = re.findall(r'<article\b[^>]*class="[^"]*\bqe-specimen\b[^>]*>\s*<(?:figure|div)\b[^>]*\bid="([^"]+)"', bench_html)
        self.assertEqual(len(specimen_ids), 53, f"Expected 53 specimen ids in bench HTML, got {len(specimen_ids)}")
        for sid in specimen_ids:
            self.assertIn(f"{SITE_BASE}bench/evidence-bench.html#{sid}", urls, f"Missing bench specimen #{sid}")

        docs_html = (REPO_ROOT / "docs" / "docs" / "index.html").read_text(encoding="utf-8")
        chapter_ids = re.findall(r'<(?:article|section)\b[^>]*class="[^"]*\boaw-docs?-section\b[^>]*\bid="(doc-[^"]+)"', docs_html)
        self.assertGreaterEqual(len(chapter_ids), 5)
        for cid in chapter_ids:
            self.assertIn(f"{SITE_BASE}docs/#{cid}", urls, f"Missing Docs chapter #{cid}")

    def test_route_html_shell_contracts(self) -> None:
        routes = (
            ("overview", REPO_ROOT / "docs" / "index.html", False),
            ("demo", REPO_ROOT / "docs" / "demo" / "index.html", False),
            ("docs", REPO_ROOT / "docs" / "docs" / "index.html", True),
        )
        for name, path, expect_subbar in routes:
            html_txt = path.read_text(encoding="utf-8")
            self.assertNotIn("oaw-pop-stage1-back", html_txt, f"{name}: legacy stage1 back link present")
            pop_m = re.search(r'<div id="oaw-projects-popover".*?</ul>', html_txt, re.S)
            self.assertIsNotNone(pop_m, f"{name}: missing #oaw-projects-popover")
            pop_html = pop_m.group(0)
            first_li = re.search(r"<li\b[^>]*>.*?</li>", pop_html, re.S)
            self.assertIsNotNone(first_li)
            self.assertIn("All Projects", first_li.group(0), f"{name}: Row 1 must be All Projects")
            for label in ("Antigravity Nexus", "Quiet User Interface Skills", "Advanced Network Utilities"):
                self.assertIn(label, pop_html, f"{name}: missing project {label}")

            for token in ('id="oaw-route-btn"', 'id="oaw-route-menu"', 'id="oaw-search-btn"', "Search", ">Ctrl+K</kbd>"):
                self.assertIn(token, html_txt, f"{name}: missing {token}")

            pillar_m = re.search(r'<div id="oaw-pillar-popover".*?</ul>', html_txt, re.S)
            self.assertIsNotNone(pillar_m, f"{name}: missing #oaw-pillar-popover")
            pillar_html = pillar_m.group(0)
            self.assertRegex(pillar_html, r'<a\b[^>]*href="https://research\.oaworkbench\.org/"[^>]*>.*?Research.*?oaw-pop-badge--preview[^>]*>Preview<')
            for pair in (("Learn", "Open Preview"), ("Projects", "Active"), ("Home", "")):
                self.assertIn(pair[0], pillar_html)
                if pair[1]:
                    self.assertIn(pair[1], pillar_html)

            has_subbar = 'id="oaw-docs-subbar"' in html_txt
            self.assertEqual(has_subbar, expect_subbar, f"{name}: subbar mismatch")
            if expect_subbar:
                self.assertIn('id="oaw-docs-toc-trigger"', html_txt)
                self.assertIn("Chapters", html_txt)
                self.assertIn('id="oaw-docs-current-chapter"', html_txt)


class TestOawShellAndSearchCDP(unittest.TestCase):
    """Headless Chrome CDP behavioral tests for OAW shell, docs subbar, popovers, search, and themes."""

    srv: Any = None
    driver: Any = None
    docs_root_url: str = ""

    @classmethod
    def setUpClass(cls) -> None:
        require_cdp = os.environ.get("QUIET_REQUIRE_CDP") == "1"
        ok, reason = _can_launch_cdp()
        if not ok:
            if require_cdp:
                raise AssertionError(f"QUIET_REQUIRE_CDP=1 set but Headless Chrome/Selenium unavailable: {reason}")
            raise unittest.SkipTest(f"CDP shell/search suite skipped ({reason})")
        cls.srv, port = start_http_server(REPO_ROOT / "docs")
        cls.docs_root_url = f"http://127.0.0.1:{port}"
        cls.driver = create_headless_driver()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.driver is not None:
            cls.driver.quit()
        if cls.srv is not None:
            cls.srv.shutdown()
            cls.srv.server_close()

    def test_cdp_viewports_overview_and_demo(self) -> None:
        script = """
        const w = arguments[0];
        if (document.documentElement.scrollWidth > document.documentElement.clientWidth)
          return `overflow ${document.documentElement.scrollWidth} > ${document.documentElement.clientWidth}`;
        if (document.getElementById('oaw-docs-subbar')) return 'unexpected #oaw-docs-subbar';
        const tb = document.querySelector('.oaw-topbar')?.getBoundingClientRect();
        if (!tb || tb.height < 44 || tb.height > 48) return `topbar height=${tb?.height}`;
        const rBtn = document.getElementById('oaw-route-btn'), rMenu = document.getElementById('oaw-route-menu');
        const rVis = rBtn && getComputedStyle(rBtn).display !== 'none' && rBtn.getBoundingClientRect().width > 0;
        if (w < 900 && !rVis) return '#oaw-route-btn should be visible';
        if (w >= 900) {
          if (rVis) return '#oaw-route-btn should be hidden';
          const links = [...(rMenu?.querySelectorAll('.oaw-nav-link') || [])];
          if (links.length < 3 || links.some(l => l.getBoundingClientRect().width <= 0 || l.getBoundingClientRect().height > 48))
            return 'inline route tabs malformed';
        }
        const sBtn = document.getElementById('oaw-search-btn'), sr = sBtn?.getBoundingClientRect();
        const txt = sBtn?.querySelector('.oaw-search-text'), kbd = sBtn?.querySelector('.oaw-search-kbd');
        if (!sr) return 'missing #oaw-search-btn';
        if (w < 960) {
          if (sr.width < 28 || sr.width > 36 || sr.height < 28 || sr.height > 36) return `compact search btn ${sr.width}x${sr.height}`;
          if (getComputedStyle(txt).display !== 'none' || getComputedStyle(kbd).display !== 'none') return 'search text/kbd visible <960';
        } else if (sr.width <= 60 || getComputedStyle(txt).display === 'none' || getComputedStyle(kbd).display === 'none') {
          return 'search btn not expanded >=960';
        }
        return '';
        """
        for route in ("/", "/demo/"):
            for w, h in VIEWPORTS:
                set_viewport(self.driver, w, h, 1)
                self.driver.get(f"{self.docs_root_url}{route}?theme=white")
                _poll_js(self.driver, "return Boolean(document.querySelector('.oaw-topbar'));")
                self.assertEqual(self.driver.execute_script(script, w), "", f"{route} @ {w}x{h}")

    def test_cdp_docs_subbar_and_chapters_drawer(self) -> None:
        expected_pos = {390: "sticky", 860: "static", 900: "static"}
        layout_js = """
        const w = arguments[0], expPos = arguments[1];
        if (document.documentElement.scrollWidth > document.documentElement.clientWidth)
          return `overflow ${document.documentElement.scrollWidth} > ${document.documentElement.clientWidth}`;
        const sub = document.getElementById('oaw-docs-subbar'), rail = document.querySelector('.oaw-docs-rail');
        if (!sub || !rail) return 'missing subbar or rail';
        const subCs = getComputedStyle(sub), railCs = getComputedStyle(rail);
        if (w < 960) {
          const sr = sub.getBoundingClientRect();
          if (subCs.display === 'none' || sr.height < 34 || sr.height > 42) return `subbar height=${sr.height}`;
          if (subCs.position !== expPos) return `subbar position=${subCs.position} expected=${expPos}`;
          if (railCs.display !== 'none') return 'rail visible <960';
        } else {
          if (subCs.display !== 'none') return 'subbar visible >=960';
          if (railCs.display === 'none' || railCs.position !== 'sticky') return `rail display=${railCs.display} pos=${railCs.position}`;
        }
        return '';
        """
        for w, h in VIEWPORTS:
            set_viewport(self.driver, w, h, 1)
            self.driver.get(f"{self.docs_root_url}/docs/?theme=white")
            _poll_js(self.driver, "return Boolean(document.getElementById('oaw-docs-subbar'));")
            self.assertEqual(self.driver.execute_script(layout_js, w, expected_pos.get(w, "")), "", f"/docs/ @ {w}x{h}")

        set_viewport(self.driver, 390, 844, 1)
        self.driver.get(f"{self.docs_root_url}/docs/?theme=white")
        _poll_js(self.driver, "return Boolean(document.getElementById('oaw-docs-toc-trigger'));")
        drawer_err = self.driver.execute_script(
            """
            const trig = document.getElementById('oaw-docs-toc-trigger'), dlg = document.getElementById('oaw-docs-toc-dialog');
            const cur = document.getElementById('oaw-docs-current-chapter');
            trig.click();
            if (!dlg.open) return 'TOC dialog failed to open';
            const target = dlg.querySelectorAll('.oaw-docs-toc-list a[href^="#"]:not(.oaw-docs-sub)')[1];
            if (!target) return 'missing second chapter link';
            const expTitle = target.textContent.trim(), targetHref = target.getAttribute('href');
            target.click();
            if (dlg.open) return 'TOC dialog failed to close after chapter click';
            if (cur.textContent.trim() !== expTitle) return `chapter text=${cur.textContent.trim()} expected=${expTitle}`;
            const active = [...document.querySelectorAll('.oaw-docs-toc-list a[aria-current="location"], .oaw-docs-rail a[aria-current="location"]')];
            if (!active.some(a => a.getAttribute('href') === targetHref)) return 'missing aria-current=location on selected chapter';
            trig.click();
            return dlg.open ? '' : 'TOC dialog failed to reopen';
            """
        )
        self.assertEqual(drawer_err, "")
        set_viewport(self.driver, 1440, 900, 1)
        self.assertTrue(_poll_js(self.driver, "return !document.getElementById('oaw-docs-toc-dialog').open;"))

    def test_cdp_popovers_links_and_badges(self) -> None:
        set_viewport(self.driver, 1440, 900, 1)
        self.driver.get(f"{self.docs_root_url}/?theme=white")
        _poll_js(self.driver, "return Boolean(document.getElementById('oaw-pillar-btn'));")
        err = self.driver.execute_script(
            """
            for (const [bid, pid] of [['oaw-projects-btn', 'oaw-projects-popover'], ['oaw-pillar-btn', 'oaw-pillar-popover']]) {
              const btn = document.getElementById(bid), pop = document.getElementById(pid);
              btn.click();
              if (!(pop.matches?.(':popover-open') || pop.classList.contains('is-open'))) return `${pid} failed to open`;
              for (const a of pop.querySelectorAll('a'))
                if (getComputedStyle(a).textDecorationLine === 'underline') return `underlined link in ${pid}: ${a.textContent}`;
              if (pid === 'oaw-pillar-popover') {
                const badge = pop.querySelector('.oaw-pop-badge--preview');
                if (!badge || getComputedStyle(badge).color === getComputedStyle(badge).backgroundColor) return 'preview badge invalid';
                const resLink = pop.querySelector('a[href="https://research.oaworkbench.org/"]');
                if (!resLink || resLink.getBoundingClientRect().height < 20) return 'missing clickable Research link';
              }
              if (typeof pop.hidePopover === 'function' && pop.matches(':popover-open')) pop.hidePopover(); else btn.click();
            }
            return '';
            """
        )
        self.assertEqual(err, "")

    def _assert_search_keyboard_and_ime(self, keys_cls: Any) -> None:
        self.driver.execute_script("const i = document.getElementById('oaw-search-input'); i.value = 'quiet'; i.dispatchEvent(new Event('input', {bubbles: true})); i.focus();")
        self.assertTrue(_poll_js(self.driver, "return document.querySelectorAll('#oaw-search-results a.oaw-search-item').length >= 2;"))
        inp = self.driver.find_element("id", "oaw-search-input")
        inp.send_keys(keys_cls.ARROW_DOWN)
        self.assertEqual(self.driver.execute_script("return document.getElementById('oaw-search-input').getAttribute('aria-activedescendant');"), "oaw-search-opt-1")
        self.assertEqual(self.driver.execute_script("return document.getElementById('oaw-search-opt-1').getAttribute('aria-selected');"), "true")
        self.driver.execute_script(
            "const i = document.getElementById('oaw-search-input');"
            "i.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', isComposing: true, bubbles: true, cancelable: true }));"
            "i.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', isComposing: true, bubbles: true, cancelable: true }));"
        )
        self.assertEqual(self.driver.execute_script("return document.getElementById('oaw-search-input').getAttribute('aria-activedescendant');"), "oaw-search-opt-1")
        self.assertTrue(self.driver.execute_script("return document.getElementById('oaw-search-dialog').open && document.getElementById('oaw-search-input').value === 'quiet';"))
        inp.send_keys(keys_cls.ARROW_UP)
        self.assertEqual(self.driver.execute_script("return document.getElementById('oaw-search-input').getAttribute('aria-activedescendant');"), "oaw-search-opt-0")
        inp.send_keys(keys_cls.ESCAPE)
        self.assertTrue(self.driver.execute_script("return document.getElementById('oaw-search-dialog').open && document.getElementById('oaw-search-input').value === '';"))
        inp.send_keys(keys_cls.ESCAPE)
        self.assertTrue(_poll_js(self.driver, "return !document.getElementById('oaw-search-dialog').open;"))
        self.assertEqual(self.driver.execute_script("return document.activeElement?.id;"), "oaw-search-btn")

    def _assert_all_oaw_remote_fallback(self) -> None:
        self.driver.execute_script(
            """
            const origFetch = window.fetch.bind(window);
            window.fetch = (url, opts) => {
              const u = String(url);
              if (u.startsWith('https://learn.oaworkbench.org/')) {
                return Promise.resolve(new Response(JSON.stringify({
                  version: '1.5.0', pillar: 'learn', project_title: 'OAW Learn',
                  entries: [{ id: 'learn-thermo', pillar: 'learn', title: 'Carnot Thermodynamics Lab', category: 'Physics', summary: 'Interactive cycle workbench', keywords: ['carnot', 'entropy'], url: 'https://learn.oaworkbench.org/thermo/' }]
                }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
              }
              if (u.includes('oaworkbench.org/search-index.json')) return Promise.reject(new Error('offline'));
              return origFetch(url, opts);
            };
            document.getElementById('oaw-search-btn').click();
            document.querySelector('.oaw-scope-btn[data-search-scope="all"]').click();
            """
        )
        all_ok = _poll_js(
            self.driver,
            "const allBtn = document.querySelector('.oaw-scope-btn[data-search-scope=\"all\"]');"
            "const status = document.getElementById('oaw-search-status')?.textContent || '';"
            "const i = document.getElementById('oaw-search-input'); i.value = 'carnot'; i.dispatchEvent(new Event('input', {bubbles: true}));"
            "const hit = [...document.querySelectorAll('#oaw-search-results a.oaw-search-item')].some(a => a.textContent.includes('Carnot Thermodynamics Lab'));"
            "return allBtn?.getAttribute('aria-pressed') === 'true' && status.includes('offline') && hit;",
        )
        self.assertTrue(all_ok, "All OAW toggle failed remote merge or graceful offline fallback")

    def test_cdp_scoped_ctrl_k_search(self) -> None:
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys

        set_viewport(self.driver, 1440, 900, 1)
        self.driver.get(f"{self.docs_root_url}/?theme=white")
        _poll_js(self.driver, "return Boolean(window.OawSiteSearch && document.getElementById('oaw-search-btn'));")
        self.assertIsNone(self.driver.execute_script("return document.getElementById('oaw-search-dialog');"))
        self.driver.execute_script("document.getElementById('oaw-search-btn').click();")
        self.assertTrue(_poll_js(self.driver, "return Boolean(document.getElementById('oaw-search-dialog')?.open);"))
        self.driver.execute_script("document.getElementById('oaw-search-close').click();")
        self.assertTrue(_poll_js(self.driver, "return !document.getElementById('oaw-search-dialog')?.open;"))

        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("k").key_up(Keys.CONTROL).perform()
        self.assertTrue(_poll_js(self.driver, "return Boolean(document.getElementById('oaw-search-dialog')?.open);"))
        self.assertEqual(self.driver.execute_script("return document.querySelector('.oaw-scope-btn[data-search-scope=\"space\"]')?.getAttribute('aria-pressed');"), "true")
        self.assertTrue(_poll_js(self.driver, "return document.querySelectorAll('#oaw-search-results a.oaw-search-item').length > 0;"))
        for query, expected_frag in (("icu bedside", "demo/index.html?domain="), ("hex tile", "bench/evidence-bench.html#"), ("brand customization", "docs/index.html#doc-")):
            self.driver.execute_script("const i = document.getElementById('oaw-search-input'); i.value = arguments[0]; i.dispatchEvent(new Event('input', {bubbles: true}));", query)
            matched = _poll_js(self.driver, "return [...document.querySelectorAll('#oaw-search-results a.oaw-search-item')].some(a => (a.getAttribute('href') || '').includes(arguments[0]));", expected_frag)
            self.assertTrue(matched, f"Query '{query}' missing match containing '{expected_frag}'")
        self._assert_search_keyboard_and_ime(Keys)
        self._assert_all_oaw_remote_fallback()

    def _filter_and_pick_ctrl_k_hidden_chapter(self, actions_cls: Any, keys_cls: Any, target_id: str) -> None:
        self.driver.execute_script("const d = document.getElementById('oaw-docs-search'); d.value = 'install in one command'; d.dispatchEvent(new Event('input', {bubbles: true}));")
        self.assertTrue(self.driver.execute_script("return Boolean(document.getElementById(arguments[0])?.hidden);", target_id))
        actions_cls(self.driver).key_down(keys_cls.CONTROL).send_keys("k").key_up(keys_cls.CONTROL).perform()
        self.assertTrue(_poll_js(self.driver, "return Boolean(document.getElementById('oaw-search-dialog')?.open && document.querySelectorAll('#oaw-search-results a.oaw-search-item').length > 0);"))
        self.driver.execute_script("const i = document.getElementById('oaw-search-input'); i.value = 'workflows'; i.dispatchEvent(new Event('input', {bubbles: true}));")
        item_sel = f'#oaw-search-results a.oaw-search-item[href*="#{target_id}"]'
        self.assertTrue(_poll_js(self.driver, "return Boolean(document.querySelector(arguments[0]));", item_sel))
        self.driver.execute_script("document.querySelector(arguments[0]).click();", item_sel)
        landed = _poll_js(
            self.driver,
            "const sec = document.getElementById(arguments[0]), d = document.getElementById('oaw-docs-search'), dlg = document.getElementById('oaw-search-dialog');"
            "if (!sec || sec.hidden || dlg?.open || d?.value !== '' || location.hash !== '#' + arguments[0]) return false;"
            "const r = sec.getBoundingClientRect(); return window.scrollY > 0 && r.top >= 46 && r.top < window.innerHeight * 0.75 && r.bottom > 46;",
            target_id,
        )
        self.assertTrue(landed, f"Ctrl+K jump to #{target_id} failed to unhide, clear filter, or scroll")

    def test_cdp_docs_ctrl_k_unhide_and_escape_popover(self) -> None:
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys

        set_viewport(self.driver, 1440, 900, 1)
        self.driver.get(f"{self.docs_root_url}/docs/?theme=white")
        _poll_js(self.driver, "return Boolean(window.OawSiteSearch && document.getElementById('oaw-docs-search'));")
        self._filter_and_pick_ctrl_k_hidden_chapter(ActionChains, Keys, "doc-workflows-and-project-site")
        self.driver.execute_script("window.scrollTo(0, 0);")
        self._filter_and_pick_ctrl_k_hidden_chapter(ActionChains, Keys, "doc-workflows-and-project-site")

        self.driver.execute_script("const d = document.getElementById('oaw-docs-search'); d.value = 'brand'; d.dispatchEvent(new Event('input', {bubbles: true})); document.getElementById('oaw-user-btn').click();")
        self.assertTrue(_poll_js(self.driver, "const p = document.getElementById('oaw-user-popover'); return Boolean(p?.matches?.(':popover-open') || p?.classList.contains('is-open') || p?.dataset?.open === 'true');"))
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        closed = _poll_js(self.driver, "const p = document.getElementById('oaw-user-popover'); return !(p?.matches?.(':popover-open') || p?.classList.contains('is-open') || p?.dataset?.open === 'true');")
        self.assertTrue(closed, "#oaw-user-popover did not close on Escape")
        self.assertEqual(self.driver.execute_script("return document.getElementById('oaw-docs-search').value;"), "brand")

    def test_cdp_docs_mobile_subheading_scroll_clearance(self) -> None:
        set_viewport(self.driver, 390, 844, 1)
        self.driver.get(f"{self.docs_root_url}/docs/?theme=white")
        _poll_js(self.driver, "return Boolean(document.getElementById('oaw-docs-toc-trigger'));")
        target_id = "three-pillars-pillar-comparison-table"
        self.driver.execute_script(
            "document.getElementById('oaw-docs-toc-trigger').click();"
            "document.querySelector('#oaw-docs-toc-dialog .oaw-docs-toc-list a[href=\"#' + arguments[0] + '\"]').click();",
            target_id,
        )
        settled = _poll_js(
            self.driver,
            "const dlg = document.getElementById('oaw-docs-toc-dialog'), el = document.getElementById(arguments[0]);"
            "if (!el || dlg?.open || window.scrollY <= 0) return null;"
            "const y = window.scrollY; window.__oawStable = (window.__oawLastY === y) ? (window.__oawStable || 0) + 1 : 0;"
            "window.__oawLastY = y; return window.__oawStable >= 2 ? { top: el.getBoundingClientRect().top } : null;",
            target_id,
        )
        self.assertIsInstance(settled, dict, "Mobile TOC subheading scroll did not settle")
        self.assertGreaterEqual(settled["top"], 84.0, f"Subheading top={settled['top']} overlaps 46px topbar + 38px subbar")
        self.assertLess(settled["top"], 260.0, f"Subheading top={settled['top']} did not scroll near top")

    def test_cdp_theme_persistence(self) -> None:
        set_viewport(self.driver, 1440, 900, 1)
        self.driver.get(f"{self.docs_root_url}/?theme=white")
        self.driver.execute_script("localStorage.clear();")
        _poll_js(self.driver, "return Boolean(document.getElementById('oaw-user-btn'));")
        self.driver.execute_script("document.getElementById('oaw-user-btn').click(); document.querySelector('.oaw-theme-opt[data-theme-opt=\"dark\"]').click();")
        self.assertEqual(
            self.driver.execute_script("return [document.documentElement.dataset.theme, localStorage.getItem('oaw_theme_v99'), localStorage.getItem('quiet-ui-site-theme')];"),
            ["dark", "dark", "dark"],
        )
        self.driver.execute_script("document.querySelector('a[data-oaw-route-link=\"demo\"]').click();")
        self.assertTrue(_poll_js(self.driver, "return location.pathname.endsWith('/demo/index.html') && document.documentElement.dataset.theme === 'dark' && document.querySelector('.oaw-demo-chrome')?.dataset?.theme === 'dark';"))
        self.driver.get(f"{self.docs_root_url}/docs/")
        self.assertTrue(_poll_js(self.driver, "return document.documentElement.dataset.theme === 'dark';"))


if __name__ == "__main__":
    unittest.main()
