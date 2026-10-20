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

## Auth and research identifiers

Research endpoints live under `https://api.recoupable.dev/api/research/…` and accept the
same auth as everything else — reuse the `AUTH` array from the account-resolver reference
(`x-api-key: $RECOUP_API_KEY` preferred, or `Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

Most artist research endpoints accept the selected search result's `id` or an
artist name. Research IDs are opaque strings, separate from workspace account
UUIDs and Spotify IDs. Resolve a name, inspect the match, and reuse its `id`:

### Read without assuming a warm-up job

These GET routes are synchronous. Empty successful data is not a cache-warming
signal. Check HTTP success before reading JSON. On `402`, stop research reads:
`insufficient_credits` uses `billingUrl`; the payment-method gate uses `checkoutUrl`.
If the expected link is missing or malformed, ask the user to check account billing.
Do not substitute the other link, follow it, create a session or initiate a purchase.
For transient network errors or `5xx`, use bounded retries;
on `429`, defer research and respect `Retry-After` before a later attempt.
never loop indefinitely or turn an unavailable count into zero.

```bash
BASE="https://api.recoupable.dev/api"
research_get() {
  local path=$1 response body status attempt headers retry_after recovery
  shift
  headers=$(mktemp) || return 1
  for attempt in 1 2 3; do
    if response=$(curl -sS --max-time 90 -D "$headers" -w $'\n%{http_code}' \
      "${AUTH[@]}" "$BASE/research${path:+/$path}" "$@"); then
      status=${response##*$'\n'}
      body=${response%$'\n'*}
      case "$status" in
        200) rm -f "$headers"; printf '%s' "$body"; return 0 ;;
        402)
          rm -f "$headers"
          recovery=$(printf '%s' "$body" | jq -r '
            if type == "object" then
              if .error == "insufficient_credits" then .billingUrl else .checkoutUrl end
            else null end
            | if type == "string" and test("^https://[^[:space:]/?#]+([/?#][^[:space:]]*)?$"; "i")
              then . else "Check account billing" end
          ' 2>/dev/null) || recovery=''
          printf 'Research access requires billing (402). Review: %s\n' \
            "${recovery:-Check account billing}" >&2
          return 1 ;;
        429)
          retry_after=$(awk 'tolower($1)=="retry-after:" {sub(/^[^:]*:[[:space:]]*/, ""); sub(/\r$/, ""); print}' "$headers")
          rm -f "$headers"
          printf 'Research step stopped. Retry-After: %s. Resume manually when allowed.\n' "${retry_after:-not provided}" >&2
          return 1 ;;
        5??) ;;
        *) rm -f "$headers"; printf 'Research HTTP %s; resolve before resuming.\n' "$status" >&2; return 1 ;;
      esac
    fi
    if [ "$attempt" -lt 3 ]; then sleep "$((attempt * 2))"; fi
  done
  rm -f "$headers"
  echo 'Research unavailable after three attempts; use workspace context.' >&2
  return 1
}
```

```bash
if CANDIDATES=$(research_get "" --get --data-urlencode "q=$ARTIST_NAME" \
  --data-urlencode "type=artists"); then
  printf '%s' "$CANDIDATES" | jq '.results[]?'
fi
RESEARCH_ID=""  # Set only after inspecting the candidate's name and platform links.
```

Select the verified candidate's exact `id`; do not automatically choose the first
match. An empty ID or failed lookup is an unavailable-data condition. Continue
from workspace context and record the gap. Never fabricate an ID. If the server
returns `Retry-After`, the caller must respect it before a later request. This
helper prints the returned `Retry-After` header and stops immediately on `429`;
the caller schedules that later request. It retries only network failures or `5xx`, at most three
attempts with a 90-second timeout each.

## The signals and what each one *changes*

Read only the signals the job needs — don't fan out every call for a single caption. The
point of each row is the **decision it drives**, not the data itself.

| Signal | Call | What it changes about the content |
| --- | --- | --- |
| **Track metadata and available audio analysis** | `research/track?id=$TRACK_ID` | cut pacing, template look, caption energy (see "Audio drives the edit") |
| **Playlist placements** | `research/playlists?id=$RESEARCH_ID` → `.placements` | name-drop the real flagship playlist in a promo/caption ("now on *Lorem Vitae*") |
| **Per-platform snapshot** | `research/metrics?id=$RESEARCH_ID&source=tiktok` | pick the lead platform + a real, current number to feature |
| **Career / activity feed** | `research/career?id=$RESEARCH_ID` | spot a fresh event worth reacting to (a sync, a chart entry, a co-sign) |
| **Milestones** | `research/milestones?id=$RESEARCH_ID` | the "moment" trigger (see "React to a moment") |
| **Audience** | `context/audience.md` (workspace) | phrasing, slang, hashtags — workspace is authoritative here |
| **Trend / what's around them** | `research/web`, `research/deep` (free-text) | current sound/format references (see "Trend awareness") |

`metrics` only returns data for sources the provider actually populates — `spotify`,
`instagram`, `tiktok`, `twitter`, `facebook`, `youtube_channel`, `youtube_artist`,
`soundcloud`, `deezer`, `bandsintown`. Others are accepted-but-empty or rejected; don't
feature a number you didn't get back.

## Audio drives the edit (P1)

The song's audio analysis is the single highest-leverage signal for **video** jobs — it
turns "make a clip" into "make a clip that *moves like this song*." Read available fields once; missing analysis is not evidence of a zero value:

```bash
# Resolve the track id for the song the content is about — from RELEASE.md if present, else
# search. The search root is /research (NO trailing slash) with type=tracks:
if [ -z "$TRACK_ID" ]; then
  if TRACK_CANDIDATES=$(research_get "" --get \
    --data-urlencode "q=$SONG_TITLE $ARTIST_NAME" --data-urlencode "type=tracks"); then
    printf '%s' "$TRACK_CANDIDATES" | jq '.results[]?'
  fi
  # Inspect title, artist and platform links, then set TRACK_ID to the verified result.
fi

# When present, audio_analysis is an ARRAY of {key, value} where value is a STRING — not a
# nested object — and tempo is keyed "tempo", not "bpm". Pull fields by key:
AUDIO='{}'
if [ -n "$TRACK_ID" ]; then
  if SIGNAL=$(research_get "track" --get --data-urlencode "id=$TRACK_ID"); then
    AUDIO=$SIGNAL
  else
    echo 'Audio analysis unavailable; continue from workspace context.' >&2
  fi
fi
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
research_get "milestones?id=$RESEARCH_ID" \
  | jq -r 'if (.milestones|length)>0 then .milestones[-1] else "no fresh milestone" end'
# The career feed is a richer activity stream — chart entries, syncs, co-signs:
research_get "career?id=$RESEARCH_ID" \
  | jq -r '.career[0:5][]? | "\(.activity_date): \(.activity_text)"'
```

A fresh milestone ("crossed 2B streams", "added to *Big Playlist*", "TV sync") becomes the
headline of a promo graphic or the angle of a caption — concrete, timely, and true. If the
latest milestone is stale (months old) or absent, don't manufacture urgency; fall back to
the evergreen ask.

## Trend awareness (P5)

For "what's the move right now" / "make it feel current", pull lightweight web intelligence
and let it inform the *reference points*, not the facts:

Use the matching web-research MCP tool or the documented `POST /api/research/web`
request schema. The GET helper above does not implement POST web/deep research.

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
