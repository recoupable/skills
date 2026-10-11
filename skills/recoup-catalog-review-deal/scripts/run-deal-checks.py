#!/usr/bin/env python3
"""Run deterministic readiness checks for a catalog deal workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


CHECKS = [
    ("workspace", "validate-deal-workspace.py", lambda workspace: [workspace]),
    (
        "normalized_ledger",
        "validate-normalized-ledger.py",
        lambda workspace: [workspace / "normalized" / "royalty-ledger.csv"],
    ),
    (
        "evidence_ledger",
        "validate-evidence-ledger.py",
        lambda workspace: [workspace / "evidence-ledger.json"],
    ),
    (
        "findings_evidence",
        "validate-findings-evidence.py",
        lambda workspace: [workspace],
    ),
    (
        "workspace_consistency",
        "validate-workspace-consistency.py",
        lambda workspace: [workspace],
    ),
]


def run_check(name: str, script_name: str, args: list[Path]) -> dict[str, object]:
    script = SCRIPT_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script), *[str(arg) for arg in args]],
        check=False,
        text=True,
        capture_output=True,
    )
    payload: dict[str, object]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    return {
        "name": name,
        "status": "ok" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "details": payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deal_workspace", help="Path to deals/{deal-id}")
    args = parser.parse_args()

    workspace = Path(args.deal_workspace)
    checks = [
        run_check(name, script_name, build_args(workspace))
        for name, script_name, build_args in CHECKS
    ]
    status = "ok" if all(check["status"] == "ok" for check in checks) else "failed"
    print(json.dumps({"status": status, "workspace": str(workspace), "checks": checks}, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
