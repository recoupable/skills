#!/usr/bin/env python3
"""Build a reproducible ZIP from a committed Git tree, never local workspace files.

Usage: python3 scripts/package_plugin.py --output /tmp/recoup-skills.zip
All skills and their supporting files are preserved. No submission is performed.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = {
    "skills", "agents", "references", "templates", "fixtures", "assets",
    ".claude-plugin", ".codex-plugin", ".cursor-plugin", ".agents",
    ".mcp.json", "mcp.json", "gemini-extension.json", "README.md", "LICENSE",
    "RESOLVER.md", "resolver-eval.jsonl", "scripts", "DISTRIBUTION.md",
}


def build(output: Path, ref: str) -> dict:
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=ROOT, text=True
    ).strip()
    archive = subprocess.check_output(["git", "archive", commit], cwd=ROOT)
    files = {}
    modes = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        for item in source:
            path = Path(item.name)
            if path.parts[0] not in COMPONENTS:
                continue
            if item.isdir():
                continue
            if not item.isfile() or path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Unsafe package member: {item.name}")
            files[item.name] = source.extractfile(item).read()
            modes[item.name] = item.mode
    for required in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
                     ".cursor-plugin/plugin.json", ".mcp.json", "mcp.json",
                     "gemini-extension.json", "README.md", "LICENSE"):
        if required not in files:
            raise ValueError(f"Missing required file: {required}")
    skills = sorted(name for name in files if name.startswith("skills/") and name.endswith("/SKILL.md"))
    if not skills:
        raise ValueError("No skills found")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidentally replacing an existing artifact.
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100000 | modes[name]) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, data)
    with zipfile.ZipFile(output) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
        for name, data in files.items():
            if bundle.read(name) != data:
                raise ValueError(f"Content mismatch: {name}")
    return {"commit": commit, "path": str(output.resolve()), "files": len(files),
            "skills": len(skills), "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.ref), indent=2))
