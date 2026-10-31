# Local overclaim evidence preparation

Scripts ship alongside this skill. Run:

`python3 scripts/prepare-provider-packet.py --case case.json --mapping preparation-map.json --output new-packet.json`

Use the existing canonical case and `resolve_claims` action. The provider must be
`The MLC`, operation `overclaim_resolution`, local subject type `composition_claim`
and right `composition mechanical`. Preserve the exact work/claim subjects, account,
represented party, source share convention, territory, period, selected remedy,
disclosure and costs. These are local action fields, not invented provider form fields.
Ordinary interest claims, new registrations and technical rejection repairs remain
registration operations. Do not relabel an action or create a duplicate case to pass.

## Bind the existing evidence

```json
{
  "case_id": "existing-case-id",
  "revision": 2,
  "action_id": "existing-overclaim-action-id",
  "payload_sha256": "<canonical existing payload SHA256>",
  "profile_id": "mlc-overclaim",
  "profile_version": "2026-10-22.1",
  "role": "member_rightsholder",
  "required_inputs": {
    "overclaim/work ID": [{"source_id": "work-state-evidence", "version": "v1"}],
    "competing claims": [
      {"source_id": "represented-claim-evidence", "version": "v2"},
      {"source_id": "contrary-claim-evidence", "version": "v3"}
    ],
    "supporting documents": [{"source_id": "mandate-evidence", "version": "v1"}],
    "exact selected remedy": [{"source_id": "requested-remedy-evidence", "version": "v4"}]
  }
}
```

The other existing eligible role is `authorized_member_representative`. A supplied
role is not verified account access or mandate. Songwriter roles are rejected.
Keep material contrary evidence; the helper cannot determine whether evidence is
complete, authentic or substantively correct. It does not inspect original documents.
Only map sources already in the case; missing labels or empty lists produce a
blocked artifact with named gaps. Complete mappings produce local `prepared`, while
adverse state, identity, source meaning and authority remain unverified.

Use the recorder's canonical payload fingerprint: SHA256 of sorted-key compact JSON,
UTF-8 with non-ASCII preserved and nonfinite values forbidden. Hash the payload, not
the entire action. Preserve current source IDs, versions and original-byte hashes.
The helper binds case bytes/revision, action/payload, mapping bytes, profile ID/version/
fingerprint, dated guidance and checked source records. It never rewrites case history.
Keep the output private with the case; it contains account and evidence metadata.

Changed case/revision/profile/payload, stale/withheld/withdrawn evidence, changed source
versions, invalid dependencies, wrong role/stage/subject/rights and existing attempts
or outcomes for this or an identical-payload action are rejected. Reconcile prior
uncertain activity instead of preparing duplicate intake. `field_values` is rejected
for overclaims; new-work percentage checks cannot adjudicate an overclaim.

Output must be a new file; existing files and aliases are refused. Exit 0 means
locally prepared, 1 means a blocked artifact, and 2 means rejection without a packet.
The helper and its existing dependencies ship inside this skill; no other skill's
files or imports are needed.

## Review each authority and outcome separately

Read `references/catalog-providers/mlc-overclaim-preparation.json` for dated generic
official guidance. `overclaim_review` preserves separate **unverified** review of:

- Exact selected remedy, work/claim scope and original disclosure.
- Contact recipients/content/channel authority.
- Exact amendment authority.
- Relinquishment authority, separate from preparation or share amendment.
- Each document's upload/disclosure authority and actual recipients.
- Provider case disposition and requested versus granted scope.
- Exact share readback, with prior shares and source versions retained.
- Financial effect, separate from a case closure or share correction.

These review entries neither choose a remedy nor grant authority. No message,
amendment, relinquishment, share change, document forwarding or upload occurs.
Do not adjudicate ownership, infer mandate, invent consent or reduce another claim
to make totals fit. A historical hold does not prove current payable; a corrected
record does not prove money received. Real account/procedure/mandate checks and
matching authority remain prerequisites for any separately requested external step.
A complete packet is not filing-ready, a provider form, receipt or resolved dispute.
