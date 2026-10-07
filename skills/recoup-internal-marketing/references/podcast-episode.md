# Podcast episode: raw recording to scheduled release

Marketing owns a Recoup Podcast episode from the moment the raw files exist to the moment it is
scheduled on Spotify and YouTube, plus its shorts. Sales owns everything before (invite, booking,
outline, consent, the recording) and after (live links to the guest, day-7 follow-up): see the
`recoup-internal-sales` skill's podcast guest pipeline. First run: 2026-10-01/02, a 33-minute
two-person Restream interview, cut to 32:20, opening + 7 chapters, released on both platforms.

Scripts and templates ship alongside this skill: `scripts/podcast/`, `templates/podcast/`, `brand/`.

## The format (approved by the owner, keep it)

A **news desk in Recoup Sky**: two Restream camera tiles on a pale grid desk with sky and lime glows and a
ghost word ("RIGHTS × AI"), a blue ring on whoever is speaking, forest/lime lower thirds, forest chapter
cards, wire-style source cards, a SOURCES ticker. Three shots, cut by the graphics, never by hand:

| Shot | When | Screen |
|---|---|---|
| A | default, questions, back-and-forth | both tiles side by side (896×504 each is native: never upscale one face full screen) |
| B | a source, a number, a list is being discussed | the card, tiles shrunk to a picture-in-picture column |
| C | chapter cards, cold-open quote, a headline, a big number | full-frame card, voice continues |

Card types: `headline` (source + date + headline + standfirst + stamp), `tline` (dated rows), `stat` (big
number, optional market-share-to-usage bar, quote), `versus` (two columns), `quote` (verbatim, lime
highlight), `list` (numbered chips). Opening = a 6-14s cold open (the guest's strongest line, host muted,
"Coming up" lower third) + the 7s **Wire intro** (`templates/podcast/wire-intro.html`).

## Project layout (one folder per episode, in the marketing workspace; media is gitignored)

```
content/podcast-<guest>/
  episode.json            title, date, guest/host names+roles, ghost word, topics (templates/podcast/episode.example.json)
  raw/                    host-audio.m4a, guest-audio.m4a, host-video.mkv, guest-video.mkv (Restream per-speaker)
  edit/                   transcripts/{host,guest}.json, transcript-merged.md, chapters.json, specs.py, ANALYSIS.md
  comp/chapters/<id>/     generated HyperFrames projects (never hand-edit: change specs/chapters, rebuild)
  exports/                ch00..chNN.mp4, opening.mp4, final/
```

