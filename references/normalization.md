# Normalization

Normalization converts provider-specific royalty exports into the canonical
`royalty-ledger.csv` shape. This lets downstream analysis calculate NPS/NLS,
concentration, and valuation bridges from one consistent ledger.

## Current normalizer

Use `scripts/normalize-royalty-statement.py` for first-pass CSV normalization.

```bash
python3 scripts/normalize-royalty-statement.py \
  --provider ascap \
  --input deals/example/source/ascap.csv \
  --output deals/example/normalized/royalty-ledger.csv
```

### Combining multiple providers into one ledger

A deal almost always has several statements (ASCAP, distributor, MLC, …). They
must all land in **one** `royalty-ledger.csv` so downstream NPS/NLS and
concentration math sees the whole catalog. Without `--append`, each call
**overwrites** the file and you silently keep only the last provider.

Delete any existing ledger first, then pass `--append` on every call:

```bash
LEDGER=deals/example/normalized/royalty-ledger.csv
rm -f "$LEDGER"                       # start clean (append never truncates)
for stmt in ascap:ascap.csv distributor:distributor.csv mlc:mlc.csv; do
  python3 scripts/normalize-royalty-statement.py \
    --provider "${stmt%%:*}" \
    --input "deals/example/source/${stmt##*:}" \
    --output "$LEDGER" --append
done
```

`--append` continues `ledger_line_id` numbering across providers (no collisions),
writes the header only on the first (fresh) call, and reports
`"appended"` plus `"ledger_total_rows"` in its JSON so you can confirm the row
count grows with each statement.

Supported provider profiles:

| Provider key | Intended source | Rights type | Income type |
| --- | --- | --- | --- |
| `ascap` | ASCAP-style performance CSV exports | publishing | performance |
| `bmi` | BMI-style performance CSV exports | publishing | performance |
| `mlc` | MLC-style mechanical CSV exports | publishing | mechanical |
| `distributor` | Distributor/DSP master royalty CSV exports | master | streaming |
| `publisher-admin` | Publisher administrator mechanical CSV exports | publishing | mechanical |
| `soundexchange` | SoundExchange/neighboring rights CSV exports | neighboring | radio |
| `direct-sync` | Direct sync income tracker CSV exports | sync | sync |
| `youtube-content-id` | YouTube Content ID CSV exports | master | UGC |
| `curve` | Curve-style royalty accounting CSV exports | source-provided | source-provided |

## PDF statements (experimental, verify-required)

CSV/TSV/XLSX is the happy path. For **text-based PDF** statements (not scanned
images), `scripts/extract-pdf-statement.py` reads tables with `pdfplumber` and
maps them via per-society templates. It ships templates for ASCAP, SESAC, HFA,
SoundExchange, PRS, SACEM, SADAIC, JASRAC, APRA, and SOCAN, matched by file
path + header signature.

```bash
python3 scripts/extract-pdf-statement.py \
  deals/{deal-id}/source/03_royalty_statements \
  --output deals/{deal-id}/normalized/pdf-extracted-ledger.csv \
  --workspace-root deals/{deal-id}
```

It walks a whole directory in one call (no per-file loop), writes to a
**separate** review ledger, and tags every row `match_confidence: low` /
`notes: extracted from PDF, verify against source`. **Always spot-check against
the source PDF and run `validate-normalized-ledger.py` before merging into
`royalty-ledger.csv`.** Requires `pip3 install -r requirements.txt` (pdfplumber);
without it the script exits with a clean `missing_dependency` status. Scanned /
image-only PDFs (true OCR) are still out of scope, and these society templates
are not yet covered by golden fixtures — treat output as a draft.

## What the normalizer guarantees

The script writes all canonical ledger columns:

- `ledger_line_id`
- `catalog_asset_id`
- `source_file`
- `provider`
- `period_start`
- `period_end`
- `payment_date`
- `rights_type`
- `income_type`
- `territory`
- `platform_or_licensee`
- `gross_amount`
- `deductions`
- `participant_share`
- `owner_net_amount`
- `currency`
- `fx_rate`
- `pro_use_type`
- `pro_credits`
- `pro_bonus_type`
- `cue_sheet_ref`
- `match_confidence`
- `notes`

It also preserves important PRO details such as use type, credits, bonus type,
licensee, and work IDs when source columns are present.

## What it does not guarantee

The current normalizer is a first-pass adapter for common CSV shapes. It does
not yet guarantee:

- Exact support for every real ASCAP, BMI, MLC, distributor, YouTube, or Curve
  export variant.
- OCR of scanned / image-only PDFs. (Text-based PDFs have an experimental,
  verify-required path — see "PDF statements" above.)
- Automatic ISRC-to-ISWC matching.
- Contract-based recoupment or reserve calculation.
- Legal ownership support.

Use validation scripts and human review after normalization.

## How to know it works

Use tests and validations:

1. Run `python3 scripts/test-normalize-royalty-statement.py`.
2. Run `python3 scripts/test-golden-fixtures.py` (CSV) and
   `python3 scripts/test-golden-pdf-fixtures.py` (PDF, 9 society templates).
3. Run `python3 scripts/validate-normalized-ledger.py <royalty-ledger.csv>`.
4. Spot-check source lineage by comparing normalized rows back to source rows.
5. Add a new fixture whenever a real provider export has a new column shape.

Provider parsers become trustworthy only when backed by golden fixtures from
real or representative exports.

## Synthetic data room smoke test

The plugin has been tested against the local Neon River synthetic data room
generated by `.local/generate_neon_river_data_room.py`. That room includes
messy seller-style exports for distributor, publisher admin, ASCAP, BMI, MLC,
SoundExchange, YouTube Content ID, and direct sync sources.

The smoke test normalizes all eight raw statement sources and validates each
output with `validate-normalized-ledger.py`. The row total matches the
generator's clean ledger count of 3,188 rows.

## Golden fixtures

Golden fixtures live in `fixtures/golden/{provider-scenario}/`:

- `input.csv` is a small provider-shaped source export.
- `expected-royalty-ledger.csv` is the exact canonical output expected from the
  normalizer.

The current fixtures are synthetic and documented in
`fixtures/external-sources.md`. They are based on public schemas and official
documentation, not private royalty data.
