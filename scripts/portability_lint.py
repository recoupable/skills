#!/usr/bin/env python3
"""Portable Skill Contract linter.

Enforces cross-harness portability for every SKILL.md in the repo. A skill is
portable iff it references only files inside its own directory, uses no
platform-specific path variables, and links local files with backtick paths
rather than markdown links.

Rules (see AGENTS.md "Portable Skill Contract"):
  1. No platform variables  -> ${CLAUDE_PLUGIN_ROOT}, $CLAUDE_*, ${CLAUDE_SKILL_DIR}
  2. No escapes             -> ../, ../../references/, skills/<other>/...
  3. Backtick paths, not markdown links, for references/scripts/etc.
  4. Every referenced local resource path must exist inside the skill dir.

Usage:
  python3 scripts/portability_lint.py            # lint whole repo
  python3 scripts/portability_lint.py plugins/research   # limit to a subtree

Exit code 0 = all skills portable; 1 = violations found (printed file:line).
Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories that hold a skill's own resources (relative to the skill dir).
RESOURCE_DIRS = ("references", "scripts", "templates", "fixtures", "assets")

# Rule 1: any Claude-only path variable in the body.
PLATFORM_VAR = re.compile(r"\$\{?CLAUDE_[A-Z_]+\}?")

# Rule 2: a relative path that climbs out of the skill dir into a resource dir.
ESCAPE_PATH = re.compile(r"(?:\.\./)+(?:%s)/" % "|".join(RESOURCE_DIRS))
# Rule 2: a reference into another skill's directory.
CROSS_SKILL = re.compile(r"skills/[A-Za-z0-9_-]+/(?:%s|SKILL\.md)" % "|".join(RESOURCE_DIRS))

# Rule 3: markdown link whose target is a local resource path (should be backtick).
MD_LINK_LOCAL = re.compile(
    r"\]\(\s*(?:\.{1,2}/)?(?:%s)/[^)]+\)" % "|".join(RESOURCE_DIRS)
)
MD_LINK_PARENT = re.compile(r"\]\(\s*\.\./[^)]+\)")

# Rule 4: a resource path token (used to check on-disk existence).
RESOURCE_TOKEN = re.compile(
    r"((?:\.{1,2}/)*(?:%s)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)" % "|".join(RESOURCE_DIRS)
)


def find_skill_files(root: Path) -> list[Path]:
    return sorted(root.rglob("SKILL.md"))


def code_and_backtick_spans(body: str) -> list[tuple[int, str]]:
    """Return (line_number, text) for inline-code spans and fenced-code lines.

    We only check resource existence against tokens that the agent would treat
    as a path (inside backticks or fenced blocks), avoiding prose false positives.
    """
    spans: list[tuple[int, str]] = []
    in_fence = False
    for i, line in enumerate(body.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            spans.append((i, line))
            continue
        for m in re.finditer(r"`([^`]+)`", line):
            spans.append((i, m.group(1)))
    return spans


def line_of(body: str, index: int) -> int:
    return body.count("\n", 0, index) + 1


def lint_skill(skill_md: Path) -> list[str]:
    skill_dir = skill_md.parent
    body = skill_md.read_text(encoding="utf-8", errors="replace")
    rel = skill_md.relative_to(REPO_ROOT)
    issues: list[str] = []

    for m in PLATFORM_VAR.finditer(body):
        issues.append(f"{rel}:{line_of(body, m.start())} platform variable '{m.group(0)}' (not portable; use a relative path)")

    for m in ESCAPE_PATH.finditer(body):
        issues.append(f"{rel}:{line_of(body, m.start())} path escapes skill dir '{m.group(0)}…' (vendor it into this skill)")

    for m in CROSS_SKILL.finditer(body):
        issues.append(f"{rel}:{line_of(body, m.start())} cross-skill reference '{m.group(0)}' (duplicate into this skill + drift-check)")

    for m in MD_LINK_LOCAL.finditer(body):
        issues.append(f"{rel}:{line_of(body, m.start())} markdown link to local file '{m.group(0)}' (use a backtick path instead)")

    for m in MD_LINK_PARENT.finditer(body):
        issues.append(f"{rel}:{line_of(body, m.start())} markdown link escapes skill dir '{m.group(0)}'")

    seen: set[str] = set()
    for lineno, span in code_and_backtick_spans(body):
        for m in RESOURCE_TOKEN.finditer(span):
            token = m.group(1)
            key = f"{lineno}:{token}"
            if key in seen:
                continue
            seen.add(key)
            target = (skill_dir / token).resolve()
            try:
                inside = target.is_relative_to(skill_dir.resolve())
            except AttributeError:  # py<3.9 safety
                inside = str(target).startswith(str(skill_dir.resolve()))
            if not inside:
                issues.append(f"{rel}:{lineno} resource path leaves skill dir '{token}'")
            elif not target.exists():
                issues.append(f"{rel}:{lineno} references missing local file '{token}' (vendor it into this skill)")

    return issues


def main(argv: list[str]) -> int:
    root = REPO_ROOT if len(argv) < 2 else (REPO_ROOT / argv[1])
    skills = find_skill_files(root)
    if not skills:
        print(f"No SKILL.md found under {root}", file=sys.stderr)
        return 1

    all_issues: list[str] = []
    for skill_md in skills:
        all_issues.extend(lint_skill(skill_md))

    if all_issues:
        print(f"PORTABILITY LINT FAILED — {len(all_issues)} issue(s) across {len(skills)} skill(s):\n")
        for issue in all_issues:
            print(f"  ✗ {issue}")
        print("\nSee AGENTS.md 'Portable Skill Contract'.")
        return 1

    print(f"PORTABILITY LINT PASSED — {len(skills)} skill(s) are cross-harness portable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
