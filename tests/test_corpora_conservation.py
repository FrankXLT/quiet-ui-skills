#!/usr/bin/env python3
"""Unit and numerical-conservation test suite for Quiet UI v9.0 5-world corpora."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "quiet-evidence" / "scripts"))

from compile_evidence import compile_spec  # noqa: E402
from verify_corpora import (  # noqa: E402
    _SVG_BLOCK_RE,
    CORPORA_DIR,
    REQUIRED_BUDGETS,
    REQUIRED_LENSES,
    REQUIRED_MEDIUMS,
    REQUIRED_MODALITIES,
    REQUIRED_TEMPOS,
    audit_corpora,
)


class TestCorporaConservation(unittest.TestCase):
    """Validate 5-world coverage, multi-theme compilation, and numerical conservation."""

    def test_all_5_worlds_matrix_and_conservation(self) -> None:
        res = audit_corpora(CORPORA_DIR)
        self.assertTrue(res["ok"], "Corpora audit failed:\n" + "\n".join(res["errors"]))
        s = res["stats"]
        self.assertEqual(s["worlds"], 6)
        self.assertEqual(s["views"], 21)
        self.assertEqual(s["evidence_specs"], 26)
        self.assertEqual(set(s["mediums"]), REQUIRED_MEDIUMS)
        self.assertEqual(set(s["lenses"]), REQUIRED_LENSES)
        self.assertEqual(set(s["tempos"]), REQUIRED_TEMPOS)
        self.assertEqual(set(s["chromatic_budgets"]), REQUIRED_BUDGETS)
        self.assertEqual(set(s["modalities"]), REQUIRED_MODALITIES)

    def test_each_world_compiles_under_all_themes_and_l1_to_l3(self) -> None:
        themes = ("white", "paper", "dark", "dark-paper")
        for corpus_path in sorted(CORPORA_DIR.glob("*/corpus.json")):
            wdir = corpus_path.parent
            ev_root = (wdir / "evidence").resolve()
            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
            seen_refs: set[Path] = set()
            for vw in corpus["views"]:
                med = str((vw.get("mediums") or ["M2"])[0]).lower()
                for ref in vw.get("evidence_refs", []):
                    resolved = (wdir / ref).resolve()
                    self.assertTrue(resolved.is_relative_to(ev_root), f"Path traversal ref: {ref}")
                    if resolved in seen_refs:
                        continue
                    seen_refs.add(resolved)
                    spec = json.loads(resolved.read_text(encoding="utf-8"))
                    for rig in ("L1", "L2", "L3"):
                        for theme in themes:
                            out = compile_spec(spec, rigor=rig, medium=med, theme=theme, include_spec_drawer=False)
                            self.assertGreater(len(out), 80, f"Empty render {wdir.name}/{ref} {rig}/{theme}")
                            self.assertNotIn("!important", out.lower())
                            for svg_txt in _SVG_BLOCK_RE.findall(out):
                                ET.fromstring(svg_txt)

    def test_conservation_gate_rejects_drifted_value_and_path_escape(self) -> None:
        sample_worlds = sorted(CORPORA_DIR.glob("*/corpus.json"))
        self.assertEqual(len(sample_worlds), 6)
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

            bad_res = audit_corpora(tmp_root)
            self.assertFalse(bad_res["ok"])
            joined = "\n".join(bad_res["errors"])
            self.assertIn("missing/mismatched", joined)
            self.assertIn("Invalid/escaping evidence_ref", joined)


if __name__ == "__main__":
    unittest.main()
