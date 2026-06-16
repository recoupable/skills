#!/usr/bin/env python3
"""Unit tests for validate_release. Stdlib unittest; no deps."""
import os
import tempfile
import unittest

import validate_release as vr


def write(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class ValidateTests(unittest.TestCase):
    def test_empty_workspace_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            r = vr.validate(d)
            self.assertEqual(r["status"], "incomplete")
            self.assertIn("RELEASE.md", r["missing"])
            self.assertIn("assumptions.yaml", r["missing"])

    def test_complete_workspace_is_ok(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "assumptions.yaml"),
                  "artist: Gatsby Grace\nrelease_title: Blue Slide Park\n"
                  "release_date: 2026-07-31\ncreative_direction: warm nostalgic bedroom pop\n")
            write(os.path.join(d, "RELEASE.md"), "# RELEASE\n## 1. Project Snapshot\n- Artist: Gatsby Grace\n")
            write(os.path.join(d, "brief", "brief-2026-06-06.md"), "# Brief\nstuff\n")
            write(os.path.join(d, "campaign", "campaign-2026-06-06.md"), "# Campaign\nstuff\n")
            r = vr.validate(d)
            self.assertEqual(r["status"], "ok", r)
            self.assertEqual(r["missing"], [])

    def test_empty_assumption_fields_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "assumptions.yaml"),
                  "artist: Gatsby Grace\nrelease_title:\nrelease_date: 2026-07-31\ncreative_direction: x\n")
            write(os.path.join(d, "RELEASE.md"), "## 1. Project Snapshot\n")
            write(os.path.join(d, "brief", "b.md"), "x")
            write(os.path.join(d, "campaign", "c.md"), "x")
            r = vr.validate(d)
            self.assertEqual(r["status"], "incomplete")
            self.assertTrue(any("release_title" in m for m in r["missing"]))

    def test_gitkeep_does_not_count_as_brief(self):
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "assumptions.yaml"),
                  "artist: A\nrelease_title: T\nrelease_date: TBD\ncreative_direction: x\n")
            write(os.path.join(d, "RELEASE.md"), "## 1. Project Snapshot\n")
            os.makedirs(os.path.join(d, "brief"))
            write(os.path.join(d, "brief", ".gitkeep"), "")
            write(os.path.join(d, "campaign", "c.md"), "x")
            r = vr.validate(d)
            self.assertIn("brief/ (no creative brief written)", r["missing"])


if __name__ == "__main__":
    unittest.main()
