#!/usr/bin/env python3
"""Build the consolidated ``recoup-records`` plugin — "a record label in a box".

``recoup-records`` is a single install that bundles every source plugin's
skills, agents, hooks, references, scripts, templates, and fixtures.
A user installs one plugin instead of picking among six.

It is GENERATED, never hand-edited. Edit the source plugin, then re-run this
script. CI runs it with ``--check`` so the committed bundle can never drift from
its sources.

We COPY rather than symlink on purpose: symlinks check out as plain text files
on Windows (git ``core.symlinks=false``), which silently breaks the bundled
skills. Copying is the same drift-checked-duplication pattern the rest of this
repo already uses (see ``scripts/vendored.json``).

Usage:
  python3 scripts/build_records_plugin.py           # (re)generate plugins/recoup-records
  python3 scripts/build_records_plugin.py --check    # verify it matches sources (exit 1 on drift)

Standard library only.
"""
from __future__ import annotations

import filecmp
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

# Square brand icon committed in the repo; copied into the bundle and referenced
# by the Cursor manifest's `logo` field (shows on the marketplace card).
ICON_SOURCE = REPO_ROOT / "assets" / "recoup-icon.png"
ICON_NAME = "recoup-icon.png"

# --- What we're building ---------------------------------------------------
TARGET_SLUG = "recoup-records"
TARGET_VERSION = "0.1.0"
TARGET_DISPLAY = "Recoup Records"
TARGET_DESCRIPTION = (
    "A record label in a box — one install that bundles every Recoup plugin: "
    "setup, research, deals, content, song analysis, and releases. Install this "
    "instead of picking individual plugins."
)
TARGET_LONG = (
    "The whole Recoup platform as a single plugin: artist setup and API access, "
    "music-industry research, catalog deal review, content creation, song audio "
    "analysis, and end-to-end release workflows — every skill, agent, "
    "and hook from the focused plugins, bundled together."
)
TARGET_KEYWORDS = [
    "music",
    "recoup",
    "record-label",
    "artist-management",
    "music-research",
    "catalog-deals",
    "content-creation",
    "release-management",
    "agent-skills",
]

# Source plugins, in install order (essentials first — it's the on-ramp).
SOURCE_PLUGINS = [
    "recoup-essentials",
    "recoup-research",
    "recoup-deals",
    "recoup-content",
    "recoup-song-analysis",
    "recoup-releases",
]

# Component directories flat-merged from each source plugin into the bundle.
# (No filename collisions across plugins except hooks/hooks.json, handled below.)
# NOTE: slash-`commands/` are intentionally excluded — the repo standardizes on
# skills only (see AGENTS.md "No slash-commands"). Skills auto-register a
# `/skill-name` entry on every harness, so a command layer is redundant.
COMPONENT_DIRS = (
    "skills",
    "agents",
    "references",
    "scripts",
    "templates",
    "fixtures",
)

# Per-plugin files/dirs we deliberately DO NOT bundle (the bundle gets its own).
SKIP = {"README.md", "LICENSE", ".claude-plugin", ".cursor-plugin", ".codex-plugin", "evals"}


def merge_component(src_plugin: Path, component: str, target: Path) -> None:
    """Copy ``src_plugin/component/*`` into ``target/component/`` (flat merge)."""
    src = src_plugin / component
    if not src.is_dir():
        return
    dest = target / component
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)


