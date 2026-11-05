---
name: recoup-song-analyst-report
description: Write a full analyst report on one song from its audio — verdict, first listen, nine dimension cards, sonic identity, production craft with seven annotated bands, songwriting with timed key lines, structure, market, comparables, sync (cut windows, scene archetypes, edit points), growth and a weighted score — built from measured numbers plus a 36-question listening pass, fact-checked by script and rendered as one HTML page. Use for "full analyst report on this song", "deep-dive report on this track", "song report card", "score this song", or "everything a supervisor or A&R needs on this record". Requires a Recoup API key and a public audio URL. For a quick BPM/key/mix answer use recoup-song-analyze-audio; for only the clip moment use recoup-song-find-hook; for a pitch email use recoup-song-placement-pitch.
---

# Recoup Song — Analyst Report

One song in, one analyst-grade report out. The report reads like a senior analyst's write-up:
an opinionated verdict, a first listen, nine dimension cards (one line and three typed bullets
each), sonic identity, production craft with seven annotated frequency bands, songwriting with
timed key lines, structure, market position, comparables, sync with cut windows, scene archetypes
and edit points, growth, and a seven-part weighted score. Numbers and timestamps come from a
measurement of the file; what the song sounds like comes from a listening model answering 36
one-line questions; the lyric comes from word-timed transcription. You (the agent) write the
prose under strict facts-only rules, a script checks every timestamp, quote, name and number,
and a second script renders the page.

Scripts ship alongside this skill in `scripts/` (Python 3, stdlib only unless noted). Set `SKILL`
to this skill's folder and run them from the folder where the outputs go.

## When to use

- The user wants the whole picture on one song: a report to share, a supervisor or A&R read, a
  pitch-prep document, a scored comparison between two mixes.
- Not for a quick tag or one question (BPM, key, mood, mix note): use recoup-song-analyze-audio.
- Not for many songs in one go: each report costs real money (see "Cost"); confirm the list and
  the total with the user first.

## Prerequisites

- **A Recoup API key** in `RECOUP_API_KEY` (sent as `x-api-key`). In a Recoup sandbox the bearer
  token `RECOUP_ACCESS_TOKEN` works too. Never put `account_id` in a request body.
- **A public audio URL** for the song (MP3 or WAV is safest). The API fetches it; local files
  cannot be uploaded. If the user only has a local file, ask for a hosted link.
- **python3** for the bundled scripts, and **jq** and **curl** for the calls below.
- Optional: **librosa** (`pip3 install librosa`) for the local arrangement probe, and **node**
  for the script check in `scripts/check_render.py`.

```bash
SKILL=/path/to/recoup-song-analyst-report      # this skill's folder
API_BASE="${RECOUP_API_URL:-https://api.recoupable.dev}"; API_BASE="${API_BASE%/}"; API_BASE="${API_BASE%/api}/api"
if [ -n "$RECOUP_API_KEY" ]; then AUTH=(-H "x-api-key: $RECOUP_API_KEY")
elif [ -n "$RECOUP_ACCESS_TOKEN" ]; then AUTH=(-H "Authorization: Bearer $RECOUP_ACCESS_TOKEN")
else echo "No Recoup credentials: ask the user for an API key" >&2; fi
AUDIO_URL="https://example.com/song.mp3"
```

In an artist workspace, write every output to `songs/{song-slug}/analysis/report/`.

## Workflow

Steps 1–3 can run in parallel; step 3's line builder needs step 1's `measurement.json`.

### 1. Measure → `measurement.json`

```bash
jq -n --arg audio "$AUDIO_URL" --argjson bpm "${TEMPO_HINT:-null}" \
  '{audio_url: $audio, describe: false} + (if $bpm then {tempo_hint: $bpm} else {} end)' |
  curl -sS -X POST "$API_BASE/songs/moments" "${AUTH[@]}" -H "Content-Type: application/json" -d @- > measurement.json
jq '{status, duration_seconds, tempo_bpm, sections: (.sections|length), moments: (.moments|length),
     extended: {lufs: has("lufs"), true_peak: has("true_peak_dbtp"), key: has("key"), bands: has("band_profile"),
                fingerprint: has("fingerprint"), drops: has("mute_drops"), edit_points: has("edit_points")}}' measurement.json
```

