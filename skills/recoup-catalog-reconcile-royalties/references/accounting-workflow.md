# Accounting branches and controls

Run only branches needed by the question. A missing contract can block entitlement
while statement normalization and cash matching still produce useful results.

## Source normalization

Scripts ship alongside this skill. Inspect their current help before use:

```bash
python3 scripts/normalize-royalty-statement.py --help
python3 scripts/calculate-entitlements.py --help
python3 scripts/reconcile-remittances.py --help
```

For a supported profile, a typical invocation is:

```bash
python3 scripts/normalize-royalty-statement.py --provider publisher-admin --input statement.csv --output ledger.csv --column-map column-map.json --controls controls.json
```

Choose the actual supported profile and explicit source-column map when needed.
The local `fixtures/subcent-statement.csv`, `fixtures/subcent-column-map.json` and
`fixtures/subcent-controls.json` form a complete synthetic example of that profile.
Do not guess the semantics of a provider-specific column merely because its name
resembles "net". Keep the original file and the helper's source receipts/row journal
with the generated ledger. A valid file extension does not prove successful parsing.

Before accepting a normalized source:

1. Confirm exact member/sheet, header row, row count and source statement identity.
   Preserve separate statement revisions; determine replacement versus additive
   adjustments from evidence. A repeated digest is the same import, not new income.
2. Determine the amount basis for each financial column: usage quantity, gross,
   commission, expense, withheld tax, reserve, owner net, balance or remittance.
   Missing owner net remains missing; the source may still support another purpose.
3. Preserve income/right classifications per row. Mixed mechanical, performance,
   sync and recording income can appear in one provider's file. Classify unknown
   codes only with documentation; retain raw codes and unknowns otherwise.
4. Explicitly establish currency. Symbol-only or blank currency is unresolved until
   supported by the file/account evidence; a provider name is not a USD instruction.
5. Reconcile per-currency, per-basis source totals against parsed detail and classified
   control/summary rows. Avoid counting a total both as detail and as a check.
   Count headers/notes/exclusions in source conservation rather than silently deleting
   them. A failed or unavailable control belongs in the report.
6. Retain exact decimal text; round only at a documented aggregate/settlement step.
   For large exports, use the streaming path where supported; process archive members
   deterministically and retain controls. Never silently sample to fit memory.

Store output in `templates/control-totals.csv`; `pass` means an actual evidenced
comparison met a disclosed tolerance. `unavailable` is distinct from `fail` or `pass`.

## Contractual entitlement and recoupment

Build a clause-linked workpaper for the specific payee and right. Use actual source
terms and amendments: earnings base, percentage/basis, allowable deductions, sequence,
reserve rules, advance, opening recoupment balance, cross-collateralization scope,
effective dates, payment cadence and audit provisions where relevant.

Separate:

- What the statement reports.
- What the supported terms calculate.
- What depends on an unresolved term, opening balance or accounting interpretation.

Use `calculate-entitlements.py` only for its documented supported calculation model.
A contract outside that model needs a transparent additional workpaper, not a forced
approximation labeled contractual. Include source/term references for each input.
Do not invent a zero opening recoupment balance or silently net advances across
unrelated works/parties. Producer participation and letters of direction can have
different payors/bases; a streaming gross estimate cannot substitute for the agreed
base. Overpayments and clawbacks are negative/offset scenarios, not recoveries.

Preserve the relationship between withheld reserves, releases, deductions and later
adjustments so one economic amount is not counted twice. An unsupported entitlement
stays unknown; it cannot become a requested debt amount in the next stage.

`fixtures/finance/entitlement-input.json` is a complete synthetic input example:
versioned rules, supported earnings lines, signed adjustments and separate recoupment
accounts. Use it to inspect the schema; replace every synthetic source with the real
evidence for the user's workpaper. Adjustment/movement IDs must remain stable across
reimports. The implemented model covers explicit fixed-rate terms and documented
effective periods; escalators and cross-collateralization remain outside its supported
calculations. Run:

```bash
python3 scripts/calculate-entitlements.py --input entitlement-input.json --output entitlement-result.json
```

## Changes and anomalies

Compare like-for-like right/provider/payee/currency/territory and both usage and
statement periods. Reconcile missing quarters/months and changed reporting coverage
before reporting growth or decline. Identify duplicate exports, correction/reversal
pairs, foreign exchange, scope changes, recoupment/reserve moves and delayed reporting.

For PRO statements, retain program/episode/cue/use information when supplied. Break
out base credits, weights, thresholds, bonuses, premiums and retroactive adjustments
using documented definitions. A one-time bonus is not a recurring annual entitlement.
When a factor cannot be separated from the source, label the comparison limited.

For sync, compare the exact license/use, fee, due trigger, split, payment and scope
against supplied accounting. A cue sheet documents a use; it does not establish an
identical amount in every PRO distribution. Separate license fees from downstream
performance income and avoid duplicate aggregation.

For a suspected gap, report the observed discontinuity, comparable denominator,
known explanations, remaining hypotheses and the specific evidence that could
resolve them. Do not infer fraud or a debt from an unexplained difference.

## Remittance and bank receipt allocation

Use `reconcile-remittances.py` for its supported allocation schema. Identify the
payee/legal entity, remittance reference, currency, issued/value date and amount.
Match against only the relevant supplied bank receipts with posting date, account
scope, reference and amount; do not require unrelated banking access.

Allow one-to-many and many-to-one allocations with explicit amounts. Use the exact
provider payment ID or other strong reference where possible; date/amount alone is
candidate evidence. Account for fees, withholding, FX and refunds only with support.
Different currencies require a documented conversion basis, not equality of numerals.
Do not allocate more than the available remittance or receipt amount; report residuals.

Provider "Paid" establishes provider status. A bank-posted matching receipt supports
cash received. A pending bank item, reversal or user recollection retains its own
evidence state. Unrelated service invoices stay outside royalty totals even when the
same counterparty sends both.

`fixtures/finance/remittance-input.json` supplies a complete synthetic example with
statement/remittance/receipt objects and explicit allocation edges. Preserve each
source record ID as well as its local object ID to detect duplicate evidence. The
default completion checks both statement-to-remittance and remittance-to-receipt;
set `completion_scope` to the actually requested branch when bank matching is outside
scope. Keep unallocated amounts and unverified receipts visible in the result. Run:

```bash
python3 scripts/reconcile-remittances.py --input remittance-input.json --output remittance-result.json
```

## Administration/ownership transition continuity

Record conveyed and retained interests, executed effective dates, mandate end/start,
source/target provider roles and contractual collection tails. Compare by usage
period and contract terms, not simply cash date. Old administrators can legitimately
report after the transfer; new and old exports can overlap.

Link duplicate/replaced accounting rows and preserve offsets rather than counting
both as new earnings. Source release, target acceptance and financial continuity
need separate evidence. Missing transfer consent blocks the affected action but does
not prevent a useful historical statement comparison.

## Report and escalation

Use `templates/reconciliation-report.md` and `templates/exception-queue.csv`.
Show gross/net/entitlement/remittance/receipt separately and by currency; an aggregate
converted view needs the explicit rate source, rate date and method. Supplied P&L or
tax-summary controls can corroborate totals but do not replace row-level checks.

Every material exception identifies the facts, input/source versions, supported
amount (or unknown), calculation, scope and next evidence/remedy. A claim-resolution
handoff must preserve uncertainty and include enough information to request records
without overstating liability. No provider contact or demand is sent by this stage.
