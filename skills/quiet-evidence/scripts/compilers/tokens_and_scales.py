# SPDX-License-Identifier: Apache-2.0
"""Quiet UI Pillar 2 — Tokens, NAVAIR 1-2-5 / Log-Decade Scales, NIST SP 811 & SVG Halos."""

from __future__ import annotations

import html
import math
import re
from typing import Any

_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_RGB_RE = re.compile(r"^rgba?\(\s*(?:\d{1,3}%?\s*[,\s]\s*){2}\d{1,3}%?\s*(?:[,/]\s*(?:0|1|0?\.\d+)\s*)?\)$")

SUPERSCRIPT_MAP = str.maketrans("-+0123456789.", "⁻⁺⁰¹²³⁴⁵⁶⁷⁸⁹·")

_GREEK_MAP: dict[str, str] = {
    "Mod_sigma_y": "Mod σ_y", "Mod sigma_y": "Mod σ_y", "sigma_y": "σ_y", "sigma": "σ",
    "Delta_phi": "Δφ", "Delta": "Δ", "Lambda_LLR": "Λ_LLR", "Lambda": "Λ",
    "lambda": "λ", "tau": "τ", "phi": "φ", "alpha": "α", "beta": "β",
    "gamma": "γ", "theta": "θ", "omega": "ω", "mu": "μ",
    "y_hat_i": "ŷᵢ", "y_hat": "ŷ", "y_i": "yᵢ", "x_i": "xᵢ",
    "X_bar": "X̄", "x_bar": "x̄", "R_bar": "R̄",
}
_GREEK_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in _GREEK_MAP) + r")\b")
_SCI_RE = re.compile(r"\b(\d+(?:\.\d+)?)[eE]([+-]?\d+)\b")
_POW_RE = re.compile(r"\^\(?(-?\d+(?:\.\d+)?)\)?")
_SUB_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-zσΔΛαβγθωλφŷX̄R̄])_([A-Za-z0-9]{1,6})\b")

SI_PREFIXES: tuple[tuple[int, str], ...] = (
    (-15, "f"), (-12, "p"), (-9, "n"), (-6, "µ"), (-3, "m"),
    (0, ""), (3, "k"), (6, "M"), (9, "G"), (12, "T"),
)

SERIES_STYLES: tuple[dict[str, str], ...] = (
    {"stroke": "var(--accent-focal)", "dash": "none", "marker": "circle", "fill": "var(--accent-focal)"},
    {"stroke": "var(--text-secondary)", "dash": "6,3", "marker": "square", "fill": "var(--bg-canvas)"},
    {"stroke": "var(--status-ok)", "dash": "2,3", "marker": "triangle", "fill": "var(--status-ok)"},
    {"stroke": "var(--tint-violet-fg)", "dash": "8,3,2,3", "marker": "diamond", "fill": "var(--bg-canvas)"},
    {"stroke": "var(--status-warn)", "dash": "4,4", "marker": "circle", "fill": "var(--bg-canvas)"},
)

PEDAGOGICAL_TERMS: dict[str, dict[str, str]] = {
    "tx": {"fg": "var(--tint-indigo-fg)", "bg": "var(--tint-indigo-bg)"},
    "gain_tx": {"fg": "var(--tint-emerald-fg)", "bg": "var(--tint-emerald-bg)"},
    "path_loss": {"fg": "var(--tint-amber-fg)", "bg": "var(--tint-amber-bg)"},
    "gain_rx": {"fg": "var(--tint-violet-fg)", "bg": "var(--tint-violet-bg)"},
    "rx": {"fg": "var(--accent-focal)", "bg": "var(--tint-indigo-bg)"},
    "noise": {"fg": "var(--tint-rose-fg)", "bg": "var(--tint-rose-bg)"},
}

ANNUNCIATOR_STATES: dict[str, dict[str, str]] = {
    "NOMINAL": {"pill": "NOMINAL", "fg": "var(--status-ok)", "bg": "var(--status-ok-bg)", "cls": "va-badge-ok"},
    "ADVISORY": {"pill": "ADVISORY", "fg": "var(--tint-indigo-fg)", "bg": "var(--tint-indigo-bg)", "cls": "qe-badge-info"},
    "WARNING": {"pill": "CAUTION", "fg": "var(--status-warn)", "bg": "var(--status-warn-bg)", "cls": "va-badge-warn"},
    "CRITICAL": {"pill": "TRIPWIRE", "fg": "var(--status-danger)", "bg": "var(--status-err-bg)", "cls": "va-badge-err"},
    "STALE": {"pill": "STALE DATA", "fg": "var(--text-muted)", "bg": "var(--bg-elevated)", "cls": "va-badge-neutral"},
    "FAULT": {"pill": "SENSOR FAULT", "fg": "var(--status-danger)", "bg": "var(--status-err-bg)", "cls": "va-badge-err"},
}

