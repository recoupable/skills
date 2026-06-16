#!/usr/bin/env python3
"""Resolver-eval runner for the recoup-records bundle.

This is the "does the RIGHT skill fire?" test from docs/fat-skills-benchmark.md
(P1) — the rarest, highest-value part of a tested skill bundle. Most people test
a skill's *output*; almost nobody tests its *routing*.

It runs in two tiers:

  STRUCTURAL (default, free, CI-safe — no LLM):
    - Every fixture's `expected` skill is real and reachable from RESOLVER.md.
    - Every `not` (adversarial-negative) skill is real (so the negative is
      meaningful, not a typo that always passes).
    - COVERAGE: every skill on disk has >= 1 positive fixture. A skill with no
      routing fixture is untested routing — fail, so fixtures keep pace with
      skills (a forward-only ratchet).

  LLM (opt-in, paid — set RECOUP_RESOLVER_EVAL_LLM=1):
    - Placeholder for the real routing eval: hand RESOLVER.md + the intent to a
      model and assert it picks `expected` (and never a `not`). Wired as a stub
      here so the harness exists; plug in the platform's model call to enable.

Fixtures: plugins/recoup-records/resolver-eval.jsonl — one JSON object per line:
    {"intent": "research Drake", "expected": "recoup-artist-research"}
    {"intent": "value it from public data, no seller files",
     "expected": "recoup-catalog-value", "not": ["recoup-deal-value"]}

Usage:
  python3 scripts/run_resolver_eval.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT / "plugins" / "recoup-records"
# Co-located with the plugin (NOT under tests/, which is gitignored) so the
# fixtures ship and CI can run them on a fresh checkout.
FIXTURES = PLUGIN / "resolver-eval.jsonl"
SKILL_TOKEN = re.compile(r"`(recoup-[a-z0-9-]+)`")


def skill_dirs() -> set[str]:
    return {p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")}


def routed_skills() -> set[str]:
    routed: set[str] = set()
    for line in (PLUGIN / "RESOLVER.md").read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("|"):
            routed.update(SKILL_TOKEN.findall(line))
    return routed


def load_fixtures() -> list[dict]:
    rows: list[dict] = []
    for i, raw in enumerate(FIXTURES.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        try:
            rows.append({"_line": i, **json.loads(raw)})
        except json.JSONDecodeError as e:
            rows.append({"_line": i, "_error": str(e)})
    return rows


def main() -> int:
    if not FIXTURES.exists():
        print(f"run_resolver_eval: missing {FIXTURES.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 2

    existing = skill_dirs()
    routed = routed_skills()
    fixtures = load_fixtures()
    problems: list[str] = []
    covered: set[str] = set()

    for fx in fixtures:
        loc = f"line {fx['_line']}"
        if "_error" in fx:
            problems.append(f"{loc}: invalid JSON — {fx['_error']}")
            continue
        intent = fx.get("intent")
        expected = fx.get("expected")
        if not intent or not expected:
            problems.append(f"{loc}: fixture needs both 'intent' and 'expected'")
            continue
        if expected not in existing:
            problems.append(f"{loc}: expected `{expected}` is not a real skill")
        elif expected not in routed:
            problems.append(f"{loc}: expected `{expected}` exists but is not routed in RESOLVER.md")
        else:
            covered.add(expected)
        for neg in fx.get("not", []):
            if neg not in existing:
                problems.append(f"{loc}: adversarial `not` skill `{neg}` does not exist (typo?)")

    # Coverage ratchet: every skill needs at least one positive routing fixture.
    uncovered = sorted(existing - covered)
    for name in uncovered:
        problems.append(f"COVERAGE: skill `{name}` has no positive routing fixture")

    positives = sum(1 for fx in fixtures if fx.get("expected") and "_error" not in fx)
    negatives = sum(len(fx.get("not", [])) for fx in fixtures if "_error" not in fx)

    if problems:
        print(f"run_resolver_eval: {len(problems)} problem(s):\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(
        f"run_resolver_eval: STRUCTURAL OK — {positives} positive fixtures + "
        f"{negatives} adversarial negatives cover all {len(existing)} skills."
    )

    if os.environ.get("RECOUP_RESOLVER_EVAL_LLM") == "1":
        print(
            "run_resolver_eval: LLM tier requested but not wired in this "
            "environment — plug a model call into the LLM section to enable "
            "true routing assertions (intent -> expected, never -> not)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
