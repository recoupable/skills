#!/usr/bin/env python3
"""Tests for auto-column-map.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
AUTO_MAP = SCRIPT_DIR / "auto-column-map.py"
NORMALIZER = SCRIPT_DIR / "normalize-royalty-statement.py"


def run_auto_map(provider: str, input_path: Path, output_path: Path | None = None) -> tuple[int, dict]:
    args = [sys.executable, str(AUTO_MAP), "--provider", provider, "--input", str(input_path)]
    if output_path is not None:
        args += ["--output", str(output_path)]
    result = subprocess.run(args, check=False, text=True, capture_output=True)
    payload = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"_raw": result.stdout, "_stderr": result.stderr}
    return result.returncode, payload


class AutoColumnMapTest(unittest.TestCase):
    def test_recovers_full_mapping_for_seller_renamed_distributor_export(self) -> None:
        """A distributor export with renamed columns should round-trip
        through the normalizer once auto-column-map writes a column-map.
        """
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            input_path = workspace / "seller-distributor.csv"
            input_path.write_text(
                "Track Title,ISRC,Sales Period,Gross Revenue,Net Revenue,Country,Store,Currency\n"
                "Bright Lights,USRC18000001,2024-01,1200.00,950.00,US,Spotify,USD\n"
                "Slow Lightning,USRC18000002,2024-01,800.00,640.00,US,Apple,USD\n",
                encoding="utf-8",
            )
            map_path = workspace / "column-map.json"
            returncode, payload = run_auto_map("distributor", input_path, map_path)
            # Read the map file BEFORE the tempdir context exits.
            bare_map = json.loads(map_path.read_text(encoding="utf-8"))

        self.assertEqual(returncode, 0, msg=payload)
        self.assertEqual(payload["status"], "ok")
        critical = payload["critical_fields"]
        for field in ("gross_amount", "owner_net_amount", "period_start"):
            self.assertEqual(
                critical[field]["status"],
                "ok",
                msg=f"{field} not recovered: {payload}",
            )
        # The written column-map.json is the bare {src: canonical} object
        # the normalizer accepts via --column-map.
        self.assertEqual(bare_map.get("Gross Revenue"), "gross_amount")
        self.assertEqual(bare_map.get("Net Revenue"), "owner_net_amount")
        self.assertEqual(bare_map.get("Sales Period"), "period_start")

    def test_returns_needs_review_when_critical_fields_unrecoverable(self) -> None:
        """The bmi-real-headers fixture is missing period and gross headers.
        The mapper should flag exactly those as missing instead of pretending
        the file is mappable.
        """
        bmi_input = SCRIPT_DIR.parent / "fixtures" / "golden" / "bmi-real-headers" / "input.csv"
        self.assertTrue(bmi_input.is_file(), msg=str(bmi_input))
        returncode, payload = run_auto_map("bmi", bmi_input)
        self.assertEqual(returncode, 1, msg=payload)
        self.assertEqual(payload["status"], "needs_review")
        critical = payload["critical_fields"]
        # net_royalty_usd ~ owner_net_amount should still recover.
        self.assertEqual(critical["owner_net_amount"]["status"], "ok")
        # No period column or gross column in this input.
        self.assertEqual(critical["period_start"]["status"], "missing")
        self.assertEqual(critical["gross_amount"]["status"], "missing")

    def test_generated_map_unblocks_partial_status_in_normalizer(self) -> None:
        """End-to-end: auto-column-map writes a JSON file, then the normalizer
        consumes it via --column-map and produces a populated ledger row."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            input_path = workspace / "publisher-admin.csv"
            input_path.write_text(
                "Track Title,ISRC,Sales Period,Gross Revenue,Net Revenue,Country,Store,Currency\n"
                "Bright Lights,USRC18000001,2024-01,1200.00,950.00,US,Spotify,USD\n",
                encoding="utf-8",
            )
            map_path = workspace / "column-map.json"
            ledger_path = workspace / "ledger.csv"

            map_rc, map_payload = run_auto_map("publisher-admin", input_path, map_path)
            self.assertEqual(map_rc, 0, msg=map_payload)

            normalize_rc = subprocess.run(
                [
                    sys.executable,
                    str(NORMALIZER),
                    "--provider",
                    "publisher-admin",
                    "--input",
                    str(input_path),
                    "--output",
                    str(ledger_path),
                    "--column-map",
                    str(map_path),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(normalize_rc.returncode, 0, msg=normalize_rc.stderr)
            normalize_payload = json.loads(normalize_rc.stdout)
            self.assertEqual(normalize_payload["status"], "ok", msg=normalize_payload)


if __name__ == "__main__":
    unittest.main()
