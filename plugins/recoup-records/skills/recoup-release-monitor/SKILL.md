---
name: recoup-release-monitor
description: Confirms a new release has dropped for an artist and builds a launch-day alert from the Recoup research API. Use when asked to "monitor [artist]'s release", "did [artist]'s single drop", "confirm the release went live", "watch for the drop", "set up a launch alert", or as the post-release monitor armed by a release campaign. Checks the activity feed + catalog + early playlist/streaming signal, and refuses to fabricate numbers. Needs the artist name (and ideally the expected release title/date).
---

# New Release Monitor

Confirms a release actually went live and assembles a **launch-day alert**: what
dropped, where it's landing (editorial adds, chart entries), and the first
streaming signal — so a campaign can react on day one instead of guessing.

This is a tracking skill. For a one-shot full sweep use `recoup-artist-research`;
for the recurring Monday artifact use `recoup-artist-brief`.

The endpoint contract (auth, base URL, params, response shapes, credit costs)
is in `references/endpoints.md` and `references/response-shapes.md`. Read them
before calling. They ship alongside this skill.

## Setup

```bash
export RECOUP_API_KEY="recoup_sk_..."        # already set in Recoup sandboxes
export RECOUP_API="https://api.recoupable.com/api"
```

## Inputs

- **artist** (required) — name or provider `id`.
- **expected title** (optional) — the single/EP/album you're watching for.
- **expected date** (optional) — the planned release date.

If you're inside a release workspace, read
`releases/{artist-slug}/{release-slug}/RELEASE.md` / `assumptions.yaml` for the
expected title + date instead of asking.

## Workflow

### 1. Pull the activity feed + catalog (parallel, low-credit)

```bash
# Activity feed — releases, playlist adds, chart entries (sort by activity_tier asc)
curl -s "$RECOUP_API/research/milestones?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
# Catalog — newest tracks carry release dates
curl -s "$RECOUP_API/research/tracks?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
# Career activity feed — broader notable events
curl -s "$RECOUP_API/research/career?artist={ARTIST}" -H "x-api-key: $RECOUP_API_KEY" &
wait
```

### 2. Decide: did it drop?

- **Confirmed** — a track matching the expected title (or any release dated
  on/after the expected date) appears in `tracks`/`milestones`. State the title,
  date, and where you saw it.
- **Not yet** — nothing matches. Say so plainly with the most recent release as
  context; suggest when to re-check. **Do not invent a confirmation.**

To resolve an exact track ID for deeper checks, search:

```bash
curl -s "$RECOUP_API/research?q={TITLE}&type=tracks" -H "x-api-key: $RECOUP_API_KEY" | jq '.results[0]'
```

### 3. If confirmed, gather the launch signal

```bash
# Early Spotify reach — listeners, popularity, editorial playlist count, reach
curl -s "$RECOUP_API/research/metrics?artist={ARTIST}&source=spotify" -H "x-api-key: $RECOUP_API_KEY" &
# Editorial / playlist placements landing the release
curl -s "$RECOUP_API/research/playlists?artist={ARTIST}&platform=spotify&status=current" -H "x-api-key: $RECOUP_API_KEY" &
wait
```

For per-track playlist depth, pass the track `id` to `/research/track/playlists`
(5 credits — only when the launch warrants it).

## Output — the launch alert

```markdown
# Launch Alert — {Artist} · {Release Title}
**Status:** LIVE (confirmed {date}) | NOT YET (last checked {date})

## What dropped
{Title, type (single/EP/album), release date, source where confirmed.}

## Where it's landing
- Editorial / playlist adds: {names + follower reach, or "none yet"}
- Chart / milestone entries: {from milestones, or "none yet"}

## First signal
| Metric | Reading |
|---|---|
| Spotify monthly listeners | {monthly_listeners_current or "—"} |
| Spotify popularity | {popularity_current or "—"} |
| Editorial playlists | {playlists_editorial_current or "—"} |

## React now
{1–3 concrete next moves for the campaign, e.g. "pitch to "—" curators who added
the last single", "the drop is confirmed — fire the day-of content."}
```

Inside a release workspace, save to
`releases/{artist-slug}/{release-slug}/tracking/launch-alert-$(date +%F).md`.
Otherwise return it in chat.

## Guardrails

- **No fabricated confirmation.** "Live" requires a dated match in the feed/catalog.
- **No invented numbers.** Missing metric → `—`, never a guess.
- **Snapshots, not history.** Metrics are current readings (Songstats-backed);
  treat the first reading as a baseline, not a trend.
- **No `account_id` games** — auth determines the account; pass `artist=`.

## References

- `references/endpoints.md` — full curl examples per endpoint, params, credits.
- `references/response-shapes.md` — actual JSON shapes per endpoint.
