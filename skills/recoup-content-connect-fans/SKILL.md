---
name: recoup-content-connect-fans
description: Add Recoup's paid Spotify fan connection to an artist site, including customer account setup, site attribution, activation, the public connection button and retrieving connected fans. Use for "add login with Spotify", "connect fans to my Recoup account", or "collect Spotify fans on this release site". Works with externally built sites as well as Recoup Sites.
---

# Connect a site's fans to the artist

Use the customer's Recoup account to configure a hosted Spotify connection journey. The site contains a public link; the agent keeps the account credential private. Paths below are relative to this skill directory.

Read `references/api.md` for exact calls, responses and release dependencies. Check endpoint availability before promising this integration: this skill requires the corresponding fan-connection API, database migration, billing policy and Spotify callback to be deployed. A 404 or 503 is a setup problem, not a reason to invent an endpoint or simulate success.

## 1. Connect the customer

Reuse a customer-provided Recoup API credential from the host's secure environment. Verify it with `GET /api/accounts/id`. Never print credentials or put them into website code, URLs, generated screenshots or logs.

If no credential exists, use the customer's real email with `POST /api/agents/signup`, ask for the emailed code, then submit `POST /api/agents/verify`. Use the returned `api_key` in the host's secret store or session environment. Ask before writing home-directory files or modifying shell configuration. Do not create a disposable identity for the artist. An empty roster can be a legitimate new account; it is not proof of invalid credentials.

## 2. Establish ownership and attribution

Resolve the intended artist from the authenticated roster. Use its Recoup artist account ID, not a Spotify ID or an artist row ID. If the artist does not exist, complete the platform's supported artist onboarding first. Resolve the customer workspace before creating a site; ask only if multiple choices remain ambiguous.

Reuse the existing Recoup site ID when provided. For an externally hosted site, register a Recoup site record with its artist and release URL. This record provides attribution without requiring Recoup to host or generate the website. Do not duplicate a site on every retry. Never accept an owner ID from public browser input.

## 3. Activate the paid feature

Read the site's current fan connection settings. Configure the final HTTPS return URL, the customer's clear marketing acceptance text, `enabled: true` and the current revision (0 when absent). Name the artist and the communication purpose in the text. The hosted journey presents it with one agreement button; Spotify presents its own permissions screen next. Do not add separate checkboxes to work around the configured journey.

If activation returns 402, explain that the owning workspace needs an eligible paid plan. Offer only the actual available checkout or upgrade path whose eligibility is confirmed by Recoup; do not invent pricing or charge without authorization. After checkout, retry activation. A 503 requires provider or billing configuration by Recoup and is not fixed by asking the customer to pay again.

## 4. Add the returned public link

Use the returned `connectUrl` as a normal anchor or full-page navigation with a clear label such as “Connect with Spotify”. Keep the visitor's existing progress so they can return to the experience. Place connection at a useful moment without making the entire experience incomprehensible behind login.

Do not expose the artist's API key, build a second Spotify client or ask the artist to supply a Spotify developer secret. Recoup owns the provider setup. The generated site needs only the public link.

The return query `recoup_spotify=connected|cancelled|failed` controls feedback only. It is not authentication, cannot identify a fan and must not authorize rewards or private content. On cancellation let the fan continue; on failure provide the same connection link for a fresh attempt. Do not automatically claim a fan has saved/followed a song, joined a mailing list delivery system or shared listening history.

## 5. Verify attribution and hand over

Have an authorized fan complete the real Spotify journey. Read the site's fans through the authenticated API and verify the new profile and separate connection, Spotify scope and marketing acceptance records. Never download the full fan list into a public repository or include personal details in deployment artifacts.

Report the site's owner, artist, configured return URL and activation state. Distinguish code implemented, paid activation enabled and live fan connection verified. If the deployment dependencies are missing, preserve the completed integration and report the exact remaining dependency.

This version captures Spotify identity and available email. It does not retain Spotify tokens, synchronize listening history, send marketing or create authenticated fan sessions. Playback is a separate capability.
