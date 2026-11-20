# SPDX-License-Identifier: Apache-2.0
"""Unit and integration tests for Quiet UI v9.0 Pillar 2 evidence compilers."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPILER_SCRIPTS = REPO_ROOT / "skills" / "quiet-evidence" / "scripts"
if str(COMPILER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMPILER_SCRIPTS))

from compile_evidence import compile_spec, detect_modality  # noqa: E402
from compilers.math_eval import eval_equation  # noqa: E402
from compilers.tokens_and_scales import (  # noqa: E402
    compute_linear_125_scale,
    compute_log_decade_scale,
    format_quantity_header,
    format_value_unit,
    select_engineering_prefix,
)


class TestTokensAndScales(unittest.TestCase):
    def test_linear_125_steps_across_ranges(self) -> None:
        for lo, hi in ((0.0, 100.0), (-65.0, 65.0), (74.0, 80.0), (0.002, 0.019), (5.0, 5.0)):
            sc = compute_linear_125_scale(lo, hi, target_ticks=6)
            self.assertIn(sc["mantissa"], (1, 2, 5))
            self.assertGreaterEqual(len(sc["majors"]), 2)
            self.assertLessEqual(sc["min"], lo + 1e-12)
            self.assertGreaterEqual(sc["max"], hi - 1e-12)

    def test_log_decade_mandatory_minor_ticks(self) -> None:
        sc = compute_log_decade_scale(1e-3, 1e4)
        self.assertEqual(len(sc["majors"]), 8)
        self.assertEqual(len(sc["minors"]), 56)  # 7 decades * 8 minor ticks (2..9)

    def test_nist_sp811_unit_formatting(self) -> None:
        self.assertEqual(format_quantity_header("f", "Frequency", "GHz"), "Frequency, f / GHz")
        self.assertNotIn("[", format_quantity_header("t", "Time", "ps"))
        txt = format_value_unit(77.342, "K", uncertainty=0.015)
        self.assertEqual(txt, "(77.342 ± 0.015)\u00a0K")
        deg = format_value_unit(45, "°")
        self.assertEqual(deg, "45°")
        factor, unit = select_engineering_prefix(2.5e9, "Hz")
        self.assertEqual(unit, "GHz")
        self.assertAlmostEqual(2.5e9 * factor, 2.5)

    def test_safe_math_eval(self) -> None:
        val = eval_equation("1.28e-13 * tau^(-0.5)", tau=100.0)
        self.assertAlmostEqual(val, 1.28e-14)
        with self.assertRaises(ValueError):
            eval_equation("__import__('os').system('echo nope')", tau=1.0)


class TestEvidenceCompilers(unittest.TestCase):
    def test_all_30_bench_specimens_compile(self) -> None:
        spec_dir = REPO_ROOT / "docs" / "bench" / "specimens"
        count = 0
        for jf in sorted(spec_dir.glob("*.json")):
            specs = json.loads(jf.read_text(encoding="utf-8"))
            for sp in specs:
                count += 1
                mod = detect_modality(sp)
                self.assertIn(mod, ("scalar", "table", "bitfield", "plot", "waveform", "schematic"))
                for theme in ("white", "paper", "dark-paper", "dark"):
                    out = compile_spec(sp, theme=theme)
                    self.assertIn("qe-figure", out)
                    self.assertNotIn("preserveAspectRatio=\"none\"", out)
                    self.assertNotIn("!important", out)
                    # Every <path must declare fill=
                    for m in re.finditer(r"<path\b[^>]*>", out):
                        self.assertIn("fill=", m.group(0))
        self.assertEqual(count, 30)

    def test_rigor_continuum_and_epistemic_truth(self) -> None:
        plot_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m4_plots.json").read_text("utf-8"))
        allan = plot_specs[2]
        out_l3 = compile_spec(allan, rigor="L3", medium="m1")
        self.assertIn("va-test-condition-block", out_l3)
        self.assertIn("Normalized Residuals", out_l3)
        self.assertNotRegex(out_l3, r'<path[^>]*\bd="[^"]*\bC\b')

        wave_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m5_waveforms.json").read_text("utf-8"))
        scope_l3 = compile_spec(wave_specs[2], rigor="L3")
        self.assertIn("DROPOUT", scope_l3)
        paths = re.findall(r'<path[^>]*\bd="([^"]+)"', scope_l3)
        self.assertTrue(any(len(re.findall(r"\bM\s+", d)) >= 2 for d in paths))

        sch_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m6_schematics.json").read_text("utf-8"))
        bus_l3 = compile_spec(sch_specs[2], rigor="L3")
        self.assertGreaterEqual(bus_l3.count("78 Ω"), 4)
        self.assertIn("58.5 Ω XFMR", bus_l3)
        self.assertIn("A 5 5", bus_l3)

    def test_all_css_tokens_are_defined(self) -> None:
        tok_css = (REPO_ROOT / "tokens" / "quiet-ui-tokens.css").read_text("utf-8")
        bench_css = (REPO_ROOT / "docs" / "bench" / "evidence-bench.css").read_text("utf-8")
        pills_css = (REPO_ROOT / "src" / "css" / "06-b-pills-and-annunciators.css").read_text("utf-8")
        dir_css = (REPO_ROOT / "src" / "v9" / "css" / "08-directional-and-planner.css").read_text("utf-8")
        defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", tok_css + "\n" + bench_css + "\n" + pills_css + "\n" + dir_css))
        for ref in re.findall(r"var\((--[a-z0-9-]+)", bench_css + "\n" + pills_css + "\n" + dir_css):
            self.assertIn(ref, defined, f"Undefined CSS var in bench/pills/directional CSS: {ref}")
        tok_only = set(re.findall(r"(--[a-z0-9-]+)\s*:", tok_css))
        for jf in sorted((REPO_ROOT / "docs" / "bench" / "specimens").glob("*.json")):
            for sp in json.loads(jf.read_text("utf-8")):
                out = compile_spec(sp, rigor="L3", medium="m1", theme="white")
                for ref in re.findall(r"var\((--[a-z0-9-]+)", out):
                    self.assertIn(ref, tok_only, f"Undefined CSS var in compiled {sp.get('id')}: {ref}")

    def test_p0_xss_and_security_guards(self) -> None:
        from compilers.tokens_and_scales import resolve_token
        self.assertEqual(resolve_token('#" onload="alert(1)'), "var(--accent-focal)")
        self.assertEqual(resolve_token('rgb(0,0,0)"/><script>alert(1)</script>'), "var(--accent-focal)")
        self.assertEqual(resolve_token("#1D4ED8"), "#1D4ED8")

        mal_wave = {
            "$schema": "urn:quiet-ui:schema:v9:waveform",
            "id": "xss-wave",
            "metadata": {"title": "XSS", "rigor_level": "L2"},
            "timebase": {"start_time": 0, "total_span": 0, "unit": "</script><img src=x>"},
            "channels": [{"id": "c1", "samples": [[0, 1], [1, 2]]}],
        }
        w_out = compile_spec(mal_wave)
        self.assertNotIn("</script><img", w_out)

        mal_plot = {
            "$schema": "urn:quiet-ui:schema:v9:plot",
            "id": "xss-plot",
            "metadata": {"title": "XSS Plot", "rigor_level": "L2"},
            "series": [{"id": "s1", "epistemic_type": "analytical_model", "equation": "x", "stroke_dasharray": '5" onload="alert(1)'}],
        }
        p_svg = compile_spec(mal_plot, include_spec_drawer=False)
        self.assertNotIn("onload=", p_svg)
        p_full = compile_spec(mal_plot)
        self.assertIn("alert(1)", p_full)
        self.assertNotIn("<script>alert", p_full)

        for bad_expr in ("9^9^9", "(-1)^0.5", "True", "sin(" * 40 + "1" + ")" * 40):
            with self.assertRaises(ValueError):
                eval_equation(bad_expr, x=1.0)

    def test_p1_boundary_rigor_and_standalone_array(self) -> None:
        sc_fs = compute_linear_125_scale(0.0, 5e-15, target_ticks=5)
        self.assertGreater(sc_fs["max"], 0.0)
        self.assertEqual(len(sc_fs["majors"]), len(set(sc_fs["majors"])))

        neg_db = {
            "$schema": "urn:quiet-ui:schema:v9:plot",
            "plot_kind": "dumbbell",
            "metadata": {"title": "Neg dBm"},
            "axes": {"y_axis": {"unit": "dBm"}},
            "dumbbells": [{"label": "S1", "before": -42.0, "after": -18.5}, {"label": "S2", "before": -36.0, "after": -14.2}],
        }
        self.assertIn("-18.5", compile_spec(neg_db))

        null_scalar = {
            "$schema": "urn:quiet-ui:schema:v9:scalar",
            "metadata": {"title": "One-sided"},
            "quantity": {"symbol": "T", "unit": "°"},
            "measurement": {"nominal_value": 45},
            "limits": {"warning_thresholds": {"upper": 60}, "abort_thresholds": {"lower": None, "upper": 80}},
            "status_annunciator": {"state": "NOMINAL"},
        }
        s_out = compile_spec(null_scalar, rigor="L3")
        self.assertIn("45°", s_out)

        m3_file = REPO_ROOT / "docs" / "bench" / "specimens" / "m3_bitfields.json"
        m3_specs = json.loads(m3_file.read_text("utf-8"))
        l1_bf = compile_spec(m3_specs[2], rigor="L1")
        self.assertIn("Term Flag: ACTIVE", l1_bf)
        self.assertNotIn("[RW]", l1_bf)

        arr_standalone = compile_spec(m3_file, theme="dark", standalone=True)
        self.assertIn('data-theme="dark"', arr_standalone)
        self.assertGreaterEqual(arr_standalone.count("<figure "), 3)

    def test_gate21_regressions_and_cross_domain(self) -> None:
        from compilers.tokens_and_scales import format_math_unicode
        self.assertEqual(format_math_unicode("2.0e-12*tau^-0.5"), "2.0 × 10⁻¹² τ⁻⁰·⁵")
        self.assertEqual(format_math_unicode("(y_i - y_hat) / u_y"), "(yᵢ − ŷ) / u_y")
        self.assertEqual(format_math_unicode("Mod sigma_y(tau)"), "Mod σ_y(τ)")

        # 1. SI units & duplicate table caption suppression
        t_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m2_tables.json").read_text("utf-8"))
        t_out = compile_spec(t_specs[2], rigor="L3")
        self.assertIn('<span class="qe-unit">t<sub>skew</sub> / ps</span>', t_out)
        self.assertIn("qe-caption-sr", t_out)

        # 2. Plot legend swatches & diagonal sloped halo curve label
        p_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m4_plots.json").read_text("utf-8"))
        p_out = compile_spec(p_specs[2], rigor="L3")
        self.assertIn('transform="rotate(', p_out)
        self.assertNotIn("qe-label-pill", p_out)
        m_leg = re.search(r'data-epistemic="model"[^>]*>.*?</svg>', p_out, re.S)
        d_leg = re.search(r'data-epistemic="discrete"[^>]*>.*?</svg>', p_out, re.S)
        self.assertIsNotNone(m_leg)
        self.assertIn('stroke-dasharray="5,4"', m_leg.group(0))
        self.assertNotIn("<circle", m_leg.group(0))
        self.assertIsNotNone(d_leg)
        self.assertIn("<circle", d_leg.group(0))

        # 3. Foreign enclave_id non-contamination even with oversized explicit box
        enclave_spec = {
            "$schema": "urn:quiet-ui:schema:v9:schematic",
            "id": "enc-iso",
            "metadata": {"title": "Enclave Isolation", "rigor_level": "L2"},
            "schematic_kind": "topology",
            "enclaves": [{"id": "e1", "label": "ENC-1", "x": 16, "y": 20, "w": 188, "h": 286}],
            "nodes": [
                {"id": "a", "enclave_id": "e1", "label": "Node A", "x": 32, "y": 78, "w": 156, "h": 58},
                {"id": "b", "enclave_id": "e2", "label": "Foreign Node", "x": 32, "y": 216, "w": 156, "h": 58},
            ],
            "edges": [{"from": "a", "to": "b", "label": "PPSM-99"}],
        }
        e_out = compile_spec(enclave_spec, rigor="L2")
        self.assertIn("ENC-1", e_out)
        self.assertIn("e2", e_out)
        self.assertIn("va-svg-halo-text", e_out)
        m6_l2 = compile_spec(json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m6_schematics.json").read_text("utf-8"))[1], rigor="L2")
        self.assertIn("qe-svg-knockout", m6_l2)
        # First enclave rect must not span down to y=216 (Node B)
        enc_rects = re.findall(r'<rect data-role="enclave" x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" height="([0-9.]+)" rx="8"', e_out)
        self.assertEqual(len(enc_rects), 2)
        self.assertLess(float(enc_rects[0][1]) + float(enc_rects[0][3]), 200.0)

        # 4. Waveform calibrated Y-spine
        w_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m5_waveforms.json").read_text("utf-8"))
        w_out = compile_spec(w_specs[2], rigor="L3")
        self.assertIn("+70", w_out)
        self.assertIn("-70", w_out)
        self.assertIn("+8", w_out)

        # 5. FSM dynamic bottom viewBox padding
        fsm_spec = {
            "$schema": "urn:quiet-ui:schema:v9:schematic",
            "id": "fsm-pad",
            "metadata": {"title": "FSM Pad", "rigor_level": "L3"},
            "schematic_kind": "fsm",
            "states": [{"id": "s1", "label": "INIT"}, {"id": "s2", "label": "RUN"}],
            "transitions": [{"from": "s1", "to": "s2", "label": "go"}, {"from": "s2", "to": "s1", "label": "reset"}],
        }
        f_out = compile_spec(fsm_spec, rigor="L3")
        vb_h = int(re.search(r'viewBox="0 0 720 (\d+)"', f_out).group(1))
        pill_bottoms = [float(y) + float(h) for y, h in re.findall(r'class="qe-svg-knockout-bg"[^>]*\by="([0-9.]+)"[^>]*\bheight="([0-9.]+)"', f_out)]
        self.assertTrue(pill_bottoms and all(b <= vb_h for b in pill_bottoms))

        # 6. Scalar atomic annunciator & separate margin span
        s_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m1_scalars.json").read_text("utf-8"))
        s_out = compile_spec(s_specs[2], rigor="L3", include_wrapper=False)
        self.assertEqual(s_out.count("STALE DATA"), 1)
        self.assertIn('data-variant="status"', s_out)
        self.assertIn("CAUTION", s_out)
        self.assertIn("Margin +18.0%", s_out)

        # 7. Cross-domain CAN-FD, RS-485/Modbus & Forest CI plot
        can_out = compile_spec({"$schema": "urn:quiet-ui:schema:v9:schematic", "id": "can", "metadata": {"title": "CAN", "rigor_level": "L3"}, "schematic_kind": "differential_bus", "bus_standard": "can_fd", "terminals": [{"label": "ECM"}, {"label": "BMS"}]})
        self.assertIn("CAN_H", can_out)
        self.assertIn("120 Ω", can_out)
        mod_out = compile_spec({"$schema": "urn:quiet-ui:schema:v9:schematic", "id": "mod", "metadata": {"title": "MOD", "rigor_level": "L3"}, "schematic_kind": "differential_bus", "bus_standard": "modbus", "terminals": [{"label": "PLC"}, {"label": "VFD"}]})
        self.assertIn("D+ (B)", mod_out)
        self.assertIn("560 Ω Bias", mod_out)
        for_out = compile_spec({"$schema": "urn:quiet-ui:schema:v9:plot", "id": "for", "plot_kind": "forest", "metadata": {"title": "Trial"}, "axes": {"x_axis": {"quantity_calculus": "HR (95% CI)"}}, "null_value": 1.0, "items": [{"label": "Subgroup A", "estimate": 0.72, "ci_low": 0.58, "ci_high": 0.89}]})
        self.assertIn("0.72 (0.58–0.89)", for_out)

    def test_gate31_pill_grammar_invariants(self) -> None:
        for jf in sorted((REPO_ROOT / "docs" / "bench" / "specimens").glob("*.json")):
            for sp in json.loads(jf.read_text("utf-8")):
                out = compile_spec(sp, rigor="L3", medium="m3", theme="white")
                self.assertNotIn("qe-label-pill", out, f"Legacy .qe-label-pill in {sp['id']}")
                for bad in ("[ NOMINAL ]", "[ CAUTION ]", "[ STALE DATA ]", "[ TRIPWIRE ]"):
                    self.assertNotIn(bad, out, f"Bracketed pill {bad} in {sp['id']}")
                for ko_rect in re.findall(r'<rect class="qe-svg-knockout-bg"[^>]*>', out):
                    self.assertIn('stroke="none"', ko_rect, f"Stroked knockout rect in {sp['id']}")
        m1 = compile_spec(json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m1_scalars.json").read_text("utf-8"))[2], rigor="L3")
        self.assertIn('data-variant="status" data-state="nominal">Nominal</span>', m1)
        self.assertIn('<span class="qe-scalar-margin va-nums">Margin +18.0%</span>', m1)
        self.assertEqual(m1.count("va-figure-scroll"), 2)  # 1 per side-by-side scalar card (never double-nested)
        m2 = compile_spec(json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m2_tables.json").read_text("utf-8"))[2], rigor="L3")
        nom_cells = re.findall(r'<rect class="qe-heatmap-cell"[^>]*data-state="nominal"[^>]*>', m2)
        self.assertEqual(len(nom_cells), 22)
        for nc in nom_cells:
            self.assertIn('fill="var(--bg-elevated)"', nc)
        m4 = compile_spec(json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m4_plots.json").read_text("utf-8"))[0], rigor="L3")
        self.assertIn('<button type="button" class="va-pill qe-eq-term', m4)
        self.assertIn('data-variant="chip"', m4)
        m5 = compile_spec(json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m5_waveforms.json").read_text("utf-8"))[2], rigor="L3")
        self.assertEqual(m5.count("DROPOUT "), 1)
        w1c = compile_spec(json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m3_bitfields.json").read_text("utf-8"))[2], rigor="L3")
        self.assertIn('data-variant="tag">W1C</span>', w1c)
        self.assertIn('class="qe-bf-access-ro">RO</span>', w1c)
        staggered = compile_spec({
            "$schema": "urn:quiet-ui:schema:v9:waveform", "id": "w-stag",
            "metadata": {"title": "Staggered", "rigor_level": "L3"},
            "timebase": {"unit": "ms", "domain": [0, 10]},
            "channels": [
                {"id": "a", "name": "A", "unit": "V", "vertical_scale_per_div": 5, "threshold_envelopes": [{"value": "4.5"}], "samples": [[0, 1], [1, 1], [2, None], [5, 1], [6, 1], [10, 1]]},
                {"id": "d", "name": "D", "type": "digital", "unit": "logic", "samples": [[0, 0], [1, 1], [2.5, None], [5.5, 0], [6, 1], [10, 1]]},
            ],
        }, rigor="L3")
        self.assertEqual(staggered.count("DROPOUT "), 1)
        self.assertIn("+4.5\u00a0V", staggered)

        # 8. Open-standards clean-room systems schematics (ITU-T Z.120, NASA SP-2016-6105, NRC NUREG-0492)
        sys_specs = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m6_systems_schematics.json").read_text("utf-8"))
        self.assertEqual(len(sys_specs), 3)
        compiled_sys = [compile_spec(sp, rigor="L3", medium="m2", theme="white") for sp in sys_specs]
        self.assertIn("ClientHello + SPIFFE ID", compiled_sys[0])
        self.assertIn("t = 0 ms", compiled_sys[0])
        self.assertIn("NASA SP-2016-6105", compiled_sys[1])
        self.assertIn("Valve Pulse cmd", compiled_sys[1])
        self.assertIn("Loss of Core Coolant Flow", compiled_sys[2])
        self.assertIn(">AND<", compiled_sys[2])
        self.assertIn(">OR<", compiled_sys[2])
        for out_svg in compiled_sys:
            self.assertIn('viewBox="0 0 720', out_svg)
            for path_tag in re.findall(r"<path\b[^>]*>", out_svg):
                self.assertIn("fill=", path_tag)

    def test_phase61_gantt_heatmap_pipeline_interlock_and_ui_specimens(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from bench_ui_specimens import compile_ui_bridge_specimens
        from compilers.echarts_adapter import build_echarts_payload, render_ecosystem_drawer

        ev_plots = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m4_everyday_charts.json").read_text("utf-8"))
        self.assertEqual(len(ev_plots), 5)
        for sp in ev_plots:
            out = compile_spec(sp, rigor=sp["metadata"]["rigor_level"], medium="m2")
            self.assertIn("data-quiet-echarts", out)
            pay = build_echarts_payload(sp, sp["metadata"]["rigor_level"], "m2")
            self.assertIsNotNone(pay)
            drawer = render_ecosystem_drawer(sp)
            self.assertIn("Apache ECharts", drawer)

        gantt_pay = build_echarts_payload(ev_plots[3], "L2", "m2")
        self.assertEqual(gantt_pay["kind"], "gantt")
        self.assertIn("gantt", render_ecosystem_drawer(ev_plots[3]))

        hm_out = compile_spec(ev_plots[4], rigor="L2", medium="m2")
        self.assertIn("linearGradient", hm_out)
        self.assertIn("#0F172A", hm_out)

        ev_topo = json.loads((REPO_ROOT / "docs" / "bench" / "specimens" / "m6_everyday_topologies.json").read_text("utf-8"))
        self.assertEqual(len(ev_topo), 4)
        self.assertIn("metrics_store" if False else "Metrics Store", compile_spec(ev_topo[1]))
        self.assertIn("SAFE TRIP", compile_spec(ev_topo[2], rigor="L3"))

        ui_html = compile_ui_bridge_specimens()
        self.assertEqual(ui_html.count('<article class="qe-specimen'), 6)
        self.assertIn("ui-coupled-tree-explorer", ui_html)
        self.assertIn("br-review-room-gate-band", ui_html)


if __name__ == "__main__":
    unittest.main()
