#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Threaded local HTTP preview server for the Quiet UI 3-route site & Showcase."""

from __future__ import annotations

import argparse
import posixpath
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = (REPO_ROOT / "docs").resolve()
_MISSING_TARGET = str(REPO_ROOT / "__nonexistent_quiet_ui_target__")
_TRAILING_SLASH_ROUTES = frozenset({"/demo", "/docs", "/bench"})


def _resolve_confined(base: Path, rel: str) -> Path | None:
    candidate = (base / rel).resolve()
    if candidate.is_relative_to(base) and candidate.exists():
        return candidate
    return None


def _resolve_docs_path(rel: str) -> Path | None:
    target = _resolve_confined(DOCS_ROOT, rel)
    if target is None:
        return None
    if target.is_dir():
        dir_index = (target / "index.html").resolve()
        if dir_index.is_relative_to(DOCS_ROOT) and dir_index.is_file():
            return dir_index
    return target


class QuietUIShowcaseHandler(SimpleHTTPRequestHandler):
    """Serves docs/ as web root for /, /demo/, /docs/, /bench/ with safe REPO_ROOT fallback."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        split = urllib.parse.urlsplit(self.path)
        unquoted_path = urllib.parse.unquote(split.path)
        parts = [p for p in unquoted_path.split("/") if p]
        if any(seg.startswith(".") for seg in parts) or "\\" in unquoted_path or "\x00" in unquoted_path:
            self.send_error(404, "Not Found")
            return None

        if split.path in _TRAILING_SLASH_ROUTES:
            location = f"{split.path}/?{split.query}" if split.query else f"{split.path}/"
            self.send_response(301)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        return super().send_head()

    def translate_path(self, path: str) -> str:
        raw_path = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        if "\\" in raw_path or "\x00" in raw_path:
            return _MISSING_TARGET

        norm = posixpath.normpath(raw_path).lstrip("/")
        if norm in ("", ".", "index.html"):
            target = _resolve_confined(DOCS_ROOT, "index.html")
            return str(target) if target is not None else _MISSING_TARGET

        if norm in ("demo", "docs", "bench") and raw_path.endswith("/"):
            route_index = _resolve_confined(DOCS_ROOT, f"{norm}/index.html")
            if route_index is not None and route_index.is_file():
                return str(route_index)

        docs_target = _resolve_docs_path(norm)
        if docs_target is not None:
            return str(docs_target)

        if norm.startswith("docs/"):
            prefixed_docs = _resolve_docs_path(norm[5:])
            if prefixed_docs is not None:
                return str(prefixed_docs)

        root_target = _resolve_confined(REPO_ROOT, norm)
        if root_target is not None and not root_target.is_relative_to(DOCS_ROOT):
            return str(root_target)

        return _MISSING_TARGET


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Quiet UI 3-route site, Studio Showcase & Evidence Library.")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8788, help="TCP port (default: 8788)")
    args = parser.parse_args()

    with ReusableThreadingHTTPServer((args.host, args.port), QuietUIShowcaseHandler) as httpd:
        host, port = httpd.server_address[:2]
        print(f"[OK] Quiet UI Showcase listening on http://{host}:{port}/ (root: {DOCS_ROOT})", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
