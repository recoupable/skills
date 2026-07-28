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

## What to produce from it

1. **Rank recent posts by engagement**, per platform.
2. **Name the differences** between the top performer and the flatliners: hook archetype, format
   (video vs image), collaborator tagged or not, length, posting slot, CTA type.
   That list is today's copy brief.
3. **Report week-over-week deltas, not all-time totals.** Customers and owners both read deltas;
   all-time totals hide a decline.
4. **Escalate structural collapses.** If a platform's numbers drop an order of magnitude (e.g. Shorts
   views falling from the hundreds to single digits), that is a distribution problem and it outranks
   whatever today's post was going to be. Say so before building.
5. **Rank by conversion where it is known, engagement where it is not.** Attributed visits and
   signups outrank likes; where the two disagree, conversion wins (`references/conversion.md`). Be
   explicit about which posts are unattributable rather than reporting their zero as a measurement.
6. **Feed it back.** Update the Performance column in `posts-log.md` for anything at its ~48h mark
   while you are here.
