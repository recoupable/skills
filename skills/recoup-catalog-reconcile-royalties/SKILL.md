---
name: recoup-catalog-reconcile-royalties
description: "Reconcile music royalty statements, contractual earnings, remittances and relevant bank receipts with source controls and explained exceptions. Use for 'reconcile these publishing royalties', 'why did my royalty income drop', 'check my producer royalties', or a context-qualified royalty deposit match. Works from statements alone; generic bank payments and unrelated invoices do not trigger this skill."
---

# Reconcile royalties

Produce reproducible accounting workpapers for the requested question. Distinguish
reported earnings, contractual entitlement, accepted adjustments, remittances and
bank cash. None is automatically newly recovered money.

Read `references/catalog-contracts.md` and the applicable branches in
`references/accounting-workflow.md`. Scripts ship alongside this skill; inspect
their `--help` for supported input formats before processing a new source. File
work does not require a deal, valuation, full catalog import or bank connection.

## Select only the needed branches

| User question | Minimum branch | Useful stopping point |
|---|---|---|
| Clean or compare these statements | Source normalization and controls | Controlled ledger, coverage and exceptions |
| Did my publisher/label account correctly? | Contractual accounting | Clause-linked entitlement/recoupment bridge and unknowns |
| Why did royalties change? | Comparable-period analysis | Supported components and unresolved hypotheses |
| Did this royalty payment arrive? | Remittance and receipt allocation | Matched amounts, residuals and confidence |
| Did this sync/TV use get accounted for? | License/cue-sheet comparison | Identified uses, applicable terms, accounting evidence and gaps |
| Check royalties after this admin transfer | Effective-date and collection-tail comparison | Nonduplicated old/new reporting and unresolved continuity |

Use an established case to interpret continuation messages. "Did these payments
reach my bank?" without music context requires identifying the payments first.
"I sent the email" records a known case event; it is not a new reconciliation or
permission to send another message.

## Build the workpapers

1. Establish payee/role, relevant rights, providers, periods, currencies and the
   requested accounting question. Preserve statement period, usage period, issue
   date and actual payment date separately. A report date is not a payment date.
2. Inventory source files and versions with `templates/source-coverage.csv`.
   Preserve original values and row references; inventory archive members and
   missing sheets/periods. Revision, reversal and replacement exports need explicit
   relationships. Reimporting the same bytes must not create fresh earnings.
3. For ZIP batches of UTF-8 CSV/TSV, use `scripts/normalize-royalty-statement.py`
   with `--archive`; its `--output` must be a new bundle directory. Read
   `references/normalization.md` for limits, member receipts and partial/error
   states. Normalize only formats the available helper actually supports. Inspect ambiguous
   headers, currencies, amount basis and classifications before accepting results.
   Keep every source row accounted for as a detail, control/summary, header/note or
   excluded row with a reason. Empty files and failed controls are not clean data.
4. Record `templates/control-totals.csv` by currency, source version and amount
   basis. Retain sub-cent precision until the documented aggregate/settlement
   rounding step. Do not add mixed currencies or treat unknown amounts as zero.
5. Run the selected branches in `references/accounting-workflow.md`. Use the local
   deterministic helpers where their supported schemas match the evidence; keep
   unresolved terms or unsupported provider semantics explicit. Never force every
   line from one provider into one right, income type or contract calculation.
6. Diagnose differences through identity, mandate, territory, usage/reporting lag,
   revisions, adjustments, recoupment, reserves and payment allocation before
   labeling an underpayment. Unexplained disappearance is a supported exception;
   it is not, on its own, a collectible debt.
7. Produce `templates/exception-queue.csv` and `templates/reconciliation-report.md`.
   Link each result to its source versions, terms, calculation and control status.
   Where bank evidence is unnecessary, complete the statement work without it.

## Financial and evidence boundaries

- Preserve raw negative or greater-than-100-percent statement values when they may
  represent corrections or provider conventions. Investigate their basis; do not
  silently clamp them to ownership percentages.
- Registry observations or a public stream-rate model cannot establish contractual
  entitlement. Use supplied agreements/amendments and actual accounting evidence.
- Compare PRO usage at program/episode/cue/use level where available. Separate
  base credits, thresholds, bonuses, premiums and retroactive adjustments; uncertain
  repeatability belongs in a scenario, not a presumed missing payment.
- Supplied P&L or tax-summary totals can corroborate scoped aggregates. They do not
  prove every royalty line or justify unrelated tax advice.
- Match remittances to receipts with references, payee, currency, dates and documented
  fee/FX allocations. Provider "Paid" is not bank-posted cash. Partial, combined,
  reversed and unidentified receipts retain their own states.
- Potential shortfall, accepted adjustment and bank cash are separate columns.
  Never add a historic earning and its later payment as two recoveries.

## Resume and next stage

Use `python3 scripts/catalog-case.py status --file CASE_FILE` and the source-linked
records in `references/catalog-contracts.md` when resuming. A newer statement or
amendment invalidates affected workpapers; preserve prior versions and unrelated
completed checks. The report must allow another authorized session to reproduce
the result without this chat.

For supported adverse states, hand off the specific provider, objects, periods,
calculation basis, evidence gaps and requested remedy to a claim-resolution stage.
Do not send a demand, change registrations or promise recovery from a reconciliation
request. `fixtures/evaluation-cases.json` supplies synthetic branch tests.

For a named provider, read `references/catalog-providers/index.md` and only its
applicable family/profile. The dated registry separates documented preparation
from implemented transports and live verification; refresh current account rules
before claiming provider validation or executing an operation.
