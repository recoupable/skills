# Proposal design and copy framework

This is a reusable two-page layout. All company-specific content, pricing, commitments, and brand
inputs come from the selected engagement. No fees or service promises are standard defaults here.

## Design

Page one explains the problem, desired outcome, and approach. Page two presents the investment and
next steps. Keep the before/after panels parallel and the investment rows easy to compare. The
sample colors and dot motif are neutral layout choices; adapt them to the workspace's `DESIGN.md`.
`BRAND_CSS` can define approved local font faces and `--brand-body-font`; use workspace font files,
not a path into the plugin author's computer. Recheck pagination after changing fonts or copy length.

## Copy

Open with the client's stated problem and one verified observation. Describe the desired outcome
without promising an unapproved result. Explain only the approach relevant to this scope.

**Fictional example:** Cedar Lantern Studio receives briefs through several inboxes. Its proposed
pilot collects the required fields in one intake flow, with a coordinator reviewing every draft.
That is a proposed workflow, not a measured saving or a promise about ownership.

Tiers may differ by capacity, scope, or support when the approved offer calls for it. Use the actual
approved numbers and terms in every tier slot. Do not invent unlimited access, same-day service,
cancellation rights, project bands, spending limits, or ownership to make an offer reassuring.
Compare against an alternative only when that comparison is supported.

## Slot contract

All slots in `proposal-template.html` must be resolved. `DOC_TITLE` is the outcome-led title.
`TIER_1_*` through `TIER_3_*` each contain NAME, PRICE, PERIOD, DETAIL, and FIT.
`STEP_1_*` through `STEP_4_*` each contain NAME and DETAIL.
`COMMERCIAL_TERMS` comes from the approved offer and relevant agreement.
`BRAND_NAME`, `BRAND_TAGLINE`, `AUTHOR_NAME`, and `BRAND_CSS` come from workspace brand inputs.
The remaining slots hold client/contact/date, lead paragraphs, now/next bullets, close anchor,
and three agreed next steps. Empty optional values must be intentional, not unfilled tokens.

Text values need HTML escaping. Only reviewed markup belongs in rich-content slots; `BRAND_CSS`
is stylesheet content, not arbitrary client-supplied text. Verify the rendered result before delivery.
