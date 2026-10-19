---
name: recoup-internal-social-ship-posts
description: INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke ONLY when the request explicitly includes "recoup-internal" (e.g. "recoup-internal draft a launch post"). Never use for customer-facing or artist requests. Write and ship data-grounded LinkedIn and X (Twitter) posts for product announcements and artist highlights, and track how they perform. Use when the user wants to draft a LinkedIn or X post, announce a feature or launch, highlight an artist or a result, plan a content calendar, decide on a CTA, or asks "how did my last post do," "what should I post," "write a post about X," or "turn this into a post/thread." This is the post copy + publishing + measurement workflow; producing a demo video is a separate asset-production step.
---

# Recoup Social — Ship Posts

Write social posts that earn engagement, then prove what worked with real numbers. This skill covers the **copy, the publish, and the measurement** for LinkedIn and X (Twitter). It deliberately does **not** cover producing media (demo videos, screen captures) — keep that distinct so the post workflow applies whether or not there's a video.

Authenticate to the Recoup API with an `x-api-key` (`RECOUP_API_KEY`) or `Authorization: Bearer` (`RECOUP_ACCESS_TOKEN`) header. Never hardcode credentials.

> **Doing a whole day of marketing, not just a post?** Start with **`recoup-internal-marketing`** —
> it owns reading the account workspace (narrative canon, hook doctrine, video styles), scraping the
> account's socials, picking the day's topic, and building the asset, then hands off to this skill for
> publish and measurement. This skill remains the owner of copy, CTA, publishing and the re-pull.

## The loop

1. **Learn** — pull how recent posts performed, so copy is grounded in evidence, not vibes.
2. **Draft** — write topic-first copy that fits the platform, the goal, and the account's story canon.
3. **Decide the CTA** — comment-gate for leads, or direct link for reach.
4. **Publish** — via the connector where supported, or hand off for manual posting.
5. **Log & re-measure** — record what went out; re-pull performance ~48h later.

Do them in order. Skipping step 1 is how posts drift back to product-led copy that flatlines.

## Principles that actually move engagement

These are defaults, not laws — treat each as a hypothesis to keep testing, and let step 1's data override them.

- **Lead topic-first, not product-first.** Open with the reader's problem or an industry question ("What's your catalog worth?"), not your brand or release notes ("X by Recoup," "We shipped…"). People react to ideas they want to be seen agreeing with.
- **Educational > launch framing.** "Here's how you'd find this out in 10 seconds" beats "we built a tool." Let the product be the proof, lower down.
- **One concrete proof point.** A single real number or example (a named result, a before/after) outperforms a feature list.
- **Broad industry hashtags, 2–3.** Discoverable topical tags reach people who don't follow you yet. Avoid brand-only tags with no topical hook.
- **Short, or substantive — not in between.** Either a punchy 1–2 liner or a post with a real insight. Avoid medium-length product blurbs.
- **One idea per day.** Don't stack two product posts in the same slot; it splits your own audience and reads as broadcasting.
- **Timing:** for B2B, a weekday mid-day window tends to reach the most people. Hold timing constant for a couple of weeks so it stops being a confounding variable when you read results.
- **Platform fit:** LinkedIn rewards comments and dwell; X rewards brevity and punishes link-in-post reach. Tailor per platform — don't cross-post identical copy.

## Step 1 — Learn from recent posts

Rank recent posts by engagement before writing. One bulk scrape covers all four platforms. Comments are the real signal for lead-gen posts (see CTA below).

```bash
# One {runId, datasetId} per linked profile. Costs $0.05 + $0.01 per requested post (50,000 + 10,000 micro-dollar credits), PER PROFILE.
curl -sS -X POST "https://api.recoupable.dev/api/artist/socials/scrape" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" -H "Content-Type: application/json" \
  -d '{"artist_account_id":"<ARTIST_ACCOUNT_ID>","posts":20}'

# Poll each run until SUCCEEDED (~1-3 min), then read `data`
curl -sS "https://api.recoupable.dev/api/apify/runs/<RUN_ID>" -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"
```

| Platform | Per post |
|---|---|
| **X** | likes, RTs, replies, quotes, bookmarks, **`viewCount` (impressions)**. Depth counts timeline items **incl. RTs/replies** — size `posts` to reach older posts |
| **YouTube** | views, likes, comments — up to `posts` videos **plus** `posts` Shorts |
| **Instagram** | likes, comments, plays — via the profile item's `latestPosts` (~12, regardless of `posts`) |
| **LinkedIn** | `engagement.{likes,comments,shares}` + reaction breakdown |

Gotchas:
- Profiles must be linked first: `GET /api/artists/{id}/socials`; add missing ones with `PATCH /api/artists/{id}` `profileUrls` (UPPERCASE keys).
- The `artist_account_id` and post ids/URNs live in the account workspace (`ACCOUNT.md`, `posts-log.md`) — read those, don't rediscover.
- IG public plays ≠ insights views (56 vs 259 on the same reel); only compare views within one source.
- Don't reach for the X connector's analytics actions — they fail (403). The scrape is the metrics source.
- Tokens last ~1h: enumerate every pull, run them in one burst.
- Need **who** reacted (the warm-lead list on a gated LinkedIn post)? Connector action `LINKEDIN_LIST_REACTIONS` with `entity: "urn:li:ugcPost:<id>"` (or `urn:li:activity:`; `urn:li:share:` may 404). Comment *bodies* still need manual reading.

