---
name: recoup-web-intelligence
description: Web research, deep research, URL extraction, and entity enrichment via the Recoup research API. Use when Chartmetric data is unavailable, when you need narrative context from the web, when enriching entities with structured facts, or when extracting content from URLs. Also the graceful degradation fallback when other research skills return empty. Triggers on "web search", "deep research", "extract from URL", "enrich", "what does this page say", or when primary research endpoints return no data.
---

# Web Intelligence

Web research, deep cited reports, URL extraction, and structured entity
enrichment through the Recoup research API. This is also the **graceful
degradation fallback** when Chartmetric endpoints return empty.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Decision tree

- **"Search the web for [topic]"** → `POST /research/web`
- **"Give me a deep report on [topic]"** → `POST /research/deep`
- **"What does this page say?"** → `POST /research/extract`
- **"Enrich [entity] with structured data"** → `POST /research/enrich`
- **Chartmetric returned empty** → Graceful Degradation chain

## Web Search

Quick ranked web results (~seconds):

```bash
curl -s -X POST "$RECOUP_API/research/web" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"emerging indie R&B artists 2026","max_results":10}'
```

## Deep Research

Comprehensive cited narrative report (~2+ min):

```bash
curl -s -X POST "$RECOUP_API/research/deep" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"why is [artist] going viral on TikTok in [country]"}'
```

**Note:** This endpoint takes 2+ minutes. Set client timeout to ≥3 min.

## URL Extraction

Extract readable content from specific URLs:

```bash
curl -s -X POST "$RECOUP_API/research/extract" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com/article","https://linkedin.com/in/person"],"objective":"key facts, quotes, and data points"}'
```

The `objective` field guides what gets extracted. Be specific.

## Entity Enrichment

Extract structured facts about any entity (~60–90s):

```bash
curl -s -X POST "$RECOUP_API/research/enrich" \
  -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "<entity name — artist, label, manager, songwriter, venue>",
    "schema": {
      "type": "object",
      "properties": {
        "founded": {"type": "string"},
        "ceo": {"type": "string"},
        "notable_artists": {"type": "array", "items": {"type": "string"}},
        "revenue_estimate": {"type": "string"},
        "recent_news": {"type": "array", "items": {"type": "string"}}
      }
    },
    "processor": "core"
  }'
```

## Graceful Degradation Chain

When Chartmetric data is unavailable (search returns empty,
`match_strength < 1`, or lookup fails), fall through:

1. **`POST /research/web`** — ranked web results (~seconds)
2. **`POST /research/enrich`** — structured facts (~60–90s)
3. **`POST /research/deep`** — cited narrative (~2+ min)

For very emerging artists, Chartmetric may not have data. Web + enrich + deep
is the full alternative path.

### When to trigger graceful degradation

- `GET /research?q=...` returns `{ results: [] }`
- Top result has `match_strength < 1`
- `/research/lookup?url=...` returns non-200
- `/research/profile` returns mostly `null` fields

## Critical gotchas

- **`/research/enrich` schemas must include `"type":"object"` at the top level.**
  Endpoint rejects schemas without it.
- **POST endpoint latency:** `/enrich` 60–90s, `/deep` 2+ min, `/web` and
  `/extract` are seconds-to-tens. Set client timeouts accordingly.
- **`/research/deep` is expensive** (time and potentially credits). Use `/web`
  first for quick answers; reserve `/deep` for when you need cited narrative.
- **`/research/extract` objective field matters.** Vague objectives = vague
  results.
- **`/research/enrich` processor options:** `core` (default) is the main
  processor. Don't change unless the docs specify alternatives.

## References

- **`references/endpoints.md`** — POST endpoint details
- **`references/workflows.md`** — chaining rules, when NOT to chain
