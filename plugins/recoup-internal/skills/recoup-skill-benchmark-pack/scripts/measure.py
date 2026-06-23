#!/usr/bin/env python3
"""Measure any skill pack (plugin or skills folder) against the frontier bar.

This is the *deterministic* half of the recoup-skill-benchmark-pack skill: it counts
what can be counted exactly so the agent never eyeballs (and mis-guesses) the
numbers. It is harness-agnostic and reads only the target you point it at — it
makes no network calls and writes nothing except its report.

What it measures (per the fat-skills benchmark methodology):
  * skill count + SKILL.md *body* line distribution (min / median / max + bands)
  * per-skill footprint = body + co-located references + co-located scripts
  * the always-loaded "catalog" cost (sum of frontmatter descriptions, ~tokens)
  * pack-level signals the frontier treats as the *definition* of a skill pack:
      - deterministic substrate (scripts), unit/integration tests, LLM evals,
        resolver / routing tests, reachability gate, hooks, learnings store,
        multi-surface distribution manifests
  * candidate description overlaps (where implicit routing may mis-fire)

Usage:
  python3 scripts/measure.py <path>                 # human-readable report
  python3 scripts/measure.py <path> --json          # machine-readable JSON
  python3 scripts/measure.py <path> --json -o m.json # JSON to a file

<path> may be a single plugin dir, a folder of skills, or a whole repo.
Standard library only; works on Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# ── File-type buckets ────────────────────────────────────────────────────────
CODE_EXT = {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".sh", ".bash", ".rb", ".go", ".rs"}
DOC_EXT = {".md", ".mdx", ".txt", ".rst"}

# A SKILL.md body line band → role hint (see references/frontier-benchmark.md §"how fat is fat").
BANDS = [
    ("tiny", 0, 99),        # utility / toggle / demonstration
    ("leaf", 100, 399),     # reusable single-task leaf (references-backed)
    ("deep", 400, 799),     # approaching a deep capability skill
    ("fat", 800, 10**9),    # frontier-grade deep capability / orchestrator body
]

# Pack-level signal detectors. Each maps a label → (filename/dirname regex,
# whether it matches directory names too). Matched case-insensitively against
# the path's parts and final name.
TEST_RE = re.compile(r"(\.test\.[a-z]+$)|(^test_.*\.py$)|(_test\.py$)|(\.spec\.[a-z]+$)", re.I)
EVAL_RE = re.compile(r"eval", re.I)
# A *routing test/table* — not just any file with "resolver" in the name (a
# reference doc like `account-resolver.md` is not a routing test).
RESOLVER_FILE_RE = re.compile(
    r"^RESOLVER\.md$|routing[-_]?eval|routing.*\.jsonl|resolver.*(\.test\.|\.spec\.|eval)|check[-_]resolvable",
    re.I,
)
REACHABLE_RE = re.compile(r"check[-_]resolvable|reachab", re.I)
LEARNINGS_RE = re.compile(r"learnings|solutions", re.I)
HOOKS_RE = re.compile(r"^hooks\.json$", re.I)
MANIFEST_DIRS = {".claude-plugin", ".cursor-plugin", ".codex-plugin", ".agents"}

# Directories never worth walking into.
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next"}


def _count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def _walk_files(root: Path):
    """Yield every file under root, skipping noise directories."""
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def parse_frontmatter(text: str):
    """Return (frontmatter_dict_lite, body_text). Only name + description matter.

    Hand-rolled (no PyYAML) so the script stays stdlib-only. Handles the two
    common shapes: inline `description: ...` and folded `description: >-`.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])

    name = ""
    description = ""
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        m = re.match(r"^(name|description)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-", ""):
            # Folded/literal block: gather subsequent more-indented lines.
            block = []
            base_indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(fm_lines):
                nxt = fm_lines[j]
                if nxt.strip() == "":
                    block.append("")
                    j += 1
                    continue
                indent = len(nxt) - len(nxt.lstrip())
                if indent <= base_indent:
                    break
                block.append(nxt.strip())
                j += 1
            val = " ".join(s for s in block if s != "").strip()
            i = j
        else:
            val = val.strip().strip('"').strip("'")
            i += 1
        if key == "name":
            name = val
        else:
            description = val
    return {"name": name, "description": description}, body


