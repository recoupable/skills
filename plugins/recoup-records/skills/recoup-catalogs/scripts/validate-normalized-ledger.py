#!/usr/bin/env python3
"""Validate required columns in a normalized royalty ledger CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = {
    "ledger_line_id",
    "catalog_asset_id",
    "source_file",
    "provider",
    "period_start",
    "period_end",
    "rights_type",
    "income_type",
    "gross_amount",
    "owner_net_amount",
    "currency",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger_csv", help="Path to royalty-ledger.csv")
    args = parser.parse_args()

    path = Path(args.ledger_csv)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - fieldnames)
        rows = list(reader)

    errors: list[str] = []
    if missing:
        errors.append(f"missing required columns: {', '.join(missing)}")

    duplicate_ids: set[str] = set()
    seen_ids: set[str] = set()
    empty_id_rows: list[int] = []
    has_id_column = "ledger_line_id" in fieldnames
    # Only inspect ids when the column exists; otherwise the missing-column
    # error above already covers it and empty strings would leak into the
    # dedup sets, producing a confusing "duplicate empty id" error.
    if has_id_column:
        # enumerate from 2: row 1 is the header, so data row N sits on file line N+1
        for line_no, row in enumerate(rows, start=2):
            line_id = (row.get("ledger_line_id") or "").strip()
            if not line_id:
                empty_id_rows.append(line_no)
                continue
            if line_id in seen_ids:
                duplicate_ids.add(line_id)
            seen_ids.add(line_id)

    if empty_id_rows:
        errors.append(
            f"{len(empty_id_rows)} row(s) have an empty ledger_line_id (lines: "
            + ", ".join(str(n) for n in empty_id_rows)
            + ")"
        )
    if duplicate_ids:
        errors.append(f"duplicate ledger_line_id values: {', '.join(sorted(duplicate_ids))}")

    status = "ok" if not errors else "errors_found"
    print(json.dumps({"status": status, "rows": len(rows), "errors": errors}, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
