---
name: recoup-internal-consulting-content-distribution
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Distribute one finished pillar article across every channel the same way — republish the same copy to the owned blog + LinkedIn newsletter + X (as an article, never a thread), ship the always-on companions (a LinkedIn promo post + an email to the list), point every link at the owned canonical URL, then find the live post and monitor its engagement into leads. Use after an article is written or published, on \"distribute this\", \"post it everywhere\", \"atomize this article\", \"where else should this go\", or when promoting a piece in content/04-published/."
---

# Consulting Content Distribution

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

One pillar, one copy, every channel — run the same way each time so the effort stays in the writing and the spread is mechanical. This skill **orchestrates** existing skills; it does not redefine them: `recoup-internal-consulting-copy-writer` (voice), `recoup-internal-consulting-linkedin-publisher` (LinkedIn out), `recoup-internal-consulting-email-atomizer` + `recoup-internal-consulting-outbound-email` (email), `recoup-internal-consulting-linkedin-audience` (engagement → leads), and the `integrations/linkedin/_work/` scripts (find post + engagement).

## Distribution model (adapt channels to workspace)

One finished article = the **canonical copy**. It travels as:

**Homes (the same copy, verbatim — only title/meta differ):**
- **owned company blog** — the **owned** home and the **canonical link target**. Owned beats rented (`reference/guide/06-owning-distribution.md`).
- **LinkedIn newsletter article** — the rented home where the subscribers already are (use the live account count if needed).
- **X, as an Article** (X long-form). **Never a thread.** Standing rule: same article copy on X, never a thread.

**Companions (ship with every article):**
- **A LinkedIn promo post** linking to the canonical URL (`recoup-internal-consulting-linkedin-publisher`).
- **An email to the list** ("I wrote this, here's why it matters") linking to the canonical URL (`recoup-internal-consulting-email-atomizer` → staged in `email/outbox/`, never sent).

**Parked (not solved yet — don't force it):**
- Instagram / short-form reels. Revisit once the visual short-form workflow is nailed. Skipping it is correct, not a gap.

## Link policy (what everything points to)
- **Canonical = the owned owned company blog URL** once the blog post is up. The blog page can link out to the LinkedIn newsletter version.
- **Until the blog is up:** point to the live LinkedIn article/post (it's already there). Record both on the bundle; repoint to the blog when it's live.
- **One canonical URL per article**, set in the published bundle frontmatter (`canonical:`). The promo post, email, X, and blog all point at it.

## Steps
1. **Confirm the canonical copy + link target.** The pillar in `content/04-published/<slug>/`. Pick the canonical URL: owned blog if up, else the live LinkedIn URL.
2. **Homes:** republish the *same* article body to the blog and to X (as an Article). Check whether the LinkedIn newsletter version already exists. Don't rewrite per platform; only title/meta change.
3. **Companions:**
   - Promo post via `recoup-internal-consulting-linkedin-publisher` (drafts/schedules through `integrations/linkedin/_work/publish.py`; prompts before sending).
   - Email via `recoup-internal-consulting-email-atomizer` + `recoup-internal-consulting-outbound-email`: a short broadcast to the list, `source:` = the article's insight, staged in `email/outbox/`.
   - Both link to the canonical URL.
4. **Find the post + record the URLs (no manual URL needed).** Run `python integrations/linkedin/_work/pull_posts.py --max 25 --yes`, locate the promo post by its hook, and record both URLs in the bundle frontmatter: `url:` = the linked article/pulse URL (pull_posts captures it from the post's `article.link`), `linkedin_post:` = the promo post (the engagement-monitoring target). This is how the agent stops asking the owner for any URL.
5. **Monitor → leads (close the flywheel).** Capture a baseline (likes/comments/shares) and, on a cadence, `pull_engagement.py --post-url <url>` → `enrich.py` → `crossref_attio.py` to turn engagers into net-new Attio lead candidates (`recoup-internal-consulting-linkedin-audience`). Re-check on the Friday cadence; promote to an unattended routine if the owner wants it hands-off.
6. **Track state.** Write/update `distribution.md` in the bundle: each channel (status + URL), the canonical link, the companions, and the engagement baseline. One glance = where this piece lives and how it's doing.

## Rails
- **Same copy across homes.** Blog, LinkedIn newsletter, and X article use the article verbatim. Don't fork the message. DRY: don't duplicate the full article into the repo per platform — point to the article file; keep only platform deltas (title, meta) in `distribution.md`.
- **Never a thread on X.** Always the Article feature.
- **Never auto-send / auto-post.** Email + LinkedIn default to drafts; publishing is a human action (`publish.py` prompts).
- **Voice = `recoup-internal-consulting-copy-writer`** for the promo post + email (anti-slop floor + human-texture seasoning). The article body is already governed.
- **Owned > rented.** Canonical is the owned blog whenever it exists.
- **Animated = MP4, not GIF.** For motion on a post or header, ship a muted MP4 loop (`integrations/linkedin/_work/make_loop.py` → `publish.py --media`) — Postbridge rejects GIF. **Link previews / OG cards stay static PNG** (they never animate). For the future owned-blog hero, use a `<video autoplay loop muted>` (graphics recipe `animated-hero`). Per-surface specs: `knowledge/sops/animated-media-for-posts-and-article-headers.md`.

## Filing
- Promo post → the bundle's `linkedin.md`.
- Email → `email/outbox/<date>-<slug>-article-announce.md` (status: draft).
- Distribution state + engagement baseline → the bundle's `distribution.md`.
- Recurring engagement monitoring → a cadence (Friday review) or a dedicated `routines/` worker; the capability is the `integrations/linkedin/_work/` pull scripts + `recoup-internal-consulting-linkedin-audience`.
