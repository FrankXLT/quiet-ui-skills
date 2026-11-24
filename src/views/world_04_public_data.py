# SPDX-License-Identifier: Apache-2.0
"""World 04 view builder: v22 Public Data Reading & Mobility Brief."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

_EVIDENCE_SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "quiet-evidence" / "scripts"
if str(_EVIDENCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_EVIDENCE_SCRIPTS))

from compile_evidence import compile_spec


def _esc(val: Any) -> str:
    return html.escape(str(val), quote=True)


def build_v22_html(corpus: dict[str, Any], specs: dict[str, dict[str, Any]]) -> str:
    """Compile v22 Question-First Civic Brief with scope picker, hex map, dumbbell, and diverging matrix."""
    metrics = corpus.get("canonical_metrics") or {}
    us_read = int(float(metrics.get("reading_proficiency_us_pct", {}).get("value", 31)))
    md_read = int(float(metrics.get("reading_proficiency_md_pct", {}).get("value", 35)))
    wy_read = int(float(metrics.get("reading_proficiency_wy_pct", {}).get("value", 36)))
    us_inc = int(float(metrics.get("median_income_us_usd", {}).get("value", 74580)))
    md_inc = int(float(metrics.get("median_income_md_usd", {}).get("value", 98461)))
    wy_inc = int(float(metrics.get("median_income_wy_usd", {}).get("value", 72495)))
    us_g = float(metrics.get("real_income_growth_us_pct", {}).get("value", 2.4))
    md_g = float(metrics.get("real_income_growth_md_pct", {}).get("value", 3.8))
    wy_g = float(metrics.get("real_income_growth_wy_pct", {}).get("value", 4.1))
    eq_pct = float(metrics.get("equal_chance_mobility_pct", {}).get("value", 20.0))

    scope_data = {
        "us": {
            "lead_clause": f"{us_read}% of fourth-graders read proficiently in 2024, down four points since 2019,",
            "lead_rest": f"while real national median household income reached ${us_inc:,} (+{us_g:.1f}% over five years).",
            "focus_state": "",
            "focus_summary": f"US National: {us_read}% proficient nationwide (state range 21%–41%) · Select any state hex tile to inspect.",
            "callouts": [
                {"num": f"{us_read}%", "desc": "4th-graders at or above Proficient reading across all US public schools (2024)"},
                {"num": f"${us_inc:,}", "desc": "Real US median household income in 2024 inflation-adjusted dollars"},
                {"num": f"+{us_g:.1f}%", "desc": f"5-year real US household growth alongside 0.0 pp ({eq_pct:.1f}%) mobility baseline"},
            ],
        },
        "md": {
            "lead_clause": f"{md_read}% of Maryland fourth-graders read proficiently, four points ahead of the US average,",
            "lead_rest": f"paired with ${md_inc:,} median household income (+{md_g:.1f}% real 5-year growth).",
            "focus_state": "MD",
            "callouts": [
                {"num": f"{md_read}%", "desc": f"Maryland Grade 4 Proficient reading share (+{md_read - us_read} pts above US national rate)"},
                {"num": f"${md_inc:,}", "desc": "Maryland 2024 median household income rank top-three nationwide"},
                {"num": f"+{md_g:.1f}%", "desc": f"Maryland 5-year real household growth (+6.1 pp vs {eq_pct:.1f}% mobility baseline)"},
            ],
        },
        "wy": {
            "lead_clause": f"{wy_read}% of Wyoming fourth-graders read proficiently, ranking top-quartile nationwide,",
            "lead_rest": f"while real median household income grew fastest at +{wy_g:.1f}% to ${wy_inc:,}.",
            "focus_state": "WY",
            "callouts": [
                {"num": f"{wy_read}%", "desc": f"Wyoming Grade 4 Proficient reading share (+{wy_read - us_read} pts above US national rate)"},
                {"num": f"${wy_inc:,}", "desc": "Wyoming 2024 median household income across rural and energy counties"},
                {"num": f"+{wy_g:.1f}%", "desc": f"Wyoming 5-year real income gain (+5.4 pp vs {eq_pct:.1f}% neutral mobility baseline)"},
            ],
        },
    }
    safe_scope_json = json.dumps(scope_data, ensure_ascii=False).replace("</", "<\\/")

    hex_html = compile_spec(specs["hex_map"], rigor="L1", medium="m2", theme="white", include_wrapper=True, include_spec_drawer=False, chrome="editorial")
    dumb_html = compile_spec(specs["arrow_dumbbell"], rigor="L2", medium="m2", theme="white", include_wrapper=True, include_spec_drawer=False, chrome="editorial")
    mat_html = compile_spec(specs["mobility_matrix"], rigor="L2", medium="m2", theme="white", include_wrapper=True, include_spec_drawer=False, chrome="editorial")

    us_c = scope_data["us"]
    callout_cards = "".join(
        f'<div class="va-callout-stat" data-v22-callout="{idx}">'
        f'<span class="va-callout-num">{_esc(item["num"])}</span>'
        f'<p class="va-callout-desc">{_esc(item["desc"])}</p>'
        '<span class="va-callout-src">NAEP &amp; Census ACS Public Series</span>'
        "</div>"
        for idx, item in enumerate(us_c["callouts"])
    )

    return f"""
