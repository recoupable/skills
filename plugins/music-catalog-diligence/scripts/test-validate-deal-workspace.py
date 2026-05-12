#!/usr/bin/env python3
"""Tests for deal workspace readiness validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate-deal-workspace.py")


def create_base_workspace(root: Path) -> Path:
    workspace = root / "deals" / "catalog-sale"
    for directory in ["source", "normalized", "workpapers", "findings", "memos"]:
        (workspace / directory).mkdir(parents=True, exist_ok=True)
    (workspace / "assumptions.yaml").write_text("deal_id: catalog-sale\n", encoding="utf-8")
    (workspace / "evidence-ledger.json").write_text('{"entries": []}\n', encoding="utf-8")
    return workspace


class ValidateDealWorkspaceTest(unittest.TestCase):
    def run_validator(self, workspace: Path) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(workspace)],
            check=False,
            text=True,
            capture_output=True,
        )
        return result.returncode, json.loads(result.stdout)

    def test_fails_when_core_artifacts_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_base_workspace(Path(directory))

            returncode, payload = self.run_validator(workspace)

        self.assertEqual(returncode, 1)
        self.assertEqual(payload["status"], "missing_requirements")
        self.assertIn("normalized/royalty-ledger.csv", payload["missing_artifacts"])
        self.assertIn("findings/findings.json", payload["missing_artifacts"])

    def test_passes_when_core_artifacts_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_base_workspace(Path(directory))
            (workspace / "normalized" / "royalty-ledger.csv").write_text(
                "ledger_line_id,catalog_asset_id,source_file,provider,period_start,period_end,rights_type,income_type,gross_amount,owner_net_amount,currency\n"
                "RL-000001,isrc:USRC17607839,source.csv,Distributor,2025-01-01,2025-01-31,master,streaming,100.00,85.00,USD\n",
                encoding="utf-8",
            )
            (workspace / "findings" / "findings.json").write_text(
                '{"findings": []}\n',
                encoding="utf-8",
            )
            (workspace / "workpapers" / "valuation-summary.json").write_text(
                '{"status": "preliminary"}\n',
                encoding="utf-8",
            )

            returncode, payload = self.run_validator(workspace)

        self.assertEqual(returncode, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["missing_artifacts"], [])


if __name__ == "__main__":
    unittest.main()
