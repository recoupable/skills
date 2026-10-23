# Catalog diligence and operations coverage

Implementation candidate, checked 2026-10-22. This describes what is in the source
package; it is not a release announcement or a claim that provider accounts have
been operated. Tracking: [catalog epic](https://github.com/recoupable/app/issues/2277).

## Choose the stage by the requested result

| User result | Skill | Completion artifact |
|---|---|---|
| Bring source lists into a controlled catalog | `recoup-catalog-import-catalog` | Typed candidates, row dispositions, source hashes and versioned import receipt |
| Understand contractual obligations | `recoup-catalog-explain-contract` | Clause-linked terms, uncertainty and obligation schedule |
| Organize works, interests and administrators | `recoup-catalog-organize-publishing` | Works, parties, scoped interests, mandates and readiness gaps |
| Find defects and missing evidence | `recoup-catalog-audit-catalog` | Scoped audit, coverage matrix, evidence-linked findings and action backlog |
| Explain royalties, balances and receipts | `recoup-catalog-reconcile-royalties` | Exact-decimal ledger, entitlement workpaper, cash bridge and unresolved differences |
| Add, claim, match, amend or transfer records | `recoup-catalog-register-catalog` | Operation-specific packet; actual submission receipt and readback when independently obtained |
| Resolve a contested claim, hold or denied remedy | `recoup-catalog-resolve-claims` | Evidence packet, communication/attempt log, provider disposition and separately tracked financial effect |
| Correct or migrate an existing delivery | `recoup-release-manage-delivery` | Field diff or migration manifest, cutover gates and destination-specific observations |
| Decide whether/how to transact | `recoup-catalog-review-deal` | Eligible asset perimeter, controlled financial bridge, risk findings and deal conditions |
| Estimate a public-data scenario | `recoup-catalog-estimate-value` | Conditional observed-subset scenario with explicit unknowns; not verified royalty income |
| Inspect credits or release fields | `recoup-song-check-credits`, `recoup-release-check-metadata` | Intended versus provider-reported versus observed field comparison |

Each substantial stage has its own entry point and internal workflows. An ordinary
registration rejection repair stays in registration; an adverse competing-rights
claim or denied monetary remedy belongs in resolution. Initial distribution is
outside delivery maintenance. Review does not send messages or file claims.
“I sent it” resumes the known case with user-attested evidence; by itself it does
not activate a new stage. A bank inquiry needs royalty context to route here.

## Shared executable foundations

- Portable cases record exact source versions, rule versions, dependencies,
  immutable revision history and selective/transitive invalidation. Local
  revision checks prevent stale writers. A changed payload invalidates its
  recorded authority. Unknown external outcomes require reconciliation before retry.
- CSV/Markdown evidence exports exclude originals, locations, action payloads and
  authorization details. IDs and selected evidence descriptions remain private;
  choose an authorized destination. Human summaries are opt-in.
- Financial normalization streams CSV/XLSX rows, preserves sub-cent decimals and
  original currency, distinguishes report from payment periods, retains lineage,
  checks row conservation and emits source-control receipts. A two-million-row
  synthetic run matched exact USD controls at approximately 44 MiB peak RSS.
- Entitlement calculations support evidenced fixed formulas, effective periods,
  territories, commissions, adjustments and explicit recoupment movements.
  Escalators and complex cross-collateralization require reviewed workpapers.
- Remittance allocation separates statement net, payable/remitted amounts and bank
  receipts; preserves fees, FX evidence and returns; rejects duplicate allocations;
  and reports unsupported legs and nonzero residuals as unresolved.
- Revised statements with stable transaction keys can be held for controlled
  revision handling. Unkeyed overlapping periods require manual comparison;
  importing files is not proof they contain disjoint transactions.
- Hosted save/read/list case operations are a coordinated Database/API change,
  separate from this portable package. They store customer assertions with
  workspace access controls; they do not execute providers or recompute royalties.

## Provider coverage is per operation

The versioned registry in `references/catalog-providers/operations.json` contains
56 preparation profiles: 51 have official source references and five are explicitly
unverified readiness placeholders (Space Heater, ISWC, IPI, ISNI and UPC routes).
The source ledger has 45 dated references; inaccessible, route-only and excerpt-only
results are distinguished from fully read procedures. The registry is not a list
of 56 implemented integrations.

| Service family | Preparation/procedure coverage | Remaining execution gate |
|---|---|---|
| The MLC | New/existing work, shares, writer/member matching, transfer, overclaim | Current role, schema, mandate, receipt and item-level readback |
| US PROs | BMI work updates/share convention; ASCAP/SESAC/GMR account routes | Current access and procedure; inaccessible ASCAP detailed help remains a gap |
| Publishing administrators | Kobalt and Songtrust intake, corrections, statements and transitions | Account-specific portal/export requirements and downstream society confirmation |
| Recording societies | SoundExchange owner/featured/producer LOD; PPL and SENA role/territory distinctions | Eligible role, track-specific mandate and accepted record evidence |
| International composition societies | PRS, SOCAN and SACEM preparation/mandate routes | Current receiver rules and reciprocal/subpublisher chain; unavailable SACEM guide unresolved |
| Copyright | Application/recordation readiness and documentary issues | Jurisdiction-specific facts, authentic attestations, fees and authorized filing |
| Distributor/DSP/UGC | Existing-record corrections, migration gates, Spotify delivery chain, YouTube Content ID eligibility | Actual distributor/account capabilities and destination readback; channel access is not Content ID access |
| CWR/DDEX and identifiers | Version/receiver selection and acknowledgment distinctions | Current schemas, serializer/validator/transport and receiving-party acceptance |

Every profile currently states automated submission `not_implemented`,
authenticated readback `not_verified`, and live operation `not_verified`. Agents
may use a separately available and verified authorized connector or assisted route,
but this package itself supplies no provider write adapters. An unfamiliar service
can enter the same evidence workflow and return a useful prepared packet with a
named missing capability; it cannot inherit a green status from another service.

## Coverage of the diligence research

The [CDP homepage](https://www.catalogdiligencepartners.com/),
[buyer framework](https://www.catalogdiligencepartners.com/blog/music-catalog-audit-how-buyers-evaluate-risk),
[pre-acquisition checklist](https://www.catalogdiligencepartners.com/blog/pre-acquisition-checklist-music-catalog-investor),
[post-acquisition service](https://www.catalogdiligencepartners.com/post-acquisition-catalog-cleanup)
and [report guide](https://www.catalogdiligencepartners.com/blog/how-to-read-music-catalog-structural-reconciliation-report)
informed the research. The mapping below is Recoup's implementation design, not a
claim about CDP's contractual scope or a reproduction of its sample assessment.

| Research subject | Recoup owner and output |
|---|---|
| Asset perimeter, retained/conveyed rights, ownership versus administration | Audit + deal review: typed control and transaction eligibility schedules |
| Recording/work/release identities, ISRC/ISWC/UPC, aliases, IPI/ISNI, cross-system links | Import + focused credits/metadata checks + audit: candidate identities, crosswalk, conflicts and provenance |
| Splits, chain of title, executed agreements, producer/featured/sample clearances | Contract explanation + audit: clause-linked rights and missing-link findings |
| Term, territory, reversion, encumbrances, accounting duties and AI permissions | Contract explanation + deal review: evidence and conditions; counsel-dependent determinations remain unresolved |
| PRO, mechanical, neighboring and international collection coverage | Publishing organization + audit: mandate/coverage matrix; registration: specific correction packet |
| Revenue source completeness, attribution, suspended/unmatched income, sync and UGC | Reconciliation: controlled source ledger, expected-versus-reported workpaper and cash bridge |
| Missing releases, territorial availability, wrong versions and delivery state | Metadata check + delivery maintenance: exact destination differences and receipt/readback log |
| Masters, backups, stems and ancillary asset availability | Audit + delivery: manifest of available, missing and uninspected assets |
| Pre-sale, buyer/lender, estate and post-acquisition circumstances | Same stage skills with scoped party authority, baseline and transition manifest |
| Corrective work, transfer readback and continuing data changes | Registration/resolution/delivery: separate attempts, provider decisions, observed records and financial effects |
| Structural report, master reconciliation sheet, evidence room and residual issues | Versioned case/report exporter plus stage workpapers and unresolved-action schedule |

A score is optional presentation, not evidence. Findings sharing one root cause
must not be added into speculative recovery totals. Missing searches, absent
contracts and hypothetical leakage do not become monetary receivables.

## Verification and release gates

The package includes executable case/financial/import/estimate regressions,
registry-integrity checks, routing fixtures and standalone packaging checks.
Synthetic stage scenarios and provider decision cases are evaluation material,
not proof that every scenario or provider has been run. The independent cold
walkthrough exercised MLC transfer preparation and exact-decimal reconciliation
using only installed skill material and synthetic inputs. It performed no filing.

Before broader service claims: merge and release the coordinated changes; apply
the additive database migration before dependent API rollout; verify authenticated
HTTP/MCP scoping and withdrawal; run representative authorized real-account
operations and inspect provider records; verify later accounting/cash effects
separately. OpenAI/Claude directory approval and publication are separate release
steps. No real-account completion is established by the synthetic benchmark,
source-document checks or a green CI run.
