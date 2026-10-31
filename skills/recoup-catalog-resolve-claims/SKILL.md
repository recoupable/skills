---
name: recoup-catalog-resolve-claims
description: "Investigate and pursue documented music-rights or royalty exceptions with a named provider or counterparty: competing catalog claims, substantively denied corrections, missing accounting, held royalties or disputed allocations. Use for 'resolve this publisher overclaim', 'challenge this denied royalty correction' or 'help resolve my publisher's payment hold'. Technical filing rejection repair stays in catalog registration. Ordinary registrations, generic claims, insurance, legal takedowns and settlement are outside this entry point."
---

# Resolve a rights or royalty exception

Turn an evidenced adverse state into a supported case, a bounded requested remedy,
authorized provider communication and a tracked disposition. Correction, accepted
entitlement and cash receipt are independent outcomes.

Read `references/catalog-contracts.md` and `references/resolution-workflow.md`.
There must be a music object/right/royalty and a responsible provider or counterparty;
"resolve my claim" without that context is insufficient to select this workflow.

## Establish the case

1. Resume the known private case or identify the provider, claimant/represented
   party, exact objects, rights, territories, periods and adverse state. Find existing
   case IDs and sent communications before preparing another contact.
2. Classify the actual problem: conflicting share/title claim, adverse match outcome,
   denied substantive correction, withheld funds, missing accounting or disputed
   royalty allocation/payment. Ordinary existing-share claims and first recording-work
   matches belong to registration; routine schema/field repairs stay with the original
   registration or delivery operation.
3. Gather the minimum support for the requested remedy using
   `templates/resolution-packet.md`: source versions, current provider state, relevant
   agreements/mandates, affected records, prior correspondence and unresolved facts.
   A historical hold does not establish a current payable balance. Do not fabricate
   missing consent or adjudicate contested ownership.
4. For money, use controlled royalty workpapers and current ledger/remittance evidence
   where available. Distinguish reported earnings, calculated entitlement, discrepancy,
   requested accounting, accepted adjustment and received cash. When entitlement is
   unresolved, ask for records/explanation instead of asserting a debt amount.

## Prepare the remedy and communication

5. Verify the exact provider process for this claim type and role. Identify required
   evidence, disclosure recipients, deadlines supplied by the provider and available
   appeal/escalation route. Ordinary registry claims, UGC monetization enrollment,
   copyright removal and contested title are not interchangeable procedures.
6. Prepare the precise remedy and a short correspondence draft using
   `templates/correspondence.md`. List each attachment and why the recipient needs
   it; minimize unrelated data. Preserve material contrary evidence. Separate factual
   requests from proposed legal conclusions or financial demands.
7. Send/file only when existing explicit authority covers the recipient, channel,
   attachments and requested action. Do not ask again when the same action is already
   authorized. A materially changed remedy, recipient, disclosure or binding legal
   step needs matching authority; provide the concrete revised packet first.

## Track responses and disposition

8. Capture actual sent/submitted evidence, provider case ID, exact payload/version
   and expected next step in `templates/case-history.csv`. If the user says "I sent
   the email", record a user-reported sent event with the available details. Do not
   resend it or convert that report into independently inspected evidence.
9. Classify responses as acknowledgment, request for evidence, partial response,
   accepted correction, denied remedy, proposed adjustment or closure. Respond to
   the actual outstanding issue using the current evidence. Preserve earlier versions
   and the requested versus provider-granted scope.
10. Before retrying an uncertain send/submission, inspect the sent record or provider
    case. Resume from the latest receipt instead of replaying the workflow. Create
    reminders or monitoring only when requested, using the host's existing scheduler.
11. Close the supported outcome in `templates/disposition.md`: corrected records
    need external readback; accepted adjustments need provider accounting evidence;
    payments need separate receipt matching. Acknowledgment, sent mail or metadata
    correction cannot establish recovered cash. Keep residual issues and future
    periods open when their evidence remains unavailable.

## Boundaries and portable continuity

This stage can prepare a useful case even when provider submission is unavailable.
State the unsupported route and the exact human/provider action remaining. Legal
adjudication, infringement/removal notices, settlement, waivers and execution of
agreements are outside its default scope; preserve the packet for an appropriate
authorized handoff without performing those actions.

Scripts ship alongside this skill. Use `python3 scripts/catalog-case.py status
--file CASE_FILE` and the record formats in `references/catalog-contracts.md` to
resume sources, findings, actions, attempts and outcomes. New evidence can change
the case, but does not erase the earlier correspondence or authorize a new send.

`fixtures/evaluation-cases.json` includes synthetic financial and nonfinancial cases,
partial responses, missing authentic consent and no-duplicate-send continuations.

For a named provider, read `references/catalog-providers/index.md` and only its
applicable family/profile. The dated registry separates documented preparation
from implemented transports and live verification; refresh current account rules
before claiming provider validation or executing an operation.


For local MLC overclaim evidence preparation, read `references/local-preparation.md`
and run the co-located `scripts/prepare-provider-packet.py` with an existing
`resolve_claims` action. It preserves exact remedy/disclosure and source versions;
missing inputs block the packet. Complete mappings remain unverified preparation,
not authority to contact, amend, relinquish or upload. No case state is changed.
