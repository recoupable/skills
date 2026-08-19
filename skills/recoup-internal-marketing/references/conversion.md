# Step 6 — Conversion: tagged CTA links and reading the result

The goal of a post is a **paying subscriber**, and knowing which post caused them. This page is how a
post becomes attributable, and what to read at the re-pull.

## Open every run with the funnel numbers (step 2a)

The social scrape cannot see the result. Before reading a single like, pull from
`recoup-internal-sales` / `recoup-internal-funnel-valuation-pipeline`:

| Read | Why it comes first |
|---|---|
| **trials / subscriptions started since the last run** | the actual result; everything else is a leading indicator |
| **signups (Privy) and cards (Stripe)** | separates "interest" from "paid" |
| **is the likely destination converting at all** | if it converts nobody, a better asset changes nothing |

**Known state 2026-07-30, re-verify rather than assume:** `/pricing` is the #2 marketing page (79
visitors in the 30 days to 07-29) and the last real trial signup and last new card were both
**2026-06-06** — pricing traffic producing zero trials
([chat#1902](https://github.com/recoupable/chat/issues/1902)). The post-signup path has reproduced
defects too: a funded outreach customer ran a valuation, saw nothing, re-ran the whole flow, hit a
second bug via a referral, and gave up on the UI
([chat#1912](https://github.com/recoupable/chat/issues/1912)).

While that is true, **more traffic is not the constraint** and the funnel guardrail in `SKILL.md`
applies: report it, get a decision, and prefer fixing the path over shipping into it.

## The destination is half the conversion

A post and its landing page are one artifact. Judge them together:

- **Continuity.** The page should visibly continue the post's promise. A post about a decade of one
  artist's catalog should not land on a generic homepage — the viewer arrives mid-thought and has to
  restart.
- **A single next action.** If the page offers four things, the post converted nobody in particular.
- **Proof that it works today.** Load it on the day you publish. "It worked last week" is not a
  check.

> **Status 2026-07-28: the capture chain is NOT built yet.** Tracked as **row 29** of
> [chat#1889](https://github.com/recoupable/chat/issues/1889). Until it ships, **tag the links anyway**
> (it costs nothing and the data is retroactively useful once capture lands) and be explicit that
> conversion is unmeasured rather than implying engagement means it worked.

## The link convention

Standard UTM parameters, because every analytics tool parses them natively and we may not be the only
consumer:

```
https://recoupable.dev/?utm_source=<platform>&utm_medium=social&utm_campaign=<project-slug>
```

| Param | Value | Source |
|---|---|---|
| `utm_source` | `ig` · `x` · `yt` · `li` | the platform being posted to |
| `utm_medium` | `social` | constant, so paid/email stay separable later |
| `utm_campaign` | the content project slug, e.g. `roster-content-recipe` | already exists as `cfg.slug` in `post.config.mjs` |

Add `utm_content` only when genuinely A/B testing two variants of the same post.

**On X a tagged link is free.** X counts *any* URL as 23 weighted characters regardless of its literal
length, so a full UTM string costs exactly what a bare `recoupable.dev` costs. The platform where
characters are scarcest is the one where this is free.

## Per-platform placement, and the Instagram problem

| Platform | Where the link goes | Attributable per post? |
|---|---|---|
| **X** | inline in the main body | ✅ yes |
| **YouTube** | description (clickable) | ✅ yes |
| **LinkedIn** | first comment, never the body (LI throttles body links) | ✅ yes |
| **Instagram** | **bio only — captions do not render clickable links** | ⚠️ campaign-level at best |

**Instagram is the real limitation and it must not be glossed over.** A per-post tagged link is
impossible in an IG caption. Options, in order of preference:

1. **Update the bio link to the current campaign's tagged URL when you post.** Gives campaign-level
   attribution for the window that post is the newest. Cheap, no build.
2. A link-in-bio landing page listing recent posts, each linking out tagged. More build, better
   granularity.
3. Accept IG as unattributed and read it on engagement only. **Say so** rather than reporting an IG
   zero as if it were measured.

Because IG is our best-performing video platform, treating "IG produced no attributable signups" as
"IG doesn't convert" would be a straightforward measurement error.

## The capture chain (what row 29 builds)

Four pieces, because the click and the signup happen on different hosts:

1. **`marketing`** (`recoupable.dev`) reads `utm_*` on first load and writes a **first-touch** cookie
   `rcp_attr` — `{source, medium, campaign, landing, ts}`, `Domain=.recoupable.dev`,
   `Max-Age` 90 days, `SameSite=Lax`. **First-touch, never overwritten:** last-touch would erase the
   post that actually earned the visit.
2. **`marketing`** appends the attribution to the outbound **"Open app"** CTA
   ([marketing#52](https://github.com/recoupable/marketing/pull/52)) as an opaque param, so the chain
   survives even if cookie scoping fails across the subdomain hop.
3. **`chat`** (`chat.recoupable.dev`) reads cookie-or-param on the auth-completion path and POSTs it to
   api once, on account creation.
4. **`api` + `database`** persist one row per account.

**Resolved 2026-08-18: Vercel Analytics DOES capture `utm_*` automatically, on both properties, with
no app code.** Pieces 1–2 are already a readable dashboard; only the **signup join** (3–4) is new
work. The pull is below — run it, don't rebuild it.

## The attributed-visits pull (verified 2026-08-18)

Attributed visits are read from the Vercel Web Analytics query API, authenticated with the local
Vercel CLI's login token. No dashboard needed, no app code involved.

```bash
# Auth: the Vercel CLI's token (team `recoup`; `vercel whoami` to confirm login)
TOKEN=$(python3 -c "import json;print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])")

# Time range MUST be epoch milliseconds in `since`/`until` — ISO `from`/`to` errors with
# "missing required property `since`".
SINCE=$(python3 -c "import datetime;print(int(datetime.datetime(2026,7,20).timestamp()*1000))")
UNTIL=$(python3 -c "import datetime;print(int(datetime.datetime.now().timestamp()*1000))")

# One call per property; run for BOTH, then split by source.
#   chat.recoupable.dev (where /keys CTAs land): prj_6X7T8B99hcyA8fVwVhk4Z6mnTiZo
#   recoupable.dev (marketing site):             prj_UxIFrlvr1a6XOs15Wu5szHh4iauI
curl -sS "https://api.vercel.com/v1/query/web-analytics/visits/aggregate?projectId=<PRJ_ID>&teamId=recoup&since=$SINCE&until=$UNTIL&by=utmCampaign&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

Gotchas that cost time the first run:

- **`limit` defaults to 10** and silently truncates — always pass `limit=50` or campaigns vanish.
- **Allowed `by` values** (anything else 400s): `hour, day, week, month, year, country, deviceType,
  environment, requestPath, referrerHostname, osName, browserName, route, utmSource, utmMedium,
  utmCampaign, utmContent, utmTerm, flags`. Use `utmCampaign` for per-post, `utmSource` for
  per-platform, `referrerHostname` to catch **untagged** social clicks (`t.co`, `l.instagram.com`,
  `linkedin.com`) that the utm read misses.
- **Query both projects every time.** `/keys` CTAs land on the chat project; homepage/`/pricing`
  CTAs land on marketing. Reading only one undercounts the slate.
- Read this at **step 2a** (is conversion readable?) and again at the **~48h re-pull**.

What this pull cannot see: signups. Visits stop at the pageview until the join (pieces 3–4, row 29
of [chat#1889](https://github.com/recoupable/chat/issues/1889)) ships — keep declaring signups
unreadable until it does.

## What to read at the re-pull

In this order, because each is closer to revenue than the last:

1. **Engagement** — the leading indicator (`references/learn-from-socials.md`).
2. **Attributed visits** — per `utm_source` / `utm_campaign`, via the pull above.
3. **Signups** — accounts created from those visits. `recoup-internal-sales` and
   `recoup-internal-funnel-valuation-pipeline` own the Privy / Stripe / credits / Attio reads.
4. **Funnel stage** — did any become an Attio **Valuation Leads** row? That stage is created
   automatically when a valuation runs, so a signup that never runs one never appears.

Log engagement **and** conversion in `posts-log.md`, including zeros. Report deltas, not totals.

## The trap this exists to prevent

A post can win on every engagement metric and produce nothing. Without attribution, that post gets
copied — and the next run optimises for the thing that felt good. **Where engagement and conversion
disagree, conversion wins**, and the only way to know they disagree is to measure both.