Business keeps the plan, Granola notes, consent and the episode README (link it, don't copy).

## The run, in order (every stage revealed in Finder and approved before the next)

1. **Intake.** Unzip the Restream audio zip and the two camera files into `raw/` under the names above.
   Identify which camera is whom from a frame, not the filename.
2. **Transcribe**: `python3 scripts/podcast/transcribe.py <project>` (ElevenLabs Scribe v2 per speaker,
   **never Whisper**). Each track holds only its speaker, so labels are free.
3. **Camera check**: `python3 scripts/podcast/camera_check.py <project>` prints each camera's offset against
   its audio track (put them in `chapters.json` offsets) and the stretches where a camera dropped frames.
   If the host was speaking during drops: `python3 scripts/podcast/fix_host_video.py <project>` (~8x
   realtime for the interpolated parts; run in the background).
4. **Analysis for the owner** (`edit/ANALYSIS.md`): map vs the run of show, cold-open candidates with exact
   timecodes (6-14s), proposed cuts. Owner decides; record every decision with who/when.
5. **Cut list** (`edit/chapters.json`, `templates/podcast/chapters.example.json`): chapters at the run of
   show's natural breaks, pieces in raw seconds. Patterns that recur every episode:
   - **The host starts the next question while the guest is still answering**, then restarts it after.
     Mute the early fragment (`mute_host`) and splice it onto the restart as a `host_only` piece with
     `video_from` pointing at matching picture, under a chapter card or a full-frame card.
   - **Backchannels** ("Yeah", "Right") over the other speaker: mute them.
   - **Filler and rambles**: cut at word boundaries from the transcript, verify silence with `silencedetect`.
   - Trims inside a sentence must leave a grammatical sentence; read it back.
6. **Specs** (`edit/specs.py`, `templates/podcast/specs.example.py`): cards anchored to transcript phrases,
   so later trims never desync them. Research every external fact you put on a card and date it; the
   guest's claims are attributed "on this episode". **Quote cards are verbatim** (ellipses allowed): a
   paraphrase inside quote marks is the defect the first run caught on four cards.
7. **Prototype first**: build and render ~90s around the strongest chapter before anything else; get the
   look approved once, then every chapter inherits it.
8. **Build + check**: `python3 scripts/podcast/build.py <project> <ch> --recut`, then
   `npx --yes hyperframes snapshot --at <card midpoints> --no-end` in `comp/chapters/<ch>` and read the
   contact sheet before rendering.
9. **Render per chapter**: `STOP_AT=HHMM scripts/podcast/render.sh <project> ch04 ch01 ...` (approved chapter
   first). Open each in Finder as it lands; notes come back per chapter, the fix is one chapter re-render.
10. **Opening**: `python3 scripts/podcast/make_intro.py <project> --show-assets <show assets dir>` then the
   join command in its docstring -> `exports/opening.mp4`.
11. **Host mic** (when it sounds muffled): measure first (band energy above 4 kHz vs the guest). Adobe
   Podcast Enhance (free tier: 30 min/file, 1 h/day, needs the owner's free account sign-in) cleaned noise
   and lifted presence but did NOT restore missing highs; synthetic highs (ffmpeg `aexciter`) measured
   right but hissed on "s". The owner chose Adobe. Split the host track under 30 min at a silence, enhance
   each half, join, verify 0 ms offset at several points, then pass it to assemble.
12. **Assemble**: `python3 scripts/podcast/assemble.py <project> [--host-audio raw/host-audio-enhanced.wav]`
   -> `exports/final/episode.mp4` (one uniform encode, -14 LUFS, decode-checked) + `episode-audio.m4a` +
   `youtube-chapters.txt`.
13. **Covers**: `python3 scripts/podcast/make_cover.py ...` with the guest's PUBLISHED headshot (speaker
   page, company site; never a call screenshot), cut out with `rembg` (bria-rmbg, Python 3.12 venv, stub
   the `pymatting` imports). 16:9 thumbnail + 1:1 art.
14. **Publish** (owner logs in, owner approves the final Publish/Schedule click):
   - **Spotify for Creators** (web only): pick the show by its ID in the URL (an empty duplicate show with
     the same name exists). Upload the episode file **by drag-and-drop**: DevTools-automated upload of a
     ~700 MB file failed processing; the same file dragged in by hand worked. HTML description switch must
     be clicked through the DOM; timestamps in the description override auto-chapters. Two image slots:
     16:9 video thumbnail and 1:1 episode art.
   - **YouTube**: the Recoup connectors can't upload long-form (staging route 500s on large files; the
     Composio SDK base64s the file into one JS string, capping files near 400 MB). Owner uploads + schedules
     in Studio; then set title/description/tags/thumbnail/playlist through the connector
     (`YOUTUBE_UPDATE_VIDEO` with snake_case `video_id`; leave `privacy_status` out so `publishAt` survives),
     and re-read `status.publishAt` to confirm. Details in the account workspace `POSTING-PLAYBOOK.md`.
   - Same release minute on both. Verify every field from the platform's own data (download the stored
     thumbnail/art back), not from the form you filled.
15. **Captions**: `python3 scripts/podcast/make_srt.py <project>` -> `exports/final/youtube-captions.srt`
   (accurate names, speaker changes, sliver cues folded so YouTube accepts the file); upload in Studio:
   video -> Details -> Subtitles (or Languages) -> ⋮ -> Upload file -> With timing.
16. **Shorts**: `references/podcast-shorts.md` (clips table, hybrid format, one prototype, then the rest).
17. **Hand back to sales**: live links to the guest the day it publishes (with the shorts folder), day-7 follow-up.

## Gotchas that cost real time on the first run

- **Renders**: ~3-5x realtime on the Intel laptop; parallel renders time out the headless-Chrome launch
  check. One at a time; a failed launch is a retry, not a bug.
- **Never render during a live recording.** CPU load is the likely cause of Restream dropping the host
  camera to 14 fps. A background "kill at 8:30" timer was itself killed by the 2-hour background limit
  before firing; `render.sh` checks `STOP_AT` in its own loop instead.
- **Host video drifts late after a camera freeze** (found 2026-10-07, +3.2 s on one episode): MP4 output
  defaulted to VFR and dropped the fill frames. `fix_host_video.py` now forces `-fps_mode cfr`. After every
  run, confirm each `edit/fixseg/*.mp4` duration equals its frame count / 30 and compare the fixed file
  against the raw camera at a few points late in the recording before cutting.
- **Lip sync looks wrong but measures right** = low camera frame rate, not timing. Measure before
  re-cutting (`lipsync.py` with the crop actually on the mouth).
- **Background job limit (2 h)**: long queues stop mid-way; check `exports/` and resume the missing chapters.
- **Spotify "This video can't be published"**: first suspect a stream-copied join (fixed in assemble.py),
  then the upload path (drag-and-drop by hand).
- Chapter titles in `youtube-chapters.txt` must start at 0:00 and match the episode description.
