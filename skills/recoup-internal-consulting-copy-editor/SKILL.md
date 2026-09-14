---
name: recoup-internal-consulting-copy-editor
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Editorial copy-edit pass on a finished draft, run through a fresh-context subagent reviewer. Use on \"copy-edit this\", \"edit this article\", \"do an editor pass\", \"give it a hard edit\", \"review my draft\", \"check this for slop\", or as the last gate before publishing any long-form article, pillar, post, or email. Dispatches a fresh-eyes subagent that returns structured editor's notes (AI slop, non-conversational phrasing, confusing rhetoric, simpler-rewrite and narrative/storyline opportunities, and anything an editorial-outlet editor would flag); the main agent then triages and implements the accepted edits, then re-checks against the house standard."
---

# Consulting Copy-Editor

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

A second set of eyes on a finished draft. The review runs in a **fresh-context subagent** so it reads like a first-time editor, not the author. The **main agent implements** the edits, with judgment. This skill *uses* `recoup-internal-consulting-copy-writer` (the house voice + anti-slop standard) and `evals/content/score_run.py` (the check) — it does not redefine them.

## When to run
On request ("copy-edit / edit / hard edit / editor pass / review this draft"), and as the last gate before publishing any long-form piece.

When a parent workflow already has a later score/report/commit gate (for example `recoup-internal-consulting-nightly-content`),
run the editorial pass through implementation (steps 1-5), then let the parent workflow handle verification,
reporting, and committing after the full bundle is assembled.

## Steps

1. **Pick the target.** The one file to edit (default: the draft in question; if unclear, ask). Note its kind (pillar article, post, email) and rough length.

2. **Resolve the paths before dispatch (the step that makes a run smooth).** The subagent starts with fresh context and no knowledge of this repo — it only knows what you hand it as **absolute paths**. Resolve all of these and substitute them into the brief's `{PLACEHOLDERS}`:
   - `{ARTICLE_PATH}` — the target file from step 1.
   - `{ANTISLOP_PATH}` — `references/anti-slop.md`
   - `{VOICEPRINCIPLES_PATH}` — `references/voice-principles.md`
   - `{LONGFORM_LINE}` — for a 1,000+ word piece only, a third `-` bullet pointing at `references/long-form-essay.md`; otherwise delete the line.

   Resolve these bundled reference paths relative to this installed skill. Pass their actual absolute
   paths to the reviewer. The files ship alongside this skill; no sibling installation is required.

3. **Dispatch ONE fresh-context subagent, read-only.** It reviews and returns notes; it does NOT touch any file. Paste the **Reviewer brief** below verbatim, with the `{PLACEHOLDERS}` filled from step 2.
   - Claude Code: Agent/Task tool, `subagent_type: generalPurpose`, `readonly: true`.
   - Other harnesses / subagents disabled: see the harness map in `references/subagent-dispatch.md`; if none, run the brief yourself in a separate pass, reading the article cold.

4. **Triage the notes with judgment** (you are the editor-in-chief, not a rubber stamp):
   - Accept clear wins: slop, wordiness, confusing lines, dead transitions, a saggy opening or ending.
   - Reject any "fix" that flattens the author's voice, deletes a deliberate choice, or weakens a real point. Spirit over letter.
   - **Evidence discipline (non-negotiable):** never let a reworded line change a fact, number, date, dollar figure, name, or client claim. If a suggested rewrite touches one, keep the verified original or confirm with the user — never fabricate to make a sentence flow.
   - **Client-facing care:** if the piece names or implies a client, read each edit from the client's chair (see the client-work trust lens in `anti-slop.md`).

5. **Implement** the accepted edits in the draft.

6. **Verify.** Re-scan for em-dashes and banned vocab. If running standalone, run `python evals/content/score_run.py`; the edited piece should read clean on its own (per-draft 100). Fix anything the edits introduced.

7. **Report & commit.** If running standalone, write a short summary: what changed, and what you deliberately left and why. Commit with a why-first message.

## Reviewer brief (paste verbatim into the subagent; fill the {PLACEHOLDERS})

```
You are a senior copy editor for a sharp editorial outlet (a demanding features desk). You are seeing this piece for the first time. Edit with fresh eyes; do not assume the author's intent.

Read, in order:
1. The draft to edit: {ARTICLE_PATH}
2. The house standard you must edit against (this defines "slop" and "voice" here — use it, not a generic notion):
   - {ANTISLOP_PATH}
   - {VOICEPRINCIPLES_PATH}
   {LONGFORM_LINE}

Review the draft across these axes:
- AI slop: anything the anti-slop file names (banned vocab, em-dashes, negative-parallelism/reframes, significance pointers, vague authority, empty adjectives, writerly surprise setups, etc.).
- Non-conversational phrasing: lines no one would say out loud; writerly tics; corporate or jargon voice.
- Confusing rhetoric: claims that don't land, buried logic, a section that doesn't deliver what its header promises.
- Simpler said: the same point in fewer or plainer words, with no loss of meaning.
- Narrative & storyline: the hook, the throughline, section order, transitions, momentum, and an ending that lands. Flag where the piece sags, repeats itself, or loses the reader.
- Anything else a great editor would flag: title, evidence/specificity, balance, repetition, length.

Hard rules:
- Do NOT edit or write any file. Return notes only.
- Do NOT invent facts. If a stronger line would change a number, date, dollar figure, name, or client claim, say so and leave the fact to the author — never fabricate.
- Preserve the author's voice. Suggest; don't homogenize.

Return your notes in exactly this shape, no preamble:
1. Overall read (3-5 sentences): the single biggest opportunity (usually narrative/structure), and is it publish-ready as-is?
2. Edits, highest-impact first. For each:
   - Location: the verbatim sentence/phrase (quote it).
   - Category: slop | non-conversational | rhetoric | simplify | narrative | other
   - Severity: must-fix | consider
   - Problem: one line.
   - Fix: the concrete rewrite, or "cut".
3. Title: keep, or 2-3 stronger options.
```

## Notes
- The subagent is a **reviewer, not an author** — keep all edits in the main agent so voice and final judgment stay in one hand.
- **Compound it:** if the reviewer catches a brand-new slop or non-conversational pattern, propose a change to the canonical copy-writer standard (bad → good) and re-sync its registered copies so it's caught automatically next time — don't just fix the one instance.
