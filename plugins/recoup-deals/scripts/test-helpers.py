#!/usr/bin/env python3
"""Tests for scripts/_helpers.py minimal YAML parser."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _helpers  # noqa: E402


class MinimalYamlParserTest(unittest.TestCase):
    def parse(self, text: str) -> dict:
        return _helpers._parse_minimal_yaml(text)

    def test_parses_top_level_scalars(self) -> None:
        parsed = self.parse("a: 1\nb: \"hello\"\nc: true\nd: null\n")
        self.assertEqual(parsed, {"a": 1, "b": "hello", "c": True, "d": None})

    def test_parses_nested_dict(self) -> None:
        parsed = self.parse(
            "deal:\n  deal_id: \"meridian-2024\"\n  currency: USD\nscope:\n  preliminary_or_full: preliminary\n"
        )
        self.assertEqual(parsed["deal"]["deal_id"], "meridian-2024")
        self.assertEqual(parsed["deal"]["currency"], "USD")
        self.assertEqual(parsed["scope"]["preliminary_or_full"], "preliminary")

    def test_parses_block_list(self) -> None:
        parsed = self.parse(
            "scope:\n  rights_included:\n    - publishing\n    - masters\n  excluded_assets: []\n"
        )
        self.assertEqual(parsed["scope"]["rights_included"], ["publishing", "masters"])
        self.assertEqual(parsed["scope"]["excluded_assets"], [])

    def test_parses_top_level_block_list(self) -> None:
        parsed = self.parse("notes:\n  - \"first note\"\n  - \"second note\"\n")
        self.assertEqual(parsed["notes"], ["first note", "second note"])

    def test_parses_real_assumptions_template(self) -> None:
        plugin_root = Path(__file__).resolve().parents[1]
        path = plugin_root / "templates" / "deal-workspace" / "assumptions.yaml"
        parsed = _helpers.load_yaml(path)
        self.assertEqual(parsed["materiality"]["concentration_threshold_percent"], 40)
        self.assertEqual(parsed["scope"]["rights_included"], ["publishing", "masters"])
        self.assertEqual(parsed["scope"]["excluded_assets"], [])

    def test_deep_get_returns_default_on_miss(self) -> None:
        parsed = {"a": {"b": {"c": 1}}}
        self.assertEqual(_helpers.deep_get(parsed, "a.b.c"), 1)
        self.assertEqual(_helpers.deep_get(parsed, "a.b.missing", default="x"), "x")
        self.assertIsNone(_helpers.deep_get(parsed, "missing.path"))

    def test_handles_unicode_em_dash_in_strings(self) -> None:
        text = "scope:\n  excluded_assets:\n    - \"Coyote Moon Blues (1978) — chain disputed\"\n"
        parsed = self.parse(text)
        self.assertEqual(parsed["scope"]["excluded_assets"][0], "Coyote Moon Blues (1978) — chain disputed")


if __name__ == "__main__":
    unittest.main()