def measure_skill(skill_md: Path):
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    body_lines = len(body.splitlines())
    skill_dir = skill_md.parent

    ref_lines = ref_files = 0
    script_lines = script_files = 0
    for sub, exts, kind in (("references", DOC_EXT, "ref"), ("scripts", CODE_EXT, "script")):
        d = skill_dir / sub
        if not d.is_dir():
            continue
        for f in d.rglob("*"):
            if f.is_file() and f.suffix.lower() in exts:
                n = _count_lines(f)
                if kind == "ref":
                    ref_lines += n
                    ref_files += 1
                else:
                    script_lines += n
                    script_files += 1

    name = fm.get("name") or skill_dir.name
    desc = fm.get("description", "")
    band = next(b for b, lo, hi in BANDS if lo <= body_lines <= hi)
    return {
        "name": name,
        "dir": str(skill_dir),
        "body_lines": body_lines,
        "band": band,
        "ref_lines": ref_lines,
        "ref_files": ref_files,
        "script_lines": script_lines,
        "script_files": script_files,
        "total_lines": body_lines + ref_lines + script_lines,
        "description": desc,
        "description_chars": len(desc),
        "has_triggers": bool(re.search(r"\b(use when|trigger|when the user|proactively)\b", desc, re.I)),
    }


def detect_signals(root: Path):
    """Scan the whole target tree for pack-level signals (defining properties)."""
    sig = {
        "test_files": [], "eval_files": [], "resolver_files": [],
        "reachability_files": [], "learnings_paths": [], "hooks_files": [],
        "distribution_manifests": [], "deterministic_scripts": 0,
    }
    seen_manifest_dirs = set()
    for p in _walk_files(root):
        rel = str(p.relative_to(root))
        name = p.name
        if TEST_RE.search(name):
            sig["test_files"].append(rel)
        if EVAL_RE.search(name) and p.suffix.lower() in (CODE_EXT | {".jsonl", ".json"}):
            sig["eval_files"].append(rel)
        if RESOLVER_FILE_RE.search(name):
            sig["resolver_files"].append(rel)
        if REACHABLE_RE.search(name):
            sig["reachability_files"].append(rel)
        if HOOKS_RE.search(name):
            sig["hooks_files"].append(rel)
        if p.suffix.lower() in CODE_EXT and not TEST_RE.search(name) and "/scripts/" in f"/{rel}":
            sig["deterministic_scripts"] += 1
        # learnings store: a docs/solutions dir or a learnings.* file
        if LEARNINGS_RE.search(rel) and ("solutions" in rel.lower() or "learnings" in name.lower()):
            top = rel.split("/")[0:3]
            sig["learnings_paths"].append("/".join(top))
        # distribution manifests
        for part in p.parts:
            if part in MANIFEST_DIRS and part not in seen_manifest_dirs:
                seen_manifest_dirs.add(part)
                sig["distribution_manifests"].append(part)

    # de-dup + cap noisy lists for readability
    sig["learnings_paths"] = sorted(set(sig["learnings_paths"]))
    sig["distribution_manifests"] = sorted(set(sig["distribution_manifests"]))
    return sig


_WORD_RE = re.compile(r"[a-z0-9']+")
_STOP = set("the a an and or of to for with use when this that is are be it as on in by your you i we our skill skills user".split())


def _desc_words(desc: str):
    return {w for w in _WORD_RE.findall(desc.lower()) if w not in _STOP and len(w) > 2}


def overlap_pairs(skills, threshold=0.45):
    """Flag skill description pairs with high word-overlap (Jaccard) — places
    where the implicit description-resolver is most likely to mis-fire."""
    pairs = []
    sets = [(s["name"], _desc_words(s["description"])) for s in skills]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            a, sa = sets[i]
            b, sb = sets[j]
            if not sa or not sb:
                continue
            inter = len(sa & sb)
            union = len(sa | sb)
            jac = inter / union if union else 0.0
            if jac >= threshold:
                pairs.append({"a": a, "b": b, "jaccard": round(jac, 2)})
    return sorted(pairs, key=lambda x: -x["jaccard"])


