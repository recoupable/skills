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

## Creative direction and working mode

Reuse authorized Recoup context, then selected files/artwork/screenshots/links,
then accessible public references for actual gaps. Keep a private reference list
with the correct artist/release, source and purpose. Reference-only inspiration
does not automatically become production imagery. Use host capabilities honestly;
blocked Instagram access is a gap, not a completed review. Current customer
direction takes precedence over stale campaign context.

The three starting points are **established**, **rough idea**, and **none**.
Preserve an established world. Develop a rough idea faithfully. With no direction,
take creative responsibility and label the resulting world as a proposal.

**Run with it** lets the agent select a direction and continue. **Show me directions
first** pauses for a customer selection or feedback, then continues the agreed pack
without per-asset approval. Three distinct boards are useful when exploring from
zero; an established world normally needs one assembled direction. Only show real
supplied or actually generated boards as boards. A concept described in text remains
a concept. Automatic board generation and collection depend on available authorized
tools; do not claim the saved-state API creates them.

Where the actual pack schema exposes `creative_context`, use this optional object:

- `starting_point`: `established`, `rough_idea` or `none`.
- `working_mode`: `autonomous` or `guided`.
- `references`: up to20 items with distinct `id`, `title`, accessible HTTPS `url`,
  `media_type` (`image`, `document` or `link`), `source_kind` (`recoup`, `customer`,
  `public` or `generated`) and `usage` (`reference_only` or `production`).
- `directions`: up to3 items with distinct `id`, `name`, `concept`, optional
  `palette`, `typography`, real supplied `board_url` and `reference_ids` from this
  manifest. Keep concepts concise; the current API exposes their exact limits.
- `selection`: `direction_id`, `selected_by` (`customer` or `agent`) and an honest
  `decision_note`. It must reference a direction in this same brief.

An unresolved creative object can be saved, but cannot quote or generate final
assets. Guided mode requires the customer's direction selection; an agent choice
is not customer approval. Autonomous mode should have the agent choose and save
the world rather than restart a creative interview. Selection records a creative
choice, not spending approval. Existing budget authorization remains required.

Only image manifest items explicitly marked `production` and referenced by the
selected direction become generation inputs. Together with legacy explicit
`reference_image_urls`, the current limit is five distinct images. The source
manifest remains unchanged; the selected direction is projected into production
prompts and input snapshots. Updating direction/mode uses the same job's current
revision and invalidates the old quote. Do not carry an earlier production-image
projection back as newly supplied source references.

If the host's schema lacks this object, keep the checkpoint in the conversation
or supported local file, follow the selected review preference and do not send
unsupported fields or claim server-enforced direction selection is available.

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
