---
name: recoup-deal-start
description: One-command end-to-end music catalog deal review. Use whenever the user types `/recoup-deal-start`, says "review this catalog", "analyze this music catalog deal", "value this catalog", "do diligence on this deal", "underwrite this catalog", or asks for a full catalog acquisition / seller-prep / financing / post-close review. Scaffolds the workspace, normalizes the data room, runs analysis, builds an agent-authored DASHBOARD.html, validates it, and drafts the IC memo without stopping for permission between phases. The default front door for the recoup-deals.
argument-hint: [deal-id] [--workflow buy-side|seller-prep|financing|post-close]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, Task]
---

# Deal Start — full review

This is the **default starting point** for any music catalog deal. It runs
the full workflow end-to-end and ends with a single executive HTML
dashboard the user can open. **Do not stop and ask the user what to do
next between phases.** Run all phases. Stop only when:

- `DASHBOARD.html` exists, validated, plus the IC memo, OR
- A hard blocker prevents proceeding (no source files, no rights scope
  declared, validator returns critical errors that cannot be auto-cured).

If a phase produces partial output, surface what is partial in one line
and **keep going** with the rest of the catalog.

## Phases (run in order, do not pause)

### Phase 1 — Setup (≤30 seconds)

This skill owns workspace setup — no separate setup skill to call.

1. Confirm `workflow_type` (`buy-side` / `seller-prep` / `financing` /
   `post-close`) and `deal_id`. If not provided, ask once with a
   structured form; otherwise infer from the user's message. The
   workflow type selects the analysis deep-dive and report package used
   later (see "Deal-type modes" below).
2. Create or locate `deals/{deal-id}/` and copy
   `templates/deal-workspace/` into it.
3. Move any user-provided source files into `deals/{deal-id}/source/`.
4. Run `python3 scripts/validate-deal-workspace.py deals/{deal-id}` and
   announce the workspace path. Validator failures here are expected —
   they are the setup worklist.

Print one line: **"Workspace scaffolded at deals/{deal-id}/. Starting
ingest."** Do not list every templated file.

### Phase 2 — Ingest (≤2 minutes for a typical data room)

Use the `recoup-deal-ingest` skill.

1. `python3 scripts/build-file-manifest.py deals/{deal-id}` — classifies
   every file with `parse_status`, `likely_provider`, `likely_period`,
   `likely_currency`, and `rights_type_hint`.
2. For each file the manifest tags with a `likely_provider`, run
   `python3 scripts/normalize-royalty-statement.py --provider <key> --input <path> --output deals/{deal-id}/normalized/royalty-ledger.csv`.

   **If the normalizer returns `status: "partial"`, do not stop and do
   not ask the user.** Auto-recover with:

   ```bash
   python3 scripts/auto-column-map.py \
     --provider <key> \
     --input <path> \
     --output deals/{deal-id}/workpapers/column-maps/<source-file>.json
   ```

   If `auto-column-map` returns `status: "ok"`, re-run the normalizer
   with `--column-map workpapers/column-maps/<source-file>.json`. If it
   returns `status: "needs_review"`, log the file in
   `findings/manual-review-queue.md` with the missing critical fields
   and continue with the rest of the catalog.

