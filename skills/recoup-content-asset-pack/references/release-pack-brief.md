# Release pack: inline context and continuation

The customer's goal is usable music content, not a completed profile. Preserve
their job while acquiring only the information needed for the next useful step.
Keep known facts, customer assertions, sourced observations and creative proposals
distinct. A saved brief is useful only if production actually consumes it.

## Minimum brief

| Input | Reuse or ask | Safe handling of a gap |
| --- | --- | --- |
| Artist/title/exact recording | Supplied facts and selected authorized context | Ask only for missing identity; do not pick the first namesake or remix |
| Usable song audio | Selected upload or accessible recording | Obtain the real file/locator; never substitute or pretend a listening link is audio |
| Occasion | New release, anniversary, reissue, remix or rediscovery | Ask which occasion; propose evergreen rediscovery if the customer asks you to choose |
| Creative direction | Artwork, real posts, references, stated direction | Offer to propose a direction from the music; label it as new creative work |
| Primary action/platforms | Explicit goals, channels and destinations | Propose listen + Instagram/TikTok formats; do not invent a link or audience metrics |
| Constraints | Supplied restrictions and established brand preferences | Favor artwork/typography if no approved face reference; no invented likeness |
| Scope/budget | Requested deliverables + current quote | Show the complete scope and ceiling before paid generation |

For anniversaries, keep the original release date separate from the campaign
date. Obtain evidence for dated anniversary claims; never manufacture a date.
For a catalog, agree the selected recordings/campaign scope before batch work.
For an unreleased artist, Spotify history, analytics and past posts are optional.

If only audio was supplied, a compact first response is:

> I’ll build the pack around this song. Who’s the artist, and is this a new release,
> anniversary, remix or catalog push? Share artwork or a reference if you have one;
> otherwise I can propose a direction from the music.

Do not repeat fields already supplied. If the customer says “run with it,” use
visible creative defaults; do not fabricate facts. Do not require a brand book,
connected socials, valuation, catalog claim or complete dated release plan.

## Branches that preserve the job

| Situation | Next action |
| --- | --- |
| Connected, zero artists | Valid new account; prepare the same pack without forced artist creation |
| Not connected | Continue brief work, use host sign-in when needed, then resume that brief |
| Existing artist/context | Read authorized context; ask only unresolved creative questions |
| Thin or unavailable research | Use supplied evidence and explicit proposals; disclose gaps |
| New tools absent | Name the missing operation and retain the brief; do not export OAuth tokens or call the connection broken |
| Plan-only request | Produce the plan; no unrequested paid generation |
| Plan plus pack | Reuse the same brief and explicitly continue into production |
| Changed song/scope | Requote; old approval does not carry across silently |
| Timeout or partial failure | Read saved job/attempt state; keep successes; do not resubmit an uncertain paid attempt |
| Completed first result | Continue agreed batch; offer reusable profile/context save afterward |

## Pack tools and portable checkpoints

Prefer the connected pack tools when discovered. `prepare_release_pack` retains
the brief and returns readiness; `estimate_release_pack` quotes the selected work;
`generate_release_pack` uses the exact current quote/revision and approved ceiling;
`get_release_pack` returns progress; `retry_release_pack` targets failed work only.
`upload_release_pack_asset` takes explicitly selected source media, not unrelated
files. Use actual input schemas and returned identifiers, not guessed arguments.

Where a host supports files, a compact `pack-brief.json` can retain the current
intent and facts before connection. In a host without files, retain those values
in the conversation and then the authenticated job. Neither checkpoint contains
credentials. It must be possible to resume without rerunning full onboarding.

Read/compile selected saved Context evidence if available; do not recollect all
research or enroll an artist just to compile a brief. Never send a private brief
to permanent public storage as a convenience export.

## First usable result and completion

First value means a reviewed asset with the correct music and a relevant caption.
It is not login, artist creation, a prompt list or a render request. A representative
first asset can be the first stage of the same approved job, without a second
mandatory customer approval. Honor an explicitly requested preview checkpoint.

Finish with previews, media links, captions, a manifest, and remaining gaps.
Distinguish unique creative pieces, carousel components and aspect-ratio variants.
Do not automatically publish or schedule. Every model-mediated step still needs
actual host acceptance; instruction/routing checks alone do not prove first-use
quality or that the current host exposes the required tools.
