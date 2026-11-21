#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unit, security, ECharts, and standalone portability tests for Quiet UI Pillar 2 compilers."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPILER_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
for p in (REPO_ROOT, REPO_ROOT / "scripts", COMPILER_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from bench_ui_specimens import compile_ui_bridge_specimens  # noqa: E402
from build_showcase import build_showcase as build_studio_showcase  # noqa: E402
from compile_evidence import compile_spec, detect_modality  # noqa: E402
from compilers.echarts_adapter import build_echarts_payload, render_ecosystem_drawer  # noqa: E402
from compilers.math_eval import eval_equation  # noqa: E402
from compilers.plot_compiler import compile_plot  # noqa: E402
from compilers.tokens_and_scales import (  # noqa: E402
    compute_linear_125_scale,
    compute_log_decade_scale,
    format_math_svg,
    format_math_unicode,
    format_quantity_header,
    format_value_unit,
    resolve_token,
    select_engineering_prefix,
)
from customizations.scripts.build_showcase import build_showcase as build_starter_showcase  # noqa: E402
from src.views.rationale_formatter import scrub_prose  # noqa: E402


class TestTokensAndMath(unittest.TestCase):
    def test_scales_units_and_math_formatting(self) -> None:
        for lo, hi in ((0.0, 100.0), (-65.0, 65.0), (74.0, 80.0), (0.0, 5e-15), (5.0, 5.0)):
            sc = compute_linear_125_scale(lo, hi, target_ticks=6)
            self.assertIn(sc["mantissa"], (1, 2, 5))
            self.assertEqual(len(sc["majors"]), len(set(sc["majors"])))
        log_sc = compute_log_decade_scale(1e-3, 1e4)
        self.assertEqual((len(log_sc["majors"]), len(log_sc["minors"])), (8, 56))
        self.assertEqual(format_quantity_header("f", "Frequency", "GHz"), "Frequency, f / GHz")
        self.assertEqual(format_value_unit(77.342, "K", uncertainty=0.015), "(77.342 ± 0.015)\u00a0K")
        self.assertEqual(format_value_unit(45, "°"), "45°")
        factor, unit = select_engineering_prefix(2.5e9, "Hz")
        self.assertEqual(unit, "GHz")
        self.assertAlmostEqual(2.5e9 * factor, 2.5)
        self.assertEqual(format_math_unicode("2.0e-12*tau^-0.5"), "2.0 × 10⁻¹² τ⁻⁰·⁵")
        self.assertEqual(format_math_unicode("(y_i - y_hat) / u_y"), "(yᵢ − ŷ) / u_y")
        svg_txt = format_math_svg("tau_1 + mu_0 + p_hat_2", sub_size=9.5)
        self.assertTrue(all(tok in svg_txt for tok in ("τ", "μ", "p̂", 'font-size="9.5"')))
        self.assertAlmostEqual(eval_equation("1.28e-13 * tau^(-0.5)", tau=100.0), 1.28e-14)

    def test_security_xss_and_ast_dos_guards(self) -> None:
        self.assertEqual(resolve_token('#" onload="alert(1)'), "var(--accent-focal)")
        self.assertEqual(resolve_token('rgb(0,0,0)"/><script>alert(1)</script>'), "var(--accent-focal)")
        self.assertEqual(resolve_token("#1D4ED8"), "#1D4ED8")
        for bad_expr in ("__import__('os').system('nope')", "9^9^9", "(-1)^0.5", "True", "sin(" * 40 + "1" + ")" * 40):
            with self.assertRaises(ValueError):
                eval_equation(bad_expr, x=1.0, tau=1.0)
        mal_wave = {
            "$schema": "urn:quiet-ui:schema:v9:waveform", "id": "xss-w",
            "metadata": {"title": "XSS"}, "timebase": {"start_time": 0, "total_span": 0, "unit": "</script><img src=x>"},
            "channels": [{"id": "c1", "samples": [[0, 1], [1, 2]]}],
        }
        self.assertNotIn("</script><img", compile_spec(mal_wave))
        mal_plot = {
            "$schema": "urn:quiet-ui:schema:v9:plot", "id": "xss-p",
            "metadata": {"title": "XSS"},
            "series": [{"id": "s1", "epistemic_type": "analytical_model", "equation": "x", "stroke_dasharray": '5" onload="alert(1)'}],
        }
        self.assertNotIn("onload=", compile_spec(mal_plot, include_spec_drawer=False))
        self.assertNotIn("<script>alert", compile_spec(mal_plot))


class TestEvidenceCompilers(unittest.TestCase):
    def test_all_33_bench_specimens_and_css_tokens(self) -> None:
        spec_dir = REPO_ROOT / "docs" / "bench" / "specimens"
        tok_css = (REPO_ROOT / "tokens" / "quiet-ui-tokens.css").read_text("utf-8")
        tok_only = set(re.findall(r"(--[a-z0-9-]+)\s*:", tok_css))
        count = 0
        for jf in sorted(spec_dir.glob("*.json")):
            for sp in json.loads(jf.read_text("utf-8")):
                count += 1
                self.assertIn(detect_modality(sp), ("scalar", "table", "bitfield", "plot", "waveform", "schematic"))
                for theme in ("white", "paper", "dark-paper", "dark"):
                    out = compile_spec(sp, theme=theme)
                    self.assertIn("qe-figure", out)
                    self.assertNotIn('preserveAspectRatio="none"', out)
                    self.assertNotIn("!important", out.lower())
                    for m in re.finditer(r"<path\b[^>]*>", out):
                        self.assertIn("fill=", m.group(0))
                out_l3 = compile_spec(sp, rigor="L3", medium="m1", theme="white")
                for ref in re.findall(r"var\((--[a-z0-9-]+)", out_l3):
                    self.assertIn(ref, tok_only, f"Undefined token in {sp.get('id')}: {ref}")
        self.assertEqual(count, 33)

    def test_modalities_rigor_and_pill_grammar(self) -> None:
        spec_dir = REPO_ROOT / "docs" / "bench" / "specimens"
        allan = json.loads((spec_dir / "m4_plots.json").read_text("utf-8"))[2]
        out_l3 = compile_spec(allan, rigor="L3", medium="m1")
        self.assertIn("va-test-condition-block", out_l3)
        self.assertIn("Normalized Residuals", out_l3)
        self.assertIn('transform="rotate(', out_l3)
        self.assertNotRegex(out_l3, r'<path[^>]*\bd="[^"]*\bC\b')

        scope = compile_spec(json.loads((spec_dir / "m5_waveforms.json").read_text("utf-8"))[2], rigor="L3")
        self.assertEqual(scope.count("DROPOUT "), 1)
        self.assertTrue(any(len(re.findall(r"\bM\s+", d)) >= 2 for d in re.findall(r'<path[^>]*\bd="([^"]+)"', scope)))

        bus = compile_spec(json.loads((spec_dir / "m6_schematics.json").read_text("utf-8"))[2], rigor="L3")
        self.assertGreaterEqual(bus.count("78 Ω"), 4)
        self.assertIn("58.5 Ω XFMR", bus)

        sys_specs = json.loads((spec_dir / "m6_systems_schematics.json").read_text("utf-8"))
        self.assertIn("ClientHello + SPIFFE ID", compile_spec(sys_specs[0], rigor="L3"))
        self.assertIn("NASA SP-2016-6105", compile_spec(sys_specs[1], rigor="L3"))
        self.assertIn(">AND<", compile_spec(sys_specs[2], rigor="L3"))

        m1 = compile_spec(json.loads((spec_dir / "m1_scalars.json").read_text("utf-8"))[2], rigor="L3")
        self.assertIn('data-variant="status" data-state="nominal">Nominal</span>', m1)
        self.assertIn('<span class="qe-scalar-margin va-nums">Margin +18.0%</span>', m1)
        m2 = compile_spec(json.loads((spec_dir / "m2_tables.json").read_text("utf-8"))[2], rigor="L3")
        self.assertIn('<span class="qe-unit">t<sub>skew</sub> / ps</span>', m2)
        self.assertEqual(len(re.findall(r'<rect class="qe-heatmap-cell"[^>]*data-state="nominal"[^>]*>', m2)), 22)
        w1c = compile_spec(json.loads((spec_dir / "m3_bitfields.json").read_text("utf-8"))[2], rigor="L3")
        self.assertIn('data-variant="tag">W1C</span>', w1c)
        self.assertIn('class="qe-bf-access-ro">RO</span>', w1c)

    def test_everyday_charts_sankey_scatter_strip_and_ui_specimens(self) -> None:
        spec_dir = REPO_ROOT / "docs" / "bench" / "specimens"
        m4 = json.loads((spec_dir / "m4_everyday_charts.json").read_text("utf-8"))
        self.assertEqual(len(m4), 7)
        sankey = next(s for s in m4 if s["id"] == "bench-m4-sankey-power-balance")
        self.assertIn("178.5 kW (71.4%)", compile_spec(sankey, rigor="L2"))
        self.assertEqual(build_echarts_payload(sankey)["kind"], "sankey")
        self.assertIn("go.Sankey", render_ecosystem_drawer(sankey))
        scatter = next(s for s in m4 if s["id"] == "bench-m4-scatter-regime-cloud")
        self.assertIn("140 °C Derate", compile_spec(scatter, rigor="L3"))
        self.assertEqual(sum(len(sr["data"]) for sr in build_echarts_payload(scatter, "L3", "m2")["series"][:3]), 84)
        strip = next(s for s in json.loads((spec_dir / "m5_waveforms.json").read_text("utf-8")) if s["id"] == "bench-m5-strip-chart-telemetry")
        self.assertIn("EXCURSION", compile_spec(strip, rigor="L3"))
        self.assertEqual(len(build_echarts_payload(strip, "L3", "m2")["tracks"]), 4)
        ui_html = compile_ui_bridge_specimens()
        self.assertEqual(ui_html.count('<article class="qe-specimen'), 6)
        self.assertIn("ui-coupled-tree-explorer", ui_html)
        self.assertIn("br-review-room-gate-band", ui_html)

    def test_echarts_conservation_boundaries_and_rationale_scrub(self) -> None:
        cross_wf = {
            "$schema": "urn:quiet-ui:schema:v9:plot", "plot_kind": "waterfall", "id": "cross-wf",
            "metadata": {"title": "Bridge"}, "axes": {"y_axis": {"unit": "M"}},
            "steps": [{"label": "Open", "value": 20.0, "kind": "start"}, {"label": "Draw", "delta": -35.0, "kind": "delta"}, {"label": "Close", "value": -15.0, "kind": "total"}],
        }
        self.assertEqual(build_echarts_payload(cross_wf, "L2", "m3")["spans"][1], [-15.0, 20.0, -35.0, "dec"])
        with self.assertRaises(ValueError):
            compile_plot({**cross_wf, "steps": [{"label": "Open", "value": 20.0, "kind": "start"}, {"label": "Close", "value": 99.0, "kind": "total"}]})
        tbl = compile_spec({
            "$schema": "urn:quiet-ui:schema:v9:table", "id": "t-ent", "metadata": {"title": "Entity", "rigor_level": "L3"},
            "columns": [{"key": "sys", "label": "Systems & Mass (ms)", "unit": "ms"}, {"key": "h", "label": "Height (m)", "unit": "m"}],
            "rows": [{"sys": "S1", "h": 1.5}],
        }, rigor="L3", chrome="embedded")
        self.assertNotIn("&a<span", tbl)
        self.assertIn('(<span class="qe-unit">m</span>)', tbl)
        self.assertNotIn("PANEL-MAIN-200A", scrub_prose("PANEL-MAIN-200A uses M7 and L3 Booktabs for N4"))

    def test_domain_06_and_starter_view_filtering(self) -> None:
        html = build_studio_showcase(REPO_ROOT, ["05-physical-systems-auto-and-aero", "06-smart-home-and-energy"])
        self.assertIn("opt_frame_art.jpg", html)
        self.assertIn("v18-home-assistant-companion-console", html)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            src_p = tmp_p / "studio.html"
            src_p.write_text(html, encoding="utf-8")
            p_out, b_out = tmp_p / "p.html", tmp_p / "b.html"
            build_starter_showcase(REPO_ROOT / "customizations" / "personal-starter", src_p, p_out, bundle=False)
            build_starter_showcase(REPO_ROOT / "customizations" / "brand-starter", src_p, b_out, bundle=False)
            self.assertIn("tpl-view-v17-picture-frame-home-kiosk", p_out.read_text("utf-8"))
            self.assertNotIn("tpl-view-v17-picture-frame-home-kiosk", b_out.read_text("utf-8"))

    def test_isolated_portable_quiet_evidence_skill_outside_repo(self) -> None:
        spec_src = REPO_ROOT / "docs" / "bench" / "specimens" / "m5_waveforms.json"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            copied_skill = tmp_p / "quiet-evidence"
            shutil.copytree(
                REPO_ROOT / "skills" / "quiet-evidence",
                copied_skill,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            single_spec = tmp_p / "scope.json"
            single_spec.write_text(json.dumps(json.loads(spec_src.read_text("utf-8"))[2]), encoding="utf-8")
            out_html = tmp_p / "chart.html"
            cli = copied_skill / "scripts" / "compile_evidence.py"
            res = subprocess.run(
                [sys.executable, "-B", str(cli), str(single_spec), "--rigor", "L3", "--theme", "dark", "--out", str(out_html)],
                cwd=tmp_p,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(res.returncode, 0)
            rendered = out_html.read_text(encoding="utf-8")
            self.assertIn('data-theme="dark"', rendered)
            self.assertIn("@layer evidence", rendered)
            self.assertIn("QuietEvidenceRuntime", rendered)
            self.assertIn("qe-waveform-svg", rendered)
            self.assertNotIn("!important", rendered.lower())

            frag = subprocess.run(
                [sys.executable, "-B", str(cli), str(single_spec), "--fragment"],
                cwd=tmp_p,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertTrue(frag.stdout.lstrip().startswith("<figure"))


if __name__ == "__main__":
    unittest.main()
