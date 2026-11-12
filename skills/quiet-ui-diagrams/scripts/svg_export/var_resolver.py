# SPDX-License-Identifier: MIT
"""Quiet UI 4-Theme tokens and CSS variable resolution for standalone SVG 1.1 export.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import re

BASE_TYPOGRAPHY = {
    "--font-sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "--font-serif": "'Newsreader', 'Charter', 'Source Serif 4', Georgia, serif",
    "--font-mono": "'JetBrains Mono', 'Fira Code', ui-monospace, monospace",
    "--font-nums": "tabular-nums slashed-zero",
    "--ts-xs": "11px",
    "--ts-sm": "12.5px",
    "--ts-nav": "13px",
    "--ts-base": "14px",
    "--ts-prose": "15.5px",
    "--ts-md": "16px",
    "--ts-xl": "20px",
    "--ts-display": "24px",
    "--radius-card": "8px",
    "--radius-sm": "6px",
    "--radius-inner": "4px",
    "--radius-pill": "999px",
}

QUIET_UI_THEMES: dict[str, dict[str, str]] = {
    "white": {
        **BASE_TYPOGRAPHY,
        "--bg-shell": "#F1F5F9",
        "--bg-canvas": "#FFFFFF",
        "--bg-surface": "#FFFFFF",
        "--bg-card": "#FFFFFF",
        "--bg-elevated": "#F8FAFC",
        "--bg-header": "#F8FAFC",
        "--bg-glass": "rgba(255, 255, 255, 0.88)",
        "--text-primary": "#0F172A",
        "--text-main": "#0F172A",
        "--text-secondary": "#334155",
        "--text-dim": "#334155",
        "--text-muted": "#64748B",
        "--border-hairline": "#E2E8F0",
        "--border-grid": "#E2E8F0",
        "--border-strong": "#CBD5E1",
        "--accent-primary": "#2563EB",
        "--accent-focal": "#2563EB",
        "--status-ok": "#15803D",
        "--status-warn": "#B45309",
        "--status-danger": "#B91C1C",
        "--status-err": "#B91C1C",
        "--tint-indigo-bg": "#EEF2FF",
        "--tint-indigo-fg": "#4338CA",
        "--tint-emerald-bg": "#ECFDF5",
        "--tint-emerald-fg": "#047857",
        "--tint-amber-bg": "#FFFBEB",
        "--tint-amber-fg": "#B45309",
        "--tint-rose-bg": "#FFF1F2",
        "--tint-rose-fg": "#BE123C",
        "--tint-violet-bg": "#F5F3FF",
        "--tint-violet-fg": "#6D28D9",
    },
    "paper": {
        **BASE_TYPOGRAPHY,
        "--bg-shell": "#EFECE6",
        "--bg-canvas": "#F6F4F0",
        "--bg-surface": "#FCFBF9",
        "--bg-card": "#FCFBF9",
        "--bg-elevated": "#EFECE6",
        "--bg-header": "#EFECE6",
        "--bg-glass": "rgba(252, 251, 249, 0.90)",
        "--text-primary": "#1C1917",
        "--text-main": "#1C1917",
        "--text-secondary": "#44403C",
        "--text-dim": "#44403C",
        "--text-muted": "#78716C",
        "--border-hairline": "#E5E0D8",
        "--border-grid": "#E5E0D8",
        "--border-strong": "#D6CFC7",
        "--accent-primary": "#1D4ED8",
        "--accent-focal": "#1D4ED8",
        "--status-ok": "#15803D",
        "--status-warn": "#B45309",
        "--status-danger": "#B91C1C",
        "--status-err": "#B91C1C",
        "--tint-indigo-bg": "#EBF0FA",
        "--tint-indigo-fg": "#3730A3",
        "--tint-emerald-bg": "#E8F5EE",
        "--tint-emerald-fg": "#065F46",
        "--tint-amber-bg": "#FDF5E6",
        "--tint-amber-fg": "#92400E",
        "--tint-rose-bg": "#FCEEEF",
        "--tint-rose-fg": "#9F1239",
        "--tint-violet-bg": "#F1EEFA",
        "--tint-violet-fg": "#5B21B6",
    },
    "dark-paper": {
        **BASE_TYPOGRAPHY,
        "--bg-shell": "#0E0D0C",
        "--bg-canvas": "#141413",
        "--bg-surface": "#1C1B1A",
        "--bg-card": "#1C1B1A",
        "--bg-elevated": "#262523",
        "--bg-header": "#262523",
        "--bg-glass": "rgba(28, 27, 26, 0.88)",
        "--text-primary": "#EDEBE6",
        "--text-main": "#EDEBE6",
        "--text-secondary": "#A8A29E",
        "--text-dim": "#A8A29E",
        "--text-muted": "#78716C",
        "--border-hairline": "#2E2D2A",
        "--border-grid": "#2E2D2A",
        "--border-strong": "#44403C",
        "--accent-primary": "#60A5FA",
        "--accent-focal": "#60A5FA",
        "--status-ok": "#22C55E",
        "--status-warn": "#F59E0B",
        "--status-danger": "#EF4444",
        "--status-err": "#EF4444",
        "--tint-indigo-bg": "rgba(99, 102, 241, 0.14)",
        "--tint-indigo-fg": "#A5B4FC",
        "--tint-emerald-bg": "rgba(16, 185, 129, 0.14)",
        "--tint-emerald-fg": "#6EE7B7",
        "--tint-amber-bg": "rgba(245, 158, 11, 0.14)",
        "--tint-amber-fg": "#FCD34D",
        "--tint-rose-bg": "rgba(244, 63, 94, 0.14)",
        "--tint-rose-fg": "#FDA4AF",
        "--tint-violet-bg": "rgba(139, 92, 246, 0.14)",
        "--tint-violet-fg": "#C4B5FD",
    },
    "dark": {
        **BASE_TYPOGRAPHY,
        "--bg-shell": "#05070B",
        "--bg-canvas": "#090D16",
        "--bg-surface": "#0F1523",
        "--bg-card": "#0F1523",
        "--bg-elevated": "#172033",
        "--bg-header": "#172033",
        "--bg-glass": "rgba(15, 21, 35, 0.86)",
        "--text-primary": "#F1F5F9",
        "--text-main": "#F1F5F9",
        "--text-secondary": "#94A3B8",
        "--text-dim": "#94A3B8",
        "--text-muted": "#64748B",
        "--border-hairline": "#1E293B",
        "--border-grid": "#1E293B",
        "--border-strong": "#334155",
        "--accent-primary": "#38BDF8",
        "--accent-focal": "#38BDF8",
        "--status-ok": "#22C55E",
        "--status-warn": "#F59E0B",
        "--status-danger": "#EF4444",
        "--status-err": "#EF4444",
        "--tint-indigo-bg": "rgba(99, 102, 241, 0.16)",
        "--tint-indigo-fg": "#A5B4FC",
        "--tint-emerald-bg": "rgba(16, 185, 129, 0.16)",
        "--tint-emerald-fg": "#6EE7B7",
        "--tint-amber-bg": "rgba(245, 158, 11, 0.16)",
        "--tint-amber-fg": "#FCD34D",
        "--tint-rose-bg": "rgba(244, 63, 94, 0.16)",
        "--tint-rose-fg": "#FDA4AF",
        "--tint-violet-bg": "rgba(139, 92, 246, 0.16)",
        "--tint-violet-fg": "#C4B5FD",
    },
}

VAR_RE = re.compile(r"var\(\s*(--[\w-]+)(?:\s*,\s*([^()]+|\([^()]*\)))?\s*\)")
PROP_DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+)")
THEME_BLOCK_RE = re.compile(r"(?:([^{}]+))\{([^{}]+)\}")


def extract_declared_variables(source: str, theme: str = "white") -> tuple[dict[str, str], dict[str, str]]:
    root_vars: dict[str, str] = {}
    theme_vars: dict[str, str] = {}
    for selector, body in THEME_BLOCK_RE.findall(source):
        sel = selector.strip().lower()
        is_theme_target = f'data-theme="{theme}"' in sel or f"data-theme='{theme}'" in sel
        is_other_theme = "data-theme=" in sel and not is_theme_target
        is_root = (":root" in sel or "html" in sel or "body" in sel) and not is_other_theme
        if is_theme_target:
            for name, val in PROP_DECL_RE.findall(body):
                theme_vars[name.strip()] = val.strip()
        elif is_root:
            for name, val in PROP_DECL_RE.findall(body):
                root_vars[name.strip()] = val.strip()
    return root_vars, theme_vars


def _sub_vars_once(text: str, lookup: dict[str, str]) -> str:
    def _repl(match: re.Match[str]) -> str:
        name = match.group(1)
        fallback = (match.group(2) or "").strip()
        return lookup.get(name, fallback or match.group(0))

    return VAR_RE.sub(_repl, text)


def resolve_token_map(
    theme: str = "white",
    root_vars: dict[str, str] | None = None,
    theme_vars: dict[str, str] | None = None,
) -> dict[str, str]:
    chosen = theme if theme in QUIET_UI_THEMES else "white"
    if chosen == "white":
        tokens = {**QUIET_UI_THEMES["white"], **(root_vars or {}), **(theme_vars or {})}
    else:
        tokens = {**(root_vars or {}), **QUIET_UI_THEMES[chosen], **(theme_vars or {})}

    resolved: dict[str, str] = {}
    for key, val in tokens.items():
        curr = val
        for _ in range(6):
            nxt = _sub_vars_once(curr, tokens)
            if nxt == curr:
                break
            curr = nxt
        resolved[key] = curr
    return resolved


def resolve_var_in_text(text: str, token_map: dict[str, str]) -> str:
    curr = text
    for _ in range(6):
        nxt = _sub_vars_once(curr, token_map)
        if nxt == curr:
            break
        curr = nxt
    return curr


def resolve_svg_variables(svg_text: str, theme: str = "white", html_source: str = "") -> str:
    root_vars: dict[str, str] = {}
    theme_vars: dict[str, str] = {}
    if html_source:
        r_html, t_html = extract_declared_variables(html_source, theme)
        root_vars.update(r_html)
        theme_vars.update(t_html)
    r_svg, t_svg = extract_declared_variables(svg_text, theme)
    root_vars.update(r_svg)
    theme_vars.update(t_svg)
    token_map = resolve_token_map(theme, root_vars, theme_vars)
    return resolve_var_in_text(svg_text, token_map)
