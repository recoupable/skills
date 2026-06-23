---
name: recoup-research-find-contacts
description: Find music-industry people — managers, A&R, press, label and booking contacts — and draft outreach you can send. Use for "find the manager for [artist]", "who's the A&R at [label]", "find press contacts", or "draft outreach to [person]". Drafts only; never sends. To research an artist's metrics and audience use recoup-research-artist-overview.
---

# Recoup Research — Find Contacts

Find industry people (managers, A&R, press) and draft outreach.

```bash
export RECOUP_API="https://api.recoupable.com/api"   # auth header: x-api-key: $RECOUP_API_KEY
```

## Procedure

- `POST /research/people {query, num_results}` — multi-source profiles (LinkedIn etc.).
- `POST /research/enrich {input, schema}` — structured facts (title, recent signings,
  contact); schema must include `"type":"object"`.
- `POST /research/extract {urls, objective}` — pull specific source pages.
- Fall back to `/web` + `/deep` for narrative and leads.

**Never fabricate a contact** — only surface people who appear in sourced results;
draft outreach only after the person is confirmed. Reference real specifics
(the artist, label, market, or release in play) so drafts aren't generic. Full chains in
`references/workflows.md` (People Outreach).

## Guardrails

- **Draft, don't send** — anything touching a real human is presented for the user
  to send themselves.
- **Never fabricate** a contact, email, or recent work.
- **Credits:** surface `checkoutUrl` on `insufficient_credits`.

## References

- `references/workflows.md` — people-outreach chains + CRM enrichment.
