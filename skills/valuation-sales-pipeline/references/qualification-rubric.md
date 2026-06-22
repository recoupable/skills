# Qualification rubric — is this valuation lead worth our time?

Goal context: every pursued lead should plausibly contribute to **recurring revenue**
(Recoup Pro and/or a managed growth+recovery engagement). Score each lead on four axes,
then route it.

## The four axes

1. **Catalog size / value.** Does the catalog have real, sustainable earnings to grow and
   recover against?
   - Strong: established catalog — tens of millions of lifetime streams and a six-figure+
     estimated value.
   - Weak: tiny or zero-stream lookups, near-zero estimated value (often a fan typing in
     their own bedroom project, or a test/junk row).
   - **Don't trust the tool's number blindly on a large catalog** — a free run can exhaust the
     lead's credits partway and report a value built on only part of the catalog (Chilled Cat:
     ~27% measured, ~$290K shown vs ~$1.08M on the full catalog). If the lead has a deep catalog,
     check remaining credits and re-measure the full catalog before qualifying on value (see
     `references/recoup-valuation-api.md` → "Spotting a truncated free run").

2. **Relationship / authority.** Can this person actually say yes to an engagement?
   - Strong: `Owner/Operator`, `Label`, `Manager`.
   - Warm: `Collaborator` (released work with the artist; an insider).
   - Weak: `Fan/Other`, `Unknown`.

3. **Recency / intent.** Did they value recently, and how engaged are they?
   - Strong: valued in the last few days; burned a lot of credits / ran multiple lookups.
   - Weak: stale, single shallow lookup.

4. **Capacity to pay.** Is there a business behind it (label, management co., active
   independent artist) rather than a hobbyist?

## Routing

- **Pursue** — strong on size + authority, recent. Enrich the Attio profile, draft outreach
  + PDF, advance toward Pro / a pilot.
- **Backlog** — real catalog but weak relationship or smaller value. Leave at `New`; revisit
  if they re-engage. Note why.
- **Disqualify → Lost** — zero/near-zero catalog, a fan, or an internal/test row. Set the
  matching `lost_reason` so the funnel teaches you why leads don't convert.

## Revenue framing (set expectations honestly)

A six-figure catalog implies only roughly $24k–$36k/yr of net label share, so one catalog
rarely justifies a large standalone retainer. Paths to recurring revenue:

- **Pro subscription** — fastest, lowest-friction; pair with standing scheduled tasks
  (weekly trends, playlist alerts, monthly value-delta) for retention.
- **Managed growth + recovery engagement** — for owners/labels with multiple acts.
- **Risk-reversal pilot** — for the single strongest catalog: recover income, grow streams,
  deliver a buyer-ready data room, priced against a documented baseline.

## Internal / test rows to always disqualify

Leads on `@example.com` domains, or internal team emails, are seed/test data — never work
them as prospects.
