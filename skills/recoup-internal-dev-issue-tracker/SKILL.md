---
name: recoup-internal-dev-issue-tracker
description: INTERNAL — Recoup staff tooling. Never use for customer-facing or artist requests. Write and maintain high-signal GitHub issues — especially long-lived tracking issues that coordinate multi-PR, multi-repo efforts — in the Recoup house style. Use when the user says "write an issue", "create a tracking issue", "open an issue for this work", "update the issue", "check off / close out an item", "log what shipped on the issue", "maintain the issue", or when capturing a plan, cutover, migration, or cleanup that spans more than one PR. Covers structure, the Open→Done lifecycle, evidence/linking rules, and acceptance criteria.
---

# Writing & Maintaining Issues

How we write GitHub issues at Recoup. The bar: **a teammate (or a cold agent) can read the issue and know exactly what's done, what's left, why each decision was made, and how to verify any claim — without re-deriving it from git history.** Issues are persistent memory, not a TODO dump.

Most substantial work gets a **tracking issue**: a long-lived issue that coordinates a multi-PR (often multi-submodule) effort. The two reference issues this skill is built from are [chat#1747](https://github.com/recoupable/chat/issues/1747) (cutover plan) and [chat#1767](https://github.com/recoupable/chat/issues/1767) (post-cutover cleanup). Read them if you want the gold standard.

## Issues live in a repository

**File every issue in `recoupable/chat`**, even when the code lands in `api`, `database`, or `docs` — one home repo means one place to find open work. Never pick the repo by "where the diff lands"; link out to sibling-repo PRs/files by full ref instead (the chat cutover tracker lives in `chat` though most commits were in `api`). Wrong repo? `gh issue transfer <n> recoupable/chat --repo <wrong-repo>` preserves body/comments and leaves a redirect.

## Anatomy of a tracking issue

Use these sections in this order. Drop sections that don't apply; never reorder the ones you keep.

1. **Lead paragraph (no heading).** One or two sentences: what this issue tracks, the current prod/live status, and a link to the parent or sibling issue. Example: *"Tracking issue for cleanup that follows the X→Y cutover ([chat#1747](url), shipped to prod 2026-06-01). The cutover is fully live; this issue captures the remaining items."*
2. **## Goal.** The end state in concrete terms — what "done" means at the macro level, and the downstream consequences. Name the files, endpoints, and tables involved.
3. **## PRs.** The fleet table — see the PRs-matrix section below.
4. **## What shipped (context)** *(optional).* Hard numbers that ground the reader: commit/PR counts, rows migrated, latency measured. *"api/main has 23 commits / 13 PRs … 17,991 sessions with correct artist_id; 0 stragglers remaining."*
5. **## Done.** Completed items as a checked list — see the Done-item format below.
6. **## Open — <bucket>.** Remaining work as unchecked items. Bucket by theme or priority (`Open — cleanup + follow-ups`, `Open — next up (in merge order)`, `Open — pre-existing docs gaps (low priority)`). See the Open-item format below.
7. **## Open — Phase N (LAST, only after …).** Sequenced/gated work. State the gate explicitly in the heading and the body — *"only after the cutover bundle is stable on `main` for some time."*
8. **## Architecture decisions.** Durable decisions with rationale, so they don't get re-litigated. Bold the decision, then explain. *"**chatId source of truth is api.** createSessionHandler mints chat.id; the client uses it as …"*
9. **## Accepted regressions / tradeoffs** *(optional).* What you knowingly gave up and may re-add later. Makes the cost explicit instead of silent.
10. **## Inherited gaps / Source references** *(optional).* Cross-links to other trackers, the originating PRs, key files (with paths), and prior art.

## The PRs matrix (required for any multi-PR tracker)

Any tracker coordinating more than one PR carries this table **directly under `## Goal`** — the one place a reader (or a cold agent) sees the whole fleet and its state without scanning prose.

Heading is `## PRs (updated <ISO date>)` so staleness is visible. Columns:

```
## PRs (updated 2026-06-25)

| PR | Item | State |
|----|------|-------|
| [docs#251](url) | `POST /api/emails` send-email contract (OpenAPI + types + nav) | ✅ merged 2026-06-25 — see Done |
| [api#708](url) | `POST /api/emails` endpoint + auth fix | 🔄 open — preview-verified end-to-end |
| [api#TBD](#) | rate-limit the send path | ⏳ not started |
```

- **PR** — full cross-repo ref, linked; one row per PR, sibling repos included. A tracker written before implementation lists planned PRs as `repo#TBD` rows so the fleet is visible up front. (All PRs target `main`; there is no base-branch column.)
- **Item** — one-line what-it-does, worded to match the Done/Open item it backs.
- **State** — `⏳ not started`, `🔄 open — <verification status>`, or `✅ merged <ISO> — see Done` (the row stays; the closure note lives under `## Done`).

**Update a row in the same session its PR changes state.** Replace `#TBD` with the live ref the moment the PR opens — never batch for "when they're all open"; an open PR whose row still says `#TBD` is drift of the same class as a merged PR without a closure note (caught in practice on chat#1841). Follow the table with a merge-sequencing blockquote when order matters (see below); when everything is one state, say so (*"all seven merged and on prod"*).

## The Open → Done lifecycle (the most important rule)

Items are **not** closed by flipping `- [ ]` to `- [x]`. When an item ships, **rewrite it into a closure note** and move it under `## Done`:

```
- [x] **chat[#1765](url) — drop legacy useChatTransport branch + delete app/chat/[roomId]/page.tsx.**
  ✅ Shipped 2026-06-03 (squash-merged to `main`).
  <what actually changed, technically — 2-4 sentences>.
  Verified end-to-end on preview: new chat → session-scoped URL, transport POSTs
  /api/chat/workflow with sessionId+chatId+bearer, assistant streams, legacy route 404s.
```

Every Done item carries: **bold lead-in + PR link**, **✅ + ISO ship date + merge commit**, **what changed**, and a **Verified** clause stating *how* you confirmed it and *on what* (preview/prod, what you clicked, what the response showed). If a hypothesis turned out wrong, say so and link the evidence — see how #1767 documents the "3 sessions per click" item turning out to already be fixed, with the `isLoading`→`isPending` root cause and a link to the source line range.

## Open-item format

An open item is a mini-spec, not a one-liner. For anything non-trivial, include:

```
- [ ] **<bold one-line summary>.** (<PR that addresses it, if one exists>)
  - **Why:** <root cause or motivation, with file:line if known>
  - **Fix:** <concrete steps, numbered if multi-step>
  - **Done when:** <observable acceptance criteria — what you'd check to call it done>
```

Real example (the model-selector bug from #1767): *Why* — the workflow reads `chats.model_id` but the UI only puts `model` in the request body. *Fix* — on model change, `PATCH .../chats/{chatId}` with `{ modelId }`. *Done when* — pick a non-default model → send → `usage_events.model_id` shows the model you selected, not the default. A reader can pick this up cold and finish it.

Note explicit **blocked-by** relationships inline (*"No blockers — unblocked by #1760"*). If items have a merge order, say "in merge order; pick from the top."

### Merge sequencing (documentation-driven development)

We follow **documentation-driven development**: the docs/contract is written and reviewed first, then implemented against. When a unit of work spans repos, sequence the PRs **docs → database → api/app** — the `docs` OpenAPI/spec change is the contract the rest fulfills, so it leads even though it's usually independent. Within that, still honor hard dependencies (e.g. a `database` migration must land before the `api` code that reads the new table). State the order explicitly in a "Merge sequencing" block and say *why* each step precedes the next (contract-first vs. hard dependency).

## Linking & evidence rules

- **Link every claim.** PRs as `[chat#1765](url)`, commits by SHA, files by path, source by line range (`[source: useArtistsRoster.ts L60-86](url)`). A claim without a link is a claim someone has to re-verify.
- **Use hard numbers**, not adjectives. "10.9s cold", "46,212 memories → chat_messages", "13 chats returned, archived row gone" beats "slow", "lots", "works".
- **ISO 8601 dates** (`2026-06-03`), always.
- **Cross-repo links** by full ref (`recoupable/api#605`) so they resolve from any repo.
- **Record rationale when you close or supersede a PR**: *"closed #1754 (superseded; chat-side direct-DB approach was wrong layer)."*
- **Never paste secrets into an issue.** No API keys, tokens, or credentials — issues are often public and always long-lived/indexed. Reference the env var or store instead (*"`SONGSTATS_API_KEY`, set in Vercel"*), not the value. Same for any key handed over in a thread.

## Maintaining an issue over time

- When you finish a unit of work, **update the issue in the same session** — move the item to Done with its closure note. Don't let the issue drift from reality.
- Keep the lead paragraph's status line current ("fully live on prod").
- **Keep the title current too.** The title is maintained state, not a fixed label — when scope changes, edit it. (#1777's title carried `+ bring-your-own-key` after that path was dropped; it had to be re-edited to match.)
- Comment for time-stamped updates or test results; edit the body for the canonical current state (`gh issue edit --body-file` — a file keeps the markdown intact). Manual test results generally go in PR comments, not the issue body.
- Close the issue only when **every** item is in Done or has been explicitly moved to a follow-up tracker (link it).

### Decision changes & reversals (supersede, don't erase)

When the plan reverses (e.g. #1777 pivoted from "keep Chartmetric behind a BYO-key router" to "delete all Chartmetric code, SongStats-only" on a YAGNI call), record the change so the *old* reasoning stays auditable — don't silently rewrite history:

- **Add a dated decision callout near the top** (a `>` blockquote under the lead): what changed, **who decided + when**, and the one-line rationale. Attribution + ISO date matter most for decisions that came from a discussion, not from code.
- **The dated callout is the tombstone — delete the dead items.** Remove superseded Open items/plans from the body; the callout alone carries what was dropped and why, so it isn't re-proposed. No strikethrough tombstones scattered through the sections.
- **Update every downstream section**: Goal, the affected Open items, Architecture decisions (mark the reversed one *"supersedes the earlier …"*), the title, and Source references (link the decision thread).
- **Re-anchor in-flight PRs to the new plan.** If an open PR was built for the old approach, say what now has to change before it can merge (e.g. #1777 flags that api#635's Chartmetric branch must be stripped pre-merge, and that verification must re-run after).

## Smaller / non-tracking issues

Not every issue is a tracker. A bug report or single-task issue still earns its keep with: a one-line **summary**, **steps to reproduce** (or the trigger), **expected vs actual**, and **Done when** acceptance criteria. Link the suspected code with file:line. Skip the Goal/Architecture/Phase scaffolding — that's for multi-PR efforts only. Match the weight of the issue to the weight of the work.

## Scope to the change, not the outcome

An issue tracks the **work to be done**, not the business goal that consumes it. Scope it to one layer/change and keep downstream logic that runs *after* the issue is solved **out of scope** — it bloats the issue and muddies what "done" means.

- **Title names the deliverable, not the outcome** — "Add `GET /api/research/track/historic-stats`", not "annualize catalog → dashboard value". (Sharper version of keeping the title current.)
- **Business context gets exactly one perspective line** — in the lead, flagged out-of-scope: enough to know who needs this and why, never repeated through Goal / steps / Done when.
- **Every Done-when item must be verifiable within scope** by whoever implements it — not a downstream outcome (a dashboard number, a calibration to a comp, a revenue figure) the implementer can't check.

The smell: domain terms from a *different* layer (e.g. a business metric in an API/docs issue) showing up in the Goal, the steps, and the acceptance criteria. State the cross-layer context once, then stay in your layer.

## Checklist before you post / update

The non-negotiables — structure/format is covered by the sections above; these are the things most often gotten wrong:

- [ ] Multi-PR tracker has a **`## PRs` matrix under `## Goal`** (PR | Item | State), `updated <ISO>` heading, every row current as of this session.
- [ ] Shipped items are **closure notes under `## Done`** (PR link, ✅ ISO date, merge path, what changed, **Verified**) — never a bare `[x]`.
- [ ] Every claim is **linked** (PR/SHA/file:line); numbers are **hard**, dates **ISO**; **no secrets** (env-var name, never a value).
- [ ] **Title + lead reflect current reality** (scope + live status); reversals superseded, not erased.
- [ ] **Scoped to the change** — cross-layer/business context stated once; every Done-when verifiable in scope.
