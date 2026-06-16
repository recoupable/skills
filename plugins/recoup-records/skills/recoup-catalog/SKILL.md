---
name: recoup-catalog
description: Review, value, and package a music catalog deal — or quickly estimate a catalog's worth from public data. Modes — review (one-command end-to-end diligence: ingest → value → dashboard → report), ingest (clean/normalize a messy data room of royalty statements + rights files), value (full valuation from seller files — NPS/NLS, concentration, decay, scenarios), dashboard (the customer-facing DASHBOARD.html), report (IC memo / seller cleanup / financing pack → shareable PDF), estimate (value a catalog/album/song from public streaming data only, no seller files), and demo (run it on a synthetic catalog). Use for "review/underwrite this catalog", "clean these royalty statements", "catalog valuation", "NPS/NLS multiple", "build the deal dashboard", "write the IC memo", "what's this catalog worth from public data", or "deal demo". Source files are immutable; completion is gated.
---

# Recoup Catalog

Catalog deal review end-to-end, plus a public-data quick estimate. **review** mode
runs the full diligence pipeline; the other modes are the stages (each runnable
alone); **estimate** is the no-seller-files shortcut. The work lives in a deal
workspace `deals/{deal-id}/` whose `source/` is **immutable evidence** (never
write into it).

The workspace schema is `references/deal-workspace.md`; the scaffold is
`templates/deal-workspace/`. Deterministic math + validators ship in `scripts/`
(invoke relatively, e.g. `python3 scripts/calculate-nps-nls-bridge.py`). Reference
deep-dives (valuation, royalty audit, rights, financing, seller-prep, red-flags,
schema, cleaning, methodology) ship in `references/`.

## Mode dispatch

| The user wants… | Mode |
|---|---|
| "review/underwrite/do diligence on this catalog deal", full run | **review** (default) |
| "clean/normalize royalty statements", "ingest the data room" | **ingest** |
| "value the catalog", "NPS/NLS multiple", "projection/scenarios" (has files) | **value** |
| "build/refresh/QC the dashboard" | **dashboard** |
| "write the IC memo / financing pack / seller report", "export the PDF" | **report** |
| "what's this catalog worth from public data" (NO seller files) | **estimate** |
| "deal demo", "show me a sample deal" | **demo** |

**Key fork:** with **seller files** (a real data room) → ingest/value/review.
With **only public/streaming data** (no files) → **estimate**. Pick by what inputs
exist.

## Mode: review (the full diligence pipeline — gated)

End-to-end, ending in a validated, shareable package. Phases:

1. **Scaffold** `deals/{deal-id}/` from `templates/deal-workspace/`. Treat
   `source/` as immutable (a PreToolUse hook blocks writes to it on Claude Code).
2. **Ingest** → run **ingest** mode (normalize statements, build the canonical
   ledger, file manifest, hygiene scan, manual-review queue).
3. **Value** → run **value** mode (NPS/NLS bridge, concentration, scenarios).
4. **Dashboard** → run **dashboard** mode (build + validate `DASHBOARD.html`).
5. **Report** → run **report** mode if the user wants the IC memo / financing
   pack / seller report PDF.
6. **Completion gate (do not claim "ready" until all pass):**
   - `python3 scripts/run-deal-checks.py deals/{deal-id}` exits clean.
   - `build-deal-readiness.py` is **not** `blocked` (output to
     `workpapers/readiness-check.md`, not customer-facing).
   - `assumptions.yaml` and `evidence-ledger.json` exist.
   - Material findings in `findings/findings.json` are closed, accepted, or
     explicitly listed open — never silently dropped.
   - Every memo claim traces to an `evidence-ledger.json` entry or an
     `assumptions.yaml` entry (no unsupported claims).
   - `python3 scripts/validate-dashboard.py deals/{deal-id}` returns `status: ok`.

   On Claude Code a Stop hook enforces this gate; elsewhere it's your job.

## Mode: ingest (clean the data room)

Normalize messy royalty statements, rights files, metadata exports into the
canonical schema (`references/canonical-schema.md`, `references/cleaning-rules.md`,
`references/normalization.md`; checklist in `references/data-room-checklist.md`):

