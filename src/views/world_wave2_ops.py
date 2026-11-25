"""Quiet UI v9.7.0 Wave 2 view builders: Semantic Config Diff (v23) and Triage Desk (v24)."""
from __future__ import annotations

import html
from typing import Iterable

_V23_DIFF_ROWS: tuple[tuple[str, str, str, str, str, str, str], ...] = (
    ("mtls.client_cert_pinning", "optional_ca", "strict_spki_pin", "Drops unpinned legacy peers (Preflight gate)", "2 canary -> 14", "BREAKING", "security"),
    ("tls.min_version", "TLSv1.2", "TLSv1.3", "Removes RSA key exchange (+1 revision)", "14 / 14", "MODERATE", "security"),
    ("ingress.header_sanitization", "permissive", "strict_rfc9110", "Rejects duplicate Host/TE smuggling", "14 / 14", "LOW", "security"),
    ("ratelimit.burst_rps", "450 req/s", "600 req/s", "+150 req/s (+33.3% burst headroom)", "2 / 14 canary", "LOW", "capacity"),
    ("upstream.connect_timeout_ms", "2500 ms", "1200 ms", "-1300 ms (-52.0% faster failover)", "2 / 14 canary", "MODERATE", "capacity"),
    ("conn_pool.max_idle_conns", "256", "384", "+128 warm sockets (+50.0% reuse)", "14 / 14", "LOW", "capacity"),
    ("tls.ocsp_stapling", "required", "required", "Unchanged baseline control", "14 / 14", "UNCHANGED", "context"),
    ("mtls.crl_refresh_sec", "300 s", "300 s", "Unchanged revocation interval", "14 / 14", "UNCHANGED", "context"),
    ("ratelimit.window_sec", "60 s", "60 s", "Unchanged sliding window", "14 / 14", "UNCHANGED", "context"),
    ("upstream.retry_idempotent", "2 attempts", "2 attempts", "Unchanged safe GET/HEAD policy", "14 / 14", "UNCHANGED", "context"),
    ("audit.log_sample_rate", "100 %", "100 %", "Unchanged full audit capture", "14 / 14", "UNCHANGED", "context"),
    ("cipher.fips_mode", "FIPS-140-3", "FIPS-140-3", "Unchanged validated module lock", "14 / 14", "UNCHANGED", "context"),
)

_V23_COHORTS: tuple[tuple[str, str, float, str], ...] = (
    ("ewr-edge-01 (Canary 1)", "Canary r42", 7.4, "var(--accent-focal)"),
    ("fra-edge-02 (Canary 2)", "Canary r42", 6.9, "var(--accent-focal)"),
    ("NA West/Central (5 clusters)", "Held r41", 36.1, "var(--text-muted)"),
    ("EU Core (4 clusters)", "Held r41", 28.8, "var(--text-muted)"),
    ("APAC Edge (3 clusters)", "Held r41", 20.8, "var(--text-muted)"),
)

_V24_BUCKETS: tuple[tuple[str, int, int, int, int], ...] = (
    ("14:00", 0, 0, 0, 1), ("14:02", 0, 1, 0, 1), ("14:05", 0, 0, 1, 0), ("14:07", 0, 1, 0, 1),
    ("14:10", 0, 0, 1, 0), ("14:12", 0, 1, 0, 1), ("14:15", 0, 1, 1, 0), ("14:17", 0, 1, 1, 0),
    ("14:20", 2, 1, 1, 0), ("14:22", 2, 2, 0, 0), ("14:25", 2, 1, 1, 0), ("14:27", 1, 1, 1, 0),
    ("14:30", 1, 1, 0, 0), ("14:32", 1, 1, 1, 0), ("14:35", 0, 1, 1, 0), ("14:37", 0, 0, 1, 1),
    ("14:40", 0, 1, 0, 1), ("14:42", 0, 0, 1, 1), ("14:45", 0, 0, 0, 1), ("14:47", 0, 0, 0, 1),
    ("14:50", 0, 0, 0, 2), ("14:52", 0, 0, 0, 1), ("14:55", 0, 0, 0, 1), ("14:57", 0, 0, 0, 1),
)

_V24_SERVICES: tuple[str, ...] = ("checkout-api", "auth-gateway", "token-signer", "tls-ingress")
_V24_CALLERS: tuple[str, ...] = ("edge-proxy-04", "web-bff-02", "cart-worker-07", "mobile-gw-01")


