# Step 2 — Learn from the account's own socials

The evidence step. One bulk scrape covers all four platforms.

## Prerequisites

Profiles must be linked to the artist account first:

```bash
curl -sS "https://api.recoupable.dev/api/artists/<ROW_ID>/socials" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"
```

Add missing ones with `PATCH /api/artists/{id}` and a `profileUrls` object (**UPPERCASE keys**).

The `artist_account_id` and existing post ids/URNs live in the account workspace (`ACCOUNT.md`,
`posts-log.md`) — read those rather than rediscovering them.

## The scrape

```bash
# Costs 5 credits + 1 per requested post, PER PROFILE. Returns one {runId, datasetId} per profile.
curl -sS -X POST "https://api.recoupable.dev/api/artist/socials/scrape" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN" -H "Content-Type: application/json" \
  -d '{"artist_account_id":"<ARTIST_ACCOUNT_ID>","posts":20}'

# Poll each run until SUCCEEDED (~1-3 min), then read `data`
curl -sS "https://api.recoupable.dev/api/apify/runs/<RUN_ID>" \
  -H "Authorization: Bearer $RECOUP_ACCESS_TOKEN"
```

## What each platform returns

| Platform | Per post |
|---|---|
| **X** | likes, RTs, replies, quotes, bookmarks, **`viewCount`** (impressions). Depth counts timeline items **including RTs and replies**, so size `posts` generously to reach older originals. |
| **YouTube** | views, likes, comments — up to `posts` videos **plus** `posts` Shorts. |
| **Instagram** | likes, comments, plays — via the profile item's `latestPosts` (~12, regardless of `posts`). |
| **LinkedIn** | `engagement.{likes,comments,shares}` + reaction breakdown. |

## Reading gotchas (each of these has burned us)

- **IG public plays are not insights views.** The same reel read 56 public plays vs 259 insights
  views. Only ever compare within one source.
- **LinkedIn scrapes include reposts.** Filter items by `author.publicIdentifier` before ranking, or
  someone else's engagement gets attributed to us.
- **Do not use the X connector's analytics actions.** They fail (`client-not-enrolled`). X
  impressions come from this bulk scrape. To confirm a video actually attached to a tweet without
  auth, hit the public syndication endpoint and read `mediaDetails[].type`.
- **LinkedIn comment bodies are not exposed** for personal posts, and neither are impressions. Read
  comments by hand. Reactions are available via `LINKEDIN_LIST_REACTIONS`.
- **Custom Shorts thumbnails** show on the watch page and channel but the Shorts feed may still show
  a video frame. Do not conclude the thumbnail failed.
- **The YouTube scrape is noisy and returns other channels' videos.** For a clean per-video audit
  (views, likes, `status.privacyStatus`, `status.embeddable`, publish timestamps) use the connector's
  `YOUTUBE_GET_VIDEO_DETAILS_BATCH` with a comma-joined id list — one call covers the whole posting
  history and is the right tool for timestamping a distribution change.
- **Verify the linked scrape profiles actually resolve to OUR channels.** On 2026-07-29 the official
  account's linked `youtube.com/@<handle>` turned out to be a **stranger's dormant channel** (the
  handle was squatted; scrape returned `NO_VIDEOS` and someone else's channel metadata). A profile
  URL that was never validated measures someone else — check the returned channel name/avatar the
  first time a profile is scraped, and after any profile edit.

## What to produce from it

1. **Rank recent posts by engagement**, per platform.
2. **Name the differences** between the top performer and the flatliners: hook archetype, format
   (video vs image), collaborator tagged or not, length, posting slot, CTA type.
   That list is today's copy brief.
3. **Report week-over-week deltas, not all-time totals.** Customers and owners both read deltas;
   all-time totals hide a decline.
4. **Escalate structural collapses — but diagnose against a like-for-like baseline first.** A
   collapse claim must compare the same *kind* of content on the same channel. The 2026-07-28
   "Shorts collapsed from 129–397 to 7–10" claim conflated a different content genre's outliers with
   the canon baseline: canon posts had **always** done 24–56 views, so the real trough was two videos
   deep and had already recovered by the time it was investigated (the newest post's first-24h views
   beat the canon lifetime median). Before stopping a run: pull per-video stats for the whole
   history, split by content type, and check whether the *newest* post is distributing. A real
   collapse stops the run; a mis-baselined one wastes a day.
5. **Audience–content fit is a distribution ceiling no asset quality fixes.** Same channel, same
   period: content matching the channel's existing audience did 37–397 views; content aimed at a
   different audience capped around ~30. Platforms test new posts on the channel's current audience
   first — if the account's audience does not match the content's intended audience, flag it as a
   structural decision for the owner (e.g. start a dedicated channel) rather than iterating hooks.
6. **Rank by conversion where it is known, engagement where it is not.** Attributed visits and
   signups outrank likes; where the two disagree, conversion wins (`references/conversion.md`). Be
   explicit about which posts are unattributable rather than reporting their zero as a measurement.
7. **Feed it back.** Update the Performance column in `posts-log.md` for anything at its ~48h mark
   while you are here.
