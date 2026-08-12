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

## Gate zero: what KIND of piece is this? (2026-08-12)

**Ask this before the arc, because it decides the structure and the arc only decorates it.**

Look at the source, not at the leaderboard:

| The source is | The piece is | Its structure |
|---|---|---|
| **A thing we shipped** (a merged PR, a new endpoint, a feature) | a **launch** | hook · the problem it removes · the solution, named · how it works · how to start using it |
| **A thing that went wrong** (an outage, a bad number, a wrong send) | an **incident** | hook · what happened · why · what changed · what is still not fixed |
| **A measured result** (an artist's earnings, a weekly delta) | a **report** | hook · the number · how it was measured · what it means · what happens next |

**A launch told as an incident is not a better launch. It is a different film.**

### The trap, and it is a strong one

Our best-performing register is confession: WE WERE WRONG was the best X post of its window and a
product changelog took 2 views on YouTube six days later. Everything in this workspace celebrates
that, and `NARRATIVE.md` makes the Integrity Arc canon. So when a **shipped feature** arrives, there
is real gravity pulling it toward "here is what we got wrong, and here is the fix."

That is how it went wrong on 2026-08-12. A new endpoint existed because a name-based lookup had
emailed a customer the wrong artist's show. The run picked the incident, cleared every gate below
(arc named, character named, why-theirs written, numbers verified) and built a film that spent its
whole runtime on our mistake. Owner ruling:

> It focuses too much on not sending any info which really hyperfocuses on the error rather than
> highlight the new feature.

It was rebuilt from scratch as a launch and came out **shorter** (34.4s against 46.1s), because
explaining what a viewer gains takes less time than explaining what we got wrong first.

**The rule:** the register is chosen by the subject, not by what scored last week. An incident that
produced a feature is a launch whose problem section is one sentence long. Our error is the *setup*,
never the subject, and it never gets more than one beat.

### The budget test

Count the beats. **A launch spends the majority of them on what the viewer gets** — the solution,
how it works, how to start. If more beats are about us (our mistake, our process, our correction)
than about them, it is an incident film wearing a launch's title. Rewrite or relabel it.

### For a launch, name the feature

Use the name the docs use, and check that the docs actually use it. On 2026-08-12 the copy invented
"Events Finder" for something the docs call "Artist Events", which would have sent every viewer who
clicked the CTA to a page with a different name on it. Either match the docs or ship a docs PR
renaming it, but never let a launch introduce a name the product does not answer to.

## The gates every pick must clear

**Why named — theirs, then ours. This gate comes first.**

Before consent, before the hook, before a single frame: write one sentence on **what the person in
the piece gets out of it**, and one on what we get. Both go at the top of the plan doc. If you
cannot write the first sentence, the piece is an ad wearing someone's name and it does not get
built.

This gate exists because the rest of this skill did not have it. Every other artist-facing rule
here is either a *permission* rule (consent, likeness, verified numbers) or a *distribution* rule
("Collaborator, not subject", justified by reach). Together they answer "may we publish this?" and
"will it travel?" — and never "what does she get?" The gap was found on 2026-08-04 by the artist,
not by us: mid-collaboration LATASHÁ asked *"what's your case for showing the numbers? like the
why?"* and nothing in this skill answered her.

**Ours is allowed to be commercial. Say it first, plainly.** We build the tool that produced the
number; their case is the proof it works. An artist who has caught us being wrong can smell a
pitch dressed as a favour, and leading with our own interest costs less than being caught
concealing it.

**Four arguments that hold up** when the piece publishes an artist's real numbers:

1. **Comparables.** There is no public benchmark for what a decade of independent work earns.
   Artists hear what labels made or what a hype cycle claimed, never an audited independent figure.
   Theirs becomes the reference point others price against, and the first to publish owns it.
2. **Financeability.** A measured, transaction-by-transaction history is an asset. "I did well" is
   a story; a ledger a stranger can audit is something to put in front of a buyer, a lender or a
   deal.
3. **The record is already public.** Chain data, play counts and sales sit there unread. Publishing
   is not exposure, it is claiming authorship of a record that exists either way. (Only true where
   the source genuinely is public — do not stretch it to cover private statements or DMs.)
4. **Scope honesty protects them.** Shipping a partial, clearly-labelled figure sets a **floor**
   that later work raises. It reads as conservative rather than inflated, and it stops a
   still-incomplete number being mistaken for a career total.

**State the risk in their terms, in the same breath.** Not a disclaimer at the end — the sentence
that could make them say no. Publishing earnings raises a target profile (acutely so for an artist
who has been hacked); historical dollars get misread as current wealth; a person can be flattened
into a figure. Naming the risk unprompted is what makes it consent rather than a signature.

**Then let them decide, and take no for an answer.** A yes obtained by not mentioning the downside
is worth less than a no.

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
