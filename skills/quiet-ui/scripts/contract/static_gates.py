# SPDX-License-Identifier: Apache-2.0
"""Static Visual Contract Gates for Quiet UI v8.0."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Sequence

from .constants import (
    CODE_LINE_BUDGET,
    EXCLUDED_LINE_BUDGET_EXACT,
    FORBIDDEN_BRANDS,
    FORBIDDEN_EMOJIS,
    FORBIDDEN_META_STRINGS,
    FORBIDDEN_PII_PATTERNS,
    MAX_LINE_BUDGET,
    REFERENCES_LINE_BUDGET,
    TIER_HTML_LINE_RANGE,
    TOKEN_MIRROR_PATHS,
)

IGNORED_DIRS: set[str] = {".git", ".cache", "node_modules", "__pycache__", ".venv"}
BINARY_EXTS: set[str] = {
    ".jpg", ".jpeg", ".png", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".gif", ".webp", ".so", ".pyc",
}


def _is_excluded_from_budget(rel_path: str) -> bool:
    if rel_path in EXCLUDED_LINE_BUDGET_EXACT:
        return True
    parts = rel_path.split("/")
    return len(parts) >= 3 and parts[0] == "customizations" and parts[-1] == "showcase.html"


def verify_line_counts(repo_root: Path) -> list[str]:
    """Gate: Rebalanced file budgets:
    - src/tiers/*.html: <= 550 lines (target 260-550L)
    - skills/**/references/*.md: <= 450 lines
    - code/css/js/scripts: <= 350 lines
    """
    violations: list[str] = []
    for p in repo_root.rglob("*"):
        if not p.is_file() or any(ig in p.parts for ig in IGNORED_DIRS):
            continue
        if p.suffix.lower() in BINARY_EXTS:
            continue
        rel = p.relative_to(repo_root).as_posix()
        if _is_excluded_from_budget(rel):
            continue
        try:
            line_count = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
            if rel.startswith("src/tiers/") and rel.endswith(".html"):
                max_l = TIER_HTML_LINE_RANGE[1]
                if line_count > max_l:
                    violations.append(
                        f"[LINE_BUDGET] {rel} has {line_count} lines (max {max_l})"
                    )
            elif "references" in p.parts and rel.endswith(".md"):
                if line_count > REFERENCES_LINE_BUDGET:
                    violations.append(
                        f"[LINE_BUDGET] {rel} has {line_count} lines (max {REFERENCES_LINE_BUDGET})"
                    )
            else:
                limit = CODE_LINE_BUDGET
                if line_count > limit:
                    violations.append(
                        f"[LINE_BUDGET] {rel} has {line_count} lines (max {limit})"
                    )
        except Exception as e:
            violations.append(f"[LINE_BUDGET_READ_ERR] Could not read {rel}: {e}")
    return violations


def verify_zero_important(repo_root: Path) -> list[str]:
    """Gate 1 Static: 0 occurrences of !important in CSS and HTML files."""
    errors: list[str] = []
    for ext in ("*.css", "*.html"):
        for p in repo_root.rglob(ext):
            if any(ig in p.parts for ig in IGNORED_DIRS):
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            matches = list(re.finditer(r"!important", text, flags=re.IGNORECASE))
            if matches:
                rel = p.relative_to(repo_root).as_posix()
                errors.append(f"[IMPORTANT_VIOLATION] {rel} has {len(matches)} '!important' instance(s)")
    return errors


def verify_token_mirror_parity(repo_root: Path) -> list[str]:
    """Gate 1 Static: SHA-256 parity across all 5 token files."""
    errors: list[str] = []
    hashes: dict[str, str] = {}
    for rel_path in TOKEN_MIRROR_PATHS:
        full_path = repo_root / rel_path
        if not full_path.exists():
            errors.append(f"[TOKEN_PARITY] Missing token mirror: {rel_path}")
            continue
        h = hashlib.sha256(full_path.read_bytes()).hexdigest()
        hashes[rel_path] = h

    if len(hashes) > 1:
        unique_hashes = set(hashes.values())
        if len(unique_hashes) > 1:
            errors.append(
                f"[TOKEN_PARITY] SHA-256 mismatch across token mirrors: {hashes}"
            )
    return errors


def verify_svg_static_rules(repo_root: Path) -> list[str]:
    """Gate 7 Static: 0 preserveAspectRatio='none', 0 path elements lacking fill=."""
    errors: list[str] = []
    # Check for preserveAspectRatio="none"
    for ext in ("*.html", "*.js"):
        for p in repo_root.rglob(ext):
            if any(ig in p.parts for ig in IGNORED_DIRS):
                continue
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"<svg\b[^>]*preserveAspectRatio\s*=\s*['\"]none['\"]", txt, re.I):
                rel = p.relative_to(repo_root).as_posix()
                errors.append(f"[SVG_ASPECT] {rel} contains preserveAspectRatio='none'")

    # Check for <path lacking fill= across HTML and docs/atlas/*.js
    atlas_js_dir = repo_root / "docs" / "atlas"
    scan_files: list[Path] = [
        p for p in repo_root.rglob("*.html") if not any(ig in p.parts for ig in IGNORED_DIRS)
    ]
    if atlas_js_dir.exists():
        scan_files.extend(atlas_js_dir.glob("*.js"))

    for p in scan_files:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        # Match <path tags without fill= attribute
        for m in re.finditer(r"<path\b(?![^>]*\bfill\s*=)[^>]*>", txt, re.I):
            rel = p.relative_to(repo_root).as_posix()
            errors.append(f"[SVG_PATH_FILL] {rel} has <path> lacking explicit fill: {m.group(0)[:60]}")
            break
    return errors


def verify_tables_static_rules(showcase_path: Path) -> list[str]:
    """Gate 9 Static: .va-table-wrap and .va-figure-scroll have tabindex=0 and role=region."""
    errors: list[str] = []
    if not showcase_path.exists():
        return [f"[TABLE_STATIC] Showcase file not found: {showcase_path}"]
    content = showcase_path.read_text(encoding="utf-8", errors="ignore")
    pattern = r'<([a-zA-Z0-9]+)\b[^>]*class\s*=\s*["\'][^"\']*\b(va-table-wrap|va-figure-scroll)\b[^"\']*["\'][^>]*>'
    for m in re.finditer(pattern, content, flags=re.I):
        tag_str = m.group(0)
        cls_matched = m.group(2)
        has_tabindex = bool(re.search(r'tabindex\s*=\s*["\']0["\']', tag_str))
        has_role = bool(re.search(r'role\s*=\s*["\']region["\']', tag_str))
        if not (has_tabindex and has_role):
            errors.append(
                f"[TABLE_A11Y] .{cls_matched} missing tabindex='0' or role='region': {tag_str[:60]}"
            )
    return errors


def verify_hygiene_static(repo_root: Path, showcase_path: Path) -> list[str]:
    """Gate 12 Static: Zero PII, banned emojis, prompt meta-strings, and clean EXIF."""
    errors: list[str] = []
    if not showcase_path.exists():
        return [f"[HYGIENE] Showcase file not found: {showcase_path}"]
    content = showcase_path.read_text(encoding="utf-8", errors="ignore")

    # Strip script/style tags for visible text analysis
    visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", content, flags=re.S | re.I)

    for pat in FORBIDDEN_PII_PATTERNS:
        m = re.search(pat, content, flags=re.IGNORECASE)
        if m:
            errors.append(f"[PII_LEAK] Forbidden identifier matched: '{m.group(0)}'")

    for emoji in FORBIDDEN_EMOJIS:
        if emoji in content:
            errors.append(f"[BANNED_EMOJI] Found banned emoji '{emoji}'")

    for meta in FORBIDDEN_META_STRINGS:
        if meta in visible:
            errors.append(f"[BANNED_META_STRING] Prompt artifact text found: '{meta}'")

    # Gate 12 EXIF check on docs/assets/as08-14-2383.jpg
    as08_path = repo_root / "docs" / "assets" / "as08-14-2383.jpg"
    if as08_path.exists():
        data = as08_path.read_bytes()
        if b"Exif\x00\x00" in data:
            errors.append(f"[EXIF_VIOLATION] {as08_path.name} contains EXIF metadata tags")
    return errors


def verify_docs_contract(repo_root: Path, skill_dir: Path) -> list[str]:
    """Check docs metadata, token usage, and banned brand terminology."""
    errors: list[str] = []
    tokens_file = repo_root / "tokens" / "quiet-ui-tokens.css"
    if not tokens_file.exists():
        tokens_file = skill_dir / "tokens" / "quiet-ui-tokens.css"
    if not tokens_file.exists():
        return [f"[DOCS_CONTRACT] Tokens file not found near {skill_dir}"]

    defined_tokens = set(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", tokens_file.read_text("utf-8")))
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        md_text = skill_md.read_text("utf-8")
        desc_m = re.search(r"^description:\s*(.+)$", md_text, flags=re.M)
        if not desc_m or len(desc_m.group(1).split()) > 55:
            errors.append("[SKILL_DESC_LEN] SKILL.md YAML description must be <= 55 words.")

    ref_files = sorted((skill_dir / "references").glob("*.md")) if (skill_dir / "references").exists() else []
    if skill_md.exists():
        md_text = skill_md.read_text("utf-8")
        for rf in ref_files:
            if f"references/{rf.name}" not in md_text:
                errors.append(f"[UNLINKED_REF] Reference '{rf.name}' is not linked in SKILL.md.")

    docs_to_check = [p for p in [skill_md, *ref_files, repo_root / "README.md", repo_root / "llms.txt"] if p.exists()]
    for doc in docs_to_check:
        txt = doc.read_text("utf-8", errors="ignore")
        for brand in FORBIDDEN_BRANDS:
            if re.search(rf"\b{re.escape(brand)}\b", txt, flags=re.I):
                errors.append(f"[DOC_BRAND] {doc.name} contains banned brand '{brand}'")
        for block in re.findall(r"(?:```|~~~)(?:css|html)\n(.*?)(?:```|~~~)", txt, flags=re.S | re.I):
            for line in block.splitlines():
                if "/* avoid */" in line:
                    continue
                for var_name in re.findall(r"var\(\s*(--[a-zA-Z0-9_-]+)", line):
                    if var_name not in defined_tokens:
                        errors.append(f"[UNDEFINED_TOKEN] {doc.name} references undefined token '{var_name}'")
    return errors


