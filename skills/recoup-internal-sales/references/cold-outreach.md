# Cold outreach — from Exa to a sent email

The one motion in this skill that does not start in our own database. Every one of the
eight sweep pulls needs the person to already be a user; this reference is how to hunt
when the funnel is cold. First run 2026-09-06 (Hopeless Records): $1.27 of Exa spend, 8
people, 3 verified emails, one email sent the same afternoon.

The whole run, in order:

1. **Exa Agent run** — find people who match the ICP, with a candidate email each.
2. **Verify every email ourselves** — Exa's provenance is unreliable (see step 2).
3. **Check they are not already ours** — Attio and Privy, before any research.
4. **Research the person and the business** — what changed for them recently.
5. **Position across ALL our services** — not just the valuation subscription.
6. **Earn one fact** — run a real valuation from our account so the email opens with a number.
7. **Draft short, one link, unslop** — and hand it to the operator.
8. **Close out** — sent file, Attio (Agency Leads), follow-up task.

## 1. Find people with the Exa Agent API

Exa is already in the product: `POST /api/research/people` on the Recoup API wraps Exa
`/search` with `category: "people"` ($0.05 a call, returns LinkedIn profiles and bios, **no
email**). For outreach use Exa directly with the same key (`EXA_API_KEY` on the api Vercel
project; one variable shared across dev/preview/prod, so `api/.env.local` has it).

- **Websets is gated to Exa Pro** — our team key gets `401 Your team does not have access
  to the API. Upgrade to a Pro plan`. Do not build on it.
- **The Agent API works on our key** and does search + email lookup in one async run,
  metered: agent compute $0.10/ACU, search $0.005, **email $0.02 each**, phone $0.07.
- `budget.maxCostDollars` is only accepted with a metered effort (`auto`, not `low`/
  `medium`); the request 400s otherwise.

```bash
K=$(grep -h '^EXA_API_KEY' api/.env.local | cut -d= -f2- | tr -d '"')
curl -s -X POST https://api.exa.ai/agent/runs -H "x-api-key: $K" -H 'Content-Type: application/json' -d '{
  "query": "Find 8 people in the United States who own or run an independent record label or artist-management company with a catalog of released music on Spotify (5+ years of releases, 3+ artists). Exclude major labels and their subsidiaries and large distributors. For each person find their work email, LinkedIn URL, company name and website, roster size, and the label'"'"'s most streamed artist.",
  "effort": "auto",
  "budget": { "maxCostDollars": 3 },
  "systemPrompt": "Prefer the label website, LinkedIn, Bandcamp and press interviews. Only return an email you found on a public source or that the email tool verified; never guess a pattern; return null instead. One person per company.",
  "outputSchema": { "type": "object", "required": ["people"], "properties": { "people": { "type": "array", "maxItems": 8, "items": { "type": "object",
    "required": ["full_name","title","company_name","company_website","email","why_fit"],
    "properties": {
      "full_name": {"type":"string"}, "title": {"type":"string"}, "company_name": {"type":"string"},
      "company_website": {"type":"string"}, "linkedin_url": {"type":"string"},
      "email": {"type":"string"}, "email_source": {"type":"string","description":"URL where found, or enrichment"},
      "roster_size": {"type":"integer"}, "top_artist": {"type":"string"}, "location": {"type":"string"},
      "why_fit": {"type":"string","description":"20 words or less: why catalog valuation and royalty tracking matter to them"}
    }}}}}
}'
# poll GET https://api.exa.ai/agent/runs/{id} until status != running; people are in .output.structured.people
```

Write the ICP into the query, not the schema: geography, label type, catalog age, roster
size, exclusions. Ask for `why_fit` so the model has to argue relevance per person; it is a
cheap first qualifier. Save the raw run JSON next to the lead list.

## 2. Verify every email yourself

**Exa's `email_source` was wrong for every sourced claim in the first run**: four addresses
were cited to bio pages that did not contain them. Treat every Exa email as a pattern guess
until one of these passes:

| Check | How | Reads as |
| --- | --- | --- |
| Published | `curl` the label site, `/contact`, `/about`; grep for `[a-z0-9._%+-]+@domain` | strongest: they chose to publish it |
| Mailbox exists | SMTP `RCPT TO` on the domain's MX (port 25 works from the dev machine), then `RCPT TO` a random address on the same domain | `250` + random `550` = verified; `250` + random `250` = catch-all, unverified |
| Catch-all fallback | run through FullEnrich or Anymail Finder (both charge only on a verified hit) | use before sending to any catch-all domain |

Most indie labels are on Google Workspace, and about half are catch-all. Report the status
next to every address in the lead list; a catch-all address is a maybe, not a contact.

## 3. Not already ours

Before researching anyone, two read-only lookups per email:

- **Attio** — `POST /v2/objects/people/records/query` with an `email_addresses.email_address`
  filter. A hit means there is history; read the notes and list entries before writing a word.
  Note the Gmail sync creates the person the moment the operator sends, so a record created
  minutes ago with no notes is the send itself, not prior contact.
