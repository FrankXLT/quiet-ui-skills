#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Repository hygiene, line budgets, SHA-256 mirror parity, links, and immutability tests."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_all import main as build_all_main  # noqa: E402

IGNORED_DIRS = {".git", ".cache", "node_modules", "__pycache__", ".venv", "vendor"}
BINARY_EXTS = {
    ".jpg", ".jpeg", ".png", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".gif", ".webp", ".so", ".pyc",
}
EXCLUDED_LINE_BUDGET = {
    "quiet-ui-showcase.html",
    "docs/index.html",
    "docs/bench/evidence-bench.html",
    "customizations/personal-starter/showcase.html",
    "customizations/brand-starter/showcase.html",
    "skills/quiet-evidence/assets/quiet-evidence-bundle.css",
    "skills/quiet-evidence/assets/quiet-evidence-bundle.js",
}
TOKEN_MIRRORS = (
    "tokens/quiet-ui-tokens.css",
    "skills/quiet-ui/tokens/quiet-ui-tokens.css",
    "customizations/personal-starter/styles/quiet-ui-tokens.css",
    "customizations/brand-starter/styles/quiet-ui-tokens.css",
)
LLMS_MIRRORS = ("llms.txt", "docs/llms.txt", "skills/quiet-ui/llms.txt")
FORBIDDEN_EMOJIS = ("✨", "⚡", "☀", "🛡", "●", "&#10024;", "🚀", "💡", "🔥", "⚠️", "❌", "✅")
FORBIDDEN_META_STRINGS = (
    "EXPECTED TICK", "PROPORTIONAL BARS", "QUIET COCKPIT GATE", "FROSTED HUD", "CREASE-AWARE",
)
PILLAR_SKILLS = ("quiet-ui", "quiet-evidence", "quiet-bridge")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestRepoHygiene(unittest.TestCase):
    """Enforce repo-wide line budgets, zero !important, mirror parity, links, and starter contracts."""

    def test_file_line_budgets(self) -> None:
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
        for ext in ("*.css", "*.html"):
            for p in sorted(REPO_ROOT.rglob(ext)):
                if set(p.parts) & IGNORED_DIRS:
                    continue
                rel = p.relative_to(REPO_ROOT).as_posix()
                if rel.startswith("docs/assets/vendor/"):
                    continue
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if "!important" in txt.lower():
                    errs.append(f"{rel}: contains !important")
                if ext == "*.html":
                    if re.search(r"<svg\b[^>]*preserveAspectRatio\s*=\s*['\"]none['\"]", txt, re.I):
                        errs.append(f"{rel}: preserveAspectRatio='none'")
                    if re.search(r"<path\b(?![^>]*\bfill\s*=)[^>]*>", txt, re.I):
                        errs.append(f"{rel}: <path> missing fill=")
        for rel in ("quiet-ui-showcase.html", "docs/index.html", "docs/bench/evidence-bench.html"):
            txt = (REPO_ROOT / rel).read_text(encoding="utf-8")
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
        tok_hashes = {p: _sha256(REPO_ROOT / p) for p in TOKEN_MIRRORS}
        self.assertEqual(len(set(tok_hashes.values())), 1, f"Token mismatch: {tok_hashes}")
        llms_hashes = {p: _sha256(REPO_ROOT / p) for p in LLMS_MIRRORS}
        self.assertEqual(len(set(llms_hashes.values())), 1, f"llms.txt mismatch: {llms_hashes}")
        self.assertEqual(build_all_main(["--check"]), 0)

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
        if spec_cnt != 49:
            errs.append(f"docs/bench/evidence-bench.html expected 49 specimens, found {spec_cnt}")
        for doc_rel in ("README.md", "AGENTS.md", "llms.txt"):
            if "49" not in (REPO_ROOT / doc_rel).read_text(encoding="utf-8"):
                errs.append(f"{doc_rel}: missing 49 specimen count sync")
        self.assertEqual(errs, [], "Docs contract failures:\n" + "\n".join(errs))

    def test_starter_customizations_and_immutability_gate(self) -> None:
        verifier = REPO_ROOT / "customizations" / "scripts" / "verify_customization.py"
        st = subprocess.check_output(["git", "status", "--porcelain", "-uall"], cwd=REPO_ROOT, text=True)
        protected = ("skills/quiet-", "customizations/personal-starter/", "customizations/brand-starter/")
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