<article class="v9-stage-inner va-question-brief va-editorial-article" id="v22-public-brief">
  <header class="va-article-header" id="v22-overview">
    <p class="va-provenance-eyebrow">Public Data Brief · Updated Nov 2026 · NAEP &amp; Census ACS</p>
    <h1 class="va-brief-question">How have reading proficiency and household income mobility shifted across U.S. states?</h1>
    <p class="va-lead-answer">
      Across
      <select class="va-inline-scope-select" id="v22-scope-select" data-v22-scope-select aria-label="Select jurisdiction scope">
        <option value="us" selected="selected">the United States</option>
        <option value="md">Maryland</option>
        <option value="wy">Wyoming</option>
      </select>,
      <span data-v22-lead><span class="va-lead-highlight">{_esc(us_c["lead_clause"])}</span> {_esc(us_c["lead_rest"])}</span>
    </p>
  </header>

  <section class="va-editorial-callouts" aria-label="Key Public Metrics">{callout_cards}</section>

  <section class="va-breakout-wide va-editorial-section" id="v22-map" aria-label="National State Hex Map">
    {hex_html}
  </section>

  <section class="va-editorial-prose" id="v22-reading-essay" aria-label="Small-State Geography and Reading Trends">
    <h2>Why equal-area tiles reveal small-state gains and stagnation</h2>
    <p>Conventional geographic choropleths squeeze Delaware, Rhode Island, the District of Columbia, and Maryland into narrow slivers that obscure both <strong>{md_read}%</strong> Grade 4 proficiency and local sampling precision. Giving every state plus Washington, DC an identical hexagonal footprint preserves legibility across all 51 jurisdictions while flipping text ink automatically for dark and pale bins alike.</p>
    <p>Viewed side by side from 2019 to 2024, state trajectories split sharply around the <strong>{us_read}%</strong> national average. Louisiana added four points over five years and Maryland held steady at {md_read}%, while Wyoming shed four points from 40% to <strong>{wy_read}%</strong>. Rural district aggregates still anchored in 2022–2023 pooled collections stay marked explicitly with an asterisk rather than being blended silently into 2024 totals.</p>
  </section>

  <section class="va-breakout-wide va-editorial-section" id="v22-dumbbell" aria-label="Ranked Reading Proficiency Shifts">
    {dumb_html}
  </section>

  <section class="va-editorial-prose" id="v22-mobility-essay" aria-label="Household Gains and Intergenerational Mobility">
    <h2>Real income growth alone does not close generational mobility gaps</h2>
    <p>Nominal pay raises meant little where post-2021 living costs absorbed household gains. Between 2019 and 2024, real US median household income edged up <strong>+{us_g:.1f}%</strong> to <strong>${us_inc:,}</strong>, led by energy and rural employment recovery in Wyoming (+{wy_g:.1f}% to ${wy_inc:,}) and sustained high-wage attainment in Maryland (+{md_g:.1f}% to ${md_inc:,}).</p>
    <p>Income levels do not tell the whole mobility story on their own. Under an equal-chance generational benchmark where children from any fifth stand a uniform <strong>{eq_pct:.1f}%</strong> probability of advancing (<strong>0.0 pp</strong> neutral benchmark), Maryland leads by <strong>+6.1 pp</strong> and Wyoming by <strong>+5.4 pp</strong>, whereas households in the lowest income fifth fell <strong>-4.3%</strong> in real income and sit <strong>-1.8 pp</strong> below neutral mobility expectations.</p>
  </section>

  <section class="va-breakout-wide va-editorial-section" id="v22-matrix" aria-label="Income Distribution and Mobility Matrix">
    {mat_html}
  </section>

  <script type="application/json" class="v22-scope-payload">{safe_scope_json}</script>
</article>"""
