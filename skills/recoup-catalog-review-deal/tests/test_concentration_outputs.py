"""Synthetic CLI acceptance for concentration input and artifact preservation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/calculate-concentration.py"


class ConcentrationOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = self.root / "ledger.csv"
        self.ledger.write_text("catalog_asset_id,owner_net_amount,currency,period_start,period_end,row_status\nA,75,USD,2024-01-01,2024-03-31,ready\nB,25,USD,2024-01-01,2024-03-31,ready\n")
        self.assumptions = self.root / "assumptions.yaml"
        self.assumptions.write_text("materiality:\n  concentration_threshold_percent: 60\n")
        self.policy = self.root / "comparison.json"
        self.policy.write_text(json.dumps({"currency": "USD", "period_start": "2024-01-01", "period_end": "2024-03-31", "evidence_refs": ["synthetic:window"]}))
        self.originals = {p: p.read_bytes() for p in (self.ledger, self.assumptions, self.policy)}

    def invoke(self, analysis, findings):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.ledger), "--assumptions", str(self.assumptions), "--comparison-policy", str(self.policy), "--output", str(analysis), "--emit-finding-output", str(findings)], capture_output=True, text=True)

    def test_each_output_rejects_aliases_of_each_input_before_any_write(self):
        for source in self.originals:
            for alias_kind in ("direct", "symlink", "hardlink"):
                for slot in ("analysis", "findings"):
                    with self.subTest(source=source.name, alias=alias_kind, slot=slot):
                        for path, raw in self.originals.items():
                            path.write_bytes(raw)
                        alias = self.root / "alias"
                        if alias.exists() or alias.is_symlink():
                            alias.unlink()
                        if alias_kind == "symlink":
                            alias.symlink_to(source)
                        elif alias_kind == "hardlink":
                            alias.hardlink_to(source)
                        else:
                            alias = source
                        other = self.root / "other-output.json"
                        other.write_text("retained artifact")
                        run = self.invoke(alias, other) if slot == "analysis" else self.invoke(other, alias)
                        self.assertNotEqual(run.returncode, 0)
                        self.assertIn("cannot overwrite", run.stderr)
                        for path, raw in self.originals.items():
                            self.assertEqual(path.read_bytes(), raw)
                        self.assertEqual(other.read_text(), "retained artifact")

    def test_outputs_cannot_alias_each_other(self):
        for alias_kind in ("direct", "symlink", "hardlink"):
            with self.subTest(alias=alias_kind):
                analysis = self.root / "analysis.json"
                analysis.write_text("prior analysis")
                findings = self.root / "findings.json"
                if findings.exists() or findings.is_symlink():
                    findings.unlink()
                if alias_kind == "symlink":
                    findings.symlink_to(analysis)
                elif alias_kind == "hardlink":
                    findings.hardlink_to(analysis)
                else:
                    findings = analysis
                run = self.invoke(analysis, findings)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("distinct", run.stderr)
                self.assertEqual(analysis.read_text(), "prior analysis")
                self.assertEqual(findings.read_text(), "prior analysis")

    def test_distinct_outputs_preserve_inputs_and_separate_results(self):
        analysis, findings = self.root / "analysis.json", self.root / "findings.json"
        run = self.invoke(analysis, findings)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(analysis.read_text())["total"], "100")
        self.assertEqual(len(json.loads(findings.read_text())["findings"]), 1)
        for path, raw in self.originals.items():
            self.assertEqual(path.read_bytes(), raw)
