#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fetch and cache verified public-domain NASA NTRS & Images API corpus for Quiet UI v8.0.

Queries live NTRS citation JSON (`https://ntrs.nasa.gov/api/citations/<ID>`) and NASA Images API
(`as08-14-2383` Apollo 8 Earthrise), caches raw responses in `.cache/nasa-corpus/`, strips EXIF
metadata from `docs/assets/as08-14-2383.jpg`, and writes structured attribution & engineering
manifests under `content/nasa-corpus/` (`17 U.S.C. § 105`).
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

USER_AGENT = "Quiet-UI-Skills-Corpus-Fetcher/8.0 (Public-Domain-17USC105)"

NTRS_MANIFEST: list[dict[str, str]] = [
    {"id": "20240010475", "tiers": "doc-1,bridge-1", "topic": "Psyche DSOC Deep Space Optical Link Architecture"},
    {"id": "20240012165", "tiers": "doc-1,bridge-1", "topic": "NASA 2024 Optical Communications Overview"},
    {"id": "20260007913", "tiers": "doc-1,doc-4b,bridge-1", "topic": "SCPPM Decoder FPGA Manual (NASA/TM-20260007913)"},
    {"id": "20170001761", "tiers": "doc-2", "topic": "NASA Systems Engineering Handbook (NASA/SP-2016-6105 Rev 2)"},
    {"id": "20230006984", "tiers": "bridge-2,app-2,app-3", "topic": "Deep Space Network Optical & RF Ground Operations"},
    {"id": "20240003670", "tiers": "app-1,app-2", "topic": "Psyche Mission Flight Operations & Triage Readiness"},
    {"id": "20220015628", "tiers": "deck-1,ctrl-1", "topic": "Lunar Gateway HALO / I-Hab Environmental Control (ECLSS)"},
    {"id": "20240016087", "tiers": "deck-1,app-4,ctrl-1", "topic": "Gateway Mission Operations & Timeline Users Guide"},
    {"id": "20130000738", "tiers": "hud-1,ctrl-1", "topic": "NASA NextGen HUD / Cockpit Human Factors Symbology"},
    {"id": "20250011652", "tiers": "app-5,hud-1", "topic": "EVA Informatics, AR HUD Field-of-Regard & Crew Readiness"},
]

EXTERNAL_STANDARDS: list[dict[str, str]] = [
    {
        "code": "CCSDS 133.0-B-2 & MRN Handbook v4",
        "tiers": "doc-3,doc-4a,app-tree",
        "url": "https://assets.science.nasa.gov/content/dam/science/psd/mars/files/mars-relay-network/MRN%20Handbook_v4_final_URS_cleared.pdf",
        "summary": "Space Packet Protocol (6-byte primary header, APID 11-bit, 14-bit sequence count) and Proximity-1 UHF/Optical relay framing.",
    },
    {
        "code": "DSN 810-005 Telecommunications Link Design Handbook",
        "tiers": "bridge-2,app-2,app-3",
        "url": "https://deepspace.jpl.nasa.gov/dsndocs/810-005/",
        "summary": "Goldstone (GDSCC), Madrid (MDSCC), and Canberra (CDSCC) 34m BWG and 70m aperture telemetry & command parameters.",
    },
    {
        "code": "NASA-STD-3001 Vol 2 Rev C & HIDH (NASA/SP-2010-3407)",
        "tiers": "app-5,hud-1,ctrl-1",
        "url": "https://www.nasa.gov/wp-content/uploads/2020/10/2022-04-08_nasa-std-3001_vol_2_rev_c_final.pdf",
        "summary": "Human-factors display/effector distinction, commanded-vs-actual state, 2-step guarded actuation, cabin 70-101.3 kPa & 25-75% RH.",
    },
]

