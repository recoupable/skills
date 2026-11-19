# Statement, remittance and receipt workpaper export

Use after `scripts/reconcile-remittances.py` for its existing supported allocation
schema. Scripts ship alongside this skill. This branch exports supplied arithmetic
and evidence states; it adds no new financial math, bank connection or provider
operation. Entitlements and generic case reports remain separate branches.

Reuse an existing validated result with its original input; do not overwrite it:

```bash
python3 scripts/build-remittance-workpaper.py --input remittance-input.json --result remittance-result-v1.json --as-of 2026-11-18 --output-directory private-remittance-workpaper-v1
```

If a new calculation is needed, create a new private version first. The calculator
itself overwrites output, so the exclusive directory creation must succeed:

```bash
( umask 077 && mkdir -m 700 remittance-run-v2 && python3 scripts/reconcile-remittances.py --input remittance-input.json --output remittance-run-v2/result.json )
```

Read the structured result status. Calculator exit 1 can mean a valid `partial`
result or `invalid_input`; these are different. Partial results can be exported;
invalid input cannot. Export a valid result in a separate command:

```bash
python3 scripts/build-remittance-workpaper.py --input remittance-input.json --result remittance-run-v2/result.json --as-of 2026-11-18 --output-directory private-remittance-workpaper-v2
```

The exporter recomputes with the existing calculator, compares the complete JSON
result including types, and refuses mismatches before writing. Keep historical
input/result pairs rather than changing them to pass. Inputs use the calculator's
existing decimal parsing contract; JSON floating-point tokens become exact input
strings. Saved results retain JSON types, so false cannot replace zero and numbers
cannot replace decimal strings. No source is modified. Output must be a new path;
existing directories/files and symlinks are refused. Directory mode is 0700 and
files are 0600. Failed writes remove only the new partial directory. Consume only
a completed directory with its final manifest; the input files' permissions are
not changed.

## Schedules and lineage

- `records.csv`: statement, remittance and receipt records with exact amounts,
  separate currencies, statement periods, actual remittance/receipt dates, source
  record aliases and supplied source-version aliases. Periods absent from receipt
  records are unknown, not the receipt date or report date. `source_version` is an
  optional original-record field; absent versions remain null. Whole input and
  result byte hashes always bind the output even without per-source versions.
- `allocations.csv`: the calculator's successful stage edges, exact from/to values,
  FX rate, signed adjustment total and verification state. `from_record_ref` and
  `to_record_ref` link records, periods and evidence. Follow statement→remittance
  edges to statement periods; don't infer allocation-specific earning dates or
  copy every ancestor period into every receipt. Edge evidence and FX evidence
  stay on the edge; record evidence stays on the records.
- `adjustments.csv`: each successful edge's fee, withholding or supported adjustment,
  its signed amount in receiving currency and evidence. Resolve `allocation_ref`
  for its bridge. These amounts are already included in the edge's to_amount.
- `residuals.csv`: stage/side/record-keyed amount, allocated and unmatched values,
  including whether each row falls in requested completion scope. Resolve its
  record link for period/evidence. The same remittance can appear on both stages;
  do not add those residuals. Unmatched does not mean debt.
- `verified-receipts.csv`: the calculator's sparse signed net totals by currency.
  Each total lists its concrete `allocation_refs` with that to_currency and
  verified_receipt/verified_return status, then links to source records and evidence. No additional
  sum is computed by the exporter. Missing currency means no supplied verified
  total, not observed zero; a present zero can reflect receipts net of returns.
- `unresolved.csv`: rejected allocation aliases, known/unsupported stage and unknown
  amounts. Detailed reasons stay in the hash-bound private result because errors
  may include private identifiers or free prose. A rejected edge is not emitted
  as a successful allocation or monetary recovery.
- `evidence.csv`: reusable source digest/current digest/check date/freshness rows.
- `workpaper.json`: authoritative exact decimal strings, null unknowns, all schedules,
  scope, missing stages, unverified allocation aliases, calculator result status,
  source controls and readiness. CSV keeps fixed headers even when empty. Negative
  and formula-like CSV values have a display-only apostrophe; do not recalculate
  from that display representation.
- `report.md`: readable scope, counts, verified currency nets and limitations.
- `manifest.json`: hashes of all other generated output files (excluding itself),
  plus original input/result bytes,
  optional evidence inventory, calculator, finance primitives, exporter and its
  local export-contract helper (`scripts/build-royalty-workpaper.py`).

`allocated_statement` is not cash. A provider Paid label is not a posted receipt.
Posted but user-reported evidence stays `user_reported_receipt_unverified`.
`verified_receipt` and `verified_return` mean the existing local calculator accepted
supplied observed posted evidence and matching account scope; no live source or
account authentication is performed. A return remains negative. Private account
references never enter this export.

Completion status `ok` applies only to the requested calculator stages. Statement-only
completion does not establish cash. Partial results preserve successful edges and
verified amounts alongside missing stages, unverified edges and unmatched entries.
`unmatched_required_records` counts residual entries, not unique people/payments.
Readiness never claims source verification. Current payable and newly recovered
cash are always null. Stages, adjustments and residuals must not be added together
as earnings or separate recoveries; no shared-cause recovery rollup is calculated.

## Source versions and privacy

Use optional `--evidence inventory.json` with the same inventory contract documented
in `references/royalty-workpaper-export.md`. Each source entry supplies evidence_ref,
source_sha256, current_sha256 and checked_on. Include FX and adjustment evidence.
Different non-null digests are stale; equal digests checked on the report calendar
date are current_as_supplied, never independently verified. Missing hashes/entries
or older checks are unknown. Future check dates and malformed hashes are refused.
The report as_of is not a payment date, source publication date or live freshness
claim. An ok arithmetic result can still be stale or unknown.

Record/allocation/source/version/status/access aliases hash canonical JSON:
`json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)` with default
ASCII escaping, prefixed by the stated kind. Thus numeric 1, string "1" and boolean
true remain distinct. Adjustment identity hashes the pair [allocation_id,
adjustment_id] to preserve scope. Evidence aliases reuse the existing UTF-8 string
SHA256 contract, so they join the evidence schedule. Resolve aliases only against
the exact private input identified by the manifest.

Only known status labels are exported literally; arbitrary reported statuses and
access descriptions have aliases and explicit other/unknown labels. Supplied access
is a description, not an authenticated capability. Source names, paths, locations,
account references, originals, arbitrary extensions and error prose are excluded
by selection. Aliases are not anonymization: amounts, dates and hashes still need
a private destination and human review before sharing. Export/report approval never
authorizes publication, provider contact, access changes or money movement.
