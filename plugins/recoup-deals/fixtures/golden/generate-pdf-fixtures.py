#!/usr/bin/env python3
"""Regenerate the golden PDF input fixtures for extract-pdf-statement.py.

Each society template gets one small text-based PDF whose table columns match
that template's expected indices, header signatures, and period encoding
(filename year/quarter, or an in-row year for HFA). The generated `input.pdf`
files are committed as golden fixtures and read back by
`scripts/test-golden-pdf-fixtures.py`; that test needs only pdfplumber, so it
runs even where reportlab (used here) is absent.

Run from anywhere:  python3 fixtures/golden/generate-pdf-fixtures.py
Requires: pip3 install reportlab
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


FIXTURE_ROOT = Path(__file__).resolve().parent


# (case dir, pdf filename, header row, data rows). The pdf filename encodes the
# period for filename_year / filename_quarter templates; HFA carries its year
# in a row column instead.
CASES: list[tuple[str, str, list[str], list[list[str]]]] = [
    (
        "ascap-pdf",
        "ascap-2024Q1.pdf",
        ["Writer Legal Name", "Work Title", "ISWC", "Share %", "Performances", "Publisher $", "Total $"],
        [
            ["Marvin Briggs", "Letter from Hattiesburg", "T1234567890", "50%", "1200", "186.49", "372.98"],
            ["Mari Vega", "Don't Stop Now", "T2229991147", "75%", "2400", "356.25", "475.00"],
        ],
    ),
    (
        "hfa-pdf",
        "hfa-statement.pdf",
        ["Song Title", "ISWC", "Usage Year", "Mechanical Royalty"],
        [
            ["Bright Lights", "T3001234560", "2023", "842.17"],
            ["Slow Tide", "T3009998870", "2023", "129.40"],
        ],
    ),
    (
        "soundexchange-pdf",
        "soundexchange-2024.pdf",
        ["Recording", "ISRC", "Label", "Plays", "Distribution"],
        [
            ["Midnight Run", "USRC11500001", "Indie Co", "50000", "410.22"],
            ["Coastline", "USRC11500002", "Indie Co", "12000", "98.10"],
        ],
    ),
    (
        "prs-pdf",
        "prs-2024.pdf",
        ["Title", "ISWC", "Royalty (GBP)"],
        [
            ["London Rain", "T4001112220", "275.50"],
            ["Underground", "T4009990001", "61.00"],
        ],
    ),
    (
        "sacem-pdf",
        "sacem-2024Q2.pdf",
        ["Titre", "ISWC", "Droits (EUR)"],
        [
            ["Nuit Parisienne", "T5001112220", "320.75"],
            ["Lumiere", "T5009990001", "88.40"],
        ],
    ),
    (
        "sadaic-pdf",
        "sadaic-2024.pdf",
        ["Titulo", "ISWC", "Liquidacion (ARS)"],
        [
            ["Calle Sur", "T6001112220", "15000.00"],
            ["Tango Nuevo", "T6009990001", "4200.50"],
        ],
    ),
    (
        "jasrac-pdf",
        "jasrac-2024.pdf",
        ["Title", "ISWC", "Distribution (JPY)"],
        [
            ["Tokyo Lights", "T7001112220", "48000.00"],
            ["Sakura", "T7009990001", "9500.00"],
        ],
    ),
    (
        "apra-pdf",
        "apra-2024.pdf",
        ["Title", "ISWC", "Royalty"],
        [
            ["Outback Sky", "T8001112220", "612.30"],
            ["Reef", "T8009990001", "145.00"],
        ],
    ),
    (
        "socan-pdf",
        "socan-2024.pdf",
        ["Title", "ISWC", "Royalty"],
        [
            ["Northern Lights", "T9001112220", "388.90"],
            ["Maple", "T9009990001", "102.25"],
        ],
    ),
]


def build_pdf(pdf_path: Path, header: list[str], rows: list[list[str]]) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    table = Table([header, *rows])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    doc.build([table])


def main() -> None:
    for case_dir, filename, header, rows in CASES:
        out = FIXTURE_ROOT / case_dir / filename
        build_pdf(out, header, rows)
        print(f"wrote {out.relative_to(FIXTURE_ROOT)}")


if __name__ == "__main__":
    main()
