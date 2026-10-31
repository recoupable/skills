# Local profile-bound preparation

`python3 scripts/prepare-provider-packet.py --case case.json --mapping preparation-map.json --output new-packet.json`

This command supports the sourced `mlc-new-work`, `mlc-transfer` and
`mlc-amend-work`, `mlc-member-match` and `mlc-songwriter-match` profiles. It produces
an evidence preparation JSON artifact, **not an MLC form, CWR file, submission,
external preflight or filing-ready payload**. It reads the existing catalog case and
never edits it, grants authorization, records an attempt or invents a provider receipt.

For new work, use the existing action's exact provider (`The MLC`), operation
(`new_work_registration`) and stage (`register`). For this command the action must
explicitly state local scope fields `subject_type: "composition"` and
`rights: ["composition mechanical"]`. These scope fields describe the local action,
not provider-form fields. Preserve the original subjects, account, party, territory,
effective dates, disclosure and costs; do not alter them just to make preparation pass.

Create an explicit mapping using the exact current case/action/profile bindings:

```json
{
  "case_id": "existing-case-id",
  "revision": 2,
  "action_id": "existing-action-id",
  "payload_sha256": "<canonical existing payload SHA256>",
  "profile_id": "mlc-new-work",
  "profile_version": "2026-10-22.1",
  "role": "member_rightsholder",
  "required_inputs": {
    "work identity": [{"source_id": "source-work", "version": "v1"}],
    "writers/publishers": [],
    "supported shares": [],
    "mandate": [],
    "current provider form": []
  }
}
```

The other profile-listed role is `authorized_member_representative`. This is a
supplied role label, not verified membership, mandate or account access. Choose it
only from supplied context; the command never infers eligibility from login access.

Use the existing recorder's canonical payload fingerprint: sorted-key compact JSON,
UTF-8, non-ASCII preserved, nonfinite numbers forbidden. For a payload saved alone,
Python's `hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()` reproduces it.
The command checks that digest against the case; never hash the full action instead.

Each required-input label must match the profile exactly. Map only existing active
source IDs and exact versions. Missing labels or empty lists produce a **blocked**
packet with named gaps. All labels supplied produce **prepared**, while evidence
meaning, current form, role and external preflight remain **unverified**. Source
metadata/hashes are bound, but source contents and legal meaning are not inspected by
this command. One source can support several labels only when the user explicitly
maps it; this is never inferred from filenames or source text.

The packet binds case bytes/revision, action/payload, mapping bytes, profile ID/version/
fingerprint and dated profile sources. It retains the exact action payload, evidence
source records, supplied/missing labels and profile completion steps. Keep the packet
private with its case: it contains scoped account, rights and evidence metadata.

The output must be a new file. Existing files, symlinks and hard-link aliases are
refused. Exit 0 means locally prepared; 1 means a blocked artifact with missing
inputs; 2 means rejection with no generated packet. Stale/withdrawn/redacted evidence,
changed payload/revision/profile, unsupported roles/routes/profiles and provider,
operation, subject or rights mismatches are rejected. Existing attempts/outcomes for
the action or an identical-payload action require resuming/reconciling that case,
not generating duplicate intake. No action or attempt is created to bypass them.

Before any separately requested provider operation, inspect current official form
and route, account role, mandate/territory/effective dates, existing work search,
disclosure/costs and action authority. Use authentic required fields/documents and
record actual provider receipts/readback only after those events. The profile's dated
references are source provenance, not a claim they were refreshed by this command.

## Public instructions and missing-input guidance

The packet includes dated `public_preparation_guidance`, its canonical SHA256, and
`missing_input_guidance` for exactly the missing evidence labels. Read
`references/catalog-providers/mlc-public-preparation.json` for official source links
and concrete preparation steps. These are public instructions checked October 30,
2026; the existing operation profile retains its separate verification date.

Use these steps to gather evidence within the same case. The helper does not parse source contents or spreadsheet values. Without the
optional worksheet below, packets report `field_validation: not_performed`.
All packets report `template_retrieval: not_performed_by_helper`. The current bulk template is obtained inside
the Member Hub; no provider workbook or CWR export is generated here. Preserve
unknown account-only fields and verify the actual template before preparing an upload.

A user may already have supplied template evidence. The helper neither retrieves
nor inspects its contents; that evidence remains semantically unverified.

## Optional public field checks (one existing work)

For `mlc-new-work` only, add `field_values` to the same mapping to check a small documented subset of MLC
individual-registration fields. Use the existing action's sole subject ID. This
local worksheet is not a provider upload schema; multi-subject actions are rejected
for these optional checks so a partial check cannot imply batch coverage.

```json
{
  "subject_id": "existing-work-id",
  "work_title": "Example composition",
  "writers": [{"name": "Example Writer", "role": "CA"}],
  "collection_shares": [{"party": "Example Publisher", "percent": "50"}],
  "recordings": [{"title": "Example recording", "artist": "Example Artist"}]
}
```

