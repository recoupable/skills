# Music Flamingo API — call contract

Shared reference for the `recoup-song-*` skills. It documents the one endpoint
these skills depend on: Recoup's audio language model ("Music Flamingo").

## Entry points

The same analysis is reachable four ways. REST and CLI accept `audio_url`; MCP
also accepts a host-provided chat attachment and normalizes it to that contract.

| Interface | How to call | Auth |
|---|---|---|
| REST (analyze) | `POST /api/songs/analyze` | Bearer **or** `x-api-key` |
| REST (presets) | `GET /api/songs/analyze/presets` | Bearer **or** `x-api-key` |
| CLI | `recoup songs analyze`, `recoup songs presets` | **`x-api-key` only** |
| MCP | tool `analyze_music` | Bearer |

**Prefer MCP when the host exposes Recoup tools**, especially for chat attachments.
Use REST otherwise. It accepts both auth methods, so it works in a Recoup
sandbox (which exposes `RECOUP_ACCESS_TOKEN`, a bearer token) and with a raw API
key. The CLI is a convenience but authenticates with `x-api-key` **only** — it
will not work from a sandbox that has only `RECOUP_ACCESS_TOKEN` set. Use MCP
`analyze_music` when the host already exposes Recoup MCP tools.

## Auth

REST accepts exactly one of:

- `Authorization: Bearer $RECOUP_ACCESS_TOKEN` — short-lived token set in Recoup
  sandboxes. Prefer this.
- `x-api-key: $RECOUP_API_KEY` — a long-lived API key.

If neither is set, the user is not authenticated — tell them to sign in or
provide a key rather than retrying.

**Never put `account_id` in the request body.** This endpoint derives account
context from auth and ignores account overrides.

## Base URL

The API answers on two hosts; examples below resolve the base from env so a skill
works in either environment:

- `RECOUP_API` — full base including `/api` (e.g. `https://api.recoupable.dev/api`)
- `RECOUP_API_URL` — host only (e.g. `https://api.recoupable.dev`)
- Default when neither is set: `https://api.recoupable.dev`

(The public docs are inconsistent about the canonical host; honoring the env
vars avoids hard-coding the wrong one.)

## Request contract

Body fields (schema: `validateFlamingoGenerateBody`):

| Field | Type | Notes |
|---|---|---|
| `preset` | string enum | one curated preset, or `full_report` |
| `prompt` | string 1–24000 | free-form question |
| `audio_url` | public URL | required for every preset (see below) |
| `max_new_tokens` | int 1–2048 | default 512 |
| `temperature` | number 0–2 | default 1.0 |
| `top_p` | number 0–1 | default 1.0 |
| `do_sample` | boolean | default false |

Rules (enforced server-side):

- Provide **exactly one** of `preset` or `prompt`. Sending both is a 400; sending
  neither is a 400.
- **Every preset requires `audio_url`**, including `full_report`. There is no
  metadata-only preset today.
- Custom prompts also require audio. There is no text-only analysis path.
- The REST endpoint accepts **URLs**, not local paths or raw file bytes. For chat
  uploads, prefer the MCP file input below or an accessible attachment URL exposed
  by the host. Do not ask users to host files themselves. If no attachment transfer
  capability exists, explain the specific host/tool limitation honestly.

## Response contract

Single preset or custom prompt:

```json
{ "status": "success", "preset": "catalog_metadata", "response": {}, "elapsed_seconds": 8.0 }
```

`response` is parsed JSON for JSON presets and plain text for text presets. If
JSON parsing fails server-side, it falls back to the raw string.

Full report:

```json
{ "status": "success", "preset": "full_report", "report": {}, "elapsed_seconds": 30.5 }
```

`full_report` runs all 13 presets in parallel; the `report` object has one key
per section. If a section fails it is replaced by an error object instead of
failing the whole report.

Errors:

```json
{ "status": "error", "error": "The \"catalog_metadata\" preset requires an audio_url" }
```

## Presets

| Preset | Format | What it returns |
|---|---|---|
| `catalog_metadata` | JSON | genre, subgenres, mood, BPM, key, time signature, instruments, vocal type/style, production style, energy, danceability, themes, similar artists, one-line description |
| `mood_tags` | JSON | 8–10 mood/vibe/energy tags + one primary mood |
| `lyric_transcription` | text | lyrics with section headers, repetition condensed |
| `mix_feedback` | text | mix critique: low end, vocals, air/harshness, stereo image, dynamics, concrete fixes |
| `song_description` | text | sub-100-word marketing description for playlist/press/blog |
| `music_theory` | JSON | key, scale, BPM, time signature, chord cycle, sections, duration, harmonic notes |
| `similar_artists` | JSON | five comparable artists with reasoning |
| `sample_detection` | text | possible samples/interpolations/references + confidence |
| `sync_brief_match` | JSON | visual scenes, emotional arc, energy curve, sync moments, searchable genres, avoid-for contexts |
| `audience_profile` | JSON | age range, gender skew, lifestyle tags, contexts, platforms, playlist types, comparable fanbases, marketing hook |
| `content_advisory` | JSON | explicit flag, profanity, thematic flags, brand-safety rating, radio friendliness, content summary |
| `playlist_pitch` | text | editorial pitch: summary, why it fits, suggested playlists, comparable tracks |
| `artist_development_notes` | text | A&R notes: vocal, songwriting, production, commercial potential, next steps |
| `full_report` | JSON | all 13 sections combined |

