# SPDX-License-Identifier: Apache-2.0
"""Static 1280x640 social preview card renderers (SVG stdlib + lazy Pillow PNG)."""

from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path
from typing import Any

_BOLD_FONTS = (
    "/usr/share/fonts/google-carlito-fonts/Carlito-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)
_REG_FONTS = (
    "/usr/share/fonts/google-carlito-fonts/Carlito-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
)
_MONO_FONTS = (
    "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf", "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", "/System/Library/Fonts/Supplemental/Menlo.ttc",
    "C:/Windows/Fonts/consola.ttf",
)

_THEMES: dict[str, dict[str, str]] = {
    "white": {
        "bg": "#FFFFFF", "card_bg": "#F8FAFC", "panel_bg": "#FFFFFF", "block_bg": "#F8FAFC",
        "border": "#E2E8F0", "grid": "#EEF2F6", "ink": "#0F172A", "muted": "#334155",
        "subtle": "#64748B", "pill_bg": "#F1F5F9", "pill_border": "#CBD5E1",
        "pill_ink": "#1E293B", "default_accent": "#0284C7", "accent_tint": "#E0F2FE",
    },
    "dark": {
        "bg": "#0B1120", "card_bg": "#0F172A", "panel_bg": "#111C33", "block_bg": "#0B1120",
        "border": "#1E293B", "grid": "#162033", "ink": "#F8FAFC", "muted": "#CBD5E1",
        "subtle": "#94A3B8", "pill_bg": "#1E293B", "pill_border": "#334155",
        "pill_ink": "#E2E8F0", "default_accent": "#38BDF8", "accent_tint": "#0C4A6E",
    },
}

_HEX_RE = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")
_DEFAULT_BLOCKS = (
    ("01", "quiet-ui", "7 mediums / 4 themes / WCAG AA"),
    ("02", "quiet-evidence", "NIST 1-2-5 / SVG & ECharts"),
    ("03", "quiet-bridge", "L1-L3 lenses / conservation"),
)
_WAVE_POINTS = (
    (808, 524), (848, 514), (888, 518), (928, 492), (968, 498),
    (1008, 474), (1048, 482), (1088, 456), (1128, 464), (1168, 444),
)


def _clean_hex(raw: Any, fallback: str) -> str:
    if isinstance(raw, str):
        m = _HEX_RE.match(raw.strip())
        if m:
            body = m.group(1)
            if len(body) == 3:
                body = "".join(ch * 2 for ch in body)
            return f"#{body.upper()}"
    return fallback


def _extract_meta(config: dict[str, Any], theme: str = "white") -> dict[str, Any]:
    pal = _THEMES.get(theme, _THEMES["white"])
    sp = config.get("social_preview") if isinstance(config.get("social_preview"), dict) else {}
    proj = config.get("project") if isinstance(config.get("project"), dict) else {}

    def pick(*keys: str, default: str = "") -> str:
        for src in (sp, proj, config):
            for key in keys:
                val = src.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
        return default

    raw_pills = sp.get("pills") or proj.get("pills") or config.get("pills") or (
        "White / Dark", "NIST 1-2-5", "Zero JS Deps", "Apache-2.0 / MIT",
    )
    pills = [str(p).strip() for p in raw_pills if p is not None and str(p).strip()][:4] if isinstance(raw_pills, (list, tuple)) else []
    url = pick("site_url", "repo_url", default="quiet-ui / static architecture")
    url = url.removeprefix("https://").removeprefix("http://").rstrip("/")
    return {
        "eyebrow": pick("eyebrow", "tagline", default="QUIET UI ARCHITECTURE").upper(),
        "title": pick("title", "name", default="Quiet UI"),
        "subtitle": pick("subtitle", "description", default="Deterministic evidence & calm human-factors interfaces."),
        "pills": pills,
        "accent": _clean_hex(pick("accent_hex", default=""), pal["default_accent"]),
        "url": url,
        "blocks": _extract_blocks(sp, proj, config),
    }


def _extract_blocks(sp: dict[str, Any], proj: dict[str, Any], config: dict[str, Any]) -> list[tuple[str, str, str]]:
    raw = sp.get("routes") or sp.get("pillars") or proj.get("routes") or config.get("routes")
    if isinstance(raw, dict):
        items: list[Any] = [
            raw[k] for k in ("overview", "demo", "docs")
            if isinstance(raw.get(k), dict) and not (k == "demo" and raw[k].get("enabled") is False)
        ]
        if not items:
            items = [v for v in raw.values() if isinstance(v, dict)]
    elif isinstance(raw, (list, tuple)):
        items = list(raw)
    else:
        items = []
    out: list[tuple[str, str, str]] = []
    for idx, item in enumerate(items[:3], start=1):
        tag = f"{idx:02d}"
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("title") or item.get("name") or f"Route {tag}").strip()
            detail = str(item.get("detail") or item.get("subtitle") or item.get("path") or item.get("href") or "").strip()
            out.append((tag, label[:30], detail[:42]))
        elif isinstance(item, str) and item.strip():
            out.append((tag, item.strip()[:30], "Structured route"))
    return out or list(_DEFAULT_BLOCKS)


