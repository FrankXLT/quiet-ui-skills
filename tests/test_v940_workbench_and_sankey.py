#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.4.0 Wave 2 tests: workbench CSS/JS primitives, Sankey layout & 7 portable probes."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_html.py"
CHECKS_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_checks.py"
PROBES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_cdp_probes.py"
STATIC_RULES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_static_rules.py"
UX_DRIFT_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_ux_and_drift.py"
WORKBENCH_PROBES_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_workbench_probes.py"
TOKENS_CSS = REPO_ROOT / "tokens" / "quiet-ui-tokens.css"
BUNDLE_CSS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.css"
BUNDLE_JS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.js"
BINNING_JS = REPO_ROOT / "src" / "js" / "quiet-time-binning.js"
STEPPER_JS = REPO_ROOT / "src" / "js" / "quiet-period-stepper.js"
SANKEY_JS = REPO_ROOT / "src" / "js" / "quiet-sankey-layout.js"

CLEAN_WB_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="white">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Clean Workbench</title>
  <link rel="stylesheet" href="bundle.css">
  <style>
    .demo-hdr { display: flex; justify-content: space-between; align-items: center; height: 48px; padding: 0 12px; background: var(--bg-surface); }
    .demo-n4 { display: none; }
    @media (max-width: 699px) { .demo-n4 { display: flex; position: fixed; bottom: 0; left: 0; right: 0; height: 52px; } }
  </style>
</head>
<body>
  <header class="va-shell-topbar demo-hdr">
    <span>Workbench</span>
    <nav class="va-tab-strip" role="tablist" aria-label="Views"><button class="va-tab" role="tab" aria-selected="true" type="button">Flow</button></nav>
  </header>
  <main class="va-stage" data-width="workbench" data-stage="workbench">
    <h1>Flow Overview</h1>
    <div class="va-toolbar-joined" role="toolbar" aria-label="Filters">
      <button class="va-tb-btn" data-active="true" aria-pressed="true" type="button">All</button>
      <button class="va-tb-btn" aria-pressed="false" type="button">Active</button>
    </div>
    <div class="va-workbench-panes" style="min-height: 160px;">
      <section class="va-pane">
        <div class="va-pane-hdr"><span>Groups</span></div>
        <div class="va-pane-body">
          <div class="va-tree-row"><button class="va-tree-caret" type="button" aria-label="Toggle"></button><a class="va-tree-dest" href="#v"><span class="va-tree-label">Retailers</span></a></div>
          <div class="va-tree-children"><a class="va-tree-dest" href="#a"><span class="va-tree-label">Amazon · orders@shop.example</span></a></div>
          <p>1 message shown cleanly.</p>
          <svg width="160" height="48" viewBox="0 0 160 48" role="img" aria-label="Ribbon flow">
            <rect x="0" y="0" width="160" height="48" fill="transparent" stroke="#cbd5e1" stroke-width="1"/>
            <path class="va-sankey-ribbon" d="M10 10 C60 10 100 10 150 10 L150 30 C100 30 60 30 10 30 Z" fill="var(--chart-1)"/>
            <rect class="va-hit-target" x="8" y="4" width="44" height="36"/>
          </svg>
        </div>
      </section>
    </div>
  </main>
  <nav class="va-shell-bottomdock demo-n4" aria-label="Mobile Nav"><button type="button">Flow</button></nav>
  <script>
    const syncNav = () => {
      if (window.innerWidth < 700) document.documentElement.setAttribute('data-effective-nav', 'n4');
      else document.documentElement.removeAttribute('data-effective-nav');
    };
    syncNav(); window.addEventListener('resize', syncNav);
  </script>
