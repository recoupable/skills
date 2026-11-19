# Entitlement workpaper export

Use this branch after `scripts/calculate-entitlements.py`. It exports that helper's
supported contractual-entitlement/recoupment result; it is not a general statement,
remittance, bank or data-room exporter. The generic case report remains an evidence
index, not a source of monetary totals. Scripts ship alongside this skill.

If a saved result already exists, reuse it with its original input; **do not rerun
the calculator over that result**. Export it directly to a new directory:

```bash
python3 scripts/build-royalty-workpaper.py --input entitlement-input.json --result entitlement-result-v1.json --as-of 2026-11-18 --output-directory private-workpaper-v1
```

If a new calculation is required, choose a new versioned directory. The calculator
itself overwrites its output, so the exclusive `mkdir` below must succeed before
it runs. If that directory exists, select another version; never reuse or clear it.
Retain the exact input version alongside its result receipt.

```bash
mkdir entitlement-run-v2 && python3 scripts/calculate-entitlements.py --input entitlement-input.json --output entitlement-run-v2/result.json
python3 scripts/build-royalty-workpaper.py --input entitlement-input.json --result entitlement-run-v2/result.json --as-of 2026-11-18 --output-directory private-workpaper-v2
```

Inspect the calculator status before exporting. A failed new calculation does not
justify replacing a historical result.

A partial calculation is exportable: unresolved rows retain unknown amounts and
require the private result's detailed blockers. An invalid top-level input or a
result that does not match recomputation with JSON types preserved is refused before creating output.
Do not replace historical results to make them pass; retain old outputs and make a
new version with its original inputs. Input/result paths can be anywhere authorized;
the destination must not exist. No source file is modified. If a write fails, the
new partial destination is removed so the same version path can be retried.
A final manifest identifies successful completion; do not consume an in-progress
directory.

## Files and interpretation

- `entitlement-lines.csv`: exact basis, rates, expected/reported amounts and signed
  variance, with currency, period, rule version alias and evidence references.
- `calculation-bridge.csv`: ordered intermediate steps, not additive earnings.
  Resolve each row's complete evidence list through `line_ref` in the entitlement
  schedule; the bridge retains currency, period, rule, order and freshness without
  repeating that potentially large list for every adjustment.
- `recoupment-accounts.csv`: opening/movements/earnings/closing/payable bridge, with
  the exact eligible line references and their periods. The calculator does not
  supply a balance date; it remains explicitly unknown, not the report date.
- `unresolved.csv`: unsupported line/account references and unknown amounts. Reasons
  remain in the hash-bound private result to avoid exporting arbitrary source prose.
- `evidence.csv`: source-version digests, supplied current-version digests, check
  dates and current-as-supplied/stale/unknown states.
- `workpaper.json`: authoritative exact decimal values and null unknowns, all
  schedules and calculation controls. Negative CSV cells have a leading apostrophe
  for spreadsheet formula safety; never recalculate from the display CSV.
- `report.md` and `manifest.json`: readable scope, limitations, file hashes, input
  hashes and calculator/exporter/helper hashes. No source path or original is copied.

The exporter compares the entire saved result with the existing calculator. It
adds no new financial formula, FX conversion, rounding step or recovery aggregate.
Recoupment reuses earnings already shown in entitlement lines. A variance and a
later payable/payment are not separate recoveries. No totals are inferred from
case findings or cause IDs; shared-cause recovery deduplication is outside this
export, so no monetary recovery total is emitted.

CSV schedules always retain their full fixed header, including when no rows are
calculated. An empty schedule is not a passed control.

## Optional source-version inventory

Without `--evidence inventory.json`, evidence freshness is **unknown**, even when
arithmetic matches. The inventory is a supplied review receipt, not live access:

```json
{
  "schema_version": "1",
  "sources": [{
    "evidence_ref": "synthetic-statement:row-2",
    "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "current_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "checked_on": "2026-11-18"
  }]
}
```

Supply an entry for every relevant `evidence_refs` value, including terms,
adjustments and recoupment movements. `source_sha256` identifies the exact source
version used in the calculation; `current_sha256` identifies the version observed
by the authorized reviewer. Different non-null hashes mean stale. Equal hashes
with `checked_on` on the same parsed calendar date as `--as-of` mean current **as supplied**, never independently
verified. Missing entries/hashes or older checks mean unknown. Future check dates
are refused. Source control totals and authenticity remain not verified by this
exporter. Hashes must be lowercase SHA256 strings (numeric JSON values are rejected);
values can be null for unknown.

Identifiers and evidence strings are exported as `kind:SHA256(UTF-8 original)`.
For example, resolve an `evidence:` alias by hashing the original `evidence_refs`
strings in the private input matching manifest `input_sha256`. Rule version aliases instead hash canonical JSON of the validated calculator
result's `rule_version`: Python `json.dumps(value, sort_keys=True,
separators=(",", ":"), allow_nan=False)` with its default ASCII escaping. Thus
numeric `1` hashes `1`, while string `"1"` hashes the quoted JSON string `"1"`;
booleans remain distinct too. The exact private rule remains in the input, parsed
with the calculator's existing exact-decimal input contract. This lets another
authorized session reproduce the output without publishing source locations,
account references, titles, free-text blockers or source prose. Hash aliases are
not anonymization; the financial rows and hashes still require a private reviewed
destination. No export approval authorizes sharing, publication or provider action.
