---
name: recoup-internal-dev
description: INTERNAL — Recoup staff tooling. Never use for customer-facing or artist requests. Write, maintain, and implement GitHub issues in the Recoup house style — from tracking-issue structure (Goal, PRs matrix, Open/Done lifecycle, evidence rules) through documentation-driven delivery (docs-first contract, TDD red-green-refactor, preview verification, docs-API-reality reconciliation, PR review hygiene). Use when the user says "write an issue", "create a tracking issue", "update the issue", "implement this issue", "ship issue #N", "build out this tracker", or hands you any dev work that needs an issue written or delivered. Covers the full loop: issue authoring through shipped code.
---

# Recoup Dev: Issues & Implementation

How we write, maintain, and ship GitHub issues at Recoup. Two halves, one loop: **Part 1** writes the issue; **Part 2** implements it. The bar for an issue: a teammate (or a cold agent) can read it and know exactly what's done, what's left, why each decision was made, and how to verify any claim. The bar for implementation: the docs, the API, and the live preview all tell the same story, and every claim on the PR is something you actually ran.

The two reference issues this skill is built from are [chat#1747](https://github.com/recoupable/chat/issues/1747) (cutover plan) and [chat#1767](https://github.com/recoupable/chat/issues/1767) (post-cutover cleanup). The gold-standard implementation slice is [chat#1789](https://github.com/recoupable/chat/issues/1789) (tracking issue) -> [docs#236](https://github.com/recoupable/docs/pull/236) (contract) -> [api#653](https://github.com/recoupable/api/pull/653) (implementation).

---

# Part 1 — Writing & Maintaining Issues

## Issues live in a repository

**File every issue in `recoupable/chat`**, even when the code lands in `api`, `database`, or `docs` -- one home repo means one place to find open work. Never pick the repo by "where the diff lands"; link out to sibling-repo PRs/files by full ref instead. Wrong repo? `gh issue transfer <n> recoupable/chat --repo <wrong-repo>` preserves body/comments and leaves a redirect.

## Anatomy of a tracking issue

Use these sections in this order. Drop sections that don't apply; never reorder the ones you keep.

1. **Lead paragraph (no heading).** One or two sentences: what this issue tracks, the current prod/live status, and a link to the parent or sibling issue. Example: *"Tracking issue for cleanup that follows the X->Y cutover ([chat#1747](url), shipped to prod 2026-06-01). The cutover is fully live; this issue captures the remaining items."*
2. **## Goal.** The end state in concrete terms -- what "done" means at the macro level, and the downstream consequences. Name the files, endpoints, and tables involved.
3. **## PRs.** The fleet table -- see the PRs-matrix section below.
4. **## What shipped (context)** *(optional).* Hard numbers that ground the reader: commit/PR counts, rows migrated, latency measured. *"api/main has 23 commits / 13 PRs ... 17,991 sessions with correct artist_id; 0 stragglers remaining."*
5. **## Done.** Completed items as a checked list -- see the Done-item format below.
6. **## Open -- <bucket>.** Remaining work as unchecked items. Bucket by theme or priority (`Open -- cleanup + follow-ups`, `Open -- next up (in merge order)`, `Open -- pre-existing docs gaps (low priority)`). See the Open-item format below.
7. **## Open -- Phase N (LAST, only after ...).** Sequenced/gated work. State the gate explicitly in the heading and the body -- *"only after the cutover bundle is stable on `main` for some time."*
8. **## Architecture decisions.** Durable decisions with rationale, so they don't get re-litigated. Bold the decision, then explain. *"**chatId source of truth is api.** createSessionHandler mints chat.id; the client uses it as ..."*
9. **## Accepted regressions / tradeoffs** *(optional).* What you knowingly gave up and may re-add later. Makes the cost explicit instead of silent.
10. **## Inherited gaps / Source references** *(optional).* Cross-links to other trackers, the originating PRs, key files (with paths), and prior art.

## The PRs matrix (required for any multi-PR tracker)

Any tracker coordinating more than one PR carries this table **directly under `## Goal`** -- the one place a reader (or a cold agent) sees the whole fleet and its state without scanning prose.

Heading is `## PRs (updated <ISO date>)` so staleness is visible. Columns:

```
## PRs (updated 2026-06-25)

| PR | Item | State |
|----|------|-------|
| [docs#251](url) | `POST /api/emails` send-email contract (OpenAPI + types + nav) | merged 2026-06-25 -- see Done |
| [api#708](url) | `POST /api/emails` endpoint + auth fix | open -- preview-verified end-to-end |
| [api#TBD](#) | rate-limit the send path | not started |
```

- **PR** -- full cross-repo ref, linked; one row per PR, sibling repos included. A tracker written before implementation lists planned PRs as `repo#TBD` rows so the fleet is visible up front. (All PRs target `main`; there is no base-branch column.)
- **Item** -- one-line what-it-does, worded to match the Done/Open item it backs.
- **State** -- `not started`, `open -- <verification status>`, or `merged <ISO> -- see Done` (the row stays; the closure note lives under `## Done`).

**Update a row in the same session its PR changes state.** Replace `#TBD` with the live ref the moment the PR opens -- never batch for "when they're all open"; an open PR whose row still says `#TBD` is drift of the same class as a merged PR without a closure note (caught in practice on chat#1841). Follow the table with a merge-sequencing blockquote when order matters; when everything is one state, say so (*"all seven merged and on prod"*).

## The Open -> Done lifecycle (the most important rule)

Items are **not** closed by flipping `- [ ]` to `- [x]`. When an item ships, **rewrite it into a closure note** and move it under `## Done`:

```
- [x] **chat[#1765](url) -- drop legacy useChatTransport branch + delete app/chat/[roomId]/page.tsx.**
  Shipped 2026-06-03 (squash-merged to `main`).
  <what actually changed, technically -- 2-4 sentences>.
  Verified end-to-end on preview: new chat -> session-scoped URL, transport POSTs
  /api/chat/workflow with sessionId+chatId+bearer, assistant streams, legacy route 404s.
```

Every Done item carries: **bold lead-in + PR link**, **ISO ship date + merge commit**, **what changed**, and a **Verified** clause stating *how* you confirmed it and *on what* (preview/prod, what you clicked, what the response showed). If a hypothesis turned out wrong, say so and link the evidence.

## Open-item format

An open item is a mini-spec, not a one-liner. For anything non-trivial, include:

```
- [ ] **<bold one-line summary>.** (<PR that addresses it, if one exists>)
  - **Why:** <root cause or motivation, with file:line if known>
  - **Fix:** <concrete steps, numbered if multi-step>
  - **Done when:** <observable acceptance criteria -- what you'd check to call it done>
```

Note explicit **blocked-by** relationships inline (*"No blockers -- unblocked by #1760"*). If items have a merge order, say "in merge order; pick from the top."

### Merge sequencing (documentation-driven development)

We follow **documentation-driven development**: the docs/contract is written and reviewed first, then implemented against. When a unit of work spans repos, sequence the PRs **docs -> database -> api/app** -- the `docs` OpenAPI/spec change is the contract the rest fulfills, so it leads even though it's usually independent. Within that, still honor hard dependencies (e.g. a `database` migration must land before the `api` code that reads the new table). State the order explicitly in a "Merge sequencing" block and say *why* each step precedes the next (contract-first vs. hard dependency).

## Linking & evidence rules

- **Link every claim.** PRs as `[chat#1765](url)`, commits by SHA, files by path, source by line range (`[source: useArtistsRoster.ts L60-86](url)`). A claim without a link is a claim someone has to re-verify.
- **Use hard numbers**, not adjectives. "10.9s cold", "46,212 memories -> chat_messages", "13 chats returned, archived row gone" beats "slow", "lots", "works".
- **ISO 8601 dates** (`2026-06-03`), always.
- **Cross-repo links** by full ref (`recoupable/api#605`) so they resolve from any repo.
- **Record rationale when you close or supersede a PR**: *"closed #1754 (superseded; chat-side direct-DB approach was wrong layer)."*
- **Never paste secrets into an issue.** No API keys, tokens, or credentials -- issues are often public and always long-lived/indexed. Reference the env var or store instead (*"`SONGSTATS_API_KEY`, set in Vercel"*), not the value. Same for any key handed over in a thread.

## Maintaining an issue over time

- When you finish a unit of work, **update the issue in the same session** -- move the item to Done with its closure note. Don't let the issue drift from reality.
- Keep the lead paragraph's status line current ("fully live on prod").
- **Keep the title current too.** The title is maintained state, not a fixed label -- when scope changes, edit it.
- Comment for time-stamped updates or test results; edit the body for the canonical current state (`gh issue edit --body-file` -- a file keeps the markdown intact). Manual test results generally go in PR comments, not the issue body.
- Close the issue only when **every** item is in Done or has been explicitly moved to a follow-up tracker (link it).

### Decision changes & reversals (supersede, don't erase)

When the plan reverses, record the change so the *old* reasoning stays auditable -- don't silently rewrite history:

- **Add a dated decision callout near the top** (a `>` blockquote under the lead): what changed, **who decided + when**, and the one-line rationale. Attribution + ISO date matter most for decisions that came from a discussion, not from code.
- **The dated callout is the tombstone -- delete the dead items.** Remove superseded Open items/plans from the body; the callout alone carries what was dropped and why, so it isn't re-proposed. No strikethrough tombstones scattered through the sections.
- **Update every downstream section**: Goal, the affected Open items, Architecture decisions (mark the reversed one *"supersedes the earlier ..."*), the title, and Source references (link the decision thread).
- **Re-anchor in-flight PRs to the new plan.** If an open PR was built for the old approach, say what now has to change before it can merge.

## Smaller / non-tracking issues

Not every issue is a tracker. A bug report or single-task issue still earns its keep with: a one-line **summary**, **steps to reproduce** (or the trigger), **expected vs actual**, and **Done when** acceptance criteria. Link the suspected code with file:line. Skip the Goal/Architecture/Phase scaffolding -- that's for multi-PR efforts only. Match the weight of the issue to the weight of the work.

## Scope to the change, not the outcome

An issue tracks the **work to be done**, not the business goal that consumes it. Scope it to one layer/change and keep downstream logic that runs *after* the issue is solved **out of scope** -- it bloats the issue and muddies what "done" means.

- **Title names the deliverable, not the outcome** -- "Add `GET /api/research/track/historic-stats`", not "annualize catalog -> dashboard value".
- **Business context gets exactly one perspective line** -- in the lead, flagged out-of-scope: enough to know who needs this and why, never repeated through Goal / steps / Done when.
- **Every Done-when item must be verifiable within scope** by whoever implements it -- not a downstream outcome the implementer can't check.

---

# Part 2 — Implementing a Tracked Issue

## Prerequisite: implement against a real contract, not a vibe

Only start when the issue is a proper spec -- it should carry a **Goal**, a **proposed contract** (endpoint, params, response shape), a **merge sequencing** block (docs -> api), **Done-when** acceptance criteria, and **source references**. If it doesn't, stop and write/upgrade it with Part 1 first. Implementing against a vague issue is how you ship the wrong thing.

## The loop

```
1. Read the issue + the ground            (contract, Done-when, conventions, the sibling to mirror)
2. Docs first -- the contract             (OpenAPI/reference PR; merge target: main)
3. API by TDD, matching the docs          (red->green->refactor; PR target: main; links the docs PR)
4. Wait for the preview deployment        (poll the PR-head commit until Ready)
5. Test the PR against the preview        (every Done-when criterion, against real data)
6. Reconcile docs <-> API <-> live results (live response is ground truth; fix drift)
7. Comment on the PR as you test          (results table; triage bot findings)
8. Hand off in merge order                (docs -> api; update the issue to Done on merge)
```

Run it in order. Docs-first and tests-first are not optional -- they are the method.

**After every push that changes behavior -- including review fixes, UI tweaks, and follow-up commits on an open PR -- re-run steps 4->7 on that new commit before you say the work is done.** Unit tests alone are not enough. Do not hand back "fixed" or "addressed feedback" until the preview for *that* SHA is Ready, exercised live, and the results (with screenshots for **app and marketing** UI PRs) are posted on the PR. Skipping preview after a mid-PR change is the same failure mode as shipping untested code.

## 1. Read the issue + the ground

- **Extract from the issue:** the exact contract (path, params, response envelope, status codes), the merge order, every Done-when checkbox (these are your test plan), and the source references (verify any external API doc the issue cites is still accurate). If a cited doc is **client-side-rendered** (`WebFetch` returns an empty JS shell), read it with a **browser MCP** -- e.g. Chrome DevTools `navigate_page` then `evaluate_script` to pull the rendered params/response -- not `WebFetch`.
- **Read the ground:** each target submodule's `CLAUDE.md`/`AGENTS.md` (branch rules, test/lint commands, response/validation/auth conventions).
- **Find the closest sibling and mirror it -- don't invent.** Almost every endpoint has a neighbor that already solves 90% of the shape (auth, validation, response wrapping, error envelope, credits). Build by analogy to it; consistency with the immediate neighbor beats cleverness.

## 2. Docs first -- the contract

Documentation-driven development: the docs/OpenAPI change is the contract, and it merges before the code that fulfills it.

- Branch from `main` in `docs`. Mirror the nearest sibling endpoint's OpenAPI block -- params, **reuse existing schemas** (DRY), the shared error-response schema, the reference-page frontmatter, and the nav entry (adding the page to `docs.json` is what surfaces it in the generated `llms.txt`).
- **Additive edits to large/generated JSON.** Round-trip the file first (`json.dumps(json.load(f), indent=2)` vs the original); only load->add->dump if it reproduces byte-for-byte -- otherwise (common) insert the new blocks via **anchored text edits** at brace boundaries so the diff stays purely additive. Either way, re-validate the result parses.
- **Accuracy over symmetry.** Document only what the API will actually return. Do not add a response code or field just because a sibling has it -- an undocumented-but-real gap is better than a documented-but-false one.
- Commit, push, open the docs PR (base `main`). This is step 1 of the merge order.

## 3. API by TDD, matching the docs

Branch from `main`. Mirror the sibling implementation's layering (route -> handler -> validate -> data function -> response shaping; auth; credits).

**Red -> green -> refactor, one unit at a time:**

1. Write the failing test **first** in `__tests__/` (mock dependencies like the sibling tests do).
2. Run it and **confirm it fails** (RED) -- usually "module not found" for a new file, or a real assertion failure for new behavior. Never write code and test in the same step.
3. Write the **minimum** implementation to pass (GREEN).
4. Refactor -- **one exported function per file** (SRP). Extract inline helpers into their own lib files when a reviewer would.

Then: the implementation must match the **documented** contract exactly (params, response envelope, status codes). Run the **full domain test suite** (not just your files) to prove no regressions, then `tsc --noEmit` and lint. Commit, push, open the api PR (base `main`) -- link the issue and the docs PR, and state the docs->api merge order in the body.

**Every time you open a PR (docs, api, or any sibling): update its row in the tracking issue's PR matrix in the same session** -- replace the `repo#TBD` placeholder with the live ref and a `open -- <verification status>` state. Don't wait until all PRs are open or until merge; an open PR with a `#TBD` row is tracker drift.

## 4. Wait for the preview deployment

This step is not one-and-done for the PR. **Every time you push a commit that changes runtime behavior or UI, start again here** for that commit's SHA -- even if you already preview-tested an earlier SHA on the same branch.

- Find the preview for **your pushed commit** -- `gh api repos/<owner>/<repo>/deployments?sha=<sha>` -> its `/statuses` -> `environment_url`, or the Vercel CLI (`vercel ls <project> --scope <team>` / `vercel inspect`).
- **Confirm it's built from your commit**, not a stale earlier preview -- verify the deployment's sha. Testing a stale preview is a classic false-positive/false-negative trap.
- Poll until `Ready`. Background the poll on long builds; don't block.
- **Preview envs may run different auth than prod** (e.g. a separate Privy app; API-key hashes peppered with a different secret) -- a prod-minted key/token can 401 on a preview even though the route is fine. Get a credential minted against the preview env before concluding anything.

## 5. Test the PR against the preview

Turn every **Done-when** criterion into a live check against the real preview URL (and re-check any criterion your latest push could have regressed -- for UI/positioning changes, measure on mobile and desktop viewports):

- **Happy path** -- the documented success response, with a real fixture (real id/ISRC/etc.).
- **Every status code** -- including a **deliberately bad input** to confirm each 4xx (a non-UUID, an unknown id, a missing required param). This is how you confirm the documented error codes are real.
- **Auth** -- 401 without a key; confirm no secret/env value is echoed in any response.
- **Cross-check the source of truth** -- when it sharpens the assertion, query the DB / upstream directly (e.g. confirm a row's state, or that a per-item number is materially smaller than an aggregate). Capture **hard numbers**, not "looks right."
- **UI PRs (app and marketing)** -- drive the changed surface in a real browser (agent-browser or equivalent). For layout claims (centered modal, mobile sheet, pricing cards/tables, etc.), capture screenshots and, when useful, element bounding boxes vs viewport -- not "looks fine locally." Screenshots are required for both `app` and `marketing` preview verification; host them in the PR **comment** (not as commits on the feature branch).

## 6. Reconcile docs <-> API <-> reality

The **live response is ground truth.** Compare it field-by-field and code-by-code against the documented contract:

- If the live response carries fields or status codes the docs **missed**, add them to the docs.
- If the docs claim something the API **doesn't do**, fix whichever is wrong -- usually the docs, sometimes the code (e.g. the contract said "exactly one identifier" but the validator allowed several -> tighten the validator).

All three must agree before you call it done. This step is the entire point of the loop -- it's what prevents doc-drift.

## 7. Comment on the PR as you test

- Post your verification as a **results table on the PR** -- *documented* vs *actual* for each path, with the hard numbers and status codes you observed. For **app and marketing UI PR preview testing**, always include screenshots in the PR comment alongside the results (desktop + mobile when layout matters). Do this on the api PR; comment on the docs PR too when you reconciled it. After a follow-up push, post a **new** comment for the new SHA (or clearly update) -- do not leave only the old SHA's results.
- **Reply on review threads** when you address them, citing the commit **and** the preview verification for that commit.
- **Triage bot review findings critically -- validate before applying.** A bot's "P1" can be a false positive (a suggested revert that would reintroduce a bug; a "missing 501" the endpoint never emits). Confirm against the code/live behavior, then either fix it or reply with the reasoning for not. Don't rubber-stamp, don't blanket-dismiss.

## 8. Hand off in merge order

- Merge order is **docs -> api** (the contract lands first). Honor hard dependencies (a database migration before the api that reads it).
- **Never merge without explicit user approval.** On approval, squash-merge to `main`.
- On merge, **update the tracking issue to Done** with a closure note (PR links, ISO date, merge path, what shipped, and a Verified clause citing the live results), and check off the Done-when boxes you actually verified.

## Quick reference

```bash
# Find + confirm the preview for the commit you pushed
gh api repos/recoupable/api/deployments?sha=<SHA> --jq '.[].id'
gh api repos/recoupable/api/deployments/<ID>/statuses --jq '[.[]|select(.state=="success")|.environment_url][0]'

# Run a single test RED->GREEN, then the whole domain + types + lint
pnpm exec vitest run lib/<domain>/__tests__/<unit>.test.ts
pnpm exec vitest run lib/<domain> && pnpm exec tsc --noEmit && pnpm exec eslint <files>

# Test the preview, then post results on the PR
curl -s -w "\nHTTP %{http_code}\n" "<preview>/api/..." -H "x-api-key: <key>"
gh pr comment <n> --repo recoupable/api --body-file results.md
```

---

# Checklists

## Before posting / updating an issue

- [ ] Multi-PR tracker has a **`## PRs` matrix under `## Goal`** (PR | Item | State), `updated <ISO>` heading, every row current as of this session.
- [ ] Shipped items are **closure notes under `## Done`** (PR link, ISO date, merge path, what changed, **Verified**) -- never a bare `[x]`.
- [ ] Every claim is **linked** (PR/SHA/file:line); numbers are **hard**, dates **ISO**; **no secrets** (env-var name, never a value).
- [ ] **Title + lead reflect current reality** (scope + live status); reversals superseded, not erased.
- [ ] **Scoped to the change** -- cross-layer/business context stated once; every Done-when verifiable in scope.

## Before calling implementation done

- [ ] Implemented against a real tracking issue (contract + Done-when present); upgraded it first if not.
- [ ] Docs PR opened **first**; api PR links it and states the docs->api merge order.
- [ ] Every opened PR's **matrix row updated** (`#TBD` -> live ref + status) in the same session it was opened.
- [ ] Every api unit was **RED before GREEN**; full domain suite + `tsc` + lint all clean.
- [ ] Preview confirmed **built from your commit**; **every Done-when criterion** exercised against it with real data.
- [ ] **Every behavior-changing push** (including review-fix rounds) was re-preview-tested on **that** SHA -- not only the first implementation push.
- [ ] Docs <-> API <-> live results **agree** (reconciled and re-pushed if not).
- [ ] Verification **posted on the PR** with screenshots for **app and marketing** UI previews; bot findings **triaged** (validated, not rubber-stamped).
- [ ] No secret value echoed anywhere -- env-var names only.
- [ ] On merge: tracking issue moved to **Done** with closure note.
