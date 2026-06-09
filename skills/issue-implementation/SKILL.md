---
name: issue-implementation
description: Deliver a tracked GitHub issue end-to-end in the Recoupable house style — documentation-driven (OpenAPI/contract first), then test-driven (red→green) implementation that matches the docs, verified against the live preview deployment, with results posted to the PR. Use when the user says "implement this issue", "build out issue #N", "ship the issue", "do the implementation", "take this issue and build it", or hands you a tracking issue (usually from the issue-management skill) to deliver. Covers docs-first ordering, the TDD loop, preview verification, the docs↔API↔reality reconciliation, and PR review hygiene. Pairs with the issue-management skill (which writes the issue this one implements).
---

# Implementing a Tracked Issue

How we take a tracking issue from open to shipped at Recoupable. The bar: **the docs, the API, and the live preview all tell the same story — and every claim you make on the PR is something you actually ran.** No contract drift, no "should work," no untested assertions.

This is the delivery counterpart to the **issue-management** skill: that one writes the issue; this one implements it. The gold-standard reference slice this skill is built from is [chat#1789](https://github.com/recoupable/chat/issues/1789) (the tracking issue) → [docs#236](https://github.com/recoupable/docs/pull/236) (contract) → [api#653](https://github.com/recoupable/api/pull/653) (implementation). Read those three together to see the whole loop.

## Prerequisite: implement against a real contract, not a vibe

Only start when the issue is a proper spec — it should carry a **Goal**, a **proposed contract** (endpoint, params, response shape), a **merge sequencing** block (docs → api), **Done-when** acceptance criteria, and **source references**. If it doesn't, stop and write/upgrade it with the **issue-management** skill first. Implementing against a vague issue is how you ship the wrong thing.

## The loop

```
1. Read the issue + the ground            (contract, Done-when, conventions, the sibling to mirror)
2. Docs first — the contract              (OpenAPI/reference PR; merge target: main)
3. API by TDD, matching the docs          (red→green→refactor; PR target: test; links the docs PR)
4. Wait for the preview deployment        (poll the PR-head commit until Ready)
5. Test the PR against the preview        (every Done-when criterion, against real data)
6. Reconcile docs ↔ API ↔ live results    (live response is ground truth; fix drift)
7. Comment on the PR as you test          (results table; triage bot findings)
8. Hand off in merge order                (docs → api; update the issue to Done on merge)
```

Run it in order. Docs-first and tests-first are not optional — they are the method.

## 1. Read the issue + the ground

- **Extract from the issue:** the exact contract (path, params, response envelope, status codes), the merge order, every Done-when checkbox (these are your test plan), and the source references (verify any external API doc the issue cites is still accurate).
- **Read the ground:** the monorepo `PROGRESS.md` and each target submodule's `CLAUDE.md`/`AGENTS.md` (branch rules, test/lint commands, response/validation/auth conventions).
- **Find the closest sibling and mirror it — don't invent.** Almost every endpoint has a neighbor that already solves 90% of the shape (auth, validation, response wrapping, error envelope, credits). Build by analogy to it; consistency with the immediate neighbor beats cleverness.

## 2. Docs first — the contract

Documentation-driven development: the docs/OpenAPI change is the contract, and it merges before the code that fulfills it.

- Branch from `main` in `docs`. Mirror the nearest sibling endpoint's OpenAPI block — params, **reuse existing schemas** (DRY), the shared error-response schema, the reference-page frontmatter, and the nav entry (adding the page to `docs.json` is what surfaces it in the generated `llms.txt`).
- **Byte-safe edits to large/generated JSON.** Before bulk-inserting into a big OpenAPI file, round-trip it (`json.dumps(json.load(f), indent=2, ensure_ascii=False)` and diff against the original) to confirm your serializer reproduces it exactly — then load → add keys → dump. This keeps the diff additive instead of a whole-file reformat. Always re-validate the JSON parses.
- **Accuracy over symmetry.** Document only what the API will actually return. Do not add a response code or field just because a sibling has it — an undocumented-but-real gap is better than a documented-but-false one.
- Commit, push, open the docs PR (base `main`). This is step 1 of the merge order.

## 3. API by TDD, matching the docs

Branch per the repo's rule (Recoupable `api` PRs target `test`). Mirror the sibling implementation's layering (route → handler → validate → data function → response shaping; auth; credits).

**Red → green → refactor, one unit at a time:**

1. Write the failing test **first** in `__tests__/` (mock dependencies like the sibling tests do).
2. Run it and **confirm it fails** (RED) — usually "module not found" for a new file, or a real assertion failure for new behavior. Never write code and test in the same step.
3. Write the **minimum** implementation to pass (GREEN).
4. Refactor — **one exported function per file** (SRP). Extract inline helpers into their own lib files when a reviewer would (see how `gateChatStreamStart` / `waitForTerminalRunStatus` were pulled out).

Then: the implementation must match the **documented** contract exactly (params, response envelope, status codes). Run the **full domain test suite** (not just your files) to prove no regressions, then `tsc --noEmit` and lint. Commit, push, open the api PR (base `test`) — link the issue and the docs PR, and state the docs→api merge order in the body.

## 4. Wait for the preview deployment

- Find the preview for **your pushed commit** — `gh api repos/<owner>/<repo>/deployments?sha=<sha>` → its `/statuses` → `environment_url`, or the Vercel CLI (`vercel ls <project> --scope <team>` / `vercel inspect`).
- **Confirm it's built from your commit**, not a stale earlier preview — verify the deployment's sha. Testing a stale preview is a classic false-positive/false-negative trap.
- Poll until `Ready`. Background the poll on long builds; don't block.

## 5. Test the PR against the preview

Turn every **Done-when** criterion into a live check against the real preview URL:

- **Happy path** — the documented success response, with a real fixture (real id/ISRC/etc.).
- **Every status code** — including a **deliberately bad input** to confirm each 4xx (a non-UUID, an unknown id, a missing required param). This is how you confirm the documented error codes are real.
- **Auth** — 401 without a key; confirm no secret/env value is echoed in any response.
- **Cross-check the source of truth** — when it sharpens the assertion, query the DB / upstream directly (e.g. confirm a row's state, or that a per-item number is materially smaller than an aggregate). Capture **hard numbers**, not "looks right."

## 6. Reconcile docs ↔ API ↔ reality

The **live response is ground truth.** Compare it field-by-field and code-by-code against the documented contract:

- If the live response carries fields or status codes the docs **missed**, add them to the docs. (In the reference slice, the live response carried a top-level `source_ids` and a `track_info.songstats_track_id` the spec lacked — the docs were patched to match.)
- If the docs claim something the API **doesn't do**, fix whichever is wrong — usually the docs, sometimes the code (e.g. the contract said "exactly one identifier" but the validator allowed several → tighten the validator).

All three must agree before you call it done. This step is the entire point of the loop — it's what prevents the doc-drift the stop endpoint had.

## 7. Comment on the PR as you test

- Post your verification as a **results table on the PR** — *documented* vs *actual* for each path, with the hard numbers and status codes you observed. Do this on the api PR; comment on the docs PR too when you reconciled it.
- **Reply on review threads** when you address them, citing the commit.
- **Triage bot review findings critically — validate before applying.** A bot's "P1" can be a false positive (a suggested revert that would reintroduce a bug; a "missing 501" the endpoint never emits). Confirm against the code/live behavior, then either fix it or reply with the reasoning for not. Don't rubber-stamp, don't blanket-dismiss.

## 8. Hand off in merge order

- Merge order is **docs → api** (the contract lands first). Honor hard dependencies (a database migration before the api that reads it).
- **Never merge without explicit user approval.** When the user approves: merge, then promote per the repo flow (Recoupable: squash → `test`, then `test` → `main` via a release PR, then sync `test` with `main`), checking the release scope first.
- On merge, **update the tracking issue to Done** with the **issue-management** skill — a closure note (PR links, ✅ ISO date, merge path, what shipped, and a Verified clause citing the live results), and check off the Done-when boxes you actually verified.

## Principles

- **Docs-first, always** — the contract leads; code fulfills it.
- **Tests before code** — RED before GREEN, every unit; one exported function per file.
- **Verify against reality** — every claim on a PR is something you ran; capture hard numbers and ISO dates.
- **Accuracy over symmetry** — never document a response the API doesn't emit; match the immediate sibling's conventions over global ideals.
- **Minimal, additive diffs** on generated/large files; re-validate they still parse.
- **Never echo secrets** — reference the env-var name (`SONGSTATS_API_KEY`), never a value.

## Quick reference

```bash
# Find + confirm the preview for the commit you pushed
gh api repos/recoupable/api/deployments?sha=<SHA> --jq '.[].id'
gh api repos/recoupable/api/deployments/<ID>/statuses --jq '[.[]|select(.state=="success")|.environment_url][0]'
vercel ls api --scope recoup        # or: vercel inspect <url> --scope recoup

# Run a single test RED→GREEN, then the whole domain + types + lint
pnpm exec vitest run lib/<domain>/__tests__/<unit>.test.ts
pnpm exec vitest run lib/<domain> && pnpm exec tsc --noEmit && pnpm exec eslint <files>

# Test the preview, then post results on the PR
curl -s -w "\nHTTP %{http_code}\n" "<preview>/api/..." -H "x-api-key: <key>"
gh pr comment <n> --repo recoupable/api --body-file results.md
```

## Checklist before you call it done

- [ ] Implemented against a real tracking issue (contract + Done-when present); upgraded it first if not.
- [ ] Docs PR opened **first**; api PR links it and states the docs→api merge order.
- [ ] Every api unit was **RED before GREEN**; full domain suite + `tsc` + lint all clean.
- [ ] Preview confirmed **built from your commit**; **every Done-when criterion** exercised against it with real data.
- [ ] Docs ↔ API ↔ live results **agree** (reconciled and re-pushed if not).
- [ ] Verification **posted on the PR**; bot findings **triaged** (validated, not rubber-stamped).
- [ ] No secret value echoed anywhere — env-var names only.
- [ ] On merge: promoted per the repo flow and the tracking issue moved to **Done** (issue-management).
