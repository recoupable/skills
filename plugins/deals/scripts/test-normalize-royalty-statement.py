#!/usr/bin/env python3
"""Golden-fixture tests for provider CSV royalty normalization."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("normalize-royalty-statement.py")


def write_csv(path: Path, rows: list[dict[str, str]], delimiter: str = ",") -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class NormalizeRoyaltyStatementTest(unittest.TestCase):
    def _invoke(
        self,
        provider: str,
        rows: list[dict[str, str]],
        *,
        column_map: dict[str, str] | None = None,
        delimiter: str = ",",
        delimiter_arg: str | None = None,
    ) -> tuple[list[dict[str, str]], dict, int]:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / ("source.tsv" if delimiter == "\t" else "source.csv")
            output = Path(directory) / "royalty-ledger.csv"
            write_csv(source, rows, delimiter=delimiter)
            argv = [
                sys.executable,
                str(SCRIPT),
                "--provider",
                provider,
                "--input",
                str(source),
                "--output",
                str(output),
            ]
            if column_map is not None:
                map_path = Path(directory) / "column-map.json"
                map_path.write_text(json.dumps(column_map), encoding="utf-8")
                argv += ["--column-map", str(map_path)]
            if delimiter_arg is not None:
                argv += ["--delimiter", delimiter_arg]
            result = subprocess.run(argv, text=True, capture_output=True)
            payload = json.loads(result.stdout) if result.stdout.strip() else {}
            ledger_rows = read_csv(output) if output.exists() else []
            return ledger_rows, payload, result.returncode

    def run_normalizer(self, provider: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        ledger, payload, code = self._invoke(provider, rows)
        self.assertEqual(code, 0, f"normalizer exited {code}: payload={payload}")
        self.assertEqual(payload.get("status"), "ok", f"unexpected status: {payload}")
        return ledger

    def test_normalizes_ascap_performance_rows_with_bonus_detail(self) -> None:
        rows = [
            {
                "Work Title": "Forever Hook",
                "Work ID": "ASC123",
                "ISWC": "T1234567890",
                "Performance Start": "2025-01-01",
                "Performance End": "2025-03-31",
                "Distribution Date": "2025-06-15",
                "Territory": "US",
                "Licensee": "WABC-FM",
                "Use Type": "Feature",
                "Credits": "125.5",
                "Bonus Type": "Audio Feature Premium",
                "Gross Amount": "$1,250.00",
                "Deductions": "$125.00",
                "Publisher Share": "$1,125.00",
                "Currency": "USD",
            }
        ]

        ledger = self.run_normalizer("ascap", rows)

        self.assertEqual(len(ledger), 1)
        row = ledger[0]
        self.assertEqual(row["provider"], "ASCAP")
        self.assertEqual(row["rights_type"], "publishing")
        self.assertEqual(row["income_type"], "performance")
        self.assertEqual(row["catalog_asset_id"], "iswc:T1234567890")
        self.assertEqual(row["platform_or_licensee"], "WABC-FM")
        self.assertEqual(row["gross_amount"], "1250.00")
        self.assertEqual(row["deductions"], "125.00")
        self.assertEqual(row["owner_net_amount"], "1125.00")
        self.assertEqual(row["pro_use_type"], "Feature")
        self.assertEqual(row["pro_credits"], "125.5")
        self.assertEqual(row["pro_bonus_type"], "Audio Feature Premium")

    def test_normalizes_distributor_master_rows(self) -> None:
        rows = [
            {
                "Track Title": "Night Drive",
                "ISRC": "USRC17607839",
                "Sales Month": "2025-02",
                "Store": "Spotify",
                "Territory": "GB",
                "Gross": "500.00",
                "Fee": "75.00",
                "Net": "425.00",
                "Currency": "USD",
            }
        ]

        ledger = self.run_normalizer("distributor", rows)

        self.assertEqual(len(ledger), 1)
        row = ledger[0]
        self.assertEqual(row["provider"], "Distributor")
        self.assertEqual(row["rights_type"], "master")
        self.assertEqual(row["income_type"], "streaming")
        self.assertEqual(row["catalog_asset_id"], "isrc:USRC17607839")
        self.assertEqual(row["period_start"], "2025-02-01")
        self.assertEqual(row["period_end"], "2025-02-28")
        self.assertEqual(row["platform_or_licensee"], "Spotify")
        self.assertEqual(row["owner_net_amount"], "425.00")

    def test_rejects_unknown_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            output = Path(directory) / "royalty-ledger.csv"
            write_csv(source, [{"Title": "Unknown", "Amount": "10"}])
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--provider",
                    "not-a-provider",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsupported provider", result.stderr)

    def test_returns_partial_status_when_financial_columns_unknown(self) -> None:
        rows = [
            {"title": "Letter from Hattiesburg", "writer": "Marvin Briggs", "iswc": "T-901112322-8", "share_pct": "50", "net_royalty_usd": "186.49"},
            {"title": "Don't Stop Now", "writer": "Mari Vega", "iswc": "T-922001124-7", "share_pct": "75", "net_royalty_usd": "356.25"},
        ]
        ledger, payload, code = self._invoke("bmi", rows)
        self.assertEqual(code, 1, f"expected exit 1 for partial, got {code}: {payload}")
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["rows"], 2)
        self.assertLess(payload["field_population_rate"], 0.5)
        warnings = payload.get("warnings", [])
        self.assertEqual(len(warnings), 1)
        missing = warnings[0]["expected_columns_not_found"]
        for required in ["Statement Qtr", "Period Start", "Period End", "Publisher Net", "Net", "Amount", "Gross Amount", "Amount Paid"]:
            self.assertIn(required, missing, f"'{required}' should be flagged missing; got {missing}")
        self.assertEqual(len(ledger), 2)
        self.assertEqual(ledger[0]["catalog_asset_id"], "iswc:T-901112322-8")
        self.assertEqual(ledger[0]["gross_amount"], "")
        self.assertEqual(ledger[0]["owner_net_amount"], "")

    def test_column_map_fills_missing_canonical_fields(self) -> None:
        rows = [
            {"title": "Letter from Hattiesburg", "writer": "Marvin Briggs", "iswc": "T-901112322-8", "share_pct": "50", "net_royalty_usd": "186.49"},
            {"title": "Don't Stop Now", "writer": "Mari Vega", "iswc": "T-922001124-7", "share_pct": "75", "net_royalty_usd": "356.25"},
        ]
        column_map = {"net_royalty_usd": "owner_net_amount", "share_pct": "participant_share"}
        ledger, payload, _ = self._invoke("bmi", rows, column_map=column_map)
        self.assertEqual(ledger[0]["owner_net_amount"], "186.49")
        self.assertEqual(ledger[1]["owner_net_amount"], "356.25")
        self.assertEqual(ledger[0]["participant_share"], "50")
        self.assertGreater(payload["field_population_rate"], 0)

    def test_column_map_rejects_non_canonical_target(self) -> None:
        rows = [{"title": "x", "iswc": "T1", "amount_usd": "10"}]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            output = Path(directory) / "out.csv"
            map_path = Path(directory) / "map.json"
            write_csv(source, rows)
            map_path.write_text(json.dumps({"amount_usd": "not_a_field"}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--provider",
                    "bmi",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--column-map",
                    str(map_path),
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a canonical ledger column", result.stderr)

    def test_auto_sniffs_tsv_input(self) -> None:
        rows = [
            {"Song Title": "Night Drive", "ISWC": "T9999999990", "Period Start": "2024-01-01", "Period End": "2024-01-31", "Mechanical Gross": "100.00", "Publisher Net": "85.00", "Currency": "USD"},
        ]
        ledger, payload, code = self._invoke("mlc", rows, delimiter="\t")
        self.assertEqual(code, 0, f"unexpected exit: payload={payload}")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["gross_amount"], "100.00")
        self.assertEqual(ledger[0]["owner_net_amount"], "85.00")
        self.assertEqual(ledger[0]["period_start"], "2024-01-01")


if __name__ == "__main__":
    unittest.main()
