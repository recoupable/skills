---
name: recoup-catalog-register-catalog
description: "Prepare and carry out authorized music-rights registrations, ordinary claims on existing records, amendments, recording-work matches and registry or administrator transfers through verified provider routes. Use for 'register these works', 'claim my share of this existing work', 'amend my registration' or 'match this recording to my composition'. Substantive contested rights and held-payment disputes belong to claim resolution."
---

# Register a catalog

Take one documented work or a batch from the requested operation through the
highest evidenced outcome. A prepared package, submission receipt, acknowledgment,
acceptance and verified external record are distinct results.

Read `references/catalog-contracts.md`, then the requested mode in
`references/registration-modes.md`. Use `references/provider-readiness.md` before
claiming that a particular provider payload or transport is supported.

## Scope the operation

1. Identify the represented party, role, target provider/account, work or recording,
   right, territory, effective dates and requested operation. No prior full audit,
   artist profile, recording or ISWC is required to prepare a composition operation.
2. Establish the actual interest and mandate from source evidence. Software access
   is not rights authority; membership is not evidence of a particular share.
   Route through the administrator when its mandate covers the requested collection.
   Preserve retained rights and collection tails.
3. Search existing records using identifiers and corroborating titles/parties.
   Distinguish an ordinary claim on an existing record from creation of a new work.
   Leave ambiguous namesakes unresolved; do not create a duplicate to avoid matching.
4. Choose the supported mode: readiness, new registration, existing-interest claim,
   amendment, recording-work match, registry/admin transfer, or eligible identifier
   assignment/repair. Copyright registration, supplementary correction and transfer
   recordation require distinct current procedures, documents and authority.

## Prepare a concrete package

5. Verify the provider's current operation-specific rules and available route using
   `references/provider-readiness.md`. Record schema/version, official sources,
   account role, required documents, share basis, submission route, costs, disclosure
   recipients, expected receipt and readback route. Do not infer a write API from
   public search, a login, or support for a file standard.
6. Assemble `templates/registration-packet.md` and a per-item
   `templates/submission-manifest.csv`. Keep the exact before/after payload,
   source versions, authority and dependencies reviewable. If only preparation is
   supported, deliver the real fields/files and explicit remaining user/provider
   step. An unresearched provider gets an evidence packet with unresolved rule and
   schema questions; label it unvalidated for filing.
7. Validate identity, field format, required terms/documents, applicable share basis,
   mandate coverage and duplicate risk. Missing authentic consent or a disputed
   interest blocks the affected action. Do not generate a signature, infer approval
   from silence or silently change a party's interest to satisfy a total.

## Submit, resolve routine errors and verify

8. Use existing explicit user authority when it covers this provider, operation,
   party, payload and consequential disclosure/fee. Complete the package before
   requesting any genuinely missing authority. A readiness/audit request alone
   authorizes preparation, not external filing. Human attestation steps stay human.
9. Record the exact submitted version, attempt key and provider receipt per item.
   If the outcome is uncertain, inspect the provider's record/receipt before retrying;
   an interrupted session must not create duplicate registrations or claims.
10. Repair routine required-field, schema or transport rejection within the same
    operation, preserving the failed attempt and checking that authority still covers
    the changed payload. Substantive competing title, denied remedy or unresolved
    hold becomes a separate resolution handoff; do not repeatedly resubmit it.
11. Read back the accepted record and effective dates where accessible. Preserve raw
    provider status plus the normalized state: pending, partial, rejected, superseded
    and rematched items remain visible. Verify source release separately from target
    acceptance on transfers. Acceptance without record access is acceptance with
    verification pending, not observed correction.

## Deliver and continue

Return the packet, validated fields and unresolved requirements, submission manifest,
receipts/errors, record readback and remaining actions by item. The report should
state exactly which service operations reached preparation, submission, acceptance
or verification. Do not promise resulting income or close historic accounting gaps.

For a transfer use `templates/registration-transition.csv` and the transfer mode
reference. Changes to ownership, administration, collection, distribution and internal
storage are separate operations. Only execute the requested stages.

Scripts ship alongside this skill. `python3 scripts/catalog-case.py --help` describes
case persistence; use `status --file CASE_FILE` before resuming and record formats in
`references/catalog-contracts.md`. Save actions, attempts and outcomes separately.
`fixtures/evaluation-cases.json` includes single-work, ordinary-claim, rejected-field,
partial-batch, changed-authority and transfer examples; fixtures prove no live filing.

For a named provider, read `references/catalog-providers/index.md` and only its
applicable family/profile. The dated registry separates documented preparation
from implemented transports and live verification; refresh current account rules
before claiming provider validation or executing an operation.

For local `mlc-new-work`, `mlc-transfer`, `mlc-amend-work`, `mlc-member-match` or
`mlc-songwriter-match` evidence preparation, read `references/local-preparation.md`
and use `scripts/prepare-provider-packet.py` with an existing case action and explicit
required-input evidence mapping. The result is a bound preparation artifact, not an
MLC form/CWR file or verified external preflight. Missing inputs remain blocked;
complete local mappings remain externally unverified. No case state is changed.
