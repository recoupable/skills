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
`references/attio-funnel.md`. Pulling a lead's catalog — album art + live streams —
straight from the public Recoup APIs (the same ones the marketing valuation tool uses,
no scraping) is documented in `references/recoup-valuation-api.md` and automated by
`scripts/fetch_catalog.py`. The qualification rubric is in
`references/qualification-rubric.md`. The email template is in
`templates/outreach-email.md`. A spoofed end-to-end example is in `fixtures/`.

## The pipeline (stages)

```
New → Report Delivered → Qualified → Pro Offer Sent → Pro Active (Won) → Lost
```

`New` = valuation ran (auto). `Pro Active (Won)` = a Stripe Pro subscription is live —
the one true win. `Lost` requires a Lost Reason. See `references/attio-funnel.md`.

## The report PDF (what you send)

`scripts/render_valuation_pdf.py` produces a 3-part PDF whose order is deliberate:

1. **Page 1 — executive summary.** The headline value + range and the top releases by streams
   (with album art) — the *same figures the contact saw in the tool*. Its one job is to build
   trust on first contact by proving the report is accurate to what they already saw. Lead with
   accuracy, not a pitch.
2. **Page 2 — an honest reading.** Grounded, specific observations from the page-1 data
   (concentration, range caveats, master-side scope). **No unverified claims** about what Recoup
   "will" recover or grow — only what the data shows.
3. **Appendix — full source data.** Every measured release (album art + year + tracks + streams),
   matching the tool's complete list, so nothing is hidden behind the summary.

Build the data with `scripts/fetch_catalog.py` (below), add the dollar band, then render.

## Workflow

### 1. Research the lead

Pull the lead's Attio record + funnel entry (`references/attio-funnel.md` has the calls).
Capture: `looked_up_artist`, `est_catalog_value`, `lifetime_streams`, `follower_count`,
`spotify_artist_url`, `email_addresses`, `name`, `primary_location`, `valued_at`.

Then establish **who they are and how official they are to the catalog** — this decides
the outreach tone and whether they can actually authorize work:

- Web-search the artist + the person/brand behind the email. Compare the email handle to
  the looked-up artist (self-search of own brand vs. a third party).
- **Verify the person's *current* role, not a stale one.** People change companies and keep
  legacy profile handles — pick the LinkedIn whose handle/email domain matches the lead's email,
  and confirm their *present* employer (a title pulled from an old campaign can be years out of
  date and will mis-set the Relationship). LinkedIn and Instagram block `WebFetch` (HTTP 999) —
  read them via the **authenticated browser (chrome-devtools MCP)**.
- Classify the **Relationship**: `Owner/Operator` (the artist or label/brand itself) ·
  `Label` · `Manager` · `Collaborator` (released work with the artist) · `Fan/Other` ·
  `Unknown`. Owners/labels/managers can authorize an engagement; collaborators are warm
  insiders; fans rarely convert. Keep the lead JSON `relationship` and the Attio field in sync —
  if you re-classify after deeper research, update **both** (the PDF reads the JSON).
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

- Pull the catalog + album art straight from the public APIs (no scraping):
  `python3 scripts/fetch_catalog.py --artist-id <spotifyId> --out lead.json` — fills streams,
  album art, and release counts. Add the dollar band (from the tool, or computed with the
  `catalog-value-estimator` skill) to `lead.json`. Don't infer "dormant" from a `$0` row in the
  live UI — confirm against the measurements endpoint (see `references/recoup-valuation-api.md`).
- **Onboard the valued artist under the lead's own Recoup account and pull exact socials over the
  API** (part of working the lead, not overkill). The self-contained recipe — resolve `account_id`
  via `POST /api/accounts {email}` (the email→`account_id` lookup; no Supabase), create the artist,
  `PATCH` profile URLs, scrape, poll — is in `references/recoup-valuation-api.md`. Put the `account_id`
  in lead JSON `account.owner_account_id` so the PDF admin line carries it.
- Fill the lead JSON `socials` block so the report renders the "Artist channels" line. Use the
  **exact** `follower_count` + **real** `bio` from the scrape (blank, never filler, if unverified),
  and cross-check the **same Spotify artist id** so you don't attach a same-name impostor.
- Render the valuation PDF (headline + a top-releases breakdown with album art, an honest
  "reading your result" page, and a full-catalog appendix):
  `python3 scripts/render_valuation_pdf.py --lead lead.json --out ./out`
  (see `fixtures/example-lead.json` for the shape).
- Draft the first email from `templates/outreach-email.md`. First touch must be **scannable in
  3-5 seconds**: **2 sentences + 3 bullets + 1 CTA**, from the rep (not a generic address). The PDF
  carries the depth - keep caveats and detail out of the email. Don't pitch the engagement here;
  that's the call.
- After it's sent, move the entry to **Report Delivered** and log a note of what was sent.

## Notes & caveats

- **PII / privacy.** Leads are real people. Keep names, emails, and account IDs inside the
  CRM; the bundled `fixtures/` use spoofed data only. Never paste a lead's PII into shared
  docs or external services.
- **Relationship drives capacity to pay** - a single six-figure catalog rarely justifies a large
  retainer; convert to Pro and/or a managed engagement, or run the strongest as a pilot. Sizing and
  routing detail in `references/qualification-rubric.md`.

## Lessons from live runs (ICEBOX · Chilled Cat · Eurotripp)

The API/measurement gotchas live in `references/recoup-valuation-api.md`; the report-judgment ones
are spelled out here because they shape what you write.

- **Before you trust a run, watch for these (all detailed in `references/recoup-valuation-api.md`):**
  the auth route-split (hex `x-api-key` works on `/spotify/*` only; `/research/*` needs a Bearer
  token that expires ~1h) · 0-streams-across-everything means auth/expiry, not a dormant catalog · a
  credit-exhausted free run undercounts, so re-measure the full catalog and reframe as "we finished
  your interrupted run" · the dollar model is trailing-12-month-driven, so a single-snapshot lead
  can't be priced same-day.
- **Gross streams ≠ owned value - read it honestly:**
  - *Collaborations / compilations* (Chilled Cat's "Vibes" releases are each Chilled Cat × a
    different producer): the owner holds only a **split** of each track, so realizable value is below
    the gross. Say so, and point to a statement to pin the splits.
  - *Cover songs* (Eurotripp's "Where's Your Head At" = ~95% of streams, a Basement Jaxx cover): the
    artist owns the **master, not the publishing**. Lead with master royalties + neighboring rights
    (SoundExchange) + Content ID, not catalog publishing.
  - Curate the displayed release list so a single that also sits on a compilation isn't shown twice
    (lifetime totals are already deduped by track id in `fetch_catalog.py`).
- **Pre-cache album art before rendering.** Downloading 100+ covers inline gets `i.scdn.co` throttled
  and `render_valuation_pdf.py` silently drops the failed images. Pre-fetch covers to local files
  (retries + a small delay) and point the lead JSON `image` fields at `file://` paths.
- **Keep page-2 reading concise, and use plain hyphens (no em/en dashes) in all outbound copy** -
  long reading notes push the footer onto a near-empty extra page, and em dashes read as AI-generated
  to recipients. The render script auto-generates the concentration paragraph from the data, so add
  only **2-3 short `reading_notes`** of your own and **don't repeat the concentration point** - that
  duplicate is what tips page 2 over. Expect a **4-page** render (cover · reading+channels ·
  Appendix A x2); a near-empty page means you overflowed - trim a `reading_note`.