SAFE_TOKENS: set[str] = {
    "--bg-shell", "--bg-canvas", "--bg-surface", "--bg-card", "--bg-elevated",
    "--bg-header", "--text-primary", "--text-main", "--text-secondary", "--text-dim",
    "--text-muted", "--border-hairline", "--border-grid", "--border-strong",
    "--accent-primary", "--accent-focal", "--status-ok", "--status-ok-bg",
    "--status-warn", "--status-warn-bg", "--status-danger", "--status-err",
    "--status-err-bg", "--tint-indigo-bg", "--tint-indigo-fg",
    "--tint-emerald-bg", "--tint-emerald-fg", "--tint-amber-bg", "--tint-amber-fg",
    "--tint-rose-bg", "--tint-rose-fg", "--tint-violet-bg", "--tint-violet-fg",
}


def esc(text: Any) -> str:
    """Escape text safely for HTML/SVG without introducing raw backticks."""
    return html.escape(str(text), quote=True)


def format_math_unicode(text: Any) -> str:
    """Format ASCII math notation into Unicode scientific typography."""
    s = str(text)
    s = _SCI_RE.sub(lambda m: f"{m.group(1)} × 10{m.group(2).lstrip('+').translate(SUPERSCRIPT_MAP)}", s)
    s = _POW_RE.sub(lambda m: m.group(1).lstrip("+").translate(SUPERSCRIPT_MAP), s)
    s = _GREEK_RE.sub(lambda m: _GREEK_MAP[m.group(1)], s)
    s = re.sub(r"\s*\*\s*", " ", s)
    return s.replace(" - ", " − ")


def format_math_html(text: Any) -> str:
    """Format ASCII math notation into escaped HTML with <sub> subscripts."""
    uni = esc(format_math_unicode(text))
    return _SUB_TOKEN_RE.sub(r"\1<sub>\2</sub>", uni)


def format_math_svg(text: Any, sub_size: float = 8.8) -> str:
    """Format ASCII math notation into escaped SVG markup with <tspan> subscripts."""
    uni = esc(format_math_unicode(text))
    return _SUB_TOKEN_RE.sub(
        lambda m: f'{m.group(1)}<tspan baseline-shift="sub" font-size="{sub_size:.1f}">{m.group(2)}</tspan>',
        uni,
    )


def resolve_token(value: str | None, fallback: str = "var(--accent-focal)") -> str:
    """Resolve CSS custom property against canonical Quiet UI tokens."""
    if not isinstance(value, str) or not value:
        return fallback
    val = value.strip()
    if val.startswith("var(") and val.endswith(")"):
        inner = val[4:-1].split(",")[0].strip()
        return f"var({inner})" if inner in SAFE_TOKENS else fallback
    if val in SAFE_TOKENS:
        return f"var({val})"
    if val == "currentColor" or _HEX_RE.match(val) or _RGB_RE.match(val):
        return val
    return fallback


def resolve_term_colors(term_key: str | None) -> dict[str, str]:
    """Return Pedagogical Flow role foreground/background tokens for a data-term."""
    if not term_key:
        return {"fg": "var(--accent-focal)", "bg": "var(--bg-elevated)"}
    return PEDAGOGICAL_TERMS.get(term_key, {"fg": "var(--accent-focal)", "bg": "var(--tint-indigo-bg)"})


def _snap_sig(val: float, step: float) -> float:
    if abs(val) < step * 1e-9:
        return 0.0
    return float(f"{val:.12g}")


