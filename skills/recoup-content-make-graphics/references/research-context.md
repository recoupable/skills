# Research signals — ground the content in what's actually true

Workspace context (`context/artist.md`, `context/audience.md`) tells you **who the artist
is**. Research signals tell you **what's happening right now** — the song's actual tempo and
mood, which tracks are gaining plays, what just happened around the artist, what's trending.
Layer research **on top of** workspace context; it never replaces it.

This is optional enrichment, not a gate. Skip it in **generic mode** (no artist). Use it
whenever an artist is named and a credential is set — grounded output beats guessed output
every time, and the data is cheap to read.

## Where research fits in the backbone

Slot it between "read workspace context" and "generate":

1. Resolve artist + workspace (account-resolver, workspace-context).
2. Read `context/artist.md` + `context/audience.md`.
3. **Read research signals (this file)** — current numbers + the song's audio analysis.
4. Generate, letting the signals drive concrete choices (below).
5. Verify (analyze-gate), write back.

If no credential or the API is erroring, **degrade gracefully**: generate from workspace
context alone and note that signals were unavailable. Never block a content job on
research.

## Auth + the ids you need

Endpoints live under `https://api.recoupable.dev/api/…` and accept the same auth as
everything else — reuse the `AUTH` array from the account-resolver reference
(`x-api-key: $RECOUP_API_KEY` preferred, or `Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

Two ids do all the work, both already in the workspace: the Recoup artist `account_id`
(the row id from account-resolver) for socials and events, and the Spotify artist id
from `RECOUP.md` for catalog and play counts.

```bash
BASE="https://api.recoupable.dev/api"
SPOTIFY_ID=$(sed -n 's/^spotifyArtistId:[[:space:]]*//p' "$ARTIST_DIR/RECOUP.md")
```

## The signals and what each one *changes*

Read only the signals the job needs — don't fan out every call for a single caption. The
point of each row is the **decision it drives**, not the data itself.

| Signal | Call | What it changes about the content |
| --- | --- | --- |
| **Song audio analysis** | the `recoup-song-analyze-audio` skill on the song file in `songs/` (tempo, energy, valence, key) | cut pacing, template look, caption energy (see "Audio drives the edit") |
| **Play-count momentum** | `research/track/playcount-deltas?isrc=&since=` per focus track | which song to feature — the one gaining, not the one you assumed |
| **Per-platform reach** | `artists/$ARTIST_ROW_ID/socials` (connected follower counts) + `spotify/artist?id=$SPOTIFY_ID` (`followers.total`, `popularity`) | pick the lead platform + a real, current number to feature |
| **Fresh moment** | `POST research/web` (last 14 days, artist-specific) | the "moment" trigger (see "React to a moment") |
| **Audience** | `context/audience.md` (workspace) | phrasing, slang, hashtags — workspace is authoritative here |
| **Trend / what's around them** | `POST research/web`, `POST research/deep` (free-text) | current sound/format references (see "Trend awareness") |

Only feature a number you actually got back. `0`/`null` follower counts mean "not
stored" — leave the platform out. Monthly listeners are not available from any endpoint.

## Audio drives the edit (P1)

The song's audio analysis is the single highest-leverage signal for **video** jobs — it
turns "make a clip" into "make a clip that *moves like this song*." Run the
`recoup-song-analyze-audio` skill on the song file (its `references/flamingo-api.md`
documents the call) and pull:

```text
TEMPO    # BPM, e.g. 80.99
ENERGY   # 0–1
VALENCE  # 0–1 (mood: sad↔happy)
KEY      # e.g. C#
```

If there is no song file in the workspace, skip this signal — never guess a tempo.

Map the numbers to concrete generation choices (`TEMPO` is BPM; let explicit user params
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

A real, recent event is a **trigger**, not just a stat. When the user asks for "something
for the launch" or "post-worthy news", check whether the artist *just* hit something real
and build the content around it:

```bash
# Recent coverage — keep only items clearly about this artist from the last 14 days
curl -sSL --max-time 90 "${AUTH[@]}" -X POST "$BASE/research/web" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg q "$ARTIST_NAME news playlist milestone" '{query:$q,max_results:10}')" \
  | jq -r '.results[] | "\(.title) — \(.url)"'

# A measured milestone: the dated play-count series for the focus track
curl -sSL --max-time 90 "${AUTH[@]}" "$BASE/research/tracks/$ISRC/measurements" \
  | jq -r '.series[-1] | "\(.date): \(.value) plays"'
```

A fresh moment ("crossed 100M plays", "added to *Big Playlist*" per a cited article, "TV
sync") becomes the headline of a promo graphic or the angle of a caption — concrete,
timely, and true, with the source link kept alongside. If the latest coverage is stale
(months old) or absent, don't manufacture urgency; fall back to the evergreen ask.

## Trend awareness (P5)

For "what's the move right now" / "make it feel current", pull lightweight web intelligence
and let it inform the *reference points*, not the facts:

```bash
curl -sSL --max-time 90 "${AUTH[@]}" -X POST "$BASE/research/web" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg q "$ARTIST_NAME current trends" '{query:$q,max_results:8}')" \
  | jq -r '.formatted // (.results[] | .snippet)'
```

Use it to choose a format or sonic/visual reference that's actually current — never to invent
a stat or a quote. Treat web/deep output as *direction*, and keep anything factual sourced
from the measured signals above or the workspace.

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
