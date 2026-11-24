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
            "lead_clause": f"{us_read}% of US fourth-graders read proficiently in 2024, down four points since 2019,",
            "lead_rest": f"while real US median household income reached ${us_inc:,} (+{us_g:.1f}% over five years).",
            "focus_state": "",
            "focus_summary": f"US National: {us_read}% proficient nationwide (state range 21%–41%) · Select any state hex tile to inspect.",
            "callouts": [
                {"num": f"{us_read}%", "desc": "4th-graders at or above Proficient reading across all US public schools (2024)"},
                {"num": f"${us_inc:,}", "desc": "Real US median household income in 2024 inflation-adjusted dollars"},
                {"num": f"+{us_g:.1f}%", "desc": f"5-year real US household growth alongside {eq_pct:.1f}% equal-chance quintile baseline"},
            ],
        },
        "md": {
            "lead_clause": f"{md_read}% of Maryland fourth-graders read proficiently, four points ahead of the US average,",
            "lead_rest": f"paired with ${md_inc:,} median household income (+{md_g:.1f}% real 5-year growth).",
            "focus_state": "MD",
            "callouts": [
                {"num": f"{md_read}%", "desc": f"Maryland Grade 4 Proficient reading share (+{md_read - us_read} pts above US national rate)"},
                {"num": f"${md_inc:,}", "desc": "Maryland 2024 median household income rank top-three nationwide"},
                {"num": f"+{md_g:.1f}%", "desc": f"Maryland 5-year real household growth (+6.1% upward vs {eq_pct:.1f}% baseline)"},
            ],
        },
        "wy": {
            "lead_clause": f"{wy_read}% of Wyoming fourth-graders read proficiently, ranking top-quartile nationwide,",
            "lead_rest": f"while real median household income grew fastest at +{wy_g:.1f}% to ${wy_inc:,}.",
            "focus_state": "WY",
            "callouts": [
                {"num": f"{wy_read}%", "desc": f"Wyoming Grade 4 Proficient reading share (+{wy_read - us_read} pts above US national rate)"},
                {"num": f"${wy_inc:,}", "desc": "Wyoming 2024 median household income across rural and energy counties"},
                {"num": f"+{wy_g:.1f}%", "desc": f"Wyoming 5-year real income gain (+5.4% upward vs {eq_pct:.1f}% neutral baseline)"},
            ],
        },
    }
    safe_scope_json = json.dumps(scope_data, ensure_ascii=False).replace("</", "<\\/")

    hex_html = compile_spec(specs["hex_map"], rigor="L1", medium="m2", theme="white", include_wrapper=True, include_spec_drawer=False, chrome="embedded")
    dumb_html = compile_spec(specs["arrow_dumbbell"], rigor="L2", medium="m2", theme="white", include_wrapper=True, include_spec_drawer=False, chrome="embedded")
    mat_html = compile_spec(specs["mobility_matrix"], rigor="L2", medium="m2", theme="white", include_wrapper=True, include_spec_drawer=False, chrome="embedded")

    us_c = scope_data["us"]
    callout_cards = "".join(
        f'<div class="va-callout-stat" data-v22-callout="{idx}">'
        f'<span class="va-callout-num">{_esc(item["num"])}</span>'
        f'<p class="va-callout-desc">{_esc(item["desc"])}</p>'
        '<span class="va-callout-src">NAEP &amp; Census ACS Public Series</span>'
        "</div>"
        for idx, item in enumerate(us_c["callouts"])
    )

    code_snippet = (
        "# Reproducible summary verification (pure standard library)\n"
        f"us_read_pct, md_read_pct, wy_read_pct = {us_read}, {md_read}, {wy_read}\n"
        f"income_2024 = {{'US': {us_inc}, 'Maryland': {md_inc}, 'Wyoming': {wy_inc}}}"
    )

    return f"""
<div class="v9-stage-inner va-question-brief" id="v22-public-brief">
  <section class="va-brief-hero" id="v22-overview" aria-label="Question-First Brief Lead">
    <aside class="va-freshness-stamp" aria-label="Brief Freshness">
      <strong>Public Data Brief</strong><br/>
      Updated Nov 2026<br/>
      NAEP + Census ACS<br/>
      Equal-Chance Verified
    </aside>
    <div>
      <h1 class="va-brief-question">How have reading proficiency and household income mobility shifted across U.S. states?</h1>
      <div class="va-brief-toolbar">
        <div class="va-scope-bar" role="group" aria-label="Select jurisdiction scope">
          <button type="button" class="va-scope-btn is-active" data-v22-scope="us" aria-pressed="true">US National</button>
          <button type="button" class="va-scope-btn" data-v22-scope="md" aria-pressed="false">Maryland</button>
          <button type="button" class="va-scope-btn" data-v22-scope="wy" aria-pressed="false">Wyoming</button>
        </div>
        <div class="va-toolbar-joined va-format-toggle" role="group" aria-label="Select output format">
          <button type="button" class="va-seg-btn is-active" data-v22-format="brief" aria-pressed="true">Web Brief</button>
          <button type="button" class="va-seg-btn" data-v22-format="deck" aria-pressed="false">Briefing Slide (16:9)</button>
        </div>
      </div>
      <p class="va-lead-answer" data-v22-lead><span class="va-lead-highlight">{_esc(us_c["lead_clause"])}</span> {_esc(us_c["lead_rest"])}</p>
    </div>
  </section>

  <section class="va-editorial-callouts" aria-label="Key Public Metrics">{callout_cards}</section>

  <div class="va-brief-web">
    <section id="v22-map" aria-label="National State Hex Map">
      {hex_html}
    </section>

    <section class="va-brief-split" id="v22-dumbbell" aria-label="Trend Breakdown and Methodology">
      <article class="va-editorial-prose">
        <h2>Why unequal state boundaries distort small states</h2>
        <p>Standard geographic maps compress Delaware, Rhode Island, Washington, DC, and Maryland into slivers that conceal both <strong>{md_read}%</strong> proficiency and sample margins. Rendering all 51 jurisdictions as equal-area hexagons keeps click targets uniform while automatically inverting label ink whenever fill luminance crosses the contrast threshold.</p>
        <p>Comparing 2019 against 2024 shows diverging post-pandemic paths: Louisiana gained four points while national scores slipped from 35% to <strong>{us_read}%</strong>. Districts still operating under 2022–2023 pooled collections stay marked with an asterisk rather than being silently merged.</p>
        <p class="va-brief-signpost">Need slide-by-slide executive talking points? Switch to <strong>Briefing Slide (16:9)</strong> above or open <strong>Print Sheet</strong> to inspect clean archival pagination with zero sticky overlays.</p>
        <pre class="va-code-surface" tabindex="0" role="region" aria-label="Notebook check snippet"><code>{_esc(code_snippet)}</code></pre>
      </article>
      <div class="va-split-visual">{dumb_html}</div>
    </section>

    <section id="v22-matrix" aria-label="Income Distribution and Mobility Matrix">
      {mat_html}
    </section>
  </div>

  <div class="va-brief-slides va-slide-deck" hidden>
    <article class="va-slide-frame">
      <div class="va-slide-kicker">Slide 1 of 3 · Question-First Synthesis</div>
      <h2>State outcomes diverge sharply around the {us_read}% national reading baseline</h2>
      <p>Maryland sustains {md_read}% Grade 4 proficiency (${md_inc:,} median income, +{md_g:.1f}% real gain) and Wyoming posts {wy_read}% (${wy_inc:,}, +{wy_g:.1f}%), even as the national average softened from 35% to {us_read}% (+{us_g:.1f}% median household income gain).</p>
      <div class="va-table-region va-table-wrap" tabindex="0" role="region" aria-label="Executive Slide Metrics">
        <table class="booktabs qe-table">
          <thead><tr><th scope="col">Scope</th><th scope="col" class="num">Grade 4 Proficient</th><th scope="col" class="num">Median Income</th><th scope="col" class="num">5-Yr Real Growth</th></tr></thead>
          <tbody>
            <tr><th scope="row">US National</th><td class="num">{us_read}%</td><td class="num">${us_inc:,}</td><td class="num">+{us_g:.1f}%</td></tr>
            <tr><th scope="row">Maryland</th><td class="num">{md_read}%</td><td class="num">${md_inc:,}</td><td class="num">+{md_g:.1f}%</td></tr>
            <tr><th scope="row">Wyoming</th><td class="num">{wy_read}%</td><td class="num">${wy_inc:,}</td><td class="num">+{wy_g:.1f}%</td></tr>
          </tbody>
        </table>
      </div>
    </article>
    <article class="va-slide-frame">
      <div class="va-slide-kicker">Slide 2 of 3 · One-Chart Focal Evidence</div>
      <h2>Equal-area US 51-state map exposes small-state performance cleanly</h2>
      <p>All 50 states plus DC hold uniform visual area. Toggle the Web Brief view for interactive hex selection, full CSV export, and Markdown copy for AI briefing workflows.</p>
    </article>
    <article class="va-slide-frame">
      <div class="va-slide-kicker">Slide 3 of 3 · Appendix &amp; Methodological Guardrails</div>
      <h2>Equal-chance {eq_pct:.1f}% baseline &amp; vintage disclosure rules</h2>
      <p>Under random sorting, each income fifth captures {eq_pct:.1f}% of adult children. Dollar levels stay unshaded while growth rates use quiet diverging bands; prior-cycle pooled district series remain flagged with asterisks (*).</p>
    </article>
  </div>

  <script type="application/json" class="v22-scope-payload">{safe_scope_json}</script>
</div>"""
