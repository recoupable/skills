#!/usr/bin/env python3
"""Validate the expected structure for a music catalog deal workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_DIRS = ["source", "normalized", "workpapers", "findings", "memos"]
REQUIRED_FILES = ["assumptions.yaml", "evidence-ledger.json"]
REQUIRED_ARTIFACTS = [
    "normalized/royalty-ledger.csv",
    "findings/findings.json",
]
RECOMMENDED_ARTIFACTS = [
    "workpapers/valuation-summary.json",
]


def validate_json_file(path: Path, label: str) -> list[str]:
    if not path.is_file():
        return []
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"{label} is not valid JSON: {error.msg}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deal_workspace", help="Path to deals/{deal-id}")
    args = parser.parse_args()

    workspace = Path(args.deal_workspace)
    missing_dirs = [name for name in REQUIRED_DIRS if not (workspace / name).is_dir()]
    missing_files = [name for name in REQUIRED_FILES if not (workspace / name).is_file()]
    missing_artifacts = [
        name for name in REQUIRED_ARTIFACTS if not (workspace / name).is_file()
    ]
    recommended_missing = [
        name for name in RECOMMENDED_ARTIFACTS if not (workspace / name).is_file()
    ]
    errors = []
    errors.extend(validate_json_file(workspace / "evidence-ledger.json", "evidence-ledger.json"))
    errors.extend(validate_json_file(workspace / "findings" / "findings.json", "findings/findings.json"))
    status = "ok" if not missing_dirs and not missing_files and not missing_artifacts and not errors else "missing_requirements"
    payload = {
        "status": status,
        "workspace": str(workspace),
        "missing_dirs": missing_dirs,
        "missing_files": missing_files,
        "missing_artifacts": missing_artifacts,
        "recommended_missing": recommended_missing,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
