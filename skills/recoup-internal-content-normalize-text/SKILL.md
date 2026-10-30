---
name: recoup-internal-content-normalize-text
description: >-
  INTERNAL — Use only when the request explicitly includes recoup-internal.
  Audit, generate, or rewrite batches of AI-generated dashboard cards, feed
  headlines, session titles, notifications, and row summaries for fast scanning.
  Establish a shared text pattern without changing the underlying facts.
  Not for standalone marketing copy, visual-layout redesign, or publishing.
---

# Normalize Text Collections

Make a collection understandable at a glance, not merely make each sentence sound
good in isolation. Work on the requested text surface; do not redesign the product
or rewrite its underlying records unless that is part of the request.

## Inputs and scope

Read the supplied collection and its available evidence. Identify the reader's
decision: finding an active task, spotting a failure, comparing feedback themes,
or choosing a story. Use the existing display format and visible text budget.
If the interface is unavailable, state an assumed budget instead of claiming
the result was visually tested.

For an audit or rewrite, existing text is sufficient to diagnose inconsistency,
but not to substantiate new claims. For generation, require source records for
the requested items. Ask only for missing information that blocks factual work;
do not search private sources or expand the corpus just to fill a template.

## Five editing principles

1. **Make the actor and action easy to parse.** Prefer straightforward active
   clauses. Omit a shared actor when it adds nothing. Let tense reflect actual
   state, not a blanket stylistic preference.
2. **Lead with the distinguishing information.** Put the action, subject, or
   status that matters to the reader near the beginning; remove repeated setup.
3. **Stabilize syntax and terminology.** Use a common pattern for comparable
   items and one label for each concept. Do not rotate synonyms for variety.
4. **Make differences informative.** Extra detail, emphasis, and length should
   reflect relevant evidence, not arbitrary generation choices.
5. **Make sentiment legible and grounded.** Choose verbs that communicate the
   evidenced praise, complaint, or neutral report. Do not exaggerate sentiment
   to fit a dashboard's theme.

## Workflow

### 1. Define the collection contract

Before rewriting, capture a small working contract:

- Item type and reader decision.
- Leading discriminator and sentence pattern.
- State-to-tense mapping, where applicable.
- Canonical terms, required fields, optional-detail rule, and length budget.
- What must survive shortening: identifiers, numbers, dates, negation,
  uncertainty, attribution, links, or a material exception.

Use one contract per genuinely different item type, not one per row. A feed of
news headlines and a list of running jobs need not share grammar. Within a
mixed-status job list, use a fixed structure but vary tense to encode status.
If leading with a status creates identical prefixes across most rows, put status
in an existing badge/column or lead with the specific action instead. Do not add
new UI components unless interface changes are authorized.

### 2. Pilot the pattern

Try the contract on a few representative items, including a long item, an
exception, and an unknown or mixed state when present. Check that the pattern
does not turn a plan into a completed result, a report into a verified fact,
or missing data into zero. If it fails, revise the contract before scaling.

For feedback themes, separate the claim, supporting example, and count. Define
the count's unit and denominator; overlapping themes are not mutually exclusive
shares. Retain a source pointer for each supporting example. Paraphrases are not
quotes. If comparable counts are unavailable, omit that comparison or mark them
unavailable; never manufacture symmetry.

### 3. Apply across the batch

Preserve item IDs, source links, order, and record coverage unless the request
also authorizes regrouping or ranking. Rewrite only display text. Do not collapse
distinct items just because their normalized labels look similar.

If processing in chunks, reuse the same contract and terminology map for every
chunk, then review the combined collection for drift. Move nonessential detail
to an existing detail field or linked source; retain qualifications that would
change the reader's decision. A meaningful exception may be longer than its
neighbors. Do not pad short items or cut essential facts to equalize lengths.

### 4. Verify the collection

- Read only each item's opening words: can a reader distinguish the entries?
- Read comparable items together: does each field carry the same kind of fact?
- Compare rewrites with sources: are numbers, state, sentiment, attribution,
  negation, and uncertainty unchanged?
- Check IDs and count: were any records lost, duplicated, or silently merged?
- Inspect the actual rendered surface when available, including narrow widths
  and truncation. Otherwise label visual fit unverified.

Audit mode returns findings and representative fixes; it does not modify files.
Rewrite/generation mode returns the requested artifact and a short QA note.
Do not publish, send notifications, or deploy merely because text is ready.

## Worked edge cases

These are synthetic examples, not Recoup records.

| Evidence | Display text | Why |
|---|---|---|
| The job is still processing a statement file. | Importing statement file | An ongoing action, not a completed import. |
| The import completed; matching has not started. | Imported statement file | Does not imply the separate matching step finished. |
| A matching job's current state is unavailable. | Matching job: status unknown | An explicit exception is more truthful than invented tense. |
| Four of 20 reviews report exports stopping; no reproduction exists. | Reviewers report export failures | Keeps the claim attributed; place 4/20 in the consistent count field. |
| Feedback praises search but criticizes export speed. | Users praise search; criticize export speed | Preserves mixed evidence instead of forcing one polarity. |

## Deliverable

Use the caller's format. For structured data, return updates keyed by original
ID and keep commentary outside the machine-readable payload. For code changes,
edit the relevant text-generation instructions or display copy in scope; do not
hardcode a single improved snapshot if the actual request concerns future output.

Briefly report the chosen contract, material exceptions, evidence gaps, and what
was verified. Never present a word-count check as proof of human readability.

## Source and adaptation

Adapted from Shreya Shankar, Full Stack Data Lab, [Five Principles for Generating
Readable AI Text in Bulk](https://fsdatalab.github.io/blog/agent-text-at-scale/),
published 2026-10-29; read 2026-10-30.
The five principles above summarize the article. The collection contract,
chunking procedure, evidence checks, and synthetic examples are Recoup workflow
adaptations. Treat the article's research discussion as motivation, not an
independently verified claim of guaranteed speed or comprehension gains.
