# Podcast shorts: one vertical short a day from a published episode

Run after the episode is approved and scheduled (`references/podcast-episode.md`). Output: ~7 vertical shorts
(1080x1920, 25-60 s) in the HYBRID format, one per day from release day, plus their captions per platform.
Scripts ship alongside this skill: `scripts/podcast/shorts/` (build_hy.py, render.sh), `scripts/podcast/cut.py`
(`--cutlist`/`--out`), `scripts/podcast/make_srt.py`; templates in `templates/podcast/shorts/`.

## 1. Clips table first (approval gate)

Read the merged transcript and the approved edit, then propose a table: day, on-screen hook, raw window
(start → end words), length, the episode card/beat it echoes. Get the rows, any filler trims and every hook
approved before building anything.

- **Windows lie inside the approved edit** and repeat its cuts and mutes (`mute_host`, `host_only`, ...).
  A filler trim inside a window is an extra piece; read the joined sentence back for grammar.
- **Hook**: <= ~60 characters, the guest's idea as a claim or question ("AI music licenses pay by market
  share. Not for long."), never "new episode". Hooks over ~45 characters use `hook_size: 58` to stay on two lines.
- **Length** 25-60 s. A short can open on the host's question if the answer needs it (the guest name tag
  then waits for the guest's first word: anchor named `who`).
- Write the approved table to `edit/shorts.json` (`templates/podcast/shorts/shorts.example.json`).

## 2. Format: HYBRID (decided; don't re-litigate per episode)

Three formats were prototyped on the same clip and compared by the owner: episode-style cards over the guest
video, all motion graphics with the guest in a small circle, and hybrid. **Hybrid won** and is the default:

- 1080x1920 canvas: show bar, **hook bar** on top (forest, lime edge), a 1000x880 **stage**.
- The **guest video fills the stage** most of the time; the guest's face carries the trust a rights-holder
  audience needs.
- **2-4 beats**: on the most literal lines, the stage becomes a full-frame motion-graphic scene and the
  video morphs into a 190 px **corner circle** (bottom-right), then morphs back. Beats are the pattern
  interrupts the all-motion version proved engaging, without losing the face.
- **Captions** below the stage: 2-3 words at a time, active word lime, from the word timestamps.
- Guest name tag for ~3.6 s, a speaking ring on the video/circle, a 2.6 s "Full episode out now" end card
  (episode title + site URL; links aren't clickable in video, the tracked link goes in the post copy).
- Two-pass loudnorm to -14 LUFS.

## 3. Beats: what to draw and the rules that cost us a re-render

Pick the guest's most literal phrases and draw them literally: a metaphor ("toothpaste back in the tube"),
a number (a 100-square grid that counts to the audience size, then lights up the share that applies), a
contrast (a balance scale; a consent toggle), a process (pipes with notes flowing in and money flowing back).

Write each short's beats in `edit/shorts/<id>.html` (`templates/podcast/shorts/beats.example.html`):
`<!--ANCHORS {...}-->`, then `<!--CSS-->`, `<!--HTML-->`, `<!--JS-->`. JS defines
`SC = [[selector, start, end], ...]`; contiguous scenes form one beat.

- **Anchor every reveal to a transcript phrase**, never a timecode (`"name": ["g", "phrase", raw_after]`,
  `@name` in JS; `_end` names anchor to the phrase's last word). Trims then never desync a beat.
- **One idea per scene.** A scene changes when her sentence does.
- **Let viewers read it.** Never let text appear less than ~2 s before its scene ends. A checklist that
  landed as the scene closed was unreadable and had to be re-rendered: hold the scene ~1.5 s past the
  last reveal, and stagger reveals on the spoken words.
- **Labels show state.** A toggle with static OUT/IN labels read "OUT" while switched on; put the state
  text on the knob.
- **Keep low text clear of the circle**: kinetic text below `top:600` gets right padding automatically
  (template rule); size it so the line still fits.
- **Quote marks mean verbatim** (ellipses allowed); check stutters ("being, being honored"). A number the
  guest cites from someone else is "as cited by <guest>".
- **Deterministic animation only**: no `Math.random()` (use the template's seeded `rnd()`), no `tl.call`
  for visible content (seeking skips it); GSAP `onUpdate` counters are fine.
- **Never use ids `c0..cN` in a scene**: they are the caption chunks. The builder refuses them (a scene
  counter once used `#c3`/`#c4` and froze a caption on screen).

## 4. Build, check, render (one prototype first)

1. Media: `build_hy.py` cuts it on first build (`cut.py --cutlist edit/shorts.json`); pass the cleaned
   host track via episode.json `shorts.host_audio` if the episode used one.
2. `python3 scripts/podcast/shorts/build_hy.py <project> s1`
3. `npx --yes hyperframes snapshot --at <every beat midpoint, the reveals, the morph back> --describe false --no-end`
   in `comp/shorts/s1`, and read the contact sheet: overlaps with the circle, clipped text, a caption stuck
   on screen, labels that contradict state.
4. `STOP_AT=HHMM scripts/podcast/shorts/render.sh <project> s1:<slug>` -> `exports/shorts/<slug>.mp4`
   (-14 LUFS). Open it in Finder for the owner.
5. **Prototype one short, get the look approved, then build the rest.** Renders run ~3-5x realtime on the
   Intel laptop; one at a time (parallel load times out the headless-Chrome launch; render.sh retries).
   A background queue can be cut off: re-run the missing shorts.

## 5. Distribution kit (drafts; the owner approves before anything posts)

- **Captions per platform** for every short, quotes verified word for word against the transcript **by
  script** (split on ellipses, normalize punctuation, search both speakers):
  - YouTube Shorts: title <= 100 chars, description links the FULL episode on YouTube + `#Shorts`.
  - Instagram: "Full episode: link in bio" (check the bio link first), 3-5 topical hashtags.
  - X: <= ~240 chars, link in a reply.
  - LinkedIn: tag the guest and their company, link in the first comment, one question on some days.
- **UTM**: `utm_source=<platform>&utm_medium=social&utm_campaign=<YYYY-MM>&utm_content=<guest-slug>&utm_term=<s1..s7|launch>`.
  1:1 sends to individuals use `utm_medium=episode-share&utm_content=<person-slug>`.
- **Clips folder for the guest's team**: the final files in a view-only Drive folder linked from the
  live-links email (sharing is set to "anyone with the link" on send day). Check the uploads by file size.
- **Same posting time daily** (B2B weekday late morning) so timing isn't a variable when results are read.

## 6. What the Recoup YouTube connector can't do (Studio steps)

The connector uploads videos (`YOUTUBE_UPLOAD_VIDEO` / `YOUTUBE_MULTIPART_UPLOAD_VIDEO`, staged files),
posts comments (`YOUTUBE_POST_COMMENT`), and edits/removes/reorders playlist items. It **cannot** schedule a
publish time (upload private, flip public on the day, or schedule in Studio), pin a comment, add a caption
track, or set a Short's related video. Episode captions: `python3 scripts/podcast/make_srt.py <project>`, then
in Studio: video -> Details -> Subtitles (or Languages) -> ⋮ -> Upload file -> With timing.
