#!/usr/bin/env python3
"""Validate plugin/marketplace manifests + connector configs.

Checks:
  - every marketplace.json / plugin.json / .mcp.json is valid JSON
    (catches the invalid-JSON class of bug, e.g. a missing comma in .mcp.json);
  - marketplace plugins have name + source + semver version, source dir exists,
    names are unique;
  - dual-manifest PARITY: .claude-plugin/marketplace.json and
    .agents/plugins/marketplace.json list the same plugins (name/source/version);
    the .agents copy may add an `interface{}` block, which is ignored.

Usage: python3 scripts/validate_manifests.py
Exit 0 = valid; 1 = problems (printed). Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+([-+].+)?$")

CLAUDE_MARKET = REPO_ROOT / ".claude-plugin" / "marketplace.json"
AGENTS_MARKET = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"


def load_json(path: Path) -> tuple[dict | list | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"
    except OSError as exc:
        return None, f"cannot read: {exc}"


def discover(name: str) -> list[Path]:
    return sorted(p for p in REPO_ROOT.rglob(name) if "node_modules" not in p.parts)


def validate_marketplace(path: Path, problems: list[str]) -> list[dict]:
    data, err = load_json(path)
    rel = path.relative_to(REPO_ROOT)
    if err:
        problems.append(f"{rel}: {err}")
        return []
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
        problems.append(f"{rel}: missing top-level 'plugins' array")
        return []

    plugins = data["plugins"]
    seen_names: set[str] = set()
    for i, plugin in enumerate(plugins):
        loc = f"{rel} plugins[{i}]"
        for field in ("name", "source", "version"):
            if field not in plugin:
                problems.append(f"{loc}: missing required field '{field}'")
        name = plugin.get("name", "")
        if name in seen_names:
            problems.append(f"{loc}: duplicate plugin name '{name}'")
        seen_names.add(name)
        version = plugin.get("version", "")
        if version and not SEMVER.match(str(version)):
            problems.append(f"{loc}: version '{version}' is not semver")
        source = plugin.get("source")
        if source:
            src_dir = (REPO_ROOT / source).resolve()
            if not src_dir.is_dir():
                problems.append(f"{loc}: source '{source}' is not a directory")
    return plugins


def parity(claude: list[dict], agents: list[dict], problems: list[str]) -> None:
    def key_set(plugins: list[dict]) -> set[tuple[str, str, str]]:
        return {(p.get("name", ""), p.get("source", ""), str(p.get("version", ""))) for p in plugins}

    c, a = key_set(claude), key_set(agents)
    only_claude = c - a
    only_agents = a - c
    for name, source, version in sorted(only_claude):
        problems.append(f"PARITY: in .claude-plugin only: {name} ({source} @ {version})")
    for name, source, version in sorted(only_agents):
        problems.append(f"PARITY: in .agents only: {name} ({source} @ {version})")


def main() -> int:
    problems: list[str] = []

    # 1. JSON validity for every manifest/connector file.
    checked = 0
    for fname in ("marketplace.json", "plugin.json", ".mcp.json"):
        for path in discover(fname):
            checked += 1
            _, err = load_json(path)
            if err:
                problems.append(f"{path.relative_to(REPO_ROOT)}: {err}")

    # 2. Marketplace structure.
    claude_plugins = validate_marketplace(CLAUDE_MARKET, problems) if CLAUDE_MARKET.exists() else []
    if not CLAUDE_MARKET.exists():
        problems.append(f"missing {CLAUDE_MARKET.relative_to(REPO_ROOT)}")
    agents_plugins = validate_marketplace(AGENTS_MARKET, problems) if AGENTS_MARKET.exists() else []
    if not AGENTS_MARKET.exists():
        problems.append(f"missing {AGENTS_MARKET.relative_to(REPO_ROOT)}")

    # 3. Dual-manifest parity.
    if claude_plugins and agents_plugins:
        parity(claude_plugins, agents_plugins, problems)

    if problems:
        print(f"MANIFEST VALIDATION FAILED — {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  ✗ {p}")
        return 1

    print(f"MANIFEST VALIDATION PASSED — {checked} manifest/connector file(s) valid; dual-manifest parity OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
