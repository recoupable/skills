#!/usr/bin/env python3
"""Tests for findings-to-evidence traceability validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate-findings-evidence.py")


def write_workspace(root: Path, ledger_entries: list[dict], findings: list[dict]) -> Path:
    workspace = root / "deals" / "test-deal"
    (workspace / "findings").mkdir(parents=True, exist_ok=True)
    (workspace / "evidence-ledger.json").write_text(
        json.dumps({"entries": ledger_entries}), encoding="utf-8"
    )
    (workspace / "findings" / "findings.json").write_text(
        json.dumps({"findings": findings}), encoding="utf-8"
    )
    return workspace


def run(workspace: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(workspace)],
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    return result.returncode, payload


class ValidateFindingsEvidenceTest(unittest.TestCase):
    def test_passes_when_all_high_severity_findings_have_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                ledger_entries=[{"evidence_id": "EV-001"}],
                findings=[
                    {"finding_id": "F-001", "severity": "high", "evidence_ids": ["EV-001"]},
                    {"finding_id": "F-002", "severity": "low", "evidence_ids": []},
                ],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["high_severity_without_evidence"], [])
        self.assertEqual(payload["broken_references"], [])

    def test_fails_when_high_severity_finding_has_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                ledger_entries=[{"evidence_id": "EV-001"}],
                findings=[
                    {"finding_id": "F-001", "severity": "high", "evidence_ids": []},
                    {"finding_id": "F-002", "severity": "P1", "evidence_ids": []},
                    {"finding_id": "F-003", "severity": "medium", "evidence_ids": []},
                    {"finding_id": "F-004", "severity": "low", "evidence_ids": []},
                ],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], "errors_found")
        self.assertEqual(
            sorted(payload["high_severity_without_evidence"]),
            ["F-001", "F-002"],
        )
        self.assertTrue(payload["errors"], payload)

    def test_fails_on_broken_evidence_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                ledger_entries=[{"evidence_id": "EV-001"}],
                findings=[
                    {
                        "finding_id": "F-001",
                        "severity": "high",
                        "evidence_ids": ["EV-001", "EV-MISSING"],
                    }
                ],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["broken_references"],
            [{"finding_id": "F-001", "evidence_id": "EV-MISSING"}],
        )

    def test_warns_above_empty_evidence_threshold_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                ledger_entries=[{"evidence_id": "EV-001"}],
                findings=[
                    {"finding_id": "F-001", "severity": "low", "evidence_ids": []},
                    {"finding_id": "F-002", "severity": "low", "evidence_ids": []},
                    {"finding_id": "F-003", "severity": "medium", "evidence_ids": []},
                    {"finding_id": "F-004", "severity": "medium", "evidence_ids": ["EV-001"]},
                ],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["warnings"], payload)

    def test_ignores_unmodified_template_example(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                ledger_entries=[{"evidence_id": "EV-001"}],
                findings=[
                    {
                        "finding_id": "F-001",
                        "severity": "example",
                        "issue": "Replace this example finding with a real diligence issue.",
                        "evidence_ids": [],
                    }
                ],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(payload["findings_count"], 0)


if __name__ == "__main__":
    unittest.main()