def merge_hooks(src_plugins: list[Path], target: Path) -> None:
    """Copy hook scripts and merge every ``hooks.json`` into one combined config.

    Each source ``hooks.json`` keys hooks by event (``SessionStart``,
    ``PreToolUse``, ``Stop``, ...). We concatenate the per-event arrays so every
    plugin's guardrails run. Script paths use ``${CLAUDE_PLUGIN_ROOT}/hooks/...``
    which still resolves correctly inside the bundle.
    """
    hooks_present = any((p / "hooks").is_dir() for p in src_plugins)
    if not hooks_present:
        return

    dest = target / "hooks"
    dest.mkdir(parents=True, exist_ok=True)

    combined_events: dict[str, list] = {}
    descriptions: list[str] = []

    for plugin in src_plugins:
        hooks_dir = plugin / "hooks"
        if not hooks_dir.is_dir():
            continue
        for item in sorted(hooks_dir.iterdir()):
            if item.name == "hooks.json":
                data = json.loads(item.read_text(encoding="utf-8"))
                if data.get("description"):
                    descriptions.append(f"[{plugin.name}] {data['description']}")
                for event, entries in data.get("hooks", {}).items():
                    combined_events.setdefault(event, []).extend(entries)
            else:
                shutil.copy2(item, dest / item.name)

    if combined_events:
        merged = {"description": " ".join(descriptions), "hooks": combined_events}
        (dest / "hooks.json").write_text(
            json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


def merge_requirements(src_plugins: list[Path], target: Path) -> None:
    """Union every plugin's ``requirements.txt`` into one (dedup, preserve order)."""
    seen: set[str] = set()
    lines: list[str] = []
    for plugin in src_plugins:
        req = plugin / "requirements.txt"
        if not req.is_file():
            continue
        for line in req.read_text(encoding="utf-8").splitlines():
            key = line.strip()
            if key and key not in seen:
                seen.add(key)
                lines.append(line)
    if lines:
        (target / "requirements.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifests(target: Path) -> None:
    """Write the three per-harness manifests for the bundle."""
    author = {"name": "Recoup", "email": "agent@recoupable.com", "url": "https://recoupable.com"}
    common = {
        "name": TARGET_SLUG,
        "version": TARGET_VERSION,
        "description": TARGET_DESCRIPTION,
        "author": author,
        "homepage": "https://recoupable.com",
        "repository": "https://github.com/recoupable/skills",
        "license": "Apache-2.0",
        "keywords": TARGET_KEYWORDS,
    }

    # Claude Code: skills/commands/agents/hooks are auto-discovered from the root.
    (target / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    _write_json(target / ".claude-plugin" / "plugin.json", common)

    # Cursor: list component paths explicitly + the card logo.
    cursor = dict(common)
    cursor.update(
        {
            "logo": f"assets/{ICON_NAME}",
            "skills": "./skills/",
            "agents": "./agents/",
        }
    )
    (target / ".cursor-plugin").mkdir(parents=True, exist_ok=True)
    _write_json(target / ".cursor-plugin" / "plugin.json", cursor)

    # Codex: skills path + interface block.
    codex = dict(common)
    codex.update(
        {
            "skills": "./skills/",
            "interface": {
                "displayName": TARGET_DISPLAY,
                "shortDescription": "A record label in a box",
                "longDescription": TARGET_LONG,
                "developerName": "Recoup",
                "category": "Music",
                "capabilities": ["Read", "Write"],
                "websiteURL": "https://recoupable.com",
            },
        }
    )
    (target / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    _write_json(target / ".codex-plugin" / "plugin.json", codex)


def write_readme(target: Path) -> None:
    rows = "\n".join(f"| {p} | bundled |" for p in SOURCE_PLUGINS)
    body = f"""# Recoup — Record Label in a Box

> **Generated bundle. Do not edit by hand.** This plugin is built from the
> individual Recoup plugins by `scripts/build_records_plugin.py`. Edit the source
> plugin, then re-run the generator.

{TARGET_LONG}

One install gives you everything below. Prefer a focused install? Install the
individual plugin instead — same skills, smaller surface.

| Source plugin | Status |
|---------------|--------|
{rows}

## Install

```bash
/plugin marketplace add recoupable/skills
/plugin install {TARGET_SLUG}@recoup
```

## Regenerate

```bash
python3 scripts/build_records_plugin.py          # rebuild
python3 scripts/build_records_plugin.py --check   # verify no drift (CI)
```
"""
    (target / "README.md").write_text(body, encoding="utf-8")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    src_plugins = [PLUGINS_DIR / name for name in SOURCE_PLUGINS]
    for plugin in src_plugins:
        if not plugin.is_dir():
            raise SystemExit(f"source plugin not found: {plugin.relative_to(REPO_ROOT)}")
        for component in COMPONENT_DIRS:
            merge_component(plugin, component, target)

    merge_hooks(src_plugins, target)
    merge_requirements(src_plugins, target)
    write_manifests(target)
    write_readme(target)
    shutil.copy2(REPO_ROOT / "LICENSE", target / "LICENSE")

    if not ICON_SOURCE.is_file():
        raise SystemExit(f"icon not found: {ICON_SOURCE.relative_to(REPO_ROOT)}")
    (target / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ICON_SOURCE, target / "assets" / ICON_NAME)


def _diff(a: Path, b: Path) -> list[str]:
    """Return human-readable differences between two directory trees."""
    cmp = filecmp.dircmp(a, b)
    diffs: list[str] = []

    def walk(c: filecmp.dircmp, prefix: str) -> None:
        for name in c.left_only:
            diffs.append(f"  - only in committed: {prefix}{name}")
        for name in c.right_only:
            diffs.append(f"  - only in freshly-built: {prefix}{name}")
        for name in c.diff_files:
            diffs.append(f"  - differs: {prefix}{name}")
        for name, sub in c.subdirs.items():
            walk(sub, f"{prefix}{name}/")

    walk(cmp, "")
    return diffs


def check(target: Path) -> int:
    if not target.exists():
        print(f"BUILD CHECK FAILED — {target.relative_to(REPO_ROOT)} does not exist. Run the generator.")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / TARGET_SLUG
        build(fresh)
        diffs = _diff(target, fresh)
    if diffs:
        print(f"BUILD CHECK FAILED — {target.relative_to(REPO_ROOT)} is out of date:\n")
        print("\n".join(diffs))
        print("\nRe-run: python3 scripts/build_records_plugin.py")
        return 1
    print(f"BUILD CHECK PASSED — {target.relative_to(REPO_ROOT)} matches its sources.")
    return 0


def main(argv: list[str]) -> int:
    target = PLUGINS_DIR / TARGET_SLUG
    if "--check" in argv:
        return check(target)
    build(target)
    skills = len(list((target / "skills").glob("*/SKILL.md")))
    print(f"BUILT {target.relative_to(REPO_ROOT)} — {skills} skills from {len(SOURCE_PLUGINS)} plugins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
