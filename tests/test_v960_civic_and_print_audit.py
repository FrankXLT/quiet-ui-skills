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
        self.assertIn('role="group"', hex_html)
        self.assertIn('va-hex-focus-ring', hex_html)
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
        self.assertIn("is-overall", sub_html)
        self.assertIn('class="qe-svg qe-svg-880"', sub_html)
        self.assertNotIn('data-qe-view="table"', sub_html)
        self.assertIn('data-qe-copy="ai"', sub_html)

        slope_html = compile_spec(specs[3], rigor="L2", theme="white")
        self.assertIn("2021 cross", slope_html)
        self.assertIn("Public Infrastructure", slope_html)
        self.assertNotIn("va-slope-legend", slope_html)
        self.assertNotIn("Analytical Model", slope_html)
        self.assertNotIn("…", slope_html)
        self.assertNotIn("...", slope_html)

        mat_html = compile_spec(specs[4], rigor="L2", theme="white")
        self.assertIn("va-diverging-matrix", mat_html)
        self.assertIn('data-diverge="pos-hi"', mat_html)
        self.assertIn('data-diverge="flat"', mat_html)
        self.assertIn("0.0 pp", mat_html)
        self.assertIn("Mobility vs 20% Baseline (pp)", mat_html)
        self.assertIn("qe-caption-sr", mat_html)
        self.assertIn('class="num va-cell-level"', mat_html)
        self.assertIn("20.0%", mat_html)
        self.assertIn("Copy for AI", mat_html)
        self.assertIn('role="status"', mat_html)

        for idx in (0, 1, 3):
            frag = compile_spec(specs[idx])
            self.assertIn('data-qe-view="table"', frag)
            self.assertIn('qe-caption-sr', frag)
            self.assertIn('class="num"', frag)
            self.assertIn('hidden="until-found"', frag)
            self.assertIn('data-qe-copy="ai"', frag)

        ed_frag = compile_spec(specs[0], rigor="L1", theme="white", chrome="editorial", include_spec_drawer=False)
        self.assertIn("is-editorial", ed_frag)
        self.assertNotIn("va-card-actions", ed_frag)
        self.assertIn("data-qe-editorial-toggle", ed_frag)
        self.assertIn("Show data table", ed_frag)
        self.assertIn("va-editorial-footer-line", ed_frag)
        self.assertIn('<div class="va-card-table-panel" id=', ed_frag)
        self.assertNotIn("va-card-table-panel va-table-wrap", ed_frag)

        for p_rel in (
            "content/corpora/02-cloud-cyber-and-ai-ops/evidence/v06_ai_calibration_plot.json",
            "content/corpora/04-civic-finance-and-stem-learning/evidence/v11_treasury_drawdown_plot.json",
        ):
            curve_frag = compile_spec(REPO_ROOT / p_rel, rigor="L3", medium="m3")
            self.assertIn('data-qe-view="table"', curve_frag)
            self.assertIn("± u_y", curve_frag)


