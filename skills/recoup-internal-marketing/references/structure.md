# Structure — holding a piece together after the hook

`references/hooks.md` buys the first three seconds. This file is about the forty after them.

Written 2026-08-07, after an owner watched a five-item changelog and said it "feels very incohesive.
Jumping from one feature to the next without presenting it as a changelog with multiple updates."
Every individual line was accurate and every number was sourced. It still did not hold together,
because nothing told the viewer they were inside a list.

## The failure mode: a list that never says it is a list

A multi-item piece assembled by writing each item well and running them in order **reads as a
jumble**, not as a changelog. Each line starts a new topic cold. The viewer has no idea how many
items there are, where they are in the sequence, or that an end is coming, so every transition feels
like a fresh start rather than a step.

The items are not the problem. The **scaffolding** is missing.

## The four pieces of scaffolding

Cheap, and they do almost all the work.

1. **State the count in the frame line.** "Five things in our product were broken." The viewer now
   knows the shape of what they are about to watch, and the piece has made a promise it can keep.
2. **Speak the ordinals.** "One… Two… Three…" A listener should never have to wonder where they are.
   This is the single largest cohesion gain per word spent.
3. **Show a step counter.** `1/5 … 5/5` on every panel. `references/hooks.md` already pairs a visible
   step counter with the list-tease archetype; this is where it earns its place. It also carries the
   structure for the ~60% of viewers watching sound-off. A step counter is **structural notation, not
   a claim** — it is explicitly exempt from the on-screen number audit in `references/hooks.md`, which
   applies only to evidence.
4. **Bookend it.** Open on a contents card listing all the items, and return to the same card at the
   end with each one ticking off. The viewer gets the map before the journey and the receipt after,
   and the close lands as completion rather than as a stop.

## Put the confession in the frame, not inside an item

If a piece carries an admission, state it once at the top and let it cover everything. Attaching it
to one item makes it a non-sequitur.

A draft ended item two with "…and given eighty two of them the same name. **Ours.**" That "Ours."
was doing the confession's work from inside an item where the viewer had no reason to expect it, and
it landed as a stray word.

Related, and an owner ruling worth carrying: **do not hedge the count**. A frame line reading "five
things were broken, four were our own fault" was cut for implying we were dodging responsibility for
the fifth. Owning all of them is both simpler and stronger, and it removes a distinction the viewer
never asked for.

## Give the credit outward at the close

A closing line that attributes the work to the system ("it came out of the logs") is weaker than one
that attributes it to the people whose usage surfaced it. Say who found it, and thank them.

**But check the attribution before making it.** "Our customers reported these" is a different and
usually false claim from "these surfaced through real use." Walk each item back to how it was
actually found — a support thread, a demo, an internal audit — and phrase the credit to match what
the evidence supports.

## The screen carries the evidence, the voice carries the meaning

The rule lives in `references/voice.md` because that is where it bites hardest, but it is a
structural decision and belongs in the plan doc, not in the edit:

- **Voice:** "the page where we ask you to pay had text you could not read."
- **Screen:** `1.08:1` · `4.5:1 required`

Deciding this while writing the beat table means the panels are designed as evidence from the start,
instead of being backfilled with whatever number was in the source issue.

## Structure costs runtime. Budget for it.

Scaffolding is not free: a frame line, five ordinals and a close added roughly 40% to one film's
narration. That is the price of coherence and it is usually worth paying, but **decide the runtime
before generating audio**, not after, because a voice change or a script redesign moves every beat
and every caption and is a timeline rebuild rather than a file swap.

If the piece cannot hold its runtime target with the scaffolding in, **cut items, not scaffolding**.
Three items told as a list beat five told as a jumble.
