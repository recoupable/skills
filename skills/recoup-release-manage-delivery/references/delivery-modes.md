# Delivered-release action modes

Use the current provider-specific route and required fields. This reference supplies
workflow invariants; it is not an implemented distributor API or a universal schema.

## Metadata or asset correction

Capture the exact delivered edition, recording version, track order, provider IDs,
ISRC/UPC where supplied, destinations, territories and current field values. Compare
the correction to supporting credits, agreements or technical requirements.

Check whether the requested field can be amended through the provider or requires a
different supported process. A small text edit, a replacement audio asset and a
different recording version can have different identity and delivery implications.
Do not create new identifiers merely to bypass a correction restriction.

Prepare the exact changed values and required assets, hashes and evidence. Keep
unrelated fields stable unless their correction is explicitly in scope. Validate
provider requirements, authority and consequential effects before submission.

Store the accepted distributor change separately from observed destination changes.
Inspect each named destination/territory, with date and evidence, against the exact
expected value. Public search uncertainty stays unknown; inaccessible destinations
are not assumed corrected. Record failed fields, partial propagation and retry scope.

## Existing-recording UGC/monetization enrollment

Establish existing delivery identity, recording owner and the specific monetization
destination/territory being requested. Verify the account's eligible partner/distributor
route, exclusive rights and reference eligibility from current provider rules.

Inspect relevant nonexclusive licenses, samples, loops, public-domain material,
existing references/claims and other restrictions where applicable. Do not infer
exclusive rights or Content ID capability from ordinary channel login or public
metadata. Missing authority blocks that item; a documented conflicting claim is a
resolution issue, not a reason to force enrollment.

Prepare the exact reference/asset, ownership/territory assertions, monetization policy,
exclusions and required attestations. Validate provider-specific rules and authorized
scope. Capture the submitted enrollment, receipt and resulting reference/policy state.

Track independently:

- Eligible/prepared enrollment.
- Actual submitted enrollment and returned item errors.
- Active reference and active policy in the eligible provider account.
- A later observed claim on a specific use, if requested and accessible.
- Reported revenue and received cash through separate accounting evidence.

Enrollment acceptance alone is not proof of detected use, a claim or revenue. This
mode does not issue infringement notices, copyright takedowns or legal demands.

## Distributor migration/redelivery

Use `templates/delivery-transition.csv`. Inventory source delivery IDs, catalog
editions, ordered recordings, identifiers, asset hashes, ownership/territory scope,
availability observations and target requirements. Preserve evidence of historic
availability and identifiers that the provider supports retaining.

Inspect source and target agreements/rules for release rights, notice periods,
exclusivity, duplicated delivery handling, identifiers, fees and removal sequencing.
Do not assume a universal takedown-first sequence or mandatory UPC reissue. Verify
the target's actual identity-continuity requirements and requested asset equivalence.

Prepare a plan by release and destination:

1. Baseline source delivery and observed availability.
2. Target payload/assets and documented continuity requirements.
3. Explicitly authorized target submission and acceptance/readback.
4. Observed intended target availability and unresolved identity/duplication issues.
5. Old-delivery removal only when authorized and appropriate to the verified provider
   sequence; document expected effects and dependencies before executing it.
6. Source removal/release readback and residual destinations/territories.
7. Accounting handoff for old/new reporting, effective dates, fees and collection tails.

An interrupted move resumes from receipts and observations; it does not resubmit
every release. Target acceptance cannot prove source removal, and source removal
cannot prove target availability. Preserve partial success instead of claiming the
whole catalog moved when one destination remains unresolved.

Ownership transfers, publishing administration and collection-mandate updates require
their own operation records. A DDEX/file-format claim is not proof that this distributor
supports this transfer, and a standard excluding distributor transfers is not a
universal migration route. Do not bundle unrelated registration changes into redelivery.

## Provider capability check and unsupported routes

Before action, record official documentation URL/retrieval date, actual account role,
operation, supported schema/version, transport, input validation, fees/disclosures,
retry behavior, receipt and readback. Prefer a verified connector/API when available;
otherwise use a supported authorized portal/import or a prepared packet with a named
human/provider step. Unsupported transport is a completion limit, not a reason to
invent a tool or call a prepared file "submitted".

For a service whose rules have not been researched, return an evidence packet plus
unresolved eligibility/schema questions; do not label it provider-validated. Capability
claims need scoped proof: synthetic scenarios cover workflow logic, while authorized
live receipts and destination observations establish actual operation coverage.
