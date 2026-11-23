#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isolated portability tests for skills/quiet-ui/scripts/audit_quiet_html.py."""

from __future__ import annotations

import json
import os
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
COMPILER_SRC = REPO_ROOT / "skills" / "quiet-evidence" / "scripts" / "compile_evidence.py"

VALID_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="white">
<head>
  <meta charset="utf-8">
  <title>Clean Fixture</title>
  <style>
    body { font-size: 14px; }
    .va-table-wrap { overflow-x: auto; }
  </style>
</head>
<body>
  <main>
    <h1>Fixture</h1>
    <svg viewBox="0 0 24 24" role="img" aria-label="Status"><circle cx="12" cy="12" r="8"/></svg>
    <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h12"/></svg>
    <div class="va-table-wrap" tabindex="0" role="region" aria-label="Metrics">
      <table>
        <thead><tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr></thead>
        <tbody><tr><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr></tbody>
      </table>
    </div>
  </main>
</body>
</html>
"""


class TestPortableAuditor(unittest.TestCase):
    """Run audit_quiet_html.py from an isolated temp directory outside the repository."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.auditor = self.tmp_dir / "audit_quiet_html.py"
        shutil.copy2(AUDITOR_SRC, self.auditor)
        shutil.copy2(CHECKS_SRC, self.tmp_dir / "audit_quiet_checks.py")
        shutil.copy2(PROBES_SRC, self.tmp_dir / "audit_cdp_probes.py")
        shutil.copy2(STATIC_RULES_SRC, self.tmp_dir / "audit_static_rules.py")
        shutil.copy2(UX_DRIFT_SRC, self.tmp_dir / "audit_ux_and_drift.py")
        shutil.copy2(WORKBENCH_PROBES_SRC, self.tmp_dir / "audit_workbench_probes.py")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run_auditor(self, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(self.auditor), str(target), *extra],
            cwd=self.tmp_dir,
            capture_output=True,
            text=True,
        )

    def test_passes_clean_html_and_compiled_evidence_output(self) -> None:
        clean_p = self.tmp_dir / "clean.html"
        clean_p.write_text(VALID_HTML, encoding="utf-8")
        res = self._run_auditor(clean_p, "--json")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertTrue(json.loads(res.stdout)["ok"])

        spec_p = self.tmp_dir / "scalar.json"
        spec_p.write_text(
            json.dumps({
                "$schema": "urn:quiet-ui:schema:v9:scalar",
                "id": "iso-scalar",
                "metadata": {"title": "Isolated Scalar", "rigor_level": "L2"},
                "quantity": {"name": "Pressure", "symbol": "P", "unit": "kPa"},
                "measurement": {"nominal_value": 101.3, "uncertainty": 0.2},
                "status_annunciator": {"state": "NOMINAL"},
            }),
            encoding="utf-8",
        )
        compiled_p = self.tmp_dir / "compiled.html"
        subprocess.run(
            [sys.executable, "-B", str(COMPILER_SRC), str(spec_p), "--out", str(compiled_p)],
            cwd=self.tmp_dir,
            check=True,
        )
        res_comp = self._run_auditor(compiled_p)
        self.assertEqual(res_comp.returncode, 0, res_comp.stdout + res_comp.stderr)

    def test_rejects_important_tiny_font_bad_svg_and_unwrapped_table(self) -> None:
        bad_important = self.tmp_dir / "bad_imp.html"
        bad_important.write_text(VALID_HTML.replace("font-size: 14px;", "font-size: 14px !important;"), encoding="utf-8")
        r1 = self._run_auditor(bad_important)
        self.assertEqual(r1.returncode, 1)
        self.assertIn("[IMPORTANT]", r1.stdout)

        bad_font = self.tmp_dir / "bad_font.html"
        bad_font.write_text(VALID_HTML.replace("font-size: 14px;", "font-size: 9px;"), encoding="utf-8")
        r2 = self._run_auditor(bad_font)
        self.assertEqual(r2.returncode, 1)
        self.assertIn("[FONT_FLOOR]", r2.stdout)

        bad_svg = self.tmp_dir / "bad_svg.html"
        bad_svg.write_text(
            VALID_HTML.replace(
                '<svg viewBox="0 0 24 24" role="img" aria-label="Status"><circle cx="12" cy="12" r="8"/></svg>',
                '<svg><circle cx="12" cy="12" r="8"/></svg>',
            ),
            encoding="utf-8",
        )
        r3 = self._run_auditor(bad_svg)
        self.assertEqual(r3.returncode, 1)
        self.assertIn("[SVG_VIEWBOX]", r3.stdout)
        self.assertIn("[SVG_A11Y]", r3.stdout)

        bad_tbl = self.tmp_dir / "bad_tbl.html"
        bad_tbl.write_text(
            '<!DOCTYPE html><html lang="en"><body><table><tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr></table></body></html>',
            encoding="utf-8",
        )
        r4 = self._run_auditor(bad_tbl)
        self.assertEqual(r4.returncode, 1)
        self.assertIn("[TABLE_WRAP]", r4.stdout)

        sub = self.tmp_dir / "nested"
        sub.mkdir()
        (self.tmp_dir / "outside.css").write_text(".outer-fake { overflow-x: auto; }", encoding="utf-8")
        trav_html = sub / "trav.html"
        trav_html.write_text(
            '<!DOCTYPE html><html lang="en"><head><link rel="stylesheet" href="../outside.css">'
            "<style>.card .inner { overflow-x: auto; }</style></head>"
            '<body><div class="outer-fake"><div class="card"><table><tr><th>A</th><th>B</th><th>C</th><th>D</th></tr></table></div></div></body></html>',
            encoding="utf-8",
        )
        r5 = self._run_auditor(trav_html)
        self.assertEqual(r5.returncode, 1)
        self.assertIn("[TABLE_WRAP]", r5.stdout)

    def test_v92_mount_prefix_honesty_self_badge_brain_and_mock_arrays(self) -> None:
        mount_root = self.tmp_dir / "mounted_web"
        mount_root.mkdir()
        (mount_root / "app.css").write_text("body { font-size: 13px; }\n.bad { color: red !important; }", encoding="utf-8")
        (mount_root / "views.js").write_text(
            "function load(isDemo, r) {\n"
            "  let rows = [];\n"
            "  if (!rows.length && isDemo) { rows = [{a: 1}, {a: 2}]; }\n"
            "  return `brain:${r.id}`;\n"
            "}\n",
            encoding="utf-8",
        )
        (mount_root / "demo_snapshot.js").write_text("window.DEMO_SNAPSHOT = { rows: [{a: 1}, {a: 2}] };", encoding="utf-8")
        (mount_root / "clean.js").write_text("const clean = (s) => String(s).replace(/^brain:/, '');", encoding="utf-8")

        app_html = self.tmp_dir / "app.html"
        app_html.write_text(
            '<!DOCTYPE html><html lang="en"><body>'
            '<header class="top"><span class="va-pill">v9.1 Quiet</span></header>'
            '<link rel="stylesheet" href="/web/app.css">'
            '<script src="/web/views.js?v=1"></script>'
            '<script src="/web/demo_snapshot.js"></script>'
            '<script src="/web/clean.js"></script>'
            "</body></html>",
            encoding="utf-8",
        )
        res = self._run_auditor(app_html, "--mount-prefix", f"/web={mount_root}")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("[SELF_BADGE]", res.stdout)
        self.assertIn("[IMPORTANT]", res.stdout)
        self.assertIn("[INLINE_MOCK_DATA]", res.stdout)
        self.assertIn("[INTERNAL_ID]", res.stdout)
        self.assertNotIn("demo_snapshot.js", res.stdout)
        self.assertNotIn("clean.js", res.stdout)

        ok_html = self.tmp_dir / "showcase.html"
        ok_html.write_text(
            '<!DOCTYPE html><html lang="en"><body>'
            '<header class="top"><span>Quiet UI v9.2 Showcase</span></header>'
            '<script src="/web/clean.js"></script>'
            "</body></html>",
            encoding="utf-8",
        )
        res_ok = self._run_auditor(ok_html, "--allow-showcase-chrome", "--mount-prefix", f"/web={mount_root}")
        self.assertEqual(res_ok.returncode, 0, res_ok.stdout + res_ok.stderr)

    def test_v92_cdp_svg_collisions_and_truncation(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise
            self.skipTest("selenium not installed")

        bad_svg_html = self.tmp_dir / "bad_cdp.html"
        bad_svg_html.write_text(
            '<!DOCTYPE html><html lang="en"><head><style>'
            "body{font-size:14px;background:#fff} nav a{display:block;width:64px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}"
            "</style></head><body>"
            '<nav><a href="#x">inspect_visual_artifacts</a></nav>'
            '<svg viewBox="0 0 320 140" width="320" height="140" role="img" aria-label="Collision specimen">'
            '<line x1="20" y1="60" x2="300" y2="60" stroke="#666" stroke-width="1.5"/>'
            '<text x="80" y="64" font-size="12">Avg 1,871</text>'
            '<text x="40" y="120" font-size="12">11-19</text>'
            '<text x="58" y="120" font-size="12">11-19</text>'
            '<text x="150" y="120" font-size="12">Gemini 4 Argon (Pr</text>'
            "</svg></body></html>",
            encoding="utf-8",
        )
        res_bad = self._run_auditor(bad_svg_html, "--cdp")
        self.assertEqual(res_bad.returncode, 1, res_bad.stdout)
        self.assertIn("[SVG_LINE_COLLISION]", res_bad.stdout)
        self.assertIn("[SVG_TEXT_OVERLAP]", res_bad.stdout)
        self.assertIn("[LABEL_TRUNCATED]", res_bad.stdout)

        halo_ok_html = self.tmp_dir / "halo_cdp.html"
        halo_ok_html.write_text(
            '<!DOCTYPE html><html lang="en"><head><style>body{font-size:14px;background:#fff}</style></head><body>'
            '<svg viewBox="0 0 320 140" width="320" height="140" role="img" aria-label="Haloed specimen">'
            '<line x1="20" y1="60" x2="300" y2="60" stroke="#666" stroke-width="1.5"/>'
            '<text x="80" y="64" font-size="12" paint-order="stroke fill" stroke="#ffffff" stroke-width="4">Avg 1,871</text>'
            '<text x="30" y="120" font-size="12">11-18</text>'
            '<text x="105" y="120" font-size="12">11-19</text>'
            '<text x="175" y="120" font-size="12">Gemini 4 Argon (Pro)</text>'
            "</svg></body></html>",
            encoding="utf-8",
        )
        res_good = self._run_auditor(halo_ok_html, "--cdp")
        self.assertEqual(res_good.returncode, 0, res_good.stdout + res_good.stderr)

    def test_v92_edge_case_regressions(self) -> None:
        mount_root = self.tmp_dir / "reg_web"
        mount_root.mkdir()
        (mount_root / "clean.css").write_text(
            "/* Safe comment without !important or font-size: 9px */\n"
            ":root { --my-font-size: 9px; }\n"
            "body { font-size: 13px; }\n",
            encoding="utf-8",
        )
        (mount_root / "clean_branch.js").write_text(
            "if (isDemo) { load(); }\nconst COLS = [{a: 1}, {b: 2}];\n",
            encoding="utf-8",
        )
        (mount_root / "bad_branch.js").write_text(
            "function pick(isDemo) {\n  if (isDemo) return [{a: 1}, {b: 2}];\n}\n",
            encoding="utf-8",
        )
        (self.tmp_dir / "outside.js").write_text("const MOCK_ROWS = [{a: 1}, {a: 2}];\n", encoding="utf-8")

        clean_html = self.tmp_dir / "reg_clean.html"
        clean_html.write_text(
            '<!DOCTYPE html><html lang="en"><head>'
            '<link rel="stylesheet" href="/web/clean.css">'
            "</head><body>"
            '<header><img src="/web/logo.png" alt=""><input type="search" aria-label="Filter"><span>0 Quiet Alerts</span></header>'
            "<main><p>v9.1 Quiet prose in main does not trigger</p></main>"
            '<script src="/web/clean_branch.js"></script>'
            '<script src="/web/../outside.js"></script>'
            "</body></html>",
            encoding="utf-8",
        )
        res_clean = self._run_auditor(clean_html, "--web-root", str(self.tmp_dir), "--mount-prefix", f"/web={mount_root}")
        self.assertEqual(res_clean.returncode, 0, res_clean.stdout + res_clean.stderr)

        hdr_void_bad = self.tmp_dir / "reg_hdr_bad.html"
        hdr_void_bad.write_text(
            '<!DOCTYPE html><html lang="en"><body>'
            '<header><img src="/web/logo.png" alt=""><input type="text"><span>v9.1 Quiet</span></header>'
            "</body></html>",
            encoding="utf-8",
        )
        res_hdr = self._run_auditor(hdr_void_bad)
        self.assertEqual(res_hdr.returncode, 1, res_hdr.stdout)
        self.assertIn("[SELF_BADGE]", res_hdr.stdout)

        bad_ui_badge = self.tmp_dir / "reg_quiet_hyphen.html"
        bad_ui_badge.write_text(
            '<!DOCTYPE html><html lang="en"><body><header><span>Quiet-UI</span></header></body></html>',
            encoding="utf-8",
        )
        res_ui = self._run_auditor(bad_ui_badge)
        self.assertEqual(res_ui.returncode, 1, res_ui.stdout)
        self.assertIn("[SELF_BADGE]", res_ui.stdout)

        bad_branch_html = self.tmp_dir / "reg_bad_branch.html"
        bad_branch_html.write_text(
            '<!DOCTYPE html><html lang="en"><body><script src="/web/bad_branch.js"></script></body></html>',
            encoding="utf-8",
        )
        res_br = self._run_auditor(bad_branch_html, "--mount-prefix", f"/web={mount_root}")
        self.assertEqual(res_br.returncode, 1, res_br.stdout)
        self.assertIn("[INLINE_MOCK_DATA]", res_br.stdout)

    def test_v921_hidden_layer_chrome_self_badge_exclude_and_mount_scoping(self) -> None:
        early_hidden = self.tmp_dir / "bad_hidden.css"
        early_hidden.write_text(
            "@layer base, shell, utilities;\n@layer base { .hidden { display: none; } }\n@layer shell { .panel { display: flex; } }\n",
            encoding="utf-8",
        )
        r_hl1 = self._run_auditor(early_hidden)
        self.assertEqual(r_hl1.returncode, 1, r_hl1.stdout)
        self.assertIn("[HIDDEN_LAYER]", r_hl1.stdout)

        bad_order = self.tmp_dir / "bad_order.css"
        bad_order.write_text(
            "@layer utilities, views;\n@layer utilities { .hidden { display: none; } }\n",
            encoding="utf-8",
        )
        r_hl2 = self._run_auditor(bad_order)
        self.assertEqual(r_hl2.returncode, 1, r_hl2.stdout)
        self.assertIn("[HIDDEN_LAYER]", r_hl2.stdout)

        good_hidden = self.tmp_dir / "good_hidden.css"
        good_hidden.write_text(
            "@layer reset, base, shell, utilities;\n"
            "@layer base { .bg { background: url(https://example.com/a.png); } }\n"
            "@layer shell { .qe-specimen[hidden] { display: none; } }\n"
            '@layer utilities { .hidden, [hidden]:not([hidden="until-found"]) { display: none; } }\n',
            encoding="utf-8",
        )
        r_hl_ok = self._run_auditor(good_hidden)
        self.assertEqual(r_hl_ok.returncode, 0, r_hl_ok.stdout + r_hl_ok.stderr)

        web_dir = self.tmp_dir / "web"
        v9_dir = web_dir / "v9"
        v9_dir.mkdir(parents=True)
        (web_dir / "demo_data.js").write_text("const cid = `brain:${x}`;", encoding="utf-8")
        (v9_dir / "styles.css").write_text(
            "@layer base, utilities;\n@layer utilities { .hidden, [hidden] { display: none; } }\n",
            encoding="utf-8",
        )
        (v9_dir / "app.js").write_text("const ok = 1;", encoding="utf-8")
        (v9_dir / "index.html").write_text(
            '<!DOCTYPE html><html lang="en"><head><link rel="stylesheet" href="/web/v9/styles.css"></head><body>'
            '<header class="va-shell-topbar"><span class="va-pill">quiet-ui-skills</span></header>'
            '<main><span class="va-pill">quiet-ui-skills-28</span><span class="v9-card-kicker">Quiet UI Specimen</span></main>'
            '<script src="/web/v9/app.js"></script><script src="/web/demo_data.js"></script>'
            "</body></html>",
            encoding="utf-8",
        )
        r_sub = self._run_auditor(v9_dir, "--mount-prefix", f"/web={web_dir}")
        self.assertEqual(r_sub.returncode, 0, r_sub.stdout + r_sub.stderr)
        sys.path.insert(0, str(self.tmp_dir))
        from audit_static_rules import compute_mount_scopes  # noqa: E402
        self.assertEqual(compute_mount_scopes("http://127.0.0.1:8765/web/v9/overview", {"/web": web_dir}), {"/web": v9_dir.resolve()})

        r_ext = self._run_auditor(v9_dir, "--mount-prefix", f"/web={web_dir}", "--audit-mounted-external")
        self.assertEqual(r_ext.returncode, 1, r_ext.stdout)
        self.assertIn("[INTERNAL_ID]", r_ext.stdout)

        r_exc = self._run_auditor(v9_dir, "--mount-prefix", f"/web={web_dir}", "--audit-mounted-external", "--exclude", "demo_data.js")
        self.assertEqual(r_exc.returncode, 0, r_exc.stdout + r_exc.stderr)

        miss_html = v9_dir / "missing.html"
        miss_html.write_text('<!DOCTYPE html><html lang="en"><body><script src="/web/missing.js"></script></body></html>', encoding="utf-8")
        r_miss = self._run_auditor(miss_html, "--mount-prefix", f"/web={web_dir}")
        self.assertEqual(r_miss.returncode, 1, r_miss.stdout)
        self.assertIn("[MISSING_ASSET]", r_miss.stdout)

        hdr_badge = self.tmp_dir / "chrome_badge.html"
        hdr_badge.write_text('<!DOCTYPE html><html lang="en"><body><div class="va-shell-topbar"><span>v9.2 Quiet</span></div></body></html>', encoding="utf-8")
        self.assertIn("[SELF_BADGE]", self._run_auditor(hdr_badge).stdout)
        opt_bad = self.tmp_dir / "opt_close_bad.html"
        opt_bad.write_text('<!DOCTYPE html><html lang="en"><body><header><ul><li>A<li>B</ul><p>v9.2 Quiet</header><main><p>Ok</p></main></body></html>', encoding="utf-8")
        self.assertIn("[SELF_BADGE]", self._run_auditor(opt_bad).stdout)
        opt_ok = self.tmp_dir / "opt_close_ok.html"
        opt_ok.write_text('<!DOCTYPE html><html lang="en"><body><header><p>Safe</header><main><p>v9.2 Quiet</p></main></body></html>', encoding="utf-8")
        self.assertEqual(self._run_auditor(opt_ok).returncode, 0)

    def test_v921_cdp_chrome_self_badge_and_slug_exemption(self) -> None:
        if os.environ.get("QUIET_SKIP_CDP") == "1":
            self.skipTest("QUIET_SKIP_CDP=1")
        try:
            import selenium  # noqa: F401
        except ImportError:
            if os.environ.get("QUIET_REQUIRE_CDP") == "1":
                raise
            self.skipTest("selenium not installed")

        ok_slug = self.tmp_dir / "cdp_slug_ok.html"
        ok_slug.write_text(
            '<!DOCTYPE html><html lang="en"><head><style>body{font-size:14px;background:#fff}</style></head><body>'
            '<header class="va-shell-topbar"><span class="va-pill">quiet-ui-skills</span></header>'
            '<main><span class="va-pill">quiet-ui-skills-28</span><span class="v9-card-kicker">Quiet UI Ref</span></main>'
            "</body></html>",
            encoding="utf-8",
        )
        self.assertEqual(self._run_auditor(ok_slug, "--cdp").returncode, 0)

        bad_chrome = self.tmp_dir / "cdp_chrome_bad.html"
        bad_chrome.write_text(
            '<!DOCTYPE html><html lang="en"><head><style>body{font-size:14px;background:#fff}</style></head><body>'
            '<header class="va-shell-topbar"><span>v9.2 Quiet</span></header>'
            "</body></html>",
            encoding="utf-8",
        )
        r_cdp_bad = self._run_auditor(bad_chrome, "--cdp")
        self.assertEqual(r_cdp_bad.returncode, 1, r_cdp_bad.stdout)
        self.assertIn("[SELF_BADGE]", r_cdp_bad.stdout)


if __name__ == "__main__":
    unittest.main()