class TestV960EditorialAndPrintGatesCDP(unittest.TestCase):
    """Run live Chrome CDP checks on Path A v22, Specimens 45–49, v06/v11 toggles, 390px picker, and print gates."""

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
            driver.execute_cdp_cmd("Browser.grantPermissions", {"permissions": ["clipboardReadWrite", "clipboardSanitizedWrite"]})
            from selenium.webdriver.common.by import By

            set_viewport(driver, 1440, 900, 1)
            driver.get(f"{root_url}/quiet-ui-showcase.html?world=04-civic-finance-and-stem-learning&view=v22-reading-and-mobility-brief&theme=white")
            time.sleep(0.35)
            driver.switch_to.frame("va-stage-portal")

            # Path A structural invariants: n0 zero sidebar, provenance eyebrow, inline select, unboxed figures, zero slide/code/toolbar clutter
            v22_layout = driver.execute_script(
                "const nav=document.documentElement.dataset.effectiveNav;"
                "const railVis=getComputedStyle(document.getElementById('va-shell-rail')).display;"
                "const barCnt=document.querySelectorAll('#v22-public-brief .va-card-actions').length;"
                "const preCnt=document.querySelectorAll('#v22-public-brief pre').length;"
                "const slideCnt=document.querySelectorAll('#v22-public-brief .va-brief-slides').length;"
                "const selW=document.querySelector('[data-v22-scope-select]').getBoundingClientRect().width;"
                "const proseW=document.querySelector('#v22-reading-essay').getBoundingClientRect().width;"
                "const hexW=document.querySelector('#v22-map').getBoundingClientRect().width;"
                "const hexTop=document.querySelector('#v22-map svg').getBoundingClientRect().top;"
                "return {nav, railVis, barCnt, preCnt, slideCnt, selW, proseW, hexW, hexTop};"
            )
            self.assertEqual((v22_layout["nav"], v22_layout["railVis"]), ("n0", "none"))
            self.assertEqual((v22_layout["barCnt"], v22_layout["preCnt"], v22_layout["slideCnt"]), (0, 0, 0))
            self.assertGreater(v22_layout["hexW"], v22_layout["proseW"] + 60.0)
            self.assertLess(v22_layout["hexTop"], 900.0)

            init_sel = driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);")
            self.assertEqual(init_sel, [], f"Expected zero hex outlines on US National load, got {init_sel}")

            # Inline sentence scope select US -> Maryland -> Wyoming -> US National
            driver.execute_script("const s=document.querySelector('[data-v22-scope-select]');s.value='md';s.dispatchEvent(new Event('change',{bubbles:true}));")
            self.assertEqual(driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);"), ["MD"])

            driver.execute_script("const s=document.querySelector('[data-v22-scope-select]');s.value='wy';s.dispatchEvent(new Event('change',{bubbles:true}));")
            self.assertEqual(driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);"), ["WY"])
            lead_wy = driver.execute_script("return document.querySelector('[data-v22-lead]').textContent;")
            self.assertIn("36% of Wyoming", lead_wy)
            self.assertIn("$72,495", driver.execute_script("return document.querySelectorAll('.va-callout-num')[1].textContent;"))

            driver.execute_script("const s=document.querySelector('[data-v22-scope-select]');s.value='us';s.dispatchEvent(new Event('change',{bubbles:true}));")
            self.assertEqual(driver.execute_script("return [...document.querySelectorAll('.va-hex-tile.is-selected')].map(e=>e.dataset.state);"), [])

            # Hex tile click readout + keyboard Enter focus retention
            driver.execute_script("document.querySelector('.va-hex-tile[data-state=\"DC\"]').dispatchEvent(new MouseEvent('click', {bubbles:true}));")
            ro = driver.execute_script("return document.querySelector('.va-hex-readout').textContent;")
            self.assertIn("District of Columbia (DC): 26%", ro)
            ca_tile = driver.find_element(By.CSS_SELECTOR, '.va-hex-tile[data-state="CA"]')
            driver.execute_script("arguments[0].focus();", ca_tile)
            ca_tile.send_keys("\n")
            kept_focus = driver.execute_script("return document.activeElement?.getAttribute('data-state') || '';")
            self.assertEqual(kept_focus, "CA", "Hex tile activation dropped keyboard focus")

            # Quiet footer Show data table -> borderless top Show chart return -> focus return + Copy for AI
            driver.execute_script("document.querySelector('#v22-map [data-qe-editorial-toggle]').click();")
            tbl_chk = driver.execute_script(
                "const p=document.querySelector('#v22-map .va-card-table-panel'), w=p.querySelector('.va-table-wrap'),"
                " bar=p.querySelector('.va-table-top-bar'), ret=p.querySelector('[data-qe-editorial-return]');"
                "const wr=w.getBoundingClientRect(), rr=ret.getBoundingClientRect();"
                "return {vis:!p.hasAttribute('hidden'), rows:p.querySelectorAll('tbody tr').length,"
                " capW:p.querySelector('caption').getBoundingClientRect().width,"
                " btnTxt:document.querySelector('#v22-map [data-qe-editorial-toggle]').textContent,"
                " align:getComputedStyle(p.querySelector('tbody td.num')).textAlign,"
                " pBdr:parseFloat(getComputedStyle(p).borderTopWidth), inWrap:!!(w&&w.contains(bar)),"
                " gap:wr.top-rr.bottom, rDelta:Math.abs(wr.right-rr.right)};"
            )
            self.assertTrue(tbl_chk["vis"] and not tbl_chk["inWrap"] and tbl_chk["pBdr"] == 0.0, tbl_chk)
            self.assertEqual((tbl_chk["rows"], tbl_chk["btnTxt"], tbl_chk["align"]), (51, "Show chart", "right"))
            self.assertLessEqual(tbl_chk["capW"], 2.0)
            self.assertGreaterEqual(tbl_chk["gap"], 4.0, tbl_chk)
            self.assertLessEqual(tbl_chk["rDelta"], 1.0, tbl_chk)
            ret_chk = driver.execute_script(
                "document.querySelector('#v22-map [data-qe-editorial-return]').click();"
                "const t=document.querySelector('#v22-map [data-qe-editorial-toggle]');"
                "return {txt:t.textContent, focused:document.activeElement===t, hid:document.querySelector('#v22-map .va-card-table-panel').hasAttribute('hidden')};"
            )
            self.assertEqual(ret_chk, {"txt": "Show data table", "focused": True, "hid": True})

            copy_link = driver.find_element(By.CSS_SELECTOR, '#v22-map [data-qe-copy="ai"]')
            w_before = float(copy_link.rect["width"])
            copy_link.click()
            time.sleep(0.15)
            copy_chk = driver.execute_script(
                "const b=document.querySelector('#v22-map [data-qe-copy=\"ai\"]');"
                "return {txt:b.textContent.trim(), st:document.querySelector('#v22-map .va-copy-status').textContent, w:b.getBoundingClientRect().width};"
            )
            self.assertIn("Copied for AI", copy_chk["txt"])
            self.assertIn("Copied for AI", copy_chk["st"])
            self.assertLessEqual(abs(copy_chk["w"] - w_before), 1.5)
            arrow_chk = driver.execute_script(
                "const g=document.querySelector('#v22-dumbbell .va-arrow-legend svg.va-arrow-swatch.is-gain');"
                "const d=document.querySelector('#v22-dumbbell .va-arrow-legend svg.va-arrow-swatch.is-drop');"
                "const gr=g?.getBoundingClientRect(), dr=d?.getBoundingClientRect();"
                "return {gW:gr?.width||0,gH:gr?.height||0,dW:dr?.width||0,dH:dr?.height||0,"
                "gCol:g?getComputedStyle(g).color:'',dCol:d?getComputedStyle(d).color:''};"
            )
            self.assertTrue(14.0 <= arrow_chk["gW"] <= 24.0 and 6.0 <= arrow_chk["gH"] <= 16.0, arrow_chk)
            self.assertTrue(14.0 <= arrow_chk["dW"] <= 24.0 and 6.0 <= arrow_chk["dH"] <= 16.0, arrow_chk)
            self.assertNotEqual(arrow_chk["gCol"], arrow_chk["dCol"])
            driver.switch_to.default_content()

            # Dark theme inline select contrast + @media print ink reset + footer link hidden
            driver.get(f"{root_url}/quiet-ui-showcase.html?world=04-civic-finance-and-stem-learning&view=v22-reading-and-mobility-brief&theme=dark")
            time.sleep(0.3)
            driver.switch_to.frame("va-stage-portal")
            sel_cols = driver.execute_script(
                "const b=document.querySelector('[data-v22-scope-select]');"
                "const cs=getComputedStyle(b), bs=getComputedStyle(document.body);return {fg:cs.color,bg:bs.backgroundColor};"
            )
            def _lum(rgb_s: str) -> float:
                nums = [int(x) / 255.0 for x in rgb_s.replace("rgba(", "").replace("rgb(", "").split(")")[0].split(",")[:3]]
                lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in nums]
                return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
            l_fg, l_bg = _lum(sel_cols["fg"]), _lum(sel_cols["bg"])
            ratio = (max(l_fg, l_bg) + 0.05) / (min(l_fg, l_bg) + 0.05)
            self.assertGreaterEqual(ratio, 4.5, f"Inline select contrast {ratio:.2f}:1 < 4.5:1 ({sel_cols})")
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
            time.sleep(0.1)
            print_ink = driver.execute_script("return getComputedStyle(document.querySelector('.va-brief-question')).color;")
            link_disp = driver.execute_script("return getComputedStyle(document.querySelector('.va-footer-link')).display;")
            cue_disp = driver.execute_script("return getComputedStyle(document.querySelector('.va-scroll-cue')).display;")
            driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "screen"})
            self.assertLess(_lum(print_ink), 0.05, f"Expected dark print ink even from dark theme, got {print_ink}")
            self.assertEqual(link_disp, "none")
            self.assertEqual(cue_disp, "none")
            driver.switch_to.default_content()

            # Explorer curves (v11 & v06) Table toggle + left-aligned col0 row headers + return to Chart
            driver.get(f"{root_url}/quiet-ui-showcase.html?world=04-civic-finance-and-stem-learning&view=v11-treasury-stress-test-solver&theme=white")
            time.sleep(0.35)
            driver.switch_to.frame("va-stage-portal")
            driver.execute_script("document.querySelector('[data-qe-view=\"table\"]').click();")
            v11_tbl = driver.execute_script(
                "const p=document.querySelector('.va-card-table-panel');"
                "const h0=p.querySelector('thead th:first-child'), r0=p.querySelector('tbody th[scope=\"row\"], tbody td:first-child');"
                "const rl=[...p.querySelectorAll('tbody tr :first-child')].map(e=>e.textContent.trim());"
                "const td=p.querySelector('tbody td.num');"
                "return {ok:!p.hasAttribute('hidden')&&rl.length===8,hA:getComputedStyle(h0).textAlign,rA:getComputedStyle(r0).textAlign,"
                "tdA:getComputedStyle(td).textAlign,rl0:rl[0],rl7:rl[7],hasNum:r0.classList.contains('num')};"
            )
            self.assertTrue(v11_tbl["ok"], "v11 Table toggle should show 8 quarters")
            self.assertIn(v11_tbl["hA"], {"left", "start"})
            self.assertIn(v11_tbl["rA"], {"left", "start"})
            self.assertFalse(v11_tbl["hasNum"])
            self.assertEqual(v11_tbl["tdA"], "right")
            self.assertEqual((v11_tbl["rl0"], v11_tbl["rl7"]), ("1", "8"))
            driver.execute_script("document.querySelector('[data-qe-view=\"chart\"]').click();")
            self.assertTrue(driver.execute_script("return document.querySelector('.va-card-table-panel').hasAttribute('hidden');"))
            driver.switch_to.default_content()

            driver.get(f"{root_url}/quiet-ui-showcase.html?world=02-cloud-cyber-and-ai-ops&view=v06-ai-drift-and-lineage-ide&theme=white")
            time.sleep(0.35)
            driver.switch_to.frame("va-stage-portal")
            driver.execute_script("document.querySelector('#w02-v06-ai-calibration-plot [data-qe-view=\"table\"]').click();")
            v06_tbl = driver.execute_script(
                "const p=document.querySelector('#w02-v06-ai-calibration-plot .va-card-table-panel');"
                "const r0=p.querySelector('tbody th[scope=\"row\"]');"
                "return {ok:!p.hasAttribute('hidden')&&p.querySelectorAll('tbody tr').length===10,"
                "rA:getComputedStyle(r0).textAlign,r0Txt:r0.textContent.trim()};"
            )
            self.assertTrue(v06_tbl["ok"], "v06 Table toggle should show 10 calibration bins")
            self.assertIn(v06_tbl["rA"], {"left", "start"})
            self.assertEqual(v06_tbl["r0Txt"], "0.05")
            driver.execute_script("document.querySelector('#w02-v06-ai-calibration-plot [data-qe-view=\"chart\"]').click();")
            self.assertTrue(driver.execute_script("return document.querySelector('#w02-v06-ai-calibration-plot .va-card-table-panel').hasAttribute('hidden');"))
            driver.switch_to.default_content()

            # Component Library Specimens 45-49 checks
            driver.get(f"{root_url}/docs/bench/evidence-bench.html")
            time.sleep(0.35)
            bench_chk = driver.execute_script(
                "const specs=[...document.querySelectorAll('.qe-specimen')];"
                "const s49=specs.find(e=>e.querySelector('#m2-l2-diverging-mobility-matrix'));"
                "const cue=s49.querySelector('.va-scroll-cue');"
                "const s45=specs.find(e=>/Equal-Area US 51-Hex Tile Map/i.test(e.textContent||''));"
                "s45.scrollIntoView({behavior:'instant',block:'start'});"
                "const tb=document.querySelector('.qe-topbar').getBoundingClientRect().bottom;"
                "const ct=s45.getBoundingClientRect().top;"
                "return {tb, ct, s49Wide:s49.classList.contains('qe-specimen-wide'), cueDisp:getComputedStyle(cue).display};"
            )
            self.assertGreaterEqual(bench_chk["ct"], bench_chk["tb"] + 8.0)
            self.assertTrue(bench_chk["s49Wide"], "Specimen 49 should span full grid width")
            self.assertEqual(bench_chk["cueDisp"], "none", "Desktop non-overflowing Specimen 49 should hide horizontal scroll cue")

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

            # 390px mobile Studio topbar picker readable width without clipping + M1 scroll-cue suppression
            set_viewport(driver, 390, 844, 1)
            driver.get(f"{root_url}/quiet-ui-showcase.html?world=04-civic-finance-and-stem-learning&view=v22-reading-and-mobility-brief&theme=white&medium=m1")
            time.sleep(0.3)
            mob_chk = driver.execute_script(
                "const bar=document.getElementById('va-studio-bar').getBoundingClientRect();"
                "const ctr=document.querySelector('.va-bar-center').getBoundingClientRect();"
                "const sel=document.getElementById('va-view-select').getBoundingClientRect();"
                "const cmp=document.getElementById('va-tab-components');"
                "const cmpClip=cmp.scrollWidth>cmp.clientWidth+1;"
                "const d=document.getElementById('va-stage-portal').contentDocument;"
                "const m1Cue=d.querySelector('#v22-matrix .va-scroll-cue');"
                "return {barH:bar.height, selW:sel.width, selClip:sel.right>ctr.right+1, cmpClip, ov:document.documentElement.scrollWidth>window.innerWidth+1, m1CueDisp:m1Cue?getComputedStyle(m1Cue).display:'none'};"
            )
            self.assertLessEqual(mob_chk["barH"], 48.5)
            self.assertGreaterEqual(mob_chk["selW"], 120.0, f"Expected mobile #va-view-select >=120px wide, got {mob_chk}")
            self.assertFalse(mob_chk["selClip"], f"Expected #va-view-select unclipped inside .va-bar-center, got {mob_chk}")
            self.assertFalse(mob_chk["cmpClip"], f"Expected Components tab unclipped, got {mob_chk}")
            self.assertFalse(mob_chk["ov"], "390px Studio bar caused horizontal overflow")
            self.assertEqual(mob_chk["m1CueDisp"], "none", f"Expected M1 scroll-cue hidden at 390px, got {mob_chk}")
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
