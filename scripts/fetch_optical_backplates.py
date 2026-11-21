#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fetch, verify, crop, and EXIF-strip public-domain/CC0 optical backplates for Quiet UI v9.0.

Queries Wikimedia Commons MediaWiki API (`w/api.php`) with strict zero-attribution licensing
verification (17 U.S.C. § 105 USGov PD or CC0 1.0 ONLY, AttributionRequired == "false"),
caches raw downloads in `.cache/optical-backplates/`, crops to 1600x1000, strips 100% of
EXIF/XMP/IPTC metadata, enforces <= 185 KB per JPEG, and saves into `docs/assets/`.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter, ImageOps

USER_AGENT = "quiet-ui-skills-fetcher/9.1 (https://github.com/FrankXLT/quiet-ui-skills)"
ALLOWED_LICENSES: frozenset[str] = frozenset(
    {
        "Public domain",
        "CC0",
        "PD-USGov",
        "PD-USGov-NASA",
        "PD-USGov-Military-Air_Force",
        "PD-USGov-DOT",
        "PD-USGov-NPS",
    }
)
TARGET_SIZE = (1600, 1000)
MAX_BYTES = 180 * 1024

BACKPLATE_MANIFEST: list[dict[str, Any]] = [
    {
        "id": "hud_daylight_rwy",
        "view": "v15",
        "mode": "daylight",
        "filename": "opt_hud_daylight_rwy.jpg",
        "commons_title": "File:DF-ST-83-04217 An aerial view of the runway approach.jpeg",
        "agency": "U.S. Department of Defense (Defense Visual Information Center)",
        "crop_box": (0.0, 0.0, 0.86, 0.61),
        "sky_pad_top_frac": 0.202,
        "centering": (0.5, 0.50),
    },
    {
        "id": "hud_night_rwy",
        "view": "v15",
        "mode": "lowlight",
        "filename": "opt_hud_night_rwy.jpg",
        "commons_title": "File:KBTP at dusk.jpg",
        "agency": "Wikimedia Commons (CC0 1.0 Public Domain Dedication)",
        "crop_box": (0.04, 0.0, 0.89, 0.741),
        "centering": (0.5, 0.50),
    },
    {
        "id": "glass_day_hwy",
        "view": "v16",
        "mode": "daylight",
        "filename": "opt_glass_day_hwy.jpg",
        "commons_title": "File:A steel arch bridge over calm water (Unsplash).jpg",
        "agency": "Wikimedia Commons / Unsplash CC0 Archive",
        "crop_box": (0.24, 0.06, 0.99, 0.86),
        "centering": (0.5, 0.50),
    },
    {
        "id": "glass_dusk_hwy",
        "view": "v16",
        "mode": "dusk",
        "filename": "opt_glass_dusk_hwy.jpg",
        "commons_title": "File:Coast Guard Cutter Hamilton (15782225475).jpg",
        "agency": "U.S. Coast Guard (17 U.S.C. § 105 Public Domain)",
        "crop_box": None,
        "centering": (0.5, 0.45),
    },
    {
        "id": "glass_night_hwy",
        "view": "v16",
        "mode": "night",
        "filename": "opt_glass_night_hwy.jpg",
        "commons_title": "File:Red Night at Tran Thi Ly Bridge (Unsplash).jpg",
        "agency": "Wikimedia Commons / Unsplash CC0 Archive",
        "crop_box": None,
        "centering": (0.5, 0.5),
    },
    {
        "id": "frame_art",
        "view": "v17",
        "mode": "art",
        "filename": "opt_frame_art.jpg",
        "commons_title": "File:Albert Bierstadt, Mount Corcoran, c. 1876-1877, NGA 166428.jpg",
        "agency": "National Gallery of Art (CC0 Open Access)",
        "crop_box": None,
        "centering": (0.5, 0.48),
    },
    {
        "id": "frame_landscape",
        "view": "v17",
        "mode": "landscape",
        "filename": "opt_frame_landscape.jpg",
        "commons_title": "File:Beautiful mountain reflection (Unsplash).jpg",
        "agency": "Wikimedia Commons / Unsplash CC0 Archive",
        "crop_box": None,
        "centering": (0.5, 0.50),
    },
]


def _http_get_bytes(url: str, timeout: int = 35) -> bytes:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < 3:
                wait_s = min(15.0, float(exc.headers.get("Retry-After") or (2.5 * (attempt + 1))))
                time.sleep(wait_s)
                continue
            raise
    raise RuntimeError(f"Exhausted retries for {url}")


def _query_commons_imageinfo(file_title: str) -> dict[str, Any]:
    api_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata|mime",
            "format": "json",
        }
    )
    payload = json.loads(_http_get_bytes(api_url).decode("utf-8"))
    pages = payload.get("query", {}).get("pages", {})
    if not pages:
        raise ValueError(f"Commons API returned no pages for {file_title}")
    page = next(iter(pages.values()))
    info_list = page.get("imageinfo") or []
    if not info_list:
        raise ValueError(f"Commons API returned no imageinfo for {file_title}")
    return info_list[0]


def _verify_zero_attribution_license(info: dict[str, Any], title: str) -> tuple[str, int, int]:
    width = int(info.get("width") or 0)
    height = int(info.get("height") or 0)
    if width < 1400 or width <= height:
        raise ValueError(f"Source {title} dimensions {width}x{height} below 1400px landscape floor")
    meta = info.get("extmetadata") or {}
    lic_short = str((meta.get("LicenseShortName") or {}).get("value") or "").strip()
    attr_req = str((meta.get("AttributionRequired") or {}).get("value") or "").strip().lower()
    if lic_short not in ALLOWED_LICENSES:
        raise ValueError(f"Rejected license '{lic_short}' for {title}; allowed={sorted(ALLOWED_LICENSES)}")
    if attr_req != "false":
        raise ValueError(f"Rejected AttributionRequired='{attr_req}' for {title}; must be 'false'")
    return lic_short, width, height


