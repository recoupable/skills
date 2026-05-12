#!/usr/bin/env python3
"""Tests for validate-workspace-consistency.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "validate-workspace-consistency.py"


CANONICAL_HEADER = (
    "catalog_asset_id,rights_type,title,alternate_titles,artist,writers,"
    "publishers,isrc,iswc,upc,ipi_cae,release_title,release_date,territory,"
    "controlled_share,ownership_confidence,metadata_confidence,source_files,conflicts\n"
)

RIGHTS_HEADER = (
    "catalog_asset_id,document_file,document_type,party,share_type,reported_share,"
    "territory,term_start,term_end,restrictions,support_level,notes\n"
)


def make_workspace(
    root: Path,
    *,
    excluded_assets: list[str],
    catalog_rows: list[str],
    rights_rows: list[str] | None = None,
    findings: list[dict] | None = None,
) -> Path:
    workspace = root / "deals" / "test"
    (workspace / "normalized").mkdir(parents=True, exist_ok=True)
    (workspace / "findings").mkdir(parents=True, exist_ok=True)

    excl = "\n".join(f"    - \"{item}\"" for item in excluded_assets) if excluded_assets else "    []"
    yaml_text = (
        "scope:\n"
        + ("  excluded_assets:\n" + excl + "\n" if excluded_assets else "  excluded_assets: []\n")
    )
    (workspace / "assumptions.yaml").write_text(yaml_text, encoding="utf-8")

    (workspace / "normalized" / "canonical-catalog.csv").write_text(
        CANONICAL_HEADER + "".join(catalog_rows), encoding="utf-8"
    )
    if rights_rows is not None:
        (workspace / "normalized" / "rights-map.csv").write_text(
            RIGHTS_HEADER + "".join(rights_rows), encoding="utf-8"
        )
    if findings is not None:
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


def catalog_row(asset_id: str, title: str, share: float, conflicts: str = "") -> str:
    return f"{asset_id},publishing,{title},,,,,,,,,,1973,worldwide,{share},,,,\"{conflicts}\"\n"


def rights_row(asset_id: str, support: str, notes: str) -> str:
    # Header has 12 columns; this row matches: catalog_asset_id, document_file,
    # document_type, party, share_type, reported_share, territory, term_start,
    # term_end, restrictions, support_level, notes.
    return f"{asset_id},,,,,,,,,,{support},\"{notes}\"\n"


class WorkspaceConsistencyTest(unittest.TestCase):
    def test_passes_when_excluded_asset_has_zero_share(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(
                Path(directory),
                excluded_assets=["Coyote Moon Blues (1978) -- chain disputed"],
                catalog_rows=[catalog_row("COYOTE_MOON", "Coyote Moon Blues", 0.0)],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["excluded_asset_violations"], [])

    def test_fails_when_excluded_asset_has_nonzero_share(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(
                Path(directory),
                excluded_assets=["Coyote Moon Blues (1978) -- chain disputed"],
                catalog_rows=[catalog_row("COYOTE_MOON", "Coyote Moon Blues", 100.0)],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 1)
        self.assertEqual(len(payload["excluded_asset_violations"]), 1)
        violation = payload["excluded_asset_violations"][0]
        self.assertEqual(violation["catalog_asset_id"], "COYOTE_MOON")
        self.assertEqual(violation["controlled_share"], 100.0)

    def test_fails_when_reverted_rights_target_has_nonzero_share(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(
                Path(directory),
                excluded_assets=[],
                catalog_rows=[catalog_row("PINEWOOD", "Pinewood", 100.0)],
                rights_rows=[rights_row("PINEWOOD", "conflicting", "Reverted per termination letter 2022")],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 1)
        self.assertEqual(len(payload["reverted_rights_violations"]), 1)
        self.assertEqual(payload["reverted_rights_violations"][0]["catalog_asset_id"], "PINEWOOD")

    def test_warns_when_exclusion_finding_targets_nonzero_share(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(
                Path(directory),
                excluded_assets=[],
                catalog_rows=[catalog_row("HIGHWAY_PINES", "Highway to the Pines", 100.0)],
                findings=[
                    {
                        "finding_id": "F-017",
                        "severity": "high",
                        "affected_assets": ["HIGHWAY_PINES"],
                        "valuation_treatment": "Exclude or apply 100% holdback on Highway to the Pines income.",
                        "evidence_ids": ["EV-001"],
                    }
                ],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(payload["exclusion_finding_warnings"]), 1)
        self.assertEqual(payload["exclusion_finding_warnings"][0]["finding_id"], "F-017")

    def test_unmatched_excluded_label_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = make_workspace(
                Path(directory),
                excluded_assets=["Some Song That Doesn't Exist"],
                catalog_rows=[catalog_row("REAL_SONG", "Real Song", 100.0)],
            )
            code, payload = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(len(payload["unmatched_excluded_labels"]), 1)


if __name__ == "__main__":
    unittest.main()