def verify_no_raw_latex_or_ascii(repo_root: Path) -> list[str]:
    """Forbid raw unrendered LaTeX math, broken HTML entities (&bar;), and +---+ ASCII box art in tier HTML."""
    errors: list[str] = []
    raw_pattern = re.compile(
        r"(\$[^$0-9\n][^$\n]{0,80}\$"
        r"|\\(?:quad|text|frac|sum|int|sigma|lambda|tau|eta|nu|pi|mu|Delta|cdot)\b"
        r"|&bar;"
        r"|\+---{2,}"
        r"|[A-Za-z0-9]_\{[^}]+\}"
        r"|[A-Za-z0-9]\^\{[^}]+\})"
    )
    for html_path in sorted((repo_root / "src" / "tiers").glob("*.html")):
        txt = html_path.read_text("utf-8", errors="ignore")
        hits = raw_pattern.findall(txt)
        if hits:
            sample = ", ".join(repr(h) for h in hits[:4])
            errors.append(
                f"[RAW_LATEX_OR_ASCII] {html_path.name} contains unrendered LaTeX/entity/ASCII box art: {sample}"
            )
    return errors


def run_static_gates(
    repo_root: Path,
    showcase_path: Path,
    check_docs: bool = False,
) -> list[str]:
    """Execute all static contract checks and return combined error list."""
    errors: list[str] = []
    errors.extend(verify_line_counts(repo_root))
    errors.extend(verify_zero_important(repo_root))
    errors.extend(verify_token_mirror_parity(repo_root))
    errors.extend(verify_svg_static_rules(repo_root))
    errors.extend(verify_tables_static_rules(showcase_path))
    errors.extend(verify_hygiene_static(repo_root, showcase_path))
    errors.extend(verify_no_raw_latex_or_ascii(repo_root))

    if check_docs:
        skill_dir = repo_root / "skills" / "quiet-ui"
        errors.extend(verify_docs_contract(repo_root, skill_dir))

    return errors

