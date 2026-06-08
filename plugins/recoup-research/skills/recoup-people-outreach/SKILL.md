---
name: recoup-people-outreach
description: Industry people search, contact enrichment, outreach draft generation, and CRM enrichment via the Recoup research API. Use when asked to find managers, A&R reps, press contacts, industry people, or to draft outreach messages. Triggers on "find the manager for", "A&R at [label]", "who manages [artist]", "draft outreach", "industry contacts", "people search", "find press contacts", "CRM enrichment".
---

# People & Outreach

Industry people search, contact enrichment, and outreach draft generation
through the Recoup research API. Find the right people and draft the pitch.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Find [role] at [company]"** → People search + enrich
- **"Who manages [artist]?"** → People search for artist's team
- **"Draft outreach for [target]"** → Research target → draft pitch
- **"Enrich this contact"** → Structured enrichment
- **"Build an outreach list"** → Fan-out: people search → enrich each → rank

## People Search

```bash
# Search for industry people — returns multi-source profiles
curl -s -X POST "$RECOUP_API/research/people" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"A&R reps at Atlantic Records hip-hop","num_results":15}'
```

## Contact Enrichment

Pull structured data from web sources for a specific person:

```bash
# Extract from specific URLs
curl -s -X POST "$RECOUP_API/research/extract" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://linkedin.com/in/...","https://example.com/team"],"objective":"role, tenure, recent signings"}'

# Enrich into structured form for CRM
curl -s -X POST "$RECOUP_API/research/enrich" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"Jane Doe A&R at Atlantic Records","schema":{"type":"object","properties":{"title":{"type":"string"},"recent_signings":{"type":"array","items":{"type":"string"}},"contact":{"type":"string"}}},"processor":"core"}'
```

## Outreach Workflow

End-to-end: research → find contacts → draft outreach.

```bash
# 1. Research the artist (full sweep — use recoup-artist-research skill)
# Get: cities, listeners, playlist reach, competitive position

# 2. Find the target contact
curl -s -X POST "$RECOUP_API/research/people" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"playlist curator indie pop Spotify","num_results":10}'

# 3. Enrich promising contacts
curl -s -X POST "$RECOUP_API/research/enrich" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"{contact_name} {role}","schema":{"type":"object","properties":{"name":{"type":"string"},"role":{"type":"string"},"company":{"type":"string"},"recent_work":{"type":"array","items":{"type":"string"}}}}}'

# 4. Draft personalized outreach (LLM synthesis — no tool call)
```

## Draft rules

When drafting outreach:

1. **Reference specific data** — don't write "love your music." Write "Your
   track has 450K playlist reach across 12 editorials, with a geographic
   concentration in São Paulo that matches our roster's expansion target."
2. **Draft, don't execute.** Present the draft for the user to send. This skill
   does NOT send emails, DMs, or contact anyone.
3. **Include the angle.** Every outreach needs a clear "why you, why now" based
   on the research data.
4. **Keep it short.** Industry people get 100+ pitches. 3-4 sentences max for
   cold outreach.

## CRM Enrichment Pattern

For bulk contact enrichment (e.g., enriching an Attio or HubSpot list):

```bash
# For each contact:
curl -s -X POST "$RECOUP_API/research/enrich" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"{name} {company}","schema":{"type":"object","properties":{"title":{"type":"string"},"company":{"type":"string"},"location":{"type":"string"},"recent_activity":{"type":"string"},"linkedin_url":{"type":"string"}}}}'
```

## Critical gotchas

- **`/research/enrich` schemas must include `"type":"object"` at the top level.**
- **`/research/enrich` takes 60–90s per call.** Don't fan out across 50 contacts
  without batching expectations.
- **`/research/people` returns multi-source profiles.** Results may include
  LinkedIn, company pages, press mentions. Quality varies by person's public
  footprint.
- **`/research/extract` objective field guides extraction.** Be specific about
  what you want.

## Output format

Produce a ranked outreach list:

| Contact | Role | Company | Recent Work | Angle | Draft |
|---------|------|---------|-------------|-------|-------|
| Jane Doe | A&R | Atlantic | Signed 3 hip-hop acts in 2025 | Genre fit + growth velocity | "Hi Jane, ..." |

## References

- **`references/endpoints.md`** — people, enrich, extract endpoints
- **`references/workflows.md`** — Workflow 11 (People Outreach), Example A (Peer Collab Outreach)
