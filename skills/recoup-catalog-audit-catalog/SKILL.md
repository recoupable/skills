---
name: recoup-catalog-audit-catalog
description: "Audit a music catalog's rights, registrations, identifiers, agreements and delivery assets against supplied and accessible evidence. Use for 'audit my catalog', 'check my catalog before a sale', 'find rights or registration gaps', or 'verify this catalog after a transfer'. Produces scoped findings and remediation requirements; does not submit corrections, contact counterparties or reconcile royalty payments."
---

# Audit a catalog

Return an evidence-linked condition report for the actual checked perimeter. A
completed audit can contain unresolved problems. It does not certify title,
worldwide registration, sale readiness or permission to remediate.

Read `references/catalog-contracts.md` for source versions, case records and
separate evidence/action states. Read `references/audit-checks.md` for the checks
that apply to the user's scope; do not load unrelated service procedures.

## Establish the perimeter

1. Identify the represented party, the one work or repertoire being reviewed,
   relevant rights, territories, dates and purpose. A writer, publisher, estate,
   label or adviser can start from files; a Recoup artist ID or public release is
   not a prerequisite. For "transfer", establish which ownership, administration,
   collection or distribution change is being checked.
2. Preserve supplied source versions and row/page/clause/asset references. Prefer
   already connected sources or supplied exports; request only evidence needed for
   the next consequential conclusion. Record inaccessible sources as unchecked.
3. Create or resume the existing private case. Use `templates/scope.md` to capture
   requested and excluded checks, population, sample selection and source cutoff.
   Do not silently expand a selected 15-work review into a complete catalog audit.

## Perform the review

4. Resolve compositions, recordings, release editions, parties and provider accounts
   separately. Build `templates/identity-crosswalk.csv`; preserve alternative matches
   until writers, identifiers, versions and other evidence establish identity. One
   recording can embody multiple works; one work can have many recordings.
5. Build `templates/rights-schedule.csv` from documents and explicit assertions.
   Keep ownership, administration, collection mandate and software access distinct.
   Compare interests only on the same share basis, right, territory and period.
   Registry parent/administrator rows are not additional ownership shares.
6. Apply the relevant checks in `references/audit-checks.md`: chain of title and
   splits; mandates and restrictions; registrations and copyright records;
   permissions and exits; delivered uses and identifiers; documentary and technical
   assets. Capture each check in `templates/check-results.csv`, including passes,
   unknowns and justified exclusions, not just discovered failures.
7. Compare source evidence with current accessible observations. An absent public
   search result means "not found in this search on this date"; it does not prove
   non-registration. A registration or credit is an observation, not independent
   title evidence. Keep unresolved conflicting evidence visible.
8. Record material exceptions in `templates/findings.csv`: exact object and scope,
   evidence and version, observed condition, supported consequence, uncertainty,
   severity, owner and evidence needed to resolve it. Group one root cause affecting
   many records; do not multiply the same potential monetary exposure across checks.

## Deliver and hand off

Use `templates/audit-report.md` with the identity crosswalk, rights schedule,
source/service coverage, check results, findings and `templates/asset-register.csv`
when assets are in scope. Deliver files in the user's selected private workspace.

- Report checked / applicable / unknown counts by check and service. Keep sample
  findings separate from whole-population conclusions. A condition rating is
  optional; disclose checks and weights, and never turn unknowns into passes.
- Give each finding a concrete next-stage requirement: document/identity correction,
  registration preparation, substantive claim resolution, release correction or
  royalty reconciliation. A missing registration alone is not a quantified loss.
- Preserve ownership when an asset is excluded from a proposed deal. Assess
  transfer eligibility and retained interests in separate fields.
- For post-transfer reviews, compare both source and target records, dates and
  retained interests. Target acceptance alone does not prove source release,
  distributor propagation or financial continuity.
- Complete the analytical stage with unresolved findings explicitly listed. Do not
  send emails, register works, change claims, alter delivery or launch monitoring
  because an audit identified a need.

## Case persistence and verification

Scripts ship alongside this skill. Run `python3 scripts/catalog-case.py --help`
for the installed commands; use `hash --input SOURCE_FILE` for real file digests,
and `status --file CASE_FILE` before resuming. Use the record format in
`references/catalog-contracts.md` when saving sources, assessments and findings.
Check the revision before a write. Changed source evidence requires refreshing
affected conclusions, not overwriting the original audit history.

`fixtures/evaluation-cases.json` contains synthetic walkthroughs, including a
composition-only entry, namesakes, parented claims, missing assets and a transfer.
They are test inputs and expected review criteria, not evidence about any catalog.

For a named provider, read `references/catalog-providers/index.md` and only its
applicable family/profile. The dated registry separates documented preparation
from implemented transports and live verification; refresh current account rules
before claiming provider validation or executing an operation.