</body>
</html>
"""

BAD_WB_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="white">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Broken Workbench</title>
  <style>
    .bad-hdr { height: 110px; background: #ffffff; }
    .bad-kpis { height: 180px; }
    .bad-tabs { display: flex; gap: 6px; }
    .bad-dock { position: fixed; bottom: 0; left: 0; right: 0; height: 54px; display: flex; }
    .bad-tree-row { padding-left: 36px; display: flex; }
    .bad-tree-kids { padding-left: 8px; }
  </style>
</head>
<body>
  <header class="va-shell-topbar bad-hdr">
    <span>Ops</span>
    <nav class="va-tab-strip bad-tabs" role="tablist" aria-label="Top tabs"><button class="va-tab" role="tab" type="button">Home</button></nav>
  </header>
  <main class="va-stage" style="max-width: 1152px;">
    <section class="va-kpi-grid bad-kpis"><article class="va-kpi-card"><span>KPI</span><strong>42</strong></article></section>
    <div class="va-toolbar-joined" role="toolbar" aria-label="Mode">
      <button class="va-tb-btn" type="button">One</button>
      <button class="va-tb-btn" type="button">Two</button>
    </div>
    <div class="va-workbench-panes" style="min-height: 140px;">
      <aside class="va-side-rail" data-mode="overlay" data-open="false" style="visibility:hidden;position:fixed;inset:0 auto 0 0;width:260px;"><div class="va-tree-row bad-tree-row"><span class="va-tree-label">Vendors</span></div><div class="va-tree-children bad-tree-kids"><a class="va-tree-dest" href="#x"><span class="va-tree-label">Acme</span></a></div></aside>
      <svg width="160" height="48" viewBox="0 0 160 48" role="img" aria-label="Hitbox">
        <rect class="va-hit-target" x="4" y="4" width="80" height="30" fill="transparent" stroke="#334155" stroke-width="2"/>
      </svg>
      <div id="bad-copy"></div>
    </div>
  </main>
  <nav class="va-shell-bottomdock bad-dock" aria-label="Bottom tabs"><button type="button">Home</button></nav>
  <script>document.getElementById('bad-copy').textContent = '1 msgs waiting';</script>
</body>
</html>
"""


class TestV940WorkbenchAndSankey(unittest.TestCase):
    """Verify Wave 2 cleanfield CSS/JS primitives, Sankey layout, and 7 portable probes."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.auditor = self.tmp_dir / "audit_quiet_html.py"
        for src in (AUDITOR_SRC, CHECKS_SRC, PROBES_SRC, STATIC_RULES_SRC, UX_DRIFT_SRC, WORKBENCH_PROBES_SRC):
            shutil.copy2(src, self.tmp_dir / src.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run_auditor(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(self.auditor), *args],
            cwd=self.tmp_dir, capture_output=True, text=True,
        )

    def _require_cdp(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise
            self.skipTest("selenium not installed")

    def test_wave2_css_bundle_primitives(self) -> None:
        css = BUNDLE_CSS.read_text("utf-8")
        self.assertNotIn("!important", css)
        self.assertNotIn("var(--accent)", css)
        for token in (
            '.va-stage[data-width="reading"]',
            '.va-stage[data-width="workbench"]',
            "min(96vw, 112rem)",
            'html[data-effective-nav="n4"] .va-shell-topbar .va-tab-strip',
            "env(safe-area-inset-bottom",
            ".va-toolbar-joined",
            ".va-hit-target",
            ".va-hit-target.is-selected",
            ".va-sankey-active-slice { pointer-events: none; fill: var(--accent-primary);",
            ".va-toolbar-joined .va-tb-btn[data-active=\"true\"]",
            "background: Highlight;",
            ".booktabs td[data-nowrap]",
            "--sankey-ribbon-active-opacity",
            "1.5px",
            '[data-swatch="paper"]',
            '[data-swatch="dark-paper"]',
            "padding-inline-start: 2.25rem",
        ):
            self.assertIn(token, css, f"Missing '{token}' in bundled CSS")

    def test_wave2_binning_stepper_and_sankey_js(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        probe = r"""
const fs = require('fs'), vm = require('vm');
const mkDoc = (bg) => ({
  documentElement: {},
  defaultView: { getComputedStyle: () => ({ getPropertyValue: (n) => n === '--bg-card' ? bg : (n === '--border-subtle' ? '#1e293b' : '') }) },
  querySelectorAll: () => [], addEventListener: () => {},
});
const ctx = { window: {}, globalThis: {}, document: null, console, HTMLElement: function(){}, Node: function(){}, HTMLDialogElement: undefined };
ctx.window = ctx; ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(ARGS[0], 'utf8'), ctx);
vm.runInContext(fs.readFileSync(ARGS[1], 'utf8'), ctx);
vm.runInContext(fs.readFileSync(ARGS[2], 'utf8'), ctx);

