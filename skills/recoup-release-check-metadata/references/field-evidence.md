# Metadata evidence and readback

Inspect the exact release edition and ordered tracks before comparing fields. A repeated ISRC
can belong to multiple releases; one track's correction does not rewrite every edition.
Keep party IDs/aliases, contributor roles, work links and provider IDs separate. Same-title
recordings, covers, remixes and namesakes need exact identity evidence. Conflicting credits
remain sourced observations until the user or an authoritative source supports a decision.

The template has three independently sourced layers per field:

- Intended: the supplied source value, its authority and source/version/locator.
- Receipt: what was actually requested, acknowledged or accepted by which provider,
  for which payload/version, account, destination and operation; include raw status.
- Observed: the value visible at the exact destination/date/territory and retrieval
  coverage; include URL/record ID and locator. An unavailable field is not a missing credit.

Return statuses such as no_difference_in_checked_field, conflicting_sources,
not_exposed, not_checked, requested, provider_accepted, observed_correct or
observed_different. Keep the layers independently; never promote a whole catalog to
observed_correct from one receipt. If a receipt names an old payload/source version,
flag superseded evidence and request a fresh scoped comparison. Retain prior observations.
An observed credit does not prove ownership, signed splits, a registry mandate or payment.

A correction packet names exact entity/edition/track, field, current observation,
proposed value, supporting source, destination and unresolved authority. Returning it
is preparation only. A request to check credits/metadata grants no permission to contact
anyone, submit corrections, enroll monetization or alter a roster. Use the separate
existing-release action workflow for explicitly requested delivery changes; preserve its
operation receipt when checking a later outcome.

Synthetic review cases: a distributor accepts a producer correction while two destinations
still expose the old role; one destination does not expose the role at all; a shared ISRC
appears on an original album and reissue with different ordered membership; a changed
source split sheet invalidates only comparisons depending on that version.