Use evidence-supported values only; preserve missing fields or nulls instead of
inventing values. Names and collecting parties are local worksheet labels, not
provider identity verification. Collection percentages concern collection authority,
not ownership or PRO shares. The checker does not require the represented shares
to total 100, infer another party's share, or verify duplicate identities.

The packet retains the supplied worksheet under `public_field_checks.values`; the
existing mapping hash binds its exact input bytes. Missing or invalid title, writer
name/role, collection party/percentage, or supplied recording title/artist produces
path-specific findings and a blocked packet even if evidence mappings are complete.
A clean result is `checked_public_subset`, never filing-ready. Required evidence gaps
still block it. Omitted recordings are optional. No template schema, IPI/ISRC format,
account eligibility, actual share entitlement or provider search is certified.
The public sources and retrieval date remain in `public_preparation_guidance`.

Do not create a new action just to bypass an existing attempt or to split a batch
for this checker. Resume the existing case; unsupported batch checks remain manual.

JSON numeric mapping values must retain their decimal value when decoded and
serialized through the helper. Tokens that would lose precision are rejected
(exit 2, no packet) before field checking; provide high-precision percentages as
quoted decimal strings instead. Strings are checked with decimal arithmetic and
retained unchanged, so an out-of-range string produces a blocked artifact with a
field finding. Ordinary numeric boundaries `0.01` and `100` remain supported.
The original mapping bytes, including numeric spelling, stay bound by SHA256;
case/profile parsing and their existing fingerprints are unchanged.


## Existing registered catalog transfer

Use the existing transfer action, provider `The MLC`, operation
`collection_catalog_transfer`, stage `register`, and local scope
`subject_type: "collection_mandate"`, `rights: ["composition mechanical"]`.
Keep its exact subjects, source/target account context, represented party, territory,
effective dates, disclosure, costs and payload fingerprint. These are local case
scope fields, not a claimed MLC form schema. Do not repurpose a new-work action.

Set `profile_id` to `mlc-transfer` and `profile_version` to `2026-10-22.1`, keeping
the same case/revision/action/payload binding fields shown above. Map the four exact
labels to existing active source IDs and versions:

```json
{
  "registered work list": [{"source_id": "existing-work-evidence", "version": "v1"}],
  "source member": [],
  "effective date": [],
  "authentic authority/termination evidence": []
}
```

This fragment is `required_inputs`, not a standalone mapping. Missing entries yield
a blocked packet. Complete mappings yield local preparation only; the helper does
not confirm registration, identify a Member, authenticate a document or interpret
termination rights. The same role, source-version, stale/withheld, withdrawn-source,
existing-attempt and existing-outcome checks apply to both profiles.

Read `references/catalog-providers/mlc-transfer-preparation.json` for dated official
source links and input guidance. It is separate from new-work guidance. Transfer
mappings reject `field_values`; no new-work title, writer-role or percentage rules
are applied. There is no invented transfer form, CWR output or submission adapter.

The packet's `transfer_review` keeps document forwarding to existing claimants
visible and marks disclosure review, source release, target acceptance/effective
scope and collection tails separately **unverified**. It preserves the action's
original disclosure rather than changing it or approving recipients. Review actual
authority before any separately requested upload. These review entries are neither
provider receipts nor observed outcomes. Keep authentic termination evidence,
retained rights and collection tails available for the human/provider checks.


## Technical amendment of an existing work

Use the existing amendment action with provider `The MLC`, operation
`amend_existing_work`, stage `register`, and local scope
`subject_type: "composition"`, `rights: ["composition mechanical"]`.
Preserve its exact subjects, account, party, territory, dates, disclosure, costs and
payload fingerprint. Do not turn an ordinary existing-interest claim or adverse
rights dispute into a technical correction just to use this helper.

Use `profile_id: "mlc-amend-work"`, `profile_version: "2026-10-22.1"`, the same
case/revision/action/payload binding fields and an eligible supplied role. Map the
three exact required-input labels to existing active evidence sources:

```json
{
  "existing work ID": [{"source_id": "existing-identity-evidence", "version": "v1"}],
  "current record": [
    {"source_id": "current-record-observation", "version": "v2"},
    {"source_id": "prior-submission-evidence", "version": "v1"}
  ],
  "evidenced correction": [{"source_id": "proposed-correction-evidence", "version": "v3"}]
}
```

This fragment belongs under `required_inputs`; it is not a new case or complete
mapping. Keep actual current and proposed values in their original evidence and
retain superseded submission history. An active source documenting an older
submission is valid evidence; a withdrawn, withheld, stale or version-mismatched
source is not. Never overwrite a source version or erase a prior receipt to make
an amendment pass. The case remains byte-for-byte unchanged and its history stays
bound by the case hash. The packet retains mapped source records and versions, not
source-document contents or an exported copy of all case history.

