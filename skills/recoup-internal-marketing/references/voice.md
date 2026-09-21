# Voice — choosing it, directing it, and proving it is not mechanical

The narration is the single most exposed choice in a video. A viewer forgives a rough cut; they do
not forgive a voice that sounds like a machine reading a press release. A model two generations old
reads mechanical (08-06); a newer model changes the gain (v2 ≈ +7 dB, v3 ≈ 0), so re-measure after
a model change (08-07).

## Install the official ElevenLabs skills first

Install once per workspace and load the `text-to-speech` skill before generating; it carries the
current model list, `voice_settings` semantics (stability / similarity / style / speed), output
formats and request stitching, so none of that gets guessed from a cloned script. Verified in use
2026-08-17 (the Jessa bake-off ran on it). The house rules below sit on top of it, not instead of it.

```bash
npx skills add elevenlabs/skills --skill text-to-speech
```

## The three axes, in the order they matter

Most "the VO sounds robotic" problems are blamed on the voice. Usually it is the model.

| Axis | Wrong answer | Right answer |
|---|---|---|
| **1. Model** | An older TTS model with flat prosody and no delivery control | The current expressive model. On ElevenLabs that is **`eleven_v3`**, which supports inline audio tags |
| **2. Voice** | The default stock voice everyone uses | A voice chosen by bake-off for the register of the piece, or a **cloned voice of a real person on the team** |
| **3. Delivery** | Defaults, no direction | Audio tags + stability tuned for variation, with punctuation carrying the pacing |

**Check the model before anything else.** Generator scripts get cloned from project to project and
quietly carry a stale `model_id` for months; ask the provider what it offers:

```bash
curl -sS "https://api.elevenlabs.io/v1/models" -H "xi-api-key: $KEY" \
  | python3 -c "import json,sys; [print(m['model_id'], m.get('name')) for m in json.load(sys.stdin)]"
```

## Run a bake-off, do not pick from the label

Voice labels ("confident", "narrative_story") are close to useless for predicting how a voice reads
*your* script. Generate candidates on **the film's actual lines** and listen:

1. **Pick 4 to 6 candidates** spanning the register you want, always including the voice you
   shipped last time on the **old** model (the control), the same voice on the **new** model
   (isolates model from voice), and a **cloned voice of someone on the team** if one exists.
2. **Use two real lines** from the script, one factual and one with a turn in it.
3. **Normalize every candidate to the same loudness before listening**, or the loudest wins.
4. **Concatenate them into one file** with a short gap; an owner will not open six files.
5. **Record the winner** with voice id, model, settings and the date.

Consistency across videos matters, but **not more than sounding human**. A recurring character keeps
its canonical voice; a narrator can change when the old one is the problem.

### Current default narrator: Jessa (owner ruling, 2026-08-17)

**Jessa** `yj30vwTGJxSHezdAGsv9` · `eleven_v3` · stability 0.0 · similarity 0.75. Won a
loudness-matched three-way against Sarah and Clara on the apple-songs-launch film's real lines; the
owner approved the delivery and ruled her the default going forward. Prior defaults for the record:
Brian (through 08-06), W. L. Oxley (08-07 to 08-12). Measured on 2026-08-17:

- **She is fast**: the same hook line paid off at 1.74s in her read vs 2.08s in the male take.
  Still generate the hook first and measure; pace is voice-specific and does not transfer.
- **Her raw output is quiet with hot peaks** (~-19 LUFS at ~0 dBTP), so a straight gain clips. Use
  the gain + true-peak limiter chain below; working values on her material were
  `volume=+4.4dB, alimiter=limit=0.84:attack=1:release=80:level=disabled` at 96k oversample,
  landing -16.5 LUFS / -1.5 dBTP with LRA preserved.
- `[matter-of-fact]` is Scribe-verified consumed in her voice.

A film may still bake off a different narrator when the register calls for it; recurring characters
keep their canonical voices regardless.

