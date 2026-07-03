---
name: recoup-research-the-web
description: Research anything on the open web — quick ranked search, deep cited narrative, read specific URLs, and enrich any entity (label, venue, brand, person) into structured facts. Use for "search the web", "deep research [topic]", "what does this URL say", "enrich [company/label/person]", or as the fallback when structured artist data is thin. Not artist-only. For metrics on a known artist use recoup-research-artist-overview.
---

# Recoup Research — The Web

General open-web research and the graceful-degradation fallback for the other
research skills. Researches any entity, not just artists.

```bash
export RECOUP_API="https://api.recoupable.dev/api"   # auth header: x-api-key: $RECOUP_API_KEY
```

## Tools

- `POST /research/web` — quick ranked results (seconds, cheap).
- `POST /research/deep` — cited narrative (2+ min, expensive).
- `POST /research/extract {urls, objective}` — read specific URLs.
- `POST /research/enrich {input, schema}` — structured facts about ANY entity
  (label, manager, venue, brand, person); schema must include `"type":"object"`.

**Verify citations** (every material claim cited; the source actually supports it;
drop dead URLs) and **distill to a sourced one-page dossier** (fact vs inference vs
open question) — not a link dump.

## Guardrails

- **Verify citations**; never present an unsupported claim as fact.
- **Latency:** `/enrich` 60–90s, `/deep` 2+ min — set timeouts ≥3 min.
- **Credits:** surface `checkoutUrl` on `insufficient_credits`.

## References

- `references/workflows.md` — web/deep research patterns + entity enrichment.