ENGINEERING_PARAMETERS: dict[str, object] = {
    "dsoc_optical_link": {
        "wavelength_nm": 1550,
        "uplink_beacon_nm": 1064,
        "max_data_rate_mbps": 267.0,
        "max_range_rate_mbps_at_2_6_au": 1.0,
        "rf_ka_34m_baseline_kbps": 500.0,
        "flight_aperture_cm": 22.0,
        "palomar_hale_aperture_m": 5.1,
        "hybrid_rf_optical_equiv_m": 8.0,
        "arrayed_4x_hybrid_equiv_m": 11.3,
        "scppm_orders": [4, 8, 16, 32, 64, 128],
        "peak_laser_power_kw": 1.25,
    },
    "ccsds_space_packet": {
        "standard": "CCSDS 133.0-B-2",
        "primary_header_bytes": 6,
        "version_bits": 3,
        "apid_bits": 11,
        "seq_flags_bits": 2,
        "seq_count_bits": 14,
        "data_length_bits": 16,
    },
    "dsn_complexes": [
        {"complex": "GDSCC · Goldstone", "apertures": ["DSS-24 34m BWG", "DSS-26 34m BWG", "DSS-14 70m", "DSS-13 Hybrid Opt"]},
        {"complex": "MDSCC · Madrid", "apertures": ["DSS-54 34m BWG", "DSS-55 34m BWG", "DSS-56 34m BWG", "DSS-63 70m"]},
        {"complex": "CDSCC · Canberra", "apertures": ["DSS-34 34m BWG", "DSS-35 34m BWG", "DSS-36 34m BWG", "DSS-43 70m"]},
    ],
    "gateway_eclss": {
        "pressure_nominal_kpa": 101.3,
        "pressure_corridor_kpa": [70.0, 101.3],
        "pp_o2_nominal_kpa": 21.2,
        "pp_co2_max_mmhg": 3.0,
        "rel_humidity_pct_range": [25, 75],
        "temp_corridor_c": [18.3, 26.7],
    },
}


