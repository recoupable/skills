---
name: valuation-sales-pipeline
description: >-
  Work the Recoup "Valuation Leads" sales funnel in Attio — take an inbound
  catalog-valuation lead and progress it from "valuation ran" to "signed up for
  Pro." Researches who the lead is and their relationship to the artist they
  valued, qualifies the catalog against revenue goals, enriches and advances the
  Attio CRM record, and drafts the first outreach email plus a clean one-page
  valuation PDF. Use when asked to "work the valuation funnel", "qualify this
  lead", "who ran this valuation", "is this catalog worth our time", "update the
  Attio pipeline", "advance this lead", "draft outreach for this valuation", or
  "turn valuation leads into Pro signups". Requires an Attio API key and a Recoup
  API key.
---

# Valuation Sales Pipeline

Turn inbound **catalog-valuation leads** into **Recoup Pro signups**. When someone
runs Recoup's free "what is my catalog worth?" valuation, a lead lands in the Attio
**Valuation Leads** funnel at stage **New**. This skill is the repeatable motion for
working that lead to a paying customer.

The valuation is the wedge; the product is **growing the catalog's value** (recover
uncollected royalties + grow streams + document it for a higher multiple). The job is
to prove that quickly enough that the lead converts.

## When to use

- "Work / triage the valuation funnel." "Who's in the pipeline?"
- "Who ran this valuation and what's their relationship to the artist?"
- "Is this catalog worth our time?" (qualify against goals)
- "Fill in the Attio profile and advance this lead."
- "Draft the welcome email + a clean valuation PDF for this lead."

## Prerequisites

- `ATTIO_API_KEY` — an Attio access token (read-write on records + list entries).
- `RECOUP_API_KEY` (`recoup_sk_…`) — for catalog sizing via the Research API; mint one
  with `POST https://api.recoupable.com/api/agents/signup`. Load the
  `music-industry-research` and `catalog-value-estimator` skills for endpoint detail.
- `reportlab` for the PDF: `pip install reportlab --break-system-packages`.
- Scripts ship in this skill's `scripts/`; run them from the skill directory as
  `python3 scripts/<name>.py`.

The funnel's stages, field slugs, and the exact Attio API calls are documented in
`references/attio-funnel.md`. The qualification rubric is in
`references/qualification-rubric.md`. The email template is in
`templates/outreach-email.md`. A spoofed end-to-end example is in `fixtures/`.

## The pipeline (stages)

```
New → Report Delivered → Qualified → Pro Offer Sent → Pro Active (Won) → Lost
```

`New` = valuation ran (auto). `Pro Active (Won)` = a Stripe Pro subscription is live —
the one true win. `Lost` requires a Lost Reason. See `references/attio-funnel.md`.

## Workflow

### 1. Research the lead

Pull the lead's Attio record + funnel entry (`references/attio-funnel.md` has the calls).
Capture: `looked_up_artist`, `est_catalog_value`, `lifetime_streams`, `follower_count`,
`spotify_artist_url`, `email_addresses`, `name`, `primary_location`, `valued_at`.

Then establish **who they are and how official they are to the catalog** — this decides
the outreach tone and whether they can actually authorize work:

- Web-search the artist + the person/brand behind the email. Compare the email handle to
  the looked-up artist (self-search of own brand vs. a third party).
- Classify the **Relationship**: `Owner/Operator` (the artist or label/brand itself) ·
  `Label` · `Manager` · `Collaborator` (released work with the artist) · `Fan/Other` ·
  `Unknown`. Owners/labels/managers can authorize an engagement; collaborators are warm
  insiders; fans rarely convert.
- Cross-check recent product activity (signup date, credits used) if you have account
  access — a lead who burned most of their credits is highly engaged.

### 2. Qualify against goals

Score the lead with `references/qualification-rubric.md`. In short: a real, mid-size
catalog (meaningful lifetime streams and estimated value) held by someone official enough
to say yes, active recently. Decide:

- **Pursue** → continue to step 3.
- **Backlog** → real but low priority (small catalog or unclear relationship). Leave at
  `New`; note why.
- **Disqualify** → move to `Lost` with a Lost Reason (e.g. junk/zero-stream lookup, a fan,
  a test row). Don't spend outreach on these.

### 3. Enrich the Attio profile

For a pursued lead, write back to the Attio record/entry (`references/attio-funnel.md`):

- Person record: set `name` (real person or brand), and socials if known.
- Funnel entry: set `Catalog Value`, `Relationship`, and `Owner` (the Recoup rep working
  it). These make the board sortable by $ and accountable.
- Advance the stage to **Report Delivered** only once the email + PDF actually go out
  (step 4). Until then it stays `New`.

### 4. Draft outreach + valuation PDF

- Render a clean one-page valuation PDF from the lead data:
  `python3 scripts/render_valuation_pdf.py --lead fixtures/example-lead.json --out ./out`
  (swap in the real lead JSON; see `fixtures/example-lead.json` for the shape).
- Draft the first email from `templates/outreach-email.md`: personal, references the
  specific artist + their number, **delivers the PDF**, gives one free specific insight
  (a playlist gap, a likely-uncollected royalty source, a concentration note), and ends
  with a low-friction CTA. Send from the rep, not a generic address.
- After it's sent, move the entry to **Report Delivered** and log a note of what was sent.

## Notes & caveats

- **PII / privacy.** Leads are real people. Keep names, emails, and account IDs inside the
  CRM; the bundled `fixtures/` use spoofed data only. Never paste a lead's PII into shared
  docs or external services.
- **Define "Won" precisely** as a live Stripe Pro subscription — not a reply or a call.
- **Relationship drives capacity to pay.** A $300k catalog implies only ~$24k–$36k/yr of
  net label share, so a single catalog rarely justifies a large retainer alone — convert
  to Pro and/or a managed growth+recovery engagement, or pursue the strongest as a pilot.
- Attio list/option IDs are workspace-specific; discover them at runtime (see the
  reference) rather than hardcoding.
