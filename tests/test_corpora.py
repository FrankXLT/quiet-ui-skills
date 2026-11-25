#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unified corpora coverage, SVG compilation, and numerical-conservation test suite."""

from __future__ import annotations

import copy
import json
import math
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPORA_DIR = REPO_ROOT / "content" / "corpora"
if str(REPO_ROOT / "skills" / "quiet-evidence" / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "skills" / "quiet-evidence" / "scripts"))

from compile_evidence import compile_spec, detect_modality  # noqa: E402

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
FORBIDDEN_EMOJIS = ("✨", "⚡", "☀", "🛡", "●", "&#10024;", "🚀", "💡", "🔥", "⚠️", "❌", "✅")

_UPPERCASE_SI_RE = re.compile(
    r"(?:/\s*(?:PS|DBM|KHZ|GHZ|MRAD|MMHG|CMH2O|BPM)\b|<th[^>]*>[^<]*\b(?:T_SKEW|P_RX|F_S)\s*/\s*(?:PS|DBM|HZ|KHZ)\b)"
)
_NUM_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.])[-+\u2212]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?(?![A-Za-z0-9_])"
)
_SVG_BLOCK_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.DOTALL)


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
                errors.append(f"[{wrel}] evidence_bindings[{idx}] invalid")
            else:
                out.append((raw_f.strip(), [str(m) for m in mids if isinstance(m, str) and m.strip()]))
        return out
    if isinstance(bindings, dict):
        pairs: list[tuple[str, list[str]]] = []
        for k, v in bindings.items():
            if isinstance(v, list):
                pairs.append((str(k), [str(m) for m in v if isinstance(m, str) and m.strip()]))
            elif isinstance(v, dict) and isinstance(v.get("evidence_file") or v.get("file"), str):
                pairs.append((str(v.get("evidence_file") or v.get("file")).strip(), [str(k)]))
            else:
                errors.append(f"[{wrel}] evidence_bindings['{k}'] invalid")
        return pairs
    errors.append(f"[{wrel}/corpus.json] evidence_bindings must be a list or object")
    return []


def audit_corpora(corpora_dir: Path = CORPORA_DIR) -> dict[str, Any]:
    """Audit all domains in content/corpora for coverage, compilation, and numerical conservation."""
    errors: list[str] = []
    world_dirs = sorted(d for d in corpora_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
    if len(world_dirs) != 6:
        errors.append(f"Expected 6 worlds under {corpora_dir}, found {len(world_dirs)}")

    cov = {"mediums": set(), "lenses": set(), "tempos": set(), "budgets": set(), "modalities": set()}
    total_views = total_evidence = conserved_checks = 0

    for wdir in world_dirs:
        wrel = wdir.name
        attr_p, corp_p, blue_p, ev_dir = wdir / "SOURCE_ATTRIBUTION.md", wdir / "corpus.json", wdir / "distillation_blueprint.md", wdir / "evidence"
        for req_p in (attr_p, corp_p, blue_p):
            if not req_p.is_file():
                errors.append(f"[{wrel}] Missing {req_p.name}")
        if not ev_dir.is_dir():
            errors.append(f"[{wrel}] Missing evidence/")
            continue
        ev_files = sorted(ev_dir.glob("*.json"))
        for fpath in sorted([attr_p, corp_p, blue_p, *ev_files]):
            if fpath.is_file():
                txt = fpath.read_text(encoding="utf-8")
                if len(txt.splitlines()) > 450:
                    errors.append(f"[{wrel}/{fpath.name}] Exceeds 450L")
                if "!important" in txt.lower() or any(e in txt for e in FORBIDDEN_EMOJIS):
                    errors.append(f"[{wrel}/{fpath.name}] Forbidden !important or emoji")
        total_evidence += len(ev_files)
        corpus = json.loads(corp_p.read_text(encoding="utf-8"))
        if corpus.get("$schema") != "urn:quiet-ui:schema:v9:corpus":
            errors.append(f"[{wrel}/corpus.json] Invalid $schema")
            continue
        blueprint_txt = blue_p.read_text(encoding="utf-8")
        views = corpus.get("views") or []
        total_views += len(views)
        ev_root, ev_rigors, referenced_ev = ev_dir.resolve(), {}, set()

        for vw in views:
            vid = str(vw.get("view_id") or vw.get("id") or "").strip()
            if not vid or not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(vid)}(?![A-Za-z0-9_-])", blueprint_txt):
                errors.append(f"[{wrel}] View '{vid}' missing from distillation_blueprint.md")
            for k in ("mediums", "lenses", "tempos"):
                cov[k].update(vw.get(k) or [])
            cov["budgets"].add(vw.get("chromatic_budget", ""))
            rig = str(vw.get("rigor_level") or "L3").upper()
            for eref in vw.get("evidence_refs") or []:
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
            spec = json.loads(evp.read_text(encoding="utf-8"))
            mod = detect_modality(spec)
            cov["modalities"].add(mod)
            for rig in sorted(ev_rigors.get(rel_ref, {str(spec.get("metadata", {}).get("rigor_level", "L3")).upper()})):
                out = compile_spec(spec, rigor=rig, medium="m2", theme="white", include_spec_drawer=False)
                if len(out) < 80 or "!important" in out.lower() or _UPPERCASE_SI_RE.search(out):
                    errors.append(f"[{wrel}/{rel_ref}] Invalid compile output ({rig})")
                for svg_txt in _SVG_BLOCK_RE.findall(out):
                    ET.fromstring(svg_txt)
            nums, strs = [], []
            _collect_json_values(spec, nums, strs)
            parsed_evidence[rel_ref] = (nums, strs)

        metrics = corpus.get("canonical_metrics") or {}
        for mid, mobj in metrics.items():
            mval = mobj.get("value") if isinstance(mobj, dict) else mobj
            if _value_on_line(mid, mval, blueprint_txt):
                conserved_checks += 1
            else:
                errors.append(f"[{wrel}] Metric '{mid}' value {mval!r} missing/mismatched in distillation_blueprint.md")

        bound_files, bound_metrics = set(), set()
        for eref, mids in _normalize_bindings(corpus.get("evidence_bindings"), wrel, errors):
            norm_res = (wdir / eref).resolve()
            norm_ref = f"evidence/{norm_res.name}" if norm_res.is_relative_to(ev_root) else eref
            if norm_ref not in parsed_evidence:
                errors.append(f"[{wrel}] evidence_binding unknown '{eref}'")
                continue
            bound_files.add(norm_ref)
            nums, strs = parsed_evidence[norm_ref]
            for mid in mids:
                bound_metrics.add(mid)
                val = metrics[mid].get("value") if isinstance(metrics[mid], dict) else metrics[mid]
                if _value_matches_collection(val, nums, strs):
                    conserved_checks += 1
                else:
                    errors.append(f"[{wrel}] Metric '{mid}' missing from {norm_ref}")
        errors.extend(f"[{wrel}] Unbound evidence '{u}'" for u in sorted(set(parsed_evidence) - bound_files))
        errors.extend(f"[{wrel}] Unbound metric '{u}'" for u in sorted(set(metrics) - bound_metrics))

    if total_views != 26:
        errors.append(f"Expected 26 views across 6 worlds, found {total_views}")
    for key, req in (("mediums", REQUIRED_MEDIUMS), ("lenses", REQUIRED_LENSES), ("tempos", REQUIRED_TEMPOS), ("budgets", REQUIRED_BUDGETS), ("modalities", REQUIRED_MODALITIES)):
        if cov[key] != req:
            errors.append(f"Matrix mismatch for {key}: {sorted(cov[key])}")

    return {"ok": not errors, "errors": errors, "stats": {"worlds": len(world_dirs), "views": total_views, "evidence_specs": total_evidence, "conserved_checks": conserved_checks}}


