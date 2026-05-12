#!/usr/bin/env python3
"""Validate that findings reference real evidence.

Rules:
- High-severity findings must have at least one evidence_id.
- Every evidence_id referenced by a finding must exist in evidence-ledger.json.
- Warn (do not fail) when more than EMPTY_EVIDENCE_WARN_THRESHOLD of findings
  have empty evidence_ids overall.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HIGH_SEVERITY = {"high", "critical", "p0", "p1"}
EMPTY_EVIDENCE_WARN_THRESHOLD = 0.20


def load_findings(workspace: Path) -> list[dict]:
    findings_path = workspace / "findings" / "findings.json"
    if not findings_path.is_file():
        return []
    data = json.loads(findings_path.read_text(encoding="utf-8"))
    findings = data.get("findings", []) if isinstance(data, dict) else []
    return [item for item in findings if isinstance(item, dict)]


def load_evidence_ids(workspace: Path) -> set[str]:
    ledger_path = workspace / "evidence-ledger.json"
    if not ledger_path.is_file():
        return set()
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    entries = data.get("entries", []) if isinstance(data, dict) else []
    return {
        entry.get("evidence_id")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("evidence_id"), str)
    }


def is_example_finding(finding: dict) -> bool:
    """Treat the unmodified template entry as a no-op rather than a violation."""
    severity = str(finding.get("severity", "")).lower()
    issue = str(finding.get("issue", "")).lower()
    return severity == "example" or "replace this example" in issue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="Path to deals/{deal-id}")
    args = parser.parse_args()

    workspace = Path(args.workspace)

    findings_path = workspace / "findings" / "findings.json"
    if not findings_path.is_file():
        payload = {
            "status": "missing_findings_file",
            "workspace": str(workspace),
            "errors": [f"missing findings file: {findings_path}"],
        }
        print(json.dumps(payload, indent=2))
        return 1

    findings = load_findings(workspace)
    ledger_ids = load_evidence_ids(workspace)

    high_without_evidence: list[str] = []
    broken_refs: list[dict[str, str]] = []
    empty_count = 0
    real_findings = 0

    for finding in findings:
        if is_example_finding(finding):
            continue
        real_findings += 1
        finding_id = str(finding.get("finding_id", "?"))
        severity = str(finding.get("severity", "")).lower()
        evidence_ids = finding.get("evidence_ids") or []
        if not isinstance(evidence_ids, list):
            evidence_ids = []
        evidence_ids = [str(item) for item in evidence_ids if item]

        if not evidence_ids:
            empty_count += 1
            if severity in HIGH_SEVERITY:
                high_without_evidence.append(finding_id)
            continue

        for ev_id in evidence_ids:
            if ev_id not in ledger_ids:
                broken_refs.append({"finding_id": finding_id, "evidence_id": ev_id})

    errors: list[str] = []
    warnings: list[str] = []

    if high_without_evidence:
        errors.append(
            f"{len(high_without_evidence)} high-severity finding(s) have no evidence_ids: "
            + ", ".join(high_without_evidence)
        )

    if broken_refs:
        formatted = ", ".join(f"{ref['finding_id']}->{ref['evidence_id']}" for ref in broken_refs)
        errors.append(
            f"{len(broken_refs)} finding(s) reference evidence_ids missing from evidence-ledger.json: "
            + formatted
        )

    empty_pct = (empty_count / real_findings) if real_findings else 0.0
    if empty_pct > EMPTY_EVIDENCE_WARN_THRESHOLD:
        warnings.append(
            f"{empty_pct:.0%} of findings have empty evidence_ids "
            f"(warn threshold {int(EMPTY_EVIDENCE_WARN_THRESHOLD * 100)}%)"
        )

    status = "ok" if not errors else "errors_found"
    payload = {
        "status": status,
        "workspace": str(workspace),
        "findings_count": real_findings,
        "high_severity_without_evidence": high_without_evidence,
        "broken_references": broken_refs,
        "empty_evidence_count": empty_count,
        "empty_evidence_pct": round(empty_pct, 4),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(payload, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
