#!/usr/bin/env python3
"""Resolver-eval runner for the Recoup Skills plugin (repo root).

This is the "does the RIGHT skill fire?" test — the rarest, highest-value part
of a tested skill bundle. Most people test a skill's *output*; almost nobody
tests its *routing*.

It runs in two tiers:

  STRUCTURAL (default, free, CI-safe — no LLM):
    - Every fixture's `expected` skill is real and reachable from RESOLVER.md.
    - Every `not` (adversarial-negative) skill is real (so the negative is
      meaningful, not a typo that always passes).
    - COVERAGE: every skill on disk has >= 1 positive fixture. A skill with no
      routing fixture is untested routing — fail, so fixtures keep pace with
      skills (a forward-only ratchet).

  LLM (opt-in, paid — set RECOUP_RESOLVER_EVAL_LLM=1):
    - The real routing test: for each fixture, hand a model the fat-skill
      descriptions (the Stage-1 trigger surface a harness actually sees) + the
      intent, and assert it routes to `expected` and never a `not`. Calls the
      Vercel AI Gateway (same path as the api repo) over its OpenAI-compatible
      HTTP endpoint — stdlib only. Needs AI_GATEWAY_API_KEY (or
      VERCEL_AI_GATEWAY_API_KEY). Prints a pass-rate + mis-route report; exits
      non-zero below RECOUP_RESOLVER_EVAL_MIN_PASS (default 1.0). Tunables:
      RECOUP_RESOLVER_EVAL_MODEL (default openai/gpt-5.4-nano), AI_GATEWAY_BASE_URL.

Fixtures: resolver-eval.jsonl (repo root) — one JSON object per line:
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
import ssl
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = REPO_ROOT
# Co-located with the plugin root (NOT under tests/, which is gitignored) so the
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


# --- LLM tier (opt-in) -----------------------------------------------------
GATEWAY_BASE_URL = os.environ.get("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1")
GATEWAY_MODEL = os.environ.get("RECOUP_RESOLVER_EVAL_MODEL", "openai/gpt-5.4-nano")
GATEWAY_KEY = os.environ.get("AI_GATEWAY_API_KEY") or os.environ.get("VERCEL_AI_GATEWAY_API_KEY")
MIN_PASS = float(os.environ.get("RECOUP_RESOLVER_EVAL_MIN_PASS", "1.0"))
FRONTMATTER_KEY = re.compile(r"^([A-Za-z][\w-]*):\s?(.*)$")
SKILL_TOKEN_PLAIN = re.compile(r"recoup-[a-z0-9-]+")


def _gateway_ssl_context() -> ssl.SSLContext:
    """Verify TLS against certifi's CA bundle when available (fixes the macOS
    'CERTIFICATE_VERIFY_FAILED' where Python can't see the system roots); fall
    back to the stdlib default elsewhere. certifi stays an optional import."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_GATEWAY_SSL = _gateway_ssl_context()


def _parse_description(text: str) -> str:
    """Pull the frontmatter `description` (inline or block scalar) from a SKILL.md."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text
    desc: list[str] = []
    capturing = False
    for line in fm.splitlines():
        if capturing:
            if line.strip() == "" or line[:1] in (" ", "\t"):
                desc.append(line.strip())
                continue
            break
        m = FRONTMATTER_KEY.match(line)
        if m and m.group(1) == "description":
            val = m.group(2).strip()
            if val and val[0] not in (">", "|"):
                return val.strip("\"'")
            capturing = True
    return " ".join(p for p in desc if p).strip()


def skill_descriptions() -> dict[str, str]:
    """Each skill (dir name) -> its frontmatter description (the Stage-1 trigger)."""
    return {
        md.parent.name: _parse_description(md.read_text(encoding="utf-8"))
        for md in sorted((PLUGIN / "skills").glob("*/SKILL.md"))
    }


def _call_gateway(intent: str, catalog: str) -> str:
    """Route one intent via the gateway. Returns the raw reply (or '__ERROR__: ...')."""
    system = (
        "You are the skill router for the Recoup Skills plugin. Given a USER "
        "REQUEST and a catalog of skills (name: description), choose the SINGLE "
        "best skill. Reply with ONLY the skill name (e.g. recoup-research); reply "
        "none if nothing fits."
    )
    user = f"SKILLS:\n{catalog}\n\nUSER REQUEST: {intent}\n\nBest skill name:"
    body = json.dumps(
        {
            "model": GATEWAY_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{GATEWAY_BASE_URL}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {GATEWAY_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90, context=_GATEWAY_SSL) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"] or ""
    except Exception as e:  # surface failures as errored fixtures, never crash the run
        return f"__ERROR__: {e}"


def _picked_skill(reply: str, known: set[str]) -> str:
    """Extract the routed skill slug from a (possibly chatty) model reply."""
    for tok in SKILL_TOKEN_PLAIN.findall(reply):
        if tok in known:
            return tok
    return "none"


def run_llm_tier(fixtures: list[dict], existing: set[str]) -> int:
    if not GATEWAY_KEY:
        print(
            "run_resolver_eval: LLM tier requested but no gateway key — set "
            "AI_GATEWAY_API_KEY (or VERCEL_AI_GATEWAY_API_KEY). Structural tier passed.",
            file=sys.stderr,
        )
        return 0
    descriptions = skill_descriptions()
    catalog = "\n".join(f"- {n}: {d}" for n, d in sorted(descriptions.items()))
    cases = [
        fx for fx in fixtures if fx.get("intent") and fx.get("expected") and "_error" not in fx
    ]
    print(
        f"run_resolver_eval: LLM tier — routing {len(cases)} intents via "
        f"{GATEWAY_MODEL} (Stage-1: descriptions only)\n"
    )
    passed = 0
    failures: list[str] = []
    for i, fx in enumerate(cases, 1):
        reply = _call_gateway(fx["intent"], catalog)
        got = _picked_skill(reply, existing)
        expected = fx["expected"]
        nots = set(fx.get("not", []))
        ok = got == expected and got not in nots
        if ok:
            passed += 1
        else:
            why = (
                "API error"
                if reply.startswith("__ERROR__")
                else "hit a `not`"
                if got in nots
                else "mis-route"
            )
            failures.append(
                f'  ✗ [{why}] "{fx["intent"]}" → got `{got}`, expected `{expected}`'
            )
        print(f"  [{i}/{len(cases)}] {'✅' if ok else '❌'} {fx['intent'][:64]}", flush=True)
    rate = passed / len(cases) if cases else 1.0
    print(
        f"\nrun_resolver_eval: LLM pass rate {passed}/{len(cases)} = {rate:.0%} "
        f"(threshold {MIN_PASS:.0%})"
    )
    if failures:
        print("\nMis-routes / failures:")
        print("\n".join(failures))
    return 0 if rate >= MIN_PASS else 1


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
        return run_llm_tier(fixtures, existing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
