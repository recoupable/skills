#!/usr/bin/env python3
"""Run golden fixture tests for royalty statement normalization."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "normalize-royalty-statement.py"
FIXTURE_ROOT = PLUGIN_ROOT / "fixtures" / "golden"


CASES = [
    ("ascap-performance", "ascap"),
    ("bmi-performance", "bmi"),
    ("mlc-mechanical", "mlc"),
    ("distributor-master", "distributor"),
    ("publisher-admin", "publisher-admin"),
    ("soundexchange", "soundexchange"),
    ("direct-sync", "direct-sync"),
    ("youtube-content-id", "youtube-content-id"),
    ("curve-income", "curve"),
]


# Cases where the input deliberately exercises partial-status behavior. The
# expected-status.json file describes the assertions to apply against the
# normalizer's stdout payload.
PARTIAL_CASES = [
    ("bmi-real-headers", "bmi"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def run_normalizer(provider: str, input_path: Path, output_path: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--provider",
            provider,
            "--input",
            str(input_path.relative_to(PLUGIN_ROOT)),
            "--output",
            str(output_path),
        ],
        cwd=PLUGIN_ROOT,
        text=True,
        capture_output=True,
    )
    payload: dict = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"_raw_stdout": result.stdout}
    return result.returncode, payload


class GoldenFixtureTest(unittest.TestCase):
    def test_all_golden_fixtures_match_expected_ledgers(self) -> None:
        for case_name, provider in CASES:
            with self.subTest(case=case_name):
                case_dir = FIXTURE_ROOT / case_name
                input_path = case_dir / "input.csv"
                expected_path = case_dir / "expected-royalty-ledger.csv"
                self.assertTrue(input_path.exists(), f"Missing input fixture: {input_path}")
                self.assertTrue(expected_path.exists(), f"Missing expected fixture: {expected_path}")

                with tempfile.TemporaryDirectory() as directory:
                    actual_path = Path(directory) / "actual.csv"
                    returncode, payload = run_normalizer(provider, input_path, actual_path)
                    self.assertEqual(
                        returncode,
                        0,
                        f"{case_name}: expected exit 0 (status=ok), got {returncode}: {payload}",
                    )
                    self.assertEqual(payload.get("status"), "ok", f"{case_name}: {payload}")
                    self.assertEqual(read_csv(actual_path), read_csv(expected_path))

    def test_partial_status_fixtures_surface_missing_columns(self) -> None:
        for case_name, provider in PARTIAL_CASES:
            with self.subTest(case=case_name):
                case_dir = FIXTURE_ROOT / case_name
                input_path = case_dir / "input.csv"
                expected_ledger_path = case_dir / "expected-royalty-ledger.csv"
                expected_status_path = case_dir / "expected-status.json"
                self.assertTrue(input_path.exists(), f"Missing input fixture: {input_path}")
                self.assertTrue(expected_status_path.exists(), f"Missing status spec: {expected_status_path}")
                expected_status = json.loads(expected_status_path.read_text(encoding="utf-8"))

                with tempfile.TemporaryDirectory() as directory:
                    actual_path = Path(directory) / "actual.csv"
                    returncode, payload = run_normalizer(provider, input_path, actual_path)
                    expected_returncode = 1 if expected_status["status"] != "ok" else 0
                    self.assertEqual(returncode, expected_returncode, f"{case_name}: payload={payload}")
                    self.assertEqual(payload.get("status"), expected_status["status"], f"{case_name}: {payload}")
                    self.assertEqual(payload.get("rows"), expected_status["rows"], f"{case_name}: {payload}")
                    self.assertEqual(
                        payload.get("field_population_rate"),
                        expected_status["field_population_rate"],
                        f"{case_name}: {payload}",
                    )
                    self.assertEqual(
                        payload.get("headers_seen"),
                        expected_status["headers_seen"],
                        f"{case_name}: {payload}",
                    )

                    warnings = payload.get("warnings") or []
                    self.assertTrue(warnings, f"{case_name}: expected warnings, got {payload}")
                    missing_columns = warnings[0].get("expected_columns_not_found", [])
                    for required_missing in expected_status["expected_columns_not_found_includes"]:
                        self.assertIn(
                            required_missing,
                            missing_columns,
                            f"{case_name}: '{required_missing}' should appear in expected_columns_not_found "
                            f"({missing_columns})",
                        )

                    if expected_ledger_path.exists():
                        self.assertEqual(read_csv(actual_path), read_csv(expected_ledger_path))


if __name__ == "__main__":
    unittest.main()
