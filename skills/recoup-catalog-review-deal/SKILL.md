---
name: recoup-catalog-review-deal
description: Review and underwrite a proposed music catalog transaction using seller evidence. Build earnings eligibility, NPS/NLS scenarios, concentration, a deal dashboard or an investment memo. Use for acquisition, sale or financing review; royalty statements alone do not imply a deal. Review does not contact the seller, negotiate, accept terms or execute transfers. Public-data estimates and standalone royalty reconciliation have separate entry points.
---

# Recoup Catalog — Review Deal

Catalog deal review end to end. **review** runs the full diligence pipeline; ingest /
value / dashboard / report are the stages (each runnable alone). Work lives in a deal
workspace `deals/{deal-id}/` whose `source/` is **immutable evidence** (never write
into it). The workspace schema is `references/deal-workspace.md`; the scaffold is
`templates/deal-workspace/`. Deterministic math + validators ship in `scripts/`
(invoke relatively).

## Mode: review (the full diligence pipeline — gated)

1. **Scaffold** `deals/{deal-id}/`. Treat `source/` as immutable.
   Write derived results to the working folders; never overwrite original evidence.
2. **Ingest** → run **ingest** mode.
3. **Value** → run **value** mode.
4. **Dashboard** → run **dashboard** mode.
5. **Report** → run **report** mode if the user wants the IC memo / financing pack /
   seller report PDF.
6. **Completion gate (don't claim "ready" until all pass):**
   `python3 scripts/run-deal-checks.py deals/{deal-id}` exits clean;
   `build-deal-readiness.py` is not `blocked`; `assumptions.yaml` +
   `evidence-ledger.json` exist; findings closed/accepted/listed; every memo claim
   traces to evidence; `python3 scripts/validate-dashboard.py deals/{deal-id}` returns
   `status: ok`. Run these checks before claiming completion. Pausing for a
   background job, missing input, or an external system is allowed; state what
   remains pending without claiming the package is ready.

## Mode: ingest (clean the data room)

Normalize messy statements/rights/metadata into the canonical schema
(`references/canonical-schema.md`, `references/cleaning-rules.md`,
`references/normalization.md`; checklist `references/data-room-checklist.md`):
`auto-column-map.py`, `normalize-royalty-statement.py` (`extract-pdf-statement.py` for
PDFs), `dataroom-hygiene-scan.py`, `build-file-manifest.py` +
`build-manual-review-queue.py`, `calculate-concentration.py`. Validate with
`validate-normalized-ledger.py` + `validate-findings-evidence.py`. Never silently
coerce ambiguous rows — queue them for manual review.

## Mode: value (full valuation — needs ingested files)

Project value with `references/valuation-framework.md`:
`calculate-nps-nls-bridge.py`, `calculate-concentration.py`; apply decay, recoupment,
reserves; build downside/base/upside scenarios. Layer the deep-dives:
`royalty-audit.md`, `rights-review.md`, `pro-performance-income.md`,
`financing-underwrite.md`, `seller-prep.md`, `post-close-admin.md`, `red-flags.md`.
For public-data-only, use recoup-catalog-estimate-value.

## Mode: dashboard (the customer-facing DASHBOARD.html)

Author with creative freedom, then **gate it**:
`python3 scripts/validate-dashboard.py deals/{deal-id}` must return `status: ok`
(also run `run-deal-checks.py`). Do not present a dashboard that fails validation.

## Mode: report (IC memo / financing pack / seller report → PDF)

Assemble from the dashboard + workpapers using `references/output-templates.md`,
export one shareable PDF. **Every claim must trace** to `evidence-ledger.json` or
`assumptions.yaml`.

## Evidence and bounded completion

Read `references/catalog-contracts.md` for the shared case and typed evidence
contract. Keep factual ownership separate from the interest offered in this deal:
excluded, retained, encumbered or unverified income never silently sets ownership
to zero. Build an eligibility schedule by asset, right, territory, date, income
stream and evidence. An expiring administrator can affect future collection without
ending underlying ownership. Missing termination evidence is a gap, not a termination.

Use `calculate-entitlements.py` for explicitly evidenced formula components and
`reconcile-remittances.py` for remittance-to-receipt allocations when required.
The NPS/NLS bridge remains a reported-to-adjusted bridge; it is not an independent
proof of entitlement. Keep unsupported contract interpretation as a scenario or
open dependency. Aggregate concentration only within comparable currency, period
and income basis. Do not annualize a partial period without an explicit assumption.

A requested value, dashboard or report update can finish at that stage. State its
input versions, completed controls and residual gaps; do not label the whole deal
ready unless the full review gate passes. A generated PDF is a private review
artifact until the user authorizes a destination. Seller outreach, negotiation,
acceptance and post-close operations require their own requested action scope.
`references/post-close-admin.md` supplies review considerations and handoff fields,
not authority to execute those actions from this review.

## Guardrails

- **`source/` is immutable evidence** — never write into it.
- **Completion is gated** — `run-deal-checks.py` clean, readiness not `blocked`,
  `validate-dashboard.py` ok before "ready".
- **Every claim traces to evidence** — no unsupported numbers.
- **Determinism where it counts** — royalty math runs in `scripts/`, not by hand.

## References & scripts

- `references/` — deal-workspace, deal-workflow, canonical-schema, cleaning-rules,
  normalization, data-room-checklist, valuation-framework, royalty-audit,
  rights-review, financing-underwrite, post-close-admin, pro-performance-income,
  red-flags, output-templates, methodology, recoup-api, seller-prep.
- `scripts/` — ingest/normalize, calculate-*, validate-*, run-deal-checks,
  build-deal-readiness. Ship alongside this skill; invoke relatively.
