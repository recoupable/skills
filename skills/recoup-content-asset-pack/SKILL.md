---
name: recoup-content-asset-pack
description: 'Create a release pack or content pack for a song: cohesive video clips, artwork, quote cards, a carousel, a visualizer and captions. Use for "create a release pack", "content pack", "30 posts for the launch", catalog rediscovery, an anniversary, a reissue or a remix campaign. Collect essential missing context inline, preserve the job through sign-in, and quote before paid generation. Stops at inspected assets; never posts. For a release plan or rollout schedule without media, use recoup-release-plan-rollout.'
---

# Recoup Content — Asset Pack

Turn the selected music and campaign occasion into a coherent pack the customer
can actually use. Keep **make this pack** as the active job throughout intake,
connection, production and recovery. Read `references/release-pack-brief.md` for
the minimum context and first-use branches. Do not explain the feature or send
the customer to general onboarding when they already asked you to make it.

## Procedure

1. **Keep the request, find the gaps.** Read the conversation, supplied audio,
   artwork and references first. Reuse authorized artist/release context when it
   exists; `references/workspace-context.md` describes local files, not a
   requirement to create them. If connected Context tools can read/compile a
   selected saved brief, use their actual schemas and coverage. Research is
   enrichment, not a gate. Do not import a whole catalog for one pack.
2. **Resolve the real recording.** Use the supplied audio or an explicitly
   selected accessible recording. A Spotify listening URL is not an audio file.
   Read `references/song-sourcing.md` only if the song is missing. Resolve remix
   and namesake ambiguity before production. Analyze available audio and choose
   a useful hook; metadata alone is not listening. Never substitute another song.
3. **Ask once, only for essentials.** Establish artist/title, usable audio,
   occasion, and direction/references or permission to propose a direction. Reuse
   anything already known. Offer clear defaults for audience, platforms and
   primary action; label them as proposals. No invented brand identity, lyrics,
   anniversary dates or metrics. Use `templates/pack-brief.json` as a compact
   checkpoint where files are supported; the host conversation and pack job must
   also work without a filesystem.
4. **Connect only when execution needs it.** Discover Recoup tools by name,
   description and schema. Use the host's connection UI if authentication is
   required, retain the brief, then resume **this** pack. An empty roster is a
   valid account. An existing artist, social connection, valuation, catalog claim
   or GitHub workspace is not a pack prerequisite. Never create a throwaway
   account, extract OAuth credentials or redirect into bulk roster onboarding.
5. **Prepare the same durable job.** Prefer `prepare_release_pack`,
   `get_release_pack`, `estimate_release_pack`, `generate_release_pack`,
   `retry_release_pack` and `upload_release_pack_asset` when actually exposed.
   Use their returned job IDs, revisions, readiness and next actions. A selected
   Context brief can be reused by ID; inspect coverage and fill essential gaps.
   Do not claim a newer tool exists on an older connection. If an operation is
   missing, name it, retain the brief and explain the specific next step. A
   missing REST credential does not invalidate working MCP authentication.
6. **Show direction + scope + complete budget.** Default to 15 creative pieces:
   eight clips, four quote cards, one artwork, one carousel and one visualizer,
   each with a caption. Adapt to the requested scope. Count a carousel as one
   piece; disclose its slides and format variants separately. Get the complete
   pack quote and spending approval before generation. Bind approval to the
   current input/revision and maximum budget. The legacy **GET**
   `/content/estimate` is advisory per video, not a complete mixed-pack quote.
   Surface the returned `billingUrl` on credit shortfall; do not buy or retry.
7. **Produce, inspect, continue.** Pass the exact brief, music window, occasion,
   aesthetic, voice and constraints into production. Produce a representative
   asset early and continue the approved batch without another mandatory approval
   stop, unless the customer requested a preview checkpoint. Use one coherent
   visual family, purposeful variations and captions tied to the actual occasion.
   Inspect the real outputs using `references/analyze-gate.md`; verify audio,
   framing, text and brief fit. A prompt, render request or generated-but-unchecked
   file is not a usable finished asset.
8. **Deliver and preserve progress.** Read the job and its export/manifest.
   Present previews, usable file links, captions, components/variants and honest
   gaps. Retain successful work on failure and retry only failed stages within
   budget; reconcile an uncertain submission before any duplicate paid work.
   Save job state immediately. After value is delivered, offer to save confirmed
   reusable artist preferences; do not overwrite branding with a one-off concept.

*Boundary:* legitimate creative volume only — no fake-account farms or mass-posting;
decline the farm, deliver the pack.

## Guardrails

- **One request, one continuing job.** Connection is not creative context.
- **Budget applies across the batch and retries.** No silent fan-out or automatic purchase.
- **Correct audio and inspected media before “done”.** Report partial packs accurately.
- **Stop at the assets.** No posting, scheduling or permanent public knowledge-base writes.
- If the customer asked only to **plan a release**, use the planning workflow and
  do not silently generate media. For both, carry the same brief into production.

## References

Use `fixtures/first-use-scenarios.json` when checking first-use behavior in a host.

- `references/release-pack-brief.md` · `templates/pack-brief.json` ·
  `references/workspace-context.md` · `references/account-resolver.md` ·
  `references/research-context.md` · `references/content-api.md` ·
  `references/song-sourcing.md` · `references/analyze-gate.md`
