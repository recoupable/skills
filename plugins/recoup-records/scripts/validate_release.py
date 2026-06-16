#!/usr/bin/env python3
"""Release-workspace completion validator (the trust/completion contract).

Checks that a release workspace is actually complete before anyone calls it
"ready". Exit 0 when complete, 1 when incomplete (so a hook or CI can gate on it).
Stdlib only — assumptions.yaml is parsed as simple `key: value` lines, not full YAML.

Usage:
    python3 scripts/validate_release.py releases/gatsby-grace/blue-slide-park
"""
import json
import os
import sys

REQUIRED_ASSUMPTIONS = ["artist", "release_title", "release_date", "creative_direction"]


def parse_simple_yaml(path):
    """Parse `key: value` lines into a dict. Good enough for the flat assumptions file."""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.split("#", 1)[0].rstrip()
            if not line or line.startswith(" ") or ":" not in line:
                continue
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip()
    return out


def has_real_md(folder):
    """True if the folder holds at least one non-placeholder .md file."""
    if not os.path.isdir(folder):
        return False
    for name in os.listdir(folder):
        if name.endswith(".md") and os.path.getsize(os.path.join(folder, name)) > 0:
            return True
    return False


def validate(workspace):
    present, missing, warnings = [], [], []

    assumptions = os.path.join(workspace, "assumptions.yaml")
    if os.path.isfile(assumptions):
        present.append("assumptions.yaml")
        data = parse_simple_yaml(assumptions)
        empty = [k for k in REQUIRED_ASSUMPTIONS if not data.get(k)]
        if empty:
            missing.append(f"assumptions.yaml fields empty: {', '.join(empty)}")
    else:
        missing.append("assumptions.yaml")

    release_md = os.path.join(workspace, "RELEASE.md")
    if os.path.isfile(release_md):
        present.append("RELEASE.md")
        with open(release_md, encoding="utf-8") as fh:
            body = fh.read()
        if "## 1. Project Snapshot" not in body:
            warnings.append("RELEASE.md is missing the Project Snapshot section")
    else:
        missing.append("RELEASE.md")

    if has_real_md(os.path.join(workspace, "brief")):
        present.append("brief/")
    else:
        missing.append("brief/ (no creative brief written)")

    if has_real_md(os.path.join(workspace, "campaign")):
        present.append("campaign/")
    else:
        missing.append("campaign/ (no dated timeline written)")

    status = "ok" if not missing else "incomplete"
    return {"workspace": workspace, "status": status,
            "present": present, "missing": missing, "warnings": warnings}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print(json.dumps({"error": "usage: validate_release.py <workspace-path>"}))
        return 2
    workspace = argv[0]
    if not os.path.isdir(workspace):
        print(json.dumps({"workspace": workspace, "status": "incomplete",
                          "present": [], "missing": ["workspace does not exist"], "warnings": []}))
        return 1
    result = validate(workspace)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
