#!/usr/bin/env python3
"""Tests for build-manual-review-queue.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
QUEUE = SCRIPT_DIR / "build-manual-review-queue.py"
MANIFEST = SCRIPT_DIR / "build-file-manifest.py"


def make_workspace(root: Path) -> Path:
    workspace = root / "deals" / "test-deal"
    source = workspace / "source"
    source.mkdir(parents=True, exist_ok=True)
    (source / "00_README.txt").write_text("seller readme", encoding="utf-8")
    bmi = source / "03_Royalty_Statements" / "BMI"
    bmi.mkdir(parents=True, exist_ok=True)
    (bmi / "Q1_2023.csv").write_text("title,iswc\nA,T1\n", encoding="utf-8")
    ascap = source / "03_Royalty_Statements" / "ASCAP"
    ascap.mkdir(parents=True, exist_ok=True)
    (ascap / "Q1_2023.pdf").write_bytes(b"%PDF-1.4 fake")
    rights = source / "04_Rights_Documents" / "Split_Sheets"
    rights.mkdir(parents=True, exist_ok=True)
    (rights / "Sun_Up_Mary_1973.pdf").write_bytes(b"%PDF-1.4 fake")
    mlc = source / "03_Royalty_Statements" / "MLC"
    mlc.mkdir(parents=True, exist_ok=True)
    (mlc / "statement_2023-08.tsv").write_text("", encoding="utf-8")  # 0-byte
    (workspace / "normalized").mkdir(parents=True, exist_ok=True)
    (workspace / "normalized" / "royalty-ledger.csv").write_text(
        "ledger_line_id,catalog_asset_id,source_file,provider,period_start,period_end,rights_type,income_type,gross_amount,owner_net_amount,currency\n"
        "RL-000001,iswc:T1,source/03_Royalty_Statements/BMI/Q1_2023.csv,BMI,2023-01-01,2023-03-31,publishing,performance,1000.00,850.00,USD\n",
        encoding="utf-8",
    )
    (workspace / "findings").mkdir(parents=True, exist_ok=True)
    (workspace / "workpapers").mkdir(parents=True, exist_ok=True)
    return workspace


def run_manifest(workspace: Path) -> None:
    subprocess.run(
        [sys.executable, str(MANIFEST), str(workspace)],
        check=True,
        text=True,
        capture_output=True,
    )


def run_queue(workspace: Path) -> tuple[int, dict, dict, str]:
    result = subprocess.run(
        [sys.executable, str(QUEUE), str(workspace)],
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    coverage = json.loads((workspace / "workpapers" / "ingest-coverage.json").read_text(encoding="utf-8"))
    queue_md = (workspace / "findings" / "manual-review-queue.md").read_text(encoding="utf-8")
    return result.returncode, payload, coverage, queue_md


class ManualReviewQueueTest(unittest.TestCase):
    def test_summary_line_reports_contribution_and_review_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            run_manifest(workspace)
            code, payload, coverage, queue_md = run_queue(workspace)
        self.assertEqual(code, 0, payload)
        self.assertIn("contributed financial data", payload["summary_line"])
        self.assertEqual(coverage["contributed_count"], 1)
        self.assertEqual(coverage["total_files"], 5)
        self.assertGreaterEqual(coverage["manual_review_count"], 3)
        self.assertEqual(coverage["unparsed_count"], 1)

    def test_pdf_files_get_extract_action_with_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            run_manifest(workspace)
            _code, _payload, _coverage, queue_md = run_queue(workspace)
        self.assertIn("ASCAP/Q1_2023.pdf", queue_md)
        self.assertIn("Extract financial detail from PDF (provider: ASCAP)", queue_md)

    def test_zero_byte_file_gets_reissue_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            run_manifest(workspace)
            _code, _payload, _coverage, queue_md = run_queue(workspace)
        self.assertIn("statement_2023-08.tsv", queue_md)
        self.assertIn("zero bytes", queue_md)

    def test_fails_when_manifest_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(Path(directory))
            # Skip manifest creation.
            result = subprocess.run(
                [sys.executable, str(QUEUE), str(workspace)],
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("file-manifest.json", result.stderr)


if __name__ == "__main__":
    unittest.main()
