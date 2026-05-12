#!/usr/bin/env python3
"""Tests for diligence readiness helpers."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
RUN_CHECKS = SCRIPT_DIR / "run-diligence-checks.py"
BUILD_DASHBOARD = SCRIPT_DIR / "build-diligence-dashboard.py"


def create_workspace(root: Path, findings: list[dict[str, Any]] | None = None) -> Path:
    """Build a minimal valid deal workspace.

    Pass ``findings`` to override the default single-P1 finding so individual
    tests can exercise different severity levels.
    """
    workspace = root / "deals" / "catalog-sale"
    for directory in ["source", "normalized", "workpapers", "findings", "memos"]:
        (workspace / directory).mkdir(parents=True, exist_ok=True)
    (workspace / "assumptions.yaml").write_text("deal_id: catalog-sale\n", encoding="utf-8")
    (workspace / "evidence-ledger.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "evidence_id": "EV-001",
                        "source_file": "source/royalties.csv",
                        "source_type": "royalty_statement",
                        "locator": "row 2",
                        "extracted_field": "owner_net_amount",
                        "extracted_value": "85.00",
                        "confidence": "high",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (workspace / "normalized" / "royalty-ledger.csv").write_text(
        "ledger_line_id,catalog_asset_id,source_file,provider,period_start,period_end,rights_type,income_type,gross_amount,owner_net_amount,currency\n"
        "RL-000001,isrc:USRC17607839,source/royalties.csv,Distributor,2025-01-01,2025-01-31,master,streaming,100.00,85.00,USD\n",
        encoding="utf-8",
    )
    if findings is None:
        findings = [
            {
                "finding_id": "F-001",
                "severity": "P1",
                "status": "open",
                "title": "Missing split sheet for top composition",
                "evidence_ids": ["EV-001"],
            }
        ]
    (workspace / "findings" / "findings.json").write_text(
        json.dumps({"findings": findings}),
        encoding="utf-8",
    )
    (workspace / "workpapers" / "valuation-summary.json").write_text(
        '{"status": "preliminary"}\n',
        encoding="utf-8",
    )
    return workspace


def run_dashboard(workspace: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    """Run build-diligence-dashboard.py against a workspace and capture output."""
    output = workspace / "diligence-dashboard.md"
    return subprocess.run(
        [
            sys.executable,
            str(BUILD_DASHBOARD),
            str(workspace),
            "--output",
            str(output),
            *extra_args,
        ],
        check=False,
        text=True,
        capture_output=True,
    )


class DiligenceReadinessTest(unittest.TestCase):
    def test_run_checks_reports_all_validator_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))

            result = subprocess.run(
                [sys.executable, str(RUN_CHECKS), str(workspace)],
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            [check["name"] for check in payload["checks"]],
            [
                "workspace",
                "normalized_ledger",
                "evidence_ledger",
                "findings_evidence",
                "workspace_consistency",
            ],
        )


class BuildDashboardTest(unittest.TestCase):
    """Locks in the fix for the severity-taxonomy / title-field bug.

    Before the fix, the dashboard only treated ``P0``/``P1`` as severe and
    looked up ``title``. The rest of the plugin emits findings using the
    canonical ``critical|high|medium|low`` taxonomy with an ``issue`` field,
    which silently produced ``ready`` even when blockers existed.
    """

    def assert_dashboard_text(self, text: str, *, status: str, must_contain: list[str]) -> None:
        self.assertIn("# Diligence Dashboard", text)
        self.assertIn(f"Overall status: `{status}`", text)
        for fragment in must_contain:
            self.assertIn(fragment, text)

    def test_legacy_p1_with_title_renders_review_needed(self) -> None:
        """Backwards compatibility: the original P1+title fixture still works."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            result = run_dashboard(workspace)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            text = (workspace / "diligence-dashboard.md").read_text(encoding="utf-8")

        self.assert_dashboard_text(
            text,
            status="review_needed",
            must_contain=["Missing split sheet for top composition"],
        )

    def test_canonical_high_severity_with_issue_renders_review_needed(self) -> None:
        """Findings emitted by the rest of the plugin (severity=high, issue=...)
        must be picked up. This is the regression that the fix addresses."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "RF-001",
                        "severity": "high",
                        "category": "rights",
                        "status": "open",
                        "issue": "Income-generating work has no split sheet.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            text = (workspace / "diligence-dashboard.md").read_text(encoding="utf-8")

        self.assert_dashboard_text(
            text,
            status="review_needed",
            must_contain=["Income-generating work has no split sheet."],
        )

    def test_canonical_critical_severity_renders_blocked(self) -> None:
        """A critical finding must drive the dashboard into ``blocked``."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "RF-002",
                        "severity": "critical",
                        "category": "rights",
                        "status": "open",
                        "issue": "Catalog-wide assignment is missing.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            text = (workspace / "diligence-dashboard.md").read_text(encoding="utf-8")

        self.assert_dashboard_text(
            text,
            status="blocked",
            must_contain=["Catalog-wide assignment is missing."],
        )

    def test_severity_match_is_case_insensitive(self) -> None:
        """``HIGH``, ``High``, ``high`` should all be treated identically."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "F-CASE",
                        "severity": "HIGH",
                        "status": "open",
                        "issue": "Mixed-case severity should still be detected.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            text = (workspace / "diligence-dashboard.md").read_text(encoding="utf-8")

        self.assertIn("Overall status: `review_needed`", text)

    def test_resolved_findings_do_not_block(self) -> None:
        """A resolved critical finding should not push the deal back to blocked."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "F-CLOSED",
                        "severity": "critical",
                        "status": "resolved",
                        "issue": "Already cured before close.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            text = (workspace / "diligence-dashboard.md").read_text(encoding="utf-8")

        self.assertIn("Overall status: `ready`", text)

    def test_stdout_payload_reports_deal_status(self) -> None:
        """The JSON payload printed to stdout must include the computed deal_status."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "RF-003",
                        "severity": "critical",
                        "status": "open",
                        "issue": "Blocking issue.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["deal_status"], "blocked")
        self.assertEqual(payload["open_blockers"], 1)
        self.assertEqual(payload["open_review_items"], 0)

    def test_fail_on_blocked_returns_nonzero_exit_when_blocked(self) -> None:
        """``--fail-on-blocked`` lets CI / orchestrators enforce the guardrail."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "RF-004",
                        "severity": "critical",
                        "status": "open",
                        "issue": "Stop-the-deal issue.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace, "--fail-on-blocked")

        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)

    def test_fail_on_blocked_succeeds_when_only_review_items_present(self) -> None:
        """``--fail-on-blocked`` must NOT fail on a ``review_needed`` deal."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(
                Path(directory),
                findings=[
                    {
                        "finding_id": "RF-005",
                        "severity": "high",
                        "status": "open",
                        "issue": "High but disclosable.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            result = run_dashboard(workspace, "--fail-on-blocked")

        self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == "__main__":
    unittest.main()