def _badge_state(risk: str) -> str:
    if risk in {"BREAKING", "CRITICAL"}:
        return "fault"
    if risk in {"MODERATE", "WARN"}:
        return "warn"
    return "nominal"


def build_v23_blast_svg() -> str:
    """Render deterministic full-width SVG bar comparison of Stage 1 canary traffic vs held clusters."""
    bars = []
    bar_x, track_w = 196.0, 788.0
    for idx, (label, cohort, pct, fill_tok) in enumerate(_V23_COHORTS):
        y = 32 + idx * 36
        bar_w = round((pct / 40.0) * track_w, 1)
        is_canary = "Canary" in cohort
        bg_op = "0.14" if is_canary else "0.06"
        bars.append(
            f'<text x="2" y="{y + 15}" text-anchor="start" font-size="11.5" fill="var(--text-primary)">{html.escape(label)}</text>'
            f'<rect x="{bar_x:.1f}" y="{y}" width="{track_w:.1f}" height="22" rx="3" fill="var(--text-muted)" opacity="{bg_op}"/>'
            f'<rect x="{bar_x:.1f}" y="{y}" width="{bar_w}" height="22" rx="3" fill="{fill_tok}"/>'
            f'<text x="1118" y="{y + 15}" text-anchor="end" font-size="11.5" font-weight="600" fill="var(--text-primary)">{pct:.1f}% ({cohort})</text>'
        )
    grid = "".join(
        f'<line x1="{bar_x:.1f}" y1="24" x2="{bar_x:.1f}" y2="210" stroke="var(--border-subtle)"/>'
        f'<text x="{bar_x:.1f}" y="226" text-anchor="middle" font-size="11.5" fill="var(--text-muted)">0%</text>'
        if i == 0 else
        f'<line x1="{bar_x + i * (track_w / 4.0):.1f}" y1="24" x2="{bar_x + i * (track_w / 4.0):.1f}" y2="210" stroke="var(--border-subtle)" stroke-dasharray="2 3"/>'
        f'<text x="{bar_x + i * (track_w / 4.0):.1f}" y="226" text-anchor="middle" font-size="11.5" fill="var(--text-muted)">{i * 10}%</text>'
        for i in range(5)
    )
    return (
        '<svg data-v23-blast-svg viewBox="0 0 1120 236" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="Canary blast radius chart showing 14.3% traffic across 2 canary clusters and 85.7% held on baseline r41">'
        '<text x="2" y="16" font-size="12" font-weight="650" fill="var(--text-primary)">Traffic Share by Cluster Cohort (14 Edge Clusters)</text>'
        f'{grid}{"".join(bars)}'
        '</svg>'
    )


def build_v23_table_rows() -> str:
    """Build semantic parameter diff table rows for v23 and Specimen 51."""
    out = []
    for key, r41, r42, impact, clusters, risk, cat in _V23_DIFF_ROWS:
        hidden_attr = " hidden" if cat == "context" else ""
        st = _badge_state(risk)
        out.append(
            f'<tr class="v23-row" data-v23-cat="{cat}" data-diff-risk="{risk}"{hidden_attr}>'
            f'<td data-label="Parameter Key"><code class="w2-code">{html.escape(key)}</code></td>'
            f'<td data-label="Baseline r41"><span class="w2-num">{html.escape(r41)}</span></td>'
            f'<td data-label="Candidate r42"><span class="w2-num">{html.escape(r42)}</span></td>'
            f'<td data-label="Policy Impact">{html.escape(impact)}</td>'
            f'<td data-label="Clusters" class="w2-num">{html.escape(clusters)}</td>'
            f'<td data-label="Risk"><span class="va-pill" data-variant="tag" data-state="{st}">{html.escape(risk)}</span></td>'
            '</tr>'
        )
    return "".join(out)


