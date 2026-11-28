# SPDX-License-Identifier: Apache-2.0
"""Schema validation, sanitization, and normalization for Quiet UI project-site configs."""

from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path
from typing import Any

SCHEMA_URI = "urn:quiet-ui:schema:v9:project-site"
DEFAULT_ACCENT_HEX = "#1D4ED8"
DEFAULT_SOCIAL_WIDTH = 1280
DEFAULT_SOCIAL_HEIGHT = 640

_OCTET = r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"
_PRIVATE_IPV4_RE = re.compile(
    rf"(?<![0-9.])(?:10\.{_OCTET}|127\.{_OCTET}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.{_OCTET}\.{_OCTET}(?![0-9.])"
)
_PRIVATE_DOMAIN_RE = re.compile(r"(?i)\.(?:lan|local)(?=$|[^a-z0-9_-])")
_PRIVATE_PATH_RE = re.compile(r"(?:/home/|/Users/)")
_BRAIN_ID_RE = re.compile(r"(?i)\bbrain:")
_DEADBOLT_RE = re.compile(r"(?i)\bdeadbolt\b")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
_DIAGRAM_PATH_KEYS = ("path", "src", "file", "svg_path", "image_path")


def _check_string_for_private_tokens(text: str, json_path: str) -> None:
    checks = (
        (_PRIVATE_IPV4_RE, "RFC1918/loopback IPv4 address"),
        (_PRIVATE_DOMAIN_RE, "private .lan/.local hostname"),
        (_PRIVATE_PATH_RE, "local filesystem home prefix (/home/ or /Users/)"),
        (_BRAIN_ID_RE, "private brain: identifier"),
        (_DEADBOLT_RE, "internal deadbolt token"),
    )
    for pattern, label in checks:
        if pattern.search(text):
            raise ValueError(f"Disallowed {label} in config at {json_path}")