def compute_linear_125_scale(
    vmin: float,
    vmax: float,
    target_ticks: int = 6,
) -> dict[str, Any]:
    """Compute NAVAIR FTM-108 1-2-5 x 10^n major and minor ticks."""
    if not (math.isfinite(vmin) and math.isfinite(vmax)):
        vmin, vmax = 0.0, 1.0
    if vmin > vmax:
        vmin, vmax = vmax, vmin
    if math.isclose(vmin, vmax, rel_tol=1e-12, abs_tol=0.0):
        pad = abs(vmin) * 0.1 if vmin != 0.0 else 1.0
        vmin -= pad
        vmax += pad
    span = vmax - vmin
    if not math.isfinite(span) or span <= 0.0:
        vmin, vmax, span = -1.0, 1.0, 2.0
    rough = span / max(target_ticks, 2)
    exp = math.floor(math.log10(rough))
    frac = rough / (10.0 ** exp)
    if frac < math.sqrt(2.0):
        c = 1.0
    elif frac < math.sqrt(10.0):
        c = 2.0
    elif frac < math.sqrt(50.0):
        c = 5.0
    else:
        c = 1.0
        exp += 1
    step = c * (10.0 ** exp)
    start = math.floor(vmin / step + 1e-9) * step
    end = math.ceil(vmax / step - 1e-9) * step
    if end <= start:
        end = start + step

    majors: list[float] = []
    cur = start
    limit = 0
    while cur <= end + step * 1e-6 and limit < 40:
        majors.append(_snap_sig(cur, step))
        cur += step
        limit += 1

    sub_div = 4 if c == 2.0 else 5
    minor_step = step / sub_div
    minors: list[float] = []
    for i in range(len(majors) - 1):
        for k in range(1, sub_div):
            minors.append(_snap_sig(majors[i] + k * minor_step, minor_step))

    return {
        "min": majors[0],
        "max": majors[-1],
        "step": step,
        "mantissa": int(c),
        "exponent": exp,
        "majors": majors,
        "minors": minors,
    }


def compute_log_decade_scale(vmin: float, vmax: float) -> dict[str, Any]:
    """Compute integer log10 decades and mandatory 2..9 minor decade ticks."""
    if not (math.isfinite(vmin) and math.isfinite(vmax)):
        vmin, vmax = 1.0, 10.0
    if vmin > vmax:
        vmin, vmax = vmax, vmin
    if vmax <= 0.0:
        lo, hi = 1.0, 10.0
    else:
        lo = vmin if vmin > 0.0 else max(1e-30, vmax * 1e-4)
        hi = max(vmax, lo * 10.0)
    exp_min = math.floor(math.log10(lo) + 1e-9)
    exp_max = math.ceil(math.log10(hi) - 1e-9)
    if exp_max <= exp_min:
        exp_max = exp_min + 1
    if exp_max - exp_min > 18:
        exp_min = exp_max - 18
    majors = [10.0 ** k for k in range(exp_min, exp_max + 1)]
    minors: list[float] = []
    for k in range(exp_min, exp_max):
        base = 10.0 ** k
        for m in range(2, 10):
            minors.append(m * base)
    return {
        "min": majors[0],
        "max": majors[-1],
        "exp_min": exp_min,
        "exp_max": exp_max,
        "majors": majors,
        "minors": minors,
    }


def select_engineering_prefix(max_abs: float, unit: str) -> tuple[float, str]:
    """Select SI engineering prefix factor and scaled unit keeping ticks in [0.1, 999]."""
    non_prefix_units = {"1", "", "%", "dB", "dBm", "dBc", "dBc/Hz", "°C", "°", "K"}
    if not unit or unit in non_prefix_units or not math.isfinite(max_abs) or max_abs <= 0:
        return 1.0, unit
    if len(unit) > 1 and unit[0] in {"f", "p", "n", "µ", "u", "m", "k", "M", "G", "T"} and unit not in {"ms", "mV", "mA", "mrad", "mm"}:
        return 1.0, unit
    if unit in {"ms", "mV", "mA", "mrad", "mm", "µs", "ps", "ns", "GHz", "MHz", "kHz", "kΩ", "km"}:
        return 1.0, unit
    exp3 = int(math.floor(math.log10(max_abs) / 3.0) * 3)
    exp3 = max(-15, min(12, exp3))
    for p_exp, p_sym in SI_PREFIXES:
        if p_exp == exp3:
            return 10.0 ** (-p_exp), f"{p_sym}{unit}"
    return 1.0, unit


def format_tick_numeral(val: float, is_log: bool = False, step: float | None = None) -> str:
    """Format axis tick numeral cleanly without floating-point artifacts."""
    if not math.isfinite(val):
        return "0"
    if is_log:
        exp = round(math.log10(max(val, 1e-30)))
        if abs(exp) <= 2 and val >= 0.01 and val == round(val, 2):
            return f"{val:g}"
        return "10" + str(exp).translate(SUPERSCRIPT_MAP)
    if val == 0.0 or (step is not None and step > 0 and abs(val) < step * 1e-9):
        return "0"
    if step is not None and step > 0:
        dec = max(0, -math.floor(math.log10(step) + 1e-9))
        if abs(val) >= 1e5 or (0 < abs(val) < 1e-3):
            return f"{val:.2e}"
        dec = min(dec, 6)
        formatted = f"{val:.{dec}f}"
        return formatted.rstrip("0").rstrip(".") if "." in formatted and dec > 2 else formatted
    return f"{val:g}"