**Consider the clone.** The objection behind "it sounds mechanical" is usually "this is not a
person," which no tag-tuning on a stock voice fully answers; a founder's own voice earns register
for a confession piece. Weigh it against tying the account to one person's availability and identity.

## Directing with audio tags

`eleven_v3` accepts inline bracket tags that act as delivery direction and are **not spoken**:

```
[matter-of-fact] Five things in our product were broken. This was the worst.
```

**Only use tags you have verified.** An unrecognised tag risks being read aloud on camera. Verify
by generating the line and transcribing it back with Scribe, not Whisper; clean prose with no
bracket content means the tag was consumed as direction.

```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: $KEY" -F "file=@line.wav" -F "model_id=scribe_v1"
```

**Verified working (2026-08-07):** `[matter-of-fact]`, `[thoughtful]`.
**⛔ `[pause]` is banned on v3: it adds ~1.8s of dead air per use.** Let punctuation pace the read.

**Under-direct.** Over-performing lands in the same uncanny valley as under-performing. A changelog
or a confession wants a person stating uncomfortable facts plainly, not an announcer: tag one or
two lines in a seven-line script, not all of them.

**Stability** on `eleven_v3` takes three values: `0.0` Creative, `0.5` Natural, `1.0` Robust. Lower
means more variation, the direct antidote to flatness. Use `0.0` for stock voices; cloned voices
can drift at `0.0`, so start them at `0.5`.

## Writing for the ear, not the page

- **Never speak a metric the listener cannot picture.** "One point zero eight to one" is checkable
  and meaningless. **Put the number on screen as evidence and let the voice say what it meant**
  ("the page where we ask you to pay had text you could not read"). This also satisfies the
  `references/hooks.md` rule that on-screen text complements the spoken line, never restates it.
- **Every number needs its unit spoken.** "A hundred and fifty five accounts sat at zero" — zero
  what? Read every line aloud hunting for a bare number.
- **A list needs scaffolding or it reads as a jumble.** State the count up front, then spoken
  ordinals ("One… Two… Three…"), paired with an on-screen step counter.

## Loudness

**Measure, then apply linear gain. Never blind-normalize.** Target **-16.5 LUFS** per line, then
check the peak: high-crest-factor voices (Brian-class) clip on a straight gain to target, so add a
limiter rather than lowering the target. A limiter catching a few transients is not dynamic
normalization of the whole signal, which is still banned.

```bash
ffmpeg -i line.wav -af ebur128 -f null -   # read Integrated loudness
ffmpeg -i in.wav -af "volume=${G}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled" out.wav
```

That lands around -16.5 LUFS with peaks near -1.5 dBFS.

**Do not pitch-correct a drifting voice.** Formant-preserving correction to a common baseline
measured perfectly and sounded far worse. Natural drift wins.

### Beds and the voice/bed mix

- Eleven Music cannot produce a flat single-instrument bed; synthesise simple beds directly.
- Never let a music model own the dynamics: keep the bed flat and author the arc as a
  frame-accurate volume envelope.
- `loudnorm` at the end of the chain undoes that envelope; use fixed gain + a true-peak limiter.
- Per-line VO delivery placed at exact timestamps, not one read (07-27).

## Before compositing

- [ ] Model checked against the provider's current list, not inherited from a cloned script
- [ ] Winner recorded with voice id, model, settings and date
- [ ] Every audio tag used has been verified by transcribing the output back
- [ ] Every line transcribed to confirm no bracket text leaked and names are pronounced right
- [ ] Loudness measured per line, gain applied linearly, peaks checked for clipping
- [ ] Raw un-normalized takes kept in a sibling directory. Name backup dirs after the voice
      (`voice-brian-backup/`, `oxley-raw/`); never guard a copy with "only if missing" (08-07)
- [ ] **Total speech duration measured** and the film's runtime re-planned against it. A model or
      voice change moves every caption and beat; it is a timeline rebuild, not a file swap