def _fit_eyebrow(text: str, max_chars: int = 58) -> str:
    clean = " ".join(text.split())
    if len(clean) <= max_chars:
        return clean
    cut = clean[: max(1, max_chars - 3)]
    if " " in cut and clean[len(cut)] != " ":
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ·-_") + "..."


def _clamp_wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(text, width=width, break_long_words=True, break_on_hyphens=True) or [text]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max(1, width - 3)].rstrip() + "..."
    return lines


def _render_svg_panel(meta: dict[str, Any], pal: dict[str, str]) -> list[str]:
    esc = html.escape
    accent = meta["accent"]
    parts = [
        f'<rect x="768" y="68" width="440" height="504" rx="12" fill="{pal["panel_bg"]}" stroke="{pal["border"]}" stroke-width="1.5"/>',
        f'<line x1="768" y1="108" x2="1208" y2="108" stroke="{pal["border"]}" stroke-width="1"/>',
        f'<text x="792" y="93" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" font-weight="700" letter-spacing="1.2" fill="{pal["subtle"]}">ARCHITECTURE</text>',
        f'<rect x="1118" y="81" width="66" height="16" rx="4" fill="{pal["accent_tint"]}"/>',
        f'<text x="1151" y="93" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11" font-weight="700" fill="{accent}">READY</text>',
    ]
    for i, (tag, label, detail) in enumerate(meta["blocks"]):
        by = 126 + i * 96
        bar_col = accent if i == 0 else pal["pill_border"]
        parts.extend([
            f'<rect x="792" y="{by}" width="392" height="82" rx="8" fill="{pal["block_bg"]}" stroke="{pal["border"]}" stroke-width="1"/>',
            f'<rect x="808" y="{by + 16}" width="4" height="50" fill="{bar_col}"/>',
            f'<text x="826" y="{by + 33}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" font-weight="700" fill="{accent}">{esc(tag)}</text>',
            f'<text x="854" y="{by + 33}" font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="16" font-weight="700" fill="{pal["ink"]}">{esc(label)}</text>',
            f'<text x="826" y="{by + 58}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="13" fill="{pal["muted"]}">{esc(detail)}</text>',
        ])
    line_d = "M " + " L ".join(f"{x} {y}" for x, y in _WAVE_POINTS)
    area_d = line_d + f" L {_WAVE_POINTS[-1][0]} 536 L {_WAVE_POINTS[0][0]} 536 Z"
    parts.extend([
        f'<rect x="792" y="422" width="392" height="128" rx="8" fill="{pal["block_bg"]}" stroke="{pal["border"]}" stroke-width="1"/>',
        f'<text x="808" y="442" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" font-weight="700" fill="{pal["subtle"]}">SIGNAL / 1-2-5 GRID</text>',
        f'<text x="1168" y="442" text-anchor="end" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" fill="{pal["subtle"]}">1280x640</text>',
        *[f'<line x1="808" y1="{gy}" x2="1168" y2="{gy}" stroke="{pal["border"]}" stroke-width="1"/>' for gy in (468, 502, 536)],
        f'<path d="{area_d}" fill="{pal["accent_tint"]}" fill-opacity="0.55" stroke="none"/>',
        f'<path d="{line_d}" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
        *[f'<circle cx="{x}" cy="{y}" r="3.5" fill="{pal["panel_bg"]}" stroke="{accent}" stroke-width="2"/>' for x, y in _WAVE_POINTS[::2]],
    ])
    return parts


