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
    for row in rows:
        line_id = row.get("ledger_line_id", "")
        if line_id in seen_ids:
            duplicate_ids.add(line_id)
        if line_id:
            seen_ids.add(line_id)

    if duplicate_ids:
        errors.append(f"duplicate ledger_line_id values: {', '.join(sorted(duplicate_ids))}")

    status = "ok" if not errors else "errors_found"
    print(json.dumps({"status": status, "rows": len(rows), "errors": errors}, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
