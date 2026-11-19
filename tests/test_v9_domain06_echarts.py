#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v9.0 Gate 5.4 — Unit tests for Domain 06 Smart Home, Photo Assets & Apache ECharts."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QE_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
if str(QE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(QE_SCRIPTS))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from compile_evidence import compile_spec  # noqa: E402
from compilers.echarts_adapter import build_echarts_payload, render_ecosystem_drawer  # noqa: E402
from customizations.scripts.build_showcase import build_showcase  # noqa: E402
from scripts.build_v9_showcase import build_v9_showcase  # noqa: E402


class TestDomain06AndECharts(unittest.TestCase):
    """Verify Gate 5.4 Domain 06 compilation, 8 EXIF-free backplates, starters & ECharts adapter."""

    def test_vendor_echarts_and_adapter_payload(self) -> None:
        vendor_js = REPO_ROOT / "docs" / "assets" / "vendor" / "echarts.min.js"
        self.assertTrue(vendor_js.is_file())
        self.assertGreater(vendor_js.stat().st_size, 500_000)

        plot_spec = json.loads(
            (REPO_ROOT / "content" / "corpora" / "06-smart-home-and-energy" / "evidence" / "v18_whole_home_energy_plot.json").read_text(encoding="utf-8")
        )
        payload = build_echarts_payload(plot_spec, rigor="L2", medium="m3")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["kind"], "cartesian")
        self.assertEqual(len(payload["series"]), 3)
        self.assertEqual(payload["series"][0]["data"][7][1], 5.1)
        self.assertEqual(payload["series"][2]["data"][7][1], -1.68)

        compiled_bench = compile_spec(plot_spec, chrome="bench", include_spec_drawer=True)
        self.assertIn("data-quiet-echarts=", compiled_bench)
        self.assertIn('class="qe-echarts-host"', compiled_bench)
        self.assertIn("Inspect Ecosystem Config (ECharts · Plotly · Matplotlib)", compiled_bench)
        self.assertIn("Plotly", render_ecosystem_drawer(plot_spec))
        self.assertIn("Matplotlib", render_ecosystem_drawer(plot_spec))

    def test_domain_06_templates_and_all_8_exif_free_photos(self) -> None:
        html = build_v9_showcase(REPO_ROOT, ["05-physical-systems-auto-and-aero", "06-smart-home-and-energy"])
        v17 = re.search(r'<template id="tpl-view-v17-picture-frame-home-kiosk">(.*?)</template>', html, flags=re.S)
        v18 = re.search(r'<template id="tpl-view-v18-home-assistant-companion-console">(.*?)</template>', html, flags=re.S)
        self.assertIsNotNone(v17)
        self.assertIsNotNone(v18)
        for tok in ("opt_frame_art.jpg", "opt_frame_landscape.jpg", "5.10 kW", "3.42 kW", "-1.68 kW", "84%", "21.5 °C"):
            self.assertIn(tok, v17.group(1))
        self.assertNotIn("v15-reticle-layer", v17.group(1))
        for tok in ("PANEL-MAIN-200A", "LOCK-FRONT-01", "GARAGE-BAY-01", "LEAK-LOOP-06", "5.10 kW", "-1.68 kW", "data-quiet-echarts="):
            self.assertIn(tok, v18.group(1))
        for jpg_name in (
            "as08-14-2383.jpg", "opt_hud_daylight_rwy.jpg", "opt_hud_night_rwy.jpg",
            "opt_glass_day_hwy.jpg", "opt_glass_dusk_hwy.jpg", "opt_glass_night_hwy.jpg",
            "opt_frame_art.jpg", "opt_frame_landscape.jpg",
        ):
            p = REPO_ROOT / "docs" / "assets" / jpg_name
            self.assertTrue(p.is_file(), f"Missing image {jpg_name}")
            self.assertLessEqual(p.stat().st_size, 185 * 1024)
            self.assertNotIn(b"Exif\x00\x00", p.read_bytes())

    def test_starter_filtering_18_vs_14_views(self) -> None:
        unified = (REPO_ROOT / "docs" / "v9" / "quiet-ui-v9-showcase.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            src_p = Path(tmp) / "unified.html"
            src_p.write_text(unified, encoding="utf-8")
            p_out = Path(tmp) / "p.html"
            b_out = Path(tmp) / "b.html"
            build_showcase(REPO_ROOT / "customizations" / "personal-starter", src_p, p_out, bundle=False)
            build_showcase(REPO_ROOT / "customizations" / "brand-starter", src_p, b_out, bundle=False)
            p_txt, b_txt = p_out.read_text(encoding="utf-8"), b_out.read_text(encoding="utf-8")
            self.assertIn("tpl-view-v17-picture-frame-home-kiosk", p_txt)
            self.assertIn("tpl-view-v18-home-assistant-companion-console", p_txt)
            self.assertNotIn("tpl-view-v17-picture-frame-home-kiosk", b_txt)
            self.assertNotIn("tpl-view-v18-home-assistant-companion-console", b_txt)

    def test_logarithmic_waterfall_and_ast_safety(self) -> None:
        plots = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m4_plots.json").read_text(encoding="utf-8"))
        allan = next(s for s in plots if "allan" in s["id"])
        a_pay = build_echarts_payload(allan, rigor="L3", medium="m2")
        self.assertIsNotNone(a_pay)
        self.assertTrue(a_pay["x"]["log"])
        self.assertTrue(a_pay["y"]["log"])
        self.assertGreaterEqual(len(a_pay["series"]), 2)
        wf = next(s for s in plots if s.get("plot_kind") == "waterfall")
        w_pay = build_echarts_payload(wf, rigor="L2", medium="m2")
        self.assertEqual(w_pay["bases"][-1], 0.0)
        evil = {
            "$schema": "urn:quiet-ui:schema:v9:plot", "plot_kind": "cartesian", "id": "dos",
            "axes": {"x_axis": {"domain": [0, 1]}, "y_axis": {"domain": [0, 1]}},
            "series": [{"id": "bad", "epistemic_type": "analytical_model", "equation": "9^(9^9)"}],
        }
        self.assertIsNone(build_echarts_payload(evil))


if __name__ == "__main__":
    unittest.main()
