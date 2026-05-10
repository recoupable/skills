#!/usr/bin/env python3
"""
Generate Recoupable marketplace files for Claude Code, Codex, and Cursor.

Reads marketplace.source.json (the single source of truth) and writes three
platform-specific marketplace files:

  - .claude-plugin/marketplace.json   (Claude Code)
  - .agents/plugins/marketplace.json  (Codex)
  - .cursor-plugin/marketplace.json   (Cursor)

Usage:
    python3 scripts/generate-marketplaces.py [--check]

    --check  exit non-zero if generated files differ from source-of-truth
             (suitable for CI).

Zero external dependencies. Python 3.9+ stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = REPO_ROOT / "marketplace.source.json"

CLAUDE_OUT = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_OUT = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_OUT = REPO_ROOT / ".cursor-plugin" / "marketplace.json"


def load_source() -> dict[str, Any]:
    if not SOURCE_FILE.exists():
        sys.exit(f"error: {SOURCE_FILE} not found")
    with SOURCE_FILE.open() as fh:
        data = json.load(fh)
    return data


def build_claude(source: dict[str, Any]) -> dict[str, Any]:
    """Claude Code marketplace.json (anthropics/skills + anthropics/claude-plugins-official shape)."""
    mp = source["marketplace"]
    out: dict[str, Any] = {
        "name": mp["name"],
        "owner": mp["owner"],
        "metadata": {
            "description": mp["description"],
            "version": mp["version"],
        },
        "plugins": [],
    }
    for plugin in source["plugins"]:
        entry: dict[str, Any] = {
            "name": plugin["name"],
            "description": plugin["description"],
            "version": plugin["version"],
            "source": plugin["source"],
            "category": plugin["category"],
            "keywords": plugin.get("keywords", []),
        }
        if plugin["type"] == "virtual":
            entry["strict"] = False
            entry["skills"] = plugin["skills"]
        if "tags" in plugin:
            entry["tags"] = plugin["tags"]
        out["plugins"].append(entry)
    return out


def build_codex(source: dict[str, Any]) -> dict[str, Any]:
    """Codex marketplace.json with richer policy/auth metadata per Codex spec."""
    mp = source["marketplace"]
    out: dict[str, Any] = {
        "name": mp["name"],
        "description": mp["description"],
        "owner": mp["owner"],
        "interface": {
            "displayName": "Recoupable",
        },
        "plugins": [],
    }
    for plugin in source["plugins"]:
        entry: dict[str, Any] = {
            "name": plugin["name"],
            "description": plugin["description"],
            "source": {
                "source": "local",
                "path": plugin["source"],
            },
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
            "category": plugin["category"],
            "keywords": plugin.get("keywords", []),
        }
        if "interface" in plugin:
            entry["interface"] = plugin["interface"]
        out["plugins"].append(entry)
    return out


def build_cursor(source: dict[str, Any]) -> dict[str, Any]:
    """Cursor marketplace.json (matches current Recoupable Cursor pattern)."""
    mp = source["marketplace"]
    out: dict[str, Any] = {
        "name": mp["name"],
        "owner": {
            "name": mp["owner"]["name"],
            "email": mp["owner"]["email"],
        },
        "metadata": {
            "description": mp["description"],
        },
        "plugins": [],
    }
    for plugin in source["plugins"]:
        entry: dict[str, Any] = {
            "name": plugin["name"],
            "source": plugin["source"].lstrip("./") or ".",
            "description": plugin["description"],
            "version": plugin["version"],
            "author": {
                "name": mp["owner"]["name"],
                "email": mp["owner"]["email"],
            },
            "homepage": mp["homepage"],
            "repository": mp["repository"],
            "license": mp["license"],
            "category": plugin["category"],
            "keywords": plugin.get("keywords", []),
        }
        if "tags" in plugin:
            entry["tags"] = plugin["tags"]
        out["plugins"].append(entry)
    return out


def serialize(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def write_if_changed(path: Path, content: str, *, check: bool) -> bool:
    """Return True when path matches content; False when it differs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else None
    if existing == content:
        return True
    if check:
        return False
    path.write_text(content)
    print(f"wrote {path.relative_to(REPO_ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if generated files would change (for CI)",
    )
    args = parser.parse_args()

    source = load_source()

    targets = [
        (CLAUDE_OUT, build_claude(source)),
        (CODEX_OUT, build_codex(source)),
        (CURSOR_OUT, build_cursor(source)),
    ]

    all_match = True
    for path, data in targets:
        if not write_if_changed(path, serialize(data), check=args.check):
            all_match = False
            print(f"would update {path.relative_to(REPO_ROOT)}", file=sys.stderr)

    if args.check and not all_match:
        print(
            "error: marketplace files are stale. Run "
            "`python3 scripts/generate-marketplaces.py` and commit the result.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
