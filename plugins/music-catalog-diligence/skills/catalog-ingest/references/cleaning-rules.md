# Cleaning rules

Catalog cleanup must stay auditable. The user, buyer, lawyer, or finance lead
needs to understand what changed and why.

## Before cleaning

Profile every structured file before transformation:

- Row count and column count.
- Grain: one row per what.
- Candidate primary keys.
- Date range.
- Currency.
- Null rates.
- Duplicate rows.
- Duplicate identifiers.
- Mixed data types.
- Suspicious values.
- Identifier format validity.
- Split totals.

## Issue taxonomy

Use this table format before changing data.

| Column | Issue | Count | Proposed fix | Destructive? |
| --- | --- | ---: | --- | --- |
| `Title` | Leading/trailing whitespace | 84 | Add cleaned title field with trimmed value | No |
| `ISRC` | Invalid format | 7 | Flag for review, do not infer | No |
| `Writer Split` | Totals 125% for 3 songs | 3 | Preserve source values and add conflict note | No |
| `Date` | Mixed date formats | 211 | Standardize into ISO date helper column | No |
| `Rows` | Exact duplicate rows | 12 | Ask before removal | Yes |

## Non-destructive defaults

Prefer adding cleaned helper fields over overwriting originals.

Examples:

- Keep `title_source` and create `title_clean`.
- Keep `isrc_source` and create `isrc_clean`.
- Keep `statement_amount_source` and create numeric `statement_amount`.
- Keep original currency and add converted currency only with an FX source.

Only overwrite values when the user explicitly approves or the output is a new
derived file that leaves the raw source untouched.

## Matching hierarchy

Match assets in this order:

1. Exact ISRC for recordings.
2. Exact ISWC for compositions.
3. UPC plus track number and title.
4. IPI/CAE plus title and writer set.
5. Normalized title plus artist/writer with high similarity.
6. Filename or folder inference.

Levels 1 to 3 can be high confidence when source data is clean. Levels 4 to 6
need review notes unless corroborated by another source.

## Split checks

Do not assume every split column has the same denominator.

Check:

- Writer share vs publisher share.
- Master ownership vs artist royalty rate.
- Controlled share vs total copyright ownership.
- Territory-specific share.
- Admin share vs ownership share.
- Producer points and featured artist participations.

Flag any split set that totals below 99.5% or above 100.5%, unless the source
clearly uses a different basis.

## Identifier checks

Use these as validation flags, not automatic corrections.

- ISRC: usually 12 characters, country/registrant/year/designation.
- ISWC: composition identifier, often starts with `T`.
- UPC/EAN: release identifier, often 12 or 13 digits.
- IPI/CAE: party identifiers for writers and publishers.

If an identifier looks wrong, mark it invalid and ask for support. Do not invent
or "fix" identifiers from search results unless the user explicitly asks for
enrichment and the source is recorded.

## PRO statement preservation

For PRO statements, keep detail fields that may look irrelevant during cleaning:

- Performance period.
- Payment period.
- Use type.
- Duration.
- Credits.
- Credit value.
- Bonus or premium category.
- Station, network, program, episode, or cue reference.
- Territory and society.
- Foreign exchange.
- Adjustment or retroactive payment notes.

These fields are needed later to decide whether income is sustainable.

## Cleanup report

After cleaning, write a short report with:

- Files processed.
- Rows before and after.
- Columns added.
- Destructive changes, if any.
- Unresolved conflicts.
- Fields that require user, legal, or seller confirmation.
- Confidence summary.
