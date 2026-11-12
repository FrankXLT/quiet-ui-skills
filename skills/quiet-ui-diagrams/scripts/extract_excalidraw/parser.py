# SPDX-License-Identifier: MIT
"""Scene loader and parser for Excalidraw documents.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    CONTAINER_TYPES,
    EDGE_TYPES,
    EXCALIDRAW_SUFFIXES,
    EXPORT_SUFFIXES,
    MAX_EDGES,
    MAX_ELEMENTS,
    MAX_INPUT_BYTES,
    MAX_NODES,
    NODE_SHAPES,
    Edge,
    Node,
    Scene,
    _fail,
    _num,
    clean_label,
    text_label,
)


def load_scene_data(path: Path) -> dict[str, Any]:
    suffix = path.suffix.casefold()
    if suffix in EXPORT_SUFFIXES:
        _fail(
            f"{path.name}: PNG/SVG exports are not supported; save the scene "
            "as .excalidraw and import that file"
        )
    if suffix not in EXCALIDRAW_SUFFIXES:
        _fail(f"{path.name}: not an Excalidraw file")
    try:
        with path.open("rb") as source:
            data = source.read(MAX_INPUT_BYTES + 1)
    except OSError as error:
        _fail(f"{path}: {error}")
    if len(data) > MAX_INPUT_BYTES:
        _fail(f"source exceeds the {MAX_INPUT_BYTES // (1024 * 1024)} MiB limit")
    try:
        document = json.loads(
            data.decode("utf-8"),
            parse_constant=lambda token: _fail(
                f"invalid geometry: {token} is not finite"
            ),
        )
    except RecursionError:
        _fail(f"{path.name}: Excalidraw JSON nesting exceeds the parser limit")
    except (UnicodeDecodeError, ValueError):
        _fail(f"{path.name}: not valid Excalidraw JSON")
    if not isinstance(document, dict) or document.get("type") != "excalidraw":
        _fail(f"{path.name}: not an Excalidraw scene (missing type: excalidraw)")
    elements = document.get("elements")
    if not isinstance(elements, list):
        _fail(f"{path.name}: scene has no elements array")
    if len(elements) > MAX_ELEMENTS:
        _fail(f"element limit exceeded (max {MAX_ELEMENTS})")
    return document


def parse_scene(path: Path, document: dict[str, Any]) -> Scene:
    scene = Scene(name=path.stem.removesuffix(".excalidraw"))
    elements = [
        element
        for element in document["elements"]
        if isinstance(element, dict) and isinstance(element.get("id"), str)
    ]

    seen_ids: set[str] = set()
    for element in elements:
        element_id = element["id"]
        if element_id in seen_ids:
            _fail("duplicate element id")
        seen_ids.add(element_id)

    live: list[dict[str, Any]] = []
    for element in elements:
        if not isinstance(element.get("type"), str):
            _fail("invalid element type: expected a string")
        if element.get("isDeleted"):
            scene.discarded["deleted_elements"] += 1
            continue
        live.append(element)

    foldable_ids = {
        element["id"]
        for element in live
        if element.get("type") in NODE_SHAPES or element.get("type") in EDGE_TYPES
    }

    bound_labels: dict[str, list[str]] = {}
    for element in live:
        if element.get("type") != "text":
            continue
        container = element.get("containerId")
        if isinstance(container, str) and container in foldable_ids:
            text = text_label(element)
            if text:
                bound_labels.setdefault(container, []).append(text)

    def label_for(element: dict[str, Any]) -> str:
        return "\n".join(bound_labels.get(element["id"], []))

    frame_ids: set[str] = set()
    for element in live:
        kind = element.get("type")
        element_id = element["id"]
        if isinstance(element.get("link"), str) and element.get("link"):
            scene.discarded["links"] += 1
        if kind in EDGE_TYPES:
            continue
        if kind == "text":
            if (
                isinstance(element.get("containerId"), str)
                and element["containerId"] in foldable_ids
            ):
                continue
            shape, label = "text", text_label(element)
        elif kind in CONTAINER_TYPES:
            frame_ids.add(element_id)
            shape = "frame"
            label = clean_label(element.get("name")) or f"Frame {len(frame_ids)}"
        elif kind in NODE_SHAPES:
            shape = NODE_SHAPES[kind]
            label = label_for(element)
            if kind == "image":
                scene.discarded["image_payloads"] += 1
            if kind in ("embeddable", "iframe"):
                scene.discarded["embeds"] += 1
        elif kind == "freedraw":
            scene.discarded["freedraw_strokes"] += 1
            continue
        elif kind in ("selection", "laser"):
            continue
        else:
            scene.discarded["unknown_elements"] += 1
            continue
        if len(scene.nodes) >= MAX_NODES:
            _fail(f"node limit exceeded (max {MAX_NODES})")
        groups = (
            [g for g in element.get("groupIds", []) if isinstance(g, str)]
            if isinstance(element.get("groupIds"), list)
            else []
        )
        scene.nodes.append(
            Node(
                id=element_id,
                label=label,
                shape=shape,
                x=_num(element, "x"),
                y=_num(element, "y"),
                w=_num(element, "width"),
                h=_num(element, "height"),
                fill=(
                    element.get("backgroundColor", "")
                    if isinstance(element.get("backgroundColor"), str)
                    else ""
                ),
                stroke=(
                    element.get("strokeColor", "")
                    if isinstance(element.get("strokeColor"), str)
                    else ""
                ),
                dashed=element.get("strokeStyle") in ("dashed", "dotted"),
                container=shape == "frame",
                groups=groups,
            )
        )

    node_map = scene.node_map

    for element in live:
        frame = element.get("frameId")
        if not isinstance(frame, str) or frame not in frame_ids:
            continue
        member = node_map.get(element["id"])
        parent = node_map.get(frame)
        if member is None or parent is None or member.id == parent.id:
            continue
        member.parent = frame
        member.depth = 1
        parent.children.append(member.id)

    def binding_id(element: dict[str, Any], key: str) -> str | None:
        binding = element.get(key)
        if isinstance(binding, dict) and isinstance(binding.get("elementId"), str):
            bound = binding["elementId"]
            return bound if bound in node_map else None
        return None

    for element in live:
        kind = element.get("type")
        if kind not in EDGE_TYPES:
            continue
        if len(scene.edges) >= MAX_EDGES:
            _fail(f"edge limit exceeded (max {MAX_EDGES})")
        default_end = "arrow" if kind == "arrow" else None
        start_head = element.get("startArrowhead")
        end_head = element.get("endArrowhead", default_end)
        if start_head is not None and not isinstance(start_head, str):
            _fail("invalid startArrowhead: expected a string or null")
        if end_head is not None and not isinstance(end_head, str):
            _fail("invalid endArrowhead: expected a string or null")
        start_bound = binding_id(element, "startBinding")
        end_bound = binding_id(element, "endBinding")
        source, target = (
            (end_bound, start_bound)
            if start_head and not end_head
            else (start_bound, end_bound)
        )
        points = element.get("points")
        waypoints = max(len(points) - 2, 0) if isinstance(points, list) else 0
        scene.edges.append(
            Edge(
                id=element["id"],
                source=source,
                target=target,
                label=label_for(element),
                dashed=element.get("strokeStyle") in ("dashed", "dotted"),
                bidirectional=bool(start_head) and bool(end_head),
                undirected=not start_head and not end_head,
                waypoints=waypoints,
                stroke=(
                    element.get("strokeColor", "")
                    if isinstance(element.get("strokeColor"), str)
                    else ""
                ),
            )
        )

    for edge in scene.edges:
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

    return scene