def _v23_kpis() -> str:
    cards = (
        ("Changed Parameters", "6 of 24", "3 security · 3 capacity & timeout", "nominal", "", "", ""),
        ("Canary Blast Radius", "2 of 14 clusters", "14.3% traffic · ewr-edge-01, fra-edge-02", "warn", ' data-v23-kpi-tile="blast"', ' data-v23-kpi="blast"', ' data-v23-kpi="blast_sub"'),
        ("Required Soak Window", "30 min", "Zero-fault gate prior to global promotion", "nominal", "", "", ""),
        ("Rollback Readiness", "Instant r41 Revert", "Pre-warmed snapshot r41 ready", "nominal", "", "", ""),
    )
    return "".join(
        f'<div class="w2-kpi-tile" data-state="{st}"{t_attr}><span class="w2-kpi-lbl">{lbl}</span>'
        f'<span class="w2-kpi-val"{v_attr}>{val}</span><span class="w2-kpi-sub"{s_attr}>{sub}</span></div>'
        for lbl, val, sub, st, t_attr, v_attr, s_attr in cards
    )


def build_v23_html() -> str:
    """Build View v23 Semantic Config & Calibration Diff Review console."""
    return (
        '<div class="w2-stack" data-v23-scope="studio" data-v23-phase="baseline">'
        f'<div class="w2-kpi-grid">{_v23_kpis()}</div>'
        '<section class="w2-card" aria-labelledby="v23-main-title">'
        '<div class="w2-card-hdr"><div>'
        '<h2 id="v23-main-title" class="w2-card-title">Edge mTLS &amp; Rate-Limit Semantic Diff (Baseline r41 vs Candidate r42)</h2>'
        '<p class="w2-card-sub">Structured parameter impact across 14 edge clusters before staged rollout.</p>'
        '</div><span id="v23-header-status-pill" class="va-pill" data-variant="status" data-state="nominal">BASELINE r41</span></div>'
        '<div class="w2-toolbar" role="region" aria-label="Diff category filters">'
        '<div class="w2-btn-group">'
        '<button type="button" class="w2-filter-btn" data-v23-filter="all" aria-pressed="true">All Changes (6)</button>'
        '<button type="button" class="w2-filter-btn" data-v23-filter="security" aria-pressed="false">Security Tightening (3)</button>'
        '<button type="button" class="w2-filter-btn" data-v23-filter="capacity" aria-pressed="false">Capacity &amp; Timeout Shifts (3)</button>'
        '</div>'
        '<label class="w2-check-lbl" for="v23-ctx-toggle">'
        '<input type="checkbox" id="v23-ctx-toggle" data-v23-context/>'
        '<span>Show unchanged context keys (6)</span></label></div>'
        '<div class="va-table-wrap w2-table-wrap"><table class="w2-table" aria-label="Semantic config diff table">'
        '<thead><tr><th>Parameter Key</th><th>Baseline r41</th><th>Candidate r42</th>'
        '<th>Signed Delta / Policy Impact</th><th>Clusters</th><th>Risk</th></tr></thead>'
        f'<tbody data-v23-tbody>{build_v23_table_rows()}</tbody></table></div>'
        '<div class="w2-promote-bar" role="region" aria-label="Two-step reversible promotion controls">'
        '<div class="w2-gate-meta">'
        '<span class="w2-gate-status-line" data-v23-gate-status>Baseline r41 active on 14/14 clusters — preflight check mtls.client_cert_pinning before staging r42</span>'
        '<span class="w2-gate-note">Reversible two-step gate: canary soak (30 min) precedes global cutover, with 1-click r41 revert.</span>'
        '</div><div class="w2-btn-group w2-gate-actions">'
        '<button type="button" class="w2-action-btn" data-tone="primary" data-v23-stage>1. Stage r42 Canary (2 clusters)</button>'
        '<button type="button" class="w2-action-btn" data-v23-confirm disabled>2. Confirm Promotion</button>'
        '<button type="button" class="w2-action-btn" data-v23-revert disabled>Revert to r41</button>'
        '</div></div>'
        '<div class="va-undo-toast" data-v23-toast hidden role="status" aria-live="polite">'
        '<span>Candidate r42 promoted globally across 14 clusters.</span>'
        '<button type="button" class="w2-action-btn" data-v23-toast-revert>Undo to r41</button></div>'
        '</section>'
        '<section class="w2-card" aria-labelledby="v23-blast-title">'
        '<div class="w2-card-hdr"><div>'
        '<h3 id="v23-blast-title" class="w2-card-title">Cluster Blast-Radius Distribution</h3>'
        '<p class="w2-card-sub">Stage 1 restricts candidate r42 exposure to 14.3% edge ingress traffic.</p>'
        '</div></div>'
        f'<div class="w2-svg-box">{build_v23_blast_svg()}</div>'
        '<div class="w2-legend-row" aria-label="Blast radius chart legend">'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="focal"></span>Canary Wave 1 (2/14 clusters · 14.3%)</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="muted"></span>Control Cohort Held on r41 (12/14 clusters · 85.7%)</span>'
        '</div></section></div>'
    )


