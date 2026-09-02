---
name: recoup-minimax-music-3
description: Generate an original song with MiniMax Music 3 on fal, for a film, an ad, a demo or a release. Covers the two inputs the model takes (a structured Caption and tagged Lyrics), how to write lyrics that survive generation, the exact fal call and its cost, and the checks to run on the returned audio before anything is built on top of it. Use when asked to "make a song", "generate a track", "write the song for this video", "score this", or when a music video needs a song that does not exist yet. For an artist's already-released song use recoup-internal-marketing's music-video.md instead; for analysing an existing recording use recoup-song-analyze-audio.
---

# MiniMax Music 3

Two inputs drive this model and they do different jobs:

| Input | fal field | Owns |
|---|---|---|
| **Caption** | `prompt` | the music: genre, tempo, key, vocals, arrangement |
| **Lyrics** | `lyrics` | the words and the song's structure, via bracketed tags |

> **Naming trap.** The open-weights repo and the model card call these `instructions` and `input`.
> **On fal they are `prompt` and `lyrics`.** Same two things, different names.

## Do not write the Caption by hand. Delegate it.

MiniMax ships an official skill for exactly this, with a thousand style templates and a genre router:

```bash
npx skills add MiniMax-AI/MiniMax-Music3 --skill music-caption-rewriter
```

Hand it your brief and it returns a caption under three required headings: **Global Metadata**,
**Vocal Details**, **Arrangement**. That is the format the model was trained to read, so use it.
It targets roughly 250 to 450 words.

**It will not write your lyrics.** It reads bracketed tags only and is forbidden from quoting or
paraphrasing lyric content. Lyrics are this skill's job, below.

If you are writing a caption without it, the minimum viable shape is a labelled header, then
instrumentation, then per-section arrangement:

```
Genre: playful indie pop, bedroom pop. BPM: 112. Key: D major. Bright and bouncy: handclaps,
plucky synth bass, jangly guitar, warm female lead with a smile in it, gang vocals on the chorus.
```

That is the house precedent (`content/rough-draft`, 2026-08-25) and it worked. Label **BPM and key
explicitly**; burying tempo in prose is weaker.

## Lyrics: the tags are the structure

Only these tags are recognised. Anything else is sung aloud.

`[Intro]` `[Verse]` `[Pre-Chorus]` `[Chorus]` `[Post-Chorus]` `[Bridge]` `[Instrumental]` `[Solo]` `[Outro]`

Put each tag on **its own line**, lowercase or titlecase both work. For an instrumental, omit words
entirely and carry the piece on `[Instrumental]` and `[Solo]`.

### Write to the line budget or the model will improvise

**About ten sung lines per sixty seconds.** Under-supply lyrics and the model does not stop early,
it **fills the remaining time by repeating and mangling your last section**.

> Measured 2026-09-02: a 26-line lyric at `duration: 110` sang cleanly to 89.7s, then looped a
> garbled version of the final line three times out to 106.8s. The closing line was "and the wall
> behind me / is enormous", which came back as "is an all behind me". Seventeen seconds unusable.

Two rules follow:

- **Give the outro enough lines to fill its time.** A two-line outro under a thirty-second tail is
  an invitation to loop.
- **Do not end on a rare or hard-to-sing word.** "Enormous" did not survive. Prefer common, open
  vowels for the last line of the song.

### Repetition is structure, not laziness

A chorus repeated verbatim is how the model knows it is a chorus. Vary a verse; keep the chorus
identical each time unless you want the arrangement to diverge.

## The call

```js
const res = await fal.subscribe("minimax/music-3", {
  input: {
    prompt: CAPTION,     // the structured caption
    lyrics: LYRICS,      // tagged, one tag per line
    duration: 110,       // UPPER BOUND, not a target. 5..300
  },
});
const url = res.data?.audio?.url;
```

| Param | Notes |
|---|---|
| `prompt` | required. The structured caption. 5,000 token ceiling. |
| `lyrics` | required. Tagged. |
| `duration` | **an upper bound.** The model may stop earlier; it will not stop early just because the lyrics ran out (see above). |
| `seed` | set it when you want a re-roll to be comparable. |
| `guidance_scale`, `num_inference_steps` | leave default unless bake-off says otherwise. |

**Returns** a WAV. The model card specifies 32 kHz; **fal returned 44.1 kHz 16-bit stereo** on
2026-09-02, so measure rather than assume. Generation took **234 seconds** for 110s of audio.

**Cost: $0.002 per second of audio produced**, measured twice against the production bill
(223.97s = $0.44794 on 2026-08-27; 110.13s = $0.2203 on 2026-09-02). It matches to the cent, so a
song is the cheapest thing in any film. A 110-second track is 22 cents. **Re-roll freely.**

## Check the audio before you build anything on it

A song is the timing spine of a film: every scene window is locked to it, so a defect found after
the scene table exists is a rebuild, not a fix.

1. **Measure it.** `ffprobe` for real duration and sample rate, `ebur128` for LUFS and peak.
2. **Transcribe it and read the transcript.** ElevenLabs Scribe with word timestamps, not whisper.
   This is what catches a mangled or looped section, and it gives you the word times you need for
   scene windows anyway. Compare the transcript against the lyrics you sent, line by line.
3. **Find the last clean word.** Where the transcript degrades, that is the end of your usable
   audio. Cut the film there rather than trying to hide it.
4. **Only then** write the scene table against those word times.

## Where this sits

- The song is **downstream of the concept**, never upstream. Genre, length and structure all follow
  from what the film is. Generating a song first locks the timing before the story exists.
- Hand the approved audio and its word times to `recoup-internal-marketing` →
  `references/video-pipeline.md`, which owns scene windows, stills, motion and the composite.
- The audio approval gate is the cheapest gate in a film build. A song change after compositing
  moves every beat and every caption; before it, it costs 22 cents.

## References

- `references/prompt-library.md` — captions we have actually shipped, with what came back
