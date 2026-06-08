#!/usr/bin/env python3
"""Golden fixture tests for PDF royalty-statement extraction.

Each `fixtures/golden/<society>-pdf/` directory holds a committed `input` PDF
(one *.pdf) and the `expected-royalty-ledger.csv` it must produce. The provider
is the directory name minus the `-pdf` suffix. PDFs are committed, so this test
needs only pdfplumber (read), not reportlab (write) — regenerate the PDFs with
`fixtures/golden/generate-pdf-fixtures.py` if a template's layout changes.
"""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "extract-pdf-statement.py"
FIXTURE_ROOT = PLUGIN_ROOT / "fixtures" / "golden"

try:
    import pdfplumber  # noqa: F401

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def discover_pdf_cases() -> list[tuple[str, Path, Path]]:
    """Return (provider, pdf_path, expected_csv_path) for each *-pdf fixture."""
    cases: list[tuple[str, Path, Path]] = []
    for case_dir in sorted(FIXTURE_ROOT.glob("*-pdf")):
        if not case_dir.is_dir():
            continue
        provider = case_dir.name[: -len("-pdf")]
        pdfs = sorted(case_dir.glob("*.pdf"))
        if not pdfs:
            continue
        cases.append((provider, pdfs[0], case_dir / "expected-royalty-ledger.csv"))
    return cases


@unittest.skipUnless(HAS_PDFPLUMBER, "needs pdfplumber")
class GoldenPdfFixtureTest(unittest.TestCase):
    def test_all_pdf_fixtures_match_expected_ledgers(self) -> None:
        cases = discover_pdf_cases()
        self.assertGreaterEqual(len(cases), 9, f"expected >=9 PDF fixtures, found {len(cases)}")
        for provider, pdf_path, expected_path in cases:
            with self.subTest(provider=provider):
                self.assertTrue(expected_path.exists(), f"missing expected ledger: {expected_path}")
                with tempfile.TemporaryDirectory() as directory:
                    actual_path = Path(directory) / "actual.csv"
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SCRIPT),
                            str(pdf_path),
                            "--provider",
                            provider,
                            "--workspace-root",
                            str(pdf_path.parent),
                            "--output",
                            str(actual_path),
                        ],
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode, 0, f"{provider}: {result.stderr}")
                    self.assertEqual(
                        read_csv(actual_path),
                        read_csv(expected_path),
                        f"{provider}: extracted ledger drifted from golden expectation",
                    )


if __name__ == "__main__":
    unittest.main()