- `describe: false` keeps it at the flat measurement price; the listening pass in step 2 covers
  the descriptions. Send `tempo_hint` (a BPM from the user or the file's metadata) when known.
- Every measurement has duration, tempo, overall loudness (`loudness_lufs`), ending (fade or
  cold), named sections, moments (intro, vocal hook, chorus lift, build-up, climax, breakdown,
  outro) with :06/:15/:30 cut windows on the beat grid, and a per-second energy curve.
- The **extended measurement** adds `lufs`, `true_peak_dbtp`, sample peak, crest, loudness
  range, a delivery-ready flag, stereo width, `key`, `time_signature`, the seven-band
  `band_profile`, the six-axis `fingerprint`, valence and arousal, `mute_drops` (drops and
  breakdowns), a chord loop, typed `edit_points` and an ending detail; it also honours
  `tempo_hint`. On a host that has not released it, those fields are absent and the report says
  less: key and time signature come from the listening model (`key_source: "model"`), production
  bands are annotated from the listening answers without shares, edit points are built from
  section starts and moment cuts, and no LUFS or dBTP figure may appear in prose. Note the missing
  fields once in `technical.notes`.
- A 404 means this host has not released the measurement route. Stop and tell the user the full
  report needs it; offer recoup-song-analyze-audio for a lighter read.

### 2. Listen → `answers.json`

The 36 questions are in `references/questions.json` (`id`, profile `field`, one-line `q`). Ask
them all on one download of the audio:

```bash
jq --arg audio "$AUDIO_URL" \
  '{audio_url: $audio, do_sample: false, prompts: [.[] | {id, prompt: .q, max_new_tokens: 400}]}' \
  "$SKILL/references/questions.json" > batch.request.json
code=$(curl -sS -o batch.json -w '%{http_code}' -X POST "$API_BASE/songs/analyze/batch" "${AUTH[@]}" \
  -H "Content-Type: application/json" -d @batch.request.json)
[ "$code" = 200 ] && jq '[.answers[] | {(.id): .response}] | add' batch.json > answers.json
jq 'length' answers.json        # expect 36
```

**Fallback** when the batch route answers 404 (not released on this host): one call per
question. Tell the user first: it costs about $2 a song against about $0.20 batched. Any other
error (402 credits, 422 audio URL not reachable or not audio, 502 model failure) is not a reason
to fall back: report it and stop.

```bash
mkdir -p answers
jq -c '.[]' "$SKILL/references/questions.json" | while read -r q; do
  id=$(jq -r .id <<<"$q"); [ -s "answers/$id.json" ] && continue
  jq -n --arg audio "$AUDIO_URL" --argjson q "$q" \
    '{prompt: $q.q, audio_url: $audio, max_new_tokens: 400, do_sample: false}' |
    curl -sS -X POST "$API_BASE/songs/analyze" "${AUTH[@]}" -H "Content-Type: application/json" -d @- > "answers/$id.json"
done
jq -n '[inputs | {(input_filename | sub(".*/"; "") | sub("\\.json$"; "")): .response}] | add' answers/*.json > answers.json
```

Re-ask any question whose answer is empty or an error. Keep each question exactly one line: the
model follows short questions and ignores long ones.

### 3. Transcribe → `lyrics.lines.json`

```bash
jq -n --arg audio "$AUDIO_URL" '{audio_urls: [$audio], chunk_level: "word"}' |
  curl -sS -X POST "$API_BASE/content/transcribe" "${AUTH[@]}" -H "Content-Type: application/json" -d @- > transcript.json
python3 "$SKILL/scripts/lines_from_transcript.py" transcript.json measurement.json lyrics.lines.json
```

Add `"language"` to the body for a song not in English. The script splits word timestamps into
timed lines tagged with the measured section and lists the repeated lines (the hook). If the
transcript is thin (`jq .word_count lyrics.lines.json` under about 60 words for a song with
vocals), say so in `technical.notes`, leave `lyrics.lines.json` out of the step 5 check, and quote
only from the model's `key_lines` answer. An instrumental needs no lyric file. The lyric file is a
working file: quote short fragments in the report and never publish the full lyric.

### 4. Context → `context.json`

Fill from verified sources only: the user, the release's own metadata, or research you can cite.
A field you cannot verify stays absent; the report then says it does not know.

```json
{
  "title": "", "artists": "", "writers": "", "producers": "", "year": "", "label": "",
  "file_version": "album master | radio edit | demo | ...",
  "comparable_songs_confirmed": [{"title": "", "artist": "", "premise": "what the two records share"}],
  "sources": ["where each fact came from"]
}
```

Names, years and comparable song titles in the report are checked against this file.

### 5. Compose → `report.json`

You write the report. Read `references/BRIEF.md` (role, facts-only rules, voice) and
`references/schema.json` (the report shape) in full first, then the four inputs. Then:

1. Write one JSON object that matches the schema. Identity fields are plain values (`"key":
   "F major"`, `"key_source": "measured"`); disagreements between the model and the measurement
   go in `technical.notes`.
2. **Declare your findings.** `technical.findings` (4–10 entries) lists every finding named in
   the verdict bullets and review headings, and every image you reuse, each with its `home`
   section and 3–14 lower-case `words` that name it. The checker counts each finding under all
   its words and fails any named more than six times in reader prose.
3. Run the fact check and fix what it reports by changing the claim, never the inputs:

   ```bash
   python3 "$SKILL/scripts/fact_check.py" report.json measurement.json answers.json context.json lyrics.lines.json
   ```

   It checks that every timestamp is within 2 s of a measured point, a lyric line or a model
   answer; every double-quoted lyric is in the transcript, an answer or the context; names,
   year and label are in the context; tempo, duration, LUFS and true peak match the measurement;
   the score adds up; every dimension card has one strength, one neutral and one risk bullet; no
   figure, finding or timestamp repeats past its cap; identity fields carry no provenance; and
   no instrument-panel words reach reader prose.
4. Stop after three passes. Whatever still cannot be anchored comes out of the prose and goes into
   `technical.notes` as a line saying what was dropped and why.

### 6. Render → `report.html` and `report.txt`

```bash
python3 "$SKILL/scripts/render.py" report.json measurement.json report.html --theme recoup --audio "$AUDIO_URL"
python3 "$SKILL/scripts/check_render.py" report.html     # optional: tags, data block, script, contrast
python3 "$SKILL/scripts/flatten.py" report.json report.txt
```

- The page is one self-contained file: charts are drawn from the embedded measurement and every
  `m:ss` becomes a play link. Fix any `warning:` the renderer prints, then re-render.
- `--audio` adds a sticky player that the play links seek. Leave it out when the audio URL is
  private or expires; the page then shows times without playback.
- Read `report.txt` once start to finish as a reader would; cut repetition and hedging the
  checker cannot see.
- Hand over the HTML (publish it if the user wants a link) with a two-line summary: the verdict
  headline and the score.

Optional local probe: `python3 "$SKILL/scripts/arrangement_density.py" song.mp3 measurement.json
[--slice START END]` prints per-section percussive share, onset rate and band shares, to tell a
section that thins out from one that only gets quieter. It needs a local copy of the audio and
librosa.

## What good looks like

- The opening paragraph starts in the song's own world (an image, a place, a line), not a genre
  label. The verdict headline is one opinionated, complete sentence.
- Every claim is anchored: a timestamp, a named element ("808 sub", "fingerpicked acoustic"), a
  short lyric fragment, or a measured number.
- Each dimension card: one summary line and exactly three bullets (strength, neutral, risk). The
  risk is real. Cards do not restate the verdict.
- Every issue has a fix. Every scene archetype names its medium, the timestamp that sells it and
  three cut windows (:06, :15, :30).
- The sync pitch is four or five sentences a supervisor could paste into an email.
- One fact, one home: a measured finding carries its number in one section; elsewhere it is
  named by how it sounds, or not at all.
- No instrument-panel words in prose (valence, arousal, crest factor, centroid, confidence).
  Say what it sounds like: "narrow", "no air above 6 kHz".
- Short sentences. No hedging, no generic praise, no filler. Unknowns admitted in one clause.
- Comparables are artists chosen by sound, marked "same era" or "present day"; song titles only
  when `context.json` confirms them.
- The score shows all seven subscores (hook 20, production 20, songwriting 15, structure 10,
  vocal 10, sync utility 15, market 10) and the total is their weighted sum.

## Known limits

- **The listening model ignores long prompts.** A multi-part prompt comes back as a stock
  caption; keep every question one line and never merge questions.
- **Its market facts are unreliable.** It invents song titles, playlist names and placements. Use
  its comparables only as "sounds like" artists; drop titles the context does not confirm.
- **Measured numbers are the truth.** When the model's tempo or key disagrees with the
  measurement, the measurement wins and the disagreement goes in `technical.notes`. Model
  timestamps usually land within 2 s of the measured landmarks, the same tolerance the checker
  allows.
- **Fingerprint constants are calibrated on two songs.** Read the six axes as directional (darker,
  denser) and never quote their decimals.
- **A hot file is reported as measured.** A true peak above 0 dBTP means this copy clips: say so
  with the fix and ask for the master's figures. The file may be a lossy copy, so never call the
  master clipped.
- **Measurement fields depend on the host's release** (step 1). A report written on the base
  measurement has no band shares, fingerprint, true peak, drops or measured key.
- Transcription thins out on dense mixes and heavy effects (step 3's fallback).
- The page loads two web fonts; offline it falls back to system fonts.

## Cost (per song, list prices)

| Step | Price |
|---|---|
| Measure (`describe: false`) | ≈ $0.01 flat |
| Listen, batched | $0.05 once + $0.001166 per second of the batch; 36 one-line questions run about 1–3 minutes, so ≈ $0.12–0.26 |
| Listen, fallback | $0.05 per call + seconds: ≈ $1.80 + $0.10–0.20 for 36 calls |
| Transcribe | small; check the current price list |
| Compose | your own model tokens, roughly $0.10–0.30 on a mid-tier model |

About $0.25–0.60 a song with the batch, about $2.00–2.30 with the fallback.

## Files

- `references/BRIEF.md` — the composer's role, facts-only rules and voice.
- `references/schema.json` — the report JSON shape, including the score rubric.
- `references/questions.json` — the 36 listening questions.
- `scripts/fact_check.py` — the machine checks (step 5).
- `scripts/lines_from_transcript.py` — word timestamps to timed lyric lines (step 3).
- `scripts/render.py`, `scripts/themes/recoup.json` — the HTML page (step 6).
- `scripts/check_render.py` — page and theme checks (step 6, optional).
- `scripts/flatten.py` — the plain-text version (step 6).
- `scripts/arrangement_density.py` — optional local probe (needs librosa).
