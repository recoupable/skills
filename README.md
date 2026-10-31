# Recoup

A record label inside Claude for artists, managers, and labels. Research artists,
organize catalogs, plan releases, and create release assets. Start with a song,
an artist, or an entire catalog, and put your agents to work.

## Connect and use

Install the plugin, connect the Recoup MCP server, and sign in to your Recoup
account through OAuth. Ask Claude to open Recoup workflows, research an artist,
or find songs in a catalog you can access. Available customer skills are listed below.
Some tools require Recoup credits or additional account entitlements. Review
proposed publishing, sending, and other external actions before authorizing them.

Documentation: https://docs.recoupable.dev
Support: agent@recoupable.dev
Privacy: https://recoupable.dev/privacy

## Execution and authentication

The declared MCP server uses remote HTTPS and host-managed OAuth. This package
does not register installation commands, lifecycle hooks, or a local MCP server.
That does not mean every workflow is remote-only: skills include readable Python,
JavaScript, and shell helpers that Claude may run for a user-requested task in a
host that supports execution. Other workflows can generate site or workspace code.
Inspect the skill and its scripts before granting execution permission.

Prefer connected MCP tools. Optional REST examples and helpers use separately
configured Recoup credentials, not tokens extracted from the host's OAuth session.
Catalog research and email helpers can call the Recoup API directly. Do not read
unrelated credentials or send Recoup credentials to another service. If a required
tool, credential, or execution capability is unavailable, report that limitation.
The bundled helper inventory below is generated from this exact release.

## Data handling and optional services

The declared connector is Recoup at api.recoupable.dev. Authorized workflows can
read and save artist, contact, catalog, release, and account information. Saved
Recoup content can remain longer than 30 days, until deletion or an applicable
retention requirement ends; disconnecting Claude does not delete the account.
See the privacy policy for retention, deletion, processors, and public assets.

Some skills also describe optional tools outside the declared Recoup connector.
ElevenLabs Scribe receives selected audio for transcription. Creative and site
workflows can use separately connected Higgsfield tools or a provider selected
by the user, such as fal.ai, receiving the prompts and reference assets needed
for that step. A user-selected hosting service can receive site files when
publishing is requested. These integrations require their own access and user
authorization; installing this plugin does not grant it. Review the destination
and inputs before sending data. External services apply their own privacy and
retention policies. The plugin is not specifically intended for users under 18.

## Included skills

- recoup-catalog-audit-catalog
- recoup-catalog-estimate-value
- recoup-catalog-explain-contract
- recoup-catalog-import-catalog
- recoup-catalog-organize-publishing
- recoup-catalog-reconcile-royalties
- recoup-catalog-register-catalog
- recoup-catalog-resolve-claims
- recoup-catalog-review-deal
- recoup-content-asset-pack
- recoup-content-build-sites
- recoup-content-connect-fans
- recoup-content-make-graphics
- recoup-content-make-video
- recoup-content-reactive-post
- recoup-content-write-caption
- recoup-minimax-music-3
- recoup-music-video
- recoup-nft-valuation
- recoup-platform-api-access
- recoup-platform-build-os
- recoup-platform-capture-lesson
- recoup-platform-connect-account
- recoup-platform-email-helper
- recoup-platform-track-onboarding
- recoup-release-add-release
- recoup-release-check-metadata
- recoup-release-manage-delivery
- recoup-release-plan-rollout
- recoup-release-track-drop
- recoup-research-artist-overview
- recoup-research-find-contacts
- recoup-research-find-talent
- recoup-research-playlist-targets
- recoup-research-the-web
- recoup-research-weekly-brief
- recoup-roster-add-artist
- recoup-roster-list-artists
- recoup-roster-manage-artist
- recoup-roster-onboard
- recoup-song
- recoup-song-analyze-audio
- recoup-song-check-credits
- recoup-song-find-hook
- recoup-song-placement-pitch
- ui-design-vocabulary

## Bundled helpers

