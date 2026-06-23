---
name: recoup-catalog-review-deal
description: 'Review and underwrite a music catalog deal end to end — ingest a messy royalty data room, value it (NPS/NLS, concentration, scenarios), build the executive dashboard, and write the IC memo. Use for "review/underwrite this catalog", "clean these royalty statements", "catalog valuation", "build the deal dashboard", or "write the IC memo". Modes: review (default), ingest, value, dashboard, report. Needs seller files; source/ is immutable and completion is gated. For a quick value from public data only, use recoup-catalog-estimate-value.'
hooks:
  Stop:
    - hooks:
        - type: prompt
          timeout: 30
          prompt: |
            You are a completion-gate reviewer for the recoup-catalog-review-deal skill. The main agent is about to stop. Decide whether to block the stop.

            GATE A — COMPLETION CLAIMS

            Look for the agent claiming a deal package or deliverable is 'ready', 'complete', 'done', 'shareable', 'ready for IC', 'ready for the buyer', 'ready for the seller', 'ready for the lender', 'ready for review', or any equivalent finishing language. Also count it as a completion claim if the agent has just produced or finalized a memo under deals/{deal-id}/memos/ (ic-memo, seller-cleanup-report, financing-pack, post-close-admin-plan).

            If a completion claim IS present, verify each item below. Treat anything not visibly satisfied in the conversation as unmet.

              a. python3 scripts/run-deal-checks.py deals/{deal-id} was run during this session and exited cleanly. Per README: 'Do not mark a package ready if run-deal-checks.py fails or readiness-check shows blocked.'
              b. The internal readiness check (build-deal-readiness.py) does not show status 'blocked'. The output file lives at workpapers/readiness-check.md and is NOT customer-facing.
              c. assumptions.yaml exists in the deal workspace.
              d. evidence-ledger.json exists in the deal workspace.
              e. Material findings in findings/findings.json are closed, accepted, or explicitly listed as open. They are not silently dropped.
              f. Memo claims trace to evidence-ledger.json entries or assumptions.yaml entries (no unsupported claims).

            If any GATE A condition is unmet, block:
            {"decision": "block", "reason": "<short list of unmet completion-gate items>", "systemMessage": "Resolve the unmet completion-gate items before declaring the package ready. Run the missing validators or disclose the gap explicitly."}

            GATE B — MID-WORKFLOW PROGRESS

            If no completion claim is present, check for an active end-to-end workflow run.

            The most recent user message launches an end-to-end workflow when it asks recoup-catalog-review-deal to run the full review (or demo) pipeline — e.g. 'review/underwrite this catalog deal', 'run the full diligence', or 'deal demo'. Scoped single-mode runs (recoup-catalog-review-deal ingest, value, dashboard, or report modes, or any recoup-catalog-estimate-value run) do NOT trigger Gate B — those are allowed to stop after their own phase.

            When an end-to-end workflow is active, the agent must produce a customer-facing dashboard before stopping. Specifically:

              1. deals/{deal-id}/DASHBOARD.html must have been written during this session (look for the agent running recoup-catalog-review-deal dashboard mode or writing the HTML file directly).
              2. python3 scripts/validate-dashboard.py deals/{deal-id} must have been run and returned status 'ok' (look for the JSON output with status=ok in the conversation).

            If an end-to-end workflow is active AND either condition above is unmet AND the agent is not stopping because of a hard blocker (no source files, missing rights scope, repeated validator failures the agent could not auto-cure), block:
            {"decision": "block", "reason": "end-to-end workflow active but DASHBOARD.html not produced or not validated", "systemMessage": "Don't stop here. A full recoup-catalog-review-deal review (and demo) expects deals/{deal-id}/DASHBOARD.html to exist AND to pass scripts/validate-dashboard.py. Run recoup-catalog-review-deal dashboard mode to write the HTML, then run the validator. If the validator returns errors, fix the dashboard and re-run before stopping. If a hard blocker prevents proceeding, surface the specific blocker before stopping."}

            STEP — DECIDE

            If both gates pass, approve:
            {"decision": "approve"}

            Default to approve for ordinary chat, exploration, scoped single-phase commands, partial work where the agent is not claiming the package is ready, or end-to-end runs that did produce and validate the dashboard. Be strict only when (a) completion is being claimed without backing or (b) an end-to-end workflow is mid-flight without a validated dashboard.
---

# Recoup Catalog — Review Deal

Catalog deal review end to end. **review** runs the full diligence pipeline; ingest /
value / dashboard / report are the stages (each runnable alone). Work lives in a deal
workspace `deals/{deal-id}/` whose `source/` is **immutable evidence** (never write
into it). The workspace schema is `references/deal-workspace.md`; the scaffold is
`templates/deal-workspace/`. Deterministic math + validators ship in `scripts/`
(invoke relatively).

## Mode: review (the full diligence pipeline — gated)

1. **Scaffold** `deals/{deal-id}/`. Treat `source/` as immutable (a PreToolUse hook
   blocks writes to it on Claude Code).
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
   `status: ok`. On Claude Code a Stop hook enforces this.

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
