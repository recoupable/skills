---
name: recoup-release-manage-delivery
description: "Carry out authorized corrections to already delivered music releases, eligible UGC monetization enrollment and distributor migration/redelivery with per-destination verification. Use for 'correct this delivered producer credit', 'move these releases to a new distributor' or 'enroll my existing recordings in Content ID'. Metadata checks and internal release creation do not authorize delivery changes."
---

# Manage delivered releases

Take an explicitly requested change to an existing delivery through preparation,
supported submission and destination verification. Keep distributor acceptance,
DSP observations, UGC activation, observed claims and revenue distinct.

Read `references/catalog-contracts.md`, then the selected mode in
`references/delivery-modes.md`. This skill does not promise initial distribution of
never-delivered music or treat an internal Recoup release record as a delivered release.

## Establish the exact change

1. Identify the recording owner/authorized representative, distributor account,
   release edition, ordered tracks, stable identifiers, affected destinations and
   territories. Inspect the current delivered version and relevant assets. Resolve
   same-title releases and recordings before editing anything.
2. Choose correction, eligible UGC enrollment or distributor migration/redelivery.
   For ambiguous "transfer my catalog", distinguish rights ownership, publishing
   administration, collection mandate, distribution and internal storage before
   selecting actions. A distributor move does not itself transfer ownership.
3. Verify authority and provider-specific route for the exact operation. Discover
   available connectors/APIs, supported exchange/import or authorized portal steps.
   Verify current official rules, eligibility, required files, irreversible effects,
   fees/disclosures and expected receipts. Public platform access or ordinary channel
   OAuth does not establish Content ID partner eligibility or distribution access.

## Prepare and execute the selected mode

4. Use `templates/delivery-plan.md` and `templates/destination-manifest.csv` to make
   the before/after values, payload/assets, affected destinations and authority
   reviewable. Validate against the actual provider schema/version. An unknown or
   unsupported provider gets a preparation packet with unresolved requirements,
   not a claim of validated submission support.
5. Apply `references/delivery-modes.md` for the selected mode. Check dependent
   evidence and constraints per item; one blocked track need not block unrelated
   authorized corrections if the provider allows partial changes.
6. Execute only within the requested action scope. Existing explicit authorization
   persists for matching actions. A metadata audit or internal add-release request
   authorizes neither external corrections nor monetization enrollment. Do not bundle
   a new takedown, contract or fee into an approved correction.
7. Save payload/asset hashes, source versions, attempt key, per-item submission
   receipt and raw provider response. Inspect ambiguous attempts before retrying;
   duplicated redelivery or repeated removals can damage availability.
8. Read back the distributor state and each intended destination separately. Record
   expected and observed fields, account/URL/record ID, observation time and remaining
   differences. Propagation delays and partial outcomes remain pending by destination.

## Deliver evidence of the actual outcome

Return the exact plan, submitted version, receipts/errors, observations and outstanding
human/provider steps. A prepared-only route should still deliver a usable packet.
It must say which external steps remain unperformed.

- Corrections: accepted provider update and observed DSP change have separate states.
  A later public check can independently verify the change without resubmitting it.
- UGC: enrollment submitted, reference active, policy active, observed claim and
  revenue reported are separate outcomes. Conflicting rights go to a documented
  resolution case, not a speculative enforcement or takedown action.
- Migration: use `templates/delivery-transition.csv` for source/target availability,
  acceptance, identity continuity and residual destinations. Verify the target before
  any authorized old-delivery removal under current provider rules. Do not apply an
  unconditional takedown-first or UPC-reissue rule.
- Financial continuity: preserve pre/post effective dates and collection tails for
  a scoped reconciliation handoff. A corrected DSP credit or successful migration
  does not demonstrate historical royalties have been corrected or paid.

Scripts ship alongside this skill. Use `python3 scripts/catalog-case.py --help`
and `references/catalog-contracts.md` for resumable action/attempt/outcome records.
Check `status --file CASE_FILE` on resume; changed payload/assets or authority
invalidate affected action readiness, not historical receipts.

`fixtures/evaluation-cases.json` covers synthetic credit correction, partial propagation,
UGC eligibility, duplicate attempts and an interrupted distributor transition.

For a named provider, read `references/catalog-providers/index.md` and only its
applicable family/profile. The dated registry separates documented preparation
from implemented transports and live verification; refresh current account rules
before claiming provider validation or executing an operation.
