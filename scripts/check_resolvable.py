#!/usr/bin/env python3
"""Resolver reachability audit for the Recoup Skills plugin (repo root).

Enforces that the bundle's RESOLVER.md routing table stays honest as skills are
added/removed — the "no dark skills" guarantee. A skill that exists but isn't
reachable from the resolver is "a surgeon the
hospital can't find"; a route that points at a deleted skill sends the agent
nowhere.

Two findings, both fatal (exit 1):
  1. UNREACHABLE — a skills/<name>/SKILL.md with no row in RESOLVER.md.
  2. BROKEN ROUTE — a `recoup-*` token in RESOLVER.md with no matching skill dir.

Usage:
  python3 scripts/check_resolvable.py                 # default: repo root (skills/ + RESOLVER.md)
  python3 scripts/check_resolvable.py path/to/subdir  # any dir with skills/ + RESOLVER.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLUGIN = REPO_ROOT

# A skill reference in RESOLVER.md is a backtick-wrapped slug: `recoup-foo-bar`.
SKILL_TOKEN = re.compile(r"`(recoup-[a-z0-9.-]+)`")


def skill_dirs(plugin: Path) -> set[str]:
    """Every skill that physically exists (has a SKILL.md)."""
    skills_root = plugin / "skills"
    return {
        p.parent.name
        for p in skills_root.glob("*/SKILL.md")
    }


def routed_skills(resolver: Path) -> set[str]:
    """Skill slugs that appear in an actual routing-table ROW (a line starting
    with `|`). Prose mentions (disambiguation notes, the plugin's own name) are
    intentionally ignored — a skill counts as "routed" only when it has a real
    table row, which forces every skill into the table rather than a passing
    backtick reference."""
    routed: set[str] = set()
    for line in resolver.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("|"):
            routed.update(SKILL_TOKEN.findall(line))
    return routed


def audit(plugin: Path, problems: list[str]) -> None:
    resolver = plugin / "RESOLVER.md"
    rel = plugin.relative_to(REPO_ROOT)
    if not resolver.exists():
        problems.append(f"{rel}: no RESOLVER.md (cannot audit routing reachability)")
        return

    existing = skill_dirs(plugin)
    routed = routed_skills(resolver)

    # 1. Skills that exist but are never routed to → dark.
    for name in sorted(existing - routed):
        problems.append(
            f"{rel}: UNREACHABLE — skills/{name}/ has no route in RESOLVER.md "
            f"(add an intent row, or the skill is dead weight nobody can reach)"
        )

    # 2. Routes that point at a skill that does not exist → broken.
    for name in sorted(routed - existing):
        problems.append(
            f"{rel}: BROKEN ROUTE — RESOLVER.md references `{name}` "
            f"but skills/{name}/SKILL.md does not exist"
        )


def main(argv: list[str]) -> int:
    plugin = DEFAULT_PLUGIN if len(argv) < 2 else (REPO_ROOT / argv[1])
    if not plugin.is_dir():
        print(f"check_resolvable: not a directory: {plugin}", file=sys.stderr)
        return 2

    problems: list[str] = []
    audit(plugin, problems)

    existing = skill_dirs(plugin)
    if problems:
        print(f"check_resolvable: {len(problems)} problem(s) in {plugin.name}:\n")
        for p in problems:
            print(f"  - {p}")
        print(
            f"\n{len(existing)} skills on disk. Every skill must have a route and "
            f"every route must resolve. Fix RESOLVER.md."
        )
        return 1

    print(
        f"check_resolvable: OK — all {len(existing)} skills in {plugin.name} are "
        f"reachable from RESOLVER.md and every route resolves."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
