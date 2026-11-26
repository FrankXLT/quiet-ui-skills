#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Repository hygiene, line budgets, SHA-256 mirror parity, links, and immutability tests."""

from __future__ import annotations

import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for _sys_p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(_sys_p) not in sys.path:
        sys.path.insert(0, str(_sys_p))

import build_all  # noqa: E402
from build_all import main as build_all_main  # noqa: E402

IGNORED_DIRS = {".git", ".cache", "node_modules", "__pycache__", ".venv", "vendor"}
BINARY_EXTS = {
    ".jpg", ".jpeg", ".png", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".gif", ".webp", ".so", ".pyc",
}
EXCLUDED_LINE_BUDGET = {
    "quiet-ui-showcase.html",
    "docs/index.html",
    "docs/demo/index.html",
    "docs/docs/index.html",
    "docs/bench/evidence-bench.html",
    "docs/assets/quiet-ui-social.svg",
    "customizations/personal-starter/showcase.html",
    "customizations/brand-starter/showcase.html",
    "customizations/project-site-starter/site/index.html",
    "customizations/project-site-starter/site/docs/index.html",
    "customizations/project-site-starter/site/assets/social-preview.svg",
    "skills/quiet-evidence/assets/quiet-evidence-bundle.css",
    "skills/quiet-evidence/assets/quiet-evidence-bundle.js",
}
TOKEN_MIRRORS = (
    "tokens/quiet-ui-tokens.css",
    "skills/quiet-ui/tokens/quiet-ui-tokens.css",
    "customizations/personal-starter/styles/quiet-ui-tokens.css",
    "customizations/brand-starter/styles/quiet-ui-tokens.css",
)
OPTIONAL_TOKEN_MIRRORS = (
    "docs/styles/quiet-ui-tokens.css",
    "customizations/project-site-starter/styles/quiet-ui-tokens.css",
    "customizations/project-site-starter/site/styles/quiet-ui-tokens.css",
)
COMPILED_DOCS_HTML = {
    "docs/docs/index.html",
    "customizations/project-site-starter/site/docs/index.html",
}
STATIC_HYGIENE_HTML = (
    "quiet-ui-showcase.html",
    "docs/index.html",
    "docs/bench/evidence-bench.html",
    "docs/demo/index.html",
    "docs/docs/index.html",
    "customizations/project-site-starter/site/index.html",
    "customizations/project-site-starter/site/docs/index.html",
)
SOCIAL_PNGS = (
    "docs/assets/quiet-ui-social.png",
    "customizations/project-site-starter/site/assets/social-preview.png",
)
LAYERED_TOKEN_CSS = (
    "docs/styles/tokens.layered.css",
    "customizations/project-site-starter/site/styles/tokens.layered.css",
)
LLMS_MIRRORS = ("llms.txt", "docs/llms.txt", "skills/quiet-ui/llms.txt")
FORBIDDEN_EMOJIS = ("✨", "⚡", "☀", "🛡", "●", "&#10024;", "🚀", "💡", "🔥", "⚠️", "❌", "✅")
FORBIDDEN_META_STRINGS = (
    "EXPECTED TICK", "PROPORTIONAL BARS", "QUIET COCKPIT GATE", "FROSTED HUD", "CREASE-AWARE",
)
PILLAR_SKILLS = ("quiet-ui", "quiet-evidence", "quiet-bridge")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_svg_markup(rel: str, txt: str, errs: list[str]) -> None:
    if re.search(r"<svg\b[^>]*preserveAspectRatio\s*=\s*['\"]none['\"]", txt, re.I):
        errs.append(f"{rel}: preserveAspectRatio='none'")
    if re.search(r"<path\b(?![^>]*\bfill\s*=)[^>]*>", txt, re.I):
        errs.append(f"{rel}: <path> missing fill=")


def _has_css_important(rel: str, txt: str, is_html: bool) -> bool:
    if not is_html or rel not in COMPILED_DOCS_HTML:
        return "!important" in txt.lower()
    styles = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", txt, flags=re.S | re.I))
    inline = "\n".join(m[1] for m in re.findall(r"\bstyle\s*=\s*(['\"])(.*?)\1", txt, flags=re.S | re.I))
    return "!important" in f"{styles}\n{inline}".lower()


