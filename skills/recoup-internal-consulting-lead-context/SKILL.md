---
name: recoup-internal-consulting-lead-context
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Assemble a grounded context dossier on a lead BEFORE any outreach or personalization, so drafts are accurate and the agent never punts \"I need your input\" on something it could look up itself. Run before recoup-internal-consulting-email-atomizer, recoup-internal-consulting-followup-sequencer, or any 1:1 outreach, especially for content-sourced leads (LinkedIn engagers)."
---

# Consulting Lead Context

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

Gather everything knowable about a lead before writing to them. The governing rule:

> **Resolve context yourself. Escalating "confirm X before I send" to the human is the LAST resort,
> only after the sources below are exhausted. If the answer sits in a post, a profile, a thread, or a
> company's homepage, go get it.**

Use the source post, thread, or company material to resolve context before escalating a question. Missing evidence remains a labeled gap.

## When to run
Before any personalized outreach. `recoup-internal-consulting-outbound-email` runs this as its context step. It matters most for
**content-sourced leads** (someone who reacted to / commented on a post), where the hook is whatever
they responded to, not a generic intro.

## Sources (gather every one that applies; cite each, quote the primary)
1. **The trigger: what they actually engaged with.** If the lead came from content, read the FULL
   post/article they engaged, not just their one-line comment. The comment only means something
   against the thing it answered.
   - LinkedIn: take the post URL from the lead's `posts` / engagement record, match it in
     `integrations/linkedin/published/<date>-posts.json`, and read the `content` field (the full post
     text). If it is not in the local mirror, pull the live post.
   - Capture their own verbatim comment/reaction and which posts they hit (the engagement /
     lead-candidates JSON).
2. **Who they are.** Enriched title / company / seniority (GetLeads / Apify), their headline, and a
   quick read on what their company actually does (its site or firmographics) so you reference it
   correctly and never miscast it.
3. **Any prior relationship.** Gmail `search_threads` for the person AND their company domain
   (colleagues), then `get_thread` for the bodies that matter. Plus Granola notes, the live Attio
   record, and the `pipeline/`/`clients/` folder if one exists.
4. **Temperature + posture.** The `recoup-internal-consulting-lead-temperature` record. If it is missing or stale
   (not recomputed since the last touch), run that skill first.

## Output: a short dossier per lead
- **Who:** name, title, company, what the company does.
- **Trigger:** the post they engaged + what it actually said + their verbatim comment.
- **Hook:** the specific, true opening this gives you (and the exact deliverable they're asking for,
  if their engagement was a CTA, e.g. "commented for access" → they want access, not a walkthrough).
- **History:** any prior contact (or "none, true cold").
- **Posture:** temperature + the objective it sets (hot = advance, cooling = re-earn attention, cold = pure value).
- **[MISSING]:** label a source ONLY if you genuinely could not retrieve it after trying. That is the
  one thing it is fair to raise with the human.

Then hand the dossier to the drafting skill. Every claim in the eventual email must trace to something
gathered here (evidence discipline).