def render_social_svg(config: dict[str, Any]) -> str:
    """Render a crisp 1280x640 Quiet UI social card SVG from config."""
    pal, meta, esc = _THEMES["white"], _extract_meta(config, theme="white"), html.escape
    accent = meta["accent"]
    aria = esc(f"{meta['title']} - {meta['subtitle']}" if meta["subtitle"] else meta["title"], quote=True)
    title_lines = _clamp_wrap(meta["title"], width=23, max_lines=3)
    sub_lines = _clamp_wrap(meta["subtitle"], width=48, max_lines=3)
    mono, sans = "ui-monospace,SFMono-Regular,Menlo,monospace", "system-ui,-apple-system,Segoe UI,sans-serif"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" width="1280" height="640" role="img" aria-label="{aria}">',
        f'<rect x="0" y="0" width="1280" height="640" fill="{pal["bg"]}"/>',
        f'<rect x="32" y="32" width="1216" height="576" rx="16" fill="{pal["card_bg"]}" stroke="{pal["border"]}" stroke-width="1.5"/>',
        *[f'<line x1="{gx}" y1="33" x2="{gx}" y2="607" stroke="{pal["grid"]}" stroke-width="1"/>' for gx in range(96, 1216, 80)],
        *[f'<line x1="33" y1="{gy}" x2="1247" y2="{gy}" stroke="{pal["grid"]}" stroke-width="1"/>' for gy in range(96, 600, 80)],
        f'<line x1="736" y1="68" x2="736" y2="572" stroke="{pal["border"]}" stroke-width="1"/>',
        f'<rect x="72" y="72" width="44" height="6" fill="{accent}"/>',
        f'<text x="128" y="80" font-family="{mono}" font-size="13" font-weight="700" letter-spacing="1.1" fill="{accent}">{esc(_fit_eyebrow(meta["eyebrow"]))}</text>',
        *[f'<text x="72" y="{138 + i * 54}" font-family="{sans}" font-size="44" font-weight="700" fill="{pal["ink"]}">{esc(ln)}</text>' for i, ln in enumerate(title_lines)],
    ]
    sy = 138 + len(title_lines) * 54 + 14
    parts.extend(f'<text x="72" y="{sy + i * 30}" font-family="{sans}" font-size="21" fill="{pal["muted"]}">{esc(ln)}</text>' for i, ln in enumerate(sub_lines))
    px = 72
    for idx, raw_pill in enumerate(meta["pills"]):
        pill = raw_pill[:26]
        pw = max(84, int(len(pill) * 8.2 + 28))
        if px + pw > 708:
            break
        bg, br, fg = (pal["accent_tint"], accent, accent) if idx == 0 else (pal["pill_bg"], pal["pill_border"], pal["pill_ink"])
        parts.append(f'<rect x="{px}" y="468" width="{pw}" height="32" rx="6" fill="{bg}" stroke="{br}" stroke-width="1"/>')
        parts.append(f'<text x="{px + pw // 2}" y="489" text-anchor="middle" font-family="{mono}" font-size="13" font-weight="600" fill="{fg}">{esc(pill)}</text>')
        px += pw + 10
    parts.extend([
        f'<line x1="72" y1="534" x2="700" y2="534" stroke="{pal["border"]}" stroke-width="1"/>',
        f'<text x="72" y="562" font-family="{mono}" font-size="14" fill="{pal["subtle"]}">{esc(meta["url"][:58])}</text>',
        *_render_svg_panel(meta, pal),
        "</svg>",
    ])
    return "\n".join(parts) + "\n"


def _load_font(image_font: Any, candidates: tuple[str, ...], size: int) -> Any:
    for path in candidates:
        if Path(path).exists():
            return image_font.truetype(path, size)
    return image_font.load_default()


def _wrap_px(draw: Any, text: str, font: Any, max_w: int, max_lines: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for word in words[1:]:
        cand = f"{cur} {word}"
        if draw.textbbox((0, 0), cand, font=font)[2] <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while len(lines[-1]) > 3 and draw.textbbox((0, 0), lines[-1] + "...", font=font)[2] > max_w:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


def _draw_png_panel(draw: Any, meta: dict[str, Any], pal: dict[str, str], fonts: tuple[Any, Any, Any]) -> None:
    f_bold_sm, f_mono_sm, f_mono_xs = fonts
    accent = meta["accent"]
    draw.rounded_rectangle([768, 68, 1208, 572], radius=12, fill=pal["panel_bg"], outline=pal["border"], width=1)
    draw.line([(768, 108), (1208, 108)], fill=pal["border"], width=1)
    draw.text((792, 82), "ARCHITECTURE", fill=pal["subtle"], font=f_mono_xs)
    draw.rounded_rectangle([1118, 79, 1184, 97], radius=4, fill=pal["accent_tint"])
    draw.text((1128, 82), "READY", fill=accent, font=f_mono_xs)
    for i, (tag, label, detail) in enumerate(meta["blocks"]):
        by = 126 + i * 96
        bar_col = accent if i == 0 else pal["pill_border"]
        draw.rounded_rectangle([792, by, 1184, by + 82], radius=8, fill=pal["block_bg"], outline=pal["border"], width=1)
        draw.rectangle([808, by + 16, 812, by + 66], fill=bar_col)
        draw.text((826, by + 19), tag, fill=accent, font=f_mono_xs)
        draw.text((854, by + 16), label, fill=pal["ink"], font=f_bold_sm)
        draw.text((826, by + 44), detail, fill=pal["muted"], font=f_mono_sm)
    draw.rounded_rectangle([792, 422, 1184, 550], radius=8, fill=pal["block_bg"], outline=pal["border"], width=1)
    draw.text((808, 432), "SIGNAL / 1-2-5 GRID", fill=pal["subtle"], font=f_mono_xs)
    draw.text((1106, 432), "1280x640", fill=pal["subtle"], font=f_mono_xs)
    for gy in (468, 502, 536):
        draw.line([(808, gy), (1168, gy)], fill=pal["border"], width=1)
    draw.polygon([*_WAVE_POINTS, (_WAVE_POINTS[-1][0], 536), (_WAVE_POINTS[0][0], 536)], fill=pal["accent_tint"])
    draw.line(list(_WAVE_POINTS), fill=accent, width=3)
    for x, y in _WAVE_POINTS[::2]:
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=pal["panel_bg"], outline=accent, width=2)