class TestRepoHygiene(unittest.TestCase):
    """Enforce repo-wide line budgets, zero !important, mirror parity, links, and starter contracts."""

    def test_file_line_budgets(self) -> None:
        self.assertTrue(set(LAYERED_TOKEN_CSS).isdisjoint(EXCLUDED_LINE_BUDGET))
        violations: list[str] = []
        for p in sorted(REPO_ROOT.rglob("*")):
            if not p.is_file() or (set(p.parts) & IGNORED_DIRS) or p.suffix.lower() in BINARY_EXTS:
                continue
            rel = p.relative_to(REPO_ROOT).as_posix()
            if rel in EXCLUDED_LINE_BUDGET or rel.startswith("docs/assets/vendor/"):
                continue
            lines = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
            if rel == "docs/WORKFLOWS.md" and not (250 <= lines <= 450):
                violations.append(f"{rel}: {lines}L outside 250-450L")
            elif rel == "AGENTS.md" and not (115 <= lines <= 155):
                violations.append(f"{rel}: {lines}L outside 115-155L")
            elif p.name == "SKILL.md" and "skills" in p.parts:
                if lines > 140:
                    violations.append(f"{rel}: {lines}L > 140L")
            elif "skills" in p.parts and p.suffix == ".md":
                if not (120 <= lines <= 450):
                    violations.append(f"{rel}: {lines}L outside 120-450L")
            elif lines > 450:
                violations.append(f"{rel}: {lines}L > 450L")
        self.assertEqual(violations, [], "Line budget violations:\n" + "\n".join(violations))

    def test_zero_important_and_static_showcase_hygiene(self) -> None:
        errs: list[str] = []
        svg_checked: set[str] = set()
        css_checked: set[str] = set()
        for ext in ("*.css", "*.html"):
            for p in sorted(REPO_ROOT.rglob(ext)):
                if set(p.parts) & IGNORED_DIRS:
                    continue
                rel = p.relative_to(REPO_ROOT).as_posix()
                if rel.startswith("docs/assets/vendor/"):
                    continue
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if ext == "*.css":
                    css_checked.add(rel)
                if _has_css_important(rel, txt, ext == "*.html"):
                    errs.append(f"{rel}: contains !important")
                if ext == "*.html":
                    _check_svg_markup(rel, txt, errs)
                    svg_checked.add(rel)
        for css_rel in LAYERED_TOKEN_CSS:
            css_p = REPO_ROOT / css_rel
            if not css_p.is_file():
                errs.append(f"{css_rel}: missing layered tokens CSS")
                continue
            css_txt = css_p.read_text(encoding="utf-8", errors="ignore")
            if "@layer tokens" not in css_txt:
                errs.append(f"{css_rel}: missing @layer tokens")
            if css_rel not in css_checked and _has_css_important(css_rel, css_txt, False):
                errs.append(f"{css_rel}: contains !important")
        for svg_rel in ("docs/assets/quiet-ui-social.svg", "customizations/project-site-starter/site/assets/social-preview.svg"):
            svg_p = REPO_ROOT / svg_rel
            if svg_p.is_file():
                _check_svg_markup(svg_rel, svg_p.read_text(encoding="utf-8", errors="ignore"), errs)
                svg_checked.add(svg_rel)
        required_static = {"quiet-ui-showcase.html", "docs/index.html", "docs/bench/evidence-bench.html"}
        for rel in STATIC_HYGIENE_HTML:
            html_p = REPO_ROOT / rel
            if not html_p.is_file():
                if rel in required_static:
                    errs.append(f"{rel}: missing required file")
                continue
            txt = html_p.read_text(encoding="utf-8")
            if rel not in svg_checked:
                _check_svg_markup(rel, txt, errs)
            vis = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", txt, flags=re.S | re.I)
            for em in FORBIDDEN_EMOJIS:
                if em in txt:
                    errs.append(f"{rel}: banned emoji {em!r}")
            for meta in FORBIDDEN_META_STRINGS:
                if meta in vis:
                    errs.append(f"{rel}: leaked prompt meta {meta!r}")
            for cdn in ("cdnjs.cloudflare.com", "font-awesome", "fa-solid"):
                if cdn in txt.lower():
                    errs.append(f"{rel}: third-party CDN ref {cdn!r}")
        for jpg in sorted((REPO_ROOT / "docs" / "assets").glob("*.jpg")):
            if b"Exif\x00\x00" in jpg.read_bytes():
                errs.append(f"docs/assets/{jpg.name}: contains EXIF metadata")
        self.assertEqual(errs, [])

    def test_mirror_parity_and_zero_build_drift(self) -> None:
        tok_paths = list(TOKEN_MIRRORS)
        build_all_tokens = set(getattr(build_all, "TOKEN_MIRRORS", ()))
        for rel in OPTIONAL_TOKEN_MIRRORS:
            p = REPO_ROOT / rel
            if rel in build_all_tokens:
                self.assertTrue(p.is_file(), f"Missing mirrored token file declared in build_all.py: {rel}")
                tok_paths.append(rel)
            elif p.is_file():
                tok_paths.append(rel)
        tok_hashes = {p: _sha256(REPO_ROOT / p) for p in tok_paths}
        self.assertEqual(len(set(tok_hashes.values())), 1, f"Token mismatch: {tok_hashes}")
        llms_hashes = {p: _sha256(REPO_ROOT / p) for p in LLMS_MIRRORS}
        self.assertEqual(len(set(llms_hashes.values())), 1, f"llms.txt mismatch: {llms_hashes}")
        self.assertEqual(build_all_main(["--check"]), 0)

    def test_site_configs_and_social_preview(self) -> None:
        for png_rel in SOCIAL_PNGS:
            png_path = REPO_ROOT / png_rel
            self.assertTrue(png_path.is_file(), f"Missing {png_rel}")
            png_bytes = png_path.read_bytes()
            self.assertLessEqual(len(png_bytes), 250_000, f"{png_rel} exceeds 250_000 bytes ({len(png_bytes)})")
            self.assertGreaterEqual(len(png_bytes), 24, f"{png_rel} truncated (<24 bytes)")
            self.assertEqual(png_bytes[:8], b"\x89PNG\r\n\x1a\n", f"{png_rel} invalid PNG signature")
            self.assertEqual(png_bytes[12:16], b"IHDR", f"{png_rel} missing IHDR chunk")
            width, height = struct.unpack(">II", png_bytes[16:24])
            self.assertEqual((width, height), (1280, 640), f"{png_rel} unexpected dimensions {width}x{height}")

        social_svg = REPO_ROOT / "docs" / "assets" / "quiet-ui-social.svg"
        self.assertTrue(social_svg.is_file(), "Missing docs/assets/quiet-ui-social.svg")
        self.assertIn("WORKBENCH", social_svg.read_text(encoding="utf-8"))

        from src.site_shell import load_site_config

        for cfg_rel in ("src/chrome/quiet-ui-site.json", "customizations/project-site-starter/oaw-site.json"):
            cfg_path = REPO_ROOT / cfg_rel
            self.assertTrue(cfg_path.is_file(), f"Missing site config: {cfg_rel}")
            cfg = load_site_config(cfg_path)
            self.assertIsInstance(cfg, dict, f"{cfg_rel} did not return dict")
            self.assertIn("project", cfg, f"{cfg_rel} missing project section")
            self.assertIn("routes", cfg, f"{cfg_rel} missing routes section")

    def test_markdown_links_schemas_and_css_tokens(self) -> None:
        tok_text = (REPO_ROOT / "tokens" / "quiet-ui-tokens.css").read_text(encoding="utf-8")
        defined_tokens = set(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", tok_text))
        errs: list[str] = []
        md_docs: list[Path] = [
            *sorted(p for p in REPO_ROOT.glob("*.md") if p.is_file()),
            *sorted((REPO_ROOT / "docs").glob("*.md")),
            REPO_ROOT / "customizations" / "README.md",
        ]
        for sk in PILLAR_SKILLS:
            sk_dir = REPO_ROOT / "skills" / sk
            skill_md = sk_dir / "SKILL.md"
            md_txt = skill_md.read_text(encoding="utf-8")
            desc_m = re.search(r"^description:\s*(.+)$", md_txt, flags=re.M)
            if not desc_m or len(desc_m.group(1).split()) > 55:
                errs.append(f"skills/{sk}/SKILL.md description > 55 words")
            md_docs.append(skill_md)
            for sub in sorted(sk_dir.rglob("*.md")):
                if sub == skill_md:
                    continue
                md_docs.append(sub)
                if sub.relative_to(sk_dir).as_posix() not in md_txt:
                    errs.append(f"skills/{sk}/SKILL.md missing link to {sub.relative_to(sk_dir).as_posix()}")

        for doc in md_docs:
            rel = doc.relative_to(REPO_ROOT).as_posix()
            txt = doc.read_text(encoding="utf-8", errors="ignore")
            for em in FORBIDDEN_EMOJIS:
                if em in txt:
                    errs.append(f"{rel}: banned emoji {em!r}")
            for _, link in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", txt):
                if link.startswith(("http://", "https://", "mailto:", "#", "file://")):
                    continue
                clean = link.split("#")[0]
                if clean and not (doc.parent / clean).resolve().exists():
                    errs.append(f"{rel}: broken link '{clean}'")
            if doc.is_relative_to(REPO_ROOT / "skills") or rel in {"docs/WORKFLOWS.md", "README.md"}:
                for block in re.findall(r"```json\s*\n(.*?)\n```", txt, flags=re.S):
                    s = block.strip()
                    if not s or s.startswith(("//", "/*")):
                        continue
                    parsed = json.loads(s)
                    sid = parsed.get("$schema") or parsed.get("schema") if isinstance(parsed, dict) else None
                    if isinstance(sid, str) and not sid.startswith("urn:quiet-ui:schema:v9:"):
                        errs.append(f"{rel}: non-offline schema '{sid}'")
                for code in re.findall(r"(?:```|~~~)(?:css|html)\n(.*?)(?:```|~~~)", txt, flags=re.S | re.I):
                    for line in code.splitlines():
                        if "/* avoid */" in line:
                            continue
                        for vn in re.findall(r"var\(\s*(--[a-zA-Z0-9_-]+)", line):
                            if vn not in defined_tokens:
                                errs.append(f"{rel}: undefined token '{vn}'")
        agents_txt = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for fnd in sorted((REPO_ROOT / "skills" / "quiet-ui" / "foundation").glob("*.md")):
            if fnd.name not in agents_txt:
                errs.append(f"AGENTS.md missing foundation guide reference '{fnd.name}'")
        bench_html = (REPO_ROOT / "docs" / "bench" / "evidence-bench.html").read_text(encoding="utf-8")
        spec_cnt = len(re.findall(r'<article\b[^>]*class="[^"]*\bqe-specimen\b', bench_html))
        if spec_cnt != 53:
            errs.append(f"docs/bench/evidence-bench.html expected 53 specimens, found {spec_cnt}")
        for doc_rel in ("README.md", "AGENTS.md", "llms.txt"):
            if "53" not in (REPO_ROOT / doc_rel).read_text(encoding="utf-8"):
                errs.append(f"{doc_rel}: missing 53 specimen count sync")
        self.assertEqual(errs, [], "Docs contract failures:\n" + "\n".join(errs))

    def test_starter_customizations_and_immutability_gate(self) -> None:
        verifier = REPO_ROOT / "customizations" / "scripts" / "verify_customization.py"
        st = subprocess.check_output(["git", "status", "--porcelain", "-uall"], cwd=REPO_ROOT, text=True)
        protected = (
            "skills/quiet-",
            "customizations/personal-starter/",
            "customizations/brand-starter/",
            "customizations/project-site-starter/",
        )
        dirty_protected = any(any(p in line for p in protected) for line in st.splitlines())
        enforce_immut = (os.environ.get("CI") == "true") or (not dirty_protected)
        for starter in ("customizations/personal-starter", "customizations/brand-starter"):
            cmd = [sys.executable, "-B", str(verifier), starter]
            if enforce_immut:
                cmd.append("--check-immutability")
            res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=tdir, check=True)
            (tdir / "skills" / "quiet-ui").mkdir(parents=True)
            (tdir / "skills" / "quiet-ui" / "SKILL.md").write_text("edited", encoding="utf-8")
            from customizations.scripts.verify_customization import check_immutability
            breaches = check_immutability(tdir)
            self.assertTrue(any("IMMUTABILITY_BREACH" in b for b in breaches))


if __name__ == "__main__":
    unittest.main()
