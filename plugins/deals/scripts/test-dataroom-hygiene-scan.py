#!/usr/bin/env python3
"""Tests for dataroom-hygiene-scan.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("dataroom-hygiene-scan.py")


def write_workspace(root: Path, files: dict[str, str]) -> Path:
    workspace = root / "deals" / "test"
    source = workspace / "source"
    source.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return workspace


def run(workspace: Path) -> tuple[int, dict, dict, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(workspace)],
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout) if result.stdout.strip() else {}
    workpaper = json.loads((workspace / "workpapers" / "dataroom-hygiene.json").read_text(encoding="utf-8"))
    findings = json.loads((workspace / "findings" / "dataroom-hygiene-findings.json").read_text(encoding="utf-8"))
    return result.returncode, payload, workpaper, findings


class HygieneScanTest(unittest.TestCase):
    def test_emits_finding_for_concealment_filename_with_content_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                {
                    "07_Misc/DELETE_BEFORE_SHARING.txt": (
                        "Personal admin checklist.\n"
                        "Estimate ~$11K we owe her. DO NOT volunteer this number.\n"
                    ),
                },
            )
            code, _payload, workpaper, findings = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(workpaper["match_count"], 1)
        match = workpaper["matches"][0]
        self.assertTrue(match["filename_strong"])
        self.assertEqual(len(match["content_matches"]), 1)
        self.assertEqual(match["match_strength"], "high")
        self.assertEqual(len(findings["findings"]), 1)
        finding = findings["findings"][0]
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["category"], "process_integrity")
        self.assertIn("DELETE_BEFORE_SHARING.txt", finding["issue"])

    def test_does_not_flag_song_titles_with_dont_or_draft_keywords(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                {
                    "Split_Sheets/Dont_Stop_Now_2010.txt": "writer share: 75/25",
                    "Catalog/old_friends_song.txt": "title: Old Friends",
                    "Catalog/Don_Henley_Catalog.txt": "writer: Don Henley",
                },
            )
            code, _payload, workpaper, findings = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(workpaper["match_count"], 0, f"unexpected matches: {workpaper}")
        self.assertEqual(findings["findings"], [])

    def test_records_weak_matches_in_workpaper_without_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                {
                    "04_Rights/Cooper_Lane_S203_termination_notice_2007_DRAFT.txt": "draft notice text",
                },
            )
            code, _payload, workpaper, findings = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(workpaper["match_count"], 1)
        self.assertEqual(workpaper["matches"][0]["match_strength"], "weak")
        self.assertEqual(findings["findings"], [])

    def test_content_only_match_emits_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(
                Path(directory),
                {
                    "07_Misc/seller_notes.md": (
                        "Some notes.\n\n"
                        "Remove before sharing the section about Brennan's reversion.\n"
                    ),
                },
            )
            code, _payload, _workpaper, findings = run(workspace)
        self.assertEqual(code, 0)
        self.assertEqual(len(findings["findings"]), 1)
        self.assertEqual(findings["findings"][0]["severity"], "high")


if __name__ == "__main__":
    unittest.main()
