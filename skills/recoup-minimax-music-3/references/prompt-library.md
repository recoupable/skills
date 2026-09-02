# Captions we have shipped, and what came back

Every entry is a real generation on `minimax/music-3` with the result measured, not estimated.
Add to this file after each song; it is the only place our own evidence accumulates.

---

## SMALL LIGHTS (2026-09-02) — indie electronic ballad, 110s

**Used for:** a Recoup marketing film about making a music video for $2.85.
**Result:** 110.13s, 44.1 kHz 16-bit stereo, **-15.3 LUFS**, LRA 12.3, peak -1.0 dBFS. 234s to
generate. **$0.2203.**

**Caption (prose form, no labelled header):**

> Slow-building indie electronic ballad. Starts almost bare: one soft felted piano, a low room hum,
> a single close female voice, intimate and unpolished, breath audible. Minor key, patient tempo
> around 82 BPM. A muted analogue synth pad enters on the pre-chorus. The chorus opens up with warm
> bass and a simple kick, still restrained. The bridge blooms: layered vocal harmonies, bright bell
> synth, gentle swell. The outro pulls back to one voice and the piano. Melancholy turning to quiet
> resolve. No drums until the chorus.

**What worked.** Every arrangement instruction landed: the bare open, the pad arriving on the
pre-chorus, drums held back to the chorus, the bridge bloom, the outro pullback. **Naming
instrumentation per section is what bought that**, and it is worth doing every time.

**What failed.** No key was specified, only "minor key". And the outro was two lines under a long
tail, so the model filled the time by looping a garbled version of the last line from 91.3s to
106.8s. "and the wall behind me / is enormous" came back as "is an all behind me", three times.
The film was cut at 89.7s to avoid it.

**Do differently:** labelled `Genre / BPM / Key` header, and either more outro lines or a shorter
`duration`.

---

## ROUGH DRAFT (2026-08-25) — playful indie pop, ~60s

**Used for:** The Studio ep 4, a manager's sung demo. Generated through Recoup's `/music` endpoint
rather than fal directly, same underlying model.
**Result:** usable; the film shipped. Verse 2 was never sung because the take ran out mid-word at
60s, and the owner chose to trim rather than re-roll.

**Caption (labelled form):**

> Genre: playful indie pop, bedroom pop. BPM: 112. Key: D major. Bright and bouncy: handclaps,
> plucky synth bass, jangly guitar, warm female lead vocal with a smile in it, gang vocals on the
> chorus. Cute, cartoonish, upbeat, a little cheeky.

**What worked.** The labelled `Genre / BPM / Key` header is compact and pins the two values that
most affect whether the result is usable. This is the better header shape of the two.

**What failed.** Same root cause as SMALL LIGHTS from the other direction: **lyrics and duration
were not reconciled.** Here there were too many lines for the time, so a section never got sung.
There it was too few, so a section got looped. Budget roughly ten sung lines per sixty seconds and
the problem disappears in both directions.

---

## The pattern across both

The music instructions have never been the thing that failed. **Both defects were the lyric-to-
duration relationship**, in opposite directions. Reconcile those two numbers before generating and
you remove the only failure mode we have actually hit.
