# SPDX-License-Identifier: MIT
"""Export machine-readable .registry.json sidecar from data-block-* attributes.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License)
for Quiet UI Skills v7.0.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

from .xml_sanitize import TAG_ATTR_RE

BLOCK_TAG_RE = re.compile(r"<([A-Za-z][\w:.-]*)([^>]*?)>", re.DOTALL)
BLOCK_KEYS = ("id", "parent", "name", "input", "output", "constraint", "assumption", "impl")


def extract_block_registry(html: str, source_path: Path) -> dict:
    blocks: list[dict[str, str]] = []
    for tag_match in BLOCK_TAG_RE.finditer(html):
        attrs_text = tag_match.group(2)
        if "data-block-id" not in attrs_text:
            continue
        attr_dict: dict[str, str] = {}
        for attr in TAG_ATTR_RE.finditer(attrs_text):
            name, quoted = attr.group(2), attr.group(4)
            if quoted is not None:
                val = quoted[1:-1] if quoted[0] in "\"'`" else quoted
                attr_dict[name.lower()] = val.strip()

        block_id = attr_dict.get("data-block-id")
        if not block_id:
            continue
        entry: dict[str, str] = {"id": block_id}
        name = attr_dict.get("data-block-name", "")
        if name:
            entry["name"] = name
        for key in ("parent", "input", "output", "constraint", "assumption", "impl"):
            val = attr_dict.get(f"data-block-{key}", "")
            if val:
                entry[key] = val
        blocks.append(entry)

    if not blocks:
        raise ValueError(
            f"no data-block-id attributes found in {source_path.name}; "
            "registry export is only supported on Traceable block decomposition diagrams"
        )

    return {"source": source_path.name, "blocks": blocks}


def export_registry(source_path: Path, output_path: Path | None = None) -> Path:
    if not source_path.is_file():
        raise FileNotFoundError(f"source file not found: {source_path}")
    if source_path.name == "index.html" and source_path.parent.name == "assets":
        raise ValueError("refuse to export registry for assets/index.html gallery")

    html = source_path.read_text(encoding="utf-8")
    data = extract_block_registry(html, source_path)
    if output_path is None:
        target = source_path.with_name(f"{source_path.stem}.registry.json")
    else:
        target = output_path
        if not target.name.endswith(".json"):
            target = target.with_name(f"{target.stem}.registry.json")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return target
