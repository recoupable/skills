---
name: recoup-release-add-release
description: "Add a release from a supported release link or distributor export and show its available details and ordered tracks, with missing information clearly labeled. Use for \"add this release\", \"put this album in Recoup\", or \"add this distributor release export\". Saves through supported Recoup operations when available; does not distribute music or plan a campaign."
---

# Add a release

Read `references/music-business-records.md` before starting; it defines supported
file-review and hosted-save routes, source handling and completion checks.

## Result

Help the user find this release and work with its tracks again. Return its title,
credited artists, release date and precision, identifiers, artwork reference and ordered
track list where supported, plus the saved Recoup record or a labeled local worksheet.

## Workflow

1. Identify the supplied release link/export and intended workspace. For a file, read
   its sheet/header structure before mapping; for a URL, confirm provider and release
   type. Do not substitute an artist page, playlist or guessed album for the input.
2. Inspect existing releases in that workspace. Reuse a verified same-provider release
   ID; retain uncertain matches for review. A reissue, edition or alternate product
   may be a separate release even when its title and songs match.
3. On the hosted route, discover the saved-release list, submit and read operations
   from the current tool catalog or REST contract. A link-only result remains “link
   saved; tracks not collected”. Inspect the actual collection capability and any
   paid scope before gathering metadata. The user's request to add a release covers
   ordinary read-only lookup for that release, as described in
   `references/music-business-records.md`; paid or broader collection requires
   separately authorized scope. Use a verified provider release ID and supported
   pagination. Report retrieved observations separately from tracks actually saved
   in the release case. A track-only link does not authorize importing an entire album.
4. On the supplied-export route, capture release/product IDs and each track's disc,
   position, title/version, credited artists and supplied recording IDs, retaining
   source rows. Preserve repeat tracks and disc order; never deduplicate track slots
   simply because an ISRC repeats. Do not claim every distributor format is supported.
5. Confirm pagination and reported track counts before presenting a complete track
   list. Preserve individual unavailable tracks and unsupported fields explicitly.
6. Save through an available authorized release/import operation and read it back;
   otherwise produce the worksheet in the private workspace and name the missing
   hosted step. Adding an observed collaborator never adds them to the roster.

## Handoff

Show **release added** only after the hosted record is read back; show **link saved**
for locator-only intake or **release worksheet prepared** for local file work. Include
track coverage (for example, 8 of 10 source positions), missing fields and one concrete
next step. Do not declare release readiness, verify ownership, upload masters, deliver
to DSPs or generate a rollout plan.

Example: “Add this distributor export” returns one release with its 12 ordered track
positions and source rows; absent writer splits remain unknown and are not fabricated.
