#!/usr/bin/env python3
"""Extract royalty data from PDF statements into the canonical ledger schema.

Uses pdfplumber to read tables from PDFs and per-provider templates to map
columns into the canonical royalty-ledger.csv shape. Provider templates are
matched by file path (folder/filename) and verified by header signature.

Output rows are written to a separate ledger file so the agent can review
before merging into normalized/royalty-ledger.csv. Every row is tagged
with `match_confidence: low` and `notes: extracted from PDF, verify against source`
to mark them for verification.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import pdfplumber  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - import-time guard
    print(
        json.dumps(
            {
                "status": "missing_dependency",
                "error": "pdfplumber is required. Install via: pip3 install -r requirements.txt",
                "details": str(exc),
            }
        ),
        file=sys.stderr,
    )
    raise SystemExit(1)


CANONICAL_COLUMNS = [
    "ledger_line_id",
    "catalog_asset_id",
    "source_file",
    "provider",
    "period_start",
    "period_end",
    "payment_date",
    "rights_type",
    "income_type",
    "territory",
    "platform_or_licensee",
    "gross_amount",
    "deductions",
    "participant_share",
    "owner_net_amount",
    "currency",
    "fx_rate",
    "pro_use_type",
    "pro_credits",
    "pro_bonus_type",
    "cue_sheet_ref",
    "match_confidence",
    "notes",
]


CURRENCY_PATTERNS = [
    (re.compile(r"^\s*\$\s*"), "USD"),
    (re.compile(r"^\s*USD\s*\$?\s*"), "USD"),
    (re.compile(r"^\s*EUR\s*€?\s*|^\s*€\s*"), "EUR"),
    (re.compile(r"^\s*GBP\s*£?\s*|^\s*£\s*"), "GBP"),
    (re.compile(r"^\s*JPY\s*¥?\s*|^\s*¥\s*"), "JPY"),
    (re.compile(r"^\s*ARS\s*\$?\s*|^\s*\$ARS\s*"), "ARS"),
    (re.compile(r"^\s*AUD\s*\$?\s*"), "AUD"),
    (re.compile(r"^\s*CAD\s*\$?\s*"), "CAD"),
]


@dataclass(frozen=True)
class PDFTemplate:
    name: str
    provider: str
    rights_type: str
    income_type: str
    territory: str
    default_currency: str
    # Header regexes — at least one must match the table's first row.
    header_signatures: tuple[re.Pattern, ...]
    # Filename/folder regexes — at least one must match.
    path_signatures: tuple[re.Pattern, ...] = ()
    # Column indices (0-based) on the data row.
    title_index: int = 0
    iswc_index: int | None = 1
    isrc_index: int | None = None
    amount_index: int = 2  # net amount
    gross_index: int | None = None
    share_index: int | None = None
    period_index: int | None = None  # if period encoded per-row
    period_format: str = "filename_quarter"  # filename_quarter | filename_year | row_year | row_period | row_quarter
    expected_columns: int | None = None


def _re(pat: str) -> re.Pattern:
    return re.compile(pat, re.IGNORECASE)


TEMPLATES: list[PDFTemplate] = [
    PDFTemplate(
        name="ascap",
        provider="ASCAP",
        rights_type="publishing",
        income_type="performance",
        territory="US",
        default_currency="USD",
        header_signatures=(_re(r"writer.*legal.*name"), _re(r"share\s*%"), _re(r"publisher\s*\$")),
        path_signatures=(_re(r"/ascap/"),),
        title_index=1,
        iswc_index=2,
        amount_index=5,  # Publisher $
        gross_index=6,  # Total $
        share_index=3,
        period_format="filename_quarter",
        expected_columns=7,
    ),
    PDFTemplate(
        name="sesac",
        provider="SESAC",
        rights_type="publishing",
        income_type="performance",
        territory="US",
        default_currency="USD",
        header_signatures=(_re(r"writer\s*share"), _re(r"publisher\s*shar")),
        path_signatures=(_re(r"/sesac/"),),
        title_index=0,
        iswc_index=1,
        amount_index=3,  # Publisher Share column
        gross_index=4,  # Total
        period_format="filename_year",
    ),
    PDFTemplate(
        name="hfa",
        provider="HFA",
        rights_type="publishing",
        income_type="mechanical",
        territory="US",
        default_currency="USD",
        header_signatures=(_re(r"mechanical\s*royalty"),),
        path_signatures=(_re(r"/hfa[\s_-]?legacy/|hfa_"),),
        title_index=0,
        iswc_index=1,
        amount_index=3,
        period_index=2,
        period_format="row_year",
    ),
    PDFTemplate(
        name="soundexchange",
        provider="SoundExchange",
        rights_type="neighboring",
        income_type="radio",
        territory="US",
        default_currency="USD",
        header_signatures=(_re(r"distribution"), _re(r"isrc"), _re(r"label")),
        path_signatures=(_re(r"/soundexchange/"),),
        title_index=0,
        iswc_index=None,
        isrc_index=1,
        amount_index=4,
        period_format="filename_year",
    ),
    PDFTemplate(
        name="prs-partial",
        provider="PRS",
        rights_type="publishing",
        income_type="performance",
        territory="GB",
        default_currency="GBP",
        header_signatures=(_re(r"royalty\s*\(gbp\)"), _re(r"period")),
        path_signatures=(_re(r"prs.*partial"),),
        title_index=1,
        iswc_index=2,
        amount_index=3,
        period_index=0,
        period_format="row_quarter",
    ),
    PDFTemplate(
        name="prs",
        provider="PRS",
        rights_type="publishing",
        income_type="performance",
        territory="GB",
        default_currency="GBP",
        header_signatures=(_re(r"royalty\s*\(gbp\)"),),
        path_signatures=(_re(r"prs"),),
        title_index=0,
        iswc_index=1,
        amount_index=2,
        period_format="filename_year",
    ),
    PDFTemplate(
        name="sacem",
        provider="SACEM",
        rights_type="publishing",
        income_type="performance",
        territory="FR",
        default_currency="EUR",
        header_signatures=(_re(r"droits\s*\(eur\)"), _re(r"titre")),
        path_signatures=(_re(r"sacem"),),
        title_index=0,
        iswc_index=1,
        amount_index=2,
        period_format="filename_quarter",
    ),
    PDFTemplate(
        name="sadaic",
        provider="SADAIC",
        rights_type="publishing",
        income_type="performance",
        territory="AR",
        default_currency="ARS",
        header_signatures=(_re(r"liquidaci(ón|on)\s*\(ars\)"), _re(r"t(í|i)tulo")),
        path_signatures=(_re(r"sadaic"),),
        title_index=0,
        iswc_index=1,
        amount_index=2,
        period_format="filename_year",
    ),
    PDFTemplate(
        name="jasrac",
        provider="JASRAC",
        rights_type="publishing",
        income_type="performance",
        territory="JP",
        default_currency="JPY",
        header_signatures=(_re(r"distribution\s*\(jpy\)"),),
        path_signatures=(_re(r"jasrac"),),
        title_index=0,
        iswc_index=1,
        amount_index=2,
        period_format="filename_year",
    ),
    PDFTemplate(
        name="apra",
        provider="APRA",
        rights_type="publishing",
        income_type="performance",
        territory="AU",
        default_currency="AUD",
        header_signatures=(_re(r"^title$"), _re(r"^iswc$"), _re(r"^royalty$")),
        path_signatures=(_re(r"apra"),),
        title_index=0,
        iswc_index=1,
        amount_index=2,
        period_format="filename_year",
    ),
    PDFTemplate(
        name="socan",
        provider="SOCAN",
        rights_type="publishing",
        income_type="performance",
        territory="CA",
        default_currency="CAD",
        header_signatures=(_re(r"^title$"), _re(r"^iswc$"), _re(r"^royalty$")),
        path_signatures=(_re(r"socan"),),
        title_index=0,
        iswc_index=1,
        amount_index=2,
        period_format="filename_year",
    ),
]


def _normalize_header_cell(cell: str | None) -> str:
    if not cell:
        return ""
    return re.sub(r"\s+", " ", cell.strip())


def _normalize_header(headers: list[str | None]) -> str:
    return " | ".join(_normalize_header_cell(c) for c in headers if c)


def detect_template(rel_path: str, headers: list[str | None]) -> PDFTemplate | None:
    header_text = _normalize_header(headers).lower()
    rel_lower = rel_path.lower()
    candidates: list[tuple[int, PDFTemplate]] = []
    for template in TEMPLATES:
        path_hits = sum(2 for pattern in template.path_signatures if pattern.search(rel_lower))
        header_hits = sum(1 for pattern in template.header_signatures if pattern.search(header_text))
        # Qualify when either signal is strong: a clear path match, or any
        # header keyword match. Generic header layouts ("Title | ISWC | Royalty"
        # for APRA/SOCAN) are disambiguated entirely by path.
        if path_hits == 0 and header_hits == 0:
            continue
        score = path_hits + header_hits
        candidates.append((score, template))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def parse_amount(raw: str | None) -> tuple[float | None, str | None]:
    if not raw:
        return None, None
    text = raw.strip()
    detected_currency: str | None = None
    for pattern, currency in CURRENCY_PATTERNS:
        new_text = pattern.sub("", text)
        if new_text != text:
            text = new_text
            detected_currency = currency
            break
    text = text.replace(",", "").replace("$", "").replace("€", "").replace("£", "").replace("¥", "").strip()
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text.strip("()")
    if not text:
        return None, detected_currency
    try:
        return float(text), detected_currency
    except ValueError:
        return None, detected_currency


def filename_quarter(filename: str) -> tuple[str, str] | None:
    match = re.search(r"Q([1-4])[\s_-]?(\d{4})|([1-4])Q[\s_-]?(\d{4})|(\d{4})[\s_-]?Q([1-4])", filename, re.IGNORECASE)
    if not match:
        return None
    if match.group(1):
        quarter = int(match.group(1))
        year = int(match.group(2))
    elif match.group(3):
        quarter = int(match.group(3))
        year = int(match.group(4))
    else:
        year = int(match.group(5))
        quarter = int(match.group(6))
    return _quarter_to_period(year, quarter)


def filename_year(filename: str) -> tuple[str, str] | None:
    match = re.search(r"(?<!\d)(20\d{2}|19\d{2})(?!\d)", filename)
    if not match:
        return None
    year = int(match.group(1))
    return f"{year}-01-01", f"{year}-12-31"


def _quarter_to_period(year: int, quarter: int) -> tuple[str, str]:
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    last_day = calendar.monthrange(year, end_month)[1]
    return f"{year:04d}-{start_month:02d}-01", f"{year:04d}-{end_month:02d}-{last_day:02d}"


def row_quarter(value: str) -> tuple[str, str] | None:
    match = re.search(r"Q([1-4])\s*(\d{4})|(\d{4})\s*Q([1-4])", value or "", re.IGNORECASE)
    if not match:
        return None
    if match.group(1):
        return _quarter_to_period(int(match.group(2)), int(match.group(1)))
    return _quarter_to_period(int(match.group(3)), int(match.group(4)))


def row_year(value: str) -> tuple[str, str] | None:
    match = re.search(r"(20\d{2}|19\d{2})", value or "")
    if not match:
        return None
    year = int(match.group(1))
    return f"{year}-01-01", f"{year}-12-31"


def determine_period(template: PDFTemplate, filename: str, row: list[str]) -> tuple[str, str]:
    if template.period_format == "filename_quarter":
        return filename_quarter(filename) or filename_year(filename) or ("", "")
    if template.period_format == "filename_year":
        return filename_year(filename) or ("", "")
    if template.period_format == "row_quarter" and template.period_index is not None:
        return row_quarter(row[template.period_index] or "") or ("", "")
    if template.period_format == "row_year" and template.period_index is not None:
        return row_year(row[template.period_index] or "") or ("", "")
    if template.period_format == "row_period" and template.period_index is not None:
        return (row[template.period_index] or "").strip(), ""
    return "", ""


def asset_id_from_row(template: PDFTemplate, row: list[str]) -> str:
    if template.iswc_index is not None and template.iswc_index < len(row):
        iswc = (row[template.iswc_index] or "").strip()
        if iswc:
            return f"iswc:{iswc}"
    if template.isrc_index is not None and template.isrc_index < len(row):
        isrc = (row[template.isrc_index] or "").strip()
        if isrc:
            return f"isrc:{isrc}"
    title = ""
    if template.title_index < len(row):
        title = (row[template.title_index] or "").strip().lower()
    if title:
        return f"title:{re.sub(r'[^a-z0-9]+', '-', title).strip('-')}"
    return "unknown"


def is_data_row(row: list[str], template: PDFTemplate) -> bool:
    if not row:
        return False
    if template.amount_index >= len(row):
        return False
    amount_cell = (row[template.amount_index] or "").strip()
    if not amount_cell:
        return False
    title_cell = (row[template.title_index] or "").strip() if template.title_index < len(row) else ""
    if not title_cell:
        return False
    if title_cell.lower() in {"total", "totals", "subtotal", "grand total"}:
        return False
    parsed, _ = parse_amount(amount_cell)
    return parsed is not None


def extract_rows(
    pdf_path: Path,
    rel_path: str,
    template: PDFTemplate | None,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    rows: list[dict[str, str]] = []
    with pdfplumber.open(pdf_path) as pdf:
        first_table = next(
            (
                table
                for page in pdf.pages
                for table in (page.extract_tables() or [])
                if table
            ),
            None,
        )
        if first_table is None:
            return rows, {"reason": "no_tables_found"}

        if template is None:
            template = detect_template(rel_path, first_table[0])
        if template is None:
            return rows, {
                "reason": "no_template_matched",
                "headers_seen": _normalize_header(first_table[0]),
            }

        ledger_index = 1
        filename = pdf_path.name
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                # Skip header row(s) — assume first row is header.
                for raw in table[1:]:
                    row = [(cell or "").strip() for cell in raw]
                    if not is_data_row(row, template):
                        continue
                    period_start, period_end = determine_period(template, filename, row)
                    amount_value, detected_currency = parse_amount(
                        row[template.amount_index] if template.amount_index < len(row) else ""
                    )
                    gross_value = None
                    if template.gross_index is not None and template.gross_index < len(row):
                        gross_value, _ = parse_amount(row[template.gross_index])
                    share_value = ""
                    if template.share_index is not None and template.share_index < len(row):
                        share_value = row[template.share_index]
                    output_row = {column: "" for column in CANONICAL_COLUMNS}
                    output_row["ledger_line_id"] = f"PDF-{ledger_index:06d}"
                    output_row["catalog_asset_id"] = asset_id_from_row(template, row)
                    output_row["source_file"] = rel_path
                    output_row["provider"] = template.provider
                    output_row["rights_type"] = template.rights_type
                    output_row["income_type"] = template.income_type
                    output_row["territory"] = template.territory
                    output_row["period_start"] = period_start
                    output_row["period_end"] = period_end
                    output_row["currency"] = detected_currency or template.default_currency
                    output_row["owner_net_amount"] = (
                        f"{amount_value:.2f}" if amount_value is not None else ""
                    )
                    if gross_value is not None:
                        output_row["gross_amount"] = f"{gross_value:.2f}"
                    output_row["participant_share"] = share_value
                    output_row["match_confidence"] = "low"
                    output_row["notes"] = "extracted from PDF, verify against source"
                    rows.append(output_row)
                    ledger_index += 1
    info = {
        "template": template.name,
        "provider": template.provider,
        "rows_extracted": len(rows),
    }
    return rows, info


def write_ledger(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to a single PDF, or a directory to walk.")
    parser.add_argument("--output", required=True, help="Output ledger CSV path.")
    parser.add_argument(
        "--workspace-root",
        default=None,
        help="Workspace root used to compute relative source_file paths.",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Force a specific template name (skip auto-detection).",
    )
    args = parser.parse_args()

    forced_template = None
    if args.provider:
        forced_template = next((t for t in TEMPLATES if t.name == args.provider), None)
        if forced_template is None:
            raise SystemExit(
                f"Unknown template '{args.provider}'. Known: {', '.join(t.name for t in TEMPLATES)}"
            )

    input_path = Path(args.input)
    if input_path.is_dir():
        pdfs = sorted(input_path.rglob("*.pdf"))
    elif input_path.is_file() and input_path.suffix.lower() == ".pdf":
        pdfs = [input_path]
    else:
        raise SystemExit(f"Input is not a PDF or directory: {input_path}")

    workspace_root = Path(args.workspace_root) if args.workspace_root else None

    all_rows: list[dict[str, str]] = []
    per_file: list[dict[str, object]] = []
    for pdf in pdfs:
        if workspace_root is not None:
            try:
                rel = str(pdf.relative_to(workspace_root))
            except ValueError:
                rel = str(pdf)
        else:
            rel = str(pdf)
        try:
            rows, info = extract_rows(pdf, rel, forced_template)
        except Exception as exc:  # pragma: no cover - defensive
            per_file.append({"path": rel, "status": "error", "error": str(exc)})
            continue
        if not rows:
            per_file.append({"path": rel, "status": "no_rows", **info})
            continue
        # Re-key ledger_line_id across the whole batch so the output file has
        # globally unique row identifiers.
        for row in rows:
            row["ledger_line_id"] = f"PDF-{len(all_rows) + 1:06d}"
            all_rows.append(row)
        per_file.append(
            {
                "path": rel,
                "status": "ok",
                "template": info.get("template"),
                "provider": info.get("provider"),
                "rows": len(rows),
            }
        )

    output_path = Path(args.output)
    write_ledger(all_rows, output_path)

    summary = {
        "status": "ok",
        "input": str(input_path),
        "output": str(output_path),
        "pdfs_scanned": len(pdfs),
        "pdfs_extracted": sum(1 for entry in per_file if entry.get("status") == "ok"),
        "rows_total": len(all_rows),
        "per_file": per_file,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
