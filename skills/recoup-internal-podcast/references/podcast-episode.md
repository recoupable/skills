# Podcast episode: raw recording to scheduled release

This file covers a Recoup Podcast episode from the moment the raw files exist to the moment it is
scheduled on Spotify and YouTube, plus its shorts. The guest relationship before (invite, booking,
outline, consent) and after (live links to the guest, day-7 follow-up) is the `recoup-internal-sales`
skill's podcast guest pipeline; the recording setup is `references/recording-prep.md`. First run: 2026-10-01/02, a 33-minute
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

0. **Run from your own skills checkout.** Create a skills worktree on `origin/main` for the episode and
   run every script from it; a shared checkout can sit on another branch with stale scripts.
1. **Intake.** Restream delivers one zip of per-speaker audio (`<Name> — Camera — Audio 1.m4a`, one per
   speaker) and one `.mkv` per camera, both named `...-restream.mkv`, the second with ` (1)`. Downloads
   land as `Unconfirmed *.crdownload` until finished; watch for them rather than polling the owner. Rename
   to `<first-name>-audio.m4a` / `<first-name>-video.mkv` and symlink the `host-*` / `guest-*` names above.
   Identify which camera is whom from a frame (`ffmpeg -ss 600 -i <file> -frames:v 1 out.jpg`), never the
   filename or download order. Note anything in the guest's frame worth using (a poster, an award).
2. **Transcribe**: `python3 scripts/podcast/transcribe.py <project>` (ElevenLabs Scribe v2 per speaker,
   **never Whisper**). Each track holds only its speaker, so labels are free.
2b. **Scan**: `python3 scripts/podcast/scan_transcripts.py <project>` writes `edit/words-{host,guest}.txt`
   (take every in/out point from these, not from the merged transcript, which can misplace a fragment by
   minutes) and prints the early-start host fragments and any dead air. **The host track reads digital zero
   whenever the host is quiet** (mic gate or mute); that alone is not a dropout. Dead air inside the
   interview usually means a line said while muted: on 2026-10-13 the host's sign-off was lost this way and
   replaced with the host's own later repeat ("I wrapped up by saying thank you for joining us today, Tom").
   Use Scribe to settle the recorder's mishearings and correct the Business recording notes.
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
5b. **Audio rough cut (gate)**: `python3 scripts/podcast/rough_audio.py <project>` renders the cut list as
   audio only (`exports/rough-cut-audio.m4a` + chapter times), about a minute. The owner checks every
   splice by ear before specs, cards or renders; a bad splice found after rendering costs a re-render.
6. **Specs** (`edit/specs.py`, `templates/podcast/specs.example.py`): cards anchored to transcript phrases,
   so later trims never desync them. Research every external fact you put on a card and date it; the
   guest's claims are attributed "on this episode". **Quote cards are verbatim** (ellipses allowed): a
   paraphrase inside quote marks is the defect the first run caught on four cards.
   **Owner's standing rules (check every chapter before the prototype; the Zac prototype missed one, 2026-10-14):**
   - **A card over every host question and recap**, mostly full-frame C (host camera is weak, 2026-10-06).
   - **Guest focus**: shot A shows the guest large and the host as a small inset. `build.py` does this by
     default; `"layout": "equal"` in `episode.json` restores side-by-side.
   - **No more than 30 s of cameras only before a card** (2026-10-10). `build.py` prints `WARN` for each
     longer stretch; fill it with a verbatim quote, list or stat from that stretch.
   - **Album or single art when a record is named** (2026-10-10): `art=[('file.jpg', 'Artist', 'Title · year')]`
     on the card, files in `<project>/edit/art/` with `SOURCES.md` (Spotify via the Recoup API `/spotify/search`).
     Never substitute another artist's cover when the record isn't found. One cover on a side card; two
     covers need a full-frame C card (a two-cover B card squeezes the text off the card). No art on stat cards.
   - **Lower thirds only on open shots**: a name tag under a card renders hidden or half-covered (Zac ch01,
     2026-10-14). `build.py` warns on any overlap. With every host line under a card, the host usually gets no tag.
