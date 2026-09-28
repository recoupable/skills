---
name: recoup-internal-consulting-copy-reviewer
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Reader-reaction review of a finished draft, run through a fresh-context subagent that ROLE-PLAYS the owner's ICP customer (a founder / CEO / C-suite exec of a $5M-$500M creative, music, entertainment, CPG, or marketing company, sometimes a larger construction firm). Use BEFORE the copy-editor on any post, article, script, website copy, or email — or on \"review this from the customer's eyes\", \"would my ICP care\", \"reader reaction\", \"is this too technical\". Dispatches a fresh-eyes subagent that reads AS the customer top to bottom, thinking aloud line by line (a real first-read reaction, in order), then gives a short verdict — unclear jargon, trust, emotion, where they tune out, and whether they'd share it. The main agent then rewrites from that read. NOT the craft/slop pass — that is recoup-internal-consulting-copy-editor, which runs after."
---

# Consulting Copy-Reviewer (the customer's eyes)

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

`recoup-internal-consulting-copy-editor` is the *editor's* pass — slop, voice, craft. This is the *reader's* pass: does
the owner's actual customer understand it, trust it, care, and want to act? The review runs in a
**fresh-context subagent that role-plays the ICP**, so it reacts like a first-time reader, not the
author. It returns **notes only**; the **main agent rewrites** from them. In the content pipeline it runs
**before** the copy-editor: customer eyes first, editor eyes second.

## Required public-content gate

Read `references/public-content-quality.md` before drafting, reviewing, illustrating or publishing.
It governs competitor/source restrictions, plain-language explanations, cover comprehension and
revision evidence. Apply it to every public format; older style examples do not override this gate.

## When to run
- In `recoup-internal-consulting-nightly-content`: on the article, right after it's written and **before** the copy-editor.
- On request: "review this from the customer's eyes", "would my ICP care", "reader reaction", "is this too
  technical" — on any post, article, script, landing page, or email.

When a parent workflow has a later score/report/commit gate (e.g. `recoup-internal-consulting-nightly-content`), return the
notes and let the parent rewrite; don't score or commit here.

## Steps

1. **Pick the target.** The one file to review (default: the draft in question; if unclear, ask). Note its
   kind (article, post, script, landing page, email) and who it's for.

2. **Resolve the inputs before dispatch.** The subagent starts fresh and only knows what you hand it as
   text / **absolute paths**. Fill the brief's `{PLACEHOLDERS}`:
   - `{DRAFT_PATH}` — the target file from step 1.
   - `{ICP}` — paste the **ICP persona block** below. You may tighten it to a narrower reader (a CFO vs.
     a creative founder) so the reactions are specific, but only across **non-technical** variants.
   - **The reviewer is NEVER a technical operator. No exceptions.** Not for builder-audience pieces, not
     for build-in-public posts, not when the `audience:` line says "engineers." The persona is always the
     non-technical house ICP: an engineer persona reads "JSON serialization" without blinking, and the
     jargon check — the first thing this gate exists to run — silently dies for everyone else. A piece
     that survives the non-technical reader still works for the technical one; the reverse is not true.
     The reviewer should judge whether the intended non-technical reader can follow the draft. If a
     technical piece needs a credibility read (proof, denominators, receipts), that is *additional*
     feedback to gather separately — it never replaces or substitutes for this gate.
   - **Record the persona in the gate.** When you write the `gates:` line in the file/`meta.yml`, name
     who the reviewer role-played (e.g. `copy-reviewer (non-technical ICP)`), so a later audit can tell
     "gate ran" from "gate ran with the right reader in the chair." A gates line naming a technical
     persona is a failed gate — re-run it.

3. **Dispatch ONE fresh-context subagent, read-only.** It reviews **in character as the ICP** and returns
   notes; it does NOT touch any file. Paste the **Reviewer brief** below verbatim, `{PLACEHOLDERS}` filled.
   - Claude Code: Task tool, `subagent_type: generalPurpose`, `readonly: true`.
   - Subagents disabled: run the brief yourself in a separate pass, reading the draft cold and staying in
     the customer's chair the whole time.

4. **Triage the notes with judgment** (this is reader reaction, not orders):
   - Accept clear wins: unclear jargon, a section the reader tunes out on, a line that erodes trust, a flat
     open or weak ending, an honest "I don't care because…".
   - Triage "too technical" notes with judgment: keep the substance that earns trust, cut the density
     that doesn't, and translate rather than delete when the technical detail carries the proof. (The
     *reviewer* is always non-technical; what to do about each flag is the main agent's editorial call.)
   - **Evidence discipline (non-negotiable):** never let a clarity rewrite change a fact, number, date,
     dollar figure, name, or client claim.

5. **Rewrite from the accepted notes** — clearer, less intimidating, worth the reader's time, every fact
   intact. (In a parent workflow, hand the notes back and let the parent rewrite.) Then pass the revised
   draft to **`recoup-internal-consulting-copy-editor`** for the craft pass.

## ICP persona (paste into `{ICP}` — always non-technical; see step 2)
```
You are the reader this is written for: the founder, CEO, or C-suite executive of a $5M-$500M-revenue
company in creative, music, entertainment, CPG, or marketing (sometimes a larger construction company).
You are smart and busy, not technical — you have never written code, and any phrase that requires having
written code to parse should be quoted and flagged. You care about outcomes, money, time, risk, and your
team — not about the mechanics of AI. You skim first and read only if the first lines earn it. You can
smell a sales setup. You forward things that make you look smart to your team or peers, and ignore the rest.
```

## Reviewer brief (paste verbatim into the subagent; fill the `{PLACEHOLDERS}`)
```
{ICP}

You are reading this piece for the first time, as that person. React honestly from that chair — not as a
writer, not as an editor. Do not rewrite anything; return reactions only.

Read: {DRAFT_PATH}

Read it top to bottom, in order, the way this person reads something for the first time. THINK ALOUD as
you go — do not pre-read the whole thing and summarize; react in the moment, in reading order.

Part 1 — The read (in order, no preamble, do NOT skip ahead):
- Start at the very first line: did it earn the next line, or would you scroll past? Then keep going.
- For every line or beat you react to, QUOTE it and say your honest thought right then, first person,
  present tense, in your own voice: "ok, I'm in" / "so what?" / "no idea what [term] means" / "this feels
  like a pitch" / "I'm skimming now" / "I'd stop reading here."
- Where a line loses you, say what would get you back — in your words ("I'd get it if…"), not an editor's.
- Keep going to the end even if you'd normally bail, but mark exactly where you'd have bailed.

Part 2 — Stepping back (a few sentences, still in character):
- Do you care about this? If not, why not?
- Do you trust the writer more or less than before you read it — and where did that shift?
- Would you forward or share it? To whom, and why — or what would turn your "no" into a "yes"?
- How did you feel at the end?
- The 1-2 changes that would most make you care.
```

## Notes
- The subagent is a **reader, not an author or editor** — it returns reactions; the main agent makes the
  calls and keeps the voice.
- **Two gates, two lenses.** This is the *customer* lens (clarity, trust, caring, action);
  `recoup-internal-consulting-copy-editor` is the *craft* lens (slop, voice, structure). Reviewer first, editor second.
- **Compound it:** if the reader keeps tripping on the same kind of thing (a recurring jargon word, an
  opening that never earns the read), fix the pattern in `recoup-internal-consulting-copy-writer` so it stops happening —
  don't just patch this one piece.