def generate_v24_events() -> list[dict[str, str]]:
    """Build deterministic 48-row triage event log matching exact 24-bucket & severity totals."""
    rows: list[dict[str, str]] = []
    crit_durs = (412, 528, 645, 486, 710, 564, 438, 612, 495)
    warn_durs = (196, 214, 240, 268, 184, 225, 252, 231, 208, 276, 192, 248, 219, 262)
    auth_durs = (92, 98, 104, 110, 116, 122, 128, 134, 140, 146, 150)
    nom_durs = (38, 42, 45, 48, 52, 41, 46, 39, 54, 44, 50, 43, 47, 56)
    c_i = w_i = a_i = n_i = 0
    for b_idx, (hhmm, c_cnt, w_cnt, a_cnt, n_cnt) in enumerate(_V24_BUCKETS):
        seq = (("critical", c_cnt), ("warning", w_cnt), ("auth_tls", a_cnt), ("nominal", n_cnt))
        sec_offset = 6
        for cat, cnt in seq:
            for _ in range(cnt):
                idx = len(rows) + 1
                ts = f"{hhmm}:{sec_offset:02d}Z"
                sec_offset = (sec_offset + 14) % 58
                span_id = f"sp-{8100 + idx}"
                trace_id = f"tr-9f{b_idx:02x}{idx:02x}"
                caller = _V24_CALLERS[idx % 4]
                if cat == "critical":
                    dur = crit_durs[c_i]
                    svc = "checkout-api" if c_i % 2 == 0 else "auth-gateway"
                    code = "503" if c_i % 2 == 0 else "504"
                    msg = f"Upstream payment lock timeout burst ({dur} ms)" if svc == "checkout-api" else f"Token verification pool exhausted ({dur} ms)"
                    c_i += 1
                    sev_lbl = "CRITICAL"
                elif cat == "warning":
                    dur = warn_durs[w_i]
                    svc = _V24_SERVICES[(w_i + 1) % 4]
                    code = "429" if w_i % 3 == 0 else "200"
                    msg = f"Retry budget queue depth elevated on {caller}"
                    w_i += 1
                    sev_lbl = "WARN"
                elif cat == "auth_tls":
                    dur = auth_durs[a_i]
                    svc = "auth-gateway" if a_i % 2 == 0 else "tls-ingress"
                    code = "200"
                    msg = f"mTLS OCSP staple & JWKS key rotation check ({svc})"
                    a_i += 1
                    sev_lbl = "AUTH/TLS"
                else:
                    dur = nom_durs[n_i]
                    svc = _V24_SERVICES[n_i % 4]
                    code = "200"
                    msg = "Nominal health probe & edge commit verified"
                    n_i += 1
                    sev_lbl = "NOMINAL"
                rows.append({
                    "idx": str(idx), "ts": ts, "bucket": str(b_idx), "cat": cat,
                    "sev": sev_lbl, "svc": svc, "span": span_id, "trace": trace_id,
                    "dur": f"{dur} ms", "caller": caller, "code": code, "msg": msg,
                })
    return rows


