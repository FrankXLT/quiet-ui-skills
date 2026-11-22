#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Headless Chrome CDP visual contract suite (requires selenium + Chrome unless QUIET_SKIP_CDP=1)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from cdp_gates import REPO_ROOT, create_headless_driver, start_http_server  # noqa: E402
from cdp_gates.bench_and_echarts import run_bench_and_docs_gates
from cdp_gates.optics_and_smart_home import run_optics_and_smart_home_gates
from cdp_gates.studio_and_viewports import run_studio_and_viewport_gates


def _can_launch_cdp() -> tuple[bool, str]:
    if os.environ.get("QUIET_SKIP_CDP") == "1":
        return False, "QUIET_SKIP_CDP=1"
    try:
        drv = create_headless_driver()
        drv.quit()
        return True, ""
    except Exception as exc:
        return False, str(exc)


class TestCDPVisuals(unittest.TestCase):
    """Run all 21 Studio CDP gates, 42 Component Library specimens, /docs root test, and portable auditor CDP."""

    def test_full_cdp_visual_contract(self) -> None:
        require_cdp = os.environ.get("QUIET_REQUIRE_CDP") == "1"
        ok, reason = _can_launch_cdp()
        if not ok:
            if require_cdp:
                self.fail(f"QUIET_REQUIRE_CDP=1 set but Headless Chrome/Selenium unavailable: {reason}")
            self.skipTest(f"CDP visual suite skipped ({reason})")

        srv, port = start_http_server(REPO_ROOT)
        root_url = f"http://127.0.0.1:{port}"
        base_url = f"{root_url}/quiet-ui-showcase.html"
        driver = create_headless_driver()
        errs: list[str] = []
        try:
            errs.extend(run_studio_and_viewport_gates(driver, base_url, root_url))
            errs.extend(run_optics_and_smart_home_gates(driver, base_url))
            errs.extend(run_bench_and_docs_gates(driver, base_url, root_url))
        finally:
            driver.quit()
            srv.shutdown()
            srv.server_close()

        self.assertEqual(errs, [], "CDP visual gate failures:\n" + "\n".join(errs))


if __name__ == "__main__":
    unittest.main()
