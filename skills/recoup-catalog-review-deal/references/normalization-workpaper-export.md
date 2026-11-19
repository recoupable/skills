# Normalization and import-controls workpaper

Use `scripts/build-normalization-workpaper.py` after an existing run of
`scripts/normalize-royalty-statement.py`. Scripts ship alongside this skill.
This is a private export of **one per-source summary receipt, its row receipt and
an explicitly supplied ledger snapshot**. It does not invoke normalization, import
new sources, select a provider, repair ledgers or establish financial entitlement.
Read `references/normalization.md` for the normalizer's existing contract.

```bash
python3 scripts/build-normalization-workpaper.py --receipt import-receipt.json --row-receipt import.rows.jsonl --ledger royalty-ledger-v1.csv --as-of 2026-11-18 --output-directory private-normalization-workpaper-v1
```

Use the original snapshot corresponding to that receipt where retained. Receipt
paths are never followed automatically. The normalizer summary contains **no ledger
or row-receipt byte digest**, so this exporter cannot retrospectively prove their
historical binding. It binds the exact supplied bytes now and checks supported
cross-file associations. Internally consistent files are not authenticated originals.

Optional `--source original.csv` hashes the explicitly supplied source bytes and
compares them to the receipt's source version. It does not parse/import them or prove
source completeness, freshness or truth. Optional `--controls controls.json` uses the
existing normalizer control validator against **supplied source_totals**, not an
independently reconstructed source. The controls document is newly byte-bound by the
export; the old receipt does not identify historical control bytes. A matching
additional control therefore means `matches_supplied_claims_only`.

## What is independently checked

- The existing ledger validator runs on an exact local snapshot of the supplied
  ledger. Its shape/value/held-row result is separate from source controls and
  monetary readiness. Raw error prose is not exported; the result includes bounded
  error sample count, not an asserted total count of every error. Ledger eligibility
  and cross-artifact consistency are separate: consistently represented held/empty
  records may have no artifact mismatch while the ledger validator reports errors.
  Neither is ready; readiness remains review_required. Detected invalid nonempty
  new-row amounts always create a mismatch, even when both receipt total maps are empty.
- Row-receipt dispositions are counted and compared with supplied summary counts.
  This is conservation between supplied artifacts, not an independent count of
  original CSV/XLSX rows. Source version, sheet, position and deterministic ledger
  identity are cross-checked; identity does not prove a source row's contents.
- Detail/held row receipts identify newly written ledger rows. Each must join
  exactly once and match source version, transform, parser, sheet, row position
  and expected status. Unknown/missing/duplicate joins are mismatches, never zero.
- For those joined new rows only, the export reproduces the normalizer's existing
  Decimal aggregation by currency and gross/owner-net/deductions field. Missing
  values remain unknown. It compares these observed values to written_totals.
  No rates, FX, entitlement, income eligibility or new financial formula is added.
  Held-row values are included just as in normalization, **not approved earnings**.
- Source totals remain supplied claims: the receipt does not preserve enough mapping
  inputs to independently reproduce source transformation here. Economic duplicate
  and duplicate-held subtype counts also remain supplied; row receipts do not
  distinguish every subtype or prove the old ledger's status.

## Append boundary

`written_totals` includes only this import's newly written rows, **never earlier
ledger rows**. For append, the baseline's bytes and financial controls stay unknown.
Even a ledger-validator `ok`, matching counts and matching new-row totals cannot
validate the old amounts or establish that old and new sources are disjoint.

An exact repeated source can produce duplicate dispositions and no new rows; its
source totals still describe the source before duplicate handling. An economic
duplicate remains a supplied duplicate-review state. A revised transaction remains
held with an explicit overlap reason. Do not count source totals and written totals
as separate earnings or add them to an earlier ledger's value. No cross-currency,
whole-ledger or monetary recovery total is emitted.

A later ledger snapshot can have extra rows relative to this receipt. The exporter
reports the count mismatch; it does not silently upgrade the receipt to cover them.
Archive batch manifests are not per-source summary receipts and are unsupported by
this helper. A retained per-member receipt can be reviewed against an explicit ledger
snapshot with the same boundaries; an original ZIP hash does not equal member bytes.
No missing file, member or historical snapshot is fetched or manufactured.

## Outputs and meaning