7. **Prototype first**: build and render ~90s around the strongest chapter before anything else; get the
   look approved once, then every chapter inherits it.
8. **Build + check**: `python3 scripts/podcast/build.py <project> <ch> --recut`, then
   `npx --yes hyperframes snapshot --at <card midpoints> --no-end` in `comp/chapters/<ch>` and read the
   contact sheet before rendering. Also run `npx --yes hyperframes inspect --at <card midpoints> --json` and
   fix every `text_box_overflow` on a card (a wide stat number once pushed its caption over the video tiles);
   the `#ghost` word and ticker `SOURCES` overlaps are by design.
9. **Render per chapter**: `STOP_AT=HHMM scripts/podcast/render.sh <project> ch04 ch01 ...` (approved chapter
   first). Open each in Finder as it lands; notes come back per chapter, the fix is one chapter re-render.
10. **Opening**: `python3 scripts/podcast/make_intro.py <project> --show-assets <show assets dir>` then the
   join command in its docstring -> `exports/opening.mp4`.
11. **Host mic** (when it sounds muffled): measure first (band energy above 4 kHz vs the guest). Adobe
   Podcast Enhance (free tier: 30 min/file, 1 h/day, needs the owner's free account sign-in) cleaned noise
   and lifted presence but did NOT restore missing highs; synthetic highs (ffmpeg `aexciter`) measured
   right but hissed on "s". The owner chose Adobe; it can be run on the guest track too (owner's call; keep it
   only if it wins a blind A/B on the same sentence).
   **Enhance only what the cut plays, after the rough cut is approved** (5b), never the raw track:
   `python3 scripts/podcast/enhance_pack.py <project> pack host` (and `guest`) writes `enhance/<track>-used.wav`,
   the pieces the cut uses minus that track's 3 s+ silences, one file per track. On 2026-10-14 the raw tracks
   were 33 min each; packed, the host was 6.9 min (cards and cuts leave little host speech) and the guest 24 min:
   31 min of quota instead of 66, both tracks in one day, one upload each instead of a split pair, and far less
   upload, processing and download time. Check the total against the 1 h/day cap before uploading. Before uploading,
   test the round trip on the unenhanced pack (`unpack` it, check 0 ms lag at several raw times). After Adobe:
   `enhance_pack.py <project> unpack <track> <enhanced.wav>` -> `raw/<track>-audio-enhanced.wav` (full length,
   silence outside the pieces); verify 0 ms offset again. Re-pack if a later cut change restores audio.
   **Then gate the host track**: `python3 scripts/podcast/gate_host_audio.py <project>`. Adobe invents short,
   low, voice-like sounds out of the host mic's room noise while the guest talks (second episode: 8 in the
   edit, the owner heard one as "a very low voice, kinda creepy"). The script lists every span where the
   enhanced track sounds without a host word, labels it INVENTED (original mic at the noise floor) or a real
   laugh/"mm" (original louder), and writes `raw/host-audio-enhanced-gated.wav` with the invented ones
   silenced and speech untouched. Assemble from the gated file, never the raw output.
12. **Assemble**: `python3 scripts/podcast/assemble.py <project> [--host-audio raw/host-audio-enhanced-gated.wav] [--guest-audio raw/guest-audio-enhanced.wav]`
   -> `exports/final/episode.mp4` (one uniform encode, -14 LUFS, decode-checked) + `episode-audio.m4a` +
   `youtube-chapters.txt`.
13. **Covers** (spec, title and description rules: `references/podcast-packaging.md`): `python3 scripts/podcast/make_cover.py ...` with the guest's PUBLISHED headshot (speaker
   page, company site; never a call screenshot), cut out with `rembg` (bria-rmbg, Python 3.12 venv, stub
   the `pymatting` imports). 16:9 thumbnail + 1:1 art.
