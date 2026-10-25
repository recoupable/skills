#!/usr/bin/env python3
"""Normalize first-pass provider CSV/TSV exports into royalty-ledger.csv.

Preserves exact decimal values, streams source rows, and retains held/control rows
in source receipts. status=ok means accepted detail rows; source controls remain
explicitly unavailable until supplied. No provider label establishes cash receipt.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import re
import sys
import hashlib
import sqlite3
import tempfile
import os
import uuid
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, getcontext
getcontext().prec = 128
from _finance import amount as exact_amount
from datetime import date
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


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
    "source_version_id", "source_sheet", "source_row", "source_record_id",
    "parser_version", "transform_id", "row_status", "held_reasons",
    "reported_period", "report_date", "statement_id", "raw_values",
]


CRITICAL_FIELDS = ("gross_amount", "owner_net_amount", "period_start")
PARTIAL_THRESHOLD = 0.5
NUMERIC_FIELDS = {"gross_amount", "deductions", "owner_net_amount"}


# Per-provider source-column aliases for the financially critical canonical
# fields. Used to compute "expected columns not found" warnings when coverage
# is partial. Compared case-insensitively against input headers.
FINANCIAL_ALIASES: dict[str, dict[str, list[str]]] = {
    "ascap": {
        "gross_amount": ["Gross Amount", "Gross"],
        "owner_net_amount": ["Publisher Share", "Net"],
        "period_start": ["Performance Start", "Period Start"],
        "period_end": ["Performance End", "Period End"],
        "platform_or_licensee": ["Licensee", "Station", "Network", "Series / Film Title"],
    },
    "bmi": {
        "gross_amount": ["Gross Amount"],
        "owner_net_amount": ["Publisher Net", "Net"],
        "period_start": ["Period Start", "Statement Qtr"],
        "period_end": ["Period End", "Statement Qtr"],
        "platform_or_licensee": ["Station", "Licensee", "Network"],
    },
    "mlc": {
        "gross_amount": ["Mechanical Gross", "Gross"],
        "owner_net_amount": ["Publisher Net", "Net", "Net Payable"],
        "period_start": ["Period Start", "Usage Period", "Period"],
        "period_end": ["Period End", "Usage Period", "Period"],
        "platform_or_licensee": ["DSP", "Platform", "Source"],
    },
    "distributor": {
        "gross_amount": ["Gross", "Gross Amount"],
        "owner_net_amount": ["Net", "Net Amount", "Net Payable"],
        "period_start": ["Period Start", "Sales Month", "Period"],
        "period_end": ["Period End", "Sales Month", "Period"],
        "platform_or_licensee": ["Store", "DSP", "Platform", "Source"],
    },
    "publisher-admin": {
        "gross_amount": ["Gross", "Gross Amount"],
        "owner_net_amount": ["Net", "Net Amount", "Net Payable"],
        "period_start": ["Period Start", "Sales Month", "Period"],
        "period_end": ["Period End", "Sales Month", "Period"],
        "platform_or_licensee": ["Store", "DSP", "Platform", "Source"],
    },
    "soundexchange": {
        "gross_amount": ["Gross", "Gross Amount"],
        "owner_net_amount": ["Net", "Net Amount", "Net Payable"],
        "period_start": ["Period Start", "Sales Month", "Period"],
        "period_end": ["Period End", "Sales Month", "Period"],
        "platform_or_licensee": ["Store", "DSP", "Platform", "Source"],
    },
    "direct-sync": {
        "gross_amount": ["Gross", "Gross Amount"],
        "owner_net_amount": ["Net", "Net Amount", "Net Payable"],
        "period_start": ["Period Start", "Sales Month", "Period"],
        "period_end": ["Period End", "Sales Month", "Period"],
        "platform_or_licensee": ["Store", "DSP", "Platform", "Source"],
    },
    "youtube-content-id": {
        "gross_amount": ["Gross Revenue", "Gross", "youtube_revenue_split"],
        "owner_net_amount": ["Net Revenue", "Net", "partner_revenue_usd"],
        "period_start": ["Reporting Month", "Month", "date"],
        "period_end": ["Reporting Month", "Month", "date"],
        "platform_or_licensee": [],
    },
    "curve": {
        "gross_amount": ["Gross"],
        "owner_net_amount": ["Net Payable", "Net"],
        "period_start": ["Period Start"],
        "period_end": ["Period End"],
        "platform_or_licensee": ["Royalty Source", "Source"],
    },
}


def clean_amount(value: str | None) -> str:
    """Preserve supplied precision. Currency symbols do not establish currency."""
    if value is None or not str(value).strip():
        return ""
    raw = str(value).strip()
    negative = raw.startswith("(") and raw.endswith(")")
    raw = raw.strip("()").strip()
    raw = raw.lstrip("$€£¥").strip()
    if not re.fullmatch(r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|[+-]?\.\d+", raw):
        return ""
    try:
        amount = exact_amount(raw.replace(",", ""))
    except (InvalidOperation, ValueError):
        return ""
    return format(-amount if negative else amount, "f")


def parse_month(value: str | None) -> tuple[str, str]:
    if not value:
        return "", ""
    text = value.strip()
    match = re.fullmatch(r"(\d{4})-(\d{2})", text)
    if not match:
        return text, text
    year = int(match.group(1))
    month = int(match.group(2))
    if not 1 <= month <= 12:
        return "", ""
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def parse_quarter(value: str | None) -> tuple[str, str]:
    if not value:
        return "", ""
    text = value.strip()
    match = re.fullmatch(r"(\d{4})Q([1-4])", text)
    if not match:
        return "", ""
    year = int(match.group(1))
    quarter = int(match.group(2))
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    last_day = calendar.monthrange(year, end_month)[1]
    return f"{year:04d}-{start_month:02d}-01", f"{year:04d}-{end_month:02d}-{last_day:02d}"


def parse_yyyymmdd(value: str | None) -> str:
    if not value:
        return ""
    text = value.strip()
    match = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", text)
    if not match:
        return text
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"


def first(row: dict[str, str], *names: str) -> str:
    lower_lookup = {key.lower(): value for key, value in row.items() if isinstance(key, str)}
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return value.strip()
        value = lower_lookup.get(name.lower())
        if value not in (None, ""):
            return value.strip()
    return ""


def has_meaningful_value(row: dict[str, str]) -> bool:
    # A song title can start with "Totals" or "Note:". Classification is explicit.
    return any(str(value).strip() for key, value in row.items() if isinstance(key, str) and value)


def asset_id(prefix: str, value: str, fallback: str) -> str:
    if value:
        return f"{prefix}:{value}"
    return f"title:{fallback.strip().lower().replace(' ', '-')}" if fallback else "unknown"


def blank_row(index: int, source_file: str) -> dict[str, str]:
    row = {column: "" for column in CANONICAL_COLUMNS}
    row["ledger_line_id"] = f"RL-{index:06d}"
    row["source_file"] = source_file
    row["match_confidence"] = "medium"
    return row


@dataclass(frozen=True)
class ProviderProfile:
    provider_name: str
    rights_type: str
    income_type: str
    normalize: Callable[[dict[str, str], int, str], dict[str, str]]


def normalize_ascap(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    output = blank_row(index, source_file)
    title = first(row, "Work Title", "Title")
    gross = clean_amount(first(row, "Gross Amount", "Gross"))
    net = clean_amount(first(row, "Publisher Share", "Net"))
    output.update(
        {
            "provider": "ASCAP",
            "rights_type": "publishing",
            "income_type": "performance",
            "catalog_asset_id": asset_id("iswc", first(row, "ISWC"), title),
            "period_start": first(row, "Performance Start", "Period Start"),
            "period_end": first(row, "Performance End", "Period End"),
            "payment_date": first(row, "Distribution Date", "Payment Date"),
            "territory": first(row, "Territory"),
            "platform_or_licensee": first(row, "Licensee", "Station", "Network", "Series / Film Title"),
            "gross_amount": gross,
            "deductions": clean_amount(first(row, "Deductions", "Fees")),
            "participant_share": first(row, "Share %"),
            "owner_net_amount": net,
            "currency": first(row, "Currency"),
            "pro_use_type": first(row, "Use Type", "Perf. Type"),
            "pro_credits": first(row, "Credits", "Total Credits", "Premium Credits"),
            "pro_bonus_type": first(row, "Bonus Type", "Premium Type"),
            "cue_sheet_ref": first(row, "Cue Sheet", "Program"),
            "notes": f"work_id={first(row, 'Work ID')}" if first(row, "Work ID") else "",
        }
    )
    return output


def normalize_bmi(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    output = blank_row(index, source_file)
    title = first(row, "Title", "Work Title")
    quarter_start, quarter_end = parse_quarter(first(row, "Statement Qtr"))
    hit_song_bonus = clean_amount(first(row, "Hit Song Bonus"))
    bonus_type = first(row, "Bonus Category", "Bonus Type") or ("Hit Song Bonus" if hit_song_bonus not in ("", "0.00") else "")
    net = clean_amount(first(row, "Publisher Net", "Net"))
    output.update(
        {
            "provider": "BMI",
            "rights_type": "publishing",
            "income_type": "performance",
            "catalog_asset_id": asset_id("iswc", first(row, "ISWC"), title),
            "period_start": first(row, "Period Start") or quarter_start,
            "period_end": first(row, "Period End") or quarter_end,
            "payment_date": first(row, "Payment Date"),
            "territory": first(row, "Territory"),
            "platform_or_licensee": first(row, "Station", "Licensee", "Network"),
            "gross_amount": clean_amount(first(row, "Gross Amount")),
            "deductions": clean_amount(first(row, "Admin Fee", "Deductions")),
            "owner_net_amount": net,
            "currency": first(row, "Currency"),
            "pro_use_type": first(row, "Performance Type", "Use Type"),
            "pro_bonus_type": bonus_type,
            "notes": f"bmi_work_id={first(row, 'BMI Work #')}" if first(row, "BMI Work #") else "",
        }
    )
    return output


def normalize_distributor(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    output = blank_row(index, source_file)
    title = first(row, "Track Title", "Title")
    period_start, period_end = parse_month(first(row, "Sales Month", "Period"))
    rights_type = first(row, "Rights Type").lower() or "master"
    income_type = first(row, "Income Type").lower() or "streaming"
    output.update(
        {
            "provider": "Distributor",
            "rights_type": rights_type,
            "income_type": income_type,
            "catalog_asset_id": asset_id("isrc", first(row, "ISRC"), title),
            "period_start": first(row, "Period Start") or period_start,
            "period_end": first(row, "Period End") or period_end,
            "payment_date": first(row, "Payment Date"),
            "territory": first(row, "Territory", "Country"),
            "platform_or_licensee": first(row, "Store", "DSP", "Platform", "Source"),
            "gross_amount": clean_amount(first(row, "Gross", "Gross Amount")),
            "deductions": clean_amount(first(row, "Fee", "Deductions")),
            "owner_net_amount": clean_amount(first(row, "Net", "Net Amount", "Net Payable")),
            "currency": first(row, "Currency"),
            "fx_rate": first(row, "FX", "FX Rate"),
            "notes": first(row, "Notes"),
        }
    )
    return output


def normalize_common_statement(
    row: dict[str, str],
    index: int,
    source_file: str,
    provider: str,
    rights_type: str,
    income_type: str,
) -> dict[str, str]:
    output = normalize_distributor(row, index, source_file)
    output.update(
        {
            "provider": provider,
            "rights_type": rights_type,
            "income_type": income_type,
        }
    )
    return output


def normalize_publisher_admin(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    return normalize_common_statement(row, index, source_file, "Publisher Admin", "publishing", "mechanical")


def normalize_soundexchange(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    return normalize_common_statement(row, index, source_file, "SoundExchange", "neighboring", "radio")


def normalize_direct_sync(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    return normalize_common_statement(row, index, source_file, "Direct Sync", "sync", "sync")


def normalize_youtube(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    output = blank_row(index, source_file)
    title = first(row, "Asset Title", "Track Title", "Title")
    report_date = parse_yyyymmdd(first(row, "date"))
    period_start, period_end = parse_month(first(row, "Reporting Month", "Month"))
    output.update(
        {
            "provider": "YouTube Content ID",
            "rights_type": "master",
            "income_type": "ugc",
            "catalog_asset_id": first(row, "custom_id") or asset_id("isrc", first(row, "ISRC", "isrc"), title),
            "period_start": period_start or report_date,
            "period_end": period_end or report_date,
            "territory": first(row, "Country", "Territory", "country_code"),
            "platform_or_licensee": "YouTube",
            "gross_amount": clean_amount(first(row, "Gross Revenue", "Gross", "youtube_revenue_split")),
            "owner_net_amount": clean_amount(first(row, "Net Revenue", "Net", "partner_revenue_usd")),
            "currency": first(row, "Currency", "currency_code"),
            "notes": f"content_type={first(row, 'Content Type')}" if first(row, "Content Type") else f"asset_id={first(row, 'asset_id')}" if first(row, "asset_id") else "",
        }
    )
    return output


def normalize_mlc(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    output = blank_row(index, source_file)
    title = first(row, "Song Title", "Work Title", "Title")
    period_start, period_end = parse_month(first(row, "Usage Period", "Period"))
    output.update(
        {
            "provider": "The MLC",
            "rights_type": "publishing",
            "income_type": "mechanical",
            "catalog_asset_id": asset_id("iswc", first(row, "ISWC"), title),
            "period_start": first(row, "Period Start") or period_start,
            "period_end": first(row, "Period End") or period_end,
            "payment_date": first(row, "Payment Date"),
            "territory": first(row, "Territory") or "US",
            "platform_or_licensee": first(row, "DSP", "Platform", "Source"),
            "gross_amount": clean_amount(first(row, "Mechanical Gross", "Gross")),
            "deductions": clean_amount(first(row, "Admin Fee", "Deductions")),
            "owner_net_amount": clean_amount(first(row, "Publisher Net", "Net", "Net Payable")),
            "currency": first(row, "Currency"),
            "fx_rate": first(row, "FX", "FX Rate"),
            "notes": first(row, "Notes"),
        }
    )
    return output


def normalize_curve(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    output = blank_row(index, source_file)
    title = first(row, "Track Title", "Work Title", "Title")
    rights_type = first(row, "Rights Type").lower() or "unknown"
    output.update(
        {
            "provider": "Curve",
            "rights_type": rights_type,
            "income_type": first(row, "Income Type").lower() or "unknown",
            "catalog_asset_id": first(row, "Source Work ID") or asset_id("isrc", first(row, "ISRC"), title),
            "period_start": first(row, "Period Start"),
            "period_end": first(row, "Period End"),
            "territory": first(row, "Territory"),
            "platform_or_licensee": first(row, "Royalty Source", "Source"),
            "gross_amount": clean_amount(first(row, "Gross")),
            "deductions": clean_amount(first(row, "Deductions")),
            "owner_net_amount": clean_amount(first(row, "Net Payable", "Net")),
            "currency": first(row, "Currency"),
        }
    )
    return output


def _filename_year_period(source_file: str) -> tuple[str, str]:
    match = re.search(r"(?<!\d)(20\d{2}|19\d{2})(?!\d)", source_file)
    if not match:
        return "", ""
    year = match.group(1)
    return f"{year}-01-01", f"{year}-12-31"


def normalize_bmi_annual(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    """BMI annual consolidated XLSX. Sums Domestic Perf + Domestic Mech +
    International + Other into owner_net_amount and preserves the breakdown
    in `notes`. period_start/end is derived from the source filename year.
    """
    output = blank_row(index, source_file)
    title = first(row, "Title", "Work Title")
    work_id = first(row, "BMI Work #", "BMI Work#", "Work ID", "BMI Work")
    components = {
        "domestic_perf": _to_float(first(row, "Domestic Perf", "Domestic Performance")),
        "domestic_mech": _to_float(first(row, "Domestic Mech", "Domestic Mechanical")),
        "international": _to_float(first(row, "International (all CMOs)", "International")),
        "other": _to_float(first(row, "Other Income", "Other")),
    }
    total_value = _to_float(first(row, "Total"))
    if total_value is None:
        total_value = sum(v for v in components.values() if v is not None) if any(v is not None for v in components.values()) else None
    components_note = ", ".join(
        f"{key}={value}" for key, value in components.items() if value is not None
    )
    period_start, period_end = _filename_year_period(source_file)
    output.update(
        {
            "provider": "BMI",
            "rights_type": "publishing",
            "income_type": "performance",
            "catalog_asset_id": (f"bmi:{work_id}" if work_id else asset_id("title", "", title)),
            "period_start": period_start,
            "period_end": period_end,
            "platform_or_licensee": "BMI consolidated",
            "owner_net_amount": format(total_value, "f") if total_value is not None else "",
            "currency": "USD",
            "notes": components_note + (f"; bmi_work_id={work_id}" if work_id else ""),
        }
    )
    return output


def normalize_gema(row: dict[str, str], index: int, source_file: str) -> dict[str, str]:
    """GEMA German sub-publisher XLSX. Header layout typically:
    Title, ISWC, Distribution (EUR), Mechanical (EUR), Performance (EUR), Total (EUR).
    """
    output = blank_row(index, source_file)
    title = first(row, "Title", "Titel", "Work Title")
    iswc = first(row, "ISWC")
    total = clean_amount(first(row, "Total (EUR)", "Total", "Distribution (EUR)", "Distribution"))
    mechanical = clean_amount(first(row, "Mechanical (EUR)", "Mechanical"))
    performance = clean_amount(first(row, "Performance (EUR)", "Performance"))
    note_parts: list[str] = []
    if mechanical:
        note_parts.append(f"mechanical={mechanical}")
    if performance:
        note_parts.append(f"performance={performance}")
    period_start, period_end = _filename_year_period(source_file)
    output.update(
        {
            "provider": "GEMA",
            "rights_type": "publishing",
            "income_type": "performance",
            "catalog_asset_id": asset_id("iswc", iswc, title),
            "period_start": period_start,
            "period_end": period_end,
            "territory": "DE",
            "platform_or_licensee": "GEMA",
            "owner_net_amount": total,
            "currency": "EUR",
            "notes": "; ".join(note_parts),
        }
    )
    return output


def _to_float(value: str | None) -> Decimal | None:
    # Historical function name kept for profile compatibility; never binary float.
    text = clean_amount(value)
    return Decimal(text) if text else None


PROFILES: dict[str, ProviderProfile] = {
    "ascap": ProviderProfile("ASCAP", "publishing", "performance", normalize_ascap),
    "bmi": ProviderProfile("BMI", "publishing", "performance", normalize_bmi),
    "bmi-annual": ProviderProfile("BMI Annual", "publishing", "performance", normalize_bmi_annual),
    "gema": ProviderProfile("GEMA", "publishing", "performance", normalize_gema),
    "distributor": ProviderProfile("Distributor", "master", "streaming", normalize_distributor),
    "publisher-admin": ProviderProfile("Publisher Admin", "publishing", "mechanical", normalize_publisher_admin),
    "soundexchange": ProviderProfile("SoundExchange", "neighboring", "radio", normalize_soundexchange),
    "direct-sync": ProviderProfile("Direct Sync", "sync", "sync", normalize_direct_sync),
    "youtube-content-id": ProviderProfile("YouTube Content ID", "master", "ugc", normalize_youtube),
    "mlc": ProviderProfile("The MLC", "publishing", "mechanical", normalize_mlc),
    "curve": ProviderProfile("Curve", "unknown", "unknown", normalize_curve),
}


def count_existing_ledger_rows(output_path: Path) -> int:
    """Count data rows (excluding the header) already in an output ledger.

    Used by --append so ledger_line_id keeps incrementing across providers
    instead of every per-provider call restarting at RL-000001 and colliding.
    Uses csv.reader so quoted multi-line fields are counted correctly.
    """
    if not output_path.exists():
        return 0
    with output_path.open("r", newline="", encoding="utf-8") as handle:
        row_count = sum(1 for _ in csv.reader(handle))
    return max(0, row_count - 1)


def detect_delimiter(text_sample: str, requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        dialect = csv.Sniffer().sniff(text_sample, delimiters=",\t|;")
        return dialect.delimiter
    except csv.Error:
        return ","


@contextmanager
def read_rows(input_path: Path, delimiter: str, sheet: str | None = None):
    """Yield headers, row iterator and selected sheet; memory independent of CSV size."""
    if input_path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
        if input_path.suffix.lower() == ".xls":
            raise ValueError("Legacy XLS must be exported to XLSX/CSV before parsing")
        try:
            import openpyxl
        except ImportError as exc:
            raise SystemExit("XLSX needs openpyxl — pip3 install openpyxl") from exc
        workbook = openpyxl.load_workbook(input_path, data_only=True, read_only=True)
        try:
            if sheet and sheet not in workbook.sheetnames:
                raise ValueError(f"Requested worksheet {sheet!r} not found; available: {workbook.sheetnames}")
            worksheet = workbook[sheet] if sheet else workbook.active
            iterator = worksheet.iter_rows(values_only=True)
            headers = [_to_str_cell(c) for c in next(iterator, ())]
            if not headers or any(not h for h in headers):
                raise ValueError("Worksheet row 1 must contain explicit nonblank headers; export the table first")
            def body():
                for number, cells in enumerate(iterator, 2):
                    yield number, {key: _to_str_cell(cells[i]) if i < len(cells) else "" for i, key in enumerate(headers)}
            yield headers, body(), worksheet.title
        finally:
            workbook.close()
    else:
        if sheet:
            raise ValueError("--sheet applies only to XLSX inputs")
        with input_path.open(newline="", encoding="utf-8-sig") as handle:
            sample = handle.read(8192)
            handle.seek(0)
            reader = csv.DictReader(handle, delimiter=detect_delimiter(sample, delimiter))
            headers = list(reader.fieldnames or [])
            def body():
                for row in reader:
                    yield reader.line_num, row
            yield headers, body(), ""


def _to_str_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _detect_header_row(rows: list[tuple]) -> int | None:
    """Find the first row that looks like column headers: ≥4 non-null string
    cells with no leading currency symbol. This skips preface metadata rows
    (e.g. "BMI Royalty Distribution — Consolidated Annual View 2022")."""
    for idx, row in enumerate(rows):
        if not row:
            continue
        non_null = [c for c in row if c is not None and str(c).strip()]
        if len(non_null) < 3:
            continue
        if not all(isinstance(c, str) for c in non_null):
            continue
        if any(str(c).strip().startswith(("$", "€", "£", "¥")) for c in non_null):
            continue
        # Title-rows usually contain only one cell + Nones; require fill on multiple columns.
        return idx
    return None


def load_column_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"--column-map must be a JSON object: {path}")
    valid: dict[str, str] = {}
    for source, canonical in data.items():
        if not isinstance(source, str) or not isinstance(canonical, str):
            continue
        if canonical not in CANONICAL_COLUMNS:
            raise SystemExit(
                f"--column-map target '{canonical}' is not a canonical ledger column. "
                f"Valid targets: {', '.join(sorted(CANONICAL_COLUMNS))}"
            )
        valid[source] = canonical
    return valid


def apply_column_map(input_row: dict[str, str], output_row: dict[str, str], column_map: dict[str, str]) -> None:
    """Explicit mapping is authoritative, including an explicitly empty value."""
    for source_col, canonical_field in column_map.items():
        source_value = first(input_row, source_col)
        if canonical_field in NUMERIC_FIELDS:
            output_row[canonical_field] = clean_amount(source_value)
        else:
            output_row[canonical_field] = source_value


def compute_population_rate(rows: list[dict[str, str]]) -> float:
    if not rows:
        return 0.0
    total = len(rows) * len(CRITICAL_FIELDS)
    filled = sum(
        1
        for row in rows
        for field in CRITICAL_FIELDS
        if (row.get(field) or "").strip()
    )
    return filled / total if total else 0.0


def expected_columns_not_found(provider: str, headers: list[str]) -> list[str]:
    aliases = FINANCIAL_ALIASES.get(provider, {})
    expected: set[str] = set()
    for field in CRITICAL_FIELDS + ("period_end", "platform_or_licensee"):
        for alias in aliases.get(field, []):
            expected.add(alias)
    if not expected:
        return []
    headers_lower = {h.lower() for h in headers if isinstance(h, str)}
    missing = [name for name in sorted(expected) if name.lower() not in headers_lower]
    return missing


PARSER_VERSION = "royalty-normalizer/2"
REQUIRED_VALUES = ("owner_net_amount", "currency", "period_start", "period_end", "rights_type", "income_type")
ROW_CLASSES = {"detail", "control", "footer", "ignored", "held"}


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_detail(output):
    reasons = [f"missing:{field}" for field in REQUIRED_VALUES if not output.get(field) or output[field] == "unknown"]
    if output.get("currency") and not re.fullmatch(r"[A-Z]{3}", output["currency"]):
        reasons.append("invalid:currency")
    for field in ("period_start", "period_end", "payment_date", "report_date"):
        if output.get(field):
            try:
                date.fromisoformat(output[field])
            except ValueError:
                reasons.append(f"invalid:{field}")
    if output.get("period_start") and output.get("period_end") and output["period_start"] > output["period_end"]:
        reasons.append("invalid:period_order")
    return reasons


def validate_source_controls(controls, totals):
    """Compare explicit supported controls without manufacturing unobserved zeros."""
    errors = []
    if not isinstance(controls, dict):
        return ["Source controls must be an object"]
    evidence_refs = controls.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs or not all(
        isinstance(ref, str) and ref.strip() for ref in evidence_refs
    ):
        errors.append("Source controls require nonempty string evidence_refs")
    control_totals = controls.get("totals")
    if not isinstance(control_totals, list) or not control_totals:
        errors.append("Source controls need at least one explicit total in a list")
        return errors
    for index, control in enumerate(control_totals, 1):
        label = f"Source control {index}"
        if not isinstance(control, dict):
            errors.append(f"{label} must be an object")
            continue
        currency, field = control.get("currency"), control.get("field")
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            errors.append(f"{label} requires an explicit uppercase three-letter currency")
            continue
        if not isinstance(field, str) or field not in NUMERIC_FIELDS:
            errors.append(f"{label} field must be one of {', '.join(sorted(NUMERIC_FIELDS))}")
            continue
        try:
            expected = exact_amount(control.get("amount"), f"{label} amount")
        except ValueError as error:
            errors.append(str(error))
            continue
        # A present key can legitimately total zero; an absent key is missing evidence.
        if (currency, field) not in totals:
            errors.append(f"{label} has no observed source amount for {currency}/{field}")
            continue
        observed = totals[(currency, field)]
        if observed != expected:
            errors.append(f"Source control mismatch {currency}/{field}: observed={observed}, expected={expected}")
    return errors


def normalize(provider, input_path, output_path, delimiter="auto", column_map_path=None,
              sheet=None, append=False, controls_path=None, statement_id=None):
    profile = PROFILES.get(provider)
    if profile is None:
        raise ValueError(f"Unsupported provider {provider!r}")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Source is immutable: output must differ from input")
    column_map = load_column_map(column_map_path)
    forbidden = {"ledger_line_id", "source_file", "source_version_id", "source_row", "source_sheet", "source_record_id", "transform_id", "parser_version", "raw_values", "row_status", "held_reasons"}
    if forbidden.intersection(column_map.values()):
        raise ValueError("Column maps cannot overwrite parser provenance or status")
    source_hash = sha256_file(input_path)
    transform_id = hashlib.sha256(json.dumps([PARSER_VERSION, provider, column_map, delimiter, sheet, statement_id], sort_keys=True).encode()).hexdigest()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    receipts_dir = Path(str(output_path) + ".receipts")
    receipts_dir.mkdir(exist_ok=True)
    receipt_base = receipts_dir / f"{source_hash}-{transform_id[:12]}-{uuid.uuid4().hex[:12]}"
    receipt_path = Path(str(receipt_base) + ".json")
    rows_path = Path(str(receipt_base) + ".rows.jsonl")
    counts = Counter()
    totals = defaultdict(Decimal)
    written_totals = defaultdict(Decimal)
    existing_count = 0
    required_count = 0
    appending = append and output_path.exists()
    controls = json.loads(controls_path.read_text(), parse_float=str) if controls_path else None
    control_errors = []
    # SQLite indexes import IDs on disk. We never load a multi-million-row ledger into RAM.
    with tempfile.TemporaryDirectory(prefix="royalty-import-", dir=output_path.parent) as temporary:
        temporary = Path(temporary)
        db = sqlite3.connect(temporary / "identities.sqlite")
        db.execute("CREATE TABLE identities (id TEXT PRIMARY KEY, transform TEXT, status TEXT)")
        db.execute("CREATE TABLE transactions (id TEXT PRIMARY KEY, economic TEXT)")
        staged = temporary / "ledger.csv"
        rowlog = temporary / "rows.jsonl"
        with staged.open("w", newline="", encoding="utf-8") as handle, rowlog.open("w", encoding="utf-8") as log:
            writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
            writer.writeheader()
            if appending:
                with output_path.open(newline="", encoding="utf-8") as old:
                    reader = csv.DictReader(old)
                    if reader.fieldnames != CANONICAL_COLUMNS:
                        raise ValueError("Existing ledger schema differs; rebuild from immutable sources before append")
                    for row in reader:
                        writer.writerow(row)
                        db.execute("INSERT OR IGNORE INTO identities VALUES (?, ?, ?)", (row["ledger_line_id"], row["transform_id"], row["row_status"]))
                        if row.get("source_record_id"):
                            db.execute("INSERT OR IGNORE INTO transactions VALUES (?, ?)", (row["source_record_id"], economic_key(row)))
                        existing_count += 1
            with read_rows(input_path, delimiter, sheet) as (headers, rows, selected_sheet):
                if not headers or any(not h for h in headers) or len(set(h.lower() for h in headers)) != len(headers):
                    raise ValueError("Missing, blank or duplicate source headers")
                absent = set(column_map) - set(headers)
                if absent:
                    raise ValueError(f"Mapped source columns absent: {sorted(absent)}")
                for source_row, raw in rows:
                    counts["source_rows"] += 1
                    row_class = first(raw, "Row Type", "row_class").lower() or ("detail" if has_meaningful_value(raw) else "ignored")
                    malformed = None in raw or any(isinstance(v, list) for v in raw.values())
                    safe_raw = {str(k): str(v) if v is not None else "" for k, v in raw.items()}
                    output = profile.normalize(safe_raw, source_row, str(input_path.resolve()))
                    # Only observed fields or explicit maps establish classification, currency and dates.
                    output.update({"rights_type": first(safe_raw, "Rights Type", "rights_type").lower(),
                                   "income_type": first(safe_raw, "Income Type", "income_type").lower(),
                                   "currency": first(safe_raw, "Currency", "currency_code").upper(),
                                   "payment_date": first(safe_raw, "Payment Date"),
                                   "report_date": first(safe_raw, "Report Date", "Distribution Date"),
                                   "reported_period": first(safe_raw, "Reporting Period", "Statement Qtr", "Reporting Month"),
                                   "statement_id": statement_id or first(safe_raw, "Statement ID")})
                    if provider in {"bmi-annual", "gema"}:
                        output["period_start"] = first(safe_raw, "Period Start")
                        output["period_end"] = first(safe_raw, "Period End")
                    if provider == "bmi" and not first(safe_raw, "Period Start"):
                        output["period_start"] = output["period_end"] = ""
                    if provider == "youtube-content-id":
                        earned_start, earned_end = parse_month(first(safe_raw, "Usage Month", "Sales Month"))
                        output["period_start"] = first(safe_raw, "Period Start") or earned_start
                        output["period_end"] = first(safe_raw, "Period End") or earned_end
                    apply_column_map(safe_raw, output, column_map)
                    output["currency"] = output["currency"].upper()
                    line_id = hashlib.sha256(f"{source_hash}:{selected_sheet}:{source_row}".encode()).hexdigest()
                    transaction = first(safe_raw, "Transaction ID", "Source Record ID")
                    account = first(safe_raw, "Account ID", "Payee ID")
                    transaction_key = f"{provider}:{account}:{output['statement_id']}:{transaction}" if transaction and account and output["statement_id"] else ""
                    output.update({"ledger_line_id": "RL-" + line_id, "source_version_id": source_hash,
                                   "source_row": str(source_row), "source_sheet": selected_sheet,
                                   "source_record_id": transaction_key, "parser_version": PARSER_VERSION,
                                   "transform_id": transform_id, "raw_values": json.dumps(raw, ensure_ascii=False)})
                    reasons = []
                    if row_class not in ROW_CLASSES:
                        reasons.append("unknown:row_class")
                        row_class = "held"
                    if malformed:
                        reasons.append("malformed:columns")
                    if row_class in {"detail", "held"}:
                        reasons += validate_detail(output)
                        for field in NUMERIC_FIELDS:
                            aliases = [source for source, target in column_map.items() if target == field]
                            if not aliases:
                                aliases = FINANCIAL_ALIASES.get(provider, {}).get(field, [])
                                if field == "deductions":
                                    aliases = ["Deductions", "Fees", "Fee", "Admin Fee"]
                            observed = first(safe_raw, *aliases)
                            if observed and not clean_amount(observed):
                                reasons.append(f"invalid:{field}")
                    if row_class == "held":
                        reasons.append("source:held")
                    if reasons:
                        row_class = "held"
                    # Totals cover every retained detail/held row, never control/footer rows.
                    if row_class in {"detail", "held"}:
                        for field in ("gross_amount", "owner_net_amount", "deductions"):
                            if output.get(field):
                                totals[(output["currency"] or "UNKNOWN", field)] += Decimal(output[field])
                    imported = db.execute("SELECT transform, status FROM identities WHERE id=?", (output["ledger_line_id"],)).fetchone()
                    if imported:
                        if imported[0] != transform_id:
                            raise ValueError("Source already imported with a different mapping; rebuild the affected ledger from sources, do not append a second interpretation")
                        counts["duplicate_rows"] += 1
                        if imported[1] == "held":
                            counts["duplicate_held_rows"] += 1
                        disposition = "duplicate"
                    else:
                        existing = db.execute("SELECT economic FROM transactions WHERE id=?", (transaction_key,)).fetchone() if transaction_key else None
                        if existing and existing[0] == economic_key(output):
                            counts["economic_duplicate_rows"] += 1
                            counts["duplicate_rows"] += 1
                            disposition = "duplicate"
                        else:
                            if existing:
                                row_class = "held"
                                reasons.append("overlap:revised_transaction_requires_resolution")
                            output["row_status"] = "ready" if row_class == "detail" else row_class
                            output["held_reasons"] = ";".join(reasons)
                            counts[row_class] += 1
                            disposition = row_class
                            if row_class in {"detail", "held"}:
                                writer.writerow(output)
                                for field in ("gross_amount", "owner_net_amount", "deductions"):
                                    if output.get(field):
                                        written_totals[(output["currency"] or "UNKNOWN", field)] += Decimal(output[field])
                                counts["written_rows"] += 1
                                required_count += sum(bool(output.get(f)) for f in CRITICAL_FIELDS)
                            db.execute("INSERT OR IGNORE INTO identities VALUES (?, ?, ?)", (output["ledger_line_id"], transform_id, output["row_status"]))
                            if transaction_key:
                                db.execute("INSERT OR IGNORE INTO transactions VALUES (?, ?)", (transaction_key, economic_key(output)))
                    log.write(json.dumps({"source_version_id": source_hash, "source_sheet": selected_sheet,
                                          "source_row": source_row, "disposition": disposition, "reasons": reasons,
                                          "ledger_line_id": output["ledger_line_id"], "raw_values": raw}, ensure_ascii=False) + "\n")
            if not counts["source_rows"]:
                control_errors.append("No data rows: header-only source")
            if controls_path is not None:
                control_errors.extend(validate_source_controls(controls, totals))
        db.close()
        os.replace(staged, output_path)
        os.replace(rowlog, rows_path)
    status = "partial" if counts["held"] or counts["economic_duplicate_rows"] or counts["duplicate_held_rows"] or control_errors or not (counts["detail"] or counts["duplicate_rows"]) else "ok"
    payload = {"status": status, "provider": profile.provider_name, "input": str(input_path.resolve()),
               "source_version_id": source_hash, "source_sheet": selected_sheet, "parser_version": PARSER_VERSION,
               "transform_id": transform_id, "output": str(output_path), "rows": counts["written_rows"],
               "appended": appending, "ledger_total_rows": existing_count + counts["written_rows"],
               "overlap_detection": "Exact source versions and explicitly scoped account/statement/transaction IDs only; unkeyed revised exports require manual overlap review.",
               "row_conservation": dict(counts), "source_totals": [{"currency": c, "field": f, "amount": format(v, "f")} for (c, f), v in sorted(totals.items())],
               "written_totals": [{"currency": c, "field": f, "amount": format(v, "f")} for (c, f), v in sorted(written_totals.items())],
               "controls_scope": "Source detail before duplicate disposition; written_totals cover only this import's newly written rows, excluding any existing appended ledger.",
               "ledger_control_status": "requires_duplicate_review" if counts["economic_duplicate_rows"] else "not_independently_controlled",
               "controls_status": "unavailable" if controls_path is None else "matched" if not control_errors else "mismatch",
               "rounding_policy": "Inputs <=24 coefficient/integer digits and <=18 fractional places; Decimal precision 128. No per-row rounding. Reporting rounding is a separate evidenced step.",
               "field_population_rate": round(required_count / (counts["written_rows"] * len(CRITICAL_FIELDS)), 4) if counts["written_rows"] else 0,
               "headers_seen": headers, "warnings": control_errors,
               "receipt": str(receipt_path), "row_receipt": str(rows_path)}
    receipt_path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def economic_key(row):
    return json.dumps([row.get(key, "") for key in ("catalog_asset_id", "currency", "period_start", "period_end", "rights_type", "income_type", "gross_amount", "owner_net_amount", "deductions")])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, help=f"One of: {', '.join(sorted(PROFILES))}")
    parser.add_argument("--input", required=True, help="Provider CSV/TSV export")
    parser.add_argument("--output", required=True, help="Output royalty-ledger.csv path")
    parser.add_argument(
        "--delimiter",
        default="auto",
        help="Field delimiter for the input file. Use 'auto' to sniff (default), or pass an explicit one ('\\t' for TSV).",
    )
    parser.add_argument(
        "--column-map",
        default=None,
        help="Optional JSON file mapping {source_column: canonical_field} for provider variants.",
    )
    parser.add_argument(
        "--sheet",
        default=None,
        help="Worksheet name for XLSX inputs (defaults to active sheet).",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help=(
            "Append rows to an existing --output ledger instead of overwriting it, "
            "continuing ledger_line_id numbering. Use this to accumulate multiple "
            "providers into one royalty-ledger.csv. Delete the ledger first to start fresh."
        ),
    )
    parser.add_argument("--controls", help="JSON source totals with evidence_refs and totals[{currency,field,amount}]")
    parser.add_argument("--statement-id", help="Observed statement identity, for source transaction overlap detection")
    args = parser.parse_args()

    delimiter = args.delimiter
    if delimiter != "auto":
        delimiter = bytes(delimiter, "utf-8").decode("unicode_escape")
    column_map_path = Path(args.column_map) if args.column_map else None

    payload = normalize(
        args.provider,
        Path(args.input),
        Path(args.output),
        delimiter=delimiter,
        column_map_path=column_map_path,
        sheet=args.sheet,
        append=args.append,
        controls_path=Path(args.controls) if args.controls else None,
        statement_id=args.statement_id,
    )
    print(json.dumps(payload, indent=2))
    if payload["status"] != "ok":
        print(
            f"normalize-royalty-statement: status={payload['status']} — see warnings above.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
