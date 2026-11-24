# SPDX-License-Identifier: Apache-2.0
"""Shared Headless Chrome CDP helpers for Quiet UI visual gates."""

from __future__ import annotations

import functools
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

ALL_WORLDS_VIEWS: list[tuple[str, tuple[str, ...]]] = [
    ("01-clinical-icu-and-trials", ("v01-icu-bedside-terminal", "v02-trial-regulatory-brief", "v03-patient-recovery-companion")),
    ("02-cloud-cyber-and-ai-ops", ("v04-sre-incident-workbench", "v05-zero-trust-ato-spec", "v06-ai-drift-and-lineage-ide", "v19-product-roadmap-and-triage")),
    ("03-industrial-grid-and-manufacturing", ("v07-grid-scada-poi-console", "v08-plant-floor-wall-kiosk", "v09-spc-quality-and-modbus-report")),
    ("04-civic-finance-and-stem-learning", ("v10-civic-capital-budget-deck", "v11-treasury-stress-test-solver", "v12-stem-interactive-lab", "v20-student-capstone-lab-report", "v22-reading-and-mobility-brief")),
    ("05-physical-systems-auto-and-aero", ("v13-propulsion-archival-monograph", "v14-fieldbus-and-scope-debugger", "v15-collimated-flight-hud", "v16-transparent-window-overlay", "v21-field-anomaly-escalation-tsn")),
    ("06-smart-home-and-energy", ("v17-picture-frame-home-kiosk", "v18-home-assistant-companion-console")),
]

ROOT_FONT_SCALE_TARGETS: dict[int, tuple[float, float]] = {
    390: (16.0, 0.25),
    840: (16.0, 0.25),
    1440: (16.0, 0.25),
    1920: (17.2, 0.35),
    3840: (22.0, 0.35),
}


class _SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str, **kwargs: Any) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_http_server(directory: Path) -> tuple[ThreadingHTTPServer, int]:
    """Launch an ephemeral local HTTP server serving `directory`."""
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_SilentHandler, directory=str(directory)))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.08)
    return srv, int(srv.server_address[1])


def create_headless_driver() -> Any:
    """Create a Headless Chrome WebDriver configured for deterministic CDP audits."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    opts = Options()
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin
    for arg in (
        "--headless=new", "--ozone-platform=headless", "--disable-gpu", "--disable-vulkan",
        "--use-gl=angle", "--use-angle=swiftshader-webgl", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1440,900",
    ):
        opts.add_argument(arg)
    driver_bin = os.environ.get("CHROMEDRIVER_BIN")
    return webdriver.Chrome(service=Service(executable_path=driver_bin), options=opts) if driver_bin else webdriver.Chrome(options=opts)


def set_viewport(driver: Any, width: int, height: int, scale: int = 1) -> None:
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": scale, "mobile": width < 600},
    )


def select_view(driver: Any, slug: str) -> None:
    """Switch active Studio view by view_id via QuietStudioPortalV9."""
    driver.switch_to.default_content()
    driver.execute_script(
        """
        const slug = arguments[0], api = window.QuietStudioPortalV9;
        const mEl = document.getElementById('va-v9-manifest');
        if (!api || !mEl) return;
        const man = JSON.parse(mEl.textContent || '{"worlds":[]}');
        let worldId = api.state.world, viewId = api.state.view;
        for (const w of man.worlds || []) {
            for (const v of w.views || []) {
                if (v.view_id === slug || v.view_id.startsWith(slug + '-')) { worldId = w.world_id; viewId = v.view_id; break; }
            }
        }
        api.state.studioView = 'examples'; api.state.world = worldId; api.state.view = viewId; api.state.presetLocked = true;
        api.applyState(false);
        """,
        slug,
    )
    for _ in range(45):
        time.sleep(0.05)
        ok = driver.execute_script(
            """
            const slug = arguments[0], d = document.getElementById('va-stage-portal')?.contentDocument;
            const cur = d?.documentElement?.dataset?.view || '', main = d?.getElementById('va-stage-main');
            if (!(cur === slug || cur.startsWith(slug + '-')) || !(main && main.children.length)) return false;
            return [...d.querySelectorAll('img.v9-opt-photo, img.v17-art-photo.is-active')].every(i => i.complete && i.naturalWidth > 0);
            """,
            slug,
        )
        if ok:
            break
    time.sleep(0.05)
