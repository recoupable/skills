---
name: recoup-internal-consulting-friday-review
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. The weekly content + system review ritual. Use on \"run the Friday review\", weekly cadence, or \"what should I write this week\". Good candidate to wire as a scheduled task."
---

# Consulting Friday Review

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

## Steps
1. Scan `signals/` for unused signals — the dated `<YYYY-MM-DD>-*.md` files (`status: new`; skip the meta files `AGENTS.md`/`_template.md`/`_index.md`/`_archive/`; target 15–20 candidates).
2. Detect repeated questions across the week's calls and `knowledge/` — repeats are the strongest content signal.
3. Scan published posts + `integrations/linkedin/engagement/` for winners/outliers → run
   `recoup-internal-consulting-content-recycler` (repost with a fresh hook · re-share with context · fan an outlier
   into new formats). A winner not recycled is shelf inventory.
4. Run `recoup-internal-consulting-content-extraction` on any un-processed transcripts in `content/01-raw/`.
5. Run `recoup-internal-consulting-research-miner` if the research wiki advanced since `integrations/research/_work/LAST_MINED` — harvest fresh agent/skill/compound-engineering ideas into `signals/` (delta-guarded; no-ops if nothing's new).
6. Propose the top 1–3 ideas to test (→ `recoup-internal-consulting-content-idea-generator`) or draft (→ `recoup-internal-consulting-content-drafter`).
7. Surface knowledge-base gaps (questions answered 2+ times but not yet an FAQ).
8. Report a short weekly content plan.

Source: Ch. 4 (the Friday Review).
