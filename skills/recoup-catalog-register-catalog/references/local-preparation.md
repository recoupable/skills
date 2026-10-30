# Local profile-bound preparation

`python3 scripts/prepare-provider-packet.py --case case.json --mapping preparation-map.json --output new-packet.json`

This command currently supports only the sourced `mlc-new-work` profile. It produces
an evidence preparation JSON artifact, **not an MLC form, CWR file, submission,
external preflight or filing-ready payload**. It reads the existing catalog case and
never edits it, grants authorization, records an attempt or invents a provider receipt.

Use the existing action's exact provider (`The MLC`), operation
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

Use these steps to gather evidence within the same case. The helper does not parse
source contents or validate title, writer, share or spreadsheet values. Both blocked
and locally prepared packets explicitly report `field_validation: not_performed`
and `template_retrieval: not_performed_by_helper`. The current bulk template is obtained inside
the Member Hub; no provider workbook or CWR export is generated here. Preserve
unknown account-only fields and verify the actual template before preparing an upload.

A user may already have supplied template evidence. The helper neither retrieves
nor inspects its contents; that evidence remains semantically unverified.