class TestCorporaConservation(unittest.TestCase):
    """Validate 6-domain coverage, multi-theme compilation, and 261 conservation checks."""

    def test_all_6_worlds_matrix_and_conservation_checks(self) -> None:
        res = audit_corpora(CORPORA_DIR)
        self.assertTrue(res["ok"], "Corpora audit failed:\n" + "\n".join(res["errors"]))
        self.assertEqual(res["stats"], {"worlds": 6, "views": 26, "evidence_specs": 36, "conserved_checks": 261})

    def test_each_world_compiles_under_all_themes_and_l1_to_l3(self) -> None:
        for corpus_path in sorted(CORPORA_DIR.glob("*/corpus.json")):
            wdir = corpus_path.parent
            ev_root = (wdir / "evidence").resolve()
            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
            seen_refs: set[Path] = set()
            for vw in corpus["views"]:
                med = str((vw.get("mediums") or ["M2"])[0]).lower()
                for ref in vw.get("evidence_refs", []):
                    resolved = (wdir / ref).resolve()
                    self.assertTrue(resolved.is_relative_to(ev_root))
                    if resolved in seen_refs:
                        continue
                    seen_refs.add(resolved)
                    spec = json.loads(resolved.read_text(encoding="utf-8"))
                    for rig in ("L1", "L2", "L3"):
                        for theme in ("white", "paper", "dark", "dark-paper"):
                            out = compile_spec(spec, rigor=rig, medium=med, theme=theme, include_spec_drawer=False)
                            self.assertGreater(len(out), 80)
                            self.assertNotIn("!important", out.lower())
                            for svg_txt in _SVG_BLOCK_RE.findall(out):
                                ET.fromstring(svg_txt)

    def test_conservation_gate_rejects_drifted_value_and_path_escape(self) -> None:
        sample_worlds = sorted(CORPORA_DIR.glob("*/corpus.json"))
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            for idx, src_corp in enumerate(sample_worlds):
                src_w = src_corp.parent
                dst_w = tmp_root / src_w.name
                (dst_w / "evidence").mkdir(parents=True)
                for fn in ("SOURCE_ATTRIBUTION.md", "distillation_blueprint.md"):
                    (dst_w / fn).write_text((src_w / fn).read_text(encoding="utf-8"), encoding="utf-8")
                for evp in (src_w / "evidence").glob("*.json"):
                    (dst_w / "evidence" / evp.name).write_text(evp.read_text(encoding="utf-8"), encoding="utf-8")
                corp_data = copy.deepcopy(json.loads(src_corp.read_text(encoding="utf-8")))
                if idx == 0:
                    first_key = next(iter(corp_data["canonical_metrics"]))
                    if isinstance(corp_data["canonical_metrics"][first_key], dict):
                        corp_data["canonical_metrics"][first_key]["value"] = 999991.23
                    else:
                        corp_data["canonical_metrics"][first_key] = 999991.23
                    corp_data["views"][0]["evidence_refs"].append("../../README.md")
                (dst_w / "corpus.json").write_text(json.dumps(corp_data, indent=2), encoding="utf-8")
            bad = audit_corpora(tmp_root)
            self.assertFalse(bad["ok"])
            joined = "\n".join(bad["errors"])
            self.assertIn("missing/mismatched", joined)
            self.assertIn("Invalid/escaping evidence_ref", joined)


if __name__ == "__main__":
    unittest.main()
