---
name: recoup-internal-consulting-lead-temperature
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Score a lead's relationship temperature (0-10) and posture from their full communications graph, so follow-ups match where the relationship actually stands. Use before drafting any re-engagement or outreach to a known lead, on \"what's their temperature\", \"score this lead\", or in the Friday warm-leads sweep."
---

# Consulting Lead Temperature

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Turn a lead's full comms history into a **temperature** (how hot the opportunity) and a **posture**
(how to speak to them). Relationship state is Attio's domain, so Attio plus the deal dashboard hold the
canonical score; this skill computes it. Feeds `recoup-internal-consulting-email-atomizer`,
`recoup-internal-consulting-followup-sequencer`, and `recoup-internal-consulting-outbound-email` as the posture input.

Heuristic, not truth: cite every input, label anything not evidenced [UNVERIFIED], never let the
number overrule judgment. **Score from primary sources only — verbatim Granola transcripts and the
actual email bodies, never the AI summaries.** Granola note bodies (`.md` mirror) are AI summaries:
leads to verify, not evidence. Tone, who-led, enthusiasm, and stalls must be read off the transcript.

## Steps

1. **Load one lead's full graph (deal-scoped only, never cross jobs).** All Gmail threads to/from the
   person and their team (`search_threads` then `get_thread`, plus `integrations/gmail/threads/<deal>.json`),
   the live Attio record and stage, and the deal `AGENTS.md`. For meetings, **read the verbatim Granola
   transcript of every call with every person from the company — never just the AI summary note.**
   - The `.md` mirror in `integrations/granola/.../<deal>/` is an AI *summary*; use it only as the index
     of which meetings exist and to grab each note's `note_id` from frontmatter.
   - Pull the verbatim transcript for each `note_id` via the Granola API
     (`GET https://public-api.granola.ai/v1/notes/{note_id}?include=transcript`, `Authorization: Bearer $GRANOLA_API_KEY`).
     Resolve `microphone` against that recording's owner; `speaker` is not necessarily one identified
     person. Verify attribution before assigning a name. Review title and content for this account
     before capture. Use the available connector for one reviewed note, or a compatible local helper:
     `python3 integrations/granola/_work/pull_transcript.py --note <id> --reviewed-scope --out <dest>`.
     Never use a bulk transcript importer or fetch unrelated notes based only on an attendee match.
   - **Do not skip any meeting or any colleague.** Read every transcript involving anyone at the account
     (champion *and* every teammate looped in), reading tone at the start vs. the end of each call.
     Missing access, withheld mixed-scope material, or an unavailable transcript must remain a labeled gap.
2. **Build the touch timeline.** Every meeting and email in order: date, who initiated, what happened,
   tone. Cite each (thread or file). This is the evidence the score rests on.
3. **Score four components, 0-10 each, with evidence:**
   - **Engagement (E):** depth. email-only < meetings < multiple meetings + they pulled in colleagues / made intros / asked for materials.
   - **Reciprocity (R):** who replied last, and the their-touch vs your-touch balance recently. You chasing with no reply pulls this down.
   - **Tone trajectory (T):** sentiment across touches, the start-vs-end-of-meeting shift, reply enthusiasm. Rising or falling.
   - **Progression (P):** did the stage advance, stall, or regress.
4. **Combine, then decay.** `raw = 0.35*E + 0.25*R + 0.25*T + 0.15*P`. Apply recency decay on the
   clock since the last THEM-initiated touch: <=2wk x1.0 · 2-6wk x0.9 · 6-12wk x0.75 · 3-6mo x0.5 ·
   >6mo x0.3. Clamp 0-10. (Weights and decay are v1; tune as data accrues.)
5. **Set the objective from the score, then the posture.** The objective is what this one touch is
   for. Do not skip ahead to closing a lead who is not hot; that is what reads as a pushy vendor.
   - **8-10 hot:** objective = advance or close. Direct ask, book the next step.
   - **5-7 warm or cooling:** objective = regain attention and curiosity, not a close. Lead with
     something genuinely interesting to them, ask for little or nothing. A reply or renewed interest
     is the win, not a meeting.
   - **2-4 cold:** objective = stay on the radar. Pure value, no ask.
   - Rising vs falling shifts tone even at the same score.
   The ask scales with temperature: hot earns a real ask, cooling a soft one or none, cold none.
6. **Write the record** to the deal `AGENTS.md` dashboard: `Temperature: X/10 (trend)`, a 2-line
   "what it means and why", the sub-scores, and the computed date. Sync the number to the Attio field
   when one exists. Keep it cited.
Output: a cited temperature record (score, sub-scores, timeline, posture) on the deal dashboard.
Recompute on-touch and in the Friday warm-leads sweep, so it doubles as a cooling-lead radar.

## How drafting uses it

Skills do not call each other or pass variables at runtime; they share state through files. There is
no handoff. The email skills (`recoup-internal-consulting-outbound-email` and the drafters) read the Temperature and
posture straight from the deal dashboard during their own "read all context" step, and set tone and
ask from it. This skill's job ends at writing a clear, cited record (step 6).