const B = ctx.window.QuietTimeBinning, P = ctx.window.QuietPeriodStepper, S = ctx.window.QuietSankeyLayout;
const darkZ = B.heatmapZeroCellStyle('var(--bg-card)', 'var(--border-subtle)', mkDoc('oklch(0.18 0.02 250)'));
const lightZ = B.heatmapZeroCellStyle('var(--bg-card)', 'var(--border-subtle)', mkDoc('#FFFFFF'));
if (darkZ.fill === '#E2E8F0' || lightZ.fill !== '#E2E8F0' || darkZ.borderColor === '#1e293b') throw new Error('Bad heatmapZeroCellStyle');

const b1 = B.resolvePeriodBounds({ mode: 'rolling', preset: '30d', today: '2026-11-22', minDate: '2026-09-01', maxDate: '2026-10-31' });
const b2 = B.resolvePeriodBounds({ mode: 'cal', preset: '30d', today: '2026-11-22', minDate: '2026-10-20', maxDate: '2026-10-31' });
const bMtdPrev = B.resolvePeriodBounds({ mode: 'cal', preset: 'mtd', anchorDate: '2026-10-31', minDate: '2026-08-01', maxDate: '2026-10-31', stepDelta: -1 });
const bBad = B.resolvePeriodBounds({ mode: 'rolling', preset: 'constructor', today: 'not-a-date' });
const b52 = B.resolvePeriodBounds({ preset: 'r52w', today: '2026-11-22', minDate: '2025-01-01', maxDate: '2026-11-22' });
const bStep = P.resolveWindowBounds({ mode: 'rolling', preset: '7d', today: '2026-11-22', minDate: '2026-10-01', maxDate: '2026-10-31', stepDelta: 1 });
const lbl = { textContent: '' }, btn = { textContent: 'Today', disabled: false, setAttribute: () => {} };
const st = {
  dataset: { minDate: '2026-09-01', maxDate: '2026-10-31', today: '2026-11-22', mode: 'rolling', value: '30d' },
  setAttribute: () => {}, querySelector: (s) => s.includes('label') ? lbl : (s.includes('today') ? btn : null), querySelectorAll: () => [],
};
const modeRes = P.setPeriodMode(st, 'cal', { today: '2026-11-22' });
P.applyPresetChoice(st, { dataset: { preset: 'r30', label: '30 Days' }, disabled: false, textContent: '30 Days' });
const swRoll = st.dataset.mode + ':' + st.dataset.value;

