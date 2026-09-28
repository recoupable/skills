---
name: recoup-internal-consulting-nightly-content
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Phase 3 of the nightly pipeline — the demand engine's insight lane (Engine A, article-first). After capture + janitor, pick a signal from the day's reservoir and produce a copy-edited pillar ARTICLE plus a LinkedIn post and a broadcast email derived from it, and an on-brand image set — staged as one role-named idea bundle (article.md + linkedin.md + email.md + images/ + meta.yml) for review, never published. Every text format goes through recoup-internal-consulting-copy-reviewer (the reader's eyes) then recoup-internal-consulting-copy-editor; recoup-internal-consulting-article-illustrator makes the hero + inline diagrams. Article-first: one pillar -> many formats. Use on \"run the nightly content\", \"draft today's article\", or as the nightly content ritual."
---

# Consulting Nightly Content (article-first flywheel engine)

## Required public-content gate

Read `references/public-content-quality.md` before drafting, reviewing, illustrating or publishing.
It governs competitor/source restrictions, plain-language explanations, cover comprehension and
revision evidence. Apply it to every public format; older style examples do not override this gate.

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

Capture turns calls into insights; this turns the day's strongest insight into a **pillar article**, runs it
past the customer's eyes and the editor's, derives and edits a **LinkedIn post**, then makes an **on-brand image set (hero + figures)**. Article-first,
because one good article becomes many platform posts later (LinkedIn, X, newsletter) — write the pillar
once, atomize forever.

The engine drafts; **the owner publishes.** Quality over cadence.

## Output — one idea bundle (slug folder) in drafts/
```
content/03-drafts/<YYYY-MM-DD>-<topic-slug>/    ← the idea is the unit (date + slug = identity)
  meta.yml         the bundle manifest / approval state machine (source + per-format status + gates)
  article.md       the pillar article (hero + figures embedded inline)
  linkedin.md      the stand-alone LinkedIn post
  email.md         a single-idea broadcast email to the list (not the weekly newsletter)
  images/          image1.<ext> = hero (also the social/OG preview), then image2.<ext>… (~1 per section)
```
Children are **role-named** (`article.md`, `linkedin.md`, `email.md`; `x.md` as the idea warrants) — the
folder carries the title, so every bundle is structurally identical and the approval queue is uniform.
**Every run produces the full set** (article + linkedin + email + images), each text format gated
(reviewer then editor). Same shape Engine B (`recoup-internal-consulting-product-engine`) produces.
(A pillar is the *folder* shape of a draft; a one-off post/graphic is a single file in `content/03-drafts/`.
See `content/AGENTS.md`.)

## Rails
1. **Never auto-publish.** Drafts only; the owner reviews + publishes via `recoup-internal-consulting-linkedin-publisher` (Postbridge).
2. **Grounded, not fabricated.** Every claim traces to a real captured insight/transcript — carry the
   citation in the private manifest; public attribution must pass the public-content gate. Never invent a client name, number, or result; confirm before naming a client, or write generically.
3. **Voice = `recoup-internal-consulting-copy-writer`** (no exceptions): no em-dashes, anti-slop list, specific, human. Read it.
4. **Two gates on EVERY audience-facing format (article, linkedin, email): reader, then editor.** Run `recoup-internal-consulting-copy-reviewer` (the right ICP per format) and rewrite from its notes, *then* `recoup-internal-consulting-copy-editor`. Reviewer before editor, always. **Scored ≠ gated:** `score_run.py` is the floor; the reader/editor passes are the bar.
5. **One idea, the full bundle.** Every run produces `article.md` + `linkedin.md` + `email.md` + `images/` + `meta.yml`. The article is the pillar; the post and email derive from the edited article.
6. **Quality over volume.** One strong pillar a night (occasionally a second). A thin day → one-line report, no bundle.

## Steps
0. **Orient + find what's new.** Read the day's `business/ops/nightly-digests/<date>.md`. Gather unused
   **signals** — the **dated `signals/<YYYY-MM-DD>-*.md` files** with `status: new` (plus `evergreen` POVs
   not yet drafted into a published pillar); skip `used`/`archived` **and the meta files** (`AGENTS.md`,
   `_template.md`, `_index.md`, `_archive/` are NOT signals). (`content/_work/LAST_DRAFTED` is just a
   run-log now; per-signal `status` is the truth.) `git log` for today.

1. **Pick ONE signal** — the strongest, most specific unused signal (`status: new`, or an `evergreen` POV
   not yet published) with a real story / POV from an actual source. Dedup vs `content/04-published/` and
   existing `content/03-drafts/` (never rewrite a published pillar). Carry its `source` so the draft stays
   grounded. Slugify the topic and make the bundle folder `content/03-drafts/<YYYY-MM-DD>-<topic-slug>/`
   (date-first, so `drafts/` sorts chronologically).
   - **Fresh `product-update` signals jump the queue.** Ingestion writes `type: product-update` signals
     (cited to PRs) from the GitHub capture. Feature news is **perishable** — announce it while it's new —
     so a fresh product-update outranks evergreen insights for tonight's slot; insights fill otherwise.
   - **Branch on the signal's `type`.** If it's a `product-update`, draft with **Engine B's
     feature-announcement variant** (`recoup-internal-consulting-product-engine` — its draft half): ground every claim in the
     cited PRs, use the feature-announcement email format, Recoup-customer ICP for the email. Otherwise use
     the insight/thought-leadership variant below. **Either way the output is the same unified bundle**
     (article + linkedin + email + images + meta.yml), each text format gated.

2. **Write the ARTICLE** (the pillar). Read **`recoup-internal-consulting-copy-writer`** first: voice-principles,
   anti-slop, formats §blog/articles, and **`references/social-article-style.md`**. Use the social-article
   structure by default: thesis first, purpose sentence, thought experiment, fair comparison, pragmatic
   verdict. Give the article a title that names its subject and takeaway clearly without the body or image. Check that its promise is supported by the article; curiosity never replaces context. Use the shortest complete explanation, usually 400–700 words; expand only when the reader needs more evidence or steps. Save as `article.md` with frontmatter: `title`, `source`
   (insight/transcript path), `audience`, `status: draft`.

3. **Reader review (customer POV) + rewrite.** Read **`recoup-internal-consulting-copy-reviewer`** and run it on
   `article.md`: a fresh-context subagent role-plays the owner's ICP customer and returns reader-reaction
   notes (unclear jargon, where they tune out, trust, whether they'd share). Rewrite the article from the
   accepted notes — clearer, less technical, worth the reader's time, every fact intact. This is the
   **customer** gate; the editor gate is next.

4. **Edit the ARTICLE.** Read **`recoup-internal-consulting-copy-editor`** and run its editorial pass on the rewritten
   `article.md`. Implement accepted edits in place. Defer score/report/commit to step 8 because this
   parent workflow scores the full bundle once. Use the edited article as the source for every downstream step.

5. **Derive + gate the LinkedIn POST.** Read `recoup-internal-consulting-copy-writer` §social + **`recoup-internal-consulting-linkedin-post-architect`**.
   Write a **stand-alone** post that delivers complete value on its own (don't just paste the article intro) —
   phone-first formatting, value above the fold. The article link is **optional**: add it only as a bonus after
   an already-complete post, never a forced "read the article" / "link in comments." Save as `linkedin.md`
   (frontmatter: `source` = the article path, `hook`, `status: draft`). Then gate it: **`recoup-internal-consulting-copy-reviewer`**
   (the owner's operator/builder ICP) → rewrite from accepted notes → **`recoup-internal-consulting-copy-editor`**, edits in place.

6. **Derive + gate the EMAIL.** From the edited article, write a **single-idea broadcast email** to the list
   (`recoup-internal-consulting-copy-writer` + the routing in `email/AGENTS.md`) — a one-idea nurture send, **not** the weekly
   newsletter. Lead with the reader's takeaway; one clear CTA; it may lead with the bundle hero (`images/image1.<ext>`).
   Save as `email.md` (frontmatter: `source` = the article path, `subject`, `status: draft`). Then gate it:
   **`recoup-internal-consulting-copy-reviewer`** (the owner's subscriber/prospect ICP) → rewrite → **`recoup-internal-consulting-copy-editor`**, edits in place.

7. **Illustrate the edited article.** Invoke **`recoup-internal-consulting-article-illustrator`** with the
   approved two-part system. `images/image1.<ext>` is a bold thumbnail with a large short text hook and
   one focal illustration: any approved Recoup background color is valid when both text and artwork
   contrast clearly. Blue is not mandatory. Embed it above the article's first line. Inline figures
   (`images/image2.<ext>` onward, in reading order) are simple illustrations on pure white backgrounds
   with minimal labels, optional headlines and no repeated wordmarks. Produce only useful figures,
   roughly one per major section. Use Higgsfield for artwork and `recoup-internal-consulting-graphics`
   for editable DM Sans text and final exports; exact data diagrams may use HTML/SVG. Preview paid
   generation costs and retain prompts/job IDs. Present the final text-bearing thumbnail, not only
   its text-free source generation. Use the workspace's delivery format for `<ext>` and preserve existing
   WebP paths without adding PNG duplicates. Check the cover at 160px wide and figures at article width.
   If rendering/provider access is unavailable, flag missing assets in the report and stage the
   article without claiming figures were made. Keep all output draft until the owner approves it.

8. **Write the manifest, mark the signal, report, score, commit.** Write the bundle **`meta.yml`** — the
   approval state machine: `id` (the folder), `title`, `date`, `engine: A`, `source` (the signal path), a
   `formats:` list (one row per artifact — `article`/`linkedin`/`email`, each with `file:` + `status: draft`),
   `images:`, and a `gates:` field recording reviewer+editor ran on each format. This is the row the owner approves
   per format. Then set the consumed signal's `status: used` + `used_by:`
   the bundle path, and regenerate `signals/_index.md` (an `evergreen` insight stays evergreen — append
   the bundle to its `used_by` history instead). Write `business/ops/content-reports/<date>.md` (**Article ·
   Article gates · Post · Post gates · Email · Email gates · Hero + figures · Skipped (why) · Needs the owner**), run
   `python evals/content/score_run.py` (composite + flags at top), commit each draft why-first, stamp
   `content/_work/LAST_DRAFTED`, then stop.

## Notes
- **Article-first is the leverage.** The pillar gets atomized later into X threads, a newsletter, more LinkedIn
  angles. Spend the effort on the pillar.
- **Mine, don't manufacture.** Nothing worth a pillar → say nothing. The flywheel rewards signal, not cadence.
- Scored by `evals/content/score_run.py`: grounding, voice, non-dup on each format (article + post + email). The scorer is the floor; the reviewer+editor gates are the bar.

## Mechanical public-copy preflight

The checker ships alongside this skill. Run `python3 scripts/check_public_copy.py <public-file> ...`
on each public format and cover source, using actual workspace paths. Optionally pass
`--policy <workspace-policy.json>` with an `excluded_public_names` list. Fix blocking references
and private source paths before delivery. Missing input files fail the run. This checker cannot
verify factual accuracy, attribution, reader comprehension or raster text; perform the manual gate
and inspect exported images separately. Do not pass internal briefs or manifests as public copy.