def build_report(root: Path):
    skill_files = sorted(root.rglob("SKILL.md"))
    skill_files = [s for s in skill_files if not any(part in SKIP_DIRS for part in s.parts)]
    skills = [measure_skill(s) for s in skill_files]
    bodies = [s["body_lines"] for s in skills] or [0]
    band_counts = {b: 0 for b, _, _ in BANDS}
    for s in skills:
        band_counts[s["band"]] += 1
    catalog_chars = sum(s["description_chars"] for s in skills)
    return {
        "target": str(root),
        "skill_count": len(skills),
        "body_lines": {
            "min": min(bodies),
            "median": int(statistics.median(bodies)),
            "max": max(bodies),
        },
        "bands": band_counts,
        "catalog": {
            "description_chars": catalog_chars,
            "est_tokens": round(catalog_chars / 4),
            "budget_tokens": 7000,
            "over_budget": (catalog_chars / 4) > 7000,
        },
        "signals": detect_signals(root),
        "overlap_candidates": overlap_pairs(skills),
        "skills": sorted(skills, key=lambda s: -s["total_lines"]),
    }


def _has(lst):
    return f"YES ({len(lst)})" if lst else "— none"


def print_report(r):
    out = print
    out(f"\nSKILL PACK BENCHMARK — {r['target']}")
    out("=" * 72)
    out(f"Skills: {r['skill_count']}    "
        f"SKILL.md body lines  min/median/max = "
        f"{r['body_lines']['min']}/{r['body_lines']['median']}/{r['body_lines']['max']}")
    b = r["bands"]
    out(f"Body-size bands:  tiny<100={b['tiny']}  leaf 100-399={b['leaf']}  "
        f"deep 400-799={b['deep']}  fat 800+={b['fat']}")
    c = r["catalog"]
    flag = "  ⚠ OVER ~7K BUDGET" if c["over_budget"] else "  (within ~7K budget)"
    out(f"Always-loaded catalog (descriptions): ~{c['est_tokens']} tokens{flag}")

    out("\nPack-level signals (the frontier's defining properties of a skill pack):")
    s = r["signals"]
    out(f"  deterministic substrate (scripts)  : {s['deterministic_scripts']} script file(s)")
    out(f"  unit / integration tests           : {_has(s['test_files'])}")
    out(f"  LLM-as-judge evals                 : {_has(s['eval_files'])}")
    out(f"  resolver / routing tests           : {_has(s['resolver_files'])}")
    out(f"  reachability gate (check-resolvable): {_has(s['reachability_files'])}")
    out(f"  hooks layer                        : {_has(s['hooks_files'])}")
    out(f"  compounding learnings store        : {_has(s['learnings_paths'])}")
    out(f"  multi-surface distribution         : {', '.join(s['distribution_manifests']) or '— none'}")

    if r["overlap_candidates"]:
        out("\nDescription-overlap candidates (implicit routing may mis-fire — test these):")
        for p in r["overlap_candidates"][:12]:
            out(f"  {p['jaccard']:>4}  {p['a']}  ⇄  {p['b']}")

    out("\nPer-skill footprint (body + co-located refs + scripts), fattest first:")
    out(f"  {'skill':<34}{'body':>6}{'refs':>7}{'scripts':>9}{'total':>8}  band")
    for sk in r["skills"]:
        out(f"  {sk['name'][:33]:<34}{sk['body_lines']:>6}{sk['ref_lines']:>7}"
            f"{sk['script_lines']:>9}{sk['total_lines']:>8}  {sk['band']}")
    out("\nNext: score these against references/scorecard.md and read"
        " references/frontier-benchmark.md for the bar + what to steal.\n")


def main(argv):
    ap = argparse.ArgumentParser(description="Measure a skill pack against the frontier bar.")
    ap.add_argument("path", help="plugin dir, skills folder, or repo root to measure")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a human report")
    ap.add_argument("-o", "--out", help="write JSON to this file (implies --json)")
    args = ap.parse_args(argv)

    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    report = build_report(root)
    if report["skill_count"] == 0:
        print(f"No SKILL.md found under {root}", file=sys.stderr)
        return 1

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    elif args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