Read the top performer against the flatliners and name the differences (framing, hashtags, CTA, timing). Those differences are your copy brief.

## Step 2 — Draft

**Check the story canon first.** If the account workspace has a `NARRATIVE.md` (story bible: premise, recurring cast, storylines), read it and name **which arc and which character this post serves** before writing a word. A post that serves no arc is an ad — reframe it into the story or drop it. Serialized rules live in the canon itself (recurring catchphrases, who may be fictionalized vs. who gets only verified numbers, cliffhanger beats); follow them over generic copy instincts. If the workspace has no `NARRATIVE.md`, note that to the account owner — the account is posting without a story.

Write to the brief from step 1 plus the principles above. Structure that travels well:

```
<Topic-first hook — a question or the reader's problem>

<The stakes in one line: why guessing/the status quo is costly>

<The shift: how the product changes that, in plain language, with ONE proof point>

<CTA — see step 3>

<2–3 broad industry hashtags>
```

House style: avoid em-dashes and obviously-templated phrasing — it reads machine-written. Prefer plain periods and the words a person would actually say. Mirror the voice of the account's past winners.

## Step 3 — Choose the CTA

| CTA | Use when | Mechanics | Trade-off |
|-----|----------|-----------|-----------|
| **Comment-gate** ("Comment WORD and I'll send the link") | The goal is leads / a DM list | Drives comments (algorithm boost) + a list of warm leads to DM | Link isn't in the post; slightly higher friction |
| **Direct link** | The goal is reach / immediate trial | Link in post (LinkedIn) or, on X, in a reply not the main post | Fewer comments, less lift, but frictionless |

If you comment-gate, prepare the reply/DM now so you can respond fast (speed compounds reach):

> Just sent it 🙌 Here's the link: <url>. Takes ~10 seconds. <one question to keep the thread alive>

Comment-gate on LinkedIn; use a direct link (often in the first reply) on X.

## Step 4 — Publish

**Video posts on any platform go through `POST /api/posts`** (docs: `https://docs.recoupable.dev`, posts). One call per platform: `{account_id, platform: "instagram"|"x"|"youtube"|"linkedin", video_url, description, cover_url?, title?, tags?, sub_account_id?}` where `video_url`/`cover_url` are public URLs (stage local files to blob first). It returns `202 {id, status: "publishing"}`; poll `GET /api/posts/{id}?account_id=...` until `status` is `posted` and `text_verified` is `true`, and use the returned `post_url`. The schema is strict and per-platform: YouTube needs `title` and rejects `cover_url`; X and Instagram reject `title`/`tags`; a LinkedIn company-page post sets `sub_account_id` to the organization URN. A `409 ... not connected` means the wrong `account_id`, not a missing connection: pass the account that holds the connector. It does not post the X link reply or the LinkedIn first comment; do those with the connector actions below or by hand.

Text, image and comment posts use the connector actions. **Confirm the exact parameter schema first** with `GET /api/connectors/actions` (it returns each action's JSON Schema) before composing a call.

**LinkedIn**
- Text or text + link card → `LINKEDIN_CREATE_LINKED_IN_POST` (`author`, `commentary`; add `contentLandingPage` for a link) or `LINKEDIN_CREATE_ARTICLE_OR_URL_SHARE`.
- Text + image → stage the image (`LINKEDIN_INITIALIZE_IMAGE_UPLOAD` / `LINKEDIN_REGISTER_IMAGE_UPLOAD`, or `POST /api/connectors/files` with a public image URL), then pass the image URN in `LINKEDIN_CREATE_LINKED_IN_POST`'s `images` array.
- Comment on a post → `LINKEDIN_CREATE_COMMENT_ON_POST`.

**X (Twitter):** post with `TWITTER_CREATION_OF_A_POST` (`text`, optional `media_media_ids`; reply via `reply_in_reply_to_tweet_id`). Images upload via `TWITTER_UPLOAD_MEDIA`.

## Step 5 — Log and re-measure

Record each post immediately: account, platform, the post id/URN, UTC time, the CTA used, the copy, and — when the account has a `NARRATIVE.md` — **the arc and character the post served** (continuity is what makes the next episode land; an unlogged arc breaks the serial). Then **re-pull performance ~48h later**: one bulk scrape (step 1) covers all four platforms; add `LINKEDIN_LIST_REACTIONS` only when you need reactor identities, and read gated posts' comment bodies manually. Compare week-over-week — report deltas, not all-time totals. Feed the result back into step 1 for the next post.

## Producing a demo video?

Keep it separate. This skill assumes media already exists (or that the post is text/image/link). If the post needs a product-demo video — capturing the live tool, assembling it, adding a voiceover — run that as its own asset-production step and attach the result here. Decoupling means this post workflow works the same whether today's post is a video, an image, or plain text.
