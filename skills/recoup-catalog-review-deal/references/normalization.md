# Royalty normalization and source controls

Use `scripts/normalize-royalty-statement.py` on supplied CSV/TSV or XLSX exports.
It preserves decimal strings, original rows, source hashes, row/sheet positions and
parser/mapping versions. It does not establish ownership, entitlement or cash.

```bash
python3 scripts/normalize-royalty-statement.py --provider publisher-admin --input original.csv --output royalty-ledger.csv --column-map mapping.json --controls controls.json
python3 scripts/validate-normalized-ledger.py royalty-ledger.csv
```

`mapping.json` maps **source column names to canonical fields**, for example
`{"Net Royalty":"owner_net_amount","Currency Code":"currency"}`. An explicit map
wins over aliases, including an empty mapped value. Do not insert invented USD,
rights, income type or owner-net amounts. Missing classifications remain held.
If a contract or statement header establishes a constant absent from every row,
prepare a separate documented derived input retaining original row references;
never claim that a provider name alone proves the constant.

`controls.json` contains `evidence_refs` and `totals`, such as
`{"evidence_refs":["statement:page-1"],"totals":[{"currency":"USD","field":"owner_net_amount","amount":"12.0049"}]}`.
Controls compare each supplied currency/field total exactly. Without independent
source totals, `controls_status` stays `unavailable`, even if rows validate. A
successful parser is not a reconciled statement or complete data room.

## Inputs and supported scope

Use `--sheet` for an identified XLSX sheet; a missing name fails rather than
silently using the active sheet. XLSX needs `openpyxl`; the script names the missing
package. CSV/TSV needs only Python's standard library. Both stream rows; append
uses a temporary SQLite identity index instead of holding the ledger in memory.

Provider keys select column aliases, **not legal rights or economic categories**:
ASCAP, BMI, MLC, distributor, publisher-admin, SoundExchange, direct-sync, YouTube
Content ID, Curve and other keys shown in `--help` still require observed category,
period and currency fields. A file with unfamiliar columns needs explicit mapping
and source controls before use. No exact support for every portal/export revision
is claimed. Kobalt and another administrator's files can use explicit supplied-field
mappings; this is not a certified Kobalt API or universal account export parser.

Preserve performance/usage periods separately from reporting periods, report dates
and payment dates. Report Date is never automatically a Payment Date. Ownership,
collection, raw statement percentages, parent-chain rows and participant shares are
different fields; do not infer an owner share from them. Sync describes a use and
may cover master, composition or both, so it cannot determine the underlying right.

## Row conservation, versions and duplicate handling

Each run creates a summary JSON receipt and a `.rows.jsonl` receipt under the
output ledger's `.receipts` directory. The summary records source SHA256, selected
sheet, parser/transform IDs, currency totals, row counts and controls status. Every
input row receives a disposition: detail, held, control, footer, ignored or duplicate.
A song title starting with “Totals” is not itself a control row. Explicit Row Type
or row_class fields identify control/footer records; retain their source receipt.

`row_status: ready` means the required observed fields are present; `held` rows
remain in the ledger with reasons and cannot enter financial aggregation unnoticed.
Missing owner-net, currency, rights, income type, dates, malformed rows and unknown
row classifications require resolution. Header-only files cannot pass as complete.

Use a **new output version** for a rebuilt ledger. To add another source to a
compatible ledger, use `--append`. Exact source-hash/sheet/row identities are stable,
so reimporting an identical export does not duplicate income. Explicit scoped
account/statement/transaction IDs also catch repeated and revised transactions.
Changed mapping of the same source requires a rebuild. Conflicting revisions are
held for review; unkeyed overlapping exports cannot be automatically deduplicated.
Do not delete old ledgers/receipts as a routine workflow step.

Amounts remain unrounded through normalization, controls and calculation. Any
statement-specific rounding is a separately evidenced reporting boundary. Never
sum different currencies or unrelated periods into a single financial number.

## ZIP statement batches

