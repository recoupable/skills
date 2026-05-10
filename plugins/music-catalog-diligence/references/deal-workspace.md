# Deal workspace

A deal workspace is the operating folder for one catalog opportunity. It keeps
raw seller files separate from normalized data, workpapers, findings, and final
outputs.

## Folder structure

Use this structure unless the user already has a stronger convention:

```text
deals/{deal-id}/
├── source/
├── normalized/
├── workpapers/
├── findings/
├── memos/
├── assumptions.yaml
└── evidence-ledger.json
```

## Folder rules

### `source/`

Store raw data-room files exactly as received.

Rules:

- Do not edit files in `source/`.
- Do not rename files unless the original path is preserved in the manifest.
- Treat files as evidence, not working copies.
- Record checksums when possible.

### `normalized/`

Store parsed and cleaned structured data.

Common files:

- `data-room-inventory.csv`
- `canonical-catalog.csv`
- `royalty-ledger.csv`
- `rights-map.csv`
- `source-lineage.csv`
- `normalized-ledger-validation.json`

### `workpapers/`

Store calculations and intermediate analysis.

Common files:

- `nps-nls-bridge.json`
- `concentration-analysis.json`
- `valuation-scenarios.md`
- `recoupment-analysis.md`
- `pro-performance-analysis.md`

### `findings/`

Store structured diligence exceptions and red flags.

Common files:

- `findings.json`
- `missing-files.md`
- `rights-exceptions.md`
- `royalty-exceptions.md`
- `metadata-exceptions.md`

### `memos/`

Store human-facing outputs.

Common files:

- `ic-memo.md`
- `seller-cleanup-report.md`
- `financing-pack.md`
- `post-close-admin-plan.md`

## Deal assumptions

Use `assumptions.yaml` for values that affect analysis but are not directly
present in source files.

Examples:

- Buyer name.
- Deal type.
- Currency.
- Valuation date.
- Discount rate.
- Multiple range.
- FX source.
- Recoupment assumptions.
- Reserve treatment.
- Materiality thresholds.

Assumptions are allowed. Hidden assumptions are not.

## Evidence ledger

Use `evidence-ledger.json` to trace extracted facts back to source files.

Every material memo claim should map to one or more evidence entries or be
labeled as an assumption.

Minimum fields:

- `evidence_id`
- `source_file`
- `source_type`
- `locator`
- `extracted_field`
- `extracted_value`
- `confidence`
- `notes`

## Findings

Use `findings/findings.json` for structured issues. Each finding should include:

- Severity.
- Category.
- Affected assets.
- Evidence IDs.
- Issue.
- Valuation treatment.
- Follow-up.
- Status.

## Workspace lifecycle

1. Create the workspace with templates.
2. Copy seller files into `source/`.
3. Build a manifest and evidence ledger.
4. Normalize catalog and royalty data into `normalized/`.
5. Run deterministic checks into `workpapers/`.
6. Write structured exceptions into `findings/`.
7. Assemble memos from normalized data, findings, and assumptions.
8. Review with specialist agents.
9. Update status as items are cured or accepted.

## Completion gate

Do not call a deal package complete unless:

- `source/` is preserved.
- `evidence-ledger.json` exists.
- `assumptions.yaml` exists.
- Material findings are either closed, accepted, or listed as open.
- Memo claims trace to evidence or assumptions.
- Validation scripts have been run or missing validations are disclosed.
