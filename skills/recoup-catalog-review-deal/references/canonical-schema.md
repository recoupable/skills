# Canonical schema

Use these schemas as the hand-off contract between catalog ingestion and later
analysis. Keep the schema stable even when a source file is messy.

## `data-room-inventory.csv`

Use one row per source file.

| Field | Meaning |
| --- | --- |
| `source_file` | Relative path to the raw file. |
| `source_type` | `financial`, `legal`, `metadata`, `asset`, `analytics`, or `unknown`. |
| `provider` | Distributor, PRO, publisher admin, label, society, platform, or seller. |
| `statement_period_start` | First covered date, if known. |
| `statement_period_end` | Last covered date, if known. |
| `currency` | Reported currency. |
| `rights_type` | `publishing`, `master`, `neighboring`, `sync`, `mixed`, or `unknown`. |
| `parse_status` | `parsed`, `partial`, `manual_review`, or `unparsed`. |
| `notes` | Issues, assumptions, or required follow-up. |

## `canonical-catalog.csv`

Use one row per work or recording candidate. If the source cannot prove whether
a row is a composition or recording, keep it and mark `rights_type` as
`unknown`.

| Field | Meaning |
| --- | --- |
| `catalog_asset_id` | Local stable ID assigned during ingest. |
| `rights_type` | `publishing`, `master`, `mixed`, or `unknown`. |
| `title` | Canonical title. |
| `alternate_titles` | Pipe-separated source titles or variants. |
| `artist` | Primary artist or performer. |
| `writers` | Writers as reported. |
| `publishers` | Publishers or admins as reported. |
| `isrc` | Recording identifier, if available. |
| `iswc` | Composition identifier, if available. |
| `upc` | Release identifier, if available. |
| `ipi_cae` | Writer/publisher party identifiers, if available. |
| `release_title` | Album, EP, single, or source release. |
| `release_date` | Release date. |
| `territory` | Controlled territory or reported territory. |
| `controlled_share` | Seller-controlled share, if supported. |
| `ownership_confidence` | `high`, `medium`, `low`, or `unknown`. |
| `metadata_confidence` | `high`, `medium`, `low`, or `unknown`. |
| `source_files` | Pipe-separated source files supporting the row. |
| `conflicts` | Summary of unresolved conflicts. |

## `royalty-ledger.csv`

Use one row per source statement line at the lowest available grain. Do not roll
up detail until analysis.

| Field | Meaning |
| --- | --- |
| `ledger_line_id` | Local stable ID for the normalized row. |
| `catalog_asset_id` | Link to `canonical-catalog.csv`, if matched. |
| `source_file` | Source statement file. |
| `provider` | Distributor, PRO, society, platform, or admin. |
| `period_start` | Revenue/performance period start. |
| `period_end` | Revenue/performance period end. |
| `payment_date` | Payment or statement date, if different. |
| `rights_type` | `publishing`, `master`, `neighboring`, `sync`, `mixed`, or `unknown`. |
| `income_type` | Performance, mechanical, streaming, sync, physical, UGC, radio, other. |
| `territory` | Reported territory. |
| `platform_or_licensee` | DSP, station, network, licensee, society, or source. |
| `gross_amount` | Gross income before deductions. |
| `deductions` | Fees, admin, reserves, returns, or other deductions. |
| `participant_share` | Writer, artist, producer, co-publisher, or other pass-through. |
| `owner_net_amount` | Estimated NPS/NLS line amount, if calculable. |
| `currency` | Currency. |
| `fx_rate` | FX rate used, if converted. |
| `pro_use_type` | Feature, background, theme, underscore, live, or other, if available. |
| `pro_credits` | PRO credits, if available. |
| `pro_bonus_type` | Premium/bonus category, if available. |
| `cue_sheet_ref` | Cue-sheet or program reference, if available. |
| `match_confidence` | `high`, `medium`, `low`, or `unmatched`. |
| `notes` | Assumptions or extraction issues. |

## `rights-map.csv`

Use one row per relationship between an asset and a rights-supporting document.

| Field | Meaning |
| --- | --- |
| `catalog_asset_id` | Local asset ID. |
| `document_file` | Contract, split sheet, registration, assignment, or support file. |
| `document_type` | Agreement, split sheet, registration, assignment, license, clearance. |
| `party` | Writer, artist, publisher, label, producer, distributor, admin, or other. |
| `share_type` | Writer, publisher, master, producer, admin, or other. |
| `reported_share` | Share percentage or fraction. |
| `territory` | Covered territory. |
| `term_start` | Effective start date. |
| `term_end` | Expiration or reversion date, if known. |
| `restrictions` | Approval rights, samples, territory carveouts, excluded uses. |
| `support_level` | `supported`, `partial`, `missing`, `conflicting`, or `unknown`. |
| `notes` | Issues requiring legal or business follow-up. |

## Confidence scoring

Use confidence labels instead of fake certainty.

- `high`: Multiple sources agree, and at least one authoritative source
  supports the field.
- `medium`: A credible source supports the field, but another source is missing
  or less specific.
- `low`: The field is inferred from weak matching, titles, filenames, or
  incomplete exports.
- `unknown`: No reliable support found.
- `conflicting`: Two or more credible sources disagree.

When in doubt, preserve both source values and explain the conflict.