- `python3 scripts/auto-column-map.py` — map a statement's columns to canonical.
- `python3 scripts/normalize-royalty-statement.py` — emit the normalized ledger;
  `python3 scripts/extract-pdf-statement.py` for PDF statements.
- `python3 scripts/dataroom-hygiene-scan.py` — flag gaps/dupes/encoding issues.
- `python3 scripts/build-file-manifest.py` + `build-manual-review-queue.py` —
  inventory + the human-review queue.
- `python3 scripts/calculate-concentration.py` — early revenue concentration.
- Validate with `validate-normalized-ledger.py` + `validate-findings-evidence.py`.

Never silently coerce ambiguous rows — queue them for manual review.

## Mode: value (full valuation — needs ingested files)

From the normalized ledger, project value with the framework in
`references/valuation-framework.md`:

- `python3 scripts/calculate-nps-nls-bridge.py` — Net Publisher/Label Share bridge.
- `python3 scripts/calculate-concentration.py` — concentration risk.
- Apply decay, recoupment, reserves; build downside/base/upside scenarios.
- Layer the deep-dives as needed: `royalty-audit.md`, `rights-review.md`,
  `pro-performance-income.md`, `financing-underwrite.md`, `seller-prep.md`,
  `post-close-admin.md`, and `red-flags.md` (the must-not-miss issues).

Requires a real ingested workspace. For public-data-only, use **estimate**.

## Mode: dashboard (the customer-facing DASHBOARD.html)

Build/refresh/QC the executive `DASHBOARD.html`. Author it with full creative
freedom on layout, then **gate it**: `python3 scripts/validate-dashboard.py
deals/{deal-id}` must return `status: ok` (also run `run-deal-checks.py` and the
`validate-*` suite). Do not present a dashboard that fails validation.

## Mode: report (IC memo / financing pack / seller report → PDF)

Assemble the memo from the dashboard + workpapers using
`references/output-templates.md`, then export a single shareable PDF. **Every
claim must trace** to `evidence-ledger.json` or `assumptions.yaml`. Memo types:
IC memo (buyer), seller-cleanup report, financing pack, post-close admin plan.

## Mode: estimate (public data only — no seller files)

Value a catalog/album/recording from **public/streaming data alone** — no data
room required. This is the clean-room cousin of value:

- `python3 scripts/fetch_album_tracks.py` — pull the catalog from public sources.
- `python3 scripts/estimate.py` — estimate streams→revenue→value per
  `references/methodology.md` (uses `references/recoup-api.md`).
- `python3 scripts/build_report.py` — assemble the estimate report.

Be explicit that this is a **public-data estimate** (wider error bars than a
seller-file valuation), and state the assumptions.

## Mode: demo

Run **review** on the bundled synthetic catalog so a first-time user sees an
executive dashboard fast (~60s). Use the demo fixtures; don't require real files.

## Guardrails

- **`source/` is immutable evidence** — never write into it.
- **Completion is gated** — don't call a package "ready" until `run-deal-checks.py`
  is clean, readiness isn't `blocked`, and `validate-dashboard.py` says `ok`.
- **Every claim traces to evidence** (`evidence-ledger.json`) or a labeled
  assumption (`assumptions.yaml`) — no unsupported numbers.
- **Determinism where it counts** — royalty math, concentration, NPS/NLS bridges
  run in `scripts/`, not by hand.
- **estimate ≠ valuation** — public-data estimates carry wider error bars; say so.

## References & scripts

- `references/` — deal-workspace, canonical-schema, cleaning-rules, normalization,
  data-room-checklist, valuation-framework, royalty-audit, rights-review,
  financing-underwrite, seller-prep, post-close-admin, pro-performance-income,
  red-flags, output-templates, methodology, recoup-api.
- `scripts/` — ingest/normalize, calculate-*, validate-*, run-deal-checks,
  build-deal-readiness, and the estimate trio (estimate/fetch_album_tracks/
  build_report). All ship alongside this skill; invoke relatively.
