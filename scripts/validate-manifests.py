#!/usr/bin/env python3
"""
Validate every marketplace, plugin manifest, and skill in this repo.

Checks performed:
  1. Generated marketplace files match marketplace.source.json
     (delegates to `generate-marketplaces.py --check`).
  2. Each plugin's `source` path resolves to an existing directory.
  3. Each `skills` entry in a virtual marketplace plugin resolves to a real
     skill folder with a valid SKILL.md (frontmatter: name + description).
  4. Each self-contained plugin folder under `plugins/` exposes the expected
     manifests (`.claude-plugin/plugin.json` + `.codex-plugin/plugin.json`).
  5. Every SKILL.md under skills/ has `name` and `description` frontmatter.

Zero external dependencies. Python 3.9+ stdlib only.

Exit code 0 = all OK. Non-zero = at least one validation error printed to stderr.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = REPO_ROOT / "marketplace.source.json"

CLAUDE_MP = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MP = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_MP = REPO_ROOT / ".cursor-plugin" / "marketplace.json"

ROOT_SKILLS_DIR = REPO_ROOT / "skills"
PLUGINS_DIR = REPO_ROOT / "plugins"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FRONTMATTER_FIELD_RE = re.compile(r"^([A-Za-z_][\w-]*)\s*:\s*(.+?)\s*$", re.MULTILINE)


class ValidationError(Exception):
    """Single named validation failure."""


def report(errors: list[str], msg: str) -> None:
    errors.append(msg)
    print(f"  ✗ {msg}", file=sys.stderr)


def check_generator(errors: list[str]) -> None:
    print("→ checking marketplace generator parity")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "generate-marketplaces.py"), "--check"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        report(errors, f"generated marketplace files are out of sync. {result.stderr.strip()}")


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text()
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValidationError(f"{skill_md.relative_to(REPO_ROOT)}: missing YAML frontmatter")
    fields: dict[str, str] = {}
    for m in FRONTMATTER_FIELD_RE.finditer(match.group(1)):
        fields[m.group(1)] = m.group(2)
    return fields


def check_skill(skill_dir: Path, errors: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    rel = skill_dir.relative_to(REPO_ROOT)
    if not skill_md.exists():
        report(errors, f"{rel}: SKILL.md missing")
        return
    try:
        fields = parse_frontmatter(skill_md)
    except ValidationError as exc:
        report(errors, str(exc))
        return
    if not fields.get("name"):
        report(errors, f"{rel}/SKILL.md: frontmatter missing `name`")
    if not fields.get("description"):
        report(errors, f"{rel}/SKILL.md: frontmatter missing `description`")


def check_root_skills(errors: list[str]) -> None:
    print(f"→ checking skills under {ROOT_SKILLS_DIR.relative_to(REPO_ROOT)}/")
    if not ROOT_SKILLS_DIR.exists():
        return
    for entry in sorted(ROOT_SKILLS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            check_skill(entry, errors)


def check_plugin_dir(plugin_dir: Path, errors: list[str]) -> None:
    rel = plugin_dir.relative_to(REPO_ROOT)
    claude = plugin_dir / ".claude-plugin" / "plugin.json"
    codex = plugin_dir / ".codex-plugin" / "plugin.json"
    if not claude.exists():
        report(errors, f"{rel}: missing .claude-plugin/plugin.json")
    if not codex.exists():
        report(errors, f"{rel}: missing .codex-plugin/plugin.json")
    # Walk every SKILL.md inside the plugin's skills folder.
    plugin_skills = plugin_dir / "skills"
    if plugin_skills.exists():
        for entry in sorted(plugin_skills.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                check_skill(entry, errors)


def check_self_contained_plugins(errors: list[str]) -> None:
    if not PLUGINS_DIR.exists():
        return
    print(f"→ checking plugins under {PLUGINS_DIR.relative_to(REPO_ROOT)}/")
    for entry in sorted(PLUGINS_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            check_plugin_dir(entry, errors)


def check_source_paths(errors: list[str]) -> None:
    print("→ checking marketplace.source.json plugin paths")
    with SOURCE_FILE.open() as fh:
        data = json.load(fh)
    for plugin in data.get("plugins", []):
        name = plugin["name"]
        source = plugin["source"]
        target = (REPO_ROOT / source).resolve()
        if not target.exists():
            report(errors, f"plugin `{name}`: source path `{source}` does not exist")
        if plugin.get("type") == "virtual":
            for skill_path in plugin.get("skills", []):
                resolved = (REPO_ROOT / skill_path).resolve()
                if not resolved.exists():
                    report(errors, f"plugin `{name}`: skill path `{skill_path}` does not exist")


def main() -> int:
    errors: list[str] = []

    check_generator(errors)
    check_source_paths(errors)
    check_root_skills(errors)
    check_self_contained_plugins(errors)

    print()
    if errors:
        print(f"✗ {len(errors)} validation error(s)", file=sys.stderr)
        return 1
    print("✓ all manifests valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
