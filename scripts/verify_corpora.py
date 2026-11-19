#!/usr/bin/env python3
"""Quiet UI v9.0 Phase 3 — 5-World Corpora Matrix, Compiler & Conservation Verifier."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPORA_DIR = REPO_ROOT / "content" / "corpora"
sys.path.insert(0, str(REPO_ROOT / "skills" / "quiet-evidence" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "quiet-ui" / "scripts"))

from compile_evidence import compile_spec, detect_modality  # noqa: E402
from contract.constants import (  # noqa: E402
    CODE_LINE_BUDGET,
    FORBIDDEN_BRANDS,
    FORBIDDEN_EMOJIS,
    FORBIDDEN_PII_PATTERNS,
)

REQUIRED_MEDIUMS = {"M1", "M2", "M3", "M4", "M5", "M6", "M7"}
REQUIRED_LENSES = {
    "Technician / Operator",
    "Discipline Engineer",
    "Project / Systems Engineer",
    "Program Manager",
    "Consumer / Common Reader",
    "Educator / Mentor",
    "Student / Learner",
}
REQUIRED_TEMPOS = {"T1", "T2", "T3"}
REQUIRED_BUDGETS = {"Quiet Cockpit", "Decision Contrast", "Pedagogical Flow", "Archival Proof"}
REQUIRED_MODALITIES = {"scalar", "table", "bitfield", "plot", "waveform", "schematic"}

_UPPERCASE_SI_RE = re.compile(
    r"(?:/\s*(?:PS|DBM|KHZ|GHZ|MRAD|MMHG|CMH2O|BPM)\b|<th[^>]*>[^<]*\b(?:T_SKEW|P_RX|F_S)\s*/\s*(?:PS|DBM|HZ|KHZ)\b)"
)
_NUM_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.])[-+\u2212]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?(?![A-Za-z0-9_])"
)
_SVG_BLOCK_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.DOTALL)


def _rel_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _parse_num(tok: str) -> float | None:
    try:
        val = float(tok.replace(",", "").replace("\u2212", "-"))
        return val if math.isfinite(val) else None
    except ValueError:
        return None


def _num_tol(target: float) -> float:
    return abs(target) * 1e-6 if target != 0.0 else 1e-12


def _collect_json_values(node: Any, out_nums: list[float], out_strs: list[str]) -> None:
    if isinstance(node, bool) or node is None:
        return
    if isinstance(node, (int, float)):
        val = float(node)
        if math.isfinite(val):
            out_nums.append(val)
            out_strs.append(str(node))
    elif isinstance(node, str):
        out_strs.append(node)
        out_nums.extend(v for tok in _NUM_TOKEN_RE.findall(node) if (v := _parse_num(tok)) is not None)
    elif isinstance(node, list):
        for item in node:
            _collect_json_values(item, out_nums, out_strs)
    elif isinstance(node, dict):
        for val in node.values():
            _collect_json_values(val, out_nums, out_strs)


def _value_matches_collection(expected: Any, nums: list[float], strs: list[str]) -> bool:
    if expected is None or isinstance(expected, bool):
        return False
    if isinstance(expected, (int, float)):
        t = float(expected)
        return math.isfinite(t) and any(abs(n - t) <= _num_tol(t) for n in nums)
    exp = str(expected).strip()
    if not exp:
        return False
    pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(exp)}(?![A-Za-z0-9_])", re.IGNORECASE)
    return any(pat.search(s) for s in strs)


def _value_on_line(mid: str, expected: Any, text: str) -> bool:
    """Require canonical metric_id and conserved value to co-occur on the same line."""
    if expected is None or isinstance(expected, bool) or not (exp := str(expected).strip()):
        return False
    id_pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(mid)}(?![A-Za-z0-9_])")
    str_pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(exp)}(?![A-Za-z0-9_])", re.IGNORECASE)
    for line in text.splitlines():
        if not id_pat.search(line):
            continue
        if isinstance(expected, (int, float)):
            t = float(expected)
            if math.isfinite(t) and any((v := _parse_num(tok)) is not None and abs(v - t) <= _num_tol(t) for tok in _NUM_TOKEN_RE.findall(line)):
                return True
        elif str_pat.search(line):
            return True
    return False


def _normalize_bindings(bindings: Any, wrel: str, errors: list[str]) -> list[tuple[str, list[str]]]:
    if isinstance(bindings, list):
        out: list[tuple[str, list[str]]] = []
        for idx, b in enumerate(bindings):
            raw_f = b.get("evidence_file") or b.get("file") if isinstance(b, dict) else None
            mids = b.get("metric_ids") if isinstance(b, dict) else None
            if not isinstance(raw_f, str) or not raw_f.strip() or not isinstance(mids, list) or not mids:
                errors.append(f"[{wrel}] evidence_bindings[{idx}] requires evidence_file and non-empty metric_ids")
            else:
                out.append((raw_f.strip(), [str(m) for m in mids if isinstance(m, str) and m.strip()]))
        return out
    if isinstance(bindings, dict):
        pairs: list[tuple[str, list[str]]] = []
        for k, v in bindings.items():
            if isinstance(v, list):
                mids = [str(m) for m in v if isinstance(m, str) and m.strip()]
                if not mids:
                    errors.append(f"[{wrel}] evidence_bindings['{k}'] has empty metric list")
                pairs.append((str(k), mids))
            elif isinstance(v, dict):
                raw_f = v.get("evidence_file") or v.get("file")
                if not isinstance(raw_f, str) or not raw_f.strip():
                    errors.append(f"[{wrel}] evidence_bindings['{k}'] missing evidence_file/file")
                else:
                    pairs.append((raw_f.strip(), [str(k)]))
            else:
                errors.append(f"[{wrel}] evidence_bindings['{k}'] must be a list or object")
        return pairs
    errors.append(f"[{wrel}/corpus.json] evidence_bindings must be a list or object")
    return []


def _check_file_hygiene(path: Path, rel: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if len(text.splitlines()) > CODE_LINE_BUDGET:
        errors.append(f"[{rel}] Exceeds {CODE_LINE_BUDGET}L budget ({len(text.splitlines())} lines)")
    if "!important" in text.lower():
        errors.append(f"[{rel}] Contains forbidden '!important' declaration")
    for pat in FORBIDDEN_PII_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            errors.append(f"[{rel}] Matches forbidden PII pattern: {pat}")
    for emoji in FORBIDDEN_EMOJIS:
        if emoji in text:
            errors.append(f"[{rel}] Contains forbidden emoji: {emoji}")
    for brand in FORBIDDEN_BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", text, re.IGNORECASE):
            errors.append(f"[{rel}] Mentions forbidden brand '{brand}'")


def _compile_and_check_evidence(
    ev_path: Path, corpora_dir: Path, rigor_set: set[str], errors: list[str]
) -> tuple[dict[str, Any], str]:
    rel = _rel_path(ev_path, corpora_dir)
    try:
        spec = json.loads(ev_path.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise TypeError("evidence spec root must be a JSON object")
        modality = detect_modality(spec)
    except (OSError, json.JSONDecodeError, ValueError, TypeError, AttributeError) as exc:
        errors.append(f"[{rel}] Failed to load evidence spec: {exc}")
        return {}, ""
    for rig in (sorted(rigor_set) if rigor_set else [str(spec.get("metadata", {}).get("rigor_level", "L3")).upper()]):
        try:
            html_out = compile_spec(spec, rigor=rig, medium="m2", theme="white", include_spec_drawer=False)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"[{rel}] Compile failed ({rig}): {exc}")
            continue
        if not html_out or len(html_out) < 80:
            errors.append(f"[{rel}] Empty HTML returned for rigor={rig}")
            continue
        if "!important" in html_out.lower():
            errors.append(f"[{rel}] Compiled output contains '!important' ({rig})")
        if si_hit := _UPPERCASE_SI_RE.search(html_out):
            errors.append(f"[{rel}] Uppercase SI unit corruption ({rig}): {si_hit.group(0)}")
        open_svgs, svg_blocks = len(re.findall(r"<svg\b", html_out)), _SVG_BLOCK_RE.findall(html_out)
        if open_svgs != len(svg_blocks):
            errors.append(f"[{rel}] Unbalanced <svg> tags ({open_svgs} open vs {len(svg_blocks)} closed)")
        for idx, svg_txt in enumerate(svg_blocks):
            try:
                ET.fromstring(svg_txt)
            except ET.ParseError as exc:
                errors.append(f"[{rel}] Invalid SVG XML at block #{idx} ({rig}): {exc}")
    return spec, modality


def audit_corpora(corpora_dir: Path = CORPORA_DIR) -> dict[str, Any]:
    """Audit all worlds in content/corpora for coverage, compilation, and numerical conservation."""
    errors: list[str] = []
    if not corpora_dir.is_dir():
        return {"ok": False, "errors": [f"Missing corpora directory: {corpora_dir}"], "stats": {}}
    world_dirs = sorted(d for d in corpora_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
    if len(world_dirs) < 6:
        errors.append(f"Expected >= 6 worlds under {corpora_dir}, found {len(world_dirs)}")

    cov = {"mediums": set(), "lenses": set(), "tempos": set(), "budgets": set(), "modalities": set()}
    total_views = total_evidence = conserved_checks = 0

    for wdir in world_dirs:
        wrel = _rel_path(wdir, corpora_dir)
        attr_p, corp_p, blue_p, ev_dir = wdir / "SOURCE_ATTRIBUTION.md", wdir / "corpus.json", wdir / "distillation_blueprint.md", wdir / "evidence"
        for req_p in (attr_p, corp_p, blue_p):
            if not req_p.is_file():
                errors.append(f"[{wrel}] Missing required file {req_p.name}")
        if not ev_dir.is_dir():
            errors.append(f"[{wrel}] Missing evidence/ directory")
            continue
        ev_files = sorted(ev_dir.glob("*.json"))
        for fpath in sorted([attr_p, corp_p, blue_p, *ev_files]):
            if fpath.is_file():
                _check_file_hygiene(fpath, _rel_path(fpath, corpora_dir), errors)
        if not (3 <= len(ev_files) <= 4):
            errors.append(f"[{wrel}] Expected 3-4 evidence/*.json specs, found {len(ev_files)}")
        total_evidence += len(ev_files)
        if not (corp_p.is_file() and blue_p.is_file()):
            continue
        try:
            corpus = json.loads(corp_p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[{wrel}/corpus.json] Invalid JSON: {exc}")
            continue
        if not isinstance(corpus, dict) or corpus.get("$schema") != "urn:quiet-ui:schema:v9:corpus":
            errors.append(f"[{wrel}/corpus.json] Invalid $schema")
            continue

        blueprint_txt = blue_p.read_text(encoding="utf-8")
        views = corpus.get("views")
        if not isinstance(views, list) or not views:
            errors.append(f"[{wrel}/corpus.json] Missing or empty views list")
            continue

        total_views += len(views)
        ev_root, ev_rigors, referenced_ev = ev_dir.resolve(), {}, set()
        for vw in views:
            if not isinstance(vw, dict):
                errors.append(f"[{wrel}] View entry must be an object"); continue
            vid = str(vw.get("view_id") or vw.get("id") or "").strip()
            if not vid or not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(vid)}(?![A-Za-z0-9_-])", blueprint_txt):
                errors.append(f"[{wrel}] View '{vid}' missing from distillation_blueprint.md")
            for k in ("mediums", "lenses", "tempos"):
                vals = vw.get(k)
                if not isinstance(vals, list) or not all(isinstance(x, str) for x in vals):
                    errors.append(f"[{wrel}] View '{vid}' field '{k}' must be a list of strings")
                else:
                    cov[k].update(vals)
            bud = vw.get("chromatic_budget")
            cov["budgets"].add(bud) if isinstance(bud, str) and bud.strip() else errors.append(f"[{wrel}] View '{vid}' missing chromatic_budget")
            rig = str(vw.get("rigor_level") or "L3").upper()
            refs = vw.get("evidence_refs")
            if refs is not None and not isinstance(refs, list):
                errors.append(f"[{wrel}] View '{vid}' field 'evidence_refs' must be a list")
                continue
            for eref in (refs or []):
                resolved = (wdir / str(eref)).resolve() if isinstance(eref, str) else Path("")
                if not isinstance(eref, str) or not resolved.is_relative_to(ev_root) or not resolved.is_file():
                    errors.append(f"[{wrel}] Invalid/escaping evidence_ref '{eref}' in view '{vid}'")
                else:
                    norm = f"evidence/{resolved.name}"
                    ev_rigors.setdefault(norm, set()).add(rig)
                    referenced_ev.add(norm)

        parsed_evidence: dict[str, tuple[list[float], list[str]]] = {}
        for evp in ev_files:
            rel_ref = f"evidence/{evp.name}"
            if rel_ref not in referenced_ev:
                errors.append(f"[{wrel}] Unreferenced evidence spec '{rel_ref}'")
            spec, mod = _compile_and_check_evidence(evp, corpora_dir, ev_rigors.get(rel_ref, set()), errors)
            if mod:
                cov["modalities"].add(mod)
            nums, strs = [], []
            _collect_json_values(spec, nums, strs)
            parsed_evidence[rel_ref] = (nums, strs)

        metrics = corpus.get("canonical_metrics")
        if not isinstance(metrics, dict) or not metrics:
            errors.append(f"[{wrel}/corpus.json] canonical_metrics must be a non-empty object"); continue
        for mid, mobj in metrics.items():
            mval = mobj.get("value") if isinstance(mobj, dict) else mobj
            conserved_checks += 1 if _value_on_line(mid, mval, blueprint_txt) else (errors.append(f"[{wrel}] Metric '{mid}' with value {mval!r} missing/mismatched in distillation_blueprint.md") or 0)

        bound_files, bound_metrics = set(), set()
        for eref, mids in _normalize_bindings(corpus.get("evidence_bindings"), wrel, errors):
            norm_res = (wdir / eref).resolve()
            norm_ref = f"evidence/{norm_res.name}" if norm_res.is_relative_to(ev_root) else eref
            if norm_ref not in parsed_evidence:
                errors.append(f"[{wrel}] evidence_binding references unknown/escaping file '{eref}'"); continue
            bound_files.add(norm_ref)
            nums, strs = parsed_evidence[norm_ref]
            for mid in mids:
                bound_metrics.add(mid)
                if mid not in metrics:
                    errors.append(f"[{wrel}] evidence_binding '{eref}' references unknown metric '{mid}'")
                else:
                    val = metrics[mid].get("value") if isinstance(metrics[mid], dict) else metrics[mid]
                    conserved_checks += 1 if _value_matches_collection(val, nums, strs) else (errors.append(f"[{wrel}] Conservation violation: metric '{mid}' value {val!r} missing from {norm_ref}") or 0)
        errors.extend(f"[{wrel}] Evidence spec '{ub}' lacks any entry in evidence_bindings" for ub in sorted(set(parsed_evidence) - bound_files))
        errors.extend(f"[{wrel}] Canonical metric '{um}' lacks any entry in evidence_bindings" for um in sorted(set(metrics) - bound_metrics))

    if total_views != 18:
        errors.append(f"Expected 18 total views across 6 worlds, found {total_views}")
    for key, req in (("mediums", REQUIRED_MEDIUMS), ("lenses", REQUIRED_LENSES), ("tempos", REQUIRED_TEMPOS), ("budgets", REQUIRED_BUDGETS), ("modalities", REQUIRED_MODALITIES)):
        if (miss := sorted(req - cov[key])) or (extra := sorted(cov[key] - req)):
            errors.append(f"Matrix coverage mismatch for {key}: missing={miss}, unexpected={extra}")

    return {"ok": not errors, "errors": errors, "stats": {"worlds": len(world_dirs), "views": total_views, "evidence_specs": total_evidence, "conserved_checks": conserved_checks, "mediums": sorted(cov["mediums"]), "lenses": sorted(cov["lenses"]), "tempos": sorted(cov["tempos"]), "chromatic_budgets": sorted(cov["budgets"]), "modalities": sorted(cov["modalities"])}}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Quiet UI v9.0 5-World Corpora & Conservation.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON summary.")
    args = parser.parse_args(argv)
    res = audit_corpora()
    if args.json:
        print(json.dumps(res, indent=2))
    elif res["ok"]:
        s = res["stats"]
        print(f"[PASS] Corpora Verified: {s['worlds']} worlds, {s['views']} views, {s['evidence_specs']} evidence specs, {s['conserved_checks']} conservation checks | 7/7 Mediums, 7/7 Lenses, 3/3 Tempos, 4/4 Budgets, 6/6 Modalities.")
    else:
        for err in res["errors"]:
            print(f"[FAIL] {err}")
        print(f"[ERROR] {len(res['errors'])} corpora violation(s) detected.")
    return 0 if res["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
