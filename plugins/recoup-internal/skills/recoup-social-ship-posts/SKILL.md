---
name: recoup-social-ship-posts
description: Write and ship data-grounded LinkedIn and X (Twitter) posts for product announcements and artist highlights, and track how they perform. Use when the user wants to draft a LinkedIn or X post, announce a feature or launch, highlight an artist or a result, plan a content calendar, decide on a CTA, or asks "how did my last post do," "what should I post," "write a post about X," or "turn this into a post/thread." This is the post copy + publishing + measurement workflow; producing a demo video is a separate asset-production step.
---

# Recoup Social — Ship Posts

Write social posts that earn engagement, then prove what worked with real numbers. This skill covers the **copy, the publish, and the measurement** for LinkedIn and X (Twitter). It deliberately does **not** cover producing media (demo videos, screen captures) — keep that distinct so the post workflow applies whether or not there's a video.

Authenticate to the Recoup API with an `x-api-key` (`RECOUP_API_KEY`) or `Authorization: Bearer` (`RECOUP_ACCESS_TOKEN`) header. Never hardcode credentials.

## The loop

1. **Learn** — pull how recent posts performed, so copy is grounded in evidence, not vibes.
2. **Draft** — write topic-first copy that fits the platform and the goal.
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

Rank recent posts by engagement before writing. Reactions are the cleanest signal the API exposes for personal posts; **comments are the real signal for lead-gen posts** (see CTA below).

Pull reactions for a known post via the connector (`POST /api/connectors/actions`):

```bash
curl -sS -X POST "https://api.recoupable.com/api/connectors/actions" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" -H "Content-Type: application/json" \
  -d '{"account_id":"<ACCOUNT_ID>","actionSlug":"LINKEDIN_LIST_REACTIONS",
       "parameters":{"entity":"urn:li:ugcPost:<ID>"}}'
```

Notes that save you time:
- Entity formats: `urn:li:activity:<id>`, `urn:li:ugcPost:<id>`, or `urn:li:share:<id>`. A feed URL's `ugcPost` id usually resolves as `urn:li:ugcPost:`; `urn:li:share:` may 404 for the same post. Try the activity/ugcPost form first.
- A post's UTC time is encoded in its numeric id: `timestamp_ms = id >> 22`.
- LinkedIn's API does **not** expose comments/impressions for **personal** posts, and post bodies often return `403`. Company-page posts unlock `LINKEDIN_GET_SHARE_STATS` / `LINKEDIN_GET_ORG_PAGE_STATS` (impressions, clicks) when reconnected with org-admin scope.
- There's no "list my posts" endpoint for personal accounts — feed post URLs/ids must be supplied.
- X analytics: `TWITTER_GET_POST_ANALYTICS`, plus `TWITTER_LIST_POST_LIKERS`, `TWITTER_GET_POST_RETWEETS`.

Read the top performer against the flatliners and name the differences (framing, hashtags, CTA, timing). Those differences are your copy brief.

## Step 2 — Draft

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

Pick the path by platform and media type. **Confirm the exact parameter schema first** with `GET /api/connectors/actions` (it returns each action's JSON Schema) before composing a call.

**LinkedIn**
- Text or text + link card → `LINKEDIN_CREATE_LINKED_IN_POST` (`author`, `commentary`; add `contentLandingPage` for a link) or `LINKEDIN_CREATE_ARTICLE_OR_URL_SHARE`.
- Text + image → stage the image (`LINKEDIN_INITIALIZE_IMAGE_UPLOAD` / `LINKEDIN_REGISTER_IMAGE_UPLOAD`, or `POST /api/connectors/files` with a public image URL), then pass the image URN in `LINKEDIN_CREATE_LINKED_IN_POST`'s `images` array.
- Comment on a post → `LINKEDIN_CREATE_COMMENT_ON_POST`.
- **Native video: not supported.** The LinkedIn connector exposes image upload only (no video upload/register action). Post videos **manually**. Get the author URN from `LINKEDIN_GET_MY_INFO`.

**X (Twitter):** post with `TWITTER_CREATION_OF_A_POST` (`text`, optional `media_media_ids`; reply via `reply_in_reply_to_tweet_id`). Images upload via `TWITTER_UPLOAD_MEDIA`.

Native video works, but the bytes can't go inline: `media` won't fetch a URL, and base64 hits the API's ~4.5MB body limit (`413`). Stage it server-side, then attach:
1. `POST /api/connectors/files` with `{url, toolSlug:"TWITTER_UPLOAD_LARGE_MEDIA"}` — the server fetches the mp4 (host it anywhere public; read once) and returns `{s3key, name, mimetype}`.
2. `TWITTER_UPLOAD_LARGE_MEDIA` with `parameters.media = {s3key, name, mimetype}` (the descriptor object, not a string) and `media_category:"tweet_video"`; wait for `processing_info.state: "succeeded"`.
3. `TWITTER_CREATION_OF_A_POST` with the returned `media_media_ids:[id]`; put the link in a reply so the main post keeps its reach.

## Step 5 — Log and re-measure

Record each post immediately: account, platform, the post id/URN, UTC time, the CTA used, and the copy. Then **re-pull performance ~48h later** (reactions + comments for gated posts) and compare week-over-week — report deltas, not all-time totals. Feed the result back into step 1 for the next post.

## Producing a demo video?

Keep it separate. This skill assumes media already exists (or that the post is text/image/link). If the post needs a product-demo video — capturing the live tool, assembling it, adding a voiceover — run that as its own asset-production step and attach the result here. Decoupling means this post workflow works the same whether today's post is a video, an image, or plain text.
