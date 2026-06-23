---
name: recoup-internal-funnel-valuation-pipeline
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal work the valuation funnel"). Never use for customer-facing or
  artist requests.
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

# Valuation Funnel

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
  `recoup-research-artist-overview` and `recoup-catalog-estimate-value` skills for endpoint detail.
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

- Pull the catalog + album art straight from the public APIs (no scraping):
  `python3 scripts/fetch_catalog.py --artist-id <spotifyId> --out lead.json` — fills streams,
  album art, and release counts. Add the dollar band (from the tool, or computed with the
  `recoup-catalog-estimate-value` skill) to `lead.json`. Don't infer "dormant" from a `$0` row in the
  live UI — confirm against the measurements endpoint (see `references/recoup-valuation-api.md`).
- Render the valuation PDF (headline + a top-releases breakdown with album art, an honest
  "reading your result" page, and a full-catalog appendix):
  `python3 scripts/render_valuation_pdf.py --lead lead.json --out ./out`
  (see `fixtures/example-lead.json` for the shape).
- Attach the artist's **verified socials** to the lead JSON `socials` block (Spotify, Instagram,
  TikTok, YouTube, X) so the report renders a clickable "Artist channels" line. Get them from
  `research/lookup?spotifyId=` / `research/metrics` when available; when those are Songstats-rate-
  limited (429) or fail, verify from the artist's **official release upload description or label
  page**, cross-checking the **same Spotify artist id** so you don't attach a same-name impostor.
- Draft the first email from `templates/outreach-email.md`: personal, references the
  specific artist + their number, **delivers the PDF**, gives one free specific insight
  (a playlist gap, a likely-uncollected royalty source, a concentration note), and ends
  with a low-friction CTA. Send from the rep, not a generic address.
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
  to recipients. The render script and `templates/outreach-email.md` already follow both; keep lead
  JSON `reading_notes` the same.
