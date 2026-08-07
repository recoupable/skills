# Voice — choosing it, directing it, and proving it is not mechanical

The narration is the single most exposed choice in a video. A viewer forgives a rough cut; they do
not forgive a voice that sounds like a machine reading a press release. This file exists because a
real listener told us ours did.

> **The incident, 2026-08-06.** A family member watching one of our Instagram posts said the voice
> "reeks of mechanical, not human" and that the sound is "just overused" on the internet. He was
> right on both counts, and neither was a taste problem: we were on a **stock voice** that thousands
> of other videos use, driven by a **model two generations old**.

## The three axes, in the order they matter

Most "the VO sounds robotic" problems are blamed on the voice. Usually it is the model.

| Axis | Wrong answer | Right answer |
|---|---|---|
| **1. Model** | An older TTS model with flat prosody and no delivery control | The current expressive model. On ElevenLabs that is **`eleven_v3`**, which supports inline audio tags |
| **2. Voice** | The default stock voice everyone uses | A voice chosen by bake-off for the register of the piece, or a **cloned voice of a real person on the team** |
| **3. Delivery** | Defaults, no direction | Audio tags + stability tuned for variation, with punctuation carrying the pacing |

### Check the model before anything else

Ask the provider what it offers rather than trusting whatever the last script hardcoded. Generator
scripts get cloned from project to project and quietly carry a stale `model_id` for months.

```bash
curl -sS "https://api.elevenlabs.io/v1/models" -H "xi-api-key: $KEY" \
  | python3 -c "import json,sys; [print(m['model_id'], m.get('name')) for m in json.load(sys.stdin)]"
```

**A newer model changes the loudness maths.** Measured 2026-08-07: `eleven_multilingual_v2` arrives
around **-23.7 LUFS** and needs roughly **+7 dB**, while `eleven_v3` arrives near broadcast level
and needs **-1.5 to 0 dB**. A gain stage copied from an older project will clip the newer model. See
"Loudness" below, and always measure.

## Run a bake-off, do not pick from the label

Voice labels ("confident", "narrative_story") are close to useless for predicting how a voice reads
*your* script. Generate candidates on **the film's actual lines** and listen.

The procedure, which takes minutes and costs a rounding error in characters:

1. **Pick 4 to 6 candidates** spanning the register you want, and always include:
   - the voice you shipped last time, on the **old** model, as the control;
   - the same voice on the **new** model, which isolates model from voice;
   - a **cloned voice of someone on the team**, if one exists.
2. **Use two real lines** from the script, one factual and one with a turn in it. A single flat
   sentence hides the differences that matter.
3. **Normalize every candidate to the same loudness before listening.** Otherwise the loudest
   candidate wins and you will not know why.
4. **Concatenate them into one file** with a short gap between each. Asking an owner to open six
   files is asking them not to do it.
5. **Record the winner** with voice id, model, settings and the date, so the next video does not
   re-litigate it.

Consistency across videos matters, but **not more than sounding human**. A recurring character keeps
its canonical voice; a narrator can change when the old one is the problem.

### Consider the clone

If someone on the team has a cloned voice, audition it. The objection behind "it sounds mechanical"
is usually "this is not a person," and no amount of tag-tuning on a stock voice fully answers that.
A founder's own voice also earns register that a hired-sounding read cannot, especially for the
Integrity Arc, where the piece is a confession. Weigh it against the fact that a cloned voice ties
the account to one person's availability and identity.

## Directing with audio tags

`eleven_v3` accepts inline bracket tags that act as delivery direction and are **not spoken**.

```
[matter-of-fact] Five things in our product were broken. This was the worst.
```

**Only use tags you have verified.** An unrecognised tag risks being read aloud on camera. Verify by
generating the line and transcribing it back:

```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: $KEY" -F "file=@line.wav" -F "model_id=scribe_v1"
```

If the transcript comes back as clean prose with no bracket content, the tag was consumed as
direction. Use Scribe, not Whisper.

**Verified working (2026-08-07):** `[matter-of-fact]`, `[thoughtful]`.

**⛔ `[pause]` is verified BAD.** v3 reads it as a dramatic beat, not a breath. Measured across seven
lines it added **12.9 seconds of dead air**, including a **3.13s** silence inside a single 9.12s
take. Let punctuation pace the read instead. This one tag was the difference between 58.6s and 48.8s
of narration on the same script.

### Under-direct

Over-performing lands in the same uncanny valley as under-performing, just from the other side. A
changelog or a confession wants a person stating uncomfortable facts plainly, not an announcer.
Tag one or two lines in a seven-line script, not all of them.

**Stability** on `eleven_v3` takes three values: `0.0` Creative, `0.5` Natural, `1.0` Robust. Lower
means more variation, which is the direct antidote to flatness. Use `0.0` for stock voices. Cloned
voices can drift at `0.0`; start them at `0.5`.

## Writing for the ear, not the page

The voice exposes writing faults that read fine as text. Three that have cost us:

- **Never speak a metric the listener cannot picture.** "One point zero eight to one" is checkable
  and meaningless; a contrast ratio means something to a front-end developer and nothing to a
  manager. **Put the number on screen as evidence and let the voice say what it meant** ("the page
  where we ask you to pay had text you could not read"). This also satisfies the rule in
  [`hooks.md`](hooks.md) that on-screen text must complement the spoken line, never restate it.
- **Every number needs its unit spoken.** "A hundred and fifty five accounts sat at zero" — zero
  what? Read every line aloud hunting for a bare number.
- **A list of items needs scaffolding or it reads as a jumble.** State the count up front, then use
  spoken ordinals ("One… Two… Three…"). A listener should always know where they are and that an end
  is coming. Pair it with an on-screen step counter.

## Loudness

**Measure, then apply linear gain. Never blind-normalize.**

```bash
ffmpeg -i line.wav -af ebur128 -f null -   # read Integrated loudness
```

Target **-16.5 LUFS** per line. Then check the peak: Brian-class voices have a high crest factor, so
a straight gain to target can clip. Add a limiter rather than lowering the target:

```bash
ffmpeg -i in.wav -af "volume=${G}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled" out.wav
```

That lands around -16.5 LUFS with peaks near -1.5 dBFS. A limiter catching a few transients is not
the same thing as dynamic normalization of the whole signal, which is still banned.

**Do not pitch-correct a drifting voice.** Formant-preserving correction to a common baseline
measured perfectly and sounded far worse. Natural drift wins.

## Before compositing

- [ ] Model checked against the provider's current list, not inherited from a cloned script
- [ ] Winner recorded with voice id, model, settings and date
- [ ] Every audio tag used has been verified by transcribing the output back
- [ ] Every line transcribed to confirm no bracket text leaked and names are pronounced right
- [ ] Loudness measured per line, gain applied linearly, peaks checked for clipping
- [ ] Raw un-normalized takes kept in a sibling directory
- [ ] **Total speech duration measured** and the film's runtime re-planned against it. A model or
      voice change moves every caption and beat; it is a timeline rebuild, not a file swap

## The backup trap

**Never guard a backup with "copy only if the directory is missing."** A stale directory from an
earlier voice silently defeats it, and the next normalize pass processes the *old* audio back over
the new. This happened on 2026-08-07 and was caught only because the durations looked wrong. Name
backup directories after the voice (`voice-brian-backup/`, `oxley-raw/`), never a bare `raw/`.
