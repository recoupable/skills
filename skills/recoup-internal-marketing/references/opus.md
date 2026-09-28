# Scheduling a slate through OpusClip (earned 2026-09-10 → 09-21)

Opus is the scheduler for YouTube, TikTok, Instagram, X and LinkedIn from one place. It is not the clipper
for our films (its clipper burns its own captions and emojis); our cuts are made in HyperFrames or ffmpeg
and imported as finished clips. Reference slate: the account workspace's
`content/jenny-ep1-h3-lipsync/opus/` (35 posts: six teasers plus a full film, five platforms).

## The tools (`scripts/`)

| Script | What it does |
|---|---|
| `opus-import.mjs` | Uploads each finished clip to fal storage, creates an Opus project with `curationPref.skipCurate: true` and every caption/emoji/b-roll flag off (the bundled CLI cannot send those flags, so this POSTs `/api/clip-projects` directly), then polls `clip list` for the single clip id. Ledger: `opus/projects.json`. |
| `opus-schedule.mjs` | Reads a manifest, composes the per-platform bodies, schedules through the CLI, appends a JSONL ledger, and stops on the first failure. Idempotent by `key:platform`. |

`OPUSCLIP_API_KEY` lives in the Opus dashboard (or the session environment), never in a file in the repo.

## The manifest

```json
{ "campaign": "jenny-ep1-h3-lipsync", "site": "https://recoupable.dev/build/start",
  "accounts": { "yt": {"id": "…"}, "tt": {"id": "…"}, "ig": {"id": "…", "sub": "…"}, "x": {"id": "…"}, "li": {"id": "…", "sub": "urn:li:person:…"} },
  "hashtags": "#ai #aivideo", "cta_yt": "Want this for your team? Get your free AI audit:", "cta_bio": "Free AI audit, link in bio.",
  "items": [ { "key": "A", "at": "2026-09-22T00:30:00.000Z", "yt_title": "…", "caption": "…", "x": "…" } ] }
```

Account ids come from `opusclip post accounts`; a reconnect changes them, so re-list after any reconnect
and cancel-and-recreate pending schedules (09-14).

## Per-platform body rules

| Platform | Body | Link |
|---|---|---|
| YouTube | `yt_title` + `caption` + `cta_yt` + tagged link | in the description |
| TikTok | `caption` + `cta_bio` + hashtags | "link in bio" (bio must carry the tagged link) |
| Instagram | `yt_title` + `caption` + `cta_bio` + hashtags | "link in bio" |
| X | `x` only, ≤280 chars | **no URL: Opus X rejects any URL in the text** (09-14) |
| LinkedIn | `caption` + `cta_yt` + tagged link | in the body |

Tag every link `?utm_source=<yt|tt|ig|x|li>&utm_medium=social&utm_campaign=<campaign>`.

## Pre-flight, then schedule, then verify

1. **Pre-flight every composed body** (the scheduler composes them; check what it will send, not the
   manifest): no em or en dashes, no `<placeholder>`, X under 280 with no URL, YouTube title under 100.
   Write the composed bodies to `preflight.bodies.json`; they are the strict-equality reference later.
2. **Export Opus's copy and read frames** before scheduling a finished film: confirm no Opus captions or
   emojis were burned (`opusclip clip export`).
3. Schedule. `has_conflict: false` on every row.
4. **`opusclip post list --from … --to …` is the only truth.** The ledger's `ok` means the schedule was
   accepted, not that anything posted; the cxy slate went half dark for four days on 09-11 because a
   handle rename killed the Meta token and nobody checked. Verify each morning while a slate runs, open
   the live posts, strict-check copy against `preflight.bodies.json`.

## Teaser slates from a finished film

Cut teasers from the master at beat windows (the composition build knows them), re-encoded for frame
accuracy, each with a 2.5s title card in and a 2.5s "full episode Sunday" tag out (rendered once as a
17.5s HyperFrames strip and sliced), silent audio on the cards, all normalised to the master's loudness.
One per day into the release; withhold the one step that is the reason to watch the full film.
