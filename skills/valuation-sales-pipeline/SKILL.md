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
  `catalog-value-estimator` skill) to `lead.json`. Don't infer "dormant" from a `$0` row in the
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

- **Pull catalog data from the Recoup API, never the `/valuation` page.** `scripts/fetch_catalog.py`
  hits the same public endpoints the marketing tool uses (`references/recoup-valuation-api.md`) and
  returns album art + streams as structured data. Don't scrape or screenshot the marketing UI — it's
  slower, lossy, and can show a misleading mid-measurement snapshot.
- **Measurements are eventually consistent.** A single read can be partial — some releases return 0
  while their measurement job is still running (we've seen the same artist read back as 0 dormant on
  one call and 13 dormant minutes later). Re-read until counts stabilize before trusting them, and
  **never infer a "dormant" catalog from a transient $0** — that's a measurement-timing artifact, not
  a fact about the catalog.
- **PII / privacy.** Leads are real people. Keep names, emails, and account IDs inside the
  CRM; the bundled `fixtures/` use spoofed data only. Never paste a lead's PII into shared
  docs or external services.
- **Define "Won" precisely** as a live Stripe Pro subscription — not a reply or a call.
- **Relationship drives capacity to pay.** A $300k catalog implies only ~$24k–$36k/yr of
  net label share, so a single catalog rarely justifies a large retainer alone — convert
  to Pro and/or a managed growth+recovery engagement, or pursue the strongest as a pilot.
- Attio list/option IDs are workspace-specific; discover them at runtime (see the
  reference) rather than hardcoding.

## Lessons from live runs (ICEBOX · Chilled Cat · Eurotripp)

Hard-won notes from real leads — read these before the next run.

- **Auth: the key and the token cover different routes.** A hex `RECOUP_API_KEY` (`x-api-key`)
  authorizes `/api/spotify/*` but **fails on `/api/research/*`** — the per-album measurements and the
  estimator need a **Bearer access token** (`RECOUP_ACCESS_TOKEN`, e.g. a Privy session JWT), which
  **expires in ~1 hour**. A bad/expired token makes `fetch_catalog.py` read **0 streams across the
  whole catalog** (it now warns loudly instead of emitting a silent empty catalog). If everything is
  0, it's auth/expiry — not a dormant catalog. Get a fresh token and re-run.
- **A free run can exhaust credits mid-valuation → the tool's figure is computed on a *partial*
  catalog and undercounts.** Chilled Cat was down to 3 of 333 credits (timestamped at the valuation
  minute); the tool measured only ~27% of the catalog (~50M of ~186M streams) and showed ~$290K when
  the full catalog scales to ~$1.08M. **Check the lead's remaining credits** (see
  `references/recoup-valuation-api.md` → "Spotting a truncated free run"); if near-zero at valuation
  time, re-measure the full catalog and reframe outreach as *"we finished your interrupted run"*
  (a strong, honest hook — pair it with a credit top-up gift).
- **Measure the whole catalog — page past 50.** `fetch_catalog.py` now pages all albums; lo-fi /
  compilation brands routinely have 100+ releases (Chilled Cat = 126 releases / 349 tracks).
- **Gross streams ≠ owned value — read it honestly:**
  - *Collaborations / compilations* (Chilled Cat's "Vibes" releases are each Chilled Cat × a
    different producer): the owner holds only a **split** of each track, so realizable value is below
    the gross. Say so, and point to a statement to pin the splits.
  - *Cover songs* (Eurotripp's "Where's Your Head At" = ~95% of streams, a Basement Jaxx cover): the
    artist owns the **master, not the publishing**. Lead with master royalties + neighboring rights
    (SoundExchange) + Content ID, not catalog publishing.
- **Dedup releases for display.** A single that also appears on an album/compilation double-counts at
  the release level (Eurotripp's mixtape re-bundles its singles). Dedup by track id for lifetime
  totals (the script does), and curate the displayed release list so one recording isn't shown twice.
- **The dollar model is trailing-12-month-driven and needs history.** The `catalog-value-estimator`
  prices on TTM streams via snapshot deltas; a brand-new lead with a single capture date has **no
  trailing window → TTM 0 → $0**. You can't recompute a rigorous value same-day. Either scale the
  marketing tool's own per-stream basis for that artist to the full catalog (what we did for Chilled
  Cat), or start a measurement window and re-run in ~4 weeks for a fully-modeled figure.
- **Pre-cache album art before rendering.** Downloading 100+ covers inline gets `i.scdn.co`
  throttled and `render_valuation_pdf.py` silently drops the failed images. Pre-fetch covers to local
  files (retries + a small delay) and point the lead JSON `image` fields at `file://` paths.
- **Keep page-2 reading concise.** Long reading sections push "How this is calculated" + the footer
  onto a near-empty extra page (cubic flagged this on the PR; we hit it live). Keep reading notes
  tight so page 2 holds the whole narrative; the bundled render script's fixed text + spacers are
  already trimmed for this.
- **No em dashes in outbound copy.** The render script and `templates/outreach-email.md` use plain
  hyphens — em/en dashes read as AI-generated to recipients. Keep it that way in lead JSON
  `reading_notes` and any drafted email.
