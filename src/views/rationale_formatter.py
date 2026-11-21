# SPDX-License-Identifier: Apache-2.0
"""Plain-English formatting and jargon scrubbing for Quiet UI v9.0 Design Rationale."""

from __future__ import annotations

import re
from typing import Any

_MEDIUM_PLAIN: dict[str, str] = {
    "M1": "Print Sheet",
    "M2": "Article / Document",
    "M3": "Interactive App",
    "M4": "Operator Console",
    "M5": "Wall Display",
    "M6": "Optical HUD",
    "M7": "Smart-Glass Overlay",
}

_RIGOR_PLAIN: dict[str, str] = {
    "L1": "Executive Summary",
    "L2": "Operational Spec",
    "L3": "Detailed Metrology",
}

_TEMPO_PLAIN: dict[str, str] = {
    "T1": "Immediate Glance (5–15 s)",
    "T2": "Decision Brief (1–3 min)",
    "T3": "Deep Analysis (10–45 min)",
    "T2/T3": "Dual-Speed Brief & Deep Analysis",
}

_VIEW_SLUG_PLAIN: dict[str, str] = {
    "v01-icu-bedside-terminal": "v01 · ICU Bedside Terminal",
    "v02-trial-regulatory-brief": "v02 · Trial Regulatory Brief",
    "v03-patient-recovery-companion": "v03 · Patient Recovery Guide",
    "v04-sre-incident-workbench": "v04 · SRE Incident Workbench",
    "v05-zero-trust-ato-spec": "v05 · Zero-Trust Security Spec",
    "v06-ai-drift-and-lineage-ide": "v06 · AI Calibration & Lineage",
    "v07-grid-scada-poi-console": "v07 · Grid SCADA POI Console",
    "v08-plant-floor-wall-kiosk": "v08 · Plant-Floor Wall Display",
    "v09-spc-quality-and-modbus-report": "v09 · SPC Quality & Modbus Audit",
    "v10-civic-capital-budget-deck": "v10 · Civic Capital Budget",
    "v11-treasury-stress-test-solver": "v11 · Treasury Stress Solver",
    "v12-stem-interactive-lab": "v12 · STEM RC Discharge Lab",
    "v13-propulsion-archival-monograph": "v13 · Propulsion Monograph",
    "v14-fieldbus-and-scope-debugger": "v14 · CAN-FD Fieldbus Debugger",
    "v15-collimated-flight-hud": "v15 · Collimated Flight HUD",
    "v16-transparent-window-overlay": "v16 · Smart-Glass Overlay Pod",
    "v17-picture-frame-home-kiosk": "v17 · Picture-Frame Home Kiosk",
    "v18-home-assistant-companion-console": "v18 · Home Assistant Companion Console",
    "v19-product-roadmap-and-triage": "v19 · Product Release Roadmap & Triage",
    "v20-student-capstone-lab-report": "v20 · Student Capstone Lab Report",
    "v21-field-anomaly-escalation-tsn": "v21 · Field Anomaly Escalation Note",
}

_NAV_PLAIN: dict[str, str] = {
    "N0": "immersive full-canvas view",
    "N1": "minimal pill navigation",
    "N2": "left rail navigation",
    "N3": "hierarchical sidebar",
    "N4": "compact action header",
}

_RUBRIC_PLAIN_RULES: tuple[tuple[str, str], ...] = (
    ("Conservation", "Numerical Consistency & Units"),
    ("Bezier", "Honest Discrete Data Plotting"),
    ("Spline", "Honest Discrete Data Plotting"),
    ("Calibration", "Instrument Calibration & Traceability"),
    ("Baseline", "Baseline & Safety Bounds"),
    ("Cognit", "Clarity & Reader Pacing"),
    ("Term", "Equation-to-Plot Highlighting"),
    ("Error Bars", "Uncertainty Whiskers & Residuals"),
    ("Residual", "Uncertainty Whiskers & Residuals"),
    ("Audience", "Audience & Format Suitability"),
    ("Interlock", "Two-Step Safety Interlock"),
    ("LOTO", "Two-Step Safety Interlock"),
    ("Enclave", "Network Boundary Separation"),
    ("FIPS", "Cryptographic Policy Enforcement"),
    ("Typography", "Type Scale & Legibility"),
    ("Contrast", "Daylight & Low-Light Contrast"),
    ("Sightline", "Unobstructed Sightline Geometry"),
    ("Dropout", "Missing-Signal Gap Honesty"),
    ("Bus", "Fieldbus Topology & Termination"),
    ("Trade", "Budget & Risk Trade-Space"),
)

