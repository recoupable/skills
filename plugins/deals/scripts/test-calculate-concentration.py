#!/usr/bin/env python3
"""Tests for calculate-concentration.py threshold logic."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "calculate-concentration.py"


HEADER = (
    "ledger_line_id,catalog_asset_id,source_file,provider,period_start,period_end,"
    "rights_type,income_type,gross_amount,owner_net_amount,currency\n"
)


def write_ledger(path: Path, asset_amounts: list[tuple[str, float]]) -> None:
    rows = [HEADER]
    for index, (asset_id, amount) in enumerate(asset_amounts, start=1):
        rows.append(
            f"RL-{index:06d},{asset_id},source.csv,BMI,2024-01-01,2024-03-31,publishing,performance,{amount:.2f},{amount:.2f},USD\n"
        )
    path.write_text("".join(rows), encoding="utf-8")


def run(args: list[str]) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    return result.returncode, payload


class ConcentrationTest(unittest.TestCase):
    def test_top_n_pcts_computed_for_default_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "ledger.csv"
            write_ledger(
                ledger,
                [("A", 50.0), ("B", 25.0), ("C", 15.0), ("D", 10.0)],
            )
            code, payload = run([str(ledger)])
        self.assertEqual(code, 0)
        catalog = payload["concentration"]["catalog_asset_id"]
        self.assertEqual(catalog["top_1_pct"], 50.0)
        self.assertEqual(catalog["top_3_pct"], 90.0)
        self.assertEqual(catalog["top_5_pct"], 100.0)

    def test_threshold_tripped_emits_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "ledger.csv"
            assumptions = Path(directory) / "assumptions.yaml"
            finding_out = Path(directory) / "concentration-finding.json"
            assumptions.write_text("materiality:\n  concentration_threshold_percent: 40\n", encoding="utf-8")
            write_ledger(ledger, [("A", 60.0), ("B", 20.0), ("C", 20.0)])
            code, payload = run(
                [
                    str(ledger),
                    "--assumptions",
                    str(assumptions),
                    "--emit-finding-output",
                    str(finding_out),
                ]
            )
            findings = json.loads(finding_out.read_text(encoding="utf-8"))["findings"]
        self.assertEqual(code, 0)
        self.assertTrue(payload["tripped_threshold"])
        self.assertEqual(payload["threshold_pct"], 40.0)
        self.assertEqual(payload["threshold_source"], "assumptions.yaml")
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["category"], "valuation")
        self.assertIn("A", finding["affected_assets"])

    def test_threshold_not_tripped_no_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "ledger.csv"
            finding_out = Path(directory) / "concentration-finding.json"
            # 100 assets at $1 each → top_10 = 10%, top_5 = 5%, top_1 = 1%.
            write_ledger(ledger, [(f"A{i:03d}", 1.0) for i in range(100)])
            code, payload = run(
                [
                    str(ledger),
                    "--threshold-pct",
                    "40",
                    "--emit-finding-output",
                    str(finding_out),
                ]
            )
            findings = json.loads(finding_out.read_text(encoding="utf-8"))["findings"]
        self.assertEqual(code, 0)
        self.assertFalse(payload["tripped_threshold"])
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