def _pad_sky_top(rgb: Image.Image, pad_h: int) -> Image.Image:
    """Seamlessly extend upper sky band by mirroring real sky grain so horizon sits at 50%."""
    if pad_h <= 0:
        return rgb
    w, h = rgb.size
    sample_h = min(pad_h, h, 240)
    sky_fill = ImageOps.flip(rgb.crop((0, 0, w, sample_h))).resize((w, pad_h), Image.Resampling.BICUBIC)
    canvas = Image.new("RGB", (w, h + pad_h))
    canvas.paste(sky_fill, (0, 0))
    canvas.paste(rgb, (0, pad_h))
    blend_h = min(10, h, pad_h)
    seam = canvas.crop((0, pad_h - blend_h, w, pad_h + blend_h)).filter(ImageFilter.GaussianBlur(radius=3))
    alpha_col = Image.new("L", (1, blend_h * 2), 0)
    for yy in range(blend_h * 2):
        alpha_col.putpixel((0, yy), int(255 * max(0.0, 1.0 - abs(yy - blend_h) / max(blend_h, 1))))
    canvas.paste(seam, (0, pad_h - blend_h), alpha_col.resize((w, blend_h * 2)))
    return canvas


def _encode_exif_free_jpeg(
    src_path: Path,
    out_path: Path,
    crop_box: tuple[float, float, float, float] | None,
    centering: tuple[float, float],
    sky_pad_top_frac: float = 0.0,
) -> int:
    with Image.open(src_path) as src_img:
        rgb = src_img.convert("RGB")
        if crop_box is not None:
            w, h = rgb.size
            x0, y0, x1, y1 = crop_box
            rgb = rgb.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
        if sky_pad_top_frac > 0.0:
            rgb = _pad_sky_top(rgb, int(rgb.height * sky_pad_top_frac))
        fitted = ImageOps.fit(rgb, TARGET_SIZE, method=Image.Resampling.LANCZOS, centering=centering)
        stripped = Image.frombytes("RGB", fitted.size, fitted.tobytes())

    chosen_bytes = b""
    for quality in (82, 78, 74, 70, 66, 62, 58, 54, 50, 46):
        buf = io.BytesIO()
        stripped.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
        raw = buf.getvalue()
        if b"Exif\x00\x00" in raw:
            raise RuntimeError(f"EXIF signature leaked into {out_path.name}")
        chosen_bytes = raw
        if len(raw) <= MAX_BYTES:
            break
    if len(chosen_bytes) > MAX_BYTES:
        raise RuntimeError(f"{out_path.name} exceeds {MAX_BYTES} bytes ({len(chosen_bytes)})")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(chosen_bytes)
    return len(chosen_bytes)


def fetch_all_backplates(repo_root: Path, offline_ok: bool) -> list[dict[str, Any]]:
    cache_dir = repo_root / ".cache" / "optical-backplates"
    assets_dir = repo_root / "docs" / "assets"
    cache_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    for item in BACKPLATE_MANIFEST:
        meta_cache = cache_dir / f"{item['id']}.json"
        raw_cache = cache_dir / f"{item['id']}_orig.jpg"
        cached_info = json.loads(meta_cache.read_text(encoding="utf-8")) if (meta_cache.exists() and raw_cache.exists()) else None
        if cached_info is not None and cached_info.get("_commons_title") == item["commons_title"]:
            info = cached_info
        elif offline_ok:
            raise FileNotFoundError(f"Offline mode requested or cache stale for {item['id']} ({item['commons_title']})")
        else:
            info = _query_commons_imageinfo(item["commons_title"])
            info["_commons_title"] = item["commons_title"]
            _verify_zero_attribution_license(info, item["commons_title"])
            img_url = str(info["url"])
            raw_bytes = _http_get_bytes(img_url, timeout=45)
            meta_cache.write_text(json.dumps(info, indent=2), encoding="utf-8")
            raw_cache.write_bytes(raw_bytes)

        lic_short, src_w, src_h = _verify_zero_attribution_license(info, item["commons_title"])
        out_path = assets_dir / item["filename"]
        size_bytes = _encode_exif_free_jpeg(raw_cache, out_path, item["crop_box"], item["centering"], float(item.get("sky_pad_top_frac") or 0.0))
        records.append(
            {
                "id": item["id"],
                "view": item["view"],
                "mode": item["mode"],
                "asset_path": f"docs/assets/{item['filename']}",
                "commons_title": item["commons_title"],
                "source_url": str(info.get("descriptionurl") or ""),
                "agency": item["agency"],
                "license": lic_short,
                "attribution_required": False,
                "source_dimensions": f"{src_w}x{src_h}",
                "output_dimensions": f"{TARGET_SIZE[0]}x{TARGET_SIZE[1]}",
                "bytes": size_bytes,
                "exif_stripped": True,
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch verified PD/CC0 optical backplates for Quiet UI v9.0.")
    parser.add_argument("--offline", action="store_true", help="Use cached responses/images only.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    try:
        records = fetch_all_backplates(repo_root, offline_ok=args.offline)
    except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError, OSError) as exc:
        print(f"[FAIL] Optical backplate fetch failed: {exc}", file=sys.stderr)
        return 1

    manifest_out = repo_root / ".cache" / "optical-backplates" / "manifest.json"
    manifest_out.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    for r in records:
        print(
            f"[OK] {r['asset_path']} ({r['output_dimensions']}, {r['bytes']} B, "
            f"src={r['source_dimensions']}, license={r['license']}, exif_stripped={r['exif_stripped']})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