Missing mappings produce a blocked packet with specific guidance. Complete mappings
produce local preparation only: source meaning, work identity and correction
accuracy remain unverified. The helper does not compare current and proposed field
values, authenticate documents or interpret rights. `field_values` is rejected for
amendments; new-work validation rules are not reused as amendment rules.

Read `references/catalog-providers/mlc-amendment-preparation.json` for separately
dated public instructions. `amendment_review` keeps superseded history, affected
interests/authority, operation scope and accepted-record readback separately
unverified. The packet preserves original disclosure and supplies no new authority.
Current Member Hub form/account review is still required before any separately
authorized operation; no provider form, transport, filing-ready payload or receipt
is generated. Preserve submission, acceptance and observed correction as distinct
actual events when they later occur.


## Member recording-to-work matching

Use the existing Member matching action with provider `The MLC`, operation
`recording_work_match`, stage `register`, and local scope
`subject_type: "recording_work_link"`, `rights: ["composition mechanical"]`.
Retain the exact work/group subjects, account, represented party, territory, dates,
disclosure, costs and payload hash. Do not change an existing action or create a
replacement to bypass previous attempts or outcomes.

Set `profile_id: "mlc-member-match"`, `profile_version: "2026-10-22.1"` and retain
the same case/revision/action/payload binding fields. The existing profile accepts
only the supplied role `member_rightsholder`. It rejects
`authorized_member_representative` and Songwriter roles; this local profile limit
is not a claim about every provider account permission. Actual eligibility remains
unverified. Songwriter matching uses the separate `mlc-songwriter-match` profile
and role described below.

Map the three existing labels to active sources with exact versions:

```json
{
  "work in eligible catalog": [{"source_id": "existing-work-evidence", "version": "v1"}],
  "recording group/ISRC": [{"source_id": "selected-group-evidence", "version": "v2"}],
  "identity evidence": [{"source_id": "identity-comparison-evidence", "version": "v3"}]
}
```

This is the `required_inputs` fragment of a mapping, not a new case or provider
form. Compare writers, version, recording artist, identifiers and group details;
title similarity alone is insufficient. Keep ambiguous identity unresolved. The
helper binds the supplied action and evidence, but does not inspect source contents,
validate ISRC format, compare identities, normalize identifiers or automatically
match a group. A changed group in the action requires a new matching payload hash;
old mappings cannot silently select another group.

Missing evidence labels yield a blocked packet. Complete mappings yield local
preparation only. `field_values` is rejected; new-work field checks are not matching
checks. Read `references/catalog-providers/mlc-member-match-preparation.json` for
dated public guidance. `member_match_review` keeps actual Hub eligibility, identity
comparison, group coverage, Match History and authority unverified. It does not
invent a provider status for any group. Preserve actual per-group partial or rematched
results separately if later observed; a prior match suggestion is not acceptance.

No Member account is inspected or changed. The original disclosure stays intact;
a complete packet neither authorizes a suggestion nor claims an accepted match,
collection entitlement, payment or receipt. Follow the existing uncertain-attempt
reconciliation rule before any separately authorized provider operation.


## Songwriter Hub recording-to-work matching

Use the existing Songwriter matching action with the same provider `The MLC`,
operation `recording_work_match`, stage `register`, local subject type
`recording_work_link` and right `composition mechanical`. Keep the exact original
work/group subjects, account, party, scope, disclosure and costs; do not relabel a
Member action or create a duplicate action to bypass an attempt.

Select `profile_id: "mlc-songwriter-match"`, `profile_version: "2026-10-22.1"`
and supplied role `songwriter_hub_user`, with the same case/revision/action/payload
binding fields and three evidence labels shown for Member matching. Map active
sources and exact versions for `work in eligible catalog`, `recording group/ISRC`
and `identity evidence`. All withdrawal, stale/dependency/version and duplicate
attempt/outcome checks still apply. Missing labels block local preparation.

The profiles share a documented route name, but their roles are not interchangeable:
Songwriter matching rejects `member_rightsholder` and
`authorized_member_representative`; Member matching rejects `songwriter_hub_user`
and `authorized_member_representative`. These are existing local profile limits,
not an account permission audit. Actual Hub eligibility remains unknown. Songwriter
catalog visibility is not Member status, a share claim or collection authority.

Read `references/catalog-providers/mlc-songwriter-match-preparation.json` for
separately dated Songwriter guidance. `songwriter_match_review` keeps Hub eligibility,
identity comparison, group coverage, Match History and authority unverified. Compare
writers, recording version, artist and identifiers, not title alone. Preserve
per-group partial/rematched observations separately if actually received; a suggested
match is not acceptance, and approval is not necessarily an observed updated record.

The helper does not inspect source contents, verify identity, validate ISRC format,
automatically match recordings, retrieve an account form or alter access. It rejects
`field_values`. Complete evidence mappings remain local preparation, never a claim
of rights, filing readiness, provider acceptance or a receipt. Account capabilities,
mandate and disclosure still need review before any separately authorized action.