def build_v24_histogram_svg() -> str:
    """Build clickable full-width 24-bucket event volume & severity histogram SVG across 14:00Z-15:00Z."""
    bars = []
    ml, pw = 26.0, 1086.0
    step = pw / 24.0
    bw = 33.0
    for i, (hhmm, c_cnt, w_cnt, a_cnt, n_cnt) in enumerate(_V24_BUCKETS):
        x = ml + i * step + (step - bw) / 2.0
        segs = ((c_cnt, "var(--status-danger)"), (w_cnt, "var(--status-warn)"), (a_cnt, "var(--accent-focal)"), (n_cnt, "var(--text-muted)"))
        cur_y = 148.0
        parts = []
        for cnt, fill_tok in segs:
            if cnt <= 0:
                continue
            h = cnt * 24.0
            cur_y -= h
            parts.append(f'<rect x="{x:.1f}" y="{cur_y:.1f}" width="{bw:.1f}" height="{h - 1:.1f}" rx="1.5" fill="{fill_tok}"/>')
        lbl = ""
        if i % 4 == 0:
            lbl = f'<text x="{x + bw / 2.0:.1f}" y="166" text-anchor="middle" font-size="11.5" fill="var(--text-muted)">{hhmm}</text>'
        elif i == 23:
            lbl = f'<text x="{ml + pw:.1f}" y="166" text-anchor="end" font-size="11.5" fill="var(--text-muted)">{hhmm}</text>'
        bars.append(
            f'<g class="w2-svg-bar-grp" role="button" tabindex="0" data-v24-bucket="{i}" '
            f'aria-pressed="false" aria-label="Bucket {hhmm} UTC: {c_cnt + w_cnt + a_cnt + n_cnt} events">'
            f'<rect class="w2-bucket-hit" x="{x - 3:.1f}" y="28" width="{bw + 6:.1f}" height="122" rx="2" fill="transparent"/>'
            f'{"".join(parts)}{lbl}</g>'
        )
    y_grid = "".join(
        f'<line x1="26" y1="{148 - val * 24}" x2="1112" y2="{148 - val * 24}" stroke="var(--border-subtle)" stroke-dasharray="2 3"/>'
        f'<text x="20" y="{152 - val * 24}" text-anchor="end" font-size="11.5" fill="var(--text-muted)">{val}</text>'
        for val in (0, 1, 2, 3, 4)
    )
    hl_x = ml + 8.0 * step
    hl_w = 6.0 * step
    hl_cx = hl_x + hl_w / 2.0
    burst_hl = (
        f'<rect x="{hl_x:.1f}" y="24" width="{hl_w:.1f}" height="124" rx="3" fill="var(--status-danger)" opacity="0.06"/>'
        f'<rect x="{hl_cx - 74:.1f}" y="14" width="148" height="18" rx="2" fill="var(--bg-surface)" opacity="0.94"/>'
        f'<text x="{hl_cx:.1f}" y="27" text-anchor="middle" font-size="11.5" font-weight="650" fill="var(--status-danger)">Burst Peak 14:20Z–14:35Z</text>'
    )
    return (
        '<svg data-v24-hist-svg viewBox="0 0 1120 178" preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="24-bucket telemetry event histogram from 14:00Z to 15:00Z showing 9 critical fault burst between 14:20Z and 14:35Z">'
        f'{burst_hl}{y_grid}{"".join(bars)}</svg>'
    )


def _v24_table_body(events: Iterable[dict[str, str]]) -> str:
    trs = []
    for idx, ev in enumerate(events):
        sel = "true" if idx == 0 else "false"
        st = _badge_state(ev["sev"])
        trs.append(
            f'<tr class="v24-row" tabindex="0" aria-selected="{sel}" '
            f'data-v24-cat="{ev["cat"]}" data-v24-bucket="{ev["bucket"]}" '
            f'data-v24-search="{html.escape((ev["svc"] + " " + ev["span"] + " " + ev["trace"] + " " + ev["msg"]).lower())}" '
            f'data-ev-ts="{ev["ts"]}" data-ev-svc="{ev["svc"]}" data-ev-span="{ev["span"]}" '
            f'data-ev-trace="{ev["trace"]}" data-ev-dur="{ev["dur"]}" data-ev-sev="{ev["sev"]}" '
            f'data-ev-caller="{ev["caller"]}" data-ev-code="{ev["code"]}" data-ev-msg="{html.escape(ev["msg"])}">'
            f'<td data-label="UTC Time" class="w2-num">{ev["ts"]}</td>'
            f'<td data-label="Service"><code class="w2-code">{ev["svc"]}</code></td>'
            f'<td data-label="Span ID" class="w2-num">{ev["span"]}</td>'
            f'<td data-label="Dur." class="w2-num">{ev["dur"]}</td>'
            f'<td data-label="Level"><span class="va-pill" data-variant="tag" data-state="{st}">{ev["sev"]}</span></td>'
            f'<td data-label="Event Summary">{html.escape(ev["msg"])}</td></tr>'
        )
    return "".join(trs)


