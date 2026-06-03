#!/usr/bin/env python3
"""Drift check for vendored (duplicated) files.

Portable skills are self-contained, so shared references/scripts are COPIED
into each skill rather than centralized. This check keeps every copy
byte-identical to its single canonical source, so vendoring can never silently
diverge.

Reads scripts/vendored.json. Two group kinds:
  - file group:  {"canonical": "<file>", "copies": ["<file>", ...]}
  - dir  group:  {"canonical_dir": "<dir>", "copies_dirs": ["<dir>", ...]}
File groups assert byte-identity; dir groups assert the trees are identical
(same files, all byte-identical) via filecmp.dircmp.

Usage: python3 scripts/check_vendored.py
Exit 0 = all copies match canonical; 1 = drift or missing files. Stdlib only.
"""
from __future__ import annotations

import filecmp
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_FILE = REPO_ROOT / "scripts" / "vendored.json"


def main() -> int:
    if not MAP_FILE.exists():
        print(f"No {MAP_FILE.relative_to(REPO_ROOT)} yet — nothing vendored to check.")
        return 0

    try:
        data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  ✗ scripts/vendored.json: invalid JSON: {exc}")
        return 1

    groups = data.get("groups", [])
    problems: list[str] = []
    copies_checked = 0

    def tree_diff(a: Path, b: Path) -> list[str]:
        """Return human-readable differences between two directory trees."""
        cmp = filecmp.dircmp(a, b)
        diffs: list[str] = []
        if cmp.left_only:
            diffs.append(f"only in canonical: {sorted(cmp.left_only)}")
        if cmp.right_only:
            diffs.append(f"only in copy: {sorted(cmp.right_only)}")
        if cmp.diff_files:
            diffs.append(f"differing files: {sorted(cmp.diff_files)}")
        for sub in cmp.common_dirs:
            diffs.extend(f"{sub}/{d}" for d in tree_diff(a / sub, b / sub))
        return diffs

    for g in groups:
        if "canonical_dir" in g:
            canonical = REPO_ROOT / g["canonical_dir"]
            if not canonical.is_dir():
                problems.append(f"canonical dir missing: {g['canonical_dir']}")
                continue
            for copy_rel in g.get("copies_dirs", []):
                copies_checked += 1
                copy = REPO_ROOT / copy_rel
                if not copy.is_dir():
                    problems.append(f"copy dir missing: {copy_rel} (canonical {g['canonical_dir']})")
                    continue
                d = tree_diff(canonical, copy)
                if d:
                    problems.append(f"DRIFT (tree): {copy_rel} != {g['canonical_dir']} -> {'; '.join(d)}")
            continue

        canonical = REPO_ROOT / g["canonical"]
        if not canonical.exists():
            problems.append(f"canonical missing: {g['canonical']}")
            continue
        for copy_rel in g.get("copies", []):
            copies_checked += 1
            copy = REPO_ROOT / copy_rel
            if not copy.exists():
                problems.append(f"copy missing: {copy_rel} (canonical {g['canonical']})")
                continue
            if not filecmp.cmp(canonical, copy, shallow=False):
                problems.append(f"DRIFT: {copy_rel} != {g['canonical']}")

    if problems:
        print(f"VENDOR DRIFT CHECK FAILED — {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  ✗ {p}")
        print("\nRe-sync copies from canonical, or update scripts/vendored.json.")
        return 1

    print(f"VENDOR DRIFT CHECK PASSED — {copies_checked} copy/copies match canonical across {len(groups)} group(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