Discover presets at runtime instead of guessing names:

```bash
curl -sS "$API_BASE/songs/analyze/presets" "${AUTH[@]}" | jq '.presets[] | {name, requiresAudio, responseFormat}'
```

## Call patterns

### REST (primary — works with Bearer or API key)

```bash
# Resolve base URL from env (default to the vercel host)
if [ -n "$RECOUP_API" ]; then
  API_BASE="${RECOUP_API%/}"
else
  RAW_API_URL="${RECOUP_API_URL:-https://api.recoupable.dev}"
  API_BASE="${RAW_API_URL%/api}/api"
fi

# Pick auth: prefer the sandbox bearer token, fall back to an API key
if [ -n "$RECOUP_ACCESS_TOKEN" ]; then
  AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
elif [ -n "$RECOUP_API_KEY" ]; then
  AUTH=(-H "x-api-key: $RECOUP_API_KEY")
else
  echo "Missing RECOUP_ACCESS_TOKEN or RECOUP_API_KEY — ask the user to authenticate." >&2
  exit 1
fi

# One preset
curl -sS -X POST "$API_BASE/songs/analyze" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg audio "$AUDIO_URL" '{preset:"catalog_metadata", audio_url:$audio}')" | jq

# Full report (13 presets in parallel — slower, more model spend)
curl -sS -X POST "$API_BASE/songs/analyze" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg audio "$AUDIO_URL" '{preset:"full_report", audio_url:$audio}')" | jq

# Custom prompt
curl -sS -X POST "$API_BASE/songs/analyze" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg audio "$AUDIO_URL" '{prompt:"Focus on vocal harshness and mono compatibility.", audio_url:$audio}')" | jq
```

### CLI (convenience — only when `RECOUP_API_KEY` is set)

```bash
recoup songs presets --json
recoup songs analyze --preset catalog_metadata --audio "$AUDIO_URL" --json
recoup songs analyze --preset full_report --audio "$AUDIO_URL" --json
recoup songs analyze --prompt "Summarize the lyrical themes." --audio "$AUDIO_URL" --json
```

### MCP (when the host exposes Recoup MCP tools)

Inspect the installed tool schema first; older connections may still expose only
`audio_url`. Updated `analyze_music` declares `_meta["openai/fileParams"]: ["file"]`
and accepts **exactly one** of `file` or `audio_url`, plus a preset or custom prompt.

For a chat attachment, pass the actual host-supplied file object:

```json
{
  "preset": "catalog_metadata",
  "file": {
    "download_url": "https://host.example/temporary-audio-download",
    "file_id": "host-provided-file-id",
    "mime_type": "audio/mpeg",
    "file_name": "My song.mp3"
  }
}
```

The values above illustrate the shape only; never invent them. `download_url` and
`file_id` are required; `mime_type` and `file_name` are optional. The tool uses the
HTTPS download URL internally, checks that it serves audio before starting the
model, and excludes MCP audio source URLs from usage-event resource links. It does not publish or
copy the audio to permanent public storage. File IDs and names are not analysis
instructions. Host support must be tested; declaring a file input does not prove
that every host can supply one.

For an existing accessible audio link, call with
`{ "preset": "catalog_metadata", "audio_url": "https://…/song.mp3" }`.
Never include `account_id`, local filesystem paths, or both source fields. Refresh
an expired host download URL through available host file APIs, or ask the user to
reattach the song. Do not send the same expired URL repeatedly.

For a selected local file, the existing `upload_release_pack_asset` tool supports
private transfer without creating a release pack: request `mode: "signed_url"`
with the audio MIME type, transfer the selected bytes using the host's local file
capability, then call `mode: "finalize"` with the returned `storage_key`. Analyze
only the URL returned after finalization verifies the bytes. Do not use public
site assets as a workaround, invent a file ID, or ask the user to host their song.
If that upload tool is absent, refresh the connected tool catalog; do not treat
an already attached local file as missing audio. Retention of private storage is
independent of download-link expiration.

Native file-input contract: https://developers.openai.com/plugins/reference#define-file-inputs

## Gotchas

- **Attachments first in MCP.** Use the host file object when available. REST
  still needs a downloadable URL; local paths are not remote file access.
- **`full_report` fans out to 13 model calls.** Don't default to it; use it only
  when the user asks for a complete analysis, and never blindly across a catalog.
- **Smallest useful preset wins.** Pick the one preset that answers the question,
  or a short chain, before reaching for `full_report`.
- **CLI ≠ Bearer.** The CLI authenticates with `x-api-key` only. In a sandbox with
  only `RECOUP_ACCESS_TOKEN`, use REST.
- **No `account_id` in the body.** Auth determines the account.
- **Return interpretation, not raw JSON dumps.** Summarize for the user; persist
  the raw JSON to a file if you are in a workspace.
