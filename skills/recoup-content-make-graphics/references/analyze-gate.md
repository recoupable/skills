# Analyze gate — verify visual output before claiming "done"

Do not assume a successful render is good. It can have the right size, format, and duration
while being glitchy, empty, off-brand, or showing the wrong subject. **Do not tell the
user an asset is ready until you've inspected it.** `POST /api/content/analyze` is the
agent's eyes.

## When to run it

After every **video** generation checkpoint — clip, composed final, upscaled output. Not just
at the very end; catch a bad clip before you spend more on it. (For still images, see the
"images" note below — the endpoint is video-only today.)

## How

```bash
curl -sS -X POST "https://api.recoupable.dev/api/content/analyze" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg v "$VIDEO_URL" --arg p "$RUBRIC" '{video_url:$v, prompt:$p}')" | jq -r '.text'
```

The field is **`video_url`** (not `video`) and the critique comes back under **`.text`**. Set
the auth header as in the account-resolver reference (`x-api-key: $RECOUP_API_KEY` or
`Authorization: Bearer $RECOUP_ACCESS_TOKEN`).

> **Stills are not supported.** Passing an image URL returns `Video analysis failed: 400`
> (verified live) — the endpoint analyzes video only. To QA a still image (cover art,
> thumbnail, quote card, carousel slide): **if your harness can view images, inspect the
> downloaded file directly** (the honest substitute for the gate) and judge it against the
> rubric below; otherwise surface the
> image to the user for sign-off. Do not claim a static image passed the analyze gate when the
> endpoint never accepted it.

## What to check (set `$RUBRIC` to the relevant bar)

- **QA** — artifacts, warping, extra fingers/limbs, subject consistency across frames,
  natural motion, no garbled text.
- **Taste** — does the first 1–3s hook attention? does visual energy match the song?
- **Platform readiness** — vertical 9:16 framing (subject not cropped), on-screen text
  legible and inside safe margins, audio-visual sync.
- **Brand fit** — matches the artist's aesthetic from `context/artist.md` when available.

Example: `RUBRIC="Rate 1-10 for social engagement. Flag any visual glitches, warped faces, or unreadable text. Is the subject centered for a 9:16 crop?"`

## Benchmark against the artist's real winners (not a generic ideal)

A 7/10 "for social" is meaningless in the abstract. When you have the artist's recent posts
(see the research-context reference, §"Close the loop"), set the bar to **their** top
performers instead of a generic one. Pull the best recent captions/thumbnails and put them
in the rubric:

```bash
RUBRIC="Compare this asset to the artist's strongest recent posts (below). Does its hook land
as hard in the first 2s? Score 1-10 and say what the winners do that this is missing.
Winners: $TOP_POSTS"
```

This makes "pass" mean *competitive with what this audience already rewarded*, not just
"technically clean". If you have no post history, use the standard rubric above.

## Acting on the result

- **Pass** → proceed / present to the user.
- **Fail** → regenerate the failing stage with adjusted params (new prompt, different
  reference, new seed) or upscale; re-analyze. Don't ship a flagged asset.
- **Borderline** → surface the analysis to the user and let them decide; don't silently
  pass it off as great.

No Stop hook enforces this gate. The agent must record actual
inspection evidence and any remaining uncertainty before delivery. Inspect still
images directly where supported. For a connected release-pack job, use its actual
QA receipts and preview/playback capabilities first; do not demand separate REST
credentials or repeat an already completed inspection. For standalone video
workflows without pack QA receipts, use the exposed analysis tool (or
`/api/content/analyze` when REST is available) at each checkpoint, with playback
as additional motion QA. If inspection is unavailable, report that gap.
For lipsync, also verify an audio stream, listen to the selected clip and inspect
mouth alignment; an audio stream alone is not proof of synchronization. Do not
spend on an unnecessary throwaway animation merely to QA a still image.

Connected pack-job QA receipts can supply inspection evidence when actually
returned. A requested analysis is not a passed analysis. For all music-bearing
assets, verify the correct recording and audio window as well as the audible
stream and timing; visual-only scores cannot establish that the music is right.
