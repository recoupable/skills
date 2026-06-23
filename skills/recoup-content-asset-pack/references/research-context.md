# Research signals — ground the content in what's actually true

Workspace context (`context/artist.md`, `context/audience.md`) tells you **who the artist
is**. Research signals tell you **what's happening right now** — the song's actual tempo and
mood, where it's charting, what just hit a milestone, what's trending around the artist.
Layer research **on top of** workspace context; it never replaces it.

This is optional enrichment, not a gate. Skip it in **generic mode** (no artist). Use it
whenever an artist is named and a credential is set — grounded output beats guessed output
every time, and the data is cheap to read.

## Where research fits in the backbone

Slot it between "read workspace context" and "generate":

1. Resolve artist + workspace (account-resolver, workspace-context).
2. Read `context/artist.md` + `context/audience.md`.
3. **Read research signals (this file)** — current snapshot + the song's audio analysis.
4. Generate, letting the signals drive concrete choices (below).
5. Verify (analyze-gate), write back.

If no credential or the research API is cold/erroring, **degrade gracefully**: generate from
workspace context alone and note that signals were unavailable. Never block a content job on
research.

## Auth + the provider ID chain

Research endpoints live under `https://api.recoupable.com/api/research/…` and accept the
same auth as everything else — reuse the `AUTH` array from the account-resolver reference
(`x-api-key: $RECOUP_API_KEY` preferred, or `Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

Most research endpoints key off the **provider (Songstats) artist id** — an alphanumeric
slug like `wjcgfd9i`, *not* the Recoup `account_id`/`id` and *not* the Spotify id. Resolve it
once from the Spotify id in `RECOUP.md`, then reuse:

```bash
BASE="https://api.recoupable.com/api"
SPOTIFY_ID=$(sed -n 's/^spotifyArtistId:[[:space:]]*//p' "$ARTIST_DIR/RECOUP.md")

PROVIDER_ID=$(curl -sSL --max-time 90 "${AUTH[@]}" \
  "$BASE/research/lookup?spotifyId=$SPOTIFY_ID" \
  | jq -r '.artist_info.songstats_artist_id // empty')
```

If `$PROVIDER_ID` is empty, the artist isn't matched on the provider — skip structured
research and continue from workspace context. Don't fabricate an id.

### Cold-cache retries (don't trust the first miss)

The research API caches per artist. A first hit can return `status:"error"` or a `202
refresh_pending` while it warms — that's transient, **not** "no data". Retry a couple of
times before giving up:

```bash
research_get() {  # usage: research_get <path-with-query>
  local out=""
  for attempt in 1 2 3; do
    out=$(curl -sSL --max-time 90 "${AUTH[@]}" "$BASE/research/$1")
    [ "$(echo "$out" | jq -r '.status // "error"')" = "success" ] && { echo "$out"; return 0; }
    sleep 3
  done
  echo "$out"; return 1   # last body; caller degrades gracefully and notes the gap
}
```

## The signals and what each one *changes*

Read only the signals the job needs — don't fan out every call for a single caption. The
point of each row is the **decision it drives**, not the data itself.

| Signal | Call | What it changes about the content |
| --- | --- | --- |
| **Song audio analysis** | `research/track?id=$TRACK_ID` | cut pacing, template look, caption energy (see "Audio drives the edit") |
| **Playlist placements** | `research/playlists?id=$PROVIDER_ID` → `.placements` | name-drop the real flagship playlist in a promo/caption ("now on *Lorem Vitae*") |
| **Per-platform snapshot** | `research/metrics?id=$PROVIDER_ID&source=tiktok` | pick the lead platform + a real, current number to feature |
| **Career / activity feed** | `research/career?id=$PROVIDER_ID` | spot a fresh event worth reacting to (a sync, a chart entry, a co-sign) |
| **Milestones** | `research/milestones?id=$PROVIDER_ID` | the "moment" trigger (see "React to a moment") |
| **Audience** | `context/audience.md` (workspace) | phrasing, slang, hashtags — workspace is authoritative here |
| **Trend / what's around them** | `research/web`, `research/deep` (free-text) | current sound/format references (see "Trend awareness") |

`metrics` only returns data for sources the provider actually populates — `spotify`,
`instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`,
`soundcloud`, `deezer`, `bandsintown`. Others are accepted-but-empty or rejected; don't
feature a number you didn't get back.

## Audio drives the edit (P1)

The song's audio analysis is the single highest-leverage signal for **video** jobs — it
turns "make a clip" into "make a clip that *moves like this song*." Pull it once:

```bash
# Resolve the track id for the song the content is about — from RELEASE.md if present, else
# search. The search root is /research (NO trailing slash) with type=tracks:
TRACK_ID=$(curl -sSL --max-time 90 "${AUTH[@]}" \
  "$BASE/research?q=$(printf %s "$SONG_TITLE $ARTIST_NAME" | jq -sRr @uri)&type=tracks" \
  | jq -r '.results[0].songstats_track_id // empty')

# audio_analysis comes back as an ARRAY of {key, value} where value is a STRING — not a
# nested object — and tempo is keyed "tempo", not "bpm". Pull fields by key:
AUDIO=$(research_get "track?id=$TRACK_ID")   # cold cache returns status:error first — the helper retries
af(){ echo "$AUDIO" | jq -r --arg k "$1" '.audio_analysis[]? | select(.key==$k) | .value'; }
TEMPO=$(af tempo)        # BPM, e.g. 80.99
ENERGY=$(af energy)      # 0–1
VALENCE=$(af valence)    # 0–1 (mood: sad↔happy)
KEY=$(af key)            # e.g. C#
```

Map the numbers to concrete generation choices (`$TEMPO` is BPM; let explicit user params
override):

| Reading | Drives |
| --- | --- |
| **High tempo** (≳120 BPM) | faster cuts; shorter `trim_duration`; punchier hook timing; energetic motion prompts |
| **Low tempo** (≲90 BPM) | longer holds; slower camera moves; let a single shot breathe |
| **High energy** | stage / crowd / motion templates; high-contrast grade |
| **Low energy** | bedroom / intimate / soft-focus templates; muted grade |
| **High valence** | bright, warm, playful caption tone + color |
| **Low valence** | moody, restrained tone; cooler palette |

When choosing a template, prefer the look whose vibe matches `energy`/`valence` rather than
guessing — e.g. high energy → `artist-caption-stage`, low energy → `artist-caption-bedroom`.
This is the difference between a template that fits the song and one slapped on at random.

## React to a moment (P2)

The activity/milestone feed is a **trigger**, not just a stat. When the user asks for
"something for the launch" or "post-worthy news", check whether the artist *just* hit
something real and build the content around it:

```bash
# milestones is {milestones:[...]} (often empty). Inspect the object's fields before
# formatting — naming varies — and degrade when there's nothing fresh:
research_get "milestones?id=$PROVIDER_ID" \
  | jq -r 'if (.milestones|length)>0 then .milestones[-1] else "no fresh milestone" end'
# The career feed is a richer activity stream — chart entries, syncs, co-signs:
research_get "career?id=$PROVIDER_ID" \
  | jq -r '.career[0:5][]? | "\(.activity_date): \(.activity_text)"'
```

A fresh milestone ("crossed 2B streams", "added to *Big Playlist*", "TV sync") becomes the
headline of a promo graphic or the angle of a caption — concrete, timely, and true. If the
latest milestone is stale (months old) or absent, don't manufacture urgency; fall back to
the evergreen ask.

## Trend awareness (P5)

For "what's the move right now" / "make it feel current", pull lightweight web intelligence
and let it inform the *reference points*, not the facts:

```bash
research_get "web?q=$(printf %s "$ARTIST_NAME current trends" | jq -sRr @uri)" | jq -r '.summary // .content'
```

Use it to choose a format or sonic/visual reference that's actually current — never to invent
a stat or a quote. Treat web/deep output as *direction*, and keep anything factual sourced
from the structured signals above or the workspace.

## Close the loop: learn from what performed (P3)

Before setting the quality bar, look at what *this* artist's audience already rewarded. Pull
recent posts (uses the **row `id`**, per account-resolver) and find the top performers:

```bash
curl -sSL "${AUTH[@]}" "$BASE/artists/$ARTIST_ROW_ID/posts" \
  | jq -r '.posts | sort_by(.engagement // 0) | reverse | .[0:3] | .[] | .caption' 2>/dev/null
```

Feed those winners into the analyze-gate rubric as the benchmark ("does this hook as hard as
the artist's top recent posts?") instead of grading against a generic ideal. If engagement
fields aren't present, fall back to the standard rubric. See the analyze-gate reference.

## Why this matters

Workspace context is the moat; research signals are the *timing*. Together they take output
from "sounds like the artist" to "sounds like the artist, about the thing that's actually
happening, moving like the song that's actually playing." The data is cheap; guessing is
expensive.
