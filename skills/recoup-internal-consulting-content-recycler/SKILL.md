---
name: recoup-internal-consulting-content-recycler
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Squeeze every published winner — repost proven posts with a fresh hook, re-share your own winners with added context, and fan one outlier post into multiple new formats. Use on \"what should I repost\", \"recycle my winners\", \"this post popped, what now\", \"turn this outlier into more posts\", \"wring the towel\", after an engagement pull shows a post outperforming baseline, or on the Friday review's recycle step. Reads published bundles + engagement data; stages new drafts; never auto-posts."
---

# Consulting Content Recycler

## Visual handoff

When this workflow creates or requests a rendered artifact, use `recoup-internal-consulting-tasteful-design` and
the selected workspace DESIGN.md. House identity is Recoup Sky; explicit client/artist branding wins.
Pass brand/version, expression, format, reference IDs and output folder to the media skill. Its bundled
package supplies exact fonts/logos. Keep new derivatives in the current identity while preserving
historical evidence. Save editable source and brand.lock.json with the deliverable. Ordinary text
outputs stay text; a script is not a rendered video. Existing data dashboards retain their canonical
Recoup CSS during data updates. Do not publish private client work to the public Brand Studio.


**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Most operators find a winner, use it once, and move on. This skill is the reuse loop: **a winner is
an asset, and an outlier is information.** Only a fraction of followers saw the original; everyone
who followed since has never seen it; the author gets bored of their own material long before the
audience does. Origin evidence: `swipe/posts/2026-07-09-anson-lin-founder-content-system.md`.

This is **not** `recoup-internal-consulting-content-distribution` (publish-day spread of one new pillar across
channels). The recycler works the back catalog on a cadence.

## Steps

1. **Find the winners.** Read `content/04-published/` bundles + engagement data in
   `integrations/linkedin/engagement/` (pull fresh if stale:
   `python integrations/linkedin/_work/pull_posts.py --max 25 --yes`, then
   `pull_engagement.py --post-url <url>` for candidates). A **winner** performs clearly above the
   account's recent baseline; an **outlier** is far above it. No engagement data → pull it, don't guess.
2. **Diagnose why it worked.** An outlier is information — isolate the variable before reusing it:
   the hook pattern (grade via `recoup-internal-consulting-linkedin-hooks`), the format (which founder format /
   archetype — `recoup-internal-consulting-linkedin-post-architect` references), the topic, or who showed up in the
   comments (ICP fit? → that's also a `recoup-internal-consulting-linkedin-audience` lead moment). Write the
   diagnosis down in the bundle's `distribution.md` — it steers the whole pipeline, not just this post.
3. **Pick the play (or several):**
   - **Repost** — after 1–2 months (or a follower-growth spurt), run the same idea again: rewrite the
     hook (different pattern, same substance), refresh any numbers to current verified values, keep
     the core. Stage as a new single draft. Don't repost verbatim inside ~60 days.
   - **Re-share with context** — while a post is running hot, or months later as backstory for new
     followers: quote/re-share your own post with an update or added context. On X, quote-post views
     stack onto the original's distribution (per the source playbook); on LinkedIn, a
     reshare-with-thoughts resurfaces it to the newer audience. The ceiling of this move is the
     **milestone chapter**: quoting your own old post as un-fakeable proof of the arc.
   - **Fan out the outlier** — one winner is never one post. Re-run the same material through other
     founder formats: a popped failure story returns later as a contrast hook, a milestone chapter
     once things turn, a build log for what came next. A launch is at least three posts sitting in
     one event: the announcement, the updated numbers, the lessons.
4. **Stage, never send.** Each recycled piece becomes a normal draft in `content/03-drafts/`
   (single or bundle per `content/AGENTS.md`), body via `recoup-internal-consulting-copy-writer`, structure via
   `recoup-internal-consulting-linkedin-post-architect`, shipped only through `recoup-internal-consulting-linkedin-publisher`.
5. **Record lineage.** In the new draft's frontmatter/meta note `recycled_from:` (the original bundle
   path + post URL) and log the recycle in the original bundle's `distribution.md`. Lineage prevents
   accidental double-recycling and lets the Friday review see which winners are already worked.

## Rails
- **Verified numbers only.** "Update the numbers" means re-verify against the primary source
  (evidence discipline) — never inflate or estimate a receipt.
- **Never auto-post.** Everything stages as a draft; publishing stays a human action.
- **Voice floor:** `recoup-internal-consulting-copy-writer` on every rewrite — a recycled post is a new post.
- **Don't strip-mine.** One recycle play per winner per cycle; the feed should never read as reruns.
  Quality bar unchanged: a cycle with nothing worth recycling produces nothing.

## Cadence
Fold into `recoup-internal-consulting-friday-review` (scan for winners/outliers) or run on demand when a post pops.
Chains: `recoup-internal-consulting-linkedin-audience` (the same hot post is also a lead source) →
`recoup-internal-consulting-followup-sequencer` for re-engaged contacts.