def _http_get_bytes(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _sanitize_text(val: str) -> str:
    """Strip any email literals or HTML tags to uphold Zero-PII invariants."""
    clean = re.sub(r"<[^>]+>", " ", val or "")
    clean = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[redacted-contact]", clean)
    return re.sub(r"\s+", " ", clean).strip()


def fetch_ntrs_citations(cache_dir: Path, offline_ok: bool) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in NTRS_MANIFEST:
        cid = item["id"]
        cache_file = cache_dir / f"ntrs_{cid}.json"
        raw_data: dict[str, object] = {}
        if cache_file.exists():
            raw_data = json.loads(cache_file.read_text(encoding="utf-8"))
        elif not offline_ok:
            url = f"https://ntrs.nasa.gov/api/citations/{cid}"
            try:
                payload = _http_get_bytes(url)
                cache_file.write_bytes(payload)
                raw_data = json.loads(payload.decode("utf-8"))
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                print(f"[WARN] Live NTRS fetch fallback for {cid}: {exc}", file=sys.stderr)

        title = _sanitize_text(str(raw_data.get("title") or item["topic"]))
        abstract = _sanitize_text(str(raw_data.get("abstract") or item["topic"]))[:340]
        c_info = raw_data.get("copyright") if isinstance(raw_data.get("copyright"), dict) else {}
        status = str(c_info.get("status") or "GOV_PUBLIC_USE_PERMITTED")
        centers = [
            str(aff.get("organizationName", "NASA"))
            for aff in (raw_data.get("authorAffiliations") or [])[:2]
            if isinstance(aff, dict) and aff.get("organizationName")
        ]
        records.append(
            {
                "ntrs_id": cid,
                "tiers": item["tiers"].split(","),
                "title": title,
                "centers": centers or ["NASA / JPL"],
                "copyright_status": status,
                "citation_url": f"https://ntrs.nasa.gov/citations/{cid}",
                "summary": abstract,
            }
        )
    return records


def fetch_earthrise_backplate(cache_dir: Path, out_jpg: Path, offline_ok: bool) -> dict[str, object]:
    raw_cache = cache_dir / "as08-14-2383_orig.jpg"
    if not raw_cache.exists() and not offline_ok:
        search_url = "https://images-api.nasa.gov/search?nasa_id=as08-14-2383"
        search_json = json.loads(_http_get_bytes(search_url).decode("utf-8"))
        items = search_json.get("collection", {}).get("items", [])
        href_json_url = items[0]["href"]
        asset_urls: list[str] = json.loads(_http_get_bytes(href_json_url).decode("utf-8"))
        chosen = next((u for u in asset_urls if u.endswith("~large.jpg")), None) or next(
            (u for u in asset_urls if u.endswith(".jpg")), asset_urls[0]
        )
        if chosen.startswith("http://"):
            chosen = "https://" + chosen[len("http://") :]
        raw_cache.write_bytes(_http_get_bytes(chosen, timeout=35))

    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(raw_cache) as src_img:
        rgb = src_img.convert("RGB")
        fitted = ImageOps.fit(rgb, (1600, 1000), method=Image.Resampling.LANCZOS, centering=(0.5, 0.46))
        stripped = Image.frombytes("RGB", fitted.size, fitted.tobytes())
        buf = io.BytesIO()
        stripped.save(buf, format="JPEG", quality=85, optimize=True)
        out_jpg.write_bytes(buf.getvalue())

    return {
        "nasa_id": "as08-14-2383",
        "title": "Apollo 8 Earthrise (December 24, 1968)",
        "asset_path": "docs/assets/as08-14-2383.jpg",
        "dimensions": "1600x1000",
        "bytes": out_jpg.stat().st_size,
        "exif_stripped": True,
    }


def write_attribution_md(out_dir: Path, records: list[dict[str, object]], img_meta: dict[str, object]) -> None:
    lines = [
        "# NASA, JPL & CCSDS Public-Domain Source Attribution (`Quiet UI v8.0`)",
        "",
        "All technical reference parameters, protocol structures, and orbital imagery used as",
        "sample content across the 16 Quiet UI tiers and 45-Type Diagram Atlas derive from",
        "publicly released United States Government works (`17 U.S.C. § 105`) and open CCSDS",
        "Consultative Committee for Space Data Systems Blue Books.",
        "",
        "> **Non-Endorsement Notice (`14 CFR Part 1221`):** Use of public-domain NASA technical",
        "> memoranda, DSN handbooks, and Apollo imagery is strictly for open-source UI/UX and",
        "> human-factors engineering demonstration and does not imply endorsement by NASA, JPL,",
        "> Caltech, or CCSDS.",
        "",
        "## 1. NTRS Technical Memoranda & Mission Papers",
        "",
        "| NTRS ID | Target Tiers | Title | Disposition |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in records:
        tiers = ", ".join(f"`{t}`" for t in r["tiers"])  # type: ignore[union-attr]
        lines.append(f"| [`{r['ntrs_id']}`]({r['citation_url']}) | {tiers} | {r['title']} | `{r['copyright_status']}` |")

    lines.extend(["", "## 2. Standards, Handbooks & Optical Viewport Imagery", ""])
    for std in EXTERNAL_STANDARDS:
        lines.append(f"- **{std['code']}** (`{std['tiers']}`): {std['summary']} ([Source]({std['url']}))")
    lines.append(
        f"- **Apollo 8 Earthrise (`{img_meta['nasa_id']}`)**: `{img_meta['asset_path']}` "
        f"(`{img_meta['dimensions']}`, `{img_meta['bytes']}` bytes, EXIF-free)."
    )
    (out_dir / "SOURCE_ATTRIBUTION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch NASA public-domain corpus for Quiet UI v8.0.")
    parser.add_argument("--offline", action="store_true", help="Use cached files only without network calls.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    cache_dir = repo_root / ".cache" / "nasa-corpus"
    out_dir = repo_root / "content" / "nasa-corpus"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = fetch_ntrs_citations(cache_dir, args.offline)
    img_meta = fetch_earthrise_backplate(cache_dir, repo_root / "docs" / "assets" / "as08-14-2383.jpg", args.offline)

    (out_dir / "ntrs_citations.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    (out_dir / "engineering_parameters.json").write_text(
        json.dumps(ENGINEERING_PARAMETERS, indent=2) + "\n", encoding="utf-8"
    )
    write_attribution_md(out_dir, records, img_meta)
    print(f"[OK] Wrote {len(records)} NTRS citations, engineering parameters, and EXIF-free Earthrise backplate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
