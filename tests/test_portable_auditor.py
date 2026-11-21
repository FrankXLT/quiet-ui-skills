#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isolated portability tests for skills/quiet-ui/scripts/audit_quiet_html.py."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDITOR_SRC = REPO_ROOT / "skills" / "quiet-ui" / "scripts" / "audit_quiet_html.py"
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


if __name__ == "__main__":
    unittest.main()
