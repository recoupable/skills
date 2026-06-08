#!/usr/bin/env python3
"""Smoke test for PDF royalty-statement extraction.

Builds a small text-based PDF with reportlab, runs extract-pdf-statement.py
against it, and asserts the rows map into the canonical ledger schema. Both
pdfplumber (read) and reportlab (write) are optional deps, so the round-trip
test skips cleanly where either is missing — but the no-dependency CLI
contract (non-PDF input) is always checked.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("extract-pdf-statement.py")

try:
    import pdfplumber  # noqa: F401

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def build_sesac_pdf(pdf_path: Path) -> None:
    """A SESAC-shaped statement: Title | ISWC | Writer Share | Publisher Share | Total.

    The sesac template uses amount_index=3 (Publisher Share) for owner_net and
    gross_index=4 (Total); period is derived from the year in the filename.
    A GRID style gives pdfplumber ruling lines so it detects the table.
    """
    data = [
        ["Title", "ISWC", "Writer Share", "Publisher Share", "Total"],
        ["Midnight in West Egg", "T1234567890", "50%", "100.00", "200.00"],
        ["Green Light", "T2222222220", "50%", "250.00", "500.00"],
    ]
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    table = Table(data)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    doc.build([table])


class ExtractPdfStatementTest(unittest.TestCase):
    def test_rejects_non_pdf_input(self) -> None:
        """The CLI must fail clearly on a non-PDF, non-directory input."""
        with tempfile.TemporaryDirectory() as directory:
            not_pdf = Path(directory) / "notes.txt"
            not_pdf.write_text("not a pdf", encoding="utf-8")
            output = Path(directory) / "out.csv"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(not_pdf), "--output", str(output)],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a PDF", result.stderr)

    @unittest.skipUnless(HAS_PDFPLUMBER and HAS_REPORTLAB, "needs pdfplumber + reportlab")
    def test_extracts_sesac_statement_into_canonical_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            # path includes /sesac/ and a year so detection + period work
            src_dir = Path(directory) / "source" / "sesac"
            src_dir.mkdir(parents=True)
            pdf_path = src_dir / "sesac-2024.pdf"
            build_sesac_pdf(pdf_path)
            output = Path(directory) / "pdf-extracted-ledger.csv"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(pdf_path),
                    "--output",
                    str(output),
                    "--provider",
                    "sesac",
                    "--workspace-root",
                    directory,
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout) if result.stdout.strip() else {}
            self.assertEqual(payload.get("rows_total"), 2, payload)
            self.assertEqual(payload.get("pdfs_extracted"), 1, payload)

            ledger = read_csv(output)
            self.assertEqual(len(ledger), 2)
            by_net = {row["owner_net_amount"]: row for row in ledger}
            self.assertIn("100.00", by_net)
            self.assertIn("250.00", by_net)
            first = by_net["100.00"]
            self.assertEqual(first["provider"], "SESAC")
            self.assertEqual(first["rights_type"], "publishing")
            self.assertEqual(first["catalog_asset_id"], "iswc:T1234567890")
            self.assertEqual(first["gross_amount"], "200.00")
            self.assertEqual(first["period_start"], "2024-01-01")
            self.assertEqual(first["period_end"], "2024-12-31")
            # every extracted row is flagged low-confidence for human verification
            self.assertTrue(all(row["match_confidence"] == "low" for row in ledger))
            self.assertTrue(all(row["ledger_line_id"].startswith("PDF-") for row in ledger))


if __name__ == "__main__":
    unittest.main()
