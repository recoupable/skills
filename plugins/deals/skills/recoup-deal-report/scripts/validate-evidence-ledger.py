#!/usr/bin/env python3
"""Validate evidence-ledger.json shape for a catalog deal workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_ENTRY_FIELDS = {
    "evidence_id",
    "source_file",
    "source_type",
    "locator",
    "extracted_field",
    "extracted_value",
    "confidence",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="Path to evidence-ledger.json")
    args = parser.parse_args()

    path = Path(args.ledger)
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries")
    errors: list[str] = []
    if not isinstance(entries, list):
        errors.append("`entries` must be a list")
        entries = []

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entries[{index}] must be an object")
            continue
        missing = sorted(REQUIRED_ENTRY_FIELDS - set(entry))
        if missing:
            errors.append(f"entries[{index}] missing fields: {', '.join(missing)}")
        evidence_id = entry.get("evidence_id")
        if evidence_id in seen:
            errors.append(f"duplicate evidence_id: {evidence_id}")
        if isinstance(evidence_id, str):
            seen.add(evidence_id)

    status = "ok" if not errors else "errors_found"
    print(json.dumps({"status": status, "entries": len(entries), "errors": errors}, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