def format_quantity_header(symbol: str, name: str | None = None, unit: str = "") -> str:
    """Format NIST SP 811 quotient or parenthetical header (never `f [GHz]`)."""
    clean_u = unit.strip()
    if not clean_u or clean_u == "1":
        return f"{name}, {symbol}" if name and name != symbol else symbol
    if name and name != symbol:
        return f"{name}, {symbol} / {clean_u}"
    return f"{symbol} / {clean_u}"


def format_value_unit(val: float | str, unit: str = "", uncertainty: float | None = None, decimals: int | None = None) -> str:
    """Format physical reading with NIST SP 811 non-breaking space and parenthetical uncertainty."""
    if isinstance(val, (int, float)):
        if decimals is None and uncertainty is not None and uncertainty > 0:
            dec = max(0, min(6, -math.floor(math.log10(uncertainty) + 1e-9) + 1))
            val_str = f"{val:.{dec}f}"
            unc_str = f"{uncertainty:.{dec}f}"
        elif decimals is not None:
            val_str = f"{val:.{decimals}f}"
            unc_str = f"{uncertainty:.{decimals}f}" if uncertainty is not None else ""
        else:
            val_str = f"{val:g}"
            unc_str = f"{uncertainty:g}" if uncertainty is not None else ""
    else:
        val_str = str(val)
        unc_str = f"{uncertainty:g}" if uncertainty is not None else ""

    clean_u = unit.strip()
    sep = "" if clean_u in {"°", "′", "″", "%"} else "\u00a0"
    if unc_str:
        return f"({val_str} \u00b1 {unc_str}){sep}{clean_u}" if clean_u and clean_u != "1" else f"{val_str} \u00b1 {unc_str}"
    if clean_u and clean_u != "1":
        return f"{val_str}{sep}{clean_u}"
    return val_str


def halo_text(
    x: float,
    y: float,
    text: str,
    anchor: str = "start",
    size: float = 11.5,
    weight: str = "500",
    fill: str = "var(--text-primary)",
    font: str = "var(--font-mono)",
    halo: bool = True,
    cls: str = "",
    attrs: str = "",
    math: bool = False,
) -> str:
    """Emit SVG <text> with paint-order stroke halo and >= 11px floor."""
    classes = " ".join(part for part in (cls, "va-svg-halo-text" if halo else "") if part)
    cls_attr = f' class="{esc(classes)}"' if classes else ""
    halo_attrs = ' paint-order="stroke fill" stroke="var(--bg-surface)" stroke-width="3.2" stroke-linejoin="round"' if halo else ""
    extra = f" {attrs.strip()}" if attrs.strip() else ""
    body = format_math_svg(text, size * 0.78) if math else esc(text)
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{font}" font-size="{size:.1f}" font-weight="{weight}" '
        f'fill="{fill}"{cls_attr}{halo_attrs}{extra}>{body}</text>'
    )


def pill_halo_text(
    x: float,
    y: float,
    text: str,
    anchor: str = "middle",
    size: float = 11.5,
    weight: str = "700",
    fill: str = "var(--text-primary)",
    border: str = "var(--border-hairline)",
    x_bounds: tuple[float, float] = (4.0, 716.0),
    cls: str = "",
    attrs: str = "",
    math: bool = True,
) -> str:
    """Emit opaque --bg-surface rounded <rect> pill behind SVG <text> so strokes never cross text."""
    plain = format_math_unicode(text) if math else str(text)
    vis = _SUB_TOKEN_RE.sub(r"\1\2", plain) if math else plain
    w = max(32.0, len(vis) * (size * 0.65) + 14.0)
    rx0 = x - w if anchor == "end" else (x - w / 2.0 if anchor == "middle" else x)
    rx0 = max(x_bounds[0], min(x_bounds[1] - w, rx0))
    tx = rx0 + w / 2.0
    pill = f'<rect class="qe-label-pill" x="{rx0:.1f}" y="{y - 13.5:.1f}" width="{w:.1f}" height="19.0" rx="4" fill="var(--bg-surface)" stroke="{border}" stroke-width="0.9"/>'
    txt = halo_text(tx, y, text, anchor="middle", size=size, weight=weight, fill=fill, halo=False, cls=cls, attrs=attrs, math=math)
    return pill + txt


