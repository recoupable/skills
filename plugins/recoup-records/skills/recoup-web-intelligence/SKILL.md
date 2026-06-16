---
name: recoup-web-intelligence
description: General web + entity intelligence — search the open web, run deep cited research, extract content from URLs, and enrich ANY entity (artist, label, manager, songwriter, venue, brand, company) into structured facts. Use when the user says "search the web", "deep research [topic]", "what does this page/URL say", "enrich [entity]", "look up [label/manager/venue]", "background on [person/company]", "find narrative context", or when structured artist data is thin and you need to fall back to the open web. Not artist-only and not metrics — for structured artist streaming/audience numbers use recoup-artist-research; this is the open-web and any-entity layer, and the graceful-degradation fallback when the structured endpoints come up empty.
---

# Web Intelligence

The platform's **general-purpose research layer**: anything that lives on the open
web or is *any* entity (not just the artist roster). Four capabilities behind one
door, plus the **graceful-degradation fallback** when the structured
(Songstats-backed) endpoints return empty.

This is deliberately broad: it enriches **labels, managers, songwriters, venues,
brands, companies, and people** — not only artists — and answers arbitrary-topic
research, which is why it is its own skill and not a mode of `recoup-artist-research`
(that one is structured artist metrics; this is the open web + any entity).

The job is never "dump what the web returned." It is **find → verify the
citations → distill to a dossier.** Unverified research presented as fact is the
failure mode this skill exists to prevent.

```bash
export RECOUP_API_KEY="recoup_sk_..."
export RECOUP_API="https://api.recoupable.com/api"
```

## Phase 1 — Pick the right tool (a cost/latency decision, not a reflex)

The four tools differ by an order of magnitude in time and credits. Choose
deliberately; don't reach for `deep` when `web` answers it.

| Need | Tool | Latency / cost | Endpoint |
|---|---|---|---|
| Quick ranked answers on a topic | **web** | ~seconds, cheap | `POST /research/web` |
| A cited narrative report on a question | **deep** | ~2+ min, **expensive** | `POST /research/deep` |
| Read specific page(s) you already have | **extract** | seconds–tens | `POST /research/extract` |
| Structured facts about a named entity | **enrich** | ~60–90s | `POST /research/enrich` |

**Decision brief** when the user's ask could go two ways and the cost differs
materially (e.g. "tell me about this label" → quick `web` digest vs an expensive
`deep` report):

```
D1 — <quick web digest, or full deep report?>
ELI10: web is seconds and cheap; deep is 2+ minutes and burns credits for a cited report.
Recommendation: <web> because <the ask reads as a quick lookup, not a dossier>
A) web digest (recommended)  ✅ seconds, low credit  ❌ shallower, fewer citations
B) deep report              ✅ cited narrative      ❌ 2+ min, expensive
Net: spend deep's cost only when the user needs a defensible, cited writeup.
```

Otherwise pick the cheapest tool that satisfies the ask and note it.

## Phase 2 — Run the tool

### web — quick ranked results
```bash
curl -s -X POST "$RECOUP_API/research/web" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"emerging indie R&B labels 2026","max_results":10,"country":"US"}'
```
Body: `query` (required), `max_results` (1–20, default 10), `country` (2-letter
ISO, optional). Returns `{ results:[{title,url,snippet,date,last_updated}],
formatted }` — `formatted` is a ready-to-read markdown digest.

### deep — comprehensive cited report (~2+ min; set client timeout ≥3 min)
```bash
curl -s -X POST "$RECOUP_API/research/deep" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"how did [label] build its catalog and who runs A&R"}'
```
Body: `query` only. Returns `{ content (markdown), citations:[url,...] }`.

### extract — readable content from specific URLs
```bash
curl -s -X POST "$RECOUP_API/research/extract" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com/article"],"objective":"key facts, quotes, data points","full_content":false}'
```
Body: `urls` (1–10), `objective` (≤3000 chars — **specific objectives = specific
results**), `full_content` (default `false`). Returns
`{ results:[{url,title,publish_date,excerpts[],full_content}], errors[] }`.

