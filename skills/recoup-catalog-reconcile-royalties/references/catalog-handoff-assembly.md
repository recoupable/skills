# Assemble a selected private catalog handoff

Use `scripts/assemble-catalog-handoff.py` to assemble already-created exports.
Scripts ship alongside this skill; invoke them relatively. This produces CSV
schedules, exact JSON and a Markdown index. It does not create an XLSX workbook,
run new financial calculations, import customer data, or complete a full deal.

## Supported immutable inputs

Select one export of each needed kind, at most four:

- `case`: the default, no-summary output of `scripts/build-catalog-report.py`.
  Schema version is integer `1`; scope is `selected_case_records`. Its six CSVs
  and report must match its manifest. Summary-inclusive exports are refused.
- `entitlement`: `scripts/build-royalty-workpaper.py` output, with string schema
  version `"1"` and stage `contractual_entitlement`.
- `remittance`: `scripts/build-remittance-workpaper.py` output, with string schema
  version `"1"` and stage `statement_remittance_receipt`.
- `normalization`: the existing output of `scripts/build-normalization-workpaper.py`,
  string schema version `"1"`, stage `normalization_import_controls`. Select the
  completed workpaper directory, not a source file, ledger, raw receipt or archive.

The financial manifest's exporter, calculator, primitives and applicable export
contract hashes must match the copies shipped with this skill. Unsupported helper
versions are refused, not silently upgraded. Preserve historical exports; regenerate
with the corresponding supported helpers into new directories when appropriate.
The normalization manifest uses its exact seven `helper_hashes` instead: normalizer,
ledger validator, entitlement export contract, finance primitives, bounded workpaper
IO, archive CSV limiter and normalization exporter. All must match shipped bytes;
unknown/missing helper entries are refused. Other stage formats remain unsupported.
Do not mark those stages complete because the selected handoff succeeded.

Each selected export is included as a whole stage, with all its schedules and
controls. Do not trim financial rows or their evidence before assembly: that could
separate a total from its contributors. Selectivity is between exports, not within
a stage. Unselected directories are never discovered or read.

## Explicit selection and new destination

Create a private selection JSON file. Supply the exact SHA256 of each reviewed
`manifest.json`; a local hash can be obtained with `shasum -a 256 PATH/manifest.json`.
Keep the selection file private because its directory locations are sensitive.
Example structure (replace the sample paths and digest with your reviewed values):

```json
{
  "schema_version": "1",
  "exports": [
    {
      "kind": "entitlement",
      "directory": "/authorized/private/entitlement-v1",
      "manifest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  ]
}
```

```bash
python3 scripts/assemble-catalog-handoff.py \
  --selection /authorized/private/selection-v1.json \
  --output-directory /authorized/private/handoff-v1
```

Paths are local filesystem paths, relative to the invocation directory if not
absolute. Dot components are canonicalized before containment checks and all IO;
the original spelling is checked for links before resolution. Use physical paths: symlinks, including linked parent directories, are
refused (on macOS use `/private/tmp` rather than `/tmp`). The output parent must
already exist. The new output cannot exist or be inside an input export, and input
exports cannot be inside the output. No overwrite or automatic parent creation.
The helper creates private directories (0700) and files (0600). A failed write
removes only the new directory created by that invocation. Original exports remain
untouched; do not edit their manifests to bypass refusal.

Limits: selection 64 KiB, each input manifest 1 MiB, other input files 16 MiB,
128 MiB combined admitted input bytes, four unique export kinds, 10,000 rows per
schedule/list, JSON depth 16, 256 keys per object and 65,536 characters per JSON
string (numeric fields and all JSON numeric tokens, including discarded extensions,
are additionally limited to 256 characters before decoding). CSV fields use
an explicit 16 MiB parser limit, restored after each read; file and row caps still
apply. Producer-accepted ISO date spellings and whitespace/underscore decimal
spellings are validated without rewriting their stored text. These bounds intentionally support review-sized exports, not every possible
calculator output. Oversized exports require a separately reviewed workflow; do not
split a total from its complete contributor/evidence schedules to fit these bounds.
JSON floating-point tokens are decoded exactly, without binary rounding, only to
admit discarded private extensions (finite, at most 256 characters and exponent
from -128 to 128). Financial fields still refuse these tokens: they require the
supported exact decimal strings or integers. Duplicate JSON keys, non-finite numbers, duplicate manifest members, unknown names listed in the manifest, unsafe paths,
mismatched file hashes and incompatible schemas are refused. Additional unlisted
files in an input directory are ignored: they are neither read nor included, and
acceptance does not certify the integrity or contents of the whole directory.

## What is verified and what is preserved