Use the existing command's explicit archive mode for a ZIP of UTF-8 CSV/TSV
exports using one chosen provider profile and column map:

```bash
python3 scripts/normalize-royalty-statement.py --archive --provider publisher-admin --input statements.zip --output normalized-batch --column-map mapping.json
```

The output must be a **new directory**. It contains `ledger.csv` when any CSV/TSV
member parsed, `manifest.json`, and per-member summary/row receipts in `receipts/`.
Keep the original ZIP. Each receipt binds its exact archive SHA256, original member
name, member SHA256, parser/transform version and source-row dispositions. Ledger
`source_file` uses `zip:<archive SHA256>!/<member name>` rather than a deleted
extraction path. Member content hashes retain the normalizer's existing identity;
identical bytes in different members do not create new ledger rows.

Members run in ascending exact-name order, **not inferred statement chronology**.
The existing normalizer handles explicitly keyed original/corrected/reversal rows;
conflicting keyed revisions remain held. Unkeyed overlap still needs manual review.
No mixed-currency or cross-period aggregate is produced. Exact source and written
totals remain separate per member. The archive command does not choose which
revision is authoritative or infer replacement relationships from filenames.

Malformed CSV members record errors without dropping previously parsed members.
Header-only and held rows keep the batch partial. Non-CSV/TSV files are recorded as
unsupported, including PDFs, spreadsheets and nested archives. They are never
silently skipped. A partial bundle exits 1; an unsafe/corrupt ZIP exits 2 without
publishing a bundle. Successful parsing exits 0 but is not independent financial
reconciliation. Archive mode has no per-member source controls interface:
`controls_status` stays unavailable. Use ordinary per-file normalization with
`--controls` when supplied control evidence needs comparison. `--append`, `--sheet`
and `--controls` are rejected in archive mode; do not apply one file's totals to
an entire ZIP. Mixed provider formats require separately selected batches.

Limits are fixed in the shipped CLI: 128 entries (including directories), 256 MiB
compressed input, 1 MiB central-directory metadata, 512 MiB expanded per member,
1 GiB expanded across files and a 200:1 per-member compression ratio. Archive
CSV parsing also caps each logical record at 1,048,576 Unicode characters
(at most 4 MiB UTF-8) before parser allocation and headers/rows at 1,024 columns.
Quoted multiline records share one budget; over-limit members record errors. ZIP64,
multidisk/encrypted archives, other compression methods, unsafe/duplicate names,
links and special files are rejected. Supported methods are stored and deflated.
No member paths are extracted. The command snapshots the archive to bounded
local temporary disk and streams one member at a time. Output disk scales with
ledger and raw-row receipts; allow space for those plus temporary staging. Each
member append scans the prior ledger using the existing disk-backed identity
index, so CPU/I/O grows with both row and member counts. These limits are not a
performance guarantee for arbitrary provider files. Keep oversized inputs split
into separately reviewed, bounded source batches.

## PDF candidates

`extract-pdf-statement.py` is an experimental text-table candidate extractor using
`pdfplumber`. Scanned PDFs need another verified extraction route. Candidate rows
are held and require row/page comparison, exact field mapping and source controls;
a PDF filename or society label does not prove successful parsing. A generated
candidate ledger must not be reported as a completed financial reconciliation.

## Validation

Run `validate-normalized-ledger.py` on the result and reconcile its source receipts.
For maintainer regression coverage in a source checkout, run:

```bash
python3 -m unittest discover -s skills/recoup-catalog-review-deal/tests
```

The public fixtures are synthetic. Tests cover precision, missing fields, repeated
and revised imports, wrong worksheets, source controls, typed dates/classifications,
financial eligibility and separate receiving-account evidence. They do not prove a
live provider integration. Keep private customer statements out of public fixtures.

Source controls compare all source detail before duplicate disposition. `written_totals` separately reports only rows newly written by this import; existing appended rows are excluded. An economic duplicate requires review and keeps overall status partial even if source controls match.
