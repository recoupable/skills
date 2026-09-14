---
name: recoup-internal-consulting-content-extraction
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Extract reusable content, insights, and knowledge-base entries from a call transcript or meeting note. Use whenever a new transcript lands in content/01-raw/ or a client's meetings/ folder, after any client/sales call, or when the user says \"extract content\", \"mine this call\", \"turn this into posts/insights\". Powers the content flywheel (\"never answer the same question twice\")."
---

# Consulting Content Extraction

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

Turn a raw transcript into compounding assets.

## When to run
Automatically after any new transcript is saved (content/01-raw/ or clients/{client}/meetings/), or on request.

## Steps
1. Read the transcript.
2. Extract and output, grouped:
   - Quotable insights shared about AI/consulting
   - Useful analogies or frameworks used
   - Industry-specific examples given
   - Questions that revealed deep insight
   - Moments that reframed the client's thinking
3. Format each as a candidate LinkedIn post or blog topic.
4. Deposit results as **atomic signals** in `signals/` — one file per item, each with frontmatter (schema
   + lifecycle in `signals/AGENTS.md`): a **traversable `source`** (the transcript path + line/quote you
   pulled it from), `type`, `hook`, `intent`, `formats`, `status: new`. This is the owned write-step for
   the reservoir:
   - Reusable explanation / durable POV → a `type: insight` signal (`status: evergreen`).
   - Post/blog candidate → a `type: content-idea` signal (`status: new`).
   - Recurring question already answered before → `knowledge/faqs/` (reference knowledge, not a signal).
5. If the same topic now appears 2+ times, flag it as a strong content piece.