- skills/recoup-catalog-audit-catalog/scripts/build-catalog-report.py
- skills/recoup-catalog-audit-catalog/scripts/catalog-case.py
- skills/recoup-catalog-estimate-value/scripts/build_report.py
- skills/recoup-catalog-estimate-value/scripts/estimate.py
- skills/recoup-catalog-estimate-value/scripts/fetch_album_tracks.py
- skills/recoup-catalog-estimate-value/scripts/scenario.mjs
- skills/recoup-catalog-estimate-value/scripts/scenario.py
- skills/recoup-catalog-estimate-value/tests/scenario-browser.test.mjs
- skills/recoup-catalog-estimate-value/tests/test_estimate.py
- skills/recoup-catalog-estimate-value/tests/test_scenario.py
- skills/recoup-catalog-explain-contract/scripts/build-catalog-report.py
- skills/recoup-catalog-explain-contract/scripts/catalog-case.py
- skills/recoup-catalog-import-catalog/scripts/build-catalog-report.py
- skills/recoup-catalog-import-catalog/scripts/catalog-case.py
- skills/recoup-catalog-import-catalog/scripts/import_catalog.py
- skills/recoup-catalog-import-catalog/tests/test_intake.py
- skills/recoup-catalog-import-catalog/tests/test_scoped_identity.py
- skills/recoup-catalog-organize-publishing/scripts/build-catalog-report.py
- skills/recoup-catalog-organize-publishing/scripts/catalog-case.py
- skills/recoup-catalog-reconcile-royalties/scripts/_finance.py
- skills/recoup-catalog-reconcile-royalties/scripts/_royalty_archive.py
- skills/recoup-catalog-reconcile-royalties/scripts/build-catalog-report.py
- skills/recoup-catalog-reconcile-royalties/scripts/calculate-entitlements.py
- skills/recoup-catalog-reconcile-royalties/scripts/catalog-case.py
- skills/recoup-catalog-reconcile-royalties/scripts/normalize-royalty-statement.py
- skills/recoup-catalog-reconcile-royalties/scripts/reconcile-remittances.py
- skills/recoup-catalog-reconcile-royalties/scripts/validate-normalized-ledger.py
- skills/recoup-catalog-register-catalog/scripts/build-catalog-report.py
- skills/recoup-catalog-register-catalog/scripts/catalog-case.py
- skills/recoup-catalog-register-catalog/scripts/mlc-public-fields.py
- skills/recoup-catalog-register-catalog/scripts/prepare-provider-packet.py
- skills/recoup-catalog-resolve-claims/scripts/build-catalog-report.py
- skills/recoup-catalog-resolve-claims/scripts/catalog-case.py
- skills/recoup-catalog-resolve-claims/scripts/mlc-public-fields.py
- skills/recoup-catalog-resolve-claims/scripts/prepare-provider-packet.py
- skills/recoup-catalog-review-deal/scripts/_finance.py
- skills/recoup-catalog-review-deal/scripts/_helpers.py
- skills/recoup-catalog-review-deal/scripts/_royalty_archive.py
- skills/recoup-catalog-review-deal/scripts/auto-column-map.py
- skills/recoup-catalog-review-deal/scripts/build-catalog-report.py
- skills/recoup-catalog-review-deal/scripts/build-deal-readiness.py
- skills/recoup-catalog-review-deal/scripts/build-file-manifest.py
- skills/recoup-catalog-review-deal/scripts/build-manual-review-queue.py
- skills/recoup-catalog-review-deal/scripts/calculate-concentration.py
- skills/recoup-catalog-review-deal/scripts/calculate-entitlements.py
- skills/recoup-catalog-review-deal/scripts/calculate-nps-nls-bridge.py
- skills/recoup-catalog-review-deal/scripts/catalog-case.py
- skills/recoup-catalog-review-deal/scripts/dataroom-hygiene-scan.py
- skills/recoup-catalog-review-deal/scripts/extract-pdf-statement.py
- skills/recoup-catalog-review-deal/scripts/normalize-royalty-statement.py
- skills/recoup-catalog-review-deal/scripts/reconcile-remittances.py
- skills/recoup-catalog-review-deal/scripts/run-deal-checks.py
- skills/recoup-catalog-review-deal/scripts/validate-dashboard.py
- skills/recoup-catalog-review-deal/scripts/validate-deal-workspace.py
- skills/recoup-catalog-review-deal/scripts/validate-evidence-ledger.py
- skills/recoup-catalog-review-deal/scripts/validate-findings-evidence.py
- skills/recoup-catalog-review-deal/scripts/validate-normalized-ledger.py
- skills/recoup-catalog-review-deal/scripts/validate-workspace-consistency.py
- skills/recoup-catalog-review-deal/tests/benchmark_archives.py
- skills/recoup-catalog-review-deal/tests/benchmark_finance.py
- skills/recoup-catalog-review-deal/tests/test_concentration_outputs.py
- skills/recoup-catalog-review-deal/tests/test_finance.py
- skills/recoup-catalog-review-deal/tests/test_normalizer_controls.py
- skills/recoup-catalog-review-deal/tests/test_readiness_dispositions.py
- skills/recoup-catalog-review-deal/tests/test_royalty_archives.py
- skills/recoup-content-build-sites/scripts/find_references.py
- skills/recoup-platform-build-os/evals/validate.py
- skills/recoup-platform-email-helper/scripts/send-email.mjs
- skills/recoup-release-check-metadata/scripts/build-catalog-report.py
- skills/recoup-release-check-metadata/scripts/catalog-case.py
- skills/recoup-release-manage-delivery/scripts/build-catalog-report.py
- skills/recoup-release-manage-delivery/scripts/catalog-case.py
- skills/recoup-release-plan-rollout/scripts/build_campaign_timeline.py
- skills/recoup-release-plan-rollout/scripts/validate_release.py
- skills/recoup-roster-add-artist/scripts/onboarding_examples.sh
- skills/recoup-song-analyze-audio/scripts/test_upload_chat_audio.py
- skills/recoup-song-analyze-audio/scripts/upload_chat_audio.py
- skills/recoup-song-check-credits/scripts/build-catalog-report.py
- skills/recoup-song-check-credits/scripts/catalog-case.py
- skills/ui-design-vocabulary/assets/atlas-data.js
- skills/ui-design-vocabulary/assets/atlas.js
- skills/ui-design-vocabulary/scripts/validate_atlas.py

## Release provenance

Source commit: fc7695cbc5188e7661bf0d3a7ebf314e17b672a0
Version: 2026.1031.85