_RUBRIC_CODE_RE = re.compile(
    r"\b(?:CL|CR|CC|PR|ER|LR|SR|TR|TRG|SC|MB)-[A-Za-z0-9]+(?:\s*(?:&|,|\.\.|/|and)\s*(?:(?:CL|CR|CC|PR|ER|LR|SR|TR|TRG|SC|MB)-)?[A-Za-z0-9]+)*\b"
)
_JSON_PATH_RE = re.compile(
    r"`?(?:evidence/)?([a-z0-9_*]+)\.json`?(?:\s*\([^)]*\$\.[^)]*\))?"
)
_ROW_STATUS_RE = re.compile(r"\(\s*_row_status\s*:\s*([a-z]+)\s*\)", re.I)
_VIEW_SLUG_RE = re.compile(r"\bv\d{2}-[a-z0-9]+(?:-[a-z0-9]+)+\b")
_TEMPO_CODE_RE = re.compile(r"\b(?:T2\s*/\s*T3|T1|T2|T3)\b")
_RIGOR_CODE_RE = re.compile(r"\b(L[123])\b")
_MEDIUM_CODE_RE = re.compile(r"\b(M[1-7])\b")
_NAV_CODE_RE = re.compile(r"\b(N[0-4])\b")
_HW_SLUG_RE = re.compile(r"\b(?:PANEL-MAIN-200A|EVSE-GARAGE-48A|LOCK-FRONT-01|GARAGE-BAY-01|ZONE-LIVING|ZONE-STUDY)\b")
_LOWER_SNAKE_RE = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b")

_UNIT_SUFFIXES: dict[str, str] = {
    "mw": "MW", "hz": "Hz", "pct": "%", "ms": "ms", "us": "µs",
    "v": "V", "s": "s", "mmhg": "mmHg", "ohm": "Ω", "m": "m",
    "hrs": "hr", "hr": "hr", "usd": "USD", "bps": "bps", "hex": "Hex",
}


def humanize_identifier(raw: Any) -> str:
    """Turn lowercase snake_case keys into concise Title Case names."""
    s = str(raw or "").strip()
    if not s or "_" not in s:
        return s
    parts = [p for p in s.split("_") if p]
    acronyms = {"icu", "bess", "poi", "spc", "p99", "ece", "canfd", "map", "spo2", "oee", "rc", "bte"}
    if len(parts) > 1 and parts[-1].lower() in _UNIT_SUFFIXES:
        unit = _UNIT_SUFFIXES[parts[-1].lower()]
        body = " ".join(p.upper() if p.lower() in acronyms else p.capitalize() for p in parts[:-1])
        return f"{body} ({unit})"
    return " ".join(p.upper() if p.lower() in acronyms else p.capitalize() for p in parts)