- **Privy** — `POST https://auth.privy.io/api/v1/users/email/address` (read-only). A user
  means this is a warm lead, not cold; route to the dossier in SKILL.md instead.

Never use `POST /api/accounts` to check existence: it creates the account and emails them.

## 4. Research the person and the business

Ten minutes, three questions, sources named in the draft file:

- **What changed for them in the last 12 months?** An acquisition, a new imprint, a
  distribution switch, an anniversary reissue, a board seat. This is the hook; a cold email
  with no recent event is a brochure. (Hopeless: acquired the Fat Wreck Chords catalog
  2025-07-17; Posen elected A2IM Treasurer and to the Merlin board in 2026.)
- **How do they say they make money?** Exec profiles and podcasts: deal structures, D2C vs
  DSP emphasis, artist-development language. Quote them back to themselves, sparingly.
- **What is the biggest catalog they own that we can measure?** Pick the artist whose whole
  catalog sits on their label (not one shared with another label), so the number is theirs.

## 5. Position across all our services

**The default pull toward the valuation subscription is a bias, not a strategy.** A label
with a 20-artist roster does not notice a $300/mo product. Decide the revenue line from the
size of the business before drafting:

| Business | Line | What the email offers |
| --- | --- | --- |
| Solo artist, manager with 1–3 acts | Product (Valuation Leads) | the number, then Pro: weekly tracking, tasks |
| Indie label, 5+ artists, catalog 5+ years | **Agency** (Agency Leads) | release audit that re-runs weekly, $10 catalog videos, advisory; the number is the proof of work |
| Label that just acquired or merged a catalog | Agency, lead with the audit | per-catalog baseline to track the integration against |

Pick **one or two** services that the measured data points at. The 260-song, 29-year
Lagwagon catalog with 16% of plays in one song points at the long tail: an audit of
registrations, metadata and DSP presence, and a video for every catalog song. It does not
point at a subscription. Advisory is held for the reply; a cold email that lists the whole
menu reads as a sequence.

Price only from a written offer. If the workspace has no rate card for a service, say so in
the draft file and price from what the operator said (Zac precedent: audit milestone $1,200).

## 6. Earn one fact

Run a real valuation from **our** account before drafting, so the first line is a number
the reader can check:

```bash
curl -s -X POST https://api.recoupable.dev/api/valuation -H "Authorization: Bearer $RECOUP_API_KEY" \
  -H 'Content-Type: application/json' -d '{"spotify_artist_id":"<id from /api/spotify/search>"}'
# → catalog id + band; then GET /api/catalogs/{id}/measurements for total_streams,
#   catalog_age_years and the top songs (value = plays); GET /api/artists for the artist id
```

The link goes to `https://chat.recoupable.dev/artists/{artist_account_id}` — verify it
renders (it redirects to app.recoupable.dev; that is normal). The `/catalogs/{id}` page
404s for a non-owner, so never link it. Their account is never written to.

Present the number the house way: one precise dollar figure flat in the first line,
"asset value at a 10 to 16x multiple on sustainable net label share, not a bid" after it,
and for a catalog older than ~3 years say it averages history flat so trailing-twelve-months
will read differently. Never soften the first line with a range.

## 7. Draft: short, one link, unslop

- **2 to 4 sentences plus "Let me know how I can help."** Sentence one is the number and
  the concentration fact. Sentence two is what we do for businesses like theirs, tied to the
  fact. Sentence three is one small advancement we will do ("tell me which artist and I will
  run the audit this week"). Offers are things we do, never instructions to the reader.
- **Exactly one link, deep** — the artist page carrying the number. No second link, no
  signature-only link.
- **Run `unslop` on the draft** and grep the body for `—` before presenting it. No em dashes,
  no "not just X but Y", no puffery, no meta-framing ("quick note from a human").
- Draft file per SKILL.md's lead workspace: `workspace/sales/<lead>/emails/drafts/
  YYYY-MM-DD-slug.md` with the research, the valuation ids, the email, and the post-send
  checklist and reply playbook. The operator sends.

## 8. Close out

Same send loop as any other send: diff the sent copy against the draft (the operator will
change things; record the commitments as sent), write `emails/sent/…`, `EMAILS.md`, then in
Attio create the person if the Gmail sync did not, the **Agency Leads** entry (`stage` New,
`buyer_or_referrer`, `project_type`, `owner`; leave `est_project_value` empty), the sent-log
note naming the local file and the reply playbook, and a dated follow-up task written as a
runbook. A cold lead never goes on Valuation Leads unless they ran a valuation themselves.

## What the first run cost and returned

| Step | Cost | Result |
| --- | --- | --- |
| Exa Agent run (auto, $3 cap) | $1.27 (9 emails, 28 searches) | 8 people, 8 candidate emails |
| Verification | $0 (SMTP + curl) | 3 verified, 1 published-on-catch-all, 4 catch-all unverified |
| Recoup valuation (our credits) | one run | Lagwagon $372,110, 260 songs, 265.7M streams |
| Email | operator sent same day | Hopeless Records → Agency Leads, follow-up 5 days out |
