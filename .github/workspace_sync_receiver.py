#!/usr/bin/env python3
"""Trusted-main receiver for repository-scoped, SSH-signed sync proposals."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile


def run(*args, cwd=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Receiver command failed: " + args[0])
    return result.stdout.strip()


def allowed(role, path):
    p = PurePosixPath(path)
    if not p.parts or p.is_absolute() or str(p) != path or ".." in p.parts or any(ord(c) < 32 for c in path):
        return False
    if role == "mono":
        return path in {"business", "skills"}
    manifests = {".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/marketplace.json"}
    if role == "skills":
        return (path.startswith("skills/recoup-internal-consulting-") or path in manifests |
                {".agents/plugins/marketplace.json", "RESOLVER.md", "resolver-eval.jsonl"})
    if role == "plugin":
        return path.startswith("skills/") or path in manifests | {".cursor-plugin/plugin.json", ".cursor-plugin/marketplace.json"}
    if role == "os" and (path == "plugin" or path in {"integrations/sharing/sync-state.json",
            "integrations/sharing/reviewed.json", "integrations/sharing/skill-names.json"} or
            path.startswith("integrations/sharing/overlays/")):
        return True
    if role == "business" and path == ".shared-export.json":
        return True
    if role == "os" and path in {"DESIGN.md", "README.md"}:
        return True
    if p.parts[0].startswith(".") or p.parts[0] in {"evals", "agents", "plugin", "memory", "work"}:
        return False
    if "_work" in p.parts or path.startswith("integrations/sharing/"):
        return False
    return p.parts[0] in {"clients", "pipeline", "signals", "knowledge", "library", "content", "proof",
        "positioning", "business", "products", "swipe", "email", "workflows", "routines", "docs", "integrations"} or (
        role == "business" and path in {"AGENTS.md", "CLAUDE.md", "README.md", "DESIGN.md", "skills/quarterly-value-review.md"})


def api(endpoint, payload=None):
    args = ["gh", "api", endpoint]
    if payload is not None:
        args += ["--method", "POST", "--input", "-"]
    result = subprocess.run(args, input=None if payload is None else json.dumps(payload),
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("GitHub receiver API request failed")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=["os", "plugin", "business", "skills", "mono"], required=True)
    args = parser.parse_args()
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    workflow = event["workflow_run"]
    repo = os.environ["GITHUB_REPOSITORY"]
    branch, head = workflow["head_branch"], workflow["head_sha"]
    if (workflow["conclusion"] != "success" or workflow["head_repository"]["full_name"] != repo or
            not re.fullmatch(r"codex/sync-[a-f0-9]{20}", branch) or not re.fullmatch(r"[a-f0-9]{40}", head)):
        raise RuntimeError("Untrusted sync run")
    # The workflow and receiver are checked out from main, never from the proposal.
    run("git", "fetch", "origin", head)
    main_head = api("repos/" + repo + "/git/ref/heads/main")["object"]["sha"]
    parent = run("git", "rev-parse", head + "^")
    if parent != main_head:
        print("Target main moved; coordinator will build a fresh proposal next run.")
        return
    if run("git", "rev-list", "--count", main_head + ".." + head) != "1":
        raise RuntimeError("A sync proposal must contain exactly one target-local commit")
    run("git", "-c", "gpg.ssh.allowedSignersFile=.github/sync-allowed-signers", "verify-commit", head)
    paths = run("git", "diff", "--name-only", "--no-renames", parent, head).splitlines()
    if not paths or any(not allowed(args.role, p) for p in paths):
        raise RuntimeError("Sync proposal touches a protected path")
    for line in run("git", "diff", "--raw", "--no-renames", parent, head).splitlines():
        fields = line.split()
        mode = fields[1]
        path = line.split("\t", 1)[1]
        if mode not in {"000000", "100644", "100755"} and not (
                mode == "160000" and path in ({"business", "skills"} if args.role == "mono" else {"plugin"} if args.role == "os" else set())):
            raise RuntimeError("Sync proposal contains an unsupported file mode")
    existing = api("repos/" + repo + "/pulls?state=open&head=" + repo.split("/")[0] + ":" + branch)
    if existing:
        pr = existing[0]
    else:
        pr = api("repos/" + repo + "/pulls", {"title": "Sync reviewed workspace changes", "head": branch, "base": "main",
            "body": "Automatically prepared by the private workspace coordinator. The signed proposal passed this repository's sync validation. Only approved file changes are included; repository history is kept separate."})
    # GitHub enforces branch protections. --auto queues required checks instead of bypassing them.
    run("gh", "pr", "merge", str(pr["number"]), "--repo", repo, "--squash", "--auto", "--match-head-commit", head)
    print("Validated sync PR: " + pr["html_url"])


if __name__ == "__main__":
    main()