def build_v24_html() -> str:
    """Build View v24 High-Row Log & Telemetry Event Triage Desk (48 events)."""
    events = generate_v24_events()
    first = events[0]
    kpis = (
        ("Total Events", "48", "60-min window (14:00Z–15:00Z)", "nominal"),
        ("Error Burst Peak", "14:20Z–14:35Z", "9 critical faults clustered", "fault"),
        ("Affected Services", "4", "checkout-api, auth-gateway, token-signer, tls-ingress", "warn"),
        ("Median Triage Latency", "148.0 ms", "Baseline health latency 45.0 ms", "nominal"),
    )
    kpi_html = "".join(
        f'<div class="w2-kpi-tile" data-state="{st}"><span class="w2-kpi-lbl">{lbl}</span>'
        f'<span class="w2-kpi-val">{val}</span><span class="w2-kpi-sub">{sub}</span></div>'
        for lbl, val, sub, st in kpis
    )
    return (
        '<div class="w2-stack" data-v24-scope="studio">'
        f'<div class="w2-kpi-grid">{kpi_html}</div>'
        '<section class="w2-card" aria-labelledby="v24-hist-title">'
        '<div class="w2-card-hdr"><div>'
        '<h2 id="v24-hist-title" class="w2-card-title">Event Volume &amp; Severity Timeline (24 Buckets · 14:00Z–15:00Z)</h2>'
        '<p class="w2-card-sub">Click any 2.5-minute bucket bar to isolate burst events across services.</p>'
        '</div><span class="w2-num" data-v24-visible-count>Showing 48 / 48 events</span></div>'
        f'<div class="w2-svg-box">{build_v24_histogram_svg()}</div>'
        '<div class="w2-legend-row" aria-label="Telemetry severity legend">'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="danger"></span>Critical Faults (9)</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="warn"></span>Warnings (14)</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="focal"></span>Auth &amp; TLS (11)</span>'
        '<span class="w2-legend-item"><span class="w2-legend-swatch" data-tone="muted"></span>Nominal (14)</span>'
        '</div></section>'
        '<section class="w2-card" aria-labelledby="v24-desk-title">'
        '<div class="w2-card-hdr"><div>'
        '<h3 id="v24-desk-title" class="w2-card-title">Structured Event Stream &amp; Live Row Inspector</h3>'
        '<p class="w2-card-sub">Filter 48 telemetry rows by severity or search trace, span, and service attributes.</p>'
        '</div></div>'
        '<div class="w2-toolbar" role="region" aria-label="Telemetry triage filters">'
        '<div class="w2-btn-group">'
        '<button type="button" class="w2-filter-btn" data-v24-filter="all" aria-pressed="true">All (48)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="critical" aria-pressed="false">Critical Faults (9)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="warning" aria-pressed="false">Warnings (14)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="auth_tls" aria-pressed="false">Auth &amp; TLS (11)</button>'
        '<button type="button" class="w2-filter-btn" data-v24-filter="nominal" aria-pressed="false">Nominal (14)</button>'
        '</div>'
        '<div class="w2-search-wrap">'
        '<label class="w2-search-lbl" for="v24-search-input">Search stream</label>'
        '<input type="search" id="v24-search-input" class="w2-search-input" placeholder="Service, span ID, message..." data-v24-search/>'
        '</div></div>'
        '<div class="v24-split">'
        '<div class="va-table-wrap w2-table-wrap v24-table-scroll" role="region" aria-label="Telemetry event table">'
        '<table class="w2-table" data-v24-table>'
        '<thead><tr><th>UTC Time</th><th>Service</th><th>Span ID</th><th>Dur.</th><th>Level</th><th>Event Summary</th></tr></thead>'
        f'<tbody data-v24-tbody>{_v24_table_body(events)}</tbody></table>'
        '<div class="va-empty-state" data-kind="filtered" data-v24-empty hidden>'
        '<p><strong>No matching telemetry rows</strong> in this filter or search query.</p>'
        '<button type="button" class="w2-action-btn" data-tone="primary" data-v24-clear>Clear filters</button>'
        '</div></div>'
        '<aside class="w2-inspector" aria-label="Selected telemetry row inspector" data-v24-inspector>'
        '<div class="w2-card-hdr">'
        '<h4 class="w2-card-title w2-inspector-title">Row Inspector</h4>'
        f'<span class="va-pill" data-variant="tag" data-state="{_badge_state(first["sev"])}" data-insp-sev>{first["sev"]}</span></div>'
        '<div class="w2-insp-empty" data-v24-insp-empty hidden>'
        '<p><strong>No matching row selected</strong> — adjust the active filter or search query, or click <em>Clear filters</em> to restore rows.</p>'
        '</div>'
        '<div data-v24-insp-body>'
        '<dl class="w2-dl">'
        f'<dt>Timestamp</dt><dd class="w2-num" data-insp-ts>{first["ts"]}</dd>'
        f'<dt>Service</dt><dd class="w2-code" data-insp-svc>{first["svc"]}</dd>'
        f'<dt>Span ID</dt><dd class="w2-num" data-insp-span>{first["span"]}</dd>'
        f'<dt>Trace ID</dt><dd class="w2-num" data-insp-trace>{first["trace"]}</dd>'
        f'<dt>Upstream Caller</dt><dd class="w2-code" data-insp-caller>{first["caller"]}</dd>'
        f'<dt>Status / Latency</dt><dd class="w2-num" data-insp-code>{first["code"]} · {first["dur"]}</dd>'
        f'<dt>Event Detail</dt><dd data-insp-msg>{html.escape(first["msg"])}</dd>'
        '</dl>'
        '<div class="w2-btn-group w2-table-mt"><button type="button" class="w2-action-btn" data-v24-copy>Copy Trace Summary</button>'
        '<span class="w2-kpi-sub" role="status" aria-live="polite" data-v24-copy-status></span></div>'
        '</div></aside></div></section></div>'
    )


