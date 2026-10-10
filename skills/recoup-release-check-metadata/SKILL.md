---
name: recoup-release-check-metadata
description: "Compare a release's titles, artist and contributor credits, identifiers, dates and track order across distributor exports, supplied correction receipts and available provider listings. Use for \"check my release metadata\", \"did these credit corrections go through\", or \"compare Spotify with this distributor export\". Returns exact discrepancies and correction status; does not submit changes to distributors."
---

# Check my release metadata

Read `references/music-business-records.md` before starting; it defines supported
file-review and hosted-save routes, source handling and completion checks.

## Result

Show precisely what disagrees, where it appears and what the user can do to resolve
it. Compare supplied source versions; a correction request is not proof of delivery.

## Workflow

1. Establish the exact release/edition and recordings being checked using provider
   IDs, UPC and ISRC where available. Identify compared documents and their dates.
   Do not compare a remix, reissue or namesake as if it were the same release.
2. Read each source's available fields and full page/row coverage. A Spotify listing
   may omit songwriter/producer credits; absence of that field is missing coverage,
   not a confirmed credit error. Preserve the original strings before normalizing.
3. Align release fields and track slots, then compare title/version, display artists,
   contributor roles, ISRC/UPC, release date precision, explicit status, disc and track
   order. Ignore harmless formatting only when it cannot change identity or meaning;
   keep aliases, transliterations and substantive role changes visible.
4. Build a discrepancy table: field/track, value in each named source, exact locator,
   difference, user impact, and proposed resolution. Identify duplicates, conflicting
   IDs and incomplete pages separately. Never choose a “correct” value solely because
   one source is newer; use an authorized source-of-truth decision or leave unresolved.
5. For correction receipts, distinguish requested, acknowledged by distributor,
   reported completed, and observed in a dated destination listing. Report which
   destination and fields were checked; one platform's update is not all-DSP proof.
6. If recording a hosted metadata review, read the current case and fingerprint,
   check coverage and source changes, and obtain the user's actual review decision.
   Use the discovered metadata-review contract; retain/read its receipt. A
   discrepancy report by itself is not user acceptance or a distribution approval.

## Handoff

Return a short verdict followed by the discrepancy table and correction checklist.
State “no differences in the compared fields” only within the inspected scope; do
not say “all credits verified” when a provider doesn't expose them. Prepare a correction
request only if requested; do not submit edits or contact the distributor in this skill.

Example: an export says writer “A. Example”, a split sheet says “Alex Example”, and
Spotify exposes neither: flag the name match for review, not a missing Spotify writer.