14. **Publish** (owner logs in, owner approves the final Publish/Schedule click):
   - **Spotify for Creators** (web only): pick the show by its ID in the URL (an empty duplicate show with
     the same name exists). Upload the episode file **by drag-and-drop**: DevTools-automated upload of a
     ~700 MB file failed processing; the same file dragged in by hand worked. HTML description switch must
     be clicked through the DOM; timestamps in the description override auto-chapters. Two image slots:
     16:9 video thumbnail and 1:1 episode art. Hung episodes list: open it in a new tab. The description counter lags a
     paste; it is not a failed fill. Replace a thumbnail by deleting the uploaded one first (that reveals Upload).
     Nothing saves until the owner clicks **Schedule** on Review; the Review thumbnail preview is blank (10 s
     signed URL), so check the stored image after saving.
   - **YouTube**: the Recoup connectors can't upload long-form (staging route 500s on large files; the
     Composio SDK base64s the file into one JS string, capping files near 400 MB). Owner uploads + schedules
     in Studio; then set title/description/tags/thumbnail/playlist through the connector
     (`YOUTUBE_UPDATE_VIDEO` with snake_case `video_id`; leave `privacy_status` out so `publishAt` survives),
     and re-read `status.publishAt` to confirm. Keep these calls in `exports/final/youtube-finish.mjs`
     (title read from `youtube-title.txt`, never touches visibility) so the next episode only changes the ID. Details in the account workspace `POSTING-PLAYBOOK.md`.
   - Same release minute on both. Verify every field from the platform's own data (download the stored
     thumbnail/art back), not from the form you filled.
15. **Captions**: `python3 scripts/podcast/make_srt.py <project>` -> `exports/final/youtube-captions.srt`
   (accurate names, speaker changes, sliver cues folded so YouTube accepts the file); then apply the episode's
   known mishearings (the analysis list, e.g. Songvest -> SongVest, Hypnosis -> Hipgnosis, "gamer songs" -> GEMA); upload in Studio:
   video -> Details -> Subtitles (or Languages) -> ⋮ -> Upload file -> With timing.
16. **Episode page** (marketing repo): entry in `content/podcast/episodes.json` (first = top card), 1280x720
   cover in `public/podcast/<slug>-wide.jpg`, transcript `content/podcast/transcripts/<slug>.json` built from the
   corrected captions (speaker turns alternate at `>>`; untangle overlapping speech by hand). Merge after the
   release minute: the embed reads "private" until then.
17. **Shorts**: `references/podcast-shorts.md` (clips table, hybrid format, one prototype, then the rest).
18. **Hand back to sales**: live links to the guest the day it publishes (with the shorts folder), the wrap-up email the day the last short posts (closes the run, asks for guest recommendations), day-7 follow-up. Templates in the `recoup-internal-sales` skill's `references/podcast-guest-pipeline.md`.

## Gotchas that cost real time on the first run

- **Renders**: ~3-5x realtime on the Intel laptop; parallel renders time out the headless-Chrome launch
  check. One at a time; a failed launch is a retry, not a bug.
- **Never render during a live recording.** CPU load is the likely cause of Restream dropping the host
  camera to 14 fps. A background "kill at 8:30" timer was itself killed by the 2-hour background limit
  before firing; `render.sh` checks `STOP_AT` in its own loop instead.
- **Lip sync looks wrong but measures right** = low camera frame rate, not timing. Measure before
  re-cutting (`lipsync.py` with the crop actually on the mouth).
- **Background job limit (2 h)**: long queues stop mid-way; check `exports/` and resume the missing chapters.
- **Spotify "This video can't be published"**: first suspect a stream-copied join (fixed in assemble.py),
  then the upload path (drag-and-drop by hand).
- Chapter titles in `youtube-chapters.txt` must start at 0:00 and match the episode description.
- **Adobe Enhance invents sound in silence** (second episode): its output can hold a ~1 s low "voice" where
  the host said nothing. Chapter reviews use the raw mic, so nobody hears it until the final file. Always run
  `gate_host_audio.py` before assembling; listen to its INVENTED spans in the final.