### enrich — structured facts about any entity (~60–90s)
```bash
curl -s -X POST "$RECOUP_API/research/enrich" -H "x-api-key: $RECOUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":"<entity — artist, label, manager, songwriter, venue, brand>",
       "schema":{"type":"object","properties":{
         "founded":{"type":"string"},"principals":{"type":"array","items":{"type":"string"}},
         "notable_works":{"type":"array","items":{"type":"string"}},
         "recent_news":{"type":"array","items":{"type":"string"}}}},
       "processor":"core"}'
```
Body: `input` (required), `schema` (required — **must include `"type":"object"`
at the top level**), `processor` (`base` fast / `core` balanced / `ultra`
comprehensive). Returns `{ output:{...your schema...}, citations:[{url,title,field}] }`.

## Phase 3 — Verify the citations (the loop; do not skip)

Research output is plausible-sounding by construction — that's exactly when it's
dangerous. Before presenting `deep` or `enrich` results:

- [ ] **Every material claim is cited.** Map each headline fact to a citation in
      the response. An uncited claim is a **lead to verify**, not a fact to state.
- [ ] **The citation actually supports the claim** — if a fact is load-bearing
      (a date, a number, an ownership claim), the cited source must say it. Spot-
      check with `extract` on the citation URL when the stakes are high.
- [ ] **Sources are real and reachable** — drop dead/placeholder URLs; never
      present a citation you couldn't resolve.
- [ ] **Flag conflicts** — if two sources disagree, say so rather than picking one
      silently.

Anything that fails → label it explicitly as unverified, or re-run `extract` to
confirm. Never launder an uncited model claim into a stated fact.

## Phase 4 — Distill to a dossier (diarization, not a scrape)

The deliverable is **one page of distilled judgment**, the way an analyst writes
an intelligence brief — not raw JSON and not a link dump. For an entity enrichment:

- Lead with **what this entity is and why it matters** to the user's task (the
  signal), not an alphabetical fact list.
- Separate **established fact (cited)** from **inference** and from **open
  questions**.
- Surface the **"so what"** — the one or two things that change a decision (who to
  contact, what the entity actually does vs claims, the recent move that matters).
- Keep raw JSON / full results in an appendix or the workspace file, not the lead.

Persist into the workspace by **primary subject** when one exists
(`artists/{slug}/research/…`, or an entity file for a label/manager), commit
`{what}: {why}`; otherwise return the dossier in chat.

## Graceful Degradation Chain (the fallback role)

When the structured endpoints come up empty — `GET /research?q=...` returns
`{results:[]}`, `/research/lookup?url=...` is non-200, `/research/profile` is thin
with no `/metrics` `stats`, or any endpoint returns `501` — fall through:

1. **`/research/web`** — ranked results (~seconds)
2. **`/research/enrich`** — structured facts (~60–90s)
3. **`/research/deep`** — cited narrative (~2+ min)

For very emerging artists Songstats may have no data; web + enrich + deep is the
full alternative path. (Still run Phase 3–4 on whatever you get back.)

## Critical gotchas

- **`enrich` schemas must include `"type":"object"` at the top level** — rejected
  otherwise.
- **`enrich` default `processor` is `base`** (fast); pass `core`/`ultra` for depth.
- **Latency:** `/web` & `/extract` seconds–tens; `/enrich` 60–90s; `/deep` 2+ min.
  Set client timeouts accordingly.
- **`/deep` is expensive** (time + credits) — try `/web` first; reserve `/deep`
  for when a cited narrative is actually needed.
- **`/extract` objective matters** — vague objective, vague extraction.
- **Credits:** on `{ "error": "insufficient_credits" }`, surface the `checkoutUrl`
  rather than silently dropping a section.

## Guardrails

- **Not artist metrics.** Structured streaming/audience/playlist numbers →
  `recoup-artist-research`. This skill is the open web + any-entity layer.
- **Verify before you state.** Uncited → unverified. Run Phase 3 every time.
- **Dossier, not a dump.** Distilled judgment with sourced facts beats a wall of
  results.

## References

- `references/endpoints.md` — POST endpoint details.
- `references/workflows.md` — chaining rules, when NOT to chain.