3. `python3 scripts/build-manual-review-queue.py deals/{deal-id}` — surfaces
   the X-of-Y coverage line. **Quote the `summary_line` verbatim** in
   your phase recap (e.g. "29 of 88 files contributed financial data;
   50 require manual review"). This is the user's first AHA moment —
   it tells them exactly how the data room held up.
4. `python3 scripts/dataroom-hygiene-scan.py deals/{deal-id}` — merge any
   high-strength matches into `findings/findings.json`.
5. `python3 scripts/calculate-concentration.py deals/{deal-id}/normalized/royalty-ledger.csv --assumptions deals/{deal-id}/assumptions.yaml --output deals/{deal-id}/workpapers/concentration-analysis.json --emit-finding-output deals/{deal-id}/findings/concentration-finding.json` — auto-emits a `valuation` finding when the threshold trips. Merge into `findings/findings.json` with a real `evidence_ids` reference to the concentration workpaper.
6. `python3 scripts/run-deal-checks.py deals/{deal-id}` — every
   validator must pass before moving on. If it fails, fix the specific
   error (usually missing evidence IDs on auto-emitted findings) and
   re-run; do not skip.

Print one line: **"Ingest complete. {N} of {M} files contributed financial
data. {K} findings open. Starting analysis."**

### Phase 3 — Analysis (parallel sub-agents)

Dispatch all three specialist sub-agents **in parallel** (single message
with three Task calls):

1. `royalty-audit-analyst` — gross-to-net, duplicate imports, retroactive
   adjustments, suspicious spikes.
2. `rights-chain-reviewer` — split sheets, assignments, samples,
   reversions, transferability.
3. `valuation-sensitivity-analyst` — assumptions visibility, NPS/NLS
   bridge support, concentration impact, decay.

Merge each agent's findings into `findings/findings.json` with proper
`evidence_ids`. After merge, re-run `run-deal-checks.py` to confirm
nothing broke.

### Phase 4 — Modeling — write the workpapers

Build the JSON workpapers that feed the dashboard. The dashboard skill
will read these in Phase 5; the validator's truth set is built from
them. Strong workpapers → easier-to-defend dashboard claims.

1. `workpapers/nps-bridge.json` and `workpapers/nls-bridge.json` —
   each with `metric`, `reported_amount`, and a `bridge` array of
   `{label, amount, running_total}` rows. Use
   `scripts/calculate-nps-nls-bridge.py` against a JSON input or write
   them directly from the royalty audit (the `recoup-deal-analysis`
   skill's royalty-audit playbook).
2. `workpapers/valuation-summary.json` — must contain at minimum:

   ```json
   {
     "normalized": {"nps": <number>, "nls": <number>},
     "scenarios": {
       "downside": {"value_low": <n>, "value_high": <n>},
       "base":     {"value_low": <n>, "value_high": <n>},
       "upside":   {"value_low": <n>, "value_high": <n>}
     }
   }
   ```

3. `workpapers/recommendations.json` — **always write this**, the
   prioritized list of "what would tighten the bracket." Use the
   canonical category names: `Data improvements`, `More modeling`,
   `Story threads`. Each item has `priority` (`P0`/`P1`/`P2`), `ask`
   (the concrete next move), and `would_change` (why it's the right
   next move). The dashboard skill reads this as a starting point — it
   may restructure or override on the dashboard if the deal's story
   calls for different framing. Generate from the deal, not from a
   template; write the 2–6 items that would actually change this
   catalog's underwriting.

4. **Optional but encouraged when the catalog's story calls for it:**
   write deal-specific JSON workpapers — `recoupment-npv.json`,
   `bright-lights-decay.json`, `pro-decomposition.json`, anything else.
   The dashboard skill is free to pull these in and shape sections
   around them. The validator's truth set picks up any numeric values
   in any `workpapers/*.json` file, so values you write here become
   "trustworthy" for the dashboard automatically.

### Phase 5 — Build the dashboard (the AHA moment)

Use the `recoup-deal-dashboard` skill. **The agent owns this artifact.**
The skill teaches the contract: required sections, brand rules,
trust contract (every `$`-claim either matches a workpaper value or
carries `data-evidence` / `data-source` / `data-derived`), CDN
allowlist, and quality bar.

You have full creative freedom on layout, chart types, interaction
patterns (tabs, scenario sliders, accordions), narrative flow, and
depth. Use that freedom. Different catalogs deserve different shapes.
A concentration-driven catalog reads differently than a recoupment-
cliff catalog.

After writing `deals/{deal-id}/DASHBOARD.html`, run the validator:

```bash
python3 scripts/validate-dashboard.py deals/{deal-id}
```

If the validator returns `status: errors_found`, **read the errors,
fix the dashboard, re-run.** Do not skip. The Stop hook blocks the
agent from finishing if `DASHBOARD.html` does not exist or the
validator does not pass.

### Phase 6 — IC memo + readiness gate

Use the `recoup-deal-report` skill (it owns the written memo as well as
the PDF export).

1. Draft the memo that matches the workflow type into
   `deals/{deal-id}/memos/` — `ic-memo.md` for buy-side,
   `seller-cleanup-report.md` for seller-prep,
   `financing-pack.md` for financing,
   `post-close-admin-plan.md` for post-close — from the matching
   template under `templates/deal-workspace/memos/`. Pull every material
   number from the workpapers, not from prose memory.
2. Run the `deal-qc-reviewer` agent against the memo. If it returns
   `overall_status: "blocked"`, surface the blockers in the final recap
   but **do not silently rewrite the memo**.
3. `python3 scripts/build-deal-readiness.py deals/{deal-id}` for
   the internal readiness check (writes
   `workpapers/readiness-check.md` — analyst-facing only, not for the
   customer).

## Final recap (the landing card)

End with **exactly** this shape, populated from the actual run:

```text
✅ Deal review ready.

Headline:
  Normalized NPS run-rate $X.
  Normalized NLS NPV / run-rate $Y.
  Preliminary value bracket: $LOW (downside) – $HIGH (upside).
  N material blockers · K high-severity items · J review-needed items.

Open this first:
  deals/{deal-id}/DASHBOARD.html

Then if you want detail:
  deals/{deal-id}/memos/ic-memo.md          — IC memo draft
  deals/{deal-id}/findings/missing-files.md — what to ask the seller for
  deals/{deal-id}/findings/findings.json    — every structured exception

What I did NOT do (and why):
  <one bullet per honest gap, e.g. "skipped GEMA statement — needs
  manual column map; queued in manual-review-queue.md">

Next options:
  /recoup-deal-dashboard — refresh DASHBOARD.html + re-run QC after edits
  /recoup-deal-report    — refine the memo and export a shareable PDF
```

## Rules the agent must follow

- **Truthfulness over polish.** If a phase failed or skipped a file,
  say so in the recap. Never claim ingest is "complete" while
  `run-deal-checks.py` reports failures.
- **No mid-workflow stops.** If you finish Phase 2 and feel uncertain
  about Phase 3, run Phase 3 anyway. The user can stop you with a
  follow-up message.
- **One dashboard.** The customer-facing artifact is
  `deals/{deal-id}/DASHBOARD.html` — and only that. The markdown
  readiness check at `workpapers/readiness-check.md` is internal.
- **Source files are immutable.** Writes into `deals/{deal-id}/source/`
  are blocked by the PreToolUse hook. Write to `normalized/`,
  `workpapers/`, `findings/`, or `memos/`.
- **Demo data permissible.** If the user explicitly says "this is a
  demo, make up a data room" (or runs `/recoup-deal-demo`), generate
  realistic synthetic seller files into `source/` before Phase 2 ingest.
  Use canonical-format CSVs that the normalizer parses cleanly.

## Deal-type modes

The same six-skill workflow runs for every deal. The `--workflow` flag
(or the inferred workflow type) only changes which analysis deep-dive
and which report package get emphasized:

| Workflow | Analysis emphasis (`recoup-deal-analysis` reference) | Report package (`recoup-deal-report`) |
| --- | --- | --- |
| `buy-side` (default) | `rights-review.md` + `royalty-audit.md` | `ic-memo` |
| `seller-prep` | `seller-prep.md` | `seller-cleanup` |
| `financing` | `financing-underwrite.md` | `financing-pack` |
| `post-close` | `post-close-admin.md` | `post-close-admin` |

You do not switch skills for these — you run the same phases and pull
the matching reference/package.

## Power-user escape hatches

These commands exist for analysts who want to run a single phase only.
The plugin is six skills, one per workflow stage:

- `/recoup-deal-ingest` — Phase 2 only (normalize the data room).
- `/recoup-deal-analysis` — Phases 3–4 only (rights, royalty, valuation diligence).
- `/recoup-deal-dashboard` — Phase 5 + QC gate (build/refresh `DASHBOARD.html`, validate, run pre-share checks).
- `/recoup-deal-report` — Phase 6 (assemble the memo, export the shareable PDF).
- `/recoup-deal-demo` — `/recoup-deal-start` against bundled synthetic data.

Most users should run `/recoup-deal-start` and let it drive the whole
thing end-to-end.