- `rows.csv`: one source-row disposition with typed row/line/source/sheet aliases,
  observed row position, allowlisted reason codes and private-reason aliases.
  Detail, held, control, footer, ignored and duplicate remain distinct.
- `written-lines.csv`: only current import detail/held rows, exact amounts, dates,
  currency, status, field unknowns and provenance checks. Raw account/name/asset
  identifiers, paths, headers, provider prose and raw_values are excluded.
- `counts.csv`: supplied/observed counts with scope and match/mismatch/not-recomputed
  status. Duplicate subtypes have null observed counts, not manufactured zeros.
- `totals.csv`: source_detail_supplied and newly_written_only are separate bases.
  Each observed new total lists its concrete line_refs; source claims link through
  the receipt byte hash. Invalid associations/amounts leave observed totals null.
- `checks.csv`: original-byte comparison, identity joins, ledger validation,
  additional-controls comparison and explicit unsupported/unverified boundaries.
- `workpaper.json`: exact decimal strings and null unknowns, all schedules and
  controls. Receipt ok/matched remains labeled **supplied**. Readiness always
  requires review; freshness, full-ledger financial controls and current rights
  remain unknown. Parser field-population rate is not presented as completeness.
- `report.md`: readable scope, supplied states, local checks and limitations.
- `manifest.json`: SHA256 hashes of all **other** generated files plus the exact
  supplied receipt/ledger/row-receipt bytes, optional source/additional-control bytes
  and executable helpers. It does not hash itself or authenticate historical inputs.

The JSON is authoritative; CSV uses display-only formula guards, including an
apostrophe before negative amounts. Every CSV has fixed headers even when empty.
An empty file, header-only source, unavailable controls, held row or supplied partial
state never becomes a passed source control. Unknown currency is null with a typed
alias, not an invented currency. Report date is not a statement or payment date.

## Supported input bounds

The ledger is hashed and copied in chunks of at most 1 MiB into a private temporary
snapshot; projection and the existing validator both stream that same snapshot.
An append baseline is never decoded/materialized as a whole string. The snapshot
is removed on success or failure. No original is reread to validate a different
version after its bytes have been bound.

Supported limits are explicit: summary and optional controls JSON at most 1 MiB
each; row-receipt JSONL at most 16 MiB and 10,000 nonblank records; each JSONL record
at most 256 KiB including its newline. Per-record JSON admits at most 16 levels,
4,096 nodes, 256 object fields, 2,048 list entries, 64 reasons and 65,536 characters
per string. The top-level raw_values source-column dictionary is exempt from
projected-object field/node counts: ordinary normalization accepts wide CSVs. Each
raw column name/value still receives the string/nested-shape bounds, and the entire
record retains its 256 KiB wire-byte cap. Raw columns are then discarded, not
retained in the row schedule. Retained written-line records are also capped at 10,000.

Ledger and optional original-source files are at most 256 MiB. Ledger CSV permits
at most 1,000,000 rows, 262,144 Unicode characters per logical record (quoted
newlines share the budget), 65,536 characters per field and the exact canonical
column layout. These are exporter admission limits, not new importer limits.
Unsupported inputs fail before the output directory is created; do not truncate
or rewrite originals to bypass a refusal. Preserve a deliberately scoped snapshot
and receipt or use another separately reviewed route for larger artifacts.

The bounded readers ship in `scripts/_normalization_workpaper_io.py`, reusing the
existing CSV record limiter in `scripts/_royalty_archive.py`. Both are included in
the manifest's executable hashes. Output-size tests establish bounded fixture
growth and complete links, not a proof of general algorithmic complexity.

Output must be a new versioned directory. Existing files/directories/symlinks are
refused; the leaf directory is 0700 and generated files 0600. Failed writes remove
only the new partial destination. Wait for the final manifest before consumption.
Malformed or unsupported schemas are refused before output, with generic CLI errors;
well-shaped contradictory artifacts export explicit mismatches for review. Preserve
originals and all prior output versions rather than editing them to make checks pass.

Aliases hash canonical JSON using `json.dumps(value, sort_keys=True,
separators=(",", ":"), allow_nan=False)` with default ASCII escaping, prefixed by
kind. Numeric, string and boolean values remain distinct. Resolve them only against
the exact private hash-bound inputs. Aliases are not anonymization: amounts, dates,
positions and hashes remain private. Report approval grants no sharing/publication,
new import, provider/account action, rights assertion or money movement.
