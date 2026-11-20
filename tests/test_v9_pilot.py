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
        self.assertIn(">120<", v01)
        self.assertIn(">40<", v01)
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
            blob = " ".join([
                vw["vector_summary"], vw["bias_removed"], vw["bias_risk"], vw["bias_replacement"], vw["actionable_disposition"],
                *vw["invariants"].values(),
                *(f"{m['rubric']} {m['finding']} {m['verdict']}" for m in vw["murder_board"]),
            ])
            for leak in (".json", "_row_status", "QUIET-BRIDGE", "Murder-Board", "Scrubbed"):
                self.assertNotIn(leak, blob, f"Jargon '{leak}' leaked in {vw['view_id']}")

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


class TestV9AllWorldsShowcase(unittest.TestCase):
    """Validate Worlds 02-05 build, numerical conservation, M5/M6/M7 physics, and starters."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.all_world_ids = [
            "01-clinical-icu-and-trials",
            "02-cloud-cyber-and-ai-ops",
            "03-industrial-grid-and-manufacturing",
            "04-civic-finance-and-stem-learning",
            "05-physical-systems-auto-and-aero",
        ]
        cls.unified_html = build_v9_showcase(REPO_ROOT, cls.all_world_ids)

    def test_unified_5_world_manifest_and_3_mode_chrome(self) -> None:
        m = re.search(r'<script[^>]*id="va-v9-manifest"[^>]*>(.*?)</script>', self.unified_html, flags=re.S)
        self.assertIsNotNone(m)
        manifest = json.loads(m.group(1))
        self.assertEqual(len(manifest["worlds"]), 5)
        self.assertEqual(sum(len(w["views"]) for w in manifest["worlds"]), 19)
        for world in manifest["worlds"]:
            self.assertTrue(world.get("conservation_ledger"), f"Missing conservation ledger for {world['world_id']}")
            for vw in world["views"]:
                for field in ("bias_removed", "bias_risk", "bias_replacement", "actionable_disposition"):
                    self.assertTrue(str(vw.get(field, "")).strip(), f"Blank {field} in {vw['view_id']}")
                inv = vw.get("invariants", {})
                for ikey in ("baseline", "provenance", "margin", "disposition"):
                    self.assertTrue(str(inv.get(ikey, "")).strip(), f"Blank invariant {ikey} in {vw['view_id']}")
                mb = vw.get("murder_board", [])
                self.assertTrue(mb and all(re.search(r"[A-Za-z]{3,}", x.get("rubric", "")) and x.get("finding") and x.get("verdict") for x in mb), f"Incomplete murder_board in {vw['view_id']}: {mb}")
                blob = " ".join([vw["vector_summary"], vw["bias_removed"], vw["bias_risk"], vw["bias_replacement"], vw["actionable_disposition"], *inv.values(), *(f"{m['rubric']} {m['finding']}" for m in mb)])
                for leak in (".json", "_row_status", "QUIET-BRIDGE", "Murder-Board", "Scrubbed", "( clear)", "(clear)"):
                    self.assertNotIn(leak, blob, f"Jargon '{leak}' in {vw['view_id']}")
                self.assertNotRegex(blob, r"\bT[123]\b", f"Raw tempo code in {vw['view_id']}")
                self.assertNotRegex(blob, r"\bv\d{2}-[a-z0-9]+-", f"Raw view slug in {vw['view_id']}")
                self.assertNotRegex(vw["title"], r"^V\d{2}:", f"Prefix leak in {vw['view_id']}")
            ledger_txt = " ".join(f"{r['metric_id']} {r['views']}" for r in world["conservation_ledger"])
            self.assertNotRegex(ledger_txt, r"\bv\d{2}-[a-z0-9]+-", f"Raw view slug in ledger for {world['world_id']}")
        for must_id in ('id="va-tab-examples"', 'id="va-tab-components"', 'id="va-domain-select"', 'data-sheet-theme="white"', 'data-sheet-theme="paper"', 'data-sheet-theme="dark-paper"', 'data-sheet-theme="dark"'):
            self.assertIn(must_id, self.unified_html)
        for gone in ('id="va-tab-worlds"', 'id="va-tab-bench"', 'id="va-tab-atlas"', 'va-sheet-toggle-btn', 'va-world-select', 'diagrams.html', 'font-awesome', 'cdnjs.cloudflare.com', 'fa-solid'):
            self.assertNotIn(gone, self.unified_html)
        self.assertIn('aria-selected="true"', self.unified_html)
        self.assertNotIn("!important", self.unified_html.lower())
        self.assertNotIn("●", self.unified_html)

    def test_worlds_02_to_05_conservation_and_zero_leakage(self) -> None:
        for num in ("420.0", "16.8", "0x8003B104", "0.050", "23.6", "59.985", "78.4", "1.64", "26.9", "179.3", "25.1", "2.40", "42.8", "0.35", "0x18FEF100"):
            self.assertIn(num, self.unified_html, f"Missing conserved metric {num}")
        self.assertIn("V<sub>0</sub>", self.unified_html)
        self.assertIn("f<sub>obs</sub>", self.unified_html)
        tpl_body = "".join(re.findall(r'<template\s+id="tpl-view-[^"]*">(.*?)</template>', self.unified_html, flags=re.S))
        for leak in ("Quiet Cockpit", "Pedagogical Flow", "Decision Contrast", "EXPECTED TICK", "FROSTED HUD", "CREASE-AWARE", "T1 GATE", "STROKE-ONLY PHOSPHOR", "WCAG AAA", "10-FT WALL DISPLAY", "V04:", "V05:", "V06:"):
            self.assertNotIn(leak, tpl_body, f"Taxonomy/meta string leaked into stage template: {leak}")
        self.assertNotRegex(tpl_body, r"\bV\d{2}:", "Card title prefix VXX: leaked into stage template")

    def test_compiler_math_negative_edge_and_standalone_themes(self) -> None:
        from compile_evidence import compile_spec
        from compilers.tokens_and_scales import format_math_svg
        svg_txt = format_math_svg("tau_1 + mu_0 + p_hat_2", sub_size=9.5)
        self.assertIn("τ", svg_txt)
        self.assertIn("μ", svg_txt)
        self.assertIn("p̂", svg_txt)
        self.assertIn('font-size="9.5"', svg_txt)

        deg_gauge = {
            "$schema": "urn:quiet-ui:schema:v9:scalar", "id": "deg-g",
            "metadata": {"title": "Inverted Gauge", "rigor_level": "L2"},
            "quantity": {"symbol": "T", "unit": "°C"},
            "measurement": {"nominal_value": -12.0},
            "limits": {"nominal_target": -10.0, "warning_thresholds": {"lower": -20.0, "upper": 5.0}, "tolerance_band": [-5.0, -1.0]},
            "gauge": {"min_scale": 10.0, "max_scale": 10.0},
            "status_annunciator": {"state": "NOMINAL"},
        }
        g_out = compile_spec(deg_gauge, rigor="L2")
        self.assertIn("[-5, -1]", g_out)
        self.assertNotIn("+-", g_out)

        neg_wf = {
            "$schema": "urn:quiet-ui:schema:v9:plot", "plot_kind": "waterfall", "id": "neg-wf",
            "metadata": {"title": "Deficit Bridge", "rigor_level": "L2"},
            "axes": {"y_axis": {"unit": "M", "quantity_calculus": "Balance / M"}},
            "steps": [{"label": "Open", "value": -12.0, "kind": "start"}, {"label": "Cut", "value": 4.0, "kind": "delta"}, {"label": "Close", "value": -8.0, "kind": "total"}],
        }
        wf_out = compile_spec(neg_wf)
        self.assertIn("-12.0", wf_out)
        self.assertIn('clipPath', compile_spec({"$schema": "urn:quiet-ui:schema:v9:plot", "id": "clip-test", "metadata": {"title": "Clip"}, "series": [{"id": "s1", "epistemic_type": "analytical_model", "equation": "2*x"}], "axes": {"x_axis": {"domain": [0, 5]}, "y_axis": {"domain": [0, 5]}}}))
        paper_doc = compile_spec(deg_gauge, theme="paper", standalone=True)
        self.assertIn('data-theme="paper"', paper_doc)

    def test_m5_m6_m7_and_customization_filtering(self) -> None:
        v15_m = re.search(r'<template id="tpl-view-v15-collimated-flight-hud">(.*?)</template>', self.unified_html, flags=re.S)
        v16_m = re.search(r'<template id="tpl-view-v16-transparent-window-overlay">(.*?)</template>', self.unified_html, flags=re.S)
        self.assertIsNotNone(v15_m)
        self.assertIsNotNone(v16_m)
        v15_html, v16_html = v15_m.group(1), v16_m.group(1)
        for tok in ("v15-hud-stage", "v9-opt-photo", "assets/as08-14-2383.jpg", "assets/opt_hud_daylight_rwy.jpg", "assets/opt_hud_night_rwy.jpg", "v15-reticle-layer", "084°", "138", "1,180", "640 FT AGL · 3.0° GS", "VS -650 FPM", "PROP BTE 42.8% · IMEP 14.0 BAR", "Night ILS", "Orbital Limb", 'y="624"', 'y1="360"'):
            self.assertIn(tok, v15_html)
        for bad in ("v15-scene-svg", "v15-earthrise-img", "BORESIGHT", "NAV/PROPULSION HUD", "dual stroke halo", "v9-chip", "Night NVG"):
            self.assertNotIn(bad, v15_html)
        for tok in ("v16-glass-viewport", "v9-opt-photo", "assets/opt_glass_day_hwy.jpg", "assets/opt_glass_dusk_hwy.jpg", "assets/opt_glass_night_hwy.jpg", "18.4", "kt SOG", "HOLD &lt;= 18 kt", "Channel Range Marker · 1.2 nm to Berth", "42.8% BTE", "HDG 084°T · Depth 14.2 m", "STBD DRIVE DERATE", "MCU Thermal Limit (85 °C)", "Hold &lt;= 18 kt · Inspect Aft J1939 Drop at Berth"):
            self.assertIn(tok, v16_html)
        for bad in ("v16-scene-svg", "v16-corridor-svg", "v16-road-gap-badge", "0x18FEF100", "Offset: 0x", "SCRIM:", "NO FLASH", ">= 7.0:1", "preserves", "120 Ω", "v9-chip", "45 mph", "E-Bound Highway", "DRIVETRAIN DERATE"):
            self.assertNotIn(bad, v16_html)
        for jpg_name in ("as08-14-2383.jpg", "opt_hud_daylight_rwy.jpg", "opt_hud_night_rwy.jpg", "opt_glass_day_hwy.jpg", "opt_glass_dusk_hwy.jpg", "opt_glass_night_hwy.jpg"):
            jpg_p = REPO_ROOT / "docs" / "assets" / jpg_name
            self.assertTrue(jpg_p.is_file(), f"Missing optical backplate {jpg_name}")
            self.assertLessEqual(jpg_p.stat().st_size, 185 * 1024)
            self.assertNotIn(b"Exif\x00\x00", jpg_p.read_bytes())
        from customizations.scripts.build_showcase import build_showcase
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            src_p = tmp_p / "unified.html"
            src_p.write_text(self.unified_html, encoding="utf-8")
            p_out = tmp_p / "personal.html"
            b_out = tmp_p / "brand.html"
            build_showcase(REPO_ROOT / "customizations" / "personal-starter", src_p, p_out, bundle=False)
            build_showcase(REPO_ROOT / "customizations" / "brand-starter", src_p, b_out, bundle=False)
            self.assertIn("tpl-view-v16-transparent-window-overlay", p_out.read_text(encoding="utf-8"))
            self.assertNotIn("tpl-view-v16-transparent-window-overlay", b_out.read_text(encoding="utf-8"))
            self.assertIn("tpl-view-v14-fieldbus-and-scope-debugger", b_out.read_text(encoding="utf-8"))

    def test_static_all_worlds_clean(self) -> None:
        self.assertEqual(verify_static(all_worlds=True), [])

    def test_echarts_conservation_rigor_and_rationale_scrubbing(self) -> None:
        from compilers.echarts_adapter import build_echarts_payload
        from compilers.plot_compiler import compile_plot
        from src.v9.views.rationale_formatter import scrub_prose

        cross_wf = {
            "$schema": "urn:quiet-ui:schema:v9:plot", "plot_kind": "waterfall", "id": "cross-wf",
            "metadata": {"title": "Zero Crossing Bridge", "rigor_level": "L2"},
            "axes": {"y_axis": {"unit": "M", "quantity_calculus": "Balance / M"}},
            "steps": [{"label": "Open", "value": 20.0, "kind": "start"}, {"label": "Draw", "delta": -35.0, "kind": "delta"}, {"label": "Close", "value": -15.0, "kind": "total"}],
        }
        pay = build_echarts_payload(cross_wf, "L2", "m3")
        self.assertEqual(pay["spans"][1], [-15.0, 20.0, -35.0, "dec"])
        self.assertIn("-15.0", compile_plot(cross_wf, rigor="L2"))
        bad_wf = {**cross_wf, "steps": [{"label": "Open", "value": 20.0, "kind": "start"}, {"label": "Close", "value": 99.0, "kind": "total"}]}
        with self.assertRaises(ValueError):
            compile_plot(bad_wf, rigor="L2")
        with self.assertRaises(ValueError):
            build_echarts_payload(bad_wf, "L2", "m3")

        eq_spec = {
            "$schema": "urn:quiet-ui:schema:v9:plot", "id": "eq-sync", "metadata": {"title": "Eq"},
            "parametric_legend": [{"symbol": "V_0", "value": 5.0, "unit": "V"}, {"symbol": "tau", "value": 2.0, "unit": "s"}],
            "axes": {"x_axis": {"domain": [0, 4]}, "y_axis": {"domain": [0, 6]}},
            "series": [
                {"id": "m", "epistemic_type": "analytical_model", "equation": "y = V_0 * exp(-x / tau)"},
                {"id": "d", "epistemic_type": "discrete_measurement", "marker_color": "var(--accent-focal)", "data_points": [{"x": 0.0, "y": 5.0, "u_y": 0.5}]},
            ],
            "residual_strip": {"enabled": True},
        }
        l1_pay = build_echarts_payload(eq_spec, "L1", "m2")
        self.assertEqual(len(l1_pay["series"]), 1)
        l3_pay = build_echarts_payload(eq_spec, "L3", "m3")
        self.assertTrue(l3_pay["series"][1]["colorExplicit"])
        self.assertTrue(l3_pay["residuals"]["points"])
        self.assertEqual(l3_pay["residuals"]["points"][0][1], 0.0)
        self.assertNotIn("PANEL-MAIN-200A", scrub_prose("PANEL-MAIN-200A uses M7 and L3 Booktabs for N4"))
        self.assertNotIn("Booktabs", scrub_prose("L3 Booktabs table in v18-home-assistant-companion-console"))

    def test_phase62_directional_views_conservation_and_hygiene(self) -> None:
        m = re.search(r'<script[^>]*id="va-v9-manifest"[^>]*>(.*?)</script>', self.unified_html, flags=re.S)
        manifest = json.loads(m.group(1))
        by_id = {vw["view_id"]: vw for w in manifest["worlds"] for vw in w["views"]}
        for vid in ("v19-product-roadmap-and-triage", "v20-student-capstone-lab-report", "v21-field-anomaly-escalation-tsn"):
            self.assertIn(vid, by_id, f"Missing {vid} in 5-world build")
            tpl_m = re.search(rf'<template id="tpl-view-{vid}">(.*?)</template>', self.unified_html, flags=re.S)
            self.assertIsNotNone(tpl_m)
            frag = tpl_m.group(1)
            self.assertNotIn("!important", frag.lower())
            self.assertNotIn("qe-fig-badges", frag)
            for leak in ("QUIET-BRIDGE", "Murder-Board", "Decision Contrast", "Pedagogical Flow", "Quiet Cockpit"):
                self.assertNotIn(leak, frag)
        v19_txt = re.search(r'<template id="tpl-view-v19-product-roadmap-and-triage">(.*?)</template>', self.unified_html, flags=re.S).group(1)
        for tok in ("250.0", "12.0 s", "0x8003B104", "+3.0 d", "4 Tracked"):
            self.assertIn(tok, v19_txt)
        v20_txt = re.search(r'<template id="tpl-view-v20-student-capstone-lab-report">(.*?)</template>', self.unified_html, flags=re.S).group(1)
        for tok in ("5.00 V", "2.40 s", "1.84 V", "1.82 V", "0.05 V", "0.8"):
            self.assertIn(tok, v20_txt)
        v21_txt = re.search(r'<template id="tpl-view-v21-field-anomaly-escalation-tsn">(.*?)</template>', self.unified_html, flags=re.S).group(1)
        for tok in ("120 Ω", "0.3 m", "0.35 µs", "85 °C", "42.8%", "8.0 h"):
            self.assertIn(tok, v21_txt)


if __name__ == "__main__":
    unittest.main()
