#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Quiet UI v8.0.1 Static + 17-Gate Headless Selenium CDP Verifier.

Usage:
  python3 -B skills/quiet-ui/scripts/verify_visual_contract.py [showcase_html] [--check-docs] [--live-url URL] [--cdp] [--screenshots-dir DIR]
"""

from __future__ import annotations

import argparse
import functools
import posixpath
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Add scripts directory to path for submodule resolution
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from contract.atlas_and_hud_gates import run_atlas_and_hud_gates
from contract.flagship_craft_gates import run_flagship_craft_gates
from contract.selenium_gates import create_headless_driver, run_selenium_gates_1_to_13
from contract.static_gates import run_static_gates
from contract.studio_and_svg_gates import run_studio_and_svg_gates


class QuietServerHandler(SimpleHTTPRequestHandler):
    """Local handler mapping root showcase, docs assets, and diagrams."""

    def __init__(self, *args, repo_dir: Path | None = None, **kwargs):
        self._repo_root = repo_dir or Path.cwd()
        super().__init__(*args, directory=str(self._repo_root), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def translate_path(self, path: str) -> str:
        norm = posixpath.normpath(urllib.parse.unquote(urllib.parse.urlsplit(path).path)).lstrip("/")
        if norm in ("", ".", "index.html"):
            return str(self._repo_root / "quiet-ui-showcase.html")
        rc = (self._repo_root / norm).resolve()
        if rc.exists() and rc.is_relative_to(self._repo_root):
            return str(rc)
        dc = (self._repo_root / "docs" / norm).resolve()
        if dc.exists() and dc.is_relative_to(self._repo_root / "docs"):
            return str(dc)
        return str(self._repo_root / "__nonexistent_target__")


def run_local_server(repo_root: Path, port: int = 8788) -> tuple[ThreadingHTTPServer, threading.Thread]:
    """Start local threaded HTTP server for live CDP testing."""
    handler = functools.partial(QuietServerHandler, repo_dir=repo_root)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    server.allow_reuse_address = True
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.12)
    return server, thread


def resolve_live_target(repo_root: Path) -> tuple[str, ThreadingHTTPServer | None]:
    """Connect to existing preview server or launch a new local instance."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:8788/", timeout=0.6) as resp:
            if resp.status == 200:
                print("  Reusing active local preview server at http://127.0.0.1:8788/")
                return "http://127.0.0.1:8788/", None
    except Exception:
        pass

    for port in (8788, 8789, 8790, 0):
        try:
            server, _ = run_local_server(repo_root, port=port)
            actual_port = server.server_address[1]
            print(f"  Launched local HTTP server on port {actual_port}")
            return f"http://127.0.0.1:{actual_port}/", server
        except OSError:
            continue
    raise RuntimeError("Failed to bind local preview server to any port")


def find_repo_root(start_dir: Path) -> Path:
    """Traverse up to find repository root containing quiet-ui-showcase.html or .git."""
    curr = start_dir.resolve()
    for _ in range(6):
        if (curr / "quiet-ui-showcase.html").exists() or (curr / ".git").exists():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    return start_dir.resolve()


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quiet UI v8.0.1 Static + 17-Gate Headless Selenium CDP Verifier"
    )
    parser.add_argument(
        "showcase_html_path",
        nargs="?",
        default="quiet-ui-showcase.html",
        help="Path to showcase HTML file (default: quiet-ui-showcase.html)",
    )
    parser.add_argument(
        "--check-docs",
        action="store_true",
        help="Run strict documentation contract & link audits",
    )
    parser.add_argument(
        "--live-url",
        default=None,
        help="Target URL for live headless CDP checks (e.g. http://127.0.0.1:8788/)",
    )
    parser.add_argument(
        "--cdp",
        action="store_true",
        help="Run live Headless Selenium CDP Gates 1-17 (starts local server if --live-url omitted)",
    )
    parser.add_argument(
        "--screenshots-dir",
        default=None,
        help="Directory to save visual audit screenshots",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli_args()
    repo_root = find_repo_root(Path.cwd())
    showcase_path = Path(args.showcase_html_path)
    if not showcase_path.is_absolute():
        showcase_path = (repo_root / showcase_path).resolve()

    print("================================================================================")
    print("  Quiet UI v8.2.0 Visual Contract & 21-Gate Selenium CDP Verifier")
    print("================================================================================")
    print(f"Repo Root:      {repo_root}")
    print(f"Showcase HTML:  {showcase_path}")
    print(f"Check Docs:     {args.check_docs}")
    print(f"Live URL:       {args.live_url}")
    print(f"CDP Live Mode:  {args.cdp or bool(args.live_url)}")
    print("--------------------------------------------------------------------------------")

    all_errors: list[str] = []

    # 1. Run Static Contract Checks
    print("\n[PHASE 1] Executing Static Visual Contract Gates...")
    static_errs = run_static_gates(repo_root, showcase_path, check_docs=args.check_docs)
    all_errors.extend(static_errs)
    if static_errs:
        print(f"  FAILED: {len(static_errs)} static contract violation(s) found.")
    else:
        print("  PASSED: 100% of static contract gates satisfied.")

    # 2. Run Headless Selenium CDP Gates if requested
    run_cdp = args.cdp or bool(args.live_url)
    if run_cdp:
        print("\n[PHASE 2] Executing 21-Gate Headless Selenium CDP Verification...")
        server = None
        target_url = args.live_url
        if not target_url:
            target_url, server = resolve_live_target(repo_root)

        driver = None
        try:
            print("  Launching Chrome (--headless=new)...")
            driver = create_headless_driver()
            print(f"  Running CDP Gates 1-13 against {target_url}...")
            all_errors.extend(run_selenium_gates_1_to_13(driver, target_url, args.screenshots_dir))
            print(f"  Running CDP Gates 14-15 (Atlas & HUD) against {target_url}...")
            all_errors.extend(run_atlas_and_hud_gates(driver, target_url, args.screenshots_dir))
            print(f"  Running CDP Gates 16-17 (Studio Bar & SVG Ceiling) against {target_url}...")
            all_errors.extend(run_studio_and_svg_gates(driver, target_url))
            print(f"  Running CDP Gates 18-21 (Craftsmanship & Substance) against {target_url}...")
            all_errors.extend(run_flagship_craft_gates(driver, target_url, repo_root))
        except Exception as e:
            all_errors.append(f"[SELENIUM_EXECUTION_ERROR] {e}")
        finally:
            if driver:
                driver.quit()
            if server:
                server.shutdown()
                server.server_close()

    # 3. Final Summary & Exit
    print("\n================================================================================")
    print("  VERIFICATION AUDIT RESULTS")
    print("================================================================================")
    if all_errors:
        print(f"[FAIL] Audit failed with {len(all_errors)} issue(s):")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[PASS] 100% of Quiet UI v8.2 Visual Contract & 21 CDP Gates Succeeded!")
        sys.exit(0)


if __name__ == "__main__":
    main()
