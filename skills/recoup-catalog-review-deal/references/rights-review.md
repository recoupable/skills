# Rights Review

Review whether the seller can transfer the rights that the valuation assumes.
Royalty income is evidence of reported payments; it is not proof of ownership.

## Workflow

1. Read the catalog assets from `normalized/canonical-catalog.csv` if present.
2. Read `normalized/rights-map.csv` if present.
3. Link each material income-generating asset to agreements, split sheets,
   registrations, assignments, or other support.
4. Check territory, term, controlled share, approval rights, reversions,
   samples, liens, side letters, and encumbrances.
5. Classify support as `supported`, `partial`, `missing`, `conflicting`, or
   `unknown`.
6. Write structured findings to `findings/findings.json`.
7. Update `findings/missing-files.md` with curative requests.

## Red flags

Read `references/red-flags.md` for severity. Prioritize:

- Income-generating works without signed support.
- Contract shares below schedule shares.
- Missing assignments.
- Unmodeled reversions.
- Sample or interpolation gaps.
- Non-one-stop sync assumptions.
- Liens, audits, disputes, or estate issues.

## Output

Return a rights memo with:

- Assets reviewed.
- Supported assets.
- Unsupported or conflicting assets.
- Critical blockers.
- Valuation treatment: include, exclude, haircut, escrow, or holdback.
- Follow-up request list.

## Guardrails

- Do not provide legal advice. Flag issues for counsel review.
- Do not infer ownership from royalties alone.
- Do not silently resolve conflicting contract terms.
