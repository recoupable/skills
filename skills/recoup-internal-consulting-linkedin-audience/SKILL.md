---
name: recoup-internal-consulting-linkedin-audience
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Turn LinkedIn engagement into leads. Use on \"who engaged with my post\", \"pull LinkedIn leads\", \"find warm leads from LinkedIn\", or after a post gets traction. Pulls reactors/commenters via Apify and cross-references Attio to surface engaged-but-not-in-CRM outreach candidates."
---

# Consulting LinkedIn Audience

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Social selling: mine post engagement for warm leads and feed them into the pipeline.

## Steps
1. **Pull engagement.** For a post URL, run:
   `python integrations/linkedin/_work/pull_engagement.py --post-url "<url>"`
   → writes normalized engaged people (name, headline, profile URL) to
   `integrations/linkedin/engagement/<date>-engagement.json`. (Apify run = pay-per-result.)
2. **Cross-reference Attio (live).** For each engaged person, check if they already exist in Attio
   (`POST /v2/objects/people/records/query` by name/handle). Split into: **already a contact** vs.
   **new** vs. **existing product-user**.
3. **Score & prioritize.** Rank by fit to the ICP (`positioning/`) — title/seniority, company in a
   target account (`integrations/attio/` Target Accounts list), and engagement depth (comment > like).
4. **Act.**
   - New high-fit people → create an Attio person (`relationship = lead`) and draft outreach
     (chain `recoup-internal-consulting-outbound-email`; its context gather reads the full post they engaged with).
   - Existing contacts who re-engaged → flag for `recoup-internal-consulting-followup-sequencer`.
5. **Record.** Save the ranked candidate list to `integrations/linkedin/engagement/` and note any
   new Attio records created.

Don't mass-add scraped people to Attio as "lead" — only real, qualified-fit people. Keep the CRM clean.
