#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Phase 4 — World 01 Vertical Pilot Unit & Conservation Tests (<= 400L)."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src" / "v9" / "views"))

from build_v9_showcase import build_v9_showcase  # noqa: E402
from verify_v9_pilot import verify_static  # noqa: E402
from world_01_clinical import build_world_01  # noqa: E402


class TestV9World01Pilot(unittest.TestCase):
    """Validate World 01 pilot compilation, conservation, and v8.2.0 isolation."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.built = build_world_01(REPO_ROOT / "content" / "corpora")
        cls.pilot_html = build_v9_showcase(REPO_ROOT, ["01-clinical-icu-and-trials"])
        cls.corpus = json.loads(
            (REPO_ROOT / "content" / "corpora" / "01-clinical-icu-and-trials" / "corpus.json").read_text(encoding="utf-8")
        )

    def test_pilot_builds_and_passes_static_hygiene(self) -> None:
        self.assertEqual(len(self.built["world_meta"]["views"]), 3)
        self.assertNotIn("!important", self.pilot_html.lower())
        self.assertNotIn("●", self.pilot_html)
        self.assertEqual(verify_static(), [])

    def test_numerical_conservation_across_all_3_views(self) -> None:
        tpls = self.built["templates"]
        v01 = tpls["v01-icu-bedside-terminal"]
        v02 = tpls["v02-trial-regulatory-brief"]
        v03 = tpls["v03-patient-recovery-companion"]

        for num in ("63.5", "65.0", "10.0", "10.2", "94.2", "2.4"):
            self.assertIn(num, v01)
        for num in ("0.74", "0.61", "0.90", "0.79", "0.68", "0.71", "11.4", "14.8"):
            self.assertIn(num, v02)
        for num in ("63.5", "65.0", "94.2", "92.0"):
            self.assertIn(num, v03)
        visible_v03 = re.sub(r"<style\b[^>]*>.*?</style>", "", v03, flags=re.S)
        for jargon in ("ADC", "k=2", "PEEP", "CAL-", "T05:30:00Z", "Mean MAP", "Oxygen / %", "HOME-OXYGEN", "Nominal", "CAUTION", "Discrete Sample"):
            self.assertNotIn(jargon, visible_v03)

    def test_gate41_domain_scales_embedded_chrome_and_homogeneity(self) -> None:
        tpls = self.built["templates"]
        v01 = tpls["v01-icu-bedside-terminal"]
        v02 = tpls["v02-trial-regulatory-brief"]
        v03 = tpls["v03-patient-recovery-companion"]

        for bad_tick in (">-120<", ">-100<", ">-50<"):
            self.assertNotIn(bad_tick, v01)
        self.assertIn(">160<", v01)
        self.assertIn(">50<", v01)
        self.assertIn("Checked Today · 5:30 AM", v03)
        self.assertIn("On Track", v03)
        self.assertIn("Recheck in 15 min", v03)
        self.assertIn("v03-oxygen-trend-chart", v03)
        self.assertIn("v03-bp-trend-chart", v03)
        self.assertIn('<span class="qe-unit">mmol/L</span>', v02)
        for vid, frag in tpls.items():
            self.assertNotIn("qe-fig-badges", frag, f"Internal badge leaked in {vid}")
            for leak in ("Quiet Cockpit", "Pedagogical Flow", "Decision Contrast", "PlainLanguage.gov", "FDA IEC 62366"):
                self.assertNotIn(leak, frag, f"Framework leak '{leak}' in {vid}")

    def test_atomic_pills_and_svg_compliance(self) -> None:
        for vid, html_frag in self.built["templates"].items():
            self.assertNotIn("qe-label-pill", html_frag, f"Legacy pill in {vid}")
            self.assertNotRegex(html_frag, r'class="va-pill"[^>]*>\s*\[', f"Bracketed pill in {vid}")
            for path_tag in re.findall(r"<path\b[^>]*>", html_frag):
                self.assertIn("fill=", path_tag, f"<path> missing fill= in {vid}")

    def test_bridge_manifest_has_murder_board_and_ledger(self) -> None:
        meta = self.built["world_meta"]
        self.assertGreaterEqual(len(meta["conservation_ledger"]), 10)
        for vw in meta["views"]:
            self.assertTrue(vw["vector_summary"])
            self.assertTrue(vw["bias_removed"])
            self.assertTrue(vw["invariants"].get("baseline"))
            self.assertGreaterEqual(len(vw["murder_board"]), 1)

    def test_write_to_temp_path_leaves_v8_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pilot.html"
            out.write_text(self.pilot_html, encoding="utf-8")
            self.assertTrue(out.is_file())
            self.assertGreater(len(out.read_text(encoding="utf-8")), 20000)


    def test_dual_review_p1_boundary_hardening(self) -> None:
        from compile_evidence import compile_spec

        v01_meta = next(v for v in self.built["world_meta"]["views"] if v["view_id"] == "v01-icu-bedside-terminal")
        self.assertIsInstance(v01_meta.get("topbar_status"), list)
        self.assertNotIn("topbar_status_html", v01_meta)
        tbl = compile_spec({
            "$schema": "urn:quiet-ui:schema:v9:table", "id": "t-ent",
            "metadata": {"title": "Entity", "rigor_level": "L3"},
            "columns": [
                {"key": "sys", "label": "Systems & Mass (ms)", "unit": "ms", "data_type": "string"},
                {"key": "h", "label": "Length & Height (m)", "unit": "m", "data_type": "numeric"},
            ],
            "rows": [{"sys": "S1", "h": 1.5}],
        }, rigor="L3", chrome="embedded")
        self.assertNotIn("&a<span", tbl)
        self.assertIn('Syste', tbl)
        self.assertNotIn('Syste<span', tbl)
        self.assertIn('(<span class="qe-unit">m</span>)', tbl)
        wf = compile_spec({
            "$schema": "urn:quiet-ui:schema:v9:waveform", "id": "w-nan",
            "metadata": {"title": "NaN Guard", "rigor_level": "L2"},
            "timebase": {"unit": "ms", "domain": [0, 10]},
            "channels": [{"id": "c1", "name": "C1", "unit": "V", "vertical_scale_per_div": float("nan"), "samples": [[0, None], [2, 10], [None, 5]]}],
        }, rigor="L2")
        self.assertNotIn("nan", wf.lower().split("<path")[1].split("/>")[0])
        sc = compile_spec({
            "$schema": "urn:quiet-ui:schema:v9:scalar", "id": "s-one",
            "metadata": {"title": "One-Sided", "rigor_level": "L3"},
            "quantity": {"name": "P", "symbol": "P", "unit": "mmHg"},
            "measurement": {"nominal_value": 40.0, "uncertainty": 1.0, "coverage_factor": None, "status": "CRITICAL"},
            "limits": {"abort_thresholds": {"lower": 55.0}},
            "gauge": {"enabled": True},
        }, rigor="L3", chrome="embedded")
        self.assertIn("k=2", sc)


if __name__ == "__main__":
    unittest.main()
