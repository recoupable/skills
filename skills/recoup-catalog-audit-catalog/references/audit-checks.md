# Structural audit checks

Select checks against the agreed perimeter. For each applicable object/check pair,
record `pass`, `finding`, `unknown`, or `not_applicable` with evidence and a reason.
"Not checked" is unknown. A pass is scoped to the inspected evidence and time.

## Identity and catalog structure

| Check | Compare | Meaningful exception |
|---|---|---|
| ID-01 Composition identity | Work identifiers, title variants, writer identities and source lineage | A same-title work belongs to different writers; an identifier links contradictory works |
| ID-02 Recording identity | ISRC/provider IDs, version, duration and recording evidence | A live/remix/version has been conflated with the studio recording |
| ID-03 Embodiment | Recording-to-work links, medley/sample arrangements and source support | A recording is matched to a namesake work or only one of several embodied works |
| ID-04 Release membership | Edition, UPC/provider ID, ordered tracks, release dates and territories | Two editions are collapsed; track order or identifiers disagree |
| ID-05 Parties and accounts | Legal party, alias, role, IPI/ISNI/provider IDs and account owner | An alias is treated as a new rights owner or login owner as beneficial owner |

Missing identifiers are missing evidence, not proof that a work is invalid. An
unreleased composition can be reviewed without a recording, ISRC or public profile.
Identifiers are typed claims with sources; do not manufacture them to fill a schema.

## Rights, control and agreements

| Check | Evidence | Review question |
|---|---|---|
| RT-01 Interest basis | Executed split/assignment/license documents plus amendments | Who asserts or holds which right, on what share basis, territory and dates? |
| RT-02 Share consistency | Comparable interest rows, exceptions and provider conventions | Do totals conflict on the same basis, or are writer/publisher/collection shares being mixed? |
| RT-03 Chain of title | Relevant executed conveyances and schedules | Are assets, parties, dates and conditions connected, or does the chain have a specific gap? |
| RT-04 Administration | Agreement and termination/renewal provisions | Does the administration/collection mandate cover this right, territory and period? |
| RT-05 Restrictions | Exclusivity, reversion, consent, lien/security and assignment terms in supplied documents | Which contemplated uses or transfers need a condition satisfied? |
| RT-06 Exit evidence | Authentic notices, releases, waivers and required signatures | Is departure/termination supported, and does a collection tail remain? |
| RT-07 Permissions | Sample/interpolation, featured artist, producer, artwork, name/image or other relevant permissions | Is the actual contemplated use covered, including scope/term restrictions? |
| RT-08 New-use authority | Supplied AI-training/voice/likeness/data or other special-use license terms | Does authority cover the proposed use, or is the conclusion unresolved? |

An asserted share, contractual ownership, registered share, administered share and
deal-eligible share are different facts. Do not delete ownership because a deal
excludes an asset. Do not construe missing termination evidence as a terminated
interest. Record ambiguous contract interpretation as unresolved and identify the
exact clause/document needed; this review does not certify legal enforceability.

## Registrations, mandates and actual uses

Build a service coverage matrix: objects × applicable right/territory/provider ×
operation checked. Include the period of membership/mandate; former and current
affiliations can both be correct for different periods. Account access is separate.

- Compare signed/source interests with supplied or authorized registry observations:
  named writers/publishers, identifiers, work/recording links, applicable shares,
  territory, effective dates and observed status. Preserve raw provider share basis.
- Treat parented administration/collection rows as relationships, not additional
  beneficial ownership. A sum over every visible parent/child row is not a split check.
- Distinguish composition performance, mechanical, recording performance/neighbouring
  rights, distribution and sync/UGC uses. A PRO record is not complete mechanical
  registration evidence; a DSP listing is not a rights registry.
- Where requested, inspect copyright registration and transfer recordation separately.
  Match the registered material and claimant/transfer scope to the actual object.
  Record search scope and unavailable records. Missing public results cannot certify
  that protection or registration is absent across jurisdictions.
- Compare known delivered uses with the applicable collection/delivery routes.
  Missing coverage is an operational finding; quantify money only from controlled
  financial evidence in a separate reconciliation.
- For sync/TV use, inventory supplied license, cue sheet, program/episode/use data
  and accounting references. Missing cue-sheet or performance evidence is a precise
  documentation gap, not automatically a missing payment.

## Assets and document availability

Use `templates/asset-register.csv` only for requested assets. Inspect technical
properties with available file/media tools and record the method: filename alone
does not prove format, bit depth or usable audio. Capture master, stems, instrumental,
artwork, delivery package and other required asset versions, locations and access.

Record separate evidence for an inspected primary file, an inspected backup and an
owner-reported backup. The requested technical specification controls; 24-bit audio
can be an applicable check without being a universal pass criterion for every asset.
An inaccessible file is unknown; a missing master is not restored or generated by
the audit. Do not publish private storage URLs in an external report unnecessarily.

## Prioritization and coverage

Use severity to communicate the evidenced impact on the user's stated purpose:

- Critical: a supported conflict or missing prerequisite blocks the contemplated
  action, such as disputed authority for the requested transfer.
- High: a material rights, mandate or asset gap affects the defined scope.
- Medium: a material discrepancy needs correction/verification but does not establish
  immediate loss or invalid rights.
- Low: a documented administrative discrepancy with limited demonstrated impact.

Severity is not a legal conclusion. Confidence and impact remain separate. Record
`not_quantified` where exposure is unknown, and link related findings to one root
cause so a financial amount is counted once.

For each check publish population, applicable count, inspected count, pass count,
finding count, unknown count and excluded count. If a sample was used, record how it
was chosen and its limits. Do not extrapolate an unrepresentative sample into a
catalog-wide failure rate. Optional scores must disclose weights and how unchecked
items affect coverage; reporting counts is sufficient.

## Post-transfer inspection

Compare signed/evidenced effective boundaries and retained interests against source
provider release, target provider acceptance and actual observed records. Inspect
distribution separately from registry/admin changes. If a source still collects a
valid historic tail, distinguish that from an unauthorized current mandate. Hand
old/new statements to reconciliation without assuming all post-close receipts belong
to the buyer. The audit can close analytically while residual transition items remain.