WAVE2_WORLD02_VIEW_CFG: dict[str, dict[str, object]] = {
    "v23-semantic-config-diff-review": {
        "option_label": "v23 · Edge Policy Config Diff", "default_medium": "m3",
        "chromatic_code": "c3", "default_nav": "n2", "allowed_navs": ["n2", "n0"],
        "nav_icon": "code-branch", "nav_brand": "Edge Config Diff",
        "topbar_brand": "Edge Policy Rollout · r41 vs r42", "rail_brand": "Diff Sections",
        "topbar_status": [], "nav_items": ["Diff Table", "Blast Radius"],
        "nav_anchors": ["v23-main-title", "v23-blast-title"],
        "inv_col": "v23-semantic-config-diff-review", "short_tag": "v23",
        "invariants_fallback": {
            "baseline": "Baseline revision r41 across 14 active edge clusters vs candidate r42.",
            "provenance": "Structured semantic diff across 24 audited keys isolating 6 changed controls.",
            "margin": "Stage 1 restricts canary traffic to 2 clusters (14.3%) during the 30 min soak gate.",
            "disposition": "Verify zero unpinned clients before staging r42 canary with instant r41 revert.",
        },
        "bias_removed": "Raw Text Line Diffs & Single-Click Global Push",
        "bias_risk": "Line-based config text diffs hide policy blast radius and lack reversible soak gates.",
        "bias_replacement": "Typed semantic key table paired with blast-radius chart and two-step canary promotion.",
    },
    "v24-telemetry-event-triage-desk": {
        "option_label": "v24 · High-Row Event Triage Desk", "default_medium": "m3",
        "chromatic_code": "c4", "default_nav": "n2", "allowed_navs": ["n2", "n0"],
        "nav_icon": "activity", "nav_brand": "Event Triage",
        "topbar_brand": "Checkout & Auth Event Triage · 48 Events", "rail_brand": "Triage Desk",
        "topbar_status": [], "nav_items": ["Volume Chart", "Event Stream"],
        "nav_anchors": ["v24-hist-title", "v24-desk-title"],
        "inv_col": "v24-telemetry-event-triage-desk", "short_tag": "v24",
        "invariants_fallback": {
            "baseline": "60-minute regional triage stream (14:00Z to 15:00Z) anchored against 45.0 ms baseline.",
            "provenance": "48 structured events binned across 24 histogram buckets with span and caller IDs.",
            "margin": "9 critical faults cluster in the 14:20Z-14:35Z burst; median latency rises to 148.0 ms.",
            "disposition": "Filter burst rows, inspect upstream caller detail, and recover cleanly via Clear filters.",
        },
        "bias_removed": "Unindexed Log Firehoses & Dead-End Search States",
        "bias_risk": "Raw log dumps conceal burst windows and trap operators in zero-result dead ends.",
        "bias_replacement": "24-bucket burst chart paired with 48-row split inspector and 1-click filter recovery.",
    },
}
