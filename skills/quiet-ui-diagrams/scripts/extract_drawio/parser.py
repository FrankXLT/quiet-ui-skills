# SPDX-License-Identifier: MIT
"""Parsing mxGraphModel XML structures into normalized Node and Edge graphs.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .loader import (
    MAX_CELLS_PER_PAGE,
    MAX_PAGES,
    _inflate,
    _reject_unsafe_xml,
    load_mxfile,
)
from .models import Edge, Node, Page, _fail, classify_shape
from .style_helpers import _num, clean_label, parse_style


def parse_page(diagram: ET.Element, index: int) -> Page:
    name = diagram.get("name") or f"Page-{index + 1}"
    page = Page(id=diagram.get("id") or f"page-{index}", name=name, index=index)

    model = diagram.find(".//mxGraphModel")
    if model is None:
        text = (diagram.text or "").strip()
        inflated = _inflate(text) if text else None
        if not inflated:
            return page
        _reject_unsafe_xml(inflated, f"page {index}")
        model = ET.fromstring(inflated)
        if model.tag != "mxGraphModel":
            found = model.find(".//mxGraphModel")
            if found is None:
                return page
            model = found

    root = model.find("root")
    if root is None:
        return page
    if len(root) > MAX_CELLS_PER_PAGE:
        _fail(f"page {index}: cell limit exceeded (max {MAX_CELLS_PER_PAGE})")

    # Pass 1: collect raw cells, unwrapping <object>/<UserObject> containers.
    raw: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for element in root:
        if element.tag in ("object", "UserObject"):
            cell = element.find("mxCell")
            if cell is None:
                continue
            attrs = {
                k: v
                for k, v in element.attrib.items()
                if k not in ("id", "label", "placeholders")
            }
            cid = element.get("id") or cell.get("id") or ""
            value = element.get("label", "")
        elif element.tag == "mxCell":
            cell = element
            attrs = {}
            cid = cell.get("id") or ""
            value = cell.get("value", "")
        else:
            continue
        if not cid:
            continue
        if cid in raw:
            _fail(f"page {index}: duplicate cell id")
        raw[cid] = {"cell": cell, "attrs": attrs, "value": value}
        order.append(cid)

    hidden: dict[str, bool] = {}

    def is_hidden(cid: str) -> bool:
        chain: list[str] = []
        visited: set[str] = set()
        current, result = cid, False
        while current in raw and current not in visited:
            if current in hidden:
                result = hidden[current]
                break
            chain.append(current)
            visited.add(current)
            if raw[current]["cell"].get("visible") == "0":
                result = True
                break
            current = raw[current]["cell"].get("parent") or ""
        for seen in chain:
            hidden[seen] = result
        return result

    # Pass 2: vertices (absolute geometry resolved after the pass).
    edge_label_parts: dict[str, list[str]] = {}
    relative_offsets: dict[str, tuple[float, float]] = {}
    for cid in order:
        entry = raw[cid]
        cell = entry["cell"]
        style = parse_style(cell.get("style"))
        parent = cell.get("parent")
        if is_hidden(cid) or cell.get("edge") == "1" or cell.get("vertex") != "1":
            continue
        parent_entry = raw.get(parent or "")
        parent_is_edge = bool(
            parent_entry and parent_entry["cell"].get("edge") == "1"
        )
        if parent_is_edge or "edgeLabel" in style:
            if parent:
                text = clean_label(entry["value"], is_html=style.get("html") == "1")
                if text:
                    edge_label_parts.setdefault(parent, []).append(text)
            continue

        geom = cell.find("mxGeometry")
        if geom is not None and geom.get("relative") == "1":
            offset = geom.find("mxPoint[@as='offset']")
            relative_offsets[cid] = (_num(offset, "x"), _num(offset, "y"))
        node = Node(
            id=cid,
            label=clean_label(entry["value"], is_html=style.get("html") == "1"),
            shape=classify_shape(style),
            parent=parent,
            x=_num(geom, "x"),
            y=_num(geom, "y"),
            w=_num(geom, "width"),
            h=_num(geom, "height"),
            fill=style.get("fillColor", ""),
            stroke=style.get("strokeColor", ""),
            font_color=style.get("fontColor", ""),
            dashed=style.get("dashed") == "1",
            rounded=style.get("rounded") == "1",
            container=style.get("container") == "1" or "swimlane" in style,
            link=entry["attrs"].get("link", ""),
            attrs={
                k: v
                for k, v in entry["attrs"].items()
                if k not in ("link", "tooltip")
            },
        )
        page.nodes.append(node)

    node_map = page.node_map

    # Resolve absolute geometry + depth iteratively and reuse resolved prefixes.
    resolved_by_id: dict[str, tuple[float, float, int]] = {}
    for node in page.nodes:
        chain: list[Node] = []
        active: set[str] = set()
        current = node
        while current.id not in resolved_by_id:
            if current.id in active:
                _fail(f"page {index}: parent cycle")
            active.add(current.id)
            chain.append(current)
            pnode = node_map.get(current.parent or "")
            if pnode is None:
                position = (0.0, 0.0, -1)
                break
            current = pnode
        else:
            position = resolved_by_id[current.id]

        px, py, pdepth = position
        while chain:
            current = chain.pop()
            dx, dy = current.x, current.y
            pnode = node_map.get(current.parent or "")
            if pnode is not None and current.id in relative_offsets:
                ox, oy = relative_offsets[current.id]
                dx, dy = dx * pnode.w + ox, dy * pnode.h + oy
            px, py, pdepth = dx + px, dy + py, pdepth + 1
            if not math.isfinite(px) or not math.isfinite(py):
                _fail(f"page {index}: geometry overflow")
            resolved_by_id[current.id] = (px, py, pdepth)

    for node in page.nodes:
        ax, ay, depth = resolved_by_id[node.id]
        node.x, node.y, node.depth = ax, ay, depth
        pnode = node_map.get(node.parent or "")
        if pnode is not None:
            pnode.children.append(node.id)
            pnode.container = True

    # Pass 3: edges.
    for cid in order:
        entry = raw[cid]
        cell = entry["cell"]
        if is_hidden(cid) or cell.get("edge") != "1":
            continue
        style = parse_style(cell.get("style"))
        geom = cell.find("mxGeometry")
        waypoints = 0
        if geom is not None:
            waypoints = len(
                [p for p in geom.findall(".//mxPoint") if p.get("as") is None]
            )
        label = clean_label(entry["value"], is_html=style.get("html") == "1")
        extra = edge_label_parts.get(cid, [])
        if extra:
            label = " / ".join([p for p in ([label] + extra) if p])
        source = cell.get("source")
        target = cell.get("target")
        start_head = style.get("startArrow", "none") not in ("none", "0", "")
        end_head = style.get("endArrow", "classic") not in ("none", "0", "")
        if start_head and not end_head:
            source, target = target, source
        page.edges.append(
            Edge(
                id=cid,
                source=source if source in node_map else None,
                target=target if target in node_map else None,
                label=label,
                dashed=style.get("dashed") == "1",
                bidirectional=start_head and end_head,
                undirected=not start_head and not end_head,
                style_name=style.get("shape", "")
                or ("orthogonal" if style.get("edgeStyle") else ""),
                waypoints=waypoints,
                stroke=style.get("strokeColor", ""),
            )
        )

    for edge in page.edges:
        source_node = node_map.get(edge.source or "")
        target_node = node_map.get(edge.target or "")
        if edge.bidirectional or edge.undirected:
            for endpoint in (source_node, target_node):
                if endpoint is not None:
                    endpoint.in_degree += 1
                    endpoint.out_degree += 1
        else:
            if source_node is not None:
                source_node.out_degree += 1
            if target_node is not None:
                target_node.in_degree += 1

    return page


def parse_file(path: Path) -> list[Page]:
    xml = load_mxfile(path)
    _reject_unsafe_xml(xml, path.name)
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        _fail(f"{path.name}: malformed XML ({exc})")
    if root.tag == "mxGraphModel":
        wrapper = ET.Element("diagram", {"name": path.stem, "id": "single"})
        wrapper.append(root)
        return [parse_page(wrapper, 0)]
    diagrams = root.findall("diagram")
    if not diagrams:
        _fail(f"{path.name}: mxfile contains no <diagram> pages")
    if len(diagrams) > MAX_PAGES:
        _fail(f"page limit exceeded (max {MAX_PAGES})")
    return [parse_page(d, i) for i, d in enumerate(diagrams)]
