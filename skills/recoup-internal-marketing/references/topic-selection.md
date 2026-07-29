# Step 3 — Picking today's topic

Every post is an episode, not an ad. Before anything gets built, this page must be answerable in one
paragraph: **which arc, which character, why today.**

## The three sources, in preference order

### 1. Continue a live arc (the default)

Read `NARRATIVE.md` for storylines in progress and check `posts-log.md` for what the last episode of
that arc teased. Serialized beats compound: a recurring segment that ends on a number and asks "did
it go up?" has a built-in reason to return.

Prefer this when an arc has an open loop. Closing loops is cheaper than opening them.

### 2. Pull a logged idea

Sources of already-approved ideas:

- Upcoming canon dates in `NARRATIVE.md` (anniversaries, launches, scheduled milestones). These are
  time-bound — missing the date wastes the idea.
- Ideas parked in workspace docs or open decisions awaiting an owner ruling.
- A skeptic's objection from the comments. The canon treats real objections as the antagonist chorus:
  answer with an episode, not a rebuttal thread.

### 3. Draft a new idea

Only if it both advances an existing arc and is worth adding to the canon. If it needs a **new
storyline**, write the arc proposal as its own doc (premise, why not an existing arc, its own
guardrail, episode list) and get an owner ruling before treating it as canon. Do not quietly expand
the canon inside a post.

## The gates every pick must clear

**Arc + character named.** A post that serves no arc is an ad. Reframe or drop it.

**Consent.**
- **Internal roster artists: no gate.** No per-piece permission, no courtesy DM. Check
  `cast/<character>/` for the recorded status rather than assuming.
- **External artists: explicit likeness consent**, and their real numbers are a **separate** gate —
  confirm the exact figure with them.
- The consent status recorded in `cast/<character>/` is the source of truth. It changes; re-read it.

**Numbers.** Any figure attributed to a real artist must be measured and verified, with
measured-versus-estimated stated. This applies to numbers about **us** too: if a cost or result
cannot be verified today, publish the counts you can audit and leave the rest blank. A flattering
unverifiable number is still the thing this account exists not to do.

*Verifying a generation-cost claim without a billing dashboard* (worked 2026-07-29, after the
docs-page route 429'd): read **live official unit prices** from fal's pricing API —
`GET https://api.fal.ai/v1/models/pricing?endpoint_id=<endpoint>` with the normal inference key
(returns e.g. `$0.08/image`, `$0.01/second`) — and multiply by the **audited unit counts** on disk.
For ElevenLabs, `GET /v1/usage/character-stats?start_unix=&end_unix=` gives the day's credits and
`GET /v1/user/subscription` shows overage ($0 overage ⇒ $0 incremental on a flat plan; report the
pro-rata plan value alongside). **Disclose computed-vs-billed:** this method is official-price ×
audited-count, not billed line items — fal's usage/billing platform API needs an **admin-scoped**
key (the inference `FAL_KEY` gets `authorization_error`), so name the basis when publishing.

**NO AI disclosure in body copy.** Owner ruling, 2026-07-28. Do not write "AI generated", "made with
AI", or any equivalent into a caption, tweet, description or on-screen line. The audience already
knows, and the characters are worth more spent on the substance — on X in particular, a disclosure
sentence is ~22 of a 280-character budget.

If platform-policy labelling is wanted, use the platform's native **AI-content toggle at upload**;
that is a metadata flag, not caption text, and it costs nothing.

This **reverses** the earlier 2026-07-06 A/B note that disclosed variants were the platform-bests.
Older workspace docs may still carry that guidance; the ruling above wins. Do not reintroduce a
disclosure line because a workspace file says to.

**Collaborator, not subject.** Where a real artist features, invite them to co-post. The one
collaborative post in our data did several times the engagement of everything without one, because
the artist amplifies to their own audience. Plan the invite as part of the post, not after it.

**One idea per day.** Two assets in the same slot split our own audience and read as broadcasting. If
a build produces two good assets, sequence them across days and let the gap be a cliffhanger.

**Fiction versus fact.** Skits and dramatizations use disclosed generated likenesses. Anything
carrying a real artist's name carries only real, verified numbers.

## Sanity check before building

- Would a stranger with no context care about the first three seconds? (If the answer depends on them
  running a record label, the hook is wrong — see `HOOKS.md`.)
- Is the payoff something we can actually show, or are we describing it?
- Is there one concrete proof point, rather than a feature list?
- **What would make this post a signup, not a like?** If the honest answer is "nothing", the idea is
  brand noise. Name the CTA and the tagged link before you build (`references/conversion.md`).
