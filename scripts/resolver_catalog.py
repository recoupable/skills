"""Shared filesystem and resolver-table inventory for structural routing gates."""
from __future__ import annotations

import re
from pathlib import Path

# A skill reference in RESOLVER.md is a backtick-wrapped slug, including user-named skills.
# Dots are allowed mid-slug (e.g. `recoup-internal-video-grok-1.5-imagine-facetime`).
SKILL_TOKEN = re.compile(r"`([a-z][a-z0-9]*-[a-z0-9-]+(?:\.[a-z0-9-]+)*)`")


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