def scrub_prose(text: Any) -> str:
    """Convert internal markup, JSON filenames, tempo codes, view slugs, and taxonomy codes into plain English."""
    s = str(text or "").strip()
    if not s:
        return ""
    s = re.sub(r"\bV\d{2}:\s*", "", s)
    s = s.replace("**", "").replace("`", "").replace("$", "")
    s = s.replace("<->", "↔").replace("->", "→")
    for raw_m, sym_m in (("X_bar", "X̄"), ("C_pk", "Cpk"), ("p_hat", "p̂"), ("f_obs", "observed frequency (fₒ)"), ("u_y", "uᵧ"), ("U_y", "uᵧ"), ("U_Y", "uᵧ")):
        s = s.replace(raw_m, sym_m)
    s = _ROW_STATUS_RE.sub(lambda m: "(status: Review Needed)" if m.group(1).lower() == "warn" else f"(status: {m.group(1).title()})", s)
    s = _JSON_PATH_RE.sub(lambda m: "supporting data specs" if "*" in m.group(1) else humanize_identifier(m.group(1)) + " spec", s)
    s = _VIEW_SLUG_RE.sub(lambda m: _VIEW_SLUG_PLAIN.get(m.group(0), m.group(0).replace("-", " ").title()), s)
    s = _TEMPO_CODE_RE.sub(lambda m: _TEMPO_PLAIN.get(re.sub(r"\s+", "", m.group(0)), m.group(0)), s)
    s = _RIGOR_CODE_RE.sub(lambda m: _RIGOR_PLAIN.get(m.group(1), m.group(1)), s)
    s = _MEDIUM_CODE_RE.sub(lambda m: _MEDIUM_PLAIN.get(m.group(1), m.group(1)), s)
    s = _NAV_CODE_RE.sub(lambda m: _NAV_PLAIN.get(m.group(1), m.group(1)), s)
    s = re.sub(r"\bBooktabs\b", "aligned ledger", s, flags=re.I)
    s = _HW_SLUG_RE.sub(lambda m: {"PANEL-MAIN-200A": "Main Panel", "EVSE-GARAGE-48A": "Garage Charger", "LOCK-FRONT-01": "Front Door", "GARAGE-BAY-01": "Garage Door", "ZONE-LIVING": "Living Room", "ZONE-STUDY": "Study"}.get(m.group(0), m.group(0)), s)
    s = _RUBRIC_CODE_RE.sub("", s)
    s = re.sub(r"\s*\(\s*clear\s*\)", "", s, flags=re.I)
    s = re.sub(r"\(\s*[·,&/\s]*\)", "", s)
    s = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", s))
    s = re.sub(r"\b(?:Quiet[- ]Bridge|QUIET[- ]BRIDGE|Murder[- ]Board|MURDER[- ]BOARD)\b", "Design Review", s)
    s = re.sub(r"\bScrubbed\b", "Clarified", s, flags=re.I)
    s = _LOWER_SNAKE_RE.sub(lambda m: humanize_identifier(m.group(1)), s)
    s = re.sub(r"\s{2,}", " ", s).strip(" ·,:-")
    return s


def humanize_rubric_title(raw_rubric: Any, finding: Any = "") -> str:
    """Convert cryptic audit gate / rubric code headers into human-readable check names."""
    s = scrub_prose(raw_rubric)
    paren = re.search(r"\(([^()]{3,})\)", s)
    if paren and re.search(r"[A-Za-z]{3,}", paren.group(1)):
        return paren.group(1).strip()
    cleaned = re.sub(r"^[\s&:·\-]+|[\s&:·\-]+$", "", s)
    if len(cleaned) >= 4 and not re.fullmatch(r"[A-Z0-9\s.&\-/]+", cleaned):
        return cleaned
    joined = f"{raw_rubric} {finding}"
    for needle, label in _RUBRIC_PLAIN_RULES:
        if needle.lower() in joined.lower():
            return label
    return "Design Quality Check"


def format_vector_summary(vw: dict[str, Any]) -> str:
    """Format presenter -> audience metadata in plain English without framework codes."""
    presenter = scrub_prose(vw.get("presenter", ""))
    audience = scrub_prose(vw.get("audience", ""))
    meds = [_MEDIUM_PLAIN.get(m, m) for m in vw.get("mediums", [])]
    raw_tempos = [str(t).strip().upper() for t in vw.get("tempos", []) if str(t).strip()]
    if set(raw_tempos) == {"T2", "T3"} or raw_tempos == ["T2/T3"]:
        tempo_str = _TEMPO_PLAIN["T2/T3"]
    else:
        mapped = [_TEMPO_PLAIN.get(t, scrub_prose(t)) for t in raw_tempos]
        tempo_str = " & ".join(dict.fromkeys(p for p in mapped if p))
    rigor = _RIGOR_PLAIN.get(str(vw.get("rigor_level", "")).upper(), "")
    parts = [f"{presenter} to {audience}".strip()]
    if tempo_str:
        parts.append(tempo_str)
    if meds:
        parts.append(" & ".join(meds))
    if rigor:
        parts.append(rigor)
    return " · ".join(p for p in parts if p)


def format_ledger_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Convert raw ledger metric_ids and file sources to readable labels."""
    out: list[dict[str, str]] = []
    for row in rows:
        out.append({
            "metric_id": humanize_identifier(row.get("metric_id", "")),
            "canonical_value": str(row.get("canonical_value", "")),
            "unit": str(row.get("unit", "")),
            "views": scrub_prose(row.get("views", "")),
        })
    return out
