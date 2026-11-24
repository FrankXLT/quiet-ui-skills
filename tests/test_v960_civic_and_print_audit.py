# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.6.0 tests: 5 civic compilers, Takeaway Chart/Table + Copy for AI, v22 brief, and 5 CDP gates."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
AUDITOR_SCRIPTS = REPO_ROOT / "skills" / "quiet-ui" / "scripts"
for _p in (str(EVIDENCE_SCRIPTS), str(AUDITOR_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from audit_quiet_html import audit_static_target, run_cdp_target  # noqa: E402
from compile_evidence import compile_spec  # noqa: E402


def _has_chrome() -> bool:
    return bool(shutil.which("chromium") or shutil.which("google-chrome") or os.environ.get("CHROME_BIN"))


class TestCivicCompilersAndExport(unittest.TestCase):
    """Verify Specimens 45–49 compilation, Takeaway metadata, and interactive exports."""

    def test_five_new_civic_specimens_and_invariants(self) -> None:
        specs = json.loads((REPO_ROOT / "docs/bench/specimens/m4_civic_research.json").read_text("utf-8"))
        self.assertEqual(len(specs), 5)

        hex_html = compile_spec(specs[0], rigor="L1", theme="white")
        self.assertEqual(hex_html.count('class="va-hex-tile'), 51)
        self.assertIn('fill="#0F172A"', hex_html)
        self.assertIn('fill="#FFFFFF"', hex_html)

        dumb_html = compile_spec(specs[1], rigor="L2", theme="white")
        self.assertIn("fallback-note", dumb_html)
        self.assertIn("2022–2023 pooled cohort", dumb_html)
        self.assertIn("<polygon", dumb_html)
        self.assertIn("(unchanged)", dumb_html)

        sub_html = compile_spec(specs[2], rigor="L1", theme="white")
        self.assertIn("All Adults", sub_html)
        self.assertIn("Adults Ages 18–29", sub_html)

        slope_html = compile_spec(specs[3], rigor="L2", theme="white")
        self.assertIn("2021 cross", slope_html)
        self.assertIn("Public Infrastructure", slope_html)
        self.assertNotIn("…", slope_html)
        self.assertNotIn("...", slope_html)

        mat_html = compile_spec(specs[4], rigor="L2", theme="white")
        self.assertIn("va-diverging-matrix", mat_html)
        self.assertIn('data-diverge="pos-hi"', mat_html)
        self.assertIn('class="num va-cell-level"', mat_html)
        self.assertIn("20.0%", mat_html)
        self.assertIn("Copy for AI", mat_html)
        self.assertIn('role="status"', mat_html)
        for sp in specs[:4]:
            frag = compile_spec(sp)
            self.assertIn('data-qe-view="table"', frag)
            self.assertIn('hidden="until-found"', frag)
            self.assertIn('data-qe-copy="ai"', frag)


class TestV960EditorialAndPrintGatesCDP(unittest.TestCase):
    """Run live Chrome CDP checks on v22, Specimens 45–49, and all 5 editorial/print auditor codes."""

    def _require_or_skip(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise AssertionError("QUIET_REQUIRE_CDP=1 requires selenium")
            self.skipTest("selenium not installed")
        if not _has_chrome():
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise AssertionError("QUIET_REQUIRE_CDP=1 requires Chromium/Chrome")
            self.skipTest("Chrome/Chromium absent")

    def test_v22_brief_and_specimen_45_49_interactions_cdp(self) -> None:
        self._require_or_skip()
        try:
            from cdp_gates import create_headless_driver, set_viewport, start_http_server
        except ImportError:
            from tests.cdp_gates import create_headless_driver, set_viewport, start_http_server

        srv, port = start_http_server(REPO_ROOT)
        root_url = f"http://127.0.0.1:{port}"
        driver = create_headless_driver()
        try:
            driver.execute_cdp_cmd(
                "Browser.grantPermissions",
                {"permissions": ["clipboardReadWrite", "clipboardSanitizedWrite"]},
            )
            from selenium.webdriver.common.by import By

            set_viewport(driver, 1440, 900, 1)
            driver.get(f"{root_url}/quiet-ui-showcase.html?world=04-civic-finance-and-stem-learning&view=v22-reading-and-mobility-brief&theme=white")
            time.sleep(0.35)
            driver.switch_to.frame("va-stage-portal")

            # Initially US National has zero selected state hex outline
            init_sel = driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);")
            self.assertEqual(init_sel, [], f"Expected zero hex outlines on US National load, got {init_sel}")

            # Scope toggle US -> Maryland -> Wyoming -> back to US National
            driver.execute_script("document.querySelector('[data-v22-scope=\"md\"]').click();")
            md_sel = driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);")
            self.assertEqual(md_sel, ["MD"])

            driver.execute_script("document.querySelector('[data-v22-scope=\"wy\"]').click();")
            wy_sel = driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);")
            self.assertEqual(wy_sel, ["WY"])
            lead_wy = driver.execute_script("return document.querySelector('[data-v22-lead]').textContent;")
            self.assertIn("36% of Wyoming", lead_wy)
            self.assertIn("$72,495", driver.execute_script("return document.querySelectorAll('.va-callout-num')[1].textContent;"))

            driver.execute_script("document.querySelector('[data-v22-scope=\"us\"]').click();")
            us_sel = driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);")
            self.assertEqual(us_sel, [], f"Expected US National scope click to clear hex outline, got {us_sel}")

            # Hex tile click readout
            driver.execute_script("document.querySelector('.va-hex-tile[data-state=\"DC\"]').dispatchEvent(new MouseEvent('click', {bubbles:true}));")
            ro = driver.execute_script("return document.querySelector('.va-hex-readout').textContent;")
            self.assertIn("District of Columbia (DC): 26%", ro)

            # In-card Chart -> Table toggle and Copy for AI status confirmation (authentic click)
            driver.execute_script("document.querySelector('#v22-map [data-qe-view=\"table\"]').click();")
            tbl_visible = driver.execute_script("const p=document.querySelector('#v22-map .va-card-table-panel');return !p.hasAttribute('hidden') && p.querySelectorAll('tbody tr').length===51;")
            self.assertTrue(tbl_visible, "Chart -> Table toggle did not reveal 51-row table")
            driver.find_element(By.CSS_SELECTOR, '#v22-map [data-qe-copy="ai"]').click()
            time.sleep(0.15)
            status_txt = driver.execute_script("return document.querySelector('#v22-map .va-copy-status').textContent;")
            self.assertIn("Copied for AI", status_txt)

            # Web Brief -> 16:9 Slide Deck toggle
            driver.execute_script("document.querySelector('[data-v22-format=\"deck\"]').click();")
            deck_vis = driver.execute_script("return !document.querySelector('.va-brief-slides').hidden && document.querySelector('.va-brief-web').hidden;")
            self.assertTrue(deck_vis)
            driver.switch_to.default_content()

            # Dark theme checks on v22 + print ink contrast reset + Bench copy confirmation opacity + sticky topbar clearance
            driver.get(f"{root_url}/quiet-ui-showcase.html?world=04-civic-finance-and-stem-learning&view=v22-reading-and-mobility-brief&theme=dark")
            time.sleep(0.3)
            driver.switch_to.frame("va-stage-portal")
            btn_colors = driver.execute_script(
                "const b=document.querySelector('.va-scope-btn.is-active');"
                "const cs=getComputedStyle(b);return {fg:cs.color,bg:cs.backgroundColor};"
            )
            def _lum(rgb_s: str) -> float:
                nums = [int(x) / 255.0 for x in rgb_s.replace("rgba(", "").replace("rgb(", "").split(")")[0].split(",")[:3]]
                lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in nums]
                return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
            l_fg, l_bg = _lum(btn_colors["fg"]), _lum(btn_colors["bg"])
            ratio = (max(l_fg, l_bg) + 0.05) / (min(l_fg, l_bg) + 0.05)
            self.assertGreaterEqual(ratio, 4.5, f"Active scope button contrast {ratio:.2f}:1 < 4.5:1 ({btn_colors})")
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
            time.sleep(0.1)
            print_ink = driver.execute_script("return getComputedStyle(document.querySelector('.va-brief-question')).color;")
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
            self.assertLess(_lum(print_ink), 0.05, f"Expected dark print ink even from dark theme, got {print_ink}")
            driver.switch_to.default_content()

            driver.get(f"{root_url}/docs/bench/evidence-bench.html")
            time.sleep(0.35)
            clr = driver.execute_script(
                "const c=[...document.querySelectorAll('.qe-specimen')].find(e=>/Equal-Area US 51-Hex Tile Map/i.test(e.textContent||''));"
                "c.scrollIntoView({behavior:'instant',block:'start'});"
                "const tb=document.querySelector('.qe-topbar').getBoundingClientRect().bottom;"
                "const ct=c.getBoundingClientRect().top;"
                "return {tb, ct};"
            )
            self.assertGreaterEqual(clr["ct"], clr["tb"] + 8.0, f"Sticky topbar overlapped scrolled card header: {clr}")
            btn = driver.find_element(By.CSS_SELECTOR, '.qe-specimen [data-qe-copy="ai"]')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.08)
            btn.click()
            time.sleep(0.25)
            status_res = driver.execute_script(
                "const btn=document.querySelector('.qe-specimen [data-qe-copy=\"ai\"]');"
                "const st=btn.closest('.va-card-actions').querySelector('.qe-copy-status');"
                "return {t:st.textContent,op:getComputedStyle(st).opacity};"
            )
            self.assertIn("Copied for AI", status_res["t"])
            self.assertGreaterEqual(float(status_res["op"]), 0.99, f"Expected visible copy confirmation opacity>=0.99, got {status_res}")
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()

    def test_auditor_catches_and_clears_5_editorial_print_failures(self) -> None:
        self._require_or_skip()
        bad_html = """<!DOCTYPE html>
<html lang="en" data-theme="white" data-medium="m2">
<head><meta charset="utf-8"><title>Broken Editorial Sample</title>
<style>
  body { margin: 0; font-family: sans-serif; font-size: 15px; background: #fff; color: #111; }
  .bad-fixed { position: fixed; top: 0; left: 0; right: 0; height: 48px; background: #1e293b; color: #fff; }
  .split { display: flex; gap: 16px; width: 100%; }
  .narrow-prose { width: 190px; height: 95px; overflow-y: auto; font-size: 15px; }
  .wide-viz { width: 760px; }
  pre.dark-slab { background: #000000; color: #f8fafc; padding: 14px; width: 320px; }
  table.clip-tbl { width: 1350px; }
  figure.overlap-fig { position: relative; margin-bottom: -45px; }
</style></head>
<body>
  <div class="bad-fixed">Sticky Header Bar</div>
  <main>
    <h1>Broken Research Article</h1>
    <div class="split">
      <div class="narrow-prose">
        <p>First long narrative paragraph explaining public reading outcomes across jurisdictions with details.</p>
        <p>Second narrative paragraph trapped inside a short scrollable container with overflow clipping.</p>
        <p>Third paragraph hidden below the scroll fold.</p>
      </div>
      <div class="wide-viz">
        <svg viewBox="0 0 420 180" width="420" height="180" role="img" aria-label="Sample Chart">
          <text x="16" y="90" transform="rotate(-90 16 90)" font-size="12">Rate<tspan x="16" dy="16">Line Two</tspan></text>
          <text x="160" y="150" transform="rotate(-45 160 150)" font-size="12">2024 Quarter 1</text>
          <text x="385" y="70" font-size="12">Very Long Series Label…</text>
        </svg>
      </div>
    </div>
    <figure class="overlap-fig"><svg viewBox="0 0 320 90" width="320" height="90"><rect x="4" y="4" width="300" height="80" fill="#cbd5e1"/></svg></figure>
    <p>Paragraph overlapping the negative-margin figure in print layout test.</p>
    <pre class="dark-slab"><code>print("dark slab")</code></pre>
    <table class="clip-tbl"><tr><th>Column</th><td>Value</td></tr></table>
  </main>
</body></html>"""

        clean_html = """<!DOCTYPE html>
<html lang="en" data-theme="white" data-medium="m2">
<head><meta charset="utf-8"><title>Clean Editorial Sample</title>
<style>
  body { margin: 24px; font-family: sans-serif; font-size: 16px; background: #ffffff; color: #0f172a; }
  .split { display: grid; grid-template-columns: minmax(320px, 1fr) minmax(0, 1.3fr); gap: 24px; }
  .clean-prose { font-size: 16px; line-height: 1.5; }
  pre.calm-code { background: #f1f5f9; color: #0f172a; padding: 14px; border: 1px solid #cbd5e1; width: 360px; }
  table.fit-tbl { width: 100%; }
  @media print { .no-print { display: none; } }
</style></head>
<body>
  <div class="no-print" style="position:fixed;top:0;left:0;right:0;height:40px;background:#fff">Screen Bar</div>
  <main>
    <h1>Clean Research Article</h1>
    <div class="split">
      <div class="clean-prose">
        <p>First long narrative paragraph explaining public reading outcomes clearly without clipping.</p>
        <p>Second narrative paragraph sitting cleanly at full document height with ample column width.</p>
      </div>
      <figure>
        <svg viewBox="0 0 420 180" width="420" height="180" role="img" aria-label="Clean Chart">
          <text x="60" y="150" font-size="12">2024 Q1</text>
          <text x="280" y="70" font-size="12">Maryland (35%)</text>
        </svg>
      </figure>
    </div>
    <pre class="calm-code"><code>print("calm light surface")</code></pre>
    <table class="fit-tbl"><tr><th>State</th><td>35%</td></tr></table>
  </main>
</body></html>"""

        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            bad_p, clean_p = tdir / "bad.html", tdir / "clean.html"
            bad_p.write_text(bad_html, encoding="utf-8")
            clean_p.write_text(clean_html, encoding="utf-8")

            bad_st, bad_files = audit_static_target(str(bad_p), allow_showcase_chrome=True)
            bad_errs = list(bad_st) + run_cdp_target(str(bad_p), bad_files, allow_showcase_chrome=True)
            joined = "\n".join(bad_errs)
            for code in (
                "[PRINT_FLOW_COLLISION]",
                "[PROSE_COLUMN_STARVATION]",
                "[NESTED_PROSE_SCROLL]",
                "[CODE_LUMINANCE_SHOCK]",
                "[DIAGONAL_TICK_OR_ROTATED_Y_TITLE]",
                "[END_LABEL_CLIP]",
            ):
                self.assertIn(code, joined, f"Expected auditor code {code}, got:\n{joined}")

            clean_st, clean_files = audit_static_target(str(clean_p), allow_showcase_chrome=True)
            clean_errs = list(clean_st) + run_cdp_target(str(clean_p), clean_files, allow_showcase_chrome=True)
            clean_ed = [e for e in clean_errs if any(c in e for c in ("PRINT_FLOW", "PROSE_COLUMN", "NESTED_PROSE", "CODE_LUMINANCE", "DIAGONAL_TICK", "END_LABEL_CLIP"))]
            self.assertEqual(clean_ed, [], f"False editorial/print failures on clean doc:\n" + "\n".join(clean_ed))