The supplied manifest must match the selection's digest. Every expected CSV, JSON
and report is hash-checked before inclusion. Financial JSON uses the supported
allowlisted fields and typed values; its controls must match the manifest, and each
CSV must match its JSON schedule using the existing display/formula-guard contract.
Amounts, negative signs, sub-cent precision, unknown nulls, periods, allocation
references, rule aliases, source hashes, supplied freshness and scope are preserved.
No arithmetic is rerun by assembly. `matches_recomputed_input` is the producer's
saved calculation check, not a new calculation or independent source verification.
Hashes bind supplied bytes; self-consistent fabricated files do not become authentic
financial evidence because their hashes match.

Private extensions, source originals, arbitrary report prose, source locations,
account identifiers and credentials are not copied. Reports are rebuilt from fixed
text. Case IDs, rule versions, source references, dependencies, shared-cause IDs and
evidence-gap prose become consistent SHA256 aliases. Case stages and statuses remain
visible, including stale and rejected states; gap text must be resolved against the
private case. Legacy scalar CSV fields beginning with an apostrophe followed by a
formula-leading character are ambiguous and refused: the original might contain
the apostrophe or the exporter might have added it. Do not strip or rename private
identities to bypass refusal. Such cases need a separately coordinated, versioned
lossless exporter contract. Unambiguous apostrophes and identities inside structured
JSON reference cells retain their exact original spelling before aliasing. Financial values and aliases remain sensitive, even without originals.

Case and financial exports retain separate scopes. The assembler does not invent a
crosswalk between their IDs, assert that they belong to one case, establish present
account access or claim the records are current. The user must establish their
relationship from the exact private source versions before relying on the combined
handoff. Unselected supported kinds are listed as excluded. There is no monetary
cross-stage rollup: intermediate bridges, earnings, recoupment, remittances, bank
receipts, adjustments and repeated shared-cause findings are never added together.
Unknown or missing values are not zero; partial and out-of-scope results are not
passed checks. Assembly never refreshes an evidence-check date.

## Resume without chat history

1. Verify output `manifest.json` against the received files. It hashes every output
   except itself; retain its digest separately when transferring an authorized copy.
2. Read `handoff.json` for included/excluded scopes, the selection digest and exact
   input manifest hashes. Read each listed `workpaper.json` for its controls and
   complete schedules. For entitlement/remittance, use input/result hashes, the
   optional evidence-inventory hash and producer hashes. For a case export, use
   case_sha256 and revision; it has no financial result/inventory or producer hashes.
   For normalization, use receipt_sha256, ledger_sha256 and row_receipt_sha256, optional
   original-source/additional-controls hashes, source/transform/parser aliases and
   the seven producer helper hashes. These bind supplied snapshots, not historical
   receipt-to-ledger bytes or authenticated originals.
3. Resolve those hashes and aliases against the authorized private evidence inventory
   and case revision. No source locations or originals are embedded in the handoff.
4. Check whether newer source/case versions supersede these snapshots. Current-record
   verification is explicitly `not_performed`; unknown/stale evidence remains so.
5. Review unresolved rows, missing stages, scope exclusions and evidence gaps before
   deciding the next action. Keep previous versions intact when assembling a successor.

The result is always `review_required`. Report approval is not permission to publish,
share externally, contact a provider, change registrations, access an account or move
money. External handoff validation and full financial workbook acceptance remain
separate from this local assembly capability.

## Normalization scope stays bounded

The `normalization` selection includes all five existing producer schedules (`rows`,
`written-lines`, `counts`, `totals`, `checks`) with their exact control fields. The
stage-specific allowlist is in `scripts/_normalization_handoff.py`; its source hash
is included in handoff.json whenever normalization is selected. Unknown currency,
amounts and optional hashes remain null. Boolean append flags and nonnegative JSON
integer counts retain their types. Reason codes are the producer's supported codes;
private reasons remain opaque aliases. Arbitrary prose and extensions are excluded.

Assembly never calls the normalizer, producer projection or ledger validator.
Saved producer checks are preserved, not rerun or promoted. Source totals remain
supplied claims; additional controls remain comparisons to those supplied claims.
Newly written detail/held totals retain their concrete line references. Held values
are not eligible earnings. Duplicate-only imports have no new written rows, not new
zero earnings. Missing/invalid associations retain withheld observed totals and
explicit mismatch states. Source totals and written totals overlap and must not be
added to each other, entitlement, remittances, receipts or a previous ledger.

For append, prior-ledger financial controls remain unknown and no baseline money
is emitted by assembly. The historical receipt-to-ledger byte binding remains
`not_provided_by_normalizer; current supplied bytes hashed here`. Consistent supplied
artifacts do not establish authenticity, current rights, freshness, earnings
eligibility or recovered cash. The output stays review_required, with no import,
provider, publication or payment authority. Each normalization input is one existing
per-source workpaper; batch aggregation and row-trimmed workpapers are unsupported.
Existing assembler file/list/numeric bounds still apply; do not truncate a producer
artifact to fit them. Preserve the original and use a separately reviewed route.
