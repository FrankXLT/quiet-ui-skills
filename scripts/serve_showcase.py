#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Threaded local HTTP preview server for the Quiet UI Skills v7.1 Showcase & Diagram Atlas."""

from __future__ import annotations

import argparse
import posixpath
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = (REPO_ROOT / "docs").resolve()


class QuietUIShowcaseHandler(SimpleHTTPRequestHandler):
    """Serves root showcase at '/', resolves docs/ assets, and blocks hidden dotfiles."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        raw_path = urllib.parse.urlsplit(self.path).path
        parts = [p for p in urllib.parse.unquote(raw_path).split("/") if p]
        if any(seg.startswith(".") for seg in parts):
            self.send_error(404, "Not Found")
            return None
        return super().send_head()

    def translate_path(self, path: str) -> str:
        raw_path = urllib.parse.urlsplit(path).path
        norm = posixpath.normpath(urllib.parse.unquote(raw_path)).lstrip("/")
        if norm in ("", ".", "index.html"):
            return str(REPO_ROOT / "quiet-ui-showcase.html")

        root_candidate = (REPO_ROOT / norm).resolve()
        if root_candidate.is_relative_to(REPO_ROOT) and root_candidate.exists():
            return str(root_candidate)

        docs_candidate = (DOCS_ROOT / norm).resolve()
        if docs_candidate.is_relative_to(DOCS_ROOT) and docs_candidate.exists():
            return str(docs_candidate)

        return str(REPO_ROOT / "__nonexistent_quiet_ui_target__")


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Quiet UI Showcase & 45-Type Diagram Atlas.")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8788, help="TCP port (default: 8788)")
    args = parser.parse_args()

    with ReusableThreadingHTTPServer((args.host, args.port), QuietUIShowcaseHandler) as httpd:
        print(f"[OK] Quiet UI Showcase v7.1 listening on http://{args.host}:{args.port}/", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
