#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.4.0 verification: .quiet-ui.md contracts, forms/zero-states, strict drift, Specimen 44, and CJK math."""

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
COMPILERS_DIR = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
BUNDLE_CSS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.css"
BUNDLE_JS = REPO_ROOT / "skills" / "quiet-evidence" / "assets" / "quiet-evidence-bundle.js"
FORMS_CSS = REPO_ROOT / "src" / "css" / "14-forms-and-states.css"
BENCH_HTML = REPO_ROOT / "docs" / "bench" / "evidence-bench.html"


class TestV940ContextFormsDrift(unittest.TestCase):
    """Verify persistent .quiet-ui.md context loading, 5 UX/drift gates, Specimen 44, and CJK math."""

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
            cwd=self.tmp_dir,
            capture_output=True,
            text=True,
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

    def test_context_init_autodiscovery_and_mount_merge(self) -> None:
        proj = self.tmp_dir / "proj"
        sub_web = proj / "a" / "b" / "web"
        static_dir = proj / "static"
        cli_dir = proj / "cli_static"
        sub_web.mkdir(parents=True)
        static_dir.mkdir(parents=True)
        cli_dir.mkdir(parents=True)

        ctx_path = proj / ".quiet-ui.md"
        r_init = self._run_auditor("--init-context", str(ctx_path))
        self.assertEqual(r_init.returncode, 0, r_init.stdout + r_init.stderr)
        self.assertIn("[INIT]", r_init.stdout)
        self.assertTrue(ctx_path.is_file())

        r_again = self._run_auditor("--init-context", str(ctx_path))
        self.assertEqual(r_again.returncode, 0)
        self.assertIn("[EXISTS]", r_again.stdout)

        (static_dir / "app.css").write_text("@layer shell { .box { color: var(--text-primary); } }", encoding="utf-8")
        (static_dir / "bad.min.js").write_text("const brokenLegacyWidget = [1,2,3];", encoding="utf-8")
        (cli_dir / "override.css").write_text("@layer shell { .cli-ok { color: var(--accent-primary); } }", encoding="utf-8")
        ctx_path.write_text(
            "# .quiet-ui.md\n"
            "- **Project Mode**: Brownfield Retrofit\n"
            "- **Primary Medium**: M3\n"
            "- **Mount Prefixes**: `/static=./static`\n"
            "- **Excludes**: `*.min.js`\n"
            "- **Strict Drift**: false\n",
            encoding="utf-8",
        )
        html_p = sub_web / "index.html"
        html_p.write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Ctx</title>"
            "<link rel='stylesheet' href='/static/app.css'>"
            "<script src='/static/bad.min.js'></script></head>"
            "<body><main><h1>Healthy Console</h1></main></body></html>",
            encoding="utf-8",
        )
        r_auto = self._run_auditor(str(html_p))
        self.assertEqual(r_auto.returncode, 0, r_auto.stdout + r_auto.stderr)

        (html_cli := sub_web / "cli_override.html").write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Override</title>"
            "<link rel='stylesheet' href='/static/override.css'></head>"
            "<body><main><h1>Override</h1></main></body></html>",
            encoding="utf-8",
        )
        r_override = self._run_auditor(str(html_cli), "--mount-prefix", f"/static={cli_dir}")
        self.assertEqual(r_override.returncode, 0, r_override.stdout + r_override.stderr)

        r_missing = self._run_auditor(str(html_p), "--context", str(proj / "missing.md"))
        self.assertEqual(r_missing.returncode, 1)
        self.assertIn("[MISSING_CONTEXT]", r_missing.stdout)

    def test_blocklist_forms_and_zero_state_static_gates(self) -> None:
        proj = self.tmp_dir / "ux"
        proj.mkdir()
        ctx_p = proj / ".quiet-ui.md"
        ctx_p.write_text(
            "# .quiet-ui.md\n## Deprecation Blocklist\n- selector: `#legacy-quota`\n- selector: `#`\n- copy: `legacy widget`\n",
            encoding="utf-8",
        )
        bad_p = proj / "bad_ux.html"
        bad_p.write_text(
            "<!DOCTYPE html><html lang='en'><body><main>"
            "<div id='legacy-quota'>Deprecated legacy widget box</div>"
            "<form><input type='text' placeholder='Only placeholder'></form>"
            "<div class='va-empty-state' data-kind='filtered'><p>0 matching rows</p></div>"
            "<script>const ns = 'http://www.w3.org/2000/svg'; const q = document.querySelector('#legacy-quota');</script>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_bad = self._run_auditor(str(bad_p), "--json")
        self.assertEqual(r_bad.returncode, 1)
        errs = json.loads(r_bad.stdout)["errors"]
        errs_s = "\n".join(errs)
        self.assertIn("[BLOCKLIST_RESURRECTION]", errs_s)
        self.assertIn("JS references blocklisted selector '#legacy-quota'", errs_s)
        self.assertIn("[UNLABELED_FORM_CONTROL]", errs_s)
        self.assertIn("[DEAD_END_ZERO_STATE]", errs_s)

        ok_p = proj / "good_ux.html"
        ok_p.write_text(
            "<!DOCTYPE html><html lang='en'><body><main>"
            "<pre><code>legacy widget #legacy-quota</code></pre>"
            "<form><input type='hidden' value='tok'>"
            "<label for='ms'>Ceiling</label><input id='ms' type='number'>"
            "<label>Note<textarea></textarea></label></form>"
            "<section class='va-empty-state' data-kind='filtered'>"
            "<p>0 rows</p><button type='button'>Clear filters</button></section>"
            "<script>// comment mentions #legacy-quota and legacy widget safely\nconst ns = 'http://www.w3.org/2000/svg';</script>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_ok = self._run_auditor(str(ok_p))
        self.assertEqual(r_ok.returncode, 0, r_ok.stdout + r_ok.stderr)

    def test_strict_drift_hex_inline_and_exemptions(self) -> None:
        proj = self.tmp_dir / "drift"
        proj.mkdir()
        (proj / "app.css").write_text(
            "@layer tokens { :root, [data-theme='dark'] { --bg-surface: #0f172a; color: #f8fafc; } }\n"
            "@layer legacy { .old-btn { color: #334155; } }\n"
            "@media print { body { color: #000000; } }\n"
            "@media (forced-colors: active) { .btn { border-color: #ffffff; } }\n"
            "@layer shell {\n"
            "  a:not([href='#112233'])\n  { color: var(--text-primary, #111827); }\n"
            "  .ok-exempt { background: #1e293b; /* token-exempt */ }\n"
            "  .bad-hex { color: #ff00aa; }\n"
            "  .bad-rgb {\n    box-shadow: 0 2px 6px RGB(12, 34, 56);\n  }\n"
            "}\n",
            encoding="utf-8",
        )
        (proj / "page.html").write_text(
            "<!DOCTYPE html><html lang='en'><body><main>"
            "<div style='display: none; --pct: 50%; border-color: var(--b, #cccccc)'>Hidden</div>"
            "<div style='padding: 12px; color: #ff00aa'>Drift</div>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r_off = self._run_auditor(str(proj))
        self.assertEqual(r_off.returncode, 0, r_off.stdout + r_off.stderr)

        r_on = self._run_auditor(str(proj), "--strict-drift", "--json")
        self.assertEqual(r_on.returncode, 1)
        errs = json.loads(r_on.stdout)["errors"]
        joined = "\n".join(errs)
        self.assertIn("[TOKEN_BYPASS_HEX]", joined)
        self.assertIn("#ff00aa", joined)
        self.assertIn("RGB(", joined)
        self.assertNotIn("#112233", joined)
        self.assertNotIn("#0f172a", joined)
        self.assertNotIn("#334155", joined)
        self.assertNotIn("#000000", joined)
        self.assertNotIn("#111827", joined)
        self.assertNotIn("#1e293b", joined)
        self.assertIn("[INLINE_STYLE_SPRAWL]", joined)
        self.assertEqual(sum(1 for e in errs if "[INLINE_STYLE_SPRAWL]" in e), 1)

    def test_specimen_44_and_forms_css_bundle(self) -> None:
        raw_forms = FORMS_CSS.read_text("utf-8")
        self.assertNotIn("!important", raw_forms)
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,8}\b", raw_forms), "14-forms-and-states.css must use pure CSS tokens")
        css = BUNDLE_CSS.read_text("utf-8")
        for sel in (".va-form-grid", ".va-field", ".va-input", ".va-field-error", ".va-gate-reason", ".va-empty-state", ".va-stale-retained", ".va-undo-toast"):
            self.assertIn(sel, css, f"Missing {sel} in bundled CSS")
        bench = BENCH_HTML.read_text("utf-8")
        self.assertIn('id="qe-forms-zero-states"', bench)
        self.assertIn("Validated Threshold Form, 4-Way Zero-States", bench)

    def test_cjk_wide_script_python_and_js_math(self) -> None:
        if str(COMPILERS_DIR) not in sys.path:
            sys.path.insert(0, str(COMPILERS_DIR))
        from compilers.svg_labels import svg_knockout_label, visual_char_units  # noqa: E402

        self.assertAlmostEqual(visual_char_units("ABC"), 3.0)
        self.assertAlmostEqual(visual_char_units("e\u0301"), 1.0)
        self.assertGreater(visual_char_units("日本語テスト"), 9.5)
        w_ascii = float(re.search(r'width="([^"]+)"', svg_knockout_label(40, 40, "ABCDEF")).group(1))
        w_cjk = float(re.search(r'width="([^"]+)"', svg_knockout_label(40, 40, "日本語テスト")).group(1))
        self.assertGreater(w_cjk, w_ascii * 1.45)

        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        probe = (
            "const fs=require('fs'), vm=require('vm');\n"
            "const ctx={window:{},globalThis:{},document:null,performance:{now:()=>0},setTimeout,clearTimeout,console};\n"
            "ctx.window=ctx; ctx.globalThis=ctx; vm.createContext(ctx);\n"
            f"vm.runInContext(fs.readFileSync({str(BUNDLE_JS)!r}, 'utf8'), ctx);\n"
            "const L=ctx.window.QuietSvgLayout;\n"
            "const cjk=L.visualUnits('日本語テスト'), comb=L.visualUnits('e\\u0301');\n"
            "if(Math.abs(comb-1)>0.01 || cjk<=9.5) throw new Error('bad visualUnits:'+cjk+'/'+comb);\n"
            "const gAsc=L.measureCategoryGutter(['ABCDEF'], {mono:false});\n"
            "const gCjk=L.measureCategoryGutter(['\U00020000\U00020001\U00020002\U00020003長時間監視パネル'], {mono:false, maxChars:12});\n"
            "const wrapped=L.wrapLabelLines('日本語テスト長時間監視パネル', 10, 2);\n"
            "const line2=L.wrapLabelLines('aa \U00020000\U00020001\U00020002\U00020003\U00020004\U00020005', 10, 2);\n"
            "console.log(JSON.stringify({gutterAsc:gAsc.gutterPx, gutterCjk:gCjk.gutterPx, lines:wrapped.length, ok:wrapped.every(l=>l.length>0), l2Max:Math.max(...line2.map(L.visualUnits))}));\n"
        )
        res = subprocess.run([node, "-e", probe], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Node probe failed:\n{res.stderr}\n{res.stdout}")
        out = json.loads(res.stdout.strip())
        self.assertTrue(out["ok"])
        self.assertGreaterEqual(out["lines"], 2)
        self.assertLessEqual(out["l2Max"], 10.5)
        self.assertGreater(out["gutterCjk"], out["gutterAsc"])

    def test_cdp_v940_blocklist_forms_and_empty_state(self) -> None:
        self._require_cdp()
        proj = self.tmp_dir / "cdp_ux"
        proj.mkdir()
        (proj / ".quiet-ui.md").write_text(
            "## Deprecation Blocklist\n- selector: `#stale-old-nav`\n- copy: `retired panel`\n",
            encoding="utf-8",
        )
        p = proj / "bad_dom.html"
        p.write_text(
            "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>CDP UX</title></head>"
            "<body><main><h1>DOM Probe</h1><input type='text'>"
            "<div class='va-empty-state' data-kind='filtered'><p>None</p></div>"
            "<script>const n=document.createElement('div');n.id='stale-old-nav';n.textContent='retired panel';document.querySelector('main').appendChild(n);</script>"
            "</main></body></html>",
            encoding="utf-8",
        )
        r = self._run_auditor(str(p), "--cdp", "--json")
        self.assertEqual(r.returncode, 1)
        joined = "\n".join(json.loads(r.stdout)["errors"])
        for code in ("[UNLABELED_FORM_CONTROL]", "[DEAD_END_ZERO_STATE]", "[BLOCKLIST_RESURRECTION]"):
            self.assertIn(code, joined)


if __name__ == "__main__":
    unittest.main()