def render_marker(cx: float, cy: float, glyph: str, size: float, stroke: str, fill: str) -> str:
    """Emit discrete epistemic geometric marker glyph for measured points."""
    r = size / 2.0
    if glyph == "square":
        return f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{size:.1f}" height="{size:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    if glyph == "triangle":
        pts = f"{cx:.1f},{cy - r - 0.8:.1f} {cx + r + 0.6:.1f},{cy + r:.1f} {cx - r - 0.6:.1f},{cy + r:.1f}"
        return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    if glyph == "diamond":
        pts = f"{cx:.1f},{cy - r - 0.8:.1f} {cx + r + 0.8:.1f},{cy:.1f} {cx:.1f},{cy + r + 0.8:.1f} {cx - r - 0.8:.1f},{cy:.1f}"
        return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def avoid_label_overlaps(items: list[dict[str, Any]], min_y: float = 16.0, max_y: float = 340.0, step_y: float = 19.0) -> list[dict[str, Any]]:
    """Nudge floating label boxes vertically to guarantee 0 text-on-text overlaps."""
    placed: list[tuple[float, float, float, float]] = []
    out: list[dict[str, Any]] = []
    for item in items:
        x, y = float(item["x"]), float(item["y"])
        w = float(item.get("w", max(44.0, len(format_math_unicode(item.get("text", ""))) * 7.5 + 14.0)))
        h = float(item.get("h", 19.0))
        anchor = item.get("anchor", "start")
        x0 = x - w if anchor == "end" else (x - w / 2.0 if anchor == "middle" else x)
        x1 = x0 + w

        def _collides(cand_y: float) -> bool:
            y0, y1 = cand_y - h, cand_y + 4.0
            return any(not (x1 + 4.0 < px0 or x0 - 4.0 > px1 or y1 + 3.0 < py0 or y0 - 3.0 > py1) for px0, py0, px1, py1 in placed)

        best_y = y
        if _collides(best_y):
            for k in range(1, 14):
                for sign in (-1, 1):
                    cand = y + sign * k * step_y
                    if min_y <= cand <= max_y and not _collides(cand):
                        best_y = cand
                        break
                else:
                    continue
                break
        placed.append((x0, best_y - h, x1, best_y + 4.0))
        out.append({**item, "y": best_y})
    return out


def render_test_condition_strip(env: dict[str, Any] | None, rigor: str) -> str:
    """Render NIST/NAVAIR/Clinical/Industrial Condition Header Block for L2/L3 visuals."""
    if not env or rigor == "L1":
        return ""
    fields: list[tuple[str, str]] = []
    for key, lbl in (("dut_id", "DUT"), ("unit_id", "Unit"), ("cohort_id", "Cohort"), ("firmware_version", "FW"), ("standard_id", "Std")):
        if env.get(key):
            fields.append((lbl, str(env[key])))
    if env.get("ambient_temperature_c") is not None:
        fields.append(("T_amb", format_value_unit(env["ambient_temperature_c"], "°C", env.get("temperature_uncertainty_c"), decimals=1)))
    elif env.get("temperature_c") is not None:
        fields.append(("T_amb", format_value_unit(env["temperature_c"], "°C", decimals=1)))
    if env.get("reference_oscillator") or env.get("reference_clock"):
        fields.append(("Timebase", str(env.get("reference_oscillator") or env.get("reference_clock"))))
    if env.get("sampling_rate_hz") or env.get("sample_rate_hz"):
        sr = float(env.get("sampling_rate_hz") or env.get("sample_rate_hz"))
        factor, s_unit = select_engineering_prefix(sr, "Hz")
        fields.append(("f_s", format_value_unit(sr * factor, s_unit, decimals=2)))
    if env.get("cpk") is not None:
        fields.append(("C_pk", f"{float(env['cpk']):.2f}"))
    if env.get("sample_subgroup_size") is not None:
        fields.append(("n_sub", str(env["sample_subgroup_size"])))
    if env.get("calibration_id"):
        fields.append(("Cal Cert", str(env["calibration_id"])))
    if not fields:
        return ""
    if rigor == "L2":
        fields = fields[:3]
    cells = "".join(
        f'<div class="qe-cond-item"><span class="qe-cond-lbl qe-unit">{format_math_html(k)}</span>'
        f'<span class="qe-cond-val va-nums">{esc(v)}</span></div>'
        for k, v in fields
    )
    return f'<div class="va-test-condition-block qe-cond-strip" role="note" aria-label="Test Conditions">{cells}</div>'
