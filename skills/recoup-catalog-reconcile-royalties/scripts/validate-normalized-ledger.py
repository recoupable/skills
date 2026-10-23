#!/usr/bin/env python3
"""Validate exact-decimal ledger values, provenance and held rows with bounded memory."""
import argparse
import csv
import json
import sqlite3
import tempfile
from pathlib import Path
from _finance import amount, currency, iso_date

REQUIRED_COLUMNS = {"ledger_line_id", "catalog_asset_id", "source_file", "provider", "period_start", "period_end", "rights_type",
                    "income_type", "gross_amount", "owner_net_amount", "currency", "row_status", "source_version_id", "source_row", "transform_id"}


def validate(path):
    errors, count, held = [], 0, 0
    with tempfile.TemporaryDirectory(prefix="ledger-validate-") as directory:
        db = sqlite3.connect(Path(directory) / "ids.sqlite")
        db.execute("CREATE TABLE ids (id TEXT PRIMARY KEY)")
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                errors.append("missing required columns: " + ", ".join(sorted(missing)))
            for number, row in enumerate(reader, 2):
                count += 1
                try:
                    identity = row.get("ledger_line_id")
                    if not identity:
                        raise ValueError("empty ledger_line_id")
                    try:
                        db.execute("INSERT INTO ids VALUES (?)", (identity,))
                    except sqlite3.IntegrityError:
                        raise ValueError("duplicate ledger_line_id") from None
                    if row.get("row_status") != "ready":
                        held += 1
                        raise ValueError("row is held or has unknown status; resolve before financial aggregation")
                    for key in ("source_file", "provider", "source_version_id", "source_row", "transform_id", "rights_type", "income_type"):
                        if not row.get(key) or row[key] == "unknown":
                            raise ValueError("missing " + key)
                    amount(row.get("owner_net_amount"), "owner_net_amount")
                    if row.get("gross_amount"):
                        amount(row["gross_amount"], "gross_amount")
                    currency(row)
                    start, end = iso_date(row.get("period_start"), "period_start"), iso_date(row.get("period_end"), "period_end")
                    if start > end:
                        raise ValueError("period_start exceeds period_end")
                except ValueError as exc:
                    if len(errors) < 100:
                        errors.append(f"row {number}: {exc}")
        db.close()
    if not count:
        errors.append("ledger contains no data rows")
    return {"status": "errors_found" if errors else "ok", "rows": count, "held_rows": held, "errors": errors,
            "error_sample_limit": 100}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger_csv")
    args = parser.parse_args()
    result = validate(Path(args.ledger_csv))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