def render_social_png(config: dict[str, Any], out_path: Path, *, theme: str = "white") -> Path:
    """Render a 1280x640 RGB PNG social card using lazy-imported Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        from PIL.PngImagePlugin import PngInfo
    except ImportError as exc:
        raise RuntimeError("Pillow is required for render_social_png(); install with: pip install pillow") from exc

    if theme not in _THEMES:
        raise ValueError(f"Unsupported theme {theme!r}; expected one of {tuple(_THEMES)}")
    pal = _THEMES[theme]
    meta = _extract_meta(config, theme=theme)
    accent = meta["accent"]
    canvas = Image.new("RGB", (1280, 640), pal["bg"])
    draw = ImageDraw.Draw(canvas)

    f_title, f_sub = _load_font(ImageFont, _BOLD_FONTS, 44), _load_font(ImageFont, _REG_FONTS, 21)
    f_url, f_pill = _load_font(ImageFont, _MONO_FONTS, 14), _load_font(ImageFont, _MONO_FONTS, 13)
    f_bold_sm, f_mono_sm, f_mono_xs = (
        _load_font(ImageFont, _BOLD_FONTS, 16),
        _load_font(ImageFont, _MONO_FONTS, 13),
        _load_font(ImageFont, _MONO_FONTS, 12),
    )

    draw.rounded_rectangle([32, 32, 1248, 608], radius=16, fill=pal["card_bg"], outline=pal["border"], width=1)
    for gx in range(96, 1216, 80):
        draw.line([(gx, 33), (gx, 607)], fill=pal["grid"], width=1)
    for gy in range(96, 600, 80):
        draw.line([(33, gy), (1247, gy)], fill=pal["grid"], width=1)
    draw.line([(736, 68), (736, 572)], fill=pal["border"], width=1)

    draw.rectangle([72, 72, 116, 78], fill=accent)
    eye = _fit_eyebrow(meta["eyebrow"])
    if draw.textbbox((0, 0), eye, font=f_pill)[2] > 572:
        eye = _wrap_px(draw, meta["eyebrow"], f_pill, 572, max_lines=1)[0]
    draw.text((128, 68), eye, fill=accent, font=f_pill)
    title_lines = _wrap_px(draw, meta["title"], f_title, 628, max_lines=3)
    for idx, line in enumerate(title_lines):
        draw.text((72, 102 + idx * 54), line, fill=pal["ink"], font=f_title)
    sy = 102 + len(title_lines) * 54 + 16
    for idx, line in enumerate(_wrap_px(draw, meta["subtitle"], f_sub, 628, max_lines=3)):
        draw.text((72, sy + idx * 30), line, fill=pal["muted"], font=f_sub)

    px = 72
    for idx, raw_pill in enumerate(meta["pills"]):
        pill = raw_pill[:26]
        pw = max(84, draw.textbbox((0, 0), pill, font=f_pill)[2] + 28)
        if px + pw > 708:
            break
        bg = pal["accent_tint"] if idx == 0 else pal["pill_bg"]
        br = accent if idx == 0 else pal["pill_border"]
        fg = accent if idx == 0 else pal["pill_ink"]
        draw.rounded_rectangle([px, 468, px + pw, 500], radius=6, fill=bg, outline=br, width=1)
        tw = draw.textbbox((0, 0), pill, font=f_pill)[2]
        draw.text((px + (pw - tw) // 2, 476), pill, fill=fg, font=f_pill)
        px += pw + 10

    draw.line([(72, 534), (700, 534)], fill=pal["border"], width=1)
    draw.text((72, 548), meta["url"][:58], fill=pal["subtle"], font=f_url)
    _draw_png_panel(draw, meta, pal, (f_bold_sm, f_mono_sm, f_mono_xs))

    dest = Path(out_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    png_meta = PngInfo()
    canvas.save(dest, format="PNG", optimize=True, pnginfo=png_meta)
    if dest.stat().st_size > 250 * 1024:
        canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(
            dest, format="PNG", optimize=True, pnginfo=png_meta
        )
    return dest
