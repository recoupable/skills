---
name: recoup-internal-consulting-prospect-resurrection
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Revive cold/dormant prospects from historical meeting data. Use on \"who's gone cold\", \"resurrect dead deals\", \"mine my old prospects\", quarterly pipeline reviews, or when pipeline is thin. Turns past conversations into ranked, grounded re-engagement."
---

# Consulting Prospect Resurrection

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

The cheapest pipeline is warm relationships that already know you. Mine the Granola archive for
dormant prospects and turn them into ranked, personalized re-engagement.

## Steps
1. **Find the cold set.** Scan `integrations/granola/<workspace>/prospects/` (and `_intro-calls/`) for
   each prospect's **last meeting date**. Flag anything dormant (e.g. >90 days). Sort by recency.
2. **Cross-reference Attio (live).** Skip anyone already an active deal/client. Note who's a
   `product-user` vs a real lapsed lead.
3. **Ground each one.** Read the prospect's latest Granola note(s) and pull: the buyer/champion,
   their **stated pain in their words**, what was discussed, and the likely reason it stalled.
   (Remember: Granola bodies are AI summaries — confirm specifics, don't fabricate.)
4. **Rank** by fit to the ICP (`positioning/`) × pain intensity × deal ceiling. Big logos and
   well-articulated pain rise to the top.
5. **Draft re-engagement** per prospect: a value-first opener that references *their* stakes (not a
   pitch), plus a 3-touch cadence (use `recoup-internal-consulting-followup-sequencer`). Mark all as drafts to review.
6. **Write the report** to `pipeline/_cold-prospect-resurrection-YYYY-MM-DD.md` (ranked table + angles).
7. **Enter the top picks** into the pipeline: create the Attio deal (stage Lead) and a
   `pipeline/01-leads/<prospect>/` folder with a grounded dashboard + `followups.md`.

Output: a prioritized resurrection report + live leads in Attio and the pipeline.

Resolve `<workspace>` from `integrations/granola/AGENTS.md`; preserve the existing mirror directory name.
