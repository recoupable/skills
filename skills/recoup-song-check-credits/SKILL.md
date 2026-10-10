---
name: recoup-song-check-credits
description: "Compare songwriter, producer and performer credits for a specific song across supplied split sheets, distributor records and available registry sources. Use for \"check my song credits\", \"who wrote this song\", or \"do these splits match the credits\". Separates recording roles from composition shares and returns cited conflicts or missing details; does not register rights or infer ownership from a credit."
---

# Check my song credits

Read `references/music-business-records.md` before starting; it defines supported
file-review and hosted-save routes, source handling and completion checks.

## Result

Show who is credited, for which role, on which recording or composition, and where
names, roles or explicitly supplied shares disagree.

## Workflow

1. Identify the recording/version and underlying composition separately. Use supplied
   ISRC, ISWC, registry work IDs and party identifiers where available; title alone is
   insufficient. A remix or cover can change recording credits without changing the
   underlying work; an unresolved composition link remains unresolved.
2. Read authorized split sheets, credit files and distributor records. Consult a
   requested registry only through supported access and record source/date/locator.
   A registry entry is a sourced claim, not independently proven ownership. Do not
   run paid enrichment or access another company's private repertoire implicitly.
3. Build two tables: recording contributors (performer, producer and other supplied
   roles) and composition contributors (writers/publishers and explicit interests).
   Preserve names and identifiers as supplied; aliases and namesakes need review.
4. Label each percentage's basis, such as writer share, publisher share, ownership
   or distributor payout. Add percentages only within the same work, right, basis,
   territory, period and compatible denominator. Different society conventions can
   use different totals; do not force every split to 100 or invent a balancing share.
5. List concrete disagreements and missing coverage with exact references: omitted
   writer, conflicting role, unmatched party ID, incompatible split basis or absent
   signed split sheet. Distinguish absence in a source from proof the person has no
   contribution, and identify what document or confirmation would resolve each item.
6. Save through a supported scoped credits/review operation if available and read
   back the result; otherwise return a dated private comparison. Preserve proposed
   matches separately from accepted decisions; do not mutate global identities.

## Handoff

Return the two tables and a short correction/confirmation list, bounded by inspected
sources. No inferred splits, ownership certification, society registration, royalty
recovery promise or external contact. A user can use the report to prepare a correction;
submission remains a separate authorized action.

Example: a producer credit and a 20% distributor payout do not establish a 20%
songwriting share; keep those relationships separate and request the actual split record.