def _assert_no_private_tokens(value: Any, json_path: str = "$") -> None:
    if isinstance(value, str):
        _check_string_for_private_tokens(value, json_path)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _assert_no_private_tokens(item, f"{json_path}[{idx}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                _check_string_for_private_tokens(key, f"{json_path}.<key:{key}>")
            _assert_no_private_tokens(item, f"{json_path}.{key}")


def _validate_confined_path(raw_path: Any, base_dir: Path, field_name: str) -> str:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError(f"{field_name} must be a non-empty relative path string")
    if "\x00" in raw_path:
        raise ValueError(f"{field_name} contains null byte")
    if raw_path.startswith(("/", "\\")) or _WINDOWS_DRIVE_RE.match(raw_path):
        raise ValueError(f"{field_name} must be a relative path, got {raw_path!r}")
    rel_candidate = Path(raw_path)
    if rel_candidate.is_absolute():
        raise ValueError(f"{field_name} must be a relative path, got {raw_path!r}")
    resolved = (base_dir / rel_candidate).resolve()
    if not resolved.is_relative_to(base_dir) or resolved == base_dir:
        raise ValueError(f"{field_name} escapes base_dir: {raw_path!r}")
    return resolved.relative_to(base_dir).as_posix()


def _expect_dict(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return value


def _expect_str(value: Any, field_name: str, default: str = "") -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def _expect_bool(value: Any, field_name: str, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _expect_pos_int(value: Any, field_name: str, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _expect_str_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    out: list[str] = []
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{field_name}[{idx}] must be a string")
        out.append(item)
    return out


def _assert_safe_url(raw: Any, json_path: str) -> str:
    """Reject protocol-relative URLs and non-http(s) schemes via ValueError."""
    val = _expect_str(raw, json_path, "").strip()
    if not val:
        return ""
    cleaned = re.sub(r"[\x00-\x20\x7f\s]", "", val)
    if not cleaned or cleaned.startswith(("//", "\\\\", "/\\", "\\/")):
        raise ValueError(f"Disallowed protocol-relative URL at {json_path}: {val!r}")
    parsed = urllib.parse.urlsplit(cleaned)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(f"Disallowed URL scheme {parsed.scheme!r} at {json_path}: {val!r}")
    if ":" in re.split(r"[/?#]", cleaned, maxsplit=1)[0] and not parsed.scheme:
        raise ValueError(f"Disallowed URL scheme at {json_path}: {val!r}")
    return val


def _normalize_url_items(
    items: list[Any], field_name: str, url_keys: tuple[str, ...] = ("href",), *, allow_str: bool = False, str_is_url: bool = False
) -> list[Any]:
    out: list[Any] = []
    for idx, entry in enumerate(items):
        if allow_str and isinstance(entry, str):
            out.append(_assert_safe_url(entry, f"{field_name}[{idx}]") if str_is_url else entry)
            continue
        item = dict(_expect_dict(entry, f"{field_name}[{idx}]"))
        for key in url_keys:
            if item.get(key) is not None:
                item[key] = _assert_safe_url(item[key], f"{field_name}[{idx}].{key}")
        out.append(item)
    return out


def _normalize_project(raw: dict[str, Any]) -> dict[str, Any]:
    proj = _expect_dict(raw.get("project"), "project")
    out = dict(proj)
    for key in ("slug", "title", "tagline", "version", "repo_url", "site_url", "license_summary"):
        val = _expect_str(proj.get(key), f"project.{key}", "")
        out[key] = _assert_safe_url(val, f"project.{key}") if key in ("repo_url", "site_url") else val
    raw_updated = proj.get("updated_at")
    out["updated_at"] = _expect_str(raw_updated, "project.updated_at", "").strip()
    return out


def _normalize_pillars(raw_pillars: Any) -> list[dict[str, Any]]:
    if raw_pillars is None:
        return []
    if not isinstance(raw_pillars, list):
        raise ValueError("hub.pillars must be a list")
    out: list[dict[str, Any]] = []
    for idx, entry in enumerate(raw_pillars):
        item = _expect_dict(entry, f"hub.pillars[{idx}]")
        norm = dict(item)
        for key in ("id", "title", "desc", "href", "badge", "status"):
            val = _expect_str(item.get(key), f"hub.pillars[{idx}].{key}", "")
            if key == "href":
                norm[key] = _assert_safe_url(val, f"hub.pillars[{idx}].{key}")
            elif key == "status":
                norm[key] = val.strip().lower()
            else:
                norm[key] = val
        out.append(norm)
    return out


def _normalize_hub(raw: dict[str, Any]) -> dict[str, Any]:
    hub = _expect_dict(raw.get("hub"), "hub")
    raw_projects = hub.get("projects")
    if raw_projects is None:
        raw_projects = []
    if not isinstance(raw_projects, list):
        raise ValueError("hub.projects must be a list")
    projects: list[dict[str, Any]] = []
    for idx, entry in enumerate(raw_projects):
        item = _expect_dict(entry, f"hub.projects[{idx}]")
        norm = dict(item)
        for key in ("slug", "title", "tagline", "url", "badge"):
            val = _expect_str(item.get(key), f"hub.projects[{idx}].{key}", "")
            norm[key] = _assert_safe_url(val, f"hub.projects[{idx}].{key}") if key == "url" else val
        norm["current"] = _expect_bool(item.get("current"), f"hub.projects[{idx}].current", False)
        projects.append(norm)
    out = dict(hub)
    out["label"] = _expect_str(hub.get("label"), "hub.label", "")
    out["hub_url"] = _assert_safe_url(hub.get("hub_url"), "hub.hub_url")
    out["projects"] = projects
    out["pillars"] = _normalize_pillars(hub.get("pillars"))
    return out


def _normalize_demo_wrapper(raw: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    dw = _expect_dict(raw.get("demo_wrapper"), "demo_wrapper")
    enabled = _expect_bool(dw.get("enabled"), "demo_wrapper.enabled", False)
    raw_entry = dw.get("entry_path")
    if raw_entry is None or raw_entry == "":
        if enabled:
            raise ValueError("demo_wrapper.entry_path is required when demo_wrapper.enabled is True")
        entry_path = ""
    else:
        entry_path = _validate_confined_path(raw_entry, base_dir, "demo_wrapper.entry_path")
    raw_links = dw.get("topbar_links")
    if raw_links is None:
        raw_links = []
    if not isinstance(raw_links, list):
        raise ValueError("demo_wrapper.topbar_links must be a list")
    out = dict(dw)
    out["enabled"] = enabled
    out["entry_path"] = entry_path
    out["docs_base"] = _expect_str(dw.get("docs_base"), "demo_wrapper.docs_base", "")
    out["default_studio_view"] = _expect_str(dw.get("default_studio_view"), "demo_wrapper.default_studio_view", "")
    out["topbar_links"] = _normalize_url_items(raw_links, "demo_wrapper.topbar_links")
    return out


def _normalize_routes(raw: dict[str, Any], demo_enabled: bool) -> dict[str, Any]:
    routes = _expect_dict(raw.get("routes"), "routes")
    ov = _expect_dict(routes.get("overview"), "routes.overview")
    dm = _expect_dict(routes.get("demo"), "routes.demo")
    dc = _expect_dict(routes.get("docs"), "routes.docs")
    out = dict(routes)
    out["overview"] = {
        **ov,
        "href": _assert_safe_url(_expect_str(ov.get("href"), "routes.overview.href", "index.html"), "routes.overview.href"),
        "label": _expect_str(ov.get("label"), "routes.overview.label", "Overview"),
    }
    out["demo"] = {
        **dm,
        "href": _assert_safe_url(_expect_str(dm.get("href"), "routes.demo.href", "demo/"), "routes.demo.href"),
        "label": _expect_str(dm.get("label"), "routes.demo.label", "Demo"),
        "enabled": _expect_bool(dm.get("enabled"), "routes.demo.enabled", demo_enabled),
        "legacy_query_keys": _expect_str_list(dm.get("legacy_query_keys"), "routes.demo.legacy_query_keys"),
    }
    out["docs"] = {
        **dc,
        "href": _assert_safe_url(_expect_str(dc.get("href"), "routes.docs.href", "docs/"), "routes.docs.href"),
        "label": _expect_str(dc.get("label"), "routes.docs.label", "Docs"),
    }
    return out


def _normalize_cta(value: Any, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    cta = _expect_dict(value, field_name)
    out = dict(cta)
    out["label"] = _expect_str(cta.get("label"), f"{field_name}.label", "")
    out["href"] = _assert_safe_url(cta.get("href"), f"{field_name}.href")
    return out


def _normalize_diagram_entry(entry: Any, base_dir: Path, idx: int) -> str | dict[str, Any]:
    field = f"overview.architecture_diagrams[{idx}]"
    if isinstance(entry, str):
        return _validate_confined_path(entry, base_dir, field)
    if not isinstance(entry, dict) or not entry:
        raise ValueError(f"{field} must be a relative path string or non-empty object")
    norm = dict(entry)
    for key in _DIAGRAM_PATH_KEYS:
        if key in norm and norm[key] is not None:
            norm[key] = _validate_confined_path(norm[key], base_dir, f"{field}.{key}")
    for text_key in ("id", "title", "caption", "alt", "svg"):
        if text_key in norm and norm[text_key] is not None:
            norm[text_key] = _expect_str(norm[text_key], f"{field}.{text_key}", "")
    return norm


def _normalize_overview(raw: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    ov = _expect_dict(raw.get("overview"), "overview")
    out = dict(ov)
    for key in ("kicker", "headline", "summary"):
        out[key] = _expect_str(ov.get(key), f"overview.{key}", "")
    for cta_key in ("primary_cta", "secondary_cta", "tertiary_cta"):
        out[cta_key] = _normalize_cta(ov.get(cta_key), f"overview.{cta_key}")
    cmd_pills = ov.get("command_pills") or []
    if not isinstance(cmd_pills, list) or any(not isinstance(x, (str, dict)) for x in cmd_pills):
        raise ValueError("overview.command_pills must be a list of strings or objects")
    out["command_pills"] = _normalize_url_items(cmd_pills, "overview.command_pills", allow_str=True)
    steps = ov.get("quickstart_steps") or []
    if not isinstance(steps, list) or any(not isinstance(x, dict) for x in steps):
        raise ValueError("overview.quickstart_steps must be a list of objects")
    out["quickstart_steps"] = [dict(x) for x in steps]
    install_cmds = ov.get("install_commands") or []
    if not isinstance(install_cmds, list) or any(not isinstance(x, (str, dict)) for x in install_cmds):
        raise ValueError("overview.install_commands must be a list of strings or objects")
    out["install_commands"] = [dict(x) if isinstance(x, dict) else x for x in install_cmds]
    blocks = ov.get("plain_language_blocks") or []
    if not isinstance(blocks, list) or any(not isinstance(x, (str, dict)) for x in blocks):
        raise ValueError("overview.plain_language_blocks must be a list of strings or objects")
    out["plain_language_blocks"] = _normalize_url_items(blocks, "overview.plain_language_blocks", allow_str=True)
    previews = ov.get("domain_previews") or []
    if not isinstance(previews, list):
        raise ValueError("overview.domain_previews must be a list")
    out["domain_previews"] = _normalize_url_items(previews, "overview.domain_previews")
    diagrams = ov.get("architecture_diagrams") or []
    if not isinstance(diagrams, list):
        raise ValueError("overview.architecture_diagrams must be a list")
    out["architecture_diagrams"] = [_normalize_diagram_entry(d, base_dir, i) for i, d in enumerate(diagrams)]
    return out


def _normalize_docs_reader(raw: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    dr = _expect_dict(raw.get("docs_reader"), "docs_reader")
    raw_sources = dr.get("sources")
    if raw_sources is None:
        raw_sources = []
    if not isinstance(raw_sources, list):
        raise ValueError("docs_reader.sources must be a list")
    sources: list[dict[str, Any]] = []
    for idx, entry in enumerate(raw_sources):
        src = _expect_dict(entry, f"docs_reader.sources[{idx}]")
        norm_path = _validate_confined_path(src.get("path"), base_dir, f"docs_reader.sources[{idx}].path")
        stem = Path(norm_path).with_suffix("").as_posix()
        default_id = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") or f"doc-{idx + 1}"
        norm = dict(src)
        norm["path"] = norm_path
        norm["id"] = _expect_str(src.get("id"), f"docs_reader.sources[{idx}].id", default_id)
        norm["title"] = _expect_str(src.get("title"), f"docs_reader.sources[{idx}].title", Path(norm_path).stem)
        sources.append(norm)
    raw_jumps = dr.get("quick_jumps")
    if raw_jumps is None:
        raw_jumps = []
    if not isinstance(raw_jumps, list) or any(not isinstance(x, (str, dict)) for x in raw_jumps):
        raise ValueError("docs_reader.quick_jumps must be a list of strings or objects")
    out = dict(dr)
    out["title"] = _expect_str(dr.get("title"), "docs_reader.title", "Documentation")
    out["subtitle"] = _expect_str(dr.get("subtitle"), "docs_reader.subtitle", "")
    out["sources"] = sources
    out["quick_jumps"] = _normalize_url_items(raw_jumps, "docs_reader.quick_jumps", ("target", "href"), allow_str=True, str_is_url=True)
    return out


def _normalize_social_preview(raw: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    sp = _expect_dict(raw.get("social_preview"), "social_preview")
    raw_img = sp.get("image_path")
    if raw_img is None or raw_img == "":
        image_path = ""
    else:
        image_path = _validate_confined_path(raw_img, base_dir, "social_preview.image_path")
    accent_hex = _expect_str(sp.get("accent_hex"), "social_preview.accent_hex", DEFAULT_ACCENT_HEX)
    if accent_hex and not _HEX_COLOR_RE.match(accent_hex):
        raise ValueError(f"social_preview.accent_hex must be a #RGB or #RRGGBB hex color, got {accent_hex!r}")
    out = dict(sp)
    out["image_path"] = image_path
    out["width"] = _expect_pos_int(sp.get("width"), "social_preview.width", DEFAULT_SOCIAL_WIDTH)
    out["height"] = _expect_pos_int(sp.get("height"), "social_preview.height", DEFAULT_SOCIAL_HEIGHT)
    out["eyebrow"] = _expect_str(sp.get("eyebrow"), "social_preview.eyebrow", "")
    out["title"] = _expect_str(sp.get("title"), "social_preview.title", "")
    out["subtitle"] = _expect_str(sp.get("subtitle"), "social_preview.subtitle", "")
    out["pills"] = _expect_str_list(sp.get("pills"), "social_preview.pills")
    out["accent_hex"] = accent_hex or DEFAULT_ACCENT_HEX
    return out


def _normalize_user_menu(raw: dict[str, Any], project: dict[str, Any]) -> dict[str, str]:
    um = _expect_dict(raw.get("user_menu"), "user_menu")
    label = _expect_str(um.get("label"), "user_menu.label", "").strip()
    profile_url = _assert_safe_url(um.get("profile_url"), "user_menu.profile_url")
    repo_label = _expect_str(um.get("repo_label"), "user_menu.repo_label", "GitHub Repository").strip() or "GitHub Repository"
    if not label or not profile_url:
        parsed = urllib.parse.urlsplit(str(project.get("repo_url") or ""))
        seg = [p for p in parsed.path.split("/") if p]
        owner = seg[0] if (parsed.netloc.lower() == "github.com" and seg) else ""
        if not label:
            label = f"@{owner}" if owner else "@owner"
        if not profile_url and owner:
            profile_url = f"https://github.com/{owner}"
    return {"label": label, "profile_url": profile_url, "repo_label": repo_label}


def load_site_config(config_path: Path) -> dict[str, Any]:
    """Load, validate, sanitize, and normalize a Quiet UI v9.8.0 project-site config."""
    resolved_path = Path(config_path).resolve()
    raw_text = resolved_path.read_text(encoding="utf-8")
    raw = json.loads(raw_text)
    if not isinstance(raw, dict):
        raise ValueError("Site config root must be a JSON object")
    if raw.get("$schema") != SCHEMA_URI:
        raise ValueError(f"Config $schema must equal {SCHEMA_URI!r}, got {raw.get('$schema')!r}")

    _assert_no_private_tokens(raw)
    base_dir = resolved_path.parent
    project = _normalize_project(raw)
    demo_wrapper = _normalize_demo_wrapper(raw, base_dir)

    return {
        "$schema": SCHEMA_URI,
        "base_dir": str(base_dir),
        "project": project,
        "hub": _normalize_hub(raw),
        "user_menu": _normalize_user_menu(raw, project),
        "routes": _normalize_routes(raw, demo_wrapper["enabled"]),
        "overview": _normalize_overview(raw, base_dir),
        "docs_reader": _normalize_docs_reader(raw, base_dir),
        "demo_wrapper": demo_wrapper,
        "social_preview": _normalize_social_preview(raw, base_dir),
    }