const sorted = S.sortColumnsTopologically(
  [{ id: 's0', col: 0, count: 10 }, { id: 'm1', col: 1, count: 8 }, { id: 'm0', col: 1, count: 3 }, { id: 't0', col: 2, count: 5, rank: 0 }, { id: 't1', col: 2, count: 8, rank: 1 }, { id: 't2', col: 2, count: 9, rank: null }],
  [{ source: 'm1', target: 't1', count: 8 }, { source: 'm0', target: 't0', count: 3 }]
);
const slicePart = S.computeActiveSlice(100, 80, 40, 10, 12), sliceFull = S.computeActiveSlice(100, 80, 40, 40, 0), sliceThin = S.computeActiveSlice(10, 1.0, 20, 1, 0);
const d1 = S.dedupeStemEmail('wholefoodsmarket', 'wholefoodsmarket@shop.example'), d2 = S.dedupeStemEmail('Amazon', 'orders@amazon.com');
console.log(JSON.stringify({ b1, b2, bMtdPrev, bBad, b52, bStep, modeRes, swRoll, lbl: lbl.textContent, btnText: btn.textContent, mid: sorted.columns[1].map(n => n.id), termTail: sorted.columns[2].slice(-1)[0].id, slicePart, sliceFull, sliceThin, d1, d2 }));
""".replace("ARGS", json.dumps([str(BINNING_JS), str(STEPPER_JS), str(SANKEY_JS)]))
        res = subprocess.run([node, "-e", probe], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Node probe failed:\n{res.stderr}\n{res.stdout}")
        out = json.loads(res.stdout.strip())
        self.assertEqual(out["b1"]["endDate"], "2026-10-31")
        self.assertEqual(out["b1"]["anchorLabel"], "Latest Scanned")
        self.assertFalse(out["b1"]["canStepNext"])
        self.assertEqual(out["b2"]["label"], "MTD")
        self.assertEqual(out["b2"]["startDate"], "2026-10-20")
        self.assertEqual((out["bMtdPrev"]["startDate"], out["bMtdPrev"]["endDate"]), ("2026-09-01", "2026-09-30"))
        self.assertNotIn("NaN", out["bBad"]["startDate"] + out["bBad"]["endDate"])
        self.assertEqual(out["b52"]["label"], "52 weeks")
        self.assertEqual(out["bStep"]["endDate"], "2026-10-31")
        self.assertEqual((out["modeRes"]["label"], out["swRoll"]), ("MTD", "rolling:r30"))
        self.assertIn("30 days", out["lbl"])
        self.assertEqual(out["btnText"], "Latest Scanned")
        self.assertEqual((out["mid"], out["termTail"]), (["m0", "m1"], "t2"))
        self.assertEqual(out["slicePart"], {"isFullBar": False, "sliceY": 112, "sliceH": 20})
        self.assertEqual(out["sliceFull"], {"isFullBar": True, "sliceY": 100, "sliceH": 80})
        self.assertLessEqual(out["sliceThin"]["sliceH"], 1.0)
        self.assertEqual((out["d1"], out["d2"]), ("wholefoodsmarket@shop.example", "Amazon · orders@amazon.com"))

    def test_static_raw_slug_and_grammar_leak(self) -> None:
        bad = self.tmp_dir / "leak.html"
        bad.write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Leaks</title></head>"
            "<body><main><h1>Status</h1><p>1 messages from wholefoodsmarket · wholefoodsmarket@shop.example</p></main></body></html>",
            encoding="utf-8",
        )
        r = self._run_auditor(str(bad), "--json")
        self.assertEqual(r.returncode, 1)
        leaks = [e for e in json.loads(r.stdout)["errors"] if "[RAW_SLUG_OR_GRAMMAR_LEAK]" in e]
        self.assertEqual(len(leaks), 2)

        ok = self.tmp_dir / "clean_copy.html"
        ok.write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Clean</title></head>"
            "<body><main><h1>Status</h1><p>101 messages, 1 message archived for Amazon · orders@shop.example</p>"
            "<pre>1 messages example in pre block</pre></main></body></html>",
            encoding="utf-8",
        )
        r_ok = self._run_auditor(str(ok), "--json")
        self.assertEqual(r_ok.returncode, 0, r_ok.stdout + r_ok.stderr)

    def test_cdp_workbench_probes_fail_and_pass(self) -> None:
        self._require_cdp()
        tokens = TOKENS_CSS.read_text("utf-8")
        bundle = BUNDLE_CSS.read_text("utf-8")
        (self.tmp_dir / "bundle.css").write_text(tokens + "\n" + bundle, encoding="utf-8")

        clean = self.tmp_dir / "good_wb.html"
        clean.write_text(CLEAN_WB_HTML, encoding="utf-8")
        rc = self._run_auditor(str(clean), "--cdp", "--json")
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)

        bad = self.tmp_dir / "bad_wb.html"
        bad.write_text(BAD_WB_HTML, encoding="utf-8")
        rb = self._run_auditor(str(bad), "--cdp", "--json")
        self.assertEqual(rb.returncode, 1)
        joined = "\n".join(json.loads(rb.stdout)["errors"])
        for tag in (
            "[CHROME_HEIGHT_BUDGET]",
            "[WORKBENCH_STAGE_TUNNEL]",
            "[DUPLICATE_PRIMARY_NAV]",
            "[UNBORDERED_SEGMENTED_TRACK]",
            "[VISIBLE_HITBOX_OUTLINE]",
            "[TREE_INDENT_INVERSION]",
            "[RAW_SLUG_OR_GRAMMAR_LEAK]",
        ):
            self.assertIn(tag, joined, f"Missing {tag} in:\n{joined}")


if __name__ == "__main__":
    unittest.main()
